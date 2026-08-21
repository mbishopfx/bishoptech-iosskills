# MediaPlayer Now Playing recipes

These are compile-oriented route sketches for projecting playback state to Apple’s system media surfaces, handling external commands, coordinating a custom Now Playing session, reading the media library with authorization, and keeping on-device AI bounded.

They are not compiled in this documentation-only workspace and do not prove physical playback, Lock Screen or Control Center rendering, accessory behavior, media-library authorization, suggestion handling, accessibility, or release eligibility. Confirm the exact API signatures and availability in the SDK selected by the target.

Before copying:

1. Choose one playback owner and one Now Playing owner.
2. Keep AVFoundation/AVAudioSession state separate from MediaPlayer projection.
3. Configure the target’s audio/background/privacy declarations only for the feature actually shipped.
4. Begin playback before expecting external-player events.
5. Test system surfaces on a physical device.

## Recipe 1: Define typed playback state

Use a value model that can be projected to both SwiftUI and MediaPlayer:

~~~swift
import Foundation

struct PlaybackItem: Sendable, Equatable {
    let id: String
    let title: String
    let creator: String?
    let artworkURL: URL?
    let duration: TimeInterval?
    let isLive: Bool
}

enum PlaybackStatus: Sendable, Equatable {
    case idle
    case preparing
    case playing(rate: Float)
    case paused
    case buffering
    case interrupted
    case ended
    case failed
}

struct PlaybackState: Sendable, Equatable {
    var item: PlaybackItem?
    var position: TimeInterval = 0
    var queueIndex: Int?
    var queueCount: Int?
    var status: PlaybackStatus = .idle
    var canSeek = false
    var canGoNext = false
    var canGoPrevious = false
    var excludeFromSuggestions = false
}
~~~

The player engine should update this model from actual callbacks. Do not treat a button tap or timer tick as playback proof.

## Recipe 2: Project one item to the default information center

The default center is a simple route for one custom playback owner:

~~~swift
import MediaPlayer

struct NowPlayingProjector {
    func dictionary(for state: PlaybackState) -> [String: Any]? {
        guard let item = state.item else {
            return nil
        }

        var result = [String: Any]()
        result[MPMediaItemPropertyTitle] = item.title
        if let creator = item.creator {
            result[MPMediaItemPropertyArtist] = creator
        }
        if let duration = item.duration, !item.isLive {
            result[MPMediaItemPropertyPlaybackDuration] = duration
        }
        result[MPNowPlayingInfoPropertyElapsedPlaybackTime] = state.position
        result[MPNowPlayingInfoPropertyPlaybackRate] = rate(for: state.status)
        result[MPNowPlayingInfoPropertyIsLiveStream] = item.isLive
        result[MPNowPlayingInfoPropertyExcludeFromSuggestions] =
            state.excludeFromSuggestions
        if let index = state.queueIndex {
            result[MPNowPlayingInfoPropertyPlaybackQueueIndex] = index
        }
        if let count = state.queueCount {
            result[MPNowPlayingInfoPropertyPlaybackQueueCount] = count
        }
        return result
    }

    func publish(_ state: PlaybackState) {
        let center = MPNowPlayingInfoCenter.default()
        center.nowPlayingInfo = dictionary(for: state)
    }

    private func rate(for status: PlaybackStatus) -> Float {
        if case let .playing(rate) = status {
            return rate
        }
        return 0
    }
}
~~~

Confirm the exact metadata key/value behavior for the selected SDK, especially for live streams and suggestion exclusion. Omit fields that are unknown rather than inserting false values.

## Recipe 3: Load artwork without making the UI the source of truth

Artwork can be projected after the canonical item is known:

~~~swift
import MediaPlayer
import UIKit

struct ArtworkProjector {
    func artwork(for image: UIImage) -> MPMediaItemArtwork {
        MPMediaItemArtwork(boundsSize: image.size) { _ in
            image
        }
    }

    func apply(_ artwork: MPMediaItemArtwork, to state: PlaybackState) {
        guard state.item != nil else {
            return
        }
        var info = MPNowPlayingInfoCenter.default().nowPlayingInfo ?? [:]
        info[MPMediaItemPropertyArtwork] = artwork
        MPNowPlayingInfoCenter.default().nowPlayingInfo = info
    }
}
~~~

In production, prefer an image cache and a bounded decode path. Do not make remote artwork fetch completion overwrite metadata for a different item; compare the item ID before applying.

## Recipe 4: Register commands from current capabilities

Own registrations in one coordinator and keep teardown deterministic:

~~~swift
import MediaPlayer

final class RemoteCommandCoordinator {
    private let center = MPRemoteCommandCenter.shared()
    private var targets = [Any]()

    func install(
        play: @escaping () -> MPRemoteCommandHandlerStatus,
        pause: @escaping () -> MPRemoteCommandHandlerStatus,
        next: @escaping () -> MPRemoteCommandHandlerStatus,
        previous: @escaping () -> MPRemoteCommandHandlerStatus
    ) {
        center.playCommand.isEnabled = true
        center.pauseCommand.isEnabled = true
        center.nextTrackCommand.isEnabled = false
        center.previousTrackCommand.isEnabled = false

        targets.append(center.playCommand.addTarget { _ in
            play()
        })
        targets.append(center.pauseCommand.addTarget { _ in
            pause()
        })
        targets.append(center.nextTrackCommand.addTarget { _ in
            next()
        })
        targets.append(center.previousTrackCommand.addTarget { _ in
            previous()
        })
    }

    func updateCapabilities(
        canGoNext: Bool,
        canGoPrevious: Bool
    ) {
        center.nextTrackCommand.isEnabled = canGoNext
        center.previousTrackCommand.isEnabled = canGoPrevious
    }

    func removeAll() {
        center.playCommand.removeTarget(nil)
        center.pauseCommand.removeTarget(nil)
        center.nextTrackCommand.removeTarget(nil)
        center.previousTrackCommand.removeTarget(nil)
        targets.removeAll()
    }
}
~~~

The targets array is bookkeeping for the route; confirm the selected SDK’s handler-token type and cleanup API. A registered handler does not prove that the app will receive events before it is actively playing and eligible.

## Recipe 5: Handle seek and position-change commands

Translate external events into a typed operation and validate against the canonical state:

~~~swift
import MediaPlayer

final class SeekCommandCoordinator {
    private let command = MPRemoteCommandCenter.shared()
        .changePlaybackPositionCommand
    private var target: Any?
    private let readState: () -> PlaybackState
    private let seek: (TimeInterval) -> Bool

    init(
        readState: @escaping () -> PlaybackState,
        seek: @escaping (TimeInterval) -> Bool
    ) {
        self.readState = readState
        self.seek = seek
    }

    func install() {
        command.isEnabled = readState().canSeek
        target = command.addTarget { [readState, seek] event in
            guard let event = event as? MPChangePlaybackPositionCommandEvent
            else {
                return .commandFailed
            }
            let state = readState()
            guard state.canSeek,
                  let item = state.item,
                  let duration = item.duration,
                  !item.isLive,
                  event.positionTime >= 0,
                  event.positionTime <= duration
            else {
                return .commandFailed
            }
            return seek(event.positionTime)
                ? .success
                : .commandFailed
        }
    }

    func remove() {
        command.removeTarget(target)
        target = nil
    }
}
~~~

The exact removeTarget overload and handler-status spelling can be SDK-sensitive. Keep the important invariant: validate the range, perform the seek through the player owner, and publish the resulting position.

## Recipe 6: Choose an MPNowPlayingSession for multiple players

Use a named owner for custom AVPlayer objects:

~~~swift
import AVFoundation
import MediaPlayer

final class MultiPlayerNowPlayingCoordinator {
    private var session: MPNowPlayingSession?

    func start(players: [AVPlayer]) {
        let session = MPNowPlayingSession(players: players)
        session.automaticallyPublishesNowPlayingInfo = false
        self.session = session
        session.becomeActiveIfPossible()
    }

    func publish(_ state: PlaybackState) {
        session?.nowPlayingInfoCenter.nowPlayingInfo =
            NowPlayingProjector().dictionary(for: state)
    }

    func stop() {
        session?.isActive = false
        session = nil
    }
}
~~~

Do not add this custom session to an AVPlayer owned by AVPlayerViewController. If the controller owns the player/session, follow that ownership route instead.

## Recipe 7: Request media-library access just in time

Keep the permission state explicit:

~~~swift
import MediaPlayer
import Combine

enum LibraryAccessState: Equatable {
    case notDetermined
    case denied
    case restricted
    case authorized
}

@MainActor
final class MediaLibraryAccessModel: ObservableObject {
    @Published private(set) var state = LibraryAccessState.notDetermined

    func refresh() {
        state = Self.map(MPMediaLibrary.authorizationStatus())
    }

    func request() {
        MPMediaLibrary.requestAuthorization { [weak self] status in
            Task { @MainActor in
                self?.state = Self.map(status)
            }
        }
    }

    private static func map(
        _ status: MPMediaLibraryAuthorizationStatus
    ) -> LibraryAccessState {
        switch status {
        case .notDetermined:
            return .notDetermined
        case .denied:
            return .denied
        case .restricted:
            return .restricted
        case .authorized:
            return .authorized
        @unknown default:
            return .denied
        }
    }
}
~~~

Request only at the library feature boundary. App-owned playback and Now Playing publication should not depend on this permission.

## Recipe 8: Query a focused library projection

After authorization, query only what the feature needs:

~~~swift
import MediaPlayer

struct LibraryEntry: Sendable, Equatable {
    let persistentID: MPMediaEntityPersistentID
    let title: String
    let artist: String?
}

struct LibraryReader {
    func songs() -> [LibraryEntry] {
        let query = MPMediaQuery.songs()
        return query.items?.compactMap { item in
            guard let title = item.title else {
                return nil
            }
            return LibraryEntry(
                persistentID: item.persistentID,
                title: title,
                artist: item.artist
            )
        } ?? []
    }
}
~~~

Treat a library record as a catalog projection, not proof of playback permission, route availability, or current physical output. Redact or avoid persistent IDs in logs and AI context.

## Recipe 9: Handle library changes with bounded lifetime

Start and stop library-change notifications around the feature:

~~~swift
import MediaPlayer

final class LibraryChangeCoordinator {
    private var observing = false

    func start() {
        guard !observing else {
            return
        }
        MPMediaLibrary.default().beginGeneratingLibraryChangeNotifications()
        observing = true
    }

    func stop() {
        guard observing else {
            return
        }
        MPMediaLibrary.default().endGeneratingLibraryChangeNotifications()
        observing = false
    }
}
~~~

Pair this with the selected SDK’s notification observation and a cache invalidation policy. Do not assume a stale cached MPMediaItem is current after a library change.

## Recipe 10: Exclude a private item from suggestions

Apply the policy at the metadata projection boundary:

~~~swift
import MediaPlayer

func publishPrivate(_ state: PlaybackState) {
    var info = NowPlayingProjector().dictionary(for: state) ?? [:]
    info[MPNowPlayingInfoPropertyExcludeFromSuggestions] = true
    MPNowPlayingInfoCenter.default().nowPlayingInfo = info
}
~~~

The flag expresses the app’s contribution policy. It does not prove that a suggestion was or was not generated, and it should not replace a broader privacy/retention policy.

## Recipe 11: Keep an app-owned Liquid Glass player semantic

System surfaces are not replicated in the app. Keep the app-owned player driven by the same state:

~~~swift
import SwiftUI

struct PlayerTransportView: View {
    let state: PlaybackState
    let play: () -> Void
    let pause: () -> Void

    var body: some View {
        HStack(spacing: 12) {
            Text(state.item?.title ?? "Nothing playing")
                .lineLimit(2)
            Spacer()
            if case .playing = state.status {
                Button("Pause", systemImage: "pause.fill", action: pause)
            } else {
                Button("Play", systemImage: "play.fill", action: play)
            }
        }
        .padding()
        .glassEffect()
        .accessibilityElement(children: .contain)
    }
}
~~~

Confirm the selected SDK’s Liquid Glass modifier and availability. Keep a material fallback for reduced transparency, contrast settings, older deployment targets, and content that needs stable reading contrast.

## Recipe 12: Bound an AI playback proposal

Use a closed proposal type and validate it outside the model:

~~~swift
struct PlaybackProposal: Sendable, Equatable {
    let itemID: String
    let action: Action
    let requiresConfirmation: Bool

    enum Action: Sendable, Equatable {
        case play
        case pause
        case seek(TimeInterval)
        case setSuggestionExclusion(Bool)
    }
}

enum ProposalRejection: Error {
    case wrongItem
    case unsupported
    case outOfRange
    case confirmationRequired
}

struct PlaybackProposalValidator {
    func validate(
        _ proposal: PlaybackProposal,
        against state: PlaybackState,
        confirmed: Bool
    ) throws -> PlaybackAction {
        guard proposal.itemID == state.item?.id else {
            throw ProposalRejection.wrongItem
        }
        if proposal.requiresConfirmation && !confirmed {
            throw ProposalRejection.confirmationRequired
        }
        switch proposal.action {
        case .play:
            return .play
        case .pause:
            return .pause
        case let .seek(position):
            guard state.canSeek,
                  let item = state.item,
                  let duration = item.duration,
                  position >= 0,
                  position <= duration,
                  !item.isLive
            else {
                throw ProposalRejection.outOfRange
            }
            return .seek(position)
        case let .setSuggestionExclusion(value):
            return .setSuggestionExclusion(value)
        }
    }
}

enum PlaybackAction: Sendable, Equatable {
    case play
    case pause
    case seek(TimeInterval)
    case setSuggestionExclusion(Bool)
}
~~~

The model receives only the approved context needed for the proposal. It cannot invent a raw remote command, media-library query, stream URL, or completed-playback result.

## Recipe 13: Keep a proof fixture

Record semantic events rather than sensitive payloads:

~~~swift
struct PlaybackEvidence: Sendable, Equatable {
    let itemID: String?
    let status: String
    let position: TimeInterval?
    let command: String?
    let result: String
    let timestamp: Date
    let device: String
}
~~~

Pair an evidence record with the exact target/SDK, physical device, named system surface, and signed artifact. A local fixture is a test aid; it is not physical or release proof.

## Sources

- [Media Player](https://developer.apple.com/documentation/mediaplayer)
- [MPNowPlayingInfoCenter](https://developer.apple.com/documentation/mediaplayer/mpnowplayinginfocenter)
- [MPNowPlayingSession](https://developer.apple.com/documentation/mediaplayer/mpnowplayingsession)
- [MPRemoteCommandCenter](https://developer.apple.com/documentation/mediaplayer/mpremotecommandcenter)
- [MPRemoteCommand](https://developer.apple.com/documentation/mediaplayer/mpremotecommand)
- [MPRemoteCommandEvent](https://developer.apple.com/documentation/mediaplayer/mpremotecommandevent)
- [MPChangePlaybackPositionCommandEvent](https://developer.apple.com/documentation/mediaplayer/mpchangeplaybackpositioncommandevent)
- [Becoming a now playable app](https://developer.apple.com/documentation/mediaplayer/becoming-a-now-playable-app)
- [Handling external player events notifications](https://developer.apple.com/documentation/mediaplayer/handling-external-player-events-notifications)
- [MPMediaLibrary](https://developer.apple.com/documentation/mediaplayer/mpmedialibrary)
- [MPMediaLibraryAuthorizationStatus](https://developer.apple.com/documentation/mediaplayer/mpmedialibraryauthorizationstatus)
- [Request media library authorization](https://developer.apple.com/documentation/mediaplayer/mpmedialibrary/requestauthorization%28_%3A%29)
- [Exclude Now Playing items from suggestions](https://developer.apple.com/documentation/mediaplayer/mpnowplayinginfopropertyexcludefromsuggestions)
- [AVFoundation](https://developer.apple.com/documentation/avfoundation)
- [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
