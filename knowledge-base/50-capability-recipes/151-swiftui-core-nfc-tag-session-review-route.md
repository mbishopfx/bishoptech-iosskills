# SwiftUI Core NFC tag-session route

This route turns a contactless idea into a bounded Apple-native implementation plan. Select the smallest Core NFC lane that can satisfy the outcome, then prove the exact device, entitlement, physical fixture, and release behavior. A working NDEF reader is not evidence for CardSession, payment tags, or an ISO 7816 product.

Related material:

- [Core NFC framework review](../42-framework-deep-dives/120-swiftui-core-nfc-tag-session-review.md)
- [Core NFC design review](../21-design-deep-dives/148-swiftui-core-nfc-tag-session-review-design.md)
- [Core NFC proof matrix](../60-verification/145-swiftui-core-nfc-tag-session-proof-matrix.md)
- [Core NFC code recipes](../70-code-recipes/163-swiftui-core-nfc-tag-session-review-recipes.md)

## 1. Write the outcome in protocol language

Complete this sentence before writing SwiftUI:

    A person wants to [verb] a [tag/reader/card] so the app can [bounded outcome].

Choose one:

| Outcome | Start here |
| --- | --- |
| Read a URL, text, or app-owned record | NFCNDEFReaderSession |
| Write an NDEF message | NFCNDEFReaderSession plus NFCNDEFTag |
| Read/write protocol blocks or issue APDUs | NFCTagReaderSession |
| Open a destination from a passive tap | Background tag reading plus universal links |
| Present an app-owned ISO 7816 credential | CardSession, only after the HCE program path |
| Read payment or VAS content | Specialized Apple entitlement/program route |
| React to a reader/presentment event in a scene | NFCWindowSceneDelegate |

If the outcome is “identify a real-world object,” define how the app verifies it. NFC presence, a UID, or a decoded URL alone does not establish authenticity.

## 2. Configuration worksheet

Record the following in the feature plan:

| Field | Decision |
| --- | --- |
| Deployment target | Exact minimum iOS version |
| Target SDK | Exact Xcode/SDK used to compile |
| Reader lane | NDEF, generic tag, background, CardSession, payment, or VAS |
| Supported tag technologies | NDEF, ISO 7816, ISO 15693, FeliCa, MIFARE |
| Privacy purpose | Human-readable NFCReaderUsageDescription |
| Formats entitlement | Required for NFCTagReaderSession |
| ISO7816 AIDs | Exact values and selection order |
| FeliCa system codes | Exact values; no wildcard assumption |
| Associated domains | Production universal-link domain and paths |
| HCE program status | Requested/approved/not applicable |
| Device fixture | Physical iPhone model and tag/reader models |
| Fallback | Manual, QR, import, or non-contactless workflow |

The Xcode capability, entitlements file, signed archive, and installed TestFlight build must be compared. A local project setting is not release evidence.

## 3. Preflight route

At the moment the person selects the action:

1. Check the target’s availability annotations and compile the current API.
2. Check NFCReaderSession.readingAvailable.
3. For CardSession, check isSupported and isEligible.
4. Check camera or other unrelated route conflicts if the feature shares a screen.
5. Confirm the required usage description and capability are in the application target.
6. Confirm the scene can own the route.
7. Create a generation token.
8. Present the system-owned route only after the above checks pass.

Preflight output should be value state:

    enum NFCAvailability {
        case checking
        case unsupported
        case configurationRequired
        case regionOrProgramRestricted
        case ready
    }

Do not create a live reader session while a view is merely appearing. The person’s action is the permission boundary for scanning.

## 4. NDEF read route

### Start

Create NFCNDEFReaderSession with:

- a retained coordinator conforming to NFCNDEFReaderSessionDelegate;
- the intended callback queue;
- invalidateAfterFirstRead set according to the product;
- a fresh generation.

Set the alert message before begin. The coordinator owns the session until didInvalidateWithError.

### Detect

For one-shot reading, handle the NDEF message callback, capture the records in order, and invalidate or let the configured session end. For a write-capable flow, handle the NFCNDEFTag callback, connect to the tag, and query availability/status before reading or writing.

The state transition is:

    ready
      -> session active
      -> NDEF detected
      -> bounded record envelope
      -> deterministic decode
      -> validation
      -> review

Persist the record envelope only after the app has decided what source retention is appropriate. Do not store the framework tag object.

### Decode

Attempt the documented well-known text and URI decoders only when the type name format and record type fit the route. Preserve raw type, identifier, payload, record index, and length. Unknown records should produce a safe “unsupported but preserved” state, not a silent discard.

### Act

Open a URL, save a label, or invoke an app feature only after validation and user intent. For domain-owned URLs, check scheme, host, path, and size. For app-owned records, validate the version and bounded fields.

## 5. NDEF write route

The write route has two distinct decisions:

1. Does the tag support read/write NDEF and have enough capacity?
2. Does the person approve replacing its current message?

Run:

    connect
      -> queryNDEFStatus
      -> status == readWrite
      -> proposedMessage.length <= capacity
      -> preview exact ordered records
      -> explicit Write confirmation
      -> writeNDEF
      -> optional read-back

Treat read-only, not-supported, too-small, moved, and write-failed as different results. Keep the draft in app state so a retry does not rebuild it from a stale view.

The lock route must be separate:

    preview warning
      -> separate destructive confirmation
      -> writeLock
      -> show read-only result

If the app never needs permanent locking, omit the control.

## 6. Generic tag/protocol route

Use NFCTagReaderSession when the app needs a protocol-specific interface. The delegate receives an NFCTag value. Switch over its technology and adapt only to the protocol the feature supports.

### ISO 7816 adapter

1. Configure the permitted ISO7816 application identifiers.
2. Record selection order and the expected initial selected AID.
3. Connect to the tag.
4. Construct the exact APDU.
5. Send one command at a time while preserving protocol state.
6. Decode bounded response data and SW1/SW2.
7. Continue only if the protocol says the next step is valid.
8. Redact sensitive bytes in diagnostics.

Never send an arbitrary SELECT AID that is absent from the entitlement configuration. Do not interpret a successful transport callback as a successful business transaction.

### ISO 15693 adapter

Define the request flags, block ranges, read/write commands, and lock behavior before presentation. Keep block numbers and byte lengths visible in an expert diagnostic view, not necessarily in the consumer UI. Test multi-block and tag-moved behavior.

### FeliCa adapter

Declare the exact system codes, poll within the supported configuration, and model service/block responses. Do not use a wildcard or infer access to an undeclared system code.

### MIFARE adapter

Branch on the MIFARE family and use the command shape the tag expects. Pay attention to the documented DESFire NDEF AID behavior: including the NDEF AID in the ISO7816 selector list can cause the reader to deliver an NFCISO7816Tag instead of an NFCMiFareTag for that application.

## 7. Background URI route

Background tag reading is a universal-link route:

    NFC URI record
      -> system notification
      -> user unlock/interaction as required
      -> associated-domain resolution
      -> NSUserActivity / URL handling
      -> host/path validation
      -> app context

Implement both cold-scene and existing-scene delivery. Store the incoming URL as value state, not as a command that automatically commits. If the app cannot validate the host/path, show a safe fallback or let the person use Safari when appropriate.

Keep direct scan in the product because background reading can be unavailable when the device is locked, a reader session is active, Apple Pay or Wallet is in use, the camera is in use, or other system conditions apply.

## 8. CardSession route

Use CardSession only for an approved HCE/contactless product:

1. Check NFCReaderSession.readingAvailable.
2. Check CardSession.isSupported.
3. Check CardSession.isEligible.
4. Confirm the signed HCE entitlement and handled AID prefixes.
5. Create CardSession with the current async API.
6. Start an event-stream consumer.
7. Set an alert message that helps the person orient the device.
8. Start emulation after explicit action.
9. Answer APDU events promptly from precomputed state.
10. Handle readerDetected, received, readerDeselected, and invalidation.
11. Stop with an appropriate EmulationUIStatus.
12. Record the physical-reader result and any expiration.

Precompute as much as possible. A model call, network request, or user edit does not belong in the APDU response deadline. Treat the current documented maximum emulation time as a hard design constraint and verify it on a real device.

If the user gesture competes with the system default contactless app, use NFCPresentmentIntentAssertion only after active user intent and only while the app is foregrounded. It expires quickly and has a cooldown; model it as a short-lived assertion, not a permanent capability.

## 9. SwiftUI integration route

Keep one feature model for app-owned values:

    view
      -> feature model
      -> coordinator/session
      -> Core NFC callback
      -> feature event
      -> reducer
      -> review view

The model owns:

- availability;
- current lane;
- generation;
- status;
- bounded source envelope;
- proposal;
- review state;
- error category;
- fallback choice.

The coordinator owns:

- session;
- delegate;
- callback queue;
- connected tag reference;
- cancellation;
- teardown.

Use UIViewControllerRepresentable only where a UIKit controller is part of the route. A reader session itself can be coordinated without embedding a controller. Never put the session in SwiftUI view identity, a persisted model, or the body.

## 10. AI route

The optional AI path is:

    deterministic NDEF/protocol output
      -> privacy filter and size bound
      -> local model availability
      -> generated proposal
      -> source-backed review
      -> explicit commit

Allowed examples:

- classify an app-owned tag into a user-selected category;
- summarize a long text record on device;
- suggest a name for a verified accessory;
- extract fields from a versioned app-owned external record.

Not allowed as an automatic default:

- treating a generated label as tag authentication;
- putting APDU credentials or payment data into a prompt;
- allowing a generated URL to open without validation;
- writing or locking a tag from generated output;
- presenting a credential or triggering a physical side effect without a deterministic, user-approved policy.

If the model is unavailable, show the deterministic decoded record and manual actions.

## 11. Route-specific test fixtures

Build fixtures before polishing:

| Fixture | Expected route |
| --- | --- |
| Empty NDEF message | Read result with no decoded action |
| Well-known text | Bounded text review |
| URI with allowed host | Validated app route |
| URI with unexpected scheme/host | Safe rejection |
| Multiple ordered records | Record order retained |
| External app record | Version/schema validation |
| Malformed/oversized record | Bounded failure |
| Read-only tag | Read-only state; no write control |
| Read-write small-capacity tag | Capacity failure with edit route |
| Tag moves during read/write | Retry with draft preserved |
| ISO 7816 known AID | Selection and status-word route |
| ISO 7816 unsupported AID | Configuration/selection failure |
| ISO 15693 block fixture | Block/read/write/lock policy |
| FeliCa declared system code | Poll/service route |
| MIFARE family variants | Family-specific adapter |
| No physical NFC | Manual/import fallback |
| Background link cold launch | Scene connection options |
| Background link warm launch | Existing-scene activity delivery |
| CardSession no reader | Invalidation or timeout state |
| CardSession reader and APDU | Prompt response and final status |

## 12. Release packet

Before calling the feature shipped, attach:

- target SDK and deployment target;
- Info.plist usage text;
- entitlements from the signed archive;
- Associated Domains configuration if used;
- physical device and tag/reader fixture IDs;
- sanitized session traces;
- screenshots or recording of ready, active, review, failure, and fallback states;
- accessibility evidence with VoiceOver and Dynamic Type;
- Reduce Motion/Transparency result;
- TestFlight install and production-domain universal-link check;
- model availability/fallback result if AI is included;
- App Store and entitlement review notes for specialized routes.

The proof matrix is the stop point for this route. A simulator build can validate reducers and decoders; it cannot validate the NFC radio, a tag’s memory behavior, a contactless reader, or Apple-managed HCE eligibility.

## Sources

- [Core NFC](https://developer.apple.com/documentation/corenfc)
- [NFCNDEFReaderSession](https://developer.apple.com/documentation/corenfc/nfcndefreadersession)
- [NFCNDEFReaderSessionDelegate](https://developer.apple.com/documentation/corenfc/nfcndefreadersessiondelegate)
- [NFCTagReaderSession](https://developer.apple.com/documentation/corenfc/nfctagreadersession)
- [NFCNDEFTag](https://developer.apple.com/documentation/corenfc/nfcndeftag)
- [NFCNDEFMessage](https://developer.apple.com/documentation/corenfc/nfcndefmessage)
- [NFCNDEFPayload](https://developer.apple.com/documentation/corenfc/nfcndefpayload)
- [NFCISO7816Tag](https://developer.apple.com/documentation/corenfc/nfciso7816tag)
- [NFCISO7816APDU](https://developer.apple.com/documentation/corenfc/nfciso7816apdu)
- [NFCISO7816ResponseAPDU](https://developer.apple.com/documentation/corenfc/nfciso7816responseapdu)
- [NFCISO15693Tag](https://developer.apple.com/documentation/corenfc/nfciso15693tag)
- [NFCFeliCaTag](https://developer.apple.com/documentation/corenfc/nfcfelicatag)
- [NFCMiFareTag](https://developer.apple.com/documentation/corenfc/nfcmifaretag)
- [Adding support for background tag reading](https://developer.apple.com/documentation/corenfc/adding-support-for-background-tag-reading)
- [CardSession](https://developer.apple.com/documentation/corenfc/cardsession)
- [NFCPresentmentIntentAssertion](https://developer.apple.com/documentation/corenfc/nfcpresentmentintentassertion)
- [NFCWindowSceneDelegate](https://developer.apple.com/documentation/corenfc/nfcwindowscenedelegate)
- [NFCWindowSceneEvent](https://developer.apple.com/documentation/corenfc/nfcwindowsceneevent)
- [Near Field Communication Tag Reader Session Formats Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.nfc.readersession.formats)
- [ISO7816 application identifiers for NFC Tag Reader Session](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.nfc.readersession.iso7816.select-identifiers)
- [ISO18092 system codes for NFC Tag Reader Session](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.nfc.readersession.felica.systemcodes)
- [HCE ISO 7816 select identifier prefixes entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.nfc.hce.iso7816.select-identifier-prefixes)
- [Universal links](https://developer.apple.com/documentation/xcode/allowing-apps-and-websites-to-link-to-your-content/)
- [NSUserActivity](https://developer.apple.com/documentation/foundation/nsuseractivity)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
