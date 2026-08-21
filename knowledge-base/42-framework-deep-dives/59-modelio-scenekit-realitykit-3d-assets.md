# Model I/O, SceneKit, and RealityKit 3D assets

The native 3D route is a pipeline, not a single view:

~~~text
asset file or generated mesh
  -> Model I/O inspection / normalization / processing
  -> RealityKit entity hierarchy or existing SceneKit scene
  -> SwiftUI, ARKit, or platform-specific presentation
  -> controls, review state, accessibility, and proof
~~~

Model I/O is the asset-language layer. RealityKit is the preferred high-level
runtime for new 3D work. SceneKit remains useful for maintaining an existing
app, but Apple now documents it as deprecated and points developers toward
RealityKit. Do not let a familiar `SCNNode` API quietly become the architecture
for a new long-lived product.

## Choose the layer from the outcome

| Outcome | Start with | Keep separate |
| --- | --- | --- |
| Show a packaged model in a SwiftUI surface | RealityKit `Model3D` when the selected target supports it | Async loading phase, placeholder, error, accessibility summary, and asset ownership |
| Place and manipulate entities or build an AR scene | RealityKit `Entity`, `ModelEntity`, components, and a target-appropriate view | ARKit tracking/camera state, scene content, gestures, and domain truth |
| Import, inspect, normalize, process, or export 3D data | Model I/O `MDLAsset`, `MDLMesh`, `MDLSubmesh`, `MDLVertexDescriptor`, materials, and resolvers | File trust, resource resolution, coordinate/scale policy, memory, and export validation |
| Keep an existing SceneKit app working | `SCNScene`, `SCNNode`, `SCNView`, existing scene files, and a bounded bridge | Soft-deprecation risk, target availability, maintenance scope, and a migration seam |
| Render custom GPU work or own the frame graph | Metal/MetalKit | Device feature sets, shader/pipeline lifecycle, frame pacing, thermal behavior, and accessibility outside the renderer |

The first decision is whether the user needs a still model, an interactive
scene, an augmented-reality relationship, a game loop, or an asset-processing
tool. A `Model3D` preview is not an AR session. An imported mesh is not a
validated physical measurement. A rendered entity is not domain state.

## Model I/O as the asset boundary

`MDLAsset` is an indexed container for objects and hierarchy information such
as meshes, transforms, cameras, lights, and time samples. It can load from a
URL, expose objects through the hierarchy, and export an asset to supported
formats. Treat the URL and all referenced resources as untrusted input:

1. obtain the file from a deliberate bundle, document picker, provider, or
   network/cache route;
2. constrain the file type, size, and resource budget before loading;
3. inspect the asset and surface a readable failure instead of force-unwrapping
   a missing scene;
4. resolve external textures through a known resolver or package layout;
5. normalize scale, up-axis, names, and coordinate assumptions explicitly;
6. process only what the chosen renderer needs;
7. export to a known destination and reopen it before treating the artifact as
   valid.

Model I/O can load textures after the asset is created. A successfully created
`MDLAsset` does not prove that every texture, material, animation, or referenced
resource resolved. Keep a resource report with missing paths and fallback
choices.

### Meshes, submeshes, and vertex descriptors

An `MDLMesh` contains vertex buffers and one or more `MDLSubmesh` objects.
Submeshes describe index data and material references. The
`MDLVertexDescriptor` describes the layout of attributes such as positions,
normals, colors, tangents, and texture coordinates. The descriptor is a
contract between the asset and the renderer; it is not merely metadata to
print in a debug panel.

Before passing a mesh onward, record:

- vertex count and submesh count;
- attribute names, formats, offsets, strides, and buffer indices;
- index type and topology assumptions;
- bounds and units/scale policy;
- material and texture references;
- normals/tangents generated or missing;
- animation/time-sample range if present;
- memory estimate and any decimation/subdivision step.

Use Model I/O mesh-buffer allocators when a route needs to reduce copies across
loading, processing, and rendering. Measure the result; a fewer-copy pipeline
can still be slower or more memory-hungry for a small asset.

### Hierarchy, naming, and time

Model I/O object paths derive from object names. Names are therefore part of
the runtime contract when a later route finds a child by path, attaches a
review marker, or maps a domain identifier to a model part. Normalize names at
ingest and keep an asset manifest rather than relying on authoring-tool names
that may contain spaces or unstable suffixes.

Assets can contain time-varying mesh or transform data. `frameInterval`,
`startTime`, and `endTime` describe the sample range. A request outside the
range is clamped, and interpolation behavior depends on the asset format. Do
not infer continuous animation from a nonzero time range; inspect the actual
asset and render it on the target.

## SceneKit: maintenance and migration boundary

SceneKit provides a node-based scene graph with `SCNScene`, `SCNNode`,
`SCNView`, actions, animation, physics, particle effects, and physically based
rendering. `SCNScene` can also be created from a Model I/O asset, which makes it
useful as a bridge for an existing codebase.

Apple’s current guidance marks SceneKit deprecated and describes it as a soft
deprecation: existing applications continue to work, but the framework is in
maintenance mode and new projects should use RealityKit. Treat that as an
architecture signal:

- keep SceneKit behind a named adapter in an existing product;
- avoid adding new product-critical systems to `SCNNode` subclasses;
- record the current scene-file format and export path;
- isolate the SwiftUI `SceneView`/`SCNView` boundary from domain state;
- plan an asset conversion and behavior mapping before a migration;
- do not claim that a SceneKit-to-RealityKit conversion is mechanical.

The conceptual mapping is not one-to-one:

| SceneKit concept | RealityKit direction | Migration question |
| --- | --- | --- |
| Node hierarchy | Entity hierarchy plus components | Which state belongs in `Transform`, `ModelComponent`, physics, or a custom component? |
| Geometry/material | `ModelComponent`, `MeshResource`, materials | Are materials and texture resources supported with the desired fidelity? |
| Per-node update/delegate | Systems, subscriptions, or app state | Can shared behavior be expressed once per frame rather than per object? |
| SCN/scene asset | USD/Reality asset route | Which animations, names, materials, and scene choices survive conversion? |
| Actions/animations | RealityKit animation/action APIs or SwiftUI state | Which transitions are presentation-only and which are domain events? |
| SceneKit physics | RealityKit physics components/collisions | Are collision shapes, mass, constraints, and determinism equivalent? |
| `SCNView` | `Model3D`, `RealityView`, AR view, or a platform target surface | What is the actual target and input model? |

Use Apple’s SceneKit-to-RealityKit sample and WWDC session as the migration
starting point. Maintain a before/after fixture with a representative asset,
animation, light, material, audio, and interaction rather than comparing only a
static screenshot.

## RealityKit’s entity-component-system route

RealityKit represents scene content with `Entity` instances and composable
components. `ModelEntity` is a common visible entity with a `ModelComponent`;
other components can describe transforms, collisions, physics, synchronization,
accessibility, audio, or custom behavior. Systems operate on matching entities
and are the right place for behavior that affects many entities each frame.

This gives a useful ownership split:

| Owner | Owns | Does not own |
| --- | --- | --- |
| Domain model / SwiftData/Core Data | Product records, selected asset ID, user annotations, review decisions | Per-frame transform or renderer internals |
| RealityKit scene | Entities, components, anchors, resources, subscriptions | Server truth or unreviewed AI mutations |
| SwiftUI shell | Navigation, controls, state presentation, empty/loading/error copy | Hidden renderer lifecycle or direct unbounded asset mutation |
| ARKit adapter | Tracking/session state and real-world anchors | The meaning of a domain record or user consent for a side effect |
| System surface | Share/export/shortcut/widget representation | The full live scene or a private renderer object |

An entity hierarchy can be loaded from USD or Reality assets. Synchronous load
methods block the main actor and are inappropriate for a responsive app route;
use the documented asynchronous loading path or `Model3D` phase-driven view and
show a placeholder/error state. A successful load is still not proof of a
reasonable frame rate, correct scale, visible textures, collision behavior, or
accessibility.

## SwiftUI and native shell composition

Treat the 3D surface as one content region inside a native screen:

~~~text
navigation title / asset identity
  -> model surface with loading/error/empty phases
  -> concise status and provenance
  -> semantic controls: rotate, reset, inspect, annotate, share
  -> optional review sheet for AI or imported metadata
  -> deterministic save/export action
~~~

Liquid Glass should group actions that belong to the model surface. It should
not obscure the object, become the only contrast boundary, or imply that the
asset has been verified. Prefer native toolbar/buttons and a small status row
over custom chrome drawn inside the 3D scene. Keep the object’s important label,
measurements, and review state in ordinary SwiftUI text and controls so they
remain available to VoiceOver, Dynamic Type, reduced-transparency settings, and
non-3D fallback layouts.

For a static model, a phase-aware `Model3D` route can be the smallest surface.
For entity manipulation, use a RealityKit view/renderer appropriate to the
selected OS target and keep the SwiftUI state adapter explicit. Do not assume a
visionOS `RealityView` or immersive-space route is interchangeable with an iOS
screen.

## On-device AI with 3D assets

AI can assist around a 3D asset without becoming the asset authority:

~~~text
validated asset manifest / thumbnail / bounded metadata
  -> on-device model proposal
  -> typed label, category, material note, or review flag
  -> source paths and model/version metadata
  -> person review
  -> deterministic domain commit
~~~

Good candidates include suggesting names for stable object paths, classifying a
bounded set of known asset categories, generating an accessibility description
from user-approved metadata, or flagging missing textures for review. Keep
arbitrary geometry generation, automatic material replacement, physical
measurement, and safety-critical placement outside the trusted commit path
unless a separate target-specific evaluation proves them.

Never send raw imported assets or private annotations to a remote model merely
because a local model is unavailable. Make the fallback explicit: no AI,
manual label, local-only metadata, or user-mediated export. Store the source
asset revision, proposal, model route/version, review decision, and final
mutation separately.

## Availability, privacy, and resources

The framework catalog is broad, but actual availability depends on the target
SDK, OS, device family, asset type, package/resource membership, and sometimes
AR or camera hardware. Before implementation, record:

- deployment target and SDK for `Model3D`, RealityKit, ARKit, SceneKit, and
  Model I/O symbols;
- whether the route is iPhone/iPad only, Catalyst, visionOS, or multi-platform;
- asset file formats and bundle/package membership;
- network/download and cache policy for external assets;
- camera usage description and permission only when an AR/capture route actually
  needs it;
- any model, texture, GPU, or memory resource limits;
- whether the asset can be shared, indexed, synced, or included in AI context;
- user-facing accessibility, export, deletion, and retention behavior.

An asset loaded from a document provider needs document/security-scoped URL
handling and a copy/cache policy. An asset downloaded over the network needs
origin, integrity, size, cancellation, and offline behavior. A bundled asset
still needs resource-membership and release-artifact inspection.

## Proof that matches the route

Source documentation proves the API shape and stated deprecation guidance. It
does not prove that a particular model is included in the target, that a
texture resolves, or that a device renders it smoothly. Use separate evidence
for:

- source and availability review;
- compile in the named target and configuration;
- unit/fixture validation of asset reports and proposal schemas;
- simulator/preview layout and state choreography;
- physical-device rendering, input, memory, thermal, and accessibility;
- AR/session/camera behavior if the route uses it;
- signed/release artifact resource membership and entitlements;
- migration comparison for an existing SceneKit project;
- system share/export or companion surface behavior.

The companion [3D asset proof matrix](../60-verification/76-3d-asset-runtime-proof-matrix.md)
turns these into fixtures. The [3D asset capability route](../50-capability-recipes/82-3d-asset-runtime-capability-route.md)
is the implementation worksheet, and the [3D asset code recipes](../70-code-recipes/94-3d-asset-runtime-recipes.md)
are deliberately labeled route sketches until compiled.

## Sources

- [Model I/O](https://developer.apple.com/documentation/modelio)
- [MDLAsset](https://developer.apple.com/documentation/modelio/mdlasset)
- [MDLMesh](https://developer.apple.com/documentation/modelio/mdlmesh)
- [MDLVertexDescriptor](https://developer.apple.com/documentation/modelio/mdlvertexdescriptor)
- [SceneKit](https://developer.apple.com/documentation/scenekit)
- [SCNScene](https://developer.apple.com/documentation/scenekit/scnscene)
- [SCNNode](https://developer.apple.com/documentation/scenekit/scnnode)
- [SCNView](https://developer.apple.com/documentation/scenekit/scnview)
- [RealityKit](https://developer.apple.com/documentation/realitykit)
- [Entity](https://developer.apple.com/documentation/realitykit/entity)
- [ModelEntity](https://developer.apple.com/documentation/realitykit/modelentity)
- [Model3D](https://developer.apple.com/documentation/realitykit/model3d)
- [Component](https://developer.apple.com/documentation/realitykit/component)
- [Systems](https://developer.apple.com/documentation/realitykit/ecs-systems)
- [Loading entities from a file](https://developer.apple.com/documentation/realitykit/entity/loadasync%28contentsof%3Awithname%3A%29)
- [Bringing your SceneKit projects to RealityKit](https://developer.apple.com/documentation/realitykit/bringing-your-scenekit-projects-to-realitykit)
- [Bringing your SceneKit projects to RealityKit](https://developer.apple.com/documentation/realitykit/bringing-your-scenekit-projects-to-realitykit)
- [Spatial layout](https://developer.apple.com/design/human-interface-guidelines/spatial-layout/)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
