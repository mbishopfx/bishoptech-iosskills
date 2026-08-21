# StoreKit and Entitlements

## Capability

StoreKit 2 is the native route for digital purchases and subscriptions distributed through the App Store. The app should turn verified StoreKit transactions into a small, testable entitlement policy; views should not scatter product-ID checks throughout the UI.

## Product-to-entitlement route

1. Define product IDs and the product type in App Store Connect or a StoreKit configuration file.
2. Load products with StoreKit 2 APIs.
3. Present price, duration, and offer information from the returned `Product`, not hard-coded copy.
4. Initiate purchase and handle every purchase result.
5. Verify the transaction result before granting access.
6. Observe `Transaction.updates` while the app runs.
7. Recompute access from `Transaction.currentEntitlements` on launch and when returning from the background.
8. Finish a verified transaction after the app has delivered the purchased access.

Illustrative policy boundary:

```swift
import StoreKit

enum AccessLevel {
    case free
    case premium
}

@MainActor
final class EntitlementStore: ObservableObject {
    @Published private(set) var access: AccessLevel = .free

    func refresh() async {
        var hasPremium = false

        for await result in Transaction.currentEntitlements {
            guard case .verified(let transaction) = result else { continue }
            if transaction.productID == "com.example.app.premium" {
                hasPremium = true
            }
        }

        access = hasPremium ? .premium : .free
    }
}
```

The product ID is an example placeholder. Compile and test the final policy against the selected StoreKit configuration and product catalog.

## Choose the product shape

| Need | StoreKit product | Entitlement policy |
| --- | --- | --- |
| Permanent feature unlock | Non-consumable | Unlock while the verified transaction remains in current entitlements. |
| Ongoing access | Auto-renewable subscription | Check current entitlement and subscription status; handle expiration and billing state. |
| Spendable in-app units | Consumable | Deliver once and persist the delivered result; do not treat current entitlements as a consumable balance. |
| Limited-time access | Non-renewing subscription or another supported product strategy | Define expiration and restoration behavior explicitly. |

## StoreKit 2 API route matrix

Keep the StoreKit adapter responsible for App Store state and the entitlement policy responsible for product access. A product, a purchase result, a verified transaction, and an entitlement are different values.

| API seam | Owns | Normalize into the app | Gate/proof |
| --- | --- | --- | --- |
| `Product.products(for:)` / `Product` | Product metadata, price, locale, subscription relationship, and offer information | Product ID, type, display price, duration/offer metadata, loading/error state | Use returned storefront metadata; test missing IDs, storefront changes, and localization. |
| `Product.purchase(options:)` | Purchase request and `Product.PurchaseResult` | `pending`, `userCancelled`, `success(verified)`, `success(unverified)`, or error | Verify result before access; test Ask to Buy/pending, cancellation, network failure, and account changes. |
| `Transaction.currentEntitlements` | Latest non-consumable and currently entitled subscription transactions | Verified entitlement candidates and revocation/expiry metadata | Recompute at launch/foreground and do not use for consumable balances; test refund/revoke/expiry. |
| `Transaction.updates` | Purchases/renewals completed outside the current purchase call | A long-lived transaction event routed through the same verifier/policy | Start a listener early, handle unverified results, deliver access, then finish only after delivery. |
| `Transaction.unfinished` / `all` | Transactions that still need processing or historical inspection | Recovery queue/history, not automatic access | Process idempotently and distinguish consumable delivery from restorable entitlements. |
| `Product.SubscriptionInfo` / status | Subscription renewal, grace, billing-retry, and expiration context | Subscription state plus policy-specific access window | Do not equate billing state with a product’s custom grace policy; test all states in configuration/sandbox. |
| `AppStore.sync()` | User-initiated restoration request | A refresh trigger followed by a new entitlement read | Provide an explicit restore route and re-read verified entitlements; do not fabricate a local restore flag. |
| StoreKit configuration / sandbox | Deterministic/local or Apple sandbox testing | Test fixture/environment identity | Record test environment; it does not prove App Store Connect metadata or production storefront behavior. |

## Entitlement ledger and target matrix

Represent access as a derived ledger rather than a Boolean written by a button:

`transaction event -> verification -> product policy -> entitlement ledger -> UI/system projection`

The ledger should retain product ID, transaction/original transaction identity where needed, verification result, purchase type, expiration/revocation, account scope, environment, policy version, granted-at, and last-evaluated time. For consumables, persist an idempotent delivery operation and balance separately; `currentEntitlements` does not represent a consumable balance.

| Target/surface | StoreKit responsibility | Safe boundary |
| --- | --- | --- |
| Main app target | Load products, purchase, verify, restore, listen, and own the entitlement policy | Entitlement service/repository; no product-ID checks scattered through views. |
| Widget/Live Activity extension | Render only a privacy-safe derived access/status projection | Do not start a purchase from a glanceable surface unless the selected route explicitly owns it; refresh after entitlement changes. |
| App Intent/control | Validate entitlement again before a premium mutation | A system invocation is not proof that the person is entitled; return an actionable denial. |
| Shared package | Define product identifiers as data/configuration and policy interfaces | Do not make a package silently depend on App Store Connect, a bundle entitlement, or a live account. |
| Server-backed account | Reconcile signed transaction/subscription data with the server’s account policy | Local verification and server authorization answer different questions; bind them deliberately. |

## Purchase and recovery state machine

Model these states independently:

`idle -> loadingProducts -> productsReady|productsUnavailable`

`productsReady -> purchasing -> pending|cancelled|unverified|verified|failed`

`verified -> delivering -> entitled|deliveryFailed -> retry`

and background paths:

`transactionUpdate -> verify -> policyEvaluate -> deliver -> finish`

On relaunch, foreground return, account change, or an explicit restore, re-evaluate current entitlements and unfinished transactions. If delivery is interrupted, keep a durable idempotency key and retry without granting the same consumable twice. If verification fails, show unavailable/pending access rather than a premium success state.

## Boundaries and failure modes

- Product loading can fail or return an empty result; the paywall needs an honest unavailable state.
- A purchase result can be pending, cancelled, unverified, or successful. Do not grant paid access on a non-verified result.
- The transaction listener is part of the app’s lifecycle; start it early enough to receive purchases completed elsewhere.
- StoreKit testing, sandbox, and production can differ. Test restore, upgrades, downgrades, refunds, expiration, family sharing where applicable, and account changes.
- Pricing, subscription terms, and legal disclosures must remain synchronized with App Store Connect and the App Store review requirements.
- Server-side receipt or transaction processing is a separate architecture decision; never invent a server requirement for a local-only product without a reason.

## Verification route

- Exercise the full purchase state machine with a StoreKit configuration file.
- Validate product IDs and pricing in the intended storefront.
- Test a signed build with sandbox accounts and restore on a second device.
- Verify that free functionality remains usable when StoreKit is unavailable.
- Log entitlement transitions without logging payment credentials or raw sensitive purchase data.

## Sources

- [StoreKit](https://developer.apple.com/documentation/storekit)
- [StoreKit 2](https://developer.apple.com/storekit/)
- [Choosing a StoreKit API for In-App Purchases](https://developer.apple.com/documentation/storekit/choosing-a-storekit-api-for-in-app-purchases)
- [Product](https://developer.apple.com/documentation/storekit/product)
- [Transaction](https://developer.apple.com/documentation/storekit/transaction)
- [currentEntitlements](https://developer.apple.com/documentation/storekit/transaction/currententitlements)
- [updates](https://developer.apple.com/documentation/storekit/transaction/updates)
- [unfinished](https://developer.apple.com/documentation/storekit/transaction/unfinished)
- [AppStore.sync()](https://developer.apple.com/documentation/storekit/appstore/sync%28%29)
- [Product.SubscriptionInfo](https://developer.apple.com/documentation/storekit/product/subscriptioninfo)
- [Product.PurchaseResult](https://developer.apple.com/documentation/storekit/product/purchaseresult)
- [In-App Purchase](https://developer.apple.com/in-app-purchase/)
- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
