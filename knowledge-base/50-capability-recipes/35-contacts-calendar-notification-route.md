# Contacts, Calendar, Reminders, and Notifications route

Use this route when an app needs people, events, reminders, or timely system updates. Pick the smallest system boundary first:

~~~text
user intent
  -> picker/editor/direct-store decision
  -> minimum authorization
  -> bounded read or draft
  -> deterministic validation
  -> user confirmation
  -> save/schedule/system handoff
  -> store/settings/delivery reconciliation
~~~

## Route selector

| Need | Smallest route | Avoid |
| --- | --- | --- |
| Choose a contact | ContactsUI picker/access button | Full address-book import. |
| Read selected contact fields | CNContactStore by identifier with limited keys | Fetching all keys for every contact. |
| Create one calendar event | EventKit system editor where suitable | Full calendar read access for a write-only task. |
| Read and edit calendar events | EKEventStore full event access | Treating local drafts as saved records. |
| Read/write reminders | EKEventStore full reminders access | Background assumptions about account/source availability. |
| Local reminder notification | UNUserNotificationCenter request/content/trigger | Scheduling before checking authorization/settings. |
| Remote update | APNs/provider + notification center delegate | Calling a register callback delivery proof. |
| AI-assisted entry | Typed draft -> validation -> review -> save/schedule | Direct model-to-store mutation. |

## Shared state model

Keep system data, app drafts, and delivery state separate:

~~~swift
struct PersonalDataRouteState {
    var contactsAccess: AccessState
    var calendarAccess: AccessState
    var remindersAccess: AccessState
    var notificationSettings: NotificationSettingsSnapshot
    var selectedContact: ContactReference?
    var eventDraft: EventDraft?
    var reminderDraft: ReminderDraft?
    var notificationDraft: NotificationDraft?
    var lastStoreChange: Date?
}
~~~

The exact types belong in the target. The ownership contract does not:

- Contacts/EventKit own the protected stores.
- User Notifications owns current presentation settings and delivery behavior.
- The app owns the selected task, draft, validation, UI, and fallback.
- AI owns only generated suggestions.
- The system completion/store-change/delegate path owns reconciliation.

## Route A: select a contact with least privilege

1. Explain why the person is selecting a contact.
2. Prefer a user-mediated Contact access button/picker when full store access is unnecessary.
3. Store only the selected identifier and fields needed for the task.
4. Re-resolve the contact before writing, sending, or generating a proposal.
5. Handle limited access, deletion, duplicate names, and permission changes.

If the product needs broad fetching:

1. Request Contacts access at the task boundary.
2. Fetch only the keys needed.
3. Run I/O off the main thread.
4. Use identifiers and batches for detail fetches.
5. Refresh caches after CNContactStoreDidChange.

## Route B: create an event

### System editor route

Use EKEventEditViewController when the person can complete the save through the familiar system editor. This can avoid broad direct store access for a one-event creation task. Handle cancellation and save result distinctly.

### Direct EventKit route

1. Create and retain an EKEventStore for the route’s lifetime.
2. Request write-only event access when the product only creates events.
3. Request full event access only when it must read/edit/delete event data.
4. Build a draft with title, start/end, time zone, calendar, recurrence, alarms, and notes policy.
5. Validate date order, time zone, calendar availability, and privacy.
6. Ask for confirmation.
7. Save and reconcile from the store.
8. Refresh after EKEventStoreChangedNotification.

Do not claim an event is in the calendar because a view model contains an event ID. Re-fetch or use the system editor result according to the selected route.

## Route C: create a reminder

1. Request full reminders access only when direct reminder read/write is needed.
2. Select a list/source from current EventKit state.
3. Validate title, notes, due date/time, recurrence, priority, and alarms.
4. Confirm the exact list and schedule.
5. Save and reconcile.
6. Refresh on store changes and handle account/source removal.

If permission is unavailable, preserve the draft and offer a local in-app task or manual instructions without calling it a system reminder.

## Route D: schedule a notification

1. Explain the user benefit in context.
2. Request only the alert/sound/badge options required.
3. Read UNNotificationSettings before scheduling or rescheduling.
4. Create privacy-reviewed content.
5. Create a stable request identifier and trigger.
6. Add the request and inspect pending requests if the product needs a management screen.
7. Handle foreground delivery, action responses, and current settings changes.
8. Remove or update obsolete requests.

State model:

~~~text
notRequested -> requesting -> authorized
                         -> denied/provisional/limited behavior
authorized -> draft -> scheduled -> delivered/acted/removed
settings changed -> recompute presentation -> update or suppress
~~~

The notification body is a public surface. Keep sensitive detail out of it unless the person has deliberately chosen that exposure and the product’s privacy policy supports it.

## Route E: AI-assisted personal-data draft

Use a typed proposal:

~~~swift
struct EventDraftProposal {
    var title: String
    var start: Date?
    var end: Date?
    var timeZone: TimeZone?
    var calendarIdentifier: String?
    var attendeeContactIDs: [String]
    var sourceText: String
    var validationMessages: [String]
    var requiresConfirmation: Bool
}
~~~

Before applying:

- re-resolve contact identifiers and calendar/list identifiers;
- verify current access;
- validate time zone and date semantics;
- remove fields not needed for the requested task;
- show all proposed side effects;
- require confirmation;
- mark the proposal stale after a store/settings change.

The same route applies to reminders and notification drafts. AI can shorten a notification or suggest a time; it cannot grant permission, decide that a contact match is correct, or guarantee system delivery.

## Fallbacks

| Failure | Fallback |
| --- | --- |
| Limited contacts | Contact picker, selected identifiers, or manual entry. |
| Contact changed | Refetch and ask for disambiguation. |
| Event read access denied | System editor, write-only creation, or export/manual route. |
| Reminder unavailable | Local task state with honest wording. |
| Notification denied | In-app timeline, badge-free status, or Settings guidance. |
| Alert/sound setting disabled | Adjust copy and use permitted behavior. |
| Store changed | Refresh and invalidate stale drafts. |
| AI unavailable | Manual form with deterministic validation. |
| APNs unavailable | Local/system state remains accurate without delivery claim. |

## Build slices

1. Contact picker or one-field contact selection.
2. Contacts permission/limited state and identifier re-resolution.
3. One EventKit system-editor event draft.
4. Direct EventKit write-only/full access branch if required.
5. Reminder draft and store-change reconciliation.
6. Local notification request/settings/foreground route.
7. Typed AI event/reminder/notification proposals.
8. Privacy, accessibility, localization, Liquid Glass review, and release proof.

## Sources

- [Contacts](https://developer.apple.com/documentation/contacts)
- [CNContactStore](https://developer.apple.com/documentation/contacts/cncontactstore)
- [Accessing the contact store](https://developer.apple.com/documentation/contacts/accessing-the-contact-store)
- [ContactsUI](https://developer.apple.com/documentation/contactsui)
- [EventKit](https://developer.apple.com/documentation/eventkit)
- [EKEventStore](https://developer.apple.com/documentation/eventkit/ekeventstore)
- [Accessing the event store](https://developer.apple.com/documentation/eventkit/accessing-the-event-store)
- [EKEvent](https://developer.apple.com/documentation/eventkit/ekevent)
- [EKReminder](https://developer.apple.com/documentation/eventkit/ekreminder)
- [EKEventEditViewController](https://developer.apple.com/documentation/eventkitui/ekeventeditviewcontroller)
- [User Notifications](https://developer.apple.com/documentation/usernotifications)
- [UNUserNotificationCenter](https://developer.apple.com/documentation/usernotifications/unusernotificationcenter)
- [Requesting authorization](https://developer.apple.com/documentation/usernotifications/unusernotificationcenter/requestauthorization%28options%3Acompletionhandler%3A%29)
- [UNNotificationSettings](https://developer.apple.com/documentation/usernotifications/unnotificationsettings)
- [UNNotificationRequest](https://developer.apple.com/documentation/usernotifications/unnotificationrequest)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy/)
- [Notifications HIG](https://developer.apple.com/design/human-interface-guidelines/notifications/)
