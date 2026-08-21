# Core NFC reader and contactless proof matrix

Core NFC crosses target configuration, a system-owned reader session, physical radio hardware, external tag/reader fixtures, protocol state, user authorization, and sometimes an Apple-managed regional program. Prove those boundaries separately.

## Claim-to-evidence matrix

| Claim | Minimum evidence | Does not prove it |
| --- | --- | --- |
| Core NFC route is documented | Current Apple Core NFC source and named API page | A copied code snippet |
| Target is configured for tag reading | Target capability plus signed formats entitlement | An unchecked Xcode capability |
| NFC prompt is configured | Signed Info.plist with a non-empty NFCReaderUsageDescription | A source string in an unbuilt project |
| Reader session starts | Named target compile and signed physical-device launch | Preview or simulator |
| NDEF message is decoded | Real supported tag with expected record fixture | A locally constructed NFCNDEFMessage only |
| NDEF write works | Writable physical tag, exact payload, capacity check, write, and read-back/verification where supported | A successful completion callback alone |
| Tag protocol is selected | Real fixture reaches the expected NFCTag case and connection state | A generic enum switch tested with a mock |
| ISO 7816 route is allowed | Signed AID configuration, physical tag, APDU result with SW1/SW2 mapping | A guessed AID or a random command |
| FeliCa route is constrained | Signed discrete system codes and a matching fixture | A wildcard or unverified code |
| MIFARE route is correct | Named family fixture and command result | A tag identifier without family evidence |
| Background tag reading works | Supported iPhone, illuminated/in-use context, system notification, user tap, associated-domain activity delivery | Direct universal-link launch |
| Payment/VAS route is eligible | Exact region/account/device/program and system session evidence | A normal NFCTagReaderSession run |
| CardSession is eligible | Physical iPhone, NFC reader, isSupported/isEligible, signed HCE entitlements, event stream, APDU responses, and session termination | Simulator, a CardSession type-check, or a local event fixture |
| Contactless transaction completed | Protocol acceptance plus provider/server/domain fulfillment evidence | Reader detected or APDU response alone |
| AI proposal is safe | Source record, decoded projection, proposal, validation, explicit approval, and committed action | Generated title or command text |
| Accessibility works | Task-based VoiceOver, Voice Control, Switch Control, Dynamic Type, reduced transparency/motion, and manual fallback testing | Accessibility labels in source |
| Release is configured | Signed archive/TestFlight artifact with exact entitlements, privacy strings, domains, and metadata | Debug device run |

## Target configuration record

| Field | Value |
| --- | --- |
| App target |  |
| App version/build |  |
| SDK and Xcode |  |
| Deployment target |  |
| Core NFC route | NDEF / tag / background / payment / VAS / HCE |
| Device model and OS |  |
| NFC capability enabled |  |
| Formats entitlement |  |
| NFCReaderUsageDescription |  |
| ISO 7816 select identifiers |  |
| FeliCa system codes |  |
| Associated Domains |  |
| HCE entitlement/program state |  |
| Protocol adapter revision |  |
| Parser/schema revision |  |
| AI model route/version |  |
| Signed artifact |  |
| Distribution environment |  |

## Physical fixture matrix

Record the fixture manufacturer/type only when it is relevant to the claim. Do not generalize one tag’s behavior to all NFC objects.

| ID | Device/fixture | Action | Expected result |
| --- | --- | --- | --- |
| P01 | Supported iPhone + NDEF Type 2 tag | Start a single-read scan | System sheet appears; expected NDEF message arrives; session ends as designed |
| P02 | Same | Read multiple NDEF records | Record order, type, identifier, and payload are preserved |
| P03 | Same | Read text record | Text and locale decode; source record remains available |
| P04 | Same | Read URI record | URL is normalized and held for review; no unvalidated action starts |
| P05 | Same | Read malformed/unsupported record | Safe error or raw-safe summary; no crash or destructive action |
| P06 | Writable NDEF tag | Query status and capacity | Correct read-only/read-write/not-supported state and capacity |
| P07 | Writable NDEF tag | Write under capacity | Exact payload is written; read-back or documented verification passes |
| P08 | Writable NDEF tag | Write over capacity | Write is rejected before mutation; person receives actionable feedback |
| P09 | Writable NDEF tag | Move phone away during write | Tag-loss state is shown; no unsafe blind retry |
| P10 | Writable NDEF tag | Attempt write lock | Separate warning and confirmation; subsequent write attempt is rejected |
| P11 | ISO 7816 fixture | Configure matching AID and connect | Expected tag type, initialSelectedAID, and connection state |
| P12 | ISO 7816 fixture | Send allowlisted APDU | Payload and SW1/SW2 map to typed result |
| P13 | ISO 7816 fixture | Send unsupported SELECT/command | Security or protocol error is handled without probing |
| P14 | ISO 15693 fixture | Detect and run intended operation | Type and availability are correct |
| P15 | FeliCa fixture | Poll declared system code | Expected code/IDm/result; undeclared code is not used |
| P16 | MIFARE fixture | Detect family and send supported command | Family-specific result; unsupported Crypto1 assumption is absent |
| P17 | Multiple objects | Present two or more candidates | App asks for isolation or applies an explicit deterministic selection |
| P18 | Any fixture | Cancel and rescan | Session invalidates cleanly; references are released; next scan works |

## Session lifecycle evidence

Prove each transition with timestamped, redacted logs or a test result:

~~~text
ready
-> session-created
-> begin-called
-> active
-> detected
-> candidate-selected
-> connected
-> operation-started
-> operation-result
-> reviewed
-> committed or discarded
-> invalidated
~~~

Record:

- session kind and configuration;
- delegate queue;
- operation/revision identifier;
- number of detected candidates;
- selected protocol case;
- whether the tag was available;
- cancellation or invalidation code;
- whether a later callback was ignored after cancellation;
- whether all tag references were released when the session ended.

Do not log raw payloads, secret APDU data, full identifiers, or authentication material in normal diagnostics.

## NDEF evidence

| Test | Evidence |
| --- | --- |
| Single-read | invalidateAfterFirstRead behavior and expected terminal invalidation |
| Multi-read | Second scan and explicit stop behavior |
| NDEF payload | Type Name Format, type, identifier, payload, and record ordering |
| Text | Locale, encoding, empty text, long text, and edit provenance |
| URI | Scheme/host allowlist, malformed URL, universal-link handoff, external confirmation |
| Capacity | Required serialized size compared with tag capacity |
| Read-only | UI does not offer write |
| Not supported | UI offers a useful fallback |
| Write | Exact serialized bytes and physical target |
| Write lock | Separate confirmation and irreversible result |
| Tag loss | Error mapping and no automatic non-idempotent retry |
| Delete | Source and derived projections are removed together |

## Protocol and APDU evidence

For every protocol adapter, retain a redacted transaction fixture:

~~~yaml
route: ISO7816
target: ""
device: ""
os: ""
aid: ""
command:
  cla: ""
  ins: ""
  p1: ""
  p2: ""
  data_length: 0
  expected_response_length: 0
response:
  payload_length: 0
  sw1: ""
  sw2: ""
typed_result: ""
retry_policy: ""
security_boundary: ""
physical_fixture: ""
~~~

The record should make clear whether a response was:

- transport success with an application-level rejection;
- transport failure;
- authentication required;
- a retryable protocol status;
- a terminal protocol status;
- an app-owned domain result.

Never use a non-zero or “interesting” status word as a generic success signal. Map status words through the protocol specification for the exact product, and keep the mapping versioned.

## Background tag evidence

| Condition | Expected result |
| --- | --- |
| Supported iPhone, screen illuminated, no active scanner | System notification can appear for a compatible URI record |
| Person taps notification | Activity is delivered to the associated app |
| App is not installed or association is absent | System fallback behavior is recorded; app does not claim delivery |
| Custom URL scheme only | Background route is not used; universal-link/manual route remains |
| Reader session is active | Background reading is not assumed to run simultaneously |
| Wallet/Apple Pay or camera is active | Availability limitation is handled |
| Device has not been unlocked after restart | Locked-device behavior is handled |
| Activity has empty/invalid payload | App rejects it safely |

## CardSession evidence

CardSession requires a distinct physical reader fixture:

| Test | Expected result |
| --- | --- |
| readingAvailable false | Feature does not attempt to create a session |
| isSupported false | HCE route is unavailable with a clear fallback |
| isEligible false | Feature does not imply approval or availability |
| Session created | Event stream begins and sessionStarted is observed |
| Reader detected | UI can start emulation or wait intentionally |
| Start emulation | System modal appears; app responds only when ready |
| SELECT AID | Only declared prefix route is accepted |
| APDU sequence | Every supported request receives a timely deterministic response |
| Reader deselected | App stops or returns to a recoverable state |
| 60-second limit | Session expiry is handled as a normal terminal result |
| Stop emulation | Correct system status and app result are shown |
| Invalidate | Resources and event task are released |

Do not mark “payment complete,” “door opened,” or “identity verified” from CardSession evidence alone. Add the provider or domain evidence that establishes the actual outcome.

## Privacy, security, and AI evidence

Check the following before shipping:

- the NFC usage string describes a real person-facing purpose;
- raw NDEF and protocol data are retained only as long as the feature needs;
- logs redact identifiers and APDU data;
- external URLs use explicit scheme/host policy;
- protocol commands come from versioned code, not model output;
- tag identifiers are not treated as secrets;
- writes and write-locks require explicit review;
- HCE responses use a bounded state machine and do not call a slow model;
- model context uses a minimal, corrected projection;
- AI proposals show source and final action separately;
- the person can delete both source observations and derived records;
- a manual route exists when NFC is unavailable.

## Accessibility and release evidence

Run the complete scan and review task with:

- VoiceOver;
- Voice Control;
- Switch Control;
- Dynamic Type at large sizes;
- increased contrast;
- reduced transparency;
- reduced motion;
- touch, keyboard, and pointer where the target supports them;
- an alternate manual route.

For distribution, inspect the archive rather than the project editor:

- signed entitlements contain only the needed NFC keys;
- Info.plist contains the exact usage string and required domains;
- the target’s deployment range matches the code’s availability guards;
- specialized or HCE routes have their approved program state;
- the release build’s behavior is tested with the same class of physical fixture;
- app privacy and retention documentation matches the actual data flow.

## Evidence record template

~~~yaml
route: CoreNFC
build:
  app_version: ""
  build_number: ""
  sdk: ""
  deployment_target: ""
  signed_artifact: ""
target:
  name: ""
  route: ndef-tag-background-payment-vas-hce
  formats_entitlement: []
  usage_description_present: false
  iso7816_aids: []
  felica_system_codes: []
  associated_domains: []
  hce_entitlements: []
device:
  model: ""
  os: ""
  region: ""
  nfc_reading_available: false
fixture:
  kind: ""
  protocol: ""
  identifier: ""
  expected_result: ""
session:
  created: false
  began: false
  active: false
  detected_count: 0
  connected: false
  invalidation_reason: ""
ndef:
  records: 0
  status: ""
  capacity: 0
  read: false
  wrote: false
  read_back: false
protocol:
  aid: ""
  commands_redacted: 0
  sw1: ""
  sw2: ""
  typed_result: ""
background:
  notification_seen: false
  activity_delivered: false
hce:
  supported: false
  eligible: false
  reader_detected: false
  apdu_responses: 0
  session_expired: false
ai:
  used: false
  model_route: ""
  proposal_reviewed: false
  committed: false
accessibility:
  voiceover: ""
  voice_control: ""
  switch_control: ""
  dynamic_type: ""
  reduced_effects: ""
release:
  environment: ""
  result: ""
known_limits: []
~~~

## Sources

- [Core NFC](https://developer.apple.com/documentation/corenfc)
- [NFCReaderSession](https://developer.apple.com/documentation/corenfc/nfcreadersession)
- [NFCReaderError](https://developer.apple.com/documentation/corenfc/nfcreadererror)
- [NFCNDEFReaderSession](https://developer.apple.com/documentation/corenfc/nfcndefreadersession)
- [NFCNDEFReaderSessionDelegate](https://developer.apple.com/documentation/corenfc/nfcndefreadersessiondelegate)
- [Building an NFC Tag-Reader App](https://developer.apple.com/documentation/corenfc/building-an-nfc-tag-reader-app)
- [Adding Support for Background Tag Reading](https://developer.apple.com/documentation/corenfc/adding-support-for-background-tag-reading)
- [NFCNDEFTag](https://developer.apple.com/documentation/corenfc/nfcndeftag)
- [NFCNDEFStatus](https://developer.apple.com/documentation/corenfc/nfcndefstatus)
- [NFCNDEFMessage](https://developer.apple.com/documentation/corenfc/nfcndefmessage)
- [NFCNDEFPayload](https://developer.apple.com/documentation/corenfc/nfcndefpayload)
- [NFCTagReaderSession](https://developer.apple.com/documentation/corenfc/nfctagreadersession)
- [NFCTagReaderSession.Configuration](https://developer.apple.com/documentation/corenfc/nfctagreadersession/configuration)
- [NFCTag](https://developer.apple.com/documentation/corenfc/nfctag-swift.enum)
- [NFCISO7816Tag](https://developer.apple.com/documentation/corenfc/nfciso7816tag)
- [NFCISO7816APDU](https://developer.apple.com/documentation/corenfc/nfciso7816apdu)
- [NFCISO7816ResponseAPDU](https://developer.apple.com/documentation/corenfc/nfciso7816responseapdu)
- [NFCISO15693Tag](https://developer.apple.com/documentation/corenfc/nfciso15693tag)
- [NFCFeliCaTag](https://developer.apple.com/documentation/corenfc/nfcfelicatag)
- [NFCMiFareTag](https://developer.apple.com/documentation/corenfc/nfcmifaretag)
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
