# SwiftUI PassKit, Wallet, Apple Pay, and commerce review recipes

These are compile-oriented Swift sketches for a named iOS target. They are not claimed to compile in this documentation-only workspace and they do not prove merchant setup, provider settlement, payment-token verification, Wallet signature acceptance, FinanceKit entitlement, order updates, accessibility, physical-device behavior, or release readiness.

Read the [commerce review](../42-framework-deep-dives/104-swiftui-passkit-wallet-apple-pay-commerce-review.md), [design guide](../21-design-deep-dives/132-swiftui-passkit-wallet-apple-pay-commerce-review-design.md), [route](../50-capability-recipes/135-swiftui-passkit-wallet-apple-pay-commerce-review-route.md), and [proof matrix](../60-verification/129-swiftui-passkit-wallet-apple-pay-commerce-review-proof-matrix.md) first. Verify every API shape, availability annotation, entitlement, certificate, provider contract, and framework import against the target SDK.

## Recipe 1: Keep cart and commerce state app-owned

Do not make a PassKit object the durable domain model.

~~~swift
import Foundation

struct CommerceOrder: Codable, Hashable, Sendable {
    enum State: String, Codable, Sendable {
        case draft
        case ready
        case unavailable
        case presenting
        case canceled
        case authorized
        case providerPending
        case providerAccepted
        case providerDeclined
        case fulfillmentPending
        case fulfilled
        case refunded
    }

    let orderID: String
    let cartRevision: String
    let currencyCode: String
    let totalMinorUnits: Int
    var state: State
    var providerTransactionID: String?
    var walletOrderIdentifier: String?
    var lastServerRevision: String?
}
~~~

Never store raw payment data, pass authentication tokens, signing keys, or private certificates in this record.

## Recipe 2: Model Apple Pay availability narrowly

Availability tells the app which route to offer. It does not prove identity, provider capture, or complete Wallet contents.

~~~swift
import PassKit

struct ApplePayAvailability: Equatable, Sendable {
    let deviceCanPay: Bool
    let matchingNetworkAvailable: Bool

    var route: Route {
        if !deviceCanPay { return .unsupported }
        if !matchingNetworkAvailable { return .setupOrAlternate }
        return .ready
    }

    enum Route: Sendable {
        case unsupported
        case setupOrAlternate
        case ready
    }
}

func applePayAvailability(
    networks: [PKPaymentNetwork]
) -> ApplePayAvailability {
    ApplePayAvailability(
        deviceCanPay: PKPaymentAuthorizationController.canMakePayments(),
        matchingNetworkAvailable:
            PKPaymentAuthorizationController.canMakePayments(
                usingNetworks: networks
            )
    )
}
~~~

Compile the exact availability APIs in the target and test unsupported, setup, and ready states on the intended device family.

## Recipe 3: Build a PKPaymentRequest from a cart snapshot

Use the same deterministic calculation that renders the app-owned total.

~~~swift
import PassKit

struct PaymentRequestInput: Sendable {
    let merchantIdentifier: String
    let countryCode: String
    let currencyCode: String
    let total: Decimal
    let label: String
    let networks: [PKPaymentNetwork]
}

func makePaymentRequest(
    from input: PaymentRequestInput
) -> PKPaymentRequest {
    let request = PKPaymentRequest()
    request.merchantIdentifier = input.merchantIdentifier
    request.countryCode = input.countryCode
    request.currencyCode = input.currencyCode
    request.supportedNetworks = input.networks
    request.merchantCapabilities = [.capability3DS]
    request.paymentSummaryItems = [
        PKPaymentSummaryItem(
            label: input.label,
            amount: NSDecimalNumber(decimal: input.total),
            type: .final
        )
    ]
    return request
}
~~~

The merchant identifier must match the target’s signed Merchant IDs entitlement. Add shipping, contact, coupon, applicationData, and order details only when the product has a current validated need.

## Recipe 4: Wrap the system Apple Pay button

Use the system-provided button rather than drawing a fake Apple Pay control.

~~~swift
import PassKit
import SwiftUI

struct ApplePayButton: UIViewRepresentable {
    let type: PKPaymentButtonType
    let style: PKPaymentButtonStyle
    let action: () -> Void

    func makeCoordinator() -> Coordinator {
        Coordinator(action: action)
    }

    func makeUIView(context: Context) -> PKPaymentButton {
        let button = PKPaymentButton(
            paymentButtonType: type,
            paymentButtonStyle: style
        )
        button.addTarget(
            context.coordinator,
            action: #selector(Coordinator.tapped),
            for: .touchUpInside
        )
        return button
    }

    func updateUIView(
        _ button: PKPaymentButton,
        context: Context
    ) {}

    final class Coordinator: NSObject {
        let action: () -> Void

        init(action: @escaping () -> Void) {
            self.action = action
        }

        @objc func tapped() {
            action()
        }
    }
}
~~~

Confirm the target’s current PassKit button and SwiftUI integration. Keep the button visible and put the app-owned amount and state beside it.

## Recipe 5: Retain an authorization-controller coordinator

The delegate receives system interactions and completion handlers. Keep it alive until the controller finishes.

~~~swift
import PassKit

@MainActor
final class ApplePayCoordinator: NSObject,
    PKPaymentAuthorizationControllerDelegate {

    private var controller: PKPaymentAuthorizationController?
    private var order: CommerceOrder?
    private let submit: @MainActor (PKPayment, CommerceOrder) async
        -> ProviderResult

    enum ProviderResult: Sendable {
        case accepted(transactionID: String)
        case pending
        case declined
    }

    init(
        submit: @escaping @MainActor (PKPayment, CommerceOrder) async
            -> ProviderResult
    ) {
        self.submit = submit
    }

    func present(
        request: PKPaymentRequest,
        order: CommerceOrder
    ) async -> Bool {
        guard let controller = PKPaymentAuthorizationController(
            paymentRequest: request
        ) else {
            return false
        }
        self.controller = controller
        self.order = order
        controller.delegate = self
        return await withCheckedContinuation { continuation in
            controller.present { presented in
                continuation.resume(returning: presented)
            }
        }
    }

    func paymentAuthorizationControllerDidFinish(
        _ controller: PKPaymentAuthorizationController
    ) {
        self.controller = nil
        self.order = nil
    }
}
~~~

Add the full delegate methods for shipping, payment method, coupon, merchant session, and authorization in the target SDK. Treat the finish callback as controller lifecycle, not fulfillment.

## Recipe 6: Submit an authorized payment without exposing token data

Pass the payment to a narrow provider adapter and return a state that the app can reconcile.

~~~swift
import PassKit

struct ProviderPaymentEnvelope: Sendable {
    let orderID: String
    let cartRevision: String
    let paymentData: Data
    let transactionIdentifier: String
}

func envelope(
    payment: PKPayment,
    order: CommerceOrder
) -> ProviderPaymentEnvelope {
    let token = payment.token
    return ProviderPaymentEnvelope(
        orderID: order.orderID,
        cartRevision: order.cartRevision,
        paymentData: token.paymentData,
        transactionIdentifier: token.transactionIdentifier
    )
}
~~~

The real implementation must use the provider’s secure transport, redact logs, bind the order revision, and handle idempotency. Do not treat this local envelope as a verified transaction.

## Recipe 7: Make provider and fulfillment states explicit

Do not turn one provider callback into a permanent “paid” Boolean.

~~~swift
enum OrderReconciliation: Sendable, Equatable {
    case authorizationReceived
    case providerPending
    case providerAccepted
    case providerDeclined
    case fulfillmentPending
    case fulfilled
    case refunded
    case duplicate
    case needsReview
}

struct ProviderEvent: Sendable {
    let orderID: String
    let providerTransactionID: String
    let state: OrderReconciliation
    let providerRevision: String
}
~~~

Persist the event and domain projection atomically. A retry with the same provider transaction ID should not fulfill twice.

## Recipe 8: Attach real order details after authorization

Use a real order service identity, not a model-generated placeholder.

~~~swift
import PassKit

func makeOrderDetails(
    orderTypeIdentifier: String,
    orderIdentifier: String,
    webServiceURL: URL,
    authenticationToken: String
) -> PKPaymentOrderDetails {
    PKPaymentOrderDetails(
        orderTypeIdentifier: orderTypeIdentifier,
        orderIdentifier: orderIdentifier,
        webServiceURL: webServiceURL,
        authenticationToken: authenticationToken
    )
}
~~~

Keep the authentication token in the Wallet order service boundary and validate the service URL, order identity, and current provider state before using the object.

## Recipe 9: Model a Wallet pass identity

Pass type and serial number are identity data, not display copy.

~~~swift
struct WalletPassIdentity: Codable, Hashable, Sendable {
    let passTypeIdentifier: String
    let serialNumber: String
    let issuerRevision: String
    let expiresAt: Date?
}

enum WalletPassState: Sendable, Equatable {
    case missing
    case downloaded
    case readyToAdd(WalletPassIdentity)
    case added(WalletPassIdentity)
    case alreadyPresent(WalletPassIdentity)
    case updateAvailable(WalletPassIdentity)
    case expired(WalletPassIdentity)
    case failed(String)
}
~~~

Do not use a customer name or local database ID as the only pass identity. Validate the server’s signed identity against the app’s intended record.

## Recipe 10: Parse a signed pass from data

The app can inspect a received pass before presenting it, but the server owns signing.

~~~swift
import PassKit

func parsePass(
    data: Data
) throws -> PKPass {
    try PKPass(data: data)
}
~~~

The exact initializer and error behavior should be compiled in the target. A non-throwing parse or a local object does not prove Wallet will accept the certificate, signature, fields, entitlements, or distribution environment.

## Recipe 11: Present Add to Wallet in SwiftUI

Use the current SwiftUI AddPassToWalletButton when the target supports it.

~~~swift
import PassKit
import SwiftUI

struct AddPassAction: View {
    let pass: PKPass
    @State private var added = false

    var body: some View {
        AddPassToWalletButton([pass]) { didAdd in
            added = didAdd
        }
        .addPassToWalletButtonStyle(.blackOutline)
        .accessibilityValue(added ? "Added" : "Ready to add")
    }
}
~~~

Display an explicit fallback when no signed pass exists. When the pass is already present, show a view/open-in-Wallet action rather than repeating an add affordance.

## Recipe 12: Bridge PKAddPassesViewController for older or UIKit-specific paths

Keep the controller visible and delegate-owned.

~~~swift
import PassKit
import SwiftUI

struct AddPassViewController: UIViewControllerRepresentable {
    let pass: PKPass
    let onFinish: () -> Void

    func makeCoordinator() -> Coordinator {
        Coordinator(onFinish: onFinish)
    }

    func makeUIViewController(
        context: Context
    ) -> PKAddPassesViewController {
        let controller = PKAddPassesViewController(pass: pass)!
        controller.delegate = context.coordinator
        return controller
    }

    func updateUIViewController(
        _ controller: PKAddPassesViewController,
        context: Context
    ) {}

    final class Coordinator: NSObject,
        PKAddPassesViewControllerDelegate {
        let onFinish: () -> Void

        init(onFinish: @escaping () -> Void) {
            self.onFinish = onFinish
        }

        func addPassesViewControllerDidFinish(
            _ controller: PKAddPassesViewController
        ) {
            onFinish()
        }
    }
}
~~~

The exact initializer and optional return should be checked against the target SDK. The finish callback does not by itself tell the app whether the person added every pass.

## Recipe 13: Isolate PKPassLibrary access

PKPassLibrary is not thread-safe. Give it one owner and expose only a projection.

~~~swift
import PassKit

@MainActor
final class WalletLibraryModel: ObservableObject {
    @Published private(set) var passes: [WalletPassIdentity] = []
    private let library = PKPassLibrary()

    func refresh() {
        guard PKPassLibrary.isPassLibraryAvailable() else {
            passes = []
            return
        }

        passes = library.passes.compactMap { pass in
            guard
                let passTypeIdentifier = pass.passTypeIdentifier,
                let serialNumber = pass.serialNumber
            else {
                return nil
            }
            return WalletPassIdentity(
                passTypeIdentifier: passTypeIdentifier,
                serialNumber: serialNumber,
                issuerRevision: "observed",
                expiresAt: pass.expirationDate
            )
        }
    }
}
~~~

Confirm the current Swift property names and optionals in the target. The returned list is entitlement-scoped, not the full Wallet.

## Recipe 14: Represent a pass-service update contract

Keep pass updates server-owned and versioned.

~~~swift
struct PassUpdateContract: Codable, Sendable {
    let passTypeIdentifier: String
    let serialNumber: String
    let serverRevision: String
    let lastUpdated: String
    let updateService: URL
    let productionPush: Bool
}

enum PassUpdateResult: Sendable {
    case noChange
    case updated(serverRevision: String)
    case unauthorized
    case invalidPass
    case retryable
}
~~~

The service should authenticate the pass/device request, return only allowed serials, provide a newly signed pass, and remove invalid device registrations according to Apple’s documented service. Never place the pass authentication token in UI logs.

## Recipe 15: Model a Wallet order package

Keep the order service projection separate from the app’s cart.

~~~swift
struct WalletOrderProjection: Codable, Sendable, Equatable {
    enum Status: String, Codable, Sendable {
        case open
        case completed
        case canceled
    }

    let orderTypeIdentifier: String
    let orderIdentifier: String
    let createdAt: Date
    let updatedAt: Date
    let status: Status
    let statusDescription: String
    let serverRevision: String
    let signedArchiveRevision: String
}
~~~

Validate monotonic updatedAt and stable identifiers before building a signed order archive. The archive is not the source of provider settlement; it is a signed Wallet presentation of an authoritative order.

## Recipe 16: Save a signed order with FinanceStore

FinanceKit accepts a signed archive, not an arbitrary JSON object.

~~~swift
import FinanceKit

@MainActor
func saveSignedOrder(
    archive: Data,
    store: FinanceStore
) async -> Result<FinanceStore.SaveOrderResult, Error> {
    do {
        return .success(
            try await store.saveOrder(signedArchive: archive)
        )
    } catch {
        return .failure(error)
    }
}
~~~

Confirm the current FinanceKit entitlement, target availability, and result cases in the selected SDK. Store only the app-owned result/revision needed for reconciliation.

## Recipe 17: Use FinanceKitUI for an order handoff

Use the system-style button for an already-signed order path.

~~~swift
import FinanceKitUI
import SwiftUI

struct WalletOrderButton: View {
    let signedArchive: Data
    @State private var message = "Ready"

    var body: some View {
        AddOrderToWalletButton(signedArchive: signedArchive) { result in
            switch result {
            case .success:
                message = "Order submitted to Wallet"
            case .failure:
                message = "Wallet order was not added"
            }
        }
        .addOrderToWalletButtonStyle(.blackOutline)
        .accessibilityValue(message)
    }
}
~~~

The exact initializer and result shape must be checked in the target SDK. The button does not create or sign the archive and does not prove fulfillment.

## Recipe 18: Keep AI proposals typed and reviewable

Use model output only as a proposal over a validated source projection.

~~~swift
struct CommerceProposal: Sendable, Equatable {
    let sourceOrderID: String
    let sourceRevision: String
    let modelRevision: String
    let title: String
    let explanation: String
    let suggestedPassLabel: String?
    let requiresReview: Bool
}

func validateProposal(
    _ proposal: CommerceProposal,
    currentOrder: CommerceOrder
) -> Bool {
    proposal.requiresReview
        && proposal.sourceOrderID == currentOrder.orderID
        && !proposal.sourceRevision.isEmpty
        && !proposal.modelRevision.isEmpty
}
~~~

Re-read the order/pass projection immediately before applying an approved label, summary, or system action. The model must never provide the amount, merchant identifier, token, signature, order archive, or fulfillment truth.

## Recipe 19: Compose a native Liquid Glass checkout shell

Glass belongs around app-owned context and actions.

~~~swift
import SwiftUI

struct CommerceShell<Content: View>: View {
    let title: String
    @ViewBuilder let content: () -> Content

    var body: some View {
        NavigationStack {
            content()
                .navigationTitle(title)
                .toolbar {
                    ToolbarItem(placement: .topBarTrailing) {
                        Button("Help", systemImage: "questionmark.circle") {
                            // Present app-owned support/recovery.
                        }
                        .buttonStyle(.glass)
                    }
                }
        }
    }
}
~~~

Verify the exact Liquid Glass API and availability in the target. Never place a custom translucent layer over the system payment sheet or use a glass checkmark to imply provider fulfillment.

## Recipe 20: Record a commerce evidence packet

Keep proof structured and redacted.

~~~swift
struct CommerceEvidence: Codable, Sendable {
    let target: String
    let build: String
    let device: String
    let merchantEnvironment: String
    let providerRevision: String?
    let passRevision: String?
    let walletOrderRevision: String?
    let modelRevision: String?
    let checks: [Check]

    struct Check: Codable, Sendable {
        let name: String
        let result: String
        let artifact: String
        let recordedAt: Date
    }
}
~~~

Do not serialize paymentData, pass authentication tokens, certificate private material, full financial records, or personal contact data into the evidence packet.

## Recipe 21: Test the failure matrix

~~~text
[ ] StoreKit versus Apple Pay route is selected correctly
[ ] Merchant ID does not match entitlement
[ ] Unsupported device/network has an alternate path
[ ] Cart revision changes invalidate stale requests
[ ] Shipping/coupon callback returns exactly once
[ ] User cancels the payment sheet
[ ] Provider times out, declines, duplicates, or accepts
[ ] Authorization is not shown as fulfillment
[ ] Payment data never appears in logs
[ ] Invalid or unsigned pass is rejected
[ ] Pass add is canceled, already present, expired, or unavailable
[ ] Pass update service returns no-change, updated, and unauthorized
[ ] Wallet order archive is invalid, duplicate, newer, or canceled
[ ] FinanceKitUI is unavailable or not entitled
[ ] AI proposal has stale source revision and requires re-review
[ ] Dynamic Type, VoiceOver, contrast, reduced effects, keyboard, pointer,
    Voice Control, and Switch Control work
[ ] Archive/TestFlight/release entitlements match the local target
~~~

## Sources

- [PassKit](https://developer.apple.com/documentation/passkit)
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
- [PKAddPassesViewControllerDelegate](https://developer.apple.com/documentation/passkit/pkaddpassesviewcontrollerdelegate)
- [AddPassToWalletButton](https://developer.apple.com/documentation/passkit/addpasstowalletbutton)
- [Wallet Passes](https://developer.apple.com/documentation/walletpasses)
- [Creating the Source for a Pass](https://developer.apple.com/documentation/walletpasses/creating-the-source-for-a-pass)
- [Building a Pass](https://developer.apple.com/documentation/walletpasses/building-a-pass)
- [Distributing and updating a pass](https://developer.apple.com/documentation/walletpasses/distributing-and-updating-a-pass)
- [Adding a Web Service to Update Passes](https://developer.apple.com/documentation/WalletPasses/adding-a-web-service-to-update-passes)
- [Wallet Orders](https://developer.apple.com/documentation/walletorders)
- [Order](https://developer.apple.com/documentation/WalletOrders/Order)
- [FinanceKit](https://developer.apple.com/documentation/FinanceKit)
- [FinanceKitUI](https://developer.apple.com/documentation/FinanceKitUI)
- [AddOrderToWalletButtonStyle](https://developer.apple.com/documentation/financekitui/addordertowalletbuttonstyle)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
