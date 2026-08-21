# SwiftUI AVSpeechSynthesizer spoken-output review design

The native read-aloud experience should make text easier to consume without making the person guess whether speech is queued, paused, finished, interrupted, or routed somewhere unexpected. The source text remains primary. Voice, rate, queue, route, and optional AI controls are supporting decisions.

This page pairs with the [AVSpeechSynthesizer framework review](../42-framework-deep-dives/125-swiftui-avspeech-synthesis-spoken-output-review.md). It covers design ownership and state presentation, not a guarantee that a particular target or system voice exists.

## 1. The screen hierarchy

~~~text
navigation title / source name
  ├─ source text or selected proposal
  ├─ current read-aloud state
  │    ├─ speaking / paused / finished / interrupted
  │    └─ current paragraph or word highlight
  ├─ optional queue / voice inspector
  └─ functional action group
       ├─ Play / Pause / Stop
       ├─ Voice / language / speed
       ├─ Export audio (if supported)
       └─ Call output (only in an explicit communication feature)
~~~

On iPhone, keep Play/Pause and Stop reachable. On iPad/Mac Catalyst, place voice and queue details in an inspector or side column. Do not turn every paragraph into a control; the person is reading content, not navigating a dashboard.

## 2. State language that tells the truth

| State | Visual language | Accessible value |
| --- | --- | --- |
| Ready | Quiet Play control | “Ready to read” |
| Preparing | Progress/status row | “Preparing speech” |
| Queued | Queue count and source identity | “Queued, item 2 of 4” |
| Speaking | Current source highlight and short state label | “Speaking paragraph 2” |
| Paused | Stable highlight, clear Resume | “Paused” |
| Interrupted | Route/interruption explanation, no false progress | “Speech interrupted; resume available” |
| Finished | No animated “live” state | “Finished” |
| Cancelled | Source remains, queue cleared | “Stopped” |
| Route unavailable | Concrete recovery action | “Output route unavailable” |
| Proposal pending | Separate generated-content status | “Suggestion needs review before speaking” |

Do not use a spinning orb, waveform, or color alone to communicate speaking. The synthesizer delegate’s range events can support highlighting, but the accessible state should be text and action based.

## 3. Functional Liquid Glass controls

Apply Liquid Glass to a compact functional group when it improves safe-area hierarchy:

- Play/Pause/Stop;
- current voice and speed control;
- queue/review actions;
- a transient interruption or route status group.

Keep the source text on a stable, readable surface. Do not put a translucent material behind every word or allow a moving highlight to reduce contrast. Provide a plain/opaque fallback for Reduce Transparency, high contrast, large text, or platforms where glass does not improve readability.

The control group should adapt to size:

| Width | Composition |
| --- | --- |
| Compact phone | Primary Play/Pause, Stop, compact status; settings sheet |
| Larger phone | Add current voice/rate and queue summary |
| iPad | Reading column plus inspector for voice/queue/source details |
| Mac Catalyst | Toolbar/menu commands, keyboard shortcuts, pointer affordances |
| Watch/companion | Compact state and stop/resume handoff, not an unbounded text reader |

## 4. Word and paragraph highlighting

Use a stable source mapping when delegate events provide character ranges or markers:

- keep the source revision unchanged while highlighting;
- map UTF-16 `NSRange` safely into Swift string/attributed-text indices;
- preserve links, emojis, combining marks, and right-to-left text;
- move VoiceOver focus only on explicit user action, not every word event;
- avoid auto-scrolling when the user is inspecting or editing earlier text;
- show a paragraph-level fallback if a range cannot be mapped;
- clear the highlight on pause/finish/cancel according to the feature contract.

Do not fake word progress with a timer. A timer can drift from the actual synthesizer and audio route. If the route changes or speech is interrupted, preserve the source/queue state and explain the new status.

## 5. Voice, language, and rate controls

Voice selection needs a readable fallback path:

1. show the selected language/region;
2. show the installed voice name and quality when available;
3. handle a missing preferred voice without silently changing language;
4. let the person preview or confirm a voice when the product warrants it;
5. keep rate and pitch within supported ranges;
6. disclose that assistive-technology settings may take precedence;
7. apply settings before enqueuing new utterances and label whether current queue items are affected.

Do not label a voice “natural” or “private” without evidence for the specific device and route. The system’s voice inventory and settings can differ across devices, locales, and downloads.

## 6. Read-aloud and accessibility speech are different surfaces

An app’s `AVSpeechSynthesizer` route can overlap with VoiceOver, Speak Screen, or other assistive technology. Give the person an obvious pause/stop action and avoid repeated announcements that compete with the system. If the app uses `prefersAssistiveTechnologySettings`, test the interaction rather than assuming the property always overrides app settings.

Required checks:

- VoiceOver focus remains stable while text highlights;
- Dynamic Type does not hide stop or route actions;
- Reduce Motion removes decorative pulses;
- high contrast and grayscale retain state distinction;
- Switch Control, Voice Control, keyboard, pointer, and external input reach actions;
- long localized text and right-to-left text preserve mapping;
- generated content is identified as a proposal before it is spoken;
- telephony output, if present, is disclosed and separately controlled.

## 7. AI proposal design

If Foundation Models generates spoken text, design the review sequence explicitly:

~~~text
original source
  -> “Suggest” action
  -> generated proposal labeled as generated
  -> edit / reject / accept
  -> “Read accepted text” action
  -> utterance queue
~~~

Never read a model response automatically because it finished streaming. Show source revision, model availability, and the user’s acceptance state. If the model is unavailable, the original source remains readable and speakable. The UI should not imply that speech synthesis validates a claim.

## 8. Queue and route controls

A queue summary should show source identity and count, not raw implementation IDs. The person needs to know:

- what will be spoken next;
- how to pause or stop all pending items;
- whether a new source replaces or appends to the current queue;
- whether export is generating a file instead of speaking;
- whether speech is using the app-managed route or system-managed speech;
- whether an interruption or route change paused the queue.

If the app can send speech into an active call, put that capability behind a separate communication affordance, explain the far-end consequence, and never hide it inside a generic output-channel picker.

## 9. Failure and empty states

Design these before polishing the happy path:

- no source text;
- source contains only unsupported/filtered text;
- selected voice unavailable;
- utterance queue rejected or cancelled;
- app audio session failed to activate;
- headphones/Bluetooth route disconnected;
- speech interrupted by another audio event;
- buffer export failed while direct speech is unaffected;
- custom voice provider unavailable or cancelled;
- model proposal unavailable or stale;
- target does not support the requested communication route.

Preserve source content and make the next action clear. Do not keep a “Speaking” badge when the audio session has been lost. Do not describe a generated file as spoken output until a playback/reopen test succeeds.

## 10. Design checklist

- [ ] Source text remains primary and readable.
- [ ] Play/Pause/Stop state is textual and accessible.
- [ ] Delegate range/marker events map to source revisions safely.
- [ ] Voice/language/rate controls have device-aware fallback.
- [ ] Liquid Glass is limited to functional controls and has a plain fallback.
- [ ] Queue replacement, cancellation, and finish states are visible.
- [ ] App-managed versus system-managed audio-session behavior is labeled.
- [ ] Buffer generation/export is separate from audible playback proof.
- [ ] Telephony uplink is an explicit, consented communication route.
- [ ] AI-generated text is reviewed and accepted before being spoken.
- [ ] VoiceOver, Dynamic Type, Reduce Motion/Transparency, contrast, and alternate input are tested.

## Sources

- [Speech synthesis](https://developer.apple.com/documentation/avfaudio/speech-synthesis)
- [AVSpeechSynthesizer](https://developer.apple.com/documentation/avfaudio/avspeechsynthesizer)
- [AVSpeechSynthesizerDelegate](https://developer.apple.com/documentation/avfaudio/avspeechsynthesizerdelegate)
- [AVSpeechUtterance](https://developer.apple.com/documentation/avfaudio/avspeechutterance)
- [AVSpeechSynthesisVoice](https://developer.apple.com/documentation/avfaudio/avspeechsynthesisvoice)
- [AVSpeechUtterance.prefersAssistiveTechnologySettings](https://developer.apple.com/documentation/avfaudio/avspeechutterance/prefersassistivetechnologysettings)
- [AVSpeechSynthesizer.usesApplicationAudioSession](https://developer.apple.com/documentation/avfaudio/avspeechsynthesizer/usesapplicationaudiosession)
- [AVSpeechSynthesizer.mixToTelephonyUplink](https://developer.apple.com/documentation/avfaudio/avspeechsynthesizer/mixtotelephonyuplink)
- [AVSpeechSynthesizer.outputChannels](https://developer.apple.com/documentation/avfaudio/avspeechsynthesizer/outputchannels)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
