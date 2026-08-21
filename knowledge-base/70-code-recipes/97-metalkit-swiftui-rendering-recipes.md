# MetalKit SwiftUI rendering recipes

These are compile-oriented route sketches for an iOS target that uses MetalKit
inside a SwiftUI shell. They are not compiled in this documentation-only
workspace and do not prove device support, shader correctness, frame rate,
thermal behavior, accessibility, or release resource membership. Confirm the
exact selected SDK signatures before copying them.

## 1. Keep a typed render state outside the view

~~~swift
import Foundation

struct RenderRevision: Sendable, Equatable {
    let sourceID: String
    let sourceRevision: String
    let profileID: String
    let isProposal: Bool
}

enum RenderSurfaceState: Sendable, Equatable {
    case unavailable(reason: String)
    case loading
    case preparing(RenderRevision)
    case ready(RenderRevision)
    case rendering(RenderRevision)
    case paused(RenderRevision)
    case degraded(RenderRevision, reason: String)
    case failed(message: String)
}
~~~

Keep this state in the feature owner. A `MTLTexture`, `MTKMesh`, or
`MTLCommandBuffer` should not be stored in a persistence model or used as the
stable identity of a source record.

## 2. Create an `MTKView` bridge

~~~swift
import MetalKit
import SwiftUI

struct MetalSurface: UIViewRepresentable {
    let snapshot: RenderSnapshot

    func makeCoordinator() -> Coordinator {
        Coordinator()
    }

    func makeUIView(context: Context) -> MTKView {
        let view = MTKView(frame: .zero)
        guard let device = MTLCreateSystemDefaultDevice() else {
            return view
        }

        view.device = device
        view.delegate = context.coordinator.renderer
        view.enableSetNeedsDisplay = true
        view.isPaused = true
        view.colorPixelFormat = .bgra8Unorm
        context.coordinator.renderer.configure(view: view)
        return view
    }

    func updateUIView(_ view: MTKView, context: Context) {
        context.coordinator.renderer.apply(snapshot: snapshot, to: view)
        view.setNeedsDisplay()
    }

    static func dismantleUIView(_ view: MTKView, coordinator: Coordinator) {
        view.delegate = nil
        view.isPaused = true
        coordinator.renderer.teardown()
    }

    final class Coordinator {
        let renderer = RendererRoute()
    }
}
~~~

`RenderSnapshot` and the renderer are intentionally undefined seams. Compile
the bridge in the chosen target, add the desired device/format/error policy,
and verify that repeated SwiftUI updates do not recreate the device, queue,
pipeline, or assets.

## 3. Separate the renderer owner from the frame description

~~~swift
import MetalKit

struct RenderSnapshot: Sendable, Equatable {
    let revision: RenderRevision
    let clearColorRGBA: SIMD4<Float>
    let selectedItemID: String?
}

final class RendererRoute: NSObject, MTKViewDelegate {
    private var device: MTLDevice?
    private var commandQueue: MTLCommandQueue?
    private var snapshot: RenderSnapshot?

    func configure(view: MTKView) {
        device = view.device
        commandQueue = device?.makeCommandQueue()
        // Create libraries and pipeline states for the selected target here.
    }

    func apply(snapshot: RenderSnapshot, to view: MTKView) {
        self.snapshot = snapshot
        // Reconcile resources by revision; do not rebuild everything blindly.
        view.drawableSize = view.bounds.size
    }

    func draw(in view: MTKView) {
        guard
            let descriptor = view.currentRenderPassDescriptor,
            let drawable = view.currentDrawable,
            let commandBuffer = commandQueue?.makeCommandBuffer()
        else {
            return
        }

        // Encode a bounded render pass using the current snapshot.
        // Finish with the documented encoder/command-buffer and drawable flow.
        commandBuffer.present(drawable)
        commandBuffer.commit()
    }

    func mtkView(_ view: MTKView, drawableSizeWillChange size: CGSize) {
        // Rebuild size-dependent uniforms/resources only.
    }

    func teardown() {
        snapshot = nil
        commandQueue = nil
        device = nil
    }
}
~~~

This is a route sketch rather than a complete renderer. A real implementation
must encode the render pass, bind validated resources, handle command errors,
and choose a clear policy for drawable unavailability. Do not assume that
calling `present` and `commit` means the GPU completed successfully.

## 4. Load a texture with a bounded file policy

~~~swift
import MetalKit

struct TextureRequest: Sendable {
    let url: URL
    let sourceRevision: String
    let maximumPixelDimension: Int
}

func loadTexture(
    _ request: TextureRequest,
    device: MTLDevice
) throws -> MTLTexture {
    // Validate URL scope, type, size, and retention before this call.
    let loader = MTKTextureLoader(device: device)
    let options: [MTKTextureLoader.Option: Any] = [
        .SRGB: false
    ]
    return try loader.newTexture(URL: request.url, options: options)
}
~~~

Confirm the option names and selected color policy in the target SDK. Add
pixel-dimension/decoded-size validation before loading and a separate
downsample or fallback path for large user assets. Keep the source revision
beside the resulting resource in the renderer cache.

## 5. Bridge a Model I/O asset through `MTKMesh`

~~~swift
import MetalKit
import ModelIO

struct MeshLoadResult {
    let asset: MDLAsset
    let meshes: [MTKMesh]
}

func loadMeshes(
    from url: URL,
    device: MTLDevice,
    descriptor: MDLVertexDescriptor
) throws -> MeshLoadResult {
    let allocator = MTKMeshBufferAllocator(device: device)
    let asset = try MDLAsset(
        url: url,
        vertexDescriptor: descriptor,
        bufferAllocator: allocator,
        preserveTopology: false
    )

    let meshes = try MTKMesh.newMeshes(asset: asset, device: device).meshes
    return MeshLoadResult(asset: asset, meshes: meshes)
}
~~~

The initializer and `MTKMesh` conversion signatures can vary with the selected
SDK/import overlay; treat this as a route sketch until it compiles. Validate
asset type, hierarchy, bounds, vertex attributes, submeshes, material/texture
resources, and shader layout. `preserveTopology: false` is a product decision,
not a universal default; use the topology policy that matches the renderer.

## 6. Validate a render proposal before applying it

~~~swift
struct RenderProfileProposal: Codable, Sendable {
    let sourceRevision: String
    let profileID: String
    let drawableScale: Double
    let textureLimit: Int
    let explanation: String
}

enum ProposalDecision {
    case rejected(String)
    case review(RenderProfileProposal)
}

func validate(
    _ proposal: RenderProfileProposal,
    currentSourceRevision: String,
    supportedProfiles: Set<String>
) -> ProposalDecision {
    guard proposal.sourceRevision == currentSourceRevision else {
        return .rejected("The source changed; generate a new proposal.")
    }
    guard supportedProfiles.contains(proposal.profileID) else {
        return .rejected("This render profile is not supported here.")
    }
    guard (0.5...2.0).contains(proposal.drawableScale) else {
        return .rejected("The scale is outside the product budget.")
    }
    guard (256...16_384).contains(proposal.textureLimit) else {
        return .rejected("The texture limit is outside the product budget.")
    }
    return .review(proposal)
}
~~~

The model’s explanation is not evidence that the profile is correct. Present
the proposal with before/after preview, source revision, edit/reject/accept,
and undo. Apply only the accepted, revalidated profile.

## 7. Use a semantic fallback beside the renderer

~~~swift
import SwiftUI

struct RenderFeatureView: View {
    let state: RenderSurfaceState

    var body: some View {
        VStack(alignment: .leading) {
            Text(statusText)
                .accessibilityAddTraits(.isHeader)

            switch state {
            case .ready, .rendering, .paused, .preparing:
                MetalSurface(snapshot: snapshot)
                    .accessibilityLabel("Custom visual preview")
                    .accessibilityHint("Use the inspector below for semantic values and actions.")
                Button("Open inspector") {
                    // Present a native list/editor route.
                }
            case .unavailable, .loading, .degraded, .failed:
                ContentUnavailableView(
                    "Preview unavailable",
                    systemImage: "rectangle.slash",
                    description: Text("Use the accessible list or manual editor.")
                )
                Button("Open manual view") {
                    // Preserve the actual task outside the renderer.
                }
            }
        }
    }

    private var statusText: String { "Render status" }
    private var snapshot: RenderSnapshot { fatalError("Route sketch") }
}
~~~

Do not ship the `fatalError` or placeholder actions. The point of the seam is
that an essential value/action remains available when the GPU path is paused,
unsupported, or inaccessible.

## 8. Test the deterministic portion first

~~~swift
// Pseudocode: use Swift Testing or XCTest in the named target.
@Test
func staleProposalCannotChangeRenderRevision() {
    let result = validate(
        staleProposal,
        currentSourceRevision: "source-2",
        supportedProfiles: ["full", "reduced"]
    )
    switch result {
    case .rejected(let message):
        #expect(message == "The source changed; generate a new proposal.")
    case .review:
        #expect(Bool(false), "A stale proposal must not reach review.")
    }
}
~~~

Add fixtures for empty/malformed/oversized assets, missing textures, descriptor
mismatch, repeated SwiftUI updates, off-screen pause, resource replacement,
reduced-quality fallback, and accessibility settings. Compile and device-test
the renderer separately from the pure state/validator tests.

## Sources

- [MetalKit](https://developer.apple.com/documentation/metalkit/)
- [MTKView](https://developer.apple.com/documentation/metalkit/mtkview/)
- [MTKViewDelegate](https://developer.apple.com/documentation/metalkit/mtkviewdelegate/)
- [MTKTextureLoader](https://developer.apple.com/documentation/metalkit/mtktextureloader/)
- [MTKMesh](https://developer.apple.com/documentation/metalkit/mtkmesh/)
- [MTKMeshBufferAllocator](https://developer.apple.com/documentation/metalkit/mtkmeshbufferallocator/)
- [MTKSubmesh](https://developer.apple.com/documentation/metalkit/mtksubmesh/)
- [Model I/O](https://developer.apple.com/documentation/modelio/)
- [MDLAsset](https://developer.apple.com/documentation/modelio/mdlasset/)
- [MDLMesh](https://developer.apple.com/documentation/modelio/mdlmesh/)
- [Metal](https://developer.apple.com/documentation/metal/)
- [MTLDevice](https://developer.apple.com/documentation/metal/mtldevice/)
- [MTLCommandQueue](https://developer.apple.com/documentation/metal/mtlcommandqueue/)
- [UIViewRepresentable](https://developer.apple.com/documentation/swiftui/uiviewrepresentable/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Swift Testing](https://developer.apple.com/documentation/testing)
