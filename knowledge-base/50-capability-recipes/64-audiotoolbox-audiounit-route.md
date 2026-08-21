# AudioToolbox and Audio Unit capability route

Use this route for a custom audio effect, instrument, generator, hostable Audio Unit, low-level render callback, spatial audio component, or audio-unit extension. Start with AVFAudio and move downward only when the product requirement needs the lower-level boundary.

## Route card

| Layer | Decision |
| --- | --- |
| User outcome | Play, process, host, tune, record, or review audio |
| Default graph | AVAudioEngine, AVAudioUnit, AVAudioSession |
| Lower-level route | AudioToolbox AudioComponentDescription, AUAudioUnit, AudioUnit, render APIs |
| Extension route | Audio Unit v3 extension target and containing host app |
| Real-time route | Render resources, bounded callback, optional Audio Workgroup |
| Domain state | Component identity, bus/format, parameters, preset, lifecycle, output status |
| UI | Native parameter view, preset inspector, route/recovery state, diagnostics |
| AI | Typed parameter/preset/format proposal with deterministic validation |
| Proof | Compile, host/extension discovery, physical output, render deadline, interruption, signed release |

## Step 1: Decide whether low-level AudioToolbox is justified

Stay in AVAudioEngine when the feature is ordinary playback, capture, mixing, effects, samplers, MIDI, or graph routing. Choose AUAudioUnit or AVAudioUnit when the product hosts or implements a custom audio unit. Choose the C AudioUnit route only for legacy interop, exact component operations, or a requirement that the higher-level layer cannot express.

Write the reason in the route document. “Lower level” is not itself a product requirement.

## Step 2: Configure the target shape

Decide whether the target is:

- an app using built-in AVFAudio nodes;
- an app hosting a custom or third-party Audio Unit;
- an Audio Unit v3 app extension plus a containing app;
- a spatial/audio-processing target with a specific component.

Inspect SDK availability and extension lifecycle. Do not assume the containing app’s process, UI, or memory lifetime is the extension’s lifetime.

## Step 3: Discover or instantiate the component

Create an AudioComponentDescription with the documented type, subtype, manufacturer, and flags. Enumerate or instantiate the component through the chosen layer. Validate:

- component exists;
- host supports the component;
- busses and channel counts are compatible;
- the selected format is valid;
- required presets/parameters exist;
- an error can recover without corrupting the current graph.

Keep component discovery out of a render callback and out of a view’s body.

## Step 4: Configure busses and resources

Use the host/engine control boundary to configure format, channel layout, connections, and parameters. Inspect inputBusses/outputBusses and the unit’s parameter tree. Allocate render resources only after configuration is settled.

The render path should consume the configured state. If a user changes a format or graph connection, stop or quiesce the relevant path according to the host lifecycle, change the configuration, and allocate resources again.

## Step 5: Build the render boundary

For a custom unit:

1. publish an internal render block or documented render path;
2. validate frame count and buffer layout;
3. process bounded frames;
4. handle silence/discontinuity/timestamps;
5. return an OSStatus or documented result;
6. avoid allocation, locks, UI, I/O, and model work.

For an engine source or node, use the documented AVFAudio callback boundary and keep control state separate from render state.

## Step 6: Use Audio Workgroups only for owned auxiliary threads

If only the framework-created real-time thread renders, the system handles its audio-device workgroup association. If the app or Audio Unit creates auxiliary real-time threads, use the Audio Workgroup route after measuring the need and following the documented synchronous/asynchronous workgroup guidance.

Do not put main-actor tasks, model inference, file writes, or UI work in a workgroup. A workgroup coordinates a deadline; it does not relax real-time rules.

## Step 7: Configure AVAudioSession and host output

Treat AVAudioSession as its own lifecycle:

- select category/mode/options;
- activate at the right time;
- handle interruption and route change;
- observe sample-rate/channel changes;
- start/stop the engine or output unit;
- separate unit/engine state from audible output evidence.

If the feature is MIDI-controlled, keep CoreMIDI input state separate from the audio-unit render state.

## Step 8: Add SwiftUI and Liquid Glass

Project only control-side state into SwiftUI:

- component/preset picker;
- parameter editor;
- bus/format inspector;
- active/rendering/interrupt/error status;
- audio-route recovery;
- AI proposal review.

Use system semantic controls and add Liquid Glass around contextual panels. Keep a simple fallback view for accessibility and performance settings.

## Step 9: Add bounded AI

Create a typed proposal:

component and parameter snapshot -> proposal -> range/format/lifecycle validation -> user review -> control-side apply

The model can suggest a preset, parameter values, an explanation, or a safe grouping. It cannot call AudioUnitRender, mutate render resources, change engine connections, or activate the audio session.

## Step 10: Proof gates

Verify:

- named target imports and compiles;
- component/extension discovery on a signed build;
- bus and format configuration;
- resource allocation/reset/deallocation;
- render callback under burst/maximum frame sizes;
- no render-thread allocation/lock/I/O/model work;
- engine and AVAudioSession interruption/route/sample-rate behavior;
- physical audio output and silence/overload evidence;
- workgroup use and Instruments evidence if custom auxiliary threads exist;
- accessibility, Dynamic Type, VoiceOver, reduced motion, and keyboard/controller alternatives;
- AI proposal rejection, approval, undo, and component disappearance;
- TestFlight/release artifact behavior.

## Sources

- [Audio Toolbox](https://developer.apple.com/documentation/audiotoolbox)
- [AudioComponentDescription](https://developer.apple.com/documentation/audiotoolbox/audiocomponentdescription)
- [AUAudioUnit](https://developer.apple.com/documentation/audiotoolbox/auaudiounit)
- [AudioUnit](https://developer.apple.com/documentation/audiotoolbox/audiounit)
- [Understanding Audio Workgroups](https://developer.apple.com/documentation/audiotoolbox/understanding-audio-workgroups)
- [Workgroup Management](https://developer.apple.com/documentation/audiotoolbox/workgroup-management)
- [Audio Engine](https://developer.apple.com/documentation/avfaudio/audio-engine)
- [AVAudioEngine](https://developer.apple.com/documentation/avfaudio/avaudioengine)
- [AVAudioUnit](https://developer.apple.com/documentation/avfaudio/avaudiounit)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)

***
