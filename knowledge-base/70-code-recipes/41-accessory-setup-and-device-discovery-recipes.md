# AccessorySetupKit and DeviceDiscoveryUI recipes

These sketches are compile-oriented route boundaries, not a compiled accessory app. Verify every initializer, availability annotation, Info.plist key, entitlement, extension point, and transport API in the selected SDK.

The implementation order is:

    system picker -> selected accessory/endpoint -> transport -> protocol -> command

Do not start with a scan loop or a generic “connected” Boolean.

## Recipe 1: keep an app-owned device record

Persist only the identity and state needed by the product. Keep framework objects and raw advertisements at the adapter boundary.

~~~swift
struct DeviceRecord: Codable, Hashable, Sendable {
    enum Route: String, Codable, Sendable {
        case accessorySetup
        case deviceDiscovery
        case wifiAware
        case coreBluetooth
        case network
    }

    var id: UUID
    var displayName: String
    var route: Route
    var protocolVersion: Int?
    var capabilityNames: [String]
    var pairingState: String
    var connectionState: String
    var lastSeen: Date?
    var isStale: Bool
}

struct DeviceCommandProposal: Codable, Hashable, Sendable {
    var deviceID: UUID
    var commandName: String
    var humanDescription: String
    var payloadSummary: String
    var expiresAt: Date
}
~~~

Do not persist a Bluetooth identifier, SSID, endpoint address, or raw advertisement in this record unless the selected transport requires it and the privacy review approves it.

## Recipe 2: activate an AccessorySession

Use one session coordinator to serialize events and keep picker state separate from transport state.

~~~swift
import AccessorySetupKit
import Foundation

@MainActor
final class AccessorySetupCoordinator: NSObject {
    private(set) var session: ASAccessorySession?
    private(set) var selectedAccessory: ASAccessory?
    private(set) var state = "idle"

    func activate() {
        guard session == nil else { return }

        let newSession = ASAccessorySession()
        session = newSession
        state = "activating"

        newSession.activate(on: .main) { [weak self] event in
            guard let self else { return }
            self.handle(event)
        }
    }

    private func handle(_ event: ASAccessoryEvent) {
        switch event.eventType {
        case .activated:
            state = "ready"
            // session?.accessories can be reconciled here.
        case .accessoryAdded:
            selectedAccessory = event.accessory
            state = "selected"
        case .accessoryChanged:
            state = "accessory-changed"
        case .accessoryRemoved:
            state = "removed"
        case .pickerDidPresent:
            state = "picker-presented"
        case .pickerDidDismiss:
            if selectedAccessory != nil {
                state = "picker-dismissed"
            }
        case .pickerSetupPairing:
            state = "pairing"
        case .pickerSetupBridging:
            state = "bridging"
        case .pickerSetupFailed:
            state = "setup-failed"
        case .migrationComplete:
            state = "migration-complete"
        case .invalidated:
            state = "invalidated"
            session = nil
        default:
            state = "unknown-event"
        }
    }

    func invalidate() {
        session?.invalidate()
        session = nil
        selectedAccessory = nil
        state = "invalidated"
    }
}
~~~

Check the current Swift event names and actor annotations. The coordinator should not create the post-setup Bluetooth or Wi-Fi connection until the picker has dismissed and the accessory has been inspected.

## Recipe 3: declare a Bluetooth descriptor and picker item

The Info.plist declarations and descriptor must agree. Use a service/company/name/data combination that identifies the product narrowly.

~~~swift
import AccessorySetupKit
import CoreBluetooth
import UIKit

func makeDisplayItem() -> ASPickerDisplayItem {
    let descriptor = ASDiscoveryDescriptor()
    descriptor.bluetoothServiceUUID = CBUUID(
        string: "0000FFF0-0000-1000-8000-00805F9B34FB"
    )
    descriptor.bluetoothNameSubstring = "Bishop Device"
    descriptor.bluetoothRange = .immediate

    let image = UIImage(named: "AccessoryProduct")!
    return ASPickerDisplayItem(
        name: "Bishop Device",
        productImage: image,
        descriptor: descriptor
    )
}

func showPicker(
    using session: ASAccessorySession,
    items: [ASPickerDisplayItem]
) async throws {
    try await session.showPicker(for: items)
}
~~~

Verify whether the selected SDK requires the company identifier, service UUID, or additional Info.plist values for the actual accessory. Do not ship the placeholder UUID.

## Recipe 4: show a Wi-Fi accessory item

Use either an SSID or an SSID prefix, not both. This is a descriptor rule, not a general local-network browser.

~~~swift
import AccessorySetupKit
import UIKit

func makeWiFiDisplayItem() -> ASPickerDisplayItem {
    let descriptor = ASDiscoveryDescriptor()
    descriptor.ssidPrefix = "Bishop-Accessory-"

    return ASPickerDisplayItem(
        name: "Bishop Wi-Fi Accessory",
        productImage: UIImage(named: "WiFiAccessory")!,
        descriptor: descriptor
    )
}
~~~

Confirm the current Wi-Fi setup key, device advertising behavior, and post-selection transport. Seeing an SSID is not proof that the device is authentic or that it is the correct room/product.

## Recipe 5: custom-filter discovered accessories

Use this route for product/firmware/pairing-mode checks that the static descriptor cannot express.

~~~swift
import AccessorySetupKit

func enableAccessoryFiltering(
    on session: ASAccessorySession
) {
    let settings = ASPickerDisplaySettings.default
    settings.options.insert(.filterDiscoveryResults)
    settings.discoveryTimeout = .unbounded
    session.pickerDisplaySettings = settings
}

func handleDiscoveredAccessory(
    _ accessory: ASDiscoveredAccessory,
    session: ASAccessorySession
) async throws {
    guard accessoryIsSupported(accessory) else {
        return
    }

    let displayItem = ASDiscoveredDisplayItem(
        name: "Verified accessory",
        productImage: productImage(for: accessory),
        accessory: accessory
    )
    try await session.updatePicker(showing: [displayItem])
}
~~~

Bound the filter with an expiry and a maximum number of candidates. If no candidate passes, call the current finishPickerDiscovery API and show a retry explanation after picker dismissal.

## Recipe 6: migrate an existing peripheral

Migration is a one-time transition. Do not initialize Core Bluetooth before the migration completion event.

~~~swift
import AccessorySetupKit

func makeMigrationItem(
    previousPeripheralIdentifier: UUID
) -> ASMigrationDisplayItem {
    // Verify the current initializer labels and migration fields.
    ASMigrationDisplayItem(
        name: "Existing accessory",
        productImage: productImage,
        peripheralIdentifier: previousPeripheralIdentifier
    )
}

func handleMigrationComplete() {
    // Reconcile old app records with session.accessories.
    // Only now create or resume the Core Bluetooth central.
}
~~~

If a device is ambiguous, ask the person to choose rather than merging records automatically.

## Recipe 7: present a DevicePicker

DevicePicker is a system SwiftUI view. Provide a label and fallback and use the selected endpoint to begin the transport path.

~~~swift
import DeviceDiscoveryUI
import Network
import SwiftUI

struct PeerDevicePicker: View {
    let onEndpoint: (NWEndpoint) -> Void

    var body: some View {
        DevicePicker(
            .applicationService(name: "BishopControlService"),
            onSelect: { endpoint in
                onEndpoint(endpoint)
            },
            label: {
                Label("Choose a device", systemImage: "dot.radiowaves.left.and.right")
            },
            fallback: {
                ContentUnavailableView(
                    "Device pairing unavailable",
                    systemImage: "wifi.slash",
                    description: Text("This device cannot use the selected pairing route.")
                )
            },
            parameters: {
                .applicationService
            }
        )
    }
}
~~~

Confirm the current NWBrowser.Descriptor, NWParameters, and application-service declaration. Apple documents that the picker should be full screen and silently closes on cancellation; the app should not show an error for a normal cancel.

## Recipe 8: publisher side with DevicePairingView

For an app that makes itself discoverable, use the system publisher view and pair it with a listener.

~~~swift
import DeviceDiscoveryUI
import SwiftUI

struct MakeDeviceDiscoverable: View {
    var body: some View {
        DevicePairingView(.applicationService(name: "BishopControlService")) {
            Text("Make this device available")
        } fallback: {
            Text("Device pairing is not supported here.")
        }
    }
}
~~~

Verify the current provider/descriptor overload and platform availability. The publisher should stop being discoverable when the product task ends or when the user disables it.

## Recipe 9: validate Wi-Fi Aware support and services

Check host support and resolve services declared in Info.plist.

~~~swift
import WiFiAware

enum WiFiAwareRouteError: Error {
    case unsupported
    case missingService
}

func resolvePublisher() throws -> WAPublishableService {
    guard WACapabilities.supportedFeatures.contains(.wifiAware) else {
        throw WiFiAwareRouteError.unsupported
    }

    guard let service = WAPublishableService
        .allServices["_bishop-control._tcp"] else {
        throw WiFiAwareRouteError.missingService
    }

    return service
}

func resolveSubscriber() throws -> WASubscribableService {
    guard let service = WASubscribableService
        .allServices["_bishop-control._tcp"] else {
        throw WiFiAwareRouteError.missingService
    }
    return service
}
~~~

Use a unique, registered service name and verify the current WiFiAwareServices plist structure. Record WACapabilities maximum devices/services before creating a large fan-out design.

## Recipe 10: connect with a Network protocol

The selected endpoint is only the start. Add a bounded application protocol.

~~~swift
import Foundation
import Network

struct HelloMessage: Codable, Sendable {
    var protocolVersion: Int
    var deviceID: String
    var capabilities: [String]
    var nonce: String
}

final class PeerConnection {
    private var connection: NWConnection?

    func connect(to endpoint: NWEndpoint) {
        let parameters = NWParameters.applicationService
        let connection = NWConnection(to: endpoint, using: parameters)
        self.connection = connection

        connection.stateUpdateHandler = { state in
            switch state {
            case .ready:
                // Send and validate HelloMessage before enabling commands.
                break
            case .failed(let error):
                self.handleFailure(error)
            case .cancelled:
                self.handleDisconnected()
            default:
                break
            }
        }
        connection.start(queue: .main)
    }

    func cancel() {
        connection?.cancel()
        connection = nil
    }

    private func handleFailure(_ error: NWError) {}
    private func handleDisconnected() {}
}
~~~

Use length framing or NWProtocolFramer for messages. Authenticate the app protocol and validate every length/type/range. A secure system pairing flow does not replace this handshake.

## Recipe 11: a user-reviewed physical command

Keep AI and UI proposals separate from the actual command.

~~~swift
struct CommandReview: Sendable {
    var deviceName: String
    var command: String
    var consequence: String
    var isCurrentConnection: Bool
    var isApproved: Bool
}

func commit(_ review: CommandReview, using connection: PeerConnection) throws {
    guard review.isCurrentConnection else {
        throw CommandError.staleConnection
    }
    guard review.isApproved else {
        throw CommandError.userApprovalRequired
    }

    // Serialize only an allow-listed command with a sequence ID and expiry.
    // Wait for a matching response and read back the device state.
}

enum CommandError: Error {
    case staleConnection
    case userApprovalRequired
}
~~~

Never let a generated string become the wire payload. Convert a reviewed proposal into an allow-listed command type.

## Recipe 12: AI device proposal

Use a local typed proposal with explicit ambiguity and no raw discovery data.

~~~swift
struct AccessoryProposal: Codable, Sendable {
    var requestedTarget: String
    var requestedService: String
    var requestedAction: String
    var payloadSummary: String
    var ambiguityNotes: [String]
}

struct ProposalDecision: Sendable {
    var errors: [String]
    var warnings: [String]
    var requiresPersonSelection: Bool
}

func review(
    _ proposal: AccessoryProposal,
    selectedDeviceID: UUID?,
    supportedServices: Set<String>,
    allowListedActions: Set<String>
) -> ProposalDecision {
    var errors: [String] = []
    var warnings = proposal.ambiguityNotes

    if selectedDeviceID == nil {
        errors.append("Select a device in the system picker.")
    }
    if !supportedServices.contains(proposal.requestedService) {
        errors.append("The service is not available on the selected device.")
    }
    if !allowListedActions.contains(proposal.requestedAction) {
        errors.append("The action is not allow-listed.")
    }
    if proposal.payloadSummary.isEmpty {
        warnings.append("Review the payload before sending.")
    }

    return ProposalDecision(
        errors: errors,
        warnings: warnings,
        requiresPersonSelection: selectedDeviceID == nil
    )
}
~~~

Keep Bluetooth advertisement payloads, SSIDs, endpoint addresses, and secrets out of the model input unless a reviewed feature explicitly needs them.

## Recipe 13: deterministic state fixtures

Use fixtures to test app-owned UI and protocol reconciliation without pretending to test radio hardware.

~~~swift
struct AccessoryFixture: Sendable {
    var name: String
    var setupState: String
    var transportState: String
    var protocolState: String
    var lastSeenAge: TimeInterval?
}

enum AccessoryFixtures {
    static let nearby = AccessoryFixture(
        name: "Desk controller",
        setupState: "discovered",
        transportState: "not-connected",
        protocolState: "unknown",
        lastSeenAge: 1
    )

    static let connected = AccessoryFixture(
        name: "Desk controller",
        setupState: "authorized",
        transportState: "connected",
        protocolState: "ready",
        lastSeenAge: 0
    )

    static let stale = AccessoryFixture(
        name: "Desk controller",
        setupState: "authorized",
        transportState: "stale",
        protocolState: "needs-refresh",
        lastSeenAge: 45
    )
}
~~~

Test duplicate accessoryAdded, picker cancellation, invalidated session, migration completion, endpoint loss, protocol mismatch, repeated command, and physical-device removal.

## Verification sequence

1. Unit-test descriptor and protocol validation.
2. UI-test labels, fallback, selection, cancellation, and review.
3. Compile app/companion targets with Info.plist and entitlements.
4. Run AccessorySetupKit on a real accessory.
5. Run DeviceDiscoveryUI between two physical devices.
6. Run Wi-Fi Aware on supported hardware and service declarations.
7. Test disconnect/reconnect/migration/removal.
8. Test VoiceOver, Dynamic Type, reduced effects, and physical ergonomics.
9. Test performance, battery, thermal, and throughput for the workload.
10. Record signed/distribution evidence.

Use the [AccessorySetupKit and DeviceDiscoveryUI proof matrix](../60-verification/23-accessory-setup-and-device-discovery-proof-matrix.md).

## Sources

- [AccessorySetupKit](https://developer.apple.com/documentation/AccessorySetupKit)
- [Discovering and configuring accessories](https://developer.apple.com/documentation/accessorysetupkit/discovering-and-configuring-accessories)
- [ASAccessorySession](https://developer.apple.com/documentation/accessorysetupkit/asaccessorysession)
- [ASAccessoryEventType](https://developer.apple.com/documentation/accessorysetupkit/asaccessoryeventtype)
- [ASDiscoveryDescriptor](https://developer.apple.com/documentation/accessorysetupkit/asdiscoverydescriptor)
- [ASPickerDisplayItem](https://developer.apple.com/documentation/accessorysetupkit/aspickerdisplayitem)
- [ASDiscoveredDisplayItem](https://developer.apple.com/documentation/accessorysetupkit/asdiscovereddisplayitem)
- [DeviceDiscoveryUI](https://developer.apple.com/documentation/devicediscoveryui)
- [DevicePicker](https://developer.apple.com/documentation/devicediscoveryui/devicepicker)
- [DevicePairingView](https://developer.apple.com/documentation/devicediscoveryui/devicepairingview)
- [DDDevicePairingAccess](https://developer.apple.com/documentation/devicediscoveryui/dddevicepairingaccess)
- [Wi-Fi Aware](https://developer.apple.com/documentation/WiFiAware)
- [WACapabilities](https://developer.apple.com/documentation/wifiaware/wacapabilities)
- [WAPublishableService](https://developer.apple.com/documentation/wifiaware/wapublishableservice)
- [WASubscribableService](https://developer.apple.com/documentation/wifiaware/wasubscribableservice)
- [WAPublisherListener](https://developer.apple.com/documentation/wifiaware/wapublisherlistener)
- [WASubscriberBrowser](https://developer.apple.com/documentation/wifiaware/wasubscriberbrowser)
- [Network](https://developer.apple.com/documentation/network)
- [Core Bluetooth](https://developer.apple.com/documentation/corebluetooth)
- [Accessory Design Guidelines](https://developer.apple.com/accessories/)
