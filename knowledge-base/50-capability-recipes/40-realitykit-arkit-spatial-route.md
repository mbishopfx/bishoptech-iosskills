# RealityKit and ARKit spatial route

## Use this route when

Use this route when an app needs camera-backed placement, scene understanding, room capture, object reconstruction, or a 3D review surface. Start by naming the spatial claim:

| Product claim | Smallest useful route | Proof that is still required |
| --- | --- | --- |
| Place a virtual object on a floor/table | ARWorldTrackingConfiguration + raycast + RealityKit anchor | Physical tracking/placement on the declared device class |
| Keep an object attached to a detected surface | ARSession + plane/anchor lifecycle | Refinement, relocalization, and tracking-loss behavior |
| Occlude virtual content with the room | Scene reconstruction/occlusion semantics when supported | LiDAR/semantic device evidence and degraded fallback |
| Scan a room into editable structure data | RoomPlan | RoomCaptureSession/RoomBuilder/StructureBuilder physical run |
| Make a 3D object from photos | ObjectCaptureSession + PhotogrammetrySession | Capture support, reconstruction resources, asset review |
| Show a 3D scene in SwiftUI | RealityView where supported, or ARView bridge for camera AR | Target-specific compilation and interaction proof |
| Suggest a layout or label | Deterministic spatial data + bounded AI proposal | Source/provenance, editable output, no hidden transform/side effect |

Do not choose Object Capture just because the app displays a 3D model. Do not choose RoomPlan just because the product has a room-themed UI. Bind the framework to a user-visible capability and a device test.

## Target and capability gate

The feature gate should be checked before the entry point appears:

~~~text
deployment target and linked frameworks
  -> device feature support
  -> camera permission
  -> session/configuration availability
  -> model/asset/resource availability
  -> interactive state machine
  -> review and save
~~~

Possible gates include:

- ARWorldTrackingConfiguration.isSupported;
- ARWorldTrackingConfiguration.supportsSceneReconstruction for the requested scene reconstruction option;
- ObjectCaptureSession.isSupported;
- PhotogrammetrySession.isSupported;
- target-specific RealityKit/RealityView availability;
- camera usage description and any additional privacy configuration;
- memory, thermal, storage, and model/resource budget.

The gate should return a typed reason, not only false:

~~~swift
enum SpatialAvailability: Sendable {
    case ready
    case unsupported(String)
    case permissionNeeded
    case permissionDenied
    case resourceUnavailable(String)
}
~~~

Use an unsupported-device route that preserves the core product goal. Examples are a manual floor-plan editor, a photo-based catalog, a 2D room list, or a prebuilt model viewer.

## Route A: camera-backed placement

### Configure

1. Add ARKit and RealityKit to the intended app target.
2. Add NSCameraUsageDescription with an honest, user-facing reason.
3. Check world-tracking support before exposing the AR entry point.
4. Create an ARWorldTrackingConfiguration.
5. Enable only required plane detection, image/object detection, and frame semantics.
6. Run the ARSession directly or through an ARView.
7. Observe camera/tracking state, interruptions, and relocalization.

### Place

1. Convert the user’s touch/point into a raycast query.
2. Choose estimated or existing plane behavior deliberately.
3. Restrict alignment to horizontal/vertical/any according to the feature.
4. Display a candidate indicator.
5. Require an explicit place action.
6. Create an AnchorEntity from the accepted world transform.
7. Add a ModelEntity or loaded hierarchy to the anchor.
8. Attach collision/input/accessibility components only when needed.
9. Save a domain record separate from the Entity object.

### Reconcile

When plane geometry or tracking improves, reconcile the anchor gently. When tracking is limited:

- stop accepting new placements;
- keep existing content visible if the product can explain its stale state;
- show the reason and a move/retry action;
- avoid pretending that a frozen frame is live spatial truth;
- expose reset/relocalize without deleting the saved record unless requested.

## Route B: scene reconstruction and occlusion

Use scene reconstruction only when the app benefits from physical geometry. Check the requested scene reconstruction support first, then configure it together with any plane or people-occlusion semantics the product needs.

Data policy:

- keep the mesh session-local by default;
- retain a derived result only when it is necessary;
- label dimensions as estimates unless the product has stronger evidence;
- make object placement reversible;
- test reflective, transparent, thin, moving, and poorly lit surfaces;
- verify that the fallback does not create a dangerous or misleading interaction.

If the requested device does not support reconstruction, switch to plane/raycast placement or a 2D/screen-space representation. Do not show a disabled “occlusion” badge that implies the feature is running.

## Route C: RoomPlan capture

### Guided system UI

Use RoomCaptureView when the framework’s scanning guidance fits the product. Surround it with a short introduction, privacy statement, room/structure naming, finish controls, and a review screen.

### Custom capture UI

Use RoomCaptureSession when the product needs custom graphics or a multi-stage workflow. Keep capture instructions short and test the session delegate lifecycle. A custom UI must preserve clear progress and stop/cancel behavior.

### Build and merge

For one room:

~~~text
RoomCaptureSession
  -> captured data
  -> RoomBuilder
  -> CapturedRoom
  -> review/export/save
~~~

For multiple rooms:

~~~text
CapturedRoom[room 1...n]
  -> StructureBuilder
  -> CapturedStructure
  -> USD/USDZ or domain export
~~~

Preserve room identity and scan order. A merged structure should still let the person inspect which room produced a wall, opening, object, or dimension. Keep partial captures recoverable if the product supports it.

## Route D: Object Capture and reconstruction

1. Check ObjectCaptureSession.isSupported.
2. Create the capture session only after the gate succeeds.
3. Present ObjectCaptureView or a documented custom capture surface.
4. Show the person the capture state and feedback.
5. Pause/cancel safely.
6. When capture completes, persist the image-set reference and metadata.
7. Check PhotogrammetrySession support and resource limits.
8. Run reconstruction as a separate cancellable operation.
9. Load the output into RealityKit.
10. Review topology, scale, orientation, textures, and privacy before saving/sharing.

Do not mix capture progress with reconstruction progress. A person can finish taking photographs while the model is still not available.

## Route E: RealityKit scene composition

Use a small scene coordinator:

~~~swift
@MainActor
final class SpatialSceneCoordinator {
    var rootAnchor: AnchorEntity?
    var selectedEntityID: String?

    func resetScene() {
        rootAnchor?.removeFromParent()
        rootAnchor = nil
        selectedEntityID = nil
    }
}
~~~

Keep the coordinator responsible for scene lifetime, not business persistence. A SwiftUI model can own the route and pass explicit commands to the coordinator:

~~~text
SwiftUI route state
  -> scene command
  -> RealityKit entity/component mutation
  -> observable scene summary
  -> review/save decision
~~~

Use components for per-entity state and systems for repeated group behavior. Do not use a system as a hidden persistence layer.

## SwiftUI integration choice

### RealityView

Choose RealityView when the intended target supports it and the product needs SwiftUI-owned 3D content. Keep asset loading asynchronous and idempotent. The make phase should establish the scene; update should reconcile changes from state without rebuilding every entity.

### ARView bridge

Choose an ARView UIViewRepresentable when the iOS product needs a camera-backed AR session and direct ARView control. Keep:

- permission and target gating in the feature model;
- ARSession delegate/coordinator lifetime explicit;
- SwiftUI state updates throttled;
- UIKit view creation and teardown symmetric;
- scene entities owned by a coordinator rather than recreated on every SwiftUI update.

Test both orientations and view disappearance. Stop sessions or release subscriptions when the feature no longer owns the camera.

## AI proposal route

Use AI only after a user selects the spatial input:

~~~text
selected captured object/room fields
  -> deterministic validation and source provenance
  -> on-device model proposal
  -> typed editable result
  -> user review
  -> deterministic geometry check
  -> explicit save/place/export/share
~~~

Examples:

- label a selected object;
- summarize a captured room;
- propose a furniture arrangement that passes deterministic collision/bounds checks;
- translate a scan review into a checklist;
- choose between AR and manual fallback based on capability state.

Never let generated text directly set a transform, delete a scan, export a room, or share a photo/mesh. Turn the model result into an approval object with a source ID and schema version.

## Native screen handoff

| Moment | Native surface |
| --- | --- |
| Why camera access is needed | Short intro or permission rationale |
| Looking for a surface | Minimal screen-space instruction |
| Candidate found | Reticle and compact action |
| Object selected | Sheet/inspector for details |
| Scan complete | Review screen with captured data |
| Reconstruction running | Cancellable progress view |
| AI proposal ready | Editable proposal card |
| Save/export/share | Explicit confirmation sheet |

Use Liquid Glass for grouped controls and transient toolbars. Keep the captured scene, room measurements, and model details on readable surfaces with adequate contrast.

## Failure matrix

| Failure | Product response |
| --- | --- |
| Device lacks world tracking | Hide AR entry point or offer manual/2D route |
| Camera denied | Explain limitation and Settings/manual route |
| Tracking limited | Pause placement and explain movement/light fix |
| Plane refines after placement | Subtle correction, preserve intent, record evidence |
| Scene reconstruction unavailable | Use plane/raycast route without claiming occlusion |
| Room scan cancelled | Keep or discard partial data by explicit user choice |
| Multi-room merge fails | Keep individual rooms and offer retry |
| Object Capture unsupported | Offer prebuilt asset or photo/manual route |
| Reconstruction runs out of resources | Save capture set, offer later/Mac route, never lose input silently |
| Asset malformed/oversized | Reject with detail and fallback asset |
| AI proposal fails | Keep original spatial record and manual editing |
| User rejects proposal | No transform/save/export side effect |

## Verification

- Compile every route in the target that will ship.
- Inspect the built target’s capabilities, privacy strings, resources, and supported devices.
- Test at least one supported device and one unsupported or degraded condition.
- Record real ARSession tracking state/reason on failures.
- Test plane refinement, reset, interruption, relocalization, and view teardown.
- Test scene reconstruction/occlusion only on the device classes that advertise support.
- Test RoomPlan single-room and multi-room review/export separately.
- Test Object Capture capture completion and PhotogrammetrySession reconstruction separately.
- Test RealityView and ARView behavior only in the target where each is used.
- Test accessibility through a 2D equivalent, not only labels on the 3D scene.
- Test AI rejection and deterministic geometry checks.
- Do not call a simulator preview or framework import physical-device proof.

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
- [Entity](https://developer.apple.com/documentation/realitykit/entity)
- [Systems](https://developer.apple.com/documentation/realitykit/ecs-systems)
- [RoomPlan](https://developer.apple.com/documentation/roomplan)
- [RoomCaptureView](https://developer.apple.com/documentation/roomplan/roomcaptureview)
- [RoomCaptureSession](https://developer.apple.com/documentation/roomplan/roomcapturesession)
- [Scanning the rooms of a single structure](https://developer.apple.com/documentation/roomplan/scanning-the-rooms-of-a-single-structure)
- [ObjectCaptureSession](https://developer.apple.com/documentation/realitykit/objectcapturesession)
- [ObjectCaptureView](https://developer.apple.com/documentation/realitykit/objectcaptureview)
- [PhotogrammetrySession](https://developer.apple.com/documentation/realitykit/photogrammetrysession)
- [AccessibilityComponent](https://developer.apple.com/documentation/realitykit/accessibilitycomponent)
- [Augmented reality](https://developer.apple.com/design/human-interface-guidelines/augmented-reality)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
