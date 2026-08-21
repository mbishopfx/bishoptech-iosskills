# SwiftUI StoreKit 2 commerce and entitlement-review design

This page defines a native Apple-style commerce surface for SwiftUI. The design goal is confidence: a person should understand the feature, the price, the renewal term, and the next system step before they tap a purchase control, then understand exactly what happened when the system sheet returns.

## Design goal

Use this hierarchy:

~~~text
why this feature matters
  -> what the selected product includes
  -> what it costs and how often it renews
  -> what offers are actually available
  -> purchase/restore/manage action
  -> verified access or honest failure state
~~~

The app can feel premium and distinctive. The commerce facts should still be unmistakable and platform-native.

## Entry patterns

| Entry | First question | Recommended surface |
| --- | --- | --- |
| Feature lock | “What do I get?” | Short benefit explanation followed by ProductView or a focused plan surface. |
| Plan comparison | “Which plan fits me?” | SubscriptionStoreView or app-owned comparison using live Product values. |
| Existing subscriber | “What is my current state?” | Entitlement/status card with manage, restore, and support. |
| Upgrade/downgrade | “What changes if I switch?” | Current plan, target plan, renewal/price facts, then native subscription action. |
| Restore after reinstall | “Can I recover access?” | Explicit restore action and a result state; do not require a new purchase. |
| AI-assisted choice | “Which live option matches my goal?” | Source-linked comparison proposal with deterministic price/term fields and explicit review. |

Do not send every person to the same generic paywall. A first-time buyer and a current subscriber need different information and actions.

## Paywall anatomy

Use a small set of functional groups:

1. Navigation title that names the capability, not a vague “Unlock more.”
2. Benefit summary with concrete behavior and honest scope.
3. Product or subscription group using localized StoreKit metadata.
4. Price, billing term, and introductory/offer context adjacent to selection.
5. Terms, privacy, restore, manage, and support actions.
6. Status region for loading, pending, verified, billing retry, grace, expired, revoked, or failed state.

Keep the primary purchase action near the plan it affects. Avoid making the customer scroll away from the selected product to discover price, billing cadence, or the dismiss path.

## Native StoreKit surface before custom glass

Choose the native primitive first:

| Surface | Visual role |
| --- | --- |
| ProductView | A single product row or focused unlock control. |
| StoreView | A system-managed collection of one-time products. |
| SubscriptionStoreView | A subscription group with Apple-managed product information and purchase controls. |
| SubscriptionStorePicker/SubscriptionStoreButton where available | A more compact or custom subscription control composition. |
| App-owned Product layout | A custom comparison or education surface that still renders live Product values and routes purchase state correctly. |

StoreKit’s views can adapt layout across supported Apple platforms. Let the platform do that work where possible, then adjust the surrounding SwiftUI shell for the available space. A screenshot-driven clone often breaks on iPad, Mac Catalyst, localization, Dynamic Type, or VoiceOver.

## Liquid Glass composition

Liquid Glass belongs to the app-owned context, not to the commercial truth layer:

~~~text
background/feature preview
  glass context header
  legible product/plan group
  glass utility group
  status and support region
~~~

Good candidates for a glass group:

- a benefit header that floats above app content;
- a compact restore/manage/terms toolbar;
- an AI comparison proposal that is clearly labeled as a proposal;
- a post-purchase status card.

Poor candidates:

- glass behind every price and legal sentence;
- transparent product cards over high-contrast imagery;
- animated glass that implies access before verification;
- a custom button that looks like Apple’s system confirmation control;
- separate glass bubbles for every plan that compete with the actual choice.

Test the glass shell over bright and dark backgrounds, larger text, increased contrast, reduced transparency, reduced motion, right-to-left content, and long localized currencies. If the effect becomes illegible, use a system material or opaque fallback while preserving the grouping and action order.

## Plan comparison

The plan model should distinguish commercial facts from app benefits:

| Field | Render from | Visual treatment |
| --- | --- | --- |
| Name | Product display name | Localized and primary. |
| Price | Product displayPrice or StoreKit view | Prominent, never hard-coded. |
| Period | Subscription period | Near price; state renewal cadence. |
| Offer | Product subscription offer/eligibility | Only show when actually available. |
| Benefits | App-owned product policy | Concrete, short, and non-guaranteed. |
| Current access | Verified entitlement/status | Separate badge or status row. |
| Renewal/billing | RenewalInfo/RenewalState | Explain next state and manage action. |

Do not call a plan “best value” solely because it has the largest price. If the app uses a recommendation label, define it from a visible policy and expose the same meaning to assistive technology.

## State language

Commerce state should be calm, specific, and actionable:

| State | Copy direction | Avoid |
| --- | --- | --- |
| Loading | “Loading plans…” | A disabled screen with no explanation. |
| Missing/unavailable | “This plan is not available right now.” | Treating it as free or hiding the failure. |
| Pending | “Purchase approval is still pending.” | “Success” before entitlement. |
| Cancelled | “No purchase was made.” | Blaming the customer. |
| Verified/delivering | “Finishing setup…” | Opening a locked feature prematurely. |
| Active | “You have access.” | A permanent local “purchased” flag without refresh. |
| Grace period | “Access continues while billing is resolved.” | Claiming billing is fully current. |
| Billing retry | “Billing needs attention.” | Promising uninterrupted access without policy. |
| Expired | “This plan ended.” | Calling it cancelled if it simply expired. |
| Revoked | “Access was removed.” | Hiding the reason or offering a duplicate purchase blindly. |
| Unverified/error | “We couldn’t verify this purchase.” | Granting premium access from an unverified result. |

The app’s exact access policy may differ by product, but the words should describe the policy and the user’s next action.

## Offers and renewal

An introductory, promotional, win-back, or offer-code state is a commercial condition. Show the duration, current price, renewal price/term, and eligibility only from live StoreKit data. If the offer is not available, remove the badge rather than keeping a stale marketing claim.

For subscriptions, give the customer a clear line of sight to:

- what starts now;
- what renews and when;
- what price/term follows an introductory period;
- how to manage or cancel;
- what happens during grace, billing retry, expiration, or revocation.

Do not create a fake urgency countdown, hide the non-purchase action, or preselect an upgrade without clearly showing the current plan.

## Existing subscriber layout

An account or settings surface should prioritize the current state:

~~~text
current plan + active/renewal/billing state
next renewal or expiration context
manage subscription
restore purchases
upgrade/downgrade choices if supported
support and terms/privacy
~~~

If manageSubscriptionsSheet is unavailable for the target, show a clear alternate route and say what the person can do. A local toggle cannot cancel an App Store subscription.

## AI explanation design

On-device AI can help a person understand live options, but it does not become a billing authority. Render an AI proposal like this:

~~~text
AI comparison
Based on: selected goal, current Product values, catalog revision
Recommendation: proposal only
Why: short explanation tied to visible facts
Price/term: deterministic StoreKit fields beside the proposal
Actions: choose, compare, dismiss
~~~

The model must not:

- invent prices, discounts, product IDs, or renewal terms;
- claim offer eligibility without StoreKit evidence;
- say access is active before verified entitlement;
- hide restore, manage, terms, privacy, or cancellation;
- initiate purchase, restore, or subscription management as an unreviewed tool.

If the catalog or entitlement changes, mark the proposal stale. A model-unavailable state should fall back to the ordinary plan comparison without degrading core commerce.

## Accessibility and alternate input

Make the whole purchase task possible without visual effects:

- VoiceOver should read plan name, price, term, offer, selection, current state, and action in a meaningful order;
- plan cards need stable labels and values, not only color or size differences;
- Dynamic Type must preserve price and legal text without clipping;
- reduced transparency should keep the same grouping using material or opaque backgrounds;
- reduced motion should not remove the only signal of verification or pending state;
- Voice Control, Switch Control, keyboard, pointer, and touch need discoverable actions;
- right-to-left and long localized strings need dedicated fixtures;
- the result of the system purchase sheet should announce the new status and focus a sensible next action.

Use a textual “Recommended,” “Current plan,” or “Pending” label when those states matter. Keep the primary action available to keyboard and assistive technologies without requiring a glass gesture or a swipe-only route.

## Privacy and trust

Do not display or log more purchase data than necessary. Raw JWS, account tokens, transaction payloads, and Apple Account identifiers need a deliberate retention and access policy. If a server receives JWS data, explain the account relationship in product documentation and protect the transport/storage path.

The paywall should also be honest about optional account requirements. If the app can unlock a local feature without an account, do not force sign-in merely to show a purchase. If the server is required for service delivery, explain that before the purchase confirmation.

## Platform adaptation

Test the same feature on the intended target families:

| Target | Design question |
| --- | --- |
| iPhone | Does the benefit, plan, and action fit without hiding terms or restore? |
| iPad | Does a wider layout avoid stretching a tiny paywall card and support keyboard/pointer? |
| Mac Catalyst | Does the paywall work in a window with menu/keyboard and system purchase presentation? |
| watchOS or other supported target | Is the chosen StoreKit surface available and appropriate, or is a companion handoff needed? |
| Reduced-capability environment | Does the free/local route remain useful when products or AI are unavailable? |

Do not assume a SwiftUI preview on iPhone proves layout, purchase presentation, or StoreKit availability on every target.

## Design review checklist

- [ ] Product name, price, currency, and term are loaded from StoreKit.
- [ ] The feature benefit is clear before the purchase action.
- [ ] The native confirmation sheet is not imitated.
- [ ] Restore and manage actions are visible.
- [ ] Current entitlement is distinct from a recommendation.
- [ ] Pending, cancelled, unverified, billing retry, grace, expired, and revoked states have specific copy.
- [ ] Liquid Glass is bounded to functional context and has a legible fallback.
- [ ] AI proposals cite the live catalog and cannot initiate purchase.
- [ ] VoiceOver, Dynamic Type, contrast, reduced transparency/motion, RTL, keyboard, pointer, and touch are covered.
- [ ] Local StoreKit tests are not described as production billing proof.

## Sources

- [StoreKit views](https://developer.apple.com/documentation/storekit/storekit-views)
- [Getting started with In-App Purchase using StoreKit views](https://developer.apple.com/documentation/storekit/getting-started-with-in-app-purchases-using-storekit-views?changes=_9)
- [ProductView](https://developer.apple.com/documentation/storekit/productview)
- [StoreView](https://developer.apple.com/documentation/storekit/storeview)
- [SubscriptionStoreView](https://developer.apple.com/documentation/storekit/subscriptionstoreview)
- [SubscriptionStoreControlStyle](https://developer.apple.com/documentation/storekit/subscriptionstorecontrolstyle)
- [Product](https://developer.apple.com/documentation/storekit/product)
- [Product.SubscriptionInfo](https://developer.apple.com/documentation/storekit/product/subscriptioninfo)
- [Product.SubscriptionInfo.Status](https://developer.apple.com/documentation/storekit/product/subscriptioninfo/status)
- [Product.SubscriptionInfo.RenewalState](https://developer.apple.com/documentation/storekit/product/subscriptioninfo/renewalstate)
- [Transaction](https://developer.apple.com/documentation/storekit/transaction)
- [Transaction.currentEntitlements](https://developer.apple.com/documentation/storekit/transaction/currententitlements)
- [Transaction.updates](https://developer.apple.com/documentation/storekit/transaction/updates)
- [manageSubscriptionsSheet(isPresented:)](https://developer.apple.com/documentation/swiftui/view/managesubscriptionssheet%28ispresented%3A%29)
- [storeButton(_:for:)](https://developer.apple.com/documentation/swiftui/view/storebutton%28_%3Afor%3A%29?changes=__1)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
