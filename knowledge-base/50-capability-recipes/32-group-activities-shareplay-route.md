# Group Activities and SharePlay route

Use this recipe when the product needs a synchronized activity in FaceTime, Messages, a share sheet, AirDrop/nearby context, or a supported spatial experience. Start with one activity and one state contract.

The route is:

    local activity record
        -> GroupActivity payload and metadata
        -> capability/eligibility preflight
        -> prepareForActivation or activate
        -> GroupSession delivered asynchronously
        -> join and participant state
        -> messenger/journal/server synchronization
        -> local reconciliation
        -> leave/invalidate/solo fallback

## Choose the transport boundary

| Need | Use | Keep separate |
| --- | --- | --- |
| Invite people to a shared activity | GroupActivity + system SharePlay route | Account/content access |
| Start from a SwiftUI share surface | GroupActivity + Transferable + ShareLink | Local UI state |
| Send small commands/state | GroupSessionMessenger | Schema, revisions, idempotence |
| Send larger data/attachments | GroupSessionJournal | Validation, retention, revocation |
| Persist canonical shared truth | CloudKit/server/custom store | SharePlay session lifetime |
| Discover nearby peers outside SharePlay | Nearby/Network/Multipeer route | SharePlay group session |
| Run a local-only fallback | App-owned domain path | Never fake a joined session |

Group Activities is not a database or a general network protocol. The current [Group Activities documentation](https://developer.apple.com/documentation/groupactivities) and [SharePlay HIG](https://developer.apple.com/design/human-interface-guidelines/shareplay) define the system and design boundaries.

## Model the local and shared layers

~~~swift
struct BoardRecord: Codable, Hashable, Sendable {
    var id: UUID
    var title: String
    var revision: Int
    var strokes: [Stroke]
    var isShared: Bool
}

struct Stroke: Codable, Hashable, Sendable {
    var id: UUID
    var authorParticipantID: UUID?
    var points: [Point]
}

struct Point: Codable, Hashable, Sendable {
    var x: Double
    var y: Double
}

struct BoardActivity: GroupActivity {
    var boardID: UUID
    var title: String

    static let activityIdentifier = "com.example.board.activity"

    var metadata: GroupActivityMetadata {
        var metadata = GroupActivityMetadata()
        metadata.type = .generic
        metadata.title = title
        metadata.subtitle = "Draw together"
        return metadata
    }
}
~~~

The exact GroupActivity metadata properties and Transferable conformance depend on the selected SDK. Keep the payload small, Codable, stable, and safe to send to the invited participant devices.

## Route A: activation

### A1. Observe eligibility

Create GroupStateObserver and observe isEligibleForGroupSession. Use it to update the action affordance:

    eligible -> prepareForActivation/activate
    not eligible -> show share sheet/sharing controller or continue locally

Do not interpret false as “SharePlay unavailable forever.” It can mean no active FaceTime context or another system condition. Do not interpret true as “every participant can join.”

### A2. Prepare or activate

If the feature supports both solo and shared use:

1. Construct the activity.
2. Call prepareForActivation.
3. If the result prefers local mode, continue locally.
4. If the result prefers activation, call activate.
5. If the user should invite others, present the system sharing route.
6. Observe the returned result/error and keep the local activity usable.

If the feature only makes sense for a group, activate directly when the current context supports it. Handle false/throwing activation and handoff cases.

### A3. Capability and metadata

Add the Group Activities capability to the app target. Keep activityIdentifier values unique and stable. Make platform support deliberate; a shared iPhone activity may need a different UI or content route on iPad, Mac, tvOS, or visionOS.

## Route B: session lifecycle

Use the activity type’s sessions AsyncSequence:

~~~swift
import GroupActivities

@MainActor
final class SharedActivityCoordinator<Activity: GroupActivity> {
    private(set) var session: GroupSession<Activity>?
    private var sessionTask: Task<Void, Never>?
    private var state = "idle"

    func listen(for activity: Activity) {
        sessionTask?.cancel()
        sessionTask = Task { @MainActor [weak self] in
            for await session in Activity.sessions() {
                guard let self else { return }
                self.session = session
                self.state = "waiting"
                self.joinWhenReady(session)
            }
        }
    }

    private func joinWhenReady(_ session: GroupSession<Activity>) {
        session.join()
        state = "joined-requested"
    }

    func leave() {
        session?.leave()
        session = nil
        sessionTask?.cancel()
        sessionTask = nil
        state = "left"
    }
}
~~~

This is a route sketch. The selected SDK may require different actor isolation, task ownership, and generic constraints. In the real coordinator, observe state, activeParticipants, and invalidation, then keep messenger/journal listener tasks tied to the session.

## Route C: message protocol

Define messages as value types:

~~~swift
struct BoardMutation: Codable, Hashable, Sendable {
    enum Kind: String, Codable, Sendable {
        case addStroke
        case removeStroke
        case setTitle
    }

    var schemaVersion: Int
    var eventID: UUID
    var sourceParticipantID: UUID
    var baseRevision: Int
    var kind: Kind
    var stroke: Stroke?
    var title: String?
}
~~~

For each message:

1. Validate schema and payload.
2. Reject expired or duplicate event IDs.
3. Check participant/role authorization.
4. Resolve baseRevision/conflict.
5. Apply idempotently.
6. Increment local revision.
7. Update the UI and provenance.

Use reliable messenger delivery for critical known-participant messages. Use unreliable delivery for disposable reaction/cursor/telemetry events. Neither mode is a canonical store or late-join replay protocol.

## Route D: journal and late join

Use GroupSessionJournal for larger attachments or a baseline that later participants can access. Store an attachment descriptor in the local domain:

~~~swift
struct SharedAttachment: Codable, Hashable, Sendable {
    var id: UUID
    var contentType: String
    var byteCount: Int
    var sourceParticipantID: UUID
    var revision: Int
    var isApproved: Bool
}
~~~

Validate file/data content before adding it to the journal. Keep user-visible deletion, revocation, retention, and moderation in an app-owned/server route. A journal is not a permanent cloud drive.

## Route E: canonical persistence

If a shared activity needs to survive after everyone leaves:

1. Keep the canonical board/document/order in SwiftData, CloudKit, or a server.
2. Use GroupSessionMessenger for bounded real-time mutations.
3. Persist accepted mutations through a domain use case.
4. Use revisions/idempotence to reconcile reconnects.
5. Use the journal only for activity-scoped attachments.
6. Let late participants load a snapshot and then receive current session messages.

Do not write received messages directly into a SwiftData model without validation. Do not treat the joined session state as permission to mutate every record in the account.

## Route F: AI collaboration

For an on-device model:

    private/local input
        -> explicit shared selection
        -> local model proposal
        -> participant-visible review
        -> typed mutation
        -> messenger/server/domain validation
        -> shared projection

Examples:

- extract a task list from the selected shared notes;
- propose a board arrangement;
- draft a group trip plan;
- explain a conflict between revisions;
- translate a user-approved shared message.

Do not share private prompts, hidden context, contact records, tokens, or unapproved transcripts. Do not let a model bypass the participant/role rule or send a physical-world command because a shared participant requested it.

## Fallback and failure

| State | App response |
| --- | --- |
| No active conversation | Offer system share/invite route or continue locally |
| Activation declined | Keep local state and explain how to retry |
| Session waiting | Show preparing state; do not enable shared-only claims |
| Participant joins late | Load current snapshot/journal baseline |
| Message rejected | Keep local state and show conflict/retry |
| Participant leaves | Remove presence and preserve/clear local projection per policy |
| Session invalidated | Stop listeners and return to local state |
| Journal unavailable | Use a server/snapshot or show missing attachment |
| Server offline | Queue only safe idempotent mutations or keep local draft |
| AI unavailable | Manual editing and deterministic merge remain available |

## Minimum implementation slices

1. Local-only activity UI and metadata preview.
2. Group Activities capability and activity definition.
3. Eligibility/prepare/activate route with solo fallback.
4. Two-device FaceTime/Messages session, join/leave/invalidation.
5. Reliable/unreliable messenger fixtures and conflict rules.
6. Journal attachment and late-join baseline.
7. Canonical persistence reconciliation.
8. Accessibility, privacy, AI proposal, and physical system proof.

## Sources

- [Group Activities](https://developer.apple.com/documentation/groupactivities)
- [GroupActivity](https://developer.apple.com/documentation/groupactivities/groupactivity)
- [GroupActivityMetadata](https://developer.apple.com/documentation/groupactivities/groupactivitymetadata)
- [Defining your app’s SharePlay activities](https://developer.apple.com/documentation/groupactivities/defining-your-apps-shareplay-activities)
- [Presenting SharePlay activities from your app’s UI](https://developer.apple.com/documentation/groupactivities/promoting-shareplay-activities-from-your-apps-ui)
- [GroupStateObserver](https://developer.apple.com/documentation/groupactivities/groupstateobserver)
- [isEligibleForGroupSession](https://developer.apple.com/documentation/groupactivities/groupstateobserver/iseligibleforgroupsession)
- [prepareForActivation](https://developer.apple.com/documentation/GroupActivities/GroupActivity/prepareForActivation%28%29)
- [activate](https://developer.apple.com/documentation/groupactivities/groupactivity/activate%28%29)
- [GroupSession](https://developer.apple.com/documentation/groupactivities/groupsession)
- [GroupSession.State](https://developer.apple.com/documentation/groupactivities/groupsession/state-swift.enum)
- [GroupSession.Sessions](https://developer.apple.com/documentation/groupactivities/groupsession/sessions)
- [Joining and managing a shared activity](https://developer.apple.com/documentation/groupactivities/joining-and-managing-a-shared-activity)
- [GroupSessionMessenger](https://developer.apple.com/documentation/groupactivities/groupsessionmessenger)
- [GroupSessionJournal](https://developer.apple.com/documentation/groupactivities/groupsessionjournal)
- [Synchronizing data during a SharePlay activity](https://developer.apple.com/documentation/groupactivities/synchronizing-data-during-a-shareplay-activity)
- [SharePlay HIG](https://developer.apple.com/design/human-interface-guidelines/shareplay)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [ShareLink](https://developer.apple.com/documentation/swiftui/sharelink)
