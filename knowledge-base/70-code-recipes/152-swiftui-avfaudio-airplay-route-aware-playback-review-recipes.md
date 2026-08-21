# SwiftUI AVFAudio, AirPlay, and route-aware playback review recipes

These are compile-oriented route sketches for a named iPhone or iPad target. They are not compiled in this documentation workspace and do not prove microphone permission, audio format, route selection, AirPlay receiver behavior, multiroute stability, spatial perception, Now Playing presentation, CarPlay/Watch control, Speech assets, model availability, accessibility, privacy, or release readiness.

Read the [audio-session review](../42-framework-deep-dives/109-swiftui-avfaudio-airplay-route-aware-playback-review.md), [design guide](../21-design-deep-dives/137-swiftui-avfaudio-airplay-route-aware-playback-review-design.md), [route](../50-capability-recipes/140-swiftui-avfaudio-airplay-route-aware-playback-review-route.md), and [proof matrix](../60-verification/134-swiftui-avfaudio-airplay-route-aware-playback-review-proof-matrix.md) first. Confirm the current SDK signature, target availability, privacy resources, background mode, session ownership, and physical-device behavior before copying any sketch.

Tilde fences keep the examples copyable in this Markdown page.

## Recipe 1: define layered audio state

Do not model an audio feature with one Boolean.

~~~swift
import AVFAudio
import Foundation

struct AudioRouteSnapshot: Sendable, Equatable {
    struct Port: Sendable, Equatable {
        let type: String
        let name: String
        let uid: String
    }

    let inputs: [Port]
    let outputs: [Port]
    let observedAt: Date
    let reason: String?
}

enum AudioFeatureState: Sendable, Equatable {
    case unavailable(String)
    case idle
    case configuring
    case active(route: AudioRouteSnapshot)
    case playing(itemID: String, position: Double, revision: Int64)
    case recording(recordingID: UUID, duration: Double, revision: Int64)
    case interrupted
    case routeChanging
    case processing(sourceRevision: Int64)
    case failed(String)
}
~~~

Keep permission, session, player, route, interruption, source, transcript, and domain state separate. A route snapshot is never a playback receipt.

## Recipe 2: record the session contract

Store the intended policy for review and testing.

~~~swift
import AVFAudio

struct AudioSessionContract: Sendable, Equatable {
    let category: AVAudioSession.Category
    let mode: AVAudioSession.Mode
    let options: AVAudioSession.CategoryOptions
    let routeSharingPolicy: AVAudioSession.RouteSharingPolicy
    let needsInput: Bool
    let needsOutput: Bool
    let longForm: Bool
}

let playbackContract = AudioSessionContract(
    category: .playback,
    mode: .default,
    options: [],
    routeSharingPolicy: .longFormAudio,
    needsInput: false,
    needsOutput: true,
    longForm: true
)
~~~

Use longFormAudio only when the content really is intended for extended listening. Verify the selected policy and SDK availability on the target platform.

## Recipe 3: configure and activate at user intent

Configure the session before activation, but defer activation until the feature is ready.

~~~swift
import AVFAudio

final class AudioSessionCoordinator {
    private let session = AVAudioSession.sharedInstance()

    func configure(_ contract: AudioSessionContract) throws {
        try session.setCategory(
            contract.category,
            mode: contract.mode,
            policy: contract.routeSharingPolicy,
            options: contract.options
        )
    }

    func activate() throws {
        try session.setActive(true)
    }

    func deactivate() {
        try? session.setActive(
            false,
            options: [.notifyOthersOnDeactivation]
        )
    }

    func currentRoute() -> AVAudioSessionRouteDescription {
        session.currentRoute
    }
}
~~~

Do not activate at app launch merely because a player screen exists. Activation can affect other apps’ audio.

## Recipe 4: describe the current route

Convert the system route into a small Sendable snapshot.

~~~swift
import AVFAudio
import Foundation

func makeRouteSnapshot(
    from route: AVAudioSessionRouteDescription,
    reason: String? = nil,
    now: Date = .now
) -> AudioRouteSnapshot {
    func port(_ value: AVAudioSessionPortDescription) -> AudioRouteSnapshot.Port {
        AudioRouteSnapshot.Port(
            type: value.portType.rawValue,
            name: value.portName,
            uid: value.uid
        )
    }

    return AudioRouteSnapshot(
        inputs: route.inputs.map(port),
        outputs: route.outputs.map(port),
        observedAt: now,
        reason: reason
    )
}
~~~

The port name and UID identify the reported route. They do not prove a receiver is audible or that the stream has finished moving.

## Recipe 5: observe route changes on an audio service

Apple documents that route-change notifications can arrive on a secondary thread. Hop to the state owner before touching UI.

~~~swift
import AVFAudio
import Foundation

enum AudioSystemEvent: Sendable {
    case routeChanged(reason: String, snapshot: AudioRouteSnapshot)
    case interruptionBegan
    case interruptionEnded(shouldResume: Bool)
    case mediaServicesReset
    case mediaServicesLost
}

final class AudioNotificationBridge {
    private var tokens: [NSObjectProtocol] = []
    private let center = NotificationCenter.default

    func start(
        emit: @escaping @Sendable (AudioSystemEvent) -> Void
    ) {
        let session = AVAudioSession.sharedInstance()

        tokens.append(
            center.addObserver(
                forName: AVAudioSession.routeChangeNotification,
                object: session,
                queue: nil
            ) { notification in
                let reason = notification.userInfo?[
                    AVAudioSessionRouteChangeReasonKey
                ] as? UInt
                let label = reason.map(String.init) ?? "unknown"
                let snapshot = makeRouteSnapshot(
                    from: session.currentRoute,
                    reason: label
                )
                emit(.routeChanged(reason: label, snapshot: snapshot))
            }
        )

        tokens.append(
            center.addObserver(
                forName: AVAudioSession.interruptionNotification,
                object: session,
                queue: nil
            ) { notification in
                let value = notification.userInfo?[
                    AVAudioSessionInterruptionTypeKey
                ] as? UInt
                if value == AVAudioSession.InterruptionType.began.rawValue {
                    emit(.interruptionBegan)
                } else {
                    let shouldResume = false
                    emit(.interruptionEnded(shouldResume: shouldResume))
                }
            }
        )

        tokens.append(
            center.addObserver(
                forName: AVAudioSession.mediaServicesWereResetNotification,
                object: session,
                queue: nil
            ) { _ in
                emit(.mediaServicesReset)
            }
        )

        tokens.append(
            center.addObserver(
                forName: AVAudioSession.mediaServicesWereLostNotification,
                object: session,
                queue: nil
            ) { _ in
                emit(.mediaServicesLost)
            }
        )
    }

    func stop() {
        for token in tokens {
            center.removeObserver(token)
        }
        tokens.removeAll()
    }
}
~~~

The interruption example deliberately returns a conservative value. A real implementation must inspect the current SDK’s interruption options and the user’s prior playback intent before resuming.

## Recipe 6: create a SwiftUI route-picker bridge

Use the system route picker rather than a manually maintained receiver list.

~~~swift
import AVKit
import SwiftUI

struct OutputRoutePicker: UIViewRepresentable {
    var activeTintColor: UIColor = .systemBlue
    var prefersVideoDevices: Bool = false

    func makeUIView(context: Context) -> AVRoutePickerView {
        let view = AVRoutePickerView()
        view.activeTintColor = activeTintColor
        view.prioritizesVideoDevices = prefersVideoDevices
        view.isRoutePickerButtonBordered = false
        view.accessibilityLabel = "Choose output device"
        return view
    }

    func updateUIView(_ view: AVRoutePickerView, context: Context) {
        view.activeTintColor = activeTintColor
        view.prioritizesVideoDevices = prefersVideoDevices
    }
}
~~~

The picker’s presentation is system evidence that the user can choose a route. Observe currentRoute and player state separately.

## Recipe 7: publish route state in SwiftUI

Keep route labels concise and honest.

~~~swift
import SwiftUI

struct RouteStatusView: View {
    let snapshot: AudioRouteSnapshot?
    let switching: Bool
    let unavailableReason: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Label {
                Text(title)
            } icon: {
                Image(systemName: "speaker.wave.2")
            }

            if let detail {
                Text(detail)
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }

            OutputRoutePicker()
                .frame(width: 44, height: 44)
        }
        .accessibilityElement(children: .combine)
    }

    private var title: String {
        if switching { return "Changing output" }
        if unavailableReason != nil { return "Output unavailable" }
        if let output = snapshot?.outputs.first { return output.name }
        return "This device"
    }

    private var detail: String? {
        if let unavailableReason { return unavailableReason }
        if switching { return "Waiting for the audio route to update" }
        return "Choose where audio plays"
    }
}
~~~

Do not show a receiver as active solely because the user tapped the picker. Update the label from a fresh route/player snapshot.

## Recipe 8: own an app player

Use one owner for playback, queue, and state projection.

~~~swift
import AVFoundation
import Foundation

@MainActor
final class PlaybackCoordinator: NSObject {
    private let player = AVPlayer()
    private let session = AVAudioSession.sharedInstance()

    private(set) var itemID: String?
    private(set) var revision: Int64 = 0
    private(set) var userStartedPlayback = false

    func prepare(itemID: String, url: URL) {
        self.itemID = itemID
        revision += 1
        player.replaceCurrentItem(with: AVPlayerItem(url: url))
    }

    func play() throws {
        try session.setActive(true)
        player.play()
        userStartedPlayback = true
    }

    func pause() {
        player.pause()
    }

    func stop() {
        player.pause()
        player.replaceCurrentItem(with: nil)
        itemID = nil
        revision += 1
        userStartedPlayback = false
    }

    func currentTime() -> Double {
        player.currentTime().seconds
    }
}
~~~

A player’s time-control state and current item should be observed in the actual implementation. Returning from play does not prove that decoding or audible output began.

## Recipe 9: handle interruptions conservatively

Keep prior user intent and system options distinct.

~~~swift
@MainActor
final class InterruptionPolicy {
    private(set) var wasPlayingBeforeInterruption = false
    private(set) var interrupted = false

    func began(isPlaying: Bool) {
        wasPlayingBeforeInterruption = isPlaying
        interrupted = true
    }

    func ended(shouldResume: Bool, play: () -> Void) {
        interrupted = false
        guard shouldResume, wasPlayingBeforeInterruption else {
            wasPlayingBeforeInterruption = false
            return
        }
        play()
        wasPlayingBeforeInterruption = false
    }
}
~~~

Do not resume merely because an interruption ended. Check the current player item, current route, user settings, and the interruption options supplied by the system.

## Recipe 10: recover from media services reset

Recreate audio objects and configuration, but wait for user action before restarting.

~~~swift
import AVFoundation

@MainActor
final class MediaServiceRecovery {
    private let session = AVAudioSession.sharedInstance()
    private(set) var needsUserRecovery = false

    func mediaServicesWereReset() {
        needsUserRecovery = true
        // Recreate AVPlayer, AVAudioEngine, converters, or queues here.
        // Reapply category, mode, options, and route-sharing policy.
        try? session.setActive(false)
    }

    func userChoseResume() throws {
        try session.setActive(true)
        needsUserRecovery = false
    }
}
~~~

Record the source and queue revision across the reset. Do not auto-play, auto-record, or auto-process after a media-server restart.

## Recipe 11: represent AirPlay and receiver state

Use a state model that refuses to call selection a receipt.

~~~swift
enum ReceiverState: Sendable, Equatable {
    case local
    case pickerPresented
    case selecting
    case selected(name: String)
    case rendering(name: String)
    case unavailable(reason: String)
    case canceled
}

struct ReceiverObservation: Sendable, Equatable {
    let state: ReceiverState
    let routeSnapshot: AudioRouteSnapshot?
    let playerIsPlaying: Bool
    let observedAt: Date
}
~~~

The selected state comes from the route/player observation after the system interaction. The rendering state needs the actual renderer/player signal and, for release claims, a physical receiver observation.

## Recipe 12: configure long-form audio policy

Use the long-form route-sharing policy only for extended listening.

~~~swift
import AVFAudio

func configureLongFormAudio() throws {
    let session = AVAudioSession.sharedInstance()
    try session.setCategory(
        .playback,
        mode: .default,
        policy: .longFormAudio,
        options: []
    )
}
~~~

This is a policy hint that can enable AirPlay 2 behavior for compatible long-form audio. It is not proof of receiver availability or multiroom playback.

## Recipe 13: publish Now Playing metadata

Project actual player state to MediaPlayer.

~~~swift
import MediaPlayer

@MainActor
func publishNowPlaying(
    title: String,
    artist: String?,
    duration: Double,
    elapsed: Double,
    rate: Float,
    queueIndex: Int,
    queueCount: Int
) {
    var info: [String: Any] = [
        MPMediaItemPropertyTitle: title,
        MPMediaItemPropertyPlaybackDuration: duration,
        MPNowPlayingInfoPropertyElapsedPlaybackTime: elapsed,
        MPNowPlayingInfoPropertyPlaybackRate: rate,
        MPNowPlayingInfoPropertyPlaybackQueueIndex: queueIndex,
        MPNowPlayingInfoPropertyPlaybackQueueCount: queueCount
    ]

    if let artist {
        info[MPMediaItemPropertyArtist] = artist
    }

    MPNowPlayingInfoCenter.default().nowPlayingInfo = info
}
~~~

Update only from actual player observations. Review whether metadata may appear on Lock Screen, CarPlay, Watch, AirPlay, or suggestions.

## Recipe 14: configure only supported remote commands

Handlers should call the same player command service as the app UI.

~~~swift
import MediaPlayer

@MainActor
final class RemoteCommandCoordinator {
    private let center = MPRemoteCommandCenter.shared()

    func start(
        play: @escaping @MainActor () -> MPRemoteCommandHandlerStatus,
        pause: @escaping @MainActor () -> MPRemoteCommandHandlerStatus,
        skipForward: @escaping @MainActor () -> MPRemoteCommandHandlerStatus
    ) {
        center.playCommand.addTarget { _ in
            play()
        }
        center.pauseCommand.addTarget { _ in
            pause()
        }
        center.skipForwardCommand.addTarget { _ in
            skipForward()
        }
    }

    func setSkipForwardEnabled(_ enabled: Bool) {
        center.skipForwardCommand.isEnabled = enabled
    }

    func stop() {
        center.playCommand.removeTarget(nil)
        center.pauseCommand.removeTarget(nil)
        center.skipForwardCommand.removeTarget(nil)
    }
}
~~~

Disable commands the current item cannot perform. Do not return success before the player or domain command has accepted the operation.

## Recipe 15: model a revisioned playback command

Use the same command service for app, CarPlay, Watch, Siri, and remote controls.

~~~swift
import Foundation

struct PlaybackCommand: Codable, Sendable, Equatable {
    enum Kind: String, Codable, Sendable {
        case play
        case pause
        case seek
        case skipForward
        case skipBackward
        case chooseRoute
    }

    let id: UUID
    let kind: Kind
    let itemID: String?
    let expectedRevision: Int64
    let origin: String
}

enum PlaybackCommandResult: Sendable, Equatable {
    case accepted(newRevision: Int64)
    case rejected(reason: String)
    case stale(currentRevision: Int64)
    case unavailable(reason: String)
}
~~~

A remote command receipt is not a domain commit. Persist idempotency and revision decisions when the action affects a queue, saved position, or shared account state.

## Recipe 16: describe multiroute output mapping

Keep stream-to-port mapping explicit.

~~~swift
import AVFAudio

struct OutputAssignment: Sendable, Equatable {
    let streamID: String
    let portUID: String
    let channelCount: Int
}

struct MultiRouteProjection: Sendable, Equatable {
    let assignments: [OutputAssignment]
    let availableOutputs: [String]
    let invalidAssignments: [String]
}
~~~

When a route changes, recompute assignments against current output ports and hardware channels. Do not continue to render into a missing port or call the multiroute graph stable because it was valid once.

## Recipe 17: inspect rendering capability

Expose capability without promising listener perception.

~~~swift
import AVFAudio

struct RenderingObservation: Sendable, Equatable {
    let mode: AVAudioSession.RenderingMode
    let supportedLayouts: Int
    let route: AudioRouteSnapshot?
    let observedAt: Date
}

func renderingObservation() -> RenderingObservation {
    let session = AVAudioSession.sharedInstance()
    return RenderingObservation(
        mode: session.renderingMode,
        supportedLayouts: session.supportedOutputChannelLayouts.count,
        route: makeRouteSnapshot(from: session.currentRoute),
        observedAt: .now
    )
}
~~~

The rendering mode can be not applicable when playback is inactive, muted, ineligible, on an unsupported route, or using another playback API. Provide a standard fallback.

## Recipe 18: represent Speech asset readiness

Speech assets are managed by the system and can be unavailable or downloading.

~~~swift
import Speech

enum SpeechReadiness: Sendable, Equatable {
    case unsupported
    case needsInstallation
    case installing
    case ready
    case failed(String)
}

struct SpeechPlan: Sendable, Equatable {
    let locale: Locale
    let readiness: SpeechReadiness
}
~~~

Use the current AssetInventory APIs to inspect and install the assets required by the selected Speech modules. Do not pass raw audio to the model because an asset appears supported; record the actual installed/readiness state.

## Recipe 19: keep transcript revisions explicit

Partial speech output is not the same as a committed transcript.

~~~swift
import Foundation

struct TranscriptSegment: Codable, Sendable, Equatable {
    let id: UUID
    let text: String
    let startSeconds: Double?
    let endSeconds: Double?
    let sourceRevision: Int64
    let isFinal: Bool
}

struct TranscriptProjection: Codable, Sendable, Equatable {
    let sourceID: String
    let sourceRevision: Int64
    let localeIdentifier: String
    let segments: [TranscriptSegment]
    let isComplete: Bool
    let observedAt: Date
}
~~~

Keep the original audio and transcript revision. If the source is edited or replaced, reject stale model output.

## Recipe 20: gate Foundation Models and propose a bounded summary

Use a typed proposal and deterministic validation.

~~~swift
import FoundationModels

enum ModelReadiness: Sendable, Equatable {
    case ready
    case unavailable(String)
}

func modelReadiness() -> ModelReadiness {
    switch SystemLanguageModel.default.availability {
    case .available:
        return .ready
    case .unavailable(let reason):
        return .unavailable(String(describing: reason))
    @unknown default:
        return .unavailable("Unknown model state")
    }
}

struct AudioSummaryCandidate: Codable, Sendable, Equatable {
    let sourceID: String
    let sourceRevision: Int64
    let title: String
    let summary: String
    let tags: [String]
}
~~~

Check the model’s supported locale, context size, and capability before prompting. Limit text to what is needed and show the result as a draft until the user accepts it.

## Recipe 21: review the AI candidate

Do not mutate the recording record from model output alone.

~~~swift
struct AudioAIReview: Sendable, Equatable {
    let candidate: AudioSummaryCandidate
    let validation: Validation
    let decision: Decision

    enum Validation: Sendable, Equatable {
        case valid
        case stale
        case tooLong
        case missingSource
        case unavailable
    }

    enum Decision: Sendable, Equatable {
        case pending
        case accepted
        case rejected
        case edited
    }
}

func validate(
    _ candidate: AudioSummaryCandidate,
    currentSourceRevision: Int64,
    currentSourceID: String,
    maxSummaryCharacters: Int
) -> AudioAIReview.Validation {
    guard candidate.sourceID == currentSourceID else { return .missingSource }
    guard candidate.sourceRevision == currentSourceRevision else { return .stale }
    guard candidate.summary.count <= maxSummaryCharacters else { return .tooLong }
    return .valid
}
~~~

Save user edits as a new domain revision. Keep source, transcript, proposal, and accepted record separate.

## Recipe 22: build a native SwiftUI audio shell

Use functional grouping for Liquid Glass and keep the transcript readable.

~~~swift
import SwiftUI

struct AudioPlayerShell: View {
    let title: String
    let route: String
    let isPlaying: Bool
    let togglePlayback: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 18) {
            Text(title)
                .font(.title.bold())

            Label(route, systemImage: "speaker.wave.2")
                .font(.subheadline)
                .foregroundStyle(.secondary)

            HStack(spacing: 12) {
                Button(action: togglePlayback) {
                    Label(
                        isPlaying ? "Pause" : "Play",
                        systemImage: isPlaying ? "pause.fill" : "play.fill"
                    )
                }
                .buttonStyle(.borderedProminent)

                OutputRoutePicker()
            }
            .padding()
            .glassEffect()

            Text("Captions and transcript available")
                .font(.footnote)
                .foregroundStyle(.secondary)
        }
        .padding()
    }
}
~~~

Test reduced transparency and high contrast. Do not place this custom shell in CarPlay, Lock Screen, Control Center, Watch, or AirPlay system UI.

## Recipe 23: use a text alternative for spatial audio

Make the fallback explicit.

~~~swift
struct SpatialAudioStatusView: View {
    let renderingMode: AVAudioSession.RenderingMode
    let transcriptAvailable: Bool

    var body: some View {
        VStack(alignment: .leading) {
            Text(renderingLabel)
            if transcriptAvailable {
                Label("Transcript available", systemImage: "captions.bubble")
            }
        }
    }

    private var renderingLabel: String {
        switch renderingMode {
        case .spatialAudio, .dolbyAudio, .dolbyAtmos:
            return "Enhanced audio active"
        case .monoStereo, .surround:
            return "Standard audio active"
        case .notApplicable:
            return "Audio capability unavailable"
        @unknown default:
            return "Audio capability unknown"
        }
    }
}
~~~

Use the exact current SDK cases and product wording. A framework rendering mode is not proof of a listener’s perception.

## Recipe 24: record a physical route evidence item

Make device and output context part of the observation.

~~~swift
import Foundation

struct AudioEvidence: Codable, Sendable, Equatable {
    enum Kind: String, Codable, Sendable {
        case source
        case compile
        case preview
        case simulator
        case physicalDevice
        case airPlayReceiver
        case carPlay
        case watch
        case archive
        case testFlight
        case production
    }

    let kind: Kind
    let deviceModel: String?
    let osVersion: String?
    let appVersion: String?
    let build: String?
    let inputRoute: String?
    let outputRoute: String?
    let sessionDescription: String?
    let playerState: String?
    let observation: String
    let timestamp: Date
}
~~~

Never write “AirPlay works” without naming the receiver, device, build, route, and observation.

## Recipe 25: test stale AI output and commands

Keep pure validation tests separate from hardware tests.

~~~swift
import Testing

@Test
func staleSummaryCannotBeAccepted() {
    let candidate = AudioSummaryCandidate(
        sourceID: "recording-1",
        sourceRevision: 2,
        title: "Draft",
        summary: "Summary",
        tags: ["meeting"]
    )

    let result = validate(
        candidate,
        currentSourceRevision: 3,
        currentSourceID: "recording-1",
        maxSummaryCharacters: 500
    )

    #expect(result == .stale)
}
~~~

Add tests for duplicate remote commands, unsupported seek, missing receiver, route loss, interruption end without resume, media-services reset, unsupported Speech locale, model unavailable, context too large, and user rejection.

## Recipe 26: archive and inspect audio configuration

Use a signed release artifact for target and entitlement claims.

~~~text
xcodebuild -scheme YourApp -configuration Release archive -archivePath build/YourApp.xcarchive

codesign -d --entitlements :- build/YourApp.xcarchive/Products/Applications/YourApp.app

plutil -p build/YourApp.xcarchive/Products/Applications/YourApp.app/Info.plist

find build/YourApp.xcarchive/Products -maxdepth 4 -type f -name '*Info.plist'
~~~

Inspect microphone and speech usage descriptions, background audio modes, CarPlay or Watch target relationships, ActivityKit/WidgetKit extensions, version/build, and signed entitlements. Then install the archive or TestFlight build on the physical device and run the route matrix.

## Recipe 27: final route record

~~~text
audio outcome:
category:
mode:
options:
route sharing policy:
activation trigger:
deactivation trigger:
player or engine owner:
input route:
output route:
AirPlay receiver:
CarPlay:
Watch:
multiroute:
spatial mode:
interruption result:
media services reset result:
Now Playing result:
remote command result:
Speech assets:
transcript revision:
Foundation Models availability:
AI validation and user decision:
Liquid Glass fallback:
accessibility result:
privacy result:
physical evidence:
archive/TestFlight result:
open risks:
~~~

A blank field means the route is unresolved.

## Sources

- [AVFAudio](https://developer.apple.com/documentation/avfaudio)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Audio routing](https://developer.apple.com/documentation/avfaudio/audio-routing)
- [Responding to audio route changes](https://developer.apple.com/documentation/avfaudio/responding-to-audio-route-changes)
- [Handling audio interruptions](https://developer.apple.com/documentation/avfaudio/handling-audio-interruptions)
- [AVRoutePickerView](https://developer.apple.com/documentation/avkit/avroutepickerview)
- [Playing custom audio with your own player](https://developer.apple.com/documentation/avfaudio/playing-custom-audio-with-your-own-player)
- [MediaPlayer](https://developer.apple.com/documentation/mediaplayer)
- [Becoming a now playable app](https://developer.apple.com/documentation/mediaplayer/becoming-a-now-playable-app)
- [MPNowPlayingInfoCenter](https://developer.apple.com/documentation/mediaplayer/mpnowplayinginfocenter)
- [MPNowPlayingSession](https://developer.apple.com/documentation/mediaplayer/mpnowplayingsession)
- [MPRemoteCommandCenter](https://developer.apple.com/documentation/mediaplayer/mpremotecommandcenter)
- [Speech](https://developer.apple.com/documentation/speech)
- [SpeechAnalyzer](https://developer.apple.com/documentation/speech/speechanalyzer)
- [SpeechTranscriber](https://developer.apple.com/documentation/speech/speechtranscriber)
- [AssetInventory](https://developer.apple.com/documentation/speech/assetinventory)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [LanguageModelCapabilities](https://developer.apple.com/documentation/foundationmodels/languagemodelcapabilities)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
