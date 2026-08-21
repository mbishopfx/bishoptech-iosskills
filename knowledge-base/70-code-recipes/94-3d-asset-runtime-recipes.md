# 3D asset runtime recipes

These are documentation-only route sketches. They name Apple APIs and show
ownership boundaries, but they are not claimed to compile in this workspace or
to prove a particular iOS 26 target, device, asset, or release artifact.

## 1. Inspect a Model I/O asset

Use Model I/O before handing a file to a renderer. Keep the report value-like
and omit private paths from analytics.

~~~swift
import Foundation
import ModelIO

struct AssetInspection: Sendable {
    let sourceExtension: String
    let rootPath: String?
    let objectCount: Int
    let meshCount: Int
    let notes: [String]
}

enum AssetInspectionError: Error {
    case unsupportedExtension(String)
    case tooLarge
}

func inspectAsset(at url: URL, maxBytes: Int64) throws -> AssetInspection {
    let ext = url.pathExtension.lowercased()
    guard MDLAsset.canImportFileExtension(ext) else {
        throw AssetInspectionError.unsupportedExtension(ext)
    }

    let values = try url.resourceValues(forKeys: [.fileSizeKey])
    guard Int64(values.fileSize ?? 0) <= maxBytes else {
        throw AssetInspectionError.tooLarge
    }

    let asset = MDLAsset(url: url)
    asset.loadTextures()

    var meshCount = 0
    var notes: [String] = []
    for case let mesh as MDLMesh in asset {
        meshCount += 1
        notes.append("vertices=\(mesh.vertexCount)")
        notes.append("submeshes=\(mesh.submeshes?.count ?? 0)")
        notes.append("attributes=\(mesh.vertexDescriptor.attributes.count)")
    }

    let rootPath = (asset.object(at: 0) as? MDLObject)?.path
    return AssetInspection(
        sourceExtension: ext,
        rootPath: rootPath,
        objectCount: asset.count,
        meshCount: meshCount,
        notes: notes
    )
}
~~~

Target checks to add around this sketch:

- validate `asset.count` and iteration behavior against the selected SDK;
- treat texture loading as a separate failure/reporting phase;
- avoid running large imports on the main actor;
- add cancellation and an external-resource resolver for document/network
  assets;
- compare the inspection report with fixture expectations.

## 2. Build an asset manifest from mesh descriptors

The manifest makes renderer and AI input bounded. Keep the actual buffer data
out of the model prompt unless the product has a deliberate privacy and memory
policy.

~~~swift
import ModelIO

struct MeshManifest: Codable, Sendable {
    let path: String
    let vertexCount: Int
    let submeshCount: Int
    let boundsDescription: String
    let attributeNames: [String]
}

func meshManifests(in asset: MDLAsset) -> [MeshManifest] {
    var result: [MeshManifest] = []

    for case let mesh as MDLMesh in asset {
        let names = mesh.vertexDescriptor.attributes
            .compactMap { ($0 as? MDLVertexAttribute)?.name }

        result.append(
            MeshManifest(
                path: mesh.path,
                vertexCount: mesh.vertexCount,
                submeshCount: mesh.submeshes?.count ?? 0,
                boundsDescription: String(describing: mesh.boundingBox),
                attributeNames: names
            )
        )
    }

    return result
}
~~~

Do not use a description string as a physical measurement contract. If an app
needs units, define and verify a unit conversion at ingestion and keep the
source scale in the manifest.

## 3. Present a model in a phase-aware SwiftUI surface

`Model3D` is a useful smallest route for a packaged model when the target SDK
supports the initializer. Keep the model stage stable and retain a normal
SwiftUI fallback.

~~~swift
import RealityKit
import SwiftUI

struct AssetPreview: View {
    let name: String
    let summary: String

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Model3D(named: name) { model in
                model
                    .resizable()
                    .aspectRatio(contentMode: .fit)
                    .frame(maxWidth: .infinity, minHeight: 220)
            } placeholder: {
                ProgressView("Loading model…")
                    .frame(maxWidth: .infinity, minHeight: 220)
            }

            Text(summary)
                .font(.subheadline)
                .foregroundStyle(.secondary)

            Text("Use the controls below to inspect or export this model.")
                .font(.footnote)
                .accessibilityLabel("Model actions are available below")
        }
        .padding()
    }
}
~~~

For a target that exposes the phase-based initializer, map empty, success,
failure, and unknown phases to the same product state model. Do not assume a
placeholder means the asset failed; keep loading and failure distinct.

## 4. Asynchronously load a RealityKit entity

For interactive scenes, use the asynchronous loading route and keep the entity
owned by a main-actor scene adapter. The exact `LoadRequest` lifecycle and
available initializer should be rechecked against the selected SDK.

~~~swift
import Combine
import RealityKit

@MainActor
final class EntityLoader: ObservableObject {
    @Published private(set) var entity: Entity?
    @Published private(set) var message = "Ready to load"

    private var request: AnyCancellable?

    func load(named name: String) {
        request?.cancel()
        entity = nil
        message = "Loading model…"

        request = Entity.loadAsync(named: name, in: nil)
            .sink(
                receiveCompletion: { [weak self] completion in
                    guard let self else { return }
                    if case .failure(let error) = completion {
                        self.message = "Could not load model: \(error.localizedDescription)"
                    }
                },
                receiveValue: { [weak self] loadedEntity in
                    self?.entity = loadedEntity
                    self?.message = "Model ready"
                }
            )
    }

    func cancel() {
        request?.cancel()
        request = nil
        message = "Loading cancelled"
    }
}
~~~

The loaded entity is not a domain record. Before adding it to a scene, validate
the asset revision, expected hierarchy, and resource report. Teardown should
cancel subscriptions and release scene references when the screen disappears.

## 5. Bridge a legacy SceneKit scene from Model I/O

This is a maintenance seam, not a new-product recommendation.

~~~swift
import ModelIO
import SceneKit
import SwiftUI

struct LegacySceneView: View {
    let sourceURL: URL

    var body: some View {
        Group {
            if let scene = try? SCNScene(mdlAsset: MDLAsset(url: sourceURL)) {
                SceneView(scene: scene, options: [.allowsCameraControl])
                    .accessibilityLabel("Legacy 3D scene")
            } else {
                ContentUnavailableView(
                    "Scene unavailable",
                    systemImage: "cube.transparent",
                    description: Text("This scene could not be prepared."))
            }
        }
    }
}
~~~

Keep this adapter behind a feature boundary. Record the current SceneKit
behavior, then build a separate RealityKit fixture rather than gradually
mixing node callbacks and entity components in the same domain layer.

## 6. Add a bounded RealityKit review component

A custom component can carry scene-local review state. Keep canonical review
decisions in the app’s persistence owner if they must survive relaunch or sync.

~~~swift
import RealityKit

struct ReviewMarkerComponent: Component, Codable {
    var sourcePath: String
    var status: Status

    enum Status: String, Codable {
        case needsReview
        case accepted
        case dismissed
    }
}

func markForReview(_ entity: Entity, sourcePath: String) {
    entity.components.set(
        ReviewMarkerComponent(sourcePath: sourcePath, status: .needsReview)
    )
}
~~~

Register custom component types when required by the selected RealityKit
workflow, especially when they must be available in a Reality file or
Reality Composer Pro package. The renderer component is only a projection;
persist the accepted proposal separately.

## 7. Type and validate an AI asset proposal

Keep the AI route independent from Foundation Models or another selected model
provider so deterministic validation and manual fallback remain available.

~~~swift
struct AssetLabelProposal: Codable, Sendable, Equatable {
    let sourceRevision: String
    let objectPath: String
    let suggestedLabel: String
    let allowedCategory: String?
    let modelRoute: String
}

enum ProposalDecision: Equatable {
    case accept
    case edit(String)
    case dismiss
    case stale
}

func validate(
    _ proposal: AssetLabelProposal,
    currentRevision: String,
    knownPaths: Set<String>,
    allowedCategories: Set<String>
) -> Bool {
    guard proposal.sourceRevision == currentRevision else { return false }
    guard knownPaths.contains(proposal.objectPath) else { return false }
    guard !proposal.suggestedLabel.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
        return false
    }
    if let category = proposal.allowedCategory {
        return allowedCategories.contains(category)
    }
    return true
}
~~~

The review UI should show the source path, source revision, proposal, and
accept/edit/dismiss actions. A stale proposal must be discarded or regenerated;
it must not be applied to a newer asset revision.

## 8. Group native controls with Liquid Glass

Use functional controls around the stage. Keep the important model status in
ordinary text and give each action a semantic label.

~~~swift
import SwiftUI

struct ModelActions: View {
    let reset: () -> Void
    let inspect: () -> Void
    let export: () -> Void

    var body: some View {
        GlassEffectContainer(spacing: 12) {
            HStack(spacing: 12) {
                Button("Reset", systemImage: "arrow.counterclockwise", action: reset)
                Button("Inspect", systemImage: "info.circle", action: inspect)
                Button("Export", systemImage: "square.and.arrow.up", action: export)
            }
            .labelStyle(.iconOnly)
            .padding(8)
            .glassEffect()
        }
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Model actions")
    }
}
~~~

Check the actual Liquid Glass API and deployment target before compiling. If
reduced transparency or contrast settings make the group ambiguous, retain
semantic button boundaries and add a plain fallback. Do not put the only
loading/error message inside the glass group.

## 9. Keep the asset workflow cancellable

The import, inspect, thumbnail, AI proposal, and export stages should have
separate cancellation and commit boundaries.

~~~swift
struct AssetWorkflowState: Equatable {
    enum Phase: Equatable {
        case idle
        case importing
        case inspecting
        case preparingPreview
        case proposing
        case waitingForReview
        case exporting
        case ready
        case failed(String)
        case cancelled
    }

    var phase: Phase = .idle
    var sourceRevision: String?
    var committedDerivedRecordID: String?
}
~~~

Only move to `ready` after the required deterministic checks pass. Only write a
derived record after review and validation. A cancelled task can leave a cache
entry, but it must not leave a domain record claiming the asset or proposal is
complete.

## Sources

- [Model I/O](https://developer.apple.com/documentation/modelio)
- [MDLAsset](https://developer.apple.com/documentation/modelio/mdlasset)
- [MDLMesh](https://developer.apple.com/documentation/modelio/mdlmesh)
- [MDLVertexDescriptor](https://developer.apple.com/documentation/modelio/mdlvertexdescriptor)
- [SceneKit](https://developer.apple.com/documentation/scenekit)
- [SCNScene](https://developer.apple.com/documentation/scenekit/scnscene)
- [SCNView](https://developer.apple.com/documentation/scenekit/scnview)
- [RealityKit](https://developer.apple.com/documentation/realitykit)
- [Entity](https://developer.apple.com/documentation/realitykit/entity)
- [ModelEntity](https://developer.apple.com/documentation/realitykit/modelentity)
- [Model3D](https://developer.apple.com/documentation/realitykit/model3d)
- [Entity loadModel](https://developer.apple.com/documentation/realitykit/entity/loadmodel%28named%3Ain%3A%29)
- [Entity load](https://developer.apple.com/documentation/realitykit/entity/load%28contentsof%3Awithname%3A%29)
- [Component](https://developer.apple.com/documentation/realitykit/component)
- [Systems](https://developer.apple.com/documentation/realitykit/ecs-systems)
- [Bringing your SceneKit projects to RealityKit](https://developer.apple.com/documentation/realitykit/bringing-your-scenekit-projects-to-realitykit)
- [Bringing your SceneKit projects to RealityKit](https://developer.apple.com/documentation/realitykit/bringing-your-scenekit-projects-to-realitykit)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
