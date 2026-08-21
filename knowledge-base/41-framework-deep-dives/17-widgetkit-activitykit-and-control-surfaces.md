# WidgetKit, ActivityKit, and control surfaces

## Scope

This page is the framework contract for small, glanceable, system-managed surfaces:

- WidgetKit widgets on the Home Screen, Lock Screen, StandBy, Smart Stack, CarPlay, and other supported contexts;
- WidgetKit interactive widgets driven by App Intents;
- ControlWidget buttons and toggles in Control Center, the Lock Screen, and the Action button;
- ActivityKit Live Activities rendered through a widget extension;
- local and remote ActivityKit updates;
- Liquid Glass and accented widget rendering;
- on-device AI proposals that project into a widget, control, or Live Activity.

These surfaces are not miniature app screens. The operating system owns placement,
space, scheduling, treatment, process lifetime, and many update decisions. The
app owns the domain state, authorization, projection, intent side effect, and
fallback story.

A useful boundary is:

    app-owned source of truth
      -> versioned system-surface projection
      -> WidgetKit / ControlWidget / ActivityKit
      -> user action or glance
      -> App Intent or app deep link
      -> current domain validation
      -> commit and projection refresh

A surface may contain a stale, redacted, denied, unavailable, or ended projection.
Do not treat a rendered view as proof that the underlying record is current.

## Version and availability boundary

Use the selected Xcode SDK and deployment target as the authority for signatures,
availability annotations, target membership, and beta labels. Apple’s current
documentation includes both established WidgetKit and ActivityKit APIs and newer
control, rendering, push, and execution capabilities whose exact availability
must be checked in the project.

Record these separately:

| Question | Evidence required |
| --- | --- |
| Does the selected SDK expose the symbol? | Named target compile and availability check |
| Can the selected device host the surface? | Device family, OS build, settings, and surface support |
| Can the extension read the required state? | App Group/resource/authorization test |
| Can a system action execute? | Signed physical invocation from the intended surface |
| Can a server update it? | APNs capability, token registration, environment, and delivery evidence |
| Can the app distribute it? | Archive target membership, entitlements, privacy, and release artifact |

A preview, documentation example, or simulator screenshot is useful layout
evidence. It is not physical system-surface or distribution proof.

## Framework roles

### WidgetKit

WidgetKit renders a SwiftUI projection supplied by a Widget configuration and a
timeline provider. A widget extension is not continuously running just because
the widget is visible. WidgetKit requests a placeholder, snapshot, or timeline
when it needs one, then renders entries according to system policy.

The principal routes are:

| Need | Route |
| --- | --- |
| Fixed kind of content with no user-selected configuration | StaticConfiguration plus TimelineProvider |
| User-configurable widget | AppIntentConfiguration plus AppIntentTimelineProvider |
| Short predictable future states | Timeline entries plus atEnd or after refresh policy |
| Event-driven local refresh | WidgetCenter reload request, used selectively |
| Remote state refresh | WidgetKit push token and APNs widgets push, subject to budget |
| Interactive mutation | Button or Toggle with an App Intent, followed by projection refresh |
| Link to app detail | widgetURL or Link, with current route reconstruction |
| Adaptive background | containerBackground(for: .widget) and environment-aware layout |
| Tinted or Liquid Glass Home Screen | widgetRenderingMode, widgetAccentable, and image rendering policy |

A widget is a read-optimized projection. It should not open a database transaction
or run an unbounded model pipeline merely because a timeline was requested.

### ActivityKit

ActivityKit manages the lifecycle of a Live Activity. WidgetKit and SwiftUI render
the Live Activity UI, but ActivityKit starts, updates, observes, and ends the
activity. A Live Activity does not use a WidgetKit timeline as its source of
updates.

A Live Activity normally has:

- ActivityAttributes for static data that remains associated with the activity;
- a nested ContentState for dynamic, Encodable, Decodable, and Hashable state;
- ActivityContent containing the current state, optional staleDate, and relevanceScore;
- an ActivityConfiguration in the widget extension;
- Activity.request, update, and end calls in the app or ActivityKit push updates;
- state handling for active, stale, dismissed, and ended conditions;
- a deep link or interactive action that returns the person to the relevant app route.

Apple documents Live Activities for glanceable data and quick actions in supported
system spaces such as the Lock Screen, Dynamic Island, CarPlay, and paired devices.
Availability and presentation vary by device and OS; verify the actual deployment
matrix rather than assuming every surface exists everywhere.

### ControlWidget

A control is a compact action or value projection. ControlWidget describes the
control, a configuration describes whether it is static or configurable, a value
provider supplies preview/current values, and a template such as
ControlWidgetButton or ControlWidgetToggle gives the system a size-adaptive
presentation.

Use a control for a small, repeatable action:

- start or stop a bounded timer;
- set a device or app mode;
- launch a specific capture or app route;
- toggle an on-device state;
- perform a safe command whose current value can be read quickly.

Do not use a control as a dashboard, a multi-step editor, or a place to expose
an unreviewed generated decision. A button has no durable on/off state; use a
toggle when the person needs to understand current state.

## WidgetKit lifecycle

### Widget configuration and target shape

Create a Widget Extension target and keep its code independent from the main app's
window hierarchy. A WidgetBundle can expose several widgets, each with a stable
kind string. The extension may share domain projection types with the app, but
it should not depend on a view model, navigation coordinator, or singleton that
only exists in the main process.

A practical target graph is:

    MainApp
      ├── Domain
      ├── ProjectionStore
      ├── AppIntents
      └── WidgetExtension
            ├── Widget definitions
            ├── Timeline providers
            ├── ControlWidget definitions
            └── ActivityConfiguration

If the projection is shared with the main app, choose a deliberately small,
versioned record. App Groups can provide shared file or database access when the
entitlements and migration policy are correct. A shared container is not an
authorization bypass: recheck account, privacy, and record access when a system
action commits a change.

### Placeholder, snapshot, and timeline

A provider has different jobs:

- placeholder: communicate the shape of the widget while the gallery or system
  is preparing content; use redacted or fixture-safe values;
- snapshot: show a representative current state for the gallery or transient
  request; do not perform expensive work;
- timeline: return entries with dates and a refresh policy.

For a configurable widget, AppIntentTimelineProvider receives the user's
WidgetConfigurationIntent. Resolve the configuration to a stable identifier and
then load only the projection needed by that widget instance.

Treat the context as a rendering constraint. It can communicate the family/size
and whether the request is a gallery preview. Do not assume the widget can query
the main app's in-memory state.

### Refresh policy and budgets

Timeline policies express what is known, not a guarantee that the view changes at
an exact instant:

- atEnd asks for a new timeline after the final entry;
- after(date) asks for a refresh around a future point;
- never asks the app to request a reload when state changes.

WidgetCenter.reloadTimelines(ofKind:) and reloadAllTimelines() are requests. They
do not make an immediate-render promise and should be used only when the current
projection is affected. WidgetKit budgets reloads based on visibility, usage,
previous reloads, and system conditions. A frequently viewed widget may receive
many more refresh opportunities than a neglected one, but the app must remain
correct when refreshes are delayed.

For predictable state, prepare future entries. For unpredictable state, use
never plus a selective reload, a dynamic date, or a WidgetKit push update when
the server owns the source of truth. Do not poll aggressively from a widget
extension.

### Relevance and dynamic dates

Relevance is a hint to help the system decide which widget is useful in a Smart
Stack or suggestion context. It is not a ranking guarantee and is not a license
to donate sensitive content.

A dynamic date can continue to display a timer/countdown while the extension is
not running. The displayed time is not the same as a durable server update.
When the underlying event changes, invalidate or reload the projection.

### Interactivity

Interactive widgets can use SwiftUI Button or Toggle with an App Intent. The
intent must be:

- fast enough for a system surface;
- idempotent for repeated invocation;
- safe when the app is terminated or the device is locked;
- able to validate current account/permission/state;
- able to return a localized result or actionable error;
- followed by a projection refresh or a value update.

Use invalidatableContent on important views whose values may change after an
interaction and the system is waiting for the updated projection. Do not animate
a large state transition as if the widget were a continuously running app.

### Background and privacy state

The widget process may be terminated, run without the main app, or receive only a
subset of the data needed by the app. Design explicit projection states:

- signed out;
- locked/redacted;
- authorized but empty;
- loading;
- ready;
- stale;
- unavailable/offline;
- permission revoked;
- migration required;
- error with a repair route.

When a widget appears on a locked device or in a privacy-sensitive context, hide
titles, images, places, health data, personal messages, and AI-generated content
unless the surface's privacy behavior has been deliberately verified.

## Liquid Glass and widget rendering

Apple documents that widgets participate in Liquid Glass environments and may be
rendered in an accented mode when a person chooses a tinted or clear Home Screen.
The system can remove or transform the widget background. The app should cooperate
with that transformation.

The reliable pattern is:

1. put the widget's background inside containerBackground(for: .widget);
2. allow the system to remove the background where the context requires it;
3. inspect widgetRenderingMode;
4. group semantically important content with widgetAccentable;
5. choose WidgetAccentedRenderingMode for images;
6. reserve fullColor for content whose meaning depends on color, such as media
   artwork or a cover image;
7. test vibrant, accented, full-color, background-removed, StandBy, and accessory
   contexts.

Do not place a large custom glass panel inside a widget to imitate the app's
main-screen glass. The system owns the outer treatment. A widget should have a
clear information hierarchy that survives desaturation, tinting, and background
removal.

The same rule applies to controls: use the system control template and semantic
labeling. A custom glass background is not a substitute for a correct
ControlWidgetButton or ControlWidgetToggle contract.

## ControlWidget lifecycle

### Static versus configurable

StaticControlConfiguration is appropriate when one control always performs one
well-defined action. AppIntentControlConfiguration is appropriate when a person
must choose a bounded configuration, such as which timer or device the control
acts on.

Configuration should reduce ambiguity, not add a setup wizard. If two controls
with different configurations would be clearer, provide distinct controls.

### Value providers

ControlValueProvider supplies:

- previewValue for the add/configuration sheet;
- currentValue() for the actual system rendering.

Keep both cheap and deterministic. A preview should be privacy-safe and not
pretend to be the current value. The current provider may read a shared local
projection or a bounded remote state, but it must handle timeout, sign-out,
locked-device, and offline conditions.

For a toggle, the value is the current on/off state. For a button, the value
provider may be unnecessary unless the template displays a status or label.

### Actions and status

A ControlWidgetButton is for a fire-and-forget action or a route that launches
the app. A ControlWidgetToggle represents an on/off value and commonly uses a
SetValueIntent. The action must re-read current state before committing; the
value rendered before the tap may be stale.

Use controlWidgetStatus for short status text when the action changes a temporary
condition. Use controlWidgetActionHint for a concise action hint when the system
needs extra context. Status text should not become a log, a generated essay, or
a sensitive-data channel.

The control's kind is a stable identifier. Changing it can make the system treat
the control as a different item. Treat localization, display name, description,
symbol, and action semantics as user-facing API.

### Locked-device behavior

A control may be invoked from a locked or otherwise restricted system state.
Choose explicitly:

- permit a low-risk idempotent action without revealing private data;
- require authentication before the side effect;
- return a safe no-op/actionable error;
- launch the app only when the route is supported.

Never display a private record name or model output just because a control value
provider was able to read it. Validate authorization in the action, not only in
the rendering provider.

## ActivityKit lifecycle

### Attributes and content state

Put stable identity and static presentation context in ActivityAttributes. Put
fast-changing progress or status in the nested ContentState. Keep the content
small and privacy-reviewed because ActivityKit data is replicated across system
surfaces and push payloads.

An ActivityContent contains state, optional staleDate, and relevanceScore:

- staleDate gives the system a point at which content should be considered out
  of date;
- relevanceScore helps order multiple activities and should reflect product
  relevance, not an attempt to force attention;
- state is the current dynamic projection.

The 4 KB combined static/dynamic Live Activity data limit documented by Apple is
a hard design constraint. Send IDs, short labels, progress, and bounded status,
not an entire domain record or model transcript.

### Start, update, and end

The app can request a Live Activity while the app is in a supported foreground
state. Keep a reference to the returned Activity or reconstruct current
activities through Activity.activities. Update with Activity.update and finish
with Activity.end using a deliberate dismissal policy.

The app must recover if it is terminated or relaunched while an activity is
visible:

- query active activities;
- reconcile each activity ID with current domain state;
- update if current;
- mark stale or end if no longer relevant;
- avoid starting a duplicate activity for the same operation.

A Live Activity is not a background worker. Its view cannot fetch arbitrary network
data or location updates. Update it through ActivityKit in the app or through
ActivityKit push notifications from a server.

### Push and authorization

If remote updates are required:

- enable the appropriate push capability in the target;
- obtain and rotate ActivityKit push tokens;
- send tokens to a server over an authenticated channel;
- use the correct APNs environment and push type;
- verify server payload size, state version, and event ordering;
- handle token changes, revoked authorization, stale activities, and delivery
  delay.

ActivityAuthorizationInfo reports whether Live Activities are enabled and whether
frequent push updates are enabled. Treat these values as current user/system
state, not as a permanent product entitlement.

### Surface state machine

Use one state model across the app and the Live Activity:

    preparing -> active -> stale -> ended
                    |          |
                    v          v
                 error      dismissed

A stale state should tell the person what is known and how current it is. An ended
state should not look like a live countdown. A server error should not be rendered
as success merely because the last push was valid.

## On-device AI projection boundary

Foundation Models, Core ML, Vision, Speech, and other on-device intelligence
frameworks can propose a status, summarize a record, classify a local event, or
suggest an action. The system surface should receive a deterministic projection,
not an unreviewed generation.

Use this route:

1. collect only the local input needed for the proposal;
2. check model/framework/device availability;
3. generate a typed proposal with source IDs and model/version metadata;
4. validate against current domain state and policy;
5. ask for review when the proposal changes data, sends a message, starts a
   sensitive activity, or exposes private content;
6. commit through the app-owned service;
7. write a compact, redacted projection for the widget, control, or activity;
8. show stale/error/repair state when the proposal or source is unavailable.

Do not run a generative model in a WidgetKit or ControlWidget rendering path as a
shortcut around app architecture. The surface may be refreshed opportunistically,
and its process lifetime is not a safe model-session boundary.

## Physical and release proof

For a complete route, preserve separate evidence for:

- named-target compile and availability checks;
- widget preview/fixture rendering;
- timeline and reload-policy tests outside the debugger;
- widget family, background-removal, accented, vibrant, and Dynamic Type tests;
- interactive widget invocation with app terminated;
- Control Center/Lock Screen/Action button control invocation;
- locked-device, authentication, sign-out, and permission behavior;
- Live Activity start, update, stale, end, dismissal, relaunch, and duplicate
  prevention;
- ActivityKit push token registration and real APNs delivery;
- process termination, memory, battery, and thermal behavior;
- VoiceOver, Voice Control, Switch Control, contrast, reduced transparency, Reduce
  Motion, and localization;
- archive target membership, entitlements, capabilities, privacy, and TestFlight/
  release behavior.

A simulator can help inspect layout and some system flows. It does not prove the
physical device, push environment, Apple Intelligence availability, device family,
or production configuration.

## Sources

- [WidgetKit](https://developer.apple.com/documentation/widgetkit/)
- [Creating a widget extension](https://developer.apple.com/documentation/widgetkit/creating-a-widget-extension)
- [TimelineProvider](https://developer.apple.com/documentation/widgetkit/timelineprovider)
- [AppIntentTimelineProvider](https://developer.apple.com/documentation/widgetkit/appintenttimelineprovider)
- [Making a configurable widget](https://developer.apple.com/documentation/widgetkit/making-a-configurable-widget)
- [Keeping a widget up to date](https://developer.apple.com/documentation/widgetkit/keeping-a-widget-up-to-date/)
- [WidgetCenter](https://developer.apple.com/documentation/widgetkit/widgetcenter)
- [Adding interactivity to widgets and Live Activities](https://developer.apple.com/documentation/widgetkit/adding-interactivity-to-widgets-and-live-activities)
- [Displaying the right widget background](https://developer.apple.com/documentation/widgetkit/displaying-the-right-widget-background)
- [Optimizing your widget for accented rendering mode and Liquid Glass](https://developer.apple.com/documentation/widgetkit/optimizing-your-widget-for-accented-rendering-mode-and-liquid-glass)
- [Creating controls to perform actions across the system](https://developer.apple.com/documentation/widgetkit/creating-controls-to-perform-actions-across-the-system)
- [Adding refinements and configuration to controls](https://developer.apple.com/documentation/widgetkit/adding-refinements-and-configuration-to-controls)
- [ControlWidget](https://developer.apple.com/documentation/swiftui/controlwidget)
- [ControlWidgetButton](https://developer.apple.com/documentation/widgetkit/controlwidgetbutton)
- [ControlWidgetToggle](https://developer.apple.com/documentation/widgetkit/controlwidgettoggle)
- [ControlValueProvider](https://developer.apple.com/documentation/widgetkit/controlvalueprovider)
- [AppIntentControlConfiguration](https://developer.apple.com/documentation/widgetkit/appintentcontrolconfiguration)
- [ActivityKit](https://developer.apple.com/documentation/activitykit/)
- [Activity](https://developer.apple.com/documentation/activitykit/activity)
- [ActivityAuthorizationInfo](https://developer.apple.com/documentation/activitykit/activityauthorizationinfo)
- [ActivityContent](https://developer.apple.com/documentation/activitykit/activitycontent)
- [ActivityConfiguration](https://developer.apple.com/documentation/widgetkit/activityconfiguration)
- [Displaying live data with Live Activities](https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities)
- [Starting and updating Live Activities with ActivityKit push notifications](https://developer.apple.com/documentation/activitykit/starting-and-updating-live-activities-with-activitykit-push-notifications)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility](https://developer.apple.com/accessibility/)
