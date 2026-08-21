# DeviceDiscoveryUI and Wi-Fi Aware capability route

Use this route when an app needs a person-mediated connection to another nearby app, an accessory, or a Wi-Fi Aware device. Keep the route explicit:

~~~text
product outcome
-> pairing owner
-> target capability and service declaration
-> support check
-> system pairing UI
-> paired-device projection
-> Network listener/browser/connection
-> typed protocol and domain acknowledgement
~~~

## Route selector

| Need | Select | Do not substitute |
| --- | --- | --- |
| Pair two app instances or a peer device | DeviceDiscoveryUI | A custom device list with unverified local-network discovery |
| Set up a personal accessory | AccessorySetupKit | Treating a transport connection as accessory ownership |
| Connect to paired Wi-Fi Aware peers | Wi-Fi Aware plus Network framework | Assuming an endpoint remains valid after pairing |
| Connect on a normal local network | Network framework | Requesting Wi-Fi Aware only because it sounds faster |
| Measure distance or direction | Nearby Interaction | Using transport reachability as proximity proof |
| Stream media to a receiver in the system picker | DeviceDiscoveryExtension plus AVRoutePickerView | Embedding a custom receiver picker in the app |

## Ownership graph

~~~text
SwiftUI app shell
  -> DevicePairingView or DevicePicker
  -> DeviceDiscoveryUI system trust/access
  -> WAPairedDevice projection
  -> NetworkListener / NetworkBrowser / NetworkConnection
  -> typed application protocol
  -> local domain store and user-visible result
~~~

The app owns the shell, protocol, local data, and action policy. DeviceDiscoveryUI owns the system discovery/pairing presentation. Wi-Fi Aware and Network own the transport implementation. None of those layers alone owns the business result.

## Target setup

Before writing the feature:

1. Pick the owning app target and any extension target.
2. Confirm the selected deployment target and SDK contain DeviceDiscoveryUI, Wi-Fi Aware, and the Network API variant used by the recipe.
3. Add the Wi-Fi Aware capability only if the feature actually uses it.
4. Set com.apple.developer.wifi-aware to Publish, Subscribe, or both.
5. Add valid WiFiAwareServices entries for every service role.
6. Inspect the signed entitlements and merged Info.plist.
7. Record supported device/OS rows and the intended two-device test pair.

The Wi-Fi Aware capability is not a replacement for the service declaration. A signed entitlement without a matching service, or a service declaration without the corresponding entitlement, is an incomplete route.

## Preflight support model

Create a small, testable support result. It should explain why a route is unavailable rather than returning a single false value.

~~~swift
import DeviceDiscoveryUI
import WiFiAware

enum PeerRouteAvailability: Equatable, Sendable {
    case supported
    case unsupportedHost
    case missingPublishCapability
    case missingSubscribeCapability
    case serviceNotDeclared
}

struct PeerRoutePreflight: Sendable {
    let availability: PeerRouteAvailability
    let supportsWiFiAware: Bool
    let maximumDevices: Int
    let maximumPublishers: Int
    let maximumSubscribers: Int
}

func inspectPeerRoute(
    needsPublisher: Bool,
    needsSubscriber: Bool,
    hasPublishCapability: Bool,
    hasSubscribeCapability: Bool,
    hasDeclaredService: Bool
) -> PeerRoutePreflight {
    let features = WACapabilities.supportedFeatures
    let wifiAwareSupported = !features.isEmpty

    let availability: PeerRouteAvailability
    if !wifiAwareSupported {
        availability = .unsupportedHost
    } else if needsPublisher && !hasPublishCapability {
        availability = .missingPublishCapability
    } else if needsSubscriber && !hasSubscribeCapability {
        availability = .missingSubscribeCapability
    } else if !hasDeclaredService {
        availability = .serviceNotDeclared
    } else {
        availability = .supported
    }

    return PeerRoutePreflight(
        availability: availability,
        supportsWiFiAware: wifiAwareSupported,
        maximumDevices: WACapabilities.maximumConnectableDevices,
        maximumPublishers: WACapabilities.maximumPublishableServices,
        maximumSubscribers: WACapabilities.maximumSubscribableServices
    )
}
~~~

This is a route sketch. The final app should select the exact WACapabilities feature it needs and use the SDK’s current capability names. Do not infer support from an import, a preview, or an iPhone model string.

## SwiftUI pairing views

### Publisher

~~~swift
import SwiftUI
import DeviceDiscoveryUI
import WiFiAware

struct MakePeerAvailableButton: View {
    let service: WAPublishableService
    let access: DDDevicePairingAccess

    var body: some View {
        DevicePairingView(
            .wifiAware(.connecting(to: service, from: .userSpecifiedDevices)),
            access: access
        ) {
            Label("Make This Device Available", systemImage: "dot.radiowaves.left.and.right")
        } fallback: {
            Label("Peer Pairing Unavailable", systemImage: "exclamationmark.triangle")
        }
    }
}
~~~

The exact Provider and selection expression should be compiled against the chosen SDK. The important product boundary is stable: the user presses a semantic control, the system owns the pairing interface, and the app handles the post-pairing state.

### Subscriber

~~~swift
import SwiftUI
import DeviceDiscoveryUI
import WiFiAware

struct ChoosePeerButton: View {
    let service: WASubscribableService
    let onEndpoint: (Any) -> Void

    var body: some View {
        DevicePicker(
            .wifiAware(.connecting(to: .userSpecifiedDevices, from: service)),
            access: .default,
            onSelect: { endpoint in
                onEndpoint(endpoint)
            }
        ) {
            Label("Choose a Nearby Device", systemImage: "iphone.and.arrow.forward")
        } fallback: {
            Label("No Supported Pairing Route", systemImage: "wifi.slash")
        }
    }
}
~~~

Do not ship Any as the endpoint type. Replace it with the concrete Provider.Endpoint produced by the selected SDK route. The placeholder keeps the recipe focused on ownership and should be treated as intentionally non-compiling until the target chooses its provider.

## Observe the paired-device projection

The system exposes WAPairedDevice.allDevices as an asynchronous sequence of snapshots. Keep observation in a lifecycle-owned task and cancel it when the feature or model goes away.

~~~swift
import WiFiAware

@MainActor
final class PairedDeviceStore: ObservableObject {
    @Published private(set) var devices: [WAPairedDevice] = []
    private var observationTask: Task<Void, Never>?

    func start() {
        observationTask?.cancel()
        observationTask = Task {
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

    func stop() {
        observationTask?.cancel()
        observationTask = nil
    }
}
~~~

Use the current observation model in the target. If a newer Observation-based model replaces ObservableObject for the selected deployment, adapt the storage layer without changing the pairing/transport contract. Do not present a cached device row as current reachability.

## Publisher transport

The current Wi-Fi Aware route uses NetworkListener with a Wi-Fi Aware provider. A publisher selects a service and a paired-device set, chooses an application protocol, observes state, and handles incoming connections.

~~~swift
import Network
import WiFiAware

struct PeerEvent: Codable, Sendable {
    let version: Int
    let operationID: String
    let kind: String
    let payload: Data
}

func runPublisher(service: WAPublishableService) async throws {
    let listener = try await NetworkListener(
        for: .wifiAware(.connecting(to: service, from: .allPairedDevices)),
        using: {
            TLS()
        }
    )
    .onStateUpdate { listener, state in
        // Persist a redacted state category for diagnostics.
        _ = listener
        _ = state
    }

    try await listener.run { connection in
        // Keep the connection until the application protocol closes.
        // Decode bounded PeerEvent values and acknowledge idempotently.
        _ = connection
    }
}
~~~

Use a typed Network protocol builder for a real app. TLS, framing, maximum message size, decode limits, and cancellation must be explicit. The listener lifetime is part of the feature; constructing it in a local function and allowing it to deallocate is not a server.

## Subscriber transport

The subscriber browses only the selected service and paired-device set, reviews candidates, then connects to one endpoint.

~~~swift
import WiFiAware

func connectToPeer(service: WASubscribableService) async throws {
    let browser = NetworkBrowser(
        for: .wifiAware(.connecting(to: .allPairedDevices, from: service))
    )
    .onStateUpdate { browser, state in
        _ = browser
        _ = state
    }

    let endpoint = try await browser.run { endpoints in
        let approved = endpoints.first
        if let approved {
            return .finish(approved)
        }
        return .continue
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

    // Wait for the target SDK’s ready state, then send one bounded event.
    _ = connection
}
~~~

Selecting the first endpoint is only acceptable when the product has already constrained the allowed devices and the UX explains the rule. Otherwise present the candidates to the person or use a deterministic app-owned identity resolver.

## App-service fallback

For app-to-app scenarios that use Network application services rather than Wi-Fi Aware, DevicePicker can be initialized with NWBrowser.Descriptor.applicationService and NWParameters.applicationService. The selected NWEndpoint still needs a NetworkConnection or NWConnection, protocol framing, and a listener on the receiving side.

~~~swift
import Network

let descriptor = NWBrowser.Descriptor.applicationService(name: "MyAppService")
let parameters = NWParameters.applicationService
// Pass descriptor and parameters to DevicePicker or DDDevicePickerViewController.
// Create an NWListener on the receiving target and an NWConnection on the sender.
~~~

This route is not the same as ordinary Bonjour browsing. DeviceDiscoveryUI provides the system pairing surface and encrypted application-service connection setup described by Apple. Inspect the selected platform’s supported service and privacy requirements.

## Typed message boundary

Keep the wire protocol independent of SwiftUI and model output.

~~~swift
struct PeerCommand: Codable, Sendable {
    let protocolVersion: Int
    let operationID: UUID
    let targetDeviceID: String
    let command: Command
    let expiresAt: Date

    enum Command: Codable, Sendable {
        case putChunk(index: Int, bytes: Data)
        case requestSnapshot
        case applyApprovedValue(String)
    }
}

struct PeerAck: Codable, Sendable {
    let operationID: UUID
    let outcome: Outcome
    let detail: String?

    enum Outcome: String, Codable, Sendable {
        case accepted
        case completed
        case rejected
        case failed
        case expired
    }
}
~~~

Validation rules:

- reject a protocol version the target does not understand;
- compare targetDeviceID with the current app-owned peer record;
- reject expired operations;
- enforce payload and collection limits before decoding into domain state;
- make operations idempotent by operationID;
- distinguish accepted from completed;
- do not retry an unknown mutation without reconciliation;
- redact payloads and endpoints in logs.

## AI-assisted peer selection

Represent AI output as a proposal, not an endpoint:

~~~swift
struct PeerActionProposal: Sendable {
    let naturalLanguageTarget: String
    let resolvedDeviceID: String?
    let resolvedServiceID: String?
    let reason: String
    let requiresConfirmation: Bool
}
~~~

Resolution should be deterministic:

1. Match the natural-language target against current app-owned peer records.
2. Require a unique stable ID and currently declared service.
3. Check the paired-device projection and support state.
4. Show the resolved device and action scope.
5. Ask for confirmation.
6. Re-read the peer projection before sending.
7. Create an idempotency key and send a typed command.

The model must not select an arbitrary endpoint, invent a pairing relationship, or bypass the system picker. If no unique peer matches, the correct result is an explanation and a choice.

## Fallbacks

| Failure state | Fallback |
| --- | --- |
| Wi-Fi Aware unsupported | Use an approved local-network, Bluetooth, External Accessory, SharePlay, or cloud route if the product permits it |
| DeviceDiscoveryUI unavailable | Explain that pairing requires a supported device or OS; do not silently browse all local devices |
| Service declaration missing | Hide the feature in production and surface a developer diagnostic in internal builds |
| No paired devices | Offer pairing and keep local work available |
| Peer offline | Queue only an idempotent operation if the product explicitly supports it; otherwise save locally |
| Transport failure | Reconcile before retrying a mutation |
| Background runtime unavailable | Show pending state and wait for a platform-approved runtime |
| Model unavailable | Use deterministic peer filters and explicit user choice |

## Verification handoff

Before calling the route ready for a real app, capture:

- target SDK and deployment target;
- capability and signed entitlement inspection;
- merged WiFiAwareServices property list;
- WACapabilities and device model;
- system pairing UI on two supported physical devices;
- WAPairedDevice.allDevices updates after pairing and removal;
- publisher/browse/connection state transitions;
- typed message round trip and acknowledgement;
- disconnect, retry, stale-peer, malformed-message, and unknown-result behavior;
- accessibility and Liquid Glass review;
- release-signed two-device evidence if the capability is shipping.

## Sources

- [DeviceDiscoveryUI](https://developer.apple.com/documentation/devicediscoveryui)
- [DevicePairingView](https://developer.apple.com/documentation/devicediscoveryui/devicepairingview)
- [DevicePicker](https://developer.apple.com/documentation/devicediscoveryui/devicepicker)
- [Device picker initializer](https://developer.apple.com/documentation/devicediscoveryui/devicepicker/init%28_%3Aaccess%3Aonselect%3Alabel%3Afallback%3Aparameters%3A%29)
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
