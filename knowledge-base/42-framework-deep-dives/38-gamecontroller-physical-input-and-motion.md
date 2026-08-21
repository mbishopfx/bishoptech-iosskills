# GameController physical input, semantic profiles, and motion

GameController gives an app a standardized route for physical and virtual controllers, keyboards, mice, Siri Remote input, and controller motion. The framework is useful for a game, a spatial interaction surface, an accessible alternate-input mode, or a SwiftUI utility that becomes richer when a controller is present.

The important boundary is between a physical input event and the app’s meaning for that event. GameController describes devices and their semantic elements. The app still owns action mapping, domain state, validation, accessibility, and the decision about whether an action is safe to apply.

Use this deep dive with the [GameController capability route](../50-capability-recipes/61-gamecontroller-input-route.md), the [controller-input design guide](../21-design-deep-dives/58-controller-input-and-accessible-game-design.md), the [proof matrix](../60-verification/55-gamecontroller-input-proof-matrix.md), and the [code recipes](../70-code-recipes/73-gamecontroller-input-recipes.md).

## What the framework represents

GCController can represent a physical controller, a virtual controller, or a snapshot. A physical controller can connect directly or wirelessly, and can be attached closely to the device. The framework supports multiple controllers and provides a current-controller concept for single-player experiences.

Keep these identities separate:

| Identity | Meaning | Product use |
| --- | --- | --- |
| Connected controller | A controller currently known to the device | Connection state and device inventory |
| Current controller | The most recently used controller | Single-player UI labels and active control hints |
| Player index | An app-assigned player association | Multiplayer ownership and controller LEDs where supported |
| Profile | The controls the device exposes | Capability and input decoding |
| Physical element | A button, axis, d-pad, touchpad, or switch | Low-level observation |
| Semantic action | An app-owned action such as move, confirm, or pause | Domain logic and game behavior |
| Snapshot | A captured input state | Consistent reads, fixtures, and replay-like tests |

Do not persist a controller object as if it were a durable player account. A connection can disappear, a controller can be replaced, and a system-level remap can change the effective element mapping.

## Project and capability configuration

Apple’s current Xcode guidance uses the Game Controllers capability. The capability adds or manages the target configuration for controller interaction and the supported controller profiles. The important configuration concepts are:

- GCSupportsControllerUserInteraction indicates that the target supports game-controller interaction.
- GCSupportedGameControllers declares the profiles the target supports or requires.
- GCSupportsMultipleMicroGamepads is relevant to the Apple TV Remote and Apple TV Remote app route.
- The target must include the Game Controller framework and the correct platform membership.

Prefer the Xcode Signing & Capabilities editor and generated target configuration for the selected SDK. Do not hand-copy a profile string from an old project without inspecting the current generated Info.plist and build settings.

Capability configuration does not mean that a controller is connected. The app still needs an empty, denied, disconnected, unsupported-profile, and fallback state.

## Discovery and connection lifecycle

At launch, query GCController.controllers() to discover controllers already connected. When the product needs an explicit pairing flow, use GCController.startWirelessControllerDiscovery and stop the discovery session when the flow ends. Use the GameController connection and disconnection notifications or the current main-actor message identifiers in the selected SDK to observe changes while the app runs.

The connection state machine should be explicit:

~~~text
app launch
-> query connected controllers
-> listen for connect/disconnect/current/remap events
-> select profile and action map
-> receive input
-> disconnect or resign current
-> fall back without losing domain state
~~~

When a controller connects:

1. Record an app-owned transient identity for diagnostics, not a personal identity.
2. Inspect the supported profile and device characteristics.
3. Assign a player index only when the product has a player-ownership decision.
4. Install exactly one input ownership strategy for the active route.
5. Update UI labels and control hints from the connected device’s labeling information.

When it disconnects, remove handlers and release any active ownership. Do not leave a callback retaining a dead controller or keep a gameplay session waiting forever for the same physical accessory.

The current controller is appropriate for a single-player experience when the app does not need to distinguish simultaneous inputs. A multiplayer experience should use the controller collection and player index deliberately. A current-controller change is also a UI event: update the control legend, glyphs, and input focus to match the controller now in use.

The controller’s isAttachedToDevice property describes whether it closely integrates with the device. It is not a quality score, a trust decision, or proof that the controller supports every advertised profile.

## Two input API layers

The current GameController documentation exposes a newer live-input layer alongside profile-oriented compatibility classes. Select one primary layer for a target and use the other only when the selected SDK and feature require it.

### Live input and physical state

GCController.input returns GCControllerLiveInput. This live input conforms to the physical-device input protocols and represents the current state of gamepads and arcade sticks. The live-input route supports:

- semantic collections such as buttons, dpads, axes, switches, and elements;
- atomic reads of individual current values;
- capture() for a coherent snapshot;
- elementValueDidChangeHandler for event-driven handling;
- inputStateQueueDepth and nextInputState() when a game loop must process buffered states;
- inputStateAvailableHandler to wake or feed a loop when queued states arrive;
- a configurable callback queue;
- unmapped input when an app is deliberately implementing its own remapping UI.

The framework documents thread-safety for the physical-input protocols as safe when accessed from one thread at a time, not concurrently from multiple threads. Choose a queue and ownership model before installing callbacks. Publish UI state on the main actor, but do not move high-rate raw input through a SwiftUI view hierarchy.

Use polling when input is sampled at a stable point in a game loop. Use element callbacks for event-driven controls. Use the input-state queue when missing intermediate changes would affect correctness, such as a high-rate device or a control that must preserve transitions between frames.

### Profile-oriented classes

GCPhysicalInputProfile is the base for profiles that expose physical buttons, thumbsticks, and directional pads. It provides element collections, named lookup, value-change handling, capture, and remapping inspection. Its common collections include:

- elements;
- buttons;
- axes;
- dpads;
- touchpads;
- allElements;
- allButtons;
- allAxes;
- allDpads;
- allTouchpads.

The profile also exposes localized names and SF Symbols names through physical input elements in the newer element protocol. Use these values to build a control legend instead of assuming that every hardware vendor uses the same visible lettering or color.

The older and profile-specific properties remain useful for targeted code:

| Profile | Typical surface |
| --- | --- |
| GCExtendedGamepad | Shoulder buttons, triggers, face buttons, d-pad, two thumbsticks, optional stick buttons, and optional menu/home/options controls |
| GCGamepad | Two shoulders, four face buttons, and a d-pad |
| GCMicroGamepad | Siri Remote-style two face buttons plus a touch-sensitive directional pad |
| GCDirectionalGamepad | Directional-only controls without motion or rotation |
| GCKeyboardInput | Keyboard key state and key-change callbacks |
| GCMouseInput | Mouse buttons, movement, and scroll-related input |
| GCMotion | Attitude, rotation rate, gravity, and user acceleration where supported |

Check for an optional profile before using it. A nil extendedGamepad is a capability result, not an error to paper over with force unwraps.

## Extended and micro gamepad behavior

GCExtendedGamepad standardizes the semantic layout of a broad gamepad. Use its named elements when the game needs a conventional layout, but do not treat a name such as buttonA as a visible promise that the physical controller has a particular letter, color, or glyph. The HIG requires the interface to respect the connected controller’s labeling scheme.

GCMicroGamepad is not just a smaller extended gamepad. Its directional pad is an analog touchpad, it can support orientation, and the profile has rotation and absolute/relative reporting choices. A route that assumes a d-pad click is available on every micro gamepad will fail on a Siri Remote-style device.

For a profile-independent control legend, prefer the physical-input element’s localizedName and sfSymbolsName when present. For a domain action, use an app-owned semantic label such as “confirm” or “move” and render the current physical glyph beside it.

## Polling, callbacks, and coherent state

There are three useful handling patterns:

### Current-state polling

Read the live input or profile once at the point where the app will apply the frame. If multiple values must agree, call capture() first and read the values from the snapshot. A sequence of separate reads can observe different input moments.

### Element callbacks

Use a button or element callback for event-driven behavior such as opening a pause overlay or starting a remap capture. Treat the callback as an input signal, not as permission to mutate arbitrary application state. Forward a typed action to the domain layer and validate it there.

### Buffered input states

Set inputStateQueueDepth to a bounded value when the game loop needs to process every meaningful transition. Drain nextInputState() until the queue is empty. The queue can overflow; current documentation says that the diff information then reports an unknown change. Overflow should become a diagnostic and a safe state, not a silent gameplay assumption.

Use timestamps and latency information for diagnostics. A timestamp is useful evidence for ordering and measurement, but it is not a promise of network latency, frame presentation, or human-perceived responsiveness.

## Remapping and semantic actions

System-level controller customization can change the effective mapping. The modern live-input object exposes an unmapped view for apps that implement their own remapping feature. The profile-oriented API exposes hasRemappedElements, mappedElementAlias, mappedPhysicalInputNames, and a customization-change notification.

The preferred product behavior is:

1. honor system remapping by default;
2. use the semantic input collections instead of hard-coding physical names;
3. re-read mappings after the customization-change event;
4. show the resulting action map using the controller’s current glyphs;
5. offer app-specific remapping only when the product truly needs it;
6. keep physical-to-action mapping separate from the game’s domain state.

If the app offers a custom mapping screen, capture a physical element, show its localized name and SF Symbol, reject reserved/system controls where appropriate, detect collisions, and provide reset/fallback behavior. Do not let a language model write directly into a controller mapping or issue arbitrary actions. An AI suggestion can propose an action map for review; deterministic code must validate and apply it.

## Keyboard and mouse routes

GCKeyboard.coalesced exposes the currently connected keyboard. GCKeyboardInput supplies key state, isAnyKeyPressed, button lookup by GCKeyCode, and key-change callbacks. A physical keyboard is an alternate input device, not an excuse to remove touch navigation on iPhone or focus support on iPad.

GCMouse.mice() and GCMouse.current expose connected mice, while GCMouseInput provides button, movement, and scroll state. Keep pointer affordances separate from gamepad focus. A mouse event can move a pointer while a controller event moves a selection; both should map to the same semantic command where the product wants parity.

For SwiftUI command surfaces, use the existing focus, keyboard shortcut, and command APIs only for app-owned commands. Avoid replacing system shortcuts or making a controller-only route the sole way to reach a critical action.

## Motion input

GCController.motion is optional. GCMotion can provide attitude and rotation-rate data, gravity, total acceleration, and user acceleration. Check hasAttitude, hasRotationRate, and hasGravityAndUserAcceleration before using a signal. Some sensors may require manual activation; inspect sensorsRequireManualActivation and sensorsActive for the target route.

Motion should be:

- sampled at the rate the feature needs;
- filtered and calibrated by deterministic code;
- optional when the user cannot comfortably perform the motion;
- represented with a reduced-motion or non-motion alternative;
- tested for drift, orientation changes, interruption, and device/controller differences.

Do not infer a real-world gesture, intent, or safety decision from raw motion alone. A motion value is an input signal with device-specific behavior.

## SwiftUI boundary

Keep GameController ownership in a dedicated model or coordinator. A practical split is:

~~~text
GameController callbacks or polling
-> normalized InputSample
-> semantic Action
-> domain reducer/game loop
-> MainActor UI projection
~~~

SwiftUI should render connection state, current profile, control hints, focus, and reviewable remapping UI. It should not be the high-frequency input buffer. Use focus APIs for navigation, accessibility APIs for control labels, and a small observable projection for the current route.

For a Liquid Glass interface, use glass as a system surface around status, controls, or a remapping sheet. Keep gameplay legible, preserve contrast and hit targets, and do not cover the area where a person needs to see the game. Glass styling does not replace a semantic button, controller glyph, press state, or non-controller fallback.

## Platform and release boundaries

Apple’s HIG lists physical controllers as an additional interaction method on iOS and iPadOS and as an available input route on the other supported game platforms except watchOS. Every target still needs its platform default interaction method:

- iPhone and iPad: touch remains a real route;
- iPad: keyboard, pointer, and Apple Pencil may be relevant;
- Mac: keyboard, mouse, and trackpad remain expected;
- Apple TV: remote behavior remains expected unless the product explicitly requires a controller;
- visionOS: hand and eye interaction may remain a required alternative.

Do not use a simulator keyboard event, a preview, or a captured virtual controller as physical controller proof. A release claim needs a signed build on each intended device family, a real connected controller profile, the intended mapping and fallback, accessibility settings, interruption/disconnection behavior, and the system/release metadata relevant to the target.

## Bounded on-device AI route

GameController is a good sensor/input boundary for a small on-device intelligence feature, but the model must remain advisory:

- summarize the current action map;
- explain a controller’s available controls;
- suggest a less-conflicting remap;
- generate a short tutorial from an app-owned action catalog;
- classify a bounded input pattern after deterministic normalization.

Keep raw input retention minimal. Store only the samples needed for the feature and evaluation. Do not send controller traces to a model by default, do not let a model issue hidden actions, and do not claim that a generated tutorial matches a device until the app has validated the current profile and mapping.

## Sources

- [Game Controller](https://developer.apple.com/documentation/gamecontroller)
- [GCController](https://developer.apple.com/documentation/gamecontroller/gccontroller)
- [Discovering game controllers](https://developer.apple.com/documentation/gamecontroller/discovering-game-controllers)
- [Handling input events](https://developer.apple.com/documentation/gamecontroller/handling-input-events)
- [Input](https://developer.apple.com/documentation/gamecontroller/input)
- [GCDevicePhysicalInput](https://developer.apple.com/documentation/gamecontroller/gcdevicephysicalinput)
- [GCDevicePhysicalInputState](https://developer.apple.com/documentation/gamecontroller/gcdevicephysicalinputstate)
- [GCDevicePhysicalInputStateDiff](https://developer.apple.com/documentation/gamecontroller/gcdevicephysicalinputstatediff)
- [GCPhysicalInputElement](https://developer.apple.com/documentation/gamecontroller/gcphysicalinputelement)
- [GCPhysicalInputProfile](https://developer.apple.com/documentation/gamecontroller/gcphysicalinputprofile)
- [GCControllerLiveInput](https://developer.apple.com/documentation/gamecontroller/gccontrollerliveinput)
- [GCExtendedGamepad](https://developer.apple.com/documentation/gamecontroller/gcextendedgamepad)
- [GCGamepad](https://developer.apple.com/documentation/gamecontroller/gcgamepad)
- [GCMicroGamepad](https://developer.apple.com/documentation/gamecontroller/gcmicrogamepad)
- [GCKeyboard](https://developer.apple.com/documentation/gamecontroller/gckeyboard)
- [GCKeyboardInput](https://developer.apple.com/documentation/gamecontroller/gckeyboardinput)
- [GCMouse](https://developer.apple.com/documentation/gamecontroller/gcmouse)
- [GCMouseInput](https://developer.apple.com/documentation/gamecontroller/gcmouseinput)
- [GCMotion](https://developer.apple.com/documentation/gamecontroller/gcmotion)
- [GCController playerIndex](https://developer.apple.com/documentation/gamecontroller/gccontroller/playerindex)
- [GCController current](https://developer.apple.com/documentation/gamecontroller/gccontroller/current)
- [GCController live input unmapped view](https://developer.apple.com/documentation/gamecontroller/gccontrollerliveinput/unmapped)
- [Configuring game controllers](https://developer.apple.com/documentation/xcode/configuring-game-controllers)
- [Supporting Game Controllers](https://developer.apple.com/documentation/gamecontroller/supporting-game-controllers)
- [Human Interface Guidelines: Game controls](https://developer.apple.com/design/human-interface-guidelines/game-controls)
- [Human Interface Guidelines: Designing for games](https://developer.apple.com/design/human-interface-guidelines/designing-for-games)
- [SwiftUI focusState](https://developer.apple.com/documentation/swiftui/focusstate)
- [SwiftUI focused](https://developer.apple.com/documentation/swiftui/view/focused%28_%3A%29)
- [SwiftUI focusable](https://developer.apple.com/documentation/swiftui/view/focusable%28_%3A%29)
- [SwiftUI keyboardShortcut](https://developer.apple.com/documentation/swiftui/view/keyboardshortcut%28_%3A%29)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
