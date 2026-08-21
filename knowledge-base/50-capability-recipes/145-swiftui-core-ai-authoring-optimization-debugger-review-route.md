# SwiftUI Core AI authoring, optimization, and debugger review route

This route turns the [Core AI authoring review](../42-framework-deep-dives/114-swiftui-core-ai-authoring-optimization-debugger-review.md) into a repeatable model-toolchain workflow. It complements the [Core AI runtime route](144-swiftui-core-ai-on-device-model-runtime-review-route.md): authoring earns an artifact; the runtime route proves that the app can load and use it.

## 1. Freeze the product and target contract

Write a short target record before conversion:

| Field | Record |
| --- | --- |
| Outcome | What the user can accomplish |
| Model task | Text, vision, audio, embedding, generation, or pipeline |
| Source | Model repository/release, author, license, commit |
| Targets | iOS 26 fallback, iOS 27 Core AI, macOS/paired debugger targets |
| Inputs | Names, shape ranges, layout, type, preprocessing |
| Outputs | Names, type, shape, postprocessing, semantic interpretation |
| Budget | Storage, memory, cold load, warm latency, sustained/thermal |
| Quality | Numerical and task-level acceptance criteria |
| Privacy | Source, calibration, reference, logging, and delivery policy |
| Update | Revision, cache, rollback, migration |

If the product does not have an iOS 26 fallback, stop and choose whether the app’s minimum OS should move or the feature should use another framework.

## 2. Select the authoring depth

Use the narrowest authoring depth that satisfies the constraint:

1. direct conversion of an exported PyTorch model;
2. config-driven compression or quantization;
3. selective layer exclusion or higher precision;
4. stateful cache or multi-function split;
5. operation fusion or a provided optimized primitive;
6. custom Metal kernel;
7. full model re-authoring for a target.

Move down this list only when measured evidence shows that the preceding route cannot meet the contract. Every deeper route increases debugging, packaging, device support, and release responsibility.

## 3. Prepare a reproducible Python workspace

Record:

- Python version and environment lock;
- PyTorch version;
- Core AI Python and PyTorch Extension versions;
- optimization package version;
- model source commit and license;
- conversion script revision;
- sample input fixture and digest;
- output naming and shape policy;
- random seed and evaluation mode;
- target platform settings.

Do not run a generated command against production model assets without reviewing its inputs, output path, license, and target flags.

## 4. Export the baseline program

The baseline route is:

    trained model -> evaluation mode -> wrapper with stable interface -> torch.export -> Core AI decomposition table -> TorchConverter -> named aimodel

The wrapper should make all app-relevant inputs and outputs explicit. If the source model has hidden global state, random behavior, implicit image preprocessing, or dynamic control flow, make the behavior visible in the wrapper and fixtures.

Before optimization, retain:

- the source model output;
- the exported program output;
- the uncompressed Core AI output;
- the function descriptor;
- the input/output fixture and digest;
- conversion warnings.

## 5. Name functions and values

Use stable names that are meaningful in both Python and Swift. Avoid names such as input0 or output1 when a domain name is available.

For each function, record:

- name;
- input names;
- output names;
- state names;
- scalar/image/tensor type;
- static/dynamic dimensions;
- layout and orientation;
- optional description;
- app-owned interpretation.

The runtime must compare this contract before loading. A renamed output is a model migration even when the tensor values are identical.

## 6. Create the first reference run

Run the original source model on controlled fixtures. Capture:

- final outputs;
- intermediate tensors when debugger comparison is planned;
- preprocessing metadata;
- source/model revision;
- target-independent reference environment;
- privacy classification and retention.

Use the save_intermediates flow described in Apple’s Core AI Debugger documentation when intermediate comparison is needed. Keep reference artifacts outside the app bundle unless the product explicitly needs them and the data is safe.

## 7. Convert and compare before compressing

Create the uncompressed aimodel. Open it in the Core AI Debugger or Xcode model viewer and verify:

- model asset is valid;
- functions exist;
- input/output names match;
- dynamic dimensions are bounded;
- metadata is accurate;
- storage and compute types are expected;
- source mapping is available if required.

Run a reference comparison. If divergence is present before optimization, investigate export, decomposition, preprocessing, unsupported operations, or output postprocessing. Do not blame quantization until the baseline conversion is understood.

## 8. Add compression as a candidate

Create a candidate optimization config with:

- target platform;
- selected modules/layers;
- weight precision;
- activation precision;
- quantization granularity;
- calibration or QAT data;
- palettization settings;
- exclusions;
- expected output contract.

Give the candidate a new revision. Do not overwrite the baseline.

## 9. Evaluate quantization and palettization

Compare candidate and baseline in this order:

1. artifact size;
2. model metadata and function contract;
3. operation-level numerical divergence;
4. final output similarity;
5. task-level quality fixtures;
6. cold-load and warm-load timing;
7. peak memory and allocation behavior;
8. sustained latency and thermal behavior;
9. iOS 26 fallback and user-visible result.

If a candidate fails one of these, keep the evidence with the rejected revision. That history helps identify sensitive layers and prevents repeating the same experiment.

## 10. Use the debugger to localize drift

When a candidate fails:

- open the candidate and baseline/reference in Debugger;
- inspect the navigator and module hierarchy;
- select the first meaningful sync-point divergence;
- inspect input/output tensors and data types;
- map to source when debug metadata exists;
- compare the optimization config for that module;
- exclude or raise precision for the sensitive section;
- re-export a new revision;
- repeat the comparison.

The debugger is a diagnosis loop, not an automatic optimization oracle.

## 11. Choose target-specific compression

Do not optimize one configuration for every Apple platform by default. Create target profiles such as:

| Profile | Design concern |
| --- | --- |
| iOS compact | Memory, battery, first use, thermal, static or narrow shapes |
| iPad | Larger screen and possibly larger memory, still mobile thermals |
| Mac | Throughput and broad device range, but package/storage still matter |
| visionOS | Spatial workload and user attention, device support must be verified |

Each profile should have its own model revision, evidence, and fallback behavior unless the artifacts are proven equivalent.

## 12. Author stateful caches when sequence cost is the bottleneck

If Instruments shows inference growing with sequence length, consider a stateful key-value cache or equivalent state design. The route is:

    baseline decoder -> add state inputs/outputs in source -> export state contract -> convert -> compare reset/continuation -> load MutableViews -> profile sustained decode

Test:

- first token/first step;
- continuation;
- reset;
- maximum cache length;
- cancellation;
- concurrent session isolation;
- model revision invalidation;
- memory usage.

Do not share mutable state between user sessions without an explicit ownership model.

## 13. Split a model into multiple functions when cadence differs

Use a multi-function artifact when one stage can be reused at a different cadence, such as image encoding once and prompt/detection multiple times.

For each function:

- define independent compression policy;
- define input/output and intermediate contract;
- define resource lifetime;
- define update compatibility;
- define function-level fixtures;
- define the sequence and failure behavior.

The runtime should load each function intentionally and avoid keeping every large function resident when the feature does not need it.

## 14. Add a custom Metal kernel only after profiling

The custom-kernel route is:

1. identify a measured bottleneck;
2. preserve a PyTorch reference implementation;
3. write MSL with explicit data types, layouts, bounds, and thread geometry;
4. define output shapes for dynamic inputs;
5. register the TorchMetalKernel with the converter;
6. embed the source in a new model revision;
7. compare reference and converted numerics;
8. run the kernel on every claimed device class;
9. profile against the default implementation;
10. document fallback and release packaging.

The kernel is a model artifact dependency. It is not enough that it runs in a standalone Metal sample.

## 15. Use Metal tensors separately when the app owns the GPU pipeline

Metal MTLTensor and TensorOps can be useful for custom GPU work and quantized operations. Use that route when the app owns a Metal pipeline or needs custom operations around model work.

Before using it:

- check the target OS and feature set;
- inspect data type and auxiliary-plane support;
- define tensor dimensions, strides, and layout;
- plan buffer ownership and command synchronization;
- compare quantized output with a reference;
- measure GPU occupancy, memory, and thermal behavior;
- decide whether the work belongs in Core AI, Core ML, Metal, or a combination.

Do not use a Metal tensor API as a substitute for Core AI’s model artifact or runtime contract.

## 16. Package the model artifact

Create a package record with:

- aimodel or resource-folder path;
- tokenizer and companion resources;
- AOT variants and architecture names;
- manifest and digest;
- license/author/source;
- model and optimization revision;
- minimum platform/OS;
- debug/reference artifacts kept outside production;
- app target and extension ownership;
- rollback revision.

For a custom Foundation Models provider, the provider package has its own Swift Package Manager dependency and platform requirements. Keep the package’s model resources and executor versioned together.

## 17. Prepare AOT variants

Use the recorded coreai-build version and target flags to produce aimodelc assets. Confirm:

- output per architecture;
- minimum deployment version;
- compute preference;
- source model revision;
- artifact digest;
- remote delivery manifest if using Background Assets.

The AOT output reduces compilation work but still needs device specialization. Test at least one physical device for each claimed architecture family.

## 18. Device execution route

Run the final candidate in Core AI Debugger on a paired supported device, then in the signed app:

- select the intended function;
- use the same fixture;
- record specialization and load time;
- record compute units;
- inspect output and intermediate values;
- record memory and latency;
- exercise cancellation and background/foreground transitions;
- compare with the baseline/reference;
- run the app-level validation and approval flow.

A Debugger device run is strong execution evidence, but it is still not App Store or domain-truth evidence.

## 19. Profile the right layer

Use the tool that answers the question:

| Question | Tool |
| --- | --- |
| Is the graph structurally what I intended? | Xcode model viewer or Core AI Debugger |
| Where did numerics diverge? | Core AI Debugger/reference comparison |
| Did specialization happen during a tap? | Xcode debug gauge |
| Which compute unit or stage is slow? | Core AI instrument |
| Is a custom kernel faster? | Instrument comparison on same device/workload |
| Is the app blocked? | Swift concurrency/UI responsiveness tools and physical run |
| Is the result semantically useful? | App-owned task fixtures and review |
| Can the signed build ship? | Archive/TestFlight/device proof |

Never cite the wrong layer as evidence.

## 20. Design the release and rollback gate

Release gate:

1. source/model license and provenance approved;
2. baseline and candidate reproducible;
3. reference comparison passed;
4. task-level quality passed;
5. target size/memory/latency/thermal passed;
6. AOT/package resources match manifest;
7. iOS 26 fallback passed;
8. signed physical-device route passed;
9. accessibility/privacy review passed;
10. archive and TestFlight artifact inspected;
11. prior accepted revision retained for rollback.

If a later model revision changes quality or requires a new target, ship it as a deliberate model update, not an invisible asset replacement.

## 21. Evidence handoff to the app team

Give the runtime implementer:

- manifest and digest;
- function descriptor snapshot;
- input preprocessing contract;
- output postprocessing contract;
- state/reset contract;
- model capability claims;
- device/OS matrix;
- memory/thermal/latency budgets;
- reference fixture and accepted thresholds;
- AOT architecture list;
- fallback route;
- known gaps and release restrictions.

The runtime team should not have to infer any of these from a model file or generated command.

## 22. Stop conditions

Stop before shipping when a candidate is only smaller, only faster on a Mac, only numerically similar at the final output, or only visually impressive in Debugger. Continue until the target device, app-level task, fallback, accessibility, privacy, and release evidence agree.

## Sources

- [Core AI](https://developer.apple.com/documentation/coreai)
- [Core AI for developers](https://developer.apple.com/core-ai/)
- [Core AI Debugger](https://developer.apple.com/documentation/coreai/inspecting-core-ai-models-with-core-ai-debugger)
- [Inspecting Core AI models with Core AI Debugger](https://developer.apple.com/documentation/coreai/inspecting-core-ai-models-with-core-ai-debugger)
- [Inspecting, debugging, and profiling Core AI models](https://developer.apple.com/documentation/coreai/inspecting-debugging-and-profiling-core-ai-models)
- [Validating inference correctness against a reference run](https://developer.apple.com/documentation/coreai/validating-inference-correctness-against-a-reference-run)
- [MTLTensor](https://developer.apple.com/documentation/metal/mtltensor)
- [MTLTensorDataType](https://developer.apple.com/documentation/metal/mtltensordatatype)
- [Machine learning passes](https://developer.apple.com/documentation/metal/machine-learning-passes)
- [Meet Core AI](https://developer.apple.com/videos/play/wwdc2026/324/)
- [Dive into Core AI model authoring and optimization](https://developer.apple.com/videos/play/wwdc2026/325/)
- [Integrate on-device AI models into your app using Core AI](https://developer.apple.com/videos/play/wwdc2026/326/)
- [Optimize custom machine learning operations with Metal tensors](https://developer.apple.com/videos/play/wwdc2026/330/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
