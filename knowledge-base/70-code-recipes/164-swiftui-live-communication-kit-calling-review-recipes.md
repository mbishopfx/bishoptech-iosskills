# SwiftUI LiveCommunicationKit calling code recipes

These are compile-oriented sketches for [the LiveCommunicationKit review](../42-framework-deep-dives/121-swiftui-live-communication-kit-calling-review.md). They separate system actions, app-owned service state, AVAudioSession, PushKit, translation, history, AI proposals, and user review. Compile each selected API against the named iOS 26 target; the snippets are not provider, entitlement, App Review, or physical-call proof.

Related pages:

- [LiveCommunicationKit route](../50-capability-recipes/152-swiftui-live-communication-kit-calling-review-route.md)
- [LiveCommunicationKit design review](../21-design-deep-dives/149-swiftui-live-communication-kit-calling-review-design.md)
- [LiveCommunicationKit proof matrix](../60-verification/146-swiftui-live-communication-kit-calling-proof-matrix.md)

## Recipe 1: route and value state

Keep the system conversation object out of SwiftUI view identity:

~~~swift
import Foundation

enum CallLane: Sendable, Hashable {
    case voip
    case cellular
    case fallback
    case history
    case translation
}

enum CallState: Sendable, Equatable {
    case idle
    case incoming
    case connecting
    case joined
    case paused
    case translating
    case interrupted
    case ending
    case ended
    case failed(String)
}

struct CallIdentity: Sendable, Hashable {
    let frameworkUUID: UUID
    let serverID: String?
    let handleKind: String
    let redactedHandle: String
}

struct CallProposal: Sendable, Equatable {
    let sourceRevision: String
    let recipient: String
    let purpose: String
    let generatedBy: String
}
~~~

The framework UUID, server ID, account ID, handle, and display name are separate values. A display name is not proof of remote identity.

## Recipe 2: manager configuration

Build one ConversationManager for the app-owned communication service:

~~~swift
import LiveCommunicationKit
import Foundation

@MainActor
final class ConversationService: NSObject {
    let manager: ConversationManager

    init() {
        let configuration = ConversationManager.Configuration(
            ringtoneName: "IncomingCall",
            iconTemplateImageData: nil,
            maximumConversationGroups: 1,
            maximumConversationsPerConversationGroup: 1,
            includesConversationInRecents: true,
            supportsVideo: false,
            supportedHandleTypes: [.phoneNumber, .emailAddress],
            supportsAudioTranslation: true
        )
        manager = ConversationManager(configuration: configuration)
        super.init()
    }
}
~~~

The initializer and Handle.Kind cases must be compiled against the current SDK. Configure only capabilities the media service and product can actually fulfill. Keep the manager alive for the service lifetime and do not reconstruct it in a SwiftUI body.

## Recipe 3: ConversationManager delegate

Use a delegate to translate framework events into a reducer:

~~~swift
import AVFAudio
import LiveCommunicationKit

@MainActor
final class ConversationDelegate: NSObject, ConversationManagerDelegate {
    let onState: @MainActor (String) -> Void

    init(onState: @escaping @MainActor (String) -> Void) {
        self.onState = onState
    }

    func conversationManagerDidBegin(
        _ conversationManager: ConversationManager
    ) {
        onState("manager-began")
    }

    func conversationManagerDidReset(
        _ conversationManager: ConversationManager
    ) {
        onState("manager-reset")
    }

    func conversationManager(
        _ conversationManager: ConversationManager,
        conversationChanged conversation: Conversation
    ) {
        onState("conversation-\(conversation.uuid)-\(conversation.state)")
    }

    func conversationManager(
        _ conversationManager: ConversationManager,
        didActivate audioSession: AVAudioSession
    ) {
        onState("audio-activated-\(audioSession.category.rawValue)")
    }

    func conversationManager(
        _ conversationManager: ConversationManager,
        didDeactivate audioSession: AVAudioSession
    ) {
        onState("audio-deactivated")
    }

    func conversationManager(
        _ conversationManager: ConversationManager,
        perform action: ConversationAction
    ) {
        onState("action-\(action.uuid)")
        // Route to an idempotent action executor.
    }

    func conversationManager(
        _ conversationManager: ConversationManager,
        timedOutPerforming action: ConversationAction
    ) {
        onState("action-timeout-\(action.uuid)")
        action.fail()
    }
}
~~~

The exact isolation annotations may differ under the selected SDK’s concurrency checking. The delegate must be retained, action deadlines must be respected, and callbacks must not mutate a discarded SwiftUI generation.

## Recipe 4: start an outgoing VoIP conversation

Use an explicit, reviewed handle:

~~~swift
import LiveCommunicationKit
import Foundation

@MainActor
func startVoIP(
    manager: ConversationManager,
    handles: [Handle],
    isVideo: Bool
) async throws -> UUID {
    precondition(!handles.isEmpty)
    let uuid = UUID()
    let action = StartConversationAction(
        conversationUUID: uuid,
        handles: handles,
        isVideo: isVideo
    )
    try await manager.perform([action])
    return uuid
}
~~~

Receiving a successful perform call is not proof that the remote participant connected. Report conversationStartedConnecting and conversationConnected only from service evidence.

## Recipe 5: report conversation events

Map app-owned service facts into system events:

~~~swift
import LiveCommunicationKit
import Foundation

@MainActor
func reportConnecting(
    manager: ConversationManager,
    conversation: Conversation
) {
    manager.reportConversationEvent(
        .conversationStartedConnecting(Date()),
        for: conversation
    )
}

@MainActor
func reportConnected(
    manager: ConversationManager,
    conversation: Conversation
) {
    manager.reportConversationEvent(
        .conversationConnected(Date()),
        for: conversation
    )
}

@MainActor
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

Use the actual current ended-reason enum and event signatures from the SDK. Do not report connected when only signaling has started.

## Recipe 6: fulfill actions idempotently

Keep action execution in a service actor or serialized feature object:

~~~swift
import LiveCommunicationKit
import Foundation

actor CallActionExecutor {
    private var completedActions = Set<UUID>()

    func execute(
        _ action: ConversationAction,
        operation: @Sendable () async throws -> Void
    ) async {
        guard !completedActions.contains(action.uuid) else {
            return
        }
        guard action.state != .completed else {
            return
        }

        do {
            try await operation()
            completedActions.insert(action.uuid)
            action.fulfill()
        } catch {
            action.fail()
        }
    }
}
~~~

The exact ConversationAction.State cases and action subclass completion behavior must be compiled against the SDK. StartConversationAction may have a specialized fulfillment method that records its start date. Use that method when the current SDK requires it.

## Recipe 7: incoming conversation

Report a validated incoming conversation:

~~~swift
import LiveCommunicationKit
import Foundation

@MainActor
func reportIncoming(
    manager: ConversationManager,
    callUUID: UUID,
    remote: Handle
) async throws {
    let update = Conversation.Update(
        localMember: nil,
        members: [remote],
        activeRemoteMembers: nil,
        capabilities: [.pausing]
    )
    try await manager.reportNewIncomingConversation(
        uuid: callUUID,
        update: update
    )
}
~~~

Do not use a model-generated handle or unverified push string as the remote identity. Resolve it through the service/authentication policy first, then pass the minimum safe data to the system.

## Recipe 8: PushKit registration

Register only the push types the app actually handles:

~~~swift
import PushKit

final class VoIPPushCoordinator: NSObject, PKPushRegistryDelegate {
    private let registry: PKPushRegistry

    override init() {
        registry = PKPushRegistry(queue: .main)
        super.init()
        registry.delegate = self
        registry.desiredPushTypes = [.voIP]
    }

    func pushRegistry(
        _ registry: PKPushRegistry,
        didUpdate pushCredentials: PKPushCredentials,
        for type: PKPushType
    ) {
        guard type == .voIP else { return }
        // Send a token representation to the authenticated provider.
    }

    func pushRegistry(
        _ registry: PKPushRegistry,
        didReceiveIncomingPushWith payload: PKPushPayload,
        for type: PKPushType,
        completion: @escaping () -> Void
    ) {
        guard type == .voIP else {
            completion()
            return
        }
        // Validate bounded payload, report system call promptly,
        // establish service connection, then call completion.
        completion()
    }
}
~~~

Apple’s current PushKit guidance requires a VoIP push to be used for a live call route and reported to CallKit. The exact incoming LiveCommunicationKit handoff must be compiled from the target SDK. Do not use this path for ordinary notifications or background model work.

## Recipe 9: legacy CallKit provider comparison

If the app uses CallKit, create one provider and report incoming calls:

~~~swift
import CallKit
import Foundation

final class CallKitProviderCoordinator: NSObject, CXProviderDelegate {
    let provider: CXProvider

    override init() {
        let configuration = CXProviderConfiguration(localizedName: "VoIP Service")
        configuration.supportsVideo = true
        configuration.supportedHandleTypes = [.phoneNumber, .emailAddress]
        provider = CXProvider(configuration: configuration)
        super.init()
        provider.setDelegate(self, queue: nil)
    }

    func reportIncoming(uuid: UUID, handle: String) {
        let update = CXCallUpdate()
        update.remoteHandle = CXHandle(
            type: .phoneNumber,
            value: handle
        )
        provider.reportNewIncomingCall(
            with: uuid,
            update: update
        ) { error in
            // Store a sanitized result, never the raw payload.
            _ = error
        }
    }

    func providerDidReset(_ provider: CXProvider) {
        // Clear provider-owned pending media actions.
    }
}
~~~

Do not report the same physical/service call to both CallKit and LiveCommunicationKit without a deliberate migration strategy. Double reporting can produce conflicting system state.

## Recipe 10: default dialer cellular fallback

Use the documented LiveCommunicationKit cellular route:

~~~swift
import LiveCommunicationKit

@MainActor
func startCellularFallback(
    phoneNumber: String,
    cellularService: CellularService? = nil
) async throws {
    let handle = Handle(
        type: .phoneNumber,
        value: phoneNumber
    )
    let action = StartCellularConversationAction(
        handle,
        cellularService: cellularService
    )
    try await TelephonyConversationManager.sharedInstance
        .startCellularConversation(action)
}
~~~

This code does not grant the Default Dialer App entitlement. Verify the signed capability, EU account/device test condition, current default-app state, and explicit user intent before calling it.

## Recipe 11: telephony URL fallback

When the app is the default calling app and VoIP fails, construct the fallback only in response to a visible user action:

~~~swift
import UIKit
import Foundation

@MainActor
func openTelephonyFallback(phoneNumber: String) {
    var components = URLComponents()
    components.scheme = "telephony"
    components.path = phoneNumber
    guard let url = components.url else { return }
    UIApplication.shared.open(url)
}
~~~

The exact URL construction should follow Apple’s current default-calling guidance and the app’s handle-validation policy. Do not open this from an incoming push, background task, or model callback.

## Recipe 12: recent conversation history

Query history with a typed predicate and update the UI on the main actor:

~~~swift
import Foundation
import LiveCommunicationKit

@MainActor
@Observable
final class RecentConversationModel {
    var rows: [ConversationHistoryManager.RecentConversation] = []
    private let history = ConversationHistoryManager.sharedInstance

    func refresh() async {
        let predicate = #Predicate<
            ConversationHistoryManager.RecentConversation
        > { _ in true }

        do {
            rows = try await history.recentConversations(
                matching: predicate
            )
        } catch {
            rows = []
        }
    }

    func markRead(
        _ row: ConversationHistoryManager.RecentConversation
    ) async {
        try? await history.markConversationAsRead(row)
    }
}
~~~

History availability and scope depend on the documented default-dialer context. Do not treat this query as a complete universal call database.

## Recipe 13: translation action

Use SetTranslatingAction with explicit languages:

~~~swift
import LiveCommunicationKit
import Foundation

@MainActor
func performTranslation(
    manager: ConversationManager,
    conversation: Conversation,
    local: Locale.Language,
    remote: Locale.Language,
    enabled: Bool,
    engine: SetTranslatingAction.TranslationEngine
) async throws {
    let action = SetTranslatingAction(
        conversationID: conversation.uuid,
        isTranslating: enabled,
        localLanguage: local,
        remoteLanguage: remote
    )
    try await manager.perform([action])
    if enabled {
        action.fulfill(using: engine)
    } else {
        action.fulfill(using: engine)
    }
}
~~~

The actual custom/default engine operation must happen before fulfillment. The recipe only demonstrates action shape. Keep upstream audio active when the documented translation/mute semantics require it, and mute app input through the conversation action rather than deactivating the entire upstream path.

## Recipe 14: audio-session boundary

Keep the system-owned activation callback separate from media service state:

~~~swift
import AVFAudio

actor CallAudioController {
    private var isRunning = false

    func systemDidActivate(_ session: AVAudioSession) async throws {
        // Configure the graph for the system-provided session.
        try session.setActive(true)
        isRunning = true
    }

    func systemDidDeactivate(_ session: AVAudioSession) async {
        isRunning = false
        try? session.setActive(false)
        // Stop/release temporary graph resources.
    }

    func interruptionBegan() {
        isRunning = false
    }
}
~~~

The app’s actual media graph and interruption policy belong here, not in a view. Test route changes and media-services reset on physical hardware.

## Recipe 15: SwiftUI feature shell

Render a value projection and keep system manager ownership outside the body:

~~~swift
import SwiftUI

struct CallScreen: View {
    let state: CallState
    let recipient: String
    let onMute: () -> Void
    let onTranslate: () -> Void
    let onEnd: () -> Void

    var body: some View {
        VStack(spacing: 20) {
            Text(recipient)
                .font(.title2)
                .accessibilityAddTraits(.isHeader)

            Text(statusText)
                .accessibilityValue(statusText)

            HStack {
                Button("Mute", action: onMute)
                Button("Translate", action: onTranslate)
                Button("End call", role: .destructive, action: onEnd)
            }
            .buttonStyle(.glass)
        }
        .padding()
    }

    private var statusText: String {
        switch state {
        case .idle: "Ready"
        case .incoming: "Incoming call"
        case .connecting: "Connecting"
        case .joined: "Connected"
        case .paused: "Paused"
        case .translating: "Translation on"
        case .interrupted: "Audio interrupted"
        case .ending: "Ending"
        case .ended: "Call ended"
        case .failed(let message): message
        }
    }
}
~~~

The current SDK may use a different glass button style or availability annotation. The state labels, semantic actions, destructive treatment, and system-UI boundary are the important design constraints.

## Recipe 16: local AI proposal

Bound a transcript or user note before asking a model for a follow-up proposal:

~~~swift
import Foundation

struct CallAIInput: Codable, Sendable {
    let conversationID: UUID
    let sourceRevision: String
    let userApprovedText: String
    let allowedActions: [String]
}

struct CallAIProposal: Codable, Sendable, Equatable {
    let sourceRevision: String
    let suggestedTitle: String
    let suggestedBody: String
    let allowedAction: String?
}

func makeCallAIInput(
    conversationID: UUID,
    revision: String,
    text: String
) -> CallAIInput {
    CallAIInput(
        conversationID: conversationID,
        sourceRevision: revision,
        userApprovedText: String(text.prefix(12_000)),
        allowedActions: ["save-note", "draft-reply", "suggest-follow-up"]
    )
}
~~~

The model cannot initiate, end, mute, merge, or translate a live call from this envelope. A separate, explicit command must revalidate the current conversation and user intent.

## Recipe 17: stale-proposal guard

Keep proposals tied to the current call revision:

~~~swift
struct CallReviewContext: Sendable, Equatable {
    let conversationID: UUID
    let revision: String
    let state: CallState
}

func canCommit(
    proposal: CallAIProposal,
    current: CallReviewContext,
    acceptedAction: String
) -> Bool {
    proposal.sourceRevision == current.revision
        && proposal.allowedAction == acceptedAction
        && current.state != .ended
        && current.state != .failed("")
}
~~~

Use explicit error enums in production instead of comparing a particular failed string. This sketch demonstrates that a stale generated proposal cannot silently become a live conversation command.

## Recipe 18: proof-friendly state logging

Log sanitized state transitions:

~~~swift
import OSLog

let callLog = Logger(
    subsystem: "com.example.app",
    category: "conversation"
)

func logTransition(
    lane: String,
    frameworkID: UUID,
    state: String,
    actionID: UUID? = nil
) {
    callLog.info(
        "lane=\(lane, privacy: .public) frameworkID=\(frameworkID.uuidString, privacy: .private(mask: .hash)) state=\(state, privacy: .public) actionID=\(actionID?.uuidString ?? "none", privacy: .private(mask: .hash))"
    )
}
~~~

Do not log full phone numbers, email handles, PushKit payloads, transcripts, audio data, APDU-like provider data, or model prompts. Use a secure support export only when the person explicitly requests it and the retention policy permits it.

## Recipe 19: action tests

Use Swift Testing for the deterministic reducer:

~~~swift
import Testing
import Foundation

@Test
func lateStartDoesNotBecomeConnected() {
    var reducer = CallReducer()
    reducer.reduce(.startRequested)
    reducer.reduce(.actionTimedOut)
    reducer.reduce(.serviceConnectedAfterTimeout)

    #expect(reducer.state == .failed("Action expired"))
}

@Test
func staleProposalCannotStartCall() {
    let proposal = CallAIProposal(
        sourceRevision: "r1",
        suggestedTitle: "Call",
        suggestedBody: "Draft",
        allowedAction: "start-call"
    )
    let context = CallReviewContext(
        conversationID: UUID(),
        revision: "r2",
        state: .idle
    )

    #expect(
        canCommit(
            proposal: proposal,
            current: context,
            acceptedAction: "start-call"
        ) == false
    )
}
~~~

These tests do not prove system UI, PushKit, audio, carrier, default-app selection, or provider behavior. Pair them with the physical proof matrix.

## Recipe 20: implementation stop conditions

Stop and resolve the product boundary when:

- the app needs default-app entitlements that have not been approved;
- the default dialer test requires an EU account/device that is unavailable;
- the provider cannot fulfill actions before their timeout;
- a model output is being used as a recipient or call-state authority;
- the app reports Connected without service/media evidence;
- the only incoming-call test is a local notification;
- the system audio session is being activated by a SwiftUI view;
- a telephony fallback can run without explicit user action;
- privacy copy does not explain system recipient sharing or transcript/translation handling.

## Sources

- [LiveCommunicationKit](https://developer.apple.com/documentation/livecommunicationkit)
- [Initiating VoIP conversations with LiveCommunicationKit](https://developer.apple.com/documentation/livecommunicationkit/initiating-voip-conversations-with-livecommunicationkit)
- [Preparing your app to be the default calling app](https://developer.apple.com/documentation/callkit/preparing-your-app-to-be-the-default-calling-app)
- [Preparing your app to be the default dialer app](https://developer.apple.com/documentation/livecommunicationkit/preparing-your-app-to-be-the-default-dialer-app)
- [ConversationManager](https://developer.apple.com/documentation/livecommunicationkit/conversationmanager)
- [ConversationManager.Configuration](https://developer.apple.com/documentation/livecommunicationkit/conversationmanager/configuration-swift.struct)
- [ConversationManagerDelegate](https://developer.apple.com/documentation/livecommunicationkit/conversationmanagerdelegate)
- [Conversation](https://developer.apple.com/documentation/livecommunicationkit/conversation)
- [Conversation.State](https://developer.apple.com/documentation/livecommunicationkit/conversation/state-swift.enum)
- [Conversation.Event](https://developer.apple.com/documentation/livecommunicationkit/conversation/event)
- [Conversation.Update](https://developer.apple.com/documentation/livecommunicationkit/conversation/update)
- [Conversation.Capabilities](https://developer.apple.com/documentation/livecommunicationkit/conversation/capabilities)
- [ConversationAction](https://developer.apple.com/documentation/livecommunicationkit/conversationaction)
- [StartConversationAction](https://developer.apple.com/documentation/livecommunicationkit/startconversationaction)
- [SetTranslatingAction](https://developer.apple.com/documentation/livecommunicationkit/settranslatingaction)
- [ConversationHistoryManager](https://developer.apple.com/documentation/livecommunicationkit/conversationhistorymanager)
- [TelephonyConversationManager](https://developer.apple.com/documentation/livecommunicationkit/telephonyconversationmanager)
- [StartCellularConversationAction](https://developer.apple.com/documentation/livecommunicationkit/startcellularconversationaction)
- [CellularService](https://developer.apple.com/documentation/livecommunicationkit/cellularservice)
- [Handle](https://developer.apple.com/documentation/livecommunicationkit/handle)
- [CallKit](https://developer.apple.com/documentation/callkit)
- [CXProvider](https://developer.apple.com/documentation/callkit/cxprovider)
- [CXCallController](https://developer.apple.com/documentation/callkit/cxcallcontroller)
- [PushKit](https://developer.apple.com/documentation/pushkit)
- [Supporting PushKit Notifications in Your App](https://developer.apple.com/documentation/pushkit/supporting-pushkit-notifications-in-your-app)
- [Responding to VoIP Notifications from PushKit](https://developer.apple.com/documentation/pushkit/responding-to-voip-notifications-from-pushkit)
- [PKPushType.voIP](https://developer.apple.com/documentation/pushkit/pkpushtype/voip)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing with Swift Testing](https://developer.apple.com/documentation/testing)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
