# SwiftUI Translation and language-pair proof matrix

Use this matrix with the [framework review](../42-framework-deep-dives/118-swiftui-translation-language-pair-review.md), the [design route](../21-design-deep-dives/146-swiftui-translation-language-pair-review-design.md), the [implementation route](../50-capability-recipes/149-swiftui-translation-language-pair-review-route.md), and the [code recipes](../70-code-recipes/161-swiftui-translation-language-pair-review-recipes.md).

Translation proof must distinguish source fidelity, language-pair readiness, session lifetime, actual response metadata, human review, accessibility, privacy, and signed-artifact behavior. A translated phrase is not by itself proof of a correct or shippable translation feature.

## 1. Evidence vocabulary

- **Source proof** — current Apple Translation, SwiftUI, accessibility, privacy, and release documentation was reviewed.
- **Compile proof** — the selected Translation APIs compile in the named target and SDK.
- **Fixture proof** — deterministic source/target/language/error fixtures produce expected app-owned states.
- **Device proof** — the intended physical device has the required language resources, strategy behavior, memory, and performance.
- **System proof** — system translation UI, language download prompts, or TranslationUIProvider behaves in the actual system surface.
- **Release proof** — archive/TestFlight contains the intended targets, entitlements, extension, resources, privacy behavior, and fallback.

## 2. Proof matrix

| Area | Evidence to collect | Minimum acceptance | Does not prove |
| --- | --- | --- | --- |
| Target | SDK, deployment target, target name, platform | Translation imports and selected surface compile in the intended target | Every device supports the same language pairs |
| Source | Apple Translation/SwiftUI/HIG/release links | Version-sensitive behavior and boundaries are recorded | Correct app implementation |
| Pair | Requested source/target Locale.Language and user-facing names | Pair state is explicit and stable | The pair is installed |
| Supported languages | supportedLanguages snapshot | UI offers supported choices and records the snapshot | A pair is ready now |
| Availability | LanguageAvailability status and preferredStrategy | Installed, supported, and unsupported are separate states | Translation quality |
| Unknown source | status(for:to:) sample, detection result/error | Source ambiguity and short-text failure are recoverable | A detected source is certain |
| Strategy | Requested highFidelity/lowLatency, availability status, fallback | Strategy copy and fallback match actual route | Specific hardware/model execution |
| Preparation | prepareTranslation result, permission/download/cancel path | Person understands and can recover from resource preparation | Resources remain installed forever |
| SwiftUI lifetime | View/configuration generation and session action | Session is not used after view/configuration changes | All late work is cancelled by hardware |
| Direct session | installed-source initializer and readiness precondition | Service only uses installed language resources | A non-installed pair can be downloaded there |
| Single response | source/target text and languages, source revision | Candidate maps to current source and actual response pair | Semantic equivalence |
| Formatting | AttributedString source/target fixture | Supported formatting/link policy is preserved or rejected honestly | Every custom attribute translates losslessly |
| Batch incremental | Request client IDs, AsyncSequence, partial/final states | Each response maps to the correct source row and stale rows cannot commit | Result order or complete batch quality |
| Batch complete | translations(from:) array, count/IDs/source order | Complete set is validated before publish/commit | Every translation is acceptable |
| Cancellation | Session.cancel, Task cancellation, user dismissal | Current UI preserves source and does not show cancelled output as success | Already encoded work stops immediately |
| Errors | Unsupported, unable-to-identify, denied, dismissed, system failure | Each error has an honest fallback or retry | A retry will always succeed |
| Provenance | Source ID/revision, requested/actual languages, strategy, generation | Response is traceable to source and destination | Translation meaning is correct |
| Review | Editable target, source/target comparison, destination confirmation | Person can approve, edit, replace, save, share, or discard | User noticed every nuance |
| Domain commit | Re-fetch current source, authorization, idempotency | Stale or unauthorized translation cannot mutate data | A preview or candidate is committed |
| Accessibility | VoiceOver, Dynamic Type, keyboard, pointer, Switch Control, RTL | Full translate/review/save/discard task completes | Every language has identical visual metrics |
| UI | Readable source/target, partial/stale/error state, Liquid Glass fallback | Material groups controls without hiding text or state | Native appearance alone |
| Privacy | Local/provider/network/storage/logging data map | Copy, retention, deletion, and diagnostics match actual routes | “On device” covers a custom provider |
| Performance | Cold/warm readiness, single/batch latency, peak memory, sustained use | Representative target-device budget is met | Future devices or OS versions |
| Interruption | Background/foreground, resource download, relaunch, target change | State recovers without losing source or committing stale target | Long-term system download reliability |
| Provider | Entitlement, extension context, replacement permission, network key | Provider behavior and replacement are tested in the system surface | In-app TranslationSession behavior |
| Archive | Signed app/extension, entitlements, resources, target membership | Translation route works in archive/TestFlight | App Store approval |

## 3. Language-pair fixture matrix

At minimum, use:

| Fixture | Expected evidence |
| --- | --- |
| Installed source/target | status installed and direct/session translation succeeds |
| Supported but not installed | status supported and prepare/download state appears |
| Unsupported pair | status unsupported with pair selection/manual fallback |
| Unknown source with a useful sample | status(for:to:) identifies or reports an actionable error |
| Short ambiguous source | source-language selection or original-only fallback |
| High-fidelity available | requested strategy and actual fallback policy are recorded |
| High-fidelity unavailable | lower-latency or original-only policy is visible |
| Download denied | source is preserved and no false target is shown |
| Download dismissed | current request cancels; later retry re-checks status |
| Target changed mid-task | old response is stale and cannot publish |
| Mixed-language batch | rejected or split according to an explicit policy |
| RTL/CJK/emoji/URLs/code | text remains readable, selectable, and source-linked |

Do not infer availability from the device locale, a static list, or a prior run.

## 4. Session lifecycle proof

For a SwiftUI task:

1. enter the view with source/target;
2. observe the task receive a session;
3. begin a translation;
4. change target;
5. verify old work cannot update the new target;
6. leave the view;
7. verify no session is retained or used by app-owned code;
8. return with a new generation;
9. verify the new response carries the new source revision.

For a direct session:

1. prove pair status is installed;
2. initialize with installed source;
3. translate a bounded string;
4. cancel;
5. verify later calls fail or require a new session according to the SDK;
6. re-check status after the user changes language.

## 5. Batch proof

For incremental batches, record:

    request count
    client identifiers
    source revision per row
    response count
    partial/final state
    cancellation point
    failed identifiers
    actual source/target languages

Test responses arriving in an order different from source order. Test a row deleted or edited while its translation is in flight. Confirm that a response cannot replace a new draft just because its client ID is still present.

For all-at-once batches, test count mismatch, duplicate IDs, one invalid request, cancellation, and a complete response set whose target text still requires human review.

## 6. Source and semantic review

Translation is not lossless proof. Use domain fixtures for:

- names and product terminology;
- identifiers, URLs, and code;
- dates, numbers, and units;
- legal, medical, or financial wording where the app makes no claim beyond presenting a candidate;
- idioms, ambiguity, and tone;
- attributed links and formatting.

The app should show the original and the target and preserve an edit path. If the product must guarantee a domain-specific term, implement a deterministic validation or glossary policy and test it separately from TranslationSession.

## 7. Accessibility task evidence

Run the complete task:

1. choose a source;
2. choose source and target languages;
3. understand readiness;
4. start and cancel;
5. read source and target;
6. navigate a partial or complete batch;
7. edit and approve;
8. save/replace/share/discard.

Record VoiceOver reading order, focus after target changes, Dynamic Type wrapping, keyboard commands, pointer access, reduced motion/transparency, and RTL behavior. A screenshot or accessibility identifier alone is not task proof.

## 8. Privacy and data-path proof

Maintain a table:

| Artifact/path | Evidence |
| --- | --- |
| Source text | Retention, deletion, and logging policy |
| Target draft | Storage and user-approval policy |
| Language resources | Download prompt, device state, and cleanup expectations |
| API metrics | Copy matches Apple’s documented bundle/language metadata boundary |
| Provider network | Entitlement, Info.plist key, network destination, and disclosure |
| Diagnostics | No raw source/target text or identifiers without an explicit policy |
| Sync/export | Translation is not sent or indexed without the destination contract |

Test deletion and cancellation. Do not claim no data leaves the device if the selected route is a custom provider or network service.

## 9. Device and release packet

Record:

    Route: SwiftUI Translation language-pair workflow
    Target/SDK/deployment: <values>
    Device/OS: <physical device>
    Source/target pair: <Locale.Language values>
    Availability status: <installed/supported/unsupported>
    Strategy: <requested/actual/fallback>
    Surface: <SwiftUI task/direct/batch/provider>
    Fixture: <source/revision/content kind>
    Result metadata: <actual source/target/client ID>
    Accessibility: <task and outcome>
    Privacy: <storage/provider/logging>
    Performance: <cold/warm/batch/memory>
    Signed artifact: <archive/TestFlight/build>
    Open risks: <known limitations>

Repeat the packet for at least one clean install and one upgraded app if the app persists translated drafts or language-pair state.

## Stop conditions

- Installed/supported/unsupported status is absent.
- The response lacks source/target language and source revision.
- Session lifetime is not tested across SwiftUI view/configuration changes.
- Batch responses cannot be mapped to source rows.
- The UI has no original/manual path.
- Provider network behavior is untested.
- Accessibility evidence is a screenshot instead of a completed task.
- A translated phrase, simulator run, or Debug build is treated as semantic, device, privacy, or release proof.

## Sources

- [Translation](https://developer.apple.com/documentation/translation)
- [LanguageAvailability](https://developer.apple.com/documentation/translation/languageavailability)
- [LanguageAvailability.Status](https://developer.apple.com/documentation/translation/languageavailability/status)
- [LanguageAvailability status for sample text](https://developer.apple.com/documentation/translation/languageavailability/status%28for%3Ato%3A%29?language=objc)
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
