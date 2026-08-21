# GameKit and Game Center multiplayer proof matrix

## Purpose

Use this matrix to prove Game Center claims at the boundary they make. A local
game loop, a simulated player, or a found match is not proof of a complete
two-device service experience.

## Evidence levels

| Level | Evidence | Proves | Does not prove |
| --- | --- | --- | --- |
| L0 | Apple GameKit/HIG and App Store Connect configuration review | The selected route, design, IDs, and documented boundaries are understood | Target signing, player account, service delivery, or gameplay correctness |
| L1 | Named-target compile and signed archive inspection | Imports, availability, target membership, capability, and entitlement resolve | Real account, match connection, system overlay, or physical input |
| L2 | Deterministic fixtures/tests | Reducer, action codec, legal moves, progression, AI proposal, and state errors | Game Center service, radio/network, invitation, or account behavior |
| L3 | Simulator/XCUI run with test seams | Menu/lobby/result/accessibility layout and scripted app states | Real Game Center account, two-device multiplayer, physical controller, or service delivery |
| L4 | Two physical devices/accounts | Authentication, invitation, real-time/turn-based exchange, reconnect, and system-surface behavior | Every OS/device/service region or release configuration |
| L5 | Signed Release/TestFlight/service environment | Shipped Game Center capability, App Store Connect IDs, localization, and release behavior | Universal reliability, fair play, or every player/network condition |

Attach the evidence level to each claim. Do not promote a fixture result into a
physical or production claim.

## Configuration and service rows

| ID | Claim | Test | Evidence | Acceptance |
| --- | --- | --- | --- | --- |
| CFG-01 | Game Center is enabled for the intended target | Inspect target capability and signed archive entitlement | Target settings plus exported entitlement | Intended app target contains the required Game Center entitlement |
| CFG-02 | App Store Connect IDs match the build | Compare achievement/leaderboard/activity IDs with configured records | Redacted configuration table and build version | No staging/test ID is in the release target |
| CFG-03 | Supported platforms are intentional | Build each declared destination and inspect availability | SDK/deployment matrix | Unsupported platform has a visible fallback or is not declared |
| CFG-04 | Friend list permission is truthful | Trigger the selected friend route with permission allowed/denied | Info.plist and physical prompt screenshots | Usage reason describes the actual feature |
| CFG-05 | Service environment is known | Run development/sandbox/release account matrix | Account/environment record | Test result names the exact environment |
| CFG-06 | Game state version is explicit | Decode old/current/future fixtures | Schema/version tests | Unsupported data is rejected/read-only, not guessed |

## Authentication and system-surface rows

| ID | Claim | Test | Evidence | Acceptance |
| --- | --- | --- | --- | --- |
| AUTH-01 | Local player authentication is initialized | Cold launch signed-in device | Handler state trace and UI result | Service operations start only after current authenticated state |
| AUTH-02 | System authentication UI presents correctly | Fresh account/permission path | Physical system prompt and dismissal run | App presents provided controller from the correct context |
| AUTH-03 | Decline/restriction is safe | Decline, sign out, restricted account, service unavailable | UI state and local play continuation | No fake success, loop, or destructive cache mix |
| AUTH-04 | Account change is isolated | Switch/sign out/change Game Center player where supported | Old/new player cache trace | Old player pending writes cannot attach to new player |
| AUTH-05 | Access point is native and placed well | Open from main menu/settings, expand/dismiss, rotate/resize | Physical host screenshots/recording | No overlap with critical controls; game pauses/quietly persists |
| AUTH-06 | Overlay return is correct | Open Game Center overlay during pause/menu and return | Navigation/state trace | Same game state returns; no duplicate presentation |
| AUTH-07 | Custom links are accurate | Open achievement/leaderboard/profile route | UI copy/artwork review | Apple terminology/artwork used correctly; custom UI is not fake system UI |

## Progression rows

| ID | Claim | Test | Evidence | Acceptance |
| --- | --- | --- | --- | --- |
| PROG-01 | Achievement milestone is deterministic | Replay exact run and alternate invalid run | Fixture/reducer trace | Only validated milestone creates pending report |
| PROG-02 | Achievement percentage is valid | 0, intermediate, 100, duplicate, decrease fixtures | Report payload and error mapping | Integer range/policy is enforced |
| PROG-03 | Achievement retry is safe | Timeout after report, offline, account change | Pending queue and dedupe trace | Duplicate report does not duplicate domain milestone |
| PROG-04 | Leaderboard score is validated | Impossible score, wrong mode, valid score | Run ID/rule/version trace | Only accepted domain result is submitted |
| PROG-05 | Leaderboard scope is clear | Friend/global, daily/all-time, range/no-score | UI and loaded-entry trace | Rank is labeled with scope/time and stale/error state |
| PROG-06 | Recurring occurrence is correct | Before, during, and after occurrence rollover | Occurrence ID/date and UI | Score is not shown under the wrong period |
| PROG-07 | Service projection is separate | Local result with service unavailable/accepted | State machine screenshot | Local best, pending, accepted, and rank unknown are distinct |

## Friends, invites, activities, and challenges

| ID | Claim | Test | Evidence | Acceptance |
| --- | --- | --- | --- | --- |
| SOC-01 | Friend access is least privilege | Not determined, denied, authorized | Permission prompt/state | Game does not inspect friends without authorized route |
| SOC-02 | Friend/contact/player identity is distinct | Same display name, changed avatar, nonfriend opponent | Typed identity fixture | Stable player ID and relationship scope are separate |
| SOC-03 | Invitation is handled after cold launch | Send/accept invite while app foreground/background/terminated | Two-device launch/deep-link trace | Invite resolves to current compatible route |
| SOC-04 | Declined/expired invite is safe | Decline, timeout, removed match | UI/error trace | No phantom lobby or auto-join |
| SOC-05 | Activity/challenge link is validated | Valid, stale, wrong game/version, unauthorized | Destination resolver tests | Unsupported links fall back without mutation |
| SOC-06 | Social content is redacted | Logs/notifications/widgets/evidence review | Redacted artifact | Private chat/player IDs are not exposed |

## Real-time multiplayer rows

| ID | Claim | Test | Evidence | Acceptance |
| --- | --- | --- | --- | --- |
| RT-01 | Matchmaker request is correct | Min/max, recipients, automatch/rules fixtures | Request/config record | Player-count/mode rules match product |
| RT-02 | Match UI lifecycle is correct | Present, cancel, find, decline, error | Physical system UI trace | Delegate dismisses exactly once and app state returns correctly |
| RT-03 | Connection state is explicit | Connecting, connected, player joins/leaves, failed | GKMatch delegate trace | Gameplay starts only after required players are ready |
| RT-04 | Protocol version is negotiated | Same version, older, newer, wrong mode | Handshake fixtures | Incompatible peers are rejected/read-only |
| RT-05 | Framing and limits hold | Split/coalesced/malformed/oversized messages | Codec tests and memory result | One callback is not assumed to be one action |
| RT-06 | Ordering/dedupe works | Out-of-order, duplicate, delayed, replayed action | Sequence/revision trace | Invalid or duplicate state cannot mutate the reducer |
| RT-07 | Reliable/unreliable policy is correct | Drop high-frequency versus critical data | Data-mode fixture and resync | Critical state has acknowledgement/snapshot recovery |
| RT-08 | Disconnect/reconnect is honest | Wi-Fi loss, app background, process interruption | Two-device recovery trace | Game pauses/resyncs/ends according to explicit policy |
| RT-09 | Player identity is checked | Wrong sender/slot, stale match, spoofed payload fixture | Rejection trace | Sender is not trusted from payload alone |
| RT-10 | Competitive authority is appropriate | Modified client/impossible score simulation | Server/validation evidence | Client-only claims are not sold as anti-cheat proof |

## Turn-based rows

| ID | Claim | Test | Evidence | Acceptance |
| --- | --- | --- | --- | --- |
| TB-01 | Match creation/acceptance works | Start, invite, automatch, accept/decline | Two-account physical trace | Match enters the correct participant state |
| TB-02 | Current participant is enforced | Local turn and waiting turn | UI/reducer tests | Only the current player can commit a move |
| TB-03 | State data is versioned | Current/old/corrupt/oversized match data | Decoder fixtures | Bad data becomes repair/read-only, not guessed |
| TB-04 | Legal moves are deterministic | Valid/invalid/repeated/stale action fixtures | Reducer output | Invalid move never reaches endTurn |
| TB-05 | End turn is correct | Next participants, timeout, current data | Physical event and callback trace | One turn transition per accepted move |
| TB-06 | Quit/forfeit/end outcomes are correct | In-turn, out-of-turn, participant removal, finish | Participant/outcome trace | Every finished participant has an explicit outcome |
| TB-07 | Cold-launch turn events work | Receive turn while app is background/terminated | Relaunch/event trace | Match opens at the current compatible state |
| TB-08 | Multiple matches remain distinct | Two concurrent matches and out-of-order events | Match-ID state trace | Events never cross-contaminate matches |

## AI and game-state rows

| ID | Claim | Test | Evidence | Acceptance |
| --- | --- | --- | --- | --- |
| AI-01 | Model sees only allowed state | Hidden-info/visible-info fixtures | Input-scope trace | No hidden opponent data reaches the helper |
| AI-02 | Proposal is tied to revision | Change state while inference runs | Source revision rejection | Stale suggestion cannot apply |
| AI-03 | Proposed move is legal | Malformed/illegal/duplicate proposals | Validator test | Model output is discarded or reviewed |
| AI-04 | Competitive policy is explicit | Practice/competitive/accessibility modes | Mode policy and UI | Model cannot silently automate ranked play |
| AI-05 | Commit uses normal action path | Approve/dismiss/double tap/intent retry | One action/revision trace | Model has no direct GameKit side-effect authority |
| AI-06 | Fairness/anti-cheat claims are bounded | Client manipulation simulation | Server/validation review | Local inference is not presented as anti-cheat |
| AI-07 | AI privacy holds | Prompt/log/cache/evidence review | Redaction and retention record | Player/private match data follows policy |

## Accessibility and input rows

| ID | Claim | Test | Evidence | Acceptance |
| --- | --- | --- | --- | --- |
| A11Y-01 | Menu and HUD are semantic | VoiceOver traversal | Accessibility tree/recording | Turn, score, status, and action are announced |
| A11Y-02 | Board has an alternate representation | VoiceOver/keyboard/Voice Control route | Accessible state panel or action list | Essential game state is not sprite-only |
| A11Y-03 | Large text/localization works | Largest Dynamic Type, long names, RTL | Device screenshots and UI tests | No clipped controls or hidden turn state |
| A11Y-04 | Reduced effects work | Reduce Motion/transparency/increased contrast | Physical device settings run | Meaning survives without animation/material |
| A11Y-05 | Alternate input works | Switch Control, Voice Control, keyboard/controller | Physical device evidence | Pause, resume, quit, accept, and recovery are reachable |
| A11Y-06 | Game Center overlay does not break recovery | Overlay/lock/resume and focus | Device trace | Critical app state remains recoverable |

## Release and live-service rows

| ID | Claim | Test | Evidence | Acceptance |
| --- | --- | --- | --- | --- |
| REL-01 | Release entitlement is correct | Inspect signed Release/TestFlight archive | Exported entitlements | Game Center is present only on intended targets |
| REL-02 | Service IDs/localization are release-ready | TestFlight/release build against configured records | App Store Connect/build matrix | No missing labels, wrong IDs, or staging artifacts |
| REL-03 | Two-account system route works | Physical release/TestFlight devices | Invitation, overlay, scoreboard, turn trace | Service behavior is proven on real hosts |
| REL-04 | Failure copy is honest | Offline/restriction/service error runs | UI review | No claim of rank/achievement/turn acceptance without evidence |
| REL-05 | Privacy metadata is signed | Info.plist/privacy review | Archive inspection | Friend usage and declared data routes match implementation |
| REL-06 | Performance remains acceptable | Device frame/hitch/memory/power run | XCTest/MetricKit/signpost artifacts | Multiplayer/UI/model helper does not break gameplay budget |

## Test matrix

Run the selected route with:

- signed-in, signed-out, restricted, declined, and account-change states;
- fresh capability/service configuration and stale/mismatched identifiers;
- one device local play;
- two physical devices on the same and different networks where applicable;
- invitation foreground/background/terminated;
- matchmaker cancel/decline/timeout;
- player join/leave/disconnect/reconnect;
- malformed, out-of-order, duplicate, delayed, and oversized payloads;
- turn timeout/forfeit/rematch/multiple concurrent matches;
- offline score/achievement report and later retry;
- leaderboard occurrence rollover/no score/private scope;
- Game Center overlay with pause/resume;
- largest Dynamic Type, VoiceOver, Voice Control, Switch Control, keyboard,
  controller, reduce motion/transparency, increased contrast, and RTL;
- model unavailable, stale, illegal, hidden-state, and approved proposal cases;
- Release/TestFlight archive and App Store Connect service environment.

## Stop conditions

Stop and fix when:

- the app invents a custom sign-in UI for Game Center;
- a display name or nickname is treated as identity;
- a found match is treated as connected/ready without protocol handshake;
- a peer payload directly mutates score or entitlement;
- a client score is described as anti-cheat proof;
- a partial or pending service report is shown as accepted;
- a turn event is applied without match ID/revision/current-participant validation;
- Game Center overlay is imitated or covered with app-owned glass;
- friend access is inferred from contacts or an identifier;
- an AI suggestion can directly send GameKit actions;
- simulator/local fixture output is described as two-device/release proof.

## Sources

- [GameKit](https://developer.apple.com/documentation/gamekit/)
- [Game Center entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.game-center)
- [Authenticating a player](https://developer.apple.com/documentation/gamekit/authenticating-a-player)
- [GKLocalPlayer](https://developer.apple.com/documentation/gamekit/gklocalplayer)
- [GKAccessPoint](https://developer.apple.com/documentation/gamekit/gkaccesspoint)
- [GKAchievement](https://developer.apple.com/documentation/gamekit/gkachievement)
- [GKLeaderboard](https://developer.apple.com/documentation/gamekit/gkleaderboard)
- [GKMatch](https://developer.apple.com/documentation/gamekit/gkmatch)
- [GKMatchDelegate](https://developer.apple.com/documentation/gamekit/gkmatchdelegate)
- [GKTurnBasedMatch](https://developer.apple.com/documentation/gamekit/gkturnbasedmatch)
- [GKTurnBasedParticipant](https://developer.apple.com/documentation/gamekit/gkturnbasedparticipant)
- [GKTurnBasedEventListener](https://developer.apple.com/documentation/gamekit/gkturnbasedeventlistener)
- [Finding multiple players for a game](https://developer.apple.com/documentation/gamekit/finding-multiple-players-for-a-game)
- [Creating real-time games](https://developer.apple.com/documentation/gamekit/creating-real-time-games)
- [Creating turn-based games](https://developer.apple.com/documentation/gamekit/creating-turn-based-games)
- [Game Center](https://developer.apple.com/design/human-interface-guidelines/game-center)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Performing accessibility testing for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
