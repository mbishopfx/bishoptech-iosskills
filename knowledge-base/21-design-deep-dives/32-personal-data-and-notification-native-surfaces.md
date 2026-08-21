# Personal-data and notification native surfaces

Contacts, calendars, reminders, and notifications deserve a calmer design than a generic “permissions plus dashboard” pattern. The person should always understand:

1. Which data or system surface is involved.
2. What the app is asking to read, write, or deliver.
3. What will happen now and what will happen later.
4. What is still a draft, what is saved, and what is only scheduled.
5. What remains useful when access or delivery is unavailable.

## Ask for access at the task boundary

The pre-permission screen should be a short explanation attached to a real action:

| Task | Better preparation copy | Avoid |
| --- | --- | --- |
| Pick a person | “Choose a contact to add to this invitation.” | “We need your contacts.” |
| Create an event | “Choose a calendar and save this appointment.” | Asking for full read access before showing the draft. |
| Schedule a reminder | “Allow reminders so this app can place the task in your list.” | Pretending a local timer is a system reminder. |
| Send a notification | “Get a reminder when your selected time arrives.” | Prompting at first launch before the person sees value. |

Apple’s privacy guidance treats contacts, calendar data, and user-generated content as protected data. Ask for the narrowest scope that completes the task. When a system editor or picker can complete the outcome without broad database access, make that route the default.

## The review-surface pattern

Use a review card or sheet before a mutation:

~~~text
source/context -> draft -> exact fields and scope -> validation
                                        -> confirm/save/schedule
                                        -> success or failure
~~~

### Contact review

Show the selected person, the fields that will be used, and the action. If multiple contacts match the same name, show disambiguating information without exposing unrelated fields. For a new contact or edit, show the fields being written and whether the person can undo the action.

### Event/reminder review

Show title, date, time, time zone, duration, recurrence, alarms, destination calendar/list, and invitees if relevant. Make a draft visibly different from a saved item. Use the system EventKit editor when it gives the person a familiar confirmation surface and avoids unnecessary full access.

### Notification review

Show what text may appear on the Lock Screen, when it may arrive, and whether sound/badge/action behavior is requested. Avoid putting private contact names, health-like information, or confidential event details in the notification body when the person has not intentionally chosen that exposure.

## Liquid Glass with private content

Liquid Glass can frame a review, filter, or confirmation control, but it should not make private data feel like decoration:

- Keep the content hierarchy opaque enough to read under transparency and increased contrast.
- Avoid displaying a full contact or calendar database in floating glass tiles.
- Use one bounded review container for the draft and its actions.
- Make scope and privacy cues text-first.
- Keep the system permission alert, system picker, and event editor system-owned.
- Use a restrained material treatment for pending/saved/error states.
- Do not animate from “draft” to “saved” until the system confirms the mutation.

The more sensitive the data, the less visual chrome is needed. A quiet sheet with exact fields often communicates trust better than a glowing dashboard.

## Notification design

Notifications are for timely, high-value information people can understand at a glance. Design a notification as a small message, not a remote control for the whole app:

- concise title/body;
- one meaningful trigger or update;
- one or two relevant actions at most;
- no duplicated reminders for the same unresolved condition;
- no secret or personal details that could be seen by someone else;
- a foreground behavior that updates the current screen without an intrusive duplicate alert;
- an in-app alert for an error that requires immediate attention.

When a notification action is appropriate, name it after the outcome: “Snooze,” “Mark Done,” or “View Details.” Avoid vague actions such as “Open” when the person needs to know what will happen.

## State language

| State | Design language |
| --- | --- |
| Access not requested | Explain the task and show the call to action. |
| Limited access | State that only selected contacts/data are available. |
| Denied | Keep manual or system-mediated alternatives visible. |
| Draft | “Ready to review” or “Not saved.” |
| Saving | Disable conflicting mutation and show progress. |
| Saved | Show the destination and a path to inspect or undo. |
| Scheduled | Show the trigger and current notification settings. |
| Delivery uncertain | Say “Scheduled” or “Not confirmed delivered,” not “You will see this.” |
| Stale | Refresh or ask the person to resolve the changed record. |
| Permission changed | Recompute the available fields/actions immediately. |

Do not turn a local Boolean into “saved” before EventKit, Contacts, or User Notifications accepts the operation.

## On-device AI review

Use AI to reduce form work, not to erase consent:

- parse a selected sentence into an event draft;
- suggest a reminder date from an explicit request;
- summarize a selected contact’s chosen fields;
- flag missing time zone or ambiguous attendee;
- propose a notification rewrite that is shorter and less revealing.

The review surface should expose:

- source text or selected fields;
- generated fields;
- uncertain or missing values;
- destination data store;
- exact side effect;
- confirmation button;
- edit path;
- privacy note when sensitive data is involved.

If Contacts access changes or an event is edited elsewhere, invalidate the proposal. If notification settings no longer allow sound or alerts, update the proposal and do not imply the original delivery behavior remains.

## Accessibility and localization

Sensitive-data flows often fail at the edges:

- Long names and event titles must wrap without hiding the primary action.
- VoiceOver should read data scope before the mutation button.
- Voice Control names should distinguish multiple “Save” or “Add” actions.
- Dynamic Type should preserve the draft fields and the confirmation result.
- Dates and times must respect locale, calendar, time zone, and daylight-saving transitions.
- Notification text must remain clear without sound, badge, color, or haptic feedback.
- Reduced motion should replace a sweeping save animation with a clear state change.
- Focus should remain in the editor when a background notification or store change arrives.

Use exact values and units where the person must make a decision; use summary text where the detail is secondary but still available.

## System surfaces versus app surfaces

| Surface | App owns | System owns |
| --- | --- | --- |
| Contact picker/access button | Preparation, selected-result handling, fallback | Access flow and contact selection UI. |
| EventKit editor | Draft preparation and result handling | Final event edit/save UI where used. |
| Calendar/reminder direct access | Projection, review, mutation, reconciliation | Protected store and permission policy. |
| Local notification | Content, trigger, request ID, in-app settings | Delivery timing, presentation, settings, and system UI. |
| Remote notification | Provider payload and app response | APNs transport and presentation constraints. |

Respect the handoff. A custom glass surface should not pretend it can guarantee a system-owned delivery or render a private system store without current authorization.

## Review checklist

- Is the data scope obvious before access?
- Is the narrowest permission or system-mediated picker/editor used?
- Is draft distinct from saved, scheduled, and delivered?
- Are partial access and permission changes visible?
- Are dates, time zones, recurrence, and store changes handled?
- Does notification copy remain private on a Lock Screen?
- Does AI produce an editable proposal with exact fields and confirmation?
- Does the screen work with VoiceOver, Dynamic Type, reduced motion/transparency, and alternate input?
- Does Liquid Glass support the task without turning private data into decorative chrome?

## Sources

- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy/)
- [Notifications HIG](https://developer.apple.com/design/human-interface-guidelines/notifications/)
- [Contacts](https://developer.apple.com/documentation/contacts)
- [CNContactStore](https://developer.apple.com/documentation/contacts/cncontactstore)
- [Accessing the contact store](https://developer.apple.com/documentation/contacts/accessing-the-contact-store)
- [ContactsUI](https://developer.apple.com/documentation/contactsui)
- [EventKit](https://developer.apple.com/documentation/eventkit)
- [EKEventStore](https://developer.apple.com/documentation/eventkit/ekeventstore)
- [Accessing the event store](https://developer.apple.com/documentation/eventkit/accessing-the-event-store)
- [EKEventEditViewController](https://developer.apple.com/documentation/eventkitui/ekeventeditviewcontroller)
- [User Notifications](https://developer.apple.com/documentation/usernotifications)
- [UNUserNotificationCenter](https://developer.apple.com/documentation/usernotifications/unusernotificationcenter)
- [UNNotificationSettings](https://developer.apple.com/documentation/usernotifications/unnotificationsettings)
- [UNNotificationRequest](https://developer.apple.com/documentation/usernotifications/unnotificationrequest)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
