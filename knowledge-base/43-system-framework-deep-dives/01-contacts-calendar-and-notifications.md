# Contacts, Calendar, Reminders, and Notifications

## Capability boundary

Contacts, EventKit, and User Notifications integrate an app with sensitive user records and attention-grabbing system surfaces. They are not one generic “personal data” permission:

| User outcome | Framework route | Boundary |
| --- | --- | --- |
| Let someone choose one person | ContactsUI picker/access button | User-mediated selection; avoid reading the full contact store. |
| Search or sync contacts | Contacts/CNContactStore | `NSContactsUsageDescription`, keys-to-fetch, partial records, change notification, retention. |
| Create a calendar event | EventKit write-only access or EventKit UI | Calendar/time-zone/account choice, confirmation, duplicate/idempotency. |
| Read/edit calendar or reminders | EventKit full access | Stronger permission, external changes, account/store state, privacy. |
| Remind someone locally | UserNotifications | Notification permission/settings, content privacy, deterministic identifiers, no delivery guarantee. |
| Receive remote notification | UserNotifications plus APNs/server | Token/server/authentication and delivery uncertainty, separate from local scheduling. |

Keep external-store records at a service boundary and convert them into app-owned, minimal models. A contact identifier, event identifier, calendar title, reminder, or notification payload can be personal data; do not put them in logs, analytics, URLs, or AI prompts by default.

## Contacts route

### Prefer a user-mediated picker

If the feature needs one contact, prefer a system picker/access button so the person chooses the record and the app does not need broad store access. If the product genuinely searches or syncs contacts, request access at the feature boundary, fetch only the keys needed, and run synchronous store I/O off the main thread.

Contacts can be partial. A `CNContact` fetched with only a subset of keys is not a complete person record. If the app caches contact objects, observe `CNContactStoreDidChange`, refetch the required keys, and release the old cache. Do not treat a missing field as proof that the person has no value or that access was complete.

### Authorization and change state

Use `CNContactStore.authorizationStatus(for:)` and the request result to drive a state machine:

`notDetermined -> requesting -> authorized|limited|denied|restricted -> fetching -> ready|empty|stale|failed`

Preserve the person’s search/entry text when access is denied or a record disappears. Provide manual entry or a user-mediated picker when it satisfies the workflow. Never silently upload the entire store for matching or enrichment.

## Calendar and reminders route

### Match access to the operation

On current iOS, EventKit distinguishes write-only event access from full event access; reading events requires full access. Reading or writing reminders uses the reminders access route. Do not request full access when the feature only creates a new event, and use EventKit UI when its system-provided create/edit surface meets the product need.

Include the current usage-description keys for the requested access level. Older calendar usage keys are not a substitute for the current target’s required declarations. Confirm the selected calendar/account, time zone, recurrence, alarms, and event content before saving.

### Draft before save

Represent event/reminder creation as an app-owned draft:

`idea -> draft -> person reviews title/time/calendar -> saving -> saved|failed`

A draft is not a saved event. Use a stable app operation identifier in the product’s local state to avoid duplicate saves after a retry, but do not assume an EventKit object’s identifier alone provides idempotency across every account/store change. Refresh after external edits and handle `EKEventStoreChanged`/store invalidation according to the target API.

Never create or edit a calendar item from an inferred AI result, notification tap, or background callback without the product’s confirmation rule. State clearly whether a save changes the person’s calendar/reminders and how they can undo it.

## Notifications route

### Permission and settings

Use `UNUserNotificationCenter` as the app’s notification boundary. Assign a `UNUserNotificationCenterDelegate` before app launch finishes if the app needs foreground presentation or action handling. Request only the interaction options the product uses, and inspect notification settings after the request and whenever the app returns to the foreground.

`requestAuthorization` returning `true` means at least one requested option was granted; it does not guarantee alerts, sounds, badges, actions, provisional behavior, Focus delivery, or lock-screen visibility. A notification is attention, not guaranteed delivery. Keep the in-app state authoritative and route a tap through validated typed navigation.

### Local versus remote

Local notifications use a content object, trigger, and stable request identifier; they do not require a server. Remote notifications add APNs tokens, server authentication, provider outages, payload limits, delivery timing, and user settings. Do not make the local scheduling path depend on a remote push unless the product truly needs remote events.

Use deterministic identifiers and a scheduling policy so repeated app launches do not create duplicate reminders. Remove or replace obsolete requests when the underlying task is completed or changed. Do not put private health/contact/calendar details in a lock-screen notification unless the person-facing privacy choice supports it.

## Background and system-surface boundary

Notification delivery, EventKit change observation, HealthKit background delivery, WidgetKit refresh, ActivityKit updates, and BackgroundTasks are separate system contracts. A scheduled notification does not grant background execution, and a background callback is not a guaranteed schedule. Persist state before requesting deferred work, make handlers idempotent, and exit safely if the system stops the process.

If a notification opens a screen, validate the record ID, ownership, current permissions, and current domain state before displaying it. A stale/deleted event or contact must land on a safe empty/error route rather than a fabricated detail screen.

## API, target, and permission matrix

Select the least-privileged system route that completes the user outcome. Contacts, EventKit, and User Notifications each have different authorization and delivery semantics.

| Outcome | API route | Domain handoff | Target/configuration/proof gate |
| --- | --- | --- | --- |
| Choose one contact | ContactsUI picker/access button | User-selected contact ID/allowed fields | User-mediated scope, cancellation, partial fields, and physical system picker. |
| Search or sync contacts | `CNContactStore`, `CNContactFetchRequest`, change-history route | Minimal keys, contact ID, source/change token, fetched-at | `NSContactsUsageDescription`, authorization/revocation, partial contacts, change notification/history, background queue, and privacy review. |
| Create an event | EventKit write-only route or `EKEventEditViewController` | Reviewed event draft, calendar/account, time zone, operation ID | Current calendar usage description, user confirmation, duplicate retry, account/calendar change, and saved-event proof. |
| Read/edit events | EventKit full event access and `EKEventStore` | Minimal event fields, external ID, last-known/change state | Full-access usage description, denied/limited/revoked, external edits, recurrence/DST, and device/system UI. |
| Read/edit reminders | EventKit reminders route/UI | Reviewed reminder draft, list/account, operation ID | `NSRemindersFullAccessUsageDescription`, authorization/store changes, duplicate prevention, and user confirmation. |
| Schedule local attention | `UNUserNotificationCenter` + `UNNotificationRequest`/trigger | Stable request ID, content privacy, schedule/cancel state | Notification authorization/settings, trigger behavior, replacement/cancel, lock screen/Focus, and physical device. |
| Receive remote event | `registerForRemoteNotifications` + APNs/provider | Device-token/account association, server payload, deep-link ID | Push entitlement/provider authentication, token refresh, server delivery logs, settings, and real-device release configuration. |
| User action from notification | Notification category/actions + validated deep link | Typed action and stable entity ID | Terminated/locked app, stale/deleted entity, authorization/account check, and safe fallback. |

## External-store and attention state machine

Use separate state machines instead of a single `permissionGranted` flag:

`notDetermined -> requesting -> authorized|limited|denied|restricted -> fetching|drafting -> ready|empty|stale|failed`

For notifications:

`notRequested -> requesting -> settingsKnown -> localScheduled|remoteRegistered -> delivered|interacted|expired|cancelled|unknown`

For every write to Contacts, EventKit, or a notification schedule, retain a local operation ID and a user-visible draft/result. If the process dies after the external store accepts a write but before the app records success, reconcile by querying the external store or presenting a review route; do not blindly duplicate the operation.

APNs device tokens are environment/device/app-specific and can change. Register each launch, forward the current token securely to the provider, and handle token/account unlinking. A server response or scheduled request proves only that the request was accepted by that layer, not that the user saw or acted on the notification.

## Privacy and retention

- Fetch only the contact keys, calendar fields, reminder fields, health types, and notification content needed for the feature.
- Keep external-store identifiers and raw values out of logs/analytics; redact or aggregate telemetry.
- Preserve user-entered text locally when permission is denied, and do not silently retry a protected-store request in a loop.
- Explain whether an action reads, creates, edits, or deletes an external record and how to revoke/delete app-owned copies.
- Avoid sending contact, calendar, reminder, or health data to a remote service or tool without an explicit product need, consent/data boundary, and retention policy.

## Verification route

- Contacts: picker versus full-store route, first request, allow/deny/limited/revoked, partial keys, duplicates, deleted records, `CNContactStoreDidChange`, background fetch queue, and redacted logs.
- Calendar/reminders: write-only versus full access, current usage descriptions, denied/revoked, calendar/account changes, time zones/DST, recurrence, duplicate retry, EventKit UI, external edits, and deletion/undo.
- Notifications: delegate timing, authorization options, provisional/settings changes, local scheduling/cancel/replace, foreground/background/terminated/relaunch, actions/deep links, stale content, Focus/lock screen, and accessibility.
- System surfaces: background execution, widget/Live Activity/notification handoff, idempotency, process termination, and physical device behavior.
- Privacy: privacy manifests/labels, content redaction, retention/deletion, export, analytics instrumentation, and user-facing permission copy.

Previews and unit fixtures can validate drafts, state machines, and typed navigation. They do not prove privacy prompts, external account stores, notification presentation, delivery timing, HealthKit background behavior, or system-owned UI on a device.

## Sources

- [Contacts](https://developer.apple.com/documentation/contacts)
- [CNContactStore](https://developer.apple.com/documentation/contacts/cncontactstore)
- [CNContactFetchRequest](https://developer.apple.com/documentation/contacts/cncontactfetchrequest)
- [CNContactStoreDidChange](https://developer.apple.com/documentation/foundation/nsnotification/name-swift.struct/cncontactstoredidchange)
- [ContactsUI](https://developer.apple.com/documentation/contactsui)
- [EventKit](https://developer.apple.com/documentation/eventkit)
- [Accessing the event store](https://developer.apple.com/documentation/eventkit/accessing-the-event-store)
- [EKEventStore](https://developer.apple.com/documentation/eventkit/ekeventstore)
- [EKEventEditViewController](https://developer.apple.com/documentation/eventkitui/ekeventeditviewcontroller)
- [User Notifications](https://developer.apple.com/documentation/usernotifications)
- [Asking permission to use notifications](https://developer.apple.com/documentation/usernotifications/asking-permission-to-use-notifications)
- [UNUserNotificationCenter](https://developer.apple.com/documentation/usernotifications/unusernotificationcenter)
- [UNUserNotificationCenterDelegate](https://developer.apple.com/documentation/usernotifications/unusernotificationcenterdelegate)
- [UNNotificationRequest](https://developer.apple.com/documentation/usernotifications/unnotificationrequest)
- [Registering your app with APNs](https://developer.apple.com/documentation/usernotifications/registering-your-app-with-apns)
- [Human Interface Guidelines: Notifications](https://developer.apple.com/design/human-interface-guidelines/notifications)
- [HealthKit](https://developer.apple.com/documentation/healthkit)
- [BackgroundTasks](https://developer.apple.com/documentation/backgroundtasks)
