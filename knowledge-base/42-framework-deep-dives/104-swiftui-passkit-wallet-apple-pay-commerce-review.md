# SwiftUI PassKit, Wallet, Apple Pay, and commerce review

This review focuses on the current SwiftUI composition boundary around PassKit, Wallet, Apple Pay, Wallet Orders, and FinanceKitUI. It complements the earlier [PassKit, Wallet, and Apple Pay deep dive](14-passkit-wallet-and-apple-pay.md), [PassKit capability route](../50-capability-recipes/30-passkit-wallet-payment-route.md), and [PassKit proof matrix](../60-verification/24-passkit-wallet-payment-proof-matrix.md) by tracing one end-to-end commerce record through app-owned review, system authorization, provider/server fulfillment, signed Wallet artifacts, and post-purchase system surfaces.

It is not a payment processor, a Wallet-pass signing service, a PCI implementation, a digital-goods entitlement guide, or proof that any merchant, card network, region, device, certificate, provider, sandbox account, or production service is configured.

## The route is a set of authorities

PassKit is a family of system-owned commerce and Wallet routes. Start by naming the authority for each fact:

| Fact or outcome | Primary authority | App-owned projection | Proof boundary |
| --- | --- | --- | --- |
| The person wants to buy a physical good or service | App order/cart | Cart and order snapshot | Deterministic order fixture |
| Apple Pay is available | PassKit/device/system | Availability state | Named-device check |
| The person authorized the payment request | Apple Pay system sheet and PassKit delegate | Authorization state | System-sheet run |
| The provider processed the token | Merchant/provider/server | Provider result | Sandbox/production provider evidence |
| The order was accepted or fulfilled | Merchant/order service | Current order record | Server/webhook/reconciliation evidence |
| A pass can be added | Signed pass plus PassKit | Ready-to-add state | Signed pass and system add flow |
| A pass is in the user’s Wallet | Wallet and PassKit library | App-visible pass projection | Physical-device Wallet run |
| A Wallet order is current | Wallet Orders service and signed archive | Tracking/order projection | Service registration/update run |
| A financial record is available | FinanceKit and its managed authorization | Minimal financial projection | Entitlement/authorization/device evidence |
| A model suggested an action | Local model or Foundation Models | Reviewable proposal | Fixture/model revision/review evidence |

Keep these states separate:

~~~text
cart snapshot
    -> app-owned review
    -> capability and availability preflight
    -> Apple Pay system authorization
    -> encrypted payment token
    -> provider/server processing
    -> order accepted or declined
    -> fulfillment or refund
    -> optional Wallet pass or Wallet order projection
~~~

A payment sheet, PKPayment object, encrypted token, successful delegate callback, pass preview, or Wallet button result does not by itself prove capture, fulfillment, identity, pass freshness, or production delivery.

## Choose the correct commerce route

The first decision is what the person receives and where it is consumed:

| Product outcome | Route | Important boundary |
| --- | --- | --- |
| Digital content or app feature consumed in the app | StoreKit 2 | StoreKit transaction and entitlement state |
| Physical good, real-world service, donation, or eligible real-world subscription | PassKit Apple Pay | Provider settlement and fulfillment |
| Ticket, boarding pass, coupon, membership, or store card | Wallet Passes and PassKit | Signed pass artifact and user add decision |
| Track a placed order in Wallet | Wallet Orders plus payment/order service | Signed order package and update web service |
| Add an order with a SwiftUI system-style control | FinanceKitUI AddOrderToWalletButton | Signed order archive and current SDK/entitlement route |
| Read app-accessible passes | PKPassLibrary | Pass-type entitlements and limited library view |
| Sell financial products or access sensitive on-device financial data | FinanceKit | Managed entitlement, eligibility, privacy, and authorization |

Apple’s PassKit documentation explicitly separates Apple Pay and Wallet from App Store digital goods. Do not use a visually convincing Apple Pay checkout to avoid StoreKit rules for digital content, and do not turn a StoreKit entitlement into a Wallet pass unless the product has a separate pass purpose.

## Target, account, and entitlement gates

Before implementing SwiftUI composition, inspect the named target and its signed artifacts:

- PassKit, FinanceKit, FinanceKitUI, SwiftUI, and any UIKit bridge imports;
- deployment target, SDK/toolchain, platform, and intended device family;
- Apple Pay capability and the Merchant IDs entitlement;
- merchant identifier and payment-processing certificate environment;
- selected payment networks, merchant capabilities, country, and currency;
- Wallet capability and allowed Pass Type IDs;
- app identifier, team identifier, pass-type signing certificate, and server ownership;
- FinanceKit managed entitlement and its current request/eligibility boundary if orders or financial data use that framework;
- App Groups and extension membership if an order or financial background extension is included;
- privacy declarations, privacy manifest, logging policy, and support links;
- sandbox account, provider test mode, pass-service staging environment, and release environment;
- archive entitlements, provisioning, version/build, and installed device family.

The merchant identifier on a payment request must match one of the Merchant IDs in the signed entitlements. A pass type identifier and serial number must align with the signed pass and its service. A string in source, an unsigned entitlement file, or a local development build is not enough.

## Apple Pay: request, sheet, token, provider

### Availability is a route preflight

PassKit availability APIs answer narrow questions about whether the device can make payments and whether supported networks are available. They do not disclose the person’s complete Wallet, guarantee provider acceptance, or verify identity.

Model at least:

~~~text
unsupported
    -> supportedWithoutMatchingCard
    -> readyForPayment
    -> requestInvalid
    -> sheetPresenting
    -> userCanceled
    -> authorizedForProcessing
    -> providerPending
    -> providerAccepted
    -> providerDeclined
    -> orderPending
    -> fulfilled
~~~

The product can offer a setup or alternate-payment route when appropriate. Do not hide Apple Pay or label it as unavailable based on a stale Boolean. Re-run the preflight when the checkout context changes and document the exact target/device behavior.

### Build the request from a stable order snapshot

PKPaymentRequest contains merchant information, processing capabilities, country and currency, supported networks, summary items, contact requirements, shipping methods, coupon behavior, application data, and optional order details. Build it only after the app has calculated a stable cart revision:

~~~text
cart revision
    -> item prices and quantities
    -> tax, discount, and shipping policy
    -> currency and country
    -> final or pending summary items
    -> requested contact fields
    -> PKPaymentRequest
~~~

Keep the item calculation deterministic and auditable. PassKit delegate callbacks can ask the app for updated payment summary items, shipping methods, or errors when the person changes a payment method, shipping contact, shipping method, or coupon. Those handlers are asynchronous and should be answered exactly once within the product’s timeout policy.

Use final summary items when the amount is known and pending items only when the payment contract genuinely permits an amount to be finalized later. A glass total that differs from the system sheet is a trust failure even if both screens look polished.

### The system sheet owns authorization

PKPaymentAuthorizationController presents the Apple Pay sheet and calls its delegate for request updates and authorization. Retain one coordinator for the presentation lifetime and handle cancellation separately from provider failure:

~~~text
app presents request
    -> system collects or confirms payment details
    -> delegate receives authorized PKPayment or cancellation
    -> app validates request-dependent details
    -> server/provider processes encrypted payment token
    -> app returns authorization result
    -> system dismisses or keeps the sheet according to result
~~~

The delegate completion handler controls when the system can continue. The finish callback can occur after cancellation and is not the same event as provider settlement. Do not navigate to a “fulfilled” screen merely because the controller presented or a delegate callback arrived.

### The token is a provider input, not a receipt

PKPayment contains a PKPaymentToken with encrypted payment data, payment method information, and a transaction identifier. The token data is intended for the merchant or payment provider. Keep the processing boundary off the general SwiftUI view model:

- redact token data and transaction identifiers from logs;
- use the provider’s documented Apple Pay integration;
- bind the token to the app’s order ID and applicationData where supported;
- validate amount, currency, merchant, and replay/idempotency conditions on the server or provider;
- reconcile provider success, decline, timeout, refund, and duplicate delivery;
- do not store the raw token as a durable customer record unless the provider contract specifically requires it;
- never place the payment-processing private key in the app.

Apple’s payment-token reference describes signature verification, certificate chain, decryption, transaction ID, amount, currency, and applicationData checks. Treat that as a server/provider contract; a client-side JSON decode is not payment verification.

### Provider and fulfillment are separate facts

Use an explicit order state such as:

~~~text
authorized
    -> submittedToProvider
    -> providerAccepted
    -> providerDeclined
    -> providerTimedOut
    -> fulfillmentPending
    -> fulfilled
    -> refunded
~~~

When a provider is asynchronous, show “Payment authorized; confirming your order” rather than “Paid” until the merchant/order service provides the fact the product promises. Make retries idempotent by order ID and provider transaction ID. Store a server revision and last-known provider timestamp.

## Apple Pay and Wallet Orders

### Add order details at the right moment

PKPaymentOrderDetails carries an order type identifier, order identifier, web service URL, and authentication token. Apple’s documentation says the device retrieves this metadata only when the payment authorization succeeds. That makes it a bridge from a successful payment authorization to an order that Wallet can track; it is not a replacement for the order service.

Use:

~~~text
provider accepted
    -> durable order identifier
    -> PKPaymentOrderDetails
    -> successful authorization result
    -> Wallet order registration/update route
~~~

Do not fabricate an order identifier in a model proposal or attach a token that does not map to a real web service. Keep the authentication token scoped to the Wallet order service and rotate/expire it according to that service’s contract.

### Wallet Orders are signed service artifacts

The Wallet Orders documentation defines a source package, a signed and compressed order package, an order schema, app association, a web service, device registration, push notifications, and retrieval of updated versions. The Order object includes identifiers, status, timestamps, merchant, customer, line items, payment, fulfillment, return, tracking, and contact information.

Order data needs stricter revision rules than an app-only receipt:

- createdAt and updatedAt need valid, monotonic values;
- order type and identifier are stable;
- status transitions are deterministic and auditable;
- line items, totals, and fulfillment facts come from the order service;
- webServiceURL is HTTPS in production;
- authentication tokens are not user-facing content;
- the service can return a current signed package after a device update request;
- associated application identifiers point to the intended app.

Use Wallet Orders when the order deserves a system-owned tracking surface. Do not use it as a second unverified cart database.

### FinanceKit and FinanceKitUI have a separate boundary

FinanceKit can access on-device financial data, Apple Card, Apple Cash, and orders in Wallet. FinanceKitUI provides standardized SwiftUI UI such as AddOrderToWalletButton. The order route can be useful even when the app does not need the broader financial-data route, but verify the current target, entitlement, SDK availability, and product eligibility instead of assuming all FinanceKit features are interchangeable.

FinanceStore.saveOrder accepts signed archive data and returns a SaveOrderResult. The archive must be valid and signed. The SwiftUI button is a system-style handoff; its presence does not sign, validate, settle, or fulfill the order.

Keep:

~~~text
server/provider order
    -> signed order archive
    -> FinanceStore.saveOrder or system order button
    -> Wallet result
    -> order service reconciliation
~~~

If the app only needs Apple Pay order tracking, prefer the narrowest documented order path and avoid requesting unrelated financial data. If it uses FinanceKit financial data, apply its managed-entitlement, purpose-string, authorization, retention, and background-delivery rules separately.

## Wallet passes: source, signature, add, update

### The pass is built outside the SwiftUI app

Wallet Passes documentation defines a source directory with pass.json, required images, optional localizations, a manifest, and a detached signature. Building a distributable pass requires a Pass Type ID, signing certificate, manifest, PKCS #7 signature, and a .pkpass archive.

Keep these on the trusted issuer/build service:

- Pass Type ID and serial-number allocation;
- pass.json and localized content generation;
- private signing key and certificate;
- manifest and signature creation;
- version and expiration policy;
- distribution response and MIME type;
- update web service and pass registration storage.

The client can receive a signed pass, inspect a limited projection, and invoke system add UI. It must not contain the signing private key or treat a generated pass JSON object as a valid pass.

### Pass identity and update semantics

The passTypeIdentifier plus serialNumber identifies one pass. A new signed version with the same identity replaces the version in Wallet according to the documented distribution/update route. The app should keep source version and server revision separate from the pass object it last observed.

Model:

~~~text
notDownloaded
    -> downloaded
    -> signedAndValidated
    -> readyToAdd
    -> userReview
    -> added
    -> updateAvailable
    -> expiredOrVoided
~~~

Adding a pass is user-mediated. An already-present pass should offer a view/open route, not a dead “Add” button. Expired, voided, or unavailable states need explicit copy and recovery.

### Use system controls and library boundaries

Use the current system Add to Apple Wallet control or PKAddPassButton where the corresponding pass is available. Present PKAddPassesViewController or PKPassLibrary add methods for the signed pass. Add multiple passes through the documented multi-pass route when that is the actual user outcome.

PKPassLibrary is not thread-safe and returns only passes the app can access under its entitlements. It does not expose the entire Wallet. Keep a single owner, usually a main-actor adapter or a deliberately isolated serial boundary, and normalize the result into an app-owned projection.

### Update through the pass web service

An updateable pass can contain webServiceURL and authenticationToken. The documented service flow registers a device/pass relationship, sends a push notification when the pass changes, returns changed serial numbers, and returns a newly signed pass. Production updates use HTTPS and the production push environment described by Apple.

An app refresh button or a local cache invalidation is not a Wallet update. Capture registration, invalid token, no-change, updated pass, and service failure evidence separately.

## Liquid Glass and Apple-native commerce

Use Liquid Glass for the app-owned context, not to redraw Apple Pay or Wallet:

| App-owned surface | Appropriate treatment |
| --- | --- |
| Cart/order summary | Clear readable content with restrained glass action group |
| Shipping or delivery choice | Standard semantic controls; glass may group transient controls |
| Payment preflight | Native PassKit button with clear amount and terms |
| Post-authorization pending | Explicit status card with retry/help, not a celebratory completion clone |
| Pass detail before add | Pass explanation plus system Add to Wallet control |
| Wallet order tracking | Native list/detail hierarchy and current order status |
| AI proposal | Reviewable candidate with source revision and editable fields |

The payment sheet, Add to Wallet control, and Wallet app own their surfaces. Do not overlay glass that hides system chrome or imply that a custom animation is Apple Pay authorization. The current HIG guidance says to use the Apple Pay mark to communicate acceptance, not as the payment button, and to keep Apple Pay as the appropriate primary option when credentials are available.

## Accessibility, privacy, and recovery

Verify the whole task:

- VoiceOver can read item, amount, tax, shipping, status, and next action in order;
- system buttons have their documented semantic labels and purpose;
- Dynamic Type does not truncate a currency, order number, date, or error;
- reduced transparency and increased contrast preserve status and action boundaries;
- Reduce Motion does not remove the state change or the route to recovery;
- keyboard, pointer, Switch Control, Voice Control, and large hit targets work around app-owned controls;
- localized currency, dates, names, pass fields, and provider errors are readable;
- canceled sheets return focus to a stable app-owned element;
- errors distinguish unavailable, canceled, declined, pending, already present, expired, and server failure;
- locked/shared surfaces do not expose unnecessary order, contact, token, or identity information;
- logs and analytics do not retain payment data, authentication tokens, pass secrets, or private signing material.

When a route has a real-world side effect, the person should be able to see what is about to happen, what is pending, and what action remains possible.

## On-device AI proposal boundary

Good local uses include:

- summarizing a validated cart;
- drafting a receipt note;
- classifying a receipt or user-selected line items;
- proposing a pass title or order label;
- finding a matching local order;
- explaining an order status using current source fields.

The model must not be authoritative for:

- total, tax, shipping, discount, refund, or currency;
- merchant identifier, payment network, or certificate;
- payment authorization, provider settlement, or fulfillment;
- Wallet pass type ID, serial number, signed archive, or authentication token;
- a person’s complete Wallet contents or financial identity;
- adding/removing a pass or saving an order without the intended system/user route.

Carry source and revision metadata:

~~~text
validated order/pass projection
    -> local model proposal
    -> source revision and model revision
    -> person review
    -> deterministic revalidation
    -> PassKit or FinanceKitUI system action
    -> server/provider/Wallet result
~~~

## Proof-first completion rule

Close the route only when the evidence names:

- the target, SDK, deployment, device family, capabilities, and signed entitlements;
- merchant/certificate/provider or pass signing environment;
- deterministic order/currency/shipping fixtures;
- availability and alternate-payment states;
- system payment-sheet presentation and cancellation;
- token redaction and provider/server result;
- Wallet pass signature, add/review/already-present states;
- order archive validation and current service update;
- FinanceKit/FinanceKitUI entitlement and system result when used;
- AI source/model/review/revalidation;
- VoiceOver, Dynamic Type, Reduce Motion, contrast, keyboard, pointer, and privacy tasks;
- archive, TestFlight, and release metadata.

## Sources

- [PassKit](https://developer.apple.com/documentation/passkit)
- [Apple Pay](https://developer.apple.com/documentation/passkit/apple-pay)
- [Setting up Apple Pay](https://developer.apple.com/documentation/PassKit/setting-up-apple-pay)
- [Configuring Apple Pay support](https://developer.apple.com/documentation/xcode/configuring-apple-pay-support)
- [Offering Apple Pay in Your App](https://developer.apple.com/documentation/passkit/offering-apple-pay-in-your-app)
- [PKPaymentRequest](https://developer.apple.com/documentation/passkit/pkpaymentrequest)
- [PKPaymentAuthorizationController](https://developer.apple.com/documentation/passkit/pkpaymentauthorizationcontroller)
- [PKPaymentAuthorizationControllerDelegate](https://developer.apple.com/documentation/passkit/pkpaymentauthorizationcontrollerdelegate)
- [PKPayment](https://developer.apple.com/documentation/passkit/pkpayment)
- [PKPaymentToken](https://developer.apple.com/documentation/passkit/pkpaymenttoken)
- [PKPaymentSummaryItem](https://developer.apple.com/documentation/passkit/pkpaymentsummaryitem)
- [PKPaymentOrderDetails](https://developer.apple.com/documentation/passkit/pkpaymentorderdetails)
- [Payment token format reference](https://developer.apple.com/documentation/PassKit/payment-token-format-reference)
- [Apple Pay HIG](https://developer.apple.com/design/human-interface-guidelines/apple-pay)
- [Wallet](https://developer.apple.com/documentation/passkit/wallet)
- [PKPass](https://developer.apple.com/documentation/passkit/pkpass)
- [PKPassLibrary](https://developer.apple.com/documentation/passkit/pkpasslibrary)
- [PKAddPassButton](https://developer.apple.com/documentation/passkit/pkaddpassbutton)
- [PKAddPassesViewController](https://developer.apple.com/documentation/passkit/pkaddpassesviewcontroller)
- [AddPassToWalletButton](https://developer.apple.com/documentation/passkit/addpasstowalletbutton)
- [Wallet Passes](https://developer.apple.com/documentation/walletpasses)
- [Creating the Source for a Pass](https://developer.apple.com/documentation/walletpasses/creating-the-source-for-a-pass)
- [Building a Pass](https://developer.apple.com/documentation/walletpasses/building-a-pass)
- [Distributing and updating a pass](https://developer.apple.com/documentation/walletpasses/distributing-and-updating-a-pass)
- [Adding a Web Service to Update Passes](https://developer.apple.com/documentation/WalletPasses/adding-a-web-service-to-update-passes)
- [Wallet Orders](https://developer.apple.com/documentation/walletorders)
- [Order](https://developer.apple.com/documentation/WalletOrders/Order)
- [FinanceKit](https://developer.apple.com/documentation/FinanceKit)
- [FinanceStore.saveOrder](https://developer.apple.com/documentation/financekit/financestore/saveorder%28signedarchive%3A%29)
- [FinanceKitUI](https://developer.apple.com/documentation/FinanceKitUI)
- [AddOrderToWalletButtonStyle](https://developer.apple.com/documentation/financekitui/addordertowalletbuttonstyle)
- [Wallet HIG](https://developer.apple.com/design/human-interface-guidelines/wallet)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
