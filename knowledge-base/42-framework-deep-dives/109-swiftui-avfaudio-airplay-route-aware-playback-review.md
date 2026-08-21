# SwiftUI AVFAudio, AirPlay, and route-aware playback review

This is the focused audio-session and output-route review for an iOS app that plays, records, processes, or hands off audio. It complements the existing [MediaPlayer Now Playing and remote-command route](28-mediaplayer-now-playing-and-remote-command-routes.md) and [SwiftUI audio capture and transcription review](89-swiftui-audio-capture-and-transcription.md). Those pages cover their own boundaries; this page concentrates on the layer where audio-session intent, route changes, interruptions, AirPlay, spatial rendering, multiroute, system commands, speech analysis, and physical output behavior meet.

The central rule is:

user audio outcome -> audio-session category/mode/options -> activation and route policy -> player or engine owner -> route/interruption/media-service state -> system metadata and command surface -> optional transcript or AI proposal -> reviewed domain action -> physical-output proof

AVAudioSession describes the app’s intended audio behavior to the operating system. It does not prove that a microphone captured useful sound, that a speaker is audible, that an AirPlay receiver accepted a stream, that spatial rendering is perceptible, or that a remote command changed domain state. MediaPlayer supplies system metadata and commands; it does not own a product’s queue or guarantee the format shown by every accessory.

## Route thesis

Choose the smallest audio architecture that matches the outcome.

| User outcome | Primary route | Add only when needed | What must remain separate |
| --- | --- | --- | --- |
| Play long-form music, spoken audio, or ambient content | AVAudioSession playback category, AVPlayer or app-owned player, MediaPlayer Now Playing | AirPlay 2 long-form route-sharing policy, remote commands, CarPlay | Session state, actual player state, route state, Now Playing projection |
| Play short sound effects without taking over other audio | Ambient or a documented mix/duck policy | Haptics and system sounds | Sound request, mix policy, and audible result |
| Record from a microphone | Record or playAndRecord category, capture engine, permission | SpeechAnalyzer, SoundAnalysis, monitoring | Permission, session, input route, buffer stream, analysis result |
| Record and play at once | playAndRecord with a supported mode and options | Echo cancellation, Bluetooth HFP, call integration | Input/output route and actual duplex behavior |
| Route to a selected AirPlay receiver | AVRoutePickerView and compatible session policy | Long-form route sharing, receiver-specific playback | User selection, current route, renderer state, receiver acceptance |
| Send distinct streams to multiple outputs | multiRoute category and channel/output mapping | USB, headphones, simultaneous input/output | Route graph, hardware capabilities, per-output stream state |
| Deliver spatial or multichannel audio | Player/renderer plus route capability inspection | Rendering mode, channel layouts, asset format | Asset format, selected route, rendering mode, perceived result |
| Drive lock-screen, Control Center, headphone, CarPlay, or Watch commands | MediaPlayer Now Playing and remote commands | MPNowPlayingSession for multiple players | Command receipt, player mutation, committed queue revision |
| Transcribe or summarize audio | SpeechAnalyzer/SpeechTranscriber, then Foundation Models if appropriate | AssetInventory, guided generation, tools | Audio source, transcript revision, AI candidate, user approval |
| Keep audio coherent across CarPlay, Watch, and AirPlay | One authoritative playback owner and revisioned projections | Watch Connectivity, CarPlay templates, Handoff | Device route, system surface, account/queue truth |

Do not solve an audio-session problem with a custom SwiftUI player alone. Do not solve a product-state problem with a route enum alone.

## The audio state model

Use layered state rather than one isPlaying Boolean.

| Layer | Example observations | Safe interpretation |
| --- | --- | --- |
| Permission | record permission, speech locale/asset readiness | The app may request or use an input route |
| Session configuration | category, mode, options, route-sharing policy | The app told the system how it intends to use audio |
| Session activation | active, inactive, activation error | The system accepted or rejected a session activation attempt |
| Current route | input/output ports, data sources, route reason | The system currently describes an audio path |
| Player or engine | time control, rate, buffer, engine running | The app’s playback or processing object reports state |
| Interruption | began, ended, resume option | Another system event changed audio availability |
| Media service | lost, reset | Recreate audio objects and restore configuration |
| Rendering | mono/stereo, surround, Dolby, spatial, not applicable | The selected route and renderer report a mode |
| System projection | Now Playing info, remote command enabled state | The system has a projection or command surface |
| Domain truth | queue revision, accepted command, saved recording | The product committed a change |
| AI output | transcript, summary, structured proposal | An analysis candidate that needs source and revision context |
| Physical result | audible, recorded, receiver playing, user-perceived | Evidence from a named device and route |

A route change can happen while the player remains technically playing. A remote command can be received while a domain mutation fails. A transcript can be final for one source revision while the user edits the source record. Keep these states visible in code and in proof records.

## AVAudioSession category, mode, and options

### Categories are behavioral contracts

Apple’s audio-session categories describe broad intended behavior:

| Category | Good fit | Important boundary |
| --- | --- | --- |
| ambient | Playback that can mix and may continue to be useful when silent | Not a general music takeover policy |
| soloAmbient | Primary playback that silences other audio under the category’s behavior | Confirm whether the interruption policy matches the product |
| playback | Recorded music or other central playback, including background playback when configured | Does not mean the item is ready or that AirPlay is selected |
| record | Input capture that silences playback | No output route is implied |
| playAndRecord | VoIP, capture plus playback, or duplex features | AirPlay and Bluetooth behavior differs from playback-only |
| multiRoute | Distinct streams to multiple output devices | Route changes can invalidate the configuration |
| audioProcessing | Hardware codec or signal processing without ordinary playback/record | Not a shortcut to a custom player |

Choose the category from the actual behavior. Do not use playback merely because the app has a play button, or playAndRecord merely because the user may later record. Categories have AirPlay and route implications: playback-only categories support mirrored and nonmirrored AirPlay, while record and multiRoute do not allow AirPlay in the same way. PlayAndRecord supports a narrower AirPlay path.

### Modes specialize a category

A mode supplies specialized behavior within a category. Examples include movie playback, spoken audio, voice chat, video chat, measurement, game chat, and dual route. If the category does not support the chosen mode, Apple documents that the session uses default mode behavior. Treat an unsupported category/mode pair as a configuration defect, not as a creative fallback.

Record the intended pair:

- category;
- mode;
- options;
- route-sharing policy;
- background mode;
- input/output requirements;
- whether the session is long-form, transient, voice, capture, or processing.

### Options change coexistence

Options such as mixWithOthers, duckOthers, interruptSpokenAudioAndMixWithOthers, allowAirPlay, allowBluetooth, defaultToSpeaker, and voice-processing-related options affect the experience of other audio and devices. Use the narrowest option set that matches the user outcome.

Do not:

- duck every other app because a preview sound played;
- interrupt spoken audio for a nonessential effect;
- assume allowAirPlay can be added to every category;
- change output port while a call or system-owned route controls the session;
- leave an audio session active after the app finishes a temporary sound.

If audio is temporary, deactivate with the documented notification option so other apps know they may resume.

## Activation timing and ownership

Configure the session before activation, but generally defer activation until the app is ready to play, record, or process. Activating early can interrupt other audio before the user has chosen the action.

Use one long-lived audio coordinator per target:

1. The coordinator owns category, mode, options, and activation policy.
2. The player, engine, or analyzer owns its own lifecycle behind that coordinator.
3. Route and interruption notifications become typed events.
4. A domain actor or MainActor store receives snapshots.
5. SwiftUI observes the snapshot and renders controls.
6. MediaPlayer receives a projection of actual playback state.
7. Deactivation occurs when the product no longer needs the route.

Do not configure AVAudioSession from a SwiftUI body, create an engine on every view refresh, or let a remote command handler mutate several independent playback owners.

## Route changes

A route changes when the system adds or removes an input or output, such as wired headphones, a Bluetooth headset, a USB audio interface, CarPlay, or AirPlay. Apple posts AVAudioSessionRouteChangeNotification with a reason and previous-route value, and the notification can arrive on a secondary thread.

On every route change:

1. capture the reason and previous route;
2. read the current route on the audio service;
3. compare input/output ports and data sources;
4. check the player or engine’s format and time state;
5. decide whether to continue, pause, reconfigure, or ask for user action;
6. publish a typed state with freshness;
7. update Now Playing only after the player’s actual state is known.

For oldDeviceUnavailable, Apple documents that the expected behavior is to pause playback when the active route disappears. Beginning with iOS 17, the system interrupts active Now Playing sessions for a route-disconnect event while other sessions are not necessarily interrupted. Do not blindly resume when a new route appears; use the interruption/route policy and user intent.

If headphones are connected or removed, the HIG says people expect media playback to continue privately when they connect headphones. Test the product’s real behavior, especially when audio was paused, a call is active, or a route is controlled by another system surface.

## Interruptions and media services

### Interruption lifecycle

Observe AVAudioSession interruption notifications. When an interruption begins:

- stop or pause the player/engine as the API requires;
- record whether the user had actively started playback;
- preserve queue and source revision;
- update controls to interrupted or unavailable;
- do not treat the interruption as a user pause.

When it ends, inspect the interruption options and current session/player state. Resume only when the product policy, system option, and user intent support resumption. A phone call, Siri request, alarm, route change, or another app can have different semantics. A hard-coded resume is unsafe.

### Media services reset or loss

Apple documents mediaServicesWereResetNotification and mediaServicesWereLostNotification for a media-server restart or termination. On reset, reinitialize audio objects and reset category, options, and mode configuration. Do not automatically restart playback, recording, or processing; wait for user action or an explicit recoverable workflow.

Keep a recovery record:

- old player or engine identity;
- source and queue revision;
- route before reset;
- reset/lost timestamp;
- recreated object status;
- user action that resumed work;
- any dropped or rebuffered audio.

A media-server reset is not the same as a route change, interruption, or application termination.

## AirPlay and route selection

### System route picker

Use AVRoutePickerView or the SwiftUI bridge to present the system list of nearby media receivers. The system presents receiver choices and handles the route-selection interaction. Do not build a fake speaker list from names observed in the current route.

Keep three facts separate:

| Fact | Meaning |
| --- | --- |
| route picker presented | The user can choose a receiver |
| currentRoute shows an output | The session currently reports an output path |
| player is rendering remotely | The player/renderer and system report remote playback |
| receiver displays or emits audio | Physical receiver evidence |
| command succeeded | The app’s player/domain accepted the command |

The route picker’s active tint can communicate an active AirPlay state, but color is not a receipt. The user may cancel, the receiver may be unavailable, or the stream may fail after selection.

### Long-form audio

Apple’s custom audio sample uses AVAudioSession.RouteSharingPolicy.longFormAudio for long-form audio and AirPlay 2 behavior such as extended buffering, responsiveness, and multiroom playback. Treat this as an intent/policy hint for music, podcasts, audiobooks, or similar extended listening, not as a guarantee of multiroom or receiver support.

Do not label a short sound effect as long-form just to make it appear in an AirPlay route. Do not claim an AirPlay route is active because the app selected the policy.

### AirPlay and input

AirPlay behavior depends on the category. Playback-only categories support broader AirPlay variants. PlayAndRecord, record, and multiRoute have restrictions. If a feature needs microphone input and remote playback, test the exact category, mode, option set, and device route on physical hardware.

## Multiroute

The multiRoute category can route distinct streams to multiple output devices, such as USB and headphones, and may support input/output together. It requires detailed knowledge of current route capabilities. Apple warns that route changes can invalidate part or all of a multiroute configuration and says observing routeChangeNotification is essential.

A multiroute design must record:

- all active input and output ports;
- channel and format requirements;
- which stream belongs to which output;
- what happens when one output disappears;
- whether the remaining output can carry the stream;
- how the user stops or reassigns a stream;
- whether the route is still valid after reconnect.

A multiroute simulator graph is not physical proof. Use named hardware, cables, USB interfaces, headphones, and the intended power/connection order.

## Spatial and multichannel playback

AVAudioSession exposes rendering mode and supported output channel layouts. The rendering mode can report mono/stereo, surround, spatial audio, Dolby audio, Dolby Atmos, or not applicable. Apple documents that the mode can be not applicable when the route is not car audio or AirPlay, playback is inactive, the API does not support the needed renderer, the session is muted, or the app is not eligible for Now Playing.

Treat spatial state as a capability observation:

- asset contains or requests a format;
- selected route supports a channel layout;
- renderer is active;
- audio session reports a rendering mode;
- device and user settings allow the path;
- physical listener confirms the intended result.

Do not use a spatial label to promise immersion, positional accuracy, or a medical/attention benefit. Provide a mono/stereo fallback and captions or text controls where the user needs to understand content without the spatial effect.

## MediaPlayer and Now Playing coordination

MediaPlayer’s Now Playing system is a projection and command channel:

- MPNowPlayingInfoCenter publishes metadata;
- MPRemoteCommandCenter receives system/accessory commands;
- MPNowPlayingSession coordinates multiple players;
- CarPlay, Control Center, Lock Screen, headphones, Watch, AirPlay receivers, and accessories may display or control the current item;
- the system or accessory controls formatting and visibility.

Use one owner for playback. Apple warns against adding a custom MPNowPlayingSession to the AVPlayer presented by AVPlayerViewController. Choose either the system player ownership model or an app-owned player/session model and keep that choice explicit.

A remote command pipeline is:

system command -> enabled command handler -> player operation -> actual player result -> queue/domain revision -> Now Playing projection

Disable commands that the current player cannot perform. A handler that returns success before the player changes state creates a false system surface. Update elapsed time, duration, rate, queue index, artwork, language options, and playback state from actual player observations.

Now Playing metadata can appear on Lock Screen, Control Center, connected accessories, CarPlay, or an AirPlay destination. Apple also documents that contributed media may be used for Siri suggestions and, unless excluded, Journaling Suggestions. Decide what metadata the product is willing to donate and apply the documented exclusion control where needed. This is a privacy and product decision, not merely a UI setting.

## CarPlay, Watch, and handoff

CarPlay’s CPNowPlayingTemplate is a shared audio template available to audio-entitled CarPlay apps. Keep the iPhone playback owner and CarPlay system projection aligned, but do not equate a CarPlay scene connection with audio-route truth.

A Watch companion may display or control playback through Watch Connectivity, but paired reachability and an immediate message do not prove that audio changed. Use a revisioned command:

- source queue revision;
- target item identifier;
- expected player state;
- command identifier;
- device of origin;
- result revision;
- stale or conflict outcome.

AirPlay route selection, CarPlay output, and Watch controls can race. One domain coordinator should arbitrate the command and publish the committed result to each system surface.

Handoff should carry a typed task or playback context, not raw credentials or a claim that a receiver is already playing. Re-resolve the item and account when the destination scene becomes active.

## Speech and on-device intelligence

SpeechAnalyzer is an asynchronous actor-based analysis path. Apple documents that it can analyze one input sequence at a time, modules provide results through AsyncSequence, and assets may need to be installed through AssetInventory. Keep microphone permission, audio session, input sequence, locale, asset status, partial transcript, final transcript, and cancellation state separate.

Foundation Models is a text generation and understanding route. Use it after a transcript or other bounded text source exists. It can summarize, extract entities, classify, refine, and generate structured content, but Apple documents that it is not suitable for every task, including basic arithmetic or arbitrary code generation. Check SystemLanguageModel availability, locale, model readiness, context size, and capability before generating.

Safe audio intelligence:

1. preserve source audio identity and time ranges;
2. produce a provisional or final transcript through Speech;
3. mark transcript revision and locale;
4. pass only the minimum authorized text to Foundation Models;
5. request a bounded schema for tags, summary, or draft;
6. validate source revision and output limits;
7. show the result as a proposal;
8. require user acceptance before changing a record or publishing content;
9. use deterministic fallback when the model or speech asset is unavailable.

Do not let a transcript, waveform, or model summary claim that the speaker said something the source does not support. Do not record or summarize private audio without the product’s permission, retention, and disclosure policy.

## Native SwiftUI and Liquid Glass

On app-owned iPhone surfaces, use SwiftUI’s current controls, semantic labels, dynamic type, and limited Liquid Glass grouping around functional playback controls. A route picker, Now Playing card, waveform, and AI review panel are separate jobs.

Use:

- a clear route button that invokes the system picker;
- textual current-route and unavailable states;
- native play/pause/seek/volume semantics;
- reduced-transparency fallback;
- captions/transcript for speech;
- a review shell for AI proposals.

Do not place glass on top of every waveform segment, use transparency to imply that a receiver accepted playback, or recreate Control Center, Lock Screen, CarPlay, or AirPlay system surfaces. The system owns those surfaces.

## Accessibility and privacy

Audio is not accessible merely because it has a play button. Review:

- VoiceOver labels and current values for route, playback, recording, and analysis;
- Voice Control names for play, pause, stop, seek, route, accept, reject, and retry;
- captions and transcript alternatives;
- Dynamic Type and long localized titles;
- Reduce Motion and Reduce Transparency;
- high contrast and non-color state cues;
- switch, keyboard, pointer, and external control input;
- safe handling when audio output is muted or unavailable;
- microphone and speech usage descriptions;
- route metadata and media donation policy;
- delete/export/retention behavior for recordings and transcripts;
- locked-screen and connected-accessory exposure.

A Now Playing item may appear outside the app. A route name or artwork may be visible on a shared speaker, car display, Lock Screen, or Watch. Keep sensitive titles, contact names, message bodies, location names, and account identifiers out of metadata unless the user and product policy permit them.

## Failure matrix

| Failure | Wrong conclusion | Correct response |
| --- | --- | --- |
| Session activation succeeds | Audio is audible | Inspect player/engine and use physical output evidence |
| Route reports AirPlay | Receiver accepted and plays | Record picker selection, renderer state, receiver result, and recovery |
| Headphones disconnect | Playback should continue from speaker | Apply route/interruption policy and protect privacy |
| Interruption ends | Always resume | Inspect options and user intent |
| Media services reset | Restart the queue automatically | Recreate audio objects and wait for user action |
| Mode is unsupported | The requested voice behavior is active | Verify category/mode support; expose fallback |
| MultiRoute has two ports | Both streams are stable | Reconcile route changes and hardware loss |
| Spatial mode is Dolby or spatial | Every listener perceives the intended effect | Report capability and provide fallback |
| Remote command returns | Domain command committed | Wait for actual player/domain result |
| Now Playing appears | Metadata format is under app control | Treat the system/accessory as renderer |
| Transcript is final | It is ground truth | Preserve source, locale, revision, and correction path |
| Model is available | It can handle every audio task | Check capability, context, locale, and deterministic fallback |
| Liquid Glass looks premium | It is an accessible audio UX | Test alternate input, contrast, motion, and text alternatives |

## Evidence ladder

| Level | Evidence | Supports | Does not support |
| --- | --- | --- | --- |
| L0 | Official source review | Category, route, system surface, and model boundaries | A working app |
| L1 | Project and entitlement inspection | Target, privacy strings, background mode, route policy, framework placement | Actual hardware behavior |
| L2 | Pure reducer and fixture tests | Interruption, route, command, revision, AI fallback logic | Sound, receiver, or microphone fidelity |
| L3 | Preview and Simulator | SwiftUI shell, mock routes, metadata, system-state fixtures | Physical output, AirPlay receiver, real interruptions, spatial perception |
| L4 | Signed physical iPhone or iPad | Permission, route, recording, playback, interruptions, system surfaces | Every route/device/receiver |
| L5 | Named physical output set | Headphones, Bluetooth, USB, AirPlay, CarPlay, Watch, multiroute, spatial behavior | Universal hardware compatibility |
| L6 | Archive and TestFlight | Target graph, entitlements, privacy manifest, version/build, install | Audio quality or App Review |
| L7 | Production observation | Real user route and diagnostic evidence | Future OS, device, receiver, or listener experience |

## Implementation checklist

Before implementing, record:

- user outcome and audio type;
- source identity and revision;
- category, mode, options, and route-sharing policy;
- activation and deactivation timing;
- player/engine/analyzer owner;
- input and output route requirements;
- interruption and route-change policy;
- media-services reset/lost recovery;
- AirPlay route picker and fallback;
- multiroute or spatial capabilities, if applicable;
- Now Playing and remote command ownership;
- CarPlay/Watch/Handoff projection boundaries;
- Speech assets and Foundation Models availability/fallback;
- transcript or AI proposal review boundary;
- Liquid Glass scope and alternate visual fallback;
- accessibility, privacy, retention, and metadata donation policy;
- physical route matrix;
- archive, TestFlight, and release proof.

## Sources

- [AVFAudio](https://developer.apple.com/documentation/avfaudio)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [AVAudioSession categories](https://developer.apple.com/documentation/avfaudio/avaudiosession/category-swift.struct)
- [AVAudioSession modes](https://developer.apple.com/documentation/avfaudio/avaudiosession/mode-swift.struct)
- [Audio routing](https://developer.apple.com/documentation/avfaudio/audio-routing)
- [Responding to audio route changes](https://developer.apple.com/documentation/avfaudio/responding-to-audio-route-changes)
- [AVAudioSession route-change notification](https://developer.apple.com/documentation/avfaudio/avaudiosession/routechangenotification)
- [Handling audio interruptions](https://developer.apple.com/documentation/avfaudio/handling-audio-interruptions)
- [AVAudioSession multiRoute category](https://developer.apple.com/documentation/avfaudio/avaudiosession/category-swift.struct/multiroute)
- [AVAudioSession allowAirPlay option](https://developer.apple.com/documentation/avfaudio/avaudiosession/categoryoptions-swift.struct/allowairplay)
- [AVAudioSession rendering mode](https://developer.apple.com/documentation/avfaudio/avaudiosession/renderingmode-swift.property)
- [Playing custom audio with your own player](https://developer.apple.com/documentation/avfaudio/playing-custom-audio-with-your-own-player)
- [AVRoutePickerView](https://developer.apple.com/documentation/avkit/avroutepickerview)
- [MediaPlayer](https://developer.apple.com/documentation/mediaplayer)
- [Becoming a now playable app](https://developer.apple.com/documentation/mediaplayer/becoming-a-now-playable-app)
- [MPNowPlayingInfoCenter](https://developer.apple.com/documentation/mediaplayer/mpnowplayinginfocenter)
- [MPNowPlayingSession](https://developer.apple.com/documentation/mediaplayer/mpnowplayingsession)
- [MPRemoteCommandCenter](https://developer.apple.com/documentation/mediaplayer/mpremotecommandcenter)
- [Handling external player events notifications](https://developer.apple.com/documentation/mediaplayer/handling-external-player-events-notifications)
- [Playing audio HIG](https://developer.apple.com/design/human-interface-guidelines/playing-audio)
- [AirPlay HIG](https://developer.apple.com/design/human-interface-guidelines/airplay)
- [Speech](https://developer.apple.com/documentation/speech)
- [SpeechAnalyzer](https://developer.apple.com/documentation/speech/speechanalyzer)
- [SpeechTranscriber](https://developer.apple.com/documentation/speech/speechtranscriber)
- [AssetInventory](https://developer.apple.com/documentation/speech/assetinventory)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [SystemLanguageModel availability](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel/availability-swift.property)
- [Generating content and performing tasks with Foundation Models](https://developer.apple.com/documentation/foundationmodels/generating-content-and-performing-tasks-with-foundation-models)
- [LanguageModelCapabilities](https://developer.apple.com/documentation/foundationmodels/languagemodelcapabilities)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Watch Connectivity](https://developer.apple.com/documentation/watchconnectivity)
- [Implementing Handoff](https://developer.apple.com/documentation/foundation/implementing-handoff-in-your-app)
- [CarPlay](https://developer.apple.com/documentation/carplay)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines)
