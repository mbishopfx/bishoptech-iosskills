# SwiftUI Core AI on-device model-runtime review recipes

These are compile-oriented route sketches for the [Core AI runtime review](../42-framework-deep-dives/113-swiftui-core-ai-on-device-model-runtime-review.md). They are not claimed to compile in this documentation-only workspace. Core AI and custom Foundation Models provider APIs are documented for iOS 27 and later, while Foundation Models LanguageModelSession is available on iOS 26. Compile each slice in a named target against the selected SDK.

The boundary for every recipe is:

    model artifact -> runtime output -> app-owned proposal -> validation -> user approval -> deterministic commit

No recipe treats model output as domain truth.

## 1. Keep version lanes app-owned

~~~swift
import Foundation

enum IntelligenceRoute: String, Codable, Sendable {
    case iOS26System
    case iOS26Deterministic
    case coreAIDirect
    case coreAIFoundationModels
    case fallback
}

enum RuntimeReadiness: Equatable, Sendable {
    case unsupported(reason: String)
    case unavailable(reason: String)
    case checking
    case downloading
    case verifying
    case specializing
    case ready
    case running
    case proposal
    case constrained(reason: String)
    case failed(reason: String)
}
~~~

Keep this state independent from SwiftUI so an iOS 26 fallback and an iOS 27 Core AI implementation can share a screen contract.

## 2. Define a model manifest

~~~swift
import Foundation

struct ModelManifest: Codable, Sendable, Equatable {
    let identifier: String
    let revision: String
    let digest: String
    let minimumOS: String
    let sourceArtifact: String
    let compiledArchitectures: [String]
    let companionResources: [String]
    let functions: [FunctionContract]
    let fallback: IntelligenceRoute
}

struct FunctionContract: Codable, Sendable, Equatable {
    let name: String
    let inputs: [ValueContract]
    let outputs: [ValueContract]
}

struct ValueContract: Codable, Sendable, Equatable {
    let name: String
    let type: String
    let shape: [Int]
    let dynamicDimensions: [Int]
}
~~~

The manifest is an app-owned allowlist. Do not let a remote manifest choose arbitrary function names or domain actions.

## 3. Locate a bundled source model

~~~swift
import Foundation

enum ModelResourceError: Error {
    case missingResource(String)
}

func bundledModelURL(
    named name: String,
    bundle: Bundle = .main
) throws -> URL {
    guard let url = bundle.url(forResource: name, withExtension: nil) else {
        throw ModelResourceError.missingResource(name)
    }
    return url
}
~~~

For a Foundation Models Core AI provider, the resource may be a folder containing the model, tokenizer, and companion resources. Verify the complete folder rather than checking only one file.

## 4. Preflight with AIModelAsset

~~~swift
import CoreAI

struct AssetPreflight: Sendable, Equatable {
    let url: URL
    let isValid: Bool
    let functionNames: [String]
    let metadataSummary: String
}

func preflightSourceModel(at url: URL) throws -> AssetPreflight {
    guard AIModelAsset.isValid(at: url) else {
        throw ModelResourceError.missingResource(url.path)
    }

    let asset = try AIModelAsset(contentsOf: url)
    let summary = try asset.summary(includingStatistics: false)
    let functionNames = summary?.functions.map(\.name) ?? []

    return AssetPreflight(
        url: url,
        isValid: true,
        functionNames: functionNames,
        metadataSummary: String(describing: summary)
    )
}
~~~

AIModelAsset is for structural and metadata inspection. It cannot perform inference. Keep this step in tooling, CI, or a preflight actor.

## 5. Load a specialized model from cache first

~~~swift
import CoreAI

actor CoreAIModelLoader {
    private var activeModel: AIModel?

    func load(from url: URL) async throws -> AIModel {
        if let cached = try AIModelCache.default.model(
            for: url,
            options: .default
        ) {
            activeModel = cached
            return cached
        }

        let model = try await AIModel(contentsOf: url, options: .default)
        activeModel = model
        return model
    }

    func clearActiveModel() {
        activeModel = nil
    }
}
~~~

The loader should publish specializing and failed states to the app. A cache hit proves only that a specialized artifact exists for the source/options key.

## 6. Specialize at a preparation point

~~~swift
import CoreAI

actor ModelPreparation {
    func prepare(url: URL) async throws -> AIModel {
        try await AIModel.specialize(
            contentsOf: url,
            options: .default,
            cache: .default,
            cachePolicy: .default
        )
    }
}
~~~

Use this when the app knows a request is coming and can show a preparation state. Specialization still happens on the device; this controls timing, not the total work.

## 7. Select an architecture-specific AOT asset

~~~swift
import CoreAI

func compiledAssetName(
    baseName: String,
    availableNames: Set<String>
) throws -> String {
    let architecture = AIModel.deviceArchitectureName
    let candidate = "\(baseName).\(architecture).aimodelc"

    guard availableNames.contains(candidate) else {
        throw ModelResourceError.missingResource(candidate)
    }
    return candidate
}
~~~

Treat the architecture string and candidate file as inputs to an app-owned manifest check. The current Apple AOT documentation uses a minimum deployment version of 27.0, so this route belongs behind an iOS 27 target or availability boundary.

## 8. Compile an AOT asset on the Mac

~~~bash
xcodebuild -downloadComponent MetalToolchain
xcrun coreai-build compile MyModel.aimodel --platform iOS --min-deployment-version 27.0 --output compiled
~~~

Record the Xcode, Metal Toolchain, model conversion tool, platform, minimum OS, output filenames, and digest. A successful command is build evidence, not device-load evidence.

## 9. Inspect available compute units

~~~swift
import CoreAI

func availableComputeUnits() -> Set<ComputeUnitKind> {
    ComputeUnitKind.availableKinds
}

func chooseSpecializationOptions() -> SpecializationOptions {
    // Start with the system default. Restrict only with measured evidence.
    .default
}
~~~

Do not assume that CPU, GPU, and Neural Engine availability is identical across devices. Record the set in a physical-device performance run.

## 10. Load a named inference function

~~~swift
import CoreAI

func loadMainFunction(from model: AIModel) throws -> InferenceFunction {
    guard let function = try model.loadFunction(named: "main") else {
        throw ModelResourceError.missingResource("main function")
    }
    return function
}
~~~

Loading a function prepares weights and intermediate resources. Keep the function owner stable and release it under an explicit lifecycle policy.

## 11. Inspect a function descriptor

~~~swift
import CoreAI

struct FunctionShapeSnapshot: Sendable, Equatable {
    let name: String
    let inputNames: [String]
    let outputNames: [String]
}

func inspect(_ function: InferenceFunction) -> FunctionShapeSnapshot {
    let descriptor = function.descriptor
    return FunctionShapeSnapshot(
        name: String(describing: descriptor),
        inputNames: descriptor.inputNames,
        outputNames: descriptor.outputNames
    )
}
~~~

The exact descriptor members can evolve. Compile this adapter against the current SDK and keep descriptor access in one module. The important behavior is to compare names, types, shapes, and dynamic bounds before inference.

## 12. Create and fill an NDArray

~~~swift
import CoreAI

func makeInput() throws -> NDArray {
    var input = NDArray(shape: [3, 4], scalarType: .float32)
    var view = input.mutableView(as: Float.self)

    guard let elements = view.contiguousElements else {
        throw ModelResourceError.missingResource("contiguous input view")
    }

    for index in elements.indices {
        elements[index] = Float(index) / 10.0
    }

    return input
}
~~~

The shape and scalar type must match the exported function contract. Do not use a model response to determine how to fill a tensor.

## 13. Run a simple inference and read a named output

~~~swift
import CoreAI

func runPrediction(
    function: InferenceFunction,
    input: NDArray
) async throws -> NDArray {
    var outputs = try await function.run(inputs: ["input": input])

    guard let value = outputs.remove("prediction"),
          let prediction = value.ndArray else {
        throw ModelResourceError.missingResource("prediction output")
    }

    return prediction
}
~~~

Treat the result as a typed inference value. Add app-owned range, finite-value, source, and revision validation before showing an Apply action.

## 14. Handle image descriptors

~~~swift
import CoreAI

struct ImageInputRequirements: Sendable, Equatable {
    let width: Int
    let height: Int
    let pixelFormat: OSType
}

func imageRequirements(
    for function: InferenceFunction,
    inputName: String
) throws -> ImageInputRequirements {
    guard let descriptor = function.descriptor.inputDescriptor(of: inputName),
          case .image(let image) = descriptor else {
        throw ModelResourceError.missingResource("image descriptor")
    }

    return ImageInputRequirements(
        width: image.width,
        height: image.height,
        pixelFormat: image.pixelFormatType
    )
}
~~~

A negative width or height means a dynamic dimension in the current documentation. Set an app-owned minimum and maximum before accepting a camera or photo source.

## 15. Wrap output with provenance

~~~swift
import Foundation

struct InferenceProposal<Value: Sendable>: Sendable {
    let value: Value
    let sourceID: String
    let sourceRevision: String
    let modelID: String
    let modelRevision: String
    let functionName: String
    let createdAt: Date
    let validation: ValidationStatus
}

enum ValidationStatus: Sendable, Equatable {
    case pending
    case accepted(notes: [String])
    case rejected(notes: [String])
}
~~~

This type is a proposal or observation. The domain layer should create a separate command after validation and user approval.

## 16. Bound concurrent inference with an actor

~~~swift
import CoreAI

actor InferenceCoordinator {
    private let function: InferenceFunction
    private var activeRequest: UUID?

    init(function: InferenceFunction) {
        self.function = function
    }

    func run(input: NDArray) async throws -> (UUID, InferenceFunction.Outputs) {
        guard activeRequest == nil else {
            throw ModelResourceError.missingResource("request already active")
        }

        let requestID = UUID()
        activeRequest = requestID
        defer { activeRequest = nil }

        try Task.checkCancellation()
        let output = try await function.run(inputs: ["input": input])
        try Task.checkCancellation()
        return (requestID, output)
    }
}
~~~

Replace the example error with a typed admission error in a real target. A live camera route may prefer a latest-frame policy instead of rejecting every overlapping frame.

## 17. Use output views for a known shape

~~~swift
import CoreAI

func runWithPreallocatedOutput(
    function: InferenceFunction,
    input: NDArray,
    output: inout InferenceFunction.MutableViews
) async throws -> InferenceFunction.Outputs {
    try await function.run(
        inputs: ["input": input],
        outputViews: consuming output
    )
}
~~~

Only preallocate output views when the function descriptor and output shape are known for the call. Capture the current SDK signature in the target’s tests because Core AI APIs are beta and overloads may change.

## 18. Encode work onto a ComputeStream

~~~swift
import CoreAI

func encodeOnStream(
    function: InferenceFunction,
    input: NDArray,
    stream: ComputeStream
) throws {
    let asyncInput = InferenceFunction.AsyncValue(input)
    _ = try function.encode(
        inputs: ["input": asyncInput],
        to: stream
    )
}
~~~

The exact async-value construction depends on the SDK overload and model input representation. Keep stream ownership in the actor or Metal pipeline that owns the command queue, and await currentWorkCompleted before releasing dependent resources.

## 19. Use a cancellation-aware preparation task

~~~swift
import CoreAI

actor PreparationCoordinator {
    private var task: Task<AIModel, Error>?

    func start(url: URL) async throws -> AIModel {
        task?.cancel()
        let next = Task { try await AIModel(contentsOf: url) }
        task = next
        defer { task = nil }
        return try await next.value
    }

    func cancel() {
        task?.cancel()
        task = nil
    }
}
~~~

Publish cancellation as a state with no commit. If cancellation occurs after a proposal exists, keep the proposal only when the product explicitly supports resuming it with the original source and model revision.

## 20. Delete stale cache entries after an update

~~~swift
import CoreAI

func replaceModel(
    oldURL: URL,
    newURL: URL
) async throws -> AIModel {
    try AIModelCache.default.deleteEntries(for: oldURL)
    try FileManager.default.replaceItemAt(oldURL, withItemAt: newURL)
    return try await AIModel.specialize(
        contentsOf: oldURL,
        options: .default,
        cachePolicy: .persistent
    )
}
~~~

Use a temporary download and an actor-owned update lock in production. Do not replace a source file while an active function may still be reading its derived resources.

## 21. Select a safe route under memory or thermal pressure

~~~swift
import Foundation

struct RuntimeBudget: Sendable {
    let maxConcurrentRequests: Int
    let allowsLargeModel: Bool
    let allowsLiveInference: Bool
}

func routeForBudget(_ budget: RuntimeBudget) -> IntelligenceRoute {
    if !budget.allowsLargeModel {
        return .iOS26Deterministic
    }
    if !budget.allowsLiveInference {
        return .iOS26System
    }
    return .coreAIDirect
}
~~~

The budget decision must be backed by measured device and thermal evidence. A placeholder budget is not a performance claim.

## 22. Deliver an optional model with Background Assets

~~~swift
import Foundation

struct DeliveredModel: Sendable {
    let localURL: URL
    let manifest: ModelManifest
}

actor ModelDeliveryBoundary {
    func acceptInstalledAsset(
        at url: URL,
        manifest: ModelManifest
    ) throws -> DeliveredModel {
        // Verify digest, companion resources, target platform, and revision here.
        guard FileManager.default.fileExists(atPath: url.path) else {
            throw ModelResourceError.missingResource(url.path)
        }
        return DeliveredModel(localURL: url, manifest: manifest)
    }
}
~~~

The Background Assets extension or downloader owns transfer and install semantics. This boundary should accept only a fully installed, verified asset and then pass it to the Core AI preflight.

## 23. Guard a Core AI Foundation Models provider

~~~swift
import Foundation
import FoundationModels
import CoreAILanguageModels

enum ProviderAvailability {
    case unsupported
    case ready
}

@available(iOS 27.0, *)
struct CoreAIFoundationModelsAdapter {
    func makeSession(resourcesAt url: URL) async throws -> LanguageModelSession {
        let model = try await CoreAILanguageModel(resourcesAt: url)
        return LanguageModelSession(model: model)
    }
}
~~~

Keep the availability annotation on the implementation module or target. The iOS 26 caller should use an app-owned factory that returns the supported fallback instead of referencing the unavailable type in an unguarded path.

## 24. Build a version-aware provider factory

~~~swift
import Foundation

enum ProviderFactoryResult {
    case iOS26Fallback
    case coreAIUnavailable(reason: String)
    case coreAIReady
}

func providerResult(
    processVersion: OperatingSystemVersion,
    hasVerifiedResource: Bool
) -> ProviderFactoryResult {
    guard processVersion.majorVersion >= 27 else {
        return .iOS26Fallback
    }
    guard hasVerifiedResource else {
        return .coreAIUnavailable(reason: "verified resource missing")
    }
    return .coreAIReady
}
~~~

This is routing state, not a substitute for the actual guarded initialization and model capability checks.

## 25. Inspect Foundation Models capabilities

~~~swift
import FoundationModels

struct CapabilityRequirements: Sendable {
    let needsVision: Bool
    let needsGuidedGeneration: Bool
    let needsToolCalling: Bool
    let needsReasoning: Bool
}

func supports(
    _ model: some LanguageModel,
    requirements: CapabilityRequirements
) -> Bool {
    let capabilities = model.capabilities
    if requirements.needsVision && !capabilities.contains(.vision) { return false }
    if requirements.needsGuidedGeneration && !capabilities.contains(.guidedGeneration) { return false }
    if requirements.needsToolCalling && !capabilities.contains(.toolCalling) { return false }
    if requirements.needsReasoning && !capabilities.contains(.reasoning) { return false }
    return true
}
~~~

The framework can reject an unsupported request, but checking before dispatch produces a better route and UI state.

## 26. Use the shared session surface

~~~swift
import FoundationModels

@available(iOS 27.0, *)
func askCoreAI(
    session: LanguageModelSession,
    prompt: String
) async throws -> String {
    let response = try await session.respond(to: prompt)
    return response.content
}
~~~

The same session API does not make every provider equivalent. Preserve model identity, capability, data path, context, tokenizer, and error information in the app-owned result.

## 27. Sketch a custom LanguageModel value

~~~swift
import FoundationModels

@available(iOS 27.0, *)
struct AppLanguageModel: LanguageModel {
    typealias Executor = AppLanguageModelExecutor

    let configuration: Executor.Configuration

    var capabilities: LanguageModelCapabilities {
        LanguageModelCapabilities([
            .guidedGeneration,
            .toolCalling
        ])
    }

    var executorConfiguration: Executor.Configuration {
        configuration
    }
}
~~~

Declare only capabilities backed by the executor. If the model cannot accept image attachments, do not advertise vision.

## 28. Sketch a custom executor boundary

~~~swift
import FoundationModels

@available(iOS 27.0, *)
struct AppLanguageModelExecutor: LanguageModelExecutor {
    struct Configuration: Hashable, Sendable {
        let modelURL: URL
        let modelRevision: String
    }

    typealias Model = AppLanguageModel

    let configuration: Configuration

    init(configuration: Configuration) throws {
        self.configuration = configuration
    }

    func prewarm(model: AppLanguageModel, transcript: Transcript) {
        // Load tokenizer/cache resources in the real implementation.
    }

    func respond(
        to request: LanguageModelExecutorGenerationRequest,
        model: AppLanguageModel,
        streamingInto channel: LanguageModelExecutorGenerationChannel
    ) async throws {
        // Translate the transcript, schema, tools, and options.
        // Stream metadata, usage, and response events through channel.
    }
}
~~~

The executor owns translation and inference. Keep credentials, raw prompts, and sensitive source values out of diagnostic logs.

## 29. Apply generation and context options deliberately

~~~swift
import FoundationModels

@available(iOS 27.0, *)
func requestSummary(
    _ request: LanguageModelExecutorGenerationRequest
) -> String {
    let sampling = String(describing: request.generationOptions)
    let context = String(describing: request.contextOptions)
    let schema = String(describing: request.schema)
    return "sampling=\(sampling); context=\(context); schema=\(schema)"
}
~~~

A real executor must map the options into native model behavior or explicitly reject unsupported options. Silently ignoring guided schema or tool definitions is not a compatible provider.

## 30. Send provider metadata before text

~~~swift
import FoundationModels

@available(iOS 27.0, *)
func sendProviderMetadata(
    request: LanguageModelExecutorGenerationRequest,
    channel: LanguageModelExecutorGenerationChannel
) async {
    let entryID = UUID().uuidString
    await channel.send(.response(
        entryID: entryID,
        action: .updateMetadata([
            "modelRevision": "app-owned-revision",
            "requestID": request.id.uuidString
        ])
    ))
}
~~~

Use the generation channel to report provider identity, usage, response fragments, tool lifecycle, and other supported events. Keep internal reasoning separate from person-facing content.

## 31. Attach a source with provenance

~~~swift
import Foundation

struct SourceDescriptor: Sendable, Equatable {
    let id: String
    let revision: String
    let label: String
    let orientation: String
}

struct ImagePromptInput: Sendable {
    let source: SourceDescriptor
    let fileURL: URL
}
~~~

The exact Attachment initializer depends on the current Foundation Models SDK. Create the attachment only after checking source permission, orientation, file type, size, and provider vision capability. Store the source descriptor alongside the prompt or proposal.

## 32. Keep tool calls bounded

~~~swift
import Foundation

struct ToolPolicy: Sendable {
    let maxTurns: Int
    let allowsSideEffects: Bool
}

struct ToolLoopState: Sendable, Equatable {
    var turnCount: Int = 0
    var awaitingApproval = false
    var committed = false
}

func admitToolTurn(
    state: ToolLoopState,
    policy: ToolPolicy
) -> Bool {
    state.turnCount < policy.maxTurns && !state.committed
}
~~~

The model may propose a tool call. The app validates arguments, checks authorization, re-resolves current state, asks for approval when necessary, and commits deterministically.

## 33. Convert a model proposal to a domain command

~~~swift
import Foundation

struct ProposedRename: Sendable, Equatable {
    let recordID: String
    let expectedRevision: Int
    let newName: String
}

struct RenameCommand: Sendable, Equatable {
    let recordID: String
    let expectedRevision: Int
    let newName: String
}

func validate(_ proposal: ProposedRename) throws -> RenameCommand {
    guard !proposal.newName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
        throw ModelResourceError.missingResource("non-empty proposed name")
    }
    return RenameCommand(
        recordID: proposal.recordID,
        expectedRevision: proposal.expectedRevision,
        newName: proposal.newName
    )
}
~~~

The domain actor must compare expectedRevision with current state and require user approval before saving.

## 34. Represent runtime status in SwiftUI

~~~swift
import SwiftUI

struct CoreAIStatusView: View {
    let readiness: RuntimeReadiness
    let routeName: String
    let cancel: () -> Void
    let useFallback: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label(routeName, systemImage: "cpu")
                .font(.headline)

            Text(statusText)
                .foregroundStyle(.secondary)

            HStack {
                if isCancellable {
                    Button("Cancel", action: cancel)
                }
                if isFallbackAvailable {
                    Button("Use Manual Mode", action: useFallback)
                }
            }
        }
        .padding()
        .glassEffect()
        .accessibilityElement(children: .combine)
        .accessibilityLabel("On-device model status")
        .accessibilityValue(statusText)
    }

    private var statusText: String {
        String(describing: readiness)
    }

    private var isCancellable: Bool {
        switch readiness {
        case .specializing, .running:
            true
        default:
            false
        }
    }

    private var isFallbackAvailable: Bool {
        switch readiness {
        case .unsupported, .unavailable, .constrained, .failed:
            true
        default:
            false
        }
    }
}
~~~

The exact Liquid Glass modifier and availability should be compiled against the selected SwiftUI SDK. Keep the status content useful if the glass material is unavailable or reduced.

## 35. Create a review card for a proposal

~~~swift
import SwiftUI

struct ProposalReview<Value: CustomStringConvertible>: View {
    let value: Value
    let sourceLabel: String
    let modelLabel: String
    let validationLabel: String
    let apply: () -> Void
    let reject: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Review suggestion")
                .font(.title3.weight(.semibold))

            Text(value.description)
                .textSelection(.enabled)

            LabeledContent("Source", value: sourceLabel)
            LabeledContent("Model", value: modelLabel)
            LabeledContent("Checks", value: validationLabel)

            HStack {
                Button("Not now", action: reject)
                Button("Apply", action: apply)
                    .buttonStyle(.borderedProminent)
            }
        }
        .padding()
        .accessibilityElement(children: .contain)
    }
}
~~~

Do not enable Apply until deterministic validation and current-revision checks pass. If applying changes external or sensitive state, add a confirmation that names the exact change.

## 36. Announce state changes once

~~~swift
import SwiftUI

struct AnnouncedRuntimeState: ViewModifier {
    let message: String

    func body(content: Content) -> some View {
        content
            .accessibilityAddTraits(.updatesFrequently)
            .accessibilityValue(message)
    }
}

extension View {
    func announcedRuntimeState(_ message: String) -> some View {
        modifier(AnnouncedRuntimeState(message: message))
    }
}
~~~

In a real implementation, announce only meaningful transitions such as preparing, ready, cancelled, rejected, or saved. Do not announce every generated token or camera frame.

## 37. Record a performance sample without raw input

~~~swift
import Foundation
import OSLog

let coreAILog = Logger(subsystem: "com.example.app", category: "core-ai")

struct RuntimeSample: Codable, Sendable {
    let modelRevision: String
    let functionName: String
    let device: String
    let loadMilliseconds: Double
    let inferenceMilliseconds: Double
    let outputShape: [Int]
}

func log(_ sample: RuntimeSample) {
    coreAILog.notice(
        "model=\(sample.modelRevision, privacy: .public) function=\(sample.functionName, privacy: .public) device=\(sample.device, privacy: .public) load_ms=\(sample.loadMilliseconds) inference_ms=\(sample.inferenceMilliseconds)"
    )
}
~~~

Keep raw photos, audio, documents, prompts, tokens, and secrets out of logs. Use Instruments and the Core AI debug gauge for deeper traces with an explicit privacy review.

## 38. Build a deterministic fixture

~~~swift
import Foundation

struct InferenceFixture: Codable, Sendable {
    let name: String
    let modelRevision: String
    let inputDigest: String
    let expectedOutputShape: [Int]
    let expectedLabel: String?
}

func validateFixture(
    _ fixture: InferenceFixture,
    actualShape: [Int]
) throws {
    guard fixture.expectedOutputShape == actualShape else {
        throw ModelResourceError.missingResource("fixture output shape mismatch")
    }
}
~~~

Use a separate reference-run fixture for numerical comparison and a domain fixture for semantic validation. Never record a generated label as expected truth without an independent source.

## 39. Model update acceptance

~~~swift
import Foundation

enum UpdateDecision: Sendable, Equatable {
    case reject(String)
    case stage
    case activate
}

func decideUpdate(
    current: ModelManifest,
    candidate: ModelManifest,
    preflightPassed: Bool,
    referencePassed: Bool
) -> UpdateDecision {
    guard candidate.identifier == current.identifier else {
        return .reject("different model identity")
    }
    guard preflightPassed && referencePassed else {
        return .reject("preflight or reference validation failed")
    }
    return .activate
}
~~~

In production, stage the candidate in a temporary location, keep the current accepted revision, and activate only after device smoke tests and contract checks.

## 40. Release evidence record

~~~swift
import Foundation

struct CoreAIReleaseEvidence: Codable, Sendable {
    let bundleID: String
    let build: String
    let sdk: String
    let deploymentTarget: String
    let modelRevision: String
    let artifactDigest: String
    let device: String
    let os: String
    let architecture: String
    let fallbackTested: Bool
    let accessibilityTasksPassed: Bool
    let archiveInspected: Bool
    let testFlightRouteTested: Bool
}
~~~

A release record should point to actual archive, device, TestFlight, accessibility, and performance evidence. It must not be synthesized from a successful compile.

## 41. Implementation checklist

Before copying any recipe into an app:

- set the deployment target and identify whether the file is iOS 26 or iOS 27;
- install and record the required Metal Toolchain;
- choose source or AOT asset strategy;
- create and validate a model manifest;
- inspect AIModelAsset and function descriptors;
- implement an actor-owned loader and update lock;
- publish specialization, cache, memory, thermal, and cancellation states;
- validate tensor/image inputs and named outputs;
- preserve source/model/function/revision provenance;
- declare LanguageModel capabilities honestly if using Foundation Models;
- bound tool calls and side effects;
- add iOS 26 or deterministic fallback;
- test Core AI Debugger reference correctness;
- profile with the debug gauge and Instruments;
- run VoiceOver, Dynamic Type, contrast, transparency, motion, keyboard, and pointer tasks;
- install the signed build on supported physical hardware;
- inspect the archive and TestFlight artifact;
- record known gaps instead of claiming completion.

## Sources

- [Core AI](https://developer.apple.com/documentation/coreai)
- [Integrating on-device AI models in your app with Core AI](https://developer.apple.com/documentation/coreai/integrating-on-device-ai-models-in-your-app-with-core-ai)
- [AIModelAsset](https://developer.apple.com/documentation/coreai/aimodelasset)
- [AIModel](https://developer.apple.com/documentation/coreai/aimodel)
- [InferenceFunction](https://developer.apple.com/documentation/coreai/inferencefunction)
- [InferenceFunctionDescriptor](https://developer.apple.com/documentation/coreai/inferencefunctiondescriptor)
- [InferenceValue](https://developer.apple.com/documentation/coreai/inferencevalue)
- [NDArray](https://developer.apple.com/documentation/coreai/ndarray)
- [ComputeStream](https://developer.apple.com/documentation/coreai/computestream)
- [AIModelCache](https://developer.apple.com/documentation/coreai/aimodelcache)
- [SpecializationOptions](https://developer.apple.com/documentation/coreai/specializationoptions)
- [ComputeUnitKind](https://developer.apple.com/documentation/coreai/computeunitkind)
- [Managing model specialization and caching](https://developer.apple.com/documentation/coreai/managing-model-specialization-and-caching)
- [Compiling Core AI models ahead of time](https://developer.apple.com/documentation/coreai/compiling-core-ai-models-ahead-of-time)
- [Inspecting, debugging, and profiling Core AI models](https://developer.apple.com/documentation/coreai/inspecting-debugging-and-profiling-core-ai-models)
- [Validating inference correctness against a reference run](https://developer.apple.com/documentation/coreai/validating-inference-correctness-against-a-reference-run)
- [Running a Core AI model in a Foundation Models session](https://developer.apple.com/documentation/foundationmodels/running-a-core-ai-model-in-a-foundation-models-session)
- [LanguageModel](https://developer.apple.com/documentation/foundationmodels/languagemodel)
- [LanguageModelCapabilities](https://developer.apple.com/documentation/foundationmodels/languagemodelcapabilities)
- [LanguageModelExecutor](https://developer.apple.com/documentation/foundationmodels/languagemodelexecutor)
- [LanguageModelExecutorGenerationRequest](https://developer.apple.com/documentation/foundationmodels/languagemodelexecutorgenerationrequest)
- [LanguageModelExecutorGenerationChannel](https://developer.apple.com/documentation/foundationmodels/languagemodelexecutorgenerationchannel)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Background Assets](https://developer.apple.com/documentation/backgroundassets)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Generative AI](https://developer.apple.com/design/human-interface-guidelines/generative-ai)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
