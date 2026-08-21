# SwiftUI Watch Connectivity and watchOS companion review recipes

These are compile-oriented route sketches for a named iOS target, watchOS target, and optional WidgetKit extension. They are not compiled in this documentation workspace and do not prove target configuration, pairing, reachability, transfer timing, Smart Stack placement, model availability, accessibility, privacy, energy, or release readiness.

Read the [companion review](../42-framework-deep-dives/107-swiftui-watch-connectivity-watchos-companion-review.md), [design guide](../21-design-deep-dives/135-swiftui-watch-connectivity-watchos-companion-review-design.md), [route](../50-capability-recipes/138-swiftui-watch-connectivity-watchos-companion-review-route.md), and [proof matrix](../60-verification/132-swiftui-watch-connectivity-watchos-companion-review-proof-matrix.md) first. Confirm current SDK signatures, target availability, entitlements, bundle relationships, and device behavior before using any sketch.

## Recipe 1: name the companion topology

Keep the product topology explicit in configuration and documentation.

~~~swift
import Foundation

struct CompanionTopology: Sendable, Equatable {
    enum Kind: Sendable {
        case watchOnly
        case iPhoneWithWatch
        case existingIPhonePlusWatch
        case independentWatchWithRelatedIPhone
    }

    let kind: Kind
    let iPhoneBundleID: String?
    let watchBundleID: String
    let widgetBundleID: String?
    let appGroupID: String?
    let companionIdentifier: String?
}
~~~

Verify the actual project, information property lists, entitlements, and archive. Do not treat this struct as proof that Xcode created the intended target graph.

## Recipe 2: activate WCSession on each target

WCSession is configured independently in the iOS app and watchOS app.

~~~swift
import WatchConnectivity

final class CompanionSessionBridge: NSObject, WCSessionDelegate {
    private let session: WCSession

    init(session: WCSession = .default) {
        self.session = session
        super.init()
    }

    func start() {
        guard WCSession.isSupported() else { return }
        session.delegate = self
        session.activate()
    }

    func session(
        _ session: WCSession,
        activationDidCompleteWith activationState: WCSessionActivationState,
        error: Error?
    ) {
        // Publish activationState and error to a state owner.
    }

    func sessionDidBecomeInactive(_ session: WCSession) {
        // iOS: stop initiating new transfers for the old active watch.
    }

    func sessionDidDeactivate(_ session: WCSession) {
        // iOS: activate again after the previous watch is fully deactivated.
        session.activate()
    }

    func sessionReachabilityDidChange(_ session: WCSession) {
        // Publish reachability; do not call it domain sync.
    }
}
~~~

Register a long-lived bridge from the target’s app lifecycle. Do not create a new delegate for every view.

## Recipe 3: project session observations

Keep pairing, activation, installation, and reachability separate.

~~~swift
import WatchConnectivity

struct CompanionObservation: Sendable, Equatable {
    let supported: Bool
    let paired: Bool
    let counterpartInstalled: Bool
    let activeWatchInstalled: Bool
    let activationState: WCSessionActivationState
    let reachable: Bool
    let complicationEnabled: Bool
    let observedAt: Date
}

func observe(_ session: WCSession, now: Date = .now) -> CompanionObservation {
    CompanionObservation(
        supported: WCSession.isSupported(),
        paired: session.isPaired,
        counterpartInstalled: session.isCompanionAppInstalled,
        activeWatchInstalled: session.isWatchAppInstalled,
        activationState: session.activationState,
        reachable: session.isReachable,
        complicationEnabled: session.isComplicationEnabled,
        observedAt: now
    )
}
~~~

This is an observation of the transport, not a proof of account identity or domain freshness.

## Recipe 4: define a versioned envelope

Use a typed envelope at the domain boundary.

~~~swift
import Foundation

struct CompanionEnvelope<Payload: Codable & Sendable>: Codable, Sendable {
    enum Kind: String, Codable, Sendable {
        case snapshot
        case event
        case file
        case complication
        case commandResult
    }

    let schema: Int
    let kind: Kind
    let source: String
    let installationID: String
    let accountScope: String?
    let revision: Int64
    let eventID: String?
    let issuedAt: Date
    let expiresAt: Date?
    let payload: Payload
}

struct PendingItem: Codable, Sendable, Equatable {
    let id: UUID
    let title: String
    let completed: Bool
}
~~~

Reject unsupported schema versions instead of silently decoding partial data.

## Recipe 5: encode a dictionary payload

Watch Connectivity methods accept dictionaries. Keep encoding centralized and bounded.

~~~swift
import Foundation

enum CompanionCodec {
    static func encode<Payload: Encodable>(
        _ envelope: CompanionEnvelope<Payload>
    ) throws -> [String: Any] {
        let data = try PropertyListEncoder().encode(envelope)
        return [
            "schema": envelope.schema,
            "kind": envelope.kind.rawValue,
            "data": data
        ]
    }

    static func decode<Payload: Decodable>(
        _ type: Payload.Type,
        from dictionary: [String: Any]
    ) throws -> CompanionEnvelope<Payload> {
        guard let data = dictionary["data"] as? Data else {
            throw CocoaError(.fileReadCorruptFile)
        }
        return try PropertyListDecoder().decode(
            CompanionEnvelope<Payload>.self,
            from: data
        )
    }
}
~~~

Confirm the chosen encoder, payload types, and dictionary values are accepted by the deployment targets. Validate size, account scope, and revision after decoding.

## Recipe 6: send an immediate message

Use immediate messaging only for a reachable counterpart and a user-visible request/reply.

~~~swift
import WatchConnectivity

func requestCurrentLabel(
    session: WCSession,
    recordID: String,
    onResult: @escaping @Sendable (Result<String, Error>) -> Void
) {
    guard session.isReachable else {
        onResult(.failure(URLError(.cannotConnectToHost)))
        return
    }

    session.sendMessage(
        ["kind": "current-label", "recordID": recordID],
        replyHandler: { reply in
            guard let label = reply["label"] as? String else {
                onResult(.failure(CocoaError(.propertyListReadCorrupt)))
                return
            }
            onResult(.success(label))
        },
        errorHandler: { error in
            onResult(.failure(error))
        }
    )
}
~~~

The reply handler does not prove that a server mutation occurred. If the command matters, use an explicit command result and durable reconciliation.

## Recipe 7: replace latest context

Use application context for current state, not an event log.

~~~swift
func sendLatestSnapshot(
    session: WCSession,
    envelope: CompanionEnvelope<[PendingItem]>
) throws {
    let dictionary = try CompanionCodec.encode(envelope)
    try session.updateApplicationContext(dictionary)
}
~~~

Keep the latest sent revision locally. If a new context overwrites an older one, that is expected. The receiver must compare revisions and scopes before replacing its projection.

## Recipe 8: queue a user-info event

Use transferUserInfo for small events that should not be collapsed.

~~~swift
func queueCompletion(
    session: WCSession,
    itemID: String,
    revision: Int64,
    installationID: String
) throws {
    let envelope = CompanionEnvelope(
        schema: 1,
        kind: .event,
        source: "watch",
        installationID: installationID,
        accountScope: nil,
        revision: revision,
        eventID: UUID().uuidString,
        issuedAt: .now,
        expiresAt: nil,
        payload: ["operation": "complete", "itemID": itemID]
    )
    let dictionary = try CompanionCodec.encode(envelope)
    session.transferUserInfo(dictionary)
}
~~~

Persist the event ID and pending state before calling the transfer method. The queue is not the domain commit.

## Recipe 9: transfer a file safely

Move received files into app-owned storage before decoding.

~~~swift
import Foundation

struct ReceivedFileReceipt: Codable, Sendable {
    let transferID: String
    let sourceURL: URL
    let receivedAt: Date
}

actor FileImportStore {
    private let directory: URL
    private var receipts = Set<String>()

    init(directory: URL) {
        self.directory = directory
    }

    func importFile(
        transferID: String,
        fileURL: URL,
        expectedExtension: String,
        expectedRevision: Int64
    ) throws -> ReceivedFileReceipt {
        guard !receipts.contains(transferID) else {
            throw CocoaError(.fileReadNoSuchFile)
        }
        guard fileURL.pathExtension.lowercased() == expectedExtension else {
            throw CocoaError(.fileReadCorruptFile)
        }

        let destination = directory.appendingPathComponent(transferID)
        try FileManager.default.copyItem(at: fileURL, to: destination)
        receipts.insert(transferID)

        return ReceivedFileReceipt(
            transferID: transferID,
            sourceURL: destination,
            receivedAt: .now
        )
    }
}
~~~

Add real byte limits, checksum validation, schema checks, account scope, cleanup, and a durable receipt before production use.

## Recipe 10: receive context and user-info

Normalize callbacks before applying them to state.

~~~swift
final class ReceivingBridge: CompanionSessionBridge {
    private let state = CompanionStateStore()

    override func session(
        _ session: WCSession,
        didReceiveApplicationContext applicationContext: [String : Any]
    ) {
        Task {
            await state.receiveContext(applicationContext)
        }
    }

    override func session(
        _ session: WCSession,
        didReceiveUserInfo userInfo: [String : Any] = [:]
    ) {
        Task {
            await state.receiveEvent(userInfo)
        }
    }
}
~~~

The exact delegate declarations vary by SDK and language mode. Confirm the current signatures. The callback should capture and hand off quickly.

## Recipe 11: reject stale and duplicate input

Use a state owner for revisions and event IDs.

~~~swift
actor CompanionStateStore {
    private var currentRevision: Int64 = 0
    private var appliedEventIDs = Set<String>()

    func acceptSnapshot(
        revision: Int64,
        scopeMatches: Bool
    ) -> Bool {
        guard scopeMatches, revision >= currentRevision else { return false }
        currentRevision = revision
        return true
    }

    func acceptEvent(
        eventID: String,
        revision: Int64,
        scopeMatches: Bool
    ) -> Bool {
        guard scopeMatches else { return false }
        guard appliedEventIDs.insert(eventID).inserted else { return false }
        currentRevision = max(currentRevision, revision)
        return true
    }
}
~~~

Persist the cursor and event IDs in production. An in-memory actor only demonstrates the reducer shape.

## Recipe 12: handle SwiftUI background delivery

For supported watchOS background tasks, keep the closure bounded and cancellable.

~~~swift
import SwiftUI

@main
struct CompanionWatchApp: App {
    var body: some Scene {
        WindowGroup {
            WatchRootView()
        }
        .backgroundTask(.appRefresh("companion-refresh")) { context in
            await withTaskCancellationHandler {
                await CompanionRefreshWorker().run()
            } onCancel: {
                CompanionRefreshWorker().checkpointCancellation()
            }
        }
    }
}
~~~

Confirm task identifiers and overloads for the deployment target. Finish quickly, persist before long work, and use a foreground recovery route when the task is throttled or expires.

## Recipe 13: handle delegate-based watch background work

A delegate-based route must complete every task it receives.

~~~swift
import WatchKit

final class WatchAppDelegate: NSObject, WKApplicationDelegate {
    func handle(_ backgroundTasks: Set<WKRefreshBackgroundTask>) {
        for task in backgroundTasks {
            switch task {
            case let connectivityTask as WKWatchConnectivityRefreshBackgroundTask:
                Task {
                    await CompanionRefreshWorker().receiveConnectivity()
                    task.setTaskCompletedWithSnapshot(false)
                }
            default:
                task.setTaskCompletedWithSnapshot(false)
            }
        }
    }
}
~~~

Use the current WatchKit task API and lifecycle configuration for the selected target. Do not leave tasks open while waiting for a network request or model generation.

## Recipe 14: persist a widget projection

The widget extension should read a compact, versioned projection.

~~~swift
import Foundation

struct WidgetProjection: Codable, Sendable {
    let schema: Int
    let revision: Int64
    let title: String
    let status: String
    let updatedAt: Date
    let expiresAt: Date?
    let redactedTitle: String
}

struct ProjectionStore {
    let url: URL

    func load() throws -> WidgetProjection {
        let data = try Data(contentsOf: url)
        return try JSONDecoder().decode(WidgetProjection.self, from: data)
    }

    func save(_ projection: WidgetProjection) throws {
        let data = try JSONEncoder().encode(projection)
        try data.write(to: url, options: [.atomic])
    }
}
~~~

The actual App Group URL must be resolved from the configured container. Do not hard-code an example group identifier.

## Recipe 15: build a timeline from projection state

Use WidgetKit to render a safe projection, not the live app model.

~~~swift
import WidgetKit
import SwiftUI

struct CompanionEntry: TimelineEntry {
    let date: Date
    let projection: WidgetProjection?
    let error: String?
}

struct CompanionTimelineProvider: TimelineProvider {
    func placeholder(in context: Context) -> CompanionEntry {
        CompanionEntry(date: .now, projection: nil, error: nil)
    }

    func getSnapshot(
        in context: Context,
        completion: @escaping (CompanionEntry) -> Void
    ) {
        completion(loadEntry())
    }

    func getTimeline(
        in context: Context,
        completion: @escaping (Timeline<CompanionEntry>) -> Void
    ) {
        let entry = loadEntry()
        let refresh = entry.projection?.expiresAt ?? .now.addingTimeInterval(900)
        completion(Timeline(entries: [entry], policy: .after(refresh)))
    }

    private func loadEntry() -> CompanionEntry {
        do {
            return CompanionEntry(
                date: .now,
                projection: try ProjectionStore(url: projectionURL()).load(),
                error: nil
            )
        } catch {
            return CompanionEntry(date: .now, projection: nil, error: "Unavailable")
        }
    }

    private func projectionURL() -> URL {
        fatalError("Resolve from the configured App Group")
    }
}
~~~

Replace the placeholder URL resolution and choose a family-specific view. The timeline date is not a promise that the system will render at that instant.

## Recipe 16: model the complication view

Keep the view legible across family and rendering contexts.

~~~swift
struct CompanionComplicationView: View {
    let entry: CompanionEntry

    var body: some View {
        if let projection = entry.projection {
            VStack(alignment: .leading) {
                Text(projection.title)
                    .font(.headline)
                    .lineLimit(1)
                Text(projection.status)
                    .font(.caption2)
                    .lineLimit(1)
            }
            .privacySensitive()
        } else {
            Label("Unavailable", systemImage: "questionmark")
        }
    }
}
~~~

Use the correct WidgetKit configuration and family-specific layout. Confirm whether privacySensitive and other modifiers behave as intended on the selected OS and watch surface.

## Recipe 17: request a reload after applying state

A reload request is a hint, not proof of immediate rendering.

~~~swift
import WidgetKit

func requestCompanionProjectionRefresh(kind: String) {
    WidgetCenter.shared.reloadTimelines(ofKind: kind)
}
~~~

Record the projection revision and the reload request separately. A widget can show the new value later or remain stale if the system defers the request.

## Recipe 18: sketch a Smart Stack relevance route

Treat relevance as a system hint and keep the visible entry safe.

~~~swift
import WidgetKit

struct CompanionRelevanceEntry: TimelineEntry {
    let date: Date
    let relevance: TimelineEntryRelevance
    let projection: WidgetProjection
}

func relevance(for projection: WidgetProjection) -> TimelineEntryRelevance {
    TimelineEntryRelevance(score: 0.5)
}
~~~

The current WidgetKit API for watchOS relevance entries may require a specific provider and configuration type. Confirm the exact deployment target and provider protocol before using this sketch. Test the widget when it is not elevated, pinned, stale, tinted, and redacted.

## Recipe 19: define a short App Intent action

The action should resolve a stable record, validate revision, and return a typed result.

~~~swift
import AppIntents

struct MarkCompanionItemComplete: AppIntent {
    static var title: LocalizedStringResource = "Mark Item Complete"

    @Parameter(title: "Item ID")
    var itemID: String

    @Parameter(title: "Expected Revision")
    var expectedRevision: Int64

    func perform() async throws -> some IntentResult & ProvidesDialog {
        let result = try await CompanionCommandService().complete(
            itemID: itemID,
            expectedRevision: expectedRevision
        )

        switch result {
        case .applied:
            return .result(dialog: "Saved.")
        case .pending:
            return .result(dialog: "Waiting to sync.")
        case .conflict:
            return .result(dialog: "This item changed. Review it in the app.")
        }
    }
}
~~~

Make the command idempotent, authorized, and safe if invoked more than once. Confirm App Intent availability in the widget and watch targets.

## Recipe 20: hand off a larger task

Preserve the record and expected revision when opening the iPhone route.

~~~swift
import Foundation

struct CompanionHandoff: Codable, Sendable {
    let recordID: String
    let expectedRevision: Int64
    let source: String
    let pendingEventID: String?
}

func handoffURL(_ handoff: CompanionHandoff) -> URL? {
    var components = URLComponents()
    components.scheme = "example"
    components.host = "companion"
    components.path = "/review"
    components.queryItems = [
        URLQueryItem(name: "record", value: handoff.recordID),
        URLQueryItem(name: "revision", value: String(handoff.expectedRevision)),
        URLQueryItem(name: "source", value: handoff.source),
        URLQueryItem(name: "event", value: handoff.pendingEventID)
    ]
    return components.url
}
~~~

Replace the example scheme with a configured universal-link or app route. Validate all incoming values and route to a known screen.

## Recipe 21: gate a model proposal

Make availability and fallback explicit.

~~~swift
import Foundation
import FoundationModels

struct PriorityProposal: Codable, Sendable {
    let sourceRevision: Int64
    let candidate: String
    let reason: String
}

enum ProposalState: Sendable {
    case unavailable
    case fallback(String)
    case candidate(PriorityProposal)
}

func proposalState(
    sourceRevision: Int64,
    sourceTitle: String
) -> ProposalState {
    let model = SystemLanguageModel.default
    guard model.isAvailable else {
        return .fallback(sourceTitle)
    }

    return .candidate(
        PriorityProposal(
            sourceRevision: sourceRevision,
            candidate: sourceTitle,
            reason: "Candidate requires review."
        )
    )
}
~~~

This is a route sketch, not a claim that Foundation Models is available on every watchOS target. Check the actual SDK, deployment target, device, locale, region, and model readiness. Revalidate the source revision before committing.

## Recipe 22: keep AI out of WidgetKit rendering

Persist a validated result before the widget reads it.

~~~swift
struct ApprovedProjection: Codable, Sendable {
    let revision: Int64
    let displayText: String
    let approvedByUser: Bool
    let sourceRevision: Int64
}

func approve(
    proposal: PriorityProposal,
    currentSourceRevision: Int64
) throws -> ApprovedProjection {
    guard proposal.sourceRevision == currentSourceRevision else {
        throw CocoaError(.validationMissingMandatoryProperty)
    }
    guard proposal.candidate.count <= 32 else {
        throw CocoaError(.validationNumberTooLarge)
    }

    return ApprovedProjection(
        revision: currentSourceRevision + 1,
        displayText: proposal.candidate,
        approvedByUser: true,
        sourceRevision: currentSourceRevision
    )
}
~~~

The widget renders ApprovedProjection or a deterministic source projection. It does not run a model, choose an account, or commit a domain mutation.

## Recipe 23: compose a native watch action shell

Keep the interaction focused and make state obvious.

~~~swift
import SwiftUI

struct CompanionActionView: View {
    let title: String
    let status: String
    let action: () -> Void

    var body: some View {
        VStack(spacing: 8) {
            Text(title)
                .font(.headline)
                .multilineTextAlignment(.center)

            Text(status)
                .font(.caption)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)

            Button("Complete", action: action)
                .buttonStyle(.borderedProminent)
        }
        .padding()
    }
}
~~~

Apply Liquid Glass only through supported native APIs and only if it improves the action hierarchy. Test the same view with reduced transparency, reduced motion, larger text, VoiceOver, and system tint.

## Recipe 24: redacted projection

Keep locked and Always On output safe.

~~~swift
struct PrivacySafeProjection {
    let title: String
    let redactedTitle: String
    let isSensitive: Bool
}

func displayTitle(
    _ projection: PrivacySafeProjection,
    isLockedOrAlwaysOn: Bool
) -> String {
    if isLockedOrAlwaysOn && projection.isSensitive {
        return projection.redactedTitle
    }
    return projection.title
}
~~~

Use the system’s privacy behavior and test actual watch surfaces. A custom boolean is only an application policy input.

## Recipe 25: test transfer reducers

Test semantics without pretending to test pairing.

~~~swift
import XCTest

final class CompanionReducerTests: XCTestCase {
    func testOlderContextCannotRollBackProjection() throws {
        let store = TestProjectionStore()
        XCTAssertTrue(store.accept(revision: 42, title: "New"))
        XCTAssertFalse(store.accept(revision: 41, title: "Old"))
        XCTAssertEqual(store.title, "New")
    }

    func testDuplicateEventIsIdempotent() throws {
        let store = TestProjectionStore()
        XCTAssertTrue(store.apply(eventID: "event-1"))
        XCTAssertFalse(store.apply(eventID: "event-1"))
    }
}
~~~

Add fixtures for wrong account scope, unsupported schema, expired file, conflict, cancellation, model unavailable, and account deletion.

## Recipe 26: test widget states

Use fixture projections for every supported context.

~~~swift
struct WidgetFixture {
    let name: String
    let projection: WidgetProjection?
    let locked: Bool
    let renderingMode: String
}

let widgetFixtures = [
    WidgetFixture(name: "fresh", projection: freshProjection(), locked: false, renderingMode: "fullColor"),
    WidgetFixture(name: "stale", projection: staleProjection(), locked: false, renderingMode: "fullColor"),
    WidgetFixture(name: "redacted", projection: sensitiveProjection(), locked: true, renderingMode: "accented"),
    WidgetFixture(name: "empty", projection: nil, locked: false, renderingMode: "fullColor")
]
~~~

Preview fixtures can prove layout and copy. They cannot prove Smart Stack placement, timeline budget, or physical appearance.

## Recipe 27: run the paired-device matrix

Record a test sheet rather than a single screenshot.

~~~swift
struct CompanionRunRecord: Codable, Sendable {
    let build: String
    let phoneModel: String
    let watchModel: String
    let iOSVersion: String
    let watchOSVersion: String
    let paired: Bool
    let activationState: String
    let reachableAtStart: Bool
    let transferKinds: [String]
    let backgroundDeliveryObserved: Bool
    let widgetInstalled: Bool
    let accessibilityChecks: [String]
    let failures: [String]
    let artifactPath: String
}
~~~

Run active, inactive, unreachable, suspended, terminated, delayed, duplicate, account-change, and reinstall cases. Attach logs or screenshots with timestamps and redacted identifiers.

## Recipe 28: inspect the release artifact

Use archive evidence for target and entitlement claims.

~~~bash
xcodebuild -scheme ExampleApp -configuration Release archive -archivePath /tmp/ExampleApp.xcarchive
plutil -p /tmp/ExampleApp.xcarchive/Info.plist
find /tmp/ExampleApp.xcarchive/Products/Applications -maxdepth 5 -type f -name Info.plist -print
~~~

The command is a starting point. Verify the actual archive path, signing, embedded watch app, widget extension, bundle identifiers, companion keys, App Groups, and supported device families. Do not call the route released from a simulator build.

## Recipe 29: handoff checklist

Before implementation:

- name the truth owner;
- select the target topology;
- select each transfer by semantics;
- define scope, revision, event ID, and expiry;
- define shared projection and privacy redaction;
- define WidgetKit family and Smart Stack fallback;
- define App Intent result and idempotency;
- define AI availability and deterministic fallback;
- define paired-device and release evidence.

## Sources

- [Watch Connectivity](https://developer.apple.com/documentation/watchconnectivity)
- [WCSession](https://developer.apple.com/documentation/watchconnectivity/wcsession)
- [WCSessionDelegate](https://developer.apple.com/documentation/watchconnectivity/wcsessiondelegate)
- [Transferring data with Watch Connectivity](https://developer.apple.com/documentation/watchconnectivity/transferring-data-with-watch-connectivity)
- [WatchKit](https://developer.apple.com/documentation/watchkit)
- [Life cycles](https://developer.apple.com/documentation/watchkit/life-cycles)
- [Background execution](https://developer.apple.com/documentation/watchkit/background-execution)
- [Using background tasks](https://developer.apple.com/documentation/watchkit/using-background-tasks)
- [WKWatchConnectivityRefreshBackgroundTask](https://developer.apple.com/documentation/watchkit/wkwatchconnectivityrefreshbackgroundtask)
- [Using extended runtime sessions](https://developer.apple.com/documentation/watchkit/using-extended-runtime-sessions)
- [watchOS apps](https://developer.apple.com/documentation/watchos-apps)
- [Setting up a watchOS project](https://developer.apple.com/documentation/watchos-apps/setting-up-a-watchos-project)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit)
- [Creating accessory widgets and watch complications](https://developer.apple.com/documentation/widgetkit/creating-accessory-widgets-and-watch-complications)
- [Developing a WidgetKit strategy](https://developer.apple.com/documentation/widgetkit/developing-a-widgetkit-strategy)
- [Widgets and watch complications](https://developer.apple.com/documentation/widgetkit/widgets-and-complications-collection)
- [Increasing the visibility of widgets in Smart Stacks](https://developer.apple.com/documentation/widgetkit/widget-suggestions-in-smart-stacks)
- [Adding interactivity to widgets and Live Activities](https://developer.apple.com/documentation/widgetkit/adding-interactivity-to-widgets-and-live-activities)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [Widgets, Live Activities, and Controls](https://developer.apple.com/documentation/appintents/widgets-live-activities-and-controls)
- [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- [App Shortcuts](https://developer.apple.com/documentation/appintents/app-shortcuts)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Designing for watchOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-watchos/)
- [Complications](https://developer.apple.com/design/human-interface-guidelines/complications)
- [Widgets](https://developer.apple.com/design/human-interface-guidelines/widgets)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
