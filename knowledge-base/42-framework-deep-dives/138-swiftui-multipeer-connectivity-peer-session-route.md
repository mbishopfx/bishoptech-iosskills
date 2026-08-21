# SwiftUI MultipeerConnectivity peer-session route

MultipeerConnectivity is the high-level discovery and session framework for an
existing product that needs nearby app instances to find one another, invite
one another, and exchange messages, resources, or streams. Apple’s current
documentation marks the framework’s primary classes and protocols deprecated
and directs new work to Network Framework. Treat this page as a source-grounded
legacy adapter guide and migration map, not as the default transport for a new
iOS 26 app.

The route is:

~~~text
user intent
  -> local-network explanation and permission
  -> stable local peer identity
  -> advertiser/browser discovery
  -> user selection and invitation context
  -> encrypted session
  -> versioned message/resource/stream protocol
  -> SwiftUI state and review
  -> foreground recovery, disconnect, and teardown
  -> physical multi-device and signed-release proof
~~~

## Decide whether MultipeerConnectivity belongs in the product

| Need | Preferred iOS 26 starting point | Why |
| --- | --- | --- |
| New app-to-app local transport | Network Framework | Apple’s migration technote maps the Multipeer features to the newer Network APIs and avoids adopting a deprecated high-level framework. |
| Maintain an existing MC browser/invitation/session product | MultipeerConnectivity adapter | Preserve a known user flow while isolating the deprecated API behind a transport protocol. |
| Measure distance or direction | Nearby Interaction | Proximity is not identity and is not a data transport. |
| Coordinate FaceTime, Messages, or a share activity | Group Activities and SharePlay | Group session semantics are different from a fully connected nearby MC session. |
| Connect a GATT accessory | Core Bluetooth or AccessorySetupKit | An app peer is not an accessory and should not be modeled as one. |
| Expose a local Bonjour service with a custom protocol | Network Framework | Own the protocol, security, architecture, reconnect, and lifecycle explicitly. |

If a new feature can choose freely, record Network Framework as the decision
and link back to the existing [Network Framework and streaming route](../41-framework-deep-dives/20-urlsession-network-and-streaming.md)
and [Nearby Interaction and local transport](17-nearby-interaction-and-local-transport.md).
If compatibility requires MC, put every use behind a capability adapter and
keep the app domain independent of MCPeerID, MCSession, and delegate queues.

## Two phases: discovery and session

Apple describes two distinct phases:

1. **Discovery.** An MCNearbyServiceBrowser searches for a service type. An
   MCNearbyServiceAdvertiser or MCAdvertiserAssistant publishes availability.
   The browser can see a small discoveryInfo dictionary and the invitee can
   receive arbitrary context bytes, but the app has not yet established a
   session or trust relationship.
2. **Session.** After an invite is accepted, MCSession reports peer state and
   carries data, resources, or byte streams. The session is a transport state,
   not an account, authorization, or domain object.

Keep the transition visible in the product state:

~~~text
idle
  -> permissionPending
  -> browsing | advertising | both
  -> candidateFound
  -> invitationPending
  -> accepted | rejected | expired
  -> connecting
  -> connected
  -> transferring | ready
  -> disconnected
  -> reconnecting | ended
~~~

Do not let a discovered display name silently become a trusted user. The
person should see what is being shared, which peer is being selected, and what
the next side effect will be.

## MCPeerID: stable identity without making identity claims

MCPeerID represents a peer in an MC session and has a user-facing displayName.
The display name is intended for a short UI label, cannot be empty, and has a
63-byte UTF-8 limit in Apple’s current documentation. It is not an account
identifier, a cryptographic proof of the person’s name, or a permission grant.

Each call to init(displayName:) creates a new peer ID even when the display
name is the same. If the device must keep a stable peer identity across app
launches, archive the local MCPeerID using secure coding and restore it before
creating the browser, advertiser, or session. Store the archive in app-owned
protected storage and treat failure to decode it as an identity-reset event.

Never create an MCPeerID for a remote device by calling init(displayName:) with
the remote display name. The remote peer ID must be the object supplied by the
framework or the object exchanged through a custom discovery protocol. For
custom discovery, Apple’s session documentation describes exchanging the
serialized peer ID, obtaining nearby connection data, and then calling
connectPeer(_:withNearbyConnectionData:). Validate the protocol and peer
binding before connecting.

Use a product-owned record alongside the framework object:

~~~text
PeerCandidate
  frameworkPeerID: in-memory MCPeerID
  stablePeerDigest: redacted local correlation value
  displayName: short presentation text
  discoveryInfo: allowlisted, size-bounded metadata
  selected: Bool
  trustState: unknown | userApproved | authenticated | rejected
  sessionEpoch: current connection attempt
~~~

Do not persist raw discovery metadata or peer display names in analytics by
default. A peer digest is only a local correlation aid; it does not turn MC
into an authentication system. Sensitive products still need an app-owned
pairing code, authenticated account binding, or a protocol-level identity
handshake.

## MCSession security and ownership

Create MCSession with the local peer ID. The security initializer exposes an
optional security identity and an MCEncryptionPreference. The choices express
whether the session prefers encryption, requires encryption, or does not use
encryption. For a legacy adapter carrying anything private, choose required
encryption where the product’s supported peers can satisfy it and document the
fallback or rejection path. Do not silently downgrade a sensitive transfer.

The SDK headers expose these states and boundaries:

| Contract | Implementation rule |
| --- | --- |
| MCSessionState | Treat connecting, connected, and notConnected as transport state; persist a protocol checkpoint rather than the session object. |
| encryptionPreference | Make the policy explicit and test the peer mismatch/error path. |
| connectedPeers | Use as a current transport snapshot, not as a durable membership database. |
| disconnect() | Call when the user leaves, the feature ends, or trust is revoked. Clear owned transfer state deliberately. |
| delegate | Retain a delegate for the session lifetime and translate callbacks into app events. |
| peer limit | Apple documents a maximum of eight peers including the local peer; design the UI and protocol for that limit. |

MCSession delegate callbacks arrive on a private queue. Apple’s current
documentation says the receiver must dispatch work explicitly when it needs a
particular run loop or operation queue. The delegate should do minimal parsing,
copy bounded data, and hand off to an actor or main-actor store. Never mutate
SwiftUI state directly from an assumed callback queue.

The delegate callback is not proof that the domain operation succeeded. For a
message, distinguish:

~~~text
encoded locally
  -> send accepted by MCSession
  -> received callback
  -> decoded and validated
  -> applied to current session/revision
  -> user-visible result
~~~

Add a schema version, event ID, source peer correlation, session epoch, and
source revision to every meaningful message. Make receiver application
idempotent and reject stale epochs.

## Advertiser and browser discovery

### Service type

The serviceType identifies the app’s networking protocol. Apple’s current
documentation requires a short Bonjour-style name: one to fifteen characters,
ASCII lowercase letters, numbers, and hyphens, at least one letter, no leading
or trailing hyphen, and no adjacent hyphens. Use a product-specific value such
as `bishop-sync`, not a generic name such as `chat` that can collide with an
unrelated app.

### discoveryInfo

discoveryInfo is a small string-to-string dictionary advertised through Bonjour
TXT records. Keep it small and non-sensitive. It can describe a protocol
version, coarse capability flags, or an invitation role; it cannot prove the
peer owns an account or is safe to trust. Allowlist keys, cap lengths, and
ignore unknown values.

### Advertiser

MCNearbyServiceAdvertiser publishes the local peer and calls its delegate when
an invitation arrives. The delegate must decide whether to accept and must
pass a valid session when accepting. The context bytes are arbitrary data from
the inviter and must be treated as untrusted input. Decode only a bounded,
versioned format and show the person what the invitation means before accepting
a sensitive action.

Call the invitation handler once. If a decision requires a SwiftUI sheet,
copy the peer/context into a pending-invitation state, suspend the connection
decision in a controlled way, and make sure the callback is resolved on every
accept, reject, cancellation, timeout, and teardown path. Do not create a
session for an invitation that the user has not approved.

### Browser

MCNearbyServiceBrowser reports foundPeer and lostPeer callbacks. It can invite
a selected peer to a session with a context and timeout. Apple’s header says a
nonpositive timeout uses a default of thirty seconds. Keep the selected peer
bound to the current browser/session epoch so a lost candidate cannot be
invited after the UI has moved on.

Neither advertiser nor browser delegate callbacks have a guaranteed queue.
Translate them into one serialized store, and do not update UIKit or SwiftUI
from the callback without an explicit hop.

## Local-network privacy and Bonjour declarations

MultipeerConnectivity uses Bonjour internally. Apple’s local-network privacy
technote says an app using the local network needs NSLocalNetworkUsageDescription
in its Info.plist. If the app registers or browses specific Bonjour services,
declare them with NSBonjourServices. For an MC service type such as
`bishop-sync`, Apple’s technote gives the Bonjour declaration form
`_bishop-sync._tcp`.

Put the privacy keys in the app target’s Info.plist. If the app has an
extension, Apple’s technote says the keys belong in the container app rather
than only in the extension. Explain the user outcome in the usage string:
“Connect to another nearby device to transfer the document you selected.” Do
not use a vague “network access” string when the feature is a peer handoff.

Test undetermined, allowed, denied, and later-revoked local-network states.
When access is denied, keep the app useful with a clear repair path and a
non-nearby fallback. Background local-network work while permission is
undetermined can be denied without showing the prompt, so request or explain
the capability during a foreground user-started flow.

## Data messages, resources, and streams

Use the smallest transport that matches the data:

| Payload | API | Product contract |
| --- | --- | --- |
| Small versioned command or state event | send(_:toPeers:with:) | Encode bounded Codable data, choose reliable or unreliable deliberately, and validate before applying. |
| File or HTTP resource | sendResource(at:withName:toPeer:withCompletionHandler:) | Observe Progress, retain only the state needed for cancellation, validate the received file, and move it out of the temporary URL before the receive callback returns. |
| Long-lived byte sequence | startStream(withName:toPeer:) | Configure InputStream/OutputStream delegates, schedule and open them on a run loop, frame bytes, and close on cancellation/disconnect. |

Reliable mode guarantees ordered delivery at the framework message layer;
unreliable mode sends without queueing and may drop or reorder messages. This
does not replace app-level idempotence, revision checks, or authorization.
Avoid sending an entire document as one unbounded Data message. Use a resource
transfer or a deliberately framed stream and include a manifest with content
type, byte count, hash, revision, and transfer ID.

On the receiving side, Apple documents a start-resource callback with
NSProgress and a finish callback with a temporary local URL. The app is
responsible for opening or moving the file to a permanent location before the
finish callback returns. Treat the URL as an ownership handoff with a short
lifetime. Validate size, type, transfer ID, and content hash before importing.

Streams are not message boundaries. Add a framing protocol such as:

~~~text
magic | protocolVersion | frameLength | transferID | sequence | payload | checksum
~~~

Bound frameLength, reject impossible values, handle partial reads and writes,
and apply backpressure. A stream open is not proof that the full document or
command was received.

## Foreground, background, and reconnect

Apple’s MultipeerConnectivity overview says that entering the background stops
advertising and browsing and disconnects open sessions. Returning to the
foreground automatically resumes advertising and browsing, but the app must
reestablish closed sessions. This is a crucial boundary for iOS apps: do not
promise continuous peer transfer while suspended.

Use a session epoch and resumable protocol checkpoint:

~~~text
foreground + user starts
  -> create/reuse stable MCPeerID
  -> create MCSession
  -> start advertiser/browser
  -> invite/accept
  -> exchange Hello(sessionEpoch, schema, capabilities)
  -> transfer with per-item revision and acknowledgement

background/disconnect
  -> stop UI activity and close local streams
  -> persist only bounded resumable metadata
  -> mark transport unavailable

foreground
  -> rebuild session and discovery objects
  -> reselect or revalidate peer
  -> perform handshake
  -> resume only uncommitted, still-authorized items
~~~

Do not resume a file upload solely because the display name matches. Rebind
the protocol to the current peer object, session epoch, account/pairing state,
and content revision.

## SwiftUI and Liquid Glass composition

Use SwiftUI to show the state of a peer workflow, not to hide transport
uncertainty. A native surface can be composed as:

~~~text
NavigationStack
  -> current phase/status section
  -> nearby peer List with stable row identity
  -> invitation or transfer review sheet
  -> per-transfer ProgressView and cancel action
  -> recovery/permission section
  -> optional typed AI proposal card
~~~

Use standard List, Button, Label, ToolbarItem, ProgressView, alerts, and
sheets for their semantic behavior. Reserve Liquid Glass for a small functional
group such as the current transport status and the primary invite/cancel
action. Do not apply glass to every row or use blur as a substitute for a
trust boundary. Keep peer display name, connection state, transfer state, and
verification state as separate readable values.

The design should expose:

- discovery is not connection;
- connection is not authentication;
- send accepted is not durable application;
- local transfer complete is not remote business success;
- AI suggestion is not approval.

On compact widths, make the peer list and review sheet sequential. On regular
widths, use a split or inspector layout with the selected candidate and current
transfer details. Preserve the same state model, stable IDs, cancellation, and
error copy across size classes.

## Optional on-device AI collaboration proposals

Foundation Models can summarize a user-selected set of nearby candidates or
propose a low-risk collaboration action from bounded, user-visible metadata.
Keep the AI boundary explicit:

~~~text
allowlisted candidate snapshot
  -> local model availability check
  -> typed proposal(peerCorrelation, action, reason, sourceRevision)
  -> deterministic peer/session/protocol validation
  -> user review
  -> explicit send/invite/transfer action
~~~

The model must not:

- infer a person’s identity from a display name or proximity;
- accept or reject an invitation silently;
- choose an unreviewed peer for a consequential transfer;
- unlock a session, bypass encryption, or grant local-network access;
- treat a sent callback as proof of remote application;
- receive raw documents, credentials, or unrestricted discovery metadata when
  a redacted summary is sufficient.

Bind a proposal to a peer correlation value, session epoch, source revision,
and an allowlisted action. If discovery or session state changes, invalidate
the proposal and require a fresh review.

## Accessibility and alternative input

The primary peer action must be a semantic control with a useful label, hint,
and value. Expose status text in addition to color, blur, haptics, or animated
connection effects. VoiceOver should be able to discover the peer name, trust
state, connection state, transfer progress, and available action in one row.

Verify:

- Dynamic Type does not truncate the only peer identity or action;
- VoiceOver can accept, reject, cancel, retry, and understand failure;
- Reduce Motion and reduced transparency preserve phase changes and legibility;
- Switch Control and Full Keyboard Access can operate the same route;
- pointer, keyboard, and controller input do not depend on a gesture-only
  invitation;
- localized service labels, invitation context, and error text fit long strings
  and right-to-left layouts.

## Migration to Network Framework

Apple’s TN3213 maps the high-level MC concepts to a Network Framework design.
Use the mapping as a decision record, not as a mechanical rename:

| MultipeerConnectivity | Network Framework design question |
| --- | --- |
| MCPeerID | Generate and persist an app-owned random peer identifier; bind it to the protocol handshake. |
| MCNearbyServiceAdvertiser | Configure a Network listener and Bonjour advertise descriptor; own service metadata and privacy. |
| MCNearbyServiceBrowser | Configure a Network browser; validate each result and deduplicate endpoints. |
| MCSession | Choose client/server or fully connected architecture, then own Network connection lifecycle. |
| reliable send | Use a framed reliable protocol over the chosen Network connection. |
| unreliable send | Use an explicit datagram or best-effort protocol where supported and appropriate. |
| sendResource | Design a resource protocol with manifest, range/chunk policy, progress, cancellation, and ownership. |
| startStream | Use a byte-stream connection with explicit framing and backpressure. |
| MC encryption preference | Configure transport security and app-level identity/authentication explicitly. |
| MC background behavior | Define what survives suspension, what resumes, and what the user must restart. |

The Network route gives the product more control and more responsibility. Keep
the same domain protocol and SwiftUI state model so an MC adapter can be
removed without rewriting the app’s user experience.

## Evidence boundary

Source and compiler checks can prove that a route is spelled correctly against
the selected SDK. They cannot prove nearby discovery, local-network prompt
behavior, encryption negotiation, device radio availability, user consent,
stream throughput, or second-device semantics. Require at least two physical
devices for an MC feature and record the exact OS/build, permission state,
service type, peer selection, session state, transfer result, and teardown.

## Sources

- [Multipeer Connectivity](https://developer.apple.com/documentation/multipeerconnectivity)
- [MCPeerID](https://developer.apple.com/documentation/multipeerconnectivity/mcpeerid)
- [MCPeerID init(displayName:)](https://developer.apple.com/documentation/multipeerconnectivity/mcpeerid/init%28displayname%3A%29)
- [MCSession](https://developer.apple.com/documentation/multipeerconnectivity/mcsession)
- [MCSessionDelegate](https://developer.apple.com/documentation/multipeerconnectivity/mcsessiondelegate)
- [MCSessionSendDataMode](https://developer.apple.com/documentation/multipeerconnectivity/mcsessionsenddatamode)
- [MCSessionState](https://developer.apple.com/documentation/multipeerconnectivity/mcsessionstate)
- [MCEncryptionPreference](https://developer.apple.com/documentation/multipeerconnectivity/mcencryptionpreference)
- [MCNearbyServiceAdvertiser](https://developer.apple.com/documentation/multipeerconnectivity/mcnearbyserviceadvertiser)
- [MCNearbyServiceAdvertiserDelegate](https://developer.apple.com/documentation/multipeerconnectivity/mcnearbyserviceadvertiserdelegate)
- [MCNearbyServiceBrowser](https://developer.apple.com/documentation/multipeerconnectivity/mcnearbyservicebrowser)
- [MCNearbyServiceBrowserDelegate](https://developer.apple.com/documentation/multipeerconnectivity/mcnearbyservicebrowserdelegate)
- [MCError](https://developer.apple.com/documentation/multipeerconnectivity/mcerror)
- [Moving from Multipeer Connectivity to Network framework](https://developer.apple.com/documentation/technotes/tn3213-moving-from-multipeer-connectivity-to-network-framework)
- [Understanding local network privacy](https://developer.apple.com/documentation/technotes/tn3179-understanding-local-network-privacy)
- [Privacy - Local Network Usage Description](https://developer.apple.com/documentation/bundleresources/information_property_list/nslocalnetworkusagedescription)
- [Privacy - Bonjour Services](https://developer.apple.com/documentation/bundleresources/information_property_list/nsbonjourservices)
- [Network](https://developer.apple.com/documentation/network)
- [NWBrowser](https://developer.apple.com/documentation/network/nwbrowser)
- [NWConnection](https://developer.apple.com/documentation/network/nwconnection)
- [NWListener](https://developer.apple.com/documentation/network/nwlistener)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
