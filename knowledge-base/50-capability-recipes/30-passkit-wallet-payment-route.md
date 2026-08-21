# PassKit, Wallet, and Apple Pay route

Use this recipe when an app needs to accept a real-world payment, issue a Wallet pass, or connect a successful order to Wallet. Keep StoreKit separate for digital goods and subscriptions consumed in the app.

The route is:

    user goal
        -> authoritative order/pass domain record
        -> app-owned review
        -> capability and availability preflight
        -> system authorization or add-pass UI
        -> provider/server/pass-service completion
        -> receipt, Wallet state, notification, or fulfillment

## Choose the narrowest route

| Requirement | Use | Do not substitute |
| --- | --- | --- |
| Buy a physical good or service | PassKit Apple Pay | StoreKit or a fake local “paid” flag |
| Buy digital content or a subscription in the app | StoreKit 2 | Apple Pay |
| Add a ticket, card, coupon, or membership | Wallet Passes + PassKit | A custom QR screen alone |
| Track a placed Apple Pay order in Wallet | PKPaymentOrderDetails + order service | Treating a payment token as a receipt |
| Read or manage app-accessible passes | PKPassLibrary | Assuming the app owns the whole Wallet library |
| Pair a pass with an App Clip | Wallet distribution + App Clip | Requiring the full app for every add flow |

The [PassKit documentation](https://developer.apple.com/documentation/passkit), [Wallet Passes documentation](https://developer.apple.com/documentation/walletpasses), and [Setting up Apple Pay](https://developer.apple.com/documentation/PassKit/setting-up-apple-pay) are the current source of truth for API, account, certificate, and capability details.

## Domain state before framework state

Keep the business record independent from PassKit objects:

~~~swift
struct OrderRecord: Codable, Hashable, Sendable {
    enum PaymentState: String, Codable, Sendable {
        case draft
        case unavailable
        case ready
        case sheetPresented
        case authorized
        case providerPending
        case providerAccepted
        case providerDeclined
        case fulfillmentPending
        case fulfilled
        case canceled
    }

    var id: String
    var currencyCode: String
    var totalMinorUnits: Int
    var paymentState: PaymentState
    var walletOrderIdentifier: String?
    var passIdentifier: String?
    var passSerialNumber: String?
    var lastProviderUpdate: Date?
}

struct PassRecord: Codable, Hashable, Sendable {
    enum State: String, Codable, Sendable {
        case notDownloaded
        case downloaded
        case readyToAdd
        case addReview
        case added
        case alreadyPresent
        case updateAvailable
        case expired
        case unavailable
        case failed
    }

    var passTypeIdentifier: String
    var serialNumber: String
    var displayName: String
    var state: State
    var lastKnownServerVersion: String?
}
~~~

Do not persist a payment token, pass authentication token, signing secret, or private certificate in this domain object. Keep those values in the narrowest server or framework boundary that needs them.

## Route A: Apple Pay

### A1. Configure the target and merchant

Before writing the payment sheet:

1. Register the merchant identifier.
2. Create the Payment Processing certificate.
3. Add the Apple Pay capability to the app target.
4. Choose a processor or merchant server for token processing.
5. Decide whether the order is physical goods, a service, a donation, or another supported real-world purchase.
6. Define the provider response and fulfillment states.

Record the merchant environment, supported networks, country/currency, shipping/contact fields, and sandbox/test account plan. A request that compiles without the correct merchant capability is not an Apple Pay integration.

### A2. Preflight and render the correct action

Use the current PKPaymentAuthorizationController availability APIs to determine whether the device can make payments and whether the supported networks can be used. Keep “can set up a card” separate from “ready to authorize this order.”

The app-owned view should render:

    unavailable -> alternate checkout
    setup possible -> system setup/payment action
    ready -> PKPaymentButton

Use the current HIG guidance for Apple Pay button placement and primary-payment behavior. Do not make a generic glass button look like Apple Pay.

### A3. Construct the request from a frozen order

Build PKPaymentRequest from a server-validated or locally deterministic order snapshot:

- merchantIdentifier;
- merchantCapabilities;
- countryCode and currencyCode;
- supportedNetworks;
- paymentSummaryItems;
- shipping methods and shipping type when relevant;
- required contact fields when relevant;
- coupon behavior only when the selected SDK/target supports it.

If a person changes shipping, contact, or coupon information in the sheet, recalculate the order and return the appropriate PassKit error or updated summary. Keep the app’s authoritative order and the sheet’s displayed total aligned.

### A4. Treat authorization as a server handoff

The delegate receives PKPayment after the person authorizes. Validate request-dependent information, send the encrypted token to the provider/server, and return a PKPaymentAuthorizationResult that matches the actual provider state.

Use a conservative state machine:

    ready
        -> presenting
        -> authorized
        -> providerPending
        -> providerAccepted
        -> fulfillmentPending
        -> fulfilled

Failure states should include unavailable, canceled, invalid contact, provider declined, provider timeout, duplicate order, and fulfillment failure. Do not show “paid” merely because the delegate callback fired.

### A5. Connect the order to Wallet only after placement

If the order is genuinely placed and the selected integration supports Wallet order details, attach PKPaymentOrderDetails to the successful authorization result. The order service should use its own identifier and scoped authentication token, then publish current order status through the documented service.

Keep “order placed”, “payment captured”, “fulfillment started”, and “delivered” as separate domain transitions. Wallet is a projection of the order; it is not the order database.

## Route B: Wallet pass

### B1. Produce a signed pass

The pass build service owns:

    pass source
        -> pass.json and assets
        -> manifest.json
        -> PKCS #7 detached signature
        -> .pkpass
        -> distribution

Use a registered Pass Type ID and a unique serial number. Keep the private signing material out of the app. Select a style that matches the real use case and include text fields for important information.

### B2. Download and validate the pass at the app boundary

The app can download a .pkpass, initialize PKPass from its data, and hand the signed object to the system add-pass route. Validate:

- expected content type and download size;
- server response and certificate/TLS policy;
- pass type identifier and serial number;
- app-owned order/member/event association;
- expiration or cancellation status;
- whether the pass is already present;
- the user-facing display name and purpose.

Treat a failed PKPass initializer or a server mismatch as a pass error, not as an opportunity to bypass signing.

### B3. Use the system add flow

For one pass, present PKAddPassesViewController with the signed pass. For multiple passes, use PKPassLibrary.addPasses when the current target and SDK support the chosen overload. Handle:

- the pass was added;
- the person should review passes;
- the person canceled;
- the system could not add the pass;
- the pass was already in the library.

A successful add callback proves the selected system action completed for that attempt. It does not prove that the pass is current, that a venue will honor it, or that another device has the same state.

### B4. Model updates and removals

For updateable passes, include the documented web service URL and authentication token in the pass. The server stores device/pass registrations, sends update pushes, responds to changed-serial requests, and returns a newly signed pass. The pass identifier and serial number identify the pass across versions.

Use PKPassLibrary for the app’s allowed pass scope and keep access on one isolation path because the class is not thread-safe. If the person removes a pass, reconcile app-owned status without re-adding it silently. If the server revokes a pass, explain the consequence and follow current Wallet/pass guidance.

## Route C: order and receipt projection

For a commerce app that wants an Apple-native receipt:

1. Create an app-owned order with a stable identifier.
2. Build a valid Apple Pay request.
3. Process the token through the provider/server.
4. Return success only when the merchant state is appropriate.
5. Attach PKPaymentOrderDetails for a placed order when configured.
6. Let the Wallet order service publish current details.
7. Show the app’s own receipt and support route as well.

Use the same order identifier across app, provider, pass/order service, notifications, and support, but do not expose secret authentication tokens in logs or URLs visible to users.

## Route D: AI-assisted purchase or pass generation

For a private on-device assistant:

    user request
        -> model extracts candidate product/pass data
        -> typed validation
        -> current catalog/order/pass lookup
        -> user reviews amount, recipient, dates, and action
        -> app constructs request
        -> PassKit authorization/add UI
        -> server/provider completion

Good model output:

- a draft cart;
- a normalized event title;
- a suggested generic-pass field;
- a receipt line-item extraction;
- a likely order lookup;
- a localized explanation for the review screen.

Blocked model output:

- a final money total without deterministic calculation;
- an invented merchant or pass identifier;
- direct use of signing credentials;
- auto-authorizing Apple Pay;
- auto-adding or removing a pass;
- claiming provider acceptance or fulfillment;
- using card availability as identity proof.

## Fallback and failure route

Every route needs a visible fallback:

| Failure | Fallback |
| --- | --- |
| Device or network does not support Apple Pay | Alternate supported checkout or save draft |
| No provisioned card | Explain setup or alternate payment method |
| Merchant capability/configuration missing | Disable payment action and log configuration failure |
| Provider timeout | Preserve order draft and show pending/retry status |
| Payment declined | Allow correction or alternate method; do not discard order context |
| Pass download fails | Retry signed download; do not build an unsigned local pass |
| Pass already present | Open/view the existing pass or show current server state |
| Add pass canceled | Return to a stable detail screen with no error masquerading as success |
| Pass update unavailable | Show last-known version and server freshness |
| Wallet service revoked/stale | Explain the pass status and offer support or reissue flow |
| AI unavailable | Use deterministic catalog, manual entry, or existing order search |

## Minimum implementation slices

### Slice 1: fixture-only UI

Build a checkout/pass-detail screen with fake domain states, but label all actions as fixtures. Verify hierarchy, Dynamic Type, VoiceOver, localization, reduced effects, and error recovery.

### Slice 2: request construction

Compile the target with PassKit, construct a PKPaymentRequest from a fixed order, and log only non-sensitive request metadata. Verify merchant capability and availability on the chosen target.

### Slice 3: sandbox provider route

Add the merchant configuration and provider/server handoff. Exercise success, decline, invalid contact, cancellation, timeout, duplicate-order, and fulfillment-pending states on a supported physical device where required.

### Slice 4: signed pass route

Generate a real .pkpass with a registered Pass Type ID, download it over the intended distribution path, present the system add flow, and record add/review/cancel outcomes.

### Slice 5: updates and Wallet projection

Add the pass update web service or order service. Verify registration, push/update, same-identifier replacement, stale state, revocation, and multi-device behavior separately.

## Verification questions before calling it ready

- Which route is this: Apple Pay, StoreKit, Wallet pass, Wallet order, or a combination?
- Is the product selling physical goods/services or digital content?
- Is the merchant identifier/certificate/capability configured in the exact app target?
- Is the payment processor/server response mapped to the domain state?
- Is the pass genuinely signed and built with a registered Pass Type ID?
- Are add/review/cancel/already-present states handled?
- Are pass updates owned by the documented web-service path?
- Is the system UI real, or only a local preview?
- Can the user understand the amount, identity scope, and consequence before authorization?
- Can VoiceOver, Dynamic Type, reduced transparency, and localization complete the task?
- Does AI stop at a typed, user-reviewed proposal?
- Which exact evidence proves the claim on a physical device and in the selected sandbox/release environment?

## Sources

- [PassKit](https://developer.apple.com/documentation/passkit)
- [Wallet Passes](https://developer.apple.com/documentation/walletpasses)
- [Setting up Apple Pay](https://developer.apple.com/documentation/PassKit/setting-up-apple-pay)
- [Offering Apple Pay in Your App](https://developer.apple.com/documentation/passkit/offering-apple-pay-in-your-app)
- [Apple Pay HIG](https://developer.apple.com/design/human-interface-guidelines/apple-pay)
- [Wallet HIG](https://developer.apple.com/design/human-interface-guidelines/wallet)
- [PKPaymentAuthorizationController](https://developer.apple.com/documentation/passkit/pkpaymentauthorizationcontroller)
- [PKPaymentAuthorizationControllerDelegate](https://developer.apple.com/documentation/passkit/pkpaymentauthorizationcontrollerdelegate)
- [PKPaymentRequest](https://developer.apple.com/documentation/passkit/pkpaymentrequest)
- [PKPaymentSummaryItem](https://developer.apple.com/documentation/passkit/pkpaymentsummaryitem)
- [PKPaymentAuthorizationResult](https://developer.apple.com/documentation/passkit/pkpaymentauthorizationresult)
- [PKPaymentToken](https://developer.apple.com/documentation/passkit/pkpaymenttoken)
- [PKPaymentOrderDetails](https://developer.apple.com/documentation/passkit/pkpaymentorderdetails)
- [PKPaymentButton](https://developer.apple.com/documentation/passkit/pkpaymentbutton)
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
