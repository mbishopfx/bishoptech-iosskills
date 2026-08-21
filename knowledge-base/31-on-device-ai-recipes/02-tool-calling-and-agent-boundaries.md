# Tool Calling and Agent Boundaries

## Capability

Foundation Models tools let a model call app-owned code to retrieve current information or perform a side effect. This can create agent-like experiences, but the model remains an untrusted planner: authorization, validation, idempotency, confirmation, and error handling belong to deterministic app code.

## Tool route

The documented flow has six phases:

1. Provide the model with the available tools and their schemas.
2. Submit the user’s bounded request.
3. Let the model generate tool arguments.
4. Run the tool code.
5. Return the tool output to the model.
6. Let the model produce a final response or another tool call.

Illustrative tool boundary:

```swift
import FoundationModels

struct SearchLocalNotes: Tool {
    let name = "search_local_notes"
    let description = "Finds notes matching a user-provided search phrase."

    @Generable
    struct Arguments {
        @Guide(description: "A short search phrase")
        var query: String
    }

    func call(arguments: Arguments) async throws -> String {
        let safeQuery = arguments.query.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !safeQuery.isEmpty, safeQuery.count <= 120 else {
            throw SearchError.invalidQuery
        }
        return try await NotesRepository().searchSummary(for: safeQuery)
    }
}

enum SearchError: Error {
    case invalidQuery
}
```

The repository, access control, and output redaction are intentionally outside the tool. A tool should return the minimum information the model needs for the next step.

## Read tools versus side-effect tools

Prefer read-only tools first. For a side effect, add:

- an explicit user-visible confirmation step;
- authorization checks independent of the model;
- input validation and resource ownership checks;
- idempotency keys or deduplication;
- an audit/result record;
- a clear cancellation and failure response;
- an exit condition if the tool mode can be required.

If a tool can send, buy, delete, unlock, publish, or alter external state, do not let a natural-language model call it directly without a deterministic policy gate.

## Prompt-injection boundary

Tool output and retrieved content can contain instructions that are not trusted task instructions. Delimit external content, treat it as data, and keep tool descriptions narrow. Never let a retrieved note or web response redefine authorization, reveal secrets, or select an arbitrary code path.

## Context and cost boundary

Tool descriptions, schemas, arguments, and outputs consume context. Return concise, typed, redacted outputs. Avoid passing entire databases, transcripts, or binary data into a session when a filtered summary is enough.

## Verification route

- Test missing, malformed, ambiguous, unauthorized, stale, duplicate, and adversarial tool arguments.
- Test tool timeout, cancellation, retry, partial success, and output truncation.
- Verify a side effect cannot happen twice when the model repeats a call.
- Test the required-tool mode with an explicit exit condition.
- Record tool decisions and outcomes in a privacy-safe evaluation log, not raw private prompts by default.

## Sources

- [Tool](https://developer.apple.com/documentation/foundationmodels/tool)
- [Expanding generation with tool calling](https://developer.apple.com/documentation/foundationmodels/expanding-generation-with-tool-calling)
- [Generating content and performing tasks with Foundation Models](https://developer.apple.com/documentation/foundationmodels/generating-content-and-performing-tasks-with-foundation-models)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Managing the context window](https://developer.apple.com/documentation/foundationmodels/managing-the-context-window)
- [Improving the safety of generative model output](https://developer.apple.com/documentation/foundationmodels/improving-the-safety-of-generative-model-output)
