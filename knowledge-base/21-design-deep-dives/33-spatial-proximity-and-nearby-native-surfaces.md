# Spatial proximity and nearby native surfaces

A nearby interaction should feel like a natural extension of a task: bring two devices together to share, point toward an accessory to find it, or move closer to refine a selection. It should not feel like the app is asking the person to solve a sensor calibration problem without explaining why.

## Design the physical task first

Write the physical action in ordinary language:

- “Bring the two phones together to share this note.”
- “Point toward the selected accessory.”
- “Move closer until the target is centered.”
- “Choose the nearby device you want before connecting.”

Then define:

1. What the app knows before proximity begins.
2. What the person explicitly selects or accepts.
3. What direction/distance adds to the task.
4. What data transport carries.
5. What happens if direction is unavailable but distance remains.
6. What happens when the device is blocked, rotated, or out of range.

Do not start with an arrow, radar circle, or floating glass orb. Start with the outcome.

## Discovery is not identity

The design must distinguish:

| State | User-facing meaning |
| --- | --- |
| Candidate discovered | A nearby service/device matches the advertised route. |
| Candidate selected | The person chose this candidate for the current task. |
| Peer accepted | The other app/device agreed to the session invitation. |
| Session authenticated | The product’s handshake and trust policy passed. |
| NI running | The current session can receive proximity updates. |
| Data ready | The transport protocol is connected and authorized for this task. |
| Side effect confirmed | The person approved the actual transfer/control action. |

Never label a candidate “your friend,” “your accessory,” or “safe” from a display name or proximity alone. Nearby Interaction uses session-lifetime discovery tokens that preserve privacy; they are not permanent person identities.

## Continuous feedback

Nearby Interaction HIG guidance recommends feedback that changes with proximity and combines visual, audible, and haptic cues. Use a predictable progression:

~~~text
candidate selected -> searching
                  -> direction available: point/align
                  -> distance improves: refine
                  -> target close: confirm
                  -> transport ready: show action
                  -> complete: summarize and stop
~~~

The screen should remain usable when a person stops moving. Provide a stable text state, current target, and manual action. If direction disappears but distance remains, say so or switch to a distance-only treatment. If the interaction pauses, freeze the last value with a timestamp rather than implying live guidance.

## Orientation, field of view, and obstacles

Design the onboarding around supported device behavior:

- Encourage a supported holding orientation with implicit visual guidance.
- Keep the target indicator in the device’s directional field of view.
- Explain that another person, animal, or large object can affect accuracy.
- Provide a “move to a clearer position” instruction.
- Avoid making the person walk or reach unnecessarily.
- Test crowded rooms, reflective surfaces, cases, and natural hand movement where relevant.

A directional arrow is not a guarantee. When only distance is available, use a centered/neutral visual that does not imply direction. Do not hide loss of direction behind a continuously animated glass effect.

## Liquid Glass and spatial guidance

Use Liquid Glass to group controls such as target selection, pause, cancel, and confirm. Keep the physical guidance itself legible:

- content and target label should remain readable over glass;
- a glass control should not move so much that it is hard to activate;
- use a bounded morph between searching, aligning, and confirming states;
- pair tint/blur with text and shape;
- respect Reduce Motion and reduced transparency;
- keep permission, system pairing, and extension UI system-owned;
- avoid glass decorations that look like an Apple system icon or private Apple surface.

An Apple-like spatial surface is quiet, responsive, and explicit about uncertainty. It does not rely on a proprietary-looking radar screen.

## Accessibility and alternate input

Spatial interaction must have an equivalent non-spatial route:

- select a candidate from a list;
- use a “continue without direction” action when safe;
- provide exact distance/status text for VoiceOver;
- announce material state transitions, not every sample;
- offer audio and haptic cues only as supplements;
- preserve touch, keyboard, pointer, Switch Control, and Voice Control actions;
- let a person pause, cancel, or retry.

If a user cannot or does not want to move the device, the core outcome should remain possible where the product’s safety/trust model allows. Use direct gestures sparingly and keep controls physically comfortable.

## Peer selection and trust UI

The invitation surface should show:

- peer/accessory display name supplied by the app;
- app/product identity;
- purpose of the connection;
- data or action to be shared;
- session expiration/close behavior;
- accept, reject, and cancel.

Do not present discovery metadata as verified identity. After acceptance, show the protocol/authentication result and the exact data action before executing it.

## AI as a nearby assistant

AI can help with:

- ranking candidates the person already selected or explicitly allowed;
- explaining why a target is unavailable;
- choosing between a distance-only and direction-aware layout;
- summarizing a transfer or proximity session;
- suggesting a next physical step from current status.

Keep the prompt local and bounded. Use “nearby candidate 2, direction unavailable, transport connected” rather than raw identity assumptions. Let the person inspect and confirm the target. Never use AI to identify an unknown person, infer consent, or trigger an unreviewed transfer.

## Notification and handoff behavior

Nearby flows often span two devices or leave the foreground:

- preserve a clear local session state;
- show when a transport is closed or must be reestablished;
- do not rely on a background MC session that the framework disconnects;
- use a system surface only if it genuinely represents current state;
- avoid notification content that exposes a private nearby target;
- make a transfer idempotent and inspectable after reconnect.

## Review checklist

- Is the physical action clear before the session begins?
- Are discovery, selection, trust, transport, NI, and side effect separate?
- Does the UI represent direction loss, distance-only, obstruction, and interruption honestly?
- Is there a non-spatial/manual path?
- Are feedback types coordinated and accessible?
- Does Liquid Glass support the task without masking uncertainty?
- Is the peer/accessory identity verified by the product protocol rather than proximity?
- Does AI remain a bounded proposal layer?
- Does the flow stop and release tokens, sensors, transports, and haptics?

## Sources

- [Nearby interactions HIG](https://developer.apple.com/design/human-interface-guidelines/nearby-interactions/)
- [Accessibility HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Nearby Interaction](https://developer.apple.com/documentation/nearbyinteraction)
- [NISession](https://developer.apple.com/documentation/nearbyinteraction/nisession)
- [NINearbyPeerConfiguration](https://developer.apple.com/documentation/nearbyinteraction/ninearbypeerconfiguration)
- [NINearbyAccessoryConfiguration](https://developer.apple.com/documentation/nearbyinteraction/ninearbyaccessoryconfiguration)
- [Initiating and maintaining a session](https://developer.apple.com/documentation/nearbyinteraction/initiating-and-maintaining-a-session)
- [Network](https://developer.apple.com/documentation/network)
- [NWBrowser](https://developer.apple.com/documentation/network/nwbrowser)
- [NWConnection](https://developer.apple.com/documentation/network/nwconnection)
- [Multipeer Connectivity](https://developer.apple.com/documentation/multipeerconnectivity)
- [MCSession](https://developer.apple.com/documentation/multipeerconnectivity/mcsession)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
