# PassKit, Wallet, and Apple Pay recipes

These are compile-oriented route sketches, not a complete payment processor or Wallet pass-signing service. Verify every API signature, availability annotation, entitlement, certificate, target, and provider contract in the selected SDK and environment before using them.

The safe layering is:

    SwiftUI app-owned state
        -> PassKit adapter
        -> system UI and user authorization
        -> provider/server or pass web service
        -> domain reconciliation

Keep signing keys, payment-processing secrets, and Wallet update authority off the client.

## Recipe 1: model payment state explicitly

~~~swift
enum PaymentState: Equatable, Sendable {
    case draft
    case unavailable(reason: String)
    case ready
    case presenting
    case authorized
    case providerPending
    case providerAccepted
    case providerDeclined(message: String)
    case fulfillmentPending
    case fulfilled
    case canceled
}

struct OrderSnapshot: Equatable, Sendable {
    var id: String
    var currencyCode: String
    var total: Decimal
    var items: [LineItem]
    var paymentState: PaymentState
}

struct LineItem: Equatable, Sendable {
    var label: String
    var amount: Decimal
}
~~~

Do not use a Boolean named isPaid as the only state. It cannot distinguish authorization, provider processing, fulfillment, refund, cancellation, or stale data.

## Recipe 2: preflight Apple Pay

~~~swift
import PassKit

struct ApplePayAvailability: Equatable, Sendable {
    var canMakePayments: Bool
    var canUseSupportedNetworks: Bool
}

func applePayAvailability(
    supportedNetworks: [PKPaymentNetwork]
) -> ApplePayAvailability {
    ApplePayAvailability(
        canMakePayments: PKPaymentAuthorizationController.canMakePayments(),
        canUseSupportedNetworks: PKPaymentAuthorizationController
            .canMakePayments(usingNetworks: supportedNetworks)
    )
}
~~~

The exact meaning of the second result and the desired setup button depend on the selected PassKit contract. Pair this with current Apple Pay HIG guidance; do not infer a provisioned card or completed payment from a single Boolean.

## Recipe 3: build a payment request from an order snapshot

~~~swift
import PassKit

enum PaymentConfiguration {
    static let merchantIdentifier = "merchant.example.app"
    static let supportedNetworks: [PKPaymentNetwork] = [
        .visa,
        .masterCard,
        .amex,
        .discover
    ]
}

func makePaymentRequest(
    order: OrderSnapshot,
    countryCode: String,
    shippingMethods: [PKShippingMethod] = []
) -> PKPaymentRequest {
    let request = PKPaymentRequest()
    request.merchantIdentifier = PaymentConfiguration.merchantIdentifier
    request.merchantCapabilities = .capability3DS
    request.countryCode = countryCode
    request.currencyCode = order.currencyCode
    request.supportedNetworks = PaymentConfiguration.supportedNetworks

    let items = order.items.map { item in
        PKPaymentSummaryItem(
            label: item.label,
            amount: NSDecimalNumber(decimal: item.amount),
            type: .final
        )
    }

    let total = PKPaymentSummaryItem(
        label: "Total",
        amount: NSDecimalNumber(decimal: order.total),
        type: .final
    )

    request.paymentSummaryItems = items + [total]
    request.shippingMethods = shippingMethods
    return request
}
~~~

The item calculation should come from the authoritative order logic. Do not let a language model or a view-local string decide the final amount.

## Recipe 4: wrap PKPaymentButton for SwiftUI

~~~swift
import PassKit
import SwiftUI

struct ApplePayButton: UIViewRepresentable {
    let type: PKPaymentButtonType
    let style: PKPaymentButtonStyle
    let action: () -> Void

    func makeUIView(context: Context) -> PKPaymentButton {
        let button = PKPaymentButton(paymentButtonType: type, paymentButtonStyle: style)
        button.addTarget(
            context.coordinator,
            action: #selector(Coordinator.didTap),
            for: .touchUpInside
        )
        return button
    }

    func updateUIView(_ button: PKPaymentButton, context: Context) {}

    func makeCoordinator() -> Coordinator {
        Coordinator(action: action)
    }

    final class Coordinator: NSObject {
        let action: () -> Void

        init(action: @escaping () -> Void) {
            self.action = action
        }

        @objc func didTap() {
            action()
        }
    }
}
~~~

If the selected SDK exposes a native SwiftUI payment control, prefer it. Otherwise this UIKit bridge keeps the system-provided control instead of recreating its mark and styling. Test its accessibility label, hit region, availability state, and placement with the current HIG.

## Recipe 5: present the Apple Pay controller

~~~swift
import PassKit

@MainActor
final class ApplePayCoordinator: NSObject, ObservableObject {
    @Published private(set) var state: PaymentState = .draft
    private var controller: PKPaymentAuthorizationController?
    private var order: OrderSnapshot?
    private var provider: PaymentProvider

    init(provider: PaymentProvider) {
        self.provider = provider
    }

    func start(order: OrderSnapshot) {
        guard state == .draft || state == .providerDeclined(message: "") else {
            return
        }

        let request = makePaymentRequest(
            order: order,
            countryCode: "US"
        )
        self.order = order
        state = .presenting

        let paymentController = PKPaymentAuthorizationController(paymentRequest: request)
        paymentController.delegate = self
        controller = paymentController
        paymentController.present { [weak self] presented in
            if !presented {
                self?.state = .unavailable(reason: "The payment sheet did not present.")
            }
        }
    }
}
~~~

The guard above is illustrative; use a real state-machine transition rather than comparing associated-value cases with a placeholder. Keep the controller strongly referenced until finish and map presentation failure separately from provider failure.

## Recipe 6: process authorization through a provider boundary

~~~swift
extension ApplePayCoordinator: PKPaymentAuthorizationControllerDelegate {
    func paymentAuthorizationController(
        _ controller: PKPaymentAuthorizationController,
        didAuthorizePayment payment: PKPayment,
        handler completion: @escaping (PKPaymentAuthorizationResult) -> Void
    ) {
        guard let order else {
            completion(PKPaymentAuthorizationResult(status: .failure, errors: nil))
            return
        }

        state = .authorized

        Task { @MainActor [weak self] in
            guard let self else { return }
            do {
                state = .providerPending
                let result = try await provider.authorize(
                    orderID: order.id,
                    token: payment.token
                )
                state = result.accepted
                    ? .providerAccepted
                    : .providerDeclined(message: result.message)

                var authorization = PKPaymentAuthorizationResult(
                    status: result.accepted ? .success : .failure,
                    errors: result.errors
                )

                if result.accepted, let orderDetails = result.orderDetails {
                    authorization.orderDetails = orderDetails
                }

                completion(authorization)
            } catch {
                state = .providerDeclined(message: "Payment could not be confirmed.")
                completion(PKPaymentAuthorizationResult(status: .failure, errors: nil))
            }
        }
    }

    func paymentAuthorizationControllerDidFinish(
        _ controller: PKPaymentAuthorizationController
    ) {
        controller.dismiss()
        self.controller = nil
    }
}
~~~

The provider call, idempotency key, token serialization, and error mapping are integration-specific. Do not log the token. Do not set success before the provider result is known. Re-check the current delegate signature and concurrency annotations in the selected SDK.

## Recipe 7: define the provider seam

~~~swift
protocol PaymentProvider: Sendable {
    func authorize(
        orderID: String,
        token: PKPaymentToken
    ) async throws -> PaymentAuthorizationResult
}

struct PaymentAuthorizationResult: Sendable {
    var accepted: Bool
    var message: String
    var errors: [Error]
    var orderDetails: PKPaymentOrderDetails?
}
~~~

A production implementation should serialize only the data required by the selected payment provider, protect transport and server credentials, use an idempotent order key, and reconcile webhooks or provider callbacks with the app’s order record.

## Recipe 8: create and present a signed Wallet pass

~~~swift
import PassKit
import SwiftUI

@MainActor
final class WalletPassCoordinator: NSObject, ObservableObject {
    @Published private(set) var state: PassRecord.State = .notDownloaded

    func preparePass(data: Data) throws -> PKPass {
        let pass = try PKPass(data: data)
        state = .readyToAdd
        return pass
    }

    func presentAddFlow(
        for pass: PKPass,
        from presenter: UIViewController
    ) {
        guard PKAddPassesViewController.canAddPasses(),
              let addController = PKAddPassesViewController(pass: pass)
        else {
            state = .unavailable
            return
        }

        state = .addReview
        addController.delegate = self
        presenter.present(addController, animated: true)
    }
}

extension WalletPassCoordinator: PKAddPassesViewControllerDelegate {
    func addPassesViewControllerDidFinish(
        _ controller: PKAddPassesViewController
    ) {
        controller.dismiss(animated: true)
        state = .added
    }
}
~~~

The pass data must be an actual signed pass from the server or controlled pass builder. A local JSON file with a .pkpass extension is only a negative test fixture. Verify whether the current SDK uses the initializer and delegate names shown here before compiling.

## Recipe 9: use the multi-pass library route

~~~swift
import PassKit

@MainActor
func addPasses(
    _ passes: [PKPass],
    library: PKPassLibrary = PKPassLibrary()
) async -> PKPassLibraryAddPassesStatus {
    await withCheckedContinuation { continuation in
        library.addPasses(passes) { status in
            continuation.resume(returning: status)
        }
    }
}

@MainActor
func reconcilePass(
    _ pass: PKPass,
    library: PKPassLibrary = PKPassLibrary()
) -> PassRecord.State {
    if library.containsPass(pass) {
        return .alreadyPresent
    }
    return .readyToAdd
}
~~~

PKPassLibrary is not thread-safe. Keep the instance and its operations on a deliberate isolation path. Handle PKPassLibraryShouldReviewPasses by presenting the individual review UI as Apple documents; do not treat the completion callback as a guarantee that every intended pass was installed.

## Recipe 10: keep Wallet updates server-owned

~~~swift
struct WalletUpdateContract: Sendable {
    var passTypeIdentifier: String
    var serialNumber: String
    var deviceLibraryIdentifier: String
    var pushToken: String
    var authenticationToken: String
}

enum WalletUpdateEndpoint {
    static func changedSerialNumbers(
        passTypeIdentifier: String,
        deviceLibraryIdentifier: String,
        previousLastUpdated: String?
    ) -> URL {
        fatalError("Construct with the server's configured base URL")
    }

    static func updatedPass(
        passTypeIdentifier: String,
        serialNumber: String
    ) -> URL {
        fatalError("Construct with the server's configured base URL")
    }
}
~~~

The Wallet device registration, push, changed-serial, and updated-pass protocol belongs on the server. Use HTTPS in production, authenticate each request with the documented pass token/device-library relationship, and return a newly signed pass with the correct content type. Do not implement the signing private key in this client target.

## Recipe 11: model an AI proposal without side effects

~~~swift
struct CommerceProposal: Codable, Hashable, Sendable {
    var productID: String?
    var orderID: String?
    var passTitle: String?
    var recipientDisplayName: String?
    var proposedAmount: Decimal?
    var explanation: String
    var expiresAt: Date
}

enum ProposalDecision {
    case rejected(reason: String)
    case needsReview(fields: [String])
    case approved
}

func validate(
    proposal: CommerceProposal,
    currentOrder: OrderSnapshot?
) -> ProposalDecision {
    guard proposal.expiresAt > Date() else {
        return .rejected(reason: "Proposal expired")
    }

    guard let currentOrder,
          proposal.proposedAmount == currentOrder.total
    else {
        return .needsReview(fields: ["amount", "order"])
    }

    return .approved
}
~~~

The model proposes. Deterministic catalog/order logic validates. The person reviews. PassKit or StoreKit owns authorization. The server/provider owns settlement and fulfillment. Keep this order even when an App Intent or model tool is the entry point.

## Recipe 12: test the claim boundary

~~~swift
struct PassKitFixture: Sendable {
    var deviceSupportsApplePay: Bool
    var hasSupportedNetwork: Bool
    var providerResult: ProviderFixture
    var passSignatureIsValid: Bool
    var passAlreadyPresent: Bool
}

enum ProviderFixture: Sendable {
    case accepted
    case declined
    case timedOut
    case malformedContact
}

func expectedPaymentState(
    fixture: PassKitFixture
) -> PaymentState {
    guard fixture.deviceSupportsApplePay else {
        return .unavailable(reason: "Unsupported fixture device")
    }
    guard fixture.hasSupportedNetwork else {
        return .unavailable(reason: "No supported network")
    }
    switch fixture.providerResult {
    case .accepted:
        return .providerAccepted
    case .declined:
        return .providerDeclined(message: "Declined fixture")
    case .timedOut:
        return .providerPending
    case .malformedContact:
        return .providerDeclined(message: "Invalid contact fixture")
    }
}
~~~

Use fixtures to test state rendering and transitions, then separately prove the real system sheet, signed pass, provider environment, Wallet update, accessibility task, and physical-device route. A fixture should never be named as if it proved production settlement or Wallet acceptance.

## Sources

- [PassKit](https://developer.apple.com/documentation/passkit)
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
- [Wallet Passes](https://developer.apple.com/documentation/walletpasses)
- [Pass](https://developer.apple.com/documentation/walletpasses/pass)
- [Building a Pass](https://developer.apple.com/documentation/walletpasses/building-a-pass)
- [Creating the Source for a Pass](https://developer.apple.com/documentation/walletpasses/creating-the-source-for-a-pass)
- [Distributing and updating a pass](https://developer.apple.com/documentation/walletpasses/distributing-and-updating-a-pass)
- [Adding a Web Service to Update Passes](https://developer.apple.com/documentation/WalletPasses/adding-a-web-service-to-update-passes)
- [Send an Updated Pass](https://developer.apple.com/documentation/walletpasses/send-an-updated-pass)
- [PKPass](https://developer.apple.com/documentation/passkit/pkpass)
- [PKPassLibrary](https://developer.apple.com/documentation/passkit/pkpasslibrary)
- [PKAddPassesViewController](https://developer.apple.com/documentation/passkit/pkaddpassesviewcontroller)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
