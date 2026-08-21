# On-Device AI Route Recipes

These pages turn the on-device AI catalog into feature-level routes. They are deliberately conservative about what a model can guarantee:

`availability -> bounded input -> generation/observation -> validation -> user review -> domain action -> fallback`

Foundation Models is not the only Apple intelligence route. Use Vision, Core ML, Speech, Translation, Natural Language, Sound Analysis, and App Intents when their narrower capability is a better fit.

## Recipes

- [Foundation Models sessions](00-foundation-model-sessions.md)
- [Guided generation and typed output](01-guided-generation-and-typed-output.md)
- [Tool calling and agent boundaries](02-tool-calling-and-agent-boundaries.md)
- [Vision and Core ML pipelines](03-vision-and-core-ml-pipelines.md)
- [Speech, translation, and language routes](04-speech-translation-and-language-routes.md)
- [Evaluation, safety, and fallback](05-evaluation-safety-and-fallback.md)
- [Reviewable multimodal AI pipeline](06-reviewable-multimodal-ai-pipeline.md)
- [Tool approval and App Intents](07-tool-approval-and-app-intents.md)
- [Native AI review shell](08-native-ai-review-shell.md)
- [Prompt evaluation and model-update recipe](09-prompt-evaluation-and-model-update-recipe.md)

## Route rule

Let the model propose content or structured values. Let deterministic application code validate authorization, schema, permissions, purchases, dates, numbers, and side effects. Put a person in the loop when an incorrect result could change a record, send a message, spend money, expose private data, or affect health/safety.

## Sources

- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Apple Intelligence and machine learning](https://developer.apple.com/documentation/TechnologyOverviews/ai-machine-learning)
- [Core ML](https://developer.apple.com/documentation/coreml/)
- [Vision](https://developer.apple.com/documentation/vision/)
- [Speech](https://developer.apple.com/documentation/speech/)
- [Translation](https://developer.apple.com/documentation/translation)
- [Natural Language](https://developer.apple.com/documentation/naturallanguage)
