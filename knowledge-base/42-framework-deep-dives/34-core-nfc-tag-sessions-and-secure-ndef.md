# Core NFC tag sessions, NDEF, and contactless routes

Core NFC is a family of physical-radio routes, not one generic “scan” API. A good design starts by naming the thing the app is trying to do:

~~~text
user outcome
-> NDEF message, protocol tag, background handoff, payment/VAS session, or card emulation
-> target capability and signed entitlement
-> system reader/session lifecycle
-> deterministic decode or protocol adapter
-> user review
-> app-owned record or explicitly approved side effect
~~~

The fact that an iPhone detected a radio target is only an observation. It does not establish that the target is the intended object, that its payload is safe, that a credential is valid, that a payment succeeded, or that a person authorized an app action.

## Choose the narrowest Core NFC route

| Desired outcome | Primary route | What the route provides | What remains app-owned |
| --- | --- | --- | --- |
| Read a physical object’s NDEF message | NFCNDEFReaderSession | A system reader sheet and NDEF messages/tags | Payload validation, URL policy, record interpretation, and persistence |
| Read or write a tag through a supported native protocol | NFCTagReaderSession | A generic NFCTag plus ISO 7816, ISO 15693, FeliCa, or MIFARE interfaces | Protocol framing, command allowlists, authentication, replay policy, and domain meaning |
| Receive a tag without opening an app first | Background tag reading | A system notification and, after user action, an NSUserActivity delivery | Universal-link association, message validation, app authorization, and manual fallback |
| Process an EU-scoped payment tag or VAS tag | NFCPaymentTagReaderSession or NFCVASReaderSession | A specialized system-managed session when device, account, region, and entitlement rules permit | Eligibility checks, approved business route, provider handoff, and payment/transaction truth |
| Emulate an ISO 7816 card for a contactless reader | CardSession | Host card emulation events and APDU request/response exchange | HCE program entitlement, AID routing, transaction protocol, timeout behavior, and transaction result |

NDEF and protocol-specific sessions both use the device’s NFC reader, but they are not interchangeable. CardSession is the opposite direction: the iPhone behaves as the card side of an ISO 7816 exchange. Keep these routes in separate modules and proof records.

## Reader-session lifecycle

### Availability and ownership

NFCReaderSession.readingAvailable is the first local capability check for tag reading. It is not a guarantee that the target tag, protocol, entitlement, region, or current system state will work.

Only one NFC reader session of any type can be active in the system at a time. The system queues additional sessions in FIFO order. A feature should therefore treat the session as an owned, short-lived resource:

1. The person starts one named scanning task.
2. The app checks availability and creates the narrowest session.
3. The app sets a concise system alert message.
4. The session begins and reports active state.
5. The delegate receives messages or detected tags.
6. The app connects to one intended tag when the protocol route requires it.
7. The app performs a bounded read, write, or command sequence.
8. The session invalidates after the intended terminal state, or restarts polling deliberately.
9. The app maps the invalidation reason to a user-facing state.

Do not create a new session from every SwiftUI body update. Keep the session in a feature coordinator or actor-isolated controller whose lifetime matches the user’s scan task. Avoid retaining detected tag objects after a session invalidates or after a new polling sequence makes them invalid.

### Session states

| State | Meaning | Safe app behavior |
| --- | --- | --- |
| unavailable | The current device or environment cannot read tags | Offer manual entry or another supported route |
| ready | The feature can start a scan | Explain what will happen and why |
| starting | The session is being created or begun | Disable duplicate starts |
| active | RF polling is enabled | Show the system instruction and a cancel path |
| detected | One or more candidates are available | Select deterministically or ask the person to isolate the intended object |
| connected | The selected tag is active for protocol operations | Run only the bounded command/read/write route |
| reviewed | Data has been decoded and displayed | Keep source bytes/metadata available |
| committed | The person approved an app-owned action | Record provenance and the resulting domain state |
| invalidated | The session ended with success, cancellation, or error | Release references and return to a restartable state |

The delegate callbacks arrive on the queue selected when the session is created. If that queue is not the main queue, send only small UI state updates to the main actor and keep parsing/transport work bounded.

## NDEF messages and payloads

NFCNDEFReaderSession is the direct route for NDEF tags. Its delegate has both a message-detection callback and a tag-detection callback. The message path is useful for reading NDEF messages. The tag path exposes an NFCNDEFTag so the app can query status and, where supported, read or write through the tag.

An NFCNDEFMessage contains an ordered array of NFCNDEFPayload records. A payload record contains:

- a Type Name Format value;
- a type;
- an identifier;
- payload data.

Prefer Apple’s payload helpers when the feature needs a well-known URI or text record. Treat every other record as untrusted bytes until the product’s format validator accepts it. A URI-looking payload is still data received from a physical object:

1. decode it with the documented payload helper or a format-specific parser;
2. reject malformed or ambiguous values;
3. apply an explicit scheme and host policy;
4. show the destination or action to the person;
5. require confirmation before an external or consequential side effect.

Do not automatically open an arbitrary URL, install a profile, invoke a privileged command, or create a purchase merely because an NDEF record contains a URI.

### NDEF read, write, and lock

For an NFCNDEFTag, queryNDEFStatus reports whether the tag is not supported, read-only, or read-write, together with its maximum NDEF capacity. The app can read NDEF, write a message when the tag is writable, and permanently write-lock the tag when the product’s contract requires it.

Writing is a physical mutation. The write flow should:

1. render the exact records that will be written;
2. show the target object and the irreversible nature of write-locking;
3. query status and capacity;
4. validate the serialized message size;
5. write once with a bounded timeout/retry policy;
6. handle tag loss as a distinct result;
7. read back when the tag/protocol supports a meaningful verification;
8. persist the source message, target fixture, and verification result.

Never call writeLock as a cleanup step. It prevents future write operations and belongs behind a separate, explicit confirmation.

## Protocol-specific tag sessions

Use NFCTagReaderSession when the feature needs a protocol interface rather than a general NDEF message. The current Core NFC route covers:

| Tag interface | Typical operation surface | Configuration and proof notes |
| --- | --- | --- |
| NFCISO7816Tag | ISO 7816 application selection and APDU commands | Declare supported application identifiers; prove AID selection and status-word handling with real fixtures |
| NFCISO15693Tag | ISO 15693 tag access and NDEF behavior where supported | Check tag availability and protocol-specific command support |
| NFCFeliCaTag | Polling, system/service codes, read/write without encryption, and command packets | Declare supported system codes; do not use wildcard configuration |
| NFCMiFareTag | MIFARE family inspection and native or ISO 7816 command paths | Verify family-specific commands; the DESFire NDEF AID changes how a tag is surfaced |

NFCTagReaderSession.Configuration lets the app select polling and constrain ISO 7816 application identifiers or FeliCa system codes. Use the narrowest configuration that can satisfy the feature. A broad polling mode makes it easier to accept a tag that is physically nearby but semantically wrong.

The generic NFCTag enum is a typed protocol boundary. Switch on the concrete case, check isAvailable, connect to the selected tag, and then run the protocol adapter. Do not treat the tag’s identifier as a secret or a durable identity credential. Hardware identifiers can be observed, copied, or changed by fixtures and do not replace cryptographic authentication.

### ISO 7816 and APDUs

An ISO 7816 route needs an allowlisted application identifier in the ISO7816 application identifiers for NFC Tag Reader Session information property list key. When the session discovers a compatible tag, it performs SELECT operations for the configured identifiers. The found NFCISO7816Tag exposes the initially selected AID and sends NFCISO7816APDU commands.

An APDU is an application protocol message, not a generic byte pipe. Define a typed command table:

| Command field | App contract |
| --- | --- |
| CLA/INS/P1/P2 | Exact instruction and parameter values allowed for this feature |
| Data | Length, encoding, and sensitivity rules |
| Le | Expected response length |
| Response payload | Schema and maximum size |
| SW1/SW2 | Explicit success, retry, authentication, and terminal mappings |
| Retry | Only commands documented as safe to repeat |
| Session | Which reader session and tag fixture own the exchange |

Apple documents that unsupported SELECT behavior can result in a security-violation error. Do not probe arbitrary AIDs or use an AI model to generate commands. Keep APDU construction deterministic, log only redacted command metadata, and keep secret material out of UI previews and diagnostics.

### FeliCa, ISO 15693, and MIFARE

These interfaces expose protocol-specific operations and raw data. Their type-specific APIs do not turn an identifier or an unencrypted block into proof of a person or product.

- FeliCa uses declared system codes and provides polling, system-code requests, reset, and service/block operations. The reader-session entitlement rejects wildcard system-code configuration.
- ISO 15693 exposes manufacturer and serial information plus the interface for the tag’s supported operations. Treat serial data as an observation, not an authentication factor.
- MIFARE exposes the family and native command routes. Apple’s docs distinguish MIFARE Ultralight, Plus, and DESFire command support and note that Crypto1 is not supported by the native command route.

When a physical tag is part of a security design, use a protocol with a documented cryptographic authentication scheme and a server or secure local verifier appropriate to the threat model. Core NFC API access alone is not authentication.

## Background tag reading

On supported iPhones, background tag reading can detect a compatible tag while the person is using the device and present a system notification. After the person taps the notification, the system delivers an NSUserActivity containing the NDEF message to the app associated with a universal link. The user may need to unlock the device before delivery.

The background route is a system handoff, not a silent background daemon. Apple documents important unavailability conditions, including an active Core NFC reader session, Wallet or Apple Pay use, camera use, Airplane Mode, and a device that has not been unlocked after restart. Background tag reading does not support custom URL schemes; use universal links and Associated Domains when this route is needed.

Handle the activity as if it came from an untrusted external boundary:

- verify the activity type;
- confirm that the NDEF message has records and is not an empty placeholder;
- validate the URI or record format;
- apply the same host and action policy as in-app scans;
- show the person what was received;
- do not assume background delivery means app authorization;
- retain a manual in-app scan path for unsupported devices and unavailable contexts.

## Payment tags, VAS, and CardSession

### Payment and VAS sessions

NFCPaymentTagReaderSession is a specialized subclass for payment tags and has region, account, device, entitlement, and eligibility constraints. Apple’s current documentation limits this route to use in the European Union and says readingAvailable is false when the current environment is not eligible. NFCVASReaderSession is a separate route for Value Added Service tags.

Do not describe a payment-tag reader as a general Apple Pay integration. Payment authorization, merchant processing, provider capture, and fulfillment remain separate system and server proofs. Keep this route behind a feature/entitlement gate and compile it only in a target whose program requirements are satisfied.

### CardSession host card emulation

CardSession is the reverse direction: the iPhone emulates an ISO 7816 card while an NFC reader sends APDUs. Apple’s current route supports host card emulation transactions for specified categories in the European Economic Area, subject to an Apple-managed entitlement program.

The documented lifecycle is:

1. Check NFCReaderSession.readingAvailable.
2. Check CardSession.isSupported and CardSession.isEligible.
3. Create the session with init.
4. Iterate the eventStream.
5. Wait for sessionStarted and readerDetected as appropriate.
6. Start emulation when the app is ready to answer the reader.
7. Process every APDU event and call respond(response:) in time.
8. Handle readerDeselected.
9. Stop emulation with an explicit EmulationUIStatus.
10. Invalidate and release the session.

CardSession has a maximum emulation duration of 60 seconds from startEmulation. It displays system modal UI over the app. The app must have the HCE entitlement and the ISO 7816 select-identifier-prefixes entitlement; the optional default-contactless-app entitlement allows the person to choose the app in Settings when the program permits it. Apple states that testing requires an iPhone and NFC hardware because Simulator does not provide an NFC reader.

An HCE APDU response is a protocol obligation. A timeout or missing response can fail the reader transaction. Implement a small, deterministic state machine with an allowlisted SELECT route, bounded response generation, redacted diagnostics, and explicit session expiry. Do not use a general-purpose model in the APDU response loop.

## Configuration and privacy register

| Item | Why it exists | Evidence to retain |
| --- | --- | --- |
| NFC tag-reading capability | Enables the target’s tag reader entitlement | Target capability, entitlements in the signed archive |
| com.apple.developer.nfc.readersession.formats | Declares supported tag formats; TAG enables tag-reader access | Entitlement value and provisioning result |
| NFCReaderUsageDescription | Explains why the app needs NFC hardware; missing value can terminate the app | Signed Info.plist and the visible prompt |
| ISO 7816 select identifiers | Constrains application selection for ISO 7816 tag routes | Exact AID list and a fixture result |
| FeliCa system codes | Constrains FeliCa polling to declared codes | Exact discrete values and fixture result |
| Associated Domains | Enables background universal-link tag handoff | Entitlement, domain association, and activity delivery |
| HCE entitlements | Permit CardSession and constrain handled AID prefixes/default role | Apple program approval, signed entitlements, and eligibility |
| Privacy and retention policy | Explains storage, sync, logging, and external handoff of tag data | Data-flow record, deletion test, and release review |

The NFC usage string should name the real user outcome in plain language. Apple’s HIG recommends approachable wording such as “Scan the object” and “Hold your iPhone near the object”; do not force people to understand the developer term NFC.

## Native design and Liquid Glass boundary

The system owns the scanning sheet, its placement, its cancel behavior, and the CardSession emulation modal. The app owns the surrounding feature screen:

- a clear start action and explanation;
- a compact state/status surface;
- a review card for the decoded payload;
- a safe confirmation step for writes, external URLs, and domain actions;
- a history or provenance view;
- a manual fallback.

Use standard SwiftUI navigation, sheets, toolbars, and controls so the current platform appearance—including Liquid Glass adoption—comes from the system. If a custom glass effect is justified, limit it to the app-owned start, review, and confirm controls. Do not cover the system NFC sheet with a duplicate fake scanner, put a translucent panel over an active card-emulation modal, or make the physical instruction depend on an animated glass effect.

## On-device AI boundary

An on-device model can help after deterministic NFC decoding:

- summarize a user-approved NDEF text payload;
- classify a known product record into an app-owned collection;
- suggest a name for a scanned object;
- explain a protocol result using redacted, typed fields;
- propose a follow-up action based on the currently reviewed record.

The model must not:

- invent an AID, APDU, FeliCa system code, or command packet;
- treat a UID or identifier as proof of identity;
- auto-open an unvalidated URL;
- write to a tag without the exact payload and explicit approval;
- approve a payment, credential, access grant, or purchase;
- turn a failed or partial response into success;
- retain raw sensitive tag data when a minimal normalized projection is enough.

Keep the source NDEF records or protocol result, decoded projection, model version/availability, user edits, proposal, validation result, and committed domain action as separate fields.

## Verification boundary

For a real NFC feature, distinguish:

| Evidence | Proves | Does not prove |
| --- | --- | --- |
| Official API source | The documented route and constraints | Target compile or hardware behavior |
| Target compile | Imports, signatures, availability, and membership | Entitlement approval or a physical read |
| Signed artifact inspection | Final privacy strings and entitlements | A successful scan or protocol exchange |
| Simulator/preview | Layout, state reducers, and parser fixtures | NFC radio, tags, card reader, or HCE |
| Physical device with named tag | Reader/session and selected fixture behavior | All tags, regions, providers, or release eligibility |
| System-surface run | Background notification, reader sheet, or HCE modal | Domain authorization or fulfillment |
| Release/TestFlight/App Store evidence | Distribution configuration and destination | Universal NFC compatibility or payment success |

At minimum, prove the exact target and signed configuration, a supported physical iPhone, the intended tag fixtures, cancellation and tag-loss paths, malformed payloads, accessibility settings, and the relevant regional/program gate.

## Sources

- [Core NFC](https://developer.apple.com/documentation/corenfc)
- [NFCReaderSession](https://developer.apple.com/documentation/corenfc/nfcreadersession)
- [NFCReaderSessionDelegate](https://developer.apple.com/documentation/corenfc/nfcreadersessiondelegate)
- [NFCNDEFReaderSession](https://developer.apple.com/documentation/corenfc/nfcndefreadersession)
- [NFCNDEFReaderSessionDelegate](https://developer.apple.com/documentation/corenfc/nfcndefreadersessiondelegate)
- [Building an NFC Tag-Reader App](https://developer.apple.com/documentation/corenfc/building-an-nfc-tag-reader-app)
- [NFCNDEFMessage](https://developer.apple.com/documentation/corenfc/nfcndefmessage)
- [NFCNDEFPayload](https://developer.apple.com/documentation/corenfc/nfcndefpayload)
- [NFCTypeNameFormat](https://developer.apple.com/documentation/corenfc/nfctypenameformat)
- [NFCNDEFTag](https://developer.apple.com/documentation/corenfc/nfcndeftag)
- [NFCNDEFStatus](https://developer.apple.com/documentation/corenfc/nfcndefstatus)
- [NFCTagReaderSession](https://developer.apple.com/documentation/corenfc/nfctagreadersession)
- [NFCTagReaderSession.Configuration](https://developer.apple.com/documentation/corenfc/nfctagreadersession/configuration)
- [NFCTagReaderSessionDelegate](https://developer.apple.com/documentation/corenfc/nfctagreadersessiondelegate)
- [NFCTag](https://developer.apple.com/documentation/corenfc/nfctag-swift.enum)
- [NFCISO7816Tag](https://developer.apple.com/documentation/corenfc/nfciso7816tag)
- [NFCISO7816APDU](https://developer.apple.com/documentation/corenfc/nfciso7816apdu)
- [NFCISO7816ResponseAPDU](https://developer.apple.com/documentation/corenfc/nfciso7816responseapdu)
- [NFCISO15693Tag](https://developer.apple.com/documentation/corenfc/nfciso15693tag)
- [NFCFeliCaTag](https://developer.apple.com/documentation/corenfc/nfcfelicatag)
- [NFCMiFareTag](https://developer.apple.com/documentation/corenfc/nfcmifaretag)
- [NFCReaderError](https://developer.apple.com/documentation/corenfc/nfcreadererror)
- [Adding Support for Background Tag Reading](https://developer.apple.com/documentation/corenfc/adding-support-for-background-tag-reading)
- [CardSession](https://developer.apple.com/documentation/corenfc/cardsession)
- [NFCPaymentTagReaderSession](https://developer.apple.com/documentation/corenfc/nfcpaymenttagreadersession)
- [NFCVASReaderSession](https://developer.apple.com/documentation/corenfc/nfcvasreadersession)
- [Near Field Communication Tag Reader Session Formats Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.nfc.readersession.formats)
- [ISO7816 application identifiers for NFC Tag Reader Session](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.nfc.readersession.iso7816.select-identifiers)
- [ISO18092 system codes for NFC Tag Reader Session](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.nfc.readersession.felica.systemcodes)
- [NFCReaderUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nfcreaderusagedescription)
- [Entitlements](https://developer.apple.com/documentation/bundleresources/entitlements)
- [NFC](https://developer.apple.com/design/human-interface-guidelines/nfc)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Associated Domains Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.associated-domains)
