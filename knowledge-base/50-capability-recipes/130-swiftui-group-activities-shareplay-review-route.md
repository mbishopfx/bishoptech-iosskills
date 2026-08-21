# SwiftUI Group Activities and SharePlay collaborative-native review route

Use this route when a SwiftUI app needs a FaceTime, Messages, share-sheet, AirDrop, or supported spatial shared experience while keeping the local domain model, participant permissions, and durable record under app control.

This page extends the existing [Group Activities and SharePlay route](32-group-activities-shareplay-route.md) with a review-oriented state/revision boundary. Pair it with the [collaborative-native deep dive](../42-framework-deep-dives/99-swiftui-group-activities-shareplay-review.md), [design companion](../21-design-deep-dives/127-swiftui-group-activities-shareplay-review-design.md), [proof matrix](../60-verification/124-swiftui-group-activities-shareplay-review-proof-matrix.md), and [recipes](../70-code-recipes/142-swiftui-group-activities-shareplay-review-recipes.md).

## Choose the outcome first

| Outcome | Start with | Do not add by default |
| --- | --- | --- |
| Invite people to view a shared activity | GroupActivity, metadata, ShareLink/system share route | A custom invitation UI that imitates system surfaces. |
| Let people choose local or shared mode | prepareForActivation and a local fallback | Treating eligibility as a permanent availability verdict. |
| Join an in-progress activity | activity.sessions() and GroupSession | Constructing GroupSession directly. |
| Send a small command or state patch | GroupSessionMessenger and Codable envelope | Sending an entire database or hidden private context. |
| Send a cursor or transient reaction | Messenger with deliberate unreliable mode | Using an unreliable event for a durable mutation. |
| Share a larger image/document artifact | GroupSessionJournal and validation | Treating a journal as server storage or unlimited transfer. |
| Support late join | Journal/server/current snapshot/deterministic baseline | Replaying an unbounded stream of historical UI events. |
| Coordinate movie/audio playback | Documented coordinated-media route | Sending every player time tick through Messenger. |
| Save canonical shared truth | CloudKit/server/custom persistence | Assuming a live session persists after leave/invalidation. |
| Suggest a shared action with on-device AI | Typed shared snapshot -> local proposal -> review | Letting model output choose raw message/side-effect identifiers. |

## Route map

~~~text
SwiftUI task and local record
  -> explicit shared/private scope
  -> target/capability/entitlement gate
  -> activity payload and metadata
  -> ShareLink, share sheet, or prepare/activate
  -> system invitation/context
  -> activity.sessions()
  -> GroupSession waiting
  -> local state restored and session.join()
  -> joined participant/session projection
  -> Messenger/Journal/media lane
  -> validate/reconcile/review
  -> deterministic local or durable commit
  -> leave/invalidate/solo fallback
~~~

Keep the system activation path separate from app-owned domain authorization. A SharePlay invitation should identify the shared experience, not silently grant account access.

## Route A: configure the target

Before implementation:

1. Add the Group Activities capability to the app target.
2. Record the generated entitlement and provisioning result.
3. Confirm platform and deployment support for every target.
4. Keep widgets, extensions, App Clips, and watchOS on explicit alternate routes unless the selected SDK documents support.
5. Decide whether activity payloads need Transferable for ShareLink/share-sheet use.
6. Record content/account/subscription checks required before join.
7. Decide what shared data is temporary and what is durable.

The feature should have a fallback for:

- no active FaceTime/Messages context;
- activation declined or canceled;
- app not installed on a participant device;
- participant lacks content access;
- session delivery delay;
- invalidated session;
- no model or model cancellation;
- durable save failure.

## Route B: define the activity

Use a small Codable value type:

~~~swift
import GroupActivities

struct SharedBoardActivity: GroupActivity {
    var boardID: String
    var boardRevision: Int

    static let activityIdentifier = "com.example.app.shared-board"

    var metadata: GroupActivityMetadata {
        var metadata = GroupActivityMetadata()
        metadata.type = .generic
        metadata.title = "Shared board"
        metadata.subtitle = "Review this board together."
        return metadata
    }
}
~~~

If the activity enters a SwiftUI ShareLink, add a verified Transferable representation for the selected target. Keep the activity identifier stable and place content identity/version in the payload. Do not put private prompts, access tokens, large files, or the entire board database in the activity value.

## Route C: activation and system handoff

Use eligibility for status, then let the system decide the activation path:

~~~swift
import GroupActivities

@MainActor
final class SharedBoardAvailability: ObservableObject {
    @Published private(set) var isEligible = false
    private let observer = GroupStateObserver()

    func refresh() {
        isEligible = observer.isEligibleForGroupSession
    }
}
~~~

For a feature that can run solo:

~~~swift
func startBoardShare() async {
    let activity = SharedBoardActivity(boardID: boardID, boardRevision: revision)
    switch await activity.prepareForActivation() {
    case .activationPreferred:
        do {
            _ = try await activity.activate()
        } catch {
            showShareFailure(error)
        }
    case .activationDisabled:
        showLocalMode()
    case .cancelled:
        showLocalMode()
    @unknown default:
        showLocalMode()
    }
}
~~~

This is a compile-oriented sketch; verify current enum cases and availability in the selected SDK. A ShareLink can offer the system share sheet:

~~~swift
ShareLink(
    item: activity,
    preview: SharePreview("Share this board")
) {
    Label("SharePlay board", systemImage: "shareplay")
}
~~~

Do not hide the ordinary share route merely because GroupStateObserver is not eligible. Do not claim a session exists until a GroupSession is delivered and joined.

## Route D: receive and join the session

Observe sessions for the activity and create one coordinator per session:

~~~swift
@MainActor
final class SharedBoardCoordinator: ObservableObject {
    @Published private(set) var status: SharedStatus = .none
    @Published private(set) var participantCount = 0

    private var session: GroupSession<SharedBoardActivity>?
    private var messenger: GroupSessionMessenger?
    private var listenerTasks: [Task<Void, Never>] = []
    private var generation = UUID()

    func observeSessions() {
        Task {
            for await session in SharedBoardActivity.sessions() {
                await MainActor.run {
                    self.attach(session)
                }
            }
        }
    }

    private func attach(_ session: GroupSession<SharedBoardActivity>) {
        stopCurrentSession()
        generation = UUID()
        self.session = session
        status = .waiting
        participantCount = session.activeParticipants.count
        messenger = GroupSessionMessenger(session: session)
        observeState(session, generation: generation)
        observeParticipants(session, generation: generation)
        observeMessages(session, generation: generation)
    }

    func joinWhenReady() {
        guard let session else { return }
        session.join()
    }

    func leave() {
        session?.leave()
        stopCurrentSession()
    }

    private func stopCurrentSession() {
        generation = UUID()
        listenerTasks.forEach { $0.cancel() }
        listenerTasks.removeAll()
        messenger = nil
        session = nil
        status = .none
    }
}
~~~

The exact published properties, participant collection names, and async observation signatures must be checked in the selected SDK. The ownership rules are the important part:

- the session is delivered by the system;
- join is explicit;
- the messenger is strongly retained for the session lifetime;
- listener tasks are canceled on leave/invalidation/replacement;
- a generation prevents old callbacks from changing the new feature;
- a local state snapshot is ready before the app joins.

## Route E: model session state and participants

Map GroupSession.State into app-owned state:

~~~swift
enum SharedStatus: Equatable, Sendable {
    case none
    case waiting
    case joined
    case catchingUp
    case invalidated(String)
    case localOnly
}

struct ParticipantSnapshot: Equatable, Sendable {
    var count: Int
    var approvedNames: [String]
    var sourceRevision: Int
}
~~~

Track:

- session UUID;
- activity payload revision;
- waiting/joined/invalidated reason;
- active participant count;
- approved display projection;
- local shared-state revision;
- baseline/catch-up status;
- current app account authorization;
- local/private/shared scope.

Do not expose GroupSession.State directly as the app’s entire domain state. A joined session can still be catching up, missing content, unauthorized for the document, or waiting for a durable commit.

## Route F: Messenger envelope and reducer

Keep messages small and typed:

~~~swift
struct SharedBoardEvent: Codable, Hashable, Sendable {
    var schemaVersion: Int
    var eventID: UUID
    var sourceRevision: Int
    var recordID: String
    var operation: Operation
    var payload: Payload

    enum Operation: String, Codable, Sendable {
        case addStroke
        case selectItem
        case rename
        case requestReview
    }

    enum Payload: Codable, Hashable, Sendable {
        case text(String)
        case point(x: Double, y: Double)
        case itemID(String)
    }
}
~~~

Before applying an event:

1. verify the activity/session generation;
2. verify schema and payload bounds;
3. reject an already-applied eventID;
4. check the source revision and conflict rule;
5. check the participant role/account authorization when required;
6. apply through a deterministic reducer;
7. publish source/revision/status to SwiftUI;
8. commit durably only through the selected authority.

Use participant subsets for role-scoped data only after the role policy is explicit. A subset send is not a security boundary by itself.

## Route G: Journal, baseline, and durable store

Use GroupSessionJournal for larger artifacts or a late-join baseline when it fits the documented limits. Keep a local descriptor:

~~~swift
struct SharedAttachmentDescriptor: Codable, Hashable, Sendable {
    var id: UUID
    var activityID: String
    var sourceRevision: Int
    var uniformTypeIdentifier: String
    var byteCount: Int
    var createdByParticipantReference: String?
}
~~~

When a late participant joins:

~~~text
join
  -> obtain current baseline
  -> validate type/size/activity/revision
  -> materialize temporary local content
  -> publish catchingUp/ready
  -> subscribe to future messages
~~~

If the product needs deletion, revocation, moderation, audit, or large files, use CloudKit/server/custom persistence and make the journal only a transfer lane.

## Route H: coordinated media

For media, keep a local player and a shared intent:

~~~swift
struct SharedPlaybackIntent: Codable, Sendable {
    var revision: Int
    var isPlaying: Bool
    var requestedTime: Double
    var sourceID: String
}

struct LocalPlaybackState: Sendable {
    var bufferedTime: Double
    var currentTime: Double
    var isReady: Bool
    var hasEntitlement: Bool
}
~~~

Use AVFoundation’s documented coordinated media route where it meets the requirement. Do not report the local player’s currentTime as shared truth. Surface buffering, catch-up, seek conflict, and content access separately.

## Route I: local AI proposal

Restrict model input and output:

~~~swift
struct SharedBoardProposalInput: Sendable {
    var activityID: String
    var sharedRevision: Int
    var selectedRecordIDs: [String]
    var allowedOperations: [String]
    var userIntent: String
}

struct SharedBoardProposal: Codable, Sendable {
    var sourceRevision: Int
    var operation: String
    var explanation: String
    var parameters: [String: String]
}
~~~

Validate:

- model availability;
- explicit selected shared input;
- current activity/session revision;
- allowlisted operation;
- bounded parameters;
- participant role and review requirement;
- stale/cancelled result;
- deterministic reducer output.

The model must not choose an arbitrary GroupSessionMessenger message type, raw file path, participant identity, external command, or durable database mutation.

## Route J: teardown and fallback

When the person leaves:

1. call GroupSession.leave where the session is still valid;
2. cancel messenger/journal/listener tasks;
3. stop media coordination;
4. mark pending proposals stale;
5. preserve or discard local work according to product policy;
6. clear shared-only controls;
7. show local/ended state;
8. allow retry without reusing the invalidated session.

When a session invalidates because the call ends, an error occurs, or the user leaves, release session-owned resources and do not call join/leave/end again on that session.

## Proof handoff

Record:

- target and Group Activities entitlement;
- activity identifier and metadata;
- activation result and system entry point;
- session ID, state timeline, participant count;
- baseline/source revision;
- message schema/event IDs/delivery mode/subset;
- journal descriptor/size/late-join/cancellation;
- durable authority and commit revision;
- AI input/proposal/review/stale policy;
- private/shared scope;
- VoiceOver/Dynamic Type/reduced effects/alternate input;
- two-device FaceTime/Messages/AirDrop evidence;
- archive/release target evidence.

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
- [GroupSession activity](https://developer.apple.com/documentation/groupactivities/groupsession/activity)
- [GroupSessionMessenger](https://developer.apple.com/documentation/groupactivities/groupsessionmessenger)
- [GroupSessionMessenger.MessageContext](https://developer.apple.com/documentation/groupactivities/groupsessionmessenger/messagecontext)
- [GroupSessionMessenger delivery modes](https://developer.apple.com/documentation/groupactivities/groupsessionmessenger/deliverymode-swift.enum/reliable)
- [GroupSessionJournal](https://developer.apple.com/documentation/groupactivities/groupsessionjournal)
- [Synchronizing data during a SharePlay activity](https://developer.apple.com/documentation/groupactivities/synchronizing-data-during-a-shareplay-activity)
- [Joining and managing a shared activity](https://developer.apple.com/documentation/groupactivities/joining-and-managing-a-shared-activity)
- [ShareLink](https://developer.apple.com/documentation/swiftui/sharelink)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [Supporting coordinated media playback](https://developer.apple.com/documentation/avfoundation/supporting-coordinated-media-playback)
- [SharePlay](https://developer.apple.com/design/human-interface-guidelines/shareplay)
- [Collaboration and sharing](https://developer.apple.com/design/human-interface-guidelines/collaboration-and-sharing)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)

## Related routes

- [SwiftUI Group Activities and SharePlay collaborative-native review](../42-framework-deep-dives/99-swiftui-group-activities-shareplay-review.md)
- [SwiftUI Group Activities and SharePlay collaborative-native design](../21-design-deep-dives/127-swiftui-group-activities-shareplay-review-design.md)
- [Group Activities and SharePlay route](32-group-activities-shareplay-route.md)
- [SwiftUI Group Activities and SharePlay proof matrix](../60-verification/124-swiftui-group-activities-shareplay-review-proof-matrix.md)
- [SwiftUI Group Activities and SharePlay recipes](../70-code-recipes/142-swiftui-group-activities-shareplay-review-recipes.md)
