# Visual Intelligence, App Intents, and entity-search route

## Outcome

Make a local-first catalog discoverable from Visual Intelligence while keeping
matching, authorization, navigation, and side effects inside explicit app-owned
boundaries.

This recipe assumes a product with records that can be matched to a scene:
landmarks, saved places, design references, products, media, documents, or a
private collection. It uses the public Apple route:

    SemanticContentDescriptor
      -> IntentValueQuery
      -> AppEntity or UnionValue projection
      -> OpenIntent
      -> native detail/search route

The code below is intentionally a route sketch. Compile it in a named app or
shared-package target against the selected SDK before relying on any generated
macro requirements or availability behavior.

## Choose the route before writing code

| Question | Local answer to record |
| --- | --- |
| What content can be matched? | A named entity type and its current store |
| What is the fallback if pixelBuffer is nil? | Labels-only candidate search, text search, or empty result |
| What can appear in a system card? | Title, subtitle, thumbnail, type, safe identifier |
| Can more than one entity type be returned? | Use a finite UnionValue or keep one entity type |
| How does a tap open? | OpenIntent re-resolves the current record |
| How does a large catalog continue? | semanticContentSearch opens the scoped app search |
| Where does matching run? | Local index, Vision/Core ML, or bounded authorized server |
| What is never retained by default? | Raw capture, private image context, and model internals |
| What proves the route? | Compile, fixture, physical system invocation, accessibility, release |

## Shared domain types

Keep the App Intent projection smaller than the persistence model. The domain
store may use SwiftData, Core Data, a file index, or another source; the route
only needs a current lookup and a bounded matcher.

~~~swift
import Foundation

struct CatalogRecord: Identifiable, Sendable {
    let id: UUID
    let name: String
    let category: String
    let context: String
    let thumbnailData: Data?
    let isAvailable: Bool
}

protocol CatalogSearching: Sendable {
    func record(id: UUID) async throws -> CatalogRecord?
    func search(labels: [String], pixelBuffer: CVReadOnlyPixelBuffer?) async throws -> [CatalogRecord]
    func searchAll(labels: [String], pixelBuffer: CVReadOnlyPixelBuffer?) async throws -> [CatalogRecord]
}

enum VisualSearchFailure: Error, Sendable {
    case unavailable
    case timedOut
    case notAuthorized
    case malformedInput
}
~~~

CVReadOnlyPixelBuffer is shown to make the capture boundary visible. Add the
appropriate Core Video import and exact SDK type spelling in the target. The
protocol is a design seam: a test double can return deterministic records, and
the production implementation can use labels, Vision, Core ML, or a server.

Do not pass a mutable view model or a UI-bound persistence context through this
protocol. The matcher should be actor-safe and cancellable.

## App entity projection

The system-facing entity should provide concise localized display information
and a query that re-resolves current records.

~~~swift
import AppIntents

struct CatalogEntity: AppEntity, Identifiable, Sendable {
    let id: UUID
    let name: String
    let category: String
    let context: String
    let thumbnailData: Data?

    static var typeDisplayRepresentation: TypeDisplayRepresentation {
        TypeDisplayRepresentation(name: "Catalog item")
    }

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(
            title: "\(name)",
            subtitle: "\(context) · \(category)",
            image: thumbnailData.map { .init(data: $0) }
        )
    }

    static let defaultQuery = CatalogEntityQuery()

    init(record: CatalogRecord) {
        id = record.id
        name = record.name
        category = record.category
        context = record.context
        thumbnailData = record.thumbnailData
    }
}

struct CatalogEntityQuery: EntityQuery, Sendable {
    // Inject the current store through the target’s documented dependency path.
    let store: any CatalogSearching

    func entities(for identifiers: [CatalogEntity.ID]) async throws -> [CatalogEntity] {
        var result: [CatalogEntity] = []
        result.reserveCapacity(identifiers.count)

        for id in identifiers {
            guard let record = try await store.record(id: id), record.isAvailable else {
                continue
            }
            result.append(CatalogEntity(record: record))
        }

        return result
    }

    func suggestedEntities() async throws -> [CatalogEntity] {
        // Keep suggestions bounded and privacy-reviewed in the real store.
        return []
    }
}
~~~

The initializer/dependency wiring is deliberately left target-specific. In a
real App Intents project, use the documented App Intents dependency mechanism or
an extension-safe factory. Never use a process-global UI singleton as the only
source of truth for an entity query.

## Label normalization and candidate generation

Labels are general system-provided categories. Normalize them only to compare
against the app’s own taxonomy. Keep the mapping versioned so a change can be
regression-tested.

~~~swift
struct LabelVocabulary: Sendable {
    let version: String
    let aliases: [String: Set<String>]

    func candidates(for labels: [String]) -> Set<String> {
        labels.reduce(into: Set<String>()) { result, label in
            let normalized = label.trimmingCharacters(in: .whitespacesAndNewlines)
                .lowercased()

            result.insert(normalized)
            result.formUnion(aliases[normalized, default: []])
        }
    }
}

let vocabulary = LabelVocabulary(
    version: "visual-label-map-1",
    aliases: [
        "tower": ["landmark", "building"],
        "building": ["architecture", "landmark"],
        "book": ["publication", "reading"]
    ]
)
~~~

This mapping is not a translation service and does not turn a general label
into an identified object. Treat it as candidate generation only.

## The Visual Intelligence query

Implement one descriptor query. Use the descriptor’s labels and optional pixel
buffer, then return a bounded list of entity values.

~~~swift
import AppIntents
import VisualIntelligence

struct CatalogIntentValueQuery: IntentValueQuery, Sendable {
    let store: any CatalogSearching
    let vocabulary: LabelVocabulary

    func values(for input: SemanticContentDescriptor) async throws -> [CatalogEntity] {
        let labels = input.labels
        let candidates = vocabulary.candidates(for: labels)
        let buffer = input.pixelBuffer

        guard !candidates.isEmpty || buffer != nil else {
            return []
        }

        let records = try await store.search(labels: Array(candidates), pixelBuffer: buffer)

        return records
            .filter(\.isAvailable)
            .prefix(20)
            .map(CatalogEntity.init(record:))
    }
}
~~~

The exact query registration and dependency initialization must match the
selected SDK and target. The important contract is that values(for:) receives
SemanticContentDescriptor, handles the optional buffer, and returns current app
entities rather than persistence objects or arbitrary text.

Return fewer highly relevant results when possible. A large catalog belongs in
the app-owned continuation route, not in an unbounded system query.

## Multiple entity types with UnionValue

If the matcher can return a landmark or a collection, model that finite choice
explicitly. Every returned entity type needs its own opening path.

~~~swift
@UnionValue
enum VisualSearchResult: Sendable {
    case item(CatalogEntity)
    case collection(CollectionEntity)
}

struct CollectionEntity: AppEntity, Sendable {
    let id: UUID
    let name: String
    let itemCount: Int

    static var typeDisplayRepresentation: TypeDisplayRepresentation {
        TypeDisplayRepresentation(name: "Collection")
    }

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(
            title: "\(name)",
            subtitle: "\(itemCount) items"
        )
    }

    static let defaultQuery = CollectionEntityQuery()
}

struct VisualSearchUnionQuery: IntentValueQuery, Sendable {
    let store: any CatalogSearching
    let vocabulary: LabelVocabulary

    func values(for input: SemanticContentDescriptor) async throws -> [VisualSearchResult] {
        let candidates = vocabulary.candidates(for: input.labels)
        guard !candidates.isEmpty || input.pixelBuffer != nil else {
            return []
        }

        let items = try await store.search(
            labels: Array(candidates),
            pixelBuffer: input.pixelBuffer
        )

        return items
            .filter(\.isAvailable)
            .prefix(10)
            .map { .item(CatalogEntity(record: $0)) }
    }
}
~~~

The CollectionEntityQuery is not shown in full; it must resolve current
collection identifiers and omit deleted or unauthorized collections. Do not
return a union case that the app cannot open in the installed version.

## Open the selected entity

Use OpenIntent as a navigation/useful-inspection route. Re-resolve the ID and
set app navigation state only after current authorization and existence checks.

~~~swift
struct OpenCatalogEntityIntent: OpenIntent, Sendable {
    static let title: LocalizedStringResource = "Open catalog item"

    @Parameter(title: "Item")
    var target: CatalogEntity

    let store: any CatalogSearching
    let navigator: any CatalogNavigator

    func perform() async throws -> some IntentResult {
        guard let record = try await store.record(id: target.id), record.isAvailable else {
            await navigator.showUnavailable(itemID: target.id)
            return .result()
        }

        await navigator.showDetail(for: CatalogEntity(record: record))
        return .result()
    }
}

protocol CatalogNavigator: Sendable {
    func showDetail(for item: CatalogEntity) async
    func showUnavailable(itemID: UUID) async
}
~~~

If the union query returns CollectionEntity, add a separate OpenIntent that
resolves and opens the collection. Opening should not trigger purchase, sharing,
deletion, messaging, unlocking, or another irreversible mutation.

## Continue to full in-app search

For a large catalog, use the documented Visual Intelligence schema for a
“More results” destination. The schema supplies the semantic content parameter;
the app’s perform() should navigate to a scoped search state.

~~~swift
@AppIntent(schema: .visualIntelligence.semanticContentSearch)
struct ContinueCatalogVisualSearchIntent: AppIntent, Sendable {
    static let title: LocalizedStringResource = "Search catalog"
    static let openAppWhenRun = true

    var semanticContent: SemanticContentDescriptor
    let navigator: any CatalogNavigator

    func perform() async throws -> some IntentResult {
        let context = VisualSearchContext(
            labels: semanticContent.labels,
            hasPixelBuffer: semanticContent.pixelBuffer != nil
        )

        await navigator.showSearch(context: context)
        return .result()
    }
}

struct VisualSearchContext: Sendable, Hashable {
    let labels: [String]
    let hasPixelBuffer: Bool
}

extension CatalogNavigator {
    func showSearch(context: VisualSearchContext) async {
        // App-owned route: set scoped search state and recompute ranked results.
        // Do not persist the raw pixel buffer by default.
    }
}
~~~

The exact generated macro requirements may change with the SDK. Do not make a
production claim from this sketch until it compiles in the target.

## Hybrid local matcher

Keep the query fast by separating candidate generation, image representation,
ranking, and current record lookup.

~~~swift
struct RankedMatch: Sendable {
    let id: UUID
    let labelScore: Double
    let imageScore: Double?
    let isAvailable: Bool
}

protocol LocalImageMatcher: Sendable {
    func rank(pixelBuffer: CVReadOnlyPixelBuffer, candidateIDs: [UUID]) async throws -> [UUID: Double]
}

actor LocalCatalogSearch: CatalogSearching {
    let recordsByID: [UUID: CatalogRecord]
    let matcher: any LocalImageMatcher

    func record(id: UUID) async throws -> CatalogRecord? {
        recordsByID[id]
    }

    func search(labels: [String], pixelBuffer: CVReadOnlyPixelBuffer?) async throws -> [CatalogRecord] {
        let labelSet = Set(labels)
        let candidates = recordsByID.values.filter { record in
            record.isAvailable && (labelSet.isEmpty || labelSet.contains(record.category.lowercased()))
        }

        guard let pixelBuffer else {
            return Array(candidates.prefix(20))
        }

        let scores = try await matcher.rank(
            pixelBuffer: pixelBuffer,
            candidateIDs: candidates.map(\.id)
        )

        return candidates
            .sorted { scores[$0.id, default: -.infinity] > scores[$1.id, default: -.infinity] }
            .prefix(20)
            .map { $0 }
    }

    func searchAll(labels: [String], pixelBuffer: CVReadOnlyPixelBuffer?) async throws -> [CatalogRecord] {
        try await search(labels: labels, pixelBuffer: pixelBuffer)
    }
}
~~~

The image matcher can be implemented with Vision feature prints, a compiled
Core ML model, a local embedding index, or another deterministic method. Keep
the model revision, preprocessing, threshold, candidate limit, and feature
storage policy in the route configuration. Precompute catalog representations
when doing so improves latency and memory behavior.

Do not let a model score bypass the app’s current availability or account
filter. Rank only records that the current user is allowed to see.

## Privacy-safe diagnostics

Log route state, not capture content:

~~~swift
struct VisualSearchDiagnostic: Sendable {
    let vocabularyVersion: String
    let labelCount: Int
    let hasPixelBuffer: Bool
    let candidateCount: Int
    let resultCount: Int
    let matcher: String
    let failureCode: String?
}
~~~

Do not add raw labels, pixel hashes, account IDs, entity names, thumbnails, or
prompt/model context to telemetry by default. If product analytics needs to
measure the feature, use aggregate counts and a documented retention policy.

## Availability gate

Use an explicit capability state in the app so system discovery and in-app
search can degrade independently.

~~~swift
enum VisualSearchAvailability: Equatable, Sendable {
    case available
    case sdkUnavailable
    case runtimeUnavailable
    case matcherUnavailable
    case signedOut
}

struct VisualSearchCapability: Sendable {
    let availability: VisualSearchAvailability
    let supportsLabels: Bool
    let supportsPixelSearch: Bool

    var canSearchInApp: Bool {
        availability == .available || availability == .matcherUnavailable
    }
}
~~~

The runtime state is product-specific. Do not invent a public Visual Intelligence
availability Boolean from the fact that the app compiled. Record the exact OS,
device, language, system settings, and signed target state in physical-device
evidence.

## SwiftUI handoff destination

The app-owned destination should make the visual context and current entity
state explicit without retaining the raw capture.

~~~swift
import SwiftUI

struct CatalogDetailView: View {
    let item: CatalogEntity
    let matchReason: String?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                Text(item.name)
                    .font(.largeTitle.weight(.semibold))

                Text(item.context)
                    .foregroundStyle(.secondary)

                if let matchReason {
                    Label(matchReason, systemImage: "viewfinder")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }

                // Keep canonical metadata, generated explanation, and actions
                // in separate sections.
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding()
        }
        .navigationTitle(item.name)
        .navigationBarTitleDisplayMode(.inline)
    }
}
~~~

The final visual hierarchy should be reviewed against the selected OS’s native
controls and Liquid Glass guidance. The recipe does not claim a particular
material modifier or transition signature compiles in every deployment target.

## Test doubles and deterministic fixtures

Build the system route around a fake matcher before connecting Vision or Core ML.

~~~swift
struct FixtureCatalog: CatalogSearching {
    let records: [CatalogRecord]

    func record(id: UUID) async throws -> CatalogRecord? {
        records.first { $0.id == id }
    }

    func search(labels: [String], pixelBuffer: CVReadOnlyPixelBuffer?) async throws -> [CatalogRecord] {
        records.filter { $0.isAvailable }.prefix(20).map { $0 }
    }

    func searchAll(labels: [String], pixelBuffer: CVReadOnlyPixelBuffer?) async throws -> [CatalogRecord] {
        records.filter { $0.isAvailable }.map { $0 }
    }
}
~~~

Fixture cases should cover labels-only input, pixel-only input, both inputs,
neither input, a deleted ID, an unauthorized record, a union result, more than
the display limit, and a matcher timeout. The fixture route proves domain
mapping and state handling; only a signed system invocation proves that Visual
Intelligence calls the query and renders the card.

## Acceptance checklist

- [ ] The selected SDK compiles the AppIntents and VisualIntelligence imports in
      the named target.
- [ ] The actual generated requirements for the visual-intelligence schema are
      checked with Xcode completion/compiler diagnostics.
- [ ] The entity projection contains only localized, privacy-reviewed fields.
- [ ] The query works when labels or pixelBuffer are absent.
- [ ] The result limit and timeout are explicit.
- [ ] Union cases are finite and each has an open route.
- [ ] Open intents re-resolve the current record and never hide a mutation.
- [ ] The More results route lands in a scoped in-app search view.
- [ ] The matcher is deterministic in fixtures and versioned in production.
- [ ] Raw captures/features are not logged or retained by default.
- [ ] VoiceOver, Dynamic Type, reduced effects, keyboard/pointer, and empty
      states are tested.
- [ ] A signed physical device verifies Visual Intelligence invocation and app
      handoff separately from compile and fixture evidence.

## Sources

- [Visual Intelligence](https://developer.apple.com/documentation/visualintelligence)
- [Integrating your app with visual intelligence](https://developer.apple.com/documentation/visualintelligence/integrating-your-app-with-visual-intelligence)
- [SemanticContentDescriptor](https://developer.apple.com/documentation/visualintelligence/semanticcontentdescriptor)
- [SemanticContentDescriptor.labels](https://developer.apple.com/documentation/visualintelligence/semanticcontentdescriptor/labels)
- [Visual intelligence App Intents domain](https://developer.apple.com/documentation/appintents/app-schema-domain-visual-intelligence)
- [IntentValueQuery](https://developer.apple.com/documentation/appintents/intentvaluequery)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- [EntityQuery](https://developer.apple.com/documentation/appintents/entityquery)
- [DisplayRepresentation](https://developer.apple.com/documentation/appintents/displayrepresentation)
- [OpenIntent](https://developer.apple.com/documentation/appintents/openintent)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [Adopting App Intents to support system experiences](https://developer.apple.com/documentation/appintents/adopting-app-intents-to-support-system-experiences)
- [Vision](https://developer.apple.com/documentation/vision)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Searching](https://developer.apple.com/design/human-interface-guidelines/searching)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
