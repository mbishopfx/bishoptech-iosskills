# SwiftUI Foundation Models production route

Use this route when an iOS 26 idea needs on-device language understanding, a typed suggestion, a reviewable draft, or a narrowly scoped tool-assisted action. The route is intentionally staged. Each stage produces an artifact and a proof question before the next stage is allowed to add complexity.

## Route map

| Stage | Decision | Primary artifact | Stop condition |
| --- | --- | --- | --- |
| 0. task shape | Is the job model-shaped? | one-sentence task contract | deterministic code or a specialized framework is better |
| 1. availability | Can this target run the model lane? | availability matrix and fallback | no honest fallback for unavailable states |
| 2. session | Is this one turn or a continuing context? | session ownership plan | multiple owners or hidden transcript state |
| 3. prompt | What is the minimum useful context? | versioned PromptBuilder fixture | prompt mixes instructions and untrusted data |
| 4. budget | What consumes context? | token/context measurement | context exceeds budget or has no recovery |
| 5. output | Text, stream, typed candidate, or dynamic schema? | output contract | output is treated as domain truth |
| 6. tools | Does the task need current data or an action? | Tool policy and approval rule | write tool has no authorization or exit condition |
| 7. UI | How will the person review, cancel, and recover? | SwiftUI state machine | spinner or glass effect hides uncertainty |
| 8. evaluation | Which fixtures and model versions matter? | evaluation record | only one happy-path sample |
| 9. proof | What real device and release evidence is required? | proof matrix and signed artifact | compile or simulator is treated as release proof |

## Stage 0: write the task contract

Start with a narrow statement:

> Given selected source material, propose a concise, editable result that the person may review and apply.

Then define:

- input source and maximum size;
- whether input is private, user-authored, imported, or network-provided;
- whether the answer must be current;
- whether the answer must be exact;
- acceptable uncertainty;
- output type;
- user approval boundary;
- domain operation after approval;
- fallback when the model is unavailable.

If the task says “manage my data” or “do anything the user asks,” split it into separate routes. A model session is easier to evaluate when its prompt, schema, tools, and side effects are narrow.

## Stage 1: availability and model version

Create a model capability object at the boundary of the feature:

| Signal | Route decision |
| --- | --- |
| SystemLanguageModel availability is available | the feature may offer the model route |
| Apple Intelligence is not enabled | explain the dependency and show fallback |
| device is not eligible | keep the core workflow usable without the model |
| model is not ready | retry later; do not create a fake success state |
| OS/model version changed | rerun fixtures and compare prompt behavior |

Record the following in development diagnostics:

- device model and OS;
- SDK and deployment target;
- Apple Intelligence state;
- model availability and use case;
- prompt version;
- schema version;
- tool set;
- whether the response was streamed;
- measured token and latency data.

Do not display internal diagnostics by default, but keep enough metadata to reproduce a fixture result without retaining private user content.

## Stage 2: choose session topology

### Single-turn route

Use a fresh session for a bounded action such as:

- summarize selected text;
- classify one item;
- draft a title;
- extract a small set of fields.

The benefit is a small context and a simple lifecycle. Do not add transcript persistence just because the framework exposes a transcript.

### Multi-turn route

Reuse one session only when the product actually needs conversation continuity. Define:

- what instructions remain stable;
- which entries can be removed;
- how the session is reset;
- when a compact app-owned summary replaces history;
- whether the transcript is visible to the person;
- whether attached data may be rehydrated;
- how the model version and prompt version are recorded.

### Multiple independent tasks

Use separate sessions for unrelated tasks. Never multiplex unrelated user flows through a single mutable session. A session cannot be a global singleton that every screen calls concurrently.

## Stage 3: prompt construction

Use a short instruction plus a dynamic prompt:

1. state the role and output goal;
2. state the relevant constraints;
3. identify the source;
4. delimit user or imported content;
5. ask for the smallest useful response;
6. choose a typed schema or tool when the contract needs it.

PromptBuilder is useful for conditional sections:

| App state | Include |
| --- | --- |
| no selection | ask for a selection or show fallback |
| one selection | source plus task instruction |
| user chose concise | concise output constraint |
| user chose formal | tone constraint |
| external data available | source and freshness, not hidden credentials |
| output requires action | ask for a proposal, not an unreviewed commit |

Do not hide a secret or authorization rule in a prompt. The actual authorization check belongs in deterministic app code.

## Stage 4: context budget

Make a budget sheet before adding tools or schemas:

| Item | Target policy |
| --- | --- |
| instructions | fixed and short |
| current prompt | only selected input |
| imported content | trim or summarize before the model |
| schema | minimum fields and bounded collections |
| tools | only tools needed for this task |
| output | reasonable maximum when necessary |
| history | compacted or reset when no longer useful |

Measure:

- prompt token count;
- instructions token count;
- schema and tool overhead;
- session transcript token count;
- response token count;
- time to first partial result;
- total response latency.

Use the current context-size property and token-counting API in the selected SDK. The documented on-device baseline of 4,096 tokens is a planning reference, not permission to append 4,096 tokens of user data without measuring the other contributors.

Recovery order for context exhaustion:

1. remove irrelevant entries;
2. shorten or summarize the source using deterministic rules where possible;
3. create a fresh session;
4. reduce schema and tool surface;
5. split the task;
6. use a different model lane only after privacy and product review.

## Stage 5: output contract

Choose the least powerful contract that satisfies the product:

### Plain draft

Use a string response for editable language. Keep it visibly provisional and give the person an edit path.

### Streaming draft

Use streamResponse when first-result latency or progressive display matters. Accumulate in view state, not the domain store. The final response still needs validation.

### Guided typed proposal

Use Generable and Guide for a small, user-reviewable shape. Examples include:

- a title and three tags;
- a finite category and short reason;
- a set of suggested edits;
- a small list of reminders;
- a draft action with a target identifier that is revalidated by the app.

### Dynamic structured output

Use GeneratedContent or DynamicGenerationSchema only when the shape is genuinely runtime-defined. Keep schema construction errors visible in development and provide a fallback.

## Stage 6: tool route

Add a tool only when model-generated language alone cannot satisfy the task:

| Need | Tool type | Approval |
| --- | --- | --- |
| current weather or app state | read-only | normally no write approval, still privacy-reviewed |
| search a user-owned collection | bounded read | show scope and source when sensitive |
| calculate or validate | deterministic service | model receives result, not authority |
| create or edit a record | write | explicit confirmation and revalidation |
| send, purchase, delete, publish | consequential write | strong confirmation, undo or recovery |

Tool definitions should be few and descriptive. Arguments should decode into a narrow type. Tool output should be compact and contain no secrets. Design for parallel calls and repeated calls; do not rely on call order unless the route enforces it.

Use tool-calling modes intentionally:

- allowed when a tool is optional;
- required when current data is necessary, with a defined exit condition;
- disallowed for a safe generative fallback.

The tool callback may return a result, but the domain layer still owns authorization and commit. For a write route, the first tool call should often create a proposal or validation result rather than immediately mutate the database.

## Stage 7: SwiftUI state and Liquid Glass shell

Represent the route as a finite state machine:

| View state | Data |
| --- | --- |
| unavailable | reason and fallback action |
| ready | source selection and task |
| generating | request ID, phase, partial text |
| candidate | typed or textual result plus validation |
| approval | operation summary and authorization scope |
| committing | deterministic operation progress |
| complete | committed record and undo |
| error | typed error, retry, fallback |

Use standard controls first. Add Liquid Glass to:

- the action cluster;
- the review toolbar;
- the approval controls;
- the compact status treatment.

Keep the source, output, and approval relationship visible. Do not place the only cancel action inside a context menu. Do not make a partial model response look like a final card through color or animation.

## Stage 8: evaluation route

Create a fixture table with columns:

| Field | Example |
| --- | --- |
| fixture ID | selected-text-short-01 |
| task | summarize |
| input class | normal, empty, long, adversarial |
| prompt version | summarize-v2 |
| schema version | none or suggestion-v1 |
| model/OS | device and update |
| expected properties | concise, no new facts, editable |
| tool expectation | no tool |
| result | pass, fail, needs review |
| evidence | sanitized output and metrics |

For each new OS or model version, rerun the fixture set. Compare:

- schema decode rate;
- semantic validation rate;
- refusal and guardrail rate;
- unwanted tool-call rate;
- average and tail latency;
- context usage;
- cancellation behavior;
- privacy and logging behavior.

Use model output as evidence for evaluation, not as a hidden test oracle. Keep exact expected values in deterministic fixtures when the task requires them.

## Stage 9: proof and release route

Run the route in this order:

1. compile the named app target with the selected SDK;
2. run unit tests for prompt construction, schema validation, tool authorization, and domain commit;
3. run UI tests for unavailable, generating, cancelled, candidate, approval, and error states;
4. run on a supported physical device with Apple Intelligence enabled;
5. run the fallback with model availability unavailable;
6. test a model-not-ready state and retry;
7. test context exhaustion with a controlled fixture;
8. test tool denial, tool failure, repeated call, and cancellation;
9. inspect VoiceOver, Dynamic Type, reduced motion, keyboard, pointer, and localization;
10. inspect logs and transcript retention for private content;
11. archive, install the signed artifact, and exercise the feature;
12. install through TestFlight and repeat the real user flow;
13. record App Store capability, privacy, metadata, and review notes.

## Reusable route patterns

### Pattern A: summarize selected text

Input: user-selected text. Output: editable plain text or a small typed summary. Tools: none. Approval: accept or dismiss. Fallback: standard copy/edit flow.

Proof focus: selection boundaries, long text trimming, streaming cancellation, no accidental persistence, accessibility status, and model-version comparison.

### Pattern B: classify a local record

Input: one record and a finite label set. Output: Generable enum plus short reason. Tools: none or deterministic local lookup. Approval: user applies label. Fallback: manual picker.

Proof focus: allowed values, semantic validation, record identity re-check, undo, and no commit from a partial response.

### Pattern C: search then propose

Input: user request. Tools: read-only search. Output: typed list of candidates. Approval: user selects one. Domain action: deterministic commit after revalidation.

Proof focus: tool arguments, source freshness, empty results, parallel calls, prompt injection in imported content, and privacy of search scope.

### Pattern D: create a draft action

Input: selected app data. Output: typed action proposal. Tools: optional read-only enrichment, then a write only after approval. Approval: action-specific confirmation. Fallback: manual editor.

Proof focus: affected records, authorization, conflicts, retries, idempotency, cancellation, and undo.

## Handoff artifact

Before implementation, write one small route brief:

- feature name;
- selected target and deployment;
- model lane and availability states;
- session topology;
- prompt version;
- schema and tool list;
- context budget;
- user approval point;
- deterministic commit function;
- fallback;
- privacy and retention;
- accessibility;
- fixture IDs;
- physical-device and release evidence.

If the brief cannot name the deterministic commit function, the feature is still a model experiment.

## Related local routes

- [Foundation Models production-route review](../42-framework-deep-dives/111-swiftui-foundation-models-production-route-review.md)
- [Foundation Models production-route design](../21-design-deep-dives/139-swiftui-foundation-models-production-route-review-design.md)
- [Foundation Models tool and structured-output route](94-foundation-models-tool-and-structured-output-route.md)
- [Prompt evaluation and model-update recipe](../31-on-device-ai-recipes/09-prompt-evaluation-and-model-update-recipe.md)
- [Tool approval and App Intents](../31-on-device-ai-recipes/07-tool-approval-and-app-intents.md)
- [AI evaluation and safety checklist](../60-verification/03-ai-evaluation-and-safety-checklist.md)
- [Build, device, and release checklist](../60-verification/01-build-device-and-release-checklist.md)
- [App Intent transfer and execution route](97-app-intents-transfer-ownership-and-execution-route.md)

## Sources

- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [SystemLanguageModel availability](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel/availability-swift.property)
- [SystemLanguageModel unavailable reasons](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel/availability-swift.enum/unavailablereason)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Prompt](https://developer.apple.com/documentation/foundationmodels/prompt)
- [Managing the context window](https://developer.apple.com/documentation/foundationmodels/managing-the-context-window)
- [GenerationOptions](https://developer.apple.com/documentation/foundationmodels/generationoptions)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
- [GenerationGuide](https://developer.apple.com/documentation/foundationmodels/generationguide)
- [Tool](https://developer.apple.com/documentation/foundationmodels/tool)
- [Expanding generation with tool calling](https://developer.apple.com/documentation/foundationmodels/expanding-generation-with-tool-calling)
- [Foundation Models updates](https://developer.apple.com/documentation/updates/foundationmodels)
- [Generative AI HIG](https://developer.apple.com/design/human-interface-guidelines/generative-ai)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
