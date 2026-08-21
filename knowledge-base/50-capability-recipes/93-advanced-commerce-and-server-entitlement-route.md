# Advanced Commerce and server entitlement capability route

This route is a capability blueprint for an app that owns a large SKU catalog while Apple owns payment processing and signed transaction evidence. It is not a claim that Advanced Commerce access, server configuration, or App Review approval exists for a target.

## Route identity

~~~text
catalog SKU -> current storefront/account validation -> signed request
  -> AdvancedCommerceProduct purchase -> StoreKit result
  -> Apple-signed transaction -> server notification/history/status
  -> idempotent delivery -> entitlement projection -> native UI
~~~

The route has three authorities:

| Authority | Owns | Does not own |
| --- | --- | --- |
| App UI | Intent, explanation, user review, accessibility, local state | Prices invented by the client, signing keys, final entitlement truth. |
| App/server catalog | SKU identity, content metadata, allowed operations, account mapping | Apple’s payment confirmation or signed Apple transaction. |
| App Store/StoreKit | Payment confirmation, transaction and renewal JWS evidence | The app’s private content delivery policy or local UI. |

## Choose the route

Use Advanced Commerce only after the product requirement passes this gate:

- The app’s core model needs an exceptionally large catalog or optional subscription add-ons.
- The app can apply for and receive per-app access.
- The app can manage generic product IDs and individual SKUs in its own system.
- The app can use StoreKit 2 in the target platform.
- The app can provide subscription management and a refund request path.
- The server can sign app requests and authorize App Store Server API calls without exposing keys to the client.
- The server can receive, verify, acknowledge, deduplicate, and recover App Store Server Notifications V2.
- The team accepts current limitations, including no Xcode StoreKit Testing for purchases handled by Advanced Commerce.

If these conditions are not met, use ordinary StoreKit 2, a non-commerce local feature, or a documented alternative route. Do not build an Advanced Commerce-shaped UI and call it ready before access and server evidence exist.

## Setup route

### App Store Connect and Apple access

1. Confirm the business model matches Apple’s current eligibility guidance.
2. Request Advanced Commerce access for the app.
3. Create the required generic one-time/subscription identifiers in App Store Connect.
4. Submit those generic identifiers in the access form.
5. Configure the subscription group and do not enable Family Sharing for the generic subscription ID if the current Apple setup guide says not to.
6. Supply supported availability, placeholder localization, and base pricing as documented.
7. Configure the optional payment-sheet image for the generic product category.
8. Provide the in-app subscription-management deep link requested by Apple.

### Server prerequisites

1. Terminate TLS 1.2 or later.
2. Store App Store Connect API key material in a secret manager or secure server environment.
3. Implement JWT generation for App Store Server API and Advanced Commerce server endpoints.
4. Implement JWS generation for Advanced Commerce in-app request signing.
5. Implement App Store Server Notifications V2 production and sandbox endpoints.
6. Implement JWS verification and bundle/environment validation.
7. Implement idempotent transaction, notification, and delivery records.
8. Implement history pagination and current subscription-status reconciliation.
9. Add a test-notification route and operational logs that omit raw secrets/JWS values.

### App prerequisites

1. Load the signed-in account/session context without embedding Apple API secrets.
2. Fetch a typed catalog entry for the selected SKU and storefront.
3. Display the current validated metadata and side effects.
4. Request a server-generated Advanced Commerce request artifact.
5. Construct AdvancedCommerceProduct with the generic product ID.
6. Call the documented purchase method with the compact JWS and options.
7. Preserve every Product.PurchaseResult case.
8. Route verified results through delivery and entitlement policy.
9. Observe current entitlements and server refresh on launch/foreground/account changes.
10. Provide manage, refund, restore/recovery, and support paths.

## Data contracts

The following models are route sketches. Confirm fields, serialization, and API availability in the selected SDK and server library.

### Catalog entry

~~~swift
struct AdvancedCatalogEntry: Codable, Identifiable, Sendable, Equatable {
    let id: String                 // app-owned SKU
    let genericProductID: String
    let displayName: String
    let description: String
    let priceMinorUnits: Int64
    let currencyCode: String
    let periodDescription: String?
    let taxCode: String
    let storefront: String
    let catalogRevision: String
    let availability: Availability
    let entitlementKey: String

    enum Availability: String, Codable, Sendable {
        case available
        case owned
        case active
        case pending
        case unavailable
    }
}
~~~

Keep the server’s price representation separate from StoreKit’s localized display values. The UI should use localized provider-facing values where Apple supplies them and never build a final confirmation price by hand. The app-owned card may show server catalog data, but the server must validate it again before signing.

### Typed purchase intent

~~~swift
struct AdvancedPurchaseIntent: Codable, Sendable, Equatable {
    let sku: String
    let genericProductID: String
    let catalogRevision: String
    let accountID: String
    let storefront: String
    let requestReferenceID: UUID
    let operation: Operation

    enum Operation: String, Codable, Sendable {
        case oneTimeChargeCreate
        case subscriptionCreate
        case subscriptionModifyInApp
        case subscriptionReactivateInApp
    }
}
~~~

The client sends intent, not an arbitrary signed payload. The server re-reads the authoritative SKU record, verifies account/session authorization, checks storefront and availability, calculates the exact request body, and signs only an allowed operation.

### Server response envelope

~~~swift
struct AdvancedCommerceRequestEnvelope: Decodable, Sendable {
    let requestReferenceID: UUID
    let genericProductID: String
    let compactJWS: String
    let catalogRevision: String
    let expiresAt: Date
}
~~~

Treat the compact JWS as opaque. The app should not parse it to make entitlement decisions. It can validate the envelope’s request reference, generic product ID, expiration, and account/session association before passing it to StoreKit.

### Entitlement projection

~~~swift
struct EntitlementProjection: Codable, Sendable, Equatable {
    let accountID: String
    let sku: String
    let status: Status
    let sourceTransactionID: String?
    let originalTransactionID: String?
    let environment: String
    let lastVerifiedAt: Date
    let deliveryState: DeliveryState

    enum Status: String, Codable, Sendable {
        case active
        case gracePeriod
        case billingRetry
        case pending
        case expired
        case revoked
        case unknown
    }

    enum DeliveryState: String, Codable, Sendable {
        case notRequired
        case queued
        case delivered
        case retryableFailure
        case blockedUntilReview
    }
}
~~~

The projection is app-owned policy. It is built from Apple evidence and delivery records; it is not a replacement for the signed source records.

## App-side route

### Load a generic product

~~~swift
import StoreKit

@MainActor
func loadAdvancedProduct(
    genericProductID: AdvancedCommerceProduct.ID
) async throws -> AdvancedCommerceProduct {
    try await AdvancedCommerceProduct(id: genericProductID)
}
~~~

Do not use Product.products(for:) as if the app-owned SKU were an ordinary App Store product ID. The documented Advanced Commerce path starts from AdvancedCommerceProduct and a generic product ID. Confirm the exact ID type and availability for the selected SDK.

### Request signed operation data

~~~swift
protocol AdvancedCommerceSigningClient: Sendable {
    func makeRequest(
        for intent: AdvancedPurchaseIntent
    ) async throws -> AdvancedCommerceRequestEnvelope
}
~~~

The implementation should call the app’s authenticated server endpoint over a secure connection. The server should reject stale revisions, mismatched generic IDs, unsupported operations, unauthorized accounts, invalid storefronts, and duplicate request reference IDs according to policy.

### Purchase through StoreKit

~~~swift
import StoreKit

@MainActor
func purchaseAdvancedItem(
    product: AdvancedCommerceProduct,
    request: AdvancedCommerceRequestEnvelope
) async -> Product.PurchaseResult? {
    do {
        return try await product.purchase(
            compactJWS: request.compactJWS,
            options: []
        )
    } catch {
        return nil
    }
}
~~~

AdvancedCommerceProduct.PurchaseResult is a type alias for Product.PurchaseResult. Preserve the complete result mapping in the caller; this helper intentionally does not convert a thrown error or verification result into access.

### Preserve purchase outcomes

~~~swift
enum AdvancedPurchaseState: Sendable, Equatable {
    case idle
    case preparing
    case systemConfirmation
    case pending
    case cancelled
    case verified(transactionID: UInt64)
    case unverified
    case failed
}

func mapPurchaseResult(
    _ result: Product.PurchaseResult
) -> AdvancedPurchaseState {
    switch result {
    case .pending:
        return .pending
    case .userCancelled:
        return .cancelled
    case .success(let verification):
        switch verification {
        case .verified(let transaction):
            return .verified(transactionID: transaction.id)
        case .unverified:
            return .unverified
        }
    @unknown default:
        return .failed
    }
}
~~~

The exact SDK signature and availability must be compiled in a real target. A verified transaction still needs delivery and account reconciliation; the app should not mark the SKU active solely from this mapping.

## Sending request data through the Product option route

Apple also documents an app-side route in which the signed Advanced Commerce request is wrapped as advancedCommerceRequestData and passed through Product.PurchaseOption.custom(key:value:). Use this route only for the request types and SDK form that Apple’s current documentation supports. The key is exactly advancedCommerceData.

~~~swift
import StoreKit

func requestDataOption(
    advancedCommerceRequestData: Data
) -> Product.PurchaseOption {
    .custom(
        key: "advancedCommerceData",
        value: advancedCommerceRequestData
    )
}
~~~

This is not the same as putting an Apple private key in the app. The Data value is the signed operation artifact. The server still creates the request JSON, base64-encodes it, signs the JWS, and securely sends the wrapped data to the app.

## Current entitlements and background updates

~~~swift
import StoreKit

@MainActor
func readAdvancedEntitlements(
    for product: AdvancedCommerceProduct
) async -> [UInt64] {
    var transactionIDs: [UInt64] = []

    for await verification in product.currentEntitlements {
        if case .verified(let transaction) = verification {
            transactionIDs.append(transaction.id)
        }
    }

    return transactionIDs
}
~~~

Use a long-lived Transaction.updates task for purchase changes made outside the current call or on another device. For Advanced Commerce, also implement server notification and history/status recovery; local sequences are not a complete server ledger.

## Server JWT and JWS boundaries

~~~text
App Store Connect private key
  -> server-only JWT for App Store Server API / Advanced Commerce web endpoints
  -> server-only JWS for Advanced Commerce in-app request
  -> short-lived signed artifact to app
  -> StoreKit purchase
~~~

Generate tokens on the server. Apple documents an ES256 JWT with kid, iss, iat, exp, aud: appstoreconnect-v1, and bid for App Store Server API authorization. For an Advanced Commerce in-app request, Apple documents a JWS with aud: advanced-commerce-api, a nonce, bundle ID, and a request claim containing base64-encoded request data. Never reuse an API JWT as an in-app purchase JWS.

The server signing endpoint should be typed and narrow:

~~~text
POST /commerce/advanced/request
body: AdvancedPurchaseIntent
checks: authenticated account, SKU, revision, storefront, operation,
        subscription status, duplicate request, catalog availability
returns: AdvancedCommerceRequestEnvelope
~~~

Do not expose sign(payload: String) or an endpoint that accepts arbitrary JSON from the client. The server must build the payload from its own catalog and policy.

## App Store Server Notification V2 route

~~~text
POST /apple/app-store-server/notifications
  -> accept only HTTPS/TLS 1.2+
  -> parse responseBodyV2.signedPayload
  -> verify outer JWS
  -> verify nested signedTransactionInfo/signedRenewalInfo
  -> validate bundle ID/environment
  -> dedupe notificationUUID
  -> apply newest valid signedDate policy
  -> enqueue idempotent ledger/projection work
  -> respond 200-206 after accepted processing
~~~

Return a retryable 4xx/5xx for transient failure. Do not return success before the server has durably accepted the event if the operational design depends on the event. Apple documents V2 retries in production and the test-notification endpoint; use those routes to prove the endpoint.

Use notificationType and subtype as event hints, not as the entire entitlement model. A current status query or transaction history reconciliation should be able to repair a delayed/out-of-order/missed event.

## Transaction history reconciliation

~~~text
GET /inApps/v2/history/{anyTransactionId}
  -> verify HistoryResponse
  -> persist signedTransactions
  -> if hasMore, repeat with same filters + revision
  -> derive current app-owned SKU projections
  -> store final revision for incremental reconciliation
~~~

Use the production or sandbox base URL that matches the transaction environment. Apple documents up to 20 transactions per history response and requires the same query parameters when following revision. The history can include refunded, revoked, and finished transactions, so it is evidence for rebuilding state—not a direct “active” flag.

For a current subscription view, call Get All Subscription Statuses and map the returned group/status data into the app-owned projection. If notification data disagrees with current status, record the disagreement, favor the latest verified provider state according to policy, and expose a support-safe refresh state rather than silently showing false access.

## Delivery and idempotency

Use an operation key such as:

~~~text
deliveryKey = appID + environment + transactionID + sku + entitlementVersion
~~~

The server should allow repeated notification, history, app retry, and foreground-refresh inputs to converge on one delivery result. For downloadable content, keep download state separate from entitlement state. For consumable content, record the grant before marking the transaction delivered/finished according to the selected architecture. For revocable subscriptions, make removal or suspension idempotent too.

## Native UI and Liquid Glass route

Compose the feature like this:

~~~text
SwiftUI navigation/search/filter shell
  -> catalog detail with semantic SKU and current terms
  -> app-owned preparation state
  -> AdvancedCommerceProduct system purchase
  -> native result/status surface
  -> system subscription management/refund route where applicable
~~~

Keep glass effects in the app-owned shell. Use solid hierarchy and semantic controls for price, period, plan state, pending, verification, and support. Do not wrap the StoreKit confirmation sheet or mirror Apple Account settings.

## On-device AI route

~~~swift
struct AICommerceProposal: Sendable, Equatable {
    let candidateSKUs: [String]
    let explanation: String
    let catalogRevision: String
    let requiresUserReview: Bool
}
~~~

Validate every candidate SKU against the current server-supplied catalog and current storefront before display. The model can explain known products or refine discovery. The model cannot create a signed request, change a price/tax code, decide entitlement, or execute purchase/restore/manage/refund without explicit user action and deterministic policy.

## Fallback matrix

| Failure | App response | Never infer |
| --- | --- | --- |
| No Advanced Commerce access | Keep feature unavailable or use ordinary StoreKit route | That a generic product ID is enough. |
| Catalog unavailable | Show last safe cache with stale marker or free fallback | That cached price is current. |
| Server signing unavailable | Keep purchase action disabled with retry/support | That the client can sign. |
| JWS expired/mismatched | Discard and request a fresh envelope | That any JWS for the app is valid for this SKU. |
| StoreKit pending | Show pending state and wait for updates/server event | That payment is complete. |
| Unverified transaction | Preserve retry/support and no new access | That a returned transaction is trustworthy. |
| Notification outage | Reconcile with history/current status | That missing notification means no purchase. |
| Server/account stale | Show refresh state and preserve known entitlement policy | That local UI is current authority. |
| Model unavailable | Keep deterministic catalog search and checkout | That AI is required for a purchase. |
| Local StoreKit test unavailable | Use fixtures for UI/state and sandbox for provider behavior | That an ordinary .storekit run proves Advanced Commerce. |

## Evidence sequence

1. Compile the exact AdvancedCommerceProduct route in a named iOS 26 target.
2. Unit-test typed intent, catalog revision, envelope expiry, JWS opaque handling, and outcome mapping.
3. Test server JWT/JWS generation and Apple JWS verification with safe fixtures and Apple’s library/tooling where selected.
4. Test notification dedupe, signed-date ordering, retry response, history pagination, environment matching, and current-status reconciliation.
5. Test UI and accessibility with catalog fixtures and unavailable/pending/unverified states.
6. Use an approved sandbox setup and physical signed device/TestFlight to prove provider transaction and system confirmation behavior.
7. Record production/release evidence separately from local and sandbox evidence.

## Related routes

- [Advanced Commerce API and App Store Server deep dive](../42-framework-deep-dives/69-advanced-commerce-api-and-app-store-server.md)
- [Advanced Commerce catalog and checkout design](../21-design-deep-dives/90-advanced-commerce-catalog-and-checkout-design.md)
- [Advanced Commerce server proof matrix](../60-verification/87-advanced-commerce-server-proof-matrix.md)
- [Advanced Commerce and App Store Server recipes](../70-code-recipes/105-advanced-commerce-and-server-recipes.md)

## Sources

- [Advanced Commerce API](https://developer.apple.com/documentation/advancedcommerceapi)
- [Advanced Commerce API access and eligibility](https://developer.apple.com/in-app-purchase/advanced-commerce-api/)
- [Setting up your project for Advanced Commerce API](https://developer.apple.com/documentation/advancedcommerceapi/setting-up-your-project-for-advanced-commerce)
- [Setting up generic product identifiers](https://developer.apple.com/documentation/advancedcommerceapi/setting-up-generic-product-identifiers)
- [AdvancedCommerceProduct](https://developer.apple.com/documentation/storekit/advancedcommerceproduct)
- [AdvancedCommerceProduct.currentEntitlements](https://developer.apple.com/documentation/storekit/advancedcommerceproduct/currententitlements)
- [AdvancedCommerceProduct.purchase(compactJWS:options:)](https://developer.apple.com/documentation/storekit/advancedcommerceproduct/purchase%28compactjws%3Aoptions%3A%29)
- [Sending Advanced Commerce API requests from your app](https://developer.apple.com/documentation/storekit/sending-advanced-commerce-api-requests-from-your-app)
- [Generating JWS to sign App Store requests](https://developer.apple.com/documentation/storekit/generating-jws-to-sign-app-store-requests)
- [App Store Server API](https://developer.apple.com/documentation/appstoreserverapi)
- [Creating API keys to authorize API requests](https://developer.apple.com/documentation/appstoreserverapi/creating-api-keys-to-authorize-api-requests)
- [Generating JSON Web Tokens for API requests](https://developer.apple.com/documentation/appstoreserverapi/generating-json-web-tokens-for-api-requests)
- [Simplifying your implementation by using the App Store Server Library](https://developer.apple.com/documentation/appstoreserverapi/simplifying-your-implementation-by-using-the-app-store-server-library)
- [Get Transaction History](https://developer.apple.com/documentation/appstoreserverapi/get-transaction-history)
- [HistoryResponse](https://developer.apple.com/documentation/appstoreserverapi/historyresponse)
- [Get All Subscription Statuses](https://developer.apple.com/documentation/appstoreserverapi/get-all-subscription-statuses)
- [App Store Server Notifications](https://developer.apple.com/documentation/appstoreservernotifications)
- [Enabling App Store Server Notifications](https://developer.apple.com/documentation/appstoreservernotifications/enabling-app-store-server-notifications)
- [Receiving App Store Server Notifications](https://developer.apple.com/documentation/appstoreservernotifications/receiving-app-store-server-notifications)
- [Responding to App Store Server Notifications](https://developer.apple.com/documentation/appstoreservernotifications/responding-to-app-store-server-notifications)
- [responseBodyV2](https://developer.apple.com/documentation/appstoreservernotifications/responsebodyv2)
- [notificationType](https://developer.apple.com/documentation/appstoreservernotifications/notificationtype)
- [signedDate](https://developer.apple.com/documentation/appstoreservernotifications/signeddate)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
