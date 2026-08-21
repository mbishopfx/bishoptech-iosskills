# NFC scan, tap, and credential-review design

NFC features feel native when the app makes the physical action obvious, lets the system own the radio interaction, and keeps the meaning of the received data visible before anything consequential happens. The design target is not a decorative “scan” animation. It is a short, honest sequence:

~~~text
what is this object?
-> hold the iPhone near it
-> system scanning sheet
-> data or protocol result
-> review source and meaning
-> explicit action
-> saved provenance
~~~

Apple’s NFC Human Interface Guidelines recommend approachable language. Say “Scan the object” or “Hold your iPhone near the pass” instead of making people learn terms like NFC, Core NFC, or tag. Also say “near” rather than “tap” or “touch”; the phone does not need to contact the object.

## Design the route before the surface

| User intent | First screen | System-owned moment | Review moment |
| --- | --- | --- | --- |
| Learn about an object | Object detail with Scan | NFC scanning sheet | Decoded text, image, or link |
| Save a link or note from a card | Empty collection or scanner | NFC scanning sheet | Normalized record with source payload |
| Program a writable object | Write setup screen | NFC scanning sheet | Exact records, capacity, and confirmation |
| Use a secure protocol | Credential/setup screen | NFC scanning sheet | Protocol status, not raw command noise |
| Use a background universal link | Existing app/home context | System notification and activity handoff | Verified destination and user intent |
| Emulate a card | Contactless session screen | CardSession modal UI | Transaction state and response outcome |

NDEF reading, native tag commands, background reading, payment/VAS sessions, and CardSession need different copy and error states. A single “Scan” button can launch them, but it should not make their security or ownership models look identical.

## In-app scan composition

Use a standard navigation shell with:

- a title naming the object or task;
- one primary Scan button;
- a one-sentence reason for access;
- a short “what to expect” instruction;
- a manual entry or alternate route;
- a recent-result or provenance area.

When the person starts scanning, let the system present its scanning sheet. Do not build a fake camera-like overlay that competes with the system sheet. The app-owned screen behind or around that sheet should remain quiet and recoverable.

### Scan state model

| State | Message | Primary action | Secondary action |
| --- | --- | --- | --- |
| ready | “Scan a library card to add it to this collection.” | Scan | Enter manually |
| unavailable | “This device can’t scan this type of object.” | Enter manually | Learn more |
| starting | “Preparing the scanner…” | Disabled | Cancel if available |
| active | System instruction: “Hold your iPhone near the object.” | System-owned cancel | None |
| too-many-candidates | “Move away from other objects and try again.” | Try again | Cancel |
| found | “Object found. Review what it contains.” | Review | Discard |
| decoding | “Reading the object…” | Cancel | None |
| malformed | “This object contains data the app can’t read safely.” | Scan again | Enter manually |
| denied | “NFC access is off. You can continue without scanning.” | Open Settings | Continue manually |
| saved | “Saved to your collection.” | View record | Scan another |

Do not promise a result before the protocol has returned one. A detected RF target is not yet a decoded record.

## NDEF review design

An NDEF review card should show the person the data in a human-readable projection and keep the source available:

| Region | Content |
| --- | --- |
| Object | The name or physical context supplied by the product |
| Record summary | Text, URL, media type, or “unrecognized record” |
| Source | Record count, type, identifier, and received timestamp when useful |
| Risk cue | External destination, unsupported scheme, sensitive content, or write-back possibility |
| Action | Save, open after confirmation, copy, or discard |
| Provenance | Scanner route, target ID surrogate, app version, and user edits |

For a URL record, show the normalized host and the action that will occur. Treat universal links as verified only after the operating system resolves the associated domain and the app validates the received activity. A raw URL in an NDEF payload is not an authorization token.

For text records, preserve the original bytes or a canonical decoded form separately from any edited title, summary, or AI-generated categorization. For media or external records, present “unsupported record” with a safe export/copy option rather than silently discarding bytes.

## Writing design

Writing should be an intentional mode, not a hidden side effect of reading:

1. Choose the object type and record template.
2. Show the exact text, URL, or fields that will be serialized.
3. Display capacity and whether the tag is read-only.
4. Explain whether the operation is reversible.
5. Ask the person to hold the phone near the object.
6. Confirm success or show a recoverable failure.
7. Read back or inspect the result when the protocol supports it.

Separate ordinary writing from write-locking. A write-lock action changes the tag so future writes are prevented; it should have its own warning and explicit confirmation. Do not put Write Lock beside an ordinary Save button with equal visual weight.

If the tag leaves the field during a write, show “The object moved away before the write finished” rather than “Unknown error.” Never retry a physical mutation automatically unless the protocol and operation are known to be idempotent.

## Secure and credential-like routes

A native protocol result can look authoritative because it contains identifiers, status words, or structured bytes. The UI must remain precise:

- “The reader returned a valid response” is different from “You are authenticated.”
- “This application identifier was selected” is different from “This pass is valid.”
- “The credential service accepted the request” is different from “Access was granted.”
- “Card emulation ended successfully” is different from “The merchant completed the transaction.”

Use a progress surface with named phases:

~~~text
Reader detected
-> Application selected
-> Secure exchange in progress
-> Response verified
-> App action awaiting approval
-> Completed or not completed
~~~

Do not show raw APDUs, secret values, or unexplained status bytes as the primary user experience. Provide a diagnostics disclosure for developers or support staff that redacts data and preserves the exact protocol phase.

## Background tag reading and handoff

Background tag reading is a system notification flow. The person sees a notification, taps it, and the app receives an NSUserActivity containing the NDEF message. Design the destination as a continuation of the person’s intent, not as an invisible command bus.

When the app receives the activity:

- confirm the activity type and non-empty message;
- show a compact “Scanned from nearby object” context;
- validate any universal-link host and route;
- show an interstitial when the action is external, paid, privileged, or destructive;
- preserve a manual scan route because background reading is unavailable in documented contexts and on unsupported devices;
- do not automatically start a write, purchase, login, or access grant.

The app should still make sense when the person reaches it directly. A deep link must not be the only place where the user can learn what the product does.

## CardSession and contactless emulation design

CardSession is not a scanner screen. The system presents a modal UI when emulation starts, and the app must respond to reader APDUs within the protocol’s timing expectations. The app-owned surface before emulation should explain:

- what role the phone will play;
- what reader or service the person should approach;
- the maximum session behavior or expected duration;
- what completion means;
- what failure or cancellation looks like;
- what information is stored.

While the system modal is active, avoid competing glass overlays or a second “hold near reader” animation. After the session ends, show a result based on the app’s verified protocol state. Do not label an APDU exchange “payment complete” without the appropriate provider/server evidence.

## Liquid Glass rules for NFC

Use system-native surfaces first:

- NavigationStack or NavigationSplitView for task hierarchy;
- standard Button and toolbar styles for Scan, Cancel, Review, and Save;
- sheets and confirmation dialogs for app-owned review;
- system NFC scanning and CardSession UI for radio interaction;
- standard alerts for denial and recoverable errors.

If a custom Liquid Glass effect is useful, use it for one functional group such as:

- a prominent Scan action;
- a compact review action bar;
- a mode switch between Read and Write;
- a non-blocking provenance/status capsule.

Avoid:

- a translucent fake scanner over the actual NFC sheet;
- stacked glass pills for every tag field;
- glass behind text that scrolls without a legibility edge treatment;
- animation that implies a tag was read before the delegate result;
- a floating glass button over a system-owned CardSession modal;
- using blur to hide raw or sensitive credential data.

Respect the system’s Liquid Glass appearance and accessibility adaptations. Test reduced transparency, increased contrast, Dynamic Type, VoiceOver, Voice Control, Switch Control, and reduced motion. A scanner must remain understandable when visual effects are reduced or removed.

## Accessibility and input

The physical action needs a text and assistive equivalent:

- the scan button has a localized label and hint;
- the instruction says what object to find and how close to hold the phone;
- status changes are announced without repeated noise;
- cancellation is always available through a standard control;
- the result is navigable in reading order;
- URLs expose their host and action;
- raw protocol details are optional and not required to complete the task;
- manual entry exists when a person cannot use the NFC radio interaction;
- no meaning depends on color, blur, vibration, or animation alone.

Use sentence case and short system alert messages so the instruction does not truncate. When the app supports multiple scans, change the instruction to identify the next object rather than repeating vague “Scan again” copy.

## AI review surface

AI belongs after the payload or protocol result is decoded and before an app-owned action:

~~~text
NDEF/protocol observation
-> canonical typed record
-> user-visible source
-> optional on-device explanation or category proposal
-> deterministic validation
-> explicit approval
-> app-owned action
~~~

The AI surface should show:

- the source record or selected protocol fields;
- the proposed title/category/summary;
- whether the proposal is local/on-device and what data was sent;
- the edit control;
- the final action and destination.

Do not ask the model to decide whether an unknown tag is a real credential, generate APDU commands, or authorize an external side effect. A proposal is not a permission grant.

## Preview and physical-device composition

Previews can prove that the state machine renders:

- ready;
- scanning;
- malformed;
- denied;
- review;
- saved;
- credential exchange failed.

They cannot prove NFC radio behavior, tag compatibility, physical ergonomics, CardSession eligibility, background notification delivery, or regional program requirements. Use fixture NDEF messages and protocol result values to exercise the app-owned reducer, then run named physical fixtures on supported hardware.

## Sources

- [NFC](https://developer.apple.com/design/human-interface-guidelines/nfc)
- [Core NFC](https://developer.apple.com/documentation/corenfc)
- [Building an NFC Tag-Reader App](https://developer.apple.com/documentation/corenfc/building-an-nfc-tag-reader-app)
- [Adding Support for Background Tag Reading](https://developer.apple.com/documentation/corenfc/adding-support-for-background-tag-reading)
- [NFCReaderUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nfcreaderusagedescription)
- [NFCTagReaderSession](https://developer.apple.com/documentation/corenfc/nfctagreadersession)
- [NFCNDEFReaderSession](https://developer.apple.com/documentation/corenfc/nfcndefreadersession)
- [NFCNDEFMessage](https://developer.apple.com/documentation/corenfc/nfcndefmessage)
- [NFCNDEFPayload](https://developer.apple.com/documentation/corenfc/nfcndefpayload)
- [NFCNDEFTag](https://developer.apple.com/documentation/corenfc/nfcndeftag)
- [NFCISO7816Tag](https://developer.apple.com/documentation/corenfc/nfciso7816tag)
- [NFCISO7816APDU](https://developer.apple.com/documentation/corenfc/nfciso7816apdu)
- [CardSession](https://developer.apple.com/documentation/corenfc/cardsession)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility modifiers](https://developer.apple.com/documentation/SwiftUI/View-Accessibility)
- [Associated Domains Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.associated-domains)
