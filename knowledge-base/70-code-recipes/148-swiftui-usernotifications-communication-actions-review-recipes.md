# SwiftUI UserNotifications, communication notifications, and action review recipes

These are compile-oriented Swift sketches for a named iOS target. They are not claimed to compile in this documentation-only workspace and they do not prove authorization, system presentation, APNs delivery, Focus behavior, communication identity, extension execution, model availability, accessibility, or release readiness.

Read the [notification review](../42-framework-deep-dives/105-swiftui-usernotifications-communication-actions-review.md), [design guide](../21-design-deep-dives/133-swiftui-usernotifications-communication-actions-review-design.md), [route](../50-capability-recipes/136-swiftui-usernotifications-communication-actions-review-route.md), and [proof matrix](../60-verification/130-swiftui-usernotifications-communication-actions-review-proof-matrix.md) first. Confirm current SDK signatures, availability, capabilities, entitlements, Info.plist keys, extension targets, provider contracts, and physical-device behavior before using any sketch.

## Recipe 1: Keep notification intent app-owned

Do not make a UserNotifications object the durable domain model.

~~~swift
import Foundation

struct NotificationRecord: Codable, Hashable, Sendable, Identifiable {
    enum Channel: String, Codable, Sendable {
        case reminder
        case status
        case directMessage
        case call
        case order
    }

    enum State: String, Codable, Sendable {
        case draft
        case ready
        case scheduled
        case providerQueued
        case providerAccepted
        case unknownDelivery
        case actionPending
        case completed
        case canceled
        case stale
    }

    let id: String
    var revision: Int
    var channel: Channel
    var state: State
    var sourceTitle: String
    var sourceBody: String
    var privacyClass: PrivacyClass
    var updatedAt: Date
}

enum PrivacyClass: String, Codable, Sendable {
    case public
    case private
    case sensitive
    case redacted
}

struct NotificationIntent: Codable, Hashable, Sendable {
    let recordID: String
    let sourceRevision: Int
    let purpose: String
    let categoryIdentifier: String
    let actionIdentifiers: [String]
    let body: String
    let privacyClass: PrivacyClass
}
~~~

The record is the app’s truth. A request identifier, userInfo dictionary, or notification body is only a system-route projection.

## Recipe 2: Model a refreshed system settings snapshot

Keep the settings read separate from an app-owned preference.

~~~swift
import UserNotifications

struct NotificationSettingsSnapshot: Sendable, Equatable {
    let authorization: UNAuthorizationStatus
    let alert: UNNotificationSetting
    let sound: UNNotificationSetting
    let badge: UNNotificationSetting
    let lockScreen: UNNotificationSetting
    let notificationCenter: UNNotificationSetting
    let carPlay: UNNotificationSetting
    let timeSensitive: UNNotificationSetting
    let criticalAlert: UNNotificationSetting
    let refreshedAt: Date

    var canOfferOrdinaryAlerts: Bool {
        authorization == .authorized || authorization == .provisional
    }
}

@MainActor
final class NotificationSettingsModel: ObservableObject {
    @Published private(set) var snapshot: NotificationSettingsSnapshot?
    @Published private(set) var isRefreshing = false

    private let center = UNUserNotificationCenter.current()

    func refresh() async {
        isRefreshing = true
        let settings = await center.notificationSettings()
        snapshot = NotificationSettingsSnapshot(
            authorization: settings.authorizationStatus,
            alert: settings.alertSetting,
            sound: settings.soundSetting,
            badge: settings.badgeSetting,
            lockScreen: settings.lockScreenSetting,
            notificationCenter: settings.notificationCenterSetting,
            carPlay: settings.carPlaySetting,
            timeSensitive: settings.timeSensitiveSetting,
            criticalAlert: settings.criticalAlertSetting,
            refreshedAt: Date()
        )
        isRefreshing = false
    }
}
~~~

Treat each value as a system snapshot. Do not mutate it locally and then claim that iOS changed.

## Recipe 3: Request only the notification options the feature needs

Explain the value before calling authorization.

~~~swift
import UserNotifications

struct NotificationAuthorizationResult: Sendable {
    let granted: Bool
    let settings: NotificationSettingsSnapshot
}

actor NotificationAuthorizationCoordinator {
    private let center = UNUserNotificationCenter.current()

    func requestOrdinaryNotifications() async throws -> NotificationAuthorizationResult {
        let granted = try await center.requestAuthorization(options: [.alert, .sound, .badge])
        let settings = await center.notificationSettings()
        let snapshot = NotificationSettingsSnapshot(
            authorization: settings.authorizationStatus,
            alert: settings.alertSetting,
            sound: settings.soundSetting,
            badge: settings.badgeSetting,
            lockScreen: settings.lockScreenSetting,
            notificationCenter: settings.notificationCenterSetting,
            carPlay: settings.carPlaySetting,
            timeSensitive: settings.timeSensitiveSetting,
            criticalAlert: settings.criticalAlertSetting,
            refreshedAt: Date()
        )
        return NotificationAuthorizationResult(granted: granted, settings: snapshot)
    }
}
~~~

Use provisional, time-sensitive, or critical options only after a separate product and entitlement review. A true granted result does not mean every presentation style is enabled.

## Recipe 4: Build content from a redacted intent

Calculate privacy and urgency before creating the system object.

~~~swift
import UserNotifications

struct NotificationContentFactory {
    static func makeContent(
        intent: NotificationIntent,
        interruption: UNNotificationInterruptionLevel = .active
    ) -> UNMutableNotificationContent {
        let content = UNMutableNotificationContent()
        content.title = title(for: intent)
        content.body = body(for: intent)
        content.categoryIdentifier = intent.categoryIdentifier
        content.threadIdentifier = "record." + intent.recordID
        content.userInfo = [
            "recordID": intent.recordID,
            "sourceRevision": intent.sourceRevision,
            "schemaVersion": 1
        ]
        content.interruptionLevel = interruption
        content.relevanceScore = 0.5
        return content
    }

    private static func title(for intent: NotificationIntent) -> String {
        switch intent.privacyClass {
        case .public:
            return intent.purpose
        case .private, .sensitive, .redacted:
            return "You have an update"
        }
    }

    private static func body(for intent: NotificationIntent) -> String {
        switch intent.privacyClass {
        case .public:
            return intent.body
        case .private, .sensitive, .redacted:
            return "Open the app to view the details."
        }
    }
}
~~~

Do not put secrets or raw model output in userInfo. Store an opaque record ID and re-resolve current truth when an action arrives.

## Recipe 5: Create documented local triggers

Use a trigger that matches the product’s time semantics.

~~~swift
import Foundation
import UserNotifications

enum LocalTriggerDraft: Sendable {
    case after(TimeInterval)
    case calendar(DateComponents)
}

enum LocalTriggerError: Error {
    case nonPositiveInterval
    case emptyCalendarComponents
}

struct LocalTriggerFactory {
    static func make(_ draft: LocalTriggerDraft) throws -> UNNotificationTrigger {
        switch draft {
        case .after(let interval):
            guard interval > 0 else { throw LocalTriggerError.nonPositiveInterval }
            return UNTimeIntervalNotificationTrigger(timeInterval: interval, repeats: false)

        case .calendar(let components):
            guard !components.isEmpty else { throw LocalTriggerError.emptyCalendarComponents }
            return UNCalendarNotificationTrigger(dateMatching: components, repeats: false)
        }
    }
}
~~~

Add a location trigger only after location permission and region behavior are part of the route proof. Test timezone and daylight-saving behavior for recurring calendar triggers.

## Recipe 6: Schedule with a stable identifier

Make replacement and cancellation explicit.

~~~swift
import UserNotifications

actor LocalNotificationScheduler {
    private let center = UNUserNotificationCenter.current()

    func schedule(
        intent: NotificationIntent,
        trigger: UNNotificationTrigger
    ) async throws -> String {
        let identifier = "notification." + intent.recordID + "." + intent.categoryIdentifier
        let content = NotificationContentFactory.makeContent(intent: intent)
        let request = UNNotificationRequest(
            identifier: identifier,
            content: content,
            trigger: trigger
        )
        try await center.add(request)
        return identifier
    }

    func cancel(identifiers: [String]) {
        center.removePendingNotificationRequests(withIdentifiers: identifiers)
        center.removeDeliveredNotifications(withIdentifiers: identifiers)
    }

    func pendingIdentifiers() async -> [String] {
        let requests = await center.pendingNotificationRequests()
        return requests.map(\.identifier)
    }
}
~~~

Removing a delivered notification is not deletion of the app-owned record. Reconcile both states independently.

## Recipe 7: Register categories and actions at launch

Register categories before sending local or remote payloads.

~~~swift
import UserNotifications

enum NotificationActionID {
    static let open = "OPEN_RECORD"
    static let markRead = "MARK_READ"
    static let accept = "ACCEPT"
    static let decline = "DECLINE"
    static let reply = "REPLY"
}

enum NotificationCategoryID {
    static let message = "MESSAGE"
    static let invitation = "INVITATION"
    static let reminder = "REMINDER"
}

struct NotificationCategoryRegistry {
    static func categories() -> Set<UNNotificationCategory> {
        let open = UNNotificationAction(
            identifier: NotificationActionID.open,
            title: "Open",
            options: [.foreground]
        )
        let markRead = UNNotificationAction(
            identifier: NotificationActionID.markRead,
            title: "Mark Read",
            options: []
        )
        let reply = UNTextInputNotificationAction(
            identifier: NotificationActionID.reply,
            title: "Reply",
            options: [],
            textInputButtonTitle: "Send",
            textInputPlaceholder: "Write a short reply"
        )
        let accept = UNNotificationAction(
            identifier: NotificationActionID.accept,
            title: "Accept",
            options: []
        )
        let decline = UNNotificationAction(
            identifier: NotificationActionID.decline,
            title: "Decline",
            options: [.destructive]
        )

        return [
            UNNotificationCategory(
                identifier: NotificationCategoryID.message,
                actions: [reply, markRead, open],
                intentIdentifiers: [],
                options: [.customDismissAction]
            ),
            UNNotificationCategory(
                identifier: NotificationCategoryID.invitation,
                actions: [accept, decline, open],
                intentIdentifiers: [],
                options: []
            ),
            UNNotificationCategory(
                identifier: NotificationCategoryID.reminder,
                actions: [open],
                intentIdentifiers: [],
                options: []
            )
        ]
    }

    static func register() {
        UNUserNotificationCenter.current().setNotificationCategories(categories())
    }
}
~~~

Keep action IDs stable across localization and UI copy changes. Confirm the current target SDK’s initializer and option availability before compiling.

## Recipe 8: Install an early delegate bridge in a SwiftUI app

Assign the delegate before launch finishes.

~~~swift
import SwiftUI
import UserNotifications

@MainActor
final class NotificationRouteStore: ObservableObject {
    @Published private(set) var events: [NotificationRouteEvent] = []

    func record(_ event: NotificationRouteEvent) {
        events.append(event)
    }
}

struct NotificationRouteEvent: Identifiable, Sendable {
    let id = UUID()
    let actionIdentifier: String
    let recordID: String?
    let sourceRevision: Int?
    let receivedAt: Date
}

final class AppNotificationDelegate: NSObject, UNUserNotificationCenterDelegate {
    let store: NotificationRouteStore

    init(store: NotificationRouteStore) {
        self.store = store
    }

    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification,
        withCompletionHandler completionHandler:
            @escaping (UNNotificationPresentationOptions) -> Void
    ) {
        let content = notification.request.content
        let event = NotificationRouteEvent(
            actionIdentifier: "FOREGROUND_NOTIFICATION",
            recordID: content.userInfo["recordID"] as? String,
            sourceRevision: content.userInfo["sourceRevision"] as? Int,
            receivedAt: Date()
        )
        Task { @MainActor in
            store.record(event)
        }
        completionHandler([])
    }

    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse,
        withCompletionHandler completionHandler: @escaping () -> Void
    ) {
        let content = response.notification.request.content
        let event = NotificationRouteEvent(
            actionIdentifier: response.actionIdentifier,
            recordID: content.userInfo["recordID"] as? String,
            sourceRevision: content.userInfo["sourceRevision"] as? Int,
            receivedAt: Date()
        )
        Task { @MainActor in
            store.record(event)
        }
        completionHandler()
    }
}
~~~

For the modern async delegate form, verify the exact SDK signature and do not implement both the completion-handler and async forms for the same route.

## Recipe 9: Wire the delegate through the app lifecycle

Keep the delegate and category registration near the lifecycle boundary.

~~~swift
import SwiftUI
import UserNotifications

@main
struct NotificationDemoApp: App {
    @StateObject private var routeStore: NotificationRouteStore
    private let delegate: AppNotificationDelegate

    init() {
        let store = NotificationRouteStore()
        _routeStore = StateObject(wrappedValue: store)
        let delegate = AppNotificationDelegate(store: store)
        self.delegate = delegate
        let center = UNUserNotificationCenter.current()
        center.delegate = delegate
        NotificationCategoryRegistry.register()
    }

    var body: some Scene {
        WindowGroup {
            NotificationSettingsView()
                .environmentObject(routeStore)
        }
    }
}
~~~

If a production app uses an application delegate adaptor, perform the early delegate assignment there and forward into a main-actor store. The important property is timing and one-owner routing.

## Recipe 10: Parse an action into a safe typed route

Never mutate from a raw action identifier or notification body.

~~~swift
import UserNotifications

enum NotificationRoute: Sendable, Equatable {
    case open(recordID: String)
    case markRead(recordID: String, sourceRevision: Int)
    case accept(recordID: String, sourceRevision: Int)
    case decline(recordID: String, sourceRevision: Int)
    case reply(recordID: String, sourceRevision: Int, text: String)
    case dismissed
    case defaultOpen(recordID: String)
    case unknown
}

struct NotificationRouteParser {
    static func parse(response: UNNotificationResponse) -> NotificationRoute {
        let content = response.notification.request.content
        guard let recordID = content.userInfo["recordID"] as? String else {
            return .unknown
        }
        let revision = content.userInfo["sourceRevision"] as? Int ?? -1

        switch response.actionIdentifier {
        case UNNotificationDefaultActionIdentifier:
            return .defaultOpen(recordID: recordID)
        case UNNotificationDismissActionIdentifier:
            return .dismissed
        case NotificationActionID.open:
            return .open(recordID: recordID)
        case NotificationActionID.markRead:
            return .markRead(recordID: recordID, sourceRevision: revision)
        case NotificationActionID.accept:
            return .accept(recordID: recordID, sourceRevision: revision)
        case NotificationActionID.decline:
            return .decline(recordID: recordID, sourceRevision: revision)
        case NotificationActionID.reply:
            guard let textResponse = response as? UNTextInputNotificationResponse else {
                return .unknown
            }
            return .reply(
                recordID: recordID,
                sourceRevision: revision,
                text: textResponse.userText
            )
        default:
            return .unknown
        }
    }
}
~~~

The app-owned route handler must load the current record, compare revisions, check account/protected-data state, and commit idempotently.

## Recipe 11: Revalidate before a domain mutation

Treat a notification response as a stale command candidate.

~~~swift
actor NotificationActionHandler {
    private let records: NotificationRecordStore

    init(records: NotificationRecordStore) {
        self.records = records
    }

    func handle(_ route: NotificationRoute) async -> ActionResult {
        switch route {
        case .open(let recordID), .defaultOpen(let recordID):
            return await records.open(recordID: recordID)

        case .markRead(let recordID, let sourceRevision):
            return await records.markRead(
                recordID: recordID,
                expectedRevision: sourceRevision
            )

        case .accept(let recordID, let sourceRevision):
            return await records.accept(
                recordID: recordID,
                expectedRevision: sourceRevision
            )

        case .decline(let recordID, let sourceRevision):
            return await records.decline(
                recordID: recordID,
                expectedRevision: sourceRevision
            )

        case .reply(let recordID, let sourceRevision, let text):
            return await records.reply(
                recordID: recordID,
                expectedRevision: sourceRevision,
                text: text
            )

        case .dismissed:
            return .ignored
        case .unknown:
            return .ignored
        }
    }
}

enum ActionResult: Sendable {
    case committed
    case stale
    case needsUnlock
    case needsAccount
    case failed
    case ignored
}

protocol NotificationRecordStore: Sendable {
    func open(recordID: String) async -> ActionResult
    func markRead(recordID: String, expectedRevision: Int) async -> ActionResult
    func accept(recordID: String, expectedRevision: Int) async -> ActionResult
    func decline(recordID: String, expectedRevision: Int) async -> ActionResult
    func reply(recordID: String, expectedRevision: Int, text: String) async -> ActionResult
}
~~~

The handler result is a domain result. It is not the same as the notification delegate completion.

## Recipe 12: Register for remote notifications

Registration is a device-token route, not a provider implementation.

~~~swift
import UIKit

final class RemoteNotificationRegistration: NSObject, UIApplicationDelegate {
    var onToken: ((Data) -> Void)?
    var onFailure: ((Error) -> Void)?

    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions:
            [UIApplication.LaunchOptionsKey: Any]? = nil
    ) -> Bool {
        application.registerForRemoteNotifications()
        return true
    }

    func application(
        _ application: UIApplication,
        didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data
    ) {
        onToken?(deviceToken)
    }

    func application(
        _ application: UIApplication,
        didFailToRegisterForRemoteNotificationsWithError error: Error
    ) {
        onFailure?(error)
    }
}

extension Data {
    var redactedHex: String {
        map { String(format: "%02x", $0) }.prefix(8).joined() + "…"
    }
}
~~~

Forward the current token securely to a provider and record the environment separately. Never print the full token.

## Recipe 13: Represent a small remote payload

Keep provider payloads versioned and opaque.

~~~swift
import Foundation

struct RemoteNotificationPayload: Encodable, Sendable {
    struct APS: Encodable, Sendable {
        let alert: Alert
        let sound: String?
        let badge: Int?
        let category: String?
        let threadID: String?
        let mutableContent: Int?
        let contentAvailable: Int?
        let interruptionLevel: String?
        let relevanceScore: Double?

        enum CodingKeys: String, CodingKey {
            case alert
            case sound
            case badge
            case category
            case threadID = "thread-id"
            case mutableContent = "mutable-content"
            case contentAvailable = "content-available"
            case interruptionLevel = "interruption-level"
            case relevanceScore = "relevance-score"
        }
    }

    struct Alert: Encodable, Sendable {
        let title: String?
        let body: String?
        let launchImage: String?
    }

    let aps: APS
    let schemaVersion: Int
    let eventID: String
    let recordID: String
    let sourceRevision: Int
}
~~~

The provider still owns APNs authentication, topic, environment, expiration, retry, and transport. This type only documents an app-side payload contract.

## Recipe 14: Redact notification content by policy

Make redaction deterministic before local scheduling or remote serialization.

~~~swift
struct NotificationRedactor: Sendable {
    func title(for record: NotificationRecord) -> String {
        switch record.privacyClass {
        case .public:
            return record.sourceTitle
        case .private, .sensitive, .redacted:
            return "You have an update"
        }
    }

    func body(for record: NotificationRecord) -> String {
        switch record.privacyClass {
        case .public:
            return record.sourceBody
        case .private, .sensitive, .redacted:
            return "Open the app to view the details."
        }
    }
}
~~~

Test this policy against locked, unlocked, shared-display, Watch, CarPlay, and accessibility announcement contexts.

## Recipe 15: Create a service-extension fallback

A notification service extension must always preserve safe original content.

~~~swift
import UserNotifications

final class NotificationService: UNNotificationServiceExtension {
    private var contentHandler: ((UNNotificationContent) -> Void)?
    private var bestAttemptContent: UNMutableNotificationContent?

    override func didReceive(
        _ request: UNNotificationRequest,
        withContentHandler contentHandler:
            @escaping (UNNotificationContent) -> Void
    ) {
        self.contentHandler = contentHandler
        bestAttemptContent = request.content.mutableCopy() as? UNMutableNotificationContent

        guard let content = bestAttemptContent else {
            contentHandler(request.content)
            return
        }

        Task {
            do {
                let transformed = try await transform(
                    content: content,
                    userInfo: request.content.userInfo
                )
                contentHandler(transformed)
            } catch {
                contentHandler(content)
            }
        }
    }

    override func serviceExtensionTimeWillExpire() {
        if let bestAttemptContent {
            contentHandler?(bestAttemptContent)
        }
    }

    private func transform(
        content: UNMutableNotificationContent,
        userInfo: [AnyHashable: Any]
    ) async throws -> UNNotificationContent {
        content.title = content.title.isEmpty ? "You have an update" : content.title
        return content
    }
}
~~~

Confirm the current extension lifecycle and concurrency behavior for the target SDK. Do not assume the extension has time for a network request or model generation.

## Recipe 16: Describe a content-extension projection

Keep the extension’s input small and immediate.

~~~swift
import UserNotifications
import UserNotificationsUI
import UIKit

final class NotificationContentViewController:
    UIViewController, UNNotificationContentExtension {
    @IBOutlet private weak var titleLabel: UILabel?
    @IBOutlet private weak var bodyLabel: UILabel?

    func didReceive(_ notification: UNNotification) {
        let content = notification.request.content
        titleLabel?.text = content.title
        bodyLabel?.text = content.body
    }

    func didReceive(
        _ response: UNNotificationResponse,
        completionHandler completion:
            @escaping (UNNotificationContentExtensionResponseOption) -> Void
    ) {
        completion(.dismiss)
    }
}
~~~

The extension target, storyboard/entry point, supported category, and system behavior must be tested separately. Do not use the main-app SwiftUI preview as evidence.

## Recipe 17: Map a communication proposal without faking identity

Keep the app-owned communication record separate from SiriKit object construction.

~~~swift
import Foundation

struct CommunicationNotificationInput: Sendable, Codable {
    enum Direction: String, Codable, Sendable {
        case incoming
        case outgoing
    }

    let communicationID: String
    let participantID: String
    let participantDisplayName: String
    let direction: Direction
    let kind: Kind
    let sourceRevision: Int

    enum Kind: String, Codable, Sendable {
        case message
        case call
    }
}

struct CommunicationNotificationBoundary {
    func validate(_ input: CommunicationNotificationInput) throws {
        guard !input.communicationID.isEmpty,
              !input.participantID.isEmpty,
              !input.participantDisplayName.isEmpty
        else {
            throw BoundaryError.missingIdentity
        }
        guard input.sourceRevision >= 0 else {
            throw BoundaryError.invalidRevision
        }
    }
}

enum BoundaryError: Error {
    case missingIdentity
    case invalidRevision
}
~~~

Construct INSendMessageIntent or INStartCallIntent only after this validation and after confirming the current SDK initializer, capability, Info.plist, and privacy requirements. An arbitrary app type cannot become system-recognized communication content merely by adopting a protocol name.

## Recipe 18: Validate a Foundation Models proposal

Treat model output as a draft with a strict allowlist.

~~~swift
import Foundation

struct NotificationProposal: Codable, Hashable, Sendable {
    let sourceRecordIDs: [String]
    let sourceRevision: Int
    let title: String
    let body: String
    let categoryIdentifier: String
    let actionIdentifiers: [String]
    let trigger: TriggerCandidate
    let interruption: InterruptionCandidate
    let privacyClass: PrivacyClass
    let modelRevision: String

    enum TriggerCandidate: Codable, Hashable, Sendable {
        case after(seconds: Double)
        case calendar(year: Int?, month: Int?, day: Int?, hour: Int?, minute: Int?)
        case none
    }

    enum InterruptionCandidate: String, Codable, Sendable {
        case passive
        case active
        case timeSensitive
        case critical
    }
}

struct NotificationProposalValidator: Sendable {
    let categories: Set<String>
    let actions: Set<String>
    let currentSourceRevision: Int
    let allowsTimeSensitive: Bool
    let allowsCritical: Bool

    func validate(_ proposal: NotificationProposal) -> Result<NotificationProposal, ProposalError> {
        guard !proposal.sourceRecordIDs.isEmpty else {
            return .failure(.missingSource)
        }
        guard proposal.sourceRevision == currentSourceRevision else {
            return .failure(.staleSource)
        }
        guard categories.contains(proposal.categoryIdentifier) else {
            return .failure(.unknownCategory)
        }
        guard Set(proposal.actionIdentifiers).isSubset(of: actions) else {
            return .failure(.unknownAction)
        }
        guard proposal.interruption != .timeSensitive || allowsTimeSensitive else {
            return .failure(.urgencyNotAllowed)
        }
        guard proposal.interruption != .critical || allowsCritical else {
            return .failure(.urgencyNotAllowed)
        }
        guard proposal.body.count <= 240 else {
            return .failure(.tooLong)
        }
        return .success(proposal)
    }
}

enum ProposalError: Error {
    case missingSource
    case staleSource
    case unknownCategory
    case unknownAction
    case urgencyNotAllowed
    case tooLong
}
~~~

Use SystemLanguageModel availability and a LanguageModelSession only after this app-owned schema exists. Guided generation can produce structured output, but the app still validates source revision, privacy, categories, actions, timing, and urgency.

## Recipe 19: Gate model availability

Always provide a deterministic fallback.

~~~swift
import FoundationModels

@MainActor
final class NotificationIntelligenceModel: ObservableObject {
    private let model = SystemLanguageModel.default
    @Published private(set) var status: Status = .checking

    enum Status: Sendable {
        case checking
        case available
        case unavailable(String)
    }

    func refresh() {
        switch model.availability {
        case .available:
            status = .available
        case .unavailable(let reason):
            status = .unavailable(String(describing: reason))
        @unknown default:
            status = .unavailable("Unknown availability")
        }
    }
}
~~~

Do not show an empty AI screen when the model is unavailable. Offer manual compose, deterministic scheduling, or the normal app route.

## Recipe 20: Use a single proposal task and cancel stale work

Tie generation to source revision.

~~~swift
import Foundation

@MainActor
final class NotificationProposalController: ObservableObject {
    @Published private(set) var proposal: NotificationProposal?
    @Published private(set) var isGenerating = false

    private var task: Task<Void, Never>?
    private var generationID = UUID()

    func generate(
        source: NotificationRecord,
        model: @Sendable @escaping (NotificationRecord) async throws -> NotificationProposal
    ) {
        task?.cancel()
        let currentGeneration = UUID()
        generationID = currentGeneration
        isGenerating = true
        proposal = nil

        task = Task {
            do {
                let result = try await model(source)
                guard !Task.isCancelled, generationID == currentGeneration else {
                    return
                }
                proposal = result
            } catch {
                guard !Task.isCancelled, generationID == currentGeneration else {
                    return
                }
                proposal = nil
            }
            isGenerating = false
        }
    }

    func cancel() {
        task?.cancel()
        task = nil
        generationID = UUID()
        isGenerating = false
        proposal = nil
    }
}
~~~

The model task does not schedule or send anything. The user review and deterministic revalidation happen after generation.

## Recipe 21: Build a SwiftUI settings screen

Use native hierarchy for the app-owned route.

~~~swift
import SwiftUI
import UserNotifications

struct NotificationSettingsView: View {
    @StateObject private var settings = NotificationSettingsModel()
    @State private var showReview = false
    @State private var reminderEnabled = true

    var body: some View {
        NavigationStack {
            Form {
                Section("System access") {
                    AuthorizationSummary(snapshot: settings.snapshot)
                    Button("Open Settings") {
                        openSystemSettings()
                    }
                }

                Section("App preferences") {
                    Toggle("Allow reminders to be scheduled", isOn: $reminderEnabled)
                    Text("This preference does not change iPhone notification authorization.")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }

                Section("Privacy") {
                    Label("Lock-screen text is redacted for sensitive items", systemImage: "lock")
                    NavigationLink("Preview policy") {
                        NotificationPreviewPolicyView()
                    }
                }

                Section("Review") {
                    Button("Review notification draft") {
                        showReview = true
                    }
                }
            }
            .navigationTitle("Notifications")
            .task {
                await settings.refresh()
            }
            .refreshable {
                await settings.refresh()
            }
            .sheet(isPresented: $showReview) {
                NotificationDraftReviewView()
            }
        }
    }

    private func openSystemSettings() {
        // Use the documented app-settings URL route for the named target.
    }
}

struct AuthorizationSummary: View {
    let snapshot: NotificationSettingsSnapshot?

    var body: some View {
        HStack {
            Image(systemName: "bell")
            VStack(alignment: .leading) {
                Text(summaryTitle)
                Text(summaryDetail)
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }
        }
    }

    private var summaryTitle: String {
        guard let snapshot else { return "Checking notification settings" }
        switch snapshot.authorization {
        case .authorized:
            return "Notifications are allowed"
        case .provisional:
            return "Notifications are provisional"
        case .denied:
            return "Notifications are off"
        case .notDetermined:
            return "Notifications are not set up"
        case .ephemeral:
            return "Notifications are temporary"
        @unknown default:
            return "Notification status is unknown"
        }
    }

    private var summaryDetail: String {
        guard let snapshot else { return "Refresh to read current system state." }
        return "Alert: " + String(describing: snapshot.alert)
    }
}
~~~

Keep the system state summary read-only and let the system own the actual setting change.

## Recipe 22: Add a restrained Liquid Glass review shell

Use a functional glass role, not a fake notification banner.

~~~swift
import SwiftUI

struct NotificationDraftReviewView: View {
    @Environment(\.dismiss) private var dismiss
    let proposal: NotificationProposal?
    let onSchedule: () -> Void

    var body: some View {
        NavigationStack {
            VStack(alignment: .leading, spacing: 20) {
                Text("Review notification")
                    .font(.title2.weight(.semibold))

                if let proposal {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(proposal.title)
                            .font(.headline)
                        Text(proposal.body)
                            .foregroundStyle(.secondary)
                        Text("Suggested from source revision " + String(proposal.sourceRevision))
                            .font(.footnote)
                            .foregroundStyle(.tertiary)
                    }
                } else {
                    ContentUnavailableView(
                        "No draft",
                        systemImage: "bell.slash",
                        description: Text("Write a notification manually or refresh the source.")
                    )
                }

                HStack {
                    Button("Discard") {
                        dismiss()
                    }
                    .buttonStyle(.borderless)

                    Spacer()

                    Button("Schedule") {
                        onSchedule()
                        dismiss()
                    }
                    .buttonStyle(.glassProminent)
                    .disabled(proposal == nil)
                }
                .padding()
                .glassEffect(in: .rect(cornerRadius: 22))
            }
            .padding()
            .navigationTitle("Draft")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}
~~~

Confirm the exact Liquid Glass API and availability for the selected SDK. Test the shell when transparency and motion effects are reduced.

## Recipe 23: Create a notification attachment safely

Attachments need a local readable file and supported type.

~~~swift
import UserNotifications

struct NotificationAttachmentFactory {
    static func make(
        identifier: String,
        fileURL: URL
    ) throws -> UNNotificationAttachment {
        try UNNotificationAttachment(
            identifier: identifier,
            url: fileURL,
            options: [
                UNNotificationAttachmentOptionsThumbnailHiddenKey: true
            ]
        )
    }
}
~~~

Do not pass a remote URL directly. Download in the documented service-extension route, validate size and type, then attach. If the file is unavailable, deliver a text-only fallback.

## Recipe 24: Separate Live Activity state

Do not reuse ordinary notification userInfo as ongoing activity truth.

~~~swift
import ActivityKit

struct DeliveryActivityAttributes: ActivityAttributes {
    let recordID: String

    struct ContentState: Codable, Hashable {
        let status: String
        let progress: Double?
        let revision: Int
        let staleDate: Date?
    }
}

struct DeliveryActivityProjection: Sendable, Hashable {
    let recordID: String
    let status: String
    let revision: Int
}
~~~

The server, ActivityKit content-state schema, supported device surface, and stale/end policy require separate proof. A Live Activity update is not ordinary alert delivery.

## Recipe 25: Capture redacted evidence

Record layer-specific results without secrets.

~~~swift
import Foundation

struct NotificationEvidence: Codable, Sendable {
    enum Layer: String, Codable, Sendable {
        case settings
        case localRequest
        case provider
        case apns
        case device
        case systemPresentation
        case action
        case communication
        case extension
        case model
        case accessibility
        case release
    }

    let id: UUID
    let layer: Layer
    let result: String
    let recordID: String?
    let sourceRevision: Int?
    let eventID: String?
    let deviceModel: String?
    let osBuild: String?
    let capturedAt: Date
    let redactedNotes: String
}
~~~

Do not store full device tokens, APNs credentials, payment-like secrets, raw notification body text, text-input replies, or decrypted service-extension payloads in evidence.

## Recipe 26: Failure matrix as typed state

Make unknown delivery explicit.

~~~swift
enum NotificationDeliveryState: String, Codable, Sendable {
    case notRequested
    case permissionDenied
    case scheduled
    case providerQueued
    case apnsAccepted
    case deviceReceiptUnknown
    case presentedUnknown
    case actionObserved
    case domainCommitted
    case canceled
    case stale
    case fallback
}

struct NotificationStatus: Codable, Sendable {
    let recordID: String
    let sourceRevision: Int
    var state: NotificationDeliveryState
    var updatedAt: Date
    var reason: String?
}
~~~

Do not collapse providerQueued, apnsAccepted, presentedUnknown, and domainCommitted into “sent.”

## Recipe 27: Manual fallback when AI is unavailable

The app must remain useful without Foundation Models.

~~~swift
import SwiftUI

struct NotificationComposeFallbackView: View {
    @State private var title = ""
    @State private var body = ""

    var body: some View {
        Form {
            TextField("Title", text: $title)
            TextEditor(text: $body)
                .frame(minHeight: 140)
            Text("Smart suggestions are unavailable. You can write the notification yourself.")
                .font(.footnote)
                .foregroundStyle(.secondary)
        }
        .navigationTitle("Compose")
    }
}
~~~

AI availability is a feature state, not an excuse to hide the deterministic workflow.

## Recipe 28: Verification checklist in code review

Use this as a handoff checklist:

~~~text
Target:
SDK:
Deployment target:
Device:
OS build:
Authorization/settings snapshot:
Category registry revision:
Action registry revision:
Local request identifiers:
Provider/APNs environment:
Payload schema:
Service extension:
Content extension:
Communication intent:
Focus authorization:
Live Activity route:
Model availability:
Model/prompt/schema revision:
Source revision:
User review:
Accessibility task:
Archive version/build:
TestFlight/release result:
Known unknowns:
~~~

## Sources

- [User Notifications](https://developer.apple.com/documentation/usernotifications)
- [UNUserNotificationCenter](https://developer.apple.com/documentation/usernotifications/unusernotificationcenter)
- [UNUserNotificationCenterDelegate](https://developer.apple.com/documentation/usernotifications/unusernotificationcenterdelegate)
- [Asking permission to use notifications](https://developer.apple.com/documentation/usernotifications/asking-permission-to-use-notifications)
- [UNNotificationSettings](https://developer.apple.com/documentation/usernotifications/unnotificationsettings)
- [Scheduling a notification locally from your app](https://developer.apple.com/documentation/usernotifications/scheduling-a-notification-locally-from-your-app)
- [UNNotificationRequest](https://developer.apple.com/documentation/usernotifications/unnotificationrequest)
- [UNMutableNotificationContent](https://developer.apple.com/documentation/usernotifications/unmutablenotificationcontent)
- [UNNotificationAttachment](https://developer.apple.com/documentation/usernotifications/unnotificationattachment)
- [Declaring your actionable notification types](https://developer.apple.com/documentation/usernotifications/declaring-your-actionable-notification-types)
- [UNNotificationCategory](https://developer.apple.com/documentation/usernotifications/unnotificationcategory)
- [UNNotificationAction](https://developer.apple.com/documentation/usernotifications/unnotificationaction)
- [UNTextInputNotificationAction](https://developer.apple.com/documentation/usernotifications/untextinputnotificationaction)
- [Handling notifications and notification-related actions](https://developer.apple.com/documentation/usernotifications/handling-notifications-and-notification-related-actions)
- [Generating a remote notification](https://developer.apple.com/documentation/usernotifications/generating-a-remote-notification)
- [Setting up a remote notification server](https://developer.apple.com/documentation/usernotifications/setting-up-a-remote-notification-server)
- [Registering your app with APNs](https://developer.apple.com/documentation/usernotifications/registering-your-app-with-apns)
- [Pushing background updates to your app](https://developer.apple.com/documentation/usernotifications/pushing-background-updates-to-your-app)
- [Modifying content in newly delivered notifications](https://developer.apple.com/documentation/usernotifications/modifying-content-in-newly-delivered-notifications)
- [UNNotificationServiceExtension](https://developer.apple.com/documentation/usernotifications/unnotificationserviceextension)
- [User Notifications UI](https://developer.apple.com/documentation/usernotificationsui)
- [Customizing the appearance of notifications](https://developer.apple.com/documentation/usernotificationsui/customizing-the-appearance-of-notifications)
- [UNNotificationContentExtension](https://developer.apple.com/documentation/usernotificationsui/unnotificationcontentextension)
- [Handling Communication Notifications and Focus Status Updates](https://developer.apple.com/documentation/UserNotifications/handling-communication-notifications-and-focus-status-updates)
- [INSendMessageIntent](https://developer.apple.com/documentation/intents/insendmessageintent)
- [INStartCallIntent](https://developer.apple.com/documentation/intents/instartcallintent)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [Starting and updating Live Activities with ActivityKit push notifications](https://developer.apple.com/documentation/ActivityKit/starting-and-updating-live-activities-with-activitykit-push-notifications)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Generating content and performing tasks with Foundation Models](https://developer.apple.com/documentation/foundationmodels/generating-content-and-performing-tasks-with-foundation-models)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
