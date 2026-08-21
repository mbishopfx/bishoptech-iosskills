# SwiftUI Audio Unit v3 host and extension proof matrix

Use this matrix to prove an AUv3 host/extension route from discovery through physical output. It separates metadata, instantiation, graph configuration, parameter values, render callbacks, route state, accessible UI, and release evidence.

## Evidence record

| Field | Value |
| --- | --- |
| Product / host target | `TBD` |
| Extension target / provider | `TBD` |
| SDK / deployment target | `iOS 26 / TBD` |
| Component description | type/subtype/manufacturer/flags: `TBD` |
| Unit kind | effect/generator/instrument/time effect |
| Graph revision | `TBD` |
| Parameter-tree revision | `TBD` |
| Preset/document revision | `TBD` |
| Physical device / OS / route | `TBD` |
| Archive/TestFlight build | `TBD` |
| Evidence owner / date | `TBD` |

## Claim-to-evidence matrix

| ID | Claim | Minimum evidence | Does not prove it |
| --- | --- | --- | --- |
| A1 | Component is registered correctly | Archived `AudioComponents`/component identity, signed host/extension inspection | Source class or Xcode template |
| A2 | Component discovery works | Manager/Audio Components snapshot with matching description and metadata | A hard-coded component description |
| A3 | Component metadata is truthful | Name/manufacturer/version/tags and bus capability inspection | Display name alone |
| A4 | Async instantiation works | Final target async result, retained unit, error/retry fixture | Synchronous-looking UI completion |
| A5 | Stale completions are safe | Selection/graph generation replacement test | Latest callback winning by timing |
| A6 | Extension lifetime is handled | Out-of-process load, termination, re-instantiation, and host recovery | Unit object exists in memory |
| A7 | Graph buses/formats are compatible | Actual input/output bus and negotiated format/channel evidence | Intended format in a form |
| A8 | Resources lifecycle is correct | Allocate/start/reset/deallocate/reconfigure sequence | Engine attached but not started |
| A9 | Parameter tree is usable | Address/name/range/unit/default/value-string/observer fixture | Slider changing a local variable |
| A10 | Parameter scheduling is correct | Control versus sample-time scheduling and output observation | Parameter value was assigned |
| A11 | Presets are safe | Factory/current/user/document apply, version, incompatibility, and undo tests | A preset plist or named preset |
| A12 | Render is real-time safe | Deadline, max-frame, discontinuity, no-blocking/allocation review, Instruments | A render callback ran once |
| A13 | Offline path is distinct | Explicit offline render context and completion/output fixture | Treating live rendering as offline |
| A14 | Audio reaches the intended route | Physical source/effect/bypass/route/interruption test | Nonzero output buffer or engine `isRunning` |
| A15 | SwiftUI controls are native/accessibile | Accessibility Inspector, VoiceOver, Dynamic Type, high contrast, alternative input | Glass screenshot |
| A16 | AI proposal is safe | Availability, typed snapshot/proposal, stale rejection, range validation, acceptance, undo | Model response or applied value |
| A17 | Release is ready | Host/extension archive/signing, TestFlight install, physical route and UI test | Simulator, compile, or archive key |

## Discovery and registration tests

Create fixtures for:

- exact type/subtype/manufacturer match;
- wildcard or partial searches with explicit filtering;
- no component installed;
- component installed but incompatible with the requested unit kind;
- registration-change notification and refreshed snapshot;
- duplicate display names with different identities;
- version change and stale host metadata;
- extension `Info.plist` missing or malformed `AudioComponents` entry;
- signed archive containing host and extension targets.

The browser should be driven by the discovered snapshot. Record the component description and manager revision in every load attempt.

## Instantiation and lifetime tests

| Scenario | Expected observation |
| --- | --- |
| Normal async instantiation | Unit retained; concrete type and identity match |
| Required async option | Host remains responsive; unit is not created synchronously on the main thread |
| User selects another unit while loading | Old completion is discarded by generation |
| Extension launch failure | Typed error, retry/fallback, no stale parameter editor |
| Extension terminates after attach | Host marks disconnected and can reconnect or remove |
| Host background/foreground | Graph/session policy is reapplied according to product contract |
| Unit deallocation | No callbacks mutate disposed SwiftUI state |

Capture the completion context and the hop to the owning actor/main-actor coordinator. Avoid logging private source data in extension errors.

## Bus, format, and graph tests

Test:

- input/output bus count and direction;
- sample rate and channel-count compatibility;
- interleaved/non-interleaved layout;
- mono/stereo/multichannel source fixtures;
- explicit versus implicit format conversion;
- maximum frames to render;
- connection before/after resource allocation;
- AVAudioSession route change and sample-rate change;
- interruption, media-service reset, stop, reconfigure, and restart;
- bypass A/B with a known source signal.

Record the actual negotiated format after graph connections. A parameter or render success with an incompatible source is not a green route.

## Parameter-tree tests

For each visible parameter, record:

~~~text
component identity
parameter address
name / unit / value string
minimum / maximum / default
flags and read-only state
tree revision
origin: user / preset / document / AI / automation
control value and applied value
sample-time or immediate behavior
undo record
~~~

Include out-of-range values, removed parameters, parameter-tree replacement, preset application, rapid edits, automation/scheduling, and extension reconnect. Verify that a UI control cannot write to a missing or stale parameter address.

## Preset and document tests

| Fixture | Expected result |
| --- | --- |
| Factory preset | Applies documented values for matching component/version |
| Current preset | Selection and unit state agree |
| User preset save | Persisted only after valid state and component identity |
| User preset delete | Explicit confirmation and recoverable failure |
| Document restore | Graph/parameter/preset revisions migrate or reject clearly |
| Preset from another unit | Rejected without mutation |
| Parameter removed in new version | Partial apply is reported and undo remains possible |
| Extension unavailable | Document retains intent and shows fallback |

## Render and performance tests

Use a deterministic source fixture and measure:

- minimum, typical, and maximum frame counts;
- silence and discontinuity flags;
- render-resource allocation/reset/deallocation;
- CPU and latency under steady state and parameter changes;
- underrun/overload behavior;
- memory growth and thermal state;
- concurrent control edits;
- route changes and interruption recovery;
- no render-side SwiftUI, suspension, file/network I/O, model call, arbitrary allocation, or contended lock;
- separate offline rendering behavior when applicable.

An Audio Workgroup claim needs an owned auxiliary real-time thread, a documented reason, and Instruments evidence. Merely importing the API proves nothing.

## Physical audio and accessibility matrix

| Client/route | Fixture | Evidence |
| --- | --- | --- |
| Built-in speaker | known source, bypass/effect A/B | physical listening/recording and graph record |
| Wired/Bluetooth headphones | connect/disconnect during playback | route events and audible result |
| Receiver/other route | route selection and interruption | physical output and recovery |
| VoiceOver | component browser, parameter labels, adjustable actions | physical accessibility test |
| Keyboard/pointer/Switch Control | discovery, load, parameter, preset, reconnect | input test record |
| Reduced transparency/high contrast | browser, inspector, error/recovery | UI evidence |
| Dynamic Type | long names, values, errors, presets | layout/accessibility evidence |

The output fixture must identify the source, unit, parameter state, route, and whether the unit was bypassed. `engine.isRunning`, a nonzero buffer, and a glass animation are not sufficient.

## AI and privacy evidence

If an on-device model proposes parameter values, retain:

- model availability and revision;
- bounded user goal and component/graph/parameter snapshot;
- typed proposal with parameter addresses and units;
- validation result and warnings;
- acceptance/rejection/edit history;
- applied revision and undo record;
- stale component/tree/graph rejection;
- deterministic manual/factory fallback;
- privacy and retention decision.

The model must not access or mutate a render callback. A parameter proposal is not a measured improvement in the physical output.

## Release checklist

- [ ] Final SDK host and extension compile.
- [ ] Archived component identity and `AudioComponents` configuration inspected.
- [ ] Host/extension signing and provisioning verified.
- [ ] TestFlight install preserves discovery and instantiation.
- [ ] Physical output and route recovery are tested.
- [ ] UI accessibility and Liquid Glass fallbacks are tested.
- [ ] Preset/document migration and privacy review are complete.
- [ ] Release metadata and App Review declarations are checked separately.

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
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
