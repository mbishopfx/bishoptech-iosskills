# MediaPlayer: Now Playing, remote commands, and media-library boundaries

MediaPlayer connects an app’s playback model to Apple’s system media surfaces and external controls. It is the route for Now Playing metadata, Lock Screen and Control Center controls, remote command handling, multiple-player Now Playing sessions, and optional access to the user’s synced media library.

This is an app integration with system-owned surfaces. The app supplies metadata and command handlers; it does not control the system’s formatting or guarantee that every accessory displays every field.

Use this deep dive when an app needs to:

- publish current title, artist, artwork, duration, position, playback rate, and queue context;
- become the active Now Playing app;
- respond to play/pause/seek/skip/track/feedback commands from system controls or accessories;
- coordinate multiple AVPlayer objects with MPNowPlayingSession;
- access the user’s media library after explicit authorization;
- decide whether a Now Playing item should be eligible for content suggestions, including Journaling Suggestions;
- prove Lock Screen, Control Center, external-accessory, audio-route, accessibility, and release behavior.

Do not use MediaPlayer as a replacement for AVFoundation playback, MusicKit catalog/subscription access, External Accessory sessions, or a custom media database.

## System surface ownership

| Surface | App supplies | System controls |
| --- | --- | --- |
| Now Playing information | Metadata dictionary and playback state updates | Layout, formatting, visibility, and destination surface |
| Lock Screen controls | Enabled remote commands and handlers | Presentation and event delivery |
| Control Center | Same Now Playing session and commands | Presentation and active-app routing |
| External media accessory | Metadata and remote command response | Accessory display and command transport |
| AirPlay destination | Now Playing metadata | Destination rendering and route behavior |
| App player | Playback UI, queue, state, and review | Audio/video framework output and interruptions |

The Now Playing information center docs state that the system or connected accessory handles display consistently. Do not claim that a custom card exactly reproduces the Lock Screen or Control Center.

## Choose the Now Playing architecture

| Playback architecture | Use |
| --- | --- |
| One custom player | MPNowPlayingInfoCenter.default and shared MPRemoteCommandCenter, or a single MPNowPlayingSession |
| Multiple custom AVPlayer objects | MPNowPlayingSession to coordinate players and associated command/info centers |
| AVPlayerViewController-owned player | Let the controller manage its own Now Playing session; do not add your own session to that player |
| System player | Do not register handlers for events the system player already handles |
| Media library browsing | MPMediaLibrary authorization and query route |
| Music catalog/subscription | MusicKit route, with MediaPlayer only for system playback projection when appropriate |

Apple’s MPNowPlayingSession docs explicitly warn not to use a custom session with the AVPlayer presented by AVPlayerViewController. Choose one owner for playback and Now Playing state.

## Now Playing metadata

The nowPlayingInfo dictionary can include:

- title, album title, artist, composer, genre;
- artwork;
- media type;
- playback duration;
- elapsed playback time;
- playback rate and default rate;
- live-stream state;
- queue count and queue index;
- external content and user-profile identifiers;
- language options and chapter/advertisement context where applicable;
- an exclude-from-suggestions flag.

Update metadata from the canonical playback state. A UI slider position is not enough to prove the player’s actual time. Reconcile position, duration, rate, buffering, queue changes, interruptions, route changes, and end-of-item transitions.

Metadata policy:

| State | Projection |
| --- | --- |
| preparing | Title/artwork only if meaningful; no false playing state |
| playing | Elapsed time, duration, rate, artwork, queue context |
| paused | Position and rate zero or paused state according to the player contract |
| buffering | Keep title but show appropriate playback status |
| interrupted | Preserve position; stop claiming active progression |
| ended | Advance or clear according to queue policy |
| failed | Clear or mark unavailable; expose retry in app |
| stopped | Clear app-owned Now Playing info when no longer eligible |

Do not update every field on every UI render. Use a single metadata publisher/reducer with explicit ownership.

## Remote commands

MPRemoteCommandCenter.shared returns the shared remote command center. Commands include play, pause, stop, toggle, next/previous track, repeat, shuffle, playback rate, seek, skip, position change, rating, like/dislike, bookmark, and language options.

For each command:

1. enable only commands the current player supports;
2. register one handler owned by the active playback coordinator;
3. map the event to a typed domain action;
4. handle the action on the correct playback actor/queue;
5. return the appropriate handler status;
6. update Now Playing metadata after the result;
7. remove handlers when the coordinator is torn down.

Do not expose a command in system UI if the app cannot perform it in the current item/state. Disabling a command tells the system not to display the related control when the app is Now Playing.

An incoming remote command is user intent, not guaranteed player completion. Return commandFailed or another appropriate status when the domain action cannot be accepted.

## Active Now Playing app

Apple’s external-player documentation says an app must begin playing content and be the Now Playing app before it receives remote control events. Test the route from:

- the app player;
- Lock Screen;
- Control Center;
- connected audio/media accessories;
- route changes and interruptions;
- the app in foreground, background, and after process restoration where applicable.

Do not assume a handler fires merely because it was registered. Do not treat a command event as proof that audio reached the speaker or destination.

## MPNowPlayingSession

MPNowPlayingSession manages Now Playing information and remote commands for multiple players. It has:

- players;
- isActive and canBecomeActive;
- becomeActiveIfPossible;
- automaticallyPublishesNowPlayingInfo;
- nowPlayingInfoCenter;
- remoteCommandCenter;
- a delegate for session changes.

Use one session owner and make player membership changes explicit. When a player is removed, update queue/index metadata and decide whether the session remains eligible.

For a custom AVPlayer, choose whether the session automatically publishes or whether the app publishes a deliberately projected dictionary. Avoid two writers racing over nowPlayingInfo.

## Media-library authorization

MPMediaLibrary has a separate authorization state: notDetermined, denied, restricted, or authorized. Request access only when the product needs to inspect the user’s library. Playback of app-owned media and publishing Now Playing info are separate from reading the user’s synced media library.

If the app observes library changes:

1. request authorization;
2. use the default library only after the state is known;
3. build focused queries;
4. begin generating library change notifications only while needed;
5. invalidate or refresh app-owned cache on change;
6. end notifications when the feature no longer needs them;
7. avoid treating a missing item as deleted without a current authorization/account explanation.

Library access is personal data. Do not pass full media-library queries or item metadata into an AI model without a clear product purpose and retention policy.

## Journaling Suggestions and content suggestions

Apple’s current MPNowPlayingInfoCenter documentation says that, beginning with iOS 17.2, media donated through Now Playing may appear as a Journaling Suggestions suggestion or in other apps using that framework unless the app opts out. The MPNowPlayingInfoPropertyExcludeFromSuggestions value is the explicit metadata control for excluding the item.

Decide this per content type:

| Content | Policy question |
| --- | --- |
| Public podcast/music content | Is contribution expected and disclosed? |
| Private voice note | Should it be excluded? |
| Sensitive health/therapy audio | Exclude unless the product has a strong, explicit reason |
| Account-restricted media | Does the identifier disclose more than intended? |
| User-authored recording | Can the person control suggestion contribution? |

Do not describe Now Playing donation as a guarantee that another app will display the content. Do describe the app’s opt-out choice accurately.

## Audio and interruption boundary

AVAudioSession and AVFoundation own playback, route, interruption, and media timing. MediaPlayer owns system metadata and command surfaces. Keep the boundaries visible:

- AVFoundation/player result: actual playback state;
- AVAudioSession: audio route/interruption/activation state;
- MediaPlayer: system-facing metadata and command intent;
- app domain: queue, entitlement, account, content license, and record state.

A system control’s play command should call the same typed playback action as the app’s play button, not a parallel code path.

## Native Liquid Glass design

Use Liquid Glass in the app-owned player for:

- compact transport controls;
- queue/context actions;
- current-item summary;
- bounded AI review such as “continue from last position?”

Keep the Now Playing system surface system-owned. Do not create a fake Lock Screen card or expose controls that are not enabled in MPRemoteCommandCenter. Keep title, artwork, elapsed time, and accessibility labels readable when the material is disabled.

## On-device AI media route

AI can propose:

- a queue reorder;
- a chapter jump;
- a summary of the current item;
- a typed playback action;
- a user-approved metadata cleanup.

The playback coordinator validates:

- item identity and availability;
- current player/session;
- authorization and account state;
- range/duration;
- command support;
- user confirmation;
- privacy and content policy.

The model cannot claim that the audio played, a remote device accepted a command, or a Now Playing item is appropriate for a journal suggestion.

## Proof boundary

| Claim | Required evidence |
| --- | --- |
| Metadata is configured | Signed target, canonical projection, runtime dictionary |
| Lock Screen/Control Center shows item | Physical device with actual playback and system surface |
| Remote play/pause works | Physical Lock Screen/Control Center/accessory event and player result |
| Unsupported command is hidden | Disabled command and system-surface observation |
| Multiple-player session works | Named players, active-session transitions, physical/system test |
| Media library access works | Permission state, query result, library-change route |
| Suggestion opt-out works | Exclude metadata, Journaling Suggestions/privacy test, redacted fixture |
| Background playback works | Audio/session configuration, physical lock/background test |
| AI is bounded | Typed proposal, validation, no unauthorized content transfer |
| Release ready | Final signed artifact, privacy/usage declarations, physical/system/accessory proof |

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
