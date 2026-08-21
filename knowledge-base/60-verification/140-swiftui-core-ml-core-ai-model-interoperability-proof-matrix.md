# SwiftUI Core ML and Core AI model-interoperability proof matrix

This matrix defines the evidence required for a feature that crosses Core ML, Vision, downloaded model delivery, on-device updates, or Core AI. It pairs with the [interoperability review](../42-framework-deep-dives/115-swiftui-core-ml-core-ai-model-interoperability-review.md), the [design review](../21-design-deep-dives/143-swiftui-core-ml-core-ai-model-interoperability-review-design.md), the [route](../50-capability-recipes/146-swiftui-core-ml-core-ai-model-interoperability-review-route.md), and the [recipe page](../70-code-recipes/158-swiftui-core-ml-core-ai-model-interoperability-review-recipes.md).

An artifact, compute plan, Vision observation, model update, successful prediction, or preview is only one kind of evidence. The release claim must identify the runtime lane, device, source contract, validation, accessibility, privacy, and signed artifact that support it.

## Evidence vocabulary

| Evidence | Can prove | Cannot prove |
| --- | --- | --- |
| Model/source manifest | Identifier, revision, digest, license, target, and contract are recorded | The model is accurate, compatible, fast, or safe |
| `.mlmodel` or `.aimodel` resource check | The intended source artifact is present | The target can compile, specialize, load, or run it |
| `MLModelAsset` inspection | Compiled Core ML asset can expose functions/description | Semantic quality or physical-device performance |
| Generated Core ML wrapper compile | Xcode can compile a known model target | Archive membership, downloaded-model behavior, or domain correctness |
| `MLModel.compileModel` result | A downloaded Core ML source was compiled into a device artifact | The artifact is trusted, accepted, or fast |
| `MLComputePlan` | Anticipated device use and estimated operation cost | Actual runtime device selection, thermal behavior, or latency |
| `MLModelConfiguration` | The requested Core ML compute policy and parameters | That the policy is optimal or available on every device |
| Vision request completion | A Vision request produced an observation for an input | The observation is current, semantically true, or authorized |
| Core AI debugger/asset run | Core AI graph/runtime behavior for its artifact lane | Core ML compatibility, domain quality, or iOS 26 support |
| Reference fixture comparison | Candidate output differs within the chosen numerical/task policy | Universal accuracy or user approval |
| SwiftUI screenshot | A state is visually rendered | Reading order, gesture access, privacy, or model behavior |
| Physical-device run | A signed build exercised the named route on a device/OS | Every device, camera condition, model revision, or release |
| Archive/TestFlight inspection | The distributed artifact contains intended targets/resources | App Store approval or production traffic behavior |

## Environment record

Capture before each run:

- app, target, bundle ID, build, source revision, and feature flag;
- Xcode, SDK, deployment target, macOS, Core ML/Core AI toolchain, and model-conversion version;
- runtime lane, model identifier/revision/digest/license, and artifact URL/path;
- source type, permission state, pixel format, orientation, color space, dimensions, crop/scale, and fixture digest;
- `MLModelConfiguration`/`MLComputeUnits` or Core AI specialization/device policy;
- device model, OS build, architecture, storage, power, network, and thermal state;
- request ID, frame ID, state/session ID, update revision, and fallback policy;
- privacy classification and retention decision for inputs, model files, logs, and reference artifacts.

## Lane and target matrix

| Claim | Required evidence | Pass condition |
| --- | --- | --- |
| Bundled Core ML model works | Target build, archive resource check, signed device run | Intended wrapper/MLModel loads and completes the fixture |
| Downloaded Core ML model works | Download, digest, compile, asset inspection, direct `MLModel` load, offline run | Verified `.mlmodelc` activates and runs without network |
| Vision route works | Permission, source/orientation/crop fixture, Vision request, observation mapping | Result is tied to the correct source/request and mapped safely |
| Live camera route works | Camera device, sequence handler/frame IDs, backpressure/cancel/interruption runs | Stale results are rejected and UI remains responsive |
| Core AI alternate lane works | iOS 27+ target, `.aimodel`/AOT, specialization/function/device run | Core AI route is proven separately from Core ML |
| iOS 26 fallback works | Signed iOS 26 device route | User can complete the promised outcome or receives a clear manual path |

## Asset and supply-chain matrix

| Claim | Test | Evidence |
| --- | --- | --- |
| Source is intended | Compare manifest to artifact | Identifier, revision, digest, license, target |
| Bundle membership is correct | Inspect build phases/archive | Resource belongs to the intended app/extension and is not accidentally duplicated |
| Download is safe | Transfer a valid and invalid candidate | HTTPS/version/digest/size/signature policy and rejection log |
| Core ML compilation is correct | Compile on a supported device | Source URL, compiled URL, OS/device, timing, result |
| Compiled asset is readable | Inspect `MLModelAsset`/description | Functions, input/output types, metadata, state capability |
| Core AI artifact is separate | Inspect `.aimodel`/AOT manifest | Core AI target/toolchain/architecture/digest record |
| Encryption policy is correct | Inspect key/team/build flags where used | Key ownership, archive/resource result, and no secrets in source |
| Update activation is atomic | Stage, fail, activate, rollback | Prior accepted revision remains runnable |

## Preprocessing and source matrix

| Claim | Test | Evidence | Pass condition |
| --- | --- | --- | --- |
| Orientation is preserved | Portrait/landscape/front-camera fixtures | Source orientation and handler/request record | Model sees the intended orientation |
| Crop/scale is intentional | Extreme aspect-ratio fixtures | `VNImageCropAndScaleOption`, region, model constraint | No unreviewed crop changes the meaning |
| Pixel format is compatible | Camera/photo/pixel-buffer fixtures | Pixel format, dimensions, color space | Invalid input is rejected before request |
| Source provenance survives | Change source during analysis | Source ID/frame ID/request ID | Candidate cannot attach to a different source |
| Permission failure is honest | Deny/revoke camera/photo access | System state and UI task result | App offers settings/picker/manual route |
| Live frame work is bounded | Sustained capture run | Admission/drop/cancel log and frame times | Work does not grow without bound |

## Core ML configuration and compute matrix

| Claim | Evidence | Pass condition |
| --- | --- | --- |
| Policy is recorded | Configuration snapshot | `computeUnits`, preferred device, precision/optimization hints are known |
| Default policy is acceptable | All/default versus restricted comparison | Product budget and quality/thermal requirements pass |
| CPU-only route is safe | Background/content-contention test | No hidden UI/latency claim exceeds the budget |
| Compute devices are understood | Available device and `MLComputePlan` record | Estimate is labeled as planning evidence |
| Runtime behavior is measured | Physical Instruments/debug-gauge/signpost trace | Actual latency/memory/thermal data is recorded by device/workload |
| Model instance ownership is correct | Concurrent call/cancellation test | Calls are serialized or isolated as documented |

## Vision request matrix

| Claim | Test | Evidence |
| --- | --- | --- |
| `VNCoreMLModel` maps the intended model | Model description and request construction | Model revision, request revision, model identity |
| Result type is understood | Classifier/general/image-to-image fixtures | Observation type and output mapping |
| Confidence is interpreted correctly | Known high/low/ambiguous fixtures | Raw value, calibration/threshold policy, no false normalization |
| Single image route works | `VNImageRequestHandler` with each supported input kind | Input/orientation/request/result record |
| Sequence route works | `VNSequenceRequestHandler` with frame changes | Frame order, state, stale/cancel handling |
| UI remains responsive | Main-thread/frame-time trace | Inference/preprocessing off main UI path |

## Model state and personalization matrix

| Claim | Test | Evidence | Pass condition |
| --- | --- | --- | --- |
| State resets correctly | Cold, continuation, reset, replacement | State/session IDs and output fixtures | No state crosses its intended boundary |
| Update data is authorized | Consent and labeled-data review | Data classification and retention record | Only approved data reaches `MLUpdateTask` |
| Update runs on compiled model | Update task fixture | Compiled model URL, update result | Route meets Core ML update prerequisite |
| Updated model is validated | Baseline versus updated fixture | Quality/regression report | Candidate is not activated solely because update completed |
| Rollback works | Corrupt/regressed update | Prior artifact and activation state | Old accepted revision is restored safely |
| Personalized state is private | Cross-account/reinstall tests | Storage ownership and deletion record | No user’s update leaks into another identity |

## Correctness and proposal matrix

Separate:

1. numerical/model output correctness;
2. preprocessing and source fidelity;
3. task-level quality on app-owned fixtures;
4. validation of ranges, schemas, record revisions, and permissions;
5. user approval or authorized workflow;
6. deterministic domain commit and undo.

For every candidate record model lane, revision, function/request, source/frame ID, preprocessing revision, raw observation/value, validation result, warnings, and approval decision. A Core ML confidence value or Core AI debugger score cannot substitute for this chain.

## Performance and resource matrix

Measure by model/device/workload:

- download and compilation time;
- Core ML/Core AI cold and warm load;
- first prediction/request latency;
- p50/p95/p99 prediction latency;
- peak memory with model, state, input, and output;
- camera frame interval, dropped frames, and UI hitching;
- CPU/GPU/Neural Engine use where observable;
- thermal/battery behavior under sustained work;
- cancellation and recovery time;
- storage/download/update/rollback cost.

Do not combine a compute-plan estimate, simulator run, Mac run, and physical-device measurement into one unlabeled “performance” claim.

## SwiftUI, Liquid Glass, and accessibility matrix

| Task | Evidence | Pass condition |
| --- | --- | --- |
| Choose source | UI test plus assistive-device run | Source identity and permission state are understandable |
| Prepare model | Physical/release run | Download/compile/specialize state is honest and cancellable |
| Observe image/frame | Device run | Current/stale/paused state is not color-only |
| Review result | VoiceOver/Dynamic Type/contrast run | Candidate, provenance, warning, and edit controls are reachable |
| Validate/apply | UI test plus domain fixture | Apply follows validation and approval |
| Recover failure | Forced missing/bad model/permission/thermal route | Source/draft survives and fallback is actionable |
| Use reduced effects | Reduced transparency/motion run | Glass is optional and content remains legible |

## Privacy and release matrix

| Claim | Evidence |
| --- | --- |
| Local processing is accurate copy | Actual Core ML/Core AI route and network/data-path record |
| Download path is disclosed | Model URL/version/digest/privacy/retention review |
| Camera/photo use is justified | Usage descriptions, permission flow, deletion/retention policy |
| Personalization is private | Storage ownership, update data policy, deletion, cross-account test |
| Model artifacts are protected | Encryption/key/team/build/archive review where used |
| Signed app contains intended route | Archive resources, target membership, entitlements, privacy metadata |
| TestFlight route works | Processed build, physical device, downloaded/update/fallback smoke test |
| App Store claim is supported | Metadata/review notes match target, permission, model, and fallback behavior |

## Evidence packet

~~~text
feature:
runtime_lane:
target:
bundle_id:
build:
sdk_xcode_macos:
deployment_target:
device_os_architecture:
source_id:
model_id_revision_digest_license:
artifact_kind_and_path:
compiled_or_specialized_artifact:
input_kind_format_orientation_dimensions:
crop_scale_preprocessing_revision:
request_or_function:
compute_policy:
compute_plan_estimate:
load_compile_specialization_latency:
prediction_or_frame_latency_p50_p95:
peak_memory_and_thermal:
source_frame_request_id:
raw_observation_or_output:
validation_result:
approval_result:
update_state_and_rollback:
fallback_route:
accessibility_tasks:
privacy_review:
archive_result:
testflight_result:
release_decision:
known_gaps:
~~~

## Stop criteria

Block release when:

- runtime lane, model revision, digest, license, or preprocessing is unknown;
- a downloaded model is activated before compile/asset/contract verification;
- Core ML and Core AI are represented as interchangeable artifacts;
- Vision results lack orientation, source/frame, request, or stale-result evidence;
- compute policy is forced without workload/device/thermal proof;
- a model update or state object crosses a user/request/record boundary;
- confidence, compute-plan cost, or debugger similarity is presented as semantic truth;
- a simulator/preview/Mac trace stands in for physical camera, compute, thermal, or release proof;
- the signed archive/TestFlight build has not exercised the final model route;
- accessibility is reduced to a screenshot or automated audit score;
- the iOS 26 fallback is incomplete or missing.

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
- [Generating a Model Encryption Key](https://developer.apple.com/documentation/coreml/generating-a-model-encryption-key)
- [Encrypting a Model in Your App](https://developer.apple.com/documentation/coreml/encrypting-a-model-in-your-app)
- [Core AI](https://developer.apple.com/documentation/coreai)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
