# FinanceKit financial data, Wallet orders, and background delivery

FinanceKit is a privacy-sensitive Apple data and Wallet surface for financial management apps. It can expose eligible on-device account, balance, and transaction data with user consent; store or update signed Wallet orders; and support Apple Card, Apple Cash, Savings, and eligible open-banking data according to the current region and Apple program rules. FinanceKitUI supplies standardized controls such as TransactionPicker and AddOrderToWalletButton.

This is not a generic banking import API. Access is gated by region, app category, managed entitlement, organization-level Apple Developer account, Account Holder request, App Store distribution criteria, Info.plist disclosure, user-selected accounts and time ranges, and Apple’s review. The app still owns its domain model, reconciliation, privacy policy, financial calculations, and user-facing explanation.

Use this deep dive with the [FinanceKit capability route](../50-capability-recipes/59-financekit-financial-data-route.md), the [financial-data design guide](../21-design-deep-dives/56-financial-data-and-wallet-review-design.md), the [proof matrix](../60-verification/53-financekit-financial-data-proof-matrix.md), and the [code recipes](../70-code-recipes/71-financekit-financial-data-recipes.md).

## Boundary model

Keep these facts separate:

~~~text
app intent
-> FinanceKit availability and entitlement
-> Apple authorization and account/time-range selection
-> FinanceStore query or history stream
-> typed local projection
-> optional financial calculation
-> optional on-device AI proposal
-> person review
-> app-owned record or Wallet order handoff
~~~

| Boundary | What it proves | What it does not prove |
| --- | --- | --- |
| Managed entitlement | Apple assigned a capability to the developer account/bundle | User consent, data availability, production distribution, or accurate app behavior |
| Availability | The current device/store can expose the requested data type | The person has shared any account or the data is fresh |
| Authorization | FinanceKit accepted the app’s request and user policy | Every account, date range, or future update is available |
| Account query | A matching set of accounts was returned | An account is current, reconciled, or owned by the person outside Wallet |
| Balance/transaction query | Typed records were returned from the FinanceStore | A forecast, budget, category, or financial recommendation is correct |
| History stream | Changes can be observed from a history token or monitor | Background delivery is timely, complete, or guaranteed |
| TransactionPicker | The person selected transactions in Apple’s UI | The app may silently import unrelated financial data |
| Wallet order save | The signed order was accepted by FinanceStore | The order is fulfilled, refunded, delivered, or permanently visible |
| AI proposal | A local explanation or classification was generated | The proposal is financial advice, truth, authorization, or a transaction |

Do not collapse all of these into one isConnected or isFinanciallyReady flag.

## Availability and entitlement

Apple’s current FinanceKit start page lists region-specific requirements. At the time this tranche was researched, the page described:

- United States: iPhone with iOS 17.4 or later, with Apple Card, Apple Cash, and Savings eligibility limitations.
- United Kingdom: iPhone with iOS 18.4 or later, with open-banking availability for listed institutions.
- An organization-level Apple Developer account, Account Holder request, assigned FinanceKit managed entitlement, and a bundle-specific capability.
- An app listed in the Finance category in App Store Connect and distributed through the App Store for iPhone in the United States or United Kingdom for the documented entitlement path.
- The NSFinancialDataUsageDescription Info.plist key with a truthful explanation.

These are not permanent product guarantees. Re-open the current [Get started with FinanceKit](https://developer.apple.com/financekit/) requirements before target configuration or release. A successful iOS 26 compile does not remove Apple’s entitlement or distribution review.

The key configuration record should include:

| Field | Value |
| --- | --- |
| App target and bundle ID |  |
| App Store category |  |
| Region and supported institutions/products |  |
| Minimum OS/device |  |
| FinanceKit entitlement assignment |  |
| Signed entitlement value |  |
| NSFinancialDataUsageDescription |  |
| App Group for extension, if used |  |
| Data retention/deletion policy |  |
| Signed archive/TestFlight build |  |

## FinanceStore surface

FinanceStore is the shared entry point for authorization, availability, accounts, balances, transactions, Wallet orders, and history.

### Authorization

Check the current authorization status before building a dashboard. Request authorization at a moment when the person understands what information is needed and why.

The authorization result is not a substitute for querying the store. After authorization:

1. Check the exact data types the feature needs.
2. Query only the necessary accounts, fields, and time range.
3. Handle no shared accounts as a valid state.
4. Store the least amount of derived data required for the feature.
5. Re-check authorization and availability when the app returns from settings or a system surface.

Do not request financial access merely to make an onboarding screen look personalized.

### Accounts

AccountQuery filters accounts with sort descriptors, an optional predicate, limit, and offset. The result is an array of typed Account values that can represent asset or liability accounts. The account projection should preserve the account identifier, type, display label where present, and provenance.

Make a distinction between:

- an account the person has added to Apple Wallet;
- an account the person selected to share with the app;
- an account returned by a current query;
- a local account record retained by the app;
- an account that has changed or disappeared from a history stream.

An account identifier is an opaque value for the app’s mapping. Do not expose it as a customer-facing account number.

### Balances

AccountBalanceQuery returns balance records. AccountBalance can include available and booked balances, a currency code, current-balance status, account ID, and a balance record identifier.

Display freshness, currency, and pending/current semantics. Do not add balances from different currencies without an explicit conversion policy. Do not turn a missing available balance into zero. Keep booked, available, pending, and stale values distinct in the domain model.

### Transactions

TransactionQuery supports sort descriptors, predicates, limits, and offsets. Apple’s current documentation lists predicates for merchant category codes, statuses, and transaction types.

Transaction can include:

- account ID and transaction ID;
- credit/debit indicator;
- transaction and posted dates;
- transaction amount and currency;
- optional foreign-currency amount and exchange rate;
- optional merchant name and merchant category code;
- original and normalized descriptions;
- transaction type and status.

Preserve originalTransactionDescription alongside any cleaned or AI-generated label. A category is a proposal until the product’s deterministic rules or the person confirms it.

## History and monitoring

FinanceStore history methods return a History sequence for accounts, account balances, or transactions. The caller can provide a HistoryToken and an isMonitoring flag.

Use a token as a checkpoint, not as an assumption that every event is a complete snapshot:

~~~text
last durable token
-> request history or current query
-> iterate changes
-> validate record identity and account scope
-> merge with local projection
-> persist records and new token atomically
-> render updated state
~~~

If the process terminates during a merge, replay from the last durable token. If a token is missing, expired, invalid, or tied to a different store state, fall back to a bounded full query and rebaseline.

For a long-running task:

- isolate the history consumer in an actor or other single-owner boundary;
- cancel it when the screen or feature no longer needs updates;
- persist the checkpoint with the projection;
- avoid logging full transactions;
- reconcile duplicate or reordered updates using stable identifiers and dates;
- show a stale or updating state when the stream has not refreshed.

The system’s update is a data signal. It is not a promise that a bank has settled a transaction or that a user’s financial position is current to the second.

## FinanceKitUI

FinanceKitUI is a system-oriented UI layer:

| Surface | Use |
| --- | --- |
| TransactionPicker | Let a person choose transactions from FinanceKit with a SwiftUI label and a bound selection |
| AddOrderToWalletButton | Offer a standardized action for adding an order to Apple Wallet |
| FinancialConnectionUIExtension | Provide the extension-side authorization/connection surface when the selected FinanceKit flow requires it |

The TransactionPicker selection is person-mediated. Treat it as the approved input set for the current action, not as permanent authorization to read every transaction.

The AddOrderToWalletButton is a system-styled control. Its presence does not mean a signed order exists or that Wallet accepted it. Build the signed order server-side or in the trusted order pipeline, call FinanceStore.saveOrder, and report the resulting state separately.

FinancialConnection UI is an extension boundary. Its target, App Group, authorization request/result, and process lifetime need their own configuration and proof. Do not put financial data into a view model that assumes the main app process is always alive.

## Wallet order route

FinanceStore can save an order from a signed archive and return a SaveOrderResult. The order must be tied to an authoritative order identifier and the product’s server/provider state.

Use this sequence:

~~~text
server/provider order state
-> signed Wallet order archive
-> FinanceStore.saveOrder
-> AddOrderToWalletButton or app-owned confirmation
-> Wallet/system result
-> order service reconciliation
~~~

The signed archive is not the same as a payment token, receipt, or fulfillment record. Do not let an AI model generate the archive, signature, order identifier, or price. It can draft explanatory copy from a validated order projection.

## Background delivery extension

FinanceKit supports a Background Delivery Extension through the BackgroundDeliveryExtension and BackgroundDeliveryExtensionProviding protocols. The app enables delivery for specific FinanceStore.BackgroundDataType values and a documented update frequency. The extension receives data-change callbacks and a willTerminate callback.

Treat extension delivery as a checkpointed ingestion process:

1. Enable only the data types the app genuinely needs.
2. Share a minimal App Group store between app and extension when the architecture requires it.
3. Read the last durable token and projection.
4. Request or iterate changes within the extension lifecycle.
5. Persist data and token atomically.
6. Mark the app-facing projection stale/updating/ready.
7. Finish quickly and tolerate termination.

Background delivery does not mean a guaranteed schedule, complete data snapshot, foreground UI update, or permission bypass. Use the app’s next foreground launch to reconcile current state.

## On-device AI and financial data

FinanceKit is a strong candidate for local proposal workflows, but finance remains sensitive personal data. Keep the source layer and proposal layer separate:

~~~text
FinanceStore record
-> minimal normalized projection
-> local model classification or summary
-> typed proposal with source IDs and confidence
-> person review
-> deterministic save
~~~

Good local uses:

- group transactions into a user-defined budget category;
- explain a month-over-month change using selected records;
- draft a budget note or savings goal;
- identify duplicate-looking records for review;
- summarize a selected transaction set from TransactionPicker.

Not safe to delegate to a model:

- decide whether a transaction is fraudulent;
- invent a balance, currency conversion, or merchant;
- authorize a payment, transfer, refund, or Wallet order;
- infer an account the person did not select;
- silently upload financial data;
- give regulated financial advice or claim a guaranteed outcome;
- change a canonical transaction description without preserving the original;
- choose the FinanceKit entitlement, region, or authorization scope.

For AI prompts, minimize data by using a redacted transaction projection. Do not include full account identifiers, unnecessary descriptions, contact data, or unrelated history. Record source IDs and the model/prompt version for any proposal that the person may save.

## Liquid Glass and financial review

Use Liquid Glass for the app-owned review shell, not as a substitute for the system’s finance authorization surface:

- show the feature value and exact data scope before requesting access;
- put the current consent/availability state in a readable card;
- keep balances, transactions, stale state, and AI proposals visually distinct;
- use glass for a primary review action or compact toolbar where hierarchy benefits;
- avoid layering translucent cards over every transaction row;
- keep currency, date, merchant, and source status as semantic text;
- preserve contrast, larger text, reduced transparency, reduced motion, and VoiceOver order;
- make “disconnect,” delete, export, or stop sharing routes discoverable.

Do not use Apple Pay or Wallet marks as custom decoration. Use FinanceKitUI controls for the exact Wallet action and keep post-save/fulfillment state separate.

## Privacy and retention

Define a data inventory before calling requestAuthorization:

| Data | Needed for | Retain? | Delete when |
| --- | --- | --- | --- |
| Account projection | Dashboard grouping |  | User disconnects or account disappears |
| Balance | Current view/history |  | Retention window ends or disconnect |
| Transaction source | Review/reconciliation |  | User deletes data or retention expires |
| AI label/proposal | User-approved categorization |  | User removes it or source is deleted |
| History token | Incremental update |  | Store reset/rebaseline |
| Wallet order status | Order display |  | Order policy/retention says |

Never use financial data for unrelated advertising or identity enrichment without a separate, lawful product decision. Treat account selection and time-range selection as user-controlled scope.

## Evidence and availability language

Say:

- “FinanceKit is configured for this target.”
- “You have not shared an eligible account.”
- “The app last refreshed this data at [time].”
- “This label is a local suggestion based on selected transactions.”
- “Wallet accepted the order archive; fulfillment remains pending.”

Do not say:

- “Your bank is always synced” because background delivery is enabled.
- “This is your complete financial picture” from one query.
- “AI found fraud” from a classifier.
- “Your order is delivered” because Wallet stored the order.
- “FinanceKit works on all iPhones” from a simulator or one device.

## Sources

- [FinanceKit](https://developer.apple.com/documentation/financekit)
- [FinanceStore](https://developer.apple.com/documentation/financekit/financestore)
- [AccountQuery](https://developer.apple.com/documentation/financekit/accountquery)
- [TransactionQuery](https://developer.apple.com/documentation/financekit/transactionquery)
- [Transaction](https://developer.apple.com/documentation/financekit/transaction)
- [AccountBalance](https://developer.apple.com/documentation/financekit/accountbalance)
- [transactions(query:)](https://developer.apple.com/documentation/financekit/financestore/transactions%28query%3A%29)
- [transactionHistory(forAccountID:since:isMonitoring:)](https://developer.apple.com/documentation/financekit/financestore/transactionhistory%28foraccountid%3Asince%3Aismonitoring%3A%29)
- [accountBalanceHistory(forAccountID:since:isMonitoring:)](https://developer.apple.com/documentation/financekit/financestore/accountbalancehistory%28foraccountid%3Asince%3Aismonitoring%3A%29)
- [enableBackgroundDelivery(for:frequency:)](https://developer.apple.com/documentation/financekit/financestore/enablebackgrounddelivery%28for%3Afrequency%3A%29)
- [BackgroundDeliveryExtension](https://developer.apple.com/documentation/financekit/backgrounddeliveryextension)
- [BackgroundDeliveryExtensionProviding](https://developer.apple.com/documentation/financekit/backgrounddeliveryextensionproviding)
- [Implementing a background delivery extension](https://developer.apple.com/documentation/financekit/implementing-a-background-delivery-extension)
- [FinanceKitUI](https://developer.apple.com/documentation/financekitui)
- [TransactionPicker](https://developer.apple.com/documentation/financekitui/transactionpicker)
- [TransactionPicker initializer](https://developer.apple.com/documentation/financekitui/transactionpicker/init%28selection%3Alabel%3A%29)
- [AddOrderToWalletButton](https://developer.apple.com/documentation/financekitui/addordertowalletbutton)
- [AddOrderToWalletButtonStyle](https://developer.apple.com/documentation/financekitui/addordertowalletbuttonstyle)
- [FinancialConnectionUIExtension](https://developer.apple.com/documentation/financekitui/financialconnectionuiextension)
- [FinanceKit updates](https://developer.apple.com/documentation/updates/financekit)
- [Get started with FinanceKit](https://developer.apple.com/financekit/)
- [FinanceKit entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.financekit)
- [NSFinancialDataUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsfinancialdatausagedescription)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
