# Reviewable Multimodal AI Pipeline

## Use one review boundary for many input types

A feature can combine text, images, audio, translation, and a language model without pretending that all of them are one kind of “AI.” Keep each framework responsible for the narrow result it can measure, then normalize those results into a reviewable app-owned proposal.

`source -> specialized Apple route -> observation/derivation -> normalized evidence -> optional Foundation Models enrichment -> typed proposal -> deterministic validation -> review -> domain commit`

The proposal is not a record until the app’s validation policy and the person’s review promote it.

## Route composition matrix

| Input | First route | Normalized evidence | Optional enrichment | Proof boundary |
| --- | --- | --- | --- | --- |
| Photo/document | Photos picker, Vision, or VisionKit | Text, regions, document structure, confidence, source reference | Summarize or map validated fields with Foundation Models | Photo permission, orientation, scanner/camera support, model quality, physical capture. |
| Live camera | AVFoundation, Vision, VisionKit DataScanner | Latest observation, freshness, geometry, confidence | Explain or group confirmed observations | Camera permission, frame backpressure, device support, thermal behavior. |
| Recording/audio stream | SpeechAnalyzer/SpeechTranscriber or Sound Analysis | Volatile/final transcript or bounded sound category | Extract a typed draft from finalized text | Microphone permission, locale/assets, route/interruption, physical audio. |
| Text | Foundation Models, Natural Language, or deterministic parser | Generated proposal or deterministic tags | Only when the narrower result leaves a real language task | Model availability, context, schema, prompt version, evaluation. |
| Translated content | Translation/TranslationSession | Source, target, translation, language pair, user edits | Summarize or classify the reviewed translation | Language availability/assets, source preservation, language-quality evaluation. |
| App/system invocation | App Intent/AppEntity/EntityQuery | Resolved entity, parameters, invocation source | Foundation Models tool only when the app-owned task needs it | System surface, authorization, process boundary, deep link, idempotency. |

## App-owned data contracts

Keep source and derived data explicit. The following is a conceptual route shape; compile the concrete types in the target project:

```swift
struct EvidenceItem: Identifiable, Sendable {
    let id: UUID
    let kind: EvidenceKind
    let sourceReference: SourceReference
    let capturedAt: Date
    let text: String?
    let confidence: Double?
    let modelOrRequestVersion: String?
}

struct ReviewableProposal: Identifiable, Sendable {
    let id: UUID
    let evidenceIDs: [UUID]
    var fields: [ProposalField]
    var validation: ValidationSummary
    var status: ProposalStatus
}

enum ProposalStatus: Sendable {
    case draft
    case needsReview
    case accepted
    case rejected
    case committed
}
```

Do not make `confidence` a truth value. Preserve source regions or timestamps when a person needs to verify the proposal. Keep the original image, audio, or text retention policy separate from the derived record.

## Coordinator responsibilities

The coordinator owns orchestration and cancellation; specialized services own their framework APIs; the domain use case owns validation and side effects.

1. Create a source record when the person selects or starts capture.
2. Check permission, hardware, locale, model, and asset readiness.
3. Start the narrow framework route with a bounded input and a cancellation handle.
4. Keep partial/volatile output in a draft buffer and show freshness/status.
5. Convert final output into `EvidenceItem` values with provenance.
6. Run deterministic normalization: dates, amounts, identifiers, units, ownership, and allowed values.
7. Optionally call Foundation Models with only the validated fields needed for a bounded enrichment task.
8. Show a review screen with editable fields, source evidence, uncertainty, and an explicit accept/reject action.
9. Revalidate on commit against current domain state and authorization.
10. Persist the accepted record and source/derived retention metadata separately.

If a source changes while processing, cancel or mark the old result stale. Never let an older asynchronous result overwrite a newer accepted proposal.

## Native review surface

Use the native screen hierarchy that matches the user’s job:

- `NavigationStack` for capture -> proposal -> detail when the user moves through a sequence.
- `Form` and semantic controls for editable fields, validation messages, language selection, and permission recovery.
- A sheet for a bounded review or confirmation that should return to the source context.
- `TextEditor` for transcript/source correction, preserving the original alongside edits.
- A toolbar or bottom action region for `Accept`, `Reject`, `Save draft`, and `Retry`, with one primary action.
- Functional Liquid Glass only for a related action group or system-provided bar; the source evidence and editable content remain readable content layers.

The screen must remain understandable with reduced transparency, reduced motion, VoiceOver, Dynamic Type, and a long localized field. A glass affordance or animated confidence cue cannot be the only indication of uncertainty or completion.

## Source-specific guardrails

### Vision/Core ML

Show the image or relevant source region when a field is ambiguous. Store model/revision and confidence only as evidence. Validate barcode payloads, dates, amounts, units, and ownership deterministically before a record is committed.

### Speech

Keep volatile transcript text visually distinct from finalized text. Require a review step before transcript-derived commands or records. Preserve punctuation/names/numbers as editable content, and make microphone/asset/route failures recoverable.

### Translation

Keep the source and target visible or reachable. Do not overwrite the source with a translation. Let the person choose the language pair and edit the derived text before it becomes a message, note, or action proposal.

### Foundation Models

Use guided output for bounded fields and pass only the minimum validated context. Validate every generated value, keep unknown values optional, and let the person correct the proposal. If a tool is available, query tools should be read-only by default; mutating tools route through the approval workflow.

## Verification matrix

| Proof | Test |
| --- | --- |
| Fixture | Empty, noisy, long, multilingual, ambiguous, malformed, adversarial, and representative source inputs. |
| UI | Loading, permission denied, assets not ready, partial, final, stale, review, rejected, committed, and retry states. |
| Accessibility | VoiceOver labels/focus, Dynamic Type, reduced motion/transparency, keyboard/pointer, and source-region descriptions. |
| Lifecycle | Cancellation, replacement source, background/foreground, interruption, duplicate submission, process restart, and persistence failure. |
| Device | Camera, microphone, language asset, model readiness, memory, thermal, audio route, and real-time behavior on supported hardware. |
| System | App Intent/entity resolution, deep link, widget/control/Live Activity invocation, or other named system surface. |
| Release | Privacy manifest, usage descriptions, entitlements, signed build, and only the server/account/TestFlight/production evidence actually claimed. |

## Sources

- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [Generating Swift data structures with guided generation](https://developer.apple.com/documentation/foundationmodels/generating-swift-data-structures-with-guided-generation)
- [Expanding generation with tool calling](https://developer.apple.com/documentation/foundationmodels/expanding-generation-with-tool-calling)
- [Vision](https://developer.apple.com/documentation/vision/)
- [VisionObservation confidence](https://developer.apple.com/documentation/vision/visionobservation/confidence)
- [CoreMLRequest](https://developer.apple.com/documentation/vision/coremlrequest)
- [VisionKit](https://developer.apple.com/documentation/visionkit/)
- [SpeechAnalyzer](https://developer.apple.com/documentation/speech/speechanalyzer)
- [SpeechTranscriber](https://developer.apple.com/documentation/speech/speechtranscriber)
- [AssetInventory](https://developer.apple.com/documentation/speech/assetinventory)
- [TranslationSession](https://developer.apple.com/documentation/translation/translationsession)
- [LanguageAvailability](https://developer.apple.com/documentation/translation/languageavailability)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Form](https://developer.apple.com/documentation/swiftui/form)
- [NavigationStack](https://developer.apple.com/documentation/swiftui/navigationstack)
- [TextEditor](https://developer.apple.com/documentation/swiftui/texteditor)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
