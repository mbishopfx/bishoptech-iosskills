# RealityKit and ARKit compile-oriented recipes

These are route sketches to compile inside a named Xcode target. They intentionally keep product state, sensor observations, RealityKit scene state, and AI proposals separate. They are not proof of device support or runtime behavior.

## 1. Typed capability gate

~~~swift
import ARKit
import RealityKit

enum SpatialAvailability: Sendable, Equatable {
    case ready
    case unsupported(String)
    case permissionNeeded
    case permissionDenied
    case resourceUnavailable(String)
}

struct SpatialSupport: Sendable {
    let worldTracking: Bool
    let meshReconstruction: Bool
    let objectCapture: Bool
    let photogrammetry: Bool

    @MainActor
    static func current() -> Self {
        Self(
            worldTracking: ARWorldTrackingConfiguration.isSupported,
            meshReconstruction: ARWorldTrackingConfiguration.supportsSceneReconstruction(.mesh),
            objectCapture: ObjectCaptureSession.isSupported,
            photogrammetry: PhotogrammetrySession.isSupported
        )
    }
}
~~~

Compile this in the target that will ship. If a symbol is unavailable for the deployment target, move that check behind the appropriate availability boundary instead of lowering the product contract silently. The UI should expose a route-specific reason, such as “This device can place objects but does not support room reconstruction.”

## 2. SwiftUI camera AR bridge

~~~swift
import SwiftUI
import ARKit
import RealityKit

struct CameraARView: UIViewRepresentable {
    func makeUIView(context: Context) -> ARView {
        let view = ARView(frame: .zero)
        guard ARWorldTrackingConfiguration.isSupported else {
            return view
        }

        let configuration = ARWorldTrackingConfiguration()
        configuration.planeDetection = [.horizontal, .vertical]
        view.session.run(
            configuration,
            options: [.resetTracking, .removeExistingAnchors]
        )
        return view
    }

    func updateUIView(_ view: ARView, context: Context) {
        // Reconcile explicit commands here; do not rebuild the scene on every
        // SwiftUI update.
    }

    static func dismantleUIView(_ view: ARView, coordinator: ()) {
        view.session.pause()
        view.scene.anchors.removeAll()
    }
}
~~~

Add NSCameraUsageDescription to the target. Keep permission rationale, unsupported-device state, and a manual fallback outside the bridge. If the app owns an ARSession directly, use a coordinator/delegate with a symmetric teardown path.

## 3. Raycast candidate and explicit placement

~~~swift
import ARKit
import RealityKit
import UIKit

@MainActor
func placeModel(
    named assetName: String,
    at point: CGPoint,
    in view: ARView
) -> Entity? {
    guard
        let query = view.makeRaycastQuery(
            from: point,
            allowing: .estimatedPlane,
            alignment: .any
        ),
        let result = view.session.raycast(query).first,
        let model = try? ModelEntity.loadModel(named: assetName)
    else {
        return nil
    }

    let anchor = AnchorEntity(world: result.worldTransform)
    anchor.addChild(model)
    view.scene.addAnchor(anchor)
    return model
}
~~~

The returned entity is only a placement result. A product should also store the query kind, alignment, tracking state, source asset, and user confirmation. Add collision/input components only when the interaction needs them. Preserve the anchor or domain ID so SwiftUI can select the entity without using a pointer to an ephemeral object as its only identity.

If the product requires an existing surface rather than an estimate, change the raycast policy and present a “keep looking” state when no result is available. Test plane refinement after the object is placed.

## 4. RealityView content lifecycle

~~~swift
import SwiftUI
import RealityKit

struct ModelSurface: View {
    let assetName: String

    var body: some View {
        RealityView { content in
            guard let model = try? await ModelEntity(named: assetName) else {
                return
            }
            model.name = assetName
            content.add(model)
        } update: { content in
            // Reconcile selected state or transforms from the app model.
            // Avoid adding a second copy every time state changes.
        }
    }
}
~~~

Compile this only in a target where RealityView is available. An iOS camera-backed AR surface may need ARView instead. Keep the make/update lifecycle idempotent, load assets asynchronously, and surface an asset failure to the SwiftUI state model.

## 5. AccessibilityComponent on a spatial entity

~~~swift
import RealityKit

@MainActor
func makeAccessible(_ entity: Entity, label: LocalizedStringResource) {
    var accessibility = AccessibilityComponent()
    accessibility.isAccessibilityElement = true
    accessibility.label = label
    accessibility.systemActions = .init()
    entity.components.set(accessibility)
}
~~~

The exact supported actions should be selected for the entity and tested with VoiceOver. Add a two-dimensional list or inspector as the equivalent route for selecting, editing, and confirming objects. Do not rely on precise 3D aiming for an essential action.

## 6. RoomPlan delegate and review boundary

~~~swift
import RoomPlan

@MainActor
final class RoomScanCoordinator: NSObject, RoomCaptureSessionDelegate {
    let session = RoomCaptureSession()
    private(set) var rooms: [CapturedRoom] = []

    func begin(configuration: RoomCaptureSession.Configuration) {
        session.run(configuration: configuration)
    }

    func stopRoom() {
        session.stop(pauseARSession: false)
    }

    func captureSession(
        _ session: RoomCaptureSession,
        didEndWith data: CapturedRoomData,
        error: Error?
    ) {
        guard error == nil else {
            // Preserve the failure and offer retry/manual review.
            return
        }

        Task { @MainActor in
            do {
                let builder = RoomBuilder(options: [.beautifyObjects])
                let room = try await builder.capturedRoom(from: data)
                rooms.append(room)
            } catch {
                // Keep the raw/partial state only if the product's privacy
                // contract permits it; otherwise expose a recoverable error.
            }
        }
    }
}
~~~

For multiple rooms, keep the room array and build a CapturedStructure with StructureBuilder after the person finishes the structure. Compile the delegate signatures against the selected SDK. Test cancellation, a partial result, and a second room rather than only the happy path.

## 7. Object Capture surface

~~~swift
import SwiftUI
import RealityKit

struct ObjectCaptureSurface: View {
    @State private var session: ObjectCaptureSession?

    var body: some View {
        Group {
            if ObjectCaptureSession.isSupported, let session {
                ObjectCaptureView(session: session)
            } else {
                ContentUnavailableView(
                    "3D capture unavailable",
                    systemImage: "cube.transparent",
                    description: Text("Use a photo or choose a prepared model.")
                )
            }
        }
        .task {
            guard ObjectCaptureSession.isSupported else { return }
            session = ObjectCaptureSession()
        }
    }
}
~~~

The session’s capture state and feedback should drive the product’s instructions. Capture completion is not reconstruction completion. Persist the input-set reference if the user expects a later reconstruction or Mac handoff.

## 8. Photogrammetry request boundary

~~~swift
import RealityKit

func reconstructObject(
    from inputDirectory: URL,
    to outputURL: URL
) async throws {
    guard PhotogrammetrySession.isSupported else {
        throw NSError(
            domain: "SpatialRoute",
            code: 1,
            userInfo: [NSLocalizedDescriptionKey: "Photogrammetry is unavailable."]
        )
    }

    let configuration = PhotogrammetrySession.Configuration()
    let session = try PhotogrammetrySession(
        input: inputDirectory,
        configuration: configuration
    )
    let request = PhotogrammetrySession.Request.modelFile(url: outputURL)
    try session.process(requests: [request])

    for try await output in session.outputs {
        switch output {
        case .processingComplete:
            return
        case .requestError(_, let error):
            throw error
        default:
            continue
        }
    }
}
~~~

Treat this as a long-running, cancellable resource operation in a real app. Add storage checks, progress UI, cleanup for partial output, and a review screen for scale, orientation, geometry, and texture before making the model part of a saved catalog.

## 9. Room merge route

~~~swift
import RoomPlan

func mergeRooms(_ rooms: [CapturedRoom]) throws -> CapturedStructure {
    let builder = StructureBuilder()
    return try builder.capturedStructure(from: rooms)
}
~~~

Keep room names and capture order in the domain layer. The structure builder output should be treated as an observed model. If the app exports USD/USDZ, test import and coordinate interpretation on the receiving route.

## 10. Bounded AI proposal

~~~swift
struct SpatialProposal: Codable, Sendable, Equatable {
    let sourceIDs: [String]
    let schemaVersion: Int
    let title: String
    let explanation: String
    let proposedTransform: [Double]?
    let confidenceReason: String
}

struct ReviewedProposal: Sendable {
    let proposal: SpatialProposal
    let accepted: Bool
    let userEdited: Bool
}
~~~

The deterministic layer should validate every proposed transform against the current scene and product constraints. The AI route should receive only the selected, minimum necessary context. Store the source IDs and schema/model context when a proposal is accepted. Rejection must leave the original scan/placement unchanged.

## 11. RealityKit system shape

~~~swift
import RealityKit

struct SelectionComponent: Component {
    var isSelected = false
}

// Compile the System protocol requirements against the target SDK.
struct SelectionSystem: System {
    static let query = EntityQuery(where: .has(SelectionComponent.self))

    init(scene: Scene) {}

    func update(context: SceneUpdateContext) {
        for entity in context.scene.performQuery(Self.query) {
            guard let selection = entity.components[SelectionComponent.self] else {
                continue
            }
            // Keep per-frame work bounded. Move heavy analysis elsewhere.
            if selection.isSelected {
                // Update a lightweight visual component or material state.
            }
        }
    }
}
~~~

Register the system before presenting the scene as required by the selected RealityKit route. Use a domain-level selection ID for persistence and an entity component for render state. Avoid doing file I/O, model inference, or network work in update.

## 12. Fixture and test matrix

~~~swift
struct SpatialFixture: Equatable, Sendable {
    let id: String
    let trackingState: String
    let queryAlignment: String
    let estimated: Bool
    let transform: [Double]
    let sourceAssetID: String
}

func acceptsPlacement(_ fixture: SpatialFixture) -> Bool {
    fixture.transform.count == 16 &&
    fixture.sourceAssetID.isEmpty == false
}
~~~

Cover:

- unsupported world tracking;
- camera denied;
- no raycast result;
- estimated versus existing plane;
- plane refinement;
- tracking interruption/relocalization;
- malformed/missing/oversized model;
- room capture cancellation and merge failure;
- Object Capture unsupported and reconstruction cancellation;
- AI proposal with invalid transform;
- accepted, edited, and rejected proposal;
- VoiceOver/manual fallback;
- reduced motion/transparency;
- export/share/delete privacy behavior.

## Verification stop list

- Compile each snippet in a named target; these pages do not claim compilation.
- Inspect the final Info.plist and target capabilities.
- Test a physical camera/AR session on each claimed device class.
- Test RoomPlan and Object Capture only on hardware where the support checks pass.
- Record resource/thermal/storage behavior for reconstruction.
- Test 2D fallback and accessibility without camera aiming.
- Verify AI proposals cannot write transforms, export, delete, or share without explicit approval.

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
- [Implementing systems for entities in a scene](https://developer.apple.com/documentation/realitykit/implementing-systems-for-entities-in-a-scene)
- [AccessibilityComponent](https://developer.apple.com/documentation/realitykit/accessibilitycomponent)
- [RoomPlan](https://developer.apple.com/documentation/roomplan)
- [RoomCaptureSession](https://developer.apple.com/documentation/roomplan/roomcapturesession)
- [Scanning the rooms of a single structure](https://developer.apple.com/documentation/roomplan/scanning-the-rooms-of-a-single-structure)
- [ObjectCaptureSession](https://developer.apple.com/documentation/realitykit/objectcapturesession)
- [ObjectCaptureView](https://developer.apple.com/documentation/realitykit/objectcaptureview)
- [PhotogrammetrySession](https://developer.apple.com/documentation/realitykit/photogrammetrysession)
- [Augmented reality](https://developer.apple.com/design/human-interface-guidelines/augmented-reality)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
