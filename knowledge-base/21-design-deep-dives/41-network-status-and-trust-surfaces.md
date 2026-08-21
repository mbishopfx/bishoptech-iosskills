# Network Status and Trust Surfaces

Networking features are easy to make look more certain than they are. A green shield, “secure” label, or animated connection line can imply encryption, tunnel coverage, server authentication, or usable connectivity that the app has not actually observed. The native design goal is precise trust: show what the system says, what the app knows, what remains pending, and what the person can do next.

## State before decoration

Use a domain-specific state model:

| State | Honest label | Primary action |
| --- | --- | --- |
| Unconfigured | Not configured | Set up |
| Needs entitlement/configuration | Setup unavailable for this build | Explain target requirement |
| Needs user approval | Approval required | Open system approval route |
| Saved but disabled | Configuration saved | Enable in Settings or connect |
| Connecting | Connecting | Cancel or wait |
| Active | Active for the observed scope | View details or disconnect |
| Partially active | Active for selected apps/routes | View included and excluded scope |
| Degraded | Active with a reported limitation | Retry, inspect, or disconnect |
| Failed | Could not start | Retry or use fallback |
| Stopped by system | Stopped | Inspect reason and restart |
| Managed restriction | Controlled by device administrator | Explain without offering a fake override |

For Wi-Fi, distinguish:

configuration applied -> approval observed -> network association observed -> IP connectivity observed -> service reachable

For a tunnel, distinguish:

configuration saved -> provider launched -> transport authenticated -> virtual interface ready -> packet path observed

The UI should never jump from “configuration applied” to “internet protected.”

## Trust hierarchy

Present facts in this order:

1. What the person asked the app to do.
2. What the system requires or controls.
3. What the app has observed.
4. What scope is covered.
5. What remains uncertain or excluded.
6. What action is safe next.

Example:

“Private DNS configuration saved. iPhone still needs you to enable it in Settings. This app has not verified that every app uses the resolver.”

This is more useful than a green lock icon with no scope or evidence.

## Liquid Glass and networking controls

Liquid Glass is appropriate for a functional connection control group when it improves hierarchy:

- connect/disconnect;
- current state;
- scope or selected profile;
- a compact activity indicator;
- a detail action.

Keep the group visually connected to the state it controls. Do not put a full-screen glass veil over a settings page or use blur to hide an error. Use native controls, semantic labels, and a high-contrast fallback when transparency is reduced.

For a tunnel or filter, the primary action must remain available without a gesture that depends on a moving animation. A small status icon can supplement text but cannot replace it. Use a stable identity when the control morphs between connect, connecting, active, and disconnecting.

## Permission and approval copy

Explain the consequence before the system or Settings handoff:

- what traffic, apps, or DNS requests are in scope;
- whether a provider or server is involved;
- whether the feature is managed or supervised;
- whether content may be inspected locally;
- whether a configuration persists after the app closes;
- how to disconnect or remove it;
- whether the app can see raw content or only a verdict/status.

Use “Continue,” “Set Up,” or “Open Settings” for a pre-alert action. Do not build a fake system approval view, use an “Allow” button that does not open the system flow, or imply that declining makes the device unsafe.

## Provider-aware surfaces

Provider extensions are not just background workers. They may be terminated, relaunched, suspended, or unable to communicate with the main app. Design the app surface around normalized events:

| Provider event | User-facing state |
| --- | --- |
| Provider launched | Starting |
| Provider reports readiness | Active for the selected scope |
| Provider reports authentication failure | Could not authenticate |
| Provider stopped with a reason | Stopped because of the reported reason |
| Configuration changed externally | Settings changed; reload required |
| Managed/supervised restriction | Controlled by device management |
| Filter verdict unavailable | Filter decision unavailable; show the chosen fail-open/closed policy |

Do not show extension logs as product copy. Translate them into a concise state, detail view, and recovery action.

## URL-filter and AI review design

An on-device AI feature can help a person understand a URL-filter rule set or propose a user-defined category. The review surface should show:

- the exact domain or normalized pattern;
- why it was proposed;
- whether the source is local, server-provided, or system-provided;
- the scope of the rule;
- the expiration or update policy;
- an example of an allowed and denied outcome;
- an editable rule before commit;
- a clear way to remove the rule.

Never let a model silently add a block list, change fail-open/closed behavior, or transmit a URL list. The filter manager or provider owns the deterministic configuration; the model only proposes text or a typed rule for review.

## Accessibility and localization

The key tasks must work with:

- VoiceOver announcing connection state, scope, and next action;
- Dynamic Type without hiding disconnect or remove controls;
- Voice Control phrases such as “Connect,” “Open Settings,” and “Disconnect”;
- Switch Control reaching the primary and recovery actions;
- Reduce Motion without losing the meaning of connecting or stopping;
- Reduce Transparency with a readable opaque surface;
- right-to-left layout and long localized network names;
- keyboard and pointer input on iPad where the target supports it.

Announce state changes only when they matter, and avoid announcing every network transition as a disruptive alert. Use a concise status announcement plus a detail route.

## Offline and degraded states

The app can often show the last known configuration while offline, but it should label freshness. Separate:

- local configuration state;
- system provider state;
- network reachability;
- remote server authentication;
- service-level reachability;
- policy/filter data freshness.

A cached “active” badge should not survive sign-out, configuration removal, or a known provider stop. A retry button should cancel or supersede an older request so a late result cannot overwrite a newer state.

## Sources

- [Network Extension](https://developer.apple.com/documentation/networkextension)
- [Configuring network extensions](https://developer.apple.com/documentation/xcode/configuring-network-extensions)
- [TN3134: Network Extension provider deployment](https://developer.apple.com/documentation/technotes/tn3134-network-extension-provider-deployment)
- [URL filters](https://developer.apple.com/documentation/networkextension/url-filters)
- [NEHotspotConfigurationManager](https://developer.apple.com/documentation/networkextension/nehotspotconfigurationmanager)
- [NEDNSSettingsManager](https://developer.apple.com/documentation/networkextension/nednssettingsmanager)
- [NETunnelProviderSession](https://developer.apple.com/documentation/networkextension/netunnelprovidersession)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
