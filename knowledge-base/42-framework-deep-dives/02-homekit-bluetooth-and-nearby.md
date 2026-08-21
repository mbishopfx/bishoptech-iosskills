# HomeKit, Core Bluetooth, Nearby Interaction, and Local Network

## Capability boundary

HomeKit, Core Bluetooth, Nearby Interaction, and Network/Bonjour all involve devices near a person, but they solve different problems:

| Outcome | Framework route | Primary data/permission boundary |
| --- | --- | --- |
| Read or control a home already configured in Apple Home | HomeKit and `HMHomeManager` | Shared home database, HomeKit capability/entitlement, `NSHomeKitUsageDescription`, accessory permissions, physical-world side effects. |
| Exchange a product-specific protocol with a Bluetooth LE accessory | Core Bluetooth | Radio/authorization state, GATT services and characteristics, `NSBluetoothAlwaysUsageDescription`, reconnect/background policy, accessory firmware. |
| Measure relative distance/direction to a supported peer or accessory | Nearby Interaction | `NSNearbyInteractionUsageDescription`, discovery/configuration token exchange, UWB/device support, session lifecycle, physical device. |
| Discover and connect to a service on the same local network | Network framework and Bonjour | Local-network permission, `NSBonjourServices`, optional multicast entitlement, service identity, transport security, network topology. |

Discovery is not identity, authentication, authorization, safety, or compatibility. A device name, Bluetooth identifier, Bonjour result, HomeKit accessory, or Nearby token becomes an app action only after the product’s protocol and user-confirmation rules accept it.

## HomeKit route

### Shared home state and permission

HomeKit stores home automation information in a database shared with Apple’s Home app and other authorized HomeKit apps. Create one app-owned `HMHomeManager`, observe its delegate callbacks, and treat `homes`, rooms, accessories, services, and characteristic values as shared external state that can change outside the process.

Enable the HomeKit capability and provide a truthful `NSHomeKitUsageDescription` before the app uses the framework. The first use normally prompts for permission; there is no separate explicit request method. Inspect `authorizationStatus`, handle the `authorized` bit, and expect the person to revoke access in Settings later. A denied or revoked route should remove/disable dependent controls while keeping unrelated app functionality usable.

### Reading versus changing the physical world

Reading a characteristic and writing a characteristic have different product risk. For every write:

1. Identify the home, room, accessory, service, and characteristic in the app-owned state.
2. Confirm that the accessory and value are still available and that the person has permission.
3. Explain the physical effect in the confirmation UI when it could surprise someone or affect safety/security.
4. Write only the value and characteristic needed by the user action.
5. Show success, stale/unavailable, authorization, and error states; do not assume the callback means the physical effect is safe or permanent.

Treat HomeKit callbacks and external Home app edits as state changes. Do not cache a “light is on” or “door is locked” claim without labeling it as last-known state and updating it when HomeKit reports a change.

## Core Bluetooth route

### Central and peripheral roles

Use `CBCentralManager` when the iPhone/iPad discovers and connects to a remote Bluetooth LE peripheral. Use `CBPeripheralManager` when the app publishes a local GATT service for another central. These roles have different background modes, protocols, and device matrices; do not mix them into a generic “Bluetooth connected” boolean.

For a central, the lifecycle is:

`managerCreated -> authorization/radioState -> poweredOn -> scan -> discovered -> userSelected/validated -> connecting -> connected -> discoverServices -> discoverCharacteristics -> read/write/subscribe -> disconnected/retry`

Wait for the manager to report `poweredOn` before scanning or connecting. Scan for the service UUIDs the product actually supports, stop scanning once the selection/connection route is chosen, set the peripheral delegate before discovery, and validate the expected GATT service/characteristic UUIDs before writing or subscribing.

### Permission, radio, and protocol state

Handle `unknown`, `resetting`, `unsupported`, `unauthorized`, and `poweredOff`/`poweredOn` states separately. Bluetooth authorization does not mean a compatible accessory exists, and a discovered peripheral does not prove it belongs to the person or implements the product protocol. Use a versioned protocol schema, validate payload length/type/range, and set timeouts for discovery, writes, notifications, and reconnect.

Add the correct Bluetooth usage description before accessing the radio. Background central/peripheral behavior is limited and depends on the selected modes and current OS/device rules. Do not promise scanning, notifications, or control continuity in the background without target-specific documentation and physical-device evidence. A Live Activity or background mode is not a substitute for protocol, battery, and privacy review.

### Reconnect and teardown

Stop scans when the feature ends, cancel pending connections, remove notification subscriptions where appropriate, and release the feature owner. On disconnect, retain only the minimum app-owned identity needed for an intentional reconnect, show the reason/last-seen time, and require user confirmation before reconnecting to an ambiguous device. Never spin an unbounded reconnect loop.

## Nearby Interaction route

Nearby Interaction measures relative distance and, where supported, direction between a device and a peer/accessory using a session-specific configuration. It is not a general location service, a proof of identity, or a replacement for an application transport.

Before starting a session, provide `NSNearbyInteractionUsageDescription`, check device/framework support, and obtain the required peer discovery token or accessory configuration through a separate authenticated/out-of-band exchange. For peer devices, `NINearbyPeerConfiguration` uses the other peer’s `NIDiscoveryToken`; for third-party accessories, use the accessory configuration route and the accessory protocol. Token exchange over Multipeer Connectivity or Network is a separate route that needs its own trust and local-network handling.

Run one intentional `NISession` per interaction, observe delegate callbacks for updates, invalidation, suspension, and removal, and invalidate it when the feature ends. Coach the person when the framework reports that range, line of sight, or camera assistance is needed. Background behavior is conditional: do not assume a foreground ranging session continues after suspension; current Apple documentation has special rules for connected Bluetooth accessories and system surfaces that must be rechecked for the target SDK.

## Local-network discovery and transport

Use `NWBrowser` for Bonjour service discovery and `NWConnection` for a product-owned transport. Provide `NSLocalNetworkUsageDescription` and declare the Bonjour service types in `NSBonjourServices` when the app browses or resolves Bonjour services. Multicast/broadcast operations can require the `com.apple.developer.networking.multicast` entitlement and separate review.

Model browser states such as `setup`, `ready`, `waiting`, `failed`, and `cancelled`. A local-network denial can surface as a waiting/unsatisfied state rather than a useful result; preserve a manual host/QR/pairing route if the product supports one. Do not treat a Bonjour name or IP address as authentication. Establish service identity, encrypt sensitive traffic, authenticate the peer, validate protocol versions, and handle network changes/reconnect.

Local-network access is separate from HomeKit access, Bluetooth authorization, Nearby Interaction permission, and internet reachability. A device can be discoverable but unreachable, reachable but unauthenticated, or authenticated but incompatible.

## API route matrix

Select the adapter from the physical or network outcome. Keep candidate discovery, protocol validation, user trust, and side effects as separate steps.

| Outcome | API seam | Domain handoff | Target/permission/proof gate |
| --- | --- | --- | --- |
| Inspect or control a Home accessory | `HMHomeManager` -> `HMHome` -> `HMAccessory`/`HMService`/`HMCharacteristic` | Home/room/accessory/service/characteristic IDs, last-known value, read/write result | HomeKit capability/usage description, authorization changes, external Home app edits, physical accessory write, and safety confirmation. |
| Discover a BLE peripheral | `CBCentralManager.scanForPeripherals` with service UUID filters | Candidate identifier, advertised service/protocol version, RSSI as a hint, last-seen time | Bluetooth authorization/radio state, scan timeout, duplicate/disappearing candidates, and physical accessory compatibility. |
| Connect and exchange GATT data | `connect` -> `discoverServices` -> `discoverCharacteristics` -> read/write/notify | Typed protocol messages with sequence/timeout/error state | Validate service/characteristic UUIDs, payload length/type/range, write acknowledgment, disconnect, reconnect, and firmware version. |
| Publish a BLE service | `CBPeripheralManager` and GATT service/characteristic route | Local role, subscribed centrals, bounded value updates | Peripheral role, background mode limits, radio state, privacy, and a second-device physical test. |
| Measure peer/accessory proximity | `NISession` with `NINearbyPeerConfiguration` or accessory configuration | Distance/direction sample, timestamp, session/configuration identity, quality state | Discovery-token/authenticated exchange, UWB/device support, usage description, session suspension/invalidation, and physical range test. |
| Find a local-network service | `NWBrowser`/Bonjour | Service endpoint candidate, TXT/protocol version, discovery time | Local-network usage description, Bonjour declarations, optional multicast entitlement, service disappearance, and manual pairing fallback. |
| Connect to a service | `NWConnection` with explicit parameters/TLS/protocol | Authenticated connection state, peer identity, request/response | Network changes, TLS/authentication, timeout/retry/idempotency, server protocol version, and device/network topology. |

## Capability and target matrix

| Route | Owning target/configuration | Separate evidence |
| --- | --- | --- |
| HomeKit app | App target with HomeKit capability and `NSHomeKitUsageDescription` | Authorization/revocation, home topology, external edits, simulator/prototype, and representative physical writes. |
| BLE central | App target with Bluetooth usage description; background central mode only if justified | Radio state, discovery, GATT protocol, reconnect, power/thermal, and physical accessory. |
| BLE peripheral | App target with peripheral route and documented background behavior | Second central/device, service advertisement, subscription, disconnect, and background limits. |
| Nearby Interaction | App target with `NSNearbyInteractionUsageDescription` and selected peer/accessory route | Token exchange/authentication, supported devices, ranging, session invalidation, and physical environment. |
| Local network | App target with local-network usage/Bonjour declarations and multicast entitlement only if required | Permission prompt, browser/connection, TLS/protocol identity, network changes, and manual fallback. |
| Widget/App Intent/Live Activity | Extension/system target with a minimal last-known projection | Never perform an unconfirmed physical write from stale system-surface state; verify invocation, freshness, authorization, and physical effect separately. |

## Trust and side-effect pipeline

Use this pipeline for every accessory or physical-world action:

`candidate -> protocol match -> authenticated/trusted -> current state read -> user confirmation -> bounded write -> acknowledged/reconciled state`

For a model-assisted command, the model may propose a target/value, but it must not select an unknown accessory, bypass authorization, or trigger an irreversible write. Require a stable app-owned target identity, current readback where possible, a user-visible effect description, an idempotency/sequence key, timeout handling, and a safe retry/manual route.

Keep `discovered`, `connected`, `authenticated`, `authorized`, `selected`, `stale`, `revoked`, and `lastKnownValue` as independent fields. A peripheral identifier can change or be spoofed; a Bonjour name can be duplicated; a Nearby token can expire; a HomeKit value can change in the Home app. Retain only the minimum identity/provenance needed to make the next action deliberate.

## Unified state and trust model

Keep framework state, product trust, and user action separate:

| Layer | Example state | Product question |
| --- | --- | --- |
| Framework availability | `poweredOff`, `unauthorized`, `waiting`, `unsupported` | Can this route operate on this device and permission state? |
| Discovery | HomeKit home, `CBPeripheral`, `NWBrowser.Result`, Nearby token | What candidate did the framework report, and when? |
| Protocol/session | Connected, services discovered, authenticated, ranging | Does this candidate speak the expected product protocol now? |
| User intent | Selected, confirmed, cancelled | Did the person authorize this connection or physical-world action? |
| Durable state | Last seen, configured, trusted, revoked | What minimum identity/metadata can be retained, and for how long? |

Do not collapse these layers into `isConnected` or `isNearby`. Every route needs visible loading, unavailable, denied, stale, disconnected, protocol-error, and retry/manual states.

## Privacy and physical-world safety

Nearby and home data can reveal routines, occupancy, relationships, and physical control. Avoid logging private home names, accessory identifiers, raw Bluetooth payloads, discovery tokens, coordinates, or local-network addresses. Retain only what the feature needs, explain retention, support deletion/revocation, and keep analytics aggregated or redacted.

For actions that unlock, open, heat, alarm, monitor, or otherwise affect the physical world, require an explicit product confirmation, show the intended target/value, and make the result reversible where possible. Discovery or a model suggestion must never silently trigger a physical side effect.

## Verification route

- HomeKit: capability/entitlement, usage description, allow/deny/revoke, multiple homes/rooms, accessory removal, external Home app edits, stale values, physical writes, HomeKit Accessory Simulator, and representative physical accessories.
- Bluetooth: supported radio/device matrix, authorization states, powered-off/reset/unsupported, scan filters, duplicate/disappearing peripherals, GATT schema/version, connection timeout, notifications, disconnect/reconnect, background/foreground, and battery/thermal behavior.
- Nearby Interaction: supported UWB/device matrix, usage prompt, valid/invalid token/configuration, out-of-band exchange, line-of-sight/range coaching, session suspension/invalidation/removal, background policy, and physical-device measurements.
- Local network: prompt/denial, Bonjour declarations, `NWBrowser` state changes, service disappearance, network change, authentication failure, TLS/protocol validation, multicast entitlement if needed, and manual pairing fallback.
- Accessibility and safety: readable discovery/progress/error states, non-proximity alternative, confirmation before physical writes, VoiceOver labels, reduced motion, and a visible/audible confirmation channel.

Simulator UI and a mocked discovery response can validate state rendering and protocol parsing. They do not prove radio behavior, UWB ranging, local-network privacy, accessory firmware compatibility, home topology, battery, or physical-world side effects. Record target devices, OS builds, capabilities, permissions, accessories, network topology, and test date for any release claim.

## Sources

- [HomeKit](https://developer.apple.com/documentation/homekit)
- [HMHomeManager](https://developer.apple.com/documentation/homekit/hmhomemanager)
- [HMAccessory](https://developer.apple.com/documentation/homekit/hmaccessory)
- [HMService](https://developer.apple.com/documentation/homekit/hmservice)
- [HMCharacteristic](https://developer.apple.com/documentation/homekit/hmcharacteristic)
- [Enabling HomeKit in your app](https://developer.apple.com/documentation/homekit/enabling-homekit-in-your-app)
- [HomeKit entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.homekit)
- [NSHomeKitUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nshomekitusagedescription)
- [Core Bluetooth](https://developer.apple.com/documentation/corebluetooth)
- [CBCentralManager](https://developer.apple.com/documentation/corebluetooth/cbcentralmanager)
- [CBCentralManagerDelegate](https://developer.apple.com/documentation/corebluetooth/cbcentralmanagerdelegate)
- [CBPeripheral](https://developer.apple.com/documentation/corebluetooth/cbperipheral)
- [CBPeripheralDelegate](https://developer.apple.com/documentation/corebluetooth/cbperipheraldelegate)
- [CBPeripheralManager](https://developer.apple.com/documentation/corebluetooth/cbperipheralmanager)
- [CBUUID](https://developer.apple.com/documentation/corebluetooth/cbuuid)
- [CBManager authorization](https://developer.apple.com/documentation/corebluetooth/cbmanager/authorization-swift.type.property)
- [NSBluetoothAlwaysUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsbluetoothalwaysusagedescription)
- [Nearby Interaction](https://developer.apple.com/documentation/nearbyinteraction)
- [Initiating and maintaining a session](https://developer.apple.com/documentation/nearbyinteraction/initiating-and-maintaining-a-session)
- [NISession](https://developer.apple.com/documentation/nearbyinteraction/nisession)
- [NINearbyPeerConfiguration](https://developer.apple.com/documentation/nearbyinteraction/ninearbypeerconfiguration)
- [NINearbyAccessoryConfiguration](https://developer.apple.com/documentation/nearbyinteraction/ninearbyaccessoryconfiguration)
- [NSNearbyInteractionUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsnearbyinteractionusagedescription)
- [Network](https://developer.apple.com/documentation/network)
- [NWBrowser](https://developer.apple.com/documentation/network/nwbrowser)
- [NWConnection](https://developer.apple.com/documentation/network/nwconnection)
- [NWParameters](https://developer.apple.com/documentation/network/nwparameters)
- [NSLocalNetworkUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nslocalnetworkusagedescription)
- [NSBonjourServices](https://developer.apple.com/documentation/bundleresources/information-property-list/nsbonjourservices)
- [Understanding local network privacy](https://developer.apple.com/documentation/technotes/tn3179-understanding-local-network-privacy)
- [Multipeer Connectivity](https://developer.apple.com/documentation/multipeerconnectivity)
