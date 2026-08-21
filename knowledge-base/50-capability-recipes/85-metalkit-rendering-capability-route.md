# MetalKit rendering capability route

Use this route when an app needs a custom Metal-rendered visual or a
Model-I/O-to-Metal asset path. It turns the requirement into a target-aware
rendering slice while keeping SwiftUI state, source assets, GPU resources,
AI proposals, and proof separate.

## Route decision

| Desired outcome | First route | Add MetalKit when | Minimum fallback |
| --- | --- | --- | --- |
| Simple custom vector/animation | SwiftUI `Shape`, `Canvas`, or `TimelineView` | A measured GPU workload or shader effect exceeds the simpler route | Static/semantic representation |
| Still-image effect | Core Image or image rendering | A custom Metal pipeline or live frame path is required | Original image and deterministic filter |
| 2D game | SpriteKit | Direct GPU control is a product requirement | Reduced-detail SpriteKit scene or static state |
| Interactive 3D asset | RealityKit/Model3D | The app owns a custom mesh/material/frame graph | 2D asset inspector or prepared preview |
| GPU compute/preprocessing | Metal compute/Core ML | The exact workload needs direct command/resource control | CPU/Core ML route if it meets the quality budget |
| Native Apple-like screen | SwiftUI/Liquid Glass | Only the visual region needs a custom renderer | Native controls and readable data view |

Do not use `MTKView` merely because it is available. Record the measurable
reason: shader capability, frame cadence, custom mesh, GPU compute, or another
requirement that the selected higher-level route cannot meet.

## Step 1: write the render contract

Record:

~~~text
user outcome:
visual source and ownership:
target platforms/device families:
minimum OS/deployment target and SDK:
rendering route and why simpler routes are insufficient:
drawable size/scale/color/depth/sample policy:
maximum in-flight frames and memory budget:
shader/library/resource inputs:
asset/import formats and provenance:
AI proposal fields, if any:
accessibility and non-rendered equivalent:
fallback and reduced-quality states:
evidence required:
~~~

This contract prevents a renderer from quietly becoming a second source of
truth or a feature that only works on the developer’s newest device.

## Step 2: map the target graph

For a SwiftUI iOS app, the usual graph is:

~~~text
Main app target
  -> SwiftUI shell and state owner
  -> UIViewRepresentable bridge
  -> MTKView / renderer module
  -> .metal shaders and visual resources
  -> optional Model I/O / texture assets
  -> unit/fixture/performance tests
~~~

If the renderer is shared, put pure render descriptions and asset metadata in a
module that does not import `MTKView` or hold a `MTLDevice`. Keep GPU resources
in the target-specific renderer. Check target membership for shader files,
asset catalogs, model files, and any package resources.

## Step 3: choose the MetalKit seam

| Seam | Record |
| --- | --- |
| `MTKView` | `MTLDevice`, drawable size, color/depth/stencil formats, sample count, pause/invalidation mode |
| `MTKViewDelegate` | draw cadence, resize handling, renderer ownership, and error/report path |
| `MTKTextureLoader` | URL/data scope, format/size limits, color/alpha policy, mip options, cancellation |
| `MTKMeshBufferAllocator` | Model I/O source, vertex descriptor, topology, memory/copy policy |
| `MTKMesh`/`MTKSubmesh` | mesh identity, index/vertex buffers, materials, shader attribute mapping |
| Metal queue/pipeline | queue owner, command order, resource lifetime, completion/error handling |
| SwiftUI bridge | create/update/dismantle behavior, state projection, semantic overlay, fallback |

Treat each seam as independently testable. A mesh-loading test does not prove
that the view presents it; a view screenshot does not prove correct asset
provenance or frame performance.

## Step 4: define the asset route

For a Model I/O asset:

1. Validate the user/app-owned URL, allowed type, scope, size, and integrity.
2. Load an `MDLAsset` with the selected vertex descriptor and
   `MTKMeshBufferAllocator` when the Metal layout is known.
3. Inspect hierarchy, mesh/submesh count, vertex attributes, materials,
   textures, animation/time samples, bounds, units, and coordinate policy.
4. Build the `MTKMesh` representation and validate its buffers/descriptors
   against the Metal pipeline.
5. Cache by source URL/revision and device/render profile, not by a global
   pointer or file name alone.
6. Show progress/cancellation and keep the last accepted render result if a
   replacement fails.

For a texture, validate file scope and decode constraints before calling
`MTKTextureLoader`. Do not retain a security-scoped URL or raw user file beyond
the documented need. Keep source image metadata outside the GPU texture.

## Step 5: define the view lifecycle

Use this state machine:

~~~text
unavailable(reason)
  -> checking device
  -> loading source
  -> preparing GPU resources
  -> ready
  -> rendering
  -> paused / offscreen / reduced quality
  -> failed(retryable or manual fallback)
  -> dismantled
~~~

The view’s `update` method reconciles state. It should not create a new device,
queue, shader library, mesh, or texture for every SwiftUI body update. Decide
who owns the renderer and how it is reset when the source revision or render
profile changes.

## Step 6: add native controls and AI review

Keep actions typed and explicit:

~~~text
import/choose -> validate -> render preview
adjust        -> typed profile -> validate -> render
AI suggest    -> typed proposal -> review/edit -> accept -> render revision
reset/delete  -> confirmation -> derived-resource cleanup -> observable result
~~~

AI may propose `RenderProfile`, `MaterialChoice`, `CameraFraming`, or
`AssetClassification`. Each proposal includes source IDs, source revision,
model route/version, bounds, confidence/context, and an explicit review state.
The renderer accepts only validated values. If the model is unavailable, use
manual controls or the last accepted profile.

## Step 7: define proof before implementation

Map each claim to a level:

| Claim | Evidence |
| --- | --- |
| API route is appropriate | Official docs and target availability review |
| Asset imports | Deterministic supported/malformed/oversized fixtures |
| Renderer state works | Unit/fixture state tests plus SwiftUI preview/simulator |
| View displays correctly | Named target compile and simulator/device visual run |
| Performance meets budget | Physical-device Release run with declared workload and metrics |
| Accessibility task works | Physical task matrix with VoiceOver, Dynamic Type, reduced effects, alternate input |
| AI proposal is safe | Typed output, validator, review, stale revision, undo, and fallback fixtures |
| Release is ready | Archive target/resource inspection, signed install, TestFlight/release evidence |

Never promote “preview loaded” into “GPU feature works on supported iPhones.”

## Stop conditions

Stop and re-scope if:

- the product cannot state why SwiftUI/Canvas/Core Image/SpriteKit/RealityKit
  is insufficient;
- a renderer owns domain truth or protected side effects;
- shader/resource files are not target-owned and archive-verified;
- the asset route has no malformed/oversized/cancelled fallback;
- essential UI exists only as pixels with no semantic alternative;
- the AI output is executed without typed validation and user/policy review;
- performance is claimed without a named device, workload, build, and metric;
- a simulator screenshot is being used as physical GPU or thermal evidence.

## Sources

- [MetalKit](https://developer.apple.com/documentation/metalkit/)
- [MTKView](https://developer.apple.com/documentation/metalkit/mtkview/)
- [MTKViewDelegate](https://developer.apple.com/documentation/metalkit/mtkviewdelegate/)
- [MTKTextureLoader](https://developer.apple.com/documentation/metalkit/mtktextureloader/)
- [MTKMesh](https://developer.apple.com/documentation/metalkit/mtkmesh/)
- [MTKMeshBufferAllocator](https://developer.apple.com/documentation/metalkit/mtkmeshbufferallocator/)
- [MTKSubmesh](https://developer.apple.com/documentation/metalkit/mtksubmesh/)
- [Model I/O](https://developer.apple.com/documentation/modelio/)
- [MDLAsset](https://developer.apple.com/documentation/modelio/mdlasset/)
- [MDLMesh](https://developer.apple.com/documentation/modelio/mdlmesh/)
- [Metal](https://developer.apple.com/documentation/metal/)
- [MTLDevice](https://developer.apple.com/documentation/metal/mtldevice/)
- [MTLCommandQueue](https://developer.apple.com/documentation/metal/mtlcommandqueue/)
- [UIViewRepresentable](https://developer.apple.com/documentation/swiftui/uiviewrepresentable/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
