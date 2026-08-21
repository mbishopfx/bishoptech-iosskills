# AVFoundation and Media

## Capability

AVFoundation is the native route for inspecting, playing, capturing, processing, and exporting audiovisual media. It can sit underneath a polished SwiftUI surface, but the media pipeline remains asynchronous, permission-sensitive, and lifecycle-dependent.

## Choose the media route

| Product need | First framework route | Important boundary |
| --- | --- | --- |
| Play a local or remote asset | `AVPlayer` and the media playback APIs | Buffering, interruption, route changes, and background policy are part of the feature. |
| Capture photos or video | `AVCaptureSession` with the appropriate device input and output | Camera/microphone permission, hardware support, and session lifecycle. |
| Capture microphone audio | `AVAudioSession` plus an audio capture/engine route | Audio category, route changes, interruptions, and microphone permission. |
| Edit or transcode a file | `AVAsset`, reader/writer, or export-session APIs | Codec, container, duration, disk space, cancellation, and export errors. |
| Analyze frames or samples | Capture output or asset reader plus Vision/Core ML/Metal | Backpressure, frame rate, memory, and on-device processing cost. |

## Capture-session sequence

The smallest camera feature usually follows this order:

1. Explain the user-facing reason for camera or microphone access.
2. Request the relevant authorization at the moment the feature needs it.
3. Check device and input availability.
4. Create an `AVCaptureSession` and configure inputs and outputs between `beginConfiguration()` and `commitConfiguration()`.
5. Connect a preview or data output to the SwiftUI/UIView bridge.
6. Start and stop the session on an appropriate queue, respecting view and app lifecycle.
7. Turn captured output into a reviewable domain draft rather than silently saving it.

`AVCaptureSession` coordinates access to capture infrastructure; inputs, outputs, and connections define what the session can actually do. A preview is not proof that photo/video capture, audio sync, orientation, or saving succeeds.

`startRunning()` is blocking work. Keep session configuration and start/stop operations off the main queue, use a serial session queue, and publish only state/value changes back to the main-actor UI. Configure changes between `beginConfiguration()` and `commitConfiguration()` so the capture graph changes atomically.

Observe `isRunning`, `isInterrupted`, runtime-error notifications, interruption start/end, and the actual active connection. When the session is interrupted or a camera becomes unavailable, render a recoverable state and stop analysis that depends on frames. Do not blindly restart after every interruption without checking permission, route, and the product’s foreground/background contract.

## Frame backpressure and analysis handoff

`AVCaptureVideoDataOutput` can deliver frames for Vision, Core ML, or a custom renderer. Its `alwaysDiscardsLateVideoFrames` policy controls what happens when the delegate queue is busy. Dropping late frames is often appropriate for current-frame guidance; it is not appropriate when every frame is part of an archival, measurement, or forensic workflow. Choose the policy from the product’s data contract, measure dropped frames, and cancel downstream analysis when the view or session stops.

The capture delegate should not perform unbounded model work inline. Keep the delegate fast, use an isolated bounded handoff, and avoid retaining sample buffers beyond their useful lifetime. For a reviewable result, attach the source frame/file identifier, capture time, orientation, model/framework version, and review state rather than logging or uploading raw media by default.

## Audio-session sequence

For recording, playback, or both, configure `AVAudioSession` for the product’s actual behavior. Choose category, mode, and options deliberately, activate the session at the right time, and respond to interruptions, route changes, media-services resets, and unavailable hardware. Do not assume the built-in speaker, microphone, or Bluetooth route is always present.

## SwiftUI boundary

Keep framework objects behind an observable controller or actor/service boundary. The view should render states such as:

`idle -> requesting permission -> preparing -> ready -> capturing/playing -> paused/interrupted -> finished/error`

Do not make `View.body` own a capture session’s lifecycle. A bridge such as `UIViewControllerRepresentable` or a dedicated observable controller can coordinate UIKit/AVFoundation with SwiftUI while keeping teardown explicit.

## Permissions and privacy

- Add truthful camera and microphone usage descriptions before requesting access.
- Request only the media access needed for the current action.
- Treat captured audio, video, location metadata, and embedded identifiers as potentially sensitive.
- Define whether media stays on device, is uploaded, is shared, or is deleted after processing.
- If media is sent into on-device AI, bound the input and retain the original only when the product needs traceability.

## API route matrix

Select the highest-level Apple API that owns the user outcome, then expose a value/state adapter to SwiftUI. Do not make a view or a camera callback the media model.

| Outcome | API seam | Domain handoff | Main lifecycle/configuration gate |
| --- | --- | --- | --- |
| Show a native player | `AVPlayer`, `AVPlayerItem`, and optionally `AVPlayerViewController` | Asset ID/URL, playback state, time, error, selected route | Buffering/readiness, interruption, route change, external playback, background policy, and release media entitlement/transport. |
| Capture a photo | `AVCaptureSession` + `AVCaptureDeviceInput` + `AVCapturePhotoOutput` | Photo file/reference, orientation, metadata, capture time, review state | Camera authorization, device/input availability, session queue, capture delegate completion, disk failure, and physical camera proof. |
| Capture a movie | `AVCaptureMovieFileOutput` or a deliberately bounded sample-buffer writer | File/reference, duration, audio/video tracks, export state | Microphone/camera authorization, storage, interruption, orientation, stop/cancel, partial-file cleanup, and physical device. |
| Analyze live frames | `AVCaptureVideoDataOutput` + bounded Vision/Core ML/Metal handoff | Frame ID/time, orientation, observation/prediction, latency, dropped-frame count | Serial session queue, `alwaysDiscardsLateVideoFrames` policy, cancellation, backpressure, thermal/memory, and device measurement. |
| Record or play audio | `AVAudioSession` plus `AVAudioEngine`/player route | Audio-session state, route, interruption, recording/playback status | Category/mode/options, activation, route changes, phone-call interruption, microphone authorization, and physical audio route. |
| Export or transcode | `AVAsset`, `AVAssetExportSession`, reader/writer or VideoToolbox when low-level control is required | Progress, output URL, codec/container metadata, cancellation/error | File coordination, disk space, codec availability, cancellation cleanup, progress, and signed target configuration. |
| Render an image effect | Core Image or an explicit video/rendering path | Rendered asset/reference, color space/orientation, effect version | `CIContext`/filter ownership, color management, memory, cancellation, and output write proof. |

## Capture graph and queue ownership

Record the graph before implementation:

`device -> input -> session -> connection -> output -> bounded handoff -> domain proposal -> review/export`

The session queue owns configuration and `startRunning()`/`stopRunning()`. Each output delegate has a bounded policy: either process every sample, explicitly drop late frames, or coalesce to the newest sample. The analysis task owns cancellation and must not retain a `CMSampleBuffer` or mutable framework object longer than the selected API contract permits. The main actor owns only published state and user actions.

Use this state model for a real-time feature:

`idle -> requestingAccess -> configuring -> ready -> running -> interrupted -> resuming | stopping -> finished`

with separate `permissionDenied`, `unsupported`, `runtimeError`, `systemPressure`, `backgroundUnavailable`, `routeUnavailable`, `storageFull`, `analysisBacklog`, and `cancelled` states. A frame delivered after the session token changes is stale; discard it rather than allowing an old task to publish into the new session.

## Audio session and media route matrix

| State/event | Required response |
| --- | --- |
| Permission not determined | Explain the immediate user benefit, request only the required media access, and wait for the result before configuring a dependent route. |
| Session inactive | Deactivate/release resources according to the product’s playback/recording policy; do not assume the app can keep the microphone or camera. |
| Audio interruption begins | Pause or stop safely, preserve position/draft state, and show that the route is interrupted rather than failed permanently. |
| Audio route changes | Re-read the current route, update UI/recording policy, and test Bluetooth/headset/speaker changes. |
| Camera unavailable in background | Stop or allow the system-preserved start request to resume only according to the documented capture behavior; never claim background camera capture. |
| Media services reset | Rebuild the affected session/player/engine and reconcile in-progress state; test a real reset path where possible. |
| Export cancelled or fails | Delete or quarantine partial output, retain the source/draft as appropriate, and make retry idempotent. |

Background audio, external playback, background processing, and camera capture are separate product routes. A background audio mode does not grant background camera access, and a preview layer does not prove that a file was captured or exported. Record each target capability, usage description, and physical-device check in the project configuration ledger.

## Verification route

- Test permission granted, denied, restricted, and revoked in Settings.
- Test camera orientation, interruptions, background/foreground transitions, phone calls, Bluetooth route changes, and low storage.
- Test real lighting, focus, motion, noisy audio, and multiple device families on physical hardware.
- Test capture queues under slow Vision/Core ML work, dropped-late-frame policy, cancellation, session interruption, runtime errors, and rapid start/stop.
- Verify cancellation and partial-file cleanup for every export path.
- Measure capture and processing latency, memory, thermal behavior, and dropped frames before shipping a real-time feature.

## Sources

- [AVFoundation](https://developer.apple.com/documentation/avfoundation/)
- [Setting up a capture session](https://developer.apple.com/documentation/avfoundation/setting-up-a-capture-session)
- [Requesting authorization to capture and save media](https://developer.apple.com/documentation/avfoundation/requesting-authorization-to-capture-and-save-media)
- [AVCaptureDevice authorization](https://developer.apple.com/documentation/avfoundation/avcapturedevice/authorizationstatus%28for%3A%29)
- [AVCaptureSession](https://developer.apple.com/documentation/avfoundation/avcapturesession)
- [AVCaptureDevice](https://developer.apple.com/documentation/avfoundation/avcapturedevice)
- [AVCaptureDeviceInput](https://developer.apple.com/documentation/avfoundation/avcapturedeviceinput)
- [AVCapturePhotoOutput](https://developer.apple.com/documentation/avfoundation/avcapturephotooutput)
- [AVCaptureMovieFileOutput](https://developer.apple.com/documentation/avfoundation/avcapturemoviefileoutput)
- [AVCaptureConnection](https://developer.apple.com/documentation/avfoundation/avcaptureconnection)
- [AVCaptureVideoPreviewLayer](https://developer.apple.com/documentation/avfoundation/avcapturevideopreviewlayer)
- [AVCaptureVideoDataOutput](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutput)
- [Dropping late video frames](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutput/alwaysdiscardslatevideoframes)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [AVAudioEngine](https://developer.apple.com/documentation/avfaudio/avaudioengine)
- [AVPlayer](https://developer.apple.com/documentation/avfoundation/avplayer)
- [AVPlayerItem](https://developer.apple.com/documentation/avfoundation/avplayeritem)
- [AVAssetExportSession](https://developer.apple.com/documentation/avfoundation/avassetexportsession)
- [PhotosUI](https://developer.apple.com/documentation/photosui)
