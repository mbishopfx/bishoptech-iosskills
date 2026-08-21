# Foundation Models Sessions

## Capability

The Foundation Models framework provides access to Apple’s language models for supported devices and configurations. Use it for bounded language understanding, summarization, extraction, refinement, dialog, creative generation, guided structured output, and tool-assisted tasks. Select a narrower framework when the feature is fundamentally OCR, speech recognition, translation, sound classification, or a conventional ML prediction.

## Availability gate

Always check `SystemLanguageModel.default.availability` before creating the intelligence UI or making a generation request. Availability can depend on device eligibility, Apple Intelligence settings, model readiness, language/locale, OS version, and other system conditions. A model downloading is a normal state, not a generation failure that should be hidden behind an endless spinner.

Illustrative gate:

```swift
import FoundationModels

func availabilityState() -> SystemLanguageModel.Availability {
    SystemLanguageModel.default.availability
}
```

Compile the route against the selected SDK and handle every documented unavailable reason. The UI should offer a useful non-model path where one exists.

## Session boundary

A `LanguageModelSession` is a context that maintains state between requests. Create a session around a coherent task, give it concise instructions, and decide when to start a fresh session rather than carrying stale context forward.

```swift
import FoundationModels

@MainActor
final class SummaryService {
    func summarize(_ input: String) async throws -> String {
        let model = SystemLanguageModel.default
        guard case .available = model.availability else {
            throw SummaryError.modelUnavailable
        }

        let session = LanguageModelSession(instructions: """
            Summarize the supplied note in three short bullets.
            Do not invent facts. Preserve uncertainty.
            """)

        let response = try await session.respond(to: "Note:\n\(input)")
        return response.content
    }
}

enum SummaryError: Error {
    case modelUnavailable
}
```

This is a route sketch, not a compiled guarantee. In a real app, bound input length, redact content as needed, validate the returned string, and expose loading/cancellation/error states.

## Prompt and context discipline

- Keep instructions short, direct, and versioned.
- Treat user input as data; delimit it instead of allowing it to rewrite the task instructions.
- Do not place secrets, hidden authorization rules, or irreversible operations in a prompt.
- Keep only the context needed for the current task; a session can exceed its available context window.
- Re-evaluate prompts when the system model changes.
- Prefer guided generation or tools when correctness depends on structure, current data, or a side effect.

## Model selection boundary

The on-device model is privacy- and latency-friendly but has finite context and capabilities. Private Cloud Compute or another explicit server route is a separate decision for larger context or stronger reasoning. Do not silently imply that a fallback has identical privacy, cost, latency, or output behavior.

## Verification route

- Test available, device-ineligible, Apple Intelligence disabled, model-not-ready, unsupported language, context-exceeded, cancellation, and generation-error states.
- Use fixtures that include ambiguous, adversarial, sensitive, empty, and very long input.
- Record prompt version, model availability state, latency, and validation outcome without retaining raw private content unnecessarily.
- Test on a physical device with the final OS and language configuration; simulator success does not prove on-device model availability.

## Sources

- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Generating content and performing tasks with Foundation Models](https://developer.apple.com/documentation/foundationmodels/generating-content-and-performing-tasks-with-foundation-models)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [Prompting an on-device foundation model](https://developer.apple.com/documentation/foundationmodels/prompting-an-on-device-foundation-model)
- [Managing the context window](https://developer.apple.com/documentation/foundationmodels/managing-the-context-window)
- [Adding server-side intelligence with Private Cloud Compute](https://developer.apple.com/documentation/foundationmodels/adding-server-side-intelligence-with-private-cloud-compute)
