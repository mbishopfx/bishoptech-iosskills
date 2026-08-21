# CallKit, LiveCommunicationKit, and VoIP route

Use this recipe when an app needs native incoming/outgoing call behavior, a VoIP service coordinated with the system, a default calling role, or a documented default-dialer route. Start with the smallest system contract that matches the user outcome.

The route is:

    call intent or server invitation
        -> account/call validation
        -> system provider/manager action
        -> system call UI
        -> provider delegate action
        -> media and audio session
        -> call state reconciliation
        -> end/reset/fallback

## Choose the route

| Requirement | Use | Extra boundaries |
| --- | --- | --- |
| Incoming VoIP call | PushKit + CallKit or LiveCommunicationKit | APNs token/environment, server invite, call UUID, media |
| Outgoing VoIP call | CallKit CXCallController or LiveCommunicationKit ConversationManager | Signaling, provider action, audio |
| App-owned call controls | CallKit CXProviderDelegate or ConversationManagerDelegate | Fulfill/fail, timeout, reset |
| Default calling app preparation | CallKit or LiveCommunicationKit | Calling-app entitlement, user selection, VoIP fallback |
| Default dialer preparation | LiveCommunicationKit | Default Dialer App entitlement, EU developer/device testing, cellular conversation |
| Ordinary chat/message notification | User Notifications | Permission, communication notification, Focus, privacy |
| Call audio | AVFAudio AVAudioSession | Activation/deactivation, route changes, interruptions |

CallKit and LiveCommunicationKit are system coordination layers. They do not replace the provider, backend, identity, encryption, media stack, or APNs configuration.

## Domain state before system state

Keep the call record independent from CXCall, Conversation, and audio framework objects:

~~~swift
struct CallRecord: Codable, Hashable, Sendable {
    enum State: String, Codable, Sendable {
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
        case failed
        case reset
    }

    var id: String
    var systemUUID: UUID
    var recipientLabel: String
    var handleValue: String
    var method: String
    var state: State
    var providerCallID: String?
    var startedAt: Date?
    var endedAt: Date?
}
~~~

A UUID is a correlation identifier, not a participant identity. Keep server call IDs, account IDs, handles, and system UUIDs in separate reviewed fields.

## Route A: incoming VoIP with PushKit and CallKit

### A1. Register the push route

At app launch:

1. Create PKPushRegistry with the intended queue.
2. Assign the delegate.
3. Set the desired VoIP push type.
4. Receive the opaque device token and APNs environment.
5. Register the token with the server over a controlled authenticated path.

Do not register VoIP pushes for ordinary background work. Apple’s current PushKit guidance says that an app linked against the iOS 13 SDK or later must use CallKit when handling VoIP calls.

### A2. Validate and report

When a VoIP payload arrives:

1. Parse only the fields needed to identify the invitation.
2. Validate account, token, expiry, call ID, and duplicate state.
3. Create or recover a stable UUID.
4. Build CXCallUpdate with accurate caller/handle/capabilities.
5. Call reportNewIncomingCall on the provider.
6. Reconcile success or error with the server.

If the system rejects the report, mark the invitation as rejected/expired and do not display a private incoming-call replica. If the report succeeds, wait for the provider’s answer/end action.

### A3. Answer and connect

When CallKit asks the provider to answer:

1. Confirm the call record is still valid.
2. Connect or accept the remote service.
3. Configure and activate AVAudioSession when the media path is ready.
4. Fulfill the action only when the provider is ready for the promised state.
5. Report connecting/connected state.

If the service cannot connect, fail the action, report the call-ended reason, deactivate media, and reconcile the server invitation.

## Route B: outgoing VoIP with CallKit

### B1. Request a system start action

The app-owned dialer reviews the recipient, then creates a CXStartCallAction with a stable UUID and CXHandle. Put the action in a CXTransaction and request it with CXCallController.

The system/provider callback then owns the next step. Do not connect media from the button handler and separately ask CallKit to catch up.

### B2. Handle provider callbacks

The provider delegate:

- validates the call record;
- starts service signaling;
- reports outgoing connection progress;
- activates audio through the audio coordinator;
- fulfills or fails the start action;
- reports end state and reason.

Duplicate start actions must be idempotent by system UUID and server call ID. A timeout should leave the call in an explicit retryable/failed state, not in an indefinite spinner.

## Route C: LiveCommunicationKit

### C1. Configure the manager

Use ConversationManager when the product wants the conversation-oriented LiveCommunicationKit contract. The manager exposes active conversations and pending actions, performs arrays of ConversationAction values asynchronously, reports incoming conversations, reports conversation events, and invalidates on reset.

The delegate receives manager lifecycle, conversation changes, audio activation/deactivation, requested actions, and action timeouts. Each action has a UUID, conversation UUID, timeout date, and fulfill/fail completion.

### C2. Start and report a conversation

For an outgoing VoIP conversation:

1. Create a conversation UUID.
2. Create a StartConversationAction with the intended handles and video capability.
3. Perform it through ConversationManager.
4. Connect the real VoIP service.
5. Report conversationStartedConnecting.
6. Report conversationConnected when media/service state agrees.
7. Report conversationEnded with an appropriate reason.

For incoming calls, use the documented reportNewIncomingConversation route or the PushKit payload handoff supported by the selected SDK. Treat the system’s allowed/disallowed result as a boundary and reconcile the server.

### C3. Default calling app

If the app is preparing to be the default calling app:

- add and verify the documented calling-app entitlement;
- provide real VoIP conversation functionality;
- explain the user-selected system role;
- handle tel-link and contact-card entry;
- provide the documented cellular/system fallback when VoIP fails;
- test system settings selection and non-selected state separately.

### C4. Default dialer

If the app is preparing to be the default dialer:

- add and verify the Default Dialer App entitlement;
- use StartCellularConversationAction and TelephonyConversationManager as documented;
- test with the required developer account and EU device location;
- distinguish confirmation when the app is not the selected default from no-confirmation behavior when it is selected;
- treat ConversationHistoryManager as a protected, role-specific route.

Do not offer default-dialer behavior as a generic setting in a worldwide app without checking current regional, account, entitlement, and device requirements.

## Audio route

Use a single call-owned audio coordinator:

~~~swift
import AVFAudio

@MainActor
final class CallAudioCoordinator {
    private let session = AVAudioSession.sharedInstance()

    func activateForCall() throws {
        try session.setCategory(.playAndRecord, mode: .voiceChat, options: [
            .allowBluetooth,
            .allowBluetoothA2DP
        ])
        try session.setActive(true)
    }

    func deactivateAfterCall() throws {
        try session.setActive(false, options: .notifyOthersOnDeactivation)
    }
}
~~~

The exact category, mode, options, and platform support depend on the media product. Observe interruption and route-change notifications. Deactivate when the call ends or system manager deactivates the audio session. Do not leave audio active because a SwiftUI view disappeared.

## App-owned UI and Liquid Glass

The app-owned screens should model:

    recipient review
        -> requesting
        -> system call surface
        -> connecting
        -> connected
        -> held/muted/media-failed
        -> ended/failed

Use semantic SwiftUI controls, clear state copy, and restrained Liquid Glass grouping for in-call controls. Do not mimic the Phone app or replace a system surface with a glass overlay. Keep accessibility and reduced-effects alternatives visible in the implementation plan.

## AI proposal route

For a voice assistant or on-device AI dialer:

    natural-language request
        -> candidate contacts/handles
        -> account and service validation
        -> recipient/method confirmation
        -> CallKit/LiveCommunicationKit action
        -> provider/media result

AI can prepare a candidate handle or draft a call note. It cannot silently choose among ambiguous recipients, bypass system confirmation, start cellular calling without the documented path, or claim connection from model output. If transcription or summarization is used, require consent and separate the transcript from the approved record.

## Fallback route

| Failure | Fallback |
| --- | --- |
| PushKit unavailable or no valid token | Normal notification/account recovery; no fake call |
| System rejects incoming report | Reconcile invitation and show no private incoming UI |
| Provider unavailable | Fail action and offer retry/support |
| VoIP connection fails | Documented cellular/system fallback when eligible |
| User has not selected default role | Show system choice/fallback, not an app-owned claim |
| Audio route unavailable | Explain media state, retry route, or end safely |
| Microphone denied | Keep call state explicit and offer Settings/help |
| App reset or logout | Invalidate provider/manager, end local service, clear account-bound state |
| AI unavailable | Manual contact selection and standard call action |

## Minimum slices

1. Fixture-only call state and in-call UI.
2. CallKit outgoing transaction with a fake provider action.
3. Signed physical-device CallKit incoming report in a controlled environment.
4. PushKit/APNs token and server invite reconciliation.
5. Real audio route, interruption, Bluetooth, and teardown.
6. LiveCommunicationKit manager/action route.
7. Default calling/dialer only after entitlement, region, user-choice, and physical proof are available.

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
- [Notifications HIG](https://developer.apple.com/design/human-interface-guidelines/notifications)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
