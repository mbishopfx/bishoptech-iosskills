# SwiftUI Core AI on-device model-runtime proof matrix

This matrix defines what must be proven before an app claims to use a custom Core AI model on device. It pairs with the [Core AI runtime review](../42-framework-deep-dives/113-swiftui-core-ai-on-device-model-runtime-review.md), the [Core AI design review](../21-design-deep-dives/141-swiftui-core-ai-on-device-model-runtime-review-design.md), and the [Core AI route](../50-capability-recipes/144-swiftui-core-ai-on-device-model-runtime-review-route.md).

The current Core AI documentation describes an iOS 27, macOS 27, and Xcode 27-or-later integration route. The Foundation Models session is an iOS 26 route for supported system-model features. Proof must record which lane was actually tested.

## Evidence vocabulary

| Evidence type | Can prove | Cannot prove |
| --- | --- | --- |
| Source artifact | A specific model package exists at a recorded digest | It is compatible, fast, accurate, or safe |
| AIModelAsset inspection | The source asset is structurally readable and exposes metadata/functions | It can specialize on a device or produce a useful result |
| Xcode model viewer | Human-readable function, metadata, and storage review | Runtime availability or semantic correctness |
| AOT build output | Architecture-specific aimodelc files were produced by the recorded toolchain | The target device selected one or that remaining specialization succeeds |
| Cache hit | A specialized artifact was available for the source/options key | The model’s output is correct |
| Physical-device load | A signed build loaded an artifact on a named device | Every supported device or every model input works |
| Inference trace | A named function ran with measured timing and resources | The output is domain truth |
| Debugger reference comparison | Numerical divergence against a reference run is within the chosen threshold | User-facing quality or domain validity |
| SwiftUI screenshot | A state is visually present | Accessibility, interaction, or physical model behavior |
| Archive inspection | The signed artifact contains intended targets, resources, entitlements, and metadata | App Store approval or real device behavior |
| TestFlight run | The distributed build can exercise a route in the selected environment | Universal device coverage or production quality |

Never substitute a simulator screenshot, successful compile, or model response for a different evidence type.

## Target and environment record

Record this before each evidence run:

- app name and bundle identifier;
- target name and extension/package ownership;
- source revision and branch/commit;
- Xcode version and SDK;
- deployment target;
- macOS version for model tooling;
- Metal Toolchain version;
- model identifier and revision;
- tokenizer and companion-resource revision;
- source or AOT artifact name and digest;
- device model, OS build, architecture, and storage state;
- network, power, battery, and thermal conditions when relevant;
- feature flag and fallback policy.

## iOS 26 and iOS 27 lane matrix

| Claim | iOS 26 evidence | iOS 27 Core AI evidence | Pass condition |
| --- | --- | --- | --- |
| Feature has a working baseline | Signed iOS 26 physical-device route | Same product outcome or explicitly richer route | User can complete the fallback workflow |
| Core AI is not used on iOS 26 | Target imports/resources/archive inspection | N/A | No unavailable Core AI symbols or assets leak into the iOS 26-only target |
| Core AI target is available | N/A | Deployment/build/physical-device record | All documented OS/toolchain gates are satisfied |
| Model resource is present | Baseline model/fallback evidence | Bundle or delivered Core AI resource evidence | Intended manifest and digest match |
| Model is ready | Baseline route-specific readiness | Asset preflight, specialization/cache, function load | UI does not claim ready before all gates pass |
| Result quality | iOS 26 fixture and deterministic checks | Core AI reference/device fixture and deterministic checks | Acceptance threshold is recorded and passed |

## Asset and packaging matrix

| Claim | Required evidence | Failure interpretation |
| --- | --- | --- |
| Source model is the intended revision | Manifest, digest, license, author, revision, target platform | Stop delivery; do not load an unverified candidate |
| Asset structure is readable | AIModelAsset load and summary output | Conversion or packaging issue |
| Function contract is compatible | Descriptor snapshot for names, types, shapes, dynamic bounds | Model/app schema mismatch |
| Companion resources exist | Tokenizer/resource manifest and local file check | Provider/resource not ready |
| Xcode target owns the resource | Build phase and archive resource inspection | Resource may be missing or duplicated |
| Metal Toolchain is installed | Xcode/toolchain record and successful target build | Target configuration incomplete |
| AOT assets match policy | coreai-build command record, output names, minimum OS, architecture list | Rebuild or deliver a source asset/fallback |
| Device selects the correct AOT file | Physical architecture record and selected asset log | Device routing is unproven |
| Background delivery is correct | Background Assets manifest, transfer, install, update, and recovery evidence | Delivery layer is not ready even if the model itself is valid |

## Load and specialization matrix

| Claim | Test | Evidence | Pass condition |
| --- | --- | --- | --- |
| Bundled source loads | Cold launch on a supported physical device | Build, device, model revision, load result | AIModel returns or a typed fallback appears |
| Downloaded source loads | Download, restart, and load without network after install | Delivery record and offline run | Local route is available after verified install |
| Cache hit works | Reopen with same source URL and options | Cache lookup and timing | Cached load is used without unsafe assumptions |
| Cache miss recovers | Delete or invalidate cache, then load | Specialization state and error handling | App shows preparation and succeeds or falls back |
| OS update invalidation recovers | Run after an OS update or simulated invalidation fixture | Bookmark/cache result | App re-downloads or re-specializes safely |
| Source revision update recovers | Install candidate, compare, activate, rollback | Old/new cache and activation records | In-use model is not replaced unsafely |
| Compute policy is respected | Test default and any CPU/GPU/Neural Engine preference | Specialization options and Instruments trace | The chosen policy matches the product rationale |
| Dynamic shapes are bounded | Exercise minimum, typical, maximum, and invalid shapes | Descriptor and input-validation evidence | Invalid shapes never reach inference |
| Function resources are released | Navigate away, cancel, and load another model | Memory and lifecycle trace | No unbounded function/resource accumulation |

## Inference matrix

| Claim | Test | Evidence |
| --- | --- | --- |
| Named inputs are mapped correctly | Use a known fixture for every input | Input name/type/shape record |
| NDArray writes are valid | Fill a mutable view with known values | Tensor checksum or fixture output |
| Image inputs preserve metadata | Exercise orientation, color space, crop, and pixel format | Source and descriptor record |
| Outputs are typed | Remove each named output and inspect NDArray/pixel-buffer kind | Output descriptor and result record |
| Stateful execution is correct | Run repeated steps with reset and continuation cases | State initialization and output fixture |
| ComputeStream ordering is correct | Encode dependent and independent operations | Stream completion and result order |
| Concurrent policy is bounded | Exercise overlapping requests | Admission log and memory trace |
| Cancellation is honest | Cancel before load, during specialization, and during inference | Cancellation state and no-commit proof |
| Errors are typed | Use missing function, invalid asset, mismatch, and resource failures | Error mapping and recovery UI |
| Result provenance survives | Persist source/model/function/revision on the proposal | Result record and review screen |

## Correctness matrix

### Numerical correctness

Use Core AI Debugger to visualize and execute the asset and compare intermediate or output tensors against a reference run. Record:

- reference model and source revision;
- input fixture digest;
- operation mapping;
- similarity or divergence measure;
- quantization/specialization settings;
- accepted threshold and rationale;
- device target;
- any known expected drift.

Numerical similarity is a conversion and runtime check. It is not proof that a generated label, measurement, or action is valid in the app’s domain.

### Semantic and domain correctness

Use app-owned fixtures and deterministic validators for:

- finite values and ranges;
- known labels and classes;
- geometry bounds;
- OCR or barcode comparison;
- authorization and account ownership;
- current record revision;
- user-approved changes;
- idempotent domain commit;
- rollback or undo.

For generative models, test structured-output parsing, refusal/error states, tool calls, and prompt/model revision behavior separately from raw token quality.

## Memory, thermal, and performance matrix

| Claim | Required measurement |
| --- | --- |
| Initial load is acceptable | Cold load and specialization duration on each claimed device class |
| Warm load is acceptable | Cache hit and function-load timing after relaunch |
| Interactive inference is responsive | Median, p95/p99, cancellation, and main-thread responsiveness |
| Memory fits | Peak process memory with model, function, inputs, outputs, and concurrent work |
| Sustained workload is safe | Repeated inference trace with thermal and battery notes |
| Compute policy is effective | Core AI instrument showing CPU/GPU/Neural Engine activity |
| AOT improves startup | Source versus AOT comparison with same model/device and recorded toolchain |
| Live source is bounded | Frame/request admission, dropped work, and UI responsiveness |

The evidence must name the device and workload. A single fast sample on a Mac is not an iPhone performance claim.

## Foundation Models bridge matrix

| Claim | Evidence | Pass condition |
| --- | --- | --- |
| Core AI model can back a session | iOS 27 physical-device provider load | CoreAILanguageModel initializes from the intended resource folder |
| Provider capabilities are declared | LanguageModelCapabilities snapshot | The app dispatches only supported vision, guided-generation, reasoning, or tool requests |
| Executor is prepared | LanguageModelExecutor prewarm and configuration record | Preparation is cancellable and errors are surfaced |
| Transcript translation is correct | Request fixture with supported transcript segments | Model receives the intended context without silent segment loss |
| Generation options are honored | Sampling/context fixture | Unsupported options are rejected or intentionally approximated and documented |
| Streaming is ordered | Channel event capture | Metadata/usage/response/tool events follow the provider contract |
| Tools are bounded | Tool-call fixture with denial, retry, and side effect | App authorization and max-turn policy hold |
| Reasoning is not leaked accidentally | Reasoning segment fixture | Person-facing UI receives reviewed content only |
| iOS 26 fallback exists | Same product journey on iOS 26 signed device | User can finish or receives a clear next action |

## SwiftUI and Liquid Glass matrix

| Claim | Evidence | Pass condition |
| --- | --- | --- |
| Preparation is visible | UI test and physical-device run | Person can tell whether the model is preparing or running |
| Result is a proposal | Review fixture | Apply is unavailable until validation/approval gates pass |
| Source is visible | Accessibility and visual task | Person can identify the input and revision |
| Failure is recoverable | Forced failure route | Source/draft survives and a fallback is offered |
| Glass remains functional | Contrast/transparency/motion variants | Controls and status remain legible and actionable |
| Native behavior is preserved | UI review across size classes | Standard navigation, typography, controls, and safe areas remain coherent |

## Accessibility matrix

Test with VoiceOver, Dynamic Type, increased contrast, reduced transparency, reduced motion, keyboard navigation, Switch Control, pointer input, and Full Keyboard Access. Record task completion, not just screenshots.

Required tasks:

1. choose or confirm a source;
2. start model preparation or inference;
3. cancel an in-flight request;
4. understand the model and data path;
5. review the generated proposal;
6. understand validation failure;
7. apply or reject the change;
8. recover through the iOS 26 or deterministic fallback.

## Privacy and release matrix

| Claim | Evidence |
| --- | --- |
| On-device route is local | Provider/data-path record and network observation where relevant |
| Download route is disclosed | Model delivery/privacy review and retention policy |
| Logs are safe | Logger/signpost field audit and redacted trace |
| App Group cache is scoped | Entitlement and target ownership inspection |
| Archive is correct | Exported archive, entitlements, resources, privacy manifest, and target inspection |
| Signed device build behaves | Physical-device install and route run |
| TestFlight build behaves | Processed build selection and real route smoke test |
| App Store metadata is accurate | Review notes, privacy answers, and user-facing data-path copy |
| Fallback ships | iOS 26 or constrained-device test in the same release configuration |

## Evidence packet template

```text
feature:
target:
bundle_id:
build:
sdk:
deployment_target:
device:
os:
architecture:
model_id:
model_revision:
artifact:
artifact_digest:
tokenizer_revision:
source_or_aot:
minimum_os:
function:
input_contract:
output_contract:
cache_state:
specialization_options:
load_duration:
inference_latency:
peak_memory:
thermal_notes:
provider_capabilities:
fallback_route:
reference_fixture:
validation_result:
approval_result:
accessibility_tasks:
privacy_review:
archive_result:
testflight_result:
release_decision:
known_gaps:
```

This packet is an evidence index, not a claim that all fields are automatically available from the framework.

## Stop criteria

Mark the route blocked for release when:

- the artifact digest or license is unknown;
- function descriptors do not match the app contract;
- a claimed architecture has no matching asset;
- specialization, memory, thermal, or cancellation behavior has not been exercised;
- a model output is being treated as a domain commit without validation and approval;
- the iOS 26 fallback is only a placeholder;
- a provider’s declared capability is not backed by tests;
- accessibility is represented only by a screenshot;
- an archive or TestFlight build has not exercised the signed route.

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
- [LanguageModelCapabilities](https://developer.apple.com/documentation/foundationmodels/languagemodelcapabilities)
- [LanguageModelExecutor](https://developer.apple.com/documentation/foundationmodels/languagemodelexecutor)
- [LanguageModelExecutorGenerationRequest](https://developer.apple.com/documentation/foundationmodels/languagemodelexecutorgenerationrequest)
- [LanguageModelExecutorGenerationChannel](https://developer.apple.com/documentation/foundationmodels/languagemodelexecutorgenerationchannel)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Generative AI](https://developer.apple.com/design/human-interface-guidelines/generative-ai)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
