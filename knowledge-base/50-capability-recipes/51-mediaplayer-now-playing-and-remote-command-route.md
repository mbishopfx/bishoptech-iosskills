# MediaPlayer Now Playing and remote-command route

Use this route when a product owns playback but needs to participate in Apple’s system media surfaces: Now Playing metadata, Lock Screen, Control Center, remote accessories, and optionally the user’s media library.

This is a compile-oriented capability blueprint. It does not prove that a player reaches an audio route, that a system surface displays every field, that an accessory accepts a command, that library authorization is granted, or that the final target is ready for distribution.

## Route selector

| Product need | Primary route | Keep separate |
| --- | --- | --- |
| Play app-owned audio or video | AVFoundation or AVKit | Actual player state and audio-session state |
| Publish current item to Apple system surfaces | MediaPlayer | System rendering and destination behavior |
| Receive play, pause, skip, seek, or feedback intent | MPRemoteCommandCenter | Player authorization, queue, and command result |
| Coordinate multiple custom players | MPNowPlayingSession | Player membership and active-session ownership |
| Browse the person’s synced media library | MPMediaLibrary and MPMediaQuery | Permission, library changes, and cache invalidation |
| Search Apple Music catalog or manage subscription playback | MusicKit | Music authorization, storefront, subscription, and catalog rules |
| Connect to a manufacturer accessory | External Accessory or Core Bluetooth | Transport protocol and physical-device proof |
| Render an in-app native player | SwiftUI, AVKit, and app-owned state | Lock Screen and Control Center remain system-owned |

Do not use MediaPlayer as a substitute for a playback engine. Do not request media-library permission merely to publish Now Playing metadata for app-owned content.

## Target register

Before implementation, record the exact target decisions:

| Field | Decision |
| --- | --- |
| App target | Bundle ID, iPhone/iPad family, deployment target, SDK |
| Playback owner | AVPlayer, AVAudioEngine, system player, or another documented engine |
| Now Playing owner | Default MPNowPlayingInfoCenter or one named MPNowPlayingSession |
| Command owner | One playback coordinator for the active command center |
| Audio session | Category, mode, activation policy, interruption/route policy |
| Library feature | None, read-only MPMediaLibrary query, or a separately authorized MusicKit feature |
| Privacy policy | Content types eligible for suggestions; items excluded by default |
| Background | User-facing audio background behavior and matching target configuration |
| Accessibility | VoiceOver state labels, Dynamic Type, alternate input, contrast/material fallback |
| AI boundary | Typed proposals, context allowlist, confirmation, result vocabulary |
| Evidence | Named physical device, system surfaces, route/accessory, signed artifact |

The target register is a planning artifact. The signed target and runtime evidence are the proof.

## Ownership graph

Use one source of truth:

SwiftUI player -> PlaybackStore -> playback engine -> canonical PlaybackState -> MediaPlayer projection

External command -> command adapter -> typed PlaybackAction -> PlaybackStore -> engine result -> state and metadata update

Media-library picker -> authorization gate -> focused MPMediaQuery -> redacted app model

AI request -> approved typed context -> model proposal -> deterministic validator -> user review -> typed PlaybackAction

The app owns:

- current item, queue, entitlement, account, and content policy;
- actual player state and operation results;
- which remote commands are currently supported;
- metadata projection and suggestion-exclusion policy;
- the media-library cache and deletion/refresh policy;
- AI proposal validation and confirmation.

MediaPlayer and the system own:

- Now Playing display and formatting;
- Lock Screen, Control Center, AirPlay, and accessory presentation;
- delivery of external command intent when the app is eligible;
- media-library authorization decision.

AVFoundation and AVAudioSession own:

- playback output, timing, buffering, interruption, route, and activation mechanics.

## Route A: default Now Playing projection

For a single custom player, publish a deliberately projected dictionary:

1. create or update the canonical playback state;
2. map only known values to Now Playing metadata;
3. include a truthful playback rate and elapsed position;
4. omit unknown or misleading fields;
5. update the default information center from one owner;
6. clear app-owned information when the item is no longer eligible.

The system may render the metadata differently on different surfaces. Treat the dictionary as an integration contract, not a pixel layout.

Recommended metadata groups:

| Group | Examples | Rule |
| --- | --- | --- |
| Identity | title, artist, album, artwork | Prefer stable, privacy-safe values |
| Timing | duration, elapsed time, playback rate | Project from the engine, not a UI slider |
| Queue | queue count, queue index | Include only when the queue is meaningful |
| Media type | audio, video, live stream | Do not imply seekability for live content |
| Context | external content ID, user profile ID | Include only when product and privacy policy allow |
| Suggestion policy | exclude-from-suggestions flag | Set explicitly for private or sensitive items |

## Route B: MPNowPlayingSession

Use MPNowPlayingSession when multiple custom AVPlayer instances need coordinated Now Playing state and remote commands.

The route is:

1. enumerate the intended players;
2. create one named session owner;
3. decide whether automatic metadata publication is appropriate;
4. keep the session’s information center and command center behind the playback coordinator;
5. make session activation and player membership changes explicit;
6. observe player/session transitions;
7. update the active item and command availability together.

Do not attach a custom MPNowPlayingSession to the AVPlayer presented by AVPlayerViewController when the controller owns that player’s session. Choose a single ownership model.

## Route C: remote command registration

For every command:

1. map the current domain capability to isEnabled;
2. register exactly one handler owned by the active coordinator;
3. convert the event to a typed action;
4. execute on the actor or queue that owns the player;
5. return a handler status that describes whether the action was accepted;
6. publish the resulting playback state;
7. remove the handler when the owner is gone.

Registering a handler is not evidence that the app is the active Now Playing app. The app must begin playing and become eligible before system external-player events are expected.

Use a capability table instead of hard-coding buttons:

| State | Play | Pause | Seek | Next/previous | Rating/feedback |
| --- | --- | --- | --- | --- | --- |
| Ready and paused | on | off | if supported | if queue supports | if product supports |
| Playing | off | on | if supported | if queue supports | if product supports |
| Buffering | usually off or deferred | usually on for stop/pause policy | product-specific | product-specific | usually off |
| Live stream | on/off by actual state | on | off unless stream supports it | product-specific | product-specific |
| Interrupted | truthful recovery state | product-specific | avoid false completion | product-specific | off when unavailable |
| Failed or unauthorized | off | off | off | off | off |

An incoming command means “the user requested this operation.” It does not mean the player completed it. Return failure or another appropriate status when validation, entitlement, range, or engine execution fails.

## Route D: media-library authorization

Use a just-in-time permission flow:

1. explain the library feature in the app;
2. call the authorization status API;
3. keep the feature in a not-determined, denied, restricted, or authorized state;
4. request authorization only when the person starts the library feature;
5. build a focused query after authorization;
6. project only the fields the feature needs;
7. subscribe to library-change notifications only while the feature needs them;
8. refresh or invalidate cached objects when the library changes;
9. end notification generation when the feature is inactive.

App-owned playback and Now Playing publication should remain available when library access is denied. Do not treat a denied library permission as a general playback failure.

## Route E: privacy and suggestions

Media contributed through Now Playing may be eligible for Journaling Suggestions and other content suggestions. Decide policy per content class and set the exclusion metadata when the product does not want a Now Playing item included.

Suggested default review:

| Content class | Suggested product decision |
| --- | --- |
| Public catalog media | Include only if the user-facing policy supports it |
| Personal recording | Exclude unless the person explicitly enables inclusion |
| Health, therapy, family, or location-linked audio | Exclude by default |
| Shared or account-restricted media | Avoid identifiers that reveal private structure |
| Draft or test content | Exclude from system-facing suggestions |

The exclusion flag controls eligibility; it does not prove that a system suggestion was created or that all copies of content were erased.

## Route F: audio-session boundary

The command adapter should call the same domain action as the in-app control. The playback engine and AVAudioSession then report actual results.

Keep these states distinct:

| State | Meaning |
| --- | --- |
| command-accepted | The coordinator accepted a valid request |
| engine-started | The player began its start operation |
| audio-session-active | The audio session is active according to the app’s policy |
| playing | The engine reports progression at a truthful rate |
| interrupted | The system or route interrupted playback |
| route-changed | The output route changed; playback result remains a separate fact |
| completed | The player reached the intended item/range end |
| unknown | The app cannot prove the requested outcome |

Never label a command as “played successfully” solely because a remote-command handler returned.

## Route G: bounded on-device AI

AI can help with queue and playback intent without owning system effects. Use a closed vocabulary:

~~~swift
struct PlaybackProposal: Sendable, Equatable {
    let itemID: String
    let action: Action
    let reason: String
    let requiresConfirmation: Bool

    enum Action: Sendable, Equatable {
        case play
        case pause
        case seek(seconds: Double)
        case selectQueueIndex(Int)
        case setSuggestionExclusion(Bool)
    }
}
~~~

The deterministic validator must check item identity, authorization, player state, command support, seek bounds, queue membership, privacy policy, and confirmation requirements. Do not send raw media-library records, private transcripts, account identifiers, or full stream URLs to a model unless the product has an explicit, reviewed policy.

## Fallback matrix

| Condition | Safe fallback |
| --- | --- |
| MediaPlayer metadata unavailable | Keep playback and in-app player; show no false system state |
| App is not active Now Playing app | Keep in-app controls; do not claim external-control support |
| Remote command unsupported | Disable command and offer the app-owned equivalent |
| Audio route/interruption changes | Reconcile with AVAudioSession and show truthful state |
| Library permission denied | Keep app-owned playback; offer Settings/help only if useful |
| Library restricted | Explain that the system does not permit access |
| Library changes | Refresh/invalidate the affected cache |
| AI unavailable | Use deterministic queue and playback controls |
| AI proposal invalid | Reject with a recoverable explanation |
| Suggestion privacy not allowed | Set exclusion metadata and keep content in the app |
| System surface differs | Preserve semantics; do not recreate a fake system card |

## Evidence route

Capture evidence in layers:

1. source and target configuration, including background/audio/privacy declarations;
2. runtime metadata dictionary and canonical state transition;
3. physical-device Now Playing view on Lock Screen and Control Center;
4. remote command event plus player/engine result;
5. interruption, route, background, and process-restoration behavior where claimed;
6. media-library authorization and focused query/change handling;
7. suggestion exclusion policy with redacted private-content fixtures;
8. accessibility tasks and Liquid Glass fallback states;
9. AI proposal, validator rejection, confirmation, and no-raw-context test;
10. final signed artifact and release configuration.

## Sources

- [Media Player](https://developer.apple.com/documentation/mediaplayer)
- [MPNowPlayingInfoCenter](https://developer.apple.com/documentation/mediaplayer/mpnowplayinginfocenter)
- [MPNowPlayingSession](https://developer.apple.com/documentation/mediaplayer/mpnowplayingsession)
- [MPRemoteCommandCenter](https://developer.apple.com/documentation/mediaplayer/mpremotecommandcenter)
- [MPRemoteCommand](https://developer.apple.com/documentation/mediaplayer/mpremotecommand)
- [MPRemoteCommandEvent](https://developer.apple.com/documentation/mediaplayer/mpremotecommandevent)
- [Becoming a now playable app](https://developer.apple.com/documentation/mediaplayer/becoming-a-now-playable-app)
- [Handling external player events notifications](https://developer.apple.com/documentation/mediaplayer/handling-external-player-events-notifications)
- [Remote command center events](https://developer.apple.com/documentation/mediaplayer/remote-command-center-events)
- [MPMediaLibrary](https://developer.apple.com/documentation/mediaplayer/mpmedialibrary)
- [MPMediaLibraryAuthorizationStatus](https://developer.apple.com/documentation/mediaplayer/mpmedialibraryauthorizationstatus)
- [Request media library authorization](https://developer.apple.com/documentation/mediaplayer/mpmedialibrary/requestauthorization%28_%3A%29)
- [Exclude Now Playing items from suggestions](https://developer.apple.com/documentation/mediaplayer/mpnowplayinginfopropertyexcludefromsuggestions)
- [AVFoundation](https://developer.apple.com/documentation/avfoundation)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
