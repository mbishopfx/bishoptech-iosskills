# 3D model preview and native spatial design

A polished Apple-native 3D feature usually has a calm 2D shell around a
focused 3D object. The object can be expressive; the surrounding interface
should remain legible, semantic, and predictable.

Use this composition:

~~~text
identity and navigation
  -> model stage
  -> load / error / provenance status
  -> semantic actions
  -> detail, annotation, or review sheet
  -> save, export, or share
~~~

The model surface is not the whole product. It is one stateful surface with a
renderer lifecycle, resource failures, accessibility needs, and a separate
domain record.

## Start with the user job

| User job | Smallest native surface | Expansion only when needed |
| --- | --- | --- |
| See an object | SwiftUI `Model3D` or a target-appropriate RealityKit view | Model metadata, reset/rotate, export |
| Inspect parts | Interactive RealityKit entity hierarchy or an existing SceneKit adapter | Selection, path labels, measurement review, annotations |
| Place an object in a room | RealityKit plus ARKit | Camera permission, tracking states, anchors, occlusion, privacy, fallback |
| Edit or prepare an asset | Model I/O processing tool or import screen | Mesh report, texture repair, normalization, export and reopen |
| Explore a game/scene | RealityKit or SpriteKit with SwiftUI shell | Game loop, input, save state, performance and accessibility |

Do not add AR, immersive spaces, or a custom Metal renderer because a static
model needs to look more premium. Choose the least powerful route that completes
the job and leaves room for the correct proof.

## The native screen hierarchy

Keep information hierarchy outside the renderer where possible:

1. navigation title identifies the asset and current mode;
2. the model stage receives the largest visual area;
3. a compact status row says loading, ready, partially resolved, unavailable,
   or failed;
4. native controls offer reset, inspect, annotate, share, and other real
   actions;
5. detail and AI review appear in a sheet, inspector, or secondary pane;
6. a save/export action commits a deterministic result.

Avoid placing every label, button, and status chip inside the 3D scene. A
renderer can be paused, unavailable, clipped, hidden by system UI, or replaced
by a fallback image. The person should still be able to understand the asset
and complete the primary task.

## Model loading is visible UI state

Treat the async model lifecycle as a state machine:

~~~text
idle
  -> loading asset
  -> model ready
  -> model partially resolved
  -> failed with retry/import action
  -> cancelled or unavailable
~~~

Use a stable placeholder that preserves the expected stage size. Do not let a
spinner cause the toolbar to jump or let a missing texture silently turn a
reviewed asset into a different object. If the route has a thumbnail, show its
source and date only when those values are trustworthy.

Customer-facing copy should describe the situation:

| Internal observation | Native copy |
| --- | --- |
| `Model3D` phase is loading | Loading model… |
| File exists but external texture is absent | Model loaded with missing texture |
| File is too large or unsupported | This model can’t be opened here |
| Camera/AR permission is denied | Camera access is off; view the model instead |
| Imported asset has no stable name | Untitled model |
| AI proposal has not been reviewed | Suggested description — Review |

Avoid “verified,” “accurate,” or “scan complete” unless the product has a
defined deterministic check and the UI names what was actually checked.

## Liquid Glass around 3D content

Liquid Glass is most useful for functional controls that sit above or beside a
model. It should provide grouping, hierarchy, and continuity with the system
shell, not become a decorative layer over the asset.

Use glass for:

- a compact control group with reset, rotate, and inspect;
- a toolbar or bottom action group that follows the model stage;
- a review/action group with Accept, Edit, Retry, and Export;
- a temporary status surface when it does not cover important content.

Keep the model, labels, measurement values, and accessibility summary on
ordinary content layers. Do not use a glass blur as the only contrast treatment
for text or as a substitute for a visible loading/error state. Avoid stacking
many translucent groups over a detailed asset; it reduces legibility and can
increase rendering cost.

If a control changes the model, animate the identity of that control and the
model state together. A Reset button should restore the deterministic camera/
transform state, not merely fade the view. A proposed material change should
be shown as a preview until accepted; do not silently replace the source asset.

## Native depth and platform adaptation

An iPhone or iPad model preview is still a 2D interface containing 3D content.
It needs 2D layout, Dynamic Type, familiar navigation, touch targets, and
accessibility. visionOS has additional depth, window, volume, and immersion
rules; do not copy those rules into an iOS screen without checking the selected
target.

When a shared feature spans iOS and visionOS, keep the domain and asset
manifest shared while adapting presentation:

| Shared | Platform-specific |
| --- | --- |
| Asset ID, source revision, object names, annotations, review state | `Model3D`/AR view/RealityView or another renderer |
| Resource manifest and fallback thumbnail | Window, volume, immersive-space, or 2D screen composition |
| User intent: inspect, reset, annotate, export | Touch, pointer, hand, gaze, controller, or keyboard input |
| AI proposal schema and provenance | Presentation of confidence, spatial placement, and comfort guidance |

Depth should clarify the object and interaction, not make text float or force
the person to refocus constantly. Keep important values in a stable panel and
provide a non-spatial reading order.

## Interaction contract

Define gestures and controls as explicit commands:

| Interaction | State transition | Fallback |
| --- | --- | --- |
| Pinch/drag to rotate | Camera or presentation transform changes | Reset button and accessible orientation summary |
| Pinch to zoom | View scale changes within a bounded range | Zoom controls or a static detail view |
| Tap a part | Selection path changes | Part list with names and VoiceOver actions |
| Reset | Deterministic transform returns | Always available in the native control group |
| Inspect | Detail/annotation sheet opens | Text summary and object path |
| Apply AI suggestion | Proposal becomes pending review | Manual edit or dismiss |
| Export/share | Snapshot or source file handoff begins | Explain unsupported destination or cancellation |

Gestures should not be the only way to reach an important action. Use semantic
buttons, menus, keyboard shortcuts where appropriate, pointer support, and
accessibility actions. Keep a cancelled gesture from partially committing a
domain mutation.

## AI review for assets

Use AI as a bounded assistant around the asset manifest:

~~~text
source asset + user-approved metadata
  -> local model or deterministic classifier
  -> typed proposal with object paths and source revision
  -> review sheet with before/after and confidence context
  -> accept, edit, or dismiss
  -> deterministic save/export
~~~

Useful review surfaces include suggested object labels, an accessibility
description draft, a missing-texture explanation, or a category suggestion
from a closed set. Show what the proposal was based on. Preserve the source
asset and original metadata when a person accepts a generated field.

Do not make a generated label appear as authored truth, infer physical size
from pixels without calibration, or let a model silently modify geometry,
collision, lighting, or safety-critical placement. A local model’s availability
or confidence is not a product guarantee; expose a manual path.

## Accessibility and inclusion

Test the complete task, not just the view’s accessibility tree:

- VoiceOver can identify the asset, state, selected part, and available actions;
- Dynamic Type and large accessibility sizes keep status and action labels
  readable without covering the model;
- Reduce Motion and reduced effects have a useful non-animated path;
- Increase Contrast and reduced transparency preserve control boundaries;
- color is not the only indication of selected, missing, or proposed state;
- Switch Control, Voice Control, keyboard, pointer, and touch can reach the
  same important commands;
- a non-3D summary exposes the information needed to complete the task;
- localization, long labels, right-to-left layouts, and landscape/iPad sizes
  do not collapse the model stage or hide actions.

For spatial targets, include comfort and depth checks. For iOS, remember that
the model stage is embedded in a conventional 2D interaction model; do not
require spatial perception to understand a critical value.

## Performance and energy as design inputs

Set an asset budget before choosing visual polish:

- maximum import size and texture dimensions;
- number of meshes, submeshes, materials, and animation tracks;
- acceptable initial-load and first-interaction latency;
- memory headroom during model loading and thumbnail generation;
- frame-time and thermal budget on representative devices;
- background/cancellation behavior for imports and exports;
- reduced-effects path for constrained devices or accessibility settings.

Use a low-detail or thumbnail fallback when the primary task is recognition.
Do not keep multiple full-resolution assets, textures, and AI thumbnails alive
when a bounded cache or downsampled projection will do. Measure the actual
target rather than using a preview or newest device as a universal baseline.

## Design review checklist

- The chosen route matches a static preview, interactive scene, AR, game, or
  asset-processing outcome.
- SceneKit is isolated to maintenance/migration work; new work starts with
  RealityKit or an explicitly justified renderer.
- Loading, missing resources, cancellation, and unsupported-format states are
  visible and recoverable.
- Liquid Glass groups real actions and does not carry the only status or
  contrast boundary.
- Model labels, important values, and review state remain available outside the
  renderer.
- Gestures have semantic control alternatives and deterministic reset.
- AI suggestions show source/revision and remain reviewable before commit.
- Dynamic Type, VoiceOver, reduced effects, contrast, keyboard/pointer,
  localization, RTL, and alternate layouts are included in the design pass.
- Asset size, memory, frame time, thermal, and export budgets are measured on
  representative devices.

## Related routes

- [Model I/O, SceneKit, and RealityKit 3D assets](../42-framework-deep-dives/59-modelio-scenekit-realitykit-3d-assets.md)
- [3D asset runtime capability route](../50-capability-recipes/82-3d-asset-runtime-capability-route.md)
- [3D asset runtime proof matrix](../60-verification/76-3d-asset-runtime-proof-matrix.md)
- [3D asset runtime recipes](../70-code-recipes/94-3d-asset-runtime-recipes.md)
- [RealityKit and ARKit spatial route](../50-capability-recipes/40-realitykit-arkit-spatial-route.md)
- [RealityKit, ARKit, RoomPlan, and Object Capture](../42-framework-deep-dives/19-realitykit-arkit-roomplan-and-object-capture.md)
- [Adaptive native glass composition](../50-capability-recipes/17-adaptive-native-glass-composition.md)

## Sources

- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Spatial layout](https://developer.apple.com/design/human-interface-guidelines/spatial-layout/)
- [RealityKit](https://developer.apple.com/documentation/realitykit)
- [Model3D](https://developer.apple.com/documentation/realitykit/model3d)
- [Entity](https://developer.apple.com/documentation/realitykit/entity)
- [ModelEntity](https://developer.apple.com/documentation/realitykit/modelentity)
- [Model I/O](https://developer.apple.com/documentation/modelio)
- [SceneKit](https://developer.apple.com/documentation/scenekit)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
