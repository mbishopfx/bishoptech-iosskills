# SoundAnalysis and on-device audio classification

SoundAnalysis provides Apple’s route for identifying sounds in an audio file or stream. An app creates an SNClassifySoundRequest with Apple’s built-in sound classifier or a custom Core ML model, adds it to an SNAudioFileAnalyzer or SNAudioStreamAnalyzer, and receives time-ranged classifications through an SNResultsObserving implementation.

Use this deep dive when an app needs to:

- tag sounds in a saved recording;
- show live sound labels from a microphone stream;
- detect a bounded sound vocabulary such as laughter, applause, music, alarms, or a product-specific event;
- train a custom sound classifier with Create ML and run it through SoundAnalysis;
- keep audio analysis local to the device when the target’s model and data path support that policy;
- design a confidence-aware, reviewable audio intelligence surface rather than treating a prediction as fact.

SoundAnalysis is a classification route, not a medical diagnostic, speaker-identity system, consent mechanism, recording archive, or proof that a physical event occurred.

## Choose the analyzer

| Need | Analyzer | Input/lifecycle |
| --- | --- | --- |
| Analyze a saved recording | SNAudioFileAnalyzer | URL to a Core Audio-supported file; synchronous or asynchronous analysis |
| Analyze microphone or another PCM stream | SNAudioStreamAnalyzer | AVAudioFormat plus buffers and frame positions |
| Use Apple’s built-in sound vocabulary | SNClassifySoundRequest with a classifier identifier | Request knows supported classifications |
| Use product-specific sounds | SNClassifySoundRequest with a custom MLModel | Bundle and verify the model in the selected target |
| Add multiple sound requests | One analyzer with multiple requests | Keep observers and request lifecycle explicit |
| Stop live analysis | Remove request or discard analyzer | Stop the input tap/engine and reconcile state |

Do not use the file analyzer for live microphone buffers or the stream analyzer with a non-PCM file path. The official stream route requires PCM audio data.

## Canonical pipeline

Use one pipeline with explicit ownership:

microphone or file -> permission/input route -> AVAudioSession -> AVAudioEngine or file URL -> PCM format -> SoundAnalysis request -> analyzer -> observer -> confidence/time-range reducer -> app state

The app owns:

- the user-facing permission explanation and recording/analysis intent;
- microphone and audio-session lifecycle;
- the audio buffer source and format transition;
- request and observer references;
- confidence threshold, debounce, persistence, and deletion policy;
- user-visible interpretation and any consequential action;
- AI/context boundary and fallback.

The frameworks own:

- audio input and engine mechanics;
- model request execution;
- classification candidates and time ranges;
- analyzer completion and error callbacks.

The framework result is not the app’s domain truth. A result must pass product policy before it becomes a tag, notification, automation, or saved record.

## SNClassifySoundRequest

The request can use:

- SNClassifierIdentifier.version1 for the built-in classifier route;
- a custom MLModel created from a product-specific sound classifier;
- knownClassifications for the model’s supported label set;
- windowDuration and overlapFactor for analysis-window behavior;
- windowDurationConstraint for supported duration boundaries.

A label is meaningful only in the context of its model, window, input format, environment, and threshold policy. Keep the request configuration in a target register and record the model revision.

Recommended request record:

| Field | Record |
| --- | --- |
| Model | Built-in classifier identifier or custom model name |
| Model revision | Bundle version, hash, or generated Core ML metadata |
| Known labels | Allowlisted domain labels used by the app |
| Window | Duration and overlap factor |
| Input | Sample rate, channel count, PCM format |
| Threshold | Product threshold and calibration fixture |
| Output policy | UI-only, tag draft, notification proposal, or automation proposal |
| Privacy | Raw audio retention, derived labels, deletion, external processing |

Do not assume the built-in classifier’s label list is a stable domain contract across SDK or OS revisions. Compare the selected target’s supported labels and keep unknown labels harmless.

## Audio file analysis

The file route is:

1. obtain a user-authorized or app-owned audio URL;
2. verify that the file is within the feature’s size and retention policy;
3. create SNAudioFileAnalyzer with the URL;
4. create the sound request;
5. retain an observer strongly;
6. add the request with the observer;
7. call analyze or analyze(completionHandler:);
8. map SNClassificationResult values to redacted domain events;
9. support cancellation;
10. remove requests and release file access when the feature ends.

The observer receives results with a time range and ranked classifications. The asynchronous completion result says whether analysis reached the end; it is not a quality score or proof that every sound was detected.

File analysis is useful for searchable metadata and timestamped moments. It should not silently upload a recording or persist sensitive sound labels without a product policy.

## Live stream analysis

The stream route is:

1. request microphone access at the feature boundary;
2. configure and activate the audio session for input;
3. inspect input availability and the input node’s hardware format;
4. create an SNAudioStreamAnalyzer with the current PCM format;
5. retain a results observer;
6. add the request;
7. install an input-node audio tap;
8. pass each PCM buffer to analyze with its frame position;
9. reduce and debounce classifications;
10. remove the tap, request, and analyzer on stop.

If the input device’s audio format changes, discard the current stream analyzer and create a new analyzer that matches the updated format. Do not continue feeding buffers from a new format into an analyzer created for the old format.

The audio tap callback is a real-time-adjacent path. Avoid blocking I/O, unbounded allocations, synchronous network calls, heavy logging, or model-side effects inside the tap. Move classification reduction and UI updates to a controlled queue/actor.

## Results and confidence

SNClassificationResult contains:

- a CMTimeRange for the analyzed audio span;
- a sorted set of top SNClassification candidates;
- a classification identifier;
- a confidence value.

Confidence is a model score, not certainty. Product policy should define:

| Result condition | App state |
| --- | --- |
| High confidence, stable across windows | Candidate event |
| High confidence, one short window | Pending candidate |
| Competing labels | Ambiguous |
| Low confidence | Unknown/no-action |
| No result in expected time | Stale or unavailable |
| Input interrupted | Pause analysis and preserve uncertainty |
| Format changed | Reconfigure; do not merge incompatible windows |

Use temporal debounce, hysteresis, or a review step for actions. Do not turn one classification into a notification, alarm, or external command without an explicit product rule.

## Microphone and audio-session gates

Microphone access requires the NSMicrophoneUsageDescription purpose string. The current audio-permission route uses AVAudioApplication; older AVAudioSession permission methods may be deprecated in the selected SDK.

Keep these states separate:

| State | Meaning |
| --- | --- |
| permission-not-determined | The app has not received the user’s recording decision |
| permission-denied | The user or system denies microphone input |
| input-unavailable | Target route has no usable audio input |
| session-configured | Category/mode/options are set |
| session-active | Audio session activation succeeded |
| engine-running | AVAudioEngine is running and delivering buffers |
| analyzer-ready | Analyzer format matches the current input |
| analyzing | Buffers are being submitted |
| interrupted | Audio session or route interrupted analysis |
| stopped | Tap, request, and analyzer are torn down |

A permission grant does not prove that a microphone route is currently available. An input route does not prove that the engine is running. An analyzer result does not prove a physical event.

## Custom sound classifiers

Create ML’s MLSoundClassifier can train a sound-classification model from audio data. Apple’s documentation recommends representative examples for each sound and a negative class for background or irrelevant noise. Training data quality, class balance, recording conditions, and model evaluation determine what the output means.

The model pipeline is:

dataset and negative class -> Create ML training/evaluation -> Core ML model -> Xcode target resource -> MLModel -> SNClassifySoundRequest -> analyzer

Record:

- the dataset source and consent;
- class definitions and negative class;
- train/validation/test split;
- recording environment and microphone/device variation;
- model revision and generated metadata;
- error cases and rejection threshold;
- privacy and deletion of source recordings.

Do not market a classifier as detecting a condition, intent, person, or emergency unless the product has evidence and review appropriate to that claim. SoundAnalysis output alone is not medical or safety validation.

## On-device AI boundary

Bundled Core ML models and SoundAnalysis requests can support a local inference path. Verify the actual target and inspect the implementation before claiming that audio never leaves the device.

Keep raw audio separate from derived labels:

| Data | Default handling |
| --- | --- |
| Microphone PCM | Process transiently; do not retain unless explicitly needed |
| Saved audio | Use a scoped URL and deletion policy |
| Classification label | Store only if the user-facing feature needs it |
| Confidence/time range | Retain with model revision and uncertainty |
| AI summary | Mark as generated interpretation, not sensor truth |
| External request | Off by default for sensitive audio; require explicit policy |

AI may summarize a user-approved result timeline or propose a tag. It cannot upgrade low confidence, infer consent, or claim that a physical event occurred.

## Native Liquid Glass design

Use Liquid Glass around app-owned analysis state:

- listening/paused/stopped status;
- current candidate label with confidence qualifier;
- input route and privacy indicator;
- reviewable timeline of detected moments;
- model/settings and delete controls.

Keep the primary content readable and avoid a wall of rapidly changing translucent labels. Provide a solid fallback for reduced transparency, increased contrast, Dynamic Type, VoiceOver, and no-microphone states.

## Lifecycle and fallback

| Condition | Fallback |
| --- | --- |
| Permission denied | Keep saved-file or manual-label features; explain Settings path if useful |
| No input route | Show unavailable state; do not start engine blindly |
| Engine start fails | Stop tap, report recoverable error, preserve no false “listening” state |
| Input format changes | Stop and recreate analyzer for the new format |
| Audio interruption | Pause/stop analysis and reconcile after the route decision |
| Observer deallocated | Keep a strong owner or stop the request |
| Analyzer error | Mark analysis failed/unknown; do not emit domain success |
| Low confidence | Show candidate/unknown or require review |
| Model missing | Disable classifier feature and offer deterministic alternatives |
| Device resource pressure | Lower scope or stop; preserve user control |
| AI unavailable | Keep raw classification review and manual tags |

## Proof boundary

| Claim | Required evidence |
| --- | --- |
| Microphone permission is configured | Signed target, purpose string, physical permission path |
| Input is available | Physical route, AVAudioSession/AVAudioApplication state, hardware format |
| Live analysis works | Physical device, real input, engine/tap, analyzer, time-ranged result |
| File analysis works | Fixture URL, analyzer completion, observer result, cancellation |
| Custom classifier works | Model in target, model revision, known labels, evaluation fixture |
| Confidence policy works | Boundary fixtures, debouncing/hysteresis, ambiguous/unknown state |
| Format change recovery works | Route/input change, analyzer recreation, no mixed-format result |
| Privacy works | Raw-audio retention/deletion test, redacted logs, network policy |
| AI is bounded | Typed context/proposal, prompt boundary, confirmation/rejection |
| Accessibility works | VoiceOver, Dynamic Type, alternate input, contrast/reduced effects |
| Release is ready | Final signed model/resource target, privacy review, physical evidence |

## Sources

- [Sound Analysis](https://developer.apple.com/documentation/soundanalysis)
- [SNClassifySoundRequest](https://developer.apple.com/documentation/soundanalysis/snclassifysoundrequest)
- [SNAudioStreamAnalyzer](https://developer.apple.com/documentation/soundanalysis/snaudiostreamanalyzer)
- [SNAudioFileAnalyzer](https://developer.apple.com/documentation/soundanalysis/snaudiofileanalyzer)
- [SNResultsObserving](https://developer.apple.com/documentation/soundanalysis/snresultsobserving)
- [SNClassificationResult](https://developer.apple.com/documentation/soundanalysis/snclassificationresult)
- [Classifying Sounds in an Audio Stream](https://developer.apple.com/documentation/soundanalysis/classifying-sounds-in-an-audio-stream)
- [Classifying Sounds in an Audio File](https://developer.apple.com/documentation/soundanalysis/classifying-sounds-in-an-audio-file)
- [Classifying Live Audio Input with a Built-in Sound Classifier](https://developer.apple.com/documentation/SoundAnalysis/classifying-live-audio-input-with-a-built-in-sound-classifier)
- [MLSoundClassifier](https://developer.apple.com/documentation/createml/mlsoundclassifier)
- [Core ML](https://developer.apple.com/documentation/coreml)
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
