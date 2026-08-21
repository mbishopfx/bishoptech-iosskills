# SwiftUI media capture and review recipes

## Recipe rules

These snippets are route starters for a named app target. They are not compiled
in this documentation workspace and do not prove PhotosPicker transfer,
camera authorization, capture-session behavior, AVKit playback, metadata
redaction, model readiness, Photos mutations, accessibility, or physical
device behavior.

Before copying a recipe:

1. Confirm the selected iOS 26 SDK signature, import, and availability.
2. Name the source identity, canonical representation, source revision, and
   app-owned file lifetime.
3. Keep transfer, permission, capture, preview, observation, review, and
   destination state separate.
4. Add cancellation and a generation/revision check to every async path.
5. Validate file type, size, orientation, metadata, model input, and output
   before showing an Apply or Save action.
6. Test picker, camera, playback, AI, accessibility, reduced effects,
   localization, performance, archive, and physical-device boundaries.

Tilde fences keep the examples copyable inside this Markdown page.

## 1. PhotosPicker selection with generation-safe loading

Use PhotosPicker for choosing existing media. Treat each selected item as a
placeholder until the requested Transferable representation has loaded.

~~~swift
import PhotosUI
import SwiftUI
import UniformTypeIdentifiers

@MainActor
final class PhotoImportModel: ObservableObject {
    enum State: Equatable {
        case idle
        case loading(generation: Int)
        case ready(ImportedMedia)
        case failed(String)
    }

    @Published private(set) var state: State = .idle

    private var generation = 0
    private var task: Task<Void, Never>?

    func select(_ item: PhotosPickerItem?) {
        generation += 1
        let current = generation
        task?.cancel()

        guard let item else {
            state = .idle
            return
        }

        state = .loading(generation: current)
        task = Task { [weak self] in
            do {
                let imported = try await item.loadTransferable(
                    type: ImportedMedia.self
                )
                try Task.checkCancellation()
                guard let self, self.generation == current else { return }
                state = imported.map(State.ready)
                    ?? .failed("The selected item has no supported file.")
            } catch is CancellationError {
                // A later selection owns the state.
            } catch {
                guard let self, self.generation == current else { return }
                state = .failed("The media could not be loaded.")
            }
        }
    }

    deinit {
        task?.cancel()
    }
}

struct PhotoImportView: View {
    @StateObject private var model = PhotoImportModel()
    @State private var selection: PhotosPickerItem?

    var body: some View {
        VStack {
            PhotosPicker(
                "Choose media",
                selection: $selection,
                matching: .any(of: [.images, .videos])
            )

            switch model.state {
            case .idle:
                Text("No media selected.")
            case .loading:
                ProgressView("Preparing media")
            case .ready(let media):
                Text(media.displayName)
            case .failed(let message):
                ContentUnavailableView(
                    "Media unavailable",
                    systemImage: "photo.badge.exclamationmark",
                    description: Text(message)
                )
            }
        }
        .onChange(of: selection) { _, item in
            model.select(item)
        }
    }
}
~~~

For multi-selection, store item IDs and order explicitly. Never use task
completion order as the visual order. Add an app-owned copy before relying on
a temporary representation after the picker task ends.

## 2. A file-backed Transferable media value

Use a file representation when large media should not be decoded into memory
just to cross the picker boundary. The production version should copy into a
controlled app directory, validate the type and size, and clean up derived
files.

~~~swift
import CoreTransferable
import Foundation
import UniformTypeIdentifiers

struct ImportedMedia: Transferable, Sendable, Equatable {
    let fileURL: URL
    let contentType: UTType
    let byteCount: Int64
    let displayName: String

    static var transferRepresentation: some TransferRepresentation {
        FileRepresentation(contentType: .item) { media in
            SentTransferredFile(media.fileURL)
        } importing: { received in
            let destination = FileManager.default.temporaryDirectory
                .appending(path: UUID().uuidString)
                .appendingPathExtension(
                    received.file.pathExtension.isEmpty
                        ? "item"
                        : received.file.pathExtension
                )

            try FileManager.default.copyItem(
                at: received.file,
                to: destination
            )

            let attributes = try FileManager.default.attributesOfItem(
                atPath: destination.path
            )
            let byteCount = (attributes[.size] as? NSNumber)?
                .int64Value ?? 0

            return ImportedMedia(
                fileURL: destination,
                contentType: .item,
                byteCount: byteCount,
                displayName: received.file.lastPathComponent
            )
        }
    }
}
~~~

The representation should not pretend that the generic item type is a fully
validated image or movie. Inspect the file with the appropriate framework
before choosing a review surface or export type.

## 3. Permission state for a camera entry

Keep permission state separate from session state. A camera session can be
configured only after authorization and device discovery succeed.

~~~swift
import AVFoundation

enum CameraPermission: Equatable, Sendable {
    case notDetermined
    case authorized
    case denied
    case restricted
}

@MainActor
final class CameraPermissionModel: ObservableObject {
    @Published private(set) var state: CameraPermission = .notDetermined

    func refresh() {
        state = map(
            AVCaptureDevice.authorizationStatus(for: .video)
        )
    }

    func request() async {
        let granted = await AVCaptureDevice.requestAccess(for: .video)
        state = granted ? .authorized : .denied
    }

    private func map(
        _ status: AVAuthorizationStatus
    ) -> CameraPermission {
        switch status {
        case .notDetermined:
            return .notDetermined
        case .authorized:
            return .authorized
        case .denied:
            return .denied
        case .restricted:
            return .restricted
        @unknown default:
            return .denied
        }
    }
}
~~~

Request microphone access separately when the feature records audio. Include
the correct camera/microphone usage descriptions in the target's processed
Info.plist. Test first launch, denial, restriction, and a Settings change.

## 4. Session-owned camera controller

The session owner should outlive SwiftUI view recomputation. This sketch shows
the ownership boundary; a production implementation should use the session
queue recommended by AVFoundation, observe interruptions/runtime errors, and
publish results through a typed delegate or continuation.

~~~swift
import AVFoundation

enum CameraError: Error {
    case notAuthorized
    case unavailable
    case cannotAddInput
    case cannotAddOutput
}

final class CameraSessionController: NSObject, @unchecked Sendable {
    let session = AVCaptureSession()
    let photoOutput = AVCapturePhotoOutput()

    private let queue = DispatchQueue(
        label: "com.example.camera-session"
    )
    private var configured = false

    func configure(completion: @escaping (Result<Void, Error>) -> Void) {
        queue.async {
            guard AVCaptureDevice.authorizationStatus(for: .video)
                    == .authorized
            else {
                completion(.failure(CameraError.notAuthorized))
                return
            }

            do {
                guard let device = AVCaptureDevice.default(
                    .builtInWideAngleCamera,
                    for: .video,
                    position: .back
                ) else {
                    throw CameraError.unavailable
                }

                let input = try AVCaptureDeviceInput(device: device)
                self.session.beginConfiguration()
                defer { self.session.commitConfiguration() }

                guard self.session.canAddInput(input) else {
                    throw CameraError.cannotAddInput
                }
                guard self.session.canAddOutput(self.photoOutput) else {
                    throw CameraError.cannotAddOutput
                }

                self.session.addInput(input)
                self.session.addOutput(self.photoOutput)
                self.configured = true
                completion(.success(()))
            } catch {
                completion(.failure(error))
            }
        }
    }

    func start() {
        queue.async {
            guard self.configured, !self.session.isRunning else { return }
            self.session.startRunning()
        }
    }

    func stop() {
        queue.async {
            guard self.session.isRunning else { return }
            self.session.stopRunning()
        }
    }
}
~~~

Do not call configure from a SwiftUI body. Add a single service instance at a
feature boundary and make its teardown explicit when the camera route closes.

## 5. SwiftUI preview-layer bridge

The service owns the session; the bridge owns only the presentation layer.
Verify orientation, mirroring, aspect fill, safe areas, and session replacement
on a real device.

~~~swift
import AVFoundation
import SwiftUI

struct CameraPreview: UIViewRepresentable {
    let session: AVCaptureSession

    func makeUIView(context: Context) -> PreviewView {
        let view = PreviewView()
        view.previewLayer.session = session
        view.previewLayer.videoGravity = .resizeAspectFill
        return view
    }

    func updateUIView(_ view: PreviewView, context: Context) {
        guard view.previewLayer.session !== session else { return }
        view.previewLayer.session = session
    }
}

final class PreviewView: UIView {
    override class var layerClass: AnyClass {
        AVCaptureVideoPreviewLayer.self
    }

    var previewLayer: AVCaptureVideoPreviewLayer {
        guard let layer = layer as? AVCaptureVideoPreviewLayer else {
            fatalError("PreviewView must use AVCaptureVideoPreviewLayer")
        }
        return layer
    }
}
~~~

For a production bridge, use a coordinator or a session adapter when the
preview connection needs orientation/mirroring updates. Do not put capture
delegates, Photos saves, or model inference in the view wrapper.

## 6. Photo capture request and result boundary

A capture button should create a capture ID. The delegate result should finish
exactly that request or report an error for it.

~~~swift
struct PhotoCaptureRequest: Sendable, Equatable {
    let captureID: UUID
    let sourceRevision: Int
}

struct PhotoCaptureResult: Sendable, Equatable {
    let captureID: UUID
    let sourceRevision: Int
    let fileURL: URL
    let contentTypeIdentifier: String
}

final class PhotoCaptureCoordinator: NSObject,
    AVCapturePhotoCaptureDelegate {

    private var continuations:
        [Int64: CheckedContinuation<PhotoCaptureResult, Error>] = [:]

    func capture(
        output: AVCapturePhotoOutput,
        request: PhotoCaptureRequest
    ) async throws -> PhotoCaptureResult {
        let settings = AVCapturePhotoSettings()

        return try await withCheckedThrowingContinuation { continuation in
            // The production implementation should associate the delegate's
            // unique capture identifier with this continuation and remove it
            // on every success and failure path.
            continuations[settings.uniqueID] = continuation
            output.capturePhoto(
                with: settings,
                delegate: self
            )
        }
    }

    func photoOutput(
        _ output: AVCapturePhotoOutput,
        didFinishProcessingPhoto photo: AVCapturePhoto,
        error: Error?
    ) {
        // Convert the photo to an app-owned file, validate its type/metadata,
        // then resume the matching continuation exactly once.
        _ = (output, photo, error)
    }
}
~~~

The exact photo-file conversion and delegate lifecycle are intentionally left
as a target-owned implementation seam. Test capture failure, cancellation,
duplicate callbacks, disk failure, orientation, and the transition to review.

## 7. Review a video with VideoPlayer

Keep the player in the review model so a row or sheet recreation does not
silently reset the review.

~~~swift
import AVKit
import SwiftUI

struct VideoReviewView: View {
    let player: AVPlayer
    let title: String
    let onRetake: () -> Void
    let onSave: () -> Void

    var body: some View {
        VStack(spacing: 16) {
            VideoPlayer(player: player)
                .accessibilityLabel(Text(title))
                .aspectRatio(16 / 9, contentMode: .fit)

            HStack {
                Button("Retake", action: onRetake)
                Spacer()
                Button("Save", action: onSave)
                    .buttonStyle(.borderedProminent)
            }
        }
        .padding()
        .onDisappear {
            player.pause()
        }
    }
}
~~~

Use AVPlayerViewController when its controller surface or platform behavior is
required. Distinguish player failure from a model-analysis failure. A video
that plays successfully has not necessarily passed metadata, export, or
observation validation.

## 8. Image I/O thumbnail and metadata inspection

Use Image I/O for source properties and bounded thumbnails. Keep the original
URL separate from the thumbnail output.

~~~swift
import CoreGraphics
import ImageIO

struct ImagePreviewData: Sendable {
    let thumbnail: CGImage
    let width: Int
    let height: Int
    let properties: [CFString: Any]
}

func makePreview(
    from url: URL,
    maxPixelSize: Int
) throws -> ImagePreviewData {
    guard
        let source = CGImageSourceCreateWithURL(
            url as CFURL,
            nil
        ),
        let properties = CGImageSourceCopyPropertiesAtIndex(
            source,
            0,
            nil
        ) as? [CFString: Any],
        let thumbnail = CGImageSourceCreateThumbnailAtIndex(
            source,
            0,
            [
                kCGImageSourceCreateThumbnailFromImageAlways: true,
                kCGImageSourceThumbnailMaxPixelSize: maxPixelSize,
                kCGImageSourceCreateThumbnailWithTransform: true
            ] as CFDictionary
        )
    else {
        throw ImageInspectionError.invalidImage
    }

    return ImagePreviewData(
        thumbnail: thumbnail,
        width: thumbnail.width,
        height: thumbnail.height,
        properties: properties
    )
}
~~~

Inspect the original properties before deciding what to display or export.
Do not treat the thumbnail's dimensions as the source dimensions. Use a
separate writer step to preserve or redact metadata intentionally.

## 9. Metadata-redacted image destination

The exact metadata dictionary depends on the format and product policy. This
route shows the important boundary: read the source, create a destination,
write the image with an explicit property dictionary, finalize, and inspect the
result.

~~~swift
import ImageIO
import UniformTypeIdentifiers

func writeRedactedImage(
    sourceURL: URL,
    destinationURL: URL,
    type: UTType
) throws {
    guard
        let source = CGImageSourceCreateWithURL(
            sourceURL as CFURL,
            nil
        ),
        let image = CGImageSourceCreateImageAtIndex(source, 0, nil),
        let destination = CGImageDestinationCreateWithURL(
            destinationURL as CFURL,
            type.identifier as CFString,
            1,
            nil
        )
    else {
        throw ImageExportError.cannotCreateDestination
    }

    let properties: [CFString: Any] = [
        kCGImagePropertyOrientation: 1
        // Add only the properties the product intentionally preserves.
        // Do not copy the source dictionary wholesale for a redacted export.
    ]

    CGImageDestinationAddImage(
        destination,
        image,
        properties as CFDictionary
    )

    guard CGImageDestinationFinalize(destination) else {
        throw ImageExportError.finalizeFailed
    }
}
~~~

Validate the output after writing. A redaction promise needs an inspection test
for GPS/device/time keys and a fixture for each supported output format.

## 10. Vision text observation from an image

Keep the request input and result source revision together. The exact Vision
API spelling and request handler initializer should be checked against the
selected SDK.

~~~swift
import Vision

struct TextObservationResult: Sendable, Equatable {
    let sourceRevision: Int
    let text: String
    let confidence: Double?
}

func recognizeText(
    imageData: Data,
    sourceRevision: Int
) async throws -> TextObservationResult {
    let request = RecognizeTextRequest()
    let observations = try await request.perform(
        on: imageData
    )

    let text = observations
        .map { $0.transcript }
        .joined(separator: "\n")

    return TextObservationResult(
        sourceRevision: sourceRevision,
        text: text,
        confidence: nil
    )
}
~~~

This is a conceptual recipe because request execution and result property names
are SDK-sensitive. Use the request's supported input and result types from the
selected SDK. Test portrait orientation, crop transforms, no text, partial
text, language configuration, cancellation, and source revision changes.

## 11. Core ML observation adapter

Keep model loading and request execution behind an adapter. The SwiftUI route
should consume a typed observation, not a framework-specific object graph.

~~~swift
struct ClassificationObservation: Sendable, Equatable {
    let sourceRevision: Int
    let modelIdentifier: String
    let modelRevision: String
    let label: String
    let confidence: Double
}

protocol MediaObservationEngine: Sendable {
    func observe(
        source: MediaModelInput,
        sourceRevision: Int
    ) async throws -> [ClassificationObservation]
}

struct MediaModelInput: Sendable {
    let representation: String
    let byteCount: Int64?
    let orientation: String?
}
~~~

The implementation should decide whether to use Vision's Core ML request
adapter or direct Core ML APIs. Record the model identifier and revision,
validate input dimensions/pixel format/orientation, and expose unavailable,
loading, partial, failed, and stale states.

## 12. Foundation Models candidate after deterministic observations

Use Foundation Models only after deterministic observations are available and
bounded. Keep candidate generation separate from commit.

~~~swift
struct MediaReviewInput: Codable, Sendable {
    let sourceRevision: Int
    let observations: [String]
    let allowedActions: [String]
}

struct MediaReviewCandidate: Codable, Sendable, Equatable {
    let candidateID: UUID
    let sourceRevision: Int
    let summary: String
    let suggestedTags: [String]
    let modelDescription: String
}

enum CandidateState: Equatable {
    case unavailable
    case generating(sourceRevision: Int)
    case ready(MediaReviewCandidate)
    case stale(MediaReviewCandidate)
    case rejected
    case committed(MediaReviewCandidate)
    case failed(String)
}
~~~

The exact Foundation Models session, availability, guided-generation, and
schema APIs are target/SDK-sensitive. The adapter should produce the typed
candidate or an explicit failure. The UI must show source, observations,
candidate status, and Apply/Discard separately. Applying a candidate should
increment the ordinary document/media revision and use the normal save path.

## 13. Revision-safe review coordinator

The source revision is the simplest guard against a late analysis result being
applied to a different media state.

~~~swift
@MainActor
final class MediaReviewCoordinator: ObservableObject {
    @Published private(set) var candidate: CandidateState = .unavailable

    private(set) var sourceID: UUID?
    private(set) var sourceRevision = 0
    private var task: Task<Void, Never>?

    func begin(
        sourceID: UUID,
        revision: Int,
        engine: @Sendable @escaping () async throws
            -> MediaReviewCandidate
    ) {
        task?.cancel()
        self.sourceID = sourceID
        sourceRevision = revision
        candidate = .generating(sourceRevision: revision)

        task = Task { [weak self] in
            do {
                let result = try await engine()
                try Task.checkCancellation()
                guard
                    let self,
                    self.sourceID == sourceID,
                    self.sourceRevision == revision
                else { return }
                candidate = .ready(result)
            } catch is CancellationError {
                // The source or review route changed.
            } catch {
                guard let self, self.sourceID == sourceID else { return }
                candidate = .failed("Review could not be completed.")
            }
        }
    }

    func sourceDidChange(id: UUID, revision: Int) {
        sourceID = id
        sourceRevision = revision
        task?.cancel()
        task = nil
        candidate = .unavailable
    }

    func discard() {
        task?.cancel()
        task = nil
        candidate = .rejected
    }
}
~~~

For multiple observations or a rich media state machine, use a typed request
object carrying source ID, source revision, capture generation, representation,
model revision, and cancellation identity. Do not rely on a matching string or
the current selected index.

## 14. Liquid Glass review shell

The media is the anchor; Liquid Glass contains contextual controls and status.
Use system labels and an opaque/reduced-effects fallback in the real target.

~~~swift
struct MediaReviewShell<Media: View>: View {
    let media: Media
    let isAnalyzing: Bool
    let canSave: Bool
    let onAnalyze: () -> Void
    let onRetake: () -> Void
    let onSave: () -> Void

    var body: some View {
        ZStack(alignment: .bottom) {
            media
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .background(.black)
                .accessibilityAddTraits(.isImage)

            VStack(spacing: 12) {
                if isAnalyzing {
                    Label(
                        "Reviewing on device",
                        systemImage: "sparkles"
                    )
                    .accessibilityValue("In progress")
                }

                HStack {
                    Button("Retake", action: onRetake)
                    Spacer()
                    Button(
                        "Analyze",
                        systemImage: "wand.and.stars",
                        action: onAnalyze
                    )
                    .disabled(isAnalyzing)
                    Spacer()
                    Button("Save", action: onSave)
                        .disabled(!canSave)
                        .buttonStyle(.borderedProminent)
                }
            }
            .padding()
            .glassEffect()
        }
    }
}
~~~

The exact Liquid Glass modifier and availability must be checked in the
selected SDK. Do not let glass hide permission, recording, stale, or
destination state. Test reduced transparency, Dynamic Type, VoiceOver, narrow
width, light/dark source imagery, and keyboard/pointer input.

## 15. Explicit destination chooser

Make the destination visible before a destructive or externally visible
action.

~~~swift
enum MediaDestination: String, CaseIterable, Identifiable {
    case app
    case export
    case photos

    var id: String { rawValue }

    var title: String {
        switch self {
        case .app: "Save in this app"
        case .export: "Export or share"
        case .photos: "Save to Photos"
        }
    }
}

struct DestinationChooser: View {
    @Binding var destination: MediaDestination
    let onContinue: () -> Void

    var body: some View {
        Form {
            Picker("Destination", selection: $destination) {
                ForEach(MediaDestination.allCases) { value in
                    Text(value.title).tag(value)
                }
            }

            Button("Continue", action: onContinue)
        }
        .navigationTitle("Where should this go?")
    }
}
~~~

The destination action then calls an app file/document save, an export/share
route, or a PhotoKit authorization/change route. These are different proof
paths. Never report Photos success when only the app file was written.

## 16. PhotoKit add-only save boundary

The exact PhotoKit request and authorization APIs vary by target and SDK. Keep
the Photos mutation behind a small service and report its result to the review
state.

~~~swift
import Photos

enum PhotosSaveResult: Equatable {
    case saved
    case denied
    case failed(String)
}

func saveToPhotos(
    fileURL: URL
) async -> PhotosSaveResult {
    let status = PHPhotoLibrary.authorizationStatus(
        for: .addOnly
    )

    let authorized: Bool
    switch status {
    case .authorized, .limited:
        authorized = true
    case .notDetermined:
        authorized = await PHPhotoLibrary.requestAuthorization(
            for: .addOnly
        ) == .authorized
    default:
        authorized = false
    }

    guard authorized else { return .denied }

    do {
        try await PHPhotoLibrary.shared().performChanges {
            PHAssetChangeRequest.creationRequestForAssetFromImage(
                atFileURL: fileURL
            )
        }
        return .saved
    } catch {
        return .failed("Photos could not save this media.")
    }
}
~~~

This sketch is intentionally not a universal drop-in implementation. Verify
the selected SDK's async PhotoKit API, whether the asset is an image or video,
the target's usage description, and the add-only/limited behavior. Keep the
original app-owned source when the Photos operation fails.

## 17. Acceptance fixture for the whole route

Use one fixture to prove the state machine without depending on a live camera.

~~~swift
struct MediaAcceptanceFixture: Equatable, Sendable {
    let sourceID: UUID
    let sourceRevision: Int
    let sourceKind: String
    let representation: String
    let transfer: String
    let permission: String
    let preview: String
    let metadataPolicy: String
    let observation: String
    let candidate: String
    let destination: String
}

let readyForReview = MediaAcceptanceFixture(
    sourceID: UUID(uuidString: "00000000-0000-0000-0000-000000000001")!,
    sourceRevision: 3,
    sourceKind: "imported-photo",
    representation: "app-owned-file",
    transfer: "complete",
    permission: "not-needed",
    preview: "oriented-thumbnail-and-original",
    metadataPolicy: "gps-redacted-export-only",
    observation: "vision-complete",
    candidate: "foundation-models-ready-for-review",
    destination: "choose-app-export-or-photos"
)
~~~

Acceptance should assert:

- a new source increments or replaces the source revision;
- an old transfer/model result cannot change the new source;
- preview and original representation remain distinct;
- metadata policy is applied only at the intended boundary;
- model output remains an observation or candidate until reviewed;
- Save in app, Export, and Save to Photos produce distinct results;
- denial, cancellation, interruption, and failure leave a recoverable state;
- all labels/actions remain useful with large text, VoiceOver, RTL, and reduced
  effects.

## Sources

- [PhotosPicker](https://developer.apple.com/documentation/photosui/photospicker)
- [PhotosPickerItem](https://developer.apple.com/documentation/photosui/photospickeritem)
- [Bringing the Photos picker to your SwiftUI app](https://developer.apple.com/documentation/PhotoKit/bringing-photos-picker-to-your-swiftui-app)
- [PhotoKit](https://developer.apple.com/documentation/photokit)
- [AVFoundation capture setup](https://developer.apple.com/documentation/avfoundation/capture-setup)
- [Setting up a capture session](https://developer.apple.com/documentation/avfoundation/setting-up-a-capture-session)
- [Requesting authorization to capture and save media](https://developer.apple.com/documentation/avfoundation/requesting-authorization-to-capture-and-save-media)
- [AVCaptureDevice](https://developer.apple.com/documentation/avfoundation/avcapturedevice)
- [AVCapturePhotoSettings](https://developer.apple.com/documentation/avfoundation/avcapturephotosettings)
- [AVCapturePhotoOutput](https://developer.apple.com/documentation/avfoundation/avcapturephotooutput)
- [AVCaptureVideoPreviewLayer](https://developer.apple.com/documentation/avfoundation/avcapturevideopreviewlayer)
- [AVCam: Building a camera app](https://developer.apple.com/documentation/avfoundation/avcam-building-a-camera-app)
- [AVKit](https://developer.apple.com/documentation/avkit)
- [VideoPlayer](https://developer.apple.com/documentation/avkit/videoplayer)
- [AVPlayerViewController](https://developer.apple.com/documentation/avkit/avplayerviewcontroller)
- [Image I/O](https://developer.apple.com/documentation/imageio)
- [CGImageSource](https://developer.apple.com/documentation/imageio/cgimagesource)
- [CGImageDestination](https://developer.apple.com/documentation/imageio/cgimagedestination)
- [Vision](https://developer.apple.com/documentation/vision)
- [RecognizeTextRequest](https://developer.apple.com/documentation/vision/recognizetextrequest)
- [CoreMLRequest](https://developer.apple.com/documentation/vision/coremlrequest)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adding intelligent app features with generative models](https://developer.apple.com/documentation/foundationmodels/adding-intelligent-app-features-with-generative-models)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Camera Control HIG](https://developer.apple.com/design/human-interface-guidelines/camera-control)
- [Live Photos HIG](https://developer.apple.com/design/human-interface-guidelines/live-photos)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
