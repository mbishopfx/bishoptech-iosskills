# Proof matrix: SwiftData, CloudKit, and CKSyncEngine sync

Use this matrix to distinguish local persistence, schema migration, remote
sync, multi-device convergence, and distribution evidence. Record the exact
app build, target, CloudKit container/environment, iCloud account state,
device pair, network, and test data for each result.

## Evidence levels

| Level | Proves | Does not prove |
| --- | --- | --- |
| S0 source | The official API, schema, entitlement, and lifecycle contract is recorded | That the project chose a compatible design |
| S1 build | SwiftData/CloudKit/CKSyncEngine code and deterministic fixtures compile | Entitlements, schema promotion, iCloud, network, or convergence |
| S2 configuration | Target capabilities, container, environment, schema, background mode, and signed entitlements align | Runtime sync, two-device behavior, or data correctness |
| S3 local runtime | A local save, fetch, delete, migration, and recovery path behaves on one device | Remote acceptance or multi-device convergence |
| S4 distributed runtime | Specific remote fetch/send, account, conflict, and two-device tests pass | Every region/account/network/build or App Store approval |
| S5 release | The exact archive/TestFlight/release build and production schema are exercised | A permanent guarantee against future SDK/service change |

Do not promote a `ModelContext.save()`, a `CKSyncEngine` callback, a sync badge,
or a simulator test to S4/S5 evidence.

## Architecture decision matrix

| Decision | Expected evidence | Failure interpretation |
| --- | --- | --- |
| Automatic SwiftData CloudKit sync selected | Documented model/container/configuration ownership | A custom engine must not also write the same record identity without a tested boundary |
| Custom `CKSyncEngine` selected | Record codec, stable IDs, zone/database scope, delegate, outbox, and state persistence design | A framework callback alone is not a custom sync implementation |
| Public database requirement | Explicit CloudKit public-database design | `CKSyncEngine` is not the route for the public database |
| Shared database requirement | Share/participant/permission design | Private-database assumptions can leak or reject operations |
| App account versus iCloud account | Separate identity and logout/switch policy | iCloud user ID must not silently become app authentication |

## Target and CloudKit configuration

| Check | Required evidence | Runtime follow-up |
| --- | --- | --- |
| iCloud capability | Target capability and signed entitlement | Fresh install can open the intended container |
| CloudKit container identifier | Explicit container ID in target/archive | Development and production environments are distinguished |
| Remote notifications | Background Modes/remote-notification entitlement | Device receives or reconciles remote changes after notification/refresh |
| CKSyncEngine database | Private/shared database is explicit | Account and permission behavior are tested |
| Container environment | Development schema versus production promotion record | TestFlight/release uses the intended environment |
| App Group | App/extension group entitlements agree if shared | Extension/app writes do not use an unowned store |
| No public-database misuse | Architecture audit | Stop before using CKSyncEngine for public data |
| Secret/token hygiene | Archive scan and redacted logs | No CloudKit tokens, record payloads, or private keys leak |

## SwiftData model and schema matrix

| Scenario | Expected result | Evidence |
| --- | --- | --- |
| Model container attached | `@Query` and environment context use the configured store | App composition and runtime store identifier |
| Missing container fixture | Test detects schema-less/in-memory context misuse | Failing fixture is visible, not silently accepted |
| Local insert/update/delete | Context transaction saves and reloads | Record ID, revision, relaunch/reopen result |
| Concurrent write attempt | One actor/context owns the write or conflict is surfaced | Actor/task trace and deterministic outcome |
| Model crossing actor boundary | ID/DTO crosses; live model does not | Compile/design review and test |
| CloudKit-compatible relationship | Optional relationship/inverse/delete policy is valid | Schema inspection and CloudKit Console result |
| Unique constraint assumption | Deduplication is explicit and tested | Collision fixture, no reliance on unsupported uniqueness |
| Development schema | Schema initialized and query/index support inspected | Container/environment and record types |
| Production schema | Compatible schema promoted before release | Production Console/release artifact |

## Migration matrix

| Scenario | Expected assertion | Required proof |
| --- | --- | --- |
| Fresh install at current schema | Container opens with empty or fixture data | Build/device/store configuration |
| Lightweight migration | Supported version pair migrates without data loss | Prior-store copy, before/after counts and field checks |
| Custom migration | Transform/default/relationship repair is deterministic | Fixture and migration log with schema versions |
| Interrupted migration | Original or safe recovery state remains | Kill/relaunch simulation on a copied store |
| Migration failure | App does not silently erase production data | Error screen, backup/export/recovery path |
| Migration plus CloudKit | Local result remains cloud-compatible | Development schema and sync recheck |
| Multiple previous versions | Each supported version is tested | Matrix of prior release stores |
| Release archive | Migration plan and current schema are in the signed build | Extracted build/settings evidence |

## Automatic SwiftData sync matrix

| Scenario | Expected result | Evidence |
| --- | --- | --- |
| iCloud account available | Local change is eventually mirrored | Two devices, account, container, timestamps/revisions |
| iCloud account unavailable | Local work remains usable; sync state is recoverable | Account status, offline edit, later reappearance |
| Network unavailable | No data loss or false “synced” label | Airplane/offline transition and retry |
| Remote notification delayed | Foreground refresh/reconciliation catches up | Notification condition and manual refresh trace |
| Device relaunch | Local data and pending state survive | Terminate/reopen and record comparison |
| Remote deletion | Deletion policy is deterministic | Delete fixture, tombstone/no-resurrection result |
| Relationship edit | CloudKit non-atomic behavior is safe | Order/retry fixture and resulting graph |
| Sync error | Local content remains and error is actionable | Error category, redacted diagnostic, retry |

## CKSyncEngine state and delegate matrix

| Scenario | Expected result | Evidence |
| --- | --- | --- |
| First initialization | Engine starts with `nil` state serialization | Fresh store and initialization trace |
| State update event | Serialization is persisted with related pending state | Data file/repository revision and relaunch load |
| Relaunch | Latest serialization is passed back to configuration | Exact serialized bytes/version metadata |
| Pending record save | State registers stable record-zone change | Record ID and outbox revision |
| Batch creation | Batch respects scope and 250-save/delete limit | Pending fixture and batch contents |
| No eligible pending changes | Delegate returns `nil` | No repeated/infinite send loop |
| Fetched database change | Zone metadata is updated | Zone ID/change result |
| Fetched record change | Record is decoded, validated, and applied idempotently | Repeated event fixture |
| Fetched deletion | Tombstone/delete policy prevents stale resurrection | Delete/reorder/relaunch test |
| Sent record changes | Only reported successes become confirmed | Partial success/failure fixture |
| Event ordering | Delegate does not trigger nested fetch/send | Trace and separate scheduled task |
| Manual sync | `fetchChanges`/`sendChanges` runs outside handler | User action and result state |

## Account and conflict matrix

| Scenario | Expected behavior | Evidence |
| --- | --- | --- |
| iCloud signed out | Engine becomes dormant/local-only; user data is isolated | Account event and local scope |
| iCloud signed in | New account initializes clean sync state | Account ID scope and no prior-account merge |
| Account switched while pending | Unsaved engine state/reset is handled without cross-account send | Pending fixture, transition trace |
| `serverRecordChanged` | Client/server/ancestor records are compared | Conflict payload with change tags |
| Field-independent edits | Deterministic field merge succeeds | Same record, separate fields, resulting revision |
| Same-field edits | User review or documented winner | Conflict sheet/action and revalidation |
| Delete versus edit | Tombstone/restore policy is explicit | Device-order permutations |
| Conflict changes during review | New conflict appears; old proposal is rejected | Revision mismatch fixture |
| Protected field | Server/domain authority wins | Entitlement/permission fixture |
| AI suggestion rejected | Canonical diff and deterministic choices remain | Model unavailable/invalid output test |

## Two-device convergence matrix

| Test | Device A | Device B | Pass condition |
| --- | --- | --- | --- |
| Sequential edit | Online edit/save | Open after sync | Same stable ID/content/revision |
| Offline edit | Edit while offline | Edit same record online | Policy result is deterministic and visible |
| Separate fields | Change title | Change color/metadata | Expected field merge without duplicate |
| Same field | Change title | Change title | Explicit winner/review; no silent overwrite |
| Delete versus update | Delete record | Update record | Tombstone policy is honored |
| Relaunch | Kill during pending sync | Open/reconcile | No lost/duplicated local work |
| Account switch | Sign out/switch account | Open old/new account | No cross-account private data |
| Schema migration | Upgrade one device | Keep prior version | Supported migration/sync boundary is documented |
| Repeated notification | Deliver duplicate change | Reconcile repeatedly | Idempotent final state |
| Large batch | Create >250 pending records | Sync | Bounded batches drain without skipped changes |

## SwiftUI and accessibility matrix

| Setting/path | Expected result |
| --- | --- |
| VoiceOver | Content, local save, remote confirmation, conflict/migration warning, and actions read in order |
| Dynamic Type | Rows/diffs wrap; actions remain reachable |
| Reduce Motion | Sync transitions remain understandable without shimmer/parallax |
| Reduce Transparency/increased contrast | Glass controls and status labels remain legible |
| Keyboard/pointer | Retry, Review, Keep, Combine, and Settings are focusable and named |
| Switch/Voice Control | Conflict and recovery actions can be invoked semantically |
| Offline mode | Useful content remains available; no false confirmation |
| Empty/partial data | Missing remote fields do not break the record or hide recovery |

## AI and privacy matrix

| Test | Expected result |
| --- | --- |
| Model available | Proposal is bounded, typed, source-revision-bound, and marked generated |
| Model unavailable | Canonical field diff and deterministic actions remain |
| Invalid proposal | No model output changes local/remote data |
| Prompt injection in record text | Text is treated as data, not instructions/tools |
| Account boundary | AI input excludes unrelated account/private records |
| Protected field | Model cannot propose ownership/entitlement/security changes |
| User acceptance | Deterministic re-fetch/revision validation runs before commit |
| Logging | No raw records, state serialization, tokens, or private keys are logged |

## Archive, TestFlight, and release matrix

Attach to the release review:

- exact archive/build/source revision;
- extracted `Info.plist` and signed entitlements;
- CloudKit container ID/environment and production-schema confirmation;
- iCloud/Remote notifications/App Group target ownership;
- migration fixtures from each supported prior release;
- physical two-device log with account, network, device OS, and test IDs;
- offline/account switch/conflict/delete/relaunch evidence;
- accessibility/reduced-effects screenshots or task log;
- open issues and fallback behavior.

TestFlight installation proves the selected build can install and run in the
tested environment. It does not prove schema promotion, every iCloud account,
two-device convergence in production, or App Store approval.

## Sources

- [SwiftData](https://developer.apple.com/documentation/swiftdata)
- [ModelContainer](https://developer.apple.com/documentation/swiftdata/modelcontainer)
- [ModelContext](https://developer.apple.com/documentation/swiftdata/modelcontext)
- [Concurrency support](https://developer.apple.com/documentation/swiftdata/concurrencysupport)
- [VersionedSchema](https://developer.apple.com/documentation/swiftdata/versionedschema)
- [SchemaMigrationPlan](https://developer.apple.com/documentation/swiftdata/schemamigrationplan)
- [Syncing model data across a person’s devices](https://developer.apple.com/documentation/swiftdata/syncing-model-data-across-a-persons-devices)
- [CloudKit](https://developer.apple.com/documentation/cloudkit)
- [CKSyncEngine](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5)
- [CKSyncEngineDelegate](https://developer.apple.com/documentation/cloudkit/cksyncenginedelegate-1q7g8)
- [CKSyncEngine.State](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/state-swift.class)
- [CKSyncEngine.Event.AccountChange](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/event/accountchange)
- [CKSyncEngine.Event.FetchedRecordZoneChanges](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/event/fetchedrecordzonechanges)
- [CKSyncEngine.RecordZoneChangeBatch](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/recordzonechangebatch)
- [CKError.serverRecordChanged](https://developer.apple.com/documentation/cloudkit/ckerror/serverrecordchanged)
- [NSPersistentCloudKitContainer](https://developer.apple.com/documentation/coredata/nspersistentcloudkitcontainer)
- [Configuring iCloud services](https://developer.apple.com/help/account/configure-app-capabilities/icloud)
- [Configuring background execution modes](https://developer.apple.com/documentation/xcode/configuring-background-execution-modes)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
