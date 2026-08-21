# SwiftUI EventKit and EventKitUI calendar/reminders code recipes

These are compile-oriented starting points for an iOS 26 target. Keep the `EKEventStore` alive while its EventKit objects are in use, verify every signature against the final SDK, and exercise the resulting Calendar/Reminders behavior with real system accounts on a physical device. A successful compile or `save` call is not release proof.

## 1. Authorization-aware store coordinator

```swift
import EventKit
import Observation

@MainActor
@Observable
final class CalendarRemindersStore {
    let store = EKEventStore()

    private(set) var eventStatus = EKAuthorizationStatus.notDetermined
    private(set) var reminderStatus = EKAuthorizationStatus.notDetermined
    private(set) var lastError: String?

    init() {
        refreshAuthorization()
    }

    func refreshAuthorization() {
        eventStatus = EKEventStore.authorizationStatus(for: .event)
        reminderStatus = EKEventStore.authorizationStatus(for: .reminder)
    }

    func requestWriteOnlyEventAccess() async {
        do {
            _ = try await store.requestWriteOnlyAccessToEvents()
            lastError = nil
        } catch {
            lastError = String(describing: error)
        }
        refreshAuthorization()
    }

    func requestFullEventAccess() async {
        do {
            _ = try await store.requestFullAccessToEvents()
            lastError = nil
        } catch {
            lastError = String(describing: error)
        }
        refreshAuthorization()
    }

    func requestFullReminderAccess() async {
        do {
            _ = try await store.requestFullAccessToReminders()
            lastError = nil
        } catch {
            lastError = String(describing: error)
        }
        refreshAuthorization()
    }
}
```

Keep `.writeOnly` separate from `.fullAccess`. A write-only event flow can create an event but must not use `events(matching:)`, `calendars(for:)`, or an event readback as if it had read permission. On iOS 17 and later, a feature that only presents `EKEventEditViewController` for event creation can use the system UI lane without requesting direct calendar access; keep that decision in the route design rather than mixing it into this coordinator.

## 2. App-owned event draft and direct commit

```swift
import EventKit
import Foundation

struct EventDraft: Sendable {
    var title: String
    var notes: String?
    var start: Date
    var end: Date
    var isAllDay: Bool
    var calendarIdentifier: String?
    var alarmOffset: TimeInterval?
}

enum CalendarCommitError: Error, LocalizedError {
    case accessRequired
    case invalidRange
    case reminderStartRequired
    case noWritableCalendar

    var errorDescription: String? {
        switch self {
        case .accessRequired:
            "Calendar access at the required level is not available."
        case .invalidRange:
            "The event end must be after its start."
        case .reminderStartRequired:
            "On iOS, a reminder with a due date also needs a start date."
        case .noWritableCalendar:
            "Choose a writable calendar before saving."
        }
    }
}

extension CalendarRemindersStore {
    func saveEvent(from draft: EventDraft) throws -> String {
        guard eventStatus == .writeOnly || eventStatus == .fullAccess else {
            throw CalendarCommitError.accessRequired
        }
        guard draft.isAllDay || draft.end > draft.start else {
            throw CalendarCommitError.invalidRange
        }

        let event = EKEvent(eventStore: store)
        event.title = draft.title.trimmingCharacters(in: .whitespacesAndNewlines)
        event.notes = draft.notes
        event.startDate = draft.start
        event.endDate = draft.end
        event.isAllDay = draft.isAllDay

        let selected = draft.calendarIdentifier.flatMap {
            store.calendar(withIdentifier: $0)
        }
        let calendar = selected ?? store.defaultCalendarForNewEvents
        guard let calendar, calendar.allowsContentModifications else {
            throw CalendarCommitError.noWritableCalendar
        }
        event.calendar = calendar

        if let alarmOffset = draft.alarmOffset {
            event.addAlarm(EKAlarm(relativeOffset: alarmOffset))
        }

        try store.save(event, span: .thisEvent, commit: true)
        return event.calendarItemIdentifier
    }
}
```

The returned local identifier is a lookup hint, not a permanent cross-device primary key. Publish a saving/committed state and refetch with full access before claiming that the system record is reconciled. If this route uses write-only access, show a write receipt that does not imply readable Calendar data.

## 3. Reminder date components and commit

```swift
import EventKit
import Foundation

struct ReminderDraft: Sendable {
    var title: String
    var notes: String?
    var listIdentifier: String?
    var start: DateComponents?
    var due: DateComponents?
    var priority: Int
}

extension CalendarRemindersStore {
    func saveReminder(from draft: ReminderDraft) throws -> String {
        guard reminderStatus == .fullAccess else {
            throw CalendarCommitError.accessRequired
        }

        if draft.due != nil && draft.start == nil {
            // iOS requires a start date when a due date is set.
            throw CalendarCommitError.reminderStartRequired
        }

        let reminder = EKReminder(eventStore: store)
        reminder.title = draft.title.trimmingCharacters(in: .whitespacesAndNewlines)
        reminder.notes = draft.notes
        reminder.startDateComponents = draft.start
        reminder.dueDateComponents = draft.due
        reminder.priority = draft.priority

        let selected = draft.listIdentifier.flatMap {
            store.calendar(withIdentifier: $0)
        }
        let calendar = selected ?? store.defaultCalendarForNewReminders()
        guard let calendar, calendar.allowsContentModifications else {
            throw CalendarCommitError.noWritableCalendar
        }
        reminder.calendar = calendar

        try store.save(reminder, commit: true)
        return reminder.calendarItemIdentifier
    }
}
```

Normalize `DateComponents` before this method: preserve all-day versus timed intent, use the Gregorian calendar for reminder date components, preserve the intended time zone or floating behavior, and keep the app-owned draft if save throws. Do not silently turn an invalid due-date-only draft into a different reminder.

## 4. Recurrence and alarm builders

```swift
import EventKit

func weeklyRule(on weekday: EKWeekday, end: EKRecurrenceEnd? = nil) -> EKRecurrenceRule {
    EKRecurrenceRule(
        recurrenceWith: .weekly,
        interval: 1,
        daysOfTheWeek: [EKRecurrenceDayOfWeek(weekday)],
        daysOfTheMonth: nil,
        monthsOfTheYear: nil,
        weeksOfTheYear: nil,
        daysOfTheYear: nil,
        setPositions: nil,
        end: end
    )
}

func addReviewedRecurrence(_ rule: EKRecurrenceRule, to event: EKEvent) {
    // Call only after the person has reviewed the recurrence summary.
    event.addRecurrenceRule(rule)
}

func reviewText(for span: EKSpan) -> String {
    switch span {
    case .thisEvent:
        "This event only"
    case .futureEvents:
        "This and future events"
    @unknown default:
        "Selected recurrence scope"
    }
}
```

Keep `EKSpan` in the command model rather than burying it inside a generic “save” button. A recurring reminder has different retrieval behavior from a recurring event, so the UI and proof fixture should name the entity explicitly.

## 5. Bounded event query

```swift
import EventKit
import Foundation

extension CalendarRemindersStore {
    func events(in interval: DateInterval, calendars: [EKCalendar]? = nil) -> [EKEvent] {
        guard eventStatus == .fullAccess else { return [] }

        let predicate = store.predicateForEvents(
            withStart: interval.start,
            end: interval.end,
            calendars: calendars
        )

        return store.events(matching: predicate)
            .sorted { $0.compareStartDate(with: $1) == .orderedAscending }
    }
}
```

Bound the interval to the visible product scope. Apple documents that the event predicate is limited to a four-year span and that returned events are not necessarily chronological. Treat an empty result as a data result only after the access and query-state gates have passed.

## 6. Async reminder fetch with a generation boundary

```swift
import EventKit
import Foundation

extension CalendarRemindersStore {
    func incompleteReminders(
        from start: Date?,
        through end: Date?,
        calendars: [EKCalendar]?,
        generation: Int
    ) async -> (generation: Int, reminders: [EKReminder]) {
        guard reminderStatus == .fullAccess else {
            return (generation, [])
        }

        let predicate = store.predicateForIncompleteReminders(
            withDueDateStarting: start,
            ending: end,
            calendars: calendars
        )

        let reminders: [EKReminder] = await withCheckedContinuation { continuation in
            _ = store.fetchReminders(matching: predicate) { reminders in
                continuation.resume(returning: reminders ?? [])
            }
        }

        // The caller accepts the result only if this generation is still current.
        return (generation, reminders)
    }
}
```

In production, retain the returned fetch request when rapid filter changes need cancellation and call `cancelFetchRequest(_:)` at the feature boundary. The generation check is still required because cancellation and callback delivery are separate concerns.

## 7. Observe store changes and refetch

```swift
import EventKit
import Foundation

@MainActor
final class EventStoreChangeBridge {
    private let store: EKEventStore
    private var token: NSObjectProtocol?
    private(set) var revision = 0

    init(store: EKEventStore, onChange: @escaping @MainActor () -> Void) {
        self.store = store
        token = NotificationCenter.default.addObserver(
            forName: .EKEventStoreChanged,
            object: store,
            queue: .main
        ) { [weak self] _ in
            guard let self else { return }
            self.revision &+= 1
            onChange()
        }
    }

    deinit {
        if let token {
            NotificationCenter.default.removeObserver(token)
        }
    }
}
```

The notification is an invalidation signal, not a diff. Release or discard fetched objects, refetch the visible range/list, and refresh an actively used item only if the item remains valid. Keep the callback small; the owner should schedule the bounded refetch and ignore results from an older revision.

## 8. SwiftUI wrapper for the system event editor

```swift
import EventKit
import EventKitUI
import SwiftUI

struct EventEditorView: UIViewControllerRepresentable {
    let store: EKEventStore
    let event: EKEvent?
    let onAction: (EKEventEditViewAction) -> Void

    func makeCoordinator() -> Coordinator {
        Coordinator(onAction: onAction)
    }

    func makeUIViewController(context: Context) -> EKEventEditViewController {
        let controller = EKEventEditViewController()
        controller.eventStore = store
        controller.event = event
        controller.editViewDelegate = context.coordinator
        return controller
    }

    func updateUIViewController(
        _ controller: EKEventEditViewController,
        context: Context
    ) {
        context.coordinator.onAction = onAction
        controller.eventStore = store
        controller.event = event
    }

    final class Coordinator: NSObject, EKEventEditViewDelegate {
        var onAction: (EKEventEditViewAction) -> Void

        init(onAction: @escaping (EKEventEditViewAction) -> Void) {
            self.onAction = onAction
        }

        func eventEditViewController(
            _ controller: EKEventEditViewController,
            didCompleteWith action: EKEventEditViewAction
        ) {
            onAction(action)
        }
    }
}
```

Present this wrapper from a SwiftUI `.sheet` or `.fullScreenCover` and let the owner dismiss it after the delegate action. Map `.saved`, `.deleted`, and `.canceled` into a reducer, then refetch. Do not make the wrapper a second EventKit store owner.

## 9. Typed AI proposal boundary

```swift
import Foundation
import FoundationModels

@Generable
struct SchedulingProposal {
    var title: String
    var durationMinutes: Int
    var candidateStartISO8601: String
    var timeZoneIdentifier: String?
    var isAllDay: Bool
    var reminderOffsetMinutes: Int?
}

struct ValidatedSchedulingProposal: Sendable {
    let title: String
    let start: Date
    let end: Date
    let reminderOffset: TimeInterval?
}

enum ProposalValidationError: Error {
    case emptyTitle
    case durationOutOfRange
    case invalidDate
    case unsupportedTimeZone
}

func validate(
    _ proposal: SchedulingProposal,
    now: Date = .now
) throws -> ValidatedSchedulingProposal {
    let title = proposal.title.trimmingCharacters(in: .whitespacesAndNewlines)
    guard !title.isEmpty else { throw ProposalValidationError.emptyTitle }
    guard (5...1_440).contains(proposal.durationMinutes) else {
        throw ProposalValidationError.durationOutOfRange
    }

    let formatter = ISO8601DateFormatter()
    guard let start = formatter.date(from: proposal.candidateStartISO8601),
          start >= now.addingTimeInterval(-60)
    else {
        throw ProposalValidationError.invalidDate
    }

    if let identifier = proposal.timeZoneIdentifier,
       TimeZone(identifier: identifier) == nil {
        throw ProposalValidationError.unsupportedTimeZone
    }

    let end = start.addingTimeInterval(TimeInterval(proposal.durationMinutes * 60))
    let reminder = proposal.reminderOffsetMinutes.map { -TimeInterval($0 * 60) }
    return ValidatedSchedulingProposal(
        title: title,
        start: start,
        end: end,
        reminderOffset: reminder
    )
}
```

The proposal is configuration, not an EventKit command. Add calendar/list resolution, duplicate checks, store-revision checks, and human review before converting it into `EventDraft` or a system editor presentation. If Foundation Models is unavailable or returns invalid output, use the manual form.

## 10. Proof-oriented Swift Testing fixtures

```swift
import EventKit
import Testing

struct EventKitRouteFixtures {
    @Test("write-only event state never becomes readable")
    func writeOnlyBoundary() {
        let status = EKAuthorizationStatus.writeOnly
        #expect(status != .fullAccess)
    }

    @Test("proposal duration is bounded")
    func proposalBounds() throws {
        let proposal = SchedulingProposal(
            title: "Project review",
            durationMinutes: 45,
            candidateStartISO8601: "2026-08-20T19:00:00Z",
            timeZoneIdentifier: "America/Chicago",
            isAllDay: false,
            reminderOffsetMinutes: 15
        )
        #expect(throws: Never.self) {
            _ = try validate(proposal, now: Date(timeIntervalSince1970: 0))
        }
    }
}
```

These tests cover deterministic policy only. They do not prove permission prompts, Calendar/Reminders account state, EventKitUI presentation, recurrence behavior, notification scheduling, or physical device release behavior.

## Sources

- [Accessing the event store](https://developer.apple.com/documentation/eventkit/accessing-the-event-store)
- [Creating events and reminders](https://developer.apple.com/documentation/eventkit/creating-events-and-reminders)
- [Retrieving events and reminders](https://developer.apple.com/documentation/eventkit/retrieving-events-and-reminders)
- [Creating a recurring event](https://developer.apple.com/documentation/eventkit/creating-a-recurring-event)
- [EKEventStore](https://developer.apple.com/documentation/eventkit/ekeventstore)
- [requestWriteOnlyAccessToEvents(completion:)](https://developer.apple.com/documentation/eventkit/ekeventstore/requestwriteonlyaccesstoevents%28completion%3A%29)
- [requestFullAccessToEvents(completion:)](https://developer.apple.com/documentation/eventkit/ekeventstore/requestfullaccesstoevents%28completion%3A%29)
- [requestFullAccessToReminders(completion:)](https://developer.apple.com/documentation/eventkit/ekeventstore/requestfullaccesstoreminders%28completion%3A%29)
- [authorizationStatus(for:)](https://developer.apple.com/documentation/eventkit/ekeventstore/authorizationstatus%28for%3A%29)
- [EKAuthorizationStatus](https://developer.apple.com/documentation/eventkit/ekauthorizationstatus)
- [EKEvent](https://developer.apple.com/documentation/eventkit/ekevent)
- [EKReminder](https://developer.apple.com/documentation/eventkit/ekreminder)
- [EKCalendar](https://developer.apple.com/documentation/eventkit/ekcalendar)
- [EKRecurrenceRule](https://developer.apple.com/documentation/eventkit/ekrecurrencerule)
- [EKAlarm](https://developer.apple.com/documentation/eventkit/ekalarm)
- [EKEventStore.EventStoreChanged](https://developer.apple.com/documentation/eventkit/ekeventstore/eventstorechanged)
- [EventKit UI](https://developer.apple.com/documentation/eventkitui)
- [EKEventEditViewController](https://developer.apple.com/documentation/eventkitui/ekeventeditviewcontroller)
- [EKEventEditViewDelegate](https://developer.apple.com/documentation/eventkitui/ekeventeditviewdelegate)
- [EKEventEditViewAction](https://developer.apple.com/documentation/eventkitui/ekeventeditviewaction)
- [UIViewControllerRepresentable](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
