# Speech, Translation, and Language

## Speech

Use Speech for live or recorded audio recognition. Modern speech APIs provide analysis sessions and transcription modules; choose the module that matches live conversation, dictation-like input, or an audio asset. Define partial, final, unavailable, and cancelled transcript states.

Before microphone capture, request authorization and configure the audio session intentionally. Handle interruptions, route changes, microphone denial, missing assets, and the person stopping capture. Do not store or upload transcripts by default when the workflow can remain local.

### Modern Speech analyzer route

For current Swift speech analysis, compose a `SpeechAnalyzer` with modules such as `SpeechTranscriber`, provide audio through an asynchronous input sequence, consume module results through an `AsyncSequence`, and finish or cancel the analysis explicitly. This is a streaming state machine, not a single synchronous “transcribe” function:

`permission -> locale/module check -> assets -> input sequence -> analyzing -> volatile result -> finalized result -> finished/cancelled`

`SpeechTranscriber` can provide progressive or final results depending on its preset/options. Volatile text may be revised as more audio arrives; keep it separate from finalized text and do not execute an action from a volatile result. Check `isAvailable`, installed/supported locales, and the required speech assets before starting. The analyzer can only analyze one input sequence at a time, so decide what happens when a new recording replaces an existing one.

The older `SFSpeechRecognizer` route has its own authorization, availability, locale, and on-device-support properties. Its documentation describes server-based recognition for the permission flow and notes that some languages may require a network connection. Do not label every Speech API as “on device”; record the exact API/module, locale, asset state, and data path selected by the target.

## Translation

The Translation framework can show system translation UI or provide a TranslationSession for custom flows. Translation sessions operate on device, but the required source and target language assets may not be installed. Check language availability, prepare downloads when appropriate, and provide an untranslated fallback.

Use `LanguageAvailability` to distinguish unsupported, supported-but-not-installed, and installed language pairs. `TranslationSession.isReady`, `canRequestDownloads`, `prepareTranslation()`, `translate`, `translations`, and `cancel()` define different states that should be visible in the product. Preserve the original text and any user edits; a translated string is a derived representation, not an overwrite of the source.

For an editable document, preserve the original text and treat the translation as a derived version. For a user-facing message, show the selected source and target language and make it easy to switch or retry.

## Natural Language

Natural Language provides deterministic language analysis such as tokenization, tagging, language identification, sentiment, and embeddings. It is a better route than a generative model when the result can be expressed as a known analysis and the app does not need open-ended text generation.

## Sound Analysis

Sound Analysis can classify audio content. Use it for bounded sound categories and treat confidence as a signal for review or thresholding, not proof of identity or intent.

## Common language pipeline

audio or text -> permission/asset check -> device analysis -> confidence/availability state -> user-visible result -> optional persistence

Keep the original content and derived result separate. If the result will trigger a side effect, require an explicit confirmation or deterministic rule.

## Audio lifecycle contract

Speech analysis and audio capture have separate responsibilities. `AVAudioSession` communicates the app’s intended audio behavior to the system, while the capture engine or input provider supplies samples. Model these states explicitly:

| State | Required decision |
| --- | --- |
| Permission | Is microphone and speech-recognition authorization granted, denied, restricted, or not yet requested? |
| Route | Which microphone/output is active, and what happens when headphones, Bluetooth, a call, or a route disconnect changes it? |
| Interruption | Does the app pause, finish, discard, or resume after a system interruption? |
| Capture | Is the input sequence accepting buffers, dropping frames, or backpressuring the source? |
| Analysis | Are results volatile, final, unavailable, or failed? |
| Stop | Does the input sequence finish before the analyzer is finalized, and what draft is preserved? |

Do not resume audio blindly after every interruption. Inspect the interruption/route state, update the UI, and ask the person to resume when the product cannot safely continue.

## Verification route

- Test accents, code-switching, background noise, silence, overlapping speakers, numbers, names, and punctuation.
- Test permission changes, route changes, phone calls, background/foreground, cancellation, and low connectivity.
- Evaluate word/term accuracy and downstream action precision separately.
- Test every supported language/locale with native or expert review for user-facing claims.
- Keep a manual text input fallback and never claim “on device” without API-specific evidence.
- Test SpeechAnalyzer asset installation, unsupported/installed locales, progressive versus final results, analyzer cancellation, replacement input, and resource exhaustion.
- Test Translation language statuses, download consent, unavailable pairs, cancellation, original-text preservation, and user edits.
- Test speaker/microphone route changes, silent mode, interruptions, Bluetooth disconnects, phone calls, backgrounding, and thermal/battery behavior on physical devices.

## Sources

- [Speech](https://developer.apple.com/documentation/speech/)
- [Recognizing speech in live audio](https://developer.apple.com/documentation/speech/recognizing-speech-in-live-audio)
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
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Handling audio interruptions](https://developer.apple.com/documentation/AVFAudio/handling-audio-interruptions)
- [Responding to audio route changes](https://developer.apple.com/documentation/AVFAudio/responding-to-audio-route-changes)
