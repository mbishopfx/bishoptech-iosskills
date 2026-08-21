# SwiftUI AVFAudio voice I/O design review

This page translates the [voice-I/O deep dive](../42-framework-deep-dives/128-swiftui-avfaudio-voice-io-review.md) into a native SwiftUI surface for microphone, speaker, voice processing, and optional voice-agent behavior. The goal is a calm communication interface that makes privacy, route, and processing state legible without pretending that a waveform or Liquid Glass panel proves audio reached another person.

## 1. Design the communication contract

Before choosing a visual style, label the product lane:

| Lane | Primary user expectation |
| --- | --- |
| Local listening assistant | The app hears a local voice and responds locally |
| Dictation/transcription | The app captures and displays text; output may be off |
| Voice chat/VoIP | Two-way audio with a communication session and far-end participant |
| Call-adjacent audio | The app has explicit, consented interaction with a call |
| Audio monitor/recording | A physical source is captured and exposed with clear privacy state |

Do not use “Live” as a generic label for all five. “Listening” can mean a microphone tap; “In a call” requires a call provider/session; “Speaking to the call” requires an explicit uplink boundary.

## 2. Native voice surface hierarchy

Use a focused screen:

~~~text
NavigationStack
  └─ Voice session
       ├─ session and privacy state
       ├─ microphone / speaker route summary
       ├─ listening / processing / speaking state
       ├─ prominent mute and stop controls
       ├─ optional transcript/response review
       ├─ voice-processing disclosure
       └─ route and diagnostics sheet
~~~

The primary action should be understandable without audio: Start, Stop, Mute, Resume, or End call. Route names should be human-readable (“iPhone microphone,” “Bluetooth headset,” “Speaker”), not raw port UIDs. Use text plus symbol/state, never color or animation alone.

## 3. Permission and start states

A microphone product should not jump from a launch screen directly to a glowing orb. Use explicit stages:

- “Microphone permission needed” with a system-settings recovery path;
- “Preparing audio route” while the session activates;
- “Microphone unavailable” when the input format has zero channels/sample rate;
- “Listening” when input is active under the declared policy;
- “Processing” when bounded audio/transcript work is underway;
- “Speaking locally” when the app owns local output;
- “Speaking to call” only after communication/uplink authorization;
- “Paused for interruption” or “Route changed” when recovery is pending;
- “Stopped” when the user has ended the session.

Keep the initial permission rationale focused on the concrete outcome. Do not ask for call-injection or other communication authority when the feature only needs local input.

## 4. Liquid Glass as control grouping

Use Liquid Glass for the controls that are spatially near the active task:

- the Stop/Mute control group;
- a compact route selector or status pill;
- a small “Voice processing” disclosure;
- a reviewed response action group.

Keep transcript text, private route warnings, and format diagnostics on readable surfaces. A glass orb with a moving waveform is not a sufficient status language. If the app does not have measured amplitude or output data, do not render an invented waveform.

Respect reduced transparency, high contrast, Dynamic Type, and reduced motion. Provide an opaque fallback and do not use material blur behind a long transcript or a dense route sheet.

## 5. Route and privacy card

The route card should answer three questions:

1. Where is input coming from?
2. Where is output going?
3. What will happen if that route changes?

Example structure:

~~~text
Audio route
  Input: Bluetooth headset microphone
  Output: Bluetooth headset
  Voice processing: On for voice chat
  Privacy: Private route; output pauses if headset disconnects
  Action: Change route / Stop listening
~~~

When headphones disconnect, do not silently send a private response through the speaker. Show a route-change state and require the product’s defined resume policy. A route card is a communication contract, not a device-debug dump.

## 6. Voice-processing disclosure

If voice processing is enabled, explain it in plain language: it helps two-way voice communication manage echo and levels. Offer an advanced disclosure for technical details such as AGC, bypass, or hardware voice-call processing, but do not make a low-level Boolean the primary UI.

Use a status pattern:

| State | UI copy |
| --- | --- |
| Requested | “Preparing voice processing” |
| Enabled | “Voice processing on” |
| Disabled | “Voice processing off” |
| Unavailable | “Voice processing unavailable on this route” |
| Reconfiguring | “Reconnecting audio…” |

When changing the state requires stopping or reconfiguring the engine, disable duplicate controls and preserve the user’s intent. Do not expose a toggle that appears immediate while the engine is still running with the previous policy.

## 7. Agent interaction design

An on-device voice agent needs a visible separation between capture, interpretation, and response:

~~~text
Listening
  -> transcript/intent preview
  -> proposal or action review
  -> Speaking locally / authorized call action
~~~

For low-friction tasks, the user may pre-authorize a limited response policy, but the UI should still expose Stop and Mute. For sensitive actions, show the proposed response or destination before output. A model response is not a fact and is not automatically authorized to be spoken into a call.

Use short, human-readable status copy rather than streaming internal model tokens. Include a fallback when the local model is unavailable: continue with deterministic commands, show a transcript, or stop safely.

## 8. Accessibility and alternate input

Voice I/O should not assume that a person can hear, see, or use a touch gesture:

- label the microphone, mute, stop, resume, and route controls;
- expose listening/processing/speaking/route states as accessibility values;
- use adjustable actions for input/output level settings where appropriate;
- make Stop and Mute available through VoiceOver, Switch Control, Voice Control, keyboard, and pointer paths;
- support Dynamic Type without hiding privacy or call state;
- announce only meaningful transitions, not every audio buffer or meter update;
- provide text alternatives for agent output and status;
- preserve focus when route changes or permission failures update the screen;
- support reduced motion and high contrast;
- do not rely on sound alone for an active-microphone indicator.

Test the physical microphone/speaker route with VoiceOver active, because the app’s own response audio can overlap with system accessibility speech.

## 9. Call and far-end language

The UI should use distinct terms:

| Meaning | Copy |
| --- | --- |
| Local microphone capture | “Listening on this device” |
| Local response | “Speaking on this device” |
| Communication session | “In a voice call” |
| Audio authorized into call | “Speaking to the call” |
| Far-end unverified | “Call audio sent; remote hearing not verified” only in diagnostics |

Do not display “Delivered” when the app only created a local buffer. A local call UI, an `AVAudioSession` active route, and an AI completion cannot prove that a remote participant heard the intended words.

## 10. Failure states

| Failure | Design response |
| --- | --- |
| Permission denied | Explain microphone requirement and settings recovery |
| No input hardware | State that the route has no usable microphone |
| Zero input format | Retry after session/route change; do not start tap |
| Voice processing unavailable | Continue only if the product’s fallback is safe |
| Route changed | Pause/reconfigure; do not expose private output |
| Interruption began | Pause and preserve state |
| Interruption ended without resume option | Require user action |
| Media services reset | Reinitialize audio objects and wait for user resume |
| AI unavailable | Keep manual/local fallback |
| Call/uplink permission missing | Keep local mode; do not silently inject |
| Physical output unverified | Avoid “heard” or “delivered” language |

Use error copy that explains the layer that failed: permission, session, hardware format, graph, processing, route, communication, model, or physical proof.

## 11. Review checklist

- [ ] The screen names the actual voice-I/O lane.
- [ ] Permission, hardware-ready, listening, processing, speaking, mute, and stopped states are distinct.
- [ ] Input and output routes are visible in human language.
- [ ] Headphone disconnect privacy behavior is explicit.
- [ ] Voice-processing status is explained without exposing a raw Boolean as the experience.
- [ ] Liquid Glass groups functional controls and has an opaque fallback.
- [ ] Stop/mute and route recovery are accessible through non-touch input.
- [ ] AI output is separated from capture and call authorization.
- [ ] The UI does not claim far-end delivery from local buffer or engine state.
- [ ] Physical microphone/speaker, interruption, route, and media-reset evidence exists.

## Sources

- [Audio Engine](https://developer.apple.com/documentation/avfaudio/audio-engine)
- [AVAudioEngine](https://developer.apple.com/documentation/avfaudio/avaudioengine)
- [AVAudioIONode](https://developer.apple.com/documentation/avfaudio/avaudioionode)
- [AVAudioInputNode](https://developer.apple.com/documentation/avfaudio/avaudioinputnode)
- [AVAudioOutputNode](https://developer.apple.com/documentation/avfaudio/avaudiooutputnode)
- [Using voice processing](https://developer.apple.com/documentation/avfaudio/using-voice-processing)
- [Audio Unit Voice I/O](https://developer.apple.com/documentation/audiotoolbox/audio-unit-voice-i-o)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [AVAudioSession.Mode.voiceChat](https://developer.apple.com/documentation/avfaudio/avaudiosession/mode-swift.struct/voicechat)
- [AVAudioApplication](https://developer.apple.com/documentation/avfaudio/avaudioapplication)
- [Handling audio interruptions](https://developer.apple.com/documentation/avfaudio/handling-audio-interruptions)
- [Responding to audio route changes](https://developer.apple.com/documentation/avfaudio/responding-to-audio-route-changes)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessible controls](https://developer.apple.com/documentation/swiftui/accessible-controls)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
