# SwiftUI audio capture and transcription

## Purpose

Audio features feel native when the microphone, audio session, engine, speech
analyzer, classifier, transcript, and review destination have different
owners and visible states.

Use this flow:

~~~text
permission and intent
    -> configure audio route
    -> capture or choose an audio asset
    -> bounded input sequence
    -> progressive transcript and optional sound observations
    -> finalized transcript / time-linked review
    -> optional local AI proposal
    -> user review
    -> save, export, share, or discard
~~~

The waveform is not the source of truth. A partial transcript is not a final
record. A sound classification is not proof of a physical event. A generated
summary is not an authorization to mutate the user's record.

This page adds the SwiftUI orchestration seam to the existing [Speech,
Translation, and Language route](../30-on-device-ai/05-speech-translation-and-language.md),
[SoundAnalysis deep dive](30-soundanalysis-on-device-audio-classification.md),
and [AVFoundation media pipeline](09-avfoundation-media-pipeline.md).

## Choose the input route

| Need | Primary route | SwiftUI boundary |
| --- | --- | --- |
| Live dictation or conversation | SpeechAnalyzer + SpeechTranscriber | Audio service owns capture; view renders volatile/final transcript |
| Recorded audio transcription | SpeechAnalyzer + AssetInputSequenceProvider | App-owned URL and revision own the review |
| Microphone speech input | SpeechAnalyzer + CaptureInputSequenceProvider or app-owned AVAudioEngine adapter | Permission, route, and input lifecycle are explicit |
| Custom audio buffering | AVAudioEngine + AVAudioInputNode + AnalyzerInputConverter | A bounded actor/sequence bridges buffers into the analyzer |
| Sound categories | SNAudioStreamAnalyzer | Sound result is time-ranged observation, not transcript truth |
| Saved-file sound review | SNAudioFileAnalyzer | File URL and analyzer completion are separate from playback |
| Record and reopen | AVAudioEngine/AVAudioFile or AVAudioRecorder | App-owned file identity and cleanup precede analysis |
| Play a recording | AVKit VideoPlayer or AVPlayerViewController | Player lifetime belongs to review state |
| Visualize amplitude | Meter/waveform derived from buffers | Derived visualization is cancellable and does not retain raw audio |
| Summarize or organize | Foundation Models after deterministic results | Typed candidate with source revision and explicit commit |

The right route depends on whether the feature needs live input, a saved
asset, a time-indexed transcript, sound labels, audio playback, or a file that
can be exported. Do not start with a waveform and infer the rest of the
architecture from it.

## Route contract

Record these decisions before implementing a screen.

| Field | Required decision |
| --- | --- |
| User outcome | Dictate, record, transcribe, search, classify, review, export, or organize |
| Audio source | Live microphone, app-owned file, imported file, system media, or no audio |
| Source identity | Recording ID, asset URL/file ID, session ID, and source revision |
| Permission | AVAudioApplication recording state, speech module readiness, and purpose strings |
| Audio session | Category, mode, options, activation, input/output route, interruption policy |
| Engine owner | Which service owns AVAudioEngine, input node, tap, converter, and teardown? |
| Buffer handoff | Input format, frame/time mapping, bounded queue/sequence, backpressure and drop policy |
| Speech module | SpeechTranscriber or another SpeechModule, locale, preset, reporting options |
| Assets | Supported/installed/downloading/unsupported Speech assets and download consent |
| Transcript | Volatile versus final, alternatives, attributes, time ranges, and revision |
| Sound analysis | Built-in/custom model, labels, confidence, windows, time ranges, threshold |
| File | Format, path ownership, duration, size, metadata, retention, and deletion |
| Review | What is shown as source, draft, observation, suggestion, or committed record? |
| AI | Typed context, model availability, candidate schema, privacy, stale policy |
| Destination | App store, export/share, transcription document, or discard |
| Lifecycle | Stop, background, interruption, route change, cancellation, and recovery |
| Visual shell | Recording, paused, processing, review, permission, and error composition |
| Targets | iPhone/iPad, Catalyst, watchOS companion, CarPlay, extension, and physical proof |

## 1. Establish source and recording identity

The audio URL, input sequence, buffer, transcript result, and player are
representations. Create an app-owned identity before recording or importing.

~~~swift
enum AudioEntry: Sendable, Equatable {
    case live(recordingID: UUID)
    case imported(fileID: UUID)
    case existing(documentID: UUID)
}

struct AudioSourceState: Sendable, Equatable {
    let entry: AudioEntry
    var sourceRevision: Int
    var fileURL: URL?
    var contentTypeIdentifier: String?
    var duration: Double?
    var sampleRate: Double?
    var channelCount: Int?
    var permission: PermissionState
    var session: AudioSessionState
    var capture: CaptureState
    var transcript: TranscriptState
    var soundObservations: [SoundObservation]
    var review: AudioReviewState
    var destination: AudioDestinationState
}
~~~

Keep source revision separate from transcript revision. A live transcript can
be revised without changing the audio source. A new recording must invalidate
the old analysis even if the same filename is reused. A new route or locale
may require a new analyzer revision while the audio file remains unchanged.

Useful state categories:

- permission: undetermined, granted, denied;
- session: inactive, configuring, active, interrupted, routeChanged, failed;
- capture: idle, preparing, listening, paused, stopping, finalized, failed;
- assets: unsupported, supported, downloading, installed, failed;
- transcript: none, volatile, finalizing, finalized, stale, failed;
- observation: none, running, partial, complete, uncertain, stale, failed;
- review: source, draft, reviewing, accepted, edited, committed;
- destination: app, export, share, discarded, failed.

Never model the feature with one isRecording Boolean. A session may be active
while an analyzer is unavailable. A recording may be finalized while the
transcript is still being reviewed. A final transcript may be stale after the
person edits the audio's associated record.

## 2. Microphone permission is a product boundary

Use AVAudioApplication for the current recording permission route in the
selected SDK. Include a truthful NSMicrophoneUsageDescription value in the
target's processed Info.plist. Without permission, the system supplies silence
to recording input; a green-looking waveform must not imply that real audio is
being captured.

~~~swift
@MainActor
final class AudioPermissionModel: ObservableObject {
    enum State: Equatable {
        case undetermined
        case granted
        case denied
    }

    @Published private(set) var state: State = .undetermined

    func refresh() {
        switch AVAudioApplication.shared.recordPermission {
        case .undetermined:
            state = .undetermined
        case .granted:
            state = .granted
        case .denied:
            state = .denied
        @unknown default:
            state = .denied
        }
    }

    func request() async {
        state = await AVAudioApplication.requestRecordPermission()
            ? .granted
            : .denied
    }
}
~~~

Request permission when the person chooses a recording action, not merely when
the app launches. If denied, keep imported-file, typed-note, or manual-review
routes useful. Explain that a Settings change is required after denial, and
refresh state when the scene becomes active.

Speech module availability and microphone permission are independent gates.
SpeechTranscriber may be unavailable for the target hardware or locale even
when a microphone is granted. AssetInventory may report supported but not yet
installed, downloading, installed, or unsupported. Render those states
separately.

## 3. Own AVAudioSession and route policy

AVAudioSession communicates intended audio behavior to the system. It does not
replace the engine, input node, speech analyzer, or app-level state. Configure
the category and mode for the real feature, activate only when needed, and
deactivate on a deliberate stop.

~~~swift
final class AudioSessionOwner {
    private let session = AVAudioSession.sharedInstance()

    func beginCapture() throws {
        try session.setCategory(
            .record,
            mode: .measurement,
            options: []
        )
        try session.setActive(true)
    }

    func endCapture() {
        try? session.setActive(
            false,
            options: [.notifyOthersOnDeactivation]
        )
    }

    var currentRouteDescription: String {
        session.currentRoute.inputs
            .map { "\($0.portType.rawValue):\($0.portName)" }
            .joined(separator: ", ")
    }
}
~~~

This is a route sketch. A feature that records and plays speech may need a
play-and-record category, a voice-processing mode, Bluetooth options, or a
different activation strategy. Verify the selected target and test built-in
mic, wired/Bluetooth routes, speaker output, phone calls, Siri, alarms,
headset disconnect, and screen lock.

Observe interruption and route-change notifications. The route-change
notification can arrive on a secondary thread. Convert notifications into
state events on the service owner, then update SwiftUI on the main actor.
Do not blindly resume after every interruption. Inspect whether the session
should remain active and whether the current input route is still suitable.

## 4. Own AVAudioEngine and the input tap

AVAudioEngine owns a graph of audio nodes and real-time rendering constraints.
The input node exposes microphone samples. The service owns engine start/stop,
tap installation/removal, format inspection, buffer conversion, and teardown.
SwiftUI only sends start/stop/retry intent.

~~~swift
final class AudioInputEngine {
    let engine = AVAudioEngine()
    private let queue = DispatchQueue(
        label: "com.example.audio-input"
    )
    private var tapInstalled = false

    func start(
        onBuffer: @escaping @Sendable (
            AVAudioPCMBuffer,
            AVAudioTime
        ) -> Void
    ) throws {
        let input = engine.inputNode
        let format = input.outputFormat(forBus: 0)
        guard format.sampleRate > 0, format.channelCount > 0 else {
            throw AudioInputError.noUsableFormat
        }

        if !tapInstalled {
            input.installTap(
                onBus: 0,
                bufferSize: 2048,
                format: format
            ) { buffer, time in
                onBuffer(buffer, time)
            }
            tapInstalled = true
        }

        try engine.start()
    }

    func stop() {
        queue.sync {
            if tapInstalled {
                engine.inputNode.removeTap(onBus: 0)
                tapInstalled = false
            }
            engine.stop()
            engine.reset()
        }
    }
}
~~~

The callback is a real-time-adjacent boundary. Avoid blocking file I/O,
unbounded allocations, network calls, logging storms, or SwiftUI mutations
inside it. Use a bounded handoff to an analyzer input sequence or an audio-file
writer. If the hardware format changes, stop the old analyzer/tap and rebuild
the conversion path for the current format.

On newer SDKs, installAudioTap can provide a sendable tap boundary. Choose
the API that matches the target deployment and concurrency model. A compile
success does not prove that the callback is safe for the chosen workload.

## 5. Choose a Speech input provider

Speech exposes input sequence providers for microphone capture and audio assets,
as well as AnalyzerInput and AnalyzerInputConverter routes. These can reduce
custom conversion code, but the selected provider's availability and exact
configuration still belong in the target's source and proof record.

| Provider | Use when | Proof |
| --- | --- | --- |
| CaptureInputSequenceProvider | Speech owns microphone-to-analyzer input | Physical microphone, permission, route, provider lifecycle |
| AssetInputSequenceProvider | A file/asset is already app-owned | File format, duration, end-of-input, cancellation |
| AnalyzerInputConverter | App owns AVAudioEngine buffers | Input/output formats, timestamps, conversion failure |
| Custom AsyncSequence | Product needs a specialized buffer source | Backpressure, time mapping, finish/cancel semantics |

Do not feed arbitrary objects into a speech analyzer. Preserve audio time and
finish the sequence when capture reaches a deliberate end. A new recording
should finish/cancel the old input before the new analyzer takes ownership.

## 6. SpeechAnalyzer is a session actor

SpeechAnalyzer manages an analysis session around one or more SpeechModules.
SpeechTranscriber is appropriate for general conversation and exposes an
asynchronous result sequence. Check isAvailable and supported/installed locales
before presenting Start.

The pipeline is:

~~~text
create module
    -> check device/locale
    -> inspect AssetInventory
    -> reserve/download/install if needed
    -> create input sequence/provider
    -> create SpeechAnalyzer
    -> consume SpeechTranscriber.results
    -> start
    -> feed live/file input
    -> finish or cancel input
    -> finalize analyzer
~~~

SpeechTranscriber presets express different product tradeoffs. Progressive
presets can deliver volatile and fast results. Time-indexed presets associate
transcript content with source audio time. Alternatives and finalization
options affect the review contract. Choose a preset intentionally and record
it with the transcript revision.

AssetInventory models are managed by the system and may be downloaded from
Apple's servers, retained, updated, shared with other apps, or released by
the system according to its asset policy. The app owns readiness copy and
download consent; it does not own the model files as ordinary app assets.

## 7. Keep volatile and final transcript content separate

SpeechTranscriber.Result can be delivered more than once for a range when
volatile results are enabled. A result includes text, finalization state, and
may include time-range and confidence attributes. Preserve the range and
source revision when the UI needs synchronized highlighting.

~~~swift
struct TranscriptSegment: Sendable, Equatable {
    let segmentID: UUID
    let sourceRevision: Int
    let audioRangeDescription: String
    var text: String
    var confidence: Double?
    var isFinal: Bool
}

struct TranscriptState: Sendable, Equatable {
    var revision: Int
    var volatile: [TranscriptSegment]
    var finalized: [TranscriptSegment]
    var alternatives: [[String]]
    var errorMessage: String?
}
~~~

Render volatile text as a draft. Do not save it as the canonical transcript,
execute a command from it, or tell the person it is final. When a final result
arrives, replace the matching source range rather than appending blindly.
Capture a transcript revision for any search, summary, tag, or AI request.

For an editable transcript, keep audio source, transcript segments, and user
edits separate. A person may correct spelling without changing the audio.
Never rebuild a user-edited transcript from the next volatile result without
an explicit merge policy.

## 8. Add SoundAnalysis as a parallel observation route

SoundAnalysis can process a saved file with SNAudioFileAnalyzer or a PCM stream
with SNAudioStreamAnalyzer. SNClassifySoundRequest can use Apple's built-in
classifier or a custom Core ML model. SNClassificationResult provides
time-ranged classification candidates.

Keep it parallel to transcription:

~~~text
same source audio
    -> speech transcript segments
    -> sound classification time ranges
    -> review timeline
~~~

The analyzer must match its input type and format. Keep the observer strongly
because the audio analyzers do not keep it strongly. A sound label is a model
observation with confidence, window, model revision, and uncertainty; it is
not a medical, identity, emergency, or physical-event fact.

Use thresholds, temporal debounce, and an unknown/ambiguous state before
showing a tag or proposing an action. Keep raw audio retention separate from
derived labels. If an audio route changes format, recreate the stream
analyzer instead of merging incompatible windows.

## 9. Record or import an app-owned audio file

When the person expects to reopen, export, or analyze later, create an
app-owned copy with a stable recording ID. Store file format, duration,
sample-rate/channels, source revision, metadata policy, and deletion policy.

A file URL is not the same as an audio identity. A temporary provider URL,
security-scoped URL, or imported file can expire or be replaced. Copy only
when the feature needs durable ownership, and clean up failed/abandoned
derived files.

Use AVAudioFile or an appropriate recorder/writer for the target format.
Measure file size and duration before starting an expensive transcription or
classifier route. Never claim that the file is finalized until the writer has
closed successfully and the file can be reopened.

## 10. Review audio with AVKit and time-linked content

Use AVKit for native playback controls when the asset/player route is
appropriate. VideoPlayer provides a SwiftUI playback view; AVPlayerViewController
is the controller route when the product needs its native presentation or
platform-specific behavior.

Keep player state and transcript state separate:

- player time selects a review range;
- transcript segments can seek the player;
- sound observations can mark time ranges;
- an AI candidate references the source and transcript revision;
- playback success does not prove transcription or model success.

Do not create a new player in a frequently recreated row. Stop or pause
according to the product's lifecycle policy when the review disappears.
Observe interruption and route changes for audio playback as well as capture.

## 11. Derive a waveform without making it the record

A waveform, meter, or level timeline is a derived projection of buffers. It
should have a bounded sample count and a source revision. It must continue to
work when the raw audio is not retained.

~~~swift
struct WaveformSample: Sendable, Equatable {
    let sourceRevision: Int
    let startTime: Double
    let endTime: Double
    let normalizedLevel: Double
}

func normalizedLevel(
    rms: Float,
    floor: Float = 0.0001
) -> Double {
    let safe = max(abs(rms), floor)
    let decibels = 20 * log10(safe)
    return min(max(Double((decibels + 60) / 60), 0), 1)
}
~~~

Downsample for the display width. Do not update a high-frequency SwiftUI
state value for every input buffer. Keep the audio callback lightweight and
coalesce visual updates on a controlled actor or main-actor model.

## 12. Add bounded on-device review

Use deterministic speech and sound observations first. A Foundation Models
feature can turn a user-approved transcript, selected time ranges, and sound
labels into a suggested title, action list, accessibility description, or
search tags. It should not decide whether permission was granted, whether a
recording succeeded, or whether the audio proves a real-world event.

~~~swift
struct AudioReviewInput: Codable, Sendable {
    let sourceRevision: Int
    let transcriptRevision: Int
    let finalizedText: String
    let soundLabels: [String]
    let allowedActions: [String]
}

struct AudioReviewCandidate: Codable, Sendable, Equatable {
    let candidateID: UUID
    let sourceRevision: Int
    let transcriptRevision: Int
    let title: String
    let summary: String
    let tags: [String]
    let reason: String
}
~~~

The exact Foundation Models availability, session, guided-generation, and
schema APIs are SDK- and device-sensitive. Keep unavailable, refused,
partial, malformed, cancelled, stale, and complete states visible. Validate
length, tags, links, actions, and source revisions before showing Apply.

## 13. Make review and commit distinct

The user can review a transcript, correct it, reject a label, edit a title,
or choose a destination. App persistence and external system actions happen
only after the ordinary validation path.

| State | Meaning |
| --- | --- |
| Source | Original audio/file and immutable capture facts |
| Draft | Volatile transcript, waveform, or observation projection |
| Finalized | Framework says this pass reached final input, still reviewable |
| Edited | User changed transcript/metadata/labels |
| Candidate | Optional generated suggestion tied to source revisions |
| Accepted | User approved a candidate/observation for the domain record |
| Committed | App-owned record or explicit export/save completed |
| Failed | Destination or serialization failed; source remains recoverable |

Saving a transcript to the app is not the same as exporting audio. Exporting
audio is not the same as sending a transcript to an external service. Keep
destination text explicit.

## 14. Liquid Glass recording and review shell

Use Liquid Glass for functional controls around the waveform/player:

- record, pause, stop, and elapsed-time status;
- microphone route and permission state;
- transcript readiness and analysis progress;
- playhead-linked transcript/observation review;
- accept, edit, discard, save, and export.

The control group should not obscure the transcript or waveform. A recording
state needs text and an accessible value, not only a red tint. Processing,
stale, error, and permission states need semantic labels. Provide an opaque
fallback for reduced transparency and sufficient contrast.

Do not animate every transcript update as a glass morph. Use motion to explain
state change, keep Reduce Motion useful, and keep controls stable with
Dynamic Type, keyboard, pointer, and VoiceOver.

## 15. Lifecycle, interruption, and cancellation

Model these events:

- new recording or imported file supersedes current work;
- scene enters background or becomes inactive;
- microphone permission changes in Settings;
- audio interruption begins or ends;
- input route changes or disappears;
- audio format changes;
- Speech assets download, fail, or become unavailable;
- user taps Stop, Cancel, Retake, Delete, or navigates away;
- analyzer results arrive after the source revision changed;
- app terminates before the file is finalized.

Finish or cancel the input sequence before finalizing the analyzer. Remove
engine taps before deallocating the engine. Cancel result-consumer tasks.
Discard stale transcript/model results. Keep an app-owned finalized file if
review can resume; do not assume a live input buffer or provider URL survives.

On interruption, do not resume blindly. Reconcile the session, route, engine,
analyzer, and UI. If resumption can change meaning, require the person to tap
Resume.

## 16. Target and input boundaries

| Target/input | Boundary |
| --- | --- |
| iPhone microphone | Physical permission, route, interruption, background, thermal, real speech |
| iPadOS | Split view, keyboard, pointer, route changes, large transcript |
| Mac Catalyst | File/import/playback may be stronger than microphone route; compile and Mac proof |
| watchOS companion | Prefer handoff/summaries; do not assume iPhone Speech/AVAudio route |
| CarPlay | System audio/driving restrictions; do not place a free-form editor in a driving surface |
| VoiceOver | Permission, listening, volatile/final, candidate, stale, and destination semantics |
| Keyboard/pointer | Start/stop, play/pause, seek, edit, accept, discard, export |
| Extensions | Memory, entitlements, process lifetime, and microphone restrictions differ |
| Local-first app | Raw audio and transcript remain app-owned unless explicit export occurs |

## Common failures

- Asking for microphone permission at launch with no nearby recording intent.
- Treating granted permission as proof that the current input route is usable.
- Configuring AVAudioSession in a SwiftUI body or creating a new engine per redraw.
- Installing a tap repeatedly without removing the old tap.
- Updating SwiftUI state for every buffer on the input callback.
- Feeding a new hardware format into an old analyzer.
- Ending the Speech input sequence too early or never finishing it.
- Saving volatile text as if it were finalized.
- Appending revised transcript results and duplicating phrases.
- Treating a sound label or confidence score as a fact.
- Claiming “on-device” without checking module, locale, asset, model, and network path.
- Passing a raw transcript or audio file to Foundation Models without bounded scope.
- Letting a late summary mutate a new recording.
- Calling audio playback/capture finished when the file cannot be reopened.
- Using a waveform as the only accessible control for recording state.
- Claiming microphone, speech-model, interruption, or thermal proof from a simulator.

## Proof boundary

| Claim | Minimum evidence |
| --- | --- |
| Microphone permission is configured | Signed target, processed purpose string, physical prompt/state |
| Audio route is active | Physical route, AVAudioSession state, format, and engine input |
| Recording works | Physical device, real input, finalized/reopenable file |
| Speech module works | Named target, locale/module/asset state, live or fixture result |
| Volatile/final policy works | Progressive and final fixture, revision-aware reducer |
| Time-linked transcript works | Source time ranges, player seeking, target device run |
| Sound classification works | File/stream fixture, model revision, confidence policy |
| Interruption recovery works | Physical call/headphone/route-change run |
| Bounded performance works | Physical release run with long audio, memory, latency, thermal |
| AI review works | Availability fixture, typed candidate, stale/apply/discard proof |
| Privacy works | Raw-audio retention/deletion, redacted logs, network policy |
| Accessibility works | VoiceOver, Dynamic Type, reduced effects, keyboard/pointer tasks |
| Release works | Archive/configuration inspection and signed physical smoke |

## Sources

- [Speech](https://developer.apple.com/documentation/speech)
- [SpeechAnalyzer](https://developer.apple.com/documentation/speech/speechanalyzer)
- [SpeechTranscriber](https://developer.apple.com/documentation/speech/speechtranscriber)
- [SpeechTranscriber.Preset](https://developer.apple.com/documentation/speech/speechtranscriber/preset)
- [SpeechTranscriber.Result](https://developer.apple.com/documentation/speech/speechtranscriber/result)
- [SpeechTranscriber.ReportingOption](https://developer.apple.com/documentation/speech/speechtranscriber/reportingoption)
- [AssetInventory](https://developer.apple.com/documentation/speech/assetinventory)
- [AssetInventory.Status](https://developer.apple.com/documentation/speech/assetinventory/status)
- [AssetInputSequenceProvider](https://developer.apple.com/documentation/speech/assetinputsequenceprovider)
- [CaptureInputSequenceProvider](https://developer.apple.com/documentation/speech/captureinputsequenceprovider)
- [AnalyzerInput](https://developer.apple.com/documentation/speech/analyzerinput)
- [AnalyzerInputConverter](https://developer.apple.com/documentation/speech/analyzerinputconverter)
- [Bringing advanced speech-to-text capabilities to your app](https://developer.apple.com/documentation/speech/bringing-advanced-speech-to-text-capabilities-to-your-app)
- [AVAudioApplication](https://developer.apple.com/documentation/avfaudio/avaudioapplication)
- [requestRecordPermission](https://developer.apple.com/documentation/avfaudio/avaudioapplication/requestrecordpermission%28completionhandler%3A%29)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Handling audio interruptions](https://developer.apple.com/documentation/AVFAudio/handling-audio-interruptions)
- [Responding to audio route changes](https://developer.apple.com/documentation/AVFAudio/responding-to-audio-route-changes)
- [AVAudioEngine](https://developer.apple.com/documentation/avfaudio/avaudioengine)
- [AVAudioNode](https://developer.apple.com/documentation/avfaudio/avaudionode)
- [AVAudioInputNode](https://developer.apple.com/documentation/avfaudio/avaudioinputnode)
- [AVAudioPCMBuffer](https://developer.apple.com/documentation/avfaudio/avaudiopcmbuffer)
- [AVAudioFile](https://developer.apple.com/documentation/avfaudio/avaudiofile)
- [AVKit](https://developer.apple.com/documentation/avkit)
- [VideoPlayer](https://developer.apple.com/documentation/avkit/videoplayer)
- [Sound Analysis](https://developer.apple.com/documentation/soundanalysis)
- [SNAudioStreamAnalyzer](https://developer.apple.com/documentation/soundanalysis/snaudiostreamanalyzer)
- [SNAudioFileAnalyzer](https://developer.apple.com/documentation/soundanalysis/snaudiofileanalyzer)
- [SNClassifySoundRequest](https://developer.apple.com/documentation/soundanalysis/snclassifysoundrequest)
- [SNClassificationResult](https://developer.apple.com/documentation/soundanalysis/snclassificationresult)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adding intelligent app features with generative models](https://developer.apple.com/documentation/foundationmodels/adding-intelligent-app-features-with-generative-models)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
