# SwiftUI Metal, Core Image, and VideoToolbox GPU-media review route

Use this route when an iOS app needs GPU drawing, image processing, live camera effects, custom media frames, or low-level encode/decode inside a native SwiftUI product shell. It is a route-selection guide, not a list of APIs to invoke indiscriminately.

Pair it with the [SwiftUI Metal, Core Image, and VideoToolbox GPU-media review](../42-framework-deep-dives/98-swiftui-metal-coreimage-videotoolbox-gpu-media-review.md), [GPU-media design companion](../21-design-deep-dives/126-swiftui-metal-coreimage-videotoolbox-gpu-media-review-design.md), [GPU-media proof matrix](../60-verification/123-swiftui-metal-coreimage-videotoolbox-gpu-media-review-proof-matrix.md), and [compile-oriented recipes](../70-code-recipes/141-swiftui-metal-coreimage-videotoolbox-gpu-media-review-recipes.md).

## Choose the outcome first

| Product outcome | Start with | Add only when the evidence requires it |
| --- | --- | --- |
| Draw a custom native visualization | SwiftUI shapes, Path, Canvas, GraphicsContext | A shader or Metal surface for a measured effect or scale requirement. |
| Apply a supported image effect | Core Image and one reusable CIContext | Metal kernels or custom shaders for a missing operation or performance need. |
| Apply a bounded SwiftUI visual effect | Shader and SwiftUI graphics modifiers | A lower-level pipeline only when arguments and output semantics are insufficient. |
| Process camera frames | AVFoundation plus CVPixelBuffer ownership | Core Image, CVMetalTextureCache, or Metal for the selected processing stage. |
| Build a custom continuous renderer | MetalKit MTKView or a carefully owned Metal surface | Manual drawable/command scheduling and synchronization after profiling. |
| Run a custom GPU calculation | Metal compute pipeline | A more specialized route only after feature/device checks and measurement. |
| Encode or decode media at low level | VideoToolbox session APIs | AVFoundation/AVAsset export when it already meets the product need. |
| Propose a media adjustment on device | Foundation Models or another approved local model over a typed summary | Never let model output directly select raw shader/Metal/codec identifiers. |

The default architecture is a SwiftUI shell around a small, typed media pipeline. The renderer should not own product truth, and the model should not own GPU resource lifetime.

## Route map

~~~text
SwiftUI task and permission gate
  -> source owner: camera, Photos, file, generated content, or video
  -> frame envelope: CVPixelBuffer, format, color, orientation, timestamp, revision
  -> selected renderer:
       native SwiftUI / Canvas / Shader / Core Image / Metal / VideoToolbox
  -> output envelope and freshness state
  -> SwiftUI preview and accessible review
  -> optional bounded local AI proposal
  -> deterministic apply/save/export
  -> teardown, performance, physical-device, archive, and release proof
~~~

Keep a source revision separate from a frame timestamp. A timestamp does not prove that a result still matches the current source or user intent.

## Route A: native SwiftUI, Canvas, and GraphicsContext

Choose native SwiftUI drawing for charts, overlays, editor chrome, symbolic marks, and visualizations that do not need a custom per-pixel kernel.

Use Canvas when:

- the app needs immediate-mode drawing of many marks;
- the marks can be represented by a semantic SwiftUI overlay or list;
- drawing can be synchronous or explicitly asynchronous;
- the app can accept that individual Canvas elements are not independently interactive/accessibility elements.

Route shape:

1. Keep source and model state in SwiftUI.
2. Derive a small render snapshot.
3. Draw with Canvas or native primitives.
4. Place semantic labels, buttons, and adjustable controls outside the raw drawing.
5. Keep the original data accessible through a list, table, or detail route.

Do not use Canvas as a replacement for a live camera pipeline merely because it can draw an image. It is a SwiftUI drawing surface, not a proof of camera capture, pixel-buffer ownership, or codec behavior.

## Route B: SwiftUI Shader and graphics modifiers

Choose Shader when a view-bound color, distortion, or layer effect is the product requirement and SwiftUI can own the surface.

Route shape:

1. Define a known, app-owned shader function in the target’s shader library.
2. Pass bounded, typed arguments such as time, amplitude, or a color parameter.
3. Apply the appropriate SwiftUI graphics modifier.
4. Expose the semantic state through surrounding SwiftUI controls.
5. Provide a static or native fallback for unsupported devices, accessibility settings, or shader compilation failure.
6. Verify the shader output color and coordinate assumptions in the selected target.

Use a small allowlist of effects. A local AI proposal may select a value such as effect = softHighlight, but it must not return an arbitrary function name or raw source code. The SwiftUI view owns whether the effect can be applied.

Use shaders for presentation, not for irreversible media operations. If a person expects an export to contain the effect, render through the export pipeline and verify that path separately.

## Route C: Core Image for reusable image graphs

Choose Core Image when the requirement is an image-processing graph that can be expressed with CIFilter and rendered by a reusable CIContext.

Route shape:

1. Receive or import a CVPixelBuffer or image source.
2. Create a CIImage recipe without assuming it is rendered pixels.
3. Apply app-owned filters with bounded parameters.
4. Reuse a deliberate CIContext for the feature lifetime.
5. Render into a requested output format, color space, and destination.
6. Publish a result envelope with source revision and output metadata.

Ownership rules:

- CIImage is a lazy, immutable recipe; do not use its existence as proof that pixels were rendered.
- CIContext owns caches and rendering resources; avoid creating one per frame.
- CIFilter is mutable; do not share one mutable filter instance across concurrent work without a synchronization policy.
- Keep color-management choices explicit when comparing preview and export.
- Use a separate export task or bounded queue when the live preview must remain responsive.

Core Image is often the best first GPU route for a standard filter. It is not automatically the best route for every custom kernel, live frame graph, or codec.

## Route D: Core Video to Metal texture

Choose Core Video plus CVMetalTextureCache when a camera or video frame already exists as a CVPixelBuffer and a Metal pass needs a GPU-accessible texture.

Route shape:

~~~text
CVPixelBuffer
  -> lock or ownership policy
  -> format and plane validation
  -> CVMetalTextureCacheCreateTextureFromImage
  -> CVMetalTexture
  -> MTLTexture
  -> Metal render or compute command
  -> output texture or CVPixelBuffer
~~~

Before conversion, record:

- pixel format and whether it is bi-planar or single-plane;
- width, height, bytes-per-row, and plane dimensions;
- color attachments and transfer/range information when relevant;
- orientation and mirroring;
- buffer owner and release point;
- whether the source is reused by a capture session;
- whether the destination is a preview-only texture or an exportable image buffer.

Do not assume that a CVMetalTexture is valid after its source buffer is returned to a pool. Keep the source and derived texture alive until the command work and any completion-dependent consumer have finished according to the selected API contract.

Use CVPixelBufferPool when the output pipeline benefits from recycled buffers. Bound the pool and the number of in-flight frames. If conversion fails for a format or plane, route to a supported fallback and state that the effect is unavailable rather than silently showing an unrelated image.

## Route E: Metal device, queue, and pipeline

Choose direct Metal when the app needs custom render or compute behavior, predictable resource ownership, a shader unavailable in Core Image/SwiftUI, or a measured throughput/latency requirement.

The minimum ownership chain is:

~~~text
MTLDevice
  -> reusable MTLCommandQueue
  -> per-submit MTLCommandBuffer
  -> render or compute encoder
  -> validated pipeline state and bound resources
  -> commit
  -> bounded completion and release
~~~

Rules:

- Create and retain a compatible MTLDevice for the feature.
- Reuse command queues; do not create one for every frame.
- Create a fresh command buffer for each submission and do not reuse it after commit.
- Build render and compute pipeline states during setup or controlled reconfiguration, not in the hot path.
- Keep resources alive until the command buffer has finished using them.
- Bound in-flight work with a semaphore, queue, or actor-owned scheduler.
- Check device capabilities and feature support at runtime.
- Treat shader validation and release-build behavior as part of the target proof.

For a live preview, decide what happens when the GPU is behind:

| Policy | Good for | Tradeoff |
| --- | --- | --- |
| Keep latest frame | Camera preview and interactive effects | Intermediate frames are skipped. |
| Process every frame | Offline export or deterministic analysis | More memory and latency; not always interactive. |
| Bounded queue | Short bursts or controlled capture | Must expose backpressure and cancellation. |
| Lower-quality mode | Thermal or memory pressure | Output detail changes and needs user-visible copy. |

Do not use a growing task list as a frame scheduler.

## Route F: MetalKit visual surface

Use MTKView when a dedicated Metal-backed visual surface and delegate-driven drawing lifecycle fit better than a SwiftUI graphics modifier.

SwiftUI responsibilities:

- navigation, controls, status, settings, and review;
- lifecycle and target gating;
- a coordinator or model that owns the MTKView bridge.

MetalKit responsibilities:

- device and drawable configuration;
- draw/resize callbacks;
- command encoding and presentation;
- resource lifetime and frame pacing.

The bridge must be idempotent. SwiftUI updates must not recreate the device, command queue, pipeline, or delegate on every state change. Teardown must stop work, clear delegates, release subscriptions, and reject late callbacks.

Use MTKView for the surface, not as permission evidence or a replacement for AVFoundation. A rendered quad proves only that the rendering route accepted the data supplied to it.

## Route G: VideoToolbox sessions

Choose VideoToolbox when the product needs low-level hardware-assisted compression/decompression control that a higher-level AVFoundation route does not provide.

Compression route:

1. Decide codec, dimensions, frame timing, color, and destination policy.
2. Create a compression session.
3. Configure properties before encoding where supported.
4. Submit frames with source revision/timing metadata.
5. Handle output callbacks and status.
6. Complete pending frames before teardown when the API contract requires it.
7. Invalidate/release the session and close the destination cleanly.

Decompression route:

1. Create the decompression session with a declared output format.
2. Submit compressed samples with timing.
3. Handle output buffers and status.
4. Bound pending work and cancellation.
5. Complete/invalidate/release in the correct order.

Use AVAsset export or AVFoundation capture when those higher-level paths meet the requirement. A VideoToolbox session is not a general-purpose image filter. Keep codec output separate from a SwiftUI preview and prove the encoded file with an independent playback or inspection step.

## Route H: local AI preprocessing and proposal

Use local AI over a typed, minimal summary:

~~~swift
struct MediaProposalInput: Sendable {
    var sourceRevision: Int
    var sourceKind: String
    var width: Int
    var height: Int
    var colorPolicy: String
    var availableEffects: [String]
    var userIntent: String
}

enum MediaEffect: String, CaseIterable, Sendable {
    case none
    case softHighlight
    case monochrome
    case cropToSubject
}
~~~

The model may propose an app-owned effect and bounded values. The app must:

- check model availability and authorization;
- reject unknown effects and out-of-range values;
- cancel or mark results stale when sourceRevision changes;
- show the proposal and its source;
- let the person edit or reject it;
- apply the selected operation deterministically;
- keep AI text from claiming that a visual result is accurate, safe, or authentic without evidence.

Do not send raw frames to a model merely because a summary is inconvenient. If raw media is required, document the retention and privacy path separately.

## Route I: fallback and teardown

Every route needs a fallback decision:

| Failure | Fallback |
| --- | --- |
| No Metal device or unsupported feature | Native SwiftUI/Core Image or static result, if the task permits it. |
| Shader compile or argument failure | Native material, unfiltered preview, or an explanatory unavailable state. |
| Core Image render failure | Original source, lower-quality render, or retry with a bounded error. |
| Pixel format/plane mismatch | Convert through a declared supported format or reject the frame. |
| GPU backlog | Keep latest, drop safely, lower quality, or pause. |
| Thermal/memory pressure | Reduce work, release caches, retain source, and explain the mode. |
| Codec/session failure | Preserve source and offer a higher-level export route. |
| AI unavailable | Keep deterministic manual controls. |

On teardown, stop capture consumers, cancel tasks, stop display/delegate work, clear callbacks, release or invalidate sessions, and ensure late GPU/media callbacks cannot mutate a replaced SwiftUI model.

## Proof handoff

Do not call the route complete after a preview renders. Hand off a packet containing:

- target, deployment, SDK, and device capability checks;
- privacy strings and source retention policy;
- source format, color, orientation, and timestamp evidence;
- renderer and pipeline configuration;
- buffer, texture, command, and session ownership;
- dropped-frame/backpressure/thermal policy;
- accessibility and fallback behavior;
- local AI availability, schema, stale-result policy, and review;
- physical-device performance evidence;
- archive, signing, and release-build evidence.

## Sources

- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Canvas](https://developer.apple.com/documentation/swiftui/canvas)
- [GraphicsContext](https://developer.apple.com/documentation/swiftui/graphicscontext)
- [Shader](https://developer.apple.com/documentation/swiftui/shader)
- [Graphics and rendering modifiers](https://developer.apple.com/documentation/swiftui/view-graphics-and-rendering)
- [Core Image](https://developer.apple.com/documentation/coreimage)
- [CIImage](https://developer.apple.com/documentation/coreimage/ciimage)
- [CIContext](https://developer.apple.com/documentation/coreimage/cicontext)
- [CIFilter](https://developer.apple.com/documentation/coreimage/cifilter-swift.class)
- [Core Video](https://developer.apple.com/documentation/corevideo)
- [CVPixelBuffer](https://developer.apple.com/documentation/corevideo/cvpixelbuffer)
- [CVPixelBufferPool](https://developer.apple.com/documentation/corevideo/cvpixelbufferpool)
- [CVMetalTextureCache](https://developer.apple.com/documentation/corevideo/cvmetaltexturecache)
- [CVMetalTexture](https://developer.apple.com/documentation/corevideo/cvmetaltexture)
- [Metal](https://developer.apple.com/documentation/metal)
- [MTLDevice](https://developer.apple.com/documentation/metal/mtldevice)
- [MTLCommandQueue](https://developer.apple.com/documentation/metal/mtlcommandqueue)
- [MTLCommandBuffer](https://developer.apple.com/documentation/metal/mtlcommandbuffer)
- [MTLRenderPipelineState](https://developer.apple.com/documentation/metal/mtlrenderpipelinestate)
- [MTLComputePipelineState](https://developer.apple.com/documentation/metal/mtlcomputepipelinestate)
- [Setting up a command structure](https://developer.apple.com/documentation/metal/gpu_devices_and_work_submission/setting_up_a_command_structure)
- [Performing calculations on a GPU](https://developer.apple.com/documentation/metal/performing-calculations-on-a-gpu)
- [Metal feature sets](https://developer.apple.com/metal/feature-sets/)
- [Metal capabilities](https://developer.apple.com/metal/capabilities/)
- [Metal shader validation](https://developer.apple.com/documentation/xcode/validating-your-apps-metal-shader-usage)
- [MetalKit](https://developer.apple.com/documentation/metalkit)
- [MTKView](https://developer.apple.com/documentation/metalkit/mtkview)
- [MTKViewDelegate](https://developer.apple.com/documentation/metalkit/mtkviewdelegate)
- [VideoToolbox](https://developer.apple.com/documentation/videotoolbox)
- [VideoToolbox compression session APIs](https://developer.apple.com/documentation/videotoolbox/vtcompressionsession-api-collection)
- [VideoToolbox decompression session APIs](https://developer.apple.com/documentation/videotoolbox/vtdecompressionsession-api-collection)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)

## Related routes

- [SwiftUI Metal/Core Image/VideoToolbox GPU-media design](../21-design-deep-dives/126-swiftui-metal-coreimage-videotoolbox-gpu-media-review-design.md)
- [SwiftUI Metal/Core Image/VideoToolbox GPU-media review](../42-framework-deep-dives/98-swiftui-metal-coreimage-videotoolbox-gpu-media-review.md)
- [SwiftUI Metal/Core Image/VideoToolbox GPU-media proof matrix](../60-verification/123-swiftui-metal-coreimage-videotoolbox-gpu-media-review-proof-matrix.md)
- [SwiftUI Metal/Core Image/VideoToolbox GPU-media recipes](../70-code-recipes/141-swiftui-metal-coreimage-videotoolbox-gpu-media-review-recipes.md)
