# SwiftUI AVSpeechSynthesizer spoken-output review

This is the focused iOS 26 route for turning app-owned text into spoken output with `AVSpeechSynthesizer`, representing the utterance queue in SwiftUI, selecting a system voice and locale, responding to word/marker events, and proving that the intended physical route produced audible speech. The existing [SwiftUI audio capture and transcription review](89-swiftui-audio-capture-and-transcription.md) covers input and recognition. The [SpeechAnalyzer review](124-swiftui-speechanalyzer-live-transcription-review.md) covers live transcription. This page covers output.

The route is:

~~~text
source text / accepted AI proposal
  -> text policy and sensitive-content review
  -> utterance chunks
  -> locale/voice/quality selection
  -> AVSpeechSynthesizer queue
  -> delegate progress and cancellation
  -> app-managed or system-managed audio session
  -> physical output route / optional buffer export
  -> SwiftUI read-aloud state and accessibility feedback
~~~

`AVSpeechSynthesizer` owns synthesized speech scheduling and can control its queue. It does not own the truth of the source text, the user’s consent to hear it, or the proof that a connected speaker produced audible output. A delegate callback proves an event in the synthesizer lifecycle; a generated buffer proves buffer generation; neither is proof that a person heard the intended words.

## 1. Choose the spoken-output lane

| Outcome | Route | Ownership boundary |
| --- | --- | --- |
| Read app text aloud | `AVSpeechSynthesizer.speak(_:)` | App owns source/utterance policy; synthesizer owns queue/progress |
| Pause/resume/stop reading | `pauseSpeaking`, `continueSpeaking`, `stopSpeaking` | App maps actions to the synthesizer and publishes observed state |
| Highlight words as spoken | `AVSpeechSynthesizerDelegate` range/marker callbacks | Delegate events map to source text ranges, not a timer |
| Generate speech buffers | `write(_:toBufferCallback:)` | Buffer consumer owns storage/playback; generated buffers are not audible proof |
| Select a voice | `AVSpeechSynthesisVoice` | App chooses a compatible locale/quality; system owns installed voice inventory |
| Route to an app-managed audio graph | `usesApplicationAudioSession = true` | App configures/activates `AVAudioSession` and handles interruptions/routes |
| Let the system manage speech | `usesApplicationAudioSession = false` | System creates a separate audio session and manages speech mixing/ducking |
| Put synthesized speech into an active call | `mixToTelephonyUplink` | Explicit communication product, privacy, permission, and physical-call proof |
| Offer generated read-aloud text | Foundation Models proposal, then TTS | Model output stays a proposal until user review/acceptance |

Do not combine buffer export and direct speaking casually. A product that stores audio needs a file format, buffer lifetime, metadata, privacy, and playback route. A product that speaks immediately needs an audio-session and physical-output test.

## 2. Build a canonical spoken-output state

Keep source and synthesis state separate:

| State | Meaning |
| --- | --- |
| sourceRevision | Revision of the text the person accepted for reading |
| utteranceID | Stable ID for a semantic chunk of source text |
| voiceID/locale | Selected voice and locale identity, not just display name |
| queueIndex/queueCount | App-owned queue projection |
| status | idle, preparing, queued, speaking, paused, stopping, finished, cancelled, failed |
| characterRange | Latest delegate-highlighted range in the utterance |
| route | Current AVAudioSession route summary or system-managed status |
| sessionPolicy | app-managed or system-managed audio session |
| telephonyPolicy | explicitly off or approved communication route |
| outputMode | audible speaking or buffer generation |
| generation | Session generation used to reject stale delegate events |

The UI’s “Play” button is an intent. `isSpeaking`, `isPaused`, delegate events, and the audio-session state are observations. After `stopSpeaking(at:)` returns, wait for the delegate cancellation/finish event or the feature owner’s state transition before claiming the queue is empty.

## 3. Utterance configuration and voice identity

`AVSpeechUtterance` is the unit of synthesis. Apple documents text and attributed-text initializers, optional SSML/IPA pronunciation routes, voice, pitch, volume, rate, pre/post delays, and `prefersAssistiveTechnologySettings`. Set the properties before enqueuing; changing rate or pitch after enqueueing does not retroactively change the already queued utterance.

Use one utterance per meaningful semantic unit when the UI needs progress or different parameters:

~~~text
document paragraph / sentence
  -> policy scrub and source ID
  -> utterance 1 (intro)
  -> utterance 2 (body)
  -> utterance 3 (call to action)
~~~

Splitting too aggressively makes the queue sound unnatural and increases event/state complexity. Keeping an entire document as one utterance makes pause, source highlighting, retry, and sensitive-content handling coarse. Choose a chunk boundary that matches the review interaction.

Voice selection should validate:

- BCP 47 language/locale compatibility;
- installed voice inventory on the target device;
- voice quality and product requirements;
- accessibility settings and the role of VoiceOver/Speak Screen;
- fallback behavior when a preferred regional voice is not available;
- source-language change between queue items;
- whether pronunciation markup is necessary and safe.

`AVSpeechSynthesisVoice.speechVoices` is a device inventory snapshot. Do not persist only the localized display name as a stable identity; record language and an available voice identifier when the product needs reproducibility, then gracefully fall back if the voice is not present.

## 4. Queue and synthesizer lifetime

Apple documents that the synthesizer maintains a queue and speaks utterances in the order received. The system does not automatically retain the synthesizer, so the feature must retain it until speech concludes. This makes the owner graph explicit:

~~~text
ReadAloudCoordinator
  ├─ source revision and utterance records
  ├─ retained AVSpeechSynthesizer
  ├─ AVSpeechSynthesizerDelegate adapter
  ├─ AVAudioSession policy / route observers
  ├─ session generation
  └─ SwiftUI observable state
~~~

Do not instantiate `AVSpeechSynthesizer()` inside a button action and release it immediately. Do not attach the delegate to a view that can disappear while speech continues. Do not let two coordinators speak the same product surface unless the queue ownership is intentional and tested.

Queue actions should be typed:

| Command | Result contract |
| --- | --- |
| enqueue | Adds a source revision/utterance record; status becomes queued |
| speak | Starts or continues a queue according to the synthesizer state |
| pause | Pauses at the chosen `AVSpeechBoundary` and retains the current record |
| resume | Calls `continueSpeaking` only when the current generation is paused |
| stop | Stops at the chosen boundary, clears pending records, waits for event state |
| replace | Cancels old generation before enqueuing the new source revision |
| export | Uses `write` and a separate buffer/file owner; does not claim audible output |

## 5. Delegate events and source highlighting

`AVSpeechSynthesizerDelegate` reports start, pause, continue, finish, cancel, and individual speech units through a character range or `AVSpeechSynthesisMarker`. The range callback can drive word highlighting. The marker callback can carry richer output metadata for the current synthesis path.

Map delegate events to source IDs and generation:

~~~text
delegate callback
  -> identify synthesizer instance
  -> identify utterance object / utteranceID
  -> verify current generation and source revision
  -> map NSRange/marker to source text
  -> publish read-aloud state
  -> ignore stale callback
~~~

`NSRange` is UTF-16 based. If the UI uses Swift `String.Index` or an attributed source document, perform a safe conversion and test emoji, combining marks, links, and right-to-left text. Highlighting must not mutate the source. If an utterance was normalized, redacted, or split, retain the mapping from spoken text back to source text and mark unmapped content.

Delegate callbacks are progress signals. They are not a substitute for an audio route snapshot or an audible physical-device test. A `didFinish` callback means the synthesizer finished the utterance according to its contract, not that an external speaker was connected or that the user heard every word.

## 6. Audio-session ownership and route policy

`usesApplicationAudioSession` is a major architecture choice. When false, Apple documents that the system creates a separate audio session to manage speech, interruptions, and mixing/ducking. When true, the app manages the audio session and must configure, activate, observe, and recover it according to its product needs.

| Policy | Use when | Proof requirement |
| --- | --- | --- |
| System-managed | Simple read-aloud that should cooperate with other audio | Physical interruption/mixing test and system setting review |
| App-managed | Speech must coordinate with an audio graph, route, recording, playback, or custom state | Category/mode/activation/route/interruption test on device |
| Buffer generation | Store/process audio or feed a custom graph | Buffer format, marker, file finalization, and playback proof separately |
| Telephony uplink | Accessibility/communication product explicitly sends synthesized speech into a call | Permission/service setting, active-call, far-end and privacy proof |

For app-managed output, configure `AVAudioSession` before speaking and observe interruption/route/media-service-reset notifications. Do not assume an output route remains valid after headphones disconnect or a Bluetooth route changes. On recovery, preserve queue/source state, revalidate the route and user intent, and resume only under the declared policy.

## 7. Output channels and telephony uplink

`outputChannels` can direct generated speech to audio-session channels. This is a route-specific capability and requires a physical channel/route fixture; a populated array is not output proof.

`mixToTelephonyUplink` has no effect without an active call, but enabling it changes the privacy and communication boundary. Treat it as an explicit feature permission:

- default it off;
- explain that synthesized text can be sent into an active call;
- require the communication feature’s current entitlement/permission/configuration;
- show active-call state separately from speech state;
- test the local and far-end result with consent;
- never enable it because a model generated a suggested response;
- record the source revision and user action that authorized speaking.

This route is not “just another output channel.” It can affect another person and must not be inferred from a local delegate callback.

## 8. Buffer generation and custom speech provider boundary

`write(_:toBufferCallback:)` generates audio buffers and the marker variant supplies associated metadata for storage or further processing. A buffer callback should hand off to a bounded writer/actor and never block the speech engine on network, UI, or a large file operation.

If a product implements `AVSpeechSynthesisProviderAudioUnit`, Apple documents that the audio unit receives a provider request, renders buffers, can supply `AVSpeechSynthesisMarker` metadata, and that network access isn’t allowed in speech synthesizers. This is an extension/voice-provider route, not a shortcut for sending generated speech to an arbitrary server. Treat voice-provider target membership, extension signing, voice inventory, cancellation, render deadlines, and physical VoiceOver/Speak Screen/system discovery as separate gates.

## 9. SwiftUI and Liquid Glass read-aloud design

The native surface should make the source text primary and spoken state secondary:

- show the source text with a stable highlighted range;
- use a compact functional control group for Play/Pause/Stop and voice/speed selection;
- show “Speaking,” “Paused,” “Finished,” “Interrupted,” or “Route unavailable” as text;
- expose the current utterance/paragraph and queue progress;
- keep voice and rate settings in a sheet or inspector, not mixed into every paragraph;
- separate a generated AI proposal from the source before it is read aloud;
- apply Liquid Glass to the functional read-aloud controls when it improves hierarchy;
- provide a solid/opaque fallback for reduced transparency, high contrast, or platforms where material is not the right choice;
- preserve source readability under all text sizes and orientations.

Do not use a pulsing glass orb as the only “speaking” signal. Do not show a fake waveform when the app is using system-managed speech and has no waveform data. A progress highlight tied to delegate ranges is more honest than decorative audio visualization.

## 10. Accessibility and assistive technology

Read-aloud is often an accessibility feature. Respect assistive-technology settings and avoid fighting VoiceOver or Speak Screen. `prefersAssistiveTechnologySettings` can let assistive technology settings take precedence over utterance properties; include it in the product’s voice/rate policy.

Test:

- VoiceOver focus and speech overlap;
- Dynamic Type and long localized text;
- Switch Control, Voice Control, keyboard, pointer, and external input;
- reduced motion and transparency;
- high contrast and color differentiation;
- interruption announcements without repeating every delegate range;
- pause/stop actions reachable while a sheet or route warning is shown;
- text highlighting that does not steal accessibility focus;
- languages with right-to-left text, diacritics, emoji, and mixed scripts.

The app should not assume its own read-aloud is the same as system accessibility speech. If it can conflict with VoiceOver, explain the behavior and make pause/stop accessible.

## 11. Optional Foundation Models boundary

Foundation Models may generate a title, summary, translation candidate, or spoken response that is then passed to TTS. Keep the stages explicit:

~~~text
source text / transcript revision
  -> user requests proposal
  -> model availability and privacy check
  -> typed proposal
  -> user reviews/edits/accepts
  -> text policy and destination check
  -> utterance queue
  -> spoken output
~~~

The model output is not a source fact, and speaking it does not make it true. Retain the model/source revision, user acceptance, chosen voice, and output policy. If the model is unavailable, let the person read the original source aloud or use a deterministic template. Do not send private source text to a server merely because local model generation failed.

## 12. Proof boundary

| Claim | Evidence |
| --- | --- |
| Queue is correct | Deterministic coordinator tests for enqueue/order/replace/stop |
| Word highlight is correct | Range/marker fixtures including UTF-16 and localized text |
| Voice selection works | Physical device voice inventory and locale/quality fixture |
| System-managed speech works | Physical route, interruption, mixing/ducking, and finish test |
| App-managed speech works | Audio-session configuration, activation, route/interruption/reset test |
| Buffer export works | Buffer format/marker/file finalization/reopen test |
| Uplink route is safe | Explicit permission/service setup, active call, local/far-end consented test |
| AI spoken response is safe | Availability, bounded input, typed output, review, stale revision, cancel |
| Release is ready | Final target compile, archive/signing, TestFlight install, physical output, metadata/privacy review |

The [route worksheet](../50-capability-recipes/156-swiftui-avspeech-synthesis-spoken-output-review-route.md), [design page](../21-design-deep-dives/153-swiftui-avspeech-synthesis-spoken-output-review-design.md), [proof matrix](../60-verification/150-swiftui-avspeech-synthesis-spoken-output-proof-matrix.md), and [recipes](../70-code-recipes/168-swiftui-avspeech-synthesis-spoken-output-review-recipes.md) carry the implementation record.

## Sources

- [Speech synthesis](https://developer.apple.com/documentation/avfaudio/speech-synthesis)
- [AVSpeechSynthesizer](https://developer.apple.com/documentation/avfaudio/avspeechsynthesizer)
- [AVSpeechSynthesizerDelegate](https://developer.apple.com/documentation/avfaudio/avspeechsynthesizerdelegate)
- [AVSpeechUtterance](https://developer.apple.com/documentation/avfaudio/avspeechutterance)
- [AVSpeechSynthesisVoice](https://developer.apple.com/documentation/avfaudio/avspeechsynthesisvoice)
- [AVSpeechUtterance.rate](https://developer.apple.com/documentation/avfaudio/avspeechutterance/rate)
- [AVSpeechUtterance.pitchMultiplier](https://developer.apple.com/documentation/avfaudio/avspeechutterance/pitchmultiplier)
- [AVSpeechUtterance.prefersAssistiveTechnologySettings](https://developer.apple.com/documentation/avfaudio/avspeechutterance/prefersassistivetechnologysettings)
- [AVSpeechSynthesizer.usesApplicationAudioSession](https://developer.apple.com/documentation/avfaudio/avspeechsynthesizer/usesapplicationaudiosession)
- [AVSpeechSynthesizer.mixToTelephonyUplink](https://developer.apple.com/documentation/avfaudio/avspeechsynthesizer/mixtotelephonyuplink)
- [AVSpeechSynthesizer.outputChannels](https://developer.apple.com/documentation/avfaudio/avspeechsynthesizer/outputchannels)
- [AVSpeechSynthesizerDelegate speech events](https://developer.apple.com/documentation/avfaudio/avspeechsynthesizerdelegate)
- [Speech range delegate callback](https://developer.apple.com/documentation/avfaudio/avspeechsynthesizerdelegate/speechsynthesizer%28_%3Awillspeakrangeofspeechstring%3Autterance%3A%29)
- [Speech marker delegate callback](https://developer.apple.com/documentation/avfaudio/avspeechsynthesizerdelegate/speechsynthesizer%28_%3Awillspeak%3Autterance%3A%29)
- [Speech finish delegate callback](https://developer.apple.com/documentation/avfaudio/avspeechsynthesizerdelegate/speechsynthesizer%28_%3Adidfinish%3A%29)
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
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
