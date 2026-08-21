# NFC, MusicKit, and ShazamKit route

## Use this route when

Use this route when an app connects a physical tag, Apple Music catalog/library, or captured audio match to a user-reviewed workflow. Keep physical observation, protected media access, candidate metadata, user-authored records, and side effects separate.

## Route selector

| Need | First API route | Required boundary |
| --- | --- | --- |
| Read NDEF | NFCNDEFReaderSession | NFC capability/entitlement, usage description, session lifecycle, malformed payload |
| Read ISO/FeliCa/MIFARE | NFCTagReaderSession | Polling/configuration identifiers, protocol handling, physical-tag proof |
| Write NDEF | NFCNDEFReaderSession with write flow | Preview/confirm payload, tag capacity, tag loss, verification |
| Background tag invocation | Core NFC background tag reading | Validate untrusted payload, system handoff, manual fallback |
| Search Apple Music catalog | MusicCatalogSearchRequest | MusicKit authorization, catalog/account/network state |
| Search personal library | MusicLibrarySearchRequest or library route | User permission, library scope, stale/partial data |
| Play without changing Music app state | ApplicationMusicPlayer | Authorization, subscription/playback, audio route and background mode |
| Control Music app state | SystemMusicPlayer | Explicit user expectation and state reconciliation |
| Match captured audio | SHSession | Microphone permission/audio pipeline, match/no-match/error |
| Managed recording and matching | SHManagedSession | Session lifecycle, microphone privacy, exact managed-session behavior |
| Match proprietary content | SHCustomCatalog + SHSession | Catalog signing/versioning, provenance, custom metadata |

## Route A: NDEF scan

1. Add Near Field Communication Tag Reading to the app target.
2. Add NFCReaderUsageDescription with an outcome-oriented explanation.
3. Configure the supported NDEF formats/entitlement.
4. Check NFCNDEFReaderSession.readingAvailable.
5. Create the session with the delegate, queue, and invalidateAfterFirstRead choice.
6. Set an alert message that tells the person how to scan.
7. Begin the session from an explicit action.
8. Decode NDEF records into an untrusted candidate.
9. Validate scheme/host/payload size/record type.
10. Show a review surface before saving, opening, writing, or sharing.

If multiple tags are detected, require isolation or selection. Do not use signal strength, first callback order, or display text as an identity guarantee.

## Route B: protocol-specific tag

Use NFCTagReaderSession when the tag is not only an NDEF message. Define the polling options and protocol identifiers in the target. Map the protocol response to a typed candidate and retain the raw protocol metadata needed for diagnostics without exposing secrets.

For credentials, payment-adjacent data, access controls, or device commands:

- define the cryptographic/authentication boundary separately;
- do not treat a readable UID as authorization;
- reject replay, malformed, unexpected, and oversized responses;
- require confirmation for physical writes or controls;
- test loss of field and session invalidation;
- define what happens when a tag belongs to a different product/version.

## Route C: MusicKit search and playback

1. Include NSAppleMusicUsageDescription.
2. Request MusicAuthorization.
3. Model authorized/denied/restricted separately from MusicSubscription state.
4. Use catalog requests for catalog results and library requests for personal data.
5. Limit queries and preserve catalog identifiers.
6. Use ApplicationMusicPlayer or SystemMusicPlayer deliberately.
7. Handle account, subscription, network, content-rating, playback, interruption, and route changes.
8. Add background audio only when the product genuinely plays audio in the background.

Catalog search can return candidate items. A result does not guarantee that the item is playable, subscribed, available in the region, or present in the person’s library.

## Route D: ShazamKit matching

### Precomputed signature

Use an existing SHSignature for a controlled audio asset:

~~~text
source audio
  -> SHSignatureGenerator
  -> SHSession(catalog:)
  -> match/result
  -> typed candidate
  -> review
~~~

### Streaming microphone

Use the audio engine/mixer route to feed AVAudioPCMBuffer values to SHSession.matchStreamingBuffer(_:at:). Request microphone permission before configuring capture. Stop the engine when the match task ends, is cancelled, or returns a usable result.

### Match policy

Store:

- catalog type and version;
- matched media identifier;
- title/artist/custom metadata;
- query time and capture duration;
- no-match/error reason;
- source record and user review state.

If the product uses a custom catalog, version metadata and reference signatures together. Do not reinterpret a historical match with an incompatible catalog without a migration/review policy.

## Shared review pipeline

~~~text
NFC/audio/media observation
  -> typed candidate
  -> validation and provenance
  -> optional on-device AI normalization/ranking
  -> user edit/confirmation
  -> local record
  -> optional playback, tag write, library change, sync, or system action
~~~

AI can make the candidate easier to understand. It cannot:

- establish a person’s identity;
- prove an NFC payload is safe;
- prove a Shazam match is certain;
- grant MusicKit access;
- start playback or change a library without user action;
- write a tag without a confirmed payload;
- create a sensitive downstream record without validation.

## Native design handoff

Use the system reader/permission interaction and keep the app-owned route compact:

- scanning/listening instruction;
- live status and cancel;
- candidate/result card;
- review/confirm action;
- manual fallback;
- provenance/details.

Liquid Glass may group Start/Stop/Review/Save actions, but the detected content stays on a readable surface. For MusicKit, separate search/browse from playback. For tag writes and system-side effects, use explicit verbs.

## Privacy and entitlements

Required configuration can include:

- NFC tag-reading capability and formats entitlement;
- NFCReaderUsageDescription;
- NSAppleMusicUsageDescription;
- MusicKit App Service/developer configuration;
- microphone usage description for audio matching;
- audio session/background audio configuration for playback if used;
- catalog or custom-catalog resources;
- signed target membership and supported-device metadata.

Inspect the final archive. A framework import, simulator result, or prompt response does not prove entitlement/service readiness.

## Failure matrix

| Failure | Preserve | Fallback |
| --- | --- | --- |
| NFC unavailable | User input/manual route | Manual entry or saved candidates |
| User cancels scan | Existing form/source | Try again |
| Multiple tags | All untrusted candidates | Ask to isolate/select |
| Malformed payload | Raw diagnostic safely | Ignore/open review |
| Music denied | Local catalog/cache | Manual search or import |
| Subscription unavailable | Catalog metadata | Preview/offer/system route |
| Shazam no match | Capture metadata only | Try again/manual search |
| Microphone interrupted | No raw audio by default | Resume/stop |
| Match ambiguous | Candidate set/provenance | User selection |
| Write fails/tag lost | Original payload | Retry after explicit confirmation |

## Verification questions

- Which physical device and tag protocols are supported?
- Does the target contain the right entitlements and usage strings?
- Is a candidate visibly distinct from a confirmed record?
- What does a no-match/denied/cancelled state do?
- Does the MusicKit route read catalog, library, or playback state?
- Which player owns playback state?
- Is microphone capture stopped after the match?
- Can AI enrichment be rejected without losing raw provenance?
- What exactly was proven on hardware versus in a fixture?
- Is the route privacy-safe in notifications, widgets, and lock-screen surfaces?

## Sources

- [Core NFC](https://developer.apple.com/documentation/corenfc)
- [Building an NFC Tag-Reader App](https://developer.apple.com/documentation/corenfc/building-an-nfc-tag-reader-app)
- [NFCNDEFReaderSession](https://developer.apple.com/documentation/corenfc/nfcndefreadersession)
- [NFCNDEFReaderSessionDelegate](https://developer.apple.com/documentation/corenfc/nfcndefreadersessiondelegate)
- [NFCTagReaderSession](https://developer.apple.com/documentation/corenfc/nfctagreadersession)
- [NFCTagReaderSession.Configuration](https://developer.apple.com/documentation/corenfc/nfctagreadersession/configuration)
- [NFCReaderUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nfcreaderusagedescription)
- [MusicKit](https://developer.apple.com/documentation/musickit)
- [MusicAuthorization](https://developer.apple.com/documentation/musickit/musicauthorization)
- [MusicCatalogSearchRequest](https://developer.apple.com/documentation/musickit/musiccatalogsearchrequest)
- [ApplicationMusicPlayer](https://developer.apple.com/documentation/musickit/applicationmusicplayer)
- [SystemMusicPlayer](https://developer.apple.com/documentation/musickit/systemmusicplayer)
- [ShazamKit](https://developer.apple.com/documentation/shazamkit)
- [SHSession](https://developer.apple.com/documentation/shazamkit/shsession)
- [SHManagedSession](https://developer.apple.com/documentation/shazamkit/shmanagedsession)
- [SHSessionDelegate](https://developer.apple.com/documentation/shazamkit/shsessiondelegate)
- [Matching audio using the built-in microphone](https://developer.apple.com/documentation/shazamkit/matching-audio-using-the-built-in-microphone)
- [AVAudioEngine](https://developer.apple.com/documentation/avfaudio/avaudioengine)
- [AVAudioPCMBuffer](https://developer.apple.com/documentation/avfaudio/avaudiopcmbuffer)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
