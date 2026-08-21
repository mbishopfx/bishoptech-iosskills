# Guided Generation and Typed Output

## Capability

Use guided generation when a feature needs a structured result rather than free-form text: extracted fields, a checklist, tags, a proposed route, a game event, or a draft action plan. A typed result gives the app a schema boundary, but it does not make the values true or safe.

## Route

1. Define the smallest app-owned value type needed by the next deterministic step.
2. Mark the type as `@Generable` and guide ambiguous fields with descriptions or constraints.
3. Prompt for only the input needed to populate that type.
4. Ask the session to generate the type.
5. Validate ranges, identifiers, dates, permissions, and cross-field invariants in normal Swift code.
6. Render a review form before persistence or side effects when the result came from untrusted or uncertain content.

Illustrative shape:

```swift
import FoundationModels

@Generable
struct NoteDraft {
    @Guide(description: "A short factual title for the note")
    var title: String

    @Guide(description: "A concise list of proposed next steps")
    var nextSteps: [String]
}

func draftNote(from source: String) async throws -> NoteDraft {
    let session = LanguageModelSession(instructions: "Extract a cautious note draft. Never invent details.")
    let response = try await session.respond(generating: NoteDraft.self) {
        "Source text:\n\(source)"
    }
    return response.content
}
```

The exact macro and response APIs are SDK-version-sensitive; compile the sketch against the target SDK and consult the linked guided-generation documentation before implementation.

## Schema design

- Use enums or constrained values for finite choices.
- Keep optionality explicit: “unknown” is different from an empty string.
- Make quantities carry units or normalize them before storage.
- Keep provenance and review state outside the generated content when the product needs auditability.
- Avoid giant nested schemas that consume context and increase correction cost.
- Treat an absent field as a result to handle, not a license to infer.

## Validation boundary

Generated objects must pass deterministic checks before the app:

- saves or overwrites a record;
- marks a task complete;
- sends a message or invokes a system intent;
- makes a purchase or changes entitlement;
- writes HealthKit/HomeKit data;
- calls a network endpoint;
- changes a game state with meaningful consequences.

For high-impact actions, show the source content and proposed values side by side. “The model returned the right type” is not sufficient evidence of correctness.

## Failure handling

Plan for schema-generation errors, context overflow, unavailable model, partial or low-quality values, cancellation, and a model update that changes phrasing. A typed fallback can be a manual form, a deterministic parser, or a “save as unprocessed text” path.

## Verification route

- Create a labeled fixture set with expected values and explicit unknown cases.
- Score field accuracy, omission, hallucination, formatting, and review burden separately.
- Test malformed, adversarial, multilingual, truncated, and duplicate inputs.
- Confirm every generated field has an accessible editing affordance where correction is expected.
- Keep the schema and prompt version in the evaluation record.

## Sources

- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
- [GeneratedContent](https://developer.apple.com/documentation/foundationmodels/generatedcontent)
- [Generating Swift data structures with guided generation](https://developer.apple.com/documentation/foundationmodels/generating-swift-data-structures-with-guided-generation)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Improving the safety of generative model output](https://developer.apple.com/documentation/foundationmodels/improving-the-safety-of-generative-model-output)
