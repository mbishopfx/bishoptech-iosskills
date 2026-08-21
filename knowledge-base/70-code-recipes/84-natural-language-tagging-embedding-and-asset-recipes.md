# Natural Language tagging, embedding, and asset recipes

These are compile-oriented route sketches. Check the selected SDK’s language/scheme availability, model revision, asset behavior, and input limits before shipping. Keep analysis instances isolated and never treat a tag/vector as an unquestionable fact.

## 1. Tokenize a bounded string

Use an NLTokenizer instance for one serial operation at a time.

~~~swift
import NaturalLanguage

struct TokenSpan: Sendable {
    let text: String
    let range: Range<String.Index>
}

func wordSpans(in text: String, language: NLLanguage?) -> [TokenSpan] {
    guard !text.isEmpty else { return [] }

    let tokenizer = NLTokenizer(unit: .word)
    tokenizer.string = text
    if let language {
        tokenizer.setLanguage(language)
    }

    var result: [TokenSpan] = []
    let fullRange = text.startIndex..<text.endIndex
    tokenizer.enumerateTokens(in: fullRange) { range, _ in
        result.append(TokenSpan(text: String(text[range]), range: range))
        return true
    }
    return result
}
~~~

For paragraph, sentence, or document units, create a tokenizer with the corresponding NLTokenUnit. Bound very large input and retain the source range with the token.

## 2. Tag names or lexical classes

Ask the device whether the desired tag scheme is available for the language before configuring the feature.

~~~swift
import NaturalLanguage

struct LinguisticTagSpan: Sendable {
    let tag: String?
    let text: String
    let range: Range<String.Index>
}

func nameAndLexicalTags(
    in text: String,
    language: NLLanguage
) -> [LinguisticTagSpan] {
    let schemes = NLTagger.availableTagSchemes(
        for: .word,
        language: language
    )
    guard schemes.contains(.nameTypeOrLexicalClass) else {
        return []
    }

    let tagger = NLTagger(
        tagSchemes: [.nameTypeOrLexicalClass, .lemma]
    )
    tagger.string = text
    let range = text.startIndex..<text.endIndex
    tagger.setLanguage(language, range: range)

    var output: [LinguisticTagSpan] = []
    let options: NLTagger.Options = [
        .omitWhitespace,
        .omitPunctuation,
        .joinNames
    ]
    tagger.enumerateTags(
        in: range,
        unit: .word,
        scheme: .nameTypeOrLexicalClass,
        options: options
    ) { tag, tokenRange in
        output.append(
            LinguisticTagSpan(
                tag: tag?.rawValue,
                text: String(text[tokenRange]),
                range: tokenRange
            )
        )
        return true
    }
    return output
}
~~~

The tagger’s serial-use rule still applies. If the operation runs concurrently, create a separate tagger per task or isolate the analyzer behind an actor.

## 3. Detect language with a qualified fallback

Language identification should retain hypotheses and support a user override.

~~~swift
import NaturalLanguage

struct LanguageGuess: Sendable {
    let dominant: NLLanguage?
    let hypotheses: [(NLLanguage, Double)]
}

func guessLanguage(for text: String) -> LanguageGuess {
    guard !text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
        return LanguageGuess(dominant: nil, hypotheses: [])
    }

    let recognizer = NLLanguageRecognizer()
    recognizer.processString(text)
    let hypotheses = recognizer
        .languageHypotheses(withMaximum: 3)
        .map { ($0.key, $0.value) }
    return LanguageGuess(
        dominant: recognizer.dominantLanguage,
        hypotheses: hypotheses
    )
}
~~~

Do not map a short-text guess directly to a consequential action. Show unknown/mixed language and allow a manual language choice.

## 4. Compare strings with a sentence embedding

Use the language and revision that match the product’s evaluation data.

~~~swift
import NaturalLanguage

struct SimilarPhrase: Sendable {
    let value: String
    let distance: Double
}

func nearestEnglishPhrases(
    to text: String,
    maximumCount: Int
) -> [SimilarPhrase] {
    guard let embedding = NLEmbedding.sentenceEmbedding(
        for: .english
    ) else {
        return []
    }

    return embedding.neighbors(
        for: text,
        maximumCount: maximumCount,
        distanceType: .cosine
    ).map {
        SimilarPhrase(value: $0.0, distance: $0.1)
    }
}
~~~

Record the embedding revision and vocabulary source in the app-owned result. Distance is a ranking signal, not a truth/identity/intent score.

## 5. Request and load contextual embedding assets

Contextual embedding assets can be unavailable, require a download, fail, or be present but not loaded.

~~~swift
import NaturalLanguage

enum ContextualEmbeddingState: Equatable {
    case unavailable
    case requesting
    case notAvailable
    case ready(model: String, revision: Int)
}

func loadEnglishContextualEmbedding(
    text: String
) async throws -> (ContextualEmbeddingState, NLContextualEmbeddingResult?) {
    guard let embedding = NLContextualEmbedding(language: .english) else {
        return (.unavailable, nil)
    }

    if !embedding.hasAvailableAssets {
        let result = try await embedding.requestAssets()
        guard result == .available else {
            return (.notAvailable, nil)
        }
    }

    try embedding.load()
    defer { embedding.unload() }

    let value = try embedding.embeddingResult(
        for: text,
        language: .english
    )
    return (
        .ready(
            model: embedding.modelIdentifier,
            revision: embedding.revision
        ),
        value
    )
}
~~~

Show the asset/download state and provide a basic fallback. Do not claim offline contextual analysis until the asset is actually available on the device.

## 6. Load a custom Natural Language model

NLModel can load a custom text classifier or word tagger. Preserve its configuration and revision in the feature record.

~~~swift
import NaturalLanguage

struct TextModelDecision: Sendable {
    let label: String?
    let hypotheses: [String: Double]
    let modelType: NLModel.ModelType
    let language: NLLanguage?
    let revision: Int
}

func classify(
    text: String,
    modelURL: URL
) throws -> TextModelDecision {
    let model = try NLModel(contentsOf: modelURL)
    let configuration = model.configuration
    return TextModelDecision(
        label: model.predictedLabel(for: text),
        hypotheses: model.predictedLabelHypotheses(
            for: text,
            maximumCount: 3
        ),
        modelType: configuration.type,
        language: configuration.language,
        revision: configuration.revision
    )
}
~~~

Use a no-model/unknown-label fallback and require review before applying a label to an external or consequential action.

## 7. Isolate reference-type analyzers behind an actor

The actor creates a fresh tagger for each operation and avoids sharing mutable Natural Language objects across tasks.

~~~swift
import NaturalLanguage

actor TextAnalyzer {
    func tokenize(_ text: String) -> [String] {
        let tokenizer = NLTokenizer(unit: .sentence)
        tokenizer.string = text
        let range = text.startIndex..<text.endIndex
        var sentences: [String] = []
        tokenizer.enumerateTokens(in: range) { tokenRange, _ in
            sentences.append(String(text[tokenRange]))
            return true
        }
        return sentences
    }
}
~~~

An actor does not solve input-size, memory, model-asset, or privacy policy by itself. Keep those boundaries in the route.

## 8. Prepare a redacted local-AI input

Use Natural Language as a deterministic preprocessing layer before a generative model sees a user-selected text range.

~~~swift
struct RedactedTextInput: Sendable {
    let text: String
    let language: String
    let sourceRangeDescription: String
    let modelRevision: Int?
}

func makeLocalAIInput(
    original: String,
    language: NLLanguage,
    modelRevision: Int?
) -> RedactedTextInput {
    // Replace this with a reviewed redaction policy. Never assume that
    // missing tags mean that sensitive text is absent.
    RedactedTextInput(
        text: original,
        language: language.rawValue,
        sourceRangeDescription: "user-selected text",
        modelRevision: modelRevision
    )
}
~~~

Keep original text, redacted text, tag ranges, embeddings, model output, and user-approved result as separate values. A local model can still be wrong.

## 9. Test language and asset semantics

Use Swift Testing for pure fallback logic, then run framework and device fixtures.

~~~swift
import Testing

@Test
func emptyTextHasNoLanguageGuess() {
    let guess = guessLanguage(for: "   ")
    #expect(guess.dominant == nil)
    #expect(guess.hypotheses.isEmpty)
}

@Test
func unavailableEmbeddingDoesNotBecomeAResult() {
    let state = ContextualEmbeddingState.notAvailable
    #expect(state != .ready(model: "unknown", revision: 0))
}
~~~

These tests prove app-owned semantics. They do not prove language coverage, asset download, model quality, memory, thermal behavior, or release readiness.

## Sources

- [Natural Language](https://developer.apple.com/documentation/naturallanguage)
- [NLTokenizer](https://developer.apple.com/documentation/naturallanguage/nltokenizer)
- [NLTagger](https://developer.apple.com/documentation/naturallanguage/nltagger)
- [NLLanguageRecognizer](https://developer.apple.com/documentation/naturallanguage/nllanguagerecognizer)
- [NLEmbedding](https://developer.apple.com/documentation/naturallanguage/nlembedding)
- [NLContextualEmbedding](https://developer.apple.com/documentation/naturallanguage/nlcontextualembedding)
- [NLContextualEmbedding.AssetsResult](https://developer.apple.com/documentation/naturallanguage/nlcontextualembedding/assetsresult)
- [NLModel](https://developer.apple.com/documentation/naturallanguage/nlmodel)
- [NLModelConfiguration](https://developer.apple.com/documentation/naturallanguage/nlmodelconfiguration)
- [NLModelConfiguration.type](https://developer.apple.com/documentation/naturallanguage/nlmodelconfiguration/type)
- [requestAssets(completionHandler:)](https://developer.apple.com/documentation/naturallanguage/nlcontextualembedding/requestassets%28completionhandler%3A%29)
- [load()](https://developer.apple.com/documentation/naturallanguage/nlcontextualembedding/load%28%29)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Testing](https://developer.apple.com/documentation/testing)
