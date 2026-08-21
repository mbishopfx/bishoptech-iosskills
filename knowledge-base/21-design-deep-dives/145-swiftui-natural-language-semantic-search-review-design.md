# SwiftUI Natural Language and local semantic-retrieval design

This design route turns local language analysis into a calm native app surface. It pairs with the [Natural Language review](../42-framework-deep-dives/117-swiftui-natural-language-semantic-search-review.md), the [implementation route](../50-capability-recipes/148-swiftui-natural-language-semantic-search-review-route.md), the [proof matrix](../60-verification/142-swiftui-natural-language-semantic-search-proof-matrix.md), and the [recipes](../70-code-recipes/160-swiftui-natural-language-semantic-search-review-recipes.md).

The design goal is not to make a person understand tokenizers, vectors, or model revisions. The goal is to help them find, understand, correct, and explicitly use a source-linked result.

## 1. Start with the human task

Choose one primary task:

- **Find** — locate related notes, documents, messages, or records;
- **Organize** — propose tags or categories for review;
- **Extract** — highlight names, places, topics, or custom spans;
- **Compare** — show similar text with source evidence;
- **Translate the query** — detect language and route to a supported local representation;
- **Inspect** — expose advanced model, language, and index details to a technical user.

The first screen should answer:

1. What source or collection is being searched?
2. What query is being used?
3. Is the result current, partial, or stale?
4. What evidence supports each candidate?
5. What can the person do next?

Avoid a dashboard of unexplained similarity percentages. A candidate is useful only when the person can understand and control it.

## 2. Native screen hierarchy

Recommended iPhone hierarchy:

1. navigation title and collection scope;
2. native search field or source picker;
3. small language/availability status;
4. result list with evidence excerpts;
5. one clear review action;
6. secondary filter, exact-search, retry, and settings actions.

Recommended iPad or Mac hierarchy:

- source/collection sidebar;
- query and filters in the main toolbar;
- candidate list in the primary column;
- source context or inspector in a secondary column;
- model/index diagnostics in an optional inspector.

Do not let the low-level route dictate the layout. The same state model should support a compact phone search, a split-view document browser, and a diagnostics inspector.

## 3. Candidate design

A candidate row should communicate:

| Element | Purpose |
| --- | --- |
| Title | Human-readable identity |
| Evidence | Text range or source excerpt that caused the match |
| Scope | Collection, document, date, or owner |
| Reason | Similar sentence, related phrase, classifier label, or extracted span |
| Freshness | Current, updating, partial, or stale |
| Action | Open source, review, edit, save, or discard |

Use a stable sort order while results stream or update. If ranking changes, tell the person that results were refreshed rather than moving rows invisibly under their finger or VoiceOver focus.

For semantic matches, show the source excerpt before the score. A numeric distance can be a secondary detail. If the app shows a score, label it as an app-specific similarity or ranking signal and disclose the embedding/model revision in advanced details.

## 4. Language and asset states

Language and model readiness should be visible without becoming the main visual:

| State | Copy direction | Action |
| --- | --- | --- |
| Detecting | “Checking the language…” | Cancel or wait |
| Supported | “English search ready” | Search |
| Ambiguous | “Language is unclear” | Choose language or search exact text |
| Preparing | “Preparing language data…” | Wait, cancel, or use exact search |
| Partial | “Some languages or sources are unavailable” | Narrow scope or continue |
| Unsupported | “Semantic search isn’t available for this language” | Use exact search or manual tagging |
| Stale | “Results changed because the source or index changed” | Refresh |
| Failed | “Couldn’t prepare local search” | Retry or use a deterministic fallback |

Never use a spinning glass control as the only indication of an unavailable language asset. A person should be able to reach an exact-search or manual path.

## 5. Search, filter, and review surfaces

Use native controls first:

- a searchable navigation title or search field for the query;
- a scope menu for collection, date, owner, or source type;
- a filter control for supported language, reviewed state, or exact/semantic mode;
- a button for refresh, cancel, and fallback;
- a sheet or inspector for advanced representation details.

Keep exact search and semantic search conceptually distinct. A segmented control can work when the product genuinely supports both, but the labels should describe user outcomes such as “Exact” and “Similar,” not internal choices such as “NLEmbedding” and “NLContextualEmbedding.”

When a person opens a candidate, anchor the source context to the matching range. Preserve the original text and show any normalized or chunked representation only in details.

## 6. Functional Liquid Glass

Liquid Glass can group:

- search and scope controls;
- a compact result-mode switcher;
- retry, refresh, and exact-search fallback;
- a small “local processing” status;
- an inspector toolbar.

Keep evidence excerpts, dense text, warnings, and privacy explanations on stable surfaces. Avoid nested translucent cards, decorative blur behind long passages, and continuously morphing result containers that interfere with reading or focus.

Glass should not imply:

- that processing is private merely because the surface is translucent;
- that a match is correct because it is highlighted;
- that a model is ready because a control is enabled;
- that a candidate is committed because it is displayed.

Use material to establish hierarchy and touch targets. Use typography, spacing, source context, and explicit actions to establish meaning.

## 7. Review before commit

For every generated tag, classification, or semantic candidate, design a review step:

    candidate -> evidence -> edit/confirm -> save or discard

The review screen should make it easy to:

- open the source;
- edit the proposed label or destination;
- see why the candidate was returned;
- see whether the result is partial or stale;
- reject the candidate without deleting the source;
- choose exact search or manual entry;
- undo a prior approval.

For high-impact actions, require a stronger confirmation that names the destination and side effect. Natural Language should never bypass a confirmation merely because a distance or label confidence exceeded a threshold.

## 8. Accessibility and alternate input

The accessibility task is not “read the similarity score.” It is:

1. enter or choose a query;
2. select the source scope;
3. understand language and availability;
4. start or cancel search;
5. move through candidates in stable order;
6. hear title, evidence, reason, and freshness;
7. open source context;
8. approve, edit, save, or discard.

Use semantic labels and values. Give a candidate a concise combined label such as “Meeting notes, similar sentence, source updated yesterday, review.” Expose the actual evidence as accessible text. Avoid relying on color, underline, blur, or a vector graphic to communicate a match.

Support:

- Dynamic Type without clipping evidence;
- VoiceOver focus that remains stable during updates;
- keyboard search, scope, and review actions;
- pointer and hover without hiding the source;
- Switch Control and Full Keyboard Access;
- reduced transparency and reduced motion;
- high contrast and long localized strings;
- right-to-left layouts and mixed scripts.

Do not announce every streamed candidate or token-level update. Announce meaningful result-set changes and make the list state queryable.

## 9. Empty, partial, and stale states

An empty result is not always “nothing is similar.” Distinguish:

- no source matches the current policy;
- the query is too short or ambiguous;
- the language is unsupported;
- assets are not ready;
- the collection is still indexing;
- the source was deleted or permission changed;
- the ranking threshold excluded all candidates.

Partial results need a visible explanation and a recovery action. Stale results need a source/index revision check and a refresh path. Do not show a stale candidate with a normal “Save” button if the destination has changed since ranking.

## 10. Privacy-first composition

The UI should clearly state, in product language:

- whether analysis occurs on device;
- whether raw text is retained;
- whether embeddings are stored;
- whether system indexing is enabled;
- whether diagnostics contain excerpts or identifiers;
- how to delete derived results and indexes;
- whether a shared or extension surface receives the data.

Avoid “private” as an unqualified badge. The app should match the badge to the actual data flow, including sync, export, analytics, model downloads, and system handoff.

For diagnostics, prefer metadata such as model revision, language, dimension, count, duration, and a redacted source ID. Do not show raw vectors or full private text by default.

## 11. Layout and localization

Long evidence excerpts need flexible layout. Use text that can wrap, grow, and scroll without making the action controls unreachable. Do not hard-code a fixed height for a candidate row based on English.

Test:

- English and a language without whitespace token boundaries;
- mixed-language text;
- Arabic/RTL;
- CJK;
- long words and URLs;
- punctuation, emoji, and diacritics;
- very large Dynamic Type;
- empty and one-character queries;
- narrow iPhone and wide iPad/Mac layouts.

Keep the original source range stable even when the displayed excerpt is localized or transformed. A translated explanation is not a replacement for the source evidence.

## 12. Interaction and motion

Use subtle transitions for:

- entering review;
- expanding source evidence;
- changing exact/semantic mode;
- refreshing the result set;
- revealing a stale or partial state.

Do not animate every score or candidate position. Reduce motion should preserve state comprehension. If a result changes while the person is reviewing it, show a clear update state and protect the review draft.

## 13. Advanced inspector

An inspector can expose:

- language and script;
- Natural Language model or embedding identifier;
- model/embedding revision;
- representation kind;
- vector dimension;
- sequence length or chunk policy;
- index revision and source count;
- measured duration and memory sample;
- whether the value is estimated, cached, or observed.

Use human-readable labels and a copy/export action for redacted evidence. Diagnostics are not the primary experience and should not be required to complete the core task.

## 14. Acceptance matrix

| Area | Acceptance question |
| --- | --- |
| Task | Can a person find, understand, and control a source-linked candidate? |
| Language | Is unsupported or ambiguous language honest and recoverable? |
| Evidence | Can the person see the source range behind the candidate? |
| Ranking | Is a distance or label presented as a signal, not truth? |
| Freshness | Are source, model, asset, and index revisions visible when relevant? |
| Review | Can the candidate be edited, approved, rejected, and undone? |
| Glass | Does material group controls without reducing text legibility? |
| Accessibility | Can assistive input complete the same task? |
| Privacy | Does the UI match actual retention, indexing, sync, and logging? |
| Fallback | Is exact search or manual input available when local assets fail? |
| Release | Does the signed build reproduce the language, asset, and index contract? |

### Stop conditions

- A result card hides its source excerpt or revision.
- A glass effect substitutes for an availability, privacy, or review explanation.
- A candidate can trigger a durable or external action without explicit approval.
- Dynamic Type, RTL, VoiceOver, keyboard, or reduced-effects paths are treated as optional.
- The interface claims “AI understands” when the actual route is a distance, tag, or classifier hypothesis.

## Sources

- [Natural Language](https://developer.apple.com/documentation/naturallanguage)
- [NLLanguageRecognizer](https://developer.apple.com/documentation/naturallanguage/nllanguagerecognizer)
- [NLTokenizer](https://developer.apple.com/documentation/naturallanguage/nltokenizer)
- [NLTagger](https://developer.apple.com/documentation/naturallanguage/nltagger)
- [NLEmbedding](https://developer.apple.com/documentation/naturallanguage/nlembedding)
- [NLContextualEmbedding](https://developer.apple.com/documentation/naturallanguage/nlcontextualembedding)
- [NLModel](https://developer.apple.com/documentation/naturallanguage/nlmodel)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
