# Screen Capture and Broadcast Services

Screen capture is a system-mediated capability, not just another media input. The app must make the capture source, microphone state, camera state, recording lifecycle, storage destination, and sharing behavior legible to the person using it.

The iOS 26 planning rule is to verify the exact SDK and deployment target before choosing an API. Apple’s current documentation describes ScreenCaptureKit as the newer high-control route and marks the older ReplayKit recording and broadcast APIs as deprecated. Apple’s current iOS ScreenCaptureKit sample also states that it requires iOS 27 or later. That sample is useful architecture guidance, but it is not proof that the same route is available on an iOS 26 deployment target.

## Choose the route by the actual outcome

| Outcome | First route to investigate | Boundary |
| --- | --- | --- |
| Record the app’s own experience with minimal editing | ReplayKit compatibility route if the selected SDK still exposes the needed API | Current Apple docs mark the legacy recording methods deprecated. Confirm the target SDK, warnings, and supported deployment range before committing. |
| Let a person choose full-display or app-owned content | ScreenCaptureKit and its system content-sharing picker | The current Apple iOS sample requires iOS 27 or later. Treat iOS 26 support as an availability question that must be compiled and run on the exact target. |
| Capture a camera or microphone for an app-owned feature | AVFoundation with AVCaptureSession | Camera and microphone authorization, capture queues, route changes, interruption, and usage descriptions are separate from screen-recording permission. |
| Send captured buffers to a broadcast service | A documented, non-deprecated broadcast route in the selected SDK | Historical ReplayKit broadcast-extension classes are currently marked deprecated or no longer supported in Apple’s reference. Do not build a new product on an old sample without a target-specific check. |
| Save a finished movie to Photos | PhotoKit after the file is finalized | A successful file write is not the same as a successful Photos-library change. Request the least privilege needed and handle denial or limited access. |
| Review a recording with on-device AI | A file or bounded sample-buffer handoff into Vision, Core ML, Speech, or Foundation Models | The model sees an app-owned representation after capture. It must not silently upload or turn unreviewed output into a domain-side effect. |

## ReplayKit compatibility contract

ReplayKit historically provides recording of the app display, app audio, microphone commentary, preview/editing, and broadcast integration. The recorder is shared on the device, only one app can use it at a time, and Apple documents cases in which it is unavailable. It also cannot record AVPlayer content.

For an iOS 26 compatibility slice:

1. Confirm the exact availability and deprecation state of RPScreenRecorder in the selected Xcode SDK.
2. Query availability before presenting a start action.
3. Treat the system confirmation or picker as part of the capture contract.
4. Keep recording state in an app-owned coordinator rather than deriving it from a button’s appearance.
5. Stop or cancel cleanly when the scene resigns active, the system reports an error, or the person leaves the capture flow.
6. Finalize the output before opening review, Photos, or a share sheet.

Do not call a legacy ReplayKit method “supported on iOS 26” merely because a symbol still autocompletes. The evidence must identify the SDK, deployment target, compiler warning state, device OS, and observed runtime behavior.

## ScreenCaptureKit availability gate

ScreenCaptureKit exposes a system content-sharing picker, content filters, streams, stream outputs, recording outputs, and fine-grained audio/video selection. Apple’s current documentation says the framework replaces ReplayKit for screen streaming and mirroring and recommends the shared system picker instead of a custom source selector.

The current iOS sample demonstrates:

- full-display and in-app capture modes;
- picker configuration for microphone and camera controls;
- a filter returned by the system picker;
- an SCStream configured from that filter;
- sample-buffer outputs and direct recording output;
- rolling clip buffering;
- finalization before saving to Photos or presenting ShareLink.

The same sample states that it requires iOS 27 or later. For an iOS 26 app, keep this route behind an exact target check. A safe capability adapter has three outcomes:

| Adapter result | UI behavior |
| --- | --- |
| The selected SDK and OS support the ScreenCaptureKit route | Present the Apple picker, report the selected source, and start a bounded stream. |
| The target does not support the route but a documented ReplayKit compatibility route does | Explain that capture is app-scoped or has fewer controls, then use the compatibility route. |
| Neither route is available or permission is denied | Offer an app-owned camera/microphone workflow, an import workflow, or an explicit unavailable state. |

Do not imitate the system picker with a custom list of windows or displays. The source choice is privacy-sensitive and belongs to the operating system where Apple provides that surface.

## Capture, AI, and storage boundaries

Keep these objects separate:

| Object | Owns | Must not claim |
| --- | --- | --- |
| Capture session | Permission state, source selection, running/paused/stopped state, interruptions, and sample delivery | That a recording was saved, shared, uploaded, or understood by AI |
| Media artifact | URL, duration, codec/container metadata, byte count, checksum, and finalization state | That Photos accepted it or that its content is trustworthy |
| AI observation | Transcript, labels, timestamps, embeddings, or a typed proposal with model/version metadata | That the person approved it or that the domain record changed |
| Review model | Evidence preview, source timestamps, confidence/uncertainty, edits, and approval state | That a system surface or server accepted a side effect |
| Domain action | Validated, idempotent commit to app-owned data | That capture or model completion happened merely because the action was requested |

For live analysis, use a bounded queue or latest-frame policy selected for the model and product outcome. Do not start an unbounded task per sample buffer. If a frame can be dropped, record that policy. If every frame matters, record the storage, timing, and thermal design instead.

## Permission and privacy gates

- Add NSMicrophoneUsageDescription when the app accesses the microphone.
- Add NSCameraUsageDescription when the app accesses the camera.
- Request only the media access needed for the selected flow.
- Use the system screen-sharing or recording consent route instead of a custom permission imitation.
- Ask for Photos add-only access when the product only saves generated media.
- Explain the purpose before a system alert only when the context is not already clear; the pre-alert should lead to the system alert and should not manipulate the person into allowing access.
- Show a conspicuous in-app recording state with elapsed time, source, microphone state, and a stop action.
- Never design a feature that records other people without their awareness or that hides the recording state.
- Keep temporary capture files in an app-controlled location and delete them according to the retention decision.
- Redact or avoid private notifications, passwords, credentials, and unrelated windows in any recording or AI export.

## Lifecycle and failure states

Model the route explicitly:

idle -> requesting permission -> presenting picker -> preparing -> running -> paused/interrupted -> stopping -> finalizing -> reviewable -> saved/shared

Every transition needs a failure or cancellation branch:

- unsupported hardware or OS;
- another recorder or system route is active;
- user cancels the picker or denies permission;
- microphone or camera route changes;
- app moves to the background;
- stream output stalls or drops frames;
- disk is full or the output cannot be finalized;
- recording stops because of an interruption or thermal pressure;
- Photos, ShareLink, or a server handoff rejects the artifact;
- the AI model is unavailable, cancelled, or produces invalid output.

The UI should distinguish “capture stopped,” “file finalized,” “saved to Photos,” “shared,” and “analysis completed.” Those are different facts.

## Background and extension boundaries

Background execution is a target configuration, not a promise that a stream will continue. Inspect the exact UIBackgroundModes values supported by the selected SDK and the current ScreenCaptureKit sample before adding a mode. The sample’s iOS configuration names screen-capture and audio for its newer target; that is not evidence that an iOS 26 deployment accepts or honors the same configuration.

An extension or broadcast process has its own target membership, signing, memory, lifecycle, and communication boundary. Pass only the smallest versioned control messages needed. Do not assume the main app remains alive, that an extension can access every app container, or that an extension’s callback proves a server received media.

## Native UI and accessibility contract

Use semantic SwiftUI controls for start, stop, pause, resume, review, save, and share. Keep the primary stop action discoverable and reachable with VoiceOver, Switch Control, Voice Control, Full Keyboard Access, pointer input, and Dynamic Type. Announce state changes such as recording started, microphone disabled, capture interrupted, and file ready.

Liquid Glass can group a functional capture toolbar or review action group, but it must not be used to obscure privacy state or reduce legibility over moving media. Keep the recording indicator visually distinct, respect Reduce Motion and Reduce Transparency, and provide a static fallback when material effects are unavailable or inappropriate.

## Sources

- [ReplayKit](https://developer.apple.com/documentation/replaykit)
- [RPScreenRecorder](https://developer.apple.com/documentation/replaykit/rpscreenrecorder)
- [ScreenCaptureKit](https://developer.apple.com/documentation/screencapturekit)
- [Capturing screen content on iOS](https://developer.apple.com/documentation/screencapturekit/capturing-screen-content-on-ios)
- [SCContentSharingPicker](https://developer.apple.com/documentation/screencapturekit/sccontentsharingpicker)
- [SCStream](https://developer.apple.com/documentation/screencapturekit/scstream)
- [AVCam: Building a camera app](https://developer.apple.com/documentation/avfoundation/avcam-building-a-camera-app)
- [Requesting authorization to capture and save media](https://developer.apple.com/documentation/avfoundation/requesting-authorization-to-capture-and-save-media)
- [Setting up a capture session](https://developer.apple.com/documentation/avfoundation/setting-up-a-capture-session)
- [PhotoKit](https://developer.apple.com/documentation/photokit)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [UIBackgroundModes](https://developer.apple.com/documentation/BundleResources/Information-Property-List/UIBackgroundModes)
- [Apple Developer agreements and guidelines](https://developer.apple.com/support/terms/)
