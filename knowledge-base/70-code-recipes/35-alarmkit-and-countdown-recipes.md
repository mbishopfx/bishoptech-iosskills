# AlarmKit and countdown recipes

These are compile-oriented route sketches for the iOS 26 SDK. They are not claimed to compile in this documentation workspace. Confirm the exact SDK signature, generic qualification, target membership, availability, and Xcode diagnostics before copying them into an app.

Every recipe assumes:

- AlarmKit is linked to the intended app target;
- NSAlarmKitUsageDescription is present and truthful;
- the app has a user-facing authorization and confirmation path;
- app-owned intent records are separate from AlarmKit runtime state;
- any countdown presentation has the required widget extension;
- custom system actions are idempotent and do not hide irreversible side effects.

## Shared metadata

Keep metadata small and shared only between the app and widget extension:

~~~swift
import AlarmKit

struct CookingMetadata: AlarmMetadata {
    let recipeID: String
    let presentationVersion: Int
}
~~~

The metadata type must satisfy the protocol’s Codable, Hashable, and Sendable requirements. Do not put raw model context, account tokens, private notes, or a database snapshot in the type.

## Recipe 1: authorization gate

Make the authorization result explicit in app state:

~~~swift
import AlarmKit

@MainActor
final class AlarmAuthorizationModel: ObservableObject {
    @Published private(set) var state: AlarmManager.AuthorizationState

    private let manager = AlarmManager.shared

    init() {
        state = manager.authorizationState
    }

    func requestIfNeeded() async {
        guard state == .notDetermined else { return }

        do {
            state = try await manager.requestAuthorization()
        } catch {
            state = manager.authorizationState
        }
    }
}
~~~

Verify the exact ObservableObject/Observation choice for the deployment target. The important behavior is that a denied result retains the draft and shows a Settings recovery path; it does not silently fall back to a registered alarm claim.

For a long-lived feature, observe authorization changes:

~~~swift
let authorizationTask = Task { [manager] in
    for await state in manager.authorizationUpdates {
        await MainActor.run {
            // Update app-owned presentation state.
            _ = state
        }
    }
}
~~~

Cancel the task when the feature owner is torn down. Do not create an unbounded observer for every view appearance.

## Recipe 2: build a relative weekly schedule

Map a validated typed draft into a local-time schedule:

~~~swift
let time = Alarm.Schedule.Relative.Time(
    hour: draft.hour,
    minute: draft.minute
)

let recurrence: Alarm.Schedule.Relative.Recurrence =
    draft.weekdays.isEmpty
    ? .never
    : .weekly(draft.weekdays)

let schedule: Alarm.Schedule = .relative(
    .init(time: time, repeats: recurrence)
)
~~~

This route means the chosen hour and minute are relative to the device’s current time zone. If the product needs a fixed instant, use the fixed-date route instead. Keep the original time-zone identifier in the app-owned record for review and reconciliation.

## Recipe 3: build a fixed one-shot schedule

Use a fixed schedule only after validating that the date is in the future:

~~~swift
guard draft.oneShotDate > clock.now else {
    throw AlarmDraftError.dateMustBeFuture
}

let schedule: Alarm.Schedule = .fixed(draft.oneShotDate)
~~~

Use an injected clock in tests. Do not compare to a preview-created Date and infer production behavior from the result.

## Recipe 4: configure alert, countdown, and paused presentations

Create only the states that the feature actually supports:

~~~swift
let repeatButton = AlarmButton(
    text: "Repeat",
    textColor: .blue,
    systemImageName: "repeat"
)

let alert = AlarmPresentation.Alert(
    title: "Food is ready",
    secondaryButton: repeatButton,
    secondaryButtonBehavior: .countdown
)

let countdown = AlarmPresentation.Countdown(
    title: "Cooking",
    pauseButton: AlarmButton(
        text: "Pause",
        textColor: .blue,
        systemImageName: "pause.circle"
    )
)

let paused = AlarmPresentation.Paused(
    title: "Cooking paused",
    resumeButton: AlarmButton(
        text: "Resume",
        textColor: .blue,
        systemImageName: "play.circle"
    )
)

let presentation = AlarmPresentation(
    alert: alert,
    countdown: countdown,
    paused: paused
)

let attributes = AlarmAttributes<CookingMetadata>(
    presentation: presentation,
    metadata: CookingMetadata(
        recipeID: "recipe-123",
        presentationVersion: 1
    ),
    tintColor: .green
)
~~~

The current API has a system-managed stop action for the alert presentation. Older sample code may show a stopButton parameter; follow the signature in the selected SDK and treat deprecation warnings as a required source refresh.

## Recipe 5: schedule an alarm configuration

Schedule the configuration only from an explicit, validated command:

~~~swift
let id = draft.id

let configuration = AlarmManager.AlarmConfiguration(
    countdownDuration: draft.countdownDuration,
    schedule: schedule,
    attributes: attributes,
    stopIntent: StopAlarmIntent(alarmID: id.uuidString),
    secondaryIntent: RepeatAlarmIntent(alarmID: id.uuidString),
    sound: .default
)

let alarm = try await AlarmManager.shared.schedule(
    id: id,
    configuration: configuration
)

// Persist the app-owned record as registered only after this returns.
_ = alarm
~~~

The exact App Intent types and optional parameter qualification are app-specific. Keep this command behind a service that performs the authorization check, revalidates the draft, creates the idempotency key, and persists only after success.

## Recipe 6: schedule an immediate timer

For a timer that starts immediately, use the timer convenience route:

~~~swift
let configuration = AlarmManager.AlarmConfiguration.timer(
    duration: 25 * 60,
    attributes: attributes,
    stopIntent: StopAlarmIntent(alarmID: id.uuidString),
    secondaryIntent: RepeatAlarmIntent(alarmID: id.uuidString),
    sound: .default
)

let alarm = try await AlarmManager.shared.schedule(
    id: id,
    configuration: configuration
)
~~~

If the timer has a custom countdown or paused presentation, confirm the widget extension and ActivityConfiguration are present before treating the route as complete.

## Recipe 7: observe the system alarm set

Observe the system set and reconcile it to app-owned records:

~~~swift
actor AlarmReconciler {
    private let manager = AlarmManager.shared

    func snapshot() throws -> [Alarm] {
        try manager.alarms
    }

    func observe(
        update: @Sendable @escaping ([Alarm]) async -> Void
    ) async {
        for await alarms in manager.alarmUpdates {
            await update(alarms)
        }
    }
}
~~~

The actual isolated type may need adjustment for the SDK’s sendability diagnostics. The architectural requirements are more important than this sketch:

- read a snapshot on launch/scene activation;
- observe changes while the feature is active;
- map by stable id;
- treat a missing one-shot alarm as an outcome needing classification;
- never delete the app-owned record just because the system set changed.

## Recipe 8: expose lifecycle operations

Keep system operations in one service:

~~~swift
struct AlarmOperations {
    let manager = AlarmManager.shared

    func pause(_ id: Alarm.ID) throws {
        try manager.pause(id: id)
    }

    func resume(_ id: Alarm.ID) throws {
        try manager.resume(id: id)
    }

    func stop(_ id: Alarm.ID) throws {
        try manager.stop(id: id)
    }

    func cancel(_ id: Alarm.ID) throws {
        try manager.cancel(id: id)
    }

    func countdown(_ id: Alarm.ID) throws {
        try manager.countdown(id: id)
    }
}
~~~

Each method can throw. Reflect the error in app-owned state and refresh from alarms/alarmUpdates. Do not optimistically mark a record stopped and then leave it there when the system operation failed.

## Recipe 9: add the countdown widget extension

The widget extension uses AlarmAttributes and the system-managed AlarmPresentationState:

~~~swift
import AlarmKit
import ActivityKit
import SwiftUI
import WidgetKit

struct AlarmLiveActivity: Widget {
    var body: some WidgetConfiguration {
        ActivityConfiguration(for: AlarmAttributes<CookingMetadata>.self) { context in
            switch context.state.mode {
            case .countdown:
                CountdownView(context: context)
            case .paused:
                PausedView(context: context)
            case .alert:
                AlertView(context: context)
            }
        } dynamicIsland: { context in
            DynamicIsland {
                DynamicIslandExpandedRegion(.leading) {
                    CountdownLabel(context: context)
                }
                DynamicIslandExpandedRegion(.trailing) {
                    StateLabel(context: context)
                }
            } compactLeading: {
                CountdownLabel(context: context)
            } compactTrailing: {
                StateLabel(context: context)
            } minimal: {
                Image(systemName: "timer")
            }
        }
    }
}
~~~

This is a route sketch. Build separate views for each mode and adapt to the actual SDK’s context state members. The extension should not query app-only storage or schedule an alarm while rendering. Test the target with a fixture AlarmAttributes value and then on a supported physical device.

## Recipe 10: safe App Intent side effect

Keep the action idempotent and bounded:

~~~swift
struct RepeatAlarmIntent: LiveActivityIntent {
    static var title: LocalizedStringResource = "Repeat alarm"

    let alarmID: String

    func perform() async throws -> some IntentResult {
        let id = try parseAlarmID(alarmID)
        try await AlarmActionService.shared.repeatIfNeeded(id: id)
        return .result()
    }
}
~~~

The exact protocol requirements and return type are SDK-sensitive. The service should:

1. validate the id;
2. load the app-owned record;
3. check whether the action was already applied;
4. call the documented AlarmKit operation or domain operation;
5. write an idempotency result;
6. return a concise success or recoverable error.

Never put an arbitrary model prompt or an unbounded network request in a system action. If a remote dependency is unavoidable, show a pending state and make failure safe.

## Recipe 11: app-owned SwiftUI review surface

The app-owned screen should summarize intent, not mirror every system detail:

~~~swift
struct AlarmReviewCard: View {
    let draft: AlarmDraft
    let onSchedule: () -> Void
    let onEdit: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Label(draft.label, systemImage: "alarm")
                .font(.headline)

            Text(scheduleSummary(for: draft))
                .font(.body)
                .fixedSize(horizontal: false, vertical: true)

            HStack {
                Button("Edit", action: onEdit)
                Spacer()
                Button("Schedule alarm", action: onSchedule)
                    .buttonStyle(.borderedProminent)
            }
        }
        .padding()
        .glassEffect()
    }
}
~~~

If the selected SDK exposes a different Liquid Glass modifier or the design does not need glass, use the native alternative. The review must remain understandable without the material.

## Recipe 12: AI proposal to confirmed schedule

Keep model output typed and side-effect free:

~~~swift
struct AlarmProposal: Codable, Hashable, Sendable {
    let label: String
    let kind: AlarmDraft.Kind
    let hour: Int?
    let minute: Int?
    let date: Date?
    let weekdays: [Locale.Weekday]
    let duration: TimeInterval?
    let explanation: String
}

func scheduleAfterConfirmation(
    proposal: AlarmProposal,
    userConfirmed: Bool
) async throws {
    let draft = try AlarmDraftNormalizer.normalize(proposal)
    try AlarmDraftValidator.validate(draft)

    guard userConfirmed else {
        throw AlarmDraftError.confirmationRequired
    }

    try await AlarmSchedulingService.shared.schedule(draft)
}
~~~

The model does not get a reference to AlarmManager. The only side-effecting method is called after deterministic validation and an explicit confirmation.

## Recipe 13: test doubles

Inject a protocol around the system service so the app-owned UI and domain tests are deterministic:

~~~swift
protocol AlarmSchedulingClient: Sendable {
    func requestAuthorization() async throws -> AlarmManager.AuthorizationState
    func schedule(
        id: Alarm.ID,
        configuration: AlarmManager.AlarmConfiguration<CookingMetadata>
    ) async throws -> Alarm
    func cancel(id: Alarm.ID) throws
}
~~~

The actual generic and protocol isolation may need adjustment in the selected SDK. A fake should simulate:

- authorized, denied, and not-determined states;
- schedule success and failure;
- alarm disappearing after fire;
- pause/resume/stop failures;
- duplicate action invocation;
- widget metadata schema mismatch.

Do not make a fake claim to prove the device’s alert UI. It proves the app’s own state transitions and recovery logic.

## Verification notes

Before copying any recipe, run:

1. target/SDK signature inspection;
2. a minimal compile with AlarmKit linked;
3. unit tests for fixed/relative/timer mapping;
4. a widget-extension fixture build if countdown is supported;
5. a signed physical-device run for authorization and delivery;
6. Lock Screen/Dynamic Island/StandBy/paired-device checks as applicable.

Use the [AlarmKit and time-based action proof matrix](../60-verification/17-alarmkit-and-time-based-action-proof-matrix.md) to record what each run actually established.

## Sources

- [AlarmKit](https://developer.apple.com/documentation/alarmkit)
- [AlarmManager](https://developer.apple.com/documentation/alarmkit/alarmmanager)
- [Scheduling an alarm with AlarmKit](https://developer.apple.com/documentation/AlarmKit/scheduling-an-alarm-with-alarmkit)
- [AlarmManager schedule](https://developer.apple.com/documentation/alarmkit/alarmmanager/schedule%28id%3Aconfiguration%3A%29)
- [AlarmConfiguration alarm](https://developer.apple.com/documentation/alarmkit/alarmmanager/alarmconfiguration/alarm%28schedule%3Aattributes%3Aappentityidentifier%3Astopintent%3Asecondaryintent%3Asound%3A%29)
- [AlarmConfiguration timer](https://developer.apple.com/documentation/alarmkit/alarmmanager/alarmconfiguration/timer%28duration%3Aattributes%3Aappentityidentifier%3Astopintent%3Asecondaryintent%3Asound%3A%29)
- [AlarmPresentation.Alert](https://developer.apple.com/documentation/alarmkit/alarmpresentation/alert-swift.struct)
- [AlarmPresentation.Countdown](https://developer.apple.com/documentation/alarmkit/alarmpresentation/countdown-swift.struct)
- [AlarmPresentation.Paused](https://developer.apple.com/documentation/alarmkit/alarmpresentation/paused-swift.struct)
- [AlarmAttributes](https://developer.apple.com/documentation/alarmkit/alarmattributes)
- [AlarmMetadata](https://developer.apple.com/documentation/alarmkit/alarmmetadata)
- [AlarmManager authorization state](https://developer.apple.com/documentation/alarmkit/alarmmanager/authorizationstate-swift.enum)
- [NSAlarmKitUsageDescription](https://developer.apple.com/documentation/BundleResources/Information-Property-List/NSAlarmKitUsageDescription)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [ActivityAttributes](https://developer.apple.com/documentation/activitykit/activityattributes)
- [Displaying live data with Live Activities](https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
