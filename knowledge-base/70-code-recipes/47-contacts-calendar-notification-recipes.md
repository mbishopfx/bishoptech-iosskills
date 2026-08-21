# Contacts, EventKit, and notification code recipes

These are compile-oriented route sketches for a selected iOS target. They are not compiled in this documentation-only workspace and do not prove permission scope, store persistence, system-editor behavior, notification delivery, APNs/provider state, accessibility, privacy, or release readiness. Verify current signatures and availability in Xcode.

## Recipe 1: request the smallest Contacts access

Request access at the task boundary and treat limited access as a first-class state:

~~~swift
import Contacts

func requestContactsAccess() async -> Bool {
    let store = CNContactStore()
    do {
        return try await store.requestAccess(for: .contacts)
    } catch {
        return false
    }
}

func contactAccessState() -> CNAuthorizationStatus {
    CNContactStore.authorizationStatus(for: .contacts)
}
~~~

The current SDK may expose different async overload availability. Add NSContactsUsageDescription, explain the task before requesting, and provide a selected-contact/manual fallback for denied or limited access.

## Recipe 2: fetch only the contact keys you need

Contacts I/O should not block the main thread, and fetched contacts can be partial:

~~~swift
import Contacts

func fetchNames(with identifiers: [String]) throws -> [CNContact] {
    let store = CNContactStore()
    let keys: [CNKeyDescriptor] = [
        CNContactGivenNameKey as CNKeyDescriptor,
        CNContactFamilyNameKey as CNKeyDescriptor
    ]
    let predicate = CNContact.predicateForContacts(withIdentifiers: identifiers)
    return try store.unifiedContacts(matching: predicate, keysToFetch: keys)
}
~~~

Run this work away from the main thread in the selected target. Re-fetch after CNContactStoreDidChange. Do not assume an identifier still resolves after deletion or permission narrowing, and do not request phone, email, note, address, or birthday fields unless the task needs them.

## Recipe 3: save a narrowly scoped contact mutation

Make the exact fields visible before execution:

~~~swift
import Contacts

func updateContact(
    _ contact: CNMutableContact,
    in container: CNContainer?
) throws {
    let saveRequest = CNSaveRequest()
    saveRequest.update(contact)
    // Optionally set the target container according to the current product route.
    try CNContactStore().execute(saveRequest)
}
~~~

The store lifetime, authorization, container choice, conflict handling, and exact field mutation need to be implemented in the target. A local success state must wait for the save result and should be followed by a fresh fetch when the UI depends on current system data.

## Recipe 4: request EventKit access by outcome

Use write-only event access for a product that creates events but does not read the calendar, and full access only when the product needs to read/edit/delete:

~~~swift
import EventKit

final class EventStoreOwner {
    let store = EKEventStore()

    func requestWriteAccess(completion: @escaping (Bool) -> Void) {
        store.requestWriteOnlyAccessToEvents { granted, error in
            completion(granted && error == nil)
        }
    }

    func requestFullEventAccess(completion: @escaping (Bool) -> Void) {
        store.requestFullAccessToEvents { granted, error in
            completion(granted && error == nil)
        }
    }

    func requestReminderAccess(completion: @escaping (Bool) -> Void) {
        store.requestFullAccessToReminders { granted, error in
            completion(granted && error == nil)
        }
    }
}
~~~

Keep the event store alive while its EventKit objects are in use. Include the exact calendar/reminder usage descriptions and handle denied/revoked/source/account states. If the task is one event creation, consider the system event editor before requesting broad access.

## Recipe 5: make an event draft explicit

Do not confuse a draft with a saved EventKit record:

~~~swift
struct EventDraft {
    var title: String
    var start: Date
    var end: Date
    var timeZone: TimeZone?
    var calendarIdentifier: String?
    var recurrenceDescription: String?
    var alarmDescription: String?
    var requiresConfirmation: Bool
}

func validate(_ draft: EventDraft) -> [String] {
    var messages: [String] = []
    if draft.title.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
        messages.append("A title is required")
    }
    if draft.end <= draft.start {
        messages.append("End time must be after start time")
    }
    if draft.calendarIdentifier == nil {
        messages.append("Choose a calendar")
    }
    return messages
}
~~~

Before saving, re-resolve the calendar identifier, validate the time zone and recurrence, show the exact fields, and require confirmation. Reconcile from the store after save.

## Recipe 6: use the system event editor

When the product can hand the final edit/save step to the system:

~~~swift
import EventKitUI

func presentEventEditor(
    event: EKEvent,
    from presenter: UIViewController
) {
    let editor = EKEventEditViewController()
    editor.event = event
    // Set the eventStore retained by the owning route.
    // editor.eventStore = retainedEventStore
    presenter.present(editor, animated: true)
}
~~~

The delegate, dismissal, save/cancel result, and UIKit/SwiftUI bridge belong in the selected target. Apple’s EventKit guidance says a product using only the system event editor for creation may not need direct calendar access; verify the current target and policy.

## Recipe 7: schedule a local notification

Request authorization before scheduling and inspect settings:

~~~swift
import UserNotifications

func scheduleReminder(
    identifier: String,
    title: String,
    body: String,
    dateComponents: DateComponents
) async throws {
    let center = UNUserNotificationCenter.current()
    let settings = await center.notificationSettings()
    guard settings.authorizationStatus == .authorized
       || settings.authorizationStatus == .provisional else {
        return
    }

    let content = UNMutableNotificationContent()
    content.title = title
    content.body = body
    content.sound = .default

    let trigger = UNCalendarNotificationTrigger(
        dateMatching: dateComponents,
        repeats: false
    )
    let request = UNNotificationRequest(
        identifier: identifier,
        content: content,
        trigger: trigger
    )
    try await center.add(request)
}
~~~

Verify the current async overloads and authorization status policy. Keep content privacy-reviewed, use stable identifiers for replacement/removal, and do not claim that adding the request proves system delivery or person attention.

## Recipe 8: handle foreground notification presentation

Configure a notification delegate and choose a calm foreground behavior:

~~~swift
import UserNotifications

final class NotificationDelegate: NSObject, UNUserNotificationCenterDelegate {
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification
    ) async -> UNNotificationPresentationOptions {
        // If the person is already viewing this data, update the in-app state
        // rather than duplicating a distracting banner.
        return []
    }

    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse
    ) async {
        // Resolve the request identifier and action, then validate the domain
        // mutation before changing app state.
        _ = response
    }
}
~~~

Set the delegate during app startup according to the target lifecycle. Test foreground, background, terminated, action, denial, settings changes, and sensitive-content redaction.

## Recipe 9: turn selected text into an AI event proposal

Keep generated fields typed and reviewable:

~~~swift
struct EventProposal: Sendable {
    var title: String
    var start: Date?
    var end: Date?
    var timeZoneIdentifier: String?
    var calendarIdentifier: String?
    var missingFields: [String]
    var explanation: String
    var requiresConfirmation: Bool
}

func canApply(
    _ proposal: EventProposal,
    currentCalendarIdentifier: String?,
    hasFullAccess: Bool
) -> Bool {
    proposal.requiresConfirmation
        && proposal.missingFields.isEmpty
        && hasFullAccess
        && proposal.calendarIdentifier == currentCalendarIdentifier
}
~~~

For a write-only route, the proposal can target the system event editor rather than a direct save. For a full-access route, re-resolve current store state immediately before mutation. The model is not allowed to send, save, schedule, or change a contact by itself.

## Recipe 10: fixture the permission and delivery state

Use fixtures to drive the same state reducer used by the UI:

~~~swift
enum PersonalDataFixture {
    case contactsLimited
    case contactsDenied
    case contactDeleted
    case eventWriteOnly
    case eventFullAccess
    case eventStoreChanged
    case notificationDenied
    case notificationScheduled
    case settingsChanged
    case aiAmbiguous
}

func reduce(_ fixture: PersonalDataFixture) -> PersonalDataRouteState {
    fatalError("Implement in the selected app target")
}
~~~

Exercise limited access, deleted identifiers, calendar time zones, recurrence, reminders, notification privacy, foreground action handling, stale AI proposals, and manual fallbacks before relying on a physical system run.

## Sources

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
- [Requesting authorization](https://developer.apple.com/documentation/usernotifications/unusernotificationcenter/requestauthorization%28options%3Acompletionhandler%3A%29)
- [UNNotificationSettings](https://developer.apple.com/documentation/usernotifications/unnotificationsettings)
- [UNNotificationRequest](https://developer.apple.com/documentation/usernotifications/unnotificationrequest)
- [UNMutableNotificationContent](https://developer.apple.com/documentation/usernotifications/unmutablenotificationcontent)
- [UNCalendarNotificationTrigger](https://developer.apple.com/documentation/usernotifications/uncalendarnotificationtrigger)
- [Notifications HIG](https://developer.apple.com/design/human-interface-guidelines/notifications/)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
