# Photos source, transfer, editing, and on-device AI capability route

## Use this route when

Choose this route when an app needs user-selected or library-backed photos/videos as input to a native workflow, local model, editor, export, or system handoff. Start with the picker when the product needs only selected assets. Add PhotoKit authorization and observers only when the product truly manages a library projection or writes changes.

Core route:

`user selection -> transfer/resource adapter -> normalized source -> optional local model -> review -> app record/export/Photos change`

## Route decision table

| Need | First route | Add when needed |
| --- | --- | --- |
| One-off image input | `PhotosPicker` with a narrow `PHPickerFilter` | Custom `Transferable` for non-PNG/large image handling. |
| Multiple model inputs | Bounded `PhotosPicker` selection and file-backed transfer | Task-group concurrency/backpressure, model input normalization, source manifests. |
| Album/library browser | PhotoKit fetches and `PHCachingImageManager` | Read authorization, limited-library handling, change observer, incremental updates. |
| Full/original/current bytes | `PHImageManager` or `PHAssetResourceManager` | iCloud network policy, progress, cancellation, temporary-file cleanup. |
| Save a generated result | User review plus `PHPhotoLibrary.performChanges` | Add-only authorization, duplicate/metadata policy, reconciliation. |
| Non-destructive edit | `PHContentEditingInput`/`Output`, `PHAdjustmentData`, `PHAssetChangeRequest` | Adjustment compatibility, before/after UI, revert/reset route. |
| Local AI suggestion | Selected source -> Vision/Core ML/Foundation Models adapter | Model readiness, privacy redaction, proposal validation, accessible review. |

## Capability slices

### 1. Source scope

Choose one source scope per feature:

```swift
enum PhotoSourceScope: Sendable {
    case pickerSelection
    case limitedLibrary
    case authorizedLibrary
}
```

The enum is app policy. Do not infer `authorizedLibrary` from the presence of a `PHAsset`; check `PHPhotoLibrary.authorizationStatus(for:)` and handle asset-level failures.

### 2. Transfer contract

Normalize a picker item only after loading the requested representation:

```text
PhotosPickerItem placeholder
  -> supported content types
  -> loadTransferable / file representation
  -> imported data/file
  -> orientation/type/size validation
  -> app-owned SourceAsset
```

Use `FileRepresentation` for large or multi-item media. Copy a received temporary file to an app-owned directory if the next phase outlives the transfer callback, then delete it according to the retention policy.

### 3. Asset manifest

```swift
struct SourceAsset: Codable, Sendable, Equatable {
    let id: UUID
    let kind: Kind
    let contentType: String
    let photoLocalIdentifier: String?
    let cloudIdentifier: String?
    let importedAt: Date
    let modifiedAt: Date?
    let localFileName: String?
    let userSelected: Bool

    enum Kind: String, Codable, Sendable {
        case image
        case video
        case livePhoto
    }
}
```

This is a domain boundary, not a complete Photos schema. Keep the photo identifier, file copy, model output, and user record separate so the user can delete one without silently deleting the others.

### 4. Full-resolution/model adapter

Choose the smallest representation that matches the model:

```text
thumbnail -> fast browse/index
current rendered image -> user-facing current-content analysis
original/resource bytes -> export, OCR/fine detail, or a documented model need
live-photo/video resource -> time-based or motion-aware feature
```

Always preserve orientation and content type. If the asset is in iCloud, make network access and progress visible. If a user changes the selection, cancel or supersede the previous request.

### 5. On-device AI proposal

```text
SourceAsset + representation metadata
  -> preprocessing contract
  -> Vision/Core ML/Foundation Models
  -> typed observation
  -> proposal with source/model version
  -> edit/accept/reject
```

The proposal should not contain unknown source IDs, silently invented EXIF facts, or side effects. If the output suggests tags, captions, crops, or edits, validate the output against the actual source and let the person edit it before saving.

### 6. Photos mutation route

Separate preparation from mutation:

```text
prepare generated resource / adjustment data
  -> show exact before/after and destination
  -> user confirms
  -> one smallest performChanges block
  -> reconcile through change observer
  -> report applied/failed/stale state
```

Do not perform library writes from a model callback without a user-facing command. Combine changes only when the user sees them as one operation. Keep a local app record of the request ID/model/source version for audit and reconciliation.

## SwiftUI composition

Expose state such as:

- picker visibility and selection generation;
- transfer progress/cancellation/error;
- source representation and retention;
- Photos authorization/limited scope;
- model readiness and proposal state;
- review decision and target destination;
- Photos change result and reconciliation state.

The SwiftUI view renders these states and sends intents. A Photos adapter owns `PHImageManager`, `PHAssetResourceManager`, `PHPhotoLibrary`, observers, and cancellation IDs. A model adapter owns preprocessing and inference. Neither should be hidden inside a button action.

## Fallbacks

- Picker-only flow when full-library permission is denied.
- Preview-size analysis when the original is unavailable.
- Manual caption/tag entry when the local model is unavailable.
- Keep the generated result in the app when Photos write authorization is unavailable.
- “Try again on Wi-Fi” when an iCloud resource cannot be retrieved.
- Stale-source warning when a Photos change observer reports deletion/modification.

Never show a previous photo’s model result as the current selection without a source ID and stale state.

## Proof route

### Deterministic

- selection supersession and nil/error handling;
- custom `Transferable` import for supported content types;
- file copy/delete and retention policy;
- source manifest and local/cloud identifier mapping;
- model preprocessing/orientation/threshold rules;
- proposal validation/edit/accept/reject;
- Photos change-result mapping and stale-source invalidation.

### UI/preview

- picker idle/selected/loading/progress/failure;
- limited/denied/restricted/authorized scope;
- model unavailable/ready/processing/suggestion/stale;
- before/after edit and app-save versus Photos-save actions;
- Dynamic Type, VoiceOver, reduced effects, high contrast, and RTL.

### Device/release

Use a physical device for iCloud retrieval, limited-library changes, large assets, original/current resource differences, Photos mutations, memory/thermal behavior, assistive technology, and actual model execution. Inspect a signed artifact for privacy strings, target membership, resource inclusion, and the intended Photos/extension configuration. A simulator fixture or picker screenshot is not proof of the full library route.

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
- [PHFetchOptions](https://developer.apple.com/documentation/photos/phfetchoptions)
- [PHImageManager](https://developer.apple.com/documentation/photos/phimagemanager)
- [PHCachingImageManager](https://developer.apple.com/documentation/photos/phcachingimagemanager)
- [PHAssetResourceManager](https://developer.apple.com/documentation/photos/phassetresourcemanager)
- [PHContentEditingInputRequestOptions](https://developer.apple.com/documentation/photos/phcontenteditinginputrequestoptions)
- [PHContentEditingOutput](https://developer.apple.com/documentation/photos/phcontenteditingoutput)
- [PHAdjustmentData](https://developer.apple.com/documentation/photos/phadjustmentdata)
- [PHPhotoLibraryChangeObserver](https://developer.apple.com/documentation/photos/phphotolibrarychangeobserver)
- [Core Transferable](https://developer.apple.com/documentation/CoreTransferable)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [DataRepresentation](https://developer.apple.com/documentation/coretransferable/datarepresentation)
- [FileRepresentation](https://developer.apple.com/documentation/coretransferable/filerepresentation)
- [Vision](https://developer.apple.com/documentation/vision)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
