# SwiftUI SwiftData, CloudKit, and CKSyncEngine sync recipes

These snippets target the installed iOS 26.4 simulator SDK. They show the
current API shape and state boundaries; they are not a complete entitlement,
CloudKit schema, migration, conflict-policy, account-change, or release
implementation. Each `~~~swift` block is intentionally independent and
compile-sized.

## 1. Define a CloudKit-compatible SwiftData record

Keep the persisted model small and explicit before enabling automatic
CloudKit synchronization. Validate every property, relationship, inverse, and
delete rule against CloudKit’s supported schema before shipping.

~~~swift
import Foundation
import SwiftData

@available(iOS 26.0, *)
@Model
final class NoteRecord {
    var title: String
    var updatedAt: Date

    init(title: String, updatedAt: Date = .now) {
        self.title = title
        self.updatedAt = updatedAt
    }
}
~~~

## 2. Configure a private CloudKit-backed model container

The identifier must match the app’s iCloud container and entitlements. Treat
container construction as an explicit startup dependency and surface failure
instead of silently presenting a schema-less in-memory context.

~~~swift
import SwiftData

@available(iOS 26.0, *)
func makeCloudKitModelConfiguration() -> ModelConfiguration {
    ModelConfiguration(
        "Primary",
        cloudKitDatabase: .private("iCloud.example.notes")
    )
}
~~~

## 3. Insert and save through a model context

A context owns insert, fetch, delete, and save operations. The surrounding
feature should translate save failures into a recoverable local state and keep
sync status separate from the user’s local edit result.

~~~swift
import Foundation
import SwiftData

@available(iOS 26.0, *)
func insertAndSaveNote(in container: ModelContainer, title: String) throws {
    let context = ModelContext(container)
    context.insert(NoteRecord(title: title))
    try context.save()
}

@available(iOS 26.0, *)
@Model
final class NoteRecord {
    var title: String
    var updatedAt: Date

    init(title: String, updatedAt: Date = .now) {
        self.title = title
        self.updatedAt = updatedAt
    }
}
~~~

## 4. Isolate writes in a model actor

Use a model actor when a store needs serialized ownership of its model
context. Keep UI observation on the main context and pass values or stable
identifiers across the actor boundary rather than sharing managed objects.

~~~swift
import Foundation
import SwiftData

@available(iOS 26.0, *)
@Model
final class NoteRecord {
    var title: String
    init(title: String) { self.title = title }
}

@available(iOS 26.0, *)
@ModelActor
actor NoteStore {
    func add(title: String) throws {
        modelContext.insert(NoteRecord(title: title))
        try modelContext.save()
    }
}
~~~

## 5. Declare versioned schemas and a migration plan

Versioned schemas make the model boundary reviewable. Use a lightweight stage
only when the change qualifies; otherwise define a custom migration stage and
test it against a real store created by the previous version.

~~~swift
import SwiftData

@available(iOS 26.0, *)
@Model
final class NoteV1 {
    var title: String
    init(title: String) { self.title = title }
}

@available(iOS 26.0, *)
@Model
final class NoteV2 {
    var title: String
    var colorName: String
    init(title: String, colorName: String = "blue") {
        self.title = title
        self.colorName = colorName
    }
}

@available(iOS 26.0, *)
enum NoteSchemaV1: VersionedSchema {
    static var versionIdentifier = Schema.Version(1, 0, 0)
    static var models: [any PersistentModel.Type] { [NoteV1.self] }
}

@available(iOS 26.0, *)
enum NoteSchemaV2: VersionedSchema {
    static var versionIdentifier = Schema.Version(2, 0, 0)
    static var models: [any PersistentModel.Type] { [NoteV2.self] }
}

@available(iOS 26.0, *)
enum NoteMigrationPlan: SchemaMigrationPlan {
    static var schemas: [any VersionedSchema.Type] {
        [NoteSchemaV1.self, NoteSchemaV2.self]
    }

    static var stages: [MigrationStage] {
        [.lightweight(fromVersion: NoteSchemaV1.self, toVersion: NoteSchemaV2.self)]
    }
}
~~~

## 6. Construct a container with a migration plan

The migration plan is part of container construction. This in-memory example
is useful for API shape checks; release evidence must also exercise a persisted
store and the exact production configuration.

~~~swift
import SwiftData

@available(iOS 26.0, *)
@Model
final class NoteRecord {
    var title: String
    init(title: String) { self.title = title }
}

@available(iOS 26.0, *)
enum NoteSchema: VersionedSchema {
    static var versionIdentifier = Schema.Version(1, 0, 0)
    static var models: [any PersistentModel.Type] { [NoteRecord.self] }
}

@available(iOS 26.0, *)
enum NotePlan: SchemaMigrationPlan {
    static var schemas: [any VersionedSchema.Type] { [NoteSchema.self] }
    static var stages: [MigrationStage] { [] }
}

@available(iOS 26.0, *)
func makeMigratingContainer() throws -> ModelContainer {
    try ModelContainer(
        for: NoteRecord.self,
        migrationPlan: NotePlan.self,
        configurations: ModelConfiguration(isStoredInMemoryOnly: true)
    )
}
~~~

## 7. Observe records with a SwiftUI query

Let SwiftUI observe the model container supplied by the app. Empty, loading,
and save-failure states still belong in the product state model; a query is
not a synchronization-complete screen.

~~~swift
import SwiftData
import SwiftUI

@available(iOS 26.0, *)
@Model
final class NoteRecord {
    var title: String
    var updatedAt: Date
    init(title: String, updatedAt: Date = .now) {
        self.title = title
        self.updatedAt = updatedAt
    }
}

@available(iOS 26.0, *)
struct NoteListView: View {
    @Query(sort: \NoteRecord.updatedAt, order: .reverse)
    private var notes: [NoteRecord]

    var body: some View {
        List(notes) { note in
            Text(note.title)
        }
    }
}
~~~

## 8. Read the iCloud account status

Account availability is a prerequisite signal, not proof that a record has
converged across devices. Keep unavailable, restricted, and no-account paths
distinct in the sync coordinator.

~~~swift
import CloudKit

@available(iOS 26.0, *)
func cloudAccountStatus() async throws -> CKAccountStatus {
    try await CKContainer.default().accountStatus()
}
~~~

## 9. Implement the CKSyncEngine delegate boundary

Sync engine events are delivered serially. The delegate should map them into
the app’s state machine and return the next batch from durable pending-change
data; it should not hide app-specific conflict policy inside a generic handler.

~~~swift
import CloudKit
import Foundation

@available(iOS 26.0, *)
final class SyncDelegate: NSObject, CKSyncEngineDelegate, @unchecked Sendable {
    func handleEvent(
        _ event: CKSyncEngine.Event,
        syncEngine: CKSyncEngine
    ) async {
        _ = event
        _ = syncEngine
    }

    func nextRecordZoneChangeBatch(
        _ context: CKSyncEngine.SendChangesContext,
        syncEngine: CKSyncEngine
    ) async -> CKSyncEngine.RecordZoneChangeBatch? {
        _ = context
        _ = syncEngine
        return nil
    }
}
~~~

## 10. Create a private-database sync engine

Create the engine early enough for its lifecycle to be owned by the app’s
sync coordinator. Automatic scheduling is indeterminate; call fetch/send for
an explicit user action only when the surrounding state and retry policy are
ready.

~~~swift
import CloudKit
import Foundation

@available(iOS 26.0, *)
final class EngineDelegate: NSObject, CKSyncEngineDelegate, @unchecked Sendable {
    func handleEvent(
        _ event: CKSyncEngine.Event,
        syncEngine: CKSyncEngine
    ) async {
        _ = event
        _ = syncEngine
    }

    func nextRecordZoneChangeBatch(
        _ context: CKSyncEngine.SendChangesContext,
        syncEngine: CKSyncEngine
    ) async -> CKSyncEngine.RecordZoneChangeBatch? {
        _ = context
        _ = syncEngine
        return nil
    }
}

@available(iOS 26.0, *)
func makeSyncEngine(delegate: EngineDelegate) -> CKSyncEngine {
    let configuration = CKSyncEngine.Configuration(
        database: CKContainer.default().privateCloudDatabase,
        stateSerialization: nil,
        delegate: delegate
    )
    return CKSyncEngine(configuration)
}

@available(iOS 26.0, *)
func requestImmediateSync(using engine: CKSyncEngine) async throws {
    try await engine.fetchChanges()
    try await engine.sendChanges()
}
~~~

## 11. Persist and restore opaque sync state

Persist the engine’s serialized state across launches. Treat the bytes as
opaque and replace them when the engine emits a new state update; do not
invent or partially edit CloudKit change tokens.

~~~swift
import CloudKit
import Foundation

@available(iOS 26.0, *)
func encodeSyncState(
    _ state: CKSyncEngine.State.Serialization
) throws -> Data {
    try JSONEncoder().encode(state)
}

@available(iOS 26.0, *)
func decodeSyncState(
    _ data: Data
) throws -> CKSyncEngine.State.Serialization {
    try JSONDecoder().decode(
        CKSyncEngine.State.Serialization.self,
        from: data
    )
}
~~~

## 12. React to state updates and account changes

An account-change event can reset engine state and discard unsaved engine
changes. Reconcile the app’s local persistence explicitly, then rebuild or
reseed pending changes according to the product’s account policy.

~~~swift
import CloudKit
import Foundation

@available(iOS 26.0, *)
func serializedState(from event: CKSyncEngine.Event) -> Data? {
    switch event {
    case .stateUpdate(let update):
        return try? JSONEncoder().encode(update.stateSerialization)
    case .accountChange:
        return nil
    default:
        return nil
    }
}
~~~

## 13. Provide a record-zone change batch

Pending changes are application-owned. The provider should return the current
record for a save and `nil` for a deletion, while the caller retains enough
metadata to retry or explain a failed operation.

~~~swift
import CloudKit

@available(iOS 26.0, *)
func makeBatch(
    pending: [CKSyncEngine.PendingRecordZoneChange],
    records: [CKRecord.ID: CKRecord]
) async -> CKSyncEngine.RecordZoneChangeBatch? {
    await CKSyncEngine.RecordZoneChangeBatch(
        pendingChanges: pending,
        recordProvider: { records[$0] }
    )
}
~~~

## 14. Surface a server-record conflict for typed review

For `serverRecordChanged`, compare the client, server, and ancestor records
before choosing a merge. A local model can ask an on-device model for a typed
proposal, but the proposal remains reviewable data—not an automatic write or a
claim that the result is semantically correct.

~~~swift
import CloudKit
import Foundation

@available(iOS 26.0, *)
func serverRecord(from error: CKError) -> CKRecord? {
    guard error.code == .serverRecordChanged else { return nil }
    return error.serverRecord
}

struct MergeProposal: Codable, Sendable {
    let recordID: String
    let localTitle: String
    let remoteTitle: String
    let proposedTitle: String
    let requiresReview: Bool
}

func makeMergeProposal(
    recordID: CKRecord.ID,
    localTitle: String,
    remoteTitle: String
) -> MergeProposal {
    MergeProposal(
        recordID: recordID.recordName,
        localTitle: localTitle,
        remoteTitle: remoteTitle,
        proposedTitle: localTitle,
        requiresReview: true
    )
}
~~~

## Acceptance checklist

- [ ] The app has a tested local-first state vocabulary: local, syncing,
      synced, retryable failure, account unavailable, conflict, and migration.
- [ ] SwiftData automatic CloudKit mirroring and custom `CKSyncEngine` use are
      selected as separate architecture lanes, not mixed casually.
- [ ] The CloudKit schema, iCloud/remote-notification capabilities, production
      container, and migration history are reviewed and reproducible.
- [ ] Model-actor ownership, pending-change durability, opaque engine-state
      persistence, account changes, transient failures, and conflict policy are
      covered by tests.
- [ ] Two physical devices prove edit, offline, retry, conflict, and
      convergence behavior; simulator compile success is not release proof.
- [ ] Sync status, conflict review, and account recovery are accessible and
      remain legible in reduced transparency, larger text, and VoiceOver.
- [ ] Any on-device AI merge proposal is typed, bounded, privacy-reviewed,
      human-reviewable, and never presented as automatic CloudKit truth.

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
- [CKSyncEngine state serialization](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/configuration/stateserialization)
- [CKSyncEngine account-change event](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/event/accountchange)
- [CKSyncEngine fetched record-zone changes](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/event/fetchedrecordzonechanges)
- [CKSyncEngine record-zone change batch](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/recordzonechangebatch)
- [CKError.serverRecordChanged](https://developer.apple.com/documentation/cloudkit/ckerror/serverrecordchanged)
- [CloudKit container capabilities](https://developer.apple.com/help/account/configure-app-capabilities/icloud/)
- [Configuring background execution modes](https://developer.apple.com/documentation/xcode/configuring-background-execution-modes)
- [Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
