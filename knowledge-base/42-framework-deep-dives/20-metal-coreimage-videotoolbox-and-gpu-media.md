# Metal, Core Image, VideoToolbox, and GPU media architecture

## Choose the layer by a measurable requirement

Apple’s graphics and media stack is layered. Start with the highest-level route that satisfies the product requirement and only descend when a measurable limitation or required effect justifies the extra ownership:

| Need | Preferred route | What it owns |
| --- | --- | --- |
| Native screen composition and simple animation | SwiftUI, Canvas, Shape, system effects | Layout, semantics, accessibility, and interaction |
| Image/video filter graph | Core Image | Lazy CIImage graph, CIFilter processing, color-managed render contexts |
| Standard playback/capture/export | AVFoundation/AVKit | Media assets, capture, playback, reader/writer, export, audio/video lifecycle |
| Low-level codec control | VideoToolbox | Compression/decompression sessions, frame callbacks, codec properties |
| Custom GPU render or compute | Metal | Devices, queues, command buffers/encoders, resources, shaders, pipelines |
| GPU-accelerated image processing | Core Image backed by Metal | Image graph plus a reusable GPU context |
| Trained model inference | Core ML or an Apple model framework | Model lifecycle, inputs/outputs, compute-unit choice, version/evaluation |

Do not use Metal because it sounds more powerful. Custom GPU ownership adds resource, synchronization, shader, pipeline, frame-pacing, memory, thermal, and device-support responsibilities.

## The render and media authority chain

Keep these layers separate:

~~~text
user intent
  -> source asset/frame
  -> validated pixel format/color space/timestamp
  -> effect or compute graph
  -> GPU/codec work
  -> output frame/file
  -> review
  -> persistence/export/share/system surface
~~~

A CIImage is a recipe-like image graph until a CIContext renders it. A Metal command buffer is submitted work until completion and error state are observed. A VideoToolbox encode callback is a compressed sample result, not a playable file until a container/muxing route completes. A Core ML output is a model result, not domain truth.

Record enough provenance to reproduce the output:

- source asset/frame identifier and revision;
- dimensions, pixel format, color space, transfer function, and orientation;
- presentation timestamp/duration;
- effect graph/shader/pipeline version;
- device/GPU family and SDK;
- model/version/context if AI was used;
- output format/container and export settings;
- cancellation/error/thermal state;
- user review and commit decision.

## Metal device and resource boundaries

An MTLDevice represents a GPU and creates the queues, libraries, pipeline states, resources, and synchronization primitives used by a Metal app. Resources and command objects must be used with the same device. Pipeline states can be expensive to create, so cache/reuse them rather than compiling them in a frame loop.

The classic Metal route generally follows:

~~~text
MTLCreateSystemDefaultDevice
  -> MTLCommandQueue
  -> MTLCommandBuffer
  -> render/compute encoder
  -> buffers/textures/samplers
  -> commit
  -> completion/error
~~~

Metal 4 adds a newer command model on supported OS/GPU combinations, including MTL4CommandQueue creation from MTLDevice, command allocation/submission, argument tables, residency, and other resource/synchronization mechanisms. Do not assume Metal 4 is available because the SDK exposes a symbol. Use availability checks and device feature-set evidence.

Choose the route in the target:

| Target fact | Product response |
| --- | --- |
| Metal 4 supported and worth the complexity | Use the Metal 4 path behind an explicit capability adapter |
| Classic Metal supported | Use MTLCommandQueue/MTLCommandBuffer route |
| GPU feature unavailable | Use Core Image/AVFoundation/CPU fallback or reduce effect |
| Resource budget too high | Downsample, reduce frame rate/quality, or defer processing |
| Thermal pressure | Pause/degrade background work and preserve a resumable job |

Do not put business truth, purchases, identity, file writes, or network authority inside a draw or compute callback.

## Shader and pipeline lifecycle

Treat shader code as a versioned product resource:

1. Validate the shader source and target language/features.
2. Load the appropriate library or binary archive.
3. Resolve functions and create render/compute pipeline states.
4. Validate resource bindings, formats, threadgroup sizes, and argument layouts.
5. Warm or prepare expensive pipeline work outside the interactive frame path where possible.
6. Reuse pipelines and resources.
7. Track errors and unsupported feature fallback.
8. Run shader validation in development/debug workflows.

Shader Validation can catch runtime GPU errors such as non-resident resources, out-of-bounds accesses, null resources, incorrect texture bindings, and undefined behavior. It adds instrumentation and can slow compilation/runtime, so treat validation evidence separately from production performance evidence.

Keep shaders deterministic where possible. A visual glitch caused by a resource race can be mistaken for a bad AI result or a user input problem; log a redacted pipeline/resource identity and capture GPU evidence instead of dumping sensitive media.

## Core Image: lazy graphs and color-managed rendering

Core Image represents processing as CIImage graphs composed of CIFilter, CIKernel, CIColor, and related types. The graph is not necessarily evaluated when an intermediate CIImage is created. Rendering occurs through a CIContext or a supported destination.

### Context ownership

CIContext holds internal state such as Metal command queues and caches. Create a small, deliberate number of contexts—often one per view or background task—and reuse them. CIContext and CIImage are immutable and can be used across threads; CIFilter instances are mutable and should not be shared concurrently without isolation.

### Color and extent

Specify color-space and working-format policy for a product that cares about HDR, wide color, or exact export. Validate:

- input and destination color space;
- premultiplied alpha;
- image extent and crop;
- orientation;
- pixel format;
- output color space/format;
- metadata that must be preserved or intentionally removed.

Do not call an image “exported” because a CIImage exists. Force the intended render and validate the resulting bytes/file.

### Live frame path

For live camera/video processing:

~~~text
capture sample buffer
  -> bounded queue/backpressure
  -> CIImage/format validation
  -> filter graph
  -> CIContext render to pixel buffer/texture
  -> display/encoder
~~~

Use a bounded queue. If the consumer is slower than capture, drop or coalesce frames according to the product’s visual requirement rather than growing memory without bound.

## VideoToolbox: sessions, frames, and containers

VideoToolbox compression/decompression sessions own codec work at the frame level. A compression route typically:

1. Creates the session with width, height, codec, attributes, and output callback/handler.
2. Sets compression properties deliberately.
3. Presents frames with correct pixel buffers, timestamps, durations, and frame properties.
4. Handles output callbacks and status flags.
5. Completes pending frames when the input ends or a segment boundary is reached.
6. Invalidates the session and releases resources.

VideoToolbox does not by itself define the app’s final container, file metadata, audio synchronization, or share format. Use AVAssetWriter/AVFoundation or another explicitly tested muxing path for a playable/exported file.

For decompression, handle format descriptions, output buffers, reorder/delivery timing, flush/invalidation, and a fallback when the requested codec/feature is not available.

Hardware acceleration and codec behavior vary by device, OS, input format, and thermal state. Do not promise “hardware encoded” or a fixed frame rate without named device evidence.

## GPU, media, and on-device AI

Use the following route selector:

| AI/media task | Route | Boundary |
| --- | --- | --- |
| Classify or detect selected frames | Vision/Core ML with bounded capture | Model availability and output quality are separate from GPU rendering |
| Generate a caption/summary from selected media | Foundation Models after deterministic extraction | Preserve source/provenance and review; model cannot export/share |
| Apply a deterministic visual effect | Core Image or Metal shader | Effect output still needs color/format/output validation |
| Run tensor/GPU compute | Core ML/Metal route chosen from measured need | Device feature support, memory, thermal, and fallback |
| Encode a user-started video | AVFoundation or VideoToolbox | Codec/frame/container/audio/permission/release evidence |

AI should not change pixel dimensions, color space, timestamps, or shader parameters without deterministic validation. A generated effect preset is a proposal; apply it only after the user reviews the result or explicitly chooses a known preset.

Keep the model route and visual route decoupled:

~~~text
pixel/frame source
  -> deterministic normalize
  -> optional GPU/media processing
  -> optional model inference
  -> typed proposal/observation
  -> review
  -> deterministic export/share/save
~~~

## SwiftUI, Liquid Glass, and custom visual effects

Use SwiftUI’s native components and system-first Liquid Glass for ordinary app chrome. Use Core Image/Metal for the content itself only when the product needs a real effect:

- a live preview surface;
- a deterministic background/texture effect;
- a custom visualization;
- an export transform;
- a GPU-accelerated media operation.

Do not use a custom blur or shader to imitate a system control that SwiftUI already renders correctly. Put high-cost effects behind an explicit state and provide:

- reduced-transparency fallback;
- reduced-motion fallback;
- static preview;
- lower-quality/low-power route;
- accessible status text;
- cancellation and recovery.

Keep a glass toolbar from obscuring video detail or hiding frame drops. A material can group controls; it cannot compensate for an unstable render pipeline.

## Performance and thermal ownership

For every GPU/media route, establish a budget:

- maximum input dimensions and frame rate;
- queue depth and dropped-frame policy;
- CPU/GPU frame-time target;
- memory/pool size;
- export duration and cancellation behavior;
- shader/pipeline warm-up;
- thermal/low-power response;
- oldest supported GPU/device.

Measure with Xcode GPU captures, Instruments, signposts, XCTest performance metrics, and physical-device release builds. Debug validation can change performance and must not be compared directly to production numbers.

If the device enters a degraded state:

1. stop accepting more work;
2. reduce quality or frame rate;
3. preserve the user’s source and progress;
4. expose the degraded state;
5. allow resume/retry;
6. avoid silently changing the export contract.

## Verification stop list

- Named target, deployment target, SDK, device/GPU family, and feature-set checks.
- Classic Metal and Metal 4 availability paths where applicable.
- Shader library/pipeline load, argument/resource binding, validation, fallback, and release artifact.
- Core Image context reuse, filter isolation, color management, extent, pixel format, and export validation.
- Live frame backpressure, queue depth, dropped-frame policy, and camera/media interruption.
- VideoToolbox compression/decompression callbacks, timestamps, completion, invalidation, codec/container integration, and cancellation.
- Core ML/Foundation Models input/output provenance and no-hidden-side-effect review.
- Liquid Glass/readability with light/dark, reduced transparency, Dynamic Type, VoiceOver, Reduce Motion, and low-power states.
- GPU frame time, memory, thermal, battery, and oldest-device evidence.

## Sources

- [Metal](https://developer.apple.com/documentation/metal)
- [MTLDevice](https://developer.apple.com/documentation/metal/mtldevice)
- [Understanding the Metal 4 core API](https://developer.apple.com/documentation/metal/understanding-the-metal-4-core-api)
- [MTLCommandQueue](https://developer.apple.com/documentation/metal/mtlcommandqueue)
- [MTLCommandBuffer](https://developer.apple.com/documentation/metal/mtlcommandbuffer)
- [MTLRenderPipelineState](https://developer.apple.com/documentation/metal/mtlrenderpipelinestate)
- [MTLComputePipelineState](https://developer.apple.com/documentation/metal/mtlcomputepipelinestate)
- [Metal feature set tables](https://developer.apple.com/metal/Metal-Feature-Set-Tables.pdf)
- [Validating your app’s Metal shader usage](https://developer.apple.com/documentation/xcode/validating-your-apps-metal-shader-usage)
- [Core Image](https://developer.apple.com/documentation/coreimage)
- [CIContext](https://developer.apple.com/documentation/coreimage/cicontext)
- [CIImage](https://developer.apple.com/documentation/coreimage/ciimage)
- [Processing an Image Using Built-in Filters](https://developer.apple.com/documentation/coreimage/processing-an-image-using-built-in-filters)
- [VideoToolbox](https://developer.apple.com/documentation/videotoolbox)
- [VTCompressionSession](https://developer.apple.com/documentation/videotoolbox/vtcompressionsession-api-collection)
- [VTDecompressionSession](https://developer.apple.com/documentation/videotoolbox/vtdecompressionsession-api-collection)
- [AVFoundation](https://developer.apple.com/documentation/avfoundation/)
- [AVAssetWriter](https://developer.apple.com/documentation/avfoundation/avassetwriter)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Motion](https://developer.apple.com/design/human-interface-guidelines/motion/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
