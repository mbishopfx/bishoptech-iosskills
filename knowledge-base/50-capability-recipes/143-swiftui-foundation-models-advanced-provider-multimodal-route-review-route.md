# Advanced Foundation Models provider and multimodal capability route

Use this route when an iOS app needs more than a single on-device text session: image understanding, dynamic tool sets, model-provider selection, Private Cloud Compute, custom local/server models, or a bounded agentic workflow. Start with the smallest provider and phase that satisfies the feature.

## Route decision table

| Requirement | First route | Escalation |
| --- | --- | --- |
| short local text task | SystemLanguageModel | deterministic fallback |
| finite image classification | SystemLanguageModel with Attachment and Generable | Vision/Core ML or PCC |
| OCR/barcode | OCRTool or BarcodeReaderTool | specialized Vision route |
| larger context or stronger reasoning | on-device evaluation first | Private Cloud Compute when available and approved |
| custom local model | LanguageModel provider backed by Core AI or another local package | system model or server fallback |
| external provider | LanguageModel provider package | on-device/private cloud fallback |
| tools change by workflow phase | DynamicInstructions/Profile | separate sessions if state is unrelated |
| multiple profiles and model handoff | DynamicProfile | explicit finite state machine |
| sensitive image or data | on-device first | approved provider only after disclosure and policy |
| consequential action | typed proposal | deterministic commit after approval |

## Phase 1: define the capability contract

Write the route in terms of input, provider, capability, output, and side effect:

> Given one user-selected image and a question, use a vision-capable model to propose a small typed observation. The person reviews it. The app validates it against the source and saves only after explicit approval.

Then list:

- source type and identity;
- image orientation and revision;
- provider candidates;
- required capabilities;
- maximum prompt and attachment size;
- tool set;
- history policy;
- output schema;
- user approval;
- fallback;
- privacy copy;
- evaluation criteria;
- physical-device and release proof.

If the contract cannot name the source or side effect, narrow it before adding a model.

## Phase 2: select a provider

Use a provider selection policy rather than a model name in view code:

1. check the task’s required capabilities;
2. check deployment and OS availability;
3. check device and region;
4. check Apple Intelligence/model readiness;
5. check PCC entitlement and quota if relevant;
6. check network or local model assets;
7. check privacy policy;
8. choose the least expensive or least external lane that meets the criteria;
9. expose the choice or data-flow message;
10. record provider label and capability set for evaluation.

### Provider record

| Field | Example |
| --- | --- |
| identifier | system-on-device |
| availability | ready, not-ready, unavailable |
| capabilities | vision, guidedGeneration, toolCalling |
| context size | current model property |
| data path | device, PCC, external |
| offline | yes or no |
| quota | none, approaching, reached |
| deployment | iOS 26 or later guarded branch |
| fallback | local deterministic route |

Do not treat PCC quota as availability. Do not treat a custom provider’s successful text response as proof that it supports vision, tools, or guided generation.

## Phase 3: capability negotiation

The selected model should expose its capabilities. Route before request:

| Capability check | If supported | If missing |
| --- | --- | --- |
| vision | attach the image | OCR/Vision/text fallback |
| guided generation | use Generable | plain draft or manual form |
| tool calling | supply narrow tools | no-tool route |
| reasoning | allow the reasoning route | simpler prompt or provider |

An unsupported capability should be a planned state in the UI, not a generic catch block. If the request needs multiple capabilities, require all of them or define a staged route.

## Phase 4: multimodal source preparation

Prepare the source deterministically:

1. obtain user permission through the owning framework;
2. choose the image or region;
3. verify that a file URL is an image;
4. preserve or deliberately transform orientation;
5. label the attachment;
6. keep source ID and revision;
7. remove unrelated metadata or pixels when policy requires;
8. build a short prompt;
9. use a typed output when the result has a finite shape;
10. show the source in the review UI.

The framework handles scaling and color conversions for supported image attachments. The app still owns source selection, permission, provenance, and the meaning of the output.

## Phase 5: add specialized image tools

Use a built-in or custom tool when the task needs current or exact image data:

| Task | Tool route |
| --- | --- |
| read text | OCRTool or Vision text recognition |
| scan barcode | BarcodeReaderTool |
| classify with app model | custom tool using ImageReference and Core ML/Vision |
| read document fields | OCR plus typed validation |
| compare image regions | labeled attachments and bounded prompt |
| edit pixels | model proposal plus deterministic Core Image/Metal pipeline |

The model should receive the smallest useful tool output. Include source and confidence metadata when the UI or evaluator needs it.

## Phase 6: dynamic instructions

Create one DynamicInstructions unit per independently testable concern:

- base safety and role;
- image inspection tools;
- inventory search;
- draft action proposal;
- review-only mode;
- provider privacy notice;
- session history projection.

The body evaluates before every model request. Keep branches deterministic and append stable sections in a cache-friendly order:

1. trusted base instructions;
2. stable schema or output policy;
3. phase-specific instructions;
4. phase-specific tools;
5. current prompt and attachments.

Do not include user or imported content in trusted Instructions. Place it in the Prompt with explicit delimiters.

## Phase 7: profiles and handoff

Model a profile as a named workflow phase:

| Profile | Model | Tools | History | Approval |
| --- | --- | --- | --- | --- |
| inspect | on-device | OCR, barcode | current attachment | none |
| classify | on-device | none | current attachment | review label |
| enrich | PCC or approved provider | read-only search | compact summary | review sources |
| plan | capable provider | read-only app tools | recent decisions | review plan |
| approve | typed proposal model | no writes | proposal and source revision | explicit |
| commit | no model required | deterministic app service | domain state | app operation |

Use DynamicProfile when one session must move through these profiles. Use separate sessions when the data or conversation should not cross a boundary.

At every handoff:

- copy only the approved context;
- check provider capabilities;
- check privacy and entitlement;
- revalidate source revision;
- reset or transform history;
- show the phase change;
- keep cancellation;
- record the handoff in evaluation metadata.

## Phase 8: history and caching

Use historyTransform to supply a phase-specific view of the transcript. Examples:

- image inspection needs the image attachment and current question;
- planning needs recent tool outputs and user decisions;
- approval needs the current proposal, source revision, and no unrelated history;
- a larger-context provider may accept more history only after privacy review.

When dynamic instructions change, preserve stable prefixes where caching can help. Use the Foundation Models Instrument to verify cache hits, token counts, model-loading time, tool duration, and time to first token.

Do not call a cache hit a semantic guarantee. Caching is a performance property.

## Phase 9: agentic tool loop

Use a bounded loop:

1. start with a user-visible task;
2. choose an active profile;
3. ask the model for the next response;
4. permit only the active tools;
5. validate every tool argument;
6. run reads concurrently when safe;
7. return compact results;
8. update deterministic app state;
9. stop on completion, error, cancellation, limit, or approval;
10. commit through app code.

Required tool-calling mode needs a defined exit condition. A tool can throw or a dynamic profile can change the mode; design the loop so it cannot call forever.

Tool boundaries:

- read tools should not write;
- write tools should create proposals when possible;
- idempotency keys should protect retries;
- authorization must be checked at execution time;
- current records and revisions must be re-read before commit;
- sensitive tool outputs should not be copied to a provider without policy;
- a tool result is a source result, not domain permission.

## Phase 10: PCC route

PCC is an optional escalation:

1. evaluate the on-device route;
2. identify the specific failure: context, reasoning, or quality;
3. check the OS availability branch;
4. verify managed entitlement/eligibility;
5. inspect quota state;
6. explain the data path;
7. route only the approved prompt and attachments;
8. show quota and retry state;
9. fall back when unavailable, offline, or over quota;
10. evaluate PCC outputs separately from on-device outputs.

Do not use PCC simply because the UI label “AI” exists. The higher-capability route may be inappropriate for a private/local-first feature or a task that works on device.

## Phase 11: custom provider route

For a custom provider:

- package the provider with Swift Package Manager;
- keep the LanguageModel type light and Sendable;
- declare capabilities accurately;
- implement an executor that owns provider work;
- translate Instructions, Prompt, tools, history, and generation options;
- stream output and metadata through the generation channel;
- support cancellation and errors;
- define authentication and secrets;
- document platform support;
- test custom segments and metadata if used;
- archive and install the provider in the real app target.

Provider integration proof must include a test of the same session request through the selected provider and through the fallback. A mock provider proves app routing but not provider behavior.

## Phase 12: typed multimodal result

Use a small schema:

| Field | UI | Validation |
| --- | --- | --- |
| label enum | Picker or review row | allowed enum |
| extracted text | editable TextEditor | source comparison and length |
| confidence band | secondary status | not a guarantee |
| source region | thumbnail or crop | source revision |
| suggested action | action card | authorization and approval |

The schema should not contain the full domain object or hidden database fields. Validate semantics after decoding.

## Phase 13: evaluation across providers

Use one dataset with provider-specific expectations:

- on-device short context;
- on-device no-network;
- PCC larger context;
- PCC quota near/reached;
- custom local model assets ready/not ready;
- server provider network failure;
- image orientation and crop;
- OCR/barcode source truth;
- adversarial attachment labels;
- dynamic profile transition;
- tool repeat and parallel calls;
- cancellation at every phase;
- approval denial and stale revision.

Measure:

- task completion;
- semantic validation;
- source fidelity;
- unwanted tool calls;
- provider handoff;
- latency;
- token and cache use;
- quota behavior;
- privacy/logging;
- accessibility;
- fallback completion.

The provider with the best average response is not enough if it fails a zero-tolerance safety or authorization criterion.

## Phase 14: native SwiftUI shell

Compose the screen as:

1. source selection;
2. task input;
3. provider/status row;
4. active phase;
5. result/proposal;
6. tool and source disclosure;
7. approval;
8. fallback.

Use Liquid Glass only for the action and phase groups. Keep the image and result legible. Use a system sheet or confirmation surface for external data-flow and side effects.

## Phase 15: evidence

The route is ready for implementation when the brief includes:

- provider matrix;
- capabilities;
- OS and entitlement gates;
- attachment/source policy;
- dynamic profile map;
- history transform;
- tool loop and exit;
- typed result and validator;
- approval and commit;
- evaluation fixtures;
- privacy copy;
- accessibility plan;
- fallback;
- physical-device test;
- archive/TestFlight/App Store proof.

## Related local routes

- [Advanced provider and multimodal deep dive](../42-framework-deep-dives/112-swiftui-foundation-models-advanced-provider-multimodal-route-review.md)
- [Advanced provider and multimodal design](../21-design-deep-dives/140-swiftui-foundation-models-advanced-provider-multimodal-route-review-design.md)
- [Foundation Models production route](142-swiftui-foundation-models-production-route-review-route.md)
- [Foundation Models production proof matrix](../60-verification/136-swiftui-foundation-models-production-route-review-proof-matrix.md)
- [Foundation Models production recipes](../70-code-recipes/154-swiftui-foundation-models-production-route-review-recipes.md)
- [PhotosPicker and media-source route](../50-capability-recipes/133-swiftui-photospicker-photokit-imageio-live-photo-source-review-route.md)
- [Core ML/Vision model lifecycle route](../40-framework-routes/12-core-ml-vision-model-lifecycle-and-device-proof.md)
- [Tool approval and App Intents](../31-on-device-ai-recipes/07-tool-approval-and-app-intents.md)

## Sources

- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [LanguageModel](https://developer.apple.com/documentation/foundationmodels/languagemodel)
- [LanguageModelCapabilities](https://developer.apple.com/documentation/foundationmodels/languagemodelcapabilities)
- [Private Cloud Compute](https://developer.apple.com/documentation/foundationmodels/adding-server-side-intelligence-with-private-cloud-compute)
- [PrivateCloudComputeLanguageModel](https://developer.apple.com/documentation/foundationmodels/privatecloudcomputelanguagemodel)
- [Private Cloud Compute quota](https://developer.apple.com/documentation/foundationmodels/privatecloudcomputelanguagemodel/quotausage-swift.struct)
- [Composing dynamic sessions with instructions and profiles](https://developer.apple.com/documentation/foundationmodels/composing-dynamic-sessions-with-instructions-and-profiles)
- [DynamicInstructions](https://developer.apple.com/documentation/foundationmodels/dynamicinstructions)
- [LanguageModelSession.Profile](https://developer.apple.com/documentation/foundationmodels/languagemodelsession/profile)
- [Attachment](https://developer.apple.com/documentation/foundationmodels/attachment)
- [ImageReference](https://developer.apple.com/documentation/foundationmodels/imagereference)
- [Analyzing images with multimodal prompting](https://developer.apple.com/documentation/foundationmodels/analyzing-images-with-multimodal-prompting)
- [Expanding generation with tool calling](https://developer.apple.com/documentation/foundationmodels/expanding-generation-with-tool-calling)
- [Evaluations](https://developer.apple.com/documentation/evaluations)
- [Evaluating language model responses](https://developer.apple.com/documentation/evaluations/evaluating-language-model-responses)
- [Analyzing the runtime performance of your Foundation Models app](https://developer.apple.com/documentation/foundationmodels/analyzing-the-runtime-performance-of-your-foundation-models-app)
- [Improving the safety of generative model output](https://developer.apple.com/documentation/foundationmodels/improving-the-safety-of-generative-model-output)
- [Generative AI HIG](https://developer.apple.com/design/human-interface-guidelines/generative-ai)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
