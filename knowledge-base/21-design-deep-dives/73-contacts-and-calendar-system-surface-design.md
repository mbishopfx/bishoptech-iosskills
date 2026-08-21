# Contacts and Calendar system-surface design

Contacts and Calendar surfaces should feel native by making the person’s choice obvious, not by copying Apple’s private screens. The app owns the task framing and review state; ContactsUI and EventKitUI own the protected picker, card, editor, and chooser interactions.

## Choose a system surface first

| Task | Preferred surface |
| --- | --- |
| Choose one person for a task | Contact picker |
| Reveal more contacts under limited access | ContactAccessButton or system contact access picker |
| Show a contact card | Contact view controller |
| Create an event from a user-approved draft | Event edit view controller |
| Inspect an existing event | Event view controller |
| Choose a writable calendar | Calendar chooser |
| Search and aggregate many records | App-owned Contacts/EventKit route with explicit authorization |

Do not ask for full access to make a single selection or event. A system surface that satisfies the outcome is usually more privacy-preserving and more recognizably native.

## Review before handoff

For an AI-assisted event flow:

~~~text
selected text or task
  -> proposed title/date/time/zone/duration
  -> review and edit
  -> choose destination calendar
  -> system EventKit editor
  -> local action result
~~~

For a contact flow:

~~~text
task
  -> contact-picker action
  -> selected contact/property
  -> app-owned redacted projection
  -> next explicit action
~~~

The contact picker’s final selection should be enough for the immediate task. Avoid showing or storing unrelated contact fields after the person chooses someone.

## Liquid Glass with personal data

Use Liquid Glass only for app-owned context:

- a compact task header;
- a draft/review card;
- a selected contact chip;
- an event proposal summary;
- a status capsule for stale, limited, or awaiting confirmation.

Keep names, phone numbers, emails, dates, time zones, and recurrence on high-contrast content surfaces. Do not allow translucency to make private text look decorative or to hide the exact destination of a mutation. The system picker/editor should appear as the system surface, not inside a counterfeit glass replica.

Use motion to communicate transitions between app-owned review and system-owned UI. Do not animate a “saved” celebration until the delegate/result state proves the local outcome.

## Limited contact access is an ongoing choice

When Contacts access is limited, the app should make the current scope understandable:

- show only contacts actually available to the app;
- offer the system ContactAccessButton near a search field when the task needs another contact;
- keep manual entry available where practical;
- refresh after Settings or the system access control changes;
- distinguish no match from no authorization from a contact outside the current scope.

Do not show a fake “all contacts” list with blank details. It creates ambiguity and encourages the person to expand access without understanding why.

## Calendar editor is not a form replacement

An app-owned form can help the person shape an event proposal, but EventKitUI should be the final system editor when it satisfies the user’s task. Show:

- title and purpose;
- local date/time and time zone;
- duration;
- recurrence;
- alerts;
- selected calendar or why the person will choose it;
- invitee/disclosure implications;
- whether the app will retain a local copy.

If the app uses a write-only/editor-first route, explain that the event will be handed to Calendar and that the app may not know every final field the person changes in Apple’s editor. If the app needs to read or reconcile calendar data later, explain and request the separate access level required.

## AI proposals need human-readable provenance

Place source and uncertainty near the proposal:

- “From the selected task note”
- “Time zone inferred from the device setting”
- “Calendar destination not chosen yet”
- “Contact match requires your selection”

The person should be able to edit all meaningful fields before the system editor opens. A model’s confidence is not a substitute for showing the actual date, destination, or contact property.

## Accessibility and privacy

Test the entire route with:

- VoiceOver reading order for contact identity and event fields;
- Dynamic Type with long names and localized dates;
- Voice Control phrases that distinguish “Choose contact,” “Add access,” “Open Calendar,” and “Cancel”;
- Switch Control and keyboard navigation;
- right-to-left names and mixed-direction addresses;
- time zones, daylight-saving changes, and 12/24-hour preferences;
- reduced motion/transparency and high contrast;
- locked-device/private-data surfaces where previews or notifications are involved.

Do not announce a contact or calendar title in a notification unless the user has chosen that disclosure.

## State copy

Use explicit status language:

| State | Copy |
| --- | --- |
| Limited Contacts | “Only selected contacts are available.” |
| Picker cancelled | “No contact selected.” |
| Contact selected | “Selected for this task.” |
| Event draft | “Review before opening Calendar.” |
| Event editor completed | “Calendar reported: added/changed/deleted/cancelled.” |
| Store changed | “Calendar changed; review this draft again.” |
| Access denied | “Calendar access is unavailable; the draft is still here.” |

Avoid generic success badges that collapse selection, authorization, and persistence into one state.

## Sources

- [Contacts UI](https://developer.apple.com/documentation/contactsui)
- [CNContactPickerViewController](https://developer.apple.com/documentation/contactsui/cncontactpickerviewcontroller)
- [ContactAccessButton](https://developer.apple.com/documentation/contactsui/contactaccessbutton)
- [CNAuthorizationStatusLimited](https://developer.apple.com/documentation/contacts/cnauthorizationstatus/limited)
- [EventKit UI](https://developer.apple.com/documentation/eventkitui)
- [EKEventEditViewController](https://developer.apple.com/documentation/eventkitui/ekeventeditviewcontroller)
- [EKEventEditViewDelegate](https://developer.apple.com/documentation/eventkitui/ekeventeditviewdelegate)
- [EKEventViewController](https://developer.apple.com/documentation/eventkitui/ekeventviewcontroller)
- [EKCalendarChooser](https://developer.apple.com/documentation/eventkitui/ekcalendarchooser)
- [Accessing Calendar using EventKit and EventKitUI](https://developer.apple.com/documentation/eventkit/accessing-calendar-using-eventkit-and-eventkitui)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
