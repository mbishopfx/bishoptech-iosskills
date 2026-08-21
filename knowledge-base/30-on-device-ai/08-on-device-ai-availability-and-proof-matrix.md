# On-Device AI Availability and Proof Matrix

“On-device AI” is a route-specific claim, not a product label. The app must identify the exact Apple framework and API, the data path, the device/model state, the language or asset state, and the evidence that supports the claim. Foundation Models, Vision, Core ML, Speech, Translation, Natural Language, Sound Analysis, and App Intents do not share one universal availability contract.

Refresh this matrix before implementation and after an OS, SDK, model, language-asset, or prompt change. Keep generated output separate from trusted app state and keep a deterministic or manual fallback for the underlying user goal.

## State layers

| Layer | Question | Typical evidence |
| --- | --- | --- |
| SDK/API | Does the selected target SDK expose the framework and symbol? | Current Apple page, deployment target, compile/build result. |
| Model/feature | Is the system model, model resource, language asset, sensor, or specialized capability ready? | Framework-specific availability API or documented readiness state on the target device. |
| Permission/data | Is the app authorized to receive the input, and is the input actually available? | Permission state, usage description, user-selected data, and input fixture. |
| Behavior | Does the route produce an acceptable result for representative inputs? | Versioned fixtures, evaluation metrics, latency/memory observations, and human review. |
| Action | Can the result be committed, exported, or used to call a tool? | Deterministic validation, authorization, idempotence, confirmation, and side-effect tests. |

Passing one layer never proves the next one. A successful compile does not prove model readiness; a model response does not authorize a database mutation; a simulator mock does not prove an Apple Intelligence result on a person’s iPhone.

## Foundation Models matrix

| Route or state | What to check | Minimum useful proof |
| --- | --- | --- |
| Foundation Models framework | Target SDK, import, deployment target, and exact API version. | Official [Foundation Models](https://developer.apple.com/documentation/foundationmodels/) page plus a target compile. |
| `SystemLanguageModel` availability | Device eligibility, region, Apple Intelligence state, model readiness/download state, and the documented availability cases. | Call the current availability API in the target app; exercise available, not-eligible, not-ready, and other unavailable paths on supported device configurations. |
| `LanguageModelSession` | Session lifecycle, context limits, cancellation, errors, prompt/instruction separation, and task scope. | Unit tests for state/error handling plus physical-device generation tests with recorded OS/model configuration. |
| Guided generation and typed output | Schema/guidance, macro/API availability, validation, missing/extra/invalid fields, and user review. | Compile against the selected SDK; fixtures that intentionally produce incomplete or invalid proposals; review UI before persistence. |
| Tool calling | Tool input validation, authorization, read-only versus mutating tools, idempotence, confirmation, timeout, and error mapping. | Mocked tool tests plus an end-to-end physical-device flow; no model call directly owns irreversible side effects. |
| Context and token budget | Input minimization, context-window size, truncation strategy, prompt version, and cancellation. | Token/context measurements and oversized-input fixtures; re-evaluate after model/OS updates. |
| Guardrails and unsafe output | System guardrails, app validation, sensitive-data minimization, refusal handling, and escalation/manual fallback. | Safety and adversarial fixtures, not just happy-path prompts; document what the app still must filter or review. |
| Model updates | OS/model version, prompt behavior, tool-call behavior, quality/latency regression, and compatibility changes. | Re-run representative evaluations after each documented model update and retain the prompt/schema version with results. |
| Private Cloud Compute or another server route | Whether the product actually needs server-side intelligence, data boundary, entitlement/account, network, disclosure, cost, and fallback. | Treat as a separate architecture and release gate; do not call it on-device proof. |

Apple’s current `SystemLanguageModel` documentation states that the model’s availability depends on device and region support for Apple Intelligence and requires an availability check. Apple’s Foundation Models updates also warn that model behavior can change across OS/model versions, so prompt and evaluation maintenance is part of the feature, not optional polish.

## Narrower intelligence routes

| User outcome | Narrow route | Gates and evidence boundary |
| --- | --- | --- |
| Detect text, objects, faces, poses, or image quality | [Vision](https://developer.apple.com/documentation/vision) | Image orientation, request type, confidence, model/device cost, and camera/photo permission. Use image fixtures and physical-device performance tests where capture or latency matters. |
| Scan documents, codes, or live camera content | [VisionKit](https://developer.apple.com/documentation/visionkit/) | Camera permission, supported hardware, scanner availability, lighting, interruption, and review of extracted results. Simulator UI is not camera proof. |
| Run a custom classifier, detector, embedder, or regressor | [Core ML](https://developer.apple.com/documentation/coreml/) | Model version/bundle, input contract, compute units, memory, thermal/battery budget, and quality fixtures. Measure representative physical devices. |
| Transcribe live or recorded speech | [Speech](https://developer.apple.com/documentation/speech/) | Exact Speech API, microphone/speech usage descriptions, locale, audio route, authorization, cancellation, and documented processing/privacy behavior. Do not label every Speech API simply “on device.” |
| Translate supported text/content | [Translation](https://developer.apple.com/documentation/translation) | Language-pair support, language assets, session/UI availability, download state, and manual correction. Test language fixtures and unavailable-asset fallback. |
| Tag, classify, identify language, or embed text deterministically | [Natural Language](https://developer.apple.com/documentation/naturallanguage) | Language/task model support, input normalization, multilingual quality, and deterministic output fixtures. Do not add a generative model when a defined analysis is enough. |
| Classify bounded audio events | [Sound Analysis](https://developer.apple.com/documentation/soundanalysis) | Audio format, microphone/asset route, analyzer/model availability, confidence, interruptions, and battery/latency budget. Verify with representative recordings and physical capture. |
| Make app actions discoverable to system intelligence | [App Intents](https://developer.apple.com/documentation/appintents/) | Intent/entity contract, authorization, parameter validation, Shortcuts/Spotlight/widget/system invocation, and safe side-effect boundaries. Test the actual system surface, not just an in-app button. |

## Minimum AI evidence loop

1. **Source:** link the exact framework/API page and record the research date.
2. **Compile:** verify the target SDK, deployment target, model resources, macros, entitlements, and usage descriptions.
3. **Availability:** render explicit unavailable, not-ready, permission-denied, unsupported-language, and input-failure states.
4. **Deterministic boundary:** validate generated or observed data before it becomes domain truth, a tool argument, an export, or an irreversible action.
5. **Evaluation:** run versioned representative, empty, oversized, multilingual, adversarial, and safety fixtures; record quality and latency.
6. **Device:** test the actual hardware, OS/model version, language, permissions, and thermal/battery conditions that the claim depends on.
7. **Fallback:** preserve a useful manual, deterministic, cached, or narrower-framework route when AI is unavailable or rejected.

## Claims this matrix rejects

- “The app supports on-device AI” based only on importing Foundation Models or Core ML.
- “Every iPhone supports this model” without the current Apple device/region availability evidence.
- “The model is private” without tracing the exact API’s data path and any server route.
- “The AI is accurate” without representative evaluation and human review for the consequence level.
- “The assistant can do it” when the model has not been authorized to call a bounded, validated app tool.
- “Simulator-tested” as evidence for camera, microphone, sensors, model readiness, physical performance, or protected data.

## Verification record

| Field | Example value to record |
| --- | --- |
| Route | Foundation Models guided generation, Vision OCR, Core ML classifier, or Speech transcription. |
| Target configuration | Device family, OS/build, SDK, language/region, Apple Intelligence/model state, and model version. |
| Input boundary | User-selected text/image/audio, redaction/minimization, maximum size, and retention. |
| Output boundary | Typed proposal/observation/transcript, validation, confidence/uncertainty, review, and commit rule. |
| Fallback | Manual entry, deterministic parser, cached result, local search, or narrower framework. |
| Evidence | Source, compile, fixture, simulator, physical device, signed/release, or production evidence. |
| Open risks | Model update, language coverage, privacy path, latency, thermal/battery, permission, or device gaps. |

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
