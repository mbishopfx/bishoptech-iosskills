# SwiftUI Natural Language and local semantic-retrieval code recipes

These are compile-oriented sketches for the [Natural Language review](../42-framework-deep-dives/117-swiftui-natural-language-semantic-search-review.md). They pair with the [design route](../21-design-deep-dives/145-swiftui-natural-language-semantic-search-review-design.md), the [capability route](../50-capability-recipes/148-swiftui-natural-language-semantic-search-review-route.md), and the [proof matrix](../60-verification/142-swiftui-natural-language-semantic-search-proof-matrix.md).

The snippets show ownership and data boundaries. They are not claimed to compile unchanged against every iOS 26 SDK revision. Compile each selected API in a named target, resolve Swift concurrency annotations, and verify the actual language/model assets on the target device.

## 1. App-owned value types

Keep Natural Language objects out of the domain and SwiftUI layers:

~~~swift
import Foundation

struct SourceRevision: Hashable, Sendable {
    let sourceID: String
    let revision: String
    let normalizationVersion: String
}

enum RepresentationKind: Hashable, Sendable {
    case sentenceEmbedding
    case wordEmbedding
    case contextualEmbedding(modelIdentifier: String)
    case classifier(modelIdentifier: String)
    case sequenceTagger(modelIdentifier: String)
}

struct RepresentationIdentity: Hashable, Sendable {
    let kind: RepresentationKind
    let language: String
    let revision: Int
    let dimension: Int?
}

struct TextChunk: Identifiable, Hashable, Sendable {
    let id: String
    let source: SourceRevision
    let displayExcerpt: String
    let originalRangeDescription: String
    let language: String
}

struct SemanticCandidate: Identifiable, Hashable, Sendable {
    let id: String
    let chunk: TextChunk
    let distance: Double
    let reason: String
    let representation: RepresentationIdentity
    let isStale: Bool
}
~~~

Do not store a framework object, mutable tagger, model instance, or unsafe pointer in these values. Store the provenance needed to decide whether a result is still valid.

## 2. Language detection actor

An NLLanguageRecognizer is stateful and should be owned by one operation. The result is a candidate, not a guaranteed language:

~~~swift
import NaturalLanguage

struct LanguageDetection: Sendable {
    let dominant: String?
    let hypotheses: [(language: String, probability: Double)]
    let sourceRevision: SourceRevision
}

actor LanguageDetector {
    func detect(
        text: String,
        source: SourceRevision,
        constraints: [NLLanguage] = [],
        hints: [NLLanguage: Double] = [:]
    ) -> LanguageDetection {
        let recognizer = NLLanguageRecognizer()
        recognizer.languageConstraints = constraints
        recognizer.languageHints = hints
        recognizer.processString(text)

        let hypotheses = recognizer
            .languageHypotheses(withMaximum: 4)
            .map { (language: $0.key.rawValue, probability: $0.value) }
            .sorted { $0.probability > $1.probability }

        return LanguageDetection(
            dominant: recognizer.dominantLanguage?.rawValue,
            hypotheses: hypotheses,
            sourceRevision: source
        )
    }
}
~~~

In a real target, verify the current Swift names and Sendable behavior. For multiple independent inputs, create a new recognizer or reset the owned instance before processing the next source.

## 3. Token ranges with NLTokenizer

Keep ranges associated with the original String and source revision:

~~~swift
import NaturalLanguage

struct TokenSpan: Sendable {
    let substring: String
    let rangeDescription: String
}

actor TokenizerService {
    func words(in text: String, language: NLLanguage?) -> [TokenSpan] {
        let tokenizer = NLTokenizer(unit: .word)
        tokenizer.string = text
        if let language {
            tokenizer.setLanguage(language)
        }

        return tokenizer.tokens(for: text.startIndex..<text.endIndex).map { range in
            TokenSpan(
                substring: String(text[range]),
                rangeDescription: String(describing: range)
            )
        }
    }
}
~~~

Prefer returning a range or an app-owned offset mapping rather than only the substring. The range is what lets a review surface highlight the original source. If normalization changes character positions, store the mapping as part of the normalization contract.

## 4. NLTagger asset and tag route

Asset readiness is a state transition. The exact async overload is SDK-sensitive, so compile it against the target SDK:

~~~swift
import NaturalLanguage

actor TaggingService {
    func availableSchemes(
        unit: NLTokenUnit,
        language: NLLanguage
    ) -> [NLTagScheme] {
        NLTagger.availableTagSchemes(for: unit, language: language)
    }

    func prepare(
        language: NLLanguage,
        scheme: NLTagScheme
    ) async throws -> NLTagger.AssetsResult {
        try await NLTagger.requestAssets(for: language, tagScheme: scheme)
    }

    func tags(
        in text: String,
        language: NLLanguage?,
        schemes: [NLTagScheme]
    ) -> [(tag: String?, rangeDescription: String)] {
        let tagger = NLTagger(tagSchemes: schemes)
        tagger.string = text
        if let language {
            tagger.setLanguage(language, range: text.startIndex..<text.endIndex)
        }

        let scheme = schemes[0]
        return tagger.tags(
            in: text.startIndex..<text.endIndex,
            unit: .word,
            scheme: scheme,
            options: [.omitWhitespace, .omitPunctuation]
        ).map { tag, range in
            (tag?.rawValue, String(describing: range))
        }
    }
}
~~~

Do not use an unavailable scheme as an empty tag result. Keep asset failure visible so the UI can offer exact/manual fallback.

## 5. Static sentence embedding

NLEmbedding is the Natural Language route for word and sentence distances:

~~~swift
import NaturalLanguage

struct EmbeddingSnapshot: Sendable {
    let language: String
    let revision: Int
    let dimension: Int
}

actor SentenceEmbeddingService {
    func snapshot(language: NLLanguage) throws -> EmbeddingSnapshot {
        guard let embedding = NLEmbedding.sentenceEmbedding(for: language) else {
            throw NSError(domain: "LocalLanguage", code: 1)
        }

        return EmbeddingSnapshot(
            language: language.rawValue,
            revision: embedding.revision,
            dimension: embedding.dimension
        )
    }

    func distance(
        between left: String,
        and right: String,
        language: NLLanguage,
        type: NLDistanceType = .cosine
    ) throws -> Double {
        guard let embedding = NLEmbedding.sentenceEmbedding(for: language) else {
            throw NSError(domain: "LocalLanguage", code: 2)
        }
        return embedding.distance(between: left, and: right, distanceType: type)
    }
}
~~~

Verify the available distance type and current Swift signature in the selected SDK. Persist the embedding revision and language beside any index row. A distance is a ranking signal, not a domain decision.

## 6. Vocabulary neighbors

Use nearest-neighbor APIs for a known vocabulary:

~~~swift
import NaturalLanguage

actor VocabularyService {
    func neighbors(
        for term: String,
        language: NLLanguage,
        maximumCount: Int
    ) throws -> [(String, Double)] {
        guard let embedding = NLEmbedding.wordEmbedding(for: language) else {
            throw NSError(domain: "LocalLanguage", code: 3)
        }

        return embedding
            .neighbors(
                for: term,
                maximumCount: maximumCount,
                distanceType: .cosine
            )
            .map { ($0.0, $0.1) }
    }
}
~~~

For document search, an app-owned chunk index normally stores each chunk’s vector and metadata. Do not pretend a general document collection is the Natural Language vocabulary unless the app deliberately built that vocabulary.

## 7. Contextual embedding lifecycle

Contextual embeddings can require assets and produce subword vectors. Keep loading and unloading inside a bounded actor:

~~~swift
import NaturalLanguage

struct PooledVector: Sendable {
    let values: [Double]
    let language: String
    let modelIdentifier: String
    let revision: Int
}

actor ContextualEmbeddingService {
    private var embedding: NLContextualEmbedding?

    func prepare(language: NLLanguage) async throws {
        guard let model = NLContextualEmbedding(language: language) else {
            throw NSError(domain: "LocalLanguage", code: 10)
        }
        self.embedding = model

        if !model.hasAvailableAssets {
            _ = try await model.requestAssets()
        }
        try model.load()
    }

    func pool(text: String) throws -> PooledVector {
        guard let model = embedding else {
            throw NSError(domain: "LocalLanguage", code: 11)
        }

        let result = try model.embeddingResult(for: text, language: nil)
        var vectors: [[Double]] = []
        result.enumerateTokenVectors(in: text.startIndex..<text.endIndex) {
            vector, _ in
            vectors.append(vector)
            return true
        }

        guard let first = vectors.first, !first.isEmpty else {
            throw NSError(domain: "LocalLanguage", code: 12)
        }
        var pooled = Array(repeating: 0.0, count: first.count)
        for vector in vectors {
            guard vector.count == pooled.count else {
                throw NSError(domain: "LocalLanguage", code: 13)
            }
            for index in pooled.indices {
                pooled[index] += vector[index]
            }
        }
        for index in pooled.indices {
            pooled[index] /= Double(vectors.count)
        }

        return PooledVector(
            values: pooled,
            language: result.language.rawValue,
            modelIdentifier: model.modelIdentifier,
            revision: model.revision
        )
    }

    func unload() {
        embedding?.unload()
        embedding = nil
    }
}
~~~

This mean-pooling implementation is a recipe choice, not an Apple semantic guarantee. Evaluate it against the app’s labeled fixtures. Verify the current async requestAssets overload and model lifecycle in the target SDK.

## 8. NLModel classifier bridge

An NLModel can wrap a Core ML natural-language model:

~~~swift
import CoreML
import NaturalLanguage

struct LabelCandidate: Sendable {
    let label: String
    let confidence: Double?
    let source: SourceRevision
}

actor TextClassifierService {
    private let model: NLModel

    init(compiledModelURL: URL) throws {
        self.model = try NLModel(contentsOf: compiledModelURL)
    }

    func classify(
        text: String,
        source: SourceRevision,
        maximumCount: Int
    ) -> [LabelCandidate] {
        let hypotheses = model.predictedLabelHypotheses(
            for: text,
            maximumCount: maximumCount
        )
        return hypotheses.map { label, confidence in
            LabelCandidate(
                label: label,
                confidence: confidence,
                source: source
            )
        }
    }
}
~~~

If the selected SDK exposes the initializer or method with a different Swift spelling, update the sketch after compiling. Inspect model.configuration and persist language/type/revision metadata. Never let the classifier service write a domain record directly.

## 9. Custom sequence tagger bridge

For a Core ML word-tagger model, attach NLModel to NLTagger under a custom scheme:

~~~swift
import NaturalLanguage

actor SequenceTaggerService {
    func tag(
        text: String,
        customModelURL: URL,
        customScheme: NLTagScheme
    ) throws -> [(label: String?, range: Range<String.Index>)] {
        let customModel = try NLModel(contentsOf: customModelURL)
        let tagger = NLTagger(tagSchemes: [.nameType, customScheme])
        tagger.string = text
        tagger.setModels([customModel], forTagScheme: customScheme)

        return tagger.tags(
            in: text.startIndex..<text.endIndex,
            unit: .word,
            scheme: customScheme,
            options: [.omitWhitespace, .omitPunctuation]
        ).map { tag, range in
            (tag?.rawValue, range)
        }
    }
}
~~~

Map the range and label into a reviewable candidate. A tagger should not silently mutate a document or send a message because a model emitted a span.

## 10. App-owned vector index

For a small collection, start with a reference scan:

~~~swift
struct IndexedVector: Sendable {
    let chunk: TextChunk
    let representation: RepresentationIdentity
    let values: [Double]
    let deleted: Bool
}

actor VectorIndex {
    private var rows: [IndexedVector] = []

    func replace(_ row: IndexedVector) {
        rows.removeAll { $0.chunk.id == row.chunk.id }
        rows.append(row)
    }

    func candidates(
        query: [Double],
        representation: RepresentationIdentity,
        scope: Set<String>,
        limit: Int
    ) -> [SemanticCandidate] {
        rows
            .filter {
                !$0.deleted &&
                $0.representation == representation &&
                scope.contains($0.chunk.source.sourceID)
            }
            .compactMap { row in
                guard row.values.count == query.count else { return nil }
                let distance = cosineDistance(query, row.values)
                return SemanticCandidate(
                    id: row.chunk.id,
                    chunk: row.chunk,
                    distance: distance,
                    reason: "similar sentence",
                    representation: row.representation,
                    isStale: false
                )
            }
            .sorted {
                if $0.distance == $1.distance {
                    return $0.id < $1.id
                }
                return $0.distance < $1.distance
            }
            .prefix(limit)
            .map { $0 }
    }
}

private func cosineDistance(_ left: [Double], _ right: [Double]) -> Double {
    let dot = zip(left, right).reduce(0) { $0 + $1.0 * $1.1 }
    let leftNorm = sqrt(left.reduce(0) { $0 + $1 * $1 })
    let rightNorm = sqrt(right.reduce(0) { $0 + $1 * $1 })
    guard leftNorm > 0, rightNorm > 0 else { return .infinity }
    return 1 - dot / (leftNorm * rightNorm)
}
~~~

This is intentionally a simple reference implementation. Production storage needs persistence, migration, deletion, chunk rebuilds, memory budgeting, and an index strategy that is compared against this result set.

## 11. Revision-aware query publication

Prevent late results from crossing source or index revisions:

~~~swift
struct QueryGeneration: Hashable, Sendable {
    let query: UInt64
    let source: String
    let index: String
}

@MainActor
final class SearchViewModel: ObservableObject {
    enum State {
        case idle
        case preparing
        case searching(QueryGeneration)
        case review([SemanticCandidate], QueryGeneration)
        case partial(String)
        case failed(String)
    }

    @Published private(set) var state: State = .idle
    private var generation: UInt64 = 0
    private var task: Task<Void, Never>?

    func search(
        sourceRevision: String,
        indexRevision: String,
        run: @escaping @Sendable (QueryGeneration) async throws -> [SemanticCandidate]
    ) {
        task?.cancel()
        generation &+= 1
        let current = QueryGeneration(
            query: generation,
            source: sourceRevision,
            index: indexRevision
        )
        state = .searching(current)

        task = Task { [weak self] in
            do {
                let candidates = try await run(current)
                guard !Task.isCancelled else { return }
                await MainActor.run {
                    guard case .searching(let active) = self?.state,
                          active == current else { return }
                    self?.state = .review(candidates, current)
                }
            } catch is CancellationError {
                return
            } catch {
                await MainActor.run {
                    self?.state = .failed("Search could not be completed.")
                }
            }
        }
    }
}
~~~

The run closure should recheck current source authorization and revision before returning candidates. A UI generation guard is not a substitute for domain validation.

## 12. SwiftUI candidate shell

Keep the candidate state human-readable:

~~~swift
import SwiftUI

struct CandidateList: View {
    let candidates: [SemanticCandidate]
    let approve: (SemanticCandidate) -> Void
    let discard: (SemanticCandidate) -> Void

    var body: some View {
        List(candidates) { candidate in
            VStack(alignment: .leading, spacing: 8) {
                Text(candidate.chunk.displayExcerpt)
                    .font(.body)
                    .textSelection(.enabled)

                Text(candidate.reason)
                    .font(.caption)
                    .foregroundStyle(.secondary)

                HStack {
                    Button("Open source") {
                        // Route to the source using candidate.chunk.source.
                    }
                    Button("Use") {
                        approve(candidate)
                    }
                    Button("Discard") {
                        discard(candidate)
                    }
                }
                .buttonStyle(.bordered)
            }
            .accessibilityElement(children: .combine)
            .accessibilityLabel(
                candidate.chunk.displayExcerpt + ", " + candidate.reason
            )
        }
        .listStyle(.insetGrouped)
    }
}
~~~

Add the project’s iOS 26 Liquid Glass treatment only around functional controls after the standard view is accessible and legible. Do not hide source evidence behind an effect. Verify the current SDK spelling for any glass modifier used by the target.

## 13. Safe approval boundary

A candidate should cross into the domain only through a validated command:

~~~swift
struct ApproveCandidate: Sendable {
    let candidateID: String
    let expectedSourceRevision: String
    let expectedIndexRevision: String
}

enum ApprovalFailure: Error {
    case stale
    case unauthorized
    case sourceDeleted
    case invalidCandidate
}

actor CandidateApprover {
    func approve(
        _ command: ApproveCandidate,
        currentSourceRevision: String?,
        currentIndexRevision: String,
        isAuthorized: Bool
    ) throws {
        guard isAuthorized else { throw ApprovalFailure.unauthorized }
        guard let currentSourceRevision else {
            throw ApprovalFailure.sourceDeleted
        }
        guard currentSourceRevision == command.expectedSourceRevision,
              currentIndexRevision == command.expectedIndexRevision else {
            throw ApprovalFailure.stale
        }
        // Re-fetch candidate, validate its destination, then commit idempotently.
    }
}
~~~

The review UI can display a candidate. It cannot assume that display equals approval.

## 14. Tests for the reference route

Cover:

~~~swift
struct SemanticFixture {
    let source: SourceRevision
    let text: String
    let language: String
    let expectedTopSourceID: String?
}

// Include positive and negative pairs, ambiguous language,
// unsupported assets, long text, changed revisions,
// deleted or unauthorized sources, and cancelled queries.
~~~

The fixture should assert source identity, range/evidence, representation identity, and stale behavior—not only a floating-point score.

## 15. Performance and privacy instrumentation

Measure the pipeline as a whole:

    source load -> normalize -> language -> tokenize/chunk
        -> asset/model load -> vector/model work -> rank
        -> source lookup -> SwiftUI publication

Record model/embedding revision, count, dimension, duration, and memory samples. Avoid logging raw source text, embeddings, or stable private identifiers. Use a redacted fixture or a one-way test identifier for diagnostics.

## 16. Compile and release checklist

- Natural Language and any Core ML target imports compile in the intended target.
- The selected API spellings and async overloads are verified against the installed SDK.
- Language/model/embedding assets work on a physical device.
- Query and index use the same representation identity.
- Stale source/index/model revisions are blocked.
- Exact/manual fallback is reachable.
- VoiceOver, Dynamic Type, keyboard, RTL, and reduced-effects tasks are exercised.
- Clean install and upgrade migration rebuild or invalidate derived artifacts correctly.
- Archive/TestFlight contains the intended model/embedding assets and release logging policy.

## Stop conditions

- A model or embedding is selected without a language, asset, and revision contract.
- The app persists vectors without source identity or deletion behavior.
- Search results can cross an authorization boundary.
- A contextual embedding is scored without a documented pooling/evaluation policy.
- A successful preview or simulator run is used as language-asset, accessibility, device, or release proof.

## Sources

- [Natural Language](https://developer.apple.com/documentation/naturallanguage)
- [NLTokenizer](https://developer.apple.com/documentation/naturallanguage/nltokenizer)
- [NLTagger](https://developer.apple.com/documentation/naturallanguage/nltagger)
- [NLEmbedding](https://developer.apple.com/documentation/naturallanguage/nlembedding)
- [NLContextualEmbedding](https://developer.apple.com/documentation/naturallanguage/nlcontextualembedding)
- [NLContextualEmbeddingResult](https://developer.apple.com/documentation/naturallanguage/nlcontextualembeddingresult)
- [NLModel](https://developer.apple.com/documentation/naturallanguage/nlmodel)
- [NLModelConfiguration](https://developer.apple.com/documentation/naturallanguage/nlmodelconfiguration)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
