# StoreKit 2 purchase, subscription, and entitlement recipes

These are compile-oriented route sketches, not verified app code. Confirm the selected iOS 26 SDK signatures, availability, product IDs, App Store Connect configuration, `.storekit` target membership, storefront behavior, server verification, accessibility, and signed-device evidence before copying them into a product.

Shared route:

```text
catalog -> native/app-owned merchandising -> purchase result
       -> verification -> delivery -> entitlement refresh -> feature access
```

## Recipe 1: load a product catalog and report missing IDs

```swift
import StoreKit

struct CatalogResult: Sendable {
    let products: [Product]
    let missingIDs: Set<String>
}

func loadProducts(ids: Set<String>) async throws -> CatalogResult {
    let products = try await Product.products(for: ids)
    let returnedIDs = Set(products.map(\.id))

    return CatalogResult(
        products: products,
        missingIDs: ids.subtracting(returnedIDs)
    )
}
```

Render names, descriptions, prices, currency, and subscription metadata from the returned values. Do not convert a missing product to a locally invented price or entitlement.

## Recipe 2: use a native ProductView

```swift
import StoreKit
import SwiftUI

struct LifetimeProductView: View {
    var body: some View {
        ProductView(id: "com.example.app.lifetime")
            .productViewStyle(.large)
    }
}
```

Verify the available initializer and `ProductViewStyle` value in the selected SDK. Surround the view with app-owned benefits, restore, support, and access state. The StoreKit view owns localized product merchandising and purchase initiation; it does not replace the app’s entitlement policy.

## Recipe 3: use SubscriptionStoreView for one subscription group

```swift
import StoreKit
import SwiftUI

struct SubscriptionPlans: View {
    var body: some View {
        SubscriptionStoreView(productIDs: [
            "com.example.app.monthly",
            "com.example.app.annual"
        ]) {
            Text("Choose a plan")
        }
        .subscriptionStoreControlStyle(.prominentPicker)
        .subscriptionStoreButtonLabel(.multiline)
    }
}
```

The exact label/style availability can vary by SDK. Keep terms-of-service, privacy, offer, and renewal copy visible and test the view with long localized product metadata. Use `visibleRelationships` or a selected product collection when the product should not show every plan in the group.

## Recipe 4: purchase a Product directly and preserve every result

```swift
import StoreKit

enum PurchaseState: Sendable, Equatable {
    case idle
    case purchasing
    case pending
    case cancelled
    case verified
    case unverified
    case failed
}

func purchase(_ product: Product) async -> PurchaseState {
    do {
        switch try await product.purchase() {
        case .pending:
            return .pending
        case .userCancelled:
            return .cancelled
        case .success(let result):
            switch result {
            case .verified:
                return .verified
            case .unverified:
                return .unverified
            }
        @unknown default:
            return .failed
        }
    } catch {
        return .failed
    }
}
```

The purchase result is not the final entitlement state. On `.verified`, route the transaction through delivery/policy evaluation. Do not grant paid access on `.unverified`, and do not call `finish()` before durable delivery.

## Recipe 5: add an app account token without putting secrets in the client

```swift
import StoreKit

func purchaseForAccount(
    _ product: Product,
    accountToken: UUID
) async throws -> Product.PurchaseResult {
    try await product.purchase(options: [
        .appAccountToken(accountToken)
    ])
}
```

The UUID helps associate the transaction with an app account. It does not authenticate the person, verify the transaction, or replace server-side authorization. Never put a payment-provider secret or offer-signing private key in this call.

## Recipe 6: derive access from current entitlements

```swift
import StoreKit

func currentProductIDs() async -> Set<String> {
    var productIDs = Set<String>()

    for await result in Transaction.currentEntitlements {
        guard case .verified(let transaction) = result else { continue }
        productIDs.insert(transaction.productID)
    }

    return productIDs
}
```

`currentEntitlements` is for current access, not transaction history and not a consumable balance. Keep a separate idempotent delivery ledger for consumables. Re-evaluate on launch, foreground return, restore, account changes, and transaction updates.

## Recipe 7: route Transaction.updates through one handler

```swift
import StoreKit

@MainActor
final class TransactionListener {
    private var task: Task<Void, Never>?

    func start() {
        task?.cancel()
        task = Task { [weak self] in
            for await result in Transaction.updates {
                guard let self else { return }
                await self.handle(result)
            }
        }
    }

    func stop() {
        task?.cancel()
        task = nil
    }

    private func handle(
        _ result: VerificationResult<Transaction>
    ) async {
        switch result {
        case .verified(let transaction):
            // Deliver idempotently, update policy, then finish.
            await transaction.finish()
        case .unverified(let transaction, let error):
            // Record a redacted retry/support state; do not grant access.
            _ = transaction
            _ = error
        }
    }
}
```

This is intentionally incomplete around delivery. In a real implementation, call `finish()` only after the app has durably recorded delivery or a retryable delivery command. Start the listener early enough to receive purchases made elsewhere.

## Recipe 8: recover unfinished transactions

```swift
import StoreKit

func recoverUnfinishedTransactions() async {
    for await result in Transaction.unfinished {
        switch result {
        case .verified(let transaction):
            // Re-run the idempotent delivery policy.
            await transaction.finish()
        case .unverified:
            // Keep the transaction unresolved and surface support/retry state.
            continue
        }
    }
}
```

The code assumes delivery has already been made idempotent. Do not finish an unfinished consumable before reconciling its delivery key and balance.

## Recipe 9: inspect subscription status and renewal information

```swift
import StoreKit

func readSubscriptionStatus(
    for product: Product
) async throws -> [Product.SubscriptionInfo.Status] {
    guard let subscription = product.subscription else { return [] }
    return try await subscription.status
}

func renewalState(
    from status: Product.SubscriptionInfo.Status
) -> Product.SubscriptionInfo.RenewalState? {
    guard case .verified(let renewalInfo) = status.renewalInfo else {
        return nil
    }
    return renewalInfo.state
}
```

Inspect both `status.renewalInfo` and `status.transaction` verification results in the real policy. Model subscribed, grace, billing retry, expired, revoked, auto-renew preference, next renewal, and price-increase states separately.

## Recipe 10: restore through a user action

```swift
import StoreKit

func restoreAndRefresh() async -> Result<Set<String>, Error> {
    do {
        try await AppStore.sync()
        return .success(await currentProductIDs())
    } catch {
        return .failure(error)
    }
}
```

Call this only from a clear Restore Purchases action or the product’s explicit account-recovery route. A successful synchronization still requires a fresh entitlement read.

## Recipe 11: show subscription management in SwiftUI

```swift
import StoreKit
import SwiftUI

struct SubscriptionManagementAction: View {
    @State private var isPresented = false

    var body: some View {
        Button("Manage subscription") {
            isPresented = true
        }
        .manageSubscriptionsSheet(isPresented: $isPresented)
    }
}
```

The modifier presents an Apple-owned surface. Refresh subscription status after dismissal. Gate the action for unsupported target contexts and provide a clear fallback rather than a button that silently does nothing.

## Recipe 12: use AppStore.showManageSubscriptions from UIKit

```swift
import StoreKit
import UIKit

func showManageSubscriptions(from scene: UIWindowScene) async {
    do {
        try await AppStore.showManageSubscriptions(in: scene)
    } catch {
        // Map to an app-owned support/unavailable state.
    }
}
```

Use the group-specific overload when the product needs to focus subscription management on a particular group and the target SDK supports it. Do not claim that the sheet was shown from a preview or an unsupported Mac context.

## Recipe 13: redeem an offer code through SwiftUI

```swift
import StoreKit
import SwiftUI

struct OfferRedemptionAction: View {
    @State private var isPresented = false
    @State private var status = ""

    var body: some View {
        VStack {
            Button("Redeem offer code") {
                isPresented = true
            }
            Text(status)
        }
        .offerCodeRedemption(isPresented: $isPresented) { result in
            // The current SDK may deliver a Result containing a
            // VerificationResult<Transaction>. Match both success cases,
            // then refresh current entitlements.
            switch result {
            case .success:
                status = "Offer result received. Refreshing access."
            case .failure:
                status = "Offer code could not be redeemed."
            }
        }
    }
}
```

Verify the overload and completion type in the selected SDK, especially when moving between deprecated and current redemption APIs. Code entry or sheet presentation is not entitlement; the resulting transaction still needs verification and policy evaluation.

## Recipe 14: make a paywall state-driven

```swift
enum PaywallState: Sendable, Equatable {
    case loading
    case ready(products: [String])
    case purchasing(productID: String)
    case pending
    case entitled(productID: String)
    case unavailable
    case failed
}

struct PaywallStateLabel: View {
    let state: PaywallState

    var body: some View {
        Group {
            switch state {
            case .loading:
                ProgressView("Loading plans")
            case .ready:
                Text("Choose a plan")
            case .purchasing:
                ProgressView("Confirming purchase")
            case .pending:
                Text("Purchase approval is pending")
            case .entitled:
                Label("Access is active", systemImage: "checkmark.circle")
            case .unavailable:
                Text("Plans are unavailable right now")
            case .failed:
                Text("We could not complete that purchase")
            }
        }
        .accessibilityElement(children: .combine)
    }
}
```

Keep product choice, price, terms, restore, manage, and error actions accessible from the same state model. Do not let a glass animation be the only evidence that access changed.

## Recipe 15: validate an AI plan proposal against current products

```swift
struct PlanProposal: Sendable, Equatable {
    let productID: String
    let explanation: String
    let catalogReadAt: Date
    let requiresUserReview: Bool
}

func resolve(
    proposal: PlanProposal,
    products: [Product]
) -> Product? {
    guard proposal.requiresUserReview else { return nil }
    return products.first { $0.id == proposal.productID }
}
```

Display the resolved product’s current StoreKit price and term beside the proposal. The model cannot determine offer eligibility, active entitlement, renewal date, or delivery success by itself. The user’s explicit action starts the native purchase route.

## Recipe 16: local StoreKit Test fixture boundary

```swift
import StoreKitTest

struct StoreKitTestPlan {
    let configurationName: String

    func makeSession() throws -> SKTestSession {
        // The .storekit configuration must be a test target resource.
        let session = try SKTestSession(configurationFileNamed: configurationName)
        session.disableDialogs = true
        return session
    }
}
```

Use the documented `SKTestSession` controls to configure renewals, Ask to Buy, interrupted purchases, billing retry, grace period, offers, and failures. Keep local StoreKit receipts/certificates isolated from production validation. This recipe proves a deterministic test environment, not App Store production behavior.

## Recipe 17: test a verification/policy adapter without StoreKit UI

```swift
protocol EntitlementReading: Sendable {
    func currentProductIDs() async -> Set<String>
}

struct FixtureEntitlements: EntitlementReading {
    let productIDs: Set<String>

    func currentProductIDs() async -> Set<String> {
        productIDs
    }
}

func hasProAccess<R: EntitlementReading>(
    using reader: R
) async -> Bool {
    let ids = await reader.currentProductIDs()
    return ids.contains("com.example.app.lifetime")
        || ids.contains("com.example.app.monthly")
        || ids.contains("com.example.app.annual")
}
```

Use fixtures to prove UI state, policy mapping, and fallback behavior. Keep real StoreKit, sandbox, and signed-device tests separate so a fixture cannot be mistaken for a payment or entitlement proof.

## Compile and proof gates

- Confirm product identifiers, types, subscription group, offer configuration, terms/privacy, and storefront data.
- Compile the main app and every target that imports StoreKit APIs.
- Start `Transaction.updates` early and test cancellation/termination cleanup.
- Test verification, delivery, finish ordering, current entitlements, unfinished recovery, and consumable idempotency.
- Test subscription renewal, grace, billing retry, expiry, revoke/refund, price increase, upgrade, downgrade, restore, and manage flows.
- Test offer-code success/failure and introductory/promotional/win-back eligibility in the appropriate environment.
- Test StoreKit configuration and `StoreKitTest` separately from sandbox/TestFlight.
- Inspect signed app configuration and keep server secrets out of the artifact.
- Test VoiceOver, Dynamic Type, reduced transparency/motion, contrast, RTL, and long localized prices.
- Record what the local test, sandbox device, server, and production evidence each actually proves.

## Sources

- [StoreKit](https://developer.apple.com/documentation/storekit)
- [Product](https://developer.apple.com/documentation/storekit/product)
- [Product.products(for:)](https://developer.apple.com/documentation/storekit/product/products%28for%3A%29)
- [ProductView](https://developer.apple.com/documentation/storekit/productview)
- [StoreView](https://developer.apple.com/documentation/storekit/storeview)
- [SubscriptionStoreView](https://developer.apple.com/documentation/storekit/subscriptionstoreview)
- [SubscriptionStoreControlStyle](https://developer.apple.com/documentation/storekit/subscriptionstorecontrolstyle)
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
