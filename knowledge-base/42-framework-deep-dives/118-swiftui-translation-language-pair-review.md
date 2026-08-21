# SwiftUI Translation and language-pair review

This review covers Apple’s Translation framework as a native iOS 26 route for on-device translation: language-pair availability, installed versus supported assets, TranslationSession ownership, SwiftUI translationTask lifecycles, single and formatted text, incremental and all-at-once batches, translation strategy, source/target provenance, and optional TranslationUIProvider system integration. It pairs with the [Translation design](../21-design-deep-dives/146-swiftui-translation-language-pair-review-design.md), the [implementation route](../50-capability-recipes/149-swiftui-translation-language-pair-review-route.md), the [proof matrix](../60-verification/143-swiftui-translation-language-pair-proof-matrix.md), and the [code recipes](../70-code-recipes/161-swiftui-translation-language-pair-review-recipes.md).

Translation is a transformation of source content, not a replacement for source meaning. Preserve the original, show the language pair and strategy when they matter, and require an app-owned review before the translated text becomes a durable record, sends a message, changes a document, or triggers a side effect.

## 1. Choose the translation surface

| Product need | First route | Owns | Does not prove |
| --- | --- | --- | --- |
| Let a person translate selected text with system UI | translationPresentation | System translation popover and replacement handoff | That the app controls model choice or every translated phrase |
| Translate one or more app-owned strings in a SwiftUI screen | translationTask with TranslationSession | View-scoped session, source/target configuration, and response state | That a session remains valid after view/configuration changes |
| Re-run translation when app content changes | TranslationSession.Configuration plus translationTask | Configuration state and invalidate() lifecycle | That old responses match new source content |
| Translate in a non-UI service | TranslationSession(installedSource:target:) | Installed language pair and direct session | That missing languages can be downloaded through this initializer |
| Translate many same-language strings incrementally | translate(batch:) and BatchResponse | Client identifiers and AsyncSequence response order | That results are complete when the first item arrives |
| Translate many strings all at once | translations(from:) | Complete response array after the batch finishes | Progress or partial results while work is in flight |
| Choose a supported language pair and readiness state | LanguageAvailability | Supported languages and installed/supported/unsupported status | Translation quality or source semantic fidelity |
| Become the device’s default translation app | TranslationUIProvider extension | System text-selection provider surface, entitlement, and extension UI | The app’s own TranslationSession behavior or network privacy |

Start with system UI when the product only needs a person to translate selected text. Use a custom session when the app owns the source, destination, review, and persistence. Treat default-provider work as a separate extension and entitlement project.

## 2. Model availability as a language-pair state

LanguageAvailability exposes:

- supported languages;
- a preferred strategy;
- status for an explicit source and target Locale.Language;
- status inferred from a sample string when the source language is unknown.

The status has three important meanings:

| Status | Product meaning |
| --- | --- |
| installed | The framework supports the pair and the required language resources are downloaded and ready |
| supported | The framework supports the pair but cannot translate with it yet; language resources or readiness work remains |
| unsupported | The framework does not support the requested pair |

Do not collapse supported and installed into one Boolean. The UI and route should distinguish:

    unsupported -> exact/original/manual fallback
    supported -> ask permission or prepare/download
    installed -> create session and translate

When the source is unknown, LanguageAvailability.status(for:to:) can inspect a sample string and attempt to identify its language. Apple’s documentation recommends a sample of at least 20 characters for best automatic language-detection results. A short, mixed, or ambiguous string needs a user language choice or a deterministic fallback.

Use Locale.Language values returned by supportedLanguages when possible. Record the requested, matched, and actual response languages because the framework may choose a target when the configuration target is nil.

## 3. Translation strategy is an explicit product choice

TranslationSession.Strategy includes:

- highFidelity, which provides more fluent translations using Apple Intelligence when available and falls back to traditional models when those models are unavailable;
- lowLatency, which uses traditional models and is intended for fast translation across supported devices.

LanguageAvailability.preferredStrategy affects the status check. A pair can be available for low-latency translation but not available in the same way for a high-fidelity model. The strategy is not a guarantee that a particular hardware block or model revision will be used.

Expose user-facing language such as:

- “Fast translation”;
- “Higher-fidelity translation when available”;
- “Using the available on-device model”;
- “Language resources need to be downloaded.”

Do not promise “Apple Intelligence translation” merely because highFidelity was requested. Record the requested strategy, actual response behavior where exposed, device/OS, and fallback state for evaluation.

## 4. SwiftUI TranslationSession lifetime

SwiftUI can attach a translation task using source and target languages, or a TranslationSession.Configuration. The action receives a session and can perform one or more translations.

The lifecycle boundary is strict:

- the task runs when the view appears or its source/target/configuration changes;
- changing source or target cancels the prior work and creates a new session;
- a Configuration can be invalidated to rerun with new content and the same language pair;
- a session must not be used after the attached view disappears or after its source/target parameters change.

Treat the session as borrowed by the action closure. Do not store it in a long-lived service, pass it to an unrelated view, or use it after the task’s configuration has been replaced. If a service needs a session, use the direct installed-source initializer and own the full lifecycle in that service.

A safe state boundary is:

    view/configuration generation
        -> session action
        -> response tagged with source revision
        -> publish only if view/configuration/source still match

## 5. TranslationSession.Configuration is mutable intent

Configuration holds source and target languages and a preferred strategy. Its version changes when its meaningful configuration changes. Calling invalidate() asks the attached translation task to rerun with new content without changing the pair.

Use Configuration when:

- a view has a stable language pair;
- source content changes over time;
- the person can change source or target;
- the app wants a button to refresh the translation;
- the app needs a state-driven SwiftUI route.

Keep source content separate from Configuration. A configuration does not automatically prove that a response belongs to the latest source string. Store source text or a content digest beside the task generation and validate it before publishing or saving.

## 6. Direct sessions are installed-only

TranslationSession(installedSource:target:) is appropriate when:

- there is no SwiftUI view to own a translation task;
- the app already established that the source/target pair is installed;
- a service needs to translate a bounded set of strings;
- the app wants to avoid a system download prompt inside a background operation.

This initializer throws when the required languages are not already installed. Do not use it as the first availability check. Ask LanguageAvailability for status, prepare/download through a user-visible flow when appropriate, and show an exact/manual fallback when the pair is not ready.

For a user-facing SwiftUI session, the framework can request permission to download languages while translation is attempted. The app must treat download consent, progress dismissal, and user cancellation as visible states. A cancelled download can continue in the background even though the current request failed.

## 7. Single and formatted translation

TranslationSession can translate a String or an AttributedString. The formatted route can preserve formatting and links in the returned attributed text. Keep the source AttributedString and translated AttributedString separate.

For every response, retain:

- original source text or attributed content;
- translated target text or attributed content;
- sourceLanguage;
- targetLanguage;
- clientIdentifier when used;
- source record ID and revision;
- requested and actual strategy;
- timestamp and freshness;
- whether the person reviewed or edited the result.

A response’s sourceText is useful for checking what the framework actually translated. Do not replace a document’s source content in place merely because targetText is non-empty. Save translated content as a candidate or separate representation until the product’s review policy approves it.

## 8. Batch translation

Use TranslationSession.Request with a clientIdentifier when translating multiple strings. The strings in one session must follow the session’s source-language contract. Keep requests in the same language and maintain the client ID-to-source record mapping.

There are two different batch routes:

| Route | Behavior | Use when |
| --- | --- | --- |
| translate(batch:) | Returns a BatchResponse AsyncSequence as responses become available | A list can update incrementally and each row has a stable client ID |
| translations(from:) | Returns all responses after the operation completes | The app needs an atomic result set before showing or committing the group |

Incremental results require:

- stable row identity;
- a partial state;
- a cancellation path;
- source revision checks;
- deterministic response-to-request mapping;
- a final/complete state;
- behavior when one request fails or the session is cancelled.

Do not interpret the first response as proof that the entire batch is ready. Do not commit every incremental response to a persistent store unless the app defines idempotency, rollback, and source-revision behavior.

## 9. Cancellation and errors

TranslationSession.cancel() attempts to stop ongoing work. Swift concurrency cancellation should also stop publication and release app-owned request state. A session that has already been cancelled can reject later translation calls.

Map errors into product states:

| Error condition | UI route |
| --- | --- |
| unsupported pair | Original text plus exact/manual fallback |
| unable to identify source | Language picker or explicit source choice |
| missing resources | Prepare/download flow |
| download denied or dismissed | Explain that translation was not completed; offer retry/fallback |
| session invalidation | Create a new session through the current view/configuration |
| cancelled by person | Preserve source and draft; do not show a false translation |
| system validation or runtime failure | Retry, lower-latency strategy, or manual path |

Never convert an error to an empty target string. An empty translation and a failed translation are different states.

## 10. Locale and provenance

A translation candidate should include:

    sourceRecordID
    sourceRevision
    sourceTextDigest
    requestedSourceLanguage
    detectedSourceLanguage
    requestedTargetLanguage
    responseSourceLanguage
    responseTargetLanguage
    requestedStrategy
    availabilityStatus
    translationSessionGeneration
    reviewed

Use the response’s sourceLanguage and targetLanguage for the actual translation. If target is nil and the framework chooses based on the person’s preferred languages, present that actual target to the person before saving or sharing.

Translation can change tone, ambiguity, formatting, names, units, legal meaning, or product terminology. Preserve names, identifiers, URLs, code, and domain-specific terms according to an app-owned policy. Validate a translation against the destination’s constraints before commit.

## 11. SwiftUI and Liquid Glass

The screen hierarchy should be:

1. source text and source language;
2. target language picker;
3. readiness/strategy state;
4. translated candidate;
5. review/edit controls;
6. save, replace, share, or discard destination.

Use Liquid Glass for compact functional controls such as language-pair selection, translate/retry, and a small readiness capsule. Keep source and translated text on readable stable surfaces. Do not make a glass effect the only explanation of a download, partial batch, source ambiguity, or review requirement.

For a translation editor, show source and target as paired blocks or a clear before/after flow. Keep the original available while the translated candidate is edited. If a translated phrase has uncertain domain meaning, show a note or terminology warning rather than a decorative confidence number.

## 12. Accessibility and localization

The translation task must support:

1. selecting source and target languages;
2. understanding installed/supported/unsupported state;
3. starting, cancelling, and retrying;
4. reading source and target text;
5. identifying partial or stale results;
6. editing and approving the target;
7. saving, replacing, sharing, or discarding.

Use semantic labels for language controls and avoid exposing only language codes. Preserve VoiceOver reading order between source, target, and actions. Dynamic Type, long language names, right-to-left text, mixed scripts, and large attributed text are part of the layout contract.

Translation does not automatically make the surrounding UI localized. Keep control labels, warnings, dates, numbers, units, and error messages in the app’s UI locale while presenting the source and target content accurately.

## 13. Privacy and system provider boundaries

Apple’s TranslationSession documentation says translations are processed on the user’s device and that Apple may collect API usage/performance metrics such as bundle ID and original/translated language, not the original or translated content. Use that statement accurately: it does not describe every data path in a custom translation provider, network service, logging layer, export, sync route, or system index.

For the built-in route:

- avoid logging source or target text;
- document model/language download behavior;
- disclose that the person may be asked for download permission;
- treat downloaded language resources as a device state;
- keep original and translated content under the app’s retention policy.

For TranslationUIProvider:

- treat the extension as a separate target and process;
- verify the default translation entitlement and provider configuration;
- declare network access only if the provider uses a network service;
- respect the selected-text context and replacement permission;
- keep provider output and source-text replacement explicitly reviewable.

Do not claim that a provider extension is local merely because the host app also has a local TranslationSession route.

## 14. Availability and release proof

Record:

- target SDK, deployment target, device, and OS;
- requested source/target Locale.Language;
- supportedLanguages snapshot;
- LanguageAvailability status and preferred strategy;
- installed versus supported resources;
- source-detection sample and outcome;
- TranslationSession generation;
- requested and actual response languages;
- strategy and fallback state;
- cold/warm latency and memory;
- batch partial/final behavior;
- accessibility task result;
- archive/TestFlight behavior with clean install and upgrade.

Test highFidelity and lowLatency where the target supports both, and test the path where highFidelity falls back. Do not infer strategy behavior from a Mac or simulator. Test language download consent, cancellation, source ambiguity, unsupported pairs, and a long batch on the intended physical device.

### Stop conditions

- A source/target pair is treated as ready from a static language list.
- Supported and installed statuses are collapsed.
- A TranslationSession is retained after its SwiftUI view/configuration lifetime.
- A translated string replaces source content without a review/revision policy.
- Incremental batch responses have no client-ID mapping or stale-result guard.
- High-fidelity is presented as guaranteed Apple Intelligence output.
- A provider extension’s network/data behavior is conflated with TranslationSession’s local route.
- A preview, simulator run, or single translated phrase is treated as device, accessibility, semantic, privacy, or release proof.

## Sources

- [Translation](https://developer.apple.com/documentation/translation)
- [LanguageAvailability](https://developer.apple.com/documentation/translation/languageavailability)
- [LanguageAvailability.Status](https://developer.apple.com/documentation/translation/languageavailability/status)
- [TranslationSession](https://developer.apple.com/documentation/translation/translationsession)
- [TranslationSession.Configuration](https://developer.apple.com/documentation/translation/translationsession/configuration)
- [TranslationSession.Strategy](https://developer.apple.com/documentation/translation/translationsession/strategy)
- [TranslationSession.Response](https://developer.apple.com/documentation/translation/translationsession/response)
- [TranslationSession.BatchResponse](https://developer.apple.com/documentation/translation/translationsession/batchresponse)
- [TranslationSession prepareTranslation](https://developer.apple.com/documentation/translation/translationsession/preparetranslation%28%29?changes=la)
- [TranslationSession translate batch](https://developer.apple.com/documentation/translation/translationsession/translate%28batch%3A%29?changes=latest_major)
- [SwiftUI translationTask](https://developer.apple.com/documentation/swiftui/view/translationtask%28source%3Atarget%3Apreferredstrategy%3Aaction%3A%29)
- [TranslationUIProvider](https://developer.apple.com/documentation/translationuiprovider)
- [Preparing your app to be the default translation app](https://developer.apple.com/documentation/translationuiprovider/preparing-your-app-to-be-the-default-translation-app)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
