# 3D asset runtime capability route

Use this route when an app needs to import, inspect, display, manipulate,
annotate, or export 3D content. It keeps the asset pipeline, renderer, native
UI, optional on-device AI, and proof requirements separate.

## Route selection

| Need | Primary route | Do not assume |
| --- | --- | --- |
| Display one bundled or remote model in a native screen | RealityKit `Model3D` or a target-appropriate RealityKit view | That the model loaded, textures resolved, or the device can sustain the desired frame rate |
| Interactive entities, animation, collision, or AR | RealityKit `Entity`/`ModelEntity` plus ARKit when real-world tracking is required | That a renderer’s interaction equals a committed domain action |
| Inspect or transform an asset before rendering | Model I/O `MDLAsset` and mesh/descriptor APIs | That file extension alone validates the asset or its referenced resources |
| Maintain an existing SceneKit app | SceneKit adapter and a migration plan | That SceneKit is a good default for a new long-lived app |
| Custom GPU pipeline | Metal/MetalKit | That a custom shader improves the product or is accessible by itself |

Start with the smallest route that serves the user job. Add ARKit only when the
person needs a relationship to the physical world. Add Model I/O when the app
needs deterministic asset inspection or processing. Add on-device AI only when
it makes a bounded proposal or classification useful.

## Step 1: write the asset contract

Create an asset manifest before writing a view:

~~~text
AssetManifest
  id / source revision / origin
  file type and byte size
  resource references and resolution report
  coordinate system / up axis / unit policy
  bounds / mesh and material counts
  animation range and named objects
  thumbnail / fallback representation
  retention, sharing, and AI-context policy
~~~

The manifest is an inspection result, not a guarantee that every runtime
feature will work. Keep the original source file or a deterministic copy when
the product needs reproducible reprocessing. Keep a separate failure report for
missing textures, unsupported materials, malformed data, and memory limits.

## Step 2: declare the target and capability matrix

Record this before selecting symbols:

| Field | Example decision |
| --- | --- |
| Deployment target / SDK | Named iOS/iPadOS target and Xcode SDK |
| Presentation | `Model3D`, RealityKit view, ARKit-backed view, or existing SceneKit adapter |
| Platforms | iPhone, iPad, Catalyst, visionOS, or a deliberately shared subset |
| Asset origin | Bundle, document picker, File Provider, network cache, or generated mesh |
| Camera requirement | None for static model; camera permission only for AR/capture |
| Resource budget | Maximum model/texture bytes, vertex count, and concurrent loads |
| Input | Touch, pointer, keyboard, controller, or spatial input |
| AI route | None, closed-set label proposal, metadata draft, or review flag |
| System handoff | Share/export/Quick Look/widget/shortcut, if any |

Check every selected symbol with the current Apple documentation and the actual
deployment target. Do not infer iOS support from a visionOS sample or from an
API appearing in autocomplete.

## Step 3: ingest and inspect with Model I/O

The import route should be cancellable and bounded:

1. receive a security-scoped/document URL or a trusted bundle URL;
2. validate extension, file size, and available disk/memory budget;
3. initialize `MDLAsset` and capture errors;
4. load or resolve textures according to a known resource policy;
5. walk the hierarchy and record stable names/paths;
6. inspect meshes, submeshes, vertex descriptors, bounds, materials, and time;
7. normalize only the fields the selected runtime requires;
8. create a preview projection and preserve the source revision;
9. export/reopen a derived asset when conversion is part of the feature.

Do not perform expensive import work synchronously on the main actor. Make the
screen say importing, preparing preview, waiting for resources, ready, failed,
or cancelled. A user-started import that is interrupted must not be marked
complete merely because a partial file exists.

## Step 4: choose the runtime

### Static SwiftUI preview

Use a phase-driven `Model3D` route where the target supports it. Keep the
placeholder layout stable and provide a text fallback. Store a thumbnail or
manifest projection if the model is unavailable at the moment the screen opens.

### Interactive RealityKit scene

Use `Entity` and components for scene state. Use `ModelEntity` when the entity
represents a visible model. Put cross-entity per-frame behavior in systems,
not in duplicated view callbacks. Load asynchronously; synchronous RealityKit
load methods block the main actor and can hitch or make the app unresponsive.

Keep the SwiftUI adapter responsible for navigation and user intent. When a
gesture changes a presentation transform, do not automatically persist a
domain mutation unless the product explicitly defines that behavior.

### ARKit addition

Add ARKit only for camera/world tracking, anchors, plane detection, scene
understanding, or other real-world relationships. Then add camera privacy,
tracking state, interruption, denied permission, unsupported-device, and
non-AR fallback states to the feature contract. An AR anchor is observation
state; it is not a verified measurement or a saved domain record.

### Existing SceneKit route

Wrap `SCNScene`/`SCNNode`/`SCNView` behind an adapter, freeze the scope, and
write a conversion inventory. For new work, prefer RealityKit and use Apple’s
SceneKit-to-RealityKit sample to map assets, hierarchy, animations, lighting,
audio, effects, and interactions. Soft deprecation means a maintenance route
can remain valid while still being the wrong default for a new product.

## Step 5: compose the native surface

The app-owned screen should expose:

- asset identity and source/revision;
- stage loading/error/partial-resource state;
- semantic reset, inspect, annotate, and export actions;
- model metadata and accessible summary outside the renderer;
- review sheet for imported or AI-derived values;
- deterministic save/delete/retry behavior.

Use Liquid Glass for functional controls that need grouping. Keep glass out of
the model’s only text/contrast path. Make the toolbar adapt to compact width,
iPad split views, keyboard/pointer input, large text, reduced transparency, and
localization.

## Step 6: add a bounded on-device AI route

Prefer the following proposal contract:

~~~text
AssetManifest revision N
  -> bounded model input: names, approved metadata, thumbnail if allowed
  -> typed proposal with object paths and allowed values
  -> deterministic validation against manifest revision N
  -> review: accept / edit / dismiss
  -> commit to a separate derived record
~~~

Good first routes are closed-set categories, object-name suggestions,
accessibility-description drafts, or a missing-resource explanation. Avoid
unbounded geometry/material mutation, physical measurements, or safety-critical
placement decisions. Record model availability, model/version route, source
revision, prompt/context policy, proposal, validation result, and review choice.

If the model is unavailable, the feature should still offer manual labels,
ordinary metadata, or a no-AI path. Do not upload the asset as an automatic
fallback unless the person explicitly chose a remote route and the product’s
privacy policy permits it.

## Step 7: persistence and system handoff

Persist value projections, not live renderer objects:

| Persist | Do not persist as domain truth |
| --- | --- |
| Source URL/copy identity, manifest revision, annotations, review decisions | `Entity`, `SCNNode`, `ModelEntity`, `SCNView`, or a renderer subscription |
| Derived labels and provenance | Unreviewed AI text or a hidden material mutation |
| Camera/transform only if product-defined | Every frame’s transform or a transient gesture |
| Export record and destination status | “Shared” merely because a sheet appeared |

For ShareLink, Quick Look, a widget, App Intent, or another system surface,
create a bounded transferable/projection. The system surface does not prove
the model is editable, fully resolved, or available in the original renderer.

## Step 8: proof packet

Create one evidence record with:

- source URLs and target-SDK availability check;
- compile/build configuration and target membership;
- asset fixtures and expected inspection reports;
- preview/simulator state evidence;
- physical-device rendering, input, memory, frame time, and thermal evidence;
- AR camera/tracking evidence where applicable;
- accessibility task results and alternate-input checks;
- signed artifact resource/package inspection;
- SceneKit migration comparison for legacy routes;
- system share/export/Quick Look/extension evidence;
- AI proposal evaluation and no-AI fallback evidence.

The [3D asset proof matrix](../60-verification/76-3d-asset-runtime-proof-matrix.md)
is the checklist. The [3D asset recipes](../70-code-recipes/94-3d-asset-runtime-recipes.md)
provide route sketches but do not replace a named target build.

## Stop conditions

Pause the implementation when:

- a model file or texture resolver is treated as trusted without validation;
- a SceneKit dependency is added to new product architecture without a reason;
- a synchronous load runs on the main actor for a user-facing screen;
- AR/camera permission is requested for a static preview;
- a gesture or AI proposal silently mutates domain truth;
- glass covers the only legible status or control boundary;
- a renderer-only demo is presented as accessibility, performance, or release
  proof;
- a remote AI fallback would expose private assets without user choice.

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
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Spatial layout](https://developer.apple.com/design/human-interface-guidelines/spatial-layout/)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
