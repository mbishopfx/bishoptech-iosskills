# RealityKit, ARKit, RoomPlan, Object Capture, and spatial scene architecture

## Why this is a family of routes

Spatial features are not one framework toggle. A native app may combine:

| Need | Primary route | What it owns |
| --- | --- | --- |
| Track the device in the world | ARKit and ARSession | Camera pose, world coordinates, tracking state, planes, images, objects, raycasts, and scene understanding |
| Render and manipulate 3D content | RealityKit | Entities, components, systems, anchors, materials, animation, physics, input, and scene hierarchy |
| Put RealityKit content into a SwiftUI surface | RealityView where the selected target supports it | SwiftUI composition around a RealityKit content lifecycle |
| Provide a camera-backed iOS AR view | ARView | A RealityKit view with an AR session and scene |
| Scan rooms | RoomPlan | Guided room capture, parametric room data, captured structures, and USD-family exports |
| Turn object photographs into a model | ObjectCaptureSession and PhotogrammetrySession | Guided image capture and a separate reconstruction phase |
| Add domain intelligence | Vision, Core ML, Foundation Models, or app-owned rules | Labels, extraction, summaries, and proposals—not spatial truth |

Choose the smallest route that proves the product outcome. A room scan is not the same as placing a model on a plane, and an Object Capture model is not evidence that the model is correctly scaled in a live AR scene.

## The spatial authority chain

Treat each layer as an observation with its own confidence and failure mode:

~~~text
camera and motion sensors
  -> ARSession tracking state
  -> plane/raycast/mesh/image/object observations
  -> anchor transform
  -> RealityKit entity hierarchy
  -> user manipulation
  -> saved spatial record or system side effect
~~~

ARKit creates a correspondence between a device and the physical world. It uses visual-inertial odometry and scene analysis, but lighting, texture, motion, occlusion, and the visible environment affect tracking quality. A plane anchor can be refined after content is placed. The app should communicate that an estimate is being refined instead of presenting every transform as permanent measurement.

Preserve the source observation when the product stores a result:

- device and operating-system context;
- tracking state and reason at the time of placement;
- query type and alignment;
- anchor or raycast transform;
- plane classification or mesh observation if used;
- model asset identifier and scale policy;
- user adjustments;
- time and coordinate-space version;
- model or AI proposal metadata if enrichment was used.

This makes later repair, migration, and review possible.

## ARKit: tracking, detection, and scene understanding

### World tracking

ARWorldTrackingConfiguration tracks six degrees of freedom: device rotation and translation. It can also enable plane detection, image detection, object detection, ray casting, and other frame semantics depending on the target and device. Check support before showing a feature. Keep the app usable when a device supports the camera but not the requested AR capability.

The basic lifecycle is:

1. Confirm the target links ARKit and includes the camera usage description.
2. Check the configuration’s support for the requested feature.
3. Obtain camera permission through the normal ARKit/session flow.
4. Create a configuration with only the plane/semantic options required.
5. Run an ARSession or camera-backed ARView.
6. Observe tracking state and interruption/relocalization events.
7. Raycast or use anchors to create a placement candidate.
8. Require an intentional placement action.
9. Attach RealityKit content to a stable anchor.
10. Reconcile or remove content when tracking becomes unavailable.

Do not start a high-cost configuration simply because it is available. Plane detection, scene reconstruction, people occlusion, image detection, and object detection each affect power, memory, and device support.

### Raycasts and planes

Ray casting asks for a 3D location corresponding to a 2D screen point or an existing AR raycast query. Plane detection provides detected surfaces that may be refined over time. Use a raycast for a direct placement gesture, and use plane anchors or classifications when the product needs a persistent surface relationship.

Placement policy should state:

- whether estimated or existing geometry is acceptable;
- horizontal, vertical, or any alignment;
- whether the object can be placed before plane refinement completes;
- how the app gently corrects a placement after refinement;
- what happens if the user moves outside the tracked area;
- whether a saved location is session-local or portable.

Apple’s AR guidance favors immediate feedback followed by subtle refinement. Avoid pretending that the edge of a detected plane is a precise physical boundary.

### Scene reconstruction and occlusion

When supported, ARWorldTrackingConfiguration.sceneReconstruction provides a polygonal mesh estimate of the physical environment. The app must check support before enabling it. Plane detection can improve parts of the mesh, and people occlusion can alter the mesh based on the frame semantics in use.

Use reconstruction for interactions that genuinely need environment geometry:

- object occlusion behind a wall or table;
- collision or placement constraints;
- room-scale visualizations;
- spatial measurement with an explicit approximate label;
- a temporary navigation or accessibility cue.

Do not retain a complete room mesh by default. Store only the minimum geometry required by the product, give the person a deletion path, and consider whether a local-only session is enough.

## RealityKit: entities, components, systems, and scene ownership

RealityKit uses an entity-component-system model:

- an Entity is a node in the scene hierarchy;
- a Component holds a capability or value such as transform, model, collision, physics, input, synchronization, or accessibility;
- a System applies repeated behavior to matching entities during scene updates.

An entity can hold one component of a given type. Components should describe state. Systems should own behavior that affects many entities or runs repeatedly. This is especially important for per-frame work: a single system query can be more coherent than putting repeated update logic on every object.

A practical ownership split is:

| Layer | Owns |
| --- | --- |
| SwiftUI state model | User intent, route state, selected entity ID, error, and saved records |
| ARSession | Tracking configuration and camera/world observations |
| RealityKit scene | Anchors, entities, components, systems, and transient render state |
| Domain store | Versioned placement/model/scan records |
| AI service | A typed proposal derived from selected source data |

Avoid making an Entity the only source of truth for a saved record. An entity can disappear when a view is rebuilt, a session is restarted, or a target changes platform.

Register custom systems before displaying the scene, and keep systems bounded:

- query only the components needed;
- avoid allocating or loading assets on every update;
- throttle work that does not need frame cadence;
- move long-running analysis off the rendering path;
- stop subscriptions and remove anchors when the feature leaves the screen;
- expose a low-power mode or a static fallback when thermal or tracking conditions degrade.

## SwiftUI, RealityView, and ARView boundaries

RealityView is a SwiftUI view for RealityKit content and exposes a make/update-style content lifecycle. Use it when the selected target and scene type support the desired RealityKit composition. Keep asynchronous asset loading, entity identity, and view-state reconciliation explicit.

ARView is a camera-backed RealityKit view with an AR session. It remains a direct route for an iOS AR experience that needs the AR session and RealityKit scene in one view. When using ARView from SwiftUI, isolate the UIKit bridge in a small UIViewRepresentable and keep business state outside the view.

Do not assume these surfaces have identical behavior:

- ARView has a session and camera-mode responsibilities;
- RealityView’s content lifecycle is SwiftUI-oriented;
- model shadows, environment blending, input, coordinate conversion, and platform availability can differ;
- a visionOS-oriented RealityView example is not automatically an iOS camera AR implementation;
- an API that compiles for one target may be unavailable or differently configured in another.

Verify the intended deployment target, SDK availability, and actual target membership before selecting the bridge.

## RoomPlan: guided room capture

RoomPlan uses the device camera, LiDAR where available, trained models, and RealityKit rendering to guide a person through scanning an interior room. It recognizes structural elements and selected room objects, then returns parametric captured data that an app can edit, measure, display, or export.

There are two UI ownership choices:

| Choice | Use when |
| --- | --- |
| RoomCaptureView | The system-guided scanning UI is enough and the app wants a focused integration |
| RoomCaptureSession | The app needs custom scanning graphics, instruction timing, or a larger workflow around the capture |

For a single room, run a capture session, guide movement, stop it, and build a CapturedRoom from the result. For multiple rooms, keep the individual CapturedRoom values and use StructureBuilder to create a CapturedStructure. A structure can contain rooms on multiple floors and can be exported to a USD-family format.

RoomPlan’s data is a model of the observed environment, not a legal survey. Label measurements and detected categories appropriately. Give the person a review step before saving, exporting, sharing, or using the scan to make a purchase or construction decision.

RoomPlan also has a target boundary: Mac Catalyst can process captured room/structure data, but the capture session itself depends on a camera, LiDAR, and AR-capable sensors on iOS or iPadOS. Do not claim that a Mac Catalyst run proves capture hardware behavior.

## Object Capture and photogrammetry

Object Capture separates guided photography from model reconstruction:

~~~text
ObjectCaptureSession + ObjectCaptureView
  -> captured image set
  -> PhotogrammetrySession
  -> model output
  -> RealityKit import and review
~~~

Check ObjectCaptureSession.isSupported before creating a capture session. ObjectCaptureView presents the capture UI and the session exposes capture state, feedback, tracking, and completion. Reconstruction is a separate phase. PhotogrammetrySession also has its own hardware support and resource constraints.

Treat the resulting asset as an input that needs review:

- verify the object is complete and has no unintended background;
- check scale and orientation;
- inspect texture and geometry quality;
- preserve the input image set or an auditable reference when the product needs reproducibility;
- make reconstruction resumable or cancellable;
- move expensive reconstruction off the interactive capture surface;
- do not block the main actor with file or model processing;
- disclose when reconstruction leaves the device or is shared to another device.

For a product that only needs a visual catalog object, a prebuilt USDZ asset may be safer and cheaper than per-user photogrammetry.

## On-device AI and spatial data

AI can be useful after the spatial observation is typed and reviewable:

| AI task | Safe input | Human-visible output |
| --- | --- | --- |
| Label a captured object | Selected crop/metadata or user-approved scan result | Candidate label with source and edit control |
| Summarize a room | Selected CapturedRoom fields, not an invisible raw stream | Editable room summary |
| Suggest furniture placement | Room dimensions, catalog item, explicit placement constraints | Proposal with preview and undo |
| Clean object metadata | User-selected object and provenance | Typed draft; original remains recoverable |
| Choose a fallback | Capability and tracking state | Route choice, never a hidden side effect |

AI should not invent a transform, silently change a saved measurement, or turn a low-confidence plane into a guaranteed surface. Keep calibration and geometric constraints deterministic. Store the model route, context version, proposal, and user decision alongside the result when AI affected a saved record.

## Native design and Liquid Glass

Use the AR HIG as the primary spatial design authority:

- devote most of the display to the physical world and virtual objects;
- keep controls sparse and reachable;
- use screen-space controls for persistent actions;
- use familiar direct manipulation when people are looking at and touching objects;
- avoid competing gestures;
- use audio/haptics as reinforcement rather than the only signal;
- show approachable instruction text;
- provide a manual or non-AR fallback when the feature is optional.

Liquid Glass belongs on app-owned controls and review surfaces. It should group actions without covering the physical scene or reducing contrast around placement feedback. Keep primary actions stable as the AR content changes, and move detailed inspectors into a sheet or a separate screen.

RealityKit entities do not automatically provide all the semantic information that assistive technologies need. Add AccessibilityComponent data to important entities, and provide a two-dimensional list or inspector that exposes the same task without requiring precise camera aiming.

## Verification stop list

- Named target, deployment target, SDK, device family, and required entitlements.
- Camera usage description and any face-data or microphone disclosure.
- AR configuration support checks and unsupported-device route.
- Physical-device tracking, plane/raycast, interruption, relocalization, and low-light tests.
- Scene reconstruction and occlusion tests on every claimed LiDAR/semantic device class.
- RoomPlan scan, cancellation, multi-room merge, export, and review tests.
- Object Capture support, capture-state, cancellation, reconstruction, and asset-review tests.
- RealityKit performance, memory, thermal, frame cadence, and asset-load tests.
- VoiceOver/Voice Control, Dynamic Type for screen UI, reduced motion, contrast, localization, and manual fallback.
- AI proposal rejection, source/provenance preservation, deterministic geometry, and no-hidden-side-effect tests.
- Signed archive inspection for privacy strings, capabilities, resources, supported devices, and release configuration.

## Sources

- [RealityKit](https://developer.apple.com/documentation/realitykit)
- [RealityKit updates](https://developer.apple.com/documentation/updates/realitykit)
- [RealityView](https://developer.apple.com/documentation/realitykit/realityview)
- [ARView](https://developer.apple.com/documentation/realitykit/arview)
- [Entity](https://developer.apple.com/documentation/realitykit/entity)
- [Systems](https://developer.apple.com/documentation/realitykit/ecs-systems)
- [Implementing systems for entities in a scene](https://developer.apple.com/documentation/realitykit/implementing-systems-for-entities-in-a-scene)
- [ARKit](https://developer.apple.com/documentation/arkit)
- [Understanding world tracking](https://developer.apple.com/documentation/arkit/understanding-world-tracking)
- [ARWorldTrackingConfiguration](https://developer.apple.com/documentation/arkit/arworldtrackingconfiguration)
- [Scene reconstruction](https://developer.apple.com/documentation/arkit/arworldtrackingconfiguration/scenereconstruction)
- [ARRaycastQuery](https://developer.apple.com/documentation/arkit/arraycastquery)
- [Verifying device support and user permission](https://developer.apple.com/documentation/arkit/verifying-device-support-and-user-permission)
- [RoomPlan](https://developer.apple.com/documentation/roomplan)
- [Scanning the rooms of a single structure](https://developer.apple.com/documentation/roomplan/scanning-the-rooms-of-a-single-structure)
- [RoomCaptureView](https://developer.apple.com/documentation/roomplan/roomcaptureview)
- [RoomCaptureSession](https://developer.apple.com/documentation/roomplan/roomcapturesession)
- [ObjectCaptureSession](https://developer.apple.com/documentation/realitykit/objectcapturesession)
- [ObjectCaptureView](https://developer.apple.com/documentation/realitykit/objectcaptureview)
- [PhotogrammetrySession](https://developer.apple.com/documentation/realitykit/photogrammetrysession)
- [AccessibilityComponent](https://developer.apple.com/documentation/realitykit/accessibilitycomponent)
- [Augmented reality](https://developer.apple.com/design/human-interface-guidelines/augmented-reality)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
