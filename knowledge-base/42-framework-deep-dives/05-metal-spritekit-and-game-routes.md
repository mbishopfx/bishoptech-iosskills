# Metal, SpriteKit, and Game Routes

## Capability

Apple’s graphics stack lets an app choose the highest-level framework that meets the product need. SpriteKit is a practical 2D route; GameplayKit supplies reusable game-architecture and gameplay algorithms; RealityKit serves interactive 3D/spatial scenes; Metal is the lower-level graphics and GPU-compute route when the app needs direct control.

GameKit is a separate account/multiplayer/system-service boundary. Authenticate the local Game Center player before using Game Center features, inspect underage/multiplayer/communication restrictions, and keep player identity, match state, cloud/leaderboard state, and game simulation separate from the renderer. A `GKMatch` provides a peer-to-peer session; it does not validate game rules or make an untrusted client authoritative.

## Choose the smallest engine

| Need | Route | Why |
| --- | --- | --- |
| 2D game, particles, sprites, simple physics | SpriteKit | High-level scene, node, action, physics, and rendering model. |
| State machines, pathfinding, agents, randomization | GameplayKit with the selected renderer | Separates gameplay algorithms from the graphics layer. |
| Interactive 3D or spatial content | RealityKit | Entity/component/system model and Apple spatial integration. |
| Custom renderer, shader, or GPU compute | Metal/MetalKit | Direct GPU control, profiling, resource and pipeline decisions. |
| SwiftUI shell around a game surface | SwiftUI plus `SpriteView`/MetalKit/RealityKit bridge | Keep menus, settings, accessibility, and system navigation native. |

## 2D route sequence

1. Define the game loop, input model, scene/state transitions, and pause behavior.
2. Use an `SKScene` as the gameplay surface and keep game state separate from view chrome.
3. Load assets with an explicit lifecycle and memory budget.
4. Use actions and physics for simple interactions; move complex rules into testable systems.
5. Host the scene inside a SwiftUI shell when the app needs native onboarding, settings, purchases, widgets, or system routing.
6. Measure frame time and memory on the target device families.

## Metal route sequence

Use Metal when the high-level framework cannot meet a measurable requirement. Start with a concrete bottleneck or rendering feature, then:

1. Select and validate the `MTLDevice` and feature set.
2. Define resource ownership, command buffers, render/compute passes, and synchronization.
3. Compile/load shader libraries and create pipeline states.
4. Add instrumentation before optimizing.
5. Profile GPU, CPU, memory, frame pacing, and thermal behavior on real hardware.

Do not choose Metal because it sounds more “ultimate.” It increases implementation and maintenance surface; the higher-level frameworks already use Metal where appropriate.

## Game-system boundaries

- Separate simulation time, render time, input, persistence, and network state.
- Make pause, interruption, backgrounding, and restoration first-class states.
- Keep purchases, analytics, player identity, and cloud saves outside the render loop.
- Use deterministic fixtures or seeded randomness for tests and reproducible bug reports.
- Treat haptics, audio, motion, and accessibility as platform features, not post-processing.

## Graphics and game API route matrix

Choose the highest-level route that satisfies a measured requirement. Keep simulation state and system services independent from the renderer.

| Outcome | API route | Shared/game state | Target/performance/proof gate |
| --- | --- | --- | --- |
| 2D scene and sprites | `SKScene`, `SKNode`, `SKSpriteNode`, `SKAction`, `SKPhysicsWorld` | Entity ID, deterministic state, input event, simulation time | Asset loading, scene transitions, pause/interruption, oldest device, frame pacing, memory, accessibility, and controller/input proof. |
| SwiftUI game shell | `SpriteView` plus native SwiftUI navigation/settings/paywall | Game state service and deep-link/system boundary | Scene lifecycle and teardown, Dynamic Type/VoiceOver, device rotation/input, and background/foreground. |
| Gameplay algorithms | GameplayKit `GKStateMachine`, `GKEntity`/`GKComponent`, `GKGraph`/pathfinding, agents/random sources | Pure state transitions, seeded randomness, path/decision result | Unit fixtures without renderer, deterministic replay, cancellation, and performance with real scene load. |
| Game Center identity | `GKLocalPlayer.authenticateHandler` and local-player state | Player ID, authentication/restriction state, consent | Account change, network/offline, parental/multiplayer restrictions, and signed physical-device system UI. |
| Matchmaking/multiplayer transport | `GKMatchmaker`/`GKMatch` or a deliberate server route | Commands/snapshots, sequence, player join/leave, reconciliation | Malformed/late data, disconnect/reconnect, authority, message rate/size, two-device test, and production service state. |
| Custom GPU render | `MTLDevice`, `MTLCommandQueue`, command buffers/encoders, buffers/textures, render/compute pipeline states | Render configuration and measured frame metrics, not business mutation | Feature-set support, shader/pipeline loading, synchronization, GPU capture, memory, thermal, oldest device, and release build. |
| GPU compute for an app feature | Metal compute pipeline or Core ML/Metal Performance route chosen from the measured need | Input/output buffers, revision, cancellation, result provenance | Correctness fixtures, GPU/CPU fallback, memory, battery/thermal, and device matrix. |

## Target and process boundary matrix

| Surface | Owns | Keep out of it |
| --- | --- | --- |
| Main app target | SwiftUI shell, game scene/renderer, lifecycle, audio/haptics/input adapters | Hidden global simulation state, secrets, entitlement policy, untestable side effects. |
| Shared game module | Deterministic domain/simulation, state machine, serialization, replay fixtures | `SKView`/`MTKView`, `MTLDevice`, Game Center UI, target-specific entitlements. |
| Game Center route | Authentication, matchmaking/leaderboards/achievements callbacks and service state | Assumption that network player state is authoritative game truth. |
| Widget/App Intent/system surface | Score/status/deep link or safe compact action | Live renderer, per-frame simulation, private account data without projection/privacy policy. |
| Metal renderer | GPU resources/pipelines/encoders and frame scheduling | Mutating purchases, identity, persistence, or network authority from a draw/compute callback. |

## Deterministic simulation and multiplayer state

Use this state model:

`boot -> loadingAssets -> ready -> playing -> paused|interrupted -> resumed|ended -> saved/replayed`

For multiplayer, keep transport state separate:

`unauthenticated -> authenticating -> restricted|ready -> matchmaking -> connecting -> connected -> synchronized -> playing -> disconnected|reconciling|ended`

Define a message/schema version, sequence number, maximum size/rate, timeout, and authority for every network command. A renderer can interpolate a snapshot for smoothness, but it must not make a client-side visual result the authoritative score, purchase, inventory, or safety decision. Use seeded randomness and recorded input/state fixtures to replay a bug without requiring Game Center.

## Performance evidence register

For each supported device class, record:

- build/configuration, OS, GPU family, display refresh target, and input mode;
- scene/entity/sprite count, texture/material/asset sizes, shader/pipeline state;
- CPU frame time, GPU frame time, hitch/drop count, memory peak, load time;
- thermal state, battery/low-power behavior, background interruption, and recovery;
- controller/accessibility settings, audio/haptic load, and the actual gameplay workload.

Use Xcode GPU captures, Metal debugging, Instruments, XCTest performance baselines, and physical-device runs as distinct evidence. A stable preview, static screenshot, simulator frame, or newest-device measurement cannot support a universal “runs at 60 fps” claim.

## Multiplayer lifecycle

`unauthenticated -> authenticating -> restricted|ready -> matchmaking -> connecting -> connected -> playing -> disconnected|ended`

Handle repeated authentication callbacks, a player changing accounts, match join/leave/disconnect, malformed or late data, foreground/background, network changes, and a player who cannot use multiplayer. Use reliable/unreliable delivery modes intentionally, bound message sizes/rates, and make state reconciliation deterministic. If a backend is authoritative, keep server validation separate from GameKit transport.

## Rendering and performance boundaries

SpriteKit is a high-level 2D scene/physics/action route and can be hosted in SwiftUI with `SpriteView`. GameplayKit state machines, entities/components, and pathfinding should be testable without a running renderer. Metal gives direct control over devices, command queues, buffers/textures, shaders, pipeline states, and compute/render passes; that control also creates more memory, synchronization, frame pacing, and thermal responsibility.

Measure frame time, dropped frames, load time, memory, GPU/CPU occupancy, shader/pipeline compilation, thermal throttling, battery, and low-power behavior on the oldest supported device. A static screenshot, preview, or newest-device run is not a performance claim.

## Verification route

- Test on the slowest supported device, not only the newest GPU.
- Measure frame pacing, memory, load time, thermal throttling, battery use, and asset failure.
- Exercise interruptions, background/foreground, orientation, external display, controller/input changes, and low-power mode.
- Verify reduced motion, audio controls, captions, contrast, readable UI, and non-color feedback.
- Use Metal debugger, GPU captures, Instruments, and performance baselines where custom rendering is involved.

## Sources

- [SpriteKit](https://developer.apple.com/documentation/spritekit)
- [SpriteView](https://developer.apple.com/documentation/spritekit/spriteview)
- [SKScene](https://developer.apple.com/documentation/spritekit/skscene)
- [SKNode](https://developer.apple.com/documentation/spritekit/sknode)
- [SKSpriteNode](https://developer.apple.com/documentation/spritekit/skspritenode)
- [SKAction](https://developer.apple.com/documentation/spritekit/skaction)
- [SKPhysicsWorld](https://developer.apple.com/documentation/spritekit/skphysicsworld)
- [GameplayKit](https://developer.apple.com/documentation/gameplaykit)
- [GKStateMachine](https://developer.apple.com/documentation/gameplaykit/gkstatemachine)
- [GKEntity](https://developer.apple.com/documentation/gameplaykit/gkentity)
- [GKGraph](https://developer.apple.com/documentation/gameplaykit/gkgraph)
- [GameKit](https://developer.apple.com/documentation/gamekit)
- [Authenticating a player](https://developer.apple.com/documentation/gamekit/authenticating-a-player)
- [GKLocalPlayer](https://developer.apple.com/documentation/gamekit/gklocalplayer)
- [GKMatch](https://developer.apple.com/documentation/gamekit/gkmatch)
- [GKMatchmaker](https://developer.apple.com/documentation/gamekit/gkmatchmaker)
- [Metal](https://developer.apple.com/documentation/metal)
- [MTLCommandQueue](https://developer.apple.com/documentation/metal/mtlcommandqueue)
- [MTLCommandBuffer](https://developer.apple.com/documentation/metal/mtlcommandbuffer)
- [MTLRenderPipelineState](https://developer.apple.com/documentation/metal/mtlrenderpipelinestate)
- [MTLComputePipelineState](https://developer.apple.com/documentation/metal/mtlcomputepipelinestate)
- [Metal sample code library](https://developer.apple.com/documentation/metal/metal-sample-code-library)
- [Improving your game’s graphics performance and settings](https://developer.apple.com/documentation/metal/improving-your-games-graphics-performance-and-settings)
- [RealityKit](https://developer.apple.com/documentation/realitykit)
- [Core Haptics](https://developer.apple.com/documentation/corehaptics)
- [AVFoundation](https://developer.apple.com/documentation/avfoundation/)
