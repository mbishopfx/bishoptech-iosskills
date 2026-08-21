# SwiftUI Foundation Models advanced provider and multimodal route review

This page extends the production lifecycle in the [Foundation Models production-route review](111-swiftui-foundation-models-production-route-review.md). T191 focused on one on-device session, context budgeting, guided output, tools, cancellation, evaluation, and release proof. This route covers the next boundary: one session API can sit over different model providers, dynamic profiles can change the model and tool set as app state changes, and a prompt can contain image attachments.

The advanced route is not “add an agent.” It is a controlled choice among:

- the on-device SystemLanguageModel;
- Private Cloud Compute when the feature and target permit it;
- a custom LanguageModel provider such as a Core AI or other package-backed model;
- a multimodal prompt with source-labeled attachments;
- a dynamic profile that changes instructions, tools, model, history view, and generation settings;
- a bounded tool loop whose current data and side effects remain app-owned.

The invariant remains:

Model provider and capability are selected by app policy. Dynamic instructions describe the current task. Attachments carry source material. Tools expose narrow operations. SwiftUI presents uncertainty and approval. Deterministic code owns truth, authorization, and commit.

## Route summary

| Question | Route answer |
| --- | --- |
| Does the feature need only local language understanding? | Start with SystemLanguageModel and keep the offline route |
| Does it need larger context or stronger reasoning? | Evaluate Private Cloud Compute when the OS, entitlement, region, quota, privacy, and product policy allow it |
| Does it need a model that Apple does not provide? | Adopt a LanguageModel provider package and declare capabilities honestly |
| Does it need to inspect an image? | Use Attachment with the correct source/orientation, start on device, and combine Vision tools when exact OCR/barcode work matters |
| Does the tool set change by screen or workflow phase? | Use DynamicInstructions/Profile/DynamicProfile and include only the current tools |
| Does the history contain sensitive or irrelevant entries? | Transform or compact the history before each request under an explicit policy |
| Can the model call multiple tools or repeat a tool? | Design tools for concurrency, idempotency, authorization, and bounded exit |
| Does a provider claim reasoning, vision, guided output, or tools? | Inspect LanguageModelCapabilities before dispatching |
| Is the feature ready for release? | Prove provider availability, source provenance, quality, privacy, accessibility, physical-device behavior, artifact, and fallback separately |

## Provider lanes

### SystemLanguageModel

The system model is the default on-device Apple Foundation Model. It is the starting point for an intelligence feature because it keeps the work offline when available and uses the system’s Apple Intelligence eligibility and model-readiness checks. T191 covers the request lifecycle and availability states in detail.

Treat these as distinct:

- Apple Intelligence is enabled;
- the device is eligible;
- model assets are ready;
- the selected language or locale is supported;
- the model supports the capability required by this request;
- the prompt and schema fit the current context;
- the result meets the feature’s quality criteria.

A ready model is not a quality guarantee.

### PrivateCloudComputeLanguageModel

Private Cloud Compute is a different provider lane with a unified LanguageModelSession request surface. Apple’s current documentation describes it as a larger-context and stronger-reasoning route that preserves privacy guarantees, but it is not an offline route and has a per-user quota. The current documentation also describes a 32K context size for PCC versus a 4K on-device context reference, and states that PCC availability begins on iOS 27 and corresponding platform versions.

For an iOS 26 product, this means:

1. keep PCC behind an availability check;
2. do not reference a PCC symbol from an unavailable deployment path without a guarded branch;
3. distinguish iOS 26’s on-device route from a later OS’s PCC route;
4. verify the managed entitlement and eligibility requirements;
5. show the person whether the request is local or PCC when that distinction affects expectations;
6. account for quota and no-network behavior;
7. evaluate whether the higher-capability route actually improves the feature;
8. retain an on-device or deterministic fallback.

PCC availability and quota are different signals. A model may be available while the user has reached the current usage limit. The UI should expose a quota state that can explain approaching, reached, or reset conditions without making a server error look like a model-quality problem.

### Custom LanguageModel provider

Foundation Models defines a LanguageModel protocol so a model provider can use the same LanguageModelSession surface. The provider describes its capabilities and gives the framework an executor configuration. The executor translates framework requests into the provider’s native format and streams events back through a generation channel.

The model value should remain intentionally light. Heavy work belongs in LanguageModelExecutor. A provider package should make target support, authentication, dependencies, cancellation, privacy, and release configuration explicit. Apple’s documentation recommends Swift Package Manager distribution for providers.

Custom provider claims must be specific:

- local or server-based;
- offline or network-dependent;
- input modalities;
- guided-generation support;
- tool-calling support;
- reasoning support;
- context size;
- quota and billing;
- authentication;
- retention and logging;
- supported platforms;
- cancellation behavior;
- custom segments or metadata;
- source and version identity.

The unified session API hides provider mechanics, not provider responsibility.

## Capability negotiation

LanguageModelCapabilities lets a provider declare what it can do. The current documented capability set includes guided generation, reasoning, tool calling, and vision. Before dispatching a request, inspect the selected model’s capabilities:

| Request | Required capability | Fallback |
| --- | --- | --- |
| plain text prompt | basic model request | deterministic or unavailable state |
| image attachment | vision | Vision/Core ML/OCR route or text-only fallback |
| Generable output | guidedGeneration | plain draft or deterministic form |
| tool call | toolCalling | disallowed-tools route or manual action |
| deeper reasoning | reasoning | simpler prompt, on-device route, or user-approved PCC |

If a model does not support a requested capability, the framework can reject the dispatch with an unsupported-capability error. That is better than allowing a model provider to pretend it can satisfy a request and producing an ambiguous failure later.

Do not infer capabilities from a provider name, marketing copy, or a successful plain-text response. Use the provider’s declared capability value and test the actual route.

## Dynamic instructions, profiles, and state

### Static instructions are not enough for phaseful apps

LanguageModelSession’s ordinary instructions are evaluated at session initialization and remain static for that session. That is useful for a simple bounded task. It becomes wasteful when a workflow moves between phases such as:

- select a photo;
- inspect image content;
- search an inventory;
- propose an edit;
- ask for approval;
- commit a change.

Do not put every tool, policy, and instruction for every phase into one permanent prompt. It increases context, can confuse the model, exposes capabilities that the current screen does not need, and makes privacy review harder.

### DynamicInstructions

DynamicInstructions declaratively assembles the instructions and tools used by a request. Its body is evaluated before every model request, so it can reflect the current app state. Nested dynamic instructions keep concerns separate.

Good dynamic instruction inputs:

- current editing mode;
- selected record or attachment identity;
- whether the user has approved a capability;
- current phase and allowed tools;
- current language or locale;
- deterministic feature flags;
- an app-owned summary of prior work.

Bad dynamic instruction inputs:

- raw untrusted content copied into developer instructions;
- secrets or access tokens;
- hidden authorization decisions;
- an entire database dump;
- a tool that is not legal in the current UI state.

When conditionally providing instructions and tools, append them in place when the provider’s caching behavior benefits from stable prefixes. Keep stable content early and phase-specific content later. Measure the cache effect rather than assuming that every dynamic branch is cheap.

### Profile

A LanguageModelSession.Profile binds DynamicInstructions to session-level values such as the model, temperature, reasoning level, lifecycle callbacks, and history behavior. A profile is a unit of work. A profile can make the model lane and output policy explicit for a feature phase.

Examples:

- local extraction profile: SystemLanguageModel, greedy sampling, no tools;
- image-triage profile: vision-capable model, OCR/BarcodeReaderTool, typed labels;
- enrichment profile: PCC or another approved provider, larger context, read-only tools;
- approval profile: no external tools, typed action proposal, human confirmation required.

Profiles should change in response to deterministic app state, not to arbitrary model wording.

### DynamicProfile

A DynamicProfile orchestrates transitions between profiles and maintains one active profile. It can coordinate specialized model configurations and conditional instructions. Use it for a workflow where the model lane itself changes with the phase, not for every small UI toggle.

Profile transitions need:

- a named phase;
- entry and exit conditions;
- allowed model providers;
- tool set;
- history view;
- capability requirements;
- privacy/data-flow policy;
- cancellation behavior;
- user-visible status;
- evaluation fixture coverage.

The profile is configuration and orchestration. It is not permission to execute a domain mutation.

## Session properties and history

The dynamic profile API exposes SessionProperty access to session-scoped values and history. History can be used for compaction, summarization, or phase-specific context. Model output can influence dynamic-instruction and tool evaluation, so the framework treats history as read-only in those contexts; use lifecycle or explicitly supported transforms for mutation.

App-owned session properties can carry small, non-sensitive state such as:

- selected workflow phase;
- activated skill identifiers;
- current source revision;
- feature policy;
- a tool-use counter;
- a deterministic approval token that is not itself authorization.

Do not store secrets or raw credentials in session properties. Do not mistake a session property for a secure storage boundary.

### historyTransform

historyTransform receives current history before a model request and can return only the entries needed for that provider and phase. This is a context, privacy, and routing tool:

| Provider/phase | History policy |
| --- | --- |
| local short extraction | current prompt and selected source only |
| image review | attachment references and current task |
| planning phase | recent decisions and tool outputs |
| approval phase | current typed proposal and source revision |
| PCC enrichment | broader history only if privacy policy allows |
| custom provider | provider-specific supported segments and metadata |

The transform is a view of history for a request; it need not delete the global transcript. Record what was sent when evaluation and privacy policy permit, but do not retain raw sensitive data by default.

## Multimodal prompting

### Attachment types and provenance

Foundation Models can combine text with image attachments. The current documentation describes Attachment inputs from CGImage, CIImage, CVPixelBuffer, and image file URLs. The framework performs needed scaling and color conversion. It can apply an orientation transform when the attachment specifies one.

Source pipeline:

1. establish app-owned source identity and user permission;
2. choose the smallest image or region that answers the task;
3. preserve orientation and color/source metadata;
4. create a labeled Attachment;
5. include the attachment in a bounded Prompt;
6. record the source revision and attachment label;
7. treat the model result as an observation candidate;
8. validate against the source or a specialized framework;
9. show review and provenance before any commit.

A file URL must actually point to an image. A CVPixelBuffer from AVFoundation needs the correct orientation. A screenshot or transformed image may no longer represent the original source; state that in the UI if it matters.

### Label attachments

Labels help the model and tool calls identify a specific attachment. Use stable, human-readable labels such as receipt-photo or barcode-image. Do not put private names, access tokens, or database keys in labels.

For a tool that receives ImageReference, resolve the reference against the session transcript and verify that the attachment still exists, belongs to the current task, and is permitted for the tool. A missing image should be a typed tool failure, not an empty success.

### On-device first

Apple’s image-analysis guidance recommends starting with the on-device model and using PCC when more reasoning or context is necessary. Use the least-capable route that meets the task:

- classification into a finite safe set: on-device plus Generable;
- OCR: Vision OCRTool or OCR framework;
- barcode extraction: BarcodeReaderTool;
- document summarization: on-device first, with source review;
- multi-image comparison: on-device with labeled attachments;
- large-context multimodal reasoning: evaluate PCC or approved provider;
- durable image edit: model proposal plus deterministic image pipeline.

Do not turn a generated description into a verified identity, diagnosis, measurement, or legal fact without domain-specific evidence.

## Built-in and custom image tools

Vision supplies built-in tools such as OCRTool and BarcodeReaderTool for Foundation Models sessions. These are useful when the task needs exact extraction or a specialized operation. A custom tool can use ImageReference to access an attachment and call Vision/Core ML or another deterministic image service.

The custom tool boundary should declare:

- which image labels it accepts;
- maximum images or regions;
- supported formats;
- whether it can run concurrently;
- whether it is read-only;
- timeout and cancellation;
- privacy and retention;
- output schema;
- confidence/source fields;
- no-result and failure behavior.

Tool output is a source-linked result, not a model-independent truth claim. The app should show which tool produced it and when.

## Agentic workflow without uncontrolled autonomy

Dynamic profiles make agentic workflows composable, but the route should remain bounded:

1. the user starts a named task;
2. the active profile selects the minimal instructions and tools;
3. the model proposes a next step or calls a tool;
4. the tool performs a narrow read or produces a proposal;
5. lifecycle callbacks record or validate the transition;
6. the app updates deterministic state;
7. the next profile or request sees a current snapshot;
8. the UI asks for approval before consequential work;
9. the domain layer commits and returns a result;
10. the profile closes or hands off to a separate task.

Avoid hidden loops. Every agentic route needs:

- maximum request count;
- maximum tool calls;
- cancellation;
- timeout;
- context policy;
- allowed tool set;
- provider capability gate;
- approval policy;
- exit condition;
- observable call graph;
- fallback.

The model can choose a tool or next phase, but the app decides whether that phase is legal.

## Provider handoff

A dynamic profile can hand off between model providers while keeping one session API. The handoff must define what context crosses the boundary:

| Boundary | Preserve | Re-check |
| --- | --- | --- |
| on-device to PCC | app-owned summary, current prompt, approved attachments | privacy disclosure, entitlement, quota, availability, locale, context size |
| on-device to custom local model | selected source, typed task, provider capabilities | model asset readiness, memory, supported schema, cancellation |
| PCC to on-device fallback | compact summary and user-owned source | lost reasoning/context, unsupported tools, offline status |
| image model to text-only model | OCR or Vision result with provenance | source loss, confidence, privacy, hallucinated visual details |
| plan profile to approval profile | typed proposal and source revision | authorization, current domain state, allowed action |

Never copy a raw external transcript into a provider that the person did not authorize. A handoff is a data-flow event, not just a model constructor change.

## Model provider privacy matrix

| Provider | Data path | Offline | Quota/entitlement | Product copy |
| --- | --- | --- | --- | --- |
| SystemLanguageModel | on-device Apple Foundation Model | yes when ready | device/region/Apple Intelligence/model readiness | On-device suggestion when accurate |
| PrivateCloudComputeLanguageModel | Private Cloud Compute | no | managed entitlement, availability, daily quota | private cloud processing and quota when relevant |
| Core AI or local provider | app-managed on-device model | generally yes after assets | model assets, memory, package/target | local model with app-specific limits |
| server provider | network/provider | no | account, network, billing, provider policy | external service and data-flow disclosure |

The app should not claim “private” as a blanket label for a custom server provider. Audit retention, authentication, transport, failure, and provider policy.

## Instrumentation and evaluation

The Foundation Models Instrument can show prompts, responses, tools, latency, model loading, and token usage. It can expose sensitive prompt and response data in unencrypted trace files. Handle traces under the developer program and project privacy policy.

For advanced providers, measure:

- time to first token;
- model loading;
- cached versus generated tokens;
- prompt and output tokens;
- tool latency;
- total request duration;
- provider handoff time;
- image preprocessing;
- history-transform cost;
- quota or network waits;
- cancellation;
- memory and thermal state;
- output quality by provider.

The Evaluations framework works with Foundation Models model lanes, including on-device, PCC, and other models. Use it to compare provider choices and profile transitions against the same dataset and criteria. A provider with better prose but worse tool authorization or image provenance does not win the production route.

## Safety and prompt injection

Apple’s safety guidance describes built-in guardrails and recommends app-specific safety layers. For advanced routes:

- keep trusted Instructions separate from user and imported content;
- never insert unverified text into instructions;
- wrap open input in app-authored prompt structure;
- use bounded schemas and safe enums;
- add deterministic deny lists or content policy where appropriate;
- limit provider and tool access by phase;
- validate image sources and labels;
- do not let an attachment or tool result change authorization;
- test prompt injection through text, image OCR, file names, tool output, and transcripts.

Dynamic instructions make injection boundaries more important because the body re-evaluates. A model-generated string should not be used as a new trusted instruction without an explicit, deterministic policy.

## Native SwiftUI route

The UI should name the active provider only when that information helps the person:

- local suggestion;
- private cloud suggestion;
- image analysis;
- waiting for a model;
- using a standard workflow.

Use Liquid Glass for the functional action group, profile/status control, and review/approval cluster. Keep provider choice in a readable status surface or settings screen, not in decorative chrome.

When a profile changes:

- announce the phase;
- update tool availability;
- show what source is in context;
- retain cancel;
- avoid animating an external data-flow change as if it were cosmetic;
- preserve a fallback when a later provider is unavailable.

For images, show the selected image or region, the attachment label when useful, and the output provenance. For PCC or external routes, make the data path and quota/retry state understandable.

## Release boundary

Advanced Foundation Models evidence must prove:

1. provider selection and target availability;
2. model capability negotiation;
3. entitlement and quota behavior for PCC;
4. local versus cloud data-flow copy;
5. image source, orientation, permission, and provenance;
6. dynamic profile transitions;
7. history transform and context budget;
8. tool loop exit, cancellation, and approval;
9. provider fallback;
10. Evaluations across providers and model versions;
11. Instruments trace handling;
12. accessibility and alternate input;
13. supported physical-device behavior;
14. signed archive and TestFlight;
15. App Store capability, privacy, and release review.

An agent trace, model capability value, image attachment, PCC session, custom provider compile, or dynamic profile is not proof that the user saw the correct result or that a domain action was authorized.

## Related local routes

- [Foundation Models production-route review](111-swiftui-foundation-models-production-route-review.md)
- [Advanced Foundation Models production-route design](../21-design-deep-dives/140-swiftui-foundation-models-advanced-provider-multimodal-route-review-design.md)
- [Advanced provider and multimodal capability route](../50-capability-recipes/143-swiftui-foundation-models-advanced-provider-multimodal-route-review-route.md)
- [Foundation Models production proof matrix](../60-verification/136-swiftui-foundation-models-production-route-review-proof-matrix.md)
- [Foundation Models production recipes](../70-code-recipes/154-swiftui-foundation-models-production-route-review-recipes.md)
- [Foundation Models native review and Liquid Glass design](../21-design-deep-dives/91-foundation-models-native-review-and-liquid-glass-design.md)
- [Core ML and Vision model lifecycle](../40-framework-routes/12-core-ml-vision-model-lifecycle-and-device-proof.md)
- [SwiftUI Apple Intelligence system surfaces](110-swiftui-apple-intelligence-system-surfaces-review.md)

## Sources

- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [LanguageModel](https://developer.apple.com/documentation/foundationmodels/languagemodel)
- [LanguageModelCapabilities](https://developer.apple.com/documentation/foundationmodels/languagemodelcapabilities)
- [LanguageModel capabilities](https://developer.apple.com/documentation/foundationmodels/languagemodelcapabilities/capability)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [PrivateCloudComputeLanguageModel](https://developer.apple.com/documentation/foundationmodels/privatecloudcomputelanguagemodel)
- [Private Cloud Compute](https://developer.apple.com/documentation/foundationmodels/adding-server-side-intelligence-with-private-cloud-compute)
- [Private Cloud Compute quota](https://developer.apple.com/documentation/foundationmodels/privatecloudcomputelanguagemodel/quotausage-swift.struct)
- [Composing dynamic sessions with instructions and profiles](https://developer.apple.com/documentation/foundationmodels/composing-dynamic-sessions-with-instructions-and-profiles)
- [DynamicInstructions](https://developer.apple.com/documentation/foundationmodels/dynamicinstructions)
- [LanguageModelSession.Profile](https://developer.apple.com/documentation/foundationmodels/languagemodelsession/profile)
- [Attachment](https://developer.apple.com/documentation/foundationmodels/attachment)
- [ImageReference](https://developer.apple.com/documentation/foundationmodels/imagereference)
- [Analyzing images with multimodal prompting](https://developer.apple.com/documentation/foundationmodels/analyzing-images-with-multimodal-prompting)
- [Expanding generation with tool calling](https://developer.apple.com/documentation/foundationmodels/expanding-generation-with-tool-calling)
- [LanguageModelExecutor](https://developer.apple.com/documentation/foundationmodels/languagemodelexecutor)
- [LanguageModelExecutorGenerationRequest](https://developer.apple.com/documentation/foundationmodels/languagemodelexecutorgenerationrequest)
- [LanguageModelExecutorGenerationChannel](https://developer.apple.com/documentation/foundationmodels/languagemodelexecutorgenerationchannel)
- [Evaluations](https://developer.apple.com/documentation/evaluations)
- [Evaluating language model responses](https://developer.apple.com/documentation/evaluations/evaluating-language-model-responses)
- [Analyzing the runtime performance of your Foundation Models app](https://developer.apple.com/documentation/foundationmodels/analyzing-the-runtime-performance-of-your-foundation-models-app)
- [Improving the safety of generative model output](https://developer.apple.com/documentation/foundationmodels/improving-the-safety-of-generative-model-output)
- [Generative AI HIG](https://developer.apple.com/design/human-interface-guidelines/generative-ai)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
