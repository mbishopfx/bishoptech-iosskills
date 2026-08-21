# Capability recipe: local-first SwiftData and CloudKit synchronization

Use this recipe when a native app must preserve useful local work while
eventually synchronizing a person’s data across devices. Select either
SwiftData automatic CloudKit mirroring or a custom `CKSyncEngine` route for the
aggregate under design. The steps below keep local persistence, remote
authority, conflict policy, AI assistance, and release evidence separate.

## Outcome contract

The app must be able to:

1. save and read the core record locally without network access;
2. identify the schema and migration version of the local store;
3. show whether a change is only local, pending, syncing, confirmed, stale,
   conflicted, or blocked by account/configuration;
4. handle iCloud account sign-in, sign-out, and account switch without
   cross-account data leakage;
5. reconcile remote changes idempotently and preserve deletion semantics;
6. apply a documented conflict policy or route the user to review;
7. support two-device testing with the exact target and CloudKit environment;
8. keep optional on-device AI proposals subordinate to deterministic merge and
   authorization gates.

## 1. Select the persistence and sync lane

Write the decision down before creating the model:

| Question | SwiftData automatic sync | Custom `CKSyncEngine` |
| --- | --- | --- |
| Who maps models to CloudKit records? | SwiftData/Core Data mirroring | The app’s record codec/reconciler |
| Who owns pending changes? | Framework-managed mirror | `CKSyncEngine.State` plus app local state |
| Where is conflict policy? | Model/schema constraints plus app reconciliation where exposed | Explicit custom record merge policy |
| Best fit | Conventional private iCloud model data | Custom zones/records, precise batching, custom local store |
| Hard stop | Unsupported CloudKit schema feature | Unbounded/custom public-database design |

Do not use both lanes for the same record identity without a documented
ownership boundary and end-to-end tests.

## 2. Configure the target and CloudKit environment

For automatic SwiftData CloudKit sync:

1. Add iCloud capability and choose/create the CloudKit container.
2. Add Background Modes and enable Remote notifications.
3. Use the exact container identifier in the signed target.
4. Initialize and inspect the development schema in CloudKit Console.
5. Promote the compatible schema to production before release.

For `CKSyncEngine`:

1. Add CloudKit and Remote notifications entitlements.
2. Choose private or shared database; do not use `CKSyncEngine` for the public
   database.
3. Configure the record zone, subscription identity, and stable record IDs.
4. Persist `CKSyncEngine.State.Serialization` beside the local pending state.
5. Make the delegate and engine lifetime survive the app’s normal launch and
   background/relaunch path.

Inspect the signed archive’s entitlements and `Info.plist`. A development
container, simulator, or Xcode capability checkbox is not production proof.

## 3. Design a CloudKit-compatible schema

Before enabling automatic mirroring, review:

- uniqueness assumptions and deterministic deduplication keys;
- optionality of all relationships and explicit inverse declarations;
- unsupported delete rules such as `deny`;
- model field types, transformables, asset size, and server query needs;
- stable model/property identity across releases;
- account scope and whether a record belongs to the private or shared database.

Represent remote confirmation with app-owned metadata when the product needs
it: logical revision, last-confirmed timestamp, pending operation, source
device, and conflict state. Do not store server tokens or raw sync engine
state in user-visible copy.

## 4. Establish local ownership and migrations

Create a `ModelContainer` intentionally and attach it to the correct scene or
view hierarchy. Use the main context for small UI edits and a `@ModelActor` for
background imports/reconciliation. Define `VersionedSchema` and
`SchemaMigrationPlan` before changing a shipped model.

For every release migration:

1. copy a store from each supported prior build;
2. run the migration with the same target configuration used in release;
3. validate required fields, relationships, IDs, and user-visible content;
4. verify the migrated store can still sync with the target CloudKit schema;
5. test interruption/relaunch/retry and keep the original store until success;
6. attach migration evidence to the archive/release record.

Never use “delete and recreate the store” as the default migration strategy.

## 5. Define the domain sync state

Expose a value type or state machine separate from framework types:

~~~text
local state
  clean | dirty | saved | deleted | migrationBlocked

remote state
  unknown | pending | syncing | confirmed(revision) | offline
  accountUnavailable | configurationError | conflict(reviewID)

aggregate identity
  stable local ID + optional CloudKit record ID + schema revision
~~~

Make transitions idempotent. A repeated remote modification or notification
must not duplicate rows or reapply a destructive action. A failed send must
leave the local record and a retryable operation.

## 6. Build the automatic SwiftData route

For the automatic route:

1. save the local graph through the owning context/actor;
2. show local success immediately;
3. let the framework mirror when system conditions permit;
4. observe/reconcile the resulting local changes through the app’s state model;
5. surface offline, account, schema, and CloudKit errors without erasing local
   work;
6. test iCloud account unavailable, remote notification delay, relaunch, and
   two-device edits.

Do not create a manual “upload” spinner that claims a server write when the
automatic route has no immediate confirmation. A Refresh action can trigger a
new read/reconciliation where supported, but it still should report evidence,
not certainty.

## 7. Build the custom `CKSyncEngine` route

Initialize the engine with the private/shared database, latest state
serialization, `automaticallySync` policy, subscription ID if needed, and a
delegate. Register pending record-zone changes through `engine.state` after a
local transaction is durable. In `nextRecordZoneChangeBatch`, include only
changes in the context’s scope and return `nil` when the eligible queue is
empty.

Use the engine’s bounded batch initializer when possible. Keep the local
record-to-CloudKit codec deterministic and versioned. For remote modifications,
decode and validate before writing into SwiftData. For deletions, apply a
tombstone or an explicit delete rule that prevents stale resurrection.

Persist state update serializations before the app can be terminated. Keep
state serialization and local pending records consistent: if a local change is
already applied to the model but not represented in the engine state, recover
it through an app-owned outbox or history mechanism.

## 8. Handle events without nested sync races

Process `CKSyncEngine.Event` serially:

- `stateUpdate`: persist serialization and the related outbox revision;
- `accountChange`: isolate/reset account-scoped state and re-evaluate local
  data ownership;
- `fetchedDatabaseChanges`: update zone metadata;
- `fetchedRecordZoneChanges`: apply record modifications/deletions through the
  reconciliation owner;
- `sentDatabaseChanges`/`sentRecordZoneChanges`: mark only reported operations
  confirmed or failed;
- `didFetchChanges`/`didSendChanges`: publish the completed operation state.

Do not call `fetchChanges()` or `sendChanges()` from inside an event handler if
it can generate nested events. Schedule a separate task after the handler
returns. Keep cancellation and relaunch recovery tied to the engine owner, not
to a view’s lifetime.

## 9. Apply conflicts and account changes

When a CloudKit save returns `serverRecordChanged`, compare the client,
server, and ancestor records. Apply a deterministic policy:

- field-level merge for independent edits;
- server-authoritative values for access, billing, or security facts;
- append-only events for history;
- explicit user review for same-field edits;
- tombstones for intentional deletion.

Merge into the server record with its current change tag, then retry only after
validation. If the record changed again while the review was open, create a
new review instead of overwriting the newer version.

On account switch/sign-out, assume the engine’s internal state and unsaved
changes may reset. Quiesce outbound writes, separate local records by account
scope, discard or export only what the product contract permits, and
reinitialize the new account’s sync state. Do not use the device’s iCloud
account as an implicit app authentication session.

## 10. Add optional AI merge proposals

Send the model only typed, redacted fields:

~~~text
record ID + local/server/ancestor revisions
changed field names and bounded values
deterministic merge policy name
allowed output fields
~~~

The model may summarize the diff or propose a value for a review sheet. It may
not invent IDs/revisions, decide account ownership, suppress a deletion, alter
protected fields, or call CloudKit/SwiftData writes. A deterministic validator
must re-fetch or compare the current revision, validate the proposal, require
user review, and commit through the owning actor/context.

If the model is unavailable, display the raw field diff and the deterministic
choices. Persist source revisions and the user’s accepted decision, not hidden
model reasoning.

## 11. Compose native SwiftUI surfaces

Use `List`/`NavigationStack` for content, `Form` for diagnostics/settings,
native buttons for Retry/Review/Keep/Combine, and a sheet or destination for
conflicts. Keep state in an observable route store that is independent of
`@Query` rendering.

Use Liquid Glass for functional groups: a sync toolbar, conflict actions, a
status control, or a transient migration/account banner. Keep record content
and field diffs on the content layer. Avoid row-by-row custom glass, and test
glass with Dynamic Type, increased contrast, Reduce Transparency, Reduce
Motion, VoiceOver, keyboard, Switch Control, light/dark appearance, and iPad
split view.

## Acceptance checklist

- [ ] The automatic SwiftData and custom `CKSyncEngine` lanes are explicitly
  selected and not double-writing the same record identity.
- [ ] The target has the correct iCloud/CloudKit and Remote notifications
  capabilities, container, environment, and signed entitlements.
- [ ] The schema is CloudKit-compatible, versioned, migrated, and promoted.
- [ ] Model contexts and actors have one clear write owner.
- [ ] Local save, pending, synced, stale, conflict, account, and migration
  states are visible and recoverable.
- [ ] CKSyncEngine state serialization, account changes, event ordering,
  batching, scope, retries, and conflicts are implemented.
- [ ] Two-device tests cover offline edits, deletion, conflict, account switch,
  relaunch, duplicate prevention, and convergence.
- [ ] AI proposals are typed, redacted, reviewable, and revalidated.
- [ ] Accessibility, reduced effects, physical devices, archive, TestFlight,
  and production-schema proof are attached.

## Sources

- [SwiftData](https://developer.apple.com/documentation/swiftdata)
- [ModelContainer](https://developer.apple.com/documentation/swiftdata/modelcontainer)
- [ModelContext](https://developer.apple.com/documentation/swiftdata/modelcontext)
- [Concurrency support](https://developer.apple.com/documentation/swiftdata/concurrencysupport)
- [ModelActor](https://developer.apple.com/documentation/swiftdata/modelactor)
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
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
