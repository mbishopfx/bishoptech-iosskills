# Metal, Core Image, VideoToolbox, and GPU media recipes

These are compile-oriented sketches. Compile each route in the target that owns the framework and feature, then verify it on the device/GPU/media workload that the product claims to support.

## 1. Reusable Metal device and queue

~~~swift
import Metal

final class MetalRenderer {
    let device: any MTLDevice
    let queue: any MTLCommandQueue

    init?() {
        guard
            let device = MTLCreateSystemDefaultDevice(),
            let queue = device.makeCommandQueue()
        else {
            return nil
        }
        self.device = device
        self.queue = queue
    }
}
~~~

Keep all Metal resources created from the same device. Reuse the command queue and pipeline states. Do not create a queue or compile shaders inside a per-frame callback.

## 2. Core Image context backed by Metal

~~~swift
import CoreImage
import Metal

final class ImageProcessor {
    let context: CIContext

    init?(device: any MTLDevice) {
        context = CIContext(mtlDevice: device)
    }

    func render(_ image: CIImage, colorSpace: CGColorSpace) -> CGImage? {
        context.createCGImage(
            image,
            from: image.extent,
            colorSpace: colorSpace
        )
    }
}
~~~

Create a small number of contexts and reuse them. CIImage and CIContext are immutable; isolate each mutable CIFilter instance per operation or processing task.

## 3. Core Image filter graph

~~~swift
import CoreImage

func makeEffect(
    input: CIImage,
    amount: Double
) -> CIImage? {
    guard
        let filter = CIFilter(name: "CIColorControls")
    else {
        return nil
    }

    filter.setValue(input, forKey: kCIInputImageKey)
    filter.setValue(amount, forKey: kCIInputSaturationKey)
    return filter.outputImage
}
~~~

The output image is a lazy graph. Force a render to a declared destination before calling the result exported, saved, or shared. Set color-space and format policy at the render boundary.

## 4. Bounded live-frame processing

~~~swift
import CoreImage
import CoreVideo

final class FrameGate {
    private var isProcessing = false

    func accept(_ buffer: CVPixelBuffer) -> Bool {
        guard isProcessing == false else {
            return false
        }
        isProcessing = true
        process(buffer)
        return true
    }

    private func process(_ buffer: CVPixelBuffer) {
        defer { isProcessing = false }
        let image = CIImage(cvPixelBuffer: buffer)
        // Render to a bounded destination or enqueue a controlled result.
        _ = image
    }
}
~~~

This is intentionally simple: a real capture route needs queue/actor isolation, cancellation, timestamps, pixel-format validation, and a UI state adapter. Decide whether to drop, coalesce, or block frames before the queue grows.

## 5. Metal shader and pipeline loading

~~~swift
import Metal

func makeComputePipeline(
    device: any MTLDevice,
    functionName: String
) throws -> any MTLComputePipelineState {
    guard let library = device.makeDefaultLibrary(),
          let function = library.makeFunction(name: functionName)
    else {
        throw NSError(
            domain: "MetalRoute",
            code: 1,
            userInfo: [NSLocalizedDescriptionKey: "Shader function unavailable."]
        )
    }
    return try device.makeComputePipelineState(function: function)
}
~~~

Cache the pipeline state by shader/effect version. Add a known fallback when a function or required feature is unavailable. Run Shader Validation in development and record its overhead separately from production performance.

## 6. Metal compute command boundary

~~~swift
import Metal

func encodeCompute(
    pipeline: any MTLComputePipelineState,
    queue: any MTLCommandQueue,
    input: any MTLBuffer,
    output: any MTLBuffer
) -> MTLCommandBuffer? {
    guard
        let commandBuffer = queue.makeCommandBuffer(),
        let encoder = commandBuffer.makeComputeCommandEncoder()
    else {
        return nil
    }

    encoder.setComputePipelineState(pipeline)
    encoder.setBuffer(input, offset: 0, index: 0)
    encoder.setBuffer(output, offset: 0, index: 1)
    encoder.dispatchThreads(
        MTLSize(width: 1024, height: 1, depth: 1),
        threadsPerThreadgroup: MTLSize(
            width: max(1, pipeline.threadExecutionWidth),
            height: 1,
            depth: 1
        )
    )
    encoder.endEncoding()
    commandBuffer.commit()
    return commandBuffer
}
~~~

The thread/grid size is illustrative and must be derived from the actual data shape and pipeline limits. Add completion/error handling and resource lifetime in the target implementation.

## 7. Metal 4 availability adapter

~~~swift
import Metal

enum GPUCommandRoute {
    case classic(any MTLCommandQueue)
    case metal4(any MTL4CommandQueue)
}

func chooseGPUCommandRoute(
    device: any MTLDevice
) -> GPUCommandRoute? {
    if #available(iOS 26.0, *) {
        if let queue = device.makeMTL4CommandQueue() {
            return .metal4(queue)
        }
    }
    guard let queue = device.makeCommandQueue() else {
        return nil
    }
    return .classic(queue)
}
~~~

The availability and feature requirements must be compiled against the selected SDK. Metal 4 and classic Metal are not interchangeable at the command/resource API level; keep the adapter boundary explicit.

## 8. VideoToolbox session shape

~~~swift
import CoreMedia
import CoreVideo
import VideoToolbox

final class CompressionRoute {
    private var session: VTCompressionSession?

    func invalidate() {
        if let session {
            VTCompressionSessionCompleteFrames(
                session,
                untilPresentationTimeStamp: .invalid
            )
            VTCompressionSessionInvalidate(session)
        }
        session = nil
    }

    func submit(
        imageBuffer: CVImageBuffer,
        presentationTimeStamp: CMTime,
        duration: CMTime
    ) -> OSStatus {
        guard let session else {
            return -1
        }
        return VTCompressionSessionEncodeFrame(
            session,
            imageBuffer: imageBuffer,
            presentationTimeStamp: presentationTimeStamp,
            duration: duration,
            frameProperties: nil,
            sourceFrameRefcon: nil,
            infoFlagsOut: nil
        )
    }
}
~~~

Creation, output callback/handler, codec properties, pixel-buffer attributes, and container writing are target-specific. Complete pending frames before invalidation and treat callback ordering/status as part of the evidence packet.

## 9. Export handoff

~~~swift
import AVFoundation

func exportAsset(
    _ asset: AVAsset,
    to outputURL: URL,
    completion: @escaping (Result<URL, Error>) -> Void
) {
    guard let session = AVAssetExportSession(
        asset: asset,
        presetName: AVAssetExportPresetHighestQuality
    ) else {
        completion(.failure(
            NSError(
                domain: "MediaRoute",
                code: 1,
                userInfo: [NSLocalizedDescriptionKey: "Export preset unavailable."]
            )
        ))
        return
    }

    session.outputURL = outputURL
    session.outputFileType = .mp4
    session.exportAsynchronously {
        switch session.status {
        case .completed:
            completion(.success(outputURL))
        case .failed:
            completion(.failure(
                session.error ?? NSError(
                    domain: "MediaRoute",
                    code: 2
                )
            ))
        case .cancelled:
            completion(.failure(
                CocoaError(.userCancelled)
            ))
        default:
            break
        }
    }
}
~~~

Reopen and validate the output before showing “exported.” The chosen container, codec, audio tracks, timestamps, orientation, and destination support are separate facts.

## 10. Effect proposal model

~~~swift
struct VisualEffectProposal: Codable, Sendable, Equatable {
    let sourceID: String
    let sourceRevision: String?
    let effectName: String
    let intensity: Double
    let colorSpace: String
    let outputType: String
    let modelVersion: String?
}

func validate(_ proposal: VisualEffectProposal) -> Bool {
    (0.0...1.0).contains(proposal.intensity) &&
    proposal.sourceID.isEmpty == false &&
    proposal.effectName.isEmpty == false
}
~~~

The commit layer should also validate the actual source revision, effect availability, color/output policy, resource budget, and user confirmation. A valid proposal is not automatically an approved export.

## 11. SwiftUI rendering state

~~~swift
import SwiftUI

enum RenderState: Equatable {
    case idle
    case preparing
    case live(fps: Double)
    case degraded(reason: String)
    case exporting(progress: Double)
    case ready(URL)
    case failed(String)
}

struct RenderStatusView: View {
    let state: RenderState

    var body: some View {
        switch state {
        case .idle:
            Text("Ready")
        case .preparing:
            ProgressView("Preparing")
        case .live(let fps):
            Text("Live \(fps, specifier: "%.0f") frames per second")
        case .degraded(let reason):
            Label(reason, systemImage: "exclamationmark.triangle")
        case .exporting(let progress):
            ProgressView(value: progress) {
                Text("Exporting")
            }
        case .ready:
            Label("Review output", systemImage: "checkmark.circle")
        case .failed(let message):
            Label(message, systemImage: "xmark.circle")
        }
    }
}
~~~

Keep technical status understandable and avoid claiming a fixed frame rate unless the state is backed by the named workload measurement. Add accessibility announcements or equivalent text for transitions.

## 12. Fixture and performance record

~~~swift
struct RenderFixture: Sendable, Equatable {
    let id: String
    let width: Int
    let height: Int
    let pixelFormat: String
    let colorSpace: String
    let frameRate: Double
    let expectedOutput: String
}

struct RenderMeasurement: Sendable, Equatable {
    let fixtureID: String
    let device: String
    let gpuFamily: String
    let cpuMilliseconds: Double
    let gpuMilliseconds: Double
    let memoryBytes: Int64
    let droppedFrames: Int
    let thermalState: String
}
~~~

Record measurements in release-like builds on every claimed device class. Keep Shader Validation, debug logging, and GPU capture runs separate from production performance claims.

## Verification stop list

- Compile each route in its owning target.
- Inspect the selected SDK/deployment target and Metal feature set.
- Test Core Image color/format/output and concurrent filter isolation.
- Test bounded live processing and cancellation.
- Test VideoToolbox callbacks, pending-frame completion, invalidation, and container output.
- Test shader validation and then separate production performance.
- Test reduced motion/transparency, VoiceOver, Dynamic Type, and fallback routes.
- Prove AI proposals cannot mutate/export/share without explicit approval.

## Sources

- [Metal](https://developer.apple.com/documentation/metal)
- [MTLDevice](https://developer.apple.com/documentation/metal/mtldevice)
- [Understanding the Metal 4 core API](https://developer.apple.com/documentation/metal/understanding-the-metal-4-core-api)
- [MTLCommandQueue](https://developer.apple.com/documentation/metal/mtlcommandqueue)
- [MTLCommandBuffer](https://developer.apple.com/documentation/metal/mtlcommandbuffer)
- [MTLComputePipelineState](https://developer.apple.com/documentation/metal/mtlcomputepipelinestate)
- [MTLRenderPipelineState](https://developer.apple.com/documentation/metal/mtlrenderpipelinestate)
- [Metal feature set tables](https://developer.apple.com/metal/Metal-Feature-Set-Tables.pdf)
- [Validating your app’s Metal shader usage](https://developer.apple.com/documentation/xcode/validating-your-apps-metal-shader-usage)
- [Core Image](https://developer.apple.com/documentation/coreimage)
- [CIContext](https://developer.apple.com/documentation/coreimage/cicontext)
- [CIImage](https://developer.apple.com/documentation/coreimage/ciimage)
- [VideoToolbox](https://developer.apple.com/documentation/videotoolbox)
- [VTCompressionSession](https://developer.apple.com/documentation/videotoolbox/vtcompressionsession-api-collection)
- [VTDecompressionSession](https://developer.apple.com/documentation/videotoolbox/vtdecompressionsession-api-collection)
- [AVFoundation](https://developer.apple.com/documentation/avfoundation/)
- [AVAssetWriter](https://developer.apple.com/documentation/avfoundation/avassetwriter)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
