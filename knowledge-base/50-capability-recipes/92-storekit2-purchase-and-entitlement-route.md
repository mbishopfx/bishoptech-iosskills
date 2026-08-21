# StoreKit 2 purchase, subscription, and entitlement capability route

## Use this route when

Use this route for digital features, consumables, non-consumables, non-renewing subscriptions, or auto-renewable subscriptions distributed through the App Store. Keep the route separate from Apple Pay for physical goods and from local feature flags that are not backed by a verified StoreKit policy.

Core route:

```text
product configuration
  -> product metadata
  -> native StoreKit view or app-owned selection
  -> purchase/restore/offer system action
  -> verification
  -> idempotent delivery
  -> entitlement ledger
  -> feature access and status UI
```

## Route decision table

| Need | Start with | Add when needed |
| --- | --- | --- |
| One-time feature unlock | `ProductView` or loaded `Product` | Current-entitlement refresh, restore, and delivery record. |
| Several in-app products | `StoreView` or a custom catalog | Product loading/error policy and purchase-event router. |
| Subscription plans in one group | `SubscriptionStoreView` | Renewal status, manage sheet, offers, billing states, and plan comparison. |
| Custom purchase UI | `Product.products(for:)` plus `purchase(options:)` | Localized product rendering, direct purchase policy, and all purchase result cases. |
| Consumable credits | Verified transaction plus delivery ledger | Server authority or persistent local idempotency if credits must survive reinstalls/accounts. |
| Restore | User action -> `AppStore.sync()` -> entitlement refresh | Clear “restoring” state and account/support explanation. |
| Subscription management | `manageSubscriptionsSheet` or `AppStore.showManageSubscriptions` | Platform availability fallback and current-plan/status display. |
| Offer code | `offerCodeRedemption` or `AppStore.presentOfferCodeRedeemSheet` | Result verification and entitlement refresh. |

## 1. Define product policy before UI

Keep product identifiers and access policy centralized:

```swift
enum StoreProduct: String, CaseIterable, Sendable {
    case monthly = "com.example.pro.monthly"
    case annual = "com.example.pro.annual"
    case lifetime = "com.example.pro.lifetime"
    case credits = "com.example.credits"

    var id: String { rawValue }
}

enum Entitlement: Hashable, Sendable {
    case pro
    case credits
}

struct ProductPolicy: Sendable {
    let productID: String
    let grants: Set<Entitlement>
    let isConsumable: Bool
}
```

These identifiers are placeholders. In a real app, keep the product catalog aligned with App Store Connect and the active StoreKit configuration. Do not let a model, remote response, or view invent an arbitrary product ID.

## 2. Load and normalize Product values

```swift
import StoreKit

struct StoreCatalog: Sendable {
    let products: [Product]
    let missingIDs: Set<String>
}

func loadCatalog(ids: Set<String>) async throws -> StoreCatalog {
    let products = try await Product.products(for: ids)
    let returned = Set(products.map(\.id))
    return StoreCatalog(
        products: products,
        missingIDs: ids.subtracting(returned)
    )
}
```

Render product name, description, price, currency, subscription period, and offer metadata from the returned `Product`. A missing ID is a catalog/configuration state, not a free product.

For the native surface, prefer:

```swift
SubscriptionStoreView(productIDs: [
    StoreProduct.monthly.id,
    StoreProduct.annual.id
]) {
    Text("Choose a plan")
}
```

Confirm the exact initializer and target availability in the selected SDK. StoreKit views can load products automatically and present purchase controls; the app still owns the surrounding benefits, fallback, and entitlement projection.

## 3. Start one transaction listener early

Route purchase events made outside the current call through the same policy:

```swift
@MainActor
final class StoreCoordinator: ObservableObject {
    private var updatesTask: Task<Void, Never>?

    func start() {
        updatesTask?.cancel()
        updatesTask = Task { [weak self] in
            for await result in Transaction.updates {
                guard let self else { return }
                await self.handle(result)
            }
        }
    }

    deinit {
        updatesTask?.cancel()
    }

    private func handle(
        _ result: VerificationResult<Transaction>
    ) async {
        // Route through the same verification, delivery, and finish policy
        // used by an in-app purchase.
    }
}
```

The code is a route sketch. In a production app, avoid a detached unowned task, define the actor boundary deliberately, and make delivery idempotent before calling `finish()`.

## 4. Purchase and verify

```swift
enum PurchaseOutcome: Sendable {
    case pending
    case cancelled
    case verified(Transaction)
    case unverified(Transaction, Error)
}

func purchase(_ product: Product) async throws -> PurchaseOutcome {
    let result = try await product.purchase()

    switch result {
    case .pending:
        return .pending
    case .userCancelled:
        return .cancelled
    case .success(let verification):
        switch verification {
        case .verified(let transaction):
            return .verified(transaction)
        case .unverified(let transaction, let error):
            return .unverified(transaction, error)
        }
    @unknown default:
        throw StoreRouteError.unknownPurchaseResult
    }
}
```

Keep the purchase UI state separate from access state. A verified result enters delivery/policy evaluation; it does not immediately mean every feature can open.

When an app account token is required, pass the documented `Product.PurchaseOption.appAccountToken(_:)` and reconcile the resulting transaction on the intended server. Do not put a signing key or provider secret in the app.

## 5. Derive non-consumable and subscription access

```swift
struct EntitlementSnapshot: Sendable, Equatable {
    var activeProductIDs: Set<String> = []
    var verifiedAt: Date?
}

func readCurrentEntitlements() async -> EntitlementSnapshot {
    var active = Set<String>()

    for await result in Transaction.currentEntitlements {
        guard case .verified(let transaction) = result else { continue }
        active.insert(transaction.productID)
    }

    return EntitlementSnapshot(
        activeProductIDs: active,
        verifiedAt: .now
    )
}
```

`currentEntitlements` does not represent a consumable balance. For consumables, use an idempotent delivery record tied to the verified transaction and keep the balance in the domain store appropriate to the product.

Map product IDs to capabilities in one policy layer:

```swift
func grantsPro(_ snapshot: EntitlementSnapshot) -> Bool {
    snapshot.activeProductIDs.contains(StoreProduct.lifetime.id)
        || snapshot.activeProductIDs.contains(StoreProduct.monthly.id)
        || snapshot.activeProductIDs.contains(StoreProduct.annual.id)
}
```

The policy should include revocation, expiration, account scope, server state, and any product-specific grace rule rather than scattering product-ID checks across views.

## 6. Read subscription status separately

```swift
func subscriptionStatuses(
    for product: Product
) async throws -> [Product.SubscriptionInfo.Status] {
    guard let subscription = product.subscription else { return [] }
    return try await subscription.status
}
```

Verify the exact async property/signature in the selected SDK. For each status, inspect the verification result for both the renewal information and latest transaction. Model at least:

```text
subscribed
inGracePeriod
inBillingRetryPeriod
expired
revoked
```

Use `RenewalInfo` to render current product, next renewal date, auto-renew preference, renewal price, grace-period expiration, price-increase status, and eligible offers. Do not show “active” solely because a product was once purchased.

## 7. Restore explicitly

```swift
func restorePurchases() async -> Result<EntitlementSnapshot, Error> {
    do {
        try await AppStore.sync()
        return .success(await readCurrentEntitlements())
    } catch {
        return .failure(error)
    }
}
```

Attach this to a user-visible Restore Purchases action. If synchronization fails, preserve the previous known projection but label it as unrefreshed; do not claim the restore succeeded.

## 8. Manage subscriptions through the system

SwiftUI route:

```swift
struct ManageSubscriptionButton: View {
    @State private var showingSheet = false

    var body: some View {
        Button("Manage subscription") {
            showingSheet = true
        }
        .manageSubscriptionsSheet(isPresented: $showingSheet)
    }
}
```

Use `AppStore.showManageSubscriptions(in:)` for a UIKit route. The surface is system-owned and should be gated for unsupported platform/target contexts. After the sheet dismisses, refresh subscription state because the user may have upgraded, downgraded, or cancelled.

## 9. Redeem offer codes

```swift
struct OfferCodeButton: View {
    @State private var showingRedemption = false
    @State private var message: String?

    var body: some View {
        Button("Redeem offer code") {
            showingRedemption = true
        }
        .offerCodeRedemption(
            isPresented: $showingRedemption
        ) { result in
            switch result {
            case .success(let verification):
                switch verification {
                case .verified:
                    message = "Offer applied. Refreshing access."
                case .unverified:
                    message = "Offer received but could not be verified."
                }
            case .failure:
                message = "Offer code could not be redeemed."
            }
        }
    }
}
```

The exact completion shape is SDK/version-sensitive; verify it in the named target. After a successful redemption, route the transaction through the same verification and entitlement refresh as a normal purchase. Do not treat presentation or code entry as entitlement.

## 10. Use StoreKit views with app-owned context

```swift
struct ProPaywall: View {
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                Text("Unlock your private workspace")
                    .font(.largeTitle.bold())

                Text("Keep your core workflow free. Pro adds the advanced tools shown here.")
                    .multilineTextAlignment(.center)

                SubscriptionStoreView(productIDs: [
                    StoreProduct.monthly.id,
                    StoreProduct.annual.id
                ]) {
                    Text("Choose a plan")
                }
                .subscriptionStoreControlStyle(.prominentPicker)

                Button("Restore purchases") {
                    // Start the explicit restore route.
                }
                .buttonStyle(.borderless)
            }
            .padding()
        }
    }
}
```

Use the native StoreKit view for localized product and purchase behavior. Confirm modifiers and styles against the selected SDK. Keep the benefit text, restore action, accessibility labels, and free fallback in the app-owned layer.

## 11. AI proposal route

```swift
struct PlanProposal: Sendable, Equatable {
    let productID: String
    let reason: String
    let sourceProductVersion: String
    let requiresReview: Bool
}

func validateProposal(
    _ proposal: PlanProposal,
    against products: [Product]
) -> Product? {
    guard proposal.requiresReview else { return nil }
    return products.first { $0.id == proposal.productID }
}
```

The model can propose a comparison. The deterministic layer resolves the product against the loaded catalog, displays the current price and terms, and waits for a user action before purchase. Never allow an AI tool to call `purchase`, `sync`, or `manageSubscriptionsSheet` without an explicit user-facing intent.

## Fallbacks

- StoreKit unavailable: preserve free functionality and explain that paid features cannot be refreshed now.
- Product missing: show a configuration/unavailable state, not a fake price.
- Purchase pending: keep the feature locked or policy-defined, with a clear pending explanation.
- Unverified: do not grant access; preserve retry/support path.
- Restore failure: retain known state and label it stale/unrefreshed.
- Subscription management unavailable: provide support/instructions appropriate to the target.
- Model unavailable: use deterministic product metadata and a manual plan comparison.
- Server unreachable: use the explicit local/server policy; never pretend provider reconciliation completed.

## Proof route

### Deterministic

- product ID mapping and missing-product behavior;
- purchase result mapping, including pending/cancelled/unverified/error;
- verification and finish ordering;
- idempotent consumable delivery;
- current-entitlement refresh and subscription-state mapping;
- restore/offer-code completion and state refresh;
- AI proposal validation against a loaded catalog.

### UI and accessibility

- StoreKit view loading, unavailable, selected, purchase, pending, and verified states;
- restore/manage/offer-code actions;
- Dynamic Type, VoiceOver, reduced transparency, increased contrast, reduced motion, RTL, and long localized prices;
- app-owned free fallback and support paths.

### Device and release

Use local StoreKit configuration and `StoreKitTest` for deterministic transaction state. Use sandbox/TestFlight for signed target, App Store account, product metadata, subscription management, and offer behavior. Use production only for approved product/provider/server evidence. A preview, local `.storekit` run, or simulator purchase does not prove App Store Connect pricing, production entitlement, server notification delivery, or App Store review readiness.

## Sources

- [StoreKit](https://developer.apple.com/documentation/storekit)
- [Product](https://developer.apple.com/documentation/storekit/product)
- [Product.products(for:)](https://developer.apple.com/documentation/storekit/product/products%28for%3A%29)
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
- [StoreKit views](https://developer.apple.com/documentation/storekit/storekit-views)
- [SubscriptionStoreView](https://developer.apple.com/documentation/storekit/subscriptionstoreview)
- [Setting up StoreKit Testing in Xcode](https://developer.apple.com/documentation/xcode/setting-up-storekit-testing-in-xcode)
- [StoreKit Test](https://developer.apple.com/documentation/storekittest)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
