# Spatial, Graphics, and Games

## Do not collapse spatial, rendering, and multiplayer into one route

| User outcome | Primary route | Boundary to prove |
| --- | --- | --- |
| Place or understand content in the physical world | ARKit plus RealityKit | Camera permission, supported sensors/device, tracking state, scene understanding, privacy, and physical-device behavior. |
| Show 3D content in a conventional or visionOS app | RealityKit/RealityView plus SwiftUI | Asset loading, scene/entity lifecycle, platform scene model, input/accessibility, memory, and spatial ergonomics. |
| Inspect, normalize, or prepare 3D assets | Model I/O, then RealityKit for new runtime presentation | Resource resolution, vertex descriptors, hierarchy/naming, scale, conversion, memory, and reopen/export proof. |
| Maintain an existing SceneKit project | SceneKit behind an adapter, with a RealityKit migration plan | SceneKit is deprecated/maintenance-mode guidance, asset/behavior mapping, and representative before/after proof. |
| Render custom GPU work | Metal/MetalKit | `MTLDevice` features, shader/pipeline/resource lifecycle, frame pacing, GPU/CPU/memory/thermal budgets. |
| Host a custom Metal surface inside SwiftUI | MetalKit `MTKView`/`MTKViewDelegate` plus `UIViewRepresentable` | View ownership, drawable cadence, shader/resource membership, semantic fallback, and physical-device frame proof. |
| Load textures or Model I/O meshes for Metal | `MTKTextureLoader`, `MTKMesh`, `MTKMeshBufferAllocator` | File scope, color/format policy, vertex descriptors, submeshes, memory, malformed assets, and resource validation. |
| Build a 2D game | SpriteKit plus SwiftUI shell | Scene/game state separation, input/pause/background, assets, frame time, accessibility, and device performance. |
| Share gameplay or leaderboards | GameKit | Game Center authentication/restrictions, match lifecycle, identity/privacy, network delivery, server/game rules, and physical-device proof. |

The Simulator and previews are excellent for scene/state choreography and deterministic game logic. They do not prove camera tracking, spatial understanding, GPU frame rate, thermal behavior, controller ergonomics, Game Center account state, or multiplayer reliability.

## Choose the rendering layer

| Outcome | Start here | Add or switch when |
| --- | --- | --- |
| SwiftUI visual effects and custom shapes | SwiftUI, Canvas, Shape | The UI needs a contained custom drawing surface. |
| Image filters/compositing | Core Image | You need reusable image processing or camera effects. |
| Vector drawing | Core Graphics | You need explicit paths, PDF/vector output, or custom rendering. |
| 2D game | SpriteKit | You need a scene graph, actions, physics, and game loop. |
| Game rules/AI/navigation | GameplayKit | You need state machines, pathfinding, or strategy helpers. |
| 3D objects/scene | RealityKit | You need entities, components, materials, spatial transforms. |
| Camera/world tracking | ARKit | You need real-world anchors, tracking, or plane detection. |
| Room capture | RoomPlan | You need supported room scanning and structured room output. |
| Low-level GPU | Metal/MetalKit | You need explicit shaders, compute, rendering, custom performance, a managed drawable view, or a Model I/O/texture bridge. |

## Spatial experience route

1. Define whether the user needs a 3D object, augmented reality, room capture, or an immersive scene.
2. Check device and sensor support before presenting the experience.
3. Request camera/scene permission in context.
4. Keep tracking state visible: initializing, limited, normal, interrupted, stopped.
5. Separate real-world measurements/anchors from display-only effects.
6. Provide a non-AR fallback when the core outcome can be completed without tracking.
7. Measure thermal, memory, and battery behavior on physical devices.

## Graphics discipline

Custom shaders, blur, image effects, and 3D layers can make a screen feel premium, but they have performance and accessibility costs. Preserve semantic labels and controls outside the drawing surface, expose an accessible summary for important data, and avoid making navigation depend on a purely visual effect.

## Games

Use SpriteKit or RealityKit for the rendering world, GameplayKit for reusable game systems, and SwiftUI for menus, settings, inventory, onboarding, and non-game system surfaces. Keep game state deterministic where possible so previews, replay, and tests can exercise it without timing-dependent rendering.

For GameKit, authenticate the local player before using Game Center services, check underage/multiplayer/communication restrictions, and keep match/leaderboard/achievement state separate from the renderer. Treat a match as a networked session with join, connected, disconnected, reconnect/leave, timeout, and stale-peer states; framework delivery does not replace game-rule validation or server authority where the product needs it.

## Sources

- [RealityKit](https://developer.apple.com/documentation/realitykit)
- [ARKit](https://developer.apple.com/documentation/arkit)
- [RoomPlan](https://developer.apple.com/documentation/roomplan)
- [Metal](https://developer.apple.com/documentation/metal)
- [MetalKit](https://developer.apple.com/documentation/metalkit/)
- [MTKView](https://developer.apple.com/documentation/metalkit/mtkview/)
- [MTKViewDelegate](https://developer.apple.com/documentation/metalkit/mtkviewdelegate/)
- [MTKTextureLoader](https://developer.apple.com/documentation/metalkit/mtktextureloader/)
- [MTKMesh](https://developer.apple.com/documentation/metalkit/mtkmesh/)
- [MTLDevice](https://developer.apple.com/documentation/metal/mtldevice)
- [Core Image](https://developer.apple.com/documentation/coreimage)
- [Core Graphics](https://developer.apple.com/documentation/coregraphics)
- [SpriteKit](https://developer.apple.com/documentation/spritekit)
- [SpriteView](https://developer.apple.com/documentation/spritekit/spriteview)
- [GameplayKit](https://developer.apple.com/documentation/gameplaykit)
- [GameKit](https://developer.apple.com/documentation/gamekit)
- [Authenticating a player](https://developer.apple.com/documentation/gamekit/authenticating-a-player)
- [GKLocalPlayer](https://developer.apple.com/documentation/gamekit/gklocalplayer)
- [GKMatch](https://developer.apple.com/documentation/gamekit/gkmatch)
- [ARSession](https://developer.apple.com/documentation/arkit/arsession)
- [ARWorldTrackingConfiguration](https://developer.apple.com/documentation/arkit/arworldtrackingconfiguration)
- [RealityView](https://developer.apple.com/documentation/realitykit/realityview)
- [Entity](https://developer.apple.com/documentation/realitykit/entity)
- [Model I/O](https://developer.apple.com/documentation/modelio)
- [MDLAsset](https://developer.apple.com/documentation/modelio/mdlasset)
- [MDLMesh](https://developer.apple.com/documentation/modelio/mdlmesh)
- [SceneKit](https://developer.apple.com/documentation/scenekit)
- [SCNScene](https://developer.apple.com/documentation/scenekit/scnscene)
- [Model3D](https://developer.apple.com/documentation/realitykit/model3d)
- [Bringing your SceneKit projects to RealityKit](https://developer.apple.com/documentation/realitykit/bringing-your-scenekit-projects-to-realitykit)
- [Bringing your SceneKit projects to RealityKit](https://developer.apple.com/documentation/realitykit/bringing-your-scenekit-projects-to-realitykit)
- [Immersive spaces](https://developer.apple.com/documentation/swiftui/immersive-spaces)
