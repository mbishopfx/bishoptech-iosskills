# Camera Control and locked capture design

## Design goal

Fast camera entry is a design problem about time, trust, and state. The user may launch from a locked device with limited context, press a physical control, or arrive in the full app ready to review. The design should let the person capture immediately without implying that the content is already saved, shared, analyzed, or published.

Use this hierarchy:

    capture context -> live preview -> primary capture feedback -> temporary source -> authenticated review -> approved action

Do not turn the lock-screen capture surface into a miniature dashboard. The extension’s job is to capture quickly and hand off safely.

## Two surfaces, two jobs

| Surface | Optimize for | Avoid |
| --- | --- | --- |
| Locked-camera extension | Immediate camera view, physical capture, minimal status, safe temporary storage | Network login, private library browsing, long settings, model-heavy review, or hidden publishing. |
| Containing app | Review, edit, organize, run on-device analysis, persist, export, and share | Treating a temporary extension URL as the durable record or assuming handoff has completed. |
| Camera Control overlay | Short controls with clear units and direct feedback | Long labels, custom art that looks like a state icon, duplicate sliders, or controls unrelated to the active capture mode. |
| In-app capture view | Content-first preview and a stable primary action | Recreating the system overlay or placing important UI beneath its portrait/landscape areas. |

An extension can use SwiftUI, but its visual hierarchy should follow its process constraints. A glass card that looks elegant in the unlocked app may be the wrong choice over a locked camera preview if it delays capture or exposes private information.

## Locked-camera entry shell

The extension should expose:

- a large live preview;
- a primary capture action that also responds to the supported hardware event;
- a clear photo/video mode if the route supports both;
- recording/processing feedback;
- a visible discard or finish path;
- a small continuation affordance that explains it will open the app after authentication.

The extension should not expose:

- private account names, library content, or recent records;
- network-dependent AI or upload status;
- a full app navigation hierarchy;
- irreversible “post,” “send,” or “publish” actions;
- a glass layer that hides the viewfinder or system privacy state.

Use short state labels:

| State | Example |
| --- | --- |
| Ready | Ready to capture |
| Capturing photo | Capturing… |
| Recording | Recording · 00:12 |
| Saved temporarily | Captured. Continue in App |
| Waiting | Preparing camera… |
| Permission | Unlock to allow camera access |
| Error | Camera unavailable. Try again |
| Handoff | Opening App after unlock… |

The user should understand where the content is and what happens if they dismiss the extension. Do not promise durable retention before the containing app imports the temporary session directory.

## Camera Control overlay design

Camera Control is a system-owned overlay with limited space. Apple’s HIG recommends:

- short control names;
- SF Symbols for control representation;
- units or symbols in slider values;
- prominent values for common choices;
- enough viewfinder space for the overlay in portrait and landscape;
- minimal duplicate UI in the camera view;
- controls that match the active camera mode.

Practical control register:

| Control | Good title/value | Design note |
| --- | --- | --- |
| Zoom | Zoom, 1×, 2×, 5× | Use the system zoom slider when it matches the capture device. |
| Exposure | Exposure, 0 EV | Include EV context; do not show a naked number. |
| Focus | Focus, near/far or a bounded value | Only expose if manual focus is genuinely useful. |
| Filter | Filters, Natural / Warm / Mono | Use a picker with short localized titles. |
| Format | Format, Photo / Video | Disable or omit values that do not apply to the current mode. |
| Framing | Framing, 4:3 / 16:9 | Preserve the source/output contract; do not imply a crop is lossless. |

An SF Symbol communicates the control’s function, not its current value. Pair symbol, localized title, and value formatting. Longer titles can obscure the viewfinder at Dynamic Type sizes.

Do not add a control to the session unless supportsControls and canAddControl pass. The overlay is system-owned, so an app cannot treat the list of controls as an ordinary SwiftUI toolbar.

## Fullscreen and overlay choreography

When the system control interface becomes active or fullscreen:

1. Reduce competing app UI.
2. Keep the viewfinder readable.
3. Avoid animated glass transitions that fight the hardware interaction.
4. Preserve the current capture mode and value.
5. Restore the previous UI only after the control overlay becomes inactive.

Use the capture session controls delegate as a state signal. Do not infer overlay visibility from a timer or from a button tap. When the overlay is active, the user’s attention belongs to the control; keep any remaining app content quiet.

## Functional Liquid Glass

In the unlocked containing app, Liquid Glass can group:

- capture/stop;
- camera switch;
- retake;
- review/continue;
- export/share after finalization.

Avoid glass on the live preview itself and avoid duplicating a Camera Control slider inside the same visual region. The system overlay already owns that interaction. If a control is available from hardware, the app surface should show its result or a compact alternate path, not a second competing control.

Use bounded morphing:

    Capture -> Capturing -> Review -> Export

Only morph controls when the action identity remains clear. A record button turning into stop is one action. A capture button turning into “Publish” is a different consequence and should receive a new label, confirmation, and usually a separate review step.

Respect reduced transparency and reduced motion. A solid action bar, clear border, or opaque fallback is preferable to a glass layer that makes a camera control unreadable.

## Privacy in a locked context

The lock-screen extension is a constrained privacy surface:

- show only the live camera and capture status needed for the task;
- do not show private data in labels or status text;
- do not imply that the person is already authenticated in the containing app;
- make the temporary nature of the capture understandable;
- require unlock before review, upload, account access, or private system actions;
- use authentication failure as a recoverable state, not as a generic capture error.

Controls placed on the Lock Screen or Action button should use privacy-aware labels. If a control’s title or state can reveal private information, redact it or require authentication according to the system control guidance.

## Physical button and accessibility feedback

Hardware capture events can begin, end, or cancel. The UI should give the same outcome for hardware and touch:

- visual state changes;
- a VoiceOver-readable label/value;
- a predictable sound when the system contract calls for it;
- optional haptic confirmation;
- a visible cancel path;
- no action when the event is disabled.

Never use a haptic or camera sound as the only confirmation. Do not leave an enabled hardware event with no working primary or secondary action. If the app is unable to respond, disable the interaction so the system can restore default behavior.

## Accessibility and localization

The Camera Control overlay has its own system presentation, but app controls and extension content still require:

- Dynamic Type-safe labels and values;
- VoiceOver order: preview, mode, status, capture, discard, continue;
- Voice Control phrases such as “Take photo,” “Stop recording,” and “Continue”;
- Differentiation without color for recording and failure state;
- reduced motion when preview or glass state changes;
- reduced transparency fallback;
- portrait and landscape layouts;
- RTL placement and localized units;
- long-language tests for control titles and status values.

Use familiar system controls for the main app action. Do not make a decorative overlay tappable with onTapGesture when a Button can carry the semantic action.

## AI after unlock

The best AI handoff is after capture finalization and authentication:

    temporary photo/movie -> app import -> source validation -> Vision/Core ML/Speech -> reviewable proposal -> user acceptance

The extension may need to capture without network or shared-container access. Keep the captured source available to the app and let the full app perform transcription, OCR, organization, or Foundation Models transformation after the privacy boundary permits it.

Show:

- original source;
- provisional/final result;
- model or framework name when useful;
- source range or crop;
- review/edit action;
- keep original;
- explicit save/share/publish action.

Never let a Camera Control value or a model result become a durable or published record merely because the capture extension ended.

## Design proof checklist

- The locked extension opens directly into an active camera, not a splash or sign-in.
- The active camera view remains visually simple and supports the physical capture event.
- Camera Control overlay labels are short, localized, and unit-aware.
- App UI does not overlap the overlay’s portrait or landscape area.
- Duplicate zoom/exposure/filter controls are removed or de-emphasized while the overlay is active.
- Locked content is temporary until the app imports it.
- Unlock is required before private review, upload, or account actions.
- Liquid Glass groups unlocked app actions without covering the media.
- VoiceOver, Voice Control, Dynamic Type, reduced motion, and reduced transparency keep the capture and review path usable.
- Unsupported devices return to an ordinary in-app capture route.

## Sources

- [Camera Control](https://developer.apple.com/design/human-interface-guidelines/camera-control)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines)
- [LockedCameraCapture](https://developer.apple.com/documentation/LockedCameraCapture)
- [Creating a camera experience for the Lock Screen](https://developer.apple.com/documentation/LockedCameraCapture/Creating-a-camera-experience-for-the-Lock-Screen)
- [Enhancing your app experience with the Camera Control](https://developer.apple.com/documentation/avfoundation/enhancing-your-app-experience-with-the-camera-control)
- [AVCaptureControl](https://developer.apple.com/documentation/avfoundation/avcapturecontrol)
- [AVCaptureSlider](https://developer.apple.com/documentation/avfoundation/avcaptureslider)
- [AVCaptureIndexPicker](https://developer.apple.com/documentation/avfoundation/avcaptureindexpicker)
- [AVCaptureSession controls](https://developer.apple.com/documentation/avfoundation/avcapturesession/controls)
- [AVCaptureEventInteraction](https://developer.apple.com/documentation/avkit/avcaptureeventinteraction)
- [onCameraCaptureEvent](https://developer.apple.com/documentation/swiftui/view/oncameracaptureevent%28isenabled%3Adefaultsounddisabled%3Aaction%3A%29)
- [CameraCaptureIntent](https://developer.apple.com/documentation/appintents/cameracaptureintent)
- [Creating controls to perform actions across the system](https://developer.apple.com/documentation/widgetkit/creating-controls-to-perform-actions-across-the-system)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
