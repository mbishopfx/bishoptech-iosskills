# PassKit, Wallet, and Apple Pay

PassKit is not one generic checkout API. It is a family of system-owned commerce and identity-adjacent routes:

- Apple Pay authorizes a payment request for eligible physical goods, services, donations, or subscriptions.
- Wallet passes are signed artifacts that people add to the Wallet app and later use for tickets, boarding passes, coupons, store cards, memberships, and related information.
- Payment order details can connect a successful Apple Pay order to an updateable Wallet order.
- Secure Element and payment-card management are separate, higher-sensitivity routes with their own capability, entitlement, region, and device requirements.

Keep this boundary visible:

    product intent
        -> app-owned checkout or pass detail
        -> availability and configuration checks
        -> Apple system sheet or Add to Wallet flow
        -> user authorization
        -> provider/server or Wallet web-service completion
        -> app-owned receipt, pass state, or fulfillment

A payment sheet, payment token, pass preview, or add-pass callback is not by itself proof that money was captured, an order was fulfilled, a pass is current, or a user identity was verified.

## Capability map

| User outcome | Primary route | System-owned surface | Separate completion boundary |
| --- | --- | --- | --- |
| Pay for a physical product or service | PassKit Apple Pay | Apple Pay payment sheet | Payment processor or merchant server, order state, fulfillment |
| Sell digital content or app features | StoreKit | App Store purchase sheet | Verified StoreKit transaction and entitlement policy |
| Add a ticket, membership, coupon, boarding pass, or store card | Wallet Passes + PassKit | Add pass UI and Wallet | Signed pass artifact, pass web service, user-managed Wallet state |
| Show a successful order in Wallet | PKPaymentOrderDetails + Wallet order service | Wallet order/pass surface | Order web service and current fulfillment state |
| Inspect or manage app-accessible passes | PKPassLibrary | App-owned list or Wallet handoff | Entitlements, user consent, current pass library |
| Add multiple passes after one action | PKPassLibrary.addPasses | PassKit review/add UI | Per-pass result and user decision |

Apple’s [PassKit documentation](https://developer.apple.com/documentation/passkit) covers Apple Pay and Wallet in one framework, while [Wallet Passes](https://developer.apple.com/documentation/walletpasses) describes the pass source, signing, distribution, and update service as a related server-backed workflow.

## Apple Pay is a payment authorization route

### Configure the developer and merchant boundary

The documented Apple Pay setup requires:

1. A merchant identifier registered with Apple.
2. A Payment Processing certificate associated with that merchant identifier.
3. The Apple Pay capability enabled for the app target in Xcode.
4. A payment processor or merchant service that can process the encrypted payment data.

Use [Setting up Apple Pay](https://developer.apple.com/documentation/PassKit/setting-up-apple-pay) for the current account, certificate, and capability steps. Keep merchant identifiers and server credentials out of the client’s general data model. The app can carry the merchant identifier needed to construct the request, but payment-processing secrets and fulfillment authority belong on the server or with the chosen payment platform.

### Preflight availability without inventing a payment state

Before showing an Apple Pay action, check the current device and supported payment networks with the current PassKit availability APIs. Apple’s sample uses PKPaymentAuthorizationController.canMakePayments and canMakePayments(usingNetworks:). These are different questions:

- Can the device make Apple Pay payments?
- Can it make payments with the networks the product accepts?
- Does the product want to offer setup when a card is not yet provisioned?

The result should be modeled as a route state, not a Boolean that says “payment is ready”:

    unsupported
        -> supportedWithoutProvisionedCard
        -> readyForPayment
        -> presenting
        -> authorizedForProcessing
        -> providerAccepted
        -> fulfilled

The current HIG guidance says to offer Apple Pay on supported devices, use it as the primary option when the relevant credentials are available, and avoid using the Apple Pay mark as a button. See [Apple Pay in the Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/apple-pay) and [Offering Apple Pay in Your App](https://developer.apple.com/documentation/passkit/offering-apple-pay-in-your-app).

### Build a PKPaymentRequest from the order

PKPaymentRequest describes the merchant request, payment-processing capabilities, country and currency, supported networks, summary items, shipping methods, contact requirements, and optional coupon behavior. Build it from a stable order snapshot:

    cart snapshot
        -> item and tax calculation
        -> shipping/contact requirements
        -> final or pending summary items
        -> PKPaymentRequest
        -> system sheet

Payment summary items need a clear label, amount, and final or pending type. A pending amount is not a license to display an unexplained total; use it only where the amount is genuinely not known at request time. Recalculate shipping and other dynamic values through the delegate callbacks, then report errors in the format PassKit expects.

Do not use Apple Pay for virtual goods or digital content consumed in the app when StoreKit is the appropriate purchase route. The Apple Pay HIG explicitly separates physical goods and services from in-app purchase content.

### Present, authorize, and hand off

PKPaymentAuthorizationController presents the payment sheet without requiring a UIKit view controller. Its delegate receives the user-authorized PKPayment and encrypted PKPaymentToken. The delegate should:

1. Validate the request-dependent shipping/contact information.
2. Send the payment token to the server or payment provider over the selected secure channel.
3. Wait for the provider or merchant result when the integration supports it.
4. Return a success or failure PKPaymentAuthorizationResult with relevant errors.
5. Let the controller finish and then show the app-owned order state.

The payment token is payment information for processing; it is not a receipt that the merchant captured funds. Apple’s [Offering Apple Pay in Your App](https://developer.apple.com/documentation/passkit/offering-apple-pay-in-your-app) sample leaves the provider handoff as an explicit integration point. Keep the UI honest when the provider is pending, declined, timed out, or accepted but fulfillment has not completed.

### Add order details only after a successful authorization

PKPaymentOrderDetails is optional metadata for a placed order. The device retrieves the metadata only when the authorization result is successful. The object carries an order type identifier, order identifier, web service URL, and authentication token for the order service. Treat the token as a scoped secret and keep the order service responsible for current status, line items, delivery, and updates.

This creates a useful cross-system route:

    Apple Pay success
        -> PKPaymentAuthorizationResult with orderDetails
        -> Wallet order service
        -> current receipt/status/tracking in Wallet

Do not attach order details before the merchant has a meaningful placed-order identity. A successful authorization result and a final shipping/fulfillment status can be different moments.

## Wallet passes are signed, user-owned artifacts

### Build and sign outside the app

A pass is a signed bundle containing pass.json, images, optional localizations, a manifest, and a detached signature. Apple’s [Building a Pass](https://developer.apple.com/documentation/walletpasses/building-a-pass) workflow requires a Pass Type ID, a signing certificate, a manifest of source files, a PKCS #7 detached signature, and a .pkpass archive.

The server or controlled build service should own:

- pass type identifiers and serial-number allocation;
- pass.json generation;
- private signing material;
- manifest and signature generation;
- distribution headers and content type;
- versioned pass updates;
- device registration and update notifications where used.

Never ship a Pass Type ID private key or signing private key in the app. A local mock pass can help layout work, but it does not prove that Wallet accepts the signature, entitlement, certificate chain, or production distribution path.

### Choose the pass style for the action

Wallet supports boarding passes, coupons, event tickets, store cards, generic passes, and newer poster-style variants where supported. The style determines the information architecture and the system presentation. Use the pass style that matches the real task instead of drawing a custom card that merely looks like a Wallet pass.

The [Pass object documentation](https://developer.apple.com/documentation/walletpasses/pass) describes style-specific fields, identifiers, relevance, associated apps, and launch behavior. Use semantic fields and text fields together when the documentation calls for backward compatibility. Ensure that important content remains available as text rather than relying only on an image.

### Distribute through a user-started flow

Apple documents three common distribution channels:

- Add a pass from an app or App Clip.
- Download a pass or bundle from a web page.
- Attach a pass to an email.

In an app, use the system-provided PKAddPassButton when appropriate, then present PKAddPassesViewController for the signed PKPass. PKPassLibrary.addPasses can present a system UI for multiple passes. The completion status can indicate that passes were added, that the person should review them, or that the person canceled. Handle each state explicitly.

Adding a pass is a user decision. A model, background refresh, or server response can prepare a pass, but it should not silently add or remove one as if the app owns the person’s Wallet.

### Read and update only the allowed scope

PKPassLibrary exposes passes the app is entitled to access. The library is not thread-safe, so keep access on one deliberate isolation path. Distinguish:

- the pass the app just downloaded;
- whether that pass is already in Wallet;
- passes the app can read under its entitlements;
- the user’s complete Wallet contents, which the app does not automatically own;
- a current server version versus the copy already installed.

Passes cannot be edited in place on the device. To change a pass, the server creates a newly signed version with the same pass type identifier and serial number, then distributes it or uses the pass update web service. Removing a pass should follow direct user intent; do not remove a user-owned pass merely because it expired or because a server record changed.

See [PKPassLibrary](https://developer.apple.com/documentation/passkit/pkpasslibrary), [PKAddPassesViewController](https://developer.apple.com/documentation/passkit/pkaddpassesviewcontroller), and [Distributing and updating a pass](https://developer.apple.com/documentation/walletpasses/distributing-and-updating-a-pass).

### Update with the Wallet web service

An updateable pass includes a webServiceURL and authenticationToken. The documented flow is cooperative:

1. The user installs the pass.
2. The device registers the pass and sends a device identifier and push token.
3. The server stores device, pass, and registration relationships.
4. The server sends a pass-update push notification when data changes.
5. The device requests changed serial numbers.
6. The device requests a new signed pass.
7. The server returns the new pass with the same pass identifier and serial number.

Use the [Adding a Web Service to Update Passes](https://developer.apple.com/documentation/WalletPasses/adding-a-web-service-to-update-passes) guide for endpoint shape, authorization, update tags, and registration behavior. Production pass updates require HTTPS and the documented push environment. A client-side “refresh” button that fetches a new JSON object is not equivalent to a Wallet update service.

## Privacy, security, and system ownership

Payment, Wallet, and identity-adjacent surfaces need stronger boundaries than a normal local form:

- Minimize order, contact, pass, and device data in logs.
- Treat payment tokens, pass authentication tokens, merchant certificates, and signing keys as sensitive.
- Make server authority explicit: client authorization, provider processing, fulfillment, and refund/reversal are different states.
- Scope Wallet access to the pass types and features the product needs.
- Let the person add, review, keep, or remove passes through the system experience.
- Do not infer a person’s complete payment-card or Wallet state from a limited availability check.
- Use current entitlements, merchant configuration, region/device availability, and certificate state as release gates.

The Apple Pay and Wallet sheets, buttons, marks, and core pass presentation are system surfaces. The app owns the surrounding context, the order explanation, the fallback, and the post-action state. It does not own the visual design of the Apple Pay sheet or the entire Wallet app.

## On-device AI and PassKit

AI can help draft a cart summary, classify a receipt, suggest an order label, propose a pass field, or resolve a natural-language request into a candidate action. It must remain upstream of the authority boundary:

    model proposal
        -> typed validation
        -> current order/pass lookup
        -> user review
        -> PassKit/system authorization
        -> server/provider/pass-service completion

Do not allow a model to invent a merchant identifier, payment amount, pass serial number, signing token, shipping commitment, or physical fulfillment result. If the request is ambiguous, show the candidate data and ask the person to correct it. Use App Intents or a typed tool boundary only for actions whose authorization and side effects are explicit.

## Liquid Glass and Apple-native composition

The app-owned checkout or pass-detail screen can use the native SwiftUI hierarchy, semantic controls, and current Liquid Glass adoption guidance. The system payment sheet, Add Pass UI, and Wallet presentation remain system-owned:

- Use PKPaymentButton or the current system-provided Apple Pay control for payment initiation.
- Use the Add to Apple Wallet button/badge and current Wallet guidance for distribution.
- Keep the primary action readable on the background; do not put custom blur behind a system button just to imitate a screenshot.
- Group related app-owned controls with the current SwiftUI material and glass APIs only where they support hierarchy.
- Keep order status, identity, amount, and authorization state legible when transparency is reduced or contrast is increased.
- Make the post-payment result a stable semantic screen, not a transient glow that disappears before fulfillment is known.

The right Apple-like result is an original product using system-owned conventions and actual system surfaces, not a visual clone of Apple’s checkout or Wallet screens.

## Route choices for app ideas

| Idea | Start with | Add only when needed |
| --- | --- | --- |
| Physical service booking | StoreKit-independent app checkout + Apple Pay | shipping/contact callbacks, provider webhooks, order-to-Wallet |
| Event ticketing | Wallet event pass | App Clip, pass updates, relevance, barcode/NFC/venue protocol |
| Membership card | Generic or store-card pass | update service, locations, app association |
| Digital subscription | StoreKit 2 | App Intents, widgets, server entitlement sync |
| Receipt and delivery tracker | Apple Pay + PKPaymentOrderDetails | Wallet order service, Live Activity, notifications |
| AI-generated shopping assistant | Foundation Models proposal layer | typed cart, user review, Apple Pay, server fulfillment |

Start with one authoritative domain state. A local order, Apple Pay authorization, provider transaction, Wallet pass, and Live Activity can project that state, but none should be treated as interchangeable.

## Evidence boundary

| Evidence | Supports | Does not support |
| --- | --- | --- |
| API/source review | Route and documented contracts | Merchant approval, signed pass, provider processing |
| Local fixture or preview | App-owned checkout/pass detail and state rendering | Apple Pay sheet, Wallet acceptance, physical card, real pass signing |
| Simulator | UI, request construction, some authorization seams | Complete Apple Pay/card support, device hardware, provider capture |
| Signed physical device | Target capability, supported system sheet, real device/account behavior | Production merchant settlement, all regions/devices, universal pass validity |
| Sandbox/TestFlight | Selected merchant/pass integration and distribution artifact | Live settlement, every Wallet update path, App Store approval |
| Production transaction/update | Provider fulfillment or pass update for the observed order/device | Universal reliability or future certificate/service state |

Record the exact SDK, deployment target, device family, merchant environment, pass certificate/type ID, payment provider, signed entitlements, and user actions for any claim that goes beyond documentation.

## Sources

- [PassKit](https://developer.apple.com/documentation/passkit)
- [Wallet Passes](https://developer.apple.com/documentation/walletpasses)
- [Setting up Apple Pay](https://developer.apple.com/documentation/PassKit/setting-up-apple-pay)
- [Offering Apple Pay in Your App](https://developer.apple.com/documentation/passkit/offering-apple-pay-in-your-app)
- [PKPaymentAuthorizationController](https://developer.apple.com/documentation/passkit/pkpaymentauthorizationcontroller)
- [PKPaymentAuthorizationControllerDelegate](https://developer.apple.com/documentation/passkit/pkpaymentauthorizationcontrollerdelegate)
- [PKPaymentRequest](https://developer.apple.com/documentation/passkit/pkpaymentrequest)
- [PKPaymentSummaryItem](https://developer.apple.com/documentation/passkit/pkpaymentsummaryitem)
- [PKPaymentAuthorizationResult](https://developer.apple.com/documentation/passkit/pkpaymentauthorizationresult)
- [PKPaymentToken](https://developer.apple.com/documentation/passkit/pkpaymenttoken)
- [PKPaymentOrderDetails](https://developer.apple.com/documentation/passkit/pkpaymentorderdetails)
- [PKPaymentButton](https://developer.apple.com/documentation/passkit/pkpaymentbutton)
- [Apple Pay HIG](https://developer.apple.com/design/human-interface-guidelines/apple-pay)
- [Wallet HIG](https://developer.apple.com/design/human-interface-guidelines/wallet)
- [Pass](https://developer.apple.com/documentation/walletpasses/pass)
- [Building a Pass](https://developer.apple.com/documentation/walletpasses/building-a-pass)
- [Creating the Source for a Pass](https://developer.apple.com/documentation/walletpasses/creating-the-source-for-a-pass)
- [Distributing and updating a pass](https://developer.apple.com/documentation/walletpasses/distributing-and-updating-a-pass)
- [Adding a Web Service to Update Passes](https://developer.apple.com/documentation/WalletPasses/adding-a-web-service-to-update-passes)
- [Send an Updated Pass](https://developer.apple.com/documentation/walletpasses/send-an-updated-pass)
- [PKPassLibrary](https://developer.apple.com/documentation/passkit/pkpasslibrary)
- [PKAddPassesViewController](https://developer.apple.com/documentation/passkit/pkaddpassesviewcontroller)
- [PKPass](https://developer.apple.com/documentation/passkit/pkpass)
- [StoreKit](https://developer.apple.com/documentation/storekit)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
