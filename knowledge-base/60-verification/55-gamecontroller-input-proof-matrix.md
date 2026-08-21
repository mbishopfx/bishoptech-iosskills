# GameController physical-input proof matrix

GameController evidence has several independent layers. A target can compile while its capability is missing, a controller can connect while the app reads the wrong profile, and a button callback can fire while SwiftUI focus, accessibility, fallback, or release behavior is broken.

Use this matrix with the [GameController deep dive](../42-framework-deep-dives/38-gamecontroller-physical-input-and-motion.md), the [capability route](../50-capability-recipes/61-gamecontroller-input-route.md), the [controller-input design guide](../21-design-deep-dives/58-controller-input-and-accessible-game-design.md), and the [code recipes](../70-code-recipes/73-gamecontroller-input-recipes.md).

## Evidence vocabulary

| Level | What it can establish |
| --- | --- |
| Source | The documented API, configuration, or design expectation exists |
| Compile | The selected target resolves symbols for the selected SDK |
| Static target audit | Capability, profile declarations, target membership, and Info.plist values are present |
| Simulator or virtual fixture | Deterministic domain behavior, UI states, and mock input |
| Physical device | Real connection, profile, button/axis/motion behavior, interruption, and hardware-specific results |
| System-surface run | Current-controller, remapping, focus, accessibility, or platform UI behavior |
| Signed device build | The distributed artifact contains the intended configuration |
| TestFlight or release | Distribution, installation, update, device family, and release behavior |

Never collapse these into one “tested” label.

## Claim-to-evidence matrix

| Claim | Minimum evidence | Does not prove it |
| --- | --- | --- |
| GameController is supported by the target | Current API source plus a successful target compile | Importing GameController in another target |
| Target advertises controller support | Signed target audit for capability, interaction flag, and supported profiles | A controller in a preview |
| A controller is connected | Physical device sees it and the app records a bounded profile summary | A saved controller object or virtual snapshot |
| Current-controller UI is correct | Current-controller event plus visible legend update and action test | Reading current once at launch |
| Multiple players are separated | Two physical controllers, playerIndex assignment, action ownership, disconnect/rejoin test | Two controllers in a collection |
| Profile support is correct | Each claimed profile tested with representative hardware or documented fixture | Assuming extendedGamepad is non-nil |
| Button mapping is correct | Physical press, semantic action, visible result, and release/edge behavior | A callback print statement |
| Analog mapping is correct | Range, dead zone, orientation, threshold, repeat, and frame behavior on hardware | One stick position in a debug view |
| Snapshot reads are coherent | Capture path with a multi-element fixture | Sequential live reads |
| Buffered input is not lost | Queue-depth fixture, drain loop, overflow diagnostic, and measured device rate | A successful low-rate callback |
| System remapping is honored | Change mapping in system settings, refresh action/glyph, and retest | An app-owned mapping dictionary |
| App remapping works | Capture, collision detection, reset, recovery action, persistence, and accessibility task | A stored mapping that never drives input |
| Legend is hardware-aware | Localized element name or SF Symbol from active profile | Static A/X/B/Y labels |
| Keyboard route works | Physical key, semantic action, focus, remap, and shortcut review | Simulator text input |
| Mouse route works | Physical button/movement/scroll, pointer/focus behavior, and semantic parity | Trackpad movement in a preview |
| Motion route works | Physical capability check, attitude/acceleration fixture, calibration, and fallback | A non-nil GCMotion object |
| SwiftUI focus works | Controller navigation through all critical destinations with visible focus and touch alternative | A focused preview control |
| Accessibility works | VoiceOver, Dynamic Type, increased contrast, reduced motion, and alternate-input task on device | Accessibility modifier presence |
| Liquid Glass surface works | Current SDK API, contrast, focus, motion, and layout tests in a signed target | A screenshot resembling Liquid Glass |
| AI help is useful | Validated profile/action-map fixture, constrained proposal, review/apply flow, and stale-map handling | A generated paragraph |
| AI stays bounded | Data-flow review, typed proposal validation, no hidden action execution, redacted diagnostics | A prompt that says “be safe” |
| Performance is acceptable | Release-like build and device measurements for input latency, queue, frame, memory, and thermal behavior | Debug FPS on a new device |
| Release supports the route | Signed app, intended device family, controller matrix, fallback, metadata, and TestFlight/release run | Simulator success or Build Succeeded |

## Environment record

| Field | Value |
| --- | --- |
| App target and bundle ID |  |
| Platform and deployment target |  |
| Xcode and SDK |  |
| Version and build |  |
| Controller make/model/firmware |  |
| Connection method |  |
| Profile claimed |  |
| Player-index policy |  |
| Current-controller policy |  |
| System remap state |  |
| Keyboard/mouse/motion hardware |  |
| Input layer | live input / profile / fixture |
| Queue depth and callback queue |  |
| Device model and OS |  |
| Accessibility settings |  |
| Liquid Glass configuration |  |
| AI model/version, if used |  |
| Signed artifact or TestFlight build |  |

Do not put serial numbers, account tokens, private controller names, or unredacted logs into a shared evidence record.

## Configuration checks

| Check | Expected evidence |
| --- | --- |
| Framework target membership | Game Controller resolves in the intended target |
| Capability | Game Controllers appears in Signing & Capabilities |
| Interaction flag | Target declares controller interaction |
| Supported profiles | Profile declarations match the code path |
| Profile order | Preferred profile order is deliberate |
| Micro-gamepad setting | Multiple-micro-gamepad behavior is intentional |
| Symbol availability | Current SDK availability is handled per API |
| Fallback | Touch/default interaction remains reachable |
| Privacy | Input retention and AI data flow are documented and minimized |

An Info.plist value is configuration evidence, not runtime behavior evidence.

## Connection and current-controller tests

| Scenario | Expected result |
| --- | --- |
| Connected before launch | App discovers it and renders the correct profile |
| Connect after launch | App installs one adapter and updates the UI |
| Disconnect during play | Domain state is safe; fallback or pause appears |
| Disconnect during remap capture | Capture cancels without corrupting the map |
| Two controllers connect | Player policy is explicit and visible |
| Current controller changes | Legend, glyphs, focus, and single-player route update |
| Current controller resigns | UI does not retain stale ownership |
| Discovery canceled | No indefinite discovery activity remains |
| Background/foreground | Handler and current-state ownership restore safely |
| Reconnect | Prior app mapping is revalidated against the new profile |

## Profile, polling, and callback tests

For each claimed profile, record the actual profile returned, press every control needed by a critical task, verify the semantic action and glyph, release each control, and test analog values, dead zones, orientation, and unsupported elements.

| Test | Expected result |
| --- | --- |
| Poll current state | Values correspond to the most recent event |
| Capture snapshot | Multiple reads represent one coherent moment |
| Button callback | Press and release produce one intended semantic edge each |
| Element callback | Only the changed element is interpreted |
| Queue depth one | No buffering is assumed |
| Queue depth greater than one | States drain in order at the target rate |
| Queue overflow | Unknown/lost diff becomes a diagnostic and safe behavior |
| Callback queue | High-rate work does not block SwiftUI rendering |
| Cancellation/reinstall | No late or duplicate semantic actions |

Use a deterministic mock adapter for unit tests, but keep a physical run for hardware claims.

## Remapping and legend tests

| Test | Expected result |
| --- | --- |
| Default system mapping | App uses the effective system mapping |
| System remap | App refreshes before the next action |
| App remap | Review, conflict detection, and explicit apply are visible |
| Reserved input | Recovery path remains available |
| Duplicate mapping | Product policy is deterministic |
| Profile changes | Legend uses current device labels and symbols |
| Reset | Mapping returns to documented default/system state |
| Accessibility remap | VoiceOver and keyboard users can complete the flow |

## Motion, keyboard, mouse, and SwiftUI tests

- Check every motion capability flag before sampling; test calibration, orientation, drift, interruption, reduced-motion fallback, and thermal impact when claimed.
- Test physical keyboard keys through GCKeyboardInput, key remapping, shortcut conflicts, focus traversal, and Full Keyboard Access where relevant.
- Test physical mouse buttons, movement, scroll, pointer hover, controller focus, and disconnection when claimed.
- Navigate every critical SwiftUI destination with the controller; keep focus visible, preserve it across layout/glass transitions, and keep touch activation available.
- Run VoiceOver, Dynamic Type, increased contrast, reduced transparency, and reduced motion on the intended device family.

Preview and snapshot tests provide state coverage. They do not prove physical discovery, system remapping, motion, latency, or release behavior.

## AI evaluation matrix

| Claim | Required evidence |
| --- | --- |
| Help describes current controls | Profile summary and mapping revision are in the fixture |
| Remap avoids conflict | Deterministic validator rejects collisions before review |
| Proposal is stale-safe | Controller/mapping change invalidates or refreshes it |
| No hidden action executes | App applies only typed, reviewed, validated actions |
| Raw input stays private | Data-flow and logging audit show bounded retention |
| Offline behavior works | Physical offline run with model local, if claimed |

Do not call a controller assistant an on-device AI feature merely because a model is present. The input data, review boundary, and measured behavior need evidence.

## Release checklist

Before shipping a controller-dependent or controller-enhanced feature:

- build the intended signed target;
- inspect the archive’s capabilities and Info.plist;
- install on every claimed device family;
- test the real controller profiles listed in metadata;
- test controller-free fallback, disconnect, remap, and accessibility;
- measure performance in a release-like build;
- validate App Store metadata and controller requirement wording;
- record what was not tested.

## Sources

- [Game Controller](https://developer.apple.com/documentation/gamecontroller)
- [GCController](https://developer.apple.com/documentation/gamecontroller/gccontroller)
- [Discovering game controllers](https://developer.apple.com/documentation/gamecontroller/discovering-game-controllers)
- [Handling input events](https://developer.apple.com/documentation/gamecontroller/handling-input-events)
- [GCControllerLiveInput](https://developer.apple.com/documentation/gamecontroller/gccontrollerliveinput)
- [GCDevicePhysicalInput](https://developer.apple.com/documentation/gamecontroller/gcdevicephysicalinput)
- [GCDevicePhysicalInputState](https://developer.apple.com/documentation/gamecontroller/gcdevicephysicalinputstate)
- [GCDevicePhysicalInputStateDiff](https://developer.apple.com/documentation/gamecontroller/gcdevicephysicalinputstatediff)
- [GCPhysicalInputElement](https://developer.apple.com/documentation/gamecontroller/gcphysicalinputelement)
- [GCPhysicalInputProfile](https://developer.apple.com/documentation/gamecontroller/gcphysicalinputprofile)
- [GCExtendedGamepad](https://developer.apple.com/documentation/gamecontroller/gcextendedgamepad)
- [GCMicroGamepad](https://developer.apple.com/documentation/gamecontroller/gcmicrogamepad)
- [GCMotion](https://developer.apple.com/documentation/gamecontroller/gcmotion)
- [GCKeyboard](https://developer.apple.com/documentation/gamecontroller/gckeyboard)
- [GCMouse](https://developer.apple.com/documentation/gamecontroller/gcmouse)
- [Configuring game controllers](https://developer.apple.com/documentation/xcode/configuring-game-controllers)
- [Human Interface Guidelines: Game controls](https://developer.apple.com/design/human-interface-guidelines/game-controls)
- [Human Interface Guidelines: Designing for games](https://developer.apple.com/design/human-interface-guidelines/designing-for-games)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
