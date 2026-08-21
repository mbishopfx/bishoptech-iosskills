# Natural Language: on-device linguistic analysis and model assets

Natural Language provides language-specific text analysis: tokenization, language identification, linguistic tagging, word/sentence embeddings, contextual embeddings, and custom Create ML natural-language models. It is a useful lower-level layer for private text features, but its tags, vectors, and classifications are not automatically correct interpretations of a person or document.

Use the framework as a staged pipeline:

input text -> language/script policy -> tokenization/tagging -> optional embedding/model -> confidence/coverage -> user review or deterministic product action

Keep source text, redacted features, model revision, language, asset state, generated result, and user-approved side effect separate.

## 1. Tokenization is not generation

NLTokenizer segments text into words, sentences, paragraphs, or documents. It uses an NLTokenUnit and can set a language. NLTagger can annotate units with token type, lexical class, name, lemma, language, and script schemes. NLLanguageRecognizer detects likely language information.

These operations can be the right route for:

- sentence and paragraph splitting;
- search indexing;
- language-aware editor features;
- named-entity review;
- vocabulary and lexical-class highlighting;
- deterministic redaction before a model sees text.

They do not write a summary, infer intent with certainty, or prove that a recognized name is a real person. Preserve the original range and tag scheme beside any redacted/derived output.

NLTokenizer and NLTagger instances should not be used simultaneously from multiple threads. Create one instance per serial execution context or isolate it behind an actor/queue.

## 2. Tag schemes and language support are runtime facts

Ask the current device which tag schemes are available for the unit and language. A tag scheme that exists in the SDK may not be supported for every language, script, revision, or OS.

Relevant schemes include:

- tokenType;
- lexicalClass;
- nameType;
- nameTypeOrLexicalClass;
- lemma;
- language;
- script.

Use availableTagSchemes(for:language:) before configuring a feature that requires a particular analysis. A fallback such as plain tokenization, user correction, or manual review is better than labeling unsupported text as known.

Language identification should remain probabilistic. Model unknown, mixed-language, short-text, code-switching, emoji, transliteration, and confidence thresholds explicitly.

## 3. Built-in embeddings are vector tools

NLEmbedding maps vocabulary strings to vectors and exposes distance/neighborhood operations. Apple provides word and sentence embeddings for supported languages and revisions; custom embeddings can be compiled from Create ML or written from a dictionary.

An embedding route can support:

- nearest-neighbor lookup;
- local semantic search over an app-owned vocabulary;
- duplicate/near-duplicate hints;
- category prototypes;
- clustering before a human review.

Embedding distance is not a truth score, safety score, or authorization. The vocabulary, language, revision, normalization, and distance type affect the result. Keep the model revision and source corpus in the feature record.

## 4. Contextual embeddings have an asset lifecycle

NLContextualEmbedding produces sequences of embedding vectors for utterances. A model may support one or more languages and has a model identifier, revision, dimension, maximum sequence length, scripts, and language list.

Before computing:

1. choose an embedding model appropriate for the target language;
2. inspect languages, revision, dimension, and maximumSequenceLength;
3. check hasAvailableAssets;
4. call requestAssets() when assets are missing and the product permits an asset request;
5. handle available, notAvailable, and error results;
6. call load();
7. compute embeddingResult(for:language:);
8. unload when the memory policy requires it.

Apple documents that contextual embedding assets can be downloaded over the air. An app should show a model-ready/download/unavailable state and not claim that a local analysis happened when the assets were never present. Asset download is a separate network/data-retention event from the embedding computation.

Do not assume that English and Chinese, or any other language pair, share one model asset. Read languages and model identifier on the current device.

## 5. Custom Natural Language models

Natural Language can load a custom NLModel trained for text classification or word tagging. NLModelConfiguration describes model type, language, and framework revision. The app should inspect the model configuration and supported revision instead of treating a compiled model file as a universal classifier.

For a custom model:

- identify the training label contract;
- keep language and revision metadata;
- handle model load/prediction errors;
- preserve a no-model/unknown-label fallback;
- validate against representative text, spelling, dialect, code-switching, and adversarial input;
- show user correction when the classification affects a visible or external action.

Word tagging and text classification have different output semantics. Do not use a text classifier as if it returned an explanation, and do not use a tagger’s ranges as a medical, legal, or identity conclusion.

## 6. Privacy boundary

Natural Language runs on input supplied by the app, but the app controls what text it stores, logs, exports, or sends elsewhere. Redact before analytics and before a remote model boundary. Named-entity tagging can itself reveal sensitive people, places, organizations, or account details.

For private local AI:

- keep source text on device unless export is explicit;
- store only derived ranges/features when possible;
- do not log tag hypotheses or embeddings with raw text;
- keep asset download and model revision visible;
- allow deletion of source and derived caches;
- make “local” mean local computation, not necessarily no asset download.

## 7. Swift concurrency and memory

Natural Language objects are Objective-C reference types with documented thread-use constraints. Isolate a tokenizer/tagger/embedding/model instance behind an actor or serial queue. Bound input length before tokenization or contextual embedding; truncate by language-aware units rather than arbitrary UTF-16 offsets when possible.

Contextual embeddings can be memory-intensive. Load only for the operation, cap sequence length, unload, and provide a deterministic fallback. Do not run one global mutable tagger across concurrent document tasks.

## 8. Native design and Liquid Glass

Use native SwiftUI text, selection, labels, and review controls. Liquid Glass can group:

- detected language and model revision;
- highlighted entity/tag ranges;
- “keep original” and “apply” actions;
- asset readiness and offline state;
- user corrections and privacy/export controls.

Do not use translucent material to hide uncertain text classifications. Keep the original text visible or recoverable, distinguish suggested highlights from committed edits, and expose the model/asset state in accessible text. Respect Dynamic Type, text selection, VoiceOver, reduced motion, high contrast, localization, and right-to-left layout.

## 9. Evidence boundaries

Prove separately:

1. supported language/tag scheme on the selected OS/device;
2. tokenizer/tagger serial-use behavior;
3. asset availability, download, failure, load, and unload;
4. embedding revision/dimension/maximum sequence length;
5. custom model configuration and label behavior;
6. local redaction and deletion;
7. low-confidence, unknown, mixed-language, and long-input fallback;
8. accessibility and localization;
9. signed target, physical-device performance, and release artifact.

A tag, vector, model label, downloaded asset, or preview does not prove truth, intent, privacy compliance, or release readiness.

## Sources

- [Natural Language](https://developer.apple.com/documentation/naturallanguage)
- [NLTokenizer](https://developer.apple.com/documentation/naturallanguage/nltokenizer)
- [NLTagger](https://developer.apple.com/documentation/naturallanguage/nltagger)
- [NLTag](https://developer.apple.com/documentation/naturallanguage/nltag)
- [NLLanguageRecognizer](https://developer.apple.com/documentation/naturallanguage/nllanguagerecognizer)
- [NLLanguage](https://developer.apple.com/documentation/naturallanguage/nllanguage)
- [NLEmbedding](https://developer.apple.com/documentation/naturallanguage/nlembedding)
- [NLContextualEmbedding](https://developer.apple.com/documentation/naturallanguage/nlcontextualembedding)
- [NLContextualEmbedding.AssetsResult](https://developer.apple.com/documentation/naturallanguage/nlcontextualembedding/assetsresult)
- [NLModel](https://developer.apple.com/documentation/naturallanguage/nlmodel)
- [NLModelConfiguration](https://developer.apple.com/documentation/naturallanguage/nlmodelconfiguration)
- [NLModelConfiguration.type](https://developer.apple.com/documentation/naturallanguage/nlmodelconfiguration/type)
- [requestAssets(completionHandler:)](https://developer.apple.com/documentation/naturallanguage/nlcontextualembedding/requestassets%28completionhandler%3A%29)
- [load()](https://developer.apple.com/documentation/naturallanguage/nlcontextualembedding/load%28%29)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
