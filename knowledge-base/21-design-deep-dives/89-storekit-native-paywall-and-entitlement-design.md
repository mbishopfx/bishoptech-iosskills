# StoreKit native paywalls, subscription states, and Liquid Glass design

## Design goal

A native StoreKit purchase surface should make four things easy to answer:

1. What does the product provide?
2. What will the customer pay, when, and for how long?
3. What does Apple’s system need the customer to confirm?
4. What will the app do after access is verified?

The app can have a distinctive visual identity. The purchase confirmation, localized price, system legal controls, and subscription-management surfaces should remain recognizable as Apple-owned commerce behavior.

Use this sequence:

```text
benefits -> plans -> price/term -> terms/privacy -> purchase -> verified access
                                                       -> pending/retry/manage
```

## Native surface first

Choose the StoreKit surface by the product shape:

| Product situation | Native starting point | App-owned design around it |
| --- | --- | --- |
| One non-consumable unlock | `ProductView` | Benefit explanation, restore, and post-purchase access. |
| Several one-time products | `StoreView` | Grouping, product education, and unavailable-product fallback. |
| Subscription group | `SubscriptionStoreView` | Header, use cases, plan comparison, support, and status context. |
| Highly custom plan comparison | App-owned layout plus loaded `Product` values | Localized price/terms, direct purchase action, verification, restore, and manage route. |
| Existing subscriber | Entitlement/status surface plus `manageSubscriptionsSheet` | Current plan, next renewal, billing state, and support. |

Do not put the entire flow inside a decorative glass card. Let the system purchase component provide the commerce interaction, then use the app’s hierarchy to explain value and state.

## Paywall anatomy

```text
navigation title: what the feature unlocks
short benefit statement: outcome, not hype
feature list: concrete included behavior
plan control: StoreKit subscription controls or product views
localized price and billing term: from Product/StoreKit
introductory or offer explanation: only when actually eligible/configured
terms and privacy: visible system/custom destinations
restore purchases: explicit user action
manage subscription: shown for current subscribers
purchase status: loading, pending, verified, unavailable, or failed
```

Keep the primary action near the plan it affects. If the person has to scroll away from the plan to understand what the button buys, the layout is not doing enough explanatory work.

Do not label a purchase button “Continue” when the side effect is a subscription. Use a localized StoreKit label or a clear app-owned label such as “Start monthly plan” only when the selected API allows that customization and the price/term remain adjacent.

## Plan comparison without dark patterns

Use a stable comparison model:

| Field | Source | Design rule |
| --- | --- | --- |
| Product name | StoreKit `Product` | Render localized storefront text. |
| Price | StoreKit `displayPrice` or native StoreKit view | Never substitute a hard-coded price. |
| Billing period | Subscription metadata | State the renewal cadence plainly. |
| Introductory offer | StoreKit offer/configuration | Show only when the current customer and storefront are eligible. |
| Benefits | App product definition | Say what the feature does; do not imply guaranteed outcomes. |
| Renewal/cancellation | App Store policy/system management | Explain auto-renewal and provide manage/cancel access. |
| Current entitlement | Verified app policy | Show “current plan” separately from “recommended plan.” |

Avoid fake countdowns, disguised dismiss buttons, preselected upgrades that hide the current plan, or a lower-contrast “not now” path. A premium design can still be direct and respectful.

## Liquid Glass composition

Use Liquid Glass for grouping and depth around app-owned content, not for obscuring commerce facts:

```text
background content or illustration
  glass header: benefit and context
  opaque/legible plan region: StoreKit controls and price
  glass utility region: restore, terms, support, manage
```

Keep the product price, billing term, selected option, and purchase state at a readable contrast. If a glass layer overlaps an image, use a material/container treatment that preserves legibility under bright, dark, HDR, and dynamic backgrounds.

Prefer system StoreKit views and semantic controls. When custom styling is appropriate, use `subscriptionStoreControlStyle`, product view styles, standard typography, and platform spacing. A custom glass button that visually imitates the App Store purchase confirmation is not a native replacement for the system sheet.

Test at least these visual states:

- product loading with placeholder content;
- products unavailable or missing from the storefront;
- selected plan with long localized name;
- introductory offer visible and not eligible;
- pending purchase;
- verified access;
- unverified or failed purchase;
- billing retry and grace period;
- expired/revoked access;
- large Dynamic Type over a glass background;
- increased contrast and reduced transparency;
- right-to-left and long localized currency strings.

## Entitlement states are product states

Do not use one green checkmark for every StoreKit result. Use distinct copy and actions:

| State | User-facing explanation | Primary action |
| --- | --- | --- |
| Products loading | “Loading plans…” | Wait/cancel. |
| Products unavailable | “Plans aren’t available right now.” | Retry or use free route. |
| Purchase pending | “Purchase approval is still pending.” | Return to app or learn more. |
| Purchase cancelled | “No purchase was made.” | Continue browsing. |
| Verified and delivering | “Finishing setup…” | Wait; prevent duplicate delivery. |
| Verified and active | “You have access.” | Open the feature/manage. |
| Billing grace period | “Access continues while billing is resolved.” | Manage subscription. |
| Billing retry | “We couldn’t confirm the next payment.” | Manage/update billing; do not overstate access. |
| Expired | “This plan ended.” | Review plans or restore if appropriate. |
| Revoked/refunded | “Access was removed.” | Contact support or choose a plan. |
| Unverified | “We couldn’t verify this purchase.” | Retry/support; do not grant paid access automatically. |

The exact access policy can vary by product and server architecture, but the UI must reflect the policy rather than the most optimistic event.

## Offer and renewal explanation

An introductory offer, promotional offer, win-back offer, or offer code is a commercial condition—not a decorative badge. Show:

- who appears eligible according to the current StoreKit/App Store result;
- the offer duration and price;
- the renewal price/term after the offer;
- how the person manages or cancels the subscription;
- what happens if redemption or eligibility fails.

When StoreKit presents the offer code or purchase sheet, do not duplicate it with competing custom copy that can drift from the current App Store configuration.

## Restore and manage actions

Place restore and manage actions where a person can find them without hunting through a settings maze. Restore is a user-triggered synchronization route; it should re-read verified entitlements afterward. Manage opens an Apple-owned surface where supported and should not pretend that a local toggle cancels an App Store subscription.

For a current subscriber, replace “Buy” emphasis with:

```text
current plan + renewal state
next renewal or expiration information
manage subscription
upgrade/downgrade options where supported
support and restore
```

If the system management sheet is unavailable for the target/platform, show a clear alternate route and retain the same honest status language.

## Accessibility and input

The purchase journey must work with:

- VoiceOver reading product, price, term, offer, and current-plan state in order;
- Voice Control targeting plan selection, purchase, restore, and manage actions;
- Switch Control and keyboard/pointer input where the target supports them;
- Dynamic Type without clipped price or hidden legal text;
- increased contrast and reduced transparency without losing state boundaries;
- reduced motion without relying on a morph or glow to communicate purchase completion;
- right-to-left layout and long localized product names;
- an explicit announcement when the system sheet returns and entitlement changes.

Give each plan one stable semantic identity. Do not communicate “recommended” only through tint, a glass halo, or a larger card. A label such as “Recommended for yearly access” should be available to assistive technology.

## On-device AI and paywall safety

AI can personalize education, not authorization. A model may summarize “monthly versus annual,” answer a question using the loaded product metadata, or draft a plan comparison. It must not:

- fabricate a discount or renewal price;
- claim that a person is eligible for an offer without StoreKit evidence;
- hide the cancel/manage path;
- make a purchase from a generated answer;
- describe an unverified transaction as active access;
- turn a preference into a medical, financial, or guaranteed outcome claim.

Render model-generated copy as a proposal tied to current product IDs and timestamps. The deterministic UI owns price, terms, eligibility, side effects, and entitlement state.

## Design review checklist

- [ ] The user understands the feature before seeing the purchase action.
- [ ] StoreKit-localized product name, price, and term are adjacent to the action.
- [ ] The system purchase confirmation is not imitated or obscured.
- [ ] StoreKit views or direct purchase code have loading/missing/error states.
- [ ] Restore and manage actions are discoverable.
- [ ] Current entitlement is distinct from a recommendation.
- [ ] Pending, billing retry, grace, expired, revoked, and unverified states have distinct copy.
- [ ] Glass effects preserve price, term, and state legibility under accessibility settings.
- [ ] AI does not invent commercial facts or execute a purchase.
- [ ] Screenshots, previews, and local StoreKit tests are not described as App Store or production proof.

## Sources

- [StoreKit views](https://developer.apple.com/documentation/storekit/storekit-views)
- [ProductView](https://developer.apple.com/documentation/storekit/productview)
- [StoreView](https://developer.apple.com/documentation/storekit/storeview)
- [SubscriptionStoreView](https://developer.apple.com/documentation/storekit/subscriptionstoreview)
- [SubscriptionStoreControlStyle](https://developer.apple.com/documentation/storekit/subscriptionstorecontrolstyle)
- [SubscriptionStoreButtonLabel](https://developer.apple.com/documentation/storekit/subscriptionstorebuttonlabel)
- [Product](https://developer.apple.com/documentation/storekit/product)
- [Product.SubscriptionInfo.Status](https://developer.apple.com/documentation/storekit/product/subscriptioninfo/status)
- [Product.SubscriptionInfo.RenewalState](https://developer.apple.com/documentation/storekit/product/subscriptioninfo/renewalstate)
- [Product.SubscriptionInfo.RenewalInfo](https://developer.apple.com/documentation/storekit/product/subscriptioninfo/renewalinfo)
- [Transaction.currentEntitlements](https://developer.apple.com/documentation/storekit/transaction/currententitlements)
- [AppStore](https://developer.apple.com/documentation/storekit/appstore)
- [manageSubscriptionsSheet(isPresented:)](https://developer.apple.com/documentation/SwiftUI/View/manageSubscriptionsSheet%28isPresented%3A%29)
- [Supporting offer codes in your app](https://developer.apple.com/documentation/storekit/supporting-offer-codes-in-your-app)
- [Human Interface Guidelines: In-app purchase](https://developer.apple.com/design/human-interface-guidelines/in-app-purchase)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
