# SwiftUI Translation and language-pair route

Use this route when an app needs to translate text on device, preserve original content, review target language output, or expose a translation surface to selected text. It pairs with the [framework review](../42-framework-deep-dives/118-swiftui-translation-language-pair-review.md), the [design route](../21-design-deep-dives/146-swiftui-translation-language-pair-review-design.md), the [proof matrix](../60-verification/143-swiftui-translation-language-pair-proof-matrix.md), and the [recipes](../70-code-recipes/161-swiftui-translation-language-pair-review-recipes.md).

This is a route sketch. Compile the chosen Translation and SwiftUI APIs against the named iOS 26 SDK and verify language assets on the target device.

## Route 1: Freeze the product contract

Write down:

| Field | Decision |
| --- | --- |
| Source | Original string or AttributedString and app-owned revision |
| Source language | Explicit Locale.Language, detected source, or user choice |
| Target language | Explicit language or preferred-language selection |
| Strategy | highFidelity, lowLatency, or user choice |
| Surface | System popover, SwiftUI task, direct session, batch, or provider extension |
| Review | Side-by-side, editable draft, or no app-owned review |
| Destination | Read-only display, saved translation, replace, share, or send |
| Fallback | Original, exact/manual, another pair, retry, or lower-latency strategy |

If the destination mutates data or sends content outside the app, translation must produce a candidate first.

## Route 2: Choose the surface

Use this ladder:

1. system translationPresentation for simple selected-text translation;
2. translationTask(source:target:action:) for a view-owned translation;
3. translationTask(configuration:action:) when the pair is state and content invalidation matters;
4. direct TranslationSession(installedSource:target:) for a non-UI service after installed-status proof;
5. translate(batch:) for incremental same-language rows;
6. translations(from:) for an all-at-once set;
7. TranslationUIProvider only when the app genuinely needs to be the default translation app.

Do not make a provider extension just to avoid designing a normal in-app review route. It has its own entitlement, process, context, replacement, and network boundaries.

## Route 3: Normalize language inputs

Use Locale.Language as the app-owned pair value. Keep user-facing names separate from identifiers. Build a language state:

    requestedSource
    requestedTarget
    detectedSource
    matchedSource
    matchedTarget
    supportedLanguages
    preferredStrategy

Prefer language values returned from LanguageAvailability.supportedLanguages. If a product accepts arbitrary locale input, record the requested value and the matched supported value rather than silently replacing it.

## Route 4: Check pair readiness

Create LanguageAvailability with the desired strategy and check:

    status(from: source, to: target)

Map the result:

- installed — safe to use an installed-source direct session;
- supported — ask the person to prepare/download resources;
- unsupported — offer another pair or fallback.

For unknown source text, call status(for:to:) with a representative sample. Handle the TranslationError path when the system cannot identify the source language. Use at least a useful sample, not a title fragment or one-word query.

Treat the readiness request as asynchronous. It may change while the app is in the foreground, after a download, or after the person changes target language.

## Route 5: Prepare resources intentionally

If the app knows the pair in advance, create a Configuration and call prepareTranslation() from a user-visible action or an appropriate preparation flow. Explain that the system may ask permission to download source and target language resources.

Keep:

    preparing -> download prompt -> downloading -> installed
                                      \-> cancelled/denied

A person dismissing a progress view can produce a user-cancelled error even while the resources continue downloading in the background. The current translation task should remain cancelled; the next attempt can re-check status.

## Route 6: Create a SwiftUI task

A SwiftUI view can use source/target or a Configuration:

~~~swift
import SwiftUI
import Translation

struct TranslationCard: View {
    let sourceText: String
    let sourceLanguage: Locale.Language?
    let targetLanguage: Locale.Language?

    @State private var targetText: String?

    var body: some View {
        VStack(alignment: .leading) {
            Text(sourceText)
            Text(targetText ?? "Not translated")
                .foregroundStyle(.secondary)
        }
        .translationTask(
            source: sourceLanguage,
            target: targetLanguage,
            preferredStrategy: .lowLatency
        ) { session in
            do {
                let response = try await session.translate(sourceText)
                targetText = response.targetText
            } catch {
                targetText = nil
            }
        }
    }
}
~~~

This is a sketch. The view should keep a generation and source revision, map errors to state, and avoid publishing a response after the source/target changes. Do not store the session beyond the action closure.

## Route 7: Use Configuration for repeatable content

Store a TranslationSession.Configuration in SwiftUI state when content changes with a stable pair:

~~~swift
@State private var configuration: TranslationSession.Configuration?

func beginTranslation(
    source: Locale.Language?,
    target: Locale.Language?
) {
    configuration = TranslationSession.Configuration(
        source: source,
        target: target,
        preferredStrategy: .lowLatency
    )
}

func refreshTranslation() {
    configuration?.invalidate()
}
~~~

The content is not stored in Configuration. Attach a source revision to the action and verify it before saving the response. When source/target changes, replace the configuration so SwiftUI creates the correct session.

## Route 8: Direct installed session

Use a direct session only after readiness:

~~~swift
import Translation

actor InstalledTranslationService {
    func translate(
        text: String,
        source: Locale.Language,
        target: Locale.Language
    ) async throws -> TranslationSession.Response {
        let session = try TranslationSession(
            installedSource: source,
            target: target,
            preferredStrategy: .lowLatency
        )
        return try await session.translate(text)
    }
}
~~~

Verify the current initializer spelling and actor isolation in the target SDK. This route should not show a download prompt or silently perform network work; if the pair is not installed, return a readiness error and route the UI to preparation.

## Route 9: Preserve formatting

Use the AttributedString overload when formatting and links are part of the product contract. Keep source and target attributes in separate values. Test links, emphasis, line breaks, and custom attributes that the destination can accept.

Do not assume every style, link, or domain annotation maps perfectly across languages. Show an editable candidate and preserve the original when a formatting or terminology check fails.

## Route 10: Incremental batch

Build requests with stable client identifiers:

~~~swift
let requests = sourceRows.map {
    TranslationSession.Request(
        sourceText: $0.text,
        clientIdentifier: $0.id
    )
}

let stream = session.translate(batch: requests)
for try await response in stream {
    guard let id = response.clientIdentifier else { continue }
    // Verify source revision, then update the matching row.
}
~~~

This is a route sketch. Confirm the current Request initializer and BatchResponse iteration in the SDK. Use one source language per session. Preserve source row identity and update UI state on the main actor only after the response belongs to the current generation.

Incremental UI states:

    waiting -> translating(2 of 10) -> partial(6 of 10) -> complete
                                      \-> cancelled/failed

Do not save each response as a final record without a durable idempotency and rollback policy.

## Route 11: All-at-once batch

Use translations(from:) when the product needs a complete set:

~~~swift
let responses = try await session.translations(from: requests)
// Validate count, client IDs, source revisions, and actual target languages.
// Publish the complete candidate set only after validation.
~~~

Keep the source order and treat missing/duplicate identifiers as a failure. A complete array does not prove every translation is semantically acceptable; it only proves the operation returned the requested response set.

## Route 12: Strategy fallback

A strategy adapter should make fallback visible:

~~~swift
enum TranslationMode: Sendable {
    case highFidelity
    case lowLatency
    case originalOnly
}

struct TranslationPlan: Sendable {
    let requested: TranslationMode
    let actual: TranslationMode
    let source: Locale.Language?
    let target: Locale.Language?
}
~~~

Ask availability using the requested strategy. If highFidelity is unavailable, decide whether the product may use lowLatency or must remain original-only. Do not silently downgrade a user-facing promise that matters to the product.

## Route 13: Generation and stale guard

Tie every response to:

    sourceRevision
    languagePair
    strategy
    configuration.version
    requestGeneration

Before publication:

- confirm the source revision is current;
- confirm target language is still selected;
- confirm the view/session generation is current;
- confirm the response’s actual languages match the intended destination;
- confirm the user has not cancelled;
- confirm the destination is still authorized.

Before commit, re-fetch the source and validate again. Translation result state is not domain state.

## Route 14: Review and commit

Convert a response into an app-owned candidate:

~~~swift
struct TranslationCandidate: Identifiable, Sendable {
    let id: String
    let sourceID: String
    let sourceRevision: String
    let sourceText: String
    let targetText: String
    let sourceLanguage: Locale.Language
    let targetLanguage: Locale.Language
    let strategy: String
    var editedTargetText: String
    var reviewed: Bool
}
~~~

The save/replace/send command should require:

- current source revision;
- current target/destination;
- user review or an explicitly documented no-review path;
- permission and account scope;
- idempotency;
- undo or recovery when the action is destructive.

## Route 15: Provider extension

Choose TranslationUIProvider only for a default translation app feature. Plan:

1. Translation UI provider entitlement;
2. provider network-access Info.plist key only if required;
3. extension target and scene;
4. selected-text context and replacement permission;
5. provider UI and accessibility;
6. custom translation service boundary;
7. privacy/network disclosure;
8. signed extension/archive/TestFlight/system proof.

The provider context and in-app TranslationSession are different ownership paths. Do not share mutable session objects across the extension boundary.

## Route 16: SwiftUI shell

Expose:

- source and target language names;
- readiness status;
- strategy/fallback;
- source text;
- target candidate;
- partial/stale/error state;
- edit/copy/save/replace/share/discard actions.

Use standard SwiftUI controls first. Add Liquid Glass around language and action groups after the semantic and accessibility paths work. Keep the original text visible in the review surface.

## Route 17: Test fixtures

Include:

- known source language and unknown source;
- 20-character-plus detection sample and short ambiguous sample;
- installed, supported, and unsupported pairs;
- download accepted, denied, dismissed, and later-ready;
- highFidelity available, fallback, and lowLatency;
- a formatted AttributedString;
- single translation;
- incremental batch with out-of-order response arrival;
- all-at-once batch;
- changed source while a session is active;
- cancelled session and late response;
- target-language change;
- RTL, CJK, emoji, URLs, code, names, and long text;
- VoiceOver, Dynamic Type, keyboard, and reduced-effects review;
- clean archive/TestFlight install.

## Route stop conditions

- Direct session creation happens before installed-pair proof.
- Source/target/strategy are not stored with the response.
- Batch rows have no client identifier.
- Translation replaces or sends content without an explicit approval policy.
- The provider extension shares an unowned session or hides network behavior.
- A single translated phrase, preview, or simulator result is treated as semantic, privacy, accessibility, device, or release proof.

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
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
