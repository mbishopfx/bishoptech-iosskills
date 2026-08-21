# ContactsUI and EventKitUI native editor route

Use this route when the user needs to choose a contact, reveal limited contact access, display a contact card, create/edit an event, inspect an event, or choose a calendar through Apple-owned UI.

## Route selection

| Outcome | Start here |
| --- | --- |
| One-time contact selection | CNContactPickerViewController |
| Contact-property selection | Contact picker with property-selection delegate |
| Existing/new/unknown contact card | CNContactViewController |
| Expand limited contact access | ContactAccessButton or contact access picker |
| Create or edit a calendar event | EKEventEditViewController |
| Display an existing event/reminder | EKEventViewController |
| Choose a writable calendar | EKCalendarChooser |
| Bulk search, aggregation, or direct mutation | Contacts/CNContactStore or EventKit/EKEventStore with exact access |

## Contact selection route

~~~text
app task
  -> explain why a contact is needed
  -> configure picker predicates/property keys
  -> present CNContactPickerViewController
  -> receive contact/property selection
  -> create a minimal app-owned projection
  -> explicit next action
~~~

The picker can return a final selection without broad Contacts authorization. Keep the result in a task-scoped model. If the app later needs more fields, request or resolve only those fields under the current authorization and re-check the contact identifier.

Use selection predicates to prevent irrelevant contacts/properties from being selectable. Configure them before presentation; do not expect a predicate change after the picker is onscreen to change the current selection behavior.

## Limited-access route

~~~text
search text
  -> ContactAccessButton
  -> person approves one or more contacts
  -> receive approved identifiers
  -> refetch minimum keys
  -> update visible task
~~~

Show the control only when limited/no access makes it useful. Keep a manual path. After approval, refresh the contact projection and handle the case where the user grants a different set than the app expected.

## Contact card route

Prepare CNContactViewController with the exact contact and required keys. Configure whether editing, actions, linked contacts, and property display are appropriate. Treat actions such as messaging or calling as explicit system handoffs. The fact that a contact card displays a phone number does not authorize the app to send a message without the user’s next choice.

## Event creation route

~~~text
EventDraft
  -> title/date/time-zone/duration/recurrence validation
  -> create EKEvent in an EKEventStore
  -> configure EKEventEditViewController
  -> person reviews/edits/calendar choice
  -> EKEventEditViewDelegate action
  -> app records local action result
~~~

The system editor is the privacy-first route for creating an event when the app does not need to read the person’s calendar. Do not inspect the dismissed controller and assume it contains the final event the person saved; the documented editor can render and save out of process.

If the app needs to choose a calendar before direct save, use EKCalendarChooser with the access level and writable-only display appropriate to the target. If it needs to read existing events, request the separate full event access and use EKEventViewController or a direct EventKit query according to the product need.

## Event inspection route

Pass a current EKEvent to EKEventViewController. Decide whether allowsEditing and allowsCalendarPreview are appropriate. On close, reconcile the source event/store rather than treating dismissal as confirmation. If the event was deleted or changed elsewhere, invalidate stale app-owned details.

## AI proposal route

~~~text
selected text/contact/task
  -> minimum authorized context
  -> ContactSelection or EventDraft
  -> deterministic validation
  -> review sheet
  -> system picker/editor/chooser
  -> result and reconciliation
~~~

Require explicit contact choice when names are ambiguous. Require explicit calendar choice when more than one writable destination is plausible. Validate time zone and recurrence in deterministic code. Keep generated copy, selected contact identifiers, and canonical system records in separate types.

## Failure states

| Failure | Preserve and offer |
| --- | --- |
| Picker cancelled | Original task and manual selection |
| Contact access limited/denied | ContactAccessButton, picker, or manual entry |
| Contact changed/deleted | Reselect/refetch by identifier |
| Event editor cancelled | EventDraft for edit/retry |
| Event action failed/unknown | Local status and refresh path; no saved claim |
| Calendar unavailable | Writable destination refresh or default-editor route |
| Store changed | Reconcile and mark draft stale |
| AI unavailable | Manual contact/event fields |

## Proof gates

Compile the wrappers in a named target and test real ContactsUI/EventKitUI surfaces on supported devices. Record access level, system result, source/store changes, accessibility settings, and signed target configuration. A simulator contact or calendar fixture does not prove the person’s real system data, account sources, or system editor behavior.

## Sources

- [Contacts UI](https://developer.apple.com/documentation/contactsui)
- [CNContactPickerViewController](https://developer.apple.com/documentation/contactsui/cncontactpickerviewcontroller)
- [CNContactPickerDelegate](https://developer.apple.com/documentation/contactsui/cncontactpickerdelegate)
- [CNContactViewController](https://developer.apple.com/documentation/contactsui/cncontactviewcontroller)
- [ContactAccessButton](https://developer.apple.com/documentation/contactsui/contactaccessbutton)
- [CNContactStore](https://developer.apple.com/documentation/contacts/cncontactstore)
- [EventKit UI](https://developer.apple.com/documentation/eventkitui)
- [EKEventEditViewController](https://developer.apple.com/documentation/eventkitui/ekeventeditviewcontroller)
- [EKEventEditViewDelegate](https://developer.apple.com/documentation/eventkitui/ekeventeditviewdelegate)
- [EKEventViewController](https://developer.apple.com/documentation/eventkitui/ekeventviewcontroller)
- [EKCalendarChooser](https://developer.apple.com/documentation/eventkitui/ekcalendarchooser)
- [Accessing Calendar using EventKit and EventKitUI](https://developer.apple.com/documentation/eventkit/accessing-calendar-using-eventkit-and-eventkitui)
- [UIViewControllerRepresentable](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable)
