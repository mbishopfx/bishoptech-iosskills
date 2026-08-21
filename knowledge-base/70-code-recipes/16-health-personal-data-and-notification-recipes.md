# Health, Personal Data, and Notification Recipes

Use the [capability-first Apple SDK atlas](../40-framework-routes/10-capability-first-apple-sdk-atlas.md) and [cross-framework feature lifecycle](../41-framework-deep-dives/06-cross-framework-feature-lifecycle.md) to keep protected-data authorization, freshness, user review, deletion, and system-surface handoffs explicit.

## Scope and compile boundary

These are compile-oriented route sketches for HealthKit authorization/query/observation, Contacts selection/fetching, EventKit calendar/reminder drafts, and User Notifications. They are not compiled in this documentation-only workspace and do not prove protected-data availability, account synchronization, background delivery, notification presentation/timing, privacy labels, medical/regulatory suitability, or physical-device/system-surface behavior.

Keep each external system behind a feature-owned service:

`explain -> request exact access -> read/write/schedule -> normalize -> review -> persist minimal state`

An authorization result is not a guarantee of complete data, a notification is not guaranteed delivery, and a framework callback is not product validation.

## Recipe 1: request the smallest HealthKit data set

Enable the HealthKit capability and include truthful health-data usage descriptions. Check availability before creating a feature state that depends on HealthKit.

```swift
import HealthKit

final class HealthService {
    let store = HKHealthStore()

    func requestStepAccess() async throws -> Bool {
        guard HKHealthStore.isHealthDataAvailable(),
              let stepType = HKQuantityType.quantityType(
                forIdentifier: .stepCount
              ) else {
            return false
        }

        let readTypes: Set<HKObjectType> = [stepType]
        let shareTypes: Set<HKSampleType> = [stepType]

        try await store.requestAuthorization(
            toShare: shareTypes,
            read: readTypes
        )

        // This means the request completed without an error. It does not
        // mean every read/share type was granted.
        return true
    }
}
```

Do not infer read permission from an empty query. HealthKit intentionally limits what the app can learn about a person’s read grants. Use `authorizationStatus(for:)` for the share/write side where appropriate, and make no-data, limited-history, denied, and unavailable states safe and understandable.

## Recipe 2: run a bounded HealthKit statistics query

Choose the smallest type, predicate, date range, and unit needed by the screen. HealthKit query callbacks may run off the main thread; publish normalized results to the feature’s observation boundary.

```swift
import HealthKit

final class StepSummaryQuery {
    private let store: HKHealthStore
    private var query: HKQuery?

    init(store: HKHealthStore) {
        self.store = store
    }

    func start(from startDate: Date, to endDate: Date) throws {
        guard let type = HKQuantityType.quantityType(
            forIdentifier: .stepCount
        ) else {
            return
        }

        let predicate = HKQuery.predicateForSamples(
            withStart: startDate,
            end: endDate,
            options: .strictStartDate
        )

        let statisticsQuery = HKStatisticsQuery(
            quantityType: type,
            quantitySamplePredicate: predicate,
            options: .cumulativeSum
        ) { [weak self] _, statistics, error in
            defer { self?.query = nil }

            guard error == nil, let statistics,
                  let sum = statistics.sumQuantity() else {
                // Publish an unavailable/failed/empty state as appropriate.
                return
            }

            let count = sum.doubleValue(for: .count())
            // Store only the derived value and source/date metadata the
            // feature needs; do not log the raw health payload.
            _ = count
        }

        query = statisticsQuery
        store.execute(statisticsQuery)
    }

    func stop() {
        if let query {
            store.stop(query)
        }
        query = nil
    }
}
```

The example is a route sketch: a real feature needs a request ID/generation so a late query cannot replace a newer date range, plus explicit empty, partial, deleted, source, unit, and time-zone state. If an incremental local projection is required, use an anchored query and persist/recover its anchor with a deletion policy rather than repeatedly copying the entire store.

## Recipe 3: observe HealthKit changes with a completion contract

An observer query reports that matching data changed; it does not supply all changed objects. Run a follow-up query, finish the bounded work, and call the completion handler. Background delivery requires its own capability/entitlement and device proof.

```swift
import HealthKit

final class HealthObserver {
    private let store: HKHealthStore
    private var query: HKObserverQuery?

    init(store: HKHealthStore) {
        self.store = store
    }

    func start(for sampleType: HKSampleType) {
        let observer = HKObserverQuery(
            sampleType: sampleType,
            predicate: nil
        ) { [weak self] query, completionHandler, error in
            defer { completionHandler() }

            guard error == nil else {
                // Record a redacted error category and leave the current
                // projection marked stale; do not claim data is absent.
                return
            }

            // Execute a bounded HKSampleQuery, HKStatisticsQuery, or
            // HKAnchoredObjectQuery here, then publish normalized state.
            _ = self
            _ = query
        }

        query = observer
        store.execute(observer)
    }

    func stop() {
        if let query {
            store.stop(query)
        }
        query = nil
    }
}
```

If background delivery is justified, enable it for the exact type and frequency, include the HealthKit background-delivery entitlement, configure observers early enough for relaunch delivery, and always call the completion handler. Do not treat the Simulator as proof of background server-query behavior.

## Recipe 4: fetch only the Contacts keys needed

Prefer ContactsUI when the feature needs one user-selected contact. If the product needs store access, include `NSContactsUsageDescription`, request access in context, fetch only required keys, and keep blocking I/O off the main thread.

```swift
import Contacts

final class ContactService {
    private let store = CNContactStore()

    func requestAccess() async throws -> Bool {
        try await withCheckedThrowingContinuation { continuation in
            store.requestAccess(for: .contacts) { granted, error in
                if let error {
                    continuation.resume(throwing: error)
                } else {
                    continuation.resume(returning: granted)
                }
            }
        }
    }

    func searchNames(matching text: String) throws -> [CNContact] {
        let keys: [CNKeyDescriptor] = [
            CNContactGivenNameKey as CNKeyDescriptor,
            CNContactFamilyNameKey as CNKeyDescriptor,
            CNContactIdentifierKey as CNKeyDescriptor,
            CNContactEmailAddressesKey as CNKeyDescriptor
        ]

        let predicate = CNContact.predicateForContacts(
            matchingName: text
        )
        return try store.unifiedContacts(
            matching: predicate,
            keysToFetch: keys
        )
    }
}
```

Run `searchNames` away from the main thread in a target implementation. These are partial contacts because only selected keys were fetched. If the app caches records, observe `CNContactStoreDidChange`, discard stale cached objects, and refetch. Do not log raw names, phone numbers, addresses, or contact identifiers.

## Recipe 5: make an EventKit write a reviewed draft

Use write-only event access when the feature only creates events. Use full access only when it must read/edit existing events. Include the current iOS usage-description key for the access level, and use EventKit UI when the system editor is the best fit.

```swift
import EventKit

final class CalendarService {
    private let store = EKEventStore()

    func requestWriteOnlyEventAccess() async throws -> Bool {
        try await withCheckedThrowingContinuation { continuation in
            store.requestWriteOnlyAccessToEvents { granted, error in
                if let error {
                    continuation.resume(throwing: error)
                } else {
                    continuation.resume(returning: granted)
                }
            }
        }
    }

    func requestFullEventAccess() async throws -> Bool {
        try await withCheckedThrowingContinuation { continuation in
            store.requestFullAccessToEvents { granted, error in
                if let error {
                    continuation.resume(throwing: error)
                } else {
                    continuation.resume(returning: granted)
                }
            }
        }
    }

    func requestFullReminderAccess() async throws -> Bool {
        try await withCheckedThrowingContinuation { continuation in
            store.requestFullAccessToReminders { granted, error in
                if let error {
                    continuation.resume(throwing: error)
                } else {
                    continuation.resume(returning: granted)
                }
            }
        }
    }
}
```

Build an app-owned `EventDraft` with title, start/end, time zone, recurrence, alarm, selected calendar, and an operation ID. Show the draft before saving. Calendar/account state can change outside the app; observe store changes and refresh rather than treating a previous `EKEvent` as authoritative. A retry must not create a duplicate event silently.

## Recipe 6: request and schedule local notifications deliberately

Assign the notification delegate before the app finishes launching when foreground presentation or action handling is needed. Request only the options the feature uses, inspect settings after the request, and use a stable identifier for replacement/cancellation.

```swift
import UserNotifications

final class NotificationService: NSObject, UNUserNotificationCenterDelegate {
    private let center = UNUserNotificationCenter.current()

    func installDelegate() {
        // Call during app launch, before launch finishes, when delegate
        // callbacks must be handled by this object.
        center.delegate = self
    }

    func requestPermission() async throws -> Bool {
        try await center.requestAuthorization(
            options: [.alert, .sound, .badge]
        )
    }

    func currentSettings() async -> UNNotificationSettings {
        await center.notificationSettings()
    }

    func scheduleReminder(
        id: String,
        title: String,
        body: String,
        after interval: TimeInterval
    ) async throws {
        let content = UNMutableNotificationContent()
        content.title = title
        content.body = body
        content.sound = .default

        let trigger = UNTimeIntervalNotificationTrigger(
            timeInterval: max(interval, 1),
            repeats: false
        )
        let request = UNNotificationRequest(
            identifier: id,
            content: content,
            trigger: trigger
        )

        try await center.add(request)
    }

    func cancelReminder(id: String) {
        center.removePendingNotificationRequests(withIdentifiers: [id])
        center.removeDeliveredNotifications(withIdentifiers: [id])
    }

    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification,
        withCompletionHandler completionHandler:
            @escaping (UNNotificationPresentationOptions) -> Void
    ) {
        completionHandler([.banner, .sound])
    }
}
```

The `true` result from `requestAuthorization` only means at least one requested option was granted. Re-read settings when the app returns to the foreground. Keep the in-app task state authoritative, avoid private lock-screen content, and do not describe local or remote notifications as guaranteed delivery. Remote notifications add APNs/server/token/authentication and delivery uncertainty; keep that route separate from local scheduling.

## Recipe 7: compose external-data state without hiding permissions

```swift
enum PersonalDataState {
    case unavailable(reason: String)
    case needsExplanation
    case authorizationPending
    case denied(manualRoute: String)
    case loading
    case ready(source: String, refreshedAt: Date)
    case empty(source: String, checkedAt: Date)
    case stale(lastKnownAt: Date)
    case failed(message: String, canRetry: Bool)
}

struct CalendarDraft {
    let operationID: UUID
    let title: String
    let start: Date
    let end: Date
    let calendarIdentifier: String?
    let timeZoneIdentifier: String?
    let requiresConfirmation: Bool
}
```

Keep external record IDs, source, fetched/created time, authorization state, and freshness beside the derived app model. A notification tap, App Intent, widget action, or AI suggestion must revalidate permission and current external state before reading or writing. Preserve user-entered drafts when access is unavailable.

## Recipe 8: privacy and retention matrix

| Data/surface | Minimum route | Do not assume |
| --- | --- | --- |
| Health sample | Exact HealthKit type/query and derived value | Empty means denied, grant means complete, or result means medical truth. |
| Contact | Picker or exact keys-to-fetch | Partial contact is complete identity; identifier is stable forever. |
| Calendar/reminder | Access level matching operation and reviewed draft | Write callback prevents duplicate or external edits. |
| Notification | Explicit content, stable ID, current settings | Permission means alert/sound/delivery on every device/context. |
| AI enrichment | Derived, minimized, user-understood context | Protected data may be sent to a remote tool or retained in prompts. |

Delete app-owned caches when the person disconnects the integration or asks for deletion. Explain which data lives in Apple’s external store and which copy belongs to the app. Keep raw payloads out of telemetry and redact error messages before persistence.

## Recipe 9: physical-device and system-surface verification

| Test | Evidence to capture |
| --- | --- |
| HealthKit | Capability/entitlements, unavailable device, fine-grained allow/deny, limited history, empty/deleted samples, units/time zones, observer query, background delivery, relaunch, and controlled Health app data. |
| Contacts | Picker versus store permission, limited/denied/revoked, selected keys, partial results, store-change notification, deleted record, background I/O, and redacted telemetry. |
| Calendar/reminders | Write-only/full access, current usage descriptions, account/calendar changes, time zones/DST, recurrence, EventKit UI, duplicate retry, external edit, and undo/delete behavior. |
| Notifications | Delegate installed at launch, authorization options/settings, local schedule/replace/cancel, foreground/background/terminated/relaunch, action/deep link, stale content, lock-screen privacy, and accessibility. |
| Fallback/privacy | Manual/app-local route, draft preservation, deletion/export, privacy labels, no protected data in logs/screenshots/analytics, and no medical claims. |

Previews and fixtures validate state machines and drafts. They do not prove protected-data prompts, HealthKit background delivery, external account stores, notification presentation/timing, APNs delivery, or system-owned UI. Record target device family, OS build, account/store setup, permissions, test data source, and test date for any release claim.

## Sources

- [HealthKit](https://developer.apple.com/documentation/healthkit)
- [HKHealthStore](https://developer.apple.com/documentation/healthkit/hkhealthstore)
- [Authorizing access to health data](https://developer.apple.com/documentation/healthkit/authorizing-access-to-health-data)
- [Reading data from HealthKit](https://developer.apple.com/documentation/healthkit/reading-data-from-healthkit)
- [Executing observer queries](https://developer.apple.com/documentation/healthkit/executing-observer-queries)
- [HealthKit background-delivery entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.healthkit.background-delivery)
- [Contacts](https://developer.apple.com/documentation/contacts)
- [CNContactStore](https://developer.apple.com/documentation/contacts/cncontactstore)
- [ContactsUI](https://developer.apple.com/documentation/contactsui)
- [NSContactsUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nscontactsusagedescription)
- [EventKit](https://developer.apple.com/documentation/eventkit)
- [Accessing the event store](https://developer.apple.com/documentation/eventkit/accessing-the-event-store)
- [EKEventStore](https://developer.apple.com/documentation/eventkit/ekeventstore)
- [NSCalendarsWriteOnlyAccessUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nscalendarswriteonlyaccessusagedescription)
- [NSCalendarsFullAccessUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nscalendarsfullaccessusagedescription)
- [NSRemindersFullAccessUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsremindersfullaccessusagedescription)
- [User Notifications](https://developer.apple.com/documentation/usernotifications)
- [Asking permission to use notifications](https://developer.apple.com/documentation/usernotifications/asking-permission-to-use-notifications)
- [UNUserNotificationCenter](https://developer.apple.com/documentation/usernotifications/unusernotificationcenter)
- [Requesting authorization](https://developer.apple.com/documentation/usernotifications/unusernotificationcenter/requestauthorization%28options%3Acompletionhandler%3A%29)
- [UNNotificationRequest](https://developer.apple.com/documentation/usernotifications/unnotificationrequest)
- [UNTimeIntervalNotificationTrigger](https://developer.apple.com/documentation/usernotifications/untimeintervalnotificationtrigger)
