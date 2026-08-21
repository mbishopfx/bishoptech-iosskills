# AVFoundation media pipeline

## Scope

This deep dive is the route map for apps that capture, play, inspect, transform, export, or enrich audiovisual media on Apple platforms. SwiftUI owns the user-facing state and composition. AVFoundation, AVFAudio, AVKit, Core Media, and the selected analysis framework own the media pipeline.

The useful mental model is:

    permission -> device/input -> session -> connection -> output -> bounded handoff -> reviewable asset -> optional enrichment -> approved record -> export or system surface

The pipeline is not one object and it is not one task. Each boundary has its own availability, cancellation, privacy, and evidence requirements.

## Choose the narrowest framework route

| Outcome | Primary route | Add only when needed | Boundary to preserve |
| --- | --- | --- | --- |
| Preview a camera | AVCaptureSession with AVCaptureVideoPreviewLayer | SwiftUI bridge or a custom preview surface | A preview proves rendering, not successful photo/movie capture or file persistence. |
| Take a photo | AVCapturePhotoOutput | Vision, Core Image, PhotosUI, or a local review model | The photo delegate owns the completed capture result; the button action does not. |
| Record a movie | AVCaptureMovieFileOutput for a high-level file route, or sample-buffer writing for deliberate control | AVAssetExportSession, AVAssetReader, AVAssetWriter | Stop, failure, cancellation, orientation, audio track presence, and partial-file cleanup are part of recording. |
| Inspect live frames | AVCaptureVideoDataOutput | Vision, Core ML, Metal, or a custom bounded processor | The output delegate needs a frame-drop and cancellation policy. |
| Record microphone audio | AVAudioSession plus AVAudioEngine or a file recorder route | SpeechAnalyzer, SoundAnalysis, or custom DSP | Category, mode, activation, interruptions, route changes, and microphone permission are explicit. |
| Play local or remote media | AVPlayer and AVPlayerItem | AVKit VideoPlayer or AVPlayerViewController | Readiness, buffering, end, failure, audio route, and background policy are separate states. |
| Transcode or trim | AVAsset and AVAssetExportSession | AVAssetReader/AVAssetWriter or VideoToolbox | The exported file is not valid until the export completion state succeeds. |
| Recognize speech | SpeechAnalyzer and SpeechTranscriber | Foundation Models for an optional reviewed transformation | Transcription is a proposal with a source range and model/locale state, not an approved record. |
| Read text or objects | Vision request handlers or a Core ML model | SwiftData or a system surface after review | An observation is not identity, permission, medical meaning, or business truth. |

## Ownership map

| Owner | Owns | Must not silently own |
| --- | --- | --- |
| Main actor and SwiftUI model | User actions, visible state, accessibility labels, review decisions, and navigation | Blocking session work, raw sample buffers, mutable AVAudioEngine graphs, or implicit capture lifetime. |
| Capture/session coordinator | Session graph, device inputs, outputs, connections, start/stop, interruption recovery, and frame policy | User-approved domain records or irreversible side effects. |
| Audio-session coordinator | Category, mode, options, activation/deactivation, current route, interruptions, and route changes | A promise that a preferred microphone or Bluetooth route exists. |
| Media processor | Asset loading, sample conversion, bounded analysis, timestamps, cancellation, and output validity | UI truth or automatic approval of generated content. |
| Review model | Source reference, observation/proposal, confidence or quality, edits, and accept/reject state | New capture permissions or hidden network upload. |
| Export/share boundary | Finalized file, destination, progress, cancellation, and cleanup | Assuming a file URL means the user has saved, shared, or published the media. |

## Capture-session lifecycle

Configure a capture session as a graph. An input is a camera or microphone device. An output is a photo, movie, preview, metadata, or sample-buffer destination. Connections describe compatible media paths. The session is the coordinator for that graph.

Use this sequence:

1. Explain the immediate user benefit before requesting access.
2. Read the current authorization state for each media type.
3. Request only the permission needed for the action.
4. Select a supported device and check that the target input can be added.
5. Create inputs and outputs.
6. Call beginConfiguration before graph changes.
7. Add only outputs and connections the feature needs.
8. Apply format, orientation, stabilization, or high-resolution choices before the running contract requires them.
9. Call commitConfiguration.
10. Start or stop the session on its designated serial session queue.
11. Publish a small value state to the main actor.
12. Tear down the session and any analysis task when the feature no longer owns the resource.

The session queue is not a reason to make every object global. Give one coordinator ownership of one graph and make replacement explicit. A new capture request should either finish or cancel the previous request; two owners should not compete for the same camera or microphone.

AVCaptureSession.startRunning is blocking work. Keep configuration and start/stop off the main actor. The SwiftUI layer should receive states such as idle, requesting access, configuring, ready, running, interrupted, stopping, finished, unsupported, denied, or failed.

## Output selection

### Still photos

AVCapturePhotoOutput is the high-level still-image route. It supports ordinary photos and other documented photography features. Configure output capabilities before the session runs when a feature requires a capture-pipeline change. A capture request is asynchronous; the delegate or async adapter must own the completion and report capture errors, processing errors, and the final file or pixel result.

Keep the source orientation, capture time, color-space choice, metadata policy, and source identifier with the review draft. If the app rotates or crops the image, record that transformation instead of presenting the transformed image as if it were the original.

### Movies

AVCaptureMovieFileOutput is the simplest file-oriented route when the product can accept its high-level behavior. A movie is not complete when recording starts and it is not necessarily ready when stop is tapped. Use the delegate completion to distinguish a finalized file from a failure or cancellation. Remove or quarantine partial output according to the product’s retention policy.

Use a sample-buffer writing route only when the product really needs custom synchronization, custom encoding, live analysis, or a container policy that the high-level file output cannot own. That route makes timestamps, track interleaving, format descriptions, writer readiness, completion, and failure your responsibility.

### Live video samples

AVCaptureVideoDataOutput is a stream of sample buffers. The output delegate must be fast enough for the selected frame policy. If the feature needs current-frame guidance, dropping late frames can be correct. If every frame is evidence or part of an archival result, dropping is not acceptable without changing the product contract.

Choose one of these policies before implementation:

| Policy | Appropriate for | Risk |
| --- | --- | --- |
| Process every sample | Measurement, archival, or deterministic frame sequence | Memory and latency can grow if processing is slower than capture. |
| Discard late frames | Live preview, guidance, or current-state recognition | A user may never see an intermediate event; measure dropped frames. |
| Keep newest bounded sample | UI indicators and responsive AI assistance | The result can be stale relative to a prior frame; publish frame time and session token. |
| Reduce capture format or rate | Thermal or battery constrained features | Lower fidelity can change model quality; make the tradeoff visible in evaluation. |

Never put an unbounded model queue behind a capture delegate. Retain only the sample data that the selected API contract permits, copy into a safe value representation when needed, and cancel processing when the session token changes.

## Audio-session lifecycle

AVAudioSession tells the system how the app intends to use audio. The default session does not record. Select category, mode, route-sharing policy, and options for the product behavior rather than choosing a category because it happens to make a sample play.

The typical recording route is:

1. Check microphone authorization.
2. Configure the category, mode, and options.
3. Register interruption and route-change observation.
4. Activate the session immediately before recording or playback needs it.
5. Inspect the current input/output route and format.
6. Start the engine, recorder, or player.
7. Pause or stop for interruption and decide whether the draft is resumable.
8. Handle route changes by re-reading the route and, when necessary, rebuilding the graph.
9. Stop the engine or recorder.
10. Deactivate the session when the product no longer owns audio.

Apple’s audio-session documentation recommends setting category and mode together when possible. Deferring activation avoids interrupting another audio app before the user actually starts the media action. The chosen category does not guarantee a hardware route, and Bluetooth, wired, speaker, receiver, and input availability must be inspected at runtime.

An interruption is a state transition. Preserve the recording or playback position, show the user what happened, and resume only if the interruption ended and the current route remains suitable. Handle media-services reset and graph failure as rebuild paths, not as generic alerts.

## Playback and review

Use AVPlayer for a controllable player model. Use SwiftUI VideoPlayer when the native SwiftUI playback surface is sufficient. Use AVPlayerViewController when the product benefits from the system player interface and its documented playback integrations. Use a custom surface only when the user outcome needs controls or composition the system player cannot provide.

Track at least:

- asset loading or item replacement;
- player-item status;
- time control status;
- buffering or waiting;
- ready-for-display for video;
- end-of-playback;
- failure and retry;
- selected audio route;
- captions/subtitles and alternate tracks when relevant;
- user play, pause, seek, and dismissal intent.

The player being created is not proof that the first frame is visible. A player item being ready is not proof that audio can play on the current route. A VideoPlayer preview is not proof of background playback, Picture in Picture, AirPlay, or release configuration.

Follow the HIG: preserve the original aspect ratio, prefer the system player when it fits, provide obvious play/pause controls, and do not communicate important information through audio alone. A transcript or caption view is a first-class alternate route, not a decorative afterthought.

## Assets, export, and file validity

AVAsset is a time-based media description. Loading tracks, duration, natural size, and metadata can be asynchronous. Do not assume every asset has a video track, audio track, known duration, or a compatible codec.

For an export:

1. Validate that the source asset and required tracks exist.
2. Choose a supported preset and output type for the target.
3. Choose a destination URL that is not already occupied unless replacement is explicit.
4. Start the export and expose progress or an indeterminate processing state.
5. Observe completion, failure, cancellation, and any error.
6. Treat the output as shareable only after successful completion.
7. Remove partial output on cancellation or failure when it is not a useful draft.
8. Re-open or inspect the result when the product needs a stronger validity check.
9. Hand the finalized URL to Transferable, ShareLink, a document exporter, or the selected system surface.

For reader/writer or VideoToolbox routes, add explicit state for format descriptions, pixel formats, timestamps, writer readiness, pending frames, completion, invalidation, and container metadata. Codec availability, color space, orientation, and thermal performance are device/asset facts to measure.

## Bounded analysis and on-device intelligence

Media can feed Speech, Vision, Core ML, Sound Analysis, Natural Language, or Foundation Models. Keep the analysis after the source has a stable identifier and a bounded representation:

    captured source -> normalized sample/file -> analysis task -> observation/proposal -> user review -> approved record

SpeechAnalyzer accepts one input sequence at a time and produces asynchronous module results. SpeechTranscriber availability, supported locales, and installed assets are runtime gates. Vision and Core ML requests need orientation, input dimensions, model/request revision, cancellation, and a frame policy.

For every generated proposal, retain:

- source asset or frame identifier;
- capture time and orientation;
- framework, model, locale, and revision;
- preprocessing and crop policy;
- confidence, quality, or match state when supplied;
- provisional or final state;
- user edits and accept/reject decision;
- retention and deletion decision.

On-device processing reduces network exposure but does not remove permission, privacy, data minimization, accessibility, or domain-validation requirements. A transcription, OCR result, classification, or summary must not directly execute a consequential action without the product’s validation and approval boundary.

## Swift concurrency boundary

Use Swift concurrency for the value/state handoff and keep legacy delegate/queue boundaries local to the framework adapter. A serial session queue can protect synchronous AVFoundation graph operations. An actor can own mutable domain state and cancellable analysis tasks. Do not send a mutable framework graph across actors just to make the compiler quiet.

The safe pattern is:

    capture delegate -> bounded value handoff -> cancellable task -> actor/domain result -> MainActor UI projection

Use a bounded AsyncStream when a stream is the right abstraction; never use its default unbounded buffer for high-rate frames or audio. Finish the continuation exactly once. Store and cancel unstructured tasks when the view or coordinator no longer owns them. After every await inside an actor, re-check the session token and relevant state because another operation may have completed.

## Privacy and configuration ledger

Record these before implementation:

| Item | Question |
| --- | --- |
| Camera permission | Why does this screen need live camera access now? |
| Microphone permission | Why does this action need audio input now? |
| Speech permission | Is the user expecting transcription, and what is retained? |
| File/photo access | Is the source imported, captured, or exported, and who owns the resulting file? |
| Background mode | Is the product actually entitled and configured for the specific background audio or processing route? |
| Network | Is media ever uploaded, and is that necessary for the outcome? |
| Logging | Are raw frames, audio, transcripts, paths, or metadata excluded from logs? |
| Retention | When are source media, temporary exports, and proposals deleted? |
| Hardware | Which camera, microphone, route, codec, and device families are required? |

Usage descriptions must be truthful and specific. Do not request camera or microphone access during app launch merely because a later screen may need it.

## Verification route

Compile the smallest target slice, then prove the pipeline in increasing scope:

1. Unit-test the state machine, source identifiers, frame policy, cancellation, and export cleanup with synthetic values.
2. Preview the SwiftUI review states with mocked media metadata and explicit permission/unsupported fixtures.
3. Run simulator tests for navigation, layout, Dynamic Type, VoiceOver labels, review editing, and failure presentation.
4. Use a signed physical device for camera, microphone, orientation, audio routes, focus, exposure, dropped frames, thermal behavior, and actual model latency.
5. Test system surfaces, background audio, Picture in Picture, AirPlay, and export destinations only in their configured target and environment.
6. Inspect the release archive, privacy strings, entitlements, target membership, and media resources separately from runtime evidence.

## Sources

- [AVFoundation](https://developer.apple.com/documentation/avfoundation)
- [Setting up a capture session](https://developer.apple.com/documentation/avfoundation/setting-up-a-capture-session)
- [Requesting authorization to capture and save media](https://developer.apple.com/documentation/avfoundation/requesting-authorization-to-capture-and-save-media)
- [AVCaptureSession](https://developer.apple.com/documentation/avfoundation/avcapturesession)
- [AVCaptureDevice](https://developer.apple.com/documentation/avfoundation/avcapturedevice)
- [AVCaptureDeviceInput](https://developer.apple.com/documentation/avfoundation/avcapturedeviceinput)
- [AVCapturePhotoOutput](https://developer.apple.com/documentation/avfoundation/avcapturephotooutput)
- [AVCaptureMovieFileOutput](https://developer.apple.com/documentation/avfoundation/avcapturemoviefileoutput)
- [AVCaptureVideoDataOutput](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutput)
- [AVCaptureOutput](https://developer.apple.com/documentation/avfoundation/avcaptureoutput)
- [AVCaptureConnection](https://developer.apple.com/documentation/avfoundation/avcaptureconnection)
- [AVCaptureVideoPreviewLayer](https://developer.apple.com/documentation/avfoundation/avcapturevideopreviewlayer)
- [Dropping late video frames](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutput/alwaysdiscardslatevideoframes)
- [AVAsset](https://developer.apple.com/documentation/avfoundation/avasset)
- [AVAssetExportSession](https://developer.apple.com/documentation/avfoundation/avassetexportsession)
- [AVPlayer](https://developer.apple.com/documentation/avfoundation/avplayer)
- [AVPlayerItem](https://developer.apple.com/documentation/avfoundation/avplayeritem)
- [AVFAudio](https://developer.apple.com/documentation/avfaudio)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Setting the audio session category](https://developer.apple.com/documentation/avfaudio/avaudiosession/setcategory%28_%3Amode%3Aoptions%3A%29)
- [Audio Engine](https://developer.apple.com/documentation/avfaudio/audio-engine)
- [AVAudioInputNode](https://developer.apple.com/documentation/avfaudio/avaudioinputnode)
- [AVAudioFile](https://developer.apple.com/documentation/avfaudio/avaudiofile)
- [AVAudioPCMBuffer](https://developer.apple.com/documentation/avfaudio/avaudiopcmbuffer)
- [AVKit](https://developer.apple.com/documentation/avkit)
- [VideoPlayer](https://developer.apple.com/documentation/avkit/videoplayer)
- [AVPlayerViewController](https://developer.apple.com/documentation/avkit/avplayerviewcontroller)
- [Playing video content in a standard user interface](https://developer.apple.com/documentation/avkit/playing-video-content-in-a-standard-user-interface)
- [SpeechAnalyzer](https://developer.apple.com/documentation/speech/speechanalyzer)
- [SpeechTranscriber](https://developer.apple.com/documentation/speech/speechtranscriber)
- [Vision](https://developer.apple.com/documentation/vision)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Playing video](https://developer.apple.com/design/human-interface-guidelines/playing-video)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines)
- [Swift language guide](https://docs.swift.org/swift-book/)
