# SwiftUI Core Motion sensor-route review recipes

These are compile-oriented starting points for an iOS 26 target. Use one owned `CMMotionManager`, extract `Sendable` projections before crossing queues or actors, preserve timestamps and frames, stop every service at the feature boundary, and verify physical behavior on the target device/accessory. The simulator can exercise reducers and UI but cannot prove sensor accuracy or a person’s motion.

## 1. One device-motion owner with a bounded projection

```swift
import CoreMotion
import Foundation
import Observation

struct DeviceMotionSample: Sendable {
    let timestamp: TimeInterval
    let gravity: (x: Double, y: Double, z: Double)
    let userAcceleration: (x: Double, y: Double, z: Double)
    let rotationRate: (x: Double, y: Double, z: Double)
    let attitudeQuaternion: (x: Double, y: Double, z: Double, w: Double)
}

@MainActor
@Observable
final class MotionSensorCoordinator {
    private let manager = CMMotionManager()
    private let queue: OperationQueue = {
        let queue = OperationQueue()
        queue.name = "com.example.motion.device-motion"
        queue.maxConcurrentOperationCount = 1
        queue.qualityOfService = .userInitiated
        return queue
    }()

    private(set) var sample: DeviceMotionSample?
    private(set) var lastError: String?
    private(set) var isRunning = false
    private var generation = 0

    func start(referenceFrame: CMAttitudeReferenceFrame, interval: TimeInterval = 1.0 / 60.0) {
        guard manager.isDeviceMotionAvailable else {
            lastError = "Device motion is unavailable on this device."
            return
        }

        let available = CMMotionManager.availableAttitudeReferenceFrames()
        guard available.contains(referenceFrame) else {
            lastError = "The requested attitude reference frame is unavailable."
            return
        }

        stop()
        generation &+= 1
        let currentGeneration = generation
        manager.deviceMotionUpdateInterval = interval

        manager.startDeviceMotionUpdates(
            using: referenceFrame,
            to: queue
        ) { [weak self] motion, error in
            guard let motion else {
                let message = error.map(String.init(describing:))
                Task { @MainActor in
                    guard let self, self.generation == currentGeneration else { return }
                    self.lastError = message ?? "No device-motion sample was delivered."
                }
                return
            }

            let attitude = motion.attitude.quaternion
            let projection = DeviceMotionSample(
                timestamp: motion.timestamp,
                gravity: (
                    motion.gravity.x,
                    motion.gravity.y,
                    motion.gravity.z
                ),
                userAcceleration: (
                    motion.userAcceleration.x,
                    motion.userAcceleration.y,
                    motion.userAcceleration.z
                ),
                rotationRate: (
                    motion.rotationRate.x,
                    motion.rotationRate.y,
                    motion.rotationRate.z
                ),
                attitudeQuaternion: (attitude.x, attitude.y, attitude.z, attitude.w)
            )

            Task { @MainActor in
                guard let self, self.generation == currentGeneration else { return }
                self.sample = projection
                self.lastError = nil
                self.isRunning = true
            }
        }
        isRunning = manager.isDeviceMotionActive
    }

    func stop() {
        generation &+= 1
        manager.stopDeviceMotionUpdates()
        isRunning = false
        sample = nil
    }
}
```

The handler extracts scalar values and a timestamp before handing work to the main actor. A production implementation should add a freshness threshold and avoid publishing every high-rate sample into a large view tree. If the interaction only needs the latest value, consider the no-handler `startDeviceMotionUpdates(using:)` route and poll `manager.deviceMotion` at the render cadence.

## 2. Accelerometer, gyro, and magnetometer availability

```swift
import CoreMotion

struct MotionCapabilities: Sendable {
    let deviceMotion: Bool
    let accelerometer: Bool
    let gyro: Bool
    let magnetometer: Bool
}

func motionCapabilities() -> MotionCapabilities {
    let manager = CMMotionManager()
    return MotionCapabilities(
        deviceMotion: manager.isDeviceMotionAvailable,
        accelerometer: manager.isAccelerometerAvailable,
        gyro: manager.isGyroAvailable,
        magnetometer: manager.isMagnetometerAvailable
    )
}
```

Use the app’s one owned manager for actual updates; this small capability helper should not be used to create a second active manager. A start method for an unavailable service has no useful effect, so gate the route before showing a live state.

## 3. Activity classification projection

```swift
import CoreMotion
import Foundation

struct ActivityProjection: Sendable {
    let startDate: Date
    let categories: Set<String>
    let confidence: String
}

@MainActor
final class ActivityCoordinator {
    private let manager = CMMotionActivityManager()
    private let queue: OperationQueue = {
        let queue = OperationQueue()
        queue.name = "com.example.motion.activity"
        queue.maxConcurrentOperationCount = 1
        return queue
    }()

    private(set) var latest: ActivityProjection?

    func start() {
        guard CMMotionActivityManager.isActivityAvailable() else { return }

        manager.startActivityUpdates(to: queue) { [weak self] activity in
            let categories = [
                (activity.stationary, "stationary"),
                (activity.walking, "walking"),
                (activity.running, "running"),
                (activity.cycling, "cycling"),
                (activity.automotive, "automotive"),
                (activity.unknown, "unknown")
            ]
            .filter { $0.0 }
            .map(\.1)

            let projection = ActivityProjection(
                startDate: activity.startDate,
                categories: Set(categories),
                confidence: String(describing: activity.confidence)
            )

            Task { @MainActor in
                self?.latest = projection
            }
        }
    }

    func stop() {
        manager.stopActivityUpdates()
        latest = nil
    }
}
```

Keep the categories as a set or multi-label projection because Apple documents that activity properties can overlap. Add a stability/debounce policy before using this projection to change another feature.

## 4. Pedometer availability, live updates, and bounded history

```swift
import CoreMotion
import Foundation

struct PedometerProjection: Sendable {
    let startDate: Date
    let endDate: Date
    let steps: Int64
    let distanceMeters: Double?
    let floorsAscended: Int?
    let floorsDescended: Int?
    let currentPaceMetersPerSecond: Double?
}

@MainActor
final class PedometerCoordinator {
    private let pedometer = CMPedometer()
    private(set) var latest: PedometerProjection?
    private(set) var lastError: String?

    func canShowSteps() -> Bool {
        CMPedometer.isStepCountingAvailable()
    }

    func startLive(from start: Date) {
        guard canShowSteps() else {
            lastError = "Step counting is unavailable on this device."
            return
        }

        pedometer.startUpdates(from: start) { [weak self] data, error in
            guard let data else {
                Task { @MainActor in self?.lastError = error.map(String.init(describing:)) }
                return
            }

            let projection = PedometerProjection(
                startDate: data.startDate,
                endDate: data.endDate,
                steps: data.numberOfSteps.int64Value,
                distanceMeters: data.distance?.doubleValue,
                floorsAscended: data.floorsAscended?.intValue,
                floorsDescended: data.floorsDescended?.intValue,
                currentPaceMetersPerSecond: data.currentPace?.doubleValue
            )
            Task { @MainActor in
                self?.latest = projection
                self?.lastError = nil
            }
        }
    }

    func queryHistory(from start: Date, to end: Date) {
        pedometer.queryPedometerData(from: start, to: end) { [weak self] data, error in
            guard let data else {
                Task { @MainActor in self?.lastError = error.map(String.init(describing:)) }
                return
            }
            let projection = PedometerProjection(
                startDate: data.startDate,
                endDate: data.endDate,
                steps: data.numberOfSteps.int64Value,
                distanceMeters: data.distance?.doubleValue,
                floorsAscended: data.floorsAscended?.intValue,
                floorsDescended: data.floorsDescended?.intValue,
                currentPaceMetersPerSecond: data.currentPace?.doubleValue
            )
            Task { @MainActor in self?.latest = projection }
        }
    }

    func stop() {
        pedometer.stopUpdates()
        pedometer.stopEventUpdates()
        latest = nil
    }
}
```

`CMPedometerData` carries the start and end of the cumulative window. Keep those dates in the UI. The historical system cache is bounded to the past seven days according to Apple’s current documentation; do not build a lifetime chart from this query alone.

## 5. Relative altitude updates

```swift
import CoreMotion
import Foundation

struct RelativeAltitudeProjection: Sendable {
    let relativeMeters: Double
    let pressureKPa: Double
    let receivedAt: Date
}

@MainActor
final class AltimeterCoordinator {
    private let altimeter = CMAltimeter()
    private let queue: OperationQueue = {
        let queue = OperationQueue()
        queue.name = "com.example.motion.altimeter"
        queue.maxConcurrentOperationCount = 1
        return queue
    }()

    private(set) var latest: RelativeAltitudeProjection?

    func startRelative() {
        guard CMAltimeter.isRelativeAltitudeAvailable() else { return }

        altimeter.startRelativeAltitudeUpdates(to: queue) { [weak self] data, error in
            guard let data else { return }
            let projection = RelativeAltitudeProjection(
                relativeMeters: data.relativeAltitude.doubleValue,
                pressureKPa: data.pressure.doubleValue,
                receivedAt: .now
            )
            Task { @MainActor in
                self?.latest = projection
                _ = error // Surface or log the error in a production reducer.
            }
        }
    }

    func stop() {
        altimeter.stopRelativeAltitudeUpdates()
        altimeter.stopAbsoluteAltitudeUpdates()
        latest = nil
    }
}
```

For absolute altitude, gate with `CMAltimeter.isAbsoluteAltitudeAvailable()` and use the matching absolute update handler and stop method. Establish a baseline and coalesce unchanged periodic events instead of treating every callback as a meaningful elevation change.

## 6. Headphone motion with disconnect-safe state

```swift
import CoreMotion
import Foundation

struct HeadphonePose: Sendable {
    let timestamp: TimeInterval
    let quaternion: (x: Double, y: Double, z: Double, w: Double)
}

@MainActor
final class HeadphoneMotionCoordinator {
    private let manager = CMHeadphoneMotionManager()
    private let queue: OperationQueue = {
        let queue = OperationQueue()
        queue.name = "com.example.motion.headphones"
        queue.maxConcurrentOperationCount = 1
        return queue
    }()

    private(set) var pose: HeadphonePose?
    private(set) var isConnectedAndAvailable = false

    func start() {
        guard manager.isDeviceMotionAvailable else {
            isConnectedAndAvailable = false
            pose = nil
            return
        }

        manager.startDeviceMotionUpdates(to: queue) { [weak self] motion, _ in
            guard let motion else { return }
            let q = motion.attitude.quaternion
            let pose = HeadphonePose(
                timestamp: motion.timestamp,
                quaternion: (q.x, q.y, q.z, q.w)
            )
            Task { @MainActor in
                self?.isConnectedAndAvailable = true
                self?.pose = pose
            }
        }
    }

    func stop() {
        manager.stopDeviceMotionUpdates()
        manager.stopConnectionStatusUpdates()
        isConnectedAndAvailable = false
        pose = nil
    }
}
```

Use `startConnectionStatusUpdates()` and the final SDK’s `CMHeadphoneMotionManagerDelegate` methods when the product needs explicit accessory connection changes. The important state rule is that a disconnected or unavailable accessory clears the live pose rather than leaving the last sample on screen.

## 7. SwiftUI status surface

```swift
import SwiftUI

struct MotionStatusView: View {
    let title: String
    let value: String
    let detail: String
    let isLive: Bool
    let start: () -> Void
    let stop: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            VStack(alignment: .leading, spacing: 6) {
                Text(title)
                    .font(.headline)
                Text(value)
                    .font(.system(.largeTitle, design: .rounded).weight(.semibold))
                    .contentTransition(.numericText())
                Text(detail)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }
            .accessibilityElement(children: .combine)
            .accessibilityLabel(title)
            .accessibilityValue("\(value). \(detail)")

            HStack {
                if isLive {
                    Button("Stop", action: stop)
                        .buttonStyle(.borderedProminent)
                } else {
                    Button("Start", action: start)
                        .buttonStyle(.borderedProminent)
                }
            }
        }
        .padding()
        .glassEffect(.regular, in: .rect(cornerRadius: 24))
    }
}
```

Keep `.glassEffect` behind the target availability/fallback policy used by the project. The view should still be fully understandable with a standard background, Reduce Transparency, Increase Contrast, and Reduce Motion. Do not call `start()` from `body`; start at an explicit feature lifecycle boundary such as a task or button action and stop on cancellation/disappearance.

## 8. Typed on-device AI motion summary

```swift
import Foundation
import FoundationModels

@Generable
struct MotionSummaryProposal {
    var label: String
    var confidence: String
    var explanation: String
    var recommendedAction: String
}

enum MotionSummaryValidationError: Error {
    case unsupportedLabel
    case unsupportedConfidence
    case tooLong
}

func validateMotionSummary(
    _ proposal: MotionSummaryProposal
) throws -> MotionSummaryProposal {
    let labels = Set(["gesture-match", "mixed-motion", "walking-signal", "no-match"])
    let confidences = Set(["low", "medium", "high"])

    guard labels.contains(proposal.label) else {
        throw MotionSummaryValidationError.unsupportedLabel
    }
    guard confidences.contains(proposal.confidence) else {
        throw MotionSummaryValidationError.unsupportedConfidence
    }
    guard proposal.explanation.count <= 240,
          proposal.recommendedAction.count <= 120 else {
        throw MotionSummaryValidationError.tooLong
    }
    return proposal
}
```

The model receives a bounded feature projection, not an unrestricted sensor stream, unless a separately reviewed product requires otherwise. Keep the proposal away from sensor start/stop, HealthKit writes, notification sends, door controls, or other side effects. A manual explanation remains available when the model is unavailable, busy, or refuses.

## 9. Swift Testing policy fixtures

```swift
import Testing

struct MotionPolicyTests {
    @Test("motion summary labels stay within the app contract")
    func summaryLabelPolicy() throws {
        let proposal = MotionSummaryProposal(
            label: "gesture-match",
            confidence: "medium",
            explanation: "The bounded feature window matched the saved gesture.",
            recommendedAction: "Ask the person to confirm."
        )
        #expect(throws: Never.self) {
            _ = try validateMotionSummary(proposal)
        }
    }

    @Test("unsupported summary labels are rejected")
    func rejectUnknownLabel() {
        let proposal = MotionSummaryProposal(
            label: "medical-diagnosis",
            confidence: "high",
            explanation: "Not an allowed label.",
            recommendedAction: "Do not act."
        )
        #expect(throws: MotionSummaryValidationError.unsupportedLabel) {
            _ = try validateMotionSummary(proposal)
        }
    }
}
```

These tests prove deterministic schema policy only. They do not prove sensor availability, authorization, cadence, accuracy, energy behavior, accessory connection, or model quality on a physical device.

## Sources

- [Core Motion](https://developer.apple.com/documentation/coremotion/)
- [CMMotionManager](https://developer.apple.com/documentation/coremotion/cmmotionmanager)
- [CMDeviceMotion](https://developer.apple.com/documentation/coremotion/cmdevicemotion)
- [CMAttitude](https://developer.apple.com/documentation/coremotion/cmattitude)
- [CMAttitudeReferenceFrame](https://developer.apple.com/documentation/coremotion/cmattitudereferenceframe)
- [CMMotionActivityManager](https://developer.apple.com/documentation/coremotion/cmmotionactivitymanager)
- [CMMotionActivity](https://developer.apple.com/documentation/coremotion/cmmotionactivity)
- [CMAuthorizationStatus](https://developer.apple.com/documentation/coremotion/cmauthorizationstatus)
- [CMPedometer](https://developer.apple.com/documentation/coremotion/cmpedometer)
- [CMPedometerData](https://developer.apple.com/documentation/coremotion/cmpedometerdata)
- [CMAltimeter](https://developer.apple.com/documentation/coremotion/cmaltimeter)
- [CMAltitudeData](https://developer.apple.com/documentation/coremotion/cmaltitudedata)
- [CMHeadphoneMotionManager](https://developer.apple.com/documentation/coremotion/cmheadphonemotionmanager)
- [NSMotionUsageDescription](https://developer.apple.com/documentation/bundleresources/information_property_list/nsmotionusagedescription)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
