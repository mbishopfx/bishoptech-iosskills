# DAT iOS API surface atlas

This is the public API and tooling inventory for the Meta Wearables Device
Access Toolkit. The current public iOS `main` snapshot is
`225f64ff1617e7acc8c407bb8d3ee132f7263d00`; the `0.9.0` tag resolves to
`9b1b83d791dfebff7afd452e924a256819094b64` (both checked on 2026-08-22).
The changelog identifies 0.9.0 as the 2026-08-03 release. Use the tag for a
reproducible package and `main` only as a separately labeled source-refresh
snapshot. The atlas also reflects the machine-readable Wearables Developer
Platform `v0.9` reference retrieved on 2026-08-22. It is an atlas for routing
and review, not a replacement for the selected package’s generated API
reference or a claim that every listed surface is available in every target.

## Authority and source conflicts

Use this order when sources disagree:

1. the exact package/tag and generated API reference used by the target;
2. the same release’s changelog and official samples;
3. the current public Developer Center and `llms.txt` index;
4. historical upstream skill prose and remembered signatures.

The public `llms.txt` currently says iOS 15.2+/Xcode 14+, while the 0.9.0 iOS
changelog says the package minimum is iOS 17.2. Treat the 0.9.0 package and
changelog as the build gate for a 0.9.0 target, and record this source conflict
until Meta publishes one consistent versioned requirement.

The upstream README and samples currently show `addCamera(config:)` guarded as
an optional result, while the changelog describes the camera capability as the
current replacement for the removed direct `addStream(config:)` route. Typecheck
the exact call against the pinned package; do not copy either shape into a
different release without checking.

The separate Web Apps sources also conflict: the public full-reference index
lists no text input, offline support, or back navigation, while the official Web
Web Apps toolkit `main` at commit `a2714f862c61b1ce9c6cb624fc7e4938087102db`
documents a text composer, service-worker/offline patterns, Escape/back,
extended gestures, and sensors. Keep those Web App features
`source-conflict`/`to-verify` until the authenticated docs/MCP result, target
firmware, and physical Display run agree.

## Public surface map

The full public platform index names these DAT surface families:

| Surface named by the current public index | Local implementation posture |
| --- | --- |
| `MWDATCore` | Confirmed iOS import in the upstream repo. Owns `Wearables`, registration, permissions, device discovery/selectors, `DeviceSession`, state, compatibility, and errors. |
| `MWDATCamera` | Confirmed iOS import. Owns `Camera`, `Stream`, `VideoFrame`, `PhotoData`, `StreamConfiguration`, frame/photo publishers, and capture. |
| `MWDATDisplay` | Confirmed iOS import. Owns `Display`, Displayable view components, input/button content, icons/images, and video. |
| `MWDATMockDevice` | Confirmed iOS import in the upstream MockDevice skill/sample. Owns simulated glasses, permissions, media feeds, gestures, and UI-test support. |
| `MWDATMockDeviceTestClient` | Confirmed 0.9.0 Swift package product. Test-process-only localhost MockDevice control; use the [portable iOS test-client starter](../skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-ios-mockdevice-test-client-starter/MetaWearablesMockDeviceTestClientStarter.swift) for the XCUITest boundary; it is not a runtime glasses capability or a substitute for physical evidence. |
| `MWDATDevice`, `MWDATMedia`, `MWDATState`, `MWDATLogger`, `MWDATMock`, `MWDATKey` | Named by the current machine-readable platform index; verify whether each is an importable product, documentation grouping, or internal/public symbol in the exact iOS package before importing it. |

Do not flatten the names above into a single guessed module. The 0.9.0 package
manifest exposes five products—four runtime products plus the test-only
`MWDATMockDeviceTestClient`. The upstream iOS skill set and samples are the
implementation anchor for 0.9.0; the API reference and package graph decide
what a real target may import.

For machine-readable routing, load the iOS rows in the [source-pinned API
surface register](../skills/packages/meta-wearables-full-sdk-audit/references/surface-manifest.yaml)
(`IOS-*` plus the conceptual-index row). Each row carries source anchors,
status, compile/runtime gate, privacy path, fallback, and migration notes; it
does not replace the selected package’s generated API or target build.

## Core lifecycle graph

```text
Wearables.configure()
  -> Wearables.shared
  -> registrationStateStream()
  -> startRegistration() / Meta AI callback / handleUrl(_:)
  -> checkPermissionStatus(_:) / requestPermission(_:)
  -> devicesStream() / deviceForIdentifier(_:) / device selector
  -> createSession(deviceSelector:)
  -> DeviceSession.start()
  -> stateStream() == .started
  -> addCamera(...) and/or addDisplay()
  -> observe capability state/errors
  -> stop capability -> stop session -> release listeners
```

The key types and responsibilities are:

- `Wearables` is the SDK entry point. Configure once at app launch, then use
  `Wearables.shared` for registration, permission, device, and session work.
- `registrationStateStream()` exposes registration states such as
  `.available`, `.registering`, `.registered`, and `.unavailable` in the current
  route. Registration is a Meta AI companion-app flow, not a local Boolean.
- `devicesStream()` reports availability. `AutoDeviceSelector` selects an
  eligible device; `SpecificDeviceSelector` is the route for explicit device
  choice where the current API exposes it.
- `DeviceSession` is device-driven and terminal. Current states include
  `idle`, `starting`, `started`, `paused`, `stopping`, and `stopped`. A stopped
  session must be released and recreated rather than blindly restarted.
- Only one session may run on a device at a time. Folding, doffing, another
  experience, a link change, or device policy can pause or stop the session.

## Camera, photo, and media surfaces

The current camera route is:

```text
started DeviceSession -> addCamera(StreamConfiguration)
  -> Camera.stream -> Stream.start()
  -> statePublisher/videoFramePublisher/photoDataPublisher
  -> Camera.stop() -> DeviceSession.stop()
```

The public 0.9 reference and upstream samples identify:

- `StreamConfiguration` with raw/compressed video selection, resolution, and
  frame rate; current sample values are low/medium/high resolutions and 2/7/15/
  24/30 FPS;
- `StreamState` transitions including `stopped`, `waitingForDevice`, `starting`,
  `streaming`, and `paused`;
- `VideoFrame.makeUIImage()` as a convenience conversion, not a proof of
  acceptable memory or frame latency;
- `photoDataPublisher` delivering `PhotoData`, with `capturePhoto(format:)`
  during an active stream;
- adaptive quality behavior under Bluetooth bandwidth pressure; record the
  observed state rather than assuming the requested resolution/rate was used.

The 0.9.0 changelog also adds an explicit `CameraState`/publisher surface,
`Camera.stop()`, and a child `Camera.stream`; it removes the older direct
`addStream(config:)` path and the older `CaptureError` type. Treat
`StreamError.hingesClosed` on doff and `StreamError.photoCaptureFailed` as
typed error categories to verify against the selected tag rather than writing
an exhaustive switch from memory.

Use a bounded frame consumer, keep listener tokens alive only as long as needed,
cancel processing on pause/stop, and stop the camera before the parent session.
Do not persist or upload raw frames/photos until purpose, consent, retention,
redaction, and network/vendor processing are explicit.

## Audio and sensors

The current public DAT guide documents audio through standard iOS Bluetooth
profiles rather than a guessed `MWDATAudio` import:

| Profile | Direction | Public route | Product implication |
| --- | --- | --- | --- |
| A2DP | output | `AVAudioSession` playback route to glasses | higher-fidelity playback/TTS; verify the active route |
| HFP | bidirectional | `.playAndRecord` plus `.allowBluetoothHFP`, preferred HFP input, `AVAudioEngine` tap | glasses microphone input at documented 8 kHz mono; output quality changes while HFP is active |

The public guide gives a meaningful ordering constraint for a camera + HFP
feature: add the DAT camera, configure and start the HFP route, wait for the
route to settle and verify `bluetoothHFP`, then start the camera stream. Treat
the route, interruption, permission, teardown, and physical audio observation
as separate evidence. The glasses microphone is not a reason to bypass iOS
microphone consent or silently transmit audio.

The same public index names IMU/sensor capabilities. The current iOS upstream
skills and samples do not provide a local implementation contract for every
sensor symbol; keep IMU work `to-verify` against the versioned API reference
until the exact target package exposes it.

## 0.9.0 lifecycle, diagnostics, and fixture deltas

Keep these changes in migration reviews and test fixtures:

| Signal | Review consequence |
| --- | --- |
| `ListenerTokenBag` actor and `AnyListenerToken.store(in:)` | Keep listener ownership explicit and actor-safe; test teardown instead of retaining tokens globally. |
| `MockCameraKit.setCameraFeed(cameraFacing:)` is synchronous | Remove stale `await` from 0.9.0 mock fixtures and typecheck the exact mock package. |
| `stateStream()`/`errorStream()` finish on `.stopped` | Treat completion as a terminal lifecycle event; do not wait forever for another state. |
| `StreamError.hingesClosed` on doff | Route a doff to a recoverable pause/stop path and test stale-frame cancellation. |
| `DeviceType.supportsDisplay` and Display `ButtonGroup` | Gate native Display by runtime capability and keep focus/action evidence separate. |
| `MWDAT > CrashReporting > OptOut` | Review crash-data disclosure and retention; do not confuse it with the removed DAM opt-out. |
| MockDevice link availability mirrors real-device checks | Missing Bluetooth/Wi-Fi usage or local-network configuration should fail the mock the same way a real target can fail; keep the static/config test. |
| Camera Access background behavior | The current sample/changelog wording is route/option-sensitive: preview may end on app background while optional sound-in-video behavior is documented separately. Mark background camera continuation `to-verify` for the target build. |

## Native Display surface

Native Display is a capability attached after a started session:

```text
device.supportsDisplay()
  -> create/start DeviceSession
  -> addDisplay()
  -> Display.start() and observe DisplayState
  -> send one root DisplayableView
  -> handle input/video errors and clear/stop
```

The public iOS route names a component DSL including `FlexBox`, `Text`,
`Button`, `Image`, `Icon`, `ButtonGroup`, and `VideoPlayer`. A structured UI
send uses one root `FlexBox`; a video send uses one root `VideoPlayer`. Each send
replaces the prior content/handlers. The current route also exposes Display
state/error and clear/stop behavior; typecheck exact method names against the
selected tag.

The public Display guide documents 600×600 rendering, captouch/Neural Band
input, high-bandwidth link requirements, and video constraints. Use short,
high-contrast, recoverable content. Native Display is not a SwiftUI window and
not the Web Apps DOM runtime.

## Mock Device Kit and UI-test control

The public iOS MockDevice route includes:

- `MockDeviceKit.shared.enable()` / `.disable()`;
- `pairGlasses(model:)` and simulated device lifecycle such as power, unfold,
  don, doff, fold, and power-off;
- controllable camera permission results and `MockCameraKit` feeds for a phone
  camera, HEVC video file, or captured image;
- simulated captouch tap/tap-and-hold behavior;
- the `MWDATMockDeviceTestClient`/localhost test-server route for XCUITest
  processes to pair devices, configure feeds, trigger gestures, and exercise
  registration/stream/photo flows without hard-coded app state.

MockDevice proves deterministic adapter behavior and failure handling. It does
not prove Bluetooth timing, HFP audio, camera optics, Display legibility,
Neural Band behavior, firmware compatibility, thermal/battery behavior, or a
release-channel device.

## Configuration and distribution gates

The current iOS setup/sample surface names these gates:

- app callback URL scheme and `MWDAT.AppLinkURLScheme`;
- `MWDAT.MetaAppID`, `ClientToken`, and `TeamID` for non-Developer-Mode
  attestation/configuration; keep values outside source control;
- `fb-viewapp` in the URL query-scheme allowlist so the SDK can detect/open
  Meta AI;
- `UISupportedExternalAccessoryProtocols` with `com.meta.ar.wearable` and the
  exact background/Bluetooth modes required by the selected route;
- `NSBluetoothAlwaysUsageDescription`; local-network/Bonjour declarations for
  Wi-Fi/high-bandwidth camera or Display paths;
- camera/microphone usage descriptions and privacy-manifest/App Store metadata.

The current public Developer Center `llms.txt` explicitly warns that App Store
submission is not currently supported for the DAT path and describes controlled
or invite-only release channels. Treat a signed local build, a release channel,
and App Store eligibility as three different gates; do not promise App Store
distribution until the current official policy changes and the exact target
passes its review requirements.

## Device and Web Apps boundary

The current public DAT hardware statement names Ray-Ban Meta Gen 1/Gen 2, Ray-Ban
Meta Optics, and Meta Ray-Ban Display, with Meta AI app/firmware version
dependencies. It does not establish a public Gen 3 runtime mapping. The Web
Apps route is separately limited to Meta Ray-Ban Display and has its own hosted
HTML/CSS/JavaScript, 600×600, input, sensor, and capability contract. The
Developer Center index and toolkit `main` currently disagree about several Web
App features; keep text composition, offline, back, extended gestures, and
sensors source-conflicted/to-verify. Do not use Web Apps docs to invent native
DAT symbols, or DAT symbols to expand the Web App runtime.

## Sources

- [Meta Wearables Developer Platform API index](https://wearables.developer.meta.com/llms.txt?full=true)
- [DAT iOS API reference](https://wearables.developer.meta.com/docs/reference/ios_swift/dat/latest)
- [DAT iOS repository at 0.9.0](https://github.com/facebook/meta-wearables-dat-ios)
- [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [DAT iOS getting-started skill](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/getting-started/SKILL.md)
- [DAT iOS camera streaming skill](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/camera-streaming/SKILL.md)
- [DAT iOS Display access skill](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/display-access/SKILL.md)
- [DAT iOS MockDevice testing skill](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/mockdevice-testing/SKILL.md)
- [DAT iOS sample apps](https://github.com/facebook/meta-wearables-dat-ios/tree/main/samples)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [AVAudioEngine](https://developer.apple.com/documentation/avfaudio/avaudioengine)
- [Apple External Accessory](https://developer.apple.com/documentation/externalaccessory)
- [Meta Wearables Web Apps](https://wearables.developer.meta.com/docs/develop/webapps)
