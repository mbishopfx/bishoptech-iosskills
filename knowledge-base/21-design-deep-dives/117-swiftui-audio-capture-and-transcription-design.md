# SwiftUI audio capture and transcription design

## Design goal

Make the audio source, recording state, transcript certainty, sound
observations, and destination legible at a glance.

Use this composition:

~~~text
recording intent
    -> permission and route
    -> listening/paused/stopped
    -> live transcript and waveform
    -> final transcript and time-linked observations
    -> review/edit
    -> save/export/share
~~~

The primary surface is the transcript, recording, or review timeline. The
waveform is a quiet visual explanation of time and level. Liquid Glass groups
the actions that help the current task; it does not carry the entire app or
make uncertain AI text look authoritative.

## Choose the entry surface

| User goal | Primary surface | Supporting state |
| --- | --- | --- |
| Dictate a note | Focused transcript editor | Recording, volatile/final, edit, save |
| Record a memo | Record screen with timer and level | Permission, route, file finalization |
| Transcribe a saved file | Import/open route | File identity, asset readiness, progress |
| Search a recording | Player plus transcript timeline | Time ranges, query, source revision |
| Find sounds | Audio timeline with observation markers | Label, confidence, model revision |
| Summarize a meeting | Final transcript review | Participants/content policy, candidate review |
| Create accessibility text | Source review plus generated candidate | On-device availability, edit, commit |
| Play/export | Native player and destination chooser | File type, share, cancellation, result |

Do not put live capture, transcript editing, sound labels, and destination
choices into one undifferentiated toolbar. Each state has a different risk and
different next action.

## State language is design

Use direct copy:

| State | Useful copy | Avoid |
| --- | --- | --- |
| Permission needed | “Allow microphone access to record.” | “Audio unavailable” |
| Permission denied | “Microphone access is off. You can use an audio file instead.” | A disabled red Record button with no reason |
| Route unavailable | “No microphone route is available.” | “Listening” |
| Listening | “Recording” with elapsed time and input route | Color alone |
| Paused/interrupted | “Recording paused by the system” | Silent waveform |
| Volatile transcript | “Draft transcript” | “Final transcript” |
| Final transcript | “Ready to review” | “Verified” |
| Sound observation | “Detected: applause, 0:14–0:18” | “Applause happened” |
| AI result | “Suggested summary” | “Summary” as if it were source truth |
| Stale candidate | “Source changed; review again” | An enabled Apply button |
| Save | “Save in this app” | “Save” with no destination |

Semantic state should be represented in text, accessibility values, and enabled
actions. A tint, glass treatment, or waveform animation is supplementary.

## Recording anatomy

Use a stable, calm hierarchy:

1. title and source identity;
2. route/permission status;
3. large transcript or waveform;
4. time and current phase;
5. one primary action;
6. secondary actions in a contextual group;
7. optional model/observation review below the source.

For a live recording:

- keep Record/Stop reachable and stable;
- show elapsed time and whether audio is actually flowing;
- identify the current input route when it matters;
- make Pause different from Stop;
- preserve a recoverable draft if the system interrupts;
- avoid a constantly moving glass control group.

For a transcript:

- show volatile text with lighter draft treatment and an explicit label;
- preserve user edits when the next result revises a segment;
- allow keyboard, VoiceOver, and pointer editing;
- keep time-linked text selectable without making timestamps the only cue;
- distinguish transcript from generated title, tags, and summary.

## Waveform and level design

A waveform can orient the person in time, but it should not be the only
recording affordance or a proxy for permission. Use a bounded number of bars or
samples; update at a display-friendly cadence; stop or freeze it on
interruption.

Use:

- stable baseline and playhead;
- readable elapsed/remaining time;
- a pause/stop control with a label;
- a reduced-motion static meter;
- a VoiceOver summary such as “Recording, 00:14, microphone input active.”

Avoid:

- giant undulating glass surfaces;
- a waveform that continues when input is denied;
- a sound label that pops over the subject without time context;
- animated noise that makes transcript reading harder;
- a gesture-only scrubber with no keyboard or accessibility route.

## Transcript and time-linked review

Use a split hierarchy for review:

~~~text
recording identity / duration
    ┌──────────────────────────────┐
    │ native player + playhead     │
    └──────────────────────────────┘
    transcript segment at playhead
    sound observations / confidence
    user edits and review actions
~~~

The player is the time authority for playback. Transcript and sound
observations reference source time ranges. If the audio is trimmed or
transcoded, create a new source revision and re-evaluate ranges. Do not render
old regions over a new file just because the filename is unchanged.

For long transcripts, use lazy content and keep segment identity stable.
Search should seek to a source range, not only highlight a matching string.
Support no-match, partial, stale, and unavailable states.

## Liquid Glass hierarchy

Use small functional groups:

- a top status group for recording/paused/processing/route;
- a bottom action group for Stop, Pause, Retake, and Save;
- a player control group for Play, seek, speed, and output route;
- a review group for Edit, Accept, Discard, Export, and Save;
- a compact AI candidate group marked as suggested.

Glass should float over a stable media/transcript surface and remain legible
over light and dark content. If the surface is visually busy, add an opaque
fallback or content separation rather than more blur.

Keep system-owned audio controls recognizable. Use SF Symbols with labels,
semantic roles, and platform placement. Do not imitate an Apple system control
so closely that a person cannot tell whether the action is app-owned or
system-owned.

Test:

- light/dark mode;
- large and extra-large Dynamic Type;
- Reduce Transparency and increased contrast;
- Reduce Motion;
- VoiceOver and Voice Control;
- keyboard focus and pointer hover;
- iPhone narrow width and iPad split view;
- Catalyst menu/keyboard behavior.

## On-device speech and sound review

The design should communicate three different layers:

1. source: the audio and the user's own transcript edits;
2. observation: framework-produced transcript/sound result with time, model,
   locale, confidence, and revision;
3. proposal: optional on-device generated title, summary, tags, or action.

Place an observation marker near the time range. Place a generated proposal in
a review card with source revision and buttons such as Edit, Accept, and
Discard. Never present an AI summary in the same visual style as a playback
caption or user-authored note.

For unavailable device or locale states:

- keep playback and manual transcript editing available;
- offer imported text or typed input;
- explain asset download state;
- do not imply that a remote service is running unless the product explicitly
  discloses it.

For partial or volatile results, use an explicit draft treatment. For stale
results, remove Apply and offer Review again.

## Privacy design

Microphone permission copy should say why recording is needed. If raw audio is
stored, show the retention/deletion behavior. If only derived text or labels
are stored, say that clearly. If an external service is ever used, make the
destination and user choice explicit before upload.

Keep private data out of:

- diagnostic logs;
- analytics event names and metadata;
- preview fixtures shared with collaborators;
- generated prompts beyond the approved source scope;
- export metadata when the product does not need it.

An on-device model route still needs availability and asset-state language. Do
not convert “the model is intended to run on device” into a universal privacy
guarantee without checking the actual implementation and target.

## Accessibility and alternate input

Every state must be usable without relying on a moving waveform or color.

VoiceOver should expose:

- permission and input route;
- recording/paused/stopped state;
- elapsed time and current transcript certainty;
- player controls and current time;
- observation label, confidence qualifier, and time range;
- AI proposal, source revision, stale state, and actions;
- destination and final result.

Keyboard and pointer should reach Start, Stop, Pause, Play, seek, edit,
accept, discard, save, export, and close. Do not steal focus when a volatile
transcript updates. Return focus to the transcript or review card after an
action. Ensure Dynamic Type does not push Stop or the error action below an
unreachable area. Support RTL and long localized labels.

## Interruption and lifecycle design

Use an explicit banner or inline state for:

- incoming call or system interruption;
- microphone route disconnect;
- audio session activation failure;
- speech assets downloading;
- scene backgrounding;
- cancellation from a new recording;
- transcription failure after a valid recording.

The person should know whether the file is being kept, whether the transcript
can resume, and what action is next. “Resume” should only appear when the
audio/session/analyzer state is actually resumable.

## Target adaptation

| Target | Design emphasis |
| --- | --- |
| iPhone | One-handed recording, clear primary action, live route, compact review |
| iPadOS | Split view, large transcript/player, keyboard/pointer, multitasking |
| Mac Catalyst | File-first workflows, menus/shortcuts, larger review, honest mic support |
| watchOS | Short companion controls/status; hand off long transcript work |
| CarPlay | Driving-safe, system-restricted, concise audio controls only |
| Extension | Small memory/lifetime budget and explicit handoff to the host app |

Do not ship an iPhone camera-style audio screen to every target. Compose the
domain route once and adapt the surface, input, and supported capability per
target.

## Design checklist

- [ ] Source identity and source revision are visible to the model layer.
- [ ] Permission copy is adjacent to the recording intent.
- [ ] Audio route and active state cannot be inferred from color alone.
- [ ] Volatile, final, edited, observation, proposal, and committed states differ.
- [ ] The waveform has a non-gesture, reduced-motion, and accessible fallback.
- [ ] Player, transcript, and observation time ranges share one source revision.
- [ ] AI output is marked as suggested and has Accept/Edit/Discard.
- [ ] Save, Export, Share, and Discard identify their destinations.
- [ ] Liquid Glass controls have task meaning and an opaque fallback.
- [ ] VoiceOver, Dynamic Type, RTL, keyboard, pointer, and reduced-effects cases are designed.
- [ ] Interruption, route change, background, cancellation, and stale-result copy exists.
- [ ] Physical microphone, speech asset, performance, and release proof is planned.

## Sources

- [Speech](https://developer.apple.com/documentation/speech)
- [SpeechAnalyzer](https://developer.apple.com/documentation/speech/speechanalyzer)
- [SpeechTranscriber](https://developer.apple.com/documentation/speech/speechtranscriber)
- [SpeechTranscriber.Preset](https://developer.apple.com/documentation/speech/speechtranscriber/preset)
- [SpeechTranscriber.Result](https://developer.apple.com/documentation/speech/speechtranscriber/result)
- [AssetInventory](https://developer.apple.com/documentation/speech/assetinventory)
- [CaptureInputSequenceProvider](https://developer.apple.com/documentation/speech/captureinputsequenceprovider)
- [AVAudioApplication](https://developer.apple.com/documentation/avfaudio/avaudioapplication)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Handling audio interruptions](https://developer.apple.com/documentation/AVFAudio/handling-audio-interruptions)
- [Responding to audio route changes](https://developer.apple.com/documentation/AVFAudio/responding-to-audio-route-changes)
- [AVAudioEngine](https://developer.apple.com/documentation/avfaudio/avaudioengine)
- [AVAudioNode](https://developer.apple.com/documentation/avfaudio/avaudionode)
- [AVAudioPCMBuffer](https://developer.apple.com/documentation/avfaudio/avaudiopcmbuffer)
- [AVKit](https://developer.apple.com/documentation/avkit)
- [VideoPlayer](https://developer.apple.com/documentation/avkit/videoplayer)
- [Sound Analysis](https://developer.apple.com/documentation/soundanalysis)
- [SNClassificationResult](https://developer.apple.com/documentation/soundanalysis/snclassificationresult)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adding intelligent app features with generative models](https://developer.apple.com/documentation/foundationmodels/adding-intelligent-app-features-with-generative-models)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
