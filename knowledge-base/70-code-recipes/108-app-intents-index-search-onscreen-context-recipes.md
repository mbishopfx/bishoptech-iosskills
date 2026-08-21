# App Intents index, search, onscreen context, and identity code recipes

## How to use these recipes

These snippets are small route recipes, not a drop-in framework. Compile each
one in a named app target against the selected iOS SDK. App Intents macros,
property wrappers, generated protocol requirements, and availability annotations
can change between SDKs.

Every recipe keeps four layers separate:

    current store
      -> AppEntity projection
      -> system bridge
      -> app-owned navigation/action

The system bridge can be invoked without the foreground scene. The app-owned
navigation layer runs on the main actor after the current record and
authorization have been resolved.

## Recipe 1: one safe current entity

Use a small AppEntity to establish the current-record contract before adding
indexing.

~~~swift
import AppIntents
import Foundation

struct NoteRecord: Sendable, Identifiable {
    let id: UUID
    let title: String
    let folderName: String
    let accountID: String
    let isDeleted: Bool
    let isSystemDiscoverable: Bool
}

protocol NoteStore: Sendable {
    func accountID() async -> String?
    func record(id: UUID) async throws -> NoteRecord?
    func records(ids: [UUID]) async throws -> [NoteRecord]
    func search(text: String, area: NoteSearchArea) async throws -> [NoteRecord]
}

struct NoteEntity: AppEntity, Identifiable, Sendable {
    let id: UUID
    let title: String
    let folderName: String

    static var typeDisplayRepresentation: TypeDisplayRepresentation {
        TypeDisplayRepresentation(name: "Note")
    }

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(
            title: "\(title)",
            subtitle: "\(folderName)"
        )
    }

    static let defaultQuery = NoteEntityQuery()
}

struct NoteEntityQuery: EntityQuery, Sendable {
    let store: any NoteStore

    func entities(for identifiers: [NoteEntity.ID]) async throws -> [NoteEntity] {
        guard let accountID = await store.accountID() else {
            return []
        }

        return try await store.records(ids: identifiers)
            .filter {
                $0.accountID == accountID &&
                !$0.isDeleted &&
                $0.isSystemDiscoverable
            }
            .map {
                NoteEntity(
                    id: $0.id,
                    title: $0.title,
                    folderName: $0.folderName
                )
            }
    }
}
~~~

The entity query intentionally returns no private rows when the account is
unknown. A separate product may choose a sign-in error, but it must not return
the old account's cached representation.

## Recipe 2: IndexedEntity projection

Add indexing only to reviewed fields.

~~~swift
import AppIntents

struct IndexedNoteEntity: IndexedEntity, Identifiable, Sendable {
    let id: UUID

    @Property(indexingKey: "title")
    var title: String

    @Property(indexingKey: "folder")
    var folderName: String

    @ComputedProperty(indexingKey: "searchText")
    var searchText: String

    static var typeDisplayRepresentation: TypeDisplayRepresentation {
        TypeDisplayRepresentation(name: "Note")
    }

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(
            title: "\(title)",
            subtitle: "\(folderName)"
        )
    }

    static let defaultQuery = IndexedNoteEntityQuery()

    init(record: NoteRecord) {
        id = record.id
        title = record.title
        folderName = record.folderName
        searchText = "\(record.title) \(record.folderName)"
    }
}

struct IndexedNoteEntityQuery: IndexedEntityQuery, Sendable {
    let store: any NoteStore

    func entities(for identifiers: [IndexedNoteEntity.ID])
        async throws -> [IndexedNoteEntity] {
        guard let accountID = await store.accountID() else { return [] }

        return try await store.records(ids: identifiers)
            .filter {
                $0.accountID == accountID &&
                !$0.isDeleted &&
                $0.isSystemDiscoverable
            }
            .map(IndexedNoteEntity.init(record:))
    }

    // Implement the documented IndexedEntityQuery subset/all reindex
    // requirements here, using the exact selected SDK signatures.
}
~~~

If the SDK requires a different property-wrapper spelling or initialization
pattern, retain the same boundary: only the reviewed, bounded fields are
indexable.

## Recipe 3: named index donation boundary

Make index updates an actor-owned service.

~~~swift
import CoreSpotlight

actor NoteIndexService {
    let store: any NoteStore
    let searchableIndex = CSSearchableIndex(name: "com.example.notes.entities")

    init(store: any NoteStore) {
        self.store = store
    }

    func update(id: UUID) async throws {
        guard
            let accountID = await store.accountID(),
            let record = try await store.record(id: id),
            record.accountID == accountID,
            !record.isDeleted,
            record.isSystemDiscoverable
        else {
            try await remove(id: id)
            return
        }

        let entity = IndexedNoteEntity(record: record)

        // Confirm the exact selected SDK API for donating AppEntity values.
        try await searchableIndex.indexAppEntities([entity], priority: nil)
    }

    func remove(id: UUID) async throws {
        // Use the documented removal API for the same named index and entity ID.
        // Do not substitute a new random ID or delete the whole index.
    }

    func rebuild() async throws {
        guard await store.accountID() != nil else { return }

        var batch: [IndexedNoteEntity] = []
        // Stream current eligible records from the store in production.
        // Donate bounded batches and persist a projection-version checkpoint.
        _ = batch
    }
}
~~~

A missing index update should create a repair signal, not prevent the note from
being saved in the app. Indexing is an eventually consistent discovery layer.

## Recipe 4: change-event router

Route domain events to index updates and withdrawals.

~~~swift
enum NoteChange: Sendable {
    case created(UUID)
    case edited(UUID)
    case moved(UUID)
    case deleted(UUID)
    case accountChanged
    case discoveryPreferenceChanged
}

actor NoteChangeRouter {
    let index: NoteIndexService

    func apply(_ change: NoteChange) async {
        do {
            switch change {
            case .created(let id), .edited(let id), .moved(let id):
                try await index.update(id: id)
            case .deleted(let id):
                try await index.remove(id: id)
            case .accountChanged, .discoveryPreferenceChanged:
                try await index.rebuild()
            }
        } catch {
            // Record a redacted retry event. Avoid note titles and query text.
        }
    }
}
~~~

Account changes deserve a full privacy transition. A rebuild that only adds the
new account is insufficient if the previous account's entries remain in the
named index.

## Recipe 5: IndexedEntityQuery repair

Use subset and all-entity repair methods as a dedicated bridge.

~~~swift
import CoreSpotlight

struct NoteIndexRepairQuery: IndexedEntityQuery, Sendable {
    let store: any NoteStore

    func reindexEntities(
        for identifiers: [NoteEntity.ID],
        indexDescription: CSSearchableIndexDescription
    ) async throws {
        let records = try await store.records(ids: identifiers)
        let entities = records
            .filter { !$0.isDeleted && $0.isSystemDiscoverable }
            .map(IndexedNoteEntity.init(record:))

        // Pass entities and indexDescription to the exact SDK API.
        _ = (entities, indexDescription)
    }

    func reindexAllEntities(
        indexDescription: CSSearchableIndexDescription
    ) async throws {
        // Stream current authorized records; donate bounded batches.
        // Do not read the whole database into memory.
        _ = indexDescription
    }
}
~~~

The index description is part of the repair contract. Keep it aligned with the
current field schema and projection version.

## Recipe 6: current OpenIntent

Opening is a current resolution route, not a trust boundary for stale display
data.

~~~swift
struct OpenNoteIntent: OpenIntent {
    var target: IndexedNoteEntity

    @MainActor
    func perform() async throws -> some IntentResult {
        let services = AppServices.shared

        guard
            let accountID = await services.noteStore.accountID(),
            let record = try await services.noteStore.record(id: target.id),
            record.accountID == accountID,
            !record.isDeleted
        else {
            await services.navigation.openNoteRecovery()
            return .result()
        }

        await services.navigation.openNoteDetail(id: record.id)
        return .result()
    }
}
~~~

Never fuzzy-match to another note after a target ID is deleted. The correct
fallback is search/recovery, not a surprising destination.

## Recipe 7: in-app search scope

Give the system a small, localized set of meaningful scopes.

~~~swift
import AppIntents

enum NoteSearchArea: String, Sendable {
    case all
    case work
    case personal
}

struct NoteSearchIntent: ShowInAppSearchResultsIntent {
    static var searchScopes: [StringSearchScope] {
        [
            StringSearchScope(
                identifier: NoteSearchArea.all.rawValue,
                displayRepresentation: "All notes"
            ),
            StringSearchScope(
                identifier: NoteSearchArea.work.rawValue,
                displayRepresentation: "Work"
            ),
            StringSearchScope(
                identifier: NoteSearchArea.personal.rawValue,
                displayRepresentation: "Personal"
            )
        ]
    }

    var criteria: StringSearchCriteria

    @MainActor
    func perform() async throws -> some IntentResult {
        let query = criteria.searchTerm
        let area = NoteSearchArea(
            rawValue: criteria.scope?.identifier ?? NoteSearchArea.all.rawValue
        ) ?? .all

        await AppServices.shared.navigation.openNoteSearch(
            query: query,
            area: area
        )
        return .result()
    }
}
~~~

Confirm the exact criteria/scope member names in the selected SDK. The route
must preserve the search text and scope and then call the same search service
used by the app's visible search field.

## Recipe 8: one SwiftUI card annotation

Associate the smallest view that represents the entity.

~~~swift
struct NoteCard: View {
    let note: IndexedNoteEntity

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(note.title)
                .font(.headline)
            Text(note.folderName)
                .font(.subheadline)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .contentShape(Rectangle())
        .appEntityIdentifier(note.id)
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(note.title), \(note.folderName)")
    }
}
~~~

Remove the modifier while the card is a placeholder, loading row, or deleted
record. A fake placeholder ID is not harmless system context.

## Recipe 9: typed List selection context

Use domain IDs, not array positions.

~~~swift
struct NoteList: View {
    @State private var selection: IndexedNoteEntity.ID?
    let notes: [IndexedNoteEntity]

    var body: some View {
        List(notes, selection: $selection) { note in
            NoteCard(note: note)
                .appEntityIdentifier(
                    forSelectionType: IndexedNoteEntity.self,
                    identifier: note.id
                )
        }
    }
}
~~~

Compile the overload against the selected SwiftUI SDK. Then run reorder,
filter, insert, delete, and account-switch tests. A reused row must never carry
the previous note's entity ID.

## Recipe 10: custom canvas element

Use AppEntityUIElement for meaningful custom-rendered content.

~~~swift
struct NoteCanvas: View {
    let note: IndexedNoteEntity
    let bounds: CGRect
    let selected: Bool

    var body: some View {
        Canvas { context, size in
            let path = Path(
                roundedRect: bounds,
                cornerRadius: 10
            )
            context.fill(
                path,
                with: .color(selected ? .accentColor.opacity(0.25) : .clear)
            )
            context.stroke(
                path,
                with: .color(selected ? .accentColor : .secondary),
                lineWidth: selected ? 3 : 1
            )
        }
        .appEntityUIElements {
            [
                AppEntityUIElement(
                    entity: note,
                    bounds: bounds,
                    state: selected ? "selected" : "available",
                    subelements: []
                )
            ]
        }
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(note.title)
        .accessibilityAddTraits(selected ? .isSelected : [])
    }
}
~~~

Check the AppEntityUIElement initializer in the selected SDK. Update bounds on
zoom/pan, remove offscreen elements, and provide an alternate list or inspector
for users who cannot operate the canvas.

## Recipe 11: stable cross-device entity

Only use SyncableEntity when the record has a stable identity.

~~~swift
struct CrossDeviceNote: SyncableEntity, Identifiable, Sendable {
    let id: SyncableEntityIdentifier
    let title: String

    static var typeDisplayRepresentation: TypeDisplayRepresentation {
        TypeDisplayRepresentation(name: "Synced note")
    }

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(title: "\(title)")
    }

    static let defaultQuery = CrossDeviceNoteQuery()
}

struct CrossDeviceNoteQuery: EntityQuery, Sendable {
    let store: any NoteStore

    func entities(
        for identifiers: [CrossDeviceNote.ID]
    ) async throws -> [CrossDeviceNote] {
        var result: [CrossDeviceNote] = []

        for identifier in identifiers {
            guard
                let stableID = identifier.stable,
                let record = try await store.record(stableID: stableID),
                let accountID = await store.accountID(),
                record.accountID == accountID,
                !record.isDeleted
            else {
                continue
            }

            result.append(
                CrossDeviceNote(
                    id: identifier,
                    title: record.title
                )
            )
        }

        return result
    }
}
~~~

Check local/stable accessor spelling in the selected SDK. Stable identity is not
authorization. Re-resolve the ID against the current account and store.

## Recipe 12: local/stable mapping seam

Make the mapping testable without a second physical device.

~~~swift
struct NoteIdentityResolver: Sendable {
    let store: any NoteStore

    func resolve(
        _ identifier: SyncableEntityIdentifier
    ) async throws -> NoteRecord? {
        guard let accountID = await store.accountID() else {
            return nil
        }

        let record: NoteRecord?
        if let stableID = identifier.stable {
            record = try await store.record(stableID: stableID)
        } else {
            record = nil
        }

        guard
            let record,
            record.accountID == accountID,
            !record.isDeleted
        else {
            return nil
        }

        return record
    }
}
~~~

Test stable ID present, stable ID absent, account mismatch, deletion, and a local
ID that differs from the stable record ID.

## Recipe 13: account transition

Make sign-out removal explicit.

~~~swift
actor NoteAccountTransition {
    let index: NoteIndexService

    func signedOut() async throws {
        // Remove account-private entities from the named index using the
        // documented SDK removal route. Clear local stable-ID mappings that
        // could reveal old titles.
    }

    func signedIn() async throws {
        try await index.rebuild()
    }
}
~~~

The sign-out test should inspect Spotlight/Siri after the transition, not only
the app UI.

## Recipe 14: system.searchInApp schema adapter

Keep schema selection isolated so a future SDK change is small.

~~~swift
enum SystemSearchRoute {
    static let currentSchemaName = "system.searchInApp"
    static let legacySchemaName = "system.search"

    static func selectedRouteForSDK() -> String {
        // Compile-time target selection should use the current documented
        // schema. Keep this string as diagnostics only; do not reflectively
        // invoke an unavailable schema.
        currentSchemaName
    }
}
~~~

Use the actual schema macro in the App Intent declaration. The adapter is for
documentation, diagnostics, and a single migration point, not a replacement for
compile-time API checking.

## Recipe 15: same search service for app and Siri

Avoid a second ranking implementation.

~~~swift
struct NoteSearchService: Sendable {
    let store: any NoteStore

    func search(
        text: String,
        area: NoteSearchArea
    ) async throws -> [IndexedNoteEntity] {
        let normalized = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !normalized.isEmpty else { return [] }

        let records = try await store.search(
            text: normalized,
            area: area
        )

        return records
            .filter { !$0.isDeleted }
            .map(IndexedNoteEntity.init(record:))
    }
}
~~~

The visible search field and ShowInAppSearchResultsIntent should both call this
service. Unit-test the handoff by injecting a fake store and asserting that the
same query and scope arrive.

## Recipe 16: physical proof log

Store a redacted evidence record for each system route.

~~~swift
struct SystemSearchProof: Codable, Sendable {
    let appVersion: String
    let build: String
    let deviceModel: String
    let osBuild: String
    let queryLabel: String
    let scope: String
    let accountFixture: String
    let result: String
    let route: String
    let notes: String
}
~~~

Use fixture labels rather than private titles or raw spoken queries in persisted
logs. Keep screenshots and test logs in the project evidence directory, with
the device/OS/build named.

## Recipe 17: compile and runtime gates

Add explicit gates in the app layer.

~~~swift
enum SemanticDiscoveryAvailability {
    static var isSupported: Bool {
        // Use the selected SDK's availability checks for the actual route.
        true
    }

    static func fallbackRoute() -> AppFallbackRoute {
        .inAppSearch
    }
}

enum AppFallbackRoute: Sendable {
    case inAppSearch
    case localLibrary
    case unavailable
}
~~~

Do not use a hard-coded true in production. The sketch makes the decision point
visible: unsupported system discovery falls back to the normal app workflow.

## Recipe 18: route-level test checklist

A focused test suite should cover:

~~~swift
struct SemanticDiscoveryTestPlan {
    let cases = [
        "entity display representation is concise and localized",
        "indexed title update keeps the same entity ID",
        "delete removes or refuses the entity",
        "sign-out removes account-private discovery",
        "subset reindex only resolves requested current IDs",
        "all reindex is bounded and repairable",
        "system.searchInApp preserves query and scope",
        "OpenIntent re-resolves current authorization",
        "SwiftUI row annotations follow reorder and filter",
        "custom element bounds follow zoom and pan",
        "stable ID resolves on a second-device fixture",
        "account mismatch returns no private entity",
        "VoiceOver and Dynamic Type remain usable",
        "physical Spotlight/Siri/app handoff is recorded"
    ]
}
~~~

## Sources

- https://developer.apple.com/documentation/appintents/indexedentity
- https://developer.apple.com/documentation/appintents/indexedentityquery
- https://developer.apple.com/documentation/appintents/spotlight
- https://developer.apple.com/documentation/appintents/making-app-entities-available-in-spotlight
- https://developer.apple.com/documentation/appintents/showinappsearchresultsintent
- https://developer.apple.com/documentation/appintents/appschema/systemintent/searchinapp
- https://developer.apple.com/documentation/appintents/appschema/systemintent/search
- https://developer.apple.com/documentation/appintents/providing-contextual-cues-to-apple-intelligence-and-siri
- https://developer.apple.com/documentation/appintents/appentityuielement
- https://developer.apple.com/documentation/appintents/syncableentity
- https://developer.apple.com/documentation/appintents/syncableentityidentifier
- https://developer.apple.com/documentation/appintents/adopting-app-intents-to-support-system-experiences
- https://developer.apple.com/documentation/swiftui/view/appentityidentifier%28_%3A%29
- https://developer.apple.com/documentation/swiftui/view/appentityidentifier%28forselectiontype%3Aidentifier%3A%29
- https://developer.apple.com/documentation/swiftui/view/appentityuielements%28_%3A%29
- https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass
- https://developer.apple.com/documentation/swiftui/navigation
