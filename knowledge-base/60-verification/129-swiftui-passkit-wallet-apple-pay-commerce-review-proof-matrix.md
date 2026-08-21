# SwiftUI PassKit, Wallet, Apple Pay, and commerce review proof matrix

This matrix proves the commerce boundaries around a named iOS target: app-owned cart/order state, Apple Pay availability and system authorization, provider/server processing, Wallet pass signing/add/update, Wallet Orders, FinanceKitUI order handoff, local-AI proposals, Liquid Glass composition, accessibility, privacy, and release.

Use it with the [commerce review](../42-framework-deep-dives/104-swiftui-passkit-wallet-apple-pay-commerce-review.md), [design guide](../21-design-deep-dives/132-swiftui-passkit-wallet-apple-pay-commerce-review-design.md), [route](../50-capability-recipes/135-swiftui-passkit-wallet-apple-pay-commerce-review-route.md), and [recipes](../70-code-recipes/147-swiftui-passkit-wallet-apple-pay-commerce-review-recipes.md).

## Evidence levels

| Level | Evidence | Boundary |
| --- | --- | --- |
| L0 | Current Apple documentation and SDK/API availability | Documented contract awareness |
| L1 | Named target settings, capabilities, signed entitlements, certificates, provider/pass service configuration | Configuration contract |
| L2 | Deterministic order, currency, shipping, pass, token, and revision fixtures | App-owned validation |
| L3 | Simulator, local provider fixture, local signed sample, or system mock | Partial app-side behavior |
| L4 | Signed physical-device Apple Pay/Wallet/FinanceKitUI/system run | Device and system behavior |
| L5 | Sandbox/provider, pass-service, archive, TestFlight, and release packet | Distribution environment |
| L6 | Repeatable privacy, accessibility, recovery, idempotency, and operational packet | Readiness claim |

Do not use an L0 or L2 artifact to claim payment settlement, Wallet presence, provider fulfillment, financial-data authorization, or release readiness.

## Claim-to-evidence matrix

| Claim | Minimum evidence | Does not prove it |
| --- | --- | --- |
| The selected product uses the correct commerce route | Route worksheet mapping StoreKit, Apple Pay, Wallet pass, Wallet order, or FinanceKit | A visually similar checkout |
| Apple Pay target is configured | Named target compile, Apple Pay capability, signed Merchant IDs entitlement, merchant/certificate environment | A merchant ID string in source |
| Payment request is correct | Cart revision fixtures for currency, totals, networks, contacts, shipping, coupons, final/pending items | A request object in a preview |
| Apple Pay availability is known | Device/system preflight matrix and alternate route | A single canMakePayments Boolean |
| System sheet presents | Signed physical-device system run with the target request | A controller initialized in source |
| User canceled correctly | Physical/system cancellation run and app focus/recovery assertion | A delegate method exists |
| Provider processed payment | Redacted token handoff, provider response, transaction/order binding, idempotency evidence | A payment sheet success |
| Fulfillment occurred | Merchant/order service event or webhook reconciliation | Provider authorization alone |
| Payment data is protected | Token redaction, transport, server/provider boundary, log and retention review | Local JSON decoding |
| Apple Pay order bridge is valid | Successful authorization result with real PKPaymentOrderDetails and service identity | An order details object in a fixture |
| Wallet pass is valid | Signed pass bundle, manifest/signature/certificate inspection, physical add flow | Pass JSON or screenshot |
| Pass identity/update is correct | Stable pass type/serial and newly signed update service run | A local file replacement |
| Pass add state is correct | Added, canceled, already-present, unavailable, and open-in-Wallet runs | Add button presence |
| Pass library scope is correct | Entitlement plus device library matrix | A list of passes from one account |
| Wallet order is current | Signed order archive, service registration/retrieval, update push/retrieval, monotonic revision | An app order status card |
| FinanceKitUI handoff is valid | Target/entitlement/SDK proof, signed archive, AddOrderToWalletButton result | Button compilation |
| AI proposal is grounded | Source IDs/revisions, model revision, invalid fixtures, review, deterministic revalidation | Model text or confidence |
| Liquid Glass shell is native | State/contrast/reduced-effects/layout fixtures and device interaction | Glass screenshot |
| Commerce flow is accessible | Task-level VoiceOver/Dynamic Type/contrast/Reduce Motion/input run | Accessibility identifiers or audit only |
| Release is ready | Signed archive, installed TestFlight/release build, environment and metadata packet | Debug/simulator success |

## Target and merchant packet

Record:

~~~text
App target:
Bundle identifier:
SDK/toolchain:
Deployment target:
Device family:
Apple Pay capability:
Signed Merchant IDs entitlement:
Merchant identifier:
Payment processing certificate revision:
Provider/processor and environment:
Wallet capability:
Pass Type IDs entitlement:
Pass type identifier:
Pass signing certificate revision:
Pass service environment:
FinanceKit/FinanceKitUI target and entitlement:
App Group/extension:
Privacy manifest and usage descriptions:
Sandbox/test account:
Archive version/build:
~~~

Compare the intended local configuration with the signed archive and installed physical build. A capability checkbox in an Xcode project is not release proof.

## Apple Pay request matrix

| Fixture | Expected result | Evidence |
| --- | --- | --- |
| Supported device and matching network | Ready | Device preflight |
| Unsupported device | Alternate route | Physical/device matrix |
| No matching card/network | Setup or alternate path | System run |
| Zero/negative/overflow amount | Deterministic rejection | Unit fixture |
| Currency mismatch | Rejection before sheet | Unit/provider fixture |
| Cart revision changes after request | Old request invalidated | Revision test |
| Shipping contact allowed | Updated items/methods | System callback run |
| Shipping contact invalid | User-visible errors and retry | System callback run |
| Shipping method changes | Updated total | System callback run |
| Coupon changes | Updated total/status | System callback run |
| Provider timeout | Pending/retry, no false success | Sandbox run |
| Provider decline | Declined recovery | Sandbox run |
| User cancellation | Stable app state/focus | Physical system run |
| Duplicate authorization delivery | Idempotent order state | Server test |

Record whether the summary items were final or pending and why. Verify the system sheet amount against the server’s authoritative order revision.

## Payment token and server matrix

| Check | Evidence | Failure boundary |
| --- | --- | --- |
| Token data is not logged | Redacted logs and crash payload review | Secrets exposed |
| Token is bound to order | Application data/order ID and server request | Token applied to wrong order |
| Signature/certificate/provider validation | Provider or server validation record | Client decoded token |
| Currency and amount match | Server comparison with order revision | Stale cart |
| Transaction ID is idempotent | Duplicate fixture and database result | Double fulfillment |
| Provider response is reconciled | Accepted/declined/pending/refunded matrix | UI-only status |
| Fulfillment is separate | Order service event/webhook | Authorization mistaken for delivery |
| Token retention is bounded | Data map and deletion test | Permanent sensitive storage |

Never put merchant private keys, payment-processing private keys, pass signing keys, or pass authentication tokens in the app target.

## Wallet pass matrix

| Claim | Fixture or run | Required artifact |
| --- | --- | --- |
| Source is complete | pass.json, image, localization, field fixture | Source manifest |
| Signature is valid | Certificate and PKCS #7 verification | Signed .pkpass |
| Identity is stable | Same pass type/serial across versions | Version comparison |
| Add UI works | AddPassToWalletButton or PKAddPassesViewController | Physical-device system run |
| User canceled | Cancel from system UI | App recovery state |
| Pass already exists | Add the same identity again | View/open-in-Wallet path |
| Multiple passes add together | Multi-pass fixture | One system handoff |
| Entitlement scope is correct | Pass type access matrix | Signed entitlement inspection |
| Pass is expired/voided | Expiry/voided fixture | Wallet display and app recovery |
| Update works | New signed revision with same identity | Service/device update packet |
| Update service rejects auth | Invalid token fixture | Safe failure/no data leak |
| Push/update is current | Registration, notification, retrieval | Production or approved staging evidence |

Do not claim “pass is in Wallet” from a downloaded file, app-local Boolean, or pass preview.

## Wallet Orders and FinanceKitUI matrix

| Claim | Minimum evidence | Does not prove it |
| --- | --- | --- |
| Order schema is valid | Required Order fields and schema fixture | A cart JSON object |
| Order archive is signed | Package/signature/certificate check | Unsigned archive |
| Order is added | FinanceStore/save-order or system button result | Button rendered |
| Order is already newer | SaveOrderResult and current revision comparison | Local duplicate check |
| Wallet shows the order | Physical Wallet/system run | App order screen |
| Order updates | Server registration, push, latest package retrieval | Local refresh |
| Fulfillment status is accurate | Merchant service event mapped to signed revision | AI-generated status |
| Support links are safe | HTTPS/allowlist/privacy review | Arbitrary URL field |
| FinanceKit access is allowed | Managed entitlement and authorization packet | Importing FinanceKit |
| Financial data is minimized | Purpose, field map, retention/deletion evidence | General privacy statement |

Keep Apple Pay order details, Wallet order identifiers, app order IDs, provider transaction IDs, and FinanceKit records distinct in the evidence packet.

## AI proposal matrix

| Proposal | Required validation | Forbidden shortcut |
| --- | --- | --- |
| Cart summary | Recalculate from current line items | Model total |
| Receipt classification | User-selected source and editable label | Silent ledger mutation |
| Pass title/field draft | Pass type/field length/localization validation | Model-generated signed pass |
| Order lookup | Current account/order IDs and authorization | Guessing from names |
| Status explanation | Current provider/order revision | Model claim of fulfillment |
| Wallet action | User review plus deterministic current lookup | Model directly adds/removes pass |

Every proposal records source identity, source revision, model revision, generated time, user decision, and revalidation result.

## Accessibility and privacy matrix

| Task | Evidence |
| --- | --- |
| Find item, amount, and total | VoiceOver task run |
| Understand final versus pending amount | VoiceOver and Dynamic Type |
| Start Apple Pay or Add to Wallet | Semantic system-control task |
| Recover from cancel/decline/pending | Focus and announcement run |
| Read order/pass fields | Dynamic Type, localization, contrast |
| Use without motion/transparency | Reduce Motion/Reduce Transparency |
| Use with keyboard/pointer/Voice Control/Switch Control | Alternate-input task |
| Protect secrets on shared/locked surfaces | Privacy screenshot/log review |
| Delete temporary token/order/pass artifacts | Storage inspection |

An audit report is one diagnostic input; it does not replace a full physical-system task.

## Release packet

~~~text
[ ] Named target compiles with selected SDK
[ ] Signed Apple Pay capability and Merchant IDs match request
[ ] Merchant/certificate/provider environment is recorded
[ ] Availability and alternate route run
[ ] Payment sheet success, cancel, update, decline, timeout runs
[ ] Token redaction and server/provider verification recorded
[ ] Order/fulfillment/idempotency/refund reconciliation recorded
[ ] Signed pass source, manifest, certificate, add, cancel, duplicate runs
[ ] Pass update service and push/retrieval run
[ ] Wallet order archive/service/device run
[ ] FinanceKit/FinanceKitUI entitlement/result run if used
[ ] AI source/model/proposal/revalidation packet
[ ] VoiceOver/Dynamic Type/contrast/Reduce Motion/input run
[ ] Privacy, retention, and log review
[ ] Physical-device system run
[ ] Archive, TestFlight, and release metadata inspection
[ ] Unsupported cases and recovery copy
~~~

## Sources

- [PassKit](https://developer.apple.com/documentation/passkit)
- [Setting up Apple Pay](https://developer.apple.com/documentation/PassKit/setting-up-apple-pay)
- [Configuring Apple Pay support](https://developer.apple.com/documentation/xcode/configuring-apple-pay-support)
- [Offering Apple Pay in Your App](https://developer.apple.com/documentation/passkit/offering-apple-pay-in-your-app)
- [PKPaymentRequest](https://developer.apple.com/documentation/passkit/pkpaymentrequest)
- [PKPaymentAuthorizationController](https://developer.apple.com/documentation/passkit/pkpaymentauthorizationcontroller)
- [PKPaymentAuthorizationControllerDelegate](https://developer.apple.com/documentation/passkit/pkpaymentauthorizationcontrollerdelegate)
- [PKPaymentToken](https://developer.apple.com/documentation/passkit/pkpaymenttoken)
- [Payment token format reference](https://developer.apple.com/documentation/PassKit/payment-token-format-reference)
- [PKPaymentOrderDetails](https://developer.apple.com/documentation/passkit/pkpaymentorderdetails)
- [Wallet](https://developer.apple.com/documentation/passkit/wallet)
- [PKPass](https://developer.apple.com/documentation/passkit/pkpass)
- [PKPassLibrary](https://developer.apple.com/documentation/passkit/pkpasslibrary)
- [PKAddPassesViewController](https://developer.apple.com/documentation/passkit/pkaddpassesviewcontroller)
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
- [FinanceStore.saveOrder](https://developer.apple.com/documentation/financekit/financestore/saveorder%28signedarchive%3A%29)
- [Apple Pay HIG](https://developer.apple.com/design/human-interface-guidelines/apple-pay)
- [Wallet HIG](https://developer.apple.com/design/human-interface-guidelines/wallet)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
