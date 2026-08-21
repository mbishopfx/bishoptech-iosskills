# Model, Capture, and Device-Proof Recipes

These route sketches connect Core ML/Vision, AVFoundation capture, SwiftUI review, and physical-device evidence. They are intentionally incomplete: compile them inside a named iOS target, confirm the selected SDK signatures, and test the actual device/model/configuration before making runtime claims.

## Recipe 1: Load a model with an explicit configuration

For a bundled generated model, prefer the wrapper Xcode creates. Use the raw MLModel route when the app needs a downloaded/compiled asset or explicit runtime configuration.

    import CoreML

    struct ModelLoader {
        func loadModel(from url: URL) async throws -> MLModel {
            let configuration = MLModelConfiguration()
            configuration.computeUnits = .all
            return try await MLModel.load(
                contentsOf: url,
                configuration: configuration
            )
        }
    }

The exact compute-unit options and availability must be checked in the selected SDK. Record model URL/version, configuration, load duration, errors, memory, and thermal state. A successful load only proves that this asset loaded on that device; it does not prove prediction quality or acceptable performance.

## Recipe 2: Route an image through Vision and Core ML

Use a Vision request when the model’s image input and output map naturally to Vision observations. Preserve source orientation and define the crop/scale policy.

    import Vision
    import CoreML

    func makeRequest(
        model: MLModel,
        completion: @escaping (VNRequest, Error?) -> Void
    ) throws -> VNCoreMLRequest {
        let visionModel = try VNCoreMLModel(for: model)
        let request = VNCoreMLRequest(
            model: visionModel,
            completionHandler: completion
        )
        request.imageCropAndScaleOption = .centerCrop
        return request
    }

    func analyze(
        pixelBuffer: CVPixelBuffer,
        orientation: CGImagePropertyOrientation,
        request: VNRequest
    ) throws {
        let handler = VNImageRequestHandler(
            cvPixelBuffer: pixelBuffer,
            orientation: orientation,
            options: [:]
        )
        try handler.perform([request])
    }

The request type and handler initializer vary between the current Swift-only Vision API and the older VN-prefixed API. Choose one generation consistently. Normalize observations deterministically, attach a timestamp/model revision/source reference, and never treat a confidence value as a universal calibrated probability without evaluation.

## Recipe 3: Configure capture away from the main actor

AVCaptureSession configuration and startRunning can block. Put setup and lifecycle on the capture service’s serial queue or actor; publish only safe state and frames to SwiftUI.

    final class CaptureService {
        private let session = AVCaptureSession()
        private let queue = DispatchQueue(label: "capture.session")
        private let videoOutput = AVCaptureVideoDataOutput()

        func configure() {
            queue.async {
                self.session.beginConfiguration()
                defer { self.session.commitConfiguration() }

                self.videoOutput.alwaysDiscardsLateVideoFrames = true
                // Add authorized device inputs and the output here.
                // Check canAddInput/canAddOutput before mutation.
            }
        }

        func start() {
            queue.async {
                self.session.startRunning()
            }
        }

        func stop() {
            queue.async {
                self.session.stopRunning()
            }
        }
    }

The sketch omits authorization, device selection, delegate wiring, interruption notifications, and teardown. Add them explicitly. A latest-frame policy can keep a live UI responsive, but it can also skip frames; record cadence, dropped frames, and freshness in the feature contract.

## Recipe 4: Keep capture and inference backpressure visible

Do not run an expensive model synchronously for every incoming frame without a policy. Choose one:

    capture frames
      -> latest-frame buffer or bounded queue
      -> inference task
      -> observation(timestamp, modelVersion)
      -> UI overlay
      -> user-selected frame
      -> reviewable proposal

For a live preview, discard late frames or sample at a bounded cadence. For an inspection workflow, pause capture while the person reviews a selected frame. For offline video, process sequentially with cancellation and progress. The right policy depends on freshness, completeness, latency, thermal budget, and user outcome.

Test:

- queue growth and memory under slow inference;
- cancellation when the view disappears;
- camera interruption and background/foreground;
- stale observation timestamps;
- model load failure;
- orientation and crop changes;
- thermal pressure and reduced-quality fallback;
- duplicate approval from the same observation.

## Recipe 5: Inject observations for SwiftUI review tests

Keep SwiftUI independent from a camera or real model so previews and UI tests can cover every state.

    struct ObservationFixture: Sendable {
        let sourceID: String
        let modelVersion: String
        let capturedAt: Date
        let fields: [String: String]
        let issues: [String]
    }

    protocol ObservationProvider: Sendable {
        func analyze(sourceID: String) async throws -> ObservationFixture
    }

    struct FixtureObservationProvider: ObservationProvider {
        let fixture: ObservationFixture

        func analyze(sourceID: String) async throws -> ObservationFixture {
            fixture
        }
    }

Use fixtures for no result, ambiguous result, low-quality source, long text, unsupported input, model refusal/unavailable, cancellation, stale source, and conflict. The review view should render the same source/proposal/validation/commit states whether the provider is fake or real.

## Recipe 6: Record physical evidence without secrets

Use a redacted evidence value in test tooling or a release notebook:

    struct DeviceEvidence: Codable, Sendable {
        let appBuild: String
        let sdk: String
        let osBuild: String
        let deviceFamily: String
        let route: String
        let modelVersion: String?
        let locale: String
        let permissionState: String
        let result: String
        let latencyMilliseconds: Double?
        let notes: [String]
    }

Do not store device credentials, signing secrets, access tokens, raw private media, health data, or full prompts in this record. Link to approved logs/metrics by an internal artifact identifier if more detail is needed.

## Recipe 7: Connect the result to a reviewable domain route

    source
      -> observation
      -> deterministic normalization
      -> optional language-model proposal
      -> validation and provenance
      -> SwiftUI edit/reject/approve
      -> domain service with authorization and idempotency
      -> confirmed record
      -> optional AppEntity/Spotlight/widget/share projection

The model and tool layers may propose; the domain service commits. System projections are derived from confirmed state and must re-resolve current authorization when invoked.

## Proof matrix

| Route | Preview/unit can prove | Physical or signed evidence still required |
| --- | --- | --- |
| MLModel load/configuration | Error mapping and fake model state | Real asset load, compute configuration, device memory/thermal, supported model/device matrix. |
| Vision request | Fixture observations and coordinate/threshold logic | Real camera/photo inputs, orientation/lighting/occlusion, model quality and latency. |
| AV capture | State reducer and mocked frame pipeline | Camera/microphone permission, actual session, interruptions, frame timing, thermal, and teardown. |
| SwiftUI review | Layout, labels, Dynamic Type, reduced effects, fake proposals | Physical material/touch/accessibility task completion and real model/device states. |
| System projection | Stable ID/deep-link and fake stale state | Signed App Intent/entity/widget/share route, actual system invocation, permissions, account/server state. |

## Sources

- [Core ML](https://developer.apple.com/documentation/coreml)
- [MLModel](https://developer.apple.com/documentation/coreml/mlmodel)
- [MLModelConfiguration](https://developer.apple.com/documentation/coreml/mlmodelconfiguration)
- [MLModel.load(contentsOf:configuration:)](https://developer.apple.com/documentation/coreml/mlmodel/load%28contentsof%3Aconfiguration%3A%29)
- [Vision](https://developer.apple.com/documentation/vision)
- [VNCoreMLRequest](https://developer.apple.com/documentation/vision/vncoremlrequest)
- [VNImageRequestHandler](https://developer.apple.com/documentation/vision/vnimagerequesthandler)
- [AVFoundation Capture setup](https://developer.apple.com/documentation/avfoundation/capture-setup)
- [Setting up a capture session](https://developer.apple.com/documentation/avfoundation/setting-up-a-capture-session)
- [AVCaptureSession](https://developer.apple.com/documentation/avfoundation/avcapturesession)
- [AVCaptureVideoDataOutput](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutput)
- [alwaysDiscardsLateVideoFrames](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutput/alwaysdiscardslatevideoframes)
- [AVCam: Building a camera app](https://developer.apple.com/documentation/avfoundation/avcam-building-a-camera-app)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [Running your app on simulated or physical devices](https://developer.apple.com/documentation/xcode/running-your-app-on-simulated-or-physical-devices)
