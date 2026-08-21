# Spatial scene, ARKit, RoomPlan, and Object Capture proof matrix

This matrix separates documented API understanding, deterministic scene logic, UI review, physical camera/tracking evidence, device-specific capability evidence, asset/reconstruction evidence, AI review, and release proof. A loaded model or simulator preview is not proof that spatial tracking, occlusion, room capture, or reconstruction works on a real device.

## Evidence levels

| Level | Evidence | What it proves |
| --- | --- | --- |
| L0 | Official-source and target review | The selected ARKit, RealityKit, RoomPlan, or Object Capture route is understood |
| L1 | Deterministic scene/asset fixtures | Transform math, state transitions, asset validation, AI proposal schema, and failure handling |
| L2 | Preview/simulator/UI fixture | SwiftUI shell, accessibility labels, Liquid Glass grouping, manual fallback, review flow |
| L3 | Signed physical-device run | Camera permission, tracking, raycast, session interruption, gesture, and target-specific RealityKit behavior |
| L4 | Declared hardware/environment matrix | LiDAR/scene reconstruction, people occlusion, RoomPlan, Object Capture, thermal/storage, lighting, and motion behavior |
| L5 | Release artifact and privacy review | Entitlements, usage descriptions, target membership, resources, supported devices, signed archive, and declared data behavior |

## Capability gate

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| AR feature is offered only when supported | Device matrix, configuration support checks, unsupported route | A camera device is not automatically AR-capable for every configuration |
| Camera permission is handled | Fresh-install permission run, denial, Settings change, manual route | A simulator prompt or Info.plist entry does not prove physical camera use |
| Scene reconstruction is available | supportsSceneReconstruction result on each declared device class | One LiDAR device does not prove every iPhone/iPad target |
| Object Capture is available | ObjectCaptureSession.isSupported and target/device run | Creating a session without the check can fail at runtime |
| Photogrammetry is available | PhotogrammetrySession.isSupported, resource/thermal/storage run | Capture support does not prove reconstruction support |
| RealityView route is usable | Named target compilation and interaction test | A visionOS-oriented sample is not automatically an iOS camera AR proof |

## ARKit tracking and placement

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| World tracking starts | Physical device, camera consent, ARSession/ARView run, tracking state | Framework import or preview does not prove tracking |
| Raycast finds a surface | Named device, lighting, horizontal/vertical/estimated/existing queries | One successful tap does not prove stable placement |
| Plane refinement is safe | Initial placement, later anchor extent/transform change, reconciliation log | A detected plane boundary is not a survey-grade measurement |
| Placement survives movement | Walk-around, relocalization, interruption, background/foreground | A stationary demo does not prove recovery |
| Tracking degradation is understandable | Low light, blank wall, fast motion, obstruction, tracking reason UI | A generic spinner hides actionable sensor state |
| Image/object detection works | Real reference image/object set, scale/orientation, false positives | Loading a reference asset does not prove camera detection |

## Scene reconstruction and occlusion

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Mesh reconstruction works | Supported device, mesh option, room shapes/materials, mesh update logs | Plane detection alone is not mesh reconstruction |
| Virtual content is occluded | Real table/wall/person crossing, depth/mesh configuration, fallback run | A dark mask or static model does not prove physical occlusion |
| People occlusion is safe | Multiple body positions, lighting, motion, partial body, privacy review | One person in a clear room is not general body segmentation proof |
| Geometry drives placement/collision | Deterministic geometry test plus physical environment run | AI-generated geometry cannot replace sensor evidence |
| Mesh retention is privacy-safe | Data-flow review, deletion, logs, export/share checks | Camera permission is not permission to retain a room mesh |

## RealityKit scene behavior

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Entity hierarchy is stable | Create/update/remove/rebuild view, session restart, ID reconciliation | A single view lifetime does not prove persistence |
| Components encode state | Unit/fixture tests for components and domain records | An Entity object is not the saved domain model |
| Systems meet frame budget | Instruments/frame-time/memory/thermal run with declared scene size | A small demo does not prove production performance |
| Gestures select the intended object | Overlap, occlusion, small target, multi-object, Voice Control tests | One easy tap does not prove reliable hit testing |
| Asset loading is resilient | Missing, malformed, oversized, delayed, and cancellation cases | A bundled USDZ does not prove remote/catalog asset safety |

## RoomPlan

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Guided room capture works | Physical camera/LiDAR run, instructions, start/stop/cancel, delegate lifecycle | A rendered sample room is not a capture proof |
| Single-room data is usable | CapturedRoom build, review of walls/openings/objects/dimensions, save/delete | Recognized categories are observations and may be incomplete |
| Multi-room structure works | Multiple room runs, preserved room identity, StructureBuilder merge, floor changes | One-room output does not prove a multi-room merge |
| USD/USDZ export works | Export/import on named target, coordinate/scale review, malformed path | Export callback alone does not prove another app interprets it correctly |
| Catalyst processing works | Captured data on Mac Catalyst, no capture-session claim | Catalyst processing does not prove iOS capture sensors |
| Privacy story is complete | Retention/share/delete/log review for scans and exports | “Local” is not a complete privacy explanation if backups/export exist |

## Object Capture and photogrammetry

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Capture session is supported | ObjectCaptureSession.isSupported on named device | The view can exist in code without proving session support |
| Guided capture completes | ObjectCaptureView/session states, feedback, pause/cancel, varied object surfaces | One well-lit object does not prove all capture conditions |
| Reconstruction completes | PhotogrammetrySession support, input set, output request, cancellation/resource run | Capture completion is not model reconstruction |
| Model quality is acceptable | Geometry/texture/scale/orientation review with acceptance thresholds | “Generated” does not mean shippable asset |
| Reconstruction is resumable | Input-set persistence, interrupted run, retry, partial-output cleanup | A long synchronous task risks losing user work |
| Transfer is disclosed | Local/Mac/cloud path, user confirmation, data deletion and privacy review | Moving photos off device is a material data-flow change |

## Native design and accessibility

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Spatial task is understandable | First-run task test, plain-language instruction, tracking-loss recovery | Technical terms like ARKit should not be required |
| Glass shell is native | Light/dark, contrast, reduced transparency, Dynamic Type, hit-region review | Material does not fix unreadable 3D or uncertain geometry |
| 3D object is accessible | AccessibilityComponent labels/actions plus 2D list/inspector | A label on a container does not expose every important entity |
| No-AR fallback is equivalent | Complete core task manually or in 2D | A settings screen is not a functional fallback |
| Motion is safe | Reduce Motion, stable status, no essential animation-only feedback | Removing animation must not remove meaning |
| Privacy surfaces are safe | Lock screen, notification, logging, share/export, deletion | Consent to camera does not authorize incidental household exposure |

## AI and side effects

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| AI labels a selected object | Fixed source fields/images, typed output, edit/reject, provenance | A label is not a verified object category |
| AI summarizes a room | Selected CapturedRoom fields, prompt/context version, privacy review | A summary may expose sensitive home details |
| AI proposes layout | Collision/bounds checks, preview, undo, explicit confirmation | Model output cannot directly commit transforms |
| AI selects fallback | Capability/tracking fixtures, deterministic route policy | Model reasoning should not override device support |
| AI affects saved record | Before/after record, source IDs, user decision, version/migration | Accepted prose does not prove measurement integrity |
| AI triggers export/share/delete | Explicit approval and system route proof | A prompt or tool call is not user authorization |

## Release evidence packet

Record this for every spatial capability:

~~~text
feature:
target/bundle/build:
sdk/deployment target:
device family and exact device:
os version:
framework route:
capability/support checks:
camera permission state:
tracking configuration:
plane/raycast/mesh/occlusion options:
roomplan/object-capture/photogrammetry route:
asset/input-set identifier:
lighting/motion/environment:
tracking state and reason:
state transitions:
accessibility settings:
manual fallback:
ai model/context/version:
proposal/review/undo:
saved/exported/shared data:
privacy retention/deletion:
frame-time/memory/thermal:
archive capabilities/entitlements/resources:
known failures:
claim supported:
claim not yet supported:
~~~

## Claim language

Use language that names the evidence:

- “On the named device and OS, ARWorldTrackingConfiguration produced a raycast result for the declared alignment after camera permission; the app showed the result as a candidate and required placement confirmation.”
- “Scene reconstruction was enabled only after the device support check and was tested on the listed LiDAR device; unsupported devices use the plane/raycast fallback.”
- “RoomPlan produced a CapturedRoom from the named scan, which the user reviewed before saving; the result is treated as an approximate environmental model.”
- “Object Capture completed image capture; PhotogrammetrySession reconstruction was tested separately and the model passed the listed asset review.”
- “The AI proposed an editable label/layout from selected source data; deterministic geometry checks and explicit confirmation preceded saving.”

Avoid:

- “Works on all iPhones.”
- “The room is measured exactly.”
- “The mesh is private” without retention/export evidence.
- “AR is supported” without naming the configuration and device.
- “The AI understood the room” without source/provenance and task evidence.

## Sources

- [ARKit](https://developer.apple.com/documentation/arkit)
- [ARWorldTrackingConfiguration](https://developer.apple.com/documentation/arkit/arworldtrackingconfiguration)
- [Understanding world tracking](https://developer.apple.com/documentation/arkit/understanding-world-tracking)
- [ARRaycastQuery](https://developer.apple.com/documentation/arkit/arraycastquery)
- [Scene reconstruction](https://developer.apple.com/documentation/arkit/arworldtrackingconfiguration/scenereconstruction)
- [Verifying device support and user permission](https://developer.apple.com/documentation/arkit/verifying-device-support-and-user-permission)
- [RealityKit](https://developer.apple.com/documentation/realitykit)
- [RealityView](https://developer.apple.com/documentation/realitykit/realityview)
- [ARView](https://developer.apple.com/documentation/realitykit/arview)
- [Systems](https://developer.apple.com/documentation/realitykit/ecs-systems)
- [AccessibilityComponent](https://developer.apple.com/documentation/realitykit/accessibilitycomponent)
- [RoomPlan](https://developer.apple.com/documentation/roomplan)
- [Scanning the rooms of a single structure](https://developer.apple.com/documentation/roomplan/scanning-the-rooms-of-a-single-structure)
- [RoomCaptureSession](https://developer.apple.com/documentation/roomplan/roomcapturesession)
- [ObjectCaptureSession](https://developer.apple.com/documentation/realitykit/objectcapturesession)
- [ObjectCaptureView](https://developer.apple.com/documentation/realitykit/objectcaptureview)
- [PhotogrammetrySession](https://developer.apple.com/documentation/realitykit/photogrammetrysession)
- [Augmented reality](https://developer.apple.com/design/human-interface-guidelines/augmented-reality)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
