# CloudKit and Sync

## Capability

CloudKit provides Apple-hosted storage and synchronization routes for apps that need data available across a person’s Apple devices or need private, public, or shared database behavior. It introduces account, entitlement, schema, network, and conflict concerns that do not exist in a purely local app.

## Select the sync route

| Product shape | Recommended first route | Ownership question |
| --- | --- | --- |
| Local-first app with optional cross-device continuity | SwiftData with automatic CloudKit sync | Which records are safe to sync, and what happens when the account is unavailable? |
| Custom records, public discovery, or shared zones | CloudKit container with `CKDatabase` and `CKRecord` | Which database and record permissions are authoritative? |
| Server-side processing or non-Apple clients | A deliberate service boundary, possibly alongside CloudKit | Where do authentication, API policy, and data retention live? |

CloudKit has three different implementation levels. SwiftData automatic sync is the least code when the model is compatible and the product wants a local replica with system-managed replication. `CKSyncEngine` keeps the app’s own local model while scheduling private/shared database changes. Direct `CKDatabase` operations provide the most record-level control, but the app owns change tokens, subscriptions, retries, conflict merges, account changes, and more of the offline contract. Do not describe these as interchangeable “CloudKit sync.”

## SwiftData automatic sync route

The documented SwiftData sync path uses CloudKit underneath. The implementation sequence is:

1. Keep the local model useful and testable without a network.
2. Add the iCloud capability and configure the CloudKit container.
3. Add the background capability needed for remote-change delivery.
4. Make the model schema compatible with the sync route.
5. Test account availability, first sync, offline edits, deletion, and conflicts.
6. Explain to the person when data is local, syncing, unavailable, or unresolved.

Do not treat adding an iCloud container as proof that sync works. The signed app, entitlements, CloudKit environment, schema deployment, and device account state all matter.

Automatic SwiftData sync is not a generic remote database. The documented CloudKit-compatible schema limitations include no server-enforced `@Attribute(.unique)`, optional relationships, explicit inverses when inference is not reliable, and no `Schema.Relationship.DeleteRule.deny`. Design the model for those constraints before initializing the development schema. If a local-only invariant is essential, keep it in app-owned validation/deduplication or choose a different sync architecture.

## Account state and local-only mode

Check `CKContainer.accountStatus()` before relying on the private database. Model at least `available`, `noAccount`, `restricted`, `temporarilyUnavailable`, and `couldNotDetermine`. Listen for the account-change notification and re-evaluate the state; do not assume that a person’s account state stays constant for the life of the process.

The app should still render the local replica when iCloud is unavailable. Make the UI honest about `local-only`, `syncing`, `lastSynced`, `accountUnavailable`, and `needsReview` states. Do not delete local data merely because the account is signed out unless the product has an explicit, reversible data policy and the person has confirmed it.

## CKSyncEngine route

Use `CKSyncEngine` when the app wants to own its local persistence and record mapping while delegating much of the scheduling, batching, subscription discovery, and change-token management to the engine. Use it with private or shared databases; Apple’s documentation explicitly says not to use it to sync a public database.

The engine’s contract is:

1. Initialize it early with the target database, delegate, and the latest persisted state serialization.
2. Register local pending database/record-zone changes through the engine’s state.
3. Implement `handleEvent` to apply fetched changes, account changes, sent results, and state updates to the local store.
4. Implement `nextRecordZoneChangeBatch` to provide bounded record saves/deletes for the requested scope.
5. Persist every state update alongside the local data before the next launch.
6. Let the system schedule normal sync, but use explicit fetch/send calls only when the product has a concrete freshness requirement.

The engine’s schedule is indeterminate and depends on conditions such as network, battery, account state, and system policy. It handles several transient errors, but app-specific record conflicts still belong to the app. Keep a durable pending-change/provenance record so a failed send can be retried or reviewed without losing the local edit.

```swift
import CloudKit

actor SyncStateStore {
    // Persist CKSyncEngine.State.Serialization with the same durability rules
    // as the local pending-change ledger.
    func save(_ state: CKSyncEngine.State.Serialization) throws {
        // Encode/store the serialization in the app-owned local store.
    }
}

final class PrivateSyncDelegate: NSObject, CKSyncEngineDelegate {
    let stateStore = SyncStateStore()

    func handleEvent(
        _ event: CKSyncEngine.Event,
        syncEngine: CKSyncEngine
    ) async {
        if case let .stateUpdate(update) = event {
            try? await stateStore.save(update.stateSerialization)
        }

        // Apply fetched record changes to the local store in a separate,
        // actor-isolated transaction. Do not call fetch/send from this handler.
    }

    func nextRecordZoneChangeBatch(
        _ context: CKSyncEngine.SendChangesContext,
        syncEngine: CKSyncEngine
    ) async -> CKSyncEngine.RecordZoneChangeBatch? {
        // Return only changes in context.options, in bounded batches.
        nil
    }
}
```

This is a delegate seam, not a complete sync engine. Verify the current Swift signatures, event payloads, record-zone mapping, state serialization codec, and actor isolation in the target SDK. A state serialization without the corresponding local pending-change/record data is not a recoverable sync state.

## Direct CloudKit conflict and deletion route

For direct `CKRecord` writes, use a save policy and handle `CKError.Code.serverRecordChanged`. CloudKit supplies the client, server, and ancestor records in the error’s user info so the app can compare the three versions, apply a deterministic merge policy, and retry with the server record’s current change tag. Do not blindly overwrite the server record or merge into an old ancestor.

For a user-authored field and an AI-derived field, a safe merge often keeps both versions and marks the record for review. For destructive edits, use a tombstone or explicit deletion record when offline replay could otherwise resurrect deleted content. Test repeated deletes, edits after delete, record-not-found, expired tokens, retry-after throttling, and a conflict from two physical devices.

## Direct CloudKit route

Use the CloudKit framework directly when the app needs record-level control, public data, shared records, custom queries, or a server-like Apple-hosted database. Keep CloudKit types behind a repository or service boundary so SwiftUI views and domain models do not depend on `CKRecord` details.

The boundary should define:

- record type and field mapping;
- private, public, or shared database ownership;
- authorization and account-change behavior;
- retry and offline policy;
- conflict resolution and record version policy;
- deletion, tombstone, and privacy behavior;
- whether the app can function when iCloud is unavailable.

## UI state machine

Represent sync state explicitly rather than showing a permanent spinner:

`local -> pending upload -> synced`

and separately:

`local -> offline`

`local -> conflict -> needs review`

`local -> account unavailable -> local-only mode`

A user-facing record should remain usable while a sync task retries. For sensitive or shared content, show the last successful sync time and any unresolved conflict without exposing raw server errors.

## Boundaries and failure modes

- CloudKit is not a substitute for an app account model when the product needs non-Apple identity or server authorization.
- iCloud account state can change after installation; test sign-out, restricted accounts, and a new device.
- SwiftData automatic CloudKit sync and `CKSyncEngine` have different ownership boundaries; choose one local truth and one conflict policy rather than layering them accidentally.
- Schema changes must be deployed deliberately and tested in the correct CloudKit environment.
- Network success does not mean every record is visible to every user; database scope and sharing permissions control visibility.
- Remote notifications and background execution are system-managed; design for delayed delivery and foreground reconciliation.
- Avoid storing secrets or assuming the device is online.
- `CKSyncEngine` does not remove the need to persist its state serialization or handle app-specific record conflicts.

## Verification route

- Test with a development container before production schema promotion.
- Exercise offline create/edit/delete and then reconnect.
- Test two physical devices signed into the intended iCloud account and a conflict case.
- Test `CKContainer.accountStatus()` transitions, account-change notification handling, and local-only behavior with no iCloud account.
- For `CKSyncEngine`, restart the process between state updates, verify state restoration, test pending batches, delayed notifications, transient retry, and `serverRecordChanged` review/merge.
- Confirm entitlements, background modes, container identifiers, and privacy copy in the signed archive.
- Test development and production containers separately; simulator evidence is limited to development, while production behavior requires a physical device.
- Validate account deletion, data export/deletion, shared-record permissions, and retention requirements for the product before App Store submission.

## Sync API route matrix

Choose the synchronization owner before adding capabilities. The same product can use more than one CloudKit database, but it should not have multiple uncoordinated authorities for the same record.

| Route | Best fit | App-owned responsibilities | Proof boundary |
| --- | --- | --- | --- |
| SwiftData automatic iCloud sync | Local-first SwiftData models that should replicate across a person’s devices | Compatible schema, local UX, migration, conflict meaning, account/offline UI, and CloudKit capability setup | Signed target with iCloud/background configuration, development schema, two-device offline/conflict test, and production-environment promotion record. |
| `CKSyncEngine` | App-owned local store with private or shared database synchronization | Record mapping, pending-change ledger, applying events, batching records, durable state serialization, conflict merge, deletion/tombstone policy | Process restart with restored state, account change, delayed delivery, partial batch, conflict, and two-device proof. |
| Direct `CKDatabase` operations | Public data, custom queries, record-level control, or a route not compatible with automatic sync | Change tokens, subscriptions, retries, conflict policy, zones, access scope, pagination, and local/offline reconciliation | Target entitlement, database environment, query/save/delete fixtures, throttling, conflict, permissions, and physical-device/account proof. |

## `CKSyncEngine` event and persistence contract

Treat the engine as a scheduler and transport coordinator, not as the app’s domain store. Persist these pieces together:

1. The serialized `CKSyncEngine.State` returned by state-update events.
2. The local records or persistent identifiers that each pending database/record-zone change refers to.
3. The local merge/provenance state needed to replay an edit after a process restart.
4. The last applied server change and the schema/mapper version used to interpret it.

Route events to a state machine:

`initialized -> waitingForAccount -> ready -> sending/receiving -> applying -> idle`

with side paths:

`ready -> offline`, `applying -> conflictReview`, `any -> accountChanged`, `any -> retryAfter`, and `any -> resetRequired`.

The delegate must bound record batches and respect the requested scope in `nextRecordZoneChangeBatch`. Apply fetched records transactionally to the local store, persist the updated engine serialization, and only then mark the corresponding local work complete. If a save returns `CKError.Code.serverRecordChanged`, compare the client, server, and ancestor records and retry a deterministic merge from the current server version. Do not resolve a conflict by blindly taking whichever callback arrived last.

## CloudKit target and environment matrix

| Concern | Development route | Release route | Evidence |
| --- | --- | --- | --- |
| Container identifier | Xcode capability and development container | Signed production entitlement and promoted schema | Inspect the built entitlements and archive environment; record the exact identifier. |
| Remote-change delivery | Background Modes/remote notifications in the selected app target | Same capability on the release target and a tested user-notification/background policy | Archive inspection plus delayed-change test on a physical device. |
| Database scope | Private, public, or shared database chosen per feature | Same scope with role/permission policy | Verify account identity, sharing permissions, and visibility with separate test users where applicable. |
| Schema | Development schema and fixtures | Deployed production schema with migration record | Record schema deployment, compatibility, and rollback/recovery plan. |
| Local replica | SwiftData/Core Data/custom store | Same local data contract with deletion/export behavior | Relaunch, offline, conflict, sign-out, and storage-pressure evidence. |

Do not treat a successful development-container save as production readiness. Container environment, target entitlements, account state, database scope, remote-notification delivery, schema deployment, and data-protection policy are separate gates.

## Conflict and deletion matrix

| Situation | Safe first response | Do not do |
| --- | --- | --- |
| Same field edited locally and remotely | Compare client/server/ancestor and apply a typed merge or review state | Overwrite the server without examining the ancestor. |
| AI-derived value conflicts with a user edit | Preserve user-authored value, retain source/provenance, and mark the derived proposal stale | Replace the edited value because a newer model output exists. |
| Offline delete races with remote edit | Use a tombstone or explicit deletion policy and resolve the race deterministically | Replay an old edit that silently resurrects deleted content. |
| Account becomes unavailable | Keep permitted local records readable and show local-only/pending state | Delete local data or claim sync completed. |
| Shared record permission changes | Re-fetch authorization and surface unavailable/shared state | Cache access as permanent authorization. |

The exact merge rule belongs to the domain, not CloudKit. Keep raw server errors out of the user-facing copy while preserving a diagnostic record with database, record ID, change token, retry state, and redacted failure category.

## Sources

- [CloudKit](https://developer.apple.com/documentation/cloudkit)
- [Syncing model data across a person’s devices](https://developer.apple.com/documentation/swiftdata/syncing-model-data-across-a-persons-devices)
- [Deciding whether CloudKit is right for your app](https://developer.apple.com/documentation/cloudkit/deciding-whether-cloudkit-is-right-for-your-app)
- [CKContainer](https://developer.apple.com/documentation/cloudkit/ckcontainer)
- [CKContainer account status](https://developer.apple.com/documentation/cloudkit/ckcontainer/accountstatus%28completionhandler%3A%29)
- [CKAccountStatus](https://developer.apple.com/documentation/cloudkit/ckaccountstatus)
- [CKDatabase](https://developer.apple.com/documentation/cloudkit/ckdatabase)
- [CKRecordZone](https://developer.apple.com/documentation/cloudkit/ckrecordzone)
- [CKSyncEngine](https://developer.apple.com/documentation/cloudkit/cksyncengine)
- [CKSyncEngineDelegate](https://developer.apple.com/documentation/cloudkit/cksyncenginedelegate-1q7g8)
- [CKSyncEngine.State](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/state-swift.class)
- [CKSyncEngine.Event](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/event)
- [CKSyncEngine state updates](https://developer.apple.com/documentation/cloudkit/cksyncenginestateupdateevent)
- [CloudKit design guide](https://developer.apple.com/library/archive/documentation/DataManagement/Conceptual/CloudKitQuickStart/)
- [CKRecord](https://developer.apple.com/documentation/cloudkit/ckrecord)
- [CKError.serverRecordChanged](https://developer.apple.com/documentation/cloudkit/ckerror/serverrecordchanged)
- [Record changed error keys](https://developer.apple.com/documentation/cloudkit/record-changed-error-keys)
- [Remote notifications](https://developer.apple.com/documentation/usernotifications)
