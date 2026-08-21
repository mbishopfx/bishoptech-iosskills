# SwiftUI AVSpeechSynthesizer spoken-output review route

Choose this route when the outcome is “read accepted app text aloud, let the person control the queue, and optionally produce a reviewed audio artifact or communication output.” It is distinct from live speech recognition: the source text is already present, and `AVSpeechSynthesizer` produces output.

The route is:

~~~text
source / accepted proposal
  -> source revision and text policy
  -> utterance chunking
  -> locale/voice selection
  -> retained AVSpeechSynthesizer
  -> delegate state/range events
  -> audio-session and route policy
  -> direct speech or bounded buffer export
  -> SwiftUI read-aloud review
  -> physical output and signed-release proof
~~~

## 1. Choose the output lane

| Product need | Starting route | Keep separate |
| --- | --- | --- |
| Immediate read-aloud | `speak(_:)` | Source revision, queue state, physical route |
| Pause/resume/stop | Synthesizer control methods | User intent versus delegate observation |
| Word highlighting | Delegate range/marker callbacks | UTF-16/source-range mapping |
| Save or process speech | `write` buffer callbacks | File/container/marker/finalization and later playback |
| Custom system-discovered voice | `AVSpeechSynthesisProviderAudioUnit` extension | Extension target, voice inventory, render/cancel proof |
| Active-call speech | `mixToTelephonyUplink` | Communication permission, call state, far-end consent and proof |
| AI-generated spoken response | Foundation Models proposal then TTS | User review, source/model revision, stale rejection |

Do not route arbitrary generated text to the phone call or a connected speaker without an explicit user-facing capability and privacy record.

## 2. Write the route contract

| Field | Record |
| --- | --- |
| Target | iOS 26 deployment target, device family, final SDK |
| Source | App text, transcript revision, document selection, or accepted AI proposal |
| Text policy | Redaction, pronunciation markup, SSML/IPA, truncation/chunking |
| Locale/voice | Requested language, fallback, voice identifier, quality |
| Queue | Append/replace, semantic chunk size, cancel behavior |
| Audio session | System-managed or app-managed; category/mode/options and activation |
| Route | Built-in, headphones, Bluetooth, AirPlay, channels, or call uplink |
| Output mode | Direct speak or buffer generation/export |
| Accessibility | Assistive-technology settings, VoiceOver overlap, focus/highlight |
| AI | Trigger, input bounds, typed output, acceptance, stale revision |
| Proof | Device/route/fixture, interruption, archive, TestFlight, release |

If the product cannot say whether it is speaking or generating buffers, stop at a design/reducer fixture.

## 3. Preflight the target

1. Confirm AVFAudio is linked to the target that owns spoken output.
2. Confirm the deployment target and final SDK; do not infer API availability from a different platform.
3. Decide whether the app manages `AVAudioSession` or lets the speech synthesizer use a separate system session.
4. Decide whether the feature is an accessibility/read-aloud feature, a media feature, a communication feature, or a custom voice-provider extension.
5. Keep any telephony uplink capability in a separate target/feature policy where possible.
6. Create deterministic source/utterance fixtures for queue, range mapping, cancellation, and localization before testing a speaker.

## 4. Step 1 — create source revisions and utterances

Before enqueuing:

1. Capture the accepted source revision and origin.
2. Apply the product’s sensitive-text and pronunciation policy.
3. Split text into meaningful utterance chunks.
4. Assign stable `utteranceID` and source range mapping.
5. Resolve voice/locale and record fallback.
6. Set rate, pitch, volume, pre/post delays, and assistive-technology preference before enqueueing.
7. Enqueue through one retained coordinator.

If the source changes after enqueueing, do not mutate the source object in place and hope the old queue notices. Cancel or replace the old generation, then enqueue the new revision with fresh IDs.

## 5. Step 2 — own one synthesizer and delegate

Create a long-lived `ReadAloudCoordinator` that retains `AVSpeechSynthesizer` and a delegate adapter. Keep the delegate alive for the full queue. Every callback should carry:

~~~text
synthesizer identity
utterance identity
source revision
session generation
event type
character range or marker
timestamp
~~~

Reject stale callbacks. A view’s `onDisappear` should not stop speech unless the feature contract says leaving the surface stops the queue. A second screen that wants to control the same queue should send typed commands to the coordinator.

## 6. Step 3 — configure audio-session policy

### System-managed speech

Set `usesApplicationAudioSession` to false when the simple product wants the system to create a separate session and manage speech interruption/mixing/ducking. Test the actual behavior with other audio and phone/system interruptions.

### App-managed speech

Set `usesApplicationAudioSession` to true when the app must coordinate speech with playback, recording, route selection, a custom graph, or explicit app state. Configure and activate `AVAudioSession` before speaking and observe interruption, route-change, and media-services-reset notifications.

Never claim that an active audio session means a speaker is audible. Capture a physical fixture with the intended route.

## 7. Step 4 — model direct speaking and buffer export separately

| Direct speaking | Buffer export |
| --- | --- |
| `speak(_:)` queue controls | `write(_:toBufferCallback:)` callbacks |
| Delegate start/pause/finish/cancel | Buffer format/lifetime and marker metadata |
| Physical route/interruption proof | File/container/flush/reopen/playback proof |
| Output route can be system/app managed | Consumer owns storage or custom graph |
| No file unless the product adds one | Generated buffer is not audible proof |

If the product uses both, use separate state and evidence. Do not show “Saved audio” when the only result was a direct `didFinish` callback.

## 8. Step 5 — handle route, interruption, and queue recovery

On interruption or route change:

1. mark the current generation interrupted;
2. preserve source and queue state;
3. stop or pause according to product policy;
4. inspect the current route and audio-session status;
5. rebuild/activate app-managed session if needed;
6. resume only after the user policy allows it;
7. publish the observed state and any skipped/unspoken range.

Do not automatically resume a sensitive read-aloud message into a newly connected Bluetooth device or an active call. Route change is a privacy event as well as an audio event.

## 9. Step 6 — optional call output

Only use `mixToTelephonyUplink` in a communication feature with an explicit call-state and consent contract:

- default the property off;
- disclose that speech may be audible to call participants;
- prove the service/permission setting and active call;
- distinguish local speaker output from far-end uplink;
- keep a clear stop action;
- prevent background/model-generated text from enabling uplink silently;
- record the accepted source revision and the user action;
- test call start/end and audio-session interruption.

Treat this as a separate route from read-aloud. The source, audience, and side effect are different.

## 10. Step 7 — SwiftUI review surface

Publish an observable state model with:

~~~text
sourceRevision
currentUtteranceID
queueCount
status
highlightedRange
voiceName/locale/quality
rate/pitch policy
audioSessionPolicy
routeSummary
exportState
telephonyPolicy
proposalState
error/recoveryAction
~~~

Keep source text readable, use stable IDs for highlights, and make Play/Pause/Stop visible in the safe area. Apply Liquid Glass only to functional controls, with an opaque fallback and accessible labels. Use a sheet/inspector for voice and queue configuration.

## 11. Step 8 — AI proposal boundary

If a Foundation Models session creates a spoken response:

1. require a user action;
2. pass only bounded, permitted source text;
3. request a typed proposal;
4. check model availability/error/cancellation;
5. show generated status and source/model revision;
6. let the person edit/reject/accept;
7. revalidate that the source has not changed;
8. create utterances only after acceptance.

If model output is stale or unavailable, keep original text and manual read-aloud available. A model response is not an audio permission and an utterance is not a fact check.

## 12. Verification order

1. Pure queue and UTF-16 range reducer tests.
2. SwiftUI previews for ready/queued/speaking/paused/interrupted/finished/route-unavailable/proposal states.
3. Final-SDK target compile and delegate conformance.
4. Device voice inventory and locale fallback.
5. Direct speech on built-in speaker, wired/Bluetooth headphones, and intended route.
6. Pause/continue/stop at word and sentence boundaries.
7. Interruption, route change, output-channel, and app-managed session fixtures.
8. Buffer generation, file finalization/reopen, and separate playback proof.
9. Accessibility and alternate-input checks.
10. Optional AI proposal, stale revision, cancellation, and privacy review.
11. Archive, signing, TestFlight install, physical output, and release evidence.

Use the [spoken-output proof matrix](../60-verification/150-swiftui-avspeech-synthesis-spoken-output-proof-matrix.md) as the acceptance record.

## Route record template

~~~text
Feature:
Target / SDK / deployment:
Source revision and text policy:
Utterance chunking rule:
Locale / voice / quality / fallback:
Rate / pitch / volume / assistive-technology policy:
Queue owner and session generation:
System-managed or app-managed audio session:
Output route / channel / AirPlay policy:
Direct speaking versus buffer export:
Telephony uplink: off / explicit communication route:
Interruption and route recovery:
SwiftUI accessibility and Liquid Glass fallback:
AI proposal trigger / schema / acceptance:
Physical-device fixture:
Archive/TestFlight/release evidence:
Open SDK questions:
~~~

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
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
