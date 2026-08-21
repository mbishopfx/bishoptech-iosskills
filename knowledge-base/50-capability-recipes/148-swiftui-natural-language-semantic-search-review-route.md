# SwiftUI Natural Language and local semantic-retrieval route

Use this route when an app needs private on-device language analysis, local semantic search, source-linked tags, or reviewable text candidates. It pairs with the [framework review](../42-framework-deep-dives/117-swiftui-natural-language-semantic-search-review.md), the [design route](../21-design-deep-dives/145-swiftui-natural-language-semantic-search-review-design.md), the [proof matrix](../60-verification/142-swiftui-natural-language-semantic-search-proof-matrix.md), and the [recipes](../70-code-recipes/160-swiftui-natural-language-semantic-search-review-recipes.md).

This is a route sketch, not a claim that the snippets compile against every iOS 26 SDK revision. Compile each selected API in a named target and verify the actual language assets and device behavior.

## Route 1: Freeze the outcome and data boundary

Write the product contract before choosing an NLP object:

| Contract | Example |
| --- | --- |
| Input | A user-authored note, imported document, or selected record |
| Output | Similar-source candidates or reviewable tags |
| Source identity | App-owned record ID plus content revision |
| Language | Auto-detected with a user-selectable constraint |
| Representation | Sentence NLEmbedding, custom vocabulary, contextual vectors, or NLModel |
| Review | Evidence excerpt, source link, edit, approve, discard |
| Commit | App-owned tag, link, or saved relation |
| Fallback | Exact search, manual tag, or “not available” |

Reject a route that cannot preserve the original source, map output back to a range or record, and prevent a stale candidate from mutating current data.

## Route 2: Choose the representation

Use this decision table:

| Requirement | Route |
| --- | --- |
| Need a language candidate | NLLanguageRecognizer |
| Need token or sentence ranges | NLTokenizer |
| Need part of speech, name, lemma, script, or custom token tags | NLTagger |
| Need word/sentence semantic distance | NLEmbedding |
| Need contextual subword vectors for a classifier/tagger or a custom representation | NLContextualEmbedding |
| Need trained labels for text | NLModel backed by a Core ML model |
| Need system discovery or handoff | Core Spotlight/App Intents route, separately reviewed |

Do not select NLContextualEmbedding merely because “contextual” sounds more intelligent. Apple’s Natural Language documentation points semantic-similarity tasks to NLEmbedding. Use contextual vectors only when the product has a pooling, scoring, and evaluation plan.

## Route 3: Define source and derived identities

Create app-owned identities before work begins:

    SourceID
    SourceRevision
    NormalizationVersion
    Language
    RepresentationKind
    ModelOrEmbeddingIdentifier
    ModelOrEmbeddingRevision
    IndexRevision

Persist the identity beside every chunk, tag, vector, or candidate. If an embedding file or Natural Language revision changes, mark the old derived records stale rather than silently comparing them.

## Route 4: Detect and constrain language

Use NLLanguageRecognizer on an analysis-owned actor or serial executor. For short text, expose ambiguity instead of treating the dominant-language result as certain. If the app knows an allowed language set, provide languageConstraints and optional languageHints.

Keep language state separate from query state:

    query text -> language detection
                   -> supported representation check
                   -> asset readiness
                   -> analysis

If the language is unsupported, route to exact search or manual review. Do not pass the text into an unrelated language model and label the result as comparable.

## Route 5: Tokenize and tag with source ranges

For segmentation:

1. instantiate NLTokenizer with the desired unit;
2. set the language when known;
3. assign the original analysis string;
4. enumerate ranges;
5. attach every range to the source revision and normalization version.

For linguistic tags:

1. ask NLTagger for available tag schemes for the language and unit;
2. request missing assets when necessary;
3. create NLTagger with only the schemes needed;
4. set custom NLModel instances for custom tag schemes when required;
5. enumerate tags over the original String range;
6. preserve missing-tag and unknown-language outcomes.

NLTokenizer and NLTagger instances have documented thread-ownership restrictions. Keep them inside the actor that owns the operation; do not reuse one mutable instance across concurrent tasks.

## Route 6: Build an NLEmbedding index

For a bounded, app-owned collection:

1. select word or sentence embedding;
2. confirm the language and revision are available;
3. normalize and chunk each source with an explicit policy;
4. compute a vector for each chunk;
5. store dimension, language, revision, source revision, and range;
6. persist the vector or a safe app-owned representation;
7. query with the same representation contract;
8. apply deterministic scope and authorization filters;
9. rank by the selected distance;
10. return source-linked candidates for review.

NLEmbedding’s vocabulary-neighbor APIs are useful for a known vocabulary. For arbitrary documents, an app-owned index usually needs its own bounded scan or storage strategy. That index is product code, not a promise supplied by NLEmbedding.

Start with a simple, correct scan for small collections. Add a specialized index only after measuring the end-to-end path and defining a correctness fixture. Keep a reference implementation so an optimized index can be compared against it.

## Route 7: Use contextual embeddings deliberately

When the product needs contextual vectors:

1. select a model identifier, language, or script;
2. inspect languages, scripts, revision, dimension, and maximumSequenceLength;
3. check hasAvailableAssets;
4. call requestAssets when the user chooses the feature;
5. load the model within a bounded lifecycle;
6. compute NLContextualEmbeddingResult;
7. enumerate subword vectors and preserve ranges;
8. pool vectors using an app-owned policy;
9. evaluate the pooled representation against labeled positives and negatives;
10. unload the model when work completes or memory pressure requires it.

Long text must be chunked before it exceeds maximumSequenceLength. Record the chunk range and whether the result is complete or truncated. A contextual result with a plausible vector is not evidence that the whole document was represented.

## Route 8: Integrate an NLModel

For a text classifier:

1. obtain the Core ML model with the correct Natural Language metadata;
2. construct NLModel from the model or compiled URL;
3. inspect its configuration, language, type, and revision;
4. call predictedLabel or predictedLabelHypotheses;
5. map the label to an app-owned candidate;
6. apply thresholds and domain validation;
7. show source evidence and an edit/approval action.

For a word tagger:

1. create NLModel;
2. create an NLTagger with the built-in and custom tag schemes;
3. set the NLModel for the custom scheme;
4. enumerate token-level results;
5. attach label/range/model revision to a reviewable candidate.

Keep Core ML model asset delivery and compilation as a separate route if the model is downloaded. A generated Swift wrapper or a local model file does not prove the correct Natural Language metadata, supported language, or release packaging.

## Route 9: Design the app-owned index

A minimal chunk record:

    id
    sourceID
    sourceRevision
    originalRange
    displayExcerpt
    language
    representationKind
    modelIdentifier
    modelRevision
    vectorDimension
    vector
    indexRevision
    deleted

An index query should return a candidate with:

    sourceID
    sourceRevision
    excerpt
    range
    distanceOrScore
    representation
    freshness
    reason

Before showing a candidate, verify:

- the source still exists;
- the source revision matches;
- the person still has access;
- the candidate’s language and representation match the query;
- the index row is not deleted or stale;
- the destination has not changed;
- the score is within the current policy.

## Route 10: Apply exact filters before or after semantic ranking

Use semantic similarity for candidate generation. Use deterministic rules for safety and meaning:

- owner/account;
- collection;
- date range;
- record status;
- explicit source type;
- required label;
- current authorization;
- duplicate and conflict policy.

The order can vary by workload, but the contract must be explicit. A semantic ranker should not be able to return a private record from outside the current scope simply because its vector is close.

## Route 11: State and cancellation

Expose a small state machine to SwiftUI:

    idle
    preparingLanguage
    preparingAssets
    indexing
    searching
    partial
    review
    stale
    failed

Associate every task with a generation:

    queryGeneration + sourceRevision + indexRevision

On completion, publish only if all three still match the current state. Cancellation can stop publication and release app-owned buffers; it should not be represented as a fake “no results” state.

Bound:

- input character/document length;
- chunk count;
- asset requests;
- concurrent index builds;
- candidate count;
- UI update frequency.

## Route 12: SwiftUI shell

Build the UI around:

1. source/collection;
2. query;
3. language/availability;
4. result candidates;
5. evidence and freshness;
6. review actions;
7. exact/manual fallback.

Use Liquid Glass only for compact functional controls and status grouping. Keep evidence and warnings legible on stable surfaces. The domain layer should never receive NLTokenizer, NLTagger, NLEmbedding, NLContextualEmbedding, or NLModel objects; it should receive app-owned value types.

## Route 13: Test layers

Create deterministic fixtures for:

- known language and ambiguous language;
- short query and long query;
- punctuation, emoji, diacritics, and mixed script;
- positive and negative semantic pairs;
- out-of-scope records with high similarity;
- changed source revision;
- changed embedding/model revision;
- unavailable tag or embedding assets;
- empty vocabulary or no candidate;
- cancelled query followed by a newer query;
- deleted source and stale index row.

Compare an optimized index or pooling strategy against a simple reference implementation. Include range integrity and source identity in expected results, not only the top-ranked label.

## Route 14: Device and release route

On the intended physical device:

- verify target SDK and deployment target;
- verify language asset availability and request behavior;
- run the same fixtures used by the reference test;
- measure cold and warm asset/model/index behavior;
- test memory pressure, interruption, backgrounding, and relaunch;
- complete the search/review task with VoiceOver and Dynamic Type;
- verify exact-search/manual fallback;
- inspect privacy logs and deletion behavior.

For a signed archive and TestFlight build:

- confirm model/embedding assets are packaged or delivered as designed;
- confirm the index migration and revision policy;
- confirm no debug text/vector logging ships;
- confirm the UI does not claim local/private support when a system handoff or sync route exists;
- repeat the primary acceptance path.

## Route stop conditions

- A model or embedding is selected without a language, asset, and revision contract.
- The app persists vectors without source identity or deletion behavior.
- Search results can cross an authorization boundary.
- A contextual embedding is scored without a documented pooling/evaluation policy.
- A successful preview or simulator run is used as language-asset, accessibility, device, or release proof.

## Sources

- [Natural Language](https://developer.apple.com/documentation/naturallanguage)
- [NLTokenizer](https://developer.apple.com/documentation/naturallanguage/nltokenizer)
- [NLTagger](https://developer.apple.com/documentation/naturallanguage/nltagger)
- [NLTagger requestAssets](https://developer.apple.com/documentation/naturallanguage/nltagger/requestassets%28for%3Atagscheme%3Acompletionhandler%3A%29)
- [NLLanguageRecognizer](https://developer.apple.com/documentation/naturallanguage/nllanguagerecognizer)
- [Identifying the language in text](https://developer.apple.com/documentation/naturallanguage/identifying-the-language-in-text)
- [NLEmbedding](https://developer.apple.com/documentation/naturallanguage/nlembedding)
- [Finding similarities between pieces of text](https://developer.apple.com/documentation/naturallanguage/finding-similarities-between-pieces-of-text)
- [NLContextualEmbedding](https://developer.apple.com/documentation/naturallanguage/nlcontextualembedding)
- [NLContextualEmbeddingResult](https://developer.apple.com/documentation/naturallanguage/nlcontextualembeddingresult)
- [NLModel](https://developer.apple.com/documentation/naturallanguage/nlmodel)
- [NLModelConfiguration](https://developer.apple.com/documentation/naturallanguage/nlmodelconfiguration)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Model Integration Samples](https://developer.apple.com/documentation/coreml/model-integration-samples)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
