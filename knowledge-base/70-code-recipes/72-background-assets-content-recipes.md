# Background Assets content and model-pack code recipes

These are target-oriented Swift sketches for managed and unmanaged Background Assets. They are not claimed to compile in this documentation-only workspace and they do not prove App Store Connect asset-pack distribution, system scheduling, extension behavior, local storage, model quality, GPU compatibility, or release readiness.

Read the [Background Assets capability route](../50-capability-recipes/60-background-assets-content-route.md), [framework deep dive](../42-framework-deep-dives/37-background-assets-managed-content-and-model-packs.md), [content and model-pack design guide](../21-design-deep-dives/57-background-assets-content-and-model-pack-design.md), and [proof matrix](../60-verification/54-background-assets-content-proof-matrix.md) first.

## Recipe 1: Inspect a managed asset-pack manifest

AssetPackManager is an actor. Keep access in an async boundary and publish a typed readiness model to SwiftUI.

~~~swift
import BackgroundAssets
import Foundation

struct AssetPackSummary: Sendable, Identifiable {
    let id: String
    let displayName: String
}

actor ManagedAssetCatalog {
    private let manager = AssetPackManager.shared

    func availablePacks() async throws -> [AssetPackSummary] {
        let manifest = try await manager.manifest
        return manifest.assetPacks.map { pack in
            AssetPackSummary(
                id: pack.id,
                displayName: pack.id
            )
        }
    }
}
~~~

The exact AssetPack properties available for the target SDK may include more metadata. Keep a stable app-owned pack identifier and do not let model output choose an arbitrary pack.

## Recipe 2: Ensure a pack is local and read a file

Separate local availability from feature validation.

~~~swift
import BackgroundAssets
import Foundation

actor ManagedAssetLoader {
    private let manager = AssetPackManager.shared

    func ensure(
        pack: AssetPack,
        relativePath: FilePath
    ) async throws -> URL {
        try await manager.ensureLocalAvailability(
            of: pack,
            requireLatestVersion: false
        )

        let url = try manager.url(for: relativePath)
        return url
    }
}
~~~

After this returns, validate the file’s schema, resource identity, version, and device/framework compatibility. Do not mark a model, shader library, or level pack ready because a URL exists.

## Recipe 3: Track managed download status

Use the manager’s asynchronous status updates to drive a state machine.

~~~swift
import BackgroundAssets

enum ResourceState: Equatable, Sendable {
    case declared
    case downloading
    case local
    case ready
    case failed
}

actor ManagedStatusObserver {
    private let manager = AssetPackManager.shared

    func observe() async {
        for await update in manager.statusUpdates {
            // Map the documented DownloadStatusUpdate values into
            // app-owned state. Publish only validated readiness.
            _ = update
        }
    }
}
~~~

Keep the observer cancellable. If a new pack supersedes the active one, the old observer must not overwrite the new feature state.

## Recipe 4: Check for pack updates

Run update checks at deliberate product boundaries, such as app foreground or a resource-management screen.

~~~swift
import BackgroundAssets

actor AssetUpdateCoordinator {
    private let manager = AssetPackManager.shared

    func check() async throws {
        let result = try await manager.checkForUpdates()
        for id in result.updatingIDs {
            // Keep the current validated version active while updating
            // unless the feature requires the latest version.
            _ = id
        }
        for id in result.removedIDs {
            // Move the feature to fallback and remove only replaceable
            // resources. Keep user-owned records.
            _ = id
        }
    }
}
~~~

An update result is not a feature-quality result. Run the pack validator after an update.

## Recipe 5: Configure managed asset-pack choices

The exact Info.plist key placement and extension template depend on the selected SDK. Keep the configuration record explicit.

~~~xml
<key>BAHasManagedAssetPacks</key>
<true/>
<key>BAUsesAppleHosting</key>
<true/>
<key>BAAppGroupID</key>
<string>group.example.resources</string>
~~~

For Apple hosting, use the StoreKit StoreDownloaderExtension route documented for the selected SDK. For self-hosted managed packs, use ManagedDownloaderExtension. Do not set managed keys and then add an unmanaged-only downloader protocol.

## Recipe 6: Schedule an unmanaged URL download

Use only an allowlisted, product-owned HTTPS host. The identifier is app-owned resource identity.

~~~swift
import BackgroundAssets
import Foundation

func scheduleResourceDownload(
    url: URL,
    resourceID: String,
    appGroupID: String
) throws {
    var request = URLRequest(url: url)
    request.httpMethod = "GET"

    let download = BAURLDownload(
        identifier: resourceID,
        request: request,
        applicationGroupIdentifier: appGroupID
    )

    try BADownloadManager.shared.scheduleDownload(download)
}
~~~

Before calling this, validate the URL’s scheme, host, path, resource ID, expected size, and feature catalog. Never pass a URL generated by a model or untrusted text.

## Recipe 7: Start a foreground unmanaged download

Foreground start can provide a deliberate user action, but the operation remains asynchronous and can fail.

~~~swift
import BackgroundAssets

func startNow(_ download: BADownload) throws {
    try BADownloadManager.shared.startForegroundDownload(download)
}

func cancel(_ download: BADownload) throws {
    try BADownloadManager.shared.cancel(download)
}
~~~

Show scheduled/running/finished/failed/canceled states. Do not close the feature screen or delete the old resource until the new file has validated.

## Recipe 8: Unmanaged downloader-extension seam

The exact extension template and protocol availability must be checked in the target SDK. This sketch shows the lifecycle boundaries.

~~~swift
import BackgroundAssets
import Foundation

final class ResourceDownloaderExtension: NSObject, BADownloaderExtension {
    func downloads(
        for request: BAContentRequest,
        manifestURL: URL,
        extensionInfo: BAAppExtensionInfo
    ) -> Set<BADownload> {
        // Parse the manifest, create only allowlisted downloads, and
        // return the set that the system should schedule.
        _ = request
        _ = manifestURL
        _ = extensionInfo
        return []
    }

    func backgroundDownload(
        _ download: BADownload,
        finishedWithFileURL fileURL: URL
    ) {
        // Validate file identity/schema/size before publishing it through
        // the App Group projection.
        _ = download
        _ = fileURL
    }

    func backgroundDownload(
        _ download: BADownload,
        failedWithError error: Error
    ) {
        // Persist retryable/terminal state without logging secrets.
        _ = download
        _ = error
    }

    func extensionWillTerminate() {
        // Save enough state for the next invocation to resume safely.
    }
}
~~~

Check the authentication-challenge method and async/concurrency annotations in the selected SDK. A code shape copied across SDK generations is not a compile proof.

## Recipe 9: Parse a self-hosted manifest

AssetPackManifest can parse a manifest from a URL or Data and produce downloads for applicable packs.

~~~swift
import BackgroundAssets
import Foundation

func parseManifest(
    data: Data,
    appGroupID: String
) throws -> AssetPackManifest {
    try AssetPackManifest(
        from: data,
        appGroupID: appGroupID
    )
}
~~~

Validate the manifest’s host/path/pack catalog and size policy before scheduling its downloads. Do not treat an arbitrary JSON file as an app manifest.

## Recipe 10: Publish a validated resource

Download completion should write a small app-group record only after validation succeeds.

~~~swift
struct ValidatedResource: Codable, Sendable {
    let resourceID: String
    let version: String
    let relativePath: String
    let byteCount: Int
    let schemaVersion: Int
    let validatedAt: Date
}

enum ResourceValidationError: Error {
    case wrongResource
    case wrongSize
    case unsupportedSchema
    case incompatibleDevice
}

func validate(
    resourceID: String,
    expectedID: String,
    byteCount: Int,
    expectedByteCount: Int,
    schemaVersion: Int,
    supportedSchemas: Set<Int>
) throws {
    guard resourceID == expectedID else {
        throw ResourceValidationError.wrongResource
    }
    guard byteCount == expectedByteCount else {
        throw ResourceValidationError.wrongSize
    }
    guard supportedSchemas.contains(schemaVersion) else {
        throw ResourceValidationError.unsupportedSchema
    }
}
~~~

Add cryptographic/content integrity checks appropriate to the asset pipeline. Keep a current validated version if the replacement fails.

## Recipe 11: Load a downloaded model through a separate gate

The asset route should hand a validated URL to the model framework, then run a second readiness check.

~~~swift
struct ModelResourceGate {
    let resourceID: String
    let version: String
    let url: URL
    let inputSchema: String
}

func prepareModel(
    _ resource: ModelResourceGate
) throws -> ModelResourceGate {
    // The selected Core ML or other model API performs the real load and
    // device/compute-unit checks. Keep the resource version in the result.
    guard FileManager.default.fileExists(atPath: resource.url.path) else {
        throw CocoaError(.fileNoSuchFile)
    }
    return resource
}
~~~

After loading, measure representative quality, latency, memory, and thermal behavior on physical devices. A downloaded model is not an approved model.

## Recipe 12: Model-versioned proposal

Record the model/asset version with any user-visible proposal.

~~~swift
struct ResourceBackedProposal: Sendable {
    let sourceID: String
    let resourceID: String
    let resourceVersion: String
    let text: String
    let confidence: Double?
}

func canApply(
    proposal: ResourceBackedProposal,
    currentResourceVersion: String
) -> Bool {
    proposal.resourceVersion == currentResourceVersion
}
~~~

If the active resource version changes, revalidate or invalidate the proposal. Do not silently apply a result produced by a resource that is no longer active.

## Recipe 13: Keep a lower-resource fallback

Make resource readiness one branch of a product capability.

~~~swift
enum RenderingMode: Equatable, Sendable {
    case enhanced(resourceVersion: String)
    case basic
    case unavailable(reason: String)
}

func renderingMode(
    resourceReady: Bool,
    version: String?,
    deviceSupported: Bool
) -> RenderingMode {
    guard deviceSupported else {
        return .basic
    }
    guard resourceReady, let version else {
        return .basic
    }
    return .enhanced(resourceVersion: version)
}
~~~

The basic path should preserve the user’s goal where possible. A glass download card should not be the only screen a person can use.

## Recipe 14: Gate newer localized-pack APIs

The current localized asset-pack documentation describes newer target availability. Keep the iOS 26 route explicit.

~~~swift
enum LanguageResourceRoute {
    case standardPack
    case localizedPacks
    case fallback(String)
}

func chooseLanguageRoute(
    systemSupportsLocalizedPacks: Bool,
    selectedTarget: String
) -> LanguageResourceRoute {
    guard systemSupportsLocalizedPacks else {
        return .standardPack
    }
    _ = selectedTarget
    return .localizedPacks
}
~~~

Do not use a runtime string or a source-level assumption as a substitute for the actual availability check and target SDK. Test the intended iOS 26 target separately from later SDKs.

## Recipe 15: Redacted resource diagnostics

Log resource lifecycle, not URLs, manifests, credentials, or user/device identifiers.

~~~swift
struct ResourceDiagnostic: Sendable {
    let resourceID: String
    let version: String?
    let phase: String
    let byteCount: Int?
    let result: String
}

func logResource(_ event: ResourceDiagnostic) {
    // Send only redacted lifecycle facts to Logger or the approved sink.
    _ = event
}
~~~

Never log signed download requests, authentication headers, private manifest URLs, or user-specific resource paths.

## Sources

- [Background Assets](https://developer.apple.com/documentation/backgroundassets)
- [Creating managed asset packs](https://developer.apple.com/documentation/backgroundassets/creating-managed-asset-packs)
- [Downloading Apple-hosted asset packs](https://developer.apple.com/documentation/backgroundassets/downloading-apple-hosted-asset-packs)
- [Testing asset packs locally](https://developer.apple.com/documentation/backgroundassets/testing-asset-packs-locally)
- [Configuring an unmanaged Background Assets project](https://developer.apple.com/documentation/backgroundassets/configuring-an-unmanaged-background-assets-project)
- [Downloading essential assets in the background](https://developer.apple.com/documentation/backgroundassets/downloading-essential-assets-in-the-background)
- [AssetPackManager](https://developer.apple.com/documentation/backgroundassets/assetpackmanager)
- [AssetPackManifest](https://developer.apple.com/documentation/backgroundassets/assetpackmanifest)
- [BADownloadManager](https://developer.apple.com/documentation/backgroundassets/badownloadmanager)
- [BADownload](https://developer.apple.com/documentation/backgroundassets/badownload)
- [BAURLDownload](https://developer.apple.com/documentation/backgroundassets/baurldownload)
- [BADownloaderExtension](https://developer.apple.com/documentation/backgroundassets/badownloaderextension)
- [BAUsesAppleHosting](https://developer.apple.com/documentation/bundleresources/information-property-list/bausesapplehosting)
- [BAHasManagedAssetPacks](https://developer.apple.com/documentation/bundleresources/information-property-list/bahasmanagedassetpacks)
- [BAAppGroupID](https://developer.apple.com/documentation/bundleresources/information-property-list/baappgroupid)
- [BAManifestURL](https://developer.apple.com/documentation/bundleresources/information-property-list/bamanifesturl)
- [Background Assets in the App Store Connect API](https://developer.apple.com/documentation/appstoreconnectapi/background-assets)
- [Reducing download and storage demands with localized asset packs](https://developer.apple.com/documentation/backgroundassets/reducing-download-and-storage-demands-with-localized-asset-packs)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
