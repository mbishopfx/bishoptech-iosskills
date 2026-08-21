# SwiftUI LiveCommunicationKit and system calling review

LiveCommunicationKit is a system-integration framework for VoIP conversations, cellular-conversation routing, and apps that may become the default calling or dialer app. It is not a replacement for a VoIP service, a network signaling layer, or a promise that a call connected. The app still owns its service connection, audio/video media, authorization, identity, and recovery.

This review is for an iOS 26 target using the current Apple SDK. Compile the exact API against the target and confirm the current entitlement and regional rules before implementation. The system conversation UI, default-app selection, PushKit delivery, and carrier network are separate evidence surfaces.

Related material:

- [LiveCommunicationKit route](../50-capability-recipes/152-swiftui-live-communication-kit-calling-review-route.md)
- [LiveCommunicationKit design review](../21-design-deep-dives/149-swiftui-live-communication-kit-calling-review-design.md)
- [LiveCommunicationKit proof matrix](../60-verification/146-swiftui-live-communication-kit-calling-proof-matrix.md)
- [LiveCommunicationKit code recipes](../70-code-recipes/164-swiftui-live-communication-kit-calling-review-recipes.md)

## 1. Select the calling lane

| Product need | Starting route | System boundary |
| --- | --- | --- |
| VoIP incoming/outgoing conversations with Phone-like system behavior | LiveCommunicationKit ConversationManager | The app supplies the VoIP service and fulfills system actions |
| Existing CallKit integration | CallKit CXProvider/CXCallController | Keep one provider, report system state, and handle actions on the provider delegate |
| Incoming VoIP wake-up | PushKit plus CallKit or the documented LiveCommunicationKit handoff | A VoIP push is for a call invitation and must be reported to the system promptly |
| Let the person choose the app for VoIP calls | Default calling app route | Requires the documented calling-app entitlement and complete VoIP functionality |
| Let the app initiate cellular carrier calls as the default dialer | TelephonyConversationManager | Default Dialer App entitlement and EU account/device testing rules apply |
| Fall back to the system for a telephone call | Explicit telephony URL fallback or cellular action | Never open the fallback as an unreviewed side effect |
| Show recent carrier conversations | ConversationHistoryManager | Documented default-dialer context and history boundary |
| Translate call audio | SetTranslatingAction | Supports system/default or custom translation engine; audio routing remains a live-call concern |

Do not build a single “call” enum that hides these distinctions. A VoIP conversation, a cellular handoff, an incoming PushKit notification, and a translated audio action have different ownership and proof requirements.

## 2. LiveCommunicationKit’s ownership model

The framework presents the system conversation surface and routes actions. The app owns the service that makes audio/video packets flow. A healthy architecture looks like:

    system event or user intent
      -> ConversationManager action
      -> app service/session
      -> AVAudioSession activation
      -> media connection
      -> report conversation event
      -> system UI state
      -> app-owned review/record

The framework can:

- initiate and receive VoIP conversations;
- display a Phone-like interface that cooperates with system behaviors such as Do Not Disturb;
- coordinate conversations with other communication apps;
- request or perform conversation actions;
- report connection, update, and end events;
- prepare an app to be the default calling or dialer app.

It cannot:

- authenticate a remote account on behalf of the app;
- guarantee that a network conversation connected;
- replace a signaling server or media transport;
- infer that a user authorized a generated recipient;
- make a transcript, translation, or model summary the call record of truth.

The service must have one authoritative conversation identity. Keep the framework conversation UUID, server call ID, participant handle, media session ID, and local domain record as separate fields that can be reconciled.

## 3. ConversationManager configuration

ConversationManager is configured for the characteristics the system UI and action router need. The documented configuration includes:

- ringtone resource name;
- template icon image data;
- maximum conversation groups;
- maximum conversations per group;
- whether the conversation appears in Recents;
- video support;
- supported handle kinds;
- audio-translation support in the current initializer.

Treat configuration as a capability contract:

| Configuration | Product consequence |
| --- | --- |
| supportsVideo | The app must be able to start, join, pause, and end video state honestly |
| supportsAudioTranslation | The app must respond to SetTranslatingAction and fulfill with the engine actually used |
| supportedHandleTypes | Only advertise handles the service can resolve |
| maximum groups/conversations | The reducer and media service must handle the documented limit |
| includesConversationInRecents | A system projection can persist beyond the in-app screen |
| ringtone/icon | These are system-surface assets, not a substitute for app-owned design |

Create one manager for the service context and retain it. A SwiftUI body should never construct a new ConversationManager on every render. The manager has pending actions and conversations that need to survive view transitions.

## 4. Delegate and action lifecycle

ConversationManagerDelegate reports:

- manager began;
- manager reset;
- a conversation changed;
- the system activated the conversation’s AVAudioSession;
- the system deactivated the AVAudioSession;
- a conversation action must be performed;
- an action timed out.

The action lifecycle is:

    received
      -> validate conversation UUID and current state
      -> start app-owned media/service work
      -> fulfill or fail before timeout
      -> report a conversation event if state changed

ConversationAction has a conversation UUID, its own UUID, a timeout date, and state. It provides fulfill and fail. A late action must not be fulfilled merely because the server eventually responded. Compare the current conversation revision and action timeout before committing.

When the system asks the app to perform an action, the app must:

1. locate the domain conversation by framework UUID;
2. reject an unknown or stale conversation safely;
3. check authorization and service account state;
4. start the minimum network/media work needed;
5. update the domain reducer;
6. fulfill only when the requested action actually succeeded;
7. fail when it cannot be completed;
8. report a user-safe result;
9. retain a sanitized diagnostic identifier.

Do not call fulfill when a local button was tapped but the media service has not answered. “Requested” and “connected” are separate states.

## 5. Conversation state and events

The documented Conversation.State values include:

| State | Meaning |
| --- | --- |
| idle | Registered with the system but not active |
| joining | Setup is in progress |
| joined | Audio/video streams are active and the local participant can engage |
| paused | Audio/video streams are paused but may resume |
| leaving | Participants are leaving and the conversation is ending |
| left | The conversation is no longer active and sessions ended |

Conversation.Event reports app-owned facts to the system:

- conversationStartedConnecting;
- conversationConnected;
- conversationEnded with an ended reason;
- conversationUpdated with a Conversation.Update.

Report an event only when the app’s service has evidence for the claim. A network request accepted by a server is not necessarily a connected media path. A system UI transition is not a server acknowledgement.

Conversation.Update carries localMember, members, activeRemoteMembers, and capabilities. Capabilities can include merging, pausing, playing tones, unmerging, and video. Treat them as current conversation capabilities, not as static account permissions.

## 6. Conversation actions

The action families cover:

| Action | App-owned work |
| --- | --- |
| StartConversationAction | Resolve handles, create service call, start signaling |
| JoinConversationAction | Accept the incoming conversation and attach media |
| EndConversationAction | Stop service/media and report the ended state |
| MuteConversationAction | Mute the app’s input path while respecting translation semantics |
| PauseConversationAction | Pause/resume media according to the service protocol |
| MergeConversationAction | Validate that both conversations can be combined |
| UnmergeConversationAction | Restore the prior conversation relationships |
| PlayToneAction | Send the tone through the service, not through an unrelated local player |
| SetTranslatingAction | Start/stop the selected translation engine and fulfill with default/custom |

Each action has a deadline. Make action execution idempotent by action UUID and conversation revision. If an action arrives twice, return the already-known state when safe instead of starting a second media operation.

Do not let generated text select an action without deterministic allowlists and explicit review. An AI suggestion may say “call this contact,” but the app must resolve the handle, display it, validate it, and receive the user’s call intent.

## 7. Incoming VoIP and PushKit

PushKit is a delivery/wake-up path, not a generic background job system. Apple documents that VoIP pushes are for initiating live voice calls and that apps receiving VoIP pushes must report the call quickly to CallKit. Apps linked against the iOS 13 SDK or later can be terminated or stop receiving VoIP pushes when they repeatedly fail to report them appropriately.

The incoming route is:

    server call invitation
      -> APNs VoIP push
      -> PKPushRegistry delegate
      -> verify bounded payload and call UUID
      -> decrypt or resolve minimum caller data
      -> report incoming system call
      -> establish media/service connection
      -> fulfill Join/Answer only after connection policy

Use a notification service extension for documented decrypt-before-display work when appropriate. Do not use a VoIP push for a message, marketing event, or model task that is not an incoming call.

The payload should contain the minimum information needed to report the incoming call and reconcile the server call. Keep server-side identity and authorization checks outside the display name. A displayed caller name is a system projection, not proof that the remote party authenticated.

When the system lets the person answer, do not fulfill the answer/join action immediately if the service has not established the media connection. Apple’s CallKit guidance describes keeping the system UI in a connecting state until the connection is ready.

After the initial push, use the app’s active network connection for call updates and cancellation where possible. Do not send extra push notifications as a substitute for an established service channel.

## 8. Default calling app

The default calling app route allows a person to choose an app other than Phone or FaceTime to handle calls. Apple’s preparation guidance requires the Default Calling App entitlement:

    com.apple.developer.calling-app

The app must also meet the App Store Connect criteria Apple documents, including a VoIP background mode and linking CallKit or LiveCommunicationKit. A default calling app needs full VoIP functionality. It cannot be just a themed dialer that immediately punts every call to the system.

When the system sends a telephone intent to the default calling app:

1. validate the handle and show the proposed recipient;
2. attempt the app’s VoIP path;
3. if it cannot provide VoIP, use the documented telephony fallback only after explicit user action;
4. let the system handle the cellular conversation;
5. keep the UI truthful about whether the app or system owns the active call.

The telephony URL fallback uses the telephony scheme and must respond to an explicit action. Do not open it from a passive notification, an AI output, or a background event.

## 9. Default dialer app and cellular conversations

The Default Dialer App route is separate from being the default calling app. It focuses on initiating cellular carrier conversations through LiveCommunicationKit. The entitlement is:

    com.apple.developer.dialing-app

Apple’s current guidance requires an Apple Developer account registered in the EU and a test device located in the EU to test default-dialer behavior. Treat region and account checks as release gates, not optional UI copy.

The flow is:

    validated phone handle
      -> choose CellularService if the route needs one
      -> StartCellularConversationAction
      -> TelephonyConversationManager.startCellularConversation
      -> system/default-calling-app routing

If the app has the entitlement but is not configured as the default dialer, the person may see a confirmation dialog. If it is configured as the default dialer, Apple documents a different confirmation behavior. The UI must not promise a no-confirmation flow outside the tested default-app state.

TelephonyConversationManager exposes cellular services and a startCellularConversation method. The service list is limited by the system/default-app context. A missing service is not necessarily a failure if the system can still route the conversation.

## 10. Conversation history

ConversationHistoryManager is an access route for recent cellular conversation history in the documented default-dialer context. It can:

- fetch recent conversations with a typed predicate;
- mark one conversation read;
- mark multiple conversations read;
- publish a conversation-history update message.

Do not use it as an all-calls database. Apple describes history access from the point the app becomes the default dialer app. The app should show that scope and retain app-owned records only when the person has agreed to the product’s retention policy.

History rows need:

- stable framework/domain identifier;
- handle type/value presentation policy;
- incoming/outgoing/missed state;
- timestamp and duration when supplied;
- read state;
- app/service reconciliation state;
- action availability.

The row is not evidence that a call connected. Preserve the distinction between invitation, attempted, connected, ended, and unknown.

## 11. Translation actions

ConversationManager.Configuration can advertise supportsAudioTranslation. SetTranslatingAction includes:

- the conversation ID;
- whether translation is starting or stopping;
- local language;
- remote language.

The action is fulfilled with SetTranslatingAction.TranslationEngine, which distinguishes the system default engine from a custom engine. If the app implements custom translation, it owns the media and translation quality/failure semantics.

Apple documents an important mute boundary: when translating, do not deactivate the upstream audio simply because a person mutes the hardware microphone. Use MuteConversationAction to mute the app’s audio input while keeping the upstream audio active so translated audio can flow as designed.

Translation is still a live communication side effect:

- show local and remote language choices before enabling it;
- disclose whether the translation engine is system/default or custom;
- keep the original audio/transcript policy clear;
- handle asset/network/model unavailability;
- never present generated translation as a verbatim legal, medical, or contractual record;
- let the person turn translation off;
- measure delay and keep a fallback to original audio.

## 12. AVAudioSession ownership

The ConversationManager delegate tells the app when the system activates and deactivates the conversation’s AVAudioSession. Use those callbacks to start or stop the app’s media graph. Do not compete with the system by activating a separate unrelated audio session from a SwiftUI view.

Recommended audio state:

    idle
      -> service connecting
      -> system audio activated
      -> audio graph running
      -> route/interruption change
      -> audio graph paused/reconfigured
      -> system audio deactivated
      -> service ended

The app owns:

- input/output graph;
- codec and transport;
- route-aware media state;
- interruption and media-service reset recovery;
- mute/pause semantics;
- audio level or quality indicators.

The system owns:

- call UI;
- audio-session activation timing;
- user-facing interruption priority;
- route policies communicated through AVAudioSession.

On activation, configure the graph and start media only when the service is ready. On deactivation, stop or suspend the graph and release resources without deleting the domain call record. Test speaker, receiver, Bluetooth, wired/USB, AirPlay limitations, interruptions, route changes, and media-services reset.

## 13. CallKit comparison

CallKit remains the documented route for apps that already use CXProvider, CXCallController, CXCallUpdate, and CXCallAction subclasses. Apple’s PushKit guidance still requires CallKit for VoIP push handling. LiveCommunicationKit offers a newer conversation abstraction and default-app integration, but the route selected for a product must match its target, entitlements, and current framework support.

| Need | CallKit | LiveCommunicationKit |
| --- | --- | --- |
| Report an incoming VoIP call | CXProvider reportNewIncomingCall | ConversationManager incoming reporting in the documented route |
| User action handling | CXProviderDelegate and CXCallAction | ConversationManagerDelegate and ConversationAction |
| Conversation state | App-owned UUID plus CX state/reporting | Conversation state and Conversation.Event |
| Default calling/dialer app | Current CallKit/default-app guidance | LiveCommunicationKit default calling/dialer APIs |
| Carrier fallback | telephony URL/system route | telephony URL or TelephonyConversationManager |
| Audio activation | CXProviderDelegate/AVAudioSession | ConversationManagerDelegate/AVAudioSession |

Do not mix both frameworks’ system reports for the same call without a deliberate migration architecture. Double-reporting can create duplicate or conflicting system state.

## 14. SwiftUI and scene bridging

SwiftUI owns:

- route selection and recipient review;
- current conversation projection;
- action progress and errors;
- translation controls;
- history browsing;
- accessibility and alternate input;
- optional on-device AI proposal review.

A reference or service object owns:

- ConversationManager;
- ConversationManagerDelegate;
- PushKit registry/delegate;
- app-owned service connection;
- audio graph;
- action deduplication and timeout;
- scene/background handoff.

Use an @MainActor feature model as the UI boundary. Convert manager callbacks into Sendable value events. Use scene phase to update the app-owned projection, but do not end an active conversation merely because a SwiftUI view disappears. The system call UI can outlive the app’s visible screen.

Cold launch, warm launch, terminated PushKit wake-up, system call UI, and app scene restoration must converge on one conversation store keyed by the framework UUID and server call ID. Never create a new conversation when a restore event references an existing one.

## 15. On-device AI boundaries

On-device AI can help with:

- suggesting a contact label from app-owned, user-approved information;
- summarizing a completed transcript after explicit consent;
- suggesting a reply or follow-up task;
- translating or classifying content when the user enables that function;
- resolving a call destination from a user-edited query before review.

It should not:

- initiate a call from an unsolicited model output;
- select a phone number from hidden content without showing it;
- tell the system that a call connected;
- mark history read or delete it without the person’s action;
- use private caller data in a prompt by default;
- record or transcribe without the required user-facing state and policy;
- let a model bypass the action timeout or audio-session boundary.

Represent an AI proposal as:

    source record/transcript revision
      -> bounded local input
      -> model availability and privacy state
      -> proposal
      -> visible recipient/content review
      -> explicit action
      -> fresh authorization and state check
      -> commit

Keep the original handle, transcript revision, model identifier, and review decision as provenance. If the model is unavailable, the manual caller/history/audio experience remains useful.

## 16. Privacy and communication data

LiveCommunicationKit documentation notes that the app provides recipient contact information to the system, which may use it for Journaling Suggestions or other system features. Tell the person what information is shared with the system and keep the recipient representation minimal.

Review:

- recipient handle storage and redaction;
- incoming caller data from PushKit;
- server payload encryption and validation;
- audio/video/transcript retention;
- translation-engine data path;
- history access and deletion;
- notification/service-extension logs;
- default-app handoff;
- health research Speech Metrics opt-out configuration where relevant.

The framework’s system UI may show names, handles, and call history. An app-owned AI screen must not imply that its summary is identical to the system record or that a model has verified the remote participant.

## 17. Native design and Liquid Glass

The system call UI owns the major call surface. The app-owned screen should be a compact companion:

- contact/handle preview before starting;
- clear call/answer/end/mute/translation controls;
- state text such as connecting, joined, paused, or ended;
- audio route and permission explanation;
- system-owned handoff indicator;
- transcript/AI summary only after an explicit review boundary.

Use current SwiftUI controls and small Liquid Glass control groups for app-owned actions. Do not draw a full counterfeit Phone screen or put raw network/call logs behind decorative glass. Use stable controls that remain legible in high contrast, reduced transparency, and Dynamic Type.

Call state must not depend on animation. A connecting pulse can be removed under Reduce Motion without hiding whether the call is joined. Translation status should be text and accessibility state, not a shifting color badge.

## 18. Accessibility

Test with:

- VoiceOver announces call state, remote participant, mute, translation, and end action;
- Dynamic Type preserves recipient, warning, and action labels;
- switch control, keyboard, pointer, and Voice Control invoke call actions;
- reduced motion removes decorative call pulses;
- reduced transparency preserves button and status contrast;
- color is not the sole distinction between connecting, joined, paused, and ended;
- system call UI and app-owned controls do not create duplicate accessible actions;
- error copy explains whether the app or system owns the next step;
- a visual or audible route is not the only way to understand audio activation.

For an AI transcript or translation, label generated/translated text and provide the original when appropriate. Do not let a generated summary replace the accessible call-state source.

## 19. Release proof

The release packet should include:

| Evidence | VoIP | Default calling | Default dialer |
| --- | --- | --- | --- |
| Target and framework | Required | Required | Required |
| Entitlements | VoIP/calling app as applicable | calling-app | dialing-app plus required route |
| Background mode | voip when required | voip | documented app configuration |
| Physical device | Two-device/service call and audio routes | Device default-app selection | EU account/device and carrier state |
| Incoming path | PushKit to system UI to media | Same plus default calling | Cellular/default-app routing |
| Failure path | action timeout, network failure, audio reset | telephony fallback | confirmation/region/cellular failure |
| Translation | source/target/engine/recovery | same | same if supported |
| History | app-owned or documented system projection | documented scope | default-dialer history since selection |
| Distribution | archive/TestFlight | entitlement and metadata | entitlement, region, App Review/program proof |

A simulator can validate reducers and UI states. It cannot prove PushKit delivery timing, carrier routing, default-app selection, microphone route, remote media, or App Store entitlement approval.

## Sources

- [LiveCommunicationKit](https://developer.apple.com/documentation/livecommunicationkit)
- [Initiating VoIP conversations with LiveCommunicationKit](https://developer.apple.com/documentation/livecommunicationkit/initiating-voip-conversations-with-livecommunicationkit)
- [Preparing your app to be the default calling app](https://developer.apple.com/documentation/callkit/preparing-your-app-to-be-the-default-calling-app)
- [Preparing your app to be the default dialer app](https://developer.apple.com/documentation/livecommunicationkit/preparing-your-app-to-be-the-default-dialer-app)
- [LiveCommunicationKit updates](https://developer.apple.com/documentation/updates/livecommunicationkit)
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
- [ConversationHistoryManager.ConversationHistoryDidUpdate](https://developer.apple.com/documentation/livecommunicationkit/conversationhistorymanager/conversationhistorydidupdate)
- [TelephonyConversationManager](https://developer.apple.com/documentation/livecommunicationkit/telephonyconversationmanager)
- [StartCellularConversationAction](https://developer.apple.com/documentation/livecommunicationkit/startcellularconversationaction)
- [CellularService](https://developer.apple.com/documentation/livecommunicationkit/cellularservice)
- [Handle](https://developer.apple.com/documentation/livecommunicationkit/handle)
- [CallKit](https://developer.apple.com/documentation/callkit)
- [CXProvider](https://developer.apple.com/documentation/callkit/cxprovider)
- [CXCallController](https://developer.apple.com/documentation/callkit/cxcallcontroller)
- [CXCallUpdate](https://developer.apple.com/documentation/callkit/cxcallupdate)
- [PushKit](https://developer.apple.com/documentation/pushkit)
- [Supporting PushKit Notifications in Your App](https://developer.apple.com/documentation/pushkit/supporting-pushkit-notifications-in-your-app)
- [Responding to VoIP Notifications from PushKit](https://developer.apple.com/documentation/pushkit/responding-to-voip-notifications-from-pushkit)
- [PKPushType.voIP](https://developer.apple.com/documentation/pushkit/pkpushtype/voip)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Handling audio interruptions](https://developer.apple.com/documentation/avfaudio/handling-audio-interruptions)
- [SwiftUI Observation](https://developer.apple.com/documentation/observation)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Generative AI HIG](https://developer.apple.com/design/human-interface-guidelines/generative-ai)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
