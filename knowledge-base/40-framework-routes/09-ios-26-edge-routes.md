# iOS 26 Edge Routes: Speech, Translation, Transfer, and Continuous Work

This card covers routes that are easy to misuse because they look like ordinary async functions but cross device assets, user permissions, system surfaces, host processes, or resource limits. Select a route from the user outcome, then carry its state and evidence contract into the app plan.

## Route map

| User outcome | Primary symbols | Core state | Minimum fallback |
| --- | --- | --- | --- |
| Transcribe a live microphone stream or audio file | `SpeechAnalyzer`, `SpeechTranscriber`, `AssetInventory`, `CaptureInputSequenceProvider`, `AnalyzerInputConverter` | Locale/asset readiness, input sequence, partial/final results, cancellation, finish | Recorded/manual text entry, unsupported-locale message, or an imported audio workflow |
| Translate text while preserving source and formatting | `TranslationSession`, `TranslationSession.Configuration`, `TranslationSession.Request`, `TranslationSession.Response` | Installed language pair, download permission, ready/not-ready, batch progress, cancellation | Show original text, let the person choose another language, or use an explicit remote route only if the product allows it |
| Share a domain record through Apple system interactions | `Transferable`, `TransferRepresentation`, `CodableRepresentation`, `DataRepresentation`, `FileRepresentation`, `ProxyRepresentation`, `UTType`, `ShareLink` | Export representation, destination capability, file staging, cancellation, retention | Copy a safe textual projection or export a user-visible file through a standard system route |
| Continue a user-started job after the app backgrounds | `BGContinuedProcessingTaskRequest`, `BGContinuedProcessingTask`, `ProgressReporting` | Foreground initiation, queued/accepted/rejected, progress, cancel, expiration, checkpoint, completion | Keep the task foreground, pause/resume later, or use `BGProcessingTask` for deferred maintenance when appropriate |

## SpeechAnalyzer and SpeechTranscriber

### Responsibility boundary

`SpeechAnalyzer` is an actor that owns an analysis session. Modules such as `SpeechTranscriber` produce analysis results asynchronously; input and output are represented as sequences that the app creates and consumes. The analyzer handles one input sequence at a time. Do not treat a partial transcription as final domain text, and do not let a view own the entire audio-session lifecycle.

### Build route

1. Resolve a supported locale and inspect `AssetInventory` for the required speech assets.
2. Request microphone/speech authorization immediately before the capture route; keep a recorded-audio or keyboard fallback.
3. Create the input provider and convert the audio format with the documented analyzer helpers.
4. Start the actor-owned analyzer and consume partial/final results through an `AsyncSequence`.
5. Render partial text as provisional UI, preserve final segments with timestamps/source metadata, and finish/cancel the analyzer when the route ends.
6. Send only the bounded transcript needed by later parsing or Foundation Models proposal generation; retain the source audio only when the product has a clear user-facing reason.

### State contract

`idle -> checking-locale/assets -> requesting-permission -> preparing-input -> transcribing -> finalizing -> finished`

Terminal/error branches include `denied`, `unsupported-locale`, `assets-missing`, `input-interrupted`, `canceled`, `analyzer-failed`, and `partial-only`. A process termination must not leave the UI showing “saved” when only a partial stream existed.

### Proof boundary

Fixtures can validate transcript parsing, segment merging, typed proposal validation, and review UI. A simulator or preview does not prove microphone routing, asset installation, locale quality, interruption recovery, background audio policy, energy use, or physical-device capture. Test the selected Speech API’s actual processing/privacy behavior; do not label the whole Speech framework “on device” without checking the exact route.

## TranslationSession

### Responsibility boundary

`TranslationSession` translates between installed source/target languages. A SwiftUI `.translationTask` route is convenient for view-owned work; direct initialization is available for contexts without UI. `prepareTranslation()` can ask to download language assets, while `isReady` and `canRequestDownloads` describe the current session state. The source text remains the app’s source of truth; a translation is a derived representation that can fail, be stale, or require correction.

### Build route

- Preserve the original text and language metadata beside every translated result.
- Surface the language pair and asset state before starting a large batch.
- Use `TranslationSession.Request`/batch APIs for repeated text rather than creating an unbounded task per line.
- Use `TranslationSession.Strategy.lowLatency` or `.highFidelity` only as a product tradeoff to evaluate; availability and behavior remain device/OS/language dependent.
- Cancel or invalidate work when the source text or language configuration changes, and associate responses with stable request IDs.
- Keep the original text visible in review/export flows; never replace user-authored content silently.

### State contract

`source-ready -> checking-language-assets -> preparing-download -> ready -> translating -> partially-translated|translated -> reviewed/exported`

Model `not-installed`, `download-declined`, `unsupported-pair`, `network/asset-error`, `canceled`, `source-changed`, and `translation-failed`. The system may process translations on device, but current Apple documentation notes that Apple may collect API usage/performance metrics; document the exact route’s privacy behavior instead of generalizing from “on device.”

### Proof boundary

Use deterministic multilingual fixtures for formatting, placeholders, source preservation, and UI adaptation. Use representative physical devices and installed language assets for readiness, latency, memory, thermal behavior, and quality review. A translated string is not proof of legal, medical, cultural, or factual correctness.

## Transferable, ShareLink, and file representations

### Responsibility boundary

`Transferable` describes how a model participates in system data-transfer contexts such as sharing, drag and drop, copy/paste, and other supported destinations. Choose representations deliberately:

| Representation | Use when | Boundary |
| --- | --- | --- |
| `CodableRepresentation` | The receiving side understands a codable domain format | Version the schema and avoid exporting secrets/private fields accidentally. |
| `DataRepresentation` | The app owns a binary or text encoding | Validate size, content type, and cancellation; do not assume every destination accepts it. |
| `FileRepresentation` | A file is the most interoperable product artifact | Stage safely, handle security scope/temporary lifetime, and clean up after transfer. |
| `ProxyRepresentation` | A safe projection such as text/URL is the right fallback | Make the projection privacy-reviewed and truthful; it may lose domain fields. |

Use `UTType` for exported/imported content types and `ShareLink` for the system share presentation. A `SharePreview` is presentation metadata, not the authoritative record. A share action can fail because the destination does not support a representation, a file cannot be staged, the user cancels, or content is too large.

### State contract

`record-ready -> selecting-representation -> staging -> presenting-share -> transferred|canceled|failed -> cleanup`

Keep export state separate from domain persistence. Do not mark a record exported until the app receives the documented completion/result for the chosen route. Redact private fields and ensure a widget, notification, or App Intent cannot accidentally export more than the person selected.

### Proof boundary

Unit tests can validate `Transferable` representations and UTType declarations. Test real destinations on supported systems with small and large payloads, cancellation, no compatible service, file-provider errors, locked device, and revoked access. A `ShareLink` preview or simulator share sheet does not prove that Mail, Messages, Files, AirDrop, or a third-party destination accepts every representation.

## BGContinuedProcessingTask

### Responsibility boundary

`BGContinuedProcessingTask` is for a person-started job that begins in the foreground and may continue after the app backgrounds. The system shows progress in a Live Activity and allows cancellation, but can terminate the task under resource constraints. It is not a hidden scheduler, daemon, or guarantee that AI/media processing reaches a deadline.

### Build route

1. Make the work explicit and user-started in the foreground; explain what may continue after backgrounding.
2. Submit a `BGContinuedProcessingTaskRequest` with localized title/subtitle and the supported submission/resource configuration for the selected SDK.
3. Persist a versioned job record and checkpoint before submitting. Make each unit idempotent and resumable.
4. Implement the task handler with bounded concurrency, progress reporting, cancellation, expiration cleanup, and a final durable state.
5. Update the system-visible progress truthfully. Never present a completed Live Activity while the durable job is only queued or partial.
6. Offer pause/resume or foreground continuation when the request is rejected, canceled, or resources become constrained. Use `BGProcessingTask` only when the product actually fits deferred system-scheduled work.

### State contract

`draft -> foreground-started -> submitted -> queued|running -> paused|canceling -> completed|failed|canceled|expired`

Record rejection reason/availability, progress, last completed unit, cancellation source, resource/thermal state, and recovery action. On relaunch, reconcile the durable job with the system surface and remove stale progress rather than assuming the task completed.

### Proof boundary

The debugger’s task controls prove only handler behavior. Test a signed physical device for foreground initiation, background transition, Live Activity progress, cancellation, expiration, memory/energy behavior, resume/relaunch, and supported GPU/entitlement paths. A successful submission is not proof that the system ran the task or that production resources will permit it.

## Composition patterns

| Product pattern | Compose | Keep explicit |
| --- | --- | --- |
| Voice capture to translated note | SpeechAnalyzer -> reviewable transcript -> TranslationSession -> SwiftData -> ShareLink | microphone/speech authorization, locale/assets, source text, translation privacy, review, export representation |
| Media batch export | PhotosUI/AVFoundation -> deterministic processing -> BGContinuedProcessingTask -> ActivityKit -> FileDocument/ShareLink | user start, progress/checkpoint, cancellation, thermal/resource state, file lifetime, signed-device proof |
| Localized field assistant | AppEntity/local record -> TranslationSession -> Foundation Models proposal -> SwiftUI review -> App Intent | bounded context, language readiness, model availability, mutation confirmation, system-surface privacy |

## Sources

- [Speech](https://developer.apple.com/documentation/speech/)
- [SpeechAnalyzer](https://developer.apple.com/documentation/speech/speechanalyzer)
- [SpeechTranscriber](https://developer.apple.com/documentation/speech/speechtranscriber)
- [AssetInventory](https://developer.apple.com/documentation/speech/assetinventory)
- [Translation](https://developer.apple.com/documentation/translation)
- [TranslationSession](https://developer.apple.com/documentation/translation/translationsession)
- [TranslationSession.Configuration](https://developer.apple.com/documentation/translation/translationsession/configuration)
- [TranslationSession.Strategy](https://developer.apple.com/documentation/translation/translationsession/strategy)
- [Core Transferable](https://developer.apple.com/documentation/coretransferable)
- [Transferable](https://developer.apple.com/documentation/coretransferable/transferable)
- [TransferRepresentation](https://developer.apple.com/documentation/coretransferable/transferrepresentation)
- [ShareLink](https://developer.apple.com/documentation/swiftui/sharelink)
- [Uniform Type Identifiers](https://developer.apple.com/documentation/uniformtypeidentifiers)
- [Background Tasks](https://developer.apple.com/documentation/backgroundtasks)
- [BGContinuedProcessingTask](https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtask)
- [BGContinuedProcessingTaskRequest](https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtaskrequest)
- [Performing long-running tasks on iOS and iPadOS](https://developer.apple.com/documentation/backgroundtasks/performing-long-running-tasks-on-ios-and-ipados)
- [ProgressReporting](https://developer.apple.com/documentation/foundation/progressreporting)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
