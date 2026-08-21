# AlarmKit and time-based actions

## Scope

AlarmKit is the iOS 26 SDK route for prominent alarms and countdowns that need to remain meaningful when the app is not on screen. Apple describes it as a framework for custom alarms and timers with one-time and repeating schedules, countdown durations, snoozing, authorization, and templated or widget presentations.

The important design decision is whether the product needs an alarm or only a reminder:

| Need | First route | Why |
| --- | --- | --- |
| A prominent, user-created alarm or timer that may alert through Focus or silent mode when necessary | AlarmKit | The system owns the alarm lifecycle and presentation contract. |
| A normal reminder that can wait in Notification Center | UserNotifications | Local notifications are appropriate for ordinary attention requests and custom notification actions. |
| A live, glanceable status for a task already in progress | ActivityKit and WidgetKit | Live Activities show changing state; they are not a general alarm scheduler. |
| Work that should continue after a user starts it | BackgroundTasks or the appropriate foreground-continuation route | Background execution is a resource-managed work problem, not an alarm presentation problem. |
| A notification generated from a server | APNs or ActivityKit push notifications | Delivery, authorization, server state, and production evidence become part of the route. |

Do not use AlarmKit as a shortcut for a notification, and do not use a local notification when the product promise is a user-controlled alarm with stop, countdown, pause, resume, or snooze semantics. The user-facing urgency must match the system capability.

## Framework and target map

| Product responsibility | API or target | Owner and boundary |
| --- | --- | --- |
| Ask whether the app may schedule alarms | AlarmManager.requestAuthorization() and AlarmManager.authorizationState | The app owns the explanation and the user decision; the system owns the authorization prompt. |
| Create a one-shot or repeating schedule | Alarm.Schedule.fixed(_:) or .relative(_:) | The domain layer owns the validated draft; AlarmKit owns the registered schedule after confirmation. |
| Create an immediate countdown | Alarm.CountdownDuration or the AlarmConfiguration.timer route | The app supplies the duration; the system owns countdown timing and presentation state. |
| Describe alert, countdown, and paused states | AlarmPresentation.Alert, .Countdown, .Paused, and AlarmAttributes | The app supplies bounded content and tint; the system renders the prominent interface. |
| Add stop or secondary behavior | stopIntent and secondaryIntent using App Intents / Live Activity intents | The system invokes the configured action; the app must make the action idempotent and safe. |
| Show non-alerting countdown UI | Widget extension with ActivityConfiguration for AlarmAttributes<Metadata> | The widget extension is a separate target and process boundary. |
| Reconcile registered alarms | AlarmManager.alarms, alarmUpdates, and an app-owned record | AlarmKit is not the only source of domain truth; one-shot alarms disappear after they fire and stop. |
| Pause, resume, stop, snooze, or cancel | pause(id:), resume(id:), countdown(id:), stop(id:), and cancel(id:) | Each operation can throw and must update the app’s state from the resulting system observation. |

The target graph is therefore usually:

    app target -> AlarmKit scheduling and review
             -> App Intents for safe stop/secondary actions
             -> widget extension for countdown and glanceable surfaces
             -> app-owned persistence for intent, provenance, and reconciliation

Adding a widget extension is not a visual-only decision. Apple’s AlarmKit sample says an app that supports a countdown presentation is expected to implement the associated Live Activity in a widget extension; without it, alarms may be dismissed or fail to alert. Validate the exact target membership and deployment target in Xcode.

## Authorization and privacy configuration

Add NSAlarmKitUsageDescription to the app target’s information property list. Apple documents that the key must contain a non-empty explanation of why the app schedules alarms; without it, the app cannot schedule AlarmKit alarms. The string should explain the user-visible outcome, for example:

    We’ll schedule the alarms you create in this app.

Request authorization at a deliberate point, usually when a person has completed an alarm draft or chooses an explicit “Enable alarms” action. AlarmKit may also request authorization automatically when the app schedules its first alarm, but a preflight step gives the app a chance to explain that the alarm can appear in system-owned surfaces and may be prominent.

The documented authorization states are:

- notDetermined: the app has not requested access;
- authorized: the person allowed alarms and timers;
- denied: the person declined previously.

Treat authorization as revocable runtime state. On every schedule attempt:

1. read authorizationState;
2. if it is notDetermined, explain and request;
3. if it is denied, show a recoverable settings path and keep the draft local;
4. if it is authorized, validate again and schedule;
5. persist the user-approved domain record only after the system operation succeeds.

The usage description is not a substitute for a privacy policy or an explanation of the product’s data retention. Alarm metadata should be minimal. Do not put secrets, access tokens, private notes, raw model context, or a large database snapshot into AlarmMetadata. The system may render alarm content while the device is locked or in another system surface.

## Schedule models

AlarmKit exposes two different schedule meanings.

### Fixed one-shot date

Alarm.Schedule.fixed(_:) describes a one-time alarm at a specific Date. Use it when the user chose an actual instant. Store the original calendar/time-zone context in the app-owned record if the product needs to explain what the person selected after a time-zone change.

### Relative local-time schedule

Alarm.Schedule.relative(_:) uses Alarm.Schedule.Relative.Time(hour:minute:) and a recurrence. The documented recurrence cases are:

- .never for a single occurrence at the local time;
- .weekly([Locale.Weekday]) for a weekly cadence.

The relative time is relative to the device’s current time zone. That is useful for “every weekday at 7:30,” but it is not the same as a fixed UTC instant. The app should display the time-zone meaning in the review surface and test travel, daylight-saving transitions, locale changes, and time-zone changes.

### Countdown duration

Alarm.CountdownDuration carries the pre-alert and post-alert duration semantics. Apple’s sample uses a pre-alert countdown to show the countdown presentation and a post-alert duration to support a repeat/snooze action after the alarm fires. A timer configuration can start immediately with a duration, while a full alarm configuration can combine a countdown duration with a schedule.

Keep these values distinct in the domain model:

| Value | Meaning | Product question |
| --- | --- | --- |
| Scheduled fire date/time | When the alert should occur | Is this a fixed instant or a local recurring time? |
| Pre-alert duration | How long a countdown runs before the alert state | Does the person expect the app to show active countdown progress? |
| Post-alert duration | How long a repeat/countdown action can postpone or re-trigger | What exactly does “repeat” mean in this product? |
| Recurrence | Whether and when the alarm registers its next occurrence | Can the person see, edit, and disable the repeat rule? |

Do not represent all four values as one Date or one free-form model string. They have different validation, copy, and proof requirements.

## Presentation and state

AlarmKit’s templated presentation has three conceptual states:

1. AlarmPresentation.Alert: the alerting state, with a title, a system-managed stop control, and an optional secondary button;
2. AlarmPresentation.Countdown: the active countdown state, optionally with a pause button;
3. AlarmPresentation.Paused: the paused state, with a required resume button.

The current API provides AlarmButton(text:textColor:systemImageName:). The system supplies the primary stop behavior for the alert presentation. The optional secondary button can have a .countdown behavior or a .custom behavior, depending on the product route and the configured intents.

The content is wrapped in AlarmAttributes<Metadata> with a tintColor and optional metadata. AlarmMetadata is required to be Decodable, Encodable, Hashable, and Sendable. Keep metadata small, stable, and safe to decode in the widget extension. Treat it as presentation-supporting data, not as an authoritative record.

Presentation construction is a state contract, not a decoration layer:

| State | Must communicate | Must not imply |
| --- | --- | --- |
| Countdown | label, current mode, pause affordance if enabled, and enough context to identify the timer | that the underlying work has completed |
| Paused | paused status and a clear resume action | that the timer is still progressing |
| Alert | what happened and the most useful immediate action | that the user’s domain action succeeded if the action is still processing |
| App review | source schedule, current system state, errors, and next safe action | that an app-owned row is proof the system alarm is still registered |

Use a stable alarm identifier, normally a UUID, across the domain record, AlarmKit schedule, intent payload, and reconciliation log. Make stop, cancel, and secondary actions idempotent: a repeated system invocation must not create duplicate records or repeat an irreversible side effect.

## Lifecycle and reconciliation

The app should model two related state machines.

### App-owned intent state

    draft -> awaiting authorization -> approved -> registered
       -> user-edited -> replacement pending -> registered
       -> cancelled locally -> cancellation confirmed
       -> fired/finished -> archived

### AlarmKit runtime state

    scheduled -> countdown -> paused -> countdown -> alerting
                                  \-> stopped
    scheduled -> cancelled
    alerting -> countdown
    alerting -> stopped

The exact Alarm.State cases and associated values are SDK-sensitive; inspect the current Xcode SDK before writing exhaustive switches. The durable architectural rule is to keep the system observation separate from the app’s intent record.

Use AlarmManager.alarmUpdates as an AsyncSequence that emits the current set of alarms when the set changes. On app launch and scene activation, also read AlarmManager.alarms and reconcile. Apple documents that an alarm missing from the daemon’s store may have fired and stopped; a one-shot alarm is deleted after it fires and stops. If the product needs to distinguish “fired” from “cancelled,” persist the app’s expected schedule and compare it with the returned set.

Reconciliation should be idempotent:

1. load the last app-owned records;
2. read the current AlarmKit alarms;
3. map by stable identifier;
4. mark missing registered one-shot alarms as needing an outcome check;
5. use stored schedule and timestamps to classify likely fired, cancelled, or externally changed;
6. refresh the review UI;
7. record the reconciliation timestamp and source.

Do not claim that a local row is a live alarm just because it was once scheduled successfully.

## Concurrency and process boundaries

AlarmManager.schedule(id:configuration:) is asynchronous and throws. The state streams are asynchronous sequences. A practical design is a @MainActor view model for review state plus an actor or isolated service for persistence and reconciliation. Keep system calls cancellable where the surrounding task can be cancelled, and do not update SwiftUI state from a detached task without returning through the intended isolation boundary.

The widget extension receives the same AlarmAttributes type used for the alarm. It does not become the owner of scheduling or domain truth. Keep shared metadata types in a module that both the app and widget target can import; keep secrets and app-only persistence out of that module.

If the app is terminated, the system can still own the registered alarm, but the app’s in-memory model is gone. On next launch, rebuild state from the app store plus AlarmManager.alarms and alarmUpdates. Do not use a foreground timer, Task.sleep, or a TimelineView countdown as the source of truth for an alarm that must survive process suspension.

## On-device AI route

AlarmKit is a useful side-effect boundary for an on-device AI feature, but model output must remain a proposal:

    natural-language request
        -> Foundation Models typed proposal
        -> deterministic schedule/date/time-zone validation
        -> visible review
        -> explicit user confirmation
        -> AlarmKit authorization and schedule
        -> app-owned record and reconciliation

Allow the model to suggest a label, a time, a recurrence, or a duration. Do not let it call AlarmManager.schedule directly. Validate:

- date is in the future when required;
- hour and minute are valid;
- recurrence days are supported and non-empty when weekly;
- duration is positive and within the product’s safe range;
- the requested time zone is represented correctly;
- no duplicate or conflicting alarm is silently created;
- the proposed title is safe for locked-screen display;
- the user has seen the actual side effect and the selected sound/urgency.

If the model is unavailable, return a normal deterministic editor. If the model proposes an unsupported schedule, preserve the person’s request as editable text and explain what can be created. Never silently convert an uncertain natural-language request into a repeating alarm.

## Accessibility and native design

Use native text, buttons, localization, Dynamic Type, and semantic actions in the app-owned scheduling and review surfaces. A Liquid Glass treatment can organize the app’s editor, review card, and action cluster when it improves hierarchy, but it cannot make the system-owned AlarmKit alert look like a custom app screen.

Keep the alert title short enough for system surfaces and localize every user-facing value. VoiceOver should expose the schedule meaning, recurrence, countdown/paused status, and action outcome. Do not encode urgency only through tint color. Provide a reduced-motion and reduced-transparency path in the app-owned surfaces; verify the system presentation separately.

## Availability and proof boundary

AlarmKit is a version-sensitive iOS 26 SDK route. Apple’s current sample and WWDC material are marked as preliminary/beta-era documentation, so confirm the deployment target, SDK signature, availability attributes, and final behavior in the Xcode version used for the app.

Previews and simulator runs can prove:

- schedule-editor layout;
- typed proposal rendering;
- deterministic validation;
- mocked authorization and alarm states;
- widget layout with fixture AlarmAttributes;
- accessibility labels and Dynamic Type behavior in app-owned views.

They do not prove:

- authorization prompt behavior;
- delivery while locked or in Focus/silent mode;
- prominent alert sound and timing;
- Countdown/Paused state transitions under suspension;
- Lock Screen, Dynamic Island, StandBy, or paired Apple Watch presentation;
- system action invocation;
- reboot, time-zone, daylight-saving, or OS update behavior;
- final hardware and release behavior.

Use the [AlarmKit proof matrix](../60-verification/17-alarmkit-and-time-based-action-proof-matrix.md) before describing the route as device-ready.

## Sources

- [AlarmKit](https://developer.apple.com/documentation/alarmkit)
- [AlarmManager](https://developer.apple.com/documentation/alarmkit/alarmmanager)
- [Scheduling an alarm with AlarmKit](https://developer.apple.com/documentation/AlarmKit/scheduling-an-alarm-with-alarmkit)
- [Alarm](https://developer.apple.com/documentation/alarmkit/alarm)
- [AlarmManager schedule](https://developer.apple.com/documentation/alarmkit/alarmmanager/schedule%28id%3Aconfiguration%3A%29)
- [Alarm schedule relative time](https://developer.apple.com/documentation/alarmkit/alarm/schedule-swift.enum/relative)
- [Alarm schedule recurrence](https://developer.apple.com/documentation/alarmkit/alarm/schedule-swift.enum/relative/recurrence)
- [AlarmPresentation.Alert](https://developer.apple.com/documentation/alarmkit/alarmpresentation/alert-swift.struct)
- [AlarmPresentation.Countdown](https://developer.apple.com/documentation/alarmkit/alarmpresentation/countdown-swift.struct)
- [AlarmPresentation.Paused](https://developer.apple.com/documentation/alarmkit/alarmpresentation/paused-swift.struct)
- [AlarmPresentation initializer](https://developer.apple.com/documentation/alarmkit/alarmpresentation/init%28alert%3Acountdown%3Apaused%3A%29)
- [AlarmButton](https://developer.apple.com/documentation/alarmkit/alarmbutton)
- [AlarmAttributes](https://developer.apple.com/documentation/alarmkit/alarmattributes)
- [AlarmMetadata](https://developer.apple.com/documentation/alarmkit/alarmmetadata)
- [Alarm authorization state](https://developer.apple.com/documentation/alarmkit/alarmmanager/authorizationstate-swift.enum)
- [NSAlarmKitUsageDescription](https://developer.apple.com/documentation/BundleResources/Information-Property-List/NSAlarmKitUsageDescription)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [Displaying live data with Live Activities](https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities)
- [Scheduling an alarm with AlarmKit](https://developer.apple.com/documentation/alarmkit/scheduling-an-alarm-with-alarmkit)
- [Scheduling a notification locally from your app](https://developer.apple.com/documentation/UserNotifications/scheduling-a-notification-locally-from-your-app)
- [Managing notifications](https://developer.apple.com/design/human-interface-guidelines/managing-notifications)
- [Alerts](https://developer.apple.com/design/human-interface-guidelines/alerts)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
