# Blueprint: Voice-to-Localized Notebook

## Product outcome

Let a person speak a note, review the transcript, optionally translate it into an installed language, and save/share the approved result without treating speech recognition, translation, or model output as the original record.

## Route composition

`SwiftUI + Observation -> AVAudioSession/capture -> SpeechAnalyzer/SpeechTranscriber -> review -> TranslationSession -> optional Foundation Models typed organization -> SwiftData -> AppEntity/AppIntent/ShareLink`

| Layer | Route | Ownership |
| --- | --- | --- |
| Shell | SwiftUI `NavigationStack`, `Form`, `TextEditor`, `ProgressView`, native toolbar actions | Screen state, focus, accessibility, Dynamic Type, reduced motion, and original visual identity |
| Audio | AVFoundation audio session/capture | Microphone route, interruption, audio format, start/stop, and retention choice |
| Speech | `SpeechAnalyzer`, `SpeechTranscriber`, `AsyncSequence` results | Provisional/final transcript segments and locale/asset readiness |
| Translation | `TranslationSession`, configuration, installed language pair | Derived translated text, source/target metadata, batch/cancel state |
| Intelligence | Foundation Models guided output only for bounded organization | Reviewable tags/summary/draft, never the source transcript or permission authority |
| Truth | SwiftData note with source transcript and derived representations | User-approved record, timestamps, language, provenance, deletion/export |
| Surfaces | AppEntity/App Intent, ShareLink/Transferable, optional notification | Validated search/action/export projections, not hidden database access |

## State machine

`empty -> requesting-mic/speech -> preparing-locale/assets -> recording -> transcribing -> review-transcript -> translating? -> review-translation -> organizing? -> review-proposal -> saved -> shared/indexed`

Model explicit failures: permission denied/revoked, unsupported locale, missing speech/translation assets, audio interruption, partial transcript, analyzer cancellation, translation download decline, model unavailable, context overflow, invalid typed proposal, storage failure, share cancellation, and stale/deleted record.

## Native interface plan

- Use a focused recording screen with one semantic primary control whose label/value changes between “Record,” “Stop,” and “Resume.”
- Show partial speech as provisional text with a live state label; distinguish “still transcribing” from “saved.”
- Present translation and AI organization in a review sheet or editor with source text visible and a clear discard/accept action.
- Use system materials/Liquid Glass only for functional layers such as the recording control group, status capsule, or review toolbar; do not use glass behind dense text where it reduces legibility.
- Move accessibility focus into the review surface, preserve keyboard/manual entry, and test large text, VoiceOver, Voice Control, reduced motion, and reduced transparency.

## Build order

1. Build a manual note editor and SwiftData persistence with source/derived fields.
2. Add recorded-audio fixtures and a transcript review model; test partial/final segment merging.
3. Add `SpeechAnalyzer` with a locale/asset gate and manual text fallback.
4. Add `TranslationSession` only when an installed language pair is ready; preserve original text.
5. Add guided Foundation Models organization with typed output, prompt/version fixtures, and explicit human acceptance.
6. Add `Transferable`/ShareLink and an AppEntity/App Intent for a validated note action.

## Privacy and permission contract

- Request microphone/speech permission at the recording boundary, not at first launch.
- Document the exact Speech route’s processing/privacy behavior; do not infer it from the framework name.
- Keep audio retention opt-in and explicit. Default to storing only the approved transcript/derived note if the product does not need raw audio.
- Keep private note contents out of Logger/signposts, notification previews, widget snapshots, App Intent parameters, and share representations unless the person selected them.
- Reconcile permission usage descriptions, privacy manifest/App Store privacy records, and actual audio/text retention.

## Fallbacks

| Condition | Fallback |
| --- | --- |
| Microphone/speech denied | Manual text editor and imported audio if supported |
| Locale/assets unavailable | Show original language, offer another installed pair, or preserve source only |
| Translation unavailable | Keep source note and let the person retry later |
| Foundation Models unavailable | Manual tags/summary or deterministic text tools |
| Storage/share failure | Keep the draft locally and offer retry/export to a standard file |

## Proof plan

- Fixtures: transcript segmentation, translation source preservation, typed organization validation, redaction, deletion, and state rendering.
- Simulator: navigation, review UI, Dynamic Type, accessibility tree, fake permission branches, and deterministic persistence.
- Physical device: microphone/audio route, speech assets/locale, interruptions, translation readiness, thermal/energy behavior, VoiceOver/Voice Control tasks, and signed system-surface invocation.
- Release: privacy report, App Store Connect App Privacy, bundle resources, App Intent metadata, share representations, TestFlight behavior, and production claims separately.

## Sources

- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [AVFoundation](https://developer.apple.com/documentation/avfoundation)
- [SpeechAnalyzer](https://developer.apple.com/documentation/speech/speechanalyzer)
- [SpeechTranscriber](https://developer.apple.com/documentation/speech/speechtranscriber)
- [TranslationSession](https://developer.apple.com/documentation/translation/translationsession)
- [TranslationSession.Strategy](https://developer.apple.com/documentation/translation/translationsession/strategy)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SwiftData](https://developer.apple.com/documentation/swiftdata)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- [Core Transferable](https://developer.apple.com/documentation/coretransferable)
- [ShareLink](https://developer.apple.com/documentation/swiftui/sharelink)
- [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- [Performing accessibility testing for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)
