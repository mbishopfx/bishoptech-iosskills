# SwiftUI media capture and review deep dive

## Purpose

A media feature usually combines a system picker or hardware capture session,
large asynchronous representations, a review surface, and an optional
on-device inference path. Keep each boundary explicit:

~~~text
user-selected or camera-captured source
    -> representation/file identity
    -> preview and media-state normalization
    -> optional Vision/Core ML/Foundation Models observation
    -> user review and edit
    -> app-owned record, export, or Photos mutation
~~~

A PhotosPickerItem is a placeholder until a representation loads. A camera
preview is not a captured asset. A pixel buffer is not a durable photo. A model
observation is not verified truth. A successful Photos change request is not the
same as an app-owned save.

This page complements the existing PhotosUI/PhotoKit, AVFoundation pipeline,
Image I/O, Vision/Core ML, and native media-design pages by focusing on the
SwiftUI capture-and-review composition boundary.

## Choose the source route

| User outcome | First route | Add only when |
| --- | --- | --- |
| Choose one image/video | PhotosPicker | Custom Transferable, file copy, metadata, or AI processing |
| Choose many assets | PhotosPicker multiple selection with a bounded count | Task-group loading, progress/cancellation, deduplication, staged review |
| Use a custom camera UI | AVFoundation AVCaptureSession behind a SwiftUI shell | Photo/video output, focus/exposure, Live Photo, depth, HDR, or custom processing |
| Use system camera capture | UIImagePickerController or another system route | The product genuinely needs custom controls or pixel access |
| Review a captured video | AVKit VideoPlayer or AVPlayerViewController | Custom trim/export/annotations or a UIKit bridge |
| Read image bytes/metadata | Image I/O or PhotoKit representation | Redaction, conversion, orientation, thumbnail, or export policy |
| OCR/document analysis | Vision RecognizeTextRequest/RecognizeDocumentsRequest | Domain schema, source-span review, or local model enrichment |
| Image model inference | Vision CoreMLRequest/Core ML | Model-specific input/output, compute-unit policy, or custom postprocessing |
| Rich app-owned proposal | Foundation Models adapter | Structured review and explicit record mutation |
| Save to Photos | PhotoKit/PHAssetCreationRequest | User-approved external library mutation and change reconciliation |

Start with PhotosPicker when a person can choose an asset. Use a custom
AVFoundation camera only when the product needs a live preview or capture
behavior the system picker cannot provide.

## Source and identity contract

Keep source identity independent from the SwiftUI view.

~~~swift
struct MediaSource: Hashable, Sendable {
    let sourceID: UUID
    let kind: Kind
    let contentTypeIdentifier: String?
    let photoLibraryIdentifier: String?
    let capturedAt: Date?
    let importedAt: Date
    let localURL: URL?
    let sourceRevision: Int

    enum Kind: String, Hashable, Sendable {
        case pickerSelection
        case cameraPhoto
        case cameraMovie
        case livePhoto
        case derivedAsset
    }
}
~~~

A PhotosPickerItem, PHAsset, temporary file, AVAsset, and app-owned record have
different lifetimes and authorities. Record:

- selection/capture provenance;
- content type and representation choice;
- orientation and color/HDR policy;
- local/cloud/library identity where valid;
- modification/capture/import time;
- copy/retention/deletion policy;
- source revision and invalidation rule;
- permission state and user action;
- model version and review state when inference runs.

Do not use a Photos local identifier as a server-global identity without a
mapping strategy. Do not persist a temporary picker/provider URL as if the
bytes were owned. Do not use a preview frame as the source record.

## PhotosPicker is selection plus transfer

PhotosPicker provides a system UI for choosing images and videos. The returned
PhotosPickerItem values are placeholders. Ask each item for a representation
through Transferable and handle nil, failure, iCloud retrieval, and
cancellation.

A route state can make the distinction visible:

~~~swift
enum PickerLoadState: Equatable, Sendable {
    case idle
    case selected(count: Int)
    case loading(itemID: String)
    case ready(MediaSource)
    case unavailable(String)
    case failed(String)
}
~~~

For a single selection:

~~~swift
struct PhotoSelectionView: View {
    @State private var item: PhotosPickerItem?
    @State private var state: PickerLoadState = .idle

    var body: some View {
        PhotosPicker(
            selection: $item,
            matching: .any(of: [.images, .videos])
        ) {
            Label("Choose media", systemImage: "photo.on.rectangle")
        }
        .onChange(of: item) { _, newItem in
            guard let newItem else {
                state = .idle
                return
            }
            let selectedID = newItem.itemIdentifier ?? "unknown"
            state = .loading(itemID: selectedID)
            Task {
                await load(newItem, selectedID: selectedID)
            }
        }
    }

    private func load(
        _ item: PhotosPickerItem,
        selectedID: String
    ) async {
        do {
            let imported = try await MediaImporter().load(item)
            await MainActor.run {
                guard item.itemIdentifier == selectedID ||
                      item.itemIdentifier == nil else { return }
                state = .ready(imported)
            }
        } catch {
            await MainActor.run {
                state = .failed(error.localizedDescription)
            }
        }
    }
}
~~~

The example is a route sketch. The production importer should carry a
generation/token so a later selection supersedes an earlier load even when
item identifiers are absent or repeated. Image is not a universal
representation; the PhotosPicker documentation notes that its Transferable
support is limited, so use a custom Transferable or file-backed representation
for formats such as HEIF, RAW, or large video.

For multiple selection, bound the maximum count and use a task group or
serial queue with cancellation and deduplication. Do not start unlimited
full-resolution loads when a thumbnail or downsampled file is enough for the
first review stage.

## Transfer representation choice

Choose the representation by downstream task:

| Representation | Good for | Risk |
| --- | --- | --- |
| SwiftUI Image | Small UI preview | Format/metadata limitations and no durable bytes |
| DataRepresentation | Small bounded data | Memory pressure for large media |
| FileRepresentation | Video, RAW, large image, staged AI input | Temporary-file lifetime, cleanup, access policy |
| Custom Codable/Transferable record | App-owned source metadata | Not a media file unless a file representation is provided |
| PhotoKit resource | Original/current/edited library bytes | Permission, iCloud, cancellation, Photos authority |

A transfer result should be copied or adopted into an app-owned lifetime before
the UI depends on it. Store the content type, checksum/size, orientation, and
source revision. Avoid logging raw paths, EXIF, precise location, faces, or
model input.

## Custom camera ownership

AVFoundation capture is a session graph:

~~~text
AVCaptureSession
    -> AVCaptureDeviceInput
        -> AVCaptureConnection
            -> AVCaptureVideoPreviewLayer
            -> AVCapturePhotoOutput
            -> AVCaptureMovieFileOutput or data output
~~~

Configure the graph on an owned serial actor/queue. Call
beginConfiguration/commitConfiguration around graph changes. Add at least one
input and output. Start the session only after the required authorization is
granted. Stop and release session-owned work when the feature leaves or the
capture is cancelled.

A SwiftUI shell can own presentation state while a capture service owns the
session:

~~~swift
enum CaptureState: Equatable, Sendable {
    case unavailable(String)
    case requestingPermission
    case configuring
    case ready
    case capturing
    case processing
    case review(MediaSource)
    case failed(String)
}

@MainActor
final class CameraModel: ObservableObject {
    @Published private(set) var state: CaptureState = .configuring

    private let service = CameraService()

    func start() async {
        state = .requestingPermission
        do {
            try await service.start()
            state = .ready
        } catch {
            state = .failed(error.localizedDescription)
        }
    }

    func capturePhoto() async {
        guard state == .ready else { return }
        state = .capturing
        do {
            let source = try await service.capturePhoto()
            state = .review(source)
        } catch {
            state = .failed(error.localizedDescription)
        }
    }

    func stop() async {
        await service.stop()
        state = .unavailable("Camera stopped")
    }
}
~~~

The service must ensure only one start/stop/configuration/capture sequence owns
the session. UI state does not replace session synchronization.
+## Preview layer and SwiftUI interoperability

AVCaptureVideoPreviewLayer is a Core Animation layer. A common bridge is a
UIViewRepresentable whose UIView subclass uses the preview layer as its
layerClass. Keep the bridge narrow:

~~~swift
final class CameraPreviewView: UIView {
    override class var layerClass: AnyClass {
        AVCaptureVideoPreviewLayer.self
    }

    var previewLayer: AVCaptureVideoPreviewLayer {
        layer as! AVCaptureVideoPreviewLayer
    }
}

struct CameraPreview: UIViewRepresentable {
    let session: AVCaptureSession

    func makeUIView(context: Context) -> CameraPreviewView {
        let view = CameraPreviewView()
        view.previewLayer.session = session
        view.previewLayer.videoGravity = .resizeAspectFill
        return view
    }

    func updateUIView(
        _ view: CameraPreviewView,
        context: Context
    ) {
        view.previewLayer.session = session
    }
}
~~~

The preview is not the capture output. Keep orientation, mirroring, safe area,
Camera Control overlay space, accessibility label, and lifecycle policy in the
target. Do not start or stop the session from every representable update.

## Photo capture and video output

For still photos, configure AVCapturePhotoOutput and pass validated
AVCapturePhotoSettings to capturePhoto(with:delegate:). Output settings can
include RAW, HEIF, JPEG, Live Photo, depth, stabilization, or wide-color
choices depending on the device/session. The output validates the settings at
capture time, so check supported formats and features before exposing controls.

For video, decide whether the product needs:

- a movie file output;
- video data output for live frames;
- audio input and AVAudioSession;
- background/interrupt/resume behavior;
- bounded recording duration and storage;
- post-capture AVAsset review/export.

Live Photos and movie file output have pipeline constraints. A feature that
combines modes must check the documented capabilities rather than presenting
every control at once.

Keep the delegate/result boundary:

~~~text
capture request ID
    -> output delegate result
    -> byte/file validation
    -> orientation/metadata normalization
    -> MediaSource revision
    -> review
~~~

A capture callback is not an app save. If a capture fails after the shutter
animation, show a recoverable state and do not leave a phantom record.

## AVKit review

Use SwiftUI VideoPlayer or AVPlayerViewController when the task is playback
with native transport controls, subtitles, AirPlay, or Picture in Picture
behavior. AVPlayerViewController adopts future system styling; do not recreate
its controls inside a glass card.

For a SwiftUI review:

~~~swift
struct VideoReview: View {
    let url: URL
    @State private var player: AVPlayer?

    var body: some View {
        Group {
            if let player {
                VideoPlayer(player: player)
            } else {
                ProgressView("Preparing video")
            }
        }
        .task(id: url) {
            player = AVPlayer(url: url)
        }
        .onDisappear {
            player?.pause()
        }
    }
}
~~~

The target should decide whether the asset is local, security-scoped, provider
backed, or temporary. A player can continue using a URL after the editor
assumes work is complete; define lifetime and cancellation. For trim/export,
use AVFoundation asset APIs with a file-backed output and validate the result
before offering ShareLink or a Photos save.

## Image orientation, thumbnails, and metadata

Image I/O can read the source type, properties, orientation, thumbnails, and
metadata. Decode only the pixel size needed for the current surface. Use
CGImageSource thumbnail options rather than decoding a full original into a
grid. Preserve orientation through model input and export; a rotated preview
can produce a correct-looking UI and a wrong model result.

Metadata policy should be explicit:

| Metadata | Default review question |
| --- | --- |
| EXIF orientation | Preserve for correct display; normalize once for model/export |
| GPS/location | Redact by default from exports/AI context unless required |
| Timestamp | Show only when useful and authorized |
| Camera/device | Usually not needed for model context |
| Faces/private text | Scope and retention require special review |
| XMP/IPTC | Preserve or remove according to export contract |
| HDR/gain map/depth | Keep only when output route supports it |
| Original filename | Treat as user data; do not expose by default |

When exporting, use Image I/O destination APIs to set or remove metadata and
finalize the output. Verify the resulting file opens, has the intended type,
and contains the intended redaction.

## Vision and Core ML review

Use the smallest normalized representation that satisfies the model. Preserve
orientation and record the input revision.

Vision's request-based Swift API can run text/document/image analysis on
Data, URL, CGImage, CIImage, CVPixelBuffer, or CMSampleBuffer depending on
the request. RecognizeTextRequest returns observations with transcripts,
languages, confidence-related data, and normalized locations. CoreMLRequest
bridges a Core ML image model into Vision and returns model-specific
observations.

Keep inference separate from view rendering:

~~~swift
struct MediaObservation: Equatable, Sendable {
    let sourceID: UUID
    let sourceRevision: Int
    let modelID: String
    let modelRevision: String
    let summary: String
    let sourceRegions: [NormalizedRegion]
}

enum ReviewState: Equatable, Sendable {
    case unavailable(String)
    case loading
    case ready
    case processing
    case candidate(MediaObservation)
    case stale
    case failed(String)
    case committed
}
~~~

A model output is an observation or proposal. Validate source ID/revision,
model revision, schema, confidence policy, region bounds, and user-visible
copy. Require explicit review before writing a caption, tag, record, album,
metadata field, or external action.

## Foundation Models over media-derived text

Foundation Models is usually the second stage, not the first raw-pixel
boundary:

~~~text
selected media
    -> Vision/Core ML deterministic observations
    -> normalized text/regions/labels
    -> bounded Foundation Models instruction
    -> typed proposal
    -> review and commit
~~~

If the product truly uses a multimodal model route, keep source scope, capability
checks, and privacy copy explicit. Do not put full-resolution media, unrelated
EXIF, or the entire Photos library into a prompt by default. An on-device claim
does not prove zero retention, zero logs, zero memory pressure, or correct
output.

## Review and commit boundary

Use one review model for both picker and camera sources:

~~~swift
struct MediaReviewCandidate: Equatable, Sendable {
    let source: MediaSource
    let observation: MediaObservation?
    let proposedTitle: String?
    let proposedTags: [String]
    let sourceRevision: Int
}

enum MediaCommitAction {
    case saveToApp
    case exportFile
    case saveToPhotos
    case discard
}
~~~

The review UI should show:

- source/preview and content type;
- loading/download/processing state;
- orientation and metadata policy when relevant;
- model observation versus proposed app fields;
- edit/accept/discard;
- save destination;
- stale/changed source;
- failure/retry;
- accessibility equivalents.

“Saved” must say where: app, file destination, or Photos library. Do not apply
AI tags or metadata merely because the model returned a result.

## Liquid Glass capture and review shell

Use system camera/picker surfaces for selection and capture. Use Liquid Glass
only around app-owned controls:

~~~text
large viewfinder or source preview
    -> capture/select action
    -> compact state/progress cluster
    -> review controls
    -> explicit save/export/discard
~~~

For Camera Control or locked camera capture routes, leave space for system
overlays and avoid duplicating controls the system already presents. Keep
controls minimal over the viewfinder. A glass surface should not obscure the
preview or imply a model result is certain.

Use text labels for:

- camera permission;
- loading from Photos/iCloud;
- capture in progress;
- preview ready;
- model processing;
- no reliable result;
- saved destination;
- source changed.

Test bright/dark/HDR media, landscape/portrait, notch/safe area, Dynamic Type,
reduced transparency, increased contrast, VoiceOver, and narrow iPadOS windows.

## Lifecycle, interruptions, and background

Capture sessions can be interrupted, restricted, or stopped when the app leaves
the foreground or another system surface takes the camera. Model and media
tasks can outlive the view. Use task identity and cancellation:

- cancel picker transfer when a new selection supersedes it;
- cancel frame inference when the review source changes;
- stop/release the camera when the screen is dismissed or permission changes;
- pause/reconcile video playback when the scene is inactive;
- checkpoint large captures and export work;
- reconcile a Photos change observer after relaunch;
- never update a new source with a late callback from an older source.

Treat interruption, denied permission, device unavailable, iCloud offline,
corrupt media, storage full, thermal pressure, and cancelled export as normal
product states.

## Target and proof boundaries

| Claim | Minimum proof |
| --- | --- |
| PhotosPicker selection works | Named-target compile plus real picker/system run |
| Custom camera works | Physical camera/microphone permission and capture run |
| Preview is correct | Physical device orientation/safe-area/Camera Control run |
| Photo/video output works | Physical capture, output reopen, cancellation, storage test |
| Video review works | AVKit target run with interruption and background |
| Metadata policy works | Image I/O input/output inspection and redaction test |
| Vision/Core ML review works | Labeled fixtures plus representative device/model run |
| AI proposal is safe | Source revision, stale, invalid, review, commit tests |
| Liquid Glass shell works | Real media visual/accessibility matrix |
| iPadOS/Catalyst works | Named target and physical/platform-specific input |
| Release works | Archive/privacy strings/entitlements and TestFlight smoke |

A Simulator can validate layout and state fixtures. It does not prove camera,
microphone, iCloud retrieval, thermal behavior, model readiness, or physical
input.

## Common failures

- treating PhotosPickerItem as image bytes or a durable URL;
- loading every selected original before a preview or memory policy exists;
- starting AVFoundation session work from a SwiftUI view update;
- configuring capture inputs without permission and usage descriptions;
- presenting a live preview without safe-area/orientation/system-overlay space;
- retaining a camera session after the feature leaves;
- using UIImage as the only path for capture output that carries rich metadata;
- showing model labels as verified facts;
- sending GPS, EXIF, faces, or unselected assets into an AI context;
- saving to Photos without naming it as a Photos library mutation;
- letting a stale selection or capture callback update a new source;
- using glass to hide loading, uncertainty, or permission failure;
- treating a simulator camera or screenshot as physical-camera proof.

## Related routes

- [Photos, files, and documents](../43-system-framework-deep-dives/00-photos-files-and-documents.md)
- [PhotosUI, PhotoKit, and source-controlled image workflows](67-photosui-photokit-source-and-editing.md)
- [AVFoundation and media](00-avfoundation-and-media.md)
- [AVFoundation media pipeline](09-avfoundation-media-pipeline.md)
- [Vision/Core ML model lifecycle](66-core-ml-model-lifecycle-and-inference.md)
- [Image I/O and media review](54-imageio-source-destination-and-metadata.md)
- [Photos AI review design](../21-design-deep-dives/88-photos-ai-review-and-liquid-glass-design.md)

## Sources

- [PhotosUI](https://developer.apple.com/documentation/photosui)
- [PhotosPicker](https://developer.apple.com/documentation/photosui/photospicker)
- [PhotosPickerItem](https://developer.apple.com/documentation/photosui/photospickeritem)
- [Bringing Photos picker to your SwiftUI app](https://developer.apple.com/documentation/PhotoKit/bringing-photos-picker-to-your-swiftui-app)
- [Core Transferable](https://developer.apple.com/documentation/coretransferable)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [DataRepresentation](https://developer.apple.com/documentation/coretransferable/datarepresentation)
- [FileRepresentation](https://developer.apple.com/documentation/coretransferable/filerepresentation)
- [AVFoundation Capture setup](https://developer.apple.com/documentation/avfoundation/capture-setup)
- [Setting up a capture session](https://developer.apple.com/documentation/avfoundation/setting-up-a-capture-session)
- [Requesting authorization to capture and save media](https://developer.apple.com/documentation/avfoundation/requesting-authorization-to-capture-and-save-media)
- [AVCaptureSession](https://developer.apple.com/documentation/avfoundation/avcapturesession)
- [AVCaptureDevice](https://developer.apple.com/documentation/avfoundation/avcapturedevice)
- [AVCapturePhotoOutput](https://developer.apple.com/documentation/avfoundation/avcapturephotooutput)
- [AVCapturePhotoSettings](https://developer.apple.com/documentation/avfoundation/avcapturephotosettings)
- [AVCaptureVideoPreviewLayer](https://developer.apple.com/documentation/avfoundation/avcapturevideopreviewlayer)
- [AVCapturePhotoCaptureDelegate](https://developer.apple.com/documentation/avfoundation/avcapturephotocapturedelegate)
- [AVKit](https://developer.apple.com/documentation/avkit)
- [VideoPlayer](https://developer.apple.com/documentation/avkit/videoplayer)
- [AVPlayerViewController](https://developer.apple.com/documentation/avkit/avplayerviewcontroller)
- [Image I/O](https://developer.apple.com/documentation/imageio)
- [CGImageSource](https://developer.apple.com/documentation/imageio/cgimagesource)
- [CGImageDestination](https://developer.apple.com/documentation/imageio/cgimagedestination)
- [Image Properties](https://developer.apple.com/documentation/imageio/image-properties)
- [Vision](https://developer.apple.com/documentation/vision)
- [RecognizeTextRequest](https://developer.apple.com/documentation/vision/recognizetextrequest)
- [CoreMLRequest](https://developer.apple.com/documentation/vision/coremlrequest)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adding intelligent app features with generative models](https://developer.apple.com/documentation/foundationmodels/adding-intelligent-app-features-with-generative-models)
- [Camera Control HIG](https://developer.apple.com/design/human-interface-guidelines/camera-control)
- [Live Photos HIG](https://developer.apple.com/design/human-interface-guidelines/live-photos)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
