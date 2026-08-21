# SwiftUI AVFAudio voice I/O review

This is the focused iOS 26 route for full-duplex voice input and output using `AVAudioEngine` I/O nodes and system voice processing. The existing [SwiftUI audio capture and transcription review](89-swiftui-audio-capture-and-transcription.md) covers microphone capture, transcription, and review. The [LiveCommunicationKit review](121-swiftui-live-communication-kit-calling-review.md) is the system-calling boundary. This page covers the audio engine and hardware path that sits between a person, a voice agent, and a communication session.

The route is:

~~~text
product voice intent
  -> microphone permission and privacy policy
  -> AVAudioSession category/mode/route
  -> AVAudioEngine input/output nodes
  -> hardware format and channel validation
  -> AVAudioIONode voice-processing policy
  -> bounded input tap / agent / playback graph
  -> output route and physical speaker/headset
  -> interruption/route/media-reset recovery
  -> SwiftUI voice state and optional reviewed on-device AI
~~~

Voice processing is not the same as speech recognition, a call provider, or an AI agent. `AVAudioEngine` can move buffers; `AVAudioIONode` can enable system voice processing; `AVAudioSession` communicates the app’s audio intent to the system. None of those facts alone proves that the right microphone was captured, that echo control was appropriate, that a model responded, or that a far-end participant heard the intended audio.

## 1. Choose the voice-I/O lane

| Outcome | Primary route | Boundary |
| --- | --- | --- |
| Record microphone input | `AVAudioInputNode` and a tap/engine graph | Input permission, hardware format, buffer ownership |
| Live transcription | Input node -> bounded input -> Speech framework | Audio capture is separate from final transcript truth |
| Duplex voice assistant | `playAndRecord` session -> input/output nodes -> agent loop | Local acoustic loop, interruption, privacy, and response policy |
| VoIP/voice chat | `playAndRecord` + `.voiceChat` and Voice I/O processing | Call provider, user consent, local/far-end evidence |
| Playback with microphone monitoring | Input/output graph with explicit route and feedback policy | Echo risk, output privacy, physical route |
| Add app audio to a call | `AVAudioApplication` microphone-injection permission plus communication system | Explicit consent, service entitlement, call state, far-end proof |
| Measurement/clean capture | A route without voice-processing chat assumptions | Do not enable voice processing merely because input exists |

Do not use voice-processing mode as a generic “make audio better” switch. Voice chat may change processing, allowed routes, tone, and Bluetooth behavior. Choose it because the product is two-way voice communication and record the reason.

## 2. Configure the audio-session intent

`AVAudioSession` is the system intermediary between the app and audio hardware. For a duplex voice route, the typical choice is `playAndRecord` with a communication mode such as `.voiceChat`, subject to the product’s actual route and platform requirements.

Apple documents that `.voiceChat` is appropriate for two-way voice communication such as VoIP, optimizes tonal equalization for voice, limits routes to those suitable for voice chat, and automatically applies the Bluetooth HFP option. The mode also coordinates with Audio Unit Voice I/O or `AVAudioEngine` voice-processing enablement.

Configure the session before the engine starts, and activate it close to the user’s explicit start action:

| Decision | Record |
| --- | --- |
| Category | `playAndRecord` or documented alternative |
| Mode | `voiceChat`, `videoChat`, `gameChat`, or other reasoned mode |
| Options | Bluetooth/HFP, default-to-speaker, mixing/ducking, other |
| Preferred input/output | port and channel policy |
| Activation | user intent and error/retry behavior |
| Background/lock | permitted target/background contract |
| Call provider | LiveCommunicationKit/CallKit/default system or none |
| Consent | microphone, call/injection, recording, AI retention |

Do not activate a recording or voice-chat session at app launch just to populate a UI. Deferring activation avoids prematurely interrupting other audio and keeps the user’s privacy intent clear.

## 3. Own the engine’s I/O nodes

`AVAudioEngine.inputNode` and `outputNode` are singleton I/O nodes created on demand. The input node receives hardware input; the output node connects the graph to the active audio route. A tap or downstream node is the app’s controlled observation point.

One coordinator should own:

~~~text
VoiceIOCoordinator
  ├─ AVAudioSession policy and route snapshot
  ├─ AVAudioEngine
  ├─ inputNode/outputNode references
  ├─ voice-processing state
  ├─ graph and format revision
  ├─ input tap/buffer handoff
  ├─ playback/agent response owner
  ├─ interruption/route/reset observers
  └─ SwiftUI state projection
~~~

Do not install a tap from a transient view, start a second engine from a sheet, or let the transcription service own the output node. A voice agent needs one input/output graph and an explicit policy for what happens when the view disappears.

## 4. Validate hardware format before capture

Apple documents that the input node’s input format should have a nonzero sample rate and channel count when input is enabled. Trying to capture while input is unavailable or disabled can throw an error or exception.

Before installing a tap or starting the engine, inspect:

- input hardware sample rate;
- input channel count;
- output hardware sample rate/channel count;
- current route input/output ports;
- selected input port and channel;
- session category/mode after activation;
- graph format at the tap and output node;
- whether a Bluetooth/HFP route changed the format.

Treat zero channels, zero sample rate, unavailable input, and a route change as explicit states. Do not feed an invalid format to SpeechAnalyzer, an AI agent, or an `AVAudioFile` and then report “no speech detected.”

Input and output formats can differ across hardware and routes. Keep `inputFormat`, `processingFormat`, and `outputFormat` in the state record. If the graph needs conversion, own it explicitly and test the conversion latency and channel behavior.

## 5. Enable voice processing deliberately

`AVAudioIONode.setVoiceProcessingEnabled(_:)` enables or disables voice processing on the I/O node, and `isVoiceProcessingEnabled` reports the current state. Apple’s voice-processing sample and Audio Unit Voice I/O documentation describe voice processing as a communication capability with features such as echo control, automatic gain correction, and muting controls.

Voice-processing state belongs to the graph/session generation:

| State | Meaning |
| --- | --- |
| disabled | Clean or non-communication I/O policy |
| requested | User/product policy wants voice processing |
| enabling | Unit/engine is being reconfigured |
| enabled | I/O node reports enabled |
| failed | Route or unit could not enable it |
| reset | Media/route change requires revalidation |

Changing this state may require graph or hardware reconfiguration. Stop or quiesce according to the documented engine lifecycle, apply the setting, revalidate formats, and restart only when user intent still permits. Do not toggle it continuously from a slider.

At the lower Audio Unit Voice I/O boundary, `kAUVoiceIOProperty_BypassVoiceProcessing` bypasses processing for microphone uplink; other Voice I/O properties control automatic gain correction and output mute. Use the lowest-level property only when the product truly needs it, and record scope, element, timing, and physical proof. A Boolean that says “bypass” is not proof that echo cancellation or AGC changed as intended.

## 6. Input tap and bounded handoff

The input tap is an observation and handoff point, not an AI boundary. Keep the callback bounded:

~~~text
input tap
  -> copy/reference only the required bounded audio
  -> enqueue to an owned async stream/actor/ring buffer
  -> release callback quickly
  -> SpeechAnalyzer / level meter / agent worker
~~~

Do not block the tap on a model, disk, network, UI update, or unbounded queue. Record buffer format, frame count, sample time, generation, and drop/backpressure policy. If the agent cannot keep up, apply a visible “processing behind” or controlled drop policy rather than silently building memory.

Separate raw input from derived state:

| State | Claim |
| --- | --- |
| permission | app may request/use microphone according to system state |
| hardwareReady | session/input reports usable format and route |
| capturing | engine/tap is active |
| voiceProcessing | I/O node reports policy state |
| level | measured signal observation |
| speechActivity | detector/model inference, not raw truth |
| transcript | Speech framework result with its own finality |
| agentResponse | generated proposal/response with model revision |

## 7. Output route and acoustic privacy

The output node follows the active audio route. Use `AVAudioSession.currentRoute` and route-change notifications to publish a route summary, but verify physical output separately.

Important route policies:

- headphones indicate a private listening intent; preserve it when possible;
- unplugging headphones should not automatically expose private voice-agent output through the speaker;
- Bluetooth HFP can change input/output format and processing behavior;
- built-in speaker/microphone can create feedback and echo conditions;
- receiver, speaker, wired, USB, and Bluetooth routes need separate fixtures;
- a route change during an active call or voice response may require pause/reconfigure/retry;
- route state should never expose raw device identifiers in user-facing accessibility copy.

Do not show “connected” as “heard.” Log route and output state, then perform a physical source/response test with the chosen privacy policy.

## 8. Interruptions, route changes, and media-service reset

Observe `AVAudioSession.interruptionNotification`, `routeChangeNotification`, `mediaServicesWereLostNotification`, and `mediaServicesWereResetNotification` as appropriate. Model recovery explicitly:

~~~text
active voice I/O
  -> interruption/route/reset
  -> stop or quiesce engine and input handoff
  -> update session/route/format/voice-processing state
  -> recreate audio objects after media-service reset
  -> ask for user-driven resume/retry
~~~

On an interruption end, use the system’s `shouldResume` option and the product’s user intent. Do not resume a sensitive microphone or voice-agent response merely because an interruption ended. Apple documents that after a media-service reset, apps should reinitialize audio objects and reset session configuration, and should not restart playback/recording/processing until user action.

On an old-device-unavailable route change, preserve the previous route record and decide whether to pause output. On a new-device-available change, requery `currentRoute`, formats, channels, and voice-processing state.

## 9. Communication and call boundary

Voice I/O can support a local assistant, a VoIP call, or a call-adjacent experience, but those are different products:

| Product | Required boundary |
| --- | --- |
| Local voice assistant | microphone permission, local output, privacy/retention, AI availability |
| VoIP | call provider/session, `playAndRecord`/voice chat, far-end transport, call UI |
| System call integration | LiveCommunicationKit/CallKit/system calling contract, action deadlines, audio session |
| App audio into a call | explicit `AVAudioApplication` microphone-injection permission and consent |
| Transcription only | input capture and Speech route; output may be off |

Never infer far-end delivery from local output or model completion. If app audio is added to a call, prove local capture, local mix, uplink permission, active call, far-end receipt, and user consent separately. Keep generated agent responses as proposals until the communication action is authorized.

## 10. SwiftUI and Liquid Glass voice surface

The native UI should state the audio contract:

- microphone permission and “Microphone ready” state;
- input/output route names at a human-readable level;
- voice-processing enabled/disabled/failed;
- listening, processing, speaking, interrupted, route unavailable, and stopped states;
- a clear mute/stop action;
- privacy indicator and retention policy;
- a compact diagnostic disclosure for format/frame/drop state;
- optional AI response review before speaking or uplinking.

Apply Liquid Glass to functional mute/stop/route controls or a compact status group. Keep the transcript/response/source text readable and avoid fake waveforms. The UI should not imply that a response was audible, private, or sent to a call unless those observations are separately present.

## 11. Optional on-device AI voice-agent boundary

Use on-device AI only after the audio pipeline has bounded input and a privacy decision:

~~~text
permission + route + format
  -> bounded input frames
  -> transcript/intent revision
  -> model availability/privacy check
  -> typed response/tool proposal
  -> user/system communication policy
  -> TTS/local output or explicit call uplink
~~~

The model must not control session activation, voice-processing toggles, microphone permission, or call uplink directly. Validate tool/response destination, source revision, active call state, and user consent. Keep deterministic fallback for unavailable models and a stop/mute action that bypasses the model.

## 12. Proof boundary

| Claim | Evidence |
| --- | --- |
| Microphone use is authorized | Physical target permission prompt, usage description, and grant/deny path |
| Hardware is ready | Active session, route, nonzero input format/channel, physical microphone |
| Voice processing is enabled | `isVoiceProcessingEnabled`, configuration record, acoustic fixture |
| Input is captured | Nonzero physical frames with format/time continuity |
| Output is routed | Current route plus physical speaker/headset evidence |
| Full duplex is safe | Echo/feedback/latency/route fixture with physical device |
| Interruption recovery works | Begin/end/shouldResume and user-intent test |
| Media reset recovery works | Reset notification, audio object/session reinitialization, user resume |
| Call uplink is authorized | Explicit permission/service/call/far-end evidence |
| AI response is safe | Availability, bounded input, typed proposal, review, stale rejection, stop/fallback |
| Accessibility works | VoiceOver, Dynamic Type, mute/stop actions, route/privacy text, alternative input |
| Release is ready | Final host target, privacy manifest/usage keys, archive, TestFlight, physical audio |

The [route worksheet](../50-capability-recipes/159-swiftui-avfaudio-voice-io-review-route.md), [design page](../21-design-deep-dives/156-swiftui-avfaudio-voice-io-review-design.md), [proof matrix](../60-verification/153-swiftui-avfaudio-voice-io-proof-matrix.md), and [recipes](../70-code-recipes/171-swiftui-avfaudio-voice-io-review-recipes.md) carry the implementation record.

## Sources

- [Audio Engine](https://developer.apple.com/documentation/avfaudio/audio-engine)
- [AVAudioEngine](https://developer.apple.com/documentation/avfaudio/avaudioengine)
- [AVAudioIONode](https://developer.apple.com/documentation/avfaudio/avaudioionode)
- [AVAudioInputNode](https://developer.apple.com/documentation/avfaudio/avaudioinputnode)
- [AVAudioOutputNode](https://developer.apple.com/documentation/avfaudio/avaudiooutputnode)
- [AVAudioNode](https://developer.apple.com/documentation/avfaudio/avaudionode)
- [AVAudioEngine.inputNode](https://developer.apple.com/documentation/avfaudio/avaudioengine/inputnode)
- [AVAudioIONode.isVoiceProcessingEnabled](https://developer.apple.com/documentation/avfaudio/avaudioionode/isvoiceprocessingenabled)
- [AVAudioIONode.setVoiceProcessingEnabled(_:)](https://developer.apple.com/documentation/avfaudio/avaudioionode/setvoiceprocessingenabled%28_%3A%29)
- [Using voice processing](https://developer.apple.com/documentation/avfaudio/using-voice-processing)
- [Audio Unit Voice I/O](https://developer.apple.com/documentation/audiotoolbox/audio-unit-voice-i-o)
- [kAUVoiceIOProperty_BypassVoiceProcessing](https://developer.apple.com/documentation/audiotoolbox/kauvoiceioproperty_bypassvoiceprocessing)
- [kAUVoiceIOProperty_VoiceProcessingEnableAGC](https://developer.apple.com/documentation/audiotoolbox/kauvoiceioproperty_voiceprocessingenableagc)
- [kAUVoiceIOProperty_MuteOutput](https://developer.apple.com/documentation/audiotoolbox/kauvoiceioproperty_muteoutput)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [AVAudioSession.Mode.voiceChat](https://developer.apple.com/documentation/avfaudio/avaudiosession/mode-swift.struct/voicechat)
- [AVAudioSessionPortDescription.hasHardwareVoiceCallProcessing](https://developer.apple.com/documentation/avfaudio/avaudiosessionportdescription/hashardwarevoicecallprocessing)
- [AVAudioApplication](https://developer.apple.com/documentation/avfaudio/avaudioapplication)
- [Handling audio interruptions](https://developer.apple.com/documentation/avfaudio/handling-audio-interruptions)
- [Responding to audio route changes](https://developer.apple.com/documentation/avfaudio/responding-to-audio-route-changes)
- [AVAudioSession.mediaServicesWereResetNotification](https://developer.apple.com/documentation/avfaudio/avaudiosession/mediaserviceswereresetnotification)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
