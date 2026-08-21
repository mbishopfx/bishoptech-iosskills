# SwiftUI Metal, Core Image, and VideoToolbox GPU-media review design

This design companion turns a GPU-heavy image, camera, editor, or media-processing feature into a calm native SwiftUI task. SwiftUI owns the product shell, state, review, accessibility, and explicit actions. Core Video owns frame envelopes and buffer lifetime. Core Image owns lazy image recipes and reusable render contexts. Metal owns direct GPU commands only where measured control is needed. VideoToolbox owns low-level codec sessions when a higher-level media route is not sufficient.

Pair this page with the [SwiftUI Metal, Core Image, and VideoToolbox GPU-media review](../42-framework-deep-dives/98-swiftui-metal-coreimage-videotoolbox-gpu-media-review.md), [GPU-media capability route](../50-capability-recipes/129-swiftui-metal-coreimage-videotoolbox-gpu-media-review-route.md), [GPU-media proof matrix](../60-verification/123-swiftui-metal-coreimage-videotoolbox-gpu-media-review-proof-matrix.md), and [compile-oriented recipes](../70-code-recipes/141-swiftui-metal-coreimage-videotoolbox-gpu-media-review-recipes.md).

## Design contract

A person should be able to answer these questions without knowing which Apple framework is underneath:

1. What media or visual task is this screen helping me complete?
2. Is the source live, paused, imported, generated, filtered, encoded, or unavailable?
3. What will the GPU operation change, and what will remain untouched?
4. Is this result a preview, a cached frame, a local AI suggestion, or a committed export?
5. Why does the app need camera, photo, microphone, file, or media access?
6. What happens if the device cannot support the effect, is under thermal pressure, or loses the source?
7. Can I inspect, reject, undo, or complete the task without relying on a shader, animation, color, or precise gesture?

The visual hierarchy is:

~~~text
task context
  -> source and privacy state
  -> media preview
  -> processing status and freshness
  -> controls and review
  -> optional AI proposal
  -> explicit export/save/apply action
  -> completion, undo, and recovery
~~~

The GPU is an implementation detail until the product has a reason to expose a measurable state such as processing, dropped frames, export progress, or reduced-quality mode.

## Native screen anatomy

| Region | Responsibility | Design rule |
| --- | --- | --- |
| Navigation shell | Exit, title, source, settings | Keep it stable while frames change. |
| Privacy/source banner | Permission, source, capture state | Explain why access is needed and what is retained. |
| Preview surface | Camera, imported image, generated frame, or video | Preserve the source framing and make stale output visible. |
| Processing status | Idle, rendering, waiting, dropped, thermal, failed | Name the next action; do not imply a false percentage. |
| Tool group | Filter, crop, quality, compare, reset, export | Use semantic controls and clear enabled states. |
| Review card | Before/after, proposal, format, color, source revision | Separate preview from the committed media record. |
| Alternate route | Still capture, low-quality preview, list, manual settings | Preserve the task when a capability is unavailable. |
| Confirmation area | Apply, save, export, discard, undo | Use the concrete side effect, not an ambiguous Done label. |

Use a dedicated editor or sheet for detailed controls. Keep the preview visually dominant but do not let it become the only source of meaning. The same source revision, filter state, and result status should be available as text.

## State language

| State | Primary copy | Secondary treatment |
| --- | --- | --- |
| Ready | “Choose a source to preview.” | Explain supported sources and access. |
| Permission needed | “Allow camera access to process live frames.” | Explain before the system prompt; offer cancel. |
| Importing | “Preparing the selected media.” | Show source name and a cancellable task. |
| Live | “Live preview.” | Show whether the preview is filtered and its current quality mode. |
| Processing | “Rendering this frame.” | Keep controls that remain safe; avoid a decorative spinner over the entire image. |
| Waiting for GPU | “Waiting for the next frame.” | Explain when backpressure or a bounded queue is active. |
| Dropped frame | “Preview skipped a frame to stay responsive.” | Keep the last complete frame and expose a lower-quality option. |
| Stale | “Preview is from the last available frame.” | Show age or paused state; do not imply live output. |
| Unsupported | “This effect is unavailable on this device.” | Offer a native or reduced-quality fallback. |
| Thermal pressure | “Reducing preview quality to keep the device comfortable.” | Preserve the task and explain how to restore quality. |
| AI proposal | “Suggested adjustment.” | Show source revision, explanation, edit, reject, and apply. |
| Exporting | “Saving the processed video.” | Show destination, format, cancellation, and retention. |
| Complete | “Saved to Photos.” or the actual outcome | Offer undo/delete only when the product supports it. |
| Failed | “The preview could not be rendered.” | Preserve the source and identify a recovery action. |

Color, blur, glow, and animation may reinforce these states. None should be their only carrier. A green tint is not a readable success message, and a moving progress ring is not proof that a codec session is advancing.

## Functional Liquid Glass composition

Use Liquid Glass around the functional layer:

- navigation and dismissal;
- source selection and privacy status;
- compact filter or comparison controls;
- processing status and recovery;
- review and explicit export/apply actions.

Keep the media or visual result as the content layer:

~~~text
camera/image/video frame + filtered output + comparison
  = content layer

navigation + status + controls + review + confirmation
  = functional layer
~~~

Good GPU-media glass patterns:

- one top source/status group;
- one bottom tool group with stable controls;
- one review card that expands into a sheet;
- one compact processing status that does not obscure the focal media;
- one compare control with an accessible before/after label.

Poor patterns:

- a glass pane over every previewed object;
- a full-screen blur that hides whether the output is current;
- a shader that changes text contrast under the control group;
- animated refraction during an interaction that requires visual comparison;
- icon-only export or destructive actions;
- a translucent status pill that is the only indication of thermal reduction.

The glass material should support legibility over bright, dark, colorful, and moving media. If reduced transparency, increased contrast, or a target platform removes the preferred effect, retain the same hierarchy with a system material or opaque surface.

## Media provenance and comparison

An output preview should expose enough provenance to avoid confusing it with source truth:

| Field | Example |
| --- | --- |
| Source | Camera frame, imported asset, generated image, or video time. |
| Source revision | App-owned revision that changes when the source or intent changes. |
| Processing | Native filter, shader, Core Image graph, Metal pass, or codec route. |
| Color/format | Source and output color space, pixel format, orientation, and dynamic-range policy when relevant. |
| Freshness | Live, paused, cached, stale, or completed export. |
| AI | Model availability and proposal status, never a claim that the pixels are correct. |
| Side effect | Preview only, replace draft, save copy, export, or publish. |

Before/after comparison should preserve the same crop and source time where possible. If a preview is downsampled or color-managed differently from export, say so. A small “preview” label is useful, but the review surface should also state the actual export setting.

## Accessibility and alternate input

Canvas does not make each drawn element an accessibility element, and a shader does not make its output self-describing. Add semantic SwiftUI controls over or beside custom visual content:

- a text label for the source and current result;
- a real before/after toggle;
- filter names and values as adjustable controls;
- a processing status with an accessible value;
- an explicit cancel, reset, save, and export action;
- a list or form route for precise adjustments;
- keyboard, pointer, Voice Control, Switch Control, and full keyboard access where supported;
- Dynamic Type that can move long status copy into a sheet;
- Reduce Motion behavior that removes decorative preview animation;
- increased contrast and reduced-transparency fallbacks.

If a visual effect is essential to understanding the result, pair it with a textual or structural description. “Edges highlighted” is more useful than a color-only edge glow. If a color transformation may reduce contrast or be visually ambiguous, provide a compare route and retain the original.

## AI proposal design

The local AI surface should be a source-linked suggestion:

~~~text
typed source summary
  -> model availability and authorization
  -> local proposal
  -> source revision check
  -> editable review
  -> deterministic media operation
~~~

Show:

- the source revision and whether it is still current;
- the model availability state;
- the proposed filter, crop, caption, or export setting;
- what the app will actually do if accepted;
- edit, reject, and reset actions;
- a clear fallback if the model is unavailable.

Do not let generated text choose an arbitrary shader function, raw Metal function name, unsafe codec setting, or external destination. Map model output into a small app-owned enum or typed parameter range, validate it, and let the user apply the deterministic operation.

Example copy:

- “Suggested: reduce highlights on this source.”
- “The suggestion uses the current imported image. Review before applying.”
- “The on-device model is unavailable, so the standard filter controls remain available.”
- “This changes the preview only until you choose Apply filter.”

## Performance and thermal calm

Performance status should be actionable:

- show a lower-quality preview choice instead of a technical queue name;
- keep the last complete frame when live processing falls behind;
- avoid making a person wait for a dropped frame that is no longer useful;
- make export progress and cancellation distinct from preview rendering;
- reduce work or frame rate under thermal pressure while preserving the saved source;
- restore full quality only after a measured safe condition, not after an arbitrary timer;
- do not make the interface flash every time a frame is skipped.

For continuous effects, a stable preview is usually better than a maximum-detail preview that stutters. Treat memory, battery, heat, and frame pacing as part of the product experience. Record device/OS/source conditions in performance evidence.

## Privacy and retention design

Before presenting capture or import:

- state why camera, microphone, Photos, or file access is needed;
- say whether frames are processed locally;
- say whether source media, pixel buffers, thumbnails, exports, or diagnostics are retained;
- let the person cancel without losing an existing draft;
- distinguish local AI from any network or cloud path;
- delete temporary buffers and derived media according to the product policy;
- avoid logging raw frames, audio, location, or sensitive metadata by default.

The fact that a Core Image or Metal operation runs on the GPU does not by itself prove that media stays private. Privacy is a product and data-flow property that needs explicit evidence.

## Review checklist

- [ ] The task and source are clear before the first effect runs.
- [ ] Live, paused, cached, stale, preview, and exported states are distinguishable.
- [ ] Liquid Glass is limited to functional controls and remains readable over the content.
- [ ] Native SwiftUI is the default route where it meets the requirement.
- [ ] Canvas and shaders have semantic overlays and non-visual descriptions.
- [ ] The source revision, format, color, orientation, and output status are reviewable.
- [ ] AI suggestions are typed, bounded, editable, and never an implicit commit.
- [ ] Dropped frames, reduced quality, memory pressure, and thermal changes have calm copy.
- [ ] Camera/photo/microphone/file access and retention are explained.
- [ ] A non-GPU or lower-capability fallback exists where the task permits it.
- [ ] Physical-device and release proof are separate from a preview or simulator result.

## Sources

- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Canvas](https://developer.apple.com/documentation/swiftui/canvas)
- [GraphicsContext](https://developer.apple.com/documentation/swiftui/graphicscontext)
- [Shader](https://developer.apple.com/documentation/swiftui/shader)
- [Graphics and rendering modifiers](https://developer.apple.com/documentation/swiftui/view-graphics-and-rendering)
- [VisualEffect](https://developer.apple.com/documentation/swiftui/visualeffect)
- [Core Image](https://developer.apple.com/documentation/coreimage)
- [CIImage](https://developer.apple.com/documentation/coreimage/ciimage)
- [CIContext](https://developer.apple.com/documentation/coreimage/cicontext)
- [CIFilter](https://developer.apple.com/documentation/coreimage/cifilter-swift.class)
- [Core Video](https://developer.apple.com/documentation/corevideo)
- [CVPixelBuffer](https://developer.apple.com/documentation/corevideo/cvpixelbuffer)
- [CVPixelBufferPool](https://developer.apple.com/documentation/corevideo/cvpixelbufferpool)
- [CVMetalTextureCache](https://developer.apple.com/documentation/corevideo/cvmetaltexturecache)
- [Metal](https://developer.apple.com/documentation/metal)
- [MTLDevice](https://developer.apple.com/documentation/metal/mtldevice)
- [MTLCommandQueue](https://developer.apple.com/documentation/metal/mtlcommandqueue)
- [MTLCommandBuffer](https://developer.apple.com/documentation/metal/mtlcommandbuffer)
- [MetalKit](https://developer.apple.com/documentation/metalkit)
- [MTKView](https://developer.apple.com/documentation/metalkit/mtkview)
- [VideoToolbox](https://developer.apple.com/documentation/videotoolbox)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Human Interface Guidelines: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)

## Related routes

- [SwiftUI Metal, Core Image, and VideoToolbox GPU-media review](../42-framework-deep-dives/98-swiftui-metal-coreimage-videotoolbox-gpu-media-review.md)
- [GPU-media capability route](../50-capability-recipes/129-swiftui-metal-coreimage-videotoolbox-gpu-media-review-route.md)
- [GPU-media proof matrix](../60-verification/123-swiftui-metal-coreimage-videotoolbox-gpu-media-review-proof-matrix.md)
- [GPU-media compile-oriented recipes](../70-code-recipes/141-swiftui-metal-coreimage-videotoolbox-gpu-media-review-recipes.md)
