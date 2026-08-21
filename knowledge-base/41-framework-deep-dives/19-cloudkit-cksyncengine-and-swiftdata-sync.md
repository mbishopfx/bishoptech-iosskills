# CloudKit, CKSyncEngine, and SwiftData synchronization

## Scope

This page defines the local-first synchronization route for native iOS apps that
store records on device and optionally reconcile them across a person's iCloud
devices or with shared CloudKit participants.

It covers:

- SwiftData automatic iCloud synchronization;
- CloudKit private, shared, and public databases;
- CKSyncEngine local/remote record synchronization;
- persisted sync-engine state and change tokens;
- pending local changes and remote change application;
- account changes, permissions, conflicts, deletion, and recovery;
- CloudKit sharing with CKShare and shared record zones/hierarchies;
- widget, Live Activity, and App Intent projections after reconciliation;
- on-device AI proposals and model/source revision boundaries.

Synchronization is not a replacement for a local data model. It is a reconciliation
system around a local source of truth.

A safe architecture is:

    local durable model
      -> local transaction/outbox
      -> sync engine or SwiftData CloudKit bridge
      -> remote record/zone
      -> remote change
      -> local reconciliation
      -> projection refresh

## Version and configuration boundary

Record the selected SDK, deployment target, CloudKit container, database type,
schema environment, capabilities, and account behavior. Apple documents different
requirements for SwiftData automatic sync and direct CloudKit/CKSyncEngine use.

Never infer that a symbol compiles means:

- the iCloud capability is configured;
- the CloudKit container exists in the selected environment;
- a production schema is deployed;
- the user is signed in to iCloud;
- remote notifications can wake the app;
- two devices reconcile correctly;
- a share participant has access;
- a widget or AI projection is current.

## Pick the synchronization owner

| Route | Best fit | Important boundary |
| --- | --- | --- |
| SwiftData automatic sync | A compatible SwiftData model that can use CloudKit conventions | Schema constraints and CloudKit limitations apply |
| CKSyncEngine | A custom local record layer needing explicit pending/fetched change control | The app must persist state and implement the delegate |
| Direct CloudKit operations | Targeted server records, custom zones, shares, or server queries | The app owns batching, errors, tokens, and reconciliation |
| Local-only SwiftData | Private/local-first app with no cross-device requirement | No automatic cloud recovery |
| App Group projection | Widget/extension access to compact local state | Entitlement, migration, and privacy are separate |
| Server database | Cross-user/service authority outside iCloud | Not a substitute for iCloud private-data semantics |

Do not use CKSyncEngine to synchronize the public database. Apple documents it
for private and shared database routes.

## SwiftData automatic iCloud sync

SwiftData automatic sync uses the CloudKit/Core Data infrastructure behind the
model container. Apple documents two required capabilities:

- iCloud with CloudKit enabled and a container;
- Background Modes with Remote notifications enabled so changes can wake the app.

The model schema must be CloudKit-compatible. Features such as unique constraints
and some nonoptional relationships may not map directly to CloudKit. Review the
schema before enabling automatic sync and deploy the schema through the correct
CloudKit environment.

A route sketch is:

    @Model schema
      -> CloudKit-compatible schema check
      -> ModelConfiguration cloudKitDatabase
      -> ModelContainer
      -> local writes
      -> system sync
      -> local change observation

Specify a container explicitly when multiple containers exist. For an app that
already uses CloudKit, Apple documents that SwiftData may infer automatic sync
from entitlements; opt out explicitly when the schema and existing CloudKit
container are not compatible.

Use a local-only configuration when the product is private/local-first and does
not want cloud sync. Do not accidentally enable sync because an entitlement was
copied into a target.

## CKSyncEngine

CKSyncEngine manages synchronization of local and remote record data. Create it
early in the app's launch process with a database and a delegate. The app can
create separate engines for the private and shared databases in the same process.

The engine periodically pushes and pulls when system conditions are good, such
as battery, network, and iCloud account availability. Its schedule is
indeterminate. When an operation needs fresh remote data before proceeding, use
the documented manual fetch/send APIs rather than assuming the next periodic
operation has run.

The engine uses opaque state to track internal sync information such as change
tokens, subscriptions, and account identity. Persist that state to disk and make
it available across launches. The state is part of the sync protocol, not merely
a cache that can be discarded on every launch.

The engine requires CloudKit and Remote notifications entitlements. If the user
is signed out or disables sync in Settings, the engine can remain dormant and
later resume when account state changes. The delegate must react to account
changes and update local persistence appropriately.

## CKSyncEngine delegate boundaries

The delegate supplies pending local changes and handles fetched events.

Important boundaries:

- the engine delivers events serially;
- do not call fetch/send methods from inside the event handler if that can cause
  additional events and violate ordering;
- include only changes within the scope provided by the send context;
- sending changes outside that scope can fail;
- handle serverRecordChanged and other CloudKit errors the engine cannot resolve;
- checkpoint the local outbox before acknowledging a successful send;
- apply fetched changes through a deterministic merge policy;
- persist state-update events.

A useful event route is:

    willFetch
      -> fetch database changes
      -> fetch record-zone changes
      -> apply remote changes
      -> record tokens/state
      -> didFetch

and:

    local outbox
      -> nextRecordZoneChangeBatch
      -> send within context scope
      -> acknowledge committed operations
      -> retain failures for retry

Do not delete an outbox item merely because a request was built. Delete or mark
it sent only after the server result and local transaction are durable.

## Local record and outbox model

For a custom CKSyncEngine route, model each local mutation with:

- stable record ID and record type;
- zone ID/database scope;
- local revision;
- server change tag or equivalent remote version;
- mutation kind;
- serialized fields or a deterministic change description;
- dependency/parent record if required;
- created/updated timestamps;
- retry count and last error category;
- account identifier scope;
- deletion/tombstone state.

A local write should commit the user-visible record and its outbox entry in one
local transaction. The sync engine reads the outbox, not a best-effort UI cache.

For deletes, keep tombstones until the remote delete is acknowledged and all
relevant devices can reconcile. Do not immediately reuse a deleted stable ID.

## Remote change application

Apply remote changes in a transaction:

1. verify database and record-zone scope;
2. resolve local record by stable ID;
3. compare local pending changes and remote version;
4. apply the documented merge policy;
5. update server metadata/change token;
6. update the projection revision;
7. preserve an audit/review state when conflict is not automatic;
8. persist the sync-engine state after the batch.

Do not let a remote change overwrite an unsent local edit without a policy. The
policy may be:

- last-writer-wins for a low-risk display preference;
- field-level merge for independent fields;
- append-only merge for events;
- manual review for a note or AI-approved classification;
- owner/participant permission rejection;
- tombstone wins for a delete, with recovery if the product supports it.

The policy is a product rule, not an accidental consequence of record ordering.

## Account changes and local privacy

CKSyncEngine monitors iCloud account status and delivers account change events.
The app must decide what to do with local data when the account changes:

- keep local-only records;
- quarantine records tied to the old account;
- delete cloud-scoped caches;
- reset engine state;
- prompt for sign-in;
- rebuild projections;
- preserve user-approved exports.

Never attach a new iCloud account to an old account's pending outbox. Persist the
account scope alongside the outbox and sync state. On sign-out, stop or cancel
sync operations, remove sensitive projections, and handle protected data according
to the product policy.

## CloudKit sharing

CloudKit sharing allows a person to share records from their private database
with other iCloud users. Shared data appears in the participant's shared database.

Choose the scope deliberately:

- share a custom record zone when all records in that zone belong in the share;
- share a record hierarchy when parent/child relationships define the intended
  boundary;
- use CKShare to manage owner/participant permissions;
- use the standard sharing UI when it fits the product;
- handle share acceptance through the supported app launch route;
- update local caches when sharing stops or participant permissions change.

A participant's ability to see a record is not the same as the ability to mutate
it. Recheck permissions at commit time and reflect owner/participant role in
AppEntity, UI, and system-surface projections.

## On-device AI and sync

Sync source records and committed user-approved outputs before syncing raw model
artifacts. Default to not syncing:

- full prompts or transcripts;
- private embeddings;
- model intermediate tensors;
- device-specific confidence logs;
- unreviewed proposals;
- private capture files beyond retention need.

If an AI proposal is synced, include:

- source record IDs;
- source revision;
- model/framework identifier;
- schema/prompt version when relevant;
- proposal status;
- reviewer/account identity;
- committed revision;
- expiration or invalidation condition.

On another device, revalidate the proposal against current source revision and
model policy. A synced proposal is not automatically approved on the destination
device.

## Widgets, Live Activities, and App Intents

After local/remote reconciliation, write a compact projection with a monotonic
projection revision. Then request widget reloads or update a Live Activity only
after the local domain transaction is committed.

App Intents and system surfaces should resolve current records from the local
store and account scope. A stable entity ID can survive across devices only when
the app has a documented stable identity and can resolve it under the current
account.

A widget showing a synced value is not evidence that the remote write was
accepted; it may be showing a cached local state. Provide freshness and pending
state where a distinction matters.

## Performance, power, and resource limits

Sync work is constrained by:

- network and account availability;
- background notification delivery;
- storage and database size;
- batch size and record payload size;
- protected data availability;
- process termination;
- server conflicts and rate limits;
- battery and thermal state.

Use small batches, backoff, deterministic retry, and manual sync only when the
user-visible operation needs freshness. Do not force a full fetch after every
keystroke or AI proposal.

## Physical and release proof

A complete sync claim needs:

- development CloudKit container/schema inspection;
- signed entitlements for iCloud and remote notifications;
- local-only versus cloud-enabled configuration proof;
- same-account two-device offline/edit/reconnect test;
- account sign-out/sign-in test;
- deleted record and tombstone test;
- conflict and serverRecordChanged test;
- shared zone/hierarchy owner/participant test;
- share acceptance/stop-sharing/permission test;
- process termination and relaunch;
- widget/App Intent/AI projection reconciliation;
- accessibility and localization;
- production schema/archive/TestFlight/environment proof.

A simulator or local model container can prove deterministic domain logic. It
does not prove iCloud account state, remote notifications, sharing, conflict
timing, or production container behavior.

## Sources

- [CloudKit](https://developer.apple.com/documentation/cloudkit)
- [CKSyncEngine](https://developer.apple.com/documentation/cloudkit/cksyncengine)
- [CKSyncEngineDelegate](https://developer.apple.com/documentation/cloudkit/cksyncenginedelegate)
- [CKSyncEngine.State](https://developer.apple.com/documentation/cloudkit/cksyncengine/state)
- [Syncing model data across a person’s devices](https://developer.apple.com/documentation/swiftdata/syncing-model-data-across-a-persons-devices)
- [Sharing CloudKit Data with Other iCloud Users](https://developer.apple.com/documentation/cloudkit/sharing-cloudkit-data-with-other-icloud-users)
- [Shared Records](https://developer.apple.com/documentation/cloudkit/shared-records)
- [CKShare](https://developer.apple.com/documentation/cloudkit/ckshare)
- [Local Records](https://developer.apple.com/documentation/cloudkit/local-records)
- [Remote Records](https://developer.apple.com/documentation/cloudkit/remote-records)
- [Providing User Access to CloudKit Data](https://developer.apple.com/documentation/cloudkit/providing-user-access-to-cloudkit-data)
- [Configuring iCloud services](https://developer.apple.com/documentation/xcode/configuring-icloud-services)
- [Configuring background execution modes](https://developer.apple.com/documentation/xcode/configuring-background-execution-modes)
- [SwiftData](https://developer.apple.com/documentation/swiftdata/)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit/)
- [ActivityKit](https://developer.apple.com/documentation/activitykit/)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Accessibility](https://developer.apple.com/accessibility/)
