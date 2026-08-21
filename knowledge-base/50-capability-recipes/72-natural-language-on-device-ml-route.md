# Natural Language on-device analysis route

Use this route for deterministic or reviewable text features that can run on device: segmentation, language identification, linguistic tags, semantic neighbors, contextual embeddings, and custom text models. Choose the smallest layer that solves the outcome.

## Route card

| Layer | Decision |
| --- | --- |
| User outcome | Search, tag, redact, classify, compare, or review text |
| Input | User-selected or app-owned text with source/retention policy |
| Language | Auto-detect, user-selected language, script, and supported-scheme check |
| Deterministic NLP | NLTokenizer, NLLanguageRecognizer, NLTagger |
| Similarity | NLEmbedding word/sentence vectors and domain vocabulary |
| Contextual features | NLContextualEmbedding with model/language/revision/asset lifecycle |
| Custom model | NLModel trained for text classification or word tagging |
| State | Unknown language, unsupported scheme, unavailable asset, no model, low coverage, user correction |
| AI | Optional local draft/proposal; keep source, label, vector, model result, and user truth separate |
| UI | Native SwiftUI text/selection/review controls; accessible highlights |
| Glass | Group language/model/asset/action controls; never hide source or uncertainty |
| Proof | Language/scheme, asset, revision, input length, evaluation, accessibility, privacy, performance, device, and release evidence |

## 1. Choose the narrowest layer

| Need | Use | Avoid |
| --- | --- | --- |
| Split sentences/words | NLTokenizer | Generative model for punctuation/segments |
| Identify likely language | NLLanguageRecognizer | Treating a short-text guess as certainty |
| Find lexical/entity/lemma tags | NLTagger | Saving a tag as an identity/medical/legal fact |
| Find similar saved terms | NLEmbedding | Treating distance as truth or intent |
| Sequence-aware features | NLContextualEmbedding | Hidden asset download or unsupported-language assumption |
| Custom label/tag | NLModel | Unreviewed external side effect from a label |

## 2. Define the text contract

Record:

- source text and owner;
- language/script selection;
- maximum input size;
- requested unit/scheme;
- model and revision;
- asset availability;
- whether tags/ranges/embeddings are retained;
- user correction path;
- export/network boundary.

If the input is a note, message, clinical record, financial document, or private transcript, add a redaction and retention review before the NLP layer.

## 3. Implement asset readiness

For NLTagger assets or contextual embedding assets:

1. check whether the language/scheme/model is supported;
2. show ready/requesting/unavailable/error state;
3. request assets only with a clear product action and network policy;
4. load only for the operation;
5. unload when memory policy requires;
6. use deterministic fallback or user review when assets are unavailable.

An asset being downloadable does not mean that the device is currently ready or that the app may claim offline operation.

## 4. Keep model output reviewable

The route should produce:

- original range/text;
- tag/label/vector match;
- language/model/revision;
- optional confidence/hypotheses;
- user correction;
- committed app state.

Do not use a Natural Language label to directly send, delete, purchase, diagnose, or disclose. Require validation and user confirmation for consequential actions.

## 5. Local-AI composition

Compose:

source text -> redaction/token/tag features -> optional embedding/classifier -> bounded prompt/draft -> user review -> app-owned result

Natural Language can reduce what a generative model sees:

- redact names or account identifiers;
- select sentences;
- identify language;
- classify document sections;
- retrieve local similar examples.

The reduction itself can be wrong. Keep an “original text available for review” route and do not silently discard content because a tagger missed it.

## 6. Native UI and Liquid Glass

Use TextEditor/Text, selection, accessibility annotations, inline highlights, and a review panel. Put model/language/asset state in a compact control area. Liquid Glass may group the controls, but the original text and uncertainty should sit on a stable readable surface.

Support Dynamic Type, VoiceOver, text selection, right-to-left, localization, high contrast, Reduce Motion, Voice Control, Switch Control, and keyboard/pointer navigation. Avoid color-only category highlights.

## 7. Failure states

Handle:

- empty input;
- short or mixed-language input;
- language unknown;
- language unsupported;
- tag scheme unavailable;
- tagger/tokenizer concurrent-use violation;
- model missing or wrong revision;
- contextual asset not available/download error;
- maximum sequence length;
- embedding vocabulary miss;
- classifier unknown label;
- low-confidence/false-positive review;
- offline mode;
- redacted input too small;
- privacy/export refusal.

## 8. Evidence bundle

- supported language and tag scheme table for the named SDK/device;
- tokenizer/tagger serial-use test;
- contextual asset availability/download/load/unload evidence;
- embedding revision/dimension/max-sequence evidence;
- custom model configuration/label fixtures;
- long/mixed/RTL/emoji/code text fixtures;
- redaction/deletion/logging review;
- local AI model and user-correction evidence;
- physical performance/memory/thermal run;
- accessibility/localization review;
- signed archive/release proof.

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
- [requestAssets(completionHandler:)](https://developer.apple.com/documentation/naturallanguage/nlcontextualembedding/requestassets%28completionhandler%3A%29)
- [load()](https://developer.apple.com/documentation/naturallanguage/nlcontextualembedding/load%28%29)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
