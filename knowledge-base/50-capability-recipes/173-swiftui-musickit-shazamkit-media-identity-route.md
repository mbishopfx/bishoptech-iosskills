# Capability recipe: MusicKit, ShazamKit, and native media identity

Use this recipe when an app needs Apple Music discovery or playback, audio
recognition, a custom reference catalog, or a reviewable media-identity flow.
It deliberately separates target configuration, account authority, protected
input, recognition, side effects, and optional on-device explanation.

## Outcome contract

The finished route should let a person:

1. understand why the app needs Apple Music and/or microphone access;
2. grant or decline each protected capability independently;
3. search Apple Music catalog content or read the supported personal library;
4. optionally listen for a match through ShazamKit or a custom catalog;
5. review canonical matched metadata and available provenance;
6. choose an explicit playback, library, save, open, or dismiss action;
7. use an optional typed explanation without treating generated text as
   identity, entitlement, rights, or mutation authority.

The route must also recover from denied permission, unavailable subscription,
no match, invalid input, route interruption, service failure, cancellation,
stale results, and a missing physical-device capability.

## 1. Decide the authority lanes before writing views

Create separate domain types or coordinators for:

| Coordinator | Owns | Does not own |
| --- | --- | --- |
| `MusicAccessCoordinator` | `MusicAuthorization`, subscription snapshot, catalog/library requests | Microphone permission or the app’s account login |
| `MusicPlaybackCoordinator` | One selected MusicKit player, queue, playback state, interruption recovery | Search-result identity or library authorization |
| `AudioInputCoordinator` | `AVAudioApplication`, `AVAudioSession`, `AVAudioEngine`, route/tap lifecycle | Apple Music tokens or match ranking |
| `MediaMatchCoordinator` | `SHSession`/`SHManagedSession`, catalog choice, match/no-match/error state | User acceptance of Play/Add/Open |
| `MediaActionCoordinator` | Explicit user actions and success/error reporting | Guessing IDs or accepting model output as proof |
| `ExplanationCoordinator` | Typed, redacted explanation proposal and fallback | Deciding the canonical match or performing side effects |

Use an epoch or request ID for every asynchronous lane. A result may update
the UI only when its epoch is still current and the selected catalog/player
has not changed.

## 2. Configure targets and services

For the app target:

1. Enable the MusicKit App Service for the explicit App ID that matches the
   target bundle identifier.
2. Add the MusicKit capability in Xcode and inspect the signed archive later.
3. Add `NSAppleMusicUsageDescription` with specific, truthful copy.
4. Add `NSMicrophoneUsageDescription` if the app captures microphone audio.
5. Enable ShazamKit for the App ID when matching the Shazam catalog. A custom
   catalog does not require ShazamKit service enablement.
6. Keep deployment targets explicit for `SHManagedSession`, confidence fields,
   `SHLibrary`, `SHCustomCatalog.dataRepresentation`, and SwiftUI Liquid Glass
   APIs. Use availability checks where the app supports older OS versions.
7. If an extension, widget, App Intent, or companion target consumes the
   route, configure that target separately. Do not assume the app target’s
   entitlements transfer.

Verify the App ID, bundle identifier, capability configuration, usage strings,
and signed entitlements as separate artifacts. A green Xcode capability
checkbox is not distribution proof.

## 3. Request access in an intentional sequence

Do not present every permission dialog at launch. Ask for the capability at
the moment its feature is explained:

~~~text
catalog-only feature
  -> MusicKit explanation
  -> MusicAuthorization.request()
  -> status: authorized | denied | restricted

listen feature
  -> microphone explanation
  -> AVAudioApplication record permission
  -> status: granted | denied

post-authorization
  -> MusicSubscription.current
  -> capabilities: catalog playback | can become subscriber | cloud library
~~~

The route should make `.denied` and `.restricted` recoverable through Settings
guidance, not through repeated prompts. Keep MusicKit permission separate from
microphone permission in both state and copy.

## 4. Search and resolve catalog content

For free-text search, use `MusicCatalogSearchRequest` with the smallest set of
types needed by the current screen, set a bounded limit, and cancel stale
requests. For a stable identifier, use `MusicCatalogResourceRequest` with the
appropriate typed filter. Use `MusicLibraryRequest` only for the person’s
library and re-check authorization/capability before library-sensitive work.

If the app receives an Apple Music ID from `SHMediaItem`, treat it as a
candidate identifier. Resolve it through MusicKit or a documented Apple Music
URL, compare canonical ID/title/artist fields, and render a missing/ambiguous
mapping state. Do not use title/artist fuzzy matching as proof of identity.

If a typed MusicKit request does not expose a needed endpoint, use
`MusicDataRequest` with a fully formed `URLRequest` and handle response status,
Apple Music API error objects, storefront, and authentication boundaries. Keep
custom API parsing in a service layer and test malformed/partial responses.

## 5. Choose the playback owner

Choose one lane in the product contract:

- `ApplicationMusicPlayer.shared` when the app owns an isolated queue and
  should not alter the Music app’s state.
- `SystemMusicPlayer.shared` when the product intentionally controls the
  Music app and clearly tells the user that external state can change.

Build a queue from playable items, call `prepareToPlay()`, and then call
`play()`. Serialize queue mutation and expose the selected lane in the domain
state. On `prepareToPlay()` or `play()` failure, keep the matched item and show
the next recovery action. Do not claim “playing” before the player confirms
the transition.

## 6. Capture and match audio

Choose `SHManagedSession` for the managed recording/match lifecycle, or choose
`SHSession` when the app owns the buffer pipeline or signature generation.

For an app-owned `SHSession` pipeline:

1. Configure an `AVAudioSession` category/mode/options suitable for the input
   and output policy.
2. Request microphone permission through `AVAudioApplication`.
3. Configure `AVAudioEngine` and, when needed, an `AVAudioMixerNode` to convert
   input to a ShazamKit-supported PCM format.
4. Install one tap, pass contiguous buffers to
   `matchStreamingBuffer(_:at:)`, and stop/remove the tap when the route ends.
5. For a finite buffer, use `SHSignatureGenerator`, then
   `await SHSession.result(from:)`.
6. Handle `.match`, `.noMatch`, and `.error` independently.

For a custom catalog, instantiate `SHSession(catalog:)` or the corresponding
managed-session catalog initializer. Version the catalog, keep the reference
audio processing rights explicit, and create a new session when the catalog
changes.

## 7. Review the result before side effects

Map framework output to a domain value such as:

~~~text
MediaMatchReview
  source: shazam | custom
  canonicalTitle: String?
  canonicalArtist: String?
  appleMusicID: String?
  appleMusicURL: URL?
  artworkURL: URL?
  matchOffset: Duration?
  predictedCurrentMatchOffset: Duration?
  confidence: Double?
  reviewState: new | accepted | dismissed | stale
~~~

Display the source, canonical fields, and confidence availability. If there
are multiple media items, preserve their ordering and let the person select.
If no Apple Music mapping exists, disable Apple Music actions rather than
guessing.

Only after the person taps an action should the route:

- prepare/play an approved MusicKit item;
- call `MusicLibrary.shared.add(_:)` for a supported item;
- add a valid `SHMediaItem` to `SHLibrary.default`;
- open a documented Apple Music or Shazam URL;
- dismiss and record the user’s choice.

Report success only after the async framework operation returns successfully.
Keep failure state and retry input-bound; do not replay a stale request when a
new match has superseded it.

## 8. Add optional on-device explanation

Define a `Sendable` input containing only deterministic fields from the
selected match and resolved catalog item. The proposal should contain the
source ID, bounded text, model/fallback state, and review status.

Allowed proposal uses:

- explain `matchOffset` or the difference between catalog and library state;
- summarize known genre, artist, or editorial fields;
- draft a neutral listening note for the person to accept or edit.

Disallowed model authority:

- deciding whether the match is correct;
- inventing or repairing an Apple Music ID/URL;
- asserting a subscription, license, ownership, or copyright right;
- calling a player or library mutation without an explicit user action;
- exposing raw microphone audio, tokens, or unrestricted personal-library
  payloads to the prompt.

If on-device AI is unavailable or the output fails validation, render a
deterministic fallback and retain the canonical result.

## 9. SwiftUI route composition

Use a view model or observable route store that exposes explicit state enums:

~~~text
MusicAccessState
  notRequested | requesting | authorized | denied | restricted | failed

ListeningState
  idle | explaining | requestingPermission | listening | stopping | stopped

MatchState
  idle | preparing | matching | matched([Review]) | noMatch | failed | cancelled

PlaybackState
  unavailable | preparing | playing | paused | stopped | failed
~~~

Use `NavigationStack` for catalog-to-detail-to-review flow, `.searchable` for
catalog search, `List`/`ScrollView` for results, native `Button` controls for
side effects, and `ContentUnavailableView` for no-match/error states. Use
`task(id:)` with cancellation and request epochs so a disappearing screen does
not leave the microphone or player task active.

Apply Liquid Glass to functional groups such as the Listen control, toolbar,
mini-player, and match actions. Keep canonical media content readable over
the underlying material. Test Dynamic Type, VoiceOver, Reduce Motion, Reduce
Transparency, increased contrast, keyboard/Switch Control, light/dark mode,
and iPad split view before polishing transitions.

## 10. Verification and release handoff

The implementation is ready for a release audit only when the proof matrix in
the companion page is complete. At minimum, record:

- source links and installed SDK availability notes;
- target capabilities, usage descriptions, App ID services, and signed
  entitlements;
- permission states and Settings recovery;
- catalog/storefront/search/library behavior;
- chosen player lane, interruption, route, and cancellation behavior;
- Shazam match/no-match/error and custom-catalog behavior;
- physical microphone, speaker, headphones/Bluetooth, and route-loss checks;
- accessibility and reduced-motion checks;
- archive, TestFlight, and exact-build evidence.

## Acceptance checklist

- [ ] The route has separate coordinators for MusicKit access, playback, audio
  input, matching, side effects, and AI explanation.
- [ ] The App ID, target capabilities, `Info.plist`, and signed archive agree.
- [ ] Apple Music permission is not confused with subscription or app login.
- [ ] Catalog, library, and `/me`/storefront boundaries are explicit.
- [ ] The selected player ownership model is visible and tested.
- [ ] Microphone permission, audio session, input route, tap teardown, and
  interruption handling are implemented.
- [ ] Match, no-match, error, cancellation, stale-result, and multiple-match
  states are testable.
- [ ] Side effects require a user action and report only confirmed success.
- [ ] AI output is typed, redacted, bounded, source-bound, reviewable, and
  optional.
- [ ] Physical-device and distribution proof are attached before release.

## Sources

- [MusicKit](https://developer.apple.com/documentation/musickit)
- [Using Automatic Developer Token Generation for Apple Music API](https://developer.apple.com/documentation/musickit/using-automatic-token-generation-for-apple-music-api)
- [MusicAuthorization](https://developer.apple.com/documentation/musickit/musicauthorization)
- [MusicSubscription](https://developer.apple.com/documentation/musickit/musicsubscription)
- [MusicCatalogSearchRequest](https://developer.apple.com/documentation/musickit/musiccatalogsearchrequest)
- [MusicCatalogResourceRequest](https://developer.apple.com/documentation/musickit/musiccatalogresourcerequest)
- [MusicLibraryRequest](https://developer.apple.com/documentation/musickit/musiclibraryrequest)
- [MusicLibrary](https://developer.apple.com/documentation/musickit/musiclibrary)
- [ApplicationMusicPlayer](https://developer.apple.com/documentation/musickit/applicationmusicplayer)
- [SystemMusicPlayer](https://developer.apple.com/documentation/musickit/systemmusicplayer)
- [MusicDataRequest](https://developer.apple.com/documentation/musickit/musicdatarequest)
- [User Authentication for MusicKit](https://developer.apple.com/documentation/applemusicapi/user-authentication-for-musickit)
- [Handling Requests and Responses](https://developer.apple.com/documentation/applemusicapi/handling-requests-and-responses)
- [ShazamKit](https://developer.apple.com/documentation/shazamkit)
- [SHSession](https://developer.apple.com/documentation/shazamkit/shsession)
- [SHManagedSession](https://developer.apple.com/documentation/shazamkit/shmanagedsession)
- [SHCustomCatalog](https://developer.apple.com/documentation/shazamkit/shcustomcatalog)
- [SHSignatureGenerator](https://developer.apple.com/documentation/shazamkit/shsignaturegenerator)
- [SHMatch](https://developer.apple.com/documentation/shazamkit/shmatch)
- [SHMatchedMediaItem](https://developer.apple.com/documentation/shazamkit/shmatchedmediaitem)
- [SHLibrary](https://developer.apple.com/documentation/shazamkit/shlibrary)
- [Matching audio using the built-in microphone](https://developer.apple.com/documentation/shazamkit/matching-audio-using-the-built-in-microphone)
- [Enable ShazamKit for an App ID](https://developer.apple.com/help/account/configure-app-services/shazamkit)
- [AVAudioApplication](https://developer.apple.com/documentation/avfaudio/avaudioapplication)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Handling audio interruptions](https://developer.apple.com/documentation/avfaudio/handling-audio-interruptions)
- [Responding to audio route changes](https://developer.apple.com/documentation/avfaudio/responding-to-audio-route-changes)
- [NSAppleMusicUsageDescription](https://developer.apple.com/documentation/bundleresources/information_property_list/nsapplemusicusagedescription)
- [NSMicrophoneUsageDescription](https://developer.apple.com/documentation/bundleresources/information_property_list/nsmicrophoneusagedescription)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
