# StoreKit 2, native merchandising, and entitlement lifecycle

## Capability boundary

StoreKit 2 is the App Store route for digital goods, subscriptions, and other in-app purchases. It is not a generic payment API and it is not an entitlement database that the UI can query once and forget.

Keep the boundary visible:

```text
App Store Connect product configuration
  -> StoreKit product metadata
  -> native StoreKit merchandising or app-owned purchase action
  -> purchase result and cryptographic verification
  -> delivery/idempotency policy
  -> entitlement projection
  -> user-facing feature access
```

A product is not a transaction. A transaction is not automatically a granted feature. A verified transaction is evidence from StoreKit, not proof that a server-side account has been reconciled or that a consumable was delivered exactly once.

## API object graph

| Concern | Primary API | Boundary to preserve |
| --- | --- | --- |
| Product metadata | `Product`, `Product.products(for:)` | App Store storefront values for name, description, price, type, subscription relationship, and offers. |
| Native merchandising | `ProductView`, `StoreView`, `SubscriptionStoreView` | System-managed product presentation and purchase initiation; app-owned context surrounds it. |
| Purchase | `Product.purchase(options:)`, `Product.PurchaseResult` | User authorization, pending/cancelled/success outcomes, and optional purchase options. |
| Verification | `VerificationResult<Transaction>` | Verified versus unverified signed transaction data. |
| Current access | `Transaction.currentEntitlements` | Latest entitling transactions for non-consumables and active subscription types; not a consumable balance. |
| Background purchase events | `Transaction.updates` | Purchases and changes made outside the current purchase call or on another device. |
| Recovery | `Transaction.unfinished`, `Transaction.all`, `AppStore.sync()` | Idempotent recovery/history and an explicit user-triggered synchronization route. |
| Subscription status | `Product.SubscriptionInfo.Status` | Signed renewal state, latest transaction, and renewal information for a subscription group. |
| Subscription management | `AppStore.showManageSubscriptions(in:)`, `manageSubscriptionsSheet` | System-owned upgrade, downgrade, cancellation, and subscription settings. |
| Offer redemption | `offerCodeRedemption`, `AppStore.presentOfferCodeRedeemSheet` | System-owned offer-code entry and resulting transaction. |
| Automated testing | StoreKit configuration, `StoreKitTest`, `SKTestSession` | Local deterministic transaction environment, distinct from App Store production. |

## Product metadata is storefront state

Load products using stable product identifiers, then render the returned `Product` values. Product names, descriptions, prices, currency, subscription period, introductory offers, and localized text belong to the App Store storefront or active StoreKit test configuration.

Do not hard-code a price into a purchase button. A hard-coded “$4.99” can disagree with the customer’s storefront, tax treatment, introductory offer, currency, or App Store configuration. If the app adds a benefit explanation, keep that copy separate from the product’s localized legal/price metadata.

Model the loading boundary explicitly:

```text
idle
  -> loading
  -> productsReady
  -> emptyOrMissingProducts
  -> unavailable(error)
```

`Product.products(for:)` can return fewer products than requested. Treat missing identifiers as a configuration problem with a visible fallback, not as a reason to invent a local product.

## StoreKit views are native merchandising surfaces

StoreKit views provide localized product information and a purchase button. `ProductView` merchandises one product, `StoreView` merchandises a collection of in-app purchases, and `SubscriptionStoreView` merchandises auto-renewable subscriptions in a subscription group.

The views can load products by identifier or receive products the app already loaded. The app can provide marketing content, icons, backgrounds, styles, and surrounding context. The system owns the purchase confirmation experience.

`SubscriptionStoreView` can show products from a group or a selected collection. It automatically displays terms-of-service and privacy-policy buttons that are configured in App Store Connect unless the app supplies a documented custom destination. Built-in subscription control styles include automatic, buttons, picker, prominent picker, paged picker, paged prominent picker, and compact picker. Choose a style by task and available space, not by copying a screenshot.

For a fully custom paywall, compose the app-owned plan explanation and use `ProductView` or a direct `Product.purchase(options:)` action where the product behavior is clearer. Custom UI still needs the same localized price, purchase result, entitlement, legal, accessibility, and fallback discipline.

## Purchase result state machine

Treat the purchase call as an async state transition:

```text
ready
  -> purchasing
  -> pending
  -> userCancelled
  -> success(verified)
  -> success(unverified)
  -> failed
```

`Product.purchase(options:)` can throw a StoreKit or purchase error. A successful purchase result wraps a `VerificationResult<Transaction>`; it is not enough to branch only on “success.”

The app’s next step after a verified transaction is delivery. For a non-consumable or subscription, delivery commonly means updating an entitlement projection. For a consumable, delivery may be a durable, idempotent balance or feature grant. Finish the transaction only after the app has delivered the purchased content or recorded the retryable delivery state.

Do not finish an unverified transaction and do not grant access solely because a confirmation sheet appeared. The exact policy for unverified data can differ for local-only products and server-reconciled services, but it must be explicit and testable.

## Transaction verification and JWS boundaries

The App Store cryptographically signs transaction information in JWS format. StoreKit returns signed information wrapped in `VerificationResult`. The `.verified` case passed StoreKit validation; `.unverified` includes the transaction plus a verification error.

`Transaction.jwsRepresentation` is the raw signed representation available when a transaction is present. A server can verify the JWS with the App Store Server Library or another documented server route. Device verification, local StoreKit verification, and server account authorization answer related but different questions:

| Question | Useful evidence | Do not infer |
| --- | --- | --- |
| Did StoreKit validate this transaction? | `.verified` result | That a user’s server account has been granted access. |
| Does this device currently have access? | `currentEntitlements` plus app policy | That a consumable was delivered or that another device has the same projection. |
| Did the server accept this signed event? | Server JWS validation and account ledger | That the client has completed the feature delivery. |
| Did the app deliver the product? | Durable delivery record and idempotency result | That the user read or used the content. |

Never log raw JWS values, account tokens, or sensitive purchase metadata as ordinary debug output. Store only the identifiers and status fields needed for recovery and support, with a declared retention policy.

## Current entitlements and transaction sequences

`Transaction.currentEntitlements` emits the latest transactions that currently entitle the customer. Apple documents this sequence for non-consumable purchases, active auto-renewable subscription states, and non-renewing subscriptions. Refunded or revoked products do not appear, and consumable purchases do not appear as a balance.

Use `Transaction.updates` as a long-lived task. It can emit purchases made outside the current purchase call or on another device. Route those events through the same verification, delivery, entitlement, and finish policy used by an in-app purchase.

Use `Transaction.unfinished` or `Transaction.all` for recovery/history needs. Do not treat `all` as a shortcut for current access and do not re-deliver consumables without an idempotent operation key.

On launch and foreground return, recompute the entitlement projection. A local “premium = true” flag can be a cache, but it is not authoritative if the App Store has revoked, refunded, expired, or changed the transaction state.

## Subscription status is more than expiration

For an auto-renewable subscription group, `Product.SubscriptionInfo.Status` contains a signed renewal state, renewal information, and the latest transaction. Its `RenewalState` values include:

| Renewal state | Service meaning |
| --- | --- |
| `subscribed` | The customer is currently subscribed and entitled to service. |
| `inGracePeriod` | The subscription remains entitled while the billing grace period is active. |
| `inBillingRetryPeriod` | Billing is being retried; do not grant access merely because a prior subscription exists unless another status/policy provides it. |
| `expired` | The subscription expired. |
| `revoked` | The App Store revoked access to the subscription group. |

Use `RenewalInfo` to distinguish current product, renewal date, auto-renew preference, renewal price/currency, billing retry, grace-period expiration, offers, and price-increase status. An account screen should tell the user what is active now, what is scheduled next, and what action is available.

`Product.SubscriptionInfo.Status.updates` is a useful subscription-status event sequence. Keep subscription status events separate from transaction delivery events: one describes a subscription group’s renewal state, while the other describes transaction objects that must be verified and finished according to product policy.

## Offers and redemption

App Store Connect can configure introductory, promotional, win-back, and offer-code experiences. Use the returned `Product.SubscriptionOffer` and the current App Store eligibility/configuration rather than guessing eligibility from a local boolean.

`Product.PurchaseOption` can carry an app account token, supported offer information, quantity, storefront-change behavior, or testing-specific purchase controls. Promotional offers that require a signature need the documented server-side signing boundary. Never generate a production offer signature with a private key embedded in the app.

Offer codes are alphanumeric codes configured in App Store Connect and can be redeemed through the App Store or an in-app system sheet. In SwiftUI, use the current `offerCodeRedemption` modifier and handle its completion `VerificationResult<Transaction>` where supported by the selected SDK. In UIKit, use the corresponding `AppStore` presentation API. The resulting transaction still enters the same verification and entitlement path.

## Restore and subscription management

`AppStore.sync()` synchronizes the app’s transaction information and subscription status with the App Store. Make restore a user-invoked action with explanatory copy. After it completes, read the entitlement sequences again; do not set a local restore flag without re-evaluating verified results.

Use `manageSubscriptionsSheet(isPresented:)` in SwiftUI or `AppStore.showManageSubscriptions(in:)` from UIKit when the user needs to view, upgrade, downgrade, or cancel subscriptions. The sheet is system-owned and has platform limitations; gate it with the selected SDK and target availability, and provide a clear fallback route where the surface is unsupported.

## App account token and server reconciliation

An app account token is a UUID the app can associate with a purchase. It helps a server connect a StoreKit transaction to an app account, but it does not replace transaction verification, user authentication, App Store account identity, or server authorization.

Choose the least complex architecture that matches the product:

| Product shape | Local StoreKit responsibility | Optional server responsibility |
| --- | --- | --- |
| Private local utility | Verify transactions and derive local access | None, if no cross-device/account requirement exists. |
| Account-backed subscription | Verify locally and render provisional state | Verify JWS, bind app account token, reconcile server entitlement and notifications. |
| Consumable balance | Verify, deliver idempotently, persist balance | Central ledger if balance must follow an account/device fleet. |
| Multi-app service | Verify each app’s transaction and platform product | Cross-platform account policy and App Store Server Notifications/API. |

Do not add a server only because it sounds more enterprise-grade. Do add one when server authority, cross-device access, fraud handling, fulfillment, or account reconciliation is a real requirement.

## StoreKit testing layers

StoreKit Testing in Xcode uses a local `.storekit` configuration file and can run without a connection to App Store servers. The configuration can describe products, subscription groups, offers, and test behavior. Local test receipts/certificates are not App Store production receipts.

`StoreKitTest` and `SKTestSession` support automated scenarios such as renewals, Ask to Buy, interrupted purchases, billing retry, grace period, promotional offers, and other transaction states. Use tests to prove state-machine behavior, not to claim production pricing, App Store Connect metadata, merchant configuration, or live server notification delivery.

Maintain three explicit environments:

```text
local StoreKit configuration -> deterministic unit/UI/StoreKitTest evidence
sandbox/TestFlight          -> signed target and Apple sandbox account evidence
production                  -> App Store Connect, signed release, server, and observed fulfillment evidence
```

## Liquid Glass and native paywall composition

Use StoreKit’s native merchandising surfaces as the commerce primitive and reserve custom Liquid Glass for the app-owned context around it:

```text
benefit explanation
  localized StoreKit product or subscription surface
  terms/privacy/manage/restore actions
  entitlement or pending state
```

Avoid placing a decorative glass layer over localized price/legal text. Keep the selected plan, current entitlement, pending purchase, billing retry, grace period, and unavailable-product state legible when transparency is reduced, contrast is increased, Dynamic Type is large, or motion is reduced.

Do not imitate Apple’s purchase confirmation sheet. The native system sheet is the trust surface; the app owns the honest explanation before and after it.

## On-device AI boundary

An on-device model can summarize plan differences, map a user’s stated goal to a candidate product, draft a comparison, or explain a billing state. It must not invent price, product ID, eligibility, renewal date, entitlement, refund, or successful delivery.

Use a typed proposal:

```text
user goal
  -> model proposal with candidate product IDs
  -> deterministic lookup against loaded Product values
  -> current entitlement/subscription-state check
  -> user review of price, terms, duration, and side effect
  -> native StoreKit action
  -> verified transaction and policy evaluation
```

The model should never call `purchase`, `AppStore.sync`, subscription management, or an entitlement mutation as an unreviewed tool. A user’s purchase decision and Apple’s system confirmation remain explicit.

## Availability, privacy, and proof gates

| Gate | Question |
| --- | --- |
| Product | Does the requested product exist in the selected storefront/configuration and is its metadata rendered from StoreKit? |
| Purchase | Are pending, cancellation, unverified, success, and thrown-error paths modeled? |
| Verification | Is access granted only through the documented verification/policy boundary? |
| Delivery | Is content delivered idempotently and is transaction finishing delayed until delivery is safe? |
| Subscription | Are renewal state, grace, retry, expiration, revocation, price increase, and plan change states visible? |
| Recovery | Are updates, unfinished transactions, foreground refresh, and explicit restore covered? |
| System surface | Are StoreKit views, confirmation, subscription management, and offer redemption treated as system-owned? |
| Privacy | Are JWS, account tokens, purchase metadata, and account linkage minimized and protected? |
| AI | Are proposals tied to current product/entitlement data and reviewed before side effects? |
| Accessibility | Can purchase, restore, manage, error, and entitlement tasks be completed without color, glass, or animation? |
| Release | Are App Store Connect metadata, target configuration, signed artifact, sandbox/production environment, and server evidence checked separately? |

## Sources

- [StoreKit](https://developer.apple.com/documentation/storekit)
- [StoreKit 2](https://developer.apple.com/storekit/)
- [Choosing a StoreKit API for In-App Purchases](https://developer.apple.com/documentation/storekit/choosing-a-storekit-api-for-in-app-purchases)
- [StoreKit views](https://developer.apple.com/documentation/storekit/storekit-views)
- [Product](https://developer.apple.com/documentation/storekit/product)
- [ProductView](https://developer.apple.com/documentation/storekit/productview)
- [StoreView](https://developer.apple.com/documentation/storekit/storeview)
- [SubscriptionStoreView](https://developer.apple.com/documentation/storekit/subscriptionstoreview)
- [SubscriptionStoreControlStyle](https://developer.apple.com/documentation/storekit/subscriptionstorecontrolstyle)
- [Product.purchase(options:)](https://developer.apple.com/documentation/storekit/product/purchase%28options%3A%29)
- [Product.PurchaseOption](https://developer.apple.com/documentation/storekit/Product/PurchaseOption)
- [Product.PurchaseResult](https://developer.apple.com/documentation/storekit/product/purchaseresult)
- [Transaction](https://developer.apple.com/documentation/storekit/transaction)
- [Transaction.currentEntitlements](https://developer.apple.com/documentation/storekit/transaction/currententitlements)
- [Transaction.updates](https://developer.apple.com/documentation/storekit/transaction/updates)
- [Transaction.unfinished](https://developer.apple.com/documentation/storekit/transaction/unfinished)
- [Product.SubscriptionInfo.Status](https://developer.apple.com/documentation/storekit/product/subscriptioninfo/status)
- [Product.SubscriptionInfo.RenewalState](https://developer.apple.com/documentation/storekit/product/subscriptioninfo/renewalstate)
- [Product.SubscriptionInfo.RenewalInfo](https://developer.apple.com/documentation/storekit/product/subscriptioninfo/renewalinfo)
- [AppStore](https://developer.apple.com/documentation/storekit/appstore)
- [AppStore.sync()](https://developer.apple.com/documentation/storekit/appstore/sync%28%29)
- [showManageSubscriptions(in:)](https://developer.apple.com/documentation/storekit/appstore/showmanagesubscriptions%28in%3A%29)
- [manageSubscriptionsSheet(isPresented:)](https://developer.apple.com/documentation/SwiftUI/View/manageSubscriptionsSheet%28isPresented%3A%29)
- [Supporting offer codes in your app](https://developer.apple.com/documentation/storekit/supporting-offer-codes-in-your-app)
- [Setting up StoreKit Testing in Xcode](https://developer.apple.com/documentation/xcode/setting-up-storekit-testing-in-xcode)
- [Testing In-App Purchases in Xcode](https://developer.apple.com/documentation/storekit/testing-in-app-purchases-in-xcode)
- [StoreKit Test](https://developer.apple.com/documentation/storekittest)
- [SKTestSession](https://developer.apple.com/documentation/storekittest/sktestsession)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
