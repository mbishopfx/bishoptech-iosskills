# Group Activities and SharePlay recipes

These are compile-oriented route sketches for a shared activity. They are not a durable collaboration backend and are not claimed to compile in this documentation workspace. Verify the current Group Activities capability, platform availability, Swift concurrency annotations, Transferable representation, and system UI behavior in the selected SDK.

## Recipe 1: define a small activity payload

~~~swift
import GroupActivities

struct StudyActivity: GroupActivity {
    var documentID: UUID
    var title: String

    static let activityIdentifier = "com.example.study.activity"

    var metadata: GroupActivityMetadata {
        var metadata = GroupActivityMetadata()
        metadata.type = .generic
        metadata.title = title
        metadata.subtitle = "Study together"
        return metadata
    }
}
~~~

Keep the payload Codable, stable, small, and privacy-reviewed. Use a document ID or content reference rather than embedding an entire private document or account token.

## Recipe 2: observe session eligibility

~~~swift
import Combine
import GroupActivities

@MainActor
final class SharePlayAvailability: ObservableObject {
    @Published private(set) var isEligible = false
    private let observer = GroupStateObserver()
    private var task: Task<Void, Never>?

    func start() {
        isEligible = observer.isEligibleForGroupSession
        task?.cancel()
        task = Task { @MainActor [weak self] in
            for await eligible in observer.$isEligibleForGroupSession.values {
                self?.isEligible = eligible
            }
        }
    }

    func stop() {
        task?.cancel()
        task = nil
    }
}
~~~

The publisher/property path may have different concurrency annotations in the selected SDK. Use the observer to adapt the UI, not as proof that every participant can join.

## Recipe 3: prepare an activation choice

~~~swift
import GroupActivities

enum StartMode {
    case local
    case shared
    case canceled
}

func chooseStartMode(
    activity: StudyActivity
) async -> StartMode {
    let result = await activity.prepareForActivation()

    switch result {
    case .activationPreferred:
        do {
            _ = try await activity.activate()
            return .shared
        } catch {
            return .local
        }
    case .activationDisabled:
        return .local
    case .cancelled:
        return .canceled
    @unknown default:
        return .local
    }
}
~~~

Verify the exact GroupActivityActivationResult cases in the selected SDK. If local mode is valid, keep the local workflow functional. If the activity is group-only, use the documented activation route and show a clear error when no session can be created.

## Recipe 4: listen for and join a GroupSession

~~~swift
import GroupActivities

@MainActor
final class StudySessionCoordinator: ObservableObject {
    @Published private(set) var state = "idle"
    @Published private(set) var participantCount = 0

    private var session: GroupSession<StudyActivity>?
    private var sessionTask: Task<Void, Never>?
    private var participantTask: Task<Void, Never>?

    func listen() {
        sessionTask?.cancel()
        sessionTask = Task { @MainActor [weak self] in
            for await newSession in StudyActivity.sessions() {
                guard let self else { return }
                self.session = newSession
                self.state = "waiting"
                self.observe(newSession)
                newSession.join()
                self.state = "joined-requested"
            }
        }
    }

    private func observe(_ session: GroupSession<StudyActivity>) {
        participantTask?.cancel()
        participantTask = Task { @MainActor [weak self] in
            for await participants in session.$activeParticipants.values {
                self?.participantCount = participants.count
            }
        }
    }

    func leave() {
        session?.leave()
        session = nil
        sessionTask?.cancel()
        participantTask?.cancel()
        state = "left"
    }
}
~~~

In a production coordinator, observe session state and invalidation, hold messenger/journal references, and cancel every listener when the session ends. The AsyncSequence and published-property names shown here are route sketches; confirm them in the SDK.

## Recipe 5: define versioned messenger messages

~~~swift
struct CursorMessage: Codable, Hashable, Sendable {
    var schemaVersion: Int
    var eventID: UUID
    var participantID: UUID
    var x: Double
    var y: Double
    var sentAt: Date
}

struct BoardCommand: Codable, Hashable, Sendable {
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
}
~~~

Use a reliable mode for critical known-participant state and an unreliable mode for disposable cursor/reaction state. Validate schema, event ID, participant role, revision, and expiry before applying.

## Recipe 6: send and receive messages

~~~swift
import GroupActivities

@MainActor
final class MessengerAdapter {
    private let messenger: GroupSessionMessenger

    init(session: GroupSession<StudyActivity>) {
        messenger = GroupSessionMessenger(session: session)
    }

    func send(_ command: BoardCommand) async throws {
        try await messenger.send(
            command,
            deliveryMode: .reliable
        )
    }

    func receive() -> Task<Void, Never> {
        Task { @MainActor in
            for await result in messenger.messages(of: BoardCommand.self) {
                let command = result.0
                // Validate before applying to the local domain model.
                _ = command
            }
        }
    }
}
~~~

The current receive/send overloads and tuple/context values are SDK-sensitive. Use the official synchronization guide and do not assume reliable delivery includes future participants or server durability.

## Recipe 7: send to a participant subset

~~~swift
func sendToReviewers(
    _ message: BoardCommand,
    reviewers: Set<GroupSession<StudyActivity>.Participant>,
    messenger: GroupSessionMessenger
) async throws {
    try await messenger.send(
        message,
        to: reviewers,
        deliveryMode: .reliable
    )
}
~~~

A subset message is a privacy boundary. Derive the participant set from a current role policy, not from a stale local list. Re-check the exact participant and send overload in Xcode.

## Recipe 8: add a journal attachment

~~~swift
import GroupActivities

@MainActor
final class JournalAdapter {
    private let journal: GroupSessionJournal

    init(session: GroupSession<StudyActivity>) {
        journal = GroupSessionJournal(session: session)
    }

    func addSnapshot(_ data: Data) async throws {
        let attachment = SharedSnapshot(data: data)
        try await journal.add(attachment)
    }
}

struct SharedSnapshot: Transferable, Codable, Sendable {
    var data: Data

    static var transferRepresentation: some TransferRepresentation {
        DataRepresentation(exportedContentType: .data) { snapshot in
            snapshot.data
        }
    }
}
~~~

This is intentionally schematic. Verify the journal initializer, add method, and Transferable representation. Validate size/type/provenance before adding data. A journal object is not a general cloud drive.

## Recipe 9: reconcile a mutation

~~~swift
struct SharedRevision: Sendable {
    var revision: Int
    var appliedEventIDs: Set<UUID>
}

enum MutationResult {
    case applied
    case duplicate
    case stale
    case rejected
}

func apply(
    _ command: BoardCommand,
    to revision: inout SharedRevision
) -> MutationResult {
    guard command.schemaVersion == 1 else {
        return .rejected
    }
    guard !revision.appliedEventIDs.contains(command.eventID) else {
        return .duplicate
    }
    guard command.baseRevision <= revision.revision else {
        return .stale
    }

    revision.appliedEventIDs.insert(command.eventID)
    revision.revision += 1
    return .applied
}
~~~

The real conflict policy may be last-change-wins, host-authority, server revision, CRDT, or a domain-specific rule. Make it explicit and visible to participants when conflicts can change shared content.

## Recipe 10: keep AI proposals upstream

~~~swift
struct SharedAIProposal: Codable, Hashable, Sendable {
    var sourceSelectionID: UUID
    var proposedTitle: String
    var proposedCommands: [BoardCommand]
    var explanation: String
    var expiresAt: Date
}

enum SharedProposalDecision {
    case rejected
    case needsReview
    case approved
}

func validate(
    _ proposal: SharedAIProposal,
    currentRevision: Int
) -> SharedProposalDecision {
    guard proposal.expiresAt > Date() else {
        return .rejected
    }
    guard proposal.proposedCommands.allSatisfy({
        $0.baseRevision <= currentRevision
    }) else {
        return .needsReview
    }
    return .needsReview
}
~~~

Even after validation, require the participant/role review required by the activity. Do not send hidden model context or automatically commit a generated mutation.

## Recipe 11: test lifecycle fixtures

~~~swift
enum SharedActivityFixture: Sendable {
    case noConversation
    case localChoice
    case activationCanceled
    case waiting
    case joined
    case lateJoin
    case duplicateMessage
    case outOfOrderMessage
    case journalUnavailable
    case participantLeaves
    case invalidated
    case modelUnavailable
}

struct SharedExpectation: Equatable, Sendable {
    var state: String
    var showSharedContent: Bool
    var allowLocalFallback: Bool
}

func expected(
    for fixture: SharedActivityFixture
) -> SharedExpectation {
    switch fixture {
    case .noConversation, .localChoice, .activationCanceled, .modelUnavailable:
        return SharedExpectation(
            state: "local",
            showSharedContent: false,
            allowLocalFallback: true
        )
    case .waiting:
        return SharedExpectation(
            state: "waiting",
            showSharedContent: false,
            allowLocalFallback: true
        )
    case .joined, .lateJoin, .duplicateMessage, .outOfOrderMessage:
        return SharedExpectation(
            state: "joined",
            showSharedContent: true,
            allowLocalFallback: true
        )
    case .journalUnavailable, .participantLeaves, .invalidated:
        return SharedExpectation(
            state: "reconcile",
            showSharedContent: false,
            allowLocalFallback: true
        )
    }
}
~~~

Fixtures prove state rendering and protocol handling. They do not prove FaceTime/Messages activation, two-device delivery, physical participant behavior, or production persistence.

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
- [Collaboration and sharing](https://developer.apple.com/design/human-interface-guidelines/collaboration-and-sharing)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [ShareLink](https://developer.apple.com/documentation/swiftui/sharelink)
