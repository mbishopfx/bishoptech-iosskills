# SwiftUI PassKit, Wallet, Apple Pay, and commerce review route

Use this route when an app idea includes payment for a real-world good or service, a Wallet pass, Apple Pay order tracking, or a FinanceKitUI order handoff. Start with the [commerce review](../42-framework-deep-dives/104-swiftui-passkit-wallet-apple-pay-commerce-review.md), [design guide](../21-design-deep-dives/132-swiftui-passkit-wallet-apple-pay-commerce-review-design.md), [proof matrix](../60-verification/129-swiftui-passkit-wallet-apple-pay-commerce-review-proof-matrix.md), and [recipes](../70-code-recipes/147-swiftui-passkit-wallet-apple-pay-commerce-review-recipes.md).

## Route selector

| User outcome | First route | Add only when needed |
| --- | --- | --- |
| Sell digital content or an in-app subscription | StoreKit 2 | App Intents, server entitlement, widgets |
| Pay for a physical product or service | PassKit Apple Pay | Shipping/coupon updates, provider server, Wallet order |
| Issue an event ticket or membership card | Wallet Passes + PassKit | App Clip, relevance, update web service |
| Show a receipt/tracking order in Wallet | Wallet Orders | Apple Pay order details, FinanceKitUI, background updates |
| Add a signed order through SwiftUI | FinanceKitUI AddOrderToWalletButton | FinanceStore/save-order result, current managed entitlement |
| Inspect a pass the app may access | PKPassLibrary | Pass type entitlement, open-in-Wallet route |
| Classify or explain a user-selected receipt | On-device AI proposal | Source revision, review, deterministic correction |

Do not choose Apple Pay because a visual checkout looks appropriate. Choose it because the product is a supported real-world commerce outcome and the merchant/provider route is configured.

## Contract worksheet

~~~text
User outcome:
Digital or real-world item:
Authoritative order ID:
Cart revision:
Currency/country:
Merchant identifier:
Payment processing certificate/provider:
Supported payment networks:
Shipping/contact/coupon behavior:
Apple Pay availability states:
Provider result states:
Fulfillment source:
Wallet pass type/serial:
Pass signing service:
Wallet order type/identifier:
Order archive/service:
FinanceKit or FinanceKitUI used:
Target/capability/entitlement:
Sandbox/test account:
AI proposal and source revision:
Accessibility/input settings:
Physical-device proof:
Archive/TestFlight/release proof:
~~~

## Target and environment gate

Inspect the named target before implementation:

- import PassKit, SwiftUI, and FinanceKit/FinanceKitUI only when the route needs them;
- confirm deployment target, SDK, platform, and intended device family;
- configure Apple Pay capability and signed Merchant IDs entitlement;
- confirm merchant identifier, payment-processing certificate, provider mode, region, and supported networks;
- configure Wallet capability and Pass Type IDs when the app reads or manages passes;
- confirm pass type identifier, team identifier, certificate, signing service, and pass server;
- confirm FinanceKit managed entitlement and privacy purpose string when the selected route needs it;
- inspect App Group, extension, and background-delivery membership;
- inspect privacy manifest, log redaction, network, and retention policy;
- capture a sandbox/provider/pass-service test environment and a separate release environment;
- archive and inspect the signed entitlements and version/build before physical testing.

Never treat a local development entitlement, placeholder merchant, unsigned pass, or fake provider response as a release-ready contract.

## Route A: Apple Pay checkout

1. Create an authoritative cart and order revision.
2. Calculate line items, tax, discounts, shipping, currency, and total deterministically.
3. Preflight PassKit availability for the device and supported networks.
4. Show the app-owned amount and choices.
5. Present the system Apple Pay button.
6. Build PKPaymentRequest from the same cart revision.
7. Respond to shipping, payment-method, coupon, and merchant-update callbacks exactly once.
8. Present PKPaymentAuthorizationController with a retained delegate coordinator.
9. On authorization, validate contact/shipping details and send the encrypted token to the provider/server.
10. Return the correct authorization result while tracking provider state separately.
11. Reconcile provider transaction, order ID, fulfillment, refund, and retry state.
12. Add PKPaymentOrderDetails only when a real order service identity exists.

Keep the sheet’s amount, the server order amount, and the provider amount tied to a cart revision. If they diverge, fail safely and ask the person to review rather than silently charging a different total.

## Route B: Wallet pass

1. Decide the pass style and the task it supports.
2. Generate pass.json, images, localization, and fields in the trusted issuer pipeline.
3. Assign a stable pass type identifier and serial number.
4. Build the manifest and detached signature using the pass certificate.
5. Validate the signed .pkpass bundle and content type.
6. Deliver it from the app, App Clip, web page, or email.
7. Use AddPassToWalletButton or PKAddPassButton for the corresponding pass.
8. Present system add UI and handle added, review, canceled, already-present, and unsupported states.
9. Let the person open the pass in Wallet when it is already present.
10. Update the pass with a new signed version using the same identity when appropriate.
11. Configure the documented pass update web service and push environment if live updates are required.

Do not place pass signing keys in the app or use an AI-generated pass as a signed artifact.

## Route C: Wallet order tracking

Use this route when an order needs the system Wallet order dashboard, detail, fulfillment, and update model.

1. Create a durable order on the merchant/provider service.
2. Create the order source package with stable order type and identifier.
3. Include merchant, line items, payment, status, timestamps, fulfillment, support, and associated-app data.
4. Build and sign the order archive.
5. Connect the successful Apple Pay authorization with PKPaymentOrderDetails when the app uses that handoff.
6. Use the documented Wallet Orders web service for registration and latest-version retrieval.
7. Use the system-provided order button or FinanceKitUI route when the target supports it.
8. Return current signed order revisions after update notifications.
9. Keep the app’s order projection and Wallet’s order projection reconcilable.

The person should see “order received” even when fulfillment is pending. Do not make Wallet depend on an AI-generated status or a client-only flag.

## Route D: FinanceKitUI order handoff

Use FinanceKitUI only after confirming the selected order route, target, entitlement, and SDK availability:

1. Produce a valid signed order archive from the trusted order pipeline.
2. Present AddOrderToWalletButton with the system style.
3. Handle added, canceled, duplicate/newer-existing, and failure results.
4. Store only the app-owned order ID and signed-archive revision.
5. Reconcile the result with the Wallet order and merchant service.
6. Do not request broad financial-data access for an order route unless the product genuinely needs it.

FinanceKit’s financial-data route has managed entitlement, account-level, purpose-string, authorization, privacy, and background-delivery gates. A SwiftUI button is not proof that those gates are satisfied.

## Route E: PassKit library and open-in-Wallet

Use PKPassLibrary on one deliberate isolation path because the class is not thread-safe. Normalize only the passes the app is entitled to access:

~~~text
PassKit library read
    -> stable pass type/serial projection
    -> current server revision lookup
    -> already-present/update/expired state
    -> open-in-Wallet or support route
~~~

Do not infer the full Wallet contents from the list returned to the app. Do not remove a user-owned pass because an app record is stale.

## Route F: local-AI commerce proposal

1. Select only user-approved order/receipt/pass fields.
2. Record source ID, source revision, model revision, and capture time.
3. Produce a bounded proposal such as a summary, label, category, or candidate order.
4. Display source values beside the proposal.
5. Let the person edit or reject the proposal.
6. Re-read the current order/pass projection.
7. Deterministically validate amount, currency, identity, and authorization.
8. Let the normal PassKit/Wallet/FinanceKitUI route perform the system action.

The model must not generate payment tokens, merchant identifiers, pass signatures, order archives, fulfillment claims, or account identity.

## SwiftUI and Liquid Glass composition

Keep app-owned views semantic:

~~~text
NavigationStack
    -> order/receipt content
    -> current amount and state
    -> system Apple Pay or Add to Wallet control
    -> app-owned result/recovery
~~~

Use native controls and current Liquid Glass APIs for the app-owned shell. The payment sheet and Wallet surfaces remain system-owned. Test the shell with reduced transparency, increased contrast, Dynamic Type, Reduce Motion, VoiceOver, keyboard, pointer, Voice Control, and Switch Control.

## Proof packet

~~~text
Target/deployment/platform:
Signed Apple Pay capability and Merchant IDs:
Merchant/certificate/provider environment:
Supported networks/country/currency:
Cart/order fixture and revision:
Availability and alternate route:
Payment sheet presentation/cancel:
Provider token handoff and server result:
Fulfillment/retry/refund:
Wallet pass source/signature/add:
Pass type/serial/update service:
Wallet order source/archive/service:
FinanceKit/FinanceKitUI entitlement/result:
AI source/model/proposal/revalidation:
Accessibility/input settings:
Privacy/log/retention review:
Physical-device/system run:
Archive/TestFlight/release result:
Known unsupported cases:
~~~

## Completion checklist

- [ ] The product route is StoreKit, Apple Pay, Wallet pass, Wallet order, FinanceKit, or an explicit combination.
- [ ] The app owns a durable order revision separate from PassKit objects.
- [ ] Merchant, certificate, provider, pass signing, and entitlements are configured for the named target.
- [ ] Apple Pay availability and alternate payment states are visible.
- [ ] Authorization, provider result, fulfillment, refund, pass add, and order update are separate.
- [ ] Tokens, signing keys, pass authentication tokens, and financial data are redacted.
- [ ] AI is a typed, reviewable proposal upstream of side effects.
- [ ] The system controls are used for Apple Pay and Wallet actions.
- [ ] Accessibility, localization, reduced effects, keyboard, and pointer routes are tested.
- [ ] Physical-device, system-surface, archive, TestFlight, and release proof are recorded.

## Sources

- [PassKit](https://developer.apple.com/documentation/passkit)
- [Apple Pay](https://developer.apple.com/documentation/passkit/apple-pay)
- [Setting up Apple Pay](https://developer.apple.com/documentation/PassKit/setting-up-apple-pay)
- [Configuring Apple Pay support](https://developer.apple.com/documentation/xcode/configuring-apple-pay-support)
- [Offering Apple Pay in Your App](https://developer.apple.com/documentation/passkit/offering-apple-pay-in-your-app)
- [PKPaymentRequest](https://developer.apple.com/documentation/passkit/pkpaymentrequest)
- [PKPaymentAuthorizationController](https://developer.apple.com/documentation/passkit/pkpaymentauthorizationcontroller)
- [PKPaymentAuthorizationControllerDelegate](https://developer.apple.com/documentation/passkit/pkpaymentauthorizationcontrollerdelegate)
- [PKPaymentOrderDetails](https://developer.apple.com/documentation/passkit/pkpaymentorderdetails)
- [Payment token format reference](https://developer.apple.com/documentation/PassKit/payment-token-format-reference)
- [Wallet](https://developer.apple.com/documentation/passkit/wallet)
- [PKPass](https://developer.apple.com/documentation/passkit/pkpass)
- [PKPassLibrary](https://developer.apple.com/documentation/passkit/pkpasslibrary)
- [PKAddPassesViewController](https://developer.apple.com/documentation/passkit/pkaddpassesviewcontroller)
- [AddPassToWalletButton](https://developer.apple.com/documentation/passkit/addpasstowalletbutton)
- [Wallet Passes](https://developer.apple.com/documentation/walletpasses)
- [Building a Pass](https://developer.apple.com/documentation/walletpasses/building-a-pass)
- [Distributing and updating a pass](https://developer.apple.com/documentation/walletpasses/distributing-and-updating-a-pass)
- [Adding a Web Service to Update Passes](https://developer.apple.com/documentation/WalletPasses/adding-a-web-service-to-update-passes)
- [Wallet Orders](https://developer.apple.com/documentation/walletorders)
- [Order](https://developer.apple.com/documentation/WalletOrders/Order)
- [FinanceKit](https://developer.apple.com/documentation/FinanceKit)
- [FinanceKitUI](https://developer.apple.com/documentation/FinanceKitUI)
- [AddOrderToWalletButtonStyle](https://developer.apple.com/documentation/financekitui/addordertowalletbuttonstyle)
- [Apple Pay HIG](https://developer.apple.com/design/human-interface-guidelines/apple-pay)
- [Wallet HIG](https://developer.apple.com/design/human-interface-guidelines/wallet)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
