# SwiftUI custom speech-provider extension proof matrix

Use this matrix for an `AVSpeechSynthesisProviderAudioUnit` extension and its containing SwiftUI app. It keeps system discovery, provider rendering, marker timing, accessibility-client behavior, and release evidence separate. A green host-app preview is not a green system voice release.

## Evidence record

| Field | Value |
| --- | --- |
| Product / target | `TBD` |
| Host app target / build | `TBD` |
| Speech-provider extension target / build | `TBD` |
| SDK / deployment target | `iOS 26 / TBD` |
| Component identity | type / subtype / manufacturer: `TBD` |
| App Group | `TBD` |
| Voice/resource revision | `TBD` |
| Physical device / OS | `TBD` |
| System accessibility settings | VoiceOver / Speak Screen / Spoken Content: `TBD` |
| TestFlight build | `TBD` |
| Archive/signing evidence | `TBD` |
| Evidence owner / date | `TBD` |

## Claim-to-evidence matrix

| ID | Claim | Minimum evidence | Does not prove it |
| --- | --- | --- | --- |
| P1 | Host and extension targets are configured | Final-SDK compile, target membership, `Info.plist`/component inspection, signed archive | A source file or Xcode template alone |
| P2 | The system can discover the provider | Signed install, extension registration, system voice inventory after refresh | Extension embedded in an unsigned or uninstalled build |
| P3 | Voice metadata is stable and truthful | Identifier/language/version/size fixture and Settings inspection | A localized name or a catalog JSON dump alone |
| P4 | Voice resources are ready | Integrity/readiness check, missing-resource negative fixture, fallback | A ready Boolean without a render request |
| P5 | Host catalog publication works | App Group write, `updateSpeechVoices()` invocation, system refresh observation | Calling the update method without system discovery |
| P6 | Valid SSML renders | Request fixture, provider selection, render frames, completion, physical/system playback | SSML parser output alone |
| P7 | Invalid/unsupported SSML fails safely | Malformed tag, unsupported tag, oversized input, wrong language, and recovery fixture | A single happy-path phrase |
| P8 | Render buffers have the correct contract | Format/channel/frame count, continuity, status, under/overrun observation | A non-empty buffer or file size |
| P9 | Requests complete | Internal render completion evidence and next-request test | A timeout or UI spinner ending |
| P10 | Cancellation is correct | Cancel during preparation/render, replacement, no stale frames/markers, restart | A Stop button changing SwiftUI state |
| P11 | Markers align with audio | Word/sentence/paragraph/phoneme/bookmark range and byte-offset fixtures | A marker object existing |
| P12 | Marker revision is safe | Delayed/replacement marker block for same buffer range and generation | A first approximate marker set |
| P13 | No network is required | Offline/denied-network run with local resources and no remote dependency | A run while the network happens to be available |
| P14 | VoiceOver and Speak Screen work | Physical-device system settings, long/localized text, interruption, route, and cancellation tests | Host-app Preview output |
| P15 | SwiftUI host is accessible | Accessibility Inspector, VoiceOver labels/actions/values, Dynamic Type, Switch Control/keyboard/pointer | A glass screenshot |
| P16 | Liquid Glass remains usable | Reduced transparency/high contrast/large text and opaque fallback fixture | Default appearance only |
| P17 | AI assistance is safe | Availability check, typed proposal, SSML validation, acceptance/rejection, stale revision, deterministic fallback | A model response or spoken generated phrase |
| P18 | Privacy is understood | Resource storage/source-text policy, diagnostics redaction, no-network review, user copy | An App Group identifier by itself |
| P19 | Release artifact works | Archive/signing, TestFlight install, host plus extension discovery, physical system speech | Simulator success or archive key |

## Deterministic catalog and publication tests

Create fixtures for:

- one voice with a stable identifier and one localized display name;
- primary and supported BCP 47 languages;
- version/resource revision changes;
- a missing voice resource;
- a retired voice with fallback;
- adding and removing a voice from the host catalog;
- repeated `updateSpeechVoices()` calls;
- system refresh pending and system-visible observations;
- malformed or incomplete catalog records.

The expected result should identify the catalog revision and not rely on row order. Verify that the extension reports only renderable voices. Record whether Settings shows the voice after a cold launch, a host relaunch, and a device restart.

## Request and SSML tests

| Fixture | Expected result |
| --- | --- |
| Plain short phrase | one valid request and audible/system output |
| Sentence and paragraph markup | supported tags render and marker ranges match |
| Unknown tag | deterministic reject or flatten policy |
| Malformed XML/SSML | typed failure, no stale output |
| Unsupported language | documented fallback or typed failure |
| Pronunciation/phoneme markup | bounded output with source mapping |
| Long text | bounded chunk or documented length failure |
| Emoji/combining marks | correct range mapping or marker suppression |
| Right-to-left/mixed script | correct text and language behavior |
| AI-proposed SSML | proposal cannot render until accepted and validated |

Capture the request’s provider voice identifier, SSML revision, source revision when available, and generation. A system accessibility client may not provide the host app’s source record; the provider must still validate and render from its request contract.

## Render and completion tests

Verify the provider under the actual host render path with:

- minimum, typical, and maximum frame counts;
- silence and discontinuity conditions;
- resource allocation, reset, deallocation, and reallocation;
- output format/channel changes;
- preparation completion before render;
- delayed resource work;
- repeated requests with different voices;
- system interruption and route changes;
- host/extension termination and re-instantiation;
- offline render completion action;
- no render-side network, disk I/O, model inference, UI work, or unbounded allocation.

Record frames, sample rate, channel count, render status, generation, and whether the result was only buffer evidence or also physical/system audible evidence.

## Marker proof fixtures

For each fixture, record:

~~~text
marker type
request SSML
plain-text projection
NSRange location/length
provider output format
byteSampleOffset
buffer range/generation
expected system highlight/timing
~~~

Include markers that arrive before audio, with audio, and after additional processing. Test metadata replacement for the same buffer range. Prove that a cancelled generation cannot deliver markers after a replacement request. When the provider cannot guarantee a correct mapping, omit the marker rather than highlight the wrong word.

## Cancellation and recovery tests

| Scenario | Required observation |
| --- | --- |
| Cancel before preparation completes | preparation stops; no stale buffer or marker |
| Cancel during render | current generation is discarded or completed according to contract |
| Replace request with another voice | old generation cannot publish after replacement |
| Remove selected voice | fallback is selected and system inventory updates |
| Extension deallocation | resources are released and next request can allocate |
| Host app terminates | system client does not receive corrupted state |
| System interruption | request state and retry/fallback are defined |
| Bluetooth/output route change | audio remains safe; physical route result is recorded |

## System accessibility and physical-output matrix

| Client | Fixture | Evidence |
| --- | --- | --- |
| Host `AVSpeechSynthesizer` | selected provider voice, short/long text, pause/stop | physical audio and host logs |
| VoiceOver | labels, web-like text, punctuation, localization, navigation | physical device recording/observer notes and accessibility state |
| Speak Screen | long scrolling content and cancellation | physical device observation |
| Spoken Content settings | add/remove/update voice and refresh | Settings screenshot or captured test record |
| Headphones/Bluetooth | connect/disconnect during request | route notification plus audible result |
| Speaker/receiver | output-route selection | physical output evidence |
| Background/lock | system client and app lifecycle | lifecycle/event record |

Do not use a simulator as the final proof for microphone/speaker routes, VoiceOver timing, Bluetooth recovery, or system speech voice discovery.

## SwiftUI and accessibility evidence

- [ ] Voice rows expose stable labels, values, and actions.
- [ ] Publication pending, system-visible, resource missing, and render failed are distinct text states.
- [ ] Dynamic Type does not hide language, version, or recovery actions.
- [ ] Reduced transparency and high contrast have a readable fallback.
- [ ] VoiceOver focus remains stable when catalog state changes.
- [ ] Keyboard, pointer, Voice Control, and Switch Control can reach the important actions.
- [ ] Preview waveform or animation is not the only state signal.
- [ ] System accessibility testing is performed outside the host app’s SwiftUI screen.

## AI and privacy evidence

If AI is included, retain:

- model availability and model revision;
- bounded input and source revision;
- typed proposal and SSML validation result;
- user acceptance/rejection and edit history;
- provider request generation;
- deterministic fallback result;
- no-network/retention behavior.

The provider’s voice inventory, render callback, and marker stream remain deterministic product evidence. A Foundation Models proposal is not a voice resource, a system entitlement, a linguistically verified pronunciation, or audible-output proof.

## Release checklist

- [ ] Final iOS 26 SDK compile for host and extension.
- [ ] Extension `Info.plist`/component identity inspected in the archived product.
- [ ] Host and extension signing/provisioning/App Group evidence captured.
- [ ] TestFlight installation preserves extension discovery.
- [ ] System Spoken Content voice inventory is tested after installation.
- [ ] VoiceOver and Speak Screen are tested on a physical device.
- [ ] Physical speaker/headphone/Bluetooth interruption and route evidence captured.
- [ ] Privacy/resource diagnostics do not leak private text or internal paths.
- [ ] App Store metadata and accessibility claim evidence are reviewed separately.

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
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
