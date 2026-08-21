# Wallet, payment, and identity-adjacent surfaces

Commerce design on Apple platforms has two layers:

1. The app-owned context where a person reviews a product, order, membership, or pass.
2. The system-owned surface where the person authorizes Apple Pay, adds a Wallet pass, or views Wallet information.

The design goal is continuity between those layers without pretending the app owns the system surface. The app should feel native because it uses the right Apple controls, hierarchy, terminology, accessibility behavior, and handoff—not because it redraws Apple Pay or Wallet.

## The surface map

| Surface | Owner | App responsibility | Design mistake to avoid |
| --- | --- | --- | --- |
| Product/cart/order detail | App | Explain what will happen, amount, identity/contact scope, and fallback | Hiding a changing total behind decorative glass |
| Apple Pay button | PassKit/system control | Place it at the decision point and build a correct request | Drawing a fake Apple Pay button or using the mark as a button |
| Apple Pay sheet | System | Supply valid request data and handle authorization/provider states | Treating presentation as capture or fulfillment |
| Add to Wallet button | PassKit/Wallet convention | Offer a signed pass after the relevant event and explain its value | Adding silently or presenting an unsigned mock as real |
| Add Pass UI | System | Respond to added, review, or canceled outcomes | Replacing the system review with an app-owned imitation |
| Wallet pass | Wallet | Design pass metadata and server update behavior | Making a pass a marketing poster with no clear action |
| Receipt/order status | App and optionally Wallet order service | Show placed, processing, fulfilled, failed, and refunded state | Showing “success” before the provider/server knows |
| Identity-adjacent confirmation | App + system auth as applicable | Minimize data, explain purpose, and show source of truth | Inferring identity from payment-card availability |

Apple’s [Apple Pay HIG](https://developer.apple.com/design/human-interface-guidelines/apple-pay) and [Wallet HIG](https://developer.apple.com/design/human-interface-guidelines/wallet) are the visual and interaction authority for these surfaces. Re-check them when the SDK or operating system changes.

## Design the app-owned preflight screen

Before a system surface appears, answer the person’s questions in the app:

- What am I buying, booking, receiving, or adding?
- What is the current total and what can still change?
- What information does the system request?
- What happens if authorization succeeds but fulfillment is pending?
- What can I do if Apple Pay, Wallet, a card, a pass, or the network is unavailable?

Keep the content hierarchy simple:

    title and purpose
        -> primary item or membership
        -> amount/status summary
        -> relevant details or delivery choice
        -> system action
        -> alternate route and help

Use semantic Text, labels, lists, forms, and Button controls so Dynamic Type, VoiceOver, localization, keyboard navigation, and system settings can adapt. A glass card that does not expose its amount, state, or action to accessibility is not native polish.

### Show the right state, not the most optimistic state

Use explicit state copy:

| State | App-owned message | Primary action |
| --- | --- | --- |
| Apple Pay unsupported | “Apple Pay isn’t available on this device.” | Use another supported route |
| Card setup possible | “Set up Apple Pay or choose another payment method.” | System setup/payment action |
| Ready | “Pay with Apple Pay” | System Apple Pay button |
| Sheet presented | “Complete payment in Apple Pay.” | System-owned |
| Authorized, provider pending | “Payment authorized; confirming your order.” | Wait or open order status |
| Provider declined | “Payment wasn’t completed.” | Correct details or retry |
| Fulfillment pending | “Order placed; delivery details will update.” | View order |
| Pass ready | “Add your ticket to Wallet.” | Add to Wallet |
| Pass already present | “This pass is already in Wallet.” | Open/view pass |
| Pass update stale | “Wallet has an older version; refresh when available.” | Refresh or contact support |

Do not collapse these into a generic checkmark animation. A payment authorization, a server capture, a pass add, and an order fulfillment are distinct facts.

## Apple Pay button and mark discipline

Use the documented PassKit control and the current HIG rules:

- Use the system Apple Pay button to initiate payment or the relevant setup flow.
- If Apple Pay credentials are available, make Apple Pay the primary payment option where the HIG requires it.
- Do not use the Apple Pay mark graphic as a tappable button.
- If a custom button begins Apple Pay, do not put the Apple Pay logo or the words Apple Pay inside that custom control; show the accepted-payment mark or text in the appropriate surrounding context.
- Keep the payment action at the point where the person has finished choosing product, quantity, shipping, and other required values.
- Do not hide a temporarily unavailable button as if Apple Pay does not exist; explain the missing prerequisite after the interaction when appropriate.

The exact payment button type and style belong to PassKit. Do not recreate their corner radius, logo, or typography with a custom Liquid Glass control. Use [PKPaymentButton](https://developer.apple.com/documentation/passkit/pkpaymentbutton) or the current SwiftUI/UIKit integration route confirmed in the selected SDK.

## Liquid Glass composition around commerce

Liquid Glass can organize an app-owned checkout without becoming the checkout:

### Use glass for transient controls

Good candidates:

- a compact checkout toolbar;
- an order filter or status control;
- a floating “View order” action after the system sheet returns;
- a segmented choice among app-owned shipping/delivery options;
- a small action cluster around a pass detail screen.

Keep the order total, pass title, event date, barcode label, payment status, and error message on a clear content surface. Glass should support hierarchy and controls, not reduce the legibility of the primary fact.

### Keep system actions visually distinct

The Apple Pay button and Add to Wallet action already have platform identity. Let the surrounding app layout adapt to them:

    content background
        -> app-owned order summary
        -> system-provided payment/add control
        -> app-owned result and next step

Avoid stacking multiple translucent layers behind a system control. Avoid animating the whole checkout when only the order state changed. Use the current SwiftUI glass APIs and transitions for app-owned surfaces, and test reduced transparency, increased contrast, Dynamic Type, and Reduce Motion.

### Preserve source-of-truth contrast

A receipt that says “paid” should be visually different from “authorization pending.” A pass that is “ready to add” should be different from “already in Wallet.” Use semantic color, text, icon plus label, and state-specific accessibility announcements. Never communicate the only distinction through glow, blur, hue, or motion.

See [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass), [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles), and [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals).

## Design Wallet passes as task surfaces

Wallet passes are not miniature app screens. They are focused, glanceable artifacts with a style-specific information architecture. Select the pass style that matches the action:

- boarding pass for travel;
- event ticket for attendance;
- coupon for redemption;
- store card for rewards or membership;
- generic pass for a different claim or access card;
- poster-style variants only when the supported pass and device route justify them.

For every pass, decide:

1. What must be understood at a glance?
2. What must remain available on the back or detail view?
3. What barcode, QR code, NFC, or semantic field is actually used?
4. When and where is the pass relevant?
5. What changes after the pass is issued?
6. What happens when the pass expires, is revoked, or cannot be updated?

Use clear labels, sufficient contrast, localized content, and text fields that remain meaningful when images are unavailable. Do not use a custom image to encode the only copy of a ticket number, venue, date, or redemption instruction.

The [Wallet HIG](https://developer.apple.com/design/human-interface-guidelines/wallet) recommends a clean pass that feels at home in Wallet rather than a literal reproduction of a physical card. The pass should help a person act, not display every field the backend happens to know.

## Order and identity-adjacent design

Payment and Wallet data can feel like identity data because it relates to a person, purchase, account, ticket, or membership. Keep the product claim narrow:

- “Apple Pay is available” is not “this person is verified.”
- “This pass was added to Wallet” is not “this person is the ticket holder.”
- “The provider accepted the token” is not “the order was delivered.”
- “The pass is in the library” is not “the pass is current.”
- “The order service returned a status” is not “the venue or merchant honored the claim.”

When an app needs identity proof, use the dedicated identity or authentication route and document its evidence separately. PassKit should be the commerce/Wallet layer, not an accidental identity shortcut.

## Accessible interaction contract

Test the entire task, including the system handoff:

- VoiceOver can find the amount, status, and system action in order.
- The Apple Pay or Add to Wallet control has an understandable label and purpose.
- A canceled system sheet returns to a stable focus location.
- Provider failure is announced and offers a retry or alternate route.
- Wallet already-present state does not leave a dead button.
- Dynamic Type does not clip amounts, dates, barcode labels, or error text.
- Reduce Motion and Reduce Transparency preserve state and action visibility.
- Large hit regions remain usable without requiring a precise tap.
- Localized currency, dates, names, and pass labels fit the supported scripts.
- Locked or shared surfaces do not expose unnecessary order or identity detail.

Use audits as diagnostics, then complete the task on representative physical devices and system surfaces. Accessibility labels and an audit report are not proof that the payment sheet, Wallet pass, or post-payment flow is understandable.

## AI-assisted commerce design

An on-device model can help with:

- extracting line items from a receipt;
- drafting a concise order summary;
- proposing a pass title or category;
- translating user-entered notes before review;
- finding a likely order from the app’s local records;
- preparing an App Intent parameter for a user-approved action.

The model should not be the visual source of truth for:

- final money amounts;
- taxes, shipping, discounts, or refunds;
- merchant identity or payment capability;
- a pass type identifier or serial number;
- the user’s Wallet contents;
- payment authorization or order fulfillment;
- identity verification.

Use a visible review state:

    extracted/proposed
        -> user edits
        -> deterministic calculation or lookup
        -> system authorization
        -> server/provider confirmation

This pattern keeps the model useful while preserving the legibility and trust expected from a commerce surface.

## Native composition checklist

- [ ] The app-owned screen states the user goal before showing a system action.
- [ ] The system Apple Pay or Wallet control is used for the system-owned action.
- [ ] The total, status, and next step remain readable without glass effects.
- [ ] Authorization, provider processing, fulfillment, pass add, and pass update are separate states.
- [ ] Apple Pay is not used as a route for App Store digital content.
- [ ] Wallet pass content uses the correct pass style and semantic fields.
- [ ] Add, review, cancel, already-present, expired, and unavailable states have copy.
- [ ] AI output is typed, reviewable, and upstream of money/pass/system side effects.
- [ ] Accessibility, localization, reduced effects, and locked/shared privacy states are tested.
- [ ] The evidence packet names the target, SDK, merchant/pass environment, device, and system surface.

## Sources

- [Apple Pay HIG](https://developer.apple.com/design/human-interface-guidelines/apple-pay)
- [Wallet HIG](https://developer.apple.com/design/human-interface-guidelines/wallet)
- [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [PassKit](https://developer.apple.com/documentation/passkit)
- [Setting up Apple Pay](https://developer.apple.com/documentation/PassKit/setting-up-apple-pay)
- [Offering Apple Pay in Your App](https://developer.apple.com/documentation/passkit/offering-apple-pay-in-your-app)
- [PKPaymentButton](https://developer.apple.com/documentation/passkit/pkpaymentbutton)
- [PKPaymentAuthorizationController](https://developer.apple.com/documentation/passkit/pkpaymentauthorizationcontroller)
- [PKPaymentRequest](https://developer.apple.com/documentation/passkit/pkpaymentrequest)
- [PKPaymentOrderDetails](https://developer.apple.com/documentation/passkit/pkpaymentorderdetails)
- [Wallet Passes](https://developer.apple.com/documentation/walletpasses)
- [Pass](https://developer.apple.com/documentation/walletpasses/pass)
- [Creating a generic pass](https://developer.apple.com/documentation/walletpasses/creating-a-generic-pass)
- [Distributing and updating a pass](https://developer.apple.com/documentation/walletpasses/distributing-and-updating-a-pass)
- [Building a Pass](https://developer.apple.com/documentation/walletpasses/building-a-pass)
- [Adding a Web Service to Update Passes](https://developer.apple.com/documentation/WalletPasses/adding-a-web-service-to-update-passes)
- [PKAddPassesViewController](https://developer.apple.com/documentation/passkit/pkaddpassesviewcontroller)
- [PKPassLibrary](https://developer.apple.com/documentation/passkit/pkpasslibrary)
- [StoreKit](https://developer.apple.com/documentation/storekit)
