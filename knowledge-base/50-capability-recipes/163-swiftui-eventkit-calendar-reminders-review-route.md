# SwiftUI EventKit and EventKitUI calendar/reminders route worksheet

Use this worksheet before implementing a Calendar or Reminders feature in an iOS 26 app. It keeps access level, system record truth, app-owned drafts, EventKitUI state, optional on-device AI, and release evidence separate.

## Route card

| Field | Decision to record |
| --- | --- |
| User outcome | What does the person want to create, read, edit, complete, or reconcile? |
| Entity | Calendar event, reminder, event calendar, reminder list, or EventKitUI presentation. |
| Read requirement | None, write-only event creation, full event access, or full reminder access. |
| System UI route | Event editor, event viewer, calendar chooser, or app-owned SwiftUI form. |
| Direct mutation | Exact save/delete operation, `EKSpan`, commit behavior, and user confirmation. |
| Identity | Local `calendarItemIdentifier`, external identifier, calendar/source context, and app-owned draft ID. |
| Date model | Event `Date` values versus reminder `DateComponents`; all-day, floating, time zone, locale, and DST behavior. |
| Recurrence/alarm | Frequency, interval, end, span, alarm offset/date, and review language. |
| Change recovery | Store-change observation, invalidation/refetch window, active-item refresh, and stale-result generation. |
| AI boundary | Sanitized user-authored inputs, typed proposal, validation, human review, deterministic fallback, and no direct tool-side effect. |
| Privacy | Info.plist keys, retention, diagnostics redaction, account/system data handling, and deletion behavior. |
| Evidence | Permission, compile, UI, system Calendar/Reminders, physical device, archive/TestFlight, and release proof. |

## 1. Pick the route from the required authority

```text
Need to create one event only?
    yes -> EventKitUI editor if system-managed editing is sufficient
    no  -> direct EventKit write-only or full access based on the actual feature

Need to read or reconcile events?
    yes -> requestFullAccessToEvents and bounded queries
    no  -> do not ask for full event access

Need reminders?
    yes -> requestFullAccessToReminders for event-store reads/writes
    no  -> keep the feature out of the reminder data lane

Need a custom UI?
    yes -> SwiftUI draft/review plus direct EventKit commit, or wrap only the needed EventKitUI controller
    no  -> let EventKitUI own the protected edit/view/choose interaction
```

Do not make a later AI or automation feature the reason for requesting broader permission at launch. Add access when the person invokes the relevant capability.

## 2. Configure privacy before calling EventKit

Record the exact built-target keys:

| Feature | Required modern purpose key |
| --- | --- |
| Direct event creation without EventKitUI | `NSCalendarsWriteOnlyAccessUsageDescription` or full-access key if reading is needed. |
| Read/edit/delete events | `NSCalendarsFullAccessUsageDescription`. |
| Read/create/edit/delete reminders | `NSRemindersFullAccessUsageDescription`. |
| EventKitUI-only event creation on iOS 17+ | Apple documents that the editor can be presented without requesting calendar access; still test the target’s privacy and system-UI behavior. |

Write a purpose that describes the user-facing action, not “calendar API access.” Keep deprecated keys out of the current-target-only plan unless a separately supported older OS requires them and the compatibility matrix documents why.

## 3. Define the app-owned draft

Use a value type that is independent of `EKEvent` and `EKReminder`:

```text
DraftID
entity: event | reminder
title / notes
event start/end or reminder start/due DateComponents
calendar identifier hint
time zone / all-day intent
recurrence intent
alarm intent
source: manual | imported | AI-proposed
revision and last validation timestamp
```

The draft should survive a denied permission response, an editor cancellation, a stale EventKit fetch, or a validation error. It should not be advertised as saved until the system record is reconciled.

## 4. Establish the store and authorization state

Create one long-lived `EKEventStore` per feature/session boundary and retain it while its EventKit objects are in use. On feature entry:

1. read `EKEventStore.authorizationStatus(for:)` for `.event` and `.reminder`;
2. present the least-privilege explanation;
3. call the modern async request method only after the person chooses the action;
4. update status from the returned value and error; and
5. refetch only when the granted state supports the query.

Keep `.writeOnly` event state distinct from `.fullAccess`. A write-only store can create events but cannot be used to prove that the event exists by reading it back.

## 5. Resolve calendars and lists at commit time

Calendar and reminder-list availability can change. Store only an identifier hint in the draft. Before committing:

```text
draft calendar hint
    -> store.calendar(withIdentifier:)
    -> confirm entity type and allowsContentModifications
    -> confirm source/account and user-selected scope
    -> fallback to the documented default calendar only with user-visible policy
    -> assign calendar to the EventKit object
```

If a calendar is immutable, missing, read-only, or no longer supports the entity type, stop and ask the person to choose another destination. Do not silently move a work event to a personal calendar or a reminder to an unrelated list.

## 6. Normalize dates, recurrence, and alarms

Use a deterministic normalization step:

- reject an end before the event start unless the product explicitly supports correction;
- preserve all-day intent instead of inventing midnight times;
- retain the selected time zone or floating-date intent;
- build reminder `DateComponents` with the required Gregorian calendar semantics;
- require a reminder start date on iOS when a due date is set;
- validate recurrence frequency, interval, rule end, and `EKSpan` wording; and
- convert a relative alarm into an explicit preview such as “15 minutes before.”

Store the normalized draft snapshot used for commit so a later reconciliation can explain a system-normalized result.

## 7. Choose EventKitUI or direct commit

### EventKitUI editor

Use `EKEventEditViewController` when the person should review or choose system-managed event details. Pass the long-lived store and a minimal event draft. In the delegate:

```text
saved   -> dismiss -> refetch or present a reconciled receipt
deleted -> dismiss -> remove only after reconciliation
canceled -> dismiss -> restore the app-owned draft
```

The controller’s completion action does not tell the app that a custom server or app cache is synchronized.

### Direct EventKit commit

Use direct saves when the app owns a focused, confirmed workflow. Require:

- the correct access level;
- an explicit user command;
- a current calendar/list resolution;
- normalized values;
- duplicate/stale checks where relevant;
- `try`/`catch` around save/delete; and
- a post-commit refetch or clearly labeled write-only receipt.

Batch with `commit: false` only when atomic product behavior is clear and `commit()` errors can be surfaced without losing the draft.

## 8. Query and reconcile

Bound event queries to a date range and sort in the app projection. Bound reminder queries to the visible list/date range and keep a cancellable fetch token. On `EKEventStoreChangedNotification`:

```text
increment store revision
invalidate fetched EventKit objects
refresh sources/calendars if needed
refetch the visible range/list
drop late results from older revisions
reconcile active draft and receipts
```

If a record is actively being viewed or edited, attempt `refresh()` and abandon the object if it is no longer valid. Never use the change notification as a record-level diff.

## 9. Optional typed on-device AI route

The safe route is:

```text
sanitized user-authored intent
    -> Foundation Models typed SchedulingProposal
    -> deterministic schema/range/time-zone/duplicate validation
    -> user edits and accepts
    -> EventKitUI editor or direct EventKit commit
    -> refetch/reconcile
```

Recommended proposal fields:

```text
title
durationMinutes
candidateStart
timeZoneIdentifier
isAllDay
recurrenceKind / interval / end
reminderOffsetMinutes
reasoningSummaryForUser
```

Do not let the proposal carry a raw `EKEvent`, an `EKReminder`, an opaque calendar object, or a delete/save command. Do not claim “free” unless the feature actually read the relevant Calendar range with full access and validated the current revision. Reject stale proposals when authorization, calendar list, date range, or store revision changes.

## 10. Evidence package

Capture a small evidence bundle per route:

```text
route.json
  target / SDK / OS / device / build
  entity and selected access level
  Info.plist keys (values redacted if necessary)
  EventKitUI versus direct-save lane
  draft fixture and normalized date/recurrence/alarm values
  record identifier hints and post-save reconciliation result
  store-change/refetch log
  accessibility and reduced-effects result
  AI availability/proposal/fallback result, if used
  archive/TestFlight build metadata
screenshots or screen recording
  purpose explanation
  permission state
  draft/review/commit
  Calendar or Reminders system result
```

A simulator can prove deterministic state reducers and form layout. It does not prove the person’s real calendars, account synchronization, permission history, EventKitUI behavior, date/time-zone edge cases, or release provisioning.

## Sources

- [Accessing the event store](https://developer.apple.com/documentation/eventkit/accessing-the-event-store)
- [Creating events and reminders](https://developer.apple.com/documentation/eventkit/creating-events-and-reminders)
- [Retrieving events and reminders](https://developer.apple.com/documentation/eventkit/retrieving-events-and-reminders)
- [Creating a recurring event](https://developer.apple.com/documentation/eventkit/creating-a-recurring-event)
- [EKEventStore](https://developer.apple.com/documentation/eventkit/ekeventstore)
- [EKAuthorizationStatus](https://developer.apple.com/documentation/eventkit/ekauthorizationstatus)
- [EKEvent](https://developer.apple.com/documentation/eventkit/ekevent)
- [EKReminder](https://developer.apple.com/documentation/eventkit/ekreminder)
- [EKCalendar](https://developer.apple.com/documentation/eventkit/ekcalendar)
- [EKCalendarItem](https://developer.apple.com/documentation/eventkit/ekcalendaritem)
- [EKEventStore.EventStoreChanged](https://developer.apple.com/documentation/eventkit/ekeventstore/eventstorechanged)
- [EventKit UI](https://developer.apple.com/documentation/eventkitui)
- [EKEventEditViewController](https://developer.apple.com/documentation/eventkitui/ekeventeditviewcontroller)
- [EKEventViewController](https://developer.apple.com/documentation/eventkitui/ekeventviewcontroller)
- [EKCalendarChooser](https://developer.apple.com/documentation/eventkitui/ekcalendarchooser)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [UIViewControllerRepresentable](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
