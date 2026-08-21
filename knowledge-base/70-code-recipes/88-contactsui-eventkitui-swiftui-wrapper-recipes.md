# ContactsUI and EventKitUI SwiftUI wrapper recipes

These snippets are compile-oriented route sketches for bringing UIKit-owned ContactsUI and EventKitUI surfaces into SwiftUI. Confirm the current signatures in the selected SDK and test the real permission/system state before shipping.

## ContactsUI picker wrapper

~~~swift
import Contacts
import ContactsUI
import SwiftUI

struct ContactPicker: UIViewControllerRepresentable {
    let onSelection: ([CNContact]) -> Void
    let onCancel: () -> Void

    func makeCoordinator() -> Coordinator {
        Coordinator(onSelection: onSelection, onCancel: onCancel)
    }

    func makeUIViewController(
        context: Context
    ) -> CNContactPickerViewController {
        let controller = CNContactPickerViewController()
        controller.delegate = context.coordinator
        controller.displayedPropertyKeys = [
            CNContactGivenNameKey,
            CNContactFamilyNameKey,
            CNContactEmailAddressesKey,
            CNContactPhoneNumbersKey
        ]
        return controller
    }

    func updateUIViewController(
        _ controller: CNContactPickerViewController,
        context: Context
    ) {
        // Configure predicates before presentation.
    }

    final class Coordinator: NSObject, CNContactPickerDelegate {
        let onSelection: ([CNContact]) -> Void
        let onCancel: () -> Void

        init(
            onSelection: @escaping ([CNContact]) -> Void,
            onCancel: @escaping () -> Void
        ) {
            self.onSelection = onSelection
            self.onCancel = onCancel
        }

        func contactPicker(
            _ picker: CNContactPickerViewController,
            didSelect contacts: [CNContact]
        ) {
            onSelection(contacts)
        }

        func contactPickerDidCancel(
            _ picker: CNContactPickerViewController
        ) {
            onCancel()
        }
    }
}
~~~

The picker’s final selection is task-scoped. Do not copy every returned field into a database or assume that the picker grants broad Contacts access.

## Limited contact access in SwiftUI

~~~swift
import Contacts
import ContactsUI
import SwiftUI

struct LimitedContactAccessView: View {
    let query: String
    let ignoredEmails: Set<String>
    let ignoredPhoneNumbers: Set<String>
    let onApproved: ([String]) -> Void

    var body: some View {
        ContactAccessButton(
            queryString: query,
            ignoredEmails: ignoredEmails,
            ignoredPhoneNumbers: ignoredPhoneNumbers,
            approvalCallback: onApproved
        )
        .contactAccessButtonCaption(.defaultText)
        .contactAccessButtonStyle(.automatic)
    }
}
~~~

Show this route according to CNContactStore.authorizationStatus(for:), not as a generic replacement for the contact picker. Refresh the visible contact model after the approval callback.

## Event editor wrapper

~~~swift
import EventKit
import EventKitUI
import SwiftUI

struct EventEditor: UIViewControllerRepresentable {
    typealias UIViewControllerType = EKEventEditViewController

    let eventStore: EKEventStore
    let event: EKEvent
    let onComplete: (EKEventEditViewAction) -> Void

    func makeCoordinator() -> Coordinator {
        Coordinator(onComplete: onComplete)
    }

    func makeUIViewController(
        context: Context
    ) -> EKEventEditViewController {
        let controller = EKEventEditViewController()
        controller.eventStore = eventStore
        controller.event = event
        controller.editViewDelegate = context.coordinator
        return controller
    }

    func updateUIViewController(
        _ controller: EKEventEditViewController,
        context: Context
    ) {
        // Create and validate the event snapshot before presentation.
    }

    final class Coordinator: NSObject, EKEventEditViewDelegate {
        let onComplete: (EKEventEditViewAction) -> Void

        init(
            onComplete: @escaping (EKEventEditViewAction) -> Void
        ) {
            self.onComplete = onComplete
        }

        func eventEditViewController(
            _ controller: EKEventEditViewController,
            didCompleteWith action: EKEventEditViewAction
        ) {
            controller.dismiss(animated: true) {
                self.onComplete(action)
            }
        }
    }
}
~~~

The completion action is a local system-editor result. If the app needs to know the final saved fields, use a documented EventKit read/reconciliation route with the appropriate access; do not inspect a dismissed editor controller and assume it reflects every change made out of process.

## Calendar chooser wrapper

~~~swift
import EventKit
import EventKitUI
import SwiftUI

struct CalendarChooser: UIViewControllerRepresentable {
    let eventStore: EKEventStore
    let onDone: (Set<EKCalendar>) -> Void
    let onCancel: () -> Void

    func makeCoordinator() -> Coordinator {
        Coordinator(onDone: onDone, onCancel: onCancel)
    }

    func makeUIViewController(
        context: Context
    ) -> EKCalendarChooser {
        let controller = EKCalendarChooser(
            selectionStyle: .single,
            displayStyle: .writableCalendarsOnly,
            entityType: .event,
            eventStore: eventStore
        )
        controller.delegate = context.coordinator
        controller.showsCancelButton = true
        controller.showsDoneButton = true
        return controller
    }

    func updateUIViewController(
        _ controller: EKCalendarChooser,
        context: Context
    ) {}

    final class Coordinator: NSObject, EKCalendarChooserDelegate {
        let onDone: (Set<EKCalendar>) -> Void
        let onCancel: () -> Void

        init(
            onDone: @escaping (Set<EKCalendar>) -> Void,
            onCancel: @escaping () -> Void
        ) {
            self.onDone = onDone
            self.onCancel = onCancel
        }

        func calendarChooser(
            _ calendarChooser: EKCalendarChooser,
            didSelect calendars: Set<EKCalendar>
        ) {
            onDone(calendars)
        }

        func calendarChooserDidCancel(
            _ calendarChooser: EKCalendarChooser
        ) {
            onCancel()
        }
    }
}
~~~

The exact initializer and delegate methods are SDK-sensitive. Compile against the selected SDK and gate the route on the access level required by the target. In a write-only route, use writable calendars only and do not treat the returned calendar objects as broad read access.

## AI proposal models

~~~swift
struct ContactSelectionProposal {
    let contactIdentifier: String
    let selectedProperty: String?
    let reason: String
}

struct EventDraft {
    let title: String
    let start: Date
    let end: Date
    let timeZoneIdentifier: String?
    let calendarIdentifier: String?
    let sourceRevision: String
}

enum PersonalDataAction {
    case chooseContact(ContactSelectionProposal)
    case openEventEditor(EventDraft)
    case chooseCalendar(EventDraft)
}
~~~

Decode model output into these types, then validate the current Contacts/EventKit state and require a person-facing confirmation. Never call a save or system action directly from an unreviewed text response.

## Proof checklist

- compile each UIViewControllerRepresentable in the named app target;
- confirm delegate signatures and main-actor behavior in Xcode;
- test picker cancellation and exactly-once completion;
- test limited/no/denied/restricted/full contact access;
- test EventKit editor action and calendar chooser destination;
- recheck access/store changes before direct mutations;
- use stable identifiers and stale-source invalidation;
- test VoiceOver, Dynamic Type, localization, RTL, reduced effects, keyboard, and pointer;
- record physical system-surface evidence before calling the route shipped.

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
- [EKCalendarChooserDelegate](https://developer.apple.com/documentation/eventkitui/ekcalendarchooserdelegate)
- [Accessing Calendar using EventKit and EventKitUI](https://developer.apple.com/documentation/eventkit/accessing-calendar-using-eventkit-and-eventkitui)
- [UIViewControllerRepresentable](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable)
