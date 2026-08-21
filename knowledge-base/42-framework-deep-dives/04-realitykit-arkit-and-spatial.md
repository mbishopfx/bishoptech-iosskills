# RealityKit, ARKit, visionOS, and Spatial Experiences

## Capability boundary

RealityKit is the high-level route for interactive 3D scenes, entities, components, systems, animation, physics, and spatial content. ARKit supplies device/world understanding and camera-based tracking for supported augmented-reality experiences. visionOS adds SwiftUI windows/volumes and `ImmersiveSpace` presentation rules. They are related but not interchangeable products.

| Product shape | First route | Proof boundary |
| --- | --- | --- |
| 3D object/scene in a normal app | RealityKit view/renderer and entity graph | Asset loading, interaction, memory, layout, input/accessibility, and device performance. |
| Place content in a physical environment | ARKit session plus RealityKit content | Camera permission, supported hardware/sensors, tracking quality, lighting/environment, privacy, and physical device. |
| visionOS window/volume | SwiftUI scene plus RealityKit/`RealityView` where 3D content is needed | visionOS target, scene role, spatial layout, coordinate conversion, input, ergonomics, and device/simulator scope. |
| visionOS immersive experience | `ImmersiveSpace` with mixed/full/progressive style and RealityKit/Metal content | User consent/entry/exit, immersion style, safety boundary, spatial interaction, performance, and physical device. |
| Custom renderer | Metal, possibly integrated with RealityKit | GPU feature set, pipeline/resource lifecycle, frame pacing, memory, thermal, and profiling. |

## AR session lifecycle

An AR session coordinates device motion, camera capture, image analysis, and anchors. Keep its lifecycle separate from the SwiftUI view and from the app’s saved domain state:

`idle -> explainingPermission -> checkingSupport -> initializing -> running(normal|limited) -> interrupted|paused|relocalizing -> running|stopped`

1. Explain camera/world-sensing use at the feature boundary and include the required usage description.
2. Check the target device/configuration’s support before presenting the experience.
3. Create the `ARSession`/configuration for the actual outcome, such as world tracking or plane detection.
4. Set a delegate/renderer boundary and run the session only while the experience owns the foreground.
5. Convert anchors/observations into an app-owned scene model with timestamps and confidence/availability state.
6. Add/update/remove RealityKit entities through a scene adapter, not from arbitrary view callbacks.
7. Pause, reset, or degrade when tracking is limited/interrupted; never treat an old pose as current.

`ARSession.run` returns immediately while processing continues. `pause()` stops processing; it does not make a physical placement permanently true. A reset/relocalization can change the relationship between virtual and real spaces, so saved arrangements need a reconstruction/review policy.

## RealityKit entity/component/system boundary

Keep product state separate from the entity graph:

`domain state -> scene adapter -> Entity/Component/System -> user interaction -> domain event`

Entities represent objects, components describe appearance/behavior data, and systems apply reusable behavior. Save a stable app object ID, semantic role, transform/placement intent, and source/provenance in domain state; rebuild entities when the scene/session changes. Do not use a generated entity hierarchy as the only durable record.

For per-frame behavior, use a RealityKit `System` or a scene update subscription deliberately. Keep simulation time, rendering time, input, persistence, and network state separate. Bound per-frame work and avoid allocating or loading assets inside the frame loop.

## visionOS and `RealityView`

Use SwiftUI for windows and controls, `RealityView` for 3D content, and `ImmersiveSpace` when content must leave a bounded window. Choose mixed, progressive, or full immersion by the user outcome. Only one immersive space can be open across the app context; opening/dismissing is asynchronous and needs explicit state/error handling.

Load models asynchronously in `RealityView`’s make closure so a large asset does not hang the UI. Keep a placeholder/loading/error route and update scene content in the update closure or a controlled system. When positioning SwiftUI and entities together, use the provided coordinate-conversion route; do not assume the origin stays fixed across spaces, device movement, or SharePlay.

Fully immersive experiences need clear entry/exit controls and safety instructions. The system can stop or alter the experience when a person moves outside its safety boundary. This is system behavior to design for, not a condition to hide.

## Privacy and safety

Camera frames, world maps, room/scene understanding, hand/eye/person observations, and spatial layouts can reveal private spaces and routines. Minimize capture/retention, avoid raw frame logs, explain whether data leaves the device, and provide deletion. Keep on-device AI/spatial enrichment at the narrowest boundary.

Do not present a virtual placement as a measurement, construction guarantee, medical result, or safety assurance unless the product has separately validated the needed accuracy and domain. A plane, mesh, anchor, or tracking pose is framework data with uncertainty and availability state.

## Performance and asset discipline

Assets can exceed memory, load-time, GPU, or thermal budgets. Prefer progressive loading/levels of detail where appropriate, reuse materials/textures, measure scene complexity, and unload when the feature ends. A high frame rate on the newest device does not establish support on the oldest target.

For custom Metal integration, validate `MTLDevice` support and keep device-owned resources together. Profile command buffers, pipeline creation, shader compilation, texture memory, CPU/GPU frame time, and thermal throttling. Choose Metal because a measured requirement needs it, not because a lower-level API sounds more capable.

## Spatial API route matrix

Choose the scene ownership and tracking source before writing entity code. Keep the persistent product model independent from the runtime scene graph.

| Outcome | API route | Normalize into domain state | Target/availability/proof gate |
| --- | --- | --- | --- |
| Show a 3D object in a bounded view | RealityKit `Entity`/`ModelEntity`/`AnchorEntity` and `RealityView` or platform renderer | Asset ID, semantic role, transform intent, loading/error state | Asset availability, platform target, memory/load time, input/accessibility, and physical performance. |
| Track a real-world scene | `ARSession` + `ARWorldTrackingConfiguration` and selected `ARAnchor`/plane/scene understanding route | Anchor ID, transform, tracking state, confidence/availability, capture time | `ARConfiguration.isSupported`, camera permission, device/sensor support, lighting/environment, relocalization, and physical device. |
| React to entity behavior | RealityKit `Component`, `System`, scene events, subscriptions | Domain event or sampled state, not raw entity hierarchy | Bound per-frame work, deterministic update order, teardown, and frame-time measurement. |
| Build a visionOS window/volume | SwiftUI scene plus `RealityView` | App state and entity placement relative to the selected scene | visionOS target/scene role, coordinate conversion, input, window/volume resizing, and simulator/device scope. |
| Enter an immersive space | `ImmersiveSpace`, `openImmersiveSpace`, `dismissImmersiveSpace` and chosen immersion style | Immersion request/state, entry/exit reason, safety/comfort settings | Entry authorization, one-space rule, system dismissal/safety boundary, hand/eye/input route, and physical device. |
| Render custom GPU work | Metal `MTLDevice`, command queue/buffer, pipeline/resource graph | Render settings, quality tier, GPU/CPU timings, thermal state | Feature-set support, shader/pipeline compilation, memory/synchronization, GPU capture, oldest target device, and thermal proof. |

## Target and scene boundary matrix

| Target/surface | Owns | Shared boundary |
| --- | --- | --- |
| iOS/iPadOS AR app target | Camera permission, `ARSession`, scene adapter, app navigation | Semantic placement intent, user-confirmed anchors, saved asset/provenance. |
| visionOS app target | Window/volume/immersive scene, spatial input, `RealityView`, immersion state | Shared domain use cases and app-owned content; never assume iOS camera/session semantics. |
| Shared package | Components/data models, deterministic placement rules, asset metadata, test fixtures | No `ARSession`, `ImmersiveSpace`, entitlement, or process-owned scene lifecycle. |
| Widget/App Intent/system surface | Compact status/deep link or safe action | Do not serialize a live entity graph or expose a stale spatial measurement as current. |
| Metal renderer module | GPU resources, pipelines, command scheduling, measured quality tiers | Explicit value/configuration interface; no hidden domain mutation from a render pass. |

A saved transform is an intent or last-known placement, not proof that the same physical surface still exists. After a session reset or relocalization, rebuild the entity graph, report uncertainty, and ask for re-anchoring or review where the product depends on spatial accuracy.

## Availability and performance state

Track framework support separately from current conditions:

`unsupported -> permissionPending -> permissionDenied|supportedUnavailable -> initializing -> running(normal|limited) -> interrupted|relocalizing -> running|stopped`

Track asset/model readiness independently:

`assetMissing -> loading -> ready -> instantiated -> visible -> unloaded|failed`

For measured rendering, record device/OS/build, scene/entity count, asset sizes, target frame rate, CPU/GPU frame time, memory, thermal state, low-power mode, and interaction workload. A RealityKit statistics overlay or simulator frame is a diagnostic input; it is not a cross-device performance guarantee.

## Accessibility and fallback

Important spatial content needs semantic labels, readable summaries, alternative controls, reduced-motion behavior, and a non-spatial path when the user’s device, permissions, environment, or access needs make tracking unsuitable. Do not make a gesture, hand pose, spatial direction, color, or camera view the only way to complete a core action.

## Verification route

- Test no camera permission, unsupported hardware, limited/interrupted tracking, relocalization, low light, blank/reflective surfaces, fast motion, and session pause/resume.
- Run a physical-device matrix across the oldest supported and target hardware. Record OS build, camera/device configuration, lighting/environment, and test date.
- Verify entity rebuild after reset/relocalization, saved arrangement provenance, asset failure/placeholder, memory, frame time, GPU/CPU use, thermal behavior, battery, and background/foreground.
- For visionOS, test window/volume/immersive scene roles, mixed/progressive/full styles, entry/exit, one-space limitation, coordinate conversion, input, comfort, and safety messaging.
- Verify VoiceOver/accessibility labels, reduced motion, alternative controls, contrast, captions/text summaries, and a non-AR route.

The simulator can validate deterministic UI, state transitions, and scene choreography. It does not prove camera tracking, plane quality, world/room understanding, hand/eye input, GPU frame rate, thermal behavior, spatial comfort, or physical-device safety.

## Sources

- [RealityKit](https://developer.apple.com/documentation/realitykit)
- [RealityView](https://developer.apple.com/documentation/realitykit/realityview)
- [Entity](https://developer.apple.com/documentation/realitykit/entity)
- [ModelEntity](https://developer.apple.com/documentation/realitykit/modelentity)
- [AnchorEntity](https://developer.apple.com/documentation/realitykit/anchorentity)
- [Component](https://developer.apple.com/documentation/realitykit/component)
- [System](https://developer.apple.com/documentation/realitykit/system)
- [SceneEvents](https://developer.apple.com/documentation/realitykit/sceneevents)
- [ARKit](https://developer.apple.com/documentation/arkit)
- [ARSession](https://developer.apple.com/documentation/arkit/arsession)
- [run(_:options:)](https://developer.apple.com/documentation/arkit/arsession/run%28_%3Aoptions%3A%29)
- [ARWorldTrackingConfiguration](https://developer.apple.com/documentation/arkit/arworldtrackingconfiguration)
- [ARConfiguration](https://developer.apple.com/documentation/arkit/arconfiguration)
- [Tracking and visualizing planes](https://developer.apple.com/documentation/arkit/tracking-and-visualizing-planes)
- [ARPlaneAnchor](https://developer.apple.com/documentation/arkit/arplaneanchor)
- [Immersive spaces](https://developer.apple.com/documentation/swiftui/immersive-spaces)
- [ImmersiveSpace](https://developer.apple.com/documentation/swiftui/immersivespace)
- [Adding 3D content to your app](https://developer.apple.com/documentation/visionos/adding-3d-content-to-your-app)
- [Bringing your ARKit app to visionOS](https://developer.apple.com/documentation/visionos/bringing-your-arkit-app-to-visionos)
- [Creating fully immersive experiences in your app](https://developer.apple.com/documentation/visionos/creating-fully-immersive-experiences)
- [Metal](https://developer.apple.com/documentation/metal)
- [MTLDevice](https://developer.apple.com/documentation/metal/mtldevice)
