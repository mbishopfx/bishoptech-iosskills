# SwiftUI Core AI authoring, optimization, and debugger review design

Model-authoring tools need a different visual language from a consumer AI feature. The person using this surface is trying to understand a graph, a tradeoff, a numerical mismatch, or a device constraint. The design should make evidence inspectable, not make an optimization look magical.

This page pairs with the [Core AI authoring and optimization review](../42-framework-deep-dives/114-swiftui-core-ai-authoring-optimization-debugger-review.md), the [authoring route](../50-capability-recipes/145-swiftui-core-ai-authoring-optimization-debugger-review-route.md), and the [authoring proof matrix](../60-verification/139-swiftui-core-ai-authoring-optimization-debugger-proof-matrix.md).

## Product lanes

The current Core AI authoring and debugger material is a macOS 27/Xcode 27/iOS 27 companion route. Metal tensor APIs have their own iOS 26 availability. Use a clear target banner:

| Lane | Primary user task | Design language |
| --- | --- | --- |
| Source model | Understand model identity, license, metadata, and graph | Calm inventory and structure |
| Candidate optimization | Compare size, precision, memory, speed, and quality | Side-by-side evidence, not a winner badge |
| Debugger | Trace an operation to source and inspect tensors | Dense but navigable inspection workspace |
| Reference comparison | Locate numerical drift | Difference-focused with thresholds and sync points |
| Device execution | See behavior on a selected target | Device and compute-unit labels always visible |
| Release package | Confirm target artifacts and provenance | Checklist and artifact manifest |
| iOS 26 fallback | Continue product development without Core AI | Separate product route, not a disabled developer toy |

Never imply that a Mac-side visualization is an iPhone proof. Keep target, OS, architecture, and compute-unit labels adjacent to every performance or execution result.

## Native workspace shell

Use a native navigation shell with a stable top-level identity:

1. model and revision;
2. selected target/device;
3. current mode: Inspect, Execute, Compare, or Package;
4. main workspace;
5. evidence/status bar;
6. export or next-step action.

For iPad or Mac Catalyst, a three-column layout can work:

- Navigator: functions, modules, operations, comparison sync points;
- Structure: graph, source, tensor preview, or timeline;
- Inspector: inputs, outputs, metadata, thresholds, and evidence.

For iPhone, use a staged route instead of shrinking the desktop graph. The user can choose a function, then an operation, then an evidence card.

## Model inventory screen

The inventory view should establish identity before showing optimization controls.

### Header

- display name and model ID;
- source or candidate revision;
- target platform and minimum OS;
- artifact type: source aimodel, compiled aimodelc, or reference file;
- validation status.

### Sections

| Section | Content |
| --- | --- |
| Provenance | Author, license, source revision, conversion/optimization versions |
| Functions | Named entrypoints, input/output summary, dynamic shapes |
| Storage | Source size, candidate size, companion resources |
| Precision | Compute/storage types and compression configuration |
| Targets | Device/OS/architecture variants and known gaps |
| Evidence | Reference fixtures, comparison status, debugger/instrument traces |
| Release | Digest, signing/package state, archive/TestFlight status |

“Ready” should mean ready for the selected next action. A model can be structurally valid but not reference-validated, or reference-validated but not packaged for a device.

## Inspect mode

Inspect mode should not mix execution and deployment actions into every row. Use clear tabs or modes:

- Overview;
- Functions;
- Graph;
- Source mapping;
- Metadata;
- Artifacts.

### Graph and source mapping

Show the module hierarchy and operation graph with a selection relationship. When source mapping exists, selecting an operation should reveal the originating source location or a clear “source mapping unavailable” state.

Avoid a graph that relies only on color. Use selected outlines, labels, keyboard focus, and a list alternative for operations.

### Function view

Each function row should show:

- name;
- inputs and outputs;
- scalar and image types;
- static or dynamic dimensions;
- state inputs/outputs;
- target support;
- last validation status.

The function view is a contract inspector, not a generated API catalog. Put the app-owned interpretation in a separate layer.

## Optimization comparison design

An optimization screen should make tradeoffs visible:

| Metric | Baseline | Candidate | Scope |
| --- | --- | --- | --- |
| Artifact size | Recorded bytes | Recorded bytes | Same resources and packaging policy |
| Peak memory | Measured | Measured | Same device and workload |
| Cold load | Measured | Measured | Same OS/toolchain where possible |
| Warm inference | Measured distribution | Measured distribution | Same input fixtures |
| Thermal behavior | Sustained trace | Sustained trace | Same duration and admission policy |
| Numerical drift | Reference metric | Reference metric | Same reference and threshold |
| Task quality | Domain fixture | Domain fixture | Same acceptance criteria |

Do not collapse the table into a single score unless the weighting is explicit and the user can inspect the underlying evidence. A smaller artifact can be a worse candidate if it fails the task fixture.

### Compression controls

Expose controls as named policy choices:

- weight precision;
- activation precision;
- quantization granularity;
- calibration/reference set;
- per-layer exclusions;
- palettization configuration;
- target platform;
- static/dynamic shape strategy.

Show a warning when a setting changes the model implementation or input/output contract. Let the person clone a configuration before editing so a comparison remains reproducible.

## Reference comparison design

Comparison mode should answer: where did the candidate diverge, by how much, and what should I do next?

### Layout

- left: sync-point and operation list sorted by graph order or divergence;
- center: side-by-side tensors, absolute difference, or preview;
- right: operation metadata, shapes, precision, source mapping, and threshold;
- bottom: candidate/reference/target identities and fixture provenance.

Use explicit labels such as:

- Reference run;
- Candidate run;
- Target device;
- Compute units;
- Similarity metric;
- Accepted threshold;
- Semantic fixture status.

Do not label a similarity score “accuracy” unless it is the actual domain metric. A debugger can help locate numerical drift; it cannot certify an app-level result.

### Difference colors and accessibility

Use color only as a supplement. Add symbols, textual deltas, magnified values, and list-based summaries. An operation with no reference should say “Not compared,” not appear green.

## Execute mode

Execution controls need a target-first structure:

1. choose Mac or paired device;
2. select OS/architecture and compute policy;
3. choose function;
4. provide named inputs;
5. confirm privacy and fixture source;
6. run or cancel;
7. inspect outputs and intermediate values.

Display specialization status separately from inference status. A model that is still specializing is not “running.” A run that produced a tensor is not “validated.”

## Custom Metal design

Custom Metal kernels are advanced authoring, not a decoration for a model card.

### Kernel review panel

Show:

- kernel name;
- MSL source revision;
- PyTorch reference function;
- input/output names;
- output shape rule;
- data type and layout;
- target support;
- fallback implementation;
- numerical comparison;
- performance trace.

The panel should warn that the kernel is embedded in the model artifact and must be packaged, reviewed, and tested with that artifact.

### Metal tensor panel

For MTLTensor or TensorOps work, show:

- dimensions and strides;
- data type;
- auxiliary planes and scale factors;
- buffer ownership or shared storage;
- feature-set/device support;
- synchronization and command-queue owner.

Do not present the existence of a Metal tensor as proof that Core AI can load the model or that the target has the needed hardware.

## Native Liquid Glass application

Liquid Glass is useful for small groups of active controls:

- mode picker;
- target selector;
- run/cancel control;
- compare/export action;
- compact evidence state.

Keep graph, tensor, and source content on readable backgrounds with strong hierarchy. A large translucent graph can look impressive while reducing legibility and focus.

Use standard SwiftUI controls and platform navigation. Avoid imitating Xcode or Apple’s internal debugger branding in a way that makes a custom tool appear official.

## Empty, loading, and failure states

| State | Message | Next action |
| --- | --- | --- |
| Missing model | “Add or select a Core AI model asset.” | Import or locate |
| Missing debug metadata | “The graph is available; source mapping is not.” | Re-export with reviewed metadata |
| Reference missing | “Choose a reference run to compare.” | Load controlled reference |
| Target unavailable | “This target cannot specialize the model.” | Pick supported device or fallback |
| Conversion failed | “The exported graph could not be converted.” | Inspect operation/error report |
| Compression drift | “Candidate diverges at these operations.” | Adjust config or exclude modules |
| Performance regression | “Candidate is smaller but slower on this target.” | Review trace and target policy |
| Sensitive artifact | “This export includes tensor/reference data.” | Review retention and sharing |
| Package incomplete | “Tokenizer, AOT variant, or manifest is missing.” | Complete artifact package |

Never use a generic “AI failed” state for a model-toolchain problem.

## Accessibility and alternate input

Developer tooling can be dense without being inaccessible. Provide:

- list alternatives for graph nodes and sync points;
- VoiceOver labels for operation, tensor, target, and comparison status;
- keyboard navigation and shortcuts with visible menu commands;
- pointer and trackpad selection targets larger than graph strokes;
- Dynamic Type strategy for metadata and error panels;
- increased contrast and reduced transparency behavior;
- reduced motion for graph transitions and tensor previews;
- text or tabular summaries for image/tensor visualizations;
- export filenames and diagnostics that do not depend on color.

For a model result, state whether the data is a raw tensor, a reference comparison, or an app-level interpretation. Do not force VoiceOver users to infer that from colors.

## iOS 26 fallback design

The authoring UI can run on a Mac or later SDK while the product app supports iOS 26. Keep the fallback concept visible in product planning:

- Core AI artifact authoring is later-OS;
- Metal tensor features may be independently available on iOS 26;
- the product’s iOS 26 route uses only APIs and models supported by that target;
- the iOS 27 route can be richer without pretending parity;
- the same source/proposal/validation/commit language spans both routes.

## Design acceptance matrix

| Check | Pass condition |
| --- | --- |
| Identity | Model ID, revision, source, license, and target are visible |
| Inspectability | Functions, graph, metadata, and source mapping have separate roles |
| Comparison | Baseline/candidate/reference/target are labeled together |
| Tradeoffs | Size, memory, latency, thermal, numerical, and semantic metrics remain separate |
| Target truth | Mac, paired device, iOS 26, and iOS 27 claims are not conflated |
| Custom kernels | Reference, MSL, shapes, feature gates, and fallback are visible |
| Liquid Glass | Used for functional controls and status, not to obscure dense data |
| Accessibility | Graph/tensor/difference views have nonvisual alternatives |
| Privacy | Fixtures, reference files, logs, and exports have an explicit data policy |
| Release | Final artifact, archive, signed device run, and TestFlight result are distinguishable |

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
- [Optimize custom machine learning operations with Metal tensors](https://developer.apple.com/videos/play/wwdc2026/330/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
