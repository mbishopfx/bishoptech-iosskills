# Screen-capture trust and review design

Screen capture is one of the places where an Apple-native interface has to earn trust continuously. The person needs to know what source is selected, whether audio or camera capture is active, what the app is doing with the media, how to stop, and what an on-device AI result means. Liquid Glass can give the experience a calm, spatially legible shell, but it cannot be used to soften or hide a privacy boundary.

This design page pairs with the [ScreenCaptureKit and ReplayKit stream lifecycle](../42-framework-deep-dives/64-screencapturekit-and-replaykit-stream-lifecycle.md), the [compatibility capability route](../50-capability-recipes/87-screen-capturekit-compatibility-capability-route.md), the [proof matrix](../60-verification/81-screen-capturekit-replaykit-proof-matrix.md), and the [route recipes](../70-code-recipes/99-screen-capturekit-replaykit-recipes.md).

## Design the trust state before the glass

Start with the user’s mental model:

```text
What is being captured?
What extra audio or camera input is active?
Where will the media go?
What is being analyzed locally?
What can I stop or undo?
```

The visual system should answer those questions before it adds translucency, morphing, or decorative motion. A good capture surface is quiet, explicit, and easy to interrupt.

## State-driven surface map

| State | Primary surface | Functional controls | Avoid implying |
| --- | --- | --- | --- |
| Unsupported or target mismatch | Native unavailable card | Target/fallback explanation, import or app-owned capture alternative | That the feature is merely waiting for permission. |
| Needs permission | Permission rationale plus system transition | Continue, cancel, privacy explanation | That the app can silently enable capture. |
| Picker presented | System-owned picker | No duplicate source selector behind it | That the app owns the source list. |
| Source selected, not running | Capture preparation card | Review source, microphone/camera choice, start | That a selected filter is already recording. |
| Running | Compact glass status bar and preview | Stop, pause if supported, source/audio state | That an animated preview means a file is safe. |
| Inactive or interrupted | Persistent status with reason | Resume if valid, stop/finalize, troubleshoot | That the last frame is current. |
| Finalizing | Progress/status surface | Cancel only if the API and artifact policy allow it | That stop completed because the button was tapped. |
| Reviewable | Artifact review shell | Play, scrub, delete, share, analyze, approve proposal | That AI output is already domain truth. |
| Analysis pending | Source-linked AI review card | Cancel, retry, inspect source interval | That a spinner means the model understood the media. |
| Proposal ready | Evidence-first approval card | Edit, reject, approve, open source | That confidence is certainty or authorization. |
| Saved/shared | Receipt state | Open destination, copy link if appropriate, delete | That every downstream system accepted the same artifact. |

Represent these as domain states rather than styling variants. The state model should survive a view recreation, scene phase change, and a process restart where durable artifacts exist.

## A restrained Liquid Glass composition

Use a single visual hierarchy:

1. **Capture status** — a compact capsule with a semantic title such as “Capturing selected app,” elapsed time, and a small audio indicator.
2. **Content stage** — the preview or review content should remain the visual focus; glass should not flatten the media underneath it.
3. **Action rail** — stop, pause/resume where truly supported, and review actions should use standard semantic controls with comfortable hit regions.
4. **Trust disclosure** — an expandable but readable explanation of source, microphone/camera, retention, and local analysis.
5. **Proposal surface** — AI output appears as a reviewable card tied to a timestamp or artifact, not as an unexplained floating assistant.

Avoid a stack of independently blurred cards. Group related controls, keep the strongest contrast around the stop action, and allow the system background and captured content to provide context without making text unreadable. If the app uses a glass container or morphing transition, the transition should preserve focus, labels, and the visible recording state.

## The system picker and the app shell have different owners

The system content-sharing picker is Apple’s privacy surface. The app’s UI should prepare the person for it and reflect the result afterward, but it should not simulate the picker with a custom list of displays/windows. When the picker returns a filter:

- show the selected source in plain language;
- show whether microphone or camera capture was selected;
- keep the stop action available as soon as the stream starts;
- offer a “change source” action that returns to the system picker;
- explain if the target only supports an app-scoped fallback;
- preserve a cancelled state instead of silently returning to “ready.”

For an iOS 26 target, a current ScreenCaptureKit sample requiring iOS 27 should produce an explicit availability or fallback state. The UI must not present an iOS 27-only route as a disabled button whose reason is hidden.

## AI review is a source-navigation problem

Make generated output inspectable:

| AI element | Native interaction |
| --- | --- |
| Transcript or caption | Tap to jump to the matching media time; show uncertainty and edits. |
| Detected text/object | Show a source frame or interval and a clear “not confirmed” label. |
| Summary | Show which recording interval and model version produced it. |
| Suggested action | Present a typed draft with edit/reject/approve; require confirmation for side effects. |
| No result | Explain whether the model was unavailable, cancelled, below confidence, or found no evidence. |

Use local processing language precisely. “Processed on this device” is a data-path statement, not a guarantee that every system service or future handoff is local. If the app later shares or uploads an artifact, make that a separate user-visible action.

## Motion and transitions

Capture UI benefits from low-amplitude transitions:

- picker presentation is a system transition, not an app-made imitation;
- running state can settle into a compact capsule without hiding the stop control;
- finalization can use a progress transition that preserves the artifact title and source;
- a proposal can appear with a short, nonessential fade or scale transition;
- Reduce Motion should remove parallax, large morphs, pulsing indicators, and motion-dependent meaning;
- an audio or haptic cue must never be the only indication that capture started or stopped.

Do not animate the recording indicator so subtly that VoiceOver users or people looking away cannot detect the state. Pair motion with text, shape, and accessibility announcements where appropriate.

## Accessibility and alternate input

Test the real task: select a source, start capture, understand the source/audio state, stop, review, find an AI proposal, reject it, and delete the artifact.

The surface should provide:

- a concise label and value for capture status;
- a distinct, consistently reachable stop control;
- VoiceOver order that follows preparation -> source -> status -> content -> actions;
- Dynamic Type layouts that do not clip the source or stop labels;
- high-contrast text and icon treatments over changing media;
- non-color states for microphone, camera, and failure conditions;
- Voice Control names that match visible labels;
- keyboard, pointer, Switch Control, and controller paths where the target supports them;
- a non-gesture source-change and review path;
- no reliance on a tiny animated red dot for recording status.

Custom previews and overlays need an accessible textual alternative. If the AI identifies a region in a captured frame, make the result available as text and source navigation rather than requiring a person to inspect the image visually.

## Privacy language and retention

The UI should disclose the whole pipeline in short, concrete terms:

```text
Selected app: Example
Microphone: Off
Camera: Off
Processing: On device for review
Saved: Only after you choose Save
Retention: Temporary captures are deleted after review
```

This is not a replacement for usage descriptions, system consent, entitlement configuration, or legal review. It is the product’s explanation of what the next action does. Treat private notifications, passwords, credentials, and unrelated windows as capture hazards. Offer redaction or exclusion before recording when the product can reliably provide it.

## Review checklist

- Is the selected source described without exposing unnecessary private metadata?
- Can the person stop capture from every running state?
- Is microphone/camera state visible and accessible?
- Can the UI distinguish unsupported, denied, cancelled, interrupted, finalizing, finalized, saved, and analyzed?
- Does the AI result link back to source time and artifact revision?
- Does the app show confidence/uncertainty and allow rejection?
- Does every side effect require an explicit typed action?
- Does the layout survive Dynamic Type, high contrast, Reduce Motion, VoiceOver, Voice Control, and keyboard input?
- Are glass layers functional and grouped rather than decorative noise?
- Is the iOS 26 versus iOS 27 availability caveat visible in the product plan and proof record?

## Sources

- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles)
- [Designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [ScreenCaptureKit](https://developer.apple.com/documentation/screencapturekit)
- [Capturing screen content on iOS](https://developer.apple.com/documentation/screencapturekit/capturing-screen-content-on-ios)
- [SCContentSharingPicker](https://developer.apple.com/documentation/screencapturekit/sccontentsharingpicker)
- [SCStream](https://developer.apple.com/documentation/screencapturekit/scstream)
- [SCFrameStatus](https://developer.apple.com/documentation/screencapturekit/scframestatus)
- [ReplayKit](https://developer.apple.com/documentation/replaykit)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Dynamic Type](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [AccessibilityNotification announcement](https://developer.apple.com/documentation/accessibility/accessibilitynotification/announcement)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
