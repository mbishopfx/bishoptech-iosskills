# Blueprint: Local Device Command Center

## Product outcome

Give a person a private, understandable control surface for a small set of nearby devices or Home accessories, with explicit trust, confirmation, stale-state handling, and useful system shortcuts/widgets.

## Route composition

`SwiftUI dashboard -> HomeKit/Core Bluetooth/Nearby Interaction/Network discovery -> trusted device model -> confirmed command -> durable local state -> WidgetKit/App Intents/notifications`

Choose one primary accessory/proximity route first. “Nearby” is not an identity or trust model.

| Need | Route | State/permission boundary |
| --- | --- | --- |
| Control devices already configured in Apple Home | HomeKit | Home authorization, accessory/characteristic state, capability, physical side effects, and user confirmation |
| Talk to a custom BLE accessory | Core Bluetooth | Radio authorization, central/peripheral state, GATT schema, reconnect, background limits, and device identity |
| Measure distance/direction to a supported peer/accessory | Nearby Interaction | Permission, discovery/token exchange, session suspension, hardware support, and physical-device evidence |
| Discover a service on the same network | Network/Bonjour | Local-network permission, Bonjour service declaration, service identity, transport security, and denial/reconnect |
| Expose a small repeatable action | App Intents, WidgetKit controls | Stable device/action ID, current authorization, idempotence, extension process, and stale state |

## State machine

`empty -> requesting-access -> discovering -> candidate-found -> pairing/trust-review -> connected -> reading -> ready -> command-confirmation -> executing -> acknowledged|failed|stale -> disconnected`

Separate these values:

- discovery result versus trusted identity;
- transport connection versus app authorization;
- reported device state versus last-known cached state;
- requested command versus acknowledged physical side effect;
- widget/App Intent projection versus canonical local device model.

## Native interface plan

- Use a SwiftUI `NavigationSplitView` or `List`/`Form` appropriate to the device family; group devices by a meaningful user-owned room/category rather than by protocol.
- Use semantic `Toggle`, `Button`, `Picker`, and `ProgressView` controls. The control’s label/value must say whether it reflects reported, pending, stale, or unavailable state.
- Use a restrained Liquid Glass control cluster only around actions/status that benefit from layering; never make a destructive physical command look like a decorative pill.
- Show a confirmation sheet for locks, power, heat, motion, doors, or other consequential actions. State the target, current known state, intended effect, and how to undo/cancel.
- Keep discovery/setup separate from the everyday dashboard. Use accessibility focus and alternate input tests for every device action.

## Build order

1. Build a fake device protocol/state service and dashboard with explicit stale/error states.
2. Add one real protocol route and model authorization/discovery/connection/reconnect.
3. Add a trusted identity record and protocol validation; never trust a display name or address alone.
4. Add command confirmation, idempotent operation IDs, acknowledgement/timeouts, and physical-side-effect recovery.
5. Add a WidgetKit/App Intent projection only for a narrow repeatable action that remains safe outside the main process.
6. Add notifications or Live Activity only when live status shortens a real workflow; keep the canonical state local and reconcile updates.

## Privacy, trust, and permissions

- Request HomeKit, Bluetooth, Nearby Interaction, or local-network permission at the feature boundary with plain-language purpose copy.
- Minimize device identifiers, network addresses, location/room names, and accessory telemetry in logs, analytics, prompts, widgets, notifications, and share paths.
- Treat discovery as untrusted input until the protocol handshake, user selection, cryptographic/authentication layer, and product trust rule accept it.
- Never let Foundation Models invent a device command or bypass confirmation. If AI is used, it may map natural language to a typed, allowlisted command proposal that deterministic code validates.
- Reconcile privacy manifests, usage descriptions, entitlements, local-network declarations, and third-party SDK behavior.

## Fallbacks

| Condition | Fallback |
| --- | --- |
| Permission denied/restricted | Explain settings path and retain a local manual/status-only mode |
| Discovery unavailable | Manual pairing/known-device route or explicit unavailable state |
| Device stale/offline | Show last-known timestamp and disable unsafe actions |
| Command timeout/unknown acknowledgement | Keep pending/unknown state; do not report success |
| Widget/App Intent process lacks access | Return a bounded unavailable result and deep-link to the app for setup |
| AI unavailable/ambiguous | Use a typed manual device/action picker |

## Proof plan

- Fixtures: protocol/state machine, trust rules, command validation, idempotency, stale state, timeouts, and accessibility labels.
- Simulator: dashboard layout, fake discovery, permission branches, error/retry, Dynamic Type, and system-surface intent routing where supported.
- Physical device/accessory: real pairing/discovery, Home authorization, BLE/UWB/local-network behavior, reconnect/interruption, lock/background, physical side effects, battery/thermal, and VoiceOver/Voice Control tasks.
- Release: capabilities/entitlements, App Group/extension configuration, privacy resources, signed widget/intent behavior, APNs/server/account state, TestFlight, and production device compatibility separately.

## Sources

- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [HomeKit](https://developer.apple.com/documentation/homekit)
- [Enabling HomeKit in your app](https://developer.apple.com/documentation/homekit/enabling-homekit-in-your-app)
- [Core Bluetooth](https://developer.apple.com/documentation/corebluetooth)
- [CBCentralManager](https://developer.apple.com/documentation/corebluetooth/cbcentralmanager)
- [Nearby Interaction](https://developer.apple.com/documentation/nearbyinteraction)
- [Network](https://developer.apple.com/documentation/network)
- [NWBrowser](https://developer.apple.com/documentation/network/nwbrowser)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit)
- [ControlWidget](https://developer.apple.com/documentation/swiftui/controlwidget)
- [User Notifications](https://developer.apple.com/documentation/usernotifications)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [Adding capabilities to your app](https://developer.apple.com/documentation/xcode/adding-capabilities-to-your-app)
- [Protected resources](https://developer.apple.com/documentation/bundleresources/protected-resources)
- [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- [Performing accessibility testing for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)
