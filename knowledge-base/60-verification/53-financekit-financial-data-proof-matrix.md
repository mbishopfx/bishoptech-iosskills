# FinanceKit financial-data and Wallet-order proof matrix

FinanceKit proof crosses Apple program eligibility, managed entitlement, regional source availability, user-selected account scope, system authorization, protected data, extension delivery, signed Wallet orders, and financial calculations. Prove each boundary separately.

Use this matrix with the [FinanceKit deep dive](../42-framework-deep-dives/36-financekit-financial-data-and-wallet-orders.md), the [capability route](../50-capability-recipes/59-financekit-financial-data-route.md), the [financial-data design guide](../21-design-deep-dives/56-financial-data-and-wallet-review-design.md), and the [code recipes](../70-code-recipes/71-financekit-financial-data-recipes.md).

## Claim-to-evidence matrix

| Claim | Minimum evidence | Does not prove it |
| --- | --- | --- |
| Product is eligible for FinanceKit | Current Apple requirements, app category, supported region/distribution, approved entitlement request | An imported framework |
| Target carries FinanceKit entitlement | Signed archive entitlement dump for exact bundle ID | An Xcode capability checkbox |
| Financial usage description is present | Built Info.plist with truthful NSFinancialDataUsageDescription | A source string in a different target |
| Device can use a data type | Physical iPhone, current FinanceStore.isDataAvailable result | Simulator or one other device |
| Person authorized the app | Real system authorization flow and result | A local boolean |
| Person shared a specific account/time range | System-selected scope plus returned account/query evidence | Authorization status alone |
| Account query is bounded | Query predicates/limits/sort and redacted result fixture | Fetching one account in a mock |
| Balance is displayed correctly | Currency, available/booked/current state, timestamp, and fixture comparison | A number in a screenshot |
| Transaction mapping preserves source | Original description, source ID, dates, status, amount/currency, and normalized projection | An AI label |
| History updates reconcile | Durable HistoryToken, change replay, merge, and restart test | One current query |
| Background delivery works | Signed app/extension, App Group, enabled data types/frequency, physical system update, checkpoint/relaunch proof | A foreground timer |
| TransactionPicker is user-mediated | Physical picker selection and bound result with selected IDs | A hand-built selection array |
| Wallet order is stored | Signed archive, FinanceStore result, system UI, and order-service reconciliation | A button tap |
| Wallet order is fulfilled | Provider/order service state and delivery/refund evidence | Wallet storage result |
| AI category is safe | Selected source IDs, minimal projection, proposal, review, deterministic apply, correction/delete | A generated paragraph |
| Disconnect/delete works | Stop-sharing action, local projection cleanup, extension disablement, and retained-data audit | Hiding the dashboard |
| Accessibility works | VoiceOver, Voice Control, Switch Control, Dynamic Type, reduced transparency/motion, localization, and full task run | Labels in source |
| Release is ready | Distribution artifact, entitlement assignment, region/category, physical iPhone, extension, system, privacy, and metadata evidence | A debug build |

## Environment record

| Field | Value |
| --- | --- |
| App target/bundle ID |  |
| Version/build |  |
| SDK/Xcode |  |
| Device model/OS |  |
| Region/store account |  |
| App Store category |  |
| FinanceKit entitlement assignment |  |
| Signed entitlement hash |  |
| NSFinancialDataUsageDescription |  |
| FinanceStore data types |  |
| User-selected account scope |  |
| Time range |  |
| App Group |  |
| Extension target/build |  |
| HistoryToken fixture |  |
| Wallet order ID/provider state |  |
| AI model/rule revision |  |
| Privacy/deletion policy revision |  |

Do not place transaction descriptions, account IDs, balances, full Wallet order archives, or user identity in ordinary diagnostics.

## Eligibility and target matrix

| Test | Expected evidence |
| --- | --- |
| Unsupported region | Feature explains unavailable route and offers manual mode |
| Supported region but no assigned entitlement | App does not claim support; build configuration is actionable |
| Assigned entitlement, wrong bundle ID | Signed artifact rejects or does not expose the route |
| Correct entitlement and disclosure | Built target contains exact managed capability and usage description |
| iOS below feature minimum | Availability gate selects fallback |
| App Store category mismatch | Release checklist blocks distribution claim |
| App Group mismatch | Extension/app handoff is refused safely |
| Entitlement removed | App returns to manual mode without corrupting local projections |

## Authorization and scope matrix

| Test | Expected evidence | Does not prove |
| --- | --- | --- |
| First authorization | System surface, accepted status, bounded first query | All accounts are now in app |
| User cancels | No local source data is created; manual mode remains | A transient callback |
| User denies | No repeated prompt loop; settings/manual path | Permanent denial in all future versions |
| No accounts shared | Empty state with scope explanation | Store unavailable |
| One account shared | Only selected account appears in projection | Permission for future accounts |
| Time range limited | Queries and retained records respect the selected range | Historical data outside scope |
| Authorization later withdrawn | App detects and marks stale/denied; delete policy runs | A cached record is still current |
| Reauthorization | New scope is reconciled with old projection | Old data may be retained without policy |

## Account and balance fixture matrix

| Fixture | Expected |
| --- | --- |
| Asset account | Account type and label map correctly |
| Liability account | Liability semantics are not displayed as cash |
| Available balance missing | UI shows unavailable, not zero |
| Booked and available differ | Both are distinguishable |
| Pending/current status | Status is textual and accessible |
| Multiple currencies | No silent sum without conversion policy |
| Account removed | Projection is marked removed/deleted and related data policy runs |
| Stale source | Timestamp and stale state remain visible |
| Empty account set | Manual mode/reconnect remains reachable |

## Transaction and query matrix

| Test | Expected |
| --- | --- |
| Query with limit/offset | Results are bounded and pagination is stable |
| Merchant category predicate | Only intended merchant category codes match |
| Status predicate | Pending/posted/other status mapping is correct |
| Type predicate | Credit/debit/other type mapping is correct |
| Original description | Source string is preserved |
| Missing merchant | Row remains understandable without inventing a name |
| Foreign currency | Foreign amount/rate are visible and not silently discarded |
| Posted date differs from transaction date | Both dates are handled under the product policy |
| Duplicate-looking records | Stable IDs prevent accidental collapse |
| Source update | Local edited proposal is revalidated against current record |
| Deletion | Derived labels and summaries obey source-delete policy |

## History and background delivery matrix

| Test | Expected evidence |
| --- | --- |
| First history with nil token | Initial records and durable token are persisted |
| History from saved token | Only changes since token are merged |
| Multiple changes | Merge is idempotent and preserves source IDs |
| Token invalid | Projection rebaselines from a bounded full query |
| Process killed during merge | Last durable checkpoint replays safely |
| App relaunch | Projection and token restore consistently |
| Background type enabled | Correct data types/frequency are signed/configured |
| Extension receives data | Callback handles selected types and persists a checkpoint |
| Extension willTerminate | State is saved or work remains replayable |
| Delivery delayed | UI says last refreshed; no false real-time promise |
| Disconnect | Background delivery is disabled and extension data is cleaned |

## TransactionPicker matrix

| Test | Expected evidence |
| --- | --- |
| Open picker with explanation | Person understands selection purpose |
| Select one transaction | Bound selection contains expected source ID |
| Select multiple transactions | Count and source scope are visible |
| Cancel picker | No selection is applied |
| Apply local proposal | Source IDs and proposal are reviewable |
| Edit category | Person correction is persisted as app-owned data |
| Source changes before apply | Proposal invalidates or revalidates |
| Delete selection | Temporary selected data is removed per policy |

## Wallet order matrix

| Test | Expected evidence | Does not prove |
| --- | --- | --- |
| Valid signed archive | FinanceStore save result and system Wallet flow | Fulfillment |
| Duplicate order | Contains/save result maps to idempotent state | New order was created |
| Invalid signature | Store/system rejects; no success copy | Local archive exists |
| User cancels | No false added-to-Wallet state | Order was refunded |
| Wallet accepted | System/UI evidence and order ID reconciliation | Merchant delivery |
| Provider pending | Pending copy and refresh/reconciliation | Payment settled |
| Provider refund | Wallet/order state follows policy | Local delete only |
| AI-generated order data | Must be rejected unless deterministic pipeline signs it | Model output is trusted |

## AI proposal matrix

| Test | Expected evidence |
| --- | --- |
| Category proposal | Source IDs, minimal projection, proposal, confidence/uncertainty |
| Missing merchant | Model does not invent a merchant |
| Currency conversion | Deterministic conversion or explicit unknown |
| Fraud-like language | Model uses review language and does not claim fraud |
| Balance question | Response cites source timestamp and records |
| Scope question | Model cannot retrieve records outside selected scope |
| Apply | Typed validator and person confirmation |
| Source changed | Proposal invalidated/reviewed again |
| Model unavailable | Manual/deterministic fallback |
| Delete | Proposal and derived data follow source deletion |

## Accessibility and Liquid Glass evidence

Run the full connect-to-review-to-disconnect task with:

- VoiceOver focus and source/proposal announcement;
- Voice Control labels for all actions;
- Switch Control reachability;
- Dynamic Type and large amounts/merchant names;
- reduced transparency and increased contrast;
- reduced motion during refresh/update;
- localized currency, dates, pluralization, and errors;
- keyboard navigation where supported.

Capture the app-owned glass shell separately from the FinanceKitUI/system surface. A polished screenshot cannot prove consent, query scope, background delivery, or Wallet storage.

## Release packet

Include:

1. Current FinanceKit eligibility/region review.
2. Entitlement assignment and signed archive.
3. Built Info.plist disclosure.
4. Physical iPhone authorization and scope report.
5. Account/balance/transaction fixture comparison.
6. History-token and extension relaunch/termination report.
7. TransactionPicker selection report.
8. Wallet order signing/save/system/provider reconciliation.
9. AI proposal and deletion/revalidation report.
10. Accessibility/localization report.
11. Privacy, retention, disconnect, and deletion review.
12. TestFlight/App Store category and production metadata review.

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
- [FinanceKitUI](https://developer.apple.com/documentation/financekitui)
- [TransactionPicker](https://developer.apple.com/documentation/financekitui/transactionpicker)
- [AddOrderToWalletButton](https://developer.apple.com/documentation/financekitui/addordertowalletbutton)
- [FinancialConnectionUIExtension](https://developer.apple.com/documentation/financekitui/financialconnectionuiextension)
- [Get started with FinanceKit](https://developer.apple.com/financekit/)
- [FinanceKit entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.financekit)
- [NSFinancialDataUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsfinancialdatausagedescription)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
