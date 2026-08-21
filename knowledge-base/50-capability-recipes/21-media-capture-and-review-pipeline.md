# Media capture and review pipeline

## Outcome

Build a native feature that captures a photo, movie, or microphone recording; lets the user inspect it; optionally transcribes, recognizes, or organizes it on device; and only then saves, exports, or hands off the result.

The recipe is intentionally media-type neutral:

    user intent -> permission -> capture/import -> finalized source -> optional analysis -> review/edit -> approved record -> export/share/system projection

Pick one capture route first. Add another media type only when the user outcome requires it.

## Route selector

| Need | Route | First proof |
| --- | --- | --- |
| Take a still and inspect it | AVCapturePhotoOutput or PhotosUI | Physical camera/import fixture and completed photo delegate result. |
| Record a movie for later review | AVCaptureMovieFileOutput | Physical camera/mic, interruption, stop completion, and playable finalized file. |
| Show live camera guidance | AVCaptureVideoDataOutput plus a preview | Physical device, bounded frame policy, dropped-frame counter, and cancellation. |
| Record voice and transcript it | AVAudioSession plus AVAudioEngine or audio-file route, then SpeechAnalyzer | Physical microphone, route change/interruption, transcript availability, and reviewed segments. |
| Play or inspect a file | AVPlayer/AVKit plus AVAsset | Local fixture, buffering/failure states, aspect ratio, captions/transcript route. |
| Trim or convert before sharing | AVAssetExportSession | Supported preset/type, successful completion, output re-open, and partial-file cleanup. |

## Target register

Before implementation, write down the selected target and the gates:

| Gate | Decision |
| --- | --- |
| App target | Owns SwiftUI screens, capture coordinator, review model, and user actions. |
| Deployment target | Determines which SwiftUI, AVFoundation, Speech, and observation APIs may be used directly. |
| Camera permission | Required only for camera capture; add a truthful camera usage description. |
| Microphone permission | Required for movie audio or audio recording; add a truthful microphone usage description. |
| Speech permission/assets | Required for the chosen Speech route; availability and locale/model assets are runtime state. |
| Photos/files | Decide whether the source is imported, captured, sandbox-local, or shared to another system surface. |
| Background modes | Treat background audio, processing, PiP, and camera as separate configuration and product claims. |
| Device family | Record required cameras, microphone input, orientation, audio route, storage, and thermal envelope. |
| Privacy | Define whether raw media, derived text, metadata, and temporary exports remain on device. |
| Release | Inspect entitlements, privacy strings/manifests, target membership, archive resources, and destination configuration. |

## State machine

Keep capture, analysis, review, and export state separate. A practical state graph is:

    idle
      -> requestingAccess
      -> configuring
      -> ready
      -> capturing
      -> stopping
      -> sourceFinalized
      -> analyzing
      -> review
      -> exporting
      -> completed

Side states:

    denied
    restricted
    unsupported
    interrupted
    routeUnavailable
    runtimeError
    droppedInput
    modelUnavailable
    lowConfidence
    cancelled
    storageFull
    exportFailed

The review model should carry a session token. Any late frame, transcript segment, or export callback that belongs to an old token is stale and must not update the current draft.

## Layered architecture

| Layer | Example type | Responsibility |
| --- | --- | --- |
| View | CaptureView, ReviewView, ExportSheet | Render state, accessibility, layout, and user intent. |
| Main-actor model | CaptureScreenModel | Own visible state, selected mode, review edits, and task handles. |
| Capture adapter | CameraSessionCoordinator, AudioCaptureCoordinator | Own framework graph, permissions, start/stop, delegate callbacks, and teardown. |
| Value boundary | MediaSource, FrameSnapshot, AudioChunk, TranscriptSegment | Carry bounded, Sendable-friendly values with source/time/orientation metadata. |
| Analysis service | SpeechService, VisionService, CoreMLService | Perform cancellable processing and publish observations/proposals. |
| Review domain | MediaDraft, ReviewDecision, ApprovedMediaRecord | Preserve source, proposal, edits, approval, provenance, and retention. |
| Export boundary | MediaExporter | Produce a finalized file and hand it to a user-selected destination. |
| System projection | ShareLink, FileDocument, AppIntent, widget, or activity | Expose only the approved projection needed by the system surface. |

Do not let the view create AVAudioEngine, start a session in body, or treat a model callback as a save operation. Do not make a capture adapter know whether the user has accepted a transcription.

## Capture sequence

### Permission and capability

Explain the immediate action first. Read authorization before configuring the session. If permission is denied or restricted, render a route to Settings or a non-camera fallback only when that fallback serves the same goal.

Check:

- authorization status;
- device discovery result;
- media type availability;
- ability to add the selected input;
- ability to add the chosen output;
- current orientation and supported connection properties;
- current microphone route and format;
- storage and output destination.

### Session ownership

Create one owner for the session graph. Configure input/output changes between beginConfiguration and commitConfiguration. Use a serial session queue for graph work and startRunning/stopRunning. Publish state values to the main actor rather than sending the session object into the view.

The session token should change on each new capture. On stop or disappearance:

1. stop new analysis;
2. finish or cancel the in-flight capture according to the product policy;
3. stop the session or engine;
4. release the preview/stream connection;
5. finish any AsyncStream exactly once;
6. delete or retain temporary files according to the draft policy.

### Source finalization

Do not open the review screen as if the source were finalized until the photo delegate, movie-file delegate, audio-file close, or writer completion has reported success. Include:

- stable local source identifier;
- file URL or bounded image reference;
- media kind;
- capture start/end time;
- duration when known;
- orientation and color-space metadata;
- audio/video track summary;
- source revision or transformation;
- retention and deletion policy.

## Analysis route

Analysis is optional and should be cancellable:

    finalized source -> normalize -> analysis -> observation/proposal -> review

### Speech

Use SpeechAnalyzer with the selected SpeechTranscriber configuration when the target supports the locale and required assets. Feed one input sequence per analyzer and consume its asynchronous results. Keep provisional and final transcript ranges separate. Finish or cancel the analyzer when the recording ends or the view no longer owns it.

If the model or locale is not available, offer the original audio and a manual text path. Do not silently send the recording to a remote service when the product is positioned as private or on-device.

### Vision and Core ML

Use the smallest Vision request that matches the outcome. Preserve orientation and crop policy. For a live stream, coalesce or discard stale frames according to the product contract. For a finalized photo or movie frame, store the source identifier and request/model revision with the observation.

Core ML model loading, compilation, input validation, and prediction are separate states. A successful prediction still needs domain validation and review before it becomes a record or action.

### Foundation Models

Foundation Models may organize or rewrite a bounded, reviewed media-derived transcript or observation. Keep the source and deterministic observation available. Use typed output and deterministic validation when a proposal will become structured app data. A generated title, summary, or task is not approved until the user accepts it or the domain’s explicit policy allows automatic commit.

## Review screen composition

Recommended hierarchy:

    source preview/player
    source metadata and state
    observation or transcript
    edits/corrections
    primary approval action
    secondary discard/retake/export actions

The primary approval action should be disabled or replaced by a clear explanation when the source is still processing. Let users keep the original when a proposal is poor. If the screen contains a glass action group, limit it to actions such as Accept, Retake, Export, and Share; keep the source content outside the group.

Review requirements:

- show whether text is partial, final, or user-edited;
- expose source time ranges for transcript or frame-derived results;
- allow correction without destroying the original;
- preserve an undo or discard path;
- disclose if a result came from a model or framework observation;
- keep sensitive source media out of logs and previews used for unrelated tests;
- make the approved record and export destination explicit.

## Fallback matrix

| Failure or boundary | User-facing fallback | Data policy |
| --- | --- | --- |
| Permission not determined | Explain and request at action time | Do not start capture before authorization. |
| Permission denied/restricted | Show non-capture import/manual route or Settings guidance | Keep no unauthorized media object. |
| Camera/mic unavailable | Show hardware-unavailable state and retry | Do not pretend a preview is active. |
| Another app interrupts capture | Pause/finish safely and offer resume if valid | Preserve the draft only if the file is valid. |
| Audio route changes | Re-read route, update state, and pause/rebuild if needed | Keep source metadata and interruption reason. |
| Late frames/dropped samples | Show current-frame mode or reduced-rate fallback | Record drop count/latency for evaluation; do not claim every frame. |
| Asset not finalized | Keep processing state | Do not expose incomplete file to share/export. |
| Speech locale/model unavailable | Keep audio and manual transcript path | Do not silently switch to a remote model. |
| OCR/model low confidence | Show proposal with correction controls | Do not auto-commit uncertain fields. |
| User cancels | Return to capture/review or discard with confirmation | Cancel tasks and clean partial outputs. |
| Storage/export failure | Keep original and retry path | Remove incomplete output; retain source by policy. |
| Thermal/memory pressure | Reduce processing rate or defer analysis | Measure the degraded path on hardware. |
| App leaves capture screen | Stop/release ownership unless the target has a documented active route | Do not leak camera/microphone ownership. |

## Persistence and system handoff

Persist the approved domain record, not raw framework objects. A record might contain:

- source reference;
- approved text or labels;
- original and edited values;
- provenance and model revision;
- review decision and timestamp;
- export/share history when the product needs it;
- deletion or retention date.

Use SwiftData or another selected persistence route only after the record has a schema and migration policy. Use Transferable or ShareLink only after a file or value representation is finalized. A widget, App Intent, or Live Activity should receive the minimum approved projection; do not expose raw audio, private transcripts, or sensitive images by default.

## Verification plan

### Fixtures

- permission not determined, denied, restricted, and revoked;
- camera unavailable or another app owns the capture device;
- microphone unavailable, silent input, noisy input, Bluetooth connect/disconnect;
- portrait and landscape capture;
- rapid start/stop and view disappearance;
- phone call, Siri, alarm, lock, background/foreground;
- long recording and low storage;
- corrupt or missing asset;
- no model/locale asset, partial transcript, low-confidence OCR;
- export cancellation, existing destination, and disk failure;
- large Dynamic Type, VoiceOver, Voice Control, Reduce Motion, Reduce Transparency, and RTL.

### Evidence boundaries

| Evidence | Proves | Does not prove |
| --- | --- | --- |
| Unit test | State transitions, token checks, cleanup decisions, parsers, and value normalization | Camera, microphone, codec, route, thermal, or system permission behavior. |
| Preview | Layout and review-state composition with mocked data | Real capture, media timing, audio routing, or model availability. |
| Simulator | Navigation, accessibility labels, layout, and many system-state fixtures | Physical camera/mic quality, orientation sensors, Bluetooth routes, or thermal behavior. |
| Signed physical device | Actual input/output hardware and performance for the tested device | All device families, App Store configuration, or production usage. |
| System surface run | Configured ShareLink, App Intent, widget, PiP, or background route in the tested target | A generic compile or simulator run. |
| Archive inspection | Target membership, entitlements, privacy strings, resources, and signing metadata | Successful user capture or model quality. |

## Sources

- [AVFoundation](https://developer.apple.com/documentation/avfoundation)
- [Setting up a capture session](https://developer.apple.com/documentation/avfoundation/setting-up-a-capture-session)
- [Requesting authorization to capture and save media](https://developer.apple.com/documentation/avfoundation/requesting-authorization-to-capture-and-save-media)
- [AVCaptureSession](https://developer.apple.com/documentation/avfoundation/avcapturesession)
- [AVCapturePhotoOutput](https://developer.apple.com/documentation/avfoundation/avcapturephotooutput)
- [AVCaptureMovieFileOutput](https://developer.apple.com/documentation/avfoundation/avcapturemoviefileoutput)
- [AVCaptureVideoDataOutput](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutput)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Audio Engine](https://developer.apple.com/documentation/avfaudio/audio-engine)
- [AVAudioFile](https://developer.apple.com/documentation/avfaudio/avaudiofile)
- [AVAsset](https://developer.apple.com/documentation/avfoundation/avasset)
- [AVAssetExportSession](https://developer.apple.com/documentation/avfoundation/avassetexportsession)
- [AVPlayer](https://developer.apple.com/documentation/avfoundation/avplayer)
- [AVKit](https://developer.apple.com/documentation/avkit)
- [VideoPlayer](https://developer.apple.com/documentation/avkit/videoplayer)
- [SpeechAnalyzer](https://developer.apple.com/documentation/speech/speechanalyzer)
- [SpeechTranscriber](https://developer.apple.com/documentation/speech/speechtranscriber)
- [Vision](https://developer.apple.com/documentation/vision)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [SwiftData](https://developer.apple.com/documentation/swiftdata)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [ShareLink](https://developer.apple.com/documentation/swiftui/sharelink)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Playing video](https://developer.apple.com/design/human-interface-guidelines/playing-video)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
