# SwiftUI audio capture and transcription recipes

## Recipe rules

These snippets are route starters for a named app target. They are not compiled
in this documentation workspace and do not prove microphone permission,
hardware routing, AVAudioEngine timing, Speech assets, transcript accuracy,
SoundAnalysis results, AVKit playback, privacy, accessibility, performance,
or release behavior.

Before copying:

1. Confirm the selected iOS 26 SDK signatures and availability.
2. Add and inspect microphone usage descriptions in the processed target.
3. Name the audio source, source revision, file lifetime, locale, module, and
   model/asset revision.
4. Keep audio session, engine, input sequence, transcript, observation,
   candidate, player, and destination state separate.
5. Add cancellation, interruption, route-change, format-change, and stale
   revision handling.
6. Test real iPhone/iPad microphones and release builds; simulator audio and
   a compile are not physical proof.

Tilde fences keep the examples copyable in this Markdown page.

## 1. Request microphone permission with explicit state

Use the current AVAudioApplication permission route in the selected SDK.

~~~swift
import AVFAudio
import SwiftUI

@MainActor
final class MicrophonePermissionModel: ObservableObject {
    enum State: Equatable {
        case undetermined
        case granted
        case denied
    }

    @Published private(set) var state: State = .undetermined

    func refresh() {
        switch AVAudioApplication.shared.recordPermission {
        case .undetermined:
            state = .undetermined
        case .granted:
            state = .granted
        case .denied:
            state = .denied
        @unknown default:
            state = .denied
        }
    }

    func request() async {
        state = await AVAudioApplication.requestRecordPermission()
            ? .granted
            : .denied
    }
}
~~~

Add an accurate NSMicrophoneUsageDescription purpose string. After denial,
offer Settings/import/manual fallback; do not repeatedly request or present a
false listening state.

## 2. Configure and deactivate AVAudioSession

Category, mode, options, and activation must match the feature's real behavior.

~~~swift
import AVFAudio

final class AudioSessionCoordinator {
    private let session = AVAudioSession.sharedInstance()

    func beginCapture() throws {
        try session.setCategory(
            .record,
            mode: .measurement,
            options: []
        )
        try session.setActive(true)
    }

    func endCapture() {
        try? session.setActive(
            false,
            options: [.notifyOthersOnDeactivation]
        )
    }

    func routeSummary() -> String {
        let input = session.currentRoute.inputs
            .map { "\($0.portType.rawValue):\($0.portName)" }
            .joined(separator: ", ")
        let output = session.currentRoute.outputs
            .map { "\($0.portType.rawValue):\($0.portName)" }
            .joined(separator: ", ")
        return "input=\(input) output=\(output)"
    }
}
~~~

If the feature records and plays at once, verify whether play-and-record,
Bluetooth options, voice processing, or another mode is required. Test calls,
Siri, alarms, headphones, Bluetooth disconnect, and screen lock.

## 3. Observe interruptions and route changes

Keep notifications in the audio service and turn them into typed feature
events. The exact notification payload keys should be checked in the target
SDK.

~~~swift
import AVFAudio
import Foundation

enum AudioSystemEvent: Sendable {
    case interruptionBegan
    case interruptionEnded(shouldResume: Bool)
    case routeChanged(String)
}

final class AudioNotificationObserver {
    private var tokens: [NSObjectProtocol] = []

    func start(
        emit: @escaping @Sendable (AudioSystemEvent) -> Void
    ) {
        let center = NotificationCenter.default
        let session = AVAudioSession.sharedInstance()

        tokens.append(
            center.addObserver(
                forName: AVAudioSession.interruptionNotification,
                object: session,
                queue: nil
            ) { notification in
                let type = notification.userInfo?[
                    AVAudioSessionInterruptionTypeKey
                ] as? UInt

                if type == AVAudioSession.InterruptionType.began.rawValue {
                    emit(.interruptionBegan)
                } else {
                    emit(.interruptionEnded(shouldResume: false))
                }
            }
        )

        tokens.append(
            center.addObserver(
                forName: AVAudioSession.routeChangeNotification,
                object: session,
                queue: nil
            ) { notification in
                let reason = notification.userInfo?[
                    AVAudioSessionRouteChangeReasonKey
                ] as? UInt
                emit(.routeChanged(String(describing: reason)))
            }
        )
    }

    func stop() {
        let center = NotificationCenter.default
        tokens.forEach(center.removeObserver)
        tokens.removeAll()
    }
}
~~~

The production handler should inspect the interruption-ended options and
current route before resuming. Do not resume blindly.

## 4. Own AVAudioEngine and its input tap

One service owns the engine, tap, queue, and teardown. Keep the callback small.

~~~swift
import AVFAudio

final class AudioEngineOwner {
    let engine = AVAudioEngine()
    private var tapInstalled = false

    func start(
        onBuffer: @escaping @Sendable (
            AVAudioPCMBuffer,
            AVAudioTime
        ) -> Void
    ) throws {
        let input = engine.inputNode
        let format = input.outputFormat(forBus: 0)
        guard format.sampleRate > 0, format.channelCount > 0 else {
            throw AudioEngineError.invalidInputFormat
        }

        if !tapInstalled {
            input.installTap(
                onBus: 0,
                bufferSize: 2048,
                format: format
            ) { buffer, time in
                onBuffer(buffer, time)
            }
            tapInstalled = true
        }

        try engine.start()
    }

    func stop() {
        if tapInstalled {
            engine.inputNode.removeTap(onBus: 0)
            tapInstalled = false
        }
        engine.stop()
        engine.reset()
    }
}
~~~

Do not allocate unbounded tasks or update SwiftUI directly from the tap. Use a
bounded handoff for Speech, SoundAnalysis, file writing, and waveform samples.
Rebuild the converter/analyzer when the hardware format changes.

## 5. Bounded buffer handoff

This is a generic backpressure sketch. Choose a policy appropriate for the
Speech input contract; do not drop arbitrary speech buffers without measuring
the effect.

~~~swift
actor AudioBufferHandoff {
    private var continuation:
        AsyncStream<AVAudioPCMBuffer>.Continuation?

    func makeStream() -> AsyncStream<AVAudioPCMBuffer> {
        let pair = AsyncStream<AVAudioPCMBuffer>.makeStream(
            of: AVAudioPCMBuffer.self,
            bufferingPolicy: .bufferingNewest(8)
        )
        continuation = pair.continuation
        return pair.stream
    }

    func submit(_ buffer: AVAudioPCMBuffer) {
        _ = continuation?.yield(buffer)
    }

    func finish() {
        continuation?.finish()
        continuation = nil
    }
}
~~~

Record dropped/coalesced input in diagnostics without logging audio. For
speech, prefer the provider/converter lifecycle intended by the selected SDK
when it avoids arbitrary buffer loss.

## 6. Check SpeechTranscriber readiness

Speech readiness includes module availability, locale support, and assets.

~~~swift
import Speech

struct SpeechReadiness: Sendable, Equatable {
    let available: Bool
    let requestedLocale: String
    let supported: Bool
    let installed: Bool
}

func speechReadiness(
    requestedLocale: Locale
) async -> SpeechReadiness {
    let available = SpeechTranscriber.isAvailable
    let supported = SpeechTranscriber.supportedLocales.contains {
        $0.identifier == requestedLocale.identifier
    }
    let installed = SpeechTranscriber.installedLocales.contains {
        $0.identifier == requestedLocale.identifier
    }

    return SpeechReadiness(
        available: available,
        requestedLocale: requestedLocale.identifier,
        supported: supported,
        installed: installed
    )
}
~~~

The exact locale-equivalence helper and AssetInventory status route should be
used in the target. A supported locale may still need a system-managed asset
download. Render supported, downloading, installed, and unsupported states.

## 7. SpeechAnalyzer lifecycle sketch

The analyzer lifecycle is asynchronous and finish-sensitive. The exact
AnalyzerInput/provider signatures should be checked in the selected SDK.

~~~swift
import Speech

struct TranscriptRequest: Sendable, Equatable {
    let sourceID: UUID
    let sourceRevision: Int
    let localeIdentifier: String
}

struct TranscriptResult: Sendable, Equatable {
    let sourceID: UUID
    let sourceRevision: Int
    let text: String
    let isFinal: Bool
}

struct SpeechAnalyzerService {
    func run(
        request: TranscriptRequest,
        emit: @escaping @Sendable (TranscriptResult) -> Void
    ) async throws {
        guard
            let locale = SpeechTranscriber.supportedLocales.first(
                where: { $0.identifier == request.localeIdentifier }
            )
        else {
            throw SpeechRouteError.unsupportedLocale
        }

        let transcriber = SpeechTranscriber(
            locale: locale,
            preset: .timeIndexedProgressiveTranscription
        )
        let analyzer = SpeechAnalyzer(modules: [transcriber])

        let resultTask = Task {
            for try await result in transcriber.results {
                emit(
                    TranscriptResult(
                        sourceID: request.sourceID,
                        sourceRevision: request.sourceRevision,
                        text: String(result.text.characters),
                        isFinal: result.isFinal
                    )
                )
            }
        }

        do {
            let inputSequence = try await makeInputSequence()
            try await analyzer.start(inputSequence: inputSequence)

            // The live capture/file owner feeds input here.
            // It must finish the sequence after Stop or EOF.
            try await analyzer.finalizeAndFinishThroughEndOfInput()
            try await resultTask.value
        } catch {
            resultTask.cancel()
            await analyzer.cancelAndFinishNow()
            throw error
        }
    }
}
~~~

This is a lifecycle recipe, not a drop-in implementation. Do not call the
finalization method while a live producer can still yield. Add source identity,
generation, cancellation, and an explicit input-provider owner.

## 8. Reduce volatile/final transcript results

Store segments by source range or stable segment ID. Do not append every
progressive result.

~~~swift
struct TranscriptSegment: Sendable, Equatable {
    let segmentID: UUID
    let sourceRevision: Int
    let rangeDescription: String
    var text: String
    var isFinal: Bool
}

actor TranscriptStore {
    private var segments: [UUID: TranscriptSegment] = [:]

    func upsert(_ segment: TranscriptSegment) {
        segments[segment.segmentID] = segment
    }

    func finalText() -> String {
        segments.values
            .filter(\.isFinal)
            .sorted { $0.rangeDescription < $1.rangeDescription }
            .map(\.text)
            .joined(separator: " ")
    }
}
~~~

Use typed audio ranges in a real implementation. If a person edits the
transcript, keep that edit as app-owned content and compare transcript revision
before applying later framework results.

## 9. SoundAnalysis observer

Sound analyzers do not keep a strong reference to the results observer. Keep
the observer alive for the analyzer's full lifetime.

~~~swift
import SoundAnalysis

final class SoundResultsObserver: NSObject, SNResultsObserving {
    var onResult: ((SNClassificationResult) -> Void)?
    var onFailure: ((Error) -> Void)?
    var onCompletion: ((Bool) -> Void)?

    func request(
        _ request: SNRequest,
        didProduce result: SNResult
    ) {
        guard let result = result as? SNClassificationResult else { return }
        onResult?(result)
    }

    func request(
        _ request: SNRequest,
        didFailWithError error: Error
    ) {
        onFailure?(error)
    }

    func request(
        _ request: SNRequest,
        didComplete successfully: Bool
    ) {
        onCompletion?(successfully)
    }
}
~~~

The protocol callback spelling can vary with SDK availability. Compile the
observer against the target and retain the same model/request/time-range
metadata used by the app state.

## 10. Analyze a saved audio file

Use SNAudioFileAnalyzer for a file, not a live PCM stream.

~~~swift
import SoundAnalysis

final class SoundFileAnalysisService {
    private var analyzer: SNAudioFileAnalyzer?
    private var observer: SoundResultsObserver?

    func analyze(url: URL) throws {
        let fileAnalyzer = try SNAudioFileAnalyzer(url: url)
        let request = try SNClassifySoundRequest(
            classifierIdentifier: .version1
        )
        let results = SoundResultsObserver()

        results.onResult = { result in
            let top = result.classifications.first
            let label = top?.identifier ?? "unknown"
            let confidence = top?.confidence ?? 0
            // Map label, confidence, and timeRange to source revision state.
            _ = (label, confidence, result.timeRange)
        }

        try fileAnalyzer.add(request, withObserver: results)
        analyzer = fileAnalyzer
        observer = results
        fileAnalyzer.analyze { completed in
            // Completion is not a quality score.
            _ = completed
        }
    }

    func cancel() {
        analyzer?.cancelAnalysis()
        analyzer?.removeAllRequests()
        analyzer = nil
        observer = nil
    }
}
~~~

The file must be app-owned or accessed under an intentional URL/lifetime
policy. Keep raw audio, derived labels, and model revision separate.

## 11. Calculate bounded waveform samples

This sample converts an RMS value into a normalized level. The buffer-to-RMS
calculation should remain outside SwiftUI and be bounded.

~~~swift
struct WaveformSample: Sendable, Equatable {
    let sourceRevision: Int
    let startTime: Double
    let endTime: Double
    let level: Double
}

func levelFromRMS(
    _ rms: Float,
    floor: Float = 0.0001
) -> Double {
    let safe = max(abs(rms), floor)
    let decibels = 20 * log10(safe)
    return min(max(Double((decibels + 60) / 60), 0), 1)
}
~~~

Downsample for the display width. Test long recordings, silence, permission
denial, interruption, Dynamic Type, and reduced motion. The waveform never
replaces Record, Stop, Pause, or an accessible state label.

## 12. Review with VideoPlayer

Keep AVPlayer in the review model and use a stable player lifetime.

~~~swift
import AVKit
import SwiftUI

struct RecordingReviewView: View {
    let player: AVPlayer
    let title: String
    let onEdit: () -> Void
    let onSave: () -> Void

    var body: some View {
        VStack(spacing: 16) {
            VideoPlayer(player: player)
                .accessibilityLabel(Text(title))
                .frame(minHeight: 120)

            HStack {
                Button("Edit", action: onEdit)
                Spacer()
                Button("Save", action: onSave)
                    .buttonStyle(.borderedProminent)
            }
        }
        .padding()
        .onDisappear {
            player.pause()
        }
    }
}
~~~

Use AVPlayerViewController when its native controller surface is required.
Player success does not prove transcript, classifier, privacy, or export
success.

## 13. Typed Foundation Models audio candidate

Feed only bounded, user-approved deterministic results. Keep the candidate
reviewable and source-revision-scoped.

~~~swift
struct AudioReviewInput: Codable, Sendable {
    let sourceID: UUID
    let sourceRevision: Int
    let transcriptRevision: Int
    let finalizedText: String
    let soundLabels: [String]
}

struct AudioReviewCandidate: Codable, Sendable, Equatable {
    let candidateID: UUID
    let sourceID: UUID
    let sourceRevision: Int
    let transcriptRevision: Int
    let title: String
    let summary: String
    let tags: [String]
}

enum AudioCandidateState: Equatable {
    case unavailable
    case generating(sourceRevision: Int, transcriptRevision: Int)
    case ready(AudioReviewCandidate)
    case stale(AudioReviewCandidate)
    case rejected
    case committed(AudioReviewCandidate)
    case failed(String)
}
~~~

The exact Foundation Models session and guided-generation APIs are SDK- and
device-sensitive. Validate schema, length, tags, source revisions, and
prohibited claims before showing Apply. Use the ordinary save/export path after
acceptance.

## 14. Revision-safe candidate coordinator

Use both audio source revision and transcript revision.

~~~swift
@MainActor
final class AudioCandidateCoordinator: ObservableObject {
    @Published private(set) var state: AudioCandidateState = .unavailable

    private var sourceID: UUID?
    private var sourceRevision = 0
    private var transcriptRevision = 0
    private var task: Task<Void, Never>?

    func generate(
        sourceID: UUID,
        sourceRevision: Int,
        transcriptRevision: Int,
        operation: @Sendable @escaping () async throws
            -> AudioReviewCandidate
    ) {
        task?.cancel()
        self.sourceID = sourceID
        self.sourceRevision = sourceRevision
        self.transcriptRevision = transcriptRevision
        state = .generating(
            sourceRevision: sourceRevision,
            transcriptRevision: transcriptRevision
        )

        task = Task { [weak self] in
            do {
                let candidate = try await operation()
                try Task.checkCancellation()
                guard
                    let self,
                    self.sourceID == sourceID,
                    self.sourceRevision == sourceRevision,
                    self.transcriptRevision == transcriptRevision
                else { return }
                state = .ready(candidate)
            } catch is CancellationError {
                // The source or transcript changed.
            } catch {
                guard let self, self.sourceID == sourceID else { return }
                state = .failed("The suggestion could not be created.")
            }
        }
    }

    func sourceChanged(
        id: UUID,
        sourceRevision: Int,
        transcriptRevision: Int
    ) {
        task?.cancel()
        task = nil
        sourceID = id
        self.sourceRevision = sourceRevision
        self.transcriptRevision = transcriptRevision
        state = .unavailable
    }
}
~~~

## 15. Liquid Glass recording/review shell

Keep the media/transcript primary and use the glass group for current actions.

~~~swift
struct AudioReviewShell<Content: View>: View {
    let content: Content
    let phaseLabel: String
    let isRecording: Bool
    let canStop: Bool
    let canSave: Bool
    let onStop: () -> Void
    let onSave: () -> Void

    var body: some View {
        ZStack(alignment: .bottom) {
            content
                .frame(maxWidth: .infinity, maxHeight: .infinity)

            HStack {
                Label(
                    phaseLabel,
                    systemImage: isRecording
                        ? "waveform"
                        : "waveform.slash"
                )
                .accessibilityValue(
                    isRecording ? "Active" : "Inactive"
                )

                Spacer()

                Button("Stop", action: onStop)
                    .disabled(!canStop)
                Button("Save", action: onSave)
                    .disabled(!canSave)
                    .buttonStyle(.borderedProminent)
            }
            .padding()
            .glassEffect()
        }
    }
}
~~~

The exact Liquid Glass modifier and availability must be checked in the
selected SDK. Provide an opaque fallback and test reduced transparency,
Dynamic Type, VoiceOver, keyboard, pointer, light/dark content, and
interruption/error states.

## 16. Explicit audio destination

Keep app save, export/share, and discard separate.

~~~swift
enum AudioDestination: String, CaseIterable, Identifiable {
    case app
    case export
    case share
    case discard

    var id: String { rawValue }

    var title: String {
        switch self {
        case .app: "Save in this app"
        case .export: "Export audio and transcript"
        case .share: "Share a copy"
        case .discard: "Discard"
        }
    }
}

struct AudioDestinationView: View {
    @Binding var destination: AudioDestination
    let onContinue: () -> Void

    var body: some View {
        Form {
            Picker("Destination", selection: $destination) {
                ForEach(AudioDestination.allCases) { value in
                    Text(value.title).tag(value)
                }
            }
            Button("Continue", action: onContinue)
        }
        .navigationTitle("Choose destination")
    }
}
~~~

Only report success after the selected destination finishes. Preserve the
app-owned source when export/share is cancelled or fails.

## 17. Acceptance fixture

Use a deterministic fixture to test stale work and review boundaries.

~~~swift
struct AudioAcceptanceFixture: Equatable, Sendable {
    let sourceID: UUID
    let sourceRevision: Int
    let transcriptRevision: Int
    let permission: String
    let route: String
    let analyzer: String
    let transcript: String
    let soundObservation: String
    let candidate: String
    let destination: String
}

let readyForReview = AudioAcceptanceFixture(
    sourceID: UUID(uuidString: "00000000-0000-0000-0000-000000000002")!,
    sourceRevision: 4,
    transcriptRevision: 7,
    permission: "granted",
    route: "built-in-microphone",
    analyzer: "speech-assets-installed",
    transcript: "finalized-and-user-reviewable",
    soundObservation: "time-ranged-low-confidence-candidate",
    candidate: "typed-and-ready-for-accept-or-discard",
    destination: "choose-app-export-share-or-discard"
)
~~~

Acceptance should assert:

- a new recording invalidates old transcript/sound/AI work;
- an interruption does not leave a false listening state;
- an input-format change rebuilds the analyzer path;
- volatile text does not become canonical without finalization/review;
- user edits survive later framework results;
- sound labels retain time, confidence, and model identity;
- AI output cannot apply when source/transcript revisions differ;
- file finalization and reopen occur before “Saved”;
- VoiceOver, Dynamic Type, keyboard, RTL, and reduced-effects states remain usable.

## Sources

- [Speech](https://developer.apple.com/documentation/speech)
- [SpeechAnalyzer](https://developer.apple.com/documentation/speech/speechanalyzer)
- [SpeechTranscriber](https://developer.apple.com/documentation/speech/speechtranscriber)
- [SpeechTranscriber.Preset](https://developer.apple.com/documentation/speech/speechtranscriber/preset)
- [SpeechTranscriber.Result](https://developer.apple.com/documentation/speech/speechtranscriber/result)
- [AssetInventory](https://developer.apple.com/documentation/speech/assetinventory)
- [AssetInputSequenceProvider](https://developer.apple.com/documentation/speech/assetinputsequenceprovider)
- [CaptureInputSequenceProvider](https://developer.apple.com/documentation/speech/captureinputsequenceprovider)
- [AnalyzerInput](https://developer.apple.com/documentation/speech/analyzerinput)
- [AnalyzerInputConverter](https://developer.apple.com/documentation/speech/analyzerinputconverter)
- [Bringing advanced speech-to-text capabilities to your app](https://developer.apple.com/documentation/speech/bringing-advanced-speech-to-text-capabilities-to-your-app)
- [AVAudioApplication](https://developer.apple.com/documentation/avfaudio/avaudioapplication)
- [Request record permission](https://developer.apple.com/documentation/avfaudio/avaudioapplication/requestrecordpermission%28completionhandler%3A%29)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Handling audio interruptions](https://developer.apple.com/documentation/AVFAudio/handling-audio-interruptions)
- [Responding to audio route changes](https://developer.apple.com/documentation/AVFAudio/responding-to-audio-route-changes)
- [AVAudioEngine](https://developer.apple.com/documentation/avfaudio/avaudioengine)
- [AVAudioNode](https://developer.apple.com/documentation/avfaudio/avaudionode)
- [AVAudioInputNode](https://developer.apple.com/documentation/avfaudio/avaudioinputnode)
- [AVAudioPCMBuffer](https://developer.apple.com/documentation/avfaudio/avaudiopcmbuffer)
- [AVAudioFile](https://developer.apple.com/documentation/avfaudio/avaudiofile)
- [AVKit](https://developer.apple.com/documentation/avkit)
- [VideoPlayer](https://developer.apple.com/documentation/avkit/videoplayer)
- [Sound Analysis](https://developer.apple.com/documentation/soundanalysis)
- [SNAudioStreamAnalyzer](https://developer.apple.com/documentation/soundanalysis/snaudiostreamanalyzer)
- [SNAudioFileAnalyzer](https://developer.apple.com/documentation/soundanalysis/snaudiofileanalyzer)
- [SNClassifySoundRequest](https://developer.apple.com/documentation/soundanalysis/snclassifysoundrequest)
- [SNClassificationResult](https://developer.apple.com/documentation/soundanalysis/snclassificationresult)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adding intelligent app features with generative models](https://developer.apple.com/documentation/foundationmodels/adding-intelligent-app-features-with-generative-models)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
