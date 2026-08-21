# SwiftUI Core NFC tag-session review

Core NFC is a proximity and contactless framework, not a general-purpose identity or payment shortcut. The framework can discover NDEF tags, read and write NDEF messages, expose protocol-specific tag interfaces, receive selected background NDEF handoffs, and—under a separate entitlement and product boundary—emulate an ISO 7816 card with CardSession. A native SwiftUI app should select one of those lanes before it designs the screen or asks for a capability.

This review is for an iOS 26 target using the current Apple SDK. API names, availability annotations, entitlements, regional eligibility, and device support still need to be compiled and tested against the exact target. The source contract is useful for architecture; it is not a substitute for a physical NFC fixture, a signed entitlement, or an App Store review decision.

Related implementation material:

- [Core NFC route](../50-capability-recipes/151-swiftui-core-nfc-tag-session-review-route.md)
- [Core NFC design review](../21-design-deep-dives/148-swiftui-core-nfc-tag-session-review-design.md)
- [Core NFC proof matrix](../60-verification/145-swiftui-core-nfc-tag-session-proof-matrix.md)
- [Core NFC code recipes](../70-code-recipes/163-swiftui-core-nfc-tag-session-review-recipes.md)

## 1. Choose the contactless lane first

| Product need | Apple route | What it actually provides | Boundary |
| --- | --- | --- | --- |
| Read or write ordinary NFC Forum data | NFCNDEFReaderSession, NFCNDEFTag | NDEF messages and payload records on supported tags | It does not prove that a payload is trusted or that a tag represents a person |
| Inspect a tag protocol or issue native commands | NFCTagReaderSession and a tag protocol adapter | ISO 7816, ISO 15693, FeliCa, or MIFARE interfaces | The app must handle protocol state, authentication, command errors, and entitlement scope |
| Receive a tap without first opening the app | Background tag reading plus an NDEF URI and associated domain | A system-delivered URL or NSUserActivity handoff | It is URI-oriented, has device/system conditions, and is not a replacement for in-app scanning |
| Emulate an ISO 7816 card | CardSession | A short contactless card-emulation session and APDU event stream | Apple-managed HCE entitlement, EEA/product eligibility, physical iPhone and reader proof |
| Read payment or VAS tags | NFCPaymentTagReaderSession or NFCVASReaderSession | Specialized system-authorized contactless routes | Separate entitlements, regions, account status, and program approval apply |
| Update an existing scene for contactless intent | NFCWindowSceneDelegate and NFCWindowSceneEvent | Reader-detected or presentation events for eligible system surfaces | An event is an opportunity to update UI, not proof that a transaction completed |

Do not make an enum called NFCFeature and let every route flow through it without preserving the lane. Keep route-specific state and evidence. An NDEF URI, an ISO 7816 response APDU, and a CardSession presentation event have different trust, lifetime, and release requirements.

## 2. Availability is a runtime and distribution contract

Core NFC requires a device that supports NFC. Check NFCReaderSession.readingAvailable immediately before offering a reader route. The framework is not available in app extensions. A target can compile successfully while a particular device, scene, region, entitlement, or system state cannot perform the operation.

Use at least these gates:

| Gate | Question | Failure behavior |
| --- | --- | --- |
| Target | Is the selected API available for the deployment target and SDK? | Compile a fallback or raise the minimum target deliberately |
| Device | Is NFC hardware and reading support available now? | Hide or disable scanning with a manual/import route |
| Permission | Is NFCReaderUsageDescription present in the shipped application target? | Fix the target configuration before presenting a session |
| Capability | Does the signed app contain the required tag-reader formats entitlement? | Do not treat a local entitlement file as proof; inspect the archive |
| Protocol | Are ISO 7816 AIDs, FeliCa system codes, or other protocol configuration declared? | Narrow the route or stop before the system rejects selection |
| Region/program | Is the specialized payment, VAS, HCE, or default-contactless route eligible? | Explain unavailability; do not simulate success |
| Scene | Is the app foregrounded and in a scene state that can own the UI? | Defer presentation and retain intent as value state |
| Physical fixture | Is a supported tag or reader actually present? | Keep the app in ready/awaiting state and do not fabricate data |

NFCReaderSession.readingAvailable is not a universal guarantee for CardSession or every specialized route. CardSession adds isSupported and isEligible. A presentment-intent assertion has its own eligibility and lifetime rules. Recheck the most specific gate immediately before using the feature.

The minimum configuration usually includes:

- NFCReaderUsageDescription with a plain-language reason tied to the user action;
- the Near Field Communication Tag Reader Session Formats Entitlement for NFCTagReaderSession;
- the ISO7816 application identifiers entitlement when the reader route needs application selection;
- the ISO18092 system-codes entitlement when the FeliCa route requires it;
- Associated Domains for an app that expects background NDEF URI handoff;
- Apple-managed HCE entitlements only after the relevant contactless program path is approved.

The entitlement keys are embedded in the signed executable. Inspect the archive or installed app when a capability appears to work in an Xcode run but fails in TestFlight.

## 3. Reader sessions are exclusive, stateful objects

NFC reader sessions are not view values. The system permits only one active NFC reader session at a time; additional sessions are queued. A SwiftUI view can appear and disappear many times, so the session belongs in a coordinator or actor-owned feature object with an explicit generation.

The common lifecycle is:

    idle
      -> preflight
      -> session-created
      -> begin
      -> became-active
      -> detecting
      -> tag-detected
      -> connected
      -> operation-in-flight
      -> result-reviewed
      -> invalidated
      -> idle

Important rules:

1. Create a session only after the user chooses the scan action and the preflight passes.
2. Retain the session strongly for the whole operation.
3. Set the delegate and an intentional callback queue.
4. Call begin once for that session.
5. Treat didBecomeActive as readiness for polling, not as a tag result.
6. Use alertMessage to tell the person what to do near the reader.
7. Connect to a detected tag before using its protocol operations.
8. Stop or invalidate when the route ends, the scene leaves the required state, or the operation is no longer user-intended.
9. Treat didInvalidateWithError as a terminal event for that session.
10. Create a new session for a new attempt; do not reuse invalid tag references.

NFCReaderSessionProtocol exposes the system-facing session contract: readiness, begin, invalidation, error invalidation, and the alert message. The delegate reports active, detection, and invalidation events. The concrete NDEF and tag-reader delegates add the lane-specific detection callbacks.

Keep an operation generation:

    view appearance -> generation 41
    start session -> generation 41
    view disappears -> cancel generation 41
    late callback -> ignored because current generation is 42

That guard prevents a late delegate callback from putting a new scan screen back into a stale result state.

## 4. NDEF messages are ordered records, not trusted domain objects

NFCNDEFMessage is an ordered array of NFCNDEFPayload records. A payload contains the Type Name Format, type, identifier, and payload data. NFCNDEFMessage also exposes its stored byte length. The raw fields are valuable for diagnostics and future compatibility; a decoded URL or text value is only a proposal until the product validates it.

Preserve at least:

| Field | Keep because |
| --- | --- |
| Record index | Ordering can be meaningful and background reading uses the first qualifying URI record |
| typeNameFormat | It distinguishes well-known, media, absolute-URI, external, empty, unknown, and chunked forms |
| type | It identifies the record kind under the NDEF specification |
| identifier | It may be used by the application protocol and must not be silently discarded |
| payload bytes | A decoder may be incomplete or a custom type may be valuable later |
| decoded text/URL | It is convenient for review, but it is derived and must be validated |
| message length | It informs capacity and fixture behavior |

Apple provides convenience constructors and decoders for well-known URI and text payloads. Use those when the route expects those record types, but retain the record fields and raw bytes. A failed convenience decode does not mean the whole message is corrupt; it may be an unsupported or application-specific record.

Treat a tag payload as hostile input:

- bound the number of records and decoded string size before displaying or handing off;
- reject URLs with unexpected schemes, hosts, or credentials when the product expects a controlled domain;
- do not auto-open a URL merely because an NDEF decoder returned a URL;
- render text as text until the person approves an action;
- avoid logging raw payloads, identifiers, or tag UIDs;
- never infer authentication, ownership, payment completion, or physical presence from an arbitrary record.

The app’s domain boundary should look like:

    NDEF bytes
      -> bounded record envelope
      -> deterministic decode
      -> validation and policy
      -> user-visible proposal
      -> explicit action
      -> app-owned record

Foundation Models or another on-device model can summarize or classify a bounded envelope after deterministic decoding. It must not turn an unknown tag into an authorized action.

## 5. NDEF session versus generic tag session

NFCNDEFReaderSession is the shortest route when the feature needs NDEF messages. It can report detected messages and can report a detected NFCNDEFTag when the app needs to query or write the tag. Its initializer includes the delegate, callback queue, and whether to invalidate after the first read.

Use invalidate-after-first-read for a one-shot “scan this tag” action. Use a continuing session only when the UI explains that the person can scan multiple tags and the product has a clear duplicate and cancellation policy. A session that continues silently can surprise the person and create accidental repeated writes.

NFCTagReaderSession is the protocol-selection route. It reports NFCTag values that can be adapted to NFCISO7816Tag, NFCISO15693Tag, NFCFeliCaTag, or NFCMiFareTag. Use it when the product must inspect a protocol, issue commands, or explicitly choose a tag technology. A tag that also carries NDEF does not mean that the generic session is the simplest implementation.

The adapter decision should be explicit:

| Detected adapter | Good fit | Proof obligation |
| --- | --- | --- |
| NFCISO7816Tag | APDU-based cards and secure elements exposed as tag sessions | AID selection, command contract, status words, authentication state, no raw secret logging |
| NFCISO15693Tag | ISO 15693 block and custom commands | Request flags, block ranges, lock operations, manufacturer and serial data handling |
| NFCFeliCaTag | FeliCa system-code polling and service/block operations | Approved system-code configuration, service codes, encryption assumptions, fixture |
| NFCMiFareTag | Native MIFARE commands or ISO 7816 command path where supported | Family-specific command framing and the DESFire NDEF AID selection behavior |
| NFCNDEFTag | NDEF status, read, write, and lock | Status/capacity check, write confirmation, irreversible lock warning |

Do not identify a product record solely by a UID. UIDs can be sensitive, can be unavailable in a given route, and do not prove that the tag is an authenticated object.

## 6. NDEF status, capacity, writing, and locking

NFCNDEFTag exposes isAvailable and operations for queryNDEFStatus, readNDEF, writeNDEF, and writeLock. The status is notSupported, readOnly, or readWrite. Query the status and capacity after connecting and before offering a write.

Write flow:

    detected
      -> connect
      -> isAvailable
      -> query status/capacity
      -> encode bounded message
      -> compare encoded length to capacity
      -> show exact proposed records
      -> explicit write confirmation
      -> write
      -> optional read-back verification
      -> success/failure review

Never put writeLock behind the same button as write. Locking is an irreversible operation for many tags. The UI should say that the tag may become permanently read-only and require a separate, deliberate confirmation. A successful write callback means the framework completed the requested operation; it is not the same as a verified read-back or an application-level authorization.

For an app that edits its own tags, use an app-owned external type or a documented URI format with a version field. Keep the record schema small, bounded, and forward-compatible. Do not store credentials, payment tokens, or unencrypted personal data simply because NDEF can carry bytes.

## 7. ISO 7816 and APDU boundaries

NFCISO7816Tag is an ISO 7816 tag interface. The reader route can use the declared ISO7816 application identifiers to perform application selection. The order of the configured identifiers matters, and Apple documents an initial selected AID for the tag when selection occurs. A SELECT command for an unsupported AID can result in a security violation when the AID is not declared.

An NFCISO7816APDU carries the command fields CLA, INS, P1, P2, data, and expected response length. sendCommand returns response data plus SW1 and SW2, or the current ResponseAPDU shape in async APIs. Those status words are protocol output; map them through the app’s protocol table rather than treating any response as success.

An APDU adapter should separate:

| Layer | Responsibility |
| --- | --- |
| Framing | Construct a command with the exact CLA/INS/P1/P2/data/Le contract |
| Transport | Send the command while the tag is connected and the session is valid |
| Status | Decode SW1/SW2 and bounded response data |
| Protocol | Advance the card-specific state machine, including authentication or secure messaging |
| Product | Turn a verified protocol result into a reviewable domain action |

Do not put APDU bytes in a SwiftUI view. Do not put a card credential or secure-messaging key in a Foundation Models prompt. Do not present a green check for a response that only means “command accepted” when the card protocol requires a later commit or cryptographic verification.

The same boundary applies to the MIFARE ISO 7816 command path and protocol-specific commands for ISO 15693 or FeliCa. Apple exposes the transport interface; the app still owns its protocol specification, fixtures, timeout policy, and security review.

## 8. Background tag reading and universal-link handoff

Background tag reading is a distinct system route. On supported iPhones, the system can read an NDEF URI record without the app first presenting a reader session. Apple’s guidance describes using the first URI record that matches the background-reading rules and delivering the result through a universal-link flow after the person interacts with the notification. A locked phone requires unlock. If no associated app handles the link, Safari can open it.

The route is intentionally constrained:

- it is URI-oriented, not a general APDU or arbitrary payload stream;
- custom URL schemes are not the supported background handoff format;
- the app needs Associated Domains and a working universal-link association;
- background reading is unavailable in several system states, including an active reader session and other contactless/camera conditions Apple documents;
- the app still needs a direct in-app scan fallback.

Handle the handoff as untrusted navigation:

    NSUserActivity / universal link
      -> verify activity type and URL
      -> validate host/path/query
      -> resolve a bounded app route
      -> show context and ask for action

The link is an invocation signal, not proof that a transaction occurred. If the link identifies a record, fetch or resolve it through the app’s authorization and data layer.

## 9. CardSession and HCE is a separate product lane

CardSession provides ISO 7816 card emulation. Apple’s current Core NFC documentation describes uses such as eligible in-store contactless transactions, car keys, closed-loop transit, corporate badges, hotel keys, loyalty/rewards, and event tickets, subject to the relevant program and entitlement boundaries. This is not an API that an ordinary app can enable by adding a Boolean to a local entitlements file.

Preflight the documented conditions:

    NFCReaderSession.readingAvailable
      && CardSession.isSupported
      && CardSession.isEligible

Then create a CardSession asynchronously, consume its eventStream, set an alertMessage when appropriate, start emulation, answer APDU events promptly, and stop or invalidate the session. The system can present a modal contactless UI. A session has a maximum emulation duration; Apple’s current documentation describes a 60-second limit from startEmulation. Test the actual SDK behavior and map expiration to a clear user state.

The CardSession event stream includes events such as:

- sessionStarted;
- readerDetected;
- received APDU;
- readerDeselected;
- sessionInvalidated.

The app must answer the APDU protocol in time or the reader can time out. Do not run a model, network call, or long database migration in the response path. Precompute the minimum protocol state before emulation and keep the APDU handler bounded. Stop emulation with the correct EmulationUIStatus so the system can show the appropriate outcome.

The HCE configuration includes Apple-managed entitlements for card session use, handled ISO 7816 SELECT identifiers, and optional default-contactless-app behavior. The HCE entitlement documentation directs developers to the EEA contactless-transaction program for application. Treat approval, region, account, and distribution state as release prerequisites rather than runtime guesses.

NFCPresentmentIntentAssertion is for expressing active intent to make exclusive use of contactless features. It can prevent a system default contactless app from launching in response to a user gesture or reader field. It is foreground-only, expires when the app backgrounds, when its maximum duration elapses, or when the object deinitializes, and has a cooldown. Check readingAvailable before attempting to acquire it; unsupported use can be fatal. Acquire it only after the user expresses the action and release it when the intent window ends.

NFCWindowSceneDelegate and NFCWindowSceneEvent let a scene respond to eligible contactless events. Store readerDetected or presentation as value state and update the appropriate view. An event should prepare the user interface; it does not replace CardSession eligibility, a reader response, or a completed transaction.

## 10. Payment tags and VAS stay separate

NFCPaymentTagReaderSession and NFCVASReaderSession have distinct entitlement and program boundaries. Apple documents regional and account requirements for payment-tag reading and an Apple entitlement for VAS. Do not implement these routes as a generic NFCTagReaderSession fallback without checking the current program documentation.

The UI should explain which route is being attempted. A generic “NFC failed” message is not enough when the problem may be that the device, region, account, entitlement, or tag category is ineligible. Keep a manual or system-approved alternative if the product requires a guaranteed user outcome.

## 11. SwiftUI ownership and bridging

Core NFC is delegate- and session-driven UIKit/Foundation work. SwiftUI should own value state and composition, while a coordinator or feature object owns the session.

Recommended boundary:

    SwiftUI view
      -> user intent
      -> @MainActor feature model
      -> session coordinator
      -> Core NFC delegate callbacks
      -> bounded value events
      -> feature model
      -> review UI

The coordinator should:

- own the concrete session strongly;
- expose start, cancel, and reset;
- receive delegate callbacks on the configured queue;
- hop to the main actor before changing published UI state;
- hold a generation and ignore stale callbacks;
- clear the session after invalidation;
- never expose a live NFC tag object to a persisted model;
- translate framework errors into user-safe categories without logging sensitive payloads.

UIViewControllerRepresentable is useful for a scanner or system-owned controller; a pure session coordinator often needs no view controller bridge at all. Do not create sessions from a SwiftUI body or an initializer that can run repeatedly. Use task cancellation and scene phase to stop work intentionally.

## 12. On-device AI handoff

NFC is a deterministic input route. On-device AI is an optional interpretation layer:

    raw tag input
      -> bounded deterministic envelope
      -> local classifier/summarizer/extractor
      -> proposal with provenance
      -> human review
      -> explicit domain action

Safe AI uses include:

- summarizing a long, app-owned NDEF text record;
- classifying a user-approved tag into a small set of app categories;
- extracting fields from an app-owned external type after deterministic size and schema checks;
- suggesting a label or next route while showing the original record and confidence/uncertainty.

Unsafe defaults include:

- sending arbitrary APDU responses, UIDs, credentials, or payment material to a model;
- allowing generated output to write a tag, call a URL, open a door, authorize a person, or trigger a purchase without review;
- claiming that a model verified the tag’s physical authenticity;
- using a network fallback without telling the person that the input left the device.

Attach provenance to every proposal:

    sourceID
    readerLane
    sessionGeneration
    recordIndices
    rawDataDigest
    decoderVersion
    modelIdentifier
    modelAvailability
    generatedAt
    reviewState

If the on-device model is unavailable, the deterministic decoder and manual editor should remain useful.

## 13. Native, Liquid Glass, and accessibility implications

The NFC system alert and contactless sheet are Apple-owned surfaces. Do not recreate them with a custom “Apple-like” modal. The app-owned screen should stay compact:

1. one clear action such as Scan, Write, or Present;
2. a short instruction describing how to hold the device;
3. a live status that says waiting, connected, reading, writing, reviewing, or unavailable;
4. a bounded result card with the source and proposed action;
5. explicit destructive confirmation for writeLock, credential changes, or other irreversible protocol actions.

Use system controls and current SwiftUI materials where they fit. Apply Liquid Glass to a small control cluster or a result/review shell, not over raw bytes or every row. Avoid custom blur overlays that hide the system scanner or compete with the contactless system UI.

Accessibility proof includes:

- VoiceOver can discover the scan/write/present action and the current NFC state;
- Dynamic Type does not hide the source, warning, or primary action;
- Reduce Motion and Reduce Transparency remain understandable;
- a proximity gesture is never the only way to invoke a route;
- a manual entry, import, or retry path is labeled;
- the result exposes text and actions in semantic order;
- write and lock warnings are announced before confirmation;
- haptics are supplemental and do not carry the only success signal.

## 14. Release proof packet

For a Core NFC feature, archive the evidence by lane:

| Evidence | Reader/NDEF | Background | CardSession/HCE |
| --- | --- | --- | --- |
| Target SDK and deployment target | Required | Required | Required |
| Device support and physical fixture | NFC iPhone and tags | iPhone/background states | Physical iPhone plus contactless reader |
| Privacy configuration | NFCReaderUsageDescription | Associated Domains and link configuration | HCE/contactless program configuration |
| Signed capability | Tag-reader formats/AIDs as needed | Associated-domain association | Apple-managed HCE entitlements |
| Runtime trace | active, detected, connected, read/write, invalidated | notification, unlock, universal-link activity | eligibility, session, APDU, reader deselect, stop/timeout |
| Failure matrix | no NFC, tag moved, read-only, malformed | locked, unavailable, no app association | no reader, ineligible, timeout, expiry |
| Accessibility | status, review, destructive warnings | link context and fallback | presentation state and result |
| Distribution | archive and TestFlight install | association on production domain | approved distribution entitlement and TestFlight/device proof |

Do not call simulator work release proof for NFC. A passing unit test can prove a decoder or state reducer; only a physical tag/reader run proves the radio interaction.

## Sources

- [Core NFC](https://developer.apple.com/documentation/corenfc)
- [NFCNDEFReaderSession](https://developer.apple.com/documentation/corenfc/nfcndefreadersession)
- [NFCNDEFReaderSessionDelegate](https://developer.apple.com/documentation/corenfc/nfcndefreadersessiondelegate)
- [NFCTagReaderSession](https://developer.apple.com/documentation/corenfc/nfctagreadersession)
- [NFCTagReaderSessionDelegate](https://developer.apple.com/documentation/corenfc/nfctagreadersessiondelegate-2joku?changes=_1)
- [NFCReaderSessionProtocol](https://developer.apple.com/documentation/corenfc/nfcreadersessionprotocol)
- [NFCNDEFTag](https://developer.apple.com/documentation/corenfc/nfcndeftag)
- [NFCNDEFStatus](https://developer.apple.com/documentation/corenfc/nfcndefstatus)
- [NFCNDEFMessage](https://developer.apple.com/documentation/corenfc/nfcndefmessage)
- [NFCNDEFPayload](https://developer.apple.com/documentation/corenfc/nfcndefpayload)
- [NFCTypeNameFormat](https://developer.apple.com/documentation/corenfc/nfctypenameformat)
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
- [SwiftUI UIViewControllerRepresentable](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Allowing apps and websites to link to your content](https://developer.apple.com/documentation/xcode/allowing-apps-and-websites-to-link-to-your-content/)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
