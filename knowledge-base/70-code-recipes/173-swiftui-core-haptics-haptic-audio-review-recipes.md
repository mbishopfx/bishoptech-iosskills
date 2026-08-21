# SwiftUI Core Haptics and haptic-audio code recipes

These recipes are compile-oriented starting points for iOS 26. Add Core Haptics code to the correct app/game target, verify signatures against the final SDK, and exercise every physical result on an iPhone. The simulator is useful for state and pattern tests but cannot prove a person felt a haptic.

## 1. Capability-first service

```swift
import CoreHaptics
import Observation

@MainActor
@Observable
final class HapticFeedbackService {
    private(set) var supportsHaptics = false
    private(set) var supportsAudio = false
    private(set) var isReady = false
    private(set) var lastStoppedReason: String?
    private(set) var lastError: String?

    private var engine: CHHapticEngine?
    private var playerGeneration = 0

    var engineForRecipeUse: CHHapticEngine? {
        engine
    }

    func prepare() {
        let capability = CHHapticEngine.capabilitiesForHardware()
        supportsHaptics = capability.supportsHaptics
        supportsAudio = capability.supportsAudio

        guard supportsHaptics || supportsAudio else {
            isReady = false
            return
        }

        do {
            let newEngine = try CHHapticEngine()
            newEngine.resetHandler = { [weak self] in
                Task { @MainActor in
                    self?.handleReset()
                }
            }
            newEngine.stoppedHandler = { [weak self] reason in
                Task { @MainActor in
                    self?.handleStopped(reason)
                }
            }

            try newEngine.start()
            engine = newEngine
            isReady = true
            lastError = nil
        } catch {
            isReady = false
            lastError = String(describing: error)
        }
    }

    func stop() {
        guard let engine else { return }
        engine.stop(completionHandler: nil)
        isReady = false
        playerGeneration &+= 1
    }

    private func handleReset() {
        // Existing players are no longer trusted after a media-server reset.
        playerGeneration &+= 1
        isReady = false
        prepare()
    }

    private func handleStopped(_ reason: CHHapticEngine.StoppedReason) {
        lastStoppedReason = String(describing: reason)
        isReady = false
        playerGeneration &+= 1
    }
}
```

Set the engine handlers before starting. A production service may choose to defer restart until the next user interaction instead of restarting immediately inside reset recovery; the important part is that the next pattern uses a valid engine and fresh players.

## 2. Play a transient confirmation

```swift
import CoreHaptics

extension HapticFeedbackService {
    func playConfirmation() {
        guard supportsHaptics else { return }
        guard let engine else {
            prepare()
            return
        }

        do {
            let intensity = CHHapticEventParameter(
                parameterID: .hapticIntensity,
                value: 0.65
            )
            let sharpness = CHHapticEventParameter(
                parameterID: .hapticSharpness,
                value: 0.35
            )
            let event = CHHapticEvent(
                eventType: .hapticTransient,
                parameters: [intensity, sharpness],
                relativeTime: 0
            )
            let pattern = try CHHapticPattern(
                events: [event],
                parameters: []
            )
            let player = try engine.makePlayer(with: pattern)
            try player.start(atTime: 0)
        } catch {
            lastError = String(describing: error)
        }
    }
}
```

Call this at the semantic commit point—for example, after a save succeeds—not from a view’s `body` or every state update. Pair it with a visible and accessible “Saved” state.

## 3. Continuous interaction with generation and cancellation

```swift
import CoreHaptics

@MainActor
final class ContinuousHapticInteraction {
    private let service: HapticFeedbackService
    private var player: CHHapticPatternPlayer?
    private var generation = 0

    init(service: HapticFeedbackService) {
        self.service = service
    }

    func begin() throws {
        guard service.supportsHaptics else { return }
        guard let engine = service.engineForRecipeUse else { return }

        generation &+= 1
        let event = CHHapticEvent(
            eventType: .hapticContinuous,
            parameters: [
                .init(parameterID: .hapticIntensity, value: 0.25),
                .init(parameterID: .hapticSharpness, value: 0.25)
            ],
            relativeTime: 0,
            duration: 30
        )
        let pattern = try CHHapticPattern(events: [event], parameters: [])
        player = try engine.makePlayer(with: pattern)
        try player?.start(atTime: 0)
    }

    func update(intensity: Float, sharpness: Float) throws {
        guard let player else { return }
        let parameters = [
            CHHapticDynamicParameter(
                parameterID: .hapticIntensity,
                value: min(max(intensity, 0), 1),
                relativeTime: 0
            ),
            CHHapticDynamicParameter(
                parameterID: .hapticSharpness,
                value: min(max(sharpness, 0), 1),
                relativeTime: 0
            )
        ]
        try player.sendParameters(parameters, atTime: 0)
    }

    func end() throws {
        try player?.stop(atTime: 0)
        player = nil
    }

    func cancel() throws {
        try player?.cancel()
        player = nil
        generation &+= 1
    }
}
```

`engineForRecipeUse` is an intentional integration point. Keep the engine strongly owned by the service and expose it only through a narrow feature adapter; do not make the view own the engine. Rate-limit `update` calls for high-frequency gestures and stop/cancel on gesture cancellation, focus loss, and view dismissal.

## 4. AHAP bundle playback

```swift
import CoreHaptics

extension HapticFeedbackService {
    func playBundledAHAP(named name: String) {
        guard supportsHaptics || supportsAudio else { return }
        guard let engine,
              let url = Bundle.main.url(forResource: name, withExtension: "ahap")
        else {
            lastError = "Missing AHAP resource or haptic capability"
            return
        }

        do {
            try engine.playPattern(from: url)
        } catch {
            lastError = String(describing: error)
        }
    }
}
```

Keep AHAP resources in the intended target bundle. Validate the file’s `Version`, `Pattern`, event parameters, dynamic parameters, curves, and audio-resource references in CI or a development tool. Test the behavior of missing/defaulted and unsupported keys on the minimum supported physical device.

## 5. Advanced player for looping and audio sync

```swift
import CoreHaptics

@MainActor
func makeAdvancedLoop(
    engine: CHHapticEngine,
    event: CHHapticEvent
) throws -> CHHapticAdvancedPatternPlayer {
    let pattern = try CHHapticPattern(events: [event], parameters: [])
    let player = try engine.makeAdvancedPlayer(with: pattern)
    player.loopEnabled = true
    player.loopEnd = 1.0
    player.playbackRate = 1.0
    try player.start(atTime: 0)
    return player
}

@MainActor
func stopAdvancedPlayer(_ player: CHHapticAdvancedPatternPlayer) {
    do {
        try player.stop(atTime: 0)
    } catch {
        // Record the error and use the visual/audio fallback.
    }
}
```

Use `pause(atTime:)`, `resume(atTime:)`, and `seek(toOffset:)` only when the interaction needs them. A loop must have a user-visible stop policy and a lifecycle owner. For synchronized custom audio, register/own the audio resource and prove the physical timing on every supported route.

## 6. Register an audio resource for an audio event

```swift
import CoreHaptics

@MainActor
func makeAudioHapticPattern(
    engine: CHHapticEngine,
    audioURL: URL
) throws -> CHHapticPattern {
    let resourceID = try engine.registerAudioResource(
        audioURL,
        options: [
            CHHapticAudioResourceKeyLoopEnabled: false,
            CHHapticAudioResourceKeyUseVolumeEnvelope: true
        ]
    )

    let haptic = CHHapticEvent(
        eventType: .hapticTransient,
        parameters: [
            .init(parameterID: .hapticIntensity, value: 0.45),
            .init(parameterID: .hapticSharpness, value: 0.2)
        ],
        relativeTime: 0
    )
    let audio = CHHapticEvent(
        audioResourceID: resourceID,
        parameters: [],
        relativeTime: 0
    )

    return try CHHapticPattern(events: [haptic, audio], parameters: [])
}
```

The audio resource, route, volume, interruption, and fallback are part of the feature contract. Do not assume a haptic-only test proves the paired audio behavior.

## 7. SwiftUI gesture bridge

```swift
import SwiftUI

struct HapticDragSurface: View {
    let service: HapticFeedbackService
    @State private var interaction: ContinuousHapticInteraction?
    @State private var value: CGFloat = 0.5

    var body: some View {
        RoundedRectangle(cornerRadius: 28)
            .fill(.blue.opacity(0.18))
            .overlay {
                Text("Value \(value, format: .number.precision(.fractionLength(2)))")
            }
            .contentShape(Rectangle())
            .gesture(
                DragGesture()
                    .onChanged { gesture in
                        if interaction == nil {
                            let next = ContinuousHapticInteraction(service: service)
                            try? next.begin()
                            interaction = next
                        }

                        value = min(max(gesture.location.x / 300, 0), 1)
                        try? interaction?.update(
                            intensity: Float(value),
                            sharpness: Float(1 - value)
                        )
                    }
                    .onEnded { _ in
                        try? interaction?.end()
                        interaction = nil
                        service.playConfirmation()
                    }
            )
            .onDisappear {
                try? interaction?.cancel()
                interaction = nil
            }
            .padding()
            .glassEffect(.regular.interactive(), in: .rect(cornerRadius: 28))
            .accessibilityValue(value, format: .number.precision(.fractionLength(2)))
    }
}
```

This is a gesture-shape recipe, not a claim that every device supports the same haptic. The visible value and accessibility value remain correct when `service.supportsHaptics` is false.

## 8. Typed AI proposal and hard validation

```swift
import FoundationModels

@Generable
struct HapticProposal {
    var eventKind: String
    var intensity: Double
    var sharpness: Double
    var duration: Double
    var explanation: String
}

struct SafeHapticProposal {
    let isContinuous: Bool
    let intensity: Float
    let sharpness: Float
    let duration: TimeInterval
    let explanation: String
}

func validate(_ proposal: HapticProposal) -> SafeHapticProposal? {
    let kind = proposal.eventKind.lowercased()
    guard kind == "transient" || kind == "continuous" else { return nil }
    guard (0...1).contains(proposal.intensity),
          (0...1).contains(proposal.sharpness),
          (0.01...5).contains(proposal.duration),
          !proposal.explanation.isEmpty
    else { return nil }

    return SafeHapticProposal(
        isContinuous: kind == "continuous",
        intensity: Float(proposal.intensity),
        sharpness: Float(proposal.sharpness),
        duration: proposal.duration,
        explanation: proposal.explanation
    )
}
```

The model should receive a semantic event description and capability summary, not private sensor traces or an uncontrolled physical-device command. Require preview, Stop, Edit, and Apply actions. If the model is unavailable, use a deterministic catalog pattern.

## 9. Swift Testing state policy

```swift
import Testing

struct HapticPolicyTests {
    @Test("unsupported hardware uses a visible fallback")
    func fallbackIsNotAPlaybackClaim() {
        let supportsHaptics = false
        let visualFallbackIsAvailable = true

        #expect(!supportsHaptics)
        #expect(visualFallbackIsAvailable)
    }

    @Test("AI proposal values are bounded before pattern creation")
    func proposalValuesAreValidated() {
        let proposal = HapticProposal(
            eventKind: "transient",
            intensity: 0.6,
            sharpness: 0.3,
            duration: 0.08,
            explanation: "A restrained confirmation"
        )

        #expect(validate(proposal) != nil)
    }
}
```

Add physical integration tests for engine start, reset, stoppage, actual player playback, audio routes, and observer-perceived timing. Unit tests cannot prove tactile output.

## Sources

- [Core Haptics](https://developer.apple.com/documentation/corehaptics)
- [CHHapticEngine](https://developer.apple.com/documentation/corehaptics/chhapticengine)
- [CHHapticDeviceCapability](https://developer.apple.com/documentation/corehaptics/chhapticdevicecapability)
- [CHHapticEngine.capabilitiesForHardware()](https://developer.apple.com/documentation/corehaptics/chhapticengine/capabilitiesforhardware%28%29)
- [CHHapticPattern](https://developer.apple.com/documentation/corehaptics/chhapticpattern)
- [CHHapticEvent](https://developer.apple.com/documentation/corehaptics/chhapticevent)
- [CHHapticEvent.EventType](https://developer.apple.com/documentation/corehaptics/chhapticevent/eventtype)
- [CHHapticEvent.ParameterID](https://developer.apple.com/documentation/corehaptics/chhapticevent/parameterid)
- [CHHapticEventParameter](https://developer.apple.com/documentation/corehaptics/chhapticeventparameter)
- [CHHapticDynamicParameter](https://developer.apple.com/documentation/corehaptics/chhapticdynamicparameter)
- [CHHapticParameterCurve](https://developer.apple.com/documentation/corehaptics/chhapticparametercurve)
- [CHHapticPatternPlayer](https://developer.apple.com/documentation/corehaptics/chhapticpatternplayer)
- [CHHapticAdvancedPatternPlayer](https://developer.apple.com/documentation/corehaptics/chhapticadvancedpatternplayer)
- [Preparing your app to play haptics](https://developer.apple.com/documentation/corehaptics/preparing-your-app-to-play-haptics)
- [Playing a custom haptic pattern from a file](https://developer.apple.com/documentation/corehaptics/playing-a-custom-haptic-pattern-from-a-file)
- [Representing haptic patterns in AHAP files](https://developer.apple.com/documentation/corehaptics/representing-haptic-patterns-in-ahap-files)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
