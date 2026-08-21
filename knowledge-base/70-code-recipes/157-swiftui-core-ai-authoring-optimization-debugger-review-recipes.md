# SwiftUI Core AI authoring, optimization, and debugger review recipes

These are compile-oriented route sketches for the [Core AI authoring and optimization review](../42-framework-deep-dives/114-swiftui-core-ai-authoring-optimization-debugger-review.md) and its [proof matrix](../60-verification/139-swiftui-core-ai-authoring-optimization-debugger-proof-matrix.md). They are documentation recipes, not a claim that this workspace has the Core AI Python packages, Xcode 27, Metal Toolchain, or an Apple device attached.

Core AI authoring and custom Foundation Models provider APIs are documented for the iOS 27/macOS 27/Xcode 27 toolchain. Foundation Models system-model routes remain the iOS 26 fallback lane. Compile every Swift and Python slice against the exact selected SDK and package versions; keep generated commands and artifact digests with the model manifest.

The invariant for every recipe is:

    source model -> exported graph -> converted artifact -> optimized candidate -> device runtime -> app proposal -> validation -> approval -> deterministic commit

No model result, debugger score, or generated response is a domain commit.

## 1. Write an authoring requirement manifest

~~~json
{
  "identifier": "receipt-reader",
  "source_revision": "checkpoint-2026-08-20",
  "functions": ["encode_image", "extract_fields"],
  "inputs": {"image": {"shape": [1, 3, 1024, 1024], "layout": "channels_first"}},
  "outputs": {"fields": {"format": "structured_candidate"}},
  "dynamic_bounds": {"sequence": {"min": 1, "max": 256}},
  "target_profiles": ["iphone-class-a", "iphone-class-b"],
  "minimum_os": "27.0",
  "fallback": "ios26-deterministic-review",
  "license_review": "required",
  "reference_fixture_digest": "sha256:record-after-export"
}
~~~

Keep this manifest app-owned. It should describe an allowlisted artifact and contract, not execute arbitrary remote model instructions.

## 2. Record the reproducible authoring environment

~~~text
python: 3.x.x
pytorch: x.y.z
coreai_torch: x.y.z
coreai_opt: x.y.z
xcode: 27.x
metal_toolchain: recorded-by-xcodebuild
macos: 27.x
source_revision: checkpoint-2026-08-20
export_config_digest: sha256:...
optimizer_config_digest: sha256:...
~~~

Save the environment with the conversion log. A model file without its exporter and optimizer versions is not a reproducible release input.

## 3. Make the source module explicit

~~~python
import torch

class ReceiptModel(torch.nn.Module):
    def __init__(self, encoder, decoder):
        super().__init__()
        self.encoder = encoder
        self.decoder = decoder

    def forward(self, image, token_ids):
        features = self.encoder(image)
        return self.decoder(features, token_ids)

model = ReceiptModel(encoder, decoder).eval()
example_image = torch.zeros((1, 3, 1024, 1024), dtype=torch.float32)
example_tokens = torch.zeros((1, 16), dtype=torch.int64)
~~~

The real source should have deterministic preprocessing, named outputs, and an evaluation fixture before export. Do not hide preprocessing in an undocumented caller.

## 4. Export with named inputs and bounded dynamic shapes

~~~python
from torch.export import Dim, export

sequence = Dim("sequence", min=1, max=256)
exported = export(
    model,
    (example_image, example_tokens),
    dynamic_shapes={
        "image": {0: 1, 2: 1024, 3: 1024},
        "token_ids": {0: 1, 1: sequence},
    },
)
exported_program = exported
~~~

This is an illustrative PyTorch export shape. Verify the selected Core AI converter’s accepted export form and named-input/output options in the current toolchain. Record the minimum, typical, maximum, and rejected shapes.

## 5. Convert the exported program to an aimodel

~~~python
from coreai_torch import TorchConverter

converter = TorchConverter(
    exported_program,
    inputs=["image", "token_ids"],
    outputs=["fields"],
)
converter.save("ReceiptModel.aimodel")
~~~

Treat the exact Python package API as SDK/toolchain-sensitive. The acceptance check is that the resulting artifact has the intended functions, contracts, metadata, and digest—not that a command merely returned zero.

## 6. Name multiple model functions deliberately

~~~python
converter.add_function("encode_image", encode_image_program)
converter.add_function("extract_fields", extract_fields_program)
converter.add_function("validate_crop", validate_crop_program)
converter.save("ReceiptModel.aimodel")
~~~

Use a function manifest with an owner, purpose, inputs, outputs, latency budget, and fallback. Never select a function by index or by an untrusted string from a server response.

## 7. Save a reference output and intermediates

~~~python
reference = run_reference(model, fixture)
reference.save("reference-output.json")

# The exact Core AI debugging helper and file format are toolchain-sensitive.
# Keep an intermediate capture for named sync points.
save_intermediates(
    exported_program,
    fixture,
    path="reference-intermediates.aimodelintermediates",
    sync_points=["encoder.layer.8", "decoder.logits"],
)
~~~

The reference run must use the same decoded input, preprocessing, seed policy, and output mapping as the converted candidate. Store the fixture digest with every comparison.

## 8. Run a structural artifact preflight in Swift

~~~swift
import CoreAI

struct ArtifactSummary: Sendable {
    let url: URL
    let functions: [String]
    let summary: String
}

func inspectArtifact(at url: URL) throws -> ArtifactSummary {
    guard AIModelAsset.isValid(at: url) else {
        throw CocoaError(.fileReadCorruptFile)
    }
    let asset = try AIModelAsset(contentsOf: url)
    let summary = try asset.summary(includingStatistics: false)
    return ArtifactSummary(
        url: url,
        functions: summary?.functions.map(\.name) ?? [],
        summary: String(describing: summary)
    )
}
~~~

This proves structural readability and metadata access. It does not prove specialization, inference, quality, or device support.

## 9. Keep the baseline before compression

~~~python
baseline = convert(exported_program, config="baseline")
baseline_digest = sha256(baseline)
baseline_metrics = evaluate(
    baseline,
    fixtures=["short", "typical", "long", "edge"],
)
write_json("baseline-record.json", {
    "digest": baseline_digest,
    "metrics": baseline_metrics,
    "source_revision": source_revision,
})
~~~

Every compressed or palettized candidate points back to one immutable baseline. Do not overwrite the only copy of a candidate while iterating.

## 10. Use a config-driven optimization candidate

~~~yaml
name: receipt-int4-candidate
baseline: sha256:...
target_profile: iphone-class-a
weight_compression:
  mode: int4
  calibration: representative-receipts-v3
precision:
  preserve: [first_projection, output_projection]
layout:
  require_static_shapes: true
  channels_first: true
validation:
  max_relative_drift: 0.02
  required_fixtures: [short, typical, long, edge]
~~~

The current Core AI authoring material describes configuration-driven optimization, target-aware compression, calibration, quantization-aware training, and palettization. Exact keys belong to the installed `coreai-opt` release; validate the config schema before running it.

## 11. Run calibration without leaking user data

~~~python
calibration = load_reviewed_fixture_set(
    name="representative-receipts-v3",
    classification="approved-sanitized",
)
candidate = optimize(
    baseline="ReceiptModel.aimodel",
    method="quantization",
    calibration=calibration,
    output="ReceiptModel.int8.aimodel",
)
~~~

Record fixture provenance, redaction, retention, and deletion. Production user content should not silently become a model-authoring artifact.

## 12. Compare quantization and palettization separately

~~~python
int8 = optimize(baseline, method="int8", output="ReceiptModel.int8.aimodel")
int4 = optimize(baseline, method="int4", output="ReceiptModel.int4.aimodel")
palette4 = optimize(baseline, method="palettization-4bit", output="ReceiptModel.palette4.aimodel")

for name, candidate in [("int8", int8), ("int4", int4), ("palette4", palette4)]:
    compare_reference(
        candidate,
        baseline=baseline,
        fixtures=["short", "typical", "long", "edge"],
        report=f"reports/{name}.json",
    )
~~~

Do not choose the smallest file until numerical drift, task quality, memory, latency, thermal behavior, and fallback policy have been reviewed together.

## 13. Preserve fragile or high-value layers

~~~yaml
candidate: receipt-int4-candidate
compression:
  default: int4
  exclusions:
    - name: encoder.input_projection
      reason: preserves small-text recall
    - name: decoder.output_projection
      reason: preserves structured-field stability
    - name: safety_gate
      reason: must remain in reviewed precision
~~~

Layer exclusions are hypotheses until the reference and task fixtures show their value. Keep the exclusion rationale in the release review.

## 14. Test a stateful cache or KV-cache contract

~~~python
state = initialize_state(batch=1, max_sequence=256)
first = run(function="prefill", inputs=prompt_tokens, state=state)
continued = run(function="decode", inputs=next_token, state=first.state)
reset = run(function="prefill", inputs=other_prompt, state=initialize_state(batch=1, max_sequence=256))

assert reset.state != first.state
assert compare_task_output(continued.output, reference_continued)
~~~

Prove reset, continuation, cancellation, memory bounds, and actor ownership. Cached state must never cross the request, user, account, or privacy boundary accidentally.

## 15. Build a multi-function artifact contract

~~~swift
struct FunctionUse: Codable, Sendable {
    let name: String
    let purpose: String
    let inputContractDigest: String
    let outputContractDigest: String
    let fallback: String
}

let allowedFunctions: [FunctionUse] = [
    .init(name: "encode_image", purpose: "image features", inputContractDigest: "sha256:...", outputContractDigest: "sha256:...", fallback: "deterministic-crop"),
    .init(name: "extract_fields", purpose: "candidate fields", inputContractDigest: "sha256:...", outputContractDigest: "sha256:...", fallback: "manual-review"),
]
~~~

The runtime can load only a function listed in the signed/local manifest and can map its output only through an app-owned adapter.

## 16. Create a typed candidate envelope

~~~swift
struct ModelCandidate<Value: Codable & Sendable>: Codable, Sendable {
    let value: Value
    let modelID: String
    let modelRevision: String
    let function: String
    let sourceDigest: String
    let fixtureOrRequestID: String
    let generatedAt: Date
    let warnings: [String]
}
~~~

The envelope makes provenance available to the review UI and logs. It is not an authorization token; validation and user approval remain separate.

## 17. Localize a numerical difference with Core AI Debugger

~~~text
1. Open the baseline and candidate artifacts in Core AI Debugger.
2. Load the same reference input and preprocessing record.
3. Run both artifacts on the same Mac or paired device where supported.
4. Add sync points around the first divergent function or custom operation.
5. Capture intermediate tensors and the final output comparison.
6. Record the similarity/difference score, threshold, and tool version.
7. Link the report to the candidate configuration and digest.
~~~

A localized numerical difference is a debugging result. It becomes a release decision only after task-level fixtures and product review.

## 18. Author a custom Metal operation as a paired reference

~~~python
class FusedProjection(torch.nn.Module):
    def forward(self, x, weight, bias):
        return reference_projection(x, weight, bias)

metal_op = TorchMetalKernel(
    name="fused_projection",
    reference=FusedProjection(),
    source="fused_projection.metal",
    inputs=["x", "weight", "bias"],
    outputs=["y"],
    output_shape="same_as_reference",
)
exported_program.register(metal_op)
~~~

The exact registration type is toolchain-sensitive. Keep the reference implementation, Metal source, input/output names, dynamic-shape policy, and target OS together. The Core AI authoring material describes embedding custom Metal kernels into the model artifact.

## 19. Keep the Metal kernel shape policy explicit

~~~metal
// Illustrative MSL only; compile against the selected Metal SDK.
kernel void fused_projection(
    device const float *x [[buffer(0)]],
    device const float *weight [[buffer(1)]],
    device const float *bias [[buffer(2)]],
    device float *y [[buffer(3)]],
    uint index [[thread_position_in_grid]]) {
    // Use the generated contract for bounds, strides, and alignment.
    y[index] = x[index] + bias[index];
}
~~~

This intentionally does not pretend to be a complete optimized kernel. Validate bounds, strides, dtype, alignment, dynamic output shapes, and numerical behavior against the reference before integrating it.

## 20. Describe a Metal tensor at the Swift boundary

~~~swift
import Metal

struct TensorPolicy: Sendable {
    let dimensions: [Int]
    let scalarType: String
    let minimumOS: String
    let supportsAuxiliaryPlanes: Bool
}

func tensorPolicy() -> TensorPolicy {
    TensorPolicy(
        dimensions: [1, 3, 1024, 1024],
        scalarType: "recorded MTLTensorDataType",
        minimumOS: "26.0 or the exact target gate",
        supportsAuxiliaryPlanes: false
    )
}
~~~

Use `MTLTensor` and `MTLTensorDataType` only after compiling against the target SDK and device matrix. Metal tensor datatype availability is version- and device-sensitive; do not infer iOS 27 support from an iOS 26 fallback or simulator.

## 21. Compile ahead-of-time with a recorded target

~~~bash
xcodebuild -downloadComponent MetalToolchain
xcrun coreai-build compile ReceiptModel.aimodel \
  --platform iOS \
  --min-deployment-version 27.0 \
  --output compiled/ReceiptModel
~~~

Treat this as a sketch of the documented route. Preserve the exact command, Xcode/Metal Toolchain versions, output filenames, architecture list, minimum OS, and artifact digests. AOT output still needs a signed physical-device run.

## 22. Select source or AOT assets through a manifest

~~~swift
struct CompiledModelAsset: Sendable {
    let architecture: String
    let url: URL
    let digest: String
}

struct ModelManifest: Sendable {
    let sourceURL: URL
    let sourceDigest: String
    let compiled: [CompiledModelAsset]
}

enum ModelDelivery: Codable, Sendable {
    case source(URL, digest: String)
    case compiled(URL, digest: String, architecture: String)
    case fallback
}

func chooseDelivery(
    manifest: ModelManifest,
    osMajor: Int,
    architecture: String
) -> ModelDelivery {
    guard osMajor >= 27 else { return .fallback }
    guard let asset = manifest.compiled.first(where: { $0.architecture == architecture }) else {
        return .source(manifest.sourceURL, digest: manifest.sourceDigest)
    }
    return .compiled(asset.url, digest: asset.digest, architecture: architecture)
}
~~~

The real manifest types should be app-owned and verified. Never silently select an unverified remote URL or treat an architecture string as proof that an artifact is valid.

## 23. Verify a downloaded artifact before activation

~~~swift
struct CandidateArtifact: Sendable {
    let url: URL
    let expectedDigest: String
    let revision: String
}

enum ArtifactActivationError: Error {
    case digestMismatch
}

func activate(_ candidate: CandidateArtifact, measuredDigest: String) throws {
    guard measuredDigest == candidate.expectedDigest else {
        throw ArtifactActivationError.digestMismatch
    }
    // Move into the app-owned inactive slot, then atomically activate.
}
~~~

The activation layer should retain the prior accepted revision, support rollback, and keep a failed candidate out of the active slot.

## 24. Keep model ownership actor-isolated

~~~swift
import CoreAI

actor ModelSessionOwner {
    private var model: AIModel?
    private var activeFunction: InferenceFunction?
    private var generation = 0

    func replace(with model: AIModel) {
        generation += 1
        activeFunction = nil
        self.model = model
    }

    func cancelAndRelease() {
        generation += 1
        activeFunction = nil
        model = nil
    }
}
~~~

Use a generation/token check around async work so a late result from an old artifact cannot overwrite a newer proposal.

## 25. Record profiling by device and workload

~~~swift
struct InferenceMeasurement: Codable, Sendable {
    let device: String
    let osBuild: String
    let modelDigest: String
    let function: String
    let fixture: String
    let coldLoadMilliseconds: Double
    let warmLoadMilliseconds: Double
    let p50Milliseconds: Double
    let p95Milliseconds: Double
    let peakMemoryBytes: Int
    let thermalNotes: String
}
~~~

Pair this record with the Xcode debug gauge/Core AI Instruments trace. Do not report a single Mac run as an iPhone performance claim.

## 26. Expose authoring state in SwiftUI without overclaiming

~~~swift
import SwiftUI

struct ModelReviewStatusView: View {
    let status: String
    let modelRevision: String
    let detail: String

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label(status, systemImage: "cpu")
                .font(.headline)
            Text("Model revision: \(modelRevision)")
                .font(.subheadline)
            Text(detail)
                .foregroundStyle(.secondary)
        }
        .padding()
        .glassEffect()
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Model status")
        .accessibilityValue("\(status). Revision \(modelRevision). \(detail)")
    }
}
~~~

Use the current SDK’s native Liquid Glass APIs and availability boundaries. Keep the status understandable if transparency, motion, or glass effects are reduced, and do not make a debugger score look like a product guarantee.

## 27. Separate proposal, validation, approval, and commit

~~~swift
enum ProposalState<Value: Sendable>: Sendable {
    case generating
    case needsReview(ModelCandidate<Value>)
    case rejected(reason: String)
    case committed
}

func commitIfApproved<Value: Codable & Sendable>(
    _ candidate: ModelCandidate<Value>,
    validation: ValidationResult,
    approval: UserApproval
) throws {
    guard validation.isAcceptable, approval == .approved else {
        throw CocoaError(.validationMissing)
    }
    // Call the deterministic domain command here.
}
~~~

The UI can display a candidate with provenance, but only the deterministic domain layer may mutate user data.

## 28. Add an iOS 26 fallback route

~~~swift
enum IntelligencePlan: Sendable {
    case coreAI
    case foundationModels
    case deterministic
}

func plan(osMajor: Int, coreAIAvailable: Bool) -> IntelligencePlan {
    if osMajor >= 27, coreAIAvailable { return .coreAI }
    if osMajor >= 26 { return .foundationModels }
    return .deterministic
}
~~~

The fallback must preserve the user journey and review/approval semantics. It is not enough to show an unavailable-model message where the product promised a usable workflow.

## 29. Build a release evidence record

~~~json
{
  "source_digest": "sha256:...",
  "converted_digest": "sha256:...",
  "optimized_digest": "sha256:...",
  "aot_digests": {"arm64": "sha256:..."},
  "reference_fixture": "sha256:...",
  "debugger_report": "reports/candidate-42.json",
  "device_runs": ["iPhone-class-a/iOS-build/..."],
  "accessibility_tasks": "passed-with-notes",
  "archive": "MyApp.xcarchive",
  "testflight_build": "record-processed-build-id",
  "rollback_revision": "accepted-41",
  "decision": "approved-with-device-scope"
}
~~~

Keep this record beside the app release, not only inside an engineer’s local model folder.

## 30. Review checklist before shipping

~~~text
[ ] source, license, and model revision are recorded
[ ] export and converter environment is reproducible
[ ] baseline artifact and reference fixtures are retained
[ ] candidate contracts and function names are reviewed
[ ] compression/quantization/palettization has a baseline comparison
[ ] Core AI Debugger has localized important numerical drift
[ ] custom Metal operations have reference, target, and fallback evidence
[ ] AOT/source selection is proven on each claimed architecture
[ ] load, specialization, latency, memory, thermal, and cancellation are measured
[ ] result provenance survives into the SwiftUI review state
[ ] validation, user approval, and deterministic commit are separate
[ ] Liquid Glass remains usable under accessibility variants
[ ] iOS 26 fallback is complete
[ ] archive and processed TestFlight route have run on device
[ ] prior accepted model can be restored
~~~

## Sources

- [Core AI](https://developer.apple.com/documentation/coreai)
- [Core AI for developers](https://developer.apple.com/core-ai/)
- [Core AI Debugger](https://developer.apple.com/documentation/coreai/inspecting-core-ai-models-with-core-ai-debugger)
- [Inspecting Core AI models with Core AI Debugger](https://developer.apple.com/documentation/coreai/inspecting-core-ai-models-with-core-ai-debugger)
- [Inspecting, debugging, and profiling Core AI models](https://developer.apple.com/documentation/coreai/inspecting-debugging-and-profiling-core-ai-models)
- [Validating inference correctness against a reference run](https://developer.apple.com/documentation/coreai/validating-inference-correctness-against-a-reference-run)
- [Integrating on-device AI models in your app with Core AI](https://developer.apple.com/documentation/coreai/integrating-on-device-ai-models-in-your-app-with-core-ai)
- [Managing model specialization and caching](https://developer.apple.com/documentation/coreai/managing-model-specialization-and-caching)
- [Compiling Core AI models ahead of time](https://developer.apple.com/documentation/coreai/compiling-core-ai-models-ahead-of-time)
- [MTLTensor](https://developer.apple.com/documentation/metal/mtltensor)
- [MTLTensorDataType](https://developer.apple.com/documentation/metal/mtltensordatatype)
- [Machine learning passes](https://developer.apple.com/documentation/metal/machine-learning-passes)
- [Understanding the Metal 4 core API](https://developer.apple.com/documentation/metal/understanding-the-metal-4-core-api)
- [Meet Core AI](https://developer.apple.com/videos/play/wwdc2026/324/)
- [Dive into Core AI model authoring and optimization](https://developer.apple.com/videos/play/wwdc2026/325/)
- [Integrate on-device AI models into your app using Core AI](https://developer.apple.com/videos/play/wwdc2026/326/)
- [Optimize custom machine learning operations with Metal tensors](https://developer.apple.com/videos/play/wwdc2026/330/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
