# SwiftUI ARKit and RealityKit spatial-scene review recipes

These are compile-oriented route sketches for an iOS SwiftUI camera AR feature. They are intentionally incomplete app slices: verify exact signatures, availability, imports, target membership, privacy strings, asset names, and SDK behavior in the selected Xcode project. They do not claim to compile in this documentation-only workspace or prove physical AR behavior.

Use them with [the ARKit/RealityKit deep dive](../42-framework-deep-dives/97-swiftui-arkit-realitykit-spatial-scene-review.md), [the design companion](../21-design-deep-dives/125-swiftui-arkit-realitykit-spatial-scene-review-design.md), [the capability route](../50-capability-recipes/128-swiftui-arkit-realitykit-spatial-scene-review-route.md), and [the proof matrix](../60-verification/122-swiftui-arkit-realitykit-spatial-scene-review-proof-matrix.md).

## Recipe 1: explicit state and source envelope

Keep framework observations, AI output, user intent, and domain records distinct:

~~~swift
enum SpatialTrackingState: Equatable, Sendable {
    case idle
    case starting
    case limited(reason: String)
    case normal
    case interrupted
    case relocalizing
    case unavailable
    case failed(message: String)
}

struct SpatialObservationSnapshot: Equatable, Sendable {
    var revision: Int
    var sessionID: UUID
    var frameTimestamp: TimeInterval
    var tracking: SpatialTrackingState
    var candidateTransform: simd_float4x4?
    var candidateTarget: String?
    var candidateAlignment: String?
    var isStale: Bool
}

struct SpatialProposalInput: Sendable {
    var sourceRevision: Int
    var sessionID: UUID
    var frameTimestamp: TimeInterval
    var tracking: SpatialTrackingState
    var summary: String
    var userIntent: String
}
~~~

Implementation notes:

- The revision belongs to the app and increments when session ownership, user intent, or the candidate changes.
- A frame timestamp is evidence metadata, not a freshness guarantee by itself.
- Keep a session UUID so callbacks from a replaced session can be rejected.
- Do not put raw camera frames or meshes in a long-lived SwiftUI view state object unless the product needs them and has a retention policy.
- Keep the proposal input small and source-linked.

## Recipe 2: SwiftUI ARView bridge

A thin UIViewRepresentable wrapper can host the iOS ARView while a coordinator owns lifecycle:

~~~swift
import ARKit
import RealityKit
import SwiftUI

struct CameraARView: UIViewRepresentable {
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

    final class Coordinator: NSObject {
        private let model: SpatialSceneModel
        private var sessionGeneration = UUID()
        private var trackedRaycast: ARTrackedRaycast?

        init(model: SpatialSceneModel) {
            self.model = model
        }

        func attach(to view: ARView) {
            // Configure the session only after permission and support checks.
        }

        func reconcileScene(in view: ARView) {
            // Reconcile app-owned records to stable RealityKit entities.
        }

        func stop(_ view: ARView) {
            trackedRaycast?.stop()
            trackedRaycast = nil
            view.session.pause()
            view.session.delegate = nil
            sessionGeneration = UUID()
        }
    }
}
~~~

Keep updateUIView idempotent. Do not call session.run from every SwiftUI update. A production coordinator should also cancel scene subscriptions, pending asset loads, and model tasks.

## Recipe 3: capability and camera gate

Make the entry decision before the camera starts:

~~~swift
@MainActor
func startARIfSupported(
    on view: ARView,
    model: SpatialSceneModel
) {
    guard ARWorldTrackingConfiguration.isSupported else {
        model.showUnsupportedFallback()
        return
    }

    guard model.cameraAccessIsAuthorized else {
        model.showCameraExplanation()
        return
    }

    let configuration = ARWorldTrackingConfiguration()
    configuration.planeDetection = [.horizontal, .vertical]

    if ARWorldTrackingConfiguration.supportsSceneReconstruction(.meshWithClassification) {
        configuration.sceneReconstruction = .meshWithClassification
    }

    view.session.delegate = model.sessionDelegate
    view.session.delegateQueue = model.sessionDelegateQueue
    view.session.run(configuration, options: [.resetTracking, .removeExistingAnchors])
}
~~~

Verify:

- whether the selected deployment target exposes each property;
- the app’s actual camera authorization path;
- whether AR is a required device capability or an optional feature;
- whether scene reconstruction is useful enough to justify its cost;
- what the fallback says when only basic world tracking is available.

Do not infer camera authorization from a preview or from the existence of an ARView.

## Recipe 4: session delegate projection

Project delegate callbacks into a small main-actor state update:

~~~swift
final class ARSessionObserver: NSObject, ARSessionDelegate {
    private let sessionID: UUID
    private let revisionSource: () -> Int
    private let publish: @Sendable (SpatialObservationSnapshot) -> Void

    init(
        sessionID: UUID,
        revisionSource: @escaping () -> Int,
        publish: @escaping @Sendable (SpatialObservationSnapshot) -> Void
    ) {
        self.sessionID = sessionID
        self.revisionSource = revisionSource
        self.publish = publish
    }

    func session(_ session: ARSession, didUpdate frame: ARFrame) {
        let tracking = mapTrackingState(frame.camera.trackingState)
        let snapshot = SpatialObservationSnapshot(
            revision: revisionSource(),
            sessionID: sessionID,
            frameTimestamp: frame.timestamp,
            tracking: tracking,
            candidateTransform: nil,
            candidateTarget: nil,
            candidateAlignment: nil,
            isStale: false
        )

        publish(snapshot)
    }

    func session(
        _ session: ARSession,
        cameraDidChangeTrackingState camera: ARCamera
    ) {
        let tracking = mapTrackingState(camera.trackingState)
        publish(
            SpatialObservationSnapshot(
                revision: revisionSource(),
                sessionID: sessionID,
                frameTimestamp: session.currentFrame?.timestamp ?? 0,
                tracking: tracking,
                candidateTransform: nil,
                candidateTarget: nil,
                candidateAlignment: nil,
                isStale: tracking != .normal
            )
        )
    }

    func sessionWasInterrupted(_ session: ARSession) {
        publish(interruptedSnapshot())
    }

    func sessionInterruptionEnded(_ session: ARSession) {
        publish(relocalizingSnapshot())
    }

    func sessionShouldAttemptRelocalization(_ session: ARSession) -> Bool {
        true
    }
}
~~~

The exact concurrency and delegate signatures should be checked in the selected SDK. Keep the callback queue bounded and hop to the main actor inside the app model. Do not retain a frame indefinitely just because a model task is slow.

## Recipe 5: tracking-state mapping

Convert ARCamera tracking state into product copy and policy:

~~~swift
func mapTrackingState(
    _ state: ARCamera.TrackingState
) -> SpatialTrackingState {
    switch state {
    case .normal:
        return .normal
    case .notAvailable:
        return .unavailable
    case .limited(let reason):
        switch reason {
        case .initializing:
            return .limited(reason: "Move slowly to initialize tracking.")
        case .insufficientFeatures:
            return .limited(reason: "Aim at a textured surface.")
        case .excessiveMotion:
            return .limited(reason: "Slow down to improve tracking.")
        case .relocalizing:
            return .relocalizing
        @unknown default:
            return .limited(reason: "Tracking quality is limited.")
        }
    }
}
~~~

For a real app, keep a machine-readable reason separate from localized copy. The UI should be able to render different languages and accessibility descriptions without changing the state machine.

## Recipe 6: one-time raycast candidate

Use a current screen point and retain the source metadata:

~~~swift
func makePlacementCandidate(
    in view: ARView,
    at point: CGPoint,
    snapshot: SpatialObservationSnapshot
) -> PlacementCandidate? {
    guard snapshot.tracking == .normal else {
        return nil
    }

    guard let query = view.makeRaycastQuery(
        from: point,
        allowing: .estimatedPlane,
        alignment: .horizontal
    ) else {
        return nil
    }

    guard let result = view.session.raycast(query).first else {
        return nil
    }

    return PlacementCandidate(
        sessionID: snapshot.sessionID,
        sourceRevision: snapshot.revision,
        frameTimestamp: snapshot.frameTimestamp,
        target: "estimatedPlane",
        alignment: "horizontal",
        worldTransform: result.worldTransform
    )
}
~~~

Before commit, revalidate:

- the session identifier;
- the app revision;
- the current tracking state;
- candidate age;
- target and alignment;
- whether a newer candidate superseded it;
- whether the person still intends to place the same asset.

An empty result is not a default position. A stale result is not a current result.

## Recipe 7: tracked raycast lifecycle

Use a tracked raycast only for an active preview:

~~~swift
func beginTrackedPreview(
    in view: ARView,
    query: ARRaycastQuery,
    update: @escaping ([ARRaycastResult]) -> Void
) -> ARTrackedRaycast? {
    view.session.trackedRaycast(query) { results in
        update(results)
    }
}

func stopTrackedPreview(_ raycast: inout ARTrackedRaycast?) {
    raycast?.stop()
    raycast = nil
}
~~~

The callback should:

- reject results from the wrong session generation;
- stop when placement is confirmed;
- stop when the gesture ends if no continuous preview is required;
- stop on interruption, background, cancellation, and dismantle;
- avoid publishing every tiny transform change when the UI does not need it.

Use presentation smoothing only in the visual layer. The committed record should contain the accepted result, not an unexamined smoothed transform.

## Recipe 8: RealityKit anchor and entity projection

Project a reviewed placement into RealityKit:

~~~swift
@MainActor
func addReviewedPlacement(
    to view: ARView,
    candidate: PlacementCandidate,
    modelEntity: ModelEntity
) -> UUID {
    let recordID = UUID()
    let anchor = AnchorEntity(world: candidate.worldTransform)
    anchor.name = "placement-" + recordID.uuidString
    modelEntity.name = "model-" + recordID.uuidString
    anchor.addChild(modelEntity)
    view.scene.addAnchor(anchor)
    return recordID
}
~~~

Production code should also:

- retain an app-owned record for the returned ID;
- attach an accessibility component with current label/value/actions;
- handle asset load and collision shape failures;
- store the source session/revision;
- update or remove the anchor on reset/undo;
- avoid treating the entity name as identity;
- reconcile by stable record ID rather than creating duplicate anchors.

RealityKit may update anchor position as tracking refines. Keep the review/source label synchronized.

## Recipe 9: RealityKit accessibility component

A scene entity should have a non-spatial semantic description:

~~~swift
@MainActor
func makeAccessible(_ entity: Entity, label: String, value: String) {
    var accessibility = AccessibilityComponent()
    accessibility.isAccessibilityElement = true
    accessibility.label = LocalizedStringResource(stringLiteral: label)
    accessibility.value = LocalizedStringResource(stringLiteral: value)
    accessibility.systemActions = [.activate]
    entity.components.set(accessibility)
}
~~~

Verify exact property availability and action cases in the selected SDK. Keep the stable SwiftUI list as the primary alternate-input route. Do not encode unverified claims such as safe, exact, or identified in the label.

## Recipe 10: idempotent scene reconciliation

A scene adapter can reconcile app-owned records:

~~~swift
@MainActor
func reconcile(
    records: [PlacementRecord],
    in view: ARView,
    registry: inout [UUID: AnchorEntity]
) {
    let expectedIDs = Set(records.map(\.id))

    for record in records {
        if registry[record.id] == nil {
            let anchor = AnchorEntity()
            anchor.name = "placement-" + record.id.uuidString
            registry[record.id] = anchor
            view.scene.addAnchor(anchor)
        }

        // Update the projection from the current record.
        // Do not attach a second model when the record already exists.
    }

    for id in registry.keys where !expectedIDs.contains(id) {
        if let anchor = registry.removeValue(forKey: id) {
            anchor.removeFromParent()
        }
    }
}
~~~

Treat this as a sketch. A real implementation needs a stable source of world transforms, asset loading, anchor tracking policy, and main-actor ownership. Never remove a domain record merely because a renderer was recreated.

## Recipe 11: source-linked local AI proposal

Keep model output downstream of the framework snapshot:

~~~swift
func propose(
    from input: SpatialProposalInput,
    generate: @escaping (SpatialProposalInput) async throws -> SpatialProposal
) async -> SpatialProposal? {
    do {
        return try await generate(input)
    } catch is CancellationError {
        return nil
    } catch {
        return nil
    }
}
~~~

The caller should compare sourceRevision, sessionID, and user intent before displaying the result. The proposal UI should show:

- source revision and update time;
- the observation summary;
- model unavailable/loading/error state;
- edit, reject, and manual actions;
- a deterministic commit button.

Do not let a model callback call addAnchor, send a device command, save a room map, or change a physical setting without review and domain validation.

## Recipe 12: SwiftUI task shell

Keep status and recovery visible:

~~~swift
struct SpatialSceneScreen: View {
    @StateObject private var model = SpatialSceneModel()

    var body: some View {
        ZStack {
            CameraARView(model: model)
                .ignoresSafeArea()

            VStack {
                TrackingStatusView(state: model.tracking)
                Spacer()
                SpatialToolBar(
                    canPlace: model.canCommit,
                    onReset: model.reset,
                    onReview: model.reviewCandidate
                )
            }
            .padding()
        }
        .sheet(isPresented: $model.isReviewPresented) {
            PlacementReviewView(model: model)
        }
    }
}
~~~

This is not a final design system. Add semantic labels, Dynamic Type behavior, reduced-motion behavior, fallback content, and target-specific safe-area handling. Keep the review sheet usable if the camera session is interrupted while it is visible.

## Recipe 13: teardown and stale callback guard

Every asynchronous path needs a cancellation boundary:

~~~swift
@MainActor
final class SpatialSceneModel: ObservableObject {
    @Published private(set) var tracking: SpatialTrackingState = .idle
    @Published private(set) var isReviewPresented = false

    private var sessionGeneration = UUID()
    private var previewTask: Task<Void, Never>?
    private var trackedRaycast: ARTrackedRaycast?

    func stop(_ view: ARView) {
        previewTask?.cancel()
        previewTask = nil
        trackedRaycast?.stop()
        trackedRaycast = nil
        view.session.pause()
        view.session.delegate = nil
        sessionGeneration = UUID()
        tracking = .idle
    }

    func accepts(sessionID: UUID, revision: Int) -> Bool {
        sessionID == sessionGeneration && revision >= 0
    }
}
~~~

The generation check is only one guard. Also reject canceled work, old user intent, stale asset loads, and a changed target. The exact architecture can use actors instead of a MainActor class; the proof obligation remains the same.

## Recipe 14: preview and fallback fixtures

A preview should not start a camera session. Build static fixtures for:

- idle;
- permission explanation;
- unsupported device;
- initializing;
- limited insufficient-features;
- normal candidate;
- stale candidate;
- interrupted;
- relocalizing;
- review with AI unavailable;
- placed with undo;
- accessibility list route.

Use a fixed entity fixture or mock placement record for the 3D portion. Verify the same SwiftUI copy and enabled-state rules against a signed physical session separately.

## Recipe 15: compile and physical run checklist

Before copying a recipe into a product:

1. Create a named app target and set its deployment target.
2. Link ARKit and RealityKit.
3. Add NSCameraUsageDescription.
4. Confirm AR configuration support on the selected device.
5. Compile the smallest ARView bridge.
6. Add a physical-device permission run.
7. Verify tracking-state transitions.
8. Verify one-time and tracked raycast no-result behavior.
9. Verify AnchorEntity add/update/remove behavior.
10. Verify interruption, relocalization, reset, and teardown.
11. Run VoiceOver, Dynamic Type, Reduce Motion, and alternate-input tests.
12. Measure a release-like build on the target device.
13. Archive and test the signed artifact.
14. Record the evidence packet in the [proof matrix](../60-verification/122-swiftui-arkit-realitykit-spatial-scene-review-proof-matrix.md).

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
- [AccessibilityComponent](https://developer.apple.com/documentation/realitykit/accessibilitycomponent)
- [Improving the Accessibility of RealityKit Apps](https://developer.apple.com/documentation/realitykit/improving-the-accessibility-of-realitykit-apps)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
