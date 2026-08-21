# SoundAnalysis audio-classification recipes

These are compile-oriented route sketches for built-in and custom sound classification, live PCM microphone analysis, saved-file analysis, observer lifecycle, confidence reduction, audio-session permission, bounded AI review, and evidence capture.

They are not compiled in this documentation-only workspace and do not prove microphone permission, physical input, analyzer quality, model accuracy, accessibility, privacy, or release readiness. Confirm the exact API signatures and availability in the selected SDK.

Before copying:

1. Add NSMicrophoneUsageDescription when the target accesses a microphone.
2. Use the current AVAudioApplication permission API in the selected SDK.
3. Keep a strong observer reference.
4. Recreate SNAudioStreamAnalyzer when the input PCM format changes.
5. Keep audio-tap callbacks bounded and move UI/domain work out of the tap.

## Recipe 1: Define model and observation state

Keep model revision, confidence, and time range explicit:

~~~swift
import Foundation

struct SoundModelSpec: Sendable, Equatable {
    let identifier: String
    let revision: String
    let labels: Set<String>
    let minimumConfidence: Double
    let stableWindows: Int
}

struct SoundCandidate: Sendable, Equatable {
    let identifier: String
    let confidence: Double
    let startSeconds: Double
    let endSeconds: Double
    let modelRevision: String
}

enum SoundState: Sendable, Equatable {
    case idle
    case permissionRequired
    case unavailable
    case preparing
    case listening
    case candidate(SoundCandidate)
    case ambiguous([SoundCandidate])
    case unknown
    case interrupted
    case failed(String)
}
~~~

The framework result should be reduced to this domain model before SwiftUI renders it.

## Recipe 2: Create a built-in classifier request

The built-in request uses a classifier identifier:

~~~swift
import SoundAnalysis

func makeBuiltInSoundRequest() throws -> SNClassifySoundRequest {
    let identifier = SNClassifierIdentifier.version1
    let request = try SNClassifySoundRequest(
        classifierIdentifier: identifier
    )
    request.overlapFactor = 0.5
    return request
}
~~~

Confirm the allowed window duration and overlap policy for the selected model and target. Inspect knownClassifications and keep only labels the app has explicitly reviewed.

## Recipe 3: Create a custom Core ML sound request

Xcode generates a wrapper for a bundled sound-classifier model:

~~~swift
import CoreML
import SoundAnalysis

func makeCustomSoundRequest() throws -> SNClassifySoundRequest {
    let configuration = MLModelConfiguration()
    let classifier = try SoundClassifier(configuration: configuration)
    let request = try SNClassifySoundRequest(
        mlModel: classifier.model
    )
    return request
}
~~~

SoundClassifier is a fixture for the generated wrapper name. Verify the model resource is in the intended target and record its revision. A bundled model is not proof of accuracy on the target device.

## Recipe 4: Keep a strong results observer

Sound analyzers do not keep a strong reference to the observer. Keep one in the analysis coordinator:

~~~swift
import SoundAnalysis

final class SoundResultsObserver: NSObject, SNResultsObserving {
    let onResult: (SNResult) -> Void
    let onFailure: (Error) -> Void
    let onComplete: () -> Void

    init(
        onResult: @escaping (SNResult) -> Void,
        onFailure: @escaping (Error) -> Void,
        onComplete: @escaping () -> Void
    ) {
        self.onResult = onResult
        self.onFailure = onFailure
        self.onComplete = onComplete
    }

    func request(
        _ request: SNRequest,
        didProduce result: SNResult
    ) {
        onResult(result)
    }

    func request(
        _ request: SNRequest,
        didFailWithError error: Error
    ) {
        onFailure(error)
    }

    func requestDidComplete(_ request: SNRequest) {
        onComplete()
    }
}
~~~

The protocol’s generated existential spelling may differ by SDK. Preserve the lifecycle: result, failure, and completion are distinct paths.

## Recipe 5: Analyze a saved audio file

Use a file analyzer for a scoped URL:

~~~swift
import SoundAnalysis

final class SoundFileAnalyzer {
    private var analyzer: SNAudioFileAnalyzer?
    private var observer: SoundResultsObserver?

    func start(
        url: URL,
        request: SNRequest,
        onResult: @escaping (SNResult) -> Void
    ) throws {
        let analyzer = try SNAudioFileAnalyzer(url: url)
        let observer = SoundResultsObserver(
            onResult: onResult,
            onFailure: { error in
                _ = error
            },
            onComplete: {}
        )
        try analyzer.add(request, withObserver: observer)
        self.analyzer = analyzer
        self.observer = observer
        analyzer.analyze { [weak self] finished in
            guard finished else {
                return
            }
            self?.analyzer = nil
            self?.observer = nil
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

Keep the URL scope and file-retention policy outside the analyzer. The completion result indicates whether analysis reached the end; it does not establish classification quality.

## Recipe 6: Request current microphone permission

Use the current AVAudioApplication route:

~~~swift
import AVFAudio

enum MicrophoneState: Equatable {
    case undetermined
    case granted
    case denied
}

func microphoneState() -> MicrophoneState {
    switch AVAudioApplication.shared.recordPermission {
    case .undetermined:
        return .undetermined
    case .granted:
        return .granted
    case .denied:
        return .denied
    @unknown default:
        return .denied
    }
}

func requestMicrophone(
    completion: @escaping (MicrophoneState) -> Void
) {
    AVAudioApplication.requestRecordPermission { granted in
        let state: MicrophoneState = granted ? .granted : .denied
        DispatchQueue.main.async {
            completion(state)
        }
    }
}
~~~

The exact AVAudioApplication API is SDK-sensitive. Include NSMicrophoneUsageDescription in the target, and do not start the engine before the app has a usable permission/input state.

## Recipe 7: Configure a live input session

Configure the audio session for input and verify the hardware format:

~~~swift
import AVFAudio

struct InputConfiguration {
    let session: AVAudioSession
    let engine: AVAudioEngine
    let inputNode: AVAudioInputNode
    let format: AVAudioFormat
}

func makeInputConfiguration() throws -> InputConfiguration {
    let session = AVAudioSession.sharedInstance()
    try session.setCategory(.record, mode: .measurement, options: [])
    try session.setActive(true)

    guard session.isInputAvailable else {
        throw NSError(
            domain: "SoundInput",
            code: 1,
            userInfo: [NSLocalizedDescriptionKey: "No input route"]
        )
    }

    let engine = AVAudioEngine()
    let inputNode = engine.inputNode
    let format = inputNode.inputFormat(forBus: 0)
    guard format.sampleRate > 0, format.channelCount > 0 else {
        throw NSError(
            domain: "SoundInput",
            code: 2,
            userInfo: [NSLocalizedDescriptionKey: "Invalid input format"]
        )
    }
    return InputConfiguration(
        session: session,
        engine: engine,
        inputNode: inputNode,
        format: format
    )
}
~~~

If a different category or mode better matches the product, record it in the target register. Audio-session activation is a separate proof step from analyzer creation.

## Recipe 8: Start a live stream analyzer

The analyzer format must match the input tap:

~~~swift
import AVFAudio
import SoundAnalysis

final class LiveSoundAnalyzer {
    private var audioEngine: AVAudioEngine?
    private var inputNode: AVAudioInputNode?
    private var streamAnalyzer: SNAudioStreamAnalyzer?
    private var request: SNRequest?
    private var observer: SoundResultsObserver?

    func start(
        configuration: InputConfiguration,
        request: SNRequest,
        onResult: @escaping (SNResult) -> Void
    ) throws {
        let analyzer = SNAudioStreamAnalyzer(
            format: configuration.format
        )
        let observer = SoundResultsObserver(
            onResult: onResult,
            onFailure: { error in
                _ = error
            },
            onComplete: {}
        )
        try analyzer.add(request, withObserver: observer)

        let inputNode = configuration.inputNode
        inputNode.installTap(
            onBus: 0,
            bufferSize: 2_048,
            format: configuration.format
        ) { [weak analyzer] buffer, time in
            guard time.isSampleTimeValid else {
                return
            }
            analyzer?.analyze(
                buffer,
                atAudioFramePosition: time.sampleTime
            )
        }

        configuration.engine.prepare()
        try configuration.engine.start()
        audioEngine = configuration.engine
        self.inputNode = inputNode
        streamAnalyzer = analyzer
        self.request = request
        self.observer = observer
    }

    func stop(session: AVAudioSession) {
        inputNode?.removeTap(onBus: 0)
        audioEngine?.stop()
        streamAnalyzer?.removeAllRequests()
        streamAnalyzer = nil
        request = nil
        observer = nil
        audioEngine = nil
        inputNode = nil
        try? session.setActive(
            false,
            options: .notifyOthersOnDeactivation
        )
    }
}
~~~

The audio tap should not perform blocking I/O, network calls, or unbounded logging. Use a serial analysis owner or actor for reduction and UI delivery.

## Recipe 9: Rebuild after an input format change

A stream analyzer is tied to its input format:

~~~swift
struct InputFormatKey: Equatable, Sendable {
    let sampleRate: Double
    let channelCount: UInt32
}

func formatKey(_ format: AVAudioFormat) -> InputFormatKey {
    InputFormatKey(
        sampleRate: format.sampleRate,
        channelCount: format.channelCount
    )
}
~~~

When the audio route or hardware format changes, stop the tap/analyzer, read the new input format, create a new SNAudioStreamAnalyzer, add the request and strong observer again, then restart. Mark the transition as reconfiguring rather than merging incompatible time ranges.

## Recipe 10: Reduce a classification result

Convert the top candidates to a bounded domain event:

~~~swift
import SoundAnalysis

func candidate(
    from result: SNResult,
    modelRevision: String
) -> SoundCandidate? {
    guard let result = result as? SNClassificationResult,
          let top = result.classifications.first
    else {
        return nil
    }

    let start = result.timeRange.start.seconds
    let end = result.timeRange.end.seconds
    return SoundCandidate(
        identifier: top.identifier,
        confidence: Double(top.confidence),
        startSeconds: start,
        endSeconds: end,
        modelRevision: modelRevision
    )
}
~~~

Apply label allowlists, confidence thresholds, temporal stability, and unknown/ambiguous states before any user-visible or external action.

## Recipe 11: Keep an AI proposal bounded

AI can summarize approved results but cannot create sensor truth:

~~~swift
struct SoundTimelineContext: Sendable, Equatable {
    let recordingID: String
    let modelRevision: String
    let candidates: [SoundCandidate]
}

enum SoundProposal: Sendable, Equatable {
    case draftSummary
    case addReviewedTag(
        label: String,
        startSeconds: Double,
        endSeconds: Double
    )
}

struct SoundProposalValidator {
    let approvedLabels: Set<String>

    func validate(
        _ proposal: SoundProposal,
        context: SoundTimelineContext,
        confirmed: Bool
    ) throws {
        switch proposal {
        case .draftSummary:
            return
        case let .addReviewedTag(label, start, end):
            guard confirmed,
                  approvedLabels.contains(label),
                  start >= 0,
                  end >= start,
                  context.candidates.contains(where: {
                      $0.identifier == label &&
                      $0.startSeconds <= end &&
                      $0.endSeconds >= start
                  })
            else {
                throw NSError(
                    domain: "SoundProposal",
                    code: 1
                )
            }
        }
    }
}
~~~

Do not send raw PCM, private recordings, or unreviewed model output to an external service by default.

## Recipe 12: Keep a semantic evidence record

Record outcomes without raw audio:

~~~swift
struct SoundEvidence: Sendable, Equatable {
    let modelRevision: String
    let source: String
    let inputFormat: String
    let label: String?
    let confidence: Double?
    let state: String
    let physicalDevice: String
    let timestamp: Date
}
~~~

Pair the record with the signed model/resource, target configuration, fixture provenance, physical route, accessibility result, and privacy test. A candidate line is not proof of a physical sound or domain action.

## Sources

- [Sound Analysis](https://developer.apple.com/documentation/soundanalysis)
- [SNClassifySoundRequest](https://developer.apple.com/documentation/soundanalysis/snclassifysoundrequest)
- [SNAudioStreamAnalyzer](https://developer.apple.com/documentation/soundanalysis/snaudiostreamanalyzer)
- [SNAudioFileAnalyzer](https://developer.apple.com/documentation/soundanalysis/snaudiofileanalyzer)
- [SNResultsObserving](https://developer.apple.com/documentation/soundanalysis/snresultsobserving)
- [SNClassificationResult](https://developer.apple.com/documentation/soundanalysis/snclassificationresult)
- [Classifying Sounds in an Audio Stream](https://developer.apple.com/documentation/soundanalysis/classifying-sounds-in-an-audio-stream)
- [Classifying Sounds in an Audio File](https://developer.apple.com/documentation/soundanalysis/classifying-sounds-in-an-audio-file)
- [MLSoundClassifier](https://developer.apple.com/documentation/createml/mlsoundclassifier)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [AVAudioEngine](https://developer.apple.com/documentation/avfaudio/avaudioengine)
- [AVAudioNode](https://developer.apple.com/documentation/avfaudio/avaudionode)
- [AVAudioInputNode](https://developer.apple.com/documentation/avfaudio/avaudioinputnode)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [AVAudioApplication](https://developer.apple.com/documentation/avfaudio/avaudioapplication)
- [NSMicrophoneUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsmicrophoneusagedescription)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
