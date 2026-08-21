# SwiftUI Background Assets and model/media delivery review recipes

These are compile-oriented Swift sketches for a named app target. They are not claimed to compile in this documentation-only workspace and they do not prove asset-pack publication, system scheduling, extension lifetime, physical-device model/GPU/media behavior, accessibility, privacy, or release readiness.

Read the [delivery review](../42-framework-deep-dives/100-swiftui-background-assets-model-media-delivery-review.md), [design guide](../21-design-deep-dives/128-swiftui-background-assets-model-media-delivery-review-design.md), [capability route](../50-capability-recipes/131-swiftui-background-assets-model-media-delivery-review-route.md), and [proof matrix](../60-verification/125-swiftui-background-assets-model-media-delivery-review-proof-matrix.md) first. These sketches intentionally keep delivery, validation, local AI, user review, and domain mutation separate.

## Recipe 1: Model the resource readiness state

Keep SwiftUI state app-owned and richer than a downloader callback.

~~~swift
import Foundation

enum ResourceReadiness: Equatable, Sendable {
    case unavailable(reason: String)
    case availableButNotInstalled(sizeBytes: Int64?)
    case downloading(progress: Double?)
    case validating(version: String)
    case preparing(version: String)
    case ready(version: String, summary: String)
    case stale(activeVersion: String, candidateVersion: String)
    case incompatible(reason: String)
    case failed(retryable: Bool, reason: String)
    case evicted
}

struct ResourceRecord: Codable, Sendable {
    let resourceID: String
    let version: String
    let fileDigest: String
    let validationRevision: String
    let installedAt: Date
}
~~~

Do not store a raw framework status as the only source of truth. Include the resource ID and operation revision so an old status update cannot overwrite a newer candidate.

## Recipe 2: Ensure a managed pack is local

AssetPackManager is an actor. Keep the manager behind an async coordinator and resolve only a known pack.

~~~swift
import BackgroundAssets
import Foundation

actor ManagedPackCoordinator {
    private let manager = AssetPackManager.shared

    func ensureModelPack(
        packID: String,
        requireLatest: Bool
    ) async throws -> AssetPack {
        let manifest = try await manager.manifest
        guard let pack = manifest.assetPacks.first(where: { $0.id == packID }) else {
            throw ResourceError.missingPack(packID)
        }

        if requireLatest {
            try await manager.ensureLocalAvailability(
                of: pack,
                requireLatestVersion: true
            )
        } else {
            try await manager.ensureLocalAvailability(
                of: pack,
                requireLatestVersion: false
            )
        }
        return pack
    }
}

enum ResourceError: Error {
    case missingPack(String)
    case invalidRelativePath(String)
    case digestMismatch
    case incompatible
}
~~~

The exact manifest collection and availability overloads must be checked against the target SDK. A successful availability call still requires file/schema/model/media validation.

## Recipe 3: Observe managed status without publishing stale state

Use an operation revision or resource version when mapping manager updates.

~~~swift
import BackgroundAssets
import Foundation

actor ManagedStatusCoordinator {
    private let manager = AssetPackManager.shared
    private var latestOperation: [String: Int] = [:]

    func observe(operation: Int, resourceID: String) async {
        latestOperation[resourceID] = operation

        for await update in manager.statusUpdates {
            guard latestOperation[resourceID] == operation else {
                return
            }

            // Map the documented update/status values into ResourceReadiness.
            // Do not publish ready until a consumer validator succeeds.
            _ = update
        }
    }
}
~~~

Cancel the observation when the feature disappears or a newer resource operation supersedes it. The exact status-update payload and filtering APIs should be verified in the selected SDK.

## Recipe 4: Read a bounded pack file

Choose a consumer-specific accessor and reject arbitrary paths.

~~~swift
import BackgroundAssets
import Foundation

actor ManagedResourceReader {
    private let manager = AssetPackManager.shared
    private let allowedPaths: Set<String> = [
        "models/feature.mlmodel",
        "models/manifest.json",
        "media/preview.m4v"
    ]

    func url(for relativePath: String) throws -> URL {
        guard allowedPaths.contains(relativePath) else {
            throw ResourceError.invalidRelativePath(relativePath)
        }
        return try manager.url(for: relativePath)
    }

    func metadata(for relativePath: String) throws -> Data {
        guard allowedPaths.contains(relativePath) else {
            throw ResourceError.invalidRelativePath(relativePath)
        }
        return try manager.contents(at: relativePath)
    }
}
~~~

Use the target SDK’s exact overloads for URL, Data, or descriptor access. If a file descriptor is returned, close it after the consumer has finished. Keep pack IDs and paths app-owned.

## Recipe 5: Filter managed downloads conservatively

Apple-hosted packs use StoreDownloaderExtension; self-hosted managed packs use ManagedDownloaderExtension. The managed protocols provide default behavior. Customize only the documented hook.

~~~swift
import BackgroundAssets

final class SelfHostedDownloader: ManagedDownloaderExtension {
    func shouldDownload(_ assetPack: AssetPack) -> Bool {
        let allowedIDs: Set<String> = [
            "feature-core",
            "feature-model-v4"
        ]
        return allowedIDs.contains(assetPack.id)
    }
}
~~~

The generated Xcode extension template and the current SDK determine the principal class and exact target wiring. Do not implement inherited downloader requirements that the protocol supplies by default. For Apple hosting, use the StoreDownloaderExtension route and verify StoreKit linkage.

## Recipe 6: Compile and persist a downloaded Core ML model

Keep a downloaded source model, temporary compilation result, and active compiled model in separate locations.

~~~swift
import CoreML
import Foundation

actor ModelInstaller {
    struct InstalledModel: Sendable {
        let version: String
        let compiledURL: URL
    }

    func install(
        sourceURL: URL,
        version: String,
        modelsDirectory: URL
    ) async throws -> InstalledModel {
        let compiledTemporaryURL = try await MLModel.compileModel(at: sourceURL)

        let versionDirectory = modelsDirectory
            .appendingPathComponent(version, isDirectory: true)
        try FileManager.default.createDirectory(
            at: versionDirectory,
            withIntermediateDirectories: true
        )

        let compiledURL = versionDirectory
            .appendingPathComponent("Model.mlmodelc", isDirectory: true)
        try replaceDirectory(
            at: compiledURL,
            with: compiledTemporaryURL
        )
        return InstalledModel(version: version, compiledURL: compiledURL)
    }

    private func replaceDirectory(
        at destination: URL,
        with source: URL
    ) throws {
        if FileManager.default.fileExists(atPath: destination.path) {
            try FileManager.default.removeItem(at: destination)
        }
        try FileManager.default.moveItem(at: source, to: destination)
    }
}
~~~

This is a route sketch, not an atomic storage implementation. A production installer should use a temporary app-owned directory, digest/schema checks, crash-safe promotion, disk-space checks, cancellation cleanup, and a record that identifies the last validated active version.

## Recipe 7: Load and inspect the compiled model

Do not publish model readiness until the model contract has passed.

~~~swift
import CoreML
import Foundation

actor ModelValidator {
    func load(
        compiledURL: URL,
        configuration: MLModelConfiguration
    ) async throws -> MLModel {
        let model = try await MLModel.load(
            contentsOf: compiledURL,
            configuration: configuration
        )

        let description = model.modelDescription
        guard description.inputDescriptionsByName["image"] != nil else {
            throw ResourceError.incompatible
        }

        // Inspect output descriptions, feature types, shapes, revision,
        // and any app-owned schema/version metadata here.
        _ = model.configuration.computeUnits
        return model
    }
}
~~~

The feature names and types are examples only. Use the actual model contract. Core ML requires serialized use of one MLModel instance on one thread or dispatch queue, or separate instances per queue. A load result does not prove quality, latency, or thermal suitability.

## Recipe 8: Record a device and compute-unit gate

Use availability as one input to a readiness decision, not as a quality guarantee.

~~~swift
import CoreML

struct ModelCapabilitySummary: Sendable {
    let computeUnits: MLComputeUnits
    let description: String
}

func modelSummary(
    model: MLModel,
    configuration: MLModelConfiguration
) -> ModelCapabilitySummary {
    let devices = model.availableComputeDevices
    let deviceNames = devices.map { String(describing: $0) }.joined(separator: ", ")
    return ModelCapabilitySummary(
        computeUnits: configuration.computeUnits,
        description: deviceNames
    )
}
~~~

The exact compute-device collection and deployment availability must be checked against the selected SDK. Record physical-device latency, memory, energy, thermal, and representative quality separately.

## Recipe 9: Validate a versioned asset manifest

Keep the file contract separate from the downloader.

~~~swift
import Foundation

struct ResourceManifest: Decodable, Sendable {
    let resourceID: String
    let version: String
    let validationRevision: String
    let files: [ResourceFile]
}

struct ResourceFile: Decodable, Sendable {
    let relativePath: String
    let byteCount: Int64
    let digest: String
}

func validateManifest(
    _ manifest: ResourceManifest,
    expectedID: String,
    expectedValidationRevision: String
) throws {
    guard manifest.resourceID == expectedID else {
        throw ResourceError.incompatible
    }
    guard manifest.validationRevision == expectedValidationRevision else {
        throw ResourceError.incompatible
    }
    guard manifest.files.allSatisfy({ $0.relativePath.hasPrefix("models/") }) else {
        throw ResourceError.invalidRelativePath("manifest")
    }
}
~~~

Production validation should also check canonical paths, file existence, byte counts, digest, supported model/media/shader format, app-build compatibility, and an allowlisted file set. Never use a remote manifest as permission to execute arbitrary code.

## Recipe 10: Publish a Liquid Glass resource status view

The view should consume a readiness state and render semantic controls. It should not own the Background Assets actor.

~~~swift
import SwiftUI

struct ResourceStatusView: View {
    let state: ResourceReadiness
    let download: () -> Void
    let retry: () -> Void
    let useBasicMode: () -> Void
    let remove: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label("Enhanced analysis", systemImage: "sparkles")
                .font(.headline)

            statusLabel
                .accessibilityElement(children: .combine)

            actions
        }
        .padding()
        .glassEffect()
    }

    @ViewBuilder
    private var statusLabel: some View {
        switch state {
        case .downloading(let progress):
            if let progress {
                ProgressView(value: progress)
            } else {
                ProgressView()
            }
            Text("Downloading the feature resource")
        case .preparing:
            ProgressView()
            Text("Preparing on-device intelligence")
        case .ready(let version, _):
            Label("Ready on this iPhone, version \(version)", systemImage: "checkmark.circle")
        case .failed(_, let reason):
            Label(reason, systemImage: "exclamationmark.triangle")
        default:
            Text("The enhanced feature is not ready")
        }
    }

    @ViewBuilder
    private var actions: some View {
        switch state {
        case .availableButNotInstalled:
            Button("Download", action: download)
            Button("Use Basic Mode", action: useBasicMode)
        case .failed:
            Button("Retry", action: retry)
            Button("Use Basic Mode", action: useBasicMode)
        case .ready:
            Button("Remove Download", action: remove)
        default:
            Button("Use Basic Mode", action: useBasicMode)
        }
    }
}
~~~

The exact Liquid Glass modifier and availability depend on the target SDK. Keep the status text accessible when the glass effect is reduced or unavailable. Do not use the view as proof that the system download or model validation succeeded.

## Recipe 11: Keep fallback and model review explicit

Make a proposal value distinct from the persisted domain record.

~~~swift
struct LocalModelProposal: Sendable {
    let sourceID: String
    let modelVersion: String
    let suggestedValue: String
    let evidenceSummary: String
}

@MainActor
final class FeatureReviewModel: ObservableObject {
    @Published private(set) var readiness: ResourceReadiness = .unavailable(
        reason: "The enhanced resource is not installed"
    )
    @Published private(set) var proposal: LocalModelProposal?

    func runLocalProposal(input: Data) async {
        guard case .ready(let version, _) = readiness else {
            readiness = .unavailable(
                reason: "Use Basic Mode until the local model is ready"
            )
            return
        }

        // Invoke a bounded, validated model adapter here.
        // Store a proposal, not a committed domain mutation.
        proposal = LocalModelProposal(
            sourceID: "user-selected-input",
            modelVersion: version,
            suggestedValue: "candidate",
            evidenceSummary: "Generated locally; review before applying"
        )
        _ = input
    }

    func apply(_ proposal: LocalModelProposal) {
        // Re-check the current revision and typed constraints before commit.
        _ = proposal
    }
}
~~~

The fallback remains available when delivery fails, the model is incompatible, or the user declines to download. Do not silently switch to a remote model or claim offline behavior that was not physically tested.

## Recipe 12: Create a release evidence record

Use a redacted, reproducible record that joins the resource and app artifacts.

~~~swift
struct ResourceProofRecord: Codable, Sendable {
    let appBuild: String
    let sdk: String
    let deploymentTarget: String
    let deviceOS: String
    let deviceModel: String
    let appBundleID: String
    let extensionBundleID: String?
    let resourceID: String
    let resourceVersion: String
    let validationRevision: String
    let localRunPassed: Bool
    let physicalRunPassed: Bool
    let fallbackVerified: Bool
    let accessibilityVerified: Bool
    let releaseRecordVerified: Bool
}
~~~

Do not include signed URLs, credentials, raw user content, prompts, or private device identifiers. A true field in a proof record should link to the actual captured artifact or test result in the team’s approved evidence store.

## Sources

- [Background Assets](https://developer.apple.com/documentation/backgroundassets)
- [Creating managed asset packs](https://developer.apple.com/documentation/backgroundassets/creating-managed-asset-packs)
- [Downloading Apple-hosted asset packs](https://developer.apple.com/documentation/backgroundassets/downloading-apple-hosted-asset-packs)
- [Testing asset packs locally](https://developer.apple.com/documentation/backgroundassets/testing-asset-packs-locally)
- [Configuring an unmanaged Background Assets project](https://developer.apple.com/documentation/backgroundassets/configuring-an-unmanaged-background-assets-project)
- [Downloading essential assets in the background](https://developer.apple.com/documentation/backgroundassets/downloading-essential-assets-in-the-background)
- [AssetPackManager](https://developer.apple.com/documentation/backgroundassets/assetpackmanager)
- [ManagedDownloaderExtension](https://developer.apple.com/documentation/backgroundassets/manageddownloaderextension)
- [StoreDownloaderExtension](https://developer.apple.com/documentation/storekit/storedownloaderextension)
- [BADownloadManager](https://developer.apple.com/documentation/backgroundassets/badownloadmanager)
- [BAURLDownload](https://developer.apple.com/documentation/backgroundassets/baurldownload)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [MLModel](https://developer.apple.com/documentation/coreml/mlmodel)
- [MLModelAsset](https://developer.apple.com/documentation/coreml/mlmodelasset)
- [Compiling a model on the user’s device](https://developer.apple.com/documentation/coreml/downloading-and-compiling-a-model-on-the-user-s-device)
- [Reducing the size of your Core ML app](https://developer.apple.com/documentation/coreml/reducing-the-size-of-your-core-ml-app)
- [Metal](https://developer.apple.com/documentation/metal)
- [Metal capabilities](https://developer.apple.com/metal/capabilities/)
- [Core Image](https://developer.apple.com/documentation/coreimage)
- [AVFoundation](https://developer.apple.com/documentation/avfoundation)
- [VideoToolbox](https://developer.apple.com/documentation/videotoolbox)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
