# SwiftData and CloudKit synchronization recipes

## Compile boundary

These are compile-oriented route sketches for iOS 26-era SwiftData and CloudKit work. They are not compiled in this documentation workspace and do not prove CloudKit schema compatibility, entitlements, account behavior, background delivery, conflict quality, physical-device sync, production promotion, or release readiness. Build them in a named Xcode target and verify the current SDK signatures before shipping.

Keep the local-first route usable before adding CloudKit. The smallest useful implementation is a local model, a deterministic review UI, and a recovery path for save failures. Sync is an additional state machine.

## Recipe 1: define a sync-friendly reviewable model

Keep user-authored data, generated proposals, and replication metadata separate. This shape avoids treating a model output as domain truth.

~~~swift
import SwiftData

@Model
final class NoteRecord {
    var id: UUID
    var createdAt: Date
    var title: String
    var userText: String
    var proposedText: String?
    var proposalSource: String?
    var proposalVersion: String?
    var reviewState: String
    var localRevision: Int

    init(
        title: String,
        userText: String = "",
        createdAt: Date = .now
    ) {
        self.id = UUID()
        self.createdAt = createdAt
        self.title = title
        self.userText = userText
        self.reviewState = "local"
        self.localRevision = 0
    }
}
~~~

Before enabling automatic CloudKit sync, review uniqueness, optional relationships, inverses, delete rules, field types, attachment storage, and migration behavior. A deterministic app lookup is not the same as a CloudKit uniqueness guarantee.

## Recipe 2: select the SwiftData CloudKit route

Apple documents automatic container discovery and explicit private-container selection. Use a configuration that makes the route obvious in the target:

~~~swift
import SwiftData

let cloudConfiguration = ModelConfiguration(
    cloudKitDatabase: .private("iCloud.com.example.notes")
)

let modelContainer = try ModelContainer(
    for: NoteRecord.self,
    configurations: cloudConfiguration
)
~~~

For a local-only fixture, override the route explicitly:

~~~swift
let localConfiguration = ModelConfiguration(cloudKitDatabase: .none)
let previewContainer = try ModelContainer(
    for: NoteRecord.self,
    configurations: localConfiguration
)
~~~

The target still needs the corresponding Xcode capabilities for the automatic sync route: iCloud with CloudKit, plus Background Modes with Remote notifications. Inspect the signed artifact rather than relying on source configuration.

## Recipe 3: make account availability a domain state

CloudKit account state should drive the sync presentation, not a permanent loading indicator.

~~~swift
import CloudKit

enum CloudAvailability: Sendable, Equatable {
    case available
    case localOnly
    case restricted
    case temporarilyUnavailable
    case unknown
}

func readCloudAvailability() async -> CloudAvailability {
    do {
        switch try await CKContainer.default().accountStatus() {
        case .available:
            return .available
        case .noAccount:
            return .localOnly
        case .restricted:
            return .restricted
        case .temporarilyUnavailable:
            return .temporarilyUnavailable
        @unknown default:
            return .unknown
        }
    } catch {
        return .unknown
    }
}
~~~

Pair this with an account-change observation and re-check when the app returns to the foreground. The exact observation/lifecycle integration belongs in the owning app target. Do not delete local data merely because the account is absent unless the product has an explicit, reversible policy.

## Recipe 4: persist CKSyncEngine state

Apple documents CKSyncEngine.State.Serialization as Codable and requires the app to persist it. This actor is a storage seam, not a complete database:

~~~swift
import CloudKit

actor SyncStateStore {
    private var encodedState: Data?

    func load() throws -> CKSyncEngine.State.Serialization? {
        guard let encodedState else {
            return nil
        }
        return try JSONDecoder().decode(
            CKSyncEngine.State.Serialization.self,
            from: encodedState
        )
    }

    func save(
        _ serialization: CKSyncEngine.State.Serialization
    ) throws {
        encodedState = try JSONEncoder().encode(serialization)
    }
}
~~~

Replace the in-memory Data with the app’s durable local store. Persist the engine state alongside the pending-change mapping and local records that it describes. A state blob with no corresponding local intent is not enough to recover an interrupted sync.

## Recipe 5: initialize a private sync engine

Use the latest saved serialization on launch. Pass nil only for the first initialization of the associated engine:

~~~swift
import CloudKit

final class SyncCoordinator {
    private let stateStore = SyncStateStore()
    private let delegate: SyncDelegate
    private(set) var engine: CKSyncEngine?

    init() {
        self.delegate = SyncDelegate(stateStore: stateStore)
    }

    func start() async throws {
        let savedState = try await stateStore.load()
        let configuration = CKSyncEngine.Configuration(
            database: CKContainer.default().privateCloudDatabase,
            stateSerialization: savedState,
            delegate: delegate
        )
        engine = CKSyncEngine(configuration)
    }
}
~~~

The delegate must outlive the engine and own the record provider/reducer. If the app syncs a shared database too, use a deliberate second engine and separate state/record-zone ownership; do not mix private and shared records in one untyped ledger.

## Recipe 6: handle state updates and build bounded batches

The delegate signatures and batch initializer are compile-oriented examples. The record provider must re-fetch current local data using the correct actor/context and must return nil for a record that is no longer eligible to save.

~~~swift
import CloudKit

final class SyncDelegate: NSObject, CKSyncEngineDelegate {
    private let stateStore: SyncStateStore

    init(stateStore: SyncStateStore) {
        self.stateStore = stateStore
    }

    func handleEvent(
        _ event: CKSyncEngine.Event,
        syncEngine: CKSyncEngine
    ) async {
        switch event {
        case let .stateUpdate(update):
            do {
                try await stateStore.save(update.stateSerialization)
            } catch {
                // Record a durable local recovery error.
            }

        case let .fetchedRecordZoneChanges(changes):
            // Apply record modifications and deletions transactionally.
            // Persist the local result before treating the event as applied.
            _ = changes

        case let .sentRecordZoneChanges(result):
            // Mark only result.savedRecords and result.deletedRecordIDs
            // as acknowledged. Preserve failed saves/deletes for retry or
            // conflict review.
            _ = result

        default:
            // Keep other lifecycle/account/database events in the reducer.
            break
        }
    }

    func nextRecordZoneChangeBatch(
        _ context: CKSyncEngine.SendChangesContext,
        syncEngine: CKSyncEngine
    ) async -> CKSyncEngine.RecordZoneChangeBatch? {
        let pending = syncEngine.state.pendingRecordZoneChanges

        // Filter pending to context.options and the app's active database/
        // zone policy before constructing a batch.
        return await CKSyncEngine.RecordZoneChangeBatch(
            pendingChanges: pending
        ) { recordID in
            // Re-fetch the latest local record and map it to CKRecord.
            // Return nil for a save that became obsolete or was deleted.
            makeCloudRecord(for: recordID)
        }
    }

    private func makeCloudRecord(for recordID: CKRecord.ID) -> CKRecord? {
        // Compile in the app target with the app-owned local mapper.
        nil
    }
}
~~~

The current event enum can expand over time. Keep a default branch in a route sketch, then make the production reducer explicit for all events that affect local state, account state, sent/failed changes, and recovery.

## Recipe 7: register pending changes in order

When a local operation becomes sync work, add it to the engine state in the order the domain intends:

~~~swift
func markRecordForSync(
    _ recordID: CKRecord.ID,
    engine: CKSyncEngine,
    isDeletion: Bool
) {
    let change: CKSyncEngine.PendingRecordZoneChange =
        isDeletion
        ? .deleteRecord(recordID)
        : .saveRecord(recordID)

    engine.state.add(pendingRecordZoneChanges: [change])
}
~~~

Apple documents that tracked pending changes are deduplicated and that order matters. A save followed by a delete can collapse to the delete, while a delete followed by a save can collapse to the save. Record the domain revision and user intent separately so deduplication does not erase a needed review state.

## Recipe 8: represent local and remote status in SwiftUI

Keep CloudKit types behind a small presentation model:

~~~swift
import SwiftUI

enum SyncPresentation: Equatable {
    case local
    case pending
    case synced(Date)
    case offline
    case accountUnavailable
    case conflict
    case failed
}

struct SyncStatusLabel: View {
    let status: SyncPresentation

    var body: some View {
        Label {
            Text(label)
        } icon: {
            Image(systemName: symbol)
        }
        .foregroundStyle(.secondary)
        .accessibilityValue(label)
    }

    private var label: String {
        switch status {
        case .local:
            "Saved on this device"
        case .pending:
            "Waiting to sync"
        case let .synced(date):
            "Synced \(date.formatted(date: .abbreviated, time: .shortened))"
        case .offline:
            "Offline; local changes are safe"
        case .accountUnavailable:
            "iCloud unavailable; using local storage"
        case .conflict:
            "Needs review"
        case .failed:
            "Sync needs attention"
        }
    }

    private var symbol: String {
        switch status {
        case .local: "internaldrive"
        case .pending: "arrow.triangle.2.circlepath"
        case .synced: "checkmark.icloud"
        case .offline: "wifi.slash"
        case .accountUnavailable: "person.crop.circle.badge.exclamationmark"
        case .conflict: "exclamationmark.triangle"
        case .failed: "xmark.icloud"
        }
    }
}
~~~

The label is intentionally not color-only and does not claim remote completion for the local case. Verify the final system symbol and wording in the target’s accessibility audit.

## Recipe 9: direct conflict comparison

Direct CloudKit saves can return CKError.Code.serverRecordChanged. CloudKit supplies client, server, and ancestor records through documented error keys:

~~~swift
import CloudKit

struct RecordConflict {
    let client: CKRecord?
    let server: CKRecord?
    let ancestor: CKRecord?
}

func conflict(from error: Error) -> RecordConflict? {
    guard let cloudError = error as? CKError,
          cloudError.code == .serverRecordChanged else {
        return nil
    }

    let info = cloudError.userInfo
    return RecordConflict(
        client: info[CKRecordChangedErrorClientRecordKey] as? CKRecord,
        server: info[CKRecordChangedErrorServerRecordKey] as? CKRecord,
        ancestor: info[CKRecordChangedErrorAncestorRecordKey] as? CKRecord
    )
}
~~~

This only extracts the comparison inputs. The product still needs a typed field merge, a current-record retry, a deletion rule, and a review UI. Do not silently choose the server record or client record for a user-authored field without a documented policy.

## Recipe 10: isolate AI merge proposals

An on-device model can prepare a typed proposal from selected local and remote values. Keep it separate from the record and invalidate it when either source revision changes:

~~~swift
struct MergeProposal: Sendable, Equatable {
    let localRevision: Int
    let remoteRevision: String
    let suggestedText: String
    let rationale: String
    let source: String
}

func proposalIsCurrent(
    _ proposal: MergeProposal,
    localRevision: Int,
    remoteRevision: String
) -> Bool {
    proposal.localRevision == localRevision &&
    proposal.remoteRevision == remoteRevision
}
~~~

Show the proposal as an editable third lane in the conflict surface. Require explicit confirmation before writing it to the user-authored field or sending a record. The model does not grant authority, establish identity, or prove that a save completed.

## Recipe 11: deterministic fixtures

Use fixtures to test the reducer before connecting a real container:

~~~swift
struct SyncFixture: Equatable {
    var localText: String
    var remoteText: String?
    var localRevision: Int
    var remoteRevision: String?
    var pending: Bool
    var account: String
}

let offlineEdit = SyncFixture(
    localText: "Edited on iPhone",
    remoteText: "Older value",
    localRevision: 4,
    remoteRevision: "server-3",
    pending: true,
    account: "available"
)

let conflict = SyncFixture(
    localText: "Edited here",
    remoteText: "Edited elsewhere",
    localRevision: 5,
    remoteRevision: "server-8",
    pending: true,
    account: "available"
)
~~~

Add cases for no account, restricted account, remote deletion, duplicate logical records, failed save, retry-after, partial batch success, process termination after a state update, stale AI proposal, and missing file attachment.

## Recipe 12: proof commands and stop conditions

Before calling the feature complete:

1. Compile each recipe in the named target and record the SDK/deployment target.
2. Inspect the signed entitlements for the CloudKit container and remote notifications.
3. Run local fixtures and migration tests.
4. Run the development container on two physical devices with offline edits and a conflict.
5. Test account transition, remote deletion, process restart, and a delayed notification.
6. Verify Dynamic Type, VoiceOver, Reduce Motion, reduced transparency, and lock-screen privacy.
7. Test production schema and release artifact separately.

Stop and rework the route if a snippet becomes an unbounded API dump, a local callback is described as remote proof, an AI proposal mutates data without confirmation, or a development-container result is reported as release readiness.

## Sources

- [SwiftData](https://developer.apple.com/documentation/swiftdata/)
- [ModelContainer](https://developer.apple.com/documentation/swiftdata/modelcontainer)
- [ModelConfiguration](https://developer.apple.com/documentation/swiftdata/modelconfiguration)
- [ModelConfiguration.CloudKitDatabase](https://developer.apple.com/documentation/swiftdata/modelconfiguration/cloudkitdatabase-swift.struct)
- [CloudKit sync for SwiftData](https://developer.apple.com/documentation/swiftdata/syncing-model-data-across-a-persons-devices)
- [CloudKit](https://developer.apple.com/documentation/cloudkit)
- [Deciding whether CloudKit is right for your app](https://developer.apple.com/documentation/cloudkit/deciding-whether-cloudkit-is-right-for-your-app)
- [CKSyncEngine](https://developer.apple.com/documentation/cloudkit/cksyncengine)
- [CKSyncEngine.Configuration](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/configuration)
- [Creating a sync engine configuration](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/configuration/init%28database%3Astateserialization%3Adelegate%3A%29)
- [CKSyncEngine.State](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/state-swift.class)
- [Adding pending record-zone changes](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/state-swift.class/add%28pendingrecordzonechanges%3A%29)
- [CKSyncEngine.PendingRecordZoneChange](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/pendingrecordzonechange)
- [CKSyncEngine.State.Serialization](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/state-swift.class/serialization)
- [CKSyncEngine.Event.StateUpdate](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/event/stateupdate)
- [CKSyncEngineDelegate](https://developer.apple.com/documentation/cloudkit/cksyncenginedelegate-1q7g8)
- [CKSyncEngine.RecordZoneChangeBatch](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/recordzonechangebatch)
- [Creating a record-zone change batch](https://developer.apple.com/documentation/cloudkit/cksyncengine-5sie5/recordzonechangebatch/init%28pendingchanges%3Arecordprovider%3A%29)
- [CKRecord](https://developer.apple.com/documentation/cloudkit/ckrecord)
- [Record changed error keys](https://developer.apple.com/documentation/cloudkit/record-changed-error-keys)
- [CKError.serverRecordChanged](https://developer.apple.com/documentation/cloudkit/ckerror/serverrecordchanged)
- [Enabling CloudKit in your app](https://developer.apple.com/documentation/cloudkit/enabling-cloudkit-in-your-app)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
