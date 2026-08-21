# Advanced Commerce API, App Store Server API, and server-authoritative commerce

## Capability boundary

Advanced Commerce API is a gated App Store commerce path for apps with exceptionally large catalogs of custom one-time purchases, subscriptions, or subscriptions with optional add-ons. The app owns and manages its SKU catalog and supplies product details dynamically at runtime; Apple handles App Store payment processing, distribution, tax support, and customer service.

This is a different catalog shape from ordinary StoreKit product loading:

~~~text
app-owned SKU catalog and merchandising data
  -> generic product ID configured in App Store Connect
  -> AdvancedCommerceProduct in StoreKit
  -> server-authorized request/JWS
  -> Apple system confirmation and App Store transaction
  -> StoreKit transaction evidence + App Store Server notifications/API
  -> deterministic entitlement and delivery projection
~~~

Do not treat Advanced Commerce API as a shortcut for ordinary subscriptions, a replacement for App Store Connect product configuration, or a client-side payment processor. Apple reviews access per app, and the documented setup and feature limitations are part of the implementation boundary.

## When this route is appropriate

Apple describes Advanced Commerce API for use cases such as large libraries of audiobooks, classes, courses, creator offerings, mini apps, or subscriptions with optional add-on content. It can be used in the same app as the ordinary StoreKit In-App Purchase API. The two paths share Apple’s signed JWS transaction and renewal-information formats, but their product/catalog setup is different.

Use the ordinary StoreKit API when a small, stable set of products configured in App Store Connect is enough. Consider Advanced Commerce only when the app’s core business model requires an exceptionally large or frequently changing SKU catalog and the app can meet Apple’s access, setup, system-surface, and server requirements.

| Product need | Better route | Reason |
| --- | --- | --- |
| A few fixed lifetime unlocks or subscription plans | StoreKit 2 | App Store Connect products, native StoreKit views, and normal purchase/entitlement flows are simpler. |
| Many individually merchandised content SKUs | Advanced Commerce API, if approved | The app hosts its catalog and supplies SKU details dynamically. |
| Server reconciliation, missed events, current subscription state, or refund history | App Store Server API | The server can query Apple independently of the app’s installation state. |
| Real-time purchase and renewal events | App Store Server Notifications V2 | Apple posts signed event payloads to the server. |
| Local deterministic StoreKit UI tests | Ordinary StoreKit testing route | Advanced Commerce purchases handled by the API cannot use StoreKit Testing in Xcode. |

## Eligibility and setup are product requirements

Advanced Commerce access is not implied by importing StoreKit. Apple’s public access page describes an application and review process handled per app. Once approved, the documented setup includes:

1. Create the required generic product identifiers in App Store Connect.
2. Send the generic IDs to Apple through the Advanced Commerce API Access form.
3. Configure a TLS 1.2-or-later server.
4. Enable App Store Server Notifications V2 for production and, optionally, sandbox.
5. Provide an in-app subscription-management deep link as part of the access setup.
6. Review tax codes and define the app-owned SKU catalog.
7. Configure an optional payment-sheet image for the generic one-time and subscription IDs.
8. Test the app and server in the sandbox before App Review.

Apple documents up to four generic product IDs for the product categories the app offers: one-time purchases, subscriptions, and the corresponding Mini Apps Partner Program categories. A generic product ID is a placeholder that tells the API what kind of SKU is being handled. It is not the individual content SKU, and it does not carry each SKU’s final price, localization, or tax information.

Keep these identifiers separate:

| Identifier | Owner | Example role |
| --- | --- | --- |
| App bundle ID | App Store Connect/app target | com.example.catalog |
| Generic product ID | App Store Connect and Apple access setup | com.example.catalog.aca.generic.subscription |
| App-owned SKU | Catalog service and signed request | creator_42_course_07 |
| Request reference ID | App/server operation | Idempotency and support correlation. |
| Transaction ID/original transaction ID | Apple-signed transaction | Apple’s transaction identity, not a local SKU. |

Never use a human-readable title as the only identity. A title can be localized or edited; the SKU and request reference ID must remain stable according to the app’s catalog and migration policy.

## StoreKit object graph

AdvancedCommerceProduct is the StoreKit representation of a generic SKU product configured in App Store Connect. Apple documents an async initializer by generic product ID, a ProductType, purchase methods that accept a compact JWS, and transaction/entitlement sequences associated with the generic product ID.

| Concern | API or data | Boundary |
| --- | --- | --- |
| Generic StoreKit product | AdvancedCommerceProduct | Represents the generic product configured for the Advanced Commerce path. |
| Generic product identity | AdvancedCommerceProduct.id | The generic ID, not the app-owned content SKU. |
| Product kind | AdvancedCommerceProduct.type | Tells the route which generic product family is in use. |
| App-side purchase | purchase(compactJWS:options:) | Uses a server-generated compact JWS for the operation. |
| Purchase result | AdvancedCommerceProduct.PurchaseResult | A type alias for Product.PurchaseResult; preserve pending, cancelled, verified, unverified, and thrown-error handling. |
| Current local entitlements | currentEntitlements | StoreKit’s current entitling transactions for Advanced Commerce items under the generic ID. |
| All local transactions | allTransactions | Transaction history associated with the generic product ID; not a substitute for the server ledger. |
| Latest transaction | latestTransaction | The most recent transaction if one exists; verify and apply app policy. |

The generic product ID is not an individual content item. The app’s visible card or detail screen must carry the app-owned SKU, the exact current display data, and the operation context that the server signs. Do not silently substitute one SKU for another because both use the same generic product.

## App-side requests use server-generated signed request data

Apple documents four Advanced Commerce request types that can be made through StoreKit in the app:

- OneTimeChargeCreateRequest
- SubscriptionCreateRequest
- SubscriptionModifyInAppRequest
- SubscriptionReactivateInAppRequest

The request construction and signature flow is intentionally split:

~~~text
app selects a known catalog item and sends a request intent
  -> server validates SKU, storefront, account, price, tax, and operation
  -> server creates UTF-8 JSON request data
  -> server base64-encodes the request data
  -> server signs a JWS with the App Store Connect private key
  -> server wraps the JWS in signatureInfo.token
  -> app receives advancedCommerceRequestData over a secure channel
  -> app passes it as the documented purchase option
  -> StoreKit presents the system confirmation surface
~~~

The custom purchase key for the request data is advancedCommerceData. The client should not invent the price, tax code, or signed payload. It may display the server’s catalog result, but the server must revalidate the operation before signing. A stale app card, a manipulated request body, or a prompt-injected model must not become an Apple-authorized purchase.

Apple’s documented JWS signing guidance uses an ES256 header with the App Store Connect key ID and JWT-style claims. For Advanced Commerce in-app requests, the audience is advanced-commerce-api, and the custom request claim contains the base64-encoded request data. The server should create and sign the compact JWS, send it securely to the app, and keep the private key out of repositories, logs, app bundles, and client-side code.

The signing boundary is not the same as the App Store Server API JWT boundary:

| Signed artifact | Issuer | Audience/use | Keep where |
| --- | --- | --- | --- |
| Advanced Commerce in-app compact JWS | App server with App Store Connect private key | Authorizes a StoreKit purchase operation | Server creates it; app receives only the operation data. |
| App Store Server API JWT | App server with App Store Connect private key | Authorizes a server REST request to Apple | Server only. |
| Apple transaction JWS | Apple | Describes a transaction | Verify on device and/or server; do not treat decoded text as unsigned truth. |
| App Store Server Notifications V2 signedPayload | Apple | Describes a notification snapshot | Verify and process on server. |

## AdvancedCommerceProduct purchase lifecycle

Treat the app-side route as an async state machine:

~~~text
idle
  -> catalogEntrySelected
  -> requestPreparing
  -> signedRequestReady
  -> systemPurchaseInFlight
  -> pending
  -> userCancelled
  -> success(verified)
  -> success(unverified)
  -> failed
~~~

The success branch still contains a VerificationResult<Transaction>. Route a verified transaction through the same delivery and entitlement policy used by ordinary StoreKit 2. Do not grant access because the native sheet appeared, because a network response was 200, or because the model predicted a successful purchase. Do not finish a transaction before the app has durably delivered the item or recorded retryable delivery state.

For a consumable or one-time content SKU, the server ledger needs an idempotency key such as the Apple transaction ID plus the app-owned SKU. For subscription content, the entitlement projection needs current product, renewal state, expiration/renewal dates, revocation/refund state, and the relationship between the Apple transaction and the app-owned content set.

AdvancedCommerceProduct.currentEntitlements is useful local evidence for the generic product. It is not a complete catalog grant table and it does not remove the need for server reconciliation when the app has an account, creator content, refunds, migrations, or cross-device delivery.

## App Store Server API is independent of installation state

The App Store Server API is a server REST API. Apple states that it returns signed transaction and renewal information and is independent of whether a customer currently has the app installed. Use it to reconcile a durable account ledger, recover from missed notifications, inspect transaction history, determine current subscription statuses, request refund history, and test notification delivery.

| Need | Endpoint family | Implementation note |
| --- | --- | --- |
| Individual transaction | Get Transaction Info | Use a known Apple transaction ID and verify returned signed data. |
| Full customer history | Get Transaction History | Page with revision; each response has up to 20 signed transactions. |
| Current subscription state | Get All Subscription Statuses | Use this for current status rather than assuming a notification snapshot is current. |
| Missed notification recovery | Get Notification History | Production history covers the documented 180-day window; sandbox has a shorter documented window. |
| Server endpoint test | Request a Test Notification/Get Test Notification Status | Proves notification delivery/response behavior in the selected environment. |
| Refund context | Get Refund History/Send Consumption Information | Follow the current endpoint and notification requirements for the product type. |
| Account association | Set App Account Token | Use only with a declared account-linkage and privacy policy. |

App Store Server API calls require a server-generated JWT. Apple documents ES256 signing, appstoreconnect-v1 as the audience, and a maximum validity of one hour after iat. Generate a new token per request according to the current documentation or use Apple’s App Store Server Library.

The App Store Server Library is an official open-source library available for Swift, Java, Python, and Node. Apple documents that it can create API clients/JWTs, verify and decode Apple JWS transactions and renewal information, extract transaction identifiers, and generate JWS signatures for Advanced Commerce in-app requests. Treat it as an implementation aid, not as permission to move private keys into the iOS target.

## Environment matching and history pagination

Apple provides production and sandbox base URLs. When an endpoint takes a transaction ID, call the environment that created that transaction. The signed transaction payload includes environment information. If the environment is unknown, Apple documents a production-first lookup followed by sandbox retry after a transaction-not-found response.

For transaction history:

~~~text
first request: no revision
  -> HistoryResponse(signedTransactions, hasMore, revision)
  -> if hasMore, call again with the same filters and revision
  -> continue until hasMore == false
  -> persist the final revision only according to the documented sort/pagination policy
~~~

Do not drop filters between pages. Apple explicitly requires subsequent requests with revision to use the same query parameters as the initial request. The response includes signed transactions for all product types and can include refunded, revoked, and unfinished transactions. A history record is not automatically an active entitlement.

The server should persist:

- Apple environment and bundle ID;
- original transaction ID and transaction ID;
- app-owned SKU and request reference ID;
- signed transaction/renewal verification result and relevant decoded fields;
- notification UUID and signed date for deduplication/order policy;
- history revision and query scope;
- entitlement projection version;
- delivery status and retry count;
- support-safe audit identifiers without raw secrets or unnecessary JWS bodies.

## App Store Server Notifications V2

App Store Server Notifications is a server-to-server service. Apple recommends V2 for new implementations; V1 endpoint and notification fields are deprecated. Configure an HTTPS endpoint for production and optionally sandbox. TLS 1.2 or later is required, and Apple documents response codes 200 through 206 as successful. A 4xx or 5xx response asks Apple to retry.

The V2 body contains a top-level signedPayload. The signed payload contains a decoded response with fields such as notificationType, optional subtype, notificationUUID, signedDate, and data. The data object can include signedTransactionInfo and signedRenewalInfo, which are themselves signed JWS values. Validate each signature on the server before using the values.

Treat notifications as signed event snapshots, not as a globally ordered database stream:

1. Validate the outer JWS certificate/signature and parse the payload.
2. Reject or quarantine a malformed, wrong-bundle, wrong-environment, or replayed notification according to the server policy.
3. Dedupe by notificationUUID and keep the signed timestamp.
4. Verify nested transaction and renewal JWS values when present.
5. Apply the event to an idempotent ledger/projection, using the newest valid state for the relevant transaction when events arrive out of order.
6. Acknowledge successful processing with 200–206.
7. On a transient failure, return a retryable status and use notification history or current-status APIs for recovery.

Apple documents that signedDate is the time the notification was signed and that the payload is a snapshot at that time. If multiple notifications concern the same transaction, use the notification with the most recent signed date as part of the ordering policy. A notification can be retried, delayed, or missed; do not use it as the only source of current subscription state.

Useful notification families include purchase/one-time charge events, renewals, renewal failures, grace-period changes, expiration, refunds/revocations, offer changes, price-increase events, consumption requests, and test notifications. Keep a table driven by the current Apple notificationType/subtype documentation; do not freeze a hand-written enum without an unknown-event path because Apple’s notification changelog is active.

## Server entitlement projection

Separate Apple evidence from product access:

~~~text
Apple-signed transaction/renewal evidence
  -> verified Apple event record
  -> app-owned SKU mapping
  -> delivery/idempotency result
  -> current entitlement projection
  -> feature access and UI explanation
~~~

The projection should be rebuildable from verified records. A local Boolean such as isPremium can be a cache, but it must not silently overrule a revocation, refund, expiration, account unlink, or migration policy.

For one-time content, decide whether access is device-local after verified delivery, account-bound after server reconciliation, a consumable balance with an idempotent grant, revocable content whose server projection can remove access, or downloadable content whose storage lifecycle is separate from purchase state.

For subscriptions, distinguish active service, grace period, billing retry, expired, revoked, pending plan change, and server-stale states. Explain the state in user language and expose the system subscription-management route Apple requires for eligible Advanced Commerce apps.

## Security and privacy boundaries

The private API key downloaded from App Store Connect is server secret material. Apple explicitly says to keep it secure, not share it, not store it in a repository, and not include it in client-side code. If compromised, revoke it in App Store Connect.

The iOS app may receive a short-lived signed request artifact, but it should not receive the private key, issuer secret, signing library credentials, or an unrestricted “sign anything” endpoint. The server endpoint should accept a typed operation and server-resolved catalog identity, validate authenticated account/session context, authorize the operation, and produce only the exact request needed.

Do not log:

- App Store Connect private keys, JWTs, or compact JWS values;
- raw Apple notification bodies when the retention policy does not require them;
- app account tokens or identity linkage values in ordinary logs;
- user prompts or model transcripts that contain hidden catalog/account data;
- full purchase metadata when a support-safe identifier is enough.

Use TLS, authenticated app-server communication, replay/idempotency checks, bundle/environment validation, key rotation, least-privilege server credentials, and an explicit retention/deletion policy. The app should fail closed for a missing or invalid signed request while leaving free or already-delivered functionality understandable.

## Advanced Commerce limitations that shape design and testing

Apple’s current Advanced Commerce access page says purchases handled by the API cannot be promoted on the App Store and cannot use certain App Store features at this time, including subscription offers, Family Sharable In-App Purchases, and StoreKit Testing in Xcode. This is a current provider limitation, not a general StoreKit rule; re-check the page and changelog before each implementation.

The same page describes app requirements to use StoreKit 2, provide in-app subscription management, use App Store Server API plus Notifications V2, and provide a customer refund path such as Report a Problem or beginRefundRequest. Encode each as a release criterion rather than treating an API call as sufficient proof.

For local development, test pure catalog rendering, request serialization, state machines, JWS envelope parsing, idempotency, and UI fallbacks with fixtures. Use Apple sandbox for real Advanced Commerce purchase/provider behavior. Do not report a successful local StoreKit configuration run as Advanced Commerce evidence.

## Liquid Glass and native-system composition

Liquid Glass belongs around app-owned discovery, search, filters, account context, and status surfaces. The Apple confirmation sheet remains the trusted system-owned payment surface. Do not draw a fake confirmation sheet or place a decorative glass panel over Apple’s localized price, terms, and transaction confirmation.

A good large-catalog composition is:

~~~text
navigation/tab shell
  -> search/filter and result context
  -> original content card with clear title and provenance
  -> localized current price/term and eligibility state
  -> explicit purchase action
  -> system confirmation sheet
  -> verified result and delivery state
~~~

Use native SwiftUI controls and system materials first. Preserve hierarchy when transparency, increased contrast, Dynamic Type, reduced motion, VoiceOver, pointer, keyboard, or RTL changes the surface. A glass treatment is successful only if the person can still identify the item, current price/term, selected state, pending state, and recovery action.

## On-device AI boundary

On-device AI may help a person browse a large catalog by summarizing a known SKU, comparing two loaded entries, generating a query refinement, or proposing a candidate item from the user’s stated goal. It must not invent a price, tax code, product identifier, renewal date, entitlement, subscription eligibility, refund result, or signed request.

Use a typed, reviewable route:

~~~text
user asks for help
  -> model returns a proposal containing known SKU IDs and rationale
  -> deterministic lookup verifies catalog version, storefront, availability, and price
  -> UI shows exact Apple/storefront data and side effects
  -> user explicitly confirms
  -> server validates and signs the operation
  -> StoreKit presents the system confirmation
~~~

The model must not receive a tool that can call purchase, AppStore.sync, subscription management, refund requests, or an unrestricted signing endpoint without a separate explicit user action and deterministic policy gate. If the model is unavailable, catalog search, manual comparison, and checkout must remain usable.

## Availability and release proof

Advanced Commerce documentation includes platform minimums and availability that can evolve independently of the iOS 26 SDK. Confirm the exact deployment target, API availability annotations, target platform, and App Store Connect approval in Xcode and the project’s release configuration.

| Layer | Evidence | Does not prove |
| --- | --- | --- |
| Source | Official API/source links and a typed route | Compilation or provider access. |
| Compile | Main target and server route compile with the selected SDK | Permission, approval, or live App Store behavior. |
| Unit/fixture | Catalog validation, JWS envelope, state machine, dedupe, revision pagination | Apple signature validity or real transaction. |
| Signed device | Physical device/TestFlight app presents and processes the tested flow | Production approval, all storefronts, or server reliability. |
| Sandbox | Real provider transaction, signed data, sandbox notification/API | Production timing, production metadata, or App Review. |
| Server | JWT auth, JWS verification, notifications, history/status reconciliation | A user’s actual feature use. |
| Release | App Store Connect metadata, entitlement, privacy, build, and review evidence | Universal hardware behavior or future API stability. |

## Related routes

- [Advanced Commerce catalog and checkout design](../21-design-deep-dives/90-advanced-commerce-catalog-and-checkout-design.md)
- [Advanced Commerce and server entitlement capability route](../50-capability-recipes/93-advanced-commerce-and-server-entitlement-route.md)
- [Advanced Commerce server proof matrix](../60-verification/87-advanced-commerce-server-proof-matrix.md)
- [Advanced Commerce and App Store Server recipes](../70-code-recipes/105-advanced-commerce-and-server-recipes.md)

## Sources

- [Advanced Commerce API](https://developer.apple.com/documentation/advancedcommerceapi)
- [Advanced Commerce API access and eligibility](https://developer.apple.com/in-app-purchase/advanced-commerce-api/)
- [Setting up your project for Advanced Commerce API](https://developer.apple.com/documentation/advancedcommerceapi/setting-up-your-project-for-advanced-commerce)
- [Setting up generic product identifiers](https://developer.apple.com/documentation/advancedcommerceapi/setting-up-generic-product-identifiers)
- [Creating SKUs for your In-App Purchases](https://developer.apple.com/documentation/advancedcommerceapi/creating-your-purchases)
- [Specifying prices for Advanced Commerce SKUs](https://developer.apple.com/documentation/advancedcommerceapi/prices)
- [Choosing tax codes for your SKUs](https://developer.apple.com/documentation/advancedcommerceapi/taxcodes)
- [AdvancedCommerceProduct](https://developer.apple.com/documentation/storekit/advancedcommerceproduct)
- [AdvancedCommerceProduct.PurchaseOption](https://developer.apple.com/documentation/storekit/advancedcommerceproduct/purchaseoption)
- [AdvancedCommerceProduct.PurchaseResult](https://developer.apple.com/documentation/storekit/advancedcommerceproduct/purchaseresult)
- [AdvancedCommerceProduct.purchase(compactJWS:options:)](https://developer.apple.com/documentation/storekit/advancedcommerceproduct/purchase%28compactjws%3Aoptions%3A%29)
- [AdvancedCommerceProduct.currentEntitlements](https://developer.apple.com/documentation/storekit/advancedcommerceproduct/currententitlements)
- [Sending Advanced Commerce API requests from your app](https://developer.apple.com/documentation/storekit/sending-advanced-commerce-api-requests-from-your-app)
- [Generating JWS to sign App Store requests](https://developer.apple.com/documentation/storekit/generating-jws-to-sign-app-store-requests)
- [App Store Server API](https://developer.apple.com/documentation/appstoreserverapi)
- [Creating API keys to authorize API requests](https://developer.apple.com/documentation/appstoreserverapi/creating-api-keys-to-authorize-api-requests)
- [Generating JSON Web Tokens for API requests](https://developer.apple.com/documentation/appstoreserverapi/generating-json-web-tokens-for-api-requests)
- [Simplifying your implementation by using the App Store Server Library](https://developer.apple.com/documentation/appstoreserverapi/simplifying-your-implementation-by-using-the-app-store-server-library)
- [Get Transaction History](https://developer.apple.com/documentation/appstoreserverapi/get-transaction-history)
- [HistoryResponse](https://developer.apple.com/documentation/appstoreserverapi/historyresponse)
- [revision](https://developer.apple.com/documentation/appstoreserverapi/revision)
- [Get All Subscription Statuses](https://developer.apple.com/documentation/appstoreserverapi/get-all-subscription-statuses)
- [StatusResponse](https://developer.apple.com/documentation/appstoreserverapi/statusresponse)
- [Identifying rate limits](https://developer.apple.com/documentation/appstoreserverapi/identifying-rate-limits)
- [App Store Server Notifications](https://developer.apple.com/documentation/appstoreservernotifications)
- [Enabling App Store Server Notifications](https://developer.apple.com/documentation/appstoreservernotifications/enabling-app-store-server-notifications)
- [App Store Server Notifications V2](https://developer.apple.com/documentation/appstoreservernotifications/app-store-server-notifications-v2)
- [Receiving App Store Server Notifications](https://developer.apple.com/documentation/appstoreservernotifications/receiving-app-store-server-notifications)
- [Responding to App Store Server Notifications](https://developer.apple.com/documentation/appstoreservernotifications/responding-to-app-store-server-notifications)
- [responseBodyV2](https://developer.apple.com/documentation/appstoreservernotifications/responsebodyv2)
- [notificationType](https://developer.apple.com/documentation/appstoreservernotifications/notificationtype)
- [subtype](https://developer.apple.com/documentation/appstoreservernotifications/subtype)
- [signedDate](https://developer.apple.com/documentation/appstoreservernotifications/signeddate)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Human Interface Guidelines: In-app purchase](https://developer.apple.com/design/human-interface-guidelines/in-app-purchase)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
