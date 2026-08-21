# SwiftUI Core ML and Core AI model-interoperability review

This review covers the production boundary between Core ML, Vision, camera/photo input, downloaded model assets, and the newer Core AI runtime. It pairs with the [Core ML/Core AI interoperability design](../21-design-deep-dives/143-swiftui-core-ml-core-ai-model-interoperability-review-design.md), the [interoperability route](../50-capability-recipes/146-swiftui-core-ml-core-ai-model-interoperability-review-route.md), the [proof matrix](../60-verification/140-swiftui-core-ml-core-ai-model-interoperability-proof-matrix.md), and the [recipe collection](../70-code-recipes/158-swiftui-core-ml-core-ai-model-interoperability-review-recipes.md).

The key decision is not “which AI API sounds newest?” It is “which model artifact, input contract, compute policy, device lane, and evidence packet can this product actually support?” Core ML provides a broad model representation and integrates with Vision, Natural Language, Speech, and other domain frameworks. Core AI is the Apple-silicon-oriented route for newer model architectures and inference techniques. A product can expose one user-facing feature across both, but it should keep the adapters and proof separate.

## 1. Runtime lanes are explicit

| Lane | Use when | Primary artifact | Important boundary |
| --- | --- | --- | --- |
| Bundled Core ML | The model is known at build time and the app can ship it in the target | `.mlmodel` compiled for the app, usually with generated wrapper access | Target membership, generated wrapper, model version, and archive contents must agree |
| Downloaded Core ML | Model choice or size makes post-install delivery useful | Downloaded `.mlmodel` compiled on device to `.mlmodelc` | Verify source/version/digest, compile off the main thread, activate atomically, and use `MLModel` directly |
| Vision + Core ML | The input is an image, pixel buffer, or sample buffer and Vision’s request/observation types fit the task | `MLModel` wrapped in `VNCoreMLModel` | Image orientation, crop/scale policy, request revision, confidence semantics, and frame admission are part of the contract |
| Core ML tensor/state route | The model needs lower-level feature providers, sequence/state, compute-plan inspection, or on-device personalization | Compiled Core ML model and `MLModel`/state objects | Thread/queue ownership, feature descriptions, state reset, and update/replacement are explicit |
| Core AI | The model uses current Apple-silicon architectures, Core AI assets, or custom Core AI/Metal authoring | `.aimodel` or AOT Core AI artifact | Core AI has its own conversion, specialization, function, cache, and device/toolchain gates |
| Deterministic fallback | The model is unavailable, unsupported, too slow, or not approved for the current target | App-owned algorithm/manual review | It must complete the promised user journey or state the next action clearly |

Do not infer that a `.mlmodelc` can be passed to Core AI, or that an `.aimodel` can be loaded through the generated Core ML wrapper. Share an app-owned feature contract and proposal envelope, not a falsely shared runtime implementation.

## 2. Core ML asset lifecycle

The Core ML lifecycle has distinct artifact stages:

1. source model or model package;
2. conversion/export into Core ML format;
3. Xcode target inclusion or post-install delivery;
4. device compilation into `.mlmodelc` when the source is downloaded;
5. `MLModelAsset` or compiled-model inspection;
6. asynchronous `MLModel` loading with `MLModelConfiguration`;
7. feature-provider or Vision request execution;
8. app-owned result validation and review;
9. deterministic domain commit.

The generated model wrapper is convenient for a model known at build time. A dynamically downloaded and compiled model is a different route: Apple’s Core ML documentation says to use `MLModel` directly for predictions, and a model instance must be serialized to one thread or dispatch queue or replaced with separate instances.

`MLModelAsset` is useful for structural inspection of a compiled model and exposes function names and descriptions. It is not semantic validation, a performance guarantee, or a replacement for running the model in the signed app.

## 3. Core AI is a separate authoring and runtime lane

Core AI starts from an `.aimodel` artifact and specializes it for the device. Its app route includes a Metal Toolchain, function contracts, device specialization/cache, `NDArray` or image descriptors, compute streams, and current Core AI target gates. Its authoring route includes Core AI PyTorch Extensions, Core AI Optimization, custom Metal, Core AI Debugger, and AOT compilation.

Use Core ML when the model and surrounding framework contract are Core ML’s strength: broad model types, generated wrappers, Vision integration, on-device updates, or an existing Core ML deployment. Use Core AI when the model requires the current Core AI architecture/toolchain or the product has deliberately accepted its iOS 27/Xcode 27/macOS 27 lane. Keep an iOS 26 path in the product plan when Core AI is unavailable.

The integration layer can normalize both runtimes into an app-owned envelope:

```text
source_id + model_revision + runtime_lane + function + input_provenance
    -> typed candidate + diagnostics + validation status
    -> review and approval
    -> deterministic domain command
```

That envelope does not make the underlying model contracts interchangeable.

## 4. Compute-unit policy is a product decision

`MLModelConfiguration.computeUnits` controls the processing-unit configurations Core ML may use. The documented choices include allowing all available units, CPU-only, CPU plus GPU, and CPU plus Neural Engine. `MLModelConfiguration` also exposes a preferred Metal device, low-precision GPU accumulation, model parameters, and optimization hints.

Start with the system-default/all policy unless the product has evidence for a restriction. CPU-only can make sense for a background or GPU-contention route; it is not a universal “safe” performance setting. A forced policy needs a named device matrix, workload, thermal budget, and fallback. Record the policy in the model manifest and in the evidence packet.

Core ML’s `MLComputePlan` can estimate the compute-device usage and cost of operations in an ML Program before prediction. Treat it as planning evidence, not actual runtime telemetry. Pair it with a physical-device measurement, debug gauge, Instruments, signposts, or MetricKit evidence for the claim you want to make.

## 5. Input provenance is part of correctness

For a photo or camera frame, preserve:

- source identifier and permission state;
- pixel format, dimensions, color space, and orientation;
- crop/scale policy and region of interest;
- capture timestamp and frame sequence where relevant;
- model input constraint and preprocessing revision;
- whether the frame was user-selected, live camera, cached, or synthesized;
- privacy/retention decision for the source and derived result.

`VNImageRequestHandler` processes requests for a single image and accepts image data, URL, Core Graphics image, Core Image image, pixel buffer, or sample buffer, with optional orientation. `VNSequenceRequestHandler` is the route for a series of frames. A live pipeline must add frame admission, cancellation, backpressure, stale-result rejection, and teardown; “Vision performed” is not proof that the result belongs to the currently visible frame.

`VNCoreMLRequest` adapts a Core ML model to Vision image analysis. Its result type depends on the model description and output features. Vision forwards Core ML confidence values as-is; it does not make an app’s confidence threshold, class semantics, or decision policy for it.

## 6. Model loading and concurrency

For a bundled model:

1. keep the model in the intended target and inspect the archive;
2. load with the generated wrapper or `MLModel` configuration;
3. share a stable model/container when the route is safe to share;
4. create a request or feature provider for each operation;
5. perform inference off the main actor;
6. return a typed candidate to the main-actor review state.

For a downloaded model:

1. download to a quarantine location;
2. verify version, digest, license, and target policy;
3. compile the `.mlmodel` on device off the main thread;
4. inspect the compiled asset and model description;
5. atomically activate the `.mlmodelc` only after preflight;
6. load it with `MLModel.load(contentsOf:configuration:)`;
7. retain the prior accepted revision for rollback;
8. remove stale artifacts only after no active operation uses them.

Loading or compilation is not readiness until the app has a usable model instance, matching contract, resource budget, and error/fallback state. A cancellation token or generation ID should prevent a late result from an old model revision from overwriting a newer proposal.

## 7. On-device updates and state

Core ML supports updatable models and `MLUpdateTask` for model personalization. Apple’s update route operates on a compiled model file and calls the completion handler on a separate thread. The app must decide whether the update is:

- a private user personalization;
- a model revision distributed by the product;
- an experiment isolated behind a feature flag;
- or an unapproved change that must not affect domain decisions.

Persist update metadata, training-data consent/classification, source revision, validation results, and rollback state. Never allow a personalized model to silently replace a shared baseline for another account or to change an authorization policy.

`MLState` and sequence/state APIs require an explicit reset and ownership policy. A state object belongs to a request/session boundary; it should not leak across users, records, or privacy domains. Test cold state, continuation, cancellation, app termination, model replacement, and memory pressure.

## 8. Vision and Core ML live pipelines

For a live camera or media route:

1. obtain camera authorization and configure the capture session;
2. define the pixel format and orientation contract;
3. admit frames at a measured cadence or use the latest-frame policy;
4. run `VNSequenceRequestHandler` or the chosen request route off the UI path;
5. associate each observation with a frame/request ID;
6. reject stale completions after cancellation or model replacement;
7. throttle UI updates and preserve a reviewable snapshot;
8. pause/recover for interruptions, backgrounding, route changes, memory pressure, and permission changes.

A camera observation is evidence about an input frame, not automatically a truth about a person, object, or authorization. Domain validation and user review remain app responsibilities.

## 9. Security, privacy, and model supply chain

Model privacy has at least four parts:

- where the source input is processed;
- whether the model or compiled artifact is bundled, downloaded, or personalized;
- how model/debug/reference artifacts are encrypted, logged, retained, and deleted;
- how a model revision is allowed to affect a domain action.

Apple documents model encryption keys and compile-time model encryption for bundled models. Encryption protects an artifact but does not make an untrusted model trustworthy. Verify source, license, digest, target, and capabilities before activation. Keep model keys and credentials out of source control and never treat a remote model manifest as permission to execute arbitrary tools or domain actions.

## 10. Native SwiftUI and Liquid Glass states

Use standard SwiftUI navigation, controls, typography, and system containers as the baseline. A model workflow benefits from a native shell with distinct states:

- selecting a photo/camera source;
- waiting for permission;
- compiling/downloading/preparing;
- ready with model/revision/compute-lane identity;
- observing a live frame;
- reviewing a candidate with evidence and warnings;
- validating or rejecting;
- committing a deterministic change;
- falling back or recovering from a stale/failed model.

Liquid Glass can provide hierarchy and grouping for small control clusters, but it should not blur source provenance, warning status, model revision, or review actions. Keep large image/tensor/debug content legible and provide a non-glass path for reduced transparency, contrast, Dynamic Type, VoiceOver, keyboard, Switch Control, and pointer use.

## 11. Evidence and release gates

The claim “this app uses an on-device model” needs more than a model file:

1. source/model/license/digest record;
2. input preprocessing and output mapping contract;
3. compile/load/compute policy evidence;
4. Core ML or Vision request evidence on a named device;
5. numerical and task-level fixture validation;
6. memory, latency, thermal, cancellation, and stale-result evidence;
7. privacy and update/rollback review;
8. accessibility task completion;
9. signed archive and processed TestFlight route;
10. App Store metadata that matches actual data/model behavior.

For Core AI, add its own asset, specialization, function, AOT, debugger, and target proof. For Core ML, add compiled-model, `MLModelAsset`, `MLComputePlan`, `MLModelConfiguration`, Vision, and dynamic-update proof where used.

## Stop conditions

Stop before release when:

- the runtime lane is selected by API novelty rather than model/target evidence;
- a downloaded model is compiled or activated without digest/license/version checks;
- Core ML and Core AI artifacts are treated as interchangeable;
- preprocessing loses orientation, crop/scale, color, frame, or source provenance;
- a `VNCoreMLRequest` confidence is treated as normalized truth or authorization;
- a live-frame result can arrive after cancellation/model replacement and still mutate state;
- a compute-plan estimate is presented as an observed performance measurement;
- an on-device update changes durable behavior without validation, approval, and rollback;
- model encryption is mistaken for model trust;
- a simulator or preview is used as physical-camera, Neural Engine, thermal, or release evidence;
- the iOS 26 fallback is absent when the Core AI target lane is unavailable.

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
- [Integrating on-device AI models in your app with Core AI](https://developer.apple.com/documentation/coreai/integrating-on-device-ai-models-in-your-app-with-core-ai)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
