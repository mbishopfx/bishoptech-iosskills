# SwiftUI Network Framework modern peer-transport route

For a new iOS 26 nearby-device product, Network Framework is the primary
transport route to study. Apple’s current migration guidance introduces
`NetworkConnection`, `NetworkListener`, and `NetworkBrowser` as the modern
Swift API aligned with iOS 26, while the older `NWConnection`, `NWListener`,
and `NWBrowser` APIs remain useful for compatibility and existing code. Apple
also says MultipeerConnectivity was deprecated in 2026 and should be avoided
for new code. This page treats the modern route as a product architecture,
not as a drop-in replacement for a peer session.

The core route is:

~~~text
user intent
  -> local-network explanation and permission
  -> listener and/or browser role
  -> Bonjour endpoint candidate
  -> untrusted metadata filter
  -> user-selected peer
  -> authenticated protocol handshake
  -> typed NetworkConnection / NetworkChannel
  -> versioned transfer and application receipt
  -> SwiftUI state and accessibility
  -> cancellation, path change, reconnect, and release proof
~~~

## Start with the architecture decision

Network Framework separates the server/listener role from the outgoing
connection role. That is an important boundary for products that previously
treated one MCSession as a symmetric group object.

| Product shape | Network Framework shape | Ownership decision |
| --- | --- | --- |
| One device hosts a local service and another selects it | The host creates a NetworkListener; the client creates a NetworkBrowser and then a NetworkConnection | The host owns admission and service availability; the client owns selection and request intent. |
| A few peers form a fully connected local group | Every participating device runs a listener and a browser, then maintains explicit outbound connections to selected peers | The app owns membership, election, duplicate suppression, and per-peer lifecycle. Network Framework does not create a group or invitation policy for you. |
| A local device talks to a cloud service | NetworkConnection or URLSession, depending on the protocol, with the local peer route kept separate | Do not make a Bonjour candidate look like an account or server authority. |
| A nearby device is only a handoff target | Bonjour discovery plus one short-lived connection, or the higher-level system handoff route when it fits | Keep transport lifetime shorter than the user’s document or task lifetime. |
| An accessory is not an app peer | Core Bluetooth, AccessorySetupKit, Matter, Thread, or the accessory-specific route | Do not use a peer transport to model accessory identity or capabilities. |

For a full mesh, model these values explicitly:

~~~text
MeshPeer
  peerID: app-owned stable identifier
  endpoint: current Bonjour endpoint
  trust: unknown | pairingRequired | authenticated | blocked
  connectionState: idle | connecting | ready | waiting | failed | cancelled
  sessionEpoch: monotonically increasing local attempt
  capabilities: allowlisted and versioned
  lastSeen: local diagnostic timestamp

MeshCoordinator
  selectedPeers
  membershipRevision
  connectionTasks
  protocolVersion
  userApproval
~~~

Do not use NetworkBrowser’s current endpoint array as the membership
database. A browse result is a transient observation. Persist the product’s
own selection and trust records, then reconcile them against discovery.

## Modern types and when to use them

| Type | Role | Design implication |
| --- | --- | --- |
| NetworkBrowser<Provider> | Runs discovery for a BrowserProvider, such as .bonjour(...) | Its run handler receives the current endpoint set. Return .continue while browsing and .finish(value) when the user or a policy has selected a result. |
| Bonjour.Endpoint | A typed discovered endpoint that conforms to Connectable | It exposes id, display-oriented Bonjour fields, nwEndpoint, and the optional NWTXTRecord; it is still not authenticated identity. |
| NetworkListener<ApplicationProtocol> | Binds and optionally advertises a local service | Register state and service changes, cap new connections, and run each accepted connection through an application-owned handler. |
| NetworkConnection<ApplicationProtocol> | An outgoing connection or an accepted listener connection | Its application protocol type determines the available send/receive surface. |
| NetworkChannel<ApplicationProtocol> | Base channel for typed transfer | Use send, receive, messages, maximumDatagramSize, and state rather than inventing a second callback layer. |
| TCP | Reliable stream protocol | It has no message boundaries by itself. Put Coder, TLV, or a custom Framer above it. |
| TLS | Encrypted stream protocol | Configure peer authentication and, for sensitive routes, a certificate or identity policy. Encryption is not the same as app authorization. |
| QUIC | Multiplexed transport | Use streams for reliable work and the single datagram channel for best-effort work; set explicit size and retry policy. |
| Coder | Typed Codable message protocol | Prefer versioned domain envelopes when the route has discrete messages. |
| TLV or Framer<T> | Message framing over a stream | Bound lengths and validate type/version before allocating or applying a payload. |
| NWParametersBuilder | Produces protocol parameters and path policy | Apply localOnly, peerToPeerIncluded, interface restrictions, and path cost policy at construction time. |

The modern API is generic over the protocol stack. A
NetworkConnection<TCP> is not interchangeable with a
NetworkConnection<Coder<...>>; keep the type at the transport boundary and
expose domain-specific methods from an actor or service object.

## Discovery is a candidate pipeline, not trust

Apple’s modern Bonjour browser can be used for either a user-facing candidate
list or a policy-driven search. The common forms are:

~~~swift
let browser = NetworkBrowser(
    for: .bonjour("_bishop-sync._tcp", includeTxtRecord: true)
)

let selected: Bonjour.Endpoint = try await browser.run {
    endpoints -> NetworkBrowser<Bonjour>.RunResult<Bonjour.Endpoint> in
    guard let endpoint = endpoints.first else { return .continue }
    return .finish(endpoint)
}
~~~

Use .continue while the user is still deciding. Use .finish only when the
product has a concrete result, then cancel or leave the browsing task. For a
manual picker, publish the endpoint snapshot to a main-actor store and keep
the browser task alive until the user taps a candidate or leaves the screen.
For a targeted lookup, inspect the TXT record and finish only when the
allowlisted value matches.

Bonjour.Endpoint and its NWTXTRecord are discovery data. Treat every field
as untrusted input:

- Do not use a device name as an account name, authorization result, or
  cryptographic identity.
- Allowlist TXT keys and cap string/data lengths before decoding.
- Ignore unsupported protocol versions and capabilities rather than guessing.
- Do not put secrets, access tokens, file names, or raw user content in a TXT
  record.
- Do not log a raw endpoint, IP address, or persistent device label by default.

On the listener side, advertise with a provider such as:

~~~swift
let provider = BonjourListenerProvider(
    name: "Bishop Peer",
    type: "_bishop-sync._tcp",
    txtRecord: NWTXTRecord(["protocol": "2", "role": "host"])
)
~~~

The name is presentation metadata and may be changed by the system if there
is a conflict. Observe onServiceRegistrationUpdate and update UI from the
registered endpoint rather than assuming the requested name is the final
name. If a stable app-owned identifier is necessary, put a non-secret
identifier in the TXT record and authenticate it again after the connection.

Register a new service type with IANA when the product creates one. Use a
short, product-specific Bonjour type and keep the service type identical in
the listener, browser, and Info.plist declaration.

## Local-network privacy and Apple peer-to-peer Wi-Fi

The app target needs a truthful NSLocalNetworkUsageDescription when the
feature uses the local network. If the app browses or advertises a specific
Bonjour service, declare the type in NSBonjourServices, for example:

~~~text
NSLocalNetworkUsageDescription
  Connect to another nearby device to transfer the item you selected.

NSBonjourServices
  _bishop-sync._tcp
~~~

Place these declarations in the container app target. An extension that
participates in the feature does not replace the container app’s privacy
declaration. Test fresh-install undetermined, allowed, denied, and later
revoked states. A denied local-network prompt is a product state with a
repair path, not an empty discovery list.

Apple’s Network Framework parameter policy exposes both localOnly and
peerToPeerIncluded. Use them for different decisions:

| Setting | Use |
| --- | --- |
| localOnly(true) | Keep a route on local links when the product must not use the wider network. |
| peerToPeerIncluded(true) | Opt the connection, listener, or browser into Apple peer-to-peer interfaces. |
| requiredInterfaceType(.wifi) | Require Wi-Fi only when the product can explain that constraint and has a fallback. |
| expensivePathsProhibited(true) | Avoid metered paths for large transfers when the user has not opted in. |
| constrainedPathsProhibited(true) | Avoid constrained paths when the feature’s traffic cannot fit them. |

Apple peer-to-peer Wi-Fi is an Apple-device route; it is not an open wire
protocol for arbitrary third-party devices. If the product needs standard
peer-to-peer discovery across supported ecosystems, investigate Wi-Fi Aware
or another explicitly supported route. When you set peerToPeerIncluded, the
physical-device matrix must include two compatible Apple devices and the
local-network permission state.

## Architecture the handshake, not just the socket

TLS gives the transport confidentiality and peer-authentication hooks. It
does not decide whether a discovered peer may read a document or apply an AI
proposal. Make the connection pipeline explicit:

~~~text
Bonjour candidate
  -> user selects candidate
  -> connection reaches ready
  -> protocol version exchange
  -> nonce/challenge or pairing-code exchange
  -> validate app-owned peer identity and capability claims
  -> authorize the requested operation
  -> create authenticated session epoch
  -> allow typed messages
~~~

Use an app-owned handshake envelope containing at least:

~~~text
Handshake
  protocolVersion
  appBuildFamily
  peerID
  sessionNonce
  supportedCapabilities
  requestedRole
  transcriptBinding
  signatureOrPairingProof
~~~

The peer identifier should be stable enough for the user’s pairing model but
should not be broadcast as a permanent personal identifier without a privacy
decision. Rotate connection nonces per attempt. Bind the accepted identity to
the current endpoint and handshake transcript. Reject:

- unsupported protocol versions;
- duplicate or reused nonces;
- claims for capabilities not actually implemented;
- a peer identity outside the user-selected allowlist;
- a handshake from a previous session epoch;
- a message received before authentication completes.

For a private or sensitive app, prefer a deliberate pairing code, account
binding, or certificate identity over trusting a device name or TXT record.
If custom TLS validation is used, document the trust anchor, rotation, failure
mode, and recovery path. Never use “TLS connected” as the user-facing
authorization sentence.

## Protocol stacks and backpressure

Pick the smallest stack that expresses the product contract:

~~~text
TCP
  -> reliable ordered bytes

TLS { TCP() }
  -> encrypted reliable ordered bytes

Coder(Message.self, using: .json) { TLS { TCP() } }
  -> typed Codable messages over encrypted stream

TLV { TLS { TCP() } }
  -> typed message IDs and bounded message payloads

QUIC(alpn: ["bishop-sync"]) { UDP() }
  -> multiplexed reliable streams plus one best-effort datagram channel
~~~

NetworkChannel’s async send and receive functions are the backpressure
boundary. Await them. Do not enqueue an unbounded array of Data in a
@MainActor view model, and do not make a send button imply that the peer has
applied the operation.

For stream routes:

- choose a maximum frame/message size before decoding;
- send a version, type, correlation ID, byte count, and revision;
- reject lengths that exceed the product budget before allocation;
- handle partial reads and write completion;
- make application of a message idempotent;
- model send accepted, bytes transferred, decoded, validated, and applied as
  separate states.

For QUIC datagrams, use only best-effort work that can be dropped or
reconstructed. Apple’s migration guidance says to use reliable streams to
bootstrap or coordinate a parallel best-effort channel, and to respect the
maximum datagram/frame size. Never send an irreversible command only through a
datagram.

## Connection state, path changes, and reconnect

The modern channel state is:

~~~text
setup
  -> waiting(error)
  -> preparing
  -> ready
  -> failed(error) | cancelled
~~~

waiting means the system may still become viable; failed is an
unrecoverable error for that connection attempt; cancelled is a deliberate
end. The reducer should expose these differences to the UI. A “connecting”
spinner that hides a denied permission, unsupported peer, or invalid
handshake is not a native-quality state.

For a one-to-one connection, observe:

- onStateUpdate for lifecycle;
- onPathUpdate for effective path changes;
- onViabilityUpdate for whether traffic currently has a route;
- onBetterPathUpdate for an available preferred path;
- currentPath, localEndpoint, and remoteEndpoint for diagnostics;
- tryNextEndpoint() when a multi-endpoint connection should fall through.

Reconnect in an actor or isolated transport coordinator:

~~~text
connection epoch 41
  -> waiting / cancelled
  -> preserve unsent domain operations
  -> invalidate in-flight receipts for epoch 41
  -> wait with bounded exponential backoff and jitter
  -> rediscover or reuse only a still-valid endpoint
  -> create epoch 42
  -> repeat handshake
  -> resend only idempotent or explicitly resumed work
~~~

Do not silently resume a stale connection after a user leaves the feature or
revokes trust. A reconnect may require re-approval when the operation is
sensitive. Background and foreground transitions must be tested on physical
devices; simulator success does not prove radio discovery or suspension
behavior.

## Native SwiftUI and Liquid Glass composition

The transport service should emit semantic state; SwiftUI should render the
state and collect user intent. A useful surface model is:

~~~text
NearbyTransportView
  permissionExplanation
  browserCandidates
  pendingTrustDecision
  authenticatedPeers
  activeTransfers
  reconnectNotice
  fallbackAction
~~~

Use system controls, labels, lists, sheets, alerts, progress views, and
navigation. Apply Liquid Glass to functional control groups—such as the
nearby picker toolbar, trust decision controls, or compact transfer actions—
rather than placing every row inside translucent decoration. Keep the
candidate identity, trust state, permission state, and transfer result legible
without color or blur alone.

Useful accessibility labels describe the semantic status:

~~~text
“Bishop Peer, nearby, protocol version 2, not yet trusted”
“Connect to Bishop Peer”
“Transfer waiting for local-network access”
“Transfer sent; waiting for the other device to apply it”
~~~

Support Dynamic Type, VoiceOver, Reduce Motion, Reduce Transparency, keyboard
and Switch Control. If reduced transparency removes the glass treatment, the
surface must still preserve grouping, contrast, focus, and action hierarchy.

## Optional typed on-device AI collaboration

An on-device model may help a person choose or prepare a peer operation, but
the model is not the transport authority. Keep AI on the proposal side:

~~~text
current candidates + user goal + bounded local metadata
  -> typed proposal
  -> stale-revision check
  -> human review
  -> explicit button action
  -> transport coordinator
  -> authenticated connection
~~~

A proposal can be:

~~~text
PeerProposal
  sourceDiscoveryRevision
  candidateID
  action: inspect | invite | prepareTransfer
  reason
  requestedFields
  expiresAt
  requiresUserApproval: true
~~~

Do not give a model raw NetworkConnection, listener, browser, credential,
file, or arbitrary tool access. Do not allow it to select a peer outside the
user’s current allowlist, bypass a pairing prompt, or send a payload without an
explicit user action. If the browser changes, the connection epoch changes,
the model is unavailable, or the model refuses, invalidate the proposal and
keep the manual path complete.

## Capability routes to build next

| Capability | Primary route | Proof that matters |
| --- | --- | --- |
| Browse nearby hosts | NetworkBrowser + Bonjour | Two devices discover a declared service after a truthful permission prompt. |
| Advertise a host | NetworkListener + BonjourListenerProvider | Registration callback reports the actual service and name. |
| Select a peer | SwiftUI state and user action | A candidate is not connected before review. |
| Authenticate | TLS plus app-owned handshake | Wrong pairing proof and stale epoch are rejected. |
| Typed messages | Coder or TLV over TLS/TCP | Duplicate, invalid, oversized, and stale messages are handled. |
| Large transfer | Framed stream or resource protocol | Progress, cancellation, hash, resume policy, and final application receipt are visible. |
| Low-latency best effort | QUIC datagrams | Oversize and dropped data are safe; reliable stream remains available. |
| Full mesh | Listener + per-peer outgoing connections | Membership and reconnect state are app-owned and bounded. |
| AI-assisted preparation | Foundation Models proposal layer | Model unavailable or stale leaves a complete manual flow. |

## Source and implementation guardrails

Before shipping a nearby route, check:

- current Apple availability and deprecation annotations in the SDK used to
  build the app;
- exact service type in listener, browser, Info.plist, and any IANA record;
- local-network usage explanation and denied-state fallback;
- protocol stack, TLS policy, app handshake, and pairing recovery;
- maximum message/datagram/frame sizes and idempotence rules;
- cancellation and reconnect behavior across permission, path, and lifecycle
  changes;
- SwiftUI accessibility and reduced-effects behavior;
- two physical devices, signed TestFlight artifact, and archive metadata.

## Sources

- [Network](https://developer.apple.com/documentation/network)
- [NetworkConnection](https://developer.apple.com/documentation/network/networkconnection)
- [NetworkListener](https://developer.apple.com/documentation/network/networklistener)
- [NetworkBrowser](https://developer.apple.com/documentation/network/networkbrowser)
- [NetworkChannel](https://developer.apple.com/documentation/network/networkchannel)
- [BrowserProvider](https://developer.apple.com/documentation/network/browserprovider)
- [Connectable](https://developer.apple.com/documentation/network/connectable)
- [ListenerProvider](https://developer.apple.com/documentation/network/listenerprovider)
- [Bonjour](https://developer.apple.com/documentation/network/bonjour)
- [BonjourListenerProvider](https://developer.apple.com/documentation/network/bonjourlistenerprovider)
- [NWTXTRecord](https://developer.apple.com/documentation/network/nwtxtrecord)
- [NWParametersProvider](https://developer.apple.com/documentation/network/nwparametersprovider)
- [NetworkProtocolOptions](https://developer.apple.com/documentation/network/networkprotocoloptions)
- [TCP](https://developer.apple.com/documentation/network/tcp)
- [TLS](https://developer.apple.com/documentation/network/tls)
- [QUIC](https://developer.apple.com/documentation/network/quic)
- [Coder](https://developer.apple.com/documentation/network/coder)
- [TLV](https://developer.apple.com/documentation/network/tlv)
- [FramerProtocol](https://developer.apple.com/documentation/network/framerprotocol)
- [NetworkChannel.State](https://developer.apple.com/documentation/network/networkchannel/state-swift.enum)
- [Choosing the right networking API](https://developer.apple.com/documentation/technotes/tn3151-choosing-the-right-networking-api)
- [Moving from Multipeer Connectivity to Network framework](https://developer.apple.com/documentation/technotes/tn3213-moving-from-multipeer-connectivity-to-network-framework)
- [Understanding local network privacy](https://developer.apple.com/documentation/technotes/tn3179-understanding-local-network-privacy)
- [Privacy - Local Network Usage Description](https://developer.apple.com/documentation/bundleresources/information_property_list/nslocalnetworkusagedescription)
- [Privacy - Bonjour Services](https://developer.apple.com/documentation/bundleresources/information_property_list/nsbonjourservices)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
