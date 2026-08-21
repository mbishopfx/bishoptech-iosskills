# SwiftUI LiveCommunicationKit calling route

Use this route to turn a calling idea into an Apple system conversation plan. Start with the smallest supported lane, document who owns the system surface and who owns the media service, and stop when a missing entitlement, region, account, or physical-service prerequisite requires product direction.

Related material:

- [LiveCommunicationKit framework review](../42-framework-deep-dives/121-swiftui-live-communication-kit-calling-review.md)
- [LiveCommunicationKit design review](../21-design-deep-dives/149-swiftui-live-communication-kit-calling-review-design.md)
- [LiveCommunicationKit proof matrix](../60-verification/146-swiftui-live-communication-kit-calling-proof-matrix.md)
- [LiveCommunicationKit code recipes](../70-code-recipes/164-swiftui-live-communication-kit-calling-review-recipes.md)

## 1. Define the conversation outcome

Write:

    A person wants to [call/answer/translate/review] [recipient]
    using [VoIP/cellular/system fallback] so [outcome].

Then select one primary route:

| Outcome | Route |
| --- | --- |
| App-owned VoIP | ConversationManager |
| Existing legacy VoIP integration | CallKit CXProvider/CXCallController |
| Incoming wake-up | PushKit plus system call reporting |
| Default calling app | calling-app entitlement and VoIP route |
| Default dialer/cellular | dialing-app entitlement and TelephonyConversationManager |
| Call history | ConversationHistoryManager in its documented scope |
| Translation | SetTranslatingAction and engine policy |

An AI summary, notification, contact card, or history row is a trigger or proposal, not proof of a call connection.

## 2. Route configuration worksheet

Record:

| Field | Decision |
| --- | --- |
| Deployment target and SDK | Exact target and Xcode SDK |
| Framework | LiveCommunicationKit, CallKit, PushKit, AVFAudio |
| Call type | Audio, video, or both |
| Handles | Phone number, email address, or generic |
| Service | Signaling, media, authentication, and account owner |
| Calling-app entitlement | Required/not required/requested/approved |
| Dialing-app entitlement | Required/not required/requested/approved |
| Background mode | voip configuration and target |
| PushKit | VoIP push used/not used, provider path |
| Fallback | Telephony URL or TelephonyConversationManager |
| History | App-owned, system projection, or default-dialer route |
| Translation | Off/system/custom, language pairs, input/mute policy |
| AI | Disabled/proposal-only/explicit review |
| Physical proof | Devices, accounts, carrier, audio routes |

Do not call an entitlement “available” because an entitlements file exists. Inspect the signed archive and test the eligible account/device.

## 3. Preflight

Before a Call action:

1. Validate the recipient handle and current account.
2. Confirm the selected route is enabled for the target.
3. Confirm calling/dialer entitlement state when applicable.
4. Confirm PushKit and voip background configuration for incoming calls.
5. Confirm the app can initialize its service connection.
6. Confirm the system conversation manager is alive and not reset.
7. Confirm the user explicitly chose the action.
8. Create a call attempt ID and framework UUID.
9. Show the correct system/app ownership copy.

For a default dialer path, also evaluate the region/account/device condition. For a translation path, check language and engine availability before offering the control.

## 4. Configure ConversationManager

Create one manager for the service context using the current Configuration initializer. Set:

- ringtone and template icon assets;
- maximum conversation groups/conversations;
- whether calls appear in Recents;
- video support;
- supported handle types;
- audio-translation support.

Retain the manager strongly and assign a single delegate. Pass value events to a MainActor feature model.

Recommended ownership:

    AppCallService
      - ConversationManager
      - service connection
      - media session
      - audio graph
      - call reducer
      - action dedupe
      - timeout/recovery

The SwiftUI screen observes the reducer; it does not own the live manager.

## 5. Outgoing VoIP route

The route is:

    user reviews handle
      -> StartConversationAction
      -> manager.perform
      -> server/service start
      -> report conversationStartedConnecting
      -> AVAudioSession activation
      -> media service ready
      -> report conversationConnected
      -> joined UI

Use one action UUID and one server call ID. If the action times out, fail it and do not continue a late connection without reconciling the call’s current state.

The system call UI should receive status updates based on actual service events. A StartConversationAction fulfillment does not by itself mean that the remote participant answered.

## 6. Incoming VoIP route

Incoming:

    server
      -> APNs VoIP push
      -> PKPushRegistry delegate
      -> bounded payload/decrypt/identity validation
      -> report incoming system conversation
      -> establish service connection
      -> JoinConversationAction
      -> media ready
      -> joined

Use CallKit as required by PushKit documentation for VoIP pushes, or use the documented LiveCommunicationKit incoming path for the target. Do not post a user notification instead of the required system call surface when the app has accepted VoIP pushes.

If the person answers before the service is ready, keep the action pending and fulfill only when the join policy is met. If the service fails, report the failure and end the system call state.

## 7. Delegate action reducer

Map actions to deterministic commands:

| Action | Validate | Complete when |
| --- | --- | --- |
| Start | handle, account, duplicate call | service accepted and call policy says started |
| Join | incoming UUID and authorization | media service joined |
| End | current conversation and revision | service ended or local end is safely recorded |
| Mute | current media state | app input policy applied |
| Pause | capability and media state | media paused/resumed |
| Merge | both conversations and capability | service and system state merged |
| PlayTone | tone policy and active media | service sent tone |
| Translate | language pair and engine | selected engine active; fulfill with engine |

Every action must have:

- a timeout date;
- an idempotency key;
- a current conversation revision;
- a safe failure path;
- a sanitized diagnostic outcome.

## 8. Audio-session route

Use ConversationManagerDelegate AVAudioSession activation/deactivation callbacks:

1. On activation, configure the app’s audio graph for the system-provided session.
2. Start service media only when the graph and remote path are ready.
3. Handle route changes and interruptions without losing the conversation record.
4. On deactivation, stop or suspend the graph and release temporary resources.
5. Report the app’s media result separately from system activation.

Test receiver, speaker, Bluetooth, wired/USB, interruption, media-services reset, no-input, and translation mute behavior. Do not promise a route name the device did not report.

## 9. Default calling app route

Add and prove the calling-app entitlement only when the product supports full VoIP functionality. Configure the voip background mode and link the intended framework according to Apple’s submission guidance.

For a system-provided phone handle:

    received handle
      -> show the proposed recipient
      -> user confirms
      -> app attempts VoIP
      -> if it cannot provide VoIP, explicit telephony fallback

The fallback telephony URL is a user-driven recovery action. It must not be opened from a background callback or generated suggestion.

## 10. Default dialer route

The default dialer route has a separate entitlement and regional proof. For the documented EU test boundary:

1. Validate the phone number.
2. Check the app’s default-dialer state.
3. Choose a CellularService only if needed.
4. Create StartCellularConversationAction.
5. Call TelephonyConversationManager.sharedInstance.
6. Handle confirmation, rejection, carrier failure, and system routing.
7. Show “requested” versus “connected” distinctly.

If the app is not the configured default dialer, the person may receive a confirmation dialog. Do not hard-code the no-confirmation design.

## 11. History route

Use ConversationHistoryManager only for the documented history context:

    default dialer eligible
      -> predicate recent conversations
      -> show bounded rows
      -> mark read explicitly
      -> revalidate handle
      -> user starts follow-up

Observe conversation-history update messages and refresh the value projection. Do not keep a permanent copy of all system history without a separate product/privacy decision.

## 12. Translation route

Offer translation only when the manager configuration advertises support and the app has an actual engine:

    selected language pair
      -> SetTranslatingAction
      -> configure system/custom engine
      -> keep input policy correct
      -> fulfill with TranslationEngine
      -> report delay/failure

Keep the upstream audio behavior compatible with the documented mute rule. If translation is unavailable, the call remains useful with original audio.

## 13. SwiftUI and scene route

The feature model holds:

    enum CallState {
        case idle
        case incoming(Recipient)
        case connecting
        case joined
        case paused
        case translating
        case interrupted
        case ending
        case ended
        case failed(CallFailure)
    }

The service layer holds live objects and sends events:

    system delegate
      -> CallEvent
      -> reducer
      -> SwiftUI projection

Cold launch and warm launch must both reconcile the same framework UUID/server ID. Scene phase changes should update presentation but must not end an active system conversation simply because the app screen is not visible.

## 14. AI route

Allow AI to propose:

- a follow-up note from a user-approved transcript;
- a contact label;
- a translated draft;
- a call destination from a user-edited query;
- a summary after the conversation.

Require:

- source and revision;
- on-device availability/fallback;
- recipient/content preview;
- explicit accept/edit/discard;
- fresh authorization and current conversation check.

Never let a generated result perform StartConversationAction, TelephonyConversationManager, End, translation, or history mutation without a user-approved deterministic command.

## 15. Fixture and proof plan

Test:

- outgoing VoIP connects;
- outgoing service rejects;
- incoming VoIP push cold-launches;
- incoming push has invalid UUID/handle;
- answer before media readiness;
- action timeout;
- duplicate action;
- remote end;
- local end;
- audio activation/deactivation;
- Bluetooth/speaker/receiver routes;
- interruption/reset;
- translation default/custom/unavailable;
- calling-app fallback;
- default-dialer confirmation;
- EU account/device/carrier conditions;
- history read/update/mark-read;
- AI proposal stale revision and unavailable model;
- accessibility and reduced effects.

The [proof matrix](../60-verification/146-swiftui-live-communication-kit-calling-proof-matrix.md) defines the evidence level for each case.

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
- [JoinConversationAction](https://developer.apple.com/documentation/livecommunicationkit/joinconversationaction)
- [EndConversationAction](https://developer.apple.com/documentation/livecommunicationkit/endconversationaction)
- [MuteConversationAction](https://developer.apple.com/documentation/livecommunicationkit/muteconversationaction)
- [PauseConversationAction](https://developer.apple.com/documentation/livecommunicationkit/pauseconversationaction)
- [PlayToneAction](https://developer.apple.com/documentation/livecommunicationkit/playtoneaction)
- [SetTranslatingAction](https://developer.apple.com/documentation/livecommunicationkit/settranslatingaction)
- [ConversationHistoryManager](https://developer.apple.com/documentation/livecommunicationkit/conversationhistorymanager)
- [TelephonyConversationManager](https://developer.apple.com/documentation/livecommunicationkit/telephonyconversationmanager)
- [StartCellularConversationAction](https://developer.apple.com/documentation/livecommunicationkit/startcellularconversationaction)
- [CellularService](https://developer.apple.com/documentation/livecommunicationkit/cellularservice)
- [CallKit](https://developer.apple.com/documentation/callkit)
- [CXProvider](https://developer.apple.com/documentation/callkit/cxprovider)
- [CXCallController](https://developer.apple.com/documentation/callkit/cxcallcontroller)
- [PushKit](https://developer.apple.com/documentation/pushkit)
- [Supporting PushKit Notifications in Your App](https://developer.apple.com/documentation/pushkit/supporting-pushkit-notifications-in-your-app)
- [Responding to VoIP Notifications from PushKit](https://developer.apple.com/documentation/pushkit/responding-to-voip-notifications-from-pushkit)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
