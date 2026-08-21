# GPU, Core Image, VideoToolbox, and media rendering route

## Use this route when

Use this route when a feature needs real-time visual effects, GPU compute, image/video processing, codec control, or a custom renderer inside a native SwiftUI/Liquid Glass app.

## Route selector

| Outcome | Start with | Descend when |
| --- | --- | --- |
| Native app chrome/effect | SwiftUI/Canvas/system effect | The required effect cannot be expressed or performs poorly |
| Still-image filter | Core Image | A custom kernel or measured GPU path is needed |
| Live camera/video effect | Core Image + AVFoundation | Custom Metal processing or synchronization is required |
| Standard export/transcode | AVAssetExportSession/AVAssetReaderWriter | Direct codec properties or low-level frame control matter |
| Low-level encode/decode | VideoToolbox | The product owns timestamps/pixel buffers/codec sessions |
| Custom render/compute | Metal classic route | Metal 4 is supported and its command/resource model is justified |
| Model inference | Core ML/Foundation Models | A measured custom tensor/GPU kernel is required |

## Pipeline contract

~~~text
source
  -> normalized frame/image metadata
  -> bounded queue
  -> effect/compute/codec
  -> output frame or sample
  -> review/preview
  -> deterministic save/export/share
~~~

Every stage needs a typed state and cancellation behavior. Keep the rendering pipeline independent from the domain record and the system handoff.

## Route A: Core Image effect

1. Create/reuse one CIContext for the view or background task.
2. Build a CIImage from the selected image or sample buffer.
3. Create per-operation CIFilter instances.
4. Apply filters as a lazy graph.
5. Set working/output color-space policy.
6. Render to the required destination.
7. Validate extent, pixel format, orientation, metadata, and output bytes.
8. Present a review or export the result.

Use Core Image before Metal for a standard filter graph. Do not create a new context or share a mutable filter for every frame.

## Route B: live Core Image/AVFoundation path

1. Configure capture/playback in AVFoundation.
2. Establish pixel format, dimensions, orientation, color space, and timestamps.
3. Enqueue samples into a bounded processing path.
4. Drop/coalesce frames when the consumer is behind according to the product contract.
5. Render the CIImage to a CVPixelBuffer or Metal texture.
6. Display or send the result to an encoder.
7. Stop/release capture and processing when the view disappears or is cancelled.

The preview route and export route may use different quality policies. Do not let a preview queue silently become an unbounded export buffer.

## Route C: Metal classic

Use Metal when the feature needs custom render/compute control:

1. Select and validate an MTLDevice.
2. Create/reuse an MTLCommandQueue.
3. Load shader functions/library.
4. Create/reuse render/compute pipeline states.
5. Allocate buffers/textures from the same device.
6. Encode work with explicit resource bindings and synchronization.
7. Commit command buffers.
8. Observe completion/error and recycle resources.

Keep the renderer behind a capability adapter so the SwiftUI model can offer Core Image or CPU fallback without knowing Metal details.

## Route D: Metal 4

Metal 4 introduces a different command/resource model on supported targets. Choose it only after checking:

- deployment/SDK availability;
- MTLDevice.makeMTL4CommandQueue support;
- GPU feature-set tables;
- shader/resource/pipeline requirements;
- measured benefit compared with the classic route;
- debug/profiling tool support;
- fallback for devices without the path.

Do not share assumptions between MTLCommandQueue and MTL4CommandQueue. Keep a protocol or adapter boundary and test resource ownership, command allocation, submission, synchronization, and completion separately.

## Route E: VideoToolbox

Use VideoToolbox for frame-level compression/decompression:

~~~text
format description
  -> VTCompressionSession / VTDecompressionSession
  -> properties
  -> timestamped pixel buffers
  -> callbacks/output handler
  -> complete/flush
  -> invalidate
  -> container/export
~~~

Define codec, width/height, pixel format, bitrate/quality, keyframe policy, timestamps, duration, output callback, pending-frame completion, and teardown. Use AVAssetWriter or another tested container path for a playable file.

Treat hardware codec availability as a device/input fact. A session creation success does not prove the requested profile, frame rate, or thermal duration.

## Route F: on-device AI and GPU

Use a deterministic media adapter before the model:

~~~text
capture/import
  -> crop/orient/normalize
  -> Core Image/Metal preprocessing
  -> Vision/Core ML/Foundation Models
  -> typed observation/proposal
  -> human review
  -> save/export/share
~~~

AI can suggest a filter, classify a selected frame, produce a caption, or summarize an export. It cannot silently change timestamps, color profiles, source files, codec settings, or share destinations.

Store:

- source/frame ID;
- preprocessing route/version;
- model/context/version;
- output/proposal;
- user edit/decision;
- final render/export settings.

## Route G: SwiftUI/Liquid Glass shell

Keep custom GPU content inside a focused surface. Let SwiftUI own:

- navigation;
- source selection;
- playback/capture controls;
- effect presets;
- status/error/recovery;
- review;
- export/share;
- accessibility and settings.

Use functional glass groups around these controls. Provide static or reduced-quality fallback when the GPU route is unavailable or degraded.

## Failure matrix

| Failure | Preserve | Fallback |
| --- | --- | --- |
| No Metal/Metal 4 support | Source and effect intent | Core Image/CPU/lower-quality route |
| Shader/pipeline compile fails | Previous valid frame | Known preset/static preview |
| Resource binding/validation error | Source and diagnostics ID | Disable effect/reload pipeline |
| CI render fails | Input/provenance | Alternate format/context or retry |
| Queue backlog | Current frame/output | Drop/coalesce according to policy |
| Codec unavailable | Original media | AVFoundation alternate export |
| Encoder callback error | Pending source/partial output | Flush/cleanup/retry |
| Thermal pressure | Work checkpoint | Lower quality/pause/resume |
| Color conversion mismatch | Original/output metadata | Re-render with explicit color policy |
| AI proposal invalid | Original effect/settings | Manual preset/control |
| Export/share cancelled | Reviewed output | Keep local draft; no claim of share |

## Verification questions

- Which device/GPU family and workload does this route target?
- Is Core Image sufficient before choosing Metal?
- Is Metal 4 actually supported and materially useful?
- Are resources/pipelines reused and owned by one device?
- What is the queue/backpressure policy?
- Which timestamps/color spaces/pixel formats are authoritative?
- Is VideoToolbox output wrapped into a tested container?
- Can a user cancel without losing the source?
- Does AI modify only an editable proposal?
- Does reduced transparency/motion and VoiceOver still communicate state?
- What was proven in a preview, simulator, signed device, and release build?

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
- [VideoToolbox](https://developer.apple.com/documentation/videotoolbox)
- [VTCompressionSession](https://developer.apple.com/documentation/videotoolbox/vtcompressionsession-api-collection)
- [VTDecompressionSession](https://developer.apple.com/documentation/videotoolbox/vtdecompressionsession-api-collection)
- [AVFoundation](https://developer.apple.com/documentation/avfoundation/)
- [AVAssetWriter](https://developer.apple.com/documentation/avfoundation/avassetwriter)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
