# Natural Language review and local-AI design

Natural Language features should feel like careful assistance, not an invisible oracle. A tag, language guess, embedding distance, or custom model label is a proposal or structured observation with a specific scope.

Use this design chain:

original text -> language/asset state -> visible analysis -> user review -> committed app state -> optional AI explanation or action

## 1. Show the source text and the derived layer

For tagging, entity recognition, or classification, preserve a visible relationship between source and result:

- highlight ranges without replacing the original;
- show the scheme, language, and model/revision;
- distinguish a suggestion from a committed tag;
- let the user correct or remove a label;
- show “unknown” or “not available” instead of silently hiding a miss.

Do not style a model label like a system fact if it is an inference. Avoid a green checkmark for an entity tag or language guess. The original text should remain accessible, selectable, and recoverable.

## 2. Language selection should be explicit when it affects meaning

Language identification can be uncertain for short text, mixed language, names, code, emoji, transliteration, and dialect. Use a small language/status control:

- detected language;
- selected language;
- auto versus manual mode;
- supported/unsupported analysis;
- confidence or “needs review”;
- model asset readiness.

When the user selects a language, do not overwrite the source language metadata without recording that the choice was user-provided. When the device does not support the requested tag scheme, fall back to plain text or tokenization.

## 3. Embeddings need human-readable semantics

An embedding distance has no universal meaning. If the app shows “similar,” explain the comparison set:

- similar to which saved phrases or categories;
- using which language/revision;
- within which date or document scope;
- with what threshold;
- what happens when there are no neighbors.

For a private semantic search feature, let the user inspect the matched source. Do not use vector proximity to assert that two people, diagnoses, legal clauses, or intentions are identical.

## 4. Contextual-embedding assets are part of onboarding

If a feature needs an over-the-air contextual embedding asset, make that state visible:

- “Model asset ready on this device”;
- “Download required” with network/storage explanation;
- “Not available for this language/device”;
- “Offline fallback: basic tokenization”;
- “Remove downloaded asset” if the product owns the cache.

Do not trigger a hidden multi-megabyte download when the person is merely opening a text editor. Ask at the moment the feature is enabled, and provide an offline route when reasonable.

## 5. Custom classifiers need a correction loop

For a Create ML text classifier:

1. display the label and source span/text;
2. provide “correct” or “not useful”;
3. persist only the user-approved app state;
4. keep model output separate from user truth;
5. offer a way to disable the classifier for sensitive documents.

If a classification controls an external action, require a distinct confirmation. Do not let a low-confidence or unknown label directly send a message, file a record, change a purchase, or create a medical/legal claim.

## 6. Liquid Glass as an analysis container

Liquid Glass can group the analysis controls without making the analysis look authoritative:

- model/language chip;
- asset state;
- range/highlight toggle;
- apply/revert;
- correction and privacy actions.

Keep the source text on a stable readable surface. Avoid animated blur behind dense text, translucent labels with low contrast, or moving highlights that are difficult to follow with Reduce Motion. A glass button should have a semantic label and a visible selected state.

## 7. Local AI copy

Useful copy:

- “Suggested language: Spanish. Change it if that looks wrong.”
- “These names were detected on this device. Review before saving.”
- “Similar phrases are shown from your selected local collection.”
- “The language model asset is unavailable offline. Basic search is still available.”
- “This draft is generated from the selected text. Review before applying.”

Avoid:

- “We understand what you mean.”
- “This is definitely the person/place.”
- “AI knows the right category.”
- “Your text is private” when assets download or the app exports text;
- “The result is accurate” without a measured evaluation boundary.

## 8. Accessibility and language inclusion

Test:

- VoiceOver reads original text, annotation, confidence/availability, and correction action in order;
- Dynamic Type does not turn highlights into unreadable overlaps;
- Voice Control can select/apply/revert;
- keyboard and pointer can navigate long text;
- right-to-left layout preserves ranges and controls;
- localization does not alter the underlying source ranges;
- reduced motion removes animated token/highlight transitions;
- high contrast preserves label and source distinction.

Do not rely on color alone for entity categories, confidence, or language state. Use text, shape, underline, or a detail panel.

## 9. Privacy and retention

Named-entity results can be personal data. Embeddings can be sensitive even without the source text. Define:

- whether original text is stored;
- whether tags/ranges are stored;
- whether embeddings are cached;
- model asset location and deletion;
- analytics redaction;
- export/share behavior;
- user deletion and app uninstall expectations.

For private AI, local computation is a meaningful boundary, but not a complete privacy claim. An app can still leak input through logs, screenshots, pasteboards, network asset downloads, widgets, or exports.

## 10. Proof before polish

Create deterministic fixtures for:

- short/mixed/unknown language;
- unsupported tag scheme;
- names/places/organizations with false positives;
- punctuation, emoji, code, and right-to-left text;
- long input and maximum sequence length;
- missing/downloaded/failed contextual assets;
- embedding revision changes;
- custom classifier unknown label and user correction;
- model unavailable/offline;
- source deletion and redacted analytics.

Visual polish can be validated in previews. Language support, model assets, performance, privacy, and semantic accuracy require device/asset/evaluation evidence.

## Sources

- [Natural Language](https://developer.apple.com/documentation/naturallanguage)
- [NLTokenizer](https://developer.apple.com/documentation/naturallanguage/nltokenizer)
- [NLTagger](https://developer.apple.com/documentation/naturallanguage/nltagger)
- [NLEmbedding](https://developer.apple.com/documentation/naturallanguage/nlembedding)
- [NLContextualEmbedding](https://developer.apple.com/documentation/naturallanguage/nlcontextualembedding)
- [NLContextualEmbedding.AssetsResult](https://developer.apple.com/documentation/naturallanguage/nlcontextualembedding/assetsresult)
- [NLModel](https://developer.apple.com/documentation/naturallanguage/nlmodel)
- [NLModelConfiguration](https://developer.apple.com/documentation/naturallanguage/nlmodelconfiguration)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
