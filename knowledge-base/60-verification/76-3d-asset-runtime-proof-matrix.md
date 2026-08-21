# 3D asset runtime proof matrix

This matrix separates what Apple’s documentation establishes from what a
particular iOS app must measure. A model that appears in a preview is useful
evidence for layout, but it is not evidence of asset integrity, physical-device
performance, accessibility, or release configuration.

## Evidence ladder

| Claim | Minimum evidence | Does not prove |
| --- | --- | --- |
| API is documented | Current Apple source and target availability review | That the selected deployment target compiles it |
| Asset is accepted | Model I/O fixture report and error handling | That every texture/material/animation resolves in the runtime |
| SwiftUI preview behaves | Preview/simulator state fixture | Physical frame time, memory, thermal, or input ergonomics |
| RealityKit scene behaves | Named-target compile plus deterministic scene fixture | AR tracking, physical performance, or system surface behavior |
| SceneKit migration is viable | Before/after fixture with representative content | Full visual/behavioral equivalence or long-term support |
| AI proposal is useful | Versioned fixtures, typed validation, review task, and fallback | General model quality or permission to mutate the source asset |
| Release contains assets | Signed artifact/package/resource inspection | Successful remote delivery or a good device experience |

## Fixture pack

Keep a small, versioned asset set with expected reports:

| Fixture | Expected purpose |
| --- | --- |
| Small bundled model with local textures | Happy path, resource membership, initial render |
| Model with a missing external texture | Partial-resource state and readable fallback |
| Malformed or unsupported file | Bounded failure, cancellation, and no crash |
| Large/high-detail model | Memory, import latency, first-frame, and thermal budget |
| Multiple object names with spaces/symbols | Stable path/name normalization |
| Mesh with normals/tangents absent | Inspection and deterministic processing decision |
| Multiple submeshes/materials | Material mapping and render fidelity |
| Animated/time-sampled asset | Time range, frame sampling, pause, and cancellation |
| SceneKit `.scn` fixture | Existing adapter and migration inventory |
| USD/RealityKit fixture | Entity hierarchy, async load, and resource behavior |
| Private annotation/provenance fixture | AI input policy, redaction, retention, and deletion |

Store expected values in a fixture manifest rather than comparing only
screenshots. Include file hash or source revision, expected units/scale, object
paths, mesh counts, resource references, and accepted fallback behavior.

## Asset inspection evidence

For each Model I/O route, record:

- `MDLAsset` initialization result and error;
- `canImportFileExtension` decision where used;
- object count, hierarchy paths, names, and transforms;
- `MDLMesh` vertex/submesh counts and bounds;
- `MDLVertexDescriptor` attributes, formats, strides, and buffer indices;
- material, texture, and external-resource resolution;
- time sample range and chosen sampling policy;
- memory estimate and processing duration;
- export destination, file size, and successful reopen;
- cancellation and cleanup behavior.

The inspection report should be safe to show in diagnostics without embedding
private file paths or raw user content in analytics.

## Runtime and interaction evidence

| Route | Required run | Record |
| --- | --- | --- |
| `Model3D` preview | Named iOS/iPadOS target and representative asset | Loading/ready/failure phase, placeholder stability, text fallback, orientation/size, and retry |
| RealityKit entity scene | Named target with async load and interaction | Entity hierarchy, transforms, materials, input, pause/resume, cancellation, and memory |
| ARKit addition | Supported physical device with camera permission states | Permission, unsupported device, tracking limited/normal/interrupted, anchors, reset, privacy, and non-AR fallback |
| SceneKit maintenance | Existing target and representative `.scn` | Existing behavior, warning/deprecation inventory, adapter ownership, and migration seam |
| Export/share | Real destination or controlled system surface | Output existence, reopen/readability, user cancellation, privacy/redaction, and destination result |

Do not label a local file URL “shared” because a share sheet was presented. Do
not label a loaded entity “placed” because it exists in a scene graph. Record
the actual side effect separately.

## Performance and resource evidence

Measure on representative physical devices and configurations:

- cold import and warm-cache load duration;
- time to first useful preview and first interaction;
- main-thread stalls/hitches during load and interaction;
- memory before/after asset load, texture load, and scene teardown;
- frame time or hitch rate for the target presentation;
- energy/thermal behavior during sustained interaction;
- background/foreground recovery and cancellation;
- large-text/accessibility layout cost around the renderer;
- export duration and temporary storage usage.

Use the release-build route where performance or resource claims matter. A
Debug build, simulator, preview, or newest device can hide a problem in the
actual shipping configuration.

## Accessibility evidence

Run task-based checks with the renderer visible and unavailable:

- VoiceOver identifies the asset, load state, selected part, and actions;
- important object metadata is exposed in a non-renderer summary;
- reset, inspect, annotate, export, and retry are reachable without a gesture;
- Dynamic Type does not cover or hide controls;
- reduced motion/transparency and increased contrast preserve understanding;
- keyboard, pointer, Switch Control, and Voice Control can complete the core
  task where those inputs are supported;
- localization, long labels, right-to-left layout, and iPad sizes are usable;
- color, depth, glow, and texture are not the only state cues.

For spatial targets, test comfort and depth relationships separately. For iOS,
prove that the critical task remains understandable as a conventional 2D UI
with a 3D content region.

## SceneKit-to-RealityKit evidence

For a migration, keep a comparison table:

| Behavior | Existing SceneKit result | RealityKit result | Decision |
| --- | --- | --- | --- |
| Asset hierarchy and names | Recorded fixture | Recorded fixture | Preserve, rename, or map explicitly |
| Materials/textures | Screenshot plus resource report | Screenshot plus resource report | Accept fidelity or revise asset |
| Animation/timing | Timed interaction | Timed interaction | Map semantics, not only pixels |
| Lighting/effects/audio | Target run | Target run | Separate unsupported/changed behavior |
| Collision/physics | Input fixture | Input fixture | Compare outcome and determinism |
| Accessibility/control path | Task run | Task run | Keep semantic shell independent of renderer |
| Memory/frame behavior | Metric packet | Metric packet | Use release configuration and target devices |

Apple’s soft-deprecation guidance supports continued operation of existing
SceneKit apps, but the migration decision should include maintenance cost and
future capability needs. A static screenshot is not a migration proof.

## On-device AI evidence

For an AI-assisted asset feature, record:

- the source asset revision and redacted input fields;
- model route, availability state, model/version identifier, and locale;
- proposal schema and allowed values;
- invalid/ambiguous/stale proposal behavior;
- deterministic validation against the source revision;
- review task completion: accept, edit, dismiss, retry;
- no-AI/manual fallback;
- privacy/retention/deletion behavior;
- whether the accepted result changes only a derived record or the canonical
  asset;
- representative quality, latency, memory, and thermal observations.

Do not generalize one model’s labels to all asset types or call a generated
description a verified physical interpretation. Keep original metadata and
review history available according to product retention policy.

## Signed/release evidence

Inspect the archive or signed artifact for:

- target membership of `.usdz`, `.usda`, `.usdc`, `.reality`, `.scn`, textures,
  shaders, and fixture resources;
- package/resource paths and case sensitivity;
- required entitlements and privacy strings for AR/camera or other system
  routes;
- deployment target and architecture;
- release-only asset processing or compression changes;
- App Store/TestFlight install and first-run behavior;
- export/share or extension resources if they are separate targets.

Asset inclusion in an archive is necessary, not sufficient. Run the installed
release artifact on the intended device family and exercise the route.

## Verification record template

~~~text
Feature / target / SDK / build configuration:
Asset fixture and source revision:
Model I/O report:
Runtime route: Model3D / RealityKit / SceneKit / ARKit / Metal
Permissions and entitlements:
Preview/simulator evidence:
Physical-device evidence:
Accessibility task evidence:
Performance/thermal/memory evidence:
AI proposal/evaluation evidence:
Signed artifact/resource evidence:
System export/share evidence:
Known limits and fallback:
Conclusion: documented / compiled / simulated / device / system / release
~~~

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
- [Loading entities from a file](https://developer.apple.com/documentation/realitykit/entity/loadasync%28contentsof%3Awithname%3A%29)
- [Bringing your SceneKit projects to RealityKit](https://developer.apple.com/documentation/realitykit/bringing-your-scenekit-projects-to-realitykit)
- [Bringing your SceneKit projects to RealityKit](https://developer.apple.com/documentation/realitykit/bringing-your-scenekit-projects-to-realitykit)
- [XCTest](https://developer.apple.com/documentation/xctest)
- [Performance Tests](https://developer.apple.com/documentation/xctest/performance-tests)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
