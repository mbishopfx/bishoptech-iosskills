# SwiftUI Core ML and Core AI model-interoperability route

This route turns the [model-interoperability review](../42-framework-deep-dives/115-swiftui-core-ml-core-ai-model-interoperability-review.md) into an implementation sequence. Pair it with the [design review](../21-design-deep-dives/143-swiftui-core-ml-core-ai-model-interoperability-review-design.md), the [proof matrix](../60-verification/140-swiftui-core-ml-core-ai-model-interoperability-proof-matrix.md), and the [code recipes](../70-code-recipes/158-swiftui-core-ml-core-ai-model-interoperability-review-recipes.md).

The route supports a bundled Core ML model, a downloaded/compiled Core ML model, Vision image or camera input, a Core AI model on its supported target, and a deterministic fallback. Choose one primary lane for the feature and document the others as explicit fallback or alternate-target routes.

## 1. Freeze the product contract

Write down:

- user outcome and whether the result is transient, reviewable, or durable;
- source types: photo, camera frame, document, audio-derived feature, or structured data;
- Core ML/Vision/Core AI runtime lane and fallback;
- model identifier, revision, license, digest, target OS, and architecture/device class;
- input/output names, feature types, shapes, orientation, crop/scale, and normalization;
- compute-unit policy, latency/memory/thermal budgets, and cancellation behavior;
- model update/personalization policy and rollback revision;
- validation, approval, deterministic commit, undo, and privacy retention.

Do not begin with a generated wrapper or prediction call. Begin with the contract the app has to preserve.

## 2. Select the runtime lane

Use this decision:

1. If the model is a known Core ML artifact and a generated wrapper/Vision integration fits, use bundled Core ML.
2. If the model is user-selected or too large to bundle, use downloaded Core ML with device compilation and direct `MLModel` loading.
3. If the input is an image, pixel buffer, or sample buffer and Vision observations fit, wrap the Core ML model in `VNCoreMLModel` and use the appropriate Vision handler.
4. If the model requires the Core AI toolchain or current Apple-silicon architecture, use Core AI behind its exact OS/SDK gate.
5. If the selected lane is unavailable, use a deterministic/manual route that still fulfills the product contract.

Do not call a Core ML `.mlmodelc` a Core AI asset or use Core AI availability as a substitute for Core ML model compatibility.

## 3. Establish the asset and manifest

Create an app-owned manifest containing:

- runtime lane and artifact kind;
- identifier/revision/digest/license;
- source and compiled URLs or bundle resource names;
- minimum OS and device/architecture policy;
- model input/output and preprocessing contract;
- Core ML `MLModelConfiguration` policy or Core AI specialization options;
- Vision request type/revision/crop/scale/orientation policy;
- update, activation, rollback, and deletion policy;
- fallback route and acceptance fixture IDs.

For dynamically delivered Core ML, verify the source before compilation and keep the compiled artifact in an inactive slot until preflight succeeds. For Core AI, keep `.aimodel`/AOT identity and Metal Toolchain evidence separate.

## 4. Build the input pipeline

For a photo:

1. request the least-privilege Photos/camera access required;
2. preserve source identity, orientation, color, and dimensions;
3. choose the Vision crop/scale policy from the model input constraint;
4. create `VNImageRequestHandler` with known orientation where available;
5. assign a request ID and source revision;
6. map the observation to an app-owned candidate.

For live camera:

1. configure capture output and pixel format;
2. use `VNSequenceRequestHandler` or a supported request route;
3. bound frame admission and work concurrency;
4. associate every result with frame/request IDs;
5. reject late/stale results after cancellation or model replacement;
6. pause and recover on interruptions/backgrounding/permission changes.

For structured Core ML inputs, use `MLFeatureProvider`/`MLFeatureValue` contracts and validate shape, type, range, and missing values before prediction.

## 5. Prepare a bundled Core ML model

1. Add the `.mlmodel` to the intended Xcode target.
2. Confirm generated wrapper ownership and target membership.
3. Install any required model compiler/toolchain components.
4. Inspect model description, inputs, outputs, metadata, and optional functions.
5. Configure `MLModelConfiguration` explicitly only where the product needs a policy.
6. Load asynchronously or through the generated wrapper’s supported path.
7. Keep the model owner stable and serialize access as required.
8. Expose preparation/failure states before accepting user input.

A successful build proves only that the target can compile the resource. Inspect the archive and run the signed device route.

## 6. Prepare a downloaded Core ML model

1. Download to a quarantine URL with cancellation and resumable/retry policy.
2. Check transport, expected version, digest, license, minimum OS, and target allowlist.
3. Compile the `.mlmodel` on the device using `MLModel.compileModel(at:)` or the current async interface, off the main actor.
4. Inspect the resulting `.mlmodelc` with `MLModelAsset` and the model description.
5. Load through `MLModel.load(contentsOf:configuration:)`.
6. Store the candidate outside the active slot until loading/preflight passes.
7. Atomically promote the candidate and retain the prior accepted revision.
8. Reconcile storage and delete old artifacts only when no in-flight request uses them.

Apple’s current Core ML documentation specifically distinguishes dynamically downloaded/compiled models from generated wrapper models: use `MLModel` directly for predictions in that route.

## 7. Choose and measure compute policy

Start with the default/all `MLComputeUnits` policy. Add a CPU-only, CPU/GPU, or CPU/Neural Engine restriction only when a measured requirement exists. Record:

- selected policy;
- available compute devices;
- model size and input workload;
- cold/warm load and prediction latency;
- peak memory, frame time, thermal state, and battery impact;
- background/foreground behavior;
- fallback if the preferred route cannot run.

Use `MLComputePlan` to inspect anticipated operation device usage and estimated cost before runtime. Use physical-device tracing to support actual performance claims.

## 8. Add Core ML model state or personalization

If using a stateful or updatable Core ML model:

1. identify the state/reset boundary;
2. create state per request/session/user as appropriate;
3. serialize access to one model instance or isolate instances by queue;
4. feed only consented/validated update data;
5. run `MLUpdateTask` against a compiled model;
6. save the updated model to a temporary location;
7. validate it before replacing the active revision;
8. keep rollback and deletion evidence.

Personalization changes a model’s behavior; it is not just a cache refresh. Keep private user updates distinct from product-wide model revisions.

## 9. Add Vision request ownership

Create one stable `VNCoreMLModel` per underlying Core ML model when sharing is appropriate. Keep request construction and completion mapping in one adapter. The adapter should own:

- `VNCoreMLRequest` revision and crop/scale option;
- source orientation and pixel-buffer format;
- observation mapping;
- confidence semantics and domain threshold;
- request cancellation/stale-result check;
- error/fallback mapping.

Keep UI state on the main actor; keep request execution and image preprocessing off the main actor. In a live route, use bounded concurrency rather than a task for every frame.

## 10. Define the Core AI bridge

If the product supports both Core ML and Core AI:

1. define a shared app-owned source/candidate/validation envelope;
2. implement separate Core ML and Core AI adapters;
3. gate Core AI by deployment target, SDK, asset, device, and toolchain;
4. map each adapter’s output and diagnostics into the envelope;
5. record runtime lane/model revision in the proposal;
6. use the same deterministic validation and approval path;
7. preserve the iOS 26 fallback when the Core AI target is unavailable.

Do not hide different preprocessing or output semantics behind a single untyped `[String: Any]` map.

## 11. Design the SwiftUI state machine

```text
sourceMissing
permissionRequired
sourceReady
modelMissing
downloading
verifying
compiling
specializing
ready
running
stale
candidate
validationFailed
approved
committed
failed
fallback
```

Transitions should carry source ID, model revision, runtime lane, request ID, and generation token. A late completion is ignored when its token no longer matches the active route.

## 12. Build the review screen

Show:

- source preview or current-frame label;
- model lane/revision and readiness;
- preprocessing disclosure;
- result/candidate values in editable semantic controls;
- warnings, quality/confidence explanation, and validation status;
- Apply, Reject, Retry, Manual, Undo, or Fallback actions;
- privacy/data-path copy.

Use native controls and modest Liquid Glass grouping for small action clusters. Keep large visualizations, image details, and warnings legible on opaque or high-contrast surfaces.

## 13. Verify the edge states

Force and record:

- denied/revoked camera or Photos permission;
- missing model, wrong digest, bad license, invalid signature, and incompatible OS;
- compile/load failure and low-storage failure;
- wrong feature type/shape, invalid pixel format, orientation mismatch;
- model replacement during an in-flight request;
- camera interruption, backgrounding, and stale frame;
- model update failure and rollback;
- thermal/memory pressure and cancellation;
- Core AI unavailable on iOS 26;
- empty, rejected, or manually corrected candidate.

Every forced failure needs a user-facing next action and a proof that no invalid result was committed.

## 14. Verify accessibility and privacy

Test source selection, preparation, review, validation, approval, and fallback with VoiceOver, Dynamic Type, increased contrast, reduced transparency, reduced motion, keyboard/Full Keyboard Access, Switch Control, and pointer input. Ensure the model lane, revision, source, stale status, and blocked action are spoken.

Review camera/photo authorization, model download disclosures, personalized-data retention, debug/reference artifacts, model encryption, logs, and deletion. The UI must describe actual data flow rather than claiming “private” because inference is local while the source or model is downloaded or retained.

## 15. Package and release

Before archive:

1. validate model/license/digest manifest;
2. inspect target membership and generated wrapper/compiled resources;
3. inspect Core AI artifacts separately if present;
4. run fixtures for the bundled/downloaded/fallback lanes;
5. run accessibility and privacy checks;
6. archive and inspect resources/entitlements/privacy metadata;
7. install the signed build on each claimed device class;
8. run processed TestFlight build and update/rollback route;
9. record known gaps and device restrictions;
10. ensure App Store copy matches model lane, permissions, and data retention.

## Stop conditions

Stop when a model can be loaded but its source, revision, preprocessing, device lane, output mapping, or fallback is unknown. Stop when a Core AI-only path is represented as iOS 26 support, when a Vision result can commit without review, when a personalized model replaces a baseline without rollback, or when performance claims rely on a simulator or Mac-only run.

## Sources

- [Core ML](https://developer.apple.com/documentation/coreml)
- [MLModel](https://developer.apple.com/documentation/coreml/mlmodel)
- [MLModelAsset](https://developer.apple.com/documentation/coreml/mlmodelasset)
- [MLModelConfiguration](https://developer.apple.com/documentation/coreml/mlmodelconfiguration)
- [MLComputeUnits](https://developer.apple.com/documentation/coreml/mlcomputeunits)
- [MLComputePlan](https://developer.apple.com/documentation/coreml/mlcomputeplan-1w21n)
- [compileModel(at:)](https://developer.apple.com/documentation/coreml/mlmodel/compilemodel%28at%3A%29-3nea?changes=la__5)
- [Model Personalization](https://developer.apple.com/documentation/coreml/model-personalization)
- [Personalizing a Model with On-Device Updates](https://developer.apple.com/documentation/coreml/personalizing-a-model-with-on-device-updates)
- [Classifying Images with Vision and Core ML](https://developer.apple.com/documentation/coreml/classifying-images-with-vision-and-core-ml)
- [VNCoreMLRequest](https://developer.apple.com/documentation/vision/vncoremlrequest)
- [VNImageRequestHandler](https://developer.apple.com/documentation/vision/vnimagerequesthandler)
- [VNSequenceRequestHandler](https://developer.apple.com/documentation/vision/vnsequencerequesthandler)
- [Core AI](https://developer.apple.com/documentation/coreai)
- [Integrating on-device AI models in your app with Core AI](https://developer.apple.com/documentation/coreai/integrating-on-device-ai-models-in-your-app-with-core-ai)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
