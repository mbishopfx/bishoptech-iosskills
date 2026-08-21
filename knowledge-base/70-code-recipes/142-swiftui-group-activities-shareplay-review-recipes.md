# SwiftUI Group Activities and SharePlay collaborative-native review recipes

These are compile-oriented route sketches for an iOS SwiftUI shared activity. They are intentionally incomplete app slices: verify current SDK signatures, platform availability, Group Activities capability, entitlements, Transferable representation, concurrency annotations, content access, and system UI in the selected Xcode target. They do not claim to compile in this documentation-only workspace or prove FaceTime/Messages/two-device behavior.

Use them with the [collaborative-native deep dive](../42-framework-deep-dives/99-swiftui-group-activities-shareplay-review.md), [design companion](../21-design-deep-dives/127-swiftui-group-activities-shareplay-review-design.md), [review route](../50-capability-recipes/130-swiftui-group-activities-shareplay-review-route.md), and [proof matrix](../60-verification/124-swiftui-group-activities-shareplay-review-proof-matrix.md).

## Recipe 1: small activity payload

Keep the activity value versioned and privacy-safe:

~~~swift
import GroupActivities

struct StudyRoomActivity: GroupActivity {
    var roomID: String
    var contentID: String
    var sourceRevision: Int

    static let activityIdentifier = "com.example.app.study-room"

    var metadata: GroupActivityMetadata {
        var metadata = GroupActivityMetadata()
        metadata.type = .generic
        metadata.title = "Study room"
        metadata.subtitle = "Review this lesson together."
        return metadata
    }
}
~~~

The actual metadata type and available fields must be confirmed in the selected SDK. Keep account access, subscription checks, and large content outside the payload. The receiving device should use contentID and sourceRevision to load the local route, then validate access before presenting shared content.

## Recipe 2: ShareLink and explicit activation

Use a system-owned entry point and keep a solo fallback:

~~~swift
import SwiftUI

struct StudyRoomShareButton: View {
    let activity: StudyRoomActivity
    let start: () async -> Void

    var body: some View {
        ShareLink(
            item: activity,
            preview: SharePreview("Study together")
        ) {
            Label("SharePlay lesson", systemImage: "shareplay")
        }
        .simultaneousGesture(
            TapGesture().onEnded {
                Task { await start() }
            }
        )
    }
}
~~~

Do not combine a ShareLink with a second implicit activation path without deciding which action the person is taking. A clearer production surface often uses a Button for prepareForActivation and a separate ShareLink for the system share sheet. Verify the selected Transferable representation rather than assuming every GroupActivity can be passed directly to ShareLink.

## Recipe 3: eligibility projection

Project GroupStateObserver into app-owned copy:

~~~swift
import GroupActivities
import Observation

@MainActor
@Observable
final class ShareEligibilityModel {
    private(set) var isEligible = false
    private(set) var message = "SharePlay can be started from the system share surface."

    private let observer = GroupStateObserver()

    func refresh() {
        isEligible = observer.isEligibleForGroupSession
        message = isEligible
            ? "Ready to start SharePlay."
            : "SharePlay is not active in this context yet."
    }
}
~~~

False eligibility should change copy or offer a system share route; it should not delete the share action or imply that the platform never supports Group Activities. Confirm observation behavior and lifecycle for the selected OS.

## Recipe 4: activation result

Handle local, group, and cancellation paths explicitly:

~~~swift
import GroupActivities

@MainActor
final class ActivityLauncher {
    var activity: StudyRoomActivity
    var mode: Mode = .local

    enum Mode {
        case local
        case preparing
        case inviting
        case failed(String)
    }

    func start() {
        mode = .preparing
        Task {
            let result = await activity.prepareForActivation()
            switch result {
            case .activationPreferred:
                do {
                    mode = (try await activity.activate()) ? .inviting : .local
                } catch {
                    mode = .failed(String(describing: error))
                }
            case .activationDisabled, .cancelled:
                mode = .local
            @unknown default:
                mode = .local
            }
        }
    }
}
~~~

The enum cases are SDK/version-sensitive; this is a route sketch. The UI must not call the local path “joined” or “shared” until a session arrives and the app joins it.

## Recipe 5: session coordinator and generation

Own one session, messenger, listener set, and generation per active feature:

~~~swift
import GroupActivities
import Observation

@MainActor
@Observable
final class StudyRoomSessionModel {
    enum Status: Equatable {
        case none
        case waiting
        case joined
        case catchingUp
        case invalidated(String)
        case localOnly
    }

    private(set) var status: Status = .none
    private(set) var participantCount = 0
    private(set) var sessionID: UUID?

    private var session: GroupSession<StudyRoomActivity>?
    private var messenger: GroupSessionMessenger?
    private var tasks: [Task<Void, Never>] = []
    private var generation = UUID()

    func listenForSessions() {
        Task { [weak self] in
            for await session in StudyRoomActivity.sessions() {
                guard let self else { return }
                await self.attach(session)
            }
        }
    }

    private func attach(_ session: GroupSession<StudyRoomActivity>) {
        stopCurrent()
        generation = UUID()
        self.session = session
        sessionID = session.id
        status = .waiting
        participantCount = session.activeParticipants.count
        messenger = GroupSessionMessenger(session: session)
        observeState(session, generation: generation)
        observeParticipants(session, generation: generation)
        observeMessages(session, generation: generation)
    }

    func joinWhenReady() {
        guard let session else { return }
        // Restore/load the local content before calling join in the real feature.
        session.join()
    }

    func leave() {
        session?.leave()
        stopCurrent()
    }

    private func stopCurrent() {
        generation = UUID()
        tasks.forEach { $0.cancel() }
        tasks.removeAll()
        messenger = nil
        session = nil
        sessionID = nil
        participantCount = 0
        status = .none
    }

    private func observeState(
        _ session: GroupSession<StudyRoomActivity>,
        generation expected: UUID
    ) {
        // Observe the current SDK's state publisher or async route.
    }

    private func observeParticipants(
        _ session: GroupSession<StudyRoomActivity>,
        generation expected: UUID
    ) {
        // Project active participant changes into approved app-owned display data.
    }

    private func observeMessages(
        _ session: GroupSession<StudyRoomActivity>,
        generation expected: UUID
    ) {
        // Start one task per message type and cancel it on invalidation.
    }
}
~~~

The session is system-created. A coordinator should not be recreated on every SwiftUI update. Verify exact state/participant observation APIs in the selected SDK and reject callbacks whose generation no longer matches.

## Recipe 6: app-owned shared event

Use an event schema instead of sending view state:

~~~swift
struct SharedEvent: Codable, Hashable, Sendable {
    var schemaVersion: Int
    var eventID: UUID
    var sourceRevision: Int
    var recordID: String
    var operation: Operation
    var sourceLabel: String?

    enum Operation: Codable, Hashable, Sendable {
        case rename(String)
        case select
        case addPoint(x: Double, y: Double)
        case requestReview
    }
}

struct SharedReducerState: Sendable {
    var revision = 0
    var appliedEventIDs = Set<UUID>()
    var names: [String: String] = [:]
}
~~~

Before applying an event, check activity/session scope, schema, event ID, source revision, payload bounds, role, and conflict policy. The sender label is for UI provenance, not authorization.

## Recipe 7: Messenger send and receive

Create a messenger for the session lifetime:

~~~swift
final class MessageLane {
    private let messenger: GroupSessionMessenger
    private var receiveTask: Task<Void, Never>?

    init(session: GroupSession<StudyRoomActivity>) {
        messenger = GroupSessionMessenger(session: session)
    }

    func startReceiving(
        apply: @escaping @MainActor (SharedEvent, String?) -> Void
    ) {
        receiveTask = Task {
            for await (event, context) in messenger.messages(
                of: SharedEvent.self
            ) {
                await apply(event, String(describing: context.source))
            }
        }
    }

    func send(_ event: SharedEvent) {
        Task {
            do {
                try await messenger.send(event, to: .all)
            } catch {
                // Publish a retry/failure state; do not claim shared commit.
            }
        }
    }

    func stop() {
        receiveTask?.cancel()
        receiveTask = nil
    }
}
~~~

The exact message tuple and participant selector must be verified in the selected SDK. Add deduplication and stale revision checks in the app reducer. A successful send call is not proof that every participant applied the event.

## Recipe 8: bounded reducer

Make remote application deterministic and idempotent:

~~~swift
struct ReducerResult: Sendable {
    var state: SharedReducerState
    var outcome: Outcome

    enum Outcome: Sendable {
        case applied
        case duplicate
        case stale
        case rejected(String)
    }
}

func reduce(
    _ event: SharedEvent,
    into current: SharedReducerState
) -> ReducerResult {
    guard !current.appliedEventIDs.contains(event.eventID) else {
        return ReducerResult(state: current, outcome: .duplicate)
    }
    guard event.sourceRevision >= current.revision else {
        return ReducerResult(state: current, outcome: .stale)
    }

    var next = current
    next.revision = event.sourceRevision
    next.appliedEventIDs.insert(event.eventID)
    // Apply only the approved operation and bounded payload here.
    return ReducerResult(state: next, outcome: .applied)
}
~~~

For append-only strokes, event IDs may be enough. For selections, renames, carts, or external effects, add a documented conflict/authority rule and a durable revision.

## Recipe 9: late-join baseline

Treat the current shared snapshot as a separate operation from future events:

~~~swift
struct SharedBaseline: Codable, Sendable {
    var activityID: String
    var revision: Int
    var records: [String: String]
    var createdByParticipantReference: String?
}

enum BaselineState: Sendable {
    case missing
    case loading
    case ready(SharedBaseline)
    case rejected(String)
}
~~~

The receiving device should join, obtain a baseline through the selected Journal/server/snapshot route, validate the activity and revision, render a catching-up state, then subscribe to future Messenger events. Do not replay an unbounded UI event history or show a partial baseline as current.

## Recipe 10: shared/private SwiftUI surface

Make the collaboration state semantic:

~~~swift
struct SharedStatusBar: View {
    let isShared: Bool
    let participantCount: Int
    let revision: Int
    let isCatchingUp: Bool
    let leave: () -> Void

    var body: some View {
        HStack {
            Label(
                isShared ? "Shared" : "Private",
                systemImage: isShared ? "person.2.fill" : "lock.fill"
            )
            if isShared {
                Text("\(participantCount) people")
                Text("Revision \(revision)")
            }
            if isCatchingUp {
                ProgressView()
                    .accessibilityLabel("Loading shared state")
            }
            Spacer()
            if isShared {
                Button("Leave SharePlay", action: leave)
            }
        }
        .padding()
        .background(.regularMaterial, in: Capsule())
        .accessibilityElement(children: .combine)
    }
}
~~~

The material is optional decoration. The labels, values, and Leave action remain meaningful when transparency is reduced or the glass effect is unavailable.

## Recipe 11: typed local AI proposal

Keep the proposal scoped to an explicitly shared selection:

~~~swift
struct SharedProposalInput: Sendable {
    var activityID: String
    var sessionID: UUID
    var sourceRevision: Int
    var selectedRecordIDs: [String]
    var allowedOperations: [String]
    var userIntent: String
}

struct SharedProposal: Codable, Sendable {
    var sourceRevision: Int
    var operation: String
    var explanation: String
    var parameters: [String: String]
}

func validate(
    proposal: SharedProposal,
    currentRevision: Int,
    allowlist: Set<String>
) -> SharedProposal? {
    guard proposal.sourceRevision == currentRevision else { return nil }
    guard allowlist.contains(proposal.operation) else { return nil }
    guard proposal.parameters.count <= 8 else { return nil }
    return proposal
}
~~~

The Foundation Models session and availability check belong in the feature model. The proposal must be reviewed before becoming a SharedEvent. Never use generated output as a raw participant selector, message type, file path, or external command.

## Recipe 12: journal descriptor and durable handoff

Keep a journal attachment descriptor separate from the file:

~~~swift
struct AttachmentDescriptor: Codable, Sendable {
    var id: UUID
    var sourceRevision: Int
    var contentType: String
    var byteCount: Int
    var displayName: String
}

struct DurableCommit: Sendable {
    var recordID: String
    var sourceRevision: Int
    var committedByAccountID: String
    var localParticipantReference: String?
}
~~~

The journal transfer and durable commit need separate proof. Validate the attachment before display/use, and require account/role authorization for the durable write.

## Recipe 13: teardown and local fallback

Make invalidation recoverable:

~~~swift
@MainActor
final class SharedFeatureLifecycle {
    private var generation = UUID()
    private var tasks: [Task<Void, Never>] = []

    func begin() -> UUID {
        generation = UUID()
        return generation
    }

    func stop(
        session: GroupSession<StudyRoomActivity>?,
        messenger: MessageLane?
    ) {
        generation = UUID()
        tasks.forEach { $0.cancel() }
        tasks.removeAll()
        messenger?.stop()
        session?.leave()
        // Preserve local work and show local/ended state in the real feature.
    }

    func accepts(_ callbackGeneration: UUID) -> Bool {
        callbackGeneration == generation
    }
}
~~~

If the session is already invalidated, do not call leave again. The real coordinator should track session state and release its session-owned resources exactly once.

## Recipe 14: proof record

Record the collaboration claim separately from the implementation:

~~~swift
struct SharePlayProofRecord: Codable, Sendable {
    var target: String
    var build: String
    var os: String
    var device: String
    var activityIdentifier: String
    var entryPoint: String
    var sessionID: UUID?
    var participantCount: Int
    var lastSharedRevision: Int?
    var messageDeliveryMode: String?
    var baselineSource: String?
    var aiAvailability: String
    var accessibilityModes: [String]
    var twoDeviceEvidencePath: String?
    var archiveEvidencePath: String?
}
~~~

Keep the record with system screenshots/logs and the two-device run. A proof record does not substitute for the evidence itself.

## Sources

- [Group Activities](https://developer.apple.com/documentation/groupactivities)
- [Configuring Group Activities](https://developer.apple.com/documentation/Xcode/configuring-group-activities)
- [GroupActivity](https://developer.apple.com/documentation/groupactivities/groupactivity)
- [GroupActivityMetadata](https://developer.apple.com/documentation/groupactivities/groupactivitymetadata)
- [Defining your app’s SharePlay activities](https://developer.apple.com/documentation/groupactivities/defining-your-apps-shareplay-activities)
- [Presenting SharePlay activities from your app’s UI](https://developer.apple.com/documentation/groupactivities/promoting-shareplay-activities-from-your-apps-ui)
- [GroupStateObserver](https://developer.apple.com/documentation/groupactivities/groupstateobserver)
- [isEligibleForGroupSession](https://developer.apple.com/documentation/groupactivities/groupstateobserver/iseligibleforgroupsession)
- [GroupSession](https://developer.apple.com/documentation/groupactivities/groupsession)
- [GroupSession.State](https://developer.apple.com/documentation/groupactivities/groupsession/state-swift.enum)
- [GroupSessionMessenger](https://developer.apple.com/documentation/groupactivities/groupsessionmessenger)
- [GroupSessionMessenger.MessageContext](https://developer.apple.com/documentation/groupactivities/groupsessionmessenger/messagecontext)
- [GroupSessionMessenger delivery modes](https://developer.apple.com/documentation/groupactivities/groupsessionmessenger/deliverymode-swift.enum/reliable)
- [GroupSessionJournal](https://developer.apple.com/documentation/groupactivities/groupsessionjournal)
- [Synchronizing data during a SharePlay activity](https://developer.apple.com/documentation/groupactivities/synchronizing-data-during-a-shareplay-activity)
- [Joining and managing a shared activity](https://developer.apple.com/documentation/groupactivities/joining-and-managing-a-shared-activity)
- [SharePlay](https://developer.apple.com/design/human-interface-guidelines/shareplay)
- [Collaboration and sharing](https://developer.apple.com/design/human-interface-guidelines/collaboration-and-sharing)
- [ShareLink](https://developer.apple.com/documentation/swiftui/sharelink)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)

## Related routes

- [SwiftUI Group Activities and SharePlay collaborative-native review](../42-framework-deep-dives/99-swiftui-group-activities-shareplay-review.md)
- [SwiftUI Group Activities and SharePlay collaborative-native design](../21-design-deep-dives/127-swiftui-group-activities-shareplay-review-design.md)
- [SwiftUI Group Activities and SharePlay review route](../50-capability-recipes/130-swiftui-group-activities-shareplay-review-route.md)
- [SwiftUI Group Activities and SharePlay proof matrix](../60-verification/124-swiftui-group-activities-shareplay-review-proof-matrix.md)
