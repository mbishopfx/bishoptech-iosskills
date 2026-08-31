---
name: meta-dat-camera-audio
description: Design and review Meta DAT camera and audio features with exact SDK-version checks, stream ownership, cancellation, AVFoundation boundaries, privacy-aware consent, and separate phone/mock/connected-glasses evidence. Use for wearable camera, microphone, preview, capture, transcription, or media-processing requests.
---

# Meta DAT camera and audio

Treat camera and audio as separate capability contracts with explicit ownership, consent, backpressure, cancellation, and evidence. A phone microphone or simulated frame is not a glasses microphone or camera result.

## Read before acting

- Inspect the actual DAT package version, target deployment, AVFoundation/AVAudioSession use, existing media pipeline, persistence, network upload, and background behavior.
- Read [device session, camera, and audio](../../../70-meta-wearables/03-device-session-camera-and-audio.md), [privacy and publishing](../../../70-meta-wearables/08-privacy-publishing-and-release.md), and [mock evidence](../../../70-meta-wearables/07-mockdevice-testing-and-evidence.md).
- Read the [on-device compliance and runtime contract](../../../70-meta-wearables/17-on-device-compliance-and-runtime-contract.md) for processing location, raw-media boundaries, HFP/A2DP labeling, retention, thermal behavior, and fallback.
- Read the [operational readiness and recovery route](../../../70-meta-wearables/18-operational-readiness-and-recovery.md) for companion, firmware, link, thermal/power, background, and recovery behavior around camera/audio sessions.
- Read the [application architecture and platform-boundaries route](../../../70-meta-wearables/19-application-architecture-and-platform-boundaries.md) for camera/audio capability ownership, bounded queues, session epochs, and phone fallback seams.
- Read [transport, audio, and runtime reliability](../../../70-meta-wearables/22-transport-audio-and-runtime-reliability.md) for Wi-Fi/local-network parity, Bluetooth/link state, HFP/A2DP route evidence, queue policy, thermal behavior, and bounded recovery.
- Refresh the official [DAT iOS camera/streaming skill](https://github.com/facebook/meta-wearables-dat-ios/tree/main/plugins/mwdat-ios/skills/camera-streaming), [debugging skill](https://github.com/facebook/meta-wearables-dat-ios/tree/main/plugins/mwdat-ios/skills/debugging), and [AVFoundation](https://developer.apple.com/documentation/avfoundation) / [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession) documentation.
- Verify the exact installed symbols and media types against the selected tag. Current 0.9.0 notes use `DeviceSession.addCamera(config:) -> Camera`, `Camera.stream`, `Camera.stop()`, and camera state; do not revive removed `addStream(config:)` examples. Also check `StreamError.hingesClosed`, current photo-failure cases, and the background-camera sample behavior.
- Start from the [source-aligned iOS camera coordinator](../meta-wearables-implementation-recipes/assets/meta-wearables-ios-camera-starter/MetaWearablesCameraStarter.swift) or [Android camera coordinator](../meta-wearables-implementation-recipes/assets/meta-wearables-android-camera-starter/MetaWearablesAndroidCameraStarter.kt) when scaffolding a concrete route. They are adapter seeds, not physical camera/audio proof.
- Use the [iOS MockDevice fixture](../meta-wearables-implementation-recipes/assets/meta-wearables-ios-mockdevice-starter/MetaWearablesMockDeviceStarter.swift) or [Android MockDevice fixture](../meta-wearables-implementation-recipes/assets/meta-wearables-android-mockdevice-starter/MetaWearablesAndroidMockDeviceStarter.kt) to make denied permission, file-feed, capture, fold/doff, tap, cancellation, and teardown cases deterministic before requesting camera or audio hardware evidence.

## Camera workflow

1. Gate on registration, session readiness, model/capability, user intent, and camera permission as required by the current release.
2. Build the camera configuration from supported values in the installed API. Record resolution, frame rate, format/codec, orientation, and expected latency; do not invent an unsupported combination.
3. Own the camera from session start through `Camera.stop()`/equivalent release. Cancel the consumer and stop the source on view exit, disconnect, error, and lifecycle transitions required by the SDK.
4. Bound buffering. Decide whether the consumer drops, coalesces, or blocks frames, and measure the effect on UI, memory, thermal load, and battery.
5. Keep conversion and inference off the UI thread. Preserve the source timestamp/ordering contract if downstream code needs it.
6. Test no-device, denied, interrupted, stale-session, slow-consumer, stop-while-streaming, and reconnect states.
7. Treat background continuation as a target-specific `to-verify` item; the
   current sample/changelog wording is not a blanket background-capture
   guarantee.

## Audio workflow

1. Establish the exact documented audio source before designing transcription or upload. The current public DAT guide documents HFP glasses microphone input through iOS audio APIs and A2DP playback; verify the package/guide revision and do not substitute an undocumented native module.
2. Distinguish phone microphone, HFP glasses microphone, A2DP playback, route changes, and a remote transcription result in names, permissions, logs, UI, and evidence.
3. Configure `AVAudioSession` for the actual phone/HFP path with the required usage description and route policy. For camera + HFP, follow the documented ordering and verify `bluetoothHFP`; do not present a phone route as glasses capture.
4. Define consent, recording indicator, pause/stop, retention, deletion, network transfer, vendor processing, and failure behavior before enabling audio.
5. Use manual text, phone mic, or an explicit unavailable state as fallback only when the product’s privacy and UX contract permits it.

## Fast path

Treat media as two independent slices: bounded camera/photo and an explicit audio route. For each, record owner, permission, buffer budget, stop order, phone fallback, and evidence; a working camera stream must not become a prerequisite for unrelated audio work.

## Required output

- exact SDK tag/commit and symbols verified;
- camera/audio capability and permission matrix;
- stream ownership and cancellation diagram;
- media format, buffering, and performance assumptions;
- phone-vs-glasses source labeling;
- privacy/data-flow table;
- mock, simulator, connected-device, and physical-device test evidence.

## Hard boundaries

- Never claim audio or camera support from a marketing page alone.
- Never send raw media to a service without a documented consent and retention path.
- Never persist raw media in fixtures, logs, crash payloads, or skill archives.
- Never let a successful phone-camera or mock-device test stand in for a glasses-camera test.
- Never hide an unavailable or permission-denied state behind a spinner.

## Related routes

- [DAT iOS integration](../meta-dat-ios-integration/SKILL.md)
- [DAT Display](../meta-dat-display/SKILL.md)
- [Privacy and publishing](../meta-wearables-privacy-publishing/SKILL.md)
- [Device proof](../meta-wearables-device-proof/SKILL.md)
- [On-device compliance](../meta-wearables-on-device-compliance/SKILL.md)
- [Operational readiness](../meta-wearables-operational-readiness/SKILL.md)
- [Application architecture](../meta-wearables-app-architecture/SKILL.md)
- [Transport/reliability](../meta-wearables-transport-reliability/SKILL.md)
- [Apple media and ML routes](../ios-media-ml-and-inputs/SKILL.md)

## Sources

- [Meta DAT iOS camera streaming skill](https://github.com/facebook/meta-wearables-dat-ios/tree/main/plugins/mwdat-ios/skills/camera-streaming)
- [Meta DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [Meta Wearables Device Access Toolkit announcement](https://developers.meta.com/blog/introducing-meta-wearables-device-access-toolkit/)
- [Apple AVFoundation](https://developer.apple.com/documentation/avfoundation)
- [Apple AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Apple privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- [Full Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
