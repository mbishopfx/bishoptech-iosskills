# WidgetKit, ActivityKit, and control surface capability route

## Capability contract

Use this route when an app needs to carry a small, current projection into a
system space or let a person perform one bounded action without opening the app.

The route has three independent outputs:

1. a durable app-owned state transition;
2. a compact system-surface projection;
3. a proof record showing where the system surface actually ran.

Do not implement the widget, control, or Live Activity as the source of truth.
They are projections with different refresh and lifetime rules.

## Start with the surface decision

| Question | Choose |
| --- | --- |
| Is the information useful without an immediate action? | Widget |
| Is the action one tap and safe when repeated? | ControlWidgetButton |
| Is the state explicitly on/off? | ControlWidgetToggle |
| Does the event persist and change over time? | Live Activity |
| Does the user need search, editing, or many choices? | Main app plus App Intents/deep link |
| Does the event require server updates? | ActivityKit push or WidgetKit push, with local fallback |
| Is the result generated or inferred? | Main-app proposal/review/commit, then projection |

A surface is a poor fit when the feature depends on a full editor, private
context that cannot be redacted, a multi-step consent flow, an unbounded model
call, or a live network connection inside an extension.

## Project and target plan

For a typical app:

    AppTarget
      ├── DomainModels
      ├── DomainServices
      ├── ProjectionStore
      ├── AppIntents
      ├── MainAppViews
      └── WidgetExtension
            ├── WidgetBundle
            ├── Widget definitions
            ├── Timeline providers
            ├── ControlWidget definitions
            └── ActivityConfiguration

Keep the following contracts explicit:

| Contract | Owner |
| --- | --- |
| Domain record and authorization | AppTarget domain service |
| Versioned compact projection | Shared projection layer |
| Shared storage/transport | App Group or documented service boundary |
| Timeline generation | Widget extension |
| Widget interaction intent | App Intents layer executable in the selected target |
| Control value/action | ControlWidget and App Intent |
| Live Activity lifecycle | AppTarget ActivityKit coordinator |
| Live Activity view | Widget extension |
| Remote push token/server mapping | Authenticated server boundary |
| AI proposal and commit | Main app/service, not the renderer |

If the widget extension and main app share files or SwiftData/CloudKit state,
define migration, locking, version, and sign-out behavior. A shared container
must not expose a private account's records to another process or account.

## Versioned projection model

Use a small Codable/Sendable projection that can be read by the surface without
hydrating the whole domain model:

~~~swift
struct SurfaceProjection: Codable, Sendable {
    enum State: String, Codable, Sendable {
        case empty
        case preparing
        case ready
        case updating
        case stale
        case offline
        case denied
        case error
        case ended
    }

    let schemaVersion: Int
    let projectionRevision: Int64
    let sourceRevision: String?
    let updatedAt: Date?
    let staleAt: Date?
    let state: State
    let title: String?
    let value: String?
    let detail: String?
    let deepLink: URL?
    let isSensitive: Bool
    let modelIdentifier: String?
}
~~~

The renderer should select a safe view from state and privacy context. It should
not infer “ready” merely because title is non-nil.

Store a redacted projection or a lock-safe placeholder when the user signs out,
revokes permission, or marks the content private. Delete or invalidate stale
shared files according to the app's privacy policy.

## Route A: static widget

Choose a static widget when the kind of content is fixed and no person-selected
configuration is needed.

1. Add a Widget Extension target.
2. Define a stable kind string.
3. Implement TimelineProvider with placeholder, snapshot, and timeline.
4. Build a Timeline of compact entries.
5. Declare supported families.
6. Declare a removable container background.
7. Add widgetURL or Link only when the main app can reconstruct the route.
8. Reload only when the displayed projection changes.
9. Add redaction, privacy, and accessibility states.
10. Test outside the debugger so WidgetKit budgets and process lifetime are real.

Use StaticConfiguration for a fixed configuration. Keep network loading bounded
and prefer app-prepared shared projection data.

## Route B: configurable widget

Choose a configurable widget when the person selects one bounded entity or
option, such as a project, timer, place, or account-safe view.

1. Define an App Intent that conforms to WidgetConfigurationIntent.
2. Give each parameter a stable, localized title and bounded query.
3. Use AppIntentConfiguration.
4. Implement AppIntentTimelineProvider.
5. Resolve the selected identifier to current projection data.
6. Include the selected value in the timeline entry, not a private persistence
   context.
7. Handle deleted, unauthorized, and signed-out selections.
8. Offer recommendations only when they are useful and privacy-safe.
9. Rebuild the timeline after relevant domain changes.
10. Prove the edit flow on a physical device.

The configuration is not an authorization token. Recheck account and permission
when producing the entry and again when an interactive action runs.

## Route C: interactive widget

Choose interaction when a person can complete the action with one bounded intent.

1. Define an AppIntent with a stable title and localized errors.
2. Make the operation idempotent and safe when called twice.
3. Read current state at execution time.
4. Perform the smallest domain mutation.
5. Write a new projection revision.
6. Reload the relevant widget kind or allow the system update path.
7. Mark changing views with invalidatableContent when that improves feedback.
8. Return a result that explains success, no-op, denial, or repair.
9. Test app terminated, account changed, permission denied, and repeated tap.
10. Confirm accessibility names and values after the update.

A Button is an action signal, not a persistent state display. Use a Toggle when
the person needs to see and set an on/off value.

## Route D: ControlWidget

Choose a control for a small action/value pair in a system space.

### Static control

1. Add a Widget Extension target with control support.
2. Define a stable kind.
3. Use StaticControlConfiguration when no setup is needed.
4. Use ControlWidgetButton or ControlWidgetToggle.
5. Supply a ControlValueProvider when the template needs a current value.
6. Use a previewValue that is safe and deterministic.
7. Use currentValue() for a bounded current read.
8. Implement the App Intent or SetValueIntent.
9. Add display name, description, status, and action hint as appropriate.
10. Test Control Center, Lock Screen, Action button, locked state, and varied
    control sizes.

### Configurable control

1. Define a ControlConfigurationIntent with one bounded choice.
2. Use AppIntentControlConfiguration.
3. Use AppIntentControlValueProvider when the current value depends on the
   selected configuration.
4. Re-resolve the configuration at action time.
5. Handle missing or revoked configuration safely.
6. Keep the configuration editor shorter than a normal app screen.
7. Avoid exposing private titles or model output in the control gallery.
8. Verify the control kind remains stable across updates.

A control should finish quickly or return a clear actionable result. It is not a
general-purpose background job runner.

## Route E: local Live Activity

Choose a Live Activity for a meaningful event with a bounded beginning, middle,
and end.

1. Add or reuse a Widget Extension with Live Activity support.
2. Enable Supports Live Activities in the app target configuration as required.
3. Define ActivityAttributes and a nested ContentState.
4. Build an ActivityConfiguration in the widget extension.
5. Check ActivityAuthorizationInfo.areActivitiesEnabled.
6. Request an Activity with initial ActivityContent.
7. Store a domain operation ID and map it to the Activity ID.
8. Update with new ActivityContent when the source changes.
9. Set staleDate when the source may stop updating.
10. End when complete, canceled, unauthorized, or no longer useful.
11. Reconcile Activity.activities after relaunch.
12. Add an app deep link and verify cold-launch restoration.

ActivityKit state is not a job queue. The app must own progress, persistence,
retry, cancellation, and completion.

## Route F: remote Live Activity updates

Use ActivityKit push notifications when a server is authoritative or the app
cannot remain active for the event.

1. Decide whether the activity starts locally or via push-to-start support in
   the selected SDK.
2. Enable remote notification capability and configure the APNs environment.
3. Observe and rotate ActivityKit push tokens.
4. Associate each token with a user/device/activity record on the server.
5. Authenticate the server connection and minimize token/data retention.
6. Include a monotonic event/revision identifier in server state.
7. Reject or ignore out-of-order updates.
8. Set stale dates in the payload and end obsolete activities.
9. Handle APNs errors, token changes, revoked Live Activity authorization,
   account sign-out, and server reconciliation.
10. Test real sandbox/TestFlight delivery on a physical device.

Do not assume a server push is instantaneous or delivered exactly once. The
projection must remain truthful when pushes are delayed, duplicated, or missing.

## Route G: WidgetKit push updates

Use WidgetKit push updates as an additional refresh mechanism for server-backed
widgets.

1. Add the push capability to the widget extension.
2. Implement WidgetPushHandler.
3. Persist and rotate WidgetKit push tokens.
4. Register the configured-widget relationship with the server.
5. Send APNs with the widgets push type and the required topic/payload.
6. Keep a timeline fallback for periods without push delivery.
7. Treat push as budgeted and opportunistic.
8. Reload only the affected widget kind when possible.
9. Remove device/configuration records after token or account changes.
10. Verify delivery, delay, deduplication, and redaction.

WidgetKit push updates do not replace a correct timeline and do not guarantee an
immediate render.

## Route H: on-device AI to a surface

Use AI when it makes a bounded projection more useful, not when it replaces
deterministic domain state.

    source records
      -> local model/Vision/Speech/Foundation Models proposal
      -> typed validation
      -> freshness/authorization/policy check
      -> optional user review
      -> domain commit
      -> projection revision
      -> widget/control/activity

### Proposal contract

The proposal should include:

- source record IDs;
- source revision or capture timestamp;
- model/framework identifier;
- availability/fallback path;
- typed fields with bounded size;
- uncertainty or “needs review” state;
- policy flags for sensitive content;
- no private prompt/transcript in the projection unless explicitly needed.

### Commit contract

Before a control or interactive widget commits an AI-related action:

- re-read the current record;
- verify account and authorization;
- check the proposal's source revision;
- confirm the action is allowed in the current mode;
- ask for confirmation for irreversible, external, financial, health, or
  communication side effects;
- commit idempotently;
- record the committed projection revision.

The system surface should never silently convert “model suggested” into “user
approved.”

## Deep-link and handoff route

For widgetURL, Link, and Live Activity taps:

1. encode a stable route identifier, not a transient view index;
2. treat the URL as untrusted input;
3. resolve current account and authorization;
4. reconstruct navigation from a cold launch;
5. show a missing/deleted/unauthorized route instead of opening a different record;
6. preserve the originating surface's context in the app screen;
7. keep the route accessible by VoiceOver and keyboard/controller input.

A deep link proves navigation only when a signed device run exercises it from the
real host surface.

## Capability-specific fallback table

| Failure | Widget | Control | Live Activity |
| --- | --- | --- | --- |
| Main app terminated | Read projection | Intent executes in allowed target or errors | Activity remains visible from last state |
| Shared store unavailable | Last-known/stale state | Safe no-op or repair route | Stale state and app handoff |
| User signed out | Redacted/empty | Require sign-in or no-op | End or redact according to policy |
| Permission revoked | Safe denied state | Require permission/authentication | End or show denied state |
| AI unavailable | Source facts/fallback | Deterministic action only | Source status, no fabricated insight |
| Network unavailable | Local cache/timeline | Local action or offline result | Local update if valid; otherwise stale |
| Push delayed | Timeline/reload hint | Current value provider | Stale date and reconciliation |
| Record deleted | Empty/missing route | Refuse mutation | End activity |
| Process terminated mid-action | Idempotent retry | Current state re-read | App reconciliation on next launch |

## Minimum proof package

For each route preserve:

- selected SDK/Xcode and deployment target;
- target names and entitlements;
- source/compile check;
- deterministic fixture or unit test;
- preview/simulator screenshots where useful;
- signed physical-device invocation;
- lock/privacy/accessibility results;
- process termination and relaunch result;
- APNs/token/server evidence where applicable;
- archive target/resource inspection;
- known limitations and deferred claims.

## Sources

- [WidgetKit](https://developer.apple.com/documentation/widgetkit/)
- [Creating a widget extension](https://developer.apple.com/documentation/widgetkit/creating-a-widget-extension)
- [Making a configurable widget](https://developer.apple.com/documentation/widgetkit/making-a-configurable-widget)
- [AppIntentTimelineProvider](https://developer.apple.com/documentation/widgetkit/appintenttimelineprovider)
- [Keeping a widget up to date](https://developer.apple.com/documentation/widgetkit/keeping-a-widget-up-to-date/)
- [WidgetCenter](https://developer.apple.com/documentation/widgetkit/widgetcenter)
- [Adding interactivity to widgets and Live Activities](https://developer.apple.com/documentation/widgetkit/adding-interactivity-to-widgets-and-live-activities)
- [Updating widgets with WidgetKit push notifications](https://developer.apple.com/documentation/widgetkit/updating-widgets-with-widgetkit-push-notifications)
- [Creating controls to perform actions across the system](https://developer.apple.com/documentation/widgetkit/creating-controls-to-perform-actions-across-the-system)
- [Adding refinements and configuration to controls](https://developer.apple.com/documentation/widgetkit/adding-refinements-and-configuration-to-controls)
- [ControlWidget](https://developer.apple.com/documentation/swiftui/controlwidget)
- [ControlWidgetButton](https://developer.apple.com/documentation/widgetkit/controlwidgetbutton)
- [ControlWidgetToggle](https://developer.apple.com/documentation/widgetkit/controlwidgettoggle)
- [ControlValueProvider](https://developer.apple.com/documentation/widgetkit/controlvalueprovider)
- [AppIntentControlConfiguration](https://developer.apple.com/documentation/widgetkit/appintentcontrolconfiguration)
- [ActivityKit](https://developer.apple.com/documentation/activitykit/)
- [Displaying live data with Live Activities](https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities)
- [Activity](https://developer.apple.com/documentation/activitykit/activity)
- [ActivityContent](https://developer.apple.com/documentation/activitykit/activitycontent)
- [ActivityAuthorizationInfo](https://developer.apple.com/documentation/activitykit/activityauthorizationinfo)
- [ActivityConfiguration](https://developer.apple.com/documentation/widgetkit/activityconfiguration)
- [Starting and updating Live Activities with ActivityKit push notifications](https://developer.apple.com/documentation/activitykit/starting-and-updating-live-activities-with-activitykit-push-notifications)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [App Groups](https://developer.apple.com/documentation/xcode/configuring-app-groups)
