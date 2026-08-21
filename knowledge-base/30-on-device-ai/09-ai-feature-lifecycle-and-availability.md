# AI Feature Lifecycle and Availability

## Scope

An on-device intelligence feature is a stateful product workflow, not a single model call. The same feature may pass compilation and still be unavailable because the device, Apple Intelligence setting, language asset, permission, camera, microphone, input, or system surface is not ready.

Use this lifecycle for Foundation Models, Vision/Core ML, Speech, Translation, Natural Language, Sound Analysis, and App Intents. Replace each gate with the exact state reported by the selected framework instead of inventing one global `isAIAvailable` flag.

## The shared route

`user outcome -> route selection -> SDK/configuration -> permission/asset check -> availability -> bounded input -> observation/generation -> validation -> review -> deterministic action -> recorded result`

The route is allowed to stop at any stage. A person can cancel, a model can be unavailable, an input can be invalid, or a review can reject a proposal without the feature becoming an error in the app.

## Cross-framework contract

| Stage | App responsibility | Typical Apple route | Evidence to retain |
| --- | --- | --- | --- |
| Route selection | Choose the narrowest technology for the user outcome. | Foundation Models, Vision, Core ML, Speech, Translation, Natural Language, Sound Analysis, or App Intents. | User outcome, chosen API, rejected alternatives, source links. |
| SDK/configuration | Confirm imports, target SDK, deployment target, model asset, usage description, capability, and entitlement. | Framework reference and Xcode project settings. | Build configuration and compile result. |
| Permission/input | Ask only when the person starts the relevant workflow and verify the selected input. | Camera, microphone, speech recognition, Photos picker, HealthKit, or user-provided text/file. | Authorization state, source reference, input format, retention choice. |
| Readiness | Check framework-specific availability, language, asset, hardware, and model state. | `SystemLanguageModel`, `SpeechAnalyzer`, `AssetInventory`, `LanguageAvailability`, Vision requests, Core ML loading. | Device/OS/model/language state and the exact readiness result. |
| Processing | Bound work, preserve cancellation, and separate partial from final output. | `LanguageModelSession`, Vision request, `SpeechAnalyzer`, `TranslationSession`, or model prediction. | Start/finish/cancel/error state and measured resource behavior. |
| Validation | Convert output into app-owned types and apply deterministic rules. | Codable/`@Generable` proposal, Vision observation, transcript, translation, or intent parameters. | Validation errors, confidence/provenance, source mapping, and schema version. |
| Review | Show what the system observed or generated and let the person edit or reject it. | SwiftUI `Form`, editor, sheet, confirmation, or source-linked review screen. | Accepted/rejected/corrected fields and reviewer action. |
| Action | Execute through the domain use case, never through raw model text. | App-owned service, `Tool`, `AppIntent`, persistence, export, or system surface. | Authorization, idempotency key, result, and failure/recovery state. |

## A state model that stays honest

Keep the feature state expressive enough to tell the difference between “not ready” and “failed.” This is a route sketch, not a claim about a single Apple enum:

```swift
enum IntelligencePhase: Equatable {
    case idle
    case checking
    case unavailable(reason: UnavailabilityReason)
    case preparing(detail: String)
    case ready
    case processing(progress: Double?)
    case draft(ProposalID)
    case validating(ProposalID)
    case review(ProposalID)
    case committing(ProposalID)
    case completed(ResultID)
    case cancelled
    case failed(FeatureFailure)
}
```

Keep the following values separate even if the UI presents them in one status row:

- **Eligibility:** whether this device, region, OS, or model can use the route.
- **Readiness:** whether a model, language asset, camera, microphone, or session is prepared now.
- **Authorization:** whether the person granted the specific protected data access.
- **Input validity:** whether the selected text, image, audio, file, or entity can be processed.
- **Processing:** whether work is active, partial, stale, cancelled, or finished.
- **Trust level:** whether the result is an observation, proposal, reviewed value, or committed domain record.

Do not collapse these into `loading` or `success`. A translation asset download, an unavailable Foundation Model, and a rejected OCR proposal require different recovery actions.

## Availability gates by route

### Foundation Models

Start from `SystemLanguageModel.default.availability` for the exact model use case. Record the selected model’s availability, supported language/locale, context size, and any model-not-ready condition before presenting an AI-dependent screen. Create a bounded `LanguageModelSession` only after the feature has a valid input and a clear task boundary.

The model’s availability is not the same as the quality of a generated result. Keep model readiness, prompt/schema version, context budget, guardrail or refusal state, validation, and user review as separate states. If the model is unavailable, preserve the underlying manual workflow instead of blocking the app.

### Vision and Core ML

Vision requests need a valid image or frame, an appropriate request/revision, and a lifecycle that can handle failure or cancellation. Core ML adds model loading, input/output contract, compute-unit, memory, thermal, and model-version decisions. An observation’s confidence or a model prediction is evidence for review, not authorization or domain truth.

For live camera work, check camera permission and supported scanner/device state before presentation. Keep capture, inference, UI preview, and accepted result as separate pipelines so a slow model does not block the camera surface.

### Speech

For the modern analyzer route, select a supported `SpeechTranscriber` locale/preset, check the required speech assets, supply an `AsyncSequence` of analyzer input, consume progressive/final results, and finish or cancel the `SpeechAnalyzer` deliberately. An analyzer can process only one input sequence at a time; decide how a new recording replaces or waits for the current one.

Keep volatile transcription separate from finalized transcription. A revised partial phrase must never directly trigger a message, purchase, deletion, or other high-impact action.

### Translation

Use `LanguageAvailability` to distinguish an unsupported language pair from a supported pair whose assets are not installed. `TranslationSession` readiness, download preparation, translation, cancellation, and user edits are separate states. Preserve the source text and treat translation as a derived representation.

### Natural Language and Sound Analysis

Use Natural Language for bounded, deterministic language analysis such as language identification, tagging, or embeddings, and Sound Analysis for bounded audio categories. Define the input format, model/task state, confidence policy, and fallback. Do not add a generative model when the product only needs a known analysis.

### App Intents and system surfaces

App Intents do not replace the availability state of a language, vision, or audio model. They expose actions and entities to Siri, Apple Intelligence, Shortcuts, Spotlight, widgets, controls, Live Activities, and other supported surfaces. The system may invoke an intent when the app UI is not running, so the intent must resolve parameters, re-check authorization, and use the same deterministic domain use case as the in-app route.

## User-facing fallback matrix

| Condition | Preserve | Offer |
| --- | --- | --- |
| Device/model not eligible | User input and app’s core goal | Manual or deterministic route; do not repeatedly retry. |
| Model or language asset not ready | Draft/source and selected language | Prepare/download, retry later, or continue without enrichment. |
| Permission denied/restricted | The user’s requested task and explanation | Settings/manual path; re-check when the app returns. |
| Unsupported language/input | Original content | Supported locale, alternate input, or manual editing. |
| Context/input too large | Source reference and partial work | Shorten, split, summarize deterministically, or start a new session. |
| Partial/cancelled processing | Last confirmed result and editable draft | Resume, retry, or save for later; never promote partial output silently. |
| Invalid/unsafe proposal | Source and validation reason | Correct fields, manual entry, or reject. |
| Tool/App Intent failure | Proposed action and current domain state | Explain, retry safely, or return to the app-owned workflow. |

## Proof gates

Record the evidence at the same granularity as the claim:

1. **Source:** exact Apple/Swift page and research date.
2. **Compile:** selected SDK, deployment target, imports, macros, entitlements, usage descriptions, and build result.
3. **Availability:** supported device, OS/build, region, language, model/asset readiness, and permission state.
4. **Behavior:** representative input, output/proposal, validation, review, cancellation, and fallback.
5. **Evaluation:** versioned fixture set, quality result, correction burden, latency, memory, thermal, and battery observations where relevant.
6. **Physical/system proof:** camera, microphone, Apple Intelligence model, system surface, or protected service tested on the hardware and surface that the claim names.
7. **Release:** signed artifact, privacy metadata, entitlement, server/account, TestFlight, or production evidence only when that boundary is actually tested.

## Sources

- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Managing the context window](https://developer.apple.com/documentation/foundationmodels/managing-the-context-window)
- [Updating prompts for new model versions](https://developer.apple.com/documentation/foundationmodels/updating-prompts-for-new-model-versions)
- [Vision](https://developer.apple.com/documentation/vision/)
- [VisionObservation confidence](https://developer.apple.com/documentation/vision/visionobservation/confidence)
- [CoreMLRequest](https://developer.apple.com/documentation/vision/coremlrequest)
- [SpeechAnalyzer](https://developer.apple.com/documentation/speech/speechanalyzer)
- [SpeechTranscriber](https://developer.apple.com/documentation/speech/speechtranscriber)
- [AssetInventory](https://developer.apple.com/documentation/speech/assetinventory)
- [Translation](https://developer.apple.com/documentation/translation)
- [TranslationSession](https://developer.apple.com/documentation/translation/translationsession)
- [LanguageAvailability](https://developer.apple.com/documentation/translation/languageavailability)
- [Natural Language](https://developer.apple.com/documentation/naturallanguage)
- [Sound Analysis](https://developer.apple.com/documentation/soundanalysis)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
