# PhotosUI, PhotoKit, Transferable, and on-device AI recipes

These are compile-oriented route sketches, not verified app code. Confirm the selected iOS 26 SDK signatures, availability, Info.plist usage descriptions, authorization scope, transfer content types, model contract, target membership, and physical-device behavior before copying them.

Shared route:

`user-selected item -> representation -> app-owned source -> model/editor -> review -> app/Photos destination`

## Recipe 1: a narrow SwiftUI PhotosPicker

Use the system picker for a one-off selection whenever possible.

```swift
import PhotosUI
import SwiftUI

struct PhotoInputButton: View {
    @Binding var selection: PhotosPickerItem?

    var body: some View {
        PhotosPicker(
            selection: $selection,
            matching: .images,
            preferredItemEncoding: .automatic
        ) {
            Label("Choose photo", systemImage: "photo")
        }
    }
}
```

The selection is a placeholder. Load a `Transferable` representation after the user chooses an item. Do not treat `selection` as image bytes or as full PhotoKit authorization.

## Recipe 2: bounded multi-selection and supersession

Keep a generation token so a late load cannot publish into a newer selection.

```swift
@MainActor
final class PhotoSelectionModel: ObservableObject {
    @Published var selection: [PhotosPickerItem] = []
    @Published private(set) var state: State = .empty

    enum State { case empty, loading, ready, failed }
    private var generation = 0

    func selectionChanged() {
        generation += 1
        let current = generation
        let selectedItems = selection
        state = selection.isEmpty ? .empty : .loading

        Task { [weak self] in
            do {
                let items = try await loadItems(selectedItems)
                guard !Task.isCancelled else { return }
                guard let self, current == self.generation else { return }
                self.state = items.isEmpty ? .empty : .ready
            } catch {
                guard let self, current == self.generation else { return }
                self.state = .failed
            }
        }
    }
}
```

The example omits the app-owned loaded-item storage and uses a route-sketch `loadItems` function. Add bounded concurrency, progress, cancellation, and file cleanup for real multi-selection.

## Recipe 3: a custom image Transferable

Apple’s default `Image` transfer route has format limitations. Use a custom model when the app needs a declared image content type.

```swift
import SwiftUI
import UniformTypeIdentifiers

struct ImportedImage: Transferable, Sendable {
    let data: Data
    let contentType: UTType

    static var transferRepresentation: some TransferRepresentation {
        DataRepresentation(importedContentType: .image) { data in
            guard !data.isEmpty else { throw CocoaError(.fileReadCorruptFile) }
            return ImportedImage(data: data, contentType: .image)
        }
    }
}

func loadImage(_ item: PhotosPickerItem) async throws -> ImportedImage {
    guard let value = try await item.loadTransferable(type: ImportedImage.self) else {
        throw CocoaError(.fileReadNoSuchFile)
    }
    return value
}
```

The exact `Transferable` representation and content-type negotiation should be tested against HEIF/JPEG/PNG and the target SDK. Decode or copy the data off the main actor, and do not retain it beyond the declared source policy.

## Recipe 4: file-backed transfer for large assets

Use `FileRepresentation` for large media or a model pipeline that already consumes files.

```swift
struct ImportedPhotoFile: Transferable, Sendable {
    let file: URL

    static var transferRepresentation: some TransferRepresentation {
        FileRepresentation(importedContentType: .image) { received in
            let destination = FileManager.default.temporaryDirectory
                .appendingPathComponent(UUID().uuidString)
                .appendingPathExtension("image")
            try FileManager.default.copyItem(
                at: received.file,
                to: destination
            )
            return ImportedPhotoFile(file: destination)
        }
    }
}
```

Copy a received file into a lifecycle you own if processing continues after the transfer. Use a specific content type and delete the copy when the source, model run, and review policy no longer need it. A temporary URL is not a durable source record.

## Recipe 5: PhotoKit authorization state

Request the narrowest access level for the actual feature.

```swift
import Photos

func requestPhotoAccess(
    level: PHAccessLevel,
    completion: @escaping (PHAuthorizationStatus) -> Void
) {
    let current = PHPhotoLibrary.authorizationStatus(for: level)
    switch current {
    case .notDetermined:
        PHPhotoLibrary.requestAuthorization(for: level, handler: completion)
    default:
        completion(current)
    }
}
```

Handle `.limited`, `.denied`, and `.restricted` distinctly. A picker-only route may not need this call. The app’s usage descriptions and UI explanation must match the chosen access level.

## Recipe 6: fetch an asset by a device-local identifier

Use a local identifier only within the scope in which it is valid.

```swift
func fetchAsset(localIdentifier: String) -> PHAsset? {
    let result = PHAsset.fetchAssets(
        withLocalIdentifiers: [localIdentifier],
        options: nil
    )
    return result.firstObject
}
```

An empty result can mean deletion, limited access, a different device, or an identifier that was never valid. Keep the source record stale until the app resolves the reason appropriate to the product.

## Recipe 7: request a display image and handle degraded delivery

Use `PHImageManager` for thumbnails or display-sized images.

```swift
func requestThumbnail(
    for asset: PHAsset,
    targetSize: CGSize,
    result: @escaping (UIImage?, Bool) -> Void
) -> PHImageRequestID {
    let options = PHImageRequestOptions()
    options.deliveryMode = .opportunistic
    options.isNetworkAccessAllowed = true

    return PHImageManager.default().requestImage(
        for: asset,
        targetSize: targetSize,
        contentMode: .aspectFill,
        options: options
    ) { image, info in
        let degraded = (info?[PHImageResultIsDegradedKey] as? Bool) ?? false
        result(image, degraded)
    }
}
```

The result handler may receive a degraded image before a final one. Update UI state on the main actor, associate the request with the source/generation, and cancel with `cancelImageRequest(_:)` when the cell or source is replaced.

## Recipe 8: request full image data with orientation

Use this route when a model or export needs the largest represented image data.

```swift
func requestImageData(
    for asset: PHAsset,
    completion: @escaping (Result<(Data, CGImagePropertyOrientation), Error>) -> Void
) -> PHImageRequestID {
    let options = PHImageRequestOptions()
    options.version = .current
    options.isNetworkAccessAllowed = true
    options.progressHandler = { progress, error, stop, _ in
        // PHAssetImageProgressHandler runs on an arbitrary serial queue.
        // Publish progress on the main actor in a real adapter; do not finish
        // the request from this callback because the result handler owns the
        // terminal success/failure transition.
        if error != nil { stop.pointee = true }
        _ = progress
    }

    return PHImageManager.default().requestImageDataAndOrientation(
        for: asset,
        options: options
    ) { data, _, orientation, info in
        if let error = info?[PHImageErrorKey] as? Error {
            completion(.failure(error))
        } else if let data {
            completion(.success((data, orientation)))
        } else {
            completion(.failure(CocoaError(.fileReadNoSuchFile)))
        }
    }
}
```

This is a route sketch. `PHAssetImageProgressHandler` receives progress, an optional error, a mutable stop flag, and an info dictionary; its callback is not the main actor. Preserve whether `.current` or `.original` was requested because it changes the meaning of the model input, and verify error/result-key handling in the target SDK.

## Recipe 9: write an underlying resource to a file

Use `PHAssetResourceManager` for a resource that must be streamed or written to disk.

```swift
func writeResource(
    _ resource: PHAssetResource,
    to destination: URL
) async throws {
    let options = PHAssetResourceRequestOptions()
    options.isNetworkAccessAllowed = true
    try await PHAssetResourceManager.default().writeData(
        for: resource,
        toFile: destination,
        options: options
    )
}
```

Keep the destination in an app-owned temporary or working directory, validate content type/size before model input, and delete it according to the feature’s retention policy. A resource may require network access and can fail or be cancelled.

## Recipe 10: observe changes to a fetch result

Keep the observer strongly referenced and update projections from change details.

```swift
final class PhotoLibraryObserver: NSObject, PHPhotoLibraryChangeObserver {
    private(set) var assets: PHFetchResult<PHAsset>?

    func photoLibraryDidChange(_ changeInstance: PHChange) {
        guard let assets else { return }
        guard let details = changeInstance.changeDetails(for: assets) else { return }
        self.assets = details.fetchResultAfterChanges
        // Invalidate model proposals for removed or modified identifiers.
    }
}

let observer = PhotoLibraryObserver()
PHPhotoLibrary.shared().register(observer)
```

The observer lifecycle, queue handoff, and fetch-result ownership need a production design. Unregister it when the feature no longer needs updates. Do not assume it receives events while the process is terminated.

## Recipe 11: prepare a non-destructive edit

Request editing input before the user confirms a Photos mutation.

```swift
func requestEditingInput(
    for asset: PHAsset,
    completion: @escaping (PHContentEditingInput?, Error?) -> Void
) -> PHContentEditingInputRequestID {
    let options = PHContentEditingInputRequestOptions()
    options.isNetworkAccessAllowed = true
    options.canHandleAdjustmentData = { adjustmentData in
        adjustmentData.formatIdentifier == "com.example.photo-edit"
    }

    return asset.requestContentEditingInput(
        with: options
    ) { input, info in
        let error = info[PHContentEditingInputErrorKey] as? Error
        completion(input, error)
    }
}
```

Use your own reverse-DNS adjustment identifier and version in a real app. Create `PHContentEditingOutput` and `PHAdjustmentData` only after the edit is prepared. If the app cannot handle prior adjustment data, Photos may provide rendered current content instead of the original.

## Recipe 12: user-approved Photos change

Keep a Photos write as a separate domain command.

```swift
func saveToPhotos(
    output: PHContentEditingOutput,
    asset: PHAsset
) async throws {
    try await PHPhotoLibrary.shared().performChanges {
        let request = PHAssetChangeRequest(for: asset)
        request.contentEditingOutput = output
    }
}
```

This route requires the appropriate authorization and an explicit user decision. Prepare output before entering the change block, keep the block small, and reconcile the app’s projection after completion. Saving a generated image as a new asset uses a creation request and should be designed separately from editing an existing asset.

## Recipe 13: source-linked on-device AI proposal

Keep the model adapter independent of Photos UI.

```swift
struct PhotoProposal: Sendable, Equatable {
    let sourceID: String
    let sourceModifiedAt: Date?
    let modelID: String
    let modelVersion: String
    let suggestion: String
    let requiresReview: Bool
}

func proposal(
    sourceID: String,
    modifiedAt: Date?,
    modelID: String,
    modelVersion: String,
    suggestion: String
) -> PhotoProposal {
    PhotoProposal(
        sourceID: sourceID,
        sourceModifiedAt: modifiedAt,
        modelID: modelID,
        modelVersion: modelVersion,
        suggestion: suggestion,
        requiresReview: true
    )
}
```

Before accepting, refetch/validate the source, compare modification dates or generation IDs, validate the output, and require explicit confirmation for app persistence, export, or Photos mutation.

## Recipe 14: Transferable export with a faithful type and fallback

Use a preferred structured representation plus a lightweight fallback.

```swift
struct ReviewedCaption: Codable, Transferable, Sendable {
    let caption: String

    static var transferRepresentation: some TransferRepresentation {
        CodableRepresentation(contentType: .json)
        ProxyRepresentation(exporting: \.caption)
    }
}
```

The actual exported `UTType` and privacy policy should match the receiving workflow. Do not put a raw photo or private EXIF into a fallback representation just because text is convenient.

## Recipe 15: deterministic preview and proof fixture

Inject adapters so UI previews never need a real photo library.

```swift
protocol PhotoSourceLoading: Sendable {
    associatedtype Source: Sendable
    func load() async throws -> Source
}

struct StubPhotoSource: PhotoSourceLoading {
    let value: Data

    func load() async throws -> Data { value }
}
```

Use real `PhotosPicker`, PhotoKit, iCloud, model, and Photos mutation tests separately. A stub proves state rendering and review logic; it does not prove authorization, asset availability, resource delivery, model quality, or a saved Photos result.

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
- [PHImageManager](https://developer.apple.com/documentation/photos/phimagemanager)
- [PHImageRequestOptions](https://developer.apple.com/documentation/photos/phimagerequestoptions)
- [PHAssetImageProgressHandler](https://developer.apple.com/documentation/photos/phassetimageprogresshandler)
- [PHAssetResourceManager](https://developer.apple.com/documentation/photos/phassetresourcemanager)
- [PHAssetResourceRequestOptions](https://developer.apple.com/documentation/photos/phassetresourcerequestoptions)
- [PHContentEditingInput](https://developer.apple.com/documentation/photos/phcontenteditinginput)
- [PHContentEditingInputRequestOptions](https://developer.apple.com/documentation/photos/phcontenteditinginputrequestoptions)
- [PHContentEditingOutput](https://developer.apple.com/documentation/photos/phcontenteditingoutput)
- [PHAdjustmentData](https://developer.apple.com/documentation/photos/phadjustmentdata)
- [PHAssetChangeRequest](https://developer.apple.com/documentation/photos/phassetchangerequest)
- [PHPhotoLibraryChangeObserver](https://developer.apple.com/documentation/photos/phphotolibrarychangeobserver)
- [Core Transferable](https://developer.apple.com/documentation/CoreTransferable)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [DataRepresentation](https://developer.apple.com/documentation/coretransferable/datarepresentation)
- [FileRepresentation](https://developer.apple.com/documentation/coretransferable/filerepresentation)
- [ProxyRepresentation](https://developer.apple.com/documentation/coretransferable/proxyrepresentation)
- [Uniform Type Identifiers](https://developer.apple.com/documentation/uniformtypeidentifiers)
- [Vision](https://developer.apple.com/documentation/vision)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
