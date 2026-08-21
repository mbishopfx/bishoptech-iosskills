# SwiftData and CloudKit sync proof matrix

This matrix keeps local persistence, remote replication, iCloud account state, schema, conflict behavior, AI proposals, system projections, and release configuration separate. A local save or a successful development-container write is not proof of cross-device production sync.

## Evidence levels

| Level | Evidence | What it proves |
| --- | --- | --- |
| L0 | Official route and architecture review | The selected SwiftData, CKSyncEngine, or direct CloudKit responsibility is documented and the database scope is deliberate. |
| L1 | Deterministic model and reducer fixtures | Schema compatibility decisions, local state transitions, pending ledger behavior, conflict rules, deletion policy, and stale AI invalidation. |
| L2 | Preview, simulator, or local-process run | UI hierarchy, fixtures, accessibility identifiers, local persistence states, and non-network error surfaces. |
| L3 | Signed physical-device run | iCloud account state, entitlements, remote-change delivery, local persistence under interruption, and named device lifecycle behavior. |
| L4 | Two-device/account/container run | Cross-device edits, deletion races, conflict reconciliation, shared permissions, background delivery, and development schema behavior. |
| L5 | Production/release artifact | Promoted schema, signed container/environment, target capabilities, privacy declarations, migrations, extension projections, and release-build behavior. |

## Target and entitlement proof

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| The app can use CloudKit | Selected target compiles and signed entitlements contain the intended iCloud container | A source import or Xcode capability checkbox is not a signed-artifact proof. |
| SwiftData automatic sync is configured | iCloud + CloudKit + Background Modes/Remote notifications on the owning target | A widget or preview target’s capability does not configure the main app. |
| CKSyncEngine can schedule sync | CloudKit and Remote notifications entitlements plus a named private/shared database | A constructed engine does not prove account, network, or system scheduling. |
| Direct CloudKit route is authorized | Database scope, container, target, and environment are verified | Public/private/shared visibility remains a separate access test. |
| Production schema is ready | Schema promotion record, signed container environment, and migration fixture | Development schema success is not production readiness. |

## Local model and schema

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Records survive relaunch | Physical or simulator relaunch with save, edit, delete, and error recovery | An in-memory preview does not prove disk persistence. |
| Schema migration works | Fixture from every supported prior version, migration plan, invariant assertions, and failed-migration recovery | A model that opens once does not prove old user data is safe. |
| The model is CloudKit-compatible | Review of uniqueness, optional relationships, inverses, delete rules, field types, and development schema | Local model constraints are not automatically server constraints. |
| Large assets remain usable | Missing-file, moved-file, partial-download, deletion, and storage-pressure fixtures | A metadata record does not prove the asset is available. |
| The local store is safe without iCloud | No-account/local-only run with create/edit/read/delete behavior | Local availability does not imply remote backup or cross-device access. |

## SwiftData automatic sync

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| First sync works | Two signed devices on the intended account, development container, new record, relaunch, and remote projection | One device seeing its own local insert is not sync. |
| Remote edit arrives | Edit on device A, reconcile on device B, inspect freshness and status | A delivered notification does not prove the app applied the record. |
| Offline work reconciles | Disable network, create/edit/delete, reconnect, inspect each record and pending state | “Back online” does not prove every operation was acknowledged. |
| Account changes are safe | available/noAccount/restricted/temporarilyUnavailable/couldNotDetermine and return-to-app recheck | A permission prompt does not prove long-lived account state. |
| Schema deployment is safe | Development schema, production promotion, archive, migration, and rollback/recovery evidence | A development schema cannot be used as production evidence. |

## CKSyncEngine state and event contract

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| State restores after relaunch | Persist State.Serialization, terminate between events, relaunch with the latest serialization | An engine initialized with nil every launch can lose incremental state. |
| Pending changes are durable | Ledger maps local IDs to record IDs, operations, revisions, and retry state | Engine state alone cannot recreate app-owned record intent. |
| Fetched changes apply once | Duplicate/out-of-order/restart fixtures with transactional local application | A callback count is not an exactly-once domain guarantee. |
| Send batches are bounded | Requested scope, batch size, partial errors, retry, delete, and cancellation fixtures | One successful record save does not prove the batch contract. |
| Delegate ordering is safe | Serial-event reducer test and no recursive fetch/send from handleEvent | Async code that compiles can still re-enter the engine incorrectly. |
| Account/database failure recovers | Simulated unavailable account, zone error, throttling, retry-after, and return to ready | A transient error message is not a recovery policy. |

## Direct CloudKit and conflict proof

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Record zones are correct | Zone creation, record IDs, database scope, sharing, and deletion fixtures | A record type name is not a zone or access policy. |
| Change tokens are safe | Incremental fetch, moreComing, expired token/reset, and process restart | A remote notification payload may be coalesced or pruned. |
| Conflict merge is correct | Client/server/ancestor fixtures, field-specific policy, retry with current record version | Last-write-wins is not a product-neutral policy. |
| Deletion is correct | Offline delete versus remote edit, remote delete versus local edit, tombstone/recreate cases | A missing record does not explain user intent. |
| Partial failures are recoverable | Mixed success/failure save and delete results with persisted retry state | An operation-level success can hide per-record failures. |

## Design, accessibility, and AI

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Sync state is understandable | Text labels, pending/offline/conflict/error states, stale time, and no-color-only distinction | A spinner or icon does not explain local versus remote truth. |
| Conflict review is usable | Keep/replace/merge/cancel with undo or recovery, real fixtures, and error states | A side-by-side screenshot does not prove a completed task. |
| Liquid Glass is appropriate | Light/dark, reduced transparency, increased contrast, Dynamic Type, small/large screens, and hit-target review | Decorative translucency is not native hierarchy. |
| Accessibility works | VoiceOver, Voice Control, Switch Control, keyboard/pointer, Reduce Motion, RTL, and largest text | Labels alone do not prove the comparison task is accessible. |
| AI suggestions are bounded | Fixed source fixtures, typed output, provenance, stale invalidation, edit/reject, and confirmation | On-device execution does not make generated output domain truth. |
| Sensitive content is safe | Lock-screen/notification review, redaction, shared-screen review, logs/analytics audit | Private CloudKit storage does not justify exposing content in UI surfaces. |

## Extensions and system surfaces

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Widget projection is current enough | Snapshot/timeline, stale label, reload, deep link, extension termination, and offline state | A widget snapshot is not the main app’s live model. |
| Notification is safe | Settings, authorization, content redaction, scheduled request, foreground behavior, and action route | Scheduling is not delivery or attention. |
| App Intent is safe | Fresh entity resolution, authorization, confirmation, mutation result, and terminated-process run | An intent declaration is not proof of system invocation. |
| Live Activity is truthful | Start/update/end/stale and authority-loss tests on supported surfaces | A rendered Live Activity does not prove server freshness. |

## Performance and release

| Claim | Required evidence |
| --- | --- |
| Reconciliation is responsive | Named-device latency from local edit to pending state, remote apply, and UI update |
| Sync is energy-aware | Long offline/online run with battery, thermal, memory, and network measurements |
| Storage is bounded | Large assets, history/ledger retention, deletion, and storage-pressure tests |
| Release is configured | Archive entitlements, container IDs/environment, capabilities, privacy strings, extensions, schema record, and migration plan |
| Production behavior is known | TestFlight/release build against the production container with a controlled account and recovery log |

## Evidence packet

Record:

~~~text
feature:
target/bundle/build:
sdk/deployment target:
replication owner: SwiftData automatic / CKSyncEngine / direct CloudKit
database scope:
container identifier/environment:
zone and record mapping:
model/schema version:
cloudkit-compatible constraints:
local store and asset policy:
account states:
pending ledger:
state serialization persistence:
remote notification/background configuration:
offline fixtures:
conflict fixtures:
deletion fixtures:
ai source/provenance/review state:
extension/system projections:
accessibility settings:
device/account pair:
known failures:
claim supported:
claim not yet supported:
~~~

## Claim language

Use:

- “The signed app restored CKSyncEngine state after process termination and replayed the pending record-zone changes on the named device.”
- “Two physical devices on the development container reconciled an offline edit; the UI distinguished local save, pending upload, and remote acknowledgment.”
- “The conflict surface displayed local and remote values separately; the AI proposal remained editable and required confirmation.”
- “The archive contains the intended CloudKit container and remote-notification configuration; production schema promotion remains a separate release record.”

Avoid:

- “Cloud sync works” after one local save.
- “The app is backed up” because a development record appeared in CloudKit.
- “The notification delivered the change” from a scheduled request or push callback.
- “AI resolved the conflict” when it only generated a merge suggestion.
- “Works offline and syncs everywhere” without account, schema, device, conflict, and release evidence.

## Sources

- [CloudKit](https://developer.apple.com/documentation/cloudkit)
- [SwiftData](https://developer.apple.com/documentation/swiftdata/)
- [ModelContainer](https://developer.apple.com/documentation/swiftdata/modelcontainer)
- [ModelConfiguration](https://developer.apple.com/documentation/swiftdata/modelconfiguration)
- [Syncing model data across a person’s devices](https://developer.apple.com/documentation/swiftdata/syncing-model-data-across-a-persons-devices)
- [Deciding whether CloudKit is right for your app](https://developer.apple.com/documentation/cloudkit/deciding-whether-cloudkit-is-right-for-your-app)
- [Enabling CloudKit in your app](https://developer.apple.com/documentation/cloudkit/enabling-cloudkit-in-your-app)
- [CKSyncEngine](https://developer.apple.com/documentation/cloudkit/cksyncengine)
- [CKSyncEngine.Configuration](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/configuration)
- [CKSyncEngine.State.Serialization](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/state-swift.class/serialization)
- [CKSyncEngine.Event.StateUpdate](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/event/stateupdate)
- [CKSyncEngineDelegate](https://developer.apple.com/documentation/cloudkit/cksyncenginedelegate-1q7g8)
- [CKDatabase](https://developer.apple.com/documentation/cloudkit/ckdatabase)
- [CKRecord](https://developer.apple.com/documentation/cloudkit/ckrecord)
- [CKRecordZone](https://developer.apple.com/documentation/cloudkit/ckrecordzone)
- [CKRecordZoneNotification](https://developer.apple.com/documentation/cloudkit/ckrecordzonenotification)
- [Record changed error keys](https://developer.apple.com/documentation/cloudkit/record-changed-error-keys)
- [Setting up Core Data with CloudKit](https://developer.apple.com/documentation/coredata/setting-up-core-data-with-cloudkit)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
