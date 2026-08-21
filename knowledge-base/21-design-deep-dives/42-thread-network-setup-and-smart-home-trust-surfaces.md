# Thread Network Setup and Smart-Home Trust Surfaces

Thread setup is a trust-sensitive system workflow disguised as a device-management screen. The design should feel native to Apple platforms, but it must not imitate Apple Home or hide the boundary between an app, a Border Router, iCloud Keychain, Apple Home, and a person’s consent.

The visual loop is:

~~~text
explain the goal -> show the exact network scope -> request consent
-> perform one credential operation -> report observed state -> offer recovery
~~~

Liquid Glass can organize this loop. It cannot make a saved credential look like an active network, and it cannot replace Apple’s consent or system-owned settings.

## Start with the person’s goal

Use an outcome-based entry point rather than a framework label:

| Person’s goal | First surface |
| --- | --- |
| Add my product’s Border Router | Border Router setup and network choice |
| Repair a stale Border Router | Router list with freshness and repair action |
| Add a second Border Router | Resiliency explanation and per-router status |
| Let another app use my product’s network | Team-scoped credential-sharing explanation |
| Connect a Matter accessory | Matter/accessory commissioning route, with Thread as infrastructure detail |
| Understand why setup failed | Diagnostic summary with next action and system boundary |

Do not lead with “Manage Thread Credentials.” That is an implementation concept, not a user outcome.

## Native screen structure

A compact iPhone route can use four levels:

1. **Context header** — home/network name only if the person has already revealed it; otherwise use a redacted or generic label.
2. **Status group** — Border Router identity, current state, credential freshness, and last observed time.
3. **Primary action** — Set up, Repair, Sync credentials, or Open Settings, depending on the state.
4. **Details and recovery** — What the app knows, what it does not know, privacy explanation, and removal/undo.

On iPad or Mac Catalyst, use a sidebar or split view for Border Routers and a detail column for the selected router. Keep the same state semantics; do not create a second vocabulary just because the layout is wider.

## Setup state model

Use a state model that makes system ownership obvious:

| State | User-facing label | Description | Action |
| --- | --- | --- | --- |
| unsupportedBuild | Not available in this build | Capability or distribution path is not present | Show target/build explanation |
| readyToDiscover | Ready to find a Border Router | The app has not identified hardware | Start discovery |
| routerFound | Border Router found | Identity is known; no credential operation yet | Review |
| networkChoice | Choose a Thread network | More than one valid choice or a preferred-network decision is pending | Choose or request consent |
| consentRequired | Permission needed | Apple will ask to access preferred credentials | Continue |
| credentialsAvailable | Credentials available | Framework returned a credential object for the intended scope | Store/update |
| syncing | Syncing network access | Store/update operation is in progress | Cancel if safe |
| stored | Credentials stored | Framework accepted the operation | Verify router state |
| routerJoining | Border Router joining | Product-owned join/configuration step is in progress | Wait or recover |
| active | Border Router active | Product has observed its own active state | View details |
| stale | Needs an update | Dataset or freshness does not match the approved state | Repair |
| denied | Access not granted | Person denied or cancelled consent | Explain and retry later |
| offline | Network unavailable | Local app state exists but current network cannot be confirmed | Retry when connected |
| removed | Border Router removed | Product no longer owns or uses that identity | Add again or dismiss |
| failed | Could not complete setup | A typed error was observed | Show reason and recovery |

Do not use a single Boolean named 'isConnected'. It collapses consent, iCloud Keychain storage, router state, Thread membership, and accessory reachability into one claim.

## Preferred-network consent

Before calling the preferred credential path, present a short rationale:

> This lets the app use the Thread network already selected for this home. Apple will ask for your permission before the network credentials are shared with this app.

Then show:

- which Border Router or product will use the credentials;
- what the app will do after approval;
- that raw credentials will not appear in the app’s interface;
- how to decline and continue with a different route;
- where the person can remove or repair the Border Router later.

Use a normal primary button such as “Continue” or “Use Preferred Network.” The button should trigger the real Apple consent path. Never build a fake permission sheet that visually imitates a system alert.

After denial, preserve the person’s choice in the current flow without treating it as a fatal error:

> Access wasn’t granted. You can try again, choose a different supported network, or finish setup later.

## Liquid Glass composition

Use the material as a grouping tool:

- one glass group for the selected Border Router;
- one compact status control with text and icon;
- one primary action;
- one details control that expands into plain, readable facts.

Avoid:

- a glass card for every row;
- translucent overlays over secrets;
- animated mesh backgrounds behind a consent explanation;
- a green glow that implies coverage or security;
- a morphing control whose label is unavailable to VoiceOver;
- blur as a substitute for redaction.

If the status changes from syncing to stored, preserve the control’s identity and animate only the meaningful change. With Reduce Motion enabled, the same state transition should be understandable from text and semantics. With Reduce Transparency enabled, use an opaque, high-contrast equivalent.

Native controls should do the work: Button, Toggle when the state is genuinely reversible, NavigationLink, confirmationDialog for destructive removal, and system Settings handoff where Apple requires it. A custom glass button should still expose a clear accessibility label, hint, value, and trait.

## Border Router list design

For each Border Router, show only what helps a person act:

- friendly product name;
- redacted or user-approved identity;
- network name only when useful;
- current state;
- last credential update time;
- last product-observed health time;
- “Needs update,” “Ready,” or “Not reachable” explanation;
- repair, inspect, or remove action.

Use a compact status badge plus a text sentence. For example:

> Ready for this app. Credentials were updated yesterday. Router reachability has not been checked since 9:42 AM.

This sentence is intentionally more precise than “Connected.” The app can separately report stored credentials and a router’s observed state.

## Multi-Border-Router resiliency

When a second Border Router is added, explain the benefit without promising a guarantee:

> Additional Border Routers can give the Thread mesh another path. This app will keep the credentials for each router aligned; radio coverage and accessory behavior still depend on the physical network.

Show a small topology summary only if the product has reliable observations. Do not draw a live mesh from a static list. If the product does not observe packet paths, label any illustration “conceptual.”

When one router is stale:

- keep the healthy router visible;
- show which router needs repair;
- do not force a full-network reset;
- provide a scoped update action;
- state whether the update changes the preferred network or only this Border Agent.

## Credential privacy surface

The detail route should expose an audit-friendly summary:

| Safe to show | Keep hidden |
| --- | --- |
| Network name when the person supplied or approved it | Network key |
| Redacted Border Agent ID | PSKC |
| Redacted extended PAN ID | Full operational dataset |
| Channel only when it materially helps troubleshooting | Copyable credential bytes |
| Created/updated timestamps | Raw credential object serialization |

If a support workflow needs an export, export a redacted diagnostic bundle with explicit user action and a retention warning. Never put credentials into a screenshot, share sheet, clipboard, analytics event, AI prompt, or crash message.

## Failure and recovery patterns

Every failure state should answer three questions:

1. What was attempted?
2. What was actually observed?
3. What can the person do next?

Examples:

| Failure | Copy | Recovery |
| --- | --- | --- |
| Preferred network unavailable | No preferred Thread network is available on this device. | Check the home setup or choose the supported product route. |
| Consent denied | Access was not granted, so this app did not receive the preferred network credentials. | Try again or choose a different route. |
| Store failed | Apple did not accept the credential update. Nothing was changed by this attempt. | Retry after checking the Border Router and account state. |
| Router left network | The router identity is known, but it is no longer observed on the selected network. | Rejoin or remove this Border Router. |
| Stale dataset | The router’s credentials may no longer match the selected network. | Review and update; do not silently replace the network. |
| App build lacks distribution entitlement | This build can’t perform the production Thread route. | Use a development build or update the released app. |

Avoid “Something went wrong” when the app has a typed error and a safe recovery action.

## Accessibility and input

The key setup task must work with VoiceOver from the first screen to the Apple consent handoff and back. A suggested reading order is:

1. page title and current goal;
2. selected Border Router and state;
3. explanation of the next operation;
4. primary action;
5. privacy details;
6. recovery and removal actions.

Check:

- Dynamic Type at the largest supported sizes;
- Voice Control phrases that match visible labels;
- Switch Control focus order;
- keyboard activation and escape/back behavior on iPad;
- pointer hover without hiding state;
- Reduce Motion and Reduce Transparency;
- right-to-left layouts;
- long localized network names and dates.

When Apple’s consent prompt appears, do not announce a duplicate fake state. After returning, announce the resulting state and next action once.

## AI-assisted troubleshooting

The best AI surface is a review sheet, not an autonomous network controller. Show:

- redacted facts used;
- the proposed explanation;
- confidence only as model uncertainty, never as network truth;
- exact next step;
- whether the step changes credentials or system state;
- an edit/decline path.

Example:

> The app found one Border Router with credentials updated 18 days ago and one router updated yesterday. This may explain the inconsistent setup result. Review the router list and update the older router?

The app still validates the selected Border Agent, credential state, and operation deterministically. If Apple’s on-device model is unavailable, show the fixed version of the same explanation.

## Proof-oriented visual QA

Capture each state on the intended iOS 26 device family:

- first launch with no Border Router;
- discovery and router selection;
- preferred-network consent before and after the system prompt;
- denial and cancellation;
- credentials stored;
- stale router;
- two Border Routers with one stale;
- network unavailable;
- removal confirmation;
- development-only build;
- reduced motion/transparency;
- VoiceOver and Dynamic Type.

Visual polish is not proof of Thread behavior. The signed target, entitlement, physical Border Router, iCloud Keychain result, consent prompt, and conformance/release evidence must be recorded separately.

## Sources

- [ThreadNetwork](https://developer.apple.com/documentation/threadnetwork)
- [Getting started with ThreadNetwork](https://developer.apple.com/documentation/threadnetwork/getting-started-with-threadnetwork)
- [Configuring a Border Router](https://developer.apple.com/documentation/threadnetwork/configuring-a-border-router)
- [Managing Thread network credentials](https://developer.apple.com/documentation/threadnetwork/managing-thread-network-credentials)
- [THClient](https://developer.apple.com/documentation/threadnetwork/thclient)
- [THCredentials](https://developer.apple.com/documentation/threadnetwork/thcredentials)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios/)
- [Onboarding](https://developer.apple.com/design/human-interface-guidelines/onboarding)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
