# Native alarm and countdown surfaces

## Design goal

An alarm feature is a promise about attention and time. The visual system should make that promise legible:

    intent -> review -> authorization -> scheduled state
       -> countdown -> alert -> stop/repeat -> outcome

The app-owned screen is for choosing and understanding the alarm. AlarmKit’s system-owned surfaces are for making the current state glanceable and actionable. A widget extension can provide a custom countdown presentation, but it is still a system surface with different size, luminance, safe-area, and interaction constraints.

The target is native coherence, not a replica of Apple’s Clock app. Keep the product’s own identity in content, metadata, tint, and workflow. Let system-owned alarms look and behave like system-owned alarms.

## Surface ownership

| Surface | Product job | Design responsibility | Avoid |
| --- | --- | --- | --- |
| Alarm editor | Choose time, days, duration, sound, label, and follow-up | Make every time rule explicit; show local-time meaning and recurrence | A free-form “magic” field with no preview of the actual schedule |
| Review/confirm sheet | Confirm the side effect before authorization and scheduling | Summarize exact date/time, repeat rule, countdown, sound, and visible alert copy | Hiding the system impact behind a generic Save button |
| App-owned alarm list | Manage records and recovery | Separate registered, paused, fired, cancelled, denied, and unknown states | Showing every local row as currently scheduled |
| AlarmKit alert | Interrupt with the required action | Supply concise, localized alert content and safe secondary behavior | Adding a mini dashboard or making the user decode a brand illustration |
| AlarmKit countdown | Show progress and pause/repeat affordance | Use a short title and one clear state | Treating a countdown as proof that an external job is running |
| Widget extension / Live Activity | Glanceable progress on Lock Screen, Dynamic Island, StandBy, or paired surfaces | Adapt to each presentation and keep metadata sufficient | Assuming every device has the same surface or available space |
| Post-alert app destination | Explain what happened and offer the next domain action | Reconcile with AlarmManager before enabling irreversible actions | Landing on a stale detail screen with no system-state refresh |

The system presentation may be visible while the device is locked. Keep labels free of private data unless the person explicitly chose that level of exposure. A label such as “Medication” may be meaningful but sensitive; the product should make that tradeoff clear and avoid putting private notes in alarm metadata.

## Review before side effect

Use a focused confirmation surface when the person creates or accepts an alarm:

1. title or task label;
2. exact next occurrence in the device’s current calendar and time zone;
3. repeat days, or “once”;
4. countdown and repeat/snooze behavior;
5. sound or alert choice;
6. what appears in the system alert;
7. a primary action with a verb such as “Schedule alarm”;
8. a secondary action to edit or cancel.

The primary action should not be “Continue” when the operation schedules an alert. HIG guidance for alerts emphasizes that interruptions should be essential and actionable. The app-owned review card is the place to make that action legible before the system takes over.

For AI-assisted creation, show the parsed result as structured fields instead of only repeating the model’s prose:

| Proposed field | Review treatment |
| --- | --- |
| “Tomorrow morning” | Resolve to an explicit date and local time; do not silently guess an hour. |
| “Every workday” | Show the exact weekday set and allow editing. |
| “In 20 minutes” | Show the calculated fire time and countdown duration. |
| Label | Show the exact alert title that may be visible on a locked device. |
| Follow-up action | Explain whether it stops, repeats, opens the app, or only updates an app-owned record. |

The model can reduce typing. It must not reduce informed consent.

## Layout and Liquid Glass

Use Liquid Glass in the app-owned editor only when it improves the hierarchy between content and controls. A good composition is:

    background or quiet context
        -> one readable schedule summary
        -> functional glass action group
        -> secondary configuration sections

Good uses:

- a glass action group containing Schedule alarm and Edit;
- a morphing transition from an alarm list row to a detail/editor surface;
- a glass toolbar that keeps the current schedule visible while options change;
- a compact timer control that remains legible over a calm background.

Poor uses:

- a translucent layer over every row and label;
- fake glass around the system-owned AlarmKit alert;
- blur that reduces the contrast of a time, day, or action;
- animation that makes the countdown harder to read;
- a glass card that suggests an alarm is registered before the schedule call succeeds.

Prefer system controls, semantic Button actions, native typography, and platform spacing. Keep glass functional: it should group, elevate, or transition an action. It should not be the product’s only explanation of state.

When an app-owned timer view uses glass, the content should remain the visual anchor. The remaining time, label, and primary action need a stable reading order in light mode, dark mode, reduced transparency, and large Dynamic Type. If the glass treatment causes focus or contrast problems, return to an opaque or less layered composition.

## State language

Use explicit state language in the app list and detail surfaces:

| Internal state | User-facing label | Next action |
| --- | --- | --- |
| Draft | Not scheduled | Review and schedule |
| Not determined | Alarm access needed | Enable alarms |
| Denied | Alarm access is off | Open Settings |
| Registered | Scheduled | Edit or cancel |
| Countdown | Counting down | Pause or stop |
| Paused | Paused | Resume or stop |
| Alerting | Alerting now | Stop or repeat |
| Missing from system set | Needs checking | Refresh status |
| Fired and reconciled | Finished | View outcome |
| Cancelled | Cancelled | Schedule again |
| Schedule error | Couldn’t schedule | Review and retry |

Do not use “active” for all of these states. “Active” can mean the app’s local record is enabled, the countdown is running, or the alarm is currently alerting. The UI should name the actual state.

When the app cannot prove whether a one-shot alarm fired or was cancelled, use a neutral recovery state such as “Needs checking” and explain the source of uncertainty. That is more trustworthy than inventing a completed outcome.

## Countdown and alert content

AlarmPresentation.Alert provides the title and optional secondary button while the system provides stop behavior. AlarmPresentation.Countdown can offer pause, and AlarmPresentation.Paused requires a resume action. Use the smallest content that identifies the task and the next useful operation.

Content rules:

- title: short, sentence-style, and localized;
- button label: a verb that describes the outcome;
- symbol: a familiar SF Symbol that reinforces the verb;
- tint: differentiates the app’s alarm family but does not carry the only meaning;
- metadata: only the small presentation data needed by the widget;
- sound: chosen as part of the reviewed alarm configuration, not hidden in a default;
- repeat/snooze: describe the resulting duration, not just the word “Repeat.”

Avoid model-generated alarm titles that contain private context, unsupported claims, or ambiguous urgency. If the user’s label is long, truncate only in the system surface while preserving the full label in the app-owned record and accessibility value as appropriate.

## Widget and Live Activity composition

If the alarm supports a countdown presentation, the widget extension is part of the route. Build separate layout decisions for:

- Lock Screen;
- Dynamic Island expanded, compact, and minimal forms;
- StandBy;
- paired Apple Watch surfaces when supported.

The countdown view should answer three questions at a glance:

1. What is this?
2. What state is it in?
3. What can I do now?

Keep the time visually dominant, but do not remove the label or state. Use system-provided date/countdown formatting when it gives the correct behavior across time zones and reduced luminance. Do not assume an exact pixel size from an Xcode preview is the final system surface.

The widget extension should read from AlarmAttributes and AlarmPresentationState. It should not query a private database, perform network work, or make a scheduling decision while rendering. If metadata is missing or stale, render a safe fallback and let the app reconcile.

Use the widget’s own accessibility description to express the whole state in one sentence. A VoiceOver user should hear the task, remaining time or paused status, and available action without needing to infer meaning from color or position.

## Accessibility and adaptation

Alarm UI is time-sensitive, so adaptation is part of correctness:

- Dynamic Type: allow the title and schedule summary to grow; do not crop the only time value;
- localization: test longer weekday names, 12/24-hour preferences, right-to-left languages, and translated action labels;
- VoiceOver: announce schedule semantics, not implementation terms such as “relative recurrence”;
- Voice Control: make actions speakable and unique;
- Switch Control and Full Keyboard Access: preserve a predictable action order;
- Reduce Motion: do not animate a countdown in a way that changes the perceived time;
- Reduce Transparency: preserve contrast with an opaque fallback;
- increased contrast and color differences: never encode paused, alerting, or denied only with tint;
- Assistive Access: keep the schedule summary and primary action understandable in simplified layouts.

For app-owned countdown views, use a stable accessibility identity when the numeric value updates rapidly. Do not force repeated announcements for every tick. Announce meaningful transitions such as started, paused, resumed, alerting, and stopped.

## Time, calendar, and localization

Time is content. Display the person’s selected time with the current locale, calendar, and time-zone meaning. The review surface should distinguish:

- one-time instant;
- local repeating time;
- countdown from now;
- post-alert repeat duration.

When a relative weekly alarm crosses a daylight-saving transition or the person changes time zones, refresh the explanation from the current AlarmKit schedule and the app’s stored intent. Do not display a stale date copied from the moment of creation.

For a natural-language builder, keep the original request alongside the normalized proposal. If the original phrase is “after dinner,” the app should not pretend that the system schedule is exact until the person chooses a time.

## Failure and recovery surfaces

Design the failure states before polishing the success state:

| Failure | Helpful response |
| --- | --- |
| Authorization denied | Keep the draft; explain Settings and provide a non-alarm reminder alternative if the product supports one. |
| Missing usage description | Treat as a build/configuration defect; do not show a misleading runtime success state. |
| Schedule call throws | Keep the intent as unscheduled, show the error category, and offer retry after revalidation. |
| App record exists but AlarmKit no longer lists it | Show “Needs checking,” reconcile, and avoid claiming delivery. |
| Widget metadata cannot decode | Show a minimal fallback and log the schema/version mismatch for the build. |
| User changes the alarm while alerting | Make the state transition explicit; do not create a second alarm by accident. |
| Model unavailable | Return to a deterministic editor with the same typed fields. |

Do not use a celebratory confetti animation for scheduling an alarm. The important feedback is a calm, precise confirmation that the system operation succeeded and what the person can do next.

## Native route checklist

Before calling the design Apple-native, verify:

- the app uses semantic controls and localized system text;
- the schedule is understandable without the glass treatment;
- the system-owned alert is not recreated as a custom imitation;
- the countdown supports all required system surfaces;
- the app distinguishes local intent from AlarmKit registration;
- the AI proposal is reviewable and never schedules without confirmation;
- Dynamic Type, VoiceOver, Reduce Motion, and reduced transparency have explicit behavior;
- the time-zone and recurrence meaning is visible;
- the proof plan includes a supported physical device and system surfaces.

The [AlarmKit framework deep dive](../42-framework-deep-dives/11-alarmkit-and-time-based-actions.md), [capability recipe](../50-capability-recipes/23-alarmkit-scheduled-action-route.md), and [proof matrix](../60-verification/17-alarmkit-and-time-based-action-proof-matrix.md) carry the implementation and evidence boundaries.

## Sources

- [AlarmKit](https://developer.apple.com/documentation/alarmkit)
- [Scheduling an alarm with AlarmKit](https://developer.apple.com/documentation/AlarmKit/scheduling-an-alarm-with-alarmkit)
- [AlarmPresentation.Alert](https://developer.apple.com/documentation/alarmkit/alarmpresentation/alert-swift.struct)
- [AlarmPresentation.Countdown](https://developer.apple.com/documentation/alarmkit/alarmpresentation/countdown-swift.struct)
- [AlarmPresentation.Paused](https://developer.apple.com/documentation/alarmkit/alarmpresentation/paused-swift.struct)
- [AlarmButton](https://developer.apple.com/documentation/alarmkit/alarmbutton)
- [AlarmAttributes](https://developer.apple.com/documentation/alarmkit/alarmattributes)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [Displaying live data with Live Activities](https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities)
- [Creating custom views for Live Activities](https://developer.apple.com/documentation/ActivityKit/creating-custom-views-for-live-activities)
- [Managing notifications](https://developer.apple.com/design/human-interface-guidelines/managing-notifications)
- [Alerts](https://developer.apple.com/design/human-interface-guidelines/alerts)
- [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles)
- [Designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
