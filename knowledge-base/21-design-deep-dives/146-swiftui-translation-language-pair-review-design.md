# SwiftUI Translation and language-pair design

This design route makes local translation feel like a native, reviewable transformation. It pairs with the [Translation review](../42-framework-deep-dives/118-swiftui-translation-language-pair-review.md), the [implementation route](../50-capability-recipes/149-swiftui-translation-language-pair-review-route.md), the [proof matrix](../60-verification/143-swiftui-translation-language-pair-proof-matrix.md), and the [recipes](../70-code-recipes/161-swiftui-translation-language-pair-review-recipes.md).

Translation should preserve the relationship between original and translated text. The person should know the source language, target language, readiness, strategy, and next action without needing to understand Apple’s model stack.

## 1. Choose the experience

Use one of these task shapes:

- **Quick translate** — show system translation UI for selected text;
- **Read in another language** — present source and translated text together;
- **Draft** — translate user-authored text before editing or sending;
- **Batch** — translate titles, captions, or rows with stable progress;
- **Review** — compare source and target before saving or replacing;
- **Provider** — offer a separate selected-text extension as the default translation app.

The screen should answer:

1. What text is being translated?
2. From which language?
3. Into which language?
4. Are the languages installed and ready?
5. Is this fast, higher-fidelity, partial, or awaiting download?
6. What can the person do with the candidate?

## 2. Native hierarchy

Recommended phone hierarchy:

1. navigation title and source context;
2. source text with language label;
3. target language control;
4. readiness/strategy status;
5. translated candidate;
6. edit, copy, save, share, replace, retry, and discard actions.

Recommended iPad/Mac hierarchy:

- source/document sidebar;
- source and target language controls in the toolbar;
- source and translated text in a split editor;
- readiness/download status in a secondary inspector;
- review and destination controls at the bottom of the target pane.

Keep the same domain state across layouts. Do not make the Mac inspector the only place where the source language or download status is explained.

## 3. Source and target pairing

Represent the pair as a visible object:

    [source language] -> [target language]

Use language names, not only locale identifiers. If source is automatic, say “Detect source language” and show an ambiguity state when the framework cannot identify it. If target is automatic, show the actual response target before the person saves or shares.

When the person changes either language:

- preserve the original source;
- cancel or invalidate the old session;
- clear or mark the old target stale;
- re-check availability;
- avoid showing a prior translation under a new language label.

## 4. Readiness states

Use an honest state language:

| State | Visual treatment | Action |
| --- | --- | --- |
| Checking | Quiet progress near the language pair | Wait or cancel |
| Installed | Ready status | Translate |
| Supported | Download/prepare action | Approve download or use fallback |
| Unsupported | Clear unavailable treatment | Choose another pair or show original |
| Ambiguous | Source-language prompt | Choose source |
| Downloading | Progress and cancel | Continue or cancel |
| Translating | Indeterminate/progressive state | Cancel |
| Partial | Completed rows plus remaining state | Continue, retry, or review partial |
| Complete | Target text plus provenance | Edit, save, share, or discard |
| Failed | Actionable error | Retry, lower-latency, or manual |

Do not disable the entire source view while language resources download. Let the person read, copy, cancel, or use an exact/manual path.

## 5. Functional Liquid Glass

Liquid Glass is useful for:

- source/target language controls;
- translate/retry/cancel actions;
- a compact readiness capsule;
- batch progress controls;
- a toolbar for source/target swapping where supported.

Keep long source and target text on stable backgrounds. Dense translated content, links, code, names, and warnings need legibility and selection. Avoid putting every paragraph inside a translucent card or using glass as a signal of translation accuracy.

The main action should remain a standard semantic Button. A glass style can group it with adjacent controls, but it should not change the meaning of the action or hide the fact that saving replaces content.

## 6. Reviewable translation

Use a two-pane or before/after review:

| Source | Translation |
| --- | --- |
| Original text and language | Editable candidate and actual target language |
| Source link/range | Translation strategy/readiness |
| Original formatting | Preserved formatting where supported |
| Source revision | Candidate revision and stale state |

For a draft, the person should be able to edit the translated text before the app saves or sends it. For a document replacement, name the destination and provide undo. For a message, make the send action distinct from translation.

Translation can change terminology, tone, ambiguity, and meaning. Show warnings for names, identifiers, URLs, legal/medical/business terms, or content that has an app-specific glossary policy. A warning should explain the action, not make a universal quality claim.

## 7. Single versus batch presentation

Single translation:

- show source and target together;
- use a clear progress state;
- keep the original visible during errors;
- place copy/save/share below the review surface.

Incremental batch:

- use stable row identity;
- show translated rows as they complete;
- display a partial state while rows remain;
- let the person cancel without losing source data;
- map each response to its source row;
- do not move VoiceOver focus when a neighboring row completes.

All-at-once batch:

- show preparation and indeterminate progress;
- reveal the target set only when the complete result is ready;
- preserve source ordering;
- explain a failed or cancelled operation without showing a misleading empty list.

## 8. Accessibility and localization

The task should be possible with:

1. VoiceOver;
2. Dynamic Type;
3. keyboard and Full Keyboard Access;
4. pointer;
5. Switch Control;
6. reduced motion and reduced transparency;
7. right-to-left layout;
8. long localized language names.

Give the language pair a combined accessible value such as “English to Spanish, installed.” Give each source/target region a heading. Do not announce every batch row update; announce “three of ten translations ready” or “translation complete.”

Keep the UI locale separate from the content language. A Spanish translation does not require Spanish controls, and English controls do not justify hiding an Arabic or Japanese source. Test mixed-script text, attributed links, punctuation, line breaks, and large text.

## 9. Error and fallback design

Fallback actions should be explicit:

- choose a supported pair;
- request language resources;
- choose a source language;
- use fast translation;
- show original text;
- copy source;
- enter a manual translation;
- retry.

Do not label an empty target as “no translation.” Say whether the operation failed, was cancelled, is waiting for resources, or produced no usable output under the current policy.

If high-fidelity is unavailable, preserve the person’s choice and state that the app is using the available strategy. Never silently imply that a low-latency result has the same quality or model path.

## 10. Privacy and provenance copy

Use short, accurate copy:

- “Translation is processed on this device.”
- “Language resources may need to download.”
- “Apple may collect API usage and performance metrics such as app and language metadata; the source and translated text are not included in that documented metric collection.”
- “Your app stores the original and translated draft according to its privacy settings.”

The final sentence belongs to the app and must match its actual storage, sync, export, logging, and system-provider behavior. Do not display a generic “private” badge if a custom provider sends text to a network service.

## 11. Provider extension design

TranslationUIProvider is a separate system-surface route:

- the extension receives selected-text context;
- the extension can provide its own UI;
- replacement may be allowed or disallowed by the context;
- a default translation app requires an entitlement and target configuration;
- network access is a separately declared provider concern.

Design the provider with a compact selected-text view, a visible translate action, an accessible target result, and a replacement action that is disabled when the context does not allow replacement. Keep provider source handling separate from the app’s in-process TranslationSession state.

## 12. Motion and focus

Animate:

- language-pair changes;
- the arrival of a target candidate;
- expansion from source to review;
- a partial batch count.

Do not animate text in a way that makes reading difficult or causes VoiceOver focus to jump. When source/target changes, move focus to the language/readiness status or the new target heading intentionally.

Respect reduced motion. A progress indicator can become a static status with an accessible value; a completion transition can become a simple content update.

## 13. Acceptance matrix

| Area | Acceptance question |
| --- | --- |
| Source | Can the person always return to or copy the original? |
| Pair | Are source and target names, actual response languages, and changes clear? |
| Readiness | Are installed, supported, and unsupported states distinct? |
| Strategy | Is fast/high-fidelity/fallback language accurate? |
| Session | Does a view/configuration change invalidate stale work safely? |
| Batch | Are rows stable, mapped, cancellable, and partial-aware? |
| Review | Can the person edit before save/replace/send? |
| Glass | Does material group controls without compromising text? |
| Accessibility | Can assistive input complete the task? |
| Privacy | Does copy match the actual local/provider/storage path? |
| Fallback | Is original/manual/exact behavior reachable? |
| Release | Does the signed build reproduce the language and asset state? |

### Stop conditions

- The target text is shown without the source or actual target language.
- Download and unsupported states look identical.
- A translation result becomes a durable side effect without review.
- A batch list has no stable response-to-source identity.
- Glass, animation, or a quality label hides a stale or partial state.
- Accessibility and RTL are deferred because translation “only changes text.”

## Sources

- [Translation](https://developer.apple.com/documentation/translation)
- [LanguageAvailability](https://developer.apple.com/documentation/translation/languageavailability)
- [TranslationSession](https://developer.apple.com/documentation/translation/translationsession)
- [TranslationSession.Configuration](https://developer.apple.com/documentation/translation/translationsession/configuration)
- [TranslationSession.Strategy](https://developer.apple.com/documentation/translation/translationsession/strategy)
- [TranslationSession.Response](https://developer.apple.com/documentation/translation/translationsession/response)
- [TranslationUIProvider](https://developer.apple.com/documentation/translationuiprovider)
- [Preparing your app to be the default translation app](https://developer.apple.com/documentation/translationuiprovider/preparing-your-app-to-be-the-default-translation-app)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
