# MIDI controller and audio-interface design

MIDI products feel native when the user can answer four questions at a glance:

1. What device or virtual endpoint am I using?
2. What is the app receiving or sending?
3. Is the route armed, connected, and actually active?
4. What can I safely change right now?

The visual system should make those answers easy without making the transport layer depend on visual timing.

## Design the musician’s task, not a device dashboard

Start from the outcome:

- play or audition an instrument;
- map a knob, pad, key, or pedal;
- record and review a performance;
- route one source to one or more destinations;
- inspect a MIDI 1/2 capability;
- reconnect a device after travel or interruption;
- build a repeatable setup.

Each outcome should have a focused route. A giant panel containing every endpoint, channel, message, and diagnostic is useful as a developer tool but overwhelming as the default product surface.

## Recommended native composition

### Compact route header

Show the selected source, selected destination, connection state, protocol, and a clear recovery action. Use the endpoint’s actual discovered name, but add a stable secondary identity when two similar devices exist.

Good states include:

- Not selected
- Discovering
- Needs permission
- Available
- Connected
- Receiving
- Sending
- Reconnecting
- Device changed
- Unsupported protocol
- Audio route inactive

Do not collapse all of them into a green dot.

### Device and endpoint picker

Use a system-like list with source and destination roles, transport labels, protocol badges, and last-seen metadata. A picker selection is an intent; the connection result should arrive as a separate state. Preserve the user’s choice across view recreation, but revalidate it against the current endpoint graph.

For network and Bluetooth routes, show trust and permission context near the action that needs it. The user should understand whether the app is choosing a local device, a paired peripheral, or a network contact.

### Route inspector

A route inspector can expose channel, group, transform, filtering, velocity/pressure behavior, clock or timing settings, and recording state. Use progressive disclosure:

- first show source, destination, armed state, and a compact activity indicator;
- reveal channel/group and protocol details on demand;
- place raw event and SysEx diagnostics behind an explicit developer/advanced affordance.

The inspector should never imply that a field is supported if MIDI-CI or endpoint discovery has not confirmed it.

### Mapping editor

A mapping editor should make capture and assignment explicit:

1. Choose an app action.
2. Arm “learn” for that action.
3. Move or press the intended physical control.
4. Show the observed endpoint, message type, channel/group, value range, and timestamp policy.
5. Let the user confirm, adjust, or cancel.

Avoid destructive auto-mapping. A control can be physically present but reserved, unmapped, or already assigned. Show conflicts before saving.

## Liquid Glass without turning the instrument into decoration

Liquid Glass can frame route controls, a floating inspector, transport status, or a review sheet. Keep the underlying hierarchy legible:

- one primary action per surface;
- strong contrast for armed, sending, and error states;
- stable placement for frequently used controls;
- restrained morphing when a route changes;
- no continuous material animation driven by every MIDI event.

High-rate event data belongs in a calm activity indicator, event counter, small timeline, or optional monitor. If every note changes the entire glass surface, the product becomes visually noisy and can consume energy without helping the musician.

Use the system material and control styles available to the target SDK. The goal is native coherence, not copying Apple’s iconography, exact screens, or private visual behavior.

## Audio and MIDI status are different

Use separate status groups:

| Status | Example user-facing meaning |
| --- | --- |
| MIDI transport | “Receiving from Launchpad Mini” |
| Protocol | “MIDI 2 negotiated” or “MIDI 1 compatibility mode” |
| Audio session | “Instrument output is active” |
| Audio route | “Built-in speaker” or “Headphones connected” |
| App action | “Mapping learned” or “Preset saved” |

An incoming note is not evidence that sound rendered. A running audio engine is not evidence that the selected MIDI endpoint is receiving. Keep the language precise.

## Accessibility and alternate input

Audio-only feedback excludes users and is also poor debugging. Every important status should have visible text and a VoiceOver description. Support:

- Dynamic Type and text expansion;
- VoiceOver labels that include source, destination, channel, and state;
- buttons instead of gesture-only controls for arm, send, stop, and confirm;
- keyboard/controller alternatives for mapping and navigation;
- reduced-motion behavior for glass transitions and meters;
- a non-color indicator for connection, warning, and armed states;
- a reviewable event list rather than an audio-only monitor.

For a touch instrument, ensure the hit target remains usable when text or accessibility settings grow. For a control surface, do not require precise simultaneous gestures to recover from a route error.

## AI suggestions should feel like setup help

Useful AI surfaces are bounded and reversible:

- “These three controls moved together; suggest a macro?”
- “This destination is MIDI 1; show what precision may be lost.”
- “Explain this device profile in plain language.”
- “Draft a starting map for the selected app actions.”

Show the observed evidence beneath the suggestion. Let the user accept individual changes, preview the result, and undo. The AI should not silently arm a route, connect a network peer, send SysEx, change a device profile, or write a persistent mapping.

## Empty, failure, and recovery states

Design the route before the happy path:

- no endpoint found;
- endpoint disappeared while editing;
- permission denied;
- Bluetooth service missing;
- network session disabled;
- source connected but no events received;
- destination accepted the send but audio is silent;
- MIDI 2 negotiation unavailable;
- event queue overflow;
- app backgrounded or audio interrupted.

Each state needs a next action that is safe and specific. “Try again” is weaker than “Reconnect the selected Bluetooth MIDI device” or “Choose a destination that supports MIDI 2.”

## Sources

- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles)
- [Playing audio](https://developer.apple.com/design/human-interface-guidelines/playing-audio)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [CoreMIDI](https://developer.apple.com/documentation/coremidi/)
- [MIDINetworkSession](https://developer.apple.com/documentation/coremidi/midinetworksession)
- [MIDI Bluetooth](https://developer.apple.com/documentation/coremidi/midi-bluetooth)
- [Incorporating MIDI 2 into your apps](https://developer.apple.com/documentation/coremidi/incorporating-midi-2-into-your-apps)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)

***
