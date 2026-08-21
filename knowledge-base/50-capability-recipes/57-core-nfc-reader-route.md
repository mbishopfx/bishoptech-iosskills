# Core NFC reader and contactless capability route

Use this route when an app needs to read or write a nearby physical object, process a protocol-specific tag, receive a background universal-link handoff, or evaluate a CardSession contactless path. Start with the [Core NFC deep dive](../42-framework-deep-dives/34-core-nfc-tag-sessions-and-secure-ndef.md), the [NFC design guide](../21-design-deep-dives/54-nfc-tap-and-credential-review-design.md), and the [NFC proof matrix](../60-verification/51-core-nfc-reader-proof-matrix.md).

## Route selector

| If the product needs to… | Choose | Start with |
| --- | --- | --- |
| Read a standard NDEF message | NFCNDEFReaderSession | Capability, NFCReaderUsageDescription, NDEF parser |
| Read/write an NDEF tag through a protocol tag | NFCTagReaderSession plus NFCNDEFTag | Formats entitlement, tag configuration, status/capacity |
| Send ISO 7816 commands | NFCTagReaderSession plus NFCISO7816Tag | AID list, APDU allowlist, status-word mapping |
| Use FeliCa or MIFARE native commands | NFCTagReaderSession plus protocol interface | System/family configuration and real fixtures |
| Launch from a nearby URI without starting a scan in-app | Background tag reading | Associated Domains, universal link, activity validation |
| Process a payment or VAS tag | Specialized session | Region/program/account/entitlement eligibility |
| Emulate an ISO 7816 card | CardSession | HCE program entitlement, AID prefix route, physical reader |

Do not build a broad “NFC manager” that silently chooses a route based on whatever tag appears. Name the feature mode and select the session intentionally.

## Minimum target setup

1. Select an iOS or iPadOS target whose deployment range includes the APIs you intend to use.
2. Add the Near Field Communication Tag Reading capability when using tag-reader sessions.
3. Verify the signed target has the formats entitlement required by the route.
4. Add a non-empty NFCReaderUsageDescription string in the target’s Info.plist.
5. Add only the ISO 7816 application identifiers and FeliCa system codes that the product supports.
6. Add Associated Domains and universal-link configuration only when background reading is a real feature.
7. Treat CardSession HCE entitlements as a separate Apple-managed program gate.
8. Compile each protocol adapter in the actual application target rather than relying on a generic playground.

### Configuration worksheet

| Field | Decision |
| --- | --- |
| App target |  |
| Deployment target |  |
| SDK/Xcode |  |
| Route | NDEF / tag / background / payment / VAS / HCE |
| Reading hardware | iPhone / iPad model and OS |
| Formats entitlement |  |
| NFCReaderUsageDescription |  |
| ISO 7816 AIDs |  |
| FeliCa system codes |  |
| Associated domains |  |
| HCE approval and entitlements |  |
| Physical fixtures |  |
| Data-retention policy |  |
| Manual fallback |  |
| Signed artifact |  |

## Architecture

Keep the physical reader and app domain separate:

~~~text
ScanIntent
  -> NFCSessionCoordinator
     -> NFCNDEFReaderSession or NFCTagReaderSession
        -> protocol adapter
           -> CanonicalNFCObservation
              -> review model
                 -> optional on-device proposal
                    -> validated app action
~~~

For HCE, the direction is different:

~~~text
ContactlessMode
  -> CardSession eligibility gate
     -> eventStream
        -> typed APDU state machine
           -> response
              -> verified protocol result
                 -> app-owned completion
~~~

The coordinator owns one session and one operation revision. A canceled or invalidated revision cannot publish a late result over a newer scan.

## NDEF read route

Use NFCNDEFReaderSession for the simplest NDEF feature:

1. Check NFCNDEFReaderSession.readingAvailable.
2. Create the session with the intended invalidate-after-first-read policy.
3. Set a concise, localized alertMessage.
4. Begin the session from an explicit user action.
5. Decode messages or connect to the detected NFCNDEFTag.
6. Preserve the record array and a canonical projection.
7. Validate links, text encoding, type, size, and record count.
8. Present the decoded result for review.
9. Invalidate or restart polling deliberately.

Use a single-read policy for a one-shot “scan this object” feature. Use a multi-read policy only when the interface explains how subsequent objects are handled and how the person stops the session.

### NDEF write route

The write route adds a physical mutation:

~~~text
draft records
-> serialize
-> show exact result
-> query status/capacity
-> confirm write
-> writeNDEF
-> read back when meaningful
-> persist verification
~~~

Never write while the person is editing a draft without a final confirmation. Do not treat a callback with no error as proof that an external device or future reader will interpret the message as intended.

## Protocol tag route

Use NFCTagReaderSession.Configuration to constrain polling and application selection. In the detection callback:

1. Filter the candidate list by a supported concrete tag case.
2. Reject or explain multiple candidates.
3. Check the selected tag’s availability.
4. Connect exactly once for the operation.
5. Call the protocol adapter with typed input.
6. Map response/error to an app-owned result.
7. Invalidate or restart polling according to the feature.

### Adapter boundaries

| Adapter | Input | Output | Safety rule |
| --- | --- | --- | --- |
| NDEFAdapter | NFCNDEFTag | Status, capacity, records | Preserve source records; validate external destinations |
| ISO7816Adapter | NFCISO7816Tag and typed command | Payload plus SW1/SW2 | Allowlist commands/AIDs; never use model-generated APDUs |
| ISO15693Adapter | NFCISO15693Tag | Typed fixture/domain result | Keep identifier separate from authentication |
| FeliCaAdapter | NFCFeliCaTag | Poll/system/service result | Use declared discrete system codes |
| MIFAREAdapter | NFCMiFareTag | Family-specific response | Know family; do not claim Crypto1 support |

The app layer should not know how a protocol command is framed. It should consume a value such as “recognized inventory object,” “credential response rejected,” or “unrecognized physical item,” with provenance and error detail.

## Background tag route

If the product supports background reading:

1. Configure Associated Domains and universal links.
2. Ensure the app can process a direct launch as well as an activity continuation.
3. Validate the NSUserActivity and NDEF payload.
4. Resolve the associated domain and host policy.
5. Show the person the object and intended action.
6. Require confirmation for writes, purchases, sign-in, permission changes, or destructive operations.
7. Keep the in-app scanner as a fallback.

Background reading is not always available. The app should never make a direct scanner screen feel like a broken fallback; it is the primary route for unsupported or unavailable contexts.

## HCE/CardSession route

CardSession deserves its own target and review:

1. Check NFCReaderSession.readingAvailable, CardSession.isSupported, and CardSession.isEligible.
2. Create the session only after those checks.
3. Iterate eventStream.
4. Start emulation when the app is ready to answer APDUs.
5. Keep the APDU state machine bounded and deterministic.
6. Respond to every handled request within protocol timing.
7. Stop emulation with the correct status.
8. Invalidate on completion, cancellation, reader deselection, or session expiry.

Apple’s current documentation describes a 60-second emulation limit and requires an iPhone plus NFC reader hardware for testing. The route is restricted to approved use cases/program rules in the EEA. It is not a general replacement for Wallet, Apple Pay, or a server-side payment processor.

## Native SwiftUI composition

Keep the SwiftUI view declarative and move Core NFC delegate lifetime into a reference-type coordinator:

~~~text
ScanView
  -> ScanViewModel
     -> NFCSessionCoordinator
        -> session delegate
           -> MainActor state
              -> review sheet
~~~

The view should render ready, scanning, result, error, and saved states. It should not create or invalidate sessions from the view’s body. Make the scan start action idempotent and disable it while a session is owned.

Use standard toolbars, sheets, confirmation dialogs, and buttons for app-owned surfaces. Let the platform own the NFC sheet and CardSession modal. Apply custom Liquid Glass only to high-priority app actions, and test reduced transparency and motion.

## AI composition

The safe order is:

~~~text
physical observation
-> deterministic decode
-> reviewable source
-> optional local model proposal
-> schema validation
-> explicit approval
-> app-owned action
~~~

Good proposals include a title, category, or summary for a known record. Bad proposals include a generated APDU, guessed credential status, unverified URL action, or automatic write. Keep the model input to the minimum corrected projection and record model availability/version when the proposal affects the user’s record.

## Failure and fallback matrix

| Failure | User-facing meaning | Fallback |
| --- | --- | --- |
| reading unavailable | This device/environment cannot scan | Manual entry |
| missing usage description/configuration | The target is not configured correctly | Fix target before release |
| permission or capability denial | The feature cannot access the reader | Settings/manual route |
| multiple tags | The intended object is ambiguous | Ask the person to isolate one |
| tag lost | The physical object moved away | Hold near and retry; avoid blind mutation retry |
| unsupported protocol | The object is not supported by this feature | Explain supported objects |
| malformed NDEF | The message cannot be decoded safely | Show raw-safe summary/copy or discard |
| AID/security violation | The configured command is not allowed | Correct target configuration; do not probe |
| CardSession ineligible | HCE is not available in this environment | Use an approved system/provider route |
| background unavailable | The system could not hand off automatically | In-app scanner |

## Evidence packet

For every route, retain:

- target name, SDK, deployment target, and build;
- signed Info.plist and entitlement dump;
- physical device model and OS;
- tag protocol, fixture identifier, and expected result;
- session state logs without raw secrets;
- malformed, cancellation, loss, and retry evidence;
- accessibility settings and manual fallback evidence;
- any regional/account/program eligibility record;
- app-owned commit and deletion evidence.

Use the [compile-oriented recipes](../70-code-recipes/69-core-nfc-reader-recipes.md) as route sketches only. The [proof matrix](../60-verification/51-core-nfc-reader-proof-matrix.md) defines the minimum evidence for each claim.

## Sources

- [Core NFC](https://developer.apple.com/documentation/corenfc)
- [Building an NFC Tag-Reader App](https://developer.apple.com/documentation/corenfc/building-an-nfc-tag-reader-app)
- [NFCNDEFReaderSession](https://developer.apple.com/documentation/corenfc/nfcndefreadersession)
- [NFCNDEFReaderSessionDelegate](https://developer.apple.com/documentation/corenfc/nfcndefreadersessiondelegate)
- [NFCNDEFTag](https://developer.apple.com/documentation/corenfc/nfcndeftag)
- [NFCNDEFStatus](https://developer.apple.com/documentation/corenfc/nfcndefstatus)
- [NFCNDEFPayload](https://developer.apple.com/documentation/corenfc/nfcndefpayload)
- [NFCTagReaderSession](https://developer.apple.com/documentation/corenfc/nfctagreadersession)
- [NFCTagReaderSession.Configuration](https://developer.apple.com/documentation/corenfc/nfctagreadersession/configuration)
- [NFCTag](https://developer.apple.com/documentation/corenfc/nfctag-swift.enum)
- [NFCISO7816Tag](https://developer.apple.com/documentation/corenfc/nfciso7816tag)
- [NFCISO7816APDU](https://developer.apple.com/documentation/corenfc/nfciso7816apdu)
- [NFCISO15693Tag](https://developer.apple.com/documentation/corenfc/nfciso15693tag)
- [NFCFeliCaTag](https://developer.apple.com/documentation/corenfc/nfcfelicatag)
- [NFCMiFareTag](https://developer.apple.com/documentation/corenfc/nfcmifaretag)
- [Adding Support for Background Tag Reading](https://developer.apple.com/documentation/corenfc/adding-support-for-background-tag-reading)
- [CardSession](https://developer.apple.com/documentation/corenfc/cardsession)
- [NFCPaymentTagReaderSession](https://developer.apple.com/documentation/corenfc/nfcpaymenttagreadersession)
- [NFCVASReaderSession](https://developer.apple.com/documentation/corenfc/nfcvasreadersession)
- [NFCReaderUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nfcreaderusagedescription)
- [Near Field Communication Tag Reader Session Formats Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.nfc.readersession.formats)
- [ISO7816 application identifiers for NFC Tag Reader Session](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.nfc.readersession.iso7816.select-identifiers)
- [ISO18092 system codes for NFC Tag Reader Session](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.nfc.readersession.felica.systemcodes)
- [NFC](https://developer.apple.com/design/human-interface-guidelines/nfc)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
