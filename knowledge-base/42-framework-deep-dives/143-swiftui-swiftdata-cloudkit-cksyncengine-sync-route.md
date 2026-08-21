# SwiftUI SwiftData, CloudKit, and CKSyncEngine local-first sync route

Synchronization is a distributed-systems boundary expressed through a native
SwiftUI app. The device needs a usable local store even when iCloud is absent,
the network is delayed, or a different device writes a newer version. CloudKit
is not a remote database that a view can synchronously query after every tap.
Choose the persistence lane, make ownership explicit, and design recovery as a
first-class product state.

~~~text
local intent
  -> actor/context-owned transaction
  -> durable local save
  -> pending or locally complete UI state
  -> automatic SwiftData mirroring
       or
     custom CKSyncEngine pending record changes
  -> remote fetch/send when system conditions permit
  -> deterministic merge/reconciliation
  -> local commit + revision/provenance update
  -> SwiftUI refresh
~~~

The local save and the remote sync are different proof levels. A local
`ModelContext.save()` proves only that the configured local store accepted the
transaction. A CloudKit event proves that the sync layer observed a remote
operation. Neither alone proves that two devices converge to the desired
domain state, that a user is signed into the expected iCloud account, or that a
release build has the correct entitlements and production schema.

## Choose one primary sync lane

| Need | Primary lane | Ownership model | Main proof burden |
| --- | --- | --- | --- |
| Persist SwiftData models across a person’s devices with conventional app data | SwiftData `ModelContainer` with iCloud/CloudKit configuration | SwiftData/Core Data mirroring owns record translation and sync scheduling | CloudKit-compatible schema, iCloud + remote-notification capabilities, production schema, account/network/device behavior |
| Keep a private local store while sending a custom record protocol | SwiftData or Core Data locally plus `CKSyncEngine` | The app owns record encoding, pending changes, change application, conflict policy, and serialized engine state | Custom record identity, zone/database scope, batch limits, state persistence, account changes, conflict/retry, two-device convergence |
| Share records with other iCloud users | CloudKit shared database plus an explicit sharing route | CloudKit share/participant authority plus app domain policy | Share acceptance, participant identity, permissions, revocation, conflict, and UI proof |
| Sync a public database | A different CloudKit API/architecture | Public database has different access and privacy boundaries | Do not use `CKSyncEngine` for the app’s public database |

Do not attach a custom `CKSyncEngine` to the same records that SwiftData’s
automatic CloudKit mirroring already owns unless the integration contract is
explicit, tested, and justified. Two writers with different change tokens and
conflict policies can create duplicate or oscillating state. A domain may use
SwiftData for one local-first aggregate and a separate custom CloudKit zone for
another, but the boundary must be visible in code and in the release audit.

## SwiftData model ownership

`@Model` describes persistent Swift types. `ModelContainer` manages the schema,
configuration, storage, and associated model contexts. `ModelContext` inserts,
fetches, deletes, and saves models. In SwiftUI, attaching
`.modelContainer(for:)` to the appropriate scene or view hierarchy supplies a
shared environment context for `@Query` and for `@Environment(\.modelContext)`.

The main context provided by a model container is main-actor bound. It is a
good owner for view-facing edits, but it is not a license to perform large
imports, long migrations, or sync reconciliation directly inside a view body.
Use an explicit context or a `@ModelActor` for background work and keep the
actor’s ownership stable.

### Context and actor rules

- A model instance belongs to the context/container that manages it. Pass a
  `PersistentIdentifier`, stable domain ID, or `Sendable` DTO across actor
  boundaries instead of passing a live model object as if it were a value.
- Serialize writes per aggregate or use a model actor to prevent two tasks
  from independently editing the same model graph.
- Keep fetch descriptors bounded and cancellable. A sync import should not
  materialize an unbounded library into a SwiftUI view.
- Treat `save()` as a local transaction boundary. After save, publish a
  revision or pending-sync marker; do not claim that the remote server has
  accepted the change.
- If the context is not attached to a configured container, SwiftData can
  provide an in-memory schema-less context. Inserting into that accidental
  context is a configuration bug, not a successful local-first workflow.

`@ModelActor` generates the actor boilerplate and provides a serialized
`modelContext` for model work. It is useful for an import/reconciliation
coordinator, but it does not decide business conflicts. The actor must still
apply a deterministic domain policy and expose failures to the UI.

## SwiftData automatic CloudKit sync

To enable automatic sync for SwiftData, configure the app’s iCloud capability
with a CloudKit container and enable Background Modes with Remote notifications.
The container identifier is part of the signed target configuration. The
system uses entitlements and the model configuration to determine the CloudKit
container and private database behavior.

Automatic sync operates when system conditions permit. Network availability,
battery, process lifecycle, iCloud account state, background execution, and
remote notification delivery all affect timing. The UI must represent pending,
stale, offline, account-unavailable, and synced states without promising an
immediate server write.

### CloudKit-compatible SwiftData schema

CloudKit mirroring narrows the schema design space. Apple documents important
limitations, including:

- CloudKit cannot enforce SwiftData’s `unique` attribute option because
  changes can arrive concurrently.
- Relationships must be optional because CloudKit does not guarantee atomic
  relationship processing; make inverses explicit when SwiftData cannot infer
  them reliably.
- The `deny` relationship delete rule is not supported by CloudKit.
- The model’s types, optionality, relationships, and transformable values must
  be reviewed against the supported CloudKit mapping rather than assumed from
  local-only SwiftData behavior.

Design uniqueness as a deterministic domain or server rule, not as a CloudKit
guarantee. If a record needs a stable deduplication key, make it an explicit
field and handle collisions in the merge/reconciliation layer. Store a
version, logical clock, or edit revision when the domain needs to explain why
one value won.

Initialize the development schema deliberately, inspect record types and
indexes in CloudKit Console, and promote the compatible schema to production
before release. Never “fix” a production migration by erasing a user’s local
store or by deleting production schema without an explicit data-recovery plan.

### Local-first state vocabulary

Expose a domain-level sync state rather than leaking raw framework callbacks:

~~~text
localOnly
  -> savedLocally
  -> pendingUpload
  -> syncing
  -> synced(revision)

recoverable branches
  -> offline
  -> iCloudAccountUnavailable
  -> permissionOrEntitlementMissing
  -> migrationRequired
  -> conflictReview
  -> retryAfter(error)
~~~

The state should be scoped to the record or aggregate when possible. A global
“Syncing…” badge can be useful, but it must not hide a record-level conflict,
failed attachment, or locally saved change. Preserve local work while showing
what could not be sent.

## Schema versioning and migrations

SwiftData performs automatic migrations for changes within its supported
lightweight boundary. Use `VersionedSchema` to describe named schema versions
and `SchemaMigrationPlan` with `MigrationStage.lightweight` or `.custom` when
the route needs explicit stages.

A migration plan is not a generic data-cleanup script. Treat it as a versioned
contract:

1. define the old schema with the model types and version identifier that were
   actually shipped;
2. define the new schema and preserve stable model/type/property identity;
3. use a lightweight stage only for changes the framework can safely migrate;
4. use a custom stage for deterministic transforms, defaults, normalization,
   or relationship repair that require application code;
5. test migration from every supported prior release on a copied real store;
6. verify the migrated data locally before allowing sync or destructive writes;
7. record the schema version and migration outcome in release evidence.

Migration and CloudKit promotion are related but not interchangeable. A local
store can migrate successfully while the production CloudKit schema rejects a
new field, relationship, or type. A CloudKit schema can be compatible while a
custom local migration loses domain semantics. Both gates must pass.

## CKSyncEngine custom-record route

Use `CKSyncEngine` when the app owns a custom record mapping and needs more
control than automatic mirroring provides. Initialize it early with the
private or shared database that the app is authorized to use, a persisted
`State.Serialization` when available, and a `CKSyncEngineDelegate`.

The engine can schedule fetch/send work automatically, but the schedule is
indeterminate. It may remain dormant when the user has no iCloud account,
network, battery, or suitable system conditions. Provide explicit Refresh or
Sync Now actions only when the product needs immediate evidence, and call
`fetchChanges()`/`sendChanges()` outside the delegate event handler.

`CKSyncEngine` requires CloudKit and Remote notifications entitlements and is
not a route for the public database. A custom engine may target a private
database and a shared database, but each target has different record/share
authority and should usually have separate domain coordinators.

### Delegate sequencing

The engine delivers delegate events serially. Do not trigger a new fetch/send
operation from inside `handleEvent` when doing so can generate nested events.
The delegate must:

- persist every `Event.stateUpdate` serialization alongside the local pending
  state before the process can be terminated;
- process `Event.accountChange` and isolate local data when the iCloud account
  signs out, signs in, or switches;
- apply `fetchedDatabaseChanges` and `fetchedRecordZoneChanges` through one
  deterministic reconciliation owner;
- acknowledge `sentDatabaseChanges` and `sentRecordZoneChanges` by updating
  local revisions/pending state only after the framework reports success;
- return `RecordZoneChangeBatch` values that stay within the context’s scope;
- use `RecordZoneChangeBatch(pendingChanges:recordProvider:)` where possible
  so the engine respects the per-request 250-save/delete batch boundary;
- return `nil` when no eligible changes remain rather than repeating the same
  batch forever.

The engine’s state is opaque but not optional to the architecture. Persisting
the model store without persisting the engine serialization can cause redundant
fetches, lost pending changes, or a poor recovery path after relaunch.

### Account transitions

An iCloud account change can reset the sync engine’s internal state, including
unsaved changes in records and zones. If the device switches accounts, do not
merge the previous account’s private records into the new account. Quiesce the
engine, decide what locally saved data belongs to which account, preserve or
export only what the product’s privacy contract allows, initialize the new
state, and show the user what requires attention.

An app’s own account and the device’s iCloud account are different authorities.
Do not use the iCloud user record ID as an app login identity without a separate
product contract. Do not make a local “signed in to iCloud” label imply that a
CloudKit write has succeeded.

### Change application and conflict policy

CloudKit does not guarantee the order of fetched record-zone changes. Apply
each record by stable record ID and revision, and make repeated application
idempotent. Deletions need an explicit tombstone or deletion policy so a stale
device cannot resurrect data accidentally.

When CloudKit returns `CKError.Code.serverRecordChanged`, compare the client,
server, and ancestor records. Merge into the server record’s current change tag
according to the domain policy, then attempt a new save if appropriate. Never
blindly overwrite the server with the client copy. Common policies include:

- last-writer-wins for a field where the latest timestamp is trustworthy;
- field-level merge when edits touch independent fields;
- append-only event log where edits are facts rather than mutable state;
- explicit review when both devices changed the same user-visible field;
- server-authoritative value for security, entitlement, or billing facts.

Conflict policy is not a place for an LLM to improvise. The model can prepare a
typed suggestion from redacted local/server/ancestor fields, but a deterministic
validator must enforce allowed fields, revision relationships, authorization,
and user review before a write.

## SwiftUI, Liquid Glass, and sync UX

Use native SwiftUI views for the record surface and keep sync status as
context, not decoration:

- list rows can show a small semantic “Saved on this device,” “Waiting to
  sync,” or “Conflict needs review” value;
- a detail view can expose last local edit, last confirmed remote revision,
  account/availability state, and retry/resolve actions;
- a settings or diagnostics screen can show container/environment/build
  identity without exposing record payloads or tokens;
- a migration-required state should explain why the app needs an update or
  safe recovery rather than silently deleting data.

Apply Liquid Glass to functional toolbar, status, retry, and conflict-action
groups. Keep the record content readable and avoid turning every list row into
a glass panel. A glass badge should not be the only indication that data is
pending or conflicted; include text and VoiceOver semantics. Respect Dynamic
Type, Reduce Motion, Reduce Transparency, increased contrast, VoiceOver,
Switch Control, keyboard navigation, and offline/no-artwork/no-network states.

Sync transitions should be calm. A local save can update immediately; a remote
confirmation can use a subtle status change. Do not animate a record into a
“synced” state before the actual evidence arrives, and do not make an error
disappear when a retry is queued.

## Optional on-device AI merge review

The safe AI boundary is a typed proposal, not an autonomous sync agent:

~~~text
MergeProposal
  recordID
  localRevision / remoteRevision / ancestorRevision
  changedFields
  proposedFieldValues
  reason: deterministic policy context + optional model explanation
  sourceHash or record revision
  requiresUserReview = true
~~~

The model may summarize differences, group similar local notes, or draft a
human-readable explanation. It may not invent a revision, suppress a deletion,
change ownership/account scope, merge protected fields, or call CloudKit save
without deterministic revalidation. If the model is unavailable, show the raw
field-level diff and the deterministic policy.

Keep raw tokens, private keys, full CloudKit records, and unrelated user data
out of model context. Redact fields not needed for the proposal, cap output,
and persist the accepted result—not the model’s hidden reasoning—as a normal
domain transaction with its source revisions.

## Privacy, security, and data retention

Private CloudKit data is still personal data. Define account scope, deletion,
export, logout, iCloud-account switching, device loss, and local-store reset
behavior before enabling sync. Do not log record fields, server change tokens,
state serializations, record contents, or account identifiers unnecessarily.

Use separate redacted diagnostics for framework errors and domain failures.
Treat a remote record as untrusted input: validate type, size, required fields,
revision, and authorization before inserting it into SwiftData or displaying it
as trusted content. CloudKit transport/security does not replace app-level
authorization for a dangerous domain action.

## Release and proof boundaries

Production sync requires more than a local preview:

| Proof level | Evidence |
| --- | --- |
| Source | Official SwiftData, CloudKit, Core Data, SwiftUI, Liquid Glass, and AI docs |
| SDK | Installed iOS 26.4 interfaces and recipe typechecks |
| Target | iCloud container, CloudKit environment, Remote notifications, App Group if used, bundle ID, signed entitlements |
| Schema | Development schema initialized/inspected and production schema promoted |
| Local | Fresh install, relaunch, migration from prior store, offline edit, delete/reopen |
| Cloud | iCloud account available/unavailable, automatic sync or CKSyncEngine fetch/send, retry/rate-limit, account switch |
| Two-device | Same account, offline edits, remote changes, conflict, deletion/tombstone, convergence, duplicate prevention |
| UI | Pending/stale/conflict/migration/account states, accessibility, Dynamic Type, reduced effects |
| Distribution | Exact archive/TestFlight build, container/environment, production schema, and release checklist |

The simulator can validate model macros, state machines, deterministic fixtures,
and some CloudKit API shape. It does not prove iCloud account behavior,
notification delivery, multi-device convergence, migration safety for user
stores, or App Store release behavior.

## Sources

- [SwiftData](https://developer.apple.com/documentation/swiftdata)
- [ModelContainer](https://developer.apple.com/documentation/swiftdata/modelcontainer)
- [ModelContext](https://developer.apple.com/documentation/swiftdata/modelcontext)
- [Concurrency support](https://developer.apple.com/documentation/swiftdata/concurrencysupport)
- [ModelActor](https://developer.apple.com/documentation/swiftdata/modelactor)
- [VersionedSchema](https://developer.apple.com/documentation/swiftdata/versionedschema)
- [SchemaMigrationPlan](https://developer.apple.com/documentation/swiftdata/schemamigrationplan)
- [MigrationStage](https://developer.apple.com/documentation/swiftdata/migrationstage)
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
