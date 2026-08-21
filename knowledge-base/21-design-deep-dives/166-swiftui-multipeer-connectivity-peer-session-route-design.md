# SwiftUI MultipeerConnectivity peer-session design

An Apple-native nearby-session surface should feel calm, explicit, and
reversible. The design goal is not to copy Apple’s peer UI or pretend that
nearby discovery is identity. It is to make the transport phase, consent
boundary, and recovery path legible while using the system controls and Liquid
Glass hierarchy that belong to the platform.

This route is for an existing MultipeerConnectivity integration. For a new
peer transport, use the [Network Framework migration route](../42-framework-deep-dives/138-swiftui-multipeer-connectivity-peer-session-route.md#migration-to-network-framework)
and keep the same design state model.

## Design contract

~~~text
user goal
  -> why nearby access is needed
  -> candidate discovery
  -> human selection
  -> invitation review
  -> connection proof
  -> transfer/realtime action
  -> receipt and recovery
~~~

Every screen should answer the current question:

| Phase | Person needs to know | Primary action |
| --- | --- | --- |
| Idle | What can I do nearby? | Start discovery |
| Permission pending | Why does this app need the local network? | Allow or open Settings |
| Browsing | Which app peers are visible? | Select a candidate |
| Invitation pending | What will joining share or enable? | Accept, reject, or cancel |
| Connecting | Is this the selected peer or a stale candidate? | Wait or cancel |
| Connected | Is the session authenticated and ready? | Start the bounded action |
| Transferring | What is moving, how much remains, and can I stop it? | Pause/cancel/retry |
| Disconnected | What was committed and what is safe to resume? | Reconnect or keep local copy |
| Error | What can I repair without losing work? | Retry, permissions, or fallback |

Do not collapse all phases into a single spinner. A spinner cannot explain
whether a user is waiting for permission, discovery, invitation acceptance,
radio connection, or remote application.

## Native composition

Use a small number of semantically strong regions:

~~~text
NavigationStack
  ├─ phase header: icon + text + accessible value
  ├─ nearby candidates: List with selection/action rows
  ├─ selected peer: identity, capability summary, trust status
  ├─ transfer/realtime detail: ProgressView, event log, cancel
  └─ recovery: permission, retry, fallback, and help
~~~

Use List, Section, Button, Label, ProgressView, ToolbarItem, sheet, alert,
confirmationDialog, and navigation destinations before inventing a custom
control. A standard control gives the system semantic behavior, keyboard and
VoiceOver support, focus management, and predictable adaptation.

The selected peer row should distinguish:

- display name: what the remote app advertises;
- service/protocol: what the app is offering;
- trust state: what the app has verified or what the person has approved;
- connection state: what MCSession currently reports;
- content/action state: what the app has actually applied.

Never title a row “Trusted” because it is nearby. Use “Not verified,” “Selected
for this transfer,” or a product-specific authenticated state with evidence.

## Liquid Glass hierarchy

Liquid Glass should support the action hierarchy rather than become the
content. Apply a small glass group to:

- the current session phase and primary action;
- a compact transfer command group with cancel/retry;
- a review sheet’s explicit accept/reject controls.

Keep peer identity, long discovery metadata, progress details, and error copy
on ordinary readable surfaces. Multiple nearby peer rows should not each carry
independent glass effects that make the list look like a floating control deck.

The visual layers are:

~~~text
content layer       peer names, protocol labels, transfer facts
functional layer    select, invite, accept, send, cancel, retry
system layer        local-network prompt, share/system handoff, settings
feedback layer      progress, status, error, stale/reconnect explanation
~~~

Place the functional glass group in a safe-area-aware toolbar or bottom action
region. Do not place a primary peer-selection control behind a translucent
overlay. A glass effect must retain contrast, hit-target clarity, and a
non-glass fallback when transparency is reduced or the selected SDK/device does
not support the effect.

Use restrained motion for:

- a candidate entering or leaving the list;
- an invitation moving from pending to accepted/rejected;
- a transfer progress change;
- an explicit peer row morphing into a selected inspector.

Respect Reduce Motion. A state change must remain understandable when all
animation is disabled.

## Screen patterns

### Discovery browser

The discovery screen has a concise explanation above the candidate list. Show
the local device’s service role and a “Stop looking” action. Each candidate row
contains a short display name, coarse capability summary, and a semantic
selection button. Use a refresh or restart action only when the framework state
actually allows it; do not imply that a refresh can repair denied local-network
permission.

Empty states should distinguish:

- no permission yet;
- permission denied;
- browsing active but no peer found;
- browser failed to start;
- nearby peer found but filtered by protocol/version.

### Invitation review sheet

The invitation sheet should show who is inviting, which protocol/version is
requesting the session, what information will be shared, and an expiry or
cancel state. Keep Accept and Decline separate and explicit. Do not hide an
invitation in a notification or auto-accept because the service type matched.

Context bytes are untrusted. If they produce a user-facing title, show a safe
fallback when decoding fails and do not render unbounded remote text as rich
markup.

### Session inspector

Once connected, show a compact state summary:

~~~text
peer display name    Remote iPhone
transport            Connected
verification         User selected; app identity not verified
encryption           Required by this adapter
session              Current attempt, short redacted ID
action               Ready to send selected item
~~~

For products with authenticated pairing, replace the explanatory status with
the actual verified account/device binding. A raw MCSessionState.connected
should not be presented as “Secure” or “Synced.”

### Transfer review

Before sending a file or command, show the source item, destination peer,
content type, approximate size, and whether the action is reversible. During
transfer, distinguish local queueing, bytes sent, remote receipt, validation,
and application. Offer cancel while cancellation is meaningful; after the
remote side has applied a command, show that cancellation is no longer a
rollback.

### Reconnect state

When the app returns from background, preserve the user’s draft and show that a
new transport session is being rebuilt. Do not silently reuse a stale “connected”
badge. Require a fresh peer/session handshake before resuming a transfer.

## Adaptation matrix

| Context | Design response |
| --- | --- |
| iPhone compact width | Sequential discovery, review, and transfer destinations; keep the primary action reachable above the keyboard/home indicator. |
| iPad regular width | Split list and inspector or a sheet with a persistent selected-peer summary. |
| Dynamic Type | Let rows wrap; keep name, state, and action separately accessible rather than truncating all into one line. |
| VoiceOver | Expose phase, peer identity, trust/verification, progress, and action state as separate accessible values. |
| Reduce Motion | Replace morphing and pulsing with text/icon/value changes. |
| Reduce Transparency/increased contrast | Use an opaque system surface with separators and explicit status text. |
| Keyboard/pointer/Switch Control | Provide focusable buttons for select, invite, accept, cancel, retry, and fallback. |
| Localization/RTL | Test long peer names, invitation context, error strings, and mirrored navigation. |
| Offline/permission denied | Preserve local work and expose repair or non-nearby fallback. |

## AI review card

An optional on-device AI card can summarize a selected candidate set or propose
a low-risk action. It should be visually subordinate to the deterministic
peer/session controls:

~~~text
AI suggestion
“Alex’s device advertises the same protocol version.”
Source: selected discovery snapshot, revision 12
Reason: capability match only; identity not verified
[Review] [Dismiss]
~~~

The card must say what it knows and what it does not know. Do not use a glowing
AI treatment to imply certainty. If the model is unavailable, refused, stale,
or cannot decode typed output, hide the suggestion and leave the manual route
fully usable.

The accept action should be a normal user-controlled Button. The model never
owns invitationHandler, MCSession, encryption policy, local-network permission,
or a file-send capability.

## Interaction and feedback rules

- Start discovery only from a clear user intent or an explicitly enabled
  feature; stop it when the feature ends.
- Keep the local-network explanation adjacent to the action that needs it.
- Make invitation expiry and cancellation recoverable.
- Use progress with a numeric or textual value, not only an animated ring.
- Announce meaningful state changes to VoiceOver without flooding it with every
  packet or byte.
- Keep transient peer loss from deleting a draft or changing the selected
  destination without confirmation.
- Use haptics only as reinforcement; never make a haptic the only indication of
  acceptance, failure, or completion.
- Keep logs and diagnostic surfaces redacted; a peer’s display name may be
  personal data.

## Design review checklist

Before calling a peer surface native and ready, verify:

- the new-vs-legacy transport decision is written down;
- discovery, selection, trust, session, and remote application are separate
  states;
- standard SwiftUI controls carry the main interactions;
- glass is limited to functional groups and has a readable fallback;
- the invitation shows purpose, scope, and explicit accept/reject;
- transfer progress, cancellation, and remote-application boundaries are
  visible;
- Dynamic Type, VoiceOver, Reduce Motion, increased contrast, keyboard, and
  Switch Control complete the route;
- local-network denial leaves a repair or fallback path;
- AI proposals are source-bound, typed, stale-invalidated, and reviewable;
- physical multi-device and signed build evidence exists before release claims.

## Sources

- [Multipeer Connectivity](https://developer.apple.com/documentation/multipeerconnectivity)
- [Moving from Multipeer Connectivity to Network framework](https://developer.apple.com/documentation/technotes/tn3213-moving-from-multipeer-connectivity-to-network-framework)
- [Understanding local network privacy](https://developer.apple.com/documentation/technotes/tn3179-understanding-local-network-privacy)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
