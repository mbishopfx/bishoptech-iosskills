# LiveCommunicationKit native and Liquid Glass design review

Calling is a system-owned experience with an app-owned service behind it. The design should make the ownership visible: the system handles the call surface and interruption rules; the app handles the service, media, account, and recovery. A custom screen can feel native without imitating the Phone app.

This review covers LiveCommunicationKit VoIP conversations, CallKit comparison, default calling/dialer app behavior, PushKit wake-up, history, telephony fallback, and optional audio translation or on-device AI. It does not grant entitlement approval or prove that a provider can connect a real call.

Related pages:

- [LiveCommunicationKit framework review](../42-framework-deep-dives/121-swiftui-live-communication-kit-calling-review.md)
- [LiveCommunicationKit route](../50-capability-recipes/152-swiftui-live-communication-kit-calling-review-route.md)
- [LiveCommunicationKit proof matrix](../60-verification/146-swiftui-live-communication-kit-calling-proof-matrix.md)
- [LiveCommunicationKit code recipes](../70-code-recipes/164-swiftui-live-communication-kit-calling-review-recipes.md)

## 1. Design the handoff, not a fake phone

The app-owned flow should be:

    choose recipient
      -> show handle and call type
      -> explicit call intent
      -> system conversation UI
      -> service connects
      -> system/app state reflects truth
      -> in-call controls and optional translation
      -> end/recovery/history

The system may show a Phone-like interface, route audio, respect Do Not Disturb, and coordinate with other communication apps. Do not cover or recreate that surface with a full-screen replica. Put Liquid Glass around app-owned controls or pre-call context where it improves grouping.

## 2. Pre-call recipient review

Before a call action, show:

- recipient display name if the app has a verified source;
- exact handle type: phone number, email address, or generic account;
- whether the route is VoIP or cellular;
- account/service selection when applicable;
- video/audio choice;
- translation language choices if enabled;
- fallback behavior if VoIP cannot connect;
- a single, explicit Call button.

The Call button must be the user-intent boundary. A PushKit event, a system default-app request, an AI suggestion, or a history row can prepare the screen but should not silently place a call.

For a phone number, visually distinguish:

    VoIP call
    Cellular fallback available

from:

    Cellular call
    System/default dialer will handle this

The person should not have to infer ownership from a tiny icon.

## 3. In-call state hierarchy

Use a small state surface:

| State | Copy | Design behavior |
| --- | --- | --- |
| incoming | Incoming call from … | Let the system surface lead; app context may be minimal |
| connecting | Connecting… | Keep end/cancel available; do not say joined |
| joined | Connected | Show elapsed time and active route |
| paused | Paused | Explain whether audio/video can resume |
| translating | Translation on · language pair | Show engine/fallback status |
| interrupted | Audio interrupted | Explain recovery or route change |
| ending | Ending… | Disable duplicate end actions |
| ended | Call ended | Offer history/recall only after review |
| failed | Couldn’t connect | Show whether retry/fallback is available |

Do not use animation, waveform motion, or color alone to communicate Joined. VoiceOver and Dynamic Type must receive the same state.

## 4. Liquid Glass control grouping

Recommended app-owned groups:

| Group | Contents | Treatment |
| --- | --- | --- |
| Call status | state, elapsed time, route | Small material/card with high-contrast text |
| Primary actions | mute, speaker/route, video, end | One compact control group; standard semantic buttons |
| Translation | language pair, on/off, engine | Separate group so translation is not confused with mute |
| Details | participant, account, fallback, diagnostics | Disclosure or sheet, not always-visible raw data |

Keep the destructive End action visually distinct. Do not use the same prominent glass treatment for End and “Suggest reply.” Do not put raw caller payloads, APNs metadata, or action UUIDs in a glossy status card.

Use current platform controls and materials first. Custom effects should support hierarchy, not create a counterfeit system call interface. Test on light/dark backgrounds, high contrast, reduced transparency, and Dynamic Type.

## 5. Incoming call design

Incoming calls have a hard time boundary. PushKit can wake the app, but the system call interface should appear promptly. The app can enrich the system update with caller information only from a bounded, validated source.

The app-owned post-answer route can show:

- connection state;
- participant identity policy;
- audio route;
- mute and end;
- translation;
- a privacy indicator;
- a service/recovery message.

Never delay the system incoming-call report to run a model, fetch a profile image, or resolve a long contact graph. Enrich later if the system and service allow it.

When the person answers, “Answering…” is honest until the media service is connected. Do not transition to Joined because the user tapped Answer.

## 6. Default calling app

If the app can be selected as the default calling app, the design must explain:

- this app handles VoIP calls;
- cellular calls may fall back to the system;
- a telephone number may require explicit confirmation;
- the app can be changed in system settings;
- a failed VoIP route has a fallback.

The telephony fallback should only occur after the person confirms the proposed number and action. A helper should say “Try cellular call” rather than automatically opening the telephony URL from a passive system event.

If the app receives a system-started calling request, show the proposed handle and give the person a clear accept/continue decision according to the system flow. Do not make a system callback look like a background AI command.

## 7. Default dialer and cellular service

The default dialer experience can contain a custom dial pad or recent-conversation list, but the design must stay within the documented regional and entitlement boundary. Mark the active service when multiple CellularService values exist. If the app is not configured as the default dialer, explain that the system may show a confirmation.

A custom dialer should handle:

- entered number normalization;
- invalid/empty input;
- cellular service selection;
- confirmation state;
- carrier/network failure;
- handoff to the default calling app;
- no-service and region fallback.

Do not show “calling” until TelephonyConversationManager accepts the action and the system route progresses. Acceptance of a start request is not proof that the remote party answered.

## 8. Conversation history design

Recent conversations are a system-derived projection with a documented scope. A history screen should state:

    Recent calls available to this app
    Scope: conversations recorded since this app became the default dialer

Each row should preserve incoming/outgoing/missed/unknown semantics and show whether it can start a new call. Marking a row read is a separate action from placing a call. Deleting an app-owned note should not imply deletion from the system’s conversation history.

Use a stable, privacy-conscious display policy:

- mask phone numbers when the product requires it;
- do not render full handles in screenshots or logs;
- use a contact name only when the source is authorized;
- expose the time and state with accessibility labels;
- revalidate the handle before a follow-up call.

## 9. Translation design

Translation belongs in its own control and status:

    Translation off
    English → Spanish
    Engine: System

When the person mutes their microphone, show “Your voice is muted; translated output may continue according to the call’s translation policy” only if that is true for the actual implementation. Follow the documented distinction between muting app input and deactivating upstream audio.

Translation states:

| State | Copy |
| --- | --- |
| unavailable | Translation unavailable for this call |
| preparing | Preparing translation |
| on | Translation on |
| delayed | Translation delayed; original audio continues |
| failed | Translation stopped; call continues |
| off | Translation off |

Show local and remote languages before enabling. Label a custom engine as custom and preserve an original-audio route. Never imply that translated speech is a verbatim legal or medical record.

## 10. Audio route and interruption

The in-call UI should reflect AVAudioSession state without pretending to own system routing:

- receiver/speaker/Bluetooth route;
- route unavailable;
- interruption;
- media-services reset;
- permission or input failure;
- muted input;
- translation input policy.

Do not use a generic “speaker” icon if the system is routing to Bluetooth. Use an accessible label that names the current route when available. If the app’s audio graph is not ready, show Connecting audio rather than Connected.

Keep route changes non-destructive. A temporary interruption should not delete the conversation draft, history state, or translation preference.

## 11. On-device AI review shell

AI may assist after the call:

    transcript or user note
      -> “Summarize on device”
      -> generated proposal
      -> source/revision disclosure
      -> edit/accept/discard

During a call, keep model interaction subordinate to communication. Do not create a floating AI button that competes with mute/end or captures audio without an obvious state and consent. If a call summary requires recording or transcription, disclose it before the relevant media begins and provide a stop path.

Proposal card:

- title: “Suggested follow-up”;
- source: transcript or user note revision;
- model state: On-device / unavailable / fallback;
- editable output;
- explicit save/share/create-task action.

Never place a model summary next to the system call’s Connected status with identical styling. One is generated interpretation; the other is system/service state.

## 12. Accessibility and alternate input

Call controls are high-frequency and high-consequence:

- End has an unambiguous label and is not color-only;
- Mute announces whether the app input is muted;
- Translation announces language pair and engine;
- route selection announces the selected output;
- VoiceOver order follows state, participant, route, primary controls, secondary controls;
- Dynamic Type keeps recipient and failure copy visible;
- keyboard, switch control, pointer, and Voice Control can invoke controls;
- Reduce Motion removes decorative waveform movement;
- Reduce Transparency keeps controls legible;
- haptics supplement, never replace, connection and end state;
- the system call UI is not duplicated as a second inaccessible action surface.

For an incoming call, the app-owned design should not require sighted interpretation to know whether the call is incoming, connected, muted, or ended.

## 13. Failure and fallback surfaces

| Failure | Design language | Next step |
| --- | --- | --- |
| service unavailable | VoIP service unavailable | Retry or cellular/system fallback |
| action timed out | The call action expired | Start a fresh action |
| invalid handle | Check the recipient | Edit before calling |
| not default app | System will ask for confirmation | Continue or cancel |
| no carrier service | Cellular calling unavailable | Retry later or use VoIP |
| audio activation failed | Call connected, audio unavailable | Retry audio/route or end |
| remote ended | The other participant ended the call | Close or call back |
| PushKit mismatch | Incoming invitation expired | Dismiss safely; do not ring stale call |
| translation failed | Call continues without translation | Retry translation or turn it off |
| model unavailable | On-device summary unavailable | Keep transcript/original note |

Error sheets should say whether the app, system, service, or person has the next action.

## 14. Design review checklist

- Is the route explicitly VoIP, cellular, default calling, or default dialer?
- Is the system call UI left in control of the call surface?
- Is Call distinct from a system callback or AI suggestion?
- Is Answering distinct from Joined?
- Does End remain reliable during connecting/interrupted states?
- Are translation and mute semantics separated?
- Does history state its scope and revalidate handles?
- Is a telephony fallback explicit and user initiated?
- Are default-app regional/entitlement states represented?
- Are raw handles, push payloads, transcripts, and model output protected?
- Does Liquid Glass group functional app controls without imitating Phone?
- Do VoiceOver, Dynamic Type, reduced motion/transparency, and alternate input work?
- Can the app explain and recover from action timeout and audio reset?

## Sources

- [LiveCommunicationKit](https://developer.apple.com/documentation/livecommunicationkit)
- [Initiating VoIP conversations with LiveCommunicationKit](https://developer.apple.com/documentation/livecommunicationkit/initiating-voip-conversations-with-livecommunicationkit)
- [Preparing your app to be the default calling app](https://developer.apple.com/documentation/callkit/preparing-your-app-to-be-the-default-calling-app)
- [Preparing your app to be the default dialer app](https://developer.apple.com/documentation/livecommunicationkit/preparing-your-app-to-be-the-default-dialer-app)
- [ConversationManager](https://developer.apple.com/documentation/livecommunicationkit/conversationmanager)
- [ConversationManagerDelegate](https://developer.apple.com/documentation/livecommunicationkit/conversationmanagerdelegate)
- [Conversation](https://developer.apple.com/documentation/livecommunicationkit/conversation)
- [Conversation.State](https://developer.apple.com/documentation/livecommunicationkit/conversation/state-swift.enum)
- [Conversation.Event](https://developer.apple.com/documentation/livecommunicationkit/conversation/event)
- [ConversationAction](https://developer.apple.com/documentation/livecommunicationkit/conversationaction)
- [SetTranslatingAction](https://developer.apple.com/documentation/livecommunicationkit/settranslatingaction)
- [ConversationHistoryManager](https://developer.apple.com/documentation/livecommunicationkit/conversationhistorymanager)
- [TelephonyConversationManager](https://developer.apple.com/documentation/livecommunicationkit/telephonyconversationmanager)
- [StartCellularConversationAction](https://developer.apple.com/documentation/livecommunicationkit/startcellularconversationaction)
- [CallKit](https://developer.apple.com/documentation/callkit)
- [CXProvider](https://developer.apple.com/documentation/callkit/cxprovider)
- [CXCallUpdate](https://developer.apple.com/documentation/callkit/cxcallupdate)
- [PushKit](https://developer.apple.com/documentation/pushkit)
- [Responding to VoIP Notifications from PushKit](https://developer.apple.com/documentation/pushkit/responding-to-voip-notifications-from-pushkit)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Generative AI HIG](https://developer.apple.com/design/human-interface-guidelines/generative-ai)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
