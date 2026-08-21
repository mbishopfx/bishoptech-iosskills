# SwiftUI PhotosPicker, PhotoKit, Image I/O, Live Photo, and media-source/editing review recipes

These are compile-oriented Swift sketches for a named iOS target. They are not claimed to compile in this documentation-only workspace and they do not prove Photos authorization, iCloud delivery, source ownership, image/video fidelity, Live Photo playback, Photos-library mutation, metadata privacy, on-device model quality, accessibility, physical-device behavior, or release readiness.

Read the [source/editing review](../42-framework-deep-dives/102-swiftui-photospicker-photokit-imageio-live-photo-source-review.md), [design guide](../21-design-deep-dives/130-swiftui-photospicker-photokit-imageio-live-photo-source-review-design.md), [route](../50-capability-recipes/133-swiftui-photospicker-photokit-imageio-live-photo-source-review-route.md), and [proof matrix](../60-verification/127-swiftui-photospicker-photokit-imageio-live-photo-source-review-proof-matrix.md) first. Verify every API shape and availability against the target SDK.

## Recipe 1: Model the media source and readiness

Keep the source manifest richer than the picker callback.

~~~swift
import Foundation

struct MediaSourceManifest: Codable, Sendable, Equatable {
    let sourceKind: SourceKind
    let localIdentifier: String?
    let pickerIdentifier: String?
    let contentType: String?
    let resourceType: String?
    let representationRevision: String
    let byteCount: Int64?
    let pixelWidth: Int?
    let pixelHeight: Int?
    let capturedAt: Date

    enum SourceKind: String, Codable, Sendable {
        case photosPicker
        case photoKit
        case appFile
    }
}

enum MediaReadiness: Equatable, Sendable {
    case idle
    case selectedPlaceholder
    case downloading(progress: Double?)
    case inspecting
    case previewReady(MediaSourceManifest)
    case proposalReady(MediaProposal)
    case editing
    case exporting
    case committed
    case missingSource
    case failed(String)
}
~~~

Do not persist a PHAsset object or assume a picker item is a durable URL.

## Recipe 2: Use a narrow SwiftUI picker

Filter to the content the feature can actually process and cap multiple selection.

~~~swift
import PhotosUI
import SwiftUI

struct MediaPicker: View {
    @Binding var selection: [PhotosPickerItem]
    @Binding var readiness: MediaReadiness

    var body: some View {
        PhotosPicker(
            selection: $selection,
            maxSelectionCount: 12,
            matching: .any(of: [.images, .videos, .livePhotos]),
            preferredItemEncoding: .current
        ) {
            Label("Choose media", systemImage: "photo.on.rectangle")
        }
        .onChange(of: selection) {
            readiness = selection.isEmpty
                ? .idle
                : .selectedPlaceholder
        }
    }
}
~~~

Treat the selection change as the beginning of a load operation, not as proof of a ready preview. The exact PhotosPicker initializer and filter availability should be checked in the target SDK.

## Recipe 3: Load a custom Transferable with generation safety

For non-PNG image data, video, or file-backed processing, use a custom Transferable model or a PhotoKit resource route. Keep the selection generation so a slow result cannot replace a newer one.

~~~swift
import PhotosUI
import SwiftUI

@MainActor
final class ImportModel: ObservableObject {
    @Published var items: [PhotosPickerItem] = []
    @Published private(set) var states: [UUID: MediaReadiness] = [:]

    private var generation = UUID()

    func replaceSelection(_ newItems: [PhotosPickerItem]) {
        generation = UUID()
        let currentGeneration = generation
        items = newItems

        Task {
            await load(
                newItems,
                generation: currentGeneration
            )
        }
    }

    private func load(
        _ items: [PhotosPickerItem],
        generation: UUID
    ) async {
        await withTaskGroup(of: Void.self) { group in
            for item in items {
                group.addTask { [weak self] in
                    do {
                        let material = try await item.loadTransferable(
                            type: ImportedMedia.self
                        )
                        guard !Task.isCancelled else { return }
                        await self?.accept(
                            material,
                            from: item,
                            generation: generation
                        )
                    } catch is CancellationError {
                        return
                    } catch {
                        await self?.fail(
                            error,
                            generation: generation
                        )
                    }
                }
            }
        }
    }

    private func accept(
        _ material: ImportedMedia?,
        from item: PhotosPickerItem,
        generation: UUID
    ) {
        guard generation == self.generation else { return }
        guard let material else {
            return
        }
        // Inspect and persist the source manifest here.
    }

    private func fail(_ error: Error, generation: UUID) {
        guard generation == self.generation else { return }
        // Map the error to retryable, offline, or unsupported state.
    }
}
~~~

The exact Transferable type and actor isolation should be compiled in the named target. The invariant is generation-safe, cancellable, bounded loading.

## Recipe 4: Define a file-backed Transferable sketch

File-backed transfer avoids forcing a large original into a SwiftUI Image. Verify the current FileRepresentation and ReceivedTransferredFile signatures against the SDK.

~~~swift
import CoreTransferable
import UniformTypeIdentifiers

struct ImportedMedia: Transferable, Sendable {
    let fileURL: URL
    let contentType: UTType

    static var transferRepresentation: some TransferRepresentation {
        FileRepresentation(
            importedContentType: .item
        ) { received in
            ImportedMedia(
                fileURL: received.file,
                contentType: .item
            )
        }
    }
}
~~~

Move or copy the received file into an app-owned temporary location before its provider lifetime ends. Inspect the bytes and enforce a file-size budget before using the file as a model input.

## Recipe 5: Request PhotoKit authorization by access level

Use the access-level API and make limited access a first-class state.

~~~swift
import Photos

enum PhotoPermission: Sendable {
    case notDetermined
    case authorized
    case limited
    case denied
    case restricted
}

func requestReadAccess() async -> PhotoPermission {
    let status = await PHPhotoLibrary.requestAuthorization(for: .readWrite)
    switch status {
    case .authorized:
        return .authorized
    case .limited:
        return .limited
    case .denied:
        return .denied
    case .restricted:
        return .restricted
    case .notDetermined:
        return .notDetermined
    @unknown default:
        return .denied
    }
}
~~~

If a feature only creates assets, use the add-only route after confirming the target’s current API and privacy configuration. Do not request read/write access for a picker-only feature.

## Recipe 6: Resolve a current PHAsset

Resolve an identifier immediately before loading or mutating.

~~~swift
import Photos

func currentAsset(
    localIdentifier: String
) throws -> PHAsset {
    let result = PHAsset.fetchAssets(
        withLocalIdentifiers: [localIdentifier],
        options: nil
    )
    guard let asset = result.firstObject else {
        throw MediaError.sourceMissing
    }
    return asset
}

struct AssetSnapshot: Sendable {
    let localIdentifier: String
    let mediaType: String
    let contentType: String
    let width: Int
    let height: Int
    let hasAdjustments: Bool
    let modificationDate: Date?
}

func snapshot(_ asset: PHAsset) -> AssetSnapshot {
    AssetSnapshot(
        localIdentifier: asset.localIdentifier,
        mediaType: String(describing: asset.mediaType),
        contentType: asset.contentType.identifier,
        width: asset.pixelWidth,
        height: asset.pixelHeight,
        hasAdjustments: asset.hasAdjustments,
        modificationDate: asset.modificationDate
    )
}
~~~

Treat the snapshot as evidence of what was resolved at one point in time. Re-resolve after a long-running load or before committing an edit.

## Recipe 7: Enumerate resources by explicit policy

Select resources by type and content type instead of assuming the first resource is the original.

~~~swift
import Photos

func resource(
    for asset: PHAsset,
    acceptedTypes: Set<PHAssetResourceType>
) throws -> PHAssetResource {
    let resources = PHAssetResource.assetResources(for: asset)
    guard let selected = resources.first(where: {
        acceptedTypes.contains($0.type)
    }) else {
        throw MediaError.unsupportedResource
    }
    return selected
}
~~~

For RAW, adjusted, and Live Photo assets, expand the policy and record the selected resource type and Uniform Type Identifier in the source manifest.

## Recipe 8: Stream a resource to a temporary file

PHAssetResourceManager can write an underlying resource to a file. The callback form and cancellation bridge must be verified against the selected SDK.

~~~swift
import Photos

final class ResourceLoader {
    private let manager = PHAssetResourceManager.default()
    private var requestID: PHAssetResourceDataRequestID?

    func load(
        _ resource: PHAssetResource,
        to url: URL,
        allowNetwork: Bool,
        progress: @escaping (Double) -> Void,
        completion: @escaping (Result<URL, Error>) -> Void
    ) {
        let options = PHAssetResourceRequestOptions()
        options.isNetworkAccessAllowed = allowNetwork
        options.progressHandler = { value in
            progress(value)
        }

        requestID = manager.writeData(
            for: resource,
            toFile: url,
            options: options
        ) { [weak self] error in
            self?.requestID = nil
            if let error {
                completion(.failure(error))
            } else {
                completion(.success(url))
            }
        }
    }

    func cancel() {
        if let requestID {
            manager.cancelDataRequest(requestID)
            self.requestID = nil
        }
    }
}
~~~

Do not leave a partially written file in the ready state. Validate the output after completion and delete it on cancellation or failure.

## Recipe 9: Inspect image metadata before decoding

Image I/O can inspect a source and create a bounded thumbnail.

~~~swift
import ImageIO

struct ImagePreview {
    let image: CGImage
    let width: Int
    let height: Int
}

func makePreview(
    data: Data,
    maxPixelSize: Int
) throws -> ImagePreview {
    guard let source = CGImageSourceCreateWithData(
        data as CFData,
        [kCGImageSourceShouldCache: false] as CFDictionary
    ) else {
        throw MediaError.invalidImage
    }

    let options: [CFString: Any] = [
        kCGImageSourceCreateThumbnailFromImageAlways: true,
        kCGImageSourceCreateThumbnailWithTransform: true,
        kCGImageSourceThumbnailMaxPixelSize: maxPixelSize,
        kCGImageSourceShouldCache: false
    ]
    guard let image = CGImageSourceCreateThumbnailAtIndex(
        source,
        0,
        options as CFDictionary
    ) else {
        throw MediaError.invalidImage
    }

    return ImagePreview(
        image: image,
        width: image.width,
        height: image.height
    )
}
~~~

Inspect source properties separately when the model or export policy needs dimensions, orientation, GPS, gain map, depth, or XMP.

## Recipe 10: Write a privacy-reviewed image derivative

Use a destination policy that excludes sensitive metadata when the product requires a clean share.

~~~swift
import ImageIO

func writeCleanJPEG(
    sourceData: Data,
    destination: URL,
    quality: Double
) throws {
    guard let source = CGImageSourceCreateWithData(
        sourceData as CFData,
        nil
    ),
    let image = CGImageSourceCreateImageAtIndex(source, 0, nil),
    let destinationRef = CGImageDestinationCreateWithURL(
        destination as CFURL,
        "public.jpeg" as CFString,
        1,
        nil
    ) else {
        throw MediaError.invalidImage
    }

    let properties: [CFString: Any] = [
        kCGImageDestinationLossyCompressionQuality: quality,
        kCGImageMetadataShouldExcludeGPS: true,
        kCGImageMetadataShouldExcludeXMP: true
    ]
    CGImageDestinationAddImage(
        destinationRef,
        image,
        properties as CFDictionary
    )
    guard CGImageDestinationFinalize(destinationRef) else {
        throw MediaError.exportFailed
    }
}
~~~

Reopen the destination with CGImageSource and inspect it. A destination dictionary is not a substitute for output verification.

## Recipe 11: Request a bounded PhotoKit thumbnail

PhotoKit may deliver a degraded and a final result. Keep both states explicit.

~~~swift
import Photos
import UIKit

final class ThumbnailLoader {
    private let manager = PHImageManager.default()
    private var requestID: PHImageRequestID?

    func request(
        asset: PHAsset,
        targetSize: CGSize,
        completion: @escaping (UIImage?, Bool, [AnyHashable: Any]?) -> Void
    ) {
        cancel()
        let options = PHImageRequestOptions()
        options.deliveryMode = .opportunistic
        options.resizeMode = .fast
        options.isNetworkAccessAllowed = false

        requestID = manager.requestImage(
            for: asset,
            targetSize: targetSize,
            contentMode: .aspectFill,
            options: options
        ) { image, info in
            let degraded = (info?[PHImageResultIsDegradedKey] as? Bool) ?? false
            completion(image, degraded, info)
        }
    }

    func cancel() {
        if let requestID {
            manager.cancelImageRequest(requestID)
            self.requestID = nil
        }
    }
}
~~~

The UI should not show “original ready” when it only received a degraded thumbnail.

## Recipe 12: Request a Live Photo only for playback

Use a still request for list thumbnails and a Live Photo request for a playback surface.

~~~swift
import Photos

final class LivePhotoLoader {
    private let manager = PHImageManager.default()
    private var requestID: PHImageRequestID?

    func request(
        asset: PHAsset,
        targetSize: CGSize,
        completion: @escaping (PHLivePhoto?, [AnyHashable: Any]?) -> Void
    ) {
        let options = PHLivePhotoRequestOptions()
        options.deliveryMode = .opportunistic
        options.isNetworkAccessAllowed = true
        options.progressHandler = { progress, _ in
            // Map to a visible downloading state.
            _ = progress
        }

        requestID = manager.requestLivePhoto(
            for: asset,
            targetSize: targetSize,
            contentMode: .aspectFit,
            options: options,
            resultHandler: completion
        )
    }

    func cancel() {
        if let requestID {
            manager.cancelImageRequest(requestID)
            self.requestID = nil
        }
    }
}
~~~

When the result info says the representation is degraded, keep loading. When motion cannot be delivered, keep the still representation and explain the fallback.

## Recipe 13: Observe a fetched Photos result

Register a change observer for objects the screen or store depends on.

~~~swift
import Photos

final class LibraryObserver: NSObject, PHPhotoLibraryChangeObserver {
    private var fetchResult: PHFetchResult<PHAsset>?

    func start() {
        fetchResult = PHAsset.fetchAssets(
            with: .image,
            options: nil
        )
        PHPhotoLibrary.shared().register(self)
    }

    func stop() {
        PHPhotoLibrary.shared().unregisterChangeObserver(self)
        fetchResult = nil
    }

    func photoLibraryDidChange(_ changeInstance: PHChange) {
        guard let fetchResult,
              let details = changeInstance.changeDetails(
                for: fetchResult
              ) else {
            return
        }
        self.fetchResult = details.fetchResultAfterChanges
        // Send a value snapshot to the main actor.
    }
}
~~~

Use the current Swift/Objective-C bridging signature in the target SDK. Do not mutate SwiftUI state directly from an arbitrary PhotoKit callback queue.

## Recipe 14: Build a non-destructive still edit

The output and adjustment data are staging values until the change block succeeds.

~~~swift
import Photos

struct FilterParameters: Codable, Sendable {
    let name: String
    let intensity: Double
    let version: Int
}

func prepareEdit(
    asset: PHAsset,
    renderedURL: URL,
    parameters: FilterParameters
) async throws {
    let options = PHContentEditingInputRequestOptions()
    options.isNetworkAccessAllowed = true
    options.canHandleAdjustmentData = { adjustment in
        adjustment.formatIdentifier == "com.example.filter"
    }

    let input = try await requestEditingInput(
        for: asset,
        options: options
    )
    let output = PHContentEditingOutput(contentEditingInput: input)
    try FileManager.default.copyItem(
        at: renderedURL,
        to: output.renderedContentURL
    )
    output.adjustmentData = PHAdjustmentData(
        formatIdentifier: "com.example.filter",
        formatVersion: String(parameters.version),
        data: try JSONEncoder().encode(parameters)
    )

    try await performPhotoLibraryChanges {
        let request = PHAssetChangeRequest(for: asset)
        request.contentEditingOutput = output
    }
}
~~~

The requestEditingInput and performPhotoLibraryChanges helpers are target-specific async bridges. Keep the temporary output URL alive until the Photos change completes and re-fetch the asset after success.

## Recipe 15: Process a Live Photo edit

Use PHLivePhotoEditingContext so the still and motion frames receive the same visual operation.

~~~swift
import CoreImage
import Photos

func editLivePhoto(
    input: PHContentEditingInput,
    output: PHContentEditingOutput
) throws {
    guard let context = PHLivePhotoEditingContext(
        livePhotoEditingInput: input
    ) else {
        throw MediaError.notALivePhoto
    }

    context.frameProcessor = { frame in
        let inputImage = frame.image
        return applyFilter(to: inputImage)
    }
    context.audioVolume = 1.0
    context.saveLivePhoto(
        to: output,
        options: nil
    ) { success, error in
        if let error {
            // Map to a retryable edit state.
            _ = error
        } else if !success {
            // Do not mark the edit as committed.
        }
    }
}
~~~

The frame processor must be profiled on a physical device. A preview-quality preparation is not proof that a full-quality Live Photo can be saved or played.

## Recipe 16: Model a local-AI proposal

Keep model output separate from a Photos change request.

~~~swift
struct MediaProposal: Codable, Sendable, Equatable {
    let source: MediaSourceManifest
    let modelID: String
    let modelRevision: String
    let label: String?
    let confidence: Double?
    let adjustment: FilterParameters?
    let needsReview: Bool
}

enum ProposalDecision: String, Codable, Sendable {
    case accepted
    case rejected
    case staleSource
    case failed
}

func acceptProposal(
    _ proposal: MediaProposal
) async throws {
    let current = try await currentSource(
        for: proposal.source
    )
    guard current.representationRevision
            == proposal.source.representationRevision else {
        throw MediaError.staleProposal
    }
    guard proposal.needsReview == false else {
        throw MediaError.confirmationRequired
    }
    // Call the same reviewed edit/export operation used by a human action.
}
~~~

If the proposal concerns identity, health, location, safety, or a destructive mutation, require an explicit review regardless of confidence.

## Recipe 17: Render source-aware SwiftUI state

Use native controls and make the authority transition readable.

~~~swift
import SwiftUI

struct MediaReviewView: View {
    let state: MediaReadiness

    var body: some View {
        Group {
            switch state {
            case .idle:
                ContentUnavailableView(
                    "Choose media",
                    systemImage: "photo.on.rectangle",
                    description: Text("Select a photo, video, or Live Photo.")
                )
            case .downloading(let progress):
                ProgressView(
                    "Downloading from iCloud",
                    value: progress
                )
            case .previewReady:
                Text("Preview ready")
            case .proposalReady:
                Text("Review suggested changes")
            case .committed:
                Label("Saved", systemImage: "checkmark.circle.fill")
            case .missingSource:
                ContentUnavailableView(
                    "Source unavailable",
                    systemImage: "photo.badge.exclamationmark"
                )
            case .failed(let message):
                Label(message, systemImage: "exclamationmark.triangle")
            default:
                ProgressView()
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .padding()
    }
}
~~~

Use a glass-backed control group only for app-owned review actions. Keep the media legible and provide an opaque/high-contrast fallback.

## Recipe 18: Record proof for a media operation

Evidence should identify the source, representation, device, and commit boundary.

~~~swift
struct MediaProof: Codable, Sendable {
    let build: String
    let device: String
    let os: String
    let sourceKind: String
    let localIdentifier: String?
    let representation: String
    let modelRevision: String?
    let operation: Operation
    let outcome: Outcome
    let evidencePath: String
    let recordedAt: Date

    enum Operation: String, Codable, Sendable {
        case pickerLoad
        case resourceDownload
        case thumbnail
        case livePhotoPlayback
        case libraryEdit
        case export
        case aiProposal
    }

    enum Outcome: String, Codable, Sendable {
        case ready
        case reviewed
        case committed
        case exported
        case missing
        case rejected
        case failed
    }
}
~~~

Attach metadata inspection, authorization state, accessibility result, and physical-device notes to the evidence path. A screenshot without source and operation context is not enough.

## Recipe 19: Run the media route checklist

~~~text
[ ] Picker filter and selection cap match the feature job.
[ ] Picker placeholders are not treated as bytes.
[ ] Transferable or PhotoKit representation is explicit.
[ ] Late loads cannot overwrite newer selections.
[ ] PhotoKit access level and limited-library state are tested.
[ ] PHAsset and PHAssetResource are re-resolved before mutation.
[ ] iCloud/network and cancellation behavior are visible.
[ ] Image I/O validates type, size, orientation, and metadata.
[ ] Temporary files are bounded and deleted.
[ ] Live Photo playback, still fallback, and paired edit are tested.
[ ] PHContentEditingOutput and adjustment data are used for library edits.
[ ] Export results are reopened and inspected.
[ ] On-device AI remains a provenance-bearing proposal.
[ ] VoiceOver, Dynamic Type, Reduce Motion, contrast, keyboard, and pointer are tested.
[ ] Physical-device, archive, TestFlight, and release evidence is attached.
~~~

## Sources

- [PhotosUI](https://developer.apple.com/documentation/photosui)
- [PhotosPicker](https://developer.apple.com/documentation/photosui/photospicker)
- [PhotosPickerItem](https://developer.apple.com/documentation/photosui/photospickeritem)
- [PhotosPickerItem.loadTransferable](https://developer.apple.com/documentation/photosui/photospickeritem/loadtransferable%28type%3A%29)
- [Bringing Photos picker to your SwiftUI app](https://developer.apple.com/documentation/PhotoKit/bringing-photos-picker-to-your-swiftui-app)
- [Core Transferable](https://developer.apple.com/documentation/coretransferable)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [Photos](https://developer.apple.com/documentation/photos)
- [PHPhotoLibrary](https://developer.apple.com/documentation/photos/phphotolibrary)
- [Delivering an enhanced privacy experience in your Photos app](https://developer.apple.com/documentation/photokit/delivering-an-enhanced-privacy-experience-in-your-photos-app)
- [PHAsset](https://developer.apple.com/documentation/photos/phasset)
- [PHAssetResource](https://developer.apple.com/documentation/photos/phassetresource)
- [PHAssetResourceManager](https://developer.apple.com/documentation/photos/phassetresourcemanager)
- [PHAssetResourceRequestOptions](https://developer.apple.com/documentation/photos/phassetresourcerequestoptions)
- [PHImageManager](https://developer.apple.com/documentation/photos/phimagemanager)
- [PHImageRequestOptions](https://developer.apple.com/documentation/photos/phimagerequestoptions)
- [PHVideoRequestOptions](https://developer.apple.com/documentation/photos/phvideorequestoptions)
- [PHLivePhoto](https://developer.apple.com/documentation/photos/phlivephoto)
- [PHLivePhotoRequestOptions](https://developer.apple.com/documentation/photos/phlivephotorequestoptions)
- [PHLivePhotoView](https://developer.apple.com/documentation/photosui/phlivephotoview)
- [PHPhotoLibraryChangeObserver](https://developer.apple.com/documentation/photos/phphotolibrarychangeobserver)
- [PHContentEditingInput](https://developer.apple.com/documentation/photos/phcontenteditinginput)
- [PHContentEditingOutput](https://developer.apple.com/documentation/photos/phcontenteditingoutput)
- [PHContentEditingInputRequestOptions](https://developer.apple.com/documentation/photos/phcontenteditinginputrequestoptions)
- [PHAdjustmentData](https://developer.apple.com/documentation/photos/phadjustmentdata)
- [PHAssetChangeRequest](https://developer.apple.com/documentation/photos/phassetchangerequest)
- [PHLivePhotoEditingContext](https://developer.apple.com/documentation/photos/phlivephotoeditingcontext)
- [Image I/O](https://developer.apple.com/documentation/imageio)
- [CGImageSource](https://developer.apple.com/documentation/imageio/cgimagesource)
- [CGImageDestination](https://developer.apple.com/documentation/imageio/cgimagedestination)
- [Vision](https://developer.apple.com/documentation/vision)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Live Photos HIG](https://developer.apple.com/design/human-interface-guidelines/live-photos)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Accessibility HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
