# Advanced Commerce and App Store Server proof matrix

This matrix separates what documentation, compilation, fixtures, a signed physical device, Apple sandbox, server evidence, and release evidence can prove. Advanced Commerce is a gated commerce path, so local StoreKit testing and an attractive Liquid Glass preview are not provider proof.

## Evidence ladder

| ID | Boundary | Minimum evidence | Not enough |
| --- | --- | --- | --- |
| AC-01 | Access/eligibility | App-specific Advanced Commerce approval or documented access status, generic IDs, review notes | A StoreKit import or a generic product string. |
| AC-02 | SDK/API | Named iOS 26 target compiles AdvancedCommerceProduct initialization and purchase call | A Markdown snippet or autocomplete. |
| AC-03 | Catalog | Server catalog fixture validates SKU, generic ID, revision, storefront, price, tax, period, and availability | A hard-coded card or AI output. |
| AC-04 | Intent | Typed client intent is authenticated and server revalidated | Accepting arbitrary client price/SKU/signing payload. |
| AC-05 | JWS request | Server generates the documented compact JWS and app receives a short-lived envelope over secure transport | A client-side private key or a mocked token. |
| AC-06 | StoreKit result | Signed device/sandbox run records pending, cancelled, verified, unverified, and thrown-error paths | A button animation or one happy-path callback. |
| AC-07 | Device entitlement | Physical signed target reads AdvancedCommerceProduct.currentEntitlements and applies policy | Simulator or fixture access. |
| AC-08 | Server API auth | Server generates JWT with correct key/bundle/environment and calls the matching Apple endpoint | A decoded JWT without Apple response. |
| AC-09 | JWS verification | Server validates outer/nested Apple JWS with Apple’s library or equivalent documented path | Base64-decoding a payload and trusting it. |
| AC-10 | Notifications | Apple test notification reaches V2 endpoint, server validates/dedupes, and returns 200–206 | A local POST with 200 response. |
| AC-11 | Notification recovery | Notification history and current transaction/subscription status repair a missed or stale event | Assuming notifications are an ordered database. |
| AC-12 | History | Production/sandbox history is paginated with stable filters and revision, and signed transactions are persisted | One page or a fake revision. |
| AC-13 | Delivery | Transaction/SKU idempotency record produces one durable delivery result | Granting on every notification. |
| AC-14 | Subscription | Current status, renewal state, expiry, revocation/refund, and management route are proved | A transaction existing in history. |
| AC-15 | Accessibility | VoiceOver, Dynamic Type, increased contrast, reduced transparency/motion, RTL, keyboard/pointer, and long localized values tested | A preview screenshot or color inspection. |
| AC-16 | AI boundary | Proposal contains only known SKU IDs; deterministic validator and explicit user review are recorded | A model answer that says “buy this.” |
| AC-17 | Release | Signed archive/TestFlight/App Review metadata, privacy, server environment, and tested provider flow are recorded | Local build, simulator, or sandbox alone. |

## Source and configuration checks

- [ ] Apple’s current Advanced Commerce access/eligibility guidance was reviewed.
- [ ] Generic product IDs are configured in App Store Connect and linked to the approved app.
- [ ] The app-owned SKU catalog is versioned and has one stable identity per purchasable item.
- [ ] The setup’s subscription group, placeholder localization, availability, tax codes, and payment-sheet image match the current Apple documentation.
- [ ] The in-app subscription-management deep link is configured and tested as a real route.
- [ ] A refund request path is present and documented for the target.
- [ ] Current App Store Server API and Notifications V2 endpoints were selected from Apple documentation rather than copied from a deprecated V1 example.
- [ ] TLS 1.2 or later is enforced at the server boundary.
- [ ] App Store Connect private keys are stored only on the server/secret manager and are absent from the repo, client bundle, logs, and screenshots.

## App compile and state checks

Compile the smallest named target containing:

- AdvancedCommerceProduct(id:);
- AdvancedCommerceProduct.purchase(compactJWS:options:);
- AdvancedCommerceProduct.PurchaseOption and its available storefront option;
- Product.PurchaseResult handling;
- current entitlement observation;
- server request envelope validation;
- native SwiftUI loading, pending, unavailable, and recovery UI.

Record the exact SDK, deployment target, platform, target membership, and availability warnings. Confirm the request method and result types in the selected iOS 26 SDK; documentation and SDK signatures can change independently.

Test the state table:

| State | Expected app behavior | Evidence |
| --- | --- | --- |
| Catalog loading | Disable duplicate purchase and show progress/context | UI test or signed device. |
| Missing SKU | Show configuration/unavailable state; never invent price | Unit + UI fixture. |
| Signed request expired | Discard, refresh, and retry | Unit + server integration. |
| StoreKit pending | No final access grant; wait for updates/server evidence | Sandbox/device. |
| User cancelled | Preserve catalog and explain no change | Sandbox/device. |
| Verified transaction | Verify, deliver idempotently, update projection, finish at the selected boundary | Sandbox/device + server ledger. |
| Unverified transaction | No new paid access; retain support/retry | Fixture + sandbox/device. |
| Notification delayed | Reconcile through history/current status | Server integration. |
| Revoke/refund/expiry | Remove or suspend access according to policy | Sandbox scenario/production-approved test. |
| Account switch | Clear/reload account-scoped projection and avoid cross-account leakage | Signed device + server. |

## Server JWS/JWT checks

Record safe identifiers, not raw secrets:

~~~text
bundle ID:
app Apple ID:
generic product IDs:
server environment:
key ID reference:
JWT audience:
JWS audience:
request reference ID:
catalog revision:
Apple transaction ID:
notification UUID:
signed date:
history revision:
verification result:
delivery result:
~~~

Prove that:

- App Store Server API JWTs use the correct ES256 key, claims, audience, bundle, and environment;
- Advanced Commerce in-app JWS uses the correct audience and request claim;
- the app never receives an App Store Connect private key;
- the server validates envelope expiry, account, generic ID, SKU, revision, and operation;
- the server rejects altered, replayed, cross-bundle, cross-environment, and wrong-operation artifacts;
- raw JWS/JWT values are not logged or stored beyond the declared need;
- key rotation and revocation have a runbook.

## Notification proof

Apple’s V2 notification body has an outer signed payload and may include nested signed transaction/renewal information. Test:

1. Request an Apple test notification for the selected environment.
2. Confirm the V2 endpoint receives the HTTPS POST.
3. Verify the outer JWS and any nested JWS values.
4. Confirm notificationUUID dedupe.
5. Confirm the event is durably accepted before a success response when that is the server’s contract.
6. Confirm a transient failure returns a retryable status.
7. Confirm a duplicate notification is safe.
8. Confirm a newer signedDate wins according to the transaction ordering policy.
9. Confirm notification history and current-status/history APIs can recover a missed event.

Do not claim “real-time entitlement” from a notification alone. Apple documents notification payloads as signed snapshots and provides current transaction/subscription APIs for current state and recovery.

## History and current-status proof

For Get Transaction History:

- start without revision;
- persist and verify up to 20 signed transactions per response;
- follow hasMore with the returned revision;
- keep the same query filters on subsequent revision requests;
- handle refunds, revocations, finished consumables, and updated transactions;
- store the final revision only when the selected sort/persistence policy supports incremental reuse;
- use production or sandbox URL matching the transaction’s environment.

For Get All Subscription Statuses:

- use an Apple transaction/account identifier accepted by the endpoint;
- map group status and signed renewal information into the app projection;
- show active, grace, retry, expired, and revoked states as distinct policy outcomes;
- reconcile conflicting notification snapshots with current endpoint data;
- record rate-limit and retry behavior.

## Advanced Commerce testing limitation

Apple’s current Advanced Commerce access page says purchases handled by Advanced Commerce cannot use StoreKit Testing in Xcode, and also lists current App Store limitations such as subscription offers and Family Sharable In-App Purchases. Therefore:

| Test environment | Can prove | Cannot prove |
| --- | --- | --- |
| Unit/fixture | Catalog validation, state machine, request envelope, dedupe, UI mapping | Apple provider signature/payment. |
| Xcode StoreKit Test | Ordinary StoreKit test scenarios where supported | Advanced Commerce provider purchase behavior. |
| Apple sandbox | Approved Advanced Commerce purchase, signed transaction, sandbox server APIs/notifications | Production metadata, production timing, App Review, all storefronts. |
| TestFlight physical device | Signed target, app-server transport, system confirmation, account/device behavior | Production approval or universal hardware coverage. |
| Production | Real approved app/provider/account/server operation | Future API behavior or all users without monitoring. |

Keep the limitation in test reports so a future maintainer does not mistake a normal .storekit fixture for an Advanced Commerce proof.

## Accessibility, Liquid Glass, and AI proof

Record task-level evidence for:

- VoiceOver reading SKU, included content, price, term, state, and action in order;
- Voice Control/Switch Control targeting purchase, restore/recovery, manage, refund/support, and retry;
- Dynamic Type and long localized prices without clipping;
- reduced transparency, increased contrast, and reduced motion preserving all state distinctions;
- RTL and keyboard/pointer/focus behavior where supported;
- glass effects remaining app-owned and not obscuring StoreKit/system surfaces;
- AI proposals constrained to current catalog IDs, with a deterministic validator and explicit user confirmation;
- model-unavailable fallback to manual catalog search and checkout.

## Release packet

~~~text
app / bundle ID / App Store ID:
target / SDK / deployment target / device family:
Advanced Commerce access status:
generic product IDs / subscription group:
catalog schema and revision:
server environment and URL:
notification V2 endpoint and test-notification ID:
App Store Server API/JWS library/version:
safe key ID reference and rotation date:
sandbox device/account/build:
transaction ID / original transaction ID:
notification UUID / signedDate:
history revision / status query:
delivery/idempotency record:
subscription management/refund path:
accessibility/localization settings:
AI proposal validation record:
known unproved claims and current API limitations:
~~~

Use precise claims:

- “The sandbox physical-device run received a verified Advanced Commerce transaction and the server recorded one idempotent delivery.”
- “The server accepted Apple’s V2 test notification, verified the JWS, deduplicated the UUID, and returned a success status.”
- “The local fixture covered pending/unverified UI mapping; it did not prove provider behavior.”
- “The archive includes no App Store Connect private key.”

Avoid:

- “The simulator proves Advanced Commerce works.”
- “A 200 response proves the customer owns the item.”
- “Notification received means entitlement is current.”
- “The model picked the right product, so purchase can proceed automatically.”

## Related routes

- [Advanced Commerce API and App Store Server deep dive](../42-framework-deep-dives/69-advanced-commerce-api-and-app-store-server.md)
- [Advanced Commerce catalog and checkout design](../21-design-deep-dives/90-advanced-commerce-catalog-and-checkout-design.md)
- [Advanced Commerce and server entitlement capability route](../50-capability-recipes/93-advanced-commerce-and-server-entitlement-route.md)
- [Advanced Commerce and App Store Server recipes](../70-code-recipes/105-advanced-commerce-and-server-recipes.md)

## Sources

- [Advanced Commerce API access and eligibility](https://developer.apple.com/in-app-purchase/advanced-commerce-api/)
- [Advanced Commerce API](https://developer.apple.com/documentation/advancedcommerceapi)
- [Setting up your project for Advanced Commerce API](https://developer.apple.com/documentation/advancedcommerceapi/setting-up-your-project-for-advanced-commerce)
- [Setting up generic product identifiers](https://developer.apple.com/documentation/advancedcommerceapi/setting-up-generic-product-identifiers)
- [AdvancedCommerceProduct](https://developer.apple.com/documentation/storekit/advancedcommerceproduct)
- [AdvancedCommerceProduct.PurchaseResult](https://developer.apple.com/documentation/storekit/advancedcommerceproduct/purchaseresult)
- [AdvancedCommerceProduct.purchase(compactJWS:options:)](https://developer.apple.com/documentation/storekit/advancedcommerceproduct/purchase%28compactjws%3Aoptions%3A%29)
- [Sending Advanced Commerce API requests from your app](https://developer.apple.com/documentation/storekit/sending-advanced-commerce-api-requests-from-your-app)
- [Generating JWS to sign App Store requests](https://developer.apple.com/documentation/storekit/generating-jws-to-sign-app-store-requests)
- [App Store Server API](https://developer.apple.com/documentation/appstoreserverapi)
- [Creating API keys to authorize API requests](https://developer.apple.com/documentation/appstoreserverapi/creating-api-keys-to-authorize-api-requests)
- [Generating JSON Web Tokens for API requests](https://developer.apple.com/documentation/appstoreserverapi/generating-json-web-tokens-for-api-requests)
- [Get Transaction History](https://developer.apple.com/documentation/appstoreserverapi/get-transaction-history)
- [HistoryResponse](https://developer.apple.com/documentation/appstoreserverapi/historyresponse)
- [Get All Subscription Statuses](https://developer.apple.com/documentation/appstoreserverapi/get-all-subscription-statuses)
- [App Store Server Notifications](https://developer.apple.com/documentation/appstoreservernotifications)
- [App Store Server Notifications V2](https://developer.apple.com/documentation/appstoreservernotifications/app-store-server-notifications-v2)
- [Receiving App Store Server Notifications](https://developer.apple.com/documentation/appstoreservernotifications/receiving-app-store-server-notifications)
- [Responding to App Store Server Notifications](https://developer.apple.com/documentation/appstoreservernotifications/responding-to-app-store-server-notifications)
- [responseBodyV2](https://developer.apple.com/documentation/appstoreservernotifications/responsebodyv2)
- [notificationType](https://developer.apple.com/documentation/appstoreservernotifications/notificationtype)
- [signedDate](https://developer.apple.com/documentation/appstoreservernotifications/signeddate)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
