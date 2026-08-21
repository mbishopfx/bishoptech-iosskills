# SwiftUI audio capture and transcription capability route

## Use this route when

Choose this route when a SwiftUI feature needs to record, transcribe, classify,
review, or organize audio:

- live dictation or conversation;
- a saved recording that receives a time-linked transcript;
- sound labels from a microphone stream or audio file;
- an editable transcript with playback and seek;
- a bounded waveform/level surface;
- a local title, summary, tag, or accessibility proposal;
- explicit save, export, share, or discard behavior.

Use the existing [Speech, Translation, and Language](../30-on-device-ai/05-speech-translation-and-language.md)
page for framework selection and legacy boundaries. Use the [SoundAnalysis
route](../42-framework-deep-dives/30-soundanalysis-on-device-audio-classification.md)
for classifier details. Use this route when the central problem is coordinating
SwiftUI state, audio session ownership, transcript revisions, review, and
destinations.

## Route contract

Complete these decisions before building the screen.

| Field | Required decision |
| --- | --- |
| Outcome | Record, dictate, transcribe, classify, search, summarize, export, or organize |
| Source | Live microphone, imported file, existing app record, or playback-only |
| Identity | Recording/file/document ID and source revision |
| Permission | AVAudioApplication recording state and Speech module/asset state |
| Audio session | Category, mode, options, activation, route, interruption, and background policy |
| Engine | AVAudioEngine/input node/tap owner, queue, teardown, and format |
| Input provider | CaptureInputSequenceProvider, AssetInputSequenceProvider, converter, or custom sequence |
| Buffer policy | Time mapping, bounded handoff, cancellation, backpressure, and drop behavior |
| Speech | SpeechTranscriber module, locale, preset, volatile/final/options |
| Sound | SNAudioStreamAnalyzer/FileAnalyzer, request, model, windows, confidence policy |
| File | Format, app-owned copy, duration, metadata, retention, deletion, reopen proof |
| Transcript | Segment IDs, audio ranges, revision, user edits, alternatives, search |
| Review | Source, observation, draft, candidate, accepted, committed |
| AI | Typed context, availability, scope, schema, stale guard, fallback |
| Destination | App save, export/share, Photos/system route, or discard |
| UI | Recording/paused/processing/review/error states and Liquid Glass groups |
| Targets | iPhone/iPad/Catalyst/watchOS/CarPlay/extension boundaries |
| Proof | Compile, fixture, preview, UI, physical, performance, archive, release |

## Route selection table

| Scenario | Route | Key boundary |
| --- | --- | --- |
| Live speech | AVAudioSession + SpeechAnalyzer/SpeechTranscriber | Live input sequence and result lifecycle |
| Saved-file transcript | AssetInputSequenceProvider or file adapter | App-owned URL, finish, cancellation |
| Live sound categories | AVAudioEngine + SNAudioStreamAnalyzer | Matching PCM format and bounded observer |
| File sound review | SNAudioFileAnalyzer | Strong observer, analyzer completion, timeline |
| Record for later | AVAudioEngine/AVAudioFile | Finalize/reopen before analysis |
| Playback review | AVKit VideoPlayer/AVPlayerViewController | Player lifetime and time-linked content |
| Editable transcript | SwiftUI text editor route | User edits versus framework revisions |
| AI organization | Foundation Models adapter | Typed candidate and explicit commit |

## 1. Create the feature state machine

Use typed states rather than independent flags that can contradict each other.

~~~swift
enum AudioFeaturePhase: Equatable, Sendable {
    case idle
    case needsMicrophonePermission
    case checkingSpeechAssets
    case ready
    case configuring
    case listening
    case paused(reason: String)
    case stopping
    case finalizingFile
    case transcribing
    case reviewing
    case failed(String)
}

struct AudioFeatureState: Sendable, Equatable {
    let sourceID: UUID
    var sourceRevision: Int
    var phase: AudioFeaturePhase
    var fileURL: URL?
    var transcriptRevision: Int
    var volatileText: String
    var finalizedText: String
    var candidate: AudioCandidateState
}
~~~

An imported file can be ready for playback but unavailable to Speech. A
recording can be finalized while its transcript is still volatile. A candidate
can be stale while the source remains playable. State should preserve those
distinctions.

## 2. Gate microphone and Speech readiness

Check the two capability families independently:

1. AVAudioApplication recording permission and an actual input route;
2. SpeechTranscriber availability, locale support, and AssetInventory status.

The route should expose:

- not determined and a nearby request action;
- denied and a Settings/import fallback;
- supported but downloading with progress/cancel policy;
- installed and ready;
- unsupported locale/device with manual/file fallback.

Do not present a Start button that silently starts a remote service when the
local Speech module is unavailable. If an external fallback is a product
decision, disclose it as a separate route.

## 3. Configure audio once

Create one session/engine owner for the feature. Keep it alive across SwiftUI
body updates and destroy it when the route closes.

~~~swift
final class AudioCaptureService {
    let session = AVAudioSession.sharedInstance()
    let engine = AVAudioEngine()

    private var tapInstalled = false

    func prepare() throws {
        try session.setCategory(
            .record,
            mode: .measurement,
            options: []
        )
        try session.setActive(true)

        let input = engine.inputNode
        let format = input.outputFormat(forBus: 0)
        guard format.sampleRate > 0, format.channelCount > 0 else {
            throw AudioCaptureError.inputUnavailable
        }
    }

    func installTap(
        handler: @escaping @Sendable (
            AVAudioPCMBuffer,
            AVAudioTime
        ) -> Void
    ) throws {
        guard !tapInstalled else { return }
        let input = engine.inputNode
        let format = input.outputFormat(forBus: 0)

        input.installTap(
            onBus: 0,
            bufferSize: 2048,
            format: format
        ) { buffer, time in
            handler(buffer, time)
        }
        tapInstalled = true
    }

    func start() throws {
        try engine.start()
    }

    func stop() {
        if tapInstalled {
            engine.inputNode.removeTap(onBus: 0)
            tapInstalled = false
        }
        engine.stop()
        engine.reset()
        try? session.setActive(
            false,
            options: [.notifyOthersOnDeactivation]
        )
    }
}
~~~

The service needs a concurrency strategy and notification observers in the
real target. Keep input callbacks lightweight, and move buffers into a
bounded analyzer/file handoff. Do not call start or installTap on each view
appearance without idempotence.

## 4. Select Speech input ownership

Use the system Speech input provider when its target availability matches the
feature. Use an app-owned AVAudioEngine adapter when the app also needs file
writing, SoundAnalysis, level data, or custom timing.

| Ownership | Advantages | Added proof |
| --- | --- | --- |
| Speech CaptureInputSequenceProvider | Less custom buffer conversion | Provider availability, permission, route, lifetime |
| Speech AssetInputSequenceProvider | Clear file-to-analyzer path | URL scope, supported format, EOF, cancellation |
| App engine + AnalyzerInputConverter | Shared audio for transcript, file, waveform, SoundAnalysis | Format/time mapping, bounded handoff, teardown |
| Separate capture and file reader | Good for post-recording analysis | Finalized file and analysis revision |

Do not feed the same live sequence to two consumers unless the ownership and
backpressure policy are explicit. If the transcript and SoundAnalysis need the
same audio, decide whether the engine tap fans out to bounded consumers or
whether a finalized app-owned file is analyzed afterward.

## 5. Run SpeechAnalyzer with explicit finish

The exact input-sequence and converter signatures are SDK-sensitive. The
lifecycle is stable:

~~~swift
struct TranscriptionRequest: Sendable, Equatable {
    let sourceID: UUID
    let sourceRevision: Int
    let localeIdentifier: String
    let presetDescription: String
}

struct TranscriptSegment: Sendable, Equatable {
    let segmentID: UUID
    let sourceRevision: Int
    let text: String
    let rangeDescription: String
    let isFinal: Bool
}
~~~

Implementation steps:

1. Resolve a supported locale.
2. Create SpeechTranscriber with an intentional preset/options.
3. Check isAvailable and installed/supported locales.
4. Inspect AssetInventory and download/install only with a clear product flow.
5. Build one input sequence/provider.
6. Create SpeechAnalyzer with the module.
7. Start a result-consumer task for SpeechTranscriber.results.
8. Start the analyzer.
9. Feed live buffers or asset input.
10. Finish the input sequence after Stop or end-of-file.
11. Call the analyzer's finalization method.
12. Wait for result consumption, then publish finalized state.
13. Cancel all tasks and finish input on every error/cancel path.

Do not call finish immediately after start for a live recording. Do not call
finalize while the producer can still yield buffers. A new recording must
cancel/finish the old sequence before replacing it.

## 6. Reduce transcript results by source range

Progressive results may revise the same audio range. Keep a map keyed by
source range/segment identity and replace volatile content instead of
appending duplicates.

~~~swift
actor TranscriptReducer {
    private var segments: [UUID: TranscriptSegment] = [:]
    private(set) var revision = 0

    func ingest(_ segment: TranscriptSegment) {
        segments[segment.segmentID] = segment
        revision += 1
    }

    func finalizedText() -> String {
        segments.values
            .filter(\.isFinal)
            .sorted { $0.rangeDescription < $1.rangeDescription }
            .map(\.text)
            .joined(separator: " ")
    }
}
~~~

The range comparison above is a placeholder for a typed time/range ordering
in the target. Preserve AttributedString/time attributes when the feature
needs highlighting, confidence, alternatives, or seek-to-text. If the person
edits the transcript, store the edit as app-owned content with its own
revision; do not overwrite it with a later framework result.

## 7. Add SoundAnalysis observations

For a live stream:

1. inspect current input format;
2. create SNAudioStreamAnalyzer with that format;
3. create SNClassifySoundRequest with built-in or custom model;
4. retain a results observer;
5. add request;
6. submit PCM buffers with frame positions;
7. reduce time-ranged classifications;
8. remove request and stop the engine.

For a file:

1. create SNAudioFileAnalyzer with the app-owned URL;
2. retain the observer;
3. add the sound request;
4. analyze synchronously/asynchronously;
5. support cancellation;
6. map completion and result ranges to the source revision.

Keep classification labels, confidence, time range, and model revision in the
observation. Use an unknown/ambiguous state and do not execute side effects
from one callback.

## 8. Persist and reopen the recording

If the user expects a durable recording:

- write to an app-owned URL;
- record a source ID and file format;
- close/finalize the writer;
- reopen with AVAudioFile or an appropriate asset reader;
- calculate duration and size;
- apply retention and deletion policy;
- then begin expensive transcription or classification.

If finalization fails, keep the original capture state recoverable and remove
or mark a partial file. Do not show “Saved” merely because the recording button
stopped.

## 9. Review with AVKit

Keep the player as one review dependency:

~~~swift
struct AudioReviewState: Sendable, Equatable {
    let sourceID: UUID
    let sourceRevision: Int
    var durationSeconds: Double
    var selectedTime: Double
    var transcriptRevision: Int
    var observationCount: Int
}
~~~

Use VideoPlayer for the SwiftUI playback route or AVPlayerViewController for
the system controller route. A transcript segment can seek to its source time.
A sound observation can seek to its range. The player does not own transcript
editing or AI commit.

Pause/stop according to lifecycle policy when the review disappears. Handle
audio interruptions and route changes. Do not recreate a player on every row
render or treat successful playback as proof that transcription succeeded.

## 10. Make a bounded waveform

Use a display-width-sized series of normalized levels. Keep it derived from a
source revision and discard it when the source changes. The capture callback
should send coarse level data through a bounded handoff rather than update
SwiftUI for every frame.

Waveform route:

~~~text
input buffer -> RMS/peak calculation -> bounded level reducer
    -> display samples -> SwiftUI waveform
~~~

Keep the recording control separate from the waveform. Add a static fallback
for Reduce Motion, large text, VoiceOver, and input-denied states.

## 11. Add a local AI proposal

Use final, user-approved transcript text and selected sound observations. Do
not send raw audio or unreviewed volatile text to a proposal by default.

~~~swift
struct AudioProposalInput: Codable, Sendable {
    let sourceID: UUID
    let sourceRevision: Int
    let transcriptRevision: Int
    let selectedText: String
    let observations: [String]
}

struct AudioProposal: Codable, Sendable, Equatable {
    let proposalID: UUID
    let sourceID: UUID
    let sourceRevision: Int
    let transcriptRevision: Int
    let title: String
    let summary: String
    let tags: [String]
}
~~~

The Foundation Models adapter should be optional and typed. Validate output
length, tags, prohibited claims, actions, and source revisions. Present
Review, Edit, Accept, and Discard. An accepted proposal enters the normal app
save/export path; it does not bypass user approval.

## 12. Compose the Liquid Glass surface

Functional groups:

- top: route/permission/recording status;
- center: waveform or transcript;
- bottom: Stop/Pause/Play/Review/Save;
- secondary: model/observation filter and destination;
- review card: source-linked AI candidate.

Use stable IDs for morphing groups and avoid glass over the whole transcript.
If Reduce Transparency is enabled, use an opaque panel with the same semantic
hierarchy. Keep system-owned playback controls recognizable.

## 13. Lifecycle route

| Event | Required action |
| --- | --- |
| Start | Check permission, route, Speech assets, configure session/engine |
| New source | Increment source revision, cancel old tasks, dispose old analyzer |
| Stop | Stop input, finish sequence, finalize analyzer, finalize file |
| Cancel | Cancel producer/consumer, remove tap/request, keep or delete draft by policy |
| Interruption | Pause/finish and show state; do not resume blindly |
| Route change | Re-read route/format; recreate analyzer if format changed |
| Background | Apply documented audio/background policy; preserve app-owned file |
| Scene close | Stop/dispose observers, taps, tasks, player, and temporary buffers |
| AI completion | Compare source/transcript revisions before showing Apply |
| Save failure | Keep source and candidate recoverable; report destination failure |

## 14. Target and proof matrix

| Target/claim | Required proof |
| --- | --- |
| iPhone live microphone | Physical permission, route, engine, Speech result, interruption |
| iPadOS audio review | Physical split view, keyboard/pointer, transcript/player |
| Catalyst file route | Named target compile and Mac file/playback task |
| Speech locale/assets | Target device, locale status, AssetInventory state, download/fallback |
| Sound classifier | File/stream fixture, model revision, confidence/unknown policy |
| AI proposal | Availability fixture, typed input/output, stale/apply/discard |
| Privacy | Processed Info.plist, retention/deletion, logs/network policy |
| Accessibility | VoiceOver, Dynamic Type, reduced effects, keyboard/pointer |
| Performance | Release physical run with long audio, memory, latency, thermal |
| Distribution | Archive, target resources, entitlement/privacy inspection, TestFlight smoke |

## Stop conditions

Stop and resolve the seam when:

- permission, input route, and engine state are collapsed into one flag;
- a live stream or file is fed to Speech without a clear input owner;
- the analyzer sequence is never finished or is finished before live capture ends;
- volatile transcript text is saved or used for an action;
- user edits are overwritten by later transcription results;
- SoundAnalysis labels are treated as facts or safety proof;
- raw audio is sent to AI without explicit scope and privacy policy;
- a waveform is the only recording control or state indicator;
- a late AI result can mutate a new recording;
- “Save” hides whether the action is app save, export, or external system mutation;
- simulator evidence is presented as microphone, route, interruption, model, or thermal proof.

## Sources

- [Speech](https://developer.apple.com/documentation/speech)
- [SpeechAnalyzer](https://developer.apple.com/documentation/speech/speechanalyzer)
- [SpeechTranscriber](https://developer.apple.com/documentation/speech/speechtranscriber)
- [SpeechTranscriber.Preset](https://developer.apple.com/documentation/speech/speechtranscriber/preset)
- [SpeechTranscriber.Result](https://developer.apple.com/documentation/speech/speechtranscriber/result)
- [AssetInventory](https://developer.apple.com/documentation/speech/assetinventory)
- [AssetInventory.Status](https://developer.apple.com/documentation/speech/assetinventory/status)
- [AssetInputSequenceProvider](https://developer.apple.com/documentation/speech/assetinputsequenceprovider)
- [CaptureInputSequenceProvider](https://developer.apple.com/documentation/speech/captureinputsequenceprovider)
- [AnalyzerInput](https://developer.apple.com/documentation/speech/analyzerinput)
- [AnalyzerInputConverter](https://developer.apple.com/documentation/speech/analyzerinputconverter)
- [Bringing advanced speech-to-text capabilities to your app](https://developer.apple.com/documentation/speech/bringing-advanced-speech-to-text-capabilities-to-your-app)
- [AVAudioApplication](https://developer.apple.com/documentation/avfaudio/avaudioapplication)
- [Request record permission](https://developer.apple.com/documentation/avfaudio/avaudioapplication/requestrecordpermission%28completionhandler%3A%29)
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
