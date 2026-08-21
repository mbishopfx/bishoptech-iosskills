# Speech, Translation, and Audio Recipes

These route sketches feed the [reviewable multimodal AI pipeline](../31-on-device-ai-recipes/06-reviewable-multimodal-ai-pipeline.md). Use the [AI lifecycle and availability guide](../30-on-device-ai/09-ai-feature-lifecycle-and-availability.md) for asset/locale/permission states and the [evaluation discipline](../30-on-device-ai/10-on-device-ai-evaluation-and-model-update-discipline.md) for representative language and audio fixtures.

## Scope and compile boundary

These are compile-oriented route sketches for Speech, Translation, AVFAudio, Sound Analysis, Natural Language, and the Swift concurrency pieces that connect them. They are intentionally explicit about authorization, language assets, audio-session lifecycle, cancellation, and review boundaries. They are not compiled in this documentation-only workspace and do not prove microphone access, speaker output, Bluetooth behavior, real-time latency, speech accuracy, or physical-device performance.

Before using a recipe, verify the selected SDK and deployment target, add truthful usage descriptions, compile the smallest route in the target app, and test on supported physical hardware. Treat captured audio, transcripts, translations, and classifier results as sensitive product data. Do not put raw audio or full transcripts in ordinary logs, analytics, crash payloads, or network requests by default.

## Route map

| Product outcome | Owning route | Output and lifecycle | Boundary to keep visible |
| --- | --- | --- | --- |
| Turn speech into editable text | Speech | Progressive or final transcript from a live/file input sequence | Microphone and speech-recognition authorization, locale/assets, interruption, cancellation, and volatile text |
| Translate text or a supported document | Translation | Derived text or attributed content for a source/target language pair | Installed versus supported language assets, download consent, original-text preservation, and cancellation |
| Read text aloud | AVFAudio `AVSpeechSynthesizer` | Speaker output with speaking, paused, finished, and cancelled states | Voice/language availability, audio-session category, interruptions, route changes, and stop controls |
| Classify bounded environmental audio | Sound Analysis | Classification observations with confidence | Microphone permission, model/request availability, noise, confidence calibration, and retention |
| Tag or analyze text deterministically | Natural Language | Tokens, language, tags, sentiment, or embeddings | Locale/task coverage and the difference between analysis and generation |
| Send or receive a live voice conversation | AVFAudio plus networking/telephony APIs | Bidirectional audio stream, usually with remote participants | This is remote communication, not an on-device-only intelligence claim; add network, privacy, call, and background review |

Choose the narrowest route that produces the needed output. A transcript is not a translation, a translation is not a command, text-to-speech is not speech recognition, and a sound classifier is not proof of who or what produced a sound.

## Recipe 1: model modern speech analysis as a state machine

Keep authorization, locale/module readiness, input, analysis, and review separate. The UI should be able to explain why it is waiting instead of presenting every non-result as an error.

```swift
import Foundation
import Speech

struct TranscriptDraft: Sendable {
    var volatileText = ""
    var finalizedText = ""
    var sourceLocale: Locale
    var isFinal = false
    var requiresReview = true
}

actor TranscriptAccumulator {
    private var draft: TranscriptDraft

    init(locale: Locale) {
        draft = TranscriptDraft(sourceLocale: locale)
    }

    func ingest(_ result: SpeechTranscriber.Result) -> TranscriptDraft {
        let text = String(result.text.characters)
        if result.isFinal {
            draft.finalizedText = text
            draft.isFinal = true
        } else {
            draft.volatileText = text
            draft.isFinal = false
        }
        return draft
    }
}

enum SpeechRouteState: Sendable {
    case needsPermission
    case checkingLocaleAndAssets
    case ready
    case listening
    case analyzing
    case interrupted
    case cancelled
    case finished
    case unavailable(String)
    case failed(String)
}
```

The modern Speech route composes a `SpeechAnalyzer` with a `SpeechTranscriber`, selects a locale and preset, supplies the framework’s current asynchronous input sequence, consumes the transcriber’s results, and explicitly finishes or cancels. The input-sequence type and asset-installation call are SDK-sensitive; resolve them against the target SDK before copying the sketch into a project.

```swift
import Speech

struct SpeechAnalyzerRunner {
    func run(
        requestedLocale: Locale,
        update: @Sendable (TranscriptDraft) -> Void
    ) async throws {
        guard let locale = SpeechTranscriber.supportedLocale(
            equivalentTo: requestedLocale
        ) else {
            throw SpeechRouteError.unsupportedLocale
        }

        let transcriber = SpeechTranscriber(
            locale: locale,
            preset: .progressiveTranscription
        )

        if let installationRequest = try await AssetInventory
            .assetInstallationRequest(supporting: [transcriber]) {
            try await installationRequest.downloadAndInstall()
        }

        let (inputSequence, inputBuilder) = AsyncStream.makeStream(
            of: AnalyzerInput.self
        )
        let audioFormat = await SpeechAnalyzer.bestAvailableAudioFormat(
            compatibleWith: [transcriber]
        )
        let converter = AnalyzerInputConverter(analyzerFormat: audioFormat)
        let analyzer = SpeechAnalyzer(modules: [transcriber])

        // Feed this builder from an AVAudioEngine tap or an audio-file reader:
        // let inputs = try converter.convert(buffer, at: bufferStartTime)
        // inputs.forEach { inputBuilder.yield($0) }
        // inputBuilder.finish() when capture/file input ends.

        let accumulator = TranscriptAccumulator(locale: locale)
        let resultsTask = Task {
            do {
                for try await result in transcriber.results {
                    update(await accumulator.ingest(result))
                }
            }
        }

        do {
            try await analyzer.start(inputSequence: inputSequence)

            // Keep the capture task alive while the analyzer consumes input.
            // For each AVAudioPCMBuffer, convert and yield AnalyzerInput values:
            // let inputs = try converter.convert(buffer, at: bufferStartTime)
            // inputs.forEach { inputBuilder.yield($0) }
            // When capture stops, calls finish on this continuation.
            // The surrounding product code must await that capture lifecycle here.
            inputBuilder.finish()
            try await analyzer.finalizeAndFinishThroughEndOfInput()
            try await resultsTask.value
        } catch is CancellationError {
            inputBuilder.finish()
            resultsTask.cancel()
            await analyzer.cancelAndFinishNow()
            throw CancellationError()
        } catch {
            inputBuilder.finish()
            resultsTask.cancel()
            throw error
        }
    }
}

enum SpeechRouteError: Error {
    case unsupportedLocale
}
```

The route follows Apple’s current `AnalyzerInput`/`AnalyzerInputConverter` shape, but the capture tap/file reader and task ownership still belong to the target app. Ensure that the input sequence is finished before calling `finalizeAndFinishThroughEndOfInput()`; ending an `AsyncStream` alone does not generally finish the analyzer. If the app wants autonomous analysis of a different input, finish or finalize the previous sequence before replacing it. Do not use the volatile string to execute an action. Promote finalized text only after the user or a deterministic parser has reviewed it.

In the sketch, `inputBuilder.finish()` represents the end of the owning capture/file task. A live implementation must not execute that line immediately after `start`; it belongs after the user taps Stop, the file reaches EOF, or an interruption policy deliberately ends capture. Keep the result-consumer task alive until the analyzer’s finish method has completed.

## Recipe 2: check authorization, locale, and assets before capture

There are at least two independent gates: microphone recording permission and speech-recognition authorization. A product can have one without the other. Add accurate `NSMicrophoneUsageDescription` and `NSSpeechRecognitionUsageDescription` values before requesting access, and explain the feature at the moment of need.

```swift
import AVFAudio
import Speech

struct SpeechReadiness {
    let recordPermission: AVAudioSession.RecordPermission
    let speechAuthorization: SFSpeechRecognizerAuthorizationStatus
    let recognizerIsAvailable: Bool
}

func currentSpeechReadiness(for locale: Locale) -> SpeechReadiness {
    let session = AVAudioSession.sharedInstance()
    let recognizer = SFSpeechRecognizer(locale: locale)

    return SpeechReadiness(
        recordPermission: session.recordPermission,
        speechAuthorization: SFSpeechRecognizer.authorizationStatus(),
        recognizerIsAvailable: recognizer?.isAvailable ?? false
    )
}
```

Request permission with the APIs documented for the selected SDK and move the app into a visible `needsPermission`, `denied`, `restricted`, or `ready` state. For the modern analyzer route, also check `SpeechTranscriber` locale support/installation and the applicable `AssetInventory` state. “The device supports Speech” is not enough: the requested locale, module, assets, audio route, and current resource state all matter.

If permission is denied, provide typed input or an imported audio-file route when that still serves the feature. Do not repeatedly present a permission prompt after denial, and do not silently switch to a remote transcription service. If a remote fallback is an intentional product choice, disclose the destination, retention, and user control before sending audio or transcript content.

## Recipe 3: own the audio-session lifecycle

Configure `AVAudioSession` for the actual behavior. A recording route and a speech-output route have different categories and modes. Activate only when needed, deactivate when the feature ends, and treat interruptions and route changes as state transitions rather than exceptional noise.

```swift
import AVFAudio

final class AudioSessionCoordinator {
    private let session = AVAudioSession.sharedInstance()

    func beginRecording() throws {
        try session.setCategory(.record, mode: .measurement, options: [])
        try session.setActive(true)
    }

    func beginSpeechOutput() throws {
        try session.setCategory(.playback, mode: .spokenAudio, options: [])
        try session.setActive(true)
    }

    func end() {
        try? session.setActive(
            false,
            options: [.notifyOthersOnDeactivation]
        )
    }
}
```

The category/mode combination is a starting point, not a universal setting. Verify whether the product needs play-and-record, Bluetooth input, echo cancellation, spoken-audio ducking, background audio, or another documented behavior. Do not add an entitlement or background mode merely because a route sketch contains audio.

Observe `AVAudioSession.interruptionNotification` and `AVAudioSession.routeChangeNotification`. On interruption, pause or finish the input sequence according to the product contract; on a route change, re-check the current input/output and update the UI. Resume only when the interruption ended and the route is still suitable. Test phone calls, alarms, Siri, headphones, Bluetooth connect/disconnect, output changes, screen lock, backgrounding, and another app taking the audio session.

## Recipe 4: stream audio with bounded work and cancellation

Speech capture can produce buffers faster than UI code can render them. Keep the capture boundary small, isolate mutable analysis state, and make dropping/coalescing behavior observable. For a transcript, dropping arbitrary middle buffers can change meaning; use the analyzer’s intended input sequence and bounded handoff rather than an unbounded task per buffer.

```swift
import Foundation

actor BoundedAudioHandoff<Buffer: Sendable> {
    private var continuation: AsyncStream<Buffer>.Continuation?
    private var stream: AsyncStream<Buffer>?

    func makeStream() -> AsyncStream<Buffer> {
        let pair = AsyncStream<Buffer>.makeStream(
            of: Buffer.self,
            bufferingPolicy: .bufferingNewest(8)
        )
        stream = pair.stream
        continuation = pair.continuation
        return pair.stream
    }

    func submit(_ buffer: Buffer) {
        _ = continuation?.yield(buffer)
    }

    func finish() {
        continuation?.finish()
        continuation = nil
        stream = nil
    }
}
```

This is a generic handoff policy, not a claim that every Speech input should buffer only eight audio values. Select a buffer policy from the analyzer’s timing contract, measure dropped input, and prefer a documented audio-buffer adapter. Cancel the consumer when the recording screen disappears; finish the producer before finalizing the analyzer; release buffers and tear down the audio engine after the task is done.

Use one owner for a recording session. A new recording should cancel or finish the previous analysis before replacing its input sequence because a `SpeechAnalyzer` session is not an unbounded collection of independent recordings.

## Recipe 5: preserve progressive and final transcript states

Render volatile text as a draft and finalized text as a stable value. Keep an explicit “review before action” boundary even when a result is marked final, because final means final for that analysis pass—not guaranteed factual accuracy or authorization.

```swift
struct TranscriptReviewModel: Sendable {
    var volatileText = ""
    var finalizedText = ""
    var editedText = ""
    var sourceLocaleIdentifier = ""
    var isFrameworkFinal = false
    var isUserConfirmed = false

    var textForReview: String {
        editedText.isEmpty
            ? (isFrameworkFinal ? finalizedText : volatileText)
            : editedText
    }
}

func commandCandidate(from model: TranscriptReviewModel) -> String? {
    guard model.isUserConfirmed else { return nil }
    let text = model.textForReview.trimmingCharacters(in: .whitespacesAndNewlines)
    return text.isEmpty ? nil : text
}
```

If the transcript proposes “send,” “buy,” “delete,” “unlock,” or a sensitive-record change, route it through typed parsing, authorization, and confirmation. Do not pass raw speech directly to an App Intent or a network request. Store source audio, transcript, parsed fields, and user confirmation as separate data with separate retention decisions.

## Recipe 6: make Translation availability and source preservation explicit

Use `LanguageAvailability` before presenting a custom translation operation. Distinguish an unsupported pair from a supported-but-not-installed pair and an installed pair. If a download is possible, explain what will happen and preserve the original while assets are prepared.

```swift
import Translation

struct TranslationRoute {
    func status(
        from source: Locale.Language,
        to target: Locale.Language
    ) async -> LanguageAvailability.Status {
        let availability = LanguageAvailability()
        return await availability.status(from: source, to: target)
    }

    func translateWhenReady(
        text: String,
        source: Locale.Language,
        target: Locale.Language
    ) async throws {
        // Route sketch: create the TranslationSession using the current SDK’s
        // installed source/target configuration after availability is ready.
        let session = try TranslationSession(installedSource: source, target: target)
        let derivedTranslation = try await session.translate(text)

        // Persist/display the returned translation beside the unchanged source.
        consumeDerivedTranslation(derivedTranslation)
    }

    private func consumeDerivedTranslation(
        _ translation: TranslationSession.Response
    ) {
        let translatedText = translation.targetText
        // Store translatedText beside the unchanged source text.
    }
}
```

The session initializer throws when the installed-language precondition is not met, and `TranslationSession.Response.targetText` is the derived string. The product contract is stable: check status, request/prepare language assets only with user-visible intent, surface not-ready/unavailable states, allow cancellation, and never overwrite source text or user edits with a derived translation.

For SwiftUI-owned translation UI, evaluate the documented translation modifiers and session configuration instead of rebuilding system UI. Use a custom `TranslationSession` when the app needs a controlled review/edit workflow, batch operation, or product-owned presentation.

## Recipe 7: speak text with a cancellable output controller

Text-to-speech is audio output, not speech recognition. Use `AVSpeechSynthesizer` and an `AVSpeechUtterance` for a local speaking route, choose a language/voice deliberately, and expose stop/pause behavior. Configure the audio session for output and handle interruptions.

```swift
import AVFAudio

@MainActor
final class SpeechOutputController: NSObject, AVSpeechSynthesizerDelegate {
    private let synthesizer = AVSpeechSynthesizer()

    override init() {
        super.init()
        synthesizer.delegate = self
    }

    func speak(_ text: String, language: String) throws {
        let session = AVAudioSession.sharedInstance()
        try session.setCategory(.playback, mode: .spokenAudio, options: [])
        try session.setActive(true)

        let utterance = AVSpeechUtterance(string: text)
        utterance.voice = AVSpeechSynthesisVoice(language: language)
        synthesizer.speak(utterance)
    }

    func stop() {
        synthesizer.stopSpeaking(at: .immediate)
        try? AVAudioSession.sharedInstance().setActive(
            false,
            options: [.notifyOthersOnDeactivation]
        )
    }
}
```

Check whether a voice exists for the requested language and offer a readable text fallback. Do not assume that a selected language, silent mode, output route, or background state produces the same result on every device. If speech output reads sensitive content, show the destination and make stop available from the active screen/system surface.

## Recipe 8: classify bounded audio without overclaiming

Use Sound Analysis when the result is a bounded audio category, not when the product needs open-ended understanding or speaker identity. A typical route is:

`microphone permission -> AVAudioEngine/input format -> SNAudioStreamAnalyzer -> SNRequest -> observer -> confidence/review -> optional local record`

Keep the classifier request and observer in a dedicated lifecycle object. Remove requests when the feature stops, stop the audio engine, and cancel work when the view/task is gone. Record the model/request version and input conditions alongside a result if the feature needs reproducible review.

Confidence is evidence for ranking or review, not proof of identity, intent, medical status, or an event. Calibrate thresholds on labeled audio from the target environment, include “unknown/noise” behavior, and make it possible to correct or dismiss a classification. Do not leave the microphone running in the background without an explicit user-facing product and entitlement review.

## Recipe 9: translate a transcript into a safe action proposal

Keep speech, translation, generation, and side effects as separate stages:

`audio -> transcript draft -> final/reviewed text -> optional translation -> typed parse -> policy check -> explicit confirmation -> side effect`

```swift
struct ActionProposal: Sendable {
    let sourceText: String
    let translatedText: String?
    let actionName: String
    let parameters: [String: String]
    let provenance: String
    var isConfirmed = false
}

func canExecute(_ proposal: ActionProposal) -> Bool {
    proposal.isConfirmed && !proposal.actionName.isEmpty
}
```

If Foundation Models enrich the route, pass only the minimum reviewed text and constrain the model to a typed result. Treat model output as a proposal. Deterministic validation must own authorization, identifiers, ranges, confirmation, idempotency, and error recovery. Translation can help a person understand a command, but it cannot grant authorization or remove the need for confirmation.

## Recipe 10: privacy, retention, and fallback contract

For every audio/language feature, write these product decisions before implementation:

| Decision | Minimum contract |
| --- | --- |
| Capture | Explain when the microphone starts/stops and show the active state. |
| Processing | Record the exact framework/API, locale, model/assets, and whether a remote service is involved. |
| Retention | Keep raw audio/transcripts only as long as the feature needs; delete on request; redact diagnostic output. |
| Derived data | Keep source and derived transcript/translation/classification separate and editable where appropriate. |
| Fallback | Provide typed input, imported audio, original language, or an unavailable state rather than silently changing data path. |
| Side effects | Require policy validation and explicit confirmation for external or sensitive changes. |
| Cancellation | Define what partial work is discarded, preserved as a draft, or finalized when a task is cancelled. |

An on-device route can still have availability, language-asset, telemetry, permission, or OS behavior caveats. Do not promise “nothing leaves the device” unless the exact API, configuration, OS, and telemetry behavior have been verified for the target release and product.

## Physical-device verification matrix

| Test | Evidence to capture |
| --- | --- |
| Microphone permission | First-use explanation, allow/deny/restricted flows, Settings change, and recovery without a reinstall |
| Speech locale/assets | Installed, supported-but-not-installed, unsupported, unavailable, download/prepare, and cancellation states |
| Streaming | Progressive versus final results, backpressure/drop policy, view disappearance, replacement recording, and cancellation |
| Audio session | Interruption begin/end, route changes, Bluetooth connect/disconnect, phone call, alarm/Siri, background/foreground, and deactivation |
| TTS | Language voice availability, stop/pause, silent mode, output route, interruption, and long text behavior |
| Sound Analysis | Noise, silence, overlapping sources, confidence calibration, unknown class, thermal/battery impact, and retention |
| Privacy | Logs, analytics, crash reports, persistence, network instrumentation, and deletion behavior contain no unintended raw content |
| Accessibility | VoiceOver labels/state, Dynamic Type, reduced motion, captions/text fallback, and controls for stop/cancel/retry |

Simulator, preview, and unit-test evidence can validate state transitions and pure parsing, but they do not prove microphone capture, speaker output, Bluetooth routes, speech quality, real-time behavior, or thermal performance. Those claims require the target physical device and an identified OS/build.

## Sources

- [Speech](https://developer.apple.com/documentation/speech/)
- [Asking permission to use speech recognition](https://developer.apple.com/documentation/speech/asking-permission-to-use-speech-recognition)
- [SpeechAnalyzer](https://developer.apple.com/documentation/speech/speechanalyzer)
- [SpeechTranscriber](https://developer.apple.com/documentation/speech/speechtranscriber)
- [SpeechTranscriber.Preset](https://developer.apple.com/documentation/speech/speechtranscriber/preset)
- [SpeechTranscriber.Result](https://developer.apple.com/documentation/speech/speechtranscriber/result)
- [AssetInventory](https://developer.apple.com/documentation/speech/assetinventory)
- [SFSpeechRecognizer](https://developer.apple.com/documentation/speech/sfspeechrecognizer)
- [Translation](https://developer.apple.com/documentation/translation)
- [TranslationSession](https://developer.apple.com/documentation/translation/translationsession)
- [LanguageAvailability](https://developer.apple.com/documentation/translation/languageavailability)
- [AVFAudio](https://developer.apple.com/documentation/avfaudio/)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [AVSpeechSynthesizer](https://developer.apple.com/documentation/avfaudio/avspeechsynthesizer)
- [AVSpeechUtterance](https://developer.apple.com/documentation/avfaudio/avspeechutterance)
- [AVSpeechSynthesisVoice](https://developer.apple.com/documentation/avfaudio/avspeechsynthesisvoice)
- [Handling audio interruptions](https://developer.apple.com/documentation/AVFAudio/handling-audio-interruptions)
- [Responding to audio route changes](https://developer.apple.com/documentation/AVFAudio/responding-to-audio-route-changes)
- [Sound Analysis](https://developer.apple.com/documentation/soundanalysis)
- [SNAudioStreamAnalyzer](https://developer.apple.com/documentation/soundanalysis/snaudiostreamanalyzer)
- [Natural Language](https://developer.apple.com/documentation/naturallanguage)
- [AsyncStream](https://developer.apple.com/documentation/swift/asyncstream)
- [Swift concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
- [Information property list key reference](https://developer.apple.com/documentation/bundleresources/information-property-list)
- [Protecting the user’s privacy](https://developer.apple.com/documentation/uikit/protecting_the_user_s_privacy)
- [App Intents](https://developer.apple.com/documentation/appintents/)
