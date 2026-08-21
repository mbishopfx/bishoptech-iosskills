# SwiftUI MusicKit, ShazamKit, and AVFAudio media-identity route

Music identity is not one API call. A native app usually crosses several
authority boundaries: the Apple Music catalog, a person’s Apple Music data,
an Apple Music player, protected microphone input, Shazam or custom reference
catalogs, and the app’s own interpretation layer. Keep those boundaries
visible in the architecture and in the UI.

~~~text
music catalog
  -> MusicKit App Service + MusicAuthorization
  -> MusicCatalogSearchRequest / MusicCatalogResourceRequest
  -> storefront-aware catalog result

personal Apple Music data
  -> informed user permission
  -> MusicSubscription capability check
  -> MusicLibraryRequest / MusicLibrary / MusicDataRequest
  -> user-scoped data or an explicit unavailable state

playback
  -> choose ApplicationMusicPlayer or SystemMusicPlayer
  -> queue and player lifecycle
  -> interruption/route/error recovery

audio identity
  -> NSMicrophoneUsageDescription + microphone permission
  -> AVAudioApplication / AVAudioSession / AVAudioEngine
  -> SHManagedSession or SHSession
  -> SHMatch | noMatch | error
  -> deterministic match review and user action

optional intelligence
  -> typed, source-bound explanation proposal
  -> human review
  -> no invented identity, entitlement, rights, or library mutation
~~~

The most important rule is that a result is evidence for the next decision,
not permission to skip the next decision. A successful `MusicAuthorization`
request does not prove that the person has an Apple Music subscription. A
`SHMatch` does not authorize playback or prove ownership. A Foundation Models
explanation does not become media metadata merely because it sounds plausible.

## Route selection

| Product need | Primary route | Required boundary | Do not infer |
| --- | --- | --- | --- |
| Search public Apple Music catalog content | `MusicCatalogSearchRequest` or `MusicCatalogResourceRequest` | MusicKit configuration, user permission, current storefront, request errors | That every catalog result is playable for the current person |
| Read a person’s Apple Music library | `MusicLibraryRequest` or a `/me` Apple Music API route | Music permission, user-token-backed request, library/subscription state | That catalog IDs and library IDs are interchangeable |
| Add a catalog item to the person’s library | `MusicLibrary.shared.add(_:)` after an explicit user action | Authorized MusicKit flow, library capability, supported item, error/retry UI | That a successful lookup silently grants write permission |
| Play without changing the Music app’s state | `ApplicationMusicPlayer` | Playability, subscription, player error, interruption and route handling | That playback is independent of external audio hardware |
| Control the Music app’s state | `SystemMusicPlayer` | Explicit product intent, external-state copy, player and route proof | That app-local state is the source of truth for the Music app |
| Identify captured audio in Shazam’s catalog | `SHManagedSession` or `SHSession` | Microphone permission, ShazamKit App ID service, network/service availability, physical input | That a no-match means the audio is silent or that a match is legally definitive |
| Identify audio in a private catalog | `SHCustomCatalog` + `SHSession` or managed session | Reference-signature pipeline, catalog versioning, supported query duration | That a custom media item has Apple Music rights or a public URL |
| Explain a match or recommend a next action | Typed app-owned explanation proposal, optionally backed by on-device AI | Source fields, deterministic identity, model availability, review, fallback | That generated prose may create or mutate media state |

Do not collapse these into `mediaService.lookupAndPlay()`. A route object should
make its authority and proof requirements explicit so a SwiftUI view can show
the correct next action: ask permission, sign in to Apple Music, choose a
catalog result, start listening, review a match, or recover from an error.

## MusicKit target and authorization contract

MusicKit integrates an Apple-platform app with the Apple Music API and provides
Swift model types, playback support, artwork views, and subscription-offer
surfaces. The app target must enable the MusicKit App Service for the matching
explicit App ID. The Developer portal configuration, Xcode target capability,
bundle identifier, signed entitlements, and distributed build are separate
artifacts to verify.

Add `NSAppleMusicUsageDescription` to the app’s `Info.plist` with a truthful,
specific explanation of the feature. Apple documents that the system
terminates the app when it attempts to access a person’s music data without
this key. A generic “music access” string is weak product communication;
explain whether the app searches, reads, plays, or adds music, and request the
smallest data scope needed by the current feature.

`MusicAuthorization.currentStatus` is a permission state. Request it at a
user-understandable moment with `MusicAuthorization.request()`, not as an
unexplained launch side effect. Treat `.notDetermined`, `.authorized`,
`.denied`, and `.restricted` as distinct UI states. If the user denies access,
catalog-only or local-only functionality may still be possible, but the route
must not keep retrying the same prompt.

Permission is not subscription. After permission, query
`MusicSubscription.current` and branch on its capabilities:

- `canPlayCatalogContent` gates the app’s catalog playback path.
- `canBecomeSubscriber` can justify a documented offer or handoff.
- `hasCloudLibraryEnabled` informs whether cloud-library behavior is available.

These values are runtime facts and can change. Store a short-lived route
snapshot for rendering, but re-check before a consequential playback or
library mutation. A disabled capability needs a recoverable UI rather than an
infinite spinner or a fake “available” button.

### Catalog, library, and API-token boundaries

`MusicCatalogSearchRequest` searches the public Apple Music catalog by term.
`MusicCatalogResourceRequest` loads catalog resources using typed filters.
`MusicLibraryRequest` reads the person’s music library. `MusicLibrary.shared`
provides the mutation route for supported library-addable items. `MusicDataRequest`
can load an arbitrary Apple Music API endpoint when the typed surface does not
cover the needed route.

The Apple Music API distinguishes `/catalog/{storefront}` resources from `/me`
personalized resources. Catalog resources use storefront-aware IDs; a person’s
library can contain distinct library identifiers. A server or custom HTTP
client must distinguish developer-token failures from user-token or permission
failures and must never treat a `401`, `403`, or empty collection as an
identity assertion.

On Apple platforms, MusicKit automatically manages the developer and Music
User Token behavior for the supported MusicKit-for-Swift route. Do not place a
MusicKit private key or a long-lived developer secret in the app bundle. If a
backend calls Apple Music API directly, keep signing material on the server,
scope its endpoints, and return only the minimum app data required. A user
token is also not a general-purpose login token for the app’s own account
system.

Storefront and localization are part of data correctness. The same search term
can yield different availability, language, explicit-content policy, and
catalog identifiers by region. Make storefront choice visible in a server
contract or derive it through the documented user-storefront path; do not bake
`us` into a global service without a product reason.

## MusicKit playback lanes

MusicKit offers two player ownership models:

| Player | State ownership | Use when | UI/evidence consequence |
| --- | --- | --- | --- |
| `ApplicationMusicPlayer.shared` | The app owns a queue and playback state that does not affect the Music app | The product needs an in-app listening lane | Show app-local queue and handle subscription, interruptions, and route changes |
| `SystemMusicPlayer.shared` | The player controls the Music app’s state | The product intentionally hands playback to the system Music experience | Explain that playback may change external Music state; refresh from the actual player state |

Build a `MusicPlayer.Queue` from playable items or explicit queue entries.
Prepare the chosen player, then call `play()` within the async lifecycle. Keep
one owner for queue mutation; otherwise a search result, mini-player, and
background task can race to replace the current entry. Observe the player’s
state through the current SDK surface and model `idle`, loading, playing,
paused, stopped, failed, and unavailable states in the app domain.

Do not assume a `Song` returned from search is playable. Subscription state,
region, content availability, account state, and current audio route can each
change. A failed `prepareToPlay()` or `play()` should preserve the selected
item, explain the next action, and allow retry without duplicating queue
entries.

If a matched Shazam item includes an Apple Music ID or URL, treat it as a
candidate handoff to MusicKit. Resolve or search the catalog again, compare the
stable ID and user-visible metadata, then require the person to tap Play, Add
to Library, or Open in Apple Music. Never autoplay from a microphone match
without an intentional product decision and appropriate user expectation.

## ShazamKit matching contract

ShazamKit compares an opaque query signature with reference signatures in the
Shazam catalog or a custom catalog. Apple describes the signature as a much
smaller, one-way representation of the time-frequency distribution of audio;
it cannot be converted back into the recording. The app still needs microphone
permission when it captures from the built-in microphone, but the signature
pipeline is not the same thing as uploading the original audio for storage.

### `SHSession` versus `SHManagedSession`

Use `SHSession` when the app owns the audio-buffer pipeline or already has an
`SHSignature`:

1. Create `SHSession()` for the Shazam catalog or `SHSession(catalog:)` for a
   custom catalog.
2. Generate a signature with `SHSignatureGenerator`, or call
   `matchStreamingBuffer(_:at:)` for compatible streaming buffers.
3. Use `result(from:)` for a single async result or the delegate route for
   streaming results.
4. Handle `.match`, `.noMatch`, and `.error` as separate domain states.

Use `SHManagedSession` when the app wants the managed recording-and-match
route. Its `prepare()`, `result()`, `results`, `state`, and `cancel()` methods
make the lifecycle explicit. Treat `idle`, `prerecording`, and `matching` as
observable states for the SwiftUI surface. Keep cancellation tied to the view
task and to the user’s Stop action so the microphone is not left running after
navigation.

`SHSession` query signatures must use supported PCM sample rates documented by
the SDK, including 48,000, 44,100, 32,000, and 16,000 Hz. The signature
duration must fit the active catalog’s minimum and maximum query duration.
Longer audio should be sliced with `SHSignature.slices(from:duration:stride:)`
or matched as a streaming buffer. A silent or discontinuous buffer can produce
an invalid signature; present that as an input-quality state rather than a
confident “unknown song” conclusion.

Matching the Shazam catalog requires enabling ShazamKit for the App ID. A
custom catalog does not require that service. A signed build’s capability
configuration and the actual App ID are release evidence; a simulator call
that reaches a delegate is not.

### Match results and provenance

`SHMatch.mediaItems` is ordered by match quality, and a single query can map to
multiple media items. `SHMatchedMediaItem` exposes fields such as title,
artist, Apple Music ID/URL, artwork URL, match offset, predicted current match
offset, frequency skew, and—on its supported OS boundary—confidence from 0.0
to 1.0. Preserve the raw match provenance in an app-owned record:

~~~text
match record
  queryStartedAt
  catalogKind: shazam | custom
  catalogVersion or service snapshot
  title / artist / IDs returned by the framework
  matchOffset / predictedCurrentMatchOffset
  confidence when available
  input route and permission state
  user decision: ignored | saved | played | opened
~~~

Confidence is useful for ranking and UI explanation, not a legal or ownership
claim. If multiple items are returned, show the result list or a review
threshold instead of silently selecting an arbitrary item. If the match has no
Apple Music ID, do not fabricate one from a title/artist string.

`SHLibrary.default` is the newer Shazam-library route on its supported OS
boundary. `SHMediaLibrary` is deprecated on newer SDKs. Saving to a Shazam
library is a distinct side effect from adding an item to Apple Music; request
the user’s clear consent and record which library action occurred.

### Custom catalogs

Build a custom catalog from reference signatures generated from audio the
product has the right to process, paired with `SHMediaItem` metadata. A custom
catalog can model training videos, product sounds, private installations, or
other controlled content. Version the catalog outside the matching session,
and create a new session when the active catalog changes. Once a catalog is
used by a session, do not assume later reference-signature mutations affect
that session.

On supported newer OS versions, persist `SHCustomCatalog.dataRepresentation`
and load it with the data initializer. The custom catalog’s metadata is app
data; it does not confer Apple Music playback rights, Shazam catalog access, or
copyright permission.

## Protected audio input and route ownership

For a microphone-driven `SHSession`, use `AVAudioEngine` and an input/mixer
pipeline that converts the hardware’s native format to one of ShazamKit’s
supported formats. The official built-in-microphone route uses an audio mixer,
installs a tap, and passes `AVAudioPCMBuffer` values to
`matchStreamingBuffer(_:at:)`.

Add `NSMicrophoneUsageDescription` before touching the microphone. On the
current SDK, request permission through `AVAudioApplication` and configure an
`AVAudioSession` category/mode/options appropriate to the product. Activate
the session only when listening is intentional, and stop the engine and remove
the tap when matching ends.

Audio input and MusicKit playback can compete for hardware and system focus.
Make the audio session coordinator a single owner that defines transitions:

~~~text
idle
  -> requesting microphone
  -> input permission denied | granted
  -> configuring audio route
  -> listening
  -> match review | no match | error | cancelled
  -> deactivate input and restore prior playback policy
~~~

Observe interruptions, route changes, media services reset, and input mute
state where relevant. Do not blindly resume after every interruption: the
hardware route, user intent, scene lifecycle, and current permission may have
changed. Test built-in microphone, wired headphones, Bluetooth input/output,
speaker, route loss, phone-call-like interruption, background/foreground, and
the simulator’s limited audio behavior separately.

Never log raw audio buffers, signatures, tokens, or full user-library payloads.
If an app stores a match history, store the minimum metadata and provide a
clear retention/deletion policy. The LLM route must receive typed, redacted
fields rather than an unrestricted microphone stream or Apple Music token.

## SwiftUI and on-device AI boundary

The SwiftUI route can be composed from native controls:

- a searchable catalog surface with `List`, `NavigationStack`, and typed
  loading/error states;
- an explicit Start Listening control with a permission explainer before the
  system prompt;
- a match-review card with artwork, title, artist, source label, match offset,
  confidence when available, and separate Play, Add to Library, Save to
  Shazam Library, Open, and Dismiss actions;
- a compact mini-player that reports the selected MusicKit player lane;
- a settings/permissions surface that explains how to recover from denied
  music or microphone access.

Use Liquid Glass where the current SwiftUI design system calls for a
functional control group, toolbar, floating control, or transient surface.
Keep the matched media content legible and let artwork or a controlled
background provide hierarchy. Do not put every row, artwork tile, and text
paragraph inside an opaque custom glass shell. Group related controls in a
`GlassEffectContainer`, preserve content behind the glass, and test tint,
contrast, Dynamic Type, Reduce Transparency, Reduce Motion, VoiceOver, Switch
Control, and external keyboard navigation.

An optional on-device model can draft a short explanation such as “why this
match may be interesting,” summarize deterministic genre/artist metadata, or
propose a playlist label. The model may not decide that a match is correct,
invent an Apple Music ID, claim that a person has a subscription, assert music
rights, or call `MusicLibrary.shared.add` without an explicit deterministic
user action. Use a typed proposal with the source IDs and a “Review” state;
when the model is unavailable, return the same feature with a deterministic
template or hide it.

Treat model output as untrusted text. Constrain the prompt to the selected
`SHMediaItem`/`Song` fields, cap output length, avoid sending raw audio or
tokens, and render output with appropriate accessibility labels. A user must
be able to see the canonical title/artist and source before accepting the
generated explanation.

## Release and proof boundaries

Archive the exact app target with the MusicKit and ShazamKit capabilities,
usage descriptions, bundle identifier, and deployment target. Inspect the
signed archive’s entitlements and `Info.plist`; do not rely on Xcode’s project
editor alone. TestFlight evidence must use the distributed build and an
eligible physical device with the intended Apple Music account, region, audio
route, microphone permission, and App ID configuration.

Minimum proof matrix for this route:

| Proof level | Evidence |
| --- | --- |
| Source | Official MusicKit, Apple Music API, ShazamKit, AVFAudio, and SwiftUI links |
| Build | Every route snippet typechecks against the installed iOS 26.4 simulator SDK |
| Configuration | App ID services, target capabilities, usage descriptions, bundle ID, entitlements |
| Permission | Music authorization and microphone authorization flows on a physical device |
| Runtime | Catalog search, subscription capability, library read/write, selected player, match/no-match/error, cancellation, interruption, route loss |
| Device | Built-in mic, speaker, headphones/Bluetooth, foreground/background, and external route behavior |
| Distribution | Signed archive inspection, TestFlight install, and release checklist for the actual build |

The simulator is useful for compile, view-state, and deterministic fixture
tests. It is not proof of microphone quality, Apple Music account behavior,
Shazam service entitlement, audio routes, or App Store distribution.

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
- [MusicPlayer](https://developer.apple.com/documentation/musickit/musicplayer)
- [MusicDataRequest](https://developer.apple.com/documentation/musickit/musicdatarequest)
- [User Authentication for MusicKit](https://developer.apple.com/documentation/applemusicapi/user-authentication-for-musickit)
- [Handling Requests and Responses](https://developer.apple.com/documentation/applemusicapi/handling-requests-and-responses)
- [Storefronts and Localization](https://developer.apple.com/documentation/applemusicapi/storefronts_and_localization)
- [ShazamKit](https://developer.apple.com/documentation/shazamkit)
- [ShazamKit product page](https://developer.apple.com/shazamkit/)
- [SHSession](https://developer.apple.com/documentation/shazamkit/shsession)
- [SHManagedSession](https://developer.apple.com/documentation/shazamkit/shmanagedsession)
- [SHCustomCatalog](https://developer.apple.com/documentation/shazamkit/shcustomcatalog)
- [SHSignatureGenerator](https://developer.apple.com/documentation/shazamkit/shsignaturegenerator)
- [SHMatch](https://developer.apple.com/documentation/shazamkit/shmatch)
- [SHMatchedMediaItem](https://developer.apple.com/documentation/shazamkit/shmatchedmediaitem)
- [SHMediaItem](https://developer.apple.com/documentation/shazamkit/shmediaitem)
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
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
