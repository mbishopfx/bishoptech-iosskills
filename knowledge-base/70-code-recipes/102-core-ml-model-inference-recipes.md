# Core ML model lifecycle and inference recipes

These are compile-oriented route sketches, not verified app code. They show the ownership boundaries that should exist before a model feature is copied into an iOS 26 target. Confirm the exact SDK signature, availability, generated wrapper, model contract, entitlements, and device behavior in Xcode.

Shared route:

`source input -> model asset -> configuration -> contract -> serialized prediction -> typed observation -> review -> domain command`

## Recipe 1: load a bundled model with an explicit configuration

Use the generated wrapper for the normal path. Use the underlying `model` property when the app needs to inspect or configure the runtime model.

```swift
import CoreML

enum ModelLoadPolicy {
    case automatic
    case cpuOnly

    var computeUnits: MLComputeUnits {
        switch self {
        case .automatic: .all
        case .cpuOnly: .cpuOnly
        }
    }
}

func loadBundledModel(
    at url: URL,
    policy: ModelLoadPolicy
) async throws -> MLModel {
    let configuration = MLModelConfiguration()
    configuration.computeUnits = policy.computeUnits
    return try await MLModel.load(
        contentsOf: url,
        configuration: configuration
    )
}
```

The URL must point to a compiled model asset such as a target resource ending in `.mlmodelc`. In a generated-wrapper route, obtain the wrapper’s underlying `model` rather than assuming the wrapper’s initializer has the same configuration hooks. Record the policy with the model version and benchmark.

## Recipe 2: inspect a model’s feature contract

Do not trust a downloaded model merely because it loaded.

```swift
struct FeatureContractError: Error {
    let feature: String
    let message: String
}

func requireFeatures(
    _ model: MLModel,
    inputs: Set<String>,
    outputs: Set<String>
) throws {
    let description = model.modelDescription
    let actualInputs = Set(description.inputDescriptionsByName.keys)
    let actualOutputs = Set(description.outputDescriptionsByName.keys)

    if !inputs.isSubset(of: actualInputs) {
        throw FeatureContractError(
            feature: "inputs",
            message: "Required model inputs are missing"
        )
    }
    if !outputs.isSubset(of: actualOutputs) {
        throw FeatureContractError(
            feature: "outputs",
            message: "Required model outputs are missing"
        )
    }
}
```

Production validation should also compare `MLFeatureDescription.featureType`, image constraints, multi-array shape/shape constraints, metadata/version, optional outputs, state descriptions, and update descriptions. Keep the error redacted and attach the model manifest rather than raw input data.

## Recipe 3: inspect feature types and multi-array shape

Use the model description to build a contract report before constructing an input.

```swift
func describe(_ feature: MLFeatureDescription) -> String {
    var summary = "type=\(feature.type.rawValue)"

    if let image = feature.imageConstraint {
        summary += " image=\(image.pixelsWide)x\(image.pixelsHigh)"
    }
    if let array = feature.multiArrayConstraint {
        summary += " shape=\(array.shape)"
    }
    return summary
}
```

The exact optional properties and availability should be checked against the target SDK. Do not assume every feature type has an image or multi-array constraint. Treat a flexible shape constraint as a contract that still needs app-owned bounds and normalization rules.

## Recipe 4: direct feature provider input

When the generated interface is not sufficient, provide named values directly to Core ML.

```swift
import CoreML

struct NamedInput: MLFeatureProvider {
    let values: [String: MLFeatureValue]

    var featureNames: Set<String> {
        Set(values.keys)
    }

    func featureValue(for featureName: String) -> MLFeatureValue? {
        values[featureName]
    }
}

func makeTextInput(_ text: String) -> MLFeatureProvider {
    NamedInput(values: [
        "text": MLFeatureValue(string: text)
    ])
}
```

The feature name and value type must match the model description. For images, use the model’s image constraints and an explicit orientation/crop policy. For numeric arrays, prefer a validated `MLMultiArray` or `MLShapedArray` route instead of converting arbitrary user data without shape checks.

## Recipe 5: serialize use of one model instance

Apple documents using one `MLModel` instance on one thread or dispatch queue at a time. An actor can own the instance and serialize prediction calls.

```swift
actor SerializedModelRunner {
    private let model: MLModel

    init(model: MLModel) {
        self.model = model
    }

    func predict(_ input: MLFeatureProvider) throws -> MLFeatureProvider {
        try model.prediction(from: input)
    }
}
```

Do not make the actor queue unbounded camera frames. Add a latest-frame or bounded-request policy at the capture boundary and return a typed superseded result when a new input invalidates the previous one.

## Recipe 6: send feature values across a concurrency boundary

`MLSendableFeatureValue` is the Core ML type intended for feature values that cross concurrency domains. Keep conversion at the boundary.

```swift
struct SendableInput: Sendable {
    let values: [String: MLSendableFeatureValue]
}

func makeCoreMLProvider(
    from input: SendableInput
) -> MLFeatureProvider {
    let values = input.values.mapValues(MLFeatureValue.init)
    return MLDictionaryFeatureProvider(dictionary: values)
}
```

This is a route sketch. Confirm the current initializer overloads and sendability diagnostics in the target SDK. Do not move a mutable `MLFeatureValue`, pixel buffer, or model instance across actors merely by wrapping it in an unchecked type.

## Recipe 7: load a downloaded model asset

Keep source download, compilation, persistence, and model loading separate.

```swift
import CoreML

struct InstalledModel {
    let compiledURL: URL
    let model: MLModel
}

func installDownloadedModel(
    sourceURL: URL,
    persistentURL: URL,
    configuration: MLModelConfiguration
) async throws -> InstalledModel {
    let compiledURL = try await MLModel.compileModel(at: sourceURL)

    // The compiled directory is a temporary artifact until moved/copied.
    let fileManager = FileManager.default
    if fileManager.fileExists(atPath: persistentURL.path) {
        _ = try fileManager.replaceItemAt(
            persistentURL,
            withItemAt: compiledURL
        )
    } else {
        try fileManager.copyItem(at: compiledURL, to: persistentURL)
    }

    let model = try await MLModel.load(
        contentsOf: persistentURL,
        configuration: configuration
    )
    return InstalledModel(compiledURL: persistentURL, model: model)
}
```

The file operations need a production temporary-directory and atomic-promotion design. Validate source integrity, model version, feature contract, and an evaluation fixture before making `persistentURL` the active asset. The async compile/load signatures and file-replacement behavior must be checked in the named SDK; this recipe is intentionally not claimed as a drop-in installer.

## Recipe 8: model asset inspection before loading

`MLModelAsset` can abstract an on-disk compiled model or an in-memory model specification.

```swift
func inspectAsset(_ url: URL) async throws -> MLModelDescription {
    let asset = try MLModelAsset(url: url)
    return try await withCheckedThrowingContinuation { continuation in
        asset.modelDescription { description, error in
            if let description {
                continuation.resume(returning: description)
            } else {
                continuation.resume(
                    throwing: error ?? CocoaError(.fileReadCorruptFile)
                )
            }
        }
    }
}
```

The continuation is illustrative; verify the current callback/async overload in the target SDK. Use asset inspection to fail early on an incompatible candidate. It does not execute a prediction or prove performance.

## Recipe 9: batch prediction

Use batch input only when the product owns the ordering, memory, and cancellation policy.

```swift
func predictBatch(
    model: MLModel,
    inputs: [MLFeatureProvider]
) throws -> [MLFeatureProvider] {
    let batch = MLArrayBatchProvider(array: inputs)
    let output = try model.predictions(fromBatch: batch)
    return (0..<output.count).compactMap { output.features(at: $0) }
}
```

This is a route sketch: confirm the current batch-provider accessors and output ordering in the selected SDK. Retain stable source IDs next to each input so a late or reordered result cannot be attached to the wrong record.

## Recipe 10: stateful model session

Use `MLState` only for a model whose description declares state and whose product semantics require state across predictions.

```swift
actor StatefulModelSession {
    private let model: MLModel
    private let state: MLState

    init(model: MLModel) {
        self.model = model
        self.state = model.makeState()
    }

    func predict(_ input: MLFeatureProvider) throws -> MLFeatureProvider {
        try model.prediction(from: input, using: state)
    }
}
```

Create a new session/state for a new logical subject or capture sequence unless the product has an explicit persistence policy. Never share one state across concurrent predictions. Do not read or mutate state buffers while the prediction is in flight.

## Recipe 11: Vision request around a Core ML model

Use Vision when it owns image orientation, crop/scale, request scheduling, and observation conversion.

```swift
import Vision

func makeImageRequest(
    model: VNCoreMLModel,
    completion: @escaping (Result<[VNObservation], Error>) -> Void
) -> VNCoreMLRequest {
    let request = VNCoreMLRequest(model: model) { request, error in
        if let error {
            completion(.failure(error))
        } else {
            completion(.success(request.results ?? []))
        }
    }
    request.imageCropAndScaleOption = .centerCrop
    return request
}
```

The request’s crop/scale, orientation, region of interest, and result type must match the model and product. Use a generation token so a late Vision result cannot overwrite a newer source. Keep Vision observations as observations until the app normalizes and reviews them.

## Recipe 12: normalize classifier output

Normalize into an app-owned type with model and source provenance.

```swift
struct LabelCandidate: Sendable, Equatable {
    let label: String
    let score: Double?
}

struct ReviewedCandidate: Sendable {
    let sourceID: String
    let modelID: String
    let modelVersion: String
    let candidates: [LabelCandidate]
    let requiresReview: Bool
}
```

Read the generated wrapper or `MLFeatureProvider` output using the exact feature names from the model description. Keep raw scores optional and separate from display language. Add a “not enough evidence” path rather than forcing a top label when output is absent or below the product’s tested threshold.

## Recipe 13: reviewable Liquid Glass shell

The view receives app-owned state; it does not know how Core ML loads or predicts.

```swift
struct InferenceReviewShell: View {
    let modelState: ModelState
    let proposal: Proposal?
    let onAccept: () -> Void
    let onReject: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label(modelState.title, systemImage: modelState.symbolName)
                .font(.subheadline.weight(.semibold))

            if let proposal {
                Text(proposal.summary)
                    .font(.headline)
                Text(proposal.provenance)
                    .font(.footnote)
                    .foregroundStyle(.secondary)
                HStack {
                    Button("Reject", action: onReject)
                    Button("Accept", action: onAccept)
                        .buttonStyle(.glassProminent)
                }
            } else {
                Text("No suggestion yet")
                    .foregroundStyle(.secondary)
            }
        }
        .padding()
        .glassEffect()
    }
}
```

The exact Liquid Glass modifiers and availability must be checked against the target SDK. Provide a non-glass fallback when reduced transparency or unsupported deployment targets require it. Keep the source media and review detail accessible outside the glass group.

## Recipe 14: update an updatable model

Use `MLUpdateTask` only with an updatable compiled model and labeled training data.

```swift
func startUpdate(
    modelURL: URL,
    trainingData: MLBatchProvider,
    completion: @escaping (Result<URL, Error>) -> Void
) throws -> MLUpdateTask {
    let task = try MLUpdateTask(
        forModelAt: modelURL,
        trainingData: trainingData
    ) { context in
        // Extract the updated model to a temporary destination,
        // validate it, then promote it atomically in the app layer.
        completion(.failure(CocoaError(.featureUnsupported)))
    }
    task.resume()
    return task
}
```

This callback is deliberately a placeholder for the app-owned save and promotion step. Implement progress/error handling with `MLUpdateProgressHandlers` when the UI needs it. Do not replace the active model from the completion callback without re-running contract and evaluation checks. Provide reset/delete and user consent paths.

## Recipe 15: compute-plan preflight

Use a compute plan for resource planning when the model and SDK support it.

```swift
func preflightPlan(
    modelURL: URL,
    configuration: MLModelConfiguration
) async throws {
    let plan = try await MLComputePlan.load(
        contentsOf: modelURL,
        configuration: configuration
    )
    _ = plan.modelStructure
    // Inspect supported operations, anticipated device usage,
    // and estimated cost in the current SDK.
}
```

Compute-plan output is diagnostic/preflight information. It does not replace end-to-end physical-device measurement, and not every model structure exposes the same inspection surface.

## Recipe 16: deterministic model test fixture

Keep the model adapter testable by injecting a runner protocol.

```swift
protocol InferenceRunning: Sendable {
    associatedtype Input: Sendable
    associatedtype Output: Sendable

    func run(_ input: Input) async throws -> Output
}

struct StubRunner<Input: Sendable, Output: Sendable>: InferenceRunning {
    let output: Output

    func run(_ input: Input) async throws -> Output {
        output
    }
}
```

Use a stub for SwiftUI previews and proposal validation tests. Add a separate integration test that loads the real compiled model, and a physical-device test for accelerator, memory, thermal, camera/audio, and performance claims. A stub must never be reported as model execution evidence.

## Sources

- [Core ML](https://developer.apple.com/documentation/coreml)
- [MLModel](https://developer.apple.com/documentation/coreml/mlmodel)
- [MLModelAsset](https://developer.apple.com/documentation/coreml/mlmodelasset)
- [MLModelConfiguration](https://developer.apple.com/documentation/coreml/mlmodelconfiguration)
- [MLComputeUnits](https://developer.apple.com/documentation/coreml/mlcomputeunits)
- [MLModelDescription](https://developer.apple.com/documentation/coreml/mlmodeldescription)
- [MLFeatureDescription](https://developer.apple.com/documentation/coreml/mlfeaturedescription)
- [MLFeatureType](https://developer.apple.com/documentation/coreml/mlfeaturetype)
- [MLFeatureValue](https://developer.apple.com/documentation/coreml/mlfeaturevalue)
- [MLSendableFeatureValue](https://developer.apple.com/documentation/coreml/mlsendablefeaturevalue)
- [MLFeatureProvider](https://developer.apple.com/documentation/coreml/mlfeatureprovider)
- [MLArrayBatchProvider](https://developer.apple.com/documentation/coreml/mlarraybatchprovider)
- [MLMultiArray](https://developer.apple.com/documentation/coreml/mlmultiarray)
- [MLShapedArray](https://developer.apple.com/documentation/coreml/mlshapedarray)
- [MLPredictionOptions](https://developer.apple.com/documentation/coreml/mlpredictionoptions)
- [MLState](https://developer.apple.com/documentation/coreml/mlstate)
- [MLModel.makeState()](https://developer.apple.com/documentation/coreml/mlmodel/makestate%28%29)
- [MLUpdateTask](https://developer.apple.com/documentation/coreml/mlupdatetask)
- [MLUpdateProgressHandlers](https://developer.apple.com/documentation/coreml/mlupdateprogresshandlers)
- [MLComputePlan](https://developer.apple.com/documentation/coreml/mlcomputeplan-1w21n)
- [Downloading and Compiling a Model on the User’s Device](https://developer.apple.com/documentation/coreml/downloading-and-compiling-a-model-on-the-user-s-device)
- [Integrating a Core ML Model into Your App](https://developer.apple.com/documentation/coreml/integrating-a-core-ml-model-into-your-app)
- [VNCoreMLRequest](https://developer.apple.com/documentation/vision/vncoremlrequest)
- [VNCoreMLModel](https://developer.apple.com/documentation/vision/vncoremlmodel)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Performance Tests](https://developer.apple.com/documentation/xctest/performance-tests)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
