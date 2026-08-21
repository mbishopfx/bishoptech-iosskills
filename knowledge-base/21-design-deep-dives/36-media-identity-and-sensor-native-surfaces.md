# Media identity and sensor-native surfaces

## Design objective

NFC and audio matching make the physical world available to an app, but the first result is an observation, not a command. Native design should help the person understand what the device detected, what the app knows, what it does not know, and what will happen after confirmation.

The best Apple-like surface is often a focused system interaction followed by a quiet review screen:

~~~text
system scan/listen
  -> candidate/result
  -> source and confidence context
  -> person confirmation
  -> app-owned record/action
~~~

Do not build a dashboard full of waveforms, floating material, and raw tag fields before the person understands the current task.

## Permission before hardware

Explain the purpose immediately before the system prompt:

- NFC: what object or tag the person should bring near the phone;
- microphone: what sound is captured and when capture stops;
- MusicKit: whether the app reads catalog/library data or controls playback;
- background tag reading: what happens when the system detects a supported tag.

The purpose copy should be plain language. Do not hide a microphone or music permission inside an unrelated “continue” button, and do not claim that a denied permission makes the app unusable if manual entry or a saved-record route exists.

## Sensor-state composition

| State | Visual hierarchy | Primary action |
| --- | --- | --- |
| Ready | One-sentence outcome and source scope | Scan or Listen |
| Preparing | Native progress/instruction | Cancel |
| Detecting | Position/audio instruction and stop | Stop |
| Candidate | Identified metadata, source, time, confidence language | Review |
| No match | What was searched and why no result was found | Try again/manual entry |
| Ambiguous | Multiple candidates or conflicting payload | Select/inspect |
| Permission denied | What is blocked and what remains possible | Settings/manual route |
| Saved | Confirmed record and provenance | Edit/share |

The detected candidate should not visually resemble a confirmed record until the person accepts it. Use a clear “Review” or “Use this” action instead of applying a large success checkmark immediately.

## NFC surfaces

The system scanning alert is already part of the interaction. The app-owned screen should supply:

- a concise instruction before scanning;
- a stop/cancel route;
- a readable result after detection;
- protection against multiple tags;
- malformed-payload handling;
- a manual route if hardware is unavailable.

When writing a tag, show the payload in a preview card and identify whether the operation overwrites existing content. The confirmation action should state the actual mutation, such as “Write this link to tag,” not “Continue.”

If background tag reading opens the app, treat the payload as untrusted input. Render a safe preview first and validate URL scheme, host, record ID, and authorization before any external navigation or side effect.

## Audio-matching surfaces

For ShazamKit or custom catalog matching, show that the app is listening and how to stop. Avoid implying that a waveform is the match itself. A match result should include:

- title/artist or custom item label;
- source catalog or app-owned collection;
- match time/recency if useful;
- no-match/error distinction;
- a manual search or retry path;
- a review action before saving or playing.

Do not expose raw microphone audio in a result card unless the product explicitly needs it. End or pause capture when the matching goal is met, and make that state visible.

## MusicKit surfaces

Catalog search, library search, and playback are different tasks. Design them as different screens or modes:

- catalog: browse/search and inspect metadata;
- library: the person’s authorized collection;
- playback: queue, play/pause, seek, route, and interruption;
- subscription: explain why a capability is unavailable and show the system offer only when appropriate.

If the app changes the Music app’s state, say so. If it uses ApplicationMusicPlayer, say that playback belongs to this app. Keep subscription limitations visible without treating them as an app error.

Artwork is content, not decoration. Use readable titles/artist metadata, content rating where relevant, loading/placeholder/error states, and safe caching. Do not let album art carry the only meaning of the result.

## Liquid Glass composition

Use Liquid Glass for functional grouping:

- a Start/Stop group around the active sensor task;
- a compact Review/Save action group below a candidate;
- a playback control group with clear state;
- a small source/status capsule that can expand into details.

Keep raw tag text, NDEF records, audio metadata, and album artwork on content surfaces with sufficient contrast. Avoid a blurred card over a moving waveform where the person cannot read the candidate or stop listening.

Material transitions should reflect state:

| State change | Treatment |
| --- | --- |
| Ready to detecting | Short focus transition and instruction change |
| Detecting to candidate | Reveal result; do not auto-commit |
| Candidate to saved | Brief confirmation, then settle |
| Detecting to no match | Calm fallback; no red alarm |
| Permission denial | Explain and offer alternate route |

Respect reduced transparency and Reduce Motion. A person should know what the system is doing without a shimmer, pulse, or haptic.

## Accessibility and alternate input

Sensor surfaces must work without sight, color, or audio:

- give Start/Stop/Review/Save actions semantic labels;
- announce “Listening” and “Match found” once, not every audio buffer;
- expose match confidence language as text;
- label tag payload fields and link destinations;
- keep Dynamic Type from truncating artist/title or NDEF text;
- support Voice Control and keyboard activation for manual routes;
- use haptics as optional reinforcement, never as the only detection signal;
- ensure focus moves to the candidate heading after a result;
- test VoiceOver when a session invalidates or a permission is denied;
- localize reading instructions, plural tags, duration, and music metadata.

A no-match state should be reachable and understandable to VoiceOver. A match result should not be announced as certain if the product still requires review.

## AI review shell

An AI review shell can sit after detection:

~~~text
source observation
  -> extracted metadata
  -> AI-normalized proposal
  -> user edit
  -> validated record
~~~

Label the proposal as generated, preserve the raw tag/audio/catalog identifiers, and show what the person is approving. Do not let the model:

- infer a person’s identity from a tag or song;
- follow an arbitrary tag URL;
- add music to a library without confirmation;
- start playback without an explicit action;
- create a sensitive record from a noisy match;
- claim copyright, ownership, or location from a match.

## Privacy and attention

Listening is a high-attention state. Make the microphone active state visible and provide a stop action. Keep permission copy and status text honest. For lock screen, notifications, widgets, or shared screens, use neutral wording for sensitive tag/audio results unless the person has intentionally enabled detailed content.

The app should record provenance such as NFC, MusicKit catalog, ShazamKit catalog, custom catalog, or manual entry. Provenance helps people correct a bad match and prevents later AI passes from treating an observation as user-authored fact.

## Design review checklist

- Is the system-owned scan/listen interaction used correctly?
- Can the person tell whether the app is reading, writing, listening, or idle?
- Does a match remain a candidate until reviewed?
- Can a tag payload or music result trigger a side effect only after confirmation?
- Is the no-match/manual route as intentional as the success route?
- Does Liquid Glass group actions without hiding sensor/media content?
- Are titles, metadata, confidence, and permission states accessible?
- Does the app preserve source/provenance for AI enrichment?
- Are lock-screen, notification, and shared-screen projections privacy-safe?

## Sources

- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Core NFC](https://developer.apple.com/documentation/corenfc)
- [Building an NFC Tag-Reader App](https://developer.apple.com/documentation/corenfc/building-an-nfc-tag-reader-app)
- [MusicKit](https://developer.apple.com/documentation/musickit)
- [MusicAuthorization](https://developer.apple.com/documentation/musickit/musicauthorization)
- [ApplicationMusicPlayer](https://developer.apple.com/documentation/musickit/applicationmusicplayer)
- [MusicCatalogSearchRequest](https://developer.apple.com/documentation/musickit/musiccatalogsearchrequest)
- [ShazamKit](https://developer.apple.com/documentation/shazamkit)
- [SHSession](https://developer.apple.com/documentation/shazamkit/shsession)
- [SHManagedSession](https://developer.apple.com/documentation/shazamkit/shmanagedsession)
- [Matching audio using the built-in microphone](https://developer.apple.com/documentation/shazamkit/matching-audio-using-the-built-in-microphone)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
