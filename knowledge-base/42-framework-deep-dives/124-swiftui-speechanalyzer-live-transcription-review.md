# SwiftUI SpeechAnalyzer live transcription review

This is the focused iOS 26 route for local speech transcription that begins with a microphone or audio asset, feeds a `SpeechAnalyzer`, renders volatile and finalized text in SwiftUI, and optionally hands an explicitly accepted transcript to an on-device language model. The existing [SwiftUI audio capture and transcription deep dive](89-swiftui-audio-capture-and-transcription.md) covers the broader AVAudioEngine/Speech/SoundAnalysis map. This page narrows the newer SpeechAnalyzer boundary so a product does not confuse microphone permission, model assets, input lifetime, transcription finality, or AI-generated interpretation.

The system is:

~~~text
user starts capture
  -> microphone permission and audio-session readiness
  -> locale/model availability and asset readiness
  -> AVAudioEngine/AVCapture input or audio asset
  -> AnalyzerInput sequence
  -> SpeechAnalyzer actor
  -> SpeechTranscriber result AsyncSequence
  -> volatile/final transcript reducer
  -> SwiftUI transcript/review surface
  -> optional user-approved Foundation Models proposal
  -> explicit app-owned save/export/side effect
~~~

`SpeechAnalyzer` is the analysis owner. `SpeechTranscriber` is a module. The audio source, result consumer, SwiftUI model, and optional AI session are separate owners connected by typed state and cancellation. A transcript result proves only that the framework produced an interpretation for a time range; it does not by itself prove that the correct microphone was captured, that every result is final, or that a generated summary is true.

## 1. What makes this a distinct iOS 26 route

The Speech framework now exposes a module-oriented analysis model around a `SpeechAnalyzer` actor. Apple documents `SpeechTranscriber` for general speech-to-text, `SpeechDetector` for voice-activity detection, `AssetInventory` for model assets, `AssetInputSequenceProvider` for files/assets, `CaptureInputSequenceProvider` for captured audio, and `AnalyzerInputConverter` for converting buffers into analyzer input. The provider and converter pages are marked beta in the current documentation; treat those APIs as SDK-sensitive until the final target SDK is compiled.

The route is not a cosmetic replacement for the older `SFSpeechRecognizer` flow:

| Concern | SpeechAnalyzer route | Legacy SFSpeechRecognizer route |
| --- | --- | --- |
| Analysis model | `SpeechAnalyzer` actor with `SpeechModule` instances | Recognition request/task objects |
| Input | `AsyncSequence<AnalyzerInput>` or an asset/capture provider | Request-specific audio input |
| Results | Module-owned `AsyncSequence` with attributed text and timing | Recognition result callbacks |
| Tentative text | `volatileResults`, `volatileRange`, and module finalization time | Partial result flag and task lifecycle |
| Model assets | `AssetInventory` and locale reservations | Service availability and legacy request behavior |
| Audio privacy | `SpeechAnalyzer` transcriber modules don’t send voice audio to Apple’s servers; microphone capture still requires permission | The legacy recognition authorization page describes server-based recognition and its distinct disclosure |
| Authorization | Ask for microphone access when capture is about to begin; do not request legacy speech authorization for a SpeechAnalyzer-only path | `SFSpeechRecognizer.requestAuthorization(_:)` and `NSSpeechRecognitionUsageDescription` apply to the legacy recognizer path |

Keep both paths in separate adapters if an app supports older OS versions. Do not copy the legacy speech-recognition disclosure into a local-only route without explaining the actual data flow, and do not omit the microphone purpose string because the model runs on device.

## 2. Availability is a typed state machine

There are at least four independent readiness questions:

1. Can this device run the selected transcriber? `SpeechTranscriber.isAvailable` is a capability check, not a guarantee that a locale’s assets are installed.
2. Does the requested locale match `supportedLocales` or resolve through `supportedLocale(equivalentTo:)`?
3. Are the assets installed or downloadable? `installedLocales`, `AssetInventory.status(forModules:)`, and the installation request answer different parts of this question.
4. Is the current app allowed to capture the microphone? `AVAudioApplication` permission, `NSMicrophoneUsageDescription`, audio-session activation, route, and interruption state are separate gates.

Model the result explicitly:

| State | Meaning | User-facing action |
| --- | --- | --- |
| unavailable | Hardware, OS, Apple Intelligence-style device capability, or module support is absent | Explain the unavailable feature and offer an asset/import fallback |
| localeUnsupported | No supported locale matches the request | Offer a supported locale or a file/import route |
| assetsNeeded | Required assets are not ready | Show download/install progress and a network-aware retry |
| permissionNeeded | Microphone permission is undetermined | Explain the capture purpose, then ask at the point of use |
| denied | Microphone permission was denied or restricted | Keep transcript import available and link to Settings |
| sessionPreparing | Audio session/model/analyzer is being prepared | Disable duplicate starts and show cancellation |
| capturing | Input is being delivered and results are changing | Show live state and a clear stop action |
| finalizing | Input ended; analyzer is finishing through a known time | Keep the transcript readable but mark finalization |
| readyForReview | The source transcript is accepted as final for the requested range | Enable review, edit, export, or optional AI proposal |
| failed | Input, model, session, or result stream failed | Preserve the source and explain retry/fallback |

Do not collapse `isAvailable == true` into `readyForReview`. A device can support the module while its locale assets are unavailable, the microphone is denied, or the analyzer is still reporting volatile results.

## 3. Configure modules and assets

Start with one transcriber and add a detector only when the product has measured a reason to gate analysis during silence. Apple documents that `SpeechDetector` works in conjunction with a transcriber or dictation transcriber. Its default role can be power optimization without reporting VAD results; enabling result reporting introduces another result stream and another error path. Aggressive VAD can save power but may discard speech, so the sensitivity choice is product- and fixture-specific.

For a general transcriber, choose the locale and reporting contract deliberately:

| Option | Product consequence |
| --- | --- |
| `fastResults` | Lower time-to-first-result bias, with an accuracy tradeoff |
| `volatileResults` | Tentative results can be replaced; the UI must not treat them as committed text |
| `alternativeTranscriptions` | More than the most likely interpretation becomes available; expose only if the review interaction can explain it |
| `audioTimeRange` | Attributed text carries source timing that can drive seek/highlight review |
| `transcriptionConfidence` | Attributed text carries confidence information; present it as a cue, never as truth |
| `etiquetteReplacements` | Certain words and phrases can be replaced by a redacted form; record this as a transcription policy |

`SpeechTranscriber.Result.text` is an `AttributedString`. Its `alternatives` are ordered interpretations. A volatile result may be sent more than once as the model improves, and an empty text can revoke an earlier volatile interpretation for that range. Preserve the source time range and result revision so the reducer can replace only the affected segment.

Before analyzing, obtain an `AssetInstallationRequest` from `AssetInventory.assetInstallationRequest(supporting:)` and call `downloadAndInstall()` when one is returned. Apple documents that requests are consolidated and repeated calls do not cause redundant downloads. A download may fail immediately and be retried by the system later, so the app needs a visible “not ready yet” state rather than assuming the current call is the only attempt. Locale reservations are a separate resource-management concern; release them when a long-lived feature no longer needs them.

## 4. Feed the analyzer without losing time or ownership

The analyzer accepts one input sequence at a time. Choose one of three input lanes:

| Input lane | Use when | Boundary |
| --- | --- | --- |
| `AssetInputSequenceProvider` | Transcribing an `AVAsset` or file | The provider reads a track and exposes a new `analyzerInputs` sequence |
| `CaptureInputSequenceProvider` | Using the documented capture-device helper | Current docs mark the API beta; verify the final initializer, target, and lifetime in the SDK |
| `AnalyzerInputConverter` plus `AsyncStream` | Owning an AVAudioEngine/AVCapture buffer pipeline | The app controls conversion, time codes, backpressure, and continuation finish |

`AnalyzerInput` must use a format supported by the modules. The analyzer does not perform arbitrary audio conversion. Call `SpeechAnalyzer.bestAvailableAudioFormat(compatibleWith:considering:)` or inspect module-compatible formats, then convert buffers before yielding them. If a buffer is discontiguous with the previous input, carry the correct `bufferStartTime`; omitting time continuity can corrupt source-range mapping.

The input sequence is a lifecycle object, not a convenience collection:

~~~text
capture session owns audio output
  -> converter produces time-coded AnalyzerInput values
  -> continuation yields bounded values
  -> analyzer consumes one sequence
  -> stop removes the tap/output and finishes the continuation
  -> analyzer finalizes through the last consumed time
  -> result task drains and ends
~~~

Bound the handoff. A microphone callback must not await a language model, write a database, perform expensive formatting, or block on the main actor. Use a small queue/actor boundary, drop or coalesce only with a documented policy, and retain enough timestamps to tell the user when a gap occurred.

## 5. Run, observe, finalize, and cancel

Use structured `analyzeSequence(_:)` when the task should own the entire input lifetime. Use `start(inputSequence:)` or an input-aware initializer when autonomous analysis is useful and the analyzer should process input as it arrives. In both cases, start a result-consumer task before or alongside analysis and cancel every task together.

The analyzer’s `volatileRange` describes the audio whose results may change, including input already sent but not yet returned as a result. `setVolatileRangeChangedHandler(_:)` can drive resource/progress policy, but Apple notes that result streams may still contain results the app has not consumed. The module result’s `resultsFinalizationTime` and `isFinal` are the better source for deciding whether a specific result can be consolidated.

Finalization is a source-revision boundary:

| Operation | Meaning |
| --- | --- |
| `finalize(through:)` | Ask modules to finalize through a time; input may be consumed first |
| `finish(after:)` | Finish once input through a time is consumed |
| `finalizeAndFinish(through:)` | Finalize through a time and end the session there |
| `finalizeAndFinishThroughEndOfInput()` | End after the input sequence is terminated and results are finalized |
| `cancelAnalysis(before:)` | Stop analyzing old audio that is no longer relevant |
| `cancelAndFinishNow()` | Stop immediately and close the session |

Do not call a finish method merely because the view disappeared. Tie it to the feature’s capture/session owner. If a user stops capture, stop the source, finish the input continuation, await analyzer finalization, then persist the final transcript revision. If a task is cancelled or an interruption occurs, preserve the last accepted revision and mark the remainder incomplete.

## 6. Reduce results into source-owned transcript state

Keep three layers:

1. `TranscriptSource`: immutable or append-only source metadata, capture/session ID, locale, model/configuration revision, and time-coded source segments.
2. `TranscriptDraft`: current volatile and finalized segments, confidence/timing attributes, gaps, and reducer revision.
3. `TranscriptProposal`: optional generated title, outline, tags, or action candidates that point back to source ranges and have not changed the source.

The reducer should:

- identify a segment by source time range and stable local ID;
- replace only segments within the current volatile range;
- retain finalized segments across later result emissions;
- accept an empty volatile result as a revocation;
- record `resultsFinalizationTime` and not infer finality from “the stream has been quiet”;
- preserve alternatives and confidence only when the UI has a clear review affordance;
- reject late results whose session generation is no longer current;
- mark audio gaps and permission loss instead of silently concatenating text.

For an editable transcript, save a source revision before applying user edits. An AI proposal must cite the transcript revision and source ranges it used. If the transcript changes, invalidate the proposal or recompute it. Never let a model response overwrite a live volatile segment.

## 7. Audio session, permission, interruption, and route recovery

The local model does not grant microphone access. Include `NSMicrophoneUsageDescription` and request `AVAudioApplication.requestRecordPermission()` at a user-initiated capture boundary. Apple’s speech-authorization page describes `NSSpeechRecognitionUsageDescription` and `SFSpeechRecognizer.requestAuthorization(_:)` for legacy server-based recognition; that is a different route. If the same target ships both routes, document and test each data flow separately.

Configure `AVAudioSession` for the product’s actual input/output need, activate it before starting the capture graph, and observe interruption and route-change notifications. On interruption, stop or pause input according to the reason and preserve the last source revision. On a microphone disconnect or route change, remove/rebuild the input tap or capture provider only after the new route is valid. Do not resume automatically merely because an interruption ended; require the app’s policy and current permission/route state to allow resume.

Useful recovery state is:

~~~text
capturing
  -> interrupted / routeUnavailable / permissionRevoked
  -> sourceStopped + transcriptDraftPreserved
  -> routeAndSessionRevalidated
  -> user resumes or feature falls back to file import
  -> new sessionGeneration
  -> new analyzer/input sequence
~~~

A new analyzer generation prevents old result tasks from mutating the new transcript. A route snapshot is evidence about the audio session, not evidence that the analyzer received nonzero samples; keep a physical microphone fixture for that claim.

## 8. SwiftUI and Liquid Glass composition

Build the transcript surface around function and state, not a decorative glass panel:

- the transcript is the primary content region;
- the capture toolbar contains the one primary action, source/permission status, and a route-safe cancel/stop action;
- a secondary review group contains language, timing/confidence visibility, import, and optional AI actions;
- a sheet or inspector shows model/asset readiness and errors without hiding the transcript;
- the AI result is visually distinct from the source transcript and requires an explicit apply/save action.

Use SwiftUI semantic controls, dynamic type, readable contrast, content shapes, and accessibility labels. Apply Liquid Glass to functional controls and groups that benefit from hierarchy or separation; keep the transcript readable against the material and allow a plain fallback for reduced transparency, high contrast, unsupported targets, or accessibility settings. Do not use glass as a substitute for status text, permission explanation, or source provenance.

When the transcript scrolls, keep the newest volatile segment visible only if the user has not taken manual control. A user who scrolls back to inspect a source range should not be pulled to the bottom by every result. Use stable segment IDs and source time ranges so edits, VoiceOver focus, and selection do not jump when volatile text is replaced.

## 9. Optional on-device AI after transcript review

Foundation Models can be a useful post-transcription lane for bounded summaries, titles, entities, or next-step proposals. It is not the recognizer and it must not receive microphone buffers. A safe handoff is:

~~~text
final transcript revision
  -> user taps “Suggest”
  -> bounded source ranges and privacy policy
  -> model availability check
  -> typed proposal with source IDs
  -> user reviews/edits/rejects
  -> deterministic validation
  -> explicit app-owned save or App Intent
~~~

Use a typed `@Generable` result when a proposal must be validated. Keep the original transcript, prompt/model revision, response, and acceptance decision separate. If the device model is unavailable, show a deterministic manual route or offer export; do not silently send sensitive audio or transcript text to a server. A generated title, task list, or summary is a proposal, not a fact and not proof that the transcript was accurate.

## 10. Evidence and release boundary

The minimum evidence packet for a real app includes:

| Claim | Required evidence |
| --- | --- |
| Microphone capture works | Physical device, permission granted, known spoken fixture, nonzero captured audio, route recorded |
| Locale/model is ready | Targeted device/OS, supported locale, asset status/install result, offline/poor-network case |
| Live transcript updates | Timestamped result log with volatile replacements and no duplicated committed text |
| Final transcript is stable | Stop/finish path, finalization time, result drain, persisted revision, relaunch/reopen check |
| Interruption recovery works | Phone/route/interruption fixture and explicit resume policy |
| SwiftUI surface is native and accessible | Dynamic Type, VoiceOver, Reduce Motion/Transparency/contrast, keyboard/pointer where relevant |
| AI proposal is safe | Model availability, bounded input, source references, rejection/edit path, stale-revision test |
| Release is ready | Final SDK compile, archive/signing, TestFlight build, physical-device evidence, privacy strings, and App Store metadata review |

Simulator text rendering can validate layout and reducer fixtures. It cannot prove microphone fidelity, model availability on the intended device, route behavior, or final release behavior. Compile-oriented sketches live in the [SpeechAnalyzer recipes](../70-code-recipes/167-swiftui-speechanalyzer-live-transcription-review-recipes.md); the route worksheet is [here](../50-capability-recipes/155-swiftui-speechanalyzer-live-transcription-review-route.md), and the proof matrix is [here](../60-verification/149-swiftui-speechanalyzer-live-transcription-proof-matrix.md).

## Sources

- [Speech framework](https://developer.apple.com/documentation/speech)
- [Speech updates](https://developer.apple.com/documentation/updates/speech)
- [SpeechAnalyzer](https://developer.apple.com/documentation/speech/speechanalyzer)
- [SpeechTranscriber](https://developer.apple.com/documentation/speech/speechtranscriber)
- [SpeechTranscriber.ReportingOption](https://developer.apple.com/documentation/speech/speechtranscriber/reportingoption)
- [SpeechTranscriber.ResultAttributeOption](https://developer.apple.com/documentation/speech/speechtranscriber/resultattributeoption)
- [SpeechTranscriber.TranscriptionOption](https://developer.apple.com/documentation/speech/speechtranscriber/transcriptionoption)
- [SpeechTranscriber.Result](https://developer.apple.com/documentation/speech/speechtranscriber/result)
- [SpeechTranscriber.Result.text](https://developer.apple.com/documentation/speech/speechtranscriber/result/text)
- [SpeechModule](https://developer.apple.com/documentation/speech/speechmodule)
- [SpeechModuleResult](https://developer.apple.com/documentation/speech/speechmoduleresult)
- [SpeechModuleResult.resultsFinalizationTime](https://developer.apple.com/documentation/speech/speechmoduleresult/resultsfinalizationtime)
- [SpeechDetector](https://developer.apple.com/documentation/speech/speechdetector)
- [AssetInventory](https://developer.apple.com/documentation/speech/assetinventory)
- [AssetInstallationRequest](https://developer.apple.com/documentation/speech/assetinstallationrequest)
- [AssetInstallationRequest.downloadAndInstall()](https://developer.apple.com/documentation/speech/assetinstallationrequest/downloadandinstall%28%29)
- [AssetInputSequenceProvider](https://developer.apple.com/documentation/speech/assetinputsequenceprovider)
- [CaptureInputSequenceProvider](https://developer.apple.com/documentation/speech/captureinputsequenceprovider)
- [CaptureInputSequenceProvider.analyzerInputs](https://developer.apple.com/documentation/speech/captureinputsequenceprovider/analyzerinputs)
- [AnalyzerInputConverter](https://developer.apple.com/documentation/speech/analyzerinputconverter)
- [AnalyzerInput](https://developer.apple.com/documentation/speech/analyzerinput)
- [Recognizing speech in live audio](https://developer.apple.com/documentation/speech/recognizing-speech-in-live-audio)
- [Bringing advanced speech-to-text capabilities to your app](https://developer.apple.com/documentation/speech/bringing-advanced-speech-to-text-capabilities-to-your-app)
- [Asking permission to use speech recognition](https://developer.apple.com/documentation/speech/asking-permission-to-use-speech-recognition)
- [AVAudioApplication](https://developer.apple.com/documentation/avfaudio/avaudioapplication)
- [Requesting audio recording permission](https://developer.apple.com/documentation/avfaudio/avaudioapplication/requestrecordpermission%28completionhandler%3A%29)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Handling audio interruptions](https://developer.apple.com/documentation/avfaudio/handling-audio-interruptions)
- [Responding to audio route changes](https://developer.apple.com/documentation/avfaudio/responding-to-audio-route-changes)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
- [Swift concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
- [Running your app on simulated or physical devices](https://developer.apple.com/documentation/xcode/running-your-app-on-simulated-or-physical-devices)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
