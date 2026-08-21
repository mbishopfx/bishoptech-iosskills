# MetalKit native visual-surface design

A MetalKit surface can make an iOS app feel bespoke, but native polish comes
from the surrounding task hierarchy, not from putting every interaction into a
shader. Design the renderer as one focused visual region inside a SwiftUI
screen with readable state, semantic controls, and a fallback that preserves
the user’s goal.

The design loop is:

~~~text
purpose of the visual
  -> source/loading state
  -> render quality and interaction model
  -> native controls and inspector
  -> accessibility/reduced-effects alternative
  -> measured device result
~~~

## Choose the surface before the effect

| User need | First surface | Add MetalKit when |
| --- | --- | --- |
| Display a diagram or light custom drawing | SwiftUI `Canvas`/`Shape` | A measured GPU/rendering need remains after simpler routes |
| Apply image filters | Core Image or SwiftUI image content | A custom shader/pipeline or continuous frame path is required |
| Edit a 3D asset | RealityKit/Model3D or a document editor | The product owns a custom GPU renderer or mesh/shader workflow |
| Build a game | SpriteKit/RealityKit/GameKit | Direct frame graph, shader, or GPU compute control is required |
| Show a live visualization | SwiftUI/Charts/Canvas | Sampling, shader, or frame-rate needs require Metal |

Choosing a higher-power renderer adds responsibilities: device capability,
shader resources, memory, thermal behavior, display cadence, accessibility,
and test complexity. The screen should not imply that custom GPU rendering is
required when a system component already provides the correct behavior.

## Screen hierarchy for a native GPU feature

Use a stable shell:

1. Navigation title and context that identify the asset/session.
2. A readable status line: loading, ready, rendering, paused, degraded, or
   failed.
3. The MetalKit surface with an intentional aspect/size policy.
4. A small action group for pause, reset, import, quality, or review.
5. A sheet or inspector for detailed values, source provenance, and edits.
6. A manual/list representation for essential selection and editing.

The person should not have to interpret frame cadence, command buffers,
pipeline states, or GPU memory. Translate those into product states such as
“Preparing preview,” “Using lower-detail mode,” or “This device cannot use
the selected effect.”

## Functional Liquid Glass composition

Use Liquid Glass for actions that operate on the visual surface, not as a
blanket texture over the rendered content:

| Action/state | Suitable treatment | Required readable companion |
| --- | --- | --- |
| Import or choose asset | Native toolbar/button or compact glass group | Source type, scope, and cancellation |
| Pause/resume a live render | Prominent semantic control | Current cadence and whether the scene is current |
| Change quality/profile | Menu or inspector control | Selected profile, device fallback, and expected cost |
| Accept an AI proposal | Review card/button group | Before/after, source, revision, and undo |
| Reset or delete derived output | Destructive confirmation | What is removed and what remains |
| Renderer error | Ordinary alert/content state | Recovery path and manual alternative |

Do not let a glass icon alone communicate that a frame is saved, an asset is
valid, a GPU feature is available, or an AI proposal was accepted. Avoid
placing several independent glass clusters over a busy renderer; hierarchy and
legibility matter more than decorative material.

## State is the visual language

Model the feature rather than inferring it from whether an `MTKView` exists:

~~~text
idle
  -> checking-device
  -> loading-source
  -> preparing-resources
  -> ready
  -> rendering
  -> paused / backgrounded / reduced-quality
  -> degraded(reason) / failed(recovery)
  -> dismantling
~~~

For imported or AI-enhanced assets, keep separate revisions:

~~~text
source asset revision
  -> decoded/validated
  -> render configuration revision
  -> generated proposal
  -> user decision
  -> accepted render revision
~~~

The renderer may display a proposal, but “shown” is not “accepted,” and
“encoded” is not “presented.” Use explicit labels and transitions.

## Interaction model

GPU content can support gestures, pointer input, controller input, and touch,
but an essential action should not depend on precise pixels or timing:

- provide a list/inspector route for selecting small or overlapping objects;
- expose zoom/pan/rotate modes with clear current mode and reset;
- make one-finger/two-finger gestures optional when possible;
- keep selection identity in the domain model, not in a GPU resource pointer;
- support keyboard/pointer/controller equivalents for editing workflows;
- make destructive or consequential transforms reviewable and undoable;
- preserve the task when motion, transparency, or high-contrast settings change.

If the renderer shows data that a person must read, duplicate the important
information in semantic text or an accessible data view. A rendered label
inside a texture is not automatically an accessible label.

## Accessibility and reduced-effects design

Test the task, not only the view hierarchy:

| Setting/input | Design response |
| --- | --- |
| Dynamic Type | Keep status, controls, and inspector text native and resizable; do not bake essential copy into a texture |
| VoiceOver | Expose the visual’s purpose, selection, value, and actions through semantic elements or a parallel inspector |
| Voice Control/Switch Control | Make import, pause, profile, accept, reset, and navigation discoverable controls |
| Full Keyboard Access/pointer | Provide focusable controls and non-gesture equivalents |
| Reduce Motion | Stop camera drift/parallax and retain state meaning with static composition |
| Reduce Transparency/increased contrast | Reduce material dependence; preserve boundaries and status contrast |
| Color/contrast limitations | Do not use hue alone for selection, warnings, or render quality |
| Low-power/thermal state | Lower cadence or quality with an explicit explanation and restore path |

The fallback can be a 2D preview, list, still image, or editable inspector as
long as it supports the actual task. “MetalKit unavailable” is not a useful
fallback if the app’s core outcome is still possible with a simpler view.

## AI review surface

For a local model that suggests a material, camera, shader parameter, or asset
classification, use a review screen with:

~~~text
source preview and provenance
  -> proposed change
  -> fields/evidence used
  -> device/profile constraints
  -> Accept / Edit / Dismiss
  -> before/after preview and Undo
~~~

Keep model availability, prompt/context revision, generated values, and the
accepted render configuration separate. The model must not silently emit and
execute arbitrary shader code or change a protected data projection. A typed
proposal can still be wrong; deterministic bounds and format checks precede
the renderer.

## Performance as a design state

Do not hide a degraded device path. A small status treatment can say:

- “Full quality” when the measured profile is active;
- “Lower detail to keep the device responsive” when the app reduced work;
- “Paused while off-screen” when the render is not consuming resources;
- “Preview unavailable; use list mode” when the route cannot run.

Define a product threshold for responsiveness, not only a developer metric.
Use a real device matrix for load time, hitches, memory, thermal behavior,
screen refresh, orientation, background/foreground, and long sessions. Keep
performance charts and logs out of customer-facing copy unless they help the
person make a choice.

## Native polish checklist

- A standard SwiftUI shell owns navigation, state, and actions.
- MetalKit is used for a named rendering requirement.
- The view has a bounded loading/error/paused/off-screen lifecycle.
- GPU resources are runtime implementation details, not domain identity.
- Glass groups actions and leaves status readable.
- AI output is typed, reviewable, reversible, and device-aware.
- Essential information has an accessible non-texture route.
- Reduced Motion/transparency and low-power/thermal states preserve meaning.
- The visual and its surrounding controls are tested in light/dark, large text,
  VoiceOver, keyboard/pointer, and representative physical devices.

## Sources

- [MetalKit](https://developer.apple.com/documentation/metalkit/)
- [MTKView](https://developer.apple.com/documentation/metalkit/mtkview/)
- [MTKViewDelegate](https://developer.apple.com/documentation/metalkit/mtkviewdelegate/)
- [MTKTextureLoader](https://developer.apple.com/documentation/metalkit/mtktextureloader/)
- [MTKMesh](https://developer.apple.com/documentation/metalkit/mtkmesh/)
- [Model I/O](https://developer.apple.com/documentation/modelio/)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [UIViewRepresentable](https://developer.apple.com/documentation/swiftui/uiviewrepresentable/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [accessibilityReduceMotion](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion)
- [Human Interface Guidelines accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Testing performance](https://developer.apple.com/documentation/xctest/performance-tests)
