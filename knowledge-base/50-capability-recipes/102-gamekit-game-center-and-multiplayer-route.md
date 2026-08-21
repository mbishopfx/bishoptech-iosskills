# GameKit, Game Center, and multiplayer capability route

## Capability contract

Use this route when a game needs Apple-native player identity, social progress,
system discovery, invitations, real-time play, turn-based play, or a Game Center
projection of validated gameplay.

The route produces:

1. a configured Game Center target and App Store Connect service records;
2. an explicit local-player/authentication state;
3. a deterministic game-state owner and versioned action protocol;
4. a service-specific progression or multiplayer route;
5. a SwiftUI/UIKit presentation and system-surface boundary;
6. on-device AI proposal/validation rules;
7. physical two-device and release evidence.

GameKit does not replace a game engine, persistence model, anti-cheat policy,
custom server, or accessibility design.

## Start with the game mode

| Game need | Preferred GameKit route | Keep separate |
| --- | --- | --- |
| Single-player progression | GKAchievement and optional GKLeaderboard | Local save/replay and authoritative score policy |
| Social profile/menu | GKAccessPoint and Game Center system UI | App-owned settings/navigation |
| Real-time peer game | GKMatchmaker/GKMatch | Game reducer, protocol, resync, authority |
| Turn-based board/card game | GKTurnBasedMatch | Legal-move reducer, versioned data, local cache |
| Friend invitation | GKLocalPlayer listener/system Game Center UI | Contact permissions and account linking |
| Challenge/activity discovery | App Store Connect activity/challenge config + deep link | Current game state and stale-link fallback |
| Cross-device single-player | GameKit saved game data or selected iCloud route | Versioning, conflict, storage policy |
| Competitive economy/inventory | GameKit projection plus trusted server | StoreKit entitlement and server authority |

## Target and service setup

1. Select the SDK, deployment target, platforms, and device families.
2. Add the Game Center capability to the intended game target.
3. Inspect the signed entitlement in a development/archive product.
4. Configure the Game Center service in App Store Connect.
5. Create/localize achievement and leaderboard IDs.
6. Configure recurring leaderboards/sets/activities/challenges when needed.
7. Set supported player counts and match rules.
8. Add friend-list usage text only if the selected friend route needs it.
9. Keep development/sandbox/release IDs and server accounts distinct.
10. Record target membership for any GameKit/UIKit/SwiftUI adapter or extension.
11. Test with the actual Game Center accounts and service environment.

Do not assume a capability added to the project is present in the exported
archive. Do not assume an App Store Connect record is available in every build
configuration.

## Route A: authenticate the local player

1. Create an authentication coordinator owned by the app lifecycle.
2. Set GKLocalPlayer.local.authenticateHandler.
3. Present the provided system view controller from the current presentation
   context when one is supplied.
4. Translate authenticated, unavailable, signed-out, restricted, and error states
   into an app-owned enum.
5. Register relevant GKLocalPlayerListener objects once.
6. Load player-scoped data only after the authenticated state is current.
7. Reconcile or discard old player-scoped caches after account changes.
8. Enable access-point visibility only in menu/settings contexts.
9. Continue a useful local game when Game Center is unavailable.

Do not block the first gameplay screen on social sign-in unless the game truly
requires it. Do not implement a custom password or biometric flow for Game
Center.

## Route B: access point and social entry

1. Obtain the shared GKAccessPoint.
2. Select a menu/settings window or platform-supported presentation context.
3. Set its location without overlapping critical controls.
4. Activate it after the game menu is ready.
5. Pause/quiet the game while the overlay/dashboard is visible if needed.
6. Keep custom profile/leaderboard/achievement links labeled and optional.
7. Use official Game Center artwork/terminology for custom links.
8. Test access point unavailable/hidden/expanded/overlay-dismissed states.

The access point is a route into Game Center. It is not a durable app state, and
its visibility does not prove that a player is authenticated for a mutation.

## Route C: achievement progression

1. Define the achievement in App Store Connect.
2. Give the local domain a stable achievement identifier.
3. Validate the gameplay milestone locally.
4. Convert progress to the documented integer percentage.
5. Store a pending report keyed by player/achievement/run.
6. Report through GKAchievement.
7. Record service acknowledgement or retryable failure.
8. Project pending/submitted/completed status to the app UI.
9. Never let a model or unvalidated client event complete an achievement.

Use a monotonic policy when appropriate. If a player can earn the achievement
through multiple modes, store the rule and source run so the report is explainable.

## Route D: leaderboard score

1. Configure a leaderboard ID, sort direction, score unit, and mode in App Store
   Connect.
2. Validate the completed run and produce a score candidate.
3. Record a run ID, game version, rule set, and anti-cheat status.
4. Submit with the intended leaderboard ID/context/player.
5. Handle offline, authentication, validation, and service errors.
6. Load entries only for display and scope them by player/time/range.
7. Distinguish local best, pending submission, accepted score, and current rank.
8. Handle recurring occurrence rollover.
9. Do not use a leaderboard entry as inventory, entitlement, or account authority.

A score can be accepted by Game Center while a separate server policy rejects the
run for competitive ranking. Name those states separately when both exist.

## Route E: friends, invitations, challenges, and activities

1. Decide whether to use Game Center system UI or an app-owned entry point.
2. Request friend-list access only when the feature needs it.
3. Add NSGKFriendListUsageDescription when required by the route.
4. Keep player IDs, display names, contacts, and friendship status distinct.
5. Register the local-player listener for invitations and relevant events.
6. Parse an invitation/activity/challenge into a typed destination.
7. Verify game version, current player, match state, and privacy scope.
8. Show a confirmation/review surface before joining or mutating state.
9. Restore the destination after process termination or cold launch.
10. Handle declined, expired, removed, or incompatible invitations safely.

Do not let a model invent a friend, join a match, or send an invitation without an
explicit app-owned action and permission policy.

## Route F: real-time match

1. Authenticate and register listeners.
2. Build a GKMatchRequest with min/max players and optional recipients/rules.
3. Present GKMatchmakerViewController or use the documented automatic-matching
   route.
4. Handle cancel, invitation acceptance, and matchmaker errors.
5. On a found GKMatch, dismiss the UI and set the match delegate.
6. Exchange protocol version, game mode, capabilities, and initial state.
7. Start the reducer only after the required connection state is reached.
8. Send versioned actions/snapshots with sequence numbers.
9. Validate sender, phase, turn, revision, size, and legal state.
10. Handle player connection changes, receive errors, backgrounding, and resync.
11. End/leave/forfeit with an explicit local result.
12. Persist replay/session metadata if the product promises recovery.
13. Close the match delegate/session at the lifecycle boundary.

Reliable and unreliable data modes serve different protocols. Do not use
unreliable delivery for a mutation that cannot be rebuilt, and do not send
unbounded high-frequency snapshots without a backpressure/resync design.

## Route G: turn-based match

1. Authenticate and register GKTurnBasedEventListener.
2. Build a GKMatchRequest with the supported player count.
3. Present GKTurnBasedMatchmakerViewController or accept an invitation.
4. On a received match, verify match ID/version/participant/currentParticipant.
5. Load or reconstruct the local board from versioned match data.
6. Reject input when it is not the local player's turn.
7. Validate the move deterministically.
8. Serialize the next game state with a schema version and bounded size.
9. Call endTurn with the next participant set and turn timeout when appropriate.
10. Handle participant quit in/out of turn and match outcomes.
11. Refresh the UI on received turn events, participant status changes, and cold
    launch.
12. Keep a local cache marked current only after the service write/event boundary.
13. Support stale/incompatible data, expired turn, deleted match, and retry.

Game Center stores/forwards the turn data, but legal-move validation remains an
app/game responsibility. Use a server when the game requires stronger authority.

## Route H: game-state and AI assistant

Use a reducer and action envelope:

~~~yaml
action:
  match_id: stable-gamekit-or-domain-id
  game_version: semantic-or-build-version
  state_revision: local-accepted-revision
  sender: player-or-slot
  kind: typed-action
  payload: bounded-encoded-data
  request_id: dedupe-key
proposal:
  source_revision: state_revision
  visible_state_scope: explicit
  model_route: on-device
  action: typed-candidate
  legality: checked-by-app
  approval: required-or-mode-policy
~~~

The model can suggest a legal action, but the app validates:

- current state revision;
- player/turn ownership;
- rule legality;
- hidden-information scope;
- score/resource invariants;
- duplicate request;
- match/server authority;
- accessibility or assist mode policy.

Commit a model suggestion only through the same action pipeline as a human
action. Never give a model direct access to GKMatch send methods or turn-ending
methods.

## Route I: SwiftUI and UIKit surface

Keep GameKit service ownership out of view recomputation:

~~~swift
Game Center service coordinator
  -> typed app-owned state
  -> SwiftUI menu/lobby/match/review surface
  -> explicit action
  -> GameKit/service operation
  -> durable local result/projection
~~~

Use UIViewControllerRepresentable only for a documented GameKit view controller
that the selected target needs to present. The Coordinator translates delegate
events into one app-owned state machine and dismisses exactly once.

The game scene should not be replaced by a full social dashboard. Use the system
access point or a small custom action that opens the system surface.

## Route J: recovery and fallback

| Condition | State | Safe fallback |
| --- | --- | --- |
| Game Center not authenticated | Local/social unavailable | Play local mode; show sign-in route |
| Account restricted/declines | Feature unavailable | Explain and preserve local progress |
| Service timeout | Pending/retryable | Keep run/move locally, dedupe retry |
| Matchmaker canceled | Lobby canceled | Return to menu without false match |
| Player disconnects | Paused/reconnecting | Resync, wait, forfeit, or safe end |
| Malformed peer data | Protocol failure | Reject frame and terminate/resync |
| Turn data incompatible | Needs update | Read-only/error route; never decode blindly |
| Achievement/score pending | Local success/service pending | Show honest pending state |
| Leaderboard unavailable | Rank unknown | Show local result and retry |
| Friend access denied | Social list unavailable | Use system invitation or local fallback |
| Activity/challenge stale | Destination unavailable | Open the normal game route |
| Model unavailable | Assistant unavailable | Manual move/explanation route |
| Source state changed | Proposal stale | Recompute/review |

## Evidence plan

Capture:

- target/SDK/deployment/device family;
- Game Center capability and signed entitlement;
- App Store Connect IDs and localization;
- test accounts and service environment;
- authentication and account-change traces;
- deterministic reducer/codec/progression fixtures;
- real-time two-device connection/sequence/reconnect logs;
- turn-based two-account event/timeout/quit traces;
- system access-point/invitation/overlay evidence;
- AI proposal visibility/legality/approval tests;
- accessibility and alternate-input results;
- release/TestFlight Game Center configuration and production-like checks.

Do not put credentials, player IDs, private chat, or raw match payloads in the
evidence package.

## Sources

- [GameKit](https://developer.apple.com/documentation/gamekit/)
- [Game Center entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.game-center)
- [Authenticating a player](https://developer.apple.com/documentation/gamekit/authenticating-a-player)
- [GKLocalPlayer](https://developer.apple.com/documentation/gamekit/gklocalplayer)
- [GKAccessPoint](https://developer.apple.com/documentation/gamekit/gkaccesspoint)
- [GKAchievement](https://developer.apple.com/documentation/gamekit/gkachievement)
- [GKLeaderboard](https://developer.apple.com/documentation/gamekit/gkleaderboard)
- [GKLeaderboardSet](https://developer.apple.com/documentation/gamekit/gkleaderboardset)
- [Finding multiple players for a game](https://developer.apple.com/documentation/gamekit/finding-multiple-players-for-a-game)
- [Connecting players with their friends in your game](https://developer.apple.com/documentation/gamekit/connecting-players-with-their-friends-in-your-game)
- [Creating activities for your game](https://developer.apple.com/documentation/gamekit/creating-activities-for-your-game)
- [Creating real-time games](https://developer.apple.com/documentation/gamekit/creating-real-time-games)
- [GKMatchRequest](https://developer.apple.com/documentation/gamekit/gkmatchrequest)
- [GKMatchmaker](https://developer.apple.com/documentation/gamekit/gkmatchmaker)
- [GKMatch](https://developer.apple.com/documentation/gamekit/gkmatch)
- [Creating turn-based games](https://developer.apple.com/documentation/gamekit/creating-turn-based-games)
- [GKTurnBasedMatch](https://developer.apple.com/documentation/gamekit/gkturnbasedmatch)
- [GKTurnBasedParticipant](https://developer.apple.com/documentation/gamekit/gkturnbasedparticipant)
- [GKTurnBasedEventListener](https://developer.apple.com/documentation/gamekit/gkturnbasedeventlistener)
- [Human Interface Guidelines: Game Center](https://developer.apple.com/design/human-interface-guidelines/game-center)
