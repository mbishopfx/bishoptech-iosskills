# DeviceDiscoveryUI and Wi-Fi Aware code recipes

These are compile-oriented route sketches for a named iOS/iPadOS/watchOS/tvOS/Mac Catalyst target. They are not proof of radio support, system pairing, transport delivery, accessory behavior, or release readiness. Compile each recipe against the selected SDK and replace intentionally generic provider types before shipping.

## Recipe 1: target configuration

Configure the owning target with:

~~~text
Frameworks:
  DeviceDiscoveryUI
  WiFiAware
  Network
  SwiftUI or UIKit

Entitlements:
  com.apple.developer.wifi-aware:
    - Publish
    - Subscribe

Info.plist:
  WiFiAwareServices:
    _example-service._tcp:
      Publishable: {}
      Subscribable: {}
~~~

Request only the roles the product needs. The service name must use the exact fully qualified form declared by Apple’s Wi-Fi Aware documentation. Inspect the signed entitlements and merged Info.plist after building.

## Recipe 2: availability and route state

Keep system capability, target configuration, pairing state, and transport state separate.

~~~swift
import WiFiAware

enum PeerCapabilityState: Equatable, Sendable {
    case unavailable
    case ready
    case waitingForPairing
    case connecting
    case connected
    case failed(String)
}

struct PeerCapabilitySnapshot: Sendable {
    let state: PeerCapabilityState
    let featureCount: Int
    let deviceLimit: Int
}

func currentCapabilityState(
    hasDeclaredService: Bool,
    hasRequiredEntitlement: Bool,
    hasPairedDevice: Bool,
    isConnecting: Bool,
    isConnected: Bool
) -> PeerCapabilitySnapshot {
    let features = WACapabilities.supportedFeatures
    let state: PeerCapabilityState

    if features.isEmpty || !hasDeclaredService || !hasRequiredEntitlement {
        state = .unavailable
    } else if isConnected {
        state = .connected
    } else if isConnecting {
        state = .connecting
    } else if hasPairedDevice {
        state = .ready
    } else {
        state = .waitingForPairing
    }

    return PeerCapabilitySnapshot(
        state: state,
        featureCount: features.count,
        deviceLimit: WACapabilities.maximumConnectableDevices
    )
}
~~~

The target should use the exact feature check needed by its chosen provider. An empty feature set is useful as a broad unsupported signal; it is not a substitute for checking the specific provider and service.

## Recipe 3: SwiftUI publisher entry point

Use DevicePairingView as the user-initiated publisher surface. The service lookup must come from the target’s declared WiFiAwareServices entries.

~~~swift
import SwiftUI
import DeviceDiscoveryUI
import WiFiAware

struct PublisherPairingView: View {
    let service: WAPublishableService
    let access: DDDevicePairingAccess

    var body: some View {
        DevicePairingView(
            .wifiAware(.connecting(to: service, from: .userSpecifiedDevices)),
            access: access
        ) {
            Label("Make This Device Available", systemImage: "dot.radiowaves.left.and.right")
        } fallback: {
            VStack {
                Image(systemName: "wifi.slash")
                Text("Peer pairing is unavailable on this device.")
            }
        }
    }
}
~~~

Treat the button press as an invitation to enter system pairing UI. Do not begin a listener or expose private data merely because the view appeared. Start the service only after the product’s pairing and session policy permits it.

## Recipe 4: SwiftUI subscriber picker

Use DevicePicker to let the person choose a peer. Keep the fallback useful and keep the endpoint out of the domain model until it passes identity and policy validation.

~~~swift
import SwiftUI
import DeviceDiscoveryUI
import WiFiAware

struct SubscriberPickerView<Provider: BrowserProvider>: View {
    let provider: Provider
    let onEndpoint: (Provider.Endpoint) -> Void

    var body: some View {
        DevicePicker(
            provider,
            access: .default,
            onSelect: onEndpoint
        ) {
            Label("Choose a Nearby Device", systemImage: "iphone.and.arrow.forward")
        } fallback: {
            Label("Peer Pairing Unavailable", systemImage: "exclamationmark.triangle")
        }
    }
}
~~~

The concrete Provider and Endpoint spelling should be compiled against the selected SDK. Keep the generic endpoint type through the picker callback rather than erasing it. The recipe’s contract remains the same: select, validate, connect, acknowledge.

## Recipe 5: support-aware entry action

DevicePickerSupportedAction can be read from the SwiftUI environment to hide or disable an action when the requested provider is not supported.

~~~swift
import SwiftUI
import DeviceDiscoveryUI

struct SupportAwarePeerAction: View {
    @Environment(\.devicePickerSupports) private var devicePickerSupports
    @State private var showingPicker = false

    var body: some View {
        let supported = devicePickerSupports(
            .applicationService(name: "MyAppService"),
            parameters: { .applicationService }
        )

        Button("Choose a Device") {
            showingPicker = true
        }
        .disabled(!supported)
        .sheet(isPresented: $showingPicker) {
            Text("Present the DevicePicker as a full-screen modal system surface.")
        }
    }
}
~~~

Use the exact environment action and descriptor available in the selected SDK. A support result should control the entry point and fallback copy, not silently switch to an unreviewed discovery mechanism.

## Recipe 6: observe paired-device snapshots

Keep the paired-device projection in a lifecycle-owned model.

~~~swift
import WiFiAware

@MainActor
final class PairedDeviceModel: ObservableObject {
    @Published private(set) var devices: [WAPairedDevice] = []
    private var task: Task<Void, Never>?

    func startObserving() {
        task?.cancel()
        task = Task {
            do {
                for try await snapshot in WAPairedDevice.allDevices {
                    guard !Task.isCancelled else { return }
                    devices = Array(snapshot.values)
                }
            } catch {
                devices = []
            }
        }
    }

    func stopObserving() {
        task?.cancel()
        task = nil
    }
}
~~~

Store a stable app-owned peer record alongside the system projection. Do not persist secrets or assume a WAPairedDevice object is a durable business identity.

## Recipe 7: app-service fallback with Network

For an application-service route, use DevicePicker with a Network browser descriptor and create the receiving listener in the other app instance.

~~~swift
import Network

let descriptor = NWBrowser.Descriptor.applicationService(name: "MyAppService")
let parameters = NWParameters.applicationService

// DevicePicker(descriptor, parameters: { parameters }) { endpoint in
//     let connection = NWConnection(to: endpoint, using: parameters)
//     connection.start(queue: .main)
// }

let listener = try NWListener(using: parameters)
listener.newConnectionHandler = { connection in
    connection.start(queue: .main)
}
listener.start(queue: .main)
~~~

The listener must advertise the service in the selected target configuration, and the app must implement framing, trust, cancellation, and message validation. This route is not evidence of Wi-Fi Aware support.

## Recipe 8: Wi-Fi Aware NetworkListener

The current Wi-Fi Aware API uses NetworkListener to publish a service to selected paired devices.

~~~swift
import WiFiAware

func startListener(
    service: WAPublishableService
) async throws {
    let listener = try await NetworkListener(
        for: .wifiAware(.connecting(to: service, from: .allPairedDevices)),
        using: {
            TLS()
        }
    )
    .onStateUpdate { listener, state in
        // Persist only a redacted state category.
        _ = listener
        _ = state
    }

    try await listener.run { connection in
        // Read a bounded, typed request and write an acknowledgement.
        _ = connection
    }
}
~~~

The exact builder and protocol stack should be selected for the app’s payload semantics. Use a reliable stream for commands and file chunks unless measured realtime datagrams are the real requirement.

## Recipe 9: Wi-Fi Aware NetworkBrowser and connection

The subscriber browses a service on a set of paired devices and then creates a NetworkConnection.

~~~swift
import WiFiAware

func connect(
    service: WASubscribableService
) async throws {
    let browser = NetworkBrowser(
        for: .wifiAware(.connecting(to: .allPairedDevices, from: service))
    )
    .onStateUpdate { browser, state in
        _ = browser
        _ = state
    }

    let endpoint = try await browser.run { endpoints in
        guard let candidate = endpoints.first else {
            return .continue
        }
        return .finish(candidate)
    }

    let connection = NetworkConnection(
        to: endpoint,
        using: {
            TLS()
        }
    )
    .onStateUpdate { connection, state in
        _ = connection
        _ = state
    }

    // Wait for the ready state before sending an application event.
    _ = connection
}
~~~

For a real product, review candidates by stable app-owned identity and user intent rather than choosing the first result by default. Stop the browser when the connection attempt starts unless the product requires continued discovery.

## Recipe 10: bounded command and acknowledgement

Keep transport messages independent from the model or UI layer.

~~~swift
struct RemoteCommand: Codable, Sendable {
    let version: Int
    let operationID: UUID
    let targetDeviceID: String
    let expiresAt: Date
    let body: Body

    enum Body: Codable, Sendable {
        case requestSnapshot
        case applyValue(String)
        case putChunk(index: Int, bytes: Data)
    }
}

struct RemoteAcknowledgement: Codable, Sendable {
    let operationID: UUID
    let outcome: Outcome
    let message: String?

    enum Outcome: String, Codable, Sendable {
        case accepted
        case completed
        case rejected
        case failed
        case expired
    }
}
~~~

Validate version, targetDeviceID, expiry, payload size, command authorization, and operationID before applying a mutation. Persist enough state to reconcile an unknown result after a disconnect.

## Recipe 11: safe send policy

The send layer should not let an AI proposal or a stale UI row execute a remote side effect.

~~~swift
struct ApprovedPeerAction: Sendable {
    let deviceID: String
    let serviceID: String
    let operationID: UUID
    let command: RemoteCommand.Body
}

enum SendDecision: Sendable {
    case reject(String)
    case send(ApprovedPeerAction)
}

func authorize(
    deviceID: String,
    serviceID: String,
    currentPeerIDs: Set<String>,
    currentServiceIDs: Set<String>,
    userApproved: Bool,
    command: RemoteCommand.Body
) -> SendDecision {
    guard currentPeerIDs.contains(deviceID) else {
        return .reject("The selected peer is no longer paired.")
    }
    guard currentServiceIDs.contains(serviceID) else {
        return .reject("The selected service is not available.")
    }
    guard userApproved else {
        return .reject("The action requires confirmation.")
    }

    return .send(
        ApprovedPeerAction(
            deviceID: deviceID,
            serviceID: serviceID,
            operationID: UUID(),
            command: command
        )
    )
}
~~~

Re-read the current paired-device projection immediately before sending. The operation ID must be safe to retry only after the receiving domain can reconcile it.

## Recipe 12: AI proposal projection

On-device AI can help interpret a request, but the app should pass it a narrow projection and keep the resolver deterministic.

~~~swift
struct PeerFact: Sendable {
    let id: String
    let displayName: String
    let serviceIDs: Set<String>
    let paired: Bool
    let reachable: Bool
}

struct PeerProposal: Sendable {
    let requestedName: String
    let candidateID: String?
    let explanation: String
}

func resolve(
    proposal: PeerProposal,
    facts: [PeerFact]
) -> PeerFact? {
    let candidates = facts.filter {
        $0.paired && $0.displayName.localizedCaseInsensitiveCompare(proposal.requestedName) == .orderedSame
    }
    guard candidates.count == 1 else { return nil }
    return candidates.first
}
~~~

Do not match remote display names as if they were trusted commands. Ask for a user choice when there is ambiguity, and show the resolved ID/service/action before confirmation.

## Recipe 13: application-level state trace

Record state transitions without logging sensitive payloads.

~~~swift
enum PeerTraceState: String, Sendable {
    case unsupported
    case pairing
    case paired
    case browsing
    case candidate
    case connecting
    case ready
    case accepted
    case completed
    case failed
    case revoked
}

struct PeerTraceEvent: Sendable {
    let state: PeerTraceState
    let peerID: String?
    let operationID: UUID?
    let timestamp: Date
    let redactedReason: String?
}
~~~

The trace should let a tester distinguish “the person selected a peer,” “the transport became ready,” “the receiver accepted the command,” and “the domain operation completed.”

## Recipe 14: test cases

Write tests around the state and protocol boundaries:

~~~text
preflight:
  unsupported host -> actionable fallback
  missing entitlement -> internal configuration failure
  invalid service declaration -> target configuration failure
pairing:
  picker presented -> system-owned evidence
  cancel -> no error alarm, no mutation
  default access -> no unintended persistence
  permanent access -> forget/revoke path
projection:
  paired device added -> row appears
  device removed -> stale row disappears or is marked revoked
transport:
  no endpoint -> browsing continues or times out
  malformed endpoint/message -> rejected
  ready -> bounded request and acknowledgement
  disconnect before ack -> unknown result, safe reconciliation
ai:
  unique peer -> review and confirmation
  ambiguous name -> choose or reject
  unpaired name -> reject
release:
  distribution-signed two-device pairing and round trip
~~~

## Sources

- [DeviceDiscoveryUI](https://developer.apple.com/documentation/devicediscoveryui)
- [DevicePairingView](https://developer.apple.com/documentation/devicediscoveryui/devicepairingview)
- [DevicePicker](https://developer.apple.com/documentation/devicediscoveryui/devicepicker)
- [Device picker initializer](https://developer.apple.com/documentation/devicediscoveryui/devicepicker/init%28_%3Aaccess%3Aonselect%3Alabel%3Afallback%3Aparameters%3A%29)
- [Device picker support environment](https://developer.apple.com/documentation/swiftui/environmentvalues/devicepickersupports?changes=_3_4)
- [Wi-Fi Aware](https://developer.apple.com/documentation/WiFiAware?changes=_7)
- [Adopting Wi-Fi Aware](https://developer.apple.com/documentation/WiFiAware/Adopting-Wi-Fi-Aware)
- [Connecting devices for peer-to-peer Wi-Fi](https://developer.apple.com/documentation/wifiaware/connecting-paired-devices)
- [Building peer-to-peer apps](https://developer.apple.com/documentation/wifiaware/building-peer-to-peer-apps?changes=_4_5&language=objc)
- [WACapabilities](https://developer.apple.com/documentation/wifiaware/wacapabilities)
- [WAPairedDevice.allDevices](https://developer.apple.com/documentation/wifiaware/wapaireddevice/alldevices)
- [NetworkBrowser](https://developer.apple.com/documentation/Network/NetworkBrowser)
- [NetworkListener](https://developer.apple.com/documentation/network/networklistener)
- [NetworkConnection](https://developer.apple.com/documentation/network/networkconnection?changes=__2)
- [Network](https://developer.apple.com/documentation/network)
- [Wi-Fi Aware entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.wifi-aware?changes=__1)
- [WiFiAwareServices](https://developer.apple.com/documentation/bundleresources/information-property-list/wifiawareservices?changes=__1_9)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Swift concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
