# Speech, Translation, and Language Routes

## Capability

Speech, Translation, Natural Language, and Sound Analysis cover narrower on-device or system-assisted intelligence workflows. Pick the framework that matches the measurable output; then combine it with SwiftUI and Foundation Models only when each layer has a clear responsibility.

## Route selection

| User outcome | First route | Important caveat |
| --- | --- | --- |
| Transcribe live or recorded speech | Speech framework | Permission, audio route, locale/assets, and server/on-device behavior vary by API. |
| Translate text or supported content | Translation framework | Language availability, user experience, and translation quality must be checked. |
| Classify or tag text | Natural Language | Use a defined language/task model and test multilingual input. |
| Detect/classify sounds | Sound Analysis | Capture permission, model quality, background noise, and device behavior matter. |
| Turn a transcript into a structured action | Speech -> review -> Foundation Models guided output | Never let a transcript directly execute a high-impact side effect. |

## Speech route

1. Explain why the app needs the microphone and/or speech recognition.
2. Request the appropriate authorization at first use.
3. Select the input source, locale, and analyzer/transcriber route supported by the target SDK.
4. Stream or process audio with cancellation and interruption handling.
5. Render partial versus final transcription distinctly.
6. Keep the transcript editable and reviewable before using it as a command or record.

Apple’s Speech APIs are not all equivalent from a privacy perspective. The `SFSpeechRecognizer` authorization documentation describes audio being sent to Apple’s servers, while newer analyzer/transcriber routes have different processing behavior. Verify the exact API and OS behavior instead of labeling the entire feature “on device.”

### SpeechAnalyzer route

For the modern analyzer path, choose a `SpeechTranscriber` locale/preset, ensure its assets are installed or prepare the installation, create a capture/file input sequence, construct the `SpeechAnalyzer`, consume the transcriber’s asynchronous results, and explicitly finalize or cancel. Keep volatile results in a draft buffer and promote only finalized or user-reviewed text to a command or record.

The analyzer’s input, output, and control streams are decoupled. That makes cancellation and lifecycle behavior part of the design: a view disappearing, a new recording starting, or a phone call interrupting audio should stop or replace the input sequence and close the analysis session deliberately.

## Translation and language route

Translation is a system capability with its own language availability and UI/session behavior. Keep source text, translated text, language identifiers, and user edits separate. Natural Language tagging/classification can provide deterministic labels for a narrower task than a generative model.

Use `LanguageAvailability.status(from:to:)` before presenting a custom translation action. Distinguish an unsupported pair from an installable pair and an installed/ready pair. If the person agrees to a language download, show preparation/progress and keep the original text available while the session is not ready. `TranslationSession` can translate one string, attributed text, or a batch; choose the smallest route that preserves the user’s formatting and review needs.

## Combining routes safely

`microphone -> transcription -> user review -> typed action proposal -> deterministic policy -> optional App Intent`

Do not skip the review/policy step because the phrase “turn on the lights,” “send this,” or “save this health note” sounds unambiguous. A transcript can be wrong, incomplete, or spoken by someone without authorization.

For translation and audio classification, keep the source and derived result side by side. A translated instruction or sound classification can inform the UI without becoming an external side effect. Require a deterministic policy and explicit confirmation for sending, purchasing, deleting, unlocking, or changing sensitive records.

## Failure modes

- Permission denied, microphone unavailable, no language assets, unsupported locale, network unavailable, interruption, and partial transcript.
- Background audio or speech requires separate lifecycle and entitlement review.
- Translation or classification can be unavailable or lower quality for a language; show the language pair and allow manual correction.
- Audio/transcripts may contain sensitive personal data; minimize retention and redact logs.
- Analyzer resources may be limited; handle an insufficient-resources failure and do not create unbounded concurrent transcription sessions.
- Volatile transcripts can be revised; do not treat a partial phrase as final command input.

## Verification route

- Test accents, code-switching, background noise, silence, overlapping speakers, numbers, names, and punctuation.
- Test permission changes, route changes, phone calls, background/foreground, cancellation, and low connectivity.
- Evaluate word/term accuracy and downstream action precision separately.
- Test every supported language/locale with native or expert review for user-facing claims.
- Keep a manual text input fallback and never claim “on device” without API-specific evidence.
- Test analyzer asset installation and cancellation, progressive/final result handling, audio route changes, and interruption recovery on physical devices.

## Sources

- [Speech](https://developer.apple.com/documentation/speech/)
- [Asking permission to use speech recognition](https://developer.apple.com/documentation/speech/asking-permission-to-use-speech-recognition)
- [SpeechAnalyzer](https://developer.apple.com/documentation/speech/speechanalyzer)
- [SpeechTranscriber](https://developer.apple.com/documentation/speech/speechtranscriber)
- [SpeechTranscriber.Preset](https://developer.apple.com/documentation/speech/speechtranscriber/preset)
- [SpeechTranscriber.Result](https://developer.apple.com/documentation/speech/speechtranscriber/result)
- [AssetInventory](https://developer.apple.com/documentation/speech/assetinventory)
- [SFSpeechRecognizer](https://developer.apple.com/documentation/speech/sfspeechrecognizer)
- [Translation](https://developer.apple.com/documentation/translation)
- [TranslationSession](https://developer.apple.com/documentation/translation/translationsession)
- [LanguageAvailability](https://developer.apple.com/documentation/translation/languageavailability)
- [Natural Language](https://developer.apple.com/documentation/naturallanguage)
- [Sound Analysis](https://developer.apple.com/documentation/soundanalysis)
- [AVFoundation](https://developer.apple.com/documentation/avfoundation/)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Handling audio interruptions](https://developer.apple.com/documentation/AVFAudio/handling-audio-interruptions)
- [Responding to audio route changes](https://developer.apple.com/documentation/AVFAudio/responding-to-audio-route-changes)
- [App Intents](https://developer.apple.com/documentation/appintents/)
