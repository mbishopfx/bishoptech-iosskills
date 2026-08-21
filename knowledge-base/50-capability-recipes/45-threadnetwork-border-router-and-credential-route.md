# ThreadNetwork Border Router and Credential Route

Use this recipe when an app must configure a Thread Border Router, keep several Border Router credential records aligned, or help a person select and repair an Apple Home Thread network. The recipe keeps four contracts separate:

~~~text
app UI -> ThreadNetwork/THClient -> iCloud Keychain credential database
        -> product Border Router -> Thread/Matter/Home behavior
~~~

The code can be correct while the product remains development-only, lacks a distribution entitlement, or has no physical Border Router to test. Plan the proof route at the same time as the capability route.

## Route selector

| Product need | Route | Do not infer |
| --- | --- | --- |
| Add a product Border Router to the framework-managed network | Border Router configuration plus THClient store/update | A successful store is not proof of radio join |
| Read the home’s preferred Thread network | isPreferredNetworkAvailable then preferred credential request | Availability is not consent |
| Update one Border Router | retrieve credentials for its Border Agent, compare, then store/update | Team-scoped credentials are not portable secrets |
| Remove one Border Router | delete credentials for its Border Agent | Delete does not prove hardware reset |
| Share credentials between same-team clients | THClient database and team-ID boundary | Cross-team sharing or server export |
| Commission a Matter accessory | MatterSupport/accessory route | Thread credential storage alone |
| Show a smart-home dashboard | HomeKit/Matter device APIs | ThreadNetwork is a general device telemetry API |

## Capability and project gate

Before implementation, record:

- deployment target and Xcode SDK;
- main-app bundle ID and target membership;
- Manage Thread Network Credentials development capability;
- entitlement value in the signed development artifact;
- Border Router configuration/management targets and extension points, if any;
- team ID / Info.plist configuration required by the selected client route;
- physical Border Router model and firmware;
- Apple Home/Matter/MFi relationship;
- conformance test plan owner;
- distribution-entitlement request owner;
- privacy manifest and diagnostic-retention decision.

The production route is not complete until the conformance evidence and distribution entitlement are approved. Keep a development-only feature flag or build-state explanation so a debug build does not resemble a shippable capability.

## Ownership graph

| Layer | Owns | Boundary |
| --- | --- | --- |
| SwiftUI route | Goal, consent rationale, state labels, accessible actions | Never stores raw credential bytes in view state |
| ThreadCoordinator | Serialized operations, cancellation, state machine, redacted events | Does not claim router health from credential storage |
| THClientAdapter | Exact Apple API calls and error normalization | Does not decide user-facing security claims |
| Product BorderRouterAdapter | Discovery, product protocol, join/configure/health | Does not bypass Apple credential consent |
| CredentialPolicy | Redacted comparison, update eligibility, removal rules | Does not synthesize or edit a dataset |
| AI ProposalService | Explanation and typed recovery proposal | Does not read secrets or commit changes |
| ProofRecorder | Build/entitlement/device/conformance evidence | Does not become a credential log |

Serialize operations per Border Agent. A late response from an earlier router update must not overwrite a newer selected-router state.

## State machine

Use distinct state axes where possible:

~~~text
capability:
  unavailable -> developmentOnly -> distributionReady

preferred network:
  unknown -> unavailable
  available -> consentNeeded -> credentialsReceived
  available -> consentDenied

border router:
  unknown -> discovered -> selected -> configured -> joinObserved
  configured -> stale -> updating -> configured
  selected -> removed

product:
  idle -> discovering -> joining -> active
  joining -> degraded -> retrying
  any state -> failed(error) -> recovery
~~~

The UI can derive a single summary from these axes, but the model should preserve the underlying facts. For example, a router may be configured with stored credentials while its product health is offline.

## Preferred-network route

1. Explain the intended operation and the credential scope.
2. Call isPreferredNetworkAvailable.
3. If false, show the unavailable route without requesting consent.
4. If true, ask the person to continue to Apple’s consent-controlled preferred credential operation.
5. Handle allow, deny, cancel, and error separately.
6. Use the returned credentials only for the selected Border Router operation.
7. Redact and release the credential object after the operation.

If the app only needs to know that a preferred network exists, stop at availability. Do not request credentials merely to render a status card.

## Existing Border Router route

For a Border Router already associated with the app’s team:

1. Identify the Border Agent with the product protocol.
2. Request the team-scoped credentials for that Border Agent.
3. Compare the required operational values using a deterministic comparison.
4. If unchanged, report credential freshness and continue to product health.
5. If changed, store/update the current active operational dataset.
6. Verify the framework operation completed.
7. Re-run the product’s join/health check.

The route should show “credentials updated” separately from “router active.” The first is a framework/database result; the second requires product-owned evidence.

## Add a second Border Router

The second-router route should be a scoped operation:

1. Discover the new Border Agent.
2. Confirm the person intends to add it to the selected network.
3. Obtain the approved active operational dataset.
4. Store/update the credential for the new Border Agent.
5. Configure the product Border Router.
6. Observe join and health state.
7. Keep the existing router record unchanged unless its dataset is also stale.

If a router reports a different network, do not auto-merge it. Present the network choice and require a deterministic product action. A model may explain the mismatch but cannot choose a home network from names alone.

## Credential comparison

Use a redacted fingerprint only for UI and diagnostics:

~~~text
credential identity:
  borderAgentID -> redacted stable display
  extendedPANID -> redacted stable display
  networkName -> user-approved display or hidden
  activeOperationalDataSet -> compare required fields, never display
  networkKey/PSKC -> never display, log, or send to AI
~~~

Do not rely on object identity, creation dates, or network names as proof that two Border Routers share a Thread network. Compare the operational values required by the product protocol and Apple route, then test the physical device.

## Removal and repair

Removal should have two separately labeled choices when both are supported:

- remove this Border Agent’s framework-managed credentials;
- reset/remove the physical product Border Router.

Deleting credentials from the framework does not automatically erase product firmware state, accessory pairings, or the preferred network. Explain the scope before confirmation and provide an undo or re-add path where possible.

Repair should be idempotent. If an update fails halfway through, a retry should reload the latest framework and product state rather than reuse a stale serialized credential.

## HomeKit, Matter, and Thread boundary

ThreadNetwork is infrastructure. A product that controls accessories still needs the supported HomeKit or Matter route. Keep these claims distinct:

| Claim | Owning route |
| --- | --- |
| Credential is stored for a Border Agent | ThreadNetwork/THClient |
| Border Router is configured | Product Border Router implementation |
| Border Router joined the Thread mesh | Physical Border Router/protocol evidence |
| Matter accessory was commissioned | MatterSupport or supported Matter flow |
| Home accessory can be controlled | HomeKit/Matter accessory APIs |
| Accessory is reachable now | Current accessory observation |

This separation prevents a polished setup screen from becoming an unsupported “all smart-home devices are online” promise.

## SwiftUI and Liquid Glass surface

Use one primary status card:

- title: selected Border Router;
- value: precise state, not “secure”;
- detail: last framework operation and last product observation;
- action: the one safe next step;
- disclosure: privacy and scope.

Examples of honest labels:

- “Credentials stored; router health not checked”
- “Waiting for Apple permission”
- “Update needed for this Border Agent”
- “Router active for the selected Thread network”
- “This build has the development capability only”

Respect accessibility and reduced-effects settings. If a custom glass surface is used, test it with opaque fallback colors and large text. Never hide a destructive removal action behind an animated transition.

## AI proposal contract

The model receives only a redacted typed summary:

~~~text
ThreadDiagnosticInput:
  selectedRouterLabel
  redactedBorderAgentID
  redactedExtendedPANID
  credentialAge
  frameworkState
  productState
  availableActions
~~~

The model returns:

~~~text
ThreadRepairProposal:
  explanation
  recommendedAction: inspect | update | retry | remove | contactSupport
  affectedBorderAgent
  userVisibleReason
  requiresCredentialAccess: false
~~~

The deterministic layer verifies that the recommended action exists, affects the selected Border Agent, does not change a preferred-network choice silently, and requires explicit approval. If the model is unavailable, render the fixed diagnostic rule.

## Minimum build and proof sequence

1. Compile a small target that imports ThreadNetwork.
2. Add and inspect the development capability.
3. Exercise availability and error branches with fixtures.
4. Run on a physical iPhone with a real Thread Resident and Border Router.
5. Test consent and denial.
6. Test store/update/delete for one Border Agent.
7. Test two Border Routers and a dataset mismatch.
8. Test same-team client sharing and cross-team boundaries.
9. Complete Apple’s User Experience and THClient test plans.
10. Request and verify the distribution entitlement before release claims.

## Sources

- [ThreadNetwork](https://developer.apple.com/documentation/threadnetwork)
- [Getting started with ThreadNetwork](https://developer.apple.com/documentation/threadnetwork/getting-started-with-threadnetwork)
- [Configuring a Border Router](https://developer.apple.com/documentation/threadnetwork/configuring-a-border-router)
- [Managing Thread network credentials](https://developer.apple.com/documentation/threadnetwork/managing-thread-network-credentials)
- [THClient](https://developer.apple.com/documentation/threadnetwork/thclient)
- [THCredentials](https://developer.apple.com/documentation/threadnetwork/thcredentials)
- [Manage Thread Network Credentials entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.networking.manage-thread-network-credentials)
- [Thread Test Plan - THClient API](https://developer.apple.com/apple-home/downloads/Thread-Test-Plan-THClient-API-R1.pdf)
- [HomeKit](https://developer.apple.com/documentation/homekit)
- [Matter](https://developer.apple.com/documentation/matter)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
