# CloudKit, CKSyncEngine, and SwiftData synchronization

## Scope

Cross-device data is not one Apple API. The local model, the replication owner, the iCloud account, the CloudKit database scope, the schema, the background delivery path, and the conflict policy are separate parts of the feature. Treating them as one “sync” switch makes a UI look finished while leaving the hardest states undefined.

This deep dive covers three documented Apple routes:

| Product need | First route | What the app still owns |
| --- | --- | --- |
| Local-first SwiftData records should follow the same person across Apple devices | SwiftData automatic CloudKit sync | CloudKit-compatible schema, capabilities, migrations, account/offline UI, deletion, and product meaning of conflicts |
| App-owned local records should replicate to a private or shared CloudKit database with explicit batching | CKSyncEngine | Record mapping, pending-change ledger, applying events, state serialization, merge policy, and recovery |
| Public data, custom queries, or record-level control | Direct CKDatabase and CKRecord | Zones, subscriptions, change tokens, retries, conflict resolution, access policy, and offline replay |

Apple’s CloudKit decision guide also distinguishes document storage, Core Data mirroring, CKSyncEngine, and direct CloudKit operations. Choose the smallest boundary that preserves the product’s data contract. Do not layer two independent replication authorities over the same records.

## The four truths in a sync feature

Keep these values separate in the domain model and in the UI:

1. **Local truth** — the record the current process can read and edit.
2. **Pending work** — local changes not yet acknowledged by the selected remote route.
3. **Remote truth** — the latest CloudKit record or change batch known to this device.
4. **Review state** — a conflict, missing account, schema problem, denied access, or stale AI proposal that needs a product decision.

A useful state machine is:

~~~text
local
  -> pendingUpload
  -> syncAcknowledged
  -> local

local -> offline
local -> accountUnavailable
pendingUpload -> retryAfter
remoteChange + localEdit -> conflictReview
remoteDelete + localEdit -> deletionReview
any -> schemaOrContainerError
~~~

The local record should remain usable when the network or iCloud account is unavailable unless the product explicitly requires remote authorization for the operation. “Saved locally” and “synced to iCloud” are different claims.

## Route A: SwiftData automatic CloudKit sync

SwiftData’s managed CloudKit route is appropriate when the app already wants SwiftData models, local querying, and a system-managed replica across a person’s devices. Apple documents the route as adding the iCloud capability and Background Modes with Remote notifications, then defining a CloudKit-compatible schema.

### Required project gates

1. Add the iCloud capability, enable CloudKit, and select the intended container.
2. Add Background Modes and enable Remote notifications for remote-change delivery.
3. Confirm that the owning app target has the capabilities; a widget or preview target does not inherit the app’s entitlements.
4. Decide whether automatic container discovery is sufficient or whether ModelConfiguration.CloudKitDatabase.private(_:) should select a specific container.
5. Initialize and inspect the development schema before any production promotion.
6. Test a signed app with an available iCloud account, then test no-account, restricted, and temporarily unavailable states.

ModelContainer owns schema, contexts, and storage configuration. If the app’s entitlements include CloudKit, SwiftData can automatically handle syncing the persisted storage across devices. The container does not make a schema compatible, make a record conflict-free, or guarantee that a remote notification is delivered promptly.

### CloudKit-compatible model constraints

Apple’s SwiftData sync guidance calls out constraints that should shape the model before the CloudKit schema is initialized:

- CloudKit cannot enforce SwiftData’s @Attribute(.unique) option in the automatic sync route.
- CloudKit requires relationships to be optional because relationship changes are not atomically processed.
- Define an explicit inverse when SwiftData cannot reliably infer it.
- CloudKit does not support Schema.Relationship.DeleteRule.deny for this route.
- CloudKit processes changes concurrently and at opportunistic times; local validation and deduplication still belong to the app.

If a local invariant is essential, make it an app-owned validation or merge rule, or choose an architecture with an explicit server-side authority. Do not assume that a local model constraint becomes a CloudKit guarantee.

### Schema and release boundary

Development schema initialization and production schema deployment are different steps. CloudKit schemas are additive after promotion, so a production migration plan must be written before shipping a model change. Keep fixtures for:

- a record created by every supported prior app version;
- a record with missing optional fields;
- a record with an unreviewed AI-derived value;
- a record whose related asset was deleted or moved;
- a record edited on two devices;
- a record deleted while another device is offline.

Do not call a successful development-container write “production sync.” Verify the signed container identifier, environment, schema deployment, target entitlements, and physical-device/account route separately.

## Route B: CKSyncEngine

CKSyncEngine manages synchronization of local and remote record data. Apple documents it for a person’s private or shared database, not the public database. The app supplies record data through CKSyncEngineDelegate, handles sync events, and persists the engine’s opaque state.

### Initialization contract

Create the engine early in the app’s launch process with:

- the private or shared CKDatabase;
- the latest persisted CKSyncEngine.State.Serialization, or nil on first initialization;
- a delegate that owns record mapping and event application.

The engine can schedule periodic work when system conditions are good, but the schedule is indeterminate. Network, battery, iCloud account, and system policy all matter. If the product has a specific freshness requirement, use the documented manual fetch/send operations at a user-visible boundary and represent the result honestly.

The state serialization is not optional app bookkeeping. Apple explicitly says that the engine does not persist it to disk. Persist the newest serialization alongside the local changes that the serialization describes, then restore it on the next launch.

### Delegate and event ordering

The delegate’s responsibilities are intentionally split:

| Delegate seam | Responsibility |
| --- | --- |
| handleEvent(_:syncEngine:) | Apply fetched database/zone/record changes, persist state updates, record account or error transitions, and update local projections |
| nextRecordZoneChangeBatch(_:syncEngine:) | Return a bounded batch of saves/deletes for the scope requested by the engine |
| nextFetchChangesOptions(_:syncEngine:) | Customize fetch behavior only when the product has a measured reason to do so |

Apple documents delegate event delivery as serial. Do not call engine methods from handleEvent if that call can cause more delegate events; enqueue a separate action after the current event has finished. This avoids reentrancy and preserves the engine’s ordering contract.

The event reducer should treat these categories as separate:

- state update: persist the new serialization;
- fetched changes: apply remote records/deletions transactionally;
- sent changes: clear only the local work that the server acknowledged;
- failed record saves/deletes: preserve retry or conflict metadata;
- account/database/zone failures: move the feature to an honest unavailable or recovery state.

Persist the serialization and apply fetched changes with a recoverable ordering. If a process terminates between those operations, the next launch must be able to reconcile rather than silently skip a change.

### Pending-change ledger

The engine asks the app for records, but it does not know how a domain object maps to the local store. Keep an app-owned ledger with at least:

| Field | Reason |
| --- | --- |
| local persistent identifier | Re-fetch the current model in the correct context or actor |
| CloudKit database and zone | Avoid applying a private record to a shared projection |
| record ID and type | Stable mapping for send/delete/retry |
| operation | Save, delete, zone creation, or zone deletion |
| local revision | Reject stale work after a newer edit |
| source/provenance | Explain whether the value came from the person, import, or AI proposal |
| retry state | Backoff, failure category, next eligible attempt |
| conflict state | Client/server/ancestor comparison or needs-review marker |

Do not store only a serialized engine state and assume it can recreate deleted local intent. The engine state and the app’s pending record mapping are one recovery unit.

## Route C: direct CloudKit operations

Use direct CKDatabase and CKRecord operations when the app needs a public database, custom queries, explicit record zones, or record-level control that the higher-level routes do not provide. This route is more intricate because the app owns:

- database scope and access decisions;
- custom record-zone creation and deletion;
- subscriptions and change-token persistence;
- fetching changes and handling moreComing;
- retry and backoff;
- account changes and remote-notification hints;
- partial errors;
- conflict comparison and retry;
- local/offline reconciliation.

CloudKit record-zone notifications are hints that a zone changed. Apple warns that notifications can be coalesced or omit data; fetch the changes rather than treating the notification payload as the record itself. For a public database, custom record zones are not available, which is another reason not to substitute direct CloudKit for CKSyncEngine without checking database scope.

## Conflict, delete, and asset policy

For a direct record save, CKError.Code.serverRecordChanged means the server has a newer version than the attempted write. CloudKit exposes client, server, and ancestor records through the record-changed error keys. Use all three to apply a typed merge. Do not blindly take the last callback or overwrite the server with the client copy.

Good default policies:

- user-authored text beats a generated suggestion;
- a user edit and a remote user edit become a reviewable conflict when automatic merging is unsafe;
- an offline delete gets an explicit tombstone or domain-specific deletion rule;
- a large image/audio/document asset gets a separate file lifecycle from its metadata record;
- a missing asset marks the record incomplete rather than silently reconstructing it from a model;
- a remote permission change moves the local projection to unavailable without deleting local data.

For AI-derived fields, store source, model/framework version, generated value, confidence or uncertainty, and review state separately. A new on-device proposal is not permission to overwrite a confirmed local value, and remote sync is not model validation.

## Account, privacy, and background boundaries

Check the CloudKit account state before presenting a remote-only action. Model at least available, noAccount, restricted, temporarilyUnavailable, and couldNotDetermine. Re-evaluate after account-change notifications. Keep local-only mode explicit.

Remote notifications are signals for reconciliation, not proof that a person saw a change. The person-facing surface should say “saved on this device,” “waiting to sync,” “updated from another device,” or “needs review” rather than exposing raw CloudKit error text.

Sensitive records need a retention and deletion story in both the local store and CloudKit scope. Explain what syncs, what remains local, what is shared, and what happens when the person signs out. Use Keychain for credentials and protected file storage for sensitive blobs instead of ordinary model fields.

## Native UI, Liquid Glass, and AI composition

Sync status belongs near the record it qualifies, not in a permanently floating dashboard. Use native hierarchy:

1. the record’s content remains primary;
2. a compact status label or icon communicates pending/offline/conflict;
3. a sheet or inspector explains the issue and offers a deterministic action;
4. the system owns account/settings permission surfaces when available;
5. Liquid Glass groups controls and status without turning a data problem into decoration.

An on-device model can summarize a conflict, suggest a merge, or classify a local record for review. It cannot establish that two users intended the same edit, grant CloudKit access, prove a save reached the server, or silently delete a remote record. Keep the generated result editable, provenance-labeled, stale-aware, and behind confirmation for side effects.

## Verification route

- Compile the selected route in the named app target and inspect its signed entitlements.
- Run a local-only fixture with no CloudKit capability before enabling replication.
- Exercise iCloud account states, first launch, schema initialization, migration, offline edits, remote edits, deletion races, and process termination.
- For CKSyncEngine, restore state after relaunch, replay fetched events, bound send batches, and verify failed record saves remain retryable.
- Use two physical devices on the intended iCloud account for cross-device behavior; simulator/local previews prove only local behavior unless a specific environment test is documented.
- Test development and production containers separately and record the schema promotion step.
- Verify VoiceOver, Dynamic Type, Reduce Motion, redacted content, localization, and accessibility of conflict resolution.
- Measure battery, network, storage, and long-running sync behavior on representative hardware before release.

## Sources

- [CloudKit](https://developer.apple.com/documentation/cloudkit)
- [SwiftData](https://developer.apple.com/documentation/swiftdata/)
- [Deciding whether CloudKit is right for your app](https://developer.apple.com/documentation/cloudkit/deciding-whether-cloudkit-is-right-for-your-app)
- [Syncing model data across a person’s devices](https://developer.apple.com/documentation/swiftdata/syncing-model-data-across-a-persons-devices)
- [Preserving your app’s model data across launches](https://developer.apple.com/documentation/swiftdata/preserving-your-apps-model-data-across-launches)
- [ModelContainer](https://developer.apple.com/documentation/swiftdata/modelcontainer)
- [ModelConfiguration](https://developer.apple.com/documentation/swiftdata/modelconfiguration)
- [ModelConfiguration.CloudKitDatabase](https://developer.apple.com/documentation/swiftdata/modelconfiguration/cloudkitdatabase-swift.struct)
- [CKSyncEngine](https://developer.apple.com/documentation/cloudkit/cksyncengine)
- [CKSyncEngine.Configuration](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/configuration)
- [Creating a sync engine configuration](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/configuration/init%28database%3Astateserialization%3Adelegate%3A%29)
- [CKSyncEngineDelegate](https://developer.apple.com/documentation/cloudkit/cksyncenginedelegate-1q7g8)
- [CKSyncEngine.State.Serialization](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/state-swift.class/serialization)
- [CKSyncEngine.Event.StateUpdate](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/event/stateupdate)
- [CKSyncEngine.Event](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/event)
- [CKDatabase](https://developer.apple.com/documentation/cloudkit/ckdatabase)
- [CKRecord](https://developer.apple.com/documentation/cloudkit/ckrecord)
- [CKRecordZone](https://developer.apple.com/documentation/cloudkit/ckrecordzone)
- [CKRecordZone.ID](https://developer.apple.com/documentation/cloudkit/ckrecordzone/id)
- [CKRecordZoneNotification](https://developer.apple.com/documentation/cloudkit/ckrecordzonenotification)
- [Record changed error keys](https://developer.apple.com/documentation/cloudkit/record-changed-error-keys)
- [CKError.serverRecordChanged](https://developer.apple.com/documentation/cloudkit/ckerror/serverrecordchanged)
- [Enabling CloudKit in your app](https://developer.apple.com/documentation/cloudkit/enabling-cloudkit-in-your-app)
- [Setting up Core Data with CloudKit](https://developer.apple.com/documentation/coredata/setting-up-core-data-with-cloudkit)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
