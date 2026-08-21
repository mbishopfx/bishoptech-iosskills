# SwiftUI Audio Unit v3 host and extension design review

This page translates the [AUv3 host and extension deep dive](../42-framework-deep-dives/127-swiftui-audiounit-v3-host-extension-review.md) into a native SwiftUI design system. The host app owns the user’s audio intent and control surface. The extension owns an Audio Unit implementation that can be loaded out of process. The UI must make those boundaries understandable without exposing raw Core Audio machinery as the primary experience.

## 1. Design the audio outcome, not the plug-in API

Start with the person’s goal:

| User goal | Native surface |
| --- | --- |
| Shape the sound | Effect card with source, bypass, preset, and key controls |
| Add a generator/instrument | Source/track card with level, patch, and transport state |
| Explore available units | Searchable component list with compatibility summaries |
| Restore a saved sound | Preset/document revision with apply, conflict, and undo state |
| Tune a parameter | Labeled native control with range, unit, current value, and reset |
| Diagnose a failure | Plain-language route, format, extension, and recovery state |
| Ask AI for a starting point | Reviewable before/after proposal, never an automatic live mutation |

Avoid designing the screen around `AudioComponentDescription`, `AUParameterAddress`, or a raw parameter tree. Those are implementation contracts. Translate them into names, units, ranges, and current audio state.

## 2. Host hierarchy

A good iOS host usually has a focused graph screen and a detail inspector:

~~~text
NavigationStack
  └─ Audio Graph
       ├─ source / input status
       ├─ effect or instrument chain
       │    ├─ component name and manufacturer
       │    ├─ ready/loading/disconnected state
       │    ├─ bypass and preset controls
       │    └─ compact key parameters
       ├─ output route and interruption state
       └─ inspector sheet
            ├─ full parameter tree
            ├─ bus and format details
            ├─ factory/user presets
            ├─ AI proposal review
            └─ diagnostics
~~~

Do not make a plug-in’s entire parameter tree appear as a dense spreadsheet by default. Surface the parameters the component identifies as important, then provide a progressive disclosure path for advanced controls. Keep the audio source and route visible enough that a user can understand what is being changed.

## 3. Component browser design

The component browser should use the system’s metadata without promising compatibility:

- name and manufacturer;
- effect/instrument/generator category;
- supported tags or search text;
- loading/ready/error status;
- compatible source/output summary;
- version and extension availability;
- one primary action: Add, Load, or Retry.

Use `List`, `NavigationSplitView`, or a searchable collection rather than a custom glass carousel. A row can show an icon or system symbol, but the text must carry the category and state. If a component is found but cannot connect to the current graph, say “Available, incompatible with this route” and explain the needed format or channel change.

Do not let the browser instantiate every component during scrolling. Discovery is a snapshot; instantiation is an explicit action owned by a loading coordinator.

## 4. Loading and out-of-process states

The user needs to know whether a unit is being found, loaded, connected, or actually processing audio:

~~~text
unselected
  -> selected
  -> instantiation pending
  -> extension loaded
  -> format negotiation
  -> render resources allocated
  -> connected / processing
  -> interrupted / disconnected / failed
~~~

Use clear labels:

- “Loading audio unit” means asynchronous instantiation is running.
- “Extension loaded; configuring format” means the object exists but is not yet connected.
- “Ready” means the engine graph and required resources are configured.
- “Processing” means the host has evidence that the graph is running, not just that a parameter changed.
- “Extension unavailable” means the host cannot use this component and should offer fallback or removal.

When an extension terminates, preserve the user’s graph intent and offer Reconnect. Do not silently show a stale parameter panel as if the unit remained active.

## 5. Parameter controls and semantic values

Every visible parameter should have:

1. a localized name;
2. a value with an appropriate unit or semantic label;
3. a range or discrete option explanation;
4. a visible current state;
5. a reset or undo path;
6. an accessibility label, value, and action.

Use a Slider for a continuous value, Toggle for a true/false state, Picker for a small discrete set, and a disclosure or custom editor for advanced parameter groups. Do not expose a raw normalized `0.5` when the unit has a meaningful value such as `-6 dB`, `440 Hz`, or `30%`.

Keep value edits distinct from observed values. While a person drags, show the pending/applied state appropriate to the unit. If a render-time parameter is scheduled at a sample time, do not present a control change as instantaneous if the audio graph applies it later.

## 6. Liquid Glass interaction design

Liquid Glass is useful when it groups controls above an active graph:

- transport and bypass controls;
- a compact output-route/status pill;
- a contextual preset or AI-review action group;
- a floating inspector action that remains anchored to the selected unit.

Keep the source waveform, parameter labels, and diagnostic text on surfaces with sufficient contrast. Avoid placing a high-density parameter editor over moving media with multiple translucent layers. Use standard controls so the system can adapt their treatment, and provide an opaque fallback for reduced transparency and high-contrast settings.

Glass should express action proximity, not plug-in status. A glass panel can be visible while an extension is disconnected, so pair material with honest text state. Do not use glow, scale, or fake meter animation to imply that a render callback reached a speaker.

## 7. Presets and reversible actions

Factory presets are choices from the plug-in. User/document presets are product data. Keep them visually and behaviorally distinct:

| Preset lane | UI treatment |
| --- | --- |
| Factory | “Factory presets” picker, read-only source |
| Current | Current selection and applied state |
| User | Save, rename, replace, delete, conflict handling |
| Document | Attached to the project/document revision |
| AI proposal | Draft comparison requiring acceptance |

Applying a preset should show the component and graph revision. If a parameter is unavailable or a format changed, report partial application and offer undo. Never overwrite a user preset or document state silently because an extension updated.

## 8. Accessibility and alternative input

Audio apps often become dense and gesture-heavy. Use the same native accessibility discipline as the rest of the platform:

- label every parameter with name and unit;
- expose slider adjustments through VoiceOver adjustable actions;
- make bypass, reset, preset, and reconnect actions reachable without a custom gesture;
- support Dynamic Type in the browser, inspector, and errors;
- preserve keyboard, pointer, Switch Control, Voice Control, and game-controller paths where the target supports them;
- avoid conveying important render or route state only through a meter or color;
- make focus stable when parameter values update from automation or a preset;
- announce meaningful state transitions without announcing every render callback;
- make reduced motion and reduced transparency usable;
- keep controls reachable while an interruption or extension failure sheet is present.

Audio is not a substitute for visual status. A person who cannot hear the output still needs to know whether the route is connected, while a person who cannot see the screen needs accessible values and action results.

## 9. AI review surface

An AI proposal should look like a design review, not a magic “Make it better” button:

~~~text
current component + graph + parameter snapshot
  -> user goal
  -> proposal card
       before value / proposed value / reason / warnings
  -> user accepts, edits, or rejects
  -> deterministic validation
  -> apply with undo
~~~

Show the component identity, parameter names, units, graph revision, and validation warnings. If a parameter is outside range or the unit is gone, explain that the proposal is stale. Keep the manual control route visible. Do not say the AI “heard” or “fixed” the audio unless a separate physical-output review supports that claim.

## 10. Failure and trust states

| Situation | Design response |
| --- | --- |
| No components found | Explain registration/availability and show a built-in fallback |
| Instantiation failed | Preserve selection, show retry/remove, include a copyable diagnostic |
| Bus/format mismatch | Show source/output formats and a safe reconfiguration choice |
| Extension disconnected | Mark controls unavailable and offer reconnect |
| Render overload | Show an actionable performance state, not a decorative spinner |
| Route interrupted | Preserve graph intent; make resume/reconfigure explicit |
| Preset incompatible | Report partial or rejected apply and offer undo |
| Parameter tree changed | Refresh controls and invalidate stale proposals |
| AI unavailable | Keep manual controls and factory presets available |
| Physical output unproven | Say “Graph running; output route not verified” |

Do not hide an Audio Unit error behind “Something went wrong.” Include the layer that failed: discovery, instantiation, format, resource allocation, render, route, or release artifact.

## 11. Review checklist

- [ ] Component browser uses metadata and explicit instantiation.
- [ ] Loading, extension, format, resource, processing, and disconnected states are distinct.
- [ ] Parameter labels use meaningful units and accessible values.
- [ ] Presets, document state, and AI proposals are different persistence lanes.
- [ ] Liquid Glass groups functional actions without obscuring parameters or diagnostics.
- [ ] Reduced transparency, high contrast, Dynamic Type, reduced motion, and alternative input work.
- [ ] Extension termination does not leave stale controls presented as active.
- [ ] AI proposals include before/after values, graph revision, validation, acceptance, and undo.
- [ ] The UI does not claim physical audio from a render callback or parameter update.
- [ ] Physical output, archive, TestFlight, and release evidence are recorded separately.

## Sources

- [Audio Components](https://developer.apple.com/documentation/audiotoolbox/audio-components)
- [AVAudioUnitComponentManager](https://developer.apple.com/documentation/avfaudio/avaudiounitcomponentmanager)
- [AVAudioUnitComponent](https://developer.apple.com/documentation/avfaudio/avaudiounitcomponent)
- [AVAudioUnit](https://developer.apple.com/documentation/avfaudio/avaudiounit)
- [Incorporating Audio Effects and Instruments](https://developer.apple.com/documentation/audiotoolbox/incorporating-audio-effects-and-instruments)
- [AUAudioUnit](https://developer.apple.com/documentation/audiotoolbox/auaudiounit)
- [AUAudioUnitFactory](https://developer.apple.com/documentation/audiotoolbox/auaudiounitfactory)
- [AUAudioUnit.parameterTree](https://developer.apple.com/documentation/audiotoolbox/auaudiounit/parametertree)
- [AUAudioUnit.renderBlock](https://developer.apple.com/documentation/audiotoolbox/auaudiounit/renderblock)
- [AUAudioUnit.factoryPresets](https://developer.apple.com/documentation/audiotoolbox/auaudiounit/factorypresets)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessible controls](https://developer.apple.com/documentation/swiftui/accessible-controls)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
