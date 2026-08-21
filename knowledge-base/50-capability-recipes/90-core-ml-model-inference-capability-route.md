# Core ML model-inference capability route

## Use this route when

Choose this route when an app needs a local Core ML model to classify, transform, rank, detect, embed, or propose something on Apple hardware. It covers both an Xcode-bundled model and a model downloaded/compiled at runtime. It is intentionally separate from Foundation Models, Vision, Speech, Natural Language, and Metal: add those only when they own a distinct boundary.

The route is:

`source -> input adapter -> model manifest -> load/compile -> contract validation -> prediction -> normalized observation -> review -> domain command`

## Route decision table

| Need | Start with | Add when needed |
| --- | --- | --- |
| Known bundled model with generated Swift interface | Xcode-generated Core ML wrapper | Direct `MLModel` for custom configuration, description inspection, batch/state, or custom features. |
| Model arrives after install | Download source model, compile with Core ML, persist compiled asset | Background transfer, model-pack UI, integrity/version manifest, fallback model. |
| Camera/image observation pipeline | Vision request around a Core ML model | Direct model adapter when preprocessing/output ownership must stay in the app. |
| Numeric/tabular or text features | `MLFeatureProvider`/generated wrapper | `MLShapedArray`, dictionary/sequence constraints, batch prediction. |
| Stateful sequence or recurrent model | `MLState` and serialized stateful prediction | Session reset, state persistence policy, bounded input cadence. |
| Personalized model | `MLUpdateTask` with labeled training data | Consent, progress, reset/delete, re-evaluation, atomic promotion. |
| Need to estimate resource placement | `MLComputePlan` and model structure inspection | Device matrix, performance fixtures, thermal/energy baseline. |
| Reviewable AI suggestion | Typed proposal with source/model metadata | SwiftUI Liquid Glass review shell and explicit domain command. |

## Capability slices

### 1. Input ownership

Define exactly what is entering the model:

- source ID and user action that selected it;
- pixel buffer, image, audio-derived feature, text, number, sequence, dictionary, or shaped array;
- orientation, crop/scale, normalization, units, locale, and missing-value behavior;
- timestamp, capture generation, and privacy/retention rule;
- whether the input is one-shot, queued, live, or a batch.

Reject or downgrade the route if the input source is stale, permission-revoked, partially available, or outside the model’s constraints. Do not make the model adapter reach into a view or a database to guess missing context.

### 2. Model manifest

Use an app-owned manifest for every candidate and active asset:

```swift
struct ModelManifest: Codable, Sendable, Equatable {
    let modelID: String
    let modelVersion: String
    let schemaVersion: String
    let sourceKind: SourceKind
    let expectedInputNames: [String]
    let expectedOutputNames: [String]
    let installedAt: Date
    let assetDigest: String?

    enum SourceKind: String, Codable, Sendable {
        case bundled
        case downloaded
        case personalized
    }
}
```

The fields are an app contract, not a Core ML requirement. Include only metadata that the product can actually verify. Keep the manifest separate from the model file and from user-generated domain data.

### 3. Model installation and readiness

Use explicit states:

```text
missing -> downloading -> downloaded -> compiling -> compiled
  -> inspecting -> validating -> warming -> ready
  -> unavailable | failed | superseded
```

For a downloaded route, compile the `.mlmodel` source on the device, move the compiled `.mlmodelc` to a persistent app-owned directory, construct `MLModelAsset` or load the compiled URL, validate the model description, and only then promote it. The active model should remain available while a candidate is being prepared.

If a candidate fails, keep the error category distinct: transport/integrity, compile, contract mismatch, load, warm-up, or evaluation failure. The UI can use one human-readable message, but the app state and diagnostics should not collapse them.

### 4. Compute-unit policy

Choose `MLModelConfiguration.computeUnits` through a named policy:

```swift
enum InferenceComputePolicy: String, Codable, Sendable {
    case automatic
    case cpuOnly
    case cpuAndGPU
    case cpuAndNeuralEngine
}
```

Map the app policy to the current SDK’s `MLComputeUnits` values at the model boundary. Record the policy with performance evidence. “Automatic” should be the default candidate until a measured reason supports a restriction. Do not present `.cpuAndNeuralEngine` as a guarantee of Neural Engine use; it is an allowed-unit policy.

### 5. Contract adapter

The adapter should validate the loaded model before accepting any live input:

```text
manifest schema -> modelDescription inputs/outputs
  -> feature type/shape/image constraint check
  -> metadata/version check
  -> supported wrapper or direct-provider choice
  -> ready
```

Return a structured mismatch containing model ID/version, schema version, feature name, expected kind, actual kind, and a safe remediation. Never include raw media or private feature values in the mismatch.

### 6. Prediction adapter

Define a small app-owned output type rather than letting `MLFeatureProvider` leak through the product:

```swift
struct InferenceObservation<Value: Sendable>: Sendable {
    let value: Value
    let modelID: String
    let modelVersion: String
    let inputID: String
    let generatedAt: Date
    let score: Double?
    let reviewRequired: Bool
}
```

The generic shape is illustrative. Production output types should encode the model’s real result and validation rules. A score is optional metadata; it is not a universal confidence contract.

### 7. Review and domain command

Route model output through a review state:

```text
observation
  -> proposal (editable, source-linked, model-versioned)
  -> user accepts/edits/rejects
  -> deterministic domain validation
  -> app command
  -> persisted record or external side effect
```

If the model identifies an object, keep the source asset and model result as evidence. If it proposes a label, let the person edit it. If it triggers a file move, message, purchase, or device action, make the final command separate and auditable.

## SwiftUI composition

Use a view model or observable state object to expose:

- input readiness and permission state;
- model installation/readiness state;
- current source and capture generation;
- observation/proposal with provenance;
- review state and validation errors;
- deterministic fallback.

The view should render state and send user intents. It should not load models, own `MLModel` instances, or parse raw `MLFeatureProvider` output.

A good Liquid Glass shell contains status, source, result, and review actions in that order. On compact screens, put provenance/detail into a sheet or pushed destination. Preserve the same proposal and decision state across navigation and size-class changes.

## Fallback routes

Plan at least one fallback:

- bundled baseline model when the downloaded candidate is unavailable;
- deterministic rules or manual entry when the model is not ready;
- lower-rate or still-image inference when live frames exceed the device budget;
- “not enough evidence” when feature quality or contract validation fails;
- a read-only result when the proposed side effect cannot be authorized.

The fallback must be honest. Do not render a stale previous result as if it came from the current input without labeling its source and timestamp.

## Verification contract

### Unit/fixture

- manifest decoding and model identity checks;
- feature-description validation for type, name, shape, image constraints, and output set;
- normalization from raw feature values to typed observations;
- unknown/missing output handling;
- input generation and cancellation/supersession;
- score thresholds and “not enough evidence” policy;
- proposal edit/accept/reject and domain-command validation;
- privacy redaction and deletion behavior.

### Preview/UI test

- every model readiness state;
- source/no-source, empty, unavailable, failed, and stale-result states;
- review card with long localized text and Dynamic Type;
- reduced transparency/motion and increased contrast;
- VoiceOver order and semantic actions;
- fallback path without model execution.

### Simulator

Use the simulator for deterministic state, input fixtures, and UI navigation. Do not use it as proof of the target accelerator, camera, microphone, memory, thermal, or on-device AI behavior.

### Physical/release

On named devices, record model load/compile time, cold/warm latency, memory, energy, dropped frames, thermal state, accessibility task completion, and failure/recovery. In the signed artifact, verify model resource membership, target/deployment, privacy strings, entitlements/capabilities, and the intended model download/update route.

## Sources

- [Core ML](https://developer.apple.com/documentation/coreml)
- [MLModel](https://developer.apple.com/documentation/coreml/mlmodel)
- [MLModelAsset](https://developer.apple.com/documentation/coreml/mlmodelasset)
- [MLModelConfiguration](https://developer.apple.com/documentation/coreml/mlmodelconfiguration)
- [MLComputeUnits](https://developer.apple.com/documentation/coreml/mlcomputeunits)
- [MLModelDescription](https://developer.apple.com/documentation/coreml/mlmodeldescription)
- [MLFeatureDescription](https://developer.apple.com/documentation/coreml/mlfeaturedescription)
- [MLFeatureProvider](https://developer.apple.com/documentation/coreml/mlfeatureprovider)
- [MLFeatureValue](https://developer.apple.com/documentation/coreml/mlfeaturevalue)
- [MLSendableFeatureValue](https://developer.apple.com/documentation/coreml/mlsendablefeaturevalue)
- [MLShapedArray](https://developer.apple.com/documentation/coreml/mlshapedarray)
- [MLState](https://developer.apple.com/documentation/coreml/mlstate)
- [MLUpdateTask](https://developer.apple.com/documentation/coreml/mlupdatetask)
- [MLComputePlan](https://developer.apple.com/documentation/coreml/mlcomputeplan-1w21n)
- [Downloading and Compiling a Model on the User’s Device](https://developer.apple.com/documentation/coreml/downloading-and-compiling-a-model-on-the-user-s-device)
- [Integrating a Core ML Model into Your App](https://developer.apple.com/documentation/coreml/integrating-a-core-ml-model-into-your-app)
- [VNCoreMLRequest](https://developer.apple.com/documentation/vision/vncoremlrequest)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
