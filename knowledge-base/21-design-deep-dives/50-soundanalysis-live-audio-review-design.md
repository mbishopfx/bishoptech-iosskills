# SoundAnalysis live-audio and review design

SoundAnalysis UI should communicate that the app is observing an audio stream and producing model candidates over time. A native design makes permission, listening state, model identity, confidence, uncertainty, and retention visible without pretending that a label is ground truth.

## Design the listening contract first

Before drawing a waveform or glass card, define:

- when the microphone turns on;
- what the app is listening for;
- whether input is live or a saved file;
- which model and revision is active;
- what labels are allowed;
- how confidence is shown;
- how long raw audio and derived labels remain;
- what action, if any, requires review;
- how stop, pause, interruption, denial, and format changes appear.

The start action should be user-visible and reversible. Never imply that the app is listening when permission, input, engine, or analyzer state is not ready.

## Surface ownership

| Surface | Purpose |
| --- | --- |
| Permission explainer | Why microphone input is needed and what is retained |
| Listening shell | Live/paused/stopped/input route state |
| Candidate card | Current label, confidence qualifier, time range, uncertainty |
| Timeline | Reviewable sound moments tied to a recording or analysis session |
| Model settings | Model revision, labels, threshold, delete/reset |
| AI review | User-selected results summarized or proposed for tagging |
| Privacy sheet | Raw audio, derived labels, network processing, deletion |

Do not make a constantly changing prediction the only visual signal. VoiceOver and alternate input need a stable semantic state.

## State design

| State | Design language |
| --- | --- |
| Permission needed | Explain microphone purpose; keep Start unavailable until appropriate |
| Permission denied | Offer manual/file route and Settings guidance without looping prompts |
| Input unavailable | State that the current device/route has no usable input |
| Preparing | Show setup, not “Listening” |
| Listening | Show active status, input route, stop action, and privacy cue |
| Paused/interrupted | Preserve last known candidate as historical, not current |
| Reconfiguring | Explain that the input format changed and analysis is restarting |
| Candidate | Label with confidence qualifier and time |
| Ambiguous | Show competing or uncertain result; no consequential action |
| Failed | Explain recovery and preserve no false result |
| Stopped | Show the session ended and what was retained |

Use “candidate,” “likely,” or “not enough signal” where the product policy requires uncertainty. Avoid percentages without explaining what they represent.

## Live card anatomy

A native live-analysis card can contain:

- a microphone/privacy indicator;
- Listening, Paused, or Stopped;
- input route such as built-in microphone or connected input;
- current candidate label;
- confidence qualifier or uncertainty;
- time since last stable result;
- Stop and Pause actions;
- a link to the timeline or review;
- a clear delete/forget action when a session is retained.

Keep the label readable over a stable background. A subtle Liquid Glass group can organize controls; it should not put every classification, waveform, model setting, and privacy detail in nested translucent panels.

## Liquid Glass application

Use Liquid Glass for app-owned state and controls:

- compact listening toolbar;
- current candidate/status pill;
- filter or model-selection controls;
- review actions.

Use a solid fallback when:

- Reduce Transparency is enabled;
- increased contrast is active;
- artwork or background audio visualization reduces text contrast;
- Dynamic Type makes the card taller;
- VoiceOver is active;
- the device or deployment target does not support the selected material.

The material should support hierarchy, not become the product’s main feedback channel.

## Timeline and review design

A timeline entry should show:

1. time range;
2. candidate label;
3. confidence qualifier;
4. model revision;
5. user decision: keep, edit, dismiss, or unknown;
6. source recording or session reference;
7. retention and deletion behavior.

If the user taps a timeline entry, play or scrub the relevant audio only when the product has a clear permission and retention policy. Do not turn a derived label into a permanent fact without an explicit user action when the domain is sensitive.

## File-analysis design

For saved recordings:

- show which file is being analyzed;
- provide cancel;
- separate analysis progress from audio playback;
- show completion, partial, canceled, and failed states;
- offer review before adding tags or timestamps;
- retain raw audio only according to the recording feature’s policy;
- keep model revision visible in exports or audit records when relevant.

Do not show a determinate progress bar when the file duration or analyzer work cannot support one.

## Permission and privacy

The microphone explanation should say:

- what sound category the app is analyzing;
- whether raw audio is stored;
- whether labels or time ranges are stored;
- whether any data leaves the device;
- how to stop and delete the session.

The app should remain useful after denial: manual tagging, saved-file import, demo fixtures, or an explanation of the unavailable feature. A permission denial is not a model error.

## AI review design

AI should operate on an approved result timeline or user-selected audio/text, not silently on the entire microphone stream.

Use this sequence:

user chooses result scope -> app shows source/model context -> bounded local analysis -> AI proposal -> review -> save/tag/share

Examples:

- “Summarize the sounds in this recording” yields a draft summary with timestamps.
- “Add the stable applause moments” yields a reviewable tag proposal.
- “Alert me when the machine sounds abnormal” requires a separate deterministic policy and should not be promised from a generic classifier.

Do not use a generated explanation to hide low confidence or model disagreement.

## Accessibility and alternate input

Test:

- VoiceOver announces listening, paused, candidate, confidence qualifier, last-update time, input route, and action result;
- Dynamic Type keeps Stop, Pause, Review, and Delete reachable;
- Voice Control and Switch Control can start, stop, pause, review, and reject a candidate;
- the waveform or animated meter is not the only evidence of activity;
- reduced motion keeps state changes understandable;
- increased contrast distinguishes active, paused, unavailable, and error states;
- localization handles long labels and right-to-left layout;
- the timeline has logical focus movement after new results arrive;
- audio playback and screen-reader speech do not create an unusable feedback loop.

## Design proof

Complete a real task:

- grant microphone access;
- start and stop listening;
- change the audio route;
- interrupt and resume;
- trigger a stable, ambiguous, and low-confidence fixture;
- change input format and rebuild the analyzer;
- analyze a saved recording and cancel it;
- delete raw audio and derived labels;
- review an AI summary with prompt-injection text;
- repeat with VoiceOver, Dynamic Type, reduced transparency, and offline state.

## Sources

- [Sound Analysis](https://developer.apple.com/documentation/soundanalysis)
- [SNClassifySoundRequest](https://developer.apple.com/documentation/soundanalysis/snclassifysoundrequest)
- [SNAudioStreamAnalyzer](https://developer.apple.com/documentation/soundanalysis/snaudiostreamanalyzer)
- [SNAudioFileAnalyzer](https://developer.apple.com/documentation/soundanalysis/snaudiofileanalyzer)
- [SNResultsObserving](https://developer.apple.com/documentation/soundanalysis/snresultsobserving)
- [SNClassificationResult](https://developer.apple.com/documentation/soundanalysis/snclassificationresult)
- [Classifying Sounds in an Audio Stream](https://developer.apple.com/documentation/soundanalysis/classifying-sounds-in-an-audio-stream)
- [Classifying Sounds in an Audio File](https://developer.apple.com/documentation/soundanalysis/classifying-sounds-in-an-audio-file)
- [MLSoundClassifier](https://developer.apple.com/documentation/createml/mlsoundclassifier)
- [AVAudioEngine](https://developer.apple.com/documentation/avfaudio/avaudioengine)
- [AVAudioNode](https://developer.apple.com/documentation/avfaudio/avaudionode)
- [AVAudioInputNode](https://developer.apple.com/documentation/avfaudio/avaudioinputnode)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [AVAudioApplication](https://developer.apple.com/documentation/avfaudio/avaudioapplication)
- [NSMicrophoneUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsmicrophoneusagedescription)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
