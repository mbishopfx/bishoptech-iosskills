# MediaPlayer system-control proof matrix

MediaPlayer crosses app playback, audio-session state, system-owned surfaces, remote command delivery, media-library authorization, personal suggestions, accessibility, and release configuration. Verify each claim at the layer where it is made.

This matrix is for evidence planning. It does not turn a simulator run, a source snippet, or a populated dictionary into proof of physical audio, system rendering, accessory behavior, privacy handling, or release readiness.

## Test record

| Field | Record |
| --- | --- |
| Target | Bundle ID, app/extension targets, target membership, player owner |
| SDK/deployment | Xcode, SDK, iOS/iPadOS target, device OS build |
| Playback | Engine type, item fixture, queue, duration/live state, audio session policy |
| Now Playing | Default center or named MPNowPlayingSession, active state, player membership |
| Commands | Enabled command set, handler owner, event status, cleanup |
| Library | Authorization state, query type, change-notification state, redacted fixture |
| Privacy | Suggestion-exclusion policy, identifiers, retention/deletion behavior |
| Device | Physical iPhone/iPad, output route, headphones/accessory/AirPlay path if claimed |
| System surface | Lock Screen, Control Center, route/accessory surface, background state |
| Accessibility | VoiceOver, Dynamic Type, Voice Control, Switch Control, contrast/transparency |
| AI | Typed context, proposal, validator result, confirmation, fallback |
| Artifact | Signed build, entitlements/plist, privacy manifest, release metadata |

Use synthetic or redacted media for shared evidence. Do not put private library titles, account identifiers, stream URLs, or sensitive recordings in screenshots or logs.

## Claim-to-evidence matrix

| Claim | Minimum evidence | Does not prove it |
| --- | --- | --- |
| App owns a real playback state | Engine callback/state record tied to item ID and timestamp | A SwiftUI slider value |
| Now Playing metadata is projected | Runtime dictionary from canonical state and target configuration | A source dictionary literal |
| App appears on Lock Screen | Physical device actively playing, lock screen observation, item/position evidence | Simulator or Control Center screenshot alone |
| App appears in Control Center | Physical device, active playback, Control Center observation | Metadata dictionary |
| Artwork and title are correct | Redacted fixture, system-surface observation, timestamped state | App-owned artwork card |
| Remote play/pause works | System event, handler status, engine result, state update | Handler registration |
| Seek works | Supported duration/range, event position, engine position result | A seek button tap |
| Unsupported command is hidden/disabled | Capability state and system-surface observation | isEnabled source line |
| App becomes active Now Playing app | Playback start, active-state evidence, subsequent external event | Session object creation |
| Multiple-player session works | Named players, session membership/active transitions, physical result | An array of AVPlayer objects |
| Background playback works | Target configuration, audio-session evidence, locked physical device, progression | Background mode declaration |
| Interruption recovery is truthful | Interruption/route event, state transition, user-visible recovery | A notification handler compile |
| Media-library authorization works | Each status path plus request callback and focused query | Permission key in a plist |
| Library changes reconcile | Change notification, cache invalidation/refresh, updated result | One query result |
| Item is excluded from suggestions | Runtime exclusion metadata and privacy fixture test | A privacy policy statement |
| AI cannot cause an unsafe action | Typed proposal, validator rejection/confirmation, redacted context | Model-generated prose |
| Accessible player is usable | Recorded VoiceOver/Dynamic Type/alternate-input task results | Accessibility labels in source |
| Release is ready | Final signed artifact, target configuration, physical/system evidence, review checks | Debug build or simulator run |

## Now Playing scenarios

- [ ] No item is playing and stale app-owned metadata is cleared.
- [ ] A single audio item starts with title, creator, artwork, duration, position, and rate.
- [ ] A paused item reports a paused state without false progression.
- [ ] A buffering item keeps identity but does not claim active playback.
- [ ] A live item does not expose a misleading finite duration or arbitrary seek.
- [ ] Position updates follow engine timing rather than a UI-only timer.
- [ ] Queue count and index change when the active item changes.
- [ ] End-of-item behavior advances, pauses, or clears according to product policy.
- [ ] Failure or authorization loss removes or marks unavailable metadata.
- [ ] Private or sensitive content receives the intended exclusion metadata.
- [ ] Long localized titles and right-to-left metadata remain legible.
- [ ] Artwork is appropriate for a system surface and has a useful accessibility label.

## System-surface and external-command scenarios

| Scenario | Expected evidence |
| --- | --- |
| Foreground playback | Player state, metadata projection, in-app controls |
| Lock Screen | Current item, state, position, available commands on a physical device |
| Control Center | Same semantic state and command availability on a physical device |
| Headphone/Bluetooth accessory | External event, handler status, actual player result if claimed |
| AirPlay or other route | Route change, metadata/result behavior, no unsupported formatting claim |
| App backgrounded | Audio/session policy, continued state, interruption handling |
| Device locked | Playback and command behavior according to target policy |
| Process restoration | Only if product claims it: restored state, session/engine reattachment, recovery |
| Unsupported command | Disabled/hidden system control and recoverable app explanation |
| Handler teardown | Removed handlers and no duplicate command execution after owner change |

The system can choose presentation and destination behavior. Record what was observed, not what the app intended the system to display.

## MPNowPlayingSession scenarios

- [ ] One owner is documented for the session.
- [ ] Custom players are listed and removed intentionally.
- [ ] canBecomeActive and activation result are recorded.
- [ ] Automatic publication is either enabled intentionally or replaced by one explicit publisher.
- [ ] Session and player changes do not create two writers for the metadata center.
- [ ] The AVPlayerViewController ownership boundary is tested if that controller is used.
- [ ] Changing the active player updates metadata and command availability together.
- [ ] Deactivating or tearing down a session clears ownership and handlers.

## Media-library scenarios

| State or event | Expected evidence |
| --- | --- |
| notDetermined | Explainer and just-in-time request |
| authorized | Focused query and redacted result projection |
| denied | Feature recovery; app-owned playback remains available |
| restricted | Clear system-policy state; no repeated request loop |
| library changed | Notification path and affected-cache refresh/invalidation |
| feature leaves screen | Change notifications stop when no longer needed |
| item disappears | Unknown/deleted decision is tied to current authorization and change state |

Do not use a library query as proof that an item can be played, licensed, or transferred to another route.

## Privacy, AI, and data-boundary checks

- [ ] Private recordings, health-related audio, family content, and drafts have an explicit suggestion policy.
- [ ] Exclusion metadata is applied before publishing the item when policy requires it.
- [ ] Logs redact titles, account IDs, URLs, library identifiers, and raw audio context.
- [ ] Media-library data is not sent to an AI model by default.
- [ ] AI context is typed, minimal, and purpose-bound.
- [ ] AI proposals cannot invent an item ID, queue index, seek range, command, or authorization.
- [ ] Consequential queue or privacy mutations require confirmation when product policy says so.
- [ ] Command acceptance is not reported as engine completion or physical-audio success.
- [ ] Unknown/stale outcomes remain visible rather than being upgraded to success.

## Accessibility and Liquid Glass matrix

- [ ] VoiceOver reads title, creator, state, position, route, and the result of each command.
- [ ] Dynamic Type preserves metadata hierarchy and transport action reachability.
- [ ] Voice Control and Switch Control reach play, pause, next, previous, seek, queue, and recovery.
- [ ] Live streams do not expose a misleading progress value.
- [ ] Reduce Motion preserves state transitions without depending on animation.
- [ ] Reduce Transparency and increased contrast preserve control grouping and error/status meaning.
- [ ] App-owned Liquid Glass controls remain legible over representative artwork and fallback surfaces.
- [ ] System-owned Lock Screen and Control Center are not represented as a fake in-app replica.
- [ ] Keyboard, pointer, localization, long text, RTL, and focus return are tested where supported.

## Evidence vocabulary

| Term | Meaning |
| --- | --- |
| projected | App wrote a metadata representation from canonical state |
| active | MediaPlayer session/center is eligible according to the app’s recorded state |
| displayed | A named physical system surface visibly showed the item |
| command-received | System delivered an external command event |
| accepted | Playback coordinator accepted the typed action |
| engine-started | Player began the requested operation |
| playing | Engine reports truthful progression |
| completed | The intended player/item/range result was observed |
| authorized | Media-library API reported authorized for the test target |
| refreshed | Library change caused an app cache/query update |
| excluded | Item carried the documented suggestion-exclusion metadata |
| unknown | The app could not prove the next physical/domain outcome |

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
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
