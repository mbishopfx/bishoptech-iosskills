# SwiftUI Metal, Core Image, and VideoToolbox GPU-media review proof matrix

This matrix separates documentation, compile, preview, simulator, signed physical-device, performance, system, and release evidence for a SwiftUI GPU/media route. It is the acceptance boundary for the [GPU-media deep dive](../42-framework-deep-dives/98-swiftui-metal-coreimage-videotoolbox-gpu-media-review.md), [design companion](../21-design-deep-dives/126-swiftui-metal-coreimage-videotoolbox-gpu-media-review-design.md), [capability route](../50-capability-recipes/129-swiftui-metal-coreimage-videotoolbox-gpu-media-review-route.md), and [compile-oriented recipes](../70-code-recipes/141-swiftui-metal-coreimage-videotoolbox-gpu-media-review-recipes.md).

## Evidence levels

| Level | Evidence | Can support | Cannot support |
| --- | --- | --- | --- |
| L0 | Official source and target review | API meaning, platform availability, privacy/configuration questions | Runtime rendering, frame timing, hardware behavior, release delivery |
| L1 | Named-target compile and tests | Imports, signatures, availability branches, model/state contracts, basic resource setup | Physical camera behavior, GPU performance, codec output, accessibility completion |
| L2 | Preview or deterministic fixture | SwiftUI hierarchy, copy, loading/recovery, review, fallback, semantic overlays | Live pixels, real frame lifetime, Metal feature support, hardware thermal behavior |
| L3 | Simulator or recorded fixture | Deterministic media state, static renderer, user flow, export UI, accessibility structure | Camera throughput, physical device GPU/codec behavior, real thermal pressure |
| L4 | Signed physical-device run | Camera/media permission, pixel pipeline, GPU completion, frame pacing, accessibility/input, thermal behavior | Every device family, App Store release, universal safety or quality |
| L5 | Archive, TestFlight, release/system run | Signing, entitlements, privacy strings, target metadata, release-build behavior | Universal runtime truth, all source formats, all devices, physical-world claims |

Never promote an L0-L3 result to physical-device language. Never promote one L4 device run to a universal device or performance claim without the measured device matrix that supports it.

## Core acceptance matrix

| Claim | Minimum proof | Capture | Fails if |
| --- | --- | --- | --- |
| Native SwiftUI is sufficient | L1/L2 | Requirement and fallback comparison | A custom GPU route is added without a measured need. |
| Canvas drawing is correct | L1/L2/L4 as target requires | Input data, scale, orientation, output, state copy | A Canvas preview is called a live camera or pixel pipeline. |
| Canvas content is accessible | L2/L4 | VoiceOver labels/actions, list or semantic overlay | Individual drawn marks are assumed to be independently accessible. |
| SwiftUI Shader applies the intended effect | L1/L2/L4 | Function identity, bounded arguments, coordinate/color assumptions | An arbitrary model-selected function or unbounded parameter is accepted. |
| Shader fallback works | L2/L4 | Unsupported/compile-failure/accessibility modes | The view becomes blank or loses its semantic controls. |
| Core Image filter graph is valid | L1/L2 | Source, filter names, parameters, extent, color policy | CIImage existence is treated as rendered output. |
| CIContext is reused safely | L1/L4 | Context lifetime, queue/thread ownership, render completion | A context is created per frame or shared without an ownership policy. |
| CIFilter concurrency is safe | L1/L4 | Instance ownership and concurrent test | One mutable filter instance is mutated by concurrent work. |
| Preview and export color are intentional | L2/L4 | Source/output color space, pixel format, dynamic-range policy | A color-managed preview is assumed to equal export bytes. |
| CVPixelBuffer format is supported | L1/L4 | Pixel format, planes, dimensions, attachments, orientation | The first plane is treated as a complete image for every format. |
| CVPixelBuffer lifetime is safe | L1/L4 | Pool ownership, lock/unlock, completion release | A buffer is returned or reused before GPU/codec consumers finish. |
| CVMetalTextureCache conversion works | L1/L4 | Device/cache, plane, usage, texture lifetime, error | A texture is used after its source buffer/cache contract ends. |
| Metal device selection is valid | L1/L4 | Runtime device and feature checks | SDK availability is used as proof of target GPU support. |
| Metal command queue is reused | L1/L4 | Queue creation/lifetime and submit path | A queue is created for every frame. |
| Command buffers are bounded | L1/L4 | In-flight count, completion, backpressure, cancellation | Work grows without a bound or late completion mutates dead state. |
| Render/compute pipeline is valid | L1/L4 | Function, formats, resource bindings, validation output | A preview on one GPU is generalized to all targets. |
| MTKView frame pacing is usable | L4 | Device/OS, drawable settings, delegate lifecycle, duration | A static screenshot proves interactive frame pacing. |
| VideoToolbox compression works | L1/L4 | Codec/session properties, input timing, callbacks, output file | A session is torn down with pending frames or output is not independently checked. |
| VideoToolbox decompression works | L1/L4 | Format description, timing, output buffers, status | A decoded preview proves a valid full export. |
| Live backpressure is safe | L4 | Source rate, processed rate, dropped/latest policy, queue depth | The app silently accumulates frames or blocks capture indefinitely. |
| Thermal/memory fallback works | L4 | Duration, device, quality mode, memory/thermal signal, recovery | A short Debug run is called production performance evidence. |
| AI proposal is bounded | L1/L2/L4 | Typed input, model availability, allowlist, revision, review | Model text chooses a raw shader, function, codec, or side effect. |
| Liquid Glass remains functional | L2/L4 | Normal, bright/dark media, reduced transparency, contrast, Dynamic Type | Glass hides status or is the only state signal. |
| Privacy is accurate | L1/L4/L5 | Info.plist, pre-prompt, retention path, network/local path | GPU usage is treated as proof that media never leaves the device. |
| Release build is valid | L5 | Archive, signing, entitlements, privacy, TestFlight | Local compile or preview is called shipped. |

## Target and privacy packet

Record a target packet before implementation:

| Field | Evidence |
| --- | --- |
| App target | Xcode target, platform, and product name. |
| Deployment target | Minimum OS and selected SDK. |
| Renderer | SwiftUI, Canvas, Shader, Core Image, MetalKit, Metal, or VideoToolbox. |
| Hardware requirement | Runtime feature checks and any declared device family policy. |
| Source access | Camera, microphone, Photos, file, or media-library authorization. |
| Privacy strings | Exact usage descriptions and pre-prompt copy. |
| Retention | Whether frames, buffers, thumbnails, exports, logs, or caches persist. |
| AI path | On-device availability, input fields, cancellation, stale-result policy. |
| Network path | Whether any source or result leaves the device, and why. |
| Fallback | Native, lower-quality, still-image, manual, or unavailable route. |
| Release | Entitlements, signing, archive, TestFlight, and App Store metadata. |

Keep camera, microphone, Photos, local AI, cloud sync, and export destination as separate privacy decisions. A private GPU render can still be followed by an explicit export.

## Source and frame packet

For each tested source, record:

- source type and identifier;
- app source revision;
- frame timestamp and duration where relevant;
- width, height, orientation, mirroring, and crop;
- pixel format and plane count;
- color attachments, color space, transfer function, and range when relevant;
- dynamic-range policy;
- buffer owner and pool behavior;
- whether the frame is live, cached, dropped, or exported;
- renderer path and output destination;
- device model, OS, build configuration, and test duration.

Acceptance rules:

1. A timestamp is not used as the only freshness check.
2. Pixel format and plane layout are validated before conversion.
3. Source buffers stay alive until their consumers release them.
4. Preview and export have explicit color/format policies.
5. Dropped frames are recorded as a policy decision, not hidden as success.

## SwiftUI drawing and shader packet

Run the same semantic task with:

- native SwiftUI drawing;
- Canvas at the target sizes and Dynamic Type settings;
- the shader enabled;
- shader fallback or unavailable mode;
- reduced motion;
- increased contrast and reduced transparency;
- VoiceOver, keyboard, pointer, Voice Control, and Switch Control where supported;
- portrait/landscape and iPad size classes where supported.

Capture:

- source view hierarchy and semantic order;
- shader function and bounded arguments;
- output coordinate and color assumptions;
- before/after screenshots or recordings;
- text equivalents for visual state;
- failure behavior when the shader cannot compile or run;
- a named fallback route.

A visual screenshot cannot prove that the individual Canvas marks are accessible or that a shader effect is present in an exported media file.

## Core Image packet

For each filter graph, capture:

| Field | Required evidence |
| --- | --- |
| Source | CIImage origin and source revision. |
| Graph | App-owned filter sequence and bounded parameters. |
| Context | CIContext lifetime, device/backend choice, and ownership. |
| Filter instances | Whether each mutable CIFilter is isolated to its task. |
| Extent | Input/output extent and crop policy. |
| Color | Working/destination color spaces and output policy. |
| Destination | Preview texture, CGImage, CVPixelBuffer, or file path. |
| Completion | Render status and error handling. |
| Cancellation | What happens when the source or intent changes. |

Test an empty/invalid filter, a large image, an orientation change, a color-space change, and concurrent work. Verify that the original source remains available after a render failure.

## Metal and texture packet

For a Metal route, record:

- MTLDevice identity and runtime capability checks;
- queue count and lifetime;
- render/compute pipeline creation and function identity;
- resource formats/usages and storage modes;
- CVMetalTextureCache device and cache lifetime;
- source buffer pool and texture lifetime;
- command-buffer count in flight;
- completion/error status;
- drawable availability and present policy;
- cancellation and teardown behavior;
- shader validation output;
- device/OS/build configuration.

Test:

1. normal input;
2. unsupported or unexpected pixel format;
3. empty drawable or allocation failure;
4. GPU error or command failure;
5. source revision change while work is in flight;
6. view teardown while a command is pending;
7. sustained processing until thermal/memory behavior is observable.

An image on screen proves only that one submission reached one renderer. It does not prove correct buffer ownership, all device support, or export parity.

## VideoToolbox session packet

For compression, record:

- codec and profile;
- dimensions and pixel format;
- frame timing and duration;
- session properties;
- input buffer ownership;
- callback status and output timing;
- pending-frame completion;
- invalidation/release order;
- destination file/container route;
- independent playback or inspection result.

For decompression, also record:

- format description;
- requested output format;
- sample timing;
- output buffer ownership;
- status/error and cancellation;
- downstream preview/export route.

Test interruption, cancellation, malformed or unsupported input, end-of-stream, and teardown with pending work. A successful callback is not by itself proof that a playable file or correctly color-managed output was produced.

## Live frame and backpressure packet

Record the source cadence and the selected policy:

| Measurement | Evidence |
| --- | --- |
| Source cadence | Nominal and observed frames per second. |
| Processing cadence | Completed frames per second. |
| Queue depth | Maximum in-flight frames and tasks. |
| Drop policy | Latest-frame, bounded queue, pause, or lower quality. |
| Latency | Source-to-preview and source-to-export where relevant. |
| Memory | Peak and steady-state footprint. |
| Thermal | Device/OS state and duration. |
| Recovery | Quality restoration, retry, or user action. |

The UI should report a meaningful product state such as “Preview reduced” or “Waiting for the next frame,” not expose a raw semaphore or queue name.

## AI proposal packet

For every local proposal, retain:

| Field | Required |
| --- | --- |
| Source revision | Yes |
| Source metadata summary | Yes |
| User intent | Yes |
| Available effect allowlist | Yes |
| Model availability state | Yes |
| Proposal and bounded values | Yes |
| Stale-result policy | Yes |
| User edit/reject/apply action | Yes |
| Deterministic operation result | Yes/no with reason |

Test model unavailable, cancellation, source replacement, malformed proposal, out-of-range values, and rejection. The model must not be able to select arbitrary shader source, Metal functions, or codec identifiers.

## Accessibility and Liquid Glass packet

Run the feature with:

- VoiceOver;
- Dynamic Type at the largest relevant sizes;
- increased contrast;
- reduced transparency;
- Reduce Motion;
- keyboard/full keyboard access;
- pointer/hover where supported;
- Switch Control or an equivalent alternate-input route;
- longer localization and right-to-left layout where supported.

Verify that:

- source, output, processing state, freshness, and limitations are spoken;
- every important action has a semantic control;
- the task can be completed without precise visual comparison or gesture-only input;
- glass does not cover essential content;
- fallback surfaces retain hierarchy;
- motion reduction does not remove necessary feedback.

## Release packet

Before calling the route shippable, attach:

- selected target and deployment/SDK;
- supported device matrix and runtime checks;
- privacy strings and retention explanation;
- release configuration and shader validation;
- physical-device test logs and screenshots;
- performance/thermal/memory measurements;
- accessibility results;
- archive and signing result;
- TestFlight or release-build result;
- known limitations and explicit claims the evidence does not support.

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
- [Metal feature sets](https://developer.apple.com/metal/feature-sets/)
- [Metal capabilities](https://developer.apple.com/metal/capabilities/)
- [Metal shader validation](https://developer.apple.com/documentation/xcode/validating-your-apps-metal-shader-usage)
- [MetalKit](https://developer.apple.com/documentation/metalkit)
- [MTKView](https://developer.apple.com/documentation/metalkit/mtkview)
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
- [SwiftUI Metal/Core Image/VideoToolbox GPU-media route](../50-capability-recipes/129-swiftui-metal-coreimage-videotoolbox-gpu-media-review-route.md)
- [SwiftUI Metal/Core Image/VideoToolbox GPU-media recipes](../70-code-recipes/141-swiftui-metal-coreimage-videotoolbox-gpu-media-review-recipes.md)
