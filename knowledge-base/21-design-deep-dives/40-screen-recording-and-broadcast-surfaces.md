# Screen Recording and Broadcast Surfaces

A screen-recording feature asks a person to hand an app unusually broad visibility into their device or app session. The native design goal is therefore confidence: the person should know what is being captured, why it is captured, whether the microphone or camera is active, where the result will go, and how to stop.

## The surface hierarchy

Build the experience in five layers:

1. **Intent** — explain the outcome in ordinary language, such as “Record this demo” or “Capture the last 15 seconds.”
2. **Permission and source** — let the operating system present the capture choice and permission; do not simulate the system picker.
3. **Live state** — show a persistent, accessible recording state with source, elapsed time, audio/camera status, and stop.
4. **Review** — show the finished artifact, its duration and provenance, optional AI observations, and an edit or discard path.
5. **Commit or share** — save to Photos, export, share, or commit an app-owned record only after the person chooses.

Do not collapse these layers into one translucent toolbar. A material treatment can group controls, but it cannot replace a privacy explanation, a state label, or a review step.

## State-driven layout

| State | Primary content | Primary action | Secondary behavior |
| --- | --- | --- | --- |
| Idle | Intended outcome and what will be captured | Start capture | Explain source and permissions |
| Preparing | Permission/picker status and selected source | Cancel | Keep the app usable if the person backs out |
| Running | Preview or capture summary, elapsed time, microphone/camera state | Stop | Pause only if the selected API and product support it |
| Interrupted | Reason, such as another route, background transition, or audio interruption | Resume or finish | Never imply uninterrupted capture |
| Finalizing | Progress or indeterminate “finishing recording” state | Cancel only if the API supports safe cancellation | Prevent duplicate save/share taps |
| Reviewable | Artifact preview, duration, source, timestamps, and AI provenance | Save, share, or approve | Edit, discard, retry analysis |
| Failed | What was and was not produced | Retry or return | Preserve any finalized artifact and explain what was lost |

The label “recording” should not remain on screen after capture has stopped. Conversely, “saved” should not appear until the save result is observed.

## Liquid Glass placement

Use standard SwiftUI controls and system bars first. If a custom capture toolbar needs a grouped material:

- keep the group close to the actions it contains;
- use one functional glass group rather than a glass layer behind the entire video;
- keep start and stop visually distinct;
- preserve text and icon contrast over light, dark, and moving backgrounds;
- avoid putting a camera or microphone indicator inside a decorative blur that can be mistaken for an inactive state;
- use a stable identity for a toolbar that morphs from start to stop;
- apply interactive material only to controls that perform an action;
- provide a reduced-transparency or opaque fallback;
- test large text, VoiceOver focus order, pointer hover, keyboard navigation, and landscape/compact layouts.

The result should feel native because it follows hierarchy, semantics, spacing, and system behavior—not because it reproduces a private Apple screen.

## Full-display versus in-app capture

The person’s mental model changes with the source:

| Source | Explain | Design consequence |
| --- | --- | --- |
| App-owned content | “Record this app” | Show the app’s own content and avoid implying unrelated device content is included. |
| Full display | “Record what appears on the display” | Make the source boundary and privacy implications explicit; rely on the system picker and indicator. |
| Camera/microphone | “Record camera and/or microphone” | Show the live camera/mic state, route changes, and the separate permission path. |
| Broadcast service | “Send this live session to a selected service” | Explain destination and network dependency before sending; keep local review and stop behavior available where possible. |

Do not promise a full-display route on iOS 26 based only on a current ScreenCaptureKit page or an iOS 27 sample. Put the availability result in the product’s capability state and let the UI fall back to an app-scoped or import workflow.

## Reviewable AI shell

An AI-assisted recording screen should make the chain visible:

captured artifact -> selected time range -> local observation -> proposal -> human review -> app-owned action

Good review affordances include:

- “Generated from 00:14–00:29”;
- model or analyzer availability state;
- transcript confidence or uncertain spans;
- “show source frame” or “play source audio”;
- editable text before commit;
- an explicit discard and retry route;
- no upload claim unless a server response was observed;
- no domain update claim until the person approved and the deterministic write succeeded.

Use a status panel or sheet for analysis rather than animating a glass blob indefinitely. If the model is unavailable, the recording remains useful as a media artifact.

## Motion and live media

Motion should communicate recording state, not create distraction. Use a small, persistent change for start/stop and a clear static state for reduced motion. Do not rely on a pulsing red dot alone; pair it with a spoken and textual state. Avoid an animation that can be mistaken for live capture when the session is paused or finalizing.

For preview media:

- maintain an aspect-ratio-aware container;
- avoid cropping the source controls or evidence when a person is reviewing;
- use captions and transcript alternatives where applicable;
- keep controls reachable without covering the important content;
- show stale or missing preview state separately from capture failure;
- use system share and save controls rather than invented equivalents.

## Accessibility and alternate input

The minimum task matrix includes:

- start capture with VoiceOver;
- identify source and microphone state without relying on color;
- stop capture without a timing-sensitive gesture;
- recover from an interruption;
- review, edit, save, share, and discard with Dynamic Type;
- use Switch Control and Voice Control for every primary action;
- navigate the live state with a keyboard or pointer on iPad;
- use Reduce Motion and Reduce Transparency;
- verify that focus moves to the review result after finalization;
- verify that an error announces what artifact remains available.

If the recording includes speech or visual content, provide a review path that does not require sound, precise touch, or real-time animation.

## Native fallback design

Fallbacks should preserve the user’s goal:

| Missing capability | Preserve the goal with |
| --- | --- |
| Screen sharing unavailable | Camera capture, app-owned media export, imported recording, or an explanatory unavailable state |
| Microphone denied | Silent recording if the product remains useful, with a visible “microphone off” label |
| Photos permission denied | Save to an app-owned file and offer ShareLink or Files |
| On-device model unavailable | Manual editing, transcript import, or a deterministic metadata view |
| Background continuation unavailable | Keep capture in the foreground and explain that leaving the app ends or pauses the session |

The fallback is part of the design system, not an afterthought. It should share the same semantic states and review actions.

## Sources

- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [ReplayKit](https://developer.apple.com/documentation/replaykit)
- [ScreenCaptureKit](https://developer.apple.com/documentation/screencapturekit)
- [Capturing screen content on iOS](https://developer.apple.com/documentation/screencapturekit/capturing-screen-content-on-ios)
- [AVCam: Building a camera app](https://developer.apple.com/documentation/avfoundation/avcam-building-a-camera-app)
- [On-device intelligence](https://developer.apple.com/documentation/TechnologyOverviews/ai-machine-learning)
