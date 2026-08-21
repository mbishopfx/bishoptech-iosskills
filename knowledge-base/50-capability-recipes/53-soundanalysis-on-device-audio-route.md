# SoundAnalysis on-device audio intelligence route

Use this route for live microphone sound classification, saved-file sound tagging, or a custom Core ML sound classifier. Keep the audio source, analyzer format, model request, observer, confidence policy, and user-facing side effect separate.

This is a compile-oriented route blueprint. It does not prove microphone permission, physical input, model accuracy, audio-route behavior, classifier quality, privacy, accessibility, or release readiness.

## Route selector

| Goal | Route | Boundary |
| --- | --- | --- |
| Classify a saved recording | SNAudioFileAnalyzer | File URL, cancellation, observer, time ranges |
| Classify live microphone audio | AVAudioEngine input tap plus SNAudioStreamAnalyzer | Permission, audio session, PCM format, teardown |
| Use Apple’s built-in vocabulary | SNClassifySoundRequest with classifier identifier | Model labels and OS/SDK version |
| Use product-specific labels | Create ML MLSoundClassifier and custom MLModel | Dataset, model resource, calibration, evaluation |
| Show a candidate label | Confidence/time-range reducer | No automatic claim or side effect |
| Create an alert or automation | Deterministic domain policy after stable result | Consent, threshold, confirmation, proof |
| Summarize results | On-device AI over a redacted result timeline | Generated interpretation, not sensor truth |

Do not make a generic sound classifier the authority for safety, health, medical, identity, or irreversible device actions.

## Target register

| Field | Required decision |
| --- | --- |
| Target | Bundle ID, deployment target, SDK, device family |
| Permission | NSMicrophoneUsageDescription and current audio permission API |
| Audio session | Category, mode, activation, interruption, input route |
| Source | File URL or AVAudioEngine input node |
| Format | Sample rate, channels, PCM format, route-change behavior |
| Analyzer | File or stream analyzer; request ownership |
| Model | Built-in identifier or bundled custom Core ML model revision |
| Labels | Allowlisted labels, unknown-label policy |
| Threshold | Confidence, debounce, hysteresis, stale interval |
| Retention | Raw audio, derived labels, time ranges, delete path |
| AI | Approved result context, proposal schema, confirmation |
| Evidence | Physical microphone/route, fixtures, target artifact, accessibility |

## Ownership graph

SwiftUI -> AnalysisStore -> AudioCaptureCoordinator -> AVAudioSession/AVAudioEngine -> SNAudioStreamAnalyzer -> ResultObserver -> classification reducer

Saved file -> scoped URL access -> SNAudioFileAnalyzer -> ResultObserver -> timestamp/tag review

Classification result -> threshold/debounce policy -> candidate state -> user review -> durable tag/notification/automation

AI request -> redacted result timeline -> typed proposal -> deterministic validator -> confirmation -> app-owned side effect

The audio tap must not directly mutate SwiftUI or call a network service. Use a bounded handoff to the analysis owner.

## Route A: file analyzer

1. Confirm the file is authorized and within size/retention limits.
2. Create SNAudioFileAnalyzer with the URL.
3. Create a built-in or custom SNClassifySoundRequest.
4. Keep an observer strongly referenced.
5. Add the request with the observer.
6. Start synchronous or asynchronous analysis according to the feature.
7. Process time-ranged results on a controlled queue/actor.
8. Support cancelAnalysis.
9. Remove requests and release file access.
10. Store only reviewed, policy-approved labels.

Do not confuse completion true with perfect classification or completion false with an empty file. Record cancellation and observer errors distinctly.

## Route B: live PCM analyzer

1. Explain microphone use and request permission.
2. Configure the audio session for input.
3. Activate only when the user starts analysis.
4. Confirm inputAvailable and a nonzero hardware sample rate/channel count.
5. Create AVAudioEngine and inspect the input node format.
6. Create SNAudioStreamAnalyzer with that exact AVAudioFormat.
7. Create and retain the results observer.
8. Add the sound request.
9. Install an input-node tap.
10. Feed PCM buffers and frame positions to analyze.
11. Reduce results outside the tap’s time-sensitive callback.
12. On stop, remove the tap, remove requests, stop the engine, and clear state.

If input format changes, stop and recreate the analyzer for the new format. Do not attempt to repair an existing analyzer by changing only a UI label.

## Route C: request configuration

Configure:

- built-in classifier identifier or custom model;
- window duration within the request’s constraint;
- overlap factor appropriate for latency and compute budget;
- known label allowlist;
- model revision and target resource.

Keep model settings in a value record:

~~~swift
struct SoundModelConfiguration: Sendable, Equatable {
    let modelID: String
    let revision: String
    let labels: Set<String>
    let minimumConfidence: Double
    let debounceWindows: Int
}
~~~

Do not claim that a model recognizes a label merely because the label exists in knownClassifications. Test representative positives, negatives, silence, overlapping sounds, route changes, and environmental noise.

## Route D: result reducer

Map framework output to an uncertainty-preserving state:

~~~swift
struct SoundCandidate: Sendable, Equatable {
    let identifier: String
    let confidence: Double
    let startSeconds: Double
    let endSeconds: Double
    let modelRevision: String
}

enum SoundObservation: Sendable, Equatable {
    case listening
    case candidate(SoundCandidate)
    case ambiguous([SoundCandidate])
    case unknown
    case interrupted
    case failed(String)
}
~~~

Use temporal stability, not one callback, to promote a candidate. The exact policy is product-owned and must be calibrated with fixtures.

## Route E: permission and audio session

Use the current AVAudioApplication permission route in the selected SDK and include NSMicrophoneUsageDescription. Configure AVAudioSession only after the user starts the feature when possible.

Separate:

- permission granted;
- input route available;
- audio session configured;
- audio session active;
- engine running;
- analyzer format ready;
- result currently fresh.

On denial or no route, retain manual/file features and never show a listening state.

## Route F: custom model resource

For a custom classifier:

1. create and consent the dataset;
2. include representative categories and a negative/background class;
3. train and evaluate with Create ML;
4. export the Core ML model;
5. add it to the target’s resources;
6. verify the generated wrapper/model resource in the signed artifact;
7. create SNClassifySoundRequest with the model;
8. record model revision and supported labels;
9. calibrate thresholds on held-out fixtures;
10. provide a model-missing fallback.

Model quality is a separate evidence packet from API wiring. Do not use training metrics as proof of real-world device performance.

## Route G: privacy and bounded AI

Default to:

- process live PCM transiently;
- store no raw audio unless a recording feature requires it;
- store derived labels only with user-visible purpose;
- redact labels and time ranges before external processing;
- let AI summarize a selected result scope;
- require confirmation for tags, notifications, or automation.

Example proposal:

~~~swift
enum SoundActionProposal: Sendable, Equatable {
    case addTag(label: String, timeRange: ClosedRange<Double>)
    case draftSummary
    case notifyReview
}
~~~

Validate that the label is allowlisted, the time range belongs to the selected recording, confidence policy passed, and the user confirmed any consequential action.

## Fallback matrix

| Condition | Safe fallback |
| --- | --- |
| Permission denied | Manual labels, file import, or Settings guidance |
| Input unavailable | No listening state; explain route |
| Session activation fails | Stop and show recoverable error |
| Engine start fails | Remove tap and preserve no result |
| Format changes | Recreate analyzer and mark transition |
| Analyzer throws | Mark analysis unavailable and allow retry |
| Observer loses ownership | Stop request or restore strong owner |
| Low confidence | Unknown/candidate review, no side effect |
| Model missing | Disable custom route and offer built-in/manual feature |
| Thermal/resource pressure | Lower scope or stop with explanation |
| AI unavailable | Keep deterministic classification review |

## Evidence route

Capture:

1. signed permission purpose string and target configuration;
2. physical input route, permission state, and audio-session state;
3. live PCM format and analyzer recreation after a route/format change;
4. file analyzer result, cancellation, and observer failure;
5. built-in/custom model resource and revision;
6. positive, negative, silence, ambiguous, low-confidence, and noisy fixtures;
7. threshold/debounce behavior and no-side-effect boundary;
8. raw-audio retention/deletion and redacted logs;
9. AI proposal/rejection/confirmation;
10. accessibility, Liquid Glass fallback, physical device, and final signed artifact.

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
