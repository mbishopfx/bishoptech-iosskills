# SwiftUI AVFAudio voice I/O proof matrix

Use this matrix for a full-duplex voice-I/O feature. It separates permission, hardware format, voice processing, engine state, local output, call uplink, AI response, accessibility, and release evidence.

## Evidence record

| Field | Value |
| --- | --- |
| Product / target | `TBD` |
| Deployment target / SDK | `iOS 26 / TBD` |
| Voice-I/O lane | local assistant / transcription / VoIP / call-adjacent |
| Audio session category/mode/options | `TBD` |
| Input/output ports | `TBD` |
| Graph revision | `TBD` |
| Input/output format | `TBD` |
| Voice-processing state | `TBD` |
| Physical device / OS / route | `TBD` |
| Call/uplink provider | `TBD` |
| AI model/revision | `TBD` |
| Archive/TestFlight build | `TBD` |
| Evidence owner / date | `TBD` |

## Claim-to-evidence matrix

| ID | Claim | Minimum evidence | Does not prove it |
| --- | --- | --- | --- |
| V1 | Microphone permission is correct | Final usage description, physical prompt, grant/deny/settings path | Simulator permission state alone |
| V2 | Input hardware is ready | Active session, nonzero input format/rate/channels, physical microphone | Permission grant or input node object |
| V3 | Output route is known | `currentRoute`, route-change observation, physical speaker/headset fixture | Route name in a UI |
| V4 | Voice processing is enabled | I/O node state, configuration record, acoustic echo/level fixture | Boolean without acoustic behavior |
| V5 | Voice processing bypass/AGC/mute is correct | Audio Unit property scope/element and physical fixture | Setting a property value |
| V6 | Engine graph is connected | Attached nodes, formats, start result, known source/output test | `isRunning` alone |
| V7 | Input capture is continuous | Nonzero physical frames, format/time continuity, bounded handoff/drop record | An input tap callback once |
| V8 | Duplex audio is safe | Feedback/echo/latency test on target route | A local loopback success |
| V9 | Interruption recovery works | Begin/end/shouldResume and user-intent test | Resume button changing state |
| V10 | Media reset recovery works | Reset notification, recreated objects/session, user-driven restart | Reusing stale engine objects |
| V11 | Route recovery is private | Headphone disconnect, speaker fallback policy, physical observation | Current route snapshot |
| V12 | Local output is audible | Known response/source, physical speaker/headset evidence | Generated buffer or engine state |
| V13 | Call uplink is authorized | Explicit permission, active call/provider state, local and far-end evidence | Local response completion |
| V14 | AI response is safe | Availability, bounded revision, typed proposal, review/accept/stop/fallback | Model text or spoken local output |
| V15 | SwiftUI is accessible | Accessibility Inspector, VoiceOver, Dynamic Type, alternate input, reduced transparency/motion | Glass screenshot |
| V16 | Release is ready | Final target compile, privacy/config review, archive/signing, TestFlight, physical device | Simulator, debug run, or archive key |

## Permission and session tests

Test:

- first-run permission grant;
- denial and settings recovery;
- permission revoked while the screen is open;
- session category/mode/options after activation;
- activation failure and retry;
- `playAndRecord` with `.voiceChat` on a supported route;
- Bluetooth/HFP availability and route restrictions;
- speaker/default route choice;
- local assistant versus call-specific permission;
- microphone injection permission if app audio is added to a call;
- lock/background behavior declared by the target.

Record actual session values after activation. Do not claim voice-chat processing because the UI selected a “conversation” mode.

## Hardware and graph fixtures

For every physical route, capture:

~~~text
session category/mode/options
current input/output port
input sample rate/channel count
output sample rate/channel count
input/tap/processing format
graph revision
voice-processing state
engine start state
source fixture and expected output
~~~

Include no input hardware, zero input channels, route removal, sample-rate change, Bluetooth HFP, wired headset, speaker, receiver, and USB route where supported. Verify that the graph does not install a tap or send invalid frames to a recognizer when input is unavailable.

## Voice-processing fixtures

| Fixture | Expected observation |
| --- | --- |
| Voice processing off | declared clean/non-chat route behavior |
| Enable on supported duplex route | node reports enabled; echo/level behavior matches policy |
| Enable failure | typed error and safe fallback |
| Disable/re-enable | controlled graph/session reconfiguration |
| Hardware voice-call processing available | product avoids redundant proprietary processing where appropriate |
| Bypass property | uplink processing bypass is scoped and physically observable |
| AGC property | level behavior and scope are recorded |
| Mute output property | output muting is distinct from microphone permission/stop |
| Route change | state revalidated; no stale Boolean claim |

Use a known acoustic fixture and physical device. A level meter or Boolean is not enough to prove echo cancellation, AGC, or mute behavior.

## Buffer and agent handoff tests

Include:

- bounded packet size and queue capacity;
- input time continuity and generation;
- backpressure/drop behavior;
- cancellation while processing;
- transcript volatile/final revision if Speech is used;
- model unavailable/expired/cancelled state;
- response proposal accepted/rejected/edited;
- Stop/Mute while the model is generating or speech is playing;
- local output versus call-uplink destination;
- raw audio/transcript retention and deletion policy.

The input callback and output render path must remain independent from model scheduling. Record whether each test proves local capture, local response generation, audible output, or far-end delivery.

## Interruption, route, and reset matrix

| Event | Required evidence |
| --- | --- |
| Interruption began | engine/tap/output state and UI update |
| Interruption ended with resume option | explicit resume decision and route revalidation |
| Interruption ended without resume | no automatic sensitive restart |
| Headphones connected | current route/format and privacy state |
| Headphones removed | safe pause/speaker policy and physical result |
| Bluetooth route change | HFP format/voice-processing/latency recheck |
| Media services lost | audio objects/session invalidated |
| Media services reset | objects/session reinitialized; user restarts |
| Call provider state changed | local/remote/uplink state remains distinct |

## Accessibility and SwiftUI evidence

- [ ] Active microphone and mute state are visible without sound.
- [ ] Stop/mute/reconnect are accessible actions with labels and hints.
- [ ] Route and privacy state are readable with VoiceOver.
- [ ] Dynamic Type preserves the primary action and warnings.
- [ ] Voice-processing state is not conveyed by color alone.
- [ ] Reduced transparency and motion have usable fallbacks.
- [ ] Keyboard, pointer, Voice Control, and Switch Control reach core actions.
- [ ] Transcript/response text has a non-audio alternative.
- [ ] VoiceOver testing accounts for overlap with app output audio.

## AI and privacy evidence

Retain, when applicable:

- model availability and model revision;
- bounded transcript/intent and source revision;
- typed response/tool proposal;
- destination and call/uplink policy;
- user/system acceptance;
- stop/mute action and cancellation;
- stale revision rejection;
- deterministic fallback;
- raw audio/transcript/response retention decision;
- no unapproved server fallback.

Do not state that an AI response was heard, correct, private, or delivered to a remote participant without the corresponding evidence.

## Release checklist

- [ ] Final iOS 26 target compile and usage keys.
- [ ] Session category/mode/options and route behavior reviewed.
- [ ] Physical microphone/speaker/headset/Bluetooth evidence captured.
- [ ] Voice-processing and hardware-format evidence captured.
- [ ] Interruption, route, media-reset, and user-recovery evidence captured.
- [ ] Call/uplink permission and far-end proof captured if applicable.
- [ ] SwiftUI accessibility and Liquid Glass fallback reviewed.
- [ ] Archive/signing/TestFlight build exercises the intended route.
- [ ] Privacy, retention, and App Review claims match tested behavior.

## Sources

- [Audio Engine](https://developer.apple.com/documentation/avfaudio/audio-engine)
- [AVAudioEngine](https://developer.apple.com/documentation/avfaudio/avaudioengine)
- [AVAudioIONode](https://developer.apple.com/documentation/avfaudio/avaudioionode)
- [AVAudioInputNode](https://developer.apple.com/documentation/avfaudio/avaudioinputnode)
- [AVAudioOutputNode](https://developer.apple.com/documentation/avfaudio/avaudiooutputnode)
- [Using voice processing](https://developer.apple.com/documentation/avfaudio/using-voice-processing)
- [Audio Unit Voice I/O](https://developer.apple.com/documentation/audiotoolbox/audio-unit-voice-i-o)
- [kAUVoiceIOProperty_BypassVoiceProcessing](https://developer.apple.com/documentation/audiotoolbox/kauvoiceioproperty_bypassvoiceprocessing)
- [kAUVoiceIOProperty_VoiceProcessingEnableAGC](https://developer.apple.com/documentation/audiotoolbox/kauvoiceioproperty_voiceprocessingenableagc)
- [kAUVoiceIOProperty_MuteOutput](https://developer.apple.com/documentation/audiotoolbox/kauvoiceioproperty_muteoutput)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [AVAudioSession.Mode.voiceChat](https://developer.apple.com/documentation/avfaudio/avaudiosession/mode-swift.struct/voicechat)
- [AVAudioApplication](https://developer.apple.com/documentation/avfaudio/avaudioapplication)
- [Handling audio interruptions](https://developer.apple.com/documentation/avfaudio/handling-audio-interruptions)
- [Responding to audio route changes](https://developer.apple.com/documentation/avfaudio/responding-to-audio-route-changes)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
