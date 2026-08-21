# SwiftUI SpeechAnalyzer live transcription review design

The native design target for a live transcript is calm, legible, and state-honest. The person should always know whether the app is listening, preparing a model, showing text that may change, showing finalized source text, or showing a generated suggestion. Liquid Glass can give the controls hierarchy, but the transcript and its source state remain the visual center.

This page pairs with the [SpeechAnalyzer framework review](../42-framework-deep-dives/124-swiftui-speechanalyzer-live-transcription-review.md). It is a design contract, not a claim that a particular SwiftUI modifier or beta Speech API compiles in every SDK.

## 1. The screen hierarchy

Use one content hierarchy:

~~~text
Navigation title: source / session name
  ├─ source and readiness status
  ├─ transcript content (primary)
  │    ├─ finalized segments
  │    └─ volatile segment with subtle “live” treatment
  ├─ optional source-time scrubber / gap indicator
  └─ functional control group
       ├─ Start / Stop / Pause
       ├─ microphone and route status
       ├─ Import / language / settings
       └─ Review / Suggest actions
~~~

Do not make the transcript a card inside a stack of equal cards. A person is reading source content; the controls should recede until needed. On compact widths, keep the primary action reachable and move diagnostics into a sheet or inspector. On iPad and Mac Catalyst, use a split view or inspector for source metadata and model readiness without shrinking the reading column unnecessarily.

## 2. Make transcription state visible without theatrical noise

Every state needs a visual, textual, and accessible representation:

| State | Visual treatment | Action language |
| --- | --- | --- |
| Ready | Quiet empty state with a microphone or import entry point | “Start recording” / “Import audio” |
| Permission needed | Explanation near the action, not a mysterious disabled button | “Allow microphone access to record” |
| Preparing model | Progress/status row with cancel | “Preparing speech model” |
| Capturing | Small live indicator, elapsed time, clear stop action | “Listening” / “Stop” |
| Volatile text | Slightly subdued or tinted trailing region, never a fake confidence badge | “Updating” |
| Finalized text | Normal body style and stable selection identity | “Final” only when useful |
| Interrupted | Persistent explanation and resume/restart choice | “Recording paused by an interruption” |
| Route unavailable | Route icon plus a concrete recovery action | “Microphone unavailable” |
| Finalizing | Progress/status separate from capture | “Finishing transcript” |
| AI proposal | Separate panel with source revision and review action | “Suggested summary — review” |
| Failed | Preserve source and offer retry/import | “Transcript incomplete; try again” |

Use color as a secondary cue. The same state must remain understandable in grayscale, high contrast, VoiceOver, and when transparency is reduced.

## 3. The live transcript should behave like an editor, not a ticker

The result stream can replace volatile text. A ticker-like append-only UI creates duplicated words, jumping scroll, and false confidence. Use stable source-range segments:

- finalized segments retain identity and selection position;
- volatile segments can be replaced in place;
- an empty volatile result can remove previously displayed tentative text;
- a source gap is shown explicitly rather than joined invisibly;
- the current volatile range is not labeled “final” because it looks visually complete;
- user edits create a local revision and stop the reducer from silently overwriting those edits;
- an AI proposal points at a transcript revision and cannot write into the source without a review action.

For long recordings, provide a “follow live” mode. It should turn off when the person scrolls away from the bottom, selects text, or starts editing. Restore it only with a clearly labeled action such as “Jump to live”.

## 4. Functional Liquid Glass groups

Apple’s Liquid Glass guidance emphasizes using the material for functional controls and hierarchy, respecting safe areas and system behavior, and avoiding a surface that competes with content. Apply it to:

1. the primary capture control group;
2. a compact route/permission status group when it floats over content;
3. a review action group containing “Edit,” “Suggest,” “Export,” or “Save”;
4. a transient progress/status group that needs separation from the transcript.

Do not wrap every transcript paragraph in glass. Do not use a glass surface to hide uncertain source state. Keep text and icons at a contrast that remains readable over changing backgrounds, and supply a plain surface fallback when a device, platform, accessibility setting, or design context makes translucency inappropriate.

Good visual layering:

~~~text
background / source artwork (optional)
  -> stable reading surface
     -> transcript text and source markers
        -> functional Liquid Glass controls at the edge or safe area
           -> system sheet for permission, model assets, or review
~~~

The microphone control should not morph into an AI control merely because the transcript became final. Preserve the user’s mental model: capture controls capture; review controls review; generated suggestions are separate.

## 5. Source identity, timing, and confidence

If the transcriber is configured with audio-time-range or confidence attributes, expose them progressively:

- a tap on a segment can reveal source time and playback/seek behavior;
- a confidence cue can be opt-in and should be described as model confidence, not correctness;
- alternatives belong in a review affordance, not in the primary reading stream;
- a source time gap should be visible in a timeline or detail view;
- imported and live sources need different labels so the person knows whether audio is still arriving;
- a language/locale label should use the selected or resolved locale, not an inferred guess presented as fact.

Do not display decimal confidence values by default. A plain “review suggested wording” affordance is usually more understandable than a false-precision percentage. If a domain requires confidence display, provide the source range and a clear explanation of what the value means.

## 6. Permission and privacy-first entry

The first capture entry should explain:

- what the microphone is used for;
- whether the audio is retained, discarded, or saved;
- whether the app uses on-device SpeechAnalyzer transcriber modules or a separate server/legacy recognition route;
- whether a later AI proposal receives transcript text;
- where the transcript and generated proposal are stored;
- how to stop, delete, or export the session.

Ask for microphone permission when the person chooses recording, not on first launch. If permission is denied, leave the import-audio and review workflows usable. If the target also includes `SFSpeechRecognizer`, show the legacy network recognition disclosure only for that route and keep the usage descriptions accurate to the actual target configuration.

The privacy view should show source, retention, and processing in normal language. A small “On device” badge is not enough if model assets download from Apple, if the app syncs transcripts, or if a separate server call happens after review.

## 7. Accessibility and alternate input

Treat each functional control as a semantic element:

- “Start recording,” “Stop recording,” and “Pause” are distinct actions with current values;
- the live state is announced without repeatedly interrupting every result;
- finalized text and volatile text have distinguishable accessibility descriptions;
- source-time and confidence details are available as custom content or a detail action;
- route and permission status are accessible before the action that depends on them;
- VoiceOver focus remains stable when a volatile segment is replaced;
- Dynamic Type does not clip transcript text or hide the stop control;
- Reduce Motion disables decorative live pulses while preserving a textual live indicator;
- Reduce Transparency and increased contrast retain control hierarchy;
- keyboard, pointer, Switch Control, Voice Control, and Full Keyboard Access can reach capture, stop, review, and save actions;
- selected text and editing affordances do not depend only on a color or a waveform.

When using a waveform or level meter, label it as a visual aid and provide a nonvisual state such as “capturing” or “silence detected.” Never require a person to interpret moving glass, color, or animation to know whether capture is active.

## 8. Model and asset readiness surfaces

Model setup is a system-resource state, not an error to hide behind a spinner. Use a compact readiness surface with:

| Readiness | Copy | Next action |
| --- | --- | --- |
| Device unsupported | “Live transcription isn’t available on this device.” | Import audio or use a supported target |
| Locale unavailable | “This language isn’t ready for live transcription.” | Choose a supported locale |
| Asset download needed | “Speech model will download before recording.” | Download / cancel |
| Network unavailable | “The model isn’t installed yet.” | Retry later or import/use fallback |
| Installed | “Ready for live transcription.” | Start |
| Reservation limit | “Another language model is reserved.” | Release/select locale |

Do not show a fake 100% progress bar if Apple’s asset API only provides completion status. Let the system progress object drive a real progress view when available; otherwise use an honest indeterminate state plus a retry action.

## 9. Optional AI review surface

The AI surface should feel like a review assistant, not a second transcript. A good composition is:

~~~text
“Suggest from this final transcript”
  -> source revision: 12
  -> selected range: 00:14–02:09
  -> model availability / privacy note
  -> generated proposal with source references
  -> Edit | Reject | Save
~~~

Suggested title, outline, tags, or action items should be typed and bounded. The review card should disclose when a field is absent or uncertain rather than inventing it. If the person edits the transcript, show that the old proposal is stale and require refresh. If the model is unavailable, keep the source transcript and manual actions prominent.

Avoid medical, legal, employment, or safety claims derived from an unreviewed transcript. The interface should never imply that a local model guarantees accuracy, privacy beyond the declared data flow, or completion of a task merely because it produced structured output.

## 10. Loading, failure, and stale states

Design the negative space before the happy path:

- no microphone permission;
- no compatible locale;
- assets downloading or deferred;
- audio input silent or route disconnected;
- capture interrupted;
- analyzer task cancelled;
- volatile text revoked;
- finalization still pending;
- transcript has gaps;
- persisted source is from an older app/model revision;
- AI proposal references a stale transcript;
- export destination unavailable;
- app relaunched after an incomplete session.

Every failure preserves what can be preserved. A failed AI request must not delete the transcript. A failed finalization should mark the source incomplete. A lost route should not silently resume into a different microphone. A stale proposal should be visibly stale and easy to discard.

## 11. Cross-device and platform adaptation

On iPhone, prioritize one-handed capture and a readable transcript. On iPad, use a wider reading column and an inspector for timing/model/source details. On Mac Catalyst, expose keyboard shortcuts, pointer affordances, and a conventional document/export path. On a companion/watch surface, show a compact status or handoff rather than trying to render a full transcript without a clear product reason. Keep the processing contract separate from the surface so a device can import an audio file if live capture is not appropriate.

## 12. Design review checklist

- [ ] The primary content is readable source transcript, not a wall of equal glass cards.
- [ ] Capture, permission, model readiness, interruption, and route states are distinct.
- [ ] Volatile text is visually and semantically distinct from finalized text.
- [ ] Finalization and cancellation preserve a source revision.
- [ ] Liquid Glass is applied to functional controls and falls back safely.
- [ ] The stop action remains reachable during preparation and capture.
- [ ] VoiceOver, Dynamic Type, Reduce Motion, Reduce Transparency, and contrast behavior are tested.
- [ ] AI suggestions are separate from the source, bounded, cited to source ranges, and explicitly accepted.
- [ ] Offline/model-unavailable/import fallbacks are visible.
- [ ] Physical-device microphone and route proof is planned before calling the design shipped.

## Sources

- [SpeechAnalyzer](https://developer.apple.com/documentation/speech/speechanalyzer)
- [SpeechTranscriber](https://developer.apple.com/documentation/speech/speechtranscriber)
- [SpeechTranscriber.Result](https://developer.apple.com/documentation/speech/speechtranscriber/result)
- [SpeechModuleResult.resultsFinalizationTime](https://developer.apple.com/documentation/speech/speechmoduleresult/resultsfinalizationtime)
- [AssetInventory](https://developer.apple.com/documentation/speech/assetinventory)
- [CaptureInputSequenceProvider](https://developer.apple.com/documentation/speech/captureinputsequenceprovider)
- [Asking permission to use speech recognition](https://developer.apple.com/documentation/speech/asking-permission-to-use-speech-recognition)
- [AVAudioApplication](https://developer.apple.com/documentation/avfaudio/avaudioapplication)
- [Handling audio interruptions](https://developer.apple.com/documentation/avfaudio/handling-audio-interruptions)
- [Responding to audio route changes](https://developer.apple.com/documentation/avfaudio/responding-to-audio-route-changes)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessible descriptions](https://developer.apple.com/documentation/swiftui/accessible-descriptions)
- [Accessibility Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
