# GameController physical-input capability route

Use this route when an iOS 26 app needs real controller input, controller-aware SwiftUI navigation, keyboard or mouse parity, motion sensing, system remapping, or an accessible alternate-input mode.

The route is deliberately capability-first. It separates target configuration, device discovery, input normalization, semantic actions, UI focus, accessibility, optional on-device AI, and physical-device proof.

Read the [GameController deep dive](../42-framework-deep-dives/38-gamecontroller-physical-input-and-motion.md), [controller-input design guide](../21-design-deep-dives/58-controller-input-and-accessible-game-design.md), [proof matrix](../60-verification/55-gamecontroller-input-proof-matrix.md), and [code recipes](../70-code-recipes/73-gamecontroller-input-recipes.md) before adding a target.

## Route card

| Boundary | Decision |
| --- | --- |
| User outcome | What becomes easier with a controller? |
| Target | iOS, iPadOS, tvOS, macOS, visionOS, or multiple targets |
| Default interaction | Touch, remote, keyboard/pointer, or hand/eye input that must remain available |
| Supported profile | Extended Gamepad, Gamepad, Micro Gamepad, Directional Gamepad, keyboard, mouse, motion, or another documented profile |
| Action model | App-owned semantic actions and domain reducer |
| UI surface | Gameplay, navigation, settings, remap sheet, tutorial, or accessibility surface |
| AI role | None, explanation, bounded classification, or remap proposal |
| Evidence | Source, compile, connection, profile, input, UI, accessibility, performance, signed device, and release evidence |

## 1. Define semantic actions before reading hardware

Write the action catalog first:

~~~text
move(vector)
look(vector)
primary
secondary
pause
cancel
nextSection
previousSection
openControls
~~~

Keep the catalog independent of:

- controller vendor;
- button letters and colors;
- physical element names;
- screen coordinates;
- SwiftUI view identity;
- model-generated text.

Each action should define:

| Field | Example |
| --- | --- |
| Identifier | primary |
| Input kind | press |
| Repeat policy | edge-triggered |
| Allowed contexts | gameplay, menu |
| Fallback | touch button or keyboard command |
| Accessibility label | Confirm |
| Safety | reversible or requires review |

For an AI-enabled route, the action catalog is the model’s bounded vocabulary. Do not ask a model to infer arbitrary Swift closures or framework calls from raw input.

## 2. Configure the target

Add the Game Controllers capability in Xcode’s Signing & Capabilities editor. Confirm the generated target configuration contains the supported interaction flag and the profile declarations needed by the app.

For every intended target, record:

- bundle identifier and target name;
- platform and deployment target;
- SDK/Xcode used for the build;
- Game Controller capability state;
- GCSupportsControllerUserInteraction value;
- GCSupportedGameControllers profile order;
- GCSupportsMultipleMicroGamepads when relevant;
- framework import and target membership;
- fallback interaction route;
- physical device and controller used for proof.

The capability tells the system what the app supports; it does not pair a device, grant a player identity, or guarantee a profile at runtime.

## 3. Choose the input layer

Use the current live-input route for a game loop or high-rate input:

~~~text
GCController
  -> input
  -> GCControllerLiveInput
  -> buttons / dpads / axes / elements
  -> current state, snapshots, callbacks, or queued states
~~~

Use profile-oriented properties when the feature explicitly targets an extended or micro gamepad:

~~~text
GCController
  -> extendedGamepad or microGamepad
  -> profile-specific button, d-pad, stick, motion, or callback APIs
~~~

Do not mix two handlers for the same action unless the duplication is intentional and tested. Pick one owner for sampling, one queue, and one normalization path.

## 4. Discover and observe controllers

At app launch:

1. query the connected controller collection;
2. derive a transient capability summary;
3. choose a current or player-owned controller;
4. install connection, disconnection, current-controller, and customization-change observations;
5. expose the summary to SwiftUI.

During a connection:

- inspect the available profile;
- avoid force-unwrapping extendedGamepad or motion;
- assign playerIndex only when the game has an ownership policy;
- read physical-element localized names and SF Symbols names where the route displays a legend;
- record isAttachedToDevice as a diagnostic property only.

During disconnection:

- unregister callbacks;
- clear the active adapter;
- preserve domain state;
- switch to touch or pause safely;
- communicate the fallback without blaming the person.

If the app offers wireless discovery, make it a short-lived user-initiated flow. Stop discovery when pairing ends or the screen disappears.

## 5. Normalize input into an app-owned sample

The normalization layer handles:

- analog dead zones;
- coordinate orientation;
- trigger thresholds;
- button edge detection;
- repeat timing;
- profile differences;
- system remapping;
- motion capability checks;
- timestamp and latency diagnostics.

Example boundary:

~~~text
physical profile
-> normalized input sample
-> semantic action event
-> game or app reducer
~~~

An input sample should be small and Sendable where the selected Swift version allows it. It should not hold a controller object, a SwiftUI view, or an unbounded raw-history array.

For frame-based play, capture a coherent snapshot before reading multiple inputs. For high-rate devices or controls where transitions matter, set a bounded input-state queue and drain it every loop. Treat queue overflow as an observable loss of evidence.

## 6. Build SwiftUI around state, not callbacks

Use a coordinator or model to project:

~~~text
controllerStatus
currentProfile
playerAssignments
activeActionMap
availableGlyphs
focusDestination
fallbackMode
remapProposal
~~~

SwiftUI views render this projection. They should not own the raw input callback or read a controller from a static global in every body evaluation.

For controller navigation:

- make important destinations focusable;
- use FocusState for a small, explicit focus model;
- use focus sections where the platform needs grouping;
- keep the selected item visible when focus changes;
- preserve focus across Liquid Glass transitions and size changes;
- let touch activate the same semantic action;
- expose an accessible label independent of the controller glyph.

Commands and keyboard shortcuts should map to semantic actions, not call a game object directly from a view modifier.

## 7. Design the controller legend

Render the legend from the active profile:

| Data | Display role |
| --- | --- |
| Semantic action | “Confirm”, “Move”, “Pause” |
| Localized element name | Hardware-aware text |
| SF Symbols name | Current controller glyph |
| Input source | System mapping or app mapping |
| Availability | Available, unavailable, or fallback |

When the current controller changes, update the legend. When a system mapping changes, update the action map and glyphs. When no controller exists, remove or replace the legend rather than showing stale controller instructions.

Use Liquid Glass for a compact status or remap surface, not as a substitute for a visible action label or a stable focus indicator. Avoid covering important game content and test contrast over dynamic scenes.

## 8. Add keyboard, mouse, and motion routes deliberately

Keyboard:

- obtain the currently connected keyboard;
- use GCKeyboardInput for key state and key-change handling;
- map key codes to semantic actions;
- let people customize game bindings where appropriate;
- respect standard system shortcuts.

Mouse:

- observe the connected mouse and current mouse;
- use GCMouseInput for button, movement, and scroll input;
- keep pointer hover separate from controller focus;
- map equivalent actions to the same domain layer.

Motion:

- check whether a motion profile exists;
- check attitude, rotation rate, gravity, and user-acceleration capabilities;
- calibrate or filter deterministically;
- provide a non-motion alternative;
- test interruption, orientation, drift, and reduced-motion settings.

Do not treat controller motion, mouse movement, or keyboard presence as proof that the person wants telemetry collected.

## 9. Optional on-device AI route

Only add AI after deterministic input and action behavior works.

Good bounded roles:

- generate plain-language help from the validated action map;
- classify a small fixed set of input patterns;
- suggest a remap based on an explicit preference form;
- explain why an action is unavailable on the current profile;
- generate tutorial cards from an app-owned catalog.

Keep the authority boundary:

~~~text
validated device/profile
-> action catalog
-> constrained model input
-> typed proposal
-> user review
-> deterministic validation
-> explicit apply
~~~

Record model version, profile summary, mapping revision, and proposal state. Do not send arbitrary raw controller traces off device by default. Do not let a model invoke arbitrary gameplay or system actions.

## 10. Fallback and accessibility

At minimum, design:

- no-controller startup;
- unsupported profile;
- current controller changes;
- disconnect while focused or playing;
- system remap changes;
- keyboard-only route where the target supports it;
- touch-only route on iPhone and iPad;
- reduced motion and reduced effects;
- VoiceOver labels and focus order;
- Dynamic Type and increased contrast;
- low battery or haptic-unavailable state when haptics are part of the feature.

The controller is an optional interaction device in the HIG’s iOS and iPadOS guidance. A fallback is not a lower-quality imitation; it is part of the product contract.

## 11. Verify the route

Use the [GameController proof matrix](../60-verification/55-gamecontroller-input-proof-matrix.md). At a minimum, collect:

1. current SDK/API source evidence;
2. target compile evidence;
3. target capability and plist evidence;
4. physical controller connection evidence;
5. profile and element evidence;
6. action mapping and current glyph evidence;
7. disconnect, remap, and fallback evidence;
8. focus and accessibility task evidence;
9. motion/keyboard/mouse evidence for claimed routes;
10. latency, queue, memory, and thermal evidence for high-rate play;
11. signed device and TestFlight/release evidence when shipping.

An input callback, simulator event, or SwiftUI preview proves only a narrow part of this chain.

## Route stop conditions

Pause and reassess if:

- the target has no default interaction fallback;
- a controller is being used as a hidden identity or telemetry source;
- the app has no semantic action layer;
- the feature depends on a profile the target does not declare;
- a model is being asked to issue raw input commands;
- a Liquid Glass surface hides critical content or focus;
- the evidence plan cannot include the real controller or intended device;
- the route claims iOS 26 support without checking the selected SDK’s symbol availability.

## Sources

- [Game Controller](https://developer.apple.com/documentation/gamecontroller)
- [GCController](https://developer.apple.com/documentation/gamecontroller/gccontroller)
- [Discovering game controllers](https://developer.apple.com/documentation/gamecontroller/discovering-game-controllers)
- [Handling input events](https://developer.apple.com/documentation/gamecontroller/handling-input-events)
- [GCControllerLiveInput](https://developer.apple.com/documentation/gamecontroller/gccontrollerliveinput)
- [GCDevicePhysicalInput](https://developer.apple.com/documentation/gamecontroller/gcdevicephysicalinput)
- [GCDevicePhysicalInputState](https://developer.apple.com/documentation/gamecontroller/gcdevicephysicalinputstate)
- [GCPhysicalInputProfile](https://developer.apple.com/documentation/gamecontroller/gcphysicalinputprofile)
- [GCPhysicalInputElement](https://developer.apple.com/documentation/gamecontroller/gcphysicalinputelement)
- [GCExtendedGamepad](https://developer.apple.com/documentation/gamecontroller/gcextendedgamepad)
- [GCMicroGamepad](https://developer.apple.com/documentation/gamecontroller/gcmicrogamepad)
- [GCMotion](https://developer.apple.com/documentation/gamecontroller/gcmotion)
- [GCKeyboard](https://developer.apple.com/documentation/gamecontroller/gckeyboard)
- [GCMouse](https://developer.apple.com/documentation/gamecontroller/gcmouse)
- [Configuring game controllers](https://developer.apple.com/documentation/xcode/configuring-game-controllers)
- [Human Interface Guidelines: Game controls](https://developer.apple.com/design/human-interface-guidelines/game-controls)
- [Human Interface Guidelines: Designing for games](https://developer.apple.com/design/human-interface-guidelines/designing-for-games)
- [SwiftUI FocusState](https://developer.apple.com/documentation/swiftui/focusstate)
- [SwiftUI focusable](https://developer.apple.com/documentation/swiftui/view/focusable%28_%3A%29)
- [SwiftUI focused](https://developer.apple.com/documentation/swiftui/view/focused%28_%3A%29)
- [SwiftUI FocusSection](https://developer.apple.com/documentation/swiftui/view/focussection%28%29)
- [SwiftUI KeyboardShortcut](https://developer.apple.com/documentation/swiftui/view/keyboardshortcut%28_%3A%29)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
