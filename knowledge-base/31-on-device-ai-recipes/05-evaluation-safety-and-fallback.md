# Evaluation, Safety, and Fallback

## Capability

An AI feature is not ready because one prompt produced a compelling answer. Readiness requires measured task quality, safety boundaries, graceful unavailability, human review where needed, and a clear record of what the system actually did.

## Evaluation loop

1. Define the user task and the cost of a wrong result.
2. Build a representative fixture set with expected outputs or scoring rules.
3. Version the prompt, schema, tool definitions, model availability state, and app build.
4. Measure accuracy, omission, hallucination, refusal, latency, token/context use, tool calls, and correction burden.
5. Include adversarial and sensitive inputs, not only happy-path examples.
6. Re-run the set after SDK, OS, model, prompt, schema, or tool changes.

For generated text, score groundedness, instruction following, tone, and safety separately. For structured output, score every field and cross-field invariant. For tools, score whether the right tool was chosen, arguments were safe, and side effects happened exactly once.

## Safety boundary

Apple’s generative safety guidance is a base layer, not a product-specific safety case. Add domain boundaries for:

- sensitive or disallowed input;
- privacy and data minimization;
- prompt injection and untrusted retrieved content;
- high-impact advice or claims;
- side effects and confirmation;
- abuse, harassment, self-harm, or illegal activity handling where relevant;
- logging and human escalation.

Do not put untrusted user content into the instruction channel. Delimit it as data, constrain the response, and validate the result outside the model.

## Availability/fallback state machine

`checking -> available -> generating -> validating -> review -> applied`

Failure branches should be first-class:

`unavailable -> manual workflow`

`model not ready -> retry/later`

`context exceeded -> shorten/split input`

`unsafe/invalid -> explain and request correction`

`tool failure -> deterministic error state`

`generation cancelled -> preserve draft, do not apply`

Fallbacks should preserve the user’s underlying goal where possible. A manual form, deterministic parser, saved draft, local search, or narrower Vision/Core ML route is often better than a vague “AI unavailable” error.

## Privacy and observability

Log feature version, availability state, latency, error class, validation result, and aggregate scores. Avoid logging raw prompts, private images, health data, transcripts, tokens, or tool payloads unless a documented consented debugging flow requires it. Keep user-visible disclosure accurate about on-device, Private Cloud Compute, and server processing.

## Verification route

- Test every availability and fallback state on the final OS/device/language matrix.
- Test unsafe, injected, sensitive, malformed, long, multilingual, and empty inputs.
- Verify high-impact actions require deterministic authorization and confirmation.
- Compare model-assisted behavior with the manual baseline; a slower but correct fallback can be the better product.
- Review App Store privacy disclosures, data retention, and marketing claims against measured evidence.

## Sources

- [Evaluating prompts to measure performance and improve model responses](https://developer.apple.com/documentation/foundationmodels/evaluating-prompts-to-measure-performance-and-improve-model-responses)
- [Evaluating language model responses](https://developer.apple.com/documentation/Evaluations/evaluating-language-model-responses)
- [Improving the safety of generative model output](https://developer.apple.com/documentation/foundationmodels/improving-the-safety-of-generative-model-output)
- [Generating content and performing tasks with Foundation Models](https://developer.apple.com/documentation/foundationmodels/generating-content-and-performing-tasks-with-foundation-models)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [Adding server-side intelligence with Private Cloud Compute](https://developer.apple.com/documentation/foundationmodels/adding-server-side-intelligence-with-private-cloud-compute)
- [Apple Intelligence and machine learning](https://developer.apple.com/documentation/TechnologyOverviews/ai-machine-learning)
