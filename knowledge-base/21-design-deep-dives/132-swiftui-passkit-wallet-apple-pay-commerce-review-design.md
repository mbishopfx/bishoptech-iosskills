# SwiftUI PassKit, Wallet, Apple Pay, and commerce review design

Commerce becomes Apple-native when the app makes the user’s goal, amount, state, and next action clear, then hands authorization to the correct system surface. It does not become Apple-native by drawing a replica of the Apple Pay sheet or the Wallet app.

Read the [commerce review](../42-framework-deep-dives/104-swiftui-passkit-wallet-apple-pay-commerce-review.md), [route](../50-capability-recipes/135-swiftui-passkit-wallet-apple-pay-commerce-review-route.md), [proof matrix](../60-verification/129-swiftui-passkit-wallet-apple-pay-commerce-review-proof-matrix.md), and [recipes](../70-code-recipes/147-swiftui-passkit-wallet-apple-pay-commerce-review-recipes.md) together. The existing [Wallet, payment, and identity surfaces guide](27-wallet-payment-and-identity-surfaces.md) remains useful for baseline principles; this page concentrates on the modern SwiftUI shell around system commerce.

## Start with the authority map

Before choosing a visual treatment, label who owns each visible fact:

| Visible thing | Owner | Design responsibility |
| --- | --- | --- |
| Cart, item, amount, shipping choice | App/domain | Keep revision, math, and edits explicit |
| Apple Pay availability | PassKit/system | Show a narrow availability and alternate route |
| Apple Pay sheet | Apple Pay system | Supply a valid request and respond to delegate updates |
| Payment token | PassKit plus provider/server | Show pending/declined/accepted without exposing token data |
| Fulfillment | Merchant/provider/order service | Render current status and recovery |
| Wallet pass | Wallet/system plus issuer | Offer signed artifact and user-mediated add |
| Wallet order tracking | Wallet Orders service/system | Show current order facts and update state |
| AI proposal | On-device model | Show provenance, uncertainty, editing, and review |

The design must never make an app-owned “paid” or “added” badge look more authoritative than the system or provider fact that supports it.

## The checkout composition

Use a simple vertical hierarchy:

~~~text
purpose and merchant
    -> item/quantity summary
    -> amount and what may still change
    -> delivery/contact choice
    -> system Apple Pay action
    -> alternate route/help
    -> current result and next step
~~~

The Apple Pay button belongs at the final decision point, after the person has selected the product, quantity, required options, and delivery choice. Avoid forcing the person to traverse a separate payment-method screen when Apple Pay is the primary supported route.

The app-owned preflight should answer:

- What am I buying or booking?
- What is the current total?
- Which details will be shown or selected in the system sheet?
- What happens if authorization succeeds but the provider is still processing?
- What happens if Apple Pay or the network is unavailable?
- Where can I see the order after I authorize it?

Use semantic text, labels, lists, forms, and buttons first. A short checkout is more native than a decorative multi-layer glass composition that makes the amount hard to find.

## Design the state machine, not a single success screen

Use state-specific copy and actions:

| State | User-facing explanation | Action |
| --- | --- | --- |
| Unsupported | Apple Pay isn’t available on this device. | Alternate payment/help |
| Setup possible | Apple Pay can be set up or another route can be used. | System setup/alternate |
| Ready | The current cart is ready for review in Apple Pay. | Apple Pay button |
| Presenting | Complete the payment in Apple Pay. | System-owned |
| Canceled | Payment was canceled before authorization. | Review cart/retry |
| Authorized | Payment was authorized; the order is being confirmed. | Wait/view status |
| Provider pending | The provider is still processing the payment. | Refresh/help |
| Declined | The payment wasn’t completed. | Correct/retry/alternate |
| Fulfillment pending | The order was accepted; delivery details will update. | View order |
| Fulfilled | The order is complete. | View receipt/pass/order |
| Pass ready | Your pass is ready to add to Wallet. | Add to Wallet |
| Already present | This pass or order is already in Wallet. | View in Wallet |
| Expired/voided | This pass is no longer valid. | Help/renew/recover |

The distinction between authorized, captured, accepted, fulfilled, added, and current matters more than the animation used to transition between them.

## Liquid Glass around system commerce

Liquid Glass is appropriate for app-owned controls that help a person navigate, filter, review, or continue. It is not an excuse to reproduce system UI:

| Surface | Glass treatment |
| --- | --- |
| Checkout toolbar | Small action group if it preserves title and amount |
| Delivery selector | Standard semantic control inside a restrained group |
| AI review card | Reviewable candidate with clear source and action |
| Pending order banner | Optional material background with high-contrast state text |
| Pass detail actions | Compact app-owned toolbar around the system Wallet action |
| Apple Pay button | Use PassKit’s provided button or current system integration |
| Apple Pay sheet | Never overlay, redraw, or imitate it |
| Add to Wallet | Use the provided Add to Wallet control and style |
| Wallet app/order surface | Treat as system-owned |

Avoid:

- translucent layers over a critical total or error;
- a glass checkmark that appears before provider confirmation;
- custom Apple Pay logo buttons;
- a fake Wallet card that suggests it is already in Wallet;
- a blurred barcode, order ID, or expiry date;
- motion that makes an authorization or fulfillment state ambiguous.

When an app-owned glass action changes state, keep the title, value, and accessibility label stable while the action result updates. Test increased contrast, reduced transparency, and Reduce Motion.

## Apple Pay button discipline

The Apple Pay HIG distinguishes the Apple Pay mark from the payment button. Use the system button to start payment or setup. If a custom app-owned button starts Apple Pay, it must not reproduce the Apple Pay logo or label inside the custom button; communicate accepted payment through the appropriate mark or surrounding text.

Do not:

- use the mark as a tappable button;
- hide an Apple Pay button so the route feels unavailable;
- show Apple Pay as a separate hidden step after another checkout;
- claim a payment method is available from a stale or overly broad check;
- use Apple Pay for in-app digital goods that belong in StoreKit.

The app-owned screen should make the action obvious without competing with the system button.

## Wallet pass design

Wallet passes are focused artifacts, not app screens. Choose the pass style that matches the user task:

- event ticket for attendance;
- boarding pass for travel;
- coupon for redemption;
- store card for rewards or membership;
- generic pass for another access or claim;
- poster-style or semantic variants only when the target SDK and pass type support them.

Use text fields for important information. Do not put the only ticket number, date, venue, expiration, or redemption instruction into a bitmap. Keep labels localized, legible, and meaningful if an image fails to load. Use barcode or semantic fields for machine-readable content rather than embedding a code in artwork.

Design decisions:

1. What does the person need to know at a glance?
2. What action must be possible from the front?
3. What belongs on the back or in detail?
4. When should the pass become relevant?
5. How does the issuer update, expire, or void it?
6. What should the app show when the pass is already in Wallet?

The Wallet HIG recommends a clean pass that feels at home in Wallet rather than a literal reproduction of a physical card. Keep the pass’s content hierarchy stable across localization and device presentation.

## Order tracking design

An order-tracking surface should prioritize the order:

~~~text
order received
    -> payment/processing status
    -> fulfillment status
    -> shipment or pickup details
    -> support/contact
    -> receipt and Wallet action
~~~

Do not show a marketing carousel, AI recommendation, or unrelated upsell above the current order status. If fulfillment details are unavailable, show the information already known and say when to check again.

When the product uses PKPaymentOrderDetails or Wallet Orders, keep these records separate:

- app order ID;
- provider transaction ID;
- Wallet order type/identifier;
- signed package revision;
- user-facing order number;
- current fulfillment revision.

The Wallet button should communicate “track/add this order,” not “payment succeeded.”

## Add to Wallet design

The app can show an Add to Apple Wallet control when a corresponding signed pass or order exists. The control should be:

- placed next to the relevant pass/order information;
- visually distinct from unrelated app actions;
- labeled with the system-provided convention;
- disabled or replaced with “View in Wallet” when already present;
- accompanied by an explicit fallback when the pass cannot be created;
- tested with VoiceOver, Dynamic Type, contrast, and localization.

Do not silently add a user’s pass because a model, server, background task, or checkout animation suggested it. The system and person remain part of the add decision.

## Accessible commerce task

Test the task, not only the controls:

- VoiceOver reaches merchant, item, quantity, amount, shipping, payment, and result in logical order;
- currency and final/pending amounts are announced with their labels;
- state changes are announced without exposing payment data;
- a canceled Apple Pay sheet returns focus to a predictable control;
- an Apple Pay or Wallet system handoff is explained before and after it occurs;
- the Add to Wallet action and already-present state are both reachable;
- errors distinguish declined, unavailable, canceled, pending, server error, expired, and already present;
- Dynamic Type grows line items and errors without clipping;
- localization handles currencies, right-to-left scripts, names, pass fields, and long merchant names;
- reduced transparency and motion preserve meaning;
- keyboard, pointer, Voice Control, and Switch Control do not depend on a precise tap or color;
- lock-screen and shared-device states do not disclose unnecessary order details.

An accessibility audit is a diagnostic. Complete the whole task on the intended physical device and system surfaces.

## Privacy and trust composition

Payment and Wallet surfaces invite strong trust assumptions. Keep them precise:

| Claim | Safe wording |
| --- | --- |
| PassKit can make a payment | “Apple Pay is available for this device and request.” |
| A payment was authorized | “Payment was authorized; order confirmation is pending.” |
| Provider accepted | “The payment provider accepted the payment.” |
| Order fulfilled | “Your order is fulfilled.” |
| A pass is present | “This pass is in Wallet on the available pass library.” |
| A pass is current | “Wallet has the latest pass revision observed by the app.” |

Minimize logs and analytics. Do not record full paymentData, authentication tokens, certificate material, card details, or pass signing keys. Use privacy-preserving identifiers for order support and delete temporary artifacts according to the product’s retention policy.

## On-device AI review design

Use AI for bounded, visible assistance:

- draft a cart explanation from validated line items;
- classify a user-selected receipt;
- propose an order label or pass title;
- find a matching local order;
- explain a current status using source fields;
- translate a user-entered note before the person reviews it.

Keep the proposal visibly separate from the commerce fact:

~~~text
source order revision
    -> local model proposal
    -> source/model revision shown
    -> edit or reject
    -> deterministic calculation and current lookup
    -> system action
~~~

The model must not choose a merchant ID, invent an amount, sign a pass, decrypt a token, add a pass, claim fulfillment, or infer a person’s identity from Apple Pay availability.

## Native commerce review checklist

- [ ] The app-owned screen states what will happen before the system handoff.
- [ ] StoreKit, Apple Pay, Wallet pass, Wallet order, and FinanceKit routes are not conflated.
- [ ] The system Apple Pay and Add to Wallet controls are used for system actions.
- [ ] Amount, state, fulfillment, pass, and order revisions remain legible without glass.
- [ ] Canceled, pending, declined, already-present, expired, and unavailable states have recovery.
- [ ] AI output carries source/model revision and is upstream of side effects.
- [ ] VoiceOver, Dynamic Type, reduced effects, contrast, localization, keyboard, pointer, and Switch Control are tested.
- [ ] Payment data, pass tokens, signing keys, and financial details are not logged.
- [ ] Target capabilities, entitlements, certificates, provider, sandbox, and release packet are named.

## Sources

- [Apple Pay HIG](https://developer.apple.com/design/human-interface-guidelines/apple-pay)
- [Wallet HIG](https://developer.apple.com/design/human-interface-guidelines/wallet)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [PassKit](https://developer.apple.com/documentation/passkit)
- [Setting up Apple Pay](https://developer.apple.com/documentation/PassKit/setting-up-apple-pay)
- [Offering Apple Pay in Your App](https://developer.apple.com/documentation/passkit/offering-apple-pay-in-your-app)
- [PKPaymentRequest](https://developer.apple.com/documentation/passkit/pkpaymentrequest)
- [PKPaymentAuthorizationController](https://developer.apple.com/documentation/passkit/pkpaymentauthorizationcontroller)
- [PKPaymentButton](https://developer.apple.com/documentation/passkit/pkpaymentbutton)
- [PKPaymentOrderDetails](https://developer.apple.com/documentation/passkit/pkpaymentorderdetails)
- [Wallet](https://developer.apple.com/documentation/passkit/wallet)
- [AddPassToWalletButton](https://developer.apple.com/documentation/passkit/addpasstowalletbutton)
- [Wallet Passes](https://developer.apple.com/documentation/walletpasses)
- [Building a Pass](https://developer.apple.com/documentation/walletpasses/building-a-pass)
- [Distributing and updating a pass](https://developer.apple.com/documentation/walletpasses/distributing-and-updating-a-pass)
- [Wallet Orders](https://developer.apple.com/documentation/walletorders)
- [FinanceKitUI](https://developer.apple.com/documentation/FinanceKitUI)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
