# Now Playing, Lock Screen, and media-control design

MediaPlayer design is a collaboration with system surfaces. The app owns playback intent and truth; the system owns Lock Screen, Control Center, AirPlay, and accessory presentation. Good native design keeps the app’s player, metadata, command availability, and privacy choices consistent.

## Start from playback truth

Before designing controls, define:

- current item identity;
- playable/authorized state;
- actual player rate and position;
- duration or live-stream state;
- buffering/interruption;
- queue and next/previous availability;
- current audio route;
- Now Playing eligibility;
- whether content should be excluded from suggestions.

The system surface should be a projection of this state, not a separate playback machine.

## App surface versus system surface

| Surface | Design |
| --- | --- |
| In-app player | Rich context, queue, transcript/chapters, content actions |
| Compact player | Current item, play/pause, progress, route/context action |
| Lock Screen/Control Center | System-owned metadata and enabled remote commands |
| External accessory | System-routed metadata and remote command events |
| Queue editor | App-owned reorder/remove/next behavior |
| AI review | App-owned proposal with explicit apply/cancel |
| Media library browser | Authorization-aware picker/query route |

Do not promise identical layout, artwork crop, or button ordering across system surfaces.

## Metadata hierarchy

Use a consistent hierarchy:

1. title;
2. artist/creator or source;
3. artwork with an accessible label;
4. position/duration or live state;
5. playback state;
6. queue context;
7. content/privacy status when the person needs to understand it.

If a field is unknown, omit it or show uncertainty. Do not insert placeholder metadata that makes a live or private recording look like a catalog track.

## Remote-command availability

System controls should reflect what the current player can do:

| Player state | Enable |
| --- | --- |
| Ready but paused | Play, seek if supported, next/previous if queue supports |
| Playing | Pause, seek, stop if product supports |
| Single item | Hide next/previous |
| Live stream | Do not expose arbitrary seek unless supported |
| No duration | Avoid progress controls that imply a known end |
| No rating/feedback | Disable those commands |
| Item unavailable | Disable playback and show recovery in-app |
| Interruption | Preserve state; do not claim active playback |

When the app disables an MPRemoteCommand, the system can omit that control. This is preferable to showing a button that always fails.

## Native player anatomy

An Apple-like player can use:

- large artwork or a calm artwork placeholder;
- title and creator text with strong Dynamic Type behavior;
- elapsed/remaining labels only when meaningful;
- a semantic progress control;
- primary play/pause control;
- secondary skip/queue/route controls;
- a compact status line for buffering, interrupted, or unavailable;
- a transcript/chapter or notes route below the transport controls.

Use SF Symbols and standard controls first. Avoid a fake Control Center layout or an imitation of Apple’s proprietary system cards.

## Liquid Glass application

Use Liquid Glass for app-owned controls when it improves grouping:

- compact transport group;
- queue and route action group;
- current-item contextual actions;
- bounded AI review.

Keep primary text and progress legible on a stable surface. Do not put metadata, artwork, transcript, queue, and controls into nested translucent panels. One clear material hierarchy is more native than a page of floating glass.

Provide a solid fallback for:

- Reduce Transparency;
- increased contrast;
- large text;
- VoiceOver;
- low-light/high-glare conditions;
- unsupported SDK/device material.

## System-owned surfaces

When the app supplies Now Playing information, the system may render it on the Lock Screen, Control Center, AirPlay destination, or an external accessory. The app should design for consistency rather than duplicate those surfaces.

System proof questions:

- Does the current item appear at the right time?
- Does artwork remain appropriate and privacy-safe?
- Does the elapsed position update without jumping?
- Do commands match what the app can perform?
- Does the app clear stale information after stop/end?
- Does a route change or interruption show a truthful state?

## Media-library permission design

Request media-library access only when the person chooses a feature that needs the library. Explain:

- what the app will read;
- whether it needs songs, playlists, or other entities;
- how selection improves the current feature;
- what happens when access is denied or restricted.

Keep app-owned playback available when it does not require library access. A denied media-library permission should not make the entire player look broken.

## Journaling and suggestion privacy

Now Playing information can contribute to Journaling Suggestions unless the app opts out for an item. Make the product decision visible in privacy documentation and, where useful, in a media item’s privacy settings:

- public catalog item and private recording may need different defaults;
- health, therapy, family, or location-linked media may deserve exclusion;
- user-authored audio may need an explicit “include in personal suggestions” choice;
- external content identifiers should not leak account or private URL structure.

Do not show a medical or emotional inference merely because a system suggestion can include media.

## AI-assisted playback

An AI feature should appear as a proposal:

person request -> current player/queue context -> typed action -> review -> playback coordinator -> actual player result

Examples:

- “Start the next chapter” becomes a validated chapter jump.
- “Keep this private” becomes an explicit exclusion metadata update.
- “Make a 20-minute focus queue” becomes a reviewable queue proposal, not an immediate mutation.

The model must not bypass remote-command availability, authorization, account/licensing rules, or confirmation.

## Accessibility

Test:

- VoiceOver reads current item, state, position, route, and action result;
- Dynamic Type keeps title, controls, and queue actions visible;
- Voice Control identifies play, pause, next, previous, and seek controls;
- Switch Control reaches the same actions;
- progress has an accessible value and does not rely on visual animation;
- live streams do not expose misleading elapsed/duration values;
- artwork has useful alternate text or is decorative;
- reduced motion preserves playback state changes;
- high contrast and reduced transparency preserve hierarchy;
- localized long titles, creator names, and right-to-left layouts work.

## Design proof

Review the app and system surfaces together:

- app foreground player;
- background playback;
- Lock Screen;
- Control Center;
- external accessory or route where supported;
- interruptions and route changes;
- library denied/restricted/authorized;
- private item excluded from suggestions;
- queue and multi-player transitions;
- AI proposal accepted/rejected;
- accessibility task results.

## Sources

- [Media Player](https://developer.apple.com/documentation/mediaplayer)
- [MPNowPlayingInfoCenter](https://developer.apple.com/documentation/mediaplayer/mpnowplayinginfocenter)
- [MPNowPlayingSession](https://developer.apple.com/documentation/mediaplayer/mpnowplayingsession)
- [MPRemoteCommandCenter](https://developer.apple.com/documentation/mediaplayer/mpremotecommandcenter)
- [MPRemoteCommand](https://developer.apple.com/documentation/mediaplayer/mpremotecommand)
- [Becoming a now playable app](https://developer.apple.com/documentation/mediaplayer/becoming-a-now-playable-app)
- [Handling external player events notifications](https://developer.apple.com/documentation/mediaplayer/handling-external-player-events-notifications)
- [MPMediaLibrary](https://developer.apple.com/documentation/mediaplayer/mpmedialibrary)
- [MPMediaLibraryAuthorizationStatus](https://developer.apple.com/documentation/mediaplayer/mpmedialibraryauthorizationstatus)
- [Exclude Now Playing items from suggestions](https://developer.apple.com/documentation/mediaplayer/mpnowplayinginfopropertyexcludefromsuggestions)
- [AVFoundation](https://developer.apple.com/documentation/avfoundation)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
