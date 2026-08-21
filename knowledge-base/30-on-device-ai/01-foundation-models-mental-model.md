# Foundation Models Mental Model

## What the framework provides

Foundation Models gives an app access to language models designed for Apple Intelligence, including the on-device SystemLanguageModel and a route to Private Cloud Compute when a larger context or stronger reasoning capability is justified. The on-device model is suited to language understanding and generation tasks such as summarization, extraction, classification, refinement, creative content, tags, and dialog.

## A session is a context boundary

LanguageModelSession holds the context used across requests. Instructions describe trusted app-level behavior; prompts contain the task and input. Every prompt, instruction, tool definition, generated schema, tool response, and model response consumes context. Reuse a session for a coherent short task, then create a new session when the context is full or the task boundary changes.

## Check availability first

Use SystemLanguageModel.default and inspect its availability before showing an AI-dependent flow. Availability can depend on device eligibility, Apple Intelligence settings, region, model readiness, language support, and OS/model version. A ready-to-compile API is not proof that the current person’s device can run the model.

~~~swift
let model = SystemLanguageModel.default

switch model.availability {
case .available:
    // Show or enable the intelligence workflow.
    break
case .unavailable(.deviceNotEligible):
    // Offer a deterministic or manual workflow.
    break
case .unavailable(.appleIntelligenceNotEnabled):
    // Explain the setting without blocking the rest of the app.
    break
case .unavailable(.modelNotReady):
    // Offer retry or a later reminder.
    break
case .unavailable:
    // Use the safest general fallback.
    break
}
~~~

The exact enum cases and availability behavior are version-sensitive; check the current SDK documentation when implementing.

## What the model is not

Do not use the on-device model as an authoritative calculator, code generator, database, permission decision, or source of current world knowledge. If the task needs current app data, provide a bounded tool. If it needs a deterministic result, use deterministic code and let the model explain or organize the result.

## Model updates

Apple can update the system model in OS releases. Prompt behavior, safety guardrails, token use, and output quality can change. Version prompts, keep representative evaluation cases, and rerun them when the target OS/model changes.

## Sources

- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Generating content and performing tasks with Foundation Models](https://developer.apple.com/documentation/foundationmodels/generating-content-and-performing-tasks-with-foundation-models)
- [Foundation Models updates](https://developer.apple.com/documentation/Updates/FoundationModels)
