# GPU, Core Image, VideoToolbox, and media rendering proof matrix

This matrix separates graphics API availability, shader/pipeline correctness, image color/output correctness, live-frame behavior, codec/session behavior, AI proposals, accessibility, performance, and release evidence. A visual preview is not proof of GPU correctness or a valid exported file.

## Evidence levels

| Level | Evidence | What it proves |
| --- | --- | --- |
| L0 | Official API/feature-set and target review | The selected Metal, Core Image, VideoToolbox, AVFoundation, or AI route is understood |
| L1 | Deterministic pixel/frame/codec fixtures | Color/format/timestamp math, effect output, pipeline state, error handling, and proposal schemas |
| L2 | Preview/simulator/UI fixture | SwiftUI shell, Liquid Glass grouping, status/review states, accessibility labels, and fallback |
| L3 | Signed physical-device run | GPU/codec creation, camera/media route, frame timing, output, interruption, and target behavior |
| L4 | Device/GPU/workload matrix | Feature-set support, oldest device, sustained workload, thermal/battery, HDR/color, codec/profile, and memory |
| L5 | Release artifact | Shader/resources, capabilities, target membership, privacy/usage configuration, signing, supported devices, and export/share configuration |

## Metal device and feature support

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Metal device is usable | Named physical device, MTLDevice creation, feature check, queue creation, error path | Simulator or non-nil device does not prove workload performance |
| Metal 4 route is usable | SDK/deployment availability, makeMTL4CommandQueue, GPU feature-set check, command/resource run | Symbol availability does not prove every device supports Metal 4 |
| Pipeline is valid | Shader library, function, pipeline creation, resource layout, validation run | A compiled shader does not prove correct bindings at runtime |
| GPU work is correct | Deterministic images/buffers, command completion/error, GPU capture | A rendered screenshot can hide race/resource bugs |
| GPU work is performant | GPU/CPU frame time, hitches, memory, thermal, oldest-device run | Newest-device/debug numbers are not universal |
| Shader validation passes | Out-of-bounds/null/residency/binding fixtures with validation enabled | Validation instrumentation changes performance |

## Core Image

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Filter graph is correct | Known images, extent/crop/orientation, filter parameters, expected output | CIImage construction is lazy and not rendered output |
| Context is correctly owned | One/reused context policy, concurrent work, cache/memory test | Many contexts can waste resources; mutable filters need isolation |
| Color is preserved | sRGB/P3/HDR/alpha/pixel-format fixtures, explicit destination, output inspection | “Looks right” on one display is not color proof |
| Live processing keeps up | Capture workload, bounded queue, dropped-frame policy, memory/thermal | A still-image render does not prove real-time behavior |
| Export is valid | Reopen output, format/metadata/size/orientation, destination acceptance | A non-nil Data result is not a usable file |

## VideoToolbox and media

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Compression session works | Named codec/profile, dimensions/pixel format, timestamped frames, callback status | Session creation is not a playable file |
| Pending frames complete | End-of-input/completeFrames/flush, callback count, ordering | One callback does not prove all frames were drained |
| Decompression is correct | Format description, reordered frames, output buffers, flush/invalidate | A decoder fixture does not prove camera/media pipeline timing |
| Video output is valid | Container/muxer, audio sync, metadata, reopen/playback/share | VideoToolbox does not own the final container |
| Codec route is sustainable | Long workload, thermal, battery, memory, interruptions, cancellation | Short encode does not prove sustained export |

## On-device AI

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| AI labels selected media | Fixed input, preprocessing record, typed output, source ID, edit/reject | A model label is not verified truth |
| AI proposes effect settings | Before/after fixture, bounds/schema validation, user review/reset | Model output must not silently change original media |
| AI summarizes video/image | Selected source/ranges, context/model version, citations, privacy review | Summaries can expose private content |
| AI selects export settings | Explicit preview, format/quality explanation, confirmation | AI cannot authorize export/share or change timestamps |
| AI uses GPU preprocessing | Measured preprocessing, model input contract, device fallback | A GPU path is not automatically faster or more private |

## Design/accessibility

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Live visual surface is understandable | Preparing/live/degraded/paused/cancelled/error task test | A spinner or animation is not semantic status |
| Liquid Glass is legible | Light/dark, contrast, reduced transparency, Dynamic Type, bright/high-frequency media | Glass does not fix an unreadable source |
| Alternate input works | VoiceOver, Voice Control, keyboard/pointer, captions/text status | Haptics/color/animation cannot be sole feedback |
| Reduced effects are safe | Reduce Motion/transparency and low-power behavior | Removing motion must not remove state meaning |
| Export review is honest | Original/output comparison, format/quality/source, undo/retry | Export callback does not prove user saw the result |

## Release and artifact packet

~~~text
feature:
target/bundle/build:
sdk/deployment target:
device/os/gpu family:
metal classic or Metal 4:
feature-set/support checks:
shader/library/pipeline version:
resource/argument/residency policy:
core image context/color space:
video input/output format:
videotoolbox codec/profile/timestamps:
queue/backpressure/drop policy:
ai model/context/version:
source/provenance:
review/undo:
export/container/share:
memory/frame-time/thermal/battery:
accessibility settings:
privacy/retention:
target/resources/entitlements:
known failures:
claim supported:
claim not yet supported:
~~~

## Claim language

Use:

- “On the named device/GPU, the Metal pipeline rendered the deterministic fixture with shader validation enabled; production performance was measured separately without validation instrumentation.”
- “Core Image rendered the selected image into the declared color space and the exported file was reopened and checked for format, orientation, and metadata.”
- “The VideoToolbox encoder completed the declared frames and the AVFoundation container was reopened and played on the named target.”
- “The AI proposed an editable effect preset from the selected frame; the original remained unchanged until confirmation.”

Avoid:

- “Runs at 60 fps” without a named workload/device matrix.
- “Hardware accelerated” without feature/codec evidence.
- “Lossless” without output/container proof.
- “AI enhanced” without source, model, and review evidence.
- “Exported” because a callback fired before the file was reopened.

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
