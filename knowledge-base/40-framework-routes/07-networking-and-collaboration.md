# Networking, Companion Devices, and Communication Surfaces

## Route selection

| Need | First route | Core boundary |
| --- | --- | --- |
| HTTP API or file transfer | URLSession | Cancellation, retry, authentication, decoding, offline state, and server truth. |
| Reachability/path/interface changes | Network | A path is not proof that a request, peer, or server will respond. |
| Peer-to-peer discovery/session | MultipeerConnectivity or Nearby Interaction | Nearby permission, radio/session lifecycle, peer identity, protocol, and user intent. |
| iCloud data sync/sharing | CloudKit | Account, schema, conflict, change token, offline cache, and deletion. |
| Live SharePlay collaboration | GroupActivities/SharePlay | Group session membership, activity lifecycle, transport, and content synchronization. |
| Pair an Apple Watch companion | WatchConnectivity | Activation/pairing state, immediate reachability versus queued transfers, ordering, and two-device proof. |
| Vehicle-screen route | CarPlay | Category entitlement/approval, system templates, scene lifecycle, driver distraction, and vehicle proof. |
| One focused instant workflow before full install | App Clips | Invocation URL/experience/App Store configuration, size/startup, limited state, and full-app handoff. |
| Incoming VoIP call | PushKit plus CallKit or LiveCommunicationKit | Specialized push purpose, APNs/token/server state, system call UI, call action lifecycle, and audio. |
| Ordinary message/status notification | UserNotifications/APNs | User authorization, notification content, server delivery, and no background-call semantics. |
| Default calling/dialer integration | LiveCommunicationKit | OS/device/region entitlement, user choice, VoIP/cellular fallback, and system call state. |

## Cross-device proof vocabulary

Do not collapse these states into one `connected` Boolean:

| State | What it means | What it does not prove |
| --- | --- | --- |
| Paired/installed | A companion relationship exists | The other process is running, current, reachable, or authenticated to the same account. |
| Activated | The framework session completed its activation path | A message will be delivered immediately or a prior device remains active. |
| Reachable | The counterpart is available for an immediate message route | Background delivery, future reachability, or server connectivity. |
| Queued transfer | The system accepted a transfer for opportunistic delivery | Exact timing, network success, available storage, or final application of the payload. |
| CarPlay connected | The system created a CarPlay scene/interface controller | Category approval, safe content, driver attention, or a particular vehicle’s behavior. |
| App Clip invoked | The system matched an experience/invocation | The URL is trusted business input, the URL is present on every launch, or the full app has the same state. |
| Push token registered | APNs has a token for a push type/environment | Delivery, freshness after reinstall, call identity, or permission to show unrelated content. |
| CallKit reported | The system accepted/rejected a call report | VoIP server connection, audio readiness, answer completion, or the user’s consent to future calls. |

## Watch route

Use `WCSession` on both targets, configure delegates before activation, and wait for the documented activation callback. Select the transport by product semantics:

- `updateApplicationContext` represents the latest state and replaces the pending context;
- `transferUserInfo` queues background dictionary updates for eventual delivery;
- `transferFile` queues larger file-backed content;
- `sendMessage`/`sendMessageData` are for immediate communication while the counterpart is reachable;
- complication-specific transfers have their own budget and are not a generic background pipe.

Persist an event ID/version on the sender and receiver. Apply transfers idempotently, handle inactive/deactivated sessions when the active watch changes, and keep UI mutations on the main actor because delegate callbacks are delivered serially on a background thread. Share a protocol and projection, not a shared in-memory model.

## CarPlay route

CarPlay creates a `CPTemplateApplicationScene` and supplies a `CPInterfaceController` to the scene delegate. The app pushes supported system templates; it does not draw an arbitrary iPhone UI for most categories. The category, entitlement, scene manifest, template choices, content freshness, and driver-attention model are part of the route.

Navigation apps have a distinct window/content route; other supported categories use the interface controller. Retain the controller for the session, rebuild or validate state after disconnect/reconnect, and never treat the CarPlay screen as a second unrestricted app process. Test the CarPlay Simulator for template/lifecycle work, then verify a real vehicle or aftermarket system for audio, safe interaction timing, connection loss, and vehicle-specific behavior.

## App Clip route

An App Clip invocation is a context signal that selects a focused workflow. Parse only expected URL paths/parameters, validate server/business state, and handle the case where no invocation URL exists. When the full app replaces the App Clip, the full app must handle the same invocations and recover any intentionally shared state.

Keep the App Clip’s data footprint and startup path narrow. App Clip experiences and associated domains/App Store Connect metadata are part of the implementation; an Xcode launch with `_XCAppClipURL` is only a development fixture. Test default/demo/advanced experiences, website/AASA association, QR/NFC/App Clip Code, Maps/Safari/Messages where supported, offline/slow network, repeated launch, notification return without URL, and install transition.

## CallKit, LiveCommunicationKit, and PushKit

Use PushKit only for documented specialized pushes. For VoIP, the app must report the call quickly to CallKit; if it cannot support CallKit, UserNotifications is the alternative—not PushKit as a general wake-up channel. Treat the push as an invitation to reconcile with the server, not as proof that a call is still active.

CallKit owns the system call UI and sends actions such as answer/end/hold through the provider delegate. The app’s VoIP service must fulfill or fail those actions after the underlying network/audio state is ready. `CXProvider` reporting and the server’s call connection are separate states.

LiveCommunicationKit adds a newer conversation manager/default-calling or default-dialer route. Verify the OS/device/region/entitlement rules, user-selected default role, contact disclosure, audio session activation/deactivation, system fallback, and conversation action timeout. Do not imply that default-dialer APIs are broadly available across regions or devices.

For notification-only communication, use UserNotifications with the right authorization and privacy policy. Use a notification service/content extension for bounded content transformation, not arbitrary background application work.

## Offline-first transport layer

1. Domain code asks an async service for a typed operation.
2. Local state returns cached/queued status immediately where possible.
3. The transport adds a request ID, account/session context, and bounded retry.
4. The result becomes `success`, `stale`, `offline`, `authNeeded`, `conflict`, `duplicate`, or `failed`.
5. Companion/system adapters publish only the safe projection for their surface.
6. Reconnect/retry replays idempotent operations under the same domain policy.

Do not use reachability, a push callback, a Watch message, or a CarPlay connection as server authorization. Keep tokens in Keychain, define account switching/deletion, and redact contact/call/vehicle/location data in logs and shared projections.

## Physical/two-device verification

- Watch: paired iPhone plus physical Apple Watch, active/inactive counterpart, multiple-watch switch, reachability off, delayed queue, file transfer, storage error, app termination, and account switch.
- CarPlay: simulator scene/template tests plus real vehicle/aftermarket connection, disconnect/reconnect, locked phone, audio route, navigation/category policy, and driver-attention review.
- App Clip: physical QR/NFC/App Clip Code or local experience, slow/offline network, no URL return, notification resume, full-app replacement, associated domain/AASA, and App Store/TestFlight configuration.
- Calling: signed device, APNs development/production environment, token rotation, incoming/outgoing/answer/end/failure, lock screen/Focus, audio session/interruption, server timeout, duplicate push, and CallKit/LiveCommunicationKit system UI.
- Networking: TLS/auth failure, replay/duplicate event, cancellation, airplane mode, account deletion, and no shared secret in the binary or logs.

## Sources

- [URL Loading System](https://developer.apple.com/documentation/foundation/url_loading_system)
- [URLSession](https://developer.apple.com/documentation/foundation/urlsession)
- [Network](https://developer.apple.com/documentation/network)
- [MultipeerConnectivity](https://developer.apple.com/documentation/multipeerconnectivity)
- [CloudKit](https://developer.apple.com/documentation/cloudkit)
- [GroupActivities](https://developer.apple.com/documentation/groupactivities)
- [Watch Connectivity](https://developer.apple.com/documentation/watchconnectivity)
- [WCSession](https://developer.apple.com/documentation/watchconnectivity/wcsession)
- [WCSessionDelegate](https://developer.apple.com/documentation/watchconnectivity/wcsessiondelegate)
- [Transferring data with Watch Connectivity](https://developer.apple.com/documentation/watchconnectivity/transferring-data-with-watch-connectivity)
- [CarPlay](https://developer.apple.com/documentation/carplay)
- [CPTemplateApplicationScene](https://developer.apple.com/documentation/carplay/cptemplateapplicationscene)
- [CPInterfaceController](https://developer.apple.com/documentation/carplay/cpinterfacecontroller)
- [Displaying content in CarPlay](https://developer.apple.com/documentation/carplay/displaying-content-in-carplay)
- [Using the CarPlay Simulator](https://developer.apple.com/documentation/carplay/using-the-carplay-simulator)
- [CarPlay Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/carplay/)
- [App Clips](https://developer.apple.com/documentation/appclip)
- [Configuring App Clip experiences](https://developer.apple.com/documentation/appclip/configuring-the-launch-experience-of-your-app-clip)
- [Responding to invocations](https://developer.apple.com/documentation/appclip/responding-to-invocations)
- [Testing the launch experience of your App Clip](https://developer.apple.com/documentation/appclip/testing-the-launch-experience-of-your-app-clip)
- [Associating your App Clip with your website](https://developer.apple.com/documentation/appclip/associating-your-app-clip-with-your-website)
- [CallKit](https://developer.apple.com/documentation/callkit)
- [CXProvider](https://developer.apple.com/documentation/callkit/cxprovider)
- [CXCallController](https://developer.apple.com/documentation/callkit/cxcallcontroller)
- [Making and receiving VoIP calls](https://developer.apple.com/documentation/callkit/making-and-receiving-voip-calls)
- [LiveCommunicationKit](https://developer.apple.com/documentation/livecommunicationkit)
- [Initiating VoIP conversations with LiveCommunicationKit](https://developer.apple.com/documentation/livecommunicationkit/initiating-voip-conversations-with-livecommunicationkit)
- [Preparing your app to be the default dialer app](https://developer.apple.com/documentation/livecommunicationkit/preparing-your-app-to-be-the-default-dialer-app)
- [ConversationManagerDelegate](https://developer.apple.com/documentation/livecommunicationkit/conversationmanagerdelegate)
- [PushKit](https://developer.apple.com/documentation/pushkit)
- [PKPushRegistry](https://developer.apple.com/documentation/pushkit/pkpushregistry)
- [Supporting PushKit Notifications](https://developer.apple.com/documentation/pushkit/supporting-pushkit-notifications-in-your-app)
- [Responding to VoIP Notifications from PushKit](https://developer.apple.com/documentation/pushkit/responding-to-voip-notifications-from-pushkit)
- [PKPushTypeVoIP](https://developer.apple.com/documentation/pushkit/pkpushtype/voip)
- [UserNotifications](https://developer.apple.com/documentation/usernotifications)
