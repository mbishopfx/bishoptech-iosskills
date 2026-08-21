# App Intents transfer, ownership, and execution proof matrix

## Purpose

This matrix proves the interoperability and execution contracts that source
documentation cannot prove by itself.

A complete route needs separate evidence for:

- semantic transfer;
- current entity resolution;
- large collection efficiency;
- ownership and confirmation;
- relevance donation;
- process/target selection;
- foreground/background behavior;
- long-running progress;
- cancellation cleanup;
- undo registration and conflict behavior;
- errors, accessibility, privacy, and release artifacts.

## Evidence levels

| Level | What it can establish | What it cannot establish |
| --- | --- | --- |
| Source | Apple documents the protocol, type, or behavior | The selected SDK compiles or the OS invokes it |
| Compile | Target imports, signatures, macros, and availability resolve | Permission, process, system ranking, or physical behavior |
| Fixture/unit | Deterministic conversion, IDs, authorization, checkpoint, error, or undo logic | Siri/Shortcuts/System UI delivery or production account behavior |
| Simulator/UI | Layout, state transitions, navigation, accessibility instrumentation | Physical hardware, system ranking, cross-device continuation |
| Signed physical device | Real target/process/system handoff and device settings | Every OS/device/account/release configuration |
| Archive/release | Target membership, resources, entitlements, localization, distribution artifact | User behavior or future system ranking |

Record device model, OS build, app version/build, SDK/Xcode, account fixture,
network, language, accessibility settings, and artifact path for each test.

## Source and compile gates

| ID | Question | Pass evidence | Boundary |
| --- | --- | --- | --- |
| SRC-01 | Does the selected SDK expose IntentValueRepresentation? | Entity compiles with the selected Transferable representation | Do not infer destination-app use |
| SRC-02 | Does the selected SDK expose EntityCollection? | Parameter and ID/resolution calls compile | Do not infer memory/latency win without measurement |
| SRC-03 | Is OwnershipProvidingEntity available? | Availability and beta note recorded | Do not infer confirmation UI |
| SRC-04 | What does EntityOwnership mean? | Private/shared/public/unknown mapping documented | Do not infer authorization |
| SRC-05 | Is RelevantEntities appropriate? | Product context matches documented media/workout route | Do not use as generic ranking |
| SRC-06 | Which target can execute the intent/query? | allowedExecutionTargets and target membership compile | Do not infer process selection |
| SRC-07 | Which IntentModes combination is required? | supportedModes compiles and mode policy is documented | Do not infer foreground guarantee |
| SRC-08 | Is LongRunningIntent available? | Protocol and progress API compile | Do not infer unlimited runtime |
| SRC-09 | Is CancellableIntent available? | Cancellation handler compiles | Do not infer rollback |
| SRC-10 | Is UndoableIntent appropriate? | UndoManager path compiles and nil policy exists | Do not infer server reversal |
| SRC-11 | Are package/extension dependencies valid? | Main app/extension/package targets build | Do not infer system discovery |
| SRC-12 | Are AppIntentError cases localized? | Error route compiles and copy is reviewed | Do not leak internal diagnostics |

## Transfer representation tests

| ID | Scenario | Fixture | Expected result | Negative evidence |
| --- | --- | --- | --- | --- |
| XFER-01 | Place export | Entity with valid coordinates/name | PlaceDescriptor contains intended location semantics | Image or private payload used instead |
| XFER-02 | Missing coordinate | Entity with no location | Export throws conversion error; no mutation | Invented coordinate |
| XFER-03 | Coordinate bounds | Invalid latitude/longitude | Import rejected | Clamped value silently saved |
| XFER-04 | Place import draft | Valid PlaceDescriptor | App-owned draft contains normalized fields | Record silently committed |
| XFER-05 | Ambiguous import | Place with weak/no name | Review state asks for user choice | Fuzzy record overwrite |
| XFER-06 | Person export | Safe contact projection | IntentPerson contains approved fields | Private notes exported |
| XFER-07 | Person import | Missing stable identifier/handle | Conversion error or review | Wrong contact matched |
| XFER-08 | File transfer | User-approved file export | Correct UTType/file lifetime and cleanup | Temporary file leaks |
| XFER-09 | Bidirectional round trip | Export then import same fixture | Stable identity or explicit new-draft result | Duplicate record without user choice |
| XFER-10 | Stale entity | ID resolves to changed record | Export uses current authorized state | Old display cache exported |
| XFER-11 | Account mismatch | Entity belongs to account A, current B | No export or privacy-safe error | A data crosses account boundary |
| XFER-12 | Localization | Long/RTL names | Display and transfer retain semantic identity | Hard-coded English or truncation |

## EntityCollection tests

| ID | Scenario | Fixture | Expected result | Negative evidence |
| --- | --- | --- | --- | --- |
| COL-01 | Empty collection | Zero IDs | No-op result with no mutation | Empty interpreted as all |
| COL-02 | ID-only action | 500 IDs, operation needs only IDs | No eager full-entity hydration | All images/network data loaded |
| COL-03 | Hydrated action | Bounded IDs needing display | resolvedEntities called only when needed | Unbounded hydration |
| COL-04 | Duplicate IDs | Same ID repeated | Domain dedupes or reports deterministic count | Double mutation |
| COL-05 | Missing IDs | Deleted subset | Remaining records handled; missing count clear | Different records substituted |
| COL-06 | Unauthorized IDs | Mixed accounts | Unauthorized subset not changed | Account leakage |
| COL-07 | Partial failure | Mutation fails after prefix | Committed count/checkpoint truthful | “All succeeded” |
| COL-08 | Cancellation | Large collection canceled | Checkpoint and partial state recorded | Prefix lost or duplicated |
| COL-09 | Memory | 10k IDs | Bounded memory; no full model hydration | Parameter timeout/termination |
| COL-10 | Undo | Reversible collection mutation | Inverse covers committed IDs only | Undo restores uncommitted items |

## Ownership and confirmation tests

| ID | Scenario | Fixture | Expected result | Negative evidence |
| --- | --- | --- | --- | --- |
| OWN-01 | Private entity | No sharing/public status | No shared/public flag | Private called public |
| OWN-02 | Shared entity | Named collaborators/share active | shared flag/context | Stale share after revoke |
| OWN-03 | Public entity | Public visibility active | public flag/context | Marketing URL treated as ownership |
| OWN-04 | Combined state | Shared and public | Combined documented flags | One state hides the other |
| OWN-05 | Unknown state | Store still loading | unknown or action delayed | False private/public claim |
| OWN-06 | Delete shared | Shared record | Confirmation explains impact | Silent destructive action |
| OWN-07 | Revoke before commit | Access removed after prompt | Mutation rechecks and refuses | Prompt treated as authorization |
| OWN-08 | Revision conflict | Record edited elsewhere | No overwrite; review/retry | Old undo overwrites new edit |
| OWN-09 | Confirmation cancellation | User cancels | No domain mutation | Cancellation still commits |
| OWN-10 | Sensitive error | Unauthorized record | No private title or collaborator leak | Error reveals existence |

## Relevance and donation tests

| ID | Scenario | Fixture | Expected result | Negative evidence |
| --- | --- | --- | --- | --- |
| REL-01 | Workout media set | Bounded playable entities | update replaces previous context set | Donation appends stale items |
| REL-02 | Empty context | No suggestions | Empty update/clear removes suggestions | Old content remains active |
| REL-03 | Deleted item | Donated item deleted | Removed from context | Deleted title suggested |
| REL-04 | Access revoked | Subscription/share removed | Removed or refused | Unplayable/private item suggested |
| REL-05 | Context ends | Workout ends | Suggestions clear per policy | Four-week expiry relied on as control |
| REL-06 | Direct UI donation | Person starts action in app | Matching intent donation recorded | System-invoked action re-donated |
| REL-07 | No ranking claim | Donation succeeds | App says suggested, not guaranteed | Product promises surface placement |
| REL-08 | Privacy | Sensitive title | Donation/logs minimize data | Raw query/context retained |

## Target and dependency tests

| ID | Scenario | Fixture | Expected result | Negative evidence |
| --- | --- | --- | --- | --- |
| TARGET-01 | Main app open route | OpenIntent with UI | Main app target and navigation route | Extension touches window |
| TARGET-02 | Extension-safe mutation | Background-safe save | App Intents extension resolves dependencies | Main app singleton required |
| TARGET-03 | Widget query | Widget surface | Widget target can load minimal data | UI-only resource required |
| TARGET-04 | Default target audit | No explicit restriction | Behavior documented and safe | Accidental target selection |
| TARGET-05 | Package registration | Shared AppIntentsPackage | Main app discovers package intents | Package omitted from target |
| TARGET-06 | Extension discovery | App terminated | Extension registers intent/query | Main app launch incorrectly required |
| TARGET-07 | Missing dependency | Store unavailable | Localized actionable error | Crash/force unwrap |
| TARGET-08 | Account transition | Sign out during invocation | Old account cannot be used | Cached dependency leaks data |
| TARGET-09 | Resource loading | Extension process | Bundle/resource lookup succeeds | Main bundle assumption |
| TARGET-10 | Sendable boundary | Concurrent query/action | No data race/non-Sendable UI object | MainActor violation |

## Mode and current-runtime tests

| ID | Scenario | Fixture | Expected result | Negative evidence |
| --- | --- | --- | --- | --- |
| MODE-01 | Background-only action | Save setting | Completes without window | UI access crash |
| MODE-02 | Foreground open | Open detail | Main app opens current route | Background detail fabricated |
| MODE-03 | Dynamic foreground | Starts background then can foreground | Uses documented continuation | Duplicate mutation |
| MODE-04 | Cannot foreground | Restricted system state | Completes background or actionable error | Hangs waiting for window |
| MODE-05 | Current mode check | Fake foreground/background context | Branch is deterministic | Process inspection guessed |
| MODE-06 | Cold launch | App terminated | Route reconstructs state | Navigation singleton nil |
| MODE-07 | Warm launch | App already in detail | Handoff is idempotent | Duplicate screens |
| MODE-08 | Locked/limited state | Device/system restriction | Action remains safe or deferred | Secret displayed |
| MODE-09 | Repeated call | Same operation twice | Operation ID prevents double commit | Duplicate side effects |
| MODE-10 | Mode transition | Foreground changes during work | Checkpoint/recovery remains valid | Partial state lost |

## Long-running progress tests

| ID | Scenario | Fixture | Expected result | Negative evidence |
| --- | --- | --- | --- | --- |
| LONG-01 | Small job | 2 units | Completes with final progress | 100 percent before commit |
| LONG-02 | Large job | 500 units | Extended route used and progress updates | Ordinary timeout |
| LONG-03 | Progress cadence | Slow operation | Progress reported regularly | System cancels for silence |
| LONG-04 | Checkpoint | Terminate after unit 20 | Resume starts from safe checkpoint | Duplicate output |
| LONG-05 | Finalization | Export plus index update | Completion after both commit/finalization | Result claims success early |
| LONG-06 | Network loss | Upload interruption | Retry/resume/offline state | Partial file treated complete |
| LONG-07 | Memory pressure | Large media | Bounded buffers and cleanup | Unbounded memory |
| LONG-08 | Thermal/battery | Device under load | Graceful throttle/cancel policy | Performance promise from simulator |
| LONG-09 | Progress accessibility | VoiceOver/Dynamic Type | Phase and count understandable | Spinner-only feedback |
| LONG-10 | Release mode | Signed archive | Same checkpoint/resource route | Debug-only job path |

## Cancellation tests

| ID | Scenario | Fixture | Expected result | Negative evidence |
| --- | --- | --- | --- | --- |
| CANCEL-01 | Person cancels | Long task in Siri/Shortcuts | Task stops and checkpoint saves | Work continues silently |
| CANCEL-02 | Timeout | No progress or system limit | Timeout reason recorded | User cancellation message shown |
| CANCEL-03 | Before commit | Cancel at start | No domain mutation | Empty partial record |
| CANCEL-04 | After prefix | Cancel after 3/10 | Partial result truthful | Reports all or zero |
| CANCEL-05 | Child task | Multiple child operations | Children cancel/release | Detached work survives |
| CANCEL-06 | Capture/model resource | Media/model task | Resource released quickly | Camera/file/model lock remains |
| CANCEL-07 | Temporary file | Export canceled | Temporary file removed or resumable | Sensitive file remains |
| CANCEL-08 | Retry | Resume after cancel | Checkpoint is idempotent | Duplicated output |
| CANCEL-09 | Error during cleanup | Cleanup failure | Diagnostic/recovery state | Original cancellation hidden |
| CANCEL-10 | Accessibility | Cancellation spoken/visible | Person knows commit state | Silent ambiguous result |

## Undo tests

| ID | Scenario | Fixture | Expected result | Negative evidence |
| --- | --- | --- | --- | --- |
| UNDO-01 | Local title edit | Revision 4 -> 5 | Undo restores prior title | No inverse registered |
| UNDO-02 | Undo manager nil | Extension/background process | Safe no-undo completion or app history | Crash |
| UNDO-03 | Revision conflict | Record changed after action | Undo refuses/asks review | New edit overwritten |
| UNDO-04 | Collection action | Three IDs changed | Undo covers three committed IDs | Uncommitted ID restored |
| UNDO-05 | Delete/restore | Local reversible delete | Restore policy works | Data permanently lost unexpectedly |
| UNDO-06 | Server action | Remote mutation | Product does not promise unsupported undo | Fake local undo |
| UNDO-07 | System-originated action | App intent changes UI/data | App exposes normal undo path | System route ignored |
| UNDO-08 | Accessibility | VoiceOver/menu/keyboard | Undo discoverable and labeled | Gesture-only undo |
| UNDO-09 | Crash/relaunch | App restarts before undo | Policy is clear and state consistent | Half-registered inverse |
| UNDO-10 | Privacy | Prior state private | Undo metadata not leaked | Old text in system dialog/log |

## Error and privacy tests

| ID | Scenario | Fixture | Expected result | Negative evidence |
| --- | --- | --- | --- | --- |
| ERR-01 | Sign-in needed | No account | UserActionRequired.signin or app recovery | Generic failure |
| ERR-02 | Permission needed | Photos/location/Bluetooth denied | Specific permission error | Raw exception |
| ERR-03 | Account setup | Service not configured | Account setup action | Private token in error |
| ERR-04 | Conversion failure | Missing semantic field | Localized fixable explanation | Silent default |
| ERR-05 | Not found | Deleted entity | Search/current recovery | Different record opens |
| ERR-06 | Partial collection | Mixed results | Counts and retry/review | All-success claim |
| ERR-07 | Unsupported OS/device | Route unavailable | Ordinary app fallback | Feature appears functional |
| ERR-08 | Sensitive entity | Private fields | Minimal display/error/log | Query/prompt/title retained |
| ERR-09 | Localization | RTL/long strings | Errors fit and speak correctly | English fallback only |
| ERR-10 | Privacy reset | Sign-out/permission revoke | Donations/index/cache cleared | Old entity discoverable |

## Physical and release evidence

For a physical run:

1. install a signed archive on the named device;
2. use a deterministic account fixture;
3. invoke from each intended system surface;
4. record whether the app, App Intents extension, or widget extension ran;
5. verify transfer, current resolution, target, progress, cancellation, or undo;
6. repeat with sign-out, permission denial, deletion, and revision conflict;
7. enable VoiceOver, Dynamic Type, Reduce Motion, and Reduce Transparency;
8. capture only redacted screenshots/logs;
9. record OS/build/device/network/language/settings;
10. preserve the archive and target inspection.

Before release, inspect:

- target membership and allowed execution targets;
- App Intents package/extension registration;
- entitlements and usage descriptions;
- localized entity/error/confirmation strings;
- resource and model/file lifetime;
- background/cancellation checkpoint storage;
- privacy settings and index/donation cleanup;
- signed archive behavior;
- TestFlight/system-surface evidence where applicable.

## Evidence record template

~~~yaml
test_id: LONG-05
feature: long-running app intent export
app_version: 0.1.0
build: 43
sdk: Xcode-selected iOS SDK
device:
  model: physical-device-model
  os: iOS build
process: app-intents-extension
account: deterministic-test-account
network: wifi
fixture:
  item_count: 20
expected:
  progress_reaches_finalization: true
  checkpoint_is_resumable: true
  no_private_text_in_logs: true
actual:
  result: pass
artifacts:
  - path/to/redacted-log
  - path/to/archive-inspection
boundary: physical-system-and-release
notes: "No raw titles or identifiers persisted in the evidence log."
~~~

## Sources

- https://developer.apple.com/documentation/appintents/appentity
- https://developer.apple.com/documentation/appintents/defining-app-entities-for-your-custom-data-types
- https://developer.apple.com/documentation/appintents/intentvaluerepresentation
- https://developer.apple.com/documentation/appintents/entitycollection
- https://developer.apple.com/documentation/appintents/ownershipprovidingentity
- https://developer.apple.com/documentation/appintents/entityownership
- https://developer.apple.com/documentation/appintents/relevantentities
- https://developer.apple.com/documentation/appintents/donations-and-discovery
- https://developer.apple.com/documentation/appintents/intentmodes
- https://developer.apple.com/documentation/appintents/intentmodes/current
- https://developer.apple.com/documentation/appintents/intentsystemcontext/currentmode
- https://developer.apple.com/documentation/appintents/appintent/supportedmodes-5zhmb
- https://developer.apple.com/documentation/appintents/appintent/allowedexecutiontargets
- https://developer.apple.com/documentation/appintents/intentexecutiontargets
- https://developer.apple.com/documentation/appintents/longrunningintent
- https://developer.apple.com/documentation/appintents/cancellableintent
- https://developer.apple.com/documentation/appintents/undoableintent
- https://developer.apple.com/documentation/appintents/undoableintent/undomanager
- https://developer.apple.com/documentation/appintents/app-intents
- https://developer.apple.com/documentation/appintents/appintentspackage
- https://developer.apple.com/documentation/appintents/app-extension
- https://developer.apple.com/documentation/appintents/appintenterror
- https://developer.apple.com/documentation/appintents/appintenterror/permissionrequired
- https://developer.apple.com/documentation/appintents/appintenterror/useractionrequired
- https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass
- https://developer.apple.com/design/human-interface-guidelines/
