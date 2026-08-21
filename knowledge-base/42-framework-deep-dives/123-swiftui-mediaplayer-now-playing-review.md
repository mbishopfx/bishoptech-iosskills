# SwiftUI MediaPlayer Now Playing and remote-command review

MediaPlayer is a system-surface projection layer for apps that play audio or video. The existing [MediaPlayer Now Playing and remote-command deep dive](28-mediaplayer-now-playing-and-remote-command-routes.md) covers the broad API map, media-library boundary, and content-suggestion policy. The [SwiftUI AVFAudio and route-aware playback review](109-swiftui-avfaudio-airplay-route-aware-playback-review.md) covers audio-session and AirPlay behavior. This page adds the focused iOS 26 implementation boundary: one canonical playback owner, one Now Playing publisher, one remote-command router, explicit active-session state, and evidence that separates metadata projection from audible output.

The architecture is:

~~~text
SwiftUI player / CarPlay / Watch / system command
  -> PlaybackCommand
  -> PlaybackCoordinator
  -> app-owned player and AVAudioSession
  -> observed PlaybackState
  -> MediaPlayer projection
  -> Lock Screen / Control Center / AirPlay / accessory surface
~~~

MediaPlayer does not replace the playback engine. It receives metadata and remote intent. The operating system or accessory decides how to render that information. The player and AVAudioSession remain the sources of truth for whether content is actually playing, paused, interrupted, routed, buffered, or audible.

## 1. Choose the playback lane

| Product need | Starting route | Ownership boundary |
| --- | --- | --- |
| App-owned audio or video playback with system controls | AVFoundation player plus MediaPlayer | App owns player truth; MediaPlayer projects it |
| Multiple custom AVPlayer instances | MPNowPlayingSession | One session owns the players and related system controls |
| AVPlayerViewController playback | Let the controller own its player/session | Do not add a custom MPNowPlayingSession to that player |
| Browse the person’s synced media library | MPMediaLibrary | Separate permission and personal-data route |
| Music catalog, subscription, or Apple Music playback | MusicKit | MediaPlayer may still project app playback, but does not provide catalog authorization |
| AirPlay destination selection | AVAudioSession and AVRoutePickerView | The route is system-selected; metadata is a separate projection |
| CarPlay or Watch transport | CarPlay/Watch route plus the same playback coordinator | System surface sends intent; coordinator validates it |

Do not build one playing Boolean that hides:

- app player status;
- AVAudioSession active, route, and interruption state;
- MediaPlayer Now Playing eligibility;
- system command request;
- remote device availability;
- audible output.

Those values can disagree temporarily and need different recovery behavior.

## 2. System surface ownership

The current MPNowPlayingInfoCenter documentation says the app supplies values in nowPlayingInfo while the system or connected accessory controls presentation and formatting. The system may show the projection on the Lock Screen, Control Center, an AirPlay destination such as Apple TV, or a connected accessory.

| Surface | App owns | System owns |
| --- | --- | --- |
| In-app player | Layout, queue, controls, explanation, accessibility | Audio framework behavior and interruptions |
| Now Playing metadata | Canonical values and freshness policy | Rendering, field selection, formatting |
| Lock Screen | Enabled commands and truthful metadata | Presentation, focus, gestures, layout |
| Control Center | Same projection and command route | Presentation and active-app routing |
| AirPlay receiver | Metadata and app playback state | Destination playback/rendering behavior |
| CarPlay | Template data and command handoff | Driver-focused template limits and presentation |
| Watch or accessory | Handoff/command contract | External display and transport |

Never claim that the app drew the Lock Screen. It supplied a system-readable projection.

## 3. One canonical PlaybackState

Define a value model that can drive SwiftUI, MediaPlayer, CarPlay, Watch, and tests:

| Field | Meaning |
| --- | --- |
| itemID | Stable app-owned item identity |
| title, creator, artwork | Metadata that can be safely projected |
| position | Observed or player-derived elapsed time |
| duration | Known duration, or nil for live/unknown |
| rate | Actual player rate, not requested rate |
| status | idle, loading, playing, paused, buffering, interrupted, ended, failed |
| queueIndex and queueCount | Valid queue context |
| isLive | Whether the item is a live stream |
| route | Current AVAudioSession output summary |
| sessionGeneration | Playback coordinator generation used to reject stale callbacks |
| nowPlayingEligible | Whether this state may be projected |
| excludeFromSuggestions | Privacy/content policy decision |

The SwiftUI slider is an input to a typed seek command. It is not authoritative playback position. Reconcile with the player’s current time and publish again after a seek result.

Recommended state flow:

~~~text
item selected
  -> player preparing
  -> player ready
  -> playback requested
  -> rate/position observed
  -> projection published
  -> interruption/route change/buffering
  -> projection refreshed
  -> item ended or stopped
  -> projection advanced or cleared
~~~

## 4. Default center versus MPNowPlayingSession

For a single custom playback owner, use the default MPNowPlayingInfoCenter and shared MPRemoteCommandCenter. For multiple custom AVPlayer objects that need coordinated Now Playing behavior, use MPNowPlayingSession.

MPNowPlayingSession currently provides:

- an array of players;
- addPlayer and removePlayer;
- isActive;
- canBecomeActive;
- becomeActiveIfPossible;
- automaticallyPublishesNowPlayingInfo;
- a session-associated nowPlayingInfoCenter;
- a session-associated remoteCommandCenter;
- a delegate for session changes.

Important ownership rule:

> An AVPlayer can have only one Now Playing session. AVPlayerViewController manages its own player and Now Playing session, so do not attach a custom MPNowPlayingSession to that player.

Choose the owner at architecture time:

| Owner | Metadata writer | Command center |
| --- | --- | --- |
| Default route | MPNowPlayingInfoCenter.default() | MPRemoteCommandCenter.shared() |
| Named session | session.nowPlayingInfoCenter or automatic publication | session.remoteCommandCenter |
| AVPlayerViewController | Controller/system route | Controller/system route |

Do not let an app coordinator and an AVPlayerViewController both write the same Now Playing item. If a session is removed or becomes inactive, clear or transfer projection state deliberately.

## 5. Active Now Playing eligibility

Registering a command handler is not enough. Apple’s external-player guidance says the app must begin playing content and be the Now Playing app before it receives remote-control events. The test path is:

~~~text
configure audio session
  -> start actual player
  -> publish current item metadata
  -> become eligible/active if using a session
  -> receive system/accessory commands
  -> mutate player
  -> publish observed state
~~~

MPNowPlayingSession.isActive answers whether the session is the app’s active Now Playing session. canBecomeActive and becomeActiveIfPossible are separate decisions. A session object’s existence is not proof of system ownership.

For a default center route, the system may send controls to the app that is currently or was most recently playing. If the app is not the active Now Playing app, its handler may not be called. Keep the in-app player usable and describe external controls as unavailable until the route is active.

## 6. Metadata projection

The nowPlayingInfo dictionary can contain the current item’s title, artist/creator, album/collection context, artwork, media type, duration, elapsed playback time, playback rate, live-stream state, queue count/index, chapter/language/ad context, stable external identifiers, and an explicit exclusion from content suggestions.

Project only values from canonical state:

| Canonical state | Metadata decision |
| --- | --- |
| Loading | Title/artwork only when known; no false playing rate |
| Ready/paused | Position and paused rate; enable play |
| Playing | Position, duration/rate, artwork, queue context |
| Buffering | Preserve item identity; avoid advancing position without player evidence |
| Interrupted | Preserve last known position; stop active-rate claim |
| Live stream | Mark live; omit unsupported duration/seek data |
| Ended | Advance to next item or clear according to queue state |
| Failed | Clear or mark unavailable; do not retain stale actionable controls |
| Stopped | Set nowPlayingInfo to nil when the app no longer owns an active item |

Apple documents that setting nowPlayingInfo to nil clears the default center. Treat clearing as a state transition, not as cleanup hidden in a view’s deinitializer.

### Time and rate

MPNowPlayingInfoPropertyElapsedPlaybackTime is elapsed time in seconds. MPNowPlayingInfoPropertyPlaybackRate represents the rate at which the player is actually progressing. A requested speed or slider drag should not be projected until the player confirms the result.

For long gaps between updates, use the player’s observed time and rate rather than writing a timer-driven value that drifts. For live streams, use MPNowPlayingInfoPropertyIsLiveStream and do not show a finite seek bar unless the player genuinely supports that operation.

### Queue and stable identity

Use queue index/count only when the queue has a meaningful current revision. Use MPNowPlayingInfoPropertyExternalContentIdentifier for an opaque stable identifier that references the item to the Now Playing app; do not place a private URL, account token, or raw database key in a system projection.

If the queue changes while an item is active:

1. increment the queue revision;
2. revalidate the current item;
3. update index/count;
4. keep the same item identifier only if the item identity is unchanged;
5. disable next/previous when the new queue cannot fulfill them.

## 7. Automatic versus explicit publication

MPNowPlayingSession.automaticallyPublishesNowPlayingInfo can publish values from the associated players. If automatic publication is true, Apple’s documentation says not to use the session’s nowPlayingInfoCenter. Use one strategy:

| Strategy | Benefit | Risk |
| --- | --- | --- |
| Automatic session publication | Less projection code for eligible player state | Less control over custom privacy, queue, and freshness fields |
| Explicit dictionary | Full control over typed app projection | App owns timing and stale-field cleanup |
| Mixed writers | None | Races, stale artwork, wrong item, unpredictable system state |

For a feature-rich SwiftUI player, explicit projection is often easier to audit because the metadata source, redaction policy, queue revision, and clear conditions are visible. Compile and test the current SDK behavior before choosing.

## 8. Remote command ownership

MPRemoteCommandCenter.shared() returns the shared command center for external accessories and system controls. A command object can:

- add a handler;
- return an opaque token;
- remove a handler by token;
- report handler status;
- be enabled or disabled.

Use a single PlaybackCoordinator to own handler registration. Do not register targets from every view appearance. A view disappearing must not remove a still-active system command route unless the playback feature itself is stopping.

Command route:

~~~text
system/accessory event
  -> MPRemoteCommand handler
  -> translate event to PlaybackCommand
  -> validate current item/queue/route
  -> execute against player
  -> return handler status
  -> publish observed PlaybackState
~~~

The handler status expresses the command result:

| Status | Use |
| --- | --- |
| success | The requested local playback action executed |
| noSuchContent | Current item or requested queue content is unavailable |
| noActionableNowPlayingItem | No valid current item exists |
| deviceNotFound | Required destination/device is unavailable |
| commandFailed | The command could not execute |

Do not return success when an async network request merely started. If a command can only be fulfilled after a server response, define a local pending state and use the command contract supported by the current SDK; never make the system believe playback succeeded before player evidence.

### Command availability

Enable only supported commands:

| Capability | Command |
| --- | --- |
| Pause current item | pauseCommand |
| Resume current item | playCommand |
| Toggle local transport | togglePlayPauseCommand |
| Move in a queue | nextTrackCommand/previousTrackCommand |
| Seek to an absolute time | changePlaybackPositionCommand |
| Skip a fixed interval | skipForwardCommand/skipBackwardCommand |
| Change speed | changePlaybackRateCommand |
| Feedback/rating/bookmark | matching feedback/rating/bookmark command |
| Language option | enable/disable language option commands |

Disable a command when the item, queue, license, or route cannot fulfill it. A hidden command is more truthful than a visible action that fails every time.

## 9. Position, rate, and feedback events

MPChangePlaybackPositionCommandEvent.positionTime carries a requested position. Validate:

- current item identity;
- finite duration or supported live seek;
- position is within the allowed range;
- content license permits the seek;
- no stale queue revision;
- no conflicting seek already committed.

MPChangePlaybackRateCommandEvent carries a requested rate. Clamp it to product-supported values before the player call and republish the actual rate.

Feedback, rating, like/dislike, bookmark, shuffle, repeat, and language-option commands have product semantics beyond transport. Do not register them simply because a UI control exists. Define whether the event changes an app-owned record, requires account authorization, or needs confirmation.

## 10. Artwork and metadata caching

MPMediaItemArtwork supports size-aware artwork through a bounds size and request handler. Use a deterministic artwork pipeline:

~~~text
item artwork identity
  -> bounded cache lookup
  -> size-aware decode/render
  -> MPNowPlayingInfo artwork
  -> cache invalidation on item/artwork revision
~~~

Artwork rules:

- use the item’s real artwork revision;
- avoid blocking a command handler on a large decode;
- provide an appropriately sized image;
- redact private or temporary artwork when the system surface can expose it;
- retain no more artwork than the product needs;
- clear stale artwork when the item changes;
- test light/dark/tinted/low-bandwidth and accessory sizes.

An artwork image appearing on the Lock Screen proves metadata presentation, not that the player is audible or that a route is connected.

## 11. Content suggestions and external identifiers

Apple’s current MPNowPlayingInfoCenter documentation says that media donated through Now Playing may appear in Journal or other apps using Journaling Suggestions unless the app opts out. MPNowPlayingInfoPropertyExcludeFromSuggestions is the explicit Boolean metadata control.

Choose policy per content class:

| Content | Default review question |
| --- | --- |
| Public catalog audio | Does suggestion contribution help the person? |
| Private recording | Should it be excluded? |
| Health, therapy, or legal audio | Exclude unless an explicit, reviewed reason exists |
| Account-restricted stream | Does an external identifier reveal access context? |
| User-created content | Can the person control contribution? |

Now Playing metadata is not a private internal dictionary once it reaches system surfaces. Keep identifiers opaque and exclude content that should not participate in suggestions. Do not claim that setting the field guarantees another app will display or suppress a suggestion; it expresses the app’s documented choice.

## 12. AVAudioSession and physical route truth

AVAudioSession communicates the app’s intended audio use to the system and mediates hardware route/interruption behavior. MediaPlayer’s metadata and command state should follow the player/audio-session reducer:

| Audio state | Now Playing behavior |
| --- | --- |
| Session not activated | No active playback claim |
| Playback route active | Project current player state |
| Interruption began | Preserve item/position; stop active progression |
| Interruption ended | Resume only if the player/audio policy says so |
| Old device unavailable | Pause to avoid unexpectedly sharing audio |
| New device available | Reconcile current route and player state |
| Media services reset | Rebuild audio/player state before projecting active playback |
| No suitable route | Show unavailable/fallback state; do not claim audible output |

Apple’s current route-change guidance emphasizes pausing when a user disconnects headphones because the person may be trying to stop private audio from becoming audible to others. Test that behavior with wired/Bluetooth route removal, AirPlay changes, lock/background transitions, phone calls, Siri, and media-services reset.

Route selection is not playback completion. A selected AirPlay destination is not proof that the remote speaker accepted or rendered the current item.

## 13. CarPlay, Watch, and system handoff

CarPlay and Watch are additional command producers and system surfaces. Do not fork playback state:

~~~text
SwiftUI / CarPlay / Watch / Lock Screen
  -> shared PlaybackCommand
  -> one PlaybackCoordinator
  -> one player/session owner
  -> one canonical state
  -> projections per surface
~~~

CarPlay templates and Watch controls have their own availability, entitlement, driver-attention, connectivity, and lifecycle boundaries. A command received from CarPlay should be validated exactly like a Lock Screen command. A Watch play button is intent, not audio proof.

## 14. SwiftUI and Liquid Glass

Use [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass) for app-owned transport grouping:

- primary play/pause should remain obvious;
- glass groups actions, not the entire artwork and metadata;
- queue, route, and AI actions belong in a secondary group;
- current title and playback status remain readable on a stable content surface;
- disabled command states look disabled and have semantic reasons;
- large text and VoiceOver do not depend on artwork layout;
- reduced transparency/high contrast has a solid fallback.

Do not recreate the Lock Screen or Control Center inside the app. Make the in-app player coherent with the system projection, then let the operating system render its own surface.

Recommended SwiftUI ownership:

- PlaybackStore: observation and UI projection;
- PlaybackCoordinator: command routing and lifecycle;
- PlayerEngine: AVPlayer and AVAudioSession;
- NowPlayingProjector: metadata and command registration;
- ArtworkStore: bounded cache;
- ContentPolicy: suggestions/privacy;
- Optional ExplanationModel: typed, reviewable AI wording.

The view should observe state and call typed commands. It should not call MPRemoteCommandCenter.shared() or mutate nowPlayingInfo from its body.

## 15. Bounded on-device AI

Safe local AI tasks:

- explain the current item or chapter;
- propose a queue reorder from app-owned eligible items;
- suggest a chapter jump;
- draft metadata cleanup for user review;
- summarize a transcript when the person requests it.

Before applying a proposal, the deterministic coordinator validates:

1. item identity and current queue revision;
2. playback entitlement/account state;
3. command support;
4. content licensing and age/privacy policy;
5. user confirmation where the action changes playback or metadata;
6. route and player readiness.

The model must not:

- fabricate a current track or chapter;
- claim a remote command succeeded;
- claim audio was audible;
- select a private media item for system suggestion without policy;
- expose library/account metadata to an external model unnecessarily;
- register system command handlers;
- mutate the player from natural-language text.

## 16. Proof boundary

| Claim | Evidence |
| --- | --- |
| Metadata is configured | Runtime projection from canonical state in a named target |
| App is active Now Playing | Playback starts, session/center state, subsequent system event |
| Lock Screen shows item | Physical device with actual playback and system surface |
| Remote play/pause works | Physical system/accessory event and observed player state |
| Seek works | Position event, player result, and republished elapsed time |
| Unsupported command is hidden | Disabled command and system-surface observation |
| Artwork is correct | Multiple physical/system/accessory sizes and privacy fixture |
| Route recovery works | Headphone/Bluetooth/AirPlay disconnect, interruption, reset |
| Multiple-player session works | Player membership and active-session transitions |
| Media-library access works | Permission state and current authorized query |
| Suggestions policy works | Exclusion metadata and privacy/content fixture |
| AI is bounded | Typed proposal, validator, user review, no side effect from prose |
| Release is ready | Final signed artifact, background audio configuration, privacy metadata, TestFlight/device/accessory evidence |

Preview and simulator runs can prove layout, reducer transitions, and command mapping. They cannot prove audible output, system presentation, route behavior, accessory compatibility, or release readiness.

## Sources

- [Media Player](https://developer.apple.com/documentation/mediaplayer)
- [MPNowPlayingInfoCenter](https://developer.apple.com/documentation/mediaplayer/mpnowplayinginfocenter)
- [MPNowPlayingInfoCenter.nowPlayingInfo](https://developer.apple.com/documentation/mediaplayer/mpnowplayinginfocenter/nowplayinginfo)
- [MPNowPlayingSession](https://developer.apple.com/documentation/mediaplayer/mpnowplayingsession)
- [MPNowPlayingSession.isActive](https://developer.apple.com/documentation/mediaplayer/mpnowplayingsession/isactive)
- [MPNowPlayingSession.automaticallyPublishesNowPlayingInfo](https://developer.apple.com/documentation/mediaplayer/mpnowplayingsession/automaticallypublishesnowplayinginfo)
- [MPRemoteCommandCenter](https://developer.apple.com/documentation/mediaplayer/mpremotecommandcenter)
- [MPRemoteCommand](https://developer.apple.com/documentation/mediaplayer/mpremotecommand)
- [MPRemoteCommand.addTarget(handler:)](https://developer.apple.com/documentation/mediaplayer/mpremotecommand/addtarget%28handler%3A%29)
- [MPRemoteCommandHandlerStatus](https://developer.apple.com/documentation/mediaplayer/mpremotecommandhandlerstatus)
- [MPRemoteCommandEvent](https://developer.apple.com/documentation/mediaplayer/mpremotecommandevent)
- [MPChangePlaybackPositionCommandEvent](https://developer.apple.com/documentation/mediaplayer/mpchangeplaybackpositioncommandevent)
- [Becoming a now playable app](https://developer.apple.com/documentation/mediaplayer/becoming-a-now-playable-app)
- [Handling external player events notifications](https://developer.apple.com/documentation/mediaplayer/handling-external-player-events-notifications)
- [Remote command center events](https://developer.apple.com/documentation/mediaplayer/remote-command-center-events)
- [MPMediaItemArtwork](https://developer.apple.com/documentation/mediaplayer/mpmediaitemartwork)
- [MPMediaItemArtwork.image(at:)](https://developer.apple.com/documentation/mediaplayer/mpmediaitemartwork/image%28at%3A%29)
- [MPNowPlayingInfoPropertyPlaybackProgress](https://developer.apple.com/documentation/mediaplayer/mpnowplayinginfopropertyplaybackprogress)
- [MPNowPlayingInfoPropertyExternalContentIdentifier](https://developer.apple.com/documentation/mediaplayer/mpnowplayinginfopropertyexternalcontentidentifier)
- [MPNowPlayingInfoPropertyAvailableLanguageOptions](https://developer.apple.com/documentation/mediaplayer/mpnowplayinginfopropertyavailablelanguageoptions)
- [MPNowPlayingInfoPropertyAdTimeRanges](https://developer.apple.com/documentation/mediaplayer/mpnowplayinginfopropertyadtimeranges)
- [MPNowPlayingInfoPropertyExcludeFromSuggestions](https://developer.apple.com/documentation/mediaplayer/mpnowplayinginfopropertyexcludefromsuggestions)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Handling audio interruptions](https://developer.apple.com/documentation/avfaudio/handling-audio-interruptions)
- [Responding to audio route changes](https://developer.apple.com/documentation/avfaudio/responding-to-audio-route-changes)
- [AVAudioSession.RouteChangeReason](https://developer.apple.com/documentation/avfaudio/avaudiosession/routechangereason)
- [AVRoutePickerView](https://developer.apple.com/documentation/avkit/avroutepickerview)
- [CarPlay](https://developer.apple.com/documentation/carplay)
- [Watch Connectivity](https://developer.apple.com/documentation/watchconnectivity)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
