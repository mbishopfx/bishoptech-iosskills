# SwiftUI PhotosPicker, PhotoKit, Image I/O, Live Photo, and media-source/editing review

Photos features are a chain of distinct authorities. PhotosPicker gives a person a system-owned way to choose media. PhotoKit exposes authorized library objects and change requests. Image I/O reads and writes image containers and metadata. PhotosUI and PhotoKit represent Live Photos as paired still, motion, and sound content. Vision and Core ML can propose observations from materialized bytes. None of those layers alone proves that an app owns a file, that the bytes are current, that a person or place is correctly identified, or that a proposed edit has been committed.

This review extends the existing [SwiftUI media capture review](88-swiftui-media-capture-and-review.md), [PhotosUI/PhotoKit source and editing deep dive](67-photosui-photokit-source-and-editing.md), [Image I/O deep dive](54-imageio-source-destination-and-metadata.md), [photos source and AI route](../50-capability-recipes/91-photos-source-and-ai-capability-route.md), and [Photos source/editing proof matrix](../60-verification/85-photos-source-and-editing-proof-matrix.md). Its distinct focus is the current iOS media-source contract: narrow picker selection, authorized library identity, representation loading, source provenance, non-destructive editing, Live Photo integrity, metadata privacy, local-AI proposal boundaries, and a reviewable export or Photos-library mutation.

## The media-source contract

Keep the authority transitions visible:

~~~text
user job
-> narrow PhotosPicker or authorized PhotoKit route
-> placeholder or current PHAsset identity
-> selected representation/resource with source metadata
-> bounded decode/thumbnail/orientation/metadata policy
-> optional local Vision/Core ML proposal
-> user review and edit parameters
-> derivative export or PHContentEditingOutput
-> PHPhotoLibrary change request or app-owned file/record
-> change observation, provenance, and recovery
~~~

The system owns the picker presentation, Photos authorization prompt, library storage, iCloud availability, and some representation delivery. The app owns the selected feature scope, the representation it requests, byte and memory budgets, source manifest, edit policy, user review, destination, and the claims it makes about the result.

## Select the smallest route

Choose the route by the user’s job rather than by the framework with the largest API surface.

| User job | Preferred route | What it establishes | What it does not establish |
| --- | --- | --- | --- |
| One-off photo or video input | SwiftUI PhotosPicker | The person chose a picker item for this operation | A broad library grant, durable file URL, or original-byte ownership |
| Multiple bounded inputs | PhotosPicker with a selection cap | A finite set of user-selected placeholders | That every item is local, decodable, or the same representation |
| Browse a persistent library feature | PhotoKit with the least required access level | Authorized access to current PHAsset objects | That cached objects, locations, or bytes remain current |
| Load an image preview | PHImageManager or a picker Transferable | A representation suitable for the requested size | Full-resolution original bytes or final color/metadata fidelity |
| Stream an underlying resource | PHAssetResourceManager | Bytes for a specific resource with an iCloud/network policy | That the resource is the user’s preferred or only representation |
| Play a Live Photo | PHImageManager requestLivePhoto and PHLivePhotoView | A paired motion-and-sound representation | That a still thumbnail has the same playback readiness |
| Non-destructive library edit | PHContentEditingInput, PHContentEditingOutput, PHAdjustmentData, PHAssetChangeRequest | A Photos edit that can be reconstructed or reverted | That a rendered preview has been committed |
| Export a derivative | Image I/O, AVFoundation, or an app-owned file workflow | A new output with an explicit format and metadata policy | That the output is still a Photos asset or preserves every source feature |
| On-device AI review | Materialized representation plus Vision/Core ML | A model proposal with provenance and model revision | Identity, diagnosis, legal truth, or permission to mutate the library |

Do not silently upgrade a one-off picker selection into an authorization screen. Do not request read/write access merely to process a single user-selected image when PhotosPicker supplies the narrower route.

## PhotosPicker is selection plus transfer

PhotosUI describes PhotosPickerItem values as placeholder objects. The item can expose an item identifier and supported content types, but the app must request a representation through Transferable or another documented route. A picker selection is therefore an intent to load, not an already-materialized image.

The SwiftUI picker can filter images, videos, Live Photos, screenshots, or other supported categories through PHPickerFilter. A multiple-selection route should set an explicit maximum and maintain a generation or selection token so a late load cannot replace the person’s newer selection.

The built-in Image Transferable path has a format boundary: the Apple documentation notes that SwiftUI Image supports PNG through its Transferable conformance. For HEIF, JPEG, RAW, video, Live Photo, or a file-backed pipeline, define a custom Transferable or use the appropriate PhotoKit representation request. A successful item load is still not a proof that the chosen representation is the original.

~~~swift
import PhotosUI
import SwiftUI
import UniformTypeIdentifiers

struct MediaPickerView: View {
    @State private var selection: PhotosPickerItem?
    @State private var loadGeneration = UUID()
    @State private var state: ImportState = .idle

    var body: some View {
        VStack {
            PhotosPicker(
                "Choose media",
                selection: $selection,
                matching: .any(of: [.images, .videos, .livePhotos]),
                preferredItemEncoding: .current
            )
            .buttonStyle(.borderedProminent)

            ImportStateView(state: state)
        }
        .task(id: selection) {
            let generation = UUID()
            loadGeneration = generation
            guard let selection else {
                state = .idle
                return
            }

            state = .loading
            do {
                let material = try await selection.loadTransferable(
                    type: ImportedMedia.self
                )
                guard loadGeneration == generation else { return }
                guard let material else {
                    state = .failed("No supported representation")
                    return
                }
                state = .ready(material)
            } catch is CancellationError {
                state = .idle
            } catch {
                guard loadGeneration == generation else { return }
                state = .failed(error.localizedDescription)
            }
        }
    }
}
~~~

The exact custom Transferable implementation belongs in a named target. Keep the representation file in a controlled temporary location, record the source item identifier when available, and delete the derivative when the feature no longer needs it.

## PhotoKit authorization is a live state machine

PhotoKit supports different access levels and limited-library behavior. Inspect authorization with the access level required by the feature. A user can change the choice in Settings or update a limited selection after the app has loaded its first screen.

The access state should distinguish at least:

- not determined;
- restricted by the system or account;
- denied;
- authorized for the requested level;
- limited to a selected subset;
- temporarily unavailable or unable to deliver the requested iCloud representation.

If the feature only adds new media, evaluate add-only access. If the feature reads existing library assets, evaluate read/write access and the limited-library route. If the feature only uses PhotosPicker, document why no broad PhotoKit grant is needed. Confirm the exact Info.plist usage descriptions and target privacy manifest in the named Xcode target.

~~~swift
import Photos

enum PhotoAccessState: Equatable, Sendable {
    case notDetermined
    case restricted
    case denied
    case limited
    case authorized
}

func currentReadWriteAccess() -> PhotoAccessState {
    switch PHPhotoLibrary.authorizationStatus(for: .readWrite) {
    case .notDetermined:
        return .notDetermined
    case .restricted:
        return .restricted
    case .denied:
        return .denied
    case .limited:
        return .limited
    case .authorized:
        return .authorized
    @unknown default:
        return .denied
    }
}

func requestReadWriteAccess() async -> PhotoAccessState {
    let status = await PHPhotoLibrary.requestAuthorization(for: .readWrite)
    switch status {
    case .authorized:
        return .authorized
    case .limited:
        return .limited
    case .restricted:
        return .restricted
    case .denied:
        return .denied
    case .notDetermined:
        return .notDetermined
    @unknown default:
        return .denied
    }
}
~~~

The legacy authorization methods have different limited-library semantics. Use the access-level forms for the behavior the feature claims to support. A permission Boolean should never be the only source of truth for whether a particular asset can be fetched or a resource can be downloaded.

## A PHAsset is an identity and metadata projection

PHAsset represents a current Photos-library object. Its localIdentifier can be used to fetch the current object again, but it is not a file URL and does not freeze the bytes or metadata. Asset fields such as mediaType, mediaSubtypes, contentType, pixel dimensions, creation and modification dates, location, favorite/hidden state, and adjustment state are snapshots that can change.

Persist an app-owned source manifest instead of serializing a PHAsset object:

~~~swift
struct MediaSourceManifest: Codable, Sendable {
    let sourceKind: SourceKind
    let localIdentifier: String?
    let itemIdentifier: String?
    let contentType: String?
    let resourceType: String?
    let pixelWidth: Int?
    let pixelHeight: Int?
    let sourceModificationDate: Date?
    let capturedAt: Date
    let representationRevision: String

    enum SourceKind: String, Codable, Sendable {
        case photosPicker
        case photoKit
        case appFile
        case cameraCapture
    }
}
~~~

If the feature needs cross-device mapping, evaluate PHCloudIdentifier and its current mapping APIs instead of treating a local identifier as globally portable. If the user deletes, edits, or removes access to an asset, resolve the identifier again and move the app record to a missing or needs-reimport state.

## Resource identity is not representation preference

PHAssetResource describes one underlying resource associated with a PHAsset. A photo can have JPEG and RAW resources. A Live Photo has still and video resources. An adjusted asset can contain original and adjusted resources plus adjustment data. Resource type and content type therefore matter.

Use PHAssetResourceManager when the feature needs underlying resource bytes, especially when streaming to a file or processing a resource that PHImageManager’s rendered image path cannot represent. Set PHAssetResourceRequestOptions.isNetworkAccessAllowed intentionally. If iCloud delivery is allowed, expose progress and cancellation; if it is not allowed, represent an unavailable-local-resource state.

Do not infer that the resource returned first is the canonical original. Select by an explicit policy:

1. identify the owning asset;
2. enumerate resources;
3. select the accepted PHAssetResourceType and UTType;
4. enforce byte, dimension, and duration budgets;
5. stream to a temporary destination;
6. validate the bytes and record a digest or local revision;
7. delete the temporary material when the operation ends.

The resource’s assetLocalIdentifier can bridge back to the owning PHAsset. It is useful for provenance, but it does not grant authorization and it does not make a local file durable.

## Render with a bounded image pipeline

Image I/O can inspect a source, read properties, create thumbnails, access metadata, and write a destination. Use it before a full decode when the user is viewing a grid or when an on-device model needs a bounded input.

The source pipeline should establish:

- a byte budget before reading untrusted or very large data;
- a supported Uniform Type Identifier;
- image count and primary-image index where relevant;
- dimensions, orientation, color space, alpha, and auxiliary data;
- a thumbnail target size and caching policy;
- metadata retention or exclusion policy;
- a final decode and validation step.

Use kCGImageSourceCreateThumbnailWithTransform to honor source orientation in thumbnails. Do not use a preview’s pixel dimensions as proof of the original. For exports, decide whether to preserve or exclude GPS/XMP metadata, gain maps, depth, portrait mattes, and other auxiliary content. The default privacy posture for sharing should be explicit rather than inherited accidentally from the source container.

~~~swift
import ImageIO
import UniformTypeIdentifiers

struct ImageInspection: Sendable {
    let typeIdentifier: String
    let width: Int
    let height: Int
    let hasGPS: Bool
}

func inspectImage(_ data: Data) throws -> ImageInspection {
    guard data.count <= 100 * 1024 * 1024 else {
        throw MediaError.byteBudgetExceeded
    }
    guard let source = CGImageSourceCreateWithData(
        data as CFData,
        [kCGImageSourceShouldCache: false] as CFDictionary
    ) else {
        throw MediaError.invalidImage
    }

    guard let type = CGImageSourceGetType(source) else {
        throw MediaError.unknownImageType
    }
    guard let properties = CGImageSourceCopyPropertiesAtIndex(
        source,
        0,
        nil
    ) as? [CFString: Any] else {
        throw MediaError.missingImageProperties
    }

    let width = properties[kCGImagePropertyPixelWidth] as? Int ?? 0
    let height = properties[kCGImagePropertyPixelHeight] as? Int ?? 0
    let hasGPS = properties[kCGImagePropertyGPSDictionary] != nil

    guard width > 0, height > 0 else {
        throw MediaError.invalidDimensions
    }
    return ImageInspection(
        typeIdentifier: type as String,
        width: width,
        height: height,
        hasGPS: hasGPS
    )
}
~~~

The Swift dictionary bridging in a recipe sketch should be checked against the SDK and compiler. The invariant is more important than a particular cast: inspect first, decode to a bounded target, and make privacy policy visible.

## PHImageManager can deliver multiple quality states

PHImageManager requests are asynchronous. Image and Live Photo result handlers can be called more than once, including a degraded or temporary representation before a higher-quality result. The info dictionary can indicate in-cloud, degraded, cancelled, or error states.

For a grid, use a target size and a thumbnail policy. For original image data, request the data route and retain orientation. For video, use PHVideoRequestOptions and request an AVAsset, player item, or export session according to the job. For Live Photo playback, request a PHLivePhoto only when motion and sound are needed; use a still image request for a thumbnail.

Keep the PHImageRequestID and cancel when the cell, task, or current selection is no longer interested. A SwiftUI task cancellation alone does not necessarily cancel a PhotoKit request unless the adapter bridges the two.

~~~swift
import Photos
import UIKit

final class PhotoRequestCoordinator {
    private let manager = PHImageManager.default()
    private var requestID: PHImageRequestID?

    func requestThumbnail(
        for asset: PHAsset,
        targetSize: CGSize,
        completion: @escaping (UIImage?, Bool) -> Void
    ) {
        requestID.map(manager.cancelImageRequest)
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
            completion(image, degraded)
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

The callback may be delivered on a framework-controlled queue. Hop to the main actor for SwiftUI state and keep the callback small. Never assume the last callback is successful without checking error and cancellation keys.

## Live Photo is a paired experience

A Live Photo includes a still image plus motion and sound. The user-facing experience should preserve that pairing when the platform supports it. If the environment cannot play a Live Photo, show a still representation and label the fallback.

The Human Interface Guidelines advise applying adjustments to all frames, keeping Live Photo content intact, previewing the complete content before sharing, indicating download and playback readiness, and providing a still-photo sharing option. Avoid disassembling the still, video, and audio into unrelated UI cards that change the meaning of the source.

When displaying playback, use PHLivePhotoView or the current SwiftUI/UIKit interoperability path appropriate to the target. When requesting content, use PHImageManager.requestLivePhoto only for a playback surface. A Live Photo request may download from iCloud if network access is allowed and can provide progress; use a loading state that says the motion is not yet ready.

When editing, create PHLivePhotoEditingContext from a Live Photo PHContentEditingInput. Its frame processor receives the visual content frame by frame, and saveLivePhoto writes the processed result to PHContentEditingOutput. A preview-quality playback preparation is not the same as a committed edit.

## Non-destructive PhotoKit editing

For a library edit, follow the Photos editing contract:

1. fetch the current PHAsset;
2. verify canPerform for the requested operation;
3. request PHContentEditingInput with an explicit network and adjustment-data policy;
4. render a preview and let the person review the parameters;
5. create PHContentEditingOutput;
6. write rendered content to the output URL or process the Live Photo context;
7. attach PHAdjustmentData that can reconstruct the edit;
8. create PHAssetChangeRequest inside PHPhotoLibrary.performChanges;
9. observe the resulting library change and refresh the app record.

Adjustment data is not optional decoration when the app promises that an edit is reversible or editable later. It should encode the app’s edit format identifier, version, and parameters needed to reapply the transformation. If the app cannot handle existing adjustment data, request original content or offer a flatten/restart policy explicitly.

The change block is the commit boundary. A file written to PHContentEditingOutput or a completed preview is not the same as a successful Photos-library mutation.

~~~swift
import Photos

struct FilterAdjustment: Codable, Sendable {
    let filterName: String
    let intensity: Double
    let version: Int
}

func commitStillEdit(
    asset: PHAsset,
    renderedURL: URL,
    adjustment: FilterAdjustment
    ) async throws {
    let inputOptions = PHContentEditingInputRequestOptions()
    inputOptions.isNetworkAccessAllowed = true
    inputOptions.canHandleAdjustmentData = { data in
        data.formatIdentifier == "com.example.app.filter"
    }

    let input = try await asset.contentEditingInput(
        with: inputOptions
    )
    let output = PHContentEditingOutput(contentEditingInput: input)
    try FileManager.default.copyItem(
        at: renderedURL,
        to: output.renderedContentURL
    )
    output.adjustmentData = PHAdjustmentData(
        formatIdentifier: "com.example.app.filter",
        formatVersion: String(adjustment.version),
        data: try JSONEncoder().encode(adjustment)
    )

    try await PHPhotoLibrary.shared().performChanges {
        let request = PHAssetChangeRequest(for: asset)
        request.contentEditingOutput = output
    }
}
~~~

The async helper shown here is a recipe boundary; use the current SDK’s continuation or callback signature and ensure the temporary rendered URL remains available until the change request finishes. Avoid pretending that this sketch compiles without a named target.

## Observe library changes and authorization changes

PhotoKit objects and fetch results can become stale after edits in Photos or another app. Register a PHPhotoLibraryChangeObserver for the fetched objects or collections that drive a screen. Use PHObjectChangeDetails or PHFetchResultChangeDetails to update only what changed when the target supports it.

On a limited-library change, re-evaluate whether each saved local identifier remains visible. If an asset disappears, do not retain its location or expose cached content as if it were still authorized. If the app retains an app-owned derivative, mark its origin and privacy choice clearly.

Observation does not replace a fresh authorization check. At scene activation, background resume, import retry, and before a library mutation, re-check the access state and resolve the current PHAsset.

## On-device AI starts after source materialization

Vision and Core ML should receive a materialized, bounded representation with a source manifest. The pipeline should capture:

- the picker item or PHAsset local identifier;
- the resource type and Uniform Type Identifier;
- the representation revision and load timestamp;
- orientation, dimensions, color-space policy, and any preprocessing;
- the model identifier, revision, compute policy, and request revision;
- the proposal confidence and uncertainty;
- the user’s decision;
- the resulting app-owned record or edit operation.

An on-device model can label, classify, detect, segment, summarize, or propose an edit. It cannot by itself prove that a detected person is a particular person, that a visual observation is a diagnosis, that a geolocation is correct, or that a user intended a destructive edit.

Do not let an AI proposal call PHPhotoLibrary.performChanges directly. Route it through the same current-asset resolver, authorization check, review UI, adjustment policy, and idempotent mutation used by a human-initiated action.

~~~swift
struct MediaModelProposal: Codable, Sendable {
    let source: MediaSourceManifest
    let modelID: String
    let modelRevision: String
    let labels: [String]
    let confidence: Double?
    let proposedAdjustment: FilterAdjustment?
    let requiresReview: Bool
}

enum ProposalDecision: String, Codable, Sendable {
    case accepted
    case rejected
    case deferred
    case staleSource
}
~~~

Keep the proposal as a draft until the person accepts it. If the source asset changes while inference is running, mark the proposal stale and re-run or discard it.

## SwiftUI state should expose authority transitions

A media feature needs more states than loading and loaded:

~~~swift
enum MediaFeatureState: Equatable, Sendable {
    case needsPhotoAccess
    case limitedLibrary
    case readyToChoose
    case selectedPlaceholder(id: String?)
    case downloadingFromICloud(progress: Double?)
    case materializing
    case inspecting
    case previewReady(MediaSourceManifest)
    case proposing(modelRevision: String)
    case reviewRequired(MediaModelProposal)
    case editing
    case exporting
    case committed
    case missingSource
    case denied
    case failed(retryable: Bool, message: String)
}
~~~

Use native controls, system typography, appropriate material, and Liquid Glass composition only for app-owned hierarchy. A glass card can make “review,” “download,” or “edit pending” legible, but it should not imitate the Photos picker’s system chrome or obscure the media itself. Keep an opaque fallback for reduced transparency, accessibility contrast, unavailable blur, and older deployment paths.

## Privacy and metadata are product decisions

Photos may contain faces, locations, time, voice, depth, original filenames, edit history, and other sensitive context. Limit access and retention to the feature’s need.

Before writing or sharing a derivative, choose a policy for:

- GPS and location metadata;
- XMP and EXIF tags;
- original filename and file creation dates;
- depth, portrait matte, gain map, and auxiliary data;
- Live Photo motion and audio;
- face or person-derived embeddings;
- temporary files, caches, logs, and crash diagnostics;
- cloud upload or external model use.

Image I/O provides destination keys for excluding GPS and XMP metadata and for controlling gain-map preservation. The presence of a privacy key in code is not proof that the final exported file has the expected metadata. Reopen the result with Image I/O and inspect it.

Do not log raw photo bytes, GPS coordinates, face crops, or unreviewed model output. If the app stores a derivative, explain what it is, why it is retained, and how the person can delete it.

## Accessibility and native media interaction

Media surfaces should support VoiceOver, Dynamic Type, reduced motion, reduced transparency, high contrast, keyboard and pointer input, Switch Control, and one-handed interaction. Do not use motion as the only signal that a Live Photo is live. Provide a badge, label, or spoken value.

For an AI result, expose the source, action, confidence or uncertainty where useful, and the next review action. A colorized mask or bounding box needs a textual alternative. A disabled edit control needs an explanation such as “Original is still downloading” or “This asset is no longer available.”

If the system picker or Live Photo view supplies a native interaction, preserve its semantics rather than layering a custom gesture that competes with playback or selection.

## Availability, target, and process gates

Before implementation, inspect the named target:

- deployment target and PhotosUI/Photos/ImageIO/Vision/Core ML imports;
- Photos usage descriptions and add-only versus read/write intent;
- privacy manifest and data-use declarations;
- app extension membership if building a Photos editing extension;
- supported device family and hardware decode/model expectations;
- file and storage budgets;
- iCloud/offline behavior;
- background or scene-resume behavior;
- accessibility and localization resources;
- archive entitlements and release configuration.

PhotosPicker, PhotoKit, Live Photo, Image I/O, Vision, and Core ML have overlapping but different availability. A recipe that compiles on the host is not proof that a physical device can load the chosen asset, decode its format, play its motion, run the model, or commit the edit.

## Verification boundary

Keep evidence separated:

| Claim | Evidence | Still not enough |
| --- | --- | --- |
| Picker route is available | Named target compile and system picker run | A binding or preview |
| User selected an item | Physical/system picker record and selection identifier | A constructed PhotosPickerItem |
| Representation loaded | File/type/dimension validation and source manifest | A non-nil preview |
| PhotoKit access is correct | Authorization matrix including limited state | One authorized run |
| Resource is current | Fresh PHAsset/resource resolution and digest/revision | A cached PHAsset |
| Live Photo is playable | Physical-device paired request and playback observation | A still thumbnail |
| Edit committed | Successful performChanges plus library observation | Rendered output URL |
| Edit is reversible | Adjustment data re-open/reapply test | Filter slider preview |
| AI proposal is reviewable | Source/model/proposal/decision record | Label or confidence number |
| Metadata policy works | Reopened output inspection and share fixture | A destination option |
| Release behavior works | Signed archive/TestFlight/system/privacy/accessibility packet | Simulator or debug build |

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
- [PHCachingImageManager](https://developer.apple.com/documentation/photos/phcachingimagemanager)
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
- [CGImageMetadata](https://developer.apple.com/documentation/imageio/cgimagemetadata)
- [kCGImageMetadataShouldExcludeGPS](https://developer.apple.com/documentation/imageio/kcgimagemetadatashouldexcludegps)
- [kCGImageMetadataShouldExcludeXMP](https://developer.apple.com/documentation/imageio/kcgimagemetadatashouldexcludexmp)
- [Vision](https://developer.apple.com/documentation/vision)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Live Photos HIG](https://developer.apple.com/design/human-interface-guidelines/live-photos)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Accessibility HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
