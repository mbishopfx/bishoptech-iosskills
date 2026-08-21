# SwiftUI Core AI on-device model-runtime review

This page owns the custom-model runtime boundary for Core AI. It extends the existing [Core ML model lifecycle and inference review](66-core-ml-model-lifecycle-and-inference.md), [Background Assets and model/media delivery review](100-swiftui-background-assets-model-media-delivery-review.md), and [Foundation Models production-route review](111-swiftui-foundation-models-production-route-review.md) without treating the frameworks as interchangeable.

The current Apple documentation used for this page states that integrating and running a Core AI model requires macOS 27, iOS 27, and Xcode 27 or later. The current custom LanguageModel bridge is also documented as an iOS 27 API. Foundation Models LanguageModelSession itself is available on iOS 26. Therefore an iOS 26 product can use its iOS 26 Foundation Models and other supported on-device routes, but must keep Core AI symbols, model packaging, and the custom provider behind a later-OS target or availability boundary.

## The central invariant

Core AI gives an app a way to deploy and execute a model on Apple silicon. It does not turn inference into domain truth.

Keep these values separate:

| Layer | What it means | What it does not prove |
| --- | --- | --- |
| Source model artifact | An author-owned model bundle such as an aimodel file, with functions, metadata, weights, and any companion resources | That the artifact is valid for this target, honest, safe, small enough, or accurate for the app |
| Compiled model artifact | An architecture-specific aimodelc produced by ahead-of-time compilation | That the current device has the matching architecture or that on-device specialization is finished |
| Model asset inspection | Metadata and function-signature inspection through AIModelAsset or the Xcode model viewer | That the model can run or that its output is semantically correct |
| Specialized AIModel | A device- and OS-specialized runtime model, possibly loaded from AIModelCache | That a function exists, that inputs are valid, or that an output is good |
| InferenceFunction | Loaded weights, intermediate buffers, state, and a callable model function | That its output should be committed to the app’s records |
| Inference result | Named NDArray or image values returned by the model | That a classification, measurement, identity, diagnosis, or recommendation is true |
| Provider capability | A declared LanguageModel capability such as guided generation, reasoning, tool calling, or vision | That the provider has been evaluated for the task or is available on every device |
| Proposal or observation | App-owned wrapping of model output with source and model identity | That the user approved it or that the domain accepted it |
| Domain commit | A deterministic, authorized write performed by app code | That the model produced the value or that the UI preview was current |

The route is therefore:

    source and policy -> asset check -> specialization -> function load -> typed inference -> validation -> review -> authorized commit

For a Foundation Models bridge, insert provider capability negotiation and transcript/tool translation between function load and typed generation. Keep the same final validation and commit boundary.

## Version and deployment truth

### iOS 26 lane

For an app whose minimum deployment target is iOS 26:

1. Do not import Core AI into an iOS 26-only target.
2. Do not put Core AI model resources in a target that cannot satisfy the documented OS and Xcode requirements.
3. Use the iOS 26 Foundation Models system route where its availability and capability state allows it.
4. Use Core ML, Vision, Metal, Accelerate, or a deterministic implementation when those APIs match the task.
5. Keep the feature contract stable so the UI can show a later-OS Core AI route when the app runs on iOS 27 or later.
6. Test the fallback as a real feature, not as an empty placeholder.

The iOS 26 fallback may be less capable. It should still preserve source provenance, cancellation, accessibility, privacy, and the same approval boundary.

### iOS 27 Core AI lane

The current Core AI integration documentation describes the following minimum development environment:

- macOS 27 or later for authoring and building;
- Xcode 27 or later;
- iOS 27 or later for the iOS runtime;
- an Apple-silicon device appropriate for the model and the chosen deployment strategy.

Record the SDK, deployment target, model tool versions, model identifier, and supported device families in the feature’s evidence packet. A beta API page or an installed SDK does not prove that an App Store build can use the route.

### Guard the route at the product boundary

The cleanest architecture is an app-owned protocol or actor with two implementations:

- an iOS 26 implementation using a supported system or deterministic route;
- an iOS 27 implementation using Core AI directly or through CoreAILanguageModel.

Keep availability checks close to the implementation boundary. Do not scatter conditional compilation through every view. SwiftUI should receive an app-owned state such as unavailable, preparing, ready, running, proposal, fallback, or failed.

## Artifact lifecycle

### 1. Define the model contract before export

Write a model contract that names:

- the user-visible outcome;
- the model family and version;
- the input function name;
- each input name, scalar type, shape, layout, color space, orientation, or tokenizer requirement;
- each output name, type, shape, and interpretation;
- dynamic dimensions and the allowed range for each dimension;
- expected compute units and latency budget;
- memory and storage budget;
- privacy and retention path;
- evaluation fixtures and acceptable numerical or semantic thresholds;
- iOS 26 fallback behavior;
- release target and update policy.

The contract is app-owned documentation and test data. It is not generated from a model response at runtime.

### 2. Export or obtain the source artifact

Core AI uses an aimodel source format. Apple’s current documentation describes converting or authoring models with its Core AI Python tooling, then bundling the aimodel file or a resource folder containing the model and companion resources. A Foundation Models Core AI resource can include an aimodel file, tokenizer, and other model-specific resources.

The export step must preserve:

- a stable model identifier;
- source repository or license record;
- author and conversion tool version;
- function names and descriptions;
- model metadata;
- tokenizer or vocabulary revision when applicable;
- reference inputs and outputs;
- a cryptographic digest for the delivery artifact;
- the target platform and minimum OS used by compilation.

Do not treat a model registry name, download URL, or parameter count as a security or quality review.

### 3. Inspect without specializing

AIModelAsset is the unspecialized inspection surface. It can read the structure and metadata of an aimodel without performing the device-specific specialization that an AIModel load may perform. Use it in tooling, CI, or a preflight command to inspect:

- function names;
- input and output descriptors;
- dynamic shapes;
- compute and storage types;
- model summary and statistics;
- author-provided metadata;
- model validity.

AIModelAsset cannot perform inference. This distinction makes it appropriate for asset validation before an app spends device time or memory on specialization.

The Xcode model viewer is a second inspection path. Review the General and Functions views before wiring Swift input code. A question mark in an NDArray dimension means the dimension is dynamic and must be supplied or determined at runtime.

### 4. Add the target toolchain and resource correctly

The current integration documentation says Core AI model integration in Xcode requires the Metal Toolchain. If the toolchain is missing, a target that includes aimodel files can fail with a missing Metal compiler error.

For each target that owns the model:

- install and record the Metal Toolchain version;
- add the model to the intended app, package, or extension target only;
- verify the model appears in the target’s build phases;
- verify the resource is copied or delivered according to the selected route;
- do not duplicate a large model in every extension by accident;
- inspect the built app or package to confirm the final resource path;
- ensure privacy and licensing metadata are tracked outside the model’s marketing label.

Model delivery can be bundled or downloaded. The [Background Assets and model/media delivery route](../50-capability-recipes/131-swiftui-background-assets-model-media-delivery-review-route.md) covers managed delivery, while this page owns the Core AI readiness after a file reaches local storage.

### 5. Compile ahead of time when it earns its cost

Core AI specializes a model for the device before inference. The coreai-build tool can move the expensive compilation portion to the Mac and produce one aimodelc asset per supported device architecture.

The runtime still performs some device specialization. AOT compilation reduces first-load work; it does not remove the need for a real device load test.

The AOT pipeline is:

    aimodel source -> coreai-build per target platform and minimum OS -> architecture-specific aimodelc assets -> matching asset delivery -> AIModel load -> remaining device specialization -> InferenceFunction

At runtime, use AIModel.deviceArchitectureName to select the compiled asset that matches the current device. The source model name and architecture string must not be accepted from an untrusted server response without validating them against an app-owned manifest.

The current Apple example compiles for iOS with a minimum deployment version of 27.0. There is no AOT Core AI route to advertise for an iOS 26 target based on the current documentation.

## Runtime stages and gates

### Gate A: capability and route selection

Before loading a model, determine:

- the running OS and target implementation;
- whether this device family is supported by the model artifact;
- whether the model is bundled, downloaded, or unavailable;
- whether the user has opted into a network or larger model route;
- whether the app is in a foreground or background execution mode;
- whether the task requires a vision, text, stateful, or generative model;
- whether the iOS 26 fallback can satisfy the user outcome.

This gate chooses a route. It does not load anything and does not promise that inference will succeed.

### Gate B: source integrity and readiness

Validate the local asset before creating an AIModel:

- file or resource folder exists;
- the app-owned manifest matches the model identifier and revision;
- the digest and signature, when used, match the downloaded artifact;
- required tokenizer or companion files exist;
- the file is valid according to AIModelAsset.isValid;
- storage policy allows the asset and cache;
- the current target and OS match the artifact’s declared minimum;
- no stale update is being used after a model revision change.

An available file is not a ready model. A ready model is not a validated result.

### Gate C: cache and specialization

AIModelCache.default stores device-specialized artifacts for the app bundle. Call model(for:options:) when a cache hit can avoid repeating specialization. If it returns nil, the app can inform the person and specialize deliberately.

Use the default specialization options first. The system can select CPU, GPU, and Neural Engine combinations. Restricting to CPU or preferring a compute unit is an optimization decision that requires measured evidence on the target device.

For dynamic-shape models, expectFrequentReshapes can change the specialization strategy. Use it only after measuring the repeated-shape behavior; it is not a blanket performance switch.

The first specialization belongs in a preparation state, not hidden inside a tap that appears to hang. Prewarm or explicitly specialize when the app has a user-meaningful preparation moment.

### Gate D: function load and descriptor check

AIModel is lightweight and does not own the weights and intermediate buffers used by loaded functions. Loading an InferenceFunction prepares the resources needed for that function and can be expensive.

After loading a named function:

- confirm the function exists;
- inspect its descriptor;
- compare expected input and output names;
- compare scalar types and shapes;
- accept dynamic dimensions only within the app’s declared range;
- verify image descriptors and pixel formats;
- reject a model revision whose function contract changed without an explicit migration.

Descriptor inspection prevents a deployment update from silently changing the meaning of an input tensor.

### Gate E: input staging

NDArray values are typed tensors. Their shape and scalar type must match the model contract. The mutable view is a write path; a read-only view is a read path. Preserve ownership and lifetime until the inference call has completed.

Image inputs and outputs use pixel-buffer values when the model was converted with image signatures. Use the ImageDescriptor to check width, height, and pixel format. A dynamic width or height is represented by a negative dimension in the current documentation; the app still needs an application-level allowed range.

For camera or media sources, preserve:

- source identifier and revision;
- orientation;
- pixel format and color space;
- crop or resize transform;
- capture time when meaningful;
- permission state;
- whether the data was original, cached, or user-edited.

Core AI receives values. The app owns what those values mean.

### Gate F: inference and scheduling

InferenceFunction.run provides an async Swift route for inputs, state, and output views. The encode route can place inference work on a ComputeStream. A ComputeStream serializes dependent work on that stream; a Metal-backed stream must respect the command queue’s ownership and lifecycle.

InferenceFunction is Sendable and can run concurrently. That does not mean unlimited concurrency is a good product choice. Multiple concurrent requests can multiply intermediate buffers and compete for CPU, GPU, Neural Engine, memory, battery, and thermal headroom.

Start with one actor-owned function and an explicit admission policy:

- one active interactive request per feature;
- latest-frame or bounded-queue policy for live sources;
- cancellation when the user leaves the screen;
- no unbounded task spawning from a camera or scroll callback;
- reduced compute or deferred work when the device is thermally constrained;
- a visible preparation or throttled state when a request cannot start.

Measure the policy with the Core AI debug gauge and Instruments rather than assuming that more parallelism is faster.

### Gate G: output interpretation

Remove outputs by their names and check whether each is an NDArray or pixel buffer. Validate:

- output shape and scalar type;
- finite numeric values where appropriate;
- range and confidence policy;
- model revision and input revision;
- cancellation and partial-result status;
- source provenance;
- whether postprocessing was performed;
- whether a deterministic domain validator accepted the output.

An output tensor is not a database update. Wrap it in an app-owned result type before SwiftUI sees it.

## Model specialization and cache policy

### What invalidates a cache entry

The current caching documentation identifies three important invalidation paths:

- an OS update, because specialized assets are tied to the OS version;
- a source model change or deletion;
- storage pressure for purgeable assets.

The app must be able to recover from a cache miss at any launch. Treat a saved bookmark as a convenience, not permanent possession of the specialized bytes. Bookmark resolution can fail after invalidation, purge, or manual deletion.

### Updates

For a model update:

1. download the candidate to a temporary location;
2. validate its manifest, digest, license, and model contract;
3. inspect it as an AIModelAsset;
4. compare the function contract with the app’s supported schema;
5. delete or retire old cache entries for the old source URL as appropriate;
6. atomically install the new source;
7. specialize or AOT-load it at a preparation point;
8. run reference and device smoke tests;
9. mark the revision active only after the app-owned acceptance gate passes.

Do not replace a model file while an active AIModel or InferenceFunction still uses its cache entry. Coordinate update and inference through the same actor or an equivalent lifecycle owner.

### App groups

The current documentation allows an AIModelCache scoped to an App Group so multiple targets can share specialized assets. Use this only when the targets share the same model contract, entitlement boundary, privacy policy, and update owner. An App Group is a sharing mechanism, not a cross-team trust boundary.

## Core AI and Foundation Models

### Direct Core AI inference

Use the direct Core AI route when the feature needs a model with tensor or image functions, low-level state, custom buffers, or explicit compute scheduling. The app owns tokenization, decoding, postprocessing, and domain integration when the model requires them.

This route is appropriate for:

- image classification or segmentation;
- vision transformers;
- speech or audio models whose input contract is app-owned;
- embeddings or ranking functions;
- generative models where the app needs explicit token/state control;
- pipelines that combine multiple model functions;
- strict memory or latency budgets that need direct profiling.

### Core AI through Foundation Models

The current Foundation Models article describes a CoreAILanguageModel supplied by the Core AI models package. The app exports a model resource folder, adds the package, initializes CoreAILanguageModel with that folder, and passes it into LanguageModelSession. The rest of the session surface can remain the same as the system or server model route.

The resource folder can contain:

- an aimodel file;
- a tokenizer;
- model-specific resources.

Loading is asynchronous because the framework compiles the model and loads the tokenizer before the first request. Preload when a request is at least a short moment away, but still show a real preparation state and handle failure.

The provider bridge changes the model, not the app’s authority model. Tools, guided output, instructions, streaming, reasoning segments, and transcript behavior still require capability checks and validation.

### LanguageModel and LanguageModelExecutor boundary

The current LanguageModel protocol describes capabilities and an executor configuration. The model type should remain intentionally light. LanguageModelExecutor owns the work:

- initialize from configuration;
- prewarm assets and caches;
- translate Transcript entries into the model’s native format;
- apply GenerationOptions and ContextOptions;
- invoke the local engine or other provider;
- stream response events through LanguageModelExecutorGenerationChannel.

LanguageModelExecutorGenerationRequest carries the transcript, enabled tool definitions, optional schema, generation options, context options, metadata, and request identifier. The channel can stream text, reasoning, tool-call lifecycle, metadata, and usage events. Report provider identity and usage metadata deliberately; do not expose internal reasoning as person-facing content unless the product has a clear, reviewed presentation.

The framework can reject an incompatible request when the declared LanguageModelCapabilities do not contain the required capability. Declare only what the executor actually implements and test each capability independently.

## Multimodal and tool boundaries

Core AI’s direct API can represent tensors and images. Foundation Models attachments are a separate session-level abstraction. A provider must actually support vision before a prompt containing an image is dispatched.

For a multimodal route:

1. identify the source and permission;
2. normalize orientation and pixel format;
3. inspect the model function or provider capability;
4. attach the smallest sufficient source;
5. preserve attachment labels and revision identity;
6. treat the model result as an observation candidate;
7. use Vision or deterministic code for exact OCR, barcodes, geometry, or validation when applicable;
8. review before any durable action.

Foundation Models tools can call app code, but a tool is not a permission grant. Keep side effects behind a typed approval or app-owned command. For a direct Core AI decoder, treat generated tokens as untrusted input and use the same action parser and authorization boundary.

## Memory, thermal, and device constraints

### Memory is a staged budget

Track at least:

- source artifact bytes on disk;
- compiled asset bytes;
- tokenizer and companion resources;
- specialized cache bytes;
- weights and intermediate buffers owned by InferenceFunction;
- input/output tensor or pixel-buffer allocations;
- concurrent request count;
- trace and debug data.

The model file’s storage size is not the runtime memory footprint. The model instance is lightweight, while loaded functions own resources needed for inference. A memory plan therefore needs a model-load budget, a per-request budget, and an update/cache budget.

### Thermal and energy policy

An inference route that is correct on a cool development device may become unusable during a camera session, navigation, playback, or charging condition. Record:

- device model and OS;
- battery and power mode if relevant;
- sustained workload duration;
- CPU/GPU/Neural Engine selection;
- frame admission or request rate;
- latency distribution rather than one fastest sample;
- thermal state transitions observed;
- cancellation and recovery behavior.

If a feature cannot meet its budget, reduce input size, reduce request frequency, use a smaller or simpler route, move work out of the hot path, or use the iOS 26 fallback. Do not hide a thermal stop behind a generic “AI failed” message.

### Device matrix

Test the model on every device family the feature claims to support. The Core AI documentation describes architecture-specific AOT assets and automatic compute-unit selection, so a Mac result is not iPhone proof, and a simulator result is not Neural Engine proof.

At minimum record:

- exact device identifier and architecture;
- OS build and app build;
- model and tokenizer revision;
- source or AOT asset selected;
- compute units available and preferred;
- cache hit or specialization duration;
- function load duration;
- inference latency and memory;
- cancellation, background, and thermal behavior;
- output validation result.

## Correctness and evaluation

Core AI Debugger supports a three-step workflow: visualize the model, execute it on a selected target, and compare output against a reference run. The current validation documentation warns that quantization and specialization can introduce numerical drift. Use reference runs to validate conversion and optimization, not to claim that a model’s user-facing output is automatically domain-correct.

Use separate fixtures for:

- conversion correctness;
- AOT versus source equivalence;
- tokenizer and decoding correctness;
- input orientation and color conversion;
- dynamic shape boundaries;
- output range and finite-value policy;
- cancellation and partial output;
- cache hit and invalidation;
- device/thermal/memory constraints;
- iOS 26 fallback equivalence at the product-contract level;
- Foundation Models capability and tool behavior;
- deterministic domain validation and approval.

The Core AI debug gauge observes model load, specialization, and inference activity during a debug session. The Core AI instrument measures timing across CPU, GPU, and Neural Engine. Keep those traces attached to a build and device record. A trace is performance evidence, not semantic evidence.

## Native SwiftUI and Liquid Glass boundary

The AI runtime should be visually subordinate to the user’s task. A native shell can show:

- model route and data path;
- preparation or specialization progress;
- current source and model revision;
- a concise capability summary;
- a proposed result with confidence or uncertainty language;
- a clear approval action;
- a deterministic validation result;
- a retry, fallback, or offline action.

Use system typography, semantic colors, standard controls, platform navigation, and Liquid Glass only where it improves hierarchy or interaction. A glass surface must not make a speculative model result look authoritative. Keep status text readable in increased contrast, large text, reduced transparency, and reduced motion.

For a direct model result, use a review card. For a model-generated action, show the action’s exact scope, source revision, model revision, and changed fields before approval. For a failure, preserve the source and offer a deterministic or iOS 26 route when possible.

## Privacy and security

On-device execution can keep model input on the device, but privacy review still includes:

- model downloads and update servers;
- authentication and package dependencies;
- source images, audio, and documents;
- tokenizer and transcript storage;
- Foundation Models transcript rehydration;
- App Group cache sharing;
- OSLog, signposts, crash reports, and Instruments traces;
- debug exports and reference fixtures;
- user approval and audit records;
- fallback routes that may use a network provider.

Do not put raw secrets into model prompts, dynamic instructions, model metadata, labels, session properties, or logs. Make the data path visible in the UI when a feature can be local, PCC, or external. Clear transient inputs and temporary model files according to the product’s retention policy.

## Release proof

The [Xcode archive, signing, TestFlight, and release review](75-xcode-archive-signing-testflight-and-release.md) remains the release authority. Add Core AI-specific proof:

1. the iOS 26 target builds without importing Core AI;
2. the iOS 27 target or guarded slice builds with the documented SDK and Metal Toolchain;
3. the archive contains only intended model resources and architecture assets;
4. the model identifier, license, digest, tokenizer, and target platform are recorded;
5. a signed physical-device build loads the intended artifact;
6. the device architecture selects the intended AOT asset when used;
7. specialization and function load complete outside a blocked tap path;
8. input descriptors and output interpretation pass fixtures;
9. Instruments and Core AI debug-gauge traces exist for claimed performance;
10. thermal, memory, cancellation, update, and cache invalidation behavior are recorded;
11. Foundation Models provider capability and transcript/tool behavior pass on the actual route;
12. accessibility tasks pass on a physical device;
13. TestFlight processing and review metadata match the actual data path;
14. App Store release notes and privacy disclosures do not claim the model is available on iOS 26 when the implementation is iOS 27-only.

## Route decision table

| Need | Preferred first route | Escalation | Evidence |
| --- | --- | --- | --- |
| Text generation on iOS 26 | Foundation Models SystemLanguageModel when available | Deterministic or product-specific fallback | Availability, prompt fixture, physical device |
| Custom tensor or image model on iOS 26 | Core ML, Vision, Metal, or a deterministic pipeline | Later-OS Core AI implementation | Model contract, target compile, device inference |
| Custom model on iOS 27 | Direct Core AI | AOT and Background Assets when load time or size requires it | AIModel/InferenceFunction trace, device matrix |
| Custom LLM through the session API | Core AI resource plus CoreAILanguageModel provider | Another explicitly supported LanguageModel provider | Capability, executor, transcript, stream, tool fixture |
| Repeated dynamic-shape inference | Core AI with measured specialization options | Preallocated outputs, ComputeStream, or a smaller model | Shape, memory, latency, thermal trace |
| Exact OCR or barcode | Vision or Foundation Models image tools | Core AI only when its contract is evaluated for the task | Source-linked ground truth, device proof |
| Durable app mutation | Model proposal plus deterministic validator and approval | Manual entry or safe fallback | Revision, user approval, domain commit log |

## Stop conditions

Stop the route and request a narrower decision when:

- a model artifact lacks an owner, license, version, or digest;
- the exported function contract cannot be inspected;
- the target cannot satisfy the documented OS or toolchain;
- the app cannot show a fallback for an iOS 26 route;
- memory or thermal behavior is unknown for the claimed device class;
- a model result is being written as domain truth without validation;
- a provider claims a capability its executor does not implement;
- a download or cache update can replace an in-use model unsafely;
- a debug trace is being used as semantic proof;
- a simulator run is being presented as physical Neural Engine or release proof.

## Sources

- [Core AI](https://developer.apple.com/documentation/coreai)
- [Integrating on-device AI models in your app with Core AI](https://developer.apple.com/documentation/coreai/integrating-on-device-ai-models-in-your-app-with-core-ai)
- [AIModelAsset](https://developer.apple.com/documentation/coreai/aimodelasset)
- [AIModel](https://developer.apple.com/documentation/coreai/aimodel)
- [InferenceFunction](https://developer.apple.com/documentation/coreai/inferencefunction)
- [InferenceValue](https://developer.apple.com/documentation/coreai/inferencevalue)
- [NDArray](https://developer.apple.com/documentation/coreai/ndarray)
- [ComputeStream](https://developer.apple.com/documentation/coreai/computestream)
- [Managing model specialization and caching](https://developer.apple.com/documentation/coreai/managing-model-specialization-and-caching)
- [Compiling Core AI models ahead of time](https://developer.apple.com/documentation/coreai/compiling-core-ai-models-ahead-of-time)
- [Inspecting, debugging, and profiling Core AI models](https://developer.apple.com/documentation/coreai/inspecting-debugging-and-profiling-core-ai-models)
- [Validating inference correctness against a reference run](https://developer.apple.com/documentation/coreai/validating-inference-correctness-against-a-reference-run)
- [Running a Core AI model in a Foundation Models session](https://developer.apple.com/documentation/foundationmodels/running-a-core-ai-model-in-a-foundation-models-session)
- [LanguageModel](https://developer.apple.com/documentation/foundationmodels/languagemodel)
- [LanguageModelCapabilities](https://developer.apple.com/documentation/foundationmodels/languagemodelcapabilities)
- [LanguageModelExecutor](https://developer.apple.com/documentation/foundationmodels/languagemodelexecutor)
- [LanguageModelExecutorGenerationRequest](https://developer.apple.com/documentation/foundationmodels/languagemodelexecutorgenerationrequest)
- [LanguageModelExecutorGenerationChannel](https://developer.apple.com/documentation/foundationmodels/languagemodelexecutorgenerationchannel)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Generative AI](https://developer.apple.com/design/human-interface-guidelines/generative-ai)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Background Assets](https://developer.apple.com/documentation/backgroundassets)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Core AI WWDC26 overview](https://developer.apple.com/videos/play/wwdc2026/324/)
- [Integrate on-device AI models using Core AI](https://developer.apple.com/videos/play/wwdc2026/326/)
