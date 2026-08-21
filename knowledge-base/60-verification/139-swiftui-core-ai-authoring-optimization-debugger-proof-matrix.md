# SwiftUI Core AI authoring, optimization, and debugger proof matrix

This matrix defines the evidence required before an authored or optimized Core AI model is treated as a production capability. It pairs with the [Core AI authoring and optimization review](../42-framework-deep-dives/114-swiftui-core-ai-authoring-optimization-debugger-review.md), the [authoring and optimization design review](../21-design-deep-dives/142-swiftui-core-ai-authoring-optimization-debugger-review-design.md), the [authoring and optimization route](../50-capability-recipes/145-swiftui-core-ai-authoring-optimization-debugger-review-route.md), and the [Core AI model-runtime proof matrix](138-swiftui-core-ai-on-device-model-runtime-proof-matrix.md).

Core AI authoring is a toolchain claim as well as an app-runtime claim. A converted, compressed, palettized, or custom-kernel artifact must be traceable to its source, reproducible settings, target device, reference run, and signed app build. The debugger can show graph structure and numerical divergence; it does not by itself prove semantic quality, accessibility, privacy, or release readiness.

## Evidence vocabulary

| Evidence | Proves | Does not prove |
| --- | --- | --- |
| Source and license manifest | The input model, code, license, and revision are identified | That the source is accurate, safe, or compatible with an Apple target |
| Export graph record | The exported program and named inputs/outputs are reproducible | That conversion preserves behavior |
| Converter log | A named toolchain produced an aimodel artifact | That the artifact runs on every claimed device |
| Model viewer or AIModelAsset inspection | Functions, metadata, storage, and contracts are inspectable | Runtime readiness or domain correctness |
| Reference output/intermediate file | A baseline exists for comparison | That the baseline is a good product outcome |
| Core AI Debugger comparison | Numerical differences can be localized and measured | User-facing quality or authorization to commit a result |
| Optimization config | The compression, precision, layout, and exclusions are intentional | That the tradeoff is acceptable |
| AOT output | Target-specific compiled assets were emitted by a recorded toolchain | That the device selected the correct asset at runtime |
| Custom Metal source | A custom operation has a reference implementation and Metal implementation | That it is faster, numerically equivalent, or supported on every target |
| Debug gauge/Instruments trace | Load, specialization, compute, memory, and timing behavior for a workload | General performance across all devices |
| Physical-device run | The signed app exercised the route on a named device and OS | Universal device coverage or App Store approval |
| Archive/TestFlight inspection | The distributed artifact contains the intended targets and resources | Production traffic or domain truth |

Do not use a successful Python conversion, a Mac-only debugger run, a simulator screenshot, or an impressive generated answer as a substitute for the evidence type it does not provide.

## Environment and provenance record

Capture this record before changing authoring settings:

- app, target, bundle identifier, and feature flag;
- source revision, branch/commit, model revision, tokenizer, and companion resources;
- Python, PyTorch, Core AI Python package, Metal Toolchain, Xcode, macOS, and SDK versions;
- export command/configuration and every converter or optimizer option;
- source artifact, intermediate artifact, final aimodel, and AOT output digests;
- license, attribution, dataset or checkpoint provenance, and redistribution decision;
- intended minimum OS, architectures, compute policy, and device classes;
- reference fixture digest, expected outputs, tolerances, and known nondeterminism;
- model-data retention and deletion policy for debug artifacts;
- reviewer, date, and decision for every optimization candidate.

## Authoring and export matrix

| Claim | Test | Required record | Pass condition |
| --- | --- | --- | --- |
| Export is reproducible | Run from a clean environment | Dependency lock, command, source digest | Same named graph and compatible digest/metadata policy |
| Input names are stable | Inspect exported signatures | Names, dtypes, ranks, shapes, dynamic bounds | App preprocessing maps to the recorded contract |
| Output names are stable | Inspect every function | Output names, dtypes, ranks, postprocessing | App result mapper has no positional guesswork |
| Dynamic dimensions are bounded | Exercise minimum, normal, maximum, invalid values | Shape constraints and fixture results | Invalid input is rejected before inference |
| Functions are intentional | Inspect multi-function artifact | Function list and purpose | Each function has a caller, budget, and acceptance fixture |
| Stateful data is explicit | Reset and continuation runs | State names, shape, lifetime, reset semantics | No hidden state crosses a user/session boundary |
| Custom operations are mapped | Compare reference and Metal implementation | Operator name, source mapping, inputs/outputs, device gate | The op is visible in the graph and has a fallback or supported-target policy |
| Model metadata is sufficient | Inspect source and converted artifact | Revision, preprocessing, license, target, tool versions | Release can identify what was shipped |

## Baseline conversion matrix

| Claim | Test | Evidence | Pass condition |
| --- | --- | --- | --- |
| Baseline conversion works | Convert without optimization | Converter log and artifact digest | Artifact is readable and structurally inspectable |
| Conversion preserves contracts | Compare source/exported/converted signatures | Contract snapshots | No unreviewed name, type, rank, or shape changes |
| Baseline output is comparable | Run identical fixtures | Output and intermediate files | Reference run and converted run use the same fixture and preprocessing |
| Divergence is explainable | Compare final and intermediate values | Debugger similarity/diff and source mapping | Differences are below threshold or have a documented decision |
| Nondeterminism is known | Repeat baseline runs | Seed, device, tolerance, and repeated outputs | Threshold accounts for known nondeterminism rather than hiding it |
| Quantization has a baseline | Save uncompressed candidate first | Baseline digest and metrics | Every optimized candidate points to the exact baseline |

## Optimization and compression matrix

| Candidate | Required comparison | Required product check | Stop condition |
| --- | --- | --- | --- |
| Weight compression | Size, intermediate/output difference, load time | Task accuracy and memory budget | A regression has no layer-level explanation or approved threshold |
| Quantization | Dtype/scale metadata, numerical drift, device performance | Task quality across representative fixtures | Calibration data is missing, unrepresentative, or sensitive without approval |
| Quantization-aware training | Training recipe, checkpoint, export comparison | Quality versus post-training candidate | Training provenance or evaluation split is unknown |
| Palettization | Palette/bit setting, error map, model size | Quality and cold/warm behavior on target hardware | Candidate is chosen only because the file is smaller |
| Precision/layout change | Input/output and intermediate comparison | Device execution and memory/latency | A layout assumption is not reflected in the contract |
| Layer exclusion | Explicit excluded modules and rationale | Quality, size, and runtime impact | A sensitive or fragile module is compressed without a fixture |
| Stateful/KV-cache change | Reset/continuation and sequence-length comparison | Long-session memory and cancellation | Cached state can leak across request, user, or account boundaries |
| Multi-function split | Per-function contract, size, load, and task quality | Correct function selection and fallback | The app chooses by string or position without a manifest |

Every optimization record should answer: what changed, why it changed, which baseline it was compared with, what got better, what got worse, which device saw the change, and who accepted the tradeoff.

## Core AI Debugger matrix

| Debugger task | Evidence to retain | Pass condition |
| --- | --- | --- |
| Visualize graph | Graph export/screenshot plus text summary | Every important function and custom op has an understandable name |
| Inspect source mapping | Node/module/source mapping record | A divergence can be traced back to an authored or lowered stage |
| Execute on Mac | Run ID, environment, fixture, output | The toolchain can execute the intended function with the recorded fixture |
| Execute on paired device | Device/OS/build/model record | The target device can load and run the selected artifact |
| Compare reference output | Final diff, similarity metric, threshold | Candidate is numerically within the chosen policy or is rejected |
| Compare intermediates | Sync-point list and layer-level diff | A final-output difference is localized where possible |
| Inspect custom kernel | Source, input/output descriptors, shape policy | Kernel mapping is reviewable and has a target/fallback decision |
| Re-run after optimization | New run linked to baseline and config | Results are attributable to one candidate configuration |
| Redact artifacts | Retention and access review | Debug files do not expose unapproved user data or secrets |

Debugger similarity scores must not be copied into customer copy as if they were accuracy, safety, or factuality guarantees.

## Custom Metal and tensor matrix

| Claim | Test | Evidence |
| --- | --- | --- |
| Tensor contract is correct | Validate rank, dimensions, dtype, layout, and planes | Descriptor snapshot and fixture |
| Reference implementation exists | Run the PyTorch/reference operator | Reference output and source revision |
| Metal implementation exists | Compile and run the MSL operation | Metal source, compiler result, target OS gate |
| Dynamic shapes are handled | Run supported shape set | Shape function or explicit bounds and outputs |
| Quantized planes are handled | Exercise scale/zero-point or auxiliary planes | Plane metadata and numerical comparison |
| Custom op is integrated | Inspect graph and execute converted model | Function/model mapping and debugger trace |
| Performance is justified | Same workload/reference on same device | Median/p95, memory, thermal, and correctness evidence |
| Unsupported target is safe | Run on a device without the feature | Deterministic fallback or clear unavailable state |

Do not infer support from a simulator or from a different Metal tensor datatype. Record the minimum OS and device matrix for every tensor type, cooperative-tensor path, and custom kernel.

## AOT, packaging, and target selection matrix

| Claim | Test | Evidence | Pass condition |
| --- | --- | --- | --- |
| Source artifact is deliverable | Inspect app/resource package | Bundle path, size, digest, license | Intended artifact is owned by the correct target |
| AOT build is reproducible | Run the recorded AOT command | Toolchain, flags, output digest | Output matches the manifest policy |
| Architecture outputs exist | Inspect compiled artifacts | Architecture/minimum-OS list | Each claimed device has a compatible asset |
| Device selection is correct | Run on each architecture class | Selected asset log and device record | No accidental source fallback or wrong-architecture choice |
| Downloaded model is verified | Transfer, verify, install, restart offline | URL/version/digest/install record | Unverified content is never activated |
| Update is recoverable | Install candidate, fail activation, roll back | Old/new activation state | Prior accepted revision remains runnable |
| Archive contains the route | Inspect archive and entitlements | Resources, target membership, privacy, signing | Signed archive matches the tested source revision |

## Performance, memory, and thermal matrix

Measure the same model, fixture, device state, and app configuration for each candidate:

- source cold-load and warm-load time;
- specialization or compilation time, including first interactive request;
- median and p95/p99 inference latency;
- peak process memory and model/cache/function memory where available;
- CPU/GPU/Neural Engine activity and custom-kernel timing;
- frame time and main-actor responsiveness for live SwiftUI routes;
- sustained workload, thermal state, battery impact, and cancellation;
- artifact size, download time, install storage, and update cost.

The pass condition must name the device class and workload. A Mac measurement is not an iPhone claim, and a single successful run is not a sustained-thermal result.

## App contract and SwiftUI proof matrix

| Claim | Evidence | Pass condition |
| --- | --- | --- |
| Preparation is honest | UI test and physical-device run | UI distinguishes source load, specialization, inference, and failure |
| Candidate provenance is visible | Review screen/accessibility output | Person can identify model revision, function, and source |
| Model output is a proposal | Apply/reject fixture | Validation and user approval precede domain mutation |
| Numerical drift is not hidden | Comparison/detail state | Debug or review copy exposes candidate status without false certainty |
| Failure is recoverable | Forced load, conversion, memory, and cancellation failures | Draft/source survives and the next action is clear |
| Liquid Glass remains functional | Contrast, transparency, motion, and size-class variants | Controls remain legible, reachable, and appropriately grouped |
| Fallback is complete | iOS 26/constrained-device run | The product journey is usable without a placeholder screen |

## Accessibility tasks

Test VoiceOver, Dynamic Type, increased contrast, reduced transparency, reduced motion, keyboard navigation, Full Keyboard Access, Switch Control, pointer input, and color-independent status. Record task completion and spoken labels rather than relying on screenshots.

1. Choose a model or source and understand its revision.
2. Start preparation, conversion, or inference and understand progress.
3. Cancel an in-flight operation and recover the draft.
4. Inspect a validation warning or numerical-drift explanation.
5. Review provenance and the proposed result.
6. Apply, reject, undo, or retry with an alternate route.
7. Reach the iOS 26 or deterministic fallback.

## Privacy, supply chain, and release matrix

| Claim | Required evidence |
| --- | --- |
| Source/license is cleared | License, attribution, model card/provenance, redistribution decision |
| Debug artifacts are safe | Input fixture classification, redaction, retention, access log |
| On-device path is accurately described | Provider/data-path record and network observation when relevant |
| Download/update path is safe | HTTPS/version/digest verification, activation and rollback record |
| Logs do not leak content | Logger/signpost field audit and redacted sample |
| Signed build contains intended artifacts | Archive contents, entitlements, target membership, privacy manifest |
| TestFlight build exercises final route | Processed build identifier, device run, route result |
| Metadata and review notes are accurate | Data-path copy, capability claims, fallback and device limitations |

## Evidence packet

~~~text
feature:
target:
bundle_id:
source_revision:
model_revision:
source_artifact_digest:
converted_artifact_digest:
optimized_artifact_digest:
aot_artifact_digests:
license_and_provenance:
python_toolchain:
xcode_sdk_macos:
minimum_os:
device_matrix:
function_contracts:
reference_fixture_digest:
reference_run:
optimization_config:
debugger_run:
custom_metal_commit:
load_specialization_latency:
inference_latency_p50_p95:
peak_memory:
thermal_notes:
fallback_route:
swiftui_review:
accessibility_tasks:
privacy_review:
archive_result:
testflight_result:
rollback_result:
release_decision:
known_gaps:
~~~

## Stop criteria

Block release when:

- source, license, toolchain, or artifact digest cannot be reproduced;
- the exported or converted contract differs without an explicit migration;
- an optimized candidate lacks a baseline and representative fixtures;
- Debugger similarity is being presented as semantic or domain truth;
- a custom kernel lacks a reference comparison, device gate, or fallback;
- a claimed device class lacks physical-device execution and performance evidence;
- memory, thermal, cancellation, or update/rollback behavior is unknown;
- debug/reference artifacts contain sensitive data without an approved retention policy;
- the signed archive or processed TestFlight build has not run the final route;
- the SwiftUI route treats model output as a committed action without validation and approval;
- accessibility is represented only by screenshots;
- the iOS 26 fallback is missing, incomplete, or only a placeholder.

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
