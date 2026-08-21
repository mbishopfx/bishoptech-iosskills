---
name: on-device-ai-feature
description: Design, implement, or audit an Apple on-device intelligence feature with a narrow framework route, explicit availability, reviewable output, privacy boundaries, and device evaluation.
metadata:
  short-description: Build safe on-device AI features
---

# On-Device AI Feature

Use this skill for features involving Foundation Models, Core ML, Vision, VisionKit, Speech, Translation, Natural Language, Sound Analysis, or App Intents. Treat model output as an uncertain proposal and the app’s deterministic code as the authority for validation, authorization, persistence, and side effects.

## Read before acting

Inspect the target project and data boundary:

- locate the deployment target, device family, model resources, entitlements, Info.plist privacy keys, package dependencies, existing persistence, and any network/server route;
- identify the source data, sensitivity, user-visible outcome, acceptable uncertainty, side effects, and fallback expectation;
- read the relevant [AI route selector](../../../30-on-device-ai/00-ai-route-selector.md), [Foundation Models mental model](../../../30-on-device-ai/01-foundation-models-mental-model.md), [privacy/availability/fallback guidance](../../../30-on-device-ai/06-privacy-availability-and-fallback.md), and [evaluation, safety, and fallback recipe](../../../31-on-device-ai-recipes/05-evaluation-safety-and-fallback.md);
- refresh the official [Foundation Models](https://developer.apple.com/documentation/foundationmodels/), [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel), [guided generation](https://developer.apple.com/documentation/foundationmodels/generating-swift-data-structures-with-guided-generation), [tool calling](https://developer.apple.com/documentation/foundationmodels/expanding-generation-with-tool-calling), [context window](https://developer.apple.com/documentation/foundationmodels/managing-the-context-window), [prompting](https://developer.apple.com/documentation/foundationmodels/prompting-an-on-device-foundation-model), and [output safety](https://developer.apple.com/documentation/foundationmodels/improving-the-safety-of-generative-model-output) pages;
- use the narrower [Core ML](https://developer.apple.com/documentation/coreml/), [Vision](https://developer.apple.com/documentation/vision/), [Speech](https://developer.apple.com/documentation/speech/), [Translation](https://developer.apple.com/documentation/translation), or [Natural Language](https://developer.apple.com/documentation/naturallanguage) route when its measurable output is the actual requirement.

## Route and implementation contract

1. Define the user outcome and choose the narrowest sufficient route. Use deterministic code for deterministic work; do not add a generative model because the feature is marketed as AI.
2. Verify API availability, device eligibility, OS version, language/locale, model readiness, permission state, and any server or Private Cloud Compute boundary before building the AI-dependent UI.
3. Keep trusted developer instructions separate from user or external content. Bound input size and context, minimize sensitive data, version prompts/schemas, and make the data flow legible.
4. Prefer typed or guided output for structured proposals. Validate every field, enum, range, identifier, and reference before it can affect domain state.
5. Keep tools small and app-owned. Read-only retrieval is safer than mutation; consequential actions require deterministic authorization, idempotence, error handling, and an explicit user confirmation step.
6. Model the full state machine: unavailable, downloading/not ready, permission denied, input missing, generating, partial output, cancellation, safety refusal, validation failure, reviewable proposal, committed result, and retry.
7. Store generated drafts/proposals separately from trusted domain truth. Show source context or uncertainty where the user needs it, and provide edit, reject, retry, and manual fallback paths.
8. Evaluate representative inputs, adversarial/safety cases, empty and oversized context, multiple languages, device classes, and prompt/schema versions. Track quality and latency without presenting a small fixture set as universal model behavior.

## Change boundary

May inspect and change the named feature, prompt/schema/tool contracts, local model integration, state machine, review UI, tests/fixtures, and directly related privacy/availability handling. Do not send data to a server, add a cloud model, collect telemetry, request broad permissions, or execute side effects merely to make an AI demo work unless the user explicitly authorizes that expansion.

## Refuse to assume

- every iPhone or iPad has the same Apple Intelligence or Foundation Models availability;
- a compiling API, simulator, mock response, or one successful prompt proves on-device behavior;
- model output is factual, deterministic, safe, or authorized to mutate data;
- a server model and Apple’s on-device model have the same limits, privacy, quality, or latency;
- “on device” applies to every Speech or Translation API without checking the exact route and availability;
- a generated string is safe to execute or publish without validation and review;
- health, legal, financial, or other high-impact output is correct merely because it sounds confident.

## Completion evidence

Report separately:

- route decision and why narrower deterministic/framework alternatives were accepted or rejected;
- data flow, privacy boundary, availability states, prompt/schema/tool contract, and fallback;
- validation, confirmation, safety, cancellation, and review behavior;
- evaluation fixtures, metrics, target OS/device/model configuration, and physical-device evidence when obtained;
- any unverified language, hardware, model-readiness, network, entitlement, or release gaps.

If the work is documentation or a route sketch, say so. If the simulator or a mock supplied the result, label it as mock/simulator evidence; never call it proof of Apple Intelligence behavior.

## Related knowledge-base routes

- [On-device AI recipes](../../../31-on-device-ai-recipes/README.md)
- [Foundation Models code recipes](../../../70-code-recipes/01-foundation-model-recipes.md)
- [AI feature brief](../../../90-templates/ai-feature-brief.md)
- [AI evaluation and safety checklist](../../../60-verification/03-ai-evaluation-and-safety-checklist.md)
- [Permission, entitlement, and privacy checklist](../../../60-verification/04-permission-entitlement-and-privacy-checklist.md)

## Sources

- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [Generating Swift data structures with guided generation](https://developer.apple.com/documentation/foundationmodels/generating-swift-data-structures-with-guided-generation)
- [Expanding generation with tool calling](https://developer.apple.com/documentation/foundationmodels/expanding-generation-with-tool-calling)
- [Managing the context window](https://developer.apple.com/documentation/foundationmodels/managing-the-context-window)
- [Prompting an on-device foundation model](https://developer.apple.com/documentation/foundationmodels/prompting-an-on-device-foundation-model)
- [Improving the safety of generative model output](https://developer.apple.com/documentation/foundationmodels/improving-the-safety-of-generative-model-output)
- [Core ML](https://developer.apple.com/documentation/coreml/)
- [Vision](https://developer.apple.com/documentation/vision/)
- [Speech](https://developer.apple.com/documentation/speech/)
- [Translation](https://developer.apple.com/documentation/translation)
- [Natural Language](https://developer.apple.com/documentation/naturallanguage)
