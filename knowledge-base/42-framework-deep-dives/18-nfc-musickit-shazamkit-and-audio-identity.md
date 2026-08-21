# Core NFC, MusicKit, ShazamKit, and audio identity

## Capability map

These frameworks touch real-world identity and media, but they solve different problems:

| User outcome | Apple route | Authority |
| --- | --- | --- |
| Read or write a nearby physical tag | Core NFC | The tag’s protocol/payload plus user confirmation |
| Find catalog or library music | MusicKit | Apple Music authorization, catalog/library scope, subscription/capability state |
| Play music in the app | MusicKit ApplicationMusicPlayer/SystemMusicPlayer | The selected player, authorization, playback/account state |
| Identify captured sound | ShazamKit SHSession/SHManagedSession | A catalog match with uncertainty and no-match/error states |
| Match proprietary audio | ShazamKit SHCustomCatalog | The app-owned reference-signature catalog |
| Turn a scan or match into an action | SwiftUI/domain layer + optional App Intent | User-confirmed domain policy, not raw tag/audio metadata |

Do not combine a tag identifier, a song match, an Apple Music catalog result, and a user identity as if they were the same proof. Each is an observation with its own authorization, freshness, and trust boundary.

## Core NFC route

Core NFC can read NDEF messages and interact with protocol-specific tags such as ISO 7816, ISO 15693, FeliCa, and MIFARE. The route begins with the target’s NFC capability, the Near Field Communication Tag Reader Session Formats entitlement, and NFCReaderUsageDescription.

### NDEF session

Use NFCNDEFReaderSession when the product needs NDEF messages. The session delegate receives activation, detected messages/tags, and invalidation. Decide whether the session should invalidate after the first successful read or remain active for multiple tags/writes.

The system scanning alert is part of the native interaction. Keep the alert message concise and tell the person how to position the phone. If multiple tags are detected, the app should not guess which one is authoritative; ask the person to isolate or select the intended tag.

### Protocol-specific tags

Use NFCTagReaderSession for ISO 7816, ISO 15693, FeliCa, and MIFARE routes. Configure protocol identifiers and polling options to the minimum required set. For ISO 7816 and FeliCa, the relevant identifiers are constrained by the target’s configuration/Info.plist. A detected tag is not automatically a trusted product, credential, or person.

### Background tag reading

Core NFC also documents background tag reading. Treat it as a system invocation boundary:

- validate the message or URL;
- show the person what was detected;
- avoid executing a destructive action from the payload alone;
- require normal app authorization;
- protect against replay, malformed data, and unexpected scheme/host;
- keep a manual scanner route for devices or contexts where background reading is unavailable.

### NFC writes

Writing is a mutation to physical media. Show the exact payload before writing, validate capacity/format, handle tag loss, and verify the resulting read where the protocol allows it. A successful write callback does not establish that a future reader will interpret the payload as your product expects.

## MusicKit route

MusicKit integrates with Apple Music catalog, library, playback, subscription, and data request routes. Before using MusicKit, request informed consent through MusicAuthorization and include NSAppleMusicUsageDescription. Then model authorization separately from subscription and catalog availability.

| State | Meaning |
| --- | --- |
| notDetermined | The app has not asked for permission |
| denied/restricted | The app cannot use the requested music-data route |
| authorized | The app may use the permitted music-data API |
| subscription unavailable | Catalog/library/playback feature may still be limited |
| network/catalog unavailable | Show cached/local content or a retry route |

MusicCatalogSearchRequest is a catalog search route. MusicLibrarySearchRequest and related library requests are user-data routes. They should not be presented as equivalent. Search results can be incomplete, region/account-dependent, or stale. Preserve the catalog identifier and title/artist metadata used for display.

### Playback boundary

ApplicationMusicPlayer plays music for the app without changing the Music app’s state. SystemMusicPlayer controls the Music app’s state. Select deliberately:

- use ApplicationMusicPlayer for an app-owned playback experience;
- use SystemMusicPlayer when the user expects the Music app’s queue/state to change;
- configure background audio only for a product that genuinely plays audio;
- handle authorization, subscription, route changes, interruptions, and item availability;
- never imply that a catalog lookup guarantees playback.

MusicKit’s artwork and model types can feed a native SwiftUI surface, but artwork is still remote/account/media content with caching, attribution, and privacy considerations.

## ShazamKit route

ShazamKit creates an acoustic signature from captured audio and compares it with a reference catalog. The signature is a smaller one-way representation, not a recording and not a general speech transcript. A match can include timecode and SHMediaItem metadata.

### SHSession

Use SHSession for explicit matching:

1. choose the Shazam catalog or an SHCustomCatalog;
2. create SHSession;
3. supply a precomputed SHSignature or streaming AVAudioPCMBuffer;
4. handle match, no-match, and error results;
5. stop/pause audio capture when the task ends;
6. present the result as an observation for review.

SHSession is asynchronous and can be driven by a delegate or the documented async result/sequence route. A match is not proof that the recording is the exact intended source, that the person owns it, or that an action is authorized.

### SHManagedSession

Use SHManagedSession when the product wants a managed recording/matching route and its documented system behavior. Keep microphone permission, capture lifecycle, match state, and library update separate. If a custom catalog is used, version the catalog and its metadata so a new catalog does not silently reinterpret old matches.

### Microphone route

Matching from the built-in microphone requires AVAudioEngine or the appropriate audio pipeline plus microphone permission and NSMicrophoneUsageDescription. Avoid retaining raw audio longer than needed. Stop or pause capture when the match goal is complete. Handle interruption, no-input, route changes, silence, noisy environments, and the person cancelling.

## Audio identity is not identity

The following pipeline is safer:

~~~text
tag/audio observation
  -> decode/verify
  -> candidate metadata
  -> person review
  -> domain record
  -> optional MusicKit/CloudKit/App Intent side effect
~~~

Do not let a tag payload open a privileged route without URL/domain validation. Do not let a song match select a contact, health record, purchase, or shared record without an independent confirmation and authorization boundary. On-device AI may rank candidate matches or summarize metadata; it cannot convert a noisy match into certainty.

## Native design and Liquid Glass

The system already owns important parts of the experience:

- NFC scanning alert and session feedback;
- permission prompts for NFC, microphone, MusicKit, and playback;
- Apple Music catalog/media semantics;
- system audio route/interruptions;
- Live Activity or notification projections where a separate feature uses them.

Build the app-owned surfaces around clear states:

| State | Primary content | Action |
| --- | --- | --- |
| Ready to scan/listen | What will be read and why | Start |
| Reading/listening | Calm instruction and stop | Cancel |
| Candidate found | Title/metadata/source and confidence language | Review |
| No match | What was attempted and fallback | Try again/manual entry |
| Permission denied | Local explanation and Settings/manual route | Open settings or continue limited |
| Saved | Confirmed record and provenance | Edit/share/export |

Use Liquid Glass to group start/stop/review actions, not to blur the tag payload or cover album artwork. The result surface should remain legible with Dynamic Type, reduced transparency, and VoiceOver.

## AI enrichment

An on-device model can:

- normalize an NDEF text payload into an editable draft;
- classify a matched media item into a user-chosen collection;
- summarize music metadata selected by the person;
- map a known tag to an app-owned workflow;
- suggest a follow-up action based on explicit context.

Keep the original tag payload, signature/match metadata, catalog identifier, model route/version, and user edits. Require confirmation before:

- opening external links;
- writing back to a tag;
- adding to a library or playlist;
- starting playback;
- sharing or syncing the result;
- creating a notification, calendar item, purchase, or other side effect.

## Verification route

- Compile each framework in the intended app target and inspect availability.
- Test NFC only on supported physical hardware with real tags/protocols.
- Test NDEF malformed payloads, multiple tags, tag loss, user cancellation, writes, capacity, and background invocation.
- Test MusicKit authorization, denial, subscription/catalog/library limitations, region/network failure, player route, interruptions, and background audio if used.
- Test ShazamKit microphone permission, silence/noise, no-match, match, custom catalog version, capture interruption, and stop.
- Verify privacy strings, entitlements, catalog/service configuration, signed release artifact, and any external URL handling.
- Use accessibility settings, localization, Dynamic Type, reduced transparency, and manual fallback routes.
- Keep AI proposals editable and record source/provenance; do not claim identity or certainty from a match.

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
- [MusicAuthorization.request](https://developer.apple.com/documentation/musickit/musicauthorization/request%28%29)
- [MusicCatalogSearchRequest](https://developer.apple.com/documentation/musickit/musiccatalogsearchrequest)
- [ApplicationMusicPlayer](https://developer.apple.com/documentation/musickit/applicationmusicplayer)
- [MusicPlayer](https://developer.apple.com/documentation/musickit/musicplayer)
- [ShazamKit](https://developer.apple.com/documentation/shazamkit)
- [SHSession](https://developer.apple.com/documentation/shazamkit/shsession)
- [SHManagedSession](https://developer.apple.com/documentation/shazamkit/shmanagedsession)
- [Matching audio using the built-in microphone](https://developer.apple.com/documentation/shazamkit/matching-audio-using-the-built-in-microphone)
- [SHSessionDelegate](https://developer.apple.com/documentation/shazamkit/shsessiondelegate)
- [SHCustomCatalog](https://developer.apple.com/documentation/shazamkit/shcustomcatalog)
- [AVAudioEngine](https://developer.apple.com/documentation/avfaudio/avaudioengine)
- [AVAudioPCMBuffer](https://developer.apple.com/documentation/avfaudio/avaudiopcmbuffer)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
