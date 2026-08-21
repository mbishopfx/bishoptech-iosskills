# SwiftUI AVFAudio, AirPlay, and route-aware playback review design

This design guide turns the [audio-session and route-aware playback review](../42-framework-deep-dives/109-swiftui-avfaudio-airplay-route-aware-playback-review.md) into native SwiftUI decisions. It complements [native media and audio surfaces](18-native-media-and-audio-surfaces.md), but focuses on output selection, interruption, route state, system media controls, spatial capability, and reviewable speech or AI.

The goal is a calm audio surface that tells the truth about four things:

what the person asked for -> what the app is doing -> where the audio is routed -> what the system or model actually observed

## Design north star

A native audio surface:

- starts audio only when the user understands the action;
- shows the current output route without pretending it is a receipt;
- handles interruptions and disconnections visibly;
- uses system route and Now Playing controls where they fit;
- preserves a text and visual alternative for speech and spatial content;
- keeps AI results reviewable and source-linked;
- lets the system own Lock Screen, Control Center, CarPlay, Watch, and AirPlay presentation;
- uses Liquid Glass as a functional grouping tool on app-owned SwiftUI surfaces;
- remains useful when a route, asset, model, or receiver is unavailable.

Premium audio UX is not a fake control center. It is trustworthy state, strong hierarchy, and pleasant recovery.

## Screen and state map

| Screen role | Primary content | Secondary content | Safe failure |
| --- | --- | --- | --- |
| Library or queue | Current item and next choices | Artwork, metadata, duration | Empty, unavailable, or account state |
| Player | Title, playback position, primary controls | Queue, captions, route, speed | Buffering, paused, interrupted |
| Route selection | Current output and system route button | Last route, privacy hint | Receiver unavailable or canceled |
| Recorder | Recording state and elapsed time | Input route, level, stop/pause | Permission, interruption, route loss |
| Transcript | Source-linked text and time range | Locale, partial/final state | Unsupported locale or assets |
| AI review | Draft summary/tags/entities | Source excerpt, revision, accept/reject | Model unavailable or stale |
| Settings | Audio policy and privacy | Background, metadata donation | Unsupported option or defer |
| Handoff | Pending task and destination | Source revision, expiry | Destination unavailable |

## Playback hierarchy

Use a stable vertical order:

1. media identity;
2. playback state and time;
3. play/pause or stop;
4. seek and queue controls;
5. route selection;
6. captions or transcript;
7. secondary settings;
8. AI review.

Do not put the route picker and a destructive action in the same visual group with equal weight. A route picker changes where sound may be heard; it does not delete or publish content.

Use labels that explain the action:

- Choose output device;
- Playing on iPhone;
- AirPlay receiver selected;
- Headphones disconnected;
- Playback paused by a phone call;
- Recording input: iPhone Microphone;
- Transcript is provisional;
- Review suggested summary.

Avoid “Connected” without naming the meaning.

## Route-aware visual language

| State | Primary treatment | Detail |
| --- | --- | --- |
| Local output | Normal player state | Show iPhone, iPad, or named local output when available |
| AirPlay selected | Route icon and selected label | Add route age or receiver state only if actually observed |
| Switching | Pending state | Do not imply audio has moved until player/route state changes |
| Receiver unavailable | Error or fallback | Offer local playback or retry |
| Headphones disconnected | Pause or policy state | Respect privacy and user intent before switching |
| Bluetooth route | Named route if useful | Avoid exposing sensitive device names without need |
| CarPlay | System surface | Let CarPlay and MediaPlayer render vehicle controls |
| Watch command pending | Pending action | Wait for player/domain revision |
| Interrupted | Interrupted | Explain the system event without blaming the user |
| Model unavailable | Deterministic route | Keep playback/transcription usable without AI |
| Stale transcript | Stale | Link to source revision and regenerate/review |

Color can reinforce the route but must not be the only signal. Use text, symbols, and accessibility values.

## AirPlay and route picker composition

Use the system AVRoutePickerView through a small SwiftUI bridge or the current SwiftUI route control available to the selected SDK. Give the system button a native role. Avoid a custom sheet that copies receiver names, icons, and connection states.

Good composition:

- current output label;
- system route-picker button;
- short helper text such as Choose where audio plays;
- fallback action such as Play on this device;
- route-change or receiver-unavailable state.

Bad composition:

- a decorative glass card with a manually maintained receiver list;
- a “connected” badge driven only by the last selection;
- a custom volume slider that claims to set a remote receiver’s volume;
- an AirPlay picker hidden inside an unlabeled icon.

When the route changes, animate only the state that changed. Do not crossfade the entire player into a “remote mode” before the player confirms remote rendering.

## Liquid Glass rules for audio

On app-owned iPhone/iPad surfaces:

- use a small glass group for play, pause, seek, and route actions;
- keep the title, transcript, and source metadata outside excessive translucency;
- use a readable solid fallback for reduced transparency and high contrast;
- avoid a glass layer over a glass layer;
- use a glass morph only when one action changes continuously, such as record to stop;
- do not animate route changes as if they were confirmed when the receiver is still negotiating;
- keep critical transcript text on an opaque or high-contrast surface;
- never use glass opacity to encode audio confidence.

For CarPlay, Watch, Lock Screen, Control Center, and AirPlay receivers, use the system surface. The app can supply content and metadata but should not recreate the shell.

## MediaPlayer system surfaces

The player’s app-owned screen can show a rich control set. The system Now Playing projection should remain sparse and accurate.

Design in three layers:

| Layer | Visual responsibility |
| --- | --- |
| App player | Full queue, source details, route picker, captions, settings |
| Now Playing projection | Current item, progress, supported remote commands, artwork |
| Receiver or vehicle | System-rendered presentation and hardware input |

Enable only the remote commands the current player can complete. If the item cannot seek, do not expose a seek command. If the app cannot skip, do not show skip controls. The system may show metadata on a connected accessory, so title, artwork, and subtitle policy must be reviewed for privacy.

## Interruptions and recovery

A good interruption treatment is small and honest:

- playback paused by call;
- recording paused by route change;
- microphone unavailable;
- media services restarted; tap Play to resume;
- output changed to iPhone;
- transcript waiting for microphone permission.

Do not use a full-screen alert for every route change. Use a banner, state label, or control-row update unless user action is required. Keep a Resume action separate from Play when the system interrupted a user-started item.

For route loss, preserve the position and queue. Do not silently play private content through the speaker after headphones disappear if the product policy says privacy wins.

## Spatial and transcript alternatives

When spatial or multichannel output is available, communicate it as a capability and content choice:

- Spatial audio available;
- Using stereo fallback;
- This route does not support the selected format;
- Captions available.

Do not claim that a user experiences a particular spatial location solely from AVAudioSession renderingMode. Provide a transcript, captions, channel map, or standard playback path for people who cannot use spatial audio or for assistive technology.

For speech analysis:

- show partial transcript as Provisional;
- distinguish speaker/source labeling from raw transcription;
- show locale and time ranges when useful;
- make the source clip available;
- expose asset download or unsupported-locale states;
- preserve edits and accept/reject actions.

## AI review surface

Use a compact review card or dedicated sheet on iPhone:

- Source: recording name and time range;
- Status: Draft, Final transcript, or Needs review;
- Suggestion: bounded summary/tags/entities;
- Why shown: optional short provenance;
- Actions: Accept, Edit, Reject, Retry;
- Fallback: manual transcript or original audio.

Do not put a long generative chat inside a playback control surface. Do not make a model-generated summary the title of the recording until the user accepts it. Do not use an AI-generated confidence glow as a substitute for source evidence.

## Accessibility and alternate input

Test every audio state with:

- VoiceOver labels for route, play state, elapsed time, transcript status, and AI action;
- Voice Control names for route picker, play, pause, seek, accept, reject, and retry;
- Dynamic Type and long localized strings;
- Reduce Motion and Reduce Transparency;
- high contrast and non-color state cues;
- switch control, keyboard, pointer, headphones, CarPlay, and Watch commands;
- captions and text alternatives;
- audio output muted or unavailable;
- haptic feedback paired with a visual/textual state.

The route picker must have a meaningful label. A waveform must have a text equivalent. A transcript must not require spatial audio to understand the content.

## Privacy and metadata

Ask before exposing:

- recording title or transcript on Lock Screen;
- personal names in Now Playing metadata;
- location names in a CarPlay or Watch surface;
- message content in a shared receiver;
- raw audio to Speech or Foundation Models;
- media history to system suggestions.

Allow deletion and retention controls. If the app donates media through Now Playing, document whether the product opts out of suggestions. Do not put credentials, raw account IDs, or private transcript body into Handoff, Watch Connectivity, or system metadata.

## Design QA matrix

| Review | Preview | Simulator | Physical device |
| --- | --- | --- | --- |
| Playback hierarchy | Fixture states | Layout and controls | Visibility and touch/voice |
| Route picker | Bridge preview | Button presentation | Receiver choice and cancellation |
| Route change | Mock events | State transitions | Headphones/Bluetooth/USB/AirPlay |
| Interruption | Mock begin/end | UI recovery | Call, Siri, alarm, navigation prompt |
| Media reset | Reducer fixture | Recovery copy | Developer media-services reset |
| Now Playing | Metadata fixture | Control surface | Lock Screen, Control Center, CarPlay, Watch |
| Spatial mode | Capability fixture | Fallback layout | Named hardware and listener check |
| Transcript | Partial/final fixture | Long text | Real microphone and locale/assets |
| AI | Candidate fixtures | Availability fallback | Device model availability and review |
| Liquid Glass | Accessibility previews | Alternate effects | Physical contrast and motion |
| Release | Target inspection | Signed run | Archive, TestFlight, version/build |

## Sources

- [Playing audio HIG](https://developer.apple.com/design/human-interface-guidelines/playing-audio)
- [AirPlay HIG](https://developer.apple.com/design/human-interface-guidelines/airplay)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Responding to audio route changes](https://developer.apple.com/documentation/avfaudio/responding-to-audio-route-changes)
- [Handling audio interruptions](https://developer.apple.com/documentation/avfaudio/handling-audio-interruptions)
- [Audio routing](https://developer.apple.com/documentation/avfaudio/audio-routing)
- [AVRoutePickerView](https://developer.apple.com/documentation/avkit/avroutepickerview)
- [MPNowPlayingInfoCenter](https://developer.apple.com/documentation/mediaplayer/mpnowplayinginfocenter)
- [MPRemoteCommandCenter](https://developer.apple.com/documentation/mediaplayer/mpremotecommandcenter)
- [SpeechAnalyzer](https://developer.apple.com/documentation/speech/speechanalyzer)
- [AssetInventory](https://developer.apple.com/documentation/speech/assetinventory)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SystemLanguageModel availability](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel/availability-swift.property)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [CarPlay](https://developer.apple.com/documentation/carplay)
- [Watch Connectivity](https://developer.apple.com/documentation/watchconnectivity)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
