# SwiftUI StoreKit 2 commerce and entitlement-review recipes

These are compile-oriented route sketches for a named iOS 26 target. They are not compiled in this documentation workspace and do not prove App Store configuration, storefront availability, account behavior, entitlement delivery, server reconciliation, accessibility task success, or release readiness. Confirm the exact SDK signature and availability in Xcode before copying a sketch.

## Recipe rules

1. Product metadata comes from StoreKit, not a hard-coded price.
2. A direct purchase result is not the same thing as current entitlement.
3. Transaction updates have one long-lived owner.
4. Delivery is idempotent and transaction finish follows delivery.
5. Restore and manage are explicit system destinations.
6. AI explains live facts but cannot invent or execute billing side effects.
7. Liquid Glass groups context and status; it does not hide commercial facts.
8. Local StoreKit testing remains distinct from sandbox, production, and release proof.

## Recipe 1: Product policy and catalog IDs

Keep product IDs, product type, and access policy in one typed place:

~~~swift
import StoreKit

enum AppProduct: String, CaseIterable, Sendable {
    case proMonthly = "com.example.app.pro.monthly"
    case proAnnual = "com.example.app.pro.annual"
    case lifetime = "com.example.app.pro.lifetime"

    var id: String { rawValue }
}

enum AppEntitlement: Hashable, Sendable {
    case pro
}

struct ProductPolicy: Sendable {
    let id: String
    let grants: Set<AppEntitlement>
    let isConsumable: Bool
}

let productPolicies: [String: ProductPolicy] = [
    AppProduct.proMonthly.id: ProductPolicy(
        id: AppProduct.proMonthly.id,
        grants: [.pro],
        isConsumable: false
    ),
    AppProduct.proAnnual.id: ProductPolicy(
        id: AppProduct.proAnnual.id,
        grants: [.pro],
        isConsumable: false
    ),
    AppProduct.lifetime.id: ProductPolicy(
        id: AppProduct.lifetime.id,
        grants: [.pro],
        isConsumable: false
    )
]
~~~

The IDs are examples. Keep the source-of-truth mapping aligned with App Store Connect and the active StoreKit configuration. A model or remote catalog may suggest a product, but the purchase path accepts only IDs that pass this policy.

## Recipe 2: Load a catalog and preserve missing IDs

Do not convert a partial Product response into a full catalog:

~~~swift
struct CatalogSnapshot: Equatable, Sendable {
    let products: [Product]
    let missingIDs: Set<String>
    let revision: Int
}

enum CatalogState: Equatable, Sendable {
    case idle
    case loading(revision: Int)
    case ready(CatalogSnapshot)
    case failed(revision: Int, message: String)
}

func loadCatalog(
    ids: Set<String>,
    revision: Int
) async throws -> CatalogSnapshot {
    let products = try await Product.products(for: ids)
    let returnedIDs = Set(products.map(\.id))
    return CatalogSnapshot(
        products: products,
        missingIDs: ids.subtracting(returnedIDs),
        revision: revision
    )
}
~~~

Sort the returned products with app policy rather than relying on App Store response order. Render Product display name, display price, subscription period, and offer facts from the returned value.

## Recipe 3: Native StoreKit view in a SwiftUI shell

Use native StoreKit views when their layout and semantics fit:

~~~swift
import SwiftUI
import StoreKit

struct SubscriptionEntryView: View {
    private let subscriptionIDs = [
        AppProduct.proMonthly.id,
        AppProduct.proAnnual.id
    ]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Choose the plan that fits your workflow")
                    .font(.title2.weight(.semibold))

                Text("Compare the live App Store prices and renewal terms below.")
                    .foregroundStyle(.secondary)

                SubscriptionStoreView(productIDs: subscriptionIDs) {
                    Text("Pro access")
                }

                Text("Restore purchases from the utility menu if access is missing.")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }
            .padding()
        }
    }
}
~~~

Confirm the initializer, control style, target availability, and surrounding modifiers against the selected SDK. The app owns the benefit explanation and status context; StoreKit owns localized product information and the purchase confirmation flow.

## Recipe 4: Direct purchase with every result case

Use a direct Product purchase only when a custom purchase action is needed:

~~~swift
enum PurchaseOutcome: Sendable {
    case pending
    case cancelled
    case verified(Transaction)
    case unverified(Transaction, String)
}

enum PurchaseError: Error {
    case unknownResult
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
            return .unverified(transaction, error.localizedDescription)
        }
    @unknown default:
        throw PurchaseError.unknownResult
    }
}
~~~

After verified, call the same delivery/entitlement coordinator used by Transaction.updates. Do not immediately show an unlocked feature before the policy/delivery boundary has completed.

## Recipe 5: One transaction-update coordinator

The listener should start early and be cancelled with its owner:

~~~swift
actor TransactionUpdateCoordinator {
    enum Source: Sendable {
        case directPurchase
        case updates
        case unfinished
    }

    private var listener: Task<Void, Never>?

    func start() {
        listener?.cancel()
        listener = Task { [weak self] in
            for await result in Transaction.updates {
                guard let self else { return }
                await process(result, source: .updates)
            }
        }
    }

    func stop() {
        listener?.cancel()
        listener = nil
    }

    func process(
        _ result: VerificationResult<Transaction>,
        source: Source
    ) async {
        guard case .verified(let transaction) = result else {
            // Keep unverified handling explicit for the product policy.
            return
        }

        // 1. Match transaction.productID to ProductPolicy.
        // 2. Apply idempotent delivery or entitlement projection.
        // 3. Publish the resulting access state.
        // 4. Finish only after delivery is safe.
        _ = transaction
        _ = source
    }
}
~~~

The exact actor ownership depends on persistence and server design. The invariant is that the paywall does not create a fresh listener every time SwiftUI recomposes.

## Recipe 6: Recompute current entitlements

Use currentEntitlements for the latest transactions that currently provide access:

~~~swift
struct EntitlementState: Equatable, Sendable {
    let productIDs: Set<String>
    let evaluatedAt: Date
    let verifiedCount: Int
}

func currentEntitlementState() async -> EntitlementState {
    var productIDs = Set<String>()
    var verifiedCount = 0

    for await result in Transaction.currentEntitlements {
        guard case .verified(let transaction) = result else { continue }
        productIDs.insert(transaction.productID)
        verifiedCount += 1
    }

    return EntitlementState(
        productIDs: productIDs,
        evaluatedAt: .now,
        verifiedCount: verifiedCount
    )
}
~~~

For an active subscription, inspect subscription status and renewal information when the UI needs billing retry, grace, expiration, revocation, or renewal context. Do not use currentEntitlements as a consumable balance.

## Recipe 7: Recover unfinished transactions

Recover unfinished transactions through the same coordinator:

~~~swift
func recoverUnfinished(
    using coordinator: TransactionUpdateCoordinator
) async {
    for await result in Transaction.unfinished {
        await coordinator.process(result, source: .unfinished)
    }
}
~~~

Call recovery at a deliberate lifecycle boundary, commonly app/feature startup. The delivery ledger must tolerate a process termination between delivery and finish. A transaction that is finished too early can be difficult to recover; a transaction that is never finished can be emitted again.

## Recipe 8: Restore with AppStore.sync and refresh

Restore is a user-triggered action:

~~~swift
@MainActor
final class RestoreModel: ObservableObject {
    enum State: Equatable {
        case idle
        case syncing
        case complete
        case failed(String)
    }

    @Published private(set) var state: State = .idle
    private var task: Task<Void, Never>?

    func restore(refresh: @escaping @Sendable () async -> Void) {
        task?.cancel()
        state = .syncing
        task = Task { @MainActor in
            do {
                try await AppStore.sync()
                await refresh()
                state = .complete
            } catch is CancellationError {
                state = .idle
            } catch {
                state = .failed(error.localizedDescription)
            }
        }
    }
}
~~~

Do not set premium to true when sync returns. Read verified entitlements again and show the result. The exact AppStore availability and error cases must be checked in the target SDK.

## Recipe 9: Manage subscriptions from SwiftUI

Keep the system management surface explicit:

~~~swift
struct CurrentPlanView: View {
    @State private var showManage = false

    var body: some View {
        VStack(spacing: 12) {
            Text("Current plan")
            Button("Manage subscription") {
                showManage = true
            }
        }
        .manageSubscriptionsSheet(isPresented: $showManage)
    }
}
~~~

Gate the modifier and provide a fallback for unsupported targets. The app should explain that cancellation and plan changes occur in the Apple Account/App Store management surface, not through a local toggle.

## Recipe 10: Restore and manage buttons around a StoreKit view

StoreKit views can expose auxiliary actions through documented modifiers:

~~~swift
SubscriptionStoreView(productIDs: [
    AppProduct.proMonthly.id,
    AppProduct.proAnnual.id
]) {
    Text("Pro")
}
.storeButton(.visible, for: .restorePurchases)
.manageSubscriptionsSheet(isPresented: $showManage)
~~~

Confirm the exact button kind and modifier availability in the target SDK. Keep restore discoverable but do not add duplicate buttons that compete with the native control. Use a settings/account route for manage if the paywall is intentionally minimal.

## Recipe 11: Subscription status projection

Map renewal status into UI-specific state without losing the underlying evidence:

~~~swift
enum SubscriptionUIState: Equatable, Sendable {
    case unknown
    case active(productID: String)
    case grace(productID: String)
    case billingRetry(productID: String)
    case expired(productID: String?)
    case revoked(productID: String?)
    case unavailable(String)
}

func project(
    status: Product.SubscriptionInfo.Status,
    productID: String
) -> SubscriptionUIState {
    switch status.state {
    case .subscribed:
        return .active(productID: productID)
    case .inGracePeriod:
        return .grace(productID: productID)
    case .inBillingRetryPeriod:
        return .billingRetry(productID: productID)
    case .expired:
        return .expired(productID: productID)
    case .revoked:
        return .revoked(productID: productID)
    default:
        return .unavailable("Unknown subscription state")
    }
}
~~~

The exact enum cases and accessors are SDK-sensitive. Keep the source status, transaction, and renewal info available for support and policy; the UI projection is not a substitute for them.

## Recipe 12: Typed AI plan explanation

Pass only normalized live facts and validate the returned candidate:

~~~swift
struct PlanContext: Codable, Sendable {
    let revision: Int
    let currentProductID: String?
    let plans: [Plan]

    struct Plan: Codable, Sendable {
        let productID: String
        let name: String
        let displayPrice: String
        let term: String?
        let includedBehavior: [String]
    }
}

struct PlanProposal: Codable, Sendable {
    let revision: Int
    let productID: String
    let explanation: String
}

func validate(
    _ proposal: PlanProposal,
    against context: PlanContext
) -> PlanContext.Plan? {
    guard proposal.revision == context.revision else { return nil }
    return context.plans.first { $0.productID == proposal.productID }
}
~~~

If validation succeeds, display the live Product price and term next to the explanation. If it fails, show the ordinary deterministic comparison. The proposal cannot call Product.purchase, AppStore.sync, manageSubscriptionsSheet, or change entitlement state.

## Recipe 13: Glass shell with a legible fallback

Bound visual treatment to a functional group:

~~~swift
struct GlassCommerceShell<Content: View>: View {
    @ViewBuilder let content: () -> Content

    var body: some View {
        content()
            .padding()
            .background {
                RoundedRectangle(cornerRadius: 28)
                    .fill(.thinMaterial)
            }
            .glassEffect(in: .rect(cornerRadius: 28))
    }
}
~~~

Treat the glassEffect call as a target-SDK route sketch. Test an opaque/system-material fallback when Liquid Glass is unavailable or reduced transparency is enabled. Keep price, term, offer, selected state, and legal text semantically readable without the effect.

## Recipe 14: Preview fixtures for commerce states

Inject the catalog and entitlement state instead of relying on a live App Store in previews:

~~~swift
struct CommerceFixture {
    static let plan = PlanFixture(
        id: AppProduct.proMonthly.id,
        name: "Pro Monthly",
        price: "$4.99",
        term: "per month"
    )

    static let states: [PurchaseState] = [
        .ready,
        .purchasing(productID: plan.id),
        .pending(productID: plan.id),
        .cancelled,
        .verifiedAwaitingDelivery(productID: plan.id),
        .unverified(productID: plan.id),
        .failed(message: "StoreKit unavailable")
    ]
}
~~~

Add fixtures for active, grace, billing retry, expired, revoked, missing product, model unavailable, stale proposal, and reduced-transparency layout. Previews prove state rendering only.

## Recipe 15: Acceptance checklist for a named target

Record the following before calling the route ready:

~~~text
target and scheme: ______________________
bundle ID: ______________________________
SDK/deployment target: ___________________
StoreKit environment: local | sandbox | production
configuration/product revision: ___________
account/server boundary: _________________

[ ] product metadata is live/localized
[ ] missing product is visible
[ ] native product/subscription surface works
[ ] direct purchase cases are mapped
[ ] Transaction.updates starts once
[ ] unfinished recovery works
[ ] currentEntitlements drives access
[ ] delivery/finish boundary is tested
[ ] restore refreshes entitlements
[ ] manage route/fallback is tested
[ ] offers and renewal states are honest
[ ] AI proposal is source-linked and side-effect free
[ ] Liquid Glass fallback is legible
[ ] VoiceOver/Dynamic Type/contrast/motion/RTL/input pass
[ ] archive and signed environment are inspected
~~~

## Sources

- [StoreKit](https://developer.apple.com/documentation/storekit)
- [StoreKit views](https://developer.apple.com/documentation/storekit/storekit-views)
- [Getting started with In-App Purchase using StoreKit views](https://developer.apple.com/documentation/storekit/getting-started-with-in-app-purchases-using-storekit-views?changes=_9)
- [Product](https://developer.apple.com/documentation/storekit/product)
- [Product.products(for:)](https://developer.apple.com/documentation/storekit/product/products%28for%3A%29)
- [ProductView](https://developer.apple.com/documentation/storekit/productview)
- [StoreView](https://developer.apple.com/documentation/storekit/storeview)
- [SubscriptionStoreView](https://developer.apple.com/documentation/storekit/subscriptionstoreview)
- [Product.purchase(options:)](https://developer.apple.com/documentation/storekit/product/purchase%28options%3A%29)
- [Product.PurchaseResult](https://developer.apple.com/documentation/storekit/product/purchaseresult)
- [Transaction](https://developer.apple.com/documentation/storekit/transaction)
- [Transaction.currentEntitlements](https://developer.apple.com/documentation/storekit/transaction/currententitlements)
- [Transaction.updates](https://developer.apple.com/documentation/storekit/transaction/updates)
- [Transaction.unfinished](https://developer.apple.com/documentation/storekit/transaction/unfinished)
- [Product.SubscriptionInfo](https://developer.apple.com/documentation/storekit/product/subscriptioninfo)
- [Product.SubscriptionInfo.Status](https://developer.apple.com/documentation/storekit/product/subscriptioninfo/status)
- [Product.SubscriptionInfo.RenewalState](https://developer.apple.com/documentation/storekit/product/subscriptioninfo/renewalstate)
- [AppStore.sync()](https://developer.apple.com/documentation/storekit/appstore/sync%28%29)
- [manageSubscriptionsSheet(isPresented:)](https://developer.apple.com/documentation/swiftui/view/managesubscriptionssheet%28ispresented%3A%29)
- [storeButton(_:for:)](https://developer.apple.com/documentation/swiftui/view/storebutton%28_%3Afor%3A%29?changes=__1)
- [Setting up StoreKit Testing in Xcode](https://developer.apple.com/documentation/xcode/setting-up-storekit-testing-in-xcode)
- [Testing In-App Purchases in Xcode](https://developer.apple.com/documentation/storekit/testing-in-app-purchases-in-xcode)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
