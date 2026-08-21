# SwiftUI audio capture and transcription proof matrix

## Purpose

Use this matrix for any claim involving AVAudioApplication microphone
permission, AVAudioSession routing, AVAudioEngine and input taps, SpeechAnalyzer
or SpeechTranscriber, Speech asset readiness, SoundAnalysis, AVAudioFile,
AVKit playback, waveform review, Foundation Models audio proposals, Liquid
Glass recording controls, or audio save/export.

Record for every run:

- app/build, Xcode, SDK, deployment target, target membership, and platform;
- source kind, source ID, source revision, recording ID, transcript revision,
  model revision, and locale;
- microphone permission, processed usage description, audio-session category/
  mode/options/activation, current input/output route, and hardware format;
- engine/input-node/tap owner, buffer size, time mapping, bounded handoff,
  sequence/provider, analyzer state, observer identity, and teardown;
- SpeechTranscriber preset/options, isAvailable, supported/installed locale,
  AssetInventory state, input start/finish/cancel, and result finalization;
- transcript segment ranges, volatile/final status, alternatives, confidence,
  user edits, and stale-result behavior;
- SoundAnalysis request/model/known labels/window/overlap/confidence/time range;
- file URL ownership, format, duration, byte count, reopen result, metadata,
  retention, deletion, and derived waveform state;
- AVKit player identity/time/interruption/background policy;
- AI input scope, capability state, candidate ID, source/transcript revision,
  validation, review action, and commit result;
- locale, RTL, Dynamic Type, VoiceOver, Voice Control, keyboard, pointer,
  reduced motion, reduced transparency, and contrast settings;
- artifact path, physical device/OS/build, test date, tester, and whether the
  evidence is static, simulated, or live.

A waveform, transcript string, player, or model file does not prove a live
microphone, authorized route, finished file, accurate transcript, physical
sound, on-device processing, accessibility task, or release behavior.

## Evidence levels

| Level | Can support | Cannot support alone |
| --- | --- | --- |
| Official source | API intent and platform contract | This app's runtime behavior |
| Static route review | Ownership, state, privacy, and destination design | Hardware/session/model readiness |
| Named-target compile | API signatures, availability, imports, target membership | Microphone, route, interruption, physical input |
| Unit/fixture test | Revisions, reducers, schemas, metadata, candidate validation | Real audio and system prompts |
| Preview | Semantic visual states and hierarchy | Live waveform, audio route, Speech assets |
| UI test | Labels, focus, ordinary mock review tasks | Hardware microphone, interrupts, real model assets |
| Simulator | Layout, localization, keyboard simulation, state fixtures | Real microphone/route, physical performance, model readiness |
| Signed physical target | Permission, mic route, engine, Speech/SoundAnalysis, accessibility | Every OS/device and distribution |
| System-surface run | Permission/settings, AVKit controls, share/export | Universal correctness or retention policy |
| Performance run | Buffer latency, memory, transcription time, thermal behavior | Correctness of every language/source |
| Archive inspection | Usage descriptions, resources, entitlements, target membership | A completed recording or transcript |
| TestFlight smoke | Signed distributed build on selected targets | Production health and all device routes |

## Fixture contract

Use deterministic text/audio metadata fixtures for most state behavior. Keep
private speech out of shared artifacts.

~~~swift
struct AudioProofFixture: Hashable, Sendable {
    let target: String
    let sourceKind: String
    let sourceID: String
    let sourceRevision: Int
    let transcriptRevision: Int
    let localeIdentifier: String
    let audioFormat: String
    let sampleRate: Double?
    let channelCount: Int?
    let durationSeconds: Double?
    let permissionState: String
    let routeState: String
    let engineState: String
    let assetState: String
    let analyzerState: String
    let transcriptState: String
    let observationState: String
    let playerState: String
    let candidateState: String
    let destinationState: String
    let accessibilityModes: [String]
}
~~~

Minimum fixture families:

- permission undetermined/granted/denied and Settings-changed;
- input route available/unavailable, built-in/Bluetooth/wired, format changed;
- session inactive/configuring/active/interrupted/routeChanged/failed;
- engine idle/prepared/running/tapInstalled/stopping/stopped/failed;
- empty, silence, short speech, long speech, accents, names, numbers,
  punctuation, code-switching, overlapping speakers, noise, and music;
- SpeechTranscriber unsupported locale, supported/download, downloading,
  installed, unavailable, volatile, final, alternative, cancelled, failed;
- SoundAnalysis unknown, low confidence, competing labels, stable label,
  time-ranged result, format-change, model-missing, and cancelled;
- file missing, unsupported, malformed, partial, finalized, reopened, large,
  deleted, and export-cancelled;
- player loading/playing/paused/interrupted/ended/failed;
- AI unavailable, generating, partial, malformed, stale, accepted, edited,
  rejected, committed, and save-failed;
- iPhone/iPad narrow and wide, Catalyst, RTL, largest Dynamic Type,
  VoiceOver, keyboard, pointer, reduced motion/transparency, and contrast.

## Microphone permission and privacy matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Usage description is present | Archive/processed plist inspection | Wrong target/configuration/localization | Built target contains truthful copy |
| Permission state is represented | Physical/system run | Undetermined, granted, denied, Settings change | UI state and next action match runtime |
| Permission request is timely | Physical task run | Launch without recording, request on intent | No surprise prompt at launch |
| Denied input is safe | Physical/system run | Denial, restriction-like conditions, no route | No false listening/waveform state |
| Imported file fallback works | UI/physical run | No mic, denied permission | Person can complete a useful alternate route |
| Raw audio retention is explicit | Static/privacy/integration review | Crash, cancellation, delete | File and temporary buffers follow policy |
| Logs are redacted | Instrumented release run | Transcript, paths, route/device names | No sensitive content in logs/analytics |
| External processing is honest | Static/network review | Offline/local mode, fallback | UI matches actual data path |
| AI input is scoped | Request fixture/security review | Prompt injection, long transcript | Only approved content reaches adapter |

## AVAudioSession and route matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Category/mode/options match feature | Named-target compile plus physical run | Record, playback, play-and-record | Recorded configuration matches product |
| Session activates | Physical run | Permission denied, route unavailable | Activation success is state, not assumption |
| Current route is visible when needed | Physical run | Built-in, wired, Bluetooth, disconnect | User sees usable route/fallback |
| Interruption is handled | Physical run | Phone call, Siri, alarm, system alert | Pause/finish/resume policy is visible |
| Route change is handled | Physical run | Headset connect/disconnect, format change | Engine/analyzer are reconciled |
| Background policy is safe | Physical lifecycle run | Home, lock, scene inactive | Audio continues/stops according to supported policy |
| Deactivation is clean | Instrumented physical run | Stop, navigation, termination | Session releases and no stale state remains |
| Notifications reach owner safely | Concurrency/instrumented run | Secondary-thread notification | Main-actor UI state is race-free |

## AVAudioEngine/input tap matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Engine graph is owned once | Static/instrumented run | View redraw, re-entry, retake | One engine/tap owner exists |
| Input format is usable | Physical run | Zero rate/channels, route change | Sample rate/channels are recorded |
| Tap installs once | Integration/run | Repeated start, stop/start | No duplicate tap or install error |
| Tap callback is bounded | Performance/instrumented run | Long session, slow consumer | No blocking I/O/network/UI mutation |
| Buffers map to time | Fixture/physical run | Route change, drift, file handoff | Time ranges match source |
| Handoff is cancellable | Async/lifecycle test | Stop, scene close, new source | Producer/consumer finish cleanly |
| Backpressure is intentional | Performance/fixture run | Slow Speech/SoundAnalysis | Drop/coalesce policy is measured |
| Tap removal is guaranteed | Teardown/instrumented run | Error, cancellation, deinit | No callback reaches stale owner |
| Engine restart is safe | Physical run | Interruption, route change | Restart uses current format/route |

## SpeechAnalyzer readiness matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Speech module is selected intentionally | Static route review | Transcriber versus legacy recognizer | Feature records module and rationale |
| Device availability is checked | Target/device fixture | Unsupported hardware/settings | UI offers fallback |
| Locale is supported | Target/device run | Unsupported, equivalent locale | Locale state is visible |
| Assets are installed | Physical/device run | Supported, downloading, installed, unsupported | Start action follows AssetInventory |
| Download is user-aware | UI/system run | Offline, cancel, retry | Copy identifies model asset work |
| Input provider is valid | Named-target compile/fixture | Capture/file/custom sequence | Provider and format are recorded |
| Analyzer starts once | Integration/lifecycle test | New source, repeated start | One input owner is active |
| Input ends intentionally | Async/integration test | Stop, EOF, cancel, error | Sequence finish precedes analyzer finalization |
| Analyzer cancellation works | Physical/async run | Scene close, retake, failure | No late result reaches new source |
| Assets/resources are bounded | Performance/device run | Multiple locales, storage pressure | Reservation/download policy is recorded |

## Transcript result and editing matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Progressive results are drafts | Target fixture/UI run | Volatile/final sequence | UI and persistence mark draft correctly |
| Final result is source-linked | Fixture/integration test | Repeated range revisions | Segment/range/revision are retained |
| Alternatives are handled | Target run where supported | Multiple interpretations | Person can review or product hides honestly |
| Confidence is surfaced appropriately | Fixture/UI/accessibility run | Low confidence, no confidence | Copy does not claim certainty |
| Results do not duplicate | Reducer/unit test | Same range repeated, out of order | Final text contains one intended segment |
| User edits survive | Integration/UI run | New volatile/final result after edit | Framework update does not overwrite edits |
| Search is time-linked | UI/physical run | Many/no matches, seek | Match selects transcript and source time |
| Transcript revision is explicit | Unit/integration test | Edit, reprocess, locale change | AI/candidate requests become stale correctly |
| Cancel is safe | Async/UI run | Stop during result delivery | No late mutation |
| VoiceOver reads certainty | Accessibility task | Draft/final/stale/candidate | State and actions are meaningful |

## SoundAnalysis matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| File analyzer receives supported file | Fixture/run | Compressed/uncompressed, corrupt | Analyzer creates or fails clearly |
| Stream analyzer receives PCM | Physical/instrumented run | Format mismatch, route change | Input format matches analyzer |
| Request uses intended model | Target/archive inspection | Built-in/custom, model missing | Model ID/revision and labels recorded |
| Observer remains alive | Integration/instrumented run | Analyzer lifecycle | Results and completion arrive |
| Result has time range | Fixture/physical run | Empty/short audio | Labels map to source |
| Confidence policy works | Calibrated fixtures | Low, competing, stable, unknown | No unsafe one-callback side effect |
| Cancellation works | Physical/async run | File cancel, stream stop | Analyzer/request/observer release |
| Raw audio policy is separate | Static/integration review | Derived label retention | Audio and label lifecycle differ |
| AI receives bounded results | Adapter fixture | Prompt injection, stale source | No raw/unapproved audio scope |

## File, waveform, and AVKit matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Recording finalizes | Physical/integration run | Stop, disk full, interruption | File closes and has valid duration |
| File reopens | Reopen fixture/run | Missing/corrupt/unsupported | App reports finalization truth |
| File identity is stable | Static/integration test | Rename, copy, relaunch | Source ID is not filename-only |
| Waveform is derived | Static/fixture test | Raw audio deleted, source changes | Waveform invalidates/rebuilds correctly |
| Waveform is bounded | Physical performance run | Long file/live session | Sample count/memory are bounded |
| VideoPlayer route works | Named-target compile/UI run | Player failure, missing URL | Playback and failure states are clear |
| Player lifetime is stable | UI/lifecycle run | Row/sheet recreation | Current time/player is not reset unexpectedly |
| Time-linked seek works | Physical/UI run | Transcript/observation range | Seek reaches intended time |
| Playback interruption works | Physical run | Call, route change, background | State and resume policy are honest |
| Export is explicit | System run | Cancel, unsupported type | Destination/type/success are clear |

## Foundation Models candidate matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Capability is optional | Device/availability fixture | Unsupported model/device | Playback/transcript/manual route remains useful |
| Input is bounded | Static adapter review | Long transcript, private content | Only approved final source is passed |
| Candidate is typed | Schema/fixture tests | Empty, huge, malformed, prohibited claim | Invalid output cannot reach Apply |
| Source revision is captured | Unit/request test | Audio edit, transcript edit, reprocess | Candidate becomes stale |
| Candidate is reviewable | Physical/accessibility run | Partial, refusal, no-op, stale | Source/proposal/actions differ |
| Cancellation is safe | Async/lifecycle run | Navigate, retake, background | No late mutation |
| Commit uses normal path | Integration/save test | Conflict, serialization, destination failure | AI cannot bypass save/export policy |
| Privacy copy is accurate | Static/UI/network review | Local availability, external fallback | User-facing data path is correct |

## Liquid Glass and accessibility matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| Glass controls have task meaning | Design review/preview | Decorative full-screen material | Each group maps to an action/state |
| Recording is semantic | UI/accessibility run | Listening, paused, denied, interrupted | State/value/action are discoverable |
| Transcript remains primary | Light/dark physical visual run | Long text, Dynamic Type | Glass does not obscure or steal focus |
| Reduced transparency works | Physical settings run | Opaque fallback, contrast | State remains legible |
| Reduced motion works | Physical settings run | Start/stop, transcript updates | No required animation conveys state |
| VoiceOver works | Physical accessibility task | Draft/final/AI/stale | User can complete route |
| Keyboard works | iPad/Catalyst physical run | Start/stop, play, seek, edit, accept | Core task completes without touch |
| Pointer works | iPad/Catalyst physical run | Hover, focus, context menu | Controls remain discoverable |
| RTL/localization works | Physical/UI run | Long labels, time strings | No clipped or reversed meaning |

## Target, performance, archive, and release matrix

| Claim | Minimum proof | Required edge cases | Acceptance evidence |
| --- | --- | --- | --- |
| iPhone live capture works | Signed physical iPhone run | Mic, route, call, lock, thermal | Device/OS/build/artifact recorded |
| iPadOS review works | Signed physical iPad run | Split view, keyboard, pointer | Layout/input evidence recorded |
| Catalyst file route works | Named-target compile and Mac run | Import, playback, menus | Unsupported live route is honest |
| Speech assets behave in release | Release physical run | Download/install/storage | Debug-only readiness is not claimed |
| Long audio is bounded | Release physical performance run | Long file/live session | Time/memory/thermal evidence |
| Repeated sessions recover | Physical lifecycle run | Start/stop/retake/interruption | No leaked tap/task/player |
| Processed privacy config is correct | Archive inspection | Wrong configuration/target | Built artifact contains intended reason |
| TestFlight route works | Distributed physical smoke | Install/update/restore | Selected path succeeds after signing |

## Required artifact set

For a serious audio feature keep:

1. named-target compile output for AVFAudio, Speech, SoundAnalysis, AVKit, and
   optional Foundation Models code;
2. deterministic transcript, sound, file, revision, candidate, and destination
   fixtures;
3. simulator/preview visual and accessibility state captures;
4. physical iPhone/iPad evidence for microphone, route, interruption, Speech
   assets, SoundAnalysis, playback, alternate input, and AI availability;
5. performance evidence for representative duration, locale, and route;
6. archive/release inspection for usage descriptions, resources, target
   membership, privacy, and signing;
7. an explicit list of unsupported targets, locales, and unverified claims.

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
