# Screen Capture, Broadcast, and AI Review Route

Use this route for a feature such as “record a product demo, keep the media on the device, extract a transcript or visual outline, let the person correct it, and optionally save or share the result.”

This is a route composition, not a claim that every API below is available on every iOS 26 device. Choose the capture adapter after compiling against the selected SDK and deployment target.

## Outcome contract

The person can:

1. understand the capture source and destination;
2. grant or deny the required permission;
3. start and stop a capture;
4. see whether the artifact was finalized;
5. review an optional local AI proposal against the original media;
6. edit or discard the proposal;
7. save, share, or commit only after an explicit action.

## Route selector

| Product requirement | Adapter |
| --- | --- |
| App-owned camera or microphone | AVFoundation AVCaptureSession |
| App display recording with compatibility constraints | ReplayKit adapter after exact SDK/deprecation review |
| Full-display or fine-grained source selection on a supported target | ScreenCaptureKit adapter with SCContentSharingPicker |
| Live service output | A currently supported system broadcast route for the exact target; do not assume historical ReplayKit extension APIs are future-proof |
| AI from finished media | Speech, Vision, Core ML, Natural Language, or Foundation Models after bounded handoff |
| Durable media | App-owned file, PhotoKit, or a user-selected Files/share destination |

ScreenCaptureKit’s current Apple iOS sample requires iOS 27 or later. For an iOS 26 product, the capability state should be computed at runtime and compile time, with an explicit fallback to ReplayKit, camera capture, import, or unavailable.

## Ownership graph

SwiftUI surface -> CaptureCoordinator -> CaptureAdapter -> MediaArtifactStore -> AnalysisCoordinator -> ReviewModel -> DomainUseCase -> Photos/Share/system surface

| Layer | Owns | Output |
| --- | --- | --- |
| SwiftUI surface | Intent, permissions explanation, live status, review actions | User commands |
| CaptureCoordinator | State machine, cancellation, source/mic/camera state, interruption | Capture events |
| CaptureAdapter | ReplayKit, ScreenCaptureKit, or AVFoundation details | Samples or finalized file |
| MediaArtifactStore | Temporary/final URLs, metadata, retention, cleanup | Reviewable artifact |
| AnalysisCoordinator | Bounded work, model readiness, progress, cancellation | Observations/proposals |
| ReviewModel | Evidence, edits, confidence, approval state | Explicit commit request |
| DomainUseCase | Validation and idempotent write | Domain truth |
| System adapter | Photos, ShareLink, App Intent, or server handoff | Observed system result |

The capture adapter must not mutate the domain model. The AI analyzer must not silently save or share. The review screen must not claim a system result before its callback or async result is observed.

## State machine

Recommended state vocabulary:

idle

requestingPermission

selectingSource

preparing

running

interrupted(reason)

stopping

finalizing

ready(artifact)

analyzing(artifact, progress)

reviewing(artifact, proposal)

committing

completed

failed(recoverableError)

Persist enough state to recover from process termination without pretending that a live stream survived. A temporary file can be resumed or cleaned; a live capture session cannot be reconstructed from a Boolean.

## Capture adapter decisions

### ReplayKit adapter

Use only after checking the current SDK’s deprecation and availability warnings. Query recorder availability, request the user’s confirmation through the system route, keep the callback short, and finalize the output before downstream work. Treat recorder-busy, unsupported, cancelled, interrupted, and permission-denied states as normal UI states.

### ScreenCaptureKit adapter

Use the shared system content-sharing picker. Register the observer before presenting it, build the stream from the returned filter, and attach only the outputs needed for the feature. The current Apple iOS sample demonstrates direct recording output and rolling clip buffering; it also identifies iOS 27 or later as its device requirement. Gate the adapter for an iOS 26 product until the selected SDK and a signed device run prove otherwise.

### AVFoundation adapter

Use AVCaptureSession when the actual input is the camera or microphone, not the device screen. Configure the session on its dedicated queue, request camera/microphone access before starting, set a bounded output policy, and tear down on cancellation or interruption. An app-owned camera preview is not a substitute for system screen-recording consent.

## AI handoff

The handoff should be file- or window-bounded:

1. finalize the media artifact;
2. record duration, source, timestamps, orientation, codec/container, and checksum;
3. select the time range or frames to analyze;
4. verify model and language availability;
5. run a bounded analyzer with cancellation;
6. attach source references to every proposal;
7. validate the proposal deterministically;
8. present an editable review;
9. commit only after approval.

For live preview intelligence, use a bounded latest-frame or sampled-window policy. Never allow a model task to retain every incoming frame. If the model needs a continuous sequence, make the storage and thermal tradeoff explicit and measure it on the target device.

## Privacy and retention

The default local-first policy is:

- capture remains in the app’s container until the person chooses an export;
- temporary files have an expiry and cleanup path;
- no transcript, frame, or embedding is uploaded without a separate product decision and notice;
- AI output carries model/version and source-range metadata;
- recordings containing notifications, credentials, or other people are treated as sensitive;
- the review surface exposes the original evidence before a derived result is saved;
- signing out or deleting the source record removes derived proposals according to the product’s retention policy.

Use the least-privilege Photos path. If the only destination is app-owned storage or ShareLink, do not request Photos write access merely to display a preview.

## Native UI composition

Use the design sequence:

intent card -> system permission/picker -> live capture bar -> artifact review -> optional AI proposal -> save/share/commit

The capture bar may use a functional Liquid Glass group for stop, elapsed state, and source status. The review sheet should show the media first, then the AI proposal, then the action. Provide a plain fallback for reduced transparency and make state changes accessible without animation.

## Fallback matrix

| Failure | Product-preserving fallback |
| --- | --- |
| ScreenCaptureKit unavailable on iOS 26 target | ReplayKit compatibility adapter if verified; otherwise app-owned camera/import workflow |
| ReplayKit unavailable or deprecated route unsuitable | App-owned AVFoundation capture or user-selected import |
| Mic denied | Continue silent capture if meaningful, clearly label it, or stop before capture |
| File finalization fails | Preserve any recoverable partial file only if the format is valid; otherwise explain that no artifact was produced |
| Model unavailable | Show the recording and manual metadata/editing flow |
| AI proposal invalid | Keep the source artifact, show no proposal, and offer retry |
| Save/share fails | Keep the finalized file in app storage and offer retry or Files/share |

## Proof minimum

Do not call the feature complete until the selected route has evidence for:

- exact SDK/deployment target and deprecation warnings;
- permissions and purpose strings;
- system picker or recorder consent;
- start/stop/interruption/cancel behavior;
- finalized media integrity;
- bounded analysis and cancellation;
- review and idempotent commit;
- save/share result;
- VoiceOver, Dynamic Type, Reduce Motion, Reduce Transparency, alternate input;
- signed physical-device capture on each claimed device family;
- archive/extension/entitlement configuration if a system or extension route is used.

## Sources

- [ReplayKit](https://developer.apple.com/documentation/replaykit)
- [RPScreenRecorder](https://developer.apple.com/documentation/replaykit/rpscreenrecorder)
- [ScreenCaptureKit](https://developer.apple.com/documentation/screencapturekit)
- [Capturing screen content on iOS](https://developer.apple.com/documentation/screencapturekit/capturing-screen-content-on-ios)
- [SCContentSharingPicker](https://developer.apple.com/documentation/screencapturekit/sccontentsharingpicker)
- [SCStream](https://developer.apple.com/documentation/screencapturekit/scstream)
- [AVCam: Building a camera app](https://developer.apple.com/documentation/avfoundation/avcam-building-a-camera-app)
- [AVCaptureVideoDataOutput](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutput)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Vision](https://developer.apple.com/documentation/vision)
- [PhotoKit](https://developer.apple.com/documentation/photokit)
