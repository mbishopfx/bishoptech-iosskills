# SwiftUI ARKit and RealityKit spatial-scene review route

Use this route when an iOS app needs camera-backed world tracking, candidate placement, spatial scene understanding, or a RealityKit-rendered 3D task inside a native SwiftUI product shell. It is a decision route, not a symbol dump.

Pair it with [SwiftUI ARKit and RealityKit spatial-scene review](../42-framework-deep-dives/97-swiftui-arkit-realitykit-spatial-scene-review.md), [the spatial-scene design companion](../21-design-deep-dives/125-swiftui-arkit-realitykit-spatial-scene-review-design.md), [the existing ARKit/RealityKit route](40-realitykit-arkit-spatial-route.md), and [the proof matrix](../60-verification/122-swiftui-arkit-realitykit-spatial-scene-review-proof-matrix.md).

## Choose the outcome first

| Product outcome | First route | Do not add |
| --- | --- | --- |
| Preview a 3D asset in a normal app screen | RealityKit or Model3D in a SwiftUI surface | ARKit unless physical-world tracking is required. |
| Place a model on a camera-visible surface | ARWorldTrackingConfiguration, raycast, RealityKit AnchorEntity | Scene reconstruction or AI unless the task needs them. |
| Keep a candidate placement updated while the person moves | ARTrackedRaycast or renderer-specific tracked query | Persistent world maps unless relaunch/resume is a real requirement. |
| Occlude virtual content with estimated geometry | ARWorldTrackingConfiguration scene reconstruction and RealityKit scene understanding | Claiming a complete room scan or safety guarantee. |
| Resume a room-specific scene | ARWorldMap and initialWorldMap | Restoring content before tracking returns to normal. |
| Show a target-specific SwiftUI/RealityKit 3D surface | RealityView when the selected target supports it | Treating a visionOS-oriented route as iOS camera AR proof. |
| Propose a label or action from a scene | Source-linked local AI proposal over a typed snapshot | Letting generated text commit placement or physical effects. |
| Need a custom camera/rendering pipeline | ARSession plus a custom renderer or Metal | Using ARView features that the custom renderer does not own. |

The simplest architecture is usually SwiftUI plus ARView for iOS camera AR, with a coordinator that owns ARSession callbacks and a scene adapter that reconciles RealityKit entities.

## Route map

~~~text
product task
  -> target/device/configuration check
  -> camera explanation and authorization
  -> renderer/session owner
  -> ARWorldTrackingConfiguration
  -> tracking-state projection
  -> raycast/plane/mesh observation
  -> typed candidate
  -> RealityKit scene projection
  -> SwiftUI review and accessible command path
  -> optional local AI proposal
  -> deterministic validation
  -> explicit commit
  -> reset/undo/persistence/release proof
~~~

The renderer should not decide business truth. The SwiftUI view should not own camera frames. The model should not decide whether an observation is safe to act on.

## Route A: camera-backed iOS placement

### A1. Confirm target and permission

Before presenting the start action:

- confirm the app target links ARKit and RealityKit;
- confirm the deployment target and selected SDK;
- test ARWorldTrackingConfiguration.isSupported;
- test additional support before enabling scene reconstruction or a specialized configuration;
- include NSCameraUsageDescription;
- decide whether AR is required or optional for distribution;
- show the reason for camera access in the app’s own copy.

On denial or revocation, keep a working non-AR path. Do not repeatedly trigger the system prompt.

### A2. Create one owner

A feature model or coordinator owns:

- the ARView instance or custom renderer;
- the ARSession and delegate queue;
- a session generation;
- current tracking state;
- current candidate and source revision;
- tracked-raycast handles;
- scene subscriptions;
- cancellation and teardown.

Use a single owner per active AR feature. A parent SwiftUI view can hold the model while the UIViewRepresentable wrapper only creates, updates, and dismantles the renderer.

### A3. Run a configuration

Start with the smallest configuration:

~~~swift
let configuration = ARWorldTrackingConfiguration()
configuration.planeDetection = [.horizontal, .vertical]

if ARWorldTrackingConfiguration.supportsSceneReconstruction(.meshWithClassification) {
    configuration.sceneReconstruction = .meshWithClassification
}

arView.session.run(configuration, options: [.resetTracking, .removeExistingAnchors])
~~~

This is a compile-oriented sketch. Verify the exact availability and target behavior in the selected SDK. Only enable scene reconstruction when the product has a real use for the estimated mesh or classification. If support is absent, omit the option and change the UI rather than leaving an “occlusion enabled” badge.

### A4. Project tracking state

The session delegate should translate ARCamera.TrackingState into an app enum:

~~~swift
enum SpatialTrackingState: Equatable, Sendable {
    case starting
    case limited(String)
    case normal
    case interrupted
    case relocalizing
    case unavailable
    case failed(String)
}
~~~

Keep the associated reason, session identifier, frame timestamp, and a monotonic revision in the snapshot. Do not store only a localized string; the UI copy may change while the state machine remains stable.

When state is limited or unavailable:

- stop enabling new placement commits;
- mark the focus result stale;
- hide or soften virtual content if its position is misleading;
- tell the user the next recovery action;
- preserve the draft if it is safe;
- allow reset after relocalization has exceeded the product’s wait policy.

### A5. Produce a raycast candidate

A one-time candidate:

~~~swift
guard let query = arView.makeRaycastQuery(
    from: screenPoint,
    allowing: .estimatedPlane,
    alignment: .horizontal
) else {
    return
}

guard let result = arView.session.raycast(query).first else {
    return
}

let candidate = PlacementCandidate(
    sessionID: arView.session.identifier,
    frameTimestamp: currentFrameTimestamp,
    target: .estimatedPlane,
    alignment: .horizontal,
    worldTransform: result.worldTransform
)
~~~

This snippet is intentionally incomplete: the app must obtain the current frame timestamp, validate tracking state, handle no-result and stale-result cases, and decide whether the target is suitable. Prefer an existing-plane query when the task requires a surface that has already been observed; use estimated planes only when the UI says the result is provisional.

For a tracked preview:

- keep the ARTrackedRaycast handle in the coordinator;
- stop it when the object is placed, the gesture ends, the session is interrupted, or the view disappears;
- update presentation smoothly only if smoothing does not hide a meaningful correction;
- never convert the preview transform directly into a committed domain record.

## Route B: RealityKit scene projection

RealityKit’s scene graph should be a projection of app-owned state:

~~~text
PlacementRecord
  -> SceneProjectionCommand
  -> AnchorEntity
  -> ModelEntity and child entities
  -> accessibility component
  -> collision/input components when needed
  -> rendered scene
~~~

Create an AnchorEntity for the accepted or previewed world transform, add the model as a child, and add the anchor to the renderer’s scene. Keep the record’s stable ID and source revision outside the entity. Entity names are useful for debugging and selection but are not an authentication mechanism.

If the anchor moves as tracking refines:

1. update the entity projection;
2. update the source/freshness label;
3. mark any AI proposal derived from the old transform stale;
4. leave the user’s saved record untouched until they review or explicitly resave.

Do not rebuild every entity on each SwiftUI update. Reconcile by stable app-owned ID and remove only entities that the projection no longer owns.

## Route C: scene reconstruction and occlusion

Use scene reconstruction only after a device-support check and only for a declared product need such as:

- occluding a model behind estimated room geometry;
- obtaining a more useful placement candidate;
- allowing a virtual object to interact with an estimated mesh;
- classifying a limited set of mesh faces for a review surface.

A mesh is an estimate. It can be incomplete, refined, noisy, or unavailable. Use state such as meshUnavailable, meshUpdating, meshEstimated, and meshReady rather than a Boolean called roomMapped.

If the device cannot provide the requested reconstruction:

- fall back to plane/raycast placement;
- remove mesh-specific controls and copy;
- do not show a disabled “occlusion” control that implies the feature is active;
- keep a clear 2D or non-AR route.

Occlusion and mesh interaction need physical-device proof in the target conditions. A simulator or static mesh fixture can prove scene composition and state handling, not live sensor coverage or physical occlusion fidelity.

## Route D: persistence and relocalization

Persist only what the product needs. A record might contain:

~~~swift
struct PlacementRecord: Codable, Identifiable, Sendable {
    var id: UUID
    var assetID: String
    var userLabel: String?
    var savedSessionID: UUID
    var savedWorldMapRevision: Int
    var status: Status
}
~~~

Do not persist a raw transform without the coordinate-space and world-map policy that gives it meaning. If using ARWorldMap:

1. acquire the map through the selected ARSession API;
2. save it with a version and deletion policy;
3. store only the minimum app-owned records needed to recreate content;
4. provide initialWorldMap on a later run when appropriate;
5. show relocalizing state while ARKit attempts reconciliation;
6. restore content only after normal tracking;
7. offer reset if relocalization does not converge;
8. mark the old record stale if the person rejects the new position.

World maps and room-related data are sensitive. Avoid cloud sync by default. If sync is necessary, document retention, encryption, account scope, conflict resolution, and deletion.

## Route E: SwiftUI and RealityView boundary

For iOS camera AR, host ARView in SwiftUI with UIViewRepresentable:

~~~swift
struct CameraSceneRepresentable: UIViewRepresentable {
    @ObservedObject var model: SpatialSceneModel

    func makeCoordinator() -> Coordinator {
        Coordinator(model: model)
    }

    func makeUIView(context: Context) -> ARView {
        let view = ARView(frame: .zero)
        context.coordinator.attach(to: view)
        return view
    }

    func updateUIView(_ view: ARView, context: Context) {
        context.coordinator.reconcileScene(in: view)
    }

    static func dismantleUIView(_ view: ARView, coordinator: Coordinator) {
        coordinator.stop(view)
    }
}
~~~

The exact ownership model can vary, but keep these responsibilities visible:

- SwiftUI: navigation, status copy, review, accessibility, and task commands;
- coordinator: renderer/session delegate and lifecycle;
- scene adapter: entity/component projection;
- domain model: accepted placement and persistence;
- AI adapter: typed proposal generation and stale-result cancellation.

Use RealityView only for the target/platform where it is available and where its scene model is the right fit. A 3D RealityView preview does not prove camera permission, touch raycasting, iOS ARWorldTrackingConfiguration, or a physical iPhone session.

## Route F: local AI review

Turn the current spatial state into a bounded input:

~~~swift
struct SpatialProposalInput: Sendable {
    var sourceRevision: Int
    var sessionID: UUID
    var frameTimestamp: TimeInterval
    var trackingState: SpatialTrackingState
    var observationSummary: String
    var userIntent: String
}
~~~

The model may propose a label, explanation, or next action. The adapter must:

- capture the input revision;
- cancel or supersede old requests;
- reject output for a different session or user intent;
- show the source and limitations;
- require user review;
- send only a validated domain command to the commit layer.

Do not pass raw camera frames, full room meshes, or unnecessary spatial history to a model. Prefer a compact normalized summary when the product task allows it. If AI is unavailable, the deterministic placement and review path should remain usable.

## Route G: SwiftUI native shell

Use a state-driven shell:

~~~text
NavigationStack
  -> CameraARView
  -> tracking/status overlay
  -> bottom functional tool group
  -> selection/review sheet
  -> explicit domain action
~~~

Suggested view state:

~~~swift
struct SpatialSceneViewState: Equatable, Sendable {
    var tracking: SpatialTrackingState
    var candidate: PlacementCandidate?
    var selectedRecordID: UUID?
    var proposal: SpatialProposal?
    var isReviewPresented: Bool
    var canCommit: Bool
}
~~~

Derive canCommit from current state, not from a button tap. It should require a current candidate, a compatible target/alignment, a usable tracking state, a current session generation, and the appropriate user confirmation. If a physical or external side effect exists, add the domain-specific validation.

Use Liquid Glass for the functional layer and a standard fallback when readability or target availability requires it. Keep camera content outside the control material.

## Failure and fallback matrix

| Failure | Detect | Recovery |
| --- | --- | --- |
| Camera denied | Authorization state or session failure | Explain Settings and offer non-AR path. |
| Unsupported configuration | isSupported/supportsSceneReconstruction | Hide or replace the route. |
| Tracking initializing | limited(initializing) | Coach movement; disable commit. |
| Insufficient features | limited(insufficientFeatures) | Ask for textured, lit surfaces. |
| Excessive motion | limited(excessiveMotion) | Ask the person to slow down. |
| No raycast result | empty results | Retarget or change alignment. |
| Stale candidate | frame/session revision mismatch | Clear preview and reacquire. |
| Session interrupted | observer callback | Mark content stale and preserve draft. |
| Relocalization stuck | limited(relocalizing) beyond timeout | Offer reset and explain consequence. |
| Mesh unsupported | support check false | Use plane/raycast fallback. |
| Asset load failed | RealityKit load error | Show placeholder/error and retry. |
| AI unavailable | model readiness/error | Use manual label/action flow. |
| View teardown | dismantle/background/cancel | stop raycasts, subscriptions, session work, and stale callbacks. |

## Target configuration checklist

Before the first compile:

- Add ARKit and RealityKit to the intended app target.
- Confirm the deployment target and SDK availability.
- Add NSCameraUsageDescription.
- Decide whether UIRequiredDeviceCapabilities should require ARKit.
- Keep device-specific features behind support checks.
- Keep ARView bridge code in an iOS target boundary.
- Keep RealityView code in the target where it compiles and is intended.
- Add model assets and verify their target membership.
- Decide whether world maps, meshes, or snapshots are ephemeral or persisted.
- Define privacy and deletion copy.
- Define the non-AR route.
- Set up preview fixtures with no camera dependency.
- Plan signed-device and archive proof before calling the route complete.

## Proof handoff

Use the [spatial proof matrix](../60-verification/122-swiftui-arkit-realitykit-spatial-scene-review-proof-matrix.md) for:

- target and source availability;
- camera permission;
- session/tracking state;
- raycast candidate and no-result handling;
- entity/anchor projection;
- scene reconstruction and occlusion;
- interruptions and relocalization;
- accessibility and alternate input;
- performance/thermal;
- archive, TestFlight, and release configuration.

A recipe that compiles is the beginning of the route. It is not evidence that the camera, sensors, world map, mesh, entity interaction, privacy policy, or release target behaves correctly.

## Sources

- [ARKit](https://developer.apple.com/documentation/arkit)
- [ARKit in iOS](https://developer.apple.com/documentation/arkit/arkit-in-ios)
- [ARSession](https://developer.apple.com/documentation/arkit/arsession)
- [ARSessionDelegate](https://developer.apple.com/documentation/arkit/arsessiondelegate)
- [ARCamera](https://developer.apple.com/documentation/arkit/arcamera)
- [Managing Session Life Cycle and Tracking Quality](https://developer.apple.com/documentation/arkit/managing-session-life-cycle-and-tracking-quality)
- [Verifying Device Support and User Permission](https://developer.apple.com/documentation/arkit/verifying-device-support-and-user-permission)
- [ARWorldTrackingConfiguration](https://developer.apple.com/documentation/arkit/arworldtrackingconfiguration)
- [sceneReconstruction](https://developer.apple.com/documentation/arkit/arworldtrackingconfiguration/scenereconstruction)
- [ARWorldMap](https://developer.apple.com/documentation/arkit/arworldmap)
- [ARAnchor](https://developer.apple.com/documentation/arkit/aranchor)
- [ARRaycastQuery](https://developer.apple.com/documentation/arkit/arraycastquery)
- [ARRaycastResult](https://developer.apple.com/documentation/arkit/arraycastresult)
- [ARTrackedRaycast](https://developer.apple.com/documentation/arkit/artrackedraycast)
- [Placing objects and handling 3D interaction](https://developer.apple.com/documentation/arkit/placing-objects-and-handling-3d-interaction)
- [RealityKit](https://developer.apple.com/documentation/realitykit)
- [ARView](https://developer.apple.com/documentation/realitykit/arview)
- [Entity](https://developer.apple.com/documentation/realitykit/entity)
- [AnchorEntity](https://developer.apple.com/documentation/realitykit/anchorentity)
- [ModelEntity](https://developer.apple.com/documentation/realitykit/modelentity)
- [Component](https://developer.apple.com/documentation/realitykit/component)
- [System](https://developer.apple.com/documentation/realitykit/system)
- [Scene](https://developer.apple.com/documentation/realitykit/scene)
- [RealityView](https://developer.apple.com/documentation/realitykit/realityview)
- [Understanding the RealityKit modular architecture](https://developer.apple.com/documentation/visionos/understanding-the-realitykit-modular-architecture)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [AccessibilityComponent](https://developer.apple.com/documentation/realitykit/accessibilitycomponent)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
