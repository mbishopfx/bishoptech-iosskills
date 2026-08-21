# AlarmKit scheduled-action route

## Outcome

Use this route when an app needs to turn a person-approved plan into a prominent alarm or countdown, keep the app’s record honest when the process is not running, and optionally attach a safe action to the system-owned alert.

Good examples:

- a cooking timer with a repeat action;
- a medication reminder that only claims to alert, not to provide medical advice;
- a focus-session timer with pause and resume;
- a local-first routine alarm;
- a device task that needs a visible countdown and a user-confirmed follow-up.

The route is not a license to silently schedule alarms from a model, infer health outcomes, or treat a local database row as proof that the system daemon still owns an alarm.

## Decision gate

Choose AlarmKit only when the requested behavior needs an alarm or countdown. Use this decision table before adding a target:

| User outcome | Route |
| --- | --- |
| “Remind me later” with no prominent stop/repeat/countdown state | UserNotifications |
| “Wake me at this time every weekday” | AlarmKit relative schedule |
| “Count down 25 minutes, pause, then alert” | AlarmKit countdown plus widget extension |
| “Show the live status of a delivery for two hours” | ActivityKit / WidgetKit Live Activity |
| “Do expensive work after the user leaves” | BackgroundTasks or a foreground-continuation route |
| “Let the user trigger scheduling from Shortcuts or a control” | App Intents plus the AlarmKit side-effect boundary |

Keep the first implementation narrow. A timer, a one-shot alarm, and a weekly alarm are three separate proof slices even if they share a screen.

## Route architecture

    user input
       -> app-owned draft
       -> optional on-device AI proposal
       -> deterministic normalization and validation
       -> visible confirmation
       -> AlarmKit authorization
       -> AlarmKit configuration and schedule
       -> app-owned record marked registered
       -> AlarmKit / widget system presentation
       -> intent action or app return
       -> reconciliation and durable outcome

### Ownership table

| State or operation | Owner | Durable? |
| --- | --- | --- |
| Natural-language request | App-owned draft | Yes, if the product needs edit/retry history |
| AI interpretation | App-owned proposal | Yes only with prompt/model/version provenance |
| Normalized schedule | App-owned typed intent | Yes |
| Authorization state | AlarmKit plus app observation | Runtime; re-read |
| Registered alarm | AlarmKit daemon | System-owned; reconcile |
| Label/tint/metadata | App-supplied presentation attributes | Shared with widget; keep small |
| Stop/repeat action | AlarmKit system interaction plus configured intent | Must be idempotent |
| Fired/cancelled classification | App-owned reconciliation | Yes |
| External side effect | Domain service after explicit action | Yes, with an idempotency key |

## Target graph

The smallest target graph depends on the feature:

### Alert-only alarm

- app target imports AlarmKit;
- app target contains the editor, authorization gate, and schedule service;
- app target persists the user-approved intent and reconciliation record;
- App Intents are optional for additional stop/secondary behavior.

### Countdown alarm

- all alert-only targets;
- widget extension target;
- shared target/module containing AlarmMetadata and any safe shared presentation types;
- ActivityConfiguration for AlarmAttributes<Metadata>;
- target configuration and Live Activity settings validated in Xcode.

Do not put app-only secrets or a private persistence container in a shared metadata module. The widget extension should render from the attributes and system state supplied to it.

## Typed domain model

Use a typed, serializable app-owned model rather than passing a natural-language string to the scheduler:

~~~swift
struct AlarmDraft: Codable, Hashable, Sendable {
    var id: UUID
    var label: String
    var kind: Kind
    var timeZoneIdentifier: String
    var oneShotDate: Date?
    var hour: Int?
    var minute: Int?
    var weekdays: [Locale.Weekday]
    var preAlertSeconds: TimeInterval?
    var postAlertSeconds: TimeInterval?
    var source: Source

    enum Kind: String, Codable, Sendable {
        case fixedDate
        case weeklyLocalTime
        case timer
    }

    enum Source: String, Codable, Sendable {
        case directInput
        case onDeviceProposal
    }
}
~~~

This is a route sketch, not a claim that the exact AlarmKit SDK accepts this model. The model exists to keep user intent, validation, persistence, and system configuration separate.

Validate before authorization:

- label is non-empty and safe for a locked-screen presentation;
- fixed-date alarms have a future date;
- weekly alarms have a valid hour/minute and at least one weekday;
- timer durations are positive and within the product’s declared range;
- pre-alert and post-alert values are not confused;
- the time-zone identifier is known;
- no active record already uses the same logical idempotency key;
- any AI-derived field has provenance and was shown to the user.

## Schedule pipeline

### 1. Create or import the draft

Accept direct controls first. If the app offers an on-device language interface, preserve the original request and create a typed proposal:

    “remind me every weekday at 7:30 to stretch”
        -> label: Stretch
        -> local time: 07:30
        -> days: Monday...Friday
        -> kind: weeklyLocalTime
        -> source: onDeviceProposal

If a phrase is ambiguous, ask for the missing field rather than selecting a dangerous default.

### 2. Show the normalized review

The review surface must display the exact schedule that will be passed to AlarmKit. Make the primary action explicit: Schedule alarm, Start timer, or Save without alert, depending on the route.

### 3. Request authorization

Ensure NSAlarmKitUsageDescription exists in the app target. Read AlarmManager.authorizationState, request if needed, and handle denied as a first-class state. Keep the draft if authorization fails.

### 4. Build the presentation

Create AlarmPresentation.Alert and add Countdown and Paused only when the route supports them. Use AlarmButton for a small, localized action set. Use AlarmAttributes<Metadata> for the presentation, tint, and optional widget metadata.

### 5. Build the schedule/configuration

Map the typed draft:

- fixedDate -> Alarm.Schedule.fixed(date);
- weeklyLocalTime -> Alarm.Schedule.relative with Relative.Time and .never or .weekly;
- timer -> AlarmConfiguration.timer(duration:attributes:...);
- combined schedule/countdown -> AlarmConfiguration with countdownDuration and schedule.

Keep the schedule call behind one service method so every entry point—main app, App Intent, or future control—passes through the same validation and authorization boundary.

### 6. Schedule and persist

Call AlarmManager.schedule(id:configuration:). Only after it returns successfully should the app mark its record as registered. Save:

- alarm id;
- normalized schedule;
- presentation version;
- metadata schema version;
- authorization result;
- schedule timestamp;
- source and model/prompt version if AI proposed it;
- a reconciliation status of registered.

### 7. Observe and reconcile

Start an alarmUpdates observer for the app’s lifetime or feature scope. On launch/scene activation, also read alarms. Map system alarms by id and refresh local state. If a one-shot alarm is no longer in the system set, classify it through the stored intent and timestamps instead of immediately calling it completed.

## Action design

AlarmKit can perform its built-in stop/countdown behavior and can invoke additional App Intent-based actions configured through AlarmConfiguration. Keep action design narrow:

| Action | Safe meaning | Guard |
| --- | --- | --- |
| Stop | Stop the current alarm | Idempotent; do not also create a domain event twice |
| Repeat/countdown | Start the documented post-alert countdown behavior | Show the resulting duration in review |
| Open app | Navigate to the matching detail/review destination | Use a deep link or stable route id |
| Mark complete | Record an app-owned completion only after the user’s explicit action | Never infer completion from alert delivery |
| Start external side effect | Use only when the user explicitly configured it | Use an idempotency key and surface failure |

App Intent code should be short. It should validate current domain state, call a safe service, and return a user-understandable result. Do not put a model call, network dependency, or irreversible multi-step workflow directly in a time-critical system action.

## AI proposal boundary

For an on-device AI alarm builder:

1. ask the model for a typed proposal;
2. record model availability and prompt/schema version;
3. validate with deterministic code;
4. render editable fields;
5. require confirmation;
6. call AlarmKit only from the confirmed command;
7. save the source/provenance;
8. reconcile the resulting system alarm.

Test fixture cases should include:

- “tomorrow at 8” with no time zone change;
- “every weekday”;
- “in 20 minutes”;
- an ambiguous time such as “after lunch”;
- an unsupported recurrence;
- a date in the past;
- a duplicate of an existing alarm;
- a private label that should be shortened before system presentation;
- Foundation Models unavailable.

Do not market the language interface as medical, therapeutic, or guaranteed. An alarm schedules attention; it does not prove a person performed the task.

## Failure routes

| Failure | State to retain | Recovery |
| --- | --- | --- |
| Authorization denied | Draft and normalized proposal | Explain Settings; offer ordinary reminder only if the product supports it |
| Missing usage description | Build/configuration failure | Fix target configuration before release |
| Schedule throws | Draft, error category, no registered claim | Retry after revalidation |
| Widget target missing for countdown | Draft and requested countdown | Add/repair widget target; do not ship countdown as complete |
| Alarm disappears | Registered record plus unknown/fired candidate | Reconcile against the stored schedule |
| App is terminated | Durable intent record | Rebuild from persistence and AlarmManager on next launch |
| User changes time zone | Original intent plus current system observation | Re-render local meaning and test expected recurrence |
| App Intent repeats | Idempotency key and domain state | Return the existing result instead of duplicating work |
| AI unavailable | Direct editor fields | Preserve the user’s goal without the model |

## Proof gate

The recipe is ready for a real app only when the selected target proves the relevant rows in the [AlarmKit proof matrix](../60-verification/17-alarmkit-and-time-based-action-proof-matrix.md). At minimum, separate:

- source and SDK signature evidence;
- compilation and target membership;
- unit tests for normalization and recurrence;
- preview/widget fixtures;
- simulator UI evidence;
- signed physical-device alarm delivery;
- Lock Screen/Dynamic Island/StandBy/paired-device evidence where supported;
- release configuration, privacy strings, and TestFlight evidence.

A green preview or successful schedule call in a development run is not proof of delivery after process termination.

## Sources

- [AlarmKit](https://developer.apple.com/documentation/alarmkit)
- [Scheduling an alarm with AlarmKit](https://developer.apple.com/documentation/AlarmKit/scheduling-an-alarm-with-alarmkit)
- [AlarmManager](https://developer.apple.com/documentation/alarmkit/alarmmanager)
- [Alarm](https://developer.apple.com/documentation/alarmkit/alarm)
- [AlarmManager schedule](https://developer.apple.com/documentation/alarmkit/alarmmanager/schedule%28id%3Aconfiguration%3A%29)
- [AlarmConfiguration alarm](https://developer.apple.com/documentation/alarmkit/alarmmanager/alarmconfiguration/alarm%28schedule%3Aattributes%3Aappentityidentifier%3Astopintent%3Asecondaryintent%3Asound%3A%29)
- [AlarmConfiguration timer](https://developer.apple.com/documentation/alarmkit/alarmmanager/alarmconfiguration/timer%28duration%3Aattributes%3Aappentityidentifier%3Astopintent%3Asecondaryintent%3Asound%3A%29)
- [AlarmMetadata](https://developer.apple.com/documentation/alarmkit/alarmmetadata)
- [AlarmAttributes](https://developer.apple.com/documentation/alarmkit/alarmattributes)
- [NSAlarmKitUsageDescription](https://developer.apple.com/documentation/BundleResources/Information-Property-List/NSAlarmKitUsageDescription)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [Displaying live data with Live Activities](https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities)
- [ActivityAttributes](https://developer.apple.com/documentation/activitykit/activityattributes)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [Managing notifications](https://developer.apple.com/design/human-interface-guidelines/managing-notifications)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
