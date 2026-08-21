# SwiftUI Natural Language and local semantic-retrieval review

This review covers Apple’s Natural Language framework as a local text-understanding layer for iOS 26 apps: language identification, tokenization, linguistic tagging, static word and sentence embeddings, contextual embeddings, and Natural Language models backed by Core ML. It pairs with the [semantic-retrieval design](../21-design-deep-dives/145-swiftui-natural-language-semantic-search-review-design.md), the [implementation route](../50-capability-recipes/148-swiftui-natural-language-semantic-search-review-route.md), the [proof matrix](../60-verification/142-swiftui-natural-language-semantic-search-proof-matrix.md), and the [code recipes](../70-code-recipes/160-swiftui-natural-language-semantic-search-review-recipes.md).

The product boundary is deliberate:

    source text -> language and representation -> local candidate retrieval
        -> source-linked review -> explicit app-owned decision

Natural Language can provide useful representations and model predictions. It does not decide whether a person’s text should be saved, shared, acted on, or treated as true. A local embedding is not a fact database, and a high similarity score is not authorization.

## 1. Select the smallest text-intelligence route

| Product need | First route | Owns | Does not prove |
| --- | --- | --- | --- |
| Detect the likely language | NLLanguageRecognizer | Dominant language, hypotheses, hints, and constraints | That a short, mixed, quoted, or domain-specific string was identified correctly |
| Segment text | NLTokenizer | Word, sentence, paragraph, or document ranges | That a token boundary is the right business boundary |
| Add linguistic metadata | NLTagger | Part of speech, lexical class, lemma, name, language, script, and custom tag schemes | Entity identity, user intent, or domain truth |
| Compare words or sentences | NLEmbedding | Vectors, vocabulary, distance, nearest neighbors, language, and revision | A calibrated relevance score for every app domain |
| Produce context-sensitive token vectors | NLContextualEmbedding | Model identity, language/script, revision, assets, sequence length, and subword vectors | A ready-made sentence similarity metric or stable cross-revision result |
| Classify or tag with a trained model | NLModel | Labels, hypotheses, sequence/classifier type, language, and revision | Safe side effects, correct thresholds, or current domain meaning |
| Discover app-owned records | App-owned index plus optional Core Spotlight/App Intents | Stable record identity, source revision, ranking, and handoff | That system discovery and local semantic ranking are the same route |

Start with deterministic segmentation or language detection when that solves the task. Add embeddings for similarity and retrieval. Add a custom model when the app needs a trained label or sequence-tagging contract. Use a larger model only when the product requirement justifies its cost, availability, and evaluation burden.

## 2. Freeze the text and source contract

Before analysis, define:

- the source record identifier;
- the source revision or content digest;
- whether the source is app-owned, imported, shared, or user-entered;
- the original text and the normalized analysis text;
- locale, writing system, and language hint;
- allowed retention for raw text, tags, vectors, and diagnostics;
- the destination of any candidate result.

Do not silently replace source text with a normalized copy. Keep the original for display and preserve the exact range mapping needed to highlight evidence. Normalization can change punctuation, whitespace, case, diacritics, script, or token boundaries. Record the normalization version with every derived artifact.

A useful derived identity is:

    sourceID + sourceRevision + normalizationVersion
        + representationKind + language + modelRevision

When any component changes, invalidate or recompute the dependent candidate rather than presenting an old score as current.

## 3. Language identification is a gate, not a decorative label

NLLanguageRecognizer can report a dominant language or multiple language hypotheses. The app can supply language hints and constraints when the product already knows something about its input. A recognizer instance is stateful: process the intended text, read the result, then reset it before starting a separate analysis stream.

Use a language state with at least:

| State | Meaning |
| --- | --- |
| unknown | The app has not analyzed the current source |
| detected | A language candidate exists and includes the analysis revision |
| ambiguous | Multiple languages remain plausible or the input is too short |
| unsupported | The selected representation/model has no route for the language |
| ready | The selected Natural Language assets and representation are usable |
| failed | The app has a recoverable analysis error |

Language detection is especially important for embeddings. A word or sentence embedding is selected by language and revision. A contextual embedding exposes the languages and scripts it supports. A model configuration also carries a language and a Natural Language framework revision. Never mix vectors or predictions across undocumented languages, model identifiers, or revisions and call the result comparable.

## 4. Tokenization and tagging preserve linguistic ranges

NLTokenizer segments a string into words, sentences, paragraphs, or a document. The tokenizer returns ranges into the original Swift String. Keep those ranges attached to the source revision rather than converting them to byte offsets without a mapping policy.

NLTagger can enumerate or return tags for a range at a chosen token unit and tag scheme. Depending on the scheme, tags can describe token type, lexical class, name type, lemma, language, or script. The app can install a custom NLModel for a custom tag scheme when its trained model has a sequence-tagging contract.

Important implementation boundaries:

- select the unit and scheme explicitly;
- use only schemes available for the selected language on the current device;
- request missing Natural Language assets before the analysis action;
- treat a missing tag as a real outcome rather than converting it to a false label;
- preserve the text range and source revision with each tag;
- do not use a lexical tag as a domain permission or a person identity;
- do not share one NLTokenizer or NLTagger instance simultaneously across threads.

Apple documents requestAssets as a way to ask the framework to load missing tag-scheme assets. The UI should expose preparing or unavailable state while that work occurs, not pretend a fallback tagger is equivalent to a ready model.

## 5. NLEmbedding is the semantic-similarity route

NLEmbedding maps strings to vectors and exposes distance and nearest-neighbor operations. Natural Language provides built-in word and sentence embeddings for supported languages and revisions. Apps can also load or write a custom embedding representation, including an embedding compiled from a dictionary at development time or runtime.

Use NLEmbedding for:

- approximate phrase or sentence similarity;
- nearest-neighbor lookup in a known vocabulary;
- local semantic search over app-owned text chunks;
- candidate suggestions that are always rechecked against source and app policy.

Record:

- word versus sentence embedding;
- language;
- embedding revision;
- vector dimension and distance type;
- vocabulary/model file identity;
- source normalization and chunking policy;
- index build revision.

The higher the similarity, the smaller the distance is in the embedding space, but a distance is still a representation-space measurement. It is not a universal relevance score. Calibrate thresholds on representative, labeled examples and retain negative examples. If the app changes its chunking, language, normalization, vocabulary, or embedding revision, treat the old index as stale.

For a custom vocabulary, distinguish:

1. a fixed, app-owned vocabulary where NLEmbedding.neighbors is useful;
2. a document collection where the app stores chunk vectors and performs its own bounded search;
3. an operational record set where semantic similarity only proposes candidates and an exact identifier, permission, or source check decides what can be shown or changed.

Do not use nearest neighbors to grant access, identify a person, or issue a physical-world command without an independent authorization and validation layer.

## 6. NLContextualEmbedding is a different representation

NLContextualEmbedding produces a sequence of vectors whose values depend on surrounding text. Apple’s documentation distinguishes it from static word embeddings: context changes the vectors, and one word can produce multiple subword vectors. The result includes the processed string, language, sequence length, and token-vector enumeration.

Treat contextual embedding as a model and asset lifecycle:

1. select a model identifier, language, or script;
2. inspect supported languages, scripts, revision, dimension, and maximum sequence length;
3. check hasAvailableAssets;
4. request assets when needed;
5. load the model for bounded work;
6. compute an embedding result;
7. pool or otherwise combine subword vectors according to an app-owned, evaluated policy;
8. unload when the lifecycle and memory budget require it.

Apple explicitly points semantic-similarity work toward NLEmbedding. If the product uses contextual vectors for retrieval, the pooling method, normalization, distance function, sequence truncation, language, model identifier, and revision become part of the app’s own retrieval contract. Do not imply that a contextual token-vector sequence is a ready-made sentence score.

The maximum sequence length is a hard representation boundary. Long text must be chunked or summarized by an explicit policy, with source ranges retained. A silently truncated query or document can produce a plausible but semantically incomplete candidate.

## 7. Natural Language models connect Core ML to text contracts

NLModel integrates Core ML text-classifier and word-tagger models into Natural Language. The model configuration exposes the model type, language, and Natural Language framework revision. A classifier produces a label or multiple label hypotheses for a string. A sequence model can produce labels for tokens and can be attached to NLTagger under a custom tag scheme.

Keep these model types separate:

| Model type | Output | Review policy |
| --- | --- | --- |
| classifier | One or more labels for a phrase/sentence/paragraph | Show label, confidence/evidence policy, model revision, and a manual alternative |
| sequence tagger | Labels aligned to token ranges | Show highlighted spans and allow correction before durable use |

A label hypothesis is not a command. Map model output to an app-owned candidate type, then validate:

- expected language and model revision;
- source revision and range integrity;
- allowed labels and threshold policy;
- user/account authorization;
- current domain state;
- duplicate or conflict rules;
- destination and side-effect risk.

Use confidence as one input to review, not as proof. A classifier trained on one set of labels can be wrong because the language, vocabulary, writing style, or domain changed.

## 8. A local semantic-retrieval pipeline

For a private notes, documents, or capture app, a source-linked pipeline can look like this:

    import or edit source
        -> store original + revision
        -> detect/constrain language
        -> tokenize or chunk with ranges
        -> choose NLEmbedding or contextual representation
        -> build or query app-owned vector index
        -> apply exact filters and authorization
        -> rank bounded candidates
        -> show source quote, distance, revision, and freshness
        -> user reviews, edits, saves, or discards

The index is an app-owned data structure. Each row should include a stable record ID, source revision, chunk range, language, representation identity, vector dimension, vector payload or reference, and deletion state. A candidate should point back to the original source so the UI can show why it was returned.

Semantic ranking should be combined with deterministic constraints where the product has them:

- exact owner or account;
- current collection or document scope;
- date or status filter;
- source permission;
- supported language;
- minimum evidence length;
- duplicate suppression;
- domain-specific validation.

Use Core Spotlight or App Intents when the requirement is system discovery, indexing, or handoff. Use the local semantic index for app-owned retrieval. These routes can cooperate, but a Spotlight result is not a vector-search result and a vector match is not an Apple Intelligence handoff.

## 9. Concurrency, assets, and cancellation

Natural Language objects have thread-ownership rules. NLTokenizer, NLTagger, and NLLanguageRecognizer should not be used simultaneously from multiple threads. Give each analysis stream an actor or serial executor, or create an instance per operation. Do not publish mutable framework objects directly into SwiftUI state.

For asset-backed work:

- make asset readiness a first-class state;
- avoid downloading or loading assets on the main actor;
- deduplicate concurrent requests for the same language/model/revision;
- cancel publication when a newer source revision supersedes the query;
- bound document size, chunk count, and candidate count;
- release contextual models and large vectors when the task ends;
- distinguish unavailable assets from a model result of “no match.”

Cancellation may stop work or stop publication; it does not necessarily erase already-computed framework work. The app must make stale results harmless by checking source revision, query generation, and destination policy before publication.

## 10. SwiftUI and Liquid Glass

The primary UI should expose the human task, not the NLP implementation:

    source -> query -> candidates -> evidence -> review -> destination

Use a small status model:

| UI state | User-facing meaning |
| --- | --- |
| preparing | Language/model assets or the local index are being prepared |
| ready | The current source and query can be analyzed |
| searching | Candidates are being computed |
| partial | Some sources or languages are unavailable; results are incomplete |
| stale | The source or index changed after the result was computed |
| review | Candidates have source evidence and await a person’s decision |
| empty | No candidate passed the current policy |
| failed | The app can retry, change scope, or use exact search |

Liquid Glass is appropriate for a compact search field, scope switcher, filter control, or retry/fallback action when it improves grouping. Keep text evidence, confidence caveats, warnings, and dense result details on stable surfaces with clear contrast. A glass capsule should not hide that a result is partial, stale, unsupported, or awaiting review.

Candidate cards should show:

- a human-readable title;
- the source quote or matching range;
- the collection and revision;
- a plain-language reason such as “similar sentence” or “label match”;
- freshness/partial state;
- a primary review action and a safe alternative.

Do not show raw vectors as the primary result. Put diagnostics—dimension, model identifier, language, revision, distance type, and timing—behind an advanced disclosure.

## 11. Accessibility and alternate input

The task must be completable with VoiceOver, Dynamic Type, keyboard, pointer, Switch Control, and reduced visual effects:

1. choose a source or enter a query;
2. understand language and availability state;
3. start, cancel, or retry analysis;
4. navigate candidates in a stable order;
5. hear the source title, evidence, freshness, and reason;
6. open the source context;
7. approve, edit, save, or discard a candidate.

Group a candidate’s title, evidence, score explanation, and action semantics without hiding the source text from assistive technology. Avoid announcing every frame or incremental candidate. Announce meaningful changes such as “search complete,” “results are partial,” or “source changed; results refreshed.”

Long localized strings, RTL layout, mixed scripts, and languages that do not use spaces are part of the test matrix. Never use English token boundaries or string offsets as a universal assumption.

## 12. Privacy and retention

Natural Language can run locally, but text, embeddings, model assets, logs, diagnostics, sync, exports, and system indexes are separate data paths. Decide whether each is:

- transient in memory;
- persisted in an app-private store;
- shared with an extension or device;
- indexed for system discovery;
- included in diagnostics;
- eligible for deletion or export.

Embeddings can be sensitive because they are derived from private text. Store only what the product needs. Redact raw text and vector payloads from logs. Keep model/revision/dimension metadata separate from content when possible. Deleting a source should invalidate its chunks, vectors, cached candidates, and any system index or handoff that the app owns.

## 13. Availability and release proof

A source page and a successful local analysis are not enough. Record:

- target SDK and deployment target;
- actual device and OS;
- language and script fixture;
- available or requested Natural Language assets;
- embedding/model identifier and revision;
- source normalization/chunking/index revision;
- memory and latency under representative text;
- foreground/background/interruption behavior;
- accessibility task evidence;
- archive and TestFlight behavior with the same assets and model packaging.

Test at least one supported language with a positive fixture, a negative fixture, mixed or ambiguous language, long text, punctuation/emoji, and an unsupported-asset path. On the physical device, verify that the UI’s ready/partial/fallback state matches actual asset availability. A simulator result does not prove the same language asset, memory, performance, or model behavior on the intended device.

## 14. Review boundaries

The app may use Natural Language to produce:

- token ranges;
- linguistic annotations;
- embedding distances;
- nearest-neighbor candidates;
- classification or tagging hypotheses.

The app must still own:

- what the source means in the product;
- who may see or change it;
- whether a candidate is acceptable;
- how a person approves or edits it;
- what gets saved, shared, indexed, or acted on;
- how a changed model, language asset, or revision is rolled back.

### Stop conditions

- The route claims semantic similarity is truth, intent, authorization, or identity.
- A contextual embedding is presented as interchangeable with NLEmbedding without an evaluated pooling and scoring policy.
- Language/model/asset revisions are absent from persisted vectors or candidates.
- Raw text, embeddings, or diagnostics are retained without an explicit privacy policy.
- A green compile, preview, simulator result, or one successful match is treated as device, accessibility, domain, or release proof.

## Sources

- [Natural Language](https://developer.apple.com/documentation/naturallanguage)
- [NLTokenizer](https://developer.apple.com/documentation/naturallanguage/nltokenizer)
- [NLTagger](https://developer.apple.com/documentation/naturallanguage/nltagger)
- [NLTag](https://developer.apple.com/documentation/naturallanguage/nltag)
- [NLTokenUnit](https://developer.apple.com/documentation/naturallanguage/nltokenunit?changes=_3_1&language=objc)
- [NLLanguageRecognizer](https://developer.apple.com/documentation/naturallanguage/nllanguagerecognizer)
- [Identifying the language in text](https://developer.apple.com/documentation/naturallanguage/identifying-the-language-in-text)
- [NLLanguage](https://developer.apple.com/documentation/naturallanguage/nllanguage)
- [NLEmbedding](https://developer.apple.com/documentation/naturallanguage/nlembedding)
- [Finding similarities between pieces of text](https://developer.apple.com/documentation/naturallanguage/finding-similarities-between-pieces-of-text)
- [NLContextualEmbedding](https://developer.apple.com/documentation/naturallanguage/nlcontextualembedding)
- [NLContextualEmbeddingResult](https://developer.apple.com/documentation/naturallanguage/nlcontextualembeddingresult)
- [NLModel](https://developer.apple.com/documentation/naturallanguage/nlmodel)
- [NLModelConfiguration](https://developer.apple.com/documentation/naturallanguage/nlmodelconfiguration)
- [NLModel.ModelType](https://developer.apple.com/documentation/naturallanguage/nlmodel/modeltype)
- [Model Integration Samples](https://developer.apple.com/documentation/coreml/model-integration-samples)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
