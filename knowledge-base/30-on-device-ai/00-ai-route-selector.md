# On-Device AI Route Selector

## Start with the job, not the word AI

Choose the narrowest technology that solves the user outcome. A language model is not the default parser, database, calculator, permission system, or source of truth.

| User outcome | First route | Add when needed |
| --- | --- | --- |
| Summarize, extract, classify, refine, or compose text | Foundation Models | Guided generation, tools, review UI |
| Produce a typed proposal from text | Foundation Models with Generable | Guide constraints, validation, human review |
| Use current app data while generating | Foundation Models tool calling | Query tool, bounded context, source references |
| Change app state through natural language | App Intent or Foundation Models tool | Confirmation, authorization, idempotence |
| Detect text, objects, faces, poses, or visual quality | Vision | Core ML custom model, VisionKit UI |
| Scan live text or codes from the camera | VisionKit DataScanner | Camera permission, device availability |
| Transcribe live or recorded audio | Speech | AVFoundation, microphone permission, asset availability |
| Translate text | Translation | Language availability/download state |
| Classify or predict with a custom model | Core ML | Create ML/Core ML Tools, model versioning |
| Expose actions and entities to Siri, Spotlight, or Shortcuts | App Intents | AppEntity, EntityQuery, App Shortcuts |
| Need larger context or stronger reasoning | Private Cloud Compute or an approved server | Entitlement, network, privacy review, fallback |

## Decide whether a model is needed

Use deterministic code for fixed transformations, calculations, validation, sorting, permissions, routing, and safety-critical rules. Use a model when the input is ambiguous or language/vision understanding is the value. Keep the deterministic layer responsible for constraints, persistence, authorization, and irreversible side effects.

## Availability is a product state

For every AI feature, design:

- available now;
- not eligible on this device;
- Apple Intelligence disabled;
- model/assets downloading or not ready;
- language unsupported;
- permission denied;
- context exhausted;
- guardrail or safety error;
- user-cancelled;
- service/model error;
- deterministic fallback.

## The review boundary

The safest default flow is:

source -> model proposal -> validation -> human review -> explicit commit

Skip the human step only for low-impact, reversible, clearly bounded presentation help where the product has evidence that the behavior is acceptable.

## Sources

- [Apple Intelligence and machine learning](https://developer.apple.com/documentation/TechnologyOverviews/ai-machine-learning)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Core ML](https://developer.apple.com/documentation/coreml/)
- [Vision](https://developer.apple.com/documentation/vision/)
- [Speech](https://developer.apple.com/documentation/speech/)
- [Translation](https://developer.apple.com/documentation/translation)
- [App Intents](https://developer.apple.com/documentation/appintents/)
