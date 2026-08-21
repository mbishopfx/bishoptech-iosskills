# SwiftUI App Clips, invocation, and full-app handoff review recipes

These are compile-oriented Swift sketches for a named full-app and App Clip target pair. They are not claimed to compile in this documentation-only workspace and they do not prove App Store Connect configuration, target size, physical invocation, domain association, account migration, payment fulfillment, App Intent runtime, model availability, accessibility, or release readiness.

Read the [App Clip review](../42-framework-deep-dives/106-swiftui-app-clips-invocation-handoff-review.md), [design guide](../21-design-deep-dives/134-swiftui-app-clips-invocation-handoff-review-design.md), [route](../50-capability-recipes/137-swiftui-app-clips-invocation-handoff-review-route.md), and [proof matrix](../60-verification/131-swiftui-app-clips-invocation-handoff-review-proof-matrix.md) first. Confirm current SDK signatures, App Clip target restrictions, entitlements, App Store Connect experience, and device behavior before using any sketch.

## Recipe 1: Keep an App Clip task model small

Share the route contract, not the full app.

~~~swift
import Foundation

struct AppClipTask: Codable, Hashable, Sendable, Identifiable {
    enum State: String, Codable, Sendable {
        case loading
        case ready
        case needsContext
        case needsSignIn
        case paymentPending
        case completed
        case stale
        case unavailable
    }

    let id: String
    let title: String
    var state: State
    var sourceRevision: Int
    var createdAt: Date
}

struct AppClipRouteVersion: Codable, Hashable, Sendable {
    let major: Int
    let minor: Int
}

enum AppClipInvocationSource: String, Codable, Sendable {
    case physical
    case safari
    case messages
    case maps
    case location
    case other
    case restored
    case unknown
}
~~~

An invocation is not the durable task record. The task record must be re-resolved after the full app is installed.

## Recipe 2: Define a typed invocation

Use a small model that both targets can share.

~~~swift
import Foundation

struct AppClipInvocation: Codable, Hashable, Sendable {
    let source: AppClipInvocationSource
    let host: String
    let path: String
    let parameters: [String: String]
    let receivedAt: Date
    let routeVersion: AppClipRouteVersion
}

enum AppClipInvocationError: Error, Sendable {
    case missingURL
    case unsupportedActivity
    case unsupportedScheme
    case unsupportedHost
    case unsupportedPath
    case invalidParameter
}
~~~

Keep the route version separate from the App Clip target version. A new full-app build may still need to understand URLs created by an earlier Clip.

## Recipe 3: Parse and allowlist an invocation URL

Treat URL values as untrusted input.

~~~swift
import Foundation

struct AppClipInvocationParser: Sendable {
    let allowedHosts: Set<String>
    let allowedPaths: Set<String>
    let allowedQueryKeys: Set<String>

    func parse(
        url: URL,
        source: AppClipInvocationSource,
        now: Date = Date()
    ) throws -> AppClipInvocation {
        guard url.scheme?.lowercased() == "https" else {
            throw AppClipInvocationError.unsupportedScheme
        }
        guard let host = url.host?.lowercased(),
              allowedHosts.contains(host)
        else {
            throw AppClipInvocationError.unsupportedHost
        }
        let path = url.path.isEmpty ? "/" : url.path
        guard allowedPaths.contains(path) else {
            throw AppClipInvocationError.unsupportedPath
        }

        var values: [String: String] = [:]
        URLComponents(url: url, resolvingAgainstBaseURL: false)?
            .queryItems?
            .forEach { item in
                guard allowedQueryKeys.contains(item.name),
                      let value = item.value,
                      value.count <= 100
                else {
                    return
                }
                values[item.name] = value
            }

        return AppClipInvocation(
            source: source,
            host: host,
            path: path,
            parameters: values,
            receivedAt: now,
            routeVersion: AppClipRouteVersion(major: 1, minor: 0)
        )
    }
}
~~~

Do not interpret a query value as a price, account identity, authorization, or exact location without resolving it through a trusted service or system API.

## Recipe 4: Convert NSUserActivity to an invocation

App Clip invocation URLs arrive through the documented web-browsing activity path.

~~~swift
import Foundation

struct AppClipActivityReader: Sendable {
    let parser: AppClipInvocationParser

    func read(
        activity: NSUserActivity,
        source: AppClipInvocationSource
    ) throws -> AppClipInvocation {
        guard activity.activityType == NSUserActivityTypeBrowsingWeb else {
            throw AppClipInvocationError.unsupportedActivity
        }
        guard let url = activity.webpageURL else {
            throw AppClipInvocationError.missingURL
        }
        return try parser.parse(url: url, source: source)
    }
}
~~~

The system can launch without an invocation URL. Keep that case separate from an invalid URL.

## Recipe 5: Receive the URL in a SwiftUI lifecycle

Use the SwiftUI lifecycle callback in both the Clip and full app where appropriate.

~~~swift
import SwiftUI

@main
struct AppClipDemoApp: App {
    @StateObject private var router = AppClipRouter()

    var body: some Scene {
        WindowGroup {
            AppClipRootView()
                .environmentObject(router)
                .onContinueUserActivity(
                    NSUserActivityTypeBrowsingWeb
                ) { activity in
                    router.receive(activity: activity)
                }
        }
    }
}
~~~

Confirm the exact modifier availability and lifecycle behavior for the target SDK. Scene connection options and UIKit callbacks may be needed for additional lifecycle paths.

## Recipe 6: Handle a missing URL without crashing

Restore a bounded local state or show a neutral entry.

~~~swift
import Foundation

@MainActor
final class AppClipRouter: ObservableObject {
    @Published private(set) var invocation: AppClipInvocation?
    @Published private(set) var task: AppClipTask?
    @Published private(set) var state: State = .waiting

    enum State: Sendable {
        case waiting
        case loading
        case ready
        case restored
        case needsNewContext
        case invalid
    }

    private let parser = AppClipInvocationParser(
        allowedHosts: ["example.com"],
        allowedPaths: ["/", "/menu", "/location"],
        allowedQueryKeys: ["location", "item", "demo"]
    )
    private let store = AppClipLocalStateStore()

    func receive(activity: NSUserActivity) {
        state = .loading
        do {
            let reader = AppClipActivityReader(parser: parser)
            let result = try reader.read(activity: activity, source: .unknown)
            invocation = result
            state = .ready
        } catch AppClipInvocationError.missingURL {
            restoreOrStartNew()
        } catch {
            state = .invalid
        }
    }

    func restoreOrStartNew() {
        if let restored = store.loadTask(), !store.isExpired(restored) {
            task = restored
            state = .restored
        } else {
            task = nil
            state = .needsNewContext
        }
    }
}
~~~

The example parser and local store are intentionally app-owned abstractions. Add server resolution and the correct invocation source mapping in a named target.

## Recipe 7: Persist a small migration envelope

Use a schema, age, and consumed marker.

~~~swift
import Foundation

struct AppClipMigrationEnvelope: Codable, Sendable {
    let schemaVersion: Int
    let taskID: String
    let sourceURLHash: String?
    let sourceRevision: Int
    let anonymousDraft: Data?
    let accountHint: String?
    let createdAt: Date
    var consumedAt: Date?
}

struct AppClipLocalStateStore: Sendable {
    func loadTask() -> AppClipTask? {
        nil
    }

    func isExpired(_ task: AppClipTask, now: Date = Date()) -> Bool {
        now.timeIntervalSince(task.createdAt) > 60 * 60 * 24
    }

    func save(_ envelope: AppClipMigrationEnvelope) throws {
        // Resolve the configured App Group container in a named target.
    }

    func loadEnvelope() -> AppClipMigrationEnvelope? {
        nil
    }

    func markConsumed(_ envelope: AppClipMigrationEnvelope) throws {
        // Write a consumed marker atomically in the shared container.
    }
}
~~~

Do not store passwords, raw model transcripts, or unrestricted personal data in shared defaults or a shared file.

## Recipe 8: Resolve a migration envelope in the full app

Import only after current account/server validation.

~~~swift
actor FullAppMigrationImporter {
    private let store: AppClipLocalStateStore
    private let server: AppClipServer

    init(store: AppClipLocalStateStore, server: AppClipServer) {
        self.store = store
        self.server = server
    }

    func importIfNeeded(accountID: String?) async -> MigrationResult {
        guard let envelope = store.loadEnvelope() else {
            return .none
        }
        guard envelope.schemaVersion == 1 else {
            return .unsupportedSchema
        }
        guard envelope.consumedAt == nil else {
            return .alreadyImported
        }

        do {
            let current = try await server.resolve(taskID: envelope.taskID)
            guard current.sourceRevision >= envelope.sourceRevision else {
                return .stale
            }
            try await server.attachClipDraft(
                envelope.anonymousDraft,
                to: current,
                accountID: accountID
            )
            try store.markConsumed(envelope)
            return .imported
        } catch {
            return .failed
        }
    }
}

enum MigrationResult: Sendable {
    case none
    case imported
    case alreadyImported
    case stale
    case unsupportedSchema
    case failed
}

protocol AppClipServer: Sendable {
    func resolve(taskID: String) async throws -> AppClipServerTask
    func attachClipDraft(
        _ draft: Data?,
        to task: AppClipServerTask,
        accountID: String?
    ) async throws
}

struct AppClipServerTask: Sendable {
    let id: String
    let sourceRevision: Int
}
~~~

An imported local draft is not a server receipt. Keep the server’s current revision authoritative.

## Recipe 9: Show a focused root view

Start at the task, not a full-app dashboard.

~~~swift
import SwiftUI

struct AppClipRootView: View {
    @EnvironmentObject private var router: AppClipRouter

    var body: some View {
        Group {
            switch router.state {
            case .waiting, .loading:
                ProgressView("Preparing your task")
            case .ready:
                FocusedTaskView(task: router.task)
            case .restored:
                RestoredTaskView(task: router.task)
            case .needsNewContext:
                NeutralEntryView()
            case .invalid:
                ContentUnavailableView(
                    "This link is unavailable",
                    systemImage: "link.badge.plus",
                    description: Text("Start a new task or return to the full app.")
                )
            }
        }
        .task {
            router.restoreOrStartNew()
        }
    }
}

struct FocusedTaskView: View {
    let task: AppClipTask?

    var body: some View {
        VStack(spacing: 16) {
            Text(task?.title ?? "Your task")
                .font(.title2.weight(.semibold))
            Text("Complete this focused task without installing the full app.")
                .foregroundStyle(.secondary)
            Button("Continue") {
                // Advance the task-owned state.
            }
            .buttonStyle(.borderedProminent)
        }
        .padding()
    }
}

struct RestoredTaskView: View {
    let task: AppClipTask?

    var body: some View {
        FocusedTaskView(task: task)
    }
}

struct NeutralEntryView: View {
    var body: some View {
        ContentUnavailableView(
            "Choose a task",
            systemImage: "sparkles",
            description: Text("Open a valid App Clip link to continue.")
        )
    }
}
~~~

Confirm the final copy and routing against the specific App Clip Experience.

## Recipe 10: Recommend the full app with StoreKit

Use the SwiftUI system overlay at a natural pause.

~~~swift
import SwiftUI
import StoreKit

struct FullAppRecommendationView: View {
    @State private var showOverlay = false

    var body: some View {
        VStack(spacing: 12) {
            Text("You’re all set.")
            Button("Keep this task in the full app") {
                showOverlay = true
            }
            .buttonStyle(.borderedProminent)
        }
        .appStoreOverlay(isPresented: $showOverlay) {
            SKOverlay.AppClipConfiguration(position: .bottom)
        }
    }
}
~~~

The App Clip overlay may recommend only the corresponding full app. Its presentation or dismissal is not proof that installation completed.

## Recipe 11: Keep Apple Pay as a separate boundary

Do not treat a Clip’s checkout as an entitlement or fulfillment record.

~~~swift
struct AppClipPaymentState: Sendable, Equatable {
    enum State: Sendable, Equatable {
        case cartReady
        case systemAuthorization
        case providerPending
        case providerAccepted
        case fulfillmentPending
        case fulfilled
        case declined
        case canceled
        case unknown
    }

    let taskID: String
    let amountMinorUnits: Int
    let currencyCode: String
    var state: State
}

protocol AppClipPaymentProvider: Sendable {
    func submitAuthorizedPayment(
        taskID: String,
        tokenData: Data,
        amountMinorUnits: Int,
        currencyCode: String
    ) async throws -> ProviderPaymentResult
}

struct ProviderPaymentResult: Sendable {
    let providerEventID: String
    let accepted: Bool
}
~~~

The payment sheet, encrypted token, provider result, and fulfillment result require different evidence. Keep private keys and provider credentials off-device.

## Recipe 12: Use a bounded URL route in the full app

The full app must handle the same invocation contract.

~~~swift
import SwiftUI

struct FullAppRootView: View {
    @StateObject private var router = AppClipRouter()

    var body: some View {
        MainAppView()
            .environmentObject(router)
            .onContinueUserActivity(
                NSUserActivityTypeBrowsingWeb
            ) { activity in
                router.receive(activity: activity)
            }
    }
}

struct MainAppView: View {
    var body: some View {
        NavigationStack {
            Text("Full app")
        }
    }
}
~~~

The full app should resolve the current server record and open its richer route, not simply reproduce stale Clip UI.

## Recipe 13: Represent a full-app App Intent separately

The Clip and full app can share route types, but App Intent runtime belongs to the target that supports it.

~~~swift
import AppIntents

struct OpenClipTaskIntent: AppIntent {
    static var title: LocalizedStringResource = "Open Task"
    static var openAppWhenRun = true

    @Parameter(title: "Task ID")
    var taskID: String

    func perform() async throws -> some IntentResult {
        // Re-resolve the current full-app task before navigation.
        return .result()
    }
}
~~~

Do not assume this intent runs inside an App Clip. Confirm the current App Clip framework table and use the invocation lifecycle inside the Clip.

## Recipe 14: Keep AI proposals structured and small

Use the model only after deterministic source context exists.

~~~swift
import Foundation

struct AppClipProposal: Codable, Hashable, Sendable {
    let sourceTaskID: String
    let sourceRevision: Int
    let title: String
    let action: Action
    let modelRevision: String

    enum Action: String, Codable, Sendable {
        case highlightItem
        case chooseFromKnownItems
        case draftShortDescription
    }
}

struct AppClipProposalValidator: Sendable {
    let currentTaskID: String
    let currentRevision: Int
    let allowedActions: Set<AppClipProposal.Action>

    func validate(_ proposal: AppClipProposal) -> Bool {
        proposal.sourceTaskID == currentTaskID &&
        proposal.sourceRevision == currentRevision &&
        allowedActions.contains(proposal.action) &&
        proposal.title.count <= 120
    }
}
~~~

Do not let a model invent a location, price, account, payment, entitlement, or installation result. If Foundation Models is unavailable, use a deterministic selection or compose route.

## Recipe 15: Gate on model availability

Model readiness is not guaranteed by framework availability.

~~~swift
import FoundationModels

@MainActor
final class AppClipModelState: ObservableObject {
    enum State: Sendable {
        case checking
        case available
        case unavailable
    }

    @Published private(set) var state: State = .checking

    func refresh() {
        switch SystemLanguageModel.default.availability {
        case .available:
            state = .available
        case .unavailable:
            state = .unavailable
        @unknown default:
            state = .unavailable
        }
    }
}
~~~

Keep the Clip useful when the model is not ready or the device does not support Apple Intelligence.

## Recipe 16: Build a restrained Liquid Glass context group

Use glass around a functional context, not the entire Clip.

~~~swift
import SwiftUI

struct InvocationContextView: View {
    let context: String
    let onContinue: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            Label(context, systemImage: "mappin.and.ellipse")
                .font(.headline)
            Text("This task is based on the link or physical context you used.")
                .font(.footnote)
                .foregroundStyle(.secondary)
            Button("Continue") {
                onContinue()
            }
            .buttonStyle(.glassProminent)
        }
        .padding()
        .glassEffect(in: .rect(cornerRadius: 20))
        .accessibilityElement(children: .contain)
    }
}
~~~

Verify the exact Liquid Glass API and availability against the selected SDK. Test reduced transparency and large text.

## Recipe 17: Write a physical-context confirmation state

Do not imply that a URL alone proved location.

~~~swift
enum PhysicalContextState: Sendable, Equatable {
    case notChecked
    case checking
    case matched
    case notMatched
    case unavailable
}

struct PhysicalContextModel: Sendable {
    var state: PhysicalContextState = .notChecked
    var explanation: String = "Location has not been confirmed."
}
~~~

Use the documented App Clip activation/location APIs only when the target and invocation source support them. Keep the UI useful when confirmation is denied or unavailable.

## Recipe 18: Enable temporary App Clip notifications by configuration

This is a target/Info.plist route, not a SwiftUI Boolean.

~~~text
App Clip Info.plist
    NSAppClip
        NSAppClipRequestEphemeralUserNotification = true
~~~

Confirm the current key name, card disclosure, notification window, and target behavior against the selected SDK. If the Clip returns from a notification without an invocation URL, use the restore route.

## Recipe 19: Build an idempotent completion record

Use a server event or task ID to prevent duplicate completion.

~~~swift
struct AppClipCompletion: Codable, Hashable, Sendable {
    let taskID: String
    let sourceRevision: Int
    let clientAttemptID: String
    let completedAt: Date
}

actor AppClipCompletionCoordinator {
    private var submitted: Set<String> = []

    func submitOnce(_ completion: AppClipCompletion) async -> Bool {
        guard !submitted.contains(completion.clientAttemptID) else {
            return false
        }
        submitted.insert(completion.clientAttemptID)
        return true
    }
}
~~~

The example set is not durable server idempotency. Use a server or database contract for real fulfillment.

## Recipe 20: Capture redacted App Clip evidence

Record the invocation layer without secrets.

~~~swift
import Foundation

struct AppClipEvidence: Codable, Sendable {
    enum Layer: String, Codable, Sendable {
        case target
        case size
        case card
        case invocation
        case task
        case location
        case payment
        case migration
        case overlay
        case appIntent
        case model
        case accessibility
        case release
    }

    let id: UUID
    let layer: Layer
    let result: String
    let target: String
    let deviceModel: String?
    let osBuild: String?
    let redactedURL: String?
    let sourceRevision: Int?
    let capturedAt: Date
    let notes: String
}
~~~

Redact query values, account IDs, tokens, credentials, precise location, and private task content.

## Recipe 21: Define the handoff state machine

Use explicit transitions:

~~~swift
enum AppClipLifecycle: String, Codable, Sendable {
    case invoked
    case cardPresented
    case launched
    case contextResolved
    case contextMissing
    case taskReady
    case taskCompleted
    case migrationPending
    case fullAppRecommended
    case fullAppInstalled
    case migrated
    case stale
    case fallback
}
~~~

Do not jump from invoked to migrated or fulfilled without matching evidence.

## Recipe 22: Failure matrix

Keep failures visible:

~~~swift
enum AppClipFailure: String, Codable, Sendable {
    case invalidInvocation
    case missingInvocation
    case experienceNotMatched
    case sizeRejected
    case networkUnavailable
    case accountRequired
    case paymentDeclined
    case fulfillmentUnknown
    case locationUnavailable
    case migrationStale
    case overlayUnavailable
    case modelUnavailable
    case unsupportedFramework
}
~~~

Map every failure to a focused recovery screen or full-app handoff. Do not show a generic “Something went wrong” for a missing URL, a rejected payment, and a model-unavailable state.

## Recipe 23: Manual fallback for model-heavy ideas

An App Clip should remain useful without AI.

~~~swift
import SwiftUI

struct AppClipManualChoiceView: View {
    let items: [String]
    let onChoose: (String) -> Void

    var body: some View {
        List(items, id: \.self) { item in
            Button(item) {
                onChoose(item)
            }
        }
        .navigationTitle("Choose")
    }
}
~~~

Do not turn model unavailability into a full-app install gate.

## Recipe 24: Handoff checklist

Use this at code review:

~~~text
Full app target:
App Clip target:
Invocation source:
Invocation URL:
URL present:
Experience type:
Card metadata:
App Clip size:
Shared container:
Migration schema:
Current server revision:
Account state:
Payment/provider state:
Location state:
Temporary notification state:
Overlay state:
Full-app route:
App Intent target:
Model availability:
Model/source revision:
Accessibility task:
Archive/TestFlight/App Store result:
Known unsupported routes:
~~~

## Sources

- [App Clips](https://developer.apple.com/documentation/appclip)
- [Choosing the right functionality for your App Clip](https://developer.apple.com/documentation/appclip/choosing-the-right-functionality-for-your-app-clip)
- [Creating an App Clip with Xcode](https://developer.apple.com/documentation/appclip/creating-an-app-clip-with-xcode)
- [Configuring App Clip experiences](https://developer.apple.com/documentation/appclip/configuring-the-launch-experience-of-your-app-clip)
- [Responding to invocations](https://developer.apple.com/documentation/AppClip/responding-to-invocations)
- [Testing the launch experience of your App Clip](https://developer.apple.com/documentation/AppClip/testing-the-launch-experience-of-your-app-clip)
- [Distributing your App Clip](https://developer.apple.com/documentation/appclip/distributing-your-app-clip)
- [Sharing data between your App Clip and your full app](https://developer.apple.com/documentation/appclip/sharing-data-between-your-app-clip-and-your-full-app)
- [Recommending your app to App Clip users](https://developer.apple.com/documentation/appclip/recommending-your-app-to-app-clip-users)
- [Enabling notifications in App Clips](https://developer.apple.com/documentation/appclip/enabling-notifications-in-app-clips)
- [Confirming a person’s physical location](https://developer.apple.com/documentation/appclip/confirming-a-person-s-physical-location)
- [NSAppClip](https://developer.apple.com/documentation/bundleresources/information-property-list/nsappclip)
- [APActivationPayload](https://developer.apple.com/documentation/appclip/apactivationpayload)
- [UIScene.ConnectionOptions](https://developer.apple.com/documentation/uikit/uiscene/connectionoptions)
- [StoreKit SKOverlay](https://developer.apple.com/documentation/storekit/skoverlay)
- [SKOverlay.AppClipConfiguration](https://developer.apple.com/documentation/storekit/skoverlay/appclipconfiguration)
- [SwiftUI appStoreOverlay](https://developer.apple.com/documentation/swiftui/view/appstoreoverlay%28ispresented%3Aconfiguration%3A%29)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- [App Shortcuts](https://developer.apple.com/documentation/appintents/app-shortcuts)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [App Clips HIG](https://developer.apple.com/design/human-interface-guidelines/app-clips)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
