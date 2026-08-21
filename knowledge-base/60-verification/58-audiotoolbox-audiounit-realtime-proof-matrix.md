# AudioToolbox and Audio Unit real-time proof matrix

Audio code needs stronger evidence than a view preview or a successful unit instantiation. Separate component discovery, render safety, engine output, physical audio, and release behavior.

## Evidence levels

| Level | Establishes | Does not establish |
| --- | --- | --- |
| Source inspection | API/lifecycle, component, extension, workgroup, and documented constraints | Selected SDK signatures, audio quality, render deadline |
| Compile | Types, target membership, extension shape, availability | Component discovery, physical output, no-overload behavior |
| Fixture/unit | DSP math, buffer processing, parameter validation, deterministic reset | Audio session route, host behavior, physical timing |
| Simulator/preview | SwiftUI parameter/status states, accessibility labels, fallback layouts | Render quality, hardware route, extension host integration |
| Physical device | Engine/session/output behavior, route/interruption, render stress | All hosts, devices, sample rates, release distribution |
| Signed/TestFlight | Extension discovery, entitlements/configuration, release build behavior | Universal host/device compatibility |

## Route matrix

| Claim | Minimum evidence | Failure and recovery cases |
| --- | --- | --- |
| The component exists | Named target finds the AudioComponentDescription or instantiates AVAudioUnit/AUAudioUnit | Missing component, disabled extension, unsupported host |
| The unit is configured | Busses, formats, channel counts, parameters, and lifecycle state are logged | Format mismatch, connection order error, unsupported layout |
| The unit can render | Known fixture produces expected bounded buffers at multiple frame counts | Silence flag, discontinuity, reset, maximum frames, invalid buffer |
| The render callback is real-time safe | Stress run plus Instruments/Audio System Trace shows bounded work without allocation/lock/I/O/model operations | Contended lock, allocation, log stall, deadline miss |
| AVAudioEngine route works | Engine starts with the named graph and physical output route | Interruption, route change, sample-rate change, engine stop |
| AVAudioSession route works | Session activation/category/options and output route are observed on a physical device | Denied/changed route, headphones/Bluetooth, interruption |
| Audio Unit v3 extension works | Signed containing app discovers, instantiates, configures, and renders the extension | Host termination, extension unavailable, version mismatch |
| Audio Workgroup use is justified | Custom auxiliary real-time thread exists and workgroup scheduling is measured | No custom thread, wrong workgroup, non-real-time work admitted |
| Presets/parameters work | Load, edit, validate, save, reset, and undo a named preset | Parameter missing, range mismatch, save failure |
| MIDI/audio boundary works | MIDI event and audio render/output state are recorded separately | MIDI arrives but audio is silent, audio runs without MIDI |
| Spatial component works | Named device/format test verifies the intended spatial route | Unsupported device, channel conversion, head tracking/route change |
| AI proposal is safe | Fixed snapshot creates typed proposal; range/format/lifecycle validator gates apply | Stale component, hallucinated parameter, model unavailable |
| Native UI is accessible | Dynamic Type, VoiceOver, reduced motion, keyboard/controller, localization, and fallback tasks pass | Meter-only status, focus loss, unreadable parameter names |
| Release is ready | Signed device/TestFlight artifact passes target/extension/privacy/configuration checks | Debug-only success, host mismatch, entitlement/signing drift |

## Render test record

Record:

- app/extension version/build and git revision;
- device, OS, SDK, host, and audio route;
- component description and unit version;
- sample rate, channel layout, frame count, maximum frames;
- input fixture and expected output;
- allocation/lock/logging policy;
- render duration, overload/underrun observations, CPU/memory/energy;
- interruption/route/reset/deallocation result;
- signed artifact and follow-up.

## Non-claims

Do not infer:

- audible output from a successful render call;
- low latency from a new device;
- real-time safety from a preview;
- extension compatibility from one host;
- no overload from a short Debug run;
- Audio Workgroup benefit without measurement;
- parameter support from a product name;
- AI quality from one preset.

## Sources

- [Audio Toolbox](https://developer.apple.com/documentation/audiotoolbox)
- [AUAudioUnit](https://developer.apple.com/documentation/audiotoolbox/auaudiounit)
- [AudioUnit](https://developer.apple.com/documentation/audiotoolbox/audiounit)
- [AudioUnitRenderActionFlags](https://developer.apple.com/documentation/audiotoolbox/audiounitrenderactionflags)
- [Understanding Audio Workgroups](https://developer.apple.com/documentation/audiotoolbox/understanding-audio-workgroups)
- [Workgroup Management](https://developer.apple.com/documentation/audiotoolbox/workgroup-management)
- [Audio Engine](https://developer.apple.com/documentation/avfaudio/audio-engine)
- [AVAudioEngine](https://developer.apple.com/documentation/avfaudio/avaudioengine)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Playing audio](https://developer.apple.com/design/human-interface-guidelines/playing-audio)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)

***
