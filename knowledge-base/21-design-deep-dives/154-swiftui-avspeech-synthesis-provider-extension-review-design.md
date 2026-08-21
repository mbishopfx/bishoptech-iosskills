# SwiftUI custom speech-provider extension design review

This page translates the [custom speech-provider extension deep dive](../42-framework-deep-dives/126-swiftui-avspeech-synthesis-provider-extension-review.md) into a native SwiftUI and Liquid Glass design system. The containing app manages the voice catalog and diagnostics. The speech-provider extension is a system-facing audio component. Keep those surfaces distinct so the app does not imply that a catalog row, a glass preview, or an AI suggestion proves system speech works.

## 1. Design the system voice contract first

There are three user-visible meanings that should never be collapsed into one label:

| State | Honest language |
| --- | --- |
| App can speak with a system voice | “Read aloud in this app” |
| Provider voice is published by the extension | “Available to system speech” |
| System has not refreshed or cannot load the voice | “Waiting for system voice list” or a concrete failure |

The host app should not claim “installed everywhere” because the extension is present in the app bundle. The user may need to wait for system discovery, the voice resource may be unavailable, or a system client may apply a different voice setting. Make the system handoff visible and bounded.

## 2. Native host-app hierarchy

Use the platform’s information hierarchy:

~~~text
NavigationStack
  └─ Voice Provider
       ├─ availability banner
       ├─ published voice cards
       │    ├─ name and language
       │    ├─ version and size
       │    ├─ ready/installing/unavailable state
       │    └─ remove/update/test action
       ├─ system voice handoff
       ├─ privacy and storage explanation
       └─ diagnostics / proof details
~~~

The voice name and language are primary. Version, package size, resource revision, last refresh request, and extension diagnostics are secondary. A “Test voice” action belongs in the host app, but label it as an app preview; it does not replace VoiceOver or Speak Screen testing.

For a small catalog, use a `List` or grouped form with native rows. For a larger catalog, use a searchable collection with a stable provider voice identifier. Keep selection separate from installation and publication. A user can select a voice in the host app without the system having refreshed its inventory yet.

## 3. State language should expose the real lifecycle

Use state labels that describe the system boundary:

~~~text
catalog empty
  -> voice draft
  -> resource preparing
  -> provider ready
  -> publish requested
  -> system refresh pending
  -> visible to system speech
  -> request rendering
  -> request cancelled / completed / failed
~~~

Do not turn every non-ready state into a generic spinner. Examples:

- “Preparing voice package” means the host is doing local work.
- “Published; waiting for system refresh” means the host asked the system to rescan, not that it has completed.
- “Available to system speech” means the system inventory test found the voice.
- “Preview failed: missing resource” means the provider could not fulfill the request.
- “System client cancelled” means the request ended outside the visible SwiftUI control.

Expose retry and fallback actions only when they have a meaningful effect. A second `updateSpeechVoices()` call is not a substitute for a missing signed extension or resource.

## 4. Use Liquid Glass as functional grouping

Liquid Glass should clarify the host controls, not imitate a floating voice orb. Good uses include:

- a compact publication status card;
- a small control group for Preview, Pause, and Stop;
- a focused voice-management toolbar;
- a contextual sheet action for “Open Spoken Content settings.”

Keep the catalog text on a readable surface. Avoid stacking multiple translucent glass cards over a busy waveform, animated model output, or long text. The extension has no reason to render a glass UI in its audio path; any extension UI is a separate target decision.

Use standard SwiftUI controls so the current platform can apply the appropriate system treatment. Provide a solid fallback for reduced transparency, high contrast, large text, and platforms where material does not preserve readability. A glass background is decoration around a control hierarchy; it is not a status signal by itself.

## 5. Voice cards and information density

A native voice row can contain:

1. localized voice name;
2. primary language and supported-language summary;
3. readiness/publication status;
4. version and storage size in a disclosure or detail screen;
5. one primary action;
6. a secondary menu for update, remove, or diagnostics.

Use semantic text and system symbols instead of custom badges that require color interpretation. An available checkmark should be paired with text. A warning should say whether the issue is resource readiness, system refresh, extension loading, or render failure.

Do not show raw bundle paths, App Group keys, component codes, or model filenames in the main screen. Put technical proof in a diagnostics view that can be copied or shared deliberately.

## 6. Preview design versus system proof

The host app’s Preview action is useful for fast feedback, but it needs an explicit boundary:

| Preview surface | What it can show | What it cannot prove |
| --- | --- | --- |
| Host app `AVSpeechSynthesizer` preview | The host can request a selected voice and show app-owned progress | VoiceOver/Speak Screen discovery, extension reload, system settings, or all system clients |
| Marker preview | Word/sentence timing in the host | Correct byte offsets under every host render format |
| Resource readiness | Local package exists and passed integrity checks | Audibility on a physical output route |
| System settings handoff | Where the user manages Spoken Content voices | That an active request will render correctly |
| Glass status card | Current app-owned state | Audio quality, system discovery, or accessibility correctness |

Use “Preview in this app” and “Test with system speech” as separate actions. The latter should provide instructions and a test checklist rather than pretending the app can control VoiceOver’s full environment.

## 7. Accessibility is part of the provider design

The voice provider may be used by people who never open the containing app. The host UI still needs to be accessible, but the provider’s actual accessibility quality must be tested through VoiceOver and Speak Screen.

For the SwiftUI host:

- give every voice row a meaningful label and value;
- expose publication, resource, and refresh states as text;
- attach actions for Preview, Stop, Publish, Update, and Remove;
- support Dynamic Type without truncating language or availability;
- make progress understandable without a custom animation;
- preserve keyboard, pointer, Switch Control, Voice Control, and external input paths;
- keep focus stable when a voice row changes from installing to ready;
- avoid announcing every marker or render callback as a separate accessibility event;
- expose a fallback voice and recovery action when a resource disappears.

For the provider:

- test system voice selection in Spoken Content settings;
- test VoiceOver reading short, long, localized, and punctuation-heavy text;
- test Speak Screen with scrolling content;
- test cancellation, interruption, route changes, and a voice being removed;
- verify that a system client can recover without the host app’s view being present.

Do not use the host app’s custom visual highlight as the only accessibility evidence. A provider can produce perfect host markers while failing to work for a system client.

## 8. Privacy and trust language

Explain what voice packages contain, where they are stored, whether the app can remove them, and whether any source text is retained by the host. The provider should not imply that the system sends speech text to the host app. Keep the inventory minimal and avoid exposing private App Group data in diagnostics or accessibility labels.

If the app supports an optional AI pronunciation or SSML proposal, show a separate review step:

~~~text
original phrase
  -> proposed pronunciation / SSML
  -> changes highlighted
  -> user accepts or rejects
  -> provider preview
~~~

Do not say “AI voice verified.” The model can propose text or markup; deterministic validation and the provider’s render evidence are separate. If local model availability changes, keep the voice provider usable with original text and deterministic markup.

## 9. Failure states that belong in the design

Plan for these visible states:

| Failure | User-facing response |
| --- | --- |
| Extension not discovered | Explain that the signed provider is not visible to the system and offer retry/support details |
| Voice resource missing | Offer download/install/update only through the approved local flow; provide fallback |
| Unsupported language/SSML | Identify the unsupported input and preserve original text |
| Render error | Stop the preview, preserve request diagnostics, and offer another voice |
| Marker mismatch | Disable word highlight for that request rather than highlighting the wrong text |
| Cancellation | Return to idle without claiming successful completion |
| System voice refresh pending | Show pending state and system settings path |
| Voice retired while selected | Select a deterministic fallback and explain why |
| Accessibility client interruption | Preserve recoverable state without stealing focus |

Error copy should not expose internal component identifiers or suggest that restarting the app guarantees a system refresh. Keep diagnostic details available behind a deliberate “Copy diagnostics” action.

## 10. Review checklist

- [ ] The host app distinguishes app preview from system speech availability.
- [ ] Voice rows use stable identifiers, language metadata, version, size, and readiness text.
- [ ] Publication and system refresh are represented as pending states.
- [ ] Liquid Glass groups useful controls and does not obscure catalog text.
- [ ] Reduced transparency, high contrast, large text, and reduced motion remain usable.
- [ ] VoiceOver and Speak Screen are tested outside the host app’s custom UI.
- [ ] Preview, system handoff, fallback, update, removal, and cancellation are separate actions.
- [ ] AI pronunciation/SSML proposals are typed, bounded, validated, and user-approved.
- [ ] Privacy copy explains resource storage and source-text handling.
- [ ] The design never presents a voice inventory or marker stream as audible-output proof.

## Sources

- [Creating a custom speech synthesizer](https://developer.apple.com/documentation/avfaudio/creating-a-custom-speech-synthesizer)
- [AVSpeechSynthesisProviderAudioUnit](https://developer.apple.com/documentation/avfaudio/avspeechsynthesisprovideraudiounit)
- [AVSpeechSynthesisProviderVoice](https://developer.apple.com/documentation/avfaudio/avspeechsynthesisprovidervoice)
- [AVSpeechSynthesisProviderVoice.updateSpeechVoices()](https://developer.apple.com/documentation/avfaudio/avspeechsynthesisprovidervoice/updatespeechvoices%28%29)
- [AVSpeechSynthesisMarker](https://developer.apple.com/documentation/avfaudio/avspeechsynthesismarker)
- [VoiceOver](https://developer.apple.com/documentation/accessibility/voiceover/)
- [VoiceOver Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/voiceover)
- [Accessibility Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessible controls](https://developer.apple.com/documentation/swiftui/accessible-controls)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
