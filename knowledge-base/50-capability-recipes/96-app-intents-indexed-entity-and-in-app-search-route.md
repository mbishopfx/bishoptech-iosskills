# App Intents indexed entities and in-app search route

## Outcome

This recipe provides a reusable route for a catalog app that wants:

- searchable AppEntity records in Spotlight and Apple Intelligence;
- incremental and repairable indexing;
- a large-catalog search handoff through system.searchInApp;
- SwiftUI list/card onscreen context;
- custom-rendered entity elements;
- stable identity across devices;
- current authorization and navigation on every open.

The code is deliberately written as SDK-facing pseudocode and compile-oriented
sketches. App Intents macros and generated requirements must be checked in the
selected Xcode/iOS SDK. A source-shaped snippet is not proof that the app
compiles or that Siri/Spotlight can invoke it.

## Route decision

Use the indexed route for durable, safe, discoverable records. Use the in-app
route for live, private, large, or richly filtered search. Many apps should use
both.

| Product condition | Route |
| --- | --- |
| Small durable safe catalog | IndexedEntity plus EntityQuery |
| Durable catalog with frequent edits | IndexedEntity plus incremental updates and repair |
| Very large or server-backed catalog | Safe index subset plus ShowInAppSearchResultsIntent |
| Private or permission-sensitive records | Minimal index or no index; current in-app search |
| Custom canvas/map/diagram | AppEntityUIElement context plus alternate list/detail |
| Cross-device continuation | SyncableEntity only with a real stable identity |
| Visual Intelligence matching | IntentValueQuery route in the companion recipe |

## Domain and service seams

Keep the entity projection independent from the persistence model.

~~~swift
import Foundation

struct LibraryRecord: Identifiable, Hashable, Sendable {
    let id: UUID
    let stableID: String?
    let title: String
    let kind: String
    let summary: String?
    let keywords: [String]
    let thumbnailData: Data?
    let accountID: String
    let isDeleted: Bool
    let canExposeToSystem: Bool
}

protocol LibraryStore: Sendable {
    func currentAccountID() async -> String?
    func record(id: UUID) async throws -> LibraryRecord?
    func record(stableID: String) async throws -> LibraryRecord?
    func records(ids: [UUID]) async throws -> [LibraryRecord]
    func allIndexableRecords() async throws -> AsyncThrowingStream<LibraryRecord, Error>
    func search(text: String, scope: LibrarySearchScope) async throws -> [LibraryRecord]
}

enum LibrarySearchScope: String, CaseIterable, Sendable {
    case all
    case projects
    case documents
    case saved
}

enum LibraryRouteError: Error, Sendable {
    case signedOut
    case notFound
    case notAuthorized
    case storeUnavailable
    case unsupportedScope
}
~~~

The store is the current source of truth. The index coordinator and AppEntity
queries depend on it, but the store should not depend on Spotlight or Siri.

## AppEntity projection

Start with a concise entity and add IndexedEntity only after the projection is
safe to expose.

~~~swift
import AppIntents

struct LibraryEntity: AppEntity, Identifiable, Sendable {
    let id: UUID
    let title: String
    let kind: String
    let summary: String?
    let stableID: String?

    static var typeDisplayRepresentation: TypeDisplayRepresentation {
        TypeDisplayRepresentation(name: "Library item")
    }

    var displayRepresentation: DisplayRepresentation {
        let subtitle = [kind, summary].compactMap { $0 }.joined(separator: " · ")
        return DisplayRepresentation(
            title: "\(title)",
            subtitle: "\(subtitle)"
        )
    }

    static let defaultQuery = LibraryEntityQuery()

    init(record: LibraryRecord) {
        id = record.id
        title = record.title
        kind = record.kind
        summary = record.summary
        stableID = record.stableID
    }
}

struct LibraryEntityQuery: EntityQuery, Sendable {
    let store: any LibraryStore

    func entities(for identifiers: [LibraryEntity.ID]) async throws -> [LibraryEntity] {
        guard let accountID = await store.currentAccountID() else {
            throw LibraryRouteError.signedOut
        }

        let records = try await store.records(ids: identifiers)
        return records
            .filter {
                !$0.isDeleted &&
                $0.accountID == accountID &&
                $0.canExposeToSystem
            }
            .map(LibraryEntity.init(record:))
    }

    func suggestedEntities() async throws -> [LibraryEntity] {
        guard await store.currentAccountID() != nil else {
            return []
        }

        // Keep suggestions short and intentional. Do not enumerate a private
        // database merely because the system asked for suggestions.
        return []
    }
}
~~~

The exact dependency injection strategy depends on the target. App Intents
queries can run outside the foreground view hierarchy, so use an extension-safe
factory or documented dependency mechanism. A process-global view model is not
a reliable entity resolver.

## IndexedEntity with safe fields

The selected SDK may require exact macro/property syntax. The structure below
shows the review boundary: searchable fields are explicit and bounded.

~~~swift
import AppIntents

struct IndexedLibraryEntity: IndexedEntity, Identifiable, Sendable {
    let id: UUID

    @Property(indexingKey: "title")
    var title: String

    @Property(indexingKey: "kind")
    var kind: String

    @ComputedProperty(indexingKey: "summary")
    var summary: String?

    @DeferredProperty(indexingKey: "keywords")
    var keywords: [String]

    static var typeDisplayRepresentation: TypeDisplayRepresentation {
        TypeDisplayRepresentation(name: "Library item")
    }

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(
            title: "\(title)",
            subtitle: "\(kind)"
        )
    }

    static let defaultQuery = IndexedLibraryEntityQuery()

    init(record: LibraryRecord) {
        id = record.id
        title = record.title
        kind = record.kind
        summary = record.summary
        keywords = record.keywords
    }
}

struct IndexedLibraryEntityQuery: IndexedEntityQuery, Sendable {
    let store: any LibraryStore

    func entities(for identifiers: [IndexedLibraryEntity.ID])
        async throws -> [IndexedLibraryEntity] {
        let records = try await store.records(ids: identifiers)
        return records
            .filter { !$0.isDeleted && $0.canExposeToSystem }
            .map(IndexedLibraryEntity.init(record:))
    }

    // The exact signatures and index-description handling are SDK-generated.
    // Implement the documented subset/all reindex methods in the target.
}
~~~

Do not index summary or keywords without reviewing every source. If a record
contains private text, create a reduced system projection instead of attaching
the whole persistence object to IndexedEntity.

## Named Spotlight index coordinator

Use a named CSSearchableIndex in the production route. The method names for
donating App Intents entities and the exact generic constraints should be
confirmed against the selected SDK.

~~~swift
import CoreSpotlight

actor LibraryIndexCoordinator {
    private let index = CSSearchableIndex(name: "com.example.library.entities")
    private let store: any LibraryStore
    private var projectionVersion = "library-index-v1"

    init(store: any LibraryStore) {
        self.store = store
    }

    func index(recordID: UUID, priority: Int? = nil) async throws {
        guard
            let accountID = await store.currentAccountID(),
            let record = try await store.record(id: recordID),
            record.accountID == accountID,
            !record.isDeleted,
            record.canExposeToSystem
        else {
            try await remove(recordID: recordID)
            return
        }

        let entity = IndexedLibraryEntity(record: record)

        // Confirm the exact SDK signature for indexAppEntities(_:priority:)
        // and the priority type in the target.
        try await index.indexAppEntities([entity], priority: priority)
        recordCheckpoint(recordID: recordID)
    }

    func remove(recordID: UUID) async throws {
        // Confirm the App Intents/Core Spotlight removal API in the target SDK.
        // The removal must use the same stable entity identifier.
        recordCheckpoint(recordID: recordID)
    }

    func reindexAll() async throws {
        guard await store.currentAccountID() != nil else {
            return
        }

        var batch: [IndexedLibraryEntity] = []
        for try await record in try await store.allIndexableRecords() {
            guard !record.isDeleted, record.canExposeToSystem else {
                continue
            }

            batch.append(IndexedLibraryEntity(record: record))

            if batch.count == 100 {
                try await donate(batch)
                batch.removeAll(keepingCapacity: true)
            }
        }

        if !batch.isEmpty {
            try await donate(batch)
        }

        recordCheckpoint(nil)
    }

    private func donate(_ entities: [IndexedLibraryEntity]) async throws {
        try await index.indexAppEntities(entities, priority: nil)
    }

    private func recordCheckpoint(_ recordID: UUID?) {
        // Persist version, timestamp, and counts in app diagnostics.
        // Never persist private record text in the diagnostic event.
        _ = (projectionVersion, recordID)
    }
}
~~~

This sketch intentionally leaves removal spelling visible as a verification
task. The contract is more important than blindly copying a signature: remove
the entity from the same named index, use the same identity, and test deletion,
sign-out, and privacy changes.

### Event routing

Domain events should feed the coordinator:

~~~swift
enum LibraryChange: Sendable {
    case inserted(UUID)
    case updated(UUID)
    case deleted(UUID)
    case sharingChanged(UUID)
    case accountChanged
    case privacySettingChanged
}

actor LibraryIndexEventRouter {
    let coordinator: LibraryIndexCoordinator

    func apply(_ change: LibraryChange) async {
        do {
            switch change {
            case .inserted(let id), .updated(let id), .sharingChanged(let id):
                try await coordinator.index(recordID: id)
            case .deleted(let id):
                try await coordinator.remove(recordID: id)
            case .accountChanged, .privacySettingChanged:
                try await coordinator.reindexAll()
            }
        } catch {
            // Persist a redacted retry reason and schedule repair.
        }
    }
}
~~~

Indexing failures should not make the record disappear from the app. They should
be observable through a repair state while the current app store continues to
work.

## IndexedEntityQuery repair route

Apple documents IndexedEntityQuery methods for reindexing requested IDs and all
entities with a CSSearchableIndexDescription.

Use a dedicated adapter so the store enumeration and index description are
testable:

~~~swift
struct LibraryIndexedQuery: IndexedEntityQuery, Sendable {
    let store: any LibraryStore

    func reindexEntities(
        for identifiers: [LibraryEntity.ID],
        indexDescription: CSSearchableIndexDescription
    ) async throws {
        let records = try await store.records(ids: identifiers)
        let entities = records
            .filter { !$0.isDeleted && $0.canExposeToSystem }
            .map(IndexedLibraryEntity.init(record:))

        // Pass entities and indexDescription through the exact SDK API.
        _ = (entities, indexDescription)
    }

    func reindexAllEntities(
        indexDescription: CSSearchableIndexDescription
    ) async throws {
        var count = 0

        for try await record in try await store.allIndexableRecords() {
            guard !record.isDeleted, record.canExposeToSystem else {
                continue
            }
            count += 1
            // Donate in bounded batches using indexDescription as documented.
        }

        _ = (count, indexDescription)
    }
}
~~~

The repair path must be safe when the store is migrating, the user is signed
out, or the index description represents an older schema. Prefer a clean,
versioned reindex over a mixed old/new projection.

## ShowInAppSearchResultsIntent

Use the in-app route for a full catalog or live search.

~~~swift
import AppIntents

struct LibrarySearchIntent: ShowInAppSearchResultsIntent {
    static var searchScopes: [StringSearchScope] {
        [
            StringSearchScope(
                identifier: LibrarySearchScope.all.rawValue,
                displayRepresentation: "All library items"
            ),
            StringSearchScope(
                identifier: LibrarySearchScope.projects.rawValue,
                displayRepresentation: "Projects"
            ),
            StringSearchScope(
                identifier: LibrarySearchScope.documents.rawValue,
                displayRepresentation: "Documents"
            )
        ]
    }

    var criteria: StringSearchCriteria

    @MainActor
    func perform() async throws -> some IntentResult {
        let query = criteria.searchTerm
        let scope = resolveScope(criteria.scope)

        guard !query.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            return .result()
        }

        // Route into app-owned navigation/search state. The target must be
        // the main app, not an app extension.
        await LibraryNavigation.shared.openSearch(query: query, scope: scope)
        return .result()
    }

    private func resolveScope(_ scope: StringSearchScope?) -> LibrarySearchScope {
        guard let scope else { return .all }
        return LibrarySearchScope(rawValue: scope.identifier) ?? .all
    }
}
~~~

The criteria property names and protocol requirements can change with SDK
generation. Confirm them with Xcode completion and the App Intents interface.
The important behavior is stable: accept the system's string criteria, validate
the scope, and hand off to the app-owned search route.

The navigation handoff must not use a global singleton as the only production
architecture. Use an app-owned route coordinator or documented scene-opening
mechanism that handles cold launch, warm launch, and an already-present screen.

## In-app search service

Reuse the same search service for ordinary in-app search and the App Intent
handoff.

~~~swift
struct LibrarySearchService: Sendable {
    let store: any LibraryStore

    func results(
        for rawQuery: String,
        scope: LibrarySearchScope
    ) async throws -> [LibraryEntity] {
        let query = rawQuery.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !query.isEmpty else { return [] }

        let records = try await store.search(text: query, scope: scope)
        return records
            .filter { !$0.isDeleted && $0.canExposeToSystem }
            .map(IndexedLibraryEntity.init(record:))
    }
}
~~~

The app-owned screen can add filters, pagination, facets, ranking explanations,
and an offline mode. It should still re-resolve an entity before opening a
detail destination.

## OpenIntent and current resolution

Every entity the system can select needs a current open route.

~~~swift
struct OpenLibraryEntityIntent: OpenIntent {
    var target: IndexedLibraryEntity

    @MainActor
    func perform() async throws -> some IntentResult {
        guard
            let accountID = await LibraryServices.shared.store.currentAccountID(),
            let record = try await LibraryServices.shared.store.record(id: target.id),
            record.accountID == accountID,
            !record.isDeleted,
            record.canExposeToSystem
        else {
            await LibraryNavigation.shared.openUnavailableEntityRecovery()
            return .result()
        }

        await LibraryNavigation.shared.openLibraryDetail(id: record.id)
        return .result()
    }
}
~~~

Treat the entity in the intent as a locator, not current truth. Re-resolve the
record, check the current account, then navigate. Do not fuzzy-match to a
different record if the ID was deleted.

## SwiftUI onscreen annotation

Annotate the row or card that represents the current entity.

~~~swift
struct LibraryRow: View {
    let entity: IndexedLibraryEntity

    var body: some View {
        HStack {
            VStack(alignment: .leading) {
                Text(entity.title)
                    .font(.headline)
                Text(entity.kind)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }

            Spacer()
        }
        .contentShape(Rectangle())
        .appEntityIdentifier(entity.id)
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(entity.title), \(entity.kind)")
    }
}
~~~

Use the selection-type overload for a typed List selection when the selected
entity type is the context the system needs.

~~~swift
struct LibraryList: View {
    @State private var selection: IndexedLibraryEntity.ID?

    let entities: [IndexedLibraryEntity]

    var body: some View {
        List(entities, selection: $selection) { entity in
            LibraryRow(entity: entity)
                .appEntityIdentifier(
                    forSelectionType: IndexedLibraryEntity.self,
                    identifier: entity.id
                )
        }
    }
}
~~~

The exact generic spelling of the selection overload must be confirmed in the
selected SwiftUI SDK. Test after sorting, filtering, insertion, deletion, and
account changes so reused rows do not retain the wrong identifier.

## Custom-rendered elements

For a Canvas, map, diagram, or Core Animation layer, expose meaningful elements
with bounds and state.

~~~swift
struct DiagramEntityElement: View {
    let entity: IndexedLibraryEntity
    let bounds: CGRect
    let isSelected: Bool

    var body: some View {
        Canvas { context, size in
            let rect = CGRect(
                x: bounds.minX,
                y: bounds.minY,
                width: bounds.width,
                height: bounds.height
            )
            context.stroke(
                Path(roundedRect: rect, cornerRadius: 8),
                with: .color(isSelected ? .accentColor : .secondary),
                lineWidth: isSelected ? 3 : 1
            )
        }
        .appEntityUIElements {
            [
                AppEntityUIElement(
                    entity: entity,
                    bounds: bounds,
                    state: isSelected ? "selected" : "available",
                    subelements: []
                )
            ]
        }
        .accessibilityLabel(entity.title)
        .accessibilityAddTraits(isSelected ? .isSelected : [])
    }
}
~~~

The initializer/property names can vary in the selected SDK; use Xcode
completion against AppEntityUIElement. The design constraints are fixed:
bounds must track rendering, state must be bounded, subelements must be
meaningful, and the accessible representation must match the visual element.

## SyncableEntity route

Use a stable identity only when the domain guarantees it across devices.

~~~swift
struct SyncableLibraryEntity: SyncableEntity, Identifiable, Sendable {
    let id: SyncableEntityIdentifier
    let title: String
    let kind: String

    static var typeDisplayRepresentation: TypeDisplayRepresentation {
        TypeDisplayRepresentation(name: "Synced library item")
    }

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(
            title: "\(title)",
            subtitle: "\(kind)"
        )
    }

    static let defaultQuery = SyncableLibraryEntityQuery()
}

struct SyncableLibraryEntityQuery: EntityQuery, Sendable {
    let store: any LibraryStore

    func entities(
        for identifiers: [SyncableLibraryEntity.ID]
    ) async throws -> [SyncableLibraryEntity] {
        guard let accountID = await store.currentAccountID() else {
            return []
        }

        var output: [SyncableLibraryEntity] = []
        for identifier in identifiers {
            guard
                let stable = identifier.stable,
                let record = try await store.record(stableID: stable),
                record.accountID == accountID,
                !record.isDeleted
            else {
                continue
            }

            output.append(
                SyncableLibraryEntity(
                    id: identifier,
                    title: record.title,
                    kind: record.kind
                )
            )
        }
        return output
    }
}
~~~

Check the exact property accessors for local and stable components in the target
SDK. If the record cannot be resolved on another device, return no entity and
let the app-owned recovery route explain sign-in, sync, or deletion.

## Index privacy and sign-out

Indexing has to respond to account transitions:

~~~swift
actor LibraryAccountBoundary {
    let indexCoordinator: LibraryIndexCoordinator
    let store: any LibraryStore

    func didSignOut() async {
        // Remove all private entities belonging to the old account using the
        // documented named-index removal API.
        // Clear any local mapping that could reveal old titles.
    }

    func didSignIn() async throws {
        // Rebuild only the new account's eligible projection.
        try await indexCoordinator.reindexAll()
    }
}
~~~

Do not wait for the next normal record edit to remove a signed-out account.
Make the account transition an explicit test fixture.

## Availability and fallback

The app should keep its core workflow usable if:

- the selected App Intents schema is unavailable;
- Spotlight indexing is disabled or stale;
- Siri/Apple Intelligence is unavailable;
- the device has no network;
- a system query is canceled;
- the index contains an old entity ID;
- the app is launched through an extension target.

The normal in-app search and detail route are the fallback. System discovery is
an enhancement, not the only way to reach a record.

## Local test seams

Build deterministic seams before physical testing:

~~~swift
struct FakeLibraryStore: LibraryStore {
    var recordsByID: [UUID: LibraryRecord]
    var recordsByStableID: [String: LibraryRecord]

    func currentAccountID() async -> String? {
        recordsByID.values.first?.accountID
    }

    func record(id: UUID) async throws -> LibraryRecord? {
        recordsByID[id]
    }

    func record(stableID: String) async throws -> LibraryRecord? {
        recordsByStableID[stableID]
    }

    func records(ids: [UUID]) async throws -> [LibraryRecord] {
        ids.compactMap { recordsByID[$0] }
    }

    func allIndexableRecords() async throws -> AsyncThrowingStream<LibraryRecord, Error> {
        AsyncThrowingStream { continuation in
            for record in recordsByID.values {
                continuation.yield(record)
            }
            continuation.finish()
        }
    }

    func search(text: String, scope: LibrarySearchScope) async throws -> [LibraryRecord] {
        recordsByID.values.filter {
            $0.title.localizedCaseInsensitiveContains(text) &&
            (scope == .all || $0.kind.localizedCaseInsensitiveContains(scope.rawValue))
        }
    }
}
~~~

Test cases should include:

- indexed title change replaces the same ID;
- delete removes the entity;
- sign-out removes private entities;
- stale ID returns no entity;
- stable ID resolves on a second-device fixture;
- unauthorized stable ID returns no entity;
- system search criteria reaches the same app search service;
- list row annotations follow reorder and filter changes;
- custom element bounds follow zoom and pan;
- empty and offline states stay honest.

## Sources

- https://developer.apple.com/documentation/appintents/indexedentity
- https://developer.apple.com/documentation/appintents/indexedentityquery
- https://developer.apple.com/documentation/appintents/spotlight
- https://developer.apple.com/documentation/appintents/making-app-entities-available-in-spotlight
- https://developer.apple.com/documentation/appintents/app-entities
- https://developer.apple.com/documentation/appintents/showinappsearchresultsintent
- https://developer.apple.com/documentation/appintents/appschema/systemintent/searchinapp
- https://developer.apple.com/documentation/appintents/providing-contextual-cues-to-apple-intelligence-and-siri
- https://developer.apple.com/documentation/appintents/appentityuielement
- https://developer.apple.com/documentation/appintents/syncableentity
- https://developer.apple.com/documentation/appintents/syncableentityidentifier
- https://developer.apple.com/documentation/appintents/adopting-app-intents-to-support-system-experiences
- https://developer.apple.com/documentation/swiftui/view/appentityidentifier%28_%3A%29
- https://developer.apple.com/documentation/swiftui/view/appentityidentifier%28forselectiontype%3Aidentifier%3A%29
- https://developer.apple.com/documentation/swiftui/view/appentityuielements%28_%3A%29
- https://developer.apple.com/documentation/corespotlight
- https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass
