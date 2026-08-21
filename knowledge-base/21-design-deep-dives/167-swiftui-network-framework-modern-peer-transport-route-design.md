# SwiftUI Network Framework modern peer-transport route design

The nearby-device screen should feel like a calm native task: explain why
local-network access is needed, show real candidates, make trust explicit,
show transport state honestly, and keep a manual fallback available. Liquid
Glass can organize the actions, but it should never become a substitute for
identity, permission, status, or accessible content.

This design page pairs with the [modern Network Framework transport
route](../42-framework-deep-dives/139-swiftui-network-framework-modern-peer-transport-route.md).

## Design objective

The user should be able to answer five questions without reading a protocol
manual:

1. What nearby task am I starting?
2. Why is the app asking for local-network access?
3. Which device am I about to connect to?
4. What has happened so far: discovered, trusted, connected, sent, or applied?
5. What can I do if the peer disappears or the model is unavailable?

The screen hierarchy should be:

~~~text
Nearby transfer
  -> explain and request local-network access
  -> browse or advertise
  -> list candidates
  -> review selected peer and requested action
  -> authenticate / connect
  -> show typed operation and progress
  -> confirm application or explain recovery
~~~

Do not skip from a translucent “nearby” card directly to a success badge.
The user needs to see the trust and application boundaries.

## State is the visual system

Make the SwiftUI view a projection of a reducer or observable transport
store. The view should not infer connection state from whether an endpoint
exists.

~~~text
PermissionState
  unknown
  explaining
  requesting
  allowed
  denied
  restricted

DiscoveryState
  idle
  browsing
  candidates(revision)
  advertising
  unavailable(reason)

PeerState
  discovered
  selected
  reviewing
  handshaking
  authenticated
  rejected(reason)
  lost

TransferState
  idle
  preparing
  sending
  received
  validating
  applied
  waitingForReconnect
  failed(recoverable)
  cancelled
~~~

Every state needs:

- a visible label;
- a system-appropriate icon or shape that is not the only signal;
- an accessible announcement when the status changes;
- an allowed action;
- a recovery or fallback path when applicable.

The state reducer should reject impossible transitions. For example, a
discovered Bonjour endpoint cannot become authenticated without a successful
handshake, and a transfer cannot become applied merely because a send call
returned.

## Suggested screen composition

### 1. Intent header

Use a large, plain-language title such as “Transfer to a nearby device.” Keep
the explanation one or two sentences:

> The app uses your local network to find the device you choose and transfer
> only the item you approve.

If the feature is local-only, say that. If the route can use a wider network
path, say what data may travel and let the user choose.

Avoid showing raw Bonjour service types, IP addresses, ports, or internal
protocol names in the primary surface. Put diagnostic details behind a
developer or support affordance.

### 2. Permission explanation

Before the system prompt, show the user-facing reason in the context of the
action. If the OS permission is denied, replace the empty candidate list with
a repair card:

~~~text
Local-network access is off
To find another nearby device, allow access in Settings.
[Open Settings] [Use another method]
~~~

When access is undetermined, do not start background discovery and then show
an unexplained blank state. Start the prompt from the user’s explicit nearby
action. Test fresh install, allowed, denied, and revoked states on a signed
device build.

### 3. Candidate list

Each candidate row should contain:

~~~text
primary label: user-recognizable device/service name
secondary label: “Nearby” + bounded capability/protocol summary
trust label: “Not yet trusted”, “Paired”, or “Unavailable”
last observation: optional local-only diagnostic text
action: “Review”
~~~

Do not style an untrusted candidate as a contact, account, or verified peer.
Use an information disclosure sheet to explain what the app learned from
discovery and what it still needs to verify.

For a device that advertises a TXT record, display only allowlisted,
human-meaningful values. Never surface raw access tokens, file names, private
metadata, or a persistent identifier that the user did not expect.

### 4. Trust and operation review

The review sheet should identify:

- the selected candidate;
- the exact item or capability to be shared;
- whether the peer is already paired;
- the permission and security status;
- the protocol or app-version compatibility result;
- the action that the primary button will perform.

Use “Connect and transfer” only when that is exactly what the next action
does. If the next action only performs an app handshake, label it “Continue.”
The user should not have to reverse-engineer side effects from a generic
“Done” button.

### 5. Connection and transfer status

Make progress semantic, not just numeric:

~~~text
Finding the device
Checking the connection
Confirming the peer
Sending the selected item
Waiting for the other device to apply it
Transfer complete
~~~

For a stream or large transfer, show byte progress only when it helps. A
progress bar at 90% is not a success signal if the other device has not
validated or applied the content.

When the path becomes nonviable, say “Connection paused; waiting for a
usable network path.” When a better path is available, do not interrupt the
user with a technical prompt unless a decision is required.

## Liquid Glass rules for this route

Use Apple’s Liquid Glass APIs as a native functional grouping layer:

- place the nearby action toolbar or compact transfer controls in a
  functional glass group;
- use a GlassEffectContainer when multiple glass elements should read as one
  group and can morph or move together;
- use stable glass identity only for controls that participate in a real
  transition;
- keep a glass control over a stable, legible content layer;
- use the system’s material and tint behavior rather than building a custom
  blur clone;
- preserve a non-glass semantic fallback under Reduce Transparency or when
  the platform does not provide the effect.

Avoid:

- wrapping every candidate row in glass;
- putting a trust warning inside low-contrast translucent decoration;
- using glass as the only boundary between “discovered” and “authenticated”;
- animating a network error into a success-like state;
- adding ornamental refraction behind dynamic text that makes VoiceOver and
  Dynamic Type harder to follow.

A strong layout might be:

~~~text
content layer
  candidate list / transfer detail / permission explanation

functional glass group
  [Refresh] [Select] [Connect] [Cancel]

status layer
  explicit text state + progress + recovery action
~~~

The content remains the product. Glass groups the actions that operate on the
content.

## Motion and transition choreography

Native motion should communicate state change:

| Event | Motion | Constraint |
| --- | --- | --- |
| Candidate appears | Insert with a restrained fade/slide | Do not imply trust or connection. |
| Candidate selected | Highlight and present review sheet | Keep focus visible for keyboard and Switch Control. |
| Handshake begins | Replace selection action with a clear progress state | Do not loop an indefinite decorative animation without status text. |
| Connection paused | Reduce activity and show a waiting label | Keep cancel and fallback actions available. |
| Transfer applied | Confirm the actual application receipt | Do not celebrate send acceptance as completion. |
| Candidate lost | Remove or mark unavailable with a reversible explanation | Preserve selected work and show reconnect choice. |

Respect Reduce Motion. Do not make a state change depend on the completion of
an animation. A user who disables motion should receive the same information
and the same action order.

## Accessibility contract

VoiceOver should be able to complete the full task:

1. understand the local-network purpose;
2. identify a candidate;
3. hear whether the candidate is trusted;
4. review the exact operation;
5. approve or cancel;
6. hear connection, validation, and application status;
7. recover from denial or peer loss.

Useful labels:

~~~text
“Bishop Peer. Nearby. Not yet trusted. Review.”
“Connect and transfer the selected document to Bishop Peer.”
“Connection paused. Waiting for a usable network path.”
“Transfer received. Checking its type, size, and revision.”
“Transfer applied on Bishop Peer.”
~~~

Use labels and values separately where the control is adjustable. Keep
Dynamic Type from truncating the peer’s state or action. Ensure color is not
the only indication of trust, connectedness, error, or completion. Support
Reduce Transparency and high-contrast settings with a solid, legible
alternative.

For keyboard and Switch Control:

- keep a predictable focus order from intent to candidate to action;
- make the selected row and primary action distinct;
- give Cancel and fallback actions reachable focus;
- avoid gesture-only selection;
- ensure a glass morphing transition does not lose focus.

## AI-assisted peer selection without hidden automation

An on-device model can help summarize bounded candidate metadata:

~~~text
“Two devices are available. One is paired and supports the selected transfer.
The other is nearby but requires review.”
~~~

It should return a typed proposal, not operate the browser or connection:

~~~text
Proposal
  candidateID
  action
  reason
  sourceDiscoveryRevision
  expiresAt
  requiresUserApproval: true
~~~

Render the proposal as an explanation beside the ordinary control. The user
still selects the peer and presses the action button. If the discovery
revision changes, the proposal expires. If Foundation Models is unavailable
or refuses, hide only the assistance and preserve the manual picker.

Never send raw device logs, credentials, private file contents, or arbitrary
network objects to a model. The transport coordinator must re-check the
candidate allowlist, trust state, permission, and current epoch after the
user approves a proposal.

## Empty, denied, and failure states

Design these states as first-class screens:

| State | Surface |
| --- | --- |
| No candidates yet | “Keep this screen open while another device advertises” plus Refresh and fallback. |
| Local network denied | Purpose, Settings repair, and alternative route. |
| Candidate has incompatible protocol | Explain that the other app needs an update; do not expose an opaque error code. |
| Candidate lost during review | Preserve the requested operation and offer retry or cancel. |
| Handshake rejected | Say the devices could not confirm each other; do not say “network error” only. |
| Waiting path | Explain that the connection is waiting for a usable path and keep cancellation visible. |
| Transfer validation failed | Identify the failed validation category without exposing sensitive payload data. |
| Model unavailable | Keep the manual route and do not show a broken AI placeholder. |

For destructive or irreversible actions, require a second review when the
transport reconnects after a long interruption or when the source revision
changes.

## Design review checklist

- The primary screen explains the nearby purpose before permission.
- A discovered candidate is visually distinct from a trusted peer.
- The exact item and side effect appear before the connection action.
- Transport, handshake, validation, and application are separate statuses.
- Liquid Glass groups controls and has a legible non-glass fallback.
- Reduce Motion and Reduce Transparency preserve task completion.
- VoiceOver, Dynamic Type, keyboard, and Switch Control can complete the task.
- A denied local-network state has a truthful Settings repair path.
- Peer loss preserves or clearly cancels in-progress work.
- AI suggestions are typed, stale-checked, optional, and user-approved.
- No raw endpoint, token, filename, or credential is exposed in the UI.
- The design is tested on the signed artifact with two physical devices.

## Sources

- [Network Framework modern peer transport route](../42-framework-deep-dives/139-swiftui-network-framework-modern-peer-transport-route.md)
- [NetworkConnection](https://developer.apple.com/documentation/network/networkconnection)
- [NetworkListener](https://developer.apple.com/documentation/network/networklistener)
- [NetworkBrowser](https://developer.apple.com/documentation/network/networkbrowser)
- [NetworkChannel](https://developer.apple.com/documentation/network/networkchannel)
- [Bonjour](https://developer.apple.com/documentation/network/bonjour)
- [BonjourListenerProvider](https://developer.apple.com/documentation/network/bonjourlistenerprovider)
- [NWTXTRecord](https://developer.apple.com/documentation/network/nwtxtrecord)
- [NWParametersProvider](https://developer.apple.com/documentation/network/nwparametersprovider)
- [TLS](https://developer.apple.com/documentation/network/tls)
- [Choosing the right networking API](https://developer.apple.com/documentation/technotes/tn3151-choosing-the-right-networking-api)
- [Moving from Multipeer Connectivity to Network framework](https://developer.apple.com/documentation/technotes/tn3213-moving-from-multipeer-connectivity-to-network-framework)
- [Understanding local network privacy](https://developer.apple.com/documentation/technotes/tn3179-understanding-local-network-privacy)
- [Privacy - Local Network Usage Description](https://developer.apple.com/documentation/bundleresources/information_property_list/nslocalnetworkusagedescription)
- [Privacy - Bonjour Services](https://developer.apple.com/documentation/bundleresources/information_property_list/nsbonjourservices)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
