# SwiftUI MediaPlayer Now Playing and remote-command code recipes

These are compile-oriented sketches for the focused [MediaPlayer Now Playing review](../42-framework-deep-dives/123-swiftui-mediaplayer-now-playing-review.md). They separate the app-owned player, AVAudioSession, MediaPlayer metadata, remote commands, artwork, route state, SwiftUI, and optional on-device AI.

Compile every selected symbol against the final iOS 26 SDK. These recipes are not proof of audible output, Lock Screen/Control Center presentation, AirPlay/CarPlay/Watch/accessory behavior, background audio, media-library authorization, privacy compliance, or release readiness.

Before copying:

1. Choose one playback owner.
2. Choose the default center or one MPNowPlayingSession.
3. Decide whether publication is automatic or explicit.
4. Keep player observations authoritative over UI intent.
5. Keep remote handlers registered by one long-lived coordinator.

## Recipe 1: PlaybackState and typed commands

Use one value model for SwiftUI and all system surfaces:

~~~swift
import Foundation

enum PlaybackStatus: Sendable, Equatable {
    case idle
    case loading
    case ready
    case playing
    case paused
    case buffering
    case interrupted
    case ended
    case failed(String)
}

struct PlaybackItem: Sendable, Equatable, Identifiable {
    let id: String
    let title: String
    let creator: String?
    let artworkID: String?
    let isLive: Bool
    let duration: TimeInterval?
}

struct PlaybackState: Sendable, Equatable {
    let generation: UInt64
    let item: PlaybackItem?
    let position: TimeInterval
    let rate: Float
    let status: PlaybackStatus
    let queueIndex: Int?
    let queueCount: Int?
    let routeName: String?
    let excludeFromSuggestions: Bool
}

enum PlaybackCommand: Sendable, Equatable {
    case play
    case pause
    case toggle
    case stop
    case next
    case previous
    case seek(TimeInterval)
    case changeRate(Float)
    case skip(TimeInterval)
}
~~~

The model distinguishes an intended command from the observed player result. Do not use the command enum as proof that the player completed the operation.

## Recipe 2: Build explicit Now Playing metadata

Project only from observed PlaybackState:

~~~swift
import MediaPlayer
import Foundation

func makeNowPlayingInfo(
    state: PlaybackState,
    artwork: MPMediaItemArtwork?
) -> [String: Any]? {
    guard let item = state.item else {
        return nil
    }

    var info: [String: Any] = [
        MPMediaItemPropertyTitle: item.title,
        MPNowPlayingInfoPropertyElapsedPlaybackTime: state.position,
        MPNowPlayingInfoPropertyPlaybackRate: state.rate,
        MPNowPlayingInfoPropertyIsLiveStream: item.isLive,
        MPNowPlayingInfoPropertyExcludeFromSuggestions:
            state.excludeFromSuggestions
    ]

    if let creator = item.creator {
        info[MPMediaItemPropertyArtist] = creator
    }
    if let duration = item.duration, !item.isLive {
        info[MPMediaItemPropertyPlaybackDuration] = duration
    }
    if let queueIndex = state.queueIndex {
        info[MPNowPlayingInfoPropertyPlaybackQueueIndex] = queueIndex
    }
    if let queueCount = state.queueCount {
        info[MPNowPlayingInfoPropertyPlaybackQueueCount] = queueCount
    }
    if let artwork {
        info[MPMediaItemPropertyArtwork] = artwork
    }

    return info
}
~~~

Use the actual player rate and observed position. If the item is stopped or invalid, set the default center’s nowPlayingInfo to nil rather than preserving stale controls.

## Recipe 3: Publish through the default center

Keep publication behind one coordinator:

~~~swift
import MediaPlayer

@MainActor
final class DefaultNowPlayingProjector {
    private let center = MPNowPlayingInfoCenter.default()

    func publish(
        state: PlaybackState,
        artwork: MPMediaItemArtwork?
    ) {
        center.nowPlayingInfo = makeNowPlayingInfo(
            state: state,
            artwork: artwork
        )
    }

    func clear() {
        center.nowPlayingInfo = nil
    }
}
~~~

Do not call this from a SwiftUI body. Call it after a new observed playback revision, queue revision, route change, interruption state, or item transition.

## Recipe 4: Size-aware artwork

Use the current item’s artwork revision and a bounded cache:

~~~swift
import MediaPlayer
import UIKit

actor ArtworkStore {
    private var images: [String: UIImage] = [:]

    func image(for id: String) -> UIImage? {
        images[id]
    }

    func insert(_ image: UIImage, for id: String) {
        images[id] = image
    }

    func removeAll() {
        images.removeAll()
    }
}

func makeArtwork(
    boundsSize: CGSize,
    store: ArtworkStore,
    artworkID: String,
    loader: @escaping @Sendable (String, CGSize) -> UIImage?
) -> MPMediaItemArtwork {
    MPMediaItemArtwork(
        boundsSize: boundsSize
    ) { requestedSize in
        loader(artworkID, requestedSize)
    }
}
~~~

The request handler must be fast enough for the system surface. In a production implementation, load/decode/cache outside the handler when possible, then publish a newer state only if artworkID and playback generation still match.

## Recipe 5: Register and remove remote handlers

Retain opaque handler tokens and register once:

~~~swift
import MediaPlayer

@MainActor
final class RemoteCommandRouter {
    private let commandCenter = MPRemoteCommandCenter.shared()
    private var tokens: [Any] = []

    func install(
        dispatch: @escaping @MainActor (PlaybackCommand) -> Void
    ) {
        removeAll()

        commandCenter.playCommand.isEnabled = true
        let play = commandCenter.playCommand.addTarget { _ in
            dispatch(.play)
            return .success
        }

        commandCenter.pauseCommand.isEnabled = true
        let pause = commandCenter.pauseCommand.addTarget { _ in
            dispatch(.pause)
            return .success
        }

        commandCenter.nextTrackCommand.isEnabled = false
        commandCenter.previousTrackCommand.isEnabled = false
        commandCenter.changePlaybackPositionCommand.isEnabled = false

        tokens = [play, pause]
    }

    func updateCapabilities(
        canGoNext: Bool,
        canGoPrevious: Bool,
        canSeek: Bool
    ) {
        commandCenter.nextTrackCommand.isEnabled = canGoNext
        commandCenter.previousTrackCommand.isEnabled = canGoPrevious
        commandCenter.changePlaybackPositionCommand.isEnabled = canSeek
    }

    func removeAll() {
        for token in tokens {
            commandCenter.playCommand.removeTarget(token)
            commandCenter.pauseCommand.removeTarget(token)
            commandCenter.nextTrackCommand.removeTarget(token)
            commandCenter.previousTrackCommand.removeTarget(token)
            commandCenter.changePlaybackPositionCommand.removeTarget(token)
        }
        tokens.removeAll()
    }
}
~~~

The exact actor isolation and handler closure diagnostics may require adaptation in the selected SDK. A handler token must be removed from the command that created it; use a small token wrapper in production when multiple commands share one lifecycle.

## Recipe 6: Return command status from player truth

Use a synchronous local state transition for the handler result:

~~~swift
import MediaPlayer

@MainActor
final class PlaybackCommandBridge {
    private(set) var state: PlaybackState

    init(state: PlaybackState) {
        self.state = state
    }

    func handlePlay() -> MPRemoteCommandHandlerStatus {
        guard state.item != nil else {
            return .noActionableNowPlayingItem
        }
        guard state.status == .paused || state.status == .ready else {
            return .commandFailed
        }
        state = PlaybackState(
            generation: state.generation + 1,
            item: state.item,
            position: state.position,
            rate: state.rate,
            status: .ready,
            queueIndex: state.queueIndex,
            queueCount: state.queueCount,
            routeName: state.routeName,
            excludeFromSuggestions: state.excludeFromSuggestions
        )
        return .success
    }
}
~~~

This sketch only proves acceptance by a local reducer. A real bridge should invoke the player and return success only under the product’s documented command policy. It must not return success merely because a remote request was queued for a later server response.

## Recipe 7: Handle seek position events

The event contains a requested position:

~~~swift
import MediaPlayer

func positionFrom(
    event: MPRemoteCommandEvent,
    duration: TimeInterval?
) -> TimeInterval? {
    guard let positionEvent =
            event as? MPChangePlaybackPositionCommandEvent else {
        return nil
    }

    let requested = positionEvent.positionTime
    guard requested.isFinite, requested >= 0 else {
        return nil
    }

    if let duration {
        guard requested <= duration else {
            return nil
        }
    }

    return requested
}
~~~

For live content, use the app’s supported seek policy instead of a finite duration check. Re-publish elapsed playback time from the player after the seek completes.

## Recipe 8: Configure a multi-player session

Use MPNowPlayingSession only for custom player ownership:

~~~swift
import AVFoundation
import MediaPlayer

@MainActor
final class MultiPlayerNowPlaying {
    let session: MPNowPlayingSession

    init(players: [AVPlayer]) {
        session = MPNowPlayingSession(players: players)
        session.automaticallyPublishesNowPlayingInfo = false
    }

    func add(_ player: AVPlayer) {
        session.addPlayer(player)
    }

    func remove(_ player: AVPlayer) {
        session.removePlayer(player)
    }

    func activateIfPossible(
        completion: @escaping (Bool) -> Void
    ) {
        session.becomeActiveIfPossible(completion: completion)
    }
}
~~~

Do not pass an AVPlayer that an AVPlayerViewController owns. Decide whether explicit publication through session.nowPlayingInfoCenter or automatic publication is the single mode.

## Recipe 9: Observe audio interruptions

Tie AVAudioSession notifications into the same playback reducer:

~~~swift
import AVFAudio
import Foundation

func observeInterruptions(
    handle: @escaping @Sendable (Notification) -> Void
) async {
    for await notification in NotificationCenter.default.notifications(
        named: AVAudioSession.interruptionNotification,
        object: AVAudioSession.sharedInstance()
    ) {
        handle(notification)
    }
}
~~~

The notification carries interruption details in userInfo. Update the player state, then republish metadata. Do not blindly resume when an interruption ends; use the player and audio policy.

## Recipe 10: Observe route changes

Route changes are a separate state stream:

~~~swift
import AVFAudio
import Foundation

func observeRouteChanges(
    handle: @escaping @Sendable (AVAudioSession.RouteChangeReason) -> Void
) async {
    for await notification in NotificationCenter.default.notifications(
        named: AVAudioSession.routeChangeNotification,
        object: AVAudioSession.sharedInstance()
    ) {
        let raw = notification.userInfo?[
            AVAudioSessionRouteChangeReasonKey
        ] as? UInt
        let reason = raw.flatMap {
            AVAudioSession.RouteChangeReason(rawValue: $0)
        } ?? .unknown
        handle(reason)
    }
}
~~~

The notification is delivered on a secondary thread. Hop to the playback coordinator’s isolation before mutating state. For oldDeviceUnavailable, pause private playback according to the product policy.

## Recipe 11: Configure playback audio

Set the category before activation and defer activation until playback:

~~~swift
import AVFAudio

func configurePlaybackAudio() throws {
    let session = AVAudioSession.sharedInstance()
    try session.setCategory(
        .playback,
        mode: .moviePlayback,
        options: [.allowAirPlay]
    )
}

func activatePlaybackAudio() throws {
    try AVAudioSession.sharedInstance().setActive(true)
}
~~~

The category/mode/options depend on the product. A successful setActive call does not prove that audio is audible on the intended route.

## Recipe 12: SwiftUI player shell

Observe the coordinator rather than constructing MediaPlayer objects in the view:

~~~swift
import SwiftUI

struct PlayerView: View {
    let state: PlaybackState
    let play: () -> Void
    let pause: () -> Void
    let seek: (Double) -> Void
    let showQueue: () -> Void
    let chooseRoute: () -> Void

    var body: some View {
        VStack(spacing: 20) {
            Text(state.item?.title ?? "No item")
                .font(.title2)
                .multilineTextAlignment(.center)

            Text(statusDescription)
                .foregroundStyle(.secondary)

            if let duration = state.item?.duration,
               duration > 0,
               !state.item!.isLive {
                Slider(
                    value: Binding(
                        get: { state.position },
                        set: seek
                    ),
                    in: 0...duration
                )
                .accessibilityLabel("Playback position")
            }

            HStack {
                Button(
                    state.status == .playing ? "Pause" : "Play",
                    action: state.status == .playing ? pause : play
                )
                .buttonStyle(.glassProminent)

                Button("Queue", action: showQueue)
                    .buttonStyle(.glass)

                Button("Choose route", action: chooseRoute)
                    .buttonStyle(.glass)
            }
        }
        .padding()
    }

    private var statusDescription: String {
        switch state.status {
        case .playing:
            return "Playing on \(state.routeName ?? "current audio route")"
        case .buffering:
            return "Buffering"
        case .interrupted:
            return "Playback interrupted"
        default:
            return "Playback available"
        }
    }
}
~~~

The exact Liquid Glass styles and availability fallback must be compiled against the selected SDK. Keep the state label accessible when a material is unavailable.

## Recipe 13: Typed AI playback proposal

Keep generated language away from direct player side effects:

~~~swift
import Foundation

struct PlaybackProposal: Sendable, Equatable {
    let proposalID: UUID
    let sourceQueueRevision: UInt64
    let action: PlaybackCommand
    let affectedItemIDs: [String]
    let reason: String
    let missingData: [String]
    let requiresUserReview: Bool
}

enum ProposalDecision: Sendable, Equatable {
    case stale
    case blocked(reason: String)
    case needsReview(PlaybackProposal)
    case accepted(PlaybackCommand)
}

func validate(
    proposal: PlaybackProposal,
    currentQueueRevision: UInt64,
    allowedItemIDs: Set<String>
) -> ProposalDecision {
    guard proposal.sourceQueueRevision == currentQueueRevision else {
        return .stale
    }
    guard proposal.affectedItemIDs.allSatisfy(allowedItemIDs.contains) else {
        return .blocked(reason: "An item is no longer eligible.")
    }
    guard proposal.requiresUserReview else {
        return .blocked(reason: "Playback changes require review.")
    }
    return .needsReview(proposal)
}
~~~

The user approval action revalidates the queue and item state again before executing. The model never writes nowPlayingInfo or registers an MPRemoteCommand handler.

## Recipe 14: Test projection boundaries

Use Swift Testing for deterministic state and projection tests:

~~~swift
import Testing

@Test
func missingItemClearsNowPlayingProjection() {
    let state = PlaybackState(
        generation: 4,
        item: nil,
        position: 0,
        rate: 0,
        status: .idle,
        queueIndex: nil,
        queueCount: nil,
        routeName: nil,
        excludeFromSuggestions: true
    )

    #expect(
        makeNowPlayingInfo(state: state, artwork: nil) == nil
    )
}

@Test
func liveItemDoesNotPublishFiniteDuration() {
    let item = PlaybackItem(
        id: "live-1",
        title: "Live stream",
        creator: nil,
        artworkID: nil,
        isLive: true,
        duration: 300
    )
    let state = PlaybackState(
        generation: 1,
        item: item,
        position: 10,
        rate: 1,
        status: .playing,
        queueIndex: nil,
        queueCount: nil,
        routeName: "iPhone",
        excludeFromSuggestions: false
    )

    let info = makeNowPlayingInfo(state: state, artwork: nil)
    #expect(info?[MPMediaItemPropertyPlaybackDuration] == nil)
}
~~~

These tests prove app-owned projection rules only. They do not prove system presentation or physical audio output.

## Sources

- [Media Player](https://developer.apple.com/documentation/mediaplayer)
- [MPNowPlayingInfoCenter](https://developer.apple.com/documentation/mediaplayer/mpnowplayinginfocenter)
- [MPNowPlayingSession](https://developer.apple.com/documentation/mediaplayer/mpnowplayingsession)
- [MPRemoteCommandCenter](https://developer.apple.com/documentation/mediaplayer/mpremotecommandcenter)
- [MPRemoteCommand](https://developer.apple.com/documentation/mediaplayer/mpremotecommand)
- [MPRemoteCommandHandlerStatus](https://developer.apple.com/documentation/mediaplayer/mpremotecommandhandlerstatus)
- [MPChangePlaybackPositionCommandEvent](https://developer.apple.com/documentation/mediaplayer/mpchangeplaybackpositioncommandevent)
- [Becoming a now playable app](https://developer.apple.com/documentation/mediaplayer/becoming-a-now-playable-app)
- [Handling external player events notifications](https://developer.apple.com/documentation/mediaplayer/handling-external-player-events-notifications)
- [MPMediaItemArtwork](https://developer.apple.com/documentation/mediaplayer/mpmediaitemartwork)
- [MPMediaLibrary](https://developer.apple.com/documentation/mediaplayer/mpmedialibrary)
- [MPNowPlayingInfoPropertyExcludeFromSuggestions](https://developer.apple.com/documentation/mediaplayer/mpnowplayinginfopropertyexcludefromsuggestions)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Handling audio interruptions](https://developer.apple.com/documentation/avfaudio/handling-audio-interruptions)
- [Responding to audio route changes](https://developer.apple.com/documentation/avfaudio/responding-to-audio-route-changes)
- [AVRoutePickerView](https://developer.apple.com/documentation/avkit/avroutepickerview)
- [CarPlay](https://developer.apple.com/documentation/carplay)
- [Watch Connectivity](https://developer.apple.com/documentation/watchconnectivity)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Swift Testing](https://developer.apple.com/documentation/testing)
