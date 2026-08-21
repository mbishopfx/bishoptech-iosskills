# SwiftUI MediaPlayer Now Playing and remote-command route

Use this route when an app owns audio or video playback and needs truthful participation in Apple’s Now Playing, Lock Screen, Control Center, AirPlay, CarPlay, Watch, or external-accessory controls. It complements the broad [MediaPlayer Now Playing route](51-mediaplayer-now-playing-and-remote-command-route.md), the [AVFAudio route-aware playback route](140-swiftui-avfaudio-airplay-route-aware-playback-review-route.md), and the [Now Playing design review](../21-design-deep-dives/151-swiftui-mediaplayer-now-playing-review-design.md).

The route ends at the first missing prerequisite. A metadata fixture can prove a projection reducer; it cannot prove audible playback, external command delivery, route behavior, or accessory compatibility.

## 1. Write the outcome contract

Write:

> A person wants to [play/pause/seek/browse/route] [content] from [surface] while [privacy/account/route constraint].

Choose one primary lane:

| Outcome | Minimum route |
| --- | --- |
| App-owned player with system metadata | AVFoundation player, AVAudioSession, MediaPlayer |
| One custom player | Default MPNowPlayingInfoCenter and shared MPRemoteCommandCenter |
| Multiple custom players | MPNowPlayingSession and session-owned controls |
| AVPlayerViewController playback | Controller-owned player and Now Playing behavior |
| Media library browsing | MPMediaLibrary authorization and focused query |
| AirPlay route selection | AVAudioSession and AVRoutePickerView |
| CarPlay transport | CarPlay templates backed by shared playback coordinator |
| Watch transport | Watch Connectivity/handoff backed by shared playback coordinator |
| On-device AI queue or chapter proposal | Typed proposal, validation, explicit review |

Do not request MPMediaLibrary permission merely to publish app-owned Now Playing metadata.

## 2. Preflight worksheet

Record:

| Field | Decision |
| --- | --- |
| Target/SDK | Named iOS 26/iPadOS 26 target and final SDK |
| Player | AVPlayer, custom engine, or controller-owned player |
| Now Playing owner | Default center or one MPNowPlayingSession |
| Publication mode | Explicit dictionary or automatic session publication |
| Audio category | Playback category/mode/options and background policy |
| Commands | Supported commands for current item/queue |
| Artwork | Source, size-aware cache, privacy policy |
| Queue | Identity, revision, next/previous capability |
| System surfaces | Lock Screen, Control Center, AirPlay, CarPlay, Watch, accessory |
| Media library | Not required, pending, denied, or authorized |
| Suggestions | Content-category exclusion policy |
| AI | Off, explanation-only, or reviewed typed proposal |
| Privacy | Metadata disclosure, logs, analytics, model input |
| Physical proof | Device, headphones, AirPlay, CarPlay/accessory, background/lock |

The presence of an import or a nowPlayingInfo dictionary is not release feature proof.

## 3. Select one owner graph

~~~text
SwiftUI / CarPlay / Watch / remote command
  -> PlaybackCommand
  -> PlaybackCoordinator
      -> PlayerEngine
      -> AVAudioSession
      -> QueueStore
      -> NowPlayingProjector
      -> ArtworkStore
      -> ContentPolicy
  -> PlaybackState
~~~

| Layer | Owns | Does not own |
| --- | --- | --- |
| SwiftUI | App-owned layout and user intent | System presentation or audio truth |
| PlaybackCoordinator | Command validation and lifecycle | Raw view identity |
| PlayerEngine | Player operations and observations | System metadata formatting |
| AVAudioSession | Audio category, route, interruption, activation | Queue/entitlement rules |
| NowPlayingProjector | Metadata dictionary and command registration | Audible output |
| ArtworkStore | Bounded image loading/cache | Item authorization |
| QueueStore | Current queue/revision | Remote command success |
| ContentPolicy | Suggestions/privacy/redaction | System display decisions |
| AI proposal | Explanation or candidate action | Direct player/MediaPlayer mutation |

## 4. Route A: default center

Use the default route for one custom playback owner:

1. Configure AVAudioSession without activating prematurely.
2. Create or prepare the player.
3. Start playback after explicit user intent.
4. Read the player’s observed item, time, rate, and status.
5. Project known values to MPNowPlayingInfoCenter.default().
6. Register only supported commands in MPRemoteCommandCenter.shared().
7. Remove handlers when the playback coordinator is actually torn down.
8. Clear the dictionary when the app no longer owns an actionable item.

The app becomes eligible for external commands after it begins playing and is the Now Playing app. A registered handler in a preview or paused setup is not external-control proof.

## 5. Route B: MPNowPlayingSession

Use MPNowPlayingSession when multiple custom AVPlayer objects need coordinated system control:

1. Construct the session from the custom player list.
2. Add/remove players as the active group changes.
3. Decide whether the session can become active.
4. Call becomeActiveIfPossible when product policy permits.
5. Choose automatic publication or explicit session metadata.
6. Register handlers on the session’s remote command center.
7. Observe isActive and session delegate changes.
8. Clear or transfer the projection when the session becomes inactive.

Do not use a custom session with the AVPlayer presented by AVPlayerViewController. If the controller owns the player, it owns the associated Now Playing route.

## 6. Route C: command registration

For every remote command:

1. decide whether the current item/queue supports it;
2. set the command enabled state;
3. register one handler and retain its opaque token;
4. translate the event into a typed PlaybackCommand;
5. validate current item, queue revision, entitlement, and route;
6. execute against the player;
7. return success only when the local action is accepted;
8. publish observed playback state;
9. remove the handler token when the owner changes.

| Command | Validate |
| --- | --- |
| play/pause/toggle | Current item exists and player can change state |
| next/previous | Queue revision and playable neighbor |
| seek/position | Duration/live policy and permitted range |
| rate | Supported rate and current item |
| skip | Item policy and current time |
| repeat/shuffle | Queue mode ownership |
| rating/like/dislike/bookmark | Account/content policy and user intent |
| language option | Available language option group |

Return a handler status that matches the local result. Do not return success because a network request merely started.

## 7. Route D: metadata projection

Maintain one projection function:

~~~text
PlaybackState revision
  -> title/creator/artwork
  -> duration/elapsed/rate/live
  -> queue index/count
  -> external content identifier
  -> suggestion exclusion
  -> nowPlayingInfo
~~~

Projection rules:

- use actual player rate;
- use actual observed position;
- omit duration for unsupported live content;
- update queue index/count only with the current queue revision;
- include artwork only after a privacy/cache decision;
- use stable opaque external identifiers;
- clear stale fields when the item changes;
- set nil when the app has no actionable item.

Do not mutate the projection from multiple callbacks without generation checks. A delayed artwork response must not replace the current item’s artwork.

## 8. Route E: artwork

Use MPMediaItemArtwork with a size-aware request handler:

1. resolve the item/artwork revision;
2. check the bounded cache;
3. decode/render at the requested bounds;
4. return a privacy-approved image;
5. update the projection if the item revision is still current;
6. discard late results from prior item generations.

Test square and tall system surfaces, small accessories, dark/tinted/high-contrast display, missing artwork, private recordings, decode failure, item changes during loading, memory pressure, and cache eviction.

Artwork readiness must never be required for play/pause command success.

## 9. Route F: AVAudioSession

Configure the audio session at the playback feature boundary, then activate when playback begins. Observe:

- interruption notification;
- route change notification;
- media services reset;
- current route and output ports;
- player time-control/rate/status.

| Event | Required response |
| --- | --- |
| New device available | Reconcile current output route |
| Old device unavailable | Pause private playback and update state |
| Category change | Re-evaluate player/route policy |
| No suitable route | Stop claiming audible playback |
| Interruption begins | Preserve item/position and stop progression |
| Interruption ends | Resume only if policy/player state permits |
| Media services reset | Rebuild audio/player state before reprojecting |

Do not resume through the built-in speaker after a private headphone disconnect without explicit product policy and user intent.

## 10. Route G: queue and chapters

Keep queue actions deterministic:

~~~text
current item + queue revision
  -> next/previous eligibility
  -> user or system command
  -> playable neighbor validation
  -> player item change
  -> observed state
  -> metadata index/count update
~~~

An AI proposal can select among eligible app-owned items or chapters. It cannot create an item, bypass content authorization, or apply after the queue revision changes.

When a queue update arrives, mark proposals stale, preserve the current item only if its identity remains valid, recompute next/previous, update system metadata, and disable controls without a valid target.

## 11. Route H: media library boundary

Use MPMediaLibrary only for library access:

1. explain why library access is needed;
2. request authorization at the feature boundary;
3. handle notDetermined, denied, restricted, and authorized states;
4. query only the needed media entities;
5. observe changes only while needed;
6. invalidate cached IDs when authorization/account state changes;
7. keep library metadata out of logs and model prompts by default.

App-owned playback, Now Playing publication, and remote commands should retain a useful path when library permission is denied.

## 12. Route I: system suggestion policy

For each item category, decide whether to set MPNowPlayingInfoPropertyExcludeFromSuggestions:

| Category | Example policy |
| --- | --- |
| Public catalog | Allow when beneficial and disclosed |
| Private voice note | Exclude |
| Health/therapy/legal recording | Exclude unless explicitly reviewed |
| Account-restricted content | Review identifier and metadata exposure |
| User-created content | Provide a person-controlled preference |

This metadata expresses the app’s choice. It is not a guarantee about another system surface’s final behavior.

## 13. Route J: SwiftUI and Liquid Glass

The app-owned player should contain native Button for play/pause, semantic Slider for finite progress, Menu or sheet for queue/route, compact buffering/interruption status, high-contrast recovery, and an optional AI disclosure.

Use Liquid Glass for grouped transport and secondary actions. Keep artwork and text on a readable content surface. Do not recreate Lock Screen/Control Center or place system ownership in app copy.

Tie task lifecycles to item, queue, and session identity:

- a new item cancels old artwork/task generation;
- a new queue revision invalidates stale proposals;
- a new session replaces old command handlers;
- scene phase refreshes the projection without duplicating handlers.

## 14. Route K: optional on-device AI

The AI input may contain current item identity/title, permitted transcript/chapter facts, queue revision, candidate item IDs, player capability, missing data, and privacy/content policy.

Use a typed proposal:

~~~text
PlaybackProposal
  proposalID
  sourceQueueRevision
  action
  affectedItemIDs
  reason
  missingData
  requiresUserReview
~~~

The deterministic coordinator revalidates before applying. The model never registers handlers, updates nowPlayingInfo, calls the player, or claims audible output.

## 15. Verification route

Run in order:

1. Unit-test PlaybackState and projection mapping.
2. Test command enablement and handler status.
3. Test stale artwork, queue, and session generations.
4. Test interruption and route reducers.
5. Test SwiftUI Dynamic Type, accessibility, and Liquid Glass fallback.
6. Compile the named iOS 26 target with final SDK.
7. Run on a physical device with headphones and Lock Screen.
8. Run Control Center, AirPlay, CarPlay, Watch, and claimed accessory routes.
9. Inspect the signed archive, background audio, and privacy metadata.
10. Recheck TestFlight and release behavior.

## 16. Stop conditions

Stop and request a product decision when:

- the product cannot identify the single playback owner;
- metadata contains private values without a suggestion/privacy decision;
- a remote command needs a server side effect with no local fulfillment contract;
- the queue or item revision is stale;
- AVPlayerViewController owns the player but a custom session is also proposed;
- a physical accessory or CarPlay entitlement is required but unavailable;
- the app claims audible output from metadata or a command callback.

## Sources

- [Media Player](https://developer.apple.com/documentation/mediaplayer)
- [MPNowPlayingInfoCenter](https://developer.apple.com/documentation/mediaplayer/mpnowplayinginfocenter)
- [MPNowPlayingSession](https://developer.apple.com/documentation/mediaplayer/mpnowplayingsession)
- [MPRemoteCommandCenter](https://developer.apple.com/documentation/mediaplayer/mpremotecommandcenter)
- [MPRemoteCommand](https://developer.apple.com/documentation/mediaplayer/mpremotecommand)
- [MPRemoteCommandHandlerStatus](https://developer.apple.com/documentation/mediaplayer/mpremotecommandhandlerstatus)
- [MPChangePlaybackPositionCommandEvent](https://developer.apple.com/documentation/mediaplayer/mpchangeplaybackpositioncommandevent)
- [Becoming a now playable app](https://developer.apple.com/documentation/mediaplayer/becoming-a-now-playable-app)
- [Handling external player events notifications](https://developer.apple.com/documentation/mediaplayer/handling-external-player-events-notifications)
- [MPMediaItemArtwork](https://developer.apple.com/documentation/mediaplayer/mpmediaitemartwork)
- [MPMediaLibrary](https://developer.apple.com/documentation/mediaplayer/mpmedialibrary)
- [MPMediaLibraryAuthorizationStatus](https://developer.apple.com/documentation/mediaplayer/mpmedialibraryauthorizationstatus)
- [MPNowPlayingInfoPropertyExcludeFromSuggestions](https://developer.apple.com/documentation/mediaplayer/mpnowplayinginfopropertyexcludefromsuggestions)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Handling audio interruptions](https://developer.apple.com/documentation/avfaudio/handling-audio-interruptions)
- [Responding to audio route changes](https://developer.apple.com/documentation/avfaudio/responding-to-audio-route-changes)
- [AVRoutePickerView](https://developer.apple.com/documentation/avkit/avroutepickerview)
- [CarPlay](https://developer.apple.com/documentation/carplay)
- [Watch Connectivity](https://developer.apple.com/documentation/watchconnectivity)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
