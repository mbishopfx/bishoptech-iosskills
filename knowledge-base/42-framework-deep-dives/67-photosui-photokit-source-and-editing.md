# PhotosUI, PhotoKit, and source-controlled image workflows

## Capability boundary

PhotosUI and PhotoKit expose two different product routes:

1. **User-selected transfer** — `PhotosPicker` or `PHPickerViewController` lets a person choose specific media and gives the app a placeholder/transfer route for those items. The picker is the least-privilege starting point for a one-off image or video workflow.
2. **Library-backed management** — PhotoKit’s `PHPhotoLibrary`, `PHAsset`, fetches, resource managers, change requests, and observers let the app inspect or modify a library within the authorization the person granted.

Keep those boundaries visible:

`picker selection -> transferred representation -> app-owned source record -> optional on-device AI -> review -> optional Photos change request`

A picker result is not a `PHAsset` domain record. A `PHAsset` is metadata, not the image bytes. An image loaded for inference is not permission to scan the rest of the library. A successful `performChanges` call is not proof that the user intended every mutation in the block unless the app made the exact change legible first.

## API object graph

| Concern | Primary API | Boundary to preserve |
| --- | --- | --- |
| SwiftUI selection | `PhotosPicker`, `PhotosPickerItem` | System picker UI and user-selected placeholder/transfer state. |
| UIKit selection | `PHPickerViewController`, `PHPickerConfiguration`, `PHPickerResult` | System picker delegate route for selected `NSItemProvider` representations. |
| Transfer contract | `Transferable`, `TransferRepresentation`, `DataRepresentation`, `FileRepresentation`, `ProxyRepresentation` | Content type, size, import/export, and memory policy between system/app boundaries. |
| Library authorization | `PHPhotoLibrary.authorizationStatus(for:)`, `requestAuthorization(for:)`, `PHAccessLevel`, `PHAuthorizationStatus` | Read/write/add-only/limited/denied/restricted state. |
| Asset identity/metadata | `PHAsset`, `PHObject`, `localIdentifier`, `PHCloudIdentifier` | Photos metadata and device/cloud identity; not a file URL or a durable app record by itself. |
| Fetching | `PHFetchOptions`, `PHFetchResult`, `PHAsset.fetchAssets(...)` | Ordered library query and change-observable result. |
| Thumbnails/representations | `PHImageManager`, `PHCachingImageManager`, `PHImageRequestOptions` | Size, version, delivery, network, degraded-result, and cancellation policy. |
| Underlying resources | `PHAssetResource`, `PHAssetResourceManager`, `PHAssetResourceRequestOptions` | Original/edited/live-photo resource bytes and asynchronous file/data delivery. |
| Editing | `PHContentEditingInput`, `PHContentEditingOutput`, `PHAdjustmentData`, `PHAssetChangeRequest` | User-approved, reversible or reconstructable content-edit route. |
| Library mutations | `PHPhotoLibrary.performChanges`, `PHAssetChangeRequest`, collection change requests | A transaction-like change block that Photos applies with authorization. |
| Library changes | `PHPhotoLibraryChangeObserver`, `PHChange`, `PHFetchResultChangeDetails`, `PHObjectChangeDetails` | External edits/deletes/reorders and invalidation of app projections. |
| Limited access management | `presentLimitedLibraryPicker(from:)` | User-mediated expansion of the app’s selected-library scope. |

## Choose the smallest access route

| Product outcome | Start with | Add only when needed |
| --- | --- | --- |
| Pick one photo for an avatar or document | `PhotosPicker` with `.images` | Custom `Transferable` or file representation for format/size control. |
| Pick several photos for a local model | `PhotosPicker` with bounded `maxSelectionCount` | Bounded task group, file-backed transfer, progress/cancellation, model input contract. |
| Pick a video or Live Photo | `PhotosPicker`/`PHPickerViewController` filter | `Transferable` representation or PhotoKit resource/editing route. |
| Browse an album or library grid | PhotoKit fetches plus `PHCachingImageManager` | `PHPhotoLibrary` authorization, change observer, limited access UI, incremental updates. |
| Read original or edited bytes | `PHImageManager.requestImageDataAndOrientation` | `PHAssetResourceManager` for underlying resources, iCloud/network policy, temporary-file lifecycle. |
| Apply a non-destructive edit | `PHContentEditingInput`/`Output`, `PHAdjustmentData`, `PHAssetChangeRequest` | Explicit review and capability/adjustment compatibility. |
| Save a new generated image | User review plus `PHPhotoLibrary.performChanges`/creation request | Add-only authorization and an honest saved/failed state. |
| Keep an app projection current | Fetch result plus `PHPhotoLibraryChangeObserver` | Persistent-change/history route when the product truly needs cross-launch recovery. |

Do not ask for full read/write library access merely because a picker result is inconvenient. The system picker is designed to let the person grant access to selected items without library authorization.

## PhotosPicker is a placeholder and transfer boundary

`PhotosPickerItem` is a placeholder object. It conforms to `Transferable` and can load a representation that the app requests. The placeholder is not the image data and should not be treated as ready input. Loading can fail, return `nil`, or take time when Photos needs to retrieve data from iCloud.

Use the selection identity to supersede work:

```text
selected item generation 1
  -> load representation
selected item generation 2
  -> cancel/ignore generation 1
  -> publish only generation 2
```

The default `Image` transfer route has format limitations documented by Apple. For images that may be HEIF, JPEG, RAW, depth, or another supported type, define a custom `Transferable` that imports a content type or use `FileRepresentation` for large assets. Prefer file-backed transfer for long media or multi-selection so the app does not eagerly hold every byte in memory.

Record the source with the transfer result:

```swift
struct PickedMediaSource: Sendable, Equatable {
    let sourceID: UUID
    let pickerItemID: String?
    let contentTypeIdentifier: String?
    let importedAt: Date
    let storageURL: URL?
    let isUserSelected: Bool
}
```

This is an app-owned record. Do not persist an `NSItemProvider`, `PhotosPickerItem`, or temporary file URL without copying the bytes into a lifecycle you control and stating the retention policy.

## Core Transferable representation choice

Choose a representation by cost and meaning:

| Representation | Use for | Avoid when |
| --- | --- | --- |
| `CodableRepresentation` | Structured app records with a declared `UTType` | The receiver needs a native image/video file rather than a model payload. |
| `DataRepresentation` | In-memory binary data with a known content type | The asset is large enough that holding or copying all bytes is expensive. |
| `FileRepresentation` | Large images/video/documents or a file-backed pipeline | The file is private and you have not designed temporary-file cleanup and access policy. |
| `ProxyRepresentation` | A lightweight fallback such as a title or text representation | The export/import work is long-running, performs file/network work, or could block the transfer operation. |

Put the most faithful representation first and compatible fallbacks after it. Use a specific `UTType` that describes the content, not a generic data type. If the transfer crosses app/process boundaries, treat visibility and redaction as part of the product contract.

## PhotoKit authorization and limited access

PhotoKit access is explicit and granular. Use `PHPhotoLibrary.authorizationStatus(for:)` and request the access level that matches the task. Model at least:

```text
notDetermined -> requesting -> authorized
                          -> limited
                          -> denied
                          -> restricted
```

`PHAccessLevel.readWrite` is appropriate only when the app truly needs to read and change existing library content. `PHAccessLevel.addOnly` is narrower for apps that only save new assets. A limited status means the user granted access to a selected subset; it is not equivalent to the entire library.

When limited access blocks a task, explain the missing scope and use `presentLimitedLibraryPicker(from:)` through a user-initiated UI route. Do not repeatedly prompt or silently degrade into scanning inaccessible assets. The picker route can often avoid this authorization entirely.

The privacy strings, access level, feature explanation, and actual code path must agree. Permission status is not proof that a specific asset is available, local, unmodified, or suitable for AI processing.

## PHAsset is metadata; bytes may be remote

`PHAsset` objects represent library assets and expose metadata such as local identifier, content type, media type/subtype, dimensions, dates, location, adjustment state, and playback style. The underlying media may be in iCloud and not present locally. Treat a `PHAsset` as a read-only metadata projection until the app requests a representation.

Persist an app source record with:

- the local identifier only when the product’s identity scope is device-local;
- a cloud identifier mapping if cross-device/iCloud continuity is a real requirement;
- the asset’s media/content type and selected version (original/current);
- fetched-at, modification date, and an invalidation policy;
- whether the app retains a copy, a derivative, or only a model observation;
- the user action that authorized the source to enter the feature.

Local identifiers are device-specific. Do not use them as a server-global identity without a documented mapping strategy. A deleted, hidden, limited, or changed asset must invalidate or downgrade app projections that depended on it.

## Thumbnail, current, and original data routes

Use `PHImageManager` or `PHCachingImageManager` for display-sized images. `requestImage(for:targetSize:contentMode:options:resultHandler:)` can deliver a degraded image before the final representation; inspect the result info and do not treat a degraded thumbnail as the final model input. Cancel an image request when a cell, source, or generation is replaced.

Use `requestImageDataAndOrientation(for:options:resultHandler:)` when a model or export requires the largest represented image data and EXIF orientation. Select `PHImageRequestOptionsVersion.current` when the feature should use the rendered result of existing edits; select original only when the product has a clear reason and the user-facing contract supports it. `isNetworkAccessAllowed` and progress/error policy determine whether Photos may retrieve iCloud content.

Use `PHAssetResourceManager` when the feature needs direct underlying resources, such as original image bytes, edited resources, or Live Photo components. Requests can deliver data progressively or write to a file and can be cancelled. The callback queue is not the main actor; marshal UI state explicitly. A resource file is private working data unless the user explicitly exports or saves it.

## Non-destructive editing and adjustment data

For an edit that should remain reopenable, request a `PHContentEditingInput` with `PHContentEditingInputRequestOptions`. Implement `canHandleAdjustmentData` so Photos knows whether the app can reconstruct prior edits. Create a `PHContentEditingOutput`, write the edited photo/video/Live Photo content, attach `PHAdjustmentData` that describes the recipe, and submit the corresponding change request in a `PHPhotoLibrary.performChanges` block.

If the app cannot handle previous adjustment data, Photos may provide the most recent rendered output instead of the original. That can be a valid edit base but may prevent the app from reconstructing or reverting prior parameters. Explain the route before the person accepts it.

Do not put long image processing or network work inside a PhotoKit change block. Prepare and validate the output first, then submit the smallest user-approved mutation. Editing multiple assets should use one coordinated change block when the product intends the batch as one action.

## Library changes are external state

After fetching assets or collections, register a `PHPhotoLibraryChangeObserver`. Photos can notify the app when another app, the Photos app, or another device changes or deletes the objects. Apply `PHFetchResultChangeDetails` and `PHObjectChangeDetails` to update projections, invalidate source IDs, cancel in-flight requests, and remove stale model proposals.

For products that need cross-launch recovery from large libraries, inspect the persistent-change APIs and design a token/anchor strategy. Do not assume a change observer remains active while the process is terminated. The local app database is a projection/cache; Photos remains the authority for library ownership and asset state.

## On-device AI over selected media

The safe AI boundary is:

`explicit selection -> representation load -> input normalization -> model observation -> source-linked proposal -> review`

Attach `sourceID`, Photos local/cloud identifier when appropriate, asset modification timestamp, transfer content type, orientation/crop policy, model version, and generated-at time to every result. If an asset changes or disappears before the person accepts a proposal, mark it stale and require reprocessing.

Use the smallest representation that satisfies the model. A thumbnail may be enough for a visual index; a full-resolution resource may be required for OCR or fine detail. Do not send unselected library items, precise location metadata, hidden albums, or unrelated EXIF fields into a model context by default. On-device execution reduces network exposure but does not eliminate retention, logging, access-control, or deletion obligations.

AI outputs remain observations or proposals. Do not infer identity, medical condition, ownership, consent, safety, or a person’s intent from a photo merely because a classifier or multimodal model returned a label. Require deterministic validation and user approval before writing metadata, creating an album, exporting a file, or triggering an external action.

## Liquid Glass photo review

Keep the source image primary and use glass for controls/status:

```text
source image or grid
  model/data readiness
  source + version + timestamp
  suggestion or “not enough evidence”
  [Edit] [Save result] [Discard]
```

Do not use a glossy overlay to make an uncertain model output appear authoritative. Show original/current/derived state plainly. Keep “save to Photos” separate from “save in this app.” Provide a non-glass fallback for reduced transparency and test over bright, dark, HDR, portrait, Live Photo, and degraded-thumbnail states.

## Availability, privacy, and proof gates

| Gate | Question |
| --- | --- |
| Picker | Does the person explicitly select the item, and is the representation supported? |
| Authorization | Does the feature require read/write, add-only, or no Photos library authorization? |
| Scope | Is access full, limited, denied, restricted, or changed since the last run? |
| Data | Is the requested representation local, degraded, edited, original, or still downloading? |
| Identity | Is the local/cloud identifier valid for the product’s scope and still present? |
| AI | Are orientation, content type, model contract, provenance, retention, and review state attached? |
| Edit | Does the user understand the exact Photos mutation and can the app reconstruct or undo it? |
| Accessibility | Can selection, review, save, and discard be completed without image-only cues? |
| Physical device | Have iCloud retrieval, limited access, large assets, memory, thermal, and VoiceOver behavior been exercised? |
| Release | Are privacy strings, target membership, Photos entitlement/configuration, resources, and signed behavior verified? |

## Sources

- [PhotosUI](https://developer.apple.com/documentation/photosui)
- [PhotosPicker](https://developer.apple.com/documentation/photosui/photospicker)
- [PhotosPickerItem](https://developer.apple.com/documentation/photosui/photospickeritem)
- [Bringing Photos picker to your SwiftUI app](https://developer.apple.com/documentation/PhotoKit/bringing-photos-picker-to-your-swiftui-app)
- [PhotoKit](https://developer.apple.com/documentation/photokit)
- [PHPhotoLibrary](https://developer.apple.com/documentation/photos/phphotolibrary)
- [PHAccessLevel](https://developer.apple.com/documentation/photos/phaccesslevel)
- [PHAuthorizationStatus](https://developer.apple.com/documentation/photos/phauthorizationstatus)
- [PHAsset](https://developer.apple.com/documentation/photos/phasset)
- [Fetching Assets](https://developer.apple.com/documentation/photokit/fetching-assets)
- [PHImageManager](https://developer.apple.com/documentation/photos/phimagemanager)
- [PHImageRequestOptions](https://developer.apple.com/documentation/photos/phimagerequestoptions)
- [PHAssetResourceManager](https://developer.apple.com/documentation/photos/phassetresourcemanager)
- [PHAssetResourceRequestOptions](https://developer.apple.com/documentation/photos/phassetresourcerequestoptions)
- [PHContentEditingInputRequestOptions](https://developer.apple.com/documentation/photos/phcontenteditinginputrequestoptions)
- [Editing Asset Content](https://developer.apple.com/documentation/photokit/editing-asset-content)
- [PHContentEditingInput](https://developer.apple.com/documentation/photos/phcontenteditinginput)
- [PHContentEditingOutput](https://developer.apple.com/documentation/photos/phcontenteditingoutput)
- [PHAdjustmentData](https://developer.apple.com/documentation/photos/phadjustmentdata)
- [Observing Changes in the Photo Library](https://developer.apple.com/documentation/photokit/observing-changes-in-the-photo-library)
- [PHPhotoLibraryChangeObserver](https://developer.apple.com/documentation/photos/phphotolibrarychangeobserver)
- [PHFetchResultChangeDetails](https://developer.apple.com/documentation/photos/phfetchresultchangedetails)
- [Core Transferable](https://developer.apple.com/documentation/CoreTransferable)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [DataRepresentation](https://developer.apple.com/documentation/coretransferable/datarepresentation)
- [FileRepresentation](https://developer.apple.com/documentation/coretransferable/filerepresentation)
- [ProxyRepresentation](https://developer.apple.com/documentation/coretransferable/proxyrepresentation)
- [Uniform Type Identifiers](https://developer.apple.com/documentation/uniformtypeidentifiers)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
