# SwiftUI Core AI on-device model-runtime review route

This route turns the [Core AI runtime review](../42-framework-deep-dives/113-swiftui-core-ai-on-device-model-runtime-review.md) into a build sequence. It is intentionally target-aware: Core AI and the custom Foundation Models LanguageModel bridge are current iOS 27 routes, while Foundation Models LanguageModelSession provides an iOS 26-compatible session surface for supported system-model work.

The route is:

    product outcome -> target lane -> model contract -> asset route -> integrity -> specialization -> function/provider -> typed result -> validation -> review -> commit -> evidence

Do not skip directly from model download to a domain write.

## 1. Select the target lane

Start with the product outcome, not the most advanced framework.

| Question | iOS 26 route | iOS 27 route |
| --- | --- | --- |
| Need Apple’s built-in language model | SystemLanguageModel and LanguageModelSession when available | Same route, plus later provider options when the target allows |
| Need a custom vision or tensor model | Core ML, Vision, Metal, or deterministic code | Core AI direct runtime |
| Need a custom LLM behind a shared session API | Keep the provider outside the iOS 26-only target or use an existing supported provider | Core AI resource plus CoreAILanguageModel and LanguageModelSession |
| Need offline behavior | Validate the local route and fallback | Prefer Core AI or system on-device route after readiness checks |
| Need larger context or stronger reasoning | Product-specific fallback or later OS path | Evaluate PCC or another approved provider separately |

Create an app-owned route enum with at least iOS26Fallback, coreAIDirect, coreAIFoundationModels, systemFoundationModels, and deterministicFallback. The enum is policy, not proof of availability.

## 2. Write the model manifest

Create a manifest for every model revision. Store it with the app’s delivery metadata, not only inside a model file.

Required fields:

- model identifier and semantic revision;
- source or download location;
- digest and signature status;
- license and author reference;
- source model format and compiled asset variants;
- target platform and minimum OS;
- tokenizer and companion-resource revisions;
- function names;
- input and output contracts;
- dynamic-shape limits;
- supported image or tensor formats;
- expected compute units;
- storage and memory budget;
- privacy/data path;
- iOS 26 fallback;
- evaluation fixture identifier;
- rollback policy.

An example manifest record in app-owned terms:

| Field | Example meaning |
| --- | --- |
| revision | vocab-model-2026-08-20 |
| sourceFormat | aimodel |
| compiledVariants | architecture-specific aimodelc files |
| minimumOS | iOS 27.0 for Core AI |
| resources | model, tokenizer, metadata |
| functions | main, optional embed |
| inputContract | named tensors and image descriptors |
| outputContract | named values and interpretation rules |
| fallback | system model or manual route |

Do not let a remote manifest authorize arbitrary model functions or side effects. Validate it against an app-owned allowlist.

## 3. Choose an asset delivery route

### Bundled source asset

Use a bundled aimodel or resource folder when:

- the model is small enough for the app footprint;
- the model revision is coupled to the app version;
- offline first-run availability matters;
- the app can tolerate initial specialization time.

Verify the model appears in the intended target’s resources or build phases and inspect the archived app.

### Downloaded source or compiled asset

Use Background Assets or another reviewed delivery route when:

- the model is large;
- the model can be updated independently;
- architecture-specific AOT assets should be selected on demand;
- optional features should not inflate the initial download.

The delivery layer owns transfer, retry, integrity, storage, and update state. The Core AI runtime layer owns model validity, specialization, function loading, and inference readiness.

### Foundation Models Core AI resource folder

The current Foundation Models Core AI article describes an exported resource folder containing an aimodel file, tokenizer, and any other model resources. Treat that folder as an atomic provider package. A model without its tokenizer is not ready just because the aimodel file exists.

## 4. Preflight an asset before loading

Perform a preflight task or tool before interactive inference:

1. resolve the bundle or local URL;
2. read and validate the app-owned manifest;
3. verify digest and signature when the delivery policy requires it;
4. confirm target platform and minimum OS;
5. check companion resources;
6. load AIModelAsset for an aimodel source;
7. inspect metadata and function descriptors;
8. compare the function contract with the app schema;
9. reject unsupported dynamic shapes or pixel formats;
10. record a preflight result with model revision and app build.

The preflight result may be readyForSpecialization or rejected. It must not be presented as an inference result.

## 5. Select source versus AOT asset

Use the source aimodel when device specialization flexibility matters and the first-load budget is acceptable. Use architecture-specific aimodelc assets when the build pipeline can produce and deliver them and first-load latency is important.

AOT selection route:

    current architecture -> app-owned manifest -> matching aimodelc -> local integrity check -> AIModel init -> remaining device specialization

Use AIModel.deviceArchitectureName only as one input to a validated selection function. If the matching variant is absent, show an explicit missing-asset state and choose the iOS 26 or deterministic fallback.

The current Apple AOT documentation uses a minimum deployment version of 27.0. Do not generate or advertise an iOS 26 AOT package from that route.

## 6. Specialize deliberately

Use the default specialization options first. The device can choose CPU, GPU, and Neural Engine combinations. Restrict to CPU or prefer a compute unit only when the feature’s measured workload justifies it.

Before specialization, capture:

- expected memory budget;
- whether the request is interactive or background;
- whether another model or media pipeline is active;
- whether a user-visible preparation moment exists;
- cancellation policy;
- thermal or power policy.

The default AIModelCache can supply an already specialized model. A cache miss should move the app to specializing, not block the main actor without a state update.

### Dynamic shapes

If a dynamic-shape model repeatedly sees new shapes, compare the cost of per-shape optimization with a generic dynamic path. SpecializationOptions.expectFrequentReshapes is a targeted option, not a general performance guarantee.

## 7. Own the runtime with an actor

Use one owner for model lifecycle, updates, active function, and admission. The exact Swift signatures depend on the selected SDK, but the ownership responsibilities are stable:

| Actor responsibility | Required behavior |
| --- | --- |
| load | Check manifest, cache, source, or AOT asset; emit state |
| specialize | Run off the view path; support cancellation and failure |
| prepare function | Load the named function; compare descriptors |
| admit | Limit concurrent work and reject stale inputs |
| infer | Preserve input/source revision and return a typed result |
| cancel | Stop the current task and report no commit |
| update | Install only a preflighted model revision |
| unload | Release function resources when policy requires |

Keep SwiftUI state as a projection of the actor’s app-owned state. Do not put AIModel, InferenceFunction, Metal command queues, or raw pixel buffers in a view model that can be recreated by view identity.

## 8. Validate descriptors before data conversion

Use InferenceFunctionDescriptor to obtain input and output descriptions. Build a conversion layer that:

- maps app values to named inputs;
- checks scalar type and shape;
- creates NDArray values with the declared scalar type;
- handles non-contiguous views explicitly;
- maps image inputs to a compatible pixel buffer;
- preserves orientation and color metadata;
- rejects missing or unexpected names;
- records the input contract version.

If the descriptor changes between model revisions, fail the update gate unless the app has an explicit migration. Do not infer the new input order from a function’s display order.

## 9. Run one typed inference

For a first implementation, prefer the async run path and one active request. Use states and output views only when the model contract requires stateful or preallocated output behavior. Use ComputeStream when a larger pipeline needs explicit scheduling and the command queue ownership is understood.

Capture an inference record:

- request identifier;
- source identity and revision;
- model and artifact revision;
- device and OS;
- function name;
- input shape/type summary;
- start/end timestamps;
- cancellation status;
- output type/shape summary;
- validation result.

Do not log raw images, documents, audio, or secrets by default.

## 10. Interpret outputs safely

Create a typed app-owned result that names the distinction:

| Result field | Purpose |
| --- | --- |
| observation | Raw or postprocessed model output |
| source | Input identity and revision |
| model | Model and artifact identity |
| confidence | App-defined presentation of model scores |
| validation | Deterministic checks and outcome |
| proposal | Fields eligible for review |
| commitStatus | NotStarted, Approved, Saved, or Rejected |

For image outputs, preserve the output pixel buffer only for the lifetime required by the app-owned result or copy it into a controlled representation. For tensor outputs, copy or transform them under a clear memory policy.

## 11. Add a Foundation Models bridge when appropriate

Choose the Foundation Models bridge when the feature benefits from:

- LanguageModelSession request and transcript handling;
- guided generation;
- tool definitions;
- prompt and response streaming;
- the same app-level surface across system and custom language models;
- a provider that can translate a custom LLM into the Foundation Models executor contract.

The current Core AI article shows CoreAILanguageModel loading an exported resource folder and passing it to LanguageModelSession. The provider must declare LanguageModelCapabilities accurately.

### Provider adapter route

1. guard the iOS 27 implementation;
2. resolve and preflight the resource folder;
3. initialize CoreAILanguageModel;
4. inspect capabilities;
5. create a LanguageModelSession;
6. apply instructions and tools owned by the current app phase;
7. respond or stream with cancellation;
8. validate structured output or tool proposals;
9. commit only through app-owned code.

### Custom executor route

If the app implements a LanguageModel provider directly:

- keep the LanguageModel value light;
- put loading and translation in LanguageModelExecutor;
- implement prewarm for resource and cache preparation;
- translate the transcript with supported segments only;
- apply GenerationOptions and ContextOptions honestly;
- stream metadata, usage, response, reasoning, and tool events in a defined order;
- propagate cancellation and errors;
- package the provider with Swift Package Manager and explicit platform requirements.

The executor’s generation request includes transcript, enabled tool definitions, optional schema, generation options, context options, metadata, and request ID. Do not silently drop schema or tool definitions and still claim guided generation or tool calling.

## 12. Add multimodal and tool gates

For an image-capable provider:

- check the provider’s vision capability;
- label the source and preserve orientation;
- include only the needed image or region;
- record the source revision;
- use deterministic OCR, barcode, geometry, or domain checks when the task needs exactness;
- treat the model output as an observation candidate.

For a tool-capable provider:

- expose only tools legal in the current phase;
- validate arguments independently;
- enforce per-tool authorization;
- set a maximum number of tool turns;
- make read-only tools distinguishable from side-effect tools;
- require approval for durable or external actions;
- re-resolve current domain state before commit;
- record tool and result provenance.

Direct Core AI models that emit tokens or action structures need the same parser, allowlist, and approval boundary even when Foundation Models is not used.

## 13. Design fallback and constrained routes

The runtime should return a typed reason for fallback:

- unsupportedOS;
- unsupportedDevice;
- missingAsset;
- integrityFailure;
- specializationFailed;
- descriptorMismatch;
- memoryConstrained;
- thermalConstrained;
- cancelled;
- providerCapabilityMissing;
- validationRejected;
- networkRequired;
- userChoseManual.

Map each reason to a user action. Preserve the source and state whether anything was saved.

For an iOS 26 product, the fallback implementation should be exercised with the same user journey and not only with an availability Boolean. If the custom model produces a richer result on iOS 27, show the iOS 26 behavior honestly rather than implying parity.

## 14. Update and rollback route

Use staged model updates:

    candidate download -> temporary location -> manifest/digest -> AIModelAsset inspection -> contract comparison -> device smoke test -> specialize -> validation -> activate

Keep the prior accepted revision until the candidate passes. If the candidate fails, delete its cache entries and return to the prior revision or fallback. If the OS update invalidates specialized assets, return to preparation instead of treating it as data loss.

For architecture-specific assets, download only the selected variant when the delivery strategy permits. If the app uses a source asset to generate the required variant, record the device specialization cost.

## 15. SwiftUI route states

Project runtime state into a small screen model:

| Screen section | App-owned input |
| --- | --- |
| Header | feature name and current source |
| Status | route, readiness, model revision, data path |
| Progress | preparation, specialization, or inference state |
| Result | typed observation or proposal |
| Validation | checks and explanation |
| Actions | Cancel, Retry, Use Manual Mode, Apply |
| Details | disclosure for artifact, device, and diagnostic information |

Use native controls and Liquid Glass where functional. Avoid a custom “AI dashboard” that hides the source and makes every state look equally polished.

## 16. Test and profile route

The route is not ready after a successful local call. Exercise:

- source asset preflight;
- missing companion resource;
- corrupt or wrong-revision asset;
- cache hit and cache miss;
- AOT architecture match and missing variant;
- descriptor mismatch;
- malformed input and dynamic-shape limits;
- cancellation before and during specialization/inference;
- memory and thermal constraint;
- repeated requests and queue bounds;
- OS-update/cache invalidation;
- model update and rollback;
- Core AI Debugger reference comparison;
- Xcode debug gauge and Instruments trace;
- iOS 26 fallback;
- Foundation Models provider capability and tool behavior;
- VoiceOver, Dynamic Type, reduced motion, keyboard, and pointer;
- signed physical-device build.

Keep numerical correctness, semantic quality, UI behavior, and release evidence in separate artifacts.

## 17. Evidence packet

The minimum evidence packet contains:

1. target and SDK/deployment record;
2. model manifest and digest;
3. license and provenance record;
4. AIModelAsset inspection output;
5. function descriptor snapshot;
6. source/AOT asset and architecture selection;
7. specialization/cache record;
8. physical-device inference trace;
9. memory, latency, and thermal notes;
10. Core AI Debugger reference comparison;
11. Foundation Models capability/provider record when used;
12. validation and approval fixture;
13. accessibility task matrix;
14. privacy/data-path review;
15. archive and signed artifact inspection;
16. TestFlight processing and route smoke test;
17. fallback and rollback result.

## Stop conditions

Stop before implementation when the model contract is missing, the current SDK cannot satisfy the route, the iOS 26 fallback is undefined, the target cannot ship the model resource, or the app has no way to validate and review the result before commit.

## Sources

- [Core AI](https://developer.apple.com/documentation/coreai)
- [Integrating on-device AI models in your app with Core AI](https://developer.apple.com/documentation/coreai/integrating-on-device-ai-models-in-your-app-with-core-ai)
- [AIModelAsset](https://developer.apple.com/documentation/coreai/aimodelasset)
- [AIModel](https://developer.apple.com/documentation/coreai/aimodel)
- [InferenceFunction](https://developer.apple.com/documentation/coreai/inferencefunction)
- [InferenceFunctionDescriptor](https://developer.apple.com/documentation/coreai/inferencefunctiondescriptor)
- [InferenceValue](https://developer.apple.com/documentation/coreai/inferencevalue)
- [NDArray](https://developer.apple.com/documentation/coreai/ndarray)
- [AIModelCache](https://developer.apple.com/documentation/coreai/aimodelcache)
- [SpecializationOptions](https://developer.apple.com/documentation/coreai/specializationoptions)
- [ComputeUnitKind](https://developer.apple.com/documentation/coreai/computeunitkind)
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
- [Background Assets](https://developer.apple.com/documentation/backgroundassets)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
