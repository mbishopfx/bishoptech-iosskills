# SwiftUI StoreKit 2 commerce and entitlement review

This deep dive covers the SwiftUI-specific part of StoreKit 2: native product merchandising, subscription selection, purchase review, entitlement projection, restore and management surfaces, Liquid Glass composition, and a bounded on-device AI explanation layer.

It extends the lower-level [StoreKit 2, native merchandising, and entitlement lifecycle](68-storekit2-product-and-entitlement-lifecycle.md) page. The distinction matters: the lower-level page explains the StoreKit transaction model; this page explains how a SwiftUI screen should expose that model without turning a paywall into a decorative purchase trap.

## The commerce boundary

Use this sequence for a native purchase surface:

~~~text
App Store Connect or StoreKit configuration
  -> Product metadata and availability
  -> SwiftUI StoreKit view or app-owned selection
  -> system purchase confirmation
  -> PurchaseResult and VerificationResult
  -> delivery/idempotency policy
  -> entitlement projection
  -> feature access
~~~

Keep these facts separate:

| Fact | Owner | What the UI may say |
| --- | --- | --- |
| A product is configured | App Store Connect/StoreKit configuration | “This plan is available in this environment.” |
| Product metadata loaded | StoreKit | Localized name, description, price, currency, duration, and offer information. |
| Purchase was requested | User plus StoreKit | “Purchase in progress.” |
| Transaction was verified | StoreKit verification result | “Apple verified this transaction.” |
| Content was delivered | App policy and durable delivery record | “Access is ready.” |
| Entitlement is current | Verified transaction/renewal policy | “You currently have access.” |
| Account is reconciled | Optional server/account authority | “Your account is synchronized.” |

A paywall that only knows that a sheet appeared cannot claim that access was granted. A local Boolean can be a cache for rendering, but it is not the source of truth when refunds, revocations, expiration, upgrades, billing retry, or purchases on another device are possible.

## Choose the SwiftUI surface

Start with Apple’s StoreKit views when their semantics fit:

| Product shape | SwiftUI surface | App-owned responsibility |
| --- | --- | --- |
| One non-consumable or one focused product | ProductView | Explain the feature, show restore/help, and react to entitlement state. |
| A collection of one-time products | StoreView | Organize the catalog and handle missing/unavailable products. |
| Auto-renewable subscriptions in one group | SubscriptionStoreView | Explain value, show current status, and provide management/recovery. |
| Custom comparison or onboarding | Loaded Product values plus app-owned layout | Render StoreKit metadata, call the documented purchase route, and implement every result state. |
| Existing customer account page | Entitlement/status projection plus system management | Show active plan, renewal/billing state, restore, refund, and manage actions. |

ProductView, StoreView, and SubscriptionStoreView can load products by identifier or use products already loaded by the app. StoreKit owns the localized product text and the purchase control behavior for those views. The app owns the surrounding context, navigation, fallback state, feature education, and entitlement projection.

Do not rebuild Apple’s confirmation sheet in SwiftUI. A custom plan screen may be branded; the final confirmation and account authorization remain system-owned trust surfaces.

## Product metadata is storefront state

The Product value returned by StoreKit represents the selected storefront or test configuration. Use it for:

- localized display name and description;
- display price and currency;
- product type;
- subscription period and group relationship;
- introductory, promotional, and win-back offer information;
- product icon or promotional image where configured;
- subscription group display name and level where available.

Never hard-code the price into a purchase button. A hard-coded price can disagree with currency, storefront, tax, an introductory offer, a price change, or App Store Connect metadata. If the app wants to show a benefit label such as “best for frequent use,” keep it separate from the localized commercial facts.

Treat a partial product response as a real state:

~~~text
idle -> loading -> productsReady
                 -> partialCatalog(missingIDs)
                 -> unavailable(error)
                 -> cancelled
~~~

Missing product identifiers are not automatically free products. Preserve the user’s context, explain that the plan is unavailable, and expose retry or a free route.

## StoreKit view loading states

StoreKit’s SwiftUI task modifiers provide a way to project product and entitlement work into a view. Use them when the view is the right lifecycle owner; use an app-level coordinator when purchase updates and entitlements must outlive a paywall.

The UI should distinguish:

| Loading state | Meaning | Action |
| --- | --- | --- |
| Product loading | StoreKit is loading metadata | Show stable placeholder and preserve navigation. |
| Product unavailable | The requested product cannot be used in this environment | Retry, support, or free path. |
| Entitlement loading | Current access is being evaluated | Do not show a misleading locked/unlocked flash. |
| Entitled | A verified transaction policy grants access | Open the feature or show current plan. |
| Not entitled | No current verified access for this product | Show available plan or free feature. |
| Entitlement failed | The state could not be determined | Explain and retry; do not silently downgrade or upgrade. |

Use currentEntitlementTask for a focused product and subscriptionStatusTask for a subscription group when those task modifiers fit the screen. The action closure still needs a policy for loading, failure, unverified, expired, revoked, and active values.

## Purchase result is not entitlement

For an app-owned purchase action, Product.purchase(options:) returns Product.PurchaseResult or throws. The state machine is:

~~~text
ready
  -> purchasing
  -> success(verified)
  -> success(unverified)
  -> pending
  -> userCancelled
  -> failed(error)
~~~

Only a verified transaction enters the normal delivery path. The app must still apply its product policy:

1. validate the product identifier and product type;
2. check verification and any server/account rule;
3. deliver the non-consumable, subscription access, or consumable balance idempotently;
4. update the entitlement projection and user-facing state;
5. finish the transaction after delivery or a durable retryable delivery record.

Do not finish an unverified transaction as if it were delivered. Do not grant access because the confirmation sheet returned without a transaction. Pending means the customer may need an external approval or payment action; the app should keep listening for Transaction.updates.

## Transaction sequences and SwiftUI state

Use separate long-lived and one-shot paths:

| Sequence/action | Use |
| --- | --- |
| Transaction.updates | Long-lived listener for purchases made outside the current call, on another device, offer-code redemptions, and other updates. Start early. |
| Transaction.currentEntitlements | Rebuild current access for non-consumables and current subscription entitlements. |
| Transaction.unfinished | Recover transactions that still need delivery/finish processing. |
| Transaction.all | History and support workflows, not a shortcut for current access. |
| AppStore.sync | User-invoked synchronization when the person asks to restore. Re-read entitlements afterward. |

Route every transaction source through the same verification and delivery actor. A paywall view should not create a second update listener every time it appears. The app-level owner can publish an EntitlementSnapshot to SwiftUI.

~~~text
StoreKit event
  -> StoreCoordinator/actor
  -> verification result
  -> product policy
  -> delivery ledger
  -> EntitlementSnapshot
  -> SwiftUI projection
~~~

The snapshot should contain status, source revision, last evaluation time, and an error/retry state. It should not contain a trusted “premium” bit without the evidence used to derive it.

## Subscription status deserves its own projection

Product.SubscriptionInfo.Status contains a signed transaction and renewal information for a subscription group. Use the renewal state to distinguish:

| Renewal state | Suggested UI treatment |
| --- | --- |
| subscribed | “Active” with current product and next renewal/expiration context. |
| inGracePeriod | “Active while billing is resolved,” with manage action. |
| inBillingRetryPeriod | “Billing needs attention,” with conservative access policy and manage action. |
| expired | “Ended,” with plan review or restore path. |
| revoked | “Access removed,” with support or plan review. |

If Family Sharing or multiple statuses can apply, choose access from the documented highest entitled service level rather than the first array item. Avoid saying “cancelled” when the subscription is still active until its expiration date; describe the actual renewal state and the next user action.

## Restore, manage, refund, and offer destinations

These are system/account routes, not local toggles:

- Restore: an explicit user action that calls AppStore.sync and then recomputes entitlements.
- Manage subscription: manageSubscriptionsSheet or the corresponding StoreKit/App Store route, with target availability checked.
- Refund: the documented refund request sheet for a transaction when the product supports it.
- Offer code: offerCodeRedemption for SwiftUI, with completion routed through verification and entitlement delivery.
- Terms/privacy: configured App Store Connect destinations or app-owned destinations that are truthful and current.

Place these actions where a person can find them without leaving the paywall confused. A current subscriber should see the current plan, renewal/billing state, manage route, and support—not a generic “buy now” screen that hides existing access.

## App account tokens and server authority

An app account token helps associate a StoreKit transaction with an app account. It does not replace:

- App Store transaction verification;
- a signed server-side JWS validation boundary;
- authentication or account linking;
- an entitlement ledger;
- fulfillment or idempotency.

For a private local utility with no account and no cross-device requirement, local verified entitlements may be sufficient. For an account-backed service, send the signed transaction to a server that validates it and reconciles the account. Never place a private signing key in the iOS target.

If a backend is authoritative, expose provisional, verified-local, server-confirmed, stale, and error states rather than hiding the difference. The user should not lose a useful free workflow merely because an optional server is unavailable, unless the product policy genuinely requires server access.

## Liquid Glass boundaries

Liquid Glass should group app-owned commerce context:

~~~text
feature context and benefit explanation
  glass header or hero
  native StoreKit product/subscription surface
  clear price/term/offer facts
  glass utility group: restore, manage, terms, support
  entitlement/pending/error state
~~~

Do not use glass to blur or visually downgrade price, billing term, legal text, or the “not now” path. Avoid a different glass card for every product row; it creates visual noise and can make the purchase action look like an unrelated decorative control.

When applying custom glass around native StoreKit views:

- keep the StoreKit view’s semantic controls intact;
- preserve a strong contrast behind localized price and term text;
- keep backgrounds bounded to functional groups;
- provide opaque/system-material fallback for reduced transparency or unsupported targets;
- avoid animations that imply a purchase completed before verification;
- test large Dynamic Type and long localized currency strings.

## On-device AI explanation boundary

Foundation Models or another on-device model can explain loaded commercial facts, compare plans, answer a question from the current Product values, or draft a short benefit summary. It must not invent or authorize:

- price, currency, renewal cadence, or discount;
- product identifier or offer eligibility;
- current entitlement or refund status;
- successful delivery;
- cancellation or subscription management;
- a purchase or restore side effect.

Use a typed proposal tied to the current catalog revision:

~~~text
user goal and preference
  -> model proposal with candidate product IDs
  -> deterministic lookup against loaded Product values
  -> current entitlement/subscription-status lookup
  -> review showing product, price, term, and offer source
  -> explicit user action
  -> native StoreKit purchase or management surface
~~~

If the model is unavailable, the native catalog remains complete. If the product catalog changes while a proposal is visible, mark it stale and require regeneration or review.

## Privacy, accessibility, and input

Minimize purchase data in logs and analytics. Do not log raw JWS values, account tokens, full transaction payloads, or Apple Account identifiers by default. If a server stores signed transaction data, define encryption, retention, access, deletion, and support policies.

The full purchase journey must work with:

- VoiceOver and semantic labels for product, price, term, selected plan, offer, current access, and result;
- Dynamic Type without clipping or hiding legal text;
- increased contrast, reduced transparency, and reduced motion;
- Voice Control, Switch Control, keyboard, pointer, and touch where supported;
- right-to-left layout and long localized product names/prices;
- focus restoration and a status announcement after the system sheet returns.

Do not communicate “recommended,” “active,” or “pending” only by tint, glow, glass thickness, or animation. The person needs an accessible status and a deterministic next action.

## Performance and lifecycle

Avoid starting product loads, entitlement scans, and transaction listeners repeatedly from cell appearance or every paywall recomposition. Keep long-lived commerce ownership at an app or feature coordinator and bind the view to a snapshot. Cancel view-scoped work when the product ID set changes or the screen leaves the route.

Measure cold launch, paywall appearance, product loading, entitlement refresh, and purchase-result projection. A responsive paywall must not block the main actor on server verification, large transaction history, or model explanation. Use placeholders that preserve layout and keep a free/cancel path interactive.

## Proof boundary

A SwiftUI preview proves rendering of an injected fixture. A local StoreKit configuration proves deterministic state-machine behavior. A sandbox/TestFlight account proves a signed target can interact with Apple’s test environment. A production archive, App Store metadata, server reconciliation, and physical device prove separate gates.

Do not use a local purchase screenshot to claim:

- production price or storefront availability;
- App Store Connect metadata correctness;
- server notification delivery;
- account reconciliation;
- entitlement persistence across real devices;
- accessibility task completion;
- App Review or release readiness.

## Sources

- [StoreKit](https://developer.apple.com/documentation/storekit)
- [StoreKit 2](https://developer.apple.com/storekit/)
- [Choosing a StoreKit API for In-App Purchases](https://developer.apple.com/documentation/storekit/choosing-a-storekit-api-for-in-app-purchases)
- [StoreKit views](https://developer.apple.com/documentation/storekit/storekit-views)
- [Getting started with In-App Purchase using StoreKit views](https://developer.apple.com/documentation/storekit/getting-started-with-in-app-purchases-using-storekit-views?changes=_9)
- [Product](https://developer.apple.com/documentation/storekit/product)
- [ProductView](https://developer.apple.com/documentation/storekit/productview)
- [StoreView](https://developer.apple.com/documentation/storekit/storeview)
- [SubscriptionStoreView](https://developer.apple.com/documentation/storekit/subscriptionstoreview)
- [Product.purchase(options:)](https://developer.apple.com/documentation/storekit/product/purchase%28options%3A%29)
- [Product.PurchaseResult](https://developer.apple.com/documentation/storekit/product/purchaseresult)
- [Product.PurchaseError](https://developer.apple.com/documentation/storekit/product/purchaseerror)
- [Transaction](https://developer.apple.com/documentation/storekit/transaction)
- [Transaction.currentEntitlements](https://developer.apple.com/documentation/storekit/transaction/currententitlements)
- [Transaction.updates](https://developer.apple.com/documentation/storekit/transaction/updates)
- [Transaction.unfinished](https://developer.apple.com/documentation/storekit/transaction/unfinished)
- [Product.SubscriptionInfo](https://developer.apple.com/documentation/storekit/product/subscriptioninfo)
- [Product.SubscriptionInfo.Status](https://developer.apple.com/documentation/storekit/product/subscriptioninfo/status)
- [Product.SubscriptionInfo.RenewalState](https://developer.apple.com/documentation/storekit/product/subscriptioninfo/renewalstate)
- [manageSubscriptionsSheet(isPresented:)](https://developer.apple.com/documentation/swiftui/view/managesubscriptionssheet%28ispresented%3A%29)
- [storeButton(_:for:)](https://developer.apple.com/documentation/swiftui/view/storebutton%28_%3Afor%3A%29?changes=__1)
- [Setting up StoreKit Testing in Xcode](https://developer.apple.com/documentation/xcode/setting-up-storekit-testing-in-xcode)
- [Testing In-App Purchases in Xcode](https://developer.apple.com/documentation/storekit/testing-in-app-purchases-in-xcode)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
