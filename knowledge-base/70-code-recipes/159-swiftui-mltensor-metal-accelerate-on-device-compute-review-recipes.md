# SwiftUI MLTensor, Metal, and Accelerate on-device compute review recipes

These are compile-oriented sketches for the [on-device compute review](../42-framework-deep-dives/116-swiftui-mltensor-metal-accelerate-on-device-compute-review.md), the [design route](../21-design-deep-dives/144-swiftui-mltensor-metal-accelerate-on-device-compute-review-design.md), and the [proof matrix](../60-verification/141-swiftui-mltensor-metal-accelerate-on-device-compute-proof-matrix.md). They are not claimed to compile in this documentation-only workspace. Compile each slice against the exact target SDK and test on physical hardware.

The invariant is:

    source -> typed buffer/tensor -> bounded compute -> completed output -> validation -> proposal -> approval -> commit

## 1. Describe a tensor contract

~~~swift
import Foundation

struct TensorContract: Codable, Sendable, Equatable {
    let shape: [Int]
    let scalarType: String
    let layout: String
    let strides: [Int]?
    let pixelFormat: String?
    let minimumOS: String
    let sourceRevision: String
}
~~~

Keep shape, layout, scalar type, pixel metadata, and OS/device gates in the app-owned contract. Do not infer the contract from whatever shape a live frame happens to provide.

## 2. Create an `MLTensor` from known values

~~~swift
import CoreML

func makeInputTensor() -> MLTensor {
    MLTensor(
        shape: [1, 3, 224, 224],
        scalars: Array(repeating: Float(0), count: 1 * 3 * 224 * 224),
        scalarType: Float.self
    )
}

func normalize(_ input: MLTensor) -> MLTensor {
    (input - 0.5) / 0.5
}
~~~

Compile the exact scalar/operator overloads against the selected SDK. Validate shape and range before execution; do not let the model define the source normalization implicitly.

## 3. Use a scoped `MLComputePolicy`

~~~swift
import CoreML

func runTensorMath(_ input: MLTensor) async -> MLShapedArray<Float> {
    await withMLTensorComputePolicy(.cpuAndGPU) {
        let transformed = input.reshaped(to: [1, 3, 224 * 224])
        return await transformed.shapedArray(of: Float.self)
    }
}
~~~

This is a policy scope, not proof that every operation used the GPU. Record the policy separately from observed device/performance evidence.

## 4. Avoid unnecessary tensor materialization

~~~swift
import CoreML

func summarize(_ tensor: MLTensor) async -> TensorSummary {
    let reduced = tensor.mean(keepRank: false)
    let values = await reduced.shapedArray(of: Float.self)
    return TensorSummary(
        shape: tensor.shape,
        scalarCount: tensor.scalarCount,
        mean: values.first ?? .nan
    )
}

struct TensorSummary: Sendable {
    let shape: [Int]
    let scalarCount: Int
    let mean: Float
}
~~~

Reduce or sample before crossing into CPU/UI memory. A complete tensor-to-array conversion can dominate an otherwise fast compute path.

## 5. Use a no-copy tensor only with owned memory

~~~swift
import CoreML

final class OwnedTensorBytes: @unchecked Sendable {
    let data: Data

    init(data: Data) { self.data = data }
}

func tensorWithoutCopy(_ owner: OwnedTensorBytes) -> MLTensor {
    owner.data.withUnsafeBytes { bytes in
        MLTensor(
            bytesNoCopy: bytes,
            shape: [1, 3, 224, 224],
            scalarType: Float.self,
            deallocator: .none
        )
    }
}
~~~

This is an ownership sketch. The backing allocation must remain valid, correctly aligned, correctly sized, and immutable or synchronized for every consumer. Prefer a copying initializer until a measured no-copy path is proven.

## 6. Validate tensor shapes at the boundary

~~~swift
enum TensorContractError: Error {
    case shapeMismatch(expected: [Int], actual: [Int])
    case scalarTypeMismatch
}

func requireShape(_ tensor: MLTensor, equals expected: [Int]) throws {
    guard tensor.shape == expected else {
        throw TensorContractError.shapeMismatch(
            expected: expected,
            actual: tensor.shape
        )
    }
}
~~~

Reject invalid shapes before a graph, kernel, or model receives them. Dynamic bounds belong in the contract and fixtures.

## 7. Inspect available Core ML compute devices

~~~swift
import CoreML

struct ComputeDeviceSnapshot: Codable, Sendable {
    let available: [String]
}

func availableDevices() -> ComputeDeviceSnapshot {
    ComputeDeviceSnapshot(
        available: MLModel.availableComputeDevices.map(String.init(describing:))
    )
}
~~~

This records availability, not the device used by every tensor or model operation. Pair it with a physical trace.

## 8. Build a BNNS Graph context

~~~swift
import Accelerate

func makeBNNSContext(modelPath: String) async throws -> BNNSGraph.Context {
    try await BNNSGraph.Context(
        compileFromPath: modelPath,
        functionName: "main",
        options: .init()
    )
}
~~~

The initializer/options surface is SDK-sensitive. Keep dynamic shape setup, tensor allocation, workspace, and execution in one adapter.

## 9. Set BNNS dynamic shapes before execution

~~~swift
import Accelerate

func prepareDynamicBNNS(
    _ context: BNNSGraph.Context,
    shape: BNNSGraph.Shape
) async throws {
    _ = try await context.setDynamicShapes(
        [shape],
        forFunction: "main"
    )
}
~~~

Do not mutate dynamic shapes while an execution is in flight. Record the inferred output shapes and allocation sizes.

## 10. Execute a BNNS graph with an owned tensor

~~~swift
import Accelerate

func executeBNNS(
    _ context: BNNSGraph.Context,
    input: inout BNNSTensor,
    output: inout BNNSTensor
) async throws {
    try await context.executeFunction(
        "main",
        arguments: &input
    )
    // Bind/read output according to the current graph contract.
}
~~~

This is an intentionally incomplete binding sketch: compile the exact `BNNSTensor` argument list for the chosen graph. The context and workspace must have a clear actor/queue owner.

## 11. Define an MPSGraph placeholder route

~~~swift
import MetalPerformanceShadersGraph

func buildGraph() -> (
    graph: MPSGraph,
    input: MPSGraphTensor,
    output: MPSGraphTensor
) {
    let graph = MPSGraph()
    let input = graph.placeholder(
        shape: [1, 3, 224, 224],
        dataType: .float32,
        name: "input"
    )
    let output = graph.relu(with: input, name: "relu")
    return (graph, input, output)
}
~~~

Graph operations and overloads evolve; keep graph construction in a named module and preserve the input/output contract for reference tests.

## 12. Compile an MPSGraph executable

~~~swift
import Metal
import MetalPerformanceShadersGraph

func compileGraph(
    graph: MPSGraph,
    input: MPSGraphTensor,
    output: MPSGraphTensor,
    device: MTLDevice
) -> MPSGraphExecutable {
    graph.compile(
        with: MPSGraphDevice(mtlDevice: device),
        feeds: [input: MPSGraphShapedType(
            shape: [1, 3, 224, 224],
            dataType: .float32
        )],
        targetTensors: [output],
        targetOperations: nil,
        compilationDescriptor: nil
    )
}
~~~

Use the SDK’s current `MPSGraphDevice`/shaped-type initializers. Record the device and compilation target; a compiled executable is not a universal artifact.

## 13. Create a Metal buffer with an explicit policy

~~~swift
import Metal

func makeInputBuffer(device: MTLDevice, byteCount: Int) -> MTLBuffer? {
    device.makeBuffer(
        length: byteCount,
        options: [.storageModeShared]
    )
}
~~~

Use shared storage when CPU and GPU both need access; use private storage for GPU-owned intermediates when the data path supports it. Start with the system default unless evidence supports a manual choice.

## 14. Create a buffer-backed texture view

~~~swift
import Metal

func makeTexture(
    from buffer: MTLBuffer,
    device: MTLDevice,
    width: Int,
    height: Int,
    bytesPerRow: Int
) -> MTLTexture? {
    let descriptor = MTLTextureDescriptor.texture2DDescriptor(
        pixelFormat: .rgba8Unorm,
        width: width,
        height: height,
        mipmapped: false
    )
    descriptor.usage = [.shaderRead, .shaderWrite]
    return buffer.makeTexture(
        descriptor: descriptor,
        offset: 0,
        bytesPerRow: bytesPerRow
    )
}
~~~

The pixel format, dimensions, row bytes, storage, and shader binding must match. A texture view can share storage, but shared storage still requires correct synchronization.

## 15. Describe a Metal tensor

~~~swift
import Metal

func makeTensorDescriptor() -> MTLTensorDescriptor {
    let descriptor = MTLTensorDescriptor()
    descriptor.dimensions = MTLTensorExtents([1, 3, 224, 224])
    descriptor.dataType = .float32
    descriptor.storageMode = .private
    descriptor.usage = [.shaderRead, .shaderWrite]
    return descriptor
}

func makeTensor(device: MTLDevice) throws -> any MTLTensor {
    try device.makeTensor(descriptor: makeTensorDescriptor())
}
~~~

Compile the exact tensor data-type/extents/usage APIs. Record the minimum OS/device family and any auxiliary-plane requirements before shipping.

## 16. Bridge a pixel buffer through the texture cache

~~~swift
import CoreVideo
import Metal

struct PixelTexture: Sendable {
    let texture: MTLTexture
    let frameID: Int64
}

func makeTextureFromPixelBuffer(
    pixelBuffer: CVPixelBuffer,
    cache: CVMetalTextureCache,
    device: MTLDevice,
    frameID: Int64
) throws -> PixelTexture {
    // Use CVMetalTextureCacheCreateTextureFromImage for the selected plane,
    // pixel format, width, and height. Retain the CVMetalTexture reference
    // until the command buffer has completed.
    throw TensorContractError.scalarTypeMismatch
}
~~~

The body is intentionally a C-API bridge sketch. Plane selection, color conversion, orientation, cache/device ownership, and lifetime must be compiled and tested for the actual camera format.

## 17. Encode a compute pass

~~~swift
import Metal

func encodeCompute(
    queue: MTLCommandQueue,
    pipeline: MTLComputePipelineState,
    input: MTLBuffer,
    output: MTLBuffer,
    count: Int
) throws -> MTLCommandBuffer {
    guard let commandBuffer = queue.makeCommandBuffer(),
          let encoder = commandBuffer.makeComputeCommandEncoder() else {
        throw TensorContractError.scalarTypeMismatch
    }
    encoder.setComputePipelineState(pipeline)
    encoder.setBuffer(input, offset: 0, index: 0)
    encoder.setBuffer(output, offset: 0, index: 1)
    let width = pipeline.threadExecutionWidth
    let threads = MTLSize(width: count, height: 1, depth: 1)
    let groups = MTLSize(width: (count + width - 1) / width, height: 1, depth: 1)
    encoder.dispatchThreadgroups(groups, threadsPerThreadgroup: MTLSize(width: width, height: 1, depth: 1))
    encoder.endEncoding()
    commandBuffer.commit()
    return commandBuffer
}
~~~

Validate bounds inside the shader. The command buffer owns the encoded work; do not release or mutate input/output resources until completion.

## 18. Await command-buffer completion

~~~swift
import Metal

func awaitCompletion(_ commandBuffer: MTLCommandBuffer) async throws {
    await commandBuffer.completed()
    guard commandBuffer.status == .completed else {
        throw TensorContractError.scalarTypeMismatch
    }
}
~~~

Use the current SDK’s async command-buffer APIs or a completion-handler continuation. Map error/status into a recoverable app state rather than silently publishing stale output.

## 19. Own the queue and in-flight work

~~~swift
import Metal

actor MetalWorkOwner {
    let device: MTLDevice
    let queue: MTLCommandQueue
    private var inFlight = 0
    private let maximumInFlight = 2

    init(device: MTLDevice) throws {
        guard let queue = device.makeCommandQueue() else {
            throw TensorContractError.scalarTypeMismatch
        }
        self.device = device
        self.queue = queue
    }

    func admit() -> Bool {
        guard inFlight < maximumInFlight else { return false }
        inFlight += 1
        return true
    }

    func complete() {
        inFlight = max(0, inFlight - 1)
    }
}
~~~

Use latest-frame/drop policies when appropriate. Bounded work is usually more useful than processing every frame late.

## 20. Guard stale frames

~~~swift
actor FrameGeneration {
    private var generation: UInt64 = 0

    func next() -> UInt64 {
        generation &+= 1
        return generation
    }

    func isCurrent(_ token: UInt64) -> Bool {
        token == generation
    }

    func invalidate() {
        generation &+= 1
    }
}
~~~

Check the generation after GPU/graph completion and before publishing to SwiftUI or committing a domain result.

## 21. Record low-level provenance

~~~swift
struct ComputeProvenance: Codable, Sendable {
    let sourceID: String
    let frameID: Int64?
    let tensorContractRevision: String
    let abstraction: String
    let device: String
    let policy: String
    let storageMode: String?
    let generatedAt: Date
}
~~~

Do not store raw frames or tensor values in this record unless the privacy plan allows it. A redacted provenance record is usually enough to reject stale output and explain a result.

## 22. Map output into a reviewable candidate

~~~swift
struct ComputeCandidate<Value: Codable & Sendable>: Codable, Sendable {
    let value: Value
    let provenance: ComputeProvenance
    let validationWarnings: [String]
    let isFresh: Bool
}

func validateCandidate<Value: Sendable>(
    _ candidate: ComputeCandidate<Value>,
    currentSourceID: String
) -> Bool {
    candidate.isFresh && candidate.provenance.sourceID == currentSourceID
}
~~~

The low-level output becomes a domain proposal only after this adapter and the app-owned validators run.

## 23. Render compute status in SwiftUI

~~~swift
import SwiftUI

struct ComputeStatusView: View {
    let title: String
    let detail: String
    let isConstrained: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Label(title, systemImage: isConstrained ? "battery.25" : "bolt")
                .font(.headline)
            Text(detail)
                .font(.subheadline)
                .foregroundStyle(.secondary)
        }
        .padding()
        .glassEffect()
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Compute status")
        .accessibilityValue("\(title). \(detail)")
    }
}
~~~

Use a current SwiftUI/Liquid Glass availability boundary and a stable opaque/high-contrast fallback. Do not use the glass effect as the only signal for running, stale, or constrained work.

## 24. Separate approval from commit

~~~swift
enum ComputeProposalState<Value: Sendable>: Sendable {
    case running
    case needsReview(ComputeCandidate<Value>)
    case rejected(String)
    case committed
}

func commit<Value: Codable & Sendable>(
    candidate: ComputeCandidate<Value>,
    validated: Bool,
    approved: Bool
) throws {
    guard validated, approved else {
        throw ModelResourceError.invalid("compute candidate is not approved")
    }
    // Invoke the deterministic domain command here.
}
~~~

A completed GPU command is not a user approval and is not a domain mutation.

## 25. Capture a performance record

~~~swift
struct ComputeMeasurement: Codable, Sendable {
    let abstraction: String
    let device: String
    let osBuild: String
    let inputShape: [Int]
    let coldMilliseconds: Double
    let warmP50Milliseconds: Double
    let warmP95Milliseconds: Double
    let peakMemoryBytes: Int
    let droppedFrames: Int
    let thermalNotes: String
}
~~~

Pair this record with signposts, Instruments, the debug gauge/Core ML tools where relevant, and a device/workload identifier. Do not compare different input shapes as if they were the same benchmark.

## 26. Test a fallback policy

~~~swift
enum ComputeFallback: Sendable {
    case mltensor
    case bnnsCPU
    case coreML
    case manual
}

func chooseFallback(
    supportsMetalTensor: Bool,
    supportsGPU: Bool,
    coreMLAvailable: Bool
) -> ComputeFallback {
    if supportsMetalTensor && supportsGPU { return .mltensor }
    if coreMLAvailable { return .coreML }
    return .manual
}
~~~

The real capability check must use current SDK/runtime APIs. A fallback should preserve the user outcome, not merely hide the failure.

## 27. Release checklist

~~~text
[ ] tensor shape/rank/type/layout/stride/plane contract is recorded
[ ] source pixel format/orientation/frame provenance is preserved
[ ] abstraction choice has a baseline and measured rationale
[ ] MLComputePolicy/BNNS/MPSGraph/Metal device policy is explicit
[ ] buffers/textures/tensors have storage, usage, lifetime, and synchronization proof
[ ] no-copy/zero-copy paths have ownership and reuse tests
[ ] command-buffer completion/error/cancellation is handled off the main actor
[ ] numerical and task-level validators pass
[ ] memory/latency/frame/thermal/battery measurements exist
[ ] low-level logs and intermediate values pass privacy review
[ ] SwiftUI status/fallback/review states pass accessibility tasks
[ ] archive/TestFlight physical-device route exercises the final compute path
~~~

## Sources

- [Core ML](https://developer.apple.com/documentation/coreml)
- [MLTensor](https://developer.apple.com/documentation/coreml/mltensor)
- [MLComputePolicy](https://developer.apple.com/documentation/coreml/mlcomputepolicy)
- [MLComputePlan](https://developer.apple.com/documentation/coreml/mlcomputeplan-1w21n)
- [MLComputeDevice](https://developer.apple.com/documentation/coreml/mlcomputedevice)
- [Accelerate](https://developer.apple.com/documentation/accelerate)
- [BNNS](https://developer.apple.com/documentation/accelerate/bnns-library)
- [BNNSGraph.Context](https://developer.apple.com/documentation/accelerate/bnnsgraph/context)
- [Metal](https://developer.apple.com/documentation/metal)
- [MTLBuffer](https://developer.apple.com/documentation/metal/mtlbuffer)
- [MTLTexture](https://developer.apple.com/documentation/metal/mtltexture)
- [MTLDevice](https://developer.apple.com/documentation/metal/mtldevice)
- [MTLCommandBuffer](https://developer.apple.com/documentation/metal/mtlcommandbuffer)
- [Compute passes](https://developer.apple.com/documentation/metal/compute-passes)
- [MTLTensor](https://developer.apple.com/documentation/metal/mtltensor)
- [MTLTensorDescriptor](https://developer.apple.com/documentation/metal/mtltensordescriptor)
- [Setting resource storage modes](https://developer.apple.com/documentation/metal/setting-resource-storage-modes)
- [Choosing a resource storage mode for Apple GPUs](https://developer.apple.com/documentation/metal/choosing-a-resource-storage-mode-for-apple-gpus)
- [Resource fundamentals](https://developer.apple.com/documentation/metal/resource-fundamentals)
- [Metal Performance Shaders Graph](https://developer.apple.com/documentation/metalperformanceshadersgraph)
- [MPSGraph](https://developer.apple.com/documentation/metalperformanceshadersgraph/mpsgraph)
- [CVMetalTextureCacheCreateTextureFromImage](https://developer.apple.com/documentation/corevideo/cvmetaltexturecachecreatetexturefromimage%28_%3A_%3A_%3A_%3A_%3A_%3A_%3A_%3A_%3A%29?changes=_3_2&language=objc)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
