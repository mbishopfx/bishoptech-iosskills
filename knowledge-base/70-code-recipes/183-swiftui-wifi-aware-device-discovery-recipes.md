# SwiftUI Wi-Fi Aware and device-discovery recipes

These snippets target the installed iOS 26.4 SDK. They are small route
examples intended to be placed behind a product-owned actor/coordinator. They
do not include the signed entitlement, `WiFiAwareServices`,
`NSAccessorySetupKitSupports`, app-owned identity, user authorization, or
physical-device proof required by a shipping app.

The iOS SwiftUI SDK interface marks `devicePickerSupports` unavailable for
iOS, even though Apple’s cross-platform documentation includes that
environment value in its DeviceDiscoveryUI material. The recipes therefore
use the provider/framework support path and explicit fallback views instead of
copying a tvOS-only environment example into an iOS target.

## 1. Gate Wi-Fi Aware and read its limits

Capability values are configuration inputs, not proof that a later pairing or
connection will succeed.

~~~swift
import WiFiAware

@available(iOS 26.0, *)
struct WiFiAwareLimits: Sendable {
    let supported: Bool
    let maximumConnectableDevices: Int
    let maximumPublishableServices: Int
    let maximumSubscribableServices: Int
}

@available(iOS 26.0, *)
func readWiFiAwareLimits() -> WiFiAwareLimits {
    WiFiAwareLimits(
        supported: WACapabilities.supportedFeatures.contains(.wifiAware),
        maximumConnectableDevices: WACapabilities.maximumConnectableDevices,
        maximumPublishableServices: WACapabilities.maximumPublishableServices,
        maximumSubscribableServices: WACapabilities.maximumSubscribableServices
    )
}
~~~

## 2. Read the current paired-device snapshot

The paired-device sequence is asynchronous. A snapshot can be absent or can
change while the screen is visible; retain a revision in the coordinator.

~~~swift
import WiFiAware

@available(iOS 26.0, *)
func currentPairedDevices() async throws -> [WAPairedDevice] {
    guard let snapshot = try await WAPairedDevice.allDevices.current() else {
        return []
    }
    return Array(snapshot.values)
}
~~~

## 3. Resolve a declared publishable service

The service name must also exist in the target’s `WiFiAwareServices` property
list declaration. Do not accept a name supplied by a peer as a substitute.

~~~swift
import WiFiAware

@available(iOS 26.0, *)
extension WAPublishableService {
    static var bishopSync: WAPublishableService {
        allServices["_bishop-sync._tcp"]!
    }
}
~~~

## 4. Create a Wi-Fi Aware publisher listener

`WAPublisherListener` describes which service this app publishes and which
paired devices it will accept. Network Framework owns the typed protocol
stack.

~~~swift
import Network
import WiFiAware

@available(iOS 26.0, *)
extension WAPublishableService {
    static var publisherService: WAPublishableService {
        allServices["_bishop-sync._tcp"]!
    }
}

@available(iOS 26.0, *)
func makeWiFiAwarePublisher() throws -> NetworkListener<TLS> {
    try NetworkListener(
        for: .wifiAware(
            .connecting(
                to: .publisherService,
                from: .userSpecifiedDevices,
                datapath: .realtime
            )
        )
    ) {
        TLS { TCP() }
    }
}
~~~

## 5. Create a Wi-Fi Aware subscriber browser

Use a typed browser provider and keep endpoint selection separate from
authentication.

~~~swift
import Network
import WiFiAware

@available(iOS 26.0, *)
extension WASubscribableService {
    static var subscriberService: WASubscribableService {
        allServices["_bishop-sync._tcp"]!
    }
}

@available(iOS 26.0, *)
func makeWiFiAwareSubscriberBrowser() -> NetworkBrowser<WASubscriberBrowser> {
    NetworkBrowser(
        for: .wifiAware(
            .connecting(
                to: .userSpecifiedDevices,
                from: .subscriberService
            )
        )
    )
}
~~~

## 6. Connect to the selected typed endpoint

The selected endpoint is a transport input. Perform the app-owned handshake
after the connection reaches the usable state.

~~~swift
import Network
import WiFiAware

@available(iOS 26.0, *)
func makeWiFiAwareConnection(to endpoint: WAEndpoint) -> NetworkConnection<TLS> {
    NetworkConnection(to: endpoint) {
        TLS { TCP() }
    }
}
~~~

## 7. Configure Wi-Fi Aware performance mode

Keep performance policy in the transport coordinator. It is not a promise of
throughput or latency.

~~~swift
import Network
import WiFiAware

@available(iOS 26.0, *)
func makeRealtimeWiFiAwareParameters() -> NWParameters {
    NWParameters().wifiAware { parameters in
        parameters.performanceMode = .realtime
    }
}
~~~

## 8. Read the current Wi-Fi Aware path performance

`NWPath.wifiAware` is asynchronous and throwable. Treat the resulting report
as a current observation and make the UI resilient to a missing path.

~~~swift
import Network
import WiFiAware

@available(iOS 26.0, *)
func currentWiFiAwarePerformance(
    from connection: NetworkConnection<TLS>
) async throws -> WAPerformanceReport? {
    guard let path = try await connection.currentPath?.wifiAware else {
        return nil
    }
    return path.performance
}
~~~

## 9. Preserve the Wi-Fi Aware-specific error

Map `NWError.wifiAware` into a domain state without flattening missing
entitlement, unsupported hardware, timeouts, and termination into one empty
list.

~~~swift
import Network
import WiFiAware

@available(iOS 26.0, *)
func wiFiAwareCause(from error: NWError) -> WAError? {
    error.wifiAware
}
~~~

## 10. Present a SwiftUI DevicePicker for a subscriber

The fallback is part of the route. Keep the endpoint out of the view’s long-
lived identity model until the coordinator has reviewed it.

~~~swift
import DeviceDiscoveryUI
import SwiftUI
import WiFiAware

@available(iOS 26.0, *)
extension WASubscribableService {
    static var pickerService: WASubscribableService {
        allServices["_bishop-sync._tcp"]!
    }
}

@available(iOS 26.0, *)
struct WiFiAwareDevicePickerView: View {
    var body: some View {
        DevicePicker(
            .wifiAware(
                .connecting(
                    to: .userSpecifiedDevices,
                    from: .pickerService
                )
            )
        ) { endpoint in
            _ = endpoint
            // Send the endpoint to an actor-owned review coordinator.
        } label: {
            Label("Choose nearby device", systemImage: "plus")
        } fallback: {
            Label("Nearby pairing unavailable", systemImage: "xmark.circle")
        }
    }
}
~~~

## 11. Present a SwiftUI DevicePairingView for a publisher

Use a user-triggered control to become discoverable. Do not advertise a
listener merely because a settings view appeared.

~~~swift
import DeviceDiscoveryUI
import SwiftUI
import WiFiAware

@available(iOS 26.0, *)
extension WAPublishableService {
    static var pairingService: WAPublishableService {
        allServices["_bishop-sync._tcp"]!
    }
}

@available(iOS 26.0, *)
struct WiFiAwareDevicePairingView: View {
    var body: some View {
        DevicePairingView(
            .wifiAware(
                .connecting(
                    to: .pairingService,
                    from: .userSpecifiedDevices
                )
            )
        ) {
            Label("Become discoverable", systemImage: "dot.radiowaves.left.and.right")
        } fallback: {
            Label("Nearby advertising unavailable", systemImage: "xmark.circle")
        }
    }
}
~~~

## 12. Bridge a Wi-Fi Aware browser into UIKit

Use this when the host app’s navigation or presentation stack is UIKit-owned.
The selected controller endpoint is still a candidate, not application trust.

~~~swift
import DeviceDiscoveryUI
import Network
import WiFiAware

@MainActor
@available(iOS 26.0, *)
func makeUIKitWiFiAwarePicker() -> DDDevicePickerViewController? {
    let browser = WASubscriberBrowser.wifiAware(
        .connecting(
            to: .userSpecifiedDevices,
            from: WASubscribableService.allServices["_bishop-sync._tcp"]!
        )
    )
    let parameters = NWParameters().wifiAware { parameters in
        parameters.performanceMode = .realtime
    }
    return DDDevicePickerViewController(
        browseDescriptor: browser.makeDescriptor(),
        parameters: parameters,
        access: .permanent
    )
}
~~~

## 13. Activate and present an AccessorySetupKit picker

Retain the session for the lifetime of the setup flow. The session is
unusable after `invalidate()`.

~~~swift
import AccessorySetupKit
import UIKit

@available(iOS 26.0, *)
final class WiFiAwareAccessorySetupCoordinator: NSObject {
    private let session = ASAccessorySession()

    func activate() {
        session.activate(on: .main) { event in
            _ = event.eventType
            _ = event.accessory
            _ = event.error
        }
    }

    func showPicker() {
        let descriptor = ASDiscoveryDescriptor()
        descriptor.wifiAwareServiceName = "_bishop-accessory._tcp"
        descriptor.wifiAwareServiceRole = .subscriber

        let item = ASPickerDisplayItem(
            name: "Bishop accessory",
            productImage: UIImage(systemName: "dot.radiowaves.left.and.right")!,
            descriptor: descriptor
        )
        session.showPicker(for: [item]) { error in
            _ = error
        }
    }

    func invalidate() {
        session.invalidate()
    }
}
~~~

## 14. Keep an AI explanation typed and subordinate

This is a deterministic proposal boundary. A Foundation Models session may
explain this redacted observation, but it must not select a raw endpoint or
invoke setup/transport side effects.

~~~swift
struct NearbyEligibility: Sendable {
    let relationship: String
    let isPaired: Bool
    let serviceRole: String
    let protocolRevision: Int
    let operationScope: String
}

struct ConnectionExplanationProposal: Sendable {
    let title: String
    let reasons: [String]
    let sourceRevision: Int
}

func makeExplanationProposal(
    from observation: NearbyEligibility
) -> ConnectionExplanationProposal? {
    guard observation.isPaired, observation.protocolRevision >= 1 else {
        return nil
    }

    return ConnectionExplanationProposal(
        title: "Eligible for review",
        reasons: [
            "The selected relationship is paired.",
            "The service role is \(observation.serviceRole).",
            "The requested scope is \(observation.operationScope)."
        ],
        sourceRevision: observation.protocolRevision
    )
}
~~~

The user still reviews the peer and operation. Immediately before a side
effect, deterministic authorization and current transport state must be
rechecked.

## Recipe guardrails

- Add the signed Wi-Fi Aware entitlement and matching service property-list
  declaration to the actual target.
- Add AccessorySetupKit technology declarations only for real accessory
  technologies and target membership.
- Keep `WAPairedDevice`, `ASAccessory`, endpoint, display name, and app-owned
  identity in separate models.
- Use TLS or another explicitly reviewed protocol stack for sensitive data.
- Bound message size, protocol revision, retry count, and operation lifetime.
- Cancel browser, listener, picker, session, and connection work when the user
  leaves or cancels.
- Treat a pairing result, path-ready state, send completion, or AI proposal as
  an intermediate state, not as proof of identity, authorization, delivery, or
  release readiness.
- Test two supported physical devices and at least one real accessory before
  claiming the route works.

## Sources

- [Wi-Fi Aware](https://developer.apple.com/documentation/wifiaware)
- [Building peer-to-peer apps](https://developer.apple.com/documentation/wifiaware/building-peer-to-peer-apps)
- [WACapabilities](https://developer.apple.com/documentation/wifiaware/wacapabilities)
- [WAPairedDevice](https://developer.apple.com/documentation/wifiaware/wapaireddevice)
- [WAPublishableService](https://developer.apple.com/documentation/wifiaware/wapublishableservice)
- [WASubscribableService](https://developer.apple.com/documentation/wifiaware/wasubscribableservice)
- [WAPublisherListener](https://developer.apple.com/documentation/wifiaware/wapublisherlistener)
- [WASubscriberBrowser](https://developer.apple.com/documentation/wifiaware/wasubscriberbrowser)
- [WAEndpoint](https://developer.apple.com/documentation/wifiaware/waendpoint)
- [WAPath](https://developer.apple.com/documentation/wifiaware/wapath)
- [WAError](https://developer.apple.com/documentation/wifiaware/waerror)
- [Network](https://developer.apple.com/documentation/network)
- [NetworkConnection](https://developer.apple.com/documentation/network/networkconnection)
- [NetworkListener](https://developer.apple.com/documentation/network/networklistener)
- [NetworkBrowser](https://developer.apple.com/documentation/network/networkbrowser)
- [NWParameters](https://developer.apple.com/documentation/network/nwparameters)
- [DeviceDiscoveryUI](https://developer.apple.com/documentation/devicediscoveryui)
- [DevicePairingView](https://developer.apple.com/documentation/devicediscoveryui/devicepairingview)
- [DevicePicker](https://developer.apple.com/documentation/devicediscoveryui/devicepicker)
- [DDDevicePickerViewController](https://developer.apple.com/documentation/devicediscoveryui/dddevicepickerviewcontroller)
- [AccessorySetupKit](https://developer.apple.com/documentation/accessorysetupkit)
- [Discovering and configuring accessories](https://developer.apple.com/documentation/accessorysetupkit/discovering-and-configuring-accessories)
- [ASAccessorySession](https://developer.apple.com/documentation/accessorysetupkit/asaccessorysession)
- [ASDiscoveryDescriptor](https://developer.apple.com/documentation/accessorysetupkit/asdiscoverydescriptor)
- [ASPickerDisplayItem](https://developer.apple.com/documentation/accessorysetupkit/aspickerdisplayitem)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
