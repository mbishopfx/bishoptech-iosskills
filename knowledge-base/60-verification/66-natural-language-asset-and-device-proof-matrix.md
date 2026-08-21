# Natural Language asset, model, and device proof matrix

Natural Language proof must establish the language/scheme/model contract, asset state, serial-use lifecycle, input boundaries, and semantic fallback. A tag or vector is not a truth claim.

| Claim | Evidence | Failure fixture / boundary |
| --- | --- | --- |
| The framework is in the named target | Target compiles Natural Language imports with intended deployment | Source import or preview without target membership |
| The language is supported | Runtime/device table records NLLanguage/NLScript and supported tag schemes | SDK enum assumed to mean every language is supported |
| Tokenizer is deterministic for the fixture | Token unit, language, ranges, punctuation, emoji, RTL, and code fixtures are recorded | Arbitrary UTF-16 slicing or language-blind segmentation |
| Tagger configuration is valid | tag schemes, unit, language, and availableTagSchemes are recorded | Unsupported scheme silently labeled as known |
| Tagger/thread lifecycle is safe | Serial queue/actor test proves no concurrent instance use | One mutable NLTagger shared across tasks |
| Language recognition is qualified | Short, mixed, unknown, transliterated, and long text fixtures include fallback | Dominant-language guess treated as certainty |
| Built-in embedding is known | Language, revision, vector dimension, distance type, vocabulary, and neighbors are recorded | Distance shown as truth, intent, or identity |
| Custom embedding is controlled | Model file, source dictionary, language/revision, load/error, and delete evidence exist | Untracked embedding file or raw private text in diagnostics |
| Contextual assets are managed | hasAvailableAssets, requestAssets result, network/storage state, load/unload, and failure are tested | Offline/local claim when assets were never downloaded |
| Contextual model contract is visible | Model identifier, languages, scripts, revision, dimension, and maximumSequenceLength are recorded | English model assumed to support another language |
| Custom NLModel is the intended model | NLModelConfiguration type/language/revision and label contract are inspected | Classifier used as tagger or explanation engine |
| Long input is bounded | Maximum sequence/input policy and truncation/user-review behavior are tested | Silent truncation changes a decision |
| Redaction is reviewable | Original ranges, redacted result, false positives/negatives, and undo path are captured | Named-entity miss leaks private text |
| AI result is separate | Model output, confidence/coverage, user correction, and committed state are separate fixtures | Label directly sends/deletes/purchases/diagnoses |
| Privacy boundary holds | Logs/analytics/screenshots/export/network traces contain no raw text/embedding unless approved | “On device” claim with hidden telemetry |
| Accessibility works | VoiceOver reads source/tag/model/uncertainty; Dynamic Type, RTL, high contrast, Reduce Motion, keyboard, and Switch Control pass | Color-only highlight or inaccessible range |
| Performance is representative | Physical device records input length, memory, latency, thermal, and asset state | Newest-device Debug run generalized to all devices |
| Release proof exists | Signed target, model/asset packaging, archive, privacy review, and device/OS matrix | Preview, mock result, or downloaded asset treated as release proof |

## Fixture set

- empty and whitespace-only text;
- short/long/mixed/unknown language;
- punctuation, emoji, code, spelling variants, transliteration, and RTL;
- supported/unsupported tag scheme;
- tokenizer/tagger serial-use;
- tag ranges and false entity matches;
- embedding vocabulary miss, neighbor threshold, revision change;
- contextual asset available, not available, request error, download canceled, load/unload;
- model language/revision mismatch;
- custom classifier unknown label and word-tagger range;
- maximum sequence length;
- redaction, user correction, deletion, export refusal;
- local AI no-model/low-confidence/draft review;
- VoiceOver, Dynamic Type, localization, high contrast, Reduce Motion, offline, memory, and thermal states.

## Evidence ladder

1. Pure range/tag/label/state fixtures.
2. Target compile and asset/model inspection.
3. Simulator text/UI/performance fixtures where appropriate.
4. Physical-device language assets, memory/thermal, and offline/network evidence.
5. Human review/evaluation for representative languages and sensitive domains.
6. Accessibility, privacy, retention, and release review.
7. Signed archive/distribution evidence.

Record the target, SDK/OS, language/script, scheme, model identifier/revision, asset status, input length, output, correction, device, and remaining proof gaps. Do not store raw private test text when a redacted fixture is sufficient.

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
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
