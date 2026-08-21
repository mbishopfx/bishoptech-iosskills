# Core Bluetooth transport and device-command route

Use this route when an app needs a bounded Bluetooth transport to a known BLE accessory or another app instance. Keep setup, transport, protocol trust, command authorization, domain result, and background proof as separate stages.

This is a route sketch, not a compiled integration. It does not prove Bluetooth permission, accessory identity, firmware compatibility, physical reachability, GATT correctness, background wake, iOS 26 Live Activity behavior, or release eligibility.

## Choose the narrowest route

| Need | Use | Do not substitute |
| --- | --- | --- |
| Custom BLE service and characteristic exchange | Core Bluetooth central/peripheral | A local mock or a HomeKit model |
| Onboard a supported accessory | AccessorySetupKit, then Core Bluetooth if needed | Broad scanning before user intent |
| Control an Apple Home accessory | HomeKit | Raw GATT commands |
| Measure distance or direction | Nearby Interaction | RSSI as a distance claim |
| Discover a local-network service | Network/Bonjour | Bluetooth advertisement as authentication |
| Phone/Watch companion transfer | WatchConnectivity when that is the product relationship | A custom BLE transport without a reason |

## Capability and target register

Record before implementation:

| Register | Decision |
| --- | --- |
| Platforms | iPhone/iPad, accessory/firmware families, and whether dual-role is needed |
| SDK/deployment | Final Xcode/SDK, deployment targets, availability checks |
| Role | Central, peripheral, or both |
| Service schema | Primary service UUID, characteristic UUIDs, properties, permissions |
| Privacy | NSBluetoothAlwaysUsageDescription wording and when it appears |
| Background | bluetooth-central or bluetooth-peripheral only if the user outcome requires it |
| Restoration | Stable manager identifier and restoration reducer |
| Setup | AccessorySetupKit migration/picker or app-owned selection |
| Trust | Protocol handshake, device binding, key lifecycle, and user confirmation |
| AI | Typed proposal schema, allowlist, model availability, fallback |
| UI | Native state hierarchy, Liquid Glass group, accessibility, localization |
| Proof | Physical pair, background, restoration, system, and signed artifact records |

Core Bluetooth usage is guarded by the Bluetooth privacy usage description. Background modes and AccessorySetupKit are separate configuration choices; do not add them merely because the framework can expose them.

## Ownership graph

The route is:

SwiftUI feature -> command/reducer -> Bluetooth actor or serialized adapter -> Core Bluetooth delegates -> protocol codec -> device result -> domain record

The adapter owns:

- manager state;
- discovered peripheral references;
- connection and service discovery;
- characteristic subscriptions;
- read/write queues and backpressure;
- restoration inputs;
- protocol decoding;
- transport error mapping.

The domain layer owns:

- selected device record;
- user authorization;
- command intent;
- confirmation;
- idempotency;
- accepted/rejected device result;
- freshness and deletion.

The AI layer may propose a typed command. It never owns the manager, peripheral, characteristic, retry loop, or side effect.

## Central route

1. Create a central manager with the intended queue and optional restoration identifier.
2. Wait for poweredOn.
3. Scan only for the required service UUIDs.
4. Bound candidate retention and stop scanning after selection.
5. Connect to the selected peripheral.
6. Assign the delegate and discover only the required services.
7. Discover and validate characteristics.
8. Subscribe to event characteristics where needed.
9. Negotiate protocol version and capabilities.
10. Enable typed commands only after the trust state is ready.
11. Frame, write, acknowledge, and reconcile each operation.
12. Stop notifications, cancel/reconnect, and clear stale state on teardown.

Do not retain an arbitrary scan result as a durable device identity. Persist an app-owned record only after the person selects the device and the product’s trust policy passes.

## Peripheral route

Use the peripheral role only when the app must expose a service:

1. Create the peripheral manager with a stable restoration identifier if restoration is needed.
2. Wait for poweredOn.
3. Build the minimum mutable service/characteristic graph.
4. Add services and handle errors.
5. Advertise only the identifiers required by the feature.
6. Handle central subscription and read/write requests.
7. Send bounded notifications with explicit backpressure.
8. Stop advertising and release resources when the user leaves the feature.
9. Reconcile restored services and subscriptions after relaunch.

An iPhone advertising a service is not automatically safe for every nearby central. The app still needs protocol authorization and operation validation.

## Protocol contract

Define a value-type protocol register independent of Core Bluetooth objects:

~~~swift
struct BLECommand: Sendable, Equatable {
    let requestID: UUID
    let deviceID: UUID
    let operation: Operation
    let protocolVersion: Int

    enum Operation: Sendable, Equatable {
        case setLevel(Int)
        case requestStatus
        case stop
    }
}

struct BLEResult: Sendable, Equatable {
    let requestID: UUID
    let deviceID: UUID
    let outcome: Outcome
    let receivedAt: Date

    enum Outcome: Sendable, Equatable {
        case accepted
        case rejected(code: String)
        case status(level: Int, isRunning: Bool)
    }
}
~~~

Encode/decode in a testable codec. Keep UUIDs, byte order, maximum payload, checksum/integrity, sequence numbers, and error values in one register. Do not scatter magic bytes through view code.

## Command review route

Use this boundary for a command with a physical effect:

intent -> selected device -> compatibility -> typed proposal -> review -> validated write -> device result -> durable record

If the app cannot observe a domain result, record completion as unknown rather than successful. If a write-with-response callback returns without a device-level result, it proves transport acknowledgement only.

## AI route

The AI adapter should accept a redacted command vocabulary:

~~~swift
struct DeviceCommandProposal: Sendable, Equatable {
    let deviceID: UUID
    let operation: BLECommand.Operation
    let explanation: String
    let requiresConfirmation: Bool
}
~~~

Validation must deterministically check:

- selected device and current connection;
- protocol version/capability;
- operation allowlist;
- numeric range and payload size;
- account/role authorization;
- stale command or duplicate request ID;
- confirmation requirement;
- cancellation and timeout;
- device result mapping.

When the model is unavailable or uncertain, show the typed controls and ask the person to choose an explicit operation.

## Background and restoration route

Use a Live Activity only for a user-started, bounded Bluetooth task that has meaningful progress. If the iOS 26 Core Bluetooth background route is used, record the exact SDK/device/ActivityKit state and do not promise indefinite execution.

For restoration:

- recreate managers with the same stable identifiers;
- accept restored objects as partial inputs;
- reattach delegates;
- reconcile with app-owned device and command records;
- reject stale or unauthorized commands;
- resume only idempotent work;
- finish or cancel the Live Activity when the task ends.

## Failure and fallback matrix

| Failure | User-facing fallback |
| --- | --- |
| Bluetooth denied/off | Explain and offer Settings or manual mode |
| Unsupported role/device | Show compatibility details and stop |
| No candidate | Keep the screen useful; offer retry and setup help |
| Duplicate names | Show product/provenance details and require selection |
| Service mismatch | Mark incompatible; do not issue commands |
| Connection timeout | Offer retry/cancel with preserved intent |
| Notification queue full | Pause and resume through documented readiness callback |
| Disconnection | Show stale state and reconnect policy |
| Restoration mismatch | Reverify or require new selection |
| AI unavailable | Use deterministic controls |
| Device rejects command | Show typed device error; do not retry blindly |
| Physical result unknown | Mark unknown and provide refresh/reconciliation |

## Evidence packet

Capture a route-specific packet:

- target membership, SDK/deployment, usage description, and background configuration;
- central-only, peripheral-only, and dual-role state behavior as applicable;
- real device discovery, selection, connection, service/characteristic graph, and protocol version;
- read, write-with-response, write-without-response/backpressure, notification, and framing tests;
- radio off/denied, unsupported, duplicate device, disconnect, stale, and mismatch cases;
- app termination, manager restoration, and user-started iOS 26 Live Activity background behavior if claimed;
- AI proposal/input audit, confirmation, redaction, fallback, and no-arbitrary-write test;
- accessibility, Dynamic Type, reduced effects, localization, and device-name edge cases;
- final signed artifact and release copy review.

## Sources

- [Core Bluetooth](https://developer.apple.com/documentation/corebluetooth)
- [CBCentralManager](https://developer.apple.com/documentation/corebluetooth/cbcentralmanager)
- [CBPeripheral](https://developer.apple.com/documentation/corebluetooth/cbperipheral)
- [CBPeripheralManager](https://developer.apple.com/documentation/corebluetooth/cbperipheralmanager)
- [CBPeripheralDelegate](https://developer.apple.com/documentation/corebluetooth/cbperipheraldelegate)
- [CBPeripheralManagerDelegate](https://developer.apple.com/documentation/corebluetooth/cbperipheralmanagerdelegate)
- [CBManager](https://developer.apple.com/documentation/corebluetooth/cbmanager)
- [CBManagerAuthorization](https://developer.apple.com/documentation/corebluetooth/cbmanagerauthorization)
- [Transferring data between Bluetooth Low Energy devices](https://developer.apple.com/documentation/corebluetooth/transferring-data-between-bluetooth-low-energy-devices)
- [Central manager state restoration options](https://developer.apple.com/documentation/corebluetooth/central-manager-state-restoration-options)
- [Peripheral manager state restoration options](https://developer.apple.com/documentation/corebluetooth/peripheral-manager-state-restoration-options)
- [NSBluetoothAlwaysUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsbluetoothalwaysusagedescription)
- [UIBackgroundModes](https://developer.apple.com/documentation/bundleresources/information-property-list/uibackgroundmodes)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [AccessorySetupKit](https://developer.apple.com/documentation/accessorysetupkit)
- [HomeKit](https://developer.apple.com/documentation/homekit)
- [Nearby Interaction](https://developer.apple.com/documentation/nearbyinteraction)
- [Network](https://developer.apple.com/documentation/network)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
