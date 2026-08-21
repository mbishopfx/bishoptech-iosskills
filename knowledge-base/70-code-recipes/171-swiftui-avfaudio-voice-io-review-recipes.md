# SwiftUI AVFAudio voice I/O review recipes

These are compile-oriented shapes for a full-duplex `AVAudioEngine` voice-I/O route. Validate exact signatures and target availability against the final iOS 26 SDK. The snippets keep the input callback, audio session, engine, voice-processing, model, and SwiftUI boundaries separate. They do not prove physical microphone/speaker behavior or far-end delivery.

## 1. Voice-I/O state model

Use state that distinguishes observed hardware/audio facts from user intent and AI output.

~~~swift
import AVFAudio
import Foundation

struct VoiceIOState: Sendable, Equatable {
    enum Phase: Sendable, Equatable {
        case stopped
        case requestingPermission
        case preparing
        case listening
        case processing
        case speakingLocally
        case speakingToCall
        case interrupted
        case routeUnavailable
        case failed(String)
    }

    var phase: Phase = .stopped
    var inputPortName: String?
    var outputPortName: String?
    var inputSampleRate: Double = 0
    var inputChannels = 0
    var outputSampleRate: Double = 0
    var outputChannels = 0
    var voiceProcessingEnabled = false
    var graphRevision: UInt64 = 0
    var sessionRevision: UInt64 = 0
}
~~~

Do not make `phase == .listening` mean that the agent has a transcript or that a remote party heard anything. Keep those facts in separate state models.

## 2. Request record permission

`AVAudioApplication` owns app-level audio operations such as record permission. Request permission as a user-initiated step and preserve denial/settings recovery.

~~~swift
import AVFAudio

enum MicrophoneAccess: Sendable, Equatable {
    case unknown
    case denied
    case granted
}

func requestMicrophoneAccess() async -> MicrophoneAccess {
    let granted = await withCheckedContinuation { continuation in
        AVAudioApplication.requestRecordPermission { allowed in
            continuation.resume(returning: allowed)
        }
    }
    return granted ? .granted : .denied
}
~~~

The exact async import may vary by SDK. Keep the operation behind an app-owned permission adapter so the SwiftUI view does not own platform callbacks directly.

## 3. Configure a duplex session

Configure category/mode/options before activation and activate close to the explicit start action.

~~~swift
import AVFAudio

func configureVoiceSession() throws -> AVAudioSession {
    let session = AVAudioSession.sharedInstance()
    try session.setCategory(
        .playAndRecord,
        mode: .voiceChat,
        options: [.allowBluetooth, .allowBluetoothA2DP]
    )
    try session.setActive(true)
    return session
}
~~~

Choose options for the actual product and route; do not copy this combination into a measurement or private playback product. `.voiceChat` is a communication mode, and the system may limit routes or apply Bluetooth HFP behavior. Record the post-activation category/mode/options and current route.

## 4. Inspect input and output hardware formats

Check the I/O nodes after session activation and before installing a tap or starting the graph.

~~~swift
import AVFAudio

struct HardwareFormats: Sendable, Equatable {
    let input: AVAudioFormat
    let output: AVAudioFormat

    var inputIsUsable: Bool {
        input.sampleRate > 0 && input.channelCount > 0
    }
}

func hardwareFormats(for engine: AVAudioEngine) -> HardwareFormats {
    HardwareFormats(
        input: engine.inputNode.inputFormat(forBus: 0),
        output: engine.outputNode.outputFormat(forBus: 0)
    )
}
~~~

Treat `inputIsUsable == false` as a route/hardware state. Do not install a tap or start SpeechAnalyzer with a zero-format input. If the graph uses a processing format that differs from hardware, record the conversion and its latency.

## 5. Configure voice processing on the I/O node

`AVAudioIONode` exposes the high-level enable/disable operation and current state.

~~~swift
import AVFAudio

func setVoiceProcessing(
    enabled: Bool,
    engine: AVAudioEngine
) throws -> Bool {
    // Stop or quiesce the graph according to the product’s lifecycle policy
    // before changing I/O processing.
    try engine.inputNode.setVoiceProcessingEnabled(enabled)
    return engine.inputNode.isVoiceProcessingEnabled
}
~~~

Some products configure the output node or a different I/O node according to the selected graph. Validate the node and route after the change. Do not assume enabling voice processing preserves the same format, channel count, latency, or Bluetooth route.

## 6. Build one engine owner

The coordinator owns session, engine, input/output nodes, and recovery. The input tap hands off bounded work to an actor or stream.

~~~swift
import AVFAudio
import Foundation

@MainActor
final class VoiceIOCoordinator: ObservableObject {
    @Published private(set) var state = VoiceIOState()

    let engine = AVAudioEngine()
    private var inputTapInstalled = false
    private var session: AVAudioSession?
    private var generation: UInt64 = 0

    func start() throws {
        session = try configureVoiceSession()
        let formats = hardwareFormats(for: engine)
        guard formats.inputIsUsable else {
            state.phase = .routeUnavailable
            return
        }

        generation &+= 1
        state.graphRevision &+= 1
        state.sessionRevision &+= 1
        state.inputSampleRate = formats.input.sampleRate
        state.inputChannels = Int(formats.input.channelCount)
        state.outputSampleRate = formats.output.sampleRate
        state.outputChannels = Int(formats.output.channelCount)

        try installInputTapIfNeeded(format: formats.input, generation: generation)
        engine.prepare()
        try engine.start()
        state.voiceProcessingEnabled = engine.inputNode.isVoiceProcessingEnabled
        state.phase = .listening
    }

    func stop() {
        generation &+= 1
        engine.inputNode.removeTap(onBus: 0)
        inputTapInstalled = false
        engine.stop()
        state.phase = .stopped
    }

    private func installInputTapIfNeeded(
        format: AVAudioFormat,
        generation: UInt64
    ) throws {
        guard !inputTapInstalled else { return }
        engine.inputNode.installTap(
            onBus: 0,
            bufferSize: 1_024,
            format: format
        ) { [weak self] buffer, time in
            // Copy or enqueue a bounded packet. Never await a model or UI here.
            self?.receiveInput(buffer: buffer, time: time, generation: generation)
        }
        inputTapInstalled = true
    }

    private func receiveInput(
        buffer: AVAudioPCMBuffer,
        time: AVAudioTime,
        generation: UInt64
    ) {
        guard generation == self.generation else { return }
        // Send a bounded, owned representation to an actor/stream.
    }
}
~~~

The tap callback is not a SwiftUI or Foundation Models boundary. The production handoff should avoid retaining a mutable framework buffer beyond its documented lifetime; copy only what the downstream owner needs.

## 7. Observe interruption and route changes

Use one observer owner and revalidate formats/processing after a change.

~~~swift
import AVFAudio
import Foundation

final class VoiceAudioObservers {
    private var tokens: [NSObjectProtocol] = []

    func start(
        session: AVAudioSession = .sharedInstance(),
        onInterruption: @escaping (Notification) -> Void,
        onRouteChange: @escaping (Notification) -> Void,
        onMediaReset: @escaping (Notification) -> Void
    ) {
        let center = NotificationCenter.default
        tokens.append(center.addObserver(
            forName: AVAudioSession.interruptionNotification,
            object: session,
            queue: .main,
            using: onInterruption
        ))
        tokens.append(center.addObserver(
            forName: AVAudioSession.routeChangeNotification,
            object: session,
            queue: .main,
            using: onRouteChange
        ))
        tokens.append(center.addObserver(
            forName: AVAudioSession.mediaServicesWereResetNotification,
            object: session,
            queue: .main,
            using: onMediaReset
        ))
    }

    func stop() {
        let center = NotificationCenter.default
        tokens.forEach(center.removeObserver)
        tokens.removeAll()
    }
}
~~~

On media-service reset, reinitialize audio objects and session configuration and wait for user action before restarting capture or processing. On interruption end, check the system’s resume option and the product’s user intent.

## 8. Inspect the current route

Use a redacted, human-readable route snapshot for SwiftUI and a fuller diagnostic record for testing.

~~~swift
import AVFAudio

struct RouteSnapshot: Sendable, Equatable {
    let inputs: [String]
    let outputs: [String]
    let inputUIDs: [String]
    let outputUIDs: [String]
}

func routeSnapshot(_ session: AVAudioSession = .sharedInstance()) -> RouteSnapshot {
    let route = session.currentRoute
    return RouteSnapshot(
        inputs: route.inputs.map(\.portName),
        outputs: route.outputs.map(\.portName),
        inputUIDs: route.inputs.map(\.uid),
        outputUIDs: route.outputs.map(\.uid)
    )
}
~~~

Keep UIDs out of normal accessibility copy and logs that leave the device. Use them only in controlled diagnostics when route identity is necessary.

## 9. Voice I/O Audio Unit properties

Use lower-level Voice I/O properties only behind a small adapter and only after confirming the selected I/O unit and scope/element.

~~~swift
import AudioToolbox

struct VoiceIOPropertyPolicy: Sendable {
    var bypassProcessing = false
    var enableAGC = true
    var muteOutput = false
}

// The actual AudioUnitSetProperty calls require the selected Voice I/O unit,
// scope, element, data size, and an error/OSStatus policy. Keep them out of the
// SwiftUI view and prove each property with a physical acoustic fixture.
~~~

`kAUVoiceIOProperty_BypassVoiceProcessing`, `kAUVoiceIOProperty_VoiceProcessingEnableAGC`, and `kAUVoiceIOProperty_MuteOutput` are Audio Toolbox Voice I/O properties. They are not interchangeable with microphone permission, engine stop, a UI mute state, or far-end call delivery.

## 10. SwiftUI voice controls

Use text and accessible actions alongside the Liquid Glass control group.

~~~swift
import SwiftUI

struct VoiceIOControls: View {
    let phase: VoiceIOState.Phase
    let routeText: String
    let voiceProcessingEnabled: Bool
    let start: () -> Void
    let stop: () -> Void
    let mute: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label(routeText, systemImage: "mic.and.signal.meter")
                .font(.subheadline)

            Text(phaseText)
                .font(.headline)

            HStack {
                Button("Start", systemImage: "mic.fill", action: start)
                Button("Stop", systemImage: "stop.fill", action: stop)
                Button("Mute", systemImage: "mic.slash.fill", action: mute)
            }
            .buttonStyle(.borderedProminent)

            Text(voiceProcessingEnabled ? "Voice processing on" : "Voice processing off")
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .padding()
        .glassEffect(.regular.interactive(), in: .rect(cornerRadius: 20))
        .accessibilityElement(children: .contain)
    }

    private var phaseText: String {
        switch phase {
        case .listening: return "Listening"
        case .processing: return "Processing"
        case .speakingLocally: return "Speaking on this device"
        case .speakingToCall: return "Speaking to the call"
        case .interrupted: return "Paused for interruption"
        case .routeUnavailable: return "Audio route unavailable"
        case .stopped: return "Stopped"
        default: return "Preparing audio"
        }
    }
}
~~~

Provide a solid fallback for reduced transparency and keep the stop/mute actions outside the AI response path.

## 11. Typed local response proposal

The host can pass a bounded transcript/intent revision to Foundation Models and keep the output reviewable.

~~~swift
import FoundationModels

@Generable
struct VoiceResponseProposal {
    @Guide(description: "A concise response for the declared local or call destination")
    var text: String

    @Guide(description: "Whether the response needs user confirmation before speaking")
    var requiresConfirmation: Bool
}

func outputPolicy(
    proposal: VoiceResponseProposal,
    destination: Destination,
    userAccepted: Bool
) -> Bool {
    switch destination {
    case .local:
        return !proposal.requiresConfirmation || userAccepted
    case .call:
        return userAccepted
    }
}

enum Destination: Sendable {
    case local
    case call
}
~~~

The policy must still check active call state, permission, source revision, and stop/mute state. Model output is not evidence that the microphone captured the intended words.

## 12. Swift Testing boundaries

Use deterministic tests for session-state reduction, generation invalidation, format validation, route copy, and output policy. Exercise microphone/speaker/voice-processing behavior on physical devices.

~~~swift
import Testing

struct VoiceIOPolicyTests {
    @Test func callOutputRequiresAcceptance() {
        let proposal = VoiceResponseProposal(
            text: "Proposed response",
            requiresConfirmation: false
        )
        #expect(!outputPolicy(
            proposal: proposal,
            destination: .call,
            userAccepted: false
        ))
    }
}
~~~

Integration tests should cover permission, route, format, voice processing, interruption, media reset, local output, call/uplink, accessibility, archive, TestFlight, and physical evidence.

## Sources

- [Audio Engine](https://developer.apple.com/documentation/avfaudio/audio-engine)
- [AVAudioEngine](https://developer.apple.com/documentation/avfaudio/avaudioengine)
- [AVAudioIONode](https://developer.apple.com/documentation/avfaudio/avaudioionode)
- [AVAudioInputNode](https://developer.apple.com/documentation/avfaudio/avaudioinputnode)
- [AVAudioOutputNode](https://developer.apple.com/documentation/avfaudio/avaudiooutputnode)
- [AVAudioEngine.inputNode](https://developer.apple.com/documentation/avfaudio/avaudioengine/inputnode)
- [Using voice processing](https://developer.apple.com/documentation/avfaudio/using-voice-processing)
- [Audio Unit Voice I/O](https://developer.apple.com/documentation/audiotoolbox/audio-unit-voice-i-o)
- [kAUVoiceIOProperty_BypassVoiceProcessing](https://developer.apple.com/documentation/audiotoolbox/kauvoiceioproperty_bypassvoiceprocessing)
- [kAUVoiceIOProperty_VoiceProcessingEnableAGC](https://developer.apple.com/documentation/audiotoolbox/kauvoiceioproperty_voiceprocessingenableagc)
- [kAUVoiceIOProperty_MuteOutput](https://developer.apple.com/documentation/audiotoolbox/kauvoiceioproperty_muteoutput)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [AVAudioSession.Mode.voiceChat](https://developer.apple.com/documentation/avfaudio/avaudiosession/mode-swift.struct/voicechat)
- [AVAudioApplication](https://developer.apple.com/documentation/avfaudio/avaudioapplication)
- [Handling audio interruptions](https://developer.apple.com/documentation/avfaudio/handling-audio-interruptions)
- [Responding to audio route changes](https://developer.apple.com/documentation/avfaudio/responding-to-audio-route-changes)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
