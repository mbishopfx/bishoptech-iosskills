# ThreadNetwork and Border Router Capabilities

ThreadNetwork is the Apple route for building or managing a certified Thread Border Router and for sharing Thread credentials between clients. It is not a general-purpose nearby-device API and it is not a substitute for HomeKit or Matter accessory commissioning. The product decision is whether the app owns a Border Router, manages a Border Router supplied by the product, or only needs to help a person understand an existing Apple Home Thread network.

The framework has an unusually strong distribution boundary. A development capability lets a team exercise the API, but Apple’s current getting-started guidance also requires User Experience and THClient conformance work before requesting a distribution entitlement. Treat that sequence as part of the architecture rather than as a final publishing checkbox.

## What ThreadNetwork represents

Apple describes Thread as a low-power wireless mesh protocol that runs over standard Internet protocols. Thread devices forward packets for one another, so the mesh can gain redundancy as devices are added. A Thread Border Router connects the Thread network to Wi-Fi or Ethernet and lets iOS devices communicate with Thread devices. Apple lists HomePod, HomePod mini, and Apple TV 4K as examples of Border Routers.

The device roles matter when explaining a product:

| Role | Meaning for an app |
| --- | --- |
| Thread Border Router | Bridges Thread traffic to an existing Wi-Fi or Ethernet network; a product that implements one needs a certified hardware and software route. |
| Thread Leader | Manages routers in one Thread network; the network chooses the leader dynamically. It is not an app-owned “master server.” |
| End device | Endpoint accessory that communicates with other Thread devices but does not forward their packets. |
| Sleepy End Device | Low-power endpoint that wakes periodically; a UI should not promise immediate responsiveness for a battery-powered accessory. |

Multiple Border Routers can improve resiliency. The app can configure or update credentials for each Border Agent, but it must not present “more Border Routers” as a guaranteed coverage or uptime claim. The physical network, radio environment, accessory firmware, and Apple Home topology still determine the observed result.

## Choose the correct Apple route

| Desired outcome | Primary Apple route | Keep separate |
| --- | --- | --- |
| Build a product that exposes a Thread Border Router | ThreadNetwork plus the product’s Border Router configuration and management implementation | Hardware certification, accessory protocol, Matter/HomeKit integration, and distribution approval |
| Add a Border Router to an existing Thread network | ThreadNetwork Border Router configuration path and credential management | User consent, accessory onboarding, and proof that the router actually joined |
| Keep credentials for several Border Routers aligned | THClient store/update/delete operations keyed by Border Agent identity | Network membership, router health, and service reachability |
| Read the preferred Thread network | THClient preferred-network availability and credential retrieval | Consent, local-network observation, and a right to modify the network |
| Let another client reuse credentials | THClient’s team-scoped credential database and approved sharing flow | Cross-team access, secret export, or arbitrary credential distribution |
| Commission a Matter accessory | MatterSupport or the product’s supported accessory flow | Thread credential storage and Border Router configuration |
| Control Apple Home accessories | HomeKit or Matter APIs appropriate to the accessory | Thread radio/network administration |
| Explain why a device is offline | A product-owned observation and diagnostic surface | Claiming that ThreadNetwork itself provides a general device-health feed |

Do not begin with a credential read just because a product mentions “smart home.” First decide whether the app is a Border Router client, an accessory app, a Matter commissioning companion, or an explanatory dashboard.

## Development capability, entitlement, and release gates

Apple’s getting-started sequence is:

1. Add the Manage Thread Network Credentials development capability to the app target.
2. Import ThreadNetwork and implement the Border Router configuration/management path.
3. Complete the Thread User Experience and THClient test plans.
4. Submit the test results through Apple’s documented process.
5. Request a Thread Network distribution entitlement before App Store submission.
6. If the product is an Apple HomeKit accessory, follow the MFi requirements separately.
7. Apply for Works with Apple Home branding only if the product meets Apple’s badge process.

The entitlement is a Boolean capability named com.apple.developer.networking.manage-thread-network-credentials. A source entitlement file or Xcode checkbox is not distribution proof. Record the capability on the correct target, inspect the signed artifact, and retain the approval/evidence packet for the distribution route.

The development and distribution states should be modeled explicitly:

~~~text
source capability declared
-> development entitlement available
-> API path compiles in the selected SDK
-> physical Border Router and network test passes
-> UX and THClient conformance artifacts submitted
-> distribution entitlement approved
-> archive target and signed entitlement verified
~~~

If any gate is absent, the app can still expose an honest “not available in this build” or “development-only” state. Do not hide the route behind a generic connection button.

## THClient and the credential database

THClient is the central client object. Apple documents it as a class that safely shares Thread credentials between multiple clients. The framework maintains a database of credentials; THClient can retrieve credentials for a Border Agent or extended PAN ID, retrieve preferred/all/active credentials, store credentials for a Border Agent, and delete credentials for a Border Agent.

The team ID matters. Apple states that the framework uses the team ID stored in the app’s Info.plist to preserve privacy across clients. Credentials stored by one client cannot be modified or deleted by another client. This means:

- do not treat a credential record as a portable JSON document;
- do not copy raw credentials into analytics, logs, pasteboards, or a server;
- keep the app’s team and target configuration consistent;
- test same-team client sharing and cross-team denial as separate cases;
- use Border Agent ID and extended PAN ID as identifiers only after confirming their current API types and lifecycle;
- never expose a “share secret” feature unless the exact Apple-approved route requires it.

The current Swift API surface includes completion-handler forms and concurrency-friendly async forms for several credential requests. Verify the exact overload and availability in the selected Xcode SDK. The documentation also shows an enableCredentialSharingMode API with a tvOS 27.0 availability note; do not assume that method is an iOS 26 route merely because it appears on the current THClient page.

## Credential fields are security-sensitive

THCredentials contains network parameters and framework metadata:

- active operational dataset;
- Border Agent ID;
- channel;
- extended PAN ID;
- network key;
- network name;
- PAN ID;
- PSKC, the commissioner pre-shared key;
- creation date;
- last modification date.

The active operational dataset, network key, PSKC, identifiers, and channel are not harmless diagnostics. The Apple documentation warns that Thread credentials can add devices to a Thread network. A safe model therefore has two representations:

| Representation | Allowed contents |
| --- | --- |
| User-facing summary | Network name when appropriate, redacted Border Router count, freshness, last known state, and next action |
| Internal credential object | Framework-managed credential values held only for the operation that requires them |
| Log/analytics event | Outcome, error category, duration, and redacted stable test identifier; never raw credential bytes |
| AI input | A redacted state summary or typed proposal; never network key, PSKC, or full operational dataset |

Credential equality, freshness, and update decisions should be deterministic. An on-device model can explain a mismatch or draft recovery copy, but it must not invent a dataset, classify a secret, or silently store a credential.

## Preferred-network consent

The preferred network is the default Thread network chosen by the framework for a home. Before requesting preferred credentials, call isPreferredNetworkAvailable. If a preferred network exists, retrieving its credentials requires the person’s consent. A product should not surprise the person with a secret-access prompt during an unrelated scan.

A safe user flow is:

1. Explain why the app needs the preferred network and what operation will follow.
2. Show the app’s current Border Router and target network context without displaying secrets.
3. Ask for the person’s action at the point where Apple will ask for consent.
4. Handle allow, denial, cancellation, and unavailable states.
5. Use the result only for the selected operation.
6. Redact and discard the credential material as soon as the operation no longer needs it.

Retrieval for a Border Agent associated with the app’s team is a different boundary from preferred-network consent. Keep “credentials for my Border Router” separate from “credentials for the home’s preferred network.”

## Store, update, and delete lifecycle

When a Border Router joins a Thread network, use the documented store operation to store or update the credentials in iCloud Keychain. When a Border Router leaves, delete its credentials. The Border Agent ID is the key used for these operations, so a product should persist the association between its physical Border Router identity and its local management record without persisting the secret material in its own database.

The reconciliation loop should account for:

- first Border Router join;
- second Border Router joining the same network;
- router reboot or software update;
- active operational dataset change;
- preferred network change;
- SSID change or home-network migration;
- user denial or revoked consent;
- Border Router removal;
- stale local state after reinstall or device transfer;
- multiple clients writing the same team-scoped credential record.

When an update is needed, compare only the operational values required by the API and product protocol. Do not serialize an entire THCredentials object for convenience. Make an update idempotent and observable:

~~~text
discover Border Agent
-> retrieve or receive current active operational dataset
-> compare against approved local identity and redacted fingerprint
-> store/update through THClient
-> verify completion
-> refresh UI with last-modified time and redacted status
~~~

“Stored” means the framework accepted the credential operation. It does not mean the Border Router is online, that an accessory is reachable, or that a Matter commissioning flow will succeed.

## Border Router configuration and resiliency

The Border Router configuration flow should report the difference between:

- hardware discovered;
- Border Agent identity known;
- target Thread network selected;
- credentials available;
- credentials stored;
- router configured;
- router joined;
- router reachable;
- accessory traffic observed.

Apple’s configuring-a-border-router guidance emphasizes choosing the preferred network and keeping credentials for Border Agents. If multiple Border Routers are present, the app should show each one’s identity and credential freshness without implying that it owns the entire home topology.

Do not use a static “primary router” label unless the product protocol truly has such a concept. Thread’s leader and the framework’s preferred network are not the same thing as an app-defined primary router.

## Privacy, accessibility, and Liquid Glass

Thread setup is a high-trust flow. A native-looking surface should use Liquid Glass only to group actions and status:

- preferred network context;
- Border Router identity;
- credential sync status;
- one primary setup or repair action;
- an expandable details route.

Never place raw network keys, PSKC values, full operational datasets, or copyable secret bytes inside a glass card. Do not make a glowing mesh animation the only indication of status. Provide text labels, a stable semantic value, and a recovery action.

The setup route must work with VoiceOver, Dynamic Type, Voice Control, Switch Control, Reduce Motion, and Reduce Transparency. Localize network names and error messages. Keep consent rationale before the system prompt and explain the consequence of denial without framing the person as unsafe.

## On-device AI route

Useful, bounded AI tasks include:

- translate a technical credential mismatch into plain language;
- summarize which Border Router is stale;
- draft a repair checklist;
- classify a user-written setup note into a typed diagnostic category;
- generate a reviewable accessory setup explanation from redacted state.

The model must not:

- fabricate or mutate Thread credentials;
- decide that a network is secure or healthy from a name alone;
- silently retrieve preferred credentials;
- choose a Border Router without a deterministic product rule;
- upload Thread credentials or raw network diagnostics;
- turn a confidence score into a commissioning or coverage guarantee.

Use a typed proposal, deterministic validation, explicit user approval, and a reversible commit. When the on-device model is unavailable, fall back to fixed diagnostic copy and the same system route.

## Proof boundary

Evidence must be recorded at the layer being claimed:

| Claim | Required evidence |
| --- | --- |
| API route is configured | Target capability, import, SDK/deployment target, and compile evidence |
| Development entitlement is usable | Signed development artifact and device run |
| Preferred network can be read | Physical device, configured home, consent prompt, allow/deny/cancel outcomes |
| Credentials can be stored | Real Border Agent, store/update result, retrieval/reconciliation result, secret-redacted logs |
| Multiple Border Routers stay aligned | Two or more physical Border Routers, dataset update, reboot/rejoin, and per-agent reconciliation |
| Client sharing works | Same-team clients, retrieval/list/delete boundaries, and cross-team denial test |
| Router joined | Border Router’s own diagnostic or protocol evidence plus the app’s observed result |
| Matter/Home accessory works | Separate certified accessory commissioning and control proof |
| App Store distribution is eligible | Conformance test artifacts, Apple approval, distribution entitlement, archive/signing inspection, and release review |

Simulator output, a code sample, or an available framework symbol cannot prove radio behavior, iCloud Keychain persistence, consent UX, a system prompt, certification, or App Store eligibility.

## Sources

- [ThreadNetwork](https://developer.apple.com/documentation/threadnetwork)
- [Getting started with ThreadNetwork](https://developer.apple.com/documentation/threadnetwork/getting-started-with-threadnetwork)
- [Configuring a Border Router](https://developer.apple.com/documentation/threadnetwork/configuring-a-border-router)
- [Managing Thread network credentials](https://developer.apple.com/documentation/threadnetwork/managing-thread-network-credentials)
- [THClient](https://developer.apple.com/documentation/threadnetwork/thclient)
- [THCredentials](https://developer.apple.com/documentation/threadnetwork/thcredentials)
- [Manage Thread Network Credentials entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.networking.manage-thread-network-credentials)
- [Thread Test Plan - THClient API](https://developer.apple.com/apple-home/downloads/Thread-Test-Plan-THClient-API-R1.pdf)
- [Apple Home development](https://developer.apple.com/apple-home/)
- [HomeKit](https://developer.apple.com/documentation/homekit)
- [Matter](https://developer.apple.com/documentation/matter)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
