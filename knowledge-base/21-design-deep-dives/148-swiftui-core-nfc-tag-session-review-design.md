# Core NFC native and Liquid Glass design review

NFC is a physical interaction, so the design has to explain three things at once: what the device is doing, what the tag or reader returned, and what the app is asking the person to approve. The best Apple-native screen is not a decorative “scanner” with a glowing ring. It is a quiet state surface around the system-owned reader alert, followed by a reviewable result.

This design review covers NDEF reading and writing, protocol-specific tags, background URI handoff, CardSession contactless presentation, and optional on-device AI interpretation. Keep the lanes separate. The person should never be shown an interface that implies an ordinary NDEF tag is a payment credential or that a reader-detected event proves a completed transaction.

Related pages:

- [Core NFC framework review](../42-framework-deep-dives/120-swiftui-core-nfc-tag-session-review.md)
- [Core NFC route](../50-capability-recipes/151-swiftui-core-nfc-tag-session-review-route.md)
- [Core NFC proof matrix](../60-verification/145-swiftui-core-nfc-tag-session-proof-matrix.md)
- [Core NFC code recipes](../70-code-recipes/163-swiftui-core-nfc-tag-session-review-recipes.md)

## 1. Design around the physical moment

The primary experience should be a short sequence:

    choose intent
      -> explain contact point
      -> system reader/presentment surface
      -> report deterministic result
      -> review proposed action
      -> commit only after approval

The screen before scanning needs:

- a single primary action that names the lane, such as Scan tag, Write tag, or Present pass;
- a short instruction such as “Hold the top of iPhone near the tag”;
- a visible fallback such as Enter manually, Import a link, or Try again;
- a compact explanation of what will be read or changed;
- a privacy note when a payload, identifier, or credential-like material is involved.

Avoid a full-screen custom camera treatment for NFC. The radio interaction is not a camera preview. The system can show its own reader alert or contactless sheet. The app-owned surface should preserve context and be ready for the result.

## 2. Use a small state vocabulary

Do not describe every delegate callback as a screen. Map framework events into a small user-facing state machine:

| Internal state | User-facing copy | Primary action |
| --- | --- | --- |
| unavailable | NFC is unavailable on this device or right now | Use manual/import fallback |
| ready | Ready to scan | Scan tag |
| presenting | Follow the system prompt | Cancel |
| active | Hold iPhone near the tag | Cancel |
| detected | Tag found; connecting | Wait |
| reading | Reading tag data | Cancel |
| writing | Writing the proposed records | Wait |
| reviewing | Review what was read | Use or discard |
| readOnly | This tag can be read but not changed | Done or choose another tag |
| capacityTooSmall | The proposed message is too large | Edit or choose another tag |
| invalidated | The scan ended | Retry or return |
| proposal | A local interpretation is ready | Review |
| committed | Saved to the app | Done |

The design must distinguish waiting from success. A glowing “connected” badge is not a completed read. A CardSession readerDetected event is not an APDU-approved transaction. A background link notification is not proof that a physical object is authentic.

Use a status line and a source card rather than a dense event log. An advanced diagnostic view can expose the protocol lane and sanitized status code behind a disclosure control.

## 3. NDEF read result: show records before meaning

The result card should have this hierarchy:

1. source: “NDEF tag” and the scan time;
2. record count and supported type summaries;
3. decoded value in readable text;
4. a disclosure for raw type/identifier metadata;
5. the proposed app action;
6. an explicit action button.

For a URI:

    NDEF tag
    1 record · Well-known URI
    https://example.com/item/123
    Open in app

For text:

    NDEF tag
    2 records · Text and app data
    “Shelf 14”
    Add label

For an unknown record:

    NDEF tag
    1 unsupported application record
    The app can preserve the bytes but cannot safely interpret them.
    Save raw record / Scan another tag

Do not show raw payload bytes as a primary visual. They are useful in a diagnostic sheet, but they are not a good Liquid Glass surface. Keep the original record index, type name format, type, identifier, and payload digest available for provenance.

## 4. Write and lock are deliberate workflows

Writing changes a physical object. The UI must show the exact proposed records before the write begins:

| Screen element | Requirement |
| --- | --- |
| Message preview | Show decoded text/URI and record order |
| Capacity | Show proposed bytes versus tag capacity |
| Tag status | Show read-only/read-write/not-supported |
| Destination | Say whether the write replaces existing records |
| Confirmation | Use a separate, explicit Write button |
| Verification | Offer read back or show that only the framework callback was observed |
| Lock action | Separate, destructive path with irreversible warning |

Never pair Write and Lock in one primary control. Locking should use a destructive confirmation whose wording says the tag may become permanently read-only. If a product does not need lock behavior, do not expose it just because the API exists.

The design should remain usable if the tag moves after the preflight. Preserve the proposed message in app state, show “Tag moved—hold steady and retry,” and do not silently retry a destructive operation without user intent.

## 5. Protocol-specific tag UI

For NFCTagReaderSession, the UI should ask for a specific user outcome instead of showing a generic “advanced scanner.” Examples:

- Read card status;
- Read asset block;
- Verify badge;
- Inspect FeliCa service;
- Read compatible device tag.

The feature model can surface a small protocol label:

    ISO 7816 · connected
    ISO 15693 · connected
    FeliCa · connected
    MIFARE · connected

Do not present the tag’s UID as a friendly name. If the product uses a UID-derived lookup, label it as an identifier lookup and explain that the app has not authenticated the physical object. For a verified protocol result, show the exact domain claim that was verified, not a vague “trusted tag” badge.

### ISO 7816

An APDU result should be presented in product language:

    Card response
    Status: authenticated / not authenticated / retry required
    Last command: verified application check

Raw CLA, INS, P1, P2, data, and SW1/SW2 belong in a developer diagnostic view. Redact or hash sensitive response data. Do not make a card flow look like a chat with a model.

### ISO 15693, FeliCa, and MIFARE

Expose block, service, or command concepts only when the person needs them. A field technician may need a detailed command result; a consumer should see “Tag verified” or “Could not read this accessory.” Both views should preserve a path to the original, bounded source and a non-destructive retry.

## 6. Background tag reading is a handoff

Background tag reading should land in a focused context screen, not a generic home screen. The universal link or NSUserActivity should resolve to:

    background handoff
      -> link validation
      -> destination lookup
      -> context preview
      -> explicit app action

The preview should say:

- how the app was invoked;
- which domain/path was recognized;
- what the app can do next;
- whether the person must sign in or confirm;
- how to continue if the link cannot be resolved.

Never imply that background reading inspected an arbitrary APDU or authenticated a tag. If the app needs a richer protocol route, offer a direct in-app scan.

## 7. CardSession and contactless presentation

CardSession has a system-owned contactless presentation model. App UI should prepare the person and then get out of the way:

1. show the selected credential or pass;
2. show the intent and any important account state;
3. explain that the system will present a contactless sheet;
4. initiate only after explicit action;
5. reflect event-stream state without duplicating the system sheet;
6. show a final status after stop, reader deselection, invalidation, or expiration.

Use NFCWindowSceneEvent to bring an existing or newly created scene into the right preparation state when the system reports readerDetected or presentation. Do not treat those events as authorization.

NFCPresentmentIntentAssertion is a short foreground intent window. A design can use it after the person chooses a credential and immediately before a contactless presentation flow. The assertion should never be held as a general “NFC mode” flag. Surface a cooldown or eligibility failure as a retryable system state.

The 60-second CardSession emulation limit has a design implication: keep the screen concise, precompute data, and tell the person when the session expired. Avoid an interaction that requires the person to navigate through several sheets before placing the phone near the reader.

## 8. Liquid Glass placement

Liquid Glass should clarify hierarchy and preserve legibility:

| Surface | Good treatment | Avoid |
| --- | --- | --- |
| Scan control cluster | Small glass container around the primary action and fallback | Full-screen glass over the contactless system UI |
| Status capsule | Compact material around “Ready,” “Reading,” or “Review” | Animated capsule that implies success before a result |
| Result/review card | Glass shell with a strong opaque text hierarchy | Transparent raw-byte tables with low contrast |
| Destructive warning | Standard alert or sheet with clear semantic emphasis | Glass button that makes Lock appear equal to Write |
| Diagnostics | Plain, scrollable text or disclosure sheet | Decorative bloom around APDU traffic |

Use system SwiftUI controls where they already adopt the current platform treatment. Custom effects should be limited to app-owned surfaces and tested with increased contrast, reduced transparency, Dynamic Type, and different backgrounds. The system reader alert and contactless presentation are not a canvas for custom Liquid Glass.

Morphing or matched transitions are useful when the same result capsule expands into a review card, but the motion must be interruptible and should not hide a changed state. A tag-moved error should be visibly different from a success expansion.

## 9. Accessibility and alternate input

NFC is invisible and proximity-based, so the UI has a high responsibility to expose state:

- provide an accessible label and hint for Scan, Write, Present, Cancel, Retry, and Review;
- announce state changes such as “Reader active,” “Tag detected,” “Reading complete,” and “Tag moved”;
- keep the result source and action in VoiceOver order;
- let keyboard, switch control, pointer, and remote focus invoke the same action as touch;
- support Dynamic Type without truncating warnings or action labels;
- keep contrast and touch targets strong when transparency is reduced;
- honor Reduce Motion by removing decorative scanner pulses;
- provide manual entry or import when NFC is unavailable;
- never make a haptic the only indication that a tag was read or written.

If a person cannot perform the proximity gesture, the app should still offer a meaningful path. This might be manual entry, importing a universal link, using a camera/QR fallback, or asking the person to retry with clear guidance.

## 10. Error presentation

Map errors to recovery, not framework names:

| Condition | Copy direction | Recovery |
| --- | --- | --- |
| NFC unavailable | “This device cannot scan NFC here.” | Manual/import route |
| permission/configuration | “NFC scanning is not configured for this app.” | Development/configuration fix; settings only when appropriate |
| multiple tags | “Move other tags away and try again.” | Retry |
| tag moved | “Hold the phone steady and try again.” | Retry without losing draft |
| read-only | “This tag can be read but not written.” | Read, edit target, or choose another tag |
| capacity too small | “The message is too large for this tag.” | Shorten or choose another tag |
| unsupported protocol | “This tag type is not supported by this action.” | Choose a supported route |
| APDU status failure | “The card did not accept this step.” | Show safe protocol state and retry policy |
| background link invalid | “This tag link is not recognized by the app.” | Safari/manual route if safe |
| CardSession ineligible | “Contactless presentation is not available here.” | Explain program/device limitation |
| session timeout | “The contactless session expired.” | Start a fresh session |

Do not expose localized framework error text as the only explanation. Keep a sanitized diagnostic identifier in logs or support exports if needed.

## 11. AI review shell

When an on-device model is useful, add it after the deterministic result:

    source card
      -> “Summarize locally” or “Suggest label”
      -> model availability state
      -> proposal card with source excerpts
      -> Edit / Accept / Discard

The proposal card should expose:

- the source records or fields used;
- a “processed on device” label only when the actual route is on device;
- model availability/fallback state;
- editable output;
- an explicit commit action;
- a way to inspect the original payload.

Never place a model-generated label next to a physical verification badge with the same visual weight. Deterministic protocol verification and generated interpretation are different facts.

## 12. Screen blueprints

### NDEF reader

    Navigation title: Scan tag
    [short instruction]
    [Scan tag] [Enter manually]
    status capsule
    system reader alert
    result card
    [Review action]

### NDEF writer

    Navigation title: Write tag
    draft record editor
    capacity/status row
    preview of exact records
    [Write tag]
    separate [Make read-only] destructive action

### Technician protocol route

    Navigation title: Verify accessory
    [Scan compatible tag]
    protocol and connection state
    sanitized command result
    source/provenance disclosure
    [Retry] [Save verification]

### CardSession

    Selected credential
    eligibility and account status
    [Present]
    system contactless sheet
    event-derived final state

## 13. Design review checklist

- Is the lane named in the screen copy?
- Is the system-owned reader or contactless UI left intact?
- Does the user see waiting, reading, review, and success as different states?
- Are NDEF records shown before a decoded action?
- Is a URL validated before opening?
- Is Write separate from Lock?
- Are APDU and UID values treated as sensitive diagnostics?
- Is background reading presented as a universal-link handoff?
- Does CardSession have its own eligibility and timeout design?
- Does a missing entitlement produce a real fallback?
- Does Reduce Motion remove decorative pulses without hiding state?
- Does VoiceOver announce the same result as visual UI?
- Does the AI shell show its source and remain optional?

## Sources

- [Core NFC](https://developer.apple.com/documentation/corenfc)
- [NFCNDEFReaderSession](https://developer.apple.com/documentation/corenfc/nfcndefreadersession)
- [NFCNDEFTag](https://developer.apple.com/documentation/corenfc/nfcndeftag)
- [NFCNDEFMessage](https://developer.apple.com/documentation/corenfc/nfcndefmessage)
- [NFCNDEFPayload](https://developer.apple.com/documentation/corenfc/nfcndefpayload)
- [NFCTagReaderSession](https://developer.apple.com/documentation/corenfc/nfctagreadersession)
- [NFCISO7816Tag](https://developer.apple.com/documentation/corenfc/nfciso7816tag)
- [NFCISO15693Tag](https://developer.apple.com/documentation/corenfc/nfciso15693tag)
- [NFCFeliCaTag](https://developer.apple.com/documentation/corenfc/nfcfelicatag)
- [NFCMiFareTag](https://developer.apple.com/documentation/corenfc/nfcmifaretag)
- [Adding support for background tag reading](https://developer.apple.com/documentation/corenfc/adding-support-for-background-tag-reading)
- [CardSession](https://developer.apple.com/documentation/corenfc/cardsession)
- [NFCPresentmentIntentAssertion](https://developer.apple.com/documentation/corenfc/nfcpresentmentintentassertion)
- [NFCWindowSceneDelegate](https://developer.apple.com/documentation/corenfc/nfcwindowscenedelegate)
- [NFCWindowSceneEvent](https://developer.apple.com/documentation/corenfc/nfcwindowsceneevent)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
