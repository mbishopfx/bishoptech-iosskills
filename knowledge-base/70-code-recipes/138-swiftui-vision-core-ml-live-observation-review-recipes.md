# SwiftUI Vision and Core ML live-observation review recipes

These recipes are compile-oriented route sketches for a named iOS target. They keep camera delegates, pixel buffers, Vision requests, Core ML models, typed observations, SwiftUI presentation, AI proposals, and side effects separate. Compile and run them against the selected SDK and a signed physical-camera target; a pasted recipe is not camera, model, privacy, accessibility, or release proof.

Pairs with [SwiftUI Vision and Core ML live-observation review](../42-framework-deep-dives/95-swiftui-vision-core-ml-live-observation-review.md), [the live-observation route](../50-capability-recipes/126-swiftui-vision-core-ml-live-observation-review-route.md), and [the proof matrix](../60-verification/120-swiftui-vision-core-ml-live-observation-review-proof-matrix.md).

## Recipe 1: model the route states

~~~swift
enum LiveObservationState {
    case unavailable(String)
    case requestingAccess
    case configuring
    case modelLoading
    case ready
    case sampling(lastFrameID: UInt64?)
    case reported(ObservationSnapshot)
    case stale(ObservationSnapshot)
    case proposal(ProposalSnapshot)
    case failed(String)
}

struct ObservationSnapshot: Identifiable, Sendable {
    let id: UUID
    let frameID: UInt64
    let sourceTime: CMTime
    let label: String?
    let confidence: Float?
    let normalizedRect: CGRect?
    let sourceDescription: String
    let isStale: Bool
}

struct ProposalSnapshot: Identifiable, Sendable {
    let id: UUID
    let sourceObservationID: UUID
    let sourceFrameID: UInt64
    let text: String
    let warnings: [String]
    let canApply: Bool
}
~~~

The route state is not AVCaptureSession running state, a model state, or physical truth. It is the product projection of those inputs.

## Recipe 2: request camera access

~~~swift
import AVFoundation

func requestCameraAccess() async -> Bool {
    let status = AVCaptureDevice.authorizationStatus(for: .video)

    switch status {
    case .authorized:
        return true
    case .notDetermined:
        return await AVCaptureDevice.requestAccess(for: .video)
    case .denied, .restricted:
        return false
    @unknown default:
        return false
    }
}
~~~

Add NSCameraUsageDescription to the actual application target before this code runs. If camera access is denied, keep a recoverable UI state and do not start the session.

## Recipe 3: own the capture session and analysis queue

~~~swift
final class CameraAnalyzer: NSObject, AVCaptureVideoDataOutputSampleBufferDelegate {
    let analysisQueue = DispatchQueue(
        label: "com.example.app.camera-analysis",
        qos: .userInitiated
    )

    let session = AVCaptureSession()
    private let videoOutput = AVCaptureVideoDataOutput()
    private var frameID: UInt64 = 0
    private var analysisBusy = false
    private var sessionRevision = 0

    func configure(device: AVCaptureDevice) throws {
        session.beginConfiguration()
        defer { session.commitConfiguration() }

        let input = try AVCaptureDeviceInput(device: device)
        guard session.canAddInput(input) else {
            throw CameraError.cannotAddInput
        }
        session.addInput(input)

        guard session.canAddOutput(videoOutput) else {
            throw CameraError.cannotAddOutput
        }
        videoOutput.alwaysDiscardsLateVideoFrames = true
        videoOutput.setSampleBufferDelegate(self, queue: analysisQueue)
        session.addOutput(videoOutput)
    }

    func start() {
        analysisQueue.async { [session] in
            guard !session.isRunning else { return }
            session.startRunning()
        }
    }

    func stop() {
        sessionRevision += 1
        analysisQueue.async { [session] in
            guard session.isRunning else { return }
            session.stopRunning()
        }
    }

    func captureOutput(
        _ output: AVCaptureOutput,
        didOutput sampleBuffer: CMSampleBuffer,
        from connection: AVCaptureConnection
    ) {
        frameID += 1
        guard !analysisBusy else { return }
        analysisBusy = true
        defer { analysisBusy = false }

        let revision = sessionRevision
        analyze(sampleBuffer, frameID: frameID, revision: revision)
    }
}
~~~

The exact isolation arrangement must be adapted to the target’s Swift concurrency checks. The important invariants are one owner for session work, one bounded delegate queue, and no direct view mutation from the callback.

## Recipe 4: make a Vision request for a pixel buffer

~~~swift
func runVision(
    on sampleBuffer: CMSampleBuffer,
    orientation: CGImagePropertyOrientation,
    frameID: UInt64
) throws -> ObservationSnapshot? {
    guard let pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else {
        throw CameraError.missingPixelBuffer
    }

    var output: VNRecognizedObjectObservation?
    let request = VNRecognizeObjectsRequest { request, error in
        guard error == nil else { return }
        output = (request.results as? [VNRecognizedObjectObservation])?.first
    }

    let handler = VNImageRequestHandler(
        cvPixelBuffer: pixelBuffer,
        orientation: orientation,
        options: [:]
    )
    try handler.perform([request])

    guard let observation = output else { return nil }
    let label = observation.labels.first?.identifier
    let labelConfidence = observation.labels.first?.confidence

    return ObservationSnapshot(
        id: UUID(),
        frameID: frameID,
        sourceTime: CMSampleBufferGetPresentationTimeStamp(sampleBuffer),
        label: label,
        confidence: labelConfidence,
        normalizedRect: observation.boundingBox,
        sourceDescription: "Vision object observation",
        isStale: false
    )
}
~~~

Use the request type supported by the selected SDK and model. A classifier request and a Core ML request can produce different observation families. Keep the observation confidence and classification confidence separate when both exist.

## Recipe 5: wrap a Core ML model for Vision

~~~swift
import CoreML
import Vision

func makeObjectRequest(modelURL: URL) async throws -> VNCoreMLRequest {
    let configuration = MLModelConfiguration()
    configuration.computeUnits = .all

    let model = try await MLModel.load(
        contentsOf: modelURL,
        configuration: configuration
    )
    let visionModel = try VNCoreMLModel(for: model)

    let request = VNCoreMLRequest(model: visionModel)
    request.imageCropAndScaleOption = .centerCrop
    return request
}
~~~

Load once and serialize use of the MLModel instance on one thread or dispatch queue. Inspect modelDescription and the returned observation family before deciding how to map outputs. Use CPU-only or another explicit policy only when the product’s target and background/GPU constraints justify it.

## Recipe 6: use a request revision and source envelope

~~~swift
struct ObservationSource: Sendable {
    let frameID: UInt64
    let time: CMTime
    let requestName: String
    let requestRevision: Int?
    let modelID: String?
    let inputSize: CGSize
    let orientation: CGImagePropertyOrientation
    let regionOfInterest: CGRect?
}

func source(
    request: VNRequest,
    frameID: UInt64,
    time: CMTime,
    inputSize: CGSize,
    orientation: CGImagePropertyOrientation
) -> ObservationSource {
    ObservationSource(
        frameID: frameID,
        time: time,
        requestName: String(describing: type(of: request)),
        requestRevision: request.revision,
        modelID: nil,
        inputSize: inputSize,
        orientation: orientation,
        regionOfInterest: request.regionOfInterest
    )
}
~~~

Check request revision availability and whether the selected request exposes a region-of-interest property in the deployment target. The source record should remain useful even when the SDK offers a newer Vision request abstraction.

## Recipe 7: map a normalized rectangle to a view

~~~swift
func topLeftImageRect(
    normalized rect: CGRect,
    imageSize: CGSize
) -> CGRect {
    let imageRect = VNImageRectForNormalizedRect(
        rect,
        Int(imageSize.width),
        Int(imageSize.height)
    )
    return CGRect(
        x: imageRect.minX,
        y: imageSize.height - imageRect.maxY,
        width: imageRect.width,
        height: imageRect.height
    )
}
~~~

This only converts the classic normalized lower-left rectangle into a top-left image rectangle. A production adapter must also apply orientation, camera mirroring, aspect fit or fill, crop, safe area, and the current container size. Test the adapter with corners, center, portrait, landscape, front camera, and aspect-fill fixtures.

## Recipe 8: publish across the UI boundary

~~~swift
@MainActor
final class LiveObservationStore: ObservableObject {
    @Published private(set) var state: LiveObservationState = .unavailable(
        "Camera is not ready."
    )

    private var currentRevision = 0

    func beginSession() -> Int {
        currentRevision += 1
        state = .ready
        return currentRevision
    }

    func publish(
        _ snapshot: ObservationSnapshot,
        sessionRevision: Int
    ) {
        guard sessionRevision == currentRevision else { return }
        state = .reported(snapshot)
    }

    func markStale(sessionRevision: Int) {
        guard sessionRevision == currentRevision else { return }
        if case let .reported(snapshot) = state {
            state = .stale(snapshot)
        }
    }
}
~~~

Capture and analysis owners should send small Sendable snapshots to the MainActor. When a session ends or source changes, increment the revision so late Vision or model completions are ignored.

## Recipe 9: present reviewable local-AI proposals

~~~swift
struct ObservationProposalInput: Codable, Sendable {
    let label: String
    let confidenceDescription: String
    let sourceFrameID: UInt64
    let sourceTimeDescription: String
    let modelRevision: String?
}

struct ValidatedAction: Sendable {
    let sourceFrameID: UInt64
    let normalizedValue: String
}

func makeProposalInput(
    from observation: ObservationSnapshot
) -> ObservationProposalInput {
    ObservationProposalInput(
        label: observation.label ?? "Unknown",
        confidenceDescription: observation.confidence.map(String.init) ?? "Unknown",
        sourceFrameID: observation.frameID,
        sourceTimeDescription: observation.sourceTime.description,
        modelRevision: observation.sourceDescription
    )
}
~~~

Pass compact, redacted, typed context to a local language-model adapter. The adapter returns a proposal, never a commit. Validate again against current source revision, supported values, authorization, and explicit user intent before any action.

## Recipe 10: build a glass control group with fallback

~~~swift
struct CameraControls: View {
    let isSampling: Bool
    let pause: () -> Void
    let review: () -> Void

    var body: some View {
        HStack(spacing: 12) {
            Button(isSampling ? "Pause analysis" : "Resume analysis") {
                pause()
            }
            .accessibilityHint("Changes whether selected camera frames are analyzed.")

            Button("Review result") {
                review()
            }
        }
        .padding(12)
        .glassEffect()
        .accessibilityElement(children: .contain)
    }
}
~~~

Check the selected SDK’s Liquid Glass availability and provide an equivalent standard-material or opaque treatment for earlier targets and accessibility settings. Glass should group functional actions; it should not be the only signal for model confidence, freshness, or success.

## Recipe 11: fixture and acceptance record

~~~swift
struct LiveObservationFixture {
    let name: String
    let inputOrientation: CGImagePropertyOrientation
    let expectedFrameID: UInt64
    let expectedState: String
    let expectedOverlayRect: CGRect?
}

let fixtures = [
    LiveObservationFixture(
        name: "front-camera-portrait",
        inputOrientation: .right,
        expectedFrameID: 10,
        expectedState: "reported",
        expectedOverlayRect: CGRect(x: 80, y: 120, width: 160, height: 160)
    ),
    LiveObservationFixture(
        name: "stale-after-session-change",
        inputOrientation: .up,
        expectedFrameID: 4,
        expectedState: "discarded",
        expectedOverlayRect: nil
    ),
    LiveObservationFixture(
        name: "low-confidence-label",
        inputOrientation: .up,
        expectedFrameID: 8,
        expectedState: "review",
        expectedOverlayRect: CGRect(x: 20, y: 30, width: 40, height: 50)
    )
]
~~~

Record which fixtures are pure geometry/state tests and which have physical-device evidence. Add permission, interruption, model-load failure, slow-analyzer, reduced-transparency, VoiceOver, Dynamic Type, and thermal cases before release.

## Sources

- [AVFoundation](https://developer.apple.com/documentation/avfoundation)
- [AVCaptureSession](https://developer.apple.com/documentation/avfoundation/avcapturesession)
- [AVCaptureVideoDataOutput](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutput)
- [AVCaptureVideoDataOutputSampleBufferDelegate](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutputsamplebufferdelegate)
- [Requesting authorization to capture and save media](https://developer.apple.com/documentation/avfoundation/requesting-authorization-to-capture-and-save-media)
- [Vision](https://developer.apple.com/documentation/vision)
- [VNImageRequestHandler](https://developer.apple.com/documentation/vision/vnimagerequesthandler)
- [VNRequest](https://developer.apple.com/documentation/vision/vnrequest)
- [VNRecognizedObjectObservation](https://developer.apple.com/documentation/vision/vnrecognizedobjectobservation)
- [VNRecognizedTextObservation](https://developer.apple.com/documentation/vision/vnrecognizedtextobservation)
- [VNRecognizedPointsObservation](https://developer.apple.com/documentation/vision/vnrecognizedpointsobservation)
- [VNCoreMLModel](https://developer.apple.com/documentation/vision/vncoremlmodel)
- [VNCoreMLRequest](https://developer.apple.com/documentation/vision/vncoremlrequest)
- [Recognizing objects in live capture](https://developer.apple.com/documentation/vision/recognizing-objects-in-live-capture)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [MLModel](https://developer.apple.com/documentation/coreml/mlmodel)
- [MLModelConfiguration](https://developer.apple.com/documentation/coreml/mlmodelconfiguration)
- [MLComputeUnits](https://developer.apple.com/documentation/coreml/mlcomputeunits)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
