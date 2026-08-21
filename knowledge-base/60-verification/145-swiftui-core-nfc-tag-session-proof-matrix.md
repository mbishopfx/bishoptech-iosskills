# Core NFC tag-session proof matrix

This matrix defines what evidence is required before a Core NFC feature is described as working. NFC has several independent proof layers: source/API correctness, SwiftUI lifecycle correctness, signed capabilities, physical radio behavior, protocol semantics, accessibility, privacy, and distribution. Passing one layer does not pass the others.

Related pages:

- [Core NFC framework review](../42-framework-deep-dives/120-swiftui-core-nfc-tag-session-review.md)
- [Core NFC design review](../21-design-deep-dives/148-swiftui-core-nfc-tag-session-review-design.md)
- [Core NFC route](../50-capability-recipes/151-swiftui-core-nfc-tag-session-review-route.md)
- [Core NFC code recipes](../70-code-recipes/163-swiftui-core-nfc-tag-session-review-recipes.md)

## 1. Evidence levels

| Level | Evidence | Proves | Does not prove |
| --- | --- | --- | --- |
| P0 | Apple documentation and current SDK symbol review | API and policy understanding | Build or device behavior |
| P1 | Unit tests for decoders/reducers | Deterministic app logic | NFC hardware or entitlements |
| P2 | Simulator/UI test | Value-state UI and navigation | NFC radio, real tag, reader, region eligibility |
| P3 | Development signed build on physical iPhone | Permission/capability integration and radio path | TestFlight signing, production domains, final program approval |
| P4 | Physical fixture matrix | Tag/reader and protocol behavior | Long-term distribution reliability |
| P5 | Archive/TestFlight install | Signed artifact and shipped configuration | App Store approval or every hardware variant |
| P6 | Release runbook and support evidence | Reproducible shipped route | New OS/device behavior without re-running |

Use the highest level required by the route. NDEF read-only can stop earlier than HCE, but no physical NFC route should be called complete from simulator evidence alone.

## 2. Gate matrix

| ID | Gate | Pass evidence | Failure meaning |
| --- | --- | --- | --- |
| F0 | Scope lane | Feature plan names NDEF, generic tag, background, specialized, or CardSession | Route ambiguity |
| F1 | SDK availability | Compiles against the selected iOS 26 SDK with availability handling | Wrong API/target assumption |
| F2 | Runtime NFC gate | NFCReaderSession.readingAvailable is checked before presentation | Device/system unavailable |
| F3 | Privacy text | NFCReaderUsageDescription exists in the application target and explains intent | Missing or misleading permission contract |
| F4 | Reader capability | Signed app contains required formats entitlement | Local Xcode configuration is incomplete |
| F5 | Protocol configuration | AIDs/system codes are present and match the intended fixtures | Selection or entitlement mismatch |
| F6 | Session ownership | One retained session, delegate, generation, begin, and invalidation path | Duplicate/stale callbacks |
| F7 | NDEF envelope | Record order, type, identifier, payload, length, and digest are preserved | Lossy/unsafe interpretation |
| F8 | Decoder policy | Text/URI/custom records are bounded and validated | Malicious or surprising payload action |
| F9 | NDEF status | notSupported/readOnly/readWrite and capacity are handled | Unsafe write path |
| F10 | Write proof | Explicit preview, write, result, and optional read-back evidence | Unverified physical mutation |
| F11 | Lock proof | Separate destructive confirmation and physical read-only behavior | Accidental irreversible action |
| F12 | Protocol adapter | ISO 7816/15693/FeliCa/MIFARE commands and responses match fixtures | Generic tag assumptions |
| F13 | APDU proof | AID selection, command fields, status words, timeouts, and sensitive logging reviewed | Transport mistaken for authorization |
| F14 | Background proof | Cold/warm scene universal-link handoff and validation | Link path assumed from in-app scan |
| F15 | Specialized eligibility | Payment/VAS/HCE entitlement, region, account, and device gates documented | Unsupported program claim |
| F16 | CardSession timing | Real reader, APDU response deadline, stop/invalidate, and duration proof | Reader timeout or false success |
| F17 | SwiftUI lifecycle | View disappearance cancels route; late callbacks are ignored | Stale UI mutation |
| F18 | AI boundary | Source/provenance/review/fallback proof | Generated output treated as physical truth |
| F19 | Accessibility | VoiceOver, Dynamic Type, alternate input, reduced motion/transparency | Proximity-only or unreadable route |
| F20 | Distribution | Archive/TestFlight and production associated-domain verification | Debug-only behavior |

## 3. Fixture inventory

Record tag model, protocol, memory/capacity, contents, and physical test date. Do not place real credentials, personal identifiers, or payment material in fixtures used for logs or screenshots.

| Fixture | Required observation |
| --- | --- |
| Empty NDEF tag | Empty records are represented without a fake success value |
| Well-known text | Locale and text are preserved; bounded rendering |
| Well-known URI | Scheme/host validation and explicit action |
| Multiple URI records | Record order and background first-URI policy are understood |
| External type | Version/schema path and raw field preservation |
| Media/absolute URI | Unsupported or supported decoder is explicit |
| Chunked/unknown record | No crash, no silent destructive action |
| Read-only NDEF | Read succeeds; write controls are disabled |
| Read-write NDEF | Status and capacity shown before write |
| Small-capacity tag | Oversized proposal is rejected before mutation |
| Lockable tag | Lock is separate and physical result is verified |
| Tag moved during read | Session invalidation/error mapped to retry |
| Multiple tags in field | User guidance and retry behavior |
| ISO 7816 AID fixture | Selection order, initial selected AID, APDU status |
| Unsupported AID fixture | Safe configuration/selection failure |
| ISO 15693 block fixture | Single/multiple block reads and writes, lock policy |
| FeliCa system-code fixture | Declared system-code poll and service result |
| MIFARE family fixtures | Family branching and command framing |
| Contactless reader | CardSession readerDetected, received, deselected |
| No contactless reader | CardSession retry/invalidation state |

## 4. NDEF reader tests

### Deterministic tests

- A message with zero records returns an empty result.
- Record order is preserved.
- Type Name Format is recorded for every record.
- Type and identifier bytes are not lost when a convenience decoder fails.
- URI decoder output is rejected for an unsupported scheme.
- URI host/path validation rejects unexpected destinations.
- Text decoding bounds size and preserves locale when available.
- An unknown external type remains available as raw, bounded data.
- Oversized record or message is rejected before it reaches a model or URL handler.
- Digest/provenance changes when source bytes change.

### Physical tests

- readingAvailable false hides or disables scan.
- The system reader alert appears after the user action.
- didBecomeActive does not show a result.
- NDEF detection creates one result and one explicit invalidation for a one-shot route.
- Tag movement produces a retryable state.
- Multiple tag detection produces actionable guidance.
- Session cancellation stops the route and late callbacks do not repopulate the next screen.

## 5. NDEF write and lock tests

For each fixture, capture:

    pre-status
    pre-capacity
    proposed-record-digest
    proposed-length
    user-confirmed-at
    write-result
    read-back-result
    post-status

Required assertions:

- notSupported never exposes a write action;
- readOnly never calls writeNDEF;
- readWrite still checks capacity;
- an exact-capacity message is tested;
- an over-capacity message fails before writing;
- existing records are shown as replaced or preserved according to the actual message;
- write failure does not show a success state;
- read-back mismatch is not hidden behind a green check;
- writeLock is never called from the normal Write action;
- lock confirmation includes an irreversible warning;
- after a verified lock, the tag reports read-only behavior;
- a cancelled confirmation makes no physical change.

## 6. Protocol and APDU tests

### ISO 7816

| Test | Expected evidence |
| --- | --- |
| Declared AID selection | System selects the intended app and reports initial selection state |
| AID order change | Behavior is documented and selection remains intentional |
| Undeclared SELECT | Safe rejection/security error; no arbitrary retry |
| APDU framing | CLA, INS, P1, P2, data, and Le match the protocol fixture |
| Success status | SW1/SW2 mapped to the specific protocol result |
| Retry status | The UI explains retry/verification rather than generic success |
| Unexpected length | Response is bounded and surfaced as a protocol error |
| Tag moved | In-flight command ends safely and state can restart |
| Sensitive response | Logs and AI envelopes redact it |

### ISO 15693, FeliCa, and MIFARE

- Test the required entitlement and adapter type.
- Test identifier handling without presenting a UID as proof of ownership.
- Test native read, write, custom, and lock commands only for the fixture family that supports them.
- Test request flags, block/service ranges, and response errors.
- Verify that a command that succeeds at the transport layer has the expected protocol meaning.
- Verify the documented MIFARE DESFire NDEF AID selection behavior.

## 7. Background tag-reading tests

Test on a supported physical iPhone and production-like associated-domain setup:

| State | Expected |
| --- | --- |
| App not running, phone unlocked | System notification/handoff resolves after user interaction |
| App not running, phone locked | Unlock requirement is handled |
| App running in foreground | Direct route and background behavior do not duplicate commands |
| App in background with existing scene | NSUserActivity/scene handling updates value state |
| No associated app | Safari or documented fallback is safe |
| Unexpected scheme | App refuses unsafe route |
| Unexpected host/path | App shows unrecognized link state |
| Multiple URI records | The background policy is deterministic |
| Reader session active | Direct scan remains the chosen route; no duplicate handoff |
| Camera/Wallet/airplane/system condition | Fallback is available |

Capture the exact URL only in a controlled test log. Production logs should retain a redacted route or digest.

## 8. CardSession/HCE tests

HCE evidence is a separate packet:

- physical iPhone is supported and eligible;
- signed app has Apple-approved HCE entitlement;
- handled AID or prefix matches the reader;
- session creation succeeds on an approved test account/region;
- readerDetected and presentation scene events update UI without claiming success;
- startEmulation shows the system presentation;
- APDU responses are produced within the protocol deadline;
- readerDeselected has a clear final state;
- session invalidation is handled without a stuck “presenting” badge;
- no-reader and ineligible states have fallback copy;
- maximum duration behavior is observed on a real reader;
- stopEmulation uses the intended EmulationUIStatus;
- presentment-intent assertion is acquired only after active intent;
- assertion expiration and cooldown are handled;
- CardSession is never inferred from a generic NDEF scan.

Do not store reader APDUs or credentials in screenshots, crash logs, or AI evaluation fixtures.

## 9. Scene and SwiftUI tests

Run these reducer/UI tests without Core NFC hardware:

- starting twice is idempotent or rejected;
- a new generation invalidates callbacks from the old generation;
- scene deactivation cancels only the owned route;
- cancellation clears the live session and leaves draft data when appropriate;
- active, detected, connected, reviewing, and invalidated states map to the correct accessibility label;
- a protocol error never transitions to committed;
- a model proposal cannot bypass review;
- a background URL can be delivered cold or warm and does not execute twice;
- presentation and reader-detected scene events update the same feature model safely.

Run these UI checks:

- VoiceOver order is source, status, warning, primary action, fallback;
- Dynamic Type at the largest supported sizes keeps Write/Lock warnings readable;
- keyboard and switch control can start the route;
- Reduce Motion removes decorative scanning pulses;
- Reduce Transparency preserves state contrast;
- the result card can be reviewed without proximity.

## 10. Privacy and security checks

- Confirm NFCReaderUsageDescription describes the actual feature.
- Review every raw payload, tag identifier, UID, APDU, status response, and URL logged.
- Redact or hash identifiers in analytics.
- Bound data before decoding, persisting, displaying, or sending to any model.
- Reject untrusted URL schemes and domains.
- Do not claim physical authenticity without a real authentication protocol.
- Keep card credentials and secure-messaging material out of prompts and crash reports.
- Review retention and deletion of scanned records.
- Test app behavior with the network unavailable when the feature claims to be on-device.

## 11. Source, archive, and live route review

The source review should record:

- the exact API URLs used by the implementation;
- the date the review was made;
- the SDK target;
- every availability/entitlement/region caveat;
- the distinction between documented behavior and app inference.

The archive review should inspect:

- embedded NFC reader formats;
- ISO7816 AIDs and FeliCa system codes where used;
- HCE entitlements where approved;
- NFCReaderUsageDescription in the final bundle;
- Associated Domains in the final app;
- the intended device family and deployment target.

The live release review should install the TestFlight artifact, use a physical fixture, and test at least one failure path. A local simulator screenshot is not a release packet.

## 12. Evidence log template

    Feature:
    Lane:
    Build:
    SDK:
    Device:
    iOS:
    Tag or reader fixture:
    Entitlement digest:
    Usage-description verified:
    Test date:
    Preconditions:
    Steps:
    Observed session events:
    Sanitized result:
    Expected:
    Accessibility result:
    Fallback result:
    Evidence level:
    Open issue:

## Sources

- [Core NFC](https://developer.apple.com/documentation/corenfc)
- [NFCNDEFReaderSession](https://developer.apple.com/documentation/corenfc/nfcndefreadersession)
- [NFCNDEFReaderSessionDelegate](https://developer.apple.com/documentation/corenfc/nfcndefreadersessiondelegate)
- [NFCReaderSessionProtocol](https://developer.apple.com/documentation/corenfc/nfcreadersessionprotocol)
- [NFCNDEFTag](https://developer.apple.com/documentation/corenfc/nfcndeftag)
- [NFCNDEFStatus](https://developer.apple.com/documentation/corenfc/nfcndefstatus)
- [NFCNDEFMessage](https://developer.apple.com/documentation/corenfc/nfcndefmessage)
- [NFCNDEFPayload](https://developer.apple.com/documentation/corenfc/nfcndefpayload)
- [NFCTagReaderSession](https://developer.apple.com/documentation/corenfc/nfctagreadersession)
- [NFCTagReaderSessionDelegate](https://developer.apple.com/documentation/corenfc/nfctagreadersessiondelegate-2joku?changes=_1)
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
- [Entitlements](https://developer.apple.com/documentation/bundleresources/entitlements)
- [Near Field Communication Tag Reader Session Formats Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.nfc.readersession.formats)
- [ISO7816 application identifiers for NFC Tag Reader Session](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.nfc.readersession.iso7816.select-identifiers)
- [ISO18092 system codes for NFC Tag Reader Session](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.nfc.readersession.felica.systemcodes)
- [HCE ISO 7816 select identifier prefixes entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.nfc.hce.iso7816.select-identifier-prefixes)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
