# Core ML model lifecycle, typed inference, and device policy

## Capability boundary

Core ML is the runtime boundary for executing a compiled machine-learning model on Apple devices. It does not decide what a product should save, show, send, or claim. The app owns the input provenance, model identity, feature-contract validation, output normalization, user review, and any domain side effect.

Keep the pipeline explicit:

`model asset -> compile/load -> runtime configuration -> feature contract -> input adapter -> prediction -> typed observation -> review -> domain action`

A successful `MLModel.load` is evidence that Core ML could construct a model instance. It is not evidence that the model matches the app’s expected input schema, that its outputs are accurate, that a particular compute unit was used, or that the result is safe to act on.

## The Core ML object graph

| Concern | Apple API | Practical responsibility |
| --- | --- | --- |
| Model runtime | `MLModel` | Loads a compiled asset, exposes configuration and description, and performs single, batch, stateful, or custom-feature predictions. |
| Model asset | `MLModelAsset` | Represents a compiled model from an on-disk URL or an in-memory specification/blob mapping. |
| Runtime policy | `MLModelConfiguration` | Carries compute-unit choice, preferred Metal device, low-precision and other runtime settings, parameters, and display name. |
| Compute units | `MLComputeUnits` | Limits or permits CPU, GPU, and Neural Engine participation; it is a policy input, not a performance promise. |
| Feature contract | `MLModelDescription`, `MLFeatureDescription`, `MLFeatureType` | Describes input/output names, types, image constraints, multi-array constraints, state, metadata, labels, and update capabilities. |
| Feature values | `MLFeatureValue`, `MLSendableFeatureValue` | Wraps typed values such as images, numbers, strings, dictionaries, sequences, multi-arrays, state, or undefined values. |
| Feature provider | `MLFeatureProvider`, `MLDictionaryFeatureProvider` | Supplies named features to a direct `MLModel` prediction. |
| Batch input | `MLBatchProvider`, `MLArrayBatchProvider` | Supplies multiple feature providers for batch prediction or model-update training data. |
| Tensor/array data | `MLMultiArray`, `MLShapedArray`, `MLTensor` | Represents multidimensional numeric data at different layers of the Core ML API. |
| Prediction options | `MLPredictionOptions` | Carries options for predictions that support them. |
| Model state | `MLState` | Holds buffers for a stateful model across predictions; calls sharing a state must be serialized. |
| Personalization | `MLTask`, `MLUpdateTask`, `MLUpdateContext` | Runs an update against an updatable compiled model with labeled data and progress/completion state. |
| Cost/placement inspection | `MLComputePlan`, `MLModelStructure` | Estimates operation cost and anticipated device usage for supported model structures before prediction. |

In most bundled-model projects, Xcode’s generated wrapper is the ergonomic app-facing layer. Use the direct `MLModel` surface when the app needs a downloaded or compiled model, custom feature providers, runtime configuration, model-description inspection, batch/stateful prediction, or a model that is not known at compile time.

## Asset lifecycle: source, compiled, loaded

Keep three states separate:

1. **Source model** — a `.mlmodel` or model package supplied by a build or download. It is not the runtime object.
2. **Compiled asset** — a `.mlmodelc` representation produced for the device by Core ML. A downloaded source model must be present locally before compilation.
3. **Loaded runtime** — an `MLModel` configured for the current process and ready to accept a valid feature provider.

For a bundled model, Xcode normally handles the build-time compilation and generated interface. For a downloaded model, the documented route is to download the source model, call `MLModel.compileModel(at:)` or its asynchronous interface, move the resulting compiled directory from its temporary location to a persistent app-owned directory, and load the compiled asset. Compilation can be time-consuming, so keep it off the main actor and report it as a distinct readiness state.

Treat an installed model as a versioned artifact:

```text
candidate download
  -> transport/integrity validation
  -> local .mlmodel presence
  -> Core ML compilation
  -> compiled-asset inspection
  -> feature-contract validation
  -> asynchronous MLModel load
  -> warm-up/evaluation fixture
  -> atomic promotion to active model
```

Do not replace the active model as soon as a file arrives. Keep a manifest with the app-supported model identifier, source version, expected feature contract hash or explicit schema version, file size, installation date, and the reason the model is active. Use a temporary directory for download/compile work and promote only after the candidate passes the contract checks. Retain a known-good fallback when a new asset is incompatible or fails to load.

The system’s compiled model directory is a runtime artifact. Do not assume its path is stable across launches or devices; persist the app-owned copy or manifest URL that your route controls. When a model is deleted, invalidate the associated loaded instance and clear any cached output whose model version no longer matches.

## Runtime configuration and compute-unit policy

`MLModelConfiguration.computeUnits` expresses which processing units Core ML may use:

| Policy | Meaning | Appropriate use |
| --- | --- | --- |
| `.all` | Permit all available units, including the Neural Engine when available, and let the OS choose | Default candidate for a measured interactive path. |
| `.cpuOnly` | Restrict the model to CPU execution | Background-like or GPU-contention cases where predictable CPU ownership matters; measure energy and latency. |
| `.cpuAndGPU` | Permit CPU and GPU but not Neural Engine | A deliberate policy for a workload that must avoid the Neural Engine; never assume it is faster. |
| `.cpuAndNeuralEngine` | Permit CPU and Neural Engine but not GPU | A deliberate policy for a workload that must leave GPU time to graphics/media; verify device support and results. |

Choose a policy from the product’s measured constraints, not from the marketing name of a device. Record model version, input shape, batch size, device/OS, warm or cold state, policy, latency, memory, energy, and thermal observations. The policy does not prove that every layer ran on one unit, that the Neural Engine was used, or that a policy is available on every target.

`MLModelConfiguration` also exposes settings such as a preferred Metal device and model parameters. Treat those as part of the model instance’s reproducible runtime configuration. If a setting can affect numerical output, resource use, or update behavior, include it in the evaluation record and active-model manifest.

`MLModel.availableComputeDevices` can describe compute devices available to the model’s prediction methods. `MLComputePlan` can provide a preflight view of anticipated device usage and estimated cost for supported model structures. These are planning and diagnostic signals, not a replacement for representative-device measurement.

## Feature contracts are runtime input validation

The generated wrapper gives compile-time ergonomics only for the model revision that generated it. A dynamic or downloaded model needs an explicit contract check before use.

Inspect `model.modelDescription` and compare the app’s expected contract with:

- required input and output names;
- `MLFeatureType` for each feature;
- image width, height, pixel format, and optional image constraints;
- multi-array shape, shape constraint, data type, and rank;
- dictionary key/value constraints and sequence element types;
- whether a feature can be undefined;
- state descriptions for stateful models;
- predicted feature and probability names when the model exposes them;
- model metadata and model version fields used by the app’s manifest;
- `isUpdatable`, training-input descriptions, and parameter descriptions for personalization routes.

Reject the model before prediction when a required feature is missing, a type is incompatible, an image orientation/format cannot be adapted safely, an array shape is unexpected, an output is missing, or the model version is outside the app’s supported range. Log a redacted contract mismatch that identifies the model/schema version and feature name without recording private input data.

`MLFeatureValue` is a typed wrapper, not a generic bag of JSON. Image values may be created from pixel buffers or images using the feature’s constraints. Numeric and string values remain distinct. `MLShapedArray` is Swift’s shaped-array counterpart to `MLMultiArray`; use shape and scalar type as part of the contract. For concurrency boundaries, `MLSendableFeatureValue` exists specifically to move feature values across concurrency domains before converting them to an `MLFeatureValue` at the model boundary.

When a model returns a classifier label and probability dictionary, preserve the distinction between a model score and a product decision. A confidence value is not universal truth, calibration, or authorization to perform a side effect.

## Prediction ownership and concurrency

Apple’s `MLModel` documentation states that one model instance should be used on one thread or dispatch queue at a time. Serialize calls to a shared instance or create a separate instance for each concurrency domain. Do not make a global model singleton that receives uncoordinated camera frames, UI requests, and background refreshes.

Recommended ownership:

```text
Capture actor / input adapter
  -> bounded frame or request policy
Model actor or serial executor
  -> one configured MLModel instance
Prediction adapter
  -> typed observation + model metadata
Main actor
  -> review UI state only
```

Use cancellation and supersession around the work that surrounds prediction: camera-frame throttling, preprocessing, model loading, and result publication. A synchronous prediction call itself should not be assumed to become cancellable merely because the surrounding Swift `Task` is cancelled. If the feature is live, drop stale frames rather than queueing unbounded work.

For stateful models, call `makeState()` to obtain an `MLState`, pass that state to the stateful prediction method, and serialize every prediction that shares it. Do not read or write state buffers while a prediction is in flight. A state object is a model-session resource, not a value to copy into unrelated tasks.

Batch prediction is a separate route from live inference. Use `MLBatchProvider` when the product benefits from batch semantics and can tolerate the memory, latency, and result-ordering rules. Keep the batch’s source IDs and model version attached to every normalized result.

## Vision bridge and media inputs

Vision can own image orientation, crop/scale, request scheduling, and observation types around a Core ML model. Use `VNCoreMLRequest` when the product’s image feature is naturally a Vision request and the output should be a Vision observation. Use direct Core ML when the model contract and preprocessing are already explicit or when the app needs a custom feature provider.

The adapter must make these choices visible:

- source asset or camera frame identifier;
- pixel format, orientation, crop/scale policy, and color space;
- whether the frame is user-selected, live, or background-derived;
- model asset/version and configuration;
- request generation and cancellation state;
- observation-to-domain normalization;
- minimum evidence required before an observation is shown or saved.

Do not describe a classifier’s output as a medical, identity, safety, or intent conclusion unless a separate validated product and regulatory route supports that claim. In a general-purpose utility, prefer language such as “model suggestion,” “detected candidate,” or “needs review.”

## Stateful, updatable, and personalized models

An updatable model is a special asset and workflow. `MLUpdateTask` updates an updatable compiled model with labeled data and reports progress/completion through its update context or progress handlers. Apple’s personalization documentation specifically notes that an update task operates on a compiled model ending in `.mlmodelc`.

Personalization requires more than a training button:

1. Explain what data becomes training data and obtain the required user choice.
2. Validate labels and input provenance before creating an `MLBatchProvider`.
3. Run the update away from interactive UI and surface progress, cancellation, failure, and storage state.
4. Save the updated compiled model through a temporary location and atomic replacement pattern.
5. Re-run the feature contract and evaluation fixture before promoting it.
6. Keep a known-good model and a reset/delete-personalization path.

Do not silently treat a personalized model as equivalent to the shipped model. Store model generation, training-data policy, and reset status separately from user-visible domain records.

## Reviewable inference as a product boundary

The safest default for AI-assisted native apps is:

`observation -> proposal -> user review -> deterministic validation -> committed action`

The proposal should carry:

- model ID/version and configuration policy;
- input-source IDs and capture times;
- normalized output fields and raw-score policy;
- uncertainty or “not enough evidence” state;
- explanation data that is actually supported by the model or deterministic inputs;
- edit/accept/reject state;
- expiry or invalidation when source data changes.

Never let a Core ML output silently mutate durable data, send a message, delete a file, change a financial record, or start a device action. Route those effects through an explicit app-owned command with authorization, validation, and confirmation.

## Liquid Glass and model states

Use Liquid Glass as a state container around inference, not as a confidence amplifier. A compact native shell can show:

- model status: bundled, downloading, compiling, validating, ready, unavailable, failed, or updating;
- a source label and timestamp;
- a small result summary with “suggested” or “detected” language;
- explicit review actions;
- a fallback action that works without the model.

Avoid putting a large glass panel over live media while the model is loading or while output is uncertain. Keep the input preview, model status, result, and action hierarchy distinct. Test bright/dark imagery, reduced transparency, increased contrast, Dynamic Type, VoiceOver, reduced motion, and a missing-model state. A material that looks premium in a screenshot can hide stale state or reduce legibility over camera content.

## Privacy, storage, and energy

On-device execution can reduce network exposure, but it does not make all handling automatically private. Define:

- whether source media, feature values, model outputs, and logs are retained;
- whether downloaded model assets are encrypted or protected at rest;
- whether precise location, faces, voices, health data, or documents enter the model;
- whether analytics record inputs, outputs, model versions, or only aggregate timings;
- how the user deletes source data, results, and personalized models;
- behavior when storage, memory, battery, thermal state, or permission is constrained.

Measure cold-load time, warm prediction latency, memory peak, dropped-frame rate, energy, and thermal behavior on named physical devices. A simulator run, a Debug timing, or a newest device is not a general performance claim.

## Availability and release gates

For every model route, record the deployment target and SDK used for the API surface, the model format and generated wrapper version, target membership, compiled resource membership, privacy strings for the input source, and whether the downloaded-model route needs network/background capabilities.

Separate the evidence layers:

| Layer | It proves | It does not prove |
| --- | --- | --- |
| Source/model inspection | Contract, metadata, version, supported model shape, update flag | Runtime performance or output quality. |
| Compile | The target can compile the source and generated wrapper | Correct resource membership or device behavior. |
| Preview/unit fixture | UI states, adapters, contract rejection, normalization | Real Core ML execution, Neural Engine use, or physical camera behavior. |
| Simulator | UI flow and some non-hardware model paths | Representative accelerator, memory, camera, thermal, or privacy behavior. |
| Signed physical device | Runtime asset, model load/prediction, permissions, input pipeline, assistive use, timings | TestFlight/App Store distribution or every device tier. |
| Release artifact | Signing, target membership, resources, privacy configuration, distribution route | Model quality or production service behavior by itself. |

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
- [MLMultiArray](https://developer.apple.com/documentation/coreml/mlmultiarray)
- [MLShapedArray](https://developer.apple.com/documentation/coreml/mlshapedarray)
- [MLPredictionOptions](https://developer.apple.com/documentation/coreml/mlpredictionoptions)
- [MLState](https://developer.apple.com/documentation/coreml/mlstate)
- [MLModel.makeState()](https://developer.apple.com/documentation/coreml/mlmodel/makestate%28%29)
- [MLUpdateTask](https://developer.apple.com/documentation/coreml/mlupdatetask)
- [Model personalization](https://developer.apple.com/documentation/coreml/model-personalization)
- [Personalizing a Model with On-Device Updates](https://developer.apple.com/documentation/coreml/personalizing-a-model-with-on-device-updates)
- [Downloading and Compiling a Model on the User’s Device](https://developer.apple.com/documentation/coreml/downloading-and-compiling-a-model-on-the-user-s-device)
- [Model Integration Samples](https://developer.apple.com/documentation/coreml/model-integration-samples)
- [VNCoreMLRequest](https://developer.apple.com/documentation/vision/vncoremlrequest)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
