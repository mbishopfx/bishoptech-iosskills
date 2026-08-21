# SwiftUI AVFAudio, AirPlay, and route-aware playback review route

This route card turns the [audio-session and route-aware playback review](../42-framework-deep-dives/109-swiftui-avfaudio-airplay-route-aware-playback-review.md) into implementation decisions. It complements the [audio capture recipes](../70-code-recipes/132-swiftui-audio-capture-and-transcription-recipes.md) and the [MediaPlayer route](../42-framework-deep-dives/28-mediaplayer-now-playing-and-remote-command-routes.md). Read the [design guide](../21-design-deep-dives/137-swiftui-avfaudio-airplay-route-aware-playback-review-design.md), [proof matrix](../60-verification/134-swiftui-avfaudio-airplay-route-aware-playback-review-proof-matrix.md), and [recipes](../70-code-recipes/152-swiftui-avfaudio-airplay-route-aware-playback-review-recipes.md) before implementation.

A route is complete only when the session policy, player or engine owner, physical output, system projection, user command, optional model result, and release artifact agree.

## Route selector

| Outcome | Start here | Add only when needed | First proof gate |
| --- | --- | --- | --- |
| Long-form playback | AVAudioSession playback category, AVPlayer or app-owned player, MediaPlayer | RouteSharingPolicy.longFormAudio, AirPlay, CarPlay | Background audio and physical playback |
| Short sound effect | Ambient or another narrow category | mixWithOthers, duckOthers, haptics | Coexistence with another app |
| Voice capture | record or playAndRecord, AVAudioEngine | SpeechAnalyzer, SoundAnalysis | Permission, input route, interruption |
| Duplex voice | playAndRecord, supported voice mode | Bluetooth HFP, echo cancellation, CallKit | Real microphone/speaker route |
| AirPlay selection | AVRoutePickerView | Long-form policy or custom route | Physical receiver selection and output |
| Multiple outputs | multiRoute | USB, headphones, per-stream mapping | Physical port graph and loss |
| Spatial/multichannel | Player/renderer and route capability | Rendering mode and supported layouts | Named route and asset format |
| External controls | MediaPlayer Now Playing | MPNowPlayingSession for multiple players | Command updates actual player state |
| Speech-to-text | SpeechAnalyzer and SpeechTranscriber | AssetInventory, locale fallback | Real audio plus final result |
| AI summary/tags | Foundation Models after bounded transcript | Guided generation/tools | Availability, source revision, review |
| CarPlay audio | Audio entitlement plus CPNowPlayingTemplate | Siri media intents | Locked phone, head unit, interruption |
| Watch audio control | Watch Connectivity command projection | Handoff or App Intent | Paired-device revision and commit |

## Preflight worksheet

### Product

- User outcome:
- Audio type: long-form, short effect, capture, duplex, spatial, or analysis
- Source identity:
- Source revision:
- Account or privacy scope:
- Primary playback or capture owner:
- Is audio expected in the background:
- Is the action reversible:
- Is a transcript or AI proposal optional:

### Session

- Category:
- Mode:
- Options:
- Route-sharing policy:
- Activation trigger:
- Deactivation trigger:
- Input required:
- Output required:
- Background mode:
- Interruption policy:
- Route-disconnect policy:
- Media-services reset policy:
- Secondary-audio/mixing policy:

### Route

- Current-route inputs:
- Current-route outputs:
- Expected device classes:
- AirPlay route picker:
- CarPlay:
- Bluetooth:
- USB:
- Multiroute:
- Spatial/multichannel:
- Receiver/user cancellation:
- Fallback output:

### System surfaces

- Now Playing metadata:
- Enabled remote commands:
- Lock Screen exposure:
- Control Center exposure:
- CarPlay exposure:
- Watch exposure:
- AirPlay receiver exposure:
- Metadata donation/opt-out decision:

### Intelligence

- Speech module:
- Locale:
- Asset state:
- Transcript revision:
- Foundation Models availability:
- Model capability:
- Context size:
- Candidate schema:
- Validation:
- User review:
- Deterministic fallback:

### Proof

- Source review:
- Unit/reducer tests:
- Preview:
- Simulator:
- iPhone/iPad:
- headphones/Bluetooth/USB:
- AirPlay receiver:
- CarPlay head unit:
- Watch:
- media-services reset:
- accessibility:
- privacy:
- archive:
- TestFlight:
- release:

## Phase 1: choose the session contract

Use the category table from AVFAudio and record why the category matches the actual behavior. Then choose a mode and options that are supported together.

Stop if:

- the feature does not know whether it plays, records, or does both;
- the category is chosen from a sample rather than the product behavior;
- the mode is unsupported by the category;
- AirPlay or Bluetooth requirements conflict with the category;
- the session is activated before the user starts the feature;
- there is no owner for deactivation.

## Phase 2: choose the player or engine owner

| Owner | Use when | Avoid |
| --- | --- | --- |
| AVPlayer or system player | File/stream playback and system player capabilities fit | Duplicating session/Now Playing ownership |
| App-owned AVPlayer plus MediaPlayer | App needs custom queue/control and can own state | Returning remote command success before player state |
| AVAudioEngine | Capture, effects, metering, custom processing | Treating engine running as proof of useful input |
| AVSampleBufferAudioRenderer | Custom sample-buffer playback and advanced route behavior | Unbounded enqueue or no backpressure |
| SpeechAnalyzer | Transcription or audio analysis | Feeding multiple sequences concurrently |
| AVPlayerViewController | System video playback and controls fit | Adding custom MPNowPlayingSession to its AVPlayer |

Use one source of truth for playback position, rate, current item, queue revision, and user intent. The system surfaces receive projections.

## Phase 3: route lifecycle

Implement this event order:

1. configure category/mode/options/policy;
2. request permission if input is needed;
3. observe interruptions, route changes, media services, and relevant player state;
4. activate only when the feature is ready;
5. start the player/engine/analyzer;
6. publish current route and actual state;
7. handle route/interruption changes;
8. stop or pause by user/system policy;
9. deactivate and notify other audio;
10. retain a recoverable source or queue state.

### Route event table

| Event | Required action |
| --- | --- |
| new output appears | Read current route and compare formats |
| old output disappears | Apply pause/privacy policy; do not blindly resume |
| headphones connect | Preserve private playback intent when safe |
| Bluetooth profile changes | Reconfigure input/output and format if needed |
| AirPlay selection | Wait for current-route/player confirmation |
| AirPlay canceled | Remain local or restore prior state |
| CarPlay connects | Let CarPlay own its system template; project actual player state |
| interruption begins | Pause/stop according to API and preserve source state |
| interruption ends | Inspect options and user intent before resume |
| media services reset | Recreate audio objects and configuration; wait for action |
| media services lost | Mark unavailable and show recovery |
| app backgrounded | Follow target background and session policy |
| app terminated | Recover queue/source from durable state |

## Phase 4: AirPlay and multiroute

Use AVRoutePickerView for user selection. Keep route picker UI and route truth separate. For long-form audio, decide whether longFormAudio route sharing is truthful. For multiroute, list each output, stream mapping, and fallback when one port disappears.

Stop if a design has:

- a manual receiver list;
- a “connected” badge with no current-route/player evidence;
- a multiroom promise without a named receiver run;
- a multiroute graph with no loss policy;
- a playAndRecord route that assumes full AirPlay support.

## Phase 5: Now Playing and remote commands

Set Now Playing metadata only from actual playback state. Enable only commands the current item and player support. Remote commands should call the same command service as the app UI, CarPlay, Watch, and Siri.

A command is complete only when:

- the handler receives the event;
- the domain/player accepts or rejects it;
- the queue or player revision changes as expected;
- Now Playing metadata is updated;
- the UI shows the result or failure.

## Phase 6: speech and AI

For SpeechAnalyzer:

- choose a supported locale;
- install or verify required assets;
- feed one bounded input sequence;
- expose partial versus final results;
- finish or cancel the analyzer;
- preserve source time ranges and revisions.

For Foundation Models:

- check SystemLanguageModel availability;
- check locale, context, and capability;
- use only minimum necessary transcript text;
- ask for structured output;
- validate identifiers, limits, and source revision;
- ask the user to accept a summary/tag/action;
- preserve the original audio and transcript;
- use manual fallback.

The model does not become an audio meter, transcript authority, or command executor merely because it can read text.

## Phase 7: native SwiftUI design

On iPhone/iPad:

- use native playback controls and system route picker;
- use a small functional Liquid Glass group;
- show route and interruption text;
- provide captions/transcript;
- give AI results a review state;
- keep source and approved result visible.

On CarPlay, Watch, Lock Screen, Control Center, and AirPlay, use system surfaces. Do not ship a custom fake surface to imitate them.

## Phase 8: proof and release

Use the proof matrix to test:

- session category/mode/options;
- permission and denial;
- route changes;
- interruptions and resume policy;
- media-services reset/loss;
- AirPlay picker and physical receiver;
- multiroute port loss;
- spatial rendering capability/fallback;
- Now Playing and remote commands;
- CarPlay and Watch projections;
- Speech assets and locale;
- Foundation Models unavailable/stale/invalid;
- accessibility and privacy;
- signed entitlements, privacy resources, archive, TestFlight, and release.

## Compact route record

- Outcome:
- Category/mode/options:
- Player/engine owner:
- Activation/deactivation:
- Input/output route:
- AirPlay policy:
- Multiroute/spatial:
- Interruption and reset:
- Now Playing owner:
- CarPlay/Watch/Handoff:
- Speech/model:
- AI review:
- Liquid Glass scope:
- Accessibility/privacy:
- Physical device set:
- Release evidence:
- Open risks:

## Sources

- [AVFAudio](https://developer.apple.com/documentation/avfaudio)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Audio routing](https://developer.apple.com/documentation/avfaudio/audio-routing)
- [Responding to audio route changes](https://developer.apple.com/documentation/avfaudio/responding-to-audio-route-changes)
- [Handling audio interruptions](https://developer.apple.com/documentation/avfaudio/handling-audio-interruptions)
- [AVAudioSession categories](https://developer.apple.com/documentation/avfaudio/avaudiosession/category-swift.struct)
- [AVAudioSession modes](https://developer.apple.com/documentation/avfaudio/avaudiosession/mode-swift.struct)
- [Playing custom audio with your own player](https://developer.apple.com/documentation/avfaudio/playing-custom-audio-with-your-own-player)
- [AVRoutePickerView](https://developer.apple.com/documentation/avkit/avroutepickerview)
- [MediaPlayer](https://developer.apple.com/documentation/mediaplayer)
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
