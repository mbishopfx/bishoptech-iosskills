# ContactsUI and EventKitUI system proof matrix

This matrix separates person selection, authorization, system editing, and canonical persistence. A picker callback or EventKitUI action is useful evidence, but it does not prove broad data access, identity, or every field the person changed.

## Claim-to-evidence matrix

| Claim | Evidence required | Do not infer |
| --- | --- | --- |
| Contact selection does not need broad access | Target test with CNContactPickerViewController and final-selection callback | The app can then fetch the entire Contacts database. |
| The selected contact is current | Identifier re-resolution with required keys and store-change handling | A CNContact object remains current forever. |
| Limited contact access can expand | ContactAccessButton/contact access picker in limited/no-access state and approval callback | A custom button can grant Contacts authorization. |
| Contact card is configured correctly | Required-key descriptor, real CNContactViewController, delegate/action dismissal | A visible card authorizes messaging, calling, or saving. |
| Event creation uses the system editor | EKEventEditViewController with eventStore/event/delegate and real completion action | Dismissal means the app knows every final field. |
| Event was saved | EKEventEditViewAction plus source/store reconciliation appropriate to the route | An editor draft or local flag proves Calendar persistence. |
| Event inspection is current | Full-access/source state, current EKEvent, EKEventViewController, and store-change test | An old event object is canonical. |
| Calendar choice is writable | EKCalendarChooser configured for the access level and writable destination, with delegate result | Every calendar title/account is readable or writable. |
| The app uses least privilege | Access matrix, purpose strings, limited/write-only/full paths, and denied/restricted tests | A broad permission is acceptable because it is convenient. |
| AI proposed a safe action | Minimum context, typed proposal, ambiguity/recurrence/time-zone validation, human review, and explicit system handoff | A fluent title or name match is authorized or correct. |
| The route is accessible | VoiceOver, Dynamic Type, Voice Control, Switch Control, keyboard/pointer, localization, reduced-effects task completion | The system UI alone proves app-owned accessibility. |
| Release readiness is proven | Signed target, Info.plist/capability review, physical system-surface run, account/source/access state, and artifact evidence | A simulator fixture or preview proves real Contacts/Calendar behavior. |

## Test matrix

### ContactsUI

- single and multiple contact selection;
- contact-property selection and predicate filtering;
- picker cancellation and dismissal;
- no, limited, denied, restricted, and authorized Contacts status;
- ContactAccessButton query, ignored emails/phone numbers, approval callback, and no-op when fully authorized;
- contact view for existing, new, and unknown contact;
- missing required keys, linked contacts, actions, and editing;
- contact store changed/deleted while a review screen is open;
- long names, localized labels, right-to-left text, VoiceOver, Dynamic Type, and alternate input.

### EventKitUI

- new event editor, existing event editor, delete, save, and cancel;
- write-only/editor-first route with no unnecessary full read access;
- full access and EventKitUI event view;
- read-only and writable calendar chooser;
- calendar/source/account changes and EKEventStoreChanged notifications;
- time zones, daylight-saving transitions, recurrence, invitations, alerts, and default calendar;
- editor completion when the person changes fields in the system UI;
- process/background return and exactly-once dismissal handling;
- accessibility, localization, reduced effects, keyboard, and pointer.

### AI and privacy

- ambiguous person requires a human picker;
- model sees only selected contact/event fields;
- generated proposal is editable and source-labelled;
- current authorization is rechecked before any direct save;
- store/source revision change invalidates stale proposal;
- no private contact notes, event details, or identifiers in logs/notifications;
- manual fallback when model unavailable or output cannot be validated.

## Evidence record

~~~text
target:
sdk:
deployment:
device_or_simulator:
contacts_authorization:
calendar_authorization:
surface:
selection_or_edit_action:
source_store_revision:
ai_proposal:
accessibility_settings:
privacy_review:
signed_artifact:
notes:
~~~

Use controlled test contacts and calendars. Do not place real addresses, calendar invitations, contact notes, or private event content in the repository.

## Sources

- [Contacts UI](https://developer.apple.com/documentation/contactsui)
- [CNContactPickerViewController](https://developer.apple.com/documentation/contactsui/cncontactpickerviewcontroller)
- [CNContactPickerDelegate](https://developer.apple.com/documentation/contactsui/cncontactpickerdelegate)
- [CNContactViewController](https://developer.apple.com/documentation/contactsui/cncontactviewcontroller)
- [CNContactViewControllerDelegate](https://developer.apple.com/documentation/contactsui/cncontactviewcontrollerdelegate)
- [ContactAccessButton](https://developer.apple.com/documentation/contactsui/contactaccessbutton)
- [CNAuthorizationStatusLimited](https://developer.apple.com/documentation/contacts/cnauthorizationstatus/limited)
- [CNContactStore](https://developer.apple.com/documentation/contacts/cncontactstore)
- [EventKit UI](https://developer.apple.com/documentation/eventkitui)
- [EKEventEditViewController](https://developer.apple.com/documentation/eventkitui/ekeventeditviewcontroller)
- [EKEventEditViewDelegate](https://developer.apple.com/documentation/eventkitui/ekeventeditviewdelegate)
- [EKEventViewController](https://developer.apple.com/documentation/eventkitui/ekeventviewcontroller)
- [EKCalendarChooser](https://developer.apple.com/documentation/eventkitui/ekcalendarchooser)
- [Accessing Calendar using EventKit and EventKitUI](https://developer.apple.com/documentation/eventkit/accessing-calendar-using-eventkit-and-eventkitui)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
