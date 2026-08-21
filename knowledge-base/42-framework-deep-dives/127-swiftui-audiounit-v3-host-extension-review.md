# SwiftUI Audio Unit v3 host and extension review

This is the focused iOS 26 route for finding, instantiating, hosting, controlling, and proving an AUv3 Audio Unit from a native SwiftUI app. The existing [AudioToolbox and Audio Units deep dive](41-audiotoolbox-audiounit-and-realtime-rendering.md) explains low-level rendering broadly. This page focuses on the complete host/extension product boundary: component identity, asynchronous instantiation, out-of-process lifetime, bus formats, render resources, parameters, presets, SwiftUI controls, and physical output.

The route is:

~~~text
user feature intent
  -> AudioComponentDescription / AVAudioUnitComponentManager discovery
  -> selected component metadata and capability review
  -> asynchronous AVAudioUnit / AUAudioUnit instantiation
  -> AVAudioEngine graph and bus-format negotiation
  -> parameter tree / preset / control-state projection
  -> allocate render resources
  -> realtime render block and AVAudioSession route
  -> SwiftUI status and accessible controls
  -> physical output, archive, TestFlight, and release proof
~~~

An Audio Unit object, a parameter value, or a render callback proves an internal framework event. It does not prove that the selected effect or instrument processed the intended source, that the engine was running, or that a person heard the correct physical output.

## 1. Select the hosting lane

| Need | Route | Main owner |
| --- | --- | --- |
| Ordinary playback/capture/effects | `AVAudioEngine` and built-in AVFAudio nodes | App audio graph |
| Host a third-party AUv3 effect/instrument | `AVAudioUnitComponentManager` -> `AVAudioUnit.instantiate` -> engine | Host app plus extension process |
| Implement a custom AUv3 | Audio Unit Extension target and `AUAudioUnit` subclass/factory | Extension target |
| Expose simple control values | `AUParameterTree` and host controls | Audio Unit control surface |
| Save a tuned configuration | Factory preset, current preset, full state, or user preset | Unit plus host/document policy |
| Render with hard timing | Cached `renderBlock` / unit internal render path | Real-time audio boundary |
| Make a model choose parameters | Typed proposal -> range/format/state validation -> user approval | Host control side |

The minimum viable route for a host is not “instantiate a class in a button.” It is component discovery, async creation, graph ownership, format negotiation, resource lifecycle, route/interruption recovery, control projection, and proof.

## 2. Component identity and registration

`AudioComponentDescription` identifies an audio component by type, subtype, manufacturer, flags, and flags mask. The host can use it to search with `AVAudioUnitComponentManager` or the Audio Components APIs. Treat this identity as data that belongs in a target/release record, not as a string guessed from a display name.

For an AUv3 app extension, Apple documents an `AudioComponents` item in the extension bundle’s `Info.plist`. The entry identifies the component and its factory. The extension’s principal class can conform to `AUAudioUnitFactory`, which creates the concrete `AUAudioUnit` subclass. The containing app and extension must be built, signed, and installed as the intended pair.

Record:

| Identity | Evidence |
| --- | --- |
| Type/subtype/manufacturer | `AudioComponentDescription` from the archived product |
| Name/version | Component metadata and user-facing localization |
| Factory/extension principal class | `Info.plist` and extension target inspection |
| Sandbox/resource declaration | Final extension configuration and review |
| Host compatibility | Required platform, bus, channel, and format support |
| Target version | Host and extension SDK/deployment/archive values |

Do not infer that a host can instantiate a component because a class with a similar name exists in source. iOS AUv3 components run out-of-process as app extensions; discovery and instantiation are system registration operations.

## 3. Discover components without opening them

`AVAudioUnitComponentManager` provides registered component metadata and can search using an `AudioComponentDescription`, predicates, or a test block. The manager also exposes standard and user tags. Use metadata to build a selection screen without instantiating every unit.

Discovery state should distinguish:

- no matching component;
- matching component found but incompatible with the requested graph;
- component found and instantiation pending;
- instantiation failed;
- unit instantiated but resource/format configuration failed;
- unit ready and connected;
- unit disconnected or extension terminated.

Subscribe to registration changes when the product needs to update a plug-in list after installation or removal. Do not let the SwiftUI view perform discovery on every body evaluation. A dedicated component manager owns a snapshot and a revision.

Component metadata is not a capability guarantee. Inspect bus counts, supported formats, channel layouts, parameter tree, factory presets, user-preset support, and the host’s current engine/session before offering an action.

## 4. Instantiate asynchronously and retain the result

Apple documents `AVAudioUnit.instantiate(with:options:completionHandler:)` and its async form. The completion handler can arrive on an arbitrary thread, and the returned `AVAudioUnit` must be retained. Components that require asynchronous instantiation must be created asynchronously when used with `AVAudioEngine`.

Use an actor or one main-actor coordinator for control state:

~~~text
selected description
  -> instantiate generation 12
  -> completion on arbitrary context
  -> hop to control owner
  -> verify generation and component identity
  -> inspect unit / attach to graph
  -> publish ready or typed failure
~~~

Do not block the main thread while loading an extension. Do not attach a unit from a stale completion after the user selected a different component. If the extension process dies, invalidate the unit, preserve the user’s source/graph intent, and make retry or fallback explicit.

The concrete subclass returned by the system may depend on the component type, such as `AVAudioUnitEffect`, `AVAudioUnitGenerator`, `AVAudioUnitMIDIInstrument`, or `AVAudioUnitTimeEffect`. The host should use the documented host surface and validate the expected kind before wiring the graph.

## 5. Host and extension are different lifetimes

The host app owns user intent, graph composition, session policy, source media, SwiftUI, and release diagnostics. The extension owns the unit implementation, render resources, parameters, and extension-side state. The extension can be loaded out-of-process and can be terminated or re-created independently of the host view.

| State | Host app | Extension |
| --- | --- | --- |
| User selected effect | Owns | Receives component instantiation |
| Source/engine graph | Owns | Receives render calls through host |
| Parameter editor | Projects | Exposes parameter metadata/values |
| Render resources | Coordinates graph lifecycle | Allocates/deallocates unit resources |
| Real-time audio | Hosts engine/render requests | Implements internal render behavior |
| Preset/document | Owns persistence policy | Provides state/preset contract |
| Failure | Shows recovery/fallback | Returns typed status and can be re-created |

Never store SwiftUI references, view models, or host-only file paths in an extension render object. Never assume a host app’s in-memory `AVAudioEngine` survives extension termination. Use stable graph and parameter revisions for recovery.

## 6. Negotiate buses and formats before resources

`AUAudioUnitBus` and `AUAudioUnitBusArray` describe input/output connection points. Before allocating render resources, inspect and set the format and channel layout through the host’s documented graph boundary. Confirm:

- input/output bus count;
- sample rate and channel count;
- interleaved versus non-interleaved layout;
- supported channel layouts and source compatibility;
- maximum frames to render;
- effect versus generator direction;
- whether the graph can connect the unit without an implicit conversion;
- whether the selected AVAudioSession route changes the usable format.

The lifecycle is:

1. instantiate the unit;
2. inspect busses, formats, capabilities, and parameters;
3. configure the engine graph and session policy;
4. allocate render resources;
5. start or render;
6. reset when the host requests a transient reset;
7. deallocate resources before changing configuration or disposing the unit.

A format shown in a SwiftUI inspector is an intended configuration. Capture the actual post-negotiation format in diagnostics and test route changes, sample-rate changes, Bluetooth transitions, and interruption recovery.

## 7. Parameter trees and control ownership

`AUAudioUnit.parameterTree` organizes the unit’s parameters. Hosts can discover parameters and observe changes. A custom unit should expose stable parameter identifiers, names, ranges, units, default values, flags, and value strings appropriate to the product.

Keep control state separate from render state:

~~~text
SwiftUI Slider / Toggle / Picker
  -> validated ParameterEdit
  -> AUParameterTree value or scheduleParameterBlock
  -> audio-unit control/render handoff
  -> observed value / error / undo record
~~~

Parameter edits need a generation and source:

| Field | Meaning |
| --- | --- |
| parameter address/identifier | Unit-owned stable identity |
| proposed value | User or AI candidate before validation |
| applied value | Value accepted by the unit/host |
| origin | user, preset, document restore, AI proposal, automation |
| graph revision | Graph state to which the edit belongs |
| timestamp/sample time | Control or scheduled timing context |

Do not call a parameter setter from a SwiftUI body. Do not allow an AI proposal to write a value outside the parameter’s range, unit, or graph state. If the unit’s parameter tree changes, refresh the host snapshot and invalidate controls that no longer exist.

## 8. Real-time render boundary

The host should fetch and cache `renderBlock` before invoking it from a real-time context. Apple documents that the render block calls the subclass’s `internalRenderBlock` and that subclasses should override the internal render block rather than the host-facing render property.

The render boundary must be:

- bounded by the requested frame count;
- allocation-free after render-resource allocation;
- nonblocking;
- free of UI, Swift concurrency suspension, file/network I/O, and model inference;
- safe for silence, discontinuity, timestamps, and reset;
- synchronized with a control-to-render snapshot that cannot be torn;
- measurable for CPU, latency, underruns, memory, and thermal behavior.

`renderingOffline` changes the no-realtime-deadline context; it does not make the ordinary live render callback a safe place for arbitrary blocking work. Use offline behavior only when the host explicitly renders offline and test the separate path.

An Audio Workgroup can coordinate owned auxiliary real-time threads, but it does not make a UI or model call safe. First prove the normal framework render thread is insufficient, then document and measure the workgroup choice.

## 9. Presets and document state

Factory presets are developer-provided configurations. A unit can also support current presets, full state, document state, and user presets. Treat those as different persistence lanes:

| State lane | Use |
| --- | --- |
| Factory preset | Stable selectable starting configuration |
| Current preset | Unit’s selected preset projection |
| Full state | Persistable unit parameter/configuration snapshot |
| Document state | Snapshot associated with a host document/session |
| User preset | User-owned named configuration with lifecycle/errors |

Before applying a preset, verify component identity, version compatibility, parameter addresses, graph format, and document revision. Do not silently apply a preset from a different unit or version. A preset can restore parameter values while the unit is missing, disconnected, or routed to an incompatible format.

## 10. SwiftUI and Liquid Glass control design

The native host surface should prioritize the audio source and current route, then expose the selected unit’s controls:

- component search and compatibility summary;
- loading/ready/disconnected/error status;
- input/output bus and format summary;
- compact parameter controls with labels, values, units, and ranges;
- factory/user preset selection;
- reset/undo/retry/fallback actions;
- CPU/latency/resource diagnostics outside the primary control flow;
- audio-session route and interruption state;
- optional AI proposal sheet with before/after values and validation errors.

Apply Liquid Glass to a functional inspector or compact transport/control group. Keep sliders, values, and labels readable in large text and high contrast. Use a solid fallback for reduced transparency. Do not put a glass animation between a person and the source/route state, and do not show fake meters unless they represent measured audio data.

## 11. Optional on-device AI proposal

AI can propose a starting preset, a parameter adjustment, a mapping from a user goal to controls, or an explanation of a format mismatch. It cannot directly mutate the live render path.

The safe route is:

~~~text
user goal + current component/parameter snapshot
  -> model availability/privacy check
  -> typed proposal with component and graph revision
  -> deterministic parameter/range/format validation
  -> user review and acceptance
  -> control-side apply / undo record
  -> measured render and physical-output review
~~~

If the unit disappears or its parameter tree changes, reject the stale proposal. If the model is unavailable, keep the manual controls and factory presets usable. Preserve the proposal, validation result, acceptance, and applied parameter revision when the AI route matters to a user-facing outcome.

## 12. Proof boundary

| Claim | Evidence |
| --- | --- |
| Component is registered | Archived `Info.plist`, component identity, signed host/extension install |
| Discovery works | `AVAudioUnitComponentManager` snapshot and registration-change observation |
| Instantiation works | Async creation result, retained unit, target error/fallback fixture |
| Buses/formats are compatible | Actual negotiated formats/channel layouts and graph connection test |
| Resources are safe | Allocate/start/reset/deallocate/reconfigure lifecycle evidence |
| Parameters are correct | Parameter tree identifiers/ranges/values/observer and scheduling fixtures |
| Presets are safe | Factory/current/user/document state version and compatibility tests |
| Render is real-time safe | Render deadline, CPU/latency/underrun, no-blocking review and Instruments evidence |
| Output is audible | Physical device route, source fixture, effect bypass/A-B, and listener/recording evidence |
| SwiftUI is native | Accessibility Inspector, Dynamic Type, input, reduced transparency/motion, and recovery tests |
| AI proposal is safe | Availability, typed proposal, stale rejection, validation, acceptance, undo, fallback |
| Release is ready | Host/extension archive, signing, TestFlight installation, physical render, metadata/review |

The [route worksheet](../50-capability-recipes/158-swiftui-audiounit-v3-host-extension-review-route.md), [design page](../21-design-deep-dives/155-swiftui-audiounit-v3-host-extension-review-design.md), [proof matrix](../60-verification/152-swiftui-audiounit-v3-host-extension-proof-matrix.md), and [recipes](../70-code-recipes/170-swiftui-audiounit-v3-host-extension-review-recipes.md) carry the implementation record.

## Sources

- [Audio Components](https://developer.apple.com/documentation/audiotoolbox/audio-components)
- [AudioComponentDescription](https://developer.apple.com/documentation/audiotoolbox/audiocomponentdescription)
- [AudioComponentFindNext](https://developer.apple.com/documentation/audiotoolbox/audiocomponentfindnext%28_%3A_%3A%29)
- [AVAudioUnitComponentManager](https://developer.apple.com/documentation/avfaudio/avaudiounitcomponentmanager)
- [AVAudioUnitComponent](https://developer.apple.com/documentation/avfaudio/avaudiounitcomponent)
- [AVAudioUnit](https://developer.apple.com/documentation/avfaudio/avaudiounit)
- [AVAudioUnit.instantiate(with:options:completionHandler:)](https://developer.apple.com/documentation/avfaudio/avaudiounit/instantiate%28with%3Aoptions%3Acompletionhandler%3A%29)
- [Incorporating Audio Effects and Instruments](https://developer.apple.com/documentation/audiotoolbox/incorporating-audio-effects-and-instruments)
- [AUAudioUnit](https://developer.apple.com/documentation/audiotoolbox/auaudiounit)
- [AUAudioUnitFactory](https://developer.apple.com/documentation/audiotoolbox/auaudiounitfactory)
- [AUAudioUnitBus](https://developer.apple.com/documentation/audiotoolbox/auaudiounitbus)
- [AUAudioUnitBusArray](https://developer.apple.com/documentation/audiotoolbox/auaudiounitbusarray)
- [AUAudioUnit.parameterTree](https://developer.apple.com/documentation/audiotoolbox/auaudiounit/parametertree)
- [AUAudioUnit.renderBlock](https://developer.apple.com/documentation/audiotoolbox/auaudiounit/renderblock)
- [AUAudioUnit.renderingOffline](https://developer.apple.com/documentation/audiotoolbox/auaudiounit/isrenderingoffline)
- [AUAudioUnit.factoryPresets](https://developer.apple.com/documentation/audiotoolbox/auaudiounit/factorypresets)
- [AUAudioUnitPreset](https://developer.apple.com/documentation/audiotoolbox/auaudiounitpreset)
- [Audio Unit v3 Plug-Ins](https://developer.apple.com/documentation/audiotoolbox/audio-unit-v3-plug-ins)
- [Creating an audio unit extension](https://developer.apple.com/documentation/avfaudio/creating-an-audio-unit-extension)
- [AVAudioEngine](https://developer.apple.com/documentation/avfaudio/avaudioengine)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Audio Workgroups](https://developer.apple.com/documentation/audiotoolbox/understanding-audio-workgroups)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
