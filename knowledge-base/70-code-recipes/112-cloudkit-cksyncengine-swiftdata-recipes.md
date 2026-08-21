# CloudKit, CKSyncEngine, and SwiftData synchronization recipes

## How to use these recipes

These are compile-oriented sketches. Confirm SDK availability, Swift overlays,
CloudKit record/change types, model schema rules, entitlements, actor isolation,
and production-container configuration in the selected project.

A code path that writes a local record or creates a sync request does not prove
server acceptance, conflict correctness, sharing, account safety, or projection
freshness.

## Recipe 1: local-only SwiftData configuration

Keep local-first/private apps explicit about not syncing.

~~~swift
import SwiftData

@Model
final class Note {
    @Attribute(.unique) var id: UUID
    var title: String
    var body: String
    var updatedAt: Date

    init(id: UUID = UUID(), title: String, body: String) {
        self.id = id
        self.title = title
        self.body = body
        self.updatedAt = .now
    }
}

func makeLocalContainer() throws -> ModelContainer {
    let configuration = ModelConfiguration(
        cloudKitDatabase: .none
    )
    return try ModelContainer(
        for: Note.self,
        configurations: configuration
    )
}
~~~

Verify the selected SwiftData initializer and local store behavior in the
target. This route is useful when the product should not create cloud/account
dependencies.

## Recipe 2: SwiftData private CloudKit configuration

Use an explicit container when multiple iCloud containers exist or when the
product wants its cloud boundary to be obvious.

~~~swift
func makePrivateCloudContainer() throws -> ModelContainer {
    let configuration = ModelConfiguration(
        cloudKitDatabase: .private("iCloud.com.example.notes")
    )
    return try ModelContainer(
        for: Note.self,
        configurations: configuration
    )
}
~~~

Automatic sync also needs the iCloud/CloudKit and Background Modes/Remote
notifications capabilities documented by Apple. Confirm the model schema is
CloudKit-compatible and do not initialize an unknown production container
blindly.

## Recipe 3: local record and outbox

A custom CKSyncEngine route needs an outbox that is committed with the local
record mutation.

~~~swift
struct PendingMutation: Codable, Sendable {
    enum Kind: String, Codable, Sendable {
        case save
        case delete
    }

    let id: UUID
    let recordID: String
    let zoneID: String
    let accountScope: String
    let sourceRevision: String
    let kind: Kind
    let payload: Data?
    let createdAt: Date
}

actor LocalOutbox {
    func append(_ mutation: PendingMutation) async throws {
        // Commit with the local record in one storage transaction.
    }

    func pending(for accountScope: String) async -> [PendingMutation] {
        []
    }

    func markSent(_ ids: [UUID]) async throws {
        // Remove only after the server result is durable.
    }
}
~~~

Tombstones should remain until the remote delete is acknowledged and the
reconciliation policy no longer needs them.

## Recipe 4: configure CKSyncEngine with persisted state

Apple documents that the engine's serialized state must be persisted and supplied
to the next configuration.

~~~swift
import CloudKit

actor SyncStateStore {
    private var serializedState: CKSyncEngine.State.Serialization?

    func load() -> CKSyncEngine.State.Serialization? {
        serializedState
    }

    func save(_ state: CKSyncEngine.State.Serialization) {
        serializedState = state
        // Persist atomically to the selected local store.
    }
}

final class PrivateSyncCoordinator: NSObject, CKSyncEngineDelegate {
    private let stateStore: SyncStateStore
    private let engine: CKSyncEngine

    init(stateStore: SyncStateStore) async throws {
        self.stateStore = stateStore

        let database = CKContainer(
            identifier: "iCloud.com.example.notes"
        ).privateCloudDatabase

        let configuration = CKSyncEngine.Configuration(
            database: database,
            stateSerialization: await stateStore.load(),
            delegate: self
        )

        self.engine = CKSyncEngine(configuration)
        super.init()
    }

    func handleEvent(
        _ event: CKSyncEngine.Event,
        syncEngine: CKSyncEngine
    ) async {
        switch event {
        case .stateUpdate(let update):
            await stateStore.save(update.stateSerialization)
        case .accountChange:
            await handleAccountChange()
        default:
            await handleOtherEvent(event)
        }
    }

    private func handleAccountChange() async {
        // Pause/rebuild account-scoped local persistence as policy requires.
    }

    private func handleOtherEvent(_ event: CKSyncEngine.Event) async {
        // Apply remote changes or acknowledge sent changes.
    }
}
~~~

This is intentionally a route sketch. Verify NSObject/delegate isolation and the
selected Swift API's event associated values. Do not create multiple production
engines targeting the same database.

## Recipe 5: use separate private and shared engines

Keep database scopes separate when the app supports both private and shared data.

~~~swift
func makePrivateDatabase() -> CKDatabase {
    CKContainer(identifier: "iCloud.com.example.notes").privateCloudDatabase
}

func makeSharedDatabase() -> CKDatabase {
    CKContainer(identifier: "iCloud.com.example.notes").sharedCloudDatabase
}
~~~

Create one coordinator per intended database. Do not use the public database with
CKSyncEngine. The local record's database scope must be part of authorization and
projection decisions.

## Recipe 6: add pending record changes

The engine's state owns pending CloudKit changes in the CKSyncEngine route. Add a
pending change after the local mutation is committed.

~~~swift
func enqueueLocalChange(
    recordID: CKRecord.ID,
    isDelete: Bool,
    engine: CKSyncEngine
) {
    let change: CKSyncEngine.PendingRecordZoneChange

    if isDelete {
        change = .deleteRecord(recordID)
    } else {
        change = .saveRecord(recordID)
    }

    engine.state.add(pendingRecordZoneChanges: [change])
}
~~~

The exact enum case and record-ID initializer must be verified in the selected
SDK. The important invariant is that the pending change describes a durable local
mutation and is not added for a speculative UI state.

## Recipe 7: serial event handling

Keep event handling serial and avoid starting recursive fetch/send operations
inside the event handler when the documentation warns that they can generate
additional events.

~~~swift
func handleEvent(
    _ event: CKSyncEngine.Event,
    syncEngine: CKSyncEngine
) async {
    switch event {
    case .willFetchChanges:
        await SyncLog.record(.willFetch)
    case .fetchedRecordZoneChanges(let fetched):
        await LocalReconciler.shared.apply(
            fetched,
            accountScope: "current-account"
        )
    case .sentRecordZoneChanges(let sent):
        await LocalOutbox.shared.acknowledge(sent)
    case .stateUpdate(let update):
        await SyncStateStore.shared.save(update.stateSerialization)
    case .accountChange(let change):
        await AccountCoordinator.shared.apply(change)
    default:
        await SyncLog.record(.otherEvent)
    }
}
~~~

Use the event's documented associated values and names for the selected Swift
overlay. Do not assume a fetched record is safe to apply without account/zone/
revision validation.

## Recipe 8: explicit fetch/send freshness route

Periodic synchronization is system-controlled. When a foreground action needs a
freshness boundary, use the documented manual operation.

~~~swift
func syncBeforeUserAction(
    engine: CKSyncEngine
) async throws {
    try await engine.fetchChanges(
        CKSyncEngine.FetchChangesOptions()
    )
    try await engine.sendChanges(
        CKSyncEngine.SendChangesOptions()
    )
}
~~~

Check the exact options and async signatures in the target SDK. Do not call this
after every keystroke or from inside an event handler that is already processing
a sync event.

## Recipe 9: deterministic merge policy

Keep merge decisions in a domain service rather than a view or network callback.

~~~swift
enum MergeDecision: Sendable {
    case keepLocal
    case keepRemote
    case merged(Note)
    case review(local: NoteSnapshot, remote: NoteSnapshot)
}

func decideMerge(
    local: NoteSnapshot,
    remote: NoteSnapshot
) -> MergeDecision {
    if local.body == remote.body {
        return .keepRemote
    }

    if local.userApprovedAIValue,
       remote.userApprovedAIValue == false {
        return .keepLocal
    }

    return .review(local: local, remote: remote)
}
~~~

The actual policy should use stable revision/change-tag semantics and record the
result of the decision. Never rely only on wall-clock timestamps when a conflict
has user-visible consequences.

## Recipe 10: CloudKit record projection

Map only the fields needed by the CloudKit route and keep account/scope explicit.

~~~swift
func makeRecord(
    note: NoteSnapshot,
    recordID: CKRecord.ID
) -> CKRecord {
    let record = CKRecord(
        recordType: "Note",
        recordID: recordID
    )
    record["title"] = note.title as CKRecordValue
    record["body"] = note.body as CKRecordValue
    record["sourceRevision"] = note.sourceRevision as CKRecordValue
    record["approvedAI"] = note.userApprovedAIValue as CKRecordValue
    return record
}
~~~

CloudKit record fields, optionality, asset handling, and record type schema must
match the deployed environment. Do not put raw prompts, private embeddings, or
temporary model outputs in a record without a separate privacy decision.

## Recipe 11: share a private record scope

Use CKShare for a custom zone or root record according to the intended share scope.

~~~swift
import CloudKit

func makeShare(for rootRecord: CKRecord) -> CKShare {
    let share = CKShare(rootRecord: rootRecord)
    share[CKShare.SystemFieldKey.title] = "Shared notes" as CKRecordValue
    return share
}
~~~

Save the share and records through the documented CloudKit operation, then use
the supported system sharing UI and share-link route. The owner/participant
permission state must be reconciled into local records and projections.

## Recipe 12: account-change cleanup

When the current iCloud account changes, stop using the old account's outbox and
projection.

~~~swift
actor AccountBoundary {
    func accountChanged(from old: String?, to new: String?) async {
        await SyncCoordinator.shared.cancelOperations()
        await LocalOutbox.shared.quarantine(accountScope: old)
        await ProjectionStore.shared.redactCloudState()
        await SyncStateStore.shared.reset(accountScope: new)
        await WidgetProjection.shared.reload()
    }
}
~~~

The real cleanup policy may preserve local-only records or ask for confirmation.
It must never upload old-account pending mutations to the new account.

## Recipe 13: projection after reconciliation

Advance the projection only after the local merge/commit is complete.

~~~swift
func applyRemoteAndRefresh(
    _ remote: NoteSnapshot
) async throws {
    let result = try await LocalReconciler.shared.merge(remote)
    try await ProjectionStore.shared.write(
        Projection(
            revision: result.projectionRevision,
            state: result.pending ? .pending : .synced,
            title: result.title,
            updatedAt: .now
        )
    )
    WidgetCenter.shared.reloadAllTimelines()
}
~~~

A reload request is downstream of local truth and remains subject to system
scheduling. A widget displaying synced is not proof of CloudKit acceptance unless
the local record has the corresponding server/reconciliation state.

## Recipe 14: AI proposal with source revision

Keep proposals separate from approved values.

~~~swift
struct SyncedAIProposal: Codable, Sendable {
    let id: UUID
    let recordID: String
    let sourceRevision: String
    let modelIdentifier: String
    let value: String
    let status: Status

    enum Status: String, Codable, Sendable {
        case needsReview
        case approved
        case rejected
        case stale
    }
}

func approve(
    proposal: SyncedAIProposal,
    currentSourceRevision: String
) async throws {
    guard proposal.sourceRevision == currentSourceRevision else {
        throw SyncError.sourceChanged
    }

    guard proposal.status == .needsReview else {
        throw SyncError.notReviewable
    }

    try await DomainStore.shared.commitApprovedAIValue(
        proposal.value,
        modelIdentifier: proposal.modelIdentifier
    )
}
~~~

Sync only the fields required for the product's trust and recovery story. The
destination device should revalidate current source and account state.

## Recipe 15: sync state fixture

Use deterministic fixtures for state and conflict tests.

~~~swift
struct SyncFixture {
    static let local = NoteSnapshot(
        id: "fixture-note",
        title: "Local title",
        body: "Local body",
        sourceRevision: "4",
        userApprovedAIValue: true
    )

    static let remote = NoteSnapshot(
        id: "fixture-note",
        title: "Remote title",
        body: "Remote body",
        sourceRevision: "5",
        userApprovedAIValue: false
    )
}
~~~

Fixtures prove merge and privacy logic. They do not prove iCloud account,
notification, sharing, or production schema behavior.

## Source checklist

Before adapting a recipe, verify:

- SwiftData schema and CloudKit compatibility;
- local-only versus automatic sync configuration;
- iCloud/CloudKit and Remote notifications capabilities;
- CKSyncEngine private/shared database choice;
- state serialization persistence;
- delegate event ordering and change scope;
- manual fetch/send API;
- outbox/tombstone/idempotence policy;
- account/sign-out behavior;
- CKShare scope and permissions;
- widget/activity/App Intent projection;
- AI source/model/approval provenance;
- physical two-device and release evidence.

## Sources

- [CloudKit](https://developer.apple.com/documentation/cloudkit)
- [CKSyncEngine](https://developer.apple.com/documentation/cloudkit/cksyncengine)
- [CKSyncEngine.Configuration](https://developer.apple.com/documentation/cloudkit/cksyncengine/configuration)
- [CKSyncEngineDelegate](https://developer.apple.com/documentation/cloudkit/cksyncenginedelegate)
- [CKSyncEngine.Event](https://developer.apple.com/documentation/cloudkit/cksyncengine/event)
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
