# SwiftUI Audio Unit v3 host and extension route worksheet

Use this worksheet for a native iOS app that discovers and hosts an AUv3 effect, instrument, generator, or time effect, or for a product that ships its own Audio Unit extension. Fill out the host, extension, graph, parameter, and proof contracts before building the SwiftUI screen.

The [AudioToolbox Audio Unit route](../42-framework-deep-dives/41-audiotoolbox-audiounit-and-realtime-rendering.md) is the broad reference. This route focuses on the product workflow from component discovery through physical output and release.

## Route record

| Field | Decision |
| --- | --- |
| User outcome | `TBD` |
| Unit kind | effect / generator / instrument / time effect / other |
| Host target | `TBD` |
| Extension target | `TBD` / third-party component |
| Deployment target / final SDK | `iOS 26 / TBD` |
| Component type/subtype/manufacturer | `TBD` |
| Host discovery API | `AVAudioUnitComponentManager` / Audio Components / other |
| Instantiation API/options | `AVAudioUnit.instantiate` / `AUAudioUnit.instantiate` / other |
| AVAudioEngine graph | source -> unit -> mixer/output: `TBD` |
| AVAudioSession policy | category/mode/options/activation/route: `TBD` |
| Input/output bus contract | counts/formats/channel layout: `TBD` |
| Parameter contract | addresses/ranges/units/scheduling: `TBD` |
| Preset contract | factory/current/user/document: `TBD` |
| Render contract | max frames/resources/reset/real-time notes: `TBD` |
| AI proposal lane | none / typed host proposal / other: `TBD` |
| Physical proof device | `TBD` |

## 1. Justification and lane selection

- [ ] The desired behavior requires an AU plug-in or extension rather than a built-in AVAudioEngine node.
- [ ] The host can tolerate an out-of-process extension boundary on iOS.
- [ ] The product has a deterministic fallback when a component is missing or incompatible.
- [ ] The feature can meet render deadlines without UI, network, file, or model work in the callback.
- [ ] The team has a plan for parameter, preset, and document revision compatibility.
- [ ] Physical output, interruption, route, and release proof are in scope.

If all the product needs is ordinary gain, filtering, playback, or capture, prefer the higher-level AVFAudio route and avoid the extra extension surface.

## 2. Component discovery contract

| Check | Record |
| --- | --- |
| Search description | type/subtype/manufacturer/flags |
| Manager snapshot revision | timestamp/count |
| Display metadata | name/manufacturer/version/tags |
| Unit kind | effect/generator/instrument/time effect |
| Required bus formats | sample rate/channels/layout |
| Component availability | installed/disabled/incompatible |
| Registration changes | notification/refresh policy |
| Selection identity | stable description, not display name |

Keep discovery off the SwiftUI body path. The component manager owns a snapshot and publishes a revision to the view model. A user selection should be a component identity plus a graph revision.

## 3. Target and extension registration

For a product-owned AUv3 extension:

- [ ] Xcode host and Audio Unit Extension targets exist.
- [ ] Extension `Info.plist` has the documented `AudioComponents` array.
- [ ] Type, subtype, manufacturer, name, version, factory/principal class, and sandbox/resource declarations are recorded.
- [ ] The extension factory creates the correct `AUAudioUnit` subclass.
- [ ] Target membership and signing/provisioning are verified in the archive.
- [ ] The containing app and extension install as a compatible pair.
- [ ] Out-of-process loading and extension termination are tested.

For third-party units, record the provider’s component identity, supported platforms, required entitlements/configuration, version, and host-compatibility evidence.

## 4. Async instantiation contract

| State | Host behavior |
| --- | --- |
| requested | capture component and graph generation |
| loading | keep UI responsive; disable duplicate load |
| loaded | retain `AVAudioUnit`; inspect concrete type |
| configuring | negotiate buses/format and graph connections |
| ready | allocate resources/start graph according to policy |
| failed | preserve selection and offer retry/fallback |
| stale completion | discard if component/graph generation changed |

The instantiation completion can arrive on an arbitrary thread. Hop to the coordinator’s actor/main-actor boundary before mutating SwiftUI or engine state. Do not attach a stale unit after a new selection.

## 5. Graph and bus worksheet

~~~text
source node / file / input
  -> source format
  -> AU input bus
  -> Audio Unit processing
  -> AU output bus
  -> mixer/output node
  -> AVAudioSession physical route
~~~

| Item | Evidence |
| --- | --- |
| Source format | actual sample rate/channels/layout |
| Input bus count | unit inspection |
| Output bus count | unit inspection |
| Negotiated formats | graph after connection |
| Conversion | explicit or system conversion, with reason |
| Maximum frames | unit/engine value |
| Session route | current output and change policy |
| Interruption/reset | recovery action |
| Audible output | physical fixture and route record |

Do not change engine-owned connections from an arbitrary view or render callback. Define who stops/quiesces the graph, changes formats, allocates resources, and restarts it.

## 6. Parameter and preset contract

| Field | Decision |
| --- | --- |
| Parameter address | `TBD` |
| Display name/unit | `TBD` |
| Minimum/maximum/default | `TBD` |
| Discrete/value strings | `TBD` |
| Flags/read-only/automatable | `TBD` |
| KVO/tree revision | `TBD` |
| Scheduling/sample-time behavior | `TBD` |
| Factory presets | IDs/names/version |
| User presets | save/delete/error policy |
| Full/document state | schema/revision/migration |

When the parameter tree changes, invalidate stale controls and AI proposals. Apply presets only after verifying component and graph compatibility. Record partial-apply behavior and undo.

## 7. Render-resource contract

- [ ] `allocateRenderResources()` occurs after graph/format configuration.
- [ ] The unit is not rendered before resources are allocated.
- [ ] `deallocateRenderResources()` precedes incompatible reconfiguration.
- [ ] `reset()` clears transient state without losing durable user intent.
- [ ] Maximum frame sizes and discontinuities are handled.
- [ ] The render callback is bounded, nonblocking, and allocation-free after setup.
- [ ] Control-to-render state handoff is real-time safe.
- [ ] Offline rendering is tested as a separate context.
- [ ] CPU, latency, underrun, memory, energy, and thermal evidence exists.

## 8. SwiftUI surface contract

| Surface | State |
| --- | --- |
| Component browser | discovery snapshot and compatibility |
| Loading row | instantiation generation and failure |
| Unit card | name, manufacturer, ready/disconnected, bypass |
| Parameter editor | tree revision, values, units, pending/apply |
| Preset picker | factory/user/document state and migration |
| Route badge | AVAudioSession route/interruption/reset |
| Diagnostics | graph/format/render evidence |
| AI review | typed proposal, validation, acceptance, undo |

Use native controls and a functional Liquid Glass group around actions. Keep an opaque/readable fallback and expose labels, values, hints, and actions through SwiftUI accessibility modifiers.

## 9. AI proposal contract

Pass only a bounded component/graph/parameter snapshot and user goal. Require the proposal to include:

- component identity;
- graph revision;
- parameter address and proposed value;
- unit/range assumptions;
- explanation and warnings;
- proposal/model revision.

Then validate deterministically, show before/after values, require acceptance, apply on the control side, and retain an undo record. Reject when the component, parameter tree, or graph revision changed. Manual controls and factory presets remain available if the model is unavailable.

## 10. Proof package

- [ ] Component discovery snapshot and registration-change test.
- [ ] Host/extension target and signed archive inspection.
- [ ] Async instantiation, stale completion, and extension termination test.
- [ ] Bus/format/channel negotiation and route-change test.
- [ ] Parameter tree/range/unit/observer/scheduling test.
- [ ] Factory/user/document preset compatibility and undo test.
- [ ] Render-resource/reset/deallocate/reconfigure test.
- [ ] Real-time safety and Instruments evidence.
- [ ] Physical source/effect/bypass/output-route test.
- [ ] SwiftUI accessibility, Dynamic Type, alternative input, and Liquid Glass fallback test.
- [ ] AI proposal validation, acceptance, rejection, stale, undo, and fallback test.
- [ ] TestFlight and release-artifact host/extension behavior.

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
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
