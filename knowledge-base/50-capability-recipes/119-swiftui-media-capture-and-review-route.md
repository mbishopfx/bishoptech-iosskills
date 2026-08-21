# SwiftUI media capture and review capability route

## Use this route when

Choose this route when an app needs to move a photo or video from a user-owned
source into a reviewable SwiftUI surface:

- select one or more existing assets with PhotosPicker;
- import a transferable file representation and keep the original identity;
- own a custom camera or microphone capture session;
- show a live preview and a captured-photo or captured-video result;
- inspect orientation, dimensions, color, duration, and metadata;
- run bounded on-device Vision or Core ML observation;
- use Foundation Models to turn structured observations into a human-reviewable
  description, label, or organization proposal;
- review, edit, discard, save in the app, export, or explicitly save to Photos;
- adapt the capture/review shell to Liquid Glass, Dynamic Type, VoiceOver,
  keyboard, pointer, and the device family that actually supports the feature.

Use the [PhotosUI and PhotoKit route](../42-framework-deep-dives/67-photosui-photokit-source-and-editing.md)
when the central problem is library browsing, changes, limited-library access,
or photo-library editing. Use the [AVFoundation media pipeline](../42-framework-deep-dives/09-avfoundation-media-pipeline.md)
when the central problem is capture-session configuration, audio/video timing,
or export. This route is the SwiftUI seam that coordinates those capabilities.

## Route contract

Write these decisions down before implementing a view.

| Field | Required decision |
| --- | --- |
| User outcome | What can the person choose, capture, inspect, review, save, or export? |
| Entry | PhotosPicker, custom capture, system camera/share/import, or an existing URL |
| Source identity | Picker item, local file, asset identifier, capture identifier, or app document |
| Representation | Data, file URL, CGImage/CIImage, CVPixelBuffer, CMSampleBuffer, AVAsset, or a derived observation |
| Transfer | Which Transferable representation, UTType, size limit, cancellation, and failure copy? |
| Permission | Camera, microphone, photo-library read/add, limited access, denied/restricted, or not needed |
| Session owner | Which actor/service owns AVCaptureSession, inputs, outputs, queue, interruption, and teardown? |
| Preview | Which view owns the preview layer/player, and how is orientation/aspect-fit handled? |
| Capture | Photo, video, audio, Live Photo, depth, or another output; what is the result identity? |
| Metadata | Which properties are read, normalized, preserved, redacted, or never displayed? |
| Model | Vision/Core ML request, revision, region, model version, confidence policy, or no model |
| Generative review | Why is Foundation Models needed, what structured input is allowed, and what is never auto-committed? |
| Review | What does the person see, correct, accept, reject, or compare with the source? |
| Destination | App storage, export/share, Photos add-only, Photos change request, or discard |
| Revision | Which source revision, capture generation, and candidate revision make a result stale? |
| Lifecycle | What happens on background, interruption, route change, cancellation, memory pressure, and scene loss? |
| Visual shell | Which controls belong in a Liquid Glass group, and what is the opaque fallback? |
| Targets | iPhone, iPadOS, Mac Catalyst, visionOS, watchOS projection, or extension |
| Proof | Which claims require compile, fixture, preview, UI, simulator, physical, system, performance, or release evidence? |

## Route selection table

| Scenario | Primary route | Secondary route | First proof |
| --- | --- | --- | --- |
| Pick an existing photo | PhotosPicker + loadTransferable | PhotoKit asset access if identity is needed | Picker selection, transfer success/failure |
| Pick an existing video | PhotosPicker + file/URL representation | AVAsset review | Transfer type, duration, playback |
| Import a large asset | PhotosPicker + file representation | Security-scoped URL or app copy | Cancellation, disk space, file lifetime |
| Capture a photo | AVCaptureSession + AVCapturePhotoOutput | System camera/share route | Permission, session, delegate result |
| Capture a video | AVCaptureMovieFileOutput or data output | AVAssetWriter pipeline | Audio/video, interruption, final URL |
| Show a live camera | AVCaptureVideoPreviewLayer bridge | Target-specific camera surface | Preview orientation, safe area, teardown |
| Review a video | VideoPlayer | AVPlayerViewController | Playback lifetime, controls, background policy |
| Read metadata | Image I/O source properties | AVAsset metadata | Orientation, dimensions, privacy policy |
| Generate a thumbnail | CGImageSource thumbnail option | AVAsset image generator | Correct orientation and cost |
| OCR or classify | Vision request or Core ML request | Custom model pipeline | Input type, revision, result fixture |
| Explain structured observations | Foundation Models session | Deterministic local formatter | Prompt scope, candidate review, fallback |
| Save to the app | App-owned file/document store | SwiftData/CloudKit route | File/data round trip |
| Save to Photos | PhotoKit authorization/change request | Share/export if unavailable | Add/change result, limited access copy |

## 1. Give every source a stable identity

Do not let a PhotosPickerItem, temporary URL, CMSampleBuffer, or rendered
preview become the durable identity of the media. Create an app-owned identity
as soon as the source enters the feature.

~~~swift
enum MediaEntry: Sendable, Equatable {
    case picker(selectionID: UUID)
    case capture(captureID: UUID)
    case imported(fileID: UUID)
}

struct MediaSourceState: Sendable, Equatable {
    let entry: MediaEntry
    var sourceRevision: Int
    var displayName: String?
    var contentTypeIdentifier: String?
    var representation: RepresentationState
    var permission: PermissionState
    var transfer: TransferState
    var preview: PreviewState
    var metadata: MetadataState
    var observation: ObservationState
    var review: ReviewState
    var destination: DestinationState
}
~~~

Keep the source state separate from the view. A derived thumbnail can be
discarded and recreated. A review candidate can become stale. A destination
can fail after the preview succeeds. Those are different states, not one
isLoading Boolean.

Useful state categories include:

- idle, preparing, ready, failed, and cancelled for transfer;
- requesting, authorized, denied, restricted, and limited for permission;
- starting, running, interrupted, stopped, and failed for capture;
- none, running, partial, complete, stale, and failed for model observation;
- draft, reviewing, accepted, rejected, edited, and committed for a proposal;
- app, export, photos, and discarded for the destination.

Every async operation should carry the entry identity and source revision. A
late transfer or model result must not write into a newly selected item.

## 2. PhotosPicker is a selection and transfer boundary

Use PhotosPicker when the person chooses existing media. The picker result is a
placeholder for the selected asset; load the representation that the feature
actually needs. A selection can fail because the requested representation is
unsupported, the asset is in iCloud and unavailable offline, the item was
deleted, or the task was cancelled.

~~~swift
@MainActor
final class PhotoImportModel: ObservableObject {
    @Published private(set) var state = ImportState.idle

    private var generation = 0
    private var task: Task<Void, Never>?

    func selectionChanged(_ item: PhotosPickerItem?) {
        generation += 1
        let currentGeneration = generation
        task?.cancel()

        guard let item else {
            state = .idle
            return
        }

        state = .loading
        task = Task { [weak self] in
            do {
                let value = try await item.loadTransferable(
                    type: ImportedMedia.self
                )
                try Task.checkCancellation()
                guard let self, self.generation == currentGeneration else {
                    return
                }
                state = value.map(ImportState.ready) ?? .failed(
                    "The selected item did not provide a supported file."
                )
            } catch is CancellationError {
                // A newer selection owns the state.
            } catch {
                guard let self, self.generation == currentGeneration else {
                    return
                }
                state = .failed("The media could not be loaded.")
            }
        }
    }
}
~~~

The exact Transferable type and representation are product decisions. Use a
file representation for large or compressed media when decoding all bytes into
memory is unnecessary. Copy a temporary representation into app-owned storage
before allowing a later review task to depend on it. Keep a user-facing error
separate from a diagnostic error.

For multi-selection, assign a stable request generation and per-item ID. Do
not let completion order decide display order. The UI should show which items
are still loading and which item is currently the review subject.

## 3. Define a transferable media representation

The representation should preserve enough information for review and
destination policy without smuggling a temporary URL through the app.

~~~swift
struct ImportedMedia: Transferable, Sendable, Equatable {
    let fileURL: URL
    let contentType: UTType
    let byteCount: Int64

    static var transferRepresentation: some TransferRepresentation {
        FileRepresentation(
            contentType: .item
        ) { media in
            SentTransferredFile(media.fileURL)
        } importing: { received in
            let destination = FileManager.default.temporaryDirectory
                .appending(path: UUID().uuidString)
            try FileManager.default.copyItem(
                at: received.file,
                to: destination
            )
            return ImportedMedia(
                fileURL: destination,
                contentType: .item,
                byteCount: 0
            )
        }
    }
}
~~~

This is a route sketch, not a universal implementation. The selected SDK may
require a more specific content type, an app-owned file-copy policy, or a
different Transferable initializer. Validate the imported type, file size,
file existence, and cleanup behavior. If a decoded Image representation is
used, confirm which image formats the system representation supports; a custom
file or data representation may be required for the feature's format set.

## 4. Own the camera session outside the view tree

AVCaptureSession coordinates exclusive capture infrastructure. Keep session
configuration, permission, start/stop, output delegates, interruptions, and
teardown in one service or actor. SwiftUI should render state and send user
intent. It should not create a new session every time the body recomputes.

~~~swift
actor CameraSessionController {
    private let session = AVCaptureSession()
    private let photoOutput = AVCapturePhotoOutput()
    private var isConfigured = false

    func configure() throws {
        guard !isConfigured else { return }

        guard AVCaptureDevice.authorizationStatus(for: .video) == .authorized
        else {
            throw CameraError.notAuthorized
        }

        session.beginConfiguration()
        defer {
            session.commitConfiguration()
        }

        guard
            let device = AVCaptureDevice.default(
                .builtInWideAngleCamera,
                for: .video,
                position: .back
            ),
            let input = try? AVCaptureDeviceInput(device: device),
            session.canAddInput(input),
            session.canAddOutput(photoOutput)
        else {
            throw CameraError.unavailable
        }

        session.addInput(input)
        session.addOutput(photoOutput)
        isConfigured = true
    }

    func start() {
        guard isConfigured, !session.isRunning else { return }
        session.startRunning()
    }

    func stop() {
        guard session.isRunning else { return }
        session.stopRunning()
    }
}
~~~

The production service needs a dedicated session queue, audio/video input
choices, output configuration, interruption observers, runtime-error recovery,
capture settings, and a delegate or async continuation for results. Check
canAddInput and canAddOutput before mutating the graph. Use
beginConfiguration/commitConfiguration for related changes.

Request camera and microphone access before configuration. The usage
descriptions in the app's processed Info.plist are part of the feature, not
just release paperwork. When access is denied or restricted, render a useful
non-camera route such as PhotosPicker or import; do not leave a black
viewfinder with a capture button that appears active.

## 5. Bridge the preview layer deliberately

The preview is a view-owned presentation of a service-owned session. A
UIViewRepresentable can host AVCaptureVideoPreviewLayer; its coordinator
should update the layer when the session identity changes and remove observers
when the view leaves the hierarchy.

~~~swift
struct CameraPreview: UIViewRepresentable {
    let session: AVCaptureSession

    func makeUIView(context: Context) -> PreviewView {
        let view = PreviewView()
        view.previewLayer.session = session
        view.previewLayer.videoGravity = .resizeAspectFill
        return view
    }

    func updateUIView(_ view: PreviewView, context: Context) {
        if view.previewLayer.session !== session {
            view.previewLayer.session = session
        }
    }
}

final class PreviewView: UIView {
    override class var layerClass: AnyClass {
        AVCaptureVideoPreviewLayer.self
    }

    var previewLayer: AVCaptureVideoPreviewLayer {
        layer as! AVCaptureVideoPreviewLayer
    }
}
~~~

Treat this as a platform bridge with a proof obligation. Verify orientation,
mirroring, aspect fill/crop, safe-area handling, rotation, interruption, and
the transition from live preview to captured media. The preview layer does not
own authorization, output capture, or app persistence.

Leave enough overlay space for camera controls and the subject. On supported
hardware, Camera Control is a system input with its own platform behavior; it
is not a promise that the same control exists on iPad, Mac, watchOS, tvOS, or
visionOS. Use a system symbol and a labeled fallback for the app's own controls.

## 6. Capture a result with an explicit identity

Photo capture is asynchronous. A capture request should have a capture ID and
settings snapshot. The delegate result should retain the original identity,
orientation/metadata inputs, and any error before publishing a review state.

~~~swift
struct CaptureRequest: Sendable, Equatable {
    let captureID: UUID
    let requestedAt: Date
    let mediaKind: String
    let settingsDescription: String
}

struct CapturedMedia: Sendable, Equatable {
    let captureID: UUID
    let fileURL: URL
    let contentTypeIdentifier: String
    let sourceRevision: Int
}
~~~

Use AVCapturePhotoSettings and AVCapturePhotoOutput for still capture. Do not
assume a photo is ready when the button returns. If video is supported, define
who owns the movie-file output or data-output writer, how audio is handled,
what ends the recording, and how a partial recording is discarded. Live Photo,
depth, high-resolution, flash, stabilization, and codec choices need
target-specific availability and real-device proof.

## 7. Make review a separate stage

After import or capture, show the source before applying optional analysis.
VideoPlayer is the SwiftUI entry point for video playback. Use
AVPlayerViewController when the product needs the system controller surface or
platform-specific AVKit behavior. Keep the player/asset lifetime owned by the
review model, not a transient row.

Review state should answer:

- Is this the original source or a derived render?
- Is the media fully loaded, still transferring, or only a thumbnail?
- Which orientation, crop, duration, and color interpretation is shown?
- Which observations are facts from a framework and which are app-generated?
- Is the proposal current with the source revision?
- What exactly will Save, Export, or Save to Photos do?

No review control should silently replace the source. A crop, normalized image,
transcoded video, or metadata-redacted copy gets a new derived identity and a
visible destination policy.

## 8. Normalize images and metadata before model review

Image I/O can read image properties, create thumbnails, and write a chosen
representation. Use it for orientation-aware decoding and metadata policy
before handing a representation to Vision, Core ML, export, or a generative
review step.

~~~swift
struct MediaInspection: Sendable, Equatable {
    let pixelWidth: Int
    let pixelHeight: Int
    let orientationDescription: String
    let durationSeconds: Double?
    let redactedMetadataKeys: [String]
}
~~~

Do not confuse a thumbnail with the original. Record the source and derived
representation separately. If the feature never needs GPS, device serial,
lens, or capture-time metadata, omit it from the review model and redact it
from an export when the product promises privacy. Validate the destination
format and confirm that the writer does not accidentally preserve sensitive
properties.

## 9. Treat Vision and Core ML output as observations

Vision requests can consume image or video-compatible representations such as
data, URL, image, pixel buffer, or sample buffer depending on the request.
Core ML can provide a model request through Vision or a direct model pipeline.
Choose the representation and request revision intentionally.

~~~swift
struct MediaObservation: Sendable, Equatable {
    let observationID: UUID
    let sourceRevision: Int
    let modelIdentifier: String
    let modelRevision: String
    let kind: String
    let value: String
    let confidence: Double?
    let regionDescription: String?
}
~~~

An observation is not a user-approved fact. Keep confidence and region when
they matter. Store the source revision and model identity. If a request
produces partial results, publish them as partial and let the user continue
reviewing the media. If a request is cancelled or the source changes, discard
or mark the result stale.

For OCR, use the Vision text-recognition request route and preserve the
recognized text's source region if the UI will highlight it. For classification
or custom detection, validate input orientation, crop, pixel format, model
revision, and coordinate conversion. Do not turn a normalized coordinate into
an overlay without checking the displayed aspect/crop.

## 10. Keep Foundation Models behind a review boundary

Foundation Models can be useful after deterministic observations exist: for
example, turning a bounded set of labels and recognized text into a suggested
caption, a folder suggestion, or a short accessibility description. It should
not be the authority for whether an image was captured, whether metadata was
redacted, whether a permission exists, or whether a save succeeded.

Use a typed input and typed candidate.

~~~swift
struct MediaReviewInput: Codable, Sendable {
    let sourceRevision: Int
    let observations: [MediaObservation]
    let allowedActions: [String]
}

struct MediaReviewCandidate: Codable, Sendable, Equatable {
    let candidateID: UUID
    let sourceRevision: Int
    let summary: String
    let suggestedTags: [String]
    let reason: String
    let modelDescription: String
}
~~~

The exact Foundation Models availability, session API, guided generation
schema, and device readiness are SDK- and target-sensitive. Keep the adapter
small and make unavailable, refused, partial, malformed, cancelled, stale,
and complete states visible. The person accepts or edits the candidate; only
the ordinary document/Photos/export path commits it.

## 11. Separate destinations

“Save” is ambiguous in a media feature. Give the person an explicit
destination:

| Destination | Ownership | Proof |
| --- | --- | --- |
| Save in app | App file/document/store | Reopen, revision, migration, failure recovery |
| Export/share | New representation and system share route | Type, metadata, cancellation, recipient |
| Save to Photos | PhotoKit authorization/change request | Limited/add-only behavior and result |
| Replace source | Asset/document mutation | Explicit confirmation and change failure |
| Discard | No destination | Derived files and tasks are cleaned up |

Saving a derived file to the app does not automatically save it to Photos.
Saving a new asset to Photos does not mean the app can later mutate the
original. The UI and state machine should preserve that distinction.

## 12. Design the Liquid Glass shell around the media

Use Liquid Glass for floating, contextual controls around a photo, viewfinder,
or video review surface. The media remains the visual anchor.

Recommended groups:

- capture mode, camera switch, flash, and permission status;
- playback controls and a compact review status;
- analyze, retake, discard, save, and export actions;
- a compact candidate card that says “suggestion” or “detected,” not “fact.”

Avoid:

- glass over the whole image with no separation between content and controls;
- a glass button that hides whether the app is recording or merely previewing;
- color alone for recording, permission, analysis, or stale state;
- a generative result that looks identical to source metadata;
- an always-visible toolbar that blocks the subject or keyboard.

Use the platform Liquid Glass APIs only on the supported deployment path, give
groups stable semantic labels, and provide an opaque/reduced-effects treatment.
A translucent material is not a substitute for contrast, accessibility, or
clear destination copy.

## 13. Handle lifecycle and interruptions

At minimum, model:

- scene inactive/background while transfer or review is running;
- camera or microphone interruption;
- audio-session route changes if audio is captured;
- authorization changing in Settings;
- memory pressure during large decode or model inference;
- cancellation from a new picker item, retake, navigation, or dismissal;
- app termination before an app-owned copy is finalized.

On background, stop a live capture session unless the product has a supported
background design and the necessary entitlement/behavior. Keep a captured
file's app-owned copy alive if review can resume. Never assume a temporary
picker URL, pixel buffer, or preview layer remains valid after the source task
ends.

## 14. Target and input boundaries

| Target/input | Route expectation |
| --- | --- |
| iPhone camera | Physical authorization, orientation, capture, interruption, thermal proof |
| iPhone PhotosPicker | Limited-library/copy/transfer proof; no camera permission required for picker-only flow |
| iPadOS | Split view, pointer, keyboard, multitasking, large preview, no iPhone-only hardware assumptions |
| Mac Catalyst | File import and AVKit review may be stronger than camera capture; compile and menu proof |
| visionOS | Spatial/media presentation and permission model are distinct; do not blindly import iPhone camera UI |
| watchOS | Prefer projection or companion result; do not assume camera/session APIs |
| App extension | Entitlements, memory, lifetime, and media access are narrower |
| VoiceOver/Voice Control | Every state and action needs semantic labels, not only an icon or color |
| Keyboard/pointer/Pencil | Review, retake, play, accept, discard, and export remain reachable |

## Stop conditions

Stop the implementation and resolve the seam when:

- a picker result is being treated as an already-decoded original;
- a temporary file URL is the only source identity;
- a camera session is created in a SwiftUI body or recreated per update;
- a denied permission leaves an apparently active capture control;
- a preview crop changes model coordinates without an explicit transform;
- metadata is exported without a documented privacy policy;
- an AI result has no source revision or review state;
- a candidate writes directly to a document or Photos without confirmation;
- “Save” does not identify its destination;
- a Liquid Glass group hides the media or communicates status only by color;
- the claimed proof is a preview or simulator for a physical-device/system-only behavior.

## Sources

- [PhotosPicker](https://developer.apple.com/documentation/photosui/photospicker)
- [PhotosPickerItem](https://developer.apple.com/documentation/photosui/photospickeritem)
- [Bringing the Photos picker to your SwiftUI app](https://developer.apple.com/documentation/PhotoKit/bringing-photos-picker-to-your-swiftui-app)
- [PhotoKit](https://developer.apple.com/documentation/photokit)
- [AVFoundation capture setup](https://developer.apple.com/documentation/avfoundation/capture-setup)
- [Setting up a capture session](https://developer.apple.com/documentation/avfoundation/setting-up-a-capture-session)
- [Requesting authorization to capture and save media](https://developer.apple.com/documentation/avfoundation/requesting-authorization-to-capture-and-save-media)
- [AVCaptureDevice](https://developer.apple.com/documentation/avfoundation/avcapturedevice)
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
