# Spatial scene, occlusion, and native AR surfaces

## Design objective

A strong AR surface makes the physical environment understandable, keeps the person oriented, and lets the virtual content feel responsive without pretending that sensors are perfect. The core experience is not a decorative 3D layer. It is a sequence of supported decisions:

~~~text
can this device do the task?
  -> may the app use the camera?
  -> is tracking good enough?
  -> where is the candidate surface/object?
  -> what will be placed or scanned?
  -> what did the app actually observe?
  -> what is the person confirming?
  -> where is the result saved or shared?
~~~

Keep those states visible. A floating object with no status, no fallback, and no explanation is not an Apple-native spatial experience.

## The screen composition

Use a layered composition with clear ownership:

| Layer | Content | Design rule |
| --- | --- | --- |
| Physical scene | Camera feed or spatial environment | Give it maximum useful area and avoid opaque chrome |
| Tracking guidance | Lightweight reticle, plane cue, movement instruction | Explain the next action in ordinary language |
| Virtual content | Models, scan highlights, occlusion, selected state | Keep scale, shadow, and motion coherent |
| Persistent controls | Cancel, reset, capture, confirm, help | Use stable screen-space controls in reachable areas |
| Detail surface | Inspector, measurements, source, AI proposal | Move complex content into a sheet or focused screen |
| Confirmation surface | Save, export, share, replace, write | State the consequence in the button label |

Liquid Glass can unify the app-owned control group or inspector, but it should not turn the entire camera feed into a translucent panel. Use a material to support hierarchy, not to decorate uncertain geometry.

## State model

Use explicit states rather than a single isLoading or isReady flag:

| State | What the person sees | Allowed action |
| --- | --- | --- |
| unsupported | A short explanation and a non-AR route | Continue manually |
| permission-needed | Why camera or related access is required | Allow or use fallback |
| permission-denied | The limited mode and Settings/manual route | Open Settings or continue |
| starting | A restrained progress state | Cancel |
| looking-for-surface | A reticle and one instruction | Move/aim |
| estimating | A candidate placement with approximate wording | Place or keep scanning |
| ready-to-place | A clear placement affordance | Tap/place |
| placed | Object and stable controls | Move, rotate, inspect, confirm |
| tracking-degraded | A calm reason such as low light or too much motion | Move slowly/reorient |
| occluded | The object remains understandable when partly hidden | Continue or move closer |
| scanning | Progress, current room/object, stop control | Pause/stop |
| review | Source, geometry/metadata, edits, and provenance | Confirm, edit, reject |
| processing | A cancellable reconstruction/export state | Cancel or background if supported |
| complete | What was saved and where | Edit/share/export |
| failed | The failed phase and a recoverable next step | Retry/manual |

Every state should have a VoiceOver-readable label, an actionable button, and a no-animation fallback. A pulsing reticle cannot be the only indication that tracking is degraded.

## Placement and plane refinement

Apple’s AR guidance supports immediate placement followed by subtle refinement as surface detection improves. Design the object so that small transform corrections do not feel like a failure:

- use a soft transition for refinement;
- preserve the person’s explicit move/rotate/scale choices when possible;
- do not snap across the room;
- show a small “adjusted to surface” explanation only when the change matters;
- retain the initial and final transform in debug evidence;
- avoid anchoring to a guessed plane if the product requires a measurement-grade result.

The placement indicator should be aligned with the candidate surface. Use an orientation cue and a shadow or contact signal, but do not imply physical contact when the result is only estimated.

## Occlusion and depth communication

Occlusion is helpful when it clarifies spatial order:

- a virtual chair should appear behind a real table when the scene data supports that relationship;
- a user’s hand or body should not disappear behind an object without a clear reason;
- a mesh-based occlusion route should degrade gracefully when scene reconstruction is unavailable;
- a fake dark mask should not be presented as measured geometry.

When the product needs room or body occlusion, name the capability and device requirement in the feature contract. Test with reflective surfaces, glass, thin objects, clutter, low light, and people crossing the camera.

If depth is unreliable, favor legible screen-space annotation or a simple outline rather than a brittle illusion. A clear label is better than an object that flickers between foreground and background.

## Direct and indirect controls

AR is physically demanding. Combine direct manipulation with stable controls:

- single-finger drag for moving a selected object when aiming is reasonable;
- two-finger rotation only when it does not conflict with scaling;
- pinch-to-scale only when scale is a meaningful product action;
- screen-space buttons for reset, delete, confirm, and help;
- keyboard/pointer routes on iPad and Mac Catalyst where the target supports them;
- Voice Control names for all persistent actions;
- haptics/audio as confirmation, never as the only output.

Do not use scaling to fake distance. If the product needs a closer inspection, move the camera or provide a focused detail view.

## Room scanning and object capture surfaces

RoomPlan and Object Capture have guided capture behavior. The app should add product context around the framework route rather than fight the capture UI:

### Room scanning

- explain what is captured and where it is stored;
- show which room or floor is being scanned;
- support finish-room and finish-structure actions;
- keep a partial result visible if the framework returns one;
- let the person review detected categories and approximate dimensions;
- let them delete or restart a room;
- do not claim that an unreviewed category is certain.

### Object capture

- explain how to move around the object;
- show capture feedback without overwhelming the scene;
- let the person pause or stop;
- separate “photos captured” from “3D model reconstructed”;
- identify whether reconstruction is local or transferred to another device;
- show a preview and asset-quality warning before adding the model to a library.

For both flows, a progress bar alone is insufficient. Tell the person what remains and why the app is asking for a specific movement.

## SwiftUI and Liquid Glass patterns

Keep the 2D shell ordinary and native:

- standard toolbar, sheet, form, and navigation patterns for settings and review;
- system typography and Dynamic Type;
- semantic buttons with explicit verbs;
- a compact GlassEffectContainer or related glass grouping only where multiple controls move together;
- no permanent glass overlay over detailed captured geometry;
- no custom glyphs that imitate system navigation controls when a standard control exists.

Use material boundaries to separate:

1. scene controls;
2. selected-object controls;
3. review/commit actions.

Do not mix destructive Delete/Discard with a visually identical Save/Confirm action. Spatial motion can make mistakes hard to recover from; an explicit confirmation sheet is often more native than a floating “are you sure?” label.

## Accessibility for 3D content

RealityKit entities need deliberate accessibility data. For every important entity or scan result, provide:

- a concise localized label;
- a value such as approximate size, selected state, or confidence when useful;
- a description for complex objects;
- supported system/custom actions;
- a predictable order or rotor strategy for collections;
- a two-dimensional equivalent for searching, editing, and confirming.

The 2D equivalent is not an optional “accessibility mode.” It is also useful for people who do not want to point a camera precisely, for devices without AR support, and for reviewing a large scene.

Test:

- VoiceOver while tracking, placing, reviewing, and saving;
- Voice Control names for camera/scene actions;
- Switch Control or external input where supported;
- large text in all screen-space controls;
- Increased Contrast and Reduce Transparency;
- Reduce Motion and reduced haptic/audio settings;
- color-blind and no-color-only status cues;
- localization expansion and right-to-left layout;
- portrait/landscape and iPad split view where supported.

## AI as a review layer

AI can help translate spatial results into human language:

| Input | Possible proposal | Required guardrail |
| --- | --- | --- |
| CapturedRoom fields | “This room contains…” summary | Source fields remain inspectable |
| Selected object metadata | Catalog/category draft | Editable and reversible |
| Scene measurements | Furniture fit suggestion | Deterministic geometric constraints win |
| Tracking state/error | Plain-language next step | Do not hide unsupported state |
| User’s selected entities | Layout alternatives | Preview before commit |

Do not use AI to silently determine where an object is, to rewrite a saved measurement, or to infer sensitive household details from a scan without explicit product need and consent. A prompt injection in imported scene text must not make the app export, share, or delete spatial data.

Record the proposal source and model context if the user accepts an AI-assisted result. The person should be able to reject the proposal and keep the original scan.

## Privacy and emotional safety

A room scan can reveal home layout, possessions, routines, and accessibility needs. A face or body-tracking route can reveal sensitive biometric information. Design for least retention:

- explain capture before the camera starts;
- keep raw frames and meshes local unless transfer is necessary;
- show exactly what will be exported or shared;
- exclude private scan content from notifications and lock-screen previews;
- provide a delete-all-captured-data action;
- scrub sensitive debug logs;
- do not ship sample scans or fixture content in a way that exposes real people or homes;
- use the App Store privacy declarations and target usage descriptions honestly.

## Spatial design review

Before calling a surface native-ready, ask:

- Can a person complete the core task without knowing the term ARKit?
- Is the next movement understandable in under a sentence?
- Is the object legible in light/dark and cluttered rooms?
- Does the design explain approximate versus confirmed?
- Can a person recover from tracking loss without restarting?
- Are reset/delete/confirm actions reachable and distinct?
- Is there a non-AR equivalent for important tasks?
- Can VoiceOver identify the selected object and its actions?
- Does reduced motion remove decorative movement while preserving state?
- Does the material system help grouping without obscuring the scene?
- Is AI visibly proposing rather than authorizing?

## Sources

- [Augmented reality](https://developer.apple.com/design/human-interface-guidelines/augmented-reality)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy/)
- [ARKit](https://developer.apple.com/documentation/arkit)
- [Understanding world tracking](https://developer.apple.com/documentation/arkit/understanding-world-tracking)
- [ARWorldTrackingConfiguration](https://developer.apple.com/documentation/arkit/arworldtrackingconfiguration)
- [Scene reconstruction](https://developer.apple.com/documentation/arkit/arworldtrackingconfiguration/scenereconstruction)
- [Verifying device support and user permission](https://developer.apple.com/documentation/arkit/verifying-device-support-and-user-permission)
- [RealityKit](https://developer.apple.com/documentation/realitykit)
- [RealityView](https://developer.apple.com/documentation/realitykit/realityview)
- [ARView](https://developer.apple.com/documentation/realitykit/arview)
- [AccessibilityComponent](https://developer.apple.com/documentation/realitykit/accessibilitycomponent)
- [Improving accessibility of RealityKit apps](https://developer.apple.com/documentation/realitykit/improving-the-accessibility-of-realitykit-apps)
- [RealityKit updates](https://developer.apple.com/documentation/updates/realitykit)
- [RoomPlan](https://developer.apple.com/documentation/roomplan)
- [Scanning the rooms of a single structure](https://developer.apple.com/documentation/roomplan/scanning-the-rooms-of-a-single-structure)
- [ObjectCaptureSession](https://developer.apple.com/documentation/realitykit/objectcapturesession)
- [ObjectCaptureView](https://developer.apple.com/documentation/realitykit/objectcaptureview)
- [PhotogrammetrySession](https://developer.apple.com/documentation/realitykit/photogrammetrysession)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
