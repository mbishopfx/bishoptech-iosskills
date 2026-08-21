# SwiftUI Nearby Interaction and spatial-peer review design

Design a spatial screen as a trustworthy status instrument. The person should know which peer or accessory they selected, whether the token exchange and session are ready, which measurements are available, how fresh they are, and what action remains under their control.

This companion page pairs with [SwiftUI Nearby Interaction and spatial-peer review](../42-framework-deep-dives/96-swiftui-nearby-interaction-spatial-peer-review.md), [spatial proximity and nearby native surfaces](33-spatial-proximity-and-nearby-native-surfaces.md), and [Core Bluetooth and nearby-accessory review design](122-swiftui-core-bluetooth-and-nearby-accessory-review-design.md).

## Design contract

The primary surface should make these facts visible:

1. Peer or accessory discovery is separate from peer selection and trust.
2. The device and peer support the requested Nearby Interaction capability.
3. Temporary token exchange and transport state are complete or still pending.
4. Distance, direction, and freshness are individually available or unavailable.
5. Session suspension, removal, invalidation, and permission denial are recoverable states.
6. Any AI wording is a proposal derived from a named spatial snapshot.
7. Any physical or account action requires an explicit deterministic gate.

Use this hierarchy:

~~~text
transport-selected peer
  -> spatial session state
  -> capability and permission context
  -> distance/direction snapshot
  -> freshness and limitation language
  -> functional controls
  -> AI explanation or proposal
  -> explicit action review
~~~

Do not start with a giant glowing arrow. The arrow is a rendering of a measurement, not the source of identity or safety.

## State language

| State | Copy | Interaction |
| --- | --- | --- |
| Unsupported | This device or peer cannot provide the requested spatial feature. | Explain the minimum supported route. |
| Discovering | Looking for the selected peer. | Show cancel and transport context. |
| Candidate | Peer found; not spatially connected. | Let the person select or reject. |
| Exchanging | Preparing a temporary spatial session. | Disable spatial action until exchange completes. |
| Permission | Nearby Interaction access is needed. | Explain the feature before the system prompt. |
| Configured | Peer selected; waiting for ranging. | Show capability and retry. |
| Acquiring | Looking for a usable measurement. | Avoid a zero or straight-ahead placeholder. |
| Reported | Distance and direction updated just now. | Show source time and controls. |
| Partial | Distance available; direction unavailable. | Keep only supported guidance. |
| Stale | Last measurement received moments ago. | Offer refresh or stop. |
| Suspended | Spatial updates are paused. | Preserve context; do not imply live guidance. |
| Removed | The peer left the session or range. | Clear or mark the snapshot stale. |
| Invalidated | The session ended and must restart. | Show the reason and recovery. |

Use text and semantics with color, angle, motion, and depth. Never rely on green, a moving arrow, or Liquid Glass shine alone.

## Peer identity and transport

A transport list should show a candidate peer, not a verified spatial identity. Use a stable app-owned peer record for the selected session:

- transport peer ID;
- user-selected display name;
- token/session generation;
- capability summary;
- last exchange time;
- trust or authentication state if the product has one.

Do not display the raw discovery token as the peer’s name. A token is temporary and session-scoped. If the product needs identity, establish it through the transport’s pairing/authentication or an app-owned account relationship.

If using Multipeer Connectivity, keep the system invitation and app-owned peer selection visible. If using Network Framework or Core Bluetooth, show the corresponding connection state. The spatial card should not say “nearby” until the transport and Nearby Interaction session are both in a state that supports that claim.

## Measurement presentation

Distance and direction are optional values. Design three distinct visual states:

| Measurement | Presentation |
| --- | --- |
| Available | Numeric distance with units, direction wording, and source time. |
| Unavailable | “Distance unavailable” or “Direction unavailable,” not zero or center. |
| Stale | Last value plus age and a refresh/retry action. |

For direction:

- pair the arrow with a spoken phrase such as “to your left” when the product can derive one;
- show the coordinate frame or camera-assistance context when important;
- do not rotate a control around an unverified arrow;
- reduce animation when Reduce Motion is enabled;
- maintain a text path for VoiceOver and Voice Control.

For distance:

- use the user’s locale and unit preference;
- avoid false precision;
- label the value as relative distance;
- do not state that the peer is safely reachable, authorized, or physically unobstructed;
- show uncertainty or unavailable state when the framework cannot provide a value.

## Functional Liquid Glass

Use Liquid Glass for a small functional group:

- stop ranging;
- pause/resume updates;
- open peer details;
- retry token exchange;
- open review;
- open settings or capability details.

Keep the spatial measurement visualization in the content layer unless a small glass treatment materially improves grouping. Apple’s guidance says Liquid Glass works as a distinct functional layer for controls and navigation and should be used sparingly. Use standard materials or opaque surfaces for source, limitations, and review text when they provide better legibility.

A glass group should survive:

- light and dark camera or AR backgrounds;
- increased contrast;
- reduced transparency;
- large text;
- pointer and keyboard input;
- VoiceOver grouping;
- compact and regular widths.

Do not make the arrow itself a glass button unless the action is clear. A directional visualization is not an action.

## Camera assistance and AR

Camera Assistance can help improve direction or precision finding for stationary objects, but it introduces ARKit, camera privacy, orientation, and coaching state. The design should tell the person when camera access and motion are needed.

Use a coaching state such as:

~~~text
Camera assistance is helping refine direction.
Move the phone slowly from side to side.
~~~

If the camera is denied or unavailable, preserve a distance-only or non-camera route when supported. Do not show a frozen arrow as if it were current. The precision-finding sample’s device, OS, simulator, and two-device requirements must remain separate from a general Nearby Interaction screen.

## AI review surface

A local AI explanation can live in a sheet or inspector below the source measurement. Display:

| Element | Example |
| --- | --- |
| Source | Peer A, session generation 4, updated at 10:42:08 |
| Measurements | Distance 1.8 m; direction left; camera assistance active |
| Missing data | Vertical direction unavailable |
| Proposal | “Walk toward the left-side peer.” |
| Limitation | Relative ranging is not secure access control. |
| Actions | Edit, reject, refresh, or continue |

The proposal must not say “the authorized person is left,” “the door is safe to open,” or “the device is definitely there” unless those are independently established facts. Keep any action button behind deterministic validation and explicit confirmation.

## Accessibility and alternate input

Represent a spatial snapshot as an accessible group:

~~~text
Peer: Studio iPhone
Status: ranging
Distance: about two meters, updated one second ago
Direction: left and slightly above
Limitation: relative position; not secure identity
Actions: stop, refresh, review
~~~

Make peer selection, cancel, retry, stop, review, and confirmation reachable through VoiceOver, Voice Control, Switch Control, keyboard, and pointer. A person should not need to aim a finger at a moving arrow to find the peer or stop the session.

Use a stable ordering for multiple peers. Do not reorder accessible elements on every measurement update. Announce meaningful state changes without flooding VoiceOver with every ranging update.

## Background and interruption

If a product supports background ranging, design the system surface as part of the route. Show whether the app is using a Bluetooth-paired path or a Live Activity path, and show when updates are stale or paused. Do not use a foreground card in the background without adapting its freshness language.

When the scene backgrounds, the peer disconnects, permission changes, or the session is invalidated:

- mark the measurement stale or unavailable;
- stop automatic actions;
- preserve the selected peer record without retaining a false live state;
- offer restart or transport recovery;
- explain when camera assistance must be re-enabled.

## Privacy and trust

Do not log raw discovery tokens, peer names, or precise spatial traces by default. If diagnostics need them, use redaction, short retention, and explicit export behavior. Explain whether the transport uses the local network, Bluetooth, or another link.

The screen should not mimic an Apple security indicator. A proximity arrow is not a lock, passkey, or authorization badge. Use a separate trust and authentication surface when the product needs protected actions.

## Responsive layouts

On a phone, show the peer context and measurement first, with details in a sheet. On a regular-width iPad or Mac Catalyst window, use a split layout with peer/session context on the leading side and measurement/review on the trailing side. Keep the same state language.

Test:

- portrait and landscape;
- narrow split view and resizable window;
- large text and long peer names;
- multiple peers;
- direction unavailable;
- no camera assistance;
- reduced motion;
- increased contrast and reduced transparency;
- VoiceOver and keyboard focus;
- transport and session failure.

## Acceptance questions

1. Can a person tell the selected peer from a nearby candidate?
2. Can they tell when a token is exchanged versus when ranging is reporting?
3. Are distance, direction, unavailable, and stale distinct?
4. Does the UI avoid using proximity as security or identity?
5. Does Liquid Glass group actions without hiding the source or limitation?
6. Can the complete task work with VoiceOver and alternate input?
7. Does background or suspension change the freshness language?
8. Can an AI proposal be rejected, refreshed, or made stale before action?
9. Does the screen remain useful on unsupported devices and without camera assistance?

## Sources

- [Nearby Interaction](https://developer.apple.com/documentation/nearbyinteraction)
- [NISession](https://developer.apple.com/documentation/nearbyinteraction/nisession)
- [NISessionDelegate](https://developer.apple.com/documentation/nearbyinteraction/nisessiondelegate)
- [NINearbyObject](https://developer.apple.com/documentation/nearbyinteraction/ninearbyobject)
- [NINearbyPeerConfiguration](https://developer.apple.com/documentation/nearbyinteraction/ninearbypeerconfiguration)
- [NINearbyAccessoryConfiguration](https://developer.apple.com/documentation/nearbyinteraction/ninearbyaccessoryconfiguration)
- [Initiating and maintaining a session](https://developer.apple.com/documentation/nearbyinteraction/initiating-and-maintaining-a-session)
- [Discovering peers with Multipeer Connectivity](https://developer.apple.com/documentation/nearbyinteraction/discovering-peers-with-multipeer-connectivity)
- [Finding devices with precision](https://developer.apple.com/documentation/nearbyinteraction/finding-devices-with-precision)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
