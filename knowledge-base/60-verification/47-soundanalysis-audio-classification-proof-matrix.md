# SoundAnalysis audio-classification proof matrix

SoundAnalysis crosses microphone permission, audio-session/input route, AVAudioEngine buffers, analyzer format, Core ML model resources, observer lifecycle, time-ranged predictions, confidence policy, privacy, accessibility, and any resulting side effect. Verify each claim at its actual boundary.

This matrix does not treat a model file, a simulator callback, a classification label, or a rendered waveform as proof of microphone access, physical sound, model accuracy, medical meaning, user consent, or release readiness.

## Test record

| Field | Record |
| --- | --- |
| Target | Bundle ID, target membership, deployment target, SDK |
| Privacy | NSMicrophoneUsageDescription text and permission state |
| Device | Physical iPhone/iPad, OS build, microphone/input route |
| Audio | AVAudioSession category/mode/activation, format, sample rate, channels |
| Source | Live input tap or file fixture URL, duration, provenance |
| Analyzer | File/stream analyzer, request, observer owner |
| Model | Built-in identifier or custom Core ML model, revision, label set |
| Policy | Threshold, overlap/window, debounce/hysteresis, stale interval |
| Output | Candidate/tag/notification/automation policy |
| Privacy | Raw audio retention, derived labels, deletion, external processing |
| Accessibility | VoiceOver, Dynamic Type, alternate input, reduced effects |
| Artifact | Signed model/resource, entitlements/plist, release metadata |

Use consented, synthetic, or redacted recordings. Do not put private speech, room identifiers, device names, or raw PCM in shared logs.

## Claim-to-evidence matrix

| Claim | Minimum evidence | Does not prove it |
| --- | --- | --- |
| Microphone purpose is configured | Signed target with NSMicrophoneUsageDescription | A source plist line |
| Permission is granted | Physical permission prompt/Settings state and runtime result | A mock permission enum |
| Input route is available | Physical route, inputAvailable, hardware format with nonzero values | Permission grant |
| Audio session is active | Configuration and activation result on target | Calling setActive in source |
| Engine delivers buffers | Physical input tap, frame positions, format record | Engine object creation |
| Stream analyzer is correct | Analyzer format matches current PCM input | An analyzer instance |
| Format change recovers | Route/input change, analyzer teardown/recreation, post-change results | Changing a UI label |
| File analysis works | Fixture URL, request, observer result, completion/cancel | A model file in the bundle |
| Observer remains live | Strong owner and results/failure callbacks | An observer type declaration |
| Built-in classifier works | Named device/SDK, positive/negative/noise fixtures, result timeline | Known classification list |
| Custom model is shipped | Signed target resource, model revision, wrapper/request creation | File in the source tree |
| Confidence policy works | Calibrated fixtures at threshold, debounce, ambiguous/unknown states | A hard-coded threshold |
| Tag or alert is safe | Stable result, allowlisted label, review/confirmation, domain result | One high-confidence callback |
| Privacy policy works | Raw-audio retention/deletion, redacted logs, network inspection/policy | A privacy statement |
| AI is bounded | Selected result context, prompt-injection fixture, typed proposal, rejection | A generated summary |
| Accessibility works | Completed VoiceOver/Dynamic Type/alternate-input tasks | Labels in SwiftUI source |
| Release is ready | Final signed artifact, target resources, physical evidence, privacy review | Debug/simulator output |

## Live-stream scenarios

- [ ] Permission not determined, granted, denied, and changed in Settings are distinct.
- [ ] No input route is visible as unavailable rather than listening.
- [ ] Built-in microphone input reports a nonzero sample rate and channel count.
- [ ] Connected microphone/headset route is identified and tested if supported.
- [ ] Audio session configuration and activation succeed.
- [ ] AVAudioEngine starts and the input tap delivers PCM buffers.
- [ ] Stream analyzer format matches the tap’s current format.
- [ ] Request and observer are added successfully.
- [ ] Results contain a time range and ranked classifications.
- [ ] Silence, background noise, overlapping sounds, and target sounds are tested.
- [ ] Low-confidence and competing labels remain uncertain.
- [ ] Input format changes stop the old analyzer and create a matching one.
- [ ] Interruption and route changes do not leave a stale listening indicator.
- [ ] Stop removes the tap, requests, analyzer, engine, and sensitive state.
- [ ] The input callback does not perform blocking I/O or network work.

## File-analysis scenarios

| Scenario | Expected evidence |
| --- | --- |
| Valid supported audio file | Analyzer creates, request adds, observer receives time-ranged results |
| Empty/short file | Safe completion or failure with no false label |
| Unsupported/corrupt URL | Error state and retry/delete path |
| Large file | Bounded progress/cancel and resource policy |
| Multiple requests | Named requests, distinct observers, predictable output |
| Cancellation | cancelAnalysis returns incomplete/false outcome and UI recovers |
| Observer lifecycle | Strong observer receives result/failure/completion |
| Deletion | Raw file and derived labels follow retention policy |
| Model revision change | Results retain the model identity and are not silently mixed |

## Model and confidence scenarios

- [ ] Built-in classifier label list is inspected in the selected target.
- [ ] Custom model has a revision and signed resource record.
- [ ] Every class has representative positive fixtures.
- [ ] A negative/background class is present for custom training where appropriate.
- [ ] Device and environmental variation are included.
- [ ] The test set is separate from training examples.
- [ ] Threshold is calibrated for the intended task.
- [ ] Debounce/hysteresis prevents rapid false transitions.
- [ ] Unknown/ambiguous state is reachable and accessible.
- [ ] Model error or missing model disables side effects.
- [ ] No label is presented as medical, safety, identity, or physical certainty without separate evidence.

## Privacy, AI, and side-effect checks

- [ ] The microphone purpose explains the live analysis behavior.
- [ ] Raw PCM retention and deletion are explicit.
- [ ] Derived labels/time ranges have a separate retention policy.
- [ ] Logs redact audio content, file paths, device names, and sensitive labels.
- [ ] External processing is disabled or governed explicitly.
- [ ] AI receives only a user-approved, bounded result timeline.
- [ ] Remote or model-generated instructions cannot call native actions.
- [ ] Labels, time ranges, and model revision are validated before a tag or alert.
- [ ] Consequential actions require confirmation and a recoverable result.
- [ ] Unknown/stale outcomes are never upgraded to success.

## Accessibility and Liquid Glass matrix

- [ ] VoiceOver announces permission, listening state, input route, candidate, uncertainty, and actions.
- [ ] Dynamic Type keeps Stop, Pause, Review, Delete, and Retry reachable.
- [ ] Voice Control and Switch Control reach the full task without relying on waveform gestures.
- [ ] Reduced motion preserves state changes and timeline updates.
- [ ] Reduced transparency and increased contrast preserve active/error/unknown meaning.
- [ ] App-owned Liquid Glass analysis controls remain readable over visualizations.
- [ ] Localized labels, long sound names, RTL, keyboard, pointer, and focus return work.

## Evidence vocabulary

| Term | Meaning |
| --- | --- |
| permitted | Runtime microphone permission is granted for the target |
| input-available | Audio session reports a usable input route |
| format-ready | Analyzer format matches the current PCM source |
| listening | Engine/tap/analyzer are active according to recorded state |
| candidate | Classification passed the app’s presentation threshold |
| stable | Candidate passed temporal debounce/hysteresis policy |
| ambiguous | Multiple or competing candidates remain unresolved |
| unknown | No supported or sufficiently confident result is proven |
| analyzed | File/stream buffers were processed by the analyzer |
| completed | File analyzer reached its end; not a quality guarantee |
| applied | A validated, user-allowed domain action occurred |
| local | The inspected implementation/model path did not send audio externally |
| physical | Evidence came from the named device and real input route |

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
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
