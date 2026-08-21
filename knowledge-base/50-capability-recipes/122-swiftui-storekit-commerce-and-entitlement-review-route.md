# SwiftUI StoreKit 2 commerce and entitlement-review route

Use this route when a SwiftUI app needs a native StoreKit 2 purchase surface, a custom plan comparison, an entitlement-aware feature lock, or a subscription-management screen. It is intentionally separate from the older [StoreKit 2 purchase, subscription, and entitlement capability route](92-storekit2-purchase-and-entitlement-route.md): this route is the screen-level orchestration contract for SwiftUI, StoreKit views, Liquid Glass, on-device explanation, and reviewable side effects.

## Route contract

~~~text
catalog configuration
  -> SwiftUI product/loading projection
  -> benefit and plan context
  -> native StoreKit view or explicit purchase action
  -> verification/delivery
  -> entitlement snapshot
  -> feature access or management destination
~~~

The route must answer:

| Question | Required answer |
| --- | --- |
| Which product IDs are allowed? | A typed app-owned catalog aligned with App Store Connect/StoreKit configuration. |
| Who loads products? | One catalog owner or a view task with explicit cancellation and missing-product state. |
| Who listens for transaction updates? | One long-lived StoreKit coordinator/actor, not every paywall appearance. |
| Who grants access? | A verified transaction and product-specific delivery/entitlement policy. |
| Who handles restore/manage? | Explicit user actions to StoreKit/App Store system routes. |
| Who explains plans? | Deterministic Product metadata plus app-owned benefit copy; AI is optional and reviewable. |
| Who owns side effects? | The person and the native StoreKit/system confirmation surface. |

## State machine

Keep catalog, purchase, entitlement, and presentation state distinct:

~~~text
Catalog
  idle -> loading -> ready(products, revision)
                   -> partial(missingIDs)
                   -> unavailable(error)

Paywall
  hidden -> presenting -> visible
                      -> dismissing

Purchase
  ready -> purchasing -> pending
                     -> cancelled
                     -> success(unverified)
                     -> success(verified)
                     -> failed(error)

Delivery
  notStarted -> validating -> delivering
                           -> delivered
                           -> retryableFailure
                           -> rejected

Entitlement
  unknown -> evaluating -> active
                       -> inactive
                       -> grace
                       -> billingRetry
                       -> expired
                       -> revoked
                       -> failed

Recovery
  idle -> syncing -> refreshed | failed

AI explanation
  unavailable | preparing | proposed(revision) | stale | rejected | accepted
~~~

Do not collapse pending, cancelled, unverified, failed, expired, and revoked into one error state. Each one has a different user action and a different accounting meaning.

## 1. Define the typed catalog

Use a small app-owned policy layer:

~~~swift
enum StoreProductID: String, CaseIterable, Sendable {
    case monthly = "com.example.app.pro.monthly"
    case annual = "com.example.app.pro.annual"
    case lifetime = "com.example.app.pro.lifetime"

    var rawID: String { rawValue }
}

struct StoreProductPolicy: Sendable {
    let id: String
    let grants: Set<EntitlementKey>
    let consumable: Bool
}

enum EntitlementKey: Hashable, Sendable {
    case pro
}
~~~

These IDs are placeholders. In a named app target, the values must match App Store Connect and the active StoreKit configuration. A model, remote response, or user-entered string must not add an arbitrary product to the purchase path.

## 2. Choose native or custom merchandising

Use a simple decision:

| Need | Route |
| --- | --- |
| One product with normal StoreKit presentation | ProductView. |
| Collection of one-time products | StoreView. |
| Subscription group with native selection | SubscriptionStoreView. |
| Custom comparison/education | Load Product values, render app-owned layout, use documented purchase action or StoreKit views within it. |
| Existing subscriber | Entitlement/status card plus manageSubscriptionsSheet and restore. |

The app-owned route must retain the same localized product, price, offer, verification, and entitlement rules. Custom styling is not permission to replace StoreKit’s system confirmation or invent a local price.

## 3. Load products with explicit revision

Store product loading is a cancellable catalog operation:

~~~swift
struct StoreCatalog: Equatable, Sendable {
    let products: [Product]
    let missingIDs: Set<String>
    let revision: Int
}

@MainActor
final class StoreCatalogModel: ObservableObject {
    @Published private(set) var state: CatalogState = .idle
    private var task: Task<Void, Never>?
    private var revision = 0

    func load(ids: Set<String>) {
        task?.cancel()
        revision += 1
        let currentRevision = revision
        state = .loading(currentRevision)
        task = Task { [weak self] in
            do {
                let products = try await Product.products(for: ids)
                try Task.checkCancellation()
                guard let self, self.revision == currentRevision else { return }
                let returned = Set(products.map(\.id))
                state = .ready(StoreCatalog(
                    products: products,
                    missingIDs: ids.subtracting(returned),
                    revision: currentRevision
                ))
            } catch is CancellationError {
                // Expected when the catalog input changes.
            } catch {
                guard let self, self.revision == currentRevision else { return }
                state = .failed(currentRevision, error)
            }
        }
    }
}
~~~

The route sketch uses Product and CatalogState without defining every enum case. Compile it in the named target and preserve the semantic contract: a newer ID set must win, missing IDs are visible, and errors do not silently become an empty catalog.

## 4. Give transaction updates one owner

Start Transaction.updates at app or feature-coordinator startup and cancel it with the owner’s lifecycle. Route updates, unfinished transactions, and direct purchase results through the same verification and delivery function.

~~~swift
actor StoreTransactionCoordinator {
    private var updateTask: Task<Void, Never>?

    func start() {
        updateTask?.cancel()
        updateTask = Task { [weak self] in
            for await result in Transaction.updates {
                guard let self else { return }
                await self.process(result, source: .updates)
            }
        }
    }

    func stop() {
        updateTask?.cancel()
        updateTask = nil
    }

    private func process(
        _ result: VerificationResult<Transaction>,
        source: TransactionSource
    ) async {
        // Verify, apply product policy, deliver idempotently, publish access,
        // and finish only after delivery is safe.
    }
}
~~~

The exact actor isolation, initialization, and finish policy depend on the app’s persistence and server boundary. Do not create one update task per product row or paywall instance.

## 5. Use current entitlements as an input to access

Rebuild entitlement state on launch, foreground return, restore completion, and relevant transaction updates:

~~~swift
struct EntitlementSnapshot: Equatable, Sendable {
    let activeProductIDs: Set<String>
    let evaluatedAt: Date
    let source: EntitlementSource
}

func readCurrentEntitlements() async -> Set<String> {
    var productIDs = Set<String>()
    for await result in Transaction.currentEntitlements {
        guard case .verified(let transaction) = result else { continue }
        productIDs.insert(transaction.productID)
    }
    return productIDs
}
~~~

For consumables, currentEntitlements is not a balance. Use a durable delivery ledger or server authority appropriate to the product. For subscriptions, also inspect Product.SubscriptionInfo.Status and RenewalInfo when the UI needs grace, billing retry, expiration, revocation, or plan-change context.

## 6. Model direct purchase results

Keep purchase state separate from entitlement state:

~~~swift
enum PurchaseState: Equatable, Sendable {
    case ready
    case purchasing(productID: String)
    case pending(productID: String)
    case cancelled
    case verifiedAwaitingDelivery(productID: String)
    case unverified(productID: String)
    case failed(message: String)
}

@MainActor
func purchase(_ product: Product) async {
    purchaseState = .purchasing(productID: product.id)
    do {
        switch try await product.purchase() {
        case .pending:
            purchaseState = .pending(productID: product.id)
        case .userCancelled:
            purchaseState = .cancelled
        case .success(let verification):
            switch verification {
            case .verified(let transaction):
                purchaseState = .verifiedAwaitingDelivery(productID: transaction.productID)
                await coordinator.process(verification, source: .directPurchase)
            case .unverified(let transaction, _):
                purchaseState = .unverified(productID: transaction.productID)
            }
        @unknown default:
            purchaseState = .failed(message: "Unknown purchase result")
        }
    } catch {
        purchaseState = .failed(message: error.localizedDescription)
    }
}
~~~

If the product is shown inside a StoreKit view, use its purchase action and completion modifiers according to the selected SDK instead of starting a second direct purchase path. A single button should have one purchase owner.

## 7. Compose the SwiftUI shell

A screen-level shell can keep app-owned context around a native StoreKit surface:

~~~swift
struct PurchaseReviewScreen: View {
    @State private var showManage = false
    @StateObject private var model = PurchaseReviewModel()

    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                BenefitHeader(model: model)
                CatalogStateView(model: model)
                EntitlementStatusView(snapshot: model.entitlement)
                RestoreAndManageRow(
                    restore: { model.restore() },
                    manage: { showManage = true }
                )
            }
            .padding()
        }
        .task { await model.loadAndRefresh() }
        .manageSubscriptionsSheet(isPresented: $showManage)
    }
}
~~~

The native surface can be inserted in CatalogStateView as ProductView, StoreView, or SubscriptionStoreView. Keep the state projection around it so a missing product, pending purchase, or entitlement failure does not disappear inside a generic progress indicator.

## 8. Add restore and manage destinations

Restore is explicit and asynchronous:

~~~swift
func restore() {
    restoreTask?.cancel()
    restoreState = .syncing
    restoreTask = Task { @MainActor in
        do {
            try await AppStore.sync()
            await refreshEntitlements()
            restoreState = .complete
        } catch is CancellationError {
            restoreState = .cancelled
        } catch {
            restoreState = .failed(error.localizedDescription)
        }
    }
}
~~~

The exact availability and error behavior must be checked in the selected SDK. The important boundary is that a restore action synchronizes and then re-evaluates verified access; it does not set a local premium flag.

Show manageSubscriptionsSheet when the user asks to manage a subscription. If the target cannot present it, preserve a clear fallback and explain that cancellation/plan changes are controlled by the App Store account surface.

## 9. Add on-device AI without billing authority

The AI route receives only the minimum normalized facts:

~~~swift
struct PlanExplanationContext: Codable, Sendable {
    let catalogRevision: Int
    let candidates: [Candidate]
    let currentEntitlement: String?

    struct Candidate: Codable, Sendable {
        let productID: String
        let displayName: String
        let displayPrice: String
        let billingTerm: String?
        let benefitSummary: String
    }
}

struct PlanProposal: Codable, Sendable {
    let productID: String
    let reasons: [String]
    let catalogRevision: Int
}
~~~

After inference, validate productID against the current catalog revision and replace any model-written price or term with live Product values. The proposal can change which plan is highlighted; it cannot call purchase, AppStore.sync, manageSubscriptionsSheet, or an entitlement mutation. The person must choose and then pass through the native StoreKit action.

## 10. Add the Liquid Glass shell

Use a bounded functional group:

~~~swift
VStack(spacing: 12) {
    BenefitHeader(model: model)
    StoreKitCatalogSurface(model: model)
    PurchaseStatusView(state: model.purchaseState)
    PurchaseUtilityActions(model: model)
}
.padding()
.glassEffect(in: .rect(cornerRadius: 28))
~~~

The exact modifier and availability must be checked in the target SDK. If the glass effect is unavailable or disabled for accessibility, use a system material or opaque background with the same semantic grouping. Do not make a transparent glass layer the only contrast boundary for localized price or legal text.

## 11. Verification fixtures

Use a deterministic fixture catalog and entitlement snapshot for previews and UI tests:

~~~swift
struct StoreFixture {
    static let monthly = ProductFixture(
        id: "com.example.app.pro.monthly",
        displayName: "Pro Monthly",
        displayPrice: "$4.99",
        term: "per month"
    )

    static let pending = PurchaseState.pending(
        productID: monthly.id
    )

    static let active = EntitlementSnapshot(
        activeProductIDs: [monthly.id],
        evaluatedAt: .now,
        source: .fixture
    )
}
~~~

The fixture proves UI state projection only. Use StoreKit Testing in Xcode for transaction behavior, sandbox/TestFlight for signed account behavior, and physical/release evidence for production gates.

## 12. Stop conditions

Pause before implementation if:

- the product IDs or product types are not agreed;
- App Store Connect/StoreKit configuration metadata is missing;
- the app cannot decide whether local or server entitlement is authoritative;
- a custom paywall would hide or replace the native confirmation/management path;
- a model is being asked to invent prices, eligibility, or access;
- restore, pending, unverified, revoked, or billing retry has no UI state;
- a local StoreKit test is being presented as production billing evidence.

## Sources

- [StoreKit](https://developer.apple.com/documentation/storekit)
- [StoreKit views](https://developer.apple.com/documentation/storekit/storekit-views)
- [Getting started with In-App Purchase using StoreKit views](https://developer.apple.com/documentation/storekit/getting-started-with-in-app-purchases-using-storekit-views?changes=_9)
- [Product](https://developer.apple.com/documentation/storekit/product)
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
- [manageSubscriptionsSheet(isPresented:)](https://developer.apple.com/documentation/swiftui/view/managesubscriptionssheet%28ispresented%3A%29)
- [storeButton(_:for:)](https://developer.apple.com/documentation/swiftui/view/storebutton%28_%3Afor%3A%29?changes=__1)
- [Setting up StoreKit Testing in Xcode](https://developer.apple.com/documentation/xcode/setting-up-storekit-testing-in-xcode)
- [Testing In-App Purchases in Xcode](https://developer.apple.com/documentation/storekit/testing-in-app-purchases-in-xcode)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
