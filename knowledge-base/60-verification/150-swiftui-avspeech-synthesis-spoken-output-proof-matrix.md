# SwiftUI AVSpeechSynthesizer spoken-output proof matrix

This matrix defines evidence for a spoken-output feature using `AVSpeechSynthesizer`. It pairs with the [framework review](../42-framework-deep-dives/125-swiftui-avspeech-synthesis-spoken-output-review.md), [design review](../21-design-deep-dives/153-swiftui-avspeech-synthesis-spoken-output-review-design.md), [route worksheet](../50-capability-recipes/156-swiftui-avspeech-synthesis-spoken-output-review-route.md), and [recipes](../70-code-recipes/168-swiftui-avspeech-synthesis-spoken-output-review-recipes.md).

The key boundary is:

> A voice object, queue state, delegate callback, or generated buffer is not proof that the intended words were audible on the intended route.

## 1. Test record

~~~text
Feature:
Target / bundle identifier / build:
Deployment target / SDK / configuration:
Device model / OS / locale / region:
Source revision and fixture:
Utterance chunking/configuration:
Voice identifier / language / quality:
Synthesizer generation:
usesApplicationAudioSession:
AVAudioSession category/mode/options/activation:
Output route / channels:
Interruption/route events:
Direct speak or buffer export:
Telephony uplink policy:
Accessibility settings:
AI proposal availability/revision:
Archive/TestFlight build:
Evidence files:
Tester/date:
Disposition:
~~~

## 2. Claim-to-evidence matrix

| Claim | Minimum evidence | Does not prove it |
| --- | --- | --- |
| TTS API compiles | Final target build with AVFAudio symbols | A recipe or docs page |
| Voice is available | Physical device inventory, language/quality/identifier, fallback | Voice name in a design mockup |
| Utterance policy is applied | Fixture checks for text, rate, pitch, volume, delays, pronunciation | A configured object after enqueue |
| Queue order is correct | Deterministic coordinator tests and delegate sequence | `speak` returning |
| Pause/resume/stop works | Physical run plus delegate/state timeline at selected boundaries | Button animation |
| Word highlight is accurate | Range/marker fixtures with UTF-16, emoji, RTL, combining marks | A timer-driven highlight |
| System-managed speech works | `usesApplicationAudioSession` policy plus interruption/mixing/route device run | A `didFinish` callback |
| App-managed speech works | Category/mode/activation/route/reset run on physical device | Session object existence |
| Intended route is audible | Known spoken phrase, physical listener/recording method, route logged | Current-route snapshot |
| Buffer export works | Buffer format, marker/file finalization, reopen/playback validation | `write` callback invoked |
| Channel selection works | Physical multi-channel/route fixture and output verification | `outputChannels` populated |
| Uplink is safe | Explicit communication state, consent, active-call local/far-end test | `mixToTelephonyUplink = true` |
| AI response is safe | Availability, bounded input, typed output, review, stale/cancel test | A generated string |
| Accessibility works | VoiceOver, Dynamic Type, contrast, Reduce Motion/Transparency, alternate input | Preview screenshot |
| Release is ready | Final archive, signing, TestFlight install, physical output, metadata review | Debug build or simulator |

## 3. Deterministic source and queue fixtures

| Fixture | Expected result |
| --- | --- |
| Empty source | Play disabled or clear empty-state action |
| One sentence | One utterance, one source mapping, start/finish state |
| Multi-paragraph source | Stable semantic queue order and paragraph progress |
| Source replacement | Old generation is cancelled; old callbacks cannot mutate new state |
| Append while speaking | New utterance is queued according to declared policy |
| Stop at word boundary | Queue stops and source state marks unspoken remainder |
| Stop at sentence boundary | Queue stops at a deterministic semantic boundary |
| Pause/continue | Highlight and queue identity remain stable |
| Duplicate delegate event | Idempotent UI state and no duplicate announcement |
| `NSRange` with emoji/combining marks | Safe source mapping or explicit unmapped fallback |
| Right-to-left/mixed script | Highlight and VoiceOver text remain correct |
| Missing voice | Fallback is visible and language is not silently changed |
| AI proposal stale | Proposal cannot be enqueued after source revision changes |

## 4. Voice and locale matrix

| Scenario | Evidence |
| --- | --- |
| Current locale voice | `AVSpeechSynthesisVoice.currentLanguageCode`/inventory and physical phrase |
| Regional fallback | Preferred region unavailable; fallback displayed and tested |
| High-quality voice | Device inventory/quality and output comparison fixture |
| Voice download/availability change | Reopen/recheck and graceful fallback |
| Long localized text | Queue chunking, range mapping, and finish behavior |
| SSML/IPA or pronunciation markup | Target SDK/parser result, privacy/content fixture, fallback on invalid input |
| Assistive technology settings | VoiceOver/Speak Screen interaction with `prefersAssistiveTechnologySettings` policy |
| Mixed languages | Separate utterance voice/locale decisions and no silent mispronunciation claim |

Do not treat voice `quality` as a listening-quality guarantee. Capture device, OS, locale, route, and system settings.

## 5. Synthesizer lifecycle matrix

| Event | Required assertion |
| --- | --- |
| Coordinator created | Synthesizer retained and delegate installed |
| Enqueue | Source revision/utterance IDs recorded before `speak` |
| Start | `didStart` mapped to current utterance/generation |
| Word/marker callback | Range/marker maps to source without stealing focus |
| Pause | `isPaused`/delegate state and UI agree |
| Continue | Current generation resumes; no duplicate utterance |
| Finish | Utterance leaves queue and state advances |
| Cancel | Pending/active state clears according to policy |
| View disappears | Queue continues or stops only by explicit contract |
| Coordinator deallocated | Speech is stopped or ownership transfer is proven |
| Source replacement | Old callbacks are ignored |

The synthesizer is not automatically retained by the system. Include a lifecycle test that would fail if the feature releases it too early.

## 6. Audio-session, interruption, and route matrix

| Scenario | Required evidence |
| --- | --- |
| System-managed speech | Other audio, interruption, mixing/ducking, and finish behavior |
| App-managed speech | Category/mode/options, activation, route, and deactivation record |
| Phone/system interruption | Pause/stop policy, preserved queue, explicit resume |
| Bluetooth/headphone connect | Intended route shown and audible fixture succeeds |
| Headphone disconnect | No unexpected private text on speaker without policy |
| AirPlay or external route | Route selection, metadata/source context, physical output |
| Route loss | “Route unavailable” state and recovery/fallback |
| Media-services reset | Session/synthesizer recovery and new generation |
| Background/lock | Behavior matches target capabilities and policy |
| Audio session activation failure | No false “Speaking” state; source/queue preserved |

A route name is a supporting diagnostic. Pair it with a known spoken phrase and a physical-device verification method.

## 7. Buffer and marker matrix

| Claim | Test |
| --- | --- |
| `write` is invoked | Callback count and request/utterance ID |
| Buffer format is known | Format/sample-rate/channel record |
| Buffers are complete | End-of-stream/finalization and frame-count check |
| Markers map to text | Marker/range fixture and UTF-16 conversion |
| File is valid | Finalize, close, reopen, decode, and playback |
| Export is private | Destination permissions, retention, deletion, metadata |
| Buffer playback is audible | Separate physical playback route test |
| Backpressure is safe | Bounded writer with cancellation and memory/thermal observation |

Do not substitute a successful buffer callback for direct output proof.

## 8. Telephony uplink matrix

Run only for a product that explicitly supports the route:

| Scenario | Required evidence |
| --- | --- |
| Default state | Uplink disabled and not hidden in generic output settings |
| Service/permission | Current system setting and app permission state recorded |
| Active call | Local call state and `AVAudioSession` state recorded |
| User action | Clear source/revision and explicit send/read action |
| Local result | Intended app/device output understood |
| Far-end result | Consent-based second-device call fixture confirms or rejects audibility |
| Call ends | Uplink stops; no lingering speech into a new call |
| Interruption/route change | Speech and call route recover according to policy |
| AI response | Generated content cannot enable uplink without acceptance |

Never test or ship this route with a hidden default or an ambiguous “speak” button.

## 9. SwiftUI, Liquid Glass, and accessibility matrix

| Check | Pass condition |
| --- | --- |
| Compact phone | Play/Pause/Stop reachable and state visible |
| iPad/Mac | Inspector/toolbar/keyboard route is coherent |
| Dynamic Type | Source and controls remain readable |
| VoiceOver | Speaking/paused/finished/route state is understandable |
| Range highlight | Focus does not jump on each callback |
| Reduce Motion | No required animation for speech state |
| Reduce Transparency/contrast | Functional controls remain legible with fallback |
| Alternate input | Stop/pause/review actions reachable |
| Generated text | Proposal visually and audibly distinguished from source |
| Privacy warning | Route/call/output implications are announced before action |

## 10. Foundation Models matrix

| Claim | Test |
| --- | --- |
| Local model available | Physical-target availability result and fallback |
| Input bounded | Source revision/range and size policy recorded |
| Typed proposal | `@Generable` decode or visible error state |
| Human review | Edit/reject/accept actions exercised |
| Stale protection | Source changes while model runs; queue rejects stale output |
| Cancellation | Model task cancellation does not enqueue speech |
| Privacy | Model input/retention/sync policy verified |
| Speech handoff | Only accepted text creates utterances |

## 11. Release matrix

| Gate | Artifact |
| --- | --- |
| Target membership | Project/target inspection and privacy/configuration record |
| Final SDK | Release compile of AVFAudio and any provider/extension symbols |
| Signing | Archive/exported entitlements and extension identity where applicable |
| TestFlight | Installed signed build on intended physical device and route |
| Accessibility | Device settings and regression results attached |
| Privacy/review | Read-aloud, call-uplink, export, and AI descriptions match actual behavior |
| Release | Build ID, route fixture, output evidence, and known limitations |

## Sources

- [Speech synthesis](https://developer.apple.com/documentation/avfaudio/speech-synthesis)
- [AVSpeechSynthesizer](https://developer.apple.com/documentation/avfaudio/avspeechsynthesizer)
- [AVSpeechSynthesizerDelegate](https://developer.apple.com/documentation/avfaudio/avspeechsynthesizerdelegate)
- [AVSpeechUtterance](https://developer.apple.com/documentation/avfaudio/avspeechutterance)
- [AVSpeechSynthesisVoice](https://developer.apple.com/documentation/avfaudio/avspeechsynthesisvoice)
- [AVSpeechSynthesizer.usesApplicationAudioSession](https://developer.apple.com/documentation/avfaudio/avspeechsynthesizer/usesapplicationaudiosession)
- [AVSpeechSynthesizer.mixToTelephonyUplink](https://developer.apple.com/documentation/avfaudio/avspeechsynthesizer/mixtotelephonyuplink)
- [AVSpeechSynthesizer.outputChannels](https://developer.apple.com/documentation/avfaudio/avspeechsynthesizer/outputchannels)
- [AVSpeechSynthesisProviderAudioUnit](https://developer.apple.com/documentation/avfaudio/avspeechsynthesisprovideraudiounit)
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
