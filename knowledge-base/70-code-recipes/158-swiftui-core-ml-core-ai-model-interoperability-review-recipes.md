# SwiftUI Core ML and Core AI model-interoperability review recipes

These are compile-oriented sketches for the [model-interoperability review](../42-framework-deep-dives/115-swiftui-core-ml-core-ai-model-interoperability-review.md), the [design route](../21-design-deep-dives/143-swiftui-core-ml-core-ai-model-interoperability-review-design.md), and the [proof matrix](../60-verification/140-swiftui-core-ml-core-ai-model-interoperability-proof-matrix.md). They are not claimed to compile in this documentation workspace. Compile each recipe against the selected Xcode/SDK and check every availability boundary.

The invariant is:

    source -> preprocessing -> model lane -> observation/prediction -> candidate -> validation -> approval -> deterministic commit

## 1. Keep model lanes app-owned

~~~swift
import Foundation

enum ModelLane: String, Codable, Sendable {
    case bundledCoreML
    case downloadedCoreML
    case visionCoreML
    case coreAI
    case deterministicFallback
}

enum ModelReadiness: Sendable, Equatable {
    case unsupported(String)
    case permissionRequired
    case downloading
    case verifying
    case compiling
    case specializing
    case ready
    case running
    case stale
    case failed(String)
}
~~~

Keep this state outside SwiftUI so Core ML, Core AI, and fallback routes can share the same product contract.

## 2. Define a model manifest

~~~swift
import Foundation

struct ModelManifest: Codable, Sendable, Equatable {
    let id: String
    let revision: String
    let digest: String
    let licenseReference: String
    let lane: ModelLane
    let minimumOS: String
    let sourceName: String
    let inputContract: InputContract
    let outputContract: OutputContract
    let preprocessingRevision: String
    let fallback: ModelLane
}

struct InputContract: Codable, Sendable, Equatable {
    let kind: String
    let pixelFormat: String?
    let dimensions: [Int]
    let orientationPolicy: String
    let cropScalePolicy: String
}

struct OutputContract: Codable, Sendable, Equatable {
    let names: [String]
    let semanticMappingRevision: String
}
~~~

Do not let a remote manifest choose arbitrary model functions, file paths, tools, or domain actions.

## 3. Locate a bundled model

~~~swift
import Foundation

enum ModelResourceError: Error {
    case missing(String)
    case invalid(String)
}

func bundledModelURL(
    named name: String,
    extension: String = "mlmodel",
    bundle: Bundle = .main
) throws -> URL {
    guard let url = bundle.url(forResource: name, withExtension: `extension`) else {
        throw ModelResourceError.missing(name)
    }
    return url
}
~~~

For a generated wrapper, the model’s target membership and archive resource should still be inspected. For a downloaded source, this helper is not the activation path.

## 4. Inspect a compiled Core ML asset

~~~swift
import CoreML

struct CoreMLAssetSummary: Sendable {
    let url: URL
    let functions: [String]
    let description: String
}

func inspectCompiledAsset(at url: URL) async throws -> CoreMLAssetSummary {
    let asset = try MLModelAsset(url: url)
    let functions = try await asset.functionNames()
    let description = String(describing: try await asset.modelDescription())
    return CoreMLAssetSummary(url: url, functions: functions, description: description)
}
~~~

The exact async spelling can vary with the SDK language overlay; isolate this adapter and compile it against the selected SDK. Asset inspection proves structure and metadata, not accuracy or release readiness.

## 5. Choose an explicit Core ML compute policy

~~~swift
import CoreML

enum ComputePolicy: String, Codable, Sendable {
    case automatic
    case cpuOnly
    case cpuAndGPU
    case cpuAndNeuralEngine
}

func makeConfiguration(_ policy: ComputePolicy) -> MLModelConfiguration {
    let configuration = MLModelConfiguration()
    switch policy {
    case .automatic:
        configuration.computeUnits = .all
    case .cpuOnly:
        configuration.computeUnits = .cpuOnly
    case .cpuAndGPU:
        configuration.computeUnits = .cpuAndGPU
    case .cpuAndNeuralEngine:
        configuration.computeUnits = .cpuAndNeuralEngine
    }
    return configuration
}
~~~

Start with `.all` unless a measured product requirement justifies a restriction. Record the policy and the device/workload evidence that supports it.

## 6. Compile a downloaded Core ML source

~~~swift
import CoreML

struct CompiledModel: Sendable {
    let sourceURL: URL
    let compiledURL: URL
}

func compileDownloadedModel(at sourceURL: URL) async throws -> CompiledModel {
    // The current async Core ML spelling is compileModel(at:).
    let compiledURL = try await MLModel.compileModel(at: sourceURL)
    return CompiledModel(sourceURL: sourceURL, compiledURL: compiledURL)
}
~~~

Run this off the main actor. The source must already have passed version, digest, license, storage, and target checks. The compiled URL is a candidate until `MLModelAsset` and model-description preflight succeeds.

## 7. Verify a candidate before activation

~~~swift
import Foundation

enum ModelActivationError: Error {
    case digestMismatch
    case unsupportedRevision
}

struct ModelCandidate: Sendable {
    let url: URL
    let expectedDigest: String
    let revision: String
}

func verifyCandidate(
    _ candidate: ModelCandidate,
    measuredDigest: String,
    acceptedRevisions: Set<String>
) throws {
    guard measuredDigest == candidate.expectedDigest else {
        throw ModelActivationError.digestMismatch
    }
    guard acceptedRevisions.contains(candidate.revision) else {
        throw ModelActivationError.unsupportedRevision
    }
}
~~~

After verification and preflight, move the compiled artifact into an app-owned inactive slot and atomically promote it. Retain the prior accepted revision for rollback.

## 8. Load dynamic Core ML through `MLModel`

~~~swift
import CoreML

actor CoreMLModelOwner {
    private var model: MLModel?

    func load(compiledURL: URL, policy: ComputePolicy) async throws -> MLModel {
        let configuration = makeConfiguration(policy)
        let loaded = try await MLModel.load(
            contentsOf: compiledURL,
            configuration: configuration
        )
        model = loaded
        return loaded
    }

    func release() {
        model = nil
    }
}
~~~

Apple’s dynamic download route requires direct `MLModel` use for predictions. Keep model instance ownership serialized or create isolated instances according to the documented concurrency policy.

## 9. Snapshot the model contract

~~~swift
import CoreML

struct FeatureContract: Sendable, Equatable {
    let name: String
    let type: String
    let constraint: String
}

func snapshot(_ model: MLModel) -> [FeatureContract] {
    let description = model.modelDescription
    let inputs = description.inputDescriptionsByName.map { name, value in
        FeatureContract(
            name: name,
            type: String(describing: value.type),
            constraint: String(describing: value)
        )
    }
    return inputs.sorted { $0.name < $1.name }
}
~~~

Compare the snapshot with the app manifest before creating a feature provider or Vision request. Never map inputs by dictionary order.

## 10. Build a typed feature provider boundary

~~~swift
import CoreML

struct FeatureInput: Sendable {
    let name: String
    let value: MLFeatureValue
}

final class InputProvider: NSObject, MLFeatureProvider {
    private let values: [String: MLFeatureValue]

    init(values: [String: MLFeatureValue]) {
        self.values = values
    }

    var featureNames: Set<String> { Set(values.keys) }

    func featureValue(for featureName: String) -> MLFeatureValue? {
        values[featureName]
    }
}
~~~

Validate image, array, dictionary, string, numeric, and missing-value constraints before building this provider. Keep preprocessing out of the domain commit layer.

## 11. Use a compute plan as planning evidence

~~~swift
import CoreML

struct OperationEstimate: Sendable {
    let name: String
    let deviceUsage: String
    let estimatedCost: String
}

func inspectComputePlan(at modelURL: URL) async throws -> [OperationEstimate] {
    let configuration = MLModelConfiguration()
    let plan = try await MLComputePlan.load(
        contentsOf: modelURL,
        configuration: configuration
    )

    guard case let .program(program) = plan.modelStructure,
          let main = program.functions["main"] else {
        return []
    }

    return main.block.operations.map { operation in
        OperationEstimate(
            name: String(describing: operation),
            deviceUsage: String(describing: plan.deviceUsage(for: operation)),
            estimatedCost: String(describing: plan.estimatedCost(of: operation))
        )
    }
}
~~~

The property and enum spellings are SDK-sensitive. A compute plan estimates anticipated device use/cost; pair it with real device measurement before making performance copy.

## 12. Wrap Core ML in Vision

~~~swift
import CoreML
import Vision

struct VisionModelAdapter {
    let model: VNCoreMLModel
    let cropScale: VNImageCropAndScaleOption

    init(coreMLModel: MLModel) throws {
        self.model = try VNCoreMLModel(for: coreMLModel)
        self.cropScale = .centerCrop
    }
}
~~~

Share one stable `VNCoreMLModel` where appropriate, but keep request state and source/frame identity separate for each operation.

## 13. Run a single image request

~~~swift
import CoreGraphics
import Vision

func classify(
    cgImage: CGImage,
    orientation: CGImagePropertyOrientation,
    adapter: VisionModelAdapter
) throws -> [VNObservation] {
    let request = VNCoreMLRequest(model: adapter.model)
    request.imageCropAndScaleOption = adapter.cropScale
    let handler = VNImageRequestHandler(
        cgImage: cgImage,
        orientation: orientation,
        options: [:]
    )
    try handler.perform([request])
    return request.results ?? []
}
~~~

Map observations into an app-owned candidate with source ID, request ID, model revision, and preprocessing revision. Vision’s confidence value is forwarded from Core ML; the app owns calibration and threshold policy.

## 14. Run a pixel-buffer sequence route

~~~swift
import CoreVideo
import Vision

final class FrameSequenceRunner {
    private let handler = VNSequenceRequestHandler()
    private var lastAcceptedFrame: Int64 = -1

    func perform(
        requests: [VNRequest],
        pixelBuffer: CVPixelBuffer,
        orientation: CGImagePropertyOrientation,
        frameID: Int64
    ) throws {
        guard frameID > lastAcceptedFrame else { return }
        try handler.perform(
            requests,
            on: pixelBuffer,
            orientation: orientation
        )
        lastAcceptedFrame = frameID
    }
}
~~~

For live capture, add admission/backpressure and cancellation around this runner. Do not create unbounded work for every camera frame.

## 15. Preserve input provenance

~~~swift
import Foundation

struct InputProvenance: Codable, Sendable, Equatable {
    let sourceID: String
    let frameID: Int64?
    let capturedAt: Date?
    let orientation: String
    let dimensions: [Int]
    let pixelFormat: String?
    let preprocessingRevision: String
}
~~~

Persist only what the privacy policy permits. The provenance record should be enough to reject a result that belongs to a stale source without retaining the original image unnecessarily.

## 16. Wrap a prediction as a proposal

~~~swift
struct PredictionProposal<Value: Codable & Sendable>: Codable, Sendable {
    let value: Value
    let runtimeLane: ModelLane
    let modelID: String
    let modelRevision: String
    let source: InputProvenance
    let warnings: [String]
    let generatedAt: Date
}
~~~

This is a proposal, not a database write. Preserve raw observations separately from the user-facing mapped value when debugging or review requires it.

## 17. Reject stale completions

~~~swift
actor InferenceGeneration {
    private var generation: UInt64 = 0

    func begin() -> UInt64 {
        generation &+= 1
        return generation
    }

    func isCurrent(_ token: UInt64) -> Bool {
        token == generation
    }

    func cancel() {
        generation &+= 1
    }
}
~~~

Capture a generation token when a model/source/request starts. Before publishing or committing, verify that the token, source ID, model revision, and record revision still match.

## 18. Map classifier confidence without false certainty

~~~swift
import Vision

struct ClassificationCandidate: Codable, Sendable {
    let identifier: String
    let rawConfidence: Double
    let displayQuality: String
}

func map(_ observation: VNClassificationObservation) -> ClassificationCandidate {
    let quality = observation.confidence >= 0.8 ? "high" : "review"
    return ClassificationCandidate(
        identifier: observation.identifier,
        rawConfidence: Double(observation.confidence),
        displayQuality: quality
    )
}
~~~

The display label is an app policy, not a claim that the raw value is calibrated probability. Test thresholds against representative fixtures and show an explanation when a result is uncertain.

## 19. Keep state/session ownership explicit

~~~swift
import CoreML

actor StatefulModelOwner {
    private var model: MLModel?
    private var state: MLState?

    func install(_ model: MLModel) {
        self.model = model
        self.state = nil
    }

    func resetState() throws {
        guard let model else { throw ModelResourceError.missing("model") }
        state = model.makeState()
    }

    func release() {
        state = nil
        model = nil
    }
}
~~~

The precise state APIs depend on the model and SDK. Test reset, continuation, cancellation, replacement, memory pressure, and cross-user isolation. State must not survive a boundary the product treats as private.

## 20. Sketch an on-device update task

~~~swift
import CoreML

func startUpdate(
    compiledModelURL: URL,
    batchProvider: MLBatchProvider,
    configuration: MLModelConfiguration,
    completion: @escaping (Result<URL, Error>) -> Void
) {
    let task = MLUpdateTask(
        forModelAt: compiledModelURL,
        trainingData: batchProvider,
        configuration: configuration
    ) { context in
        // Save to a temporary URL, validate, then atomically promote.
        completion(.success(context.updatedModelURL))
    }
    task.resume()
}
~~~

This is a route sketch: compile against the current `MLUpdateTask` initializer and `MLUpdateContext` members. The update only counts as accepted after the updated compiled model passes the baseline/task fixtures.

## 21. Build a rollback slot

~~~swift
struct ModelSlots: Sendable {
    let active: URL
    let candidate: URL
    let previous: URL?
}

func activate(
    candidate: ModelCandidate,
    slots: ModelSlots,
    acceptedRevision: String
) throws {
    guard candidate.revision != acceptedRevision else { return }
    // Validate candidate, move current active to previous, then promote candidate.
}
~~~

Use atomic file operations and a durable activation record. Rollback must be possible after a bad update, app restart, or failed migration.

## 22. Define the Core AI adapter boundary

~~~swift
enum RuntimeResult<Value: Sendable>: Sendable {
    case candidate(Value, lane: ModelLane, revision: String)
    case fallback(reason: String)
}

protocol ModelInferenceAdapter<Value>: Sendable {
    associatedtype Value: Sendable
    func prepare() async throws
    func infer(input: InputProvenance) async throws -> RuntimeResult<Value>
    func cancel()
}
~~~

Implement Core ML/Vision and Core AI adapters separately. The shared protocol should describe product behavior, not erase incompatible artifact/function/input contracts.

## 23. Gate Core AI by the real target

~~~swift
func selectLane(
    osMajor: Int,
    coreAIArtifactPresent: Bool,
    coreMLArtifactPresent: Bool
) -> ModelLane {
    if osMajor >= 27, coreAIArtifactPresent { return .coreAI }
    if coreMLArtifactPresent { return .bundledCoreML }
    return .deterministicFallback
}
~~~

The exact availability check should use the current SDK’s availability and capability APIs. This simple function demonstrates the product rule: a Core AI lane must not leak into an iOS 26-only path.

## 24. Render model status with native SwiftUI

~~~swift
import SwiftUI

struct ModelStatusView: View {
    let readiness: String
    let lane: String
    let revision: String

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Label(readiness, systemImage: "cpu")
                .font(.headline)
            Text("On-device model · \(lane)")
                .font(.subheadline)
            Text("Revision \(revision)")
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .padding()
        .glassEffect()
        .accessibilityElement(children: .combine)
        .accessibilityLabel("On-device model status")
        .accessibilityValue("\(readiness). Lane \(lane). Revision \(revision).")
    }
}
~~~

Use the current SDK’s Liquid Glass availability boundary. Keep the status legible if glass is reduced and avoid implying that the lane or revision guarantees output quality.

## 25. Separate validation, approval, and commit

~~~swift
enum CandidateState<Value: Sendable>: Sendable {
    case running
    case needsReview(PredictionProposal<Value>)
    case rejected(String)
    case committed
}

struct ValidationResult: Sendable {
    let isAcceptable: Bool
    let reasons: [String]
}

func commit<Value: Codable & Sendable>(
    proposal: PredictionProposal<Value>,
    validation: ValidationResult,
    approved: Bool
) throws {
    guard validation.isAcceptable, approved else {
        throw ModelResourceError.invalid("proposal is not approved")
    }
    // Call the deterministic domain command here.
}
~~~

A prediction can populate a draft. It cannot silently mutate the user’s durable record.

## 26. Test single-image fixtures

~~~swift
struct VisionFixture: Codable, Sendable {
    let name: String
    let imageDigest: String
    let orientation: String
    let expectedLabels: [String]
    let maxLatencyMilliseconds: Double
}

let fixtures = [
    VisionFixture(name: "portrait", imageDigest: "sha256:...", orientation: "right", expectedLabels: ["receipt"], maxLatencyMilliseconds: 250),
    VisionFixture(name: "wide", imageDigest: "sha256:...", orientation: "up", expectedLabels: ["document"], maxLatencyMilliseconds: 250),
]
~~~

Use fixtures for orientation, crop/scale, invalid input, ambiguous class, empty result, and stale-source validation. Store only approved fixture data.

## 27. Record device performance

~~~swift
struct ModelMeasurement: Codable, Sendable {
    let lane: ModelLane
    let modelRevision: String
    let device: String
    let osBuild: String
    let fixture: String
    let compileMilliseconds: Double?
    let loadMilliseconds: Double
    let p50Milliseconds: Double
    let p95Milliseconds: Double
    let peakMemoryBytes: Int
    let thermalNotes: String
}
~~~

Pair the record with the relevant Core ML compute-plan estimate, Instruments/debug-gauge trace, and signed build. Do not label a single measurement “all devices.”

## 28. Build a release checklist

~~~text
[ ] model source, revision, digest, license, and target are recorded
[ ] Core ML versus Core AI lane and iOS 26 fallback are explicit
[ ] input orientation, pixel format, crop/scale, and preprocessing revision are tested
[ ] bundled target membership or downloaded compile/activation is verified
[ ] MLModelAsset/model description/function/feature contract is checked
[ ] compute-unit policy and compute-plan estimate are recorded
[ ] Vision request/sequence, frame IDs, stale-result, and cancellation paths are tested
[ ] state/personalization update data and rollback are reviewed
[ ] numerical and task-level fixtures pass
[ ] memory/latency/thermal/device evidence exists
[ ] SwiftUI review state and accessibility tasks pass
[ ] privacy, encryption, logging, and retention are reviewed
[ ] archive and processed TestFlight route exercise the final artifact
~~~

## Sources

- [Core ML](https://developer.apple.com/documentation/coreml)
- [MLModel](https://developer.apple.com/documentation/coreml/mlmodel)
- [MLModelAsset](https://developer.apple.com/documentation/coreml/mlmodelasset)
- [MLModelConfiguration](https://developer.apple.com/documentation/coreml/mlmodelconfiguration)
- [computeUnits](https://developer.apple.com/documentation/coreml/mlmodelconfiguration/computeunits)
- [MLComputeUnits](https://developer.apple.com/documentation/coreml/mlcomputeunits)
- [MLComputePlan](https://developer.apple.com/documentation/coreml/mlcomputeplan-1w21n)
- [compileModel(at:)](https://developer.apple.com/documentation/coreml/mlmodel/compilemodel%28at%3A%29-3nea?changes=la__5)
- [Model Personalization](https://developer.apple.com/documentation/coreml/model-personalization)
- [Personalizing a Model with On-Device Updates](https://developer.apple.com/documentation/coreml/personalizing-a-model-with-on-device-updates)
- [Classifying Images with Vision and Core ML](https://developer.apple.com/documentation/coreml/classifying-images-with-vision-and-core-ml)
- [VNCoreMLRequest](https://developer.apple.com/documentation/vision/vncoremlrequest)
- [VNImageRequestHandler](https://developer.apple.com/documentation/vision/vnimagerequesthandler)
- [VNSequenceRequestHandler](https://developer.apple.com/documentation/vision/vnsequencerequesthandler)
- [Model Integration Samples](https://developer.apple.com/documentation/coreml/model-integration-samples)
- [Generating a Model Encryption Key](https://developer.apple.com/documentation/coreml/generating-a-model-encryption-key)
- [Encrypting a Model in Your App](https://developer.apple.com/documentation/coreml/encrypting-a-model-in-your-app)
- [Core AI](https://developer.apple.com/documentation/coreai)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
