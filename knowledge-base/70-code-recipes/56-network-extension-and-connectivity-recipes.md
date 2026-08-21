# Network Extension and Connectivity Recipes

These are compile-oriented route sketches for Network Extension managers, provider targets, Wi-Fi configuration, DNS, URL filters, VPN lifecycle, and reviewable AI policy. They are not compiled in this documentation-only workspace and do not prove entitlement approval, managed-device eligibility, extension execution, traffic protection, URL filtering, Wi-Fi association, server connectivity, privacy compliance, or release readiness.

## Recipe 1: Describe a capability before touching an API

Keep route selection explicit:

~~~swift
enum NetworkCapability {
    case packetTunnel
    case appProxy
    case dnsSettings
    case dnsProxy
    case contentFilter
    case urlFilter
    case hotspotConfiguration
    case hotspotProvider
    case ordinaryNetworking
}

struct NetworkRoute {
    let capability: NetworkCapability
    let requiredTargets: [String]
    let entitlementValues: [String]
    let managedDeviceOnly: Bool
    let userApproval: Bool
    let fallback: String
}
~~~

Populate this from the exact Apple deployment row and the project’s target graph. A route that needs an extension or managed device should not appear as an ordinary “Connect” button until those gates are satisfied.

## Recipe 2: Apply a Wi-Fi configuration, then verify separately

NEHotspotConfigurationManager apply reports configuration work and user approval. It does not prove association or usable service connectivity.

~~~swift
import NetworkExtension

func applyWiFi(ssid: String, passphrase: String) async -> Result<Void, Error> {
    let configuration = NEHotspotConfiguration(
        ssid: ssid,
        passphrase: passphrase,
        isWEP: false
    )
    configuration.joinOnce = false

    do {
        try await NEHotspotConfigurationManager.shared.apply(configuration)
        // Next: observe current network state and wait for the actual service.
        return .success(())
    } catch {
        return .failure(error)
    }
}
~~~

The target needs the Hotspot Configuration entitlement. Handle userDenied and other manager errors. After apply, use a separate connectivity check and label the UI as “configuration applied” until association and service reachability are observed.

## Recipe 3: Load and save a tunnel manager

Keep preference operations separate from tunnel status:

~~~swift
import NetworkExtension

func loadTunnelManagers() async throws -> [NETunnelProviderManager] {
    try await NETunnelProviderManager.loadAllFromPreferences()
}

func persist(_ manager: NETunnelProviderManager) async throws {
    // Configure NETunnelProviderProtocol, localizedDescription, and enabled
    // state according to the selected target and server contract.
    try await manager.saveToPreferences()
}

func start(_ manager: NETunnelProviderManager) throws {
    guard manager.isEnabled else {
        throw NetworkRouteError.notEnabled
    }
    let session = manager.connection
    try session.startTunnel(options: nil)
}
~~~

Verify the exact async signatures and connection property in the selected SDK. The session start call begins the connection process; the app must observe provider and connection state before showing active protection.

## Recipe 4: Packet tunnel provider lifecycle

The provider owns the virtual interface and custom protocol:

~~~swift
import NetworkExtension

final class PacketTunnelProvider: NEPacketTunnelProvider {
    override func startTunnel(
        options: [String : NSObject]?,
        completionHandler: @escaping (Error?) -> Void
    ) {
        let settings = NEPacketTunnelNetworkSettings(
            tunnelRemoteAddress: "198.51.100.1"
        )
        // Set virtual address, DNS, routes, excluded routes, and MTU only
        // after validating the signed configuration and server contract.
        setTunnelNetworkSettings(settings) { error in
            guard error == nil else {
                completionHandler(error)
                return
            }
            // Establish authenticated transport, then report ready.
            completionHandler(nil)
        }
    }

    override func stopTunnel(
        with reason: NEProviderStopReason,
        completionHandler: @escaping () -> Void
    ) {
        // Cancel transport, drain or discard bounded queues, and finish.
        completionHandler()
    }
}
~~~

This is a lifecycle sketch. Do not send packets or claim a connected tunnel until the remote protocol is authenticated, routes are configured, and packetFlow handling is ready. Never hard-code credentials or a production server in a recipe.

## Recipe 5: Save encrypted DNS settings

Built-in DNS settings are not a custom DNS proxy:

~~~swift
import NetworkExtension

func saveDNS() async throws {
    let manager = NEDNSSettingsManager.shared
    try await manager.loadFromPreferences()
    // Build NEDNSOverHTTPSSettings or NEDNSOverTLSSettings with the
    // resolver configuration required by the selected target.
    // Set localizedDescription and onDemandRules deliberately.
    try await manager.saveToPreferences()
    // The person still needs to enable the configuration in Settings on iOS.
}
~~~

Confirm the exact settings initializer and async availability in Xcode. The UI should show saved, enabled, disabled, and removed states independently.

## Recipe 6: Voluntary URL filtering

For a custom networking path that is not WebKit or URLSession, use the voluntary URL filter API when the selected SDK supports it:

~~~swift
import NetworkExtension

func checkURL(_ url: URL) async -> Bool {
    // Confirm the exact NEURLFilter verdict(for:) signature in the SDK.
    // Await the system verdict before opening the URL.
    // If the verdict is deny, do not create the network request.
    return true
}
~~~

For a system URL filter, configure NEURLFilterManager and the URL Filter Control Provider instead. Do not treat a local allow/deny list as proof that WebKit and URLSession traffic is filtered by the system.

## Recipe 7: Reviewable AI policy proposal

Use a typed proposal that cannot install itself:

~~~swift
struct DomainRuleProposal: Sendable {
    let domain: String
    let action: Action
    let reason: String
    let source: String
    let expiresAt: Date?

    enum Action: Sendable {
        case allow
        case block
        case monitor
    }
}

func validate(_ proposal: DomainRuleProposal) throws {
    // Validate domain syntax, scope, expiration, policy, and duplicates.
    // Require explicit approval before changing a manager or provider store.
}
~~~

The model may explain or propose. The deterministic policy layer validates. The user approves. The Network Extension manager/provider commits. Record the observed result and provide an undo/remove action.

## Recipe 8: Render exact network state

Do not map every non-error result to “secure”:

~~~swift
enum NetworkState {
    case savedDisabled
    case waitingForSettings
    case starting
    case providerReady
    case active(scope: String)
    case associationPending
    case serviceUnreachable
    case stopped(reason: String)
    case failed(message: String)
}

func label(for state: NetworkState) -> String {
    switch state {
    case .savedDisabled: return "Saved, not enabled"
    case .waitingForSettings: return "Enable in Settings"
    case .starting: return "Starting"
    case .providerReady: return "Provider ready"
    case .active(let scope): return "Active for " + scope
    case .associationPending: return "Waiting for Wi-Fi"
    case .serviceUnreachable: return "Network connected, service unavailable"
    case .stopped(let reason): return "Stopped: " + reason
    case .failed(let message): return "Could not start: " + message
    }
}
~~~

Use localized strings and a semantic accessibility value in the real target. Keep scope visible and state changes observable.

## Compile and proof gates

- Confirm the exact Network Extension capability and entitlement values.
- Read TN3134 for the provider’s iOS 26 packaging and restriction row.
- Compile the main app and every provider extension as separate targets.
- Inspect signed app and extension entitlements.
- Test approval, denial, Settings changes, provider termination, stale configuration, reconnect, removal, and uninstall.
- Test managed, supervised, and personal-device branches where applicable.
- Measure provider throughput, memory, thermal impact, and failure behavior.
- Test VoiceOver, Dynamic Type, Reduce Motion, Reduce Transparency, Voice Control, and Switch Control.
- Record AI proposal validation, approval, commit, and undo evidence.

## Sources

- [Network Extension](https://developer.apple.com/documentation/networkextension)
- [Configuring network extensions](https://developer.apple.com/documentation/xcode/configuring-network-extensions)
- [Network Extensions Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.networking.networkextension)
- [TN3134: Network Extension provider deployment](https://developer.apple.com/documentation/technotes/tn3134-network-extension-provider-deployment)
- [NEHotspotConfiguration](https://developer.apple.com/documentation/networkextension/nehotspotconfiguration)
- [NEHotspotConfigurationManager](https://developer.apple.com/documentation/networkextension/nehotspotconfigurationmanager)
- [NETunnelProviderManager](https://developer.apple.com/documentation/networkextension/netunnelprovidermanager)
- [NEPacketTunnelProvider](https://developer.apple.com/documentation/networkextension/nepackettunnelprovider)
- [NEDNSSettingsManager](https://developer.apple.com/documentation/networkextension/nednssettingsmanager)
- [URL filters](https://developer.apple.com/documentation/networkextension/url-filters)
- [NEURLFilter](https://developer.apple.com/documentation/networkextension/neurlfilter)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
