# SwiftData and CloudKit sync route

## Use this route when

Use this recipe when an iOS app should work locally first and optionally keep structured records available across the same person’s Apple devices. It covers the route choice, model constraints, target configuration, recovery state, AI boundaries, and proof gates.

Start with [the persistence and sync recipes](../70-code-recipes/11-persistence-local-first-and-sync-recipes.md) for smaller code sketches. Use [the CloudKit/CKSyncEngine deep dive](../41-framework-deep-dives/12-cloudkit-syncengine-and-swiftdata.md) when deciding which synchronization owner should exist.

## Choose one replication owner

| Need | Route | Avoid |
| --- | --- | --- |
| SwiftData model, local-first UI, same person’s devices | SwiftData automatic CloudKit sync | Adding a second custom sync engine for the same records |
| App-owned record mapping and private/shared databases | CKSyncEngine | Expecting it to provide a domain model or public-database sync |
| Public database, custom queries, custom zones, record-level control | Direct CKDatabase/CKRecord | Treating a push notification as the record or ignoring change tokens |
| Files/documents/media | File or document route plus model metadata | Putting large blobs and sync policy in an unreviewed model field |

The route is an architectural decision. A successful local save, a successful CloudKit write, and a remote notification are three different events.

## Route A: automatic SwiftData sync

### Project setup

1. Choose the app target and deployment target.
2. Add iCloud capability and select the CloudKit container.
3. Add Background Modes and Remote notifications.
4. Define a CloudKit-compatible SwiftData schema.
5. Build a development schema and inspect it in CloudKit Console.
6. Create local, offline, account-unavailable, conflict, deletion, and migration fixtures.
7. Promote the production schema only after the model contract is stable.

Do not turn on CloudKit in a preview-only or widget target and assume the main app is configured. Inspect the signed app entitlements after the archive is built.

### Model shape

Keep the record’s product meaning separate from replication metadata:

~~~text
domain record
  source
  user-authored value
  derived/proposed value
  review state
  local revision
  last observed remote revision
  deletion/recovery state
~~~

Avoid using a SwiftData uniqueness constraint as a CloudKit guarantee. If the app needs a logical key, implement a deterministic local lookup and define what happens when two devices create the same logical record before reconciliation.

CloudKit-compatible relationships should be optional. Define inverses explicitly when inference is not reliable, and avoid delete rules that the automatic sync route cannot represent. Keep large assets in a separate file lifecycle when appropriate.

### Local-first UI state

Expose a small view model state rather than CloudKit types:

~~~text
syncPresentation:
  local
  pending
  synced(at:)
  offline
  accountUnavailable
  updatedElsewhere
  conflict
  failed(retryable: Bool)
~~~

The record view can remain usable in every state. Only remote-dependent actions should be blocked when the person has no account, access is restricted, or the network is unavailable.

## Route B: CKSyncEngine

Choose this route when the local store is app-owned and the product needs explicit record mapping, batching, private/shared database selection, or a custom conflict policy.

### Build order

1. Define the local record and pending-change ledger.
2. Define a stable record type, record ID, and zone mapping.
3. Persist the latest CKSyncEngine.State.Serialization.
4. Create the engine early with the private or shared CKDatabase.
5. Implement the delegate event reducer.
6. Implement bounded record-zone change batches.
7. Apply fetched records and deletions transactionally.
8. Reconcile failed saves/deletes and server-record-changed conflicts.
9. Add explicit fetch/send only where the user outcome needs freshness.

The engine schedule is not a timer contract. Keep “queued,” “attempted,” “acknowledged,” and “conflict” as observable local states.

### Event reducer

Route engine events into app-owned commands:

| Engine signal | App command |
| --- | --- |
| State update | Persist the new serialization with the local sync ledger |
| Fetched database/zone changes | Reconcile scope, records, and deletions |
| Sent record-zone changes | Mark only acknowledged operations complete |
| Failed record save | Preserve the local edit and classify retry/conflict |
| Failed record delete | Preserve a deletion intent or recovery state |
| Account/database problem | Switch the local UI to unavailable/recovery |

Do not call fetch/send recursively from the serial delegate event handler. Enqueue a follow-up action after the current event has completed.

## Route C: direct CloudKit

Use direct CloudKit when the app needs custom record-zone behavior or public data:

1. Pick the database scope.
2. Define record types and fields.
3. Create custom zones only in supported databases.
4. Persist record-zone change tokens.
5. Subscribe to changes and treat notifications as reconciliation hints.
6. Fetch changes until the server says no more changes are coming.
7. Apply partial failures per record.
8. Compare client/server/ancestor on server-record-changed.
9. Retry with the current record version after a deterministic merge.

This route needs more infrastructure than SwiftData automatic sync or CKSyncEngine. Document the reason before choosing it.

## Conflict policy worksheet

Fill this out before writing a merge function:

| Question | Decision |
| --- | --- |
| Which fields are user-authored? | List each field and its authority |
| Which fields are derived by AI or import? | Keep source, version, and review state |
| Can two values be combined without changing meaning? | Define a deterministic merge or require review |
| What happens when one device deletes? | Tombstone, restore, or explicit recreation |
| What happens when the iCloud account disappears? | Local-only mode and pending retention |
| What happens when a remote record is no longer shared? | Unavailable projection and local recovery |
| How long are old values retained? | Privacy, storage, and undo policy |
| How is the person told what will happen? | Plain-language comparison and confirmation |

For AI-derived fields, a safe default is user-authored value first, generated proposal second, and explicit review before any destructive or system-side effect.

## System surfaces and extensions

Widgets and notifications should display a projection with a freshness label. App Intents should resolve the current record and re-check authorization before mutating it. A Live Activity should become stale or end when the authority that drives its state is no longer available. None of these surfaces should imply that sync completed merely because a snapshot rendered.

Use a deep link into the main app for conflicts. Keep sensitive record content out of lock-screen notifications unless that exposure is intentionally designed and tested.

## Privacy and data lifecycle

Before enabling iCloud:

- classify every record field and attachment;
- state whether it is private, shared, or public;
- document account sign-out behavior;
- define export and deletion;
- remove raw assets and derived data together when required;
- keep credentials and API tokens in Keychain;
- record whether AI input/output is retained, synced, or deleted after confirmation.

CloudKit being Apple-hosted does not replace product privacy design. A local-only route may be the correct route for a sensitive feature.

## Minimal rollout slices

### Slice 1: local persistence

Build the record, migration fixture, review UI, and local-only state. Prove relaunch and save failure recovery.

### Slice 2: development sync

Add capabilities and a development container. Prove schema initialization, first sync, offline edit, account unavailable, and two-device reconciliation.

### Slice 3: conflict and deletion

Create controlled two-device edits, delete races, stale assets, and server-record-changed cases. Prove the user-facing review route.

### Slice 4: extensions and AI

Add projections only after the main app has honest sync state. Add bounded on-device suggestions that remain drafts and are invalidated when source records change.

### Slice 5: production gate

Inspect signed entitlements, container identifiers, production schema, privacy copy, migration record, and release build. Production promotion is a separate evidence item from a development-container test.

## Verification questions

- Which target owns the model container and iCloud capabilities?
- Is the schema CloudKit-compatible?
- Which database and record zone own the data?
- Where is CKSyncEngine state serialization persisted, if used?
- Can a process terminate between a fetched change and a state update?
- Can the app render and edit local data without iCloud?
- What does a conflict look like with VoiceOver and Dynamic Type?
- Can a stale AI proposal be rejected without changing domain truth?
- What exactly was proved on two physical devices?
- Which claims remain unverified for production, sharing, background delivery, and release?

## Sources

- [SwiftData](https://developer.apple.com/documentation/swiftdata/)
- [ModelContainer](https://developer.apple.com/documentation/swiftdata/modelcontainer)
- [ModelConfiguration](https://developer.apple.com/documentation/swiftdata/modelconfiguration)
- [ModelConfiguration.CloudKitDatabase](https://developer.apple.com/documentation/swiftdata/modelconfiguration/cloudkitdatabase-swift.struct)
- [Automatic CloudKit sync for SwiftData](https://developer.apple.com/documentation/swiftdata/syncing-model-data-across-a-persons-devices)
- [Preserving model data across launches](https://developer.apple.com/documentation/swiftdata/preserving-your-apps-model-data-across-launches)
- [CloudKit](https://developer.apple.com/documentation/cloudkit)
- [Deciding whether CloudKit is right for your app](https://developer.apple.com/documentation/cloudkit/deciding-whether-cloudkit-is-right-for-your-app)
- [CKSyncEngine](https://developer.apple.com/documentation/cloudkit/cksyncengine)
- [CKSyncEngine.Configuration](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/configuration)
- [CKSyncEngine.State.Serialization](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/state-swift.class/serialization)
- [CKSyncEngine.Event.StateUpdate](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/event/stateupdate)
- [CKSyncEngineDelegate](https://developer.apple.com/documentation/cloudkit/cksyncenginedelegate-1q7g8)
- [CKDatabase](https://developer.apple.com/documentation/cloudkit/ckdatabase)
- [CKRecordZone](https://developer.apple.com/documentation/cloudkit/ckrecordzone)
- [CKRecordZoneNotification](https://developer.apple.com/documentation/cloudkit/ckrecordzonenotification)
- [Record changed error keys](https://developer.apple.com/documentation/cloudkit/record-changed-error-keys)
- [Enabling CloudKit in your app](https://developer.apple.com/documentation/cloudkit/enabling-cloudkit-in-your-app)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
