# SwiftUI AVSpeechSynthesizer spoken-output review recipes

These are compile-oriented sketches for the focused [AVSpeechSynthesizer review](../42-framework-deep-dives/125-swiftui-avspeech-synthesis-spoken-output-review.md). They separate source text, utterance configuration, queue ownership, delegate events, audio-session policy, buffer export, SwiftUI state, and optional on-device AI.

Compile selected symbols against the final iOS 26 SDK. These recipes do not prove that a person heard audio, that a route was private, that a far-end call participant heard an uplink, or that a signed release behaves like a debug build.

## Recipe 1: Configure a voice and utterance

Set parameters before enqueueing and retain the source mapping outside the UIKit object:

~~~swift
import AVFAudio

struct SpokenUtterance: Sendable, Identifiable {
    let id: UUID
    let sourceRevision: UInt64
    let sourceText: String
    let localeIdentifier: String
}

func makeUtterance(
    _ item: SpokenUtterance,
    rate: Float,
    pitch: Float,
    volume: Float
) -> AVSpeechUtterance {
    let utterance = AVSpeechUtterance(string: item.sourceText)
    utterance.voice = AVSpeechSynthesisVoice(
        language: item.localeIdentifier
    )
    utterance.rate = rate
    utterance.pitchMultiplier = pitch
    utterance.volume = volume
    utterance.prefersAssistiveTechnologySettings = true
    return utterance
}
~~~

If the preferred voice is unavailable, make the fallback visible and record it. Do not treat the localized voice display name as a stable identity.

## Recipe 2: Retain one queue owner

Keep the synthesizer and delegate alive for the queue’s lifetime:

~~~swift
import AVFAudio

struct ReadAloudState: Sendable, Equatable {
    enum Status: Sendable, Equatable {
        case idle
        case queued
        case speaking
        case paused
        case interrupted
        case finished
        case cancelled
        case failed(String)
    }

    var generation: UInt64 = 0
    var status: Status = .idle
    var currentUtteranceID: UUID?
    var queueCount = 0
    var highlightedRange: NSRange?
}

@MainActor
final class ReadAloudCoordinator: NSObject {
    private let synthesizer = AVSpeechSynthesizer()
    private(set) var state = ReadAloudState()
    private var utteranceIDs: [ObjectIdentifier: UUID] = [:]

    override init() {
        super.init()
        synthesizer.delegate = self
    }

    func enqueue(
        _ item: SpokenUtterance,
        rate: Float = AVSpeechUtteranceDefaultSpeechRate,
        pitch: Float = 1.0,
        volume: Float = 1.0
    ) {
        let utterance = makeUtterance(
            item,
            rate: rate,
            pitch: pitch,
            volume: volume
        )
        utteranceIDs[ObjectIdentifier(utterance)] = item.id
        synthesizer.speak(utterance)
        state.currentUtteranceID = item.id
        state.queueCount += 1
        state.status = .queued
    }

    func pause() {
        guard synthesizer.pauseSpeaking(at: .word) else { return }
        state.status = .paused
    }

    func resume() {
        guard synthesizer.continueSpeaking() else { return }
        state.status = .speaking
    }

    func stop() {
        state.generation &+= 1
        _ = synthesizer.stopSpeaking(at: .immediate)
        state.queueCount = 0
        state.currentUtteranceID = nil
        state.highlightedRange = nil
        state.status = .cancelled
    }
}
~~~

The delegate methods below are shown separately so a production coordinator can add generation/source checks and make stale callbacks harmless.

## Recipe 3: Map delegate progress to source text

Use the delegate’s range or marker callback instead of a timer:

~~~swift
import AVFAudio

extension ReadAloudCoordinator: AVSpeechSynthesizerDelegate {
    func speechSynthesizer(
        _ synthesizer: AVSpeechSynthesizer,
        didStart utterance: AVSpeechUtterance
    ) {
        state.status = .speaking
    }

    func speechSynthesizer(
        _ synthesizer: AVSpeechSynthesizer,
        willSpeakRangeOfSpeechString characterRange: NSRange,
        utterance: AVSpeechUtterance
    ) {
        state.highlightedRange = characterRange
    }

    func speechSynthesizer(
        _ synthesizer: AVSpeechSynthesizer,
        didPause utterance: AVSpeechUtterance
    ) {
        state.status = .paused
    }

    func speechSynthesizer(
        _ synthesizer: AVSpeechSynthesizer,
        didContinue utterance: AVSpeechUtterance
    ) {
        state.status = .speaking
    }

    func speechSynthesizer(
        _ synthesizer: AVSpeechSynthesizer,
        didFinish utterance: AVSpeechUtterance
    ) {
        state.queueCount = max(0, state.queueCount - 1)
        state.highlightedRange = nil
        state.status = state.queueCount == 0 ? .finished : .queued
    }

    func speechSynthesizer(
        _ synthesizer: AVSpeechSynthesizer,
        didCancel utterance: AVSpeechUtterance
    ) {
        state.queueCount = 0
        state.highlightedRange = nil
        state.status = .cancelled
    }
}
~~~

`NSRange` uses UTF-16 offsets. Convert it against the exact `speechString`/attributed source that created the utterance, and test emoji, combining marks, links, and right-to-left text. The example omits that mapping for clarity.

## Recipe 4: App-managed audio session

Use app-managed mode when the product needs explicit audio coordination:

~~~swift
import AVFAudio

func configureAppManagedSpeech(
    synthesizer: AVSpeechSynthesizer
) throws {
    let session = AVAudioSession.sharedInstance()
    try session.setCategory(
        .playback,
        mode: .spokenAudio,
        options: [.duckOthers]
    )
    try session.setActive(true)
    synthesizer.usesApplicationAudioSession = true
}

func deactivateAppManagedSpeech() {
    try? AVAudioSession.sharedInstance().setActive(
        false,
        options: .notifyOthersOnDeactivation
    )
}
~~~

If the feature does not need to coordinate the session, test `usesApplicationAudioSession = false` and let the system manage its separate speech session. Do not mix the two policies in one generation without recording the transition.

## Recipe 5: Observe interruptions and route changes

Keep notification observation in the long-lived audio owner:

~~~swift
import AVFAudio

final class SpeechAudioObserver {
    private var tokens: [NSObjectProtocol] = []

    func start(
        onInterruption: @escaping (Notification) -> Void,
        onRouteChange: @escaping (Notification) -> Void
    ) {
        let center = NotificationCenter.default
        tokens.append(
            center.addObserver(
                forName: AVAudioSession.interruptionNotification,
                object: AVAudioSession.sharedInstance(),
                queue: .main,
                using: onInterruption
            )
        )
        tokens.append(
            center.addObserver(
                forName: AVAudioSession.routeChangeNotification,
                object: AVAudioSession.sharedInstance(),
                queue: .main,
                using: onRouteChange
            )
        )
    }

    func stop() {
        let center = NotificationCenter.default
        for token in tokens {
            center.removeObserver(token)
        }
        tokens.removeAll()
    }
}
~~~

The callback should preserve the queue/source, mark the generation interrupted, inspect the current route and interruption reason, and resume only according to user intent and product policy.

## Recipe 6: Generate buffers instead of direct speech

Use the `write` API when the product needs a buffer consumer or file/export route:

~~~swift
import AVFAudio

final class SpeechBufferCollector {
    private var buffers: [AVAudioPCMBuffer] = []

    func collect(
        utterance: AVSpeechUtterance,
        synthesizer: AVSpeechSynthesizer
    ) {
        synthesizer.write(utterance) { [weak self] buffer in
            guard let pcm = buffer as? AVAudioPCMBuffer else { return }
            self?.buffers.append(pcm)
        }
    }

    func finish() -> [AVAudioPCMBuffer] {
        defer { buffers.removeAll() }
        return buffers
    }
}
~~~

The real collector needs a bounded buffer writer, synchronization, format checks, cancellation, finalization, and a destination/file policy. A callback proves generated data only; it does not prove that a speaker played it.

## Recipe 7: Explicit telephony-uplink guard

Keep the communication route separate from generic read-aloud:

~~~swift
import AVFAudio

enum SpokenOutputDestination: Sendable, Equatable {
    case localOnly
    case activeCallWithExplicitConsent
}

@MainActor
func configureDestination(
    _ destination: SpokenOutputDestination,
    synthesizer: AVSpeechSynthesizer,
    hasActiveCall: Bool,
    consented: Bool
) -> Bool {
    switch destination {
    case .localOnly:
        synthesizer.mixToTelephonyUplink = false
        return true
    case .activeCallWithExplicitConsent:
        guard hasActiveCall, consented else {
            synthesizer.mixToTelephonyUplink = false
            return false
        }
        synthesizer.mixToTelephonyUplink = true
        return true
    }
}
~~~

In production, add current communication-service permission/entitlement gates, a visible confirmation, call lifecycle observation, and a physical local/far-end test. Never let an AI response enable this property on its own.

## Recipe 8: SwiftUI read-aloud control group

Keep the source text primary and use glass for functional controls:

~~~swift
import SwiftUI

struct ReadAloudControls: View {
    let state: ReadAloudState
    let play: () -> Void
    let pause: () -> Void
    let stop: () -> Void

    var body: some View {
        HStack {
            switch state.status {
            case .speaking:
                Button("Pause", action: pause)
            case .paused:
                Button("Resume", action: play)
            default:
                Button("Read aloud", action: play)
            }

            Button("Stop", action: stop)
                .disabled(state.status == .idle)
        }
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Read aloud controls")
        .glassEffect(.regular.interactive(), in: .capsule)
    }
}
~~~

Add an accessible textual status next to the controls. Test the same view with Reduce Transparency and VoiceOver; the material and animation must not be required to understand the state.

## Recipe 9: Typed AI text proposal

Generate text separately, then hand only accepted text to the synthesizer:

~~~swift
import FoundationModels

@Generable
struct SpokenProposal: Sendable, Equatable {
    let title: String
    let spokenText: String
    let caution: String?
}

func makeSpokenProposal(
    from acceptedSource: String
) async throws -> SpokenProposal {
    let session = LanguageModelSession(
        instructions: "Create a concise spoken proposal. "
            + "Do not claim that an action happened."
    )
    let response = try await session.respond(
        to: acceptedSource,
        generating: SpokenProposal.self
    )
    return response.content
}
~~~

Store the model/source revision and require an explicit review/accept action before calling `makeUtterance` or `speak`. If the source changes, invalidate the proposal.

## Recipe 10: Pure queue and stale-state tests

Test source/queue state independently of audio hardware:

~~~swift
import Testing

@Test
func replacingSourceIncrementsGeneration() {
    let first = SpokenUtterance(
        id: UUID(),
        sourceRevision: 1,
        sourceText: "Old text",
        localeIdentifier: "en-US"
    )
    let second = SpokenUtterance(
        id: UUID(),
        sourceRevision: 2,
        sourceText: "New text",
        localeIdentifier: "en-US"
    )

    #expect(first.sourceRevision < second.sourceRevision)
}

@Test
func localOnlyDestinationDisablesTelephonyUplink() {
    let synthesizer = AVSpeechSynthesizer()
    let accepted = MainActor.assumeIsolated {
        configureDestination(
            .localOnly,
            synthesizer: synthesizer,
            hasActiveCall: true,
            consented: true
        )
    }

    #expect(accepted)
    #expect(!synthesizer.mixToTelephonyUplink)
}
~~~

Add device tests for voice availability, physical output, interruption/route recovery, buffer finalization, and active-call behavior. These unit tests prove only policy state.

## Sources

- [Speech synthesis](https://developer.apple.com/documentation/avfaudio/speech-synthesis)
- [AVSpeechSynthesizer](https://developer.apple.com/documentation/avfaudio/avspeechsynthesizer)
- [AVSpeechSynthesizerDelegate](https://developer.apple.com/documentation/avfaudio/avspeechsynthesizerdelegate)
- [AVSpeechUtterance](https://developer.apple.com/documentation/avfaudio/avspeechutterance)
- [AVSpeechSynthesisVoice](https://developer.apple.com/documentation/avfaudio/avspeechsynthesisvoice)
- [AVSpeechUtterance.rate](https://developer.apple.com/documentation/avfaudio/avspeechutterance/rate)
- [AVSpeechUtterance.pitchMultiplier](https://developer.apple.com/documentation/avfaudio/avspeechutterance/pitchmultiplier)
- [AVSpeechUtterance.prefersAssistiveTechnologySettings](https://developer.apple.com/documentation/avfaudio/avspeechutterance/prefersassistivetechnologysettings)
- [AVSpeechSynthesizer.usesApplicationAudioSession](https://developer.apple.com/documentation/avfaudio/avspeechsynthesizer/usesapplicationaudiosession)
- [AVSpeechSynthesizer.mixToTelephonyUplink](https://developer.apple.com/documentation/avfaudio/avspeechsynthesizer/mixtotelephonyuplink)
- [AVSpeechSynthesizer.outputChannels](https://developer.apple.com/documentation/avfaudio/avspeechsynthesizer/outputchannels)
- [AVSpeechSynthesisProviderAudioUnit](https://developer.apple.com/documentation/avfaudio/avspeechsynthesisprovideraudiounit)
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
