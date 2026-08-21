# ThreadNetwork and Border Router Proof Matrix

ThreadNetwork work needs evidence at several boundaries: Apple capability, signed target, consent, credential database, physical Border Router, Thread network, accessory protocol, and distribution. A compile result is only the first row.

## Evidence record

Record these fields before a test run:

| Field | Required value |
| --- | --- |
| App target | Bundle ID, target membership, build configuration |
| SDK/deployment | Xcode version, SDK, iOS deployment target |
| Capability | Manage Thread Network Credentials development or approved distribution state |
| Signed entitlement | Extracted entitlement value from the app/archive |
| Team identity | Team ID and relevant Info.plist configuration |
| Border Router | Manufacturer/product, model, firmware, Border Agent ID redaction |
| Thread Resident | HomePod mini, HomePod, or Apple TV model and software where used |
| Network | Wi-Fi/Ethernet topology, selected home, preferred-network state |
| Accessory | Matter/Home accessory model and commissioning state |
| Test device | iPhone/iPad model, OS build, locale, account state |
| Privacy | Credential redaction, logs, retention, upload audit |
| Evidence artifacts | Screen recording, console excerpt, signed artifact, test-plan result, and operator notes |

Never put network keys, PSKC values, active operational datasets, or raw credential objects in the evidence packet.

## Claim-to-evidence matrix

| Claim | Minimum evidence | Does not prove it |
| --- | --- | --- |
| ThreadNetwork is the selected route | Architecture decision naming Border Router/credential outcome | A product brief that only says “smart home” |
| App target has development capability | Xcode target capability and build settings | A source entitlement file not used by the target |
| Signed artifact carries entitlement | Extracted signed entitlements from the app | An Xcode checkbox or compile success |
| API is available to this target | Compile of the target at the selected SDK/deployment target | A current web page symbol alone |
| Preferred network is available | Physical-device call/result with a configured home | A hard-coded fixture or cached label |
| Preferred credentials consent works | Physical-device allow, deny, and cancel flows with Apple’s prompt | A mock permission Boolean |
| Team-scoped credentials can be read | Same-team app target retrieves the intended Border Agent record | An arbitrary credential fixture |
| Other-team isolation holds | Separate signed team/client attempt cannot modify/delete the first team’s record | A prose statement about team IDs |
| Credential store/update works | Real Border Agent, store result, reload/reconcile, and redacted logs | A successful in-memory object update |
| Credential deletion works | Delete result, reload, expected missing state, and product-state comparison | Deleting a local row only |
| Two routers share approved network state | Two physical Border Routers, per-agent records, same operational comparison, and device observations | Matching network names |
| Router joined Thread | Product or protocol join evidence and physical-network observation | Credentials stored in iCloud Keychain |
| Router is reachable | Product-owned health check from the intended network | An active UI badge |
| Matter/Home accessory works | Separate commissioning/control test on the supported accessory | ThreadNetwork API completion |
| AI route is local | Model availability trace, redacted input audit, and no-upload verification | A copy line saying “on-device AI” |
| AI repair proposal is safe | Typed fixture, deterministic validation, approval, commit, and undo | Free-form model text shown in a card |
| Release is eligible | User Experience and THClient test artifacts, Apple approval, distribution entitlement, archive/signing inspection | A development build on one phone |

## Development and signing checks

### Source and compile

- [ ] The target imports ThreadNetwork.
- [ ] The exact capability is documented in the target plan.
- [ ] API availability is checked in the selected Xcode SDK.
- [ ] The app handles missing capability/build states.
- [ ] Credential operations are isolated behind a testable adapter.
- [ ] No sample or recipe claims compile without a named target.

### Signed artifact

- [ ] Main app bundle ID and target membership are correct.
- [ ] Signed entitlement is present on the target that calls the API.
- [ ] App extensions or Border Router components have their own correct target configuration.
- [ ] Development versus distribution values are recorded.
- [ ] Team ID and Info.plist configuration are inspected.
- [ ] Archive contains the intended target graph.

## Consent and credential scenarios

Run each scenario on a physical device with a real configured Thread environment:

| Scenario | Expected evidence |
| --- | --- |
| No preferred network | Availability false or documented unavailable result; no consent prompt |
| Preferred network available | Availability true; rationale precedes consent |
| Person allows | Credential result scoped to the intended operation; secret redaction verified |
| Person denies | Typed denial state; no credential store/update attempted |
| Person cancels | Cancellation state; retry remains possible |
| Credential request fails | Error category and recovery; no stale success badge |
| Same-team Border Agent read | Intended credential record returned |
| Different Border Agent | Correct no-match/error result |
| Same-team client list | Only permitted team-scoped records appear |
| Cross-team modification/delete | Operation is rejected or does not affect the other team’s record |
| Update accepted | Store/update completes; last-modified state refreshes |
| Update rejected | Previous known state remains visible; retry reloads |
| Delete accepted | Framework record is absent after reload; physical product state is separately reported |

Verify that no raw credential bytes appear in unified logs, crash diagnostics, screenshots, clipboard history, share sheets, analytics, or AI prompts.

## Multi-router scenarios

Use at least two physical Border Routers where the product claims multi-router resilience:

- [ ] Add router A to the selected network.
- [ ] Add router B to the same network.
- [ ] Confirm per-agent identity and credential records.
- [ ] Reboot router A and observe recovery.
- [ ] Reboot router B and observe recovery.
- [ ] Update the active operational dataset and reconcile both agents.
- [ ] Make one agent stale or unavailable.
- [ ] Repair only the stale agent.
- [ ] Confirm a healthy agent is not reset as a side effect.
- [ ] Remove one agent and verify the other remains represented.
- [ ] Change the Wi-Fi/Ethernet path and record the resulting distinction between stored credentials and reachability.
- [ ] Restore the network and record whether the product rejoins automatically or requires action.

Do not record “coverage improved” or “always available” unless the product has a defined physical test protocol that supports the claim.

## HomeKit and Matter separation

If the product also supports Matter or HomeKit:

1. test Thread credential preparation;
2. test Border Router configuration;
3. test physical Thread join;
4. test accessory commissioning;
5. test accessory reachability and control;
6. test removal and re-commissioning.

A passing row must identify which layer passed. A Matter accessory’s success does not prove the app can manage every Thread credential, and a stored credential does not prove the accessory is commissioned.

## UI and accessibility matrix

Run the setup route with:

- VoiceOver from first screen through consent and return;
- Dynamic Type at the largest supported size;
- Voice Control using visible action names;
- Switch Control through every primary/recovery action;
- Reduce Motion;
- Reduce Transparency;
- right-to-left locale;
- long localized network names;
- keyboard and pointer on iPad where supported;
- dark and light appearance;
- interruption by backgrounding, lock, phone call, or system prompt.

Record:

- status label and accessibility value;
- focus order after a state change;
- whether the Apple prompt return restores focus;
- whether secret fields remain unavailable to accessibility and copy actions;
- whether a destructive removal action is understandable and reversible.

## AI safety matrix

| Test | Expected result |
| --- | --- |
| Model unavailable | Fixed diagnostic copy and normal deterministic route |
| Model receives redacted state | No credential fields in the serialized input |
| Model proposes update | Proposal is typed and reviewable |
| Model proposes another router | App verifies selected identity and asks the person |
| Model suggests network replacement | App blocks silent replacement and shows explicit network choice |
| Model returns malformed action | Deterministic validator rejects it |
| Person edits proposal | Edited value is validated again |
| Person declines | No ThreadNetwork mutation |
| Person approves | One scoped operation commits; result is observed |
| Operation fails | No false success; retry reloads current state |
| Undo/remove | Scope is shown and result is verified |

## Conformance and distribution packet

Apple’s getting-started documentation points to User Experience and THClient test plans, then a distribution-entitlement request. Preserve:

1. selected test-plan revision;
2. test setup and physical-device inventory;
3. signed development artifact;
4. test results and failure/retry notes;
5. UX evidence for consent, error, and recovery;
6. THClient evidence for retrieval, storage, deletion, and team boundaries;
7. privacy/redaction review;
8. Apple submission/approval communication;
9. approved distribution entitlement;
10. signed release archive and metadata review.

The presence of the PDF or a completed local checklist does not equal Apple approval. Record the actual status and date.

## Evidence vocabulary

Use these terms precisely:

| Term | Meaning |
| --- | --- |
| configured | App/project has the intended target and capability |
| signed | Extracted artifact carries the intended entitlements |
| available | Framework reported the selected availability result |
| consented | Person completed Apple’s consent path |
| stored | Framework accepted a credential store/update operation |
| joined | Product/physical test observed Thread membership |
| reachable | Product/device health test observed current reachability |
| commissioned | Accessory commissioning flow completed |
| controlled | Supported HomeKit/Matter command succeeded |
| distribution-ready | Apple entitlement and release artifact evidence exists |

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
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Organizing tests](https://developer.apple.com/documentation/xcode/organizing-tests-to-improve-feedback)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
