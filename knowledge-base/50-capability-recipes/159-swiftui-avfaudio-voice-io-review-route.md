# SwiftUI AVFAudio voice I/O route worksheet

Use this worksheet for a full-duplex microphone/speaker feature, voice agent, VoIP audio path, or communication surface that uses `AVAudioEngine` I/O nodes and optional system voice processing. Complete it before wiring a model to audio.

The [audio capture and transcription route](120-swiftui-audio-capture-and-transcription-route.md) covers input recognition. The [LiveCommunicationKit route](../42-framework-deep-dives/121-swiftui-live-communication-kit-calling-review.md) covers system calling. This route records the hardware and engine boundary shared by those products.

## Route record

| Field | Decision |
| --- | --- |
| Product lane | local assistant / transcription / VoIP / call-adjacent / monitor |
| User outcome | `TBD` |
| Host target / deployment | `TBD / iOS 26` |
| Microphone usage description | `TBD` |
| Record permission owner | `AVAudioApplication` / other: `TBD` |
| Session category | `playAndRecord` / other: `TBD` |
| Session mode | `voiceChat` / `videoChat` / `default` / other: `TBD` |
| Session options | Bluetooth/HFP, speaker, mixing/ducking: `TBD` |
| Input port/channel | `TBD` |
| Output route | `TBD` |
| Engine graph | input -> processing -> output: `TBD` |
| Voice processing | on/off/bypass property/route fallback: `TBD` |
| Input format | sample rate/channels/layout: `TBD` |
| Output format | sample rate/channels/layout: `TBD` |
| Buffer handoff | tap/stream/actor/ring buffer/backpressure: `TBD` |
| Call provider | none / LiveCommunicationKit / CallKit / other: `TBD` |
| Uplink/injection consent | `TBD` |
| AI response lane | none / local typed proposal / other: `TBD` |
| Physical proof device | `TBD` |

## 1. Choose the lane

- [ ] Local mode, transcription mode, voice chat, and call-adjacent mode are named separately.
- [ ] The output route is allowed by the product’s privacy policy.
- [ ] Voice processing is enabled only because the route needs communication processing.
- [ ] The product can stop/mute input and output immediately.
- [ ] A model response cannot activate the microphone, change the route, or inject into a call without the declared authorization.
- [ ] A deterministic fallback exists for no input, no output, no model, and no call.

## 2. Permission and session contract

| Gate | Evidence |
| --- | --- |
| Usage description | final target `Info.plist` and prompt copy |
| Record permission | `AVAudioApplication` result and deny/settings path |
| Category/mode | actual post-configuration session values |
| Activation | user intent and activation error/retry |
| Preferred input | selected port/channel and fallback |
| Route | current input/output and changes |
| Background/lock | target/background mode decision |
| Call/injection | separate permission, active call, and consent |

Do not request call-specific authority for a local assistant. Do not activate the session until the product is actually beginning audio use unless an explicit platform requirement says otherwise.

## 3. Engine and node ownership

| Owner | Responsibility |
| --- | --- |
| One `VoiceIOCoordinator` | session, engine, nodes, graph revision, recovery |
| Input node | hardware input and bounded tap/handoff |
| Output node | graph output to active route |
| Processing/agent actor | transcript/model/response work outside render/tap deadline |
| SwiftUI model | state projection, controls, accessibility, user intent |
| Call provider | call lifecycle and far-end communication contract |

No transient view installs the tap, starts a second engine, or owns the only route observer. A view disappearance should have a documented effect: keep listening, pause, or stop.

## 4. Hardware and format contract

Before starting:

- [ ] Input format has nonzero sample rate and channel count.
- [ ] Output format and route are available.
- [ ] Current session category/mode matches the graph.
- [ ] Input/output channel layout is compatible.
- [ ] Bluetooth/HFP route is handled separately.
- [ ] Tap/processing format is recorded.
- [ ] Conversion is explicit when formats differ.
- [ ] Zero-format and no-hardware states do not start capture.

Record `graphRevision`, `sessionRevision`, `inputFormat`, `outputFormat`, `inputPort`, `outputPort`, and `voiceProcessingState` with each session start.

## 5. Voice-processing contract

| State | Action |
| --- | --- |
| desired on | configure the I/O node/session for voice communication |
| enable request | stop/quiesce as required, call documented API, validate result |
| enabled | record `isVoiceProcessingEnabled` and run acoustic fixture |
| failed | show route-specific fallback or stop safely |
| bypass | use only the documented Audio Unit property and approved product policy |
| route changed | revalidate hardware processing and policy |
| media reset | recreate/reconfigure audio objects and wait for user action |

If using lower-level Voice I/O properties such as bypass, AGC, or mute, record the Audio Unit scope/element and the physical effect expected. Do not expose unsupported low-level switches as if they were universal on every route.

## 6. Buffer and agent handoff

~~~text
input tap
  -> bounded frame packet {generation, format, time, frames}
  -> owned async queue/stream
  -> transcript/level/agent worker
  -> typed response proposal
  -> review or policy gate
  -> output utterance / local playback / authorized uplink
~~~

| Field | Decision |
| --- | --- |
| Maximum packet size | `TBD` |
| Queue capacity | `TBD` |
| Drop/backpressure | `TBD` |
| Time continuity | `TBD` |
| Transcript finality | `TBD` |
| Agent cancellation | `TBD` |
| Output cancellation | Stop/mute action |
| Retention | raw audio/transcript/response: `TBD` |

The tap must not await a model or disk. The agent must not assume that every captured frame becomes a transcript token. Keep input, derived speech activity, transcript, model response, and output state separate.

## 7. Route/recovery contract

- [ ] Interruption begin stops or pauses the graph and updates UI.
- [ ] Interruption end checks `shouldResume` and user intent.
- [ ] New route re-queries current route and hardware formats.
- [ ] Old route removal does not expose private output through speaker without policy.
- [ ] Media-service lost/reset reinitializes audio objects/session.
- [ ] Voice processing is revalidated after reconfiguration.
- [ ] Reconnect does not duplicate taps or engine nodes.
- [ ] Recovery waits for user action when Apple’s reset contract requires it.

## 8. SwiftUI and Liquid Glass route

| Surface | State |
| --- | --- |
| Permission card | request/denied/settings |
| Route card | input/output/format/privacy |
| Voice-processing card | off/requested/on/unavailable |
| Session control | start/stop/mute/resume |
| Agent status | listening/processing/reviewing/speaking |
| Call status | local/call/uplink authorized/far-end unverified |
| Recovery sheet | interruption/route/reset action |
| Diagnostics | graph/format/drop/latency evidence |

Use a compact functional glass group for control actions; keep privacy copy, transcript/response text, and diagnostics readable. Add labels, values, hints, named actions, and non-touch alternatives. Do not show a measured waveform unless one exists.

## 9. AI and communication contract

If an on-device model is used:

1. check model availability and local privacy policy;
2. pass bounded transcript/intent revision, not unrestricted raw audio by default;
3. request a typed response or tool proposal;
4. validate destination, action, call state, and stale revision;
5. require user/system policy acceptance;
6. speak locally or send to the call only through the declared output lane;
7. keep Stop/Mute outside the model;
8. use deterministic fallback when the model is unavailable.

Never treat a model completion as proof of capture, intent, local audibility, or far-end delivery.

## 10. Proof package

- [ ] Permission grant/deny and usage copy.
- [ ] Active session category/mode/options and route.
- [ ] Nonzero hardware input format and physical microphone capture.
- [ ] Output route and physical speaker/headset result.
- [ ] Voice-processing enabled/bypass/AGC/mute result and acoustic fixture.
- [ ] Tap/queue format, time, capacity, and backpressure fixture.
- [ ] Interruption, route-change, media-lost/reset, and user-recovery fixture.
- [ ] Local assistant and call/uplink lanes tested separately.
- [ ] AI availability, typed proposal, acceptance, stop, stale, and fallback evidence.
- [ ] VoiceOver, Dynamic Type, reduced motion/transparency, and alternate input evidence.
- [ ] Archive, signed install, TestFlight, and physical-device release evidence.

## Sources

- [Audio Engine](https://developer.apple.com/documentation/avfaudio/audio-engine)
- [AVAudioEngine](https://developer.apple.com/documentation/avfaudio/avaudioengine)
- [AVAudioIONode](https://developer.apple.com/documentation/avfaudio/avaudioionode)
- [AVAudioInputNode](https://developer.apple.com/documentation/avfaudio/avaudioinputnode)
- [AVAudioOutputNode](https://developer.apple.com/documentation/avfaudio/avaudiooutputnode)
- [Using voice processing](https://developer.apple.com/documentation/avfaudio/using-voice-processing)
- [Audio Unit Voice I/O](https://developer.apple.com/documentation/audiotoolbox/audio-unit-voice-i-o)
- [kAUVoiceIOProperty_BypassVoiceProcessing](https://developer.apple.com/documentation/audiotoolbox/kauvoiceioproperty_bypassvoiceprocessing)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [AVAudioSession.Mode.voiceChat](https://developer.apple.com/documentation/avfaudio/avaudiosession/mode-swift.struct/voicechat)
- [AVAudioApplication](https://developer.apple.com/documentation/avfaudio/avaudioapplication)
- [Handling audio interruptions](https://developer.apple.com/documentation/avfaudio/handling-audio-interruptions)
- [Responding to audio route changes](https://developer.apple.com/documentation/avfaudio/responding-to-audio-route-changes)
- [AVAudioSession.mediaServicesWereResetNotification](https://developer.apple.com/documentation/avfaudio/avaudiosession/mediaserviceswereresetnotification)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
