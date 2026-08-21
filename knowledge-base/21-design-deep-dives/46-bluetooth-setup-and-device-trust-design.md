# Bluetooth setup and device-trust design

Core Bluetooth design should make the radio state, user choice, transport state, protocol trust, and physical result legible as different things. Apple-like polish comes from calm hierarchy and honest status, not from making every device card translucent.

This page is for BLE accessories, device-to-device utilities, sensor readers, and local command surfaces. It does not replace system-owned AccessorySetupKit, HomeKit, or Nearby Interaction UI.

## Start from the user outcome

| User outcome | Primary route | Design responsibility |
| --- | --- | --- |
| Add a supported accessory | AccessorySetupKit, then Core Bluetooth if the accessory uses BLE | System discovery/consent first; app-owned device details after selection |
| Connect to a known custom BLE device | Core Bluetooth central | Explain why scanning starts and how the selected device is recognized |
| Let two app instances exchange bounded data | Core Bluetooth dual role or a different peer route | Show both device roles, transfer progress, and retry/duplicate behavior |
| Control an Apple Home accessory | HomeKit | Use Home authorization and Home semantics, not a generic GATT screen |
| Measure relative direction/distance | Nearby Interaction | Use NI session/protocol and system/device support, not RSSI as a range UI |
| Discover a local-network service | Network/Bonjour | Use local-network permission and application-level trust |

The route selector is part of the UX. If the product cannot explain why it needs raw Bluetooth transport, it may be choosing the wrong framework.

## A calm setup flow

Design a staged flow:

1. Explain the user outcome in plain language.
2. Request Bluetooth access at the feature boundary with a specific reason.
3. Scan only for the service identifiers needed by the current feature.
4. Show a bounded candidate list with a clear “what is this?” explanation.
5. Ask the person to choose the device; do not silently bind to the first advertisement.
6. Connect and show discovery progress.
7. Verify the expected service/characteristic schema and protocol version.
8. Show the device as ready only after the app’s trust rules pass.
9. Require confirmation before a physical side effect.
10. Provide Remove, Forget, Retry, and Reconnect controls.

Do not make a generic spinner carry the whole meaning of scanning, connection, and trust. Each state should tell the person what happened and what they can do next.

## State-driven device surface

| State | Visual hierarchy | Primary action | Avoid |
| --- | --- | --- | --- |
| Bluetooth unavailable | Explanation and system setting guidance | Open Settings or use fallback | “No devices found” |
| Permission needed | Why the feature needs Bluetooth | Continue/request access | Prompt before context |
| Scanning | Progress plus stop control | Stop scanning | Endless animation with no scope |
| Candidate found | Device name, product family, provenance | Select | Treating name as identity |
| Connecting | Selected device and cancellation | Cancel | Duplicate connect buttons |
| Discovering services | “Checking compatibility” | Wait/cancel | Showing an optimistic ready state |
| Connected but untrusted | Transport status plus trust explanation | Verify/remove | Enabling commands |
| Ready | Verified device, freshness, available commands | Open feature | Raw UUIDs as primary copy |
| Stale | Last verified event and freshness | Refresh/reconnect | Presenting cached state as live |
| Disconnected | Reason when known and preserved intent | Reconnect | Silent retry loops |
| Restoring | “Reconnecting to your selected device” | Cancel | Claiming restored domain truth |
| Error | Specific next step and diagnostic ID | Retry/remove | Dumping callback text |

If the device controls something consequential, add a second confirmation surface that repeats the intended device and operation. A connected radio is not permission to mutate the physical world.

## Device identity and trust

Separate these labels:

- Advertised name: a user-facing hint supplied by the peer.
- System peripheral identity: a connection object managed by Core Bluetooth.
- App registry identity: the app’s stable record for a selected device.
- Protocol identity: the version/capabilities that the peer proves.
- Physical identity: the product-specific evidence that the person is controlling the intended object.
- Command result: the device’s domain-level acknowledgement or measured outcome.

Use a compact “verified” state only after the app’s protocol and user-selection rules pass. If the product has a secure pairing or cryptographic handshake, show its result in plain language and keep keys out of logs and AI context.

## Bluetooth detail layout

A strong native detail screen can use:

1. a title and status indicator;
2. a short device family and selected-device explanation;
3. freshness/last-seen/last-verified information;
4. the smallest useful live observation;
5. primary typed commands;
6. a reviewable command confirmation;
7. connection diagnostics and Forget in a secondary section.

Prefer a semantic List, Form, Section, Label, Toggle, Button, and ProgressView before custom canvas or raw telemetry. Reserve charts for measurements that have a meaningful time axis and an explicit unit.

## Liquid Glass application

Apply Liquid Glass to a functional group such as:

- a selected-device summary;
- a compact connection status cluster;
- a command review action group;
- a transient reconnect control.

Keep high-information content on an opaque or high-contrast surface when needed. A glass group should not merge:

- unverified advertisements with verified devices;
- stale values with live values;
- an AI proposal with an executed command;
- transport callbacks with physical-world results.

Use one material hierarchy, avoid nested glass panels, and provide reduced-transparency and accessibility fallbacks. The app should remain understandable if material effects are disabled or unavailable.

## AI interaction model

The safest AI Bluetooth surface is proposal-first:

person intent -> typed proposal -> deterministic validation -> confirmation -> BLE write -> device result -> app-owned record

Example:

- Person: “Turn the desk fan down.”
- Model proposal: SetFanSpeed(deviceID: selectedDeskFan, level: 2).
- Validator: verifies selected device, current protocol, range, authorization, and connection.
- Review: shows “Desk Fan · speed 2” with Confirm and Cancel.
- Transport: writes the command with a request ID.
- Device: returns accepted/rejected/current state.
- App: records the result with timestamp and freshness.

The model must not choose arbitrary service UUIDs, construct unbounded binary payloads, or infer that a write succeeded. If the model is unavailable, keep typed controls and deterministic commands.

## Background and Live Activity design

Only show a Live Activity when the person has started a bounded task that benefits from glanceable progress. The Live Activity should state:

- the selected device or safe product name;
- the active task;
- progress or last verified result;
- a stop/cancel action where supported;
- a stale/expired state if updates stop.

Do not use a Live Activity as a permanent “Bluetooth is connected” badge. The Core Bluetooth iOS 26 route is about certain user-started background activities; it does not eliminate radio state, termination, battery, or device-result uncertainty.

## Accessibility and adaptation

Test the complete workflow, not only the device list:

- VoiceOver reads purpose, selected device, connection state, freshness, and action result in order.
- Dynamic Type does not hide Forget, Cancel, Confirm, or error recovery.
- Voice Control can say the device and command labels without relying on icons or color.
- Switch Control reaches scan stop, device selection, confirmation, reconnect, and removal.
- Reduce Motion keeps state transitions understandable without animated scanning.
- Reduce Transparency and increased contrast preserve status differences.
- RTL, localization, long device names, duplicate names, and unavailable measurements remain legible.
- Keyboard, pointer, and external input have a visible focus path where supported.

Use accessibility values for state and freshness, not only a green/red icon.

## Privacy and retention

Document what the app retains:

| Data | Default policy |
| --- | --- |
| Advertisements/RSSI | Ephemeral unless needed for the current session |
| Device identifier | App-owned identifier with deletion/forget path |
| Raw characteristic data | Decode only required fields; avoid indefinite retention |
| Command payload | Retain typed audit fields, not raw secrets |
| Device name/room label | User-visible and deletion-aware |
| AI prompt | Redacted, minimum fields, no raw radio dump |
| Diagnostics | Redacted event code and target/device metadata |

The app’s privacy policy, system usage description, and UI copy should agree. “Local” or “on-device” does not by itself define retention or security.

## Evidence-aware design review

Before calling the experience native and trustworthy, capture:

- a target/permission/configuration record;
- a physical scan/connect/discover flow;
- a trust/protocol mismatch flow;
- read/write/notification behavior;
- disconnect/reconnect and stale data;
- background/termination/restoration;
- iOS 26 Live Activity route if claimed;
- AI proposal rejection and deterministic fallback;
- accessibility task results;
- deletion/forget and log redaction.

## Sources

- [Core Bluetooth](https://developer.apple.com/documentation/corebluetooth)
- [CBCentralManager](https://developer.apple.com/documentation/corebluetooth/cbcentralmanager)
- [CBPeripheral](https://developer.apple.com/documentation/corebluetooth/cbperipheral)
- [CBPeripheralManager](https://developer.apple.com/documentation/corebluetooth/cbperipheralmanager)
- [CBManagerAuthorization](https://developer.apple.com/documentation/corebluetooth/cbmanagerauthorization)
- [Transferring data between Bluetooth Low Energy devices](https://developer.apple.com/documentation/corebluetooth/transferring-data-between-bluetooth-low-energy-devices)
- [Central manager state restoration options](https://developer.apple.com/documentation/corebluetooth/central-manager-state-restoration-options)
- [NSBluetoothAlwaysUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsbluetoothalwaysusagedescription)
- [UIBackgroundModes](https://developer.apple.com/documentation/bundleresources/information-property-list/uibackgroundmodes)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
