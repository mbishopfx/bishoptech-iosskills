# CallKit, LiveCommunicationKit, and VoIP system routes

Communication features become native only when the app respects the system call boundary. CallKit and LiveCommunicationKit do not provide a VoIP backend, an account system, an audio engine, or guaranteed push delivery. They coordinate a real communication service with system-owned call UI, user actions, interruptions, Focus, lock-screen behavior, and other calling apps.

PushKit is a specialized delivery route for VoIP notifications. For apps linked against the iOS 13 SDK or later, Apple requires CallKit when handling VoIP pushes. If a product cannot present or manage calls through the system call route, it should use User Notifications or a notification service extension for its actual need instead.

Keep the architecture explicit:

    provider/server event
        -> PushKit or app-owned outgoing intent
        -> validate account/call identity
        -> CallKit or LiveCommunicationKit system action
        -> user/system decision
        -> provider action callback
        -> media transport and AVAudioSession
        -> call state reconciliation
        -> end/reset/failure

A notification callback is not an incoming call. A reported call is not a connected media session. A fulfilled CallKit action is not proof that the remote participant answered. A default-calling or default-dialer entitlement is not user selection or release approval.

## Capability map

| User outcome | Primary route | System-owned boundary | Separate responsibility |
| --- | --- | --- | --- |
| Receive a VoIP call with native incoming-call UI | PushKit + CallKit | Phone-like incoming call screen | APNs/server invite, account validation, media connection |
| Start an outgoing VoIP call from the app | CallKit CXCallController or LiveCommunicationKit ConversationManager | System call state and call controls | Provider signaling, media, audio |
| Coordinate hold, mute, end, group, DTMF, or translation | CallKit actions or LiveCommunicationKit ConversationAction | System actions and status | Perform/fail action against the real service |
| Prepare as the default calling app | CallKit or LiveCommunicationKit | User-selected default calling setting | VoIP service, cellular fallback, entitlement/configuration |
| Prepare as a default dialer | LiveCommunicationKit + TelephonyConversationManager | Dialer/default-app and cellular conversation route | Default Dialer App entitlement, regional/device testing |
| Receive an ordinary message/status notification | User Notifications | Notification Center/banner/communication notification | Notification permission, content, privacy, action |
| Run call audio | AVFAudio AVAudioSession | Audio route, interruptions, activation | Media engine, route changes, teardown |

The [CallKit framework](https://developer.apple.com/documentation/callkit) and [LiveCommunicationKit framework](https://developer.apple.com/documentation/livecommunicationkit) describe overlapping but distinct routes. Choose one system contract for the feature, then document whether the app owns the VoIP conversation, forwards a cellular conversation, or is preparing for a default calling/dialer role.

## CallKit route

### Configure a provider

Create a CXProviderConfiguration that states what the system call surface supports:

- audio or video;
- phone-number or email handle types;
- call grouping/holding limits;
- ringtone and icon resources;
- whether calls appear in Recents;
- any supported translation capability in the selected SDK.

Create a CXProvider with that configuration and keep it available for the app’s call-related code. Set a CXProviderDelegate on a deliberate queue. The provider delegate is the boundary where system actions become app/service operations.

The delegate must handle lifecycle and action results such as:

- provider reset;
- answer;
- start;
- end;
- hold/unhold;
- mute/unmute;
- group/ungroup;
- DTMF;
- translation where supported;
- audio session activation and deactivation.

Every action must end in fulfill or fail. If the provider action is still running, preserve a bounded pending state and honor the action timeout. Never fulfill because the request was received; fulfill when the underlying communication service has reached the state the action promises.

See [CXProvider](https://developer.apple.com/documentation/callkit/cxprovider), [CXProviderConfiguration](https://developer.apple.com/documentation/callkit/cxproviderconfiguration), [CXProviderDelegate](https://developer.apple.com/documentation/callkit/cxproviderdelegate), and [CXCallAction](https://developer.apple.com/documentation/callkit/cxcallaction).

### Incoming VoIP calls

The incoming route is:

    PKPushRegistry registration
        -> APNs VoIP payload
        -> token/account/call validation
        -> UUID and CXCallUpdate
        -> CXProvider.reportNewIncomingCall
        -> system allows or rejects report
        -> provider answer/end action

The server sends a short-lived call invitation through APNs. The app receives it through the PKPushRegistry delegate, validates the call identity and current account state, creates a stable call UUID, and reports it to the CXProvider. The system can disallow the report, for example when a caller is blocked or system state prevents the call.

Use [reportNewIncomingCall](https://developer.apple.com/documentation/callkit/cxprovider/reportnewincomingcall%28with%3Aupdate%3Acompletion%3A%29) or the current async overload. If reporting fails, reconcile the server invitation and show no fake incoming-call surface. If it succeeds, wait for the provider’s answer/end action before opening media.

Avoid placing private message text, access tokens, or unnecessary personal details in the VoIP payload or the call update. Use the localized caller name and handle fields the system needs, then fetch the minimum additional state required to connect the call.

### Outgoing calls

For an app-owned outgoing call:

1. Create a stable call UUID and a CXHandle.
2. Create a CXStartCallAction.
3. Place it in a CXTransaction.
4. Submit it through CXCallController.
5. Let the provider delegate perform the real signaling.
6. Report connecting and connected times to the provider.
7. End the call through a system action and report the end reason.

The app’s “Call” button starts an intent. It does not directly mutate system call state or claim connection. The provider delegate receives the action and must connect the real VoIP service or fail it.

See [Making and receiving VoIP calls](https://developer.apple.com/documentation/callkit/making-and-receiving-voip-calls), [CXCallController](https://developer.apple.com/documentation/callkit/cxcallcontroller), [CXTransaction](https://developer.apple.com/documentation/callkit/cxtransaction), and [CXStartCallAction](https://developer.apple.com/documentation/callkit/cxstartcallaction).

### Report live state transitions

CallKit has reporting methods for outgoing connection progress, active call updates, and call-ended reasons. Keep a call state ledger:

    draft
        -> requested
        -> reporting
        -> ringing
        -> connecting
        -> connected
        -> held|muted|grouped
        -> ending
        -> ended
        -> reset|failed

The provider state and the VoIP service state can diverge. Reconcile them by call UUID and server call ID. Handle duplicate pushes, process restart, a stale provider action, account logout, network loss, and provider reset.

## PushKit is not a generic background channel

Register PKPushRegistry at launch, assign its delegate before setting desiredPushTypes, and keep the registry alive for the app’s intended runtime. Send the opaque token and APNs environment to the server through a controlled registration path.

Use the VoIP push type only for a real incoming VoIP call. Apple’s [Responding to VoIP Notifications from PushKit](https://developer.apple.com/documentation/pushkit/responding-to-voip-notifications-from-pushkit) states that apps built with the iOS 13 SDK or later must use CallKit when handling VoIP calls. If the product needs only a message, refresh, decryption step, or ordinary status alert, use User Notifications and the appropriate extension/background route.

Server responsibilities include:

- storing the current token and environment;
- expiring call invitations quickly;
- deduplicating call IDs and UUIDs;
- authenticating the account/device relationship;
- sending only the data needed to report the call;
- removing invalid tokens;
- reconciling unanswered, declined, timed-out, and connected calls.

A local notification, simulator callback, or APNs registration token does not prove an incoming call will reach the system UI on a real device.

## LiveCommunicationKit route

LiveCommunicationKit provides a newer conversation-oriented route for VoIP and cellular conversations and helps an app prepare to be a default calling or dialer app. It does not eliminate the need for a real VoIP service, media transport, account identity, or audio lifecycle.

### ConversationManager

ConversationManager owns current Conversation values and pending ConversationAction values. It can:

- perform actions such as StartConversationAction, EndConversationAction, JoinConversationAction, MergeConversationAction, MuteConversationAction, PauseConversationAction, PlayToneAction, SetTranslatingAction, and unmerge actions where supported;
- report a new incoming conversation;
- report conversation events such as started connecting, connected, updated, or ended;
- expose pending actions that need completion;
- invalidate the manager and fail pending actions on reset.

ConversationManagerDelegate receives:

- manager began;
- manager reset;
- conversation changed;
- system audio activated or deactivated;
- a ConversationAction to perform;
- an action timeout.

When a delegate receives an action, perform it against the real VoIP service, then call fulfill or fail. Respect the action’s timeoutDate. If the process cannot finish in time, fail/reconcile rather than leaving the system in a false connected state.

See [ConversationManager](https://developer.apple.com/documentation/livecommunicationkit/conversationmanager), [ConversationManagerDelegate](https://developer.apple.com/documentation/livecommunicationkit/conversationmanagerdelegate), [ConversationAction](https://developer.apple.com/documentation/livecommunicationkit/conversationaction), and [Conversation.Event](https://developer.apple.com/documentation/livecommunicationkit/conversation/event).

### Default calling app

Apple documents a default calling app route in iOS and iPadOS 18.2 and later. A person may select an app other than Phone or FaceTime to handle calls. To prepare for that role, follow the current [Preparing your app to be the default calling app](https://developer.apple.com/documentation/callkit/preparing-your-app-to-be-the-default-calling-app) guide and use the documented entitlement and fallback route.

Eligibility, user selection, device/OS support, review, and real-call behavior remain separate. If the VoIP attempt fails, the app may need to forward the conversation to the system/cellular path using the documented fallback. Do not present a custom “default” label before the person has actually selected the app in Settings.

### Default dialer app

The default dialer route uses LiveCommunicationKit and the Default Dialer App entitlement. Apple’s current guidance requires an Apple Developer account registered in the European Union and a test device located within the EU for testing the default-dialer behavior. It also distinguishes:

- a default calling app that handles incoming/outgoing VoIP and can fall back to cellular;
- a default dialer app that initiates cellular conversations;
- an ordinary app that asks the system/default calling app to place a call.

Use StartCellularConversationAction, TelephonyConversationManager, and ConversationHistoryManager only within the documented entitlement, user-choice, region, and device boundaries. Conversation history access is not a general permission to read a person’s call history. See [Preparing your app to be the default dialer app](https://developer.apple.com/documentation/livecommunicationkit/preparing-your-app-to-be-the-default-dialer-app).

## Audio and media boundary

CallKit and LiveCommunicationKit coordinate the system call state and audio session activation. The app still owns the media engine and must use AVAudioSession appropriately:

    provider/manager didActivate
        -> configure media route
        -> activate/start audio
        -> observe interruptions and route changes
        -> stop media on end or deactivate

The AVAudioSession documentation treats the audio session as the intermediary between app intent and hardware. Configure category/mode/options for the actual call media, activate only when needed, and respond to interruption and route-change notifications. A call state that says connected while the audio route is unavailable is an honest state only if the UI explains the media problem.

Do not mix audio setup into the UI view lifecycle. Keep it in a call coordinator that handles system activation/deactivation, Bluetooth route changes, speaker/receiver state, microphone permission, audio interruptions, process suspension, and teardown.

See [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession), [Handling audio interruptions](https://developer.apple.com/documentation/avfaudio/handling-audio-interruptions), and [Responding to audio route changes](https://developer.apple.com/documentation/avfaudio/responding-to-audio-route-changes).

## Privacy and contact data

When a person starts a communication that uses CallKit or LiveCommunicationKit, the app provides recipient contact information to the system. Apple notes that the system may use this information for Journaling Suggestions or related system suggestions. Make the product’s data-flow review explicit:

- what handle type is sent;
- when the data is sent;
- whether the contact is user-entered, imported, or inferred;
- how the app handles account logout or contact deletion;
- what is placed in notification previews, logs, and shared containers;
- what the user sees on a locked device or another connected Apple device.

Use communication notification conventions for direct messages/calls. Do not put confidential content in a call push or notification body merely because the app can encrypt it later. Protect display names, handles, call links, transcripts, and server diagnostics.

## On-device AI and call surfaces

AI can assist with a draft call target, contact disambiguation, local transcript organization, or a reviewable call-summary proposal when the product has an explicit consent and data-retention policy. It must not:

- invent or silently alter the recipient;
- auto-start a cellular or VoIP call without the required user/system action;
- use caller-name inference as identity proof;
- bypass CallKit/LiveCommunicationKit actions;
- expose private transcript/contact data in a notification;
- claim a call connected because the model predicted success.

Use a typed call proposal:

    user phrase
        -> candidate handle(s)
        -> current account/contact validation
        -> clear recipient and method review
        -> CallKit/LiveCommunicationKit action
        -> provider/media result

For transcript or summary features, keep captured audio, transcript, generated summary, user-edited record, and system call state separate. Record whether the model ran on device, whether the person opted in, and whether the summary is a proposal or an approved record.

## Design and Liquid Glass boundary

The system incoming-call, outgoing-call, lock-screen, and call-control surfaces are not an app-owned Liquid Glass canvas. Use the current system route so the call feels consistent with Phone and respects Focus, interruptions, audio routing, accessibility, and other calls.

The app-owned in-call screen can use native SwiftUI layout and restrained current Liquid Glass treatment for controls such as mute, speaker, keypad, participants, or a reviewable summary:

- keep the participant and call state on a clear content layer;
- group related actions instead of making every button a floating glass pill;
- use semantic controls and labels;
- show connecting, connected, held, muted, media-failed, and ended states in text and accessible values;
- preserve the system’s call-control outcome after the app returns from the system surface;
- provide a reduced-transparency/reduced-motion fallback;
- never imply that a glass animation is a connection or recording proof.

The [Notifications HIG](https://developer.apple.com/design/human-interface-guidelines/notifications) supports distinct communication notifications with contact-oriented presentation, while [Managing Notifications](https://developer.apple.com/design/human-interface-guidelines/managing-notifications) describes permission, Focus, delivery, and urgency boundaries. Follow them instead of treating every call event as a marketing alert.

## Evidence boundary

| Evidence | Supports | Does not support |
| --- | --- | --- |
| Documentation review | API roles, entitlement names, system boundaries, and current regional/device caveats | Target provisioning, APNs delivery, call audio, default-app selection |
| Local state fixture | UI and coordinator transitions | System call screen, PushKit, real VoIP service |
| Simulator | App-owned screens and some CallKit seams | Reliable VoIP push delivery, cellular/default dialer route, hardware audio |
| Signed physical device | CallKit/LCK surface and selected audio route for the device | Universal device/region support, provider quality, APNs reliability |
| Controlled APNs/provider environment | Incoming invitation and server reconciliation for tested account/device | All background timing, app review, or production delivery |
| Default calling/dialer test | Selected OS/device/region/user-choice behavior | Eligibility on every account, region, or future OS |
| Production call | Observed provider/media outcome | Universal uptime, privacy compliance, or future system policy |

## Sources

- [CallKit](https://developer.apple.com/documentation/callkit)
- [Making and receiving VoIP calls](https://developer.apple.com/documentation/callkit/making-and-receiving-voip-calls)
- [CXProvider](https://developer.apple.com/documentation/callkit/cxprovider)
- [CXProviderConfiguration](https://developer.apple.com/documentation/callkit/cxproviderconfiguration)
- [CXProviderDelegate](https://developer.apple.com/documentation/callkit/cxproviderdelegate)
- [CXCallController](https://developer.apple.com/documentation/callkit/cxcallcontroller)
- [CXTransaction](https://developer.apple.com/documentation/callkit/cxtransaction)
- [CXCallAction](https://developer.apple.com/documentation/callkit/cxcallaction)
- [CXCallUpdate](https://developer.apple.com/documentation/callkit/cxcallupdate)
- [CXStartCallAction](https://developer.apple.com/documentation/callkit/cxstartcallaction)
- [reportNewIncomingCall](https://developer.apple.com/documentation/callkit/cxprovider/reportnewincomingcall%28with%3Aupdate%3Acompletion%3A%29)
- [Preparing your app to be the default calling app](https://developer.apple.com/documentation/callkit/preparing-your-app-to-be-the-default-calling-app)
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
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
