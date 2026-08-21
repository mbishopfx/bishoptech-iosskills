---
name: ios-on-device-intelligence-evaluation
description: Design, implement, evaluate, or review iOS on-device intelligence features using Foundation Models, Vision, Core ML, Speech, Translation, Natural Language, Sound Analysis, and App Intents. Use when a feature generates, extracts, classifies, transcribes, translates, analyzes, or safely acts on user content with Apple intelligence frameworks.
---

# iOS On-Device Intelligence Evaluation

Use this skill to choose the narrowest intelligence route and keep availability, privacy, model output, deterministic validation, review, fallback, evaluation, and physical-device evidence explicit.

`authorized source -> bounded input -> available model/asset -> cancellable proposal -> validation/provenance -> review/authorization -> durable result or side effect`

## Read before acting

- Inspect the actual Xcode targets, deployment target, device family, model resources, language assets, entitlements, usage descriptions, persistence, network/server routes, and current AI adapter.
- Read the [AI route selector](../../../30-on-device-ai/00-ai-route-selector.md), [Foundation Models mental model](../../../30-on-device-ai/01-foundation-models-mental-model.md), [privacy/availability/fallback guidance](../../../30-on-device-ai/06-privacy-availability-and-fallback.md), [availability/proof matrix](../../../30-on-device-ai/08-on-device-ai-availability-and-proof-matrix.md), and [evaluation/safety/fallback recipe](../../../31-on-device-ai-recipes/05-evaluation-safety-and-fallback.md).
- Read the [on-device AI feature package](../on-device-ai-feature/SKILL.md) and the narrower [media/ML/input package](../ios-media-ml-and-inputs/SKILL.md) when capture, Vision, Core ML, audio, or NFC state is part of the route.
- Refresh the exact official Apple pages in the Sources section before relying on model availability, device/region/language behavior, API spelling, output safety, tool calling, context limits, or privacy claims.

## Route workflow

1. State the user outcome and decide whether a model is necessary. Use deterministic code for calculations, parsing, validation, routing, permissions, sorting, and safety rules; use a model only when ambiguity or learned perception/language is the value.
2. Choose the narrowest route: Foundation Models for bounded language generation/extraction; Vision for system observations; Core ML for a packaged custom model; Speech for the exact transcription route; Translation for supported language pairs; Natural Language for deterministic text analysis; Sound Analysis for bounded audio classification; App Intents for system-discoverable actions.
3. Record the route matrix: target SDK, OS/device eligibility, Apple Intelligence/model state, model/resource version, locale/language asset, permission, input sensitivity/retention, server or Private Cloud Compute boundary, expected uncertainty, and manual/deterministic fallback.
4. Model availability as state, not a Boolean: available, not eligible, disabled, model/asset not ready, unsupported language, permission denied, context exceeded, guardrail refusal, cancelled, input failure, service error, and retry/manual route.
5. Keep trusted instructions separate from user or external content. Bound input size, duration, image/audio dimensions, context, tool arguments, and concurrency. Version prompts, schemas, model revisions, preprocessing, and evaluation fixtures.
6. Prefer typed/guided output for structured proposals. Validate every field, enum, range, identifier, source reference, confidence/quality value, and authorization before it can affect domain state, export, messaging, payment, health data, or an irreversible action.
7. Keep tools narrow and app-owned. Prefer read-only tools; for mutation require deterministic authorization, validation, idempotence, timeout/error handling, audit/provenance, and explicit user confirmation. The model never becomes the authority for permissions or side effects.
8. Store generated drafts, observations, predictions, transcripts, translations, and classifications separately from trusted domain truth. Show source context/uncertainty when it matters, allow edit/reject/retry, redact logs, and define raw-input/output retention and deletion.
9. Evaluate representative, empty, oversized, multilingual, adversarial, safety-sensitive, low-quality, and stale-input fixtures. Record quality, abstention/refusal, correction rate, latency, memory, battery, thermal state, dropped inputs, and device/OS/model configuration.
10. Verify the actual physical device and target language/model configuration for any claim that depends on Apple Intelligence availability, camera/microphone/sensor behavior, on-device performance, or system-surface invocation. A simulator, mock, preview, or successful compile is narrower evidence.

## Framework boundaries

### Foundation Models

- Check `SystemLanguageModel` availability and the documented device/region/Apple Intelligence/model states before starting a session. Do not assume every iPhone or iPad supports the same model.
- Keep session context bounded and cancellable. Separate instructions from user/external content, handle context exhaustion and guardrail refusal, and re-evaluate behavior after OS/model updates.
- Use guided/typed generation for structured output, but validate schema and semantics yourself. A fluent generated answer is not factual truth, identity, medical/legal/financial advice, or authorization.
- Tool calling is an app trust boundary. Validate tool arguments, keep read-only retrieval separate from mutation, require confirmation for consequential actions, and record the source/reason/authorization for the final effect.

### Vision, Core ML, Speech, Translation, Natural Language, and Sound Analysis

- Vision observations depend on orientation, request/revision, preprocessing, input quality, and confidence. Preserve source/provenance and treat OCR, labels, face/pose, and coordinates as proposals.
- Core ML model loading, compiled asset availability, input/output shapes, normalization, model version, and compute-unit policy are explicit. Compute-unit choice does not guarantee a Neural Engine, accuracy, latency, or thermal result.
- Speech depends on the exact API, microphone permission, locale, audio route, asset/processing behavior, and cancellation. Do not call every Speech result “on device” without tracing the selected route.
- Translation depends on supported language pairs and language-asset/session readiness. Preserve original content, show language state, and allow correction/fallback.
- Natural Language is appropriate for defined tokenization, language identification, tagging, embeddings, or classification tasks. Record locale/model revision and do not inflate deterministic analysis into a generative conclusion.
- Sound Analysis depends on audio format, analyzer/model availability, confidence, interruptions, and capture/asset privacy. Stop capture when the feature ends and do not claim universal recognition from a fixture.

### App Intents and remote intelligence

- App Intents exposes typed actions/entities to Siri, Shortcuts, Spotlight, widgets, and system intelligence. Validate parameters and authorization exactly as for an in-app action; system discoverability is not permission to perform a side effect.
- Private Cloud Compute or another server model is a separate architecture. Trace what leaves the device, account/entitlement/network/cost, disclosure, retention, provider policy, and fallback. Never call a server route on-device proof.

## Evaluation and safety contract

For each evaluation record:

- route/framework/API and source URL;
- target SDK, OS/build, device family, region/language, Apple Intelligence/model/asset state, and model/prompt/schema version;
- input source, redaction/minimization, maximum size, retention, and consent/permission state;
- expected behavior, fixture class, output type, quality/correction/abstention metric, latency, memory, battery, and thermal observations;
- validation/review/commit rule, fallback, and unresolved risks.

Re-run representative prompts/fixtures after OS, SDK, model, language, prompt, schema, preprocessing, or tool changes. Test prompt-injection-like content when user or web content enters the context. Apple guardrails are a base layer; add app-specific domain, audience, privacy, and harm validation.

## Non-negotiable safety and evidence rules

- Never present generated text, OCR, classification, translation, transcription, sound analysis, or model output as medical/legal/financial truth, identity, authenticity, guaranteed accuracy, or authorization without domain validation and appropriate human review.
- Never claim “on-device,” “private,” “real-time,” “supported,” “accurate,” or “safe” from an imported framework, model response, simulator, preview, mock, one prompt, one language, one device, or successful compile.
- Keep source permission, model availability, input availability, output quality, domain validation, and side-effect authorization separate. A model that is ready can still return an unusable or unsafe proposal.
- Do not send sensitive prompts, audio, images, health/personal data, or model output remotely or retain raw inputs beyond the stated feature. Do not add broad permissions, analytics, telemetry, accounts, or servers merely to make an AI demo work.
- Cancel and clean up model sessions, capture, inference, translation, transcription, tool calls, and background tasks when the feature ends. Ignore stale results so an older proposal cannot overwrite newer user state.

## Deliverable

Produce a compact AI route note or implementation change containing:

- selected framework and rejected deterministic/narrower alternatives;
- availability, device/OS/model/language/permission/entitlement, privacy, retention, and server-boundary matrix;
- input/output/tool state machine with cancellation, context/backpressure, validation, review, authorization, fallback, and deletion;
- evaluation fixtures/metrics and exact compile, simulator, physical-device, performance, privacy, signing, and release evidence;
- remaining `to-verify` gaps and claims deliberately not made.

For implementation, change only the requested target and directly related adapters, prompt/schema/tool contracts, review UI, fixtures, or privacy/availability handling. Do not add a remote model, data upload, account, broad permission, irreversible tool, telemetry, or secret without a stated user-facing need and authorization.

## Related routes and recipes

- [On-device AI feature package](../on-device-ai-feature/SKILL.md)
- [AI route selector](../../../30-on-device-ai/00-ai-route-selector.md)
- [Foundation Models mental model](../../../30-on-device-ai/01-foundation-models-mental-model.md)
- [Privacy, availability, safety, and fallback](../../../30-on-device-ai/06-privacy-availability-and-fallback.md)
- [On-device AI availability and proof matrix](../../../30-on-device-ai/08-on-device-ai-availability-and-proof-matrix.md)
- [Foundation Models recipes](../../../70-code-recipes/01-foundation-model-recipes.md)
- [Vision, Core ML, and language recipes](../../../31-on-device-ai-recipes/03-vision-and-core-ml-pipelines.md)
- [Speech, translation, and language recipes](../../../31-on-device-ai-recipes/04-speech-translation-and-language-routes.md)
- [Evaluation, safety, and fallback](../../../31-on-device-ai-recipes/05-evaluation-safety-and-fallback.md)
- [AI evaluation and safety checklist](../../../60-verification/03-ai-evaluation-and-safety-checklist.md)
- [Permission, entitlement, and privacy checklist](../../../60-verification/04-permission-entitlement-and-privacy-checklist.md)

## Sources

- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Generating Swift data structures with guided generation](https://developer.apple.com/documentation/foundationmodels/generating-swift-data-structures-with-guided-generation)
- [Expanding generation with tool calling](https://developer.apple.com/documentation/foundationmodels/expanding-generation-with-tool-calling)
- [Managing the context window](https://developer.apple.com/documentation/foundationmodels/managing-the-context-window)
- [Prompting an on-device foundation model](https://developer.apple.com/documentation/foundationmodels/prompting-an-on-device-foundation-model)
- [Improving the safety of generative model output](https://developer.apple.com/documentation/foundationmodels/improving-the-safety-of-generative-model-output)
- [Foundation Models updates](https://developer.apple.com/documentation/Updates/FoundationModels)
- [Evaluating language-model responses](https://developer.apple.com/documentation/Evaluations/evaluating-language-model-responses)
- [Evaluating prompts to measure performance and improve model responses](https://developer.apple.com/documentation/foundationmodels/evaluating-prompts-to-measure-performance-and-improve-model-responses)
- [Adding server-side intelligence with Private Cloud Compute](https://developer.apple.com/documentation/foundationmodels/adding-server-side-intelligence-with-private-cloud-compute)
- [Core ML](https://developer.apple.com/documentation/coreml/)
- [Vision](https://developer.apple.com/documentation/vision/)
- [VisionKit](https://developer.apple.com/documentation/visionkit/)
- [Speech](https://developer.apple.com/documentation/speech/)
- [Translation](https://developer.apple.com/documentation/translation)
- [Natural Language](https://developer.apple.com/documentation/naturallanguage)
- [Sound Analysis](https://developer.apple.com/documentation/soundanalysis)
- [App Intents](https://developer.apple.com/documentation/appintents/)
