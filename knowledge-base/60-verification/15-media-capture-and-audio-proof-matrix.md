# Media capture and audio proof matrix

## Evidence rule

Media features cross protected permissions, physical hardware, asynchronous callbacks, mutable graphs, files, model assets, and system surfaces. Verify each claim at the boundary where it matters. A compiling adapter or an attractive SwiftUI preview is not evidence that the camera, microphone, audio route, codec, or export destination works.

Record:

    claim -> target/configuration -> fixture -> evidence -> limits

## Claim matrix

| Claim | Minimum evidence | Useful fixture | Common false conclusion |
| --- | --- | --- | --- |
| Camera permission is requested correctly | Target privacy string, authorization-state tests, device run with fresh permission | Not determined, denied, restricted, revoked in Settings | A simulator prompt proves the usage description is truthful. |
| Microphone permission is requested correctly | Target privacy string, authorization-state tests, physical recording run | Not determined, denied, revoked | A movie with no audio track is still a valid audio capture. |
| Capture graph can be configured | Compiled target and logs/state from the selected device | Missing device, cannot add input/output, unsupported format | Creating AVCaptureSession proves the graph is valid. |
| Photo capture completes | Physical device, delegate completion, readable output, source metadata | Portrait/landscape, low light, rapid capture, storage failure | A live preview proves a photo was saved. |
| Movie capture completes | Physical device, start/stop completion, playable file, audio/video track inspection | Interruption, cancellation, low storage, long recording | Stop button press proves the file is finalized. |
| Live frames are bounded | Device measurement of queue policy, dropped-frame count, cancellation | Slow Vision/Core ML task, thermal pressure, rapid view dismissal | An always-responsive preview proves no frames were dropped. |
| Frame orientation is correct | Device fixtures in portrait/landscape/front/rear camera and inspected output | Rotations during capture, mirrored front camera | The UI orientation proves file orientation. |
| Audio route is correct | AVAudioSession route inspection on physical hardware | Speaker, receiver, wired headset, Bluetooth connect/disconnect | Category selection guarantees a particular microphone/output. |
| Interruption recovery works | Physical or controlled interruption run, state log, resumed/finished draft | Phone call, Siri, alarm, another audio app | A notification observer exists, therefore recovery works. |
| Audio engine graph is stable | Physical microphone run, format inspection, start/stop/rebuild evidence | Route change, media-services reset, input unavailable | An engine object can be created in a preview. |
| Playback is native and controllable | Local fixture through VideoPlayer or AVPlayerViewController, controls and state evidence | Buffering, bad URL, missing track, end, seek, captions | AVPlayer initialization proves the first frame is visible. |
| Aspect ratio is preserved | Device/simulator visual inspection at compact/regular sizes | 4:3, 16:9, ultrawide, letterboxed source | A fixed frame is acceptable for every asset. |
| Export is valid | Successful export completion, destination inspection, optional re-open | Existing destination, cancellation, low disk, unsupported preset | A file URL exists, therefore the export succeeded. |
| Partial output is cleaned | Failure/cancel fixture and filesystem assertion | Cancellation while writing, disk full | Retrying over a partial file is idempotent. |
| Speech input is available | Permission, locale/model asset state, physical audio fixture | Unsupported locale, missing asset, partial/final results | A transcript string proves the selected locale/model is available in release. |
| OCR/model result is reviewable | Source-linked proposal UI and accept/edit/reject test | Low confidence, empty result, wrong orientation | A high confidence value proves domain truth. |
| AI remains on device when promised | Architecture review, network instrumentation, target configuration, device run | Offline mode, model unavailable, fallback attempt | Using a local API automatically means no data leaves the device. |
| Review prevents accidental side effects | UI test and domain test from proposal to approval | Tap-through, cancel, edit, reject, duplicate acceptance | Model completion automatically authorizes save/share/publish. |
| Accessibility works | VoiceOver, Voice Control, Switch Control, Full Keyboard Access task runs | Start, stop, review, edit, accept, discard, share | Accessibility labels alone prove task completion. |
| Reduced effects work | Device/simulator accessibility settings and task run | Reduce Motion, Reduce Transparency, Differentiate Without Color | A glass surface is accessible at the default setting. |
| Thermal and memory envelope is acceptable | Release-like physical-device profiling and repeated-run metrics | Long capture, analysis backlog, large export, older device | A short Debug run on the newest device proves production performance. |
| Release configuration is complete | Archive inspection of privacy, entitlements, target membership, resources, and signing | Clean archive, TestFlight install, configured system surface | Simulator success proves the archive is configured. |

## State-transition tests

Test the following transitions with deterministic value fixtures:

    idle -> requestingAccess -> denied
    idle -> requestingAccess -> configuring -> unsupported
    configuring -> ready -> capturing -> stopping -> sourceFinalized
    capturing -> interrupted -> paused -> resumed
    capturing -> runtimeError -> rebuilding -> ready
    sourceFinalized -> analyzing -> provisional -> final
    analyzing -> modelUnavailable -> reviewOriginal
    review -> exporting -> completed
    exporting -> cancelled -> review
    exporting -> failed -> sourceRetained

Assert that:

- a stale session token cannot publish into a new capture;
- cancellation stops analysis and does not show an error alert for a normal user dismissal;
- a continuation or delegate stream finishes exactly once;
- partial exports are removed or quarantined;
- a denied permission never causes a framework start attempt;
- an interrupted audio route does not claim that recording continued;
- a final transcript does not overwrite a user edit without an explicit merge policy;
- a duplicate callback cannot create two approved records.

## Physical-device fixture matrix

| Fixture | Observe | Store as evidence |
| --- | --- | --- |
| Rear camera portrait | Focus, exposure, orientation, preview, photo file | Device model/OS, settings, source/output metadata, result screenshot. |
| Front camera portrait | Mirroring, orientation, framing, permission | Device model/OS, connection settings, output inspection. |
| Movie with microphone | Audio track, route, duration, sync | Device route, track summary, playable output. |
| Wired or Bluetooth headset | Route change, input/output availability, interruption | Before/after route, state transition, user copy. |
| Phone call or system interruption | Pause/stop policy, draft validity, recovery | Event, pre/post state, audio/video file status. |
| Slow analysis | Dropped frame policy, latency, cancellation | Frame count, processed count, drop count, peak memory. |
| Long recording | Storage, thermal, memory, UI responsiveness | Duration, file size, energy/thermal notes, export result. |
| Low-light and motion | Model quality, focus, preview legibility | Fixture conditions, observation quality, user review. |
| Dynamic Type and VoiceOver | Reading order, controls, text wrapping, action completion | Task transcript or screen recording with accessibility settings. |
| Reduce Motion/Transparency | Material and transition fallback | Before/after screenshots/video and state behavior. |

## Playback and export matrix

Test local and remote fixture categories separately:

- short video with audio;
- video without audio;
- audio-only file;
- variable duration and unknown duration;
- portrait, landscape, and ultrawide;
- unsupported or corrupt asset;
- interrupted network or delayed buffering;
- captions/subtitles or transcript;
- export to a new destination;
- export to an existing destination;
- cancellation during processing;
- insufficient storage;
- share handoff after successful completion.

For each run capture:

- player-item status and time-control state;
- ready-for-display state when video is used;
- current route and interruption state;
- export preset/output type;
- completion, cancellation, or error;
- final file existence, size, duration, and track summary;
- whether the original source remains intact.

## AI and provenance matrix

| Output | Required provenance | Review requirement |
| --- | --- | --- |
| Transcript | Source file/time range, locale, Speech module, provisional/final state | User can edit and approve; original audio remains available by policy. |
| OCR | Source image/frame, orientation/crop, Vision request/revision, confidence | User can correct text and reject uncertain fields. |
| Classification | Source ID, model version, input preprocessing, confidence | Do not infer identity or authorization; domain validation required. |
| Summary/title | Source observations, prompt/context version, model state | Show as a draft and preserve source text. |
| Exported media | Source asset ID, transformation/effect version, output metadata | Only finalized output reaches ShareLink or a system surface. |

## Release evidence packet

The release packet should include:

1. Target and deployment configuration.
2. Camera/microphone/speech usage strings and privacy manifest review.
3. Entitlements and background-mode decision.
4. Device matrix and unsupported fallback.
5. Test plan and fixtures.
6. Physical-device capture/audio results.
7. Playback/export results.
8. Accessibility and reduced-effects task results.
9. Performance, memory, dropped-frame, and thermal observations.
10. Archive inspection and TestFlight/system-surface evidence where applicable.

Do not replace a missing physical-device result with a preview, simulator screenshot, or documentation link.

## Sources

- [AVFoundation](https://developer.apple.com/documentation/avfoundation)
- [Requesting authorization to capture and save media](https://developer.apple.com/documentation/avfoundation/requesting-authorization-to-capture-and-save-media)
- [Setting up a capture session](https://developer.apple.com/documentation/avfoundation/setting-up-a-capture-session)
- [AVCaptureSession](https://developer.apple.com/documentation/avfoundation/avcapturesession)
- [AVCapturePhotoOutput](https://developer.apple.com/documentation/avfoundation/avcapturephotooutput)
- [AVCaptureMovieFileOutput](https://developer.apple.com/documentation/avfoundation/avcapturemoviefileoutput)
- [AVCaptureVideoDataOutput](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutput)
- [Dropping late video frames](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutput/alwaysdiscardslatevideoframes)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Handling audio interruptions](https://developer.apple.com/documentation/avfaudio/handling-audio-interruptions)
- [Responding to audio route changes](https://developer.apple.com/documentation/avfaudio/responding-to-audio-route-changes)
- [Audio Engine](https://developer.apple.com/documentation/avfaudio/audio-engine)
- [AVAsset](https://developer.apple.com/documentation/avfoundation/avasset)
- [AVAssetExportSession](https://developer.apple.com/documentation/avfoundation/avassetexportsession)
- [AVPlayer](https://developer.apple.com/documentation/avfoundation/avplayer)
- [AVPlayerViewController](https://developer.apple.com/documentation/avkit/avplayerviewcontroller)
- [VideoPlayer](https://developer.apple.com/documentation/avkit/videoplayer)
- [SpeechAnalyzer](https://developer.apple.com/documentation/speech/speechanalyzer)
- [SpeechTranscriber](https://developer.apple.com/documentation/speech/speechtranscriber)
- [Vision](https://developer.apple.com/documentation/vision)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Swift Testing](https://developer.apple.com/documentation/testing)
- [XCTest](https://developer.apple.com/documentation/xctest)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Playing video](https://developer.apple.com/design/human-interface-guidelines/playing-video)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines)
