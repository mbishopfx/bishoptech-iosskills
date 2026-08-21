# Foundation Models Recipes

Use these route sketches with the [AI feature lifecycle and availability guide](../30-on-device-ai/09-ai-feature-lifecycle-and-availability.md), [evaluation and model-update discipline](../30-on-device-ai/10-on-device-ai-evaluation-and-model-update-discipline.md), and [tool approval/App Intent workflow](../31-on-device-ai-recipes/07-tool-approval-and-app-intents.md). They are not compiled in this documentation-only workspace.

## Availability-gated text generation

```swift
import FoundationModels

enum IntelligenceState {
    case checking
    case available
    case unavailable
}

@MainActor
final class IntelligenceController: ObservableObject {
    @Published private(set) var state: IntelligenceState = .checking

    func checkAvailability() {
        switch SystemLanguageModel.default.availability {
        case .available:
            state = .available
        case .unavailable:
            state = .unavailable
        }
    }

    func summarize(_ source: String) async throws -> String {
        guard case .available = SystemLanguageModel.default.availability else {
            throw IntelligenceError.unavailable
        }

        let bounded = String(source.prefix(8_000))
        let session = LanguageModelSession(instructions: """
            Summarize the supplied text in three factual bullets.
            Do not invent details. Preserve uncertainty.
            """)

        let response = try await session.respond(to: "Source:\n\(bounded)")
        return response.content
    }
}

enum IntelligenceError: Error {
    case unavailable
}
```

The `prefix` is only a crude example of bounding input; use token/context-aware budgeting for the real feature. The exact `availability` cases and response APIs must be checked against the selected Foundation Models SDK.

## Guided output

```swift
@Generable
struct DraftTask {
    @Guide(description: "A concise task title")
    var title: String

    @Guide(description: "A proposed due date, or nil when unknown")
    var dueDate: String?
}

func makeDraft(from source: String) async throws -> DraftTask {
    let session = LanguageModelSession(instructions: "Extract a cautious task draft.")
    let response = try await session.respond(generating: DraftTask.self) {
        "Source:\n\(source)"
    }
    return response.content
}
```

Validate dates and permissions in Swift. Show the person a reviewable edit form before saving or scheduling anything.

## Compile/device gate

- Add the correct framework and deployment target.
- Check model availability on the final device/language/Apple Intelligence configuration.
- Handle model-not-ready, context exceeded, cancellation, safety, and generation errors.
- Keep prompt/schema versions and evaluate a fixture set after each change.
- Do not call a remote fallback without separately documenting privacy, cost, consent, and entitlement behavior.

## Sources

- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
- [Generating Swift data structures with guided generation](https://developer.apple.com/documentation/foundationmodels/generating-swift-data-structures-with-guided-generation)
- [Managing the context window](https://developer.apple.com/documentation/foundationmodels/managing-the-context-window)
