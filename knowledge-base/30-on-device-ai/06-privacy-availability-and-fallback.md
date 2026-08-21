# Privacy, Availability, Safety, and Fallback

## Availability matrix

Treat model readiness as state, not a Boolean hidden in a service:

| State | User-facing behavior | Engineering action |
| --- | --- | --- |
| Available | Enable the AI route. | Run the bounded task and show progress/cancellation. |
| Device not eligible | Offer manual or deterministic path. | Do not repeatedly retry. |
| Apple Intelligence disabled | Explain the setting and keep core app usable. | Deep-link to settings only when appropriate. |
| Model not ready | Show retry/later behavior. | Avoid blocking the first-run flow. |
| Unsupported language | Offer supported language or original content. | Check supported languages before starting. |
| Context exceeded | Ask for a shorter task or start a fresh session. | Trim history and preserve only necessary state. |
| Guardrail violation | Explain that the request cannot be completed. | Log only what is appropriate for the privacy model. |
| Permission denied | Explain the missing permission and alternate route. | Re-check authorization when the app returns. |
| Model/service failure | Preserve input and offer retry/manual edit. | Make failure recoverable and observable. |

## Prompt boundaries

Keep trusted instructions separate from user or external content. Do not put unverified input into system instructions. Wrap user content in an explicit task template, constrain the expected output, and test prompt-injection-like inputs when the feature accepts open text or web content.

## Safety is app-specific

Apple’s framework guardrails are a base layer, not the complete safety design. Add domain-specific validation for the app’s audience, content, and possible real-world consequences. An app that generates a journal prompt has a different safety boundary from an app that drafts a medication reminder, sends a message, or edits financial records.

## Privacy minimization

- Send only the smallest input needed for the task.
- Keep raw personal data on device when the route allows it.
- Do not log full prompts/responses by default.
- Separate diagnostic sampling from production user data.
- Tell the user when content is generated, translated, transcribed, or sent to a larger service.
- Store source and generated output with separate retention/deletion rules.

## Fallback design

A fallback should preserve the user’s goal, not merely display an error. Examples: manual form entry instead of OCR, original text instead of translation, deterministic tags instead of model categories, local summary controls instead of a language-model summary, or a review queue until the model becomes ready.

## Model update discipline

Rerun representative prompts and safety tests after OS/model updates. Record prompt version, target OS, model availability, device family, language, and result. Treat a model change as a behavior change even when the Swift source is unchanged.

## Sources

- [Improving the safety of generative model output](https://developer.apple.com/documentation/foundationmodels/improving-the-safety-of-generative-model-output)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [Generating content and performing tasks with Foundation Models](https://developer.apple.com/documentation/foundationmodels/generating-content-and-performing-tasks-with-foundation-models)
- [Managing the context window](https://developer.apple.com/documentation/foundationmodels/managing-the-context-window)
- [Prompting an on-device foundation model](https://developer.apple.com/documentation/foundationmodels/prompting-an-on-device-foundation-model)
- [Adding server-side intelligence with Private Cloud Compute](https://developer.apple.com/documentation/foundationmodels/adding-server-side-intelligence-with-private-cloud-compute)
