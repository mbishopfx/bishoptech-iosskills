# MetalKit view, texture, and mesh bridge

MetalKit is the utility layer that makes a custom Metal renderer practical in
an app. It provides a view that manages a Metal drawable, a delegate cadence,
texture loading helpers, and Metal-facing mesh types that can share Model I/O
asset data with a GPU pipeline. It does not replace Metal’s device, command,
resource, shader, synchronization, or performance contracts.

Use this route when the product needs a custom GPU surface, image/texture
loading, or a Model I/O mesh rendered by Metal. Use SwiftUI `Canvas`, Core
Image, SpriteKit, RealityKit, or a higher-level view when those already meet
the measured requirement. A custom renderer should begin with a concrete
visual or performance need, not with the desire to make every screen “more
advanced.”

The useful composition is:

~~~text
SwiftUI state and native shell
  -> UIViewRepresentable boundary
  -> MTKView and MTKViewDelegate
  -> MTLDevice / MTLCommandQueue
  -> resources and render/compute pipelines
  -> drawable presentation
  -> semantic overlay, review state, and evidence
~~~

## What MetalKit owns

| Product need | MetalKit route | Keep in the neighboring layer |
| --- | --- | --- |
| Display a custom Metal surface | `MTKView` and `MTKViewDelegate` | SwiftUI navigation, state, accessibility, and lifecycle intent |
| Load a common image into a Metal texture | `MTKTextureLoader` | File scope, image provenance, color policy, memory budget, and cancellation |
| Load a Model I/O mesh for Metal | `MTKMesh`, `MTKMeshBufferAllocator`, `MTKSubmesh` | `MDLAsset` source validation, material policy, scene identity, and domain state |
| Convert vertex descriptors | MetalKit Model I/O conversion functions | Shader input contract and target GPU feature checks |
| Schedule GPU work | Metal `MTLCommandQueue`, command buffers, encoders, resources | Frame policy, synchronization, error recovery, thermal and power decisions |
| Present a product feature | SwiftUI/UIKit shell over the renderer | User task, semantic controls, Dynamic Type, VoiceOver, and reduced-effects fallback |

MetalKit helps allocate and connect rendering objects; it does not establish
that a file is safe, a shader is correct, a frame meets a performance target,
or a GPU feature exists on every iPhone. Keep those claims as separate state
and proof records.

## `MTKView` is a view lifecycle, not the render loop’s business model

`MTKView` is a specialized view that creates and displays Metal objects. It
uses a `CAMetalLayer` for drawable objects and requires a `MTLDevice`. Its
configuration includes drawable size, color/depth/stencil formats, sample
count, frame timing, and whether drawing is paused or invalidated. Choose the
drawing mode from the user outcome:

| Mode | Appropriate use | Risk to make explicit |
| --- | --- | --- |
| Timed updates | Continuous animation, games, live visualizations | Battery, thermal, frame pacing, and off-screen/background behavior |
| Draw-on-demand | Editors, static previews, state-driven graphics | Invalidation and stale-data ownership |
| Explicit draw calls | A tightly controlled render/export workflow | Caller must handle drawable availability and timing |

The view should not own the app’s canonical model. A renderer receives a
small, immutable frame description or render snapshot, turns it into GPU
resources, and reports only render status/metrics back to the feature owner.
Do not mutate purchases, contacts, health records, permissions, or network
authority from `draw(in:)`.

The view’s lifetime needs symmetric teardown:

~~~text
created
  -> device and pipeline ready
  -> drawing / paused / invalidated
  -> app inactive or surface hidden
  -> pause or reduce cadence
  -> release renderer resources
  -> view dismantled
~~~

SwiftUI may recreate or update a representable without changing the user’s
feature identity. Use a coordinator or a separate renderer owner when the
Metal objects must outlive one update call, and make `updateUIView` reconcile
state rather than rebuild the entire GPU graph on every body evaluation.

## Device, queue, drawable, and resource boundaries

The minimum MetalKit bridge still has several Metal responsibilities:

1. Obtain a `MTLDevice` and check the feature set/capabilities needed by the
   selected shader and resource formats.
2. Create a command queue and establish who owns command-buffer submission.
3. Create or load shader libraries and pipeline states before the first frame
   whenever possible.
4. Allocate buffers/textures with a deliberate storage mode and lifetime.
5. Acquire the current drawable/render-pass descriptor only when a frame will
   be submitted.
6. Encode work in a bounded order, commit the command buffer, and handle
   unavailable drawables, errors, and completion callbacks.
7. Limit in-flight frames and release resources when the surface or scene is
   no longer active.

`MTKView` can manage the drawable and render-pass setup, but it cannot decide
whether a frame’s resources are correct or whether a requested texture fits
the device budget. Keep a render configuration with explicit scale, color
format, depth policy, sample count, maximum in-flight frames, and fallback.

Avoid making a `MTLTexture`, `MTLBuffer`, `MTLRenderPipelineState`, or
`MTLCommandBuffer` the identity of a domain object. GPU objects are runtime
resources. Domain IDs, source revisions, and user actions belong in Swift
state or persistence; the renderer maps them into resource handles.

## Texture loading with `MTKTextureLoader`

`MTKTextureLoader` creates a Metal texture from existing image data. Treat the
URL/data and the resulting texture as different stages:

~~~text
user/app-owned URL or data
  -> scope and type validation
  -> decode/size/color policy
  -> MTKTextureLoader
  -> MTLTexture readiness
  -> render snapshot
~~~

Before loading, decide:

- whether the URL is bundled, security-scoped, downloaded, or user-selected;
- whether the feature is allowed to read the file while locked or offline;
- maximum pixel dimensions, compressed/uncompressed size, and mip policy;
- color space, alpha interpretation, orientation, and HDR/wide-color intent;
- whether the source can be discarded after a GPU texture is created;
- what a missing, malformed, oversized, or cancelled load shows;
- whether the texture may be shared between frames or must be replaced by
  revision.

Do not equate a non-nil texture with a valid visual result. Validate that the
shader’s texture/sampler contract matches the loaded format and that the
render path can draw the image on the declared device family. Keep source
metadata and privacy/retention rules outside the texture object.

For live camera/video or image-analysis features, the loader is usually not
the frame-ingest path. Use the capture framework’s buffers and a deliberate
conversion route; do not decode every frame from a file URL merely because
`MTKTextureLoader` can load still images.

## Model I/O and `MTKMesh`

Model I/O describes asset hierarchies, meshes, cameras, lights, transforms,
materials, and timed data. MetalKit supplies `MTKMesh`, mesh buffers, a buffer
allocator, and submeshes for Metal rendering. The bridge is valuable because a
`MDLAsset` can be loaded with a `MTKMeshBufferAllocator` and a vertex
descriptor selected for the intended Metal input layout, reducing unnecessary
copies and translations.

Keep the asset pipeline explicit:

~~~text
asset URL / package
  -> supported-format and file-scope check
  -> MDLAsset import
  -> hierarchy/material/animation inspection
  -> MDLVertexDescriptor and MTKMeshBufferAllocator choice
  -> MTKMesh / MTKSubmesh resources
  -> Metal pipeline input validation
  -> render snapshot and user review
~~~

Important distinctions:

| Stage | What it proves | What it does not prove |
| --- | --- | --- |
| `MDLAsset` constructed | Model I/O accepted the source and built an asset graph | Every texture/material/animation is present or visually correct |
| `MDLMesh`/`MTKMesh` built | Vertex/index data has a runtime representation | The shader consumes the descriptor correctly |
| `MTKSubmesh` selected | A submesh index/material unit is available | The material is safe, complete, or stylistically appropriate |
| Draw call encoded | The command encoder accepted the arguments | The GPU completed, the drawable presented, or frame time is acceptable |
| Screenshot captured | One device rendered one state | Animation, interaction, memory, thermal, accessibility, or release behavior |

Use stable asset IDs and source revisions. A file name or pointer to a mesh is
not enough to reconcile a scene after reload. Keep coordinate-system,
unit/scale, winding, culling, tangent/normal, texture, and animation policies
in the asset-import record. If a model is downloaded or generated, validate
its size, file type, integrity, and provenance before creating GPU resources.

When a Model I/O vertex descriptor is converted for Metal, validate the final
attribute offsets, formats, strides, buffer indexes, and shader argument
layout. Do not assume that a descriptor’s existence means the pipeline will
read the intended positions, normals, UVs, colors, or tangents.

## SwiftUI boundary and native shell

The renderer is usually best hosted as a focused visual surface inside a
native SwiftUI shell:

~~~text
navigation / toolbar / settings / review
  -> state-driven Metal surface
  -> semantic overlay or inspector
  -> fallback for unsupported, reduced-effects, and accessibility states
~~~

Use `UIViewRepresentable` to bridge `MTKView` on iOS when the selected SDK
requires the UIKit view route. The representable should:

- create the view and renderer once per representable identity;
- pass only the relevant render state in `updateUIView`;
- pause drawing when the feature is not visible or when policy requires it;
- dismantle the view and release GPU/display resources;
- expose a 2D list, controls, or inspector for essential actions;
- keep selection, editing, and confirmation independent from pixel shaders.

Do not draw the only button, error, permission explanation, or data label into
the Metal surface. If the visual itself is the product, add semantic overlays,
accessibility elements, alternate input, and a reduced-effects representation
that preserves the task.

## Liquid Glass around GPU content

Liquid Glass belongs to the native shell around the renderer unless a custom
render effect is the actual product requirement. A good hierarchy is:

~~~text
native navigation and toolbar
  -> readable status/progress/error region
  -> MetalKit visual surface
  -> glass controls for actions that operate on the surface
  -> inspector/review sheet
~~~

Keep the glass group small and functional. A GPU scene may be visually rich,
but the person still needs to know whether an asset is loading, whether the
renderer is paused, whether a generated adjustment is only a proposal, and
what action will happen next. Test increased contrast, reduced transparency,
Reduce Motion, Dynamic Type, dark/light appearance, and low-power behavior.

## On-device AI and custom rendering

AI can be useful around a renderer without becoming the renderer’s authority:

- suggest a color palette, material, camera framing, or layout adjustment from
  selected source assets;
- classify an imported asset before a person chooses a render profile;
- summarize a performance trace or explain a missing-resource error;
- generate a typed scene/material proposal for review;
- choose among deterministic fallback render paths after capability checks.

The safe pipeline is:

~~~text
source asset / measured frame data
  -> redacted, bounded feature input
  -> typed proposal
  -> deterministic format/bounds/device validation
  -> person review or explicit product policy
  -> renderer configuration revision
  -> measured result
~~~

Do not allow a model to emit arbitrary shader source, silently change a
security-sensitive visual, infer physical measurements from a render, or
commit a destructive asset replacement. A generated appearance is still a
proposal until the user and validator accept it.

## Performance, memory, and thermal discipline

Record a workload before optimizing: drawable size, refresh target, scene/mesh
count, texture dimensions, material count, shader/pipeline state, in-flight
frames, CPU/GPU frame time, memory peak, load time, and thermal/power state.

Use a measured budget:

| Budget | Design response |
| --- | --- |
| Drawable/frame time | Reduce cadence, work per pass, overdraw, resolution, or effect complexity |
| GPU memory | Bound texture/mesh sizes, release unused resources, stream deliberately |
| CPU preparation | Cache immutable resources, batch updates, avoid rebuilding on SwiftUI body changes |
| Pipeline/shader creation | Prewarm or show a clear loading state; do not stall the first interaction silently |
| Thermal/power | Pause or lower quality when the feature is hidden, backgrounded, or hot |
| Asset load time | Show progress/cancellation and preserve the last accepted result |

Use Xcode GPU capture, Instruments, XCTest metrics/signposts, and physical
devices as different evidence. A simulator or preview can validate state and
layout but cannot establish GPU frame time, thermal behavior, display cadence,
or device feature support.

## Proof route

The [MetalKit rendering capability route](../50-capability-recipes/85-metalkit-rendering-capability-route.md)
is the planning worksheet. The [MetalKit proof matrix](../60-verification/79-metalkit-rendering-proof-matrix.md)
maps claims to fixtures and device evidence, and the [MetalKit SwiftUI recipes](../70-code-recipes/97-metalkit-swiftui-rendering-recipes.md)
are compile-oriented route sketches.

## Sources

- [MetalKit](https://developer.apple.com/documentation/metalkit/)
- [MTKView](https://developer.apple.com/documentation/metalkit/mtkview/)
- [MTKViewDelegate](https://developer.apple.com/documentation/metalkit/mtkviewdelegate/)
- [MTKTextureLoader](https://developer.apple.com/documentation/metalkit/mtktextureloader/)
- [MTKMesh](https://developer.apple.com/documentation/metalkit/mtkmesh/)
- [MTKMeshBuffer](https://developer.apple.com/documentation/metalkit/mtkmeshbuffer/)
- [MTKMeshBufferAllocator](https://developer.apple.com/documentation/metalkit/mtkmeshbufferallocator/)
- [MTKSubmesh](https://developer.apple.com/documentation/metalkit/mtksubmesh/)
- [Model I/O](https://developer.apple.com/documentation/modelio/)
- [MDLAsset](https://developer.apple.com/documentation/modelio/mdlasset/)
- [MDLMesh](https://developer.apple.com/documentation/modelio/mdlmesh/)
- [Loading a Model I/O asset with a MetalKit buffer allocator](https://developer.apple.com/documentation/modelio/mdlasset/init%28url%3Avertexdescriptor%3Abufferallocator%3Apreservetopology%3Aerror%3A%29-510xi)
- [Metal](https://developer.apple.com/documentation/metal/)
- [MTLDevice](https://developer.apple.com/documentation/metal/mtldevice/)
- [MTLCommandQueue](https://developer.apple.com/documentation/metal/mtlcommandqueue/)
- [Performing calculations on a GPU](https://developer.apple.com/documentation/metal/performing-calculations-on-a-gpu)
- [Metal feature set tables](https://developer.apple.com/metal/capabilities/)
- [UIViewRepresentable](https://developer.apple.com/documentation/swiftui/uiviewrepresentable/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [Testing performance](https://developer.apple.com/documentation/xctest/performance-tests)
- [XCTHitchMetric](https://developer.apple.com/documentation/xctest/xcthitchmetric)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
