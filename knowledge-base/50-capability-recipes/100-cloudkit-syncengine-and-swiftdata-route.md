# CloudKit, CKSyncEngine, and SwiftData synchronization route

## Capability contract

Use this route when an app needs records to remain useful locally and optionally
reconcile them across a person's iCloud devices or with shared participants.

The route has four outputs:

1. a local durable model;
2. a sync owner and account/permission boundary;
3. a deterministic merge/outbox/recovery policy;
4. a compact projection for widgets, App Intents, Live Activities, and AI review.

CloudKit is not a generic database shortcut. Decide whether the product needs
private iCloud data, shared collaboration, a public catalog, or a separate server.

## Choose the local/cloud shape

| Need | Preferred starting route |
| --- | --- |
| Private records on one device | Local SwiftData with no cloud configuration |
| Compatible private records across the user's devices | SwiftData automatic iCloud sync |
| Explicit custom local record/outbox protocol | CKSyncEngine |
| Private/shared collaborative records | CloudKit private/shared databases and CKShare |
| Public read-only catalog | CloudKit public database or another documented service; not CKSyncEngine |
| Widget/extension compact projection | App Group/shared local projection after commit |
| AI proposal with source provenance | Local proposal record; sync only approved/necessary fields |

Do not add iCloud capability because it seems useful. It changes the account,
privacy, schema, test, and release surface.

## Route A: local-only first

1. Define SwiftData models and migrations.
2. Use a local-only ModelConfiguration.
3. Create the ModelContainer in the main app.
4. Keep widgets/extensions on a compact projection.
5. Add an export/backup route if the product needs recovery.
6. Document that no cloud sync occurs.
7. Keep future stable IDs and revision fields compatible with a possible sync
   route, without claiming that sync exists.

This is a good default for private/local-first utilities. It preserves the free
core workflow and avoids asking users to sign into iCloud until the product has a
clear need.

## Route B: SwiftData automatic sync

1. Confirm the model schema is compatible with CloudKit.
2. Add the iCloud capability and enable CloudKit.
3. Create or select the container.
4. Add Background Modes and Remote notifications as documented.
5. Use a private CloudKit database configuration when appropriate.
6. Test development schema and migration before production.
7. Run same-account two-device offline/edit/reconnect tests.
8. Handle account unavailable/sign-out states.
9. Decide how widgets and AI proposals reflect pending/synced/conflict state.
10. Archive and inspect entitlements, containers, and model resources.

Automatic sync abstracts much of the record transport, but product behavior still
needs account, conflict, deletion, migration, and physical-device proof.

## Route C: CKSyncEngine

1. Define the local record, stable CloudKit record ID, zone, and outbox.
2. Configure iCloud and Remote notifications capabilities.
3. Create one CKSyncEngine for the private database and another for the shared
   database when both are needed.
4. Persist the engine's opaque state across launches.
5. Implement CKSyncEngineDelegate with serial event handling.
6. Supply pending record/database changes only within the context scope.
7. Apply fetched changes through an explicit merge policy.
8. Handle account changes, missing subscriptions, serverRecordChanged, and
   permission errors.
9. Use manual fetch/send only when freshness is required.
10. Write the projection after local reconciliation, not after request creation.
11. Test process termination, offline state, and token/state recovery.

Do not use CKSyncEngine for a public database. Do not call methods from an event
handler that create additional engine events and violate the documented ordering.

## Route D: sharing

1. Put shareable records in a custom private record zone or explicit hierarchy.
2. Create CKShare for the intended root/zone.
3. Present standard sharing UI when appropriate.
4. Add the supported share-link launch configuration.
5. Accept share metadata through the app's scene/app route.
6. Reconcile the shared database after acceptance.
7. Show owner/editor/viewer permissions.
8. Handle stop-sharing, participant removal, and permission changes.
9. Recheck permission before mutation.
10. Test two different iCloud accounts on physical devices.

Sharing a record is not the same as making it public. A participant's shared
database is a scoped view of the owner's shared data.

## Record and outbox contract

For each syncable record, store:

- stable local ID;
- CloudKit record ID and zone/database scope;
- account scope;
- local revision;
- server change tag or remote revision;
- tombstone/delete state;
- pending mutation list;
- source/projection revision;
- AI proposal/approval metadata when relevant.

Commit the local user edit and the outbox entry together. A failed send should
leave the mutation retryable. A remote change should update the record and sync
state together.

## Conflict policy

Choose policy by field semantics:

| Field | Possible policy |
| --- | --- |
| Display preference | Last-writer-wins |
| Independent metadata | Field-level merge |
| Event history | Append-only with stable event IDs |
| Rich note | Review/merge |
| Shared permission | Server/owner authority |
| Delete versus edit | Tombstone plus recovery/review |
| AI classification | Approved value plus proposal conflict |
| Payment/entitlement | Server authority; do not local-merge access |

When a conflict cannot be safely automated, create a review record. Never let
remote ordering silently overwrite user-approved content.

## Route E: AI with sync

1. Store source record and source revision locally.
2. Generate a local typed proposal.
3. Mark proposal unreviewed.
4. Let the person approve in the main app.
5. Commit the approved value with model/source metadata.
6. Sync the approved value and necessary provenance.
7. On another device, revalidate source revision and account.
8. If model/device policy differs, show review or rerun locally.
9. Project only committed, privacy-safe state.

Do not sync raw prompts, transcripts, private embeddings, or intermediate tensors
unless a separate retention/security decision explicitly requires them.

## Route F: projections

After a successful local transaction:

1. write a compact projection with monotonic revision;
2. include pending/synced/conflict/denied state;
3. redact if locked/signed out;
4. reload affected widgets;
5. update or end a relevant Live Activity;
6. repair App Intent/Spotlight indexes if needed;
7. include source/model revision in AI-facing records.

A widget reload or ActivityKit update is downstream of the local transaction.
Neither proves that CloudKit accepted a remote change.

## Route G: recovery and account changes

On account change or sync disable:

- pause/cancel sends;
- preserve local-only data according to product policy;
- quarantine old-account outbox entries;
- reset/rebuild account-scoped sync state;
- invalidate private projections;
- refresh widget/intent indexes;
- ask for sign-in or Settings repair;
- avoid uploading an old account's pending data to the new account.

On process termination, reload the persisted engine state and local outbox. If
state is corrupt, use a documented rebuild route rather than silently deleting
user records.

## Route H: archive and production proof

Inspect:

- iCloud/CloudKit and Remote notifications entitlements;
- Background Modes capability;
- container identifiers and environment;
- production schema deployment;
- SwiftData model configuration;
- sync-engine state storage;
- App Group projection membership;
- CloudKit sharing keys/URL route;
- privacy and sign-out cleanup;
- widget/activity/App Intent resources;
- TestFlight and two-device behavior.

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
- [Configuring iCloud services](https://developer.apple.com/documentation/xcode/configuring-icloud-services)
- [Configuring background execution modes](https://developer.apple.com/documentation/xcode/configuring-background-execution-modes)
- [SwiftData](https://developer.apple.com/documentation/swiftdata/)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit/)
- [ActivityKit](https://developer.apple.com/documentation/activitykit/)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [App Groups](https://developer.apple.com/documentation/xcode/configuring-app-groups)
