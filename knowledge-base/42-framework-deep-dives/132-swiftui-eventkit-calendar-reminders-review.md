# SwiftUI EventKit and EventKitUI calendar/reminders review

EventKit is the app-facing access layer for a person’s Calendar and Reminders databases. EventKitUI is the system-managed editing, viewing, and calendar-selection surface. SwiftUI owns the app’s explanation, draft, review, loading, error, and reconciliation states around those frameworks.

The reliable mental model is:

```text
user intent
    -> least-privilege access decision
    -> EKEventStore lifetime and authorization state
    -> app-owned draft or EventKitUI handoff
    -> explicit user review and commit
    -> system record identity / change notification
    -> refetch and UI reconciliation
```

An authorization Boolean, an `EKEvent` in memory, a successful `save`, a dismissed editor, or a generated scheduling suggestion is not proof that the intended Calendar or Reminders workflow is correct. Calendar data belongs to the person and can change from another device, another app, a system UI surface, or an account synchronization event.

This review is for iOS 26-targeted native apps. The recipes remain compile-oriented sketches until they are checked against the final SDK and exercised with real calendars and reminders on a physical device.

## Choose the narrowest EventKit lane

| Product outcome | First route | Permission and ownership boundary |
| --- | --- | --- |
| Let a person create one calendar event with Apple’s editor | `EKEventEditViewController` through EventKitUI | On iOS 17 and later, Apple documents that presenting the event editor for event creation does not require the app to request calendar access. The system UI owns the save interaction. |
| Create events directly from an app-owned workflow without reading Calendar | `EKEventStore` plus `requestWriteOnlyAccessToEvents()` | Write-only access can create events but cannot read existing calendars or events, including events the app created. Do not build a read-dependent UI on this lane. |
| Search, edit, delete, or reconcile calendar events | `EKEventStore` plus `requestFullAccessToEvents()` | Full event access is required for reading event data. Keep the store alive while its EventKit objects are in use. |
| Read or create reminders | `EKEventStore` plus `requestFullAccessToReminders()` | Current EventKit access is full access for reminders; there is no read-only request. Scope the feature and explain why reminder data is needed. |
| Show a saved event or allow a person to edit it | `EKEventViewController` or `EKEventEditViewController` | EventKitUI owns a system-managed modal workflow. Delegate completion is a UI outcome; refetch the EventKit record afterward. |
| Let a person choose a writable calendar | `EKCalendarChooser` | Let the system surface the calendars and writable/read-only state. Revalidate the chosen calendar before a direct save. |
| Suggest a time, title, or reminder decomposition with on-device AI | Foundation Models proposal -> deterministic validation -> person review -> one of the above lanes | The model proposes app-owned values. It must not receive unneeded private calendar records or write to EventKit without a reviewable, validated commit. |

Do not request full Calendar access merely because the app can technically ask for it. If the feature only needs a person to create an event, prefer the EventKitUI editor or write-only access as appropriate.

## Authorization is an access-level state machine

The modern `EKEventStore` API distinguishes the event and reminder entity types and exposes access states such as `.notDetermined`, `.writeOnly`, `.fullAccess`, `.denied`, and `.restricted` through `EKAuthorizationStatus`. The older `.authorized` value is deprecated in the current API shape; do not collapse all non-denied results into “full read/write.”

Model permissions separately:

| State | Calendar event behavior | Reminder behavior | UI treatment |
| --- | --- | --- | --- |
| Not determined | Explain the exact action that needs access, then request only the required level. | Same, using full reminder access when the feature reads or writes reminders. | A purpose-first action, not a surprise prompt on launch. |
| Write only | Create events directly; do not read calendars, events, or app-created events from the store. | Not the normal reminder lane. | Keep the UI write-only: compose, review, commit, and show local receipt state without claiming database readback. |
| Full access | Fetch, create, edit, delete, and reconcile events. | Fetch, create, edit, delete, and reconcile reminders. | Show current data only after a successful fetch and preserve denied/error states. |
| Denied | The app cannot rely on the protected store for the denied entity. | Same. | Explain how to enable access in Settings or offer a no-permission draft/export path. |
| Restricted | Access is constrained by system policy. | Same. | Do not repeatedly prompt; provide a deterministic fallback and a clear boundary. |

On iOS 17 and later, include the appropriate privacy purpose strings. Apple documents `NSCalendarsWriteOnlyAccessUsageDescription` for write-only event creation, `NSCalendarsFullAccessUsageDescription` for reading and writing calendar data, and `NSRemindersFullAccessUsageDescription` for reading and writing reminders. The older `NSCalendarsUsageDescription` and `NSRemindersUsageDescription` keys are not a substitute for the modern access-level keys on the current target.

Access requests are asynchronous and may complete on an arbitrary queue when using completion handlers. Prefer the async variants in a concurrency-aware app, then update the UI on the main actor. Authorization can change outside the current view, so refresh status at scene or feature boundaries and after the store’s change notification.

## Keep a long-lived event store with its objects

`EKEventStore` is the main point of contact with Calendar and Reminders. EventKit objects retrieved from one store cannot be used with another store. Apple’s event-store guidance also warns that releasing a store before other EventKit objects can cause errors. Make the ownership explicit:

```text
feature coordinator / model
    owns one EKEventStore
        owns fetched EKEvent / EKReminder / EKCalendar references
            publishes app projections to SwiftUI
```

Do not create a new store in every row, computed property, `body` evaluation, or button action. Do not pass an EventKit object between unrelated stores. Keep the store and the observation token together; tear both down when the feature no longer needs them.

The store’s `eventStoreIdentifier` identifies the store instance/context, while calendar items expose local and external identifiers. `calendarItemIdentifier` is useful for looking up an item with `calendarItem(withIdentifier:)`, but Apple documents that a full sync can make the local identifier no longer fetchable. Cache a user-facing or app-owned projection and be prepared to re-resolve. `calendarItemExternalIdentifier` can identify the same item across devices, but duplicates can exist for imports, shared calendars, invitations, delegates, or subscriptions. Use calendar/source context and other stable fields when disambiguating.

Never treat an EventKit identifier as an authorization token, a permanent database primary key, or proof that a record still exists.

## Events and reminders have different date models

An `EKEvent` uses `startDate` and `endDate` and can be all-day, recurring, alarm-bearing, attached to a calendar, or associated with attendees and structured location. Floating/all-day event values are returned in the default time zone; the app should retain the intended calendar/time-zone context in its own draft and display model.

An `EKReminder` uses `startDateComponents` and `dueDateComponents`. Date components carry date and time-zone information together. Apple documents that omitting hour, minute, and second creates an all-day reminder, a `nil` time zone represents a floating date, and the calendar must be Gregorian for these properties. On iOS, a start date is required when a due date is set. Do not turn a reminder due date into an event `Date` without preserving whether it is floating, all-day, or time-zone-specific.

Use a typed app-owned draft rather than binding a form directly to EventKit objects:

```text
CalendarDraft
    title
    notes
    local start/end or reminder date components
    time zone / all-day intent
    selected calendar identifier
    recurrence intent
    alarm intent
    user confirmation state
```

At commit time, normalize the draft, resolve the calendar, create or update the EventKit object, save it, and publish a small receipt projection. If the save fails, retain the draft and error; do not silently claim success.

## Recurrence and alarms are product semantics, not decoration

`EKRecurrenceRule` describes daily, weekly, monthly, or yearly repetition with an interval and optional end. Complex rules can add days of the week, days of the month, months, weeks, days of the year, and set positions. A recurrence rule is assigned to an event or reminder. Apple documents that the rule is not directly mutable; create a new rule when changing the recurrence definition.

EventKit uses `EKSpan` when changing or deleting a recurring event: `.thisEvent` affects one occurrence and `.futureEvents` affects that occurrence and future instances. Make this choice explicit in a confirmation dialog. “Edit this event” and “edit all future events” are different user actions and should produce different app commands.

Reminders have an important product-specific rule: for a recurring set, EventKit exposes only the first incomplete reminder; after it is completed, the next one becomes available. A list UI that assumes every occurrence is independently fetchable will misrepresent the system data.

Alarms can be absolute-date or relative-offset alarms, and EventKit also exposes proximity-related alarm properties. Keep alarm intent in the draft and show the actual saved alarm in the receipt. An AI proposal may suggest “15 minutes before,” but only the validated `EKAlarm` attached to the committed record is system truth.

## Save, delete, and batching are explicit commits

Calendar and reminder mutations require specific user instruction. Apple’s EventKit guidance says an app should not modify the Calendar database without confirmation from the person. This matters even if a model, import, automation, or background task generated the draft.

Use `EKEventStore.save(_:span:commit:)` for events and `save(_:commit:)` for reminders. With `commit: true`, the change is committed immediately. With `commit: false`, batch related changes and call `commit()` once. Handle thrown errors. When deleting a recurring event, apply the same explicit span and confirmation semantics.

After a save:

1. capture the returned or newly available item identifiers only as lookup hints;
2. publish a “submitted” state while the store synchronizes;
3. refetch the record or the relevant date range with full access; and
4. display the reconciled system value, including any server or calendar normalization.

When the person chooses EventKitUI, the UI’s `.saved`, `.deleted`, or `.canceled` action is a presentation result. For `.saved`, the app should still refetch. For `.deleted`, remove the local projection only after reconciling the store or receiving the corresponding change.

## Fetches are bounded queries, not a permanent snapshot

For events, create a predicate with `predicateForEvents(withStart:end:calendars:)`, then call `events(matching:)` or `enumerateEvents(matching:using:)`. Apple documents that event results are not necessarily chronological and that the predicate matches a maximum four-year span; sort the returned app projection and bound the requested window.

For reminders, use `predicateForReminders(in:)`, `predicateForIncompleteReminders(withDueDateStarting:ending:calendars:)`, or the completed-reminder predicate as appropriate, then call `fetchReminders(matching:completion:)`. The reminder fetch is asynchronous and returns a request token that can be canceled. Keep cancellation and view-generation state so a late result cannot overwrite a newer query.

Do not query on every keystroke or every SwiftUI render. Debounce search, bound date windows, apply calendar filters, and move synchronous event enumeration away from a latency-sensitive rendering path. A “no results” array can mean no records, denied access, an uncommitted draft, a stale store, an overly narrow predicate, or an unavailable source; keep those states distinguishable.

## Change notifications require invalidation and refetch

`EKEventStoreChangedNotification` / `EKEventStore.EventStoreChanged` indicates that Calendar or Reminders changed. It is not a complete diff. Apple’s EventKit headers state that when this notification arrives, existing `EKEvent` instances should be considered invalid; release and refetch the displayed range. If an event is actively being viewed or edited, call `refresh()` and continue only if the object remains valid.

A robust reducer treats a change as:

```text
store changed
    -> invalidate fetched projections
    -> refresh authorization and source/calendar list
    -> refetch bounded visible range
    -> reconcile local drafts and pending receipts
    -> announce what changed, if useful
```

Do not infer which calendar changed from the notification. Do not keep stale pointers in a long-lived SwiftUI list. Keep an app-owned `revision` or generation counter so a late fetch from before the notification cannot replace newer data.

## EventKitUI is a system-owned interaction lane

`EKEventEditViewController` is a modal system UI for creating, editing, and deleting events. Set its `eventStore`, optionally provide a partially constructed event, retain a delegate, and dismiss the controller when the delegate reports the completion action. New events use the default calendar unless the person chooses another calendar in the UI.

`EKEventViewController` displays an existing event and can optionally allow editing. `EKCalendarChooser` lets the person select one or more calendars and can be configured to show all calendars or only writable calendars. These controllers are not replacements for app-owned authorization and reconciliation state; they are system interaction surfaces that reduce the app’s need to recreate Calendar UI.

On iOS 17 and later, Apple documents that EventKitUI presents the editor and chooser outside the app’s process and can be used without requesting write-only or full Calendar access for the system-managed flow. Keep the boundary visible: a system UI save can be successful while the app still lacks permission to read the resulting event back through `EKEventStore`.

In SwiftUI, wrap a UIKit controller with `UIViewControllerRepresentable` only at the system-UI edge. Keep the wrapper small, pass a stable store and event, and map delegate actions into an app command. Do not mirror the entire Calendar editor in SwiftUI merely to make it look custom; use the system surface when it expresses the user’s intent well.

## Native SwiftUI and Liquid Glass design

An Apple-like calendar or reminder feature is mostly hierarchy and state clarity:

```text
top-level purpose
    -> scope/calendar filter
    -> current range or list
    -> item rows with semantic date/status
    -> one obvious add/review action
    -> permission, sync, or stale-state explanation
```

Use standard SwiftUI navigation, `List`, `Section`, `Form`, `DatePicker`, `Toggle`, `Menu`, `Searchable`, and semantic `Button` controls first. Let the system provide control behavior and accessibility. If Liquid Glass is appropriate on the target SDK, apply it to a small functional control group or toolbar/surface; do not cover dense calendar rows in translucent glass. The record’s title, date, reminder completion, and conflict/error state must remain legible when transparency is reduced or glass is unavailable.

Recommended states to design explicitly:

| State | Surface copy / behavior |
| --- | --- |
| Access needed | “Allow Calendar access to show and update these events.” Explain full versus write-only purpose before the prompt. |
| Write-only | “You can create an event, but this app can’t read Calendar data.” Do not show a fake calendar list. |
| Empty | Distinguish “no items in this range” from “access unavailable.” |
| Draft | Show local, unsaved values with a clear Review and Cancel path. |
| Saving | Disable duplicate commit, preserve the draft, and expose cancellation if the route supports it. |
| Reconciled | Show the system-normalized title/date/calendar and a stable receipt. |
| Changed elsewhere | Refetch and explain if a visible item moved, changed, or disappeared. |
| AI proposal | Show source inputs, proposed values, confidence/uncertainty language, and a required human commit. |

Support Dynamic Type, VoiceOver labels and values, keyboard and pointer input on iPad, non-color status cues, Reduce Motion, Increase Contrast, Reduce Transparency, and a text equivalent for every calendar/reminder action. A glass button that says only “+” without an accessibility label is not a native-quality add flow.

## Optional on-device AI scheduling proposals

Foundation Models can help transform user-authored intent into a typed proposal, such as a title, duration, candidate time windows, recurrence intent, and reminder offset. Keep raw Calendar and Reminders records out of the model unless the feature has a clear, consented, minimized reason to use them. Prefer structured app-owned inputs:

```text
user-authored task or meeting intent
    + selected date range / working hours
    + explicitly supplied constraints
    -> typed SchedulingProposal
    -> deterministic conflict and policy validation
    -> human review
    -> EventKitUI or direct EventKit commit
```

The model must not choose a calendar identifier, delete a record, mutate a recurrence span, or send a commit command directly. Validate title length, time-zone interpretation, duration, recurrence frequency, alarm offset, date bounds, calendar eligibility, and duplicate risk. If Foundation Models is unavailable, busy, refused, or returns invalid output, fall back to an ordinary form or a deterministic slot picker.

Treat an AI proposal as stale when the visible date range, authorization state, calendar list, or underlying EventKit revision changes. Re-run validation immediately before commit. Log the proposal version and the final user-edited values, not private calendar contents.

## Privacy and data minimization

Calendar events and reminders can reveal schedules, health appointments, work relationships, locations, and personal routines. Request the least privilege that completes the task, use precise usage descriptions, avoid sending raw records to a server by default, and make retention/deletion behavior explicit.

Keep three values separate:

- user-authored draft data;
- EventKit data returned by the system; and
- generated AI proposal data.

Do not use an EventKit object as a general-purpose Codable cache. Store only the minimum app-owned projection needed for display, reconciliation, or an explicitly approved offline workflow. Redact titles, attendees, locations, and notes from diagnostics unless the person has approved that logging.

## Verification boundary

| Claim | Minimum evidence |
| --- | --- |
| Privacy configuration is correct | Built `Info.plist` contains the modern calendar/reminder usage keys with purpose-first text; deprecated-only configurations are rejected. |
| Least-privilege request works | Physical device shows the requested access level and the app handles not-determined, write-only, full, denied, and restricted states. |
| Direct event creation works | Full or write-only gate as required, explicit review, save error handling, committed item refetch, and Calendar app confirmation. |
| Reminder creation works | Full reminder access, Gregorian/date-component fixture, start/due semantics, save/reload, completion, and Reminders app confirmation. |
| EventKitUI flow works | Present editor/viewer/chooser, exercise saved/deleted/canceled actions, dismiss correctly, and reconcile afterward. |
| Recurrence/alarm semantics work | Test this occurrence versus future occurrences, recurrence end, time zone, all-day, relative alarm, and deletion behavior on physical data. |
| Change recovery works | Change the record in Calendar/Reminders or a second device, observe the store change, invalidate/refetch, and verify no stale row survives. |
| SwiftUI design works | Dynamic Type, VoiceOver, Reduce Motion/Transparency, Increase Contrast, keyboard/pointer, iPad layout, localization/RTL, and glass fallback task evidence. |
| AI is safe | Availability/error/refusal, typed-output validation, stale proposal rejection, privacy-minimized inputs, deterministic fallback, and human commit evidence. |
| Release works | Archive, signed installation, TestFlight retest, target privacy metadata, and a physical-device run with real system Calendar/Reminders accounts. |

The [EventKit/EventKitUI design review](../21-design-deep-dives/160-swiftui-eventkit-calendar-reminders-review-design.md), [route worksheet](../50-capability-recipes/163-swiftui-eventkit-calendar-reminders-review-route.md), [proof matrix](../60-verification/157-swiftui-eventkit-calendar-reminders-proof-matrix.md), and [code recipes](../70-code-recipes/175-swiftui-eventkit-calendar-reminders-review-recipes.md) turn these boundaries into reusable project artifacts.

## Sources

- [EventKit](https://developer.apple.com/documentation/eventkit)
- [Accessing the event store](https://developer.apple.com/documentation/eventkit/accessing-the-event-store)
- [Creating events and reminders](https://developer.apple.com/documentation/eventkit/creating-events-and-reminders)
- [Retrieving events and reminders](https://developer.apple.com/documentation/eventkit/retrieving-events-and-reminders)
- [Creating a recurring event](https://developer.apple.com/documentation/eventkit/creating-a-recurring-event)
- [EKEventStore](https://developer.apple.com/documentation/eventkit/ekeventstore)
- [requestWriteOnlyAccessToEvents(completion:)](https://developer.apple.com/documentation/eventkit/ekeventstore/requestwriteonlyaccesstoevents%28completion%3A%29)
- [requestFullAccessToEvents(completion:)](https://developer.apple.com/documentation/eventkit/ekeventstore/requestfullaccesstoevents%28completion%3A%29)
- [requestFullAccessToReminders(completion:)](https://developer.apple.com/documentation/eventkit/ekeventstore/requestfullaccesstoreminders%28completion%3A%29)
- [authorizationStatus(for:)](https://developer.apple.com/documentation/eventkit/ekeventstore/authorizationstatus%28for%3A%29)
- [EKAuthorizationStatus](https://developer.apple.com/documentation/eventkit/ekauthorizationstatus)
- [EKEvent](https://developer.apple.com/documentation/eventkit/ekevent)
- [EKReminder](https://developer.apple.com/documentation/eventkit/ekreminder)
- [EKCalendar](https://developer.apple.com/documentation/eventkit/ekcalendar)
- [EKCalendarItem](https://developer.apple.com/documentation/eventkit/ekcalendaritem)
- [calendarItemIdentifier](https://developer.apple.com/documentation/eventkit/ekcalendaritem/calendaritemidentifier)
- [calendarItemExternalIdentifier](https://developer.apple.com/documentation/eventkit/ekcalendaritem/calendaritemexternalidentifier)
- [EKRecurrenceRule](https://developer.apple.com/documentation/eventkit/ekrecurrencerule)
- [EKRecurrenceEnd](https://developer.apple.com/documentation/eventkit/ekrecurrenceend)
- [EKAlarm](https://developer.apple.com/documentation/eventkit/ekalarm)
- [events(matching:)](https://developer.apple.com/documentation/eventkit/ekeventstore/events%28matching%3A%29)
- [enumerateEvents(matching:using:)](https://developer.apple.com/documentation/eventkit/ekeventstore/enumerateevents%28matching%3Ausing%3A%29)
- [fetchReminders(matching:completion:)](https://developer.apple.com/documentation/eventkit/ekeventstore/fetchreminders%28matching%3Acompletion%3A%29)
- [predicateForEvents(withStart:end:calendars:)](https://developer.apple.com/documentation/eventkit/ekeventstore/predicateforevents%28withstart%3Aend%3Acalendars%3A%29)
- [predicateForIncompleteReminders(withDueDateStarting:ending:calendars:)](https://developer.apple.com/documentation/eventkit/ekeventstore/predicateforincompletereminders%28withduedatestarting%3Aending%3Acalendars%3A%29)
- [EKEventStore.EventStoreChanged](https://developer.apple.com/documentation/eventkit/ekeventstore/eventstorechanged)
- [EKEventEditViewController](https://developer.apple.com/documentation/eventkitui/ekeventeditviewcontroller)
- [EKEventEditViewDelegate](https://developer.apple.com/documentation/eventkitui/ekeventeditviewdelegate)
- [EKEventEditViewAction](https://developer.apple.com/documentation/eventkitui/ekeventeditviewaction)
- [EKEventViewController](https://developer.apple.com/documentation/eventkitui/ekeventviewcontroller)
- [EKCalendarChooser](https://developer.apple.com/documentation/eventkitui/ekcalendarchooser)
- [EventKit UI](https://developer.apple.com/documentation/eventkitui)
- [UIViewControllerRepresentable](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [NSCalendarsFullAccessUsageDescription](https://developer.apple.com/documentation/bundleresources/information_property_list/nscalendarsfullaccessusagedescription)
- [NSCalendarsWriteOnlyAccessUsageDescription](https://developer.apple.com/documentation/bundleresources/information_property_list/nscalendarswriteonlyaccessusagedescription)
- [NSRemindersFullAccessUsageDescription](https://developer.apple.com/documentation/bundleresources/information_property_list/nsremindersfullaccessusagedescription)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
