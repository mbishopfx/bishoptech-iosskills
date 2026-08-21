# PassKit, Wallet, and Apple Pay proof matrix

Use this matrix before describing a commerce or Wallet feature as working. Record the exact SDK, deployment target, device family, OS build, merchant/pass environment, certificates and entitlements, server/provider, account state, and user actions.

## Evidence levels

| Level | Can prove | Cannot prove by itself |
| --- | --- | --- |
| Documentation | API roles, setup requirements, system boundaries, and HIG rules | Project configuration, merchant approval, signed pass, or device behavior |
| Source/compile | Imports, request/state types, target membership, and conditional availability | Apple Pay presentation, card provisioning, Wallet acceptance, provider capture |
| Preview/UI test | App-owned checkout/pass detail, states, accessibility, and fallbacks | Real system sheet, pass signature, Wallet library, merchant settlement |
| Simulator | Layout, fixtures, request construction, some callback seams | Complete card/Wallet hardware behavior, physical-device account state, all Apple Pay features |
| Signed physical device | Target capability, device availability, system sheet, account and selected device path | Provider settlement, all regions, all cards, universal pass validity |
| Sandbox/TestFlight | Selected merchant/pass distribution integration and release-style artifact | Live settlement, every pass update environment, App Store approval |
| Production | Observed provider fulfillment, order update, or pass update for the tested record/device | Future reliability, every device/region, another merchant or pass type |

Never promote a lower evidence level into a higher claim. A green preview is not a signed Apple Pay or Wallet integration.

## Target and configuration matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| PassKit import and availability | Build the named app target with the selected SDK | Wrong deployment target, unavailable symbol, wrong platform | The selected target can compile the chosen route |
| Apple Pay merchant identifier | Developer-account record and target capability | Identifier not assigned to target, stale account sync | Merchant identifier is configured for the tested target |
| Payment Processing certificate | Certificate record, expiry, and provider/server configuration | Expired/revoked certificate, wrong merchant, wrong environment | Payment processing is configured for the selected environment |
| Apple Pay capability | Built entitlements and provisioning profile | Capability missing from a secondary target, development-only profile | The selected artifact carries the configured capability |
| Wallet Pass Type ID | Pass Type ID record and signed pass metadata | Type ID mismatch, wrong team identifier | The pass is associated with the selected issuer |
| Wallet signing certificate | Certificate and controlled signing log | Private key on client, expired/revoked cert, wrong type ID | The selected build service can sign the tested pass |
| App target/server boundary | Secret and token inventory review | Payment/signing secrets in app, token in logs | Sensitive authority remains in the intended boundary |
| Privacy manifest and usage descriptions | Built artifact and source review | Missing reason/usage text, excessive logging | The selected build declares reviewed access |

## Apple Pay availability and UI matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| Device can make Apple Pay payments | Physical device or documented supported test environment using current availability API | Unsupported hardware, parental controls, regional limitation | Availability was observed on the tested device |
| Supported network check | Test each supported network set used by the product | Card network mismatch, empty network list, stale assumptions | The selected network set returns the observed result |
| Card setup route | Device without a provisioned card where supported | Setup action misrepresented as payment readiness | App explains setup versus ready-to-pay state |
| Apple Pay button | Real PKPaymentButton or current system integration | Fake logo/button, wrong placement, hidden unavailable action | Payment initiation uses the documented control |
| Apple Pay mark | HIG review of surrounding payment context | Mark used as a button or translated/altered improperly | Mark communicates acceptance only |
| Payment sheet presentation | System sheet run from the app-owned checkout | Presentation failure, background state, wrong target | The system sheet presented for this request/device |
| Cancellation | User cancels sheet and app returns to stable focus/state | Cancellation shown as success, duplicate retry, lost order | The cancellation recovery path works for the tested route |
| Dynamic request update | Shipping/contact/coupon update run | Total drift, stale summary, missing validation error | The sheet reflects the tested update behavior |
| Accessibility and localization | VoiceOver, Dynamic Type, locale/currency, reduced effects | Amount clipped, unclear action, state only conveyed by color | The tested preflight is usable under selected settings |

## Payment processing and fulfillment matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| Payment token handoff | Redacted provider/server request and response trace | Token logged, sent to wrong endpoint, no retry policy | Token was handed to the selected processor path |
| Provider success | Provider response tied to order identifier | Client callback treated as capture, webhook ignored | Provider accepted the tested transaction |
| Provider decline | Declined sandbox/known negative fixture | Generic error, order discarded, no alternate path | Decline is presented and recoverable |
| Invalid shipping/contact | Invalid address or unsupported region test | Sheet returns success, error not attached to field | The selected validation errors are handled |
| Timeout/retry | Delayed provider/server fixture | Duplicate charge/order, unsafe retry | The tested retry is idempotent for the chosen integration |
| Fulfillment | Merchant/order service record or real fulfillment observation | Payment accepted but “delivered” shown | Fulfillment state is separately evidenced |
| Refund/reversal | Provider and app order reconciliation | Local state remains paid, Wallet order stale | Refund/reversal mapping works for the tested order |
| Digital-goods separation | StoreKit route test for digital content | Apple Pay used where StoreKit is required | Product routing follows the appropriate platform purchase path |

## Wallet pass signing and distribution matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| Pass source | Source folder and pass.json review | Wrong style, missing fields, unlocalized content | Source describes the tested pass |
| Manifest | Manifest generated from the exact pass files | Extra metadata, changed asset after hashing | Manifest covers the distributed source |
| Detached signature | Signature verification with selected certificate | Unsigned fixture, wrong certificate, private key exposed | The selected pass bundle is signed |
| .pkpass bundle | Correct archive and MIME type | Wrong extension, corrupt zip, extra files | The distributed object is a valid candidate pass |
| Pass Type ID and serial | Metadata and issuer record | Duplicate/unstable serial, type mismatch | The pass identity is stable for the tested record |
| Product/server association | Order/member/event record tied to pass identity | User receives another person’s pass | App maps the pass to the intended record |
| App distribution | App/App Clip download and add flow | Download requires unsupported app, stale URL | The app distribution path works for the tested pass |
| Web distribution | Add to Apple Wallet badge/download with real pass | Wrong content type, redirect failure | Web distribution works for the tested route |
| Email distribution | Attachment and add flow | Mail client transforms attachment, stale pass | Email route works for the tested client/device |
| Multiple-pass bundle | .pkpasses bundle with tested limits | Oversize/count rejection, partial add unclear | Multi-pass distribution works for the selected bundle |

## Add, library, and update matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| PKPass initialization | Signed pass data initializes in the app | Unsigned local JSON, wrong signature, corrupt bytes | The app accepted the tested pass object |
| Add one pass | PKAddPassesViewController system UI | Missing presentation context, cancellation ignored | Person could review/add the tested pass |
| Add multiple passes | PKPassLibrary.addPasses completion status | Review status not presented, partial outcome lost | The selected multi-pass outcome is handled |
| Already present | containsPass or current library check for the allowed scope | Duplicate add prompt, stale local flag | App handles an already-present tested pass |
| Pass library access | Entitlement and physical-library observation | App assumes full Wallet access, thread race | App can access only the tested entitled scope |
| Library change | Pass-library notification/refresh on a single isolation path | Stale list, non-thread-safe access, duplicate UI | App reconciles observed library changes |
| User removal | Direct user removal and app refresh | App silently re-adds, backend state overwritten | Removal is handled as user-owned state |
| Signed replacement | New pass with same identifier and serial | In-place local mutation, mismatched identity | Replacement behavior works for the tested pass |
| Update registration | Device/pass registration request and database record | Authentication token leak, duplicate registration | The update service registered the tested device/pass |
| Update push | Provider/APNs trace in the documented environment | Development push assumed to prove production, invalid token retained | Push reached the selected update environment |
| Changed serial request | Server returns changed serials and update tag | Always returns all passes, stale tag, wrong auth | The update listing route works for the tested device |
| Updated pass response | Signed response with correct content type and auth | Wrong serial, stale signature, 401 mishandled | The selected pass update was delivered |
| Revoke/expire | Server/pass state and Wallet observation | App deletes user pass without intent, stale order status | Revocation/expiration behavior is evidenced for the route |

## Wallet order details matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| Placed-order identity | Server/provider record exists before order details | Details attached to a draft or failed auth | Order details identify a placed order |
| PKPaymentOrderDetails construction | Type ID, order ID, web service URL, and scoped token fixture | Token in logs, unstable identifier, wrong service URL | Object is configured for the selected order service |
| Successful authorization result | Order details attached only to success | Details attached after failure/cancel | Wallet order handoff was requested for the observed success |
| Order service | Authentication, current status, receipt/tracking response | Stale status, exposed tokens, no update path | Order service returned the observed data |
| App/Wallet consistency | App receipt compared with Wallet order | App says fulfilled while Wallet says pending | The tested projection is reconciled, not universal |

## Privacy, accessibility, and AI matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| Data minimization | Redacted logs, payload review, retention decision | Payment token, contact, pass token, or barcode in logs | Selected build avoids unnecessary sensitive output |
| Locked/shared context | Lock Screen, notification, and task review | Order/pass identity exposed to bystanders | Tested surfaces use the chosen privacy policy |
| VoiceOver | Complete checkout/add/view/update task | Focus lost after system handoff, status not announced | The selected task is accessible on tested settings |
| Dynamic Type | Largest supported sizes and localized strings | Amount/date/barcode label clips | Tested app-owned surfaces adapt |
| Reduced transparency/motion | Physical settings or controlled UI test | Glass hides status, animation is only feedback | State remains understandable with effects reduced |
| AI extraction | Fixtures with ambiguous/malformed receipt or event input | Model invents amount, pass ID, or identity | Model output is a proposal with deterministic validation |
| Human review | UI test that edits proposed amount/recipient/date | Auto-submit or auto-add | Side effects require the tested user action |
| No-model fallback | Model unavailable/canceled/unsupported route | Commerce blocked by AI availability | Deterministic manual route remains usable |

## Required evidence packet

- Target name, SDK, deployment target, OS build, and device model.
- Merchant identifier, pass type ID, certificate environment, and signed entitlements.
- Provider/server name and sandbox/production state.
- Redacted request/response traces with order/pass identifiers.
- Screenshots or recording of the real system payment/add-pass surface.
- User actions for ready, cancel, decline, already-present, update, and failure states.
- Signed pass bundle and verification result, with private keys excluded.
- Wallet update registration/push/server evidence where used.
- App/Wallet/order state comparison after authorization and fulfillment.
- Accessibility settings, locale, Dynamic Type, reduced effects, and privacy observations.
- AI proposal, validation, review, and final side-effect record.

## Claim language

Use precise language:

- “The Apple Pay sheet presented on the tested device” rather than “Apple Pay works everywhere.”
- “The provider accepted the sandbox transaction” rather than “the order was delivered.”
- “The signed pass was added to Wallet for the tested user” rather than “the Wallet pass is universally valid.”
- “The order service returned the observed status” rather than “Wallet always stays current.”
- “The model proposed a pass field and the user approved it” rather than “AI purchased or issued the pass.”

## Sources

- [PassKit](https://developer.apple.com/documentation/passkit)
- [Setting up Apple Pay](https://developer.apple.com/documentation/PassKit/setting-up-apple-pay)
- [Offering Apple Pay in Your App](https://developer.apple.com/documentation/passkit/offering-apple-pay-in-your-app)
- [Apple Pay HIG](https://developer.apple.com/design/human-interface-guidelines/apple-pay)
- [Wallet HIG](https://developer.apple.com/design/human-interface-guidelines/wallet)
- [Wallet Passes](https://developer.apple.com/documentation/walletpasses)
- [Building a Pass](https://developer.apple.com/documentation/walletpasses/building-a-pass)
- [Creating the Source for a Pass](https://developer.apple.com/documentation/walletpasses/creating-the-source-for-a-pass)
- [Distributing and updating a pass](https://developer.apple.com/documentation/walletpasses/distributing-and-updating-a-pass)
- [Adding a Web Service to Update Passes](https://developer.apple.com/documentation/WalletPasses/adding-a-web-service-to-update-passes)
- [Register a Pass for Update Notifications](https://developer.apple.com/documentation/walletpasses/register-a-pass-for-update-notifications)
- [Get the List of Updatable Passes](https://developer.apple.com/documentation/walletpasses/get-the-list-of-updatable-passes)
- [Send an Updated Pass](https://developer.apple.com/documentation/walletpasses/send-an-updated-pass)
- [PKPaymentAuthorizationController](https://developer.apple.com/documentation/passkit/pkpaymentauthorizationcontroller)
- [PKPaymentAuthorizationControllerDelegate](https://developer.apple.com/documentation/passkit/pkpaymentauthorizationcontrollerdelegate)
- [PKPaymentRequest](https://developer.apple.com/documentation/passkit/pkpaymentrequest)
- [PKPaymentAuthorizationResult](https://developer.apple.com/documentation/passkit/pkpaymentauthorizationresult)
- [PKPaymentToken](https://developer.apple.com/documentation/passkit/pkpaymenttoken)
- [PKPaymentOrderDetails](https://developer.apple.com/documentation/passkit/pkpaymentorderdetails)
- [PKPaymentButton](https://developer.apple.com/documentation/passkit/pkpaymentbutton)
- [PKPass](https://developer.apple.com/documentation/passkit/pkpass)
- [PKPassLibrary](https://developer.apple.com/documentation/passkit/pkpasslibrary)
- [PKAddPassesViewController](https://developer.apple.com/documentation/passkit/pkaddpassesviewcontroller)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
