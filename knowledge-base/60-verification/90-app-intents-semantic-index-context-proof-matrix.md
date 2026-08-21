# App Intents semantic index, in-app search, onscreen context, and identity proof matrix

## Purpose

This matrix separates source understanding, compilation, local behavior,
system invocation, physical-device behavior, accessibility, privacy, and
release evidence for App Intents semantic indexing and in-app search.

The route is not complete when an entity conforms to IndexedEntity. Completion
requires proof that:

- the index is fresh and repairable;
- Spotlight/Siri can discover or hand off search;
- the app re-resolves current authorized records;
- visible entity annotations follow the UI;
- custom elements match their rendered bounds;
- stable IDs work across devices without bypassing authorization;
- Liquid Glass and accessibility states remain usable;
- the archived target contains the intended routes and privacy configuration.

## Evidence rule

For each row, record:

- test ID;
- app build and commit/working-tree state;
- Xcode and selected SDK;
- OS/device model and OS build;
- account, network, language, and accessibility settings;
- fixture IDs and expected results;
- actual result;
- artifact path, screenshot, console excerpt, or test report;
- whether the evidence is source, compile, simulator, physical, or release proof.

A simulator screenshot can prove layout. It cannot prove Siri, Spotlight, Apple
Intelligence, cross-device continuation, or a physical system handoff unless the
specific behavior is documented as simulator-supported and independently
verified.

## Source and availability matrix

| ID | Question | Fixture/setup | Expected evidence | Boundary |
| --- | --- | --- | --- | --- |
| SRC-01 | Does the selected SDK document IndexedEntity? | Open the SDK docs/interface | Official URL, SDK symbol, availability note | Source only |
| SRC-02 | Does the selected SDK document IndexedEntityQuery? | Inspect protocol requirements | Exact subset/all reindex signatures recorded | Source/compile |
| SRC-03 | Is system.searchInApp available? | Inspect App Intents schema completion | Current schema compiles or is explicitly beta-gated | Source/compile |
| SRC-04 | Is the old system.search route deprecated? | Inspect migration/deprecation note | Adapter uses current schema | Source only |
| SRC-05 | Are SwiftUI entity modifiers available? | Compile a minimal view | Modifier signatures match selected SDK | Compile only |
| SRC-06 | Is AppEntityUIElement available for the target? | Compile custom-element adapter | Target-specific availability and initializer recorded | Compile only |
| SRC-07 | Is SyncableEntity available and appropriate? | Review stable identity model | ID proof and availability note | Design/source |

## Entity projection tests

| ID | Scenario | Fixture | Pass criteria | Failure evidence |
| --- | --- | --- | --- | --- |
| ENT-01 | Display representation | One record with title, type, context, thumbnail | Localized type/title/context are concise and truthful | Long/private field appears |
| ENT-02 | Missing thumbnail | Same record without image data | Text remains complete and accessible | Card depends on image |
| ENT-03 | Long localized title | Long title and German/Arabic locale | Layout wraps/truncates without losing identity | Fixed-height clipping |
| ENT-04 | Sensitive record | Private note or restricted category | Projection omits or excludes it according to policy | Sensitive text indexed |
| ENT-05 | Deleted record | Entity ID exists in fixture, record deleted | Query returns no entity or clear unavailable recovery | Different record opens |
| ENT-06 | Signed-out account | Index has account A, app signs out | A's private entity is removed or refused | Old title/subtitle visible |
| ENT-07 | Shared record revoked | Shared access removed | Query and OpenIntent reject it | Revoked record remains openable |
| ENT-08 | Duplicate ID attempt | Two records with same projected ID | Build/index layer rejects or resolves deterministically | Duplicate system results |

## Index lifecycle tests

| ID | Scenario | Fixture | Pass criteria | Failure evidence |
| --- | --- | --- | --- | --- |
| IDX-01 | Initial import | 250 eligible records, 25 ineligible | Eligible records indexed in bounded batches | UI blocked or private rows indexed |
| IDX-02 | Initial import cancellation | Cancel after batch 2 | Checkpoint recorded; repair can resume | Partial state reported complete |
| IDX-03 | Insert | New eligible record | One result with the new stable ID | No donation or duplicate |
| IDX-04 | Update title | Same ID, changed title | Old projection replaced; ID unchanged | Duplicate old/new result |
| IDX-05 | Update searchable metadata | Same ID, changed category/keywords | Search sees the new metadata after refresh | Stale terms persist |
| IDX-06 | Archive | Record archived | Record removed or policy-specific hidden state | Archived record still discoverable |
| IDX-07 | Delete | Record deleted | Entity removed from named index | Old card opens another record |
| IDX-08 | Privacy toggle off | User disables system discovery | Eligible private entries removed | Toggle has no effect |
| IDX-09 | Privacy toggle on | User enables discovery | Only current eligible records reindexed | Old account data returns |
| IDX-10 | Sign-out | Account A -> no account | Account A entries withdrawn promptly | A data remains discoverable |
| IDX-11 | Sign-in | No account -> account B | Only B entries indexed | A/B contamination |
| IDX-12 | Index version change | Projection v1 -> v2 | Repair/reindex marker runs | Mixed schema silently persists |
| IDX-13 | Named index isolation | Two named indexes in debug fixture | Only intended index changes | Default/global index assumed |
| IDX-14 | System repair subset | System requests selected IDs | Only requested current authorized IDs reindexed | Entire private store exported |
| IDX-15 | System repair all | All reindex request | Bounded stream, accurate description, current records | Unbounded memory or stale schema |

## Search and handoff tests

| ID | Scenario | Fixture | Pass criteria | Failure evidence |
| --- | --- | --- | --- | --- |
| SRCH-01 | Indexed lexical query | Index has title/category terms | Expected entity appears | Index metadata absent |
| SRCH-02 | Indexed semantic query | Natural-language query for a safe category | Relevant entity appears when system supports semantic search | App claims ranking guarantee |
| SRCH-03 | Index stale title | Index old title, store new title | Open route displays current title | Old title treated as truth |
| SRCH-04 | No indexed results | Safe catalog not indexed | In-app search route remains available | Product becomes unreachable |
| SRCH-05 | system.searchInApp string | Siri supplies a query string | App screen contains the same query | Query silently rewritten |
| SRCH-06 | Search scope | Projects scope | Search service receives projects scope | Scope ignored |
| SRCH-07 | Unknown scope | Future/invalid scope | App falls back or shows honest unsupported state | Wrong data scope searched |
| SRCH-08 | Empty criteria | Empty/whitespace criteria | Search screen opens with editable field | Hidden mutation or fake results |
| SRCH-09 | Large catalog | 100k-record fake server/local fixture | Handoff opens quickly; results paginate/live query | Full index required |
| SRCH-10 | Offline search | Network disabled | Local result/offline state is accurate | Server success implied |
| SRCH-11 | Signed out | Query for old account content | Account recovery, no private rows | Old content exposed |
| SRCH-12 | Cold launch | App terminated before system handoff | Main app opens on search route | Extension/main-window crash |
| SRCH-13 | Warm launch | App already showing detail | Search route replaces/presents predictably | Duplicate navigation stack |
| SRCH-14 | Repeated invocation | Same criteria twice | Idempotent state, no duplicate side effects | Duplicate mutation/navigation |
| SRCH-15 | App extension target | Intent declared in shared framework | Main app target is allowed | Extension tries to own foreground UI |

## OpenIntent tests

| ID | Scenario | Fixture | Pass criteria | Failure evidence |
| --- | --- | --- | --- | --- |
| OPEN-01 | Current record | Existing authorized ID | Detail opens current record | Stale projection shown |
| OPEN-02 | Deleted ID | Record removed after indexing | Unavailable/search recovery | Different record opens |
| OPEN-03 | Account mismatch | ID belongs to account A, current B | Privacy-safe rejection | A title disclosed |
| OPEN-04 | Shared access revoked | User loses share | Rejection with current explanation | Record remains openable |
| OPEN-05 | Store migration | App store not ready | Loading/retry/unavailable route | Crash or dead screen |
| OPEN-06 | Side effect check | OpenIntent selected | No send/delete/purchase occurs | Hidden mutation |
| OPEN-07 | Deep-link repeat | Same ID opened twice | One coherent detail route | Duplicate pushed screens |

## SwiftUI list and card context tests

| ID | Scenario | Fixture | Pass criteria | Failure evidence |
| --- | --- | --- | --- | --- |
| UI-01 | Single card annotation | One current AppEntity | Modifier identifies the card's ID | Container gets wrong ID |
| UI-02 | Row reorder | Sort order changes | Each row retains its own current ID | Previous cell ID retained |
| UI-03 | Row filter | Filter hides/shows entities | Hidden row is absent; visible row ID correct | Stale annotation |
| UI-04 | Insert at top | New row inserted | Existing rows remain correctly mapped | Index-based identity bug |
| UI-05 | Delete selected row | Selected record deleted | Selection clears or recovers | Deleted entity still annotated |
| UI-06 | Selection type | Typed List selection | System context reports intended entity type | Selection is ambiguous |
| UI-07 | Loading placeholder | Store loading | Placeholder has no false entity ID | Fake ID sent to system |
| UI-08 | Account switch | Account A list -> B list | All annotations reflect B | A entity remains |
| UI-09 | VoiceOver | VoiceOver on | Label/type/state match entity | Silent or contradictory row |
| UI-10 | Dynamic Type | Accessibility size large | Row and toolbar remain usable | Text/action clipping |
| UI-11 | Reduce Motion | Reduce Motion on | Handoff/highlight has no disorienting animation | Motion ignored |
| UI-12 | High contrast | Increased contrast on | Controls and selection remain obvious | Glass is only state cue |

## Custom AppEntityUIElement tests

| ID | Scenario | Fixture | Pass criteria | Failure evidence |
| --- | --- | --- | --- | --- |
| CANVAS-01 | Static element | One diagram node | Bounds align with node | Offset overlay |
| CANVAS-02 | Zoom | Canvas scales 2x | Bounds scale with rendered node | Stale coordinates |
| CANVAS-03 | Pan | Canvas moves | Element bounds move with content | Context points elsewhere |
| CANVAS-04 | Selection | Node selected | State and accessibility update | State remains stale |
| CANVAS-05 | Subelements | Group with child nodes | Subelement IDs are meaningful and bounded | Decorative noise |
| CANVAS-06 | Offscreen | Node moves offscreen | Element is removed/hidden | Invisible entity remains |
| CANVAS-07 | Touch hit test | Tap near node | Accessible action matches visible target | System identifies unreachable mark |
| CANVAS-08 | Privacy | Sensitive diagram node | No secret payload in UI element | Raw data exported/logged |
| CANVAS-09 | Alternate list | Custom canvas unavailable | List/inspector still exposes entity | Canvas is only access path |

## Cross-device and stable identity tests

| ID | Scenario | Fixture | Pass criteria | Failure evidence |
| --- | --- | --- | --- | --- |
| ID-01 | Stable server ID | Same record on device A/B | Entity resolves to same record | New local record created |
| ID-02 | Local/stable mapping | Local ID differs on device B | Stable maps to B's local record | Local integer assumed global |
| ID-03 | Account mismatch | Same stable ID, different account | No private result | Stable ID treated as bearer token |
| ID-04 | Record deleted remotely | Delete on A, continue on B | B shows unavailable/search recovery | Old card opens |
| ID-05 | Share revoked | Revoke before B open | B rejects current authorization | Access persists |
| ID-06 | Offline B | Stable ID known, data not synced | Honest pending/offline route | Fake current detail |
| ID-07 | Sign out B | Sign out before continuation | Old private mapping cleared | Old metadata remains |
| ID-08 | Local-only entity | No stable ID | Current-device route only | App claims cross-device support |
| ID-09 | Migration | Stable ID schema changes | Migration preserves identity or safely reindexes | Duplicate records |
| ID-10 | Physical continuation | Two supported devices, same account | Siri/system continuation opens current detail | Simulator-only result |

## Accessibility and design evidence

| ID | Scenario | Fixture | Pass criteria | Failure evidence |
| --- | --- | --- | --- | --- |
| A11Y-01 | VoiceOver system handoff | VoiceOver on | Result and destination are understandable | Visual-only identity |
| A11Y-02 | VoiceOver custom element | Canvas plus element | Name, value, action, bounds make sense | No accessible path |
| A11Y-03 | Dynamic Type | Largest supported size | Search/result layout remains navigable | Fixed glass height |
| A11Y-04 | Reduce Transparency | Setting enabled | Search shell readable without glass dependence | Contrast collapse |
| A11Y-05 | Reduce Motion | Setting enabled | Handoff and selection transitions adapt | Motion causes disorientation |
| A11Y-06 | RTL | Arabic/Hebrew fixture | Title/context/order are correct | Hard-coded direction |
| A11Y-07 | Keyboard/pointer | iPad/Mac Catalyst if supported | Search, scope, rows, back route operable | Touch-only action |
| A11Y-08 | Privacy speech | Public environment fixture | Spoken text avoids unnecessary sensitive metadata | Private subtitle read aloud |

## Physical system-invocation evidence

Capture a signed, reproducible run for each supported path:

1. install the archive on the named physical device;
2. sign in with a test account containing deterministic fixtures;
3. create/update/delete a record;
4. wait for or trigger index refresh according to the product route;
5. invoke Spotlight/Siri/Apple Intelligence using a natural query;
6. confirm the entity or in-app handoff appears;
7. open the result and verify current detail;
8. repeat after deletion, sign-out, and permission revocation;
9. capture the app build, OS build, device, account mode, network, and settings;
10. store screenshots/logs without private fixture content.

For onscreen context, scroll, filter, reorder, and update the visible list before
invoking the system. For custom elements, zoom/pan and select a different item.
For cross-device proof, use two devices or the supported Apple system path and
record both sides.

Do not report a unit test or simulator result as Siri/Spotlight proof.

## Archive and release evidence

Before shipping:

- [ ] App Intents target membership is correct.
- [ ] Main-app execution target is present for in-app search.
- [ ] Availability checks and fallbacks are present.
- [ ] Named index identifier and schema version are documented.
- [ ] Privacy settings and sign-out removal are tested.
- [ ] Local/stable ID migrations are archived with the release.
- [ ] Display strings and index fields are localized.
- [ ] Entitlements, capabilities, and Info.plist privacy declarations are
      inspected.
- [ ] Archive contains the intended app and extension targets.
- [ ] No debug-only fake store or navigation singleton is active.
- [ ] The release build is installed and the affected route is exercised.
- [ ] Physical system evidence is stored separately from compile evidence.
- [ ] Reindex/repair instructions exist for an update that changes metadata.

## Evidence record template

~~~yaml
test_id: SRCH-05
feature: system.searchInApp
app_version: 0.1.0
build: 42
sdk: Xcode-selected iOS SDK
device:
  model: physical-device-model
  os: iOS build
account: deterministic-test-account
network: wifi
accessibility:
  voice_over: false
  dynamic_type: default
  reduce_motion: false
fixture:
  query: "launch brief"
  scope: "documents"
expected:
  query_preserved: true
  scope_preserved: true
  current_entity_opens: true
actual:
  result: pass
artifacts:
  - path/to/screenshot-or-test-log
boundary: physical-system-handoff
notes: "No private record text in logs."
~~~

## Sources

- https://developer.apple.com/documentation/appintents/indexedentity
- https://developer.apple.com/documentation/appintents/indexedentityquery
- https://developer.apple.com/documentation/appintents/spotlight
- https://developer.apple.com/documentation/appintents/making-app-entities-available-in-spotlight
- https://developer.apple.com/documentation/appintents/showinappsearchresultsintent
- https://developer.apple.com/documentation/appintents/appschema/systemintent/searchinapp
- https://developer.apple.com/documentation/appintents/providing-contextual-cues-to-apple-intelligence-and-siri
- https://developer.apple.com/documentation/appintents/appentityuielement
- https://developer.apple.com/documentation/appintents/syncableentity
- https://developer.apple.com/documentation/appintents/syncableentityidentifier
- https://developer.apple.com/documentation/appintents/adopting-app-intents-to-support-system-experiences
- https://developer.apple.com/documentation/swiftui/view/appentityidentifier%28_%3A%29
- https://developer.apple.com/documentation/swiftui/view/appentityidentifier%28forselectiontype%3Aidentifier%3A%29
- https://developer.apple.com/documentation/swiftui/view/appentityuielements%28_%3A%29
- https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass
- https://developer.apple.com/documentation/swiftui/navigation
