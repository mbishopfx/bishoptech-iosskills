# SwiftUI AVSpeechSynthesisProviderAudioUnit custom voice-provider extension review

This is the focused iOS 26 route for shipping a custom speech-synthesis provider as an Audio Unit extension. The [AVSpeechSynthesizer spoken-output review](125-swiftui-avspeech-synthesis-spoken-output-review.md) covers an app that speaks with a system voice. This page covers the different boundary where an extension contributes voices to the system so they can be selected by `AVSpeechSynthesizer` and assistive technologies such as VoiceOver and Speak Screen.

The route is:

~~~text
host app voice catalog
  -> App Group/shared configuration
  -> AVSpeechSynthesisProviderVoice.updateSpeechVoices()
  -> system scans the signed speech-provider extension
  -> extension speechVoices inventory
  -> AVSpeechSynthesisProviderRequest (SSML + provider voice)
  -> provider control-side synthesis preparation
  -> AUAudioUnit render block and bounded audio buffers
  -> speech markers mapped to buffer offsets
  -> system host / AVSpeechSynthesizer / VoiceOver / Speak Screen
~~~

This is an extension and system-integration contract, not a server TTS adapter. Apple explicitly documents that network access isn’t allowed in speech synthesizers. A voice appearing in the provider’s inventory proves discoverability data, not that the system can render the requested SSML, that markers align, or that a person heard correct speech.

## 1. Choose the provider lane

| Product need | Best lane | Why |
| --- | --- | --- |
| Read app-owned text immediately | `AVSpeechSynthesizer` with a system voice | The host app owns source text and queue state; no extension is needed |
| Provide a custom voice to the whole system | `AVSpeechSynthesisProviderAudioUnit` extension | The system can discover the provider voice for speech synthesis and accessibility surfaces |
| Generate a downloadable voice package | Provider extension plus a separately designed, approved resource-delivery path | The provider itself still cannot assume network access during synthesis |
| Produce a private server voice | App-owned product route with explicit server/privacy review | Do not disguise a network dependency as a system speech provider |
| Let an on-device model draft or transform text | Host-side, bounded proposal before the speech request | Model output remains reviewable text; it does not become trusted SSML automatically |

Do not select a custom provider merely to avoid implementing a small read-aloud control. The extension adds a containing app, extension target, component registration, voice inventory, App Group or other shared-state contract, render deadline, system discovery, accessibility, signing, and release obligations.

## 2. Understand the target and process shape

Apple’s custom speech synthesizer sample uses a host app and an Audio Unit extension. The host can maintain the user-facing voice list, while the extension subclasses `AVSpeechSynthesisProviderAudioUnit` and supplies voices and audio. The two targets have different lifetimes and may be loaded by system clients outside the host app’s visible UI.

Record the target shape before writing synthesis code:

| Boundary | Owner | Evidence |
| --- | --- | --- |
| Host app | Voice catalog editor, user settings, App Group writes, update notification | Host target compile, signed install, catalog mutation |
| Speech-provider extension | `AUAudioUnit` subclass, voice inventory, request/cancel/render implementation | Extension target compile, component registration, runtime load |
| System speech host | Voice discovery, settings selection, request scheduling, output route | Settings inventory, `AVSpeechSynthesizer`/accessibility exercise |
| Shared data | Minimal catalog and versioned resource state | App Group read/write and stale-schema test |
| SwiftUI host UI | Status, catalog, install/update/failure state | Dynamic Type, VoiceOver, input, and system handoff test |

An extension that compiles inside an Xcode project is not necessarily registered as the correct Audio Unit component. Validate the selected SDK, extension point, component type/subtype/manufacturer identity, `Info.plist` `AudioComponents` entry, target membership, signing, and installation artifact in the actual release target. Keep a host target and extension target in the release record.

## 3. Build a stable voice inventory

`AVSpeechSynthesisProviderVoice` is distinct from `AVSpeechSynthesisVoice`. The provider voice describes what the extension offers to its host and includes a name, identifier, primary languages, supported languages, version, package size, and optional age/gender information. Use BCP 47 language codes and treat the identifier as the stable key.

A catalog record should be explicit:

~~~text
voiceID
localizedName
primaryLanguages
supportedLanguages
version
resourceRevision
resourceSize
availability: ready | installing | unavailable | retired
~~~

Do not use only a localized display name. Two voices can have the same name in different locales, and a localized name can change without identifying the same resource. Do not put secrets, private source text, or a remote URL in the provider inventory. The system needs enough information to display and select a voice, not the product’s internal account state.

The provider’s `speechVoices` property is the inventory the system reads. If the host app adds or removes a voice, call `AVSpeechSynthesisProviderVoice.updateSpeechVoices()` after the shared catalog is durably updated. Treat the system refresh as asynchronous: keep the host UI in `published`, `refreshing`, or `not-yet-visible` state rather than promising that Settings changes immediately. Apple’s custom synthesizer sample notes that a system voice list can take time to refresh, so test a signed installation and a cold system discovery path.

When a voice is retired, preserve a deterministic fallback in the host app and tell the system only about voices the extension can actually render. A catalog entry for a missing model or audio resource is a misleading capability advertisement.

## 4. Treat the request as untrusted, versioned input

The provider receives an `AVSpeechSynthesisProviderRequest` containing an `ssmlRepresentation` and an `AVSpeechSynthesisProviderVoice`. The request is not the host app’s original `String` object. It is a system handoff with a voice selection and SSML representation.

At the control boundary:

1. capture a request generation and selected provider voice identifier;
2. verify that the voice is in the current inventory and its resource revision is ready;
3. parse only the SSML subset the provider supports;
4. bound text length, nesting, language tags, pronunciation markup, and resource work;
5. retain a source-to-SSML/range map if the host needs highlighting;
6. prepare a renderable buffer plan without touching SwiftUI or network services;
7. publish a cancellation token before starting work for the next request.

SSML is a representation, not proof that every requested tag or pronunciation will be honored. Unknown, malformed, or unsafe markup should produce a typed failure or deterministic fallback according to the product contract. Do not silently interpret arbitrary markup as executable instructions. If an on-device model proposes SSML, parse and validate it as if it came from an untrusted editor, then require user acceptance when it changes wording or pronunciation.

Keep request state separate from the host app’s AI state. A system accessibility client may request speech without the host app having a current SwiftUI screen, model session, or app-owned source revision.

## 5. Separate synthesis preparation from real-time rendering

`AVSpeechSynthesisProviderAudioUnit` receives a request through `synthesizeSpeechRequest(_:)`. Its audio is obtained through the Audio Unit render path. The provider should use the request method to select or prepare bounded synthesis state, and the render block to deliver audio under the host’s timing contract.

The separation matters:

| Operation | Safe boundary |
| --- | --- |
| Parse SSML, select resource, schedule preparation | Control side of the provider |
| Allocate render resources | `allocateRenderResources()` lifecycle |
| Generate or copy frames for the host | `internalRenderBlock`/render boundary, with real-time constraints |
| Update voice catalog | Host/shared state plus `updateSpeechVoices()` |
| Write logs, inspect diagnostics, update UI | Non-render control/diagnostic side |
| Fetch a network model or call a remote TTS service | Not allowed as a speech-synthesizer dependency |

The Audio Toolbox `AUAudioUnit` contract makes the render block a deadline-sensitive path. Cache the render block when acting as a host; for a provider subclass, implement the documented internal render boundary and keep it bounded. Do not allocate arbitrary Swift collections, take contended locks, perform file or network I/O, invoke SwiftUI, or run a Foundation Models session in the render callback. Precompute or stage the data needed for the current request, then make the callback’s work predictable for the requested frame count.

When the request’s audio is complete, report the documented offline completion action through the internal render contract. Completion is a lifecycle signal for the host; it is not an audible-output assertion. Keep a provider generation on every prepared buffer so a late render cycle cannot emit audio from a cancelled request.

## 6. Align markers with buffers

The provider can set `speechSynthesisOutputMetadataBlock` to send an array of `AVSpeechSynthesisMarker` values to the host. Markers can describe word, sentence, paragraph, phoneme, or bookmark ranges and a byte sample offset into the audio buffer.

Marker correctness is a data contract:

~~~text
SSML text range
  -> synthesis token/range
  -> generated sample span
  -> byteSampleOffset in the provider’s output format
  -> AVSpeechSynthesisMarker
  -> system word/sentence/accessibility timing
~~~

Apple documents that a host may delay speech output until markers arrive and that a later metadata block can replace marker data for an audio-buffer range. That means the provider must use stable buffer offsets and must be prepared for metadata to be delivered or revised after additional processing. Do not emit approximate markers just to make a highlight animate. A wrong word marker is worse than no marker because it misrepresents what is being spoken.

Test UTF-16 `NSRange` semantics, SSML tags that do not appear as spoken characters, punctuation, right-to-left scripts, combining marks, emoji, abbreviations, and provider fallback pronunciations. Keep a marker fixture that records the SSML, plain-text projection, output format, byte offsets, and expected word/sentence ranges.

## 7. Cancellation and stale-request control

`cancelSpeechRequest()` tells the provider to discard the current speech request. It must be a real cancellation boundary, not a Boolean that the renderer checks only after producing the entire document.

Use a generation model:

~~~text
request A starts -> generation 41
request B or cancel -> generation 42
render callback sees generation 41 -> emit silence/complete according to contract
new request B -> only generation 42 may publish buffers or markers
~~~

Cancellation should stop preparation work, prevent stale markers, release or recycle request-owned buffers, and leave the unit in a state from which the host can request another voice. Handle extension termination, host disappearance, resource deallocation, and system interruption as normal lifecycle events. Do not assume a visible host-app “Stop” button is the only cancellation source; VoiceOver, Speak Screen, Settings, and the system speech host can stop or replace a request independently.

## 8. System voice settings and assistive technology

The system scans and loads speech-provider voices. Apple documents that the voices can be used by `AVSpeechSynthesizer` and accessibility technologies such as VoiceOver and Speak Screen. The user’s system voice settings are therefore part of the product surface even when the containing app is not open.

Test the provider as a system voice:

- install the signed host app and extension on a supported physical device;
- publish a voice and wait for system discovery;
- verify the voice appears in the system Spoken Content voice settings;
- use the voice through an app-owned `AVSpeechSynthesizer` host;
- use VoiceOver and Speak Screen with ordinary text and long text;
- change the selected voice or remove the resource while a request is active;
- lock/unlock, background/foreground, interrupt, route-change, and relaunch;
- confirm that the fallback voice and user-facing error do not expose private source or resource paths.

VoiceOver is an assistive technology, not a demo player. The provider must preserve intelligible speech, predictable markers, cancellation, and low enough latency for a system client. The host app’s custom SwiftUI controls still need labels, values, hints, and actions, but those controls cannot replace testing the provider through the system accessibility client.

## 9. SwiftUI and Liquid Glass host design

The containing app should present a compact provider-management surface rather than pretending that the extension owns the entire experience:

- voice list with language, version, size, and availability;
- add/remove/update controls with explicit progress and cancellation;
- “Available to system speech” versus “available only in this app” state;
- last system-refresh request and a non-guaranteed refresh status;
- test phrase preview using the host app’s `AVSpeechSynthesizer` route;
- fallback voice and resource-missing explanation;
- privacy and storage explanation for voice packages;
- a link or instruction to the system Spoken Content settings when needed.

Use standard SwiftUI controls and apply Liquid Glass only to functional control groups or a focused status card. Keep a readable opaque fallback for reduced transparency, high contrast, large text, and platforms where the material obscures the catalog. Do not put a constantly animated glass waveform in the host UI when the provider has not supplied measurable output levels. Show real request, marker, render, and discovery states instead.

## 10. Optional on-device AI boundary

An on-device model can help a user create a pronunciation alias, normalize a short phrase, or draft a voice description. It should not decide that a voice is system-ready or mutate the render path.

Keep the proposal route:

~~~text
user text / pronunciation request
  -> model availability check
  -> bounded typed proposal
  -> SSML parser and supported-tag validation
  -> user review and acceptance
  -> provider request generation
  -> deterministic synthesis/render path
~~~

The provider extension should not depend on an AI session to answer a system accessibility request. If a model is unavailable, use the original text or a deterministic pronunciation fallback. If the model changes the words, language, or pronunciation, retain the proposal revision and acceptance record in the host app; never silently feed generated SSML to VoiceOver or Speak Screen.

## 11. Proof boundary

| Claim | Evidence |
| --- | --- |
| Provider is discoverable | Signed host/extension install, component registration, system voice inventory |
| Voice metadata is correct | Identifier/language/version/size fixture and Settings inspection |
| Voice resources are ready | Resource integrity/readiness check and missing-resource fallback |
| SSML request is handled | Valid/invalid/unsupported markup fixtures and selected-voice checks |
| Audio is rendered | Render-buffer format/frame/continuity evidence under the target host |
| Render completes | Offline completion and next-request lifecycle evidence |
| Markers are correct | Word/sentence/phoneme offset fixtures and system highlighting exercise |
| Cancellation is safe | Mid-preparation, mid-render, replacement, and extension-reload tests |
| No network dependency exists | Offline/denied-network test with bundled or approved local resources |
| Accessibility works | VoiceOver, Speak Screen, system voice settings, interruption, and long-text tests |
| SwiftUI host is native | Accessibility Inspector, Dynamic Type, reduced transparency/motion, input, and handoff evidence |
| AI assistance is safe | Availability, bounded typed proposal, validation, acceptance, stale revision, and fallback tests |
| Release is ready | Host and extension archive/signing, TestFlight install, physical-device system discovery and speech output |

The [route worksheet](../50-capability-recipes/157-swiftui-avspeech-synthesis-provider-extension-review-route.md), [design page](../21-design-deep-dives/154-swiftui-avspeech-synthesis-provider-extension-review-design.md), [proof matrix](../60-verification/151-swiftui-avspeech-synthesis-provider-extension-proof-matrix.md), and [recipes](../70-code-recipes/169-swiftui-avspeech-synthesis-provider-extension-review-recipes.md) carry the implementation record.

## Sources

- [AVSpeechSynthesisProviderAudioUnit](https://developer.apple.com/documentation/avfaudio/avspeechsynthesisprovideraudiounit)
- [AVSpeechSynthesisProviderRequest](https://developer.apple.com/documentation/avfaudio/avspeechsynthesisproviderrequest)
- [AVSpeechSynthesisProviderVoice](https://developer.apple.com/documentation/avfaudio/avspeechsynthesisprovidervoice)
- [AVSpeechSynthesisProviderVoice.updateSpeechVoices()](https://developer.apple.com/documentation/avfaudio/avspeechsynthesisprovidervoice/updatespeechvoices%28%29)
- [AVSpeechSynthesisMarker](https://developer.apple.com/documentation/avfaudio/avspeechsynthesismarker)
- [speechSynthesisOutputMetadataBlock](https://developer.apple.com/documentation/avfaudio/avspeechsynthesisprovideraudiounit/speechsynthesisoutputmetadatablock)
- [synthesizeSpeechRequest(_:)](https://developer.apple.com/documentation/avfaudio/avspeechsynthesisprovideraudiounit/synthesizespeechrequest%28_%3A%29)
- [cancelSpeechRequest()](https://developer.apple.com/documentation/avfaudio/avspeechsynthesisprovideraudiounit/cancelspeechrequest%28%29)
- [Creating a custom speech synthesizer](https://developer.apple.com/documentation/avfaudio/creating-a-custom-speech-synthesizer)
- [Creating an audio unit extension](https://developer.apple.com/documentation/avfaudio/creating-an-audio-unit-extension)
- [AUAudioUnit](https://developer.apple.com/documentation/audiotoolbox/auaudiounit)
- [AUAudioUnit.renderBlock](https://developer.apple.com/documentation/audiotoolbox/auaudiounit/renderblock)
- [AUInternalRenderBlock](https://developer.apple.com/documentation/audiotoolbox/auinternalrenderblock)
- [AUAudioUnit.renderingOffline](https://developer.apple.com/documentation/audiotoolbox/auaudiounit/isrenderingoffline)
- [VoiceOver](https://developer.apple.com/documentation/accessibility/voiceover/)
- [VoiceOver Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/voiceover)
- [Accessibility Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessible controls](https://developer.apple.com/documentation/swiftui/accessible-controls)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
