# SwiftUI Vision and Core ML live-observation review design

Design a camera-and-analysis surface as a trustworthy instrument. It should show what the app is seeing, how current the result is, what the model actually produced, and what the person can do next. It should not make glass, animation, or confidence typography imply truth.

This companion page pairs with [SwiftUI Vision and Core ML live-observation review](../42-framework-deep-dives/95-swiftui-vision-core-ml-live-observation-review.md), [SwiftUI media capture and review design](116-swiftui-media-capture-and-review-design.md), and [Core ML reviewable inference design](87-core-ml-reviewable-inference-design.md).

## The screen hierarchy

Use four distinct layers:

~~~text
camera content
  -> sparse observation overlay
  -> functional controls
  -> review or detail surface
  -> explicit action confirmation
~~~

The preview is content. Observation boxes and points are derived data. Pause, retake, torch, camera selection, review, and settings are controls. A language-model explanation is a proposal or interpretation. Keep these layers visually and semantically distinct.

The first screen should make these facts discoverable:

1. Camera access is available, denied, or not yet requested.
2. The preview is running, paused, interrupted, or unavailable.
3. Analysis is loading, sampling, reported, stale, or failed.
4. The current observation belongs to which frame and request/model revision.
5. A label, text candidate, point, or box is uncertain and needs review.
6. Whether an action is merely suggested, ready for validation, or committed.

Do not hide all state in a tiny status dot. Use copy, accessibility values, and a readable secondary state.

## State language

| Runtime state | Suggested copy | Control policy |
| --- | --- | --- |
| Permission not determined | Camera access is needed for this feature. | Explain the purpose, then offer the system request. |
| Denied or restricted | Camera access is off for this app. | Offer Settings/recovery and a non-camera path if one exists. |
| Preparing | Preparing on-device analysis. | Keep the preview privacy-safe; do not imply results. |
| Live sampling | Analyzing selected frames. | Show pause and last analyzed time. |
| Reported | Observed in the latest admitted frame. | Show source time and review action. |
| Low confidence | Possible match; review before using. | Avoid automatic commit. |
| Stale | Last result from a previous frame. | Offer refresh or retake. |
| Interrupted | Camera temporarily unavailable. | Explain interruption and recovery. |
| Model unavailable | On-device analysis is unavailable. | Keep capture or manual workflow where useful. |
| Proposal ready | Suggested from this observation. | Show source, warnings, edit, reject, and apply gates. |
| Committed | Saved or applied by the app. | Show deterministic result, not a model score. |

A “connected,” “ready,” or “complete” treatment should refer to the correct authority. Analysis completion means a request returned; it does not mean a person, object, document, or action is correct.

## Observation overlays

A box, label, and confidence state are one semantic unit. Do not draw a label in a detached floating pill that can be mistaken for a system control. Use a stable observation identifier and keep the selected observation visually distinct without making every detection glow.

For object recognition:

- show a human-readable label only after mapping the technical identifier;
- preserve the original identifier in a details route;
- distinguish the observation confidence from label confidence;
- display “possible” or “review” language at the product threshold;
- show a source time or stale state when the overlay remains on screen.

For text:

- present the candidate string in a reviewable card;
- show the region or crop when verification matters;
- allow copy or edit only after the person can inspect the source;
- do not turn recognized text into a command without an explicit confirmation boundary.

For pose or points:

- provide a list or rotor-accessible representation of important points;
- do not rely on a colored skeleton alone;
- distinguish missing points from zero-valued points;
- avoid medical, safety, or identity conclusions without an appropriately validated product and evidence plan.

## Geometry is part of the design

The preview and overlay must use one documented coordinate policy:

~~~text
normalized Vision lower-left coordinates
  -> image pixels
  -> orientation and mirroring
  -> aspect-fit or aspect-fill transform
  -> visible SwiftUI container
~~~

When the device rotates, the user changes camera, or the layout changes width, recompute the transform. Avoid animating a box from an old coordinate space into a new one without marking the source revision. A correct-looking portrait screenshot does not prove landscape, Dynamic Type, iPad split view, or front-camera mirroring.

If the user taps a detection, bind the action to the observation ID and frame revision. If the source has changed, ask the person to review the current result rather than applying the old tap target.

## Functional Liquid Glass

Apple describes Liquid Glass as a dynamic material for controls and navigation that forms a distinct functional layer. Use it for related controls such as pause, capture, review, or camera settings. Keep most camera imagery and observation content in the content layer, using standard materials or opaque surfaces when they improve contrast.

A good glass group:

- contains a small number of related controls;
- has a clear container boundary;
- stays away from the primary observation region when possible;
- remains legible over light and dark camera content;
- has an opaque or standard-material fallback;
- respects increased contrast and reduced transparency;
- does not communicate model accuracy through blur or shine.

Use clear glass only over visually rich content when contrast and readability remain acceptable. Do not create a glass card for every label or point. The more glass groups compete with the camera content, the less clear the hierarchy becomes.

## Reviewable AI cards

A local language model may explain selected typed observations or draft a next step. The card should show:

| Card element | Purpose |
| --- | --- |
| Source | Frame time, observation ID, request/model revision, and selected region. |
| Proposal | What the model suggests in plain language. |
| Uncertainty | Missing source, stale result, low confidence, or unsupported field. |
| Deterministic fields | Values the validator will check. |
| Edit | Lets the person correct wording or parameters. |
| Reject | Removes the proposal without side effects. |
| Apply | Runs only after validation and explicit confirmation. |

Keep AI copy visually subordinate to source and action state. “Suggested” is not “detected,” and “detected” is not “confirmed.” A proposal cannot authorize a device command, purchase, message, medical conclusion, identity decision, or destructive change by itself.

## Accessibility and alternate input

Every observation needs a semantic representation:

- label or role;
- value and confidence meaning;
- frame freshness;
- action or review hint;
- grouping with related observations;
- a stable order that does not depend on visual overlap.

The complete task must work with VoiceOver, Voice Control, Switch Control, keyboard, pointer, and Dynamic Type. Provide explicit controls for pause, retake, review, and dismiss. Do not require a person to drag a bounding box accurately to reach its detail. Ensure spoken labels do not expose raw technical identifiers unless the detail route requests them.

Use color, contrast, position, shape, and text together. Reduced motion should preserve the semantic state change without a fast tracking animation. Increased contrast and reduced transparency should not remove the meaning of reported versus stale versus proposal.

## Privacy and trust cues

The camera is a sensitive surface. Keep the camera indicator and system privacy behavior visible; do not imitate or obscure system privacy signals. Explain whether analysis is on-device, whether frames are retained, and whether any selected content can be exported or sent elsewhere.

A helpful trust panel can state:

~~~text
Camera: allowed
Analysis: on device
Latest source: 10:42:08
Request: object recognition revision 4
Model: accessory-detector 1.2
Status: possible match; review required
~~~

The panel is evidence context, not a guarantee. Avoid claiming that on-device means private in every sense if the app stores, exports, or shares results.

## Width, orientation, and interruption

On a compact phone, keep the preview dominant and move details to a sheet. On a regular-width layout, a side inspector can show source and review data without covering the camera. On iPad or Mac Catalyst, preserve keyboard and pointer routes and test resizable windows.

When the app backgrounds, locks, loses camera permission, or receives an interruption:

- stop or pause analysis according to the product contract;
- mark the last result stale;
- preserve an explicit selected-frame review if appropriate;
- avoid showing a previous overlay as live;
- offer recovery without losing an already reviewed draft.

## Acceptance questions

Before approving the design, ask:

1. Can a person tell whether the preview is active and whether analysis is current?
2. Can they inspect the source frame and model/request revision?
3. Is low confidence visually and semantically distinct from failure?
4. Does the overlay remain correct after orientation, mirroring, crop, and width changes?
5. Does Liquid Glass contain functional controls rather than content truth?
6. Can VoiceOver and alternate input complete the same review and commit task?
7. Does Reduce Motion and increased contrast preserve every state?
8. Can an AI proposal be rejected or made stale before any action?
9. Does the screen remain useful when camera or model access is unavailable?

## Sources

- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines)
- [Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [AVCaptureVideoDataOutput](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutput)
- [Recognizing objects in live capture](https://developer.apple.com/documentation/vision/recognizing-objects-in-live-capture)
- [VNRecognizedObjectObservation](https://developer.apple.com/documentation/vision/vnrecognizedobjectobservation)
- [VNRecognizedTextObservation](https://developer.apple.com/documentation/vision/vnrecognizedtextobservation)
- [VNObservation](https://developer.apple.com/documentation/vision/vnobservation)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
