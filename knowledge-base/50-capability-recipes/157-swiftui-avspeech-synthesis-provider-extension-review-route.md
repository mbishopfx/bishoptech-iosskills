# SwiftUI custom speech-provider extension route worksheet

Use this worksheet when a product needs a custom voice that can be discovered by system speech services, `AVSpeechSynthesizer`, VoiceOver, or Speak Screen. It is intentionally stricter than an app-only read-aloud route. Fill it in before creating the extension target.

The generic system-voice route is documented in the [AVSpeechSynthesizer spoken-output review](../42-framework-deep-dives/125-swiftui-avspeech-synthesis-spoken-output-review.md). The provider-extension route adds system discovery, voice inventory, App Group/target boundaries, Audio Unit rendering, marker offsets, no-network enforcement, and accessibility-client proof.

## Route record

| Field | Decision |
| --- | --- |
| Product outcome | `TBD` |
| Custom provider required? | yes / no / decision pending |
| Host app target | `TBD` |
| Speech-provider extension target | `TBD` |
| Deployment target / SDK | `iOS 26 / TBD final SDK` |
| Provider component identity | type / subtype / manufacturer: `TBD` |
| Voice inventory source | App Group / bundled catalog / other approved local source |
| Voice resource policy | bundled / local package / other approved non-network runtime source |
| Primary languages | `TBD` BCP 47 list |
| Supported languages | `TBD` BCP 47 list |
| System refresh path | `AVSpeechSynthesisProviderVoice.updateSpeechVoices()` |
| SSML support | supported tags, bounds, fallback: `TBD` |
| Marker policy | word / sentence / paragraph / phoneme / bookmark: `TBD` |
| Output format | sample rate / channels / PCM contract: `TBD` |
| App Group identifier | `TBD` or not required |
| AI proposal lane | none / bounded host-side proposal / other: `TBD` |
| Accessibility clients | `AVSpeechSynthesizer`, VoiceOver, Speak Screen, other: `TBD` |
| Physical proof device | `TBD` |

## 1. Confirm the route is justified

- [ ] The requirement is “a custom voice is selectable by system speech,” not merely “speak text in one app.”
- [ ] The extension’s no-network runtime boundary is compatible with the voice resource design.
- [ ] The product can support a host app and a separate extension target through signing and release.
- [ ] VoiceOver and Speak Screen are first-class test clients.
- [ ] The team accepts render-deadline and Audio Unit lifecycle obligations.
- [ ] A deterministic fallback system voice or user-facing failure exists.

If any item is false, use the app-only `AVSpeechSynthesizer` route or redesign the requirement before writing an Audio Unit extension.

## 2. Target and registration worksheet

| Gate | Record |
| --- | --- |
| Host app target exists and owns catalog UI | target name / commit / status |
| Audio Unit Extension target exists | target name / extension point / status |
| `AVSpeechSynthesisProviderAudioUnit` subclass and factory | class / module |
| `AudioComponents` `Info.plist` entry | type / subtype / manufacturer / version |
| App Group capability | identifier / host membership / extension membership |
| Resource target membership | package or asset / host / extension |
| Signing and provisioning | host / extension profiles and entitlements |
| Installed artifact | app version / build / extension embedded path |
| System discovery | Settings inventory result / refresh timestamp |

Do not infer extension discovery from Xcode’s project navigator. Prove it from the signed installed artifact and system voice settings.

## 3. Voice catalog contract

Create a versioned local record for each provider voice:

~~~text
VoiceRecord {
  identifier
  localizedName
  primaryLanguages[]
  supportedLanguages[]
  voiceVersion
  resourceRevision
  resourceSize
  readiness
}
~~~

| Rule | Decision/evidence |
| --- | --- |
| Identifier is stable across app launches | fixture |
| Localized name is presentation only | review |
| Primary/supported languages are valid BCP 47 codes | locale test |
| Version changes when voice output changes | migration test |
| Resource size is truthful or omitted | catalog test |
| Missing resources are not advertised as ready | negative fixture |
| Retired voices have a fallback | migration test |
| Catalog contains no private source text or secrets | privacy review |

After a durable catalog change, call `updateSpeechVoices()`. Record the update request and wait for a system inventory observation; do not call the host app’s local catalog “system-visible” until the system client confirms it.

## 4. Request and SSML contract

| Input | Required handling |
| --- | --- |
| `ssmlRepresentation` | Parse the supported subset; reject or deterministically flatten unsupported tags |
| Provider voice | Verify identifier and resource revision against the extension inventory |
| Language tags | Validate supported language and fallback policy |
| Pronunciation/phoneme markup | Bound, preserve source mapping, and test locale behavior |
| Text length | Enforce a product limit and a defined chunking/retry policy |
| AI-generated markup | Mark as proposal; validate and require acceptance before system speech |
| Source revision | Keep a generation so stale work cannot publish buffers or markers |

The provider should never assume that the request came from the containing app. It may be created by an accessibility or system speech client. Do not require SwiftUI state, app login, a Foundation Models session, or an app-owned network connection to fulfill a valid local request.

## 5. Render and buffer contract

| Stage | Owner | Proof |
| --- | --- | --- |
| Request preparation | Provider control-side state | selected voice, parsed SSML, generation |
| Resource preparation | Local provider resource manager | package/readiness and bounded-work evidence |
| Render-resource allocation | `AUAudioUnit` lifecycle | allocate/deallocate/reset fixture |
| Audio delivery | internal render block | frame count, format, continuity, status |
| Metadata delivery | `speechSynthesisOutputMetadataBlock` | marker range/offset fixture |
| Completion | provider render contract | offline completion and next-request test |
| Cancellation | provider request generation | mid-request silence/discard/replacement test |

Do not put file I/O, networking, UI updates, model inference, unbounded allocation, or a contended lock in the render path. Keep control-side preparation and render-side delivery separate. A generated buffer is evidence of provider output, not evidence that the system output route was audible.

## 6. Marker worksheet

| Marker type | Source range representation | Offset contract | Expected client behavior |
| --- | --- | --- | --- |
| Word | UTF-16 range in request text | byte sample offset | word highlighting |
| Sentence | UTF-16 range | byte sample offset | sentence progress |
| Paragraph | UTF-16 range | byte sample offset | larger navigation |
| Phoneme | text/phoneme identity | byte sample offset | specialized timing |
| Bookmark | bookmark name | byte sample offset | semantic event |

Record the output sample format and how the provider calculates `byteSampleOffset`. Include tags removed by SSML parsing, whitespace normalization, punctuation, emoji, combining marks, right-to-left scripts, and fallback pronunciations in the fixture set. If marker data is revised after additional processing, the replacement must identify the same buffer range and generation.

## 7. Cancellation and resource recovery

- [ ] `cancelSpeechRequest()` stops the current request’s preparation.
- [ ] In-flight render state cannot publish stale generation audio.
- [ ] Markers from a cancelled request are suppressed or clearly invalidated.
- [ ] Resources are returned or recycled after cancellation.
- [ ] A new voice request can start after cancellation.
- [ ] `deallocateRenderResources()` leaves the unit restartable.
- [ ] Extension termination and host disappearance are recoverable.
- [ ] Voice removal/update while speaking produces a defined fallback.

Use explicit state such as `idle`, `preparing`, `rendering`, `cancelling`, `completed`, and `failed`. A Boolean `isBusy` is not enough to distinguish a request that finished from a request that was replaced.

## 8. Host SwiftUI route

| Surface | State it may own |
| --- | --- |
| Voice list | catalog records and stable selection |
| Resource action | installing/updating/removing/cancelled/failed |
| Publication status | update requested/system refresh pending/system-visible |
| Preview | host `AVSpeechSynthesizer` lifecycle and local range highlight |
| System handoff | instructions to test Spoken Content/VoiceOver/Speak Screen |
| Diagnostics | copied proof record, not raw private state |
| AI sheet | typed pronunciation/SSML proposal and acceptance |

Apply Liquid Glass to a small functional toolbar or publication card. Keep the voice catalog readable and resilient to Dynamic Type and reduced transparency. Use `accessibilityLabel`, `accessibilityValue`, and named actions for rows and controls. Do not make a decorative waveform the only evidence of rendering or availability.

## 9. On-device AI route

If using Foundation Models in the host app:

1. check model availability and the selected target/device;
2. pass only the bounded text and explicit pronunciation task;
3. request a typed proposal, not an unstructured provider command;
4. validate SSML tags, language, length, and source revision;
5. show the original and proposed wording/markup;
6. require acceptance before the host requests speech;
7. use deterministic fallback when the model is unavailable;
8. never make the provider extension depend on model inference.

Record `modelVersion`, `sourceRevision`, `proposalID`, acceptance, and provider request generation when the proposal affects speech. Do not claim that AI-generated pronunciation is linguistically correct without a human or deterministic review fixture.

## 10. Proof package

The route is ready for implementation only when the record has:

- [ ] host and extension target matrix;
- [ ] component registration and signing evidence;
- [ ] voice inventory and `updateSpeechVoices()` evidence;
- [ ] system Settings discovery evidence;
- [ ] request/SSML positive and negative fixtures;
- [ ] render format/frame/completion evidence;
- [ ] marker alignment evidence;
- [ ] cancellation and replacement evidence;
- [ ] offline/no-network evidence;
- [ ] VoiceOver and Speak Screen evidence;
- [ ] SwiftUI accessibility and Liquid Glass fallback evidence;
- [ ] optional AI proposal/accept/reject/fallback evidence;
- [ ] physical-device output evidence;
- [ ] archive, signed install, TestFlight, and release evidence.

## Sources

- [Creating a custom speech synthesizer](https://developer.apple.com/documentation/avfaudio/creating-a-custom-speech-synthesizer)
- [Creating an audio unit extension](https://developer.apple.com/documentation/avfaudio/creating-an-audio-unit-extension)
- [AVSpeechSynthesisProviderAudioUnit](https://developer.apple.com/documentation/avfaudio/avspeechsynthesisprovideraudiounit)
- [AVSpeechSynthesisProviderRequest](https://developer.apple.com/documentation/avfaudio/avspeechsynthesisproviderrequest)
- [AVSpeechSynthesisProviderVoice](https://developer.apple.com/documentation/avfaudio/avspeechsynthesisprovidervoice)
- [AVSpeechSynthesisProviderVoice.updateSpeechVoices()](https://developer.apple.com/documentation/avfaudio/avspeechsynthesisprovidervoice/updatespeechvoices%28%29)
- [AVSpeechSynthesisMarker](https://developer.apple.com/documentation/avfaudio/avspeechsynthesismarker)
- [speechSynthesisOutputMetadataBlock](https://developer.apple.com/documentation/avfaudio/avspeechsynthesisprovideraudiounit/speechsynthesisoutputmetadatablock)
- [synthesizeSpeechRequest(_:)](https://developer.apple.com/documentation/avfaudio/avspeechsynthesisprovideraudiounit/synthesizespeechrequest%28_%3A%29)
- [cancelSpeechRequest()](https://developer.apple.com/documentation/avfaudio/avspeechsynthesisprovideraudiounit/cancelspeechrequest%28%29)
- [AUAudioUnit](https://developer.apple.com/documentation/audiotoolbox/auaudiounit)
- [AUAudioUnit.renderBlock](https://developer.apple.com/documentation/audiotoolbox/auaudiounit/renderblock)
- [AUInternalRenderBlock](https://developer.apple.com/documentation/audiotoolbox/auinternalrenderblock)
- [AUAudioUnit.renderingOffline](https://developer.apple.com/documentation/audiotoolbox/auaudiounit/isrenderingoffline)
- [VoiceOver](https://developer.apple.com/documentation/accessibility/voiceover/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
