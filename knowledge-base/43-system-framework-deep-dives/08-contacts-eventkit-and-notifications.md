# Contacts, EventKit, and User Notifications deep dive

Contacts, calendars, reminders, and notifications are personal-data and system-surface routes. They look simple in a view but cross permission scope, partial access, account/store state, background delivery, system UI, and privacy. A sound iOS 26 architecture keeps these boundaries explicit:

~~~text
user task
  -> minimum data/surface route
  -> authorization and current settings
  -> bounded fetch or user-mediated system UI
  -> app-owned projection/draft
  -> review and validation
  -> save/schedule/system handoff
  -> change/revocation/delivery reconciliation
~~~

## Choose the narrowest route

| User outcome | Primary API | Boundary |
| --- | --- | --- |
| Select a person without importing the address book | ContactsUI contact access button/picker or contact picker route | User-mediated selection is different from broad Contacts authorization and bulk fetch. |
| Find a small set of contacts | CNContactStore, predicate, keysToFetch | Fetch only needed keys, perform I/O off the main thread, and refetch after store changes. |
| Create or edit a calendar event with system UI | EKEventEditViewController | The system editor can save the event; a custom store route may need different access. |
| Read or write calendar data | EKEventStore with write-only or full event access | Write-only events cannot be used to read calendar data; full access has a broader privacy boundary. |
| Read or write reminders | EKEventStore full reminders access | Permission, account/source state, recurrence, completion, and store changes remain explicit. |
| Schedule a local notification | UNUserNotificationCenter, UNNotificationRequest, content, trigger | Authorization settings, trigger behavior, actions, foreground handling, and privacy copy. |
| Handle a remote notification | APNs registration/payload and UNUserNotificationCenter delegate | Token/provider/server delivery is separate from local notification scheduling and UI. |
| Let AI draft a contact/calendar/notification action | Typed proposal -> current-state validation -> confirmation | Generated text is not a contact, event, reminder, authorization, or delivery result. |

## Contacts: partial access and least privilege

CNContactStore represents the user’s Contacts database and fetches or saves contacts, groups, and containers. Access is per app and can be denied, limited, or full. A product that only needs a person’s selection should prefer a user-mediated access/picker route over importing every contact.

If the feature uses CNContactStore:

1. Ask for the entity access required by the task.
2. Explain why before the system prompt.
3. Fetch only the keys the feature needs.
4. Use predicates and identifier batches rather than loading every property of every contact.
5. Perform I/O off the main thread.
6. Treat every returned contact as possibly partial.
7. Refetch cached contacts when CNContactStoreDidChange is posted.
8. Handle limited access by showing what is available and offering the system’s contact-access controls where appropriate.
9. Treat contact identifiers as references that need re-resolution, not as personal identity proof.

The contact store can save changes through CNSaveRequest, but the app should make the exact mutation visible and avoid bulk editing without a clear user action. Notes and other sensitive fields can have additional entitlement/configuration boundaries; do not request or fetch them by default.

## EventKit: write-only, full access, or system UI

EKEventStore is the point of contact for calendar event and reminder data. Current EventKit APIs distinguish:

- write-only calendar access for creating events without reading calendar data;
- full access to events for reading and writing calendar data;
- full access to reminders for reading and writing reminders;
- system EventKit UI, such as EKEventEditViewController, when the product can let the person complete the save through Apple’s editor instead of directly accessing the database.

Do not request full access just to create one event if a system editor satisfies the outcome. The event store must be kept alive while its event/reminder objects are used, and the app should respond to EKEventStoreChangedNotification by refreshing state relevant to the screen.

Treat dates, time zones, recurrence, alarms, calendar source, invitation status, and event identifiers as separate state. A draft event is not saved until the store or system editor confirms it. A local “saved” flag is not proof that the person’s calendar contains the event.

## Notifications: authorization is a changing setting

UNUserNotificationCenter manages local and remote notification-related activity. Request only the options the feature needs, and do so in a context that explains the value. Always inspect UNNotificationSettings because people can change alert, sound, badge, lock-screen, notification-center, and CarPlay settings later.

Separate notification layers:

1. Authorization and current settings.
2. Content: title, subtitle, body, badge, sound, category, thread, relevance, and privacy.
3. Trigger: time interval, calendar, location, or remote delivery.
4. Request identity and pending/delivered state.
5. Foreground delegate behavior and action handling.
6. Provider/APNs delivery when the notification is remote.

Use an alert for an in-app error instead of scheduling a notification that says “open the app to fix this.” Avoid sensitive, personal, or confidential content because the notification may appear when someone else can see the screen. Do not send multiple notifications for one unresolved condition simply because the person has not responded.

For a local request:

~~~text
draft content -> privacy review -> trigger -> unique request ID
              -> schedule -> inspect pending state
              -> deliver/foreground/action -> reconcile or remove
~~~

For remote notifications, the server/provider, APNs token, environment, payload, delivery, and system presentation are separate evidence records. A successful registerForRemoteNotifications callback does not prove the provider delivered the content.

## Data and system-surface ownership

Contacts and EventKit own system data. User Notifications owns delivery/presentation constraints. The app owns the task projection and any user-created draft until it hands off or saves.

Use explicit model layers:

~~~text
system record
  -> normalized read projection
  -> user draft
  -> validation
  -> confirmed mutation or notification request
  -> system change/delivery callback
~~~

Do not copy a full contact book or calendar into a local database unless the product has a clear authorization, retention, deletion, freshness, and sync plan. Keep only identifiers and fields needed for the task, and re-resolve them before acting. If a record disappears or permission narrows, invalidate the draft rather than applying to a different record.

## AI and personal data

Bounded on-device intelligence can help:

- turn a selected text into an event draft;
- identify missing time zone, duration, invitee, or reminder information;
- summarize a selected contact or event using only the chosen fields;
- propose a reminder time from an explicit user instruction;
- explain why a notification would be suppressed by current settings;
- group a user-selected set of contacts or events for review.

The model should receive the smallest authorized context, and its output should decode into types such as ContactSelection, EventDraft, ReminderDraft, or NotificationDraft. Deterministically validate dates, time zones, contact IDs, permissions, notification settings, and privacy class. Require confirmation before saving or scheduling. Do not let a natural-language model silently send a message, modify a contact, create an event, or schedule a sensitive notification.

Keep source context and generated text separate from canonical records. If the calendar or contact store changes while a review sheet is open, mark the proposal stale and resolve again.

## Design and Liquid Glass

Apple-like personal-data surfaces prioritize clarity and restraint:

- Show why a person is being asked for access before the system prompt.
- Use a contact’s selected name and relevant field, not a wall of raw contact properties.
- Show calendar title, date, time zone, duration, recurrence, and destination calendar before save.
- Show notification timing, content, category, and privacy level before scheduling.
- Keep pending, denied, limited, stale, and saved states distinct.
- Use system pickers/editors when they reduce privacy and configuration burden.
- Use Liquid Glass around app-owned review controls, not as a replacement for the system permission or editor surface.
- Keep destructive contact/calendar mutations visibly separate and confirmable.
- Preserve text, accessible values, and high-contrast states when transparency is reduced.

Do not build a decorative dashboard that exposes private data just because glass makes it look polished. The surface should make the person’s choice and the data scope obvious.

## Accessibility and localization

Test:

- VoiceOver reading order for contact identity, selected fields, event details, notification settings, and save state;
- Dynamic Type with long names, long event titles, localized dates, time zones, and error messages;
- Voice Control and Switch Control for selection, review, save, cancel, and retry;
- calendar formats, first weekday, 12/24-hour preferences, daylight-saving transitions, and right-to-left text;
- notification content that remains understandable without color or sound;
- reduced motion/transparency for sheets, review cards, and pending state;
- contact disambiguation when names repeat.

Never use a haptic or notification sound as the only indication of a saved event or changed contact. Announce material state changes without stealing focus from an active editor.

## Failure and fallback states

| Failure | Fallback |
| --- | --- |
| Contacts denied/limited | Use user-mediated selection, manual entry, or selected contacts only. |
| Contact changed/deleted | Refetch by identifier and ask the person to resolve if missing. |
| EventKit access denied | Use system editor where available or export/manual instructions. |
| Calendar/reminder store changed | Refresh visible records and invalidate stale drafts. |
| Notification denied | Keep in-app timeline/status and explain Settings; do not imply delivery. |
| Notification settings narrowed | Reduce requested behavior and show the current limitation. |
| Local schedule rejected | Preserve the draft and provide a retry/correction path. |
| APNs/provider failure | Keep app state accurate and avoid claiming notification delivery. |
| AI unavailable/ambiguous | Use manual fields and deterministic validation. |

## Evidence checklist

- target Info.plist usage descriptions and signed artifact inspection;
- limited/full/denied/restricted Contacts states;
- key-minimized fetch, background I/O, partial contact, store-change, save, and deletion tests;
- EventKit write-only/full event/reminder access, system editor, time zones, recurrence, store change, and account/source errors;
- notification authorization options, settings changes, pending/delivered requests, foreground handling, actions, privacy redaction, and remote provider/APNs evidence if used;
- AI prompt/context minimization, typed decode, stale invalidation, confirmation, refusal, and fallback;
- VoiceOver, Dynamic Type, localization, reduced motion/transparency, and alternate-input task completion;
- signed release configuration and App Review/privacy declarations.

## Sources

- [Contacts](https://developer.apple.com/documentation/contacts)
- [CNContactStore](https://developer.apple.com/documentation/contacts/cncontactstore)
- [Accessing the contact store](https://developer.apple.com/documentation/contacts/accessing-the-contact-store)
- [CNContact](https://developer.apple.com/documentation/contacts/cncontact)
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
- [UNMutableNotificationContent](https://developer.apple.com/documentation/usernotifications/unmutablenotificationcontent)
- [UNCalendarNotificationTrigger](https://developer.apple.com/documentation/usernotifications/uncalendarnotificationtrigger)
- [Notifications HIG](https://developer.apple.com/design/human-interface-guidelines/notifications/)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
