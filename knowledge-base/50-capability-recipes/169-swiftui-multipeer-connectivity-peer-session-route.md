# SwiftUI MultipeerConnectivity peer-session capability route

Use this capability route when a product has a concrete nearby peer outcome and
must decide between MultipeerConnectivity, Network Framework, Nearby Interaction,
Group Activities, or an accessory framework. The current Apple route is
legacy-first: MC is appropriate for an existing integration or a deliberate
compatibility adapter, while new app-to-app transport should start with
Network Framework.

## Outcome-to-capability routing

| User outcome | Route | Hard boundary |
| --- | --- | --- |
| Discover a nearby app that supports an existing MC protocol | MCNearbyServiceBrowser and MCNearbyServiceAdvertiser | Deprecated API, service type rules, local-network permission, invitation consent, and no identity guarantee. |
| Maintain an existing peer session | MCSession and MCSessionDelegate | Encryption policy, private delegate queue, eight-peer limit, disconnect/reconnect, and per-payload validation. |
| Build a new local peer transport | Network Framework | Own architecture, identity, Bonjour, security, framing, backpressure, and reconnect. |
| Show distance or direction | Nearby Interaction | Session-scoped tokens, hardware, permission, and no data transport. |
| Share an activity through FaceTime/Messages | Group Activities and SharePlay | Activity eligibility, group session lifecycle, participant state, and message/attachment semantics. |
| Pair a Bluetooth accessory | AccessorySetupKit/Core Bluetooth | Accessory identity, GATT or setup contract, background behavior, and hardware. |
| Transfer a file into a provider or system surface | File Provider, document picker, or ShareLink | System ownership, document identity, security-scoped access, or transfer destination. |

## Product boundary map

Keep these layers separate:

~~~text
SwiftUI feature
  -> peer use-case interface
  -> transport adapter (MC legacy or Network modern)
  -> discovery/identity/security policy
  -> framed protocol
  -> domain reducer
  -> persistence/outbox
  -> optional local-AI proposal
~~~

The SwiftUI feature should ask for capabilities such as discover, invite,
connect, sendCommand, sendResource, cancel, and reconnect. It should not know
which delegate callback or Bonjour object implements them.

## Configuration checklist

### App and extension targets

- Link the selected framework in the target that actually owns the code.
- Set the deployment target and availability checks from the current SDK.
- Add NSLocalNetworkUsageDescription to the app’s Info.plist for local-network
  access.
- Add the MC service declaration to NSBonjourServices in the container app when
  using Bonjour-backed MC discovery; format the service type as a leading
  underscore and trailing `._tcp` entry.
- Review privacy manifest, logging, analytics, and diagnostics for peer names,
  invitation context, file names, and transfer contents.
- Keep a host-app UI target separate from any extension or system-surface target.

### Peer identity

- Create the local MCPeerID once and archive it with secure coding.
- Keep displayName short and user-appropriate; do not encode an account token.
- Do not construct a remote MCPeerID from a string.
- Bind the remote framework peer to a product-owned session epoch and, for
  sensitive flows, an account or pairing handshake.

### Session security

- Choose MCEncryptionPreference explicitly for a legacy session.
- Prefer required encryption for sensitive data if the supported peer matrix
  permits it.
- Define what happens on negotiation failure; do not silently send unencrypted
  content.
- Keep MCSession behind a transport protocol so the app can migrate to Network.

## Discovery and invitation recipe

1. Validate the service type at build/configuration time.
2. Create or restore the local peer ID.
3. Create the MCSession with the chosen encryption policy.
4. Create advertiser/browser objects with the same service type.
5. Start discovery only for the user-started feature lifetime.
6. Present candidates using bounded, allowlisted discoveryInfo.
7. On user selection, invite with a versioned context and finite timeout.
8. On the invitee, validate context and user intent before calling the
   invitation handler.
9. Establish a protocol Hello exchange after MCSession reports connected.
10. Transition to ready only after the handshake and capability checks pass.

The context and discoveryInfo are transport inputs, not authorization. A
malicious or buggy peer can advertise arbitrary values. Decode with bounded
data, reject unknown schema versions when necessary, and keep the UI safe if a
candidate disappears between selection and invitation.

## Transfer policy

| Transfer | Use when | Required product policy |
| --- | --- | --- |
| Reliable Data | Small state/event messages where order matters | Size cap, schema/revision, idempotence, acknowledgement or application receipt. |
| Unreliable Data | Freshness matters more than retransmission | Sequence/timestamp, drop-tolerant reducer, no irreversible side effect on a single packet. |
| Resource | File or HTTP document | Manifest, content type, byte limit, hash, Progress cancellation, temporary URL ownership, safe destination. |
| Stream | Continuous bytes or large custom protocol | Frame length, backpressure, stream delegate/run loop, cancellation, reconnect/resume design. |

The framework’s completion or receive callback is only one evidence point. A
resource can be received but fail validation; a command can be delivered but
rejected by the domain; a stream can close after partial data. Record each
state explicitly.

## Lifecycle and recovery

~~~text
featureOff
  -> starting
  -> permissionDenied | discovering
  -> candidateSelected
  -> inviting
  -> connecting
  -> handshaking
  -> ready
  -> transferPending | transferring
  -> applied | rejected | failed
  -> disconnected
  -> rebuilding | ended
~~~

On backgrounding, close or mark MC transport state as unavailable and preserve
only bounded resumable metadata. On foreground, rebuild discovery/session
objects and require a fresh handshake. If the peer object or pairing state
does not match, do not resume automatically.

Own cancellation in one coordinator. Cancelling a Swift task, an NSProgress,
an OutputStream, or an invitation must update the same domain state and release
the associated object. Use generation IDs so a late delegate callback cannot
reopen a canceled transfer.

## SwiftUI state model

```text
PeerFeatureState
  permission: unknown | allowed | denied
  discovery: idle | browsing | advertising | failed
  candidates: [PeerCandidate]
  invitation: pending | accepted | rejected | expired | none
  session: none | connecting | connected | handshaking | ready | closed
  transfers: [TransferState]
  proposal: none | generating | review | stale | rejected | applied
  fallback: manual | localOnly | unavailable
```

Persist domain state, not framework delegates. Make the transition to applied
depend on deterministic validation and any required acknowledgement. Keep a
draft or source item when the peer disconnects.

## Optional typed AI route

Use Foundation Models only after selecting a bounded candidate snapshot. A
proposal shape can include:

~~~text
peerCorrelation: redacted local candidate key
action: inspect | invite | prepareTransfer
reason: short source-grounded explanation
sourceRevision: discovery/session snapshot revision
~~~

The proposal is advisory. The host app must check current candidate membership,
session epoch, transport status, encryption policy, content permissions, and
user confirmation. A typed schema must not contain a capability to call
invitationHandler, send data, or grant access. If the model is unavailable,
refuses, or returns stale output, preserve the deterministic peer flow.

## Proof route

### Source/compile

- Re-open MC and Network docs for the selected SDK.
- Typecheck adapter code against the actual iOS SDK.
- Inspect deprecation warnings and record the migration decision.
- Verify Info.plist keys and target membership in the archive, not only in the
  host app source.

### Runtime/device

- Use two or more physical devices with the target OS/build.
- Exercise local-network undetermined, allowed, denied, and revoked states.
- Accept/reject invitations and send invalid/oversized contexts.
- Test peer loss before invitation, during connection, and during resource
  transfer.
- Verify encryption mismatch behavior and reconnect after background/foreground.
- Validate resource destination, stream framing, cancellation, and resume.
- Run VoiceOver, Dynamic Type, Reduce Motion/transparency, keyboard, pointer,
  and Switch Control through the complete route.

### Release

- Archive the host and any extension targets.
- Inspect bundle privacy keys, service declarations, entitlements, and profiles.
- Test the signed TestFlight build on named devices, not only a Simulator.
- Keep the production claim bounded: “two tested devices completed the transfer
  under recorded conditions,” not “works with nearby devices.”

## Sources

- [Multipeer Connectivity](https://developer.apple.com/documentation/multipeerconnectivity)
- [MCSession](https://developer.apple.com/documentation/multipeerconnectivity/mcsession)
- [MCPeerID](https://developer.apple.com/documentation/multipeerconnectivity/mcpeerid)
- [MCNearbyServiceAdvertiser](https://developer.apple.com/documentation/multipeerconnectivity/mcnearbyserviceadvertiser)
- [MCNearbyServiceBrowser](https://developer.apple.com/documentation/multipeerconnectivity/mcnearbyservicebrowser)
- [MCSessionDelegate](https://developer.apple.com/documentation/multipeerconnectivity/mcsessiondelegate)
- [MCSessionSendDataMode](https://developer.apple.com/documentation/multipeerconnectivity/mcsessionsenddatamode)
- [Moving from Multipeer Connectivity to Network framework](https://developer.apple.com/documentation/technotes/tn3213-moving-from-multipeer-connectivity-to-network-framework)
- [Understanding local network privacy](https://developer.apple.com/documentation/technotes/tn3179-understanding-local-network-privacy)
- [Privacy - Local Network Usage Description](https://developer.apple.com/documentation/bundleresources/information_property_list/nslocalnetworkusagedescription)
- [Privacy - Bonjour Services](https://developer.apple.com/documentation/bundleresources/information_property_list/nsbonjourservices)
- [Network](https://developer.apple.com/documentation/network)
- [Nearby Interaction](https://developer.apple.com/documentation/nearbyinteraction)
- [Group Activities](https://developer.apple.com/documentation/groupactivities)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
