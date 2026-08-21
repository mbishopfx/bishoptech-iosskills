# Advanced Commerce and App Store Server recipes

These are compile-oriented route sketches, not verified product code. They deliberately keep server secrets, Apple approval, catalog authority, JWS verification, account policy, and delivery state visible. Confirm every signature, availability annotation, target platform, and server-library API in the selected iOS 26 SDK and server implementation before copying.

Advanced Commerce path:

~~~text
validated app-owned SKU -> server-signed request -> AdvancedCommerceProduct
  -> StoreKit result -> verified transaction -> idempotent delivery
~~~

## Recipe 1: typed catalog entry

~~~swift
struct AdvancedCatalogEntry: Codable, Identifiable, Sendable, Equatable {
    let id: String
    let genericProductID: String
    let displayName: String
    let description: String
    let priceMinorUnits: Int64
    let currencyCode: String
    let periodDescription: String?
    let taxCode: String
    let storefront: String
    let catalogRevision: String
    let isAvailable: Bool
}
~~~

Keep the app-owned SKU (id) distinct from genericProductID. Render the catalog entry only after validating the response’s schema, account scope, storefront, revision, and availability. Do not treat the server’s display price as the signed Apple transaction or use it to bypass StoreKit.

## Recipe 2: typed purchase intent

~~~swift
struct AdvancedPurchaseIntent: Encodable, Sendable, Equatable {
    let sku: String
    let genericProductID: String
    let catalogRevision: String
    let requestReferenceID: UUID
    let operation: Operation

    enum Operation: String, Encodable, Sendable {
        case oneTimeChargeCreate
        case subscriptionCreate
        case subscriptionModifyInApp
        case subscriptionReactivateInApp
    }
}
~~~

The app sends a typed intent to an authenticated server endpoint. It does not send a client-chosen price, tax code, arbitrary request JSON, or compact JWS to be re-signed without validation.

## Recipe 3: server response envelope

~~~swift
struct AdvancedCommerceRequestEnvelope: Decodable, Sendable {
    let requestReferenceID: UUID
    let genericProductID: String
    let compactJWS: String
    let catalogRevision: String
    let expiresAt: Date
}

enum EnvelopeError: Error {
    case expired
    case wrongGenericProduct
    case wrongRequest
    case staleRevision
}

func validate(
    _ envelope: AdvancedCommerceRequestEnvelope,
    expectedGenericProductID: String,
    expectedRequestReferenceID: UUID,
    expectedRevision: String,
    now: Date = .now
) throws {
    guard envelope.expiresAt > now else { throw EnvelopeError.expired }
    guard envelope.genericProductID == expectedGenericProductID else {
        throw EnvelopeError.wrongGenericProduct
    }
    guard envelope.requestReferenceID == expectedRequestReferenceID else {
        throw EnvelopeError.wrongRequest
    }
    guard envelope.catalogRevision == expectedRevision else {
        throw EnvelopeError.staleRevision
    }
}
~~~

Treat compactJWS as opaque. The app validates the envelope context and passes the artifact to the documented StoreKit call; it does not decode the payload to decide entitlement.

## Recipe 4: initialize AdvancedCommerceProduct

~~~swift
import StoreKit

@MainActor
func advancedProduct(
    genericProductID: AdvancedCommerceProduct.ID
) async throws -> AdvancedCommerceProduct {
    try await AdvancedCommerceProduct(id: genericProductID)
}
~~~

AdvancedCommerceProduct is the documented StoreKit representation of a generic SKU product configured for Advanced Commerce. Confirm the generic ID belongs to the approved app and the selected product family before starting a purchase.

## Recipe 5: purchase with the compact JWS

~~~swift
import StoreKit

@MainActor
func startAdvancedPurchase(
    product: AdvancedCommerceProduct,
    envelope: AdvancedCommerceRequestEnvelope
) async throws -> Product.PurchaseResult {
    try await product.purchase(
        compactJWS: envelope.compactJWS,
        options: []
    )
}
~~~

AdvancedCommerceProduct.PurchaseResult is a type alias for Product.PurchaseResult. The result can be pending, user-cancelled, or success with a verified/unverified transaction; the method can also throw a purchase, StoreKit, or invalid-request error. Preserve each branch.

## Recipe 6: map every purchase result

~~~swift
import StoreKit

enum AdvancedPurchaseOutcome: Sendable, Equatable {
    case pending
    case cancelled
    case verified(transactionID: UInt64)
    case unverified
    case failed
}

func outcome(
    from result: Product.PurchaseResult
) -> AdvancedPurchaseOutcome {
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

The verified branch is evidence to feed into delivery and entitlement policy. It is not itself a content grant. Do not call finish before the selected delivery policy has durable success or a retryable record.

## Recipe 7: wrap server JWS as advancedCommerceData

Apple documents an app-side request-data form for certain Advanced Commerce request types. The server creates the request JSON, UTF-8 encodes it, base64-encodes it, puts that value in the JWS request claim, and wraps the compact JWS in signatureInfo.token.

~~~swift
import Foundation
import StoreKit

struct SignatureInfo: Encodable, Sendable {
    let token: String
}

struct AdvancedCommerceSignatureEnvelope: Encodable, Sendable {
    let signatureInfo: SignatureInfo
}

func advancedCommerceRequestData(
    compactJWS: String
) throws -> Data {
    let envelope = AdvancedCommerceSignatureEnvelope(
        signatureInfo: SignatureInfo(token: compactJWS)
    )
    return try JSONEncoder().encode(envelope)
}

func advancedCommerceOption(
    requestData: Data
) -> Product.PurchaseOption {
    .custom(key: "advancedCommerceData", value: requestData)
}
~~~

The exact request type and StoreKit call must match Apple’s current Advanced Commerce documentation. The custom key is case-sensitive. The app receives signed request data, never the signing key.

## Recipe 8: request the app-side option

~~~swift
import StoreKit

@MainActor
func purchaseWithAdvancedCommerceData(
    product: Product,
    requestData: Data
) async throws -> Product.PurchaseResult {
    try await product.purchase(options: [
        .custom(key: "advancedCommerceData", value: requestData)
    ])
}
~~~

Use this only with the product/request shape Apple documents for the selected SDK. Do not assume an ordinary Product loaded from a fixed App Store product list is interchangeable with AdvancedCommerceProduct; verify the object graph and initializer in the target.

## Recipe 9: read current Advanced Commerce entitlements

~~~swift
import StoreKit

@MainActor
func verifiedAdvancedEntitlements(
    for product: AdvancedCommerceProduct
) async -> [Transaction] {
    var transactions: [Transaction] = []

    for await verification in product.currentEntitlements {
        if case .verified(let transaction) = verification {
            transactions.append(transaction)
        }
    }

    return transactions
}
~~~

The current-entitlements sequence is local StoreKit evidence for items under the generic product ID. Apply account, server, content, revocation, and delivery policy before exposing access. Keep the unverified branch visible in the real implementation if the app needs support telemetry or retry handling.

## Recipe 10: observe transaction updates

~~~swift
import StoreKit

struct TransactionUpdateTask: Sendable {
    let task: Task<Void, Never>
}

@MainActor
func startTransactionUpdates(
    handle: @escaping @Sendable (VerificationResult<Transaction>) async -> Void
) -> TransactionUpdateTask {
    let task = Task {
        for await verification in Transaction.updates {
            await handle(verification)
        }
    }
    return TransactionUpdateTask(task: task)
}
~~~

Start a long-lived listener early in the app lifecycle and cancel it at the selected owner’s teardown. Route updates through the same verification, delivery, entitlement, and finish policy as the direct purchase call. The listener does not replace server notifications or history reconciliation.

## Recipe 11: typed server intent endpoint

~~~text
POST /commerce/advanced/request
Authorization: Bearer <app-session-token>
Content-Type: application/json

{
  "sku": "course_42_lesson_07",
  "genericProductID": "com.example.catalog.aca.generic.consumable",
  "catalogRevision": "rev-2026-08-20T12:00:00Z",
  "requestReferenceID": "<uuid>",
  "operation": "oneTimeChargeCreate"
}
~~~

Server checks:

~~~text
authenticate account/session
load SKU from server catalog
verify generic product family and operation
verify catalog revision/storefront/availability
resolve current price, currency, period, and tax code
reject duplicate or replayed request reference
construct Apple request body
base64-encode UTF-8 JSON
sign JWS with server-only key
return short-lived envelope
~~~

The endpoint is not a generic JWS signer. Build the Apple request from server-owned data.

## Recipe 12: server-only JWS claim model

~~~swift
struct AdvancedCommerceJWSClaims: Encodable, Sendable {
    let iss: String
    let iat: Int64
    let aud: String
    let bid: String
    let nonce: UUID
    let request: String
}
~~~

Apple’s current guidance documents aud as advanced-commerce-api for Advanced Commerce in-app requests, and request as the base64-encoded request data. Sign with ES256 on the server. Do not place iss, private key contents, or a reusable signer in the app.

## Recipe 13: server JWT authorization model

~~~swift
struct AppStoreServerJWTClaims: Encodable, Sendable {
    let iss: String
    let iat: Int64
    let exp: Int64
    let aud: String
    let bid: String
}
~~~

For App Store Server API calls, Apple documents aud as appstoreconnect-v1, ES256 signing, an App Store Connect key ID, and an expiration no more than one hour after iat. Prefer Apple’s App Store Server Library for the selected server language when it meets the project’s operational requirements.

## Recipe 14: notification handler boundary

~~~swift
struct NotificationAcceptance: Sendable, Equatable {
    let notificationUUID: String
    let signedDateMilliseconds: Int64
    let accepted: Bool
}

protocol AppleNotificationVerifier: Sendable {
    func verifyAndDecode(
        signedPayload: String
    ) throws -> DecodedAppleNotification
}

struct DecodedAppleNotification: Sendable {
    let notificationUUID: String
    let signedDateMilliseconds: Int64
    let notificationType: String
    let subtype: String?
    let bundleID: String
    let environment: String
}
~~~

The verifier should validate Apple’s JWS, bundle, environment, and nested signed values where present. Keep the verifier behind a protocol so state-machine tests can use fixtures without pretending that fixture decoding proves Apple signatures.

## Recipe 15: notification dedupe and ordering

~~~swift
struct NotificationRecord: Sendable, Equatable {
    let uuid: String
    let transactionID: String?
    let signedDateMilliseconds: Int64
    let payloadDigest: String
}

func shouldApply(
    incomingSignedDate: Int64,
    newestStoredDate: Int64?
) -> Bool {
    guard let newestStoredDate else { return true }
    return incomingSignedDate >= newestStoredDate
}
~~~

Use notificationUUID for dedupe and signedDate as part of the state-ordering policy. Apple documents notifications as snapshots and provides current-status/history routes for recovery, so do not build a system that assumes arrival order is provider truth.

## Recipe 16: App Store Server API history pagination

~~~swift
struct HistoryPage: Decodable, Sendable {
    let hasMore: Bool
    let revision: String?
    let signedTransactions: [String]
}

protocol AppStoreServerHistoryClient: Sendable {
    func page(
        transactionID: String,
        revision: String?,
        filters: [URLQueryItem]
    ) async throws -> HistoryPage
}

func loadAllHistory(
    transactionID: String,
    filters: [URLQueryItem],
    client: AppStoreServerHistoryClient
) async throws -> [String] {
    var revision: String?
    var signedTransactions: [String] = []

    repeat {
        let page = try await client.page(
            transactionID: transactionID,
            revision: revision,
            filters: filters
        )
        signedTransactions += page.signedTransactions
        revision = page.revision

        if !page.hasMore { break }
    } while true

    return signedTransactions
}
~~~

The production client must keep the same query filters on subsequent revision requests, verify each signed transaction, match the environment, and persist a support-safe revision according to the selected sort policy. The String values above are still signed JWS values until the server verifies them.

## Recipe 17: current subscription status is separate

~~~swift
enum ServerSubscriptionState: Sendable, Equatable {
    case subscribed
    case gracePeriod
    case billingRetry
    case expired
    case revoked
    case unavailable
}

func featureAccess(
    from state: ServerSubscriptionState
) -> Bool {
    switch state {
    case .subscribed, .gracePeriod:
        return true
    case .billingRetry, .expired, .revoked, .unavailable:
        return false
    }
}
~~~

Map the actual decoded App Store Server API status and renewal information into this app-owned policy. Do not infer current access merely because a transaction appears in history or because a notification was received.

## Recipe 18: idempotent delivery record

~~~swift
struct DeliveryKey: Hashable, Sendable {
    let environment: String
    let transactionID: String
    let sku: String
}

enum DeliveryResult: Sendable, Equatable {
    case delivered
    case alreadyDelivered
    case retryableFailure
    case blocked
}

protocol DeliveryLedger: Sendable {
    func deliver(
        key: DeliveryKey,
        transactionData: VerifiedTransactionData
    ) async throws -> DeliveryResult
}

struct VerifiedTransactionData: Sendable {
    let transactionID: String
    let originalTransactionID: String?
    let sku: String
}
~~~

The actual ledger must atomically prevent duplicate grants and record retryable failures. Keep download, content indexing, and access projection separate when those lifecycles differ.

## Recipe 19: SwiftUI catalog card with explicit state

~~~swift
import SwiftUI

struct AdvancedCatalogCard: View {
    let entry: AdvancedCatalogEntry
    let purchase: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(entry.displayName)
                .font(.headline)

            Text(entry.description)
                .font(.subheadline)
                .foregroundStyle(.secondary)

            HStack {
                Text(entry.currencyCode)
                    .font(.caption)
                Spacer()
                if entry.isAvailable {
                    Button("Review purchase", action: purchase)
                        .buttonStyle(.borderedProminent)
                } else {
                    Label("Unavailable", systemImage: "nosign")
                        .font(.caption)
                }
            }
        }
        .padding()
        .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 20))
    }
}
~~~

This sketch intentionally does not format a final localized price. Replace the placeholder with the validated localized value required by the product design, and confirm the catalog/payment-sheet data are consistent. Use Liquid Glass selectively around app-owned actions; do not use this card as a fake system confirmation sheet.

## Recipe 20: reviewable AI proposal

~~~swift
struct CommerceAIProposal: Sendable, Equatable {
    let sku: String
    let explanation: String
    let catalogRevision: String
    let requiresUserReview: Bool
}

func resolveProposal(
    _ proposal: CommerceAIProposal,
    entries: [AdvancedCatalogEntry],
    currentRevision: String
) -> AdvancedCatalogEntry? {
    guard proposal.requiresUserReview,
          proposal.catalogRevision == currentRevision else {
        return nil
    }

    return entries.first {
        $0.id == proposal.sku && $0.isAvailable
    }
}
~~~

The proposal is a candidate, not an order. Show the exact current catalog values, require a visible user action, and have the server revalidate before signing. Never allow a model to provide arbitrary price/tax fields or invoke the signing endpoint as a generic tool.

## Recipe 21: notification endpoint behavior

~~~text
POST /apple/app-store-server/notifications

if transport/body invalid:
    return 400 or 500 according to retry policy

verify signedPayload and nested JWS values
validate bundle ID and environment
if notificationUUID already stored:
    return 200

store notification and enqueue projection work
return 200
~~~

Apple documents 200–206 as success for V2 notification posts. Match the response to the server’s durable-acceptance contract and use 4xx/5xx for retryable failures. Test with Apple’s Request a Test Notification endpoint rather than only posting a local fixture.

## Recipe 22: safe server logging

~~~swift
struct CommerceAuditEvent: Codable, Sendable {
    let requestReferenceID: UUID
    let sku: String
    let genericProductID: String
    let environment: String
    let transactionID: String?
    let notificationUUID: String?
    let status: String
    let timestamp: Date
}
~~~

Keep audit logs to support-safe identifiers and status. Do not log App Store Connect private keys, JWTs, compact JWS strings, app account tokens, full notification bodies, or model transcripts containing account/catalog data.

## Recipe 23: unavailable/local test fallback

~~~swift
enum CommerceCapabilityState: Sendable, Equatable {
    case loading
    case ready
    case serverUnavailable
    case providerUnavailable
    case pending
    case needsReview
}

func showsPurchaseAction(
    state: CommerceCapabilityState
) -> Bool {
    state == .ready
}
~~~

Keep already-delivered/free functionality usable if the server or provider is unavailable. If Advanced Commerce cannot be tested locally, use catalog/state fixtures for UI and Apple sandbox for provider behavior; do not show a false “test purchase succeeded” state.

## Recipe 24: proof checklist

~~~text
source: official Advanced Commerce, StoreKit, App Store Server API/Notifications docs
compile: named iOS 26 target with AdvancedCommerceProduct route
fixture: catalog, envelope, state, dedupe, history pagination
server: JWT/JWS generation, Apple JWS verification, V2 test notification
device: signed physical sandbox purchase and current entitlement
recovery: notification history/current-status/history reconciliation
accessibility: VoiceOver, Dynamic Type, contrast/transparency/motion, RTL, long prices
release: App Store Connect approval, metadata, signed archive, server environment
not proven: anything not represented by a recorded evidence row
~~~

## Related routes

- [Advanced Commerce API and App Store Server deep dive](../42-framework-deep-dives/69-advanced-commerce-api-and-app-store-server.md)
- [Advanced Commerce catalog and checkout design](../21-design-deep-dives/90-advanced-commerce-catalog-and-checkout-design.md)
- [Advanced Commerce and server entitlement capability route](../50-capability-recipes/93-advanced-commerce-and-server-entitlement-route.md)
- [Advanced Commerce server proof matrix](../60-verification/87-advanced-commerce-server-proof-matrix.md)

## Sources

- [Advanced Commerce API](https://developer.apple.com/documentation/advancedcommerceapi)
- [Advanced Commerce API access and eligibility](https://developer.apple.com/in-app-purchase/advanced-commerce-api/)
- [Setting up your project for Advanced Commerce API](https://developer.apple.com/documentation/advancedcommerceapi/setting-up-your-project-for-advanced-commerce)
- [Setting up generic product identifiers](https://developer.apple.com/documentation/advancedcommerceapi/setting-up-generic-product-identifiers)
- [Creating SKUs for your In-App Purchases](https://developer.apple.com/documentation/advancedcommerceapi/creating-your-purchases)
- [AdvancedCommerceProduct](https://developer.apple.com/documentation/storekit/advancedcommerceproduct)
- [AdvancedCommerceProduct.PurchaseResult](https://developer.apple.com/documentation/storekit/advancedcommerceproduct/purchaseresult)
- [AdvancedCommerceProduct.PurchaseOption](https://developer.apple.com/documentation/storekit/advancedcommerceproduct/purchaseoption)
- [AdvancedCommerceProduct.purchase(compactJWS:options:)](https://developer.apple.com/documentation/storekit/advancedcommerceproduct/purchase%28compactjws%3Aoptions%3A%29)
- [AdvancedCommerceProduct.currentEntitlements](https://developer.apple.com/documentation/storekit/advancedcommerceproduct/currententitlements)
- [Sending Advanced Commerce API requests from your app](https://developer.apple.com/documentation/storekit/sending-advanced-commerce-api-requests-from-your-app)
- [Generating JWS to sign App Store requests](https://developer.apple.com/documentation/storekit/generating-jws-to-sign-app-store-requests)
- [Product.PurchaseOption](https://developer.apple.com/documentation/storekit/product/purchaseoption)
- [Product.purchase(options:)](https://developer.apple.com/documentation/storekit/product/purchase%28options%3A%29)
- [Transaction](https://developer.apple.com/documentation/storekit/transaction)
- [Transaction.updates](https://developer.apple.com/documentation/storekit/transaction/updates)
- [App Store Server API](https://developer.apple.com/documentation/appstoreserverapi)
- [Creating API keys to authorize API requests](https://developer.apple.com/documentation/appstoreserverapi/creating-api-keys-to-authorize-api-requests)
- [Generating JSON Web Tokens for API requests](https://developer.apple.com/documentation/appstoreserverapi/generating-json-web-tokens-for-api-requests)
- [Simplifying your implementation by using the App Store Server Library](https://developer.apple.com/documentation/appstoreserverapi/simplifying-your-implementation-by-using-the-app-store-server-library)
- [Get Transaction History](https://developer.apple.com/documentation/appstoreserverapi/get-transaction-history)
- [HistoryResponse](https://developer.apple.com/documentation/appstoreserverapi/historyresponse)
- [revision](https://developer.apple.com/documentation/appstoreserverapi/revision)
- [Get All Subscription Statuses](https://developer.apple.com/documentation/appstoreserverapi/get-all-subscription-statuses)
- [App Store Server Notifications](https://developer.apple.com/documentation/appstoreservernotifications)
- [App Store Server Notifications V2](https://developer.apple.com/documentation/appstoreservernotifications/app-store-server-notifications-v2)
- [Enabling App Store Server Notifications](https://developer.apple.com/documentation/appstoreservernotifications/enabling-app-store-server-notifications)
- [Receiving App Store Server Notifications](https://developer.apple.com/documentation/appstoreservernotifications/receiving-app-store-server-notifications)
- [Responding to App Store Server Notifications](https://developer.apple.com/documentation/appstoreservernotifications/responding-to-app-store-server-notifications)
- [responseBodyV2](https://developer.apple.com/documentation/appstoreservernotifications/responsebodyv2)
- [notificationType](https://developer.apple.com/documentation/appstoreservernotifications/notificationtype)
- [signedDate](https://developer.apple.com/documentation/appstoreservernotifications/signeddate)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
