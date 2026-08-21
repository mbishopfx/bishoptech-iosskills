# SwiftUI AVFAudio, AirPlay, and route-aware playback review proof matrix

This matrix defines what evidence can establish for the [audio-session and route-aware playback review](../42-framework-deep-dives/109-swiftui-avfaudio-airplay-route-aware-playback-review.md). Use the [route card](../50-capability-recipes/140-swiftui-avfaudio-airplay-route-aware-playback-review-route.md), [design guide](../21-design-deep-dives/137-swiftui-avfaudio-airplay-route-aware-playback-review-design.md), and [recipes](../70-code-recipes/152-swiftui-avfaudio-airplay-route-aware-playback-review-recipes.md) together.

The proof rule is:

documented session behavior -> target/configuration proof -> deterministic state tests -> simulator/preview -> physical route -> system surfaces -> archive/TestFlight/release

## Evidence levels

| Level | Evidence | Supports | Does not support |
| --- | --- | --- | --- |
| L0 | Official Apple source review | Category, mode, route, system-surface, HIG, Speech, and model boundaries | A functioning target |
| L1 | Project and processed plist inspection | Framework imports, privacy strings, background mode, target membership, policy intent | Physical route or account behavior |
| L2 | Reducer, command, and fixture tests | Route/interruption state, revision, idempotency, AI fallback, metadata projection | Audible sound, microphone quality, receiver acceptance |
| L3 | SwiftUI preview and Simulator | Controls, labels, mock route states, metadata, transcript, fallback | AirPlay, real interruption, hardware, spatial perception |
| L4 | Signed physical iPhone or iPad | Permission, player/engine, route, recording, interruption, system controls | All accessory and receiver combinations |
| L5 | Named hardware matrix | Headphones, Bluetooth, USB, AirPlay, CarPlay, Watch, multiroute, spatial | Universal compatibility or listener experience |
| L6 | Archive/TestFlight | Bundle graph, entitlements, privacy resources, version/build, installation | Audio quality, route stability, App Review |
| L7 | Production observation | Real device/route logs and support evidence | Future OS, device, receiver, or user perception |

## Claim-to-evidence matrix

| Claim | Minimum evidence | Strong evidence |
| --- | --- | --- |
| Category and mode match the product | Source review and route record | Project review plus physical scenario |
| Audio session activates | Compile and unit fixture | Signed physical device with result/error log |
| Player plays | Player fixture | Physical speaker/headphone run with actual time progression |
| Recording captures | Input fixture | Physical microphone recording, file reopen, and source identity |
| Route changes are handled | Reducer test | Headphone/Bluetooth/USB/AirPlay route matrix |
| Headphone removal is private | Policy source review | Physical disconnect with expected pause/fallback |
| Interruption handling is correct | Begin/end fixture | Call, Siri, alarm, navigation prompt, and resume run |
| Media services reset recovers | Reset reducer | Developer reset on physical device with user-initiated recovery |
| AirPlay picker works | AVRoutePickerView bridge test | Named receiver selection, cancel, disconnect, and playback |
| Long-form AirPlay is configured | Source and session inspection | AirPlay 2 receiver run with recorded route/player state |
| Multiroute works | Port mapping fixture | USB plus headphones or intended physical graph, including loss |
| Spatial mode is supported | Format and capability fixture | Named device/route playback and fallback |
| Now Playing is accurate | Metadata fixture | Lock Screen, Control Center, CarPlay, Watch, and receiver run |
| Remote commands are safe | Command reducer test | External control run with actual player/queue revision |
| CarPlay playback works | CarPlay target/source inspection | Locked iPhone and physical head unit |
| Watch command commits | Revisioned command fixture | Paired Watch command and physical player revision |
| Speech assets are ready | Asset state fixture | Named device/locale install and real audio analysis |
| Transcript is final | Analyzer finish fixture | Source-linked physical recording and final output |
| AI summary is reviewed | Candidate validator | User acceptance/rejection with source revision |
| Model fallback works | Unavailable fixture | Device/region/model-not-ready run |
| Liquid Glass is accessible | Preview settings | Physical contrast, motion, Dynamic Type, VoiceOver |
| Metadata privacy is correct | Policy fixture | Lock Screen, receiver, CarPlay, Watch, delete/sign-out |
| Release includes the route | Build inspection | Archive, TestFlight install, signed entitlement inspection |

## Session and route matrix

| Scenario | Expected observation | Evidence |
| --- | --- | --- |
| Category set | Readable category/mode/options | Project and runtime snapshot |
| Activation before play | No premature interruption | Unit or physical test |
| Activation error | User sees unavailable state | Error fixture and device |
| Current route local | Player/engine format matches | Physical route record |
| AirPlay selected | Picker, route, and renderer states converge | Receiver run |
| AirPlay canceled | Local route remains usable | Physical cancellation |
| Headphones inserted | Private route behavior is preserved | Physical run |
| Headphones removed | Policy handles output loss | Physical run |
| Bluetooth profile changes | Input/output state updates | Physical headset run |
| USB route appears | Hardware format and route update | Physical interface run |
| MultiRoute port loss | Affected stream stops/reassigns safely | Physical graph run |
| CarPlay route | CarPlay owns system UI | Head-unit run |
| Watch route | Command result is revisioned | Paired device run |
| Route is unavailable | Fallback is explicit | State fixture and device |

## Interruption and reset matrix

| Event | Required state transition | Failure proof |
| --- | --- | --- |
| Interruption began | Player/engine pauses or stops according to policy | Audio continues incorrectly |
| Interruption ended with resume option | Resume only when user/system policy permits | Unexpected autoplay |
| Interruption ended without resume | Remain paused and preserve position | Lost queue or position |
| Route disconnect interruption | Apply documented route policy | Private audio leaks to speaker |
| Media services reset | Recreate audio objects and configuration | Stale engine/player remains |
| Media services lost | Mark unavailable and recover later | Crash or phantom playing |
| App background | Follow background mode and active session policy | Work continues without entitlement |
| App termination | Restore durable source/queue state | Lost recording or false Now Playing |

## Now Playing and command matrix

| Test | Expected result |
| --- | --- |
| Metadata update while playing | Title, artwork, duration, rate, elapsed time reflect actual player |
| Pause | Player pauses before command reports success |
| Play | Player starts or returns a failure |
| Skip | Queue revision changes only after item transition |
| Seek | Current time changes within supported bounds |
| Unsupported command | Command disabled or returns failure |
| Queue end | Now Playing state and commands update |
| Player stops | Stale metadata is cleared or marked according to policy |
| Multiple players | Active MPNowPlayingSession is explicit |
| AVPlayerViewController | No conflicting custom Now Playing owner |
| AirPlay receiver | Receiver display is observed separately |
| CarPlay/Watch | System surface mirrors committed state, not intent |

## Speech and AI matrix

| Case | Expected result |
| --- | --- |
| Unsupported locale | Manual or alternate locale route |
| Assets downloading | Clear pending state; no fake transcript |
| Assets unavailable | Fallback and retry |
| Partial transcript | Mark provisional and source-linked |
| Analyzer canceled | Result stream finishes or cancels cleanly |
| Final transcript | Source revision and locale recorded |
| Model unavailable | Deterministic summary/tag/manual route |
| Context too large | Chunk or defer; no silent truncation |
| Unsupported capability | Use a supported schema/task |
| Stale source | Reject candidate and regenerate |
| User rejects | Original audio/transcript remains |
| User accepts | New domain revision is recorded |
| Privacy deletion | Audio, transcript, candidate, and metadata follow retention policy |

## Accessibility and privacy matrix

| Review | Required observation |
| --- | --- |
| VoiceOver | Route, playback, recording, transcript, and AI state are spoken |
| Voice Control | System route picker and custom actions have clear labels |
| Dynamic Type | Player and transcript remain usable |
| Reduce Motion | Route/interruption transitions remain clear |
| Reduce Transparency | Critical text and controls retain contrast |
| Captions/transcript | Important speech does not require hearing |
| Output muted | Visible/textual state explains silence |
| Lock Screen | Metadata policy is intentional |
| AirPlay receiver | Sensitive metadata is minimized |
| CarPlay/Watch | Shared surfaces do not leak private text |
| Sign-out/delete | Stored audio, transcript, and projections clear or quarantine |
| Account change | Old source identifiers cannot resolve |

## Physical route record

Record each run:

- device model and OS;
- app version/build;
- audio session category/mode/options/policy;
- input and output route names/types;
- player/engine/analyzer state;
- source and queue revision;
- route/interruption events and timestamps;
- Now Playing projection;
- remote command and domain result;
- receiver/head-unit model;
- spatial/rendering mode if applicable;
- transcript/model availability;
- accessibility settings;
- privacy state;
- observed failures and fallback.

## Release matrix

| Stage | Verify |
| --- | --- |
| Source | AVFAudio, MediaPlayer, AVKit, Speech, Foundation Models, HIG, privacy, accessibility, release docs |
| Project | Framework imports, privacy strings, background modes, entitlements, extensions |
| Compile | Current signatures, tests, no target-only code leakage |
| Simulator | UI state, metadata, route fixtures, fallback |
| Physical iPhone/iPad | Permission, route, interruption, capture/playback |
| Hardware matrix | Headphones, Bluetooth, USB, AirPlay, CarPlay, Watch, multiroute |
| Archive | Version/build, entitlements, privacy, embedded targets |
| TestFlight | Install and system-surface behavior |
| App Store | Metadata, declarations, review |
| Production | Route failure telemetry and support observations |

## Sources

- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Audio routing](https://developer.apple.com/documentation/avfaudio/audio-routing)
- [Responding to audio route changes](https://developer.apple.com/documentation/avfaudio/responding-to-audio-route-changes)
- [Handling audio interruptions](https://developer.apple.com/documentation/avfaudio/handling-audio-interruptions)
- [AVAudioSession multiRoute](https://developer.apple.com/documentation/avfaudio/avaudiosession/category-swift.struct/multiroute)
- [Playing custom audio with your own player](https://developer.apple.com/documentation/avfaudio/playing-custom-audio-with-your-own-player)
- [AVRoutePickerView](https://developer.apple.com/documentation/avkit/avroutepickerview)
- [MPNowPlayingInfoCenter](https://developer.apple.com/documentation/mediaplayer/mpnowplayinginfocenter)
- [MPNowPlayingSession](https://developer.apple.com/documentation/mediaplayer/mpnowplayingsession)
- [MPRemoteCommandCenter](https://developer.apple.com/documentation/mediaplayer/mpremotecommandcenter)
- [Playing audio HIG](https://developer.apple.com/design/human-interface-guidelines/playing-audio)
- [AirPlay HIG](https://developer.apple.com/design/human-interface-guidelines/airplay)
- [SpeechAnalyzer](https://developer.apple.com/documentation/speech/speechanalyzer)
- [AssetInventory](https://developer.apple.com/documentation/speech/assetinventory)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SystemLanguageModel availability](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel/availability-swift.property)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
