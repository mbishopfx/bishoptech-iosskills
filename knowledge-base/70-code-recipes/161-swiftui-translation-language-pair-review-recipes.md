# SwiftUI Translation and language-pair code recipes

These are compile-oriented sketches for the [Translation review](../42-framework-deep-dives/118-swiftui-translation-language-pair-review.md). They pair with the [design route](../21-design-deep-dives/146-swiftui-translation-language-pair-review-design.md), the [capability route](../50-capability-recipes/149-swiftui-translation-language-pair-review-route.md), and the [proof matrix](../60-verification/143-swiftui-translation-language-pair-proof-matrix.md).

The snippets show session, source, language, and review boundaries. They are not claimed to compile unchanged against every iOS 26 SDK revision. Compile each selected API in a named target and test the actual language resources on a physical device.

## 1. App-owned translation values

Keep Translation framework sessions out of domain records:

~~~swift
import Foundation
import Translation

struct TranslationSource: Hashable, Sendable {
    let id: String
    let revision: String
    let text: String
    let localeDescription: String?
}

struct LanguagePair: Hashable, Sendable {
    let source: Locale.Language?
    let target: Locale.Language?
}

enum TranslationReadiness: Sendable {
    case checking
    case installed
    case supportedNeedsDownload
    case unsupported
    case unableToIdentify
    case failed(String)
}

enum TranslationMode: Sendable {
    case highFidelity
    case lowLatency
    case originalOnly
}

struct TranslationCandidate: Identifiable, Sendable {
    let id: String
    let source: TranslationSource
    let sourceLanguage: Locale.Language
    let targetLanguage: Locale.Language
    let targetText: String
    let requestedMode: TranslationMode
    let actualMode: TranslationMode
    let clientIdentifier: String?
    var editedText: String
    var reviewed: Bool
}
~~~

Persist source identity and response metadata, not a TranslationSession instance.

## 2. Language availability service

LanguageAvailability is the pair-readiness gate:

~~~swift
import Translation

actor TranslationAvailabilityService {
    func supportedLanguages(
        preferredStrategy: TranslationSession.Strategy
    ) async -> [Locale.Language] {
        let availability = LanguageAvailability(
            preferredStrategy: preferredStrategy
        )
        return await availability.supportedLanguages
    }

    func status(
        from source: Locale.Language,
        to target: Locale.Language?,
        preferredStrategy: TranslationSession.Strategy
    ) async -> LanguageAvailability.Status {
        let availability = LanguageAvailability(
            preferredStrategy: preferredStrategy
        )
        return await availability.status(from: source, to: target)
    }

    func status(
        for sample: String,
        to target: Locale.Language?,
        preferredStrategy: TranslationSession.Strategy
    ) async throws -> LanguageAvailability.Status {
        let availability = LanguageAvailability(
            preferredStrategy: preferredStrategy
        )
        return try await availability.status(for: sample, to: target)
    }
}
~~~

Verify the current async property and initializer spellings in the selected SDK. Never use a supported language list as proof that a particular pair is installed.

## 3. Map availability to UI state

Keep installed, supported, and unsupported distinct:

~~~swift
func readiness(
    for status: LanguageAvailability.Status
) -> TranslationReadiness {
    switch status {
    case .installed:
        return .installed
    case .supported:
        return .supportedNeedsDownload
    case .unsupported:
        return .unsupported
    @unknown default:
        return .failed("Unknown translation availability state.")
    }
}
~~~

The unknown case is an app safety boundary. The exact enum behavior can change with SDK evolution, so compile and test the current cases.

## 4. SwiftUI translation task

A view-owned session should stay inside the action closure:

~~~swift
import SwiftUI
import Translation

struct TranslationCard: View {
    let source: TranslationSource
    let sourceLanguage: Locale.Language?
    let targetLanguage: Locale.Language?

    @State private var targetText: String?
    @State private var failure: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(source.text)
            if let targetText {
                Text(targetText)
            } else {
                Text("Translation not ready")
                    .foregroundStyle(.secondary)
            }
            if let failure {
                Text(failure)
                    .foregroundStyle(.red)
            }
        }
        .translationTask(
            source: sourceLanguage,
            target: targetLanguage,
            preferredStrategy: .lowLatency
        ) { session in
            do {
                let response = try await session.translate(source.text)
                guard response.sourceText == source.text else {
                    failure = "The source changed before translation completed."
                    return
                }
                targetText = response.targetText
                failure = nil
            } catch {
                targetText = nil
                failure = "Translation could not be completed."
            }
        }
    }
}
~~~

This is only a view sketch. A production view should include a source generation and ensure that a response belongs to the current source revision before it is saved.

## 5. Configuration-driven rerun

Use Configuration as SwiftUI state when the same pair translates changing content:

~~~swift
import SwiftUI
import Translation

struct DraftTranslationView: View {
    @State private var sourceText = ""
    @State private var targetText = ""
    @State private var configuration: TranslationSession.Configuration?

    let sourceLanguage: Locale.Language?
    let targetLanguage: Locale.Language?

    var body: some View {
        VStack {
            TextEditor(text: $sourceText)
            Text(targetText)
            Button("Translate") {
                if let configuration {
                    configuration.invalidate()
                } else {
                    configuration = TranslationSession.Configuration(
                        source: sourceLanguage,
                        target: targetLanguage,
                        preferredStrategy: .lowLatency
                    )
                }
            }
        }
        .translationTask(configuration) { session in
            do {
                let response = try await session.translate(sourceText)
                targetText = response.targetText
            } catch {
                targetText = ""
            }
        }
    }
}
~~~

Keep the source revision outside the Configuration. Calling invalidate does not make a response current if the source changes again while the work is in flight.

## 6. Preparation flow

Prepare a known pair through a user-visible action:

~~~swift
@MainActor
final class TranslationPreparationModel: ObservableObject {
    @Published private(set) var state = "Not prepared"
    private var configuration: TranslationSession.Configuration?

    func prepare(
        source: Locale.Language?,
        target: Locale.Language?
    ) {
        let configuration = TranslationSession.Configuration(
            source: source,
            target: target,
            preferredStrategy: .lowLatency
        )
        self.configuration = configuration
        state = "Preparing language resources"

        Task {
            do {
                try await configuration.prepareTranslation()
                await MainActor.run {
                    self.state = "Ready to translate"
                }
            } catch {
                await MainActor.run {
                    self.state = "Preparation was cancelled or failed"
                }
            }
        }
    }
}
~~~

Confirm the current API placement and actor behavior in the target SDK. The UI should explain download permission and preserve the original source if preparation fails.

## 7. Direct installed session

Use the installed initializer only after readiness proof:

~~~swift
import Translation

actor InstalledTranslationService {
    func translate(
        text: String,
        source: Locale.Language,
        target: Locale.Language,
        strategy: TranslationSession.Strategy
    ) async throws -> TranslationSession.Response {
        let session = try TranslationSession(
            installedSource: source,
            target: target,
            preferredStrategy: strategy
        )
        return try await session.translate(text)
    }
}
~~~

If the pair is not installed, return a readiness error rather than attempting a hidden background download. The caller can route to SwiftUI preparation.

## 8. AttributedString translation

Preserve formatting only when the target accepts it:

~~~swift
import Foundation
import Translation

actor FormattedTranslationService {
    func translate(
        source: AttributedString,
        session: TranslationSession
    ) async throws -> TranslationSession.Response {
        try await session.translate(source)
    }
}
~~~

Store source and target AttributedString values separately. Test links, emphasis, line breaks, and custom attributes. A formatted response still requires content review before a destructive replacement.

## 9. Batch request identities

Give every request a client identifier:

~~~swift
import Translation

struct BatchSource: Identifiable, Sendable {
    let id: String
    let sourceRevision: String
    let text: String
}

func requests(
    from rows: [BatchSource]
) -> [TranslationSession.Request] {
    rows.map {
        TranslationSession.Request(
            sourceText: $0.text,
            clientIdentifier: $0.id
        )
    }
}
~~~

Verify the current Request initializer against the SDK. Do not map responses by array position when incremental responses can arrive in a different order.

## 10. Incremental batch model

Keep partial results separate from committed records:

~~~swift
@MainActor
final class BatchTranslationModel: ObservableObject {
    @Published private(set) var targetByID: [String: String] = [:]
    @Published private(set) var completed = 0
    @Published private(set) var isPartial = false
    @Published private(set) var errorMessage: String?

    func translate(
        rows: [BatchSource],
        session: TranslationSession
    ) {
        targetByID = [:]
        completed = 0
        isPartial = true
        errorMessage = nil

        Task {
            do {
                let stream = session.translate(batch: requests(from: rows))
                for try await response in stream {
                    guard let id = response.clientIdentifier else { continue }
                    await MainActor.run {
                        targetByID[id] = response.targetText
                        completed += 1
                    }
                }
                await MainActor.run {
                    isPartial = false
                }
            } catch is CancellationError {
                await MainActor.run {
                    errorMessage = "Translation was cancelled."
                }
            } catch {
                await MainActor.run {
                    errorMessage = "Some translations could not be completed."
                }
            }
        }
    }
}
~~~

The real model needs a generation and source-revision check before every publication. The sketch shows the partial/final distinction but is not a complete persistence implementation.

## 11. All-at-once batch

Use translations(from:) when the UI should reveal a complete set:

~~~swift
func translateAll(
    rows: [BatchSource],
    session: TranslationSession
) async throws -> [TranslationSession.Response] {
    let response = try await session.translations(from: requests(from: rows))
    guard response.count == rows.count else {
        throw NSError(domain: "TranslationRoute", code: 20)
    }
    return response
}
~~~

Validate client identifiers, actual source/target languages, source revisions, and source order before creating a candidate set. A complete response array is not permission to commit every target.

## 12. Strategy adapter

Make requested and actual strategy visible:

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

func strategy(
    requested: TranslationMode
) -> TranslationSession.Strategy? {
    switch requested {
    case .highFidelity:
        return .highFidelity
    case .lowLatency:
        return .lowLatency
    case .originalOnly:
        return nil
    }
}
~~~

Check pair readiness with the same preferred strategy. If high-fidelity is not available, choose low latency only when the product permits that fallback and disclose the actual mode in the review state.

## 13. Revision-aware publication

Associate every asynchronous task with a generation:

~~~swift
struct TranslationGeneration: Hashable, Sendable {
    let number: UInt64
    let sourceID: String
    let sourceRevision: String
    let targetDescription: String
}

@MainActor
final class TranslationViewModel: ObservableObject {
    @Published private(set) var targetText = ""
    @Published private(set) var status = "Idle"
    private var generation: UInt64 = 0
    private var task: Task<Void, Never>?

    func start(
        source: TranslationSource,
        sourceLanguage: Locale.Language?,
        targetLanguage: Locale.Language?,
        run: @escaping @Sendable (TranslationGeneration) async throws -> String
    ) {
        task?.cancel()
        generation &+= 1
        let current = TranslationGeneration(
            number: generation,
            sourceID: source.id,
            sourceRevision: source.revision,
            targetDescription: String(describing: targetLanguage)
        )
        status = "Translating"

        task = Task { [weak self] in
            do {
                let text = try await run(current)
                guard !Task.isCancelled else { return }
                await MainActor.run {
                    guard self?.generation == current.number else { return }
                    self?.targetText = text
                    self?.status = "Ready for review"
                }
            } catch is CancellationError {
                await MainActor.run {
                    self?.status = "Cancelled"
                }
            } catch {
                await MainActor.run {
                    self?.status = "Translation failed"
                }
            }
        }
    }
}
~~~

The domain layer must re-fetch and validate the source again before save, replace, share, or send.

## 14. Reviewable candidate and commit

Keep translation output as a candidate:

~~~swift
struct TranslationCandidate: Identifiable, Sendable {
    let id: String
    let sourceID: String
    let sourceRevision: String
    let sourceText: String
    let targetText: String
    let sourceLanguage: Locale.Language
    let targetLanguage: Locale.Language
    let strategyDescription: String
    var editedText: String
    var reviewed: Bool
}

enum CommitFailure: Error {
    case staleSource
    case unauthorized
    case emptyTarget
    case destinationChanged
}

actor TranslationCommitter {
    func commit(
        candidate: TranslationCandidate,
        currentSourceRevision: String?,
        destinationStillValid: Bool,
        authorized: Bool
    ) throws {
        guard authorized else { throw CommitFailure.unauthorized }
        guard currentSourceRevision == candidate.sourceRevision else {
            throw CommitFailure.staleSource
        }
        guard destinationStillValid else {
            throw CommitFailure.destinationChanged
        }
        guard !candidate.editedText.isEmpty else {
            throw CommitFailure.emptyTarget
        }
        // Re-fetch, validate, commit idempotently, and record undo.
    }
}
~~~

Do not make the translation service call the committer internally. Keeping the boundary explicit makes it possible to add editing, approval, and safety checks.

## 15. TranslationUIProvider outline

The provider route is an extension target with its own context:

~~~swift
import SwiftUI
import TranslationUIProvider

@main
struct TranslationProviderExtension: TranslationUIProviderExtension {
    var body: some TranslationUIProviderExtensionScene {
        TranslationUIProviderSelectedTextScene { context in
            ProviderSelectedTextView(context: context)
        }
    }
}

struct ProviderSelectedTextView: View {
    let context: TranslationUIProviderContext
    @State private var translated = ""

    var body: some View {
        VStack(alignment: .leading) {
            Text(context.inputText ?? "")
            Text(translated)
            Button("Translate") {
                // Call the provider-owned translation service.
            }
            Button("Replace with translation") {
                context.finish(
                    replacingWithTranslation: AttributedString(translated)
                )
            }
            .disabled(!context.allowsReplacement)
        }
    }
}
~~~

Confirm the current protocol and scene spellings. The provider must disclose its own network/local behavior and must not assume that in-app TranslationSession state is available in the extension.

## 16. Tests and fixture contracts

Write tests for:

~~~swift
struct TranslationFixture: Sendable {
    let sourceID: String
    let sourceRevision: String
    let sourceText: String
    let sourceLanguage: String?
    let targetLanguage: String?
    let expectedReadiness: String
}

// Include installed, supported, unsupported, ambiguous,
// download-denied, high-fidelity fallback, single, batch,
// target-change, cancellation, RTL, CJK, URLs, and formatting fixtures.
~~~

Assert source revision, actual response language, client identifier, partial/final state, and stale behavior—not only that targetText is non-empty.

## 17. Compile and release checklist

- Translation and SwiftUI imports compile in the named target.
- Async availability, session, batch, and provider signatures match the installed SDK.
- Installed/supported/unsupported language pairs are tested on a physical device.
- Download permission, dismissal, cancellation, and later retry are tested.
- Source, target, strategy, and source revision are stored with every candidate.
- SwiftUI session lifetime is not extended beyond its view/configuration.
- Batch responses map by client identifier.
- Original/manual fallback is reachable.
- VoiceOver, Dynamic Type, keyboard, RTL, attributed text, and reduced effects are tested.
- Archive/TestFlight contains the intended provider extension, entitlements, and resources.

## Stop conditions

- The code uses a direct installed session before readiness proof.
- Stale target text can overwrite a new source or language pair.
- A batch candidate can commit without source identity or review.
- The provider extension hides network behavior or replacement permission.
- A translated phrase, preview, or simulator run is treated as semantic, privacy, accessibility, device, or release proof.

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
