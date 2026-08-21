# Native media and audio surfaces

## Design goal

A camera, recorder, player, or media-review screen should feel native because its hierarchy is clear, its controls are familiar, and its system boundaries are honest. Liquid Glass can group functional controls, but it should not obscure the media, invent a fake camera chrome, or turn an uncertain AI result into a system-looking fact.

Use this composition contract:

    content first -> functional controls second -> system state third -> optional intelligence last

The media itself is usually the primary surface. Controls should recede until needed, remain discoverable, and preserve safe-area and accessibility behavior.

## Screen roles

| Screen role | Primary content | Functional controls | State that must remain visible |
| --- | --- | --- | --- |
| Capture | Live preview or audio recording context | Capture, stop, pause, switch input, permission, cancel | Ready, recording, interrupted, denied, unsupported, or failed. |
| Review | Frozen photo, playable movie, waveform, transcript, or extracted content | Play, scrub, retake, trim, edit, accept, discard, export | Processing, provisional, final, edited, export-ready, or failed. |
| Browse/playback | Media content and supporting metadata | Play/pause, seek, captions, route, full-screen, PiP where configured | Loading, buffering, playing, paused, ended, unavailable, or interrupted. |
| AI inspection | Source media plus bounded observation | Retry, compare, correct, accept, reject, explain source | Model unavailable, low confidence, partial, final, stale, or user-edited. |
| Export/share | Finalized representation and destination choice | Save, share, copy, open in, cancel | Preparing, exporting, complete, cancelled, destination unavailable, or failed. |

Do not collapse all of these into one overloaded button. A capture control starts a capture. A review control approves a result. An export control hands off a finalized artifact. Each action should have a distinct label and consequence.

## Native capture shell

### Preview hierarchy

Give the preview the largest useful region. Keep important capture controls inside a stable safe-area region, and avoid placing controls over high-contrast details when the preview is the content. Use the system preview and capture components where they satisfy the outcome. A custom overlay should explain a product-specific action, not imitate a proprietary Apple screen.

The minimum capture surface should expose:

- the current mode, such as photo, video, or audio;
- a clear primary capture button with a text label available to assistive technologies;
- recording state and elapsed time;
- permission or hardware availability;
- a visible stop or cancel path;
- a non-audio confirmation of capture state;
- a route to review before save, publish, or AI action.

Use shape, text, and icon state in addition to color. A red tint may reinforce recording, but the label Recording and an accessible value are more reliable than color alone.

### Liquid Glass controls

Use Liquid Glass for a small, coherent group of actions that float above content:

- capture/stop;
- camera switch or input route;
- flash, timer, or recording options;
- review/export actions after the media is finalized.

Do not apply glass to the entire video or waveform, add nested glass to every icon, or place a translucent control over text that needs maximum contrast. Let the system choose material behavior where a native control already owns the surface. Keep a solid or higher-contrast fallback for Reduce Transparency and difficult preview backgrounds.

The glass action group should have one visual identity while its state changes. A record button can morph to stop only if the transition communicates one continuous action and does not make the hit target jump. If the app has multiple unrelated actions, use separate labeled controls rather than a single decorative cluster.

### Recording confirmation

Recording must be perceivable without sound:

- text state such as Recording or Paused;
- elapsed duration;
- a visual state change in the primary control;
- VoiceOver value and hint;
- optional haptic confirmation, never as the only signal;
- system privacy indicators are not a substitute for app-level status.

When the microphone or camera is interrupted, retain the draft if safe and state why capture stopped. Do not show a still preview with a live-looking recording affordance after the session has ended.

## Native audio surfaces

Waveforms are useful context but are not a complete status indicator. Pair them with elapsed time, current route, pause/stop controls, and a text transcription or caption route when speech matters.

For a recorder:

1. Show the microphone purpose before permission.
2. Show the current input route when it matters.
3. Make recording, paused, and stopped states distinguishable.
4. Let the user review and delete the recording.
5. Show audio level without implying that loudness equals intelligibility or success.
6. Keep the transcript provisional until the analyzer reports the result state.
7. Give the user a text alternative to important audio information.

For playback, prefer VideoPlayer or the system player when it meets the need. A custom player must preserve familiar play/pause, seek, captions, route, and dismissal behavior. Preserve the media’s aspect ratio. Do not autoplay audio without a clear user control and a way to stop it.

For voice or music, route changes need a visible explanation when the output changes. “Headphones disconnected” or “Microphone unavailable” is more useful than silently switching to a route that changes the user’s expectations.

## Reviewable AI media

An AI-assisted media screen should distinguish four things:

| Element | User-facing treatment |
| --- | --- |
| Source | Show which photo, frame, audio file, or time range produced the result. |
| Observation | Show extracted text, labels, transcript segments, or measured metadata as a framework result. |
| Proposal | Use language such as Draft, Suggested, or Needs review when a model transformed or organized the result. |
| Approved record | Give the user an explicit Accept, Save, or Apply action and preserve edits. |

For streaming speech, show partial text as provisional and make the transition to final text visible. Do not reorder a transcript silently while the user is editing it. For OCR or object detection, preserve the source crop and allow correction. For summaries or structured extraction, show missing fields and uncertainty instead of filling gaps with confident-looking glass cards.

AI controls should be action-oriented:

- Review suggestion;
- Compare with source;
- Correct text;
- Keep original;
- Accept selected fields;
- Retry with a narrower input.

Avoid a magic wand with no explanation, an unbounded “improve” action, or a generated result that shares or publishes without a confirmation boundary.

## Accessibility and alternate input

Apple’s accessibility guidance says important information should not be communicated through audio alone. Provide captions, transcripts, visual state labels, and accessible values. Pair haptics with visual or textual feedback.

Design the capture and review route for:

- Dynamic Type and long localized labels;
- VoiceOver reading order and rotor-friendly headings;
- Voice Control labels for capture, pause, stop, retake, accept, discard, and share;
- Switch Control and Full Keyboard Access;
- pointer hover/focus states on iPad and Mac Catalyst;
- Reduce Motion and Reduce Transparency;
- Differentiate Without Color;
- landscape, split view, Stage Manager, and compact widths;
- RTL layouts and localized time/duration formats.

Do not make an icon-only button the only way to start or stop capture. The visible label can be compact, but the semantic label must explain the action. The primary action needs at least the platform-appropriate minimum interaction size, and a destructive discard action should have confirmation when recovery is difficult.

## Layout and material rules

Keep the hierarchy stable as the state changes:

    media -> status -> primary action -> secondary actions -> review details

Use adaptive stacks and system typography. Avoid fixed preview heights that crop the primary content on every device, and avoid placing important controls in a hard-coded bottom coordinate. Let the safe area, container size, Dynamic Type, and input method shape the composition.

Glass should frame actions, not replace layout:

- use one material family per functional group;
- keep labels legible over changing media;
- do not put a full-screen glass veil above a live camera without a clear purpose;
- use a solid fallback when transparency reduces contrast;
- respect reduced effects and reduced motion;
- keep animation short, cancellable, and tied to the user’s action;
- preserve identity when a capture control becomes a review or export control only when the action is continuous.

When the preview itself is dark or bright, use a contrast-aware control region rather than stacking more translucent materials. The content should remain the visual anchor.

## State copy

Use concrete, calm state language:

| State | Example copy |
| --- | --- |
| Permission needed | Allow camera access to scan the document. |
| Waiting for hardware | Camera unavailable. Close another app using the camera and try again. |
| Ready | Ready to record. |
| Capturing | Recording · 00:18 |
| Interrupted | Recording paused by a phone call. |
| Processing | Preparing a reviewable transcript… |
| Provisional | Draft transcript · still updating |
| Final | Transcript ready to review |
| Exporting | Exporting a copy… |
| Complete | Saved to the selected destination |
| Failed | We could not finish the export. Your original recording is still here. |

The UI should not imply that a model or export is complete when the framework is still buffering, analyzing, or writing.

## Proof checklist for the design

- Preview, permission, and review states are visible without a physical media source.
- A signed device proves actual camera/microphone routing, orientation, focus, audio interruptions, and thermal behavior.
- Simulator and previews prove hierarchy, copy, Dynamic Type, accessibility labels, and layout branches; they do not prove camera quality or audio routes.
- Accessibility tasks cover start, pause, stop, review, edit, accept, discard, and share.
- Reduced motion/transparency and long text preserve the primary action.
- The original aspect ratio remains intact in playback and export review.
- Capture and AI states are distinguishable from system privacy indicators.
- Generated results are reviewable and cannot trigger consequential side effects by merely appearing.

## Sources

- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Playing video](https://developer.apple.com/design/human-interface-guidelines/playing-video)
- [Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
- [Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
- [Layout](https://developer.apple.com/design/human-interface-guidelines/layout)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [AVFoundation](https://developer.apple.com/documentation/avfoundation)
- [Setting up a capture session](https://developer.apple.com/documentation/avfoundation/setting-up-a-capture-session)
- [AVCaptureSession](https://developer.apple.com/documentation/avfoundation/avcapturesession)
- [AVCapturePhotoOutput](https://developer.apple.com/documentation/avfoundation/avcapturephotooutput)
- [AVCaptureVideoPreviewLayer](https://developer.apple.com/documentation/avfoundation/avcapturevideopreviewlayer)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [AVKit](https://developer.apple.com/documentation/avkit)
- [VideoPlayer](https://developer.apple.com/documentation/avkit/videoplayer)
- [AVPlayerViewController](https://developer.apple.com/documentation/avkit/avplayerviewcontroller)
- [Playing video content in a standard user interface](https://developer.apple.com/documentation/avkit/playing-video-content-in-a-standard-user-interface)
- [SpeechAnalyzer](https://developer.apple.com/documentation/speech/speechanalyzer)
- [SpeechTranscriber](https://developer.apple.com/documentation/speech/speechtranscriber)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [VoiceOver](https://developer.apple.com/documentation/accessibility/voiceover)
