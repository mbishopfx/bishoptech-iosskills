# Financial data and Wallet review design

FinanceKit screens should feel calm, legible, and precise. Financial data is personal, often incomplete, and sometimes delayed. The design should make scope, freshness, provenance, and user control visible before it adds decoration.

Use this guide with the [FinanceKit framework deep dive](../42-framework-deep-dives/36-financekit-financial-data-and-wallet-orders.md), the [capability route](../50-capability-recipes/59-financekit-financial-data-route.md), the [proof matrix](../60-verification/53-financekit-financial-data-proof-matrix.md), and the [code recipes](../70-code-recipes/71-financekit-financial-data-recipes.md).

## Design objective

The core screen should answer four questions at a glance:

1. What data has the person shared?
2. How current is the data?
3. What is canonical source data versus an app calculation or AI suggestion?
4. What can the person review, correct, stop sharing, or delete?

Avoid a dashboard that makes every number look equally authoritative. A balance returned from FinanceKit, a locally computed trend, and an AI-generated category are different visual and semantic classes.

## Consent before connection

Do not open the system authorization surface without an app-owned explanation. The pre-consent screen should state:

- the purpose of the feature;
- the kinds of data requested;
- whether the person chooses accounts and time range in the system surface;
- what the app stores locally;
- whether data is used for optional AI categorization;
- how to disconnect and delete.

Use a compact, readable explanation. Do not put a large chart or a glass button in front of the actual scope.

### Connection screen anatomy

~~~text
Navigation title: Financial overview
  scope card
    "Accounts shared with this app"
    "Selected in Apple Wallet"
  value statement
    "See balances and transactions in one place"
  primary action
    Connect financial data
  privacy action
    What we store and how to disconnect
  manual fallback
    Add a budget without connecting an account
~~~

The manual fallback preserves the product’s core value when FinanceKit is unavailable, not eligible, denied, or pending review.

## State-driven shell

Use explicit states rather than showing a blank or fake dashboard:

| State | Primary message | Action |
| --- | --- | --- |
| notConfigured | This version is not configured for financial data | Contact/build configuration path |
| notEligible | FinanceKit is not available for this region/account/target | Manual mode |
| readyToConnect | Connect selected financial data | System authorization |
| selecting | Choose accounts and time range in Apple’s surface | Wait/cancel |
| connectedNoAccounts | No eligible account is shared | Revisit sharing or manual mode |
| loading | Updating balances and transactions | Show progress and last known data |
| ready | Data refreshed at a specific time | Review/filter |
| stale | Last update is older than product policy | Refresh/reconnect/manual |
| partial | Some account/field data is unavailable | Show exact scope |
| denied | Access was denied or withdrawn | Explain settings/disconnect |
| extensionUpdating | Background update is being merged | Show last successful refresh |
| orderPending | Wallet order accepted or awaiting system result | Reconcile with order service |
| proposalReady | Local categorization or summary is ready for review | Review/apply/discard |
| error | Data could not be read or reconciled | Retry/manual/support |

Do not use a zero balance as a loading placeholder. Do not use a spinner with no freshness label when old data remains visible.

## Balance hierarchy

Use a predictable hierarchy:

1. Account name/type and scope.
2. Balance amount and currency.
3. Current/available/booked semantics.
4. Last refreshed time.
5. Supporting transaction/trend action.

Keep the currency code and amount accessible as text. If there are multiple currencies, group them rather than silently converting to a preferred currency. Show unavailable values as unavailable, not zero or a dash that may be misread.

For a trend card:

- define the date range;
- identify whether it uses posted, transaction, or balance data;
- include a text alternative for VoiceOver;
- distinguish an app calculation from source values;
- allow the person to inspect the records behind a conclusion.

## Transaction list

A row may contain merchant name, transaction description, date, amount, credit/debit status, category, and a source or pending marker. Keep the original transaction description accessible even if the visible label is normalized.

Design rules:

- never color-code credit/debit without text or an icon label;
- preserve minus/plus semantics and currency;
- show pending versus posted status;
- display the transaction date and posted date when the difference matters;
- offer a source/details screen rather than hiding context in a swipe gesture;
- do not imply that a merchant category code is a user-confirmed category;
- keep filters reversible and visible;
- use the system TransactionPicker when the person must choose a set of transactions.

## TransactionPicker flow

Use a person-mediated selection path when a task needs only a subset:

~~~text
Explain why a selection is needed
-> TransactionPicker label
-> person chooses transactions
-> app shows selected count and total scope
-> optional local proposal
-> review each proposed change
-> apply only approved deterministic changes
~~~

The picker is not a shortcut to broad access. A person’s selected transactions are still financial data, and the app should not retain them longer than the task requires.

## Budget and AI review

AI should appear as a review layer on top of source data:

~~~text
source transaction rows
-> deterministic projection
-> local category proposal
-> source IDs and confidence
-> review card
-> apply or discard
~~~

The review card should show:

- the selected source records or a drill-down link;
- proposed category or explanation;
- uncertainty and missing data;
- the model or rule path used;
- an Apply, Edit, and Discard action;
- a way to correct future suggestions.

Use language such as “Suggested category” or “Draft summary.” Avoid “verified,” “safe,” “fraud,” “best financial decision,” or “guaranteed savings” unless the product has a separate deterministic and legally reviewed basis.

Never let a model:

- authorize a transaction or transfer;
- change a balance;
- infer a hidden account;
- choose a new account-sharing scope;
- create or sign a Wallet order;
- use a user’s full financial history when the selected records are sufficient;
- silently sync financial records to an external service.

## Wallet order design

An order-to-Wallet route should show:

1. the validated order or fulfillment state;
2. what will be added to Wallet;
3. the standardized AddOrderToWalletButton;
4. what happens after the person confirms;
5. how to find the order in Wallet;
6. how order changes or refunds are reflected.

Do not present a “saved to Wallet” message before FinanceStore and the system UI return the appropriate result. Do not call an order delivered because it is stored in Wallet.

## Liquid Glass composition

Liquid Glass should establish focus and continuity:

- use one primary glass action per hierarchy;
- keep source numbers on stable, opaque-enough surfaces with strong contrast;
- let semantic labels and separators carry structure;
- use GlassEffectContainer or grouping only where related actions need to read as one unit;
- avoid glass behind every row or chart point;
- let the system-owned FinanceKitUI surface keep its own appearance;
- test large text, bold text, increased contrast, reduced transparency, and reduced motion;
- keep destructive disconnect/delete actions visually distinct from connect or apply.

The app can feel Apple-native through spacing, typography, controls, material restraint, and clear state—not by copying Wallet or Apple Card screens.

## Empty, partial, and stale data

Empty data is meaningful:

- no account shared;
- account exists but no transactions in the selected range;
- balance unavailable;
- transaction description missing;
- account data pending;
- region has no eligible provider.

Partial data should name the missing part. A dashboard that combines one fresh account with one stale account needs per-account freshness or a clear aggregate warning.

If a background update arrives while the person is reviewing a proposal, revalidate the source IDs and invalidate the proposal if the underlying records changed.

## Accessibility and localization

Make the full financial task accessible:

- VoiceOver reads account scope, amount, currency, pending/current status, dates, freshness, and source/proposal distinction.
- Voice Control can reach Connect, Refresh, Review, Apply, Edit, Disconnect, and Delete.
- Dynamic Type keeps amounts and explanatory text readable without clipping.
- Reduce Transparency preserves contrast without requiring glass.
- Reduce Motion does not hide a data update.
- Color is never the only signal for credit, debit, warning, or stale state.
- Currency, dates, decimal separators, pluralization, and time zones are localized.
- Long merchant names and large amounts have a deliberate truncation and detail route.
- The deletion and disconnect actions are discoverable and reversible where policy allows.

Charts need an accessible text summary and a path to the underlying transactions. Do not make a sparkline the only representation of a balance change.

## Privacy settings surface

Include an in-app data settings screen with:

| Control | Meaning |
| --- | --- |
| Shared accounts | Which account projections are currently used |
| Time range | How much history the feature retains or analyzes |
| AI categorization | Whether local suggestions are enabled |
| Background refresh | Whether the feature listens for updates |
| Disconnect | Stop reading new data and remove/reconcile local projections |
| Delete | Remove stored financial records and proposals under the data policy |
| Export | Provide a human-readable user-owned export only when intentionally supported |

The screen should not imply that Apple’s Wallet data can be edited by the app. The app can manage its local projection and its own orders; Apple owns the system store and consent surface.

## Proof-oriented preview fixtures

Use redacted fixtures for:

- not configured;
- no entitlement;
- authorization denied;
- selected one account;
- selected multiple accounts;
- no transactions;
- pending transaction;
- foreign currency;
- stale balance;
- history token invalid;
- background delivery update;
- AI proposal with missing merchant;
- edited proposal;
- deleted source record;
- order save pending/failure/success.

Previews show the shell. They do not prove FinanceKit authorization, regional eligibility, Apple Wallet data, background extension delivery, or App Store entitlement assignment.

## Sources

- [FinanceKit](https://developer.apple.com/documentation/financekit)
- [FinanceStore](https://developer.apple.com/documentation/financekit/financestore)
- [FinanceKitUI](https://developer.apple.com/documentation/financekitui)
- [TransactionPicker](https://developer.apple.com/documentation/financekitui/transactionpicker)
- [AddOrderToWalletButton](https://developer.apple.com/documentation/financekitui/addordertowalletbutton)
- [FinancialConnectionUIExtension](https://developer.apple.com/documentation/financekitui/financialconnectionuiextension)
- [Get started with FinanceKit](https://developer.apple.com/financekit/)
- [NSFinancialDataUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsfinancialdatausagedescription)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
