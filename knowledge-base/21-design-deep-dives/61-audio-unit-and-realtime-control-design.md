# Audio Unit and real-time control design

Low-level audio products feel native when the user can understand the sound route without being exposed to every pointer, bus, and render flag. The visual product is a control and review surface; the audio render path is a separate real-time system.

## Design the sound task first

Start with a concrete outcome:

- load an effect or instrument;
- choose a preset;
- map a MIDI controller;
- inspect an input/output format;
- record or monitor a signal;
- recover after an interruption or route change;
- understand why a host cannot instantiate a component;
- tune a custom audio unit.

Do not make “Audio Unit dashboard” the default information architecture. Most users need a clear sound route and a safe primary action.

## A native control hierarchy

### Route header

Show:

- selected component or instrument;
- source and destination;
- active, paused, interrupted, or unavailable state;
- preset;
- a clear recovery action.

The component’s discovered name is useful, but type/subtype/manufacturer and version belong in an advanced detail view.

### Parameter and preset surface

Use semantic controls for parameters:

- sliders with values and units;
- toggles for discrete settings;
- menus for modes and bus choices;
- reset and undo;
- explicit save/apply for persistent presets.

Keep parameter ranges and availability grounded in the current AUParameterTree or documented unit state. Do not render controls for a parameter that the current component does not expose.

### Format and latency inspector

Progressively disclose sample rate, channel count, bus direction, maximum frames, latency, and route status. A format mismatch should tell the user what they can change:

- choose a compatible route;
- reconnect the engine;
- load a different component;
- continue with a converted format;
- cancel without changing the live graph.

Avoid implying that a single latency number describes the entire physical path. Distinguish unit latency, output presentation latency, engine state, and user-perceived result where the target exposes them.

## Liquid Glass with a real-time boundary

Liquid Glass works well for:

- a floating preset inspector;
- a contextual parameter sheet;
- a route/status cluster;
- a reviewable AI proposal;
- an interruption or recovery panel.

It should not wrap every meter or animate on each audio buffer. Keep render health, overload, and silence indicators calm and readable. Provide a plain fallback for reduced transparency, reduced motion, low power, or unavailable material effects.

## Audio status is not audio truth

Use distinct labels:

| State | Meaning |
| --- | --- |
| Unit loaded | The component was instantiated |
| Resources allocated | The unit accepted the current render configuration |
| Engine running | The host graph is running |
| Render observed | A render callback or observer ran |
| Output route active | AVAudioSession and output route are active |
| Audible result | A user/device test confirms the intended output |

Only claim the last state when the product has evidence appropriate to its feature. A loaded unit is not a playing instrument.

## Accessible audio controls

Audio products need visual and semantic alternatives:

- VoiceOver labels for component, preset, parameter, and value;
- Dynamic Type in inspectors and recovery sheets;
- keyboard/controller alternatives for common parameter changes;
- non-audio overload and connection indicators;
- reduced-motion behavior for meters and glass transitions;
- no gesture-only reset, arm, stop, or confirm action;
- localized units, numbers, and long plug-in names.

Do not require a user to hear a tone to discover that a route is active. Do not make a flashing meter the only evidence of input.

## AI as a reviewable producer assistant

Good AI surfaces:

- “Suggest a starting filter cutoff for this selected recording.”
- “Explain why the component cannot connect to this bus.”
- “Group these parameters into a simpler control page.”
- “Draft a preset name from the user’s approved session notes.”

Show the parameter evidence and the exact proposed changes. Require review before applying a live graph mutation or saving a preset. The AI must not operate in the render callback or silently change an active audio route.

## Extension and host states

Design for:

- component not found;
- extension disabled or unavailable;
- host cannot instantiate;
- unsupported format or channel count;
- resources not allocated;
- engine stopped;
- audio interruption;
- route change/sample-rate change;
- render overload or silence;
- preset load/save failure;
- extension process or host termination.

Every state should have a safe next action and preserve the user’s non-destructive work.

## Sources

- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Playing audio](https://developer.apple.com/design/human-interface-guidelines/playing-audio)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Audio Toolbox](https://developer.apple.com/documentation/audiotoolbox)
- [AUAudioUnit](https://developer.apple.com/documentation/audiotoolbox/auaudiounit)
- [AudioComponentDescription](https://developer.apple.com/documentation/audiotoolbox/audiocomponentdescription)
- [Understanding Audio Workgroups](https://developer.apple.com/documentation/audiotoolbox/understanding-audio-workgroups)
- [Audio Engine](https://developer.apple.com/documentation/avfaudio/audio-engine)
- [AVAudioEngine](https://developer.apple.com/documentation/avfaudio/avaudioengine)
- [AVAudioUnit](https://developer.apple.com/documentation/avfaudio/avaudiounit)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)

***
