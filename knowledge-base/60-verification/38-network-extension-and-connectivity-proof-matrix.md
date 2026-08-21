# Network Extension and Connectivity Proof Matrix

Network Extension features can compile while still lacking entitlement approval, a valid provider target, a permitted device class, user approval, a working server, or a trustworthy policy. Use this matrix to keep those claims separate.

## Target and entitlement record

Record before testing:

| Field | Evidence |
| --- | --- |
| Xcode/SDK and deployment target | Project settings and build log |
| Provider type | Packet tunnel, app proxy, DNS, content filter, URL filter, hotspot, or other exact route |
| Main app target | Bundle ID, capabilities, entitlements |
| Extension targets | Bundle IDs, extension point, principal class, embed phase |
| Entitlement values | Signed app and extension entitlements |
| Provisioning/profile state | Developer portal capability and signed profile |
| Device class | Exact iPhone/iPad model and OS build |
| Management state | Supervised, managed, Screen Time, personal, or not applicable |
| External configuration | Server, PIR/CloudKit Identity & Trust, MDM profile, hotspot provider approval |
| Privacy contract | Raw content, URL, DNS, rule, credential, and diagnostic retention |

TN3134 is the deployment authority. Its iOS table currently lists URL filter and hotspot provider routes at iOS 26.0, while other provider types have different minimum versions and managed/supervised restrictions.

## Evidence matrix

| Claim | Minimum evidence | Does not prove the claim |
| --- | --- | --- |
| Entitlement is usable | Developer capability, signed artifact value, correct target membership, and device run | An entitlements source file or Xcode checkbox |
| Manager configuration persists | Load/save/remove result after process restart | An in-memory manager object |
| User approval works | Fresh-device run showing approval, denial, cancellation, and Settings return | A simulated Boolean |
| Packet tunnel starts | Provider extension launch, authenticated transport, network settings completion, and observed packet path | startTunnel returning without error |
| VPN protects intended scope | Included/excluded routes, app rules, DNS behavior, and representative traffic tests | A connected badge |
| App proxy handles flows | Managed configuration, provider launch, TCP/UDP flow handling, and stop/reconnect evidence | A normal consumer device run |
| DNS settings are active | Saved configuration, Settings enablement, resolver observation, and remove path | A DNS server string in memory |
| Content filter works | Supervised/managed device, both provider extensions, rules, verdicts, and sandbox-safe communication | A local filter list or development override |
| URL filter works | iOS 26 target, provider/PIR configuration, prefilter freshness, manager status, WebKit/URLSession requests, and voluntary NEURLFilter verdicts | An AI category label or a Bloom file alone |
| Wi-Fi configuration works | User approval, apply result, current association, waits-for-connectivity service test, and remove result | apply returning nil error |
| Hotspot provider works | Approved entitlement, provider launch, evaluate/authenticate command sequence, notification/UI path, and successful system state | Deprecated HotspotHelper sample code |
| Privacy boundary holds | Redacted logs, traffic/content handling review, retention/deletion test, and no unauthorized upload | A privacy label or local-only claim |
| AI is local | Build/model route, device trace, input boundary, and upload audit | A model object or “on-device” copy line |
| AI rule is safe | Typed proposal fixture, syntax/policy validation, user approval, idempotent save, undo/remove | Model text appearing in a settings view |
| Accessibility works | VoiceOver, Dynamic Type, Reduce Motion/Transparency, Voice Control, Switch Control, and Settings handoff tasks | A visual review |
| Release route is eligible | Archive inspection, entitlements, extension signing, target restrictions, TestFlight/managed-device run, and metadata review | A debug run or simulator success |

## Scenario matrix

### Packet tunnel

- first install and first configuration;
- user cancels or rejects the system approval;
- server authentication failure;
- DNS or route configuration failure;
- provider termination and relaunch;
- reconnect with stale credentials;
- stop while packets are queued;
- excluded route and per-app route fixtures;
- sign out, remove configuration, and uninstall;
- no-server/offline fallback.

### URL and content filtering

- fresh prefilter;
- stale or malformed prefilter;
- allow, block, need-more-information, and fail-open/closed branches;
- WebKit URL, URLSession URL, and custom networking participation;
- IDN/Punycode and URL parsing edge cases;
- configuration/status change while the app is closed;
- supervised versus personal device;
- control provider/data provider termination;
- raw URL redaction and report retention;
- AI proposal rejected or edited.

### Wi-Fi and hotspot

- open, personal, enterprise, and unsupported configuration;
- user approval and denial;
- network not nearby;
- apply succeeds but association does not;
- association succeeds but service is unreachable;
- MDM/Carrier configuration conflict;
- current network changes while the app is open;
- provider evaluation/authentication with and without UI;
- disconnect, remove, reinstall, and Settings changes.

## Performance and safety record

For a provider, record:

- packet or flow throughput;
- queue depth and dropped/blocked data;
- startup and reconnect latency;
- memory and CPU within the extension process;
- battery and thermal impact;
- server round trips and timeout behavior;
- behavior when the app is not running;
- logs redacted to the approved level.

For a filter, record worst-case decision latency and the selected behavior when rules or servers are unavailable. Never use an AI model’s latency or confidence as a substitute for a deterministic safety policy.

## Evidence packet

Attach:

1. route decision and entitlement request;
2. TN3134 deployment row and restriction;
3. target graph and signed artifact inspection;
4. permission/approval and Settings evidence;
5. provider lifecycle traces;
6. traffic, DNS, URL, Wi-Fi, or hotspot observations;
7. privacy/retention review;
8. AI evaluation and approval fixtures, if used;
9. accessibility task results;
10. device-management and release evidence.

Keep the claim vocabulary exact: configured, saved, enabled, provider ready, tunnel active, route observed, service reachable, filter verdict returned, URL blocked, Wi-Fi associated, and hotspot authenticated are not interchangeable.

## Sources

- [Network Extension](https://developer.apple.com/documentation/networkextension)
- [Configuring network extensions](https://developer.apple.com/documentation/xcode/configuring-network-extensions)
- [Network Extensions Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.networking.networkextension)
- [TN3134: Network Extension provider deployment](https://developer.apple.com/documentation/technotes/tn3134-network-extension-provider-deployment)
- [NETunnelProviderManager](https://developer.apple.com/documentation/networkextension/netunnelprovidermanager)
- [NEPacketTunnelProvider](https://developer.apple.com/documentation/networkextension/nepackettunnelprovider)
- [NETunnelProviderSession](https://developer.apple.com/documentation/networkextension/netunnelprovidersession)
- [NEFilterManager](https://developer.apple.com/documentation/networkextension/nefiltermanager)
- [URL filters](https://developer.apple.com/documentation/networkextension/url-filters)
- [NEHotspotConfigurationManager](https://developer.apple.com/documentation/networkextension/nehotspotconfigurationmanager)
- [NEHotspotManager](https://developer.apple.com/documentation/networkextension/nehotspotmanager)
- [NEDNSSettingsManager](https://developer.apple.com/documentation/networkextension/nednssettingsmanager)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
