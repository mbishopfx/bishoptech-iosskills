# SwiftUI Core Bluetooth and nearby-accessory review recipes

These are compile-oriented route sketches for a named iOS target. They keep Core Bluetooth delegates, protocol bytes, typed device state, SwiftUI presentation, AI proposals, and physical effects separate. Compile and run them against the selected SDK and accessory; do not treat a pasted recipe as radio, identity, background, or release proof.

This page pairs with [SwiftUI Core Bluetooth and nearby-accessory review](../42-framework-deep-dives/94-swiftui-core-bluetooth-and-nearby-accessory-review.md), [SwiftUI Core Bluetooth and nearby-accessory review route](../50-capability-recipes/125-swiftui-core-bluetooth-and-nearby-accessory-review-route.md), and the [proof matrix](../60-verification/119-swiftui-core-bluetooth-and-nearby-accessory-review-proof-matrix.md).

## Recipe 1: define transport and UI states

Start with explicit states:

~~~swift
enum BluetoothRouteState {
    case unavailable(String)
    case waitingForPermission
    case poweredOff
    case scanning
    case candidate(CandidateSnapshot)
    case connecting(CandidateSnapshot)
    case discovering(CandidateSnapshot)
    case verifying(CandidateSnapshot)
    case ready(AccessorySnapshot)
    case stale(AccessorySnapshot)
    case commandPending(CommandID)
    case failed(String)
}

enum BluetoothIntent {
    case startScan
    case stopScan
    case connect(UUID)
    case disconnect
    case refresh
    case send(AccessoryCommand)
    case review(BluetoothCommandProposal)
    case apply(BluetoothCommandProposal)
}
~~~

A route state is not a CBManagerState and is not a physical device state. It is the app’s product projection of several inputs.

## Recipe 2: create one central owner

Keep manager and delegate ownership outside SwiftUI rows:

~~~swift
import CoreBluetooth
import SwiftUI

@MainActor
final class BluetoothStore: NSObject, ObservableObject {
    @Published private(set) var route: BluetoothRouteState = .waitingForPermission

    private var central: CBCentralManager!
    private var candidates: [UUID: CandidateSnapshot] = [:]
    private var selected: CBPeripheral?
    private var adapter: AccessoryProtocolAdapter?
    private var sessionRevision = 0

    override init() {
        super.init()
        central = CBCentralManager(
            delegate: self,
            queue: nil,
            options: [
                CBCentralManagerOptionRestoreIdentifierKey: "com.example.bluetooth.central"
            ]
        )
    }

    func startScan() {
        guard central.state == .poweredOn else {
            route = .unavailable("Bluetooth is not ready.")
            return
        }
        candidates.removeAll()
        route = .scanning
        central.scanForPeripherals(
            withServices: requiredServiceUUIDs,
            options: [CBCentralManagerScanOptionAllowDuplicatesKey: false]
        )
    }

    func stopScan() {
        central.stopScan()
        if case .scanning = route {
            route = .waitingForPermission
        }
    }
}

extension BluetoothStore: CBCentralManagerDelegate {
    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        // Map authorization and state to explicit route states.
    }

    func centralManager(
        _ central: CBCentralManager,
        didDiscover peripheral: CBPeripheral,
        advertisementData: [String: Any],
        rssi RSSI: NSNumber
    ) {
        // Normalize candidate data and update the SwiftUI projection.
    }

    func centralManager(
        _ central: CBCentralManager,
        didConnect peripheral: CBPeripheral
    ) {
        selected = peripheral
        peripheral.delegate = self
        peripheral.discoverServices(requiredServiceUUIDs)
    }
}
~~~

The restoration identifier, delegate queue, and exact concurrency annotations must be checked in the target. The ownership rule is stable: one central, one session owner, and one command path.

## Recipe 3: model a candidate separately from a verified accessory

Do not use a display name as the device model:

~~~swift
struct CandidateSnapshot: Identifiable {
    let id: UUID
    let name: String
    let advertisedServices: Set<CBUUID>
    let discoveredAt: Date
    let signalDescription: String
    let isStale: Bool
}

struct VerifiedAccessory {
    let peripheralID: UUID
    let productID: String
    let serial: String?
    let protocolVersion: String
    let sessionRevision: Int
}
~~~

The candidate is a discovery observation. The verified accessory exists only after the product’s protocol identity and security requirements succeed.

## Recipe 4: stop scanning at the product boundary

Use service filters and stop scanning as soon as the session no longer needs discovery:

~~~swift
let requiredServiceUUIDs = [
    CBUUID(string: "0000FFF0-0000-1000-8000-00805F9B34FB")
]

func beginDiscovery() {
    guard central.state == .poweredOn else { return }
    central.scanForPeripherals(
        withServices: requiredServiceUUIDs,
        options: [
            CBCentralManagerScanOptionAllowDuplicatesKey: false
        ]
    )
}

func endDiscovery() {
    central.stopScan()
}
~~~

The UUID above is a placeholder, not a universal product contract. Use the accessory’s documented service UUID and test candidate filtering. Broad scans, duplicate advertisements, and indefinite scanning require explicit product justification and energy evidence.

## Recipe 5: connect and discover only the required GATT surface

Make the connection state explicit:

~~~swift
func connect(to peripheral: CBPeripheral) {
    endDiscovery()
    route = .connecting(candidate(for: peripheral))
    selected = peripheral
    central.connect(peripheral, options: nil)
}

func centralManager(
    _ central: CBCentralManager,
    didConnect peripheral: CBPeripheral
) {
    peripheral.delegate = self
    route = .discovering(candidate(for: peripheral))
    peripheral.discoverServices(requiredServiceUUIDs)
}

func peripheral(
    _ peripheral: CBPeripheral,
    didDiscoverServices error: Error?
) {
    guard error == nil else {
        route = .failed("Service discovery failed.")
        return
    }
    let services = peripheral.services ?? []
    for service in services where requiredServiceUUIDs.contains(service.uuid) {
        peripheral.discoverCharacteristics(
            requiredCharacteristicUUIDs,
            for: service
        )
    }
}
~~~

Do not expose a control until the required characteristics and properties have been validated.

## Recipe 6: build a capability map

The adapter should inspect properties once discovery completes:

~~~swift
struct GATTCapability {
    let serviceID: CBUUID
    let characteristicID: CBUUID
    let canRead: Bool
    let canWrite: Bool
    let canWriteWithoutResponse: Bool
    let canNotify: Bool
    let maximumWriteLengthWithResponse: Int
    let maximumWriteLengthWithoutResponse: Int
}

func capability(
    service: CBService,
    characteristic: CBCharacteristic,
    peripheral: CBPeripheral
) -> GATTCapability {
    GATTCapability(
        serviceID: service.uuid,
        characteristicID: characteristic.uuid,
        canRead: characteristic.properties.contains(.read),
        canWrite: characteristic.properties.contains(.write),
        canWriteWithoutResponse: characteristic.properties.contains(.writeWithoutResponse),
        canNotify: characteristic.properties.contains(.notify) ||
            characteristic.properties.contains(.indicate),
        maximumWriteLengthWithResponse: peripheral.maximumWriteValueLength(
            for: .withResponse
        ),
        maximumWriteLengthWithoutResponse: peripheral.maximumWriteValueLength(
            for: .withoutResponse
        )
    )
}
~~~

Use the actual property and write-type names from the selected SDK. The recipe is meant to make the checks visible, not to hide target availability.

## Recipe 7: define a versioned protocol adapter

Keep Data out of the view:

~~~swift
struct SensorState: Equatable {
    let temperature: Double
    let batteryPercent: Int
    let deviceRevision: Int
}

enum AccessoryCommand {
    case setTemperature(Double)
    case requestStatus
}

struct AccessoryProtocolAdapter {
    func decode(_ data: Data) throws -> SensorState {
        guard data.count >= 6 else {
            throw ProtocolError.invalidLength
        }
        guard data.first == 1 else {
            throw ProtocolError.unsupportedVersion
        }
        // Validate checksum/authentication before decoding fields.
        return SensorState(
            temperature: decodeTemperature(data),
            batteryPercent: Int(data[4]),
            deviceRevision: Int(data[5])
        )
    }

    func encode(
        _ command: AccessoryCommand,
        maximumLength: Int
    ) throws -> Data {
        let payload = encodeCommand(command)
        guard payload.count <= maximumLength else {
            throw ProtocolError.payloadTooLarge
        }
        return payload
    }
}
~~~

The byte layout is illustrative. Replace it with the accessory’s documented protocol, include bounds/checksum/authentication rules, and add fixtures for malformed or future-version packets.

## Recipe 8: verify protocol identity

A product identity handshake can be modeled as:

~~~swift
func verifyAccessory(
    using characteristic: CBCharacteristic,
    on peripheral: CBPeripheral
) async throws -> VerifiedAccessory {
    let challenge = makeChallenge()
    let response = try await performChallenge(
        challenge,
        characteristic: characteristic,
        peripheral: peripheral
    )
    let identity = try verifyResponse(response, for: challenge)
    return VerifiedAccessory(
        peripheralID: peripheral.identifier,
        productID: identity.productID,
        serial: identity.serial,
        protocolVersion: identity.protocolVersion,
        sessionRevision: nextSessionRevision()
    )
}
~~~

Do not invent a security scheme in the UI layer. Use the accessory’s documented protocol or an approved product security design. If no trust handshake exists, keep the UI honest about the weaker identity boundary.

## Recipe 9: read a characteristic

Read only after capability validation:

~~~swift
func readState(
    from peripheral: CBPeripheral,
    characteristic: CBCharacteristic
) throws {
    guard characteristic.properties.contains(.read) else {
        throw ProtocolError.notReadable
    }
    peripheral.readValue(for: characteristic)
}

func peripheral(
    _ peripheral: CBPeripheral,
    didUpdateValueFor characteristic: CBCharacteristic,
    error: Error?
) {
    guard error == nil, let data = characteristic.value else {
        publishReadFailure(error)
        return
    }
    do {
        let state = try adapter.decode(data)
        publishReportedState(state, source: .read)
    } catch {
        publishProtocolFailure(error)
    }
}
~~~

Record the source as read, notification, or restored cache. A successful decode does not prove the value describes the intended physical device until the session is verified.

## Recipe 10: write with response

Use response semantics for commands that require transport acknowledgment:

~~~swift
func sendWithResponse(
    _ command: AccessoryCommand,
    to peripheral: CBPeripheral,
    characteristic: CBCharacteristic
) throws {
    guard characteristic.properties.contains(.write) else {
        throw ProtocolError.notWritableWithResponse
    }
    let data = try adapter.encode(
        command,
        maximumLength: peripheral.maximumWriteValueLength(for: .withResponse)
    )
    markCommandPending(command)
    peripheral.writeValue(data, for: characteristic, type: .withResponse)
}

func peripheral(
    _ peripheral: CBPeripheral,
    didWriteValueFor characteristic: CBCharacteristic,
    error: Error?
) {
    if let error {
        publishCommandFailure(error)
    } else {
        publishTransportAcknowledged()
        // Wait for notification or read before claiming reported state.
    }
}
~~~

Transport acknowledgment and physical completion are different evidence. Keep both in the UI and acceptance record.

## Recipe 11: write without response

Use this mode only for a protocol that explicitly supports best-effort writes:

~~~swift
func sendWithoutResponse(
    _ data: Data,
    to peripheral: CBPeripheral,
    characteristic: CBCharacteristic
) throws {
    guard characteristic.properties.contains(.writeWithoutResponse) else {
        throw ProtocolError.notWritableWithoutResponse
    }
    guard data.count <= peripheral.maximumWriteValueLength(
        for: .withoutResponse
    ) else {
        throw ProtocolError.payloadTooLarge
    }
    guard peripheral.canSendWriteWithoutResponse else {
        throw ProtocolError.flowControl
    }
    peripheral.writeValue(data, for: characteristic, type: .withoutResponse)
    publishSentBestEffort()
}
~~~

There is no delegate completion for a write without response. Use sequence numbers, acknowledgments at the accessory protocol layer, or a later report when the product needs delivery evidence.

## Recipe 12: subscribe to notifications

Enable and disable subscriptions with session ownership:

~~~swift
func subscribe(
    _ characteristic: CBCharacteristic,
    on peripheral: CBPeripheral
) {
    guard characteristic.properties.contains(.notify) ||
        characteristic.properties.contains(.indicate) else {
        publishNotifiable(false)
        return
    }
    peripheral.setNotifyValue(true, for: characteristic)
}

func peripheral(
    _ peripheral: CBPeripheral,
    didUpdateNotificationStateFor characteristic: CBCharacteristic,
    error: Error?
) {
    if let error {
        publishSubscriptionFailure(error)
    } else {
        publishSubscriptionState(characteristic.isNotifying)
    }
}
~~~

On disconnect or session end, disable or release subscriptions according to the target lifecycle. After reconnect, re-discover and re-subscribe; do not assume in-memory characteristic objects remain valid.

## Recipe 13: publish a value-only SwiftUI snapshot

Use a UI model that has no Core Bluetooth object references:

~~~swift
struct AccessorySnapshot: Identifiable {
    let id: UUID
    let name: String
    let connection: ConnectionState
    let verification: VerificationState
    let temperature: Double?
    let batteryPercent: Int?
    let freshness: Freshness
    let pending: AccessoryCommand?
    let revision: Int
}

enum Freshness {
    case current(Date)
    case lastKnown(Date)
    case pending(Date)
    case unknown
}
~~~

Publish snapshots on the UI isolation boundary. Keep protocol state serialized in the coordinator or selected actor/queue.

## Recipe 14: SwiftUI device card

Render truthful state:

~~~swift
struct AccessoryCard: View {
    let snapshot: AccessorySnapshot
    let onConnect: () -> Void
    let onRefresh: () -> Void
    let onCommand: (AccessoryCommand) -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text(snapshot.name)
                    .font(.headline)
                Spacer()
                Text(connectionLabel)
                    .font(.caption)
            }

            Text(valueLabel)
                .font(.title2)

            Text(freshnessLabel)
                .font(.caption)
                .foregroundStyle(.secondary)

            HStack {
                Button(connectionActionLabel, action: onConnect)
                Button("Refresh", action: onRefresh)
            }
        }
        .padding()
        .accessibilityElement(children: .contain)
    }

    private var connectionLabel: String {
        snapshot.connection.description
    }

    private var connectionActionLabel: String {
        snapshot.connection.isReady ? "Send command" : "Connect"
    }

    private var valueLabel: String {
        snapshot.temperature.map { String(format: "%.1f°", $0) }
            ?? "No reported value"
    }

    private var freshnessLabel: String {
        snapshot.freshness.description
    }
}
~~~

Use a real Toggle, Slider, Picker, or Button after the typed protocol adapter maps the capability. Do not place raw packet data in Text.

## Recipe 15: add an optional Liquid Glass group

Keep the fallback identical in semantics:

~~~swift
struct DeviceStatusGroup<Content: View>: View {
    @ViewBuilder let content: () -> Content

    var body: some View {
        content()
            .padding()
            .background {
                RoundedRectangle(cornerRadius: 24)
                    .fill(.regularMaterial)
            }
    }
}
~~~

In the named iOS 26 target, evaluate the current Liquid Glass API and use GlassEffectContainer for related controls when it improves grouping. Keep the result readable without glass and outside system-owned permission/setup surfaces.

## Recipe 16: background restoration

Opt into restoration only when the product has a real session need:

~~~swift
let options: [String: Any] = [
    CBCentralManagerOptionRestoreIdentifierKey:
        "com.example.bluetooth.central"
]

func centralManager(
    _ central: CBCentralManager,
    willRestoreState dict: [String: Any]
) {
    // Rebuild the manager/session from restored peripherals, subscriptions,
    // and durable checkpoints. Revalidate identity before commands.
    restoreSession(from: dict)
}
~~~

The target must also configure the supported background mode and be tested through termination/relaunch on physical hardware. A restoration callback fixture without system relaunch evidence is incomplete.

## Recipe 17: typed AI command proposal

Keep the model away from bytes:

~~~swift
struct BluetoothCommandProposal {
    let accessoryID: UUID
    let sessionRevision: Int
    let serviceID: CBUUID
    let characteristicID: CBUUID
    let commandDescription: String
    let typedCommand: String
    let warnings: [String]
    let requiresConfirmation: Bool
}
~~~

The model may propose a known command name, but the protocol adapter must produce the payload. Supply only selected typed context:

~~~text
verified accessory product
session revision
known service and characteristic labels
typed current state
supported command names
range/unit/freshness
user request
~~~

Exclude credentials, pairing keys, raw advertisement data, and unrelated devices. Do not let the model choose a peripheral from fuzzy text.

## Recipe 18: apply proposal through the same command owner

Revalidate at the moment of apply:

~~~swift
func apply(
    _ proposal: BluetoothCommandProposal,
    against current: VerifiedAccessory,
    snapshot: AccessorySnapshot
) throws {
    guard proposal.accessoryID == current.peripheralID else {
        throw ProposalError.staleSession
    }
    guard proposal.sessionRevision == current.sessionRevision else {
        throw ProposalError.staleSession
    }
    guard snapshot.revision == proposal.sessionRevision else {
        throw ProposalError.changedState
    }

    let command = try commandFromKnownName(proposal.typedCommand)
    try validate(command, against: snapshot)
    requireUserConfirmation(proposal)
    try send(command)
}
~~~

The actual target may use an actor or command queue. The invariants are stable: same verified session, current revision, known command, validated payload, explicit confirmation, and later device report.

## Recipe 19: map failure and recovery

Use state-specific recovery:

~~~swift
enum BluetoothFailure {
    case permissionDenied
    case poweredOff
    case unsupported
    case candidateExpired
    case connectionFailed
    case missingService
    case missingCharacteristic
    case identityFailed
    case malformedPacket
    case writeRejected
    case staleProposal
}

func recovery(for failure: BluetoothFailure) -> String {
    switch failure {
    case .permissionDenied:
        return "Open Bluetooth settings"
    case .poweredOff:
        return "Turn on Bluetooth"
    case .unsupported:
        return "Use a supported device"
    case .candidateExpired, .connectionFailed:
        return "Scan again"
    case .missingService, .missingCharacteristic, .identityFailed:
        return "Check accessory compatibility"
    case .malformedPacket, .writeRejected:
        return "Review device protocol"
    case .staleProposal:
        return "Refresh accessory state"
    }
}
~~~

Do not offer “try again” for a physical command without rechecking the session and confirmation policy.

## Recipe 20: fixture matrix

Create deterministic fixtures:

~~~text
fixture/not-determined
fixture/denied
fixture/restricted
fixture/powered-off
fixture/resetting
fixture/unsupported
fixture/filtered-discovery
fixture/duplicate-advertisements
fixture/candidate-expired
fixture/same-name-different-ids
fixture/connection-failed
fixture/missing-service
fixture/missing-characteristic
fixture/identity-failure
fixture/valid-packet
fixture/short-packet
fixture/bad-checksum
fixture/unknown-version
fixture/read
fixture/write-with-response
fixture/write-without-response
fixture/notification
fixture/fragmented-notification
fixture/reconnect
fixture/restoration
fixture/ai-stale-session
fixture/ai-unknown-command
fixture/ai-safety-confirmation
~~~

Use a protocol fixture or accessory simulator for deterministic parsing, then use physical devices for radio, timing, battery, and side-effect evidence.

## Recipe 21: acceptance record

Store the evidence with the target:

~~~text
route: swiftui-core-bluetooth-nearby-accessory
target: <named Xcode target>
role: central / peripheral / both
sdk: <selected SDK>
device: <physical device or simulator>
accessory: <redacted physical identity>
authorization: allowed / denied / restricted
manager_state: poweredOn / poweredOff / resetting / unsupported
identity_handshake: pass / fail / not used
gatt_discovery: pass / fail
read_write_notify: pass / fail
background_restoration: pass / fail / not claimed
ai_validation: pass / fail / not used
accessibility: VoiceOver / Dynamic Type / keyboard / pointer
energy: <measurement or not run>
archive: <artifact path or not run>
release_gate: pass / blocked
known_limits: <protocol/accessory/target limitations>
~~~

Do not call the route complete if a claim has no corresponding evidence.

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
