# Game Center, multiplayer, and native game-surface design

## Design objective

Game Center should make a game feel connected to Apple's platform without
interrupting play or turning a game menu into a social dashboard.

The design must answer:

- when the player is signed in, unavailable, restricted, or changing accounts;
- where the system Game Center surface belongs;
- what is local gameplay state versus a service projection;
- how a player knows a match is finding, connecting, paused, synchronized,
  disconnected, or ended;
- whether a score/achievement is pending, accepted, rejected, or unverified;
- whether a turn is local, waiting, expired, forfeited, or stale;
- what an on-device AI suggestion can see and do;
- how the game remains playable with no network, reduced motion, VoiceOver,
  alternate input, or a large text size.

The player should feel the game first and the service second.

## Native hierarchy

Use the game scene, menu, HUD, pause sheet, result screen, and settings route as
app-owned surfaces. Use Game Center's system UI for profile, friends, dashboard,
leaderboard, achievement, invitation, and access-point behavior where it fits.

A good hierarchy is:

    play
      -> pause/menu
      -> app-owned result/review
      -> system Game Center route when requested
      -> return to the same game state

Do not embed a fake dashboard inside a glass card just to imitate Apple UI.
Use standard navigation, sheets, confirmation, menus, buttons, and accessibility
semantics. Liquid Glass can support a functional layer such as a pause toolbar,
match-status capsule, result sheet, or settings action group; it should not cover
the playfield or compete with the system overlay.

## Access point placement

Apple's Game Center guidance recommends placing the access point in a menu or
settings context, away from active gameplay, splash screens, cinematic sequences,
and tutorials.

Use these rules:

- reserve the corner for the system access point;
- keep custom buttons and critical score elements clear of its collapsed/expanded
  geometry;
- pause or quiet the game when the Game Center overlay/dashboard is visible if
  gameplay would otherwise continue;
- preserve the game state across dismissal;
- do not place a decorative glass control directly underneath it;
- show the access point only when the product wants Game Center available in that
  context;
- test every supported orientation, window size, and platform.

If the access point is unavailable, the menu should still expose app-owned
settings/help/achievements routes without claiming that the system dashboard is
open.

## Visual language by state

| State | App-owned treatment | Copy | Avoid |
| --- | --- | --- | --- |
| Game Center unavailable | Compact neutral status | “Game Center unavailable” | Red alarm during gameplay |
| Authentication UI requested | System presentation | “Sign in to Game Center to use multiplayer” | Fake sign-in fields |
| Authenticated | Quiet profile/access-point route | Player display name only where useful | Treat nickname as account security |
| Finding match | Progress status and cancel | “Finding players…” | Indefinite spinner with no cancel |
| Invitation pending | Match lobby card | “Waiting for 1 player” | Start play before required players accept |
| Connecting | Stable lobby/play boundary | “Connecting…” | Treat match object creation as ready |
| Connected | In-game HUD/status | “2 players connected” | Covering the playfield with glass |
| Disconnected | Pause/reconnect route | “Connection lost” | Continue hidden state mutations |
| Resyncing | App-owned recovery sheet | “Restoring the match…” | Pretend the last frame was authoritative |
| Local turn | Clear turn indicator | “Your turn” | Color-only highlight |
| Waiting turn | Readable passive state | “Waiting for Alex” | Repeated intrusive alerts |
| Score pending | Result card status | “Submitting score…” | Claim rank before service response |
| Score accepted | Result/progression | “Score submitted” | Promise global rank at once |
| Achievement pending | Result detail | “Sending achievement progress…” | Treat local milestone as service receipt |
| AI suggestion | Review surface | “Practice suggestion” | “Best move” without scope/validation |

Use text, iconography, shape, and accessible traits together. Color and animation
can enrich the state but should not carry its meaning alone.

## Liquid Glass without imitation

Functional glass roles:

- pause and resume controls;
- match status and reconnect action;
- result sheet with score/progression;
- nonintrusive practice-hint review;
- settings/menu action group;
- small party-code or invite status card.

Keep the playfield legible and stable:

- use one clear material grouping for related actions;
- preserve contrast against dynamic game backgrounds;
- avoid glass behind dense gameplay text or fine hit targets;
- do not animate material continuously to represent packets or model tokens;
- respect reduced transparency and increased contrast;
- keep state changes in content/copy as well as material/tint;
- keep the system Game Center overlay visually untouched.

For a game with a strong visual identity, the artwork, scene, typography, sound,
and controls can be original while the service affordance remains recognizable and
platform-consistent.

## Match lobby design

A lobby is a contract, not a decorative waiting room. Show:

- game mode and rules;
- min/max players;
- invited/accepted/declined/matching states;
- player names and safe avatar treatment;
- privacy/social action;
- cancel/leave action;
- connectivity state;
- whether late join is allowed;
- whether the game can resume after backgrounding;
- the exact condition for Start.

For a party-code flow, support copy/paste/manual entry where the product uses it,
but keep Game Center invitations and system discovery available when appropriate.
Do not expose private invite payloads in logs or notifications.

## Real-time play

During play, keep transport detail subordinate:

- a small connection indicator can expand to a recovery sheet;
- pause on disconnect if state could diverge;
- make reconnect/resync explicit;
- preserve the last accepted local revision;
- show which actions are pending if input can queue;
- provide a safe forfeit/leave route;
- do not let an AI helper obscure the active turn or opponent identity.

A stateful real-time HUD can be:

    score/progress
      -> turn/phase
      -> connection status
      -> pause/recovery
      -> optional practice hint

Do not show a new glass capsule for every network event. Batch state and use
meaningful transitions.

## Turn-based play

Turn-based screens need to support multiple concurrent matches and a player who
returns later. Use a list/detail hierarchy:

- match identity and mode;
- participants and status;
- current participant;
- last turn date/timeout when useful;
- local turn action;
- waiting state;
- forfeit/quit route;
- stale/incompatible-version state;
- sync/update status;
- local cached snapshot versus current Game Center state.

If the match is not the player's turn, show read-only board state and a clear
return route. When a participant forfeits or a match ends, preserve the outcome
and explain what changed.

## Achievements and leaderboards

Make progression meaningful and restrained:

- show a local validated milestone first;
- label service submission separately;
- use the system Game Center surface for the full catalog when possible;
- let the result screen link to a leaderboard or achievement;
- do not use rank as the only measure of success;
- support no-score, private, offline, and service-error states;
- localize score units and achievement language;
- avoid manipulative prompts that interrupt play after every event.

A score or achievement card can use a glass review/result shell, but the card
should name the game mode, source run, pending/submitted state, and action. A
model-generated explanation is optional and must not imply service verification.

## On-device AI game assistants

Keep a practice helper inside a clear mode boundary:

| Mode | AI access | AI action |
| --- | --- | --- |
| Practice | Visible local state | Suggest legal move or explain rules |
| Accessibility assist | Visible state plus user-selected detail | Narrate/contrast/explain |
| Competitive | Product-defined visible state | Optional hint with explicit policy |
| Spectator/replay | Recorded public match state | Summarize or annotate |
| Hidden-information game | Only permitted visible state | No hidden opponent inference |
| Turn-based review | Current local snapshot | Proposal pending validation |
| Automation/agent | Explicit product mode | App-owned action validator and confirmation |

A glass suggestion panel should show “Suggestion,” source revision, and Apply/Use
or Dismiss. The model must not send a raw action to GameKit, mutate score,
select hidden information, or claim that its recommendation is fair or optimal.

## Social/privacy design

Use player display names and avatars carefully:

- allow the system Game Center UI to manage friend relationships;
- show only the minimum participant context needed for play;
- do not treat contact access as friend access;
- explain friend-list permission at the moment it adds value;
- provide mute/report/block/leave routes where the product needs them;
- do not put player IDs or private chat in screenshots, logs, widgets, or
  notifications;
- protect lock-screen previews for matches with sensitive content;
- delete or quarantine player-scoped local caches after account changes.

Avoid social pressure. A missed turn, low rank, or declined invitation should not
be phrased as a personal failure.

## Accessibility and alternate input

The menu and game state must remain understandable without color, sound, haptics,
or precise gestures.

Verify:

- VoiceOver says whose turn it is, the current score, match status, and available
  actions;
- the board has a meaningful accessible representation or alternate list/action
  route;
- dynamic game events do not repeatedly steal accessibility focus;
- Dynamic Type works in menus, overlays, result cards, and turn details;
- reduce motion disables camera shake, flashing, and fast reconnect animation;
- captions or text equivalents exist for important audio cues;
- haptics supplement, never replace, state;
- Voice Control and Switch Control can pause, resume, submit, quit, accept, and
  dismiss;
- keyboard/controller mappings expose the same essential actions;
- large touch targets remain clear of the Game Center access point;
- iPad, pointer, orientation, and size-class transitions preserve state.

For visually dense games, provide a reviewable state panel that names actors,
values, units, and actions instead of relying on animated sprites alone.

## Review checklist

- Is Game Center authenticated before service operations?
- Is the system-owned access point located in a menu/settings context?
- Is the game still useful when Game Center is unavailable?
- Are local gameplay state and Game Center service projections distinct?
- Are match start, reconnect, resync, forfeit, and end states explicit?
- Does real-time data have framing, sequence, validation, and recovery?
- Does turn-based data have versioning, current-turn, outcome, and stale handling?
- Are scores/achievements pending until service acknowledgement?
- Are friend/contact permissions distinct and explained?
- Is the AI constrained to visible state and an app-owned validator?
- Can the game pause, resume, and recover with VoiceOver and alternate input?
- Are physical two-device and release/service evidence available?

## Sources

- [Game Center](https://developer.apple.com/design/human-interface-guidelines/game-center)
- [Designing for games](https://developer.apple.com/design/human-interface-guidelines/designing-for-games/)
- [GameKit](https://developer.apple.com/documentation/gamekit/)
- [GKAccessPoint](https://developer.apple.com/documentation/gamekit/gkaccesspoint)
- [Authenticating a player](https://developer.apple.com/documentation/gamekit/authenticating-a-player)
- [Finding multiple players for a game](https://developer.apple.com/documentation/gamekit/finding-multiple-players-for-a-game)
- [Creating real-time games](https://developer.apple.com/documentation/gamekit/creating-real-time-games)
- [Creating turn-based games](https://developer.apple.com/documentation/gamekit/creating-turn-based-games)
- [Adding Liquid Glass to your app](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Performing accessibility testing for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)
