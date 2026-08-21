# HomeKit, Bluetooth, Nearby, and Local-Network Recipes

These routes follow the [device and companion capability contracts](../42-framework-deep-dives/08-device-and-companion-capability-contracts.md): discovery is not trust, permission is not capability, and physical side effects require current-state validation.

## Scope and compile boundary

These are compile-oriented route sketches for shared HomeKit state, Bluetooth LE central discovery, Nearby Interaction sessions, and Bonjour/local-network browsing. They are not compiled in this documentation-only workspace and do not prove accessory compatibility, radio/UWB behavior, local-network privacy, background execution, protocol security, battery/thermal cost, or physical-world side effects.

Keep the route layered:

`permission/capability -> discovery -> protocol/session -> user confirmation -> side effect or durable state`

Discovery is not trust. A framework object must be validated against the product protocol and user intent before the app reads sensitive data, writes a physical value, pairs, persists an identifier, or sends a message.

## Recipe 1: create one HomeKit manager and observe authorization

Enable the HomeKit capability and add a truthful `NSHomeKitUsageDescription` before creating the manager. HomeKit prompts on first framework use rather than through a separate explicit authorization call.

```swift
import HomeKit

final class HomeStore: NSObject, HMHomeManagerDelegate {
    private let manager: HMHomeManager

    private(set) var isAuthorized = false
    private(set) var homes: [HMHome] = []
    private(set) var message = "Home access has not been checked"

    override init() {
        manager = HMHomeManager()
        super.init()

        // Keep one manager alive for the feature/app lifetime and observe
        // changes made by Apple Home or another authorized HomeKit app.
        manager.delegate = self
        refreshState()
    }

    func refreshState() {
        isAuthorized = manager.authorizationStatus.contains(.authorized)
        homes = isAuthorized ? manager.homes : []
        message = isAuthorized ? "Home data available" : "Home access unavailable"
    }

    func homeManagerDidUpdateHomes(_ manager: HMHomeManager) {
        refreshState()
    }

    func homeManagerDidUpdatePrimaryHome(_ manager: HMHomeManager) {
        refreshState()
    }
}
```

Treat `homes`, rooms, accessories, services, and characteristic values as shared external state. A person can revoke permission in Settings or change the home in Apple’s Home app while your process is suspended. Keep unrelated app features usable when HomeKit is denied, and display a settings/manual route when HomeKit is essential to a clearly scoped feature.

## Recipe 2: make HomeKit writes reviewable

A read/write callback is a framework seam, not a product authorization policy. Convert framework objects into an app-owned target and require confirmation for physical effects that could surprise someone.

```swift
import HomeKit

enum HomeActionError: Error {
    case notWritable
}

func writeHomeValue(
    _ value: Any,
    to characteristic: HMCharacteristic
) async throws {
    guard characteristic.properties.contains(HMCharacteristicPropertyWritable) else {
        throw HomeActionError.notWritable
    }

    try await withCheckedThrowingContinuation { continuation in
        characteristic.writeValue(value) { error in
            if let error {
                continuation.resume(throwing: error)
            } else {
                continuation.resume(returning: ())
            }
        }
    }
}
```

Before calling this function, confirm the target home/room/accessory/service/characteristic is still present, the person selected it, the value is in the product’s allowed range, and the UI states the physical effect. After the callback, show success or failure but do not claim a safety/security result that the product has not independently verified. Preserve last-known values with timestamps and respond to external HomeKit changes.

## Recipe 3: central Bluetooth state and discovery

Create and retain one central manager for the feature. Wait for `.poweredOn` before scanning. Use the service UUIDs the product actually supports and do not auto-connect to the first nearby peripheral without a product-level selection/trust rule.

```swift
import CoreBluetooth

final class BluetoothCentral: NSObject, CBCentralManagerDelegate, CBPeripheralDelegate {
    private let serviceUUID = CBUUID(string: "0000FFF0-0000-1000-8000-00805F9B34FB")
    private var central: CBCentralManager!
    private(set) var candidates: [CBPeripheral] = []
    private(set) var connected: CBPeripheral?

    override init() {
        super.init()

        // Use a deliberate queue. This example routes delegate work to main
        // so a view model can publish state without an extra hop.
        central = CBCentralManager(delegate: self, queue: .main)
    }

    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        guard central.state == .poweredOn else {
            candidates.removeAll()
            connected = nil
            // Publish unauthorized, unsupported, resetting, or powered-off
            // as distinct user-facing states in the real feature.
            return
        }
    }

    func startScan() {
        guard central.state == .poweredOn else { return }

        candidates.removeAll()
        central.scanForPeripherals(
            withServices: [serviceUUID],
            options: [CBCentralManagerScanOptionAllowDuplicatesKey: false]
        )
    }

    func stopScan() {
        central.stopScan()
    }

    func centralManager(
        _ central: CBCentralManager,
        didDiscover peripheral: CBPeripheral,
        advertisementData: [String: Any],
        rssi RSSI: NSNumber
    ) {
        guard !candidates.contains(where: { $0.identifier == peripheral.identifier }) else {
            return
        }

        candidates.append(peripheral)
        // Keep advertisement data/RSSI ephemeral unless the product has a
        // documented reason to retain a redacted value.
    }

    func connect(_ peripheral: CBPeripheral) {
        stopScan()
        peripheral.delegate = self
        central.connect(peripheral)
    }

    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        connected = peripheral
        peripheral.discoverServices([serviceUUID])
    }

    func centralManager(
        _ central: CBCentralManager,
        didFailToConnect peripheral: CBPeripheral,
        error: Error?
    ) {
        connected = nil
        // Publish a retry/manual-selection state with the error category.
    }

    func centralManager(
        _ central: CBCentralManager,
        didDisconnectPeripheral peripheral: CBPeripheral,
        error: Error?
    ) {
        if connected?.identifier == peripheral.identifier {
            connected = nil
        }
        // Reconnect only under an intentional, bounded product policy.
    }

    func disconnect() {
        stopScan()
        if let connected {
            central.cancelPeripheralConnection(connected)
        }
        self.connected = nil
    }

    func peripheral(
        _ peripheral: CBPeripheral,
        didDiscoverServices error: Error?
    ) {
        guard error == nil,
              let service = peripheral.services?.first(where: { $0.uuid == serviceUUID }) else {
            return
        }

        peripheral.discoverCharacteristics(nil, for: service)
    }

    func peripheral(
        _ peripheral: CBPeripheral,
        didDiscoverCharacteristicsFor service: CBService,
        error: Error?
    ) {
        guard error == nil else { return }
        // Validate the expected characteristic UUIDs and properties here.
        // Do not write until the product protocol has been validated.
    }
}
```

Replace the example UUID with the accessory protocol’s documented identifiers. Validate characteristic properties, payload length/type/range, protocol version, and write acknowledgment. Add timeouts for scan, connect, service discovery, characteristic discovery, writes, and notifications. Call `disconnect()` when the feature ends; do not leave a scan or connection owned by a disappearing view.

## Recipe 4: session-scoped Nearby Interaction

Nearby Interaction needs a session-specific peer token or accessory configuration delivered through a separate exchange. The session does not discover or authenticate the other product by itself.

```swift
import NearbyInteraction

final class NearbySession: NSObject, NISessionDelegate {
    private let session = NISession()
    private(set) var isRunning = false

    override init() {
        super.init()
        session.delegate = self
    }

    func start(with peerToken: NIDiscoveryToken) {
        guard NISession.isSupported else {
            isRunning = false
            return
        }

        let configuration = NINearbyPeerConfiguration(peerToken: peerToken)
        session.run(configuration)
        isRunning = true
    }

    func session(
        _ session: NISession,
        didUpdate nearbyObjects: [NINearbyObject]
    ) {
        guard let object = nearbyObjects.first else { return }
        // Treat distance/direction as a current measurement with an explicit
        // timestamp and uncertainty, not as identity or absolute location.
        _ = object
    }

    func session(_ session: NISession, didInvalidateWith error: Error) {
        isRunning = false
        // Distinguish user denial, invalid configuration, device loss, and
        // other errors in the feature state.
    }

    func sessionWasSuspended(_ session: NISession) {
        isRunning = false
    }

    func sessionSuspensionEnded(_ session: NISession) {
        isRunning = true
        // Re-run or re-establish the configuration according to the product
        // state and current peer trust; do not assume the old measurement is fresh.
    }

    func stop() {
        session.invalidate()
        isRunning = false
    }
}
```

Add `NSNearbyInteractionUsageDescription`, check the target device’s support, and implement the out-of-band token/configuration exchange separately. For background use, follow the current Nearby Interaction documentation for the exact supported peer/accessory and system-surface route; a suspended session must render a clear state and stop using old measurements as current.

## Recipe 5: browse a local Bonjour service

Use `NWBrowser` for discovery and `NWConnection` for a product-owned connection. Add `NSLocalNetworkUsageDescription` and the declared service type in `NSBonjourServices`. If the product uses multicast/broadcast, review the separate multicast entitlement.

```swift
import Network

final class LocalServiceBrowser {
    private let queue = DispatchQueue(label: "local-service-browser")
    private let browser: NWBrowser

    init() {
        browser = NWBrowser(
            for: .bonjour(type: "_example._tcp", domain: nil),
            using: .tcp
        )

        browser.stateUpdateHandler = { state in
            // Map setup, ready, waiting, failed, and cancelled to UI state.
            _ = state
        }

        browser.browseResultsChangedHandler = { results, changes in
            // A result is a candidate service, not an authenticated peer.
            _ = results
            _ = changes
        }
    }

    func start() {
        browser.start(queue: queue)
    }

    func stop() {
        browser.cancel()
    }
}
```

When a person selects a service, establish an authenticated and integrity-protected protocol before sending private data or accepting commands. Handle local-network denial, a service disappearing, network-path changes, waiting/unsatisfied states, protocol mismatch, TLS/authentication failure, and a manual pairing/QR route where appropriate. Never use a Bonjour name, IP address, or discovery result as a secret.

## Recipe 6: unify accessory state without hiding failure

Use framework-specific state plus product trust and intent instead of one `isConnected` flag:

```swift
enum AccessoryRouteState {
    case unavailable(reason: String)
    case awaitingPermission
    case discovering
    case candidateNeedsSelection
    case connecting
    case validatingProtocol
    case ready(lastSeen: Date)
    case suspended(reason: String)
    case stale(lastSeen: Date)
    case failed(message: String, canRetry: Bool)
    case cancelled
}

struct AccessoryIdentity {
    let appID: UUID
    let displayName: String
    let framework: String
    let protocolVersion: String?
    let lastSeen: Date?
    let isUserConfirmed: Bool
}
```

Persist only the minimum stable identifier and metadata needed for the product. Treat identifiers, discovery tokens, advertisement payloads, home names, accessory states, and local-network addresses as sensitive. Do not retain raw protocol data or private home topology in logs/analytics by default.

## Recipe 7: permission, capability, and fallback matrix

| Route | Required review | Meaningful fallback |
| --- | --- | --- |
| HomeKit | HomeKit capability/entitlement, `NSHomeKitUsageDescription`, authorization/revocation, shared-home state | Manual control, device-local behavior, or hide the optional integration. |
| Core Bluetooth | Bluetooth usage description, radio state, central/peripheral background mode only if justified, accessory protocol | Manual entry, cable/QR setup, or a disconnected state with retry. |
| Nearby Interaction | `NSNearbyInteractionUsageDescription`, supported UWB/device matrix, token/configuration exchange | Visual/list pairing, manual selection, or non-ranging workflow. |
| Local network | `NSLocalNetworkUsageDescription`, Bonjour declarations, multicast entitlement if required, authenticated transport | QR/manual address, cloud relay if intentionally designed, or offline mode. |

Never turn a missing permission or entitlement into a silent empty list. Preserve user input, explain the limitation, and make a safe next action available. Require confirmation before physical-world writes and visible/audible feedback after them.

## Physical-device verification matrix

| Test | Evidence to capture |
| --- | --- |
| HomeKit | Capability in signed target, prompt/denial/revocation, multiple homes/rooms, external Home app edits, accessory removal, stale value, physical write, and simulator/physical accessory comparison. |
| Bluetooth | Radio/authorization states, scan filters, duplicate/disappearing peripherals, connection/discovery timeouts, GATT schema/version, reads/writes/notifications, disconnect/reconnect, background/foreground, battery, and thermal behavior. |
| Nearby Interaction | Supported devices/UWB, usage prompt, valid/invalid token, out-of-band exchange, distance/direction updates, line-of-sight/range coaching, suspension/invalidation/removal, background rule, and measured physical behavior. |
| Local network | Permission prompt/denial, Bonjour declaration, browser state, service disappearance, network change, authentication/TLS/protocol failure, multicast requirement, and manual pairing. |
| Privacy and safety | No raw private identifiers/payloads in logs, deletion/revocation, confirmation before physical side effects, visible/audible feedback, VoiceOver, reduced motion, and error recovery. |

Previews, simulators, mocked peripherals, and recorded discovery responses validate UI/state rendering and protocol parsing. They do not prove radio/UWB behavior, accessory firmware compatibility, local-network privacy, home topology, battery/thermal cost, or physical-world safety. Record device family, OS build, capability/permission state, accessory firmware, network topology, and test date for any claim.

## Sources

- [HomeKit](https://developer.apple.com/documentation/homekit)
- [HMHomeManager](https://developer.apple.com/documentation/homekit/hmhomemanager)
- [Enabling HomeKit in your app](https://developer.apple.com/documentation/homekit/enabling-homekit-in-your-app)
- [HomeKit entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.homekit)
- [NSHomeKitUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nshomekitusagedescription)
- [Core Bluetooth](https://developer.apple.com/documentation/corebluetooth)
- [CBCentralManager](https://developer.apple.com/documentation/corebluetooth/cbcentralmanager)
- [CBCentralManagerDelegate](https://developer.apple.com/documentation/corebluetooth/cbcentralmanagerdelegate)
- [CBPeripheral](https://developer.apple.com/documentation/corebluetooth/cbperipheral)
- [CBPeripheralDelegate](https://developer.apple.com/documentation/corebluetooth/cbperipheraldelegate)
- [CBPeripheralManager](https://developer.apple.com/documentation/corebluetooth/cbperipheralmanager)
- [CBManager authorization](https://developer.apple.com/documentation/corebluetooth/cbmanager/authorization-swift.type.property)
- [NSBluetoothAlwaysUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsbluetoothalwaysusagedescription)
- [Nearby Interaction](https://developer.apple.com/documentation/nearbyinteraction)
- [Initiating and maintaining a session](https://developer.apple.com/documentation/nearbyinteraction/initiating-and-maintaining-a-session)
- [NISession](https://developer.apple.com/documentation/nearbyinteraction/nisession)
- [NINearbyPeerConfiguration](https://developer.apple.com/documentation/nearbyinteraction/ninearbypeerconfiguration)
- [NSNearbyInteractionUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsnearbyinteractionusagedescription)
- [Network](https://developer.apple.com/documentation/network)
- [NWBrowser](https://developer.apple.com/documentation/network/nwbrowser)
- [NWConnection](https://developer.apple.com/documentation/network/nwconnection)
- [NSLocalNetworkUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nslocalnetworkusagedescription)
- [NSBonjourServices](https://developer.apple.com/documentation/bundleresources/information-property-list/nsbonjourservices)
- [Understanding local network privacy](https://developer.apple.com/documentation/technotes/tn3179-understanding-local-network-privacy)
- [Multipeer Connectivity](https://developer.apple.com/documentation/multipeerconnectivity)
