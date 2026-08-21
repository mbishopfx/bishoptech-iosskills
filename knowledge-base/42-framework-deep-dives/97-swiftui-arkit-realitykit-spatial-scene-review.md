# SwiftUI ARKit and RealityKit spatial-scene review

This deep dive defines the iOS boundary between a SwiftUI product shell, an ARKit camera and motion session, and a RealityKit scene. It focuses on a source-linked spatial scene that can be reviewed, recovered, and proven on a named physical device. It is intentionally distinct from the existing [RealityKit, ARKit, and spatial experiences](04-realitykit-arkit-and-spatial.md), [RealityKit/ARKit spatial route](../50-capability-recipes/40-realitykit-arkit-spatial-route.md), [spatial scene and occlusion design](../21-design-deep-dives/37-spatial-scene-and-occlusion-native-surfaces.md), and [Nearby Interaction spatial-peer review](96-swiftui-nearby-interaction-spatial-peer-review.md): this page treats a live AR session as a stateful, privacy-sensitive observation pipeline whose rendered entities and AI proposals must not become physical-world truth by implication.

## The composed route

Use the smallest route that satisfies the product outcome:

~~~text
SwiftUI task and navigation shell
  -> target and device capability gate
  -> camera privacy explanation and authorization
  -> ARSession ownership
  -> ARConfiguration selection
  -> ARFrame and ARCamera tracking state
  -> optional plane, raycast, image, body, or scene-reconstruction observation
  -> typed scene snapshot with source session and revision
  -> RealityKit scene adapter
  -> AnchorEntity and Entity graph
  -> user review and explicit placement/edit action
  -> optional on-device AI proposal
  -> deterministic validation and domain commit
  -> accessibility, performance, physical-device, archive, and release evidence
~~~

ARKit coordinates motion sensing, camera access, and image analysis through ARSession. A standard renderer such as ARView can own or expose a session, while a custom renderer can instantiate one directly. RealityKit is the scene and entity layer; it does not turn a camera frame, plane, mesh, anchor, or raycast into a verified measurement of the world.

Keep these authorities separate:

| Fact | Framework or owner | What the app may claim |
| --- | --- | --- |
| ARKit configuration support | ARConfiguration subclass and the selected device | This device can attempt the selected AR route. |
| Camera permission | iOS privacy system | The app may use camera-backed AR after consent. |
| Session state | ARSession, ARSessionDelegate, ARSessionObserver | The current session reports a tracking and interruption state. |
| Camera pose | ARFrame and ARCamera | ARKit produced a pose estimate for that frame. |
| Plane/raycast/mesh result | ARKit environmental analysis | A candidate surface or estimated scene feature was returned. |
| Anchor identity | ARAnchor or RealityKit AnchorEntity | Content is attached to a framework-managed session/scene anchor. |
| Entity graph | RealityKit scene adapter | The app’s virtual content is currently represented in the renderer. |
| AI output | Foundation Models or another local model | The model proposed text, a label, or a next step from named input. |
| Product truth | App-owned validation and persistence | The user or deterministic domain logic accepted a resulting action. |

A green placement badge, a stable-looking mesh, or a confident AI sentence cannot fill a missing permission, unsupported feature, stale tracking state, or user decision.

## Target, device, and privacy gates

ARKit requires an iOS device with an appropriate processor and camera permission. The exact feature set remains target- and device-dependent. Apple’s device-support guidance distinguishes a primary AR feature from an optional AR feature:

- If AR is fundamental to the app, declare the appropriate required device capability so incompatible devices are not presented as supported.
- If AR is an optional feature, test the selected ARConfiguration subclass’s isSupported value before presenting the entry point.
- For face-tracking or another specialized configuration, check that configuration’s support rather than inferring support from the existence of ARKit.
- Add NSCameraUsageDescription with a concrete explanation of the camera-backed task.
- Treat denied, restricted, and later-revoked camera access as normal recoverable states.
- Do not request or retain camera frames merely to decorate an otherwise non-AR screen.
- Keep camera, microphone, location, Bluetooth, local-network, and face-data explanations separate when the route uses more than one protected resource.

A capability matrix should be explicit:

| Gate | Example state | User-facing consequence |
| --- | --- | --- |
| ARKit available | available / unavailable | Offer AR or a non-AR route. |
| Selected configuration supported | supported / unsupported | Explain the fallback before starting a session. |
| Camera authorization | notDetermined / authorized / denied / restricted | Explain, request, or link to Settings. |
| Session running | stopped / starting / running / paused | Control renderer ownership and copy. |
| Tracking quality | not available / limited(reason) / normal | Gate placement and describe the next recovery action. |
| Plane detection | enabled / unavailable / refining | Show candidate surface state, never a guaranteed surface. |
| Scene reconstruction | supported / unsupported / unavailable now | Keep occlusion and mesh controls truthful. |
| Anchor persistence | none / saving / saved / relocalizing / failed | Do not show old content as current until tracking is normal. |
| Renderer | ARView / custom renderer / target-specific RealityView | Keep target and interaction assumptions visible. |
| AI availability | ready / unavailable / loading / failed | Keep the deterministic scene task usable without AI. |

The app should decide whether to hide, disable, or explain an unavailable entry point. Hiding a feature can be appropriate when it is irrelevant; a visible fallback is better when the person has already started a task.

## ARSession ownership and lifecycle

Keep one explicit owner for an ARSession in a feature coordinator or renderer adapter. A SwiftUI row, transient sheet, or view callback should not create a new session on every body evaluation. The owner should:

1. Create or receive the session from the selected renderer.
2. Assign the session delegate and a deliberate delegate queue.
3. Build the selected configuration only after support and permission checks.
4. Run the session with documented run options.
5. Project delegate callbacks into immutable, app-owned snapshots.
6. Stop, pause, cancel, or detach the session when the feature leaves scope.
7. Ignore callbacks from an old session generation after replacement or teardown.

A useful state model is:

| State | Meaning | Allowed UI |
| --- | --- | --- |
| idle | No session owns the camera. | Explain the task and start route. |
| explainingPermission | The app explains why camera access is needed. | Show consent context and cancel. |
| requestingPermission | iOS is presenting camera consent. | Avoid duplicate prompts. |
| unsupported | Device or configuration cannot run. | Provide the smallest non-AR route. |
| starting | Configuration was accepted; ARKit is gathering data. | Show guidance; do not allow placement. |
| limited(initializing) | Camera or motion data is not yet sufficient. | Coaching and retry; no committed placement. |
| runningLimited | A pose exists but quality is questionable. | Keep content provisional and explain the reason. |
| runningNormal | ARKit reports normal tracking for the frame. | Allow the declared interactions, still with review. |
| interrupted | The session cannot track while interrupted. | Hide or mark content stale; preserve draft intent. |
| relocalizing | ARKit is attempting to reconcile the previous world. | Show recovery guidance and an eventual reset action. |
| paused | The owner intentionally stopped processing. | Do not imply live spatial state. |
| stopping | Teardown is in flight. | Disable side effects; drain or cancel work. |
| failed | The route needs a new session or fallback. | Explain reason and offer recovery. |

ARSession delegate callbacks may arrive on the configured delegate queue. Do not mutate SwiftUI state directly from an arbitrary callback queue. Capture a session generation and frame revision, then hop to the main actor only for the small immutable state update that the view needs.

Use a session state object rather than booleans such as isReady and isTracking. A boolean cannot express that a session is running but limited because of insufficient features, or that an old result arrived after a new session was started.

## Tracking quality is a first-class product state

ARCamera exposes the tracking state associated with each ARFrame. The important categories are:

- notAvailable: the camera position is not available.
- limited(initializing): ARKit is gathering enough camera and motion data.
- limited(insufficientFeatures): the view lacks enough recognizable features.
- limited(excessiveMotion): device motion is too fast for reliable image-based tracking.
- limited(relocalizing): ARKit is attempting to recover an interrupted or saved world.
- normal: camera position tracking is providing optimal results for the current frame.

When tracking is limited, features that depend on mapping the local environment may not produce usable plane anchors or hit-test results. The UI should name the reason in plain language:

| Framework reason | Useful guidance |
| --- | --- |
| initializing | Move the device slowly and show more of the room. |
| insufficientFeatures | Aim at textured surfaces rather than a blank wall or dark area. |
| excessiveMotion | Slow the movement and keep the target in view. |
| relocalizing | Return near the previous viewpoint or reset the session. |
| notAvailable | Stop claiming live tracking and offer a fallback. |

Relocalization is not instant truth restoration. Apple documents that the device may need to return near the prior position and orientation. If the environment changed or the device moved elsewhere, relocalization can remain limited indefinitely. Provide a user-visible reset path after a bounded period. On reset, clear or version the previous placement draft deliberately; do not silently keep a transform that belongs to an unknown coordinate system.

Only promote a placement candidate after the current frame is usable, the selected query returned a result, the target alignment is acceptable, and the person confirms the action. Even in normal tracking, a result remains a framework observation with environmental limitations.

## Configuration and environmental analysis

ARWorldTrackingConfiguration tracks device movement with six degrees of freedom and is the common rear-camera route for placing content in the world. Choose its features by product need:

| Feature | What it contributes | Boundary |
| --- | --- | --- |
| Plane detection | Candidate horizontal or vertical surfaces. | Plane refinement and tracking quality affect results. |
| Raycasting | A screen point mapped to a candidate real-world intersection. | Query target, alignment, tracking, and lighting matter. |
| Initial world map | A saved map that ARKit can attempt to reconcile. | Relocalization must succeed before restoring content as current. |
| Scene reconstruction | A polygonal mesh estimate of the surrounding environment. | Check support first; mesh is an estimate, not a survey. |
| People occlusion | Occlusion behavior based on supported frame semantics. | Camera/privacy/device support and scene conditions apply. |
| Image/object detection | Anchors for recognized reference content. | Detection is not identity or authenticity. |

Before enabling scene reconstruction, call the support check for the requested mode. Apple describes the resulting mesh as an estimate of the physical environment. Plane detection can inform the mesh, and people occlusion can adjust it for detected people. The UI should say “estimated scene mesh” or “occlusion available” rather than “the room is mapped” unless the product has a separate, independently validated claim.

Do not retain or upload raw meshes, camera frames, world maps, or face/body observations by default. These can expose private spaces, routines, or people. If persistence is necessary, state what is saved, why, how long it lives, where it goes, and how the person deletes it.

## Raycasts, tracked raycasts, and placement

A raycast starts from a screen point and asks ARKit for real-world intersections matching a target and alignment. An ARRaycastResult includes a world transform and information about the target/alignment. The transform is a placement candidate, not proof that the surface is safe, stable, owned by the user, or suitable for the intended physical action.

Separate three interaction phases:

1. Preview: a focus indicator follows a current or tracked result.
2. Candidate: the app records the result’s session ID, frame timestamp, query target/alignment, and feature state.
3. Commit: the person confirms after the app validates freshness, scale, orientation, supported target, and current tracking.

Use a one-time raycast for a transient gesture such as dragging. Use a tracked raycast only when the product needs ARKit to update a placement preview as the scene understanding changes. Stop the tracked raycast when the object is placed, the gesture ends, the session is interrupted, or the view is torn down.

Avoid these common errors:

- treating an empty result as a floor at zero height;
- using estimated planes without labeling the result as estimated;
- keeping the last transform visible as if it were current after tracking becomes limited;
- accepting a vertical result for a product that needs a horizontal support surface;
- converting a screen point with a stale camera transform;
- placing an entity before ARKit has reached a usable tracking state;
- using hit-test success as proof of a real-world object’s identity or load-bearing capacity.

## Anchors and persistent worlds

ARAnchor identifies a position and orientation in the physical environment for an AR session. Its transform is relative to the session’s world coordinate space, and its session identifier matters when diagnosing stale or cross-session data. Anchors can help ARKit optimize tracking around their locations, but an anchor does not guarantee that the same physical item still exists.

RealityKit’s AnchorEntity attaches entity content to a scene. RealityKit may move an anchor entity as the scene updates, and an anchor target may not appear if the required target is never detected. Therefore:

- keep an app-owned placement record separate from the live AnchorEntity;
- keep an anchor/session generation on every scene projection;
- reconcile anchor updates on the renderer’s scene adapter;
- remove or mark content stale when the session no longer owns the anchor;
- never use a raw anchor identifier as a verified product identity;
- preserve an explicit user decision if a relocalized anchor changes position;
- allow reset and undo without deleting the domain record unless the person asks.

ARWorldMap can persist information needed to resume a session. A saved map includes anchors, and a later run can use initialWorldMap to attempt relocalization. The product should restore virtual content only after ARKit reports normal tracking for the current session. A saved map is a private environmental artifact; protect it like other sensitive spatial data and provide deletion.

## RealityKit entity and component ownership

RealityKit uses an entity-component-system architecture:

- Entity is the scene element and hierarchy node.
- AnchorEntity attaches content to an anchor target.
- ModelEntity or a custom entity supplies visible content.
- Components hold modular appearance, transform, collision, accessibility, or behavior state.
- Systems implement recurring behavior over entities with matching components.
- Scene owns anchors, subscriptions, and the renderer’s runtime graph.

Keep app state and entity state separate. The app-owned model should contain stable IDs, user intent, source revision, selected asset, placement status, and commit state. The entity graph should contain the current rendering projection. A SwiftUI update should reconcile the projection idempotently; it should not recreate the whole hierarchy on every state change.

A useful adapter boundary is:

~~~text
ARFrame/tracking snapshot
  -> SpatialObservationStore
  -> validated PlacementCandidate
  -> SceneProjectionCommand
  -> RealityKit AnchorEntity/Entity mutation
  -> rendered result
~~~

Do not attach domain truth directly to a transient ModelEntity. If the user deletes a rendered entity, the app must decide whether that means canceling a draft, hiding a projection, or deleting a persisted record.

AnchorEntity may move when tracking refines. Any label, callout, or SwiftUI attachment that describes its location should follow the same entity transform and carry a freshness/state label. A screen-space panel can show the selected object’s metadata without pretending that the panel itself is spatially anchored.

## ARView, SwiftUI, and RealityView

On iOS camera-backed AR, ARView is a RealityKit view with an AR session and scene. A SwiftUI app can host it through UIViewRepresentable, with a coordinator that owns renderer/session delegate lifetime. Keep the wrapper thin; place authorization, configuration, state projection, and teardown in the coordinator or feature model.

Use RealityView only when the selected target and scene model support it. Apple’s SwiftUI/RealityKit guidance is target-specific and includes visionOS-oriented spatial composition. A RealityView preview or a successful 3D scene render is not proof that the iOS camera AR session, world tracking, touch raycasts, or physical-device behavior is available. Make the target explicit in the route table.

| Product need | Preferred boundary | Proof required |
| --- | --- | --- |
| Camera-backed iPhone/iPad AR | SwiftUI shell plus ARView or a custom AR renderer | Physical camera permission, ARSession tracking, raycast/anchor behavior, interruption and release target. |
| Bounded 3D content in a target that supports RealityView | SwiftUI plus RealityView | Named target compilation, asset loading, interaction, accessibility, and target-specific runtime. |
| Custom metal renderer | ARSession plus Metal | Session delegate/frame timing, camera coordinate conversion, GPU frame budget, physical device. |
| Non-AR 3D preview | RealityKit or Model3D without ARSession | Asset/resource loading and 3D interaction; do not call it world tracking. |

Do not let a UIKit bridge become a dumping ground. The SwiftUI shell owns navigation, task state, accessible commands, and recovery copy. The renderer owns frame and entity lifetimes. The domain layer owns accepted placements and side effects.

## Local AI proposals over spatial observations

On-device AI can summarize a named scene snapshot, suggest an object label, draft a placement instruction, or propose a next step. It cannot supply missing ARKit tracking, authenticate an object, prove a surface is safe, or commit a physical action.

Give every proposal an input envelope:

| Field | Example |
| --- | --- |
| sceneRevision | Monotonic app-owned revision. |
| sessionIdentifier | Current ARSession identifier. |
| frameTimestamp | Time of the source ARFrame. |
| trackingState | normal or limited with reason. |
| observationKind | raycast, plane, mesh, image, or user-selected entity. |
| target/alignment | Query constraints used. |
| anchorIdentifier | Optional current anchor reference. |
| userIntent | The task the person explicitly selected. |
| retention | Whether the snapshot is ephemeral or saved. |

The proposal is stale if the session changes, the revision changes, tracking becomes unavailable, the anchor is removed, or the user changes intent. Show “Suggested from the last usable scan” instead of silently applying a stale answer. Keep the commit path deterministic:

~~~text
framework observation
  -> normalized snapshot
  -> optional model proposal
  -> visible source and limitations
  -> user review
  -> deterministic validation
  -> explicit app-owned commit
~~~

A generated instruction such as “place this on the table” is not a table detector with legal, construction, medical, or safety authority. If the app’s outcome could cause harm or a physical side effect, require a stronger domain validation path and a confirmation that names the concrete action.

## Liquid Glass belongs to the functional layer

The camera and reconstructed scene are content. Liquid Glass should support the app’s functional layer: navigation, tool groups, placement controls, status, recovery, and review. Keep the scene visible and keep uncertain observations legible.

Use a compact control hierarchy:

- Top bar: exit, privacy/status, and target/task context.
- Spatial status card: tracking state, freshness, and the next recovery action.
- Functional tools: scan, retarget, undo, reset, confirm, and accessibility alternative.
- Review sheet: selected object, source revision, AI proposal, limitations, and commit.
- Secondary detail: optional measurement or mesh metadata, never the only indication of state.

Avoid a full-screen translucent coating over camera content. Do not use blur, shine, or motion as the only state signal. Test Reduce Transparency, increased contrast, Dynamic Type, Reduce Motion, VoiceOver, and light/dark appearance. If the device cannot support a glass effect or the surface becomes unreadable over the scene, use a standard opaque or material-backed control group.

## Accessibility and alternate input

Spatial content needs a non-spatial task path. Provide:

- a list or outline of detected/placed items;
- a selected-item summary with label, state, source time, and available actions;
- semantic buttons for place, move, remove, retry, reset, and confirm;
- VoiceOver labels, values, traits, custom actions, and a meaningful order;
- Dynamic Type layouts that do not clip recovery or confirmation copy;
- Reduce Motion behavior that removes unnecessary entity animation and arrow motion;
- keyboard, pointer, switch, and Voice Control paths where the target supports them;
- a 2D preview or guided placement fallback when a person cannot use camera movement.

RealityKit’s AccessibilityComponent can expose an entity as an accessibility element and provide label, value, traits, custom actions, and custom content. Keep those values synchronized with the app-owned state rather than a one-time asset name. A VoiceOver label such as “chair” is not proof that ARKit identified a chair; say “candidate: chair” when the label is a model proposal or classification.

## Privacy, energy, and frame discipline

Camera AR is high-sensitivity and resource-intensive. The route should:

- start the camera only inside the user-approved task;
- stop or pause the session when the feature leaves scope;
- avoid logging raw frames, world maps, meshes, or face/body data;
- keep frame processing bounded and discard stale work;
- cap entity counts, mesh detail, and expensive material effects;
- avoid doing model inference on every frame without a measured reason;
- record only the minimum source metadata needed to reproduce a decision;
- redact identifiers and spatial data from diagnostics;
- test thermal and battery behavior on a representative device, not only the newest phone;
- keep a non-camera path for unsupported or denied states.

A renderer preview, stable 60 FPS on one device, or short debug run is not a universal frame or thermal claim. Capture the device, OS, build configuration, scene size, asset set, camera mode, and duration for any performance conclusion.

## Proof boundary

Use the [ARKit/RealityKit spatial proof matrix](../60-verification/122-swiftui-arkit-realitykit-spatial-scene-review-proof-matrix.md) and [compile-oriented recipes](../70-code-recipes/140-swiftui-arkit-realitykit-spatial-scene-review-recipes.md) to record evidence separately:

- source and availability: official API and target notes;
- compile: selected SDK, deployment target, target membership, Info.plist;
- preview/simulator: SwiftUI layout, state copy, fallback, and non-camera 3D content;
- signed physical device: camera consent, tracking states, raycast, anchors, scene reconstruction, interruption, relocalization, and input;
- performance: frame time, memory, thermal, battery, and asset/mesh conditions;
- system/release: archive, entitlements, privacy strings, TestFlight, and release configuration.

No documentation page, code snippet, simulator scene, or AI proposal is a substitute for physical AR evidence.

## Sources

- [ARKit](https://developer.apple.com/documentation/arkit)
- [ARKit in iOS](https://developer.apple.com/documentation/arkit/arkit-in-ios)
- [ARSession](https://developer.apple.com/documentation/arkit/arsession)
- [ARSessionDelegate](https://developer.apple.com/documentation/arkit/arsessiondelegate)
- [ARCamera](https://developer.apple.com/documentation/arkit/arcamera)
- [ARCamera.TrackingState](https://developer.apple.com/documentation/arkit/arcamera/trackingstate-swift.enum)
- [Managing Session Life Cycle and Tracking Quality](https://developer.apple.com/documentation/arkit/managing-session-life-cycle-and-tracking-quality)
- [Verifying Device Support and User Permission](https://developer.apple.com/documentation/arkit/verifying-device-support-and-user-permission)
- [ARConfiguration](https://developer.apple.com/documentation/arkit/arconfiguration)
- [ARWorldTrackingConfiguration](https://developer.apple.com/documentation/arkit/arworldtrackingconfiguration)
- [sceneReconstruction](https://developer.apple.com/documentation/arkit/arworldtrackingconfiguration/scenereconstruction)
- [ARWorldMap](https://developer.apple.com/documentation/arkit/arworldmap)
- [ARAnchor](https://developer.apple.com/documentation/arkit/aranchor)
- [ARPlaneAnchor](https://developer.apple.com/documentation/arkit/arplaneanchor)
- [ARRaycastQuery](https://developer.apple.com/documentation/arkit/arraycastquery)
- [ARRaycastResult](https://developer.apple.com/documentation/arkit/arraycastresult)
- [ARTrackedRaycast](https://developer.apple.com/documentation/arkit/artrackedraycast)
- [Placing objects and handling 3D interaction](https://developer.apple.com/documentation/arkit/placing-objects-and-handling-3d-interaction)
- [Visualizing and interacting with a reconstructed scene](https://developer.apple.com/documentation/arkit/visualizing-and-interacting-with-a-reconstructed-scene)
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
- [AccessibilityComponent](https://developer.apple.com/documentation/realitykit/accessibilitycomponent)
- [Improving the Accessibility of RealityKit Apps](https://developer.apple.com/documentation/realitykit/improving-the-accessibility-of-realitykit-apps)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adding intelligent app features with generative models](https://developer.apple.com/documentation/foundationmodels/adding-intelligent-app-features-with-generative-models)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)

## Related knowledge-base routes

- [RealityKit, ARKit, and spatial experiences](04-realitykit-arkit-and-spatial.md)
- [RealityKit/ARKit spatial route](../50-capability-recipes/40-realitykit-arkit-spatial-route.md)
- [Spatial scene and occlusion native surfaces](../21-design-deep-dives/37-spatial-scene-and-occlusion-native-surfaces.md)
- [SwiftUI ARKit/RealityKit design](../21-design-deep-dives/125-swiftui-arkit-realitykit-spatial-scene-review-design.md)
- [SwiftUI ARKit/RealityKit capability route](../50-capability-recipes/128-swiftui-arkit-realitykit-spatial-scene-review-route.md)
