# NFC, MusicKit, and ShazamKit proof matrix

This matrix separates physical detection, protected-resource authorization, catalog/library state, playback, audio matching, candidate review, AI enrichment, system handoff, and release evidence. A tag callback or media match is not identity, authorization, or side-effect completion.

## Evidence levels

| Level | Evidence | What it proves |
| --- | --- | --- |
| L0 | Apple route and privacy review | The selected NFC, MusicKit, or ShazamKit API and target boundary are understood. |
| L1 | Deterministic payload/catalog/audio fixtures | Parsing, validation, provenance, malformed input, no-match, duplicate, stale, and AI proposal behavior. |
| L2 | Preview/simulator/UI fixture | Review hierarchy, manual fallback, accessibility labels, Liquid Glass states, and deep links. |
| L3 | Signed physical-device run | NFC hardware/session, microphone permission/capture, MusicKit authorization/player, tag/audio interruption, and system UI. |
| L4 | Real tag/account/catalog/audio environment | Protocol variants, tag loss, Apple Music account/subscription/region, noisy audio, custom catalog, and playback route. |
| L5 | Release artifact | Entitlements, usage strings, MusicKit service configuration, catalog resources, privacy declarations, supported devices, and signed archive. |

## Core NFC

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| NDEF reader works | Physical supported iPhone, entitlement, usage string, session begin/active/detect/invalidate | Simulator or framework import does not prove NFC radio behavior. |
| Tag format is supported | Real tags for each declared NDEF/protocol type and payload encoding | One NDEF tag does not prove ISO/FeliCa/MIFARE routes. |
| Multiple tags are handled | Two or more tags, ambiguous selection, isolation/cancel route | First callback or signal strength is not identity. |
| Tag payload is safe | Malformed/oversized/unknown scheme/host/record, replay, user review | A readable payload is untrusted input. |
| NFC write works | Writable tag, capacity, existing content, tag loss, write/read-back, cancellation | Write callback does not prove future interoperability. |
| Background tag reading works | System invocation, supported message, app routing, validation, manual fallback | Foreground scan evidence is not background invocation proof. |
| Protocol command is authorized | Authentication/crypto fixture, invalid response, replay, physical device | A tag UID is not a credential or person identity. |

## MusicKit

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Authorization works | Usage string, notDetermined/authorized/denied/restricted, Settings change | Prompt acceptance does not prove all catalog/library features. |
| Catalog search works | MusicCatalogSearchRequest fixture, empty/partial/network/region result, identifier preservation | A catalog result is not a library item or playable subscription. |
| Library route works | Authorized account, library search, missing/stale item, deletion/change, privacy review | Catalog access does not prove personal-library access. |
| Playback works | Correct player choice, authorization/subscription, queue, prepare/play/pause/stop, interruption/route | Catalog lookup or play invocation does not prove audio output. |
| Background audio works | Signed audio mode, physical lock/background route, interruption/output device, energy review | An app that plays in foreground is not background-audio proof. |
| System player route is truthful | SystemMusicPlayer state reconciliation and explicit copy | App-owned player state is not Music app state. |

## ShazamKit

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Signature match works | Fixed signature, SHSession result, match/no-match/error, catalog identity | A match is a candidate, not certainty or ownership. |
| Microphone matching works | Microphone permission, AVAudioEngine route, streaming buffers, noise/silence, stop | One clean audio fixture does not prove real environments. |
| Capture stops safely | Match/cancel/no-match/error/interruption, engine stop/pause, no unexpected retention | A result callback does not prove the microphone is inactive. |
| Custom catalog works | Catalog version, reference signatures, metadata, mismatch, update, replay | A custom match does not prove catalog freshness. |
| Managed session works | SHManagedSession lifecycle, system/account behavior, permission, cancellation | SHSession fixture does not prove managed-session behavior. |
| Match history is safe | User-approved save, provenance, deletion, library/account behavior | A match does not imply permission to save to a personal library. |

## AI and side effects

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| AI normalizes tag text | Fixed payloads, typed output, edit/reject, provenance | Model output does not prove payload safety. |
| AI ranks audio candidates | Multiple candidates, ambiguity, no-match, stale catalog, confirmation | Ranking is not identity or certainty. |
| AI proposes MusicKit action | Authorization/subscription re-check, editable proposal, explicit action | Proposal does not add/play/share by itself. |
| AI triggers NFC write | Payload preview, validation, explicit confirmation, tag/session result | Generated content cannot silently write physical media. |
| Result is synced/shared | Domain commit, CloudKit/share proof, privacy/deletion, current source revision | Match callback is not remote persistence. |

## Design and accessibility

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Scan/listen surface is understandable | Ready/active/no-match/error/cancel state task test | Waveform or animation is not semantic status. |
| Result is reviewable | Raw source, candidate metadata, provenance, edit/confirm/reject, undo/retry | A success checkmark is not user confirmation. |
| Liquid Glass is native | Light/dark, reduced transparency, contrast, Dynamic Type, hit regions, state transitions | Material does not replace readable content. |
| Accessible task works | VoiceOver, Voice Control, Switch Control, keyboard/pointer, localization, no-color-only cues | Haptics/audio cannot be the sole output. |
| Privacy is safe | Lock screen/notification/widget/shared screen, logs, raw audio/payload retention | User permission does not authorize arbitrary exposure. |

## Release and physical evidence

| Claim | Required evidence |
| --- | --- |
| NFC entitlement is shipped | Archive entitlements, usage string, supported formats, target membership |
| MusicKit integration is shipped | MusicKit App Service configuration, usage string, signed app, catalog/player test |
| Microphone match is shipped | Usage string, audio session route, signed app, capture stop, privacy review |
| Custom catalog is shipped | Signed/versioned catalog resource, metadata schema, update/recovery path |
| Physical workflow is ready | Named device/OS, tags/protocols/account/subscription/audio environment, known failures |

## Evidence packet

Record:

~~~text
feature:
target/bundle/build:
sdk/deployment target:
route:
nfc capability/entitlement:
music authorization/subscription:
shazam catalog:
microphone usage/route:
physical device/tag/protocol/audio:
payload/signature/catalog fixture:
permission state:
match/no-match/error:
candidate/provenance:
ai model/context:
review/confirmation:
playback/write/library/system side effect:
accessibility settings:
privacy/retention:
release artifact:
known failures:
claim supported:
claim not yet supported:
~~~

## Claim language

Use:

- “The signed device read the declared NDEF format on the named tag and showed the payload for confirmation before opening the validated destination.”
- “MusicKit authorization was granted for the named account; catalog search returned a candidate, while playback was tested separately with ApplicationMusicPlayer.”
- “ShazamKit produced a match from the named audio fixture; the app preserved the raw provenance and required confirmation before saving.”
- “The AI normalized a selected candidate into an editable draft; it did not infer identity or perform a tag write/library change.”

Avoid:

- “The tag is trusted.”
- “The song is definitely identified” from one match.
- “Music is available” from catalog metadata without subscription/player proof.
- “The microphone is private” without retention and system-surface review.
- “Works on iPhone” without named hardware and tag/audio/account evidence.

## Sources

- [Core NFC](https://developer.apple.com/documentation/corenfc)
- [Building an NFC Tag-Reader App](https://developer.apple.com/documentation/corenfc/building-an-nfc-tag-reader-app)
- [NFCNDEFReaderSession](https://developer.apple.com/documentation/corenfc/nfcndefreadersession)
- [NFCNDEFReaderSessionDelegate](https://developer.apple.com/documentation/corenfc/nfcndefreadersessiondelegate)
- [NFCTagReaderSession](https://developer.apple.com/documentation/corenfc/nfctagreadersession)
- [MusicKit](https://developer.apple.com/documentation/musickit)
- [MusicAuthorization](https://developer.apple.com/documentation/musickit/musicauthorization)
- [MusicCatalogSearchRequest](https://developer.apple.com/documentation/musickit/musiccatalogsearchrequest)
- [ApplicationMusicPlayer](https://developer.apple.com/documentation/musickit/applicationmusicplayer)
- [SystemMusicPlayer](https://developer.apple.com/documentation/musickit/systemmusicplayer)
- [ShazamKit](https://developer.apple.com/documentation/shazamkit)
- [SHSession](https://developer.apple.com/documentation/shazamkit/shsession)
- [SHManagedSession](https://developer.apple.com/documentation/shazamkit/shmanagedsession)
- [Matching audio using the built-in microphone](https://developer.apple.com/documentation/shazamkit/matching-audio-using-the-built-in-microphone)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
