# SwiftUI SpeechAnalyzer live transcription proof matrix

This matrix defines what must be proven for an iOS 26 SpeechAnalyzer feature. It complements the [framework review](../42-framework-deep-dives/124-swiftui-speechanalyzer-live-transcription-review.md), [design review](../21-design-deep-dives/152-swiftui-speechanalyzer-live-transcription-review-design.md), [route worksheet](../50-capability-recipes/155-swiftui-speechanalyzer-live-transcription-review-route.md), and [compile-oriented recipes](../70-code-recipes/167-swiftui-speechanalyzer-live-transcription-review-recipes.md).

The central rule is:

> A result stream, availability flag, permission grant, simulator preview, or AI response is evidence for one layer only. It is not proof of the layers around it.

## 1. Test record

Record one row per target/device/SDK/configuration:

~~~text
Feature:
App target and bundle identifier:
Deployment target / SDK / build:
Device model / OS / locale / region:
SpeechTranscriber configuration revision:
Asset status and locale reservation:
Input lane and audio fixture:
Audio-session category/mode/options:
Microphone permission state:
Network state during asset setup:
Analyzer/session generation:
Transcript fixture and expected source ranges:
Interruption/route fixture:
AI model availability and output schema:
Accessibility settings:
Evidence artifacts:
Tester/date:
Known limitations:
Disposition: pass / fail / blocked / not applicable
~~~

Do not merge “works on my device” into a release claim. The target, SDK, device family, locale, asset state, and signed build are part of the result.

## 2. Claim-to-evidence matrix

| Claim | Minimum evidence | Does not prove it |
| --- | --- | --- |
| SpeechAnalyzer compiles in the target | Final SDK target build with `import Speech` and selected APIs | A code snippet or documentation page |
| Device supports the transcriber | Physical target query of `SpeechTranscriber.isAvailable` and supported/resolved locale | Simulator or a different device |
| Locale assets are ready | `AssetInventory.status(forModules:)`, install result, and a transcription fixture | `supportedLocales` alone |
| Microphone permission is handled | `NSMicrophoneUsageDescription`, permission-denied/granted runs, Settings recovery | A permission Boolean without a capture run |
| The intended microphone is captured | Physical device, known spoken fixture, nonzero buffer/timestamp evidence, route recorded | Audio-session route snapshot |
| The input format is compatible | Selected analyzer format and converter/fixture logs | Passing an arbitrary buffer without an error |
| Live text updates | Timestamped result log showing ordered volatile revisions | A final static string |
| Volatile text is not committed early | Reducer test with replacement/revocation and a UI run | A quiet result stream |
| Final text is final | Explicit finish/finalization, result drain, persisted source revision, reopen check | `result.text` alone |
| Stop works | Input termination, analyzer finalization, task completion, no late mutation | A button tap animation |
| Cancel works | Cancellation fixture with incomplete/discarded state and no stale result mutation | A task cancellation without state inspection |
| Interruption recovery works | Phone/route interruption fixture, preserved source, explicit resume policy | A notification handler existing |
| Route change recovery works | Headphone/Bluetooth/USB route fixture and capture restart or fallback evidence | Current route name |
| SwiftUI design is accessible | VoiceOver, Dynamic Type, contrast, Reduce Motion/Transparency, alternate-input run | A preview screenshot |
| Liquid Glass is appropriate | Functional control hierarchy plus reduced-transparency/plain fallback review | Applying a glass modifier everywhere |
| AI proposal is bounded | Availability result, source revision/range, typed output, rejection/edit/save, stale invalidation | A model response |
| Offline behavior is honest | Model-not-installed/poor-network/import fallback run | Labeling the feature “on device” |
| Release target is configured | Archive inspection, signing, privacy strings, TestFlight install | Simulator archive or local debug run |

## 3. Deterministic reducer fixtures

Before a microphone run, feed the transcript reducer a fixed sequence of result records:

| Fixture | Expected assertion |
| --- | --- |
| Empty source | No transcript, start action remains available |
| One final segment | One stable segment with source time and revision |
| Volatile “hello” then “hello world” | One replaced live segment, no duplicate “hello” |
| Volatile text then empty text | Earlier tentative segment is revoked |
| Volatile then final same range | Final segment replaces tentative state and remains stable |
| Final result arrives out of UI render order | Source-time ordering wins; arrival order is not display order |
| Overlapping ranges | Reducer resolves by the documented range/revision rule and logs ambiguity |
| Old session generation | Result is ignored and cannot mutate current transcript |
| Capture gap | Gap marker/source discontinuity is retained |
| Cancellation before finalization | Transcript is marked incomplete, never final |
| Duplicate final result | Idempotent state; no extra save or accessibility announcement |
| Edited source revision | AI proposal tied to the old revision becomes stale |

The fixture should retain `AttributedString` timing/confidence attributes when the target enables them. A test that converts every result immediately to plain `String` cannot prove source-range behavior.

## 4. Asset and locale matrix

| Scenario | Setup | Expected result |
| --- | --- | --- |
| Supported and installed locale | Device has the target locale assets | Ready state; no unnecessary download |
| Supported but not installed | Network available | Asset request/install state; recording waits or clearly chooses fallback |
| Deferred install | Initial request cannot complete | Honest not-ready state and retry; no false success |
| Unsupported locale | Requested locale has no equivalent | Locale fallback/import path |
| Module unavailable | `SpeechTranscriber.isAvailable == false` | Feature disabled with reason and fallback |
| Reservation limit | Another locale is reserved | Release/select route visible |
| OS/model update | Reopen after update | Availability and asset status rechecked |
| Offline first launch | Assets absent and network unavailable | No silent server recognition; import/manual fallback |
| Asset removed later | Previously ready locale no longer installed | Re-enter asset readiness state |

Capture the device model, OS build, locale, `AssetInventory.Status`, and model configuration revision in the evidence packet. The word “offline” should only describe the tested data path, not an assumption from the API name.

## 5. Microphone and input matrix

| Scenario | Evidence |
| --- | --- |
| First permission prompt | Purpose string visible; grant path starts only after approval |
| Denied permission | Capture stays stopped; Settings/manual import fallback works |
| Permission revoked while app is not running | Relaunch rechecks and explains state |
| Audio session activation fails | No analyzer start; actionable recovery and preserved draft |
| Known spoken fixture | Physical device recording includes expected words and timestamps |
| Silence fixture | UI distinguishes silence from “no result yet”; detector tradeoff measured if used |
| Rapid speech/noise | Volatile replacements and finalization remain ordered |
| Buffer format change | Converter/reconfiguration behavior is logged or rejected clearly |
| Dropped/backpressured buffer | Gap/quality state is visible; no silent concatenation |
| Capture stops | Tap/provider released, sequence finishes, analyzer closes |
| App background/foreground | Behavior matches target audio/background policy and does not corrupt revision |
| Input provider deallocation | Analyzer result sequence finishes or fails predictably |

For a real microphone claim, record a human-spoken or generated fixture, device route, approximate input level, start/stop times, and resulting source ranges. Do not store sensitive recordings in a shared test artifact without a declared retention policy.

## 6. Analyzer lifecycle and finality matrix

| Lifecycle | Required assertion |
| --- | --- |
| Analyzer created | Correct module list and configuration revision |
| `prepareToAnalyze` | Startup progress/state is visible if the feature preheats resources |
| `analyzeSequence` | Structured task ends when the input sequence ends |
| `start` route | Autonomous task is cancellable and owned by the feature |
| Result task | Module `AsyncSequence` errors are surfaced and tied to the session generation |
| `volatileRange` change | UI/reducer policy updates without assuming result stream consumption |
| `resultsFinalizationTime` | Segments outside finalization boundary can be consolidated |
| `finalize(through:)` | Requested time is consumed/finalized or an error is recorded |
| `finish(after:)` | Analyzer closes after the requested input time is consumed |
| `finalizeAndFinishThroughEndOfInput()` | Finite source ends and result streams terminate |
| `cancelAnalysis(before:)` | Old source range is no longer processed and behavior is logged |
| `cancelAndFinishNow()` | Immediate cancellation does not produce a false final transcript |
| New session | Old tasks/results cannot mutate the new session |

Use a timeline log with input time, result range, finalization time, session generation, task state, and UI revision. “The text looked good” is not sufficient finality evidence.

## 7. Interruption, route, and recovery matrix

| Event | Required behavior |
| --- | --- |
| Phone/FaceTime/system interruption begins | Capture/analyzer policy changes; draft preserved |
| Interruption ends | App checks permission, route, session, and user intent before resuming |
| Headphones disconnected | Capture route revalidated; no unexpected microphone switch |
| Bluetooth route changes | Route state and input graph revalidated |
| USB/external microphone removed | Clear status and offer built-in/import fallback |
| Audio-session media-services reset | Rebuild session/graph/analyzer generation as required |
| Audio route unavailable | No “listening” claim while no valid input exists |
| App terminated mid-session | Relaunch shows incomplete/recoverable source if promised |
| Screen locks or background begins | Behavior matches entitlement and product policy |

The route snapshot is supporting evidence. Pair it with captured samples or a fixture result to establish that the intended input reached the analyzer.

## 8. SwiftUI, Liquid Glass, and accessibility matrix

| Check | Pass condition |
| --- | --- |
| Compact iPhone | Primary capture/stop action reachable; transcript readable |
| iPad split/inspector | Source and readiness details do not crowd transcript |
| Large Dynamic Type | Text and buttons expand without clipping/overlap |
| VoiceOver | State, action, segment, source time, and proposal status are understandable |
| Reduce Motion | Decorative pulses disappear; state remains clear |
| Reduce Transparency/high contrast | Controls and transcript remain legible with fallback materials |
| Keyboard/pointer | Capture, stop, review, save, and dismiss are reachable |
| Manual scroll | Auto-follow stops when the user inspects older text |
| Volatile replacement | Focus/selection does not jump or announce duplicate content |
| Error state | Recovery action is accessible and source is preserved |
| Liquid Glass | Material is used for functional hierarchy, not the primary text surface |
| AI proposal | Generated content is distinct from source and has review actions |

Test in the actual target family. A SwiftUI preview can prove composition for fixtures, not microphone, asset, route, or system permission behavior.

## 9. Optional Foundation Models matrix

| Claim | Test |
| --- | --- |
| Model available | Query current model availability on the physical target |
| Prompt bounded | Record source revision/range and input-size policy |
| Typed output | `@Generable` response decodes or fails into a visible state |
| Source citations | Proposal fields link to valid transcript segment IDs |
| Stale protection | Edit transcript while model runs; proposal is rejected or marked stale |
| Cancellation | Cancel task; no late save or UI mutation |
| Error/fallback | Context/availability/error path leaves manual review usable |
| User consent | AI action is user initiated and processing disclosure is visible |
| Commit | User explicitly accepts and deterministic validation succeeds |

Do not count an AI-generated summary as transcription proof. Keep the source transcript, model output, prompt/configuration revision, and acceptance event separately auditable.

## 10. Archive, TestFlight, and release matrix

| Release gate | Required artifact |
| --- | --- |
| Target membership | Final project/target inspection showing Speech/AVFAudio imports and privacy strings in the shipping target |
| Final SDK | Release build compiles selected APIs without accidental beta-only target drift |
| Entitlements/capabilities | Exported archive profile and entitlements match the product’s audio/background/storage claims |
| Archive | Signed archive with build/version and reproducible configuration record |
| TestFlight | Installed build on the intended physical device with locale/model/microphone fixture |
| Review metadata | Accurate microphone, speech, AI, privacy, and data-retention descriptions |
| Regression | Reducer, UI, interruption, route, accessibility, and AI stale-revision results attached |
| Release | Live signed artifact and a known-device evidence packet |

Do not mark the route shipped from a preview, simulator, debug build, or archive alone. Use Apple’s release-build testing and distribution guidance as the final source of truth for the signed target.

## Sources

- [Speech framework](https://developer.apple.com/documentation/speech)
- [Speech updates](https://developer.apple.com/documentation/updates/speech)
- [SpeechAnalyzer](https://developer.apple.com/documentation/speech/speechanalyzer)
- [SpeechTranscriber](https://developer.apple.com/documentation/speech/speechtranscriber)
- [SpeechTranscriber.Result](https://developer.apple.com/documentation/speech/speechtranscriber/result)
- [SpeechModuleResult.resultsFinalizationTime](https://developer.apple.com/documentation/speech/speechmoduleresult/resultsfinalizationtime)
- [SpeechDetector](https://developer.apple.com/documentation/speech/speechdetector)
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
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
