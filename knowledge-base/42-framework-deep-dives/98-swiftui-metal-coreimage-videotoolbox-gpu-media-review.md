# SwiftUI Metal, Core Image, and VideoToolbox GPU-media review

This deep dive defines the boundary between SwiftUI’s native drawing/effect tools, Metal’s direct GPU command model, Core Image’s lazy image graph, Core Video’s pixel-buffer pipeline, VideoToolbox’s low-level codec sessions, and the product’s on-device AI/media state. It extends the existing [Metal, Core Image, VideoToolbox, and GPU media deep dive](20-metal-coreimage-videotoolbox-and-gpu-media.md), [MetalKit rendering route](../50-capability-recipes/85-metalkit-rendering-capability-route.md), [MetalKit visual-surface design](../21-design-deep-dives/82-metalkit-native-visual-surface-design.md), and [SwiftUI Vision/Core ML live-observation review](95-swiftui-vision-core-ml-live-observation-review.md) with a SwiftUI-owned decision and proof boundary.

The core rule is simple: use the highest-level Apple renderer that meets the measured requirement, preserve source pixel/format/time provenance, and keep a GPU output separate from the source media and from any AI or domain claim.

## The composed pipeline

A live camera, media, or visualization route typically looks like this:

~~~text
SwiftUI task and native shell
  -> source permission and target gate
  -> AVFoundation / Photos / file / generated input
  -> CVPixelBuffer plus pixel format, color, orientation, and timestamp
  -> optional CIImage lazy graph
  -> optional Metal texture cache or MTLTexture
  -> command queue and command buffer
  -> render/compute pipeline or Core Image context
  -> SwiftUI Canvas/effect, MTKView, RealityKit, AVAsset output, or review image
  -> optional local AI preprocessing/proposal
  -> user review and deterministic media/domain commit
  -> performance, privacy, physical-device, archive, and release proof
~~~

Keep these authorities separate:

| Fact | Owner | Meaning |
| --- | --- | --- |
| Source frame | AVFoundation/Core Video/Photos/file | The app received or loaded a media value with source metadata. |
| Pixel buffer | Core Video | A buffer with a pixel format, dimensions, attachments, and lifetime. |
| CIImage | Core Image | A lazy image recipe; it is not necessarily rendered pixels. |
| Metal texture | Core Video/Metal | A GPU-accessible view of a source or intermediate resource. |
| Command buffer | Metal | Ordered GPU work that is encoded, committed, and completed or errored. |
| Filtered output | Core Image/Metal/VideoToolbox | Pixels produced by a declared operation under a chosen format/color policy. |
| Display surface | SwiftUI/MetalKit/RealityKit/AVFoundation | The current presentation or export target. |
| AI result | Core ML/Foundation Models or another local model | A proposal or analysis from named input. |
| Product truth | App-owned model and user action | The accepted edit, export, record, or side effect. |

A shader compiling, a CIImage existing, a pixel buffer arriving, or a command buffer completing does not prove that the displayed color, frame timing, accessibility, camera meaning, or user-approved product outcome is correct.

## Pick the smallest rendering route

Use a route ladder:

| Need | First choice | Escalate when |
| --- | --- | --- |
| Standard image, shape, text, or animation | SwiftUI native views, Shape, Image, Canvas | The measured workload exceeds the native route. |
| Many dynamic 2D primitives | Canvas and GraphicsContext | The product needs custom per-pixel or GPU shader work. |
| A color/filter/distortion effect on a SwiftUI view | SwiftUI colorEffect, layerEffect, or distortionEffect | The effect needs a broader frame graph or persistent resource ownership. |
| Still-image filtering and export | Core Image and a reused CIContext | A custom Metal kernel, command graph, or exact GPU resource control is required. |
| Custom 2D/3D draw or compute | Metal or MetalKit | A higher-level route cannot satisfy the measured requirement. |
| Live camera pixel processing | AVFoundation/Core Video plus Core Image or Metal | The app owns a codec, conversion, or custom low-level pipeline. |
| Hardware encode/decode or pixel transfer | VideoToolbox | Only when AVFoundation/AVAssetReader/Writer does not own the needed behavior. |
| 3D scene content | RealityKit or SceneKit migration route | The product truly needs a custom GPU renderer or shader pipeline. |

Do not choose Metal because a screenshot looks “more premium.” Choose it for a named requirement such as a measured frame budget, custom compute, a shader graph, a device-supported pixel path, or a renderer that a higher-level framework cannot express.

## Metal device and command ownership

Metal’s MTLDevice represents a GPU device and its capabilities. Query feature support and limits at runtime. A symbol available in the SDK is not proof that the selected iPhone/iPad GPU supports it. Record the selected device, feature family, pixel formats, argument/resource limits, and any Metal 3 or Metal 4 requirement.

A classic Metal submission route is:

1. Obtain the intended MTLDevice.
2. Create a small deliberate number of MTLCommandQueue instances.
3. Load and validate shader libraries and pipeline states outside the frame loop.
4. Acquire or allocate source/output resources with an explicit lifetime policy.
5. Create an MTLCommandBuffer from the owning queue.
6. Encode render, compute, or blit commands in the intended order.
7. Keep required resources alive until the GPU no longer uses them.
8. Attach scheduled/completed/error handling where the feature needs it.
9. Commit the command buffer.
10. Recycle buffers and resources only after completion policy permits it.

Apple documents that a command queue maintains an ordered list of command buffers and that a command buffer cannot be reused after it is committed. A queue may be used from multiple threads, but the app still needs a clear ownership policy for resources, encoders, frame slots, and state mutations.

Use bounded in-flight work. If a camera produces frames faster than the GPU or consumer can finish them, choose whether to drop, replace, or queue a small number of frames. Unbounded retention turns a visual feature into a memory and latency problem.

## Pipeline and shader lifecycle

A render or compute pipeline is a compiled description of GPU work. Treat shader and pipeline resources like versioned product assets:

- target membership is explicit;
- shader source and function names are reviewed;
- function signatures and argument layouts are versioned;
- pipeline creation occurs before the hot frame path;
- device support and pixel formats are checked;
- shader validation is a development diagnostic, not production performance proof;
- pipeline/resource errors have a visible fallback;
- archive validation confirms the library is present.

For SwiftUI Shader, Apple describes a reference to a function in a Metal shader library plus bound uniform arguments. SwiftUI can apply it as a color, layer, or distortion effect, and Shader can compile asynchronously. Use that API for bounded view effects, not as a hidden substitute for a full renderer.

A shader effect must declare:

- the view or content it receives;
- coordinate space and scale assumptions;
- uniform values and their units;
- maximum sample offset for sampling effects;
- enabled/disabled state;
- reduced-motion and reduced-effects fallback;
- color space and output range;
- failure behavior when the shader cannot compile or the target cannot support it.

Never let an AI model generate arbitrary Metal source or unvalidated shader arguments. A model may choose among app-owned, signed, typed presets such as subtle blur, tint, grain, or highlight. The renderer validates ranges and selects a known function.

## Core Image is a lazy, color-managed graph

CIImage is a representation or recipe for image processing. It does not necessarily contain rendered pixels. CIFilter creates a new graph node, and CIContext evaluates the graph into a destination.

Apple documents these concurrency boundaries:

- CIImage and CIContext are immutable and can be shared safely among threads.
- CIFilter is mutable and should not be shared concurrently without isolation.
- CIContext maintains internal state such as Metal command queues, compiled-kernel caches, and intermediate buffers.
- Creating many CIContext instances is discouraged; reuse a deliberate context per rendering surface or background task.
- Core Image performs color management through a working color space unless the app specifies another policy.

Record the source and destination color spaces. A filtered image can look correct on one display and differ after export if the app silently changes working space, extended dynamic range, alpha, orientation, or pixel format.

Use a Core Image route when the product needs built-in filters, a lazy graph, a color-managed render, a standard image destination, or a small reusable custom kernel. Render at the edge of the pipeline, not every time a view reads a CIImage.

A CIImage graph is not an edit record. The product should store the source identity, filter name/version, parameter values, crop/orientation policy, and user decision so an edit can be reproduced or undone.

## Core Video pixel-buffer and texture boundaries

CVPixelBuffer is a Core Video image buffer. It carries memory, dimensions, pixel format, and attachments that may describe color, orientation, timing, or camera metadata. CVPixelBufferPool manages recyclable pixel buffers. Keep the pool bounded and match its attributes to the actual consumer.

CVMetalTextureCache can create a CVMetalTexture backed by a Core Video image buffer for Metal rendering or compute. The cache is a bridge, not a copy-free license to ignore lifetime:

- the source pixel buffer must remain valid while the GPU work uses it;
- the created texture must match the expected plane, pixel format, width, and height;
- bi-planar camera formats may need separate luma/chroma handling;
- color conversion and range policy must be explicit;
- cache flushing is a resource policy, not a per-frame superstition;
- the output should not be published as complete until the command buffer or downstream consumer has finished.

Keep a frame envelope:

| Field | Why it matters |
| --- | --- |
| sourceID | App-owned identity for the camera/media source. |
| frameIndex | Monotonic intake count for drop and latency diagnosis. |
| presentationTime | Source timing and synchronization. |
| pixelFormat | Determines conversion and shader interpretation. |
| dimensions | Determines texture allocation and layout. |
| colorSpace/range | Prevents silent color drift. |
| orientation | Keeps display and model geometry aligned. |
| bufferGeneration | Rejects stale or recycled data. |
| privacyClass | Controls logging, persistence, and model handoff. |

Do not log raw buffer addresses, unredacted frames, or entire attachments in production diagnostics.

## VideoToolbox is a low-level codec session boundary

VideoToolbox provides direct access to hardware-assisted video encoding, decoding, and pixel transfer. Apple notes that apps that do not need direct hardware encoder/decoder access generally should not use it directly.

A compression session has a lifecycle:

1. Create the session with the intended codec and output callback.
2. Configure only the properties the product needs.
3. Submit frames with valid timing, dimensions, pixel format, color metadata, and frame lifetime.
4. Handle asynchronous output and status/error flags.
5. Complete pending frames when the route is ending or a pass requires it.
6. Invalidate the session.
7. Release or detach resources and finalize the container through the selected AVFoundation route.

A decompression session follows the same ownership discipline: create, configure, decode, handle output frames, invalidate, and release. VideoToolbox does not own the final container, audio synchronization, user-facing export UI, Photos destination, or share policy. If the product needs a playable file, prove the AVAssetWriter/container/muxing path separately.

Do not hide a codec session inside a SwiftUI view. Put it in an actor, coordinator, or media pipeline object with explicit cancellation and teardown. A successful encode callback does not prove that the final file is playable, synchronized, private, or accessible.

## SwiftUI Canvas and GraphicsContext

Canvas is an immediate-mode drawing surface for rich dynamic 2D graphics. GraphicsContext can draw paths, images, text, symbols, filters, transforms, blends, and layers. SwiftUI can render Canvas asynchronously when the route allows it.

Canvas has a crucial accessibility boundary: Apple documents that Canvas does not provide interactivity or accessibility for individual elements, including views passed as symbols. Use Canvas for the visual layer, but provide semantic SwiftUI overlays, a list, labels, or a custom accessible control path for task-critical elements.

Choose Canvas for:

- particle fields and data visualizations;
- decorative overlays that do not need independent hit targets;
- large numbers of dynamic 2D marks;
- lightweight previews with a separate semantic route.

Do not use Canvas as the only representation of:

- an editable timeline;
- a selected object list;
- a media scrubber;
- an AI proposal with actions;
- a critical warning or confirmation;
- a chart that must be navigated element by element.

Use GraphicsContext’s environment resolution for image, color, display, and layout assumptions. Keep source data separate from drawing commands so the same model can feed a semantic list or accessible text summary.

## SwiftUI shaders and native composition

SwiftUI’s graphics/rendering modifiers let an app apply a shader to a view. Use them as controlled visual effects:

| Modifier | Product meaning | Review boundary |
| --- | --- | --- |
| colorEffect | Per-pixel color transformation | Preserve readability and color semantics. |
| layerEffect | Filter over a rendered layer | Bound sample offsets and memory. |
| distortionEffect | Pixel-location distortion | Reduce motion and keep content geometry usable. |
| visualEffect | Geometry-aware visual effect | Do not use it to replace layout or semantics. |
| Canvas | Immediate-mode drawing | Add semantic overlays for interactive elements. |

Do not apply high-cost effects to the entire navigation shell or to text that needs maximum clarity. Keep effects in the content layer and use native SwiftUI controls, materials, and Liquid Glass for the functional layer.

Shader functions should use app-owned parameters with explicit units, ranges, and accessibility fallbacks. A setting such as intensity, radius, or speed must have a reduced-effects policy. A shader failure should preserve the source view or a standard material, not produce a blank screen.

## On-device AI and GPU preprocessing

Core ML or Foundation Models can use local compute for summarization, classification, parameter selection, or editing proposals. The GPU path remains the source/preprocessing/presentation authority:

~~~text
source frame
  -> deterministic crop/scale/color conversion
  -> optional model input tensor
  -> local model output
  -> typed proposal
  -> visible review
  -> deterministic render/export/commit
~~~

A model may propose:

- a signed filter preset;
- a crop or region to review;
- an export quality choice;
- a caption or accessibility summary;
- a suggested non-destructive effect amount;
- a processing route when the device supports several.

The model must not silently change source pixels, dimensions, color space, timestamps, privacy class, or export destination. Reject proposals that are out of range, stale, incompatible with the current source revision, or unavailable on the selected device.

If the model is unavailable, the GPU/media route remains functional with a deterministic preset or manual controls. “On-device” describes where computation occurs; it does not prove that logs, source frames, or exported files remain private.

## Liquid Glass and GPU effects

Use Liquid Glass for navigation, tool groups, playback/capture status, review, and explicit controls. Use Metal/Core Image/SwiftUI shaders for content effects that the product actually needs.

Do not:

- recreate native controls with a custom blur;
- put a high-cost shader behind every glass button;
- blur a full camera view to imitate system chrome;
- let a generated effect make a source frame look like verified reality;
- use motion or shimmer as the only progress/error signal.

A GPU effect should have a standard fallback, a reduced-motion/reduced-transparency policy, and an accessible source/summary. Keep the effect’s cost measurable and its state visible.

## Accessibility and alternate input

GPU surfaces often remove semantics. Pair every custom surface with:

- a stable SwiftUI label and value;
- semantic controls for play, pause, scrub, apply, undo, reset, and export;
- a text or list summary of important visual elements;
- Dynamic Type-safe status and review copy;
- Reduce Motion behavior for animated shaders and continuous effects;
- increased contrast and reduced-transparency behavior;
- VoiceOver actions that do not require pixel targeting;
- keyboard, pointer, switch, or Voice Control paths where relevant;
- an original-media or standard-render fallback when an effect is unavailable.

Canvas marks, shader particles, and filtered pixels are not individually accessible by default. Accessibility must come from the app-owned data model and semantic overlay.

## Privacy, memory, and thermal boundaries

Treat camera frames, photos, video buffers, GPU captures, model inputs, and generated exports as potentially sensitive. The route should:

- start protected capture only inside the user-approved task;
- use the minimum frame resolution and retention needed;
- avoid raw-frame logging;
- keep CVPixelBuffer pools and in-flight command buffers bounded;
- release or recycle textures after completion;
- avoid creating CIContext or pipeline state inside each frame;
- stop VideoToolbox sessions and capture outputs during teardown;
- cancel model preprocessing when the source revision changes;
- test low-power, background, interruption, memory pressure, and thermal states;
- report an effect as unavailable rather than silently changing color or timing;
- separate debug GPU captures from production diagnostics.

A high frame rate on a new device or a short simulator preview is not universal performance proof. Record device, OS, build, source format, effect graph, resolution, frame cadence, duration, and thermal state.

## Proof boundary

The [GPU/media proof matrix](../60-verification/123-swiftui-metal-coreimage-videotoolbox-gpu-media-review-proof-matrix.md) and [compile-oriented recipes](../70-code-recipes/141-swiftui-metal-coreimage-videotoolbox-gpu-media-review-recipes.md) separate:

- source/SDK: official API and availability;
- compile: target membership, shader resources, linked frameworks, signatures;
- preview/simulator: SwiftUI copy, Canvas/static effects, fallback and semantic overlays;
- physical device: camera/media frames, pixel formats, GPU features, shader behavior, frame pacing, memory and thermal;
- system: camera/photo privacy, export, background/interruption, asset availability;
- archive/release: signed resources, codec path, entitlements, privacy metadata, TestFlight and release-like performance.

A command buffer completion, a CIImage, a shader compile, a pixel buffer, or a model output is one observation in a pipeline. It is never by itself a complete media, accessibility, privacy, or release claim.

## Sources

- [Metal](https://developer.apple.com/documentation/metal)
- [MTLDevice](https://developer.apple.com/documentation/metal/mtldevice)
- [MTLCommandQueue](https://developer.apple.com/documentation/metal/mtlcommandqueue)
- [MTLCommandBuffer](https://developer.apple.com/documentation/metal/mtlcommandbuffer)
- [Setting up a command structure](https://developer.apple.com/documentation/metal/gpu_devices_and_work_submission/setting_up_a_command_structure)
- [Performing calculations on a GPU](https://developer.apple.com/documentation/metal/performing-calculations-on-a-gpu)
- [Understanding the Metal 4 core API](https://developer.apple.com/documentation/metal/understanding-the-metal-4-core-api)
- [Metal feature sets](https://developer.apple.com/metal/feature-sets/)
- [Metal feature set tables](https://developer.apple.com/metal/Metal-Feature-Set-Tables.pdf)
- [Validating your app’s Metal shader usage](https://developer.apple.com/documentation/xcode/validating-your-apps-metal-shader-usage)
- [Core Image](https://developer.apple.com/documentation/coreimage)
- [CIContext](https://developer.apple.com/documentation/coreimage/cicontext)
- [CIImage](https://developer.apple.com/documentation/coreimage/ciimage)
- [CIFilter](https://developer.apple.com/documentation/coreimage/cifilter-swift.class)
- [Core Video](https://developer.apple.com/documentation/corevideo)
- [CVPixelBuffer](https://developer.apple.com/documentation/corevideo/cvpixelbuffer)
- [CVPixelBufferPool](https://developer.apple.com/documentation/corevideo/cvpixelbufferpool)
- [CVMetalTextureCache](https://developer.apple.com/documentation/corevideo/cvmetaltexturecache)
- [CVMetalTexture](https://developer.apple.com/documentation/corevideo/cvmetaltexture)
- [Video Toolbox](https://developer.apple.com/documentation/videotoolbox)
- [VTCompressionSession](https://developer.apple.com/documentation/videotoolbox/vtcompressionsession-api-collection)
- [VTDecompressionSession](https://developer.apple.com/documentation/videotoolbox/vtdecompressionsession-api-collection)
- [MetalKit](https://developer.apple.com/documentation/metalkit)
- [MTKView](https://developer.apple.com/documentation/metalkit/mtkview)
- [MTKViewDelegate](https://developer.apple.com/documentation/metalkit/mtkviewdelegate)
- [MTKTextureLoader](https://developer.apple.com/documentation/metalkit/mtktextureloader)
- [Canvas](https://developer.apple.com/documentation/swiftui/canvas)
- [GraphicsContext](https://developer.apple.com/documentation/swiftui/graphicscontext)
- [Shader](https://developer.apple.com/documentation/swiftui/shader)
- [Graphics and rendering modifiers](https://developer.apple.com/documentation/swiftui/view-graphics-and-rendering)
- [VisualEffect](https://developer.apple.com/documentation/swiftui/visualeffect)
- [Drawing and graphics](https://developer.apple.com/documentation/swiftui/drawing-and-graphics)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)

## Related knowledge-base routes

- [Metal, Core Image, VideoToolbox, and GPU media](20-metal-coreimage-videotoolbox-and-gpu-media.md)
- [MetalKit rendering capability route](../50-capability-recipes/85-metalkit-rendering-capability-route.md)
- [MetalKit native visual-surface design](../21-design-deep-dives/82-metalkit-native-visual-surface-design.md)
- [SwiftUI Metal/Core Image/VideoToolbox GPU-media design](../21-design-deep-dives/126-swiftui-metal-coreimage-videotoolbox-gpu-media-review-design.md)
- [SwiftUI Metal/Core Image/VideoToolbox GPU-media route](../50-capability-recipes/129-swiftui-metal-coreimage-videotoolbox-gpu-media-review-route.md)
