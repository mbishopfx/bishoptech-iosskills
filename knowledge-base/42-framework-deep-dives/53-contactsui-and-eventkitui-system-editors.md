# ContactsUI and EventKitUI system editors

ContactsUI and EventKitUI are system-owned interaction routes for personal data. They can reduce the amount of raw contact or calendar data an app needs to access, but they do not remove the need for explicit intent, accurate state, privacy copy, or reconciliation.

Use the route that matches the user’s outcome:

~~~text
user intent
  -> narrow system picker/editor
  -> selected or edited system object
  -> app-owned projection
  -> optional AI proposal
  -> deterministic validation and confirmation
  -> system or app-owned mutation
~~~

## ContactsUI route map

| User outcome | API | Access boundary |
| --- | --- | --- |
| Let a person choose one or more contacts | CNContactPickerViewController | The picker can return only the person’s final selection without requiring broad Contacts access. |
| Let a person choose a contact property | CNContactPickerViewController delegate property-selection callbacks | The app receives the selected property, not an unrestricted contact database. |
| Display an existing/new/unknown contact card | CNContactViewController | The contact and required keys must be prepared correctly; the system card owns the presentation. |
| Let a person add contacts under limited access | ContactAccessButton or contact access picker route | The person expands the app’s allowed set; the app should not simulate this with a custom contact list. |
| Fetch/search many contacts | CNContactStore | Requires the appropriate Contacts authorization, keysToFetch discipline, background I/O, and change reconciliation. |

### CNContactPickerViewController

The contact picker supports single or multiple contact selection and contact-property selection. Configure selection predicates and displayed property keys before presenting. Delegate callbacks tell the app what the person selected or that the picker was cancelled.

The picker is a strong default when the feature needs one person for an action such as:

- choosing a recipient for a reviewed message;
- selecting a person for a local reminder or note;
- attaching a contact identity to a user-created record;
- choosing a single contact for a call or system handoff.

The picker is not a bulk-import shortcut. Do not treat a selected contact as permission to fetch every field, or as proof that the person’s phone number/email is current. Retain only the fields needed for the confirmed task and re-resolve an identifier before a later mutation.

### CNContactViewController

Use CNContactViewController to display a new, unknown, or existing contact. Use descriptorForRequiredKeys when preparing an existing contact so the view controller has the keys it needs. Configure allowsEditing, allowsActions, shouldShowLinkedContacts, displayedPropertyKeys, alternateName, and message intentionally.

The contact view controller’s delegate can observe selected properties and completion/dismissal. A selected phone number or email is user intent for that particular action, not a general authorization to send, save, or disclose other contact fields.

### ContactAccessButton

ContactAccessButton is a SwiftUI button for expanding the set of contacts exposed to an app under limited access. It works with a search UI and can show a matching contact or navigate to a selection view. When the app is already authorized, the button does not appear; when access is denied or limited, it can guide the person through adding access.

This control is materially different from a custom button labeled “Allow contacts.” The system owns the access decision and returns approved contact identifiers. The app must refresh its own contact projections after approval and still fetch only the required keys.

## EventKitUI route map

| User outcome | API | Access boundary |
| --- | --- | --- |
| Create/edit/delete a calendar event with Apple’s editor | EKEventEditViewController | The system editor owns interaction and can save through the selected/default calendar; app result is the edit action, not a full event read-back. |
| Display an existing event/reminder | EKEventViewController | The app needs the event object and appropriate read access; the view controller can optionally allow editing. |
| Choose a calendar for a write | EKCalendarChooser | Requires the appropriate write-only or full calendar access; writable-only display is useful for least privilege. |
| Read/search all calendar events | EKEventStore | Requires full access to events and purpose strings; use only when system UI is insufficient. |
| Create an event without reading the calendar | EKEventEditViewController | Prefer the user-mediated editor route when it satisfies the outcome; do not request broad access merely to create one event. |

### EKEventEditViewController

Configure eventStore, event, and editViewDelegate before presenting. The person can add, edit, or delete an event in Apple’s editor. EKEventEditViewDelegate reports the action when the editing session ends. Dismiss the controller in the delegate path.

The editor is important for privacy: a write-only or editor-first feature can let the person choose a calendar in a system-owned surface without the app reading all calendar contents. The app should not inspect the dismissed controller and claim to know every final field the person changed. The documented system-editor route performs the final save out of process; record the action and reconcile later if the product needs a local projection.

### EKEventViewController

Use EKEventViewController to present existing events or reminders. Set allowsEditing only when the product genuinely wants to let the person change the event in that surface. Set allowsCalendarPreview deliberately for invitations or organizer previews. Its delegate reports closing; closing is not proof that the event was accepted, edited, or saved.

### EKCalendarChooser

EKCalendarChooser lets a person select one or more calendars and can display all calendars or only writable calendars. The selected calendars are a user choice and should be treated as a destination projection, not as a guarantee that the calendar remains available. Use EKCalendarChooserDelegate to handle selection and cancellation. Refresh state if the EventKit store changes or access narrows.

In a write-only route, the documented chooser behavior limits selection to writable calendars even if a broader display style was requested. Do not build a custom calendar list that exposes calendar titles or accounts the app is not authorized to read.

## Permissions and system-owned UI

Separate these states:

~~~text
Contacts picker selection
  != ContactsStore authorization

Event editor completion
  != full calendar read access

Calendar chooser selection
  != durable calendar identity

Contact/event draft
  != saved canonical record
~~~

For ContactsStore and direct EventKit reads/writes, use the current authorization APIs, narrow usage descriptions, and exact Info.plist keys for the target SDK. For system picker/editor routes, verify the current Apple documentation because system UI may intentionally reduce the app’s direct data access.

Keep access state and system-surface state separate from app-owned status. If the person changes Contacts or Calendar access in Settings, invalidate stale projections and offer a reselect/refresh path.

## AI and personal-data actions

AI can assist with:

- turning selected text into an EventDraft;
- identifying missing event time zone, duration, or calendar destination;
- summarizing a user-selected contact using only selected keys;
- suggesting a reminder title from a selected task;
- finding ambiguous names before a human chooses a contact.

AI must not:

- infer a recipient from an ambiguous name and open a sender;
- read a full contact book to choose one person when a picker suffices;
- write a contact or event without explicit confirmation;
- treat a contact identifier as account identity;
- silently invite people, modify recurrence, or change a calendar destination;
- expose private event/contact fields in a notification, preview, or Liquid Glass card.

Use typed proposals such as ContactSelection, ContactDraft, EventDraft, CalendarDestination, and ReminderDraft. Validate identifiers, permissions, time zones, recurrence, date arithmetic, contact properties, and current store state deterministically. If the source store changes while a review sheet is open, mark the proposal stale and re-resolve it.

## Native design and accessibility

Keep system pickers and editors visibly system-owned. An app-owned Liquid Glass review card can show the task, selected fields, proposed event details, or destination calendar before the system handoff. Do not rebuild Contact Card or Calendar Editor UI just to match a visual mockup.

Use semantic labels for:

- contact name and selected property;
- event title, time zone, duration, recurrence, and destination calendar;
- limited-access state and the system control that expands it;
- save, cancel, delete, retry, stale, and unavailable outcomes.

Test VoiceOver, Dynamic Type, right-to-left names, long event titles, localized dates/time zones, Voice Control, Switch Control, keyboard/pointer input, reduced motion, reduced transparency, and high contrast. A system editor closing or a contact picker returning does not replace an accessible app-owned confirmation state.

## Lifecycle and fallback states

| State | Fallback |
| --- | --- |
| Contacts access limited | Use ContactAccessButton, contact picker, selected fields, or manual entry. |
| Contacts access denied/restricted | Preserve the task and provide manual/user-mediated selection. |
| Contact disappeared/changed | Refetch by identifier; invalidate if the identity cannot be resolved. |
| Event editor unavailable/fails | Preserve EventDraft and offer manual/export instructions. |
| Calendar access narrowed | Refresh writable destinations and remove stale choices. |
| Event store changed | Reconcile the visible projection and invalidate stale edits. |
| User cancels picker/editor | Keep the app-owned draft; do not report a saved mutation. |
| AI unavailable/ambiguous | Manual fields and deterministic validation. |

## Evidence checklist

- exact ContactsUI and EventKitUI APIs compiled in the named target;
- picker/editor/chooser presentation and delegate dismissal;
- limited, denied, restricted, write-only, full, and changed-access states;
- out-of-process EventKit editor result semantics;
- source/store-change and stale-proposal behavior;
- privacy-minimized contact/event fields and logs;
- AI typed proposal, confirmation, and refusal cases;
- accessibility and localization task completion;
- physical system-surface and signed target/release evidence.

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
- [UIViewControllerRepresentable](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
