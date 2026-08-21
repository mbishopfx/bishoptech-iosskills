# FinanceKit financial-data and Wallet-order capability route

Use this route for an iPhone financial-management feature that reads eligible Apple Wallet account data, shows balances or transactions, receives FinanceKit background updates, lets a person pick transactions, or adds a signed order to Apple Wallet. Start with the [FinanceKit deep dive](../42-framework-deep-dives/36-financekit-financial-data-and-wallet-orders.md), the [financial-data design guide](../21-design-deep-dives/56-financial-data-and-wallet-review-design.md), the [proof matrix](../60-verification/53-financekit-financial-data-proof-matrix.md), and the [code recipes](../70-code-recipes/71-financekit-financial-data-recipes.md).

## Route selector

| Product needs to… | Route | Main boundary |
| --- | --- | --- |
| Show an aggregated finance dashboard | FinanceStore authorization plus AccountQuery and AccountBalanceQuery | Managed entitlement, region, user-selected scope, freshness |
| Analyze selected transactions | FinanceKitUI TransactionPicker | Person-mediated selection, temporary scope, source provenance |
| Query transaction history | FinanceStore TransactionQuery or transactionHistory | History token, cancellation, merge/reconciliation |
| Track updates outside the app process | BackgroundDeliveryExtension | App extension target, App Group, checkpoint, termination |
| Add a Wallet order | FinanceStore.saveOrder plus AddOrderToWalletButton | Signed archive, Wallet/system result, fulfillment state |
| Offer a financial-connection extension | FinanceKitUI financial connection APIs | Extension target, authorization request/result, App Group |
| Enrich a financial view with AI | Local typed projection plus reviewable proposal | Data minimization, no financial authorization/advice claim |

FinanceKit is not a general bank-aggregation entitlement. Check current regional requirements and Apple’s managed-entitlement request criteria before designing the production route.

## Eligibility gate

Complete this gate before implementation:

1. Confirm the product qualifies as a financial management app under Apple’s current FinanceKit criteria.
2. Confirm target is an iPhone app in a supported region and distribution path.
3. Confirm current iOS minimum and supported Wallet products/institutions.
4. Request the FinanceKit managed entitlement from an Account Holder.
5. Confirm the entitlement is assigned to the exact bundle ID.
6. Add the entitlement to the app target and verify the signed artifact.
7. Add a truthful NSFinancialDataUsageDescription value.
8. Add App Groups to app and background delivery extension when shared storage is required.
9. Define retention, disconnect, delete, and data-minimization policy.
10. Define a no-FinanceKit/manual mode before requesting user consent.

### Configuration worksheet

| Field | Value |
| --- | --- |
| App target/bundle ID |  |
| App Store category |  |
| Region | US / UK / other eligibility to verify |
| Supported Wallet products/institutions |  |
| Minimum OS/device |  |
| FinanceKit managed entitlement request |  |
| Signed com.apple.developer.financekit |  |
| NSFinancialDataUsageDescription |  |
| Background delivery extension target |  |
| App Group |  |
| Data types enabled for background delivery |  |
| Update frequency |  |
| Local retention window |  |
| Delete/disconnect behavior |  |
| AI route enabled |  |
| Wallet order server/signing owner |  |

## Architecture

Keep the protected source store separate from the local app projection:

~~~text
FinanceKitAccess
  -> AuthorizationCoordinator
     -> FinanceStore
        -> Account/Balance/Transaction adapters
           -> LocalFinancialProjection
              -> deterministic calculations
                 -> optional AIProposal
                    -> review
                       -> app-owned record or Wallet handoff
~~~

The extension has its own process:

~~~text
BackgroundDeliveryExtension
  -> App Group checkpoint/projection store
     -> history/query reconciliation
        -> app foreground refresh signal
~~~

Do not make the extension write arbitrary user-facing UI state while the app is not running. Persist a durable checkpoint and show freshness when the app returns.

## Authorization route

Use a two-step interaction:

1. App-owned scope explanation.
2. FinanceKit requestAuthorization system surface.

After the result:

- check authorizationStatus again;
- check FinanceStore.isDataAvailable for each requested data type;
- query only the selected feature’s needed records;
- handle no-account and no-transaction states;
- persist only the local projection needed for the feature;
- show a last-updated timestamp.

If the person denies access, do not immediately show the same request again. Provide manual mode and a settings/disconnect explanation.

## Account and balance route

Use AccountQuery to bound accounts by predicate, sort, limit, and offset. Use AccountBalanceQuery for the balance records needed by the screen.

The adapter should normalize:

| Source | Local projection |
| --- | --- |
| Account ID | Opaque stable local mapping key |
| Account type | Asset/liability display category |
| Account label | Localized display text, if present |
| Account balance ID | Balance provenance key |
| Currency code | Explicit display/conversion domain |
| Available/booked balance | Separate optional values |
| Current-balance state | Pending/current/unknown semantics |
| Source timestamp | Freshness indicator |

Never coerce nil available/booked values to zero. Preserve source amount and currency before any local aggregate.

## Transaction route

Use TransactionQuery for bounded snapshots:

1. Build explicit sort descriptors.
2. Add a predicate for selected merchant categories, statuses, or transaction types only when the feature needs it.
3. Set a limit and offset for a bounded screen.
4. Execute the query off the main UI update path.
5. Map each Transaction to a redacted local projection.
6. Preserve original description, normalized display label, and source identifier.
7. Reconcile duplicates and updates by stable IDs.

Use TransactionPicker when a person needs to approve the input set. Do not fetch broad history to simulate a picker.

## History route

For live or incremental views, use transactionHistory, accountHistory, or accountBalanceHistory with a durable FinanceStore.HistoryToken:

~~~text
stored checkpoint
-> history(token, isMonitoring)
-> changes
-> validate scope and IDs
-> merge projection
-> persist new checkpoint atomically
-> mark fresh
~~~

If the task is canceled, stop the consumer. If the token is invalid or the projection is corrupt, delete only the derived checkpoint and rebaseline from a bounded query.

## Background delivery route

Create a separate Background Delivery Extension target:

1. Add the extension target from the Xcode template.
2. Add App Groups to app and extension.
3. Share only the minimum checkpoint/projection data.
4. Enable selected FinanceStore.BackgroundDataType values with a documented frequency.
5. Implement didReceiveData for the extension protocol.
6. Handle willTerminate and persist before process termination.
7. Reconcile in the main app before showing the dashboard as current.
8. Disable delivery when the user disconnects or the feature is disabled.

The frequency is a system-managed preference, not a timer guarantee. The extension can be terminated. It must be idempotent and restartable.

## TransactionPicker route

Use a label that explains the task:

~~~text
Select transactions to categorize
-> person selects
-> show selected count
-> normalize source rows
-> optional local proposal
-> review
-> apply only approved changes
~~~

Do not retain unselected transactions. Do not confuse picker selection with ongoing FinanceKit authorization.

## Wallet order route

For an order:

1. Keep authoritative order state on the server/provider.
2. Create the signed order archive in the trusted order pipeline.
3. Call FinanceStore.saveOrder with the signed archive.
4. Present AddOrderToWalletButton or the relevant system surface.
5. Handle SaveOrderResult/system cancellation/error.
6. Reconcile Wallet visibility with provider order/fulfillment status.

The app cannot claim settlement, delivery, or refund from a Wallet save result. The signed archive is not a place for generated, unvalidated financial values.

## Financial connection extension

If the product needs a FinancialConnectionUIExtension:

- define the app and extension target separately;
- add the required App Group;
- model authorization request/result as extension data;
- keep the extension’s UI and process lifetime bounded;
- persist only a minimal handoff state;
- test cancellation, denial, termination, and relaunch;
- do not assume the main app view model is alive.

Verify the exact extension protocols and scene configuration against the selected SDK’s FinanceKitUI documentation.

## On-device AI route

Allowed pattern:

~~~text
user-selected FinanceKit records
-> minimal typed projection
-> local classifier/summarizer
-> proposal with source IDs
-> person review
-> deterministic write
~~~

The model can propose a category, summary, or budget note. It cannot access a broader scope than the person authorized, change source values, authorize a payment, make a fraud determination, sign a Wallet order, or claim regulated financial advice.

Use deterministic checks for:

- currency and amount math;
- date/time-zone grouping;
- duplicate IDs;
- account scope;
- source deletion;
- category validity;
- user-approved apply;
- retention and delete.

## Liquid Glass route

Use app-owned glass only for:

- the connect/review toolbar;
- a compact scope/freshness card;
- an AI proposal review action;
- a non-destructive filter or mode control.

Keep source financial values on semantic, high-contrast surfaces. Use FinanceKitUI’s own standard controls for system Wallet actions. Test increased contrast, large text, reduced transparency, and VoiceOver.

## Failure and fallback matrix

| Failure | Meaning | Fallback |
| --- | --- | --- |
| Entitlement missing | Target is not authorized for the capability | Manual mode/build configuration |
| Region/product unsupported | No eligible FinanceKit source | Manual import or local-only budget |
| Data unavailable | Current device/store lacks the requested data type | Explain and narrow feature |
| Authorization denied | Person did not grant access | Manual mode/settings |
| No accounts shared | Access exists but scope is empty | Revisit Wallet sharing |
| Partial account data | Some fields/source values are absent | Per-field unknown/stale state |
| Query error | Source read failed | Retry and preserve last-known state with timestamp |
| History token invalid | Incremental checkpoint cannot continue | Rebaseline bounded projection |
| Extension terminated | Background process ended | Resume from durable checkpoint in app |
| Wallet order rejected | Signed archive or store handoff failed | Explain; keep provider order state |
| AI unavailable | Local model cannot run | Deterministic category/manual edit |
| Source changed during review | Proposal is stale | Invalidate and rebuild from current records |

## Route completion

- [ ] Current FinanceKit eligibility and region are recorded.
- [ ] Managed entitlement is assigned to the exact bundle ID.
- [ ] Signed entitlement and NSFinancialDataUsageDescription are verified.
- [ ] User scope, account/time-range selection, and no-account state are designed.
- [ ] FinanceStore queries are bounded and preserve provenance.
- [ ] History tokens and extension checkpoints are durable and restartable.
- [ ] App Group data is minimized and deletion-aware.
- [ ] TransactionPicker is used for person-mediated selection where appropriate.
- [ ] Wallet order signing and fulfillment remain outside AI/local UI.
- [ ] AI is local, typed, source-linked, reviewable, and optional.
- [ ] Liquid Glass remains app-owned and accessible.
- [ ] Physical iPhone, system authorization, extension, Wallet, region, and release evidence are collected.

## Sources

- [FinanceKit](https://developer.apple.com/documentation/financekit)
- [FinanceStore](https://developer.apple.com/documentation/financekit/financestore)
- [AccountQuery](https://developer.apple.com/documentation/financekit/accountquery)
- [TransactionQuery](https://developer.apple.com/documentation/financekit/transactionquery)
- [Transaction](https://developer.apple.com/documentation/financekit/transaction)
- [AccountBalance](https://developer.apple.com/documentation/financekit/accountbalance)
- [Transaction history](https://developer.apple.com/documentation/financekit/financestore/transactionhistory%28foraccountid%3Asince%3Aismonitoring%3A%29)
- [Balance history](https://developer.apple.com/documentation/financekit/financestore/accountbalancehistory%28foraccountid%3Asince%3Aismonitoring%3A%29)
- [Enable background delivery](https://developer.apple.com/documentation/financekit/financestore/enablebackgrounddelivery%28for%3Afrequency%3A%29)
- [BackgroundDeliveryExtension](https://developer.apple.com/documentation/financekit/backgrounddeliveryextension)
- [BackgroundDeliveryExtensionProviding](https://developer.apple.com/documentation/financekit/backgrounddeliveryextensionproviding)
- [Implementing a background delivery extension](https://developer.apple.com/documentation/financekit/implementing-a-background-delivery-extension)
- [FinanceKitUI](https://developer.apple.com/documentation/financekitui)
- [TransactionPicker](https://developer.apple.com/documentation/financekitui/transactionpicker)
- [AddOrderToWalletButton](https://developer.apple.com/documentation/financekitui/addordertowalletbutton)
- [FinancialConnectionUIExtension](https://developer.apple.com/documentation/financekitui/financialconnectionuiextension)
- [Get started with FinanceKit](https://developer.apple.com/financekit/)
- [FinanceKit entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.financekit)
- [NSFinancialDataUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsfinancialdatausagedescription)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
