# WidgetKit, ActivityKit, and control surface recipes

## How to use these recipes

These are compile-oriented route sketches, not a claim that they compile in an
unidentified project. Confirm protocol requirements, access control, availability
annotations, target membership, macro behavior, and initializer signatures in
the selected Xcode/iOS SDK.

The common boundary is:

    domain state
      -> compact projection
      -> system surface
      -> App Intent action
      -> current validation
      -> idempotent commit
      -> new projection

A preview or sketch does not prove WidgetKit scheduling, Control Center delivery,
ActivityKit push behavior, physical-device support, accessibility, or release
configuration.

## Recipe 1: versioned shared projection

Keep the projection small and versioned. The main app writes it after a domain
commit; the extension reads it without requiring a main-app view model.

~~~swift
import Foundation

struct FocusSurfaceProjection: Codable, Sendable {
    enum State: String, Codable, Sendable {
        case empty
        case ready
        case updating
        case stale
        case denied
        case error
    }

    let schemaVersion: Int
    let revision: Int64
    let updatedAt: Date?
    let staleAt: Date?
    let state: State
    let title: String?
    let value: String?
    let detail: String?
    let deepLink: URL?
    let isPrivate: Bool
}

actor SurfaceProjectionStore {
    private let defaults: UserDefaults
    private let key = "focus.surface.projection"

    init() {
        defaults = UserDefaults(suiteName: "group.example.focus") ?? .standard
    }

    func read() -> FocusSurfaceProjection? {
        guard let data = defaults.data(forKey: key) else { return nil }
        return try? JSONDecoder().decode(FocusSurfaceProjection.self, from: data)
    }

    func write(_ projection: FocusSurfaceProjection) throws {
        let data = try JSONEncoder().encode(projection)
        defaults.set(data, forKey: key)
    }

    func invalidate() {
        defaults.removeObject(forKey: key)
    }
}
~~~

The App Group identifier, entitlement, migration policy, and privacy behavior
must be configured in the actual app and extension targets. Do not use shared
UserDefaults as proof that the domain write was authorized.

## Recipe 2: basic timeline provider

This provider uses a deterministic fixture for placeholder and snapshot, then
reads a compact local projection for the real timeline.

~~~swift
import WidgetKit
import SwiftUI

struct FocusEntry: TimelineEntry {
    let date: Date
    let projection: FocusSurfaceProjection?
}

struct FocusProvider: TimelineProvider {
    func placeholder(in context: Context) -> FocusEntry {
        FocusEntry(date: .now, projection: .placeholder)
    }

    func getSnapshot(in context: Context, completion: @escaping (FocusEntry) -> Void) {
        if context.isPreview {
            completion(FocusEntry(date: .now, projection: .placeholder))
        } else {
            completion(FocusEntry(date: .now, projection: loadProjection()))
        }
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<FocusEntry>) -> Void) {
        let projection = loadProjection()
        let entry = FocusEntry(date: .now, projection: projection)
        completion(Timeline(entries: [entry], policy: .never))
    }

    private func loadProjection() -> FocusSurfaceProjection? {
        // Replace with a synchronous, bounded projection read for the target.
        nil
    }
}

private extension FocusSurfaceProjection {
    static let placeholder = FocusSurfaceProjection(
        schemaVersion: 1,
        revision: 0,
        updatedAt: nil,
        staleAt: nil,
        state: .ready,
        title: "Focus",
        value: "00:25",
        detail: "Preview",
        deepLink: nil,
        isPrivate: false
    )
}
~~~

A real provider should use the current provider protocol signature for the
selected SDK. If the source changes, update the target and this route together.
The widget should still render when no projection exists.

## Recipe 3: widget view with adaptive background and privacy

Use the environment to adapt the family and rendering mode. Keep the example
foreground useful if the system removes the background.

~~~swift
struct FocusWidgetView: View {
    let entry: FocusEntry

    @Environment(\.widgetFamily) private var family
    @Environment(\.widgetRenderingMode) private var renderingMode

    var body: some View {
        content
            .containerBackground(for: .widget) {
                Color.indigo.opacity(0.18)
            }
            .widgetURL(entry.projection?.deepLink)
    }

    @ViewBuilder
    private var content: some View {
        switch entry.projection?.state {
        case .denied:
            Label("Private", systemImage: "lock.fill")
        case .stale:
            Label("Needs update", systemImage: "clock.badge.exclamationmark")
        case .ready:
            readyContent
        default:
            Label("Focus unavailable", systemImage: "questionmark.circle")
        }
    }

    private var readyContent: some View {
        VStack(alignment: .leading) {
            Text(entry.projection?.title ?? "Focus")
                .font(.headline)
            Text(entry.projection?.value ?? "—")
                .font(.title2.monospacedDigit())
                .widgetAccentable()
            if family != .systemSmall {
                Text(entry.projection?.detail ?? "")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
        .redacted(reason: entry.projection?.isPrivate == true ? .privacy : [])
    }
}
~~~

The exact widget rendering environment and supported family values must be
checked against the selected SDK. The important design contract is to provide a
removable background, preserve semantic hierarchy, and redact private state.

## Recipe 4: static widget configuration

Expose a stable kind and the families the product can actually support.

~~~swift
struct FocusWidget: Widget {
    let kind = "com.example.focus.widget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: FocusProvider()) { entry in
            FocusWidgetView(entry: entry)
        }
        .configurationDisplayName("Focus")
        .description("See the current focus session.")
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}

@main
struct FocusWidgetBundle: WidgetBundle {
    var body: some Widget {
        FocusWidget()
    }
}
~~~

Do not list a family merely because the API accepts it. Add a proof row for every
family and host context that the release claims to support.

## Recipe 5: configurable App Intent widget

A configurable widget uses a WidgetConfigurationIntent and an
AppIntentTimelineProvider. The query and entity definitions are intentionally
omitted here because they depend on the app's domain identity and authorization.

~~~swift
import AppIntents
import WidgetKit

struct SelectFocusIntent: WidgetConfigurationIntent {
    static var title: LocalizedStringResource = "Focus session"

    @Parameter(title: "Session")
    var session: FocusEntity

    init() {
        session = FocusEntity.defaultValue
    }
}

struct ConfiguredFocusEntry: TimelineEntry {
    let date: Date
    let sessionID: String?
    let state: FocusSurfaceProjection.State
}

struct ConfiguredFocusProvider: AppIntentTimelineProvider {
    func placeholder(in context: Context) -> ConfiguredFocusEntry {
        ConfiguredFocusEntry(
            date: .now,
            sessionID: nil,
            state: .ready
        )
    }

    func snapshot(
        for configuration: SelectFocusIntent,
        in context: Context
    ) async -> ConfiguredFocusEntry {
        ConfiguredFocusEntry(
            date: .now,
            sessionID: configuration.session.id,
            state: .ready
        )
    }

    func timeline(
        for configuration: SelectFocusIntent,
        in context: Context
    ) async -> Timeline<ConfiguredFocusEntry> {
        let current = await loadCurrentProjection(id: configuration.session.id)
        let entry = ConfiguredFocusEntry(
            date: .now,
            sessionID: configuration.session.id,
            state: current?.state ?? .empty
        )
        return Timeline(entries: [entry], policy: .never)
    }

    private func loadCurrentProjection(id: String) async -> FocusSurfaceProjection? {
        nil
    }
}
~~~

The configuration value is not permission to mutate the record. Resolve current
identity and authorization again in any interactive intent.

## Recipe 6: interactive widget action

Use a small App Intent with an idempotent domain service. The widget view can
show a button or toggle, but the mutation belongs to the service.

~~~swift
import AppIntents
import WidgetKit

struct ToggleFocusIntent: AppIntent {
    static var title: LocalizedStringResource = "Toggle focus session"

    @Dependency
    var focusService: FocusService

    func perform() async throws -> some IntentResult {
        guard await focusService.canUseCurrentAccount else {
            throw AppIntentError.UserActionRequired.signin
        }

        let result = try await focusService.toggleCurrentSession()
        WidgetCenter.shared.reloadTimelines(ofKind: "com.example.focus.widget")

        return .result(
            dialog: result.isRunning ? "Focus started." : "Focus stopped."
        )
    }
}
~~~

The actual dependency registration and error cases must be implemented in the
named target. Re-read current state in toggleCurrentSession so a stale widget
entry cannot overwrite a newer action.

A view-level route can be:

~~~swift
Button(intent: ToggleFocusIntent()) {
    Label("Toggle focus", systemImage: "timer")
}
~~~

Use the widget's supported interactive view/API route for the selected SDK and
test the action after the app has been terminated.

## Recipe 7: ControlWidget button

A button has no durable on/off state. It is appropriate for an idempotent action
or a route to the app.

~~~swift
import WidgetKit
import SwiftUI
import AppIntents

struct StartFocusControl: ControlWidget {
    static let kind = "com.example.focus.start-control"

    var body: some ControlWidgetConfiguration {
        StaticControlConfiguration(kind: Self.kind) {
            ControlWidgetButton(action: StartFocusIntent()) {
                Label("Start focus", systemImage: "timer")
            }
        }
        .displayName("Start Focus")
        .description("Start the current focus session.")
    }
}

struct StartFocusIntent: AppIntent {
    static var title: LocalizedStringResource = "Start focus"

    func perform() async throws -> some IntentResult {
        // Re-read authorization and current session state here.
        return .result()
    }
}
~~~

If starting focus twice is harmless, the intent should converge to “running”
rather than creating duplicate sessions. If it is not harmless, require an
app-owned confirmation route instead of hiding that complexity in a control.

## Recipe 8: ControlWidget toggle with a value provider

A toggle exposes a current Boolean state and uses a SetValueIntent to accept the
desired value.

~~~swift
struct FocusModeControl: ControlWidget {
    static let kind = "com.example.focus.mode-control"

    var body: some ControlWidgetConfiguration {
        StaticControlConfiguration(
            kind: Self.kind,
            provider: Provider()
        ) { value in
            ControlWidgetToggle(
                "Focus mode",
                isOn: value,
                action: SetFocusModeIntent()
            ) { isOn in
                Label(
                    isOn ? "On" : "Off",
                    systemImage: isOn ? "moon.fill" : "moon"
                )
            }
        }
        .displayName("Focus Mode")
        .description("Turn the local focus mode on or off.")
    }

    struct Provider: ControlValueProvider {
        var previewValue: Bool { false }

        func currentValue() async throws -> Bool {
            await FocusService.shared.isFocusModeEnabled
        }
    }
}

struct SetFocusModeIntent: SetValueIntent {
    static var title: LocalizedStringResource = "Set focus mode"

    @Parameter(title: "Enabled")
    var value: Bool

    func perform() async throws -> some IntentResult {
        try await FocusService.shared.setFocusMode(value)
        return .result()
    }
}
~~~

The exact provider isolation and dependency strategy must match the selected SDK.
The control action must validate permissions and current account state again.

## Recipe 9: configurable control outline

Use AppIntentControlConfiguration only when a person must choose a bounded target.

~~~swift
struct SessionControlConfiguration: ControlConfigurationIntent {
    static var title: LocalizedStringResource = "Focus session"

    @Parameter(title: "Session")
    var session: FocusEntity
}

struct SelectedSessionProvider: AppIntentControlValueProvider {
    typealias Value = Bool

    var previewValue: Bool { false }

    func currentValue(
        configuration: SessionControlConfiguration
    ) async throws -> Bool {
        try await FocusService.shared.isRunning(id: configuration.session.id)
    }
}

struct SelectedSessionControl: ControlWidget {
    static let kind = "com.example.focus.selected-session"

    var body: some ControlWidgetConfiguration {
        AppIntentControlConfiguration(
            kind: Self.kind,
            provider: SelectedSessionProvider()
        ) { isRunning in
            ControlWidgetToggle(
                "Focus",
                isOn: isRunning,
                action: SetSelectedSessionIntent()
            )
        }
    }
}

struct SetSelectedSessionIntent: SetValueIntent {
    static var title: LocalizedStringResource = "Set selected session"

    @Parameter(title: "Session")
    var session: FocusEntity

    @Parameter(title: "Running")
    var value: Bool

    func perform() async throws -> some IntentResult {
        try await FocusService.shared.setRunning(
            id: session.id,
            value: value
        )
        return .result()
    }
}
~~~

This is an API-shape sketch. Verify the selected SDK's
AppIntentControlValueProvider requirements and how the configuration is passed
to the action. Keep entity resolution bounded and privacy-safe.

## Recipe 10: ActivityAttributes and ActivityConfiguration

Define static attributes and compact dynamic state. The ActivityConfiguration
belongs in the widget extension.

~~~swift
import ActivityKit
import WidgetKit
import SwiftUI

struct FocusActivityAttributes: ActivityAttributes {
    public struct ContentState: Codable, Hashable {
        var phase: Phase
        var elapsedSeconds: Int
        var remainingSeconds: Int?
        var sourceRevision: String
        var isStale: Bool

        enum Phase: String, Codable, Hashable {
            case preparing
            case active
            case paused
            case completed
            case canceled
        }
    }

    let sessionID: String
    let title: String
}

struct FocusLiveActivity: Widget {
    var body: some WidgetConfiguration {
        ActivityConfiguration(for: FocusActivityAttributes.self) { context in
            VStack(alignment: .leading) {
                Text(context.attributes.title)
                    .font(.headline)
                Text(context.state.phase.rawValue.capitalized)
                Text("\(context.state.elapsedSeconds) seconds")
                    .monospacedDigit()
            }
            .activityBackgroundTint(.indigo)
            .activitySystemActionForegroundColor(.white)
        } dynamicIsland: { context in
            DynamicIsland {
                DynamicIslandExpandedRegion(.leading) {
                    Text(context.attributes.title)
                }
                DynamicIslandExpandedRegion(.trailing) {
                    Text(context.state.phase.rawValue)
                }
                DynamicIslandExpandedRegion(.bottom) {
                    Text("\(context.state.elapsedSeconds) seconds")
                        .monospacedDigit()
                }
            } compactLeading: {
                Image(systemName: "timer")
            } compactTrailing: {
                Text("\(context.state.elapsedSeconds)")
                    .monospacedDigit()
            } minimal: {
                Image(systemName: "timer")
            }
        }
    }
}
~~~

Keep the view meaningful when the activity is stale, ended, or rendered in a
different host. Verify the exact Dynamic Island regions and activity modifiers
for the selected SDK.

## Recipe 11: start, update, and end a Live Activity

The main app owns the activity lifecycle and maps it to a durable operation ID.

~~~swift
import ActivityKit

actor FocusActivityCoordinator {
    private var activity: Activity<FocusActivityAttributes>?

    func start(sessionID: String, title: String) async throws {
        guard ActivityAuthorizationInfo().areActivitiesEnabled else {
            throw FocusActivityError.liveActivitiesDisabled
        }

        let attributes = FocusActivityAttributes(
            sessionID: sessionID,
            title: title
        )

        let state = FocusActivityAttributes.ContentState(
            phase: .active,
            elapsedSeconds: 0,
            remainingSeconds: 1500,
            sourceRevision: "start-1",
            isStale: false
        )

        let content = ActivityContent(
            state: state,
            staleDate: Date().addingTimeInterval(60),
            relevanceScore: 0.5
        )

        activity = try Activity.request(
            attributes: attributes,
            content: content,
            pushType: nil
        )
    }

    func update(
        _ activity: Activity<FocusActivityAttributes>,
        state: FocusActivityAttributes.ContentState
    ) async {
        let content = ActivityContent(
            state: state,
            staleDate: Date().addingTimeInterval(60),
            relevanceScore: 0.5
        )
        await activity.update(content)
    }

    func end(
        _ activity: Activity<FocusActivityAttributes>,
        state: FocusActivityAttributes.ContentState
    ) async {
        let content = ActivityContent(
            state: state,
            staleDate: nil,
            relevanceScore: 0
        )
        await activity.end(content, dismissalPolicy: .default)
    }
}

enum FocusActivityError: Error {
    case liveActivitiesDisabled
}
~~~

This example is intentionally not a complete account/revision coordinator. The
real implementation must dedupe starts, reject out-of-order updates, reconcile
Activity.activities after relaunch, and end obsolete activities.

## Recipe 12: observe ActivityKit push tokens

Use the token sequence and send tokens through an authenticated server boundary.
Do not log the token or keep it after the activity/account relationship ends.

~~~swift
func observePushToken(
    for activity: Activity<FocusActivityAttributes>,
    send: @escaping (Data) async throws -> Void
) -> Task<Void, Never> {
    Task {
        for await token in activity.pushTokenUpdates {
            do {
                try await send(token)
            } catch {
                // Record a redacted category and retry by policy.
            }
        }
    }
}
~~~

Token rotation, APNs environment, account sign-out, server deduplication, and
payload revision ordering are part of the proof route.

## Recipe 13: WidgetKit push handler outline

WidgetKit push updates complement timelines. The exact registration and
configuration modifier must match the selected SDK.

~~~swift
struct FocusWidgetPushHandler: WidgetPushHandler {
    func pushTokenDidChange(
        _ pushInfo: WidgetPushInfo,
        widgets: [WidgetInfo]
    ) {
        // Send a redacted token/configuration relationship to the server.
        // Remove old configuration records when widgets are removed.
    }
}

struct FocusServerWidget: Widget {
    var body: some WidgetConfiguration {
        StaticConfiguration(
            kind: "com.example.focus.server-widget",
            provider: FocusProvider()
        ) { entry in
            FocusWidgetView(entry: entry)
        }
        .pushHandler(FocusWidgetPushHandler.self)
    }
}
~~~

The server must use the documented APNs widgets push type/topic/payload and the
app must retain a timeline fallback.

## Recipe 14: AI proposal to committed projection

Keep the model output typed and do not let a system surface commit it directly.

~~~swift
struct FocusProposal: Codable, Sendable {
    let sourceRevision: String
    let suggestedLabel: String
    let suggestedRemainingSeconds: Int?
    let modelIdentifier: String
    let needsReview: Bool
}

struct CommitFocusProposalIntent: AppIntent {
    static var title: LocalizedStringResource = "Apply focus suggestion"

    let proposal: FocusProposal

    func perform() async throws -> some IntentResult {
        let current = try await FocusService.shared.currentSourceRevision()

        guard current == proposal.sourceRevision else {
            throw AppIntentError.UserActionRequired.confirmation
        }

        guard !proposal.needsReview else {
            throw AppIntentError.UserActionRequired.confirmation
        }

        try await FocusService.shared.commit(
            label: proposal.suggestedLabel,
            remainingSeconds: proposal.suggestedRemainingSeconds,
            modelIdentifier: proposal.modelIdentifier
        )

        WidgetCenter.shared.reloadAllTimelines()
        return .result(dialog: "Focus suggestion applied.")
    }
}
~~~

In a real app, proposal transport must be privacy-reviewed and bounded. For
irreversible or external effects, use a main-app review screen rather than
passing the proposal into a control.

## Recipe 15: projection fallback selector

Centralize surface state selection so widgets, controls, and activities do not
invent different privacy or freshness rules.

~~~swift
enum SurfaceState {
    case ready(FocusSurfaceProjection)
    case stale(FocusSurfaceProjection)
    case denied
    case empty
    case error
}

func surfaceState(
    projection: FocusSurfaceProjection?,
    now: Date = .now,
    isAuthorized: Bool
) -> SurfaceState {
    guard isAuthorized else { return .denied }
    guard let projection else { return .empty }

    if let staleAt = projection.staleAt, staleAt <= now {
        return .stale(projection)
    }

    switch projection.state {
    case .ready:
        return .ready(projection)
    case .stale:
        return .stale(projection)
    case .denied:
        return .denied
    case .empty:
        return .empty
    default:
        return .error
    }
}
~~~

A deterministic fallback is more trustworthy than a generated “probably current”
status.

## Recipe 16: proof fixture

Use synthetic state to exercise surface paths without exposing personal content.

~~~swift
struct SurfaceFixture {
    static let stale = FocusSurfaceProjection(
        schemaVersion: 1,
        revision: 4,
        updatedAt: Date(timeIntervalSince1970: 1_000),
        staleAt: Date(timeIntervalSince1970: 1_100),
        state: .stale,
        title: "Private focus",
        value: "00:12",
        detail: "Last known",
        deepLink: URL(string: "focus://session/fixture"),
        isPrivate: true
    )
}
~~~

The fixture is useful for previews and unit tests. It is not evidence that a real
device shows the correct surface, that a push arrived, or that a release archive
contains the intended target.

## Source checklist

When adapting a recipe, revisit:

- provider protocol and async/sync requirements;
- supported widget families and host contexts;
- background-removal and rendering-mode APIs;
- App Intent availability and target/process execution;
- ControlWidget provider/configuration requirements;
- ActivityKit authorization, stale, update, end, and push signatures;
- APNs capability, topic, token, and environment;
- target membership, App Groups, privacy, and accessibility;
- selected SDK and physical-device behavior.

## Sources

- [WidgetKit](https://developer.apple.com/documentation/widgetkit/)
- [Creating a widget extension](https://developer.apple.com/documentation/widgetkit/creating-a-widget-extension)
- [TimelineProvider](https://developer.apple.com/documentation/widgetkit/timelineprovider)
- [AppIntentTimelineProvider](https://developer.apple.com/documentation/widgetkit/appintenttimelineprovider)
- [Making a configurable widget](https://developer.apple.com/documentation/widgetkit/making-a-configurable-widget)
- [Keeping a widget up to date](https://developer.apple.com/documentation/widgetkit/keeping-a-widget-up-to-date/)
- [WidgetCenter](https://developer.apple.com/documentation/widgetkit/widgetcenter)
- [Adding interactivity to widgets and Live Activities](https://developer.apple.com/documentation/widgetkit/adding-interactivity-to-widgets-and-live-activities)
- [Updating widgets with WidgetKit push notifications](https://developer.apple.com/documentation/widgetkit/updating-widgets-with-widgetkit-push-notifications)
- [Displaying the right widget background](https://developer.apple.com/documentation/widgetkit/displaying-the-right-widget-background)
- [Optimizing your widget for accented rendering mode and Liquid Glass](https://developer.apple.com/documentation/widgetkit/optimizing-your-widget-for-accented-rendering-mode-and-liquid-glass)
- [ControlWidget](https://developer.apple.com/documentation/swiftui/controlwidget)
- [ControlWidgetButton](https://developer.apple.com/documentation/widgetkit/controlwidgetbutton)
- [ControlWidgetToggle](https://developer.apple.com/documentation/widgetkit/controlwidgettoggle)
- [StaticControlConfiguration](https://developer.apple.com/documentation/widgetkit/staticcontrolconfiguration)
- [ControlValueProvider](https://developer.apple.com/documentation/widgetkit/controlvalueprovider)
- [AppIntentControlConfiguration](https://developer.apple.com/documentation/widgetkit/appintentcontrolconfiguration)
- [ActivityKit](https://developer.apple.com/documentation/activitykit/)
- [Activity](https://developer.apple.com/documentation/activitykit/activity)
- [ActivityAuthorizationInfo](https://developer.apple.com/documentation/activitykit/activityauthorizationinfo)
- [ActivityContent](https://developer.apple.com/documentation/activitykit/activitycontent)
- [ActivityConfiguration](https://developer.apple.com/documentation/widgetkit/activityconfiguration)
- [Displaying live data with Live Activities](https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities)
- [Starting and updating Live Activities with ActivityKit push notifications](https://developer.apple.com/documentation/activitykit/starting-and-updating-live-activities-with-activitykit-push-notifications)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [App Groups](https://developer.apple.com/documentation/xcode/configuring-app-groups)
