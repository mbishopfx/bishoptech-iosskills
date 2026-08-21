# SwiftUI Core Bluetooth and nearby-accessory review route

Use this route when a SwiftUI app discovers, connects to, observes, or controls a Bluetooth Low Energy accessory, or when two Apple devices use Core Bluetooth as a transport for a bounded feature.

This is a capability route, not a compiled sample:

~~~text
user outcome
  -> central/peripheral role decision
  -> target, permission, and radio check
  -> lifecycle owner
  -> discovery or advertising session
  -> identity and protocol trust
  -> GATT discovery
  -> typed adapter
  -> user command or AI proposal
  -> payload validation and transport
  -> notification/response/reconnect reconciliation
  -> physical and release evidence
~~~

## Route contract

### Inputs

- named Xcode target, SDK, deployment platform, and device role;
- NSBluetoothAlwaysUsageDescription and any background modes;
- a required service/characteristic UUID contract;
- accessory identity and protocol version policy;
- user-started session or supported background route;
- typed user intent or selected AI context;
- physical side-effect safety policy.

### Outputs

- discovery/session state;
- a value-only device projection;
- typed GATT values and protocol events;
- command result plus reported-state reconciliation;
- optional restored-session checkpoint;
- evidence for simulator, physical accessory, two-device, accessibility, energy, and release gates.

### Non-goals

- treating a discovered name, UUID, or RSSI as authenticated identity;
- parsing or writing raw Data in SwiftUI;
- polling a device indefinitely;
- claiming background execution from a UIBackgroundModes entry alone;
- claiming a write-without-response was delivered;
- allowing an AI model to invent UUIDs or byte payloads;
- using Core Bluetooth in place of HomeKit/Matter when the device belongs in the user’s home model.

## Choose the role

| Need | Route | Proof requirement |
| --- | --- | --- |
| App controls a hardware accessory | CBCentralManager -> CBPeripheral | Physical accessory and protocol response. |
| App publishes a service | CBPeripheralManager -> CBMutableService/Characteristic | Second-device central and local peripheral behavior. |
| Two iOS devices exchange data | Both roles | Two signed devices and protocol convergence. |
| Nearby distance or direction | Nearby Interaction plus an exchange transport | Separate identity and side-effect proof. |
| Home accessory | HomeKit/Matter | Shared-home authorization and system route. |

Do not mix central and peripheral ownership in one view model. Choose a coordinator per role and make cross-role protocol state explicit.

## Permission and radio gate

Map CBManager.authorization and manager state before any operation:

~~~swift
enum BluetoothGate {
    case notDetermined
    case denied
    case restricted
    case poweredOff
    case resetting
    case unsupported
    case unauthorized
    case poweredOn
}
~~~

The route is ready only when:

- authorization permits the selected role;
- the manager is poweredOn;
- the target includes the usage description;
- the requested service/role is supported;
- the session is user-visible or explicitly covered by a background policy.

If a gate fails, stop scan/connect/write operations and expose recovery. Do not leave a stale ready control on screen.

## Central coordinator

One central coordinator owns scan, connect, discovery, and command queues:

~~~text
CentralCoordinator
  CBCentralManager
  discovered candidates
  selected session
  CBPeripheral delegate
  protocol adapter
  command queue
  value snapshot publisher
~~~

Start the manager once. Wait for centralManagerDidUpdateState. When powered on:

1. start a bounded scan;
2. filter by required service UUIDs when possible;
3. stop scan after candidate selection;
4. connect;
5. set the peripheral delegate;
6. discover required services;
7. discover required characteristics/descriptors;
8. verify properties and protocol identity;
9. publish ready.

If the user cancels, stopScan and cancel pending connection/session work. If the view disappears, decide whether the product session should end; do not let view lifetime accidentally keep the radio active.

## Peripheral coordinator

For an app acting as a peripheral:

1. create CBPeripheralManager with an intentional delegate queue;
2. wait for peripheralManagerDidUpdateState and poweredOn;
3. create services and characteristics with the documented properties/permissions;
4. add them to the local GATT database;
5. advertise only when the user or product session requires it;
6. handle read/write/subscription requests with bounded work;
7. send notifications only to subscribed centrals;
8. stop advertising and remove services when the session ends.

Background peripheral behavior, advertising data, and request handling have different limits. Test the target device rather than assuming that a foreground peripheral route continues unchanged in the background.

## Identity and handshake

Use a product identity adapter:

~~~swift
struct CandidateIdentity {
    let peripheralID: UUID
    let advertisedServices: Set<UUID>
    let displayName: String?
    let discoveredAt: Date
}

struct VerifiedAccessory {
    let peripheralID: UUID
    let productID: String
    let serial: String?
    let protocolVersion: String
    let sessionNonce: Data
}
~~~

Identity route:

~~~text
candidate
  -> connect
  -> discover expected identity characteristic
  -> challenge/response or protected read
  -> validate product and protocol
  -> verified session
~~~

The handshake must be specific to the accessory protocol. A name match, service UUID, RSSI, or connect callback is not an authentication scheme.

## GATT discovery route

Discover only what the feature needs:

1. required service UUIDs;
2. required characteristic UUIDs;
3. descriptors only when formatting, user description, or protocol metadata matters;
4. read/write/notify properties;
5. maximum write length for the selected write type;
6. protocol version and feature capabilities.

Create a capability map:

~~~swift
struct GATTCapability {
    let serviceID: CBUUID
    let characteristicID: CBUUID
    let canRead: Bool
    let canWrite: Bool
    let canWriteWithoutResponse: Bool
    let canNotify: Bool
    let maximumWriteLength: Int
}
~~~

Do not expose a control until the capability map and protocol adapter agree on the value type and safety policy.

## Typed payload route

Use a versioned adapter:

~~~swift
protocol AccessoryProtocol {
    associatedtype State
    associatedtype Command

    func decodeState(_ data: Data) throws -> State
    func encode(_ command: Command, maximumLength: Int) throws -> Data
    func validate(_ command: Command, against state: State) throws
}
~~~

The real target may use concrete types instead of an associated-type protocol. The important boundary is:

~~~text
Data
  -> length/version/checksum/authentication
  -> decoder
  -> typed state
  -> SwiftUI

typed command
  -> policy/range/identity validation
  -> encoder
  -> write type and length check
  -> Core Bluetooth
~~~

Never use a stringly typed model as the source of safety-critical bytes.

## Read/write/notify route

For a read:

- verify the characteristic supports read;
- call readValue;
- decode only the expected version/type;
- record timestamp and session revision;
- publish current state.

For a write with response:

- verify the write property;
- validate length and payload;
- enqueue one command;
- wait for didWriteValueForCharacteristic;
- keep the reported state unchanged until response/notification/read;
- reconcile errors and retry only with a product policy.

For a write without response:

- verify the accessory and protocol explicitly support the mode;
- respect canSendWriteWithoutResponse and flow control;
- use framing/sequence if the protocol needs it;
- label the result as sent, not delivered or physically complete;
- wait for a device report to show the effect.

For notifications:

- call setNotifyValue only for required characteristics;
- handle subscription callback errors;
- reassemble fragmented reports;
- deduplicate/sequence according to the protocol;
- disable or restore subscriptions with session lifecycle;
- re-read after reconnect when state may have changed.

## SwiftUI projection route

Publish value-only state:

~~~swift
struct AccessorySnapshot: Identifiable {
    let id: UUID
    let name: String
    let connection: ConnectionState
    let verification: VerificationState
    let services: [AccessoryServiceSnapshot]
    let lastReportedAt: Date?
    let revision: Int
}

struct AccessoryServiceSnapshot: Identifiable {
    let id: UUID
    let title: String
    let value: TypedValue
    let writable: Bool
    let notifiable: Bool
    let freshness: Freshness
    let pendingCommand: CommandID?
}
~~~

The view should not retain a CBPeripheral or mutate Data. It should send intents to the coordinator:

~~~text
View
  -> .scan / .connect / .disconnect
  -> .setTypedValue
  -> .sendCommand
  -> .reviewProposal

Coordinator
  -> validation
  -> protocol adapter
  -> Core Bluetooth
  -> snapshot/reconciliation
~~~

## Background and restoration route

If the product needs background central behavior:

1. document the user-visible need;
2. add bluetooth-central only when the use case qualifies;
3. use state preservation/restoration options;
4. implement willRestoreState;
5. reconstruct managers after relaunch;
6. restore only the needed peripherals and subscriptions;
7. checkpoint quickly;
8. return to the system;
9. show a truthful last-event state on next foreground launch.

If the product needs background peripheral behavior, use bluetooth-peripheral and prove local advertising/request behavior separately. Background modes do not provide unlimited time, continuous scanning, or immunity from termination.

## Local AI route

Create a proposal from selected typed context:

~~~swift
struct BluetoothCommandProposal {
    let accessoryID: UUID
    let sessionRevision: Int
    let serviceID: CBUUID
    let characteristicID: CBUUID
    let typedCommand: String
    let encodedPreview: String
    let warnings: [String]
    let requiresConfirmation: Bool
}
~~~

The model may draft typedCommand text only if a deterministic adapter maps it to one known command. It must not invent encodedPreview; that field should be produced by the protocol adapter after validation. At apply:

1. verify the same accessory session is still verified;
2. compare session/protocol revision;
3. resolve the characteristic;
4. validate command and safety policy;
5. show exact effect and response semantics;
6. require confirmation;
7. encode and write through the command owner;
8. reconcile the device report.

## Liquid Glass route

Use a bounded status/action group:

~~~text
device identity and verification
  -> connection state
  -> typed service values
  -> primary semantic control
  -> result/freshness
~~~

Use GlassEffectContainer when related controls need to read as one functional group. Use system material or opaque fallback when glass is unavailable, reduced, or harms contrast. Keep the pairing/permission system surface outside app-owned decoration.

## Validation and stop conditions

Stop if:

- Bluetooth permission or poweredOn is missing;
- the target role is not supported;
- the accessory cannot be identified beyond a name/UUID/RSSI;
- the required GATT service or characteristic is absent;
- the payload is unknown, malformed, out of range, or too large;
- a proposal is stale or ambiguous;
- the action has a physical/security consequence without confirmation;
- background behavior has not been proven for the release target;
- the UI claims delivered/complete without a response or report;
- a simulator packet is being treated as physical accessory proof.

## Evidence packet

Record:

- target, SDK, Info.plist, capability, usage description, background modes, and signing;
- authorization and manager-state transitions;
- scan filter, duplicate policy, candidate expiry, and identity handshake;
- service/characteristic/descriptor discovery;
- read, write-with-response, write-without-response, notification, timeout, and reconnect;
- background wake/restoration/termination where claimed;
- central, peripheral, or two-device physical route;
- AI invalid-payload, stale-session, ambiguous-device, and confirmation rejection;
- accessibility, energy, privacy, archive, and release evidence.

## Sources

- [Core Bluetooth](https://developer.apple.com/documentation/corebluetooth)
- [CBCentralManager](https://developer.apple.com/documentation/corebluetooth/cbcentralmanager)
- [CBCentralManagerDelegate](https://developer.apple.com/documentation/corebluetooth/cbcentralmanagerdelegate)
- [CBManager](https://developer.apple.com/documentation/corebluetooth/cbmanager)
- [CBManagerAuthorization](https://developer.apple.com/documentation/corebluetooth/cbmanagerauthorization)
- [CBManagerState](https://developer.apple.com/documentation/corebluetooth/cbmanagerstate)
- [CBPeripheral](https://developer.apple.com/documentation/corebluetooth/cbperipheral)
- [CBPeripheralDelegate](https://developer.apple.com/documentation/corebluetooth/cbperipheraldelegate)
- [CBService](https://developer.apple.com/documentation/corebluetooth/cbservice)
- [CBCharacteristic](https://developer.apple.com/documentation/corebluetooth/cbcharacteristic)
- [CBDescriptor](https://developer.apple.com/documentation/corebluetooth/cbdescriptor)
- [CBUUID](https://developer.apple.com/documentation/corebluetooth/cbuuid)
- [CBPeripheralManager](https://developer.apple.com/documentation/corebluetooth/cbperipheralmanager)
- [CBPeripheralManagerDelegate](https://developer.apple.com/documentation/corebluetooth/cbperipheralmanagerdelegate)
- [Core Bluetooth Background Processing for iOS Apps](https://developer.apple.com/library/archive/documentation/NetworkingInternetWeb/Conceptual/CoreBluetooth_concepts/CoreBluetoothBackgroundProcessingForIOSApps/PerformingTasksWhileYourAppIsInTheBackground.html)
- [Best Practices for Interacting with a Remote Peripheral Device](https://developer.apple.com/library/archive/documentation/NetworkingInternetWeb/Conceptual/CoreBluetooth_concepts/BestPracticesForInteractingWithARemotePeripheralDevice/BestPracticesForInteractingWithARemotePeripheralDevice.html)
- [NSBluetoothAlwaysUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsbluetoothalwaysusagedescription)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
