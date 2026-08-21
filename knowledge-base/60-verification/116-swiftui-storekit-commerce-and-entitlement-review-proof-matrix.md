# SwiftUI StoreKit 2 commerce and entitlement-review proof matrix

This matrix separates documentation, deterministic StoreKit testing, UI evidence, signed account behavior, physical-device behavior, server/account reconciliation, and release evidence. A paywall screenshot or successful local transaction is useful evidence, but it closes only a narrow part of the route.

## Evidence levels

| Level | Evidence | Can prove | Cannot prove |
| --- | --- | --- | --- |
| S0 | Official source | API role and stated platform behavior | The app’s configuration or UX. |
| S1 | SwiftUI fixture/preview | Deterministic rendering and copy for catalog/entitlement states | Storefront, account, billing, or system-sheet behavior. |
| S2 | Unit/Swift Testing | Catalog normalization, state transitions, policy, idempotency, stale-revision rejection | Real App Store transactions or accessibility task success. |
| S3 | StoreKit Testing in Xcode | Local product loading, purchase results, renewals, refunds, offers, and recovery fixtures | Production metadata, sandbox account, server notifications, or App Review. |
| S4 | UI automation | Repeatable taps, selection, restore/manage entry, and state projections in a named target | Physical account behavior or every localization/accessibility condition. |
| S5 | Signed sandbox/TestFlight device | Apple test account, signing, system sheet, entitlement updates, account/environment wiring | Production price, live fulfillment, App Review, or all device families. |
| S6 | Server/account evidence | JWS validation, account association, notification processing, entitlement ledger, delivery | Native UI quality or physical device accessibility. |
| S7 | Release artifact/system evidence | Archive identity, App Store metadata, entitlements, privacy, distribution configuration, selected live route | Future storefront changes or broad user success. |

## Fixture contract

Every test fixture should identify:

- target name, bundle ID, SDK, deployment target, and platform;
- local StoreKit configuration or sandbox/production environment;
- product IDs, types, subscription group, localized price, term, and offer fixture;
- catalog revision and missing-product condition;
- current entitlement and subscription renewal state;
- purchase result: pending, cancelled, verified, unverified, or thrown error;
- delivery outcome and transaction-finish decision;
- account token/server reconciliation state if applicable;
- locale, currency, Dynamic Type, contrast/transparency/motion settings, and input mode;
- timestamp and artifact location.

Do not call a fixture “production” because its product ID resembles the App Store product ID.

## Catalog and StoreKit-view matrix

| Gate | Fixture/action | Expected evidence | Failure meaning |
| --- | --- | --- | --- |
| Product IDs | All configured IDs returned | Each Product has expected type and live localized metadata | App Store/configuration mismatch or unavailable storefront. |
| Partial catalog | One requested ID missing | Missing ID is visible; no invented product/price | Silent empty/free behavior. |
| ProductView | One non-consumable | Native product row and purchase action appear | Wrong product type, availability, or target route. |
| StoreView | Multiple one-time products | Collection layout and selection/purchase behavior | Layout or product collection mismatch. |
| SubscriptionStoreView | One subscription group | Group products, localized metadata, and native selection | Wrong group, product IDs, or target support. |
| Long metadata | Long name/description/currency | No clipping at Dynamic Type and RTL | Layout depends on English/compact text. |
| Loading | Delayed product response | Stable placeholder preserves navigation and dismiss | Main actor blocked or content jumps. |
| Error | StoreKit/configuration failure | Retry/support/free path is visible | Error becomes empty success. |

## Purchase and delivery matrix

| Gate | Required case | Evidence |
| --- | --- | --- |
| User starts purchase | Tap one product action | Product ID, purchase start, system confirmation, and target scene recorded. |
| User cancels | Cancel system sheet | No entitlement grant; clear non-error state. |
| Pending | Ask to Buy or delayed payment fixture | Pending UI persists and updates listener is active. |
| Verified success | Valid transaction | Product policy delivers access, publishes entitlement, and finishes at the correct point. |
| Unverified | Automatic verification failure fixture | Access is not granted under the chosen policy; support/retry path exists. |
| Thrown error | Product unavailable/not allowed/offer error | Error is mapped to a user action without losing catalog context. |
| Duplicate update | Same transaction delivered twice | Delivery ledger/idempotency prevents duplicate consumable grant. |
| Interrupted delivery | App terminates before finish | Unfinished transaction is recovered and delivered once. |
| Revocation/refund | Revoked/refunded transaction | Access is removed or policy-adjusted and UI explains state. |
| Finish boundary | Delivery succeeds/fails | Transaction finishes only after safe delivery or declared retry record. |

## Entitlement and subscription matrix

| State | Required test | Expected result |
| --- | --- | --- |
| Current non-consumable | currentEntitlements emits verified transaction | Feature opens after policy evaluation. |
| Active subscription | RenewalState.subscribed | Current plan and access are shown. |
| Grace period | RenewalState.inGracePeriod | Access/copy match the product policy and manage action is present. |
| Billing retry | RenewalState.inBillingRetryPeriod | Billing attention is visible; access is not overstated. |
| Expired | RenewalState.expired or expired transaction | Locked/ended state and plan review appear. |
| Revoked | RenewalState.revoked or revocation date | Access removal and support/plan route appear. |
| Upgrade/downgrade | Subscription group status with multiple levels | Highest applicable service state is selected; current/target plan are clear. |
| Family Sharing | More than one status where supported | Policy does not assume the first status is authoritative. |
| Foreground refresh | Return from background/settings | Entitlement projection is re-evaluated. |
| Cross-device update | Transaction arrives through updates | Same verification/delivery path handles it. |

## Restore, manage, offer, and refund matrix

| Destination | Evidence |
| --- | --- |
| Restore | User taps restore, AppStore.sync runs, result state appears, entitlements are re-read. |
| Manage | manageSubscriptionsSheet or supported system route opens from current-plan context. |
| Unsupported manage | Target/platform fallback explains the limitation. |
| Offer code | SwiftUI redemption sheet returns a result; verified transaction reaches entitlement pipeline. |
| Promotional offer | Eligibility/signature/configuration route is exercised; private key is not in the app. |
| Win-back | Eligible and ineligible fixtures show distinct copy. |
| Refund | Refund request route identifies transaction and handles approved/declined result. |
| Terms/privacy | Destinations are reachable, localized where required, and match the shipped product. |

## StoreKit environment matrix

| Environment | Prove | Do not claim |
| --- | --- | --- |
| Local .storekit | Product/state/UI logic and automated scenarios | App Store Connect metadata, live price, production account, or real server delivery. |
| Xcode StoreKit transaction manager | Manual transaction-state setup and recovery | Broad physical-device or production behavior. |
| Sandbox/TestFlight | Signed target, Apple test account, system sheet, account behavior | Production price, review, regional availability, or live server scale. |
| Production | App Store product, signed release, server/notification/fulfillment evidence | That every user, locale, device, or future price behaves identically. |

## AI proposal matrix

| AI state | Fixture | Required proof |
| --- | --- | --- |
| Model unavailable | Unsupported/unavailable model state | Native comparison remains usable. |
| Preparing | Delayed generation | Loading is bounded and cancellable. |
| Valid proposal | Candidate IDs match catalog revision | Price/term are replaced from Product, not model text. |
| Unknown product ID | Model emits arbitrary ID | Proposal rejected or marked invalid. |
| Stale proposal | Catalog/entitlement revision changes | Review is blocked or proposal is regenerated. |
| Commercial hallucination | Wrong price/offer/renewal in candidate | Deterministic facts override or reject it. |
| Side-effect attempt | Tool asks to purchase/restore/manage | Tool is unavailable; user action remains explicit. |
| Accepted explanation | User chooses a plan | Native StoreKit route begins; AI does not become authorization. |

## Native design and accessibility matrix

| Gate | Required fixtures |
| --- | --- |
| Liquid Glass | Light/dark imagery, bright/dim background, glass fallback, opaque/system-material fallback. |
| Dynamic Type | Largest supported sizes with long product names, prices, offers, terms, and status. |
| VoiceOver | Read order for benefit, product, price, term, selected state, action, result, restore, and manage. |
| Contrast/transparency | Increased contrast and reduced transparency preserve grouping and state. |
| Motion | Reduced motion still communicates pending/verified/failed state. |
| RTL/localization | Arabic or another RTL locale, long localized name, currency, plural/term language. |
| Keyboard/pointer | Focus, selection, purchase, restore, manage, dismissal, and error recovery. |
| Switch/Voice Control | Actions have stable accessible names and do not require a glass gesture. |
| Cancellation | Paywall dismissal preserves free flow and does not trap the user. |

## Performance and lifecycle matrix

Record:

- time to first useful paywall frame;
- product-load latency and failure rate in the selected environment;
- entitlement evaluation time and main-actor work;
- number of active transaction listeners;
- restore and management presentation latency;
- memory and hitch behavior while a plan surface is visible;
- cancellation when product IDs, scene identity, or navigation changes;
- foreground/background recomputation behavior;
- model explanation latency and cancellation if AI is enabled.

The test should prove that product loading, server verification, transaction history, and AI explanation do not block the main actor or make a free/cancel path unresponsive.

## Artifact checklist

For a release-bound commerce route, retain:

1. source and SDK links;
2. product catalog policy and product-ID mapping;
3. local StoreKit configuration and test plan;
4. unit/UI/StoreKit test results;
5. screenshot/video of native system purchase/restore/manage states where permitted;
6. sandbox/TestFlight device, account, OS build, locale, and target evidence;
7. signed transaction/JWS verification and account-ledger evidence when a server exists;
8. privacy/retention/logging review;
9. accessibility and localization results;
10. archive, entitlements, App Store metadata, and release-build inspection.

## Stop conditions

The route is not proven when the only artifact is a SwiftUI preview, paywall screenshot, local StoreKit purchase, cached “premium” Boolean, successful compile, or AI recommendation. Those artifacts remain valuable, but the claim must stay within the evidence level they actually support.

## Sources

- [StoreKit views](https://developer.apple.com/documentation/storekit/storekit-views)
- [Setting up StoreKit Testing in Xcode](https://developer.apple.com/documentation/xcode/setting-up-storekit-testing-in-xcode)
- [Testing In-App Purchases in Xcode](https://developer.apple.com/documentation/storekit/testing-in-app-purchases-in-xcode)
- [Product](https://developer.apple.com/documentation/storekit/product)
- [Product.PurchaseResult](https://developer.apple.com/documentation/storekit/product/purchaseresult)
- [Product.PurchaseError](https://developer.apple.com/documentation/storekit/product/purchaseerror)
- [Transaction](https://developer.apple.com/documentation/storekit/transaction)
- [Transaction.currentEntitlements](https://developer.apple.com/documentation/storekit/transaction/currententitlements)
- [Transaction.updates](https://developer.apple.com/documentation/storekit/transaction/updates)
- [Transaction.unfinished](https://developer.apple.com/documentation/storekit/transaction/unfinished)
- [Product.SubscriptionInfo](https://developer.apple.com/documentation/storekit/product/subscriptioninfo)
- [Product.SubscriptionInfo.Status](https://developer.apple.com/documentation/storekit/product/subscriptioninfo/status)
- [Product.SubscriptionInfo.RenewalState](https://developer.apple.com/documentation/storekit/product/subscriptioninfo/renewalstate)
- [manageSubscriptionsSheet(isPresented:)](https://developer.apple.com/documentation/swiftui/view/managesubscriptionssheet%28ispresented%3A%29)
- [storeButton(_:for:)](https://developer.apple.com/documentation/swiftui/view/storebutton%28_%3Afor%3A%29?changes=__1)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
