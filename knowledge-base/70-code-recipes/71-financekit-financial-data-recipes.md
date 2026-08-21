# FinanceKit financial-data and Wallet-order code recipes

These are target-oriented Swift sketches for a named iPhone app and, where noted, a FinanceKit background delivery extension. They are not claimed to compile in this documentation-only workspace and they do not prove managed-entitlement assignment, regional eligibility, user consent, financial-data freshness, extension delivery, Wallet behavior, or release readiness.

Read the [FinanceKit capability route](../50-capability-recipes/59-financekit-financial-data-route.md), [framework deep dive](../42-framework-deep-dives/36-financekit-financial-data-and-wallet-orders.md), [financial-data design guide](../21-design-deep-dives/56-financial-data-and-wallet-review-design.md), and [proof matrix](../60-verification/53-financekit-financial-data-proof-matrix.md) first.

## Recipe 1: Check availability and request authorization

Request access after the app has explained scope and fallback. Availability and authorization are separate checks.

~~~swift
import FinanceKit
import Foundation

@MainActor
final class FinanceAccessModel: ObservableObject {
    @Published private(set) var state = "Not connected"
    private let store = FinanceStore.shared

    func connect() {
        Task {
            do {
                guard FinanceStore.isDataAvailable(.financialData) else {
                    state = "Financial data is unavailable on this device."
                    return
                }

                let current = try await store.authorizationStatus()
                _ = current

                let result = try await store.requestAuthorization()
                _ = result

                let afterRequest = try await store.authorizationStatus()
                _ = afterRequest
                state = "Ready to query selected financial data."
            } catch {
                state = "FinanceKit authorization could not be completed."
            }
        }
    }
}
~~~

The exact AuthorizationStatus cases should be handled in the selected SDK. Keep denied, restricted, unavailable, and not-yet-requested states separate in the app model.

## Recipe 2: Query bounded accounts

Use an AccountQuery with an explicit limit and sort. Keep the result in a source projection rather than exposing raw framework values throughout the UI.

~~~swift
import FinanceKit
import Foundation

struct FinanceAccountSnapshot: Sendable, Identifiable {
    let id: UUID
    let label: String
    let kind: String
}

func loadAccounts(
    from store: FinanceStore = .shared
) async throws -> [FinanceAccountSnapshot] {
    let query = AccountQuery(
        sortDescriptors: [],
        predicate: nil,
        limit: 100,
        offset: 0
    )

    let accounts = try await store.accounts(query: query)
    return accounts.map { account in
        // Map the concrete Account enum cases for the target SDK.
        // Preserve the opaque source identifier and source provenance.
        FinanceAccountSnapshot(
            id: account.id,
            label: "Selected account",
            kind: String(describing: account)
        )
    }
}
~~~

This sketch leaves the concrete Account enum mapping visible because the product should choose the fields it actually needs. Do not turn an opaque account ID into a bank account number or log it as a user identifier.

## Recipe 3: Query transactions with explicit bounds

Bound transaction queries by sort, predicate, limit, and offset. Use a selected account or time-range policy before calling the store.

~~~swift
import FinanceKit
import Foundation

struct TransactionProjection: Sendable, Identifiable {
    let id: UUID
    let accountID: UUID
    let amount: Decimal
    let currencyCode: String
    let transactionDate: Date
    let postedDate: Date?
    let originalDescription: String
    let displayDescription: String
}

func loadTransactions(
    from store: FinanceStore = .shared
) async throws -> [TransactionProjection] {
    let query = TransactionQuery(
        sortDescriptors: [],
        predicate: nil,
        limit: 200,
        offset: 0
    )

    let transactions = try await store.transactions(query: query)
    return transactions.map { transaction in
        TransactionProjection(
            id: transaction.id,
            accountID: transaction.accountID,
            amount: transaction.transactionAmount.value,
            currencyCode: transaction.transactionAmount.currencyCode,
            transactionDate: transaction.transactionDate,
            postedDate: transaction.postedDate,
            originalDescription: transaction.originalTransactionDescription,
            displayDescription: transaction.transactionDescription
        )
    }
}
~~~

Check the exact CurrencyAmount property names and decimal representation for the selected SDK. Preserve originalTransactionDescription even when a local rule or AI model proposes a friendlier display label.

## Recipe 4: Use a merchant-category predicate

FinanceKit documents predicate helpers on TransactionQuery for merchant category codes, statuses, and transaction types. Keep the selected predicate part of the feature contract.

~~~swift
import FinanceKit
import Foundation

func loadDiningTransactions(
    categoryCodes: [MerchantCategoryCode],
    from store: FinanceStore = .shared
) async throws -> [Transaction] {
    let predicate = TransactionQuery.predicate(
        forMerchantCategoryCodes: categoryCodes
    )
    let query = TransactionQuery(
        sortDescriptors: [],
        predicate: predicate,
        limit: 100,
        offset: 0
    )
    return try await store.transactions(query: query)
}
~~~

The category code is source data, not a guarantee that the merchant or purchase intent is understood. Keep the original description and let the person correct a local category.

## Recipe 5: Present TransactionPicker

FinanceKitUI’s TransactionPicker is a SwiftUI selection surface. Its binding is the person-mediated scope for the current task.

~~~swift
import FinanceKit
import FinanceKitUI
import SwiftUI

struct TransactionSelectionView: View {
    @State private var selected: [Transaction] = []

    var body: some View {
        VStack {
            TransactionPicker(selection: $selected) {
                Label(
                    "Select transactions to categorize",
                    systemImage: "checklist"
                )
            }

            Text("\(selected.count) selected")
                .accessibilityLabel(
                    "\(selected.count) transactions selected"
                )
        }
        .padding()
    }
}
~~~

Use the selected values only for the intended task. If a proposal is saved, persist source IDs and the app-owned result under an explicit retention policy.

## Recipe 6: Reconcile transaction history

FinanceStore history exposes changes from an optional HistoryToken and can monitor future changes. Use one actor to own the checkpoint and projection.

~~~swift
import FinanceKit
import Foundation

actor FinanceHistoryStore {
    private var token: FinanceStore.HistoryToken?
    private var projections: [UUID: TransactionProjection] = [:]
    private let financeStore = FinanceStore.shared

    func monitor(accountID: UUID) async {
        let history = financeStore.transactionHistory(
            forAccountID: accountID,
            since: token,
            isMonitoring: true
        )

        // History is an asynchronous source in the selected SDK.
        // Iterate its documented changes, merge by stable transaction ID,
        // persist the new token with the projection, and handle cancellation.
        _ = history
    }

    func resetCheckpoint() {
        token = nil
        projections.removeAll()
    }
}
~~~

Persist the checkpoint only after the corresponding projection is durable. If a token is invalid or the local projection is lost, perform a bounded rebaseline rather than guessing which changes were missed.

## Recipe 7: Enable background delivery

Enable only the background data types the feature needs. The frequency is a system-managed minimum interval, not a timer.

~~~swift
import FinanceKit

func enableDailyFinanceUpdates() {
    FinanceStore.shared.enableBackgroundDelivery(
        for: [
            .accounts,
            .accountBalances,
            .transactions
        ],
        frequency: .daily
    )
}

func disableFinanceUpdates() {
    FinanceStore.shared.disableAllBackgroundDelivery()
}
~~~

Call the enable/disable methods under the product’s consent and disconnect policy. Verify the exact set of background types and frequency in the target SDK.

## Recipe 8: Implement the delivery-extension protocol seam

The extension is a separate process. Keep its callback short, idempotent, and checkpointed.

~~~swift
import FinanceKit
import Foundation

struct FinanceDeliveryExtension: BackgroundDeliveryExtensionProviding {
    func didReceiveData(
        for types: [FinanceStore.BackgroundDataType]
    ) async {
        // Read the last durable token from the App Group store.
        // Query/replay only the named types, merge source IDs, persist the
        // projection and new token atomically, then return promptly.
        _ = types
    }

    func willTerminate() async {
        // Finish or checkpoint work that can be safely resumed.
    }
}
~~~

Create the actual extension target and conformance required by the selected SDK template. Do not assume a callback proves that a foreground screen refreshed or that all transactions were delivered.

## Recipe 9: Save a signed Wallet order

FinanceStore.saveOrder accepts the archive data of a valid, signed order. The signature and authoritative order values come from the trusted order pipeline.

~~~swift
import FinanceKit
import Foundation

enum WalletOrderState {
    case added
    case canceled
    case newerExisting
}

func saveWalletOrder(
    signedArchive: Data,
    from store: FinanceStore = .shared
) async throws -> WalletOrderState {
    let result = try await store.saveOrder(signedArchive: signedArchive)
    switch result {
    case .added:
        return .added
    case .cancelled:
        return .canceled
    case .newerExisting:
        return .newerExisting
    @unknown default:
        fatalError("Handle future FinanceKit order results explicitly.")
    }
}
~~~

A result of added means FinanceStore added the order. It does not mean a merchant fulfilled the order, funds settled, or a delivery completed.

## Recipe 10: Keep the Wallet button system-owned

FinanceKitUI provides AddOrderToWalletButton and AddOrderToWalletButtonStyle. Use the current SDK initializer rather than drawing a look-alike control.

~~~swift
import FinanceKitUI
import SwiftUI

struct WalletOrderAction: View {
    var body: some View {
        // Use the AddOrderToWalletButton initializer documented for the
        // selected SDK and supply the current signed-order action.
        VStack(alignment: .leading, spacing: 12) {
            Text("Add your order to Apple Wallet")
            Text("The system will show the Wallet confirmation surface.")
                .font(.footnote)
        }
    }
}
~~~

The system-owned button/surface should remain distinct from app-owned Liquid Glass review cards. Show the validated order summary before the action and reconcile the result afterward.

## Recipe 11: Redact a financial projection for AI

Pass only the minimum source-linked projection to an on-device model.

~~~swift
struct AITransactionInput: Sendable {
    let sourceID: UUID
    let amount: Decimal
    let currencyCode: String
    let transactionDate: Date
    let merchantLabel: String?
}

struct CategoryProposal: Sendable {
    let sourceIDs: [UUID]
    let category: String
    let explanation: String
    let confidence: Double?
}

func makeAIInput(
    from transaction: TransactionProjection
) -> AITransactionInput {
    AITransactionInput(
        sourceID: transaction.id,
        amount: transaction.amount,
        currencyCode: transaction.currencyCode,
        transactionDate: transaction.transactionDate,
        merchantLabel: transaction.displayDescription
    )
}
~~~

Do not pass account identifiers, unrelated transaction history, access tokens, or full original descriptions unless the task requires them. A proposal must retain source IDs so the app can revalidate before apply.

## Recipe 12: Validate a category proposal

The model proposes; deterministic code validates; the person confirms.

~~~swift
struct CategoryCatalog {
    let allowed: Set<String>
}

enum ProposalValidationError: Error {
    case noSourceRecords
    case unknownCategory
    case sourceChanged
}

func validate(
    proposal: CategoryProposal,
    currentSourceIDs: Set<UUID>,
    catalog: CategoryCatalog
) throws {
    guard !proposal.sourceIDs.isEmpty else {
        throw ProposalValidationError.noSourceRecords
    }
    guard catalog.allowed.contains(proposal.category) else {
        throw ProposalValidationError.unknownCategory
    }
    guard Set(proposal.sourceIDs).isSubset(of: currentSourceIDs) else {
        throw ProposalValidationError.sourceChanged
    }
}
~~~

Never let a model write a balance, modify the source transaction, authorize a payment, or produce a signed Wallet order. Save only an app-owned categorization after confirmation.

## Recipe 13: Model freshness and scope

Expose the last successful source refresh and the selected scope in the view model.

~~~swift
struct FinanceFreshness: Sendable, Equatable {
    let lastSuccessfulRefresh: Date?
    let selectedAccountCount: Int
    let selectedRangeDescription: String
    let isStale: Bool
}

enum FinanceViewState: Equatable {
    case manual
    case connecting
    case emptyScope(FinanceFreshness)
    case loading(FinanceFreshness)
    case ready(FinanceFreshness)
    case stale(FinanceFreshness)
    case failed(String, FinanceFreshness?)
}
~~~

Do not replace stale or unavailable source data with a synthetic zero or an AI guess.

## Recipe 14: Disconnect and delete derived data

Disconnect must cover the app, extension, and derived proposal stores.

~~~swift
actor FinanceDeletionCoordinator {
    func disconnect() async {
        FinanceStore.shared.disableAllBackgroundDelivery()
        await deleteDerivedProjections()
        await deleteAIProposals()
        await deleteHistoryCheckpoints()
    }

    private func deleteDerivedProjections() async {
        // Remove only the app-owned projection and source-linked derivatives.
    }

    private func deleteAIProposals() async {
        // Remove generated labels, summaries, and embeddings if retained.
    }

    private func deleteHistoryCheckpoints() async {
        // Remove App Group tokens/checkpoints that no longer have a source.
    }
}
~~~

Coordinate with the product’s data policy. Disabling background delivery does not automatically delete every previously stored app-owned record.

## Recipe 15: Unit-test financial math independently

Keep source parsing and financial math deterministic and independent of the framework.

~~~swift
struct Money: Equatable, Sendable {
    let amount: Decimal
    let currencyCode: String
}

enum MoneyError: Error {
    case mixedCurrencies
}

func sum(_ values: [Money]) throws -> Money {
    guard let first = values.first else {
        return Money(amount: 0, currencyCode: "XXX")
    }
    guard values.allSatisfy({ $0.currencyCode == first.currencyCode }) else {
        throw MoneyError.mixedCurrencies
    }
    let total = values.reduce(Decimal.zero) { $0 + $1.amount }
    return Money(amount: total, currencyCode: first.currencyCode)
}
~~~

Run this kind of test with fixed currency/date fixtures. It does not prove FinanceKit authorization, source freshness, or regional availability.

## Recipe 16: Redacted diagnostics

Log lifecycle and counts, not financial content.

~~~swift
struct FinanceDiagnostic: Sendable {
    let phase: String
    let dataType: String
    let recordCount: Int
    let refreshAgeSeconds: Int?
    let result: String
}

func logFinance(_ event: FinanceDiagnostic) {
    // Use Logger or an approved diagnostic sink.
    // Never add merchant text, amount, account ID, order archive, or
    // user identity to a normal log message.
    _ = event
}
~~~

Keep any server/provider diagnostics in an access-controlled, redacted path with a documented retention period.

## Sources

- [FinanceKit](https://developer.apple.com/documentation/financekit)
- [FinanceStore](https://developer.apple.com/documentation/financekit/financestore)
- [FinanceStore.DataType](https://developer.apple.com/documentation/financekit/financestore/datatype)
- [FinanceStore.BackgroundDataType](https://developer.apple.com/documentation/financekit/financestore/backgrounddatatype)
- [FinanceStore.UpdateFrequency](https://developer.apple.com/documentation/financekit/financestore/updatefrequency)
- [FinanceStore.SaveOrderResult](https://developer.apple.com/documentation/financekit/financestore/saveorderresult)
- [AccountQuery](https://developer.apple.com/documentation/financekit/accountquery)
- [TransactionQuery](https://developer.apple.com/documentation/financekit/transactionquery)
- [Transaction](https://developer.apple.com/documentation/financekit/transaction)
- [AccountBalance](https://developer.apple.com/documentation/financekit/accountbalance)
- [transactions(query:)](https://developer.apple.com/documentation/financekit/financestore/transactions%28query%3A%29)
- [TransactionPicker](https://developer.apple.com/documentation/financekitui/transactionpicker)
- [TransactionPicker initializer](https://developer.apple.com/documentation/financekitui/transactionpicker/init%28selection%3Alabel%3A%29)
- [FinanceKitUI](https://developer.apple.com/documentation/financekitui)
- [AddOrderToWalletButton](https://developer.apple.com/documentation/financekitui/addordertowalletbutton)
- [FinancialConnectionUIExtension](https://developer.apple.com/documentation/financekitui/financialconnectionuiextension)
- [BackgroundDeliveryExtension](https://developer.apple.com/documentation/financekit/backgrounddeliveryextension)
- [BackgroundDeliveryExtensionProviding](https://developer.apple.com/documentation/financekit/backgrounddeliveryextensionproviding)
- [Enable background delivery](https://developer.apple.com/documentation/financekit/financestore/enablebackgrounddelivery%28for%3Afrequency%3A%29)
- [Save an order](https://developer.apple.com/documentation/financekit/financestore/saveorder%28signedarchive%3A%29)
- [Get started with FinanceKit](https://developer.apple.com/financekit/)
- [FinanceKit entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.financekit)
- [NSFinancialDataUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsfinancialdatausagedescription)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
