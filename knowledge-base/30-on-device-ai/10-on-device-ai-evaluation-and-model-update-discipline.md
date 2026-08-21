# On-Device AI Evaluation and Model-Update Discipline

## Readiness is more than a good demo

A prompt that produces one attractive answer is not evidence that an AI feature is ready. Evaluate the complete route: input selection, availability, generation or observation, validation, human correction, side effects, fallback, privacy, and resource behavior.

The evaluation target is the user outcome, not the model’s fluency. Compare the AI route with the deterministic or manual baseline that a person would otherwise use.

## Evaluation layers

| Layer | Question | Example evidence |
| --- | --- | --- |
| API contract | Does the selected SDK/API compile with the intended deployment target? | Xcode build, availability annotations, macro expansion, generated model wrapper, entitlements. |
| Readiness | Does the target device have the model, language asset, camera, microphone, or system capability now? | Runtime state capture on the supported device/configuration. |
| Task quality | Did the route complete the intended user job? | Versioned fixture results, field-level correctness, groundedness, correction rate, or task completion. |
| Safety and trust | Did it avoid unsafe, private, unauthorized, or unsupported conclusions? | Sensitive/adversarial fixtures, refusal handling, validation failures, human review. |
| Action correctness | Did the app perform the intended side effect once and only once? | Authorization, idempotency, tool/intent selection, confirmation, commit, and recovery tests. |
| Resource behavior | Is latency, memory, energy, thermal load, and cancellation acceptable? | Device measurements with build, model, input, and workload recorded. |
| System integration | Does the actual Siri, Spotlight, Shortcuts, widget, control, Live Activity, Visual Intelligence, or Writing Tools surface behave correctly? | Invocation and deep-link evidence on the supported system surface. |

Do not turn a pass at one layer into a claim about the next layer. A green compile does not prove model readiness; a high-confidence Vision observation does not prove a record; a correct in-app intent does not prove Siri or Spotlight resolution.

## Build a fixture taxonomy

Keep fixtures small, named, and versioned. Include the source and expected boundary without storing unnecessary private data.

- **Representative:** common inputs from the actual user workflow.
- **Empty:** no text, no detected object, silence, missing fields, no search result, or no matching entity.
- **Ambiguous:** multiple valid interpretations, unclear dates, similar labels, overlapping speech, or low-contrast text.
- **Long/large:** context-heavy text, long audio, multi-page documents, large images, or a sequence that approaches the route’s budget.
- **Multilingual:** supported languages, locale variants, code-switching, names, numbers, right-to-left text, and unsupported-language fallback.
- **Adversarial/untrusted:** prompt injection, instruction-like retrieved content, malformed tool arguments, hostile text, or image/audio content that should not control the app.
- **Privacy-sensitive:** redaction, deletion, logs, retention, permission denial, restricted access, and user-selected versus broad data access.
- **Lifecycle:** cancellation, view disappearance, repeated submission, interruption, background/foreground, asset download, model-not-ready, timeout, and process restart.
- **Side effect:** duplicate calls, stale state, revoked authorization, invalid ownership, partial failure, and a person rejecting the review.

Fixtures should test both the model route and the fallback route. A fallback that is never exercised is only a design intention.

## Route-specific measurements

### Foundation Models

Measure instruction following, groundedness in supplied context, omission versus invention, schema validity, field-level correctness, refusal or safety behavior, tool selection, argument validity, number of tool calls, correction burden, context usage, latency, cancellation, and the final user task outcome. For a typed proposal, score every field and cross-field invariant instead of marking the whole response correct because the title sounds good.

Record prompt/instruction version, schema/guidance version, tool definitions, tool-calling mode, model availability/use case, OS/build, language, device, and the exact fixture. Re-run after OS/model updates even when the Swift source has not changed.

### Vision and Core ML

Measure the behavior that the product actually needs: false positives/negatives, localization or geometry, confidence calibration, negative examples, model revision, input orientation, lighting/blur/occlusion, model loading, latency, memory, thermal behavior, and user correction. Keep Vision observations and Core ML predictions separate from the domain record they may inform.

For live capture, measure freshness and dropped-frame policy in addition to per-frame accuracy. A smooth preview with a stale but clearly labeled result can be preferable to a blocked preview; the product must make freshness visible.

### Speech, Translation, Natural Language, and Sound Analysis

Measure transcript or classification quality on representative accents, noise, silence, overlap, punctuation, names, numbers, languages, and route interruptions. Keep volatile and finalized speech results separate. For translation, preserve source text, measure meaning-preserving edits, and test unsupported or not-installed language pairs. For deterministic Natural Language or Sound Analysis output, define the category/task contract and score uncertainty and fallback rather than presenting a generic “AI accuracy” number.

### App Intents and system routes

Measure entity resolution, parameter completion, authorization, user confirmation, deep-link destination, process/extension behavior, duplicate invocation, cancellation, stale data, and the actual system-owned surface. An in-app button test cannot prove Siri, Spotlight, Shortcuts, a widget, a control, a Live Activity, or Visual Intelligence.

## Evaluation record

Use a record that makes changes comparable:

| Field | Required detail |
| --- | --- |
| Feature and outcome | What the person is trying to accomplish and the consequence of being wrong. |
| Route | Exact framework, API, model use case, request/revision, language pair, or system surface. |
| Version | App/build, SDK, OS/build, model/asset version, prompt/instruction, schema, tool, and fixture versions. |
| Configuration | Device family, region, language/locale, Apple Intelligence/model setting, permissions, network, thermal/battery context. |
| Input boundary | Source type, size/length, redaction, retention, and whether it was user-selected. |
| Output boundary | Observation/proposal/transcript/translation, confidence/provenance, validation, review, and commit rule. |
| Result | Quality score, correction/rejection, latency, memory/thermal notes, error/fallback, tool calls, and side-effect result. |
| Evidence | Source, compile, preview, simulator, physical device, system surface, signed/release, or production record. |

Avoid retaining raw private prompts, images, audio, health data, or tool payloads by default. Store aggregate or redacted evidence unless a documented, consented debugging workflow requires more.

## Updating prompts and models

Apple can update the system language model through OS releases. Treat model updates as behavior changes, not invisible infrastructure. Keep a small prompt/schema/tool regression set and rerun it when any of these change:

- OS or SDK;
- model availability or model version;
- prompt/instructions or localized copy;
- `@Generable` schema or `Guide` constraints;
- tool definitions, tool output, or tool-calling mode;
- supported language or translation/speech assets;
- domain validation, confirmation, or fallback policy.

If a new model version improves fluency but increases unsafe proposals, omissions, latency, or correction burden, keep the older prompt/route or narrow the task until the complete user outcome is acceptable. Do not silently widen the product claim because a demo looks better.

## Release and marketing boundary

Use precise claims:

- “Uses Foundation Models when available” is different from “works on every iPhone.”
- “Runs a Core ML model on supported devices” is different from “recognizes objects accurately.”
- “Offers speech transcription” is different from “transcription is always on device.”
- “Exposes an App Intent” is different from “Siri can always complete the action.”
- “Passed a fixture set” is different from “safe for all user inputs.”

Keep the evidence record attached to the claim, and state the unsupported devices, languages, settings, and fallbacks plainly.

## Sources

- [Evaluating language model responses](https://developer.apple.com/documentation/Evaluations/evaluating-language-model-responses)
- [Evaluating prompts to measure performance and improve model responses](https://developer.apple.com/documentation/foundationmodels/evaluating-prompts-to-measure-performance-and-improve-model-responses)
- [Updating prompts for new model versions](https://developer.apple.com/documentation/foundationmodels/updating-prompts-for-new-model-versions)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [Managing the context window](https://developer.apple.com/documentation/foundationmodels/managing-the-context-window)
- [Improving the safety of generative model output](https://developer.apple.com/documentation/foundationmodels/improving-the-safety-of-generative-model-output)
- [Expanding generation with tool calling](https://developer.apple.com/documentation/foundationmodels/expanding-generation-with-tool-calling)
- [Vision](https://developer.apple.com/documentation/vision/)
- [VisionObservation confidence](https://developer.apple.com/documentation/vision/visionobservation/confidence)
- [CoreMLRequest](https://developer.apple.com/documentation/vision/coremlrequest)
- [Classifying images with Vision and Core ML](https://developer.apple.com/documentation/coreml/classifying-images-with-vision-and-core-ml)
- [SpeechAnalyzer](https://developer.apple.com/documentation/speech/speechanalyzer)
- [SpeechTranscriber](https://developer.apple.com/documentation/speech/speechtranscriber)
- [TranslationSession](https://developer.apple.com/documentation/translation/translationsession)
- [LanguageAvailability](https://developer.apple.com/documentation/translation/languageavailability)
- [Natural Language](https://developer.apple.com/documentation/naturallanguage)
- [Sound Analysis](https://developer.apple.com/documentation/soundanalysis)
- [App Intents](https://developer.apple.com/documentation/appintents/)
