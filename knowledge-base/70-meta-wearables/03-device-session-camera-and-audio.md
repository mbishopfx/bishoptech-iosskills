# Device sessions, camera, and audio boundaries

The current DAT iOS route is session-based. A session owns the connection to a
selected device; a `Camera` owns the camera resource; its `Stream` owns video
frames and photo capture. Keep these lifetimes explicit so a paused, doffed,
thermally limited, or stopped device cannot be treated as an active source.

## Session lifecycle

| State | Meaning | App behavior |
| --- | --- | --- |
| `idle` | Session exists but is not running | Show a deliberate Start action. |
| `starting` | DAT is negotiating the device path | Show progress; do not add capabilities yet. |
| `started` | Session can accept capabilities | Attach `Camera` or `Display`. |
| `paused` | Device temporarily suspended the experience | Hold work; wait for the SDK to resume or stop. |
| `stopping` | Resources are being released | Disable actions; await terminal state. |
| `stopped` | Session is terminal | Release listeners and create a new session to restart. |

The device can pause or stop because of user gestures, another app, folding or
doffing, connectivity, battery, thermal state, peak power, or compatibility.
Use the SDK's typed state/error streams and device state rather than inferring a
cause from a missing frame.

## Current camera route

The current iOS 0.9.0 shape is:

```swift
let session = try Wearables.shared.createSession(
    deviceSelector: AutoDeviceSelector(wearables: Wearables.shared)
)
try session.start()

// Wait for session.stateStream() == .started.
let camera = try session.addCamera(
    config: StreamConfiguration(
        videoCodec: .raw,
        resolution: .medium,
        frameRate: 24
    )
)
let stream = camera.stream
stream.start()
```

The reusable [iOS camera starter](../skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-ios-camera-starter/MetaWearablesCameraStarter.swift)
turns this shape into a bounded adapter with explicit permission, first-frame,
photo-sink, stream-error, and child-before-parent teardown events. Its compile
receipt is target-specific and its photo sink is a phone-local data boundary.

This is a shape to typecheck against the pinned package; it is not a claim that
the snippet alone compiles in every project. The old direct
`addStream(config:)` route was removed in 0.9.0.

The current 0.9.0 migration also adds a `CameraState`/publisher surface and
makes the `Camera` the owner of its child stream. `Camera.stop()` is the
capability teardown boundary. Doff can report `StreamError.hingesClosed`, and
photo failures use the current stream error model rather than the removed
older `CaptureError` type; verify exact enum names against the selected tag.

## Stream configuration and backpressure

The official iOS skill lists these current presets:

| Setting | Values in the public route | Design implication |
| --- | --- | --- |
| Resolution | low `360x640`, medium `504x896`, high `720x1280` | Higher resolution is not automatically better over a constrained link. |
| Frame rate | `2`, `7`, `15`, `24`, `30` | Choose the smallest rate that serves the user task and thermal budget. |
| Codec | raw or compressed HEVC (`hvc1` in the changelog) | Raw frames are convenient for image processing; compressed/background behavior needs a separate decode/recording route. |

The documented adaptive behavior may reduce resolution and frame rate when
bandwidth is constrained. Do not treat the requested configuration as the
observed configuration; record actual stream state, frame metadata, drops,
thermal changes, and user-visible fallback.

Background capture is not a general permission implied by the camera API. The
current Camera Access sample/changelog contains route- and option-sensitive
wording: the preview session can end when the app backgrounds, while optional
sound-in-video behavior is discussed separately. Treat continuation while
backgrounded as `to-verify` for the exact target and build.

## Photo and frame handling

`VideoFrame` and photo data are observations. Normalize them off the main actor
when processing is expensive, retain only what the product needs, and bind a
result to the session/device/source revision before displaying or committing it.
Photo capture failures surface through the current stream error model rather
than the removed older `CaptureError` type. Recheck the exact enum cases in the
pinned API before writing exhaustive switches.

Stop order matters:

```text
stop preview/recording -> Camera.stop() -> DeviceSession.stop()
```

The current Camera capability owns its child stream and stopping the camera
cascades to the child. A real app still needs to cancel frame tasks, clear
listener tokens, close files, and release decoded images.

## Audio boundary

The current full public DAT guide documents audio through standard Bluetooth
profiles rather than a guessed `MWDATAudio` import:

- A2DP is output-only and is the higher-fidelity route for playback/TTS.
- HFP is bidirectional and delivers documented 8 kHz mono microphone audio from
  the glasses through the iOS audio stack.
- For a camera + HFP feature, add the DAT camera, configure/start the HFP
  `AVAudioSession` route, wait for the route to settle and verify a
  `bluetoothHFP` input, then start the camera stream. Recheck this ordering in
  the current official guide before implementation.

Use iOS microphone consent, a visible/stoppable recording state, bounded audio
processing, interruption/route recovery, and explicit retention/network rules.
The documented HFP route is source evidence; it is not physical audio quality,
latency, speaker routing, or transcription proof. Test those on the named pair
and firmware.

## Sources

- [DAT iOS camera streaming skill](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/camera-streaming/SKILL.md)
- [DAT iOS session lifecycle skill](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/session-lifecycle/SKILL.md)
- [DAT iOS changelog 0.9.0](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [DAT iOS API reference](https://wearables.developer.meta.com/docs/reference/ios_swift/dat/latest)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [AVFoundation](https://developer.apple.com/documentation/avfoundation)
- [Speech](https://developer.apple.com/documentation/speech)
- [Full Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
