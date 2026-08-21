# Contacts, EventKit, and User Notifications proof matrix

This matrix keeps personal-data access, system editing, local scheduling, APNs delivery, AI proposals, and privacy claims separate. A permission prompt, a saved draft, or a notification request does not prove the data was available, the mutation was accepted, or the person saw a notification.

## Evidence levels

| Level | Evidence | What it proves |
| --- | --- | --- |
| L0 | Official source, privacy, and route review | The API, permission scope, system surface, and HIG boundary are documented. |
| L1 | Deterministic state/fixture tests | Permission reducers, partial data, draft validation, trigger construction, privacy redaction, and stale invalidation. |
| L2 | Preview/simulator/UI fixture | Screen hierarchy, editable review, accessibility identifiers, fallback copy, and foreground state. |
| L3 | Signed physical-device/system run | Contacts/EventKit authorization, system picker/editor, store changes, notification settings, and device presentation. |
| L4 | Provider/APNs or account environment | Remote registration/provider payload, token/environment, delivery/action path, and account/source behavior. |
| L5 | Release artifact | Usage strings, entitlements, privacy declarations, extension configuration, signing, TestFlight/App Store metadata, and release build. |

## Permission and data scope

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Contact access works | Signed target, usage description, not-determined/limited/full/denied/restricted runs | Permission does not imply every contact or field is available. |
| Contact picker works | User-mediated picker/access button, selected identifiers, cancelled flow | A selected contact does not grant broad address-book access. |
| Minimal contact fetch works | keysToFetch/predicate fixture, background I/O, partial object handling | A full-name preview does not prove email/phone/note access. |
| Contact cache stays fresh | CNContactStoreDidChange and deleted/changed identifier tests | Cached objects can be stale and must be refetched. |
| Contact write works | CNSaveRequest valid/invalid/conflict/denied tests | A local mutation flag is not proof of store persistence. |
| Notes/private fields work | Exact entitlement and target artifact if required | General Contacts access does not prove sensitive field access. |

## EventKit access

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Create one event | System event editor save/cancel result, destination calendar | A draft is not saved until the system route confirms it. |
| Write-only calendar route | requestWriteOnlyAccessToEvents, creation, denied, revoked, and no-read fixture | Write-only access cannot be used to read calendar data. |
| Full event route | Full access allow/deny, read/edit/delete, time zone/recurrence/calendar source cases | Full access has broader privacy and account/source failure states. |
| Reminder route | Full reminders authorization, list/source, save/delete/recurrence, store change | A reminder request is not proof it is visible in the person’s chosen account. |
| Event store freshness | EKEventStoreChangedNotification and re-fetch | Existing objects can be invalid after store changes. |
| Account/source state | Multiple calendars/lists, unavailable source, account change, time zone change | One local calendar does not represent every account configuration. |

## Notification scheduling and delivery

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Request authorization works | Requested options, allow/deny, settings inspection, Settings change | A true response does not mean every option remains enabled. |
| Local notification scheduled | Content/trigger/request ID, add completion, pending-request inspection | Scheduling does not prove exact delivery time or presentation. |
| Notification privacy is safe | Lock Screen/Notification Center content review, redaction fixtures | A notification is a public-at-display surface. |
| Foreground behavior works | UNUserNotificationCenterDelegate foreground path | A delivered payload does not prove the desired in-app experience. |
| Action works | Category/action registration, action response, app state/extension state | An action identifier is not a completed domain mutation. |
| Remote delivery works | APNs token/environment, provider payload, server logs, device/system presentation | Registration does not prove provider delivery, and provider delivery does not prove the person saw it. |
| CarPlay/paired surfaces work | Current settings and supported system-surface run | iPhone Notification Center evidence does not prove CarPlay/Watch presentation. |

## AI proposal route

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| AI parses an event | Fixed text fixtures, typed decode, date/time-zone validation, uncertainty | Generated fields are still a draft. |
| AI selects a contact | Limited selected context, identifier resolution, duplicate/unknown tests | Name similarity is not identity proof. |
| AI suggests a notification | Privacy redaction, settings-aware rewrite, edit/reject route | AI cannot guarantee delivery or permission. |
| AI saves/schedules safely | Explicit confirmation, current access, stale invalidation, completion reconciliation | Model output cannot silently mutate system stores. |
| AI privacy is bounded | Prompt/context audit, retention/deletion/log review | On-device execution does not eliminate sensitive-data design work. |

## Design and accessibility

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Native review surface | HIG review, system picker/editor where appropriate, adaptive Liquid Glass states | A glass card does not replace the system-owned permission/editor. |
| VoiceOver task completion | Select, review, edit, save/schedule, failure, and retry with VoiceOver | Labels alone do not prove an accessible task. |
| Dynamic Type/localization | Long names/titles, calendar formats, time zones, recurrence, RTL, largest text | Default locale/default text-size screenshots are insufficient. |
| Privacy copy is useful | Pre-permission explanation and post-denial/limited paths | A purpose string alone does not explain the product task. |
| Foreground notification is calm | App-open delivery and no-duplicate UI test | Repeating a banner over a visible in-app update is distracting. |

## Evidence packet

Record:

~~~text
feature:
target/bundle/build:
sdk/deployment target:
device/OS:
framework and route:
usage description:
permission state:
contact/event/reminder/notification fixture:
draft/proposal:
store/settings state:
system surface:
provider/APNs environment:
accessibility settings:
privacy/redaction review:
known failures:
claim supported:
~~~

## Claim language

Use:

- “The signed target fetched only the selected contact keys after limited access and refetched after the contact store changed.”
- “The event was created through the system editor on the named device; cancellation left the draft unsaved.”
- “The local notification request was accepted with the named trigger and content; delivery was tested separately.”
- “The AI produced an editable event draft from selected text and required confirmation before EventKit mutation.”

Avoid:

- “The app has the user’s contacts” when access is limited.
- “Calendar sync is complete” after saving one event.
- “The notification was delivered” from a scheduled request.
- “AI scheduled it” when the model only generated a draft.

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
- [Notifications HIG](https://developer.apple.com/design/human-interface-guidelines/notifications/)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
