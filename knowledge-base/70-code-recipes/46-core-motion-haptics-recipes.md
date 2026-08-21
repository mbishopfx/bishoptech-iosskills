# Core Motion and Core Haptics code recipes

These are compile-oriented route sketches for a selected iOS target. They are not compiled in this documentation-only workspace and do not prove sensor availability, authorization, physical-device accuracy, haptic output, accessibility, energy, or release readiness. Verify API signatures, actor isolation, Info.plist keys, and availability in Xcode.

## Recipe 1: own a device-motion session

Keep the manager and stop policy in one owner. Do not create a new manager or task for every view update.

~~~swift
import CoreMotion

final class DeviceMotionSession {
    private let manager = CMMotionManager()
    private let queue: OperationQueue = {
        let queue = OperationQueue()
        queue.qualityOfService = .userInitiated
        queue.maxConcurrentOperationCount = 1
        return queue
    }()

    func start(
        referenceFrame: CMAttitudeReferenceFrame? = nil,
        handler: @escaping (CMDeviceMotion) -> Void
    ) {
        guard manager.isDeviceMotionAvailable else {
            return
        }

        manager.deviceMotionUpdateInterval = 1.0 / 30.0
        if let referenceFrame,
           CMMotionManager.availableAttitudeReferenceFrames.contains(referenceFrame) {
            manager.startDeviceMotionUpdates(
                using: referenceFrame,
                to: queue,
                withHandler: { motion, error in
                    guard error == nil, let motion else { return }
                    handler(motion)
                }
            )
        } else {
            manager.startDeviceMotionUpdates(to: queue) { motion, error in
                guard error == nil, let motion else { return }
                handler(motion)
            }
        }
    }

    func stop() {
        manager.stopDeviceMotionUpdates()
    }
}
~~~

The handler should timestamp, normalize, filter, and coalesce before updating the UI. Add a real cancellation/interrupt path and ensure the usage description is in the target.

## Recipe 2: use a bounded accelerometer stream

Raw streams need a sampling and retention decision:

~~~swift
import CoreMotion

final class AccelerometerSession {
    private let manager = CMMotionManager()
    private let queue = OperationQueue()

    func start(onSample: @escaping (Double, Double, Double, TimeInterval) -> Void) {
        guard manager.isAccelerometerAvailable else { return }
        manager.accelerometerUpdateInterval = 1.0 / 20.0
        manager.startAccelerometerUpdates(to: queue) { data, error in
            guard error == nil, let data else { return }
            onSample(
                data.acceleration.x,
                data.acceleration.y,
                data.acceleration.z,
                data.timestamp
            )
        }
    }

    func stop() {
        manager.stopAccelerometerUpdates()
    }
}
~~~

The queue and callback are a route sketch. Add finite windows, dropped-sample counters, a filter/calibration version, and a manual fallback. Do not retain raw motion forever just because it is easy to append to an array.

## Recipe 3: query or stream pedometer data

Use the smallest time range and preserve a clear source window:

~~~swift
import CoreMotion

final class PedometerRoute {
    private let pedometer = CMPedometer()

    func query(from start: Date, to end: Date, completion: @escaping (CMPedometerData?) -> Void) {
        guard CMPedometer.isStepCountingAvailable else {
            completion(nil)
            return
        }

        pedometer.queryPedometerData(from: start, to: end) { data, error in
            guard error == nil else {
                completion(nil)
                return
            }
            completion(data)
        }
    }

    func stop() {
        pedometer.stopUpdates()
    }
}
~~~

Add the selected privacy/authorization handling and test no data, denied access, date changes, live updates, and device availability. A pedometer result should be presented as a measurement with a time range, not as an identity or health conclusion.

## Recipe 4: create a semantic SwiftUI feedback route

Use SwiftUI sensoryFeedback when the interaction matches a system semantic:

~~~swift
import SwiftUI

struct LevelControl: View {
    @State private var level = 0

    var body: some View {
        Stepper("Level \(level)", value: $level, in: 0...10)
            .sensoryFeedback(.selection, trigger: level)
    }
}
~~~

The visible label/value remains the source of truth. Check the current SDK overload and supported feedback cases. Do not make a haptic the only indication of a changed level.

## Recipe 5: play a custom transient Core Haptics pattern

Use a custom engine only when a semantic system feedback route is insufficient:

~~~swift
import CoreHaptics

final class HapticPlayer {
    private var engine: CHHapticEngine?
    private var player: CHHapticPatternPlayer?

    func prepare() throws {
        guard CHHapticEngine.capabilitiesForHardware().supportsHaptics else {
            return
        }

        let engine = try CHHapticEngine()
        let event = CHHapticEvent(
            eventType: .hapticTransient,
            parameters: [
                CHHapticEventParameter(parameterID: .hapticIntensity, value: 0.6),
                CHHapticEventParameter(parameterID: .hapticSharpness, value: 0.4)
            ],
            relativeTime: 0
        )
        let pattern = try CHHapticPattern(events: [event], parameters: [])
        player = try engine.makePlayer(with: pattern)
        self.engine = engine
        try engine.start()
    }

    func play() throws {
        try player?.start(atTime: CHHapticTimeImmediate)
    }

    func stop() {
        player?.stop(atTime: CHHapticTimeImmediate)
        engine?.stop(completionHandler: nil)
    }
}
~~~

Core Haptics names and overloads must be compiled against the selected SDK. Add engine reset/stopped handlers, interruption handling, capability fallback, audio-route decisions, and a visible/accessibility-equivalent result. Do not play a long continuous pattern from a high-frequency sensor callback.

## Recipe 6: map a stable threshold to one haptic

Keep feedback downstream from a debounced state transition:

~~~swift
struct ThresholdState {
    var isInside: Bool
    var lastHapticAt: Date?
}

func nextThresholdState(
    sample: Double,
    threshold: ClosedRange<Double>,
    previous: ThresholdState,
    now: Date
) -> ThresholdState {
    let inside = threshold.contains(sample)
    let crossed = inside != previous.isInside
    let canPulse = previous.lastHapticAt.map {
        now.timeIntervalSince($0) > 0.5
    } ?? true

    return ThresholdState(
        isInside: inside,
        lastHapticAt: crossed && canPulse ? now : previous.lastHapticAt
    )
}
~~~

The example is deterministic state logic, not a claim that this threshold is appropriate. Test jitter, oscillation, stale samples, device rotation, Reduce Motion, and no-haptics output. Pair the pulse with a visible state change.

## Recipe 7: represent a bounded AI sensor proposal

Pass a time-bounded derived summary instead of an unlimited raw stream:

~~~swift
struct MotionWindow: Sendable {
    var start: Date
    var end: Date
    var sampleCount: Int
    var dominantFeatures: [Double]
    var calibrationVersion: String
}

struct HapticProposal: Sendable {
    var style: String
    var intensity: Double
    var sharpness: Double
    var reason: String
    var sourceWindow: MotionWindow
    var needsConfirmation: Bool
}

func validate(_ proposal: HapticProposal, currentWindow: MotionWindow) -> Bool {
    proposal.needsConfirmation
        && proposal.intensity >= 0
        && proposal.intensity <= 1
        && proposal.sharpness >= 0
        && proposal.sharpness <= 1
        && proposal.sourceWindow.start >= currentWindow.start
        && proposal.sourceWindow.end <= currentWindow.end
}
~~~

The model session, model availability, prompt/versioning, and local privacy policy belong in the app’s AI adapter. The validator stays deterministic. Never let the model start a sensor session, emit an unbounded haptic loop, or make a medical/safety/identity claim.

## Recipe 8: make the UI state accessible

Expose a textual and semantic projection of the physical state:

~~~swift
struct SensorStatusView: View {
    let state: SensorState

    var body: some View {
        VStack(alignment: .leading) {
            Text(state.title)
            Text(state.detail)
                .foregroundStyle(.secondary)
            if let value = state.accessibleValue {
                Text(value)
                    .accessibilityLabel("Current sensor value")
            }
            Button(state.isRunning ? "Stop" : "Start") {
                // Start/stop the owned session.
            }
        }
        .accessibilityElement(children: .contain)
    }
}
~~~

Provide the same result without animation or haptics, respect Reduce Motion and reduced transparency, and keep VoiceOver focus stable when live values update.

## Recipe 9: proof fixtures

~~~swift
enum SensorFixture {
    case unavailable
    case denied
    case available
    case noisy
    case interrupted
    case stableThreshold
    case engineReset
    case hapticsUnsupported
    case aiUnavailable
}

func reduce(_ fixture: SensorFixture) -> SensorState {
    fatalError("Implement in the selected target")
}
~~~

Exercise availability, permission, start/stop, no data, stale data, interruption, hardware removal, sensor noise, threshold debounce, haptic reset, Reduce Motion, VoiceOver, and AI fallback before the physical test.

## Sources

- [Core Motion](https://developer.apple.com/documentation/coremotion/)
- [CMMotionManager](https://developer.apple.com/documentation/coremotion/cmmotionmanager)
- [CMDeviceMotion](https://developer.apple.com/documentation/coremotion/cmdevicemotion)
- [CMPedometer](https://developer.apple.com/documentation/coremotion/cmpedometer)
- [Core Haptics](https://developer.apple.com/documentation/corehaptics)
- [CHHapticEngine](https://developer.apple.com/documentation/corehaptics/chhapticengine)
- [CHHapticPattern](https://developer.apple.com/documentation/corehaptics/chhapticpattern)
- [CHHapticEvent](https://developer.apple.com/documentation/corehaptics/chhapticevent)
- [Playing a single-tap haptic pattern](https://developer.apple.com/documentation/corehaptics/playing-a-single-tap-haptic-pattern)
- [SensoryFeedback](https://developer.apple.com/documentation/swiftui/sensoryfeedback)
- [Motion HIG](https://developer.apple.com/design/human-interface-guidelines/motion)
- [Playing haptics](https://developer.apple.com/design/human-interface-guidelines/playing-haptics)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
