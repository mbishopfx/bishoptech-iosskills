# Foundation Models on iOS 26: tools, guided output, and failure modes

## Scope and version ledger

This page is the iOS 26 baseline for the Foundation Models framework. It focuses on the on-device SystemLanguageModel, LanguageModelSession, guided generation, and tool calling as documented for the iOS 26 SDK.

The Foundation Models documentation continues to evolve. Current documentation also exposes newer beta APIs such as dynamic profiles, custom LanguageModel providers, and newer error types. Those APIs need their own availability checks and should not be pulled into an iOS 26 implementation merely because they appear in the current documentation index. When a project moves to a newer SDK, re-check the API reference and release notes, then evaluate the same feature again on the new OS.

This is a framework reference, not a claim that a route compiles in this documentation-only workspace. Compile the smallest slice against the exact Xcode and deployment target used by the app.

## Capability contracts

| Need | Foundation Models route | Deterministic responsibility |
| --- | --- | --- |
| Summarize or rewrite bounded text | LanguageModelSession string response | Input bounds, source selection, review, disclosure |
| Extract a record or proposal | Generable type with Guide constraints | Domain validation, dates, numbers, IDs, persistence |
| Use current app data | Read-only Tool | Authorization, query scope, redaction, result size |
| Perform a consequential action | Proposal plus deterministic use case | Confirmation, authorization, idempotency, commit |
| Use a current external source | Explicit network tool or separate service | Network consent, authentication, freshness, privacy |
| Need a fixed classification | App rules, Natural Language, Vision, or Core ML first | Thresholds, confidence policy, fallback |

The model is a bounded language component. It is not the source of truth for permissions, purchases, identity, current records, financial amounts, or irreversible state transitions.

## Availability is the first state

Before presenting a model-dependent flow, inspect the selected system model’s availability:

~~~swift
import FoundationModels

@available(iOS 26.0, *)
func currentFoundationModelAvailability() -> SystemLanguageModel.Availability {
    SystemLanguageModel.default.availability
}
~~~

Availability can depend on device eligibility, Apple Intelligence settings, model assets, language or locale, and system state. Treat unavailable as a product state rather than as an exceptional crash. The feature should be able to explain the state and, where practical, continue with a manual or deterministic route.

At minimum, model the following states:

- checking;
- available;
- device not eligible;
- Apple Intelligence not enabled;
- model assets not ready or unavailable;
- unsupported language or locale;
- rate limited or otherwise temporarily unavailable;
- request in progress;
- completed;
- refused or blocked by guardrails;
- cancelled;
- failed with a recoverable or non-recoverable error.

Do not infer physical device support from the deployment target or from a successful import. Do not infer model readiness from a preview or simulator run.

## A session is a context budget

LanguageModelSession holds the transcript for a coherent interaction. The transcript includes prompts, responses, instructions, tool definitions, tool arguments, tool outputs, and guided-generation schema information. In the iOS 26 documentation, the system model context window is 4,096 tokens. The total across the session matters; a single large prompt is not the only way to overflow.

Design the session boundary deliberately:

| Session decision | Good default |
| --- | --- |
| One focused task | Reuse a session for a short sequence that benefits from context |
| New source record | Start a new session unless the prior context is essential |
| Context nearing its limit | Summarize or discard old context, then create a new session |
| User leaves the feature | Cancel the request and release the feature-owned session |
| Sensitive content no longer needed | Do not carry it into a later session |
| Multiple simultaneous prompts | Serialize or create separate sessions; do not issue a second request on a responding session |

If the context exceeds the limit, the documented recovery is to remove entries and retry, or split the source into smaller chunks and combine deterministic results. A retry that simply repeats the same oversized transcript is not recovery.

### Prewarm is a latency hint, not readiness proof

iOS 26 adds useful prewarming behavior: LanguageModelSession.prewarm can ask the system to load resources and cache the instructions and a prompt prefix. Use it while the person is making a choice that is likely to lead to generation, not on every screen appearance.

Prewarm does not prove that a request will succeed. The model can still be unavailable, the prompt can exceed the context window, the request can be refused, or the person can cancel before generation starts. Record the actual request timing separately from the prewarm call.

## Guided generation: structure first, validation second

Guided generation replaces manual parsing of a raw response with a Swift type. Use the Generable macro on a structure or enumeration and Guide only where names, descriptions, ranges, or counts materially improve the result.

~~~swift
import FoundationModels

@available(iOS 26.0, *)
@Generable(description: "A reviewable task proposal")
struct TaskProposal {
    @Guide(description: "A short task title")
    var title: String

    @Guide(description: "A short explanation of the proposed task")
    var rationale: String

    @Guide(description: "A priority from 1 to 3", .range(1...3))
    var priority: Int
}
~~~

Guided generation uses constrained sampling. That helps keep the response in the declared shape, but it does not prove that the values are true, authorized, current, or useful. The application still validates every field:

- trim and length-limit text;
- reject empty or disallowed titles;
- clamp or reject values outside the domain’s real range;
- parse dates and amounts with locale-aware deterministic code;
- resolve any generated reference against current data;
- discard generated IDs and use domain-owned IDs;
- require a person to review before writing a record or triggering an action;
- retain provenance when the proposal may be misunderstood later.

Keep schema names and Guide descriptions short. Schema text consumes the session’s context and can add latency. The model generates properties in declaration order, so put foundational fields before dependent or explanatory fields.

### Dynamic schemas

Use DynamicGenerationSchema only when the schema truly depends on runtime data. A bounded menu, a set of user-selected fields, or a server-provided list can justify a runtime schema. A general-purpose arbitrary form builder is usually safer as deterministic UI with model-filled suggestions.

Constructing a GenerationSchema can fail when property names conflict, references are undefined, or types are duplicated. Surface schema construction as a preflight state before showing the generate button. Do not discover a malformed schema after the person has waited for a model response.

### Partial and incomplete output

Streaming a generable type produces partial snapshots. An incomplete object is a draft, not a committed domain value. iOS 26 also exposes completion information through GeneratedContent, so the route can distinguish a complete generated value from content that is still being assembled.

The UI should make the following distinction visible:

partial model output -> local validation -> editable draft -> accepted domain value

Do not save a partial object as if it were final merely because all currently visible properties look plausible.

## Tool calling: a typed bridge to app code

A Tool is Sendable and supplies:

- a unique name;
- a short description of when it is useful;
- an Arguments type that can be initialized from generated content;
- an Output type that can be represented in a prompt;
- an async call method.

The framework gives the model the tool definition, lets the model generate arguments, runs the tool, feeds the result back, and lets the model continue. A model can call tools concurrently when the calls are independent, so the tool and its dependencies must be concurrency-safe.

~~~swift
import FoundationModels

@available(iOS 26.0, *)
struct SearchLocalTasks: Tool {
    let name = "search_local_tasks"
    let description = "Finds a small set of tasks in the person’s local task store."

    @Generable
    struct Arguments {
        @Guide(description: "A short search phrase")
        var query: String

        @Guide(description: "The maximum number of results", .range(1...5))
        var limit: Int
    }

    let repository: TaskRepository

    func call(arguments: Arguments) async throws -> [String] {
        let query = arguments.query.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !query.isEmpty, query.count <= 120 else {
            throw TaskSearchError.invalidQuery
        }

        let rows = try await repository.search(
            query: query,
            limit: min(max(arguments.limit, 1), 5)
        )

        return rows.map { row in
            "Task: \(row.title). Status: \(row.status). Reference: \(row.opaqueReference)."
        }
    }
}

enum TaskSearchError: Error {
    case invalidQuery
}
~~~

The repository in this example must apply the person’s current authorization and account scope. The model must not be able to choose an arbitrary file path, database predicate, SQL fragment, URL, user ID, or secret. Use opaque references and resolve them against current authorized state after the model responds.

### Tool output is prompt input

Tool output becomes context for the model. Return the smallest useful representation:

- bounded result count;
- concise fields;
- no access tokens, private URLs, raw database rows, or hidden account metadata;
- explicit “not found,” “stale,” or “not authorized” states;
- stable opaque references that the app can resolve;
- a source label when the final answer needs attribution.

If a tool calls a network service, the network boundary is part of the tool contract. Declare whether the feature can work offline, what data leaves the device, how authentication is obtained, and what a timeout or partial response means.

### Tool calling modes

GenerationOptions.ToolCallingMode has three documented modes:

| Mode | Meaning | Use |
| --- | --- | --- |
| allowed | The model may call a tool | Normal grounded assistance |
| required | The model must call one or more tools | Fresh-data gate or mandatory policy lookup |
| disallowed | The model cannot call a tool | Final formatting from already-grounded context |

Required mode needs an exit condition. A tool can throw when its work is complete, or the session can change the mode dynamically in newer APIs. On the iOS 26 baseline, keep the loop bounded in app code and test that the model can reach a final response. A permanently required tool can produce repeated calls instead of a final answer.

Treat every model-selected action as a proposal. For a query tool, authorization can usually happen inside the query. For a mutation tool, prefer a two-stage route: generate a typed proposal, show the person the affected record and exact change, then commit through a deterministic use case after confirmation.

## Error taxonomy and recovery

The iOS 26 SDK documents Foundation Models failures through session and generation errors. Avoid showing the raw localized error as the only user experience; map each class to a product state and retain redacted diagnostics for development.

| Failure class | Likely meaning | Recovery |
| --- | --- | --- |
| Assets unavailable | Model resources are not ready or cannot be loaded | Explain readiness, offer retry/manual path |
| Context exceeded | Instructions, schema, prompts, tools, outputs, or transcript are too large | Reduce context, split work, start a new session |
| Concurrent requests | A second request started while the session was responding | Serialize, cancel, or use another session |
| Rate limited | The service temporarily rejected the request | Back off and offer retry; do not spin |
| Unsupported language or locale | The selected model cannot process the requested language | Switch language, use deterministic path, or explain |
| Guardrail violation | Prompt or output crossed the framework’s safety boundary | Rephrase fixed prompts, narrow input, explain refusal |
| Refusal | The model declined even when the request did not map to a guardrail violation | Show a predetermined explanation or the documented refusal explanation |
| Decoding failure | Generated content could not be decoded into the requested type | Record schema/prompt version, narrow type, retry only with a changed route |
| Unsupported guide | A generation guide pattern is not supported by the model | Replace with a supported constraint or deterministic validation |
| Tool call error | A tool threw or failed to execute | Show the affected step, preserve state, retry safely |

For iOS 26 source, the legacy LanguageModelSession.GenerationError cases are the relevant implementation vocabulary. Current documentation marks those cases deprecated for newer SDKs in favor of LanguageModelError and related error types. When migrating, update both the catch logic and the verification matrix; do not use an availability check as a substitute for testing the new error surface.

ToolCallError includes the tool that failed and its underlying error. Use that information to distinguish a permission problem, a stale record, a timeout, and a programming defect. Do not leak the underlying error’s private values into the person-facing message.

## Safety and content boundaries

Foundation Models has built-in safety layers, but app-specific safety remains the developer’s responsibility. Keep trusted instructions separate from untrusted prompts, retrieved notes, web content, attachments, and tool output. A retrieved document can contain prompt-injection text; it is data, not a new authorization policy.

The default guardrails apply to model input and output. The iOS 26 permissiveContentTransformations guardrail mode is intended for text-to-text transformations such as summarization or rewriting of sensitive source material. It does not turn off safety for arbitrary generation, and it does not change guided-generation behavior. Do not use it to bypass a policy or to make a high-impact action model-safe.

For every open-input feature:

- provide curated examples or constrained input when possible;
- bound length and supported content type;
- define an app-specific deny or allow policy if the domain needs one;
- label generated content;
- give the person a way to dismiss, retry, correct, or report a problem;
- never automate deletion, purchase, message sending, access changes, or publication from an unreviewed model response.

## iOS 26 release-note details worth testing

Apple’s iOS 26 release notes are part of the implementation source, not just a historical changelog. They call out behavior that directly affects a build:

- prewarm caches more than just system resources;
- guided generation can expose refusal and incomplete-content states;
- permissive content transformations apply to string generation;
- tool calling and guided generation have had decoding and invocation fixes;
- duplicate tool names can be fatal, so enforce uniqueness in the tool registry;
- a session reconstructed from a transcript must receive the tools it needs;
- enum arguments with associated values have had decoding limitations, so prefer a wrapper structure for the iOS 26 route;
- incomplete model assets can surface as misleading guardrail failures, so verify asset readiness before classifying a prompt as unsafe.

Record the SDK and OS build in test artifacts whenever one of these boundaries matters.

## Implementation order

1. Define the domain outcome and its deterministic fallback.
2. Add the availability state before creating the model UI.
3. Create a bounded session around one task.
4. Start with raw string generation only when a string is truly the output.
5. Move to a small Generable type when the app needs fields.
6. Add a read-only tool only when current app data is necessary.
7. Return concise, authorized tool output.
8. Validate every generated value in normal Swift code.
9. Make side effects explicit and reviewable.
10. Add cancellation, error mapping, and a non-model path.
11. Evaluate representative and adversarial fixtures.
12. Compile, run on a named physical device, and record the exact OS/model/language/resource state.

## What this page proves

This page documents the official iOS 26 API shape and the boundaries that an implementation should honor. It does not prove that a particular app’s prompts are high quality, that a model is available on a particular device, or that a tool side effect is safe. Those require the compile, fixture, physical-device, system-state, and release evidence described in the verification pages.

## Sources

- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Generating content and performing tasks with Foundation Models](https://developer.apple.com/documentation/foundationmodels/generating-content-and-performing-tasks-with-foundation-models)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Expanding generation with tool calling](https://developer.apple.com/documentation/foundationmodels/expanding-generation-with-tool-calling)
- [Tool](https://developer.apple.com/documentation/foundationmodels/tool)
- [Generating Swift data structures with guided generation](https://developer.apple.com/documentation/foundationmodels/generating-swift-data-structures-with-guided-generation)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
- [GeneratedContent](https://developer.apple.com/documentation/foundationmodels/generatedcontent)
- [Managing the context window](https://developer.apple.com/documentation/foundationmodels/managing-the-context-window)
- [Improving the safety of generative model output](https://developer.apple.com/documentation/foundationmodels/improving-the-safety-of-generative-model-output)
- [permissiveContentTransformations](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel/guardrails/permissivecontenttransformations)
- [LanguageModelSession.GenerationError](https://developer.apple.com/documentation/foundationmodels/languagemodelsession/generationerror)
- [iOS and iPadOS 26 release notes](https://developer.apple.com/documentation/ios-ipados-release-notes/ios-ipados-26-release-notes)
- [Generative AI](https://developer.apple.com/design/human-interface-guidelines/generative-ai)
