# App Intents, Widgets, and Live Activities

## Capability

App Intents is the route for expressing app actions and entities to system experiences such as Siri, Shortcuts, Apple Intelligence, widgets, controls, and other supported surfaces. WidgetKit and ActivityKit extend the app without making the main app a permanently running process.

## System-surface route

1. Start with a user-facing verb: create, complete, start, pause, log, search, or show.
2. Model the action as an `AppIntent` with localized title, description, parameters, and a deterministic `perform()` method.
3. Model selectable domain objects as `AppEntity` and provide an `EntityQuery` when the system needs to resolve them.
4. Donate or expose the action through App Shortcuts when appropriate.
5. Choose the smallest surface: widget, control, Live Activity, Shortcuts, Siri, or an in-app deep link.
6. Keep the actual domain operation in a shared service that the app and extension can call safely.

Illustrative action boundary:

```swift
import AppIntents

struct MarkCaptureReviewed: AppIntent {
    static var title: LocalizedStringResource = "Mark capture reviewed"
    static var description = IntentDescription("Marks a saved capture as reviewed.")

    @Parameter(title: "Capture")
    var capture: CaptureEntity

    func perform() async throws -> some IntentResult {
        try await CaptureActions.markReviewed(id: capture.id)
        return .result()
    }
}
```

The example assumes an `AppEntity` and shared action service that still need to be designed. An intent should not mutate SwiftUI view state directly; it should call a domain operation and return a result the system can understand.

## Surface selection

| Surface | Best for | Main constraint |
| --- | --- | --- |
| App Shortcut | A small set of memorable actions | Titles, phrases, and parameters must make sense outside the app. |
| Widget | Glanceable state and a few direct actions | Timeline/rendering model and extension process limit live app assumptions. |
| Control | A frequent, low-friction toggle or action | The action must be safe and clear from a compact system surface. |
| Live Activity | Time-bounded, changing progress or status | Activity lifecycle, stale content, and update budget must be designed. |
| Siri/Apple Intelligence action | Natural-language discovery and execution | Parameters, entity resolution, authorization, and safety must be explicit. |

## Widget and Live Activity boundary

Interactive buttons and toggles use App Intents. Widget code runs in an extension process and renders archived/timeline-driven views; it cannot assume that arbitrary app bindings or an always-live model context are available. Live Activities share a related extension boundary but update through ActivityKit rather than a normal WidgetKit timeline.

For an interaction, persist the domain change before returning from `perform()`, then let the system reload or refresh the surface. If the write fails, return or render an honest stale/error state.

## Boundaries and failure modes

- Localize intent titles and parameter names; these are user-facing system vocabulary.
- Limit intent side effects to operations the person has authorized and expects from the surface.
- Do not expose private records through entity queries without an access check.
- Widgets and Live Activities can be stale, unavailable, removed, or rendered under different size and context constraints.
- App Intents availability and behavior varies by OS, surface, device, and system configuration; verify the selected deployment target.
- A deep link is a navigation handoff, not permission to bypass authentication, purchase, or safety gates.

## Verification route

- Run the intent from the app, Shortcuts, and each supported system surface.
- Test parameter resolution with missing, ambiguous, deleted, and unauthorized entities.
- Test the extension with the app terminated and its shared store in a known state.
- Verify WidgetKit timeline reloads and Live Activity start/update/end behavior on a physical device.
- Inspect accessibility labels, localization, privacy descriptions, and the behavior when an action cannot complete.

## Outcome-first surface map

Choose the surface by the user outcome and lifecycle, not by the visual novelty of the surface:

| User outcome | Smallest useful route | Why it fits | Proof boundary |
| --- | --- | --- | --- |
| Perform one memorable action by voice or phrase | `AppIntent` plus `AppShortcut` | The system can discover and execute a focused verb | Intent metadata, phrase, parameter resolution, authorization, and system execution must be tested outside the main app screen |
| Find a user-owned record through system search | `AppEntity`, `EntityQuery`, and indexing/donation route | The system gets a stable display representation and identifier | Privacy filtering, deleted records, ambiguous matches, and authentication are still app responsibilities |
| See status at a glance | WidgetKit timeline or a Live Activity | The system owns when and where the content appears | Timeline budgets, stale state, extension process, data freshness, and device-family support are target-specific |
| Complete a safe frequent toggle/action without opening the app | Interactive widget or `ControlWidget` | Direct interaction fits a small, repeatable action | The intent must finish and persist state before returning; locked-device and remote update behavior need proof |
| Track a time-bounded event | ActivityKit Live Activity | The surface can remain visible while the event is relevant | Start/update/end, stale content, alert frequency, push configuration, and dismissal behavior require system/device proof |
| Open the right in-app context | `Link`, `widgetURL`, `OpenIntent`, or scene routing | The system surface can hand off to an explicit destination | Deep links must preserve authentication, permission, purchase, and safety gates |

Avoid adding a widget, control, or Live Activity when the feature is not useful outside the app. A system surface that only launches the home screen adds indirection; use a direct link to the relevant destination or keep the action in the app.

## App Intent contract

An App Intent is a system-facing use case, not a view callback. Keep the contract narrow and make the result honest:

1. Name the user-facing verb in localized metadata.
2. Declare only the parameters needed for the operation.
3. Resolve `AppEntity` values through an access-checked query or accept an explicitly supplied stable identifier.
4. Validate authorization, availability, and current domain state inside `perform()`.
5. Perform the domain operation through a shared service/repository boundary.
6. Persist or reconcile the result before returning when the surface depends on the new state.
7. Return a result or error that the system can present and that the app can test.

Keep view state out of `perform()`. An intent can request an app destination or return a dialog/snippet result where supported, but it should not reach into a SwiftUI view instance or assume that the app scene is in memory.

### Parameter and entity safety

- Use an `AppEntity` display representation that reveals only what the person is allowed to choose or see in a system surface.
- Make deleted, archived, signed-out, and ambiguous records resolve to a clear failure or selection route.
- Treat identifiers passed from Shortcuts, widgets, or external system context as untrusted input to the domain layer.
- Do not expose private notes, health data, precise location, payment data, or communication content merely because an entity is convenient to query.
- Keep parameter summaries and phrases natural in the supported locales; system vocabulary is product copy.

## App Shortcuts and Apple Intelligence boundary

App Shortcuts make selected intents easy to discover through Siri, Spotlight, Shortcuts, and supported hardware entry points. Design the shortcut as a complete request that can be understood without the app’s visual context:

- The phrase should be short, memorable, and include the app name where required.
- The full dialogue/result text should contain critical information for audio-only interaction.
- Parameters should have meaningful summaries, defaults, and resolution behavior.
- A shortcut that starts a Live Activity should make the activity’s time-bounded purpose clear.
- A shortcut that opens the app should route to a precise destination, not a generic home screen.
- Treat Apple Intelligence discovery as system-mediated; do not promise invocation, ranking, model behavior, or language availability that the app has not verified.

The app’s direct Foundation Models path and its App Intents/system-surface path are related but not interchangeable. An App Intent expresses an action or entity for system use; it does not imply that the app controls Apple Intelligence’s UI, model choice, or context selection.

## Widget lifecycle and timeline discipline

Widgets are archived, timeline-driven views in an extension process. The view cannot assume that a live app binding, in-memory model context, network connection, or current user session is available when the system renders it.

### Timeline rules

- Prepare compact, privacy-safe data in a shared store or supported data boundary.
- Choose a refresh policy that reflects the data’s predictability: future entries, `after`, or `never` plus explicit reload.
- Treat the requested date as the earliest time WidgetKit may request a refresh, not a guaranteed render deadline.
- Reload only when the widget’s displayed data changed; unnecessary reloads waste budget and can reduce reliability.
- Show stale, signed-out, unavailable, or permission-limited states instead of silently presenting old data as current.
- Use a deep link to the relevant app scene when the person needs more context.

### Interactive widget behavior

Buttons and toggles use App Intents. The intent must finish the domain operation and store the new state before it returns so the system can request the next timeline. A toggle may update optimistically while the operation is pending; if synchronization fails, the next rendered state must correct the optimistic value and explain the failure.

For a widget hosted on another device or context, such as an iPhone widget on Mac, allow for additional delay. Mark only important changing views as invalidatable content where the current SDK supports it, and design copy that remains honest while the result is pending.

## Live Activity lifecycle

Live Activities are for relevant, time-bounded information—not a general-purpose notification feed or a permanent dashboard. ActivityKit updates them from the app or through ActivityKit push notifications; they do not use a normal WidgetKit timeline.

Model the lifecycle explicitly:

`not requested -> active -> updated -> stale or interrupted -> ended -> dismissed`

For each transition, define:

- the current content state and timestamp/freshness;
- what happens with no network or a delayed push;
- whether the person can start another activity;
- the user-visible end reason;
- whether the final state remains visible after ending;
- whether an alert is necessary and how often it may interrupt.

Use a stale date and stale presentation when a Live Activity can outlive a reliable update source. Use ActivityKit push tokens, server authentication, payload encoding, update frequency, and push entitlement as separate infrastructure gates; a local ActivityKit request does not prove remote update delivery.

### Live Activity interaction

Keep interactive buttons/toggles limited to essential actions directly related to the visible event. A Live Activity tap should open the matching app scene. If the action is a start/pause/stop or another short transition, expose it through a `LiveActivityIntent` and persist the result before returning. Do not put a full editor, unrelated navigation, or a destructive action with ambiguous wording in a compact Live Activity.

## Controls and Control Center

Controls live in highly constrained system surfaces such as Control Center, the Lock Screen, and the Action button. Offer a control only for a frequent, safe, immediately understandable action:

- Use `ControlWidgetButton` for a focused action.
- Use `ControlWidgetToggle` or the value-provider route for a true on/off state.
- Use a descriptive symbol because the title/value may not always be visible.
- Represent both on and off states with meaningful symbols and labels.
- Update state after interaction, completion, local reload, or supported remote push.
- Finish the action and save state before the intent returns so the system can query the current value.
- If the action should open the app, use an `OpenIntent` and route to the specific destination.

Do not make a control a miniature app or use it as a shortcut to a generic landing screen. Control configuration, push updates, device availability, and the system’s placement UI require target-specific testing.

## Shared data and extension architecture

Use a small, explicit boundary for data shared by the app and its extensions:

| Boundary | Keep there | Do not assume |
| --- | --- | --- |
| Shared store or app-group data | Minimum display state, stable IDs, freshness, and pending/error flags | Every private record or live service object belongs there |
| Domain service | Validation, authorization, mutation, reconciliation, and cancellation | A view or extension owns business rules |
| App Intent | User-facing metadata, parameter decoding, invocation, result/error | A system invocation has the same process or UI as the app |
| Widget provider | Snapshot/timeline preparation and compact rendering | The provider can run arbitrary app code at render time |
| ActivityKit coordinator | Start/update/end requests, stale state, push-token boundary | A push was delivered or a Live Activity is still relevant |
| SwiftUI surface | Layout, semantic controls, labels, deep links, accessibility | It can keep a process alive or guarantee a refresh deadline |

When a user signs out, loses permission, deletes a record, or changes accounts, reload every affected system surface and ensure the shared representation does not leak the previous account’s content.

## API and process route matrix

Use the API seam that matches the system invocation. The process that renders a surface is part of the contract and must be recorded in the target plan.

| API seam | Input/output contract | Process and lifecycle question |
| --- | --- | --- |
| `AppIntent.perform()` | Typed parameters in, validated `IntentResult`/error out | Does the system run it in the app target or an extension process? Can it complete without a scene, network, or in-memory service? |
| `AppEntity` + `EntityQuery` | Stable identifier, display representation, suggested/default entities, and lookup results | Can the query enforce account/permission scope and return a useful result after the app process was terminated? |
| `AppShortcutsProvider` | Localized phrases and discoverable intent metadata | Are phrases, parameter summaries, and supported locales tested outside the app’s visual context? |
| `AppIntentTimelineProvider` | `placeholder`, `snapshot(for:in:)`, and `timeline(for:in:)` entries plus configuration intent | Can the provider build a privacy-safe archived representation from compact shared data with no live binding? |
| `WidgetConfigurationIntent` | User-selected widget configuration values | Are values assigned before the interactive widget intent runs, and are deleted/unauthorized selections handled? |
| `ControlWidgetButton` / `ControlWidgetToggle` | Small action or persisted on/off/value state | Does the intent finish and save before the system queries the value again? What happens on the locked device or when the app is unavailable? |
| `ActivityAttributes` / `Activity` | Static attributes plus changing `ContentState`, started/updated/ended locally or by push | What is the stale/end contract, and which app/server target owns the push token and authenticated update? |
| `LiveActivityIntent` | A short, activity-specific mutation | Can it validate and persist the transition without presenting a full app UI, and does the next rendered state reflect failure? |

For an interactive widget, Apple’s route is to add the custom `AppIntent` to the widget extension; add it to the app target too when the same action is reused in the app. The framework reloads the widget timeline after the interaction, but the intent still has to finish the domain write before returning and handle errors with a truthful stale/error state. If the intent conforms to a system-defined foreground-running protocol or requests the app to open, verify the process and target behavior for the selected SDK rather than assuming all intents run in the app.

## Surface-to-target matrix

| Surface | Owning target/process | Shared boundary | Minimum system proof |
| --- | --- | --- | --- |
| App Intent used only inside the app | App target | Domain use case and authorization service | Unit/fixture invocation plus an in-app user task. |
| App Intent used by widget interaction | Widget extension, or app process for the documented foreground route | Small shared store/projection and idempotent use case | Extension invocation after app termination, persistence before return, timeline reload, and error recovery. |
| App Entity/Shortcuts | App Intents declarations in the target that exposes them | Stable IDs, privacy-filtered display representations, query adapter | Shortcuts/system resolution with signed build, account state, deleted records, and localization. |
| Widget | Widget extension | Snapshot/timeline projection, freshness, deep link | All supported families, placeholder/snapshot/timeline, stale/privacy states, reload behavior, and physical device. |
| Control | Widget extension/control target | Value provider and short mutation intent | Placement/invocation in the selected system surfaces, locked-device behavior, and supported device family. |
| Live Activity | App target for ActivityKit coordinator plus widget extension UI; optional server/APNs route | Activity attributes/content state and authenticated push boundary | Start/update/end locally, stale/interrupted flow, Dynamic Island/Lock Screen/paired surface, and push route if used. |

Treat the shared projection as disposable presentation state. Rebuild it after account changes, deletion, permission loss, migration, or a failed mutation; never use an extension’s cached text as the app’s canonical domain truth.

## Verification matrix

| Route | Preview/simulator can cover | Physical/device/release proof still needed |
| --- | --- | --- |
| App Intent | Metadata, parameter fixtures, domain unit tests, deterministic perform results | Actual Shortcuts/Siri/system discovery, authorization, localization, and supported device surfaces |
| App Entity/query | Matching, missing/ambiguous/deleted records, privacy filters | Real Spotlight/system resolution and account/permission state |
| Widget | Timeline fixtures, snapshots, families, empty/stale/error states | Refresh budget behavior, extension lifecycle, deep links, real device sizes, signed-out state, and update timing |
| Interactive widget | Intent route and deterministic shared-store update | Locked device, iPhone-on-Mac delay, optimistic toggle correction, extension signing, and physical interaction |
| Live Activity | Content states, layout regions, start/update/end fixtures | Authorization, Dynamic Island/Lock Screen/paired surfaces, push tokens/APNs, stale and interruption behavior |
| Control | Provider preview and action state | Control Center/Lock Screen/Action button placement, value refresh, locked-device rules, and supported hardware |

No screenshot, local simulator, or successful `perform()` call proves that the system will discover, schedule, refresh, deliver, or display the surface in production.

## Sources

- [App Intents](https://developer.apple.com/documentation/appintents/)
- [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- [EntityQuery](https://developer.apple.com/documentation/appintents/entityquery)
- [App Shortcuts](https://developer.apple.com/documentation/appintents/app-shortcuts)
- [Widgets, Live Activities, and Controls](https://developer.apple.com/documentation/appintents/widgets-live-activities-and-controls)
- [Adding interactivity to widgets and Live Activities](https://developer.apple.com/documentation/widgetkit/adding-interactivity-to-widgets-and-live-activities)
- [Developing a WidgetKit strategy](https://developer.apple.com/documentation/WidgetKit/Developing-a-WidgetKit-strategy)
- [Timeline](https://developer.apple.com/documentation/widgetkit/timeline)
- [TimelineProvider](https://developer.apple.com/documentation/widgetkit/timelineprovider)
- [Keeping a widget up to date](https://developer.apple.com/documentation/widgetkit/keeping-a-widget-up-to-date)
- [Reloading widget timelines](https://developer.apple.com/documentation/widgetkit/widgetcenter/reloadtimelines%28ofkind%3A%29)
- [Controls collection](https://developer.apple.com/documentation/widgetkit/controls-collection)
- [Creating controls to perform actions across the system](https://developer.apple.com/documentation/widgetkit/creating-controls-to-perform-actions-across-the-system)
- [ControlWidgetButton](https://developer.apple.com/documentation/widgetkit/controlwidgetbutton)
- [ControlWidgetToggle](https://developer.apple.com/documentation/widgetkit/controlwidgettoggle)
- [ActivityKit](https://developer.apple.com/documentation/activitykit/)
- [ActivityAttributes](https://developer.apple.com/documentation/activitykit/activityattributes)
- [Activity](https://developer.apple.com/documentation/activitykit/activity)
- [Displaying live data with Live Activities](https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities)
- [Starting and updating Live Activities with ActivityKit push notifications](https://developer.apple.com/documentation/ActivityKit/starting-and-updating-live-activities-with-activitykit-push-notifications)
- [ActivityKit push type](https://developer.apple.com/documentation/activitykit/pushtype)
- [Live Activities](https://developer.apple.com/design/human-interface-guidelines/live-activities)
- [App Shortcuts](https://developer.apple.com/design/human-interface-guidelines/app-shortcuts)
- [Controls](https://developer.apple.com/design/human-interface-guidelines/controls)
