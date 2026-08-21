# Persistence, Local-First, and Sync Recipes

## Scope and compile boundary

These are compile-oriented route sketches for SwiftData, schema migration, model actors, CloudKit automatic sync, `CKSyncEngine`, direct `CKDatabase` operations, and privacy-aware storage of AI-derived records. They are not compiled in this documentation-only workspace and do not prove migration safety, CloudKit schema deployment, account behavior, conflict quality, offline durability, backup behavior, or multi-device correctness.

Start with a useful local app. Add sync only when the user outcome requires cross-device continuity, shared records, public discovery, or another explicit remote capability. Before copying a recipe, set the deployment target, compile the smallest route, create a development CloudKit container, test old data fixtures, and verify entitlements and signed-device behavior.

## Route selector

| Need | First route | Ownership and proof boundary |
| --- | --- | --- |
| Private records on one device | SwiftData local `ModelContainer` | App owns schema, saves, deletion, migration, export, and privacy |
| Same person’s records across Apple devices without custom sync policy | SwiftData automatic CloudKit sync | CloudKit-compatible schema, iCloud capability, background capability, account state, schema deployment |
| App-owned local model with private/shared CloudKit replication | `CKSyncEngine` | App owns record mapping, local pending changes, conflict merge, state serialization, and applying fetched events |
| Public data, custom record queries, or record-level control | Direct `CKDatabase`/`CKRecord` | App owns zones, subscriptions, change tokens, retries, conflicts, permissions, and offline replay |
| Documents, images, audio, or large blobs | File/document storage plus a model reference | App owns source/derived relationship, retention, deletion, backup/cache policy, and file protection |

Do not layer SwiftData automatic sync and `CKSyncEngine` over the same records casually. Pick one replication owner and make the other layer a local source or a separate boundary.

## Recipe 1: persist a reviewable AI-derived record

Keep the source, derived result, provenance, review state, and user edit separate. This model avoids a local-only unique constraint so it can remain a candidate for automatic CloudKit sync; use app-owned deduplication instead of assuming CloudKit enforces uniqueness.

```swift
import SwiftData

@Model
final class IntelligenceRecord {
    var id = UUID()
    var createdAt = Date.now
    var sourceKind = "unknown"
    var sourceLocator: String?
    var sourceText: String?
    var derivedText: String?
    var userEditedText: String?
    var provenance = ""
    var processingRoute = ""
    var reviewStateRawValue = "needsReview"
    var modelOrFrameworkVersion = ""
    var lastReviewedAt: Date?

    init(
        sourceKind: String,
        sourceText: String?,
        provenance: String,
        processingRoute: String,
        modelOrFrameworkVersion: String
    ) {
        self.sourceKind = sourceKind
        self.sourceText = sourceText
        self.provenance = provenance
        self.processingRoute = processingRoute
        self.modelOrFrameworkVersion = modelOrFrameworkVersion
    }

    var textForDisplay: String {
        userEditedText ?? derivedText ?? sourceText ?? ""
    }
}
```

The source locator should be an app-owned identifier or file reference, not a secret-bearing URL. If the source is audio, an image, or a document, keep the large asset outside the model row when appropriate and retain a clear deletion relationship. If the derived value is user-confirmed, record that state and preserve the original source for correction or audit.

## Recipe 2: insert, review, and save with an explicit context boundary

Use the context for the persistence operation and keep parsing/model work outside the save transaction. A failed save should leave the draft recoverable rather than report success after only an in-memory insert.

```swift
import SwiftData

@MainActor
func saveReviewedRecord(
    sourceKind: String,
    sourceText: String?,
    derivedText: String,
    provenance: String,
    route: String,
    version: String,
    context: ModelContext
) throws {
    let record = IntelligenceRecord(
        sourceKind: sourceKind,
        sourceText: sourceText,
        provenance: provenance,
        processingRoute: route,
        modelOrFrameworkVersion: version
    )
    record.derivedText = derivedText
    record.reviewStateRawValue = "confirmed"
    record.lastReviewedAt = .now

    context.insert(record)
    do {
        try context.save()
    } catch {
        context.rollback()
        throw error
    }
}
```

For an unreviewed result, insert a draft with `needsReview` and do not call it a confirmed record. For a user edit, write `userEditedText` and retain `derivedText`; a later model pass can offer a new proposal without erasing the correction. Add product-specific validation for identifiers, dates, numbers, and required fields before marking confirmation.

## Recipe 3: use a migration plan instead of an implicit model edit

Define named schemas for releases that must be migrated reliably. A lightweight stage is appropriate only when the selected SDK can perform the change without app-owned transformation. A custom stage is the route for normalization, value splitting/merging, or other deterministic conversion.

```swift
import SwiftData

enum AppSchemaV1: VersionedSchema {
    static var versionIdentifier = Schema.Version(1, 0, 0)
    static var models: [any PersistentModel.Type] = [Record.self]

    @Model
    final class Record {
        var sourceText: String

        init(sourceText: String) {
            self.sourceText = sourceText
        }
    }
}

enum AppSchemaV2: VersionedSchema {
    static var versionIdentifier = Schema.Version(2, 0, 0)
    static var models: [any PersistentModel.Type] = [Record.self]

    @Model
    final class Record {
        var sourceText: String
        var reviewState = "needsReview"

        init(sourceText: String, reviewState: String = "needsReview") {
            self.sourceText = sourceText
            self.reviewState = reviewState
        }
    }
}

enum AppMigrationPlan: SchemaMigrationPlan {
    static var schemas: [any VersionedSchema.Type] = [
        AppSchemaV1.self,
        AppSchemaV2.self
    ]

    static var stages: [MigrationStage] = [
        .lightweight(
            fromVersion: AppSchemaV1.self,
            toVersion: AppSchemaV2.self
        )
    ]
}

let container = try ModelContainer(
    for: Schema(versionedSchema: AppSchemaV2.self),
    migrationPlan: AppMigrationPlan.self
)
```

The model types and migration stage are intentionally small. In a real app, keep a fixture for each shipped version, run the migration against a copy of that fixture, assert invariants, and test an interrupted or failed migration path. Never make remote model inference the only path for repairing old local data. Preserve source and mark derived fields pending if a migration cannot safely recompute them.

## Recipe 4: isolate background persistence with `ModelActor`

SwiftData’s main context and UI models should not be passed through arbitrary concurrent tasks. Use a model actor for background persistence work, construct it with the app’s model container, and pass Sendable values or persistent identifiers across the boundary.

```swift
import SwiftData

@ModelActor
actor BackgroundStore {
    func addDraft(
        sourceText: String,
        provenance: String,
        route: String
    ) throws {
        let record = IntelligenceRecord(
            sourceKind: "text",
            sourceText: sourceText,
            provenance: provenance,
            processingRoute: route,
            modelOrFrameworkVersion: "current"
        )
        modelContext.insert(record)
        try modelContext.save()
    }
}
```

This sketch assumes the `IntelligenceRecord` model from Recipe 1 and the current `@ModelActor` macro. The model actor serializes its `modelContext`; it does not make arbitrary network clients, audio buffers, or AI session objects safe to share. Re-fetch a model in the actor’s context rather than handing a live UI object to a detached task.

## Recipe 5: implement local deduplication without a sync-incompatible constraint

CloudKit automatic sync cannot enforce SwiftData’s local unique property option. If a product needs a logical key such as `sourceLocator + sourceKind`, use a deterministic lookup and an explicit merge policy for the automatic-sync model.

```swift
import SwiftData

@MainActor
func existingRecord(
    sourceKind: String,
    sourceLocator: String,
    context: ModelContext
) throws -> IntelligenceRecord? {
    let descriptor = FetchDescriptor<IntelligenceRecord>(
        predicate: #Predicate { record in
            record.sourceKind == sourceKind &&
            record.sourceLocator == sourceLocator
        },
        sortBy: [SortDescriptor(\IntelligenceRecord.createdAt)]
    )
    return try context.fetch(descriptor).first
}
```

This is not a substitute for a server uniqueness guarantee. Two devices can create two records before either sees the other. On reconciliation, keep provenance for both, choose a deterministic winner only when safe, or show a reviewable duplicate state. If the local store must enforce uniqueness and sync is not required, `@Attribute(.unique)` is a separate local-only choice.

## Recipe 6: make account availability a first-class state

Private CloudKit data requires an available iCloud account. Check the state asynchronously, listen for account changes, and keep local records usable when the account is absent or temporarily unavailable.

```swift
import CloudKit

enum CloudAvailability: Sendable {
    case available
    case localOnly
    case temporarilyUnavailable
    case restricted
    case unknown
}

func cloudAvailability() async -> CloudAvailability {
    do {
        switch try await CKContainer.default().accountStatus() {
        case .available:
            return .available
        case .noAccount:
            return .localOnly
        case .temporarilyUnavailable:
            return .temporarilyUnavailable
        case .restricted:
            return .restricted
        case .couldNotDetermine:
            return .unknown
        @unknown default:
            return .unknown
        }
    } catch {
        return .unknown
    }
}
```

The state only describes account access; it does not prove that the container, schema, entitlement, network, or sync engine is healthy. Observe `CKAccountChangedNotification` and re-check after the notification. Do not erase local data on `.noAccount` as an implicit side effect.

## Recipe 7: choose a `CKSyncEngine` local/sync boundary

`CKSyncEngine` is useful when the app owns a local store and wants CloudKit to schedule private/shared record-zone changes. Persist its state serialization with the local pending-change ledger, provide bounded batches, and apply fetched records through an actor-isolated repository.

```swift
import CloudKit

final class SyncDelegate: NSObject, CKSyncEngineDelegate {
    private let localChanges = LocalChangeLedger()

    func handleEvent(
        _ event: CKSyncEngine.Event,
        syncEngine: CKSyncEngine
    ) async {
        switch event {
        case let .stateUpdate(update):
            await localChanges.persistEngineState(update.stateSerialization)
        case let .accountChange(change):
            await localChanges.accountChanged(change)
        case let .fetchedRecordZoneChanges(changes):
            await localChanges.applyFetched(changes)
        default:
            await localChanges.recordEvent(event)
        }
    }

    func nextRecordZoneChangeBatch(
        _ context: CKSyncEngine.SendChangesContext,
        syncEngine: CKSyncEngine
    ) async -> CKSyncEngine.RecordZoneChangeBatch? {
        await localChanges.nextBatch(for: context)
    }
}
```

The event enum and associated values are SDK-sensitive; this sketch shows the ownership boundary rather than a complete ledger. Do not call `fetchChanges` or `sendChanges` from inside `handleEvent` when the delegate call could generate another event. Use the engine for private/shared databases, not the public database. The normal schedule is indeterminate; request an immediate operation only for a documented freshness requirement.

Before initialization, restore the most recent serialized engine state. When a state-update event arrives, persist it alongside the local changes that were already applied. If the two get out of step, the engine can replay or skip changes incorrectly after relaunch.

## Recipe 8: resolve a direct CloudKit record conflict

Direct `CKDatabase` writes require an explicit save policy and conflict strategy. `serverRecordChanged` provides client, server, and ancestor records; compare them and apply the product’s merge rules before retrying with the server record’s change tag.

```swift
import CloudKit

func saveRecordWithReviewableConflict(
    _ record: CKRecord,
    in database: CKDatabase
) async throws {
    do {
        _ = try await database.modifyRecords(
            saving: [record],
            deleting: [],
            savePolicy: .ifServerRecordUnchanged,
            atomically: false
        )
    } catch let error as CKError
        where error.code == .serverRecordChanged {
        let client = error.userInfo[CKRecordChangedErrorClientRecordKey] as? CKRecord
        let server = error.userInfo[CKRecordChangedErrorServerRecordKey] as? CKRecord
        let ancestor = error.userInfo[CKRecordChangedErrorAncestorRecordKey] as? CKRecord

        guard let server else { throw error }

        // Compare client/server/ancestor. Keep user edits and AI-derived
        // proposals separate, or create a review record for an unsafe merge.
        let merged = mergeForProductReview(
            client: client,
            server: server,
            ancestor: ancestor
        )

        _ = try await database.modifyRecords(
            saving: [merged],
            deleting: [],
            savePolicy: .ifServerRecordUnchanged,
            atomically: false
        )
    }
}
```

`mergeForProductReview` is intentionally app-owned. Do not merge into the ancestor or blindly replace the server copy with stale client data. For a destructive or sensitive field, preserve both versions and require review. Handle other `CKError` values such as account unavailable, network unavailable, rate limiting, change-token expiration, record-not-found, and request limits with state-specific retry or recovery.

## Recipe 9: keep files and secrets outside ordinary model fields

Use a SwiftData row for metadata and a file reference for a large image, recording, or document when that is the appropriate storage route. Define whether the asset is source, derived cache, export, or temporary work. Delete or invalidate related files when the owning record is deleted, and do not retain a stale path as if it were a valid source.

Keep passwords, API tokens, private keys, and other small secrets in Keychain Services, not in SwiftData or CloudKit records. A local database being on-device does not make every field appropriate for ordinary persistence. For sensitive records, choose file protection, backup/cache, export, and deletion behavior deliberately and test it after relaunch, lock/unlock, sign-out, and device migration.

## Recipe 10: verification matrix for local-first sync

| Test | Evidence to capture |
| --- | --- |
| Local persistence | Insert/edit/delete, relaunch, interrupted save, storage pressure, and recovery from a thrown save |
| Schema migration | Every supported prior schema, lightweight/custom stage, old source/derived fields, user edits, partially completed drafts, and migration failure recovery |
| Actor isolation | Background writes through `ModelActor`, UI reads through the intended context, no live model crossing an unsafe boundary |
| Cloud account | Available, no account, restricted, temporarily unavailable, account change, and local-only UI |
| Automatic SwiftData sync | Compatible schema, development initialization, offline edits, deletion, two physical devices, conflict behavior, and production schema promotion |
| `CKSyncEngine` | State restoration, pending batches, fetched events, delayed notifications, transient retry, account change, private/shared database, and app-specific conflict handling |
| Direct CloudKit | Zone/subscription/change-token lifecycle, record conflict with ancestor, rate limit, token expiration, deletion/tombstone, and retry idempotency |
| Privacy and deletion | Logs/analytics/crash output, source and derived retention, Keychain separation, file deletion, export, account deletion, and shared-copy behavior |

Simulator and preview evidence can validate pure migration fixtures and state rendering, but they do not prove production CloudKit behavior. Apple’s CloudKit documentation limits simulator use to the development environment; production container behavior needs a physical device, the signed entitlements, a real account, and a named build.

## Sources

- [SwiftData](https://developer.apple.com/documentation/swiftdata/)
- [ModelContainer](https://developer.apple.com/documentation/swiftdata/modelcontainer)
- [ModelContext](https://developer.apple.com/documentation/swiftdata/modelcontext)
- [Preserving your app’s model data across launches](https://developer.apple.com/documentation/swiftdata/preserving-your-apps-model-data-across-launches)
- [VersionedSchema](https://developer.apple.com/documentation/swiftdata/versionedschema)
- [SchemaMigrationPlan](https://developer.apple.com/documentation/swiftdata/schemamigrationplan)
- [MigrationStage](https://developer.apple.com/documentation/swiftdata/migrationstage)
- [Concurrency support](https://developer.apple.com/documentation/swiftdata/concurrencysupport)
- [ModelActor](https://developer.apple.com/documentation/swiftdata/modelactor)
- [Syncing model data across a person’s devices](https://developer.apple.com/documentation/swiftdata/syncing-model-data-across-a-persons-devices)
- [SwiftData updates](https://developer.apple.com/documentation/updates/swiftdata)
- [CloudKit](https://developer.apple.com/documentation/cloudkit)
- [Deciding whether CloudKit is right for your app](https://developer.apple.com/documentation/cloudkit/deciding-whether-cloudkit-is-right-for-your-app)
- [CKContainer](https://developer.apple.com/documentation/cloudkit/ckcontainer)
- [CKContainer account status](https://developer.apple.com/documentation/cloudkit/ckcontainer/accountstatus%28completionhandler%3A%29)
- [CKAccountStatus](https://developer.apple.com/documentation/cloudkit/ckaccountstatus)
- [CKDatabase](https://developer.apple.com/documentation/cloudkit/ckdatabase)
- [CKRecord](https://developer.apple.com/documentation/cloudkit/ckrecord)
- [CKRecordZone](https://developer.apple.com/documentation/cloudkit/ckrecordzone)
- [CKSyncEngine](https://developer.apple.com/documentation/cloudkit/cksyncengine)
- [CKSyncEngineDelegate](https://developer.apple.com/documentation/cloudkit/cksyncenginedelegate-1q7g8)
- [CKSyncEngine state](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/state-swift.class)
- [CKSyncEngine events](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/event)
- [CKSyncEngine state updates](https://developer.apple.com/documentation/cloudkit/cksyncenginestateupdateevent)
- [CKError.serverRecordChanged](https://developer.apple.com/documentation/cloudkit/ckerror/serverrecordchanged)
- [Keychain services](https://developer.apple.com/documentation/security/keychain-services)
- [Keychain items](https://developer.apple.com/documentation/security/keychain-items)
