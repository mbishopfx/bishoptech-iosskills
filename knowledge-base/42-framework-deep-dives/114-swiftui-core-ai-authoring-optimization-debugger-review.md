# SwiftUI Core AI model-authoring, optimization, and debugger review

This page owns the upstream model-toolchain route for Core AI. It is intentionally distinct from the [Core AI on-device runtime review](113-swiftui-core-ai-on-device-model-runtime-review.md): that page begins with a model artifact and covers app loading, specialization, inference, and release; this page covers how an artifact is exported, compressed, inspected, debugged, re-authored, and compared against a reference before it enters an app.

The current Apple material describes Core AI authoring and deployment as a Python/PyTorch workflow plus a Swift runtime and developer toolchain. The Core AI framework and its custom Foundation Models bridge are documented for iOS 27 and later. Some related Metal tensor APIs are available in iOS 26. Do not collapse “Metal can represent tensors on iOS 26” into “Core AI custom-model deployment is an iOS 26 route.”

## Authoring invariant

Optimization is a search over a constrained model contract. Every change must be evaluated against the intended target and workload.

Keep these stages separate:

| Stage | Output | Evidence boundary |
| --- | --- | --- |
| Product requirement | Outcome, input sources, latency/memory/energy budgets, device matrix | Product and target decision, not model quality |
| Source model | PyTorch module, weights, tokenizer, license, reference implementation | Source ownership and reproducibility |
| Exported program | Captured graph, operations, shapes, weights | Graph capture and shape contract |
| Core AI conversion | aimodel program with named functions and metadata | Conversion structure and reference equivalence |
| Optimization | Quantized, palettized, cast, fused, or re-authored program | Measured size/performance/quality tradeoff |
| Debug artifact | Model with source mapping or intermediate/reference files | Traceability and numerical diagnosis |
| Compiled asset | AOT architecture-specific aimodelc | Toolchain and target artifact; still needs device specialization |
| Runtime | AIModel and InferenceFunction | Device load and execution |
| App proposal | App-owned typed observation or generated candidate | Source/model provenance and validation |
| Domain state | Deterministic accepted commit | Authorization, current revision, and user approval |

The model toolchain can prove that a graph converts, runs, or matches a reference within a chosen numerical threshold. It cannot prove that the app’s business interpretation is correct.

## Target-aware model plan

Before touching conversion code, write:

- target platforms and minimum OS;
- exact devices and Apple Silicon families;
- model input modalities and source formats;
- batch, sequence, and dynamic-shape ranges;
- memory and storage budget;
- cold-load and warm-load budgets;
- interactive, background, or sustained workload;
- acceptable numerical drift;
- acceptable semantic quality;
- privacy/data path;
- license and redistribution constraints;
- model update and rollback policy;
- iOS 26 fallback;
- evidence to collect for archive, TestFlight, and release.

An optimization that wins on a Mac but loses on an iPhone is not a successful iPhone optimization. A smaller artifact that misses required detections is not a successful compression change. A lower latency trace that changes the output contract is a model migration, not a transparent optimization.

## Toolchain map

The current Apple WWDC material describes this authoring flow:

    PyTorch source -> torch.export -> Core AI PyTorch Extensions -> Core AI graph/aimodel -> coreai-opt or model re-authoring -> Debugger/reference validation -> AOT or runtime specialization -> app

Supporting tools have distinct responsibilities:

| Tool or surface | Responsibility |
| --- | --- |
| Core AI PyTorch Extensions | Convert exported PyTorch programs, name inputs/outputs, assemble functions, and integrate custom lowerings or Metal kernels |
| Core AI Python runtime | Run and inspect converted models in the Python workflow when supported |
| Core AI Optimization | Config-driven compression, quantization, casting, and palettization strategies |
| Core AI models resources | Apple-hosted examples, reusable model components, Swift helpers, and skills; use as references rather than as unreviewed product dependencies |
| Core AI Debugger | Visualize graph/source structure, execute on a target, inspect intermediate tensors, and compare with reference data |
| Xcode model viewer | Inspect metadata, storage, operation distribution, and function signatures |
| Core AI debug gauge | Observe model load, specialization, and inference events during an Xcode debug session |
| Core AI instrument | Profile timing and compute activity across CPU, GPU, and Neural Engine |
| coreai-build | Produce architecture-specific AOT aimodelc artifacts |
| Metal TensorOps | Author or optimize custom tensor operations and kernels; related APIs have their own iOS 26/27 availability |

Do not use a tool’s name as a quality claim. Record the exact version, target, input fixture, and result.

## Export with an explicit graph contract

### PyTorch export is the boundary

The WWDC26 integration material shows using torch.export to capture a program with weights, operations, and shapes. The exported program is the input to the Core AI converter.

At export time, record:

- example input values and their digest;
- input names and output names;
- shape constraints and dynamic dimensions;
- decomposition table or custom lowering configuration;
- training/evaluation mode;
- random seeds where relevant;
- precision and device used for the reference run;
- model and dependency versions;
- debug metadata configuration;
- warnings or unsupported operations.

An exported graph is not automatically an app-ready artifact. It may capture the wrong input layout, omit a dynamic-shape bound, or expose an output whose semantics the app has not defined.

### Core AI converter

Core AI’s TorchConverter can take the exported program and produce a Core AI program with named inputs and outputs. Use stable names that match the app contract. When a model has multiple independently useful stages, consider multiple named functions in one artifact only when the lifecycle and compression policy remain understandable.

Good function boundaries are product meaningful:

- image_encode;
- text_encode;
- detect;
- embed;
- decode;
- classify.

Do not split a graph merely to make a catalog look impressive. Splitting changes memory residency, synchronization, intermediate formats, update semantics, and validation fixtures.

### Dynamic shapes

Dynamic dimensions let a model handle a range of input sizes, but they affect specialization, output allocation, caching, and testing. Define minimum, typical, maximum, and invalid shapes. If a decoder grows one token at a time, measure repeated-shape specialization and consider stateful caches or the expected-frequent-reshape option at the runtime layer.

Use static shapes or a narrow shape range when a target such as iPhone benefits from predictable memory and hardware mapping. This is a model design choice, not a cosmetic compiler flag.

## Conversion correctness

### Baseline before compression

Create a baseline aimodel before changing precision or topology. Run:

1. original PyTorch reference;
2. exported program reference;
3. uncompressed Core AI model;
4. the same input fixtures across each;
5. intermediate and final comparison;
6. app-level semantic checks.

If the uncompressed conversion already diverges, do not debug quantization first. Fix export, decomposition, unsupported operation handling, input preprocessing, or output postprocessing.

### Reference intermediates

The current Core AI Debugger documentation describes an aimodelintermediates file containing intermediate tensor values from a PyTorch reference run. The save_intermediates API can produce this artifact for comparison. Preserve:

- source model identifier;
- Core AI artifact identifier;
- fixture digest;
- input preprocessing;
- source and target compute settings;
- operation mapping;
- tolerance and similarity metric;
- whether the comparison is baseline, quantized, palettized, AOT, or re-authored.

Reference files can be large and may contain sensitive data. Store them in controlled development artifacts, not in a production app bundle or public log.

### Numerical versus semantic validation

Use debugger similarity scores and tensor differences to find where a conversion or optimization diverges. Then run domain fixtures:

- image masks against labeled fixtures;
- OCR or barcode output against known text;
- ranking or embedding behavior against a frozen benchmark set;
- generated text against structured-output and safety criteria;
- audio or speech output against a reviewed corpus;
- action proposals against authorization and revision rules.

PSNR, absolute difference, or tensor similarity is not a semantic acceptance criterion by itself.

## Compression and optimization

### Config-driven optimization

The current WWDC26 authoring session describes Core AI Optimization, commonly surfaced through coreai-opt, as a config-driven model-compression library. A configuration states what to compress and what to leave alone, and can differ by target platform.

Keep a versioned optimization configuration with:

- target platform and device class;
- weight versus activation policy;
- precision per module or layer;
- granularity such as per-channel or block;
- symmetric or asymmetric behavior;
- calibration data and preprocessing;
- quantization-aware training choice;
- palettization or lookup-table configuration;
- layers explicitly excluded;
- expected size, latency, memory, and quality thresholds.

The configuration is part of the model artifact identity. Changing it without changing the model revision makes debugging and rollback ambiguous.

### Quantization

The current Apple material describes int4, int8, FP4, and FP8 weight-compression choices with flexible granularity, plus quantization APIs that can use a small calibration set or larger quantization-aware training data. The correct choice depends on the model and target.

Review quantization in this order:

1. preserve a full-precision baseline;
2. quantize one module family or a safe preset;
3. compare tensor divergence by operation;
4. identify sensitive modules;
5. exclude or use higher precision for sensitive sections;
6. compare full-task quality;
7. measure cold/warm load, peak memory, latency, and thermal behavior;
8. select the smallest artifact that still meets the product contract.

Uniform aggressive compression is a useful experiment, not a default shipping policy. A model can shrink substantially and still fail the actual feature.

### Calibration data

Calibration data is part of the optimization contract. Record:

- sample count and source;
- privacy and license;
- preprocessing and normalization;
- representative device/task distribution;
- outlier handling;
- random seed and tool version;
- excluded data and rationale.

Do not use a tiny convenient sample to claim broad quality. Do not ship calibration data or reference tensors with personal content.

### Palettization

Palettization replaces values with a lookup table and indices. It can be valuable for specific weight distributions and target power/memory constraints. It can also degrade sensitive layers.

When using a KMeans-style palettizer:

- record cluster count and granularity;
- keep scales and layout explicit;
- compare per-layer divergence;
- exclude layers that show unacceptable semantic drift;
- measure dequantization and hardware support;
- test the final device route.

Never present “4-bit” as a single performance number. The layout, scale representation, supported hardware, model topology, and workload all matter.

### Precision casting and layout

The WWDC26 authoring material describes casting exported programs to half precision when useful. It also shows target-specific re-authoring patterns such as static shapes, channels-first layouts, convolutional projections, and independently compressible functions for iOS.

These changes can alter:

- graph operation selection;
- memory layout and copies;
- numerical range;
- shader or hardware primitive selection;
- function boundaries;
- input/output contract;
- cache reuse.

Treat a re-authored model as a new implementation with module-level and end-to-end tests. Keep the original reference model available.

## Stateful and multi-function authoring

### Key-value cache and state

The WWDC26 Core AI session demonstrates that a transformer decoder can slow down as sequence length grows because it recomputes key and value embeddings. Adding key/value caches as state inputs lets the model update buffers in place and avoid replaying the entire history.

Stateful authoring needs:

- initial state creation;
- state reset semantics;
- maximum sequence or cache size;
- concurrent-request ownership;
- cancellation behavior;
- cache invalidation on model/revision change;
- serialization policy if a session is restored;
- exact output equivalence tests for reset and continuation.

A mutable state buffer is not a transcript and does not provide persistence or privacy by itself.

### Multiple functions in one artifact

Use multiple functions when the feature naturally reuses stages at different cadences. An image encoder can run once while prompts or detection stages change. This can improve power and latency, but it introduces:

- shared intermediate contract;
- function-specific compression;
- ordering and synchronization;
- resource lifetime;
- version compatibility;
- partial-update recovery;
- distinct proof fixtures.

The app still needs to validate every function descriptor at runtime.

## Core AI Debugger workflow

### Visualize

Open the aimodel in Core AI Debugger to inspect:

- module hierarchy;
- operation graph;
- data dependencies;
- source mapping to Python where debug metadata exists;
- operation inputs and outputs;
- model structure and metadata.

If source mapping is unavailable, record that limitation. A graph without source mapping can still show structure, but it cannot point directly back to the authoring line.

### Execute

Choose a Mac or paired device, function, compute units, and inputs. The Debugger specializes the model for the selected target and exposes intermediate tensor outputs. This is device execution evidence for that target, not universal platform coverage.

Record:

- selected target;
- OS and architecture;
- function;
- compute units;
- input fixture;
- specialization result;
- output tensor snapshots;
- errors and unsupported operations.

### Validate

Load reference intermediates or another comparison configuration. Use operation-level sync points and tensor differences to locate drift. Compare the final task output afterward.

The correct debugging loop is:

    symptom -> operation divergence -> source/optimization choice -> revised artifact -> reference comparison -> target execution -> task fixture

Do not use one final output image to guess which layer caused a mismatch when operation-level evidence is available.

## Debug gauge and Instruments

The Core AI debug gauge is the first runtime feedback surface inside Xcode. Use it to answer:

- did the model load when expected;
- did specialization happen during an interactive moment;
- did a function reload repeatedly;
- did inference events appear at the expected cadence;
- which event should be opened in a deeper tool.

Use the Core AI instrument for:

- load and specialization timing;
- inference duration and cadence;
- CPU/GPU/Neural Engine activity;
- repeated work or growing latency;
- memory and scheduling hypotheses;
- source versus AOT comparison.

The instrument reports runtime behavior. It does not establish semantic quality, privacy, or user approval.

## Custom Metal kernels and TensorOps

### Use custom kernels only for a demonstrated bottleneck

Core AI’s authoring material describes embedding a custom Metal Shading Language kernel in an aimodel by supplying:

- a PyTorch reference function;
- MSL source;
- input and output names;
- output shape information for dynamic inputs;
- a TorchMetalKernel registration;
- a TorchConverter integration.

The MSL travels with the model asset. That makes the kernel part of the model’s supply chain and release artifact, not an ephemeral app shader.

Before using a custom kernel, prove that:

- the default Core AI graph is insufficient;
- the reference function and MSL agree on shapes, types, and edge cases;
- the kernel is available on every claimed target;
- input/output layouts are explicit;
- error and fallback paths exist;
- the kernel stays within memory and thermal budgets;
- the debugger can inspect the resulting graph or a suitable reference exists;
- the archive contains the intended embedded source/compiled representation.

### Metal tensor route

Metal’s tensor APIs have their own lifecycle. MTLTensor represents a multidimensional resource, MTLTensorDataType defines data formats, and TensorOps can work with quantized values, multi-plane tensors, cooperative tensors, matrix multiplication, reductions, and other operations.

The current Metal documentation and WWDC material distinguish iOS 26 support for some tensor data types from newer iOS 27 quantized and scale-plane features. Query device support and guard the feature. A Core AI custom-kernel integration is a separate target gate.

Do not confuse:

- a Metal tensor allocation with a Core AI InferenceValue;
- a Metal TensorOps shader with a model conversion;
- an MTLTensor feature flag with a complete model route;
- a GPU correctness trace with semantic task quality.

### Model re-authoring

Re-authoring changes the PyTorch implementation to fit target hardware. Examples from Apple’s material include operation fusion, use of optimized primitives, static shapes, channels-first layouts, convolutional projections, stateful caches, and splitting a model into independent functions.

Re-authoring requires:

- a retained source/reference implementation;
- module tests;
- conversion tests;
- per-function fixtures;
- full-task equivalence or explicitly accepted quality changes;
- target-device performance and thermal traces;
- an update and rollback plan.

## Artifact identity and supply chain

An optimized artifact should carry or be accompanied by:

- model identifier and revision;
- source commit or source release;
- author/license;
- conversion and optimization tool versions;
- optimization configuration digest;
- reference fixture digest;
- debug metadata status;
- target platform/minimum OS;
- function names and contracts;
- tokenizer or companion resource revisions;
- AOT compiler version and architecture list;
- artifact digest and signature status;
- known numerical drift and quality gaps.

Do not put credentials, private data, raw calibration samples, or unreviewed prompts in model metadata. Treat a custom Metal source string as source code subject to licensing and security review.

## iOS 26 fallback and release split

The authoring tools in this route target Core AI’s later OS path. For an iOS 26 product:

- keep the Core AI authoring pipeline in a later target/toolchain;
- retain a supported Core ML, Metal, Vision, Foundation Models, or deterministic fallback;
- test the fallback as a complete user journey;
- do not claim identical model behavior;
- make the model/data path and availability state visible when useful.

The [runtime review](113-swiftui-core-ai-on-device-model-runtime-review.md) owns loading and release integration. This page owns how the artifact earns the right to be loaded.

## Native design and accessibility for toolchain-facing apps

If you build a developer-facing model inspector or in-app diagnostics view, use native SwiftUI hierarchy:

- model revision and target at the top;
- source/optimized/reference comparison as explicit tabs or sections;
- tensor/graph details behind disclosure;
- progress and error states with standard controls;
- a clear distinction between numerical drift and task quality;
- export actions that explain privacy and file contents.

Liquid Glass can group a small control cluster, but it should not make a debugger look like a consumer AI oracle. Large tensor tables and graph views need nonvisual summaries, keyboard/pointer navigation, Dynamic Type strategy, contrast, and reduced-motion behavior.

## Release proof for an authored model

Before distributing an optimized Core AI artifact:

1. freeze source and tool versions;
2. export the baseline and candidate with reproducible manifests;
3. inspect function contracts and metadata;
4. run reference and debugger comparisons;
5. record target-specific model size, memory, latency, and thermal results;
6. inspect custom Metal and companion resources;
7. compile AOT assets when required and test the architecture selection;
8. load the final artifact in the signed physical-device build;
9. exercise the iOS 26 fallback;
10. run accessibility and privacy review;
11. inspect archive contents and entitlements;
12. run the processed TestFlight build;
13. preserve the prior accepted model for rollback;
14. record unresolved drift or device gaps.

## Stop conditions

Stop optimization when:

- the source model, license, or reference inputs are not reproducible;
- a compressed artifact has no baseline comparison;
- an optimization changes the input/output contract without a migration;
- a debugger similarity score is presented as semantic truth;
- a custom kernel has no device support or fallback plan;
- a Metal tensor capability is assumed from an unverified device;
- memory/thermal behavior is unknown;
- debug metadata or reference artifacts contain sensitive data without a retention plan;
- the iOS 26 route is missing;
- the signed physical-device and release artifacts have not run the final model.

## Sources

- [Core AI](https://developer.apple.com/documentation/coreai)
- [Core AI for developers](https://developer.apple.com/core-ai/)
- [Core AI Debugger](https://developer.apple.com/documentation/coreai/inspecting-core-ai-models-with-core-ai-debugger)
- [Inspecting, debugging, and profiling Core AI models](https://developer.apple.com/documentation/coreai/inspecting-debugging-and-profiling-core-ai-models)
- [Inspecting Core AI models with Core AI Debugger](https://developer.apple.com/documentation/coreai/inspecting-core-ai-models-with-core-ai-debugger)
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
