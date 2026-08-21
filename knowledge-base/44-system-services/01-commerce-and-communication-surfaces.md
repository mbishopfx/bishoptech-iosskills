# Commerce and Communication Surfaces

These routes place an app inside a high-trust system experience: Apple Pay, Wallet, calls, VoIP notifications, Focus-aware communication notifications, or a default calling surface. They combine app code with developer-account setup, signing, server behavior, user permissions, and system-owned UI.

## Proof boundary for high-trust surfaces

Keep local UI state, system authorization, signed artifacts, server processing, and release configuration separate. A StoreKit product row is not a verified entitlement; an Apple Pay token is not provider fulfillment; a Wallet pass is not identity; a Sign in with Apple credential is not business authorization; a device-integrity signal is not absolute security. Record the exact capability/entitlement, account, server, environment, and physical-device evidence for the claim being made.

## Route matrix

| User outcome | First route | Boundary to verify | Proof that matters |
| --- | --- | --- | --- |
| Accept payment for real-world goods or services inside the app | [PassKit](https://developer.apple.com/documentation/passkit) and [Setting up Apple Pay](https://developer.apple.com/documentation/passkit/setting-up-apple-pay) | Merchant identifier, payment-processing certificate, Apple Pay capability, payment provider/server contract, supported networks, account, and regional/device conditions | StoreKit/fixture tests are not Apple Pay proof. Use the documented simulator limits, then a signed physical-device sandbox flow with a supported card and a controlled payment backend. |
| Add or manage tickets, loyalty cards, boarding passes, or other Wallet passes | [PassKit Wallet](https://developer.apple.com/documentation/passkit/wallet) and [Configuring Wallet support](https://developer.apple.com/documentation/xcode/configuring-wallet-support) | Wallet capability, pass type IDs, pass signing/distribution, update channel, user authorization, pass lifecycle, and device-family support | Signed physical-device add/display/update/delete flow; verify stale or revoked passes and real Wallet presentation. |
| Sell digital goods or subscriptions | [StoreKit](https://developer.apple.com/documentation/storekit) | Use In-App Purchase rather than Apple Pay for digital goods; products, transactions, entitlement verification, restore, refunds, sandbox/TestFlight/App Store configuration | StoreKit Testing for deterministic state; signed sandbox/TestFlight and release metadata for the actual commerce boundary. |
| Present a native system call UI for a VoIP service | [CallKit](https://developer.apple.com/documentation/callkit) or [LiveCommunicationKit](https://developer.apple.com/documentation/LiveCommunicationKit) | Provider/backend communication, incoming push route, call actions, audio/session lifecycle, system call state, privacy disclosures, default-calling eligibility, and supported OS | Physical-device incoming/outgoing call flow with PushKit/service configuration, interruptions, lock screen, Focus, audio route, and failure recovery. |
| Receive VoIP pushes and hand them to the system call surface | [PushKit](https://developer.apple.com/documentation/pushkit) plus CallKit/LiveCommunicationKit | Push entitlement, APNs environment, token lifecycle, payload policy, server delivery, timing, duplicate/replay handling, and user privacy | Signed physical device and controlled APNs environment; a local notification or simulator mock does not prove VoIP delivery or system call presentation. |
| Give calls/messages a richer system notification and Focus-aware behavior | [Communication notifications and Focus status](https://developer.apple.com/documentation/UserNotifications/handling-communication-notifications-and-focus-status-updates) | Push, Communication Notifications, Time Sensitive Notifications, SiriKit/intent declarations, notification service extension, Focus authorization, usage description, and content policy | Physical-device notification delivery and Focus-state behavior with the actual extension and signing configuration; test denied authorization and fallback notification content. |
| Set an app as a default calling/dialer surface where supported | [CallKit](https://developer.apple.com/documentation/callkit) or [LiveCommunicationKit](https://developer.apple.com/documentation/LiveCommunicationKit) | Current OS/device support, system settings flow, provider behavior, account/phone identity, regulatory/product requirements, and user choice | System settings selection and real calls on supported hardware; do not infer default-app readiness from an in-app call button. |

## Commerce route shape

1. Classify the thing being sold: digital content/service, real-world good/service, or a Wallet pass.
2. Select StoreKit or PassKit accordingly; do not use Apple Pay as a shortcut around digital-goods rules.
3. Record merchant IDs, pass type IDs, certificates, entitlements, product identifiers, server responsibilities, account requirements, and regional/device constraints.
4. Separate local UI/payment-sheet tests from signed sandbox/TestFlight/production configuration.
5. Make restore, cancel, declined payment, expired entitlement, network failure, and server reconciliation visible states.

## Communication route shape

1. Decide whether the product needs messaging, VoIP, cellular/default-dialer behavior, or only a normal notification.
2. Keep the communication provider/backend separate from the system-owned call or notification UI.
3. Treat contact identity, call metadata, Focus status, and push payloads as privacy-sensitive data with explicit retention and disclosure.
4. Model token rotation, duplicate pushes, delayed delivery, termination, interruption, audio-route changes, and denied authorization.
5. Test the real system surface on a signed physical device before calling the communication feature complete.

## CallKit and PushKit sequence

For a VoIP feature, keep the system-call state and service state separate:

`APNs VoIP push -> PKPushRegistry callback -> validate/reconcile call -> CXProvider report -> system UI -> provider action -> VoIP/audio state -> fulfilled|failed|ended`

PushKit is specialized. For apps linked against the iOS 13 SDK or later, a VoIP push must be handled with CallKit; it is not a generic silent notification or background job. Register the push registry at launch, keep the token/environment current on the server, use short expiration for a call invitation, and report the call quickly. If CallKit disallows the report, do not present a private imitation of the system call screen as a fallback.

CallKit can accept/reject the incoming report based on system state such as blocked handles or Focus. The provider delegate then receives user actions. Fulfill an answer action only when the media/service path is ready; fail or report an end reason when the server cannot connect. Treat duplicate push/call UUIDs as an idempotence problem and reconcile with the server instead of creating a second call.

If the feature only needs a message or status alert, use UserNotifications. If a notification needs bounded decryption/content transformation, use a notification service extension; do not register PushKit to wake the app for unrelated work.

## LiveCommunicationKit boundary

LiveCommunicationKit coordinates VoIP/cellular conversations with the system and can prepare a product for a default calling or dialer role. It does not supply the VoIP backend, identity, audio engine, or entitlement approval. Model `ConversationManager` actions, delegate status, audio-session activation/deactivation, timeouts, and system reset as state transitions.

Default calling/dialer behavior is a separate product/release decision with OS, region, entitlement, user-choice, and testing constraints. Where the documented route allows it, provide a clear system/cellular fallback when a VoIP attempt fails. Do not infer that adding the framework makes the app eligible for a default role or grants access to conversation history.

Contact information passed to LiveCommunicationKit can be surfaced by system suggestions such as Journal, so explain the data use and minimize recipient metadata. Keep raw call payloads, tokens, and server diagnostics out of notifications, shared containers, and logs.

## Communication proof matrix

| Claim | Required evidence |
| --- | --- |
| “A call can arrive” | Signed physical device, PushKit entitlement/environment, fresh token, controlled APNs server, valid CallKit report, and server call state. |
| “The user can answer” | Real lock-screen/system call UI, provider action, audio-session activation, server connection, timeout, and failure/end handling. |
| “The app can be the default caller/dialer” | Current LiveCommunicationKit documentation, exact entitlement/account/region/device configuration, system settings selection, and real calls. |
| “Messages notify reliably” | UserNotifications authorization/settings, server delivery tests, denied/Focus/locked states, and a non-push fallback. |
| “A call is private” | Minimized payload, token/identity handling, notification redaction, logs/retention review, and explicit contact disclosure. |

## Refuse to infer

- A payment sheet means the merchant certificates, backend processing, supported card, and production review path are complete.
- Apple Pay is the right route for digital goods delivered inside an app.
- CallKit or LiveCommunicationKit supplies the app’s VoIP backend or guarantees incoming push delivery.
- A local notification test proves PushKit, Communication Notifications, Focus, or a Notification Service Extension.
- A simulator call or screenshot proves the audio route, lock-screen behavior, default-calling settings, or physical-device privacy behavior.
- System integration is complete before entitlement, signing, account, and release configuration are verified.

## Sources

- [PassKit (Apple Pay and Wallet)](https://developer.apple.com/documentation/passkit)
- [Setting up Apple Pay](https://developer.apple.com/documentation/passkit/setting-up-apple-pay)
- [Offering Apple Pay in your app](https://developer.apple.com/documentation/PassKit/offering-apple-pay-in-your-app)
- [Wallet](https://developer.apple.com/documentation/passkit/wallet)
- [Configuring Wallet support](https://developer.apple.com/documentation/xcode/configuring-wallet-support)
- [StoreKit](https://developer.apple.com/documentation/storekit)
- [CallKit](https://developer.apple.com/documentation/callkit)
- [LiveCommunicationKit](https://developer.apple.com/documentation/LiveCommunicationKit)
- [PushKit](https://developer.apple.com/documentation/pushkit)
- [Handling Communication Notifications and Focus Status Updates](https://developer.apple.com/documentation/UserNotifications/handling-communication-notifications-and-focus-status-updates)
- [Adding capabilities to your app](https://developer.apple.com/documentation/xcode/adding-capabilities-to-your-app)
- [Running your app on simulated or physical devices](https://developer.apple.com/documentation/xcode/running-your-app-on-simulated-or-physical-devices)
