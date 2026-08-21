# SwiftUI Nearby Interaction and spatial-peer review proof matrix

Use this matrix to distinguish a token exchange, session callback, and UI preview from proof of physical ranging, peer identity, safety, background delivery, accessibility, or release behavior.

Pairs with [SwiftUI Nearby Interaction and spatial-peer review](../42-framework-deep-dives/96-swiftui-nearby-interaction-spatial-peer-review.md), [the spatial-peer route](../50-capability-recipes/127-swiftui-nearby-interaction-spatial-peer-review-route.md), and [Core Bluetooth nearby-accessory proof](119-swiftui-core-bluetooth-and-nearby-accessory-review-proof-matrix.md).

## Evidence levels

| Level | Proves | Does not prove |
| --- | --- | --- |
| Source | The documented Nearby Interaction/transport contract was read. | Target configuration or physical behavior. |
| Static audit | Usage descriptions, capabilities, transport settings, and platform matrix exist. | Permission, token exchange, UWB, or background delivery. |
| Compile | Selected symbols and availability checks compile. | Supported hardware, spatial accuracy, accessibility, or system delivery. |
| Fixture | State, token matching, optional-value handling, and proposal rejection. | UWB distance, direction, camera assistance, or physical ergonomics. |
| Simulator | Some UI and controlled transport behavior. | Physical UWB, direction, AR camera assistance, thermal, or multi-device proof. |
| Physical two-device | Token exchange, ranging callbacks, peer removal, orientation, and input. | Every device/OS or App Store behavior. |
| Archive/TestFlight | Signed target and capability/privacy configuration installs. | Production delivery, universal support, or model truth. |
| Production | Released route works for measured users/devices. | Future hardware/OS behavior without regression evidence. |

## Gate matrix

| Gate | Evidence | Pass condition | Rejection |
| --- | --- | --- | --- |
| N0 target | Inspect signed target | NSNearbyInteractionUsageDescription and intended capability are present | Source text only |
| N1 platform | Device/support matrix | Direction/distance/accessory mode matches the selected target | One Boolean for every platform |
| N2 transport | Discovery and selection | User-selected peer has transport identity and cancellation | Nearby candidate treated as identity |
| N3 token exchange | Secure encode/decode and peer match | Temporary token exchange is tied to selected transport peer | Token stored as account identity |
| N4 permission | Physical allow/deny/Settings recovery | userDidNotAllow has truthful recovery | Permission inferred from compile |
| N5 session | Start, suspend, resume, invalidate | Explicit state machine and safe cleanup | Running flag treated as current ranging |
| N6 measurement | Physical distance/direction updates | Optional values, timestamps, and token matching are preserved | Nil rendered as zero or straight ahead |
| N7 capability | Local and peer deviceCapabilities | Unsupported mode is rejected before run | Peer incompatibility discovered after action |
| N8 camera assistance | Physical camera/motion route | Coaching, camera privacy, orientation, and AR state are explicit | Arrow preview treated as precision proof |
| N9 accessory | Real accessory data link | Configuration data, pairing identity, and token are correlated | Bluetooth connection treated as spatial identity |
| N10 background | Lock/background/relaunch | Claimed BLE or Live Activity path remains truthful and fresh | Capability checkbox alone |
| N11 AI | Proposal fixtures | Source age/capability/limitation and explicit apply gate | Ranging controls an action automatically |
| N12 accessibility | VoiceOver and alternate-input tasks | Peer selection, status, stop, review, and recovery complete | Accessibility identifier only |
| N13 privacy | Logs, retention, export, transport review | Tokens and spatial traces are minimized/redacted | Raw tokens in diagnostics |
| N14 physical energy | Sustained two-device run | Cadence, thermal, power, and stale behavior are acceptable | Simulator or newest device only |
| N15 release | Archive/TestFlight/metadata | Target, capabilities, privacy, and claims match evidence | Debug run or upload alone |

## Fixture matrix

| Fixture | Expected result |
| --- | --- |
| Nearby Interaction unsupported | Feature-specific unavailable state |
| Peer lacks direction | Distance-only state; no invented arrow |
| Peer lacks precise distance | Supported lower-fidelity route or rejection |
| Token exchange delayed | Exchanging state with cancel/retry |
| Token from wrong transport peer | Reject and require selection |
| userDidNotAllow | Settings/recovery route; no ranging claim |
| incompatiblePeerDevice | Capability-specific rejection |
| No nearby object update | Acquiring or stale state, not zero |
| Peer removed | Snapshot stale/cleared and actions stopped |
| Session suspended | Pause state and no automatic commit |
| Session invalidated | Error reason, cleanup, and new-session path |
| Two peer tokens | Match by token, not array order |
| Direction nil | Text says unavailable |
| Distance nil | Text says unavailable |
| Stale callback after stop | Discard using session generation |
| Camera assistance unavailable | Distance-only or non-camera fallback |
| Background without supported path | Ranging pause is explained |
| Live Activity stale | System surface no longer says current |
| AI proposal with stale source | Reject and require refresh |
| Reduce Motion | No essential state depends on arrow animation |
| Dynamic Type/VoiceOver | Full task remains reachable |
| Peer leaves range | Recovery and no physical action |

## Provenance record

For each spatial snapshot, record:

- app-owned peer identity;
- transport identity;
- session generation;
- discovery token association without exposing the raw token;
- local and peer capability summary;
- configuration type and revision;
- distance and direction optionality;
- receipt time and source age;
- camera-assistance/AR state when used;
- transport connection state;
- session lifecycle state;
- whether the result is current, stale, unavailable, or a proposal.

A screenshot of an arrow is not reproducible spatial evidence without the device pair, target build, capability, transport, session, and source record.

## Accessibility task record

Run the task with:

1. discover or select a peer;
2. understand token exchange and permission state;
3. hear whether distance and direction are available;
4. find the peer through semantic navigation;
5. stop or retry the session;
6. review limitations and any AI proposal;
7. reject, refresh, or explicitly apply the action;
8. recover from suspension, removal, invalidation, and unsupported state.

Repeat with VoiceOver, Voice Control, Switch Control, keyboard/pointer, Dynamic Type, increased contrast, reduced transparency, and Reduce Motion. Test compact and regular-width layouts.

## Physical multi-device record

Record:

| Field | Evidence |
| --- | --- |
| Devices | Model, OS, UWB capability, and orientation |
| Build | Configuration, signing, version, and target |
| Transport | Technology, privacy prompts, peer identities, and framing |
| Token exchange | Time, success/failure, secure decode, selected peer |
| Nearby session | Start, update, suspension, removal, invalidation |
| Measurements | Distance/direction availability and source age |
| Environment | Line of sight, obstructions, motion, and room |
| Camera assistance | Permission, AR coaching, and orientation if used |
| Accessibility | Complete task under alternate settings |
| Energy | Duration, thermal state, and update cadence |
| Background | Lock, background, Live Activity, and relaunch if claimed |

Do not call a device pair “accurate” from one screenshot. Record the conditions and product claim being tested.

## Release acceptance

The route is release-ready only when the claim is no stronger than the evidence:

- relative ranging is described as relative ranging;
- secure access and identity use independent authorization;
- unsupported, denied, stale, suspended, and invalidated states are safe;
- spatial AI remains optional, sourced, and reviewable;
- physical multi-device behavior is tested on supported release hardware;
- background/system surfaces have their own proof;
- accessibility and reduced-effects tasks complete;
- the signed artifact contains the correct privacy/capability configuration;
- marketing and App Store copy avoid guaranteed distance, identity, safety, or security claims.

## Sources

- [Nearby Interaction](https://developer.apple.com/documentation/nearbyinteraction)
- [Initiating and maintaining a session](https://developer.apple.com/documentation/nearbyinteraction/initiating-and-maintaining-a-session)
- [NISession](https://developer.apple.com/documentation/nearbyinteraction/nisession)
- [NISessionDelegate](https://developer.apple.com/documentation/nearbyinteraction/nisessiondelegate)
- [NIDiscoveryToken](https://developer.apple.com/documentation/nearbyinteraction/nidiscoverytoken)
- [NINearbyPeerConfiguration](https://developer.apple.com/documentation/nearbyinteraction/ninearbypeerconfiguration)
- [NINearbyAccessoryConfiguration](https://developer.apple.com/documentation/nearbyinteraction/ninearbyaccessoryconfiguration)
- [NINearbyObject](https://developer.apple.com/documentation/nearbyinteraction/ninearbyobject)
- [Nearby Interaction errors](https://developer.apple.com/documentation/nearbyinteraction/nierror)
- [userDidNotAllow](https://developer.apple.com/documentation/nearbyinteraction/nierror/userdidnotallow)
- [Discovering peers with Multipeer Connectivity](https://developer.apple.com/documentation/nearbyinteraction/discovering-peers-with-multipeer-connectivity)
- [Finding devices with precision](https://developer.apple.com/documentation/nearbyinteraction/finding-devices-with-precision)
- [NSNearbyInteractionUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsnearbyinteractionusagedescription)
- [Multipeer Connectivity](https://developer.apple.com/documentation/multipeerconnectivity)
- [Network Framework](https://developer.apple.com/documentation/network)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
