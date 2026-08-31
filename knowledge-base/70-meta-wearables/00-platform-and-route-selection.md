# Meta Wearables platform and route selection

Choose the surface before choosing an API. A Meta Wearables experience is not
“an iPhone app with a Bluetooth screen”; it is a coordinated route across the
phone app, Meta AI, a wearable model, firmware/app compatibility, and a
capability-specific session.

## Route decision

| User outcome | First route | Why | Do not assume |
| --- | --- | --- | --- |
| Capture the glasses' point-of-view camera or still photo in a native iOS app | DAT iOS `MWDATCore` + `MWDATCamera` | The official native route owns registration, permissions, sessions, camera, stream, and photo capture. | A connected device is permissioned, streaming, or thermally able to continue. |
| Render interactive content or video on Meta Ray-Ban Display | DAT iOS `MWDATDisplay` or a Web App | DAT is a native app integration; Web Apps are HTML/CSS/JavaScript hosted for the Display surface. | A display-capable frame is selected by name, or a Web App has the same lifecycle as DAT. |
| Build a display-only prototype quickly | Web App + official browser/simulator workflow | The Web App path has a fixed display contract and can be previewed with browser input. | Browser rendering proves additive-display legibility, EMG behavior, or release delivery. |
| Extend a native cross-platform product | DAT iOS first, then compare official Android DAT naming/configuration | The official iOS and Android SDKs are designed for parallel capability concepts. | API signatures, lifecycle timing, manifest/Info.plist keys, or test evidence are identical. |
| Voice/audio-first experience without a verified DAT audio surface | Native iOS audio route with an explicit phone fallback | `AVAudioSession`, Speech, and AVFoundation can own phone-side audio when the target DAT surface is not documented or available. | The consumer glasses' speakers/microphones imply an app-owned raw audio API. |
| No compatible hardware or developer access yet | MockDeviceKit, browser simulator, fixtures, and a phone-only fallback | These provide deterministic progress while keeping the missing gate visible. | A mock or simulator is physical-device or production proof. |

The current raw full-reference endpoint is the DAT SDK v0.9 route for native
mobile iOS/Android integration. The separate Web Apps toolkit and Developer
Center route covers hosted HTML/CSS/JavaScript experiences on Meta Ray-Ban
Display. Therefore resolve “regular SDK” against the intended surface: native
regular glasses use DAT; glasses-hosted Display UI uses Web Apps; Meta AI
consumer behavior is an account and companion surface, not an invented
third-party SDK.

## Handoff graph

Use this shape in plans and code reviews:

```text
user intent
  -> chosen surface (native DAT | Web App | phone fallback)
  -> target/configuration (iOS, package, Info.plist, URL, account/channel)
  -> Meta AI registration and permission state
  -> device selection and compatibility
  -> capability/session state
  -> normalized observation (frame, photo, display result, input)
  -> deterministic validation and user-visible state
  -> domain action or derived UI
```

Keep the raw frame, device state, session state, permission state, generated
interpretation, and committed domain action as different values. A model can
describe a frame, but it cannot authorize a capture, publish a Web App, or
declare a device compatible.

## Route intake

Before implementation, record:

- primary task, consequence of failure, and whether the experience is
  glanceable, audio-first, camera-first, or phone-first;
- device models actually owned and the runtime capability required;
- native DAT versus Web App versus fallback choice and rejected alternatives;
- iOS deployment target, Xcode/Swift/package revision, Android parity needs,
  Meta AI version, firmware, Developer Mode, release channel, and account;
- camera, microphone, display, network, local storage, and external-service
  data boundaries;
- MockDevice/browser/simulator, physical/system, signed, release-channel, and
  production evidence still required.

## Sources

- [Meta Wearables Device Access Toolkit announcement](https://developers.meta.com/blog/introducing-meta-wearables-device-access-toolkit/)
- [Official DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [Official DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
- [Official Meta Wearables Web App toolkit](https://github.com/facebook/meta-wearables-webapp)
- [Full Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
- [Meta Wearables Web Apps documentation](https://wearables.developer.meta.com/docs/develop/webapps)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Evidence and verification language](../00-foundations/05-evidence-and-verification-language.md)
