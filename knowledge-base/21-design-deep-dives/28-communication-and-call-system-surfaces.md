# Communication and call system surfaces

Calling is a system experience before it is an app screen. The person expects incoming and outgoing calls to respect the same broad behaviors as Phone and FaceTime: clear caller identity, predictable answer/end actions, Focus and interruption behavior, consistent audio routing, locked-device handling, and recovery when the network or service fails.

Use the app-owned interface to explain service identity and current media state. Use CallKit or LiveCommunicationKit to enter the system-owned call experience. Let Liquid Glass support the app’s secondary controls without trying to redraw the system call surface.

## Design the handoff

The communication flow has distinct visual owners:

| Stage | Visual owner | App design responsibility |
| --- | --- | --- |
| Contact or dialer input | App | Show recipient, account, call method, and permission/availability |
| Outgoing intent | App plus system | Make the target and consequence obvious before requesting |
| Incoming call report | System | Supply accurate caller identity and handle data |
| Answer/end/hold/mute | System action | Fulfill or fail against real provider state |
| In-call media | App plus system audio | Show media state and route without duplicating system controls |
| Call ended/reset | App | Reconcile history, retry, support, and privacy |
| AI proposal or summary | App | Show provenance, consent, editable output, and review boundary |

Do not animate a local call card to “connected” before the provider and media path report the corresponding state. Do not treat the appearance of the system incoming-call UI as proof that the remote service is ready.

## Incoming call design

CallKit can show a phone-like system interface for an incoming call when the app reports it through the provider. The app’s input should be limited to the data required for the system route:

- localized caller name;
- remote handle when required;
- whether video is supported;
- call capabilities supported by the service;
- a stable call UUID;
- the current account/service validation result.

The system controls answer, decline, and other call actions. The app should make sure a failed report does not leave an orphaned incoming row or a private imitation of the call UI. If the call is blocked, expired, duplicated, or no longer valid, reconcile the server invitation and present a quiet, understandable app-owned state.

Communication notifications can use contact-oriented presentation distinct from ordinary notifications. Keep notification preview content generic enough to protect the person when the device is locked or visible to others. The system may display contact information in ways that affect the user’s broader communication experience, so document the data flow.

See the [Notifications HIG](https://developer.apple.com/design/human-interface-guidelines/notifications) and [CXCallUpdate](https://developer.apple.com/documentation/callkit/cxcallupdate).

## Outgoing call design

Before a person starts a call, the app should show:

- the recipient and how it was selected;
- the communication account or line;
- VoIP versus cellular/default-dialer route;
- any video or translation behavior;
- the fallback if VoIP cannot connect;
- whether the action will invoke a system confirmation.

Then use the system route:

    review recipient
        -> request CXStartCallAction or StartConversationAction
        -> system accepts/rejects action
        -> provider connects or fails
        -> media activates
        -> in-call controls

Do not hide a system confirmation by presenting an app-owned button that looks like the call already started. If the app is actually the configured default dialer and the documented route changes confirmation behavior, label that as a consequence of the user’s system choice, not as an app-controlled shortcut.

## In-call hierarchy

An in-call screen is a high-attention utility. Keep the hierarchy calm:

1. Connection state and participant identity.
2. Primary media state: connected, connecting, muted, held, no route, or degraded.
3. Essential controls: mute, speaker/audio route, keypad, video, end.
4. Secondary actions: participants, translation, notes, report, or summary.
5. Recovery and support.

Use semantic labels and values for all control states. The text “Muted” should not be communicated only by a changed tint. The difference between “connecting” and “connected” should not depend on a shimmer. The difference between “ended” and “failed” should not depend on a red glass effect.

If the call includes video, keep the video route and audio route state separate. If the call includes translation, keep the system translation action and the actual translation/media state separate.

## Liquid Glass without a fake Phone app

App-owned controls may use current SwiftUI material and Liquid Glass guidance, but treat the call as content first:

- put participant identity, timer, network/media state, and error copy on a stable content layer;
- group related controls in one functional glass container when that improves hierarchy;
- use system semantic controls for mute, speaker, keypad, participant, and end actions;
- keep the end action visually distinct and easy to find;
- place floating controls in safe areas without obscuring the participant or state;
- use current glass transitions for state changes that people can understand;
- preserve a clear fallback for reduced transparency, high contrast, and reduced motion.

Avoid:

- a translucent custom replica of the Phone incoming call screen;
- a fake “system” control row that sends actions without a CallKit/LiveCommunicationKit request;
- a blur layer behind a critical status that makes text unreadable;
- a looping animation that suggests audio is connected;
- a glass pill for every possible action;
- a custom system-looking lock-screen card.

Use [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass), [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles), and [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals) as the design constraints.

## Focus, interruptions, and locked devices

Calling is an interruption-sensitive experience. Test:

- Do Not Disturb and other Focus states;
- an incoming call while media is playing;
- an incoming system call while the app is active;
- lock-screen answer/end behavior;
- a device route change to Bluetooth, wired audio, speaker, or receiver;
- a microphone permission change;
- app suspension and return;
- a provider reset;
- network loss while connecting or connected;
- a call ending while the app is backgrounded.

The app must not imply that a local notification or a background callback can replace the system call surface. Use the system’s call UI for high-attention call actions, and use normal notifications for ordinary communication status.

## Communication notification design

Use communication notification conventions for direct calls and messages:

- concise, descriptive content;
- contact-oriented identity where appropriate;
- generic preview text when full previews are hidden;
- no tokens, transcripts, private message bodies, or full call links in visible push payloads;
- no marketing urgency disguised as a call;
- no repeated notifications for the same invitation;
- nondestructive actions first;
- clear management of notification permission and Focus behavior.

The system determines much of the presentation. An app should not add its icon or app name redundantly where the system already supplies them, and it should not use Time Sensitive or Critical levels just to get attention for a non-urgent communication.

## Default calling and dialer surfaces

Default-app design needs a dedicated setup explanation:

    what role is being offered
        -> what data/system behavior changes
        -> exact system settings action
        -> user-selected or not selected
        -> fallback if the role is not active

Use a plain-language explanation for:

- default calling app: VoIP calls and tel links may route through the app;
- default dialer app: cellular conversation initiation and possibly recent history are affected by the documented entitlement and user choice;
- ordinary app: the app can initiate or forward a call but does not own the default role.

Never display “Default” as an app-owned badge before reading the current system state. Do not claim access to conversation history outside the current documented default-dialer route.

## Accessibility and alternate input

A call control must be usable under the settings that matter most during a call:

- VoiceOver can identify participant, call state, audio route, mute state, and end action.
- The end action is not confused with navigation back.
- The app announces connection and media-route changes without flooding the user.
- Voice Control and Switch Control can activate all essential actions.
- Dynamic Type does not obscure the call state or end action.
- High contrast and reduced transparency preserve the control grouping.
- Reduced motion does not remove connection feedback.
- Hardware keyboard, pointer, and external audio route changes have understandable state.
- Touch targets remain usable when the person is moving or holding the device differently.

After a system call action, restore focus to the relevant app-owned state. Do not place VoiceOver focus on a stale “Call” button after the call has ended.

## AI call assistance

AI can be helpful when it stays reviewable:

- resolve a natural-language contact candidate;
- summarize a call after explicit consent and local retention review;
- extract action items from a user-approved transcript;
- draft a follow-up message without sending it;
- classify the user’s own call notes.

The review shell should show:

    source audio/transcript/notes
        -> model proposal
        -> confidence or ambiguity
        -> editable text
        -> user approval
        -> saved record or drafted follow-up

Keep the call’s actual system state, audio recording consent, transcript, generated summary, and approved record separate. AI should never silently dial a candidate, expose a private caller, claim connection, or send a follow-up without its own user action.

## Design checklist

- [ ] The recipient and call method are visible before the call action.
- [ ] The app uses CallKit or LiveCommunicationKit for the system call route.
- [ ] Incoming, outgoing, connecting, connected, held, muted, media-failed, ended, and reset states are distinct.
- [ ] System actions are fulfilled or failed against the real service.
- [ ] CallKit/LiveCommunicationKit is not replaced with a local notification or imitation.
- [ ] Audio route, interruption, microphone permission, and teardown are visible in the design.
- [ ] Default calling/dialer setup explains user choice and fallback.
- [ ] Communication notifications avoid unnecessary private content.
- [ ] Liquid Glass groups app-owned controls without obscuring state or mimicking Phone.
- [ ] Dynamic Type, VoiceOver, reduced effects, alternate input, and locked-device behavior are tested.
- [ ] AI output is consented, typed, editable, and upstream of call/system side effects.

## Sources

- [CallKit](https://developer.apple.com/documentation/callkit)
- [Making and receiving VoIP calls](https://developer.apple.com/documentation/callkit/making-and-receiving-voip-calls)
- [Preparing your app to be the default calling app](https://developer.apple.com/documentation/callkit/preparing-your-app-to-be-the-default-calling-app)
- [CXProvider](https://developer.apple.com/documentation/callkit/cxprovider)
- [CXProviderConfiguration](https://developer.apple.com/documentation/callkit/cxproviderconfiguration)
- [CXProviderDelegate](https://developer.apple.com/documentation/callkit/cxproviderdelegate)
- [CXCallAction](https://developer.apple.com/documentation/callkit/cxcallaction)
- [CXCallUpdate](https://developer.apple.com/documentation/callkit/cxcallupdate)
- [LiveCommunicationKit](https://developer.apple.com/documentation/livecommunicationkit)
- [Initiating VoIP conversations with LiveCommunicationKit](https://developer.apple.com/documentation/livecommunicationkit/initiating-voip-conversations-with-livecommunicationkit)
- [Preparing your app to be the default dialer app](https://developer.apple.com/documentation/livecommunicationkit/preparing-your-app-to-be-the-default-dialer-app)
- [ConversationManager](https://developer.apple.com/documentation/livecommunicationkit/conversationmanager)
- [ConversationManagerDelegate](https://developer.apple.com/documentation/livecommunicationkit/conversationmanagerdelegate)
- [ConversationAction](https://developer.apple.com/documentation/livecommunicationkit/conversationaction)
- [StartConversationAction](https://developer.apple.com/documentation/livecommunicationkit/startconversationaction)
- [PushKit](https://developer.apple.com/documentation/pushkit)
- [Responding to VoIP Notifications from PushKit](https://developer.apple.com/documentation/pushkit/responding-to-voip-notifications-from-pushkit)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Handling audio interruptions](https://developer.apple.com/documentation/avfaudio/handling-audio-interruptions)
- [Notifications HIG](https://developer.apple.com/design/human-interface-guidelines/notifications)
- [Managing Notifications HIG](https://developer.apple.com/design/human-interface-guidelines/managing-notifications)
- [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
