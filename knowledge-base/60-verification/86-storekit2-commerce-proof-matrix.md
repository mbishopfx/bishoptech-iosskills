# StoreKit 2 product, purchase, subscription, and entitlement proof matrix

Use this matrix before describing a StoreKit 2 route as working. Record the exact SDK, deployment target, device/OS, storefront, App Store Connect product configuration, StoreKit configuration, account, target, build, and server environment.

## Evidence ladder

| Claim | Minimum useful evidence | Stronger evidence | Does not prove |
| --- | --- | --- | --- |
| Product metadata loads | Product fixture or local StoreKit configuration | Sandbox/TestFlight product load in the intended storefront | Production pricing or App Store Connect review. |
| Product view renders | SwiftUI preview/UI test with deterministic product state | Device run with localized product data and loading/missing states | Successful payment or entitlement. |
| Purchase starts | Direct purchase test with known product | Device system confirmation flow in sandbox/TestFlight | Provider delivery or universal availability. |
| Purchase result maps correctly | `Product.PurchaseResult` fixtures for pending/cancelled/success/error | StoreKitTest and sandbox negative/positive scenarios | Production settlement. |
| Transaction is verified | `.verified`/`.unverified` test cases | Signed sandbox or production JWS validation on device/server | That the app delivered the product. |
| Entitlement is current | `Transaction.currentEntitlements` fixture and policy test | Launch/foreground/account-change refresh on a signed device | Consumable balance or cross-account access. |
| Consumable delivered once | Idempotent delivery test keyed by transaction identity | Interrupted delivery/relaunch/retry on device and server | That a user consumed or enjoyed the item. |
| Subscription state is correct | Renewal-state/status fixtures | Sandbox/TestFlight renewal, grace, retry, plan change, refund, revoke, and expiration | Every future renewal or region. |
| Restore works | `AppStore.sync()` failure/success fixtures followed by entitlement refresh | User-invoked device restore with sandbox account | That a local “restored” flag is authoritative. |
| Manage subscriptions works | Modifier/action presentation fixture | System sheet on the intended signed device/platform | That cancellation happened without rereading status. |
| Offer code works | Redemption completion and verification fixture | Sandbox/TestFlight code redemption with entitlement refresh | Offer eligibility in every storefront. |
| AI explanation is grounded | Proposal fixture validated against current `Product` data | Device proposal with current storefront/product timestamp and review | A model’s commercial or entitlement claims without deterministic data. |
| Paywall is accessible | Semantic UI tests and preview states | Physical-device VoiceOver, Dynamic Type, reduced-effects, RTL, keyboard/pointer run | Accessibility from a screenshot. |
| Release is ready | Archive, target, product/configuration, and privacy review | Signed TestFlight install with sandbox and intended server path | App Store approval or production reliability. |

## Product and target configuration matrix

| Boundary | Evidence to collect | Failure cases | Claim language |
| --- | --- | --- | --- |
| Product identifier | App Store Connect or `.storekit` record | Typo, missing product, wrong bundle/app | “The tested catalog contains this product ID.” |
| Product type | Non-consumable, consumable, non-renewing, or auto-renewable record | Entitlement policy treats a consumable like current access | “The tested policy matches the configured product type.” |
| Subscription group | Group membership and level order | Plan comparison crosses groups or hides upgrade/downgrade rules | “These plans belong to the tested group.” |
| Localization | Product name, description, price/currency from storefront | Hard-coded price, clipped currency, untranslated product copy | “The tested storefront rendered the localized metadata.” |
| Offers | Introductory/promotional/win-back/offer-code configuration | Offer shown to ineligible customer or stale copy | “The configured offer appeared for the tested eligibility state.” |
| Terms/privacy | App Store Connect policy metadata or custom destinations | Missing links, inaccessible legal copy, custom URL drift | “The tested purchase surface exposes the configured policies.” |
| Main target | StoreKit import, deployment target, product IDs, capabilities | Extension or alternate target missing the route | “The named target compiles the selected StoreKit surface.” |
| Extension target | Widget/Live Activity/App Intent access policy | Extension starts purchase or exposes private entitlement data | “The extension renders the tested derived projection only.” |
| Server boundary | App account token, JWS verification, notification/API configuration | Secrets or raw JWS logged/shipped in the client | “Server reconciliation is configured for the tested environment.” |

## Product loading and merchandising matrix

| Boundary | Deterministic test | Device/release proof | Does not prove |
| --- | --- | --- | --- |
| Product request | Requested IDs, returned IDs, missing-ID mapping | Storefront request on signed device | A missing product is free or intentionally configured. |
| Product price | Currency/price fixture | Localized sandbox/TestFlight product display | Production tax or price tier everywhere. |
| `ProductView` | One-product loading, success, missing, and error state | Device StoreKit view with configured product | Purchase success. |
| `StoreView` | Collection order and product filtering | Device collection with localized icons/marketing content | Catalog completeness beyond the tested IDs. |
| `SubscriptionStoreView` | Group/collection/options fixture | Device plan picker with terms/privacy and offer | Entitlement after purchase. |
| StoreKit style | Automatic/buttons/picker/prominent/paged/compact rendering | Device layout at target sizes and Dynamic Type | Universal visual equivalence to Apple’s own App Store. |
| Custom paywall | App-owned benefit/plan/status state fixtures | Signed device with live localized metadata | Legal/commercial correctness of custom copy alone. |
| Loading fallback | Offline, empty, missing, and retry states | Device network interruption and storefront change | Product catalog recovery in every environment. |

## Purchase and verification matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| Availability | `AppStore.canMakePayments`/target availability fixture | App shows purchase action when disabled or unsupported | The tested device/target can offer the route. |
| Purchase start | Product purchase action fixture | Duplicate taps, no loading state, wrong product | The app initiated the tested purchase request. |
| Pending | StoreKitTest Ask to Buy/pending scenario | Pending shown as access, retry duplicates purchase | The app keeps the tested purchase pending. |
| Cancellation | System/user cancellation fixture | Cancellation shown as failure or success, lost focus | The cancellation recovery path works. |
| Throwing error | Network/StoreKit error fixture | Raw error leaked, retry unsafe, feature locked forever | The app maps the tested error to a usable state. |
| `.verified` | Verified transaction fixture | Access granted before verification, no delivery record | StoreKit verified the tested transaction. |
| `.unverified` | Invalid/test verification fixture | App grants access or finishes blindly | The app rejects or handles the tested unverified result according to policy. |
| JWS handling | Redacted local/server verification trace | Raw JWS in logs, wrong environment certificate | The selected verifier accepted the tested signed information. |
| Finish ordering | Delivery succeeds before `finish()` fixture | Transaction finished before content is durable | The tested delivery/finish order is safe for retry. |
| Background updates | `Transaction.updates` event fixture | Listener starts too late, duplicate delivery | The listener handles the tested outside-app event. |

## Entitlement and delivery matrix

| Boundary | Deterministic evidence | Device/server evidence | Does not prove |
| --- | --- | --- | --- |
| Non-consumable | Verified current entitlement grants feature | Relaunch/restore/refund/revoke on sandbox device | Future App Store state. |
| Auto-renewable | Active state maps to access | Renewal and status changes on sandbox/TestFlight | Guaranteed renewal success. |
| Non-renewing | App-defined expiration and restore policy | Device/account restore if server-backed | Automatic App Store renewal behavior. |
| Consumable | Transaction-keyed idempotent delivery/balance test | Interrupted delivery, relaunch, retry, account state | `currentEntitlements` representing the balance. |
| `currentEntitlements` | Refunded/revoked/consumable exclusion fixture | Launch/foreground refresh | Full transaction history or server ledger. |
| `unfinished`/`all` | Recovery queue fixture | Recovery after termination or crash | Current access without verification/policy. |
| Account token | UUID association fixture | Server binding and transaction reconciliation | Authentication or authorization by itself. |
| Local ledger | Snapshot/version/retry fixture | Relaunch, migration, storage failure | App Store authority. |

## Subscription status matrix

| Status | Required UI proof | State boundary |
| --- | --- | --- |
| `subscribed` | Current plan and active access | Service is entitled under the tested policy. |
| `inGracePeriod` | Access continues plus billing-resolution action | Access is temporary and must be re-evaluated. |
| `inBillingRetryPeriod` | Billing issue and manage/support path | Do not assume entitlement from prior purchase alone. |
| `expired` | Ended access and plan/restore route | No current access unless another valid status/policy grants it. |
| `revoked` | Access removed and support explanation | App Store revoked the subscription-group access. |
| Price increase pending | Consent/management explanation | Renewal may expire if the customer does not consent. |
| Auto-renew disabled | End date and continued access until expiry if applicable | Cancellation is not always immediate access removal. |
| Upgrade/downgrade | Current and next plan, effective timing | Plan changes have different effective timing. |
| Family sharing | Policy-specific entitlement explanation | One status does not describe every account/device relationship. |

Test `Product.SubscriptionInfo.Status.updates`, latest transaction verification, and `RenewalInfo` fields together. Do not derive all status copy from a single `willAutoRenew` Boolean.

## Restore, management, and offers matrix

| Route | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| Restore action | User tap -> `AppStore.sync()` -> new entitlement read | Local flag flips before sync, no failure state | The tested user-triggered restore path completed. |
| Manage sheet | Presentation and dismissal state | Unsupported target, no refresh after change | The system management sheet presented on the tested platform. |
| Offer-code sheet | Valid/invalid/expired/downgrade code fixtures | Code entry mistaken for entitlement | The tested redemption result was handled. |
| Introductory offer | Eligible/ineligible customer and renewal price fixture | Free copy omits later charge/term | The tested offer appeared under the tested eligibility. |
| Promotional offer | Server signature and purchase-option fixture | Private key in app, invalid signature | The selected offer signature was accepted in the test environment. |
| Win-back offer | Lapsed subscription/eligible ID fixture | Win-back shown to active user | The selected win-back flow was observed for the test user. |

## StoreKit testing matrix

| Environment | Good for | Must not be used to claim |
| --- | --- | --- |
| Local `.storekit` file | Product states, UI, purchase results, renewal timing, failures, offers, and deterministic automation | App Store production pricing, real server notifications, App Store review. |
| `StoreKitTest` / `SKTestSession` | Unit/CI control over transactions, renewals, Ask to Buy, and failure cases | Physical device hardware, production account, universal storefront behavior. |
| Sandbox/TestFlight | Signed target, Apple account, localized product/storefront, subscription management, selected offer flows | Production settlement or all regional/device behavior. |
| Production | Observed approved product, account, server, and fulfillment path | Future reliability or App Store approval of untested changes. |

Local StoreKit receipts/certificates and production App Store receipts are different evidence classes. Keep environment labels in logs and test reports.

## Privacy, accessibility, and AI matrix

Verify:

- raw JWS, account tokens, purchase metadata, and server credentials are not logged or bundled accidentally;
- product and entitlement data are minimized in widgets, Live Activities, notifications, and shared containers;
- VoiceOver reads plan, price, term, offer, current state, and next action;
- Dynamic Type, high contrast, reduced transparency, reduced motion, RTL, and long localized currency strings remain usable;
- an AI explanation is grounded in the current `Product`/`RenewalInfo` data and carries a freshness/source marker;
- model output cannot call purchase, restore, manage, or an entitlement mutation without an explicit user intent;
- a non-AI, free, manual, or support fallback remains usable when the model is unavailable;
- a custom Liquid Glass paywall does not hide price, legal text, selection, pending state, or management actions.

## Release evidence packet

Record:

```text
target and bundle identifier:
SDK/deployment target/platform:
App Store Connect product IDs and subscription group:
local StoreKit configuration / sandbox / production environment:
storefront and account type:
signed artifact/build number:
entitlement/product policy version:
verification path and server environment:
purchase/restore/offer/manage user actions:
transaction/entitlement/delivery evidence:
accessibility and localization settings:
AI proposal and deterministic validation record:
known limitations and unproved claims:
```

## Claim language

Prefer:

- “The local StoreKit test mapped the pending result correctly.”
- “The sandbox device received a verified transaction and the app delivered the tested entitlement.”
- “The subscription management sheet presented on the tested platform.”
- “The model proposed a plan explanation from current product metadata and the user reviewed it.”

Avoid:

- “The paywall works everywhere.”
- “The purchase callback proves the customer paid.”
- “The simulator proves the App Store product is configured.”
- “The AI knows which subscription the user needs.”

## Sources

- [StoreKit](https://developer.apple.com/documentation/storekit)
- [StoreKit views](https://developer.apple.com/documentation/storekit/storekit-views)
- [ProductView](https://developer.apple.com/documentation/storekit/productview)
- [StoreView](https://developer.apple.com/documentation/storekit/storeview)
- [SubscriptionStoreView](https://developer.apple.com/documentation/storekit/subscriptionstoreview)
- [Product.purchase(options:)](https://developer.apple.com/documentation/storekit/product/purchase%28options%3A%29)
- [Product.PurchaseOption](https://developer.apple.com/documentation/storekit/Product/PurchaseOption)
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
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
