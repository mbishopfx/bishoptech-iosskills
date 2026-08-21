# SwiftUI Natural Language and local semantic-retrieval proof matrix

Use this matrix with the [framework review](../42-framework-deep-dives/117-swiftui-natural-language-semantic-search-review.md), the [design route](../21-design-deep-dives/145-swiftui-natural-language-semantic-search-review-design.md), the [implementation route](../50-capability-recipes/148-swiftui-natural-language-semantic-search-review-route.md), and the [code recipes](../70-code-recipes/160-swiftui-natural-language-semantic-search-review-recipes.md).

The proof vocabulary is strict:

- **Source proof** — the current Apple API and HIG source was reviewed.
- **Compile proof** — the selected target compiles with the named SDK.
- **Fixture proof** — deterministic language, source, and expected-output fixtures pass.
- **Device proof** — the intended physical device has the required assets, memory, performance, and accessibility behavior.
- **System proof** — Core Spotlight/App Intents or other system handoff behaves in the real system surface.
- **Release proof** — archive/TestFlight metadata, model/embedding assets, privacy behavior, and the primary task work in the signed artifact.

A green compile, a vector, or a top-ranked result is only one piece of evidence.

## 1. Evidence matrix

| Area | Evidence to collect | Minimum acceptance | Does not prove |
| --- | --- | --- | --- |
| Target | SDK, deployment target, target name, device family | The selected Natural Language route is compiled by the intended target | All devices or languages support the same assets |
| Source | Official Natural Language, model, design, accessibility, and release links | Current API semantics and availability boundaries are recorded | Implementation correctness |
| Input | Source ID, source revision, original text, normalized text, normalization version | Results map to the intended source | That normalized text preserves every meaning |
| Language | NLLanguageRecognizer result, hypotheses, hints/constraints, fixture | Supported and ambiguous states are visible and recoverable | Linguistic certainty |
| Tokenization | NLTokenizer unit, ranges, language, fixture | Word/sentence/paragraph/document ranges map to original text | Business segmentation |
| Tags | NLTagger schemes, asset result, tag ranges, missing-tag behavior | Tags are source-linked and unavailable schemes do not masquerade as labels | Entity identity or authorization |
| Thread ownership | Actor/serial executor and object lifecycle | Mutable NLP instances are not used simultaneously across threads | That an async task cannot outlive its source |
| Static embedding | Word/sentence kind, language, revision, dimension, distance type | Query and index use the same representation contract | Domain relevance or truth |
| Custom embedding | File URL/digest, vocabulary, language, revision, build policy | Custom data can be loaded and rebuilt reproducibly | A custom vocabulary covers future user language |
| Contextual embedding | Model identifier, languages/scripts, revision, dimension, maximum sequence length, asset result | Asset/load/compute/unload lifecycle is observable | A subword vector sequence is a sentence similarity score |
| Pooling | Pooling method, normalization, chunk policy, labeled fixtures | Pooled vectors are evaluated against positive and negative examples | General semantic quality |
| Natural Language model | Core ML model identity, NLModel configuration, type, language, revision | Classifier or sequence-tagging output maps to a reviewable candidate | Label correctness outside the fixture distribution |
| Classification | Label hypotheses, threshold policy, evidence, manual correction | Low-confidence or unknown labels remain reviewable | Safe side effects |
| Index | Record identity, source revision, vector identity, index revision, deletion state | Stale or deleted rows are excluded or visibly marked | Complete retrieval recall |
| Ranking | Reference implementation, optimized implementation, distance/score, filters | Ranking is deterministic for the same fixture and scope | Universal benchmark quality |
| Authorization | Account/collection/source scope checked before display and commit | Semantic ranking cannot cross access boundaries | That the source itself is safe to share |
| Freshness | Query generation, source revision, model/embedding revision, index revision | Stale results cannot commit to current data | User intent after a long review |
| Cancellation | Cancelled task, newer query, late completion fixture | Late work does not publish or mutate current state | Hardware cancellation of already submitted work |
| Privacy | Retention/deletion test, log redaction, index/system handoff inventory | Raw text, vectors, and diagnostics match documented policy | “On device” means no data leaves the app |
| SwiftUI state | Ready/preparing/partial/stale/review/fallback/error fixtures | The UI reports actual availability and freshness | Native appearance by itself |
| Liquid Glass | Standard-controls-first review, reduced-transparency screenshot/recording | Material groups actions without hiding evidence or warnings | Accessibility or privacy |
| Accessibility | VoiceOver, Dynamic Type, keyboard, pointer, Switch Control, RTL | Search/review/save/discard completes without gesture-only requirements | Every language is equally readable |
| Performance | Cold/warm assets, index build/query latency, memory, energy | Representative workload meets product budget on target device | Other devices or future OS versions |
| Interruption | Background/foreground, memory pressure, relaunch, source changes | State recovers with stale/partial explanation | Long-term persistence reliability |
| Release | Archive, TestFlight, model/embedding assets, privacy manifest if applicable | Signed artifact reproduces the primary task and fallback | App Store approval |

## 2. Fixture design

Use a fixture set that includes:

- a known language with a known positive pair;
- a negative semantic pair that shares keywords but should not match;
- an ambiguous or too-short language sample;
- mixed-language content;
- punctuation, emoji, diacritics, and non-whitespace scripts;
- long text that reaches the chunk or contextual sequence limit;
- a changed source revision with an old candidate;
- a changed embedding/model revision;
- an unavailable tag or embedding asset;
- an empty or deleted source;
- an out-of-scope record with a high similarity score;
- a cancelled query followed by a newer query;
- a classifier label that needs manual correction;
- an accessibility label with a long localized source excerpt.

Store the expected source ID, range, language, representation identity, and candidate policy. Do not assert only that “some result exists.”

## 3. Representation proof

For each representation, record:

    representationKind
    language
    modelIdentifier
    revision
    dimension
    normalizationVersion
    chunkingVersion

For NLEmbedding, prove that query and indexed text use the same word/sentence choice, language, revision, and distance type. For NLContextualEmbedding, prove the model was available, loaded, used within its sequence limit, and pooled according to the selected policy. For NLModel, prove the Core ML artifact carries the Natural Language metadata expected by NLModel and that classifier versus sequence behavior is correct.

## 4. Range and source proof

For token or tag output:

1. keep the original Swift String;
2. record the returned Range<String.Index>;
3. show the same range in the review fixture;
4. verify that normalization does not shift it without a mapping;
5. mutate the source and ensure the old range becomes stale.

For retrieval:

1. create a source revision;
2. index one or more chunks;
3. query and return a source-linked candidate;
4. edit the source;
5. verify the old candidate cannot save against the new revision;
6. delete the source;
7. verify the vector/index row and UI state follow the deletion policy.

## 5. Asset and language proof

Record the result of:

- available tag schemes for the selected unit and language;
- NLTagger requestAssets;
- contextual embedding hasAvailableAssets;
- contextual embedding requestAssets;
- contextual model load and unload;
- NLEmbedding language/revision lookup;
- NLModel configuration language/type/revision.

Test cold and warm behavior. A device with a language asset already present can hide an onboarding or download path that a clean device exposes.

## 6. Retrieval correctness proof

Use a simple reference scan and compare any optimized index against it:

| Check | Requirement |
| --- | --- |
| Same representation | Same language, revision, dimensions, and normalization |
| Same scope | Same owner, collection, date, and permission filters |
| Same candidates | No unauthorized or deleted records |
| Same ordering | Ties and deterministic secondary ordering are defined |
| Same evidence | Source ranges and excerpts match |
| Same stale policy | Changed sources cannot silently reuse old rows |

Measure recall and false-positive behavior on labeled fixtures. Treat thresholds as app policy. If the product cannot explain a candidate to a person, it should not silently commit it.

## 7. UI and accessibility proof

Capture evidence for:

- empty, partial, stale, unsupported, and failed states;
- semantic versus exact search;
- source evidence and review;
- VoiceOver candidate order and labels;
- Dynamic Type at a large size;
- keyboard and pointer search/review;
- RTL and long localized text;
- reduced transparency and reduced motion;
- manual/exact fallback.

The test task is complete only when a person can choose a source, enter a query, understand the current language/asset state, review evidence, and approve or discard a candidate.

## 8. Privacy proof

Write a data-path table:

| Artifact | Retained? | Location | Deletion trigger | Diagnostic policy |
| --- | --- | --- | --- | --- |
| Original text | Product-defined | App-owned source store | Source deletion | Redact by default |
| Normalized text | Product-defined | Derived store | Source/revision deletion | Do not log raw text |
| Token/tag ranges | Usually derived | App-owned index | Source revision/deletion | Metadata only |
| Embeddings | Product-defined | App-owned index | Source/model deletion | Never dump by default |
| Model/asset metadata | Usually safe metadata | App support store | Revision cleanup | Model ID/revision/dimension |
| Candidate | Review lifetime | App state/store | Review cancel or source change | Source ID and redacted reason |
| System index | Optional | System service | App deletion policy | Verify handoff separately |

Prove that deletion affects all app-owned derived artifacts. If a system index or sync path exists, document its separate lifecycle.

## 9. Device and release proof

On the intended physical device, capture:

- device model and OS;
- target SDK and build configuration;
- language and asset readiness;
- cold/warm timings;
- peak memory and sustained behavior;
- background/foreground recovery;
- accessibility task result;
- exact/manual fallback;
- logs showing no raw text/vector leakage.

For archive/TestFlight:

- inspect the signed artifact’s model/embedding assets;
- test clean install and upgrade from an older index revision;
- run the same positive/negative fixtures;
- verify the user-facing local-processing copy matches the actual data path;
- confirm production logging and debug inspector policy.

## 10. Evidence packet template

    Route: Natural Language local semantic retrieval
    Target: <target name>
    SDK/deployment: <values>
    Device/OS: <physical device>
    Language fixture: <language/script>
    Representation: <kind/model/revision/dimension>
    Assets: <available/requested/result>
    Source contract: <ID/revision/normalization>
    Index: <revision/chunk policy/deletion policy>
    Fixture result: <positive/negative/ambiguous/stale>
    Accessibility: <task and outcome>
    Privacy: <retention/deletion/logging>
    Performance: <cold/warm/peak memory/sustained>
    Signed artifact: <archive/TestFlight/build>
    Open risks: <known limitations>

## Stop conditions

- The proof packet omits language, asset, model, or embedding revision.
- A result cannot be traced to a source range or stable record.
- The optimized index has no reference comparison.
- Privacy proof checks only framework imports and not retention, deletion, sync, or logs.
- Accessibility proof is a screenshot without a completed task.
- A simulator or Debug build is treated as physical-device or release evidence.

## Sources

- [Natural Language](https://developer.apple.com/documentation/naturallanguage)
- [NLTokenizer](https://developer.apple.com/documentation/naturallanguage/nltokenizer)
- [NLTagger](https://developer.apple.com/documentation/naturallanguage/nltagger)
- [NLTagger requestAssets](https://developer.apple.com/documentation/naturallanguage/nltagger/requestassets%28for%3Atagscheme%3Acompletionhandler%3A%29)
- [NLLanguageRecognizer](https://developer.apple.com/documentation/naturallanguage/nllanguagerecognizer)
- [NLEmbedding](https://developer.apple.com/documentation/naturallanguage/nlembedding)
- [NLContextualEmbedding](https://developer.apple.com/documentation/naturallanguage/nlcontextualembedding)
- [NLContextualEmbeddingResult](https://developer.apple.com/documentation/naturallanguage/nlcontextualembeddingresult)
- [NLModel](https://developer.apple.com/documentation/naturallanguage/nlmodel)
- [NLModelConfiguration](https://developer.apple.com/documentation/naturallanguage/nlmodelconfiguration)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
