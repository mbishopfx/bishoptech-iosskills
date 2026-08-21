# ContactProvider proof matrix

ContactProvider crosses an app target, an extension process, a system-owned
Contacts projection, and user-controlled Settings. This matrix prevents a
successful manager call or a local contact list from being mistaken for system
consumer visibility.

## Evidence ladder

| Claim | Minimum evidence | Does not prove |
| --- | --- | --- |
| API is documented | Current Apple source and target availability review | That the target graph or extension compiles |
| Provider can be enabled | Host-app run with manager/domain and person approval | That a contact is visible in Phone/Mail |
| Full content is correct | Fixture with paging, generation marker, deterministic order, and completion | That later changes are delivered |
| Changes are correct | Anchor/update/delete/moreComing fixture and persisted history | That the system has displayed every change |
| Data is private | Projection field audit, redaction, Settings disable, deletion/logout test | That a copied consumer artifact is instantly erased |
| Extension is reliable | Host-not-running/termination/offline/migration run | That every OS budget or device behaves the same |
| AI enrichment is safe | Typed proposal, review, revision validation, and last-accepted publication | That a model can merge contacts universally |
| Release is ready | Signed app-plus-extension artifact and physical/system run | That a source file in the host target is an installed extension |

## Fixture pack

Use a versioned canonical dataset with stable provider identifiers:

| Fixture | Expected purpose |
| --- | --- |
| Empty domain | Initial content enumeration and empty-state behavior |
| Small deterministic set | Ordering, IDs, names, methods, and image projection |
| More contacts than one page | Paging, offsets, suggested batch size, and generation marker |
| Insert/update/delete between generations | Full snapshot versus change enumeration |
| Multiple updates to one item | Coalescing/history policy and latest stable projection |
| Delete-only batch | `didDelete` and anchor advancement |
| Unknown/pruned anchor | Error or full-reset recovery |
| Changes during full enumeration | Stable generation plus later change delivery |
| Missing image/invalid field | Redaction, fallback, and no-crash behavior |
| Offline canonical source | Last approved generation/stale state |
| Disabled provider | Host UI, Settings state, and publication fallback |
| Extension missing/unavailable | Manager error and app-owned fallback |
| AI label/merge proposal | Review, stale revision, reject, and last-accepted projection |

Do not use the person’s actual Contacts database as the only test fixture. Keep
provider data and native Contacts data distinct.

## Host-app manager evidence

Record a run for each manager operation:

- manager creation with default/named domain;
- extension not found and unsupported-feature errors;
- `enable()` before/after person approval;
- `isEnabled` after returning from Settings;
- `signalEnumerator(for:)` after a canonical revision;
- `disable()` and re-enable;
- `reset()` and rebuilt full enumeration;
- `invalidate()` and subsequent manager recovery;
- host app background/foreground and relaunch;
- network/account/migration unavailable states.

For every result, label whether it proves a host request, an extension run, a
system database update, or a real consumer surface. Never collapse those into a
single “synced” field.

## Full enumeration evidence

For each full-content fixture, record:

- requested collection/root container;
- initial page and all subsequent pages;
- generation marker identity and source snapshot;
- page offset/cursor and deterministic ordering;
- number of items per batch and suggested batch-size handling;
- observer page-completion calls and final completion;
- failure completion for source/serialization errors;
- item identifiers, field redaction, and image bounds;
- changes made during enumeration and their later change batch;
- extension termination and safe resume.

The same generation marker must represent the same source view across pages.
Compare the projected identifiers and fields to the expected fixture, not just a
count of returned items.

## Change enumeration evidence

| Test | Required observation |
| --- | --- |
| Start at initial/known anchor | Updates/deletes after the anchor only |
| Multiple batches | Suggested batch size respected; `moreComing` correct |
| Update | Stable identifier and complete approved projection |
| Delete | Stable identifier removed; no fabricated replacement |
| Finish | Highest completed anchor persisted only after batch success |
| Invalid anchor | Explicit error or reset/full enumeration |
| Failure mid-stream | No false success; recovery does not skip changes |
| Concurrent canonical edit | Deterministic ordering and later change delivery |
| Extension termination | System can resume from the last completed anchor |

An anchor is a cursor, not proof of system visibility. If the product claims
Phone/Mail behavior, run those system surfaces separately on a supported
physical device and record the exact configuration.

## Extension process evidence

Test the extension without a warm host app:

- launch from system enumeration;
- host app not running;
- host app logged out or canonical store locked;
- extension interrupted or terminated during a page;
- large data set and bounded image fields;
- offline/stale source;
- canonical schema migration or unavailable store;
- repeated requests and teardown;
- archive/install with the extension target present.

Record process logs without raw contact fields. A development extension run does
not prove Settings enablement or a real system consumer.

## Privacy and deletion evidence

Review the projection field-by-field:

- only app-managed contacts are included;
- sensitive fields/images are intentionally included or redacted;
- provider disable removes/restricts publication as designed;
- Reset does not delete canonical app records unless explicitly chosen;
- canonical deletion produces a provider delete;
- logout/account removal produces the documented projection state;
- app deletion removes the extension/provider data according to Apple’s route;
- diagnostics and analytics do not contain full names, phone numbers, emails,
  images, or private notes without an approved policy;
- consumer copies/caches are not claimed erased without evidence.

## AI and accessibility evidence

For AI-assisted contact review, capture:

- source record and revision;
- local model availability/route/version;
- fields supplied to the model and redaction;
- proposal and evidence context;
- duplicate/merge/label validation;
- accept/edit/dismiss/stale behavior;
- last-accepted publication and provider signal;
- manual/no-AI fallback.

Run provider setup/review tasks with VoiceOver, Dynamic Type, reduced effects,
increased contrast, keyboard/pointer, localization, and right-to-left layout.
Confirm that Enable, Refresh, Review, Disable, and Reset are reachable without
gestures and that “request sent” is not read as “system updated.”

## Physical/system/release evidence

The final evidence packet should include:

- source and target-SDK review;
- host-app and Contact Provider extension compile/build;
- simulator/state choreography where useful;
- physical device with provider Settings state;
- actual Contacts consumer behavior only if claimed;
- app-plus-extension signed archive inspection;
- privacy strings, capabilities, extension point, and resource membership;
- TestFlight/release install and relaunch;
- stale/offline/disabled/deleted/account states;
- performance and memory under representative provider data.

## Verification record template

~~~text
Host app / extension target / SDK / configuration:
Domain identifier and enabled state:
Canonical source/revision:
Projection fields and privacy policy:
Full enumeration fixtures/pages/generation markers:
Change anchors/updates/deletes/moreComing:
Manager and extension lifecycle evidence:
Settings/system-consumer evidence:
AI proposal/review/fallback evidence:
Accessibility evidence:
Physical-device/release/archive evidence:
Known limits and fallback:
Conclusion: documented / compiled / extension / device / system / release
~~~

## Sources

- [ContactProvider](https://developer.apple.com/documentation/contactprovider)
- [ContactProviderManager](https://developer.apple.com/documentation/contactprovider/contactprovidermanager)
- [ContactProviderExtension](https://developer.apple.com/documentation/contactprovider/contactproviderextension)
- [ContactProviderDomain](https://developer.apple.com/documentation/contactprovider/contactproviderdomain)
- [ContactItemEnumerating](https://developer.apple.com/documentation/contactprovider/contactitemenumerating)
- [ContactItemEnumerator](https://developer.apple.com/documentation/contactprovider/contactitemenumerator)
- [ContactItemContentObserver](https://developer.apple.com/documentation/contactprovider/contactitemcontentobserver)
- [ContactItemChangeObserver](https://developer.apple.com/documentation/contactprovider/contactitemchangeobserver)
- [ContactItemPage](https://developer.apple.com/documentation/contactprovider/contactitempage)
- [ContactItemSyncAnchor](https://developer.apple.com/documentation/contactprovider/contactitemsyncanchor)
- [Contacts](https://developer.apple.com/documentation/contacts)
- [ContactsUI](https://developer.apple.com/documentation/contactsui)
- [XCTest](https://developer.apple.com/documentation/xctest)
- [Performance Tests](https://developer.apple.com/documentation/xctest/performance-tests)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
