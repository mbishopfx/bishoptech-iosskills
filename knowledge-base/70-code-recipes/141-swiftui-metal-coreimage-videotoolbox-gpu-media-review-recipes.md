# SwiftUI Metal, Core Image, and VideoToolbox GPU-media review recipes

These are compile-oriented route sketches for an iOS SwiftUI GPU/media feature. They are intentionally incomplete app slices: verify exact signatures, availability, imports, target membership, shader library names, pixel formats, color policy, privacy strings, and SDK behavior in the selected Xcode project. They do not claim to compile in this documentation-only workspace or prove physical-device performance, camera behavior, or codec output.

Use them with the [GPU-media deep dive](../42-framework-deep-dives/98-swiftui-metal-coreimage-videotoolbox-gpu-media-review.md), [design companion](../21-design-deep-dives/126-swiftui-metal-coreimage-videotoolbox-gpu-media-review-design.md), [capability route](../50-capability-recipes/129-swiftui-metal-coreimage-videotoolbox-gpu-media-review-route.md), and [proof matrix](../60-verification/123-swiftui-metal-coreimage-videotoolbox-gpu-media-review-proof-matrix.md).

## Recipe 1: source and output envelopes

Keep source metadata, renderer state, AI proposals, and domain actions separate:

~~~swift
import CoreVideo
import Foundation

struct MediaSourceEnvelope: Sendable {
    var revision: Int
    var sourceID: String
    var kind: String
    var width: Int
    var height: Int
    var pixelFormat: UInt32?
    var orientation: String
    var colorPolicy: String
    var timestamp: TimeInterval?
    var isLive: Bool
}

enum MediaRenderState: Equatable, Sendable {
    case idle
    case preparing
    case rendering
    case live
    case waiting
    case droppedFrame
    case stale
    case reducedQuality
    case unavailable(String)
    case failed(String)
    case complete
}

struct MediaOutputEnvelope: Sendable {
    var sourceRevision: Int
    var state: MediaRenderState
    var outputDescription: String
    var isPreview: Bool
    var renderedAt: Date?
    var errorMessage: String?
}
~~~

Implementation notes:

- Increment revision when the source, crop, effect intent, or output policy changes.
- Keep a frame timestamp as provenance, not as the only freshness test.
- Do not put a CVPixelBuffer, MTLTexture, or CIContext directly in long-lived SwiftUI value state.
- Keep preview and export outputs distinct.
- Include format, orientation, and color policy in review data when they can change the result.

## Recipe 2: Canvas with semantic controls

Canvas can draw a custom visualization while SwiftUI provides the accessible source and controls:

~~~swift
import SwiftUI

struct SignalCanvas: View {
    let samples: [CGFloat]
    @Binding var showMarkers: Bool

    var body: some View {
        VStack(alignment: .leading) {
            Text("Signal preview")
                .font(.headline)

            Canvas(opaque: false, colorMode: .linear, rendersAsynchronously: true) { context, size in
                guard samples.count > 1 else { return }
                let step = size.width / CGFloat(samples.count - 1)
                var path = Path()
                for (index, sample) in samples.enumerated() {
                    let x = CGFloat(index) * step
                    let y = size.height * (1 - sample)
                    if index == 0 {
                        path.move(to: CGPoint(x: x, y: y))
                    } else {
                        path.addLine(to: CGPoint(x: x, y: y))
                    }
                }
                context.stroke(path, with: .color(.accentColor), lineWidth: 2)
            }
            .frame(minHeight: 180)
            .accessibilityElement(children: .ignore)
            .accessibilityLabel("Signal preview")
            .accessibilityValue("A plotted signal with \(samples.count) samples")

            Toggle("Show markers", isOn: $showMarkers)
        }
        .padding()
    }
}
~~~

The individual path points are not automatically independent accessibility elements. Provide a list, table, summary, or adjustable controls when the person needs to inspect or edit the underlying data. Test the chosen Canvas color mode and scaling behavior in the selected target.

## Recipe 3: bounded SwiftUI Shader effect

Use an app-owned shader name and bounded arguments. The exact shader library declaration and argument API must be verified in the selected Xcode target:

~~~swift
import SwiftUI

struct SoftHighlightView: View {
    let intensity: CGFloat
    let isAvailable: Bool

    var body: some View {
        RoundedRectangle(cornerRadius: 28, style: .continuous)
            .fill(.blue.gradient)
            .overlay {
                Text("Preview")
                    .font(.title2.weight(.semibold))
                    .foregroundStyle(.white)
            }
            .modifier(SoftHighlightModifier(
                intensity: min(max(intensity, 0), 1),
                isAvailable: isAvailable
            ))
            .accessibilityLabel("Soft highlight preview")
            .accessibilityHint("A visual preview effect. The source remains unchanged until you apply it.")
    }
}

struct SoftHighlightModifier: ViewModifier {
    let intensity: CGFloat
    let isAvailable: Bool

    func body(content: Content) -> some View {
        if isAvailable {
            content.colorEffect(
                ShaderLibrary.softHighlight(
                    .float(Float(intensity))
                )
            )
        } else {
            content
                .overlay(alignment: .bottom) {
                    Text("Preview effect unavailable")
                        .font(.caption)
                        .padding(8)
                        .background(.regularMaterial, in: Capsule())
                }
        }
    }
}
~~~

Keep the shader function in a known allowlist. A model can propose softHighlight and a value in a validated range; it must not supply arbitrary source, function names, or unbounded coordinates. Provide a native fallback when the effect is unavailable or an accessibility setting calls for reduced visual complexity.

## Recipe 4: reusable Core Image context

CIImage is a lazy recipe. Render it through a deliberately reused CIContext:

~~~swift
import CoreImage
import CoreImage.CIFilterBuiltins
import CoreVideo

final class ImageFilterRenderer {
    private let context: CIContext

    init(device: MTLDevice? = nil) {
        if let device {
            context = CIContext(mtlDevice: device)
        } else {
            context = CIContext()
        }
    }

    func makePreview(
        from pixelBuffer: CVPixelBuffer,
        sourceRevision: Int,
        amount: Float
    ) throws -> MediaOutputEnvelope {
        let input = CIImage(cvPixelBuffer: pixelBuffer)
        let filter = CIFilter.sepiaTone()
        filter.inputImage = input
        filter.intensity = min(max(amount, 0), 1)

        guard let output = filter.outputImage else {
            throw RenderError.noOutput
        }

        let extent = output.extent
        guard !extent.isEmpty else {
            throw RenderError.emptyExtent
        }

        // Choose an explicit color space and destination in the real app.
        _ = output
        return MediaOutputEnvelope(
            sourceRevision: sourceRevision,
            state: .complete,
            outputDescription: "Core Image preview recipe",
            isPreview: true,
            renderedAt: Date(),
            errorMessage: nil
        )
    }
}

enum RenderError: Error {
    case noOutput
    case emptyExtent
}
~~~

This sketch omits the destination render call because the correct output depends on the target: a CGImage, CVPixelBuffer, MTLTexture, or file export. In production:

- reuse the context for the feature lifetime;
- isolate mutable CIFilter instances per task or synchronize them;
- select working and destination color spaces deliberately;
- reject stale source revisions before publishing a result;
- keep the source buffer alive through the render operation.

## Recipe 5: CVPixelBuffer to Metal texture

The conversion path must validate the format and plane policy:

~~~swift
import CoreVideo
import Metal

final class PixelBufferTextureBridge {
    let device: MTLDevice
    let cache: CVMetalTextureCache

    init(device: MTLDevice) throws {
        self.device = device
        var createdCache: CVMetalTextureCache?
        let status = CVMetalTextureCacheCreate(
            kCFAllocatorDefault,
            nil,
            device,
            nil,
            &createdCache
        )
        guard status == kCVReturnSuccess, let createdCache else {
            throw TextureBridgeError.cacheCreationFailed(status)
        }
        cache = createdCache
    }

    func makeTexture(
        from pixelBuffer: CVPixelBuffer,
        pixelFormat: MTLPixelFormat,
        plane: Int = 0
    ) throws -> CVMetalTexture {
        let width = CVPixelBufferGetWidthOfPlane(pixelBuffer, plane)
        let height = CVPixelBufferGetHeightOfPlane(pixelBuffer, plane)
        var texture: CVMetalTexture?

        let status = CVMetalTextureCacheCreateTextureFromImage(
            kCFAllocatorDefault,
            cache,
            pixelBuffer,
            nil,
            pixelFormat,
            width,
            height,
            plane,
            &texture
        )

        guard status == kCVReturnSuccess, let texture else {
            throw TextureBridgeError.textureCreationFailed(status)
        }
        return texture
    }
}

enum TextureBridgeError: Error {
    case cacheCreationFailed(OSStatus)
    case textureCreationFailed(OSStatus)
}
~~~

For bi-planar formats, create and process each supported plane deliberately. Do not assume a texture created from plane zero is a complete color image. The pixel buffer and its derived texture must remain valid until all consumers finish according to the chosen ownership and command-completion policy.

## Recipe 6: Metal device, queue, and compute submission

Create long-lived GPU objects during setup and bound each submission:

~~~swift
import Metal

final class ComputeRenderer {
    let device: MTLDevice
    let commandQueue: MTLCommandQueue
    let pipeline: MTLComputePipelineState

    init(functionName: String) throws {
        guard let device = MTLCreateSystemDefaultDevice() else {
            throw MetalError.noDevice
        }
        guard let queue = device.makeCommandQueue() else {
            throw MetalError.noQueue
        }
        guard let library = device.makeDefaultLibrary(),
              let function = library.makeFunction(name: functionName) else {
            throw MetalError.functionUnavailable
        }
        pipeline = try device.makeComputePipelineState(function: function)
        self.device = device
        commandQueue = queue
    }

    func submit(
        source: MTLTexture,
        destination: MTLTexture,
        completion: @escaping (Result<Void, Error>) -> Void
    ) {
        guard let commandBuffer = commandQueue.makeCommandBuffer(),
              let encoder = commandBuffer.makeComputeCommandEncoder() else {
            completion(.failure(MetalError.commandSetupFailed))
            return
        }

        encoder.setComputePipelineState(pipeline)
        encoder.setTexture(source, index: 0)
        encoder.setTexture(destination, index: 1)

        let width = pipeline.threadExecutionWidth
        let height = max(1, pipeline.maxTotalThreadsPerThreadgroup / width)
        let threadsPerGrid = MTLSize(
            width: source.width,
            height: source.height,
            depth: 1
        )
        let threadsPerGroup = MTLSize(
            width: width,
            height: height,
            depth: 1
        )
        encoder.dispatchThreads(threadsPerGrid, threadsPerThreadgroup: threadsPerGroup)
        encoder.endEncoding()

        commandBuffer.addCompletedHandler { buffer in
            if let error = buffer.error {
                completion(.failure(error))
            } else {
                completion(.success(()))
            }
        }
        commandBuffer.commit()
    }
}

enum MetalError: Error {
    case noDevice
    case noQueue
    case functionUnavailable
    case commandSetupFailed
}
~~~

This is a route sketch, not a complete scheduler. Add a bounded in-flight policy, source-revision check, resource lifetime policy, and main-actor result handoff. Do not create a new queue or pipeline for each frame. Verify threadgroup sizes and texture usage for the actual kernel.

## Recipe 7: MTKView bridge

A thin UIViewRepresentable can host an MTKView while a coordinator owns the renderer:

~~~swift
import MetalKit
import SwiftUI

struct MetalSurface: UIViewRepresentable {
    @ObservedObject var model: MetalSurfaceModel

    func makeCoordinator() -> Coordinator {
        Coordinator(model: model)
    }

    func makeUIView(context: Context) -> MTKView {
        let view = MTKView(frame: .zero, device: context.coordinator.device)
        view.delegate = context.coordinator
        view.enableSetNeedsDisplay = false
        view.isPaused = false
        context.coordinator.attach(to: view)
        return view
    }

    func updateUIView(_ view: MTKView, context: Context) {
        context.coordinator.update(view: view, model: model)
    }

    static func dismantleUIView(_ view: MTKView, coordinator: Coordinator) {
        coordinator.stop(view: view)
    }

    final class Coordinator: NSObject, MTKViewDelegate {
        let device: MTLDevice
        private let model: MetalSurfaceModel

        init(model: MetalSurfaceModel) {
            guard let device = MTLCreateSystemDefaultDevice() else {
                fatalError("Use a fallback before creating this surface")
            }
            self.device = device
            self.model = model
        }

        func attach(to view: MTKView) {
            // Configure pixel format, drawable policy, and renderer state once.
        }

        func update(view: MTKView, model: MetalSurfaceModel) {
            // Update typed state; do not rebuild device or pipeline here.
        }

        func draw(in view: MTKView) {
            // Encode one bounded frame and present when the drawable is available.
        }

        func mtkView(_ view: MTKView, drawableSizeWillChange size: CGSize) {
            // Rebuild size-dependent state only.
        }

        func stop(view: MTKView) {
            view.delegate = nil
            view.isPaused = true
            // Cancel tasks and reject late callbacks in the real renderer.
        }
    }
}
~~~

The real model should expose a non-Metal fallback before constructing the bridge. A static fixture or preview cannot prove drawable availability, frame pacing, or thermal behavior.

## Recipe 8: bounded live-frame consumer

Keep the latest useful frame instead of allowing an unbounded task queue:

~~~swift
actor LatestFrameConsumer<Frame: Sendable> {
    private var pending: Frame?
    private var isProcessing = false
    private var isStopped = false

    func submit(_ frame: Frame, process: @escaping @Sendable (Frame) async -> Void) {
        guard !isStopped else { return }
        pending = frame
        guard !isProcessing else { return }
        isProcessing = true
        Task {
            await drain(process: process)
        }
    }

    func stop() {
        isStopped = true
        pending = nil
    }

    private func drain(
        process: @escaping @Sendable (Frame) async -> Void
    ) async {
        while !isStopped {
            guard let frame = pending else {
                isProcessing = false
                return
            }
            pending = nil
            await process(frame)
        }
        isProcessing = false
    }
}
~~~

This sketch needs an app-specific cancellation and result-publication policy. Include the source revision in Frame. For offline export, process every frame through a bounded sequence instead of using latest-frame behavior. Record dropped-frame policy in the UI and proof packet.

## Recipe 9: typed local AI proposal

Constrain model output before it reaches a media operation:

~~~swift
struct MediaProposal: Codable, Sendable {
    var effect: String
    var intensity: Double
    var explanation: String
}

enum ApprovedEffect: String, CaseIterable, Sendable {
    case softHighlight
    case monochrome
    case cropToSubject
}

func validate(
    _ proposal: MediaProposal,
    sourceRevision: Int,
    currentRevision: Int
) -> (ApprovedEffect, Double, String)? {
    guard sourceRevision == currentRevision else { return nil }
    guard let effect = ApprovedEffect(rawValue: proposal.effect) else { return nil }
    guard proposal.intensity.isFinite else { return nil }
    let intensity = min(max(proposal.intensity, 0), 1)
    return (effect, intensity, proposal.explanation)
}
~~~

The actual Foundation Models session, availability check, authorization, and cancellation belong in the app’s model layer. Keep the proposal source-linked and reviewable. Never interpolate a proposal into shader source or use it as an unchecked Metal function/codec identifier.

## Recipe 10: VideoToolbox session boundary

VideoToolbox session calls vary by codec and selected SDK; keep the lifecycle visible:

~~~swift
import CoreMedia
import VideoToolbox

final class CompressionSessionOwner {
    private var session: VTCompressionSession?
    private var isStopping = false

    func start(width: Int32, height: Int32) throws {
        var created: VTCompressionSession?
        let status = VTCompressionSessionCreate(
            allocator: nil,
            width: width,
            height: height,
            codecType: kCMVideoCodecType_H264,
            encoderSpecification: nil,
            imageBufferAttributes: nil,
            compressedDataAllocator: nil,
            outputCallback: nil,
            refcon: nil,
            compressionSessionOut: &created
        )
        guard status == noErr, let created else {
            throw CodecError.creationFailed(status)
        }
        session = created
        // Set only properties supported by the selected codec/target.
    }

    func encode(_ imageBuffer: CVImageBuffer, presentationTime: CMTime) throws {
        guard let session, !isStopping else {
            throw CodecError.notRunning
        }
        let status = VTCompressionSessionEncodeFrame(
            session,
            imageBuffer: imageBuffer,
            presentationTimeStamp: presentationTime,
            duration: .invalid,
            frameProperties: nil,
            sourceFrameRefcon: nil,
            infoFlagsOut: nil
        )
        guard status == noErr else {
            throw CodecError.encodeFailed(status)
        }
    }

    func stop() {
        guard let session else { return }
        isStopping = true
        VTCompressionSessionCompleteFrames(session, untilPresentationTimeStamp: .invalid)
        VTCompressionSessionInvalidate(session)
        self.session = nil
    }
}

enum CodecError: Error {
    case creationFailed(OSStatus)
    case notRunning
    case encodeFailed(OSStatus)
}
~~~

The output callback and destination writer are intentionally omitted. Implement them with the selected codec’s format description, timing, container, cancellation, and error policy. Independently inspect or play the resulting file. Do not present a successful session creation as proof of a complete export.

## Recipe 11: teardown and fallback

Make teardown an explicit state transition:

~~~swift
@MainActor
final class MediaFeatureModel: ObservableObject {
    @Published private(set) var state: MediaRenderState = .idle
    private var generation = UUID()
    private var tasks: [Task<Void, Never>] = []

    func begin() {
        generation = UUID()
        state = .preparing
    }

    func stop() {
        generation = UUID()
        tasks.forEach { $0.cancel() }
        tasks.removeAll()
        state = .idle
    }

    func publish(
        generation expected: UUID,
        state newState: MediaRenderState
    ) {
        guard expected == generation else { return }
        state = newState
    }

    func showFallback(_ message: String) {
        state = .unavailable(message)
    }
}
~~~

Use the same generation boundary for camera consumers, Core Image tasks, Metal completion handlers, codec callbacks, and AI proposals. Cancel or invalidate the underlying framework object as required; a SwiftUI state check alone does not release a pixel buffer, command, display link, or codec session.

## Recipe 12: proof handoff record

Keep a small record next to an implementation ticket or test run:

~~~swift
struct GPUMediaProofRecord: Codable, Sendable {
    var build: String
    var target: String
    var device: String
    var os: String
    var rendererRoute: String
    var sourceFormat: String
    var colorPolicy: String
    var inFlightLimit: Int
    var droppedFramePolicy: String
    var thermalPolicy: String
    var accessibilityModes: [String]
    var aiAvailability: String
    var physicalDeviceEvidencePath: String?
    var archiveEvidencePath: String?
}
~~~

The record is not a replacement for screenshots, logs, profiling captures, or release evidence. It makes unsupported assumptions visible and gives the next implementation a reproducible starting point.

## Sources

- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Canvas](https://developer.apple.com/documentation/swiftui/canvas)
- [GraphicsContext](https://developer.apple.com/documentation/swiftui/graphicscontext)
- [Shader](https://developer.apple.com/documentation/swiftui/shader)
- [Graphics and rendering modifiers](https://developer.apple.com/documentation/swiftui/view-graphics-and-rendering)
- [Core Image](https://developer.apple.com/documentation/coreimage)
- [CIImage](https://developer.apple.com/documentation/coreimage/ciimage)
- [CIContext](https://developer.apple.com/documentation/coreimage/cicontext)
- [CIFilter](https://developer.apple.com/documentation/coreimage/cifilter-swift.class)
- [Core Video](https://developer.apple.com/documentation/corevideo)
- [CVPixelBuffer](https://developer.apple.com/documentation/corevideo/cvpixelbuffer)
- [CVPixelBufferPool](https://developer.apple.com/documentation/corevideo/cvpixelbufferpool)
- [CVMetalTextureCache](https://developer.apple.com/documentation/corevideo/cvmetaltexturecache)
- [CVMetalTexture](https://developer.apple.com/documentation/corevideo/cvmetaltexture)
- [Metal](https://developer.apple.com/documentation/metal)
- [MTLDevice](https://developer.apple.com/documentation/metal/mtldevice)
- [MTLCommandQueue](https://developer.apple.com/documentation/metal/mtlcommandqueue)
- [MTLCommandBuffer](https://developer.apple.com/documentation/metal/mtlcommandbuffer)
- [MTLRenderPipelineState](https://developer.apple.com/documentation/metal/mtlrenderpipelinestate)
- [MTLComputePipelineState](https://developer.apple.com/documentation/metal/mtlcomputepipelinestate)
- [Setting up a command structure](https://developer.apple.com/documentation/metal/gpu_devices_and_work_submission/setting_up_a_command_structure)
- [Performing calculations on a GPU](https://developer.apple.com/documentation/metal/performing-calculations-on-a-gpu)
- [MetalKit](https://developer.apple.com/documentation/metalkit)
- [MTKView](https://developer.apple.com/documentation/metalkit/mtkview)
- [VideoToolbox](https://developer.apple.com/documentation/videotoolbox)
- [VideoToolbox compression session APIs](https://developer.apple.com/documentation/videotoolbox/vtcompressionsession-api-collection)
- [VideoToolbox decompression session APIs](https://developer.apple.com/documentation/videotoolbox/vtdecompressionsession-api-collection)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)

## Related routes

- [SwiftUI Metal/Core Image/VideoToolbox GPU-media design](../21-design-deep-dives/126-swiftui-metal-coreimage-videotoolbox-gpu-media-review-design.md)
- [SwiftUI Metal/Core Image/VideoToolbox GPU-media review](../42-framework-deep-dives/98-swiftui-metal-coreimage-videotoolbox-gpu-media-review.md)
- [SwiftUI Metal/Core Image/VideoToolbox GPU-media route](../50-capability-recipes/129-swiftui-metal-coreimage-videotoolbox-gpu-media-review-route.md)
- [SwiftUI Metal/Core Image/VideoToolbox GPU-media proof matrix](../60-verification/123-swiftui-metal-coreimage-videotoolbox-gpu-media-review-proof-matrix.md)
