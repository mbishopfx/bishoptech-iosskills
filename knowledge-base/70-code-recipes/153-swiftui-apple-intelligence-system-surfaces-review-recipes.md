# SwiftUI Apple Intelligence system-surfaces review recipes

These are compile-oriented route sketches for Writing Tools, Image Playground, Genmoji/adaptive image glyphs, Visual Intelligence, App Intents, onscreen context, Spotlight, Foundation Models, and native Liquid Glass review surfaces. Confirm every current signature, availability annotation, target membership, and deployment constraint in the named project before copying a sketch.

Read the [framework review](../42-framework-deep-dives/110-swiftui-apple-intelligence-system-surfaces-review.md), [design guide](../21-design-deep-dives/138-swiftui-apple-intelligence-system-surfaces-review-design.md), [route card](../50-capability-recipes/141-swiftui-apple-intelligence-system-surfaces-review-route.md), and [proof matrix](../60-verification/135-swiftui-apple-intelligence-system-surfaces-review-proof-matrix.md) first.

## Recipe 1: make the system owner explicit

Do not let a feature called smart route to an arbitrary model. Start with a typed lane:

~~~swift
enum IntelligenceRoute: Sendable {
    case writingTools
    case imagePlayground
    case visualSearch
    case onscreenContext
    case appIntent
    case foundationModel
}

struct IntelligenceRequest: Sendable {
    let route: IntelligenceRoute
    let sourceRevision: String
    let userInitiated: Bool
}
~~~

The route enum is app-owned bookkeeping. It does not enable a system feature. Use it to keep design, proof, and analytics from conflating a system presentation with a local model call.

## Recipe 2: model availability state

Keep capability state separate from UI presentation:

~~~swift
enum ModelReadiness: Equatable, Sendable {
    case unavailable
    case deviceNotEligible
    case modelNotReady
    case ready
    case unknown
}

struct ModelReadinessReader {
    func read() -> ModelReadiness {
        let model = SystemLanguageModel.default
        switch model.availability {
        case .available:
            return .ready
        case .unavailable(.deviceNotEligible):
            return .deviceNotEligible
        case .unavailable(.modelNotReady):
            return .modelNotReady
        case .unavailable:
            return .unknown
        }
    }
}
~~~

The exact unavailable cases can evolve. Confirm the current SDK enum and handle unknown values. The fallback must not disappear because a new unavailable reason was added.

## Recipe 3: expose Writing Tools in a SwiftUI editor

Use the standard view first:

~~~swift
struct NoteEditor: View {
    @Binding var text: String
    @Environment(\.supportsWritingTools) private var supportsWritingTools

    var body: some View {
        TextEditor(text: $text)
            .writingToolsBehavior(.automatic)
            .writingToolsAffordanceVisibility(.automatic)
            .accessibilityLabel("Note")
            .overlay(alignment: .bottomLeading) {
                if !supportsWritingTools {
                    Text("Writing Tools unavailable; manual editing remains available")
                        .font(.caption)
                }
            }
    }
}
~~~

The environment key shown here is illustrative. Verify the current SDK’s availability surface; do not invent a custom availability key if the target does not expose one. The important product behavior is that the editor remains useful without Writing Tools.

## Recipe 4: prefer a rich TextEditor for formatted content

When the app owns attributed text, bind the editor to an AttributedString and a TextSelection:

~~~swift
struct RichNoteEditor: View {
    @Binding var document: AttributedString
    @State private var selection: TextSelection?

    var body: some View {
        TextEditor(text: $document, selection: $selection)
            .textInputFormattingControlVisibility(.automatic, for: .all)
            .writingToolsBehavior(.limited)
    }
}
~~~

This sketch assumes the current SDK has the stated initializer and formatting placement. Keep a plain-text fallback and preserve all supported attributes during document saves.

## Recipe 5: pause conflicting sync while Writing Tools is active

A custom editor or a document synchronizer should not overwrite text while the system is applying a replacement:

~~~swift
@MainActor
final class DocumentRevisionGate: ObservableObject {
    @Published private(set) var writingToolsActive = false
    private(set) var revision = 0

    func beginWritingTools() {
        writingToolsActive = true
    }

    func endWritingTools() {
        writingToolsActive = false
    }

    func applyExternalTextIfSafe(_ text: String) -> Bool {
        guard !writingToolsActive else { return false }
        revision += 1
        return true
    }
}
~~~

The real editor should use the system callbacks appropriate to its route. The gate is a reminder that autosave, CloudKit sync, network refresh, and model output need a revision policy.

## Recipe 6: gate a custom UIKit Writing Tools coordinator

Use a coordinator only for a custom UIView or text engine:

~~~swift
final class CustomTextCanvas: UIView, UIWritingToolsCoordinator.Delegate {
    private var writingToolsCoordinator: UIWritingToolsCoordinator?

    func configureWritingTools() {
        guard UIWritingToolsCoordinator.isWritingToolsAvailable else { return }
        guard writingToolsCoordinator == nil else { return }

        let coordinator = UIWritingToolsCoordinator(delegate: self)
        coordinator.preferredBehavior = .limited
        coordinator.preferredResultOptions = [.plainText, .richText]
        addInteraction(coordinator)
        writingToolsCoordinator = coordinator
    }
}
~~~

Implement the delegate requirements for the selected behavior. A coordinator object without context, replacement, selection, cancellation, and layout handling is not feature proof.

## Recipe 7: keep custom Writing Tools ranges revisioned

Never map an incoming range directly into a mutable document without checking the source revision:

~~~swift
struct WritingToolsContextRecord: Sendable {
    let contextID: String
    let sourceRevision: Int
    let startingOffset: Int
}

func adjustedRange(
    incomingOffset: Int,
    length: Int,
    context: WritingToolsContextRecord,
    currentRevision: Int
) -> Range<Int>? {
    guard context.sourceRevision == currentRevision else { return nil }
    let start = context.startingOffset + incomingOffset
    return start..<(start + length)
}
~~~

When the range is stale, cancel or request fresh context. A plausible replacement at the wrong offset is a data-loss bug.

## Recipe 8: gate the Image Playground sheet

Use the system sheet only when the current environment supports it:

~~~swift
struct GenerateArtworkButton: View {
    @Environment(\.supportsImagePlayground) private var supportsImagePlayground
    @State private var isPresented = false
    @State private var candidateURL: URL?

    var body: some View {
        Group {
            if supportsImagePlayground {
                Button("Create artwork") {
                    isPresented = true
                }
                .imagePlaygroundSheet(
                    isPresented: $isPresented,
                    concepts: [.text("A friendly lighthouse in a paper-cut style")],
                    sourceImage: nil
                ) { url in
                    candidateURL = url
                }
            } else {
                Button("Choose an existing image") {
                    // Present the app’s ordinary importer.
                }
            }
        }
    }
}
~~~

Verify the current overload. Recent documentation exposes both concept-based and source-image-URL-based SwiftUI routes, and the result URL is temporary.

## Recipe 9: copy a temporary Image Playground result

Persist the result before storing a domain reference:

~~~swift
enum ImagePersistenceError: Error {
    case missingSource
    case copyFailed
}

struct GeneratedImageStore {
    let directory: URL

    func persistTemporaryImage(_ temporaryURL: URL, id: UUID) throws -> URL {
        let destination = directory
            .appendingPathComponent(id.uuidString)
            .appendingPathExtension("png")

        let fileManager = FileManager.default
        guard fileManager.fileExists(atPath: temporaryURL.path) else {
            throw ImagePersistenceError.missingSource
        }

        do {
            if fileManager.fileExists(atPath: destination.path) {
                try fileManager.removeItem(at: destination)
            }
            try fileManager.copyItem(at: temporaryURL, to: destination)
            return destination
        } catch {
            throw ImagePersistenceError.copyFailed
        }
    }
}
~~~

Validate the image and storage policy before committing the domain record. If the copy fails, keep the source or previous image untouched.

## Recipe 10: configure Image Playground options deliberately

Options should reflect an explainable product choice:

~~~swift
var options = ImagePlaygroundOptions()
options.personalization = .automatic
options.creationVariety = .automatic
options.creationStrategy = .automatic
options.sizeSpecification = .closest(to: CGSize(width: 512, height: 512))
~~~

The exact option members can change with the SDK. Confirm the target’s current ImagePlaygroundOptions API. Do not show a personalization toggle unless the app can explain what enabling or disabling it changes.

## Recipe 11: preserve adaptive image glyph attributes

When transforming rich text, copy the adaptive glyph attribute with the other attributes:

~~~swift
func preservedAttributes(
    from source: AttributedString,
    range: Range<AttributedString.Index>
) -> AttributedString {
    let fragment = AttributedString(source[range])
    return fragment
}

func describeAdaptiveGlyph(_ glyph: NSAdaptiveImageGlyph) -> String {
    glyph.contentDescription
}
~~~

This small function is intentionally conservative. A custom editor should avoid rebuilding attributes from a whitelist that excludes adaptiveImageGlyph. A production format should persist imageContent, contentIdentifier, and contentDescription or document the export fallback.

## Recipe 12: define a lightweight AppEntity

Keep the system-facing entity smaller than the database record:

~~~swift
struct LandmarkEntity: AppEntity, Identifiable, Sendable {
    let id: UUID
    let name: String
    let region: String
    let thumbnailData: Data?

    static var typeDisplayRepresentation: TypeDisplayRepresentation {
        TypeDisplayRepresentation(name: "Landmark")
    }

    var displayRepresentation: DisplayRepresentation {
        if let thumbnailData {
            return DisplayRepresentation(
                title: LocalizedStringResource(stringLiteral: name),
                subtitle: LocalizedStringResource(stringLiteral: region),
                image: .init(data: thumbnailData)
            )
        }
        return DisplayRepresentation(
            title: LocalizedStringResource(stringLiteral: name),
            subtitle: LocalizedStringResource(stringLiteral: region)
        )
    }
}
~~~

Confirm the current DisplayRepresentation and LocalizedStringResource initializers. The entity must resolve quickly and use stable identity.

## Recipe 13: associate a standard SwiftUI view with an entity

Use the entity identifier modifier for visible content:

~~~swift
struct LandmarkCard: View {
    let landmark: LandmarkEntity

    var body: some View {
        VStack(alignment: .leading) {
            Text(landmark.name)
            Text(landmark.region)
                .font(.caption)
        }
        .appEntityIdentifier(
            EntityIdentifier(for: LandmarkEntity.self, identifier: landmark.id)
        )
    }
}
~~~

The association should match the actual visible record. Remove or replace it when the view changes identity or authorization.

## Recipe 14: describe custom-drawn entities

For a canvas or Metal-backed view, provide spatial elements:

~~~swift
struct EntityCanvas: View {
    let visibleItems: [LandmarkEntity]

    var body: some View {
        CustomCanvas(items: visibleItems)
            .appEntityUIElements { context in
                visibleItems.map { item in
                    AppEntityUIElement(
                        identifier: EntityIdentifier(
                            for: LandmarkEntity.self,
                            identifier: item.id
                        ),
                        bounds: context.bounds(for: item.id),
                        state: context.isSelected(item.id) ? .init(isSelected: true) : .init()
                    )
                }
            }
    }
}
~~~

This is an API-shaped sketch. Implement the provider with the current SwiftUI context type and local coordinate system. Bounds and selection are part of the meaning, not decorative metadata.

## Recipe 15: implement a Visual Intelligence query

The query receives a SemanticContentDescriptor and returns app entities:

~~~swift
struct LandmarkVisualQuery: IntentValueQuery {
    let search: LandmarkSearch

    func values(
        for input: SemanticContentDescriptor
    ) async throws -> [LandmarkEntity] {
        if let labels = input.labels, !labels.isEmpty {
            return try await search.byLabels(Array(labels.prefix(5)))
        }
        guard let pixelBuffer = input.pixelBuffer else {
            return []
        }
        return try await search.byPixelBuffer(pixelBuffer, limit: 20)
    }
}
~~~

The current SDK may expose labels as a non-optional collection. Confirm the signature. Keep the first result list bounded and return quickly.

## Recipe 16: open a Visual Intelligence result

OpenIntent should resolve stable identity and navigate to the current entity:

~~~swift
struct OpenLandmarkIntent: OpenIntent {
    static var title: LocalizedStringResource {
        "Open Landmark"
    }

    @Parameter(title: "Landmark")
    var target: LandmarkEntity

    func perform() async throws -> some IntentResult {
        let current = try await LandmarkStore.shared.resolve(id: target.id)
        guard current != nil else {
            return .result(dialog: "That landmark is no longer available.")
        }
        await Navigator.shared.showLandmark(id: target.id)
        return .result()
    }
}
~~~

An OpenIntent must not assume that the entity snapshot is current. Re-resolve by stable identity and handle deletion or authorization.

## Recipe 17: return several Visual Intelligence entity types

Use a UnionValue when a single descriptor search can return different entity types:

~~~swift
@UnionValue
enum VisualSearchResult {
    case landmark(LandmarkEntity)
    case collection(LandmarkCollectionEntity)
}

struct MixedVisualQuery: IntentValueQuery {
    func values(
        for input: SemanticContentDescriptor
    ) async throws -> [VisualSearchResult] {
        let landmarks = try await Search.shared.landmarks(for: input)
        let collections = try await Search.shared.collections(for: input)
        return landmarks.map(VisualSearchResult.landmark)
            + collections.map(VisualSearchResult.collection)
    }
}
~~~

Each entity type needs an OpenIntent. Do not register several descriptor queries when a UnionValue is the intended contract.

## Recipe 18: provide a more-results route

The system result panel should stay bounded. Add the visual intelligence semantic-content-search schema to open the app’s full search experience:

~~~swift
@AppIntent(schema: .visualIntelligence.semanticContentSearch)
struct ShowVisualSearchResultsIntent {
    var semanticContent: SemanticContentDescriptor

    func perform() async throws -> some IntentResult {
        await Navigator.shared.showVisualSearch(
            labels: semanticContent.labels,
            pixelBuffer: semanticContent.pixelBuffer
        )
        return .result()
    }
}
~~~

The schema and macro surface are version-sensitive. Confirm the current generated requirements and use the app’s navigation owner rather than a global view lookup.

## Recipe 19: index stable entities in Spotlight

Use a named index and stable identifiers:

~~~swift
struct LandmarkIndexer {
    let index: CSSearchableIndex

    func donate(_ entities: [LandmarkEntity]) async throws {
        try await index.indexAppEntities(entities)
    }

    func delete(ids: [String]) async throws {
        try await index.deleteSearchableItems(withIdentifiers: ids)
    }
}
~~~

Use IndexedEntity on the entity type and IndexedEntityQuery where the system needs reindexing. Delete entries when the record is deleted or no longer authorized.

## Recipe 20: expose an expensive property safely

Choose computed and deferred properties with care:

~~~swift
struct RecordEntity: IndexedEntity {
    let id: UUID
    let title: String
    let store: RecordStore

    @ComputedProperty(indexingKey: \.contentDescription)
    var description: String {
        store.shortDescription(for: id)
    }

    @DeferredProperty
    var fullContent: String {
        get async throws {
            try await store.fullContent(for: id)
        }
    }
}
~~~

The property-wrapper signatures and indexing-key syntax are SDK-sensitive. The design rule is stable: index cheap useful data and defer expensive content only when its system behavior is acceptable.

## Recipe 21: associate an entity with a user activity

Use NSUserActivity when an activity-based route is appropriate:

~~~swift
func activity(for entity: LandmarkEntity) -> NSUserActivity {
    let activity = NSUserActivity(activityType: "com.example.landmark")
    activity.title = entity.name
    activity.appEntityIdentifier = EntityIdentifier(
        for: LandmarkEntity.self,
        identifier: entity.id
    )
    activity.isEligibleForPrediction = true
    return activity
}
~~~

The example identifier is a fixture, not a production bundle ID. Only mark the activity eligible and associate content that is current, relevant, and safe to share with the system.

## Recipe 22: provide a bounded Transferable representation

When cross-app context needs content, provide the smallest useful representation:

~~~swift
struct NoteEntity: AppEntity, Transferable {
    let id: UUID
    let title: String
    let body: String

    static var transferRepresentation: some TransferRepresentation {
        DataRepresentation(exportedContentType: .plainText) { note in
            Data((note.title + "\n" + note.body).utf8)
        }
    }
}
~~~

Confirm the current AppEntity and Transferable requirements. Do not export private database files, unbounded attachments, or content the person is not authorized to share.

## Recipe 23: stream a Foundation Model candidate

Keep model output separate from domain truth:

~~~swift
struct SummaryProposal: Sendable {
    let sourceRevision: Int
    let text: String
    let promptVersion: String
}

@MainActor
final class SummaryModelController: ObservableObject {
    @Published private(set) var proposal: SummaryProposal?
    @Published private(set) var readiness: ModelReadiness = .unavailable

    func summarize(_ input: String, revision: Int) async {
        readiness = ModelReadinessReader().read()
        guard readiness == .ready else { return }

        do {
            let session = LanguageModelSession()
            let response = try await session.respond(
                to: "Summarize the following text in three short sentences: " + input
            )
            proposal = SummaryProposal(
                sourceRevision: revision,
                text: response.content,
                promptVersion: "summary-v1"
            )
        } catch {
            proposal = nil
        }
    }
}
~~~

Foundation Models session and response types are version-sensitive. Verify the current SDK and keep the feature unavailable-safe. Do not save proposal.text until the source revision and user approval are checked.

## Recipe 24: validate a model proposal

Use a domain validator before showing a commit action:

~~~swift
struct ProposalValidator {
    func validate(
        proposal: SummaryProposal,
        currentRevision: Int,
        original: String
    ) -> Result<String, ValidationError> {
        guard proposal.sourceRevision == currentRevision else {
            return .failure(.stale)
        }
        guard !proposal.text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            return .failure(.empty)
        }
        guard proposal.text.count < original.count else {
            return .failure(.notShorter)
        }
        return .success(proposal.text)
    }
}

enum ValidationError: Error {
    case stale
    case empty
    case notShorter
}
~~~

The rule should match the product. Do not use an arbitrary length heuristic as proof of correctness; use it only as one gate before human review.

## Recipe 25: choose App Intent runtime modes

Declare the execution modes your action can actually support:

~~~swift
struct SummarizeNoteIntent: AppIntent {
    static var title: LocalizedStringResource {
        "Summarize Note"
    }

    static var supportedModes: IntentModes {
        [.background, .foreground(.deferred)]
    }

    @Parameter(title: "Note")
    var note: NoteEntity

    func perform() async throws -> some IntentResult {
        if systemContext.currentMode == .background {
            // Complete background-safe preparation or ask to continue.
        }
        return .result()
    }
}
~~~

Consult current IntentModes syntax and the ability to continue in the foreground. A mode declaration is not permission to show UI at any time.

## Recipe 26: keep review actions ordinary

Use native controls around the proposal:

~~~swift
struct ProposalReview: View {
    let proposal: SummaryProposal
    let onAccept: () -> Void
    let onReject: () -> Void
    let onRetry: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(proposal.text)
                .textSelection(.enabled)
            Text("Draft from the current note revision")
                .font(.caption)
            HStack {
                Button("Accept", action: onAccept)
                    .buttonStyle(.borderedProminent)
                Button("Edit", action: onReject)
                Button("Retry", action: onRetry)
            }
        }
        .padding()
    }
}
~~~

The proposal must remain editable and dismissible. Use the app’s normal undo system after acceptance.

## Recipe 27: add restrained Liquid Glass

Apply glass to a functional group, not to every view:

~~~swift
struct IntelligenceToolbar: View {
    let isReady: Bool
    let onAction: () -> Void

    var body: some View {
        HStack(spacing: 12) {
            Label(
                isReady ? "Ready" : "Unavailable",
                systemImage: isReady ? "sparkles" : "exclamationmark.circle"
            )
            Button("Use intelligence", action: onAction)
                .disabled(!isReady)
        }
        .padding(.horizontal)
        .glassEffect()
    }
}
~~~

Verify the current Liquid Glass API and use the native control hierarchy. The icon is illustrative; the label and accessible state carry the meaning.

## Recipe 28: project true state into the UI

Keep system state, candidate state, and domain state distinct:

~~~swift
enum IntelligenceViewState: Equatable {
    case unavailable(String)
    case ready
    case presentingSystemSurface
    case working
    case candidate(String, sourceRevision: Int)
    case committed
    case failed(String)
}

func canCommit(
    _ state: IntelligenceViewState,
    currentRevision: Int
) -> Bool {
    guard case let .candidate(_, sourceRevision) = state else {
        return false
    }
    return sourceRevision == currentRevision
}
~~~

Use this projection to prevent a stale candidate from keeping an enabled Accept button.

## Recipe 29: make unavailable paths visible in tests

Build a fixture table before connecting a real model:

~~~swift
enum IntelligenceFixture {
    case available
    case deviceNotEligible
    case modelNotReady
    case cancelled
    case emptyInput
    case staleRevision
    case malformedOutput
}

struct FixtureExpectation {
    let fixture: IntelligenceFixture
    let allowsCommit: Bool
    let fallbackText: String
}
~~~

Unit tests can prove the state machine. They cannot prove Apple Intelligence is available on a particular device or that the system panel appears.

## Recipe 30: test adaptive glyph preservation

Use a rich-text fixture with an adaptive glyph and verify round trips:

~~~swift
struct RichTextRoundTrip {
    func assertPreservesGlyph(_ document: AttributedString) throws {
        let encoded = try JSONEncoder().encode(document)
        let decoded = try JSONDecoder().decode(AttributedString.self, from: encoded)
        guard decoded == document else {
            throw RoundTripError.glyphOrAttributeLost
        }
    }
}

enum RoundTripError: Error {
    case glyphOrAttributeLost
}
~~~

The exact Codable support depends on the document format and SDK. If the app uses a custom format, inspect adaptiveImageGlyph explicitly and add a migration fixture.

## Recipe 31: record a Visual Intelligence evidence item

Use a structured record instead of a screenshot alone:

~~~swift
struct VisualSearchEvidence: Codable, Sendable {
    let deviceModel: String
    let osBuild: String
    let locale: String
    let labels: [String]
    let hadPixelBuffer: Bool
    let resultIDs: [String]
    let openIntentResolved: Bool
    let moreResultsOpened: Bool
    let sourceRevision: String
    let privacyReviewed: Bool
}
~~~

Store only the metadata needed for the proof record. Avoid storing the raw screenshot or pixel buffer unless the test plan explicitly requires it and the retention policy allows it.

## Recipe 32: archive the AI target configuration

Inspect the archive rather than trusting the Xcode project navigator:

~~~text
archive
    -> Info.plist and embedded provisioning
    -> entitlements
    -> app and extension target membership
    -> linked frameworks
    -> privacy manifest and usage descriptions
    -> model and rich-text resources
    -> TestFlight install
    -> physical and system-surface proof
~~~

The archive establishes the signed artifact. It does not establish model readiness, system invocation, or accessibility until the artifact is installed and exercised.

## Recipe 33: final route record

Capture the route in a small reviewable record:

~~~yaml
feature: landmark visual search plus local summary
system_route: Visual Intelligence -> IntentValueQuery -> OpenIntent
entity: stable LandmarkEntity ID
app_route: detail view -> Foundation Models summary proposal
commit: user accepts summary into current landmark revision
fallback: normal search and manual description
availability: system capture and model readiness checked separately
accessibility: VoiceOver, Dynamic Type, Reduce Motion, keyboard
privacy: pixel buffer not logged; summary input limited to selected record
proof: compile, system invocation, physical device, archive, TestFlight
status: pending until all evidence exists
~~~

Do not mark the route complete because a generated string or screenshot exists. Mark each evidence level separately.

## Sources

- [Apple Intelligence](https://developer.apple.com/documentation/technologyoverviews/apple-intelligence/)
- [Apple Intelligence and Siri AI](https://developer.apple.com/documentation/appintents/apple-intelligence-and-siri-ai)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- [IndexedEntity](https://developer.apple.com/documentation/appintents/indexedentity)
- [Making app entities available in Spotlight](https://developer.apple.com/documentation/appintents/making-app-entities-available-in-spotlight)
- [Providing contextual cues to Apple Intelligence and Siri](https://developer.apple.com/documentation/appintents/providing-contextual-cues-to-apple-intelligence-and-siri)
- [AppEntityUIElement](https://developer.apple.com/documentation/appintents/appentityuielement)
- [appEntityIdentifier(_:)](https://developer.apple.com/documentation/swiftui/view/appentityidentifier%28_%3A%29)
- [appEntityIdentifier](https://developer.apple.com/documentation/foundation/nsuseractivity/appentityidentifier)
- [Integrating your app with visual intelligence](https://developer.apple.com/documentation/visualintelligence/integrating-your-app-with-visual-intelligence)
- [SemanticContentDescriptor](https://developer.apple.com/documentation/visualintelligence/semanticcontentdescriptor)
- [Visual intelligence app schema](https://developer.apple.com/documentation/appintents/app-schema-domain-visual-intelligence)
- [Writing Tools](https://developer.apple.com/documentation/uikit/writing-tools)
- [Customizing Writing Tools behavior for UIKit views](https://developer.apple.com/documentation/uikit/customizing-writing-tools-behavior-for-system-views)
- [Adding Writing Tools support to a custom UIKit view](https://developer.apple.com/documentation/uikit/adding-writing-tools-support-to-a-custom-uiview)
- [WritingToolsBehavior](https://developer.apple.com/documentation/swiftui/writingtoolsbehavior)
- [writingToolsBehavior(_:)](https://developer.apple.com/documentation/swiftui/view/writingtoolsbehavior%28_%3A%29)
- [TextEditor](https://developer.apple.com/documentation/swiftui/texteditor)
- [NSAdaptiveImageGlyph](https://developer.apple.com/documentation/uikit/nsadaptiveimageglyph)
- [AttributedString.AdaptiveImageGlyph](https://developer.apple.com/documentation/foundation/attributedstring/adaptiveimageglyph)
- [Image Playground](https://developer.apple.com/documentation/imageplayground)
- [ImagePlaygroundOptions](https://developer.apple.com/documentation/imageplayground/imageplaygroundoptions)
- [ImagePlaygroundStyle](https://developer.apple.com/documentation/imageplayground/imageplaygroundstyle)
- [imagePlaygroundSheet(isPresented:concepts:sourceImageURL:onCompletion:onCancellation:)](https://developer.apple.com/documentation/swiftui/view/imageplaygroundsheet%28ispresented%3Aconcepts%3Asourceimageurl%3Aoncompletion%3Aoncancellation%3A%29)
- [ImageCreator](https://developer.apple.com/documentation/imageplayground/imagecreator)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [Generating content and performing tasks with Foundation Models](https://developer.apple.com/documentation/foundationmodels/generating-content-and-performing-tasks-with-foundation-models)
- [supportedModes](https://developer.apple.com/documentation/appintents/appintent/supportedmodes)
- [IntentModes.Current](https://developer.apple.com/documentation/appintents/intentmodes/current)
- [Generative AI HIG](https://developer.apple.com/design/human-interface-guidelines/generative-ai)
- [Siri HIG](https://developer.apple.com/design/human-interface-guidelines/siri)
- [Accessibility HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
