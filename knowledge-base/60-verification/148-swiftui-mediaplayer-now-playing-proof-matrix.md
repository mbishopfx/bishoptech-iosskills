# SwiftUI MediaPlayer Now Playing and remote-command proof matrix

MediaPlayer evidence crosses the app-owned player, AVAudioSession, system metadata, remote command delivery, artwork, route changes, privacy/suggestion policy, and external surfaces. This matrix keeps those claims separate.

The baseline [MediaPlayer system-control proof matrix](45-mediaplayer-system-control-proof-matrix.md) remains useful. This page adds focused evidence for a SwiftUI iOS 26 target, one projection owner, command reconciliation, route/privacy behavior, and AI proposal boundaries.

## 1. Test record

| Field | Record |
| --- | --- |
| Target | Bundle ID, target, extensions, CarPlay/Watch membership |
| SDK | Xcode and final iOS 26 SDK |
| Player | AVPlayer/custom engine/controller-owned player |
| Now Playing owner | Default center or named MPNowPlayingSession |
| Publication | Explicit dictionary or automatic session publication |
| Audio session | Category, mode, options, background configuration |
| Item | Redacted item ID, title policy, content category |
| Queue | Revision, count, current index |
| Commands | Enabled/disabled commands and handler ownership |
| Artwork | Revision, source, bounds/cache policy |
| Route | Device/output route and route-change history |
| System surface | Lock Screen, Control Center, AirPlay, CarPlay, Watch/accessory |
| Library | Authorization state and query scope, if applicable |
| Suggestions | Exclusion policy and fixture |
| AI | Model availability, typed proposal, review result |
| Build evidence | Signed archive, device model/OS, TestFlight build |
| Privacy | Metadata disclosure, logs, analytics, model input |

Redact private titles, user identifiers, account data, artwork, library IDs, and raw command payloads in shared evidence.

## 2. Claim-to-evidence matrix

| Claim | Minimum evidence | Does not prove it |
| --- | --- | --- |
| MediaPlayer is the correct route | App owns playback and needs system metadata/controls | A custom player UI alone |
| Metadata is configured | Canonical PlaybackState maps to a runtime dictionary | A source dictionary literal |
| One projection owner exists | Target architecture and runtime writer audit | A page that imports MediaPlayer |
| Active Now Playing app | Real playback begins and subsequent system event reaches app | Session object creation |
| Lock Screen shows item | Physical locked device with actual playback | Preview/simulator |
| Control Center shows item | Physical device and current Now Playing state | Metadata assignment |
| Remote play/pause works | Physical command, handler status, player observation, republished state | Handler registration |
| Seek works | Position event, player result, elapsed-time projection | Slider animation |
| Unsupported command hidden | Command disabled and system UI observation | A disabled in-app button |
| Artwork renders | Physical/system/accessory sizes and privacy fixture | Artwork object creation |
| Queue navigation works | Next/previous command, revision validation, player item change | Queue array exists |
| Session active | isActive/canBecomeActive transition and system event | MPNowPlayingSession initializer |
| Automatic publication works | Final SDK behavior with one publication mode | Setting the Boolean |
| Audio is audible | Physical route/device and observed player/audio evidence | Metadata or command success |
| Headphone disconnect is private | Physical disconnect pauses and state updates | Route notification received |
| AirPlay works | Physical receiver selection and output behavior | Route picker displayed |
| Library access works | Authorization state and current query on a physical account | App-owned playback |
| Content is excluded from suggestions | Exclusion metadata and privacy/content fixture | A copy statement |
| AI is bounded | Typed proposal, validation, review, no direct side effect | Fluent model output |
| Release is ready | Signed artifact, privacy/background metadata, physical/system/accessory test | Debug build |

## 3. Ownership and publication tests

- [ ] The app identifies one PlaybackCoordinator.
- [ ] The app has one metadata writer per active Now Playing owner.
- [ ] A view re-render does not create a second command handler.
- [ ] Scene phase changes do not duplicate handlers or clear an active session.
- [ ] Item changes invalidate late artwork and metadata callbacks.
- [ ] Queue changes invalidate stale proposals.
- [ ] Session replacement removes old handlers.
- [ ] Automatic publication and explicit nowPlayingInfo are never mixed on the same session.
- [ ] AVPlayerViewController-owned players do not receive a custom MPNowPlayingSession.
- [ ] Stopped/ended/failed state clears or intentionally replaces system metadata.

## 4. Playback-state fixtures

| Fixture | Expected result |
| --- | --- |
| Item selected, not prepared | No active playing claim |
| Player ready and paused | Item metadata, paused state, play enabled |
| Player starts | Observed rate/position and metadata update |
| Buffering | Item retained, progression does not advance falsely |
| Finite item ends | Next item or clear follows queue policy |
| Live item | Live label, no unsupported finite duration/seek |
| Authorization failure | Recovery state, no stale actionable controls |
| Player error | Failure state and no false progress |
| Queue revision changes | Index/count and commands recompute |
| Item changes during artwork load | Old artwork discarded |
| App leaves foreground | Player/session state remains coherent |
| Process restoration | State rehydrates without publishing stale item |

## 5. Remote-command fixtures

- [ ] playCommand starts the current item only when content is available.
- [ ] pauseCommand returns a failure status when there is no actionable item.
- [ ] togglePlayPauseCommand maps to the same domain action as the SwiftUI button.
- [ ] nextTrackCommand validates the current queue revision.
- [ ] previousTrackCommand handles the product’s previous-track policy.
- [ ] changePlaybackPositionCommand rejects invalid/live positions.
- [ ] changePlaybackRateCommand clamps or rejects unsupported rates.
- [ ] skip commands honor current time and content policy.
- [ ] repeat/shuffle commands update queue state before metadata.
- [ ] rating/like/dislike/bookmark commands use the correct account policy.
- [ ] language option commands only appear for available options.
- [ ] each handler token is removed when the owner is destroyed.
- [ ] duplicate handler registration is detected in tests.
- [ ] asynchronous server work never returns success before local playback proof.

For each command, record:

| Evidence | Record |
| --- | --- |
| Source | Lock Screen, Control Center, accessory, CarPlay, Watch, or app |
| Event | Command subtype and item/queue generation |
| Validation | Item, entitlement, queue, route, and content checks |
| Handler result | success/noSuchContent/noActionableNowPlayingItem/deviceNotFound/commandFailed |
| Player result | Actual state transition |
| Projection | Updated position/rate/item/metadata |
| UI | Accessibility and recovery state |

## 6. Audio-session and route fixtures

| Scenario | Expected result |
| --- | --- |
| Playback begins | Audio session activates at the product boundary |
| Phone call/Siri/system alert | Interruption state and player response are visible |
| Interruption ends | Resume follows player/audio policy, not a blind timer |
| Headphones connect | Current route reconciles; private playback continues as appropriate |
| Headphones disconnect | Playback pauses to avoid unexpected speaker output |
| Bluetooth route changes | Current route and system metadata remain coherent |
| AirPlay receiver changes | Route state is separate from audible-output proof |
| No suitable route | App stops claiming audible playback |
| Media services reset | Player/audio graph rebuilds before active projection |
| Background/lock | Playback and metadata remain coherent |
| Route changes during seek | Stale seek result is ignored or reconciled |

Collect physical-device evidence for any claim about privacy, audible output, route selection, or background playback.

## 7. Artwork and metadata tests

- [ ] Title/creator are localized and Dynamic Type-safe.
- [ ] Artwork uses the current item and artwork revision.
- [ ] Artwork request handler returns an image at requested sizes.
- [ ] Artwork loading does not block playback commands.
- [ ] Late artwork response cannot replace a newer item.
- [ ] Missing artwork has a readable fallback.
- [ ] Private/sensitive content has a privacy-safe artwork policy.
- [ ] Live content omits unsupported duration/seek fields.
- [ ] Elapsed time follows observed player position.
- [ ] Playback rate follows actual player rate.
- [ ] Queue index/count match the current queue revision.
- [ ] External content identifier is opaque and stable without leaking account data.
- [ ] Stopped/cleared state removes stale metadata.

Test square, tall, small accessory, tinted, dark, light, high-contrast, and reduced-transparency presentations.

## 8. Media-library tests

- [ ] The app explains why library access is needed.
- [ ] notDetermined prompts only at the library feature boundary.
- [ ] denied/restricted states preserve app-owned playback.
- [ ] authorized query is scoped to the feature.
- [ ] library change notifications start and end intentionally.
- [ ] deleted/changed media invalidates app cache.
- [ ] account/library changes do not silently select a different item.
- [ ] raw library metadata is excluded from diagnostics and AI prompts by default.

Do not use media-library permission as evidence that app-owned Now Playing metadata works.

## 9. System-surface and companion tests

### Lock Screen and Control Center

- [ ] Current item appears after actual playback begins.
- [ ] Title, creator, artwork, progress, and state are truthful.
- [ ] Commands match enabled capabilities.
- [ ] Item changes update without stale previous metadata.
- [ ] Stop/end clears or replaces the projection.

### AirPlay

- [ ] Route picker is present only when the route is intended.
- [ ] Destination selection is explicit.
- [ ] Current route updates after selection/disconnect.
- [ ] Metadata and output behavior are tested separately.
- [ ] Receiver failure does not claim audible playback.

### CarPlay/Watch/accessory

- [ ] Companion command maps to shared PlaybackCommand.
- [ ] Queue/item revision is revalidated.
- [ ] Driver-attention/system limits are respected.
- [ ] Connectivity loss has a recovery state.
- [ ] The companion surface does not become a second playback authority.

## 10. Suggestion and privacy fixtures

| Content fixture | Expected result |
| --- | --- |
| Public catalog audio | Product policy decides allow/exclude |
| Private voice note | Excluded by default unless explicitly reviewed |
| Health/therapy/legal recording | Excluded and redacted from shared evidence |
| Account-restricted stream | External ID and metadata reviewed |
| User-created recording | Person-controlled preference if offered |
| AI summary of private item | On-device/redacted route or explicit block |
| Screenshot/support export | Private title/artwork/identity masked |

Verify that:

- [ ] MPNowPlayingInfoPropertyExcludeFromSuggestions matches policy.
- [ ] app privacy copy describes system-facing metadata.
- [ ] external identifiers do not contain raw URLs/tokens.
- [ ] logs exclude full item titles when sensitive.
- [ ] model input excludes unnecessary library/account metadata.
- [ ] analytics do not record remote command payloads by default.

## 11. AI evaluation matrix

| Fixture | Expected result |
| --- | --- |
| Current queue, valid items | Proposal lists eligible IDs and current revision |
| Queue changed after proposal | Proposal is stale and cannot apply |
| Missing chapter data | Model states missing data |
| Private recording | Model route respects exclusion policy |
| Item not authorized | Deterministic validator rejects |
| Live stream seek request | Proposal is rejected or narrowed to supported action |
| Remote command pending | Model never claims success |
| Model unavailable | Player and system controls remain usable |
| Natural-language mutation | Requires typed output and user review |
| External model boundary | Input audit blocks unapproved raw metadata |

The model can explain or rank. The PlaybackCoordinator decides and performs.

## 12. SwiftUI and accessibility tests

- [ ] Native Button, Slider, Menu, and Toggle semantics are present.
- [ ] VoiceOver reads title, creator, state, position, route, and command.
- [ ] Dynamic Type keeps title and transport controls usable.
- [ ] Reduce Motion does not hide a state transition.
- [ ] Reduce Transparency and increased contrast have a solid fallback.
- [ ] Voice Control can play, pause, seek, skip, show queue, and choose route.
- [ ] Switch Control reaches the same actions.
- [ ] Keyboard/pointer/controller routes work on supported targets.
- [ ] Artwork is not the only identifier.
- [ ] Buffering/interruption/route changes are announced.
- [ ] AI explanation is labeled and dismissible.

## 13. Physical-device and release gates

### Physical gate

- [ ] Final SDK target compiles.
- [ ] Signed target has background audio/configuration required by the product.
- [ ] Device plays actual content.
- [ ] Lock Screen and Control Center show the current item.
- [ ] Headphone disconnect pauses private playback.
- [ ] AirPlay/CarPlay/Watch/accessory route works if claimed.
- [ ] Interruption and media-services reset recover.
- [ ] Remote commands mutate actual player state.
- [ ] Artwork and privacy fixtures pass.

### Release gate

- [ ] Signed archive has intended target membership and capabilities.
- [ ] Privacy/App Store metadata matches library, audio, and AI behavior.
- [ ] Content suggestion policy is documented.
- [ ] No stale debug-only metadata or logging remains.
- [ ] TestFlight build reproduces physical system behavior.
- [ ] App Review copy does not claim Apple system-surface ownership or guaranteed route output.

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
