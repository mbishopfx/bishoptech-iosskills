# CallKit, LiveCommunicationKit, and VoIP recipes

These are compile-oriented route sketches, not a complete VoIP service. Confirm current SDK signatures, availability, entitlements, APNs topic/environment, provider protocol, audio configuration, and regional default-app requirements before compiling.

The app should own one call coordinator and one audio coordinator. SwiftUI views observe domain state; they do not own the provider, PushKit registry, ConversationManager, or AVAudioSession lifecycle.

## Recipe 1: use a domain call record

~~~swift
enum CallState: Equatable, Sendable {
    case draft
    case validating
    case requested
    case reported
    case ringing
    case connecting
    case connected
    case held
    case muted
    case mediaUnavailable
    case ended
    case failed(String)
    case reset
}

struct CallRecord: Equatable, Sendable {
    var id: String
    var systemUUID: UUID
    var recipientLabel: String
    var handleValue: String
    var state: CallState
    var providerCallID: String?
}
~~~

Keep system UUID, server call ID, user-facing handle, and account identity separate. Persist only the minimum needed to reconcile a process restart.

## Recipe 2: configure a CallKit provider

~~~swift
import CallKit

final class CallProviderController: NSObject {
    let provider: CXProvider

    override init() {
        let configuration = CXProviderConfiguration(localizedName: "Example Calls")
        configuration.supportsVideo = true
        configuration.supportedHandleTypes = [.phoneNumber, .emailAddress]
        configuration.maximumCallGroups = 1
        configuration.maximumCallsPerCallGroup = 2
        configuration.includesCallsInRecents = true

        provider = CXProvider(configuration: configuration)
        super.init()
        provider.setDelegate(self, queue: nil)
    }
}

extension CallProviderController: CXProviderDelegate {
    func providerDidReset(_ provider: CXProvider) {
        // End local media and reconcile all system calls with the server.
    }

    func provider(_ provider: CXProvider, didActivate audioSession: AVAudioSession) {
        // Start or resume the media engine after system activation.
    }

    func provider(_ provider: CXProvider, didDeactivate audioSession: AVAudioSession) {
        // Pause or stop media and update the domain state.
    }
}
~~~

The configuration initializer and supported handle values are SDK-sensitive. Verify the current API and target availability. Keep the provider alive for the intended app lifetime.

## Recipe 3: report a validated incoming call

~~~swift
import CallKit

@MainActor
func reportIncomingCall(
    provider: CXProvider,
    callUUID: UUID,
    callerName: String,
    handleValue: String
) async -> Result<Void, Error> {
    let update = CXCallUpdate()
    update.localizedCallerName = callerName
    update.remoteHandle = CXHandle(type: .generic, value: handleValue)
    update.hasVideo = false
    update.supportsHolding = true
    update.supportsDTMF = false

    do {
        try await provider.reportNewIncomingCall(
            with: callUUID,
            update: update
        )
        return .success(())
    } catch {
        return .failure(error)
    }
}
~~~

Call this only after validating the account, invitation expiry, duplicate state, and server call ID. A successful report means the system accepted the report attempt; it does not mean the person answered or media connected.

## Recipe 4: request an outgoing call action

~~~swift
import CallKit

func requestOutgoingCall(
    callUUID: UUID,
    handleValue: String
) async throws {
    let handle = CXHandle(type: .generic, value: handleValue)
    let action = CXStartCallAction(call: callUUID, handle: handle)
    let transaction = CXTransaction(action: action)
    try await CXCallController().request(transaction)
}
~~~

The current async overload and initializer spelling can vary with SDK annotations; verify them in Xcode. The provider delegate, not the button handler, should start the actual VoIP signaling and fulfill/fail the action.

## Recipe 5: handle provider actions

~~~swift
extension CallProviderController {
    func perform(_ action: CXAction) async {
        switch action {
        case let answer as CXAnswerCallAction:
            do {
                try await service.answer(callUUID: answer.callUUID)
                answer.fulfill()
            } catch {
                answer.fail()
            }

        case let start as CXStartCallAction:
            do {
                try await service.start(callUUID: start.callUUID)
                start.fulfill()
            } catch {
                start.fail()
            }

        case let end as CXEndCallAction:
            do {
                try await service.end(callUUID: end.callUUID)
                end.fulfill()
            } catch {
                end.fail()
            }

        case let mute as CXSetMutedCallAction:
            do {
                try await service.setMuted(
                    callUUID: mute.callUUID,
                    isMuted: mute.isMuted
                )
                mute.fulfill()
            } catch {
                mute.fail()
            }

        default:
            action.fail()
        }
    }
}
~~~

This is a route sketch. A production delegate must use the exact typed delegate methods for the current SDK and handle hold/group/DTMF/translation where the provider supports them. Every action needs timeout and reset handling.

## Recipe 6: register PushKit at launch

~~~swift
import PushKit

final class VoIPPushCoordinator: NSObject, PKPushRegistryDelegate {
    private var registry: PKPushRegistry?

    func register() {
        let registry = PKPushRegistry(queue: nil)
        registry.delegate = self
        registry.desiredPushTypes = [.voIP]
        self.registry = registry
    }

    func pushRegistry(
        _ registry: PKPushRegistry,
        didUpdate credentials: PKPushCredentials,
        for type: PKPushType
    ) {
        let token = credentials.token
        // Send the opaque token and environment to the authenticated server.
        _ = token
    }

    func pushRegistry(
        _ registry: PKPushRegistry,
        didReceiveIncomingPushWith payload: PKPushPayload,
        for type: PKPushType,
        completion: @escaping () -> Void
    ) {
        Task {
            defer { completion() }
            // Validate payload and call identity before reporting to CallKit.
        }
    }
}
~~~

Do not use the VoIP registry for unrelated background work. The server must know the current token/environment and must expire/deduplicate invitations.

## Recipe 7: centralize call audio

~~~swift
import AVFAudio

@MainActor
final class CallAudioCoordinator {
    private let session = AVAudioSession.sharedInstance()

    func prepare() throws {
        try session.setCategory(
            .playAndRecord,
            mode: .voiceChat,
            options: [.allowBluetooth, .allowBluetoothA2DP]
        )
    }

    func activate() throws {
        try session.setActive(true)
    }

    func deactivate() throws {
        try session.setActive(
            false,
            options: .notifyOthersOnDeactivation
        )
    }
}
~~~

Observe audio-session interruption and route-change notifications in the coordinator. Do not start the media engine only because the system call UI appeared, and do not leave the audio session active after provider/manager deactivation.

## Recipe 8: model LiveCommunicationKit actions

~~~swift
import LiveCommunicationKit

@MainActor
final class ConversationCoordinator: NSObject {
    private let manager: ConversationManager

    init(configuration: ConversationManager.Configuration) {
        manager = ConversationManager(configuration: configuration)
        super.init()
        manager.delegate = self
    }

    func startConversation(
        uuid: UUID,
        handles: Set<Handle>,
        isVideo: Bool
    ) async throws {
        let action = StartConversationAction(
            conversationUUID: uuid,
            handles: handles,
            isVideo: isVideo
        )
        try await manager.perform([action])
    }

    func stop() {
        manager.invalidate()
    }
}

extension ConversationCoordinator: ConversationManagerDelegate {
    func conversationManagerDidBegin(_ manager: ConversationManager) {}

    func conversationManagerDidReset(_ manager: ConversationManager) {
        // Clear pending local actions and stop media.
    }

    func conversationManager(
        _ manager: ConversationManager,
        conversationChanged conversation: Conversation
    ) {
        // Reconcile the domain call record.
    }

    func conversationManager(
        _ manager: ConversationManager,
        didActivate audioSession: AVAudioSession
    ) {
        // Start media after system activation.
    }

    func conversationManager(
        _ manager: ConversationManager,
        didDeactivate audioSession: AVAudioSession
    ) {
        // Stop or pause media.
    }

    func conversationManager(
        _ manager: ConversationManager,
        perform action: ConversationAction
    ) {
        // Perform against the VoIP service, then action.fulfill() or fail().
    }

    func conversationManager(
        _ manager: ConversationManager,
        timedOutPerforming action: ConversationAction
    ) {
        // Reconcile timeout and stop any unsafe retry.
    }
}
~~~

The exact initializer and delegate annotations are availability-sensitive. Keep the system manager and service adapter separate. A manager action does not connect media by itself.

## Recipe 9: report conversation events

~~~swift
import LiveCommunicationKit

func reportConnected(
    manager: ConversationManager,
    conversation: Conversation
) {
    manager.reportConversationEvent(
        .conversationConnected(Date()),
        for: conversation
    )
}

func reportEnded(
    manager: ConversationManager,
    conversation: Conversation,
    reason: Conversation.EndedReason
) {
    manager.reportConversationEvent(
        .conversationEnded(Date(), reason),
        for: conversation
    )
}
~~~

Use event reporting only when the real service state supports the claim. Keep a server call ID and conversation UUID for reconciliation.

## Recipe 10: model a reviewable AI call proposal

~~~swift
struct CallProposal: Codable, Hashable, Sendable {
    var recipientCandidates: [String]
    var selectedHandle: String?
    var method: String
    var explanation: String
    var expiresAt: Date
}

enum CallProposalDecision {
    case rejected(String)
    case needsRecipientReview
    case needsMethodReview
    case approved
}

func validate(
    proposal: CallProposal,
    knownHandles: Set<String>
) -> CallProposalDecision {
    guard proposal.expiresAt > Date() else {
        return .rejected("Proposal expired")
    }
    guard let selectedHandle = proposal.selectedHandle,
          knownHandles.contains(selectedHandle)
    else {
        return .needsRecipientReview
    }
    guard proposal.method == "voip" || proposal.method == "cellular" else {
        return .needsMethodReview
    }
    return .approved
}
~~~

The model suggests; deterministic account/contact logic validates; the person reviews; CallKit or LiveCommunicationKit performs the system action. Never let the model directly call the provider or select an ambiguous recipient.

## Recipe 11: test call and media fixtures

~~~swift
enum CallFixture: Sendable {
    case validIncoming
    case duplicateIncoming
    case expiredIncoming
    case providerDeclined
    case actionTimedOut
    case audioInterrupted
    case microphoneDenied
    case managerReset
}

struct CallExpectation: Equatable, Sendable {
    var state: CallState
    var shouldReportToSystem: Bool
    var shouldStartMedia: Bool
}

func expected(for fixture: CallFixture) -> CallExpectation {
    switch fixture {
    case .validIncoming:
        return CallExpectation(
            state: .reported,
            shouldReportToSystem: true,
            shouldStartMedia: false
        )
    case .duplicateIncoming, .expiredIncoming:
        return CallExpectation(
            state: .failed("stale invitation"),
            shouldReportToSystem: false,
            shouldStartMedia: false
        )
    case .providerDeclined, .actionTimedOut, .microphoneDenied:
        return CallExpectation(
            state: .failed("provider or media failure"),
            shouldReportToSystem: true,
            shouldStartMedia: false
        )
    case .audioInterrupted:
        return CallExpectation(
            state: .mediaUnavailable,
            shouldReportToSystem: true,
            shouldStartMedia: false
        )
    case .managerReset:
        return CallExpectation(
            state: .reset,
            shouldReportToSystem: false,
            shouldStartMedia: false
        )
    }
}
~~~

Fixtures verify state and fallback behavior. They do not prove APNs delivery, system call UI, physical audio, default-role behavior, or provider reliability.

## Sources

- [CallKit](https://developer.apple.com/documentation/callkit)
- [Making and receiving VoIP calls](https://developer.apple.com/documentation/callkit/making-and-receiving-voip-calls)
- [Preparing your app to be the default calling app](https://developer.apple.com/documentation/callkit/preparing-your-app-to-be-the-default-calling-app)
- [CXProvider](https://developer.apple.com/documentation/callkit/cxprovider)
- [CXProviderConfiguration](https://developer.apple.com/documentation/callkit/cxproviderconfiguration)
- [CXProviderDelegate](https://developer.apple.com/documentation/callkit/cxproviderdelegate)
- [CXCallController](https://developer.apple.com/documentation/callkit/cxcallcontroller)
- [CXTransaction](https://developer.apple.com/documentation/callkit/cxtransaction)
- [CXCallAction](https://developer.apple.com/documentation/callkit/cxcallaction)
- [CXStartCallAction](https://developer.apple.com/documentation/callkit/cxstartcallaction)
- [CXAnswerCallAction](https://developer.apple.com/documentation/callkit/cxanswercallaction)
- [CXEndCallAction](https://developer.apple.com/documentation/callkit/cxendcallaction)
- [CXCallUpdate](https://developer.apple.com/documentation/callkit/cxcallupdate)
- [PushKit](https://developer.apple.com/documentation/pushkit)
- [PKPushRegistry](https://developer.apple.com/documentation/pushkit/pkpushregistry)
- [Supporting PushKit Notifications in Your App](https://developer.apple.com/documentation/pushkit/supporting-pushkit-notifications-in-your-app)
- [Responding to VoIP Notifications from PushKit](https://developer.apple.com/documentation/pushkit/responding-to-voip-notifications-from-pushkit)
- [LiveCommunicationKit](https://developer.apple.com/documentation/livecommunicationkit)
- [Initiating VoIP conversations with LiveCommunicationKit](https://developer.apple.com/documentation/livecommunicationkit/initiating-voip-conversations-with-livecommunicationkit)
- [Preparing your app to be the default dialer app](https://developer.apple.com/documentation/livecommunicationkit/preparing-your-app-to-be-the-default-dialer-app)
- [ConversationManager](https://developer.apple.com/documentation/livecommunicationkit/conversationmanager)
- [ConversationManagerDelegate](https://developer.apple.com/documentation/livecommunicationkit/conversationmanagerdelegate)
- [ConversationAction](https://developer.apple.com/documentation/livecommunicationkit/conversationaction)
- [StartConversationAction](https://developer.apple.com/documentation/livecommunicationkit/startconversationaction)
- [Conversation.Event](https://developer.apple.com/documentation/livecommunicationkit/conversation/event)
- [Conversation.Update](https://developer.apple.com/documentation/livecommunicationkit/conversation/update)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Handling audio interruptions](https://developer.apple.com/documentation/avfaudio/handling-audio-interruptions)
- [Responding to audio route changes](https://developer.apple.com/documentation/avfaudio/responding-to-audio-route-changes)
- [Notifications HIG](https://developer.apple.com/design/human-interface-guidelines/notifications)
- [Managing Notifications HIG](https://developer.apple.com/design/human-interface-guidelines/managing-notifications)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
