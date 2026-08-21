# GameKit and Game Center multiplayer

## Scope

This page defines the native GameKit route for iOS apps and games that need
Game Center identity, social progress, achievements, leaderboards, friends,
challenges, game activities, real-time matches, or turn-based matches.

It covers:

- Game Center capability and local-player authentication;
- GKLocalPlayer, GKPlayer, listener registration, account restrictions, and
  authentication changes;
- GKAccessPoint and system-owned Game Center overlay/dashboard;
- GKAchievement and GKAchievementDescription progress;
- GKLeaderboard, GKLeaderboardSet, score submission, occurrences, and loading;
- friends, friend-list authorization, invites, challenges, and activities;
- GKMatchRequest, GKMatchmaker, GKMatchmakerViewController, GKMatch, and
  GKMatchDelegate real-time lifecycle;
- GKTurnBasedMatch, participants, turn events, exchanges, match outcomes, and
  stored match data;
- SwiftUI/UIKit presentation seams;
- deterministic game state, on-device AI proposal boundaries, anti-cheat
  responsibilities, privacy, accessibility, and physical/release proof.

GameKit is a service and multiplayer boundary. A local game state reducer remains
the gameplay source of truth inside the running process, while Game Center or a
server owns the service records and player/session identity appropriate to the
route.

## Version and configuration boundary

Record:

- selected SDK and deployment target;
- supported Apple platforms and device families;
- bundle identifier and Team;
- Game Center capability and signed entitlement;
- App Store Connect Game Center configuration;
- leaderboards, recurring leaderboards, leaderboard sets, achievements, challenges,
  and activities;
- authentication/account restriction policy;
- real-time versus turn-based match mode;
- server authority, if a custom server or hosted match is used;
- accessibility and input matrix;
- physical-device/two-account and release evidence.

Before using GameKit classes, enable Game Center and initialize the local player.
Apple documents that failing to initialize/authenticate can produce a not
authenticated error. A symbol compiling does not prove that:

- the Game Center capability is signed into the target;
- the player is signed in or allowed to use the feature;
- App Store Connect identifiers match the build;
- a friend or contact is visible;
- an invitation will launch the app;
- a match will connect, stay connected, or deliver every event;
- a score or achievement has been accepted;
- a turn-based write has reached all participants;
- a model-generated move is legal or fair;
- a release build has the correct environment.

## Choose the GameKit route

| Outcome | First route | Important boundary |
| --- | --- | --- |
| Identify the player for Game Center features | GKLocalPlayer authentication | Authentication is service identity, not a custom account/session policy |
| Open the player's Game Center information | GKAccessPoint | The overlay/dashboard is system-owned; do not rebuild it as if it were your source |
| Report progression | GKAchievement | App Store Connect achievement configuration and player/service state apply |
| Compare scores | GKLeaderboard/GKLeaderboardSet | Leaderboard display and score acceptance are Game Center service results |
| View or invite friends | GKLocalPlayer friend APIs, invites, or system UI | Friend-list privacy authorization and social boundaries apply |
| Real-time game | GKMatchRequest, GKMatchmaker, GKMatch | Define protocol, state snapshots, sequence, reconnect, and host/authority |
| Turn-based game | GKTurnBasedMatch and event listener | Game Center stores/forwards turn data; the app owns legal move validation |
| Contextual Game Center activity | Game Center activities/challenges | App Store Connect configuration, artwork, deep-link route, and system discovery |
| Cross-device single-player resume | Game Center saved game data or selected iCloud route | Define versioning, conflict, privacy, and account scope |
| Authoritative competitive action | GameKit plus trusted server/validated protocol | Local AI or client state cannot be the anti-cheat authority |

Use the narrowest route. A real-time match is not automatically a durable cloud
save, and a leaderboard is not an authoritative inventory or payment ledger.

## Game Center capability and App Store Connect

Game Center configuration has two sides:

    Xcode target capability and signed entitlement
      -> runtime local-player authentication
      -> App Store Connect Game Center records
      -> service operation
      -> app-owned local projection

Configure identifiers and localization in App Store Connect, then reference the
matching IDs in the target. Keep development/sandbox and production/release
configuration separate. Verify the exported archive rather than assuming the
Xcode capability checkbox describes the shipped entitlement.

App Store Connect configuration can include:

- achievements and descriptions;
- classic or recurring leaderboards;
- leaderboard sets;
- challenges or activities;
- multiplayer settings and supported player counts;
- artwork, localization, and display text.

Treat service configuration as versioned product data. Do not hard-code a label
that disagrees with the Game Center dashboard or imply that a score is ranked
until the service response confirms it.

## Local-player authentication

GKLocalPlayer.local represents the player using the game. Set its
authenticateHandler early enough that Game Center can present its system
authentication UI from the correct presentation context.

The handler can be invoked more than once:

- with a view controller that the app must present;
- after authentication succeeds;
- after the player declines or cannot authenticate;
- after an account or restriction changes.

The app should model:

    unknown
      -> presentingSystemAuthentication
      -> authenticated
      -> unavailable(reason)
      -> signedOutOrRestricted
      -> authenticated again

When authentication changes:

1. stop or pause Game Center operations that require the old identity;
2. remove player-scoped caches and pending service writes when policy requires;
3. close or reconcile a match according to the route;
4. refresh access-point visibility and player display;
5. rebuild local projections with the new stable player ID;
6. avoid attaching the old player's unsent action or score to the new player.

Register the appropriate local-player listener for invitations, match events, or
turn-based events. Keep listener registration idempotent and remove it when a
target/process lifecycle requires.

Authentication is not a replacement for an app account. If a product has a
server account, link the Game Center player identity according to a reviewed
server flow and never use an unverified nickname or display name as identity.

## System-owned Game Center surfaces

GKAccessPoint provides a system-designed control that opens the Game Center
overlay or dashboard. Use the shared access point and activate it only when the
main menu/settings context makes it useful.

Apple's Game Center design guidance recommends:

- place the access point in menu screens;
- avoid active gameplay, splash screens, cinematics, and tutorials;
- keep nearby controls from overlapping its collapsed/expanded forms;
- consider pausing the game while the overlay/dashboard is present;
- use official Game Center artwork and terminology when creating custom links;
- let the system UI provide player profile, achievements, leaderboards, and
  friends-management experiences where appropriate.

Do not present a fake Game Center sheet that implies the player has opened the
system service. A custom leaderboard or achievement screen can be useful, but
label it as app content and keep the system route available.

## Achievements

GKAchievement identifies an achievement configured in App Store Connect and
reports progress for a player. Apple documents percentComplete as an integer
percentage from 0 through 100. The game decides how progress maps to its domain.

A safe achievement route is:

    local validated milestone
      -> stable achievement identifier
      -> monotonic local pending report
      -> GKAchievement report
      -> service acknowledgement
      -> local projection/access-point refresh

Keep achievement progress separate from arbitrary model confidence. A player
earning an achievement should be caused by a validated gameplay milestone, not by
a model saying that a milestone probably occurred.

Define:

- stable identifier and localized display;
- whether progress is monotonic;
- whether multiple local events collapse into one report;
- retry and duplicate-report behavior;
- account change/reset behavior;
- offline queue and privacy policy;
- whether an achievement can be earned in a particular mode or difficulty;
- what happens if the service is unavailable.

If a score or achievement has competitive meaning, server-side validation may be
required. A client report is evidence of a client request, not proof that a
player legitimately achieved the result.

## Leaderboards

GKLeaderboard represents a Game Center leaderboard. The game can submit scores
and load entries using configured identifiers, player scope, time scope, and rank
ranges. GKLeaderboardSet groups leaderboards in App Store Connect.

Keep the gameplay event and service report separate:

    completed validated run
      -> score candidate
      -> local result record
      -> leaderboard submission
      -> service result/error
      -> rank/leaderboard projection

Record:

- leaderboard ID and version;
- score unit and sort direction;
- context field semantics;
- game mode/difficulty/season;
- source run ID;
- player ID and account scope;
- local submission state;
- service response and last error;
- anti-cheat or server validation status.

A loaded entry is a service projection. It can be stale, filtered by scope/time,
or unavailable due to account/privacy/network state. Do not use a displayed rank as
a local authorization or inventory value.

Recurring leaderboards need an occurrence policy: the current occurrence, previous
occurrence, time window, score reset, and UI copy must agree. Test a new
occurrence, an expired occurrence, offline submission, duplicate submission, and
a player with no score.

## Friends, challenges, and activities

Game Center offers friend and social routes, but the player controls the social
boundary. If the game loads friend data, use the documented authorization and
usage-description flow. Apple documents NSGKFriendListUsageDescription for friend
list access in relevant routes.

Distinguish:

- a Game Center player identity;
- a friend relationship;
- a recent opponent;
- a contact or invited recipient;
- a visible display name/avatar;
- an authorized friend-list result;
- a challenge/activity participant.

Do not scrape contacts or infer a friend relationship from a player identifier.
Use system UI for friend requests and invitations where Apple provides it.

Game Center activities and challenges can connect system discovery to a deep link
inside the game. Treat the deep link as untrusted input:

1. parse a typed activity/challenge identifier;
2. validate that it belongs to the current game and supported version;
3. resolve current player/account permission;
4. load current gameplay state;
5. show the destination context;
6. ask for confirmation before consequential actions;
7. fall back safely if the activity is stale, removed, or unsupported.

## Real-time multiplayer

A real-time route uses GKMatchRequest, matchmaking, GKMatch, and delegate/listener
lifecycle. The Game Center interface can invite friends, nearby/recent players,
contacts, groups, or use automatic matching. The app can also use the
GKMatchmaker route without presenting the full interface where supported.

A real-time session needs two state machines:

    Game Center session:
      idle -> matching -> invited -> connecting -> connected
      connected -> disconnected -> reconnecting -> ended

    Game state:
      lobby -> countdown -> playing -> paused -> finished
      playing -> desynchronized -> resyncing -> aborted

When the match is found:

1. dismiss or finish the matchmaker UI;
2. retain the GKMatch for the session;
3. set its delegate;
4. exchange protocol/version/capability information;
5. establish player/slot mapping;
6. send a snapshot or deterministic initial seed;
7. start gameplay only after the required players are ready.

Use reliable data for messages that must arrive and an appropriate unreliable
route for high-frequency state where the game can recover from loss. Define the
data envelope with:

- protocol version;
- match/session ID;
- sender/player ID or slot;
- sequence number;
- tick or turn;
- message kind;
- payload length/decoder;
- checksum or validation where useful;
- acknowledgement or resync request for critical events.

Do not assume the delegate callback is a complete game state, that a player is
authenticated for your domain, or that a message is persisted after delivery.
Handle connection-state changes, player joins/leaves, errors, app backgrounding,
and match termination. A client-side reducer should reject messages that are
out-of-phase, from the wrong sender/slot, too large, malformed, or inconsistent
with the current revision.

If the game is competitive, choose an authoritative design. Game Center real-time
transport can carry gameplay data, but it does not automatically prevent a
modified client from sending an impossible state. Use a server or deterministic
validation protocol when the product risk warrants it.

## Turn-based multiplayer

A GKTurnBasedMatch is stored and forwarded by Game Center between participants.
It contains participant state, the current participant, match status, last-turn
message, and game-specific data. A game can have multiple open matches that
continue while players leave the app.

Turn-based state should be:

    current match snapshot
      -> validate local player's legal turn
      -> apply local move
      -> serialize versioned game data
      -> end turn or quit with documented outcome
      -> Game Center forwards to next participant
      -> event listener refreshes the app

The app must validate:

- match ID and game version;
- participant and current-turn identity;
- state revision;
- legal move;
- resource/currency/score invariants;
- timeout and forfeit policy;
- outcome assignment for every participant before ending the match;
- data size and decode failure;
- stale or duplicate event handling.

Use GKTurnBasedEventListener to update the UI when a turn becomes active,
participants change, or an invitation/match event arrives. Implement
participantQuitInTurn, participantQuitOutOfTurn, endTurn, and match-ending routes
according to the actual game rules.

Do not treat a turn-based match object as a substitute for local persistence.
Save a local copy for offline display and recovery, but mark it as cached until
the current Game Center event/write is reconciled.

## Game state and on-device AI

Use a deterministic game-state owner:

    input/control
      -> validated action
      -> reducer
      -> local state revision
      -> network/Game Center envelope
      -> peer/server validation
      -> accepted state
      -> rendering/projection

An on-device model can propose:

- a legal move from visible state;
- tutorial text;
- accessibility narration;
- opponent-summary text;
- level or challenge suggestions;
- practice-mode strategy hints;
- a cosmetic or pacing recommendation.

The model must not silently:

- choose a move for a player without consent in a competitive mode;
- access hidden opponent state;
- change score, rank, entitlement, or achievement status;
- send network packets outside the game action boundary;
- declare a match finished;
- bypass turn ownership or server validation;
- use private friend/profile data without authorization.

Represent a model suggestion as:

- source game-state revision;
- visible-state scope;
- model/device route;
- proposal text or typed action;
- legality validation result;
- user approval or mode policy;
- committed action ID;
- replay/audit metadata where appropriate.

For an AI assistant, show “Suggestion” or “Practice hint,” not “official move,”
until the app validates and commits it. Do not claim that local inference alone
makes a multiplayer game cheat-proof or that a generated explanation is a
record of what another player intended.

## Privacy, security, and retention

Game Center player data is service-scoped. Limit what the app copies into local
records, logs, widgets, notifications, analytics, or remote servers.

Review:

- local player identifier and account link;
- display name/avatar caching and deletion;
- friend-list permission and reason string;
- match data visibility;
- chat/message content;
- gameplay telemetry;
- anti-cheat evidence;
- location/contact use, if any;
- protected data and lock-screen previews;
- model prompts and hidden-state exposure;
- retention after sign-out or account unlinking.

Do not put raw player identifiers, invite payloads, private chat, or full match
snapshots in debug logs. Redact evidence packages and test fixtures.

## Accessibility and platform adaptation

Games still need a semantic menu, settings, progress, pause, turn, and recovery
route. Verify:

- VoiceOver labels current turn, match status, score, achievement, and actions;
- buttons and controls have stable names independent of player display names;
- color is not the only team/status signal;
- Dynamic Type works in menus, overlays, matchmaker wrappers, and result screens;
- reduced motion has a static or less intense mode;
- switch, Voice Control, keyboard, pointer, and controller users can pause, quit,
  inspect state, and recover;
- captions/transcripts exist for important audio cues;
- haptic feedback is supplemental;
- orientation and size-class changes do not destroy a match;
- iPad popovers/sheets and external display behavior are tested where supported;
- Game Center overlay does not hide required app-owned recovery state.

For custom Game Center links, use correct terminology and official artwork. Avoid
placing a custom glass card over the system Game Center overlay.

## Evidence boundary

Prove in layers:

1. source and App Store Connect configuration review;
2. named-target compile and signed entitlement inspection;
3. deterministic reducers, encoders, decoders, score/achievement, and AI proposal
   tests;
4. UI tests for authentication, menu/access-point state, pause, overlay, and
   recovery;
5. two physical devices/accounts for invitations, real-time match data, turn
   handoff, disconnect, and account changes;
6. release/TestFlight/Game Center production-like configuration for service IDs,
   leaderboard/achievement localization, privacy, and system delivery.

A local reducer, loaded leaderboard, found match, received event, or preview is
not proof of a complete multi-device experience.

## Sources

- [GameKit](https://developer.apple.com/documentation/gamekit/)
- [Authenticating a player](https://developer.apple.com/documentation/gamekit/authenticating-a-player)
- [GKLocalPlayer](https://developer.apple.com/documentation/gamekit/gklocalplayer)
- [GKPlayer](https://developer.apple.com/documentation/gamekit/gkplayer)
- [GKAccessPoint](https://developer.apple.com/documentation/gamekit/gkaccesspoint)
- [GKAchievement](https://developer.apple.com/documentation/gamekit/gkachievement)
- [GKAchievementDescription](https://developer.apple.com/documentation/gamekit/gkachievementdescription)
- [GKLeaderboard](https://developer.apple.com/documentation/gamekit/gkleaderboard)
- [GKLeaderboardSet](https://developer.apple.com/documentation/gamekit/gkleaderboardset)
- [Connecting players with their friends in your game](https://developer.apple.com/documentation/gamekit/connecting-players-with-their-friends-in-your-game)
- [Finding multiple players for a game](https://developer.apple.com/documentation/gamekit/finding-multiple-players-for-a-game)
- [Creating real-time games](https://developer.apple.com/documentation/gamekit/creating-real-time-games)
- [GKMatchRequest](https://developer.apple.com/documentation/gamekit/gkmatchrequest)
- [GKMatchmaker](https://developer.apple.com/documentation/gamekit/gkmatchmaker)
- [GKMatchmakerViewController](https://developer.apple.com/documentation/gamekit/gkmatchmakerviewcontroller)
- [GKMatch](https://developer.apple.com/documentation/gamekit/gkmatch)
- [GKMatchDelegate](https://developer.apple.com/documentation/gamekit/gkmatchdelegate)
- [GKInviteEventListener](https://developer.apple.com/documentation/gamekit/gkinviteeventlistener)
- [Creating turn-based games](https://developer.apple.com/documentation/gamekit/creating-turn-based-games)
- [Starting turn-based matches and passing turns between players](https://developer.apple.com/documentation/gamekit/starting-turn-based-matches-and-passing-turns-between-players)
- [GKTurnBasedMatch](https://developer.apple.com/documentation/gamekit/gkturnbasedmatch)
- [GKTurnBasedParticipant](https://developer.apple.com/documentation/gamekit/gkturnbasedparticipant)
- [GKTurnBasedMatchmakerViewController](https://developer.apple.com/documentation/gamekit/gkturnbasedmatchmakerviewcontroller)
- [GKTurnBasedEventListener](https://developer.apple.com/documentation/gamekit/gkturnbasedeventlistener)
- [Creating activities for your game](https://developer.apple.com/documentation/gamekit/creating-activities-for-your-game)
- [Game Center](https://developer.apple.com/design/human-interface-guidelines/game-center)
- [Designing for games](https://developer.apple.com/design/human-interface-guidelines/designing-for-games/)
