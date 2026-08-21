# App Intents and Visual Intelligence code recipes

## Use these as route sketches

These snippets are compile-oriented starting points for a named iOS target. They
are not claims that a generic project compiles unchanged against every iOS 26
SDK seed, nor do they prove that Visual Intelligence invokes the route.

The recurring boundary is:

    system descriptor
      -> bounded matching service
      -> app entity projection
      -> system result
      -> current entity re-resolution
      -> app-owned detail/search
      -> explicit side effect, if any

Keep the matcher, entity/query layer, navigation layer, and domain mutation
separate.

## Recipe 1: minimal AppEntity projection

~~~swift
import AppIntents
import Foundation

struct ReferenceEntity: AppEntity, Sendable {
    let id: UUID
    let title: String
    let subtitle: String

    static var typeDisplayRepresentation: TypeDisplayRepresentation {
        TypeDisplayRepresentation(name: "Reference")
    }

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(
            title: "\(title)",
            subtitle: "\(subtitle)"
        )
    }

    static let defaultQuery = ReferenceEntityQuery()
}

struct ReferenceEntityQuery: EntityQuery, Sendable {
    let store: any ReferenceStore

    func entities(for identifiers: [ReferenceEntity.ID]) async throws -> [ReferenceEntity] {
        try await identifiers.compactMap { id in
            guard let record = try await store.currentReference(id: id) else {
                return nil
            }
            return ReferenceEntity(
                id: record.id,
                title: record.title,
                subtitle: record.subtitle
            )
        }
    }

    func suggestedEntities() async throws -> [ReferenceEntity] {
        []
    }
}

protocol ReferenceStore: Sendable {
    func currentReference(id: UUID) async throws -> ReferenceRecord?
}

struct ReferenceRecord: Sendable {
    let id: UUID
    let title: String
    let subtitle: String
}
~~~

Compile notes:

- Verify the exact EntityQuery requirements in the selected SDK.
- Keep the query dependency independent of a SwiftUI scene.
- Omit records that no longer exist or are not authorized.
- Add localized resources for user-facing display strings.
- Do not expose persistence relationships or private notes by default.

## Recipe 2: descriptor normalization

~~~swift
import VisualIntelligence

struct DescriptorInput: Sendable {
    let labels: [String]
    let pixelBuffer: CVReadOnlyPixelBuffer?
}

func descriptorInput(
    from descriptor: SemanticContentDescriptor
) -> DescriptorInput {
    DescriptorInput(
        labels: descriptor.labels.map {
            $0.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        },
        pixelBuffer: descriptor.pixelBuffer
    )
}
~~~

The labels are coarse system classifications. This helper only normalizes them
for the app’s own matching policy. It does not translate labels, add synonyms,
or identify a named object.

## Recipe 3: labels-only fallback

~~~swift
struct LabelCandidate: Sendable {
    let category: String
    let score: Int
}

struct LabelMatcher: Sendable {
    let categoryAliases: [String: Set<String>]

    func candidates(labels: [String]) -> [LabelCandidate] {
        labels.compactMap { label in
            let normalized = label.lowercased()
            let matchingCategory = categoryAliases.first { _, aliases in
                aliases.contains(normalized)
            }?.key

            guard let matchingCategory else {
                return nil
            }

            return LabelCandidate(category: matchingCategory, score: 1)
        }
    }
}
~~~

Use this route when a catalog has strong category metadata or when a pixel
buffer is unavailable. Treat its output as candidate discovery, not object
identity. Return no result when the candidate is too broad to be useful.

## Recipe 4: bounded pixel-buffer matcher seam

~~~swift
protocol PixelBufferMatcher: Sendable {
    func rank(
        pixelBuffer: CVReadOnlyPixelBuffer,
        candidateIDs: [UUID]
    ) async throws -> [UUID: Double]
}

struct BoundedPixelSearch: Sendable {
    let matcher: any PixelBufferMatcher
    let maxCandidates: Int
    let maxResults: Int
    let minimumScore: Double

    func search(
        pixelBuffer: CVReadOnlyPixelBuffer,
        candidates: [UUID]
    ) async throws -> [UUID] {
        let boundedCandidates = Array(candidates.prefix(maxCandidates))
        let scores = try await matcher.rank(
            pixelBuffer: pixelBuffer,
            candidateIDs: boundedCandidates
        )

        return scores
            .filter { $0.value >= minimumScore }
            .sorted { $0.value > $1.value }
            .prefix(maxResults)
            .map(\.key)
    }
}
~~~

The matcher can wrap Vision feature prints, Core ML, a local embedding index, or
another deterministic implementation. Record preprocessing, model/index
revision, threshold, candidate limit, and device observations. Never use a
feature score as authorization.

## Recipe 5: hybrid descriptor search

~~~swift
struct VisualCandidate: Sendable {
    let id: UUID
    let labelScore: Double
    let imageScore: Double?
}

struct HybridRanker: Sendable {
    let labelWeight: Double
    let imageWeight: Double
    let minimumScore: Double

    func rank(_ candidates: [VisualCandidate]) -> [UUID] {
        candidates
            .map { candidate in
                let imageScore = candidate.imageScore ?? 0
                let total = candidate.labelScore * labelWeight
                    + imageScore * imageWeight
                return (candidate.id, total)
            }
            .filter { $0.1 >= minimumScore }
            .sorted { $0.1 > $1.1 }
            .map(\.0)
    }
}
~~~

Keep this deterministic and versioned. If the catalog changes, a record becomes
private, or the model revision changes, recompute the current candidate set
before mapping IDs to entities.

## Recipe 6: IntentValueQuery route

~~~swift
import AppIntents
import VisualIntelligence

struct ReferenceIntentValueQuery: IntentValueQuery, Sendable {
    let store: any ReferenceStore
    let searcher: any ReferenceMatcher

    func values(for input: SemanticContentDescriptor) async throws -> [ReferenceEntity] {
        guard !input.labels.isEmpty || input.pixelBuffer != nil else {
            return []
        }

        let records = try await searcher.search(
            labels: input.labels,
            pixelBuffer: input.pixelBuffer
        )

        return records
            .filter(\.isAvailable)
            .prefix(20)
            .map {
                ReferenceEntity(
                    id: $0.id,
                    title: $0.title,
                    subtitle: $0.subtitle
                )
            }
    }
}

protocol ReferenceMatcher: Sendable {
    func search(
        labels: [String],
        pixelBuffer: CVReadOnlyPixelBuffer?
    ) async throws -> [ReferenceRecord]
}

extension ReferenceRecord {
    var isAvailable: Bool {
        true
    }
}
~~~

The exact dependency wiring is target-specific. Keep the query fast and
cancellable, and do not require a visible app scene to resolve an entity.

## Recipe 7: union result

~~~swift
@UnionValue
enum ReferenceSearchResult: Sendable {
    case reference(ReferenceEntity)
    case collection(ReferenceCollectionEntity)
}

struct ReferenceCollectionEntity: AppEntity, Sendable {
    let id: UUID
    let title: String
    let count: Int

    static var typeDisplayRepresentation: TypeDisplayRepresentation {
        TypeDisplayRepresentation(name: "Reference collection")
    }

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(
            title: "\(title)",
            subtitle: "\(count) references"
        )
    }

    static let defaultQuery = ReferenceCollectionQuery()
}

struct ReferenceUnionQuery: IntentValueQuery, Sendable {
    let matcher: any ReferenceMatcher

    func values(for input: SemanticContentDescriptor) async throws -> [ReferenceSearchResult] {
        let records = try await matcher.search(
            labels: input.labels,
            pixelBuffer: input.pixelBuffer
        )

        return records.prefix(10).map {
            .reference(
                ReferenceEntity(
                    id: $0.id,
                    title: $0.title,
                    subtitle: $0.subtitle
                )
            )
        }
    }
}
~~~

Use a union only for a finite semantic set. Add an OpenIntent and current query
for every returned case. If a type cannot be opened in the installed app, omit
it from the query.

## Recipe 8: OpenIntent with current re-resolution

~~~swift
struct OpenReferenceIntent: OpenIntent, Sendable {
    static let title: LocalizedStringResource = "Open reference"

    @Parameter(title: "Reference")
    var target: ReferenceEntity

    let store: any ReferenceStore
    let navigator: any ReferenceNavigator

    func perform() async throws -> some IntentResult {
        guard let current = try await store.currentReference(id: target.id),
              current.isAvailable else {
            await navigator.showUnavailable(id: target.id)
            return .result()
        }

        await navigator.showReference(
            ReferenceEntity(
                id: current.id,
                title: current.title,
                subtitle: current.subtitle
            )
        )
        return .result()
    }
}

protocol ReferenceNavigator: Sendable {
    func showReference(_ reference: ReferenceEntity) async
    func showUnavailable(id: UUID) async
}
~~~

Do not use OpenIntent to perform a hidden write. If opening needs an account,
permission, or record refresh, surface the recovery state in the app.

## Recipe 9: semanticContentSearch continuation

~~~swift
@AppIntent(schema: .visualIntelligence.semanticContentSearch)
struct ContinueReferenceSearchIntent: AppIntent, Sendable {
    static let title: LocalizedStringResource = "Search references"
    static let openAppWhenRun = true

    var semanticContent: SemanticContentDescriptor
    let navigator: any ReferenceNavigator

    func perform() async throws -> some IntentResult {
        let state = ReferenceSearchState(
            labels: semanticContent.labels,
            includesImageContext: semanticContent.pixelBuffer != nil
        )

        await navigator.showSearch(state: state)
        return .result()
    }
}

struct ReferenceSearchState: Hashable, Sendable {
    let labels: [String]
    let includesImageContext: Bool
}

extension ReferenceNavigator {
    func showSearch(state: ReferenceSearchState) async {
        // Set an app-owned, bounded search state. Do not persist raw capture
        // data unless the person explicitly saves it.
    }
}
~~~

Use the app’s normal searchable/navigation composition after the handoff. The
search scope should be visible, and clearing visual context should lead to a
normal text search.

## Recipe 10: safe entity display

~~~swift
struct SafeReferenceProjection: Sendable {
    let title: String
    let subtitle: String
    let thumbnail: Data?
}

func safeProjection(
    record: ReferenceRecord,
    account: AccountScope
) -> SafeReferenceProjection? {
    guard record.accountID == account.id, record.isAvailable else {
        return nil
    }

    return SafeReferenceProjection(
        title: record.publicTitle,
        subtitle: record.publicSubtitle,
        thumbnail: record.thumbnailData
    )
}

struct AccountScope: Sendable {
    let id: UUID
}
~~~

Treat title, subtitle, and thumbnail as system-facing data. Do not include
private notes, access tokens, raw model context, exact location, or unbounded
user text unless the product has specifically reviewed that exposure.

## Recipe 11: privacy-safe diagnostics

~~~swift
struct VisualSearchMetrics: Sendable {
    let labelCount: Int
    let hasPixelBuffer: Bool
    let candidateCount: Int
    let resultCount: Int
    let queryDurationMS: Int
    let matcherRevision: String
    let failure: String?
}

func makeMetrics(
    labels: [String],
    hasPixelBuffer: Bool,
    candidateCount: Int,
    resultCount: Int,
    durationMS: Int,
    revision: String,
    failure: String?
) -> VisualSearchMetrics {
    VisualSearchMetrics(
        labelCount: labels.count,
        hasPixelBuffer: hasPixelBuffer,
        candidateCount: candidateCount,
        resultCount: resultCount,
        queryDurationMS: durationMS,
        matcherRevision: revision,
        failure: failure
    )
}
~~~

Keep aggregate route measurements separate from raw input. If debugging requires
a sample, create a redacted, user-approved fixture outside production telemetry.

## Recipe 12: app-owned search state

~~~swift
import Observation

@MainActor
@Observable
final class ReferenceSearchModel {
    var query = ""
    var visualLabels: [String] = []
    var hasVisualContext = false
    var results: [ReferenceEntity] = []
    var status: Status = .idle

    enum Status: Equatable {
        case idle
        case searching
        case empty
        case unavailable
        case failed
    }

    func startVisualSearch(labels: [String], hasPixelBuffer: Bool) {
        visualLabels = labels
        hasVisualContext = hasPixelBuffer || !labels.isEmpty
        query = ""
        status = .searching
    }

    func clearVisualContext() {
        visualLabels = []
        hasVisualContext = false
        status = .idle
    }
}
~~~

The model holds sanitized navigation/search state, not a raw pixel buffer. Keep
canonical results in the domain store and refresh them when the search changes.

## Recipe 13: SwiftUI detail shell

~~~swift
import SwiftUI

struct ReferenceDetailView: View {
    let reference: ReferenceEntity
    let reason: String?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                Text(reference.title)
                    .font(.largeTitle.weight(.semibold))

                Text(reference.subtitle)
                    .foregroundStyle(.secondary)

                if let reason {
                    Label(reason, systemImage: "viewfinder")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }

                // Add canonical content, source metadata, and explicit actions.
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding()
        }
        .navigationTitle(reference.title)
        .navigationBarTitleDisplayMode(.inline)
    }
}
~~~

Use native navigation and semantic controls. Add Liquid Glass only for
functional grouping in the selected SDK; test the same hierarchy with reduced
transparency and without decorative effects.

## Recipe 14: fixture matcher

~~~swift
struct FixtureReferenceMatcher: ReferenceMatcher {
    let fixture: [ReferenceRecord]

    func search(
        labels: [String],
        pixelBuffer: CVReadOnlyPixelBuffer?
    ) async throws -> [ReferenceRecord] {
        fixture.filter(\.isAvailable).prefix(20).map { $0 }
    }
}
~~~

Fixture expectations:

- no labels and no buffer returns an empty array when the contract requires it;
- labels-only produces a deterministic candidate order;
- pixel-only calls the fake image matcher path;
- unavailable records are filtered;
- result count never exceeds the query limit;
- an entity selected after deletion produces an unavailable state;
- the same input and matcher revision produce the same order.

## Recipe 15: explicit side-effect boundary

~~~swift
struct SaveVisualMatchIntent: AppIntent, Sendable {
    static let title: LocalizedStringResource = "Save visual match"

    @Parameter(title: "Reference")
    var reference: ReferenceEntity

    let store: any ReferenceStore
    let confirmation: any ConfirmationService

    func perform() async throws -> some IntentResult {
        guard let current = try await store.currentReference(id: reference.id),
              current.isAvailable else {
            return .result()
        }

        let approved = try await confirmation.request(
            action: "Save this reference"
        )
        guard approved else {
            return .result()
        }

        try await store.save(current)
        return .result()
    }
}

protocol ConfirmationService: Sendable {
    func request(action: String) async throws -> Bool
}
~~~

A visual match is an input to a user-approved action, not approval itself. The
production route must add current authorization, idempotency, undo/recovery, and
a clear result.

## Recipe 16: availability and fallback

~~~swift
enum VisualRouteState: Equatable, Sendable {
    case ready
    case systemUnavailable
    case matcherUnavailable
    case signedOut
    case noAuthorizedContent
}

struct VisualRoutePresentation: Sendable {
    let state: VisualRouteState

    var canUseAppSearch: Bool {
        switch state {
        case .ready, .matcherUnavailable, .noAuthorizedContent:
            true
        case .systemUnavailable, .signedOut:
            false
        }
    }
}
~~~

Use the route state to decide whether to register/show a system integration or
only expose normal app search. The state must come from actual target/runtime
checks, not from a hard-coded “iOS 26 means available” assumption.

## Recipe 17: source and release checklist

~~~swift
struct VisualRouteReleaseChecklist: Sendable {
    let sdkAndOSRecorded: Bool
    let targetMembershipInspected: Bool
    let localizationReviewed: Bool
    let privacyReviewed: Bool
    let physicalInvocationPassed: Bool
    let archiveInspected: Bool

    var readyForReview: Bool {
        sdkAndOSRecorded
            && targetMembershipInspected
            && localizationReviewed
            && privacyReviewed
            && physicalInvocationPassed
            && archiveInspected
    }
}
~~~

This is a planning value, not an App Store approval signal. Keep the full
evidence record in the verification matrix and tie it to the exact archive,
device, OS, and source revision.

## Recipe 18: route-specific test table

| Route | Deterministic test | Device/system proof |
| --- | --- | --- |
| Entity projection | Safe title/subtitle/image and current ID | System result card is legible/localized |
| Descriptor labels | Normalization and category mapping | Real Visual Intelligence labels reach query |
| Pixel matcher | Fixture buffer/ranking/threshold | Real camera/screenshot capture reaches query |
| UnionValue | Every case maps to an openable type | Mixed result types render and open |
| OpenIntent | Deleted/account-switched ID fails safely | System tap opens selected current record |
| semanticContentSearch | Sanitized continuation state | More results opens scoped in-app search |
| Liquid Glass detail | Preview/reduced-effects states | Legibility and interaction on physical device |
| Accessibility | VoiceOver/UI automation diagnostics | Complete handoff/detail/search task |
| Privacy | No raw input in logs/retention tests | Signed archive and real account boundary |
| Release | Target/resource/archive inspection | Distribution artifact matches tested route |

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
- [Searching](https://developer.apple.com/design/human-interface-guidelines/searching)
- [Search fields](https://developer.apple.com/design/human-interface-guidelines/search-fields)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
