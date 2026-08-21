# WorkoutKit and HealthKit live-workout recipes

These are compile-oriented route sketches for a selected iOS, iPadOS, or watchOS target. They are not claimed to compile in this documentation workspace. The WorkoutKit API is availability-sensitive and several HealthKit callbacks have target-specific behavior, so confirm the exact signature, actor isolation, entitlement, and deployment target in Xcode before copying.

The snippets keep the important boundary visible:

    draft -> deterministic validation -> WorkoutKit plan
    session -> HealthKit callbacks -> normalized projection
    projection -> SwiftUI / Live Activity / App Intent
    stopped -> end collection -> finish or discard

Do not let an AI result, a view timer, or a Live Activity become the authority for HealthKit state.

## Recipe 1: keep a pure draft before WorkoutKit types

Use an app-owned draft for editing and generation. Store WorkoutKit values at the adapter boundary so the editor can be tested without HealthKit or WorkoutKit.

~~~swift
struct WorkoutDraft: Codable, Hashable, Sendable {
    var id: UUID
    var displayName: String
    var activityRawValue: UInt
    var locationRawValue: UInt
    var stepCount: Int
    var repeatCount: Int
    var goalDescription: String?
    var alertDescription: String?
}

struct DraftValidation {
    var errors: [String] = []
    var warnings: [String] = []

    var isValid: Bool { errors.isEmpty }
}

func validateDraft(_ draft: WorkoutDraft) -> DraftValidation {
    var result = DraftValidation()

    if draft.displayName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
        result.errors.append("Add a workout name.")
    }
    if draft.stepCount == 0 {
        result.errors.append("Add at least one workout step.")
    }
    if draft.stepCount < 0 || draft.repeatCount < 0 {
        result.errors.append("Step and repeat counts cannot be negative.")
    }
    if draft.goalDescription == nil && draft.alertDescription == nil {
        result.warnings.append("This plan has no explicit goal or alert.")
    }

    return result
}
~~~

The raw-value fields are a deliberately boring persistence boundary. Convert them to the current HKWorkoutActivityType and HKWorkoutSessionLocationType only inside the adapter, and fail when a raw value is no longer supported.

## Recipe 2: adapt a validated draft to CustomWorkout

This sketch shows the responsibilities, not a guaranteed current initializer. Confirm the current WorkoutKit measurement and enum case signatures before compiling.

~~~swift
import HealthKit
import WorkoutKit

enum WorkoutPlanAdapterError: Error {
    case unsupportedActivity
    case unsupportedGoal
    case unsupportedAlert
    case invalidDraft([String])
}

func makeCustomWorkoutPlan(from draft: WorkoutDraft) throws -> WorkoutPlan {
    let validation = validateDraft(draft)
    guard validation.isValid else {
        throw WorkoutPlanAdapterError.invalidDraft(validation.errors)
    }

    let activity = HKWorkoutActivityType(rawValue: draft.activityRawValue)
    let location = HKWorkoutSessionLocationType(rawValue: draft.locationRawValue)

    guard CustomWorkout.supportsActivity(activity) else {
        throw WorkoutPlanAdapterError.unsupportedActivity
    }

    // Build WorkoutStep, IntervalStep, IntervalBlock, WorkoutGoal, and
    // WorkoutAlert from validated user fields. Check exact current labels,
    // Measurement units, and enum cases in the selected SDK.
    let warmup: WorkoutStep? = makeWarmup(from: draft)
    let blocks: [IntervalBlock] = makeBlocks(from: draft)
    let cooldown: WorkoutStep? = makeCooldown(from: draft)

    for block in blocks {
        for step in block.steps {
            if let goal = step.goal,
               !CustomWorkout.supportsGoal(goal, activity: activity, location: location) {
                throw WorkoutPlanAdapterError.unsupportedGoal
            }
            if let alert = step.alert,
               !CustomWorkout.supportsAlert(alert, activity: activity, location: location) {
                throw WorkoutPlanAdapterError.unsupportedAlert
            }
        }
    }

    let workout = CustomWorkout(
        activity: activity,
        location: location,
        displayName: draft.displayName,
        warmup: warmup,
        blocks: blocks,
        cooldown: cooldown
    )

    // Confirm the current WorkoutPlan.Workout case and initializer labels.
    return WorkoutPlan(workout: .custom(workout), id: draft.id)
}
~~~

The adapter should reject unsupported goals or alerts. It should not silently remove them because the resulting Workout app plan would no longer represent the user’s request.

## Recipe 3: preview, open, serialize, and restore a plan

Treat each handoff as a separate result. A successful serialization is not a successful Workout app handoff.

~~~swift
import WorkoutKit

enum PlanHandoffResult {
    case serialized(Data)
    case opened
    case failed(String)
}

func serializePlan(_ plan: WorkoutPlan) -> Data {
    // The current SDK exposes a data representation on WorkoutPlan.
    // Store it with the stable app-owned plan ID and SDK/schema metadata.
    plan.dataRepresentation
}

func restorePlan(_ data: Data) throws -> WorkoutPlan {
    try WorkoutPlan(from: data)
}

func openPlanInWorkout(_ plan: WorkoutPlan) async -> PlanHandoffResult {
    do {
        try await plan.openInWorkoutApp()
        return .opened
    } catch {
        return .failed(String(describing: error))
    }
}
~~~

For preview, use the current WorkoutKit preview API exposed by the SDK and retain the result as preview evidence only. Keep a user-facing distinction between Preview, Open in Workout, Exported, and Scheduled.

## Recipe 4: request scheduling authorization and reconcile

The scheduler is a system boundary. Re-read its state after a request and on app activation.

~~~swift
import WorkoutKit

struct ScheduledWorkoutRecord: Codable, Hashable, Sendable {
    let planID: UUID
    let requestedDate: Date
    var lastObservedDate: Date?
    var systemState: String
}

enum SchedulingError: Error {
    case unsupported
    case noMatchingPlan
}

func schedule(_ plan: WorkoutPlan, at date: Date) async throws {
    let scheduler = WorkoutScheduler.shared
    guard scheduler.isSupported else {
        throw SchedulingError.unsupported
    }

    // Verify the current async authorization signature in the selected SDK.
    try await scheduler.requestAuthorization()

    // The current SDK wraps a plan and date in ScheduledWorkoutPlan.
    let scheduled = ScheduledWorkoutPlan(plan, date: date)

    // Verify whether the selected SDK uses schedule(_:) or schedule(_:at:).
    try await scheduler.schedule(scheduled)
}

func reconcileSchedules(
    local: [ScheduledWorkoutRecord],
    observed: [ScheduledWorkoutPlan],
    now: Date
) -> [ScheduledWorkoutRecord] {
    let observedIDs = Set(observed.map { $0.plan.id })

    return local.map { record in
        var next = record
        next.lastObservedDate = now
        if !observedIDs.contains(record.planID) && record.systemState == "scheduled" {
            next.systemState = "missing-from-system"
        }
        return next
    }
}
~~~

The exact properties on ScheduledWorkoutPlan are SDK-defined. Keep reconciliation code behind a small adapter and test it with fixtures for scheduled, completed, removed, unknown, and system-limit states.

## Recipe 5: ask HealthKit for the smallest useful access

Use the HealthKit store only after the app has explained the feature. Keep the sets explicit and target-specific.

~~~swift
import HealthKit

struct HealthAuthorizationPlan {
    let share: Set<HKSampleType>
    let read: Set<HKObjectType>
}

func liveWorkoutAuthorizationPlan() -> HealthAuthorizationPlan {
    let share: Set<HKSampleType> = [
        HKObjectType.workoutType()
    ]

    var read = Set<HKObjectType>()
    if let heartRate = HKObjectType.quantityType(forIdentifier: .heartRate) {
        read.insert(heartRate)
    }
    if let energy = HKObjectType.quantityType(forIdentifier: .activeEnergyBurned) {
        read.insert(energy)
    }
    if let distance = HKObjectType.quantityType(forIdentifier: .distanceWalkingRunning) {
        read.insert(distance)
    }

    return HealthAuthorizationPlan(share: share, read: read)
}

func requestHealthAuthorization(
    store: HKHealthStore,
    plan: HealthAuthorizationPlan
) async throws {
    // Confirm the current async or completion-handler signature for the SDK.
    try await store.requestAuthorization(toShare: plan.share, read: plan.read)
}
~~~

Do not interpret a successful authorization request as permission to read every type. Keep per-metric availability in the runtime model.

## Recipe 6: own the live session in a coordinator

A coordinator keeps HealthKit objects out of SwiftUI view lifetime. The delegate method names below follow Apple’s documented route; verify actor annotations and signatures in the target SDK.

~~~swift
import Foundation
import HealthKit

struct TelemetrySnapshot: Sendable, Equatable {
    var activityName: String
    var state: String
    var elapsedTime: TimeInterval
    var heartRateBPM: Double?
    var activeEnergyKilocalories: Double?
    var distanceMeters: Double?
    var lastSampleDate: Date?
    var freshness: String
}

final class LiveWorkoutCoordinator: NSObject,
                                    HKWorkoutSessionDelegate,
                                    HKLiveWorkoutBuilderDelegate {
    private let healthStore: HKHealthStore
    private(set) var session: HKWorkoutSession?
    private(set) var builder: HKLiveWorkoutBuilder?

    var onSnapshot: (@Sendable (TelemetrySnapshot) -> Void)?
    var onError: (@Sendable (String) -> Void)?

    init(healthStore: HKHealthStore) {
        self.healthStore = healthStore
    }

    func start(
        activity: HKWorkoutActivityType,
        location: HKWorkoutSessionLocationType
    ) throws {
        guard session == nil else { return }

        let configuration = HKWorkoutConfiguration()
        configuration.activityType = activity
        configuration.locationType = location

        let newSession = try HKWorkoutSession(
            healthStore: healthStore,
            configuration: configuration
        )
        let newBuilder = newSession.associatedWorkoutBuilder()
        newBuilder.dataSource = HKLiveWorkoutDataSource(
            healthStore: healthStore,
            workoutConfiguration: configuration
        )
        newSession.delegate = self
        newBuilder.delegate = self

        session = newSession
        builder = newBuilder

        let startDate = Date()
        newSession.startActivity(with: startDate)
        newBuilder.beginCollection(withStart: startDate) { [weak self] success, error in
            guard success else {
                self?.onError?(String(describing: error))
                return
            }
            self?.publishState("running")
        }
    }

    func pause() {
        session?.pause()
    }

    func resume() {
        session?.resume()
    }

    func stop() {
        session?.stopActivity(with: Date())
    }

    private func publishState(_ state: String) {
        // Convert HealthKit values into a small Sendable snapshot on a
        // deliberate isolation boundary before touching SwiftUI state.
    }

    func workoutSession(
        _ workoutSession: HKWorkoutSession,
        didChangeTo toState: HKWorkoutSessionState,
        from fromState: HKWorkoutSessionState,
        date: Date
    ) {
        if toState == .stopped {
            finishAfterStop(at: date)
        } else {
            publishState(String(describing: toState))
        }
    }

    func workoutSession(
        _ workoutSession: HKWorkoutSession,
        didFailWithError error: Error
    ) {
        onError?(String(describing: error))
    }

    func workoutBuilder(
        _ workoutBuilder: HKLiveWorkoutBuilder,
        didCollectDataOf collectedTypes: Set<HKSampleType>
    ) {
        // Query statistics for changed quantity types. Convert each value
        // into an explicit unit and attach freshness metadata.
    }

    func workoutBuilderDidCollectEvent(
        _ workoutBuilder: HKLiveWorkoutBuilder
    ) {
        // Read the latest event and update the normalized event projection.
    }

    func workoutBuilder(
        _ workoutBuilder: HKLiveWorkoutBuilder,
        didBeginCollectionWithStart startDate: Date
    ) {
        publishState("collecting")
    }

    private func finishAfterStop(at endDate: Date) {
        guard let builder, let session else { return }

        builder.endCollection(withEnd: endDate) { [weak self] success, error in
            guard success else {
                self?.onError?(String(describing: error))
                return
            }

            builder.finishWorkout { [weak self] workout, error in
                guard let self else { return }
                if let error {
                    self.onError?(String(describing: error))
                    return
                }
                guard workout != nil else {
                    self.onError?("HealthKit returned no finished workout.")
                    return
                }
                session.end()
                self.publishState("saved")
                self.session = nil
                self.builder = nil
            }
        }
    }
}
~~~

This sketch intentionally leaves statistics extraction and actor isolation as explicit work. The final implementation should not send mutable HealthKit objects into a detached task without a reviewed isolation strategy.

## Recipe 7: finish or discard with an explicit policy

Expose save and discard as separate product decisions. If the user chooses discard, call the current builder discard API and update the app-owned record without saying that a HealthKit workout exists.

~~~swift
enum FinishPolicy: Sendable {
    case save
    case discard
}

func finishBuilder(
    _ builder: HKWorkoutBuilder,
    policy: FinishPolicy,
    endDate: Date
) async throws -> HKWorkout? {
    // The current HealthKit API uses completion handlers for these methods
    // in many SDKs. Bridge them with a checked continuation in production.
    switch policy {
    case .save:
        try await endCollection(builder, endDate: endDate)
        return try await finishWorkout(builder)
    case .discard:
        builder.discardWorkout()
        return nil
    }
}
~~~

Keep the finalize gate idempotent. A second tap should observe saving, saved, discarded, or failed rather than start a second finish sequence.

## Recipe 8: project live state to a Live Activity

The Live Activity is a projection. It should be driven by the coordinator’s normalized snapshot and should tolerate a stale or unavailable value.

~~~swift
import ActivityKit

struct WorkoutActivityAttributes: ActivityAttributes {
    public struct ContentState: Codable, Hashable {
        var state: String
        var primaryMetricText: String
        var elapsedText: String
        var lastUpdated: Date?
        var isStale: Bool
    }

    var activityName: String
    var planID: UUID
}

func startWorkoutActivity(
    name: String,
    planID: UUID,
    snapshot: TelemetrySnapshot
) throws -> Activity<WorkoutActivityAttributes> {
    let attributes = WorkoutActivityAttributes(
        activityName: name,
        planID: planID
    )
    let state = WorkoutActivityAttributes.ContentState(
        state: snapshot.state,
        primaryMetricText: formatPrimaryMetric(snapshot),
        elapsedText: formatElapsed(snapshot.elapsedTime),
        lastUpdated: snapshot.lastSampleDate,
        isStale: snapshot.freshness != "fresh"
    )

    return try Activity.request(
        attributes: attributes,
        content: ActivityContent(state: state, staleDate: nil),
        pushType: nil
    )
}
~~~

The widget extension should not query HealthKit as a hidden second session owner. Send it the smallest safe content state, display freshness, and end the activity when the authoritative runtime reaches saved, discarded, or failed.

## Recipe 9: make an idempotent App Intent command

Use an App Intent to call a deterministic command router. The router must verify the expected session state and return the observed result.

~~~swift
import AppIntents

struct TogglePauseWorkoutIntent: AppIntent {
    static var title: LocalizedStringResource = "Pause or Resume Workout"
    static var openAppWhenRun = false

    @Parameter(title: "Workout ID")
    var workoutID: String

    func perform() async throws -> some IntentResult {
        let result = try await WorkoutCommandRouter.shared.togglePause(
            workoutID: workoutID
        )

        // Return only after the coordinator reports the actual command result.
        // Use the current App Intents result/snippet API if a richer surface is
        // desired; do not claim success from the request alone.
        return .result(dialog: IntentDialog(result.userMessage))
    }
}
~~~

Do not let a language model invoke HealthKit methods directly. An App Intent can be discoverable by the system, but the command still needs authorization, ownership, state checks, and an idempotency key.

## Recipe 10: validate a local AI workout proposal

Keep the proposal Codable and independent from WorkoutKit. After decoding, run deterministic validation and only then adapt it to WorkoutKit.

~~~swift
struct AIWorkoutProposal: Codable, Hashable, Sendable {
    var title: String
    var activity: String
    var location: String
    var steps: [AIStep]
    var assumptions: [String]
    var modelIdentifier: String
    var generatedAt: Date
}

struct AIStep: Codable, Hashable, Sendable {
    var purpose: String
    var durationSeconds: Int?
    var goalText: String?
    var alertText: String?
}

struct ProposalReview: Sendable {
    var errors: [String]
    var warnings: [String]
    var isReadyForUserApproval: Bool
}

func validateProposal(
    _ proposal: AIWorkoutProposal,
    supportedActivities: Set<String>
) -> ProposalReview {
    var errors: [String] = []
    var warnings: [String] = []

    if !supportedActivities.contains(proposal.activity) {
        errors.append("The selected activity is not supported on this target.")
    }
    if proposal.steps.isEmpty {
        errors.append("The proposal has no steps.")
    }
    if proposal.steps.contains(where: { ($0.durationSeconds ?? 1) <= 0 }) {
        errors.append("Every timed step needs a positive duration.")
    }
    if proposal.assumptions.isEmpty {
        warnings.append("The proposal has no recorded assumptions.")
    }

    return ProposalReview(
        errors: errors,
        warnings: warnings,
        isReadyForUserApproval: errors.isEmpty
    )
}
~~~

The review UI should display title, assumptions, source request, validation messages, and editable fields. The Apply action should create an app-owned approved version and then call the WorkoutKit adapter.

## Recipe 11: simulate live telemetry without HealthKit

Use a deterministic source for SwiftUI previews and unit/UI tests. This proves presentation and state transitions, not sensor correctness.

~~~swift
actor FakeTelemetrySource {
    private var step = 0

    func nextSnapshot() -> TelemetrySnapshot {
        step += 1
        return TelemetrySnapshot(
            activityName: "Outdoor Run",
            state: step < 6 ? "running" : "paused",
            elapsedTime: TimeInterval(step * 30),
            heartRateBPM: 142 + Double(step),
            activeEnergyKilocalories: Double(step) * 4.5,
            distanceMeters: Double(step) * 275,
            lastSampleDate: Date(timeIntervalSince1970: 1_700_000_000 + Double(step) * 30),
            freshness: step == 4 ? "stale" : "fresh"
        )
    }
}

#if DEBUG
struct LiveWorkoutFixture {
    static let running = TelemetrySnapshot(
        activityName: "Outdoor Run",
        state: "running",
        elapsedTime: 1_245,
        heartRateBPM: 148,
        activeEnergyKilocalories: 186,
        distanceMeters: 3_240,
        lastSampleDate: Date(timeIntervalSince1970: 1_700_001_245),
        freshness: "fresh"
    )

    static let noHeartRate = TelemetrySnapshot(
        activityName: "Outdoor Run",
        state: "running",
        elapsedTime: 1_245,
        heartRateBPM: nil,
        activeEnergyKilocalories: 186,
        distanceMeters: 3_240,
        lastSampleDate: Date(timeIntervalSince1970: 1_700_001_000),
        freshness: "stale"
    )
}
#endif
~~~

Add fixtures for unauthorized, preparing, paused, interrupted, saving, saved, discarded, and failed. Assert that every fixture has a truthful label and that no missing value is rendered as zero.

## Recipe 12: test the route in layers

Use this sequence:

1. Unit-test pure draft and AI proposal validation.
2. Round-trip WorkoutPlan serialization with fixture data.
3. Test schedule reconciliation with system-list fixtures.
4. UI-test every normalized live state using fake snapshots.
5. Compile each target with the exact entitlements and usage descriptions.
6. Run a signed physical-device session with permission changes and interruption.
7. Run the Lock Screen App Intent and Live Activity path.
8. Inspect the saved or discarded result in HealthKit.
9. Test VoiceOver, Dynamic Type, reduced motion/transparency, contrast, and battery/thermal conditions.

The [WorkoutKit and live-workout proof matrix](../60-verification/21-workoutkit-and-live-workout-proof-matrix.md) records what each layer can prove.

## Sources

- [WorkoutKit](https://developer.apple.com/documentation/workoutkit)
- [CustomWorkout](https://developer.apple.com/documentation/workoutkit/customworkout)
- [IntervalStep](https://developer.apple.com/documentation/workoutkit/intervalstep)
- [WorkoutGoal](https://developer.apple.com/documentation/workoutkit/workoutgoal)
- [WorkoutAlert](https://developer.apple.com/documentation/workoutkit/workoutalert)
- [WorkoutPlan](https://developer.apple.com/documentation/workoutkit/workoutplan)
- [ScheduledWorkoutPlan](https://developer.apple.com/documentation/workoutkit/scheduledworkoutplan)
- [WorkoutScheduler](https://developer.apple.com/documentation/workoutkit/workoutscheduler)
- [HealthKit](https://developer.apple.com/documentation/healthkit)
- [Requesting authorization to access health data](https://developer.apple.com/documentation/HealthKit/authorizing-access-to-health-data)
- [Protecting user privacy](https://developer.apple.com/documentation/healthkit/protecting-user-privacy)
- [Running workout sessions](https://developer.apple.com/documentation/healthkit/running-workout-sessions)
- [HKWorkoutSession](https://developer.apple.com/documentation/healthkit/hkworkoutsession)
- [HKWorkoutConfiguration](https://developer.apple.com/documentation/healthkit/hkworkoutconfiguration)
- [HKWorkoutSessionState](https://developer.apple.com/documentation/healthkit/hkworkoutsessionstate)
- [HKLiveWorkoutBuilder](https://developer.apple.com/documentation/healthkit/hkliveworkoutbuilder)
- [HKLiveWorkoutBuilderDelegate](https://developer.apple.com/documentation/healthkit/hkliveworkoutbuilderdelegate)
- [HKLiveWorkoutDataSource](https://developer.apple.com/documentation/healthkit/hkliveworkoutdatasource)
- [HKWorkoutBuilder](https://developer.apple.com/documentation/healthkit/hkworkoutbuilder)
- [Building a workout app for iPhone and iPad](https://developer.apple.com/documentation/healthkit/building-a-workout-app-for-iphone-and-ipad)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [Displaying live data with Live Activities](https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities)
- [Adding interactivity to widgets and Live Activities](https://developer.apple.com/documentation/widgetkit/adding-interactivity-to-widgets-and-live-activities)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [Swift concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
