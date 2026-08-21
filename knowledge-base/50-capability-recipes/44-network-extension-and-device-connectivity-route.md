# Network Extension and Device Connectivity Route

Use this route when an app must configure Wi-Fi, manage a system networking profile, route traffic through a provider, filter URLs, explain a supervised-device policy, or help a person diagnose a connection without overstating what the app can observe.

This route is intentionally capability-first. Network Extension work can be blocked by entitlement approval, managed-device policy, extension packaging, or distribution restrictions even when the Swift code is correct.

## Outcome contract

The person can:

1. understand the networking scope and privacy consequence;
2. see whether the selected capability is available for this target and device;
3. approve or configure the system-owned route;
4. observe saved, enabled, connecting, active, degraded, and stopped states;
5. recover from a provider, server, Wi-Fi, or managed-device failure;
6. inspect or remove the configuration;
7. review any AI-generated rule or diagnosis before it changes networking behavior.

## Choose the smallest route

| Need | Route |
| --- | --- |
| Join a known Wi-Fi network | NEHotspotConfigurationManager |
| System DNS-over-HTTPS or DNS-over-TLS | NEDNSSettingsManager |
| Custom packet VPN | NETunnelProviderManager and NEPacketTunnelProvider |
| Custom flow proxy | NEAppProxyProvider and a managed per-app configuration |
| Organization or Screen Time filtering | NEFilterManager with Filter Control/Data Provider extensions |
| Full URL policy on supported iOS 26 deployment | NEURLFilterManager and URL Filter Control Provider |
| Custom DNS proxy | NEDNSProxyManager and DNS Proxy Provider |
| Captive hotspot authentication | NEHotspotManager with evaluation/authentication extensions |
| Ordinary API request | URLSession, Network Framework, or WebKit instead |

Do not choose a system-wide provider when a normal app-owned request, local-network permission, or Network Framework connection satisfies the outcome.

## Deployment gate

Before writing a manager or provider:

- identify the exact provider type;
- read TN3134 for the selected platform, minimum OS, managed-device, supervised-device, and App Store restrictions;
- request or confirm the necessary Apple capability/entitlement;
- map every executable target that needs the entitlement;
- map the extension point and principal class;
- decide whether the product is consumer, managed, supervised, Screen Time, or enterprise;
- define the server/protocol or rule-data contract;
- write the fallback for a build without the capability.

For iOS 26, TN3134 lists URL filter and hotspot provider rows at 26.0, but that does not remove their entitlement, configuration, or use-case restrictions.

## Ownership graph

SwiftUI settings surface -> CapabilityCoordinator -> NetworkExtension manager -> system preference/configuration -> provider extension -> remote service or local rule store

| Layer | Owns | Does not own |
| --- | --- | --- |
| SwiftUI surface | Explanation, state labels, user actions, accessibility | Raw provider lifecycle or security proof |
| CapabilityCoordinator | Availability, load/save/apply, cancellation, normalized state | Packet forwarding or filter verdicts |
| Manager adapter | NetworkExtension API and preference lifecycle | Product claims about protection or server reachability |
| Provider extension | Tunnel/proxy/filter/hotspot protocol lifecycle | Main-app view state or arbitrary shared secrets |
| Rule/configuration store | Versioned rules, expiration, integrity, redaction | User approval or system enablement |
| Remote service | Protocol authentication and server-side policy | Device-side system state |
| AI proposal layer | Explanation, classification, typed suggestion | Silent installation, security guarantee, or final policy |

## State machine

Use a state machine such as:

unavailable(reason)

needsEntitlement

needsUserApproval

loadingConfiguration

configuredDisabled

starting

providerReady

active(scope)

degraded(reason)

stopping

stopped(reason)

failed(recoverableError)

For Wi-Fi, add separate association and service-reachability states. For URL filtering, add prefilter freshness, manager status, control-provider status, verdict, and report status. For a packet tunnel, add transport authentication and virtual-interface readiness.

## Packet-tunnel composition

The app configures a NETunnelProviderManager with a NETunnelProviderProtocol. The Packet Tunnel Provider sets NEPacketTunnelNetworkSettings, then reads and writes packetFlow. The remote protocol should have:

- authenticated handshake;
- configuration/version negotiation;
- bounded send/receive queues;
- packet ordering and loss policy;
- reconnect and reasserting behavior;
- cancellation and stop handling;
- key/credential rotation;
- redacted diagnostics;
- explicit routes and excluded routes.

The app’s “active” state should be driven by observed provider and connection status, not by a successful call to startTunnel alone.

## URL-filter composition

For the iOS 26 URL Filter route:

1. configure the URL Filter capability and extension target;
2. register the configuration on the documented Identity & Trust path;
3. provision the PIR server and filter metadata;
4. fetch or package a valid Bloom prefilter through the control provider;
5. load and save the manager preferences;
6. observe status/configuration changes;
7. choose fail-open or fail-closed behavior deliberately;
8. test WebKit, URLSession, and the voluntary NEURLFilter participation route separately;
9. redact reports and keep a retention policy.

The filter is not a generic content crawler. Do not send every URL to an AI model or server merely to decide a simple rule.

## Wi-Fi composition

For a user-started Wi-Fi setup:

1. create the narrowest NEHotspotConfiguration;
2. apply it through the shared manager;
3. handle user denial and configuration errors;
4. verify current network association separately;
5. wait for actual service connectivity before claiming success;
6. remove only configurations created by the app;
7. explain that uninstalling the app removes its configured networks.

For hotspot provider extensions, keep evaluation and authentication separate. The provider may need to ask the person to interact through a notification or system route; it should not assume a foreground SwiftUI screen exists.

## AI route

Useful on-device AI roles:

- explain a provider error in plain language;
- classify a user-provided domain list into editable categories;
- suggest a Wi-Fi troubleshooting step;
- summarize redacted connection diagnostics;
- draft a rule for a person to inspect.

Required safeguards:

- do not pass raw network content to a model unless the product explicitly needs it;
- attach source identifiers and freshness to every suggestion;
- validate domain syntax, route scope, expiration, and policy constraints deterministically;
- require user approval before saving a rule or enabling a system profile;
- preserve an undo/remove path;
- do not claim encrypted, private, safe, or protected behavior beyond observed evidence.

## Fallbacks

| Failure | Preserve the goal with |
| --- | --- |
| Network Extension entitlement unavailable | Ordinary URLSession/Network route, manual settings instructions, or import/export of a configuration where allowed |
| Provider restricted to managed/supervised devices | Explain the restriction and provide a local-only diagnostic or admin handoff |
| VPN server unreachable | Show saved configuration and retry; do not show active protection |
| DNS configuration not enabled | Open Settings or provide a manual explanation |
| Wi-Fi apply succeeds but association fails | Show saved network and current association state separately |
| URL filter data is stale | Use explicit stale policy and do not silently broaden the block/allow result |
| AI unavailable | Show deterministic status, rules, and recovery actions |

## Proof minimum

Require target-specific evidence for entitlement, manager preference persistence, system approval, provider launch, active scope, network/service reachability, disconnect/removal, privacy, accessibility, managed-device restrictions, and release configuration. A framework import and a green settings screen prove none of those by themselves.

## Sources

- [Network Extension](https://developer.apple.com/documentation/networkextension)
- [Configuring network extensions](https://developer.apple.com/documentation/xcode/configuring-network-extensions)
- [Network Extensions Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.networking.networkextension)
- [TN3134: Network Extension provider deployment](https://developer.apple.com/documentation/technotes/tn3134-network-extension-provider-deployment)
- [Packet tunnel provider](https://developer.apple.com/documentation/networkextension/packet-tunnel-provider)
- [URL filters](https://developer.apple.com/documentation/networkextension/url-filters)
- [NEURLFilterManager](https://developer.apple.com/documentation/networkextension/neurlfiltermanager)
- [NEHotspotConfigurationManager](https://developer.apple.com/documentation/networkextension/nehotspotconfigurationmanager)
- [DNS settings](https://developer.apple.com/documentation/networkextension/dns-settings)
- [Content filter providers](https://developer.apple.com/documentation/networkextension/content-filter-providers)
- [On-device intelligence](https://developer.apple.com/documentation/TechnologyOverviews/ai-machine-learning)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
