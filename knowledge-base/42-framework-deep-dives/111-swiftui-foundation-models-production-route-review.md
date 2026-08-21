# SwiftUI Foundation Models production-route review

Status: active iOS 26 reference. This page is a production lifecycle review, not a dump of every Foundation Models symbol. The framework is evolving, the on-device model can change in routine operating-system updates, and beta documentation is not a promise that an API or behavior is frozen. Re-open the current Apple pages, compile against the selected SDK, and record the target and model version used by every experiment.

The useful boundary is:

SystemLanguageModel tells the app whether a model lane is eligible and ready. LanguageModelSession owns one evolving interaction context. Prompt and PromptBuilder describe the next request. A transcript records the interaction. Guided generation shapes a typed proposal. A tool can obtain current app data or perform an operation. SwiftUI presents state and asks for human confirmation. The app’s deterministic domain layer validates and commits the approved action.

That boundary keeps a fluent model response from becoming an accidental database write.

## Route in one sentence

Check availability, choose the narrowest task, own one session in one concurrency domain, keep prompts and schemas within a measured context budget, stream into reviewable state, validate typed output, gate tools and side effects, expose cancellation and fallback, evaluate against fixtures and model versions, then prove the real device, privacy, accessibility, signed artifact, TestFlight, and App Store paths.

## What is covered here

- on-device model availability, device eligibility, Apple Intelligence state, model readiness, and version changes;
- single-turn and multi-turn LanguageModelSession ownership;
- Prompt and PromptBuilder composition, untrusted input boundaries, token budgets, and context-window recovery;
- transcript visibility, rehydration, error-time mutation policy, and tool-call history;
- plain-text responses, streaming snapshots, guided generation, Generable, Guide, and dynamic schemas;
- tool declarations, arguments, outputs, parallel calls, tool-calling modes, idempotency, and approval;
- prewarming and Instruments-based performance work;
- cancellation, concurrent-request prevention, actor isolation, and UI lifecycle;
- prompt/model evaluation, feedback attachments, guardrails, refusals, and model-version drift;
- native SwiftUI and Liquid Glass controls for AI states;
- accessibility, privacy, device, archive, TestFlight, and release evidence.

It deliberately does not turn a model response, transcript, typed value, tool callback, simulator run, or archive into domain truth by itself.

## The Foundation Models mental model

### 1. The model lane is a capability with gates

The default SystemLanguageModel represents the on-device text foundation model that powers Apple Intelligence. Its availability is not equivalent to “the app compiled” or “the device has a neural engine.” The current API exposes an availability state with an available case and unavailable reasons such as Apple Intelligence not being enabled, a device that is not eligible, or model assets that are not ready.

The UI should translate those states into honest next actions:

| State | Meaning for the route | UI and fallback |
| --- | --- | --- |
| available | The system reports that requests may be made | Enable the feature and keep deterministic fallbacks available |
| Apple Intelligence not enabled | The user has not enabled the system capability | Explain the dependency without pretending the app can enable it |
| device not eligible | The current device cannot run the requested model lane | Keep the core feature usable or provide an explicit non-model route |
| model not ready | Assets may still be downloading or the system is otherwise preparing | Show a retry/later state; do not spin indefinitely |
| another unavailable reason | The current SDK may add or refine cases | Preserve a generic fallback and log a non-sensitive diagnostic |

Use the current availability value at the point where a request begins. A cached “available” result can become stale after settings, model downloads, memory pressure, or an OS update. Availability is a gate, not a quality score and not a guarantee that a particular prompt will succeed.

### 2. Model versions are part of the experiment

Apple periodically updates SystemLanguageModel in operating-system updates. The current documentation describes model versions aligned to iOS 26.0 through 26.3, iOS 26.4, and iOS 27.0 across the supported platforms. A project whose deployment target is iOS 26 still needs to distinguish:

- the SDK used to compile the binary;
- the minimum OS on which the binary runs;
- the OS version and model version on the test device;
- whether Apple Intelligence is enabled;
- whether model assets are ready;
- the prompt and schema variant used by that build.

Do not silently assume that a prompt that worked on one model version will produce the same structure, refusal, tool choice, or wording on another. Maintain a small prompt-version policy. Check newer versions first when using availability-based prompt selection, and retain a tested fallback for older supported versions. Store prompt variants as source-controlled resources or string-catalog entries when localization or versioning benefits from that representation.

The app can own a prompt version identifier in its evaluation record. That identifier is an experiment label, not a claim that the model itself is pinned forever.

### 3. A session is mutable interaction state

LanguageModelSession represents one context and maintains state between requests. A new session is appropriate for a bounded single turn. Reusing a session is appropriate when prior instructions, prompts, responses, and tool activity are genuinely part of the next turn.

Session policy:

1. Create a session only after the model lane is eligible for the task.
2. Give it short, stable instructions that define role and output expectations.
3. Keep the session owned by one explicit concurrency domain.
4. Prevent concurrent requests against the same session.
5. Do not mutate its transcript while a request is in flight.
6. Recreate or compact the context when the task no longer needs its full history.
7. Persist only the transcript or task state that the product actually needs and is allowed to retain.

A session is not a repository, an authorization object, a source of truth, or a durable conversation database. It is an inference context. The product record should remain independently modeled.

### 4. Prompts are structured input, not a string concatenation contest

Prompt can be created from a literal or assembled with PromptBuilder. Dynamic prompts are useful when app state determines which instructions or data sections are relevant. Keep boundaries visible:

- identify task instructions separately from user-provided material;
- label imported text, OCR, document excerpts, and network content as data;
- avoid asking the model to reinterpret hidden developer policy from untrusted input;
- include only the context needed for this turn;
- give short, concrete output instructions;
- use a schema or a tool when exact shape or current data matters;
- treat prompt strings as versioned behavior.

PromptBuilder controls whether conditional content is present; it does not sanitize malicious or misleading content inserted into a selected branch. The app still owns data provenance, redaction, and privacy decisions.

### 5. The context window is a shared budget

Every instruction, prompt, tool definition, Generable schema, and model response contributes to the session context. The on-device model’s commonly documented context size is 4,096 tokens, while the current API exposes model context-size information and token-counting APIs for measuring the actual route. Do not hard-code a comfortable budget from an old sample and call it safe across model updates.

Budget the whole interaction:

| Contributor | Why it costs context | Design response |
| --- | --- | --- |
| instructions | repeated role and policy text | make them stable and compact |
| prompt | current task and user input | include only the necessary slice |
| tool definitions | names, descriptions, argument schemas | expose few, narrow tools |
| Generable schema | typed output contract and descriptions | keep fields short and useful |
| prior responses | multi-turn history | summarize or restart when history is no longer needed |
| tool calls/results | current data and execution history | return compact, typed results |
| long output | response itself remains in context | bound output only when a safe cap helps |

Use tokenCount(for:) and contextSize where available in the selected SDK. Measure prompt, instructions, and the entire session separately during development. A maximum response-token limit is a safety rail for unexpectedly verbose output, not a substitute for good prompt design; a strict cap can produce malformed typed output or incomplete prose.

When contextSizeExceeded occurs, do not append more text and retry the same session blindly. Decide whether to:

- remove entries that the task does not need;
- create a new session with a compact, app-authored summary;
- narrow the request;
- split the workflow into deterministic stages;
- move the task to a different model lane only when the product and privacy policy allow it.

The summary should be an app-owned projection of the task, not an unreviewed model response treated as permanent memory.

### 6. A transcript is history, not truth

Transcript is a linear history of session entries. It can contain instructions, prompts, model responses, and, when tools are used, tool calls and tool results. It is useful for debug visualization, review, controlled rehydration, and context management.

Transcript rules:

- display provenance when showing model or tool content;
- do not use a transcript entry as proof that the user approved an action;
- do not treat a generated response as a committed domain record;
- avoid persisting sensitive raw entries unless the user-facing feature requires it;
- do not mutate the transcript while a request is responding;
- when rehydrating, verify that the entries belong to the current task, prompt policy, and app version;
- test whether attached images/files or structured segments are safe to retain before storing them.

Rehydrating a transcript can make a new session continue from prior context. It does not reproduce the original device state, tool data, model version, network response, user identity, or side effects. Revalidate all of those.

### 7. Plain text, streaming, and typed output have different contracts

Plain text is appropriate for low-risk draft language where the user can inspect and edit. A streaming response is an asynchronous sequence of partial snapshots; it is a presentation mechanism and latency tool, not a stream of committed records.

Guided generation is appropriate when the app needs a typed proposal. Generable types become schemas, and Guide can constrain values or describe fields. A typed result proves that the framework produced a value matching the declared shape; it does not prove that the values are correct, current, authorized, safe, or semantically appropriate.

Treat output as a ladder:

1. model text or partial snapshot;
2. decoded typed candidate;
3. app validation and normalization;
4. user review or explicit approval when consequential;
5. deterministic domain operation;
6. persisted result with audit metadata.

Never jump from step 1 or 2 to step 6 for destructive, financial, medical, legal, messaging, permission, or externally visible actions.

### 8. Schema design is prompt and latency design

Every Generable type adds schema material to the context. Favor:

- a small number of fields;
- short property names only when readability is not harmed;
- concise descriptions;
- bounded collections;
- enums for finite choices;
- nested types only when the product needs the nesting;
- a schema that describes a proposal rather than the entire domain object.

Use Guide to constrain values that the model can reasonably select. Do not use a Guide as a database constraint or permission check. The model can still be wrong within the allowed range, and a schema can be too complex for the context or model. DynamicGenerationSchema is useful for runtime-defined shapes, but schema construction can fail for conflicting names, duplicate types, or undefined references; surface those failures as developer diagnostics and keep a deterministic fallback.

Set includeSchemaInPrompt deliberately. Including a schema can bias the model toward the expected format; it also consumes context. Measure the tradeoff with the exact target model and prompt.

### 9. Tools bridge model reasoning to current app state

The Tool protocol gives a model a named capability with a description, generated arguments, and an async call that returns prompt-representable output. A tool can gather current data or perform an operation. Tool definitions and their argument/result material add context, and the model may call a tool more than once or call multiple tools in parallel.

Tool policy:

- name tools after user-visible capabilities, not internal methods;
- describe inputs and limits precisely;
- keep tool arguments narrow and validated;
- return the smallest useful result;
- make read tools side-effect free;
- make write tools idempotent where possible;
- treat tool calls as untrusted requests;
- require approval before consequential writes;
- make authorization and current-user checks deterministic;
- avoid exposing secrets, arbitrary file access, raw database queries, or unrestricted network operations;
- design for parallel calls and repeated calls;
- return a structured failure that lets the session exit or ask for clarification.

GenerationOptions can control tool-calling mode. Allowed is a normal route when the model may decide whether a tool is useful. Required is a route for tasks that must obtain current data, but it needs an exit condition or the model may keep calling. Disallowed is a useful fallback when the task should remain purely generative.

The tool itself may perform work, but the app should separate “the model requested this tool” from “the user authorized this action” and “the domain commit succeeded.” A successful tool callback is evidence about that callback only.

### 10. Prewarming is a latency hint, not readiness

LanguageModelSession prewarm asks the system to load resources ahead of a request and can optionally cache a prompt prefix. Apple’s documentation positions it for a strong signal that the user will interact within a few seconds, with at least about one second before respond or streamResponse. Prewarming does not guarantee immediate asset loading, especially under background execution or system load.

Good prewarm moments:

- the user opens a focused AI composer;
- the user begins typing after a clear affordance;
- a deterministic screen transition predicts an imminent request.

Bad prewarm moments:

- app launch with no user intent;
- every keystroke;
- background loops;
- a screen that may never use AI;
- while treating prewarm completion as model availability.

Use Instruments to measure whether prewarming reduces the latency that matters to the user. Do not add it before the route has a measured prediction window.

## Concurrency and lifecycle ownership

### One session, one request at a time

The framework reports session misuse such as concurrent requests and transcript mutation while responding. The simplest safe pattern is to keep all session calls behind one coordinator, actor, or main-actor view model and expose intent methods such as start, cancel, retry, and approve. The exact Sendable and isolation annotations can evolve; let the selected SDK and compiler decide what can cross actors.

A coordinator should own:

- availability snapshot;
- session instance;
- request task;
- request identifier;
- phase;
- partial output;
- last typed candidate;
- pending tool approval;
- error and fallback state.

The view should render that state and send user intents. It should not call the same session from multiple buttons, task modifiers, and event handlers independently.

### Cancellation is a product state

Cancellation can happen because the user taps Stop, the view disappears, a new prompt supersedes the old one, the task times out, or the app enters a state where the result is no longer wanted. Wire Task cancellation through the async response or stream, stop rendering stale partial output, and do not commit a candidate after cancellation.

Use a request identifier or generation token to prevent a late result from an earlier task replacing a newer state. Reset or preserve the transcript deliberately. A cancelled visual stream is not automatically a failed product operation, and a task that returns after the user navigated away is not permission to mutate the old screen.

### Long-running tools and approval

Tool calls can be asynchronous and may outlive a quick view interaction. Keep durable work in an app service with explicit authorization and cancellation. If a tool needs approval, model the approval as a first-class state with a summary of the proposed operation, affected records, data sharing, and reversible options. After approval, re-check user identity, current state, authorization, and conflicts before commit.

## Capability and limitation routing

Foundation Models is well suited to bounded language understanding, extraction, classification, transformation, summarization, and creative text tasks that can tolerate probabilistic output. Use deterministic code, database queries, domain validators, and specialized Apple frameworks for exact arithmetic, authorization, durable state, source-of-truth lookups, media processing, and safety-critical decisions.

For image understanding or OCR-like tasks, combine an image prompt with a specialized Vision tool or framework capability when appropriate. Do not assume a text model has current world knowledge, arbitrary code execution, reliable logical reasoning, or exact computation because it can produce fluent text.

Route by the output contract:

| Need | Primary route | Review boundary |
| --- | --- | --- |
| draft language | Prompt plus plain response | user edits or accepts |
| incremental text | streamResponse | partial snapshots never commit |
| finite recommendation | Generable enum or bounded values | app validation and review |
| current app data | read Tool | deterministic data source |
| user-visible write | write Tool or app action | explicit confirmation and revalidation |
| dynamic but controlled structure | GeneratedContent or DynamicGenerationSchema | schema and semantic validation |
| exact calculation | Swift/Foundation/domain code | model may explain, never calculate authority |
| system shortcut/action | App Intents | supported-mode and target proof |

## Prompt and model evaluation

### Build a fixture, not a vibe

Every production prompt should have a small fixture set with:

- representative inputs;
- empty, very long, malformed, and adversarial inputs;
- supported languages and locales;
- sensitive-content cases;
- expected structural properties;
- tool-use expectations;
- refusal and fallback expectations;
- a prompt version;
- OS, SDK, device, model version, and availability state.

For typed output, assert schema decoding, required-field presence, allowed values, bounds, and semantic validation. For text, assert properties rather than one exact sentence unless exact wording is a product requirement. For tools, assert whether a tool should be called, arguments, authorization, idempotency, and final domain state.

### Compare model versions intentionally

When the OS updates the on-device model:

1. run the existing fixture set against the new device;
2. record old and new outputs plus prompt and model labels;
3. compare structure, refusal, tool calls, latency, token use, and semantic checks;
4. decide whether the prompt needs a versioned adjustment;
5. preserve the previous fixture results as evidence;
6. repeat on the oldest supported OS/model combination.

Do not “fix” a model update by adding verbose prompt text until token cost and the new behavior are measured. A shorter prompt with a narrower typed schema or deterministic tool may be more robust.

Use Feedback Assistant attachments only under a deliberate privacy policy. A feedback attachment can include interaction context; do not export sensitive user material accidentally.

### Evaluate failure as a first-class output

Test at least:

- Apple Intelligence disabled;
- device ineligible;
- model assets not ready;
- context size exceeded;
- refusal or guardrail violation;
- rate limiting or timeout;
- unsupported language or locale;
- decoding failure;
- unsupported guide;
- concurrent request;
- tool failure;
- user cancellation;
- view disappearance;
- OS/model update;
- low memory or interrupted execution.

Every failure should have a readable UI state, a deterministic fallback or retry path, and a privacy-preserving diagnostic. “The model said nothing” is not an adequate diagnosis.

## SwiftUI and Liquid Glass integration

Use standard SwiftUI controls, labels, toolbars, sheets, alerts, progress indicators, and text editing where they match the task. Liquid Glass should express hierarchy and interaction state, not become a second AI brand layer. Place the AI affordance in the same navigation and toolbar grammar as the rest of the app. Use a glass container for related controls and let the system manage material, contrast, and adaptation.

An AI review shell should expose:

- the source or task the model is acting on;
- a compact “draft” or “suggested” label;
- current phase: preparing, generating, awaiting approval, or failed;
- a stop or cancel control while work is in flight;
- partial output that does not look committed;
- retry, edit, and dismiss paths;
- a clear confirmation action for side effects;
- fallback content when the model is unavailable;
- accessibility labels and values that describe status;
- privacy copy when user data is sent to a tool or external service.

Do not use a shimmering glass pill as a substitute for a working cancel button. Do not hide an AI-generated change behind a decorative transition. Do not imply that an Apple-owned system surface will appear merely because the app uses an Apple framework.

## Release and evidence boundary

The minimum production evidence package for a Foundation Models feature includes:

1. target and deployment configuration showing the Foundation Models import and availability strategy;
2. supported-device and Apple Intelligence/model readiness behavior;
3. physical-device run on the target class;
4. deterministic fallback run with Apple Intelligence disabled or unavailable;
5. cancellation, context, refusal, and tool-failure evidence;
6. accessibility inspection and alternate-input pass;
7. privacy review for prompts, transcript retention, tool data, logs, and feedback attachments;
8. prompt fixture results labeled with OS, SDK, device, and model version;
9. signed archive and release-build test;
10. TestFlight install and real-flow evidence;
11. App Store metadata and capability/entitlement review;
12. a release note describing any model-version-sensitive behavior.

An Xcode compile proves source compatibility for one configuration. A simulator proves only the simulated environment. An archive proves packaging and signing for that artifact. None proves on-device model readiness, output quality, tool authorization, physical UI behavior, privacy, or App Store review acceptance on its own.

## Decision checklist

Before implementation:

- Is this task genuinely model-shaped, or would a deterministic API be better?
- Does the target device and OS support the desired model lane?
- What is the fallback if Apple Intelligence is disabled or the model is not ready?
- Is this single-turn or a real multi-turn session?
- What must be in the transcript, and what must never be persisted?
- What output is a draft, a typed proposal, a tool request, or a committed domain action?
- Which operations require user approval?
- What is the context budget?
- How will cancellation and concurrent requests be prevented?
- Which model versions and prompt variants will be evaluated?
- What physical-device, accessibility, privacy, archive, TestFlight, and release evidence will be captured?

If those answers are not explicit, the route is still a prototype.

## Related local routes

- [Foundation Models mental model](../30-on-device-ai/01-foundation-models-mental-model.md)
- [Foundation Models prompt, context, and versioning](../30-on-device-ai/11-foundation-models-prompt-context-and-versioning.md)
- [Foundation Models native review and Liquid Glass design](../21-design-deep-dives/91-foundation-models-native-review-and-liquid-glass-design.md)
- [Foundation Models tool and structured-output route](../50-capability-recipes/94-foundation-models-tool-and-structured-output-route.md)
- [Prompt evaluation and model-update recipe](../31-on-device-ai-recipes/09-prompt-evaluation-and-model-update-recipe.md)
- [AI evaluation and safety checklist](../60-verification/03-ai-evaluation-and-safety-checklist.md)
- [AI review shell and glass state](../20-liquid-glass/06-ai-review-shell-and-glass-state.md)
- [Concurrency and Main Actor](../00-foundations/04-concurrency-and-main-actor.md)
- [Evidence and verification language](../00-foundations/05-evidence-and-verification-language.md)

## Sources

- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [SystemLanguageModel availability](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel/availability-swift.property)
- [SystemLanguageModel unavailable reasons](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel/availability-swift.enum/unavailablereason)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Transcript](https://developer.apple.com/documentation/foundationmodels/transcript)
- [Prompt](https://developer.apple.com/documentation/foundationmodels/prompt)
- [Generating content and performing tasks with Foundation Models](https://developer.apple.com/documentation/foundationmodels/generating-content-and-performing-tasks-with-foundation-models)
- [Managing the context window](https://developer.apple.com/documentation/foundationmodels/managing-the-context-window)
- [Foundation Models updates](https://developer.apple.com/documentation/updates/foundationmodels)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
- [GenerationGuide](https://developer.apple.com/documentation/foundationmodels/generationguide)
- [Generating Swift data structures with guided generation](https://developer.apple.com/documentation/foundationmodels/generating-swift-data-structures-with-guided-generation)
- [Tool](https://developer.apple.com/documentation/foundationmodels/tool)
- [Expanding generation with tool calling](https://developer.apple.com/documentation/foundationmodels/expanding-generation-with-tool-calling)
- [Adding intelligent app features with generative models](https://developer.apple.com/documentation/foundationmodels/adding-intelligent-app-features-with-generative-models)
- [LanguageModelError](https://developer.apple.com/documentation/foundationmodels/languagemodelerror)
- [LanguageModelSession.Error](https://developer.apple.com/documentation/foundationmodels/languagemodelsession/error)
- [Generative AI HIG](https://developer.apple.com/design/human-interface-guidelines/generative-ai)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
