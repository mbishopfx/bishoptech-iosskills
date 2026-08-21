# SwiftUI EventKit and EventKitUI calendar/reminders proof matrix

Use this matrix to keep source knowledge, compile evidence, permission behavior, system records, UI quality, optional AI, and release proof separate. A green row is evidence for that row only.

## Proof matrix

| Claim | Source/compile check | Simulator or fixture | Physical/system proof | Release evidence | Failure boundary |
| --- | --- | --- | --- | --- | --- |
| The target declares the correct privacy purpose | Inspect built `Info.plist`; confirm modern Calendar/Reminders keys match the requested level. | N/A | Trigger each request on a clean device and record the prompt copy. | Archive inspection and TestFlight install. | A source `Info.plist` entry or permission Boolean alone does not prove the shipped target prompt. |
| Event write-only access is least privilege | Compile `requestWriteOnlyAccessToEvents()` and status handling. | Reducer fixtures for `.notDetermined`, `.writeOnly`, `.fullAccess`, `.denied`, `.restricted`. | Grant write-only access; verify the app can create as designed but cannot read a calendar list or readback event. | TestFlight retest with reset permission history. | A created event or app-owned receipt is not proof of readable Calendar access. |
| Full event access works | Compile async full-access request and `authorizationStatus(for:)`. | Authorization state-machine tests. | Grant full access, fetch a bounded range, edit/delete a test event, and confirm in Calendar. | Archive entitlements/Info.plist and TestFlight retest. | “Granted” without a successful real fetch is incomplete. |
| Full reminder access works | Compile async reminder request and status path. | Reminder state fixtures, including denied and empty. | Create/fetch/complete a test reminder in the Reminders app and verify list/calendar ownership. | Signed build on the same device family. | A reminder draft or empty array does not prove access or correct list selection. |
| EventKit store ownership is correct | Compile one long-lived `EKEventStore`; audit no cross-store object use. | Unit fixture prevents objects crossing coordinator generations. | Use the feature while records are displayed and after scene/background transitions. | Release build smoke test. | A singleton-looking property is not proof of valid object lifetime. |
| Calendar/list resolution is correct | Compile identifier lookup, entity filtering, writable/immutable checks, and default-calendar fallback. | Missing/immutable/read-only calendar fixtures. | Select a real writable calendar and confirm the saved record lands there; test account removal or read-only source. | TestFlight account/device matrix. | Calendar title/color alone cannot prove source or writability. |
| Event date/time semantics are correct | Compile `Date` mapping, all-day, time-zone, and recurrence normalization. | Fixtures for DST, 12/24-hour, locale, all-day, floating, and cross-zone inputs. | Create events around DST and time-zone changes; compare Calendar’s displayed result. | Archive and physical retest on target OS. | A formatted string or UTC timestamp alone is not proof of user-visible time semantics. |
| Reminder date components are correct | Compile `startDateComponents`/`dueDateComponents` normalization and Gregorian guard. | All-day, floating, timed, missing-start, and invalid-date fixtures. | Create reminders and compare due/start behavior in Reminders. | TestFlight device/account evidence. | Converting reminder components into a `Date` can hide important semantics. |
| Recurrence edits have the intended span | Compile `EKRecurrenceRule` and `EKSpan` branch. | Single occurrence/future occurrence/end-count fixtures. | Edit and delete “this event” versus “future events”; verify every affected occurrence. | Release build retest with real account sync. | A recurrence rule object does not prove the Calendar database applied the intended span. |
| Alarms are correct | Compile relative and absolute `EKAlarm` creation. | Offset/date normalization fixtures. | Verify the alarm in Calendar/Reminders and observe notification timing where appropriate. | TestFlight retest with notification settings. | An alarm attached in memory is not proof of system scheduling. |
| Direct save/delete is explicit and recoverable | Compile `try`/`catch`, `commit` choice, duplicate-submit guard, and draft retention. | Error, cancellation, retry, and stale-draft fixtures. | Make a real save/delete and confirm the system record; force or simulate account/source failure where possible. | Signed archive and TestFlight. | A `save` call returning without error is not the full user-visible workflow. |
| EventKitUI editor works | Compile `UIViewControllerRepresentable`, store/event assignment, delegate action mapping, and dismissal. | Preview wrapper and delegate-action reducer fixtures. | Present editor, save/delete/cancel, choose a calendar, and confirm the resulting system record. | TestFlight UI smoke test. | `.saved` or dismissal alone does not prove post-edit reconciliation. |
| Event viewer and calendar chooser work | Compile controller wrappers and delegate paths. | Reducer fixtures for chosen calendars and viewer actions. | View an event, test read-only/editable behavior, choose writable/read-only calendars, and confirm app state. | Release UI run on iPhone/iPad as applicable. | The controller’s appearance does not prove the app applied the selection. |
| Event queries are bounded and sorted | Compile date-range predicate and app-side sort. | Four-year-limit, empty, overlapping, and out-of-order fixture data. | Fetch a real range and compare visible rows to Calendar. | TestFlight performance smoke test. | An array from `events(matching:)` is not guaranteed chronological. |
| Reminder fetch cancellation works | Compile request-token retention/cancellation and generation checks. | Late-result and canceled-query fixtures. | Change list/date filters rapidly on a device with real reminder data. | TestFlight run with logging. | No crash does not prove stale results were excluded. |
| Store-change recovery works | Compile notification observer, invalidation, refetch, and active-item `refresh()` branch. | Change-generation reducer and stale-fetch fixtures. | Edit/delete a record in Calendar/Reminders or another device; verify the app refetches and removes stale rows. | TestFlight account-sync retest. | A notification received without invalidation/refetch is incomplete. |
| SwiftUI state is honest | Compile separate access, draft, saving, system UI, reconciled, changed, denied, and error states. | Preview matrix across all states and dynamic sizes. | Exercise the full task with real data and permission changes. | TestFlight screenshots/screen recording. | A single “loading/success” Boolean hides important system boundaries. |
| Liquid Glass is restrained and adaptable | Compile target-available glass route and fallback. | Reduced-transparency and unsupported-glass previews. | Test glass enabled/disabled, Increase Contrast, Reduce Transparency, and the dense-list route on device. | Archive on minimum supported OS/device matrix. | A screenshot proves appearance at one state, not legibility or adaptation. |
| Accessibility task completion works | Accessibility audit plus identifiers and semantic labels compile. | Dynamic Type, VoiceOver rotor/action fixtures, Reduce Motion/Transparency previews. | VoiceOver add/view/edit/complete task, keyboard/pointer route on iPad, RTL/localized long titles. | TestFlight accessibility pass. | An audit or label string alone does not prove a person completed the task. |
| AI scheduling proposal is safe | Compile `@Generable` schema, availability/error handling, validation, and fallback. | Invalid title/date/time-zone/recurrence/duplicate/stale proposal fixtures. | Run on a supported device with model available and unavailable; compare accepted values to EventKit record. | TestFlight with model availability matrix. | A plausible proposal or model transcript is not proof of correct system mutation. |
| Privacy minimization holds | Audit prompt inputs, logs, local caches, and analytics redaction. | Synthetic titles/locations/attendees only. | Inspect on-device data and exercise deny/delete/revoke paths. | Release privacy review and metadata check. | A local model does not automatically make an over-collected feature private. |
| Background/scene recovery is honest | Compile scene task cancellation and coordinator recreation. | Kill/relaunch and stale-task fixtures where deterministic. | Create/edit outside the app, background, terminate, relaunch, and verify refetch. | TestFlight cold-launch run. | A foreground fetch does not prove account/system changes are recovered after relaunch. |
| Distribution is correct | Inspect bundle, SDK, deployment target, privacy keys, and framework links. | N/A | Install signed archive/TestFlight and repeat the protected-data flow. | Archive export, TestFlight build, device matrix, release checklist. | A local debug run or compile is not release proof. |

## Fixture catalog

### Access fixtures

- event status: not determined, write only, full access, denied, restricted;
- reminder status: not determined, full access, denied, restricted;
- missing modern usage keys and deprecated-only key configuration;
- authorization changed while a view is active; and
- EventKitUI editor available with no direct read permission.

### Data fixtures

- event with all-day, timed, floating, DST-boundary, and cross-time-zone dates;
- event with a relative alarm and an absolute alarm;
- weekly/monthly/complex recurrence with end date and end count;
- reminder with date-only, timed, floating, start/due, completion, and recurring first-incomplete semantics;
- immutable/read-only calendar, missing calendar, duplicate external identifier, and source/account change; and
- event or reminder deleted/changed between fetch and save.

### UI and AI fixtures

- empty, denied, write-only, saving, reconciled, changed-elsewhere, and error states;
- very long titles, RTL, Dynamic Type, Reduce Motion, Reduce Transparency, Increase Contrast, and iPad keyboard/pointer;
- valid typed scheduling proposal;
- invalid date/time-zone/recurrence/alarm proposal;
- stale proposal after store revision or calendar-list change; and
- model unavailable/refusal/error with deterministic manual-form fallback.

## Evidence naming

Use names that make the boundary obvious:

```text
eventkit-access-write-only-iphone26-2026-08-20.json
eventkit-full-event-reconcile-calendar-change-iphone26-2026-08-20.mp4
eventkit-reminder-due-components-dst-iphone26-2026-08-20.json
eventkit-editor-saved-refetch-testflight-<build>.json
eventkit-ai-proposal-invalid-fallback-<model-state>.json
```

Redact titles, attendee names, locations, notes, account identifiers, and private system screenshots before sharing evidence.

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
- [EKRecurrenceRule](https://developer.apple.com/documentation/eventkit/ekrecurrencerule)
- [EKAlarm](https://developer.apple.com/documentation/eventkit/ekalarm)
- [EKEventStore.EventStoreChanged](https://developer.apple.com/documentation/eventkit/ekeventstore/eventstorechanged)
- [EventKit UI](https://developer.apple.com/documentation/eventkitui)
- [EKEventEditViewController](https://developer.apple.com/documentation/eventkitui/ekeventeditviewcontroller)
- [EKEventViewController](https://developer.apple.com/documentation/eventkitui/ekeventviewcontroller)
- [EKCalendarChooser](https://developer.apple.com/documentation/eventkitui/ekcalendarchooser)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
