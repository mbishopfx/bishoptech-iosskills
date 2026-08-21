# Network Extension and Secure Connectivity

Network Extension is the route for extending system networking behavior, not a replacement for URLSession, Network Framework, or ordinary local-network discovery. It can create VPN configurations, proxy or filter traffic, manage encrypted DNS, configure Wi-Fi, integrate with hotspot authentication, and participate in newer URL-filter and provider routes. Each capability has its own extension process, entitlement values, target graph, device restrictions, user consent, and distribution boundary.

The first planning question is not “which Network Extension class should I import?” It is “which system-owned networking outcome is actually required, and is the intended product eligible for that capability?”

## Route selector

| Product outcome | Primary route | Important boundary |
| --- | --- | --- |
| Route IP packets through a custom VPN protocol | Packet Tunnel Provider with NEPacketTunnelProvider and NETunnelProviderManager | Requires the Network Extensions entitlement, a Packet Tunnel Provider extension, a custom protocol/server, and target-specific signing. |
| Proxy app flows through a custom flow-oriented VPN protocol | App Proxy Provider with NEAppProxyProvider | Apple’s deployment note lists iOS App Proxy as managed-device only. Do not assume a consumer App Store route. |
| Use system-provided encrypted DNS | NEDNSSettingsManager with DNS-over-HTTPS or DNS-over-TLS settings | The person must enable the configuration in Settings on iOS. A saved configuration is not an active resolver. |
| Implement a custom on-device DNS proxy | DNS Proxy Provider | Apple’s deployment note lists iOS DNS proxy restrictions including supervised devices; use only with the exact approved distribution model. |
| Filter traffic from other apps | Content Filter Provider with NEFilterManager, NEFilterControlProvider, and NEFilterDataProvider | Distribution content filters are restricted to supervised devices, with other modes for Screen Time or managed deployments. The data provider has a highly restrictive sandbox. |
| Filter full URLs while preserving privacy | URL Filter with NEURLFilterManager and NEURLFilterControlProvider | Apple’s current deployment note lists the iOS URL filter provider at iOS 26.0. It uses device-side prefiltering and a Private Information Retrieval service. |
| Voluntarily check URLs in a custom networking stack | NEURLFilter participation API | Use the returned allow/deny verdict and do not connect when the verdict denies the URL. This is not the same as installing a system-wide URL filter. |
| Configure a nearby Wi-Fi network | NEHotspotConfiguration and NEHotspotConfigurationManager | Requires the Hotspot Configuration entitlement and user approval. Applying a configuration does not prove the device joined or that the network is usable. |
| Participate in captive-hotspot authentication | NEHotspotManager with evaluation/authentication provider extensions | Requires an approved hotspot use case and extension configuration. The older NEHotspotHelper route is deprecated and requires a special entitlement. |

The [Network Extension provider deployment technote](https://developer.apple.com/documentation/technotes/tn3134-network-extension-provider-deployment) is the authority for packaging, minimum OS, managed-device, supervised-device, and App Store restrictions. Do not infer eligibility from an API symbol or a successful simulator import.

## Entitlement and target graph

The main app and provider extension are separate signed executables. The Network Extensions entitlement is an array whose values identify the provider capabilities used by the target. Common values include:

- dns-settings;
- dns-proxy;
- app-proxy-provider;
- packet-tunnel-provider;
- content-filter-provider;
- url-filter-provider;
- app-push-provider;
- relay, where the selected relay route is supported and approved.

The exact entitlement belongs on the target that needs it. A main-app entitlement does not automatically configure an extension target. Check the final signed artifact rather than trusting the Xcode capability checkbox alone.

Typical target graphs:

| Route | Main app | Extension or provider | External configuration |
| --- | --- | --- | --- |
| Packet tunnel | Manager, consent, status, user controls | Packet Tunnel Provider | App ID capability, provider extension point, tunnel server/protocol |
| App proxy | Manager and per-app rules | App Proxy Provider | Managed deployment and provider configuration |
| Content filter | NEFilterManager configuration and status | Filter Control Provider plus Filter Data Provider | Supervised/managed device, filter capability, App Group rules if used |
| URL filter | NEURLFilterManager configuration, status, reports | URL Filter Control Provider | PIR server, CloudKit Console Identity & Trust registration, filter entitlement |
| DNS settings | NEDNSSettingsManager configuration and user handoff | None for built-in DoH/DoT settings | Network Extensions capability and Settings approval |
| DNS proxy | NEDNSProxyManager configuration | DNS Proxy Provider | Restricted device/deployment model |
| Hotspot configuration | NEHotspotConfigurationManager | None for ordinary network configuration | Hotspot Configuration entitlement and user approval |
| Hotspot providers | NEHotspotManager configuration | Evaluation and Authentication Provider extensions | Approved hotspot use case, provider bundle IDs, provider entitlements |

The extension host process can be started, stopped, suspended, or terminated independently of the app. Use a versioned, minimal control message and an app-owned state model; do not make the provider depend on a view or a live reference to the main process.

## Packet tunnel lifecycle

A packet tunnel provider exposes a virtual interface through packetFlow. The provider receives IP packets routed to the tunnel, encapsulates them according to the custom protocol, sends them to a tunnel server, and injects decapsulated packets back into the virtual interface.

The lifecycle is:

1. The app loads or creates a NETunnelProviderManager configuration.
2. The app saves the configuration and waits for the system to persist it.
3. The person enables or starts the VPN through the app/system route.
4. The system launches the Packet Tunnel Provider extension.
5. startTunnel configures virtual IP, DNS, routes, excluded routes, proxy settings, and MTU.
6. The provider reports readiness only after its transport is established and packet handling is ready.
7. The provider reads/writes packetFlow with bounded work and cancellation.
8. stopTunnel tears down transport and calls its completion handler.

A connected status is not proof that the remote service authenticated, that every route is protected, or that an application-side request succeeded. Keep transport state, tunnel state, route state, and server authorization separate.

## App proxy and flow-oriented routes

An App Proxy Provider receives flows that match its app rules and forwards them over a custom protocol. It is appropriate for flow-oriented proxying, not arbitrary packet manipulation. Apple documents separate TCP and UDP flow types and a provider lifecycle with startProxy, stopProxy, and handleNewFlow.

Higher-level URLSession requests may expose the destination hostname as endpoint information rather than a separate DNS flow. Do not design a hostname policy assuming every networking API yields identical flow metadata. If an app needs packet-level behavior, choose a packet tunnel route instead.

## DNS settings and DNS proxy

NEDNSSettingsManager manages a system-wide built-in DNS configuration using DNS-over-HTTPS or DNS-over-TLS. The settings manager can load, save, remove, and report enabled state, but the person must enable the configuration in Settings on iOS. A UI label such as “private DNS enabled” is only valid after the enabled state is observed.

A DNS Proxy Provider is a different route. It is an extension that handles DNS queries using a custom protocol and has its own deployment restrictions. Do not substitute a built-in DNS settings configuration for a custom DNS proxy or claim that changing the resolver proves all app traffic is tunnelled.

## Content filters and URL filters

### Content filter

A network content filter uses two cooperating providers:

- the Filter Data Provider examines flows and makes pass, block, or need-more-information decisions in a restrictive sandbox;
- the Filter Control Provider supplies rules and can coordinate updates without exposing raw network content to the data provider.

NEFilterManager stores a configuration in Network Extension preferences. Loading, saving, enabling, and provider callbacks are separate state transitions. Distribution filters require the device and deployment model described by Apple, including supervised-device restrictions. A development-only override is not a production entitlement.

### URL filter on iOS 26

The URL Filter route is a distinct iOS 26-era capability. NEURLFilterManager coordinates a privacy-preserving filter using a device-side Bloom filter and, when needed, a Private Information Retrieval server. A control provider fetches the prefilter. The system can evaluate requests from WebKit and URLSession. Apps using other networking APIs can voluntarily call NEURLFilter and honor the returned verdict.

Treat these as separate proof claims:

- the configuration was saved;
- the system reports the filter enabled;
- the control provider fetched a valid prefilter;
- the filter returned a verdict;
- the request was actually prevented;
- a report was generated and delivered.

Do not log full URLs or raw network content merely to make the feature observable. Use redacted identifiers, counts, verdict categories, and explicit retention rules.

## Wi-Fi and hotspot configuration

NEHotspotConfiguration describes an open, personal, enterprise, or Hotspot 2.0 network. Applying it through NEHotspotConfigurationManager can prompt the person for approval and attempts to join when the network is nearby. Apple explicitly distinguishes successful configuration from successful association and usable TCP/IP connectivity.

After apply returns, use the appropriate current-network or connectivity route and a connection API that waits for connectivity. For a local service, Network Framework can wait for a Bonjour connection; for a URL, URLSession can use waitsForConnectivity. Never show “connected” solely because apply completed.

Hotspot provider extensions are a different feature from ordinary Wi-Fi configuration. The current API uses NEHotspotManager with evaluation and authentication provider extensions. The older NEHotspotHelper class is deprecated and needs an Apple-approved special entitlement. Do not use HotspotHelper for accessory integration, Wi-Fi location, or a generic Wi-Fi scanner.

## Security and AI boundaries

Network Extension can affect traffic from other apps or the entire device. Treat every rule, route, DNS server, domain list, and filter decision as security-sensitive:

- use least-privilege capability and target configuration;
- keep credentials in Keychain or the system configuration path, not logs or App Groups;
- authenticate the tunnel server and protect replay/reconnect state;
- validate provider messages and configuration versions;
- fail safely according to the product’s explicit policy;
- do not call a tunnel, DNS, filter, or Wi-Fi route “secure” without defining what it protects and what it does not.

On-device AI can propose a domain classification, a blocked-domain rule, a Wi-Fi setup explanation, or a human-readable connection diagnosis. The model must not silently install a VPN, change a filter, approve a hotspot, or claim security. Review the proposal, validate it deterministically, and commit through a system-aware use case.

## Sources

- [Network Extension](https://developer.apple.com/documentation/networkextension)
- [Configuring network extensions](https://developer.apple.com/documentation/xcode/configuring-network-extensions)
- [Network Extensions Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.networking.networkextension)
- [TN3134: Network Extension provider deployment](https://developer.apple.com/documentation/technotes/tn3134-network-extension-provider-deployment)
- [Packet tunnel provider](https://developer.apple.com/documentation/networkextension/packet-tunnel-provider)
- [NEPacketTunnelProvider](https://developer.apple.com/documentation/networkextension/nepackettunnelprovider)
- [NETunnelProviderManager](https://developer.apple.com/documentation/networkextension/netunnelprovidermanager)
- [NETunnelProviderSession](https://developer.apple.com/documentation/networkextension/netunnelprovidersession)
- [App proxy provider](https://developer.apple.com/documentation/networkextension/app-proxy-provider)
- [DNS settings](https://developer.apple.com/documentation/networkextension/dns-settings)
- [DNS proxy provider](https://developer.apple.com/documentation/networkextension/dns-proxy-provider)
- [Content filter providers](https://developer.apple.com/documentation/networkextension/content-filter-providers)
- [URL filters](https://developer.apple.com/documentation/networkextension/url-filters)
- [NEURLFilter](https://developer.apple.com/documentation/networkextension/neurlfilter)
- [NEURLFilterManager](https://developer.apple.com/documentation/networkextension/neurlfiltermanager)
- [Hotspot helper](https://developer.apple.com/documentation/networkextension/hotspot-helper)
- [NEHotspotManager](https://developer.apple.com/documentation/networkextension/nehotspotmanager)
- [NEHotspotConfiguration](https://developer.apple.com/documentation/networkextension/nehotspotconfiguration)
- [NEHotspotConfigurationManager](https://developer.apple.com/documentation/networkextension/nehotspotconfigurationmanager)
