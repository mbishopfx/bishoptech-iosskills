# System Surface and Shortcut Recipes

## Scope and compile boundary

These are bounded Swift route sketches for App Intents, App Entities, App Shortcuts, WidgetKit, ActivityKit, and WidgetKit controls. They are designed to make process, state, and capability boundaries visible. They are not compiled in this documentation-only workspace and do not establish entitlement, signing, server, push, system-discovery, or device proof.

Before using a recipe:

1. Select the app, widget extension, and deployment targets.
2. Check the current API signature and availability in the selected SDK.
3. Decide which data can cross the app/extension boundary and which user authorization is required.
4. Compile a minimal intent or surface in the target project.
5. Test with the app terminated, signed out, offline, unauthorized, stale, and running on supported physical devices.

## Recipe 1: shared domain action boundary

The app, intent, widget, and control should call one domain action rather than copy business rules into each surface.

```swift
protocol CaptureActions: Sendable {
    func markReviewed(id: String) async throws
}

struct CaptureActionService: CaptureActions {
    let repository: CaptureRepository

    func markReviewed(id: String) async throws {
        try await repository.markReviewed(id: id)
        // Reconcile any shared-store or server state before returning.
    }
}

protocol CaptureRepository: Sendable {
    func markReviewed(id: String) async throws
}
```

The repository may be backed by SwiftData, a shared app-group store, or a server-backed actor. The intent should not assume that the app scene is alive, and the widget view should not own this service.

## Recipe 2: App Entity and access-checked query

Expose a small, stable representation for system selection. Keep private fields in the domain model and enforce account/permission checks in the query and service.

```swift
import AppIntents

struct CaptureEntity: AppEntity, Identifiable {
    let id: String
    let title: String

    static var typeDisplayRepresentation = TypeDisplayRepresentation(name: "Capture")
    static var defaultQuery = CaptureQuery()

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(title: "\(title)")
    }
}

struct CaptureQuery: EntityQuery {
    func entities(
        for identifiers: [CaptureEntity.ID]
    ) async throws -> [CaptureEntity] {
        // Return only records the current account may access.
        return []
    }

    func suggestedEntities() async throws -> [CaptureEntity] {
        // Return a bounded, privacy-safe suggestion set.
        return []
    }
}
```

The empty arrays are route placeholders. A real query must handle deleted, archived, unauthorized, and ambiguous records. Do not pass a full SwiftData model or private transcript as the display representation merely to avoid designing a query boundary.

## Recipe 3: App Intent with a deterministic perform boundary

`perform()` should validate the current state, call the shared action, and return only after the operation has reached the state that the system surface will render.

```swift
import AppIntents

struct MarkCaptureReviewed: AppIntent {
    static var title: LocalizedStringResource = "Mark capture reviewed"
    static var description = IntentDescription(
        "Marks a saved capture as reviewed."
    )

    @Parameter(title: "Capture")
    var capture: CaptureEntity

    func perform() async throws -> some IntentResult {
        let actions = CaptureActionService(repository: CurrentRepository.shared)
        try await actions.markReviewed(id: capture.id)
        return .result()
    }
}
```

`CurrentRepository.shared` is a placeholder for an injected or otherwise testable dependency. A production intent must define what happens when the user is signed out, permission is denied, the record has disappeared, the write conflicts, or the service is offline. Do not report success before the domain operation succeeds.

## Recipe 4: an App Shortcut with system-readable vocabulary

Shortcuts are user-facing system copy. Keep phrases memorable, avoid generic verbs that collide with other apps, and provide enough result text for audio-only interaction.

```swift
import AppIntents

struct CaptureShortcuts: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        [
            AppShortcut(
                intent: MarkCaptureReviewed(),
                phrases: [
                    "Review a capture in \(.applicationName)"
                ],
                shortTitle: "Review capture",
                systemImageName: "checkmark.circle"
            )
        ]
    }
}
```

Check the current phrase interpolation and metadata signature in the selected SDK. Test the phrase in every supported locale, with missing/ambiguous parameters, with the app locked or signed out, and with the app not currently open. App Shortcut availability does not guarantee Apple Intelligence or Siri invocation in every language, region, device, or system context.

## Recipe 5: a timeline-driven widget

The provider prepares a timeline entry; the widget view renders the entry. It does not rely on an always-live app binding or a guaranteed refresh deadline.

```swift
import SwiftUI
import WidgetKit

struct SummaryEntry: TimelineEntry {
    let date: Date
    let status: String
    let isStale: Bool
}

struct SummaryProvider: TimelineProvider {
    func placeholder(in context: Context) -> SummaryEntry {
        SummaryEntry(date: .now, status: "Ready", isStale: false)
    }

    func getSnapshot(
        in context: Context,
        completion: @escaping (SummaryEntry) -> Void
    ) {
        completion(SummaryEntry(date: .now, status: "Preview", isStale: false))
    }

    func getTimeline(
        in context: Context,
        completion: @escaping (Timeline<SummaryEntry>) -> Void
    ) {
        let entry = SummaryEntry(
            date: .now,
            status: SharedSummaryStore.readStatus(),
            isStale: SharedSummaryStore.isStale
        )

        completion(
            Timeline(entries: [entry], policy: .after(.now.addingTimeInterval(900)))
        )
    }
}

struct SummaryWidget: Widget {
    var body: some WidgetConfiguration {
        StaticConfiguration(
            kind: "com.example.summary",
            provider: SummaryProvider()
        ) { entry in
            Text(entry.isStale ? "Outdated: \(entry.status)" : entry.status)
                .containerBackground(.fill.tertiary, for: .widget)
        }
        .configurationDisplayName("Summary")
        .description("Shows the latest safe summary.")
    }
}
```

The store and refresh interval are illustrative. WidgetKit may request a timeline later than its entry date, and the system limits refreshes. Build entries for signed-out, permission-limited, no-data, stale, error, and long-localized states. Use an app deep link for details instead of trying to fit an entire workflow into the widget.

## Recipe 6: interactive widget button

Use an App Intent for an action that changes data without opening the app. Store the change before `perform()` returns so the next timeline reflects the result.

```swift
struct RefreshSummaryIntent: AppIntent {
    static var title: LocalizedStringResource = "Refresh summary"

    func perform() async throws -> some IntentResult {
        try await SharedSummaryStore.refresh()
        return .result()
    }
}

struct InteractiveSummary: View {
    var body: some View {
        VStack(alignment: .leading) {
            Text(SharedSummaryStore.readStatus())

            Button(intent: RefreshSummaryIntent()) {
                Label("Refresh", systemImage: "arrow.clockwise")
            }
        }
        .invalidatableContent()
    }
}
```

`SharedSummaryStore` is a route placeholder. Use `invalidatableContent()` only on important content that is awaiting a result, not as a blanket modifier. If the action fails, render an honest error or stale state after the timeline reload; do not leave a success-looking label because the button was pressed.

## Recipe 7: interactive widget toggle with reconciliation

Widget toggles can appear optimistic while the intent runs. The domain operation and subsequent rendered state must reconcile the optimistic value.

```swift
struct SetCaptureReviewedIntent: AppIntent {
    static var title: LocalizedStringResource = "Set capture reviewed"

    @Parameter(title: "Reviewed")
    var value: Bool

    @Parameter(title: "Capture ID")
    var captureID: String

    func perform() async throws -> some IntentResult {
        try await SharedSummaryStore.setReviewed(value, id: captureID)
        return .result()
    }
}

struct ReviewToggle: View {
    let isReviewed: Bool
    let captureID: String

    var body: some View {
        Toggle(
            isOn: isReviewed,
            intent: SetCaptureReviewedIntent(
                value: isReviewed,
                captureID: captureID
            )
        ) {
            Text("Reviewed")
        }
    }
}
```

The exact initializer and parameter requirements are SDK-sensitive. Check the current WidgetKit/App Intents documentation and target membership. Test the success, timeout, conflict, unauthorized, and offline paths, especially when the widget is hosted in another context.

## Recipe 8: start and update a Live Activity locally

ActivityKit separates static attributes from dynamic content state. Keep the event time-bounded and provide a stale policy.

```swift
import ActivityKit

struct FocusSessionAttributes: ActivityAttributes {
    let sessionID: String

    struct ContentState: Codable, Hashable {
        let phase: String
        let progress: Double
        let staleDate: Date?
    }
}

func startFocusSession(
    sessionID: String,
    initialState: FocusSessionAttributes.ContentState
) throws -> Activity<FocusSessionAttributes> {
    let attributes = FocusSessionAttributes(sessionID: sessionID)
    let content = ActivityContent(
        state: initialState,
        staleDate: initialState.staleDate
    )

    return try Activity.request(
        attributes: attributes,
        content: content,
        pushType: nil
    )
}

func updateFocusSession(
    _ activity: Activity<FocusSessionAttributes>,
    state: FocusSessionAttributes.ContentState
) async {
    let content = ActivityContent(state: state, staleDate: state.staleDate)
    await activity.update(content)
}
```

Handle authorization errors, duplicate sessions, user-disabled Live Activities, app backgrounding, and stale content. If the activity needs remote updates, request a push token and implement the APNs/ActivityKit server boundary; `pushType: nil` intentionally does not prove remote delivery.

## Recipe 9: render a Live Activity surface

Use the widget extension to render the activity’s Lock Screen and Dynamic Island regions. Keep the content glanceable and the interactive actions essential to the event.

```swift
import ActivityKit
import WidgetKit
import SwiftUI

struct FocusSessionLiveActivity: Widget {
    var body: some WidgetConfiguration {
        ActivityConfiguration(for: FocusSessionAttributes.self) { context in
            VStack(alignment: .leading, spacing: 8) {
                Text(context.state.phase)
                    .font(.headline)
                ProgressView(value: context.state.progress)
                Text("Session \(context.attributes.sessionID)")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            .activityBackgroundTint(.black)
            .activitySystemActionForegroundColor(.white)
        } dynamicIsland: { context in
            DynamicIsland {
                DynamicIslandExpandedRegion(.leading) {
                    Text(context.state.phase)
                }
                DynamicIslandExpandedRegion(.trailing) {
                    Text(context.state.progress, format: .percent)
                }
                DynamicIslandExpandedRegion(.bottom) {
                    ProgressView(value: context.state.progress)
                }
            } compactLeading: {
                Image(systemName: "timer")
            } compactTrailing: {
                Text(context.state.progress, format: .percent)
            } minimal: {
                Image(systemName: "timer")
            }
        }
    }
}
```

The visual regions and modifiers are target-sensitive. Test text length, Dynamic Island availability, Lock Screen, Always-On appearance, contrast, stale state, Dynamic Type, VoiceOver, and deep-link behavior. Do not claim that a Live Activity appears on every device or platform.

## Recipe 10: end a Live Activity honestly

End only when the event’s domain state is complete, cancelled, or no longer useful. Preserve final content when a person may need to reference it.

```swift
func endFocusSession(
    _ activity: Activity<FocusSessionAttributes>,
    finalState: FocusSessionAttributes.ContentState
) async {
    let finalContent = ActivityContent(
        state: finalState,
        staleDate: nil
    )
    await activity.end(finalContent, dismissalPolicy: .default)
}
```

Choose a dismissal policy based on the product’s need to preserve the final result. Test interrupted, expired, stale, duplicate, and user-cancelled sessions. An ended activity may remain visible for a period chosen by the system or policy; it is not the same as deleting a record from the app.

## Recipe 11: a Control Center toggle

Controls have a value-provider boundary and an App Intent action. The system queries the value after the action returns.

```swift
import AppIntents
import WidgetKit

struct FocusTimerControl: ControlWidget {
    static let kind = "com.example.focus.timer-control"

    var body: some ControlWidgetConfiguration {
        StaticControlConfiguration(
            kind: Self.kind,
            provider: Provider()
        ) { value in
            ControlWidgetToggle(
                "Focus timer",
                isOn: value,
                action: ToggleFocusTimerIntent(),
                valueLabel: { isOn in
                    Label(
                        isOn ? "Running" : "Stopped",
                        systemImage: isOn ? "timer" : "timer.slash"
                    )
                }
            )
        }
        .displayName("Focus timer")
        .description("Start or stop the focus timer.")
    }

    struct Provider: ControlValueProvider {
        var previewValue: Bool { false }

        func currentValue() async throws -> Bool {
            try await SharedSummaryStore.isFocusTimerRunning()
        }
    }
}

struct ToggleFocusTimerIntent: SetValueIntent {
    static var title: LocalizedStringResource = "Focus timer"

    @Parameter(title: "Timer is running")
    var value: Bool

    func perform() async throws -> some IntentResult {
        try await SharedSummaryStore.setFocusTimerRunning(value)
        return .result()
    }
}
```

The control’s symbol, on/off labels, provider state, and action must agree. Test locked-device behavior, Control Center placement, stale values, action failure, remote/local reloads, and the hardware surfaces that support the control. The control extension needs the correct target membership and capabilities in the target project.

## Recipe 12: reload and test the system surface boundary

Reload only when the shared data that the surface displays changes. Keep the reload call outside the view when possible.

```swift
import WidgetKit

struct SurfaceRefreshCoordinator {
    let widgetKind = "com.example.summary"

    func didCommitSummaryChange() {
        WidgetCenter.shared.reloadTimelines(ofKind: widgetKind)
        // Reload controls through ControlCenter in a target that owns controls.
        // Update Live Activities through ActivityKit or its push boundary.
    }
}
```

This call requests a timeline reload; it does not guarantee an immediate render. Test data freshness, account changes, permission changes, extension termination, network loss, and rate/budget behavior outside the Xcode debugger.

## System-surface test matrix

- App Intent: run from the app, Shortcuts, Siri/Apple Intelligence where supported, and a terminated app; test parameters, errors, authorization, and localization.
- App Entity: test suggested, identifier, missing, deleted, ambiguous, private, and signed-out records.
- Widget: test placeholder, snapshot, every supported family, timeline dates, stale/error/empty states, deep links, and privacy on the Lock Screen.
- Interactive widget: test the intent in the extension process, shared-store commit, optimistic toggle correction, locked device, iPhone-on-Mac delay, and failure copy.
- Live Activity: test start/update/end, stale state, interruption, duplicate activity, Dynamic Island/Lock Screen/paired surface layouts, deep links, and push token lifecycle.
- Control: test provider value, button/toggle action, symbol and label, locked device, Control Center/Lock Screen/Action button placement, and reload behavior.
- Release boundary: verify target membership, entitlements, capabilities, bundle identifiers, signing, privacy strings, push environment, and supported device/OS matrix separately from source and compile checks.

## Sources

- [App Intents](https://developer.apple.com/documentation/appintents)
- [App intents](https://developer.apple.com/documentation/appintents/app-intents)
- [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- [EntityQuery](https://developer.apple.com/documentation/appintents/entityquery)
- [AppShortcutsProvider](https://developer.apple.com/documentation/AppIntents/AppShortcutsProvider)
- [ParameterSummary](https://developer.apple.com/documentation/appintents/parametersummary)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit)
- [Timeline](https://developer.apple.com/documentation/widgetkit/timeline)
- [TimelineProvider](https://developer.apple.com/documentation/widgetkit/timelineprovider)
- [AppIntentConfiguration](https://developer.apple.com/documentation/widgetkit/appintentconfiguration)
- [Adding interactivity to widgets and Live Activities](https://developer.apple.com/documentation/widgetkit/adding-interactivity-to-widgets-and-live-activities)
- [Keeping a widget up to date](https://developer.apple.com/documentation/widgetkit/keeping-a-widget-up-to-date)
- [WidgetCenter](https://developer.apple.com/documentation/widgetkit/widgetcenter)
- [reloadTimelines(ofKind:)](https://developer.apple.com/documentation/widgetkit/widgetcenter/reloadtimelines%28ofkind%3A%29)
- [Controls collection](https://developer.apple.com/documentation/widgetkit/controls-collection)
- [Creating controls to perform actions across the system](https://developer.apple.com/documentation/widgetkit/creating-controls-to-perform-actions-across-the-system)
- [ControlWidget](https://developer.apple.com/documentation/swiftui/controlwidget)
- [ControlWidgetButton](https://developer.apple.com/documentation/widgetkit/controlwidgetbutton)
- [ControlWidgetToggle](https://developer.apple.com/documentation/widgetkit/controlwidgettoggle)
- [ControlValueProvider](https://developer.apple.com/documentation/widgetkit/controlvalueprovider)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [ActivityAttributes](https://developer.apple.com/documentation/activitykit/activityattributes)
- [Activity](https://developer.apple.com/documentation/activitykit/activity)
- [ActivityContent](https://developer.apple.com/documentation/activitykit/activitycontent)
- [request(attributes:content:pushType:)](https://developer.apple.com/documentation/activitykit/activity/request%28attributes%3Acontent%3Apushtype%3A%29)
- [Displaying live data with Live Activities](https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities)
- [Starting and updating Live Activities with ActivityKit push notifications](https://developer.apple.com/documentation/ActivityKit/starting-and-updating-live-activities-with-activitykit-push-notifications)
- [Live Activities](https://developer.apple.com/design/human-interface-guidelines/live-activities)
- [App Shortcuts](https://developer.apple.com/design/human-interface-guidelines/app-shortcuts)
- [Controls](https://developer.apple.com/design/human-interface-guidelines/controls)
