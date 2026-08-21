# Spatial, Graphics, and Game Recipes

Use the [device and companion capability contracts](../42-framework-deep-dives/08-device-and-companion-capability-contracts.md) for camera/tracking/input state, and the [cross-framework feature lifecycle](../41-framework-deep-dives/06-cross-framework-feature-lifecycle.md) for ownership, teardown, performance, and proof boundaries.

## Scope and compile boundary

These are compile-oriented route sketches for ARKit sessions, RealityKit/RealityView scene content, visionOS immersive spaces, Metal setup, SpriteKit/GameplayKit game state, and GameKit authentication/multiplayer. They are not compiled in this documentation-only workspace and do not prove camera tracking, scene understanding, spatial comfort, GPU frame rate, shader compatibility, thermal/battery behavior, controller/input ergonomics, Game Center account state, or multiplayer reliability.

Keep the layers separate:

`device/session availability -> domain/simulation state -> scene/renderer -> input/network event -> review/persistence`

## Recipe 1: run an AR session only while the feature owns the camera

Check camera permission and configuration support before running. Keep tracking state explicit and pause on teardown/background according to the product’s policy.

```swift
import ARKit

final class ARSessionCoordinator: NSObject, ARSessionDelegate {
    let session = ARSession()
    private(set) var state = "idle"

    override init() {
        super.init()
        session.delegate = self
    }

    func startWorldTracking() {
        guard ARWorldTrackingConfiguration.isSupported else {
            state = "unsupported"
            return
        }

        let configuration = ARWorldTrackingConfiguration()
        configuration.planeDetection = [.horizontal, .vertical]
        state = "starting"
        session.run(configuration)
    }

    func pause() {
        session.pause()
        state = "paused"
    }

    func session(
        _ session: ARSession,
        cameraDidChangeTrackingState camera: ARCamera
    ) {
        switch camera.trackingState {
        case .normal:
            state = "normal"
        case .notAvailable:
            state = "notAvailable"
        case .limited:
            state = "limited"
        }
    }
}
```

Add a truthful camera usage description before presenting AR content. Explain limited tracking, show relocalization/retry, and avoid using a last-known pose as a current measurement. A configuration can be supported yet perform poorly in low light, blank/reflective environments, fast motion, or a crowded scene; record the environment and device when evaluating quality.

## Recipe 2: load RealityKit content asynchronously

Keep app-owned scene intent separate from entities. Load large assets asynchronously and show a placeholder/error route instead of blocking the UI.

```swift
import RealityKit
import SwiftUI

struct ModelScene: View {
    var body: some View {
        RealityView { content in
            do {
                let model = try await ModelEntity(named: "ExampleModel")
                content.add(model)
            } catch {
                // Publish a user-facing asset-load error in the product state.
            }
        } update: { content in
            // Apply bounded updates from app-owned state. Do not rebuild the
            // whole entity graph for every SwiftUI state change.
            _ = content
        }
    }
}
```

`RealityView` availability and content types differ by target platform. For visionOS, use the appropriate window/volume/immersive scene model; for iOS/iPadOS, use the supported RealityKit view route. Keep model/entity loading, transforms, animations, systems, and teardown owned by a scene adapter. A generated entity hierarchy is not a persistence model.

## Recipe 3: present a visionOS immersive space deliberately

Declare an `ImmersiveSpace`, select the immersion style, and make entry/exit asynchronous and observable. The user needs a clear way to leave the experience.

```swift
import SwiftUI

@main
struct SpatialExampleApp: App {
    @State private var style: ImmersionStyle = .mixed

    var body: some Scene {
        WindowGroup {
            ContentView()
        }

        ImmersiveSpace(id: "spatialScene") {
            ImmersiveContentView()
        }
        .immersionStyle(selection: $style, in: .mixed, .progressive, .full)
    }
}
```

Opening/dismissing a space uses asynchronous system actions, and only one immersive space can be open at a time in the relevant app context. Handle unavailable/error results, user cancellation, scene dismissal, safety interruptions, coordinate-origin changes, and a non-immersive route. Do not treat immersive presentation as proof of spatial input, tracking, comfort, or performance.

## Recipe 4: host a deterministic SpriteKit scene in SwiftUI

Keep simulation state and rendering nodes separate so game rules can be tested without a frame loop.

```swift
import SpriteKit
import SwiftUI

final class ExampleScene: SKScene {
    private var elapsed: TimeInterval = 0

    override func didMove(to view: SKView) {
        backgroundColor = .black
        // Load bounded assets and create nodes once for the scene lifecycle.
    }

    override func update(_ currentTime: TimeInterval) {
        // Use a bounded/deterministic simulation step in a target game.
        elapsed = currentTime
    }
}

struct GameView: View {
    private let scene: ExampleScene = {
        let scene = ExampleScene(size: CGSize(width: 800, height: 600))
        scene.scaleMode = .aspectFill
        return scene
    }()

    var body: some View {
        SpriteView(
            scene: scene,
            isPaused: false,
            preferredFramesPerSecond: 60
        )
        .ignoresSafeArea()
    }
}
```

Pause/foreground/background, orientation, external display, controller changes, low-power mode, and asset failures must be explicit states. Use a SwiftUI shell for menus/settings/purchases/accessibility and keep core game state independent from `SKNode` identity.

## Recipe 5: use GameplayKit for testable game logic

GameplayKit state machines, entities/components, pathfinding, and randomization can live outside the renderer. Use seeded randomness and deterministic inputs for replays/fixtures.

```swift
import GameplayKit

final class PlayingState: GKState {
    private(set) var elapsed: TimeInterval = 0

    override func didEnter(from previousState: GKState?) {
        elapsed = 0
    }

    func advance(by deltaTime: TimeInterval) {
        elapsed += min(max(deltaTime, 0), 0.1)
    }
}

final class PausedState: GKState {}

let playing = PlayingState()
let paused = PausedState()
let machine = GKStateMachine(states: [playing, paused])
```

The snippet is a route sketch: implement a concrete paused state and transition rules in the target. Keep pathfinding inputs, player actions, simulation time, and persistence serializable/testable; do not hide game-critical truth in animation completion callbacks.

## Recipe 6: initialize Metal from a measured requirement

Use Metal when a measurable custom-rendering or compute requirement cannot be met by a higher-level framework. Validate the device, create a command queue, load pipeline resources, and measure before optimizing.

```swift
import Metal

final class MetalRenderer {
    let device: MTLDevice
    let commandQueue: MTLCommandQueue

    init?() {
        guard let device = MTLCreateSystemDefaultDevice(),
              let commandQueue = device.makeCommandQueue() else {
            return nil
        }

        self.device = device
        self.commandQueue = commandQueue
    }

    func submitWork() {
        guard let commandBuffer = commandQueue.makeCommandBuffer() else {
            return
        }

        // Encode bounded render/compute work using resources and pipeline
        // states created for this same MTLDevice.
        commandBuffer.commit()
    }
}
```

Create buffers/textures/pipelines on the same device, define synchronization/resource ownership, and avoid compiling pipelines or allocating large resources inside the frame loop. Check feature support and use GPU captures/Metal profiling. A successful command-buffer submission does not prove frame pacing, visual quality, memory, thermal, or battery behavior.

## Recipe 7: authenticate Game Center before multiplayer

GameKit authenticates the local player and may invoke its handler multiple times, including with a system view controller that needs presentation. Check restrictions before enabling multiplayer/communication features.

```swift
import GameKit

final class GameCenterCoordinator: NSObject {
    private(set) var state = "notAuthenticated"

    func authenticate() {
        GKLocalPlayer.local.authenticateHandler = { [weak self] viewController, error in
            if let viewController {
                // Present through the app’s current UI boundary.
                _ = viewController
                self?.state = "needsSystemUI"
                return
            }

            guard error == nil, GKLocalPlayer.local.isAuthenticated else {
                self?.state = "unavailable"
                return
            }

            if GKLocalPlayer.local.isUnderage
                || GKLocalPlayer.local.isMultiplayerGamingRestricted {
                self?.state = "restricted"
                return
            }

            self?.state = "ready"
        }
    }
}
```

A Game Center account is not the same as an app account or server authorization. Respect communication restrictions and user privacy. Keep matchmaking, match join/leave, connected/disconnected, message validation, timeouts, and server/game-rule authority explicit.

## Recipe 8: treat a match as a lossy session boundary

```swift
import GameKit

final class MatchCoordinator: NSObject, GKMatchDelegate {
    private(set) var connectedPlayers: [GKPlayer] = []
    private(set) var isInMatch = false

    func attach(_ match: GKMatch) {
        match.delegate = self
        connectedPlayers = match.players
        isInMatch = true
    }

    func send(_ data: Data, using match: GKMatch) throws {
        guard isInMatch else { return }
        try match.sendData(toAllPlayers: data, with: .reliable)
    }

    func match(
        _ match: GKMatch,
        didReceive data: Data,
        fromRemotePlayer player: GKPlayer
    ) {
        // Validate version, sender/player mapping, size, sequence, and game
        // rule before applying the event to simulation state.
        _ = data
        _ = player
    }

    func match(_ match: GKMatch, player: GKPlayer, didChange state: GKPlayerConnectionState) {
        // Map connected/disconnected/unknown to explicit session state.
        _ = player
        _ = state
    }

    func match(_ match: GKMatch, didFailWithError error: Error?) {
        isInMatch = false
        // Show retry/leave/reconnect state; do not keep simulating as online.
        _ = error
    }
}
```

Bound message size/rate, use reliable/unreliable delivery intentionally, handle late/duplicate data, and make reconnect/reconciliation deterministic. A peer-to-peer match is not a trusted authority for inventory, purchase, ranking, or anti-cheat decisions.

## Recipe 9: unified scene/game state and teardown

```swift
enum GraphicsFeatureState {
    case unavailable(reason: String)
    case permissionNeeded
    case loadingAssets
    case initializing
    case running
    case limited(reason: String)
    case paused(reason: String)
    case disconnected
    case failed(message: String, canRetry: Bool)
}

struct RenderBudget {
    let targetFramesPerSecond: Int
    let maxTextureBytes: Int
    let maxSimulationStep: TimeInterval
}
```

When a scene/game feature leaves the screen, pause or invalidate AR sessions, stop subscriptions/updates, release large assets/command resources, cancel pending loads, detach match delegates/leave matches when appropriate, and publish the resulting state. Teardown must be idempotent; repeated background/foreground and view lifecycle events must not duplicate sessions, match listeners, or frame tasks.

## Recipe 10: physical-device and accessibility proof

| Route | Evidence to capture |
| --- | --- |
| ARKit/RealityKit | Camera permission, supported/unsupported device, tracking limited/normal/interrupted/relocalizing, low light/blank/reflective/fast-motion environments, anchors/entity rebuild, frame time, memory, thermal, battery, and non-AR fallback. |
| visionOS | Window/volume/immersive scene, mixed/progressive/full style, entry/exit, coordinate conversion, input/comfort/safety, scene dismissal, and physical device where available. |
| Metal | Device feature set, shader/pipeline load, GPU capture, command-buffer errors, frame pacing, CPU/GPU/memory, thermal throttling, low-power, and oldest supported hardware. |
| SpriteKit/GameplayKit | Deterministic simulation, pause/background, input/controller/orientation, asset failure, frame rate, memory, accessibility shell, reduced motion, and oldest supported device. |
| GameKit | Game Center authentication, restrictions, matchmaking, join/leave/disconnect/reconnect, message validation, account/privacy, network loss, duplicate/late events, and physical-device multiplayer. |

Previews, simulators, static models, mocked matches, and local GPU fixtures validate state rendering and pure logic. They do not prove camera tracking, spatial understanding, GPU frame rate, thermal behavior, controller ergonomics, Game Center account state, or multiplayer reliability.

## Sources

- [ARKit](https://developer.apple.com/documentation/arkit)
- [ARSession](https://developer.apple.com/documentation/arkit/arsession)
- [ARWorldTrackingConfiguration](https://developer.apple.com/documentation/arkit/arworldtrackingconfiguration)
- [RealityKit](https://developer.apple.com/documentation/realitykit)
- [RealityView](https://developer.apple.com/documentation/realitykit/realityview)
- [Immersive spaces](https://developer.apple.com/documentation/swiftui/immersive-spaces)
- [ImmersiveSpace](https://developer.apple.com/documentation/swiftui/immersivespace)
- [Metal](https://developer.apple.com/documentation/metal)
- [MTLDevice](https://developer.apple.com/documentation/metal/mtldevice)
- [Performing calculations on a GPU](https://developer.apple.com/documentation/metal/performing-calculations-on-a-gpu)
- [SpriteKit](https://developer.apple.com/documentation/spritekit)
- [SpriteView](https://developer.apple.com/documentation/spritekit/spriteview)
- [SKScene](https://developer.apple.com/documentation/spritekit/skscene)
- [GameplayKit](https://developer.apple.com/documentation/gameplaykit)
- [GKStateMachine](https://developer.apple.com/documentation/gameplaykit/gkstatemachine)
- [GKEntity](https://developer.apple.com/documentation/gameplaykit/gkentity)
- [GKGraph](https://developer.apple.com/documentation/gameplaykit/gkgraph)
- [GameKit](https://developer.apple.com/documentation/gamekit)
- [Authenticating a player](https://developer.apple.com/documentation/gamekit/authenticating-a-player)
- [GKLocalPlayer](https://developer.apple.com/documentation/gamekit/gklocalplayer)
- [GKMatch](https://developer.apple.com/documentation/gamekit/gkmatch)
