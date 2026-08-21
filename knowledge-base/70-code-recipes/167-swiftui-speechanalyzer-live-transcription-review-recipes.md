# SwiftUI SpeechAnalyzer live transcription review recipes

These are compile-oriented sketches for the focused [SpeechAnalyzer review](../42-framework-deep-dives/124-swiftui-speechanalyzer-live-transcription-review.md). They separate microphone permission, model assets, audio input, SpeechAnalyzer ownership, volatile/final transcript state, SwiftUI, and optional Foundation Models proposals.

Compile every selected symbol against the final iOS 26 SDK. The current Speech input provider and converter documentation includes beta APIs; initializers and availability must be checked in the target SDK. These sketches are not proof of microphone fidelity, model availability, final transcript accuracy, accessibility, background behavior, or release readiness.

## Recipe 1: Permission and transcriber preparation

Ask for microphone access at the point of capture and prepare a locale-specific module separately:

~~~swift
import AVFAudio
import Speech

enum SpeechPreparationError: Error {
    case unavailable
    case unsupportedLocale(Locale)
}

struct PreparedSpeech: Sendable {
    let locale: Locale
    let transcriber: SpeechTranscriber
}

func prepareSpeech(for requestedLocale: Locale) async throws -> PreparedSpeech {
    guard SpeechTranscriber.isAvailable else {
        throw SpeechPreparationError.unavailable
    }

    guard let locale = await SpeechTranscriber
        .supportedLocale(equivalentTo: requestedLocale) else {
        throw SpeechPreparationError.unsupportedLocale(requestedLocale)
    }

    let transcriber = SpeechTranscriber(
        locale: locale,
        preset: .transcription
    )

    if let request = try await AssetInventory
        .assetInstallationRequest(supporting: [transcriber]) {
        try await request.downloadAndInstall()
    }

    return PreparedSpeech(locale: locale, transcriber: transcriber)
}

func requestMicrophoneAccess() async -> Bool {
    await AVAudioApplication.requestRecordPermission()
}
~~~

The target still needs `NSMicrophoneUsageDescription`. Do not call `SFSpeechRecognizer.requestAuthorization(_:)` for a SpeechAnalyzer-only feature; that is a separate legacy recognition route. If the app supports both, keep the authorization and privacy copy explicit for each route.

## Recipe 2: Explicit transcriber options

Use explicit options when the UI needs timing, confidence, alternatives, or volatile updates:

~~~swift
import Speech

func makeReviewTranscriber(locale: Locale) -> SpeechTranscriber {
    SpeechTranscriber(
        locale: locale,
        transcriptionOptions: [],
        reportingOptions: [
            .fastResults,
            .volatileResults,
            .alternativeTranscriptions
        ],
        attributeOptions: [
            .audioTimeRange,
            .transcriptionConfidence
        ]
    )
}
~~~

If a product does not have a review interaction for alternatives or confidence, omit those options. `fastResults` and `volatileResults` are policy choices with UI and testing consequences, not default decoration.

## Recipe 3: Bounded AnalyzerInput stream

For an app-owned buffer pipeline, create a bounded input stream and convert buffers to a supported analyzer format. This sketch leaves the capture callback small and makes finish explicit:

~~~swift
import AVFAudio
import Speech

struct AnalyzerInputPipe {
    let sequence: AsyncStream<AnalyzerInput>
    let continuation: AsyncStream<AnalyzerInput>.Continuation
    let converter: AnalyzerInputConverter
}

func makeAnalyzerInputPipe(
    for modules: [any SpeechModule]
) async -> AnalyzerInputPipe? {
    guard let format = await SpeechAnalyzer
        .bestAvailableAudioFormat(compatibleWith: modules) else {
        return nil
    }

    let (sequence, continuation) = AsyncStream
        .makeStream(of: AnalyzerInput.self)

    return AnalyzerInputPipe(
        sequence: sequence,
        continuation: continuation,
        converter: AnalyzerInputConverter(analyzerFormat: format)
    )
}

func yield(
    _ buffer: AVAudioPCMBuffer,
    into pipe: AnalyzerInputPipe
) {
    do {
        let inputs = try pipe.converter.convert(buffer, at: nil)
        for input in inputs {
            pipe.continuation.yield(input)
        }
    } catch {
        pipe.continuation.finish(throwing: error)
    }
}

func finish(_ pipe: AnalyzerInputPipe) throws {
    for input in try pipe.converter.flush() {
        pipe.continuation.yield(input)
    }
    pipe.continuation.finish()
}
~~~

In a production capture graph, protect the converter and continuation with the chosen actor/queue boundary and apply a backpressure policy. If audio is discontiguous, create `AnalyzerInput` with the correct `bufferStartTime` instead of passing `nil` and silently changing the source timeline.

## Recipe 4: Run analysis and finalize the source

Start the result consumer with the analysis task and close both deliberately:

~~~swift
import Speech

struct TranscriptResultSnapshot: Sendable {
    let text: AttributedString
    let isFinal: Bool
    let resultsFinalizationTime: CMTime
}

func runAnalysis(
    pipe: AnalyzerInputPipe,
    transcriber: SpeechTranscriber,
    consume: @escaping @Sendable (TranscriptResultSnapshot) async -> Void
) async throws {
    let analyzer = SpeechAnalyzer(modules: [transcriber])

    let resultTask = Task {
        do {
            for try await result in transcriber.results {
                await consume(
                    TranscriptResultSnapshot(
                        text: result.text,
                        isFinal: result.isFinal,
                        resultsFinalizationTime: result.resultsFinalizationTime
                    )
                )
            }
        } catch {
            // Route the module error to the session generation's error state.
        }
    }

    let lastSampleTime = try await analyzer
        .analyzeSequence(pipe.sequence)

    if let lastSampleTime {
        try await analyzer.finalizeAndFinish(through: lastSampleTime)
    } else {
        await analyzer.cancelAndFinishNow()
    }

    await resultTask.value
}
~~~

The result task should normally be owned by a larger session coordinator so cancellation can stop the input source and the analyzer together. `result.isFinal` and `resultsFinalizationTime` are module-result evidence; they should feed a reducer rather than directly mutate a `Text` view.

## Recipe 5: AVAudioSession and AVAudioEngine capture boundary

This is a structural sketch for a microphone-owned audio graph. Add the target’s actual route, interruption, and background policy:

~~~swift
import AVFAudio

final class MicrophoneSource {
    private let session = AVAudioSession.sharedInstance()
    private let engine = AVAudioEngine()

    func start(onBuffer: @escaping (AVAudioPCMBuffer) -> Void) throws {
        try session.setCategory(.record, mode: .measurement, options: [])
        try session.setActive(true)

        let input = engine.inputNode
        let format = input.outputFormat(forBus: 0)
        input.installTap(
            onBus: 0,
            bufferSize: 1_024,
            format: format
        ) { buffer, _ in
            onBuffer(buffer)
        }

        engine.prepare()
        try engine.start()
    }

    func stop() {
        engine.inputNode.removeTap(onBus: 0)
        engine.stop()
        try? session.setActive(false, options: .notifyOthersOnDeactivation)
    }
}
~~~

Do not infer that a running engine means the intended microphone is producing valid data. Observe permission, route, interruption, buffer timing, and a known spoken fixture. Register interruption and route observers in the session owner, not in a transient SwiftUI view.

## Recipe 6: Minimal source-owned transcript reducer

Keep source segments and generated proposals separate:

~~~swift
import Foundation

struct SourceTranscriptSegment: Identifiable, Equatable, Sendable {
    let id: UUID
    var text: String
    var isFinal: Bool
    var sourceStart: TimeInterval?
    var sourceEnd: TimeInterval?
}

struct SourceTranscript: Equatable, Sendable {
    var revision: UInt64 = 0
    var sessionGeneration: UInt64 = 0
    var segments: [SourceTranscriptSegment] = []
    var hasGap = false
    var isComplete = false
}

enum TranscriptReducer {
    static func accept(
        _ result: TranscriptResultSnapshot,
        into transcript: inout SourceTranscript,
        segmentID: UUID,
        sessionGeneration: UInt64
    ) {
        guard transcript.sessionGeneration == sessionGeneration else {
            return
        }

        let value = SourceTranscriptSegment(
            id: segmentID,
            text: String(result.text.characters),
            isFinal: result.isFinal,
            sourceStart: nil,
            sourceEnd: nil
        )

        if let index = transcript.segments.firstIndex(
            where: { $0.id == segmentID }
        ) {
            transcript.segments[index] = value
        } else {
            transcript.segments.append(value)
        }
        transcript.revision &+= 1
    }
}
~~~

The real reducer should use time-range attributes or a source-range adapter to choose `segmentID`, retain gaps, and revoke empty volatile results. This small type is intentionally deterministic and easy to test without microphone or model access.

## Recipe 7: SwiftUI source/review shell

Keep the transcript primary and make the glass group functional:

~~~swift
import SwiftUI

struct TranscriptReviewShell: View {
    let transcript: SourceTranscript
    let isCapturing: Bool
    let isPreparing: Bool
    let start: () -> Void
    let stop: () -> Void
    let suggest: () -> Void

    var body: some View {
        ScrollView {
            LazyVStack(alignment: .leading, spacing: 14) {
                ForEach(transcript.segments) { segment in
                    Text(segment.text)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .foregroundStyle(
                            segment.isFinal ? .primary : .secondary
                        )
                        .accessibilityLabel(
                            segment.isFinal
                                ? "Final transcript segment"
                                : "Updating transcript segment"
                        )
                }

                if transcript.hasGap {
                    Label(
                        "Audio gap needs review",
                        systemImage: "exclamationmark.triangle"
                    )
                    .foregroundStyle(.orange)
                }
            }
            .padding()
        }
        .safeAreaInset(edge: .bottom) {
            HStack {
                if isCapturing {
                    Button("Stop", action: stop)
                        .buttonStyle(.borderedProminent)
                } else {
                    Button("Start recording", action: start)
                        .buttonStyle(.borderedProminent)
                        .disabled(isPreparing)
                }

                Button("Suggest", action: suggest)
                    .disabled(!transcript.isComplete)
            }
            .padding()
            .glassEffect(.regular.interactive(), in: .capsule)
            .padding(.horizontal)
        }
        .navigationTitle("Transcript")
    }
}
~~~

Use a plain fallback when a target or accessibility setting makes translucency inappropriate. A button label, accessibility state, and source status must communicate capture even when the material, animation, or color is unavailable.

## Recipe 8: Typed on-device AI proposal

Call Foundation Models only after the source revision is final or explicitly accepted:

~~~swift
import FoundationModels

@Generable
struct TranscriptSuggestion: Sendable, Equatable {
    let title: String
    let summary: String
    let actionCandidates: [String]
}

struct VersionedTranscript: Sendable {
    let revision: UInt64
    let text: String
}

func suggest(
    from source: VersionedTranscript
) async throws -> TranscriptSuggestion {
    let session = LanguageModelSession(
        instructions: "Suggest concise review text from the provided transcript. "
            + "Do not invent facts or claim that an action happened."
    )

    let response = try await session.respond(
        to: "Transcript revision \(source.revision):\n\(source.text)",
        generating: TranscriptSuggestion.self
    )
    return response.content
}
~~~

In a real feature, include a bounded source-range contract, availability/fallback, cancellation, model/prompt revision, and a deterministic validator. Never save `response.content` automatically; display it as a proposal tied to the exact source revision.

## Recipe 9: Pure Swift Testing boundaries

Test the reducer and stale-proposal rule without requiring a microphone:

~~~swift
import Testing

@Test
func oldSessionResultsDoNotMutateCurrentTranscript() {
    var transcript = SourceTranscript(
        revision: 0,
        sessionGeneration: 2
    )

    let result = TranscriptResultSnapshot(
        text: AttributedString("stale"),
        isFinal: true,
        resultsFinalizationTime: .zero
    )

    TranscriptReducer.accept(
        result,
        into: &transcript,
        segmentID: UUID(),
        sessionGeneration: 1
    )

    #expect(transcript.segments.isEmpty)
    #expect(transcript.revision == 0)
}
~~~

Add separate integration tests for real `SpeechAnalyzer`, physical microphone input, route/interruption behavior, asset state, accessibility, and Foundation Models availability. A reducer test proves state logic only.

## Recipe 10: Evidence packet fields

Persist or attach these fields to a test run rather than logging private audio by default:

~~~text
target / build / SDK
device / OS / locale
transcriber configuration revision
asset status and install result
permission state
audio route and interruption events
input fixture identifier and source time range
analyzer/session generation
volatile/final result counts
finalization/cancellation outcome
transcript revision
AI model availability and proposal revision
accessibility settings
archive/TestFlight build identifier
~~~

This packet makes it possible to distinguish “the UI rendered” from “the intended physical device captured and finalized the source.”

## Sources

- [Speech framework](https://developer.apple.com/documentation/speech)
- [SpeechAnalyzer](https://developer.apple.com/documentation/speech/speechanalyzer)
- [SpeechTranscriber](https://developer.apple.com/documentation/speech/speechtranscriber)
- [SpeechTranscriber.ReportingOption](https://developer.apple.com/documentation/speech/speechtranscriber/reportingoption)
- [SpeechTranscriber.ResultAttributeOption](https://developer.apple.com/documentation/speech/speechtranscriber/resultattributeoption)
- [SpeechTranscriber.Result](https://developer.apple.com/documentation/speech/speechtranscriber/result)
- [SpeechModuleResult.resultsFinalizationTime](https://developer.apple.com/documentation/speech/speechmoduleresult/resultsfinalizationtime)
- [SpeechDetector](https://developer.apple.com/documentation/speech/speechdetector)
- [AssetInventory](https://developer.apple.com/documentation/speech/assetinventory)
- [AssetInstallationRequest](https://developer.apple.com/documentation/speech/assetinstallationrequest)
- [AssetInputSequenceProvider](https://developer.apple.com/documentation/speech/assetinputsequenceprovider)
- [CaptureInputSequenceProvider](https://developer.apple.com/documentation/speech/captureinputsequenceprovider)
- [AnalyzerInputConverter](https://developer.apple.com/documentation/speech/analyzerinputconverter)
- [AnalyzerInput](https://developer.apple.com/documentation/speech/analyzerinput)
- [AVAudioApplication](https://developer.apple.com/documentation/avfaudio/avaudioapplication)
- [Requesting audio recording permission](https://developer.apple.com/documentation/avfaudio/avaudioapplication/requestrecordpermission%28completionhandler%3A%29)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Handling audio interruptions](https://developer.apple.com/documentation/avfaudio/handling-audio-interruptions)
- [Responding to audio route changes](https://developer.apple.com/documentation/avfaudio/responding-to-audio-route-changes)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
- [Swift Testing](https://developer.apple.com/documentation/testing)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
