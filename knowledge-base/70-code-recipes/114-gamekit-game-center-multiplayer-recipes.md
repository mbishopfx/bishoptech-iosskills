# GameKit, Game Center, and multiplayer recipes

## How to use these recipes

These are compile-oriented route sketches for a named iOS target. Replace the
placeholder bundle/service IDs, state schemas, presentation contexts, and
authentication/server policy.

Before adopting a recipe:

- enable Game Center in the intended target and inspect the signed archive;
- configure matching App Store Connect records;
- test with real Game Center accounts and a physical device;
- keep GameKit callbacks outside SwiftUI view recomputation;
- make gameplay state/reducer authority explicit;
- bound and version every multiplayer payload;
- keep AI proposals behind the same action validator as human input;
- redact player IDs, private chat, tokens, and match payloads from logs.

## Recipe 1: local-player authentication coordinator

Game Center supplies the authentication interface through the authenticateHandler.
Present the provided controller from the current app-owned UIKit context and
translate callbacks into app state.

~~~swift
import GameKit
import UIKit

@MainActor
final class GameCenterCoordinator: NSObject {
    enum State: Equatable {
        case idle
        case presenting
        case authenticated(playerID: String)
        case unavailable(String)
    }

    private(set) var state: State = .idle
    private var didRegisterListener = false

    func start(presenting rootViewController: UIViewController) {
        let player = GKLocalPlayer.local

        player.authenticateHandler = { [weak self, weak rootViewController] viewController, error in
            Task { @MainActor in
                guard let self else { return }

                if let viewController {
                    self.state = .presenting
                    rootViewController?.present(viewController, animated: true)
                    return
                }

                if player.isAuthenticated {
                    if !self.didRegisterListener {
                        player.register(self)
                        self.didRegisterListener = true
                    }
                    self.state = .authenticated(playerID: player.gamePlayerID)
                } else {
                    let message = error?.localizedDescription ?? "Game Center is unavailable."
                    self.state = .unavailable(message)
                }
            }
        }
    }

    func stop() {
        if didRegisterListener {
            GKLocalPlayer.local.unregisterListener(self)
            didRegisterListener = false
        }
        GKLocalPlayer.local.authenticateHandler = nil
        state = .idle
    }
}

extension GameCenterCoordinator: GKLocalPlayerListener {
    func player(_ player: GKPlayer, didAccept invite: GKInvite) {
        // Route the invite through a typed app state machine.
    }
}
~~~

The exact listener methods depend on the selected GameKit feature. Register once,
keep the coordinator alive for the app/session lifecycle, and avoid attaching
old player-scoped pending writes after the account changes.

## Recipe 2: show the Game Center access point

Place the shared access point in a menu/settings context. The system owns the
overlay/dashboard; the app owns when it is appropriate to activate.

~~~swift
import GameKit

@MainActor
func configureGameCenterAccessPoint() {
    let accessPoint = GKAccessPoint.shared
    accessPoint.location = .topLeading
    accessPoint.showHighlights = true
    accessPoint.isActive = true
}

@MainActor
func hideGameCenterAccessPoint() {
    GKAccessPoint.shared.isActive = false
}
~~~

The location choices and presentation behavior are target/platform-specific.
Keep controls away from the access point, pause or quiet active gameplay while
the system surface is shown when needed, and verify the real host rather than
using a preview as proof.

## Recipe 3: report an achievement

Validate a gameplay milestone before creating a Game Center report. Store a
pending local report if offline or if the product needs retry/reconciliation.

~~~swift
import GameKit

struct AchievementReport: Sendable {
    let identifier: String
    let percentComplete: Double
    let runID: UUID
}

func reportAchievement(
    _ report: AchievementReport,
    completion: @escaping @Sendable (Result<Void, Error>) -> Void
) {
    guard GKLocalPlayer.local.isAuthenticated else {
        completion(.failure(GameCenterError.notAuthenticated))
        return
    }

    let achievement = GKAchievement(identifier: report.identifier)
    achievement.percentComplete = min(max(report.percentComplete.rounded(), 0), 100)

    GKAchievement.report([achievement]) { error in
        if let error {
            completion(.failure(error))
        } else {
            completion(.success(()))
        }
    }
}

enum GameCenterError: Error {
    case notAuthenticated
    case invalidScore
    case invalidMove
    case incompatibleState
}
~~~

The report callback proves a GameKit operation returned without an error. Keep
the local milestone, pending report, and service acknowledgement as separate
states. Do not report model confidence as achievement progress.

## Recipe 4: submit a validated leaderboard score

Configure the identifier and score semantics in App Store Connect. Submit only
after the local run passes the app's rule and anti-cheat policy.

~~~swift
import GameKit

struct ValidatedScore: Sendable {
    let leaderboardID: String
    let value: Int
    let context: Int
    let runID: UUID
}

func submit(
    score: ValidatedScore,
    completion: @escaping @Sendable (Result<Void, Error>) -> Void
) {
    guard GKLocalPlayer.local.isAuthenticated else {
        completion(.failure(GameCenterError.notAuthenticated))
        return
    }

    GKLeaderboard.submitScore(
        score.value,
        context: score.context,
        player: GKLocalPlayer.local,
        leaderboardIDs: [score.leaderboardID]
    ) { error in
        if let error {
            completion(.failure(error))
        } else {
            completion(.success(()))
        }
    }
}
~~~

For a competitive game, the score should also carry a run ID and game/rule
version into a trusted validation path. A local submit call is not anti-cheat
proof.

## Recipe 5: load leaderboard entries for a display route

Load leaderboard data for display only. Show the time/player scope and a stale or
unavailable state when the service cannot respond.

~~~swift
import GameKit

func loadLeaderboard(
    identifier: String,
    range: NSRange = NSRange(location: 1, length: 10),
    completion: @escaping @Sendable (Result<GKLeaderboardDisplay, Error>) -> Void
) {
    GKLeaderboard.loadLeaderboards(IDs: [identifier]) { leaderboards, error in
        if let error {
            completion(.failure(error))
            return
        }

        guard let leaderboard = leaderboards?.first else {
            completion(.failure(GameCenterError.incompatibleState))
            return
        }

        leaderboard.loadEntries(
            for: .global,
            timeScope: .allTime,
            range: range
        ) { localEntry, entries, totalPlayerCount, error in
            if let error {
                completion(.failure(error))
                return
            }

            completion(
                .success(
                    GKLeaderboardDisplay(
                        leaderboardID: identifier,
                        localEntry: localEntry,
                        entries: entries ?? [],
                        totalPlayerCount: totalPlayerCount
                    )
                )
            )
        }
    }
}

struct GKLeaderboardDisplay: Sendable {
    let leaderboardID: String
    let localEntry: GKLeaderboard.Entry?
    let entries: [GKLeaderboard.Entry]
    let totalPlayerCount: Int
}
~~~

The exact overload and isolation annotations may change with the target SDK.
Compile this in the named target and add a mapper that strips unsafe/private
fields before the SwiftUI view receives it.

## Recipe 6: create a real-time match request

Use the Game Center interface when it provides the intended invitation and
automatch experience. Keep the minimum/maximum player rules in the game
configuration.

~~~swift
import GameKit
import UIKit

@MainActor
func presentRealTimeMatchmaker(
    from rootViewController: UIViewController,
    delegate: GKMatchmakerViewControllerDelegate
) {
    let request = GKMatchRequest()
    request.minPlayers = 2
    request.maxPlayers = 2

    guard let viewController = GKMatchmakerViewController(matchRequest: request) else {
        return
    }

    viewController.matchmakerDelegate = delegate
    rootViewController.present(viewController, animated: true)
}
~~~

Add recipients, player properties, queue/rule configuration, and invite handling
only when the game contract needs them. The matchmaker result is a lobby/service
event, not permission to begin gameplay before the match protocol is ready.

## Recipe 7: real-time match controller and bounded messages

The controller below sketches the delegate seam. The game reducer should validate
the decoded message before applying it.

~~~swift
import GameKit

struct GameMessage: Codable, Sendable {
    let version: Int
    let sequence: Int64
    let stateRevision: Int64
    let kind: String
    let payload: Data
}

final class RealtimeMatchController: NSObject, GKMatchDelegate {
    private(set) var match: GKMatch?
    private let queue = DispatchQueue(label: "com.example.game.match")
    private let maximumMessageBytes = 512_000
    private var nextSequence: Int64 = 0

    func start(match: GKMatch) {
        self.match = match
        match.delegate = self
    }

    func send(_ message: GameMessage, reliable: Bool) throws {
        let data = try JSONEncoder().encode(message)
        guard data.count <= maximumMessageBytes else {
            throw GameCenterError.incompatibleState
        }

        let mode: GKMatch.SendDataMode = reliable ? .reliable : .unreliable
        try match?.sendData(toAllPlayers: data, with: mode)
    }

    func stop() {
        match?.disconnect()
        match = nil
    }

    func match(
        _ match: GKMatch,
        player: GKPlayer,
        didChange state: GKPlayerConnectionState
    ) {
        queue.async {
            // Convert state into connecting/ready/disconnected/reconnect policy.
        }
    }

    func match(
        _ match: GKMatch,
        didReceive data: Data,
        fromRemotePlayer player: GKPlayer
    ) {
        guard data.count <= maximumMessageBytes else {
            match.disconnect()
            return
        }

        queue.async {
            do {
                let message = try JSONDecoder().decode(GameMessage.self, from: data)
                // Check sender, version, sequence, state revision, phase, and
                // legal action before sending a typed event to the reducer.
                _ = message
                _ = player
            } catch {
                match.disconnect()
            }
        }
    }
}
~~~

Do not mutate SwiftUI state from an arbitrary delegate queue. Translate callbacks
to typed events and let one state owner decide whether to resync, pause, reject,
or end the match. Add an acknowledgement/snapshot route for critical state.

## Recipe 8: turn-based match request and event listener

Create a turn-based matchmaker view controller and route received turn events to
the current match ID/state owner.

~~~swift
import GameKit
import UIKit

@MainActor
func presentTurnBasedMatchmaker(
    from rootViewController: UIViewController,
    delegate: GKTurnBasedMatchmakerViewControllerDelegate,
    minPlayers: Int,
    maxPlayers: Int
) {
    let request = GKMatchRequest()
    request.minPlayers = minPlayers
    request.maxPlayers = maxPlayers

    let viewController = GKTurnBasedMatchmakerViewController(matchRequest: request)
    viewController.turnBasedMatchmakerDelegate = delegate
    rootViewController.present(viewController, animated: true)
}

final class TurnBasedListener: NSObject, GKTurnBasedEventListener {
    func player(
        _ player: GKPlayer,
        receivedTurnEventFor match: GKTurnBasedMatch,
        didBecomeActive: Bool
    ) {
        // Load matchID, participants, currentParticipant, status, and matchData.
        // Decode a bounded, versioned state before showing a turn action.
        _ = player
        _ = match
        _ = didBecomeActive
    }
}
~~~

Implement the other listener methods for invitations, exchanges, quit requests,
or rematches only when the selected game uses them. Register the listener once
after authentication and keep match events associated with the match ID.

## Recipe 9: validate and end a turn

The move validator must run before the turn data is sent to Game Center.

~~~swift
import GameKit

struct BoardState: Codable, Sendable {
    let schemaVersion: Int
    let revision: Int64
    let currentPlayerID: String
    let cells: [Int]
}

struct Move: Codable, Sendable {
    let index: Int
}

func endTurn(
    match: GKTurnBasedMatch,
    state: BoardState,
    nextParticipants: [GKTurnBasedParticipant],
    turnTimeout: TimeInterval
) async throws {
    guard match.currentParticipant?.player?.gamePlayerID == state.currentPlayerID else {
        throw GameCenterError.invalidMove
    }

    guard state.cells.count <= 256 else {
        throw GameCenterError.incompatibleState
    }

    let data = try JSONEncoder().encode(state)

    try await withCheckedThrowingContinuation { continuation in
        match.endTurn(
            withNextParticipants: nextParticipants,
            turnTimeout: turnTimeout,
            match: data
        ) { error in
            if let error {
                continuation.resume(throwing: error)
            } else {
                continuation.resume(returning: ())
            }
        }
    }
}
~~~

Add a transaction/revision policy around local persistence. A successful
completion handler means Game Center accepted the operation according to that
API; update the local cache and user-visible state with the service result.

## Recipe 10: SwiftUI wrapper for a GameKit view controller

Use a representable only for a documented GameKit UIKit controller. The parent
owns whether the sheet is presented and the Coordinator translates dismissal/
delegate callbacks exactly once.

~~~swift
import GameKit
import SwiftUI
import UIKit

struct MatchmakerSheet: UIViewControllerRepresentable {
    let request: GKMatchRequest
    let onFinished: @MainActor @Sendable () -> Void

    func makeCoordinator() -> Coordinator {
        Coordinator(onFinished: onFinished)
    }

    func makeUIViewController(context: Context) -> GKMatchmakerViewController {
        let controller = GKMatchmakerViewController(matchRequest: request)!
        controller.matchmakerDelegate = context.coordinator
        return controller
    }

    func updateUIViewController(
        _ controller: GKMatchmakerViewController,
        context: Context
    ) {
        // Do not rebuild the matchmaker for ordinary SwiftUI state changes.
    }

    final class Coordinator: NSObject, GKMatchmakerViewControllerDelegate {
        let onFinished: @MainActor @Sendable () -> Void

        init(onFinished: @escaping @MainActor @Sendable () -> Void) {
            self.onFinished = onFinished
        }

        func matchmakerViewController(
            _ viewController: GKMatchmakerViewController,
            didFind match: GKMatch
        ) {
            Task { @MainActor in
                onFinished()
            }
        }

        func matchmakerViewControllerWasCancelled(
            _ viewController: GKMatchmakerViewController
        ) {
            Task { @MainActor in
                onFinished()
            }
        }

        func matchmakerViewController(
            _ viewController: GKMatchmakerViewController,
            didFailWithError error: Error
        ) {
            Task { @MainActor in
                onFinished()
            }
        }
    }
}
~~~

In a production route, pass the found match/error through a typed result rather
than only dismissing. Protect against both delegate dismissal and parent sheet
state trying to finish the route twice.

## Recipe 11: model suggestion through the action validator

Keep the model output typed and visible. The validator should be shared by
human input, controller input, and the model.

~~~swift
struct GameAction: Codable, Sendable, Equatable {
    let sourceRevision: Int64
    let playerID: String
    let kind: String
    let payload: Data
}

enum ActionDecision: Sendable, Equatable {
    case accepted(GameAction)
    case stale
    case notThisPlayer
    case illegal
    case hiddenInformation
}

struct GameActionValidator: Sendable {
    func validate(
        _ action: GameAction,
        currentRevision: Int64,
        currentPlayerID: String,
        visibleState: Data
    ) -> ActionDecision {
        guard action.sourceRevision == currentRevision else { return .stale }
        guard action.playerID == currentPlayerID else { return .notThisPlayer }

        // Decode the typed payload, check the rule set, and compare against
        // visibleState. Never let a model provide hidden state or a side effect.
        _ = visibleState
        return .accepted(action)
    }
}
~~~

The UI can present the accepted action as a suggestion and ask the player to
apply it. The final commit should pass through the same validator and match
protocol as a human action.

## Recipe 12: deterministic multiplayer fixtures

Use fixtures to prove reducer/protocol behavior before using two physical devices.

~~~swift
@Test
func duplicateRealtimeActionDoesNotAdvanceTwice() throws {
    let first = GameMessage(
        version: 1,
        sequence: 7,
        stateRevision: 12,
        kind: "move",
        payload: Data([1, 2, 3])
    )

    let second = first

    let reducer = TestReducer()
    try reducer.apply(first)
    try reducer.apply(second)

    #expect(reducer.acceptedSequences == [7])
}

@Test
func staleTurnStateIsReadOnly() async throws {
    // Decode an older schema/revision and verify the app exposes repair/read-only
    // state rather than guessing a move or calling endTurn.
}
~~~

Add physical-device tests for account authentication, invitation, overlay,
connection loss, turn handoff, app termination, and release service IDs. Local
fixtures cannot prove Game Center delivery or multiplayer fairness.

## Recipe 13: release evidence record

Keep a redacted record tied to the build:

~~~yaml
target: NamedGameTarget
sdk: selected iOS SDK
deployment_target: selected minimum
game_center:
  capability_enabled: true
  signed_entitlement_inspected: true
  app_store_connect_ids_reviewed: true
  achievements_localized: true
  leaderboards_localized: true
  activities_or_challenges_reviewed: false
multiplayer:
  mode: real_time_or_turn_based
  two_device_tested: true
  reconnect_tested: true
  account_change_tested: true
ai:
  visible_state_only: true
  action_validator_shared: true
  ranked_mode_policy_explicit: true
accessibility:
  voiceover: true
  dynamic_type: true
  reduced_motion: true
  alternate_input: true
privacy:
  friend_usage_string_reviewed: true
  player_ids_redacted: true
  chat_and_match_data_redacted: true
release:
  configuration: Release
  testflight_or_signed_device: true
~~~

Never store player credentials, private messages, raw match payloads, or
unredacted identifiers in the record.

## Sources

- [GameKit](https://developer.apple.com/documentation/gamekit/)
- [Game Center entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.game-center)
- [Authenticating a player](https://developer.apple.com/documentation/gamekit/authenticating-a-player)
- [GKLocalPlayer](https://developer.apple.com/documentation/gamekit/gklocalplayer)
- [GKAccessPoint](https://developer.apple.com/documentation/gamekit/gkaccesspoint)
- [GKAchievement](https://developer.apple.com/documentation/gamekit/gkachievement)
- [GKLeaderboard](https://developer.apple.com/documentation/gamekit/gkleaderboard)
- [GKMatchRequest](https://developer.apple.com/documentation/gamekit/gkmatchrequest)
- [GKMatchmaker](https://developer.apple.com/documentation/gamekit/gkmatchmaker)
- [GKMatchmakerViewController](https://developer.apple.com/documentation/gamekit/gkmatchmakerviewcontroller)
- [GKMatch](https://developer.apple.com/documentation/gamekit/gkmatch)
- [GKMatchDelegate](https://developer.apple.com/documentation/gamekit/gkmatchdelegate)
- [Creating real-time games](https://developer.apple.com/documentation/gamekit/creating-real-time-games)
- [Finding multiple players for a game](https://developer.apple.com/documentation/gamekit/finding-multiple-players-for-a-game)
- [GKTurnBasedMatch](https://developer.apple.com/documentation/gamekit/gkturnbasedmatch)
- [GKTurnBasedParticipant](https://developer.apple.com/documentation/gamekit/gkturnbasedparticipant)
- [GKTurnBasedMatchmakerViewController](https://developer.apple.com/documentation/gamekit/gkturnbasedmatchmakerviewcontroller)
- [GKTurnBasedEventListener](https://developer.apple.com/documentation/gamekit/gkturnbasedeventlistener)
- [Starting turn-based matches and passing turns between players](https://developer.apple.com/documentation/gamekit/starting-turn-based-matches-and-passing-turns-between-players)
- [Game Center](https://developer.apple.com/design/human-interface-guidelines/game-center)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
