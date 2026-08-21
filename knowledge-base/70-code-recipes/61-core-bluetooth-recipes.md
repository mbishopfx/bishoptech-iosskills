# Core Bluetooth recipes

These are compile-oriented route sketches for Core Bluetooth central/peripheral roles, GATT discovery, notifications, write backpressure, state restoration, bounded protocol commands, and a native status surface. They are not compiled in this documentation-only workspace and do not prove permission, physical radio behavior, accessory compatibility, background execution, restoration, iOS 26 Live Activity behavior, or release eligibility.

Before copying:

1. Confirm that raw Bluetooth transport is the right route instead of AccessorySetupKit, HomeKit, Nearby Interaction, Network, or WatchConnectivity.
2. Add and verify NSBluetoothAlwaysUsageDescription for the target.
3. Add bluetooth-central or bluetooth-peripheral background mode only when the user outcome requires it.
4. Use a real service/characteristic register and a real firmware protocol; the UUIDs below are fixtures.
5. Serialize manager/delegate state and keep Core Bluetooth objects behind an adapter.
6. Use a physical two-device or accessory test for every radio, GATT, background, and physical-result claim.

## Recipe 1: Keep the protocol independent from Core Bluetooth

Use value types for commands and results so the domain and AI layers never depend on CBPeripheral or CBCharacteristic:

~~~swift
import Foundation

struct BLECommand: Sendable, Equatable {
    let requestID: UUID
    let deviceID: UUID
    let operation: Operation

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

enum BLEFixtureUUID {
    static let service = CBUUID(string: "8C1A0001-0000-4000-8000-000000000001")
    static let command = CBUUID(string: "8C1A0001-0000-4000-8000-000000000002")
    static let event = CBUUID(string: "8C1A0001-0000-4000-8000-000000000003")
}
~~~

Replace fixture UUIDs with the accessory’s documented register. Do not use a device name or RSSI as the protocol identity.

## Recipe 2: Model transport state explicitly

Make the state reducer testable without creating a radio manager:

~~~swift
enum BLETransportState: Equatable, Sendable {
    case idle
    case waitingForBluetooth
    case scanning
    case candidateFound(name: String?)
    case connecting
    case discovering
    case ready
    case stale(reason: String)
    case disconnected(reason: String?)
    case restoring
    case failed(code: String)
}

enum BLETransportEvent: Sendable {
    case managerState(CBManagerState)
    case discovered(name: String?)
    case connected
    case servicesReady
    case disconnected(String?)
    case restored
    case protocolMismatch
    case failure(String)
}
~~~

Keep system radio state, connection state, protocol compatibility, trust, and domain result as separate state fields in a production reducer. A ready transport is not a completed physical command.

## Recipe 3: Create a central manager and scan narrowly

The manager must be powered on before scanning. This sketch uses a stable restoration identifier and a serial queue for delegate callbacks:

~~~swift
import CoreBluetooth
import Foundation

final class BLECentralAdapter: NSObject, CBCentralManagerDelegate {
    private let serviceUUID = BLEFixtureUUID.service
    private var central: CBCentralManager!
    private var selectedPeripheral: CBPeripheral?

    override init() {
        super.init()
        central = CBCentralManager(
            delegate: self,
            queue: DispatchQueue(label: "com.example.ble.central"),
            options: [
                CBCentralManagerOptionRestoreIdentifierKey:
                    "com.example.ble.central.v1"
            ]
        )
    }

    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        guard central.state == .poweredOn else {
            // Map poweredOff, unauthorized, unsupported, resetting, and unknown.
            return
        }

        central.scanForPeripherals(
            withServices: [serviceUUID],
            options: nil
        )
    }

    func stopScanning() {
        central.stopScan()
    }

    func centralManager(
        _ central: CBCentralManager,
        didDiscover peripheral: CBPeripheral,
        advertisementData: [String: Any],
        rssi RSSI: NSNumber
    ) {
        // Keep a bounded candidate projection and ask the person to select it.
        selectedPeripheral = peripheral
    }
}
~~~

The delegate queue and MainActor UI boundary need a deliberate handoff in the real target. Never update SwiftUI state from an arbitrary delegate queue without an isolation plan.

## Recipe 4: Connect and discover the GATT graph

After person selection, stop scanning, connect, assign the peripheral delegate, and discover only the required service:

~~~swift
extension BLECentralAdapter: CBPeripheralDelegate {
    func connectSelected() {
        guard let selectedPeripheral else { return }
        central.stopScan()
        central.connect(selectedPeripheral, options: nil)
    }

    func centralManager(
        _ central: CBCentralManager,
        didConnect peripheral: CBPeripheral
    ) {
        peripheral.delegate = self
        peripheral.discoverServices([BLEFixtureUUID.service])
    }

    func peripheral(
        _ peripheral: CBPeripheral,
        didDiscoverServices error: Error?
    ) {
        guard error == nil,
              let service = peripheral.services?.first(where: {
                  $0.uuid == BLEFixtureUUID.service
              }) else {
            return
        }

        peripheral.discoverCharacteristics(
            [BLEFixtureUUID.command, BLEFixtureUUID.event],
            for: service
        )
    }

    func peripheral(
        _ peripheral: CBPeripheral,
        didDiscoverCharacteristicsFor service: CBService,
        error: Error?
    ) {
        guard error == nil else { return }
        // Store validated characteristic references in the adapter.
    }
}
~~~

Do not mark the device ready merely because didConnectPeripheral fired. Compatibility and trust are later states.

## Recipe 5: Subscribe and handle incoming frames

Subscribe only after the event characteristic is validated. Decode on the adapter queue, then publish a typed result to the domain layer:

~~~swift
final class BLEEventDecoder {
    func decode(
        data: Data,
        requestID: UUID,
        deviceID: UUID
    ) throws -> BLEResult {
        // Validate version, length, checksum, operation, and value ranges.
        return BLEResult(
            requestID: requestID,
            deviceID: deviceID,
            outcome: .accepted,
            receivedAt: Date()
        )
    }
}

extension BLECentralAdapter {
    func subscribe(to characteristic: CBCharacteristic) {
        guard characteristic.properties.contains(.notify) else { return }
        selectedPeripheral?.setNotifyValue(true, for: characteristic)
    }

    func peripheral(
        _ peripheral: CBPeripheral,
        didUpdateValueFor characteristic: CBCharacteristic,
        error: Error?
    ) {
        guard error == nil, let data = characteristic.value else {
            // Surface a typed transport failure; do not hide it in logs.
            return
        }

        // Pass data to the codec and reconcile the result with the request ID.
    }
}
~~~

Incoming bytes are not domain truth until framing, integrity, sequence, protocol version, and device authorization checks pass.

## Recipe 6: Write with a response and bound payloads

Use withResponse for commands whose acceptance must be observed at the transport layer. The device must still return a domain-level result:

~~~swift
extension BLECentralAdapter {
    func writeCommand(
        _ payload: Data,
        to characteristic: CBCharacteristic
    ) -> Bool {
        guard let peripheral = selectedPeripheral,
              characteristic.properties.contains(.write)
        else {
            return false
        }

        let maxLength = peripheral.maximumWriteValueLength(
            for: .withResponse
        )
        guard payload.count <= maxLength else {
            return false
        }

        peripheral.writeValue(
            payload,
            for: characteristic,
            type: .withResponse
        )
        return true
    }

    func peripheral(
        _ peripheral: CBPeripheral,
        didWriteValueFor characteristic: CBCharacteristic,
        error: Error?
    ) {
        // Transport acknowledgement only. Await the app-level result.
    }
}
~~~

For larger messages, define an application framing/chunking protocol. Do not assume a single characteristic write is a complete domain command.

## Recipe 7: Handle write-without-response backpressure

Use write-without-response only for data that can tolerate loss or has an explicit application-level recovery path:

~~~swift
final class BLEWriteQueue {
    private var pending = [Data]()
    private var canWriteWithoutResponse = false

    func enqueue(_ data: Data) {
        pending.append(data)
    }

    func updateReadiness(_ ready: Bool) {
        canWriteWithoutResponse = ready
    }

    func nextChunk() -> Data? {
        guard canWriteWithoutResponse, !pending.isEmpty else {
            return nil
        }
        return pending.removeFirst()
    }

    func restore(_ data: Data) {
        pending.insert(data, at: 0)
    }
}

extension BLECentralAdapter {
    func peripheralIsReady(
        toSendWriteWithoutResponse peripheral: CBPeripheral
    ) {
        // Drain a bounded queue after Core Bluetooth signals readiness.
    }
}
~~~

Record whether the application queue is empty, paused, canceled, or failed. An empty queue does not prove that the peer consumed the data.

## Recipe 8: Opt into central state restoration

Use a stable restoration identifier on every manager creation and reconcile restored objects:

~~~swift
extension BLECentralAdapter {
    func centralManager(
        _ central: CBCentralManager,
        willRestoreState dict: [String: Any]
    ) {
        let peripherals =
            dict[CBCentralManagerRestoredStatePeripheralsKey]
                as? [CBPeripheral] ?? []

        let services =
            dict[CBCentralManagerRestoredStateScanServicesKey]
                as? [CBUUID] ?? []

        for peripheral in peripherals {
            peripheral.delegate = self
            // Match against an app-owned selected-device record.
        }

        // Reconcile services with the current protocol register.
        _ = services
    }
}
~~~

Restoration is a system-provided partial snapshot. Reconnect or reselect when the selected device, firmware, authorization, or protocol no longer matches.

## Recipe 9: Publish a local peripheral

Use the peripheral role only when the app must expose a service:

~~~swift
final class BLEPeripheralAdapter: NSObject, CBPeripheralManagerDelegate {
    private var manager: CBPeripheralManager!
    private var eventCharacteristic: CBMutableCharacteristic?

    override init() {
        super.init()
        manager = CBPeripheralManager(
            delegate: self,
            queue: DispatchQueue(label: "com.example.ble.peripheral"),
            options: [
                CBPeripheralManagerOptionRestoreIdentifierKey:
                    "com.example.ble.peripheral.v1"
            ]
        )
    }

    func peripheralManagerDidUpdateState(
        _ peripheral: CBPeripheralManager
    ) {
        guard peripheral.state == .poweredOn else { return }

        let event = CBMutableCharacteristic(
            type: BLEFixtureUUID.event,
            properties: [.notify, .read],
            value: nil,
            permissions: [.readable]
        )
        let service = CBMutableService(
            type: BLEFixtureUUID.service,
            primary: true
        )
        service.characteristics = [event]
        eventCharacteristic = event
        peripheral.add(service)
    }

    func startAdvertising() {
        manager.startAdvertising([
            CBAdvertisementDataServiceUUIDsKey: [BLEFixtureUUID.service]
        ])
    }
}
~~~

Handle service-add and advertising errors before showing the peripheral as ready. Advertising is not a secure pairing result.

## Recipe 10: Apply peripheral backpressure

The updateValue result determines whether the peripheral can accept more notification data:

~~~swift
extension BLEPeripheralAdapter {
    func send(_ data: Data, to centrals: [CBCentral]? = nil) {
        guard let eventCharacteristic else { return }

        let accepted = manager.updateValue(
            data,
            for: eventCharacteristic,
            onSubscribedCentrals: centrals
        )

        if !accepted {
            // Store a bounded pending chunk and wait for readiness.
        }
    }

    func peripheralManagerIsReady(
        toUpdateSubscribers peripheral: CBPeripheralManager
    ) {
        // Drain the bounded notification queue.
    }
}
~~~

If a central sends a read or write request, validate the characteristic, offset, payload, and protocol before responding with the appropriate ATT result.

## Recipe 11: Use a typed AI command proposal

Keep AI behind a deterministic validator:

~~~swift
struct DeviceCommandProposal: Sendable, Equatable {
    let deviceID: UUID
    let operation: BLECommand.Operation
    let explanation: String
    let requiresConfirmation: Bool
}

enum BLECommandValidationError: Error {
    case wrongDevice
    case notReady
    case unsupportedOperation
    case invalidRange
    case staleRequest
}

func validate(
    _ proposal: DeviceCommandProposal,
    selectedDeviceID: UUID,
    transport: BLETransportState
) throws -> BLECommand {
    guard proposal.deviceID == selectedDeviceID else {
        throw BLECommandValidationError.wrongDevice
    }
    guard transport == .ready else {
        throw BLECommandValidationError.notReady
    }

    return BLECommand(
        requestID: UUID(),
        deviceID: proposal.deviceID,
        operation: proposal.operation
    )
}
~~~

The production validator must also check protocol version, ranges, user confirmation, idempotency, account authorization, and characteristic mapping. Model output, a successful write, and physical completion are separate evidence states.

## Recipe 12: Keep the SwiftUI surface native and honest

The app-owned UI should show status and confirmation; it should not imitate system pairing UI:

~~~swift
import SwiftUI

struct BLEStatusView: View {
    let state: BLETransportState
    let deviceName: String?
    let reconnect: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label(
                deviceName ?? "Bluetooth device",
                systemImage: "dot.radiowaves.left.and.right"
            )
            .font(.headline)

            Text(statusText)
                .foregroundStyle(.secondary)

            if case .disconnected = state {
                Button("Reconnect", action: reconnect)
                    .buttonStyle(.borderedProminent)
            }
        }
        .padding()
        .glassEffect(.regular, in: .rect(cornerRadius: 24))
    }

    private var statusText: String {
        switch state {
        case .ready:
            return "Verified and ready"
        case .scanning:
            return "Looking for the selected device"
        case .connecting:
            return "Connecting"
        case .discovering:
            return "Checking compatibility"
        case .stale(let reason):
            return "Stale: \(reason)"
        case .disconnected(let reason):
            return reason ?? "Disconnected"
        default:
            return "Bluetooth status needs attention"
        }
    }
}
~~~

Verify the exact Liquid Glass API in the final SDK and test the surface with reduced transparency, Dynamic Type, VoiceOver, duplicate names, and no device.

## Recipe 13: Record proof instead of a binary connected flag

Use an app-owned evidence model:

~~~swift
struct BLEEvidence: Sendable, Equatable {
    let target: String
    let deviceModel: String
    let firmware: String
    let serviceUUIDs: [String]
    let protocolVersion: Int
    let transportAcknowledged: Bool
    let domainResultObserved: Bool
    let backgroundTested: Bool
    let restorationTested: Bool
    let aiExternalUploadBlocked: Bool
}
~~~

The model should never allow domain completion when domainResultObserved is false. Use unknown/stale states rather than guessing from a callback.

## Sources

- [Core Bluetooth](https://developer.apple.com/documentation/corebluetooth)
- [CBCentralManager](https://developer.apple.com/documentation/corebluetooth/cbcentralmanager)
- [CBCentralManagerDelegate](https://developer.apple.com/documentation/corebluetooth/cbcentralmanagerdelegate)
- [CBPeripheral](https://developer.apple.com/documentation/corebluetooth/cbperipheral)
- [CBPeripheralDelegate](https://developer.apple.com/documentation/corebluetooth/cbperipheraldelegate)
- [CBPeripheralManager](https://developer.apple.com/documentation/corebluetooth/cbperipheralmanager)
- [CBPeripheralManagerDelegate](https://developer.apple.com/documentation/corebluetooth/cbperipheralmanagerdelegate)
- [CBManager](https://developer.apple.com/documentation/corebluetooth/cbmanager)
- [CBManagerAuthorization](https://developer.apple.com/documentation/corebluetooth/cbmanagerauthorization)
- [Transferring data between Bluetooth Low Energy devices](https://developer.apple.com/documentation/corebluetooth/transferring-data-between-bluetooth-low-energy-devices)
- [Central manager state restoration options](https://developer.apple.com/documentation/corebluetooth/central-manager-state-restoration-options)
- [Peripheral manager state restoration options](https://developer.apple.com/documentation/corebluetooth/peripheral-manager-state-restoration-options)
- [Core Bluetooth background processing for iOS apps](https://developer.apple.com/library/archive/documentation/NetworkingInternetWeb/Conceptual/CoreBluetooth_concepts/CoreBluetoothBackgroundProcessingForIOSApps/PerformingTasksWhileYourAppIsInTheBackground.html)
- [Using Core Bluetooth Classic](https://developer.apple.com/documentation/corebluetooth/using-core-bluetooth-classic)
- [NSBluetoothAlwaysUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsbluetoothalwaysusagedescription)
- [UIBackgroundModes](https://developer.apple.com/documentation/bundleresources/information-property-list/uibackgroundmodes)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
