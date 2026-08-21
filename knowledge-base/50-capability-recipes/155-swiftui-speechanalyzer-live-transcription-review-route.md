# SwiftUI SpeechAnalyzer live transcription review route

Use this route when the product outcome is “capture or import speech, show a trustworthy live transcript, and optionally turn an accepted transcript into a structured on-device AI proposal.” It is intentionally narrower than the [generic audio capture/transcription route](120-swiftui-audio-capture-and-transcription-route.md) and should be chosen when the iOS 26 SpeechAnalyzer actor, module results, locale assets, volatile range, or finalization semantics are central to the feature.

The route is:

~~~text
outcome
  -> target and data-flow contract
  -> microphone permission / audio-session readiness
  -> SpeechTranscriber locale and model asset readiness
  -> input provider or bounded AnalyzerInput stream
  -> SpeechAnalyzer analysis task
  -> volatile/final result reducer
  -> SwiftUI source review
  -> optional typed AI proposal
  -> deterministic validation and explicit commit
  -> physical-device and signed-release proof
~~~

## 1. Select the lane before writing UI

| Outcome | Start here | Add only when justified |
| --- | --- | --- |
| Live microphone transcript | `SpeechAnalyzer` + `SpeechTranscriber` + AVAudio input | `SpeechDetector`, `CaptureInputSequenceProvider`, `AnalyzerInputConverter` |
| Audio-file transcript | `AssetInputSequenceProvider` or `SpeechAnalyzer(inputAudioFile:)` | Time-range editing, batch export |
| Voice-activated transcription | `SpeechDetector` with a transcriber | Sensitivity tuning and false-negative fixtures |
| Older OS fallback | Existing `SFSpeechRecognizer` adapter or file import | Separate server/privacy/authorization contract |
| Transcript summary or extraction | Foundation Models after final review | `@Generable` typed proposal and source-range validation |
| Playback of source audio | AVFoundation/AVKit | A separate player and source-time mapping contract |

Do not add Foundation Models to the capture callback. Do not use a server transcription path simply because the local model is not ready without making the data-flow change visible and obtaining the product’s required consent.

## 2. Route contract

Write these decisions in the feature record:

| Contract | Decision to record |
| --- | --- |
| Supported target | iOS 26 deployment target, device family, final SDK, and beta API policy |
| Input | Microphone, `AVAsset`, file, or another source; expected sample format and time base |
| Locale | Requested locale, fallback locale, supported/installed asset behavior |
| Privacy | Audio retention, transcript retention, model processing, sync/export, deletion |
| Model | `SpeechTranscriber` preset/options, `SpeechDetector` policy, asset reservation |
| Result policy | Volatile text, alternatives, timing, confidence, and finalization rule |
| Domain truth | Source transcript revision and explicit save/export destination |
| AI | User action, bounded source ranges, typed output, validation, stale-revision behavior |
| Accessibility | VoiceOver, Dynamic Type, Reduce Motion/Transparency, alternate input |
| Proof | Fixture, physical device, route/interruption, archive, TestFlight, release record |

If any row is unknown, the route is not ready for implementation beyond a reducer fixture or static UI.

## 3. Preflight the target and privacy strings

1. Create or select the named iOS app target and confirm the deployment target is the one the route claims.
2. Add the Speech and AVFAudio imports only to the target that owns capture/transcription.
3. Add `NSMicrophoneUsageDescription` with a product-specific purpose string.
4. Do not add `NSSpeechRecognitionUsageDescription` unless the target actually uses the legacy `SFSpeechRecognizer` route; keep that disclosure separate from a SpeechAnalyzer-only local route.
5. Confirm background audio, audio session, App Group, document, CloudKit, or export capabilities only if the product needs them.
6. Record whether `CaptureInputSequenceProvider`, `AnalyzerInputConverter`, or other current Speech input APIs are beta in the SDK being used.
7. Create a deterministic fixture target for transcript reduction before connecting a microphone.

The target graph and privacy strings are part of the feature. A working local preview with the wrong target or missing usage description is not a safe route.

## 4. Step 1 — ask for microphone access at the capture boundary

Use `AVAudioApplication.requestRecordPermission()` immediately before a user-initiated recording flow. The UI should explain the purpose before the system prompt and handle `undetermined`, `granted`, and `denied` states.

Stop conditions:

- no `NSMicrophoneUsageDescription`;
- capture begins before permission is granted;
- denied permission is represented only by a disabled button with no fallback;
- the app silently switches from local SpeechAnalyzer to a server recognizer;
- the system audio route is treated as proof that nonzero samples are arriving.

If permission is denied, keep file import, transcript review, and manual entry available when they fit the product. Do not repeatedly prompt on every view appearance.

## 5. Step 2 — resolve locale, availability, and assets

Choose a locale through the transcriber’s supported-locale APIs, then distinguish installed assets from merely supported or downloadable locales.

Recommended sequence:

1. Evaluate `SpeechTranscriber.isAvailable`.
2. Resolve the requested locale with `SpeechTranscriber.supportedLocale(equivalentTo:)` or select from `supportedLocales`.
3. Decide whether the UI may offer only `installedLocales` for an offline-first moment or may download a supported locale.
4. Create the transcriber with the chosen preset or explicit transcription/reporting/attribute options.
5. Inspect `AssetInventory.status(forModules:)`.
6. Reserve a locale only for a feature that needs a long-lived reservation; release it when appropriate.
7. Obtain `AssetInventory.assetInstallationRequest(supporting:)` and call `downloadAndInstall()` when a request exists.
8. Handle deferred download, failure, cancellation, and retry without losing the user’s source or settings.

The readiness record should contain:

~~~text
requestedLocale
resolvedLocale
isAvailable
installedAtStart
assetStatusBefore
installationAttempted
assetStatusAfter
networkPolicy
transcriberConfigurationRevision
~~~

Do not persist “ready” merely because a previous session succeeded. Recheck on the target device and after an OS/model update.

## 6. Step 3 — choose and own input lifetime

### Live capture

For a documented capture-provider route, verify the final initializer and target availability of `CaptureInputSequenceProvider`, retain the capture session/output for the required lifetime, and use its `analyzerInputs` sequence. The current documentation marks the API beta and notes that the sequence terminates when the audio data output/capture session is deallocated.

For an app-owned AVAudioEngine or AVCapture graph, create a bounded `AsyncSequence<AnalyzerInput>` and use `AnalyzerInputConverter` to convert each supported buffer. The capture callback should do minimal work:

~~~text
capture callback
  -> copy/retain buffer for the bounded handoff
  -> convert to supported analyzer format
  -> attach correct bufferStartTime when discontinuous
  -> yield AnalyzerInput
  -> never await the model or database in the callback
~~~

### File or asset input

Use `AssetInputSequenceProvider` when the source is an `AVAsset` or file and the provider can select a compatible track. For a finite source, prefer an analyzer method that naturally ends after the file, then finalize through the last consumed time.

### Raw AnalyzerInput

Use raw input when the product already owns a media pipeline or needs to skip ranges. The analyzer does not convert arbitrary formats; choose a compatible format first. If a later buffer is discontiguous, pass its time code instead of pretending the skipped audio existed.

## 7. Step 4 — create one analyzer owner

Create one long-lived feature owner that holds:

- the current session generation;
- the transcriber and optional detector;
- the analyzer actor;
- the input continuation/provider lifetime;
- the result-consumer task;
- the analysis task;
- the audio-session/capture observer tokens;
- the transcript reducer and source revision.

The analyzer can analyze only one input sequence at a time. When starting a new session:

1. cancel the old result and analysis tasks;
2. stop and release the old input source;
3. finish or cancel the old analyzer according to the source state;
4. increment `sessionGeneration`;
5. create a fresh module/analyzer/input sequence;
6. reject late results from prior generations.

Do not create a new analyzer in a SwiftUI view initializer or let every view register its own result loop.

## 8. Step 5 — reduce volatile and final results

The result consumer should store source ranges and finalization metadata rather than just append strings.

For each `SpeechTranscriber.Result`:

- read `result.text` as the most likely interpretation;
- preserve `alternatives` only if review supports them;
- inspect time-range and confidence attributes when configured;
- use `result.isFinal` or `resultsFinalizationTime` to decide whether to consolidate;
- replace/revoke only the affected volatile range;
- attach the current session generation;
- publish a new immutable transcript snapshot to the main-actor UI model.

When `SpeechAnalyzer.volatileRange` changes, use it for broad resource/progress policy, not as a guarantee that the result stream has already been consumed. A transcript reducer may safely commit content outside the volatile range once the module’s finalization contract says it is final.

The reducer must be deterministic for the same ordered fixture. Test:

- a volatile result replaced by a longer result;
- a volatile result replaced by an empty result;
- a final result arriving after an earlier volatile result;
- overlapping results with source times;
- a late result from an old session generation;
- a cancellation before finalization;
- a gap caused by a route interruption;
- a duplicate unchanged final result.

## 9. Step 6 — finish and cancel explicitly

When the person taps Stop:

1. mark capture stopping so new UI commands are rejected;
2. stop/remove the audio tap or capture output;
3. finish the input continuation/provider;
4. let the analyzer consume the end of input;
5. call `finalizeAndFinishThroughEndOfInput()` or finalize through a known last sample time;
6. drain the result sequence;
7. persist a final or incomplete source revision;
8. release model/session resources according to policy.

When the person cancels:

1. stop input;
2. call `cancelAndFinishNow()` or cancel the owned task;
3. mark the source revision incomplete or discarded according to the explicit UI choice;
4. do not label unfinalized text as final;
5. preserve a recoverable draft if the product promises recovery.

If the app is interrupted or backgrounded, follow the target’s audio/background policy; do not assume a view lifecycle event is a valid analyzer-finish event.

## 10. Step 7 — compose the SwiftUI route

The SwiftUI model should publish:

~~~text
permissionState
assetReadiness
audioRouteState
analysisState
transcriptSnapshot
selectedSourceRange
followLive
sourceRevision
proposalState
error / recoveryAction
~~~

Use a `ScrollView`/editor surface for the source, a stable segment identity for updates, and a functional control group for capture/review. Keep state badges short and pair each with accessibility text. Use the design rules in [the focused design page](../21-design-deep-dives/152-swiftui-speechanalyzer-live-transcription-review-design.md).

Liquid Glass is appropriate for the capture/review controls and status groups when it improves hierarchy. It is not a reason to put translucent material behind every paragraph or to hide the source revision. Test with Reduce Transparency, high contrast, large text, VoiceOver, keyboard/pointer input, and narrow widths.

## 11. Step 8 — optional AI proposal after explicit review

Gate the AI action on:

- a final or user-accepted transcript revision;
- a bounded source range and character/token budget;
- current model availability;
- privacy/retention policy;
- a typed output contract;
- a stale-revision check before display and save.

Good first proposal types are a title, outline, tags from an allowlist, or action candidates that cite source ranges. Keep the proposal separate from the transcript. Require the user to edit/reject/save it. Do not run the model automatically on every live result, and do not let it infer sensitive conclusions from a source without product-specific review.

## 12. Verification route

Run in this order:

1. Pure reducer tests with deterministic result fixtures.
2. SwiftUI previews for every readiness, volatile/final, interruption, gap, and proposal state.
3. Target compile against the final iOS 26 SDK with real Speech imports.
4. Audio-asset fixture transcription without microphone permissions.
5. Physical-device microphone capture with a known spoken fixture.
6. Poor-network/model-install/deferred-asset fixture.
7. Permission denial/revocation, route change, interruption, background, and relaunch fixtures.
8. VoiceOver, Dynamic Type, Reduce Motion/Transparency, contrast, keyboard/pointer/accessibility-input checks.
9. Optional AI proposal on supported and unavailable devices, including stale-revision rejection.
10. Release configuration, archive/signing, TestFlight install, and final-device evidence.

The [proof matrix](../60-verification/149-swiftui-speechanalyzer-live-transcription-proof-matrix.md) is the acceptance record. A simulator transcript or a green compile is not proof of microphone fidelity or target-device model readiness.

## Route record template

~~~text
Feature:
Target / deployment / SDK:
Input lane:
Requested and resolved locale:
Transcriber preset/options:
SpeechDetector policy:
Asset reservation/install policy:
Microphone permission string:
Audio-session category/mode/options:
Interruption and route recovery:
Analyzer owner and session generation:
Volatile/final reducer rule:
Transcript storage/export:
AI proposal trigger and typed output:
Accessibility checks:
Physical-device fixture:
Archive/TestFlight/release evidence:
Open SDK/beta questions:
~~~

## Sources

- [Speech framework](https://developer.apple.com/documentation/speech)
- [Speech updates](https://developer.apple.com/documentation/updates/speech)
- [SpeechAnalyzer](https://developer.apple.com/documentation/speech/speechanalyzer)
- [SpeechTranscriber](https://developer.apple.com/documentation/speech/speechtranscriber)
- [SpeechDetector](https://developer.apple.com/documentation/speech/speechdetector)
- [SpeechTranscriber.ReportingOption](https://developer.apple.com/documentation/speech/speechtranscriber/reportingoption)
- [SpeechTranscriber.ResultAttributeOption](https://developer.apple.com/documentation/speech/speechtranscriber/resultattributeoption)
- [SpeechTranscriber.Result](https://developer.apple.com/documentation/speech/speechtranscriber/result)
- [SpeechModuleResult.resultsFinalizationTime](https://developer.apple.com/documentation/speech/speechmoduleresult/resultsfinalizationtime)
- [AssetInventory](https://developer.apple.com/documentation/speech/assetinventory)
- [AssetInstallationRequest](https://developer.apple.com/documentation/speech/assetinstallationrequest)
- [AssetInputSequenceProvider](https://developer.apple.com/documentation/speech/assetinputsequenceprovider)
- [CaptureInputSequenceProvider](https://developer.apple.com/documentation/speech/captureinputsequenceprovider)
- [AnalyzerInputConverter](https://developer.apple.com/documentation/speech/analyzerinputconverter)
- [AnalyzerInput](https://developer.apple.com/documentation/speech/analyzerinput)
- [AVAudioApplication](https://developer.apple.com/documentation/avfaudio/avaudioapplication)
- [Requesting audio recording permission](https://developer.apple.com/documentation/avfaudio/avaudioapplication/requestrecordpermission%28completionhandler%3A%29)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Handling audio interruptions](https://developer.apple.com/documentation/avfaudio/handling-audio-interruptions)
- [Responding to audio route changes](https://developer.apple.com/documentation/avfaudio/responding-to-audio-route-changes)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
- [Running your app on simulated or physical devices](https://developer.apple.com/documentation/xcode/running-your-app-on-simulated-or-physical-devices)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
