# SwiftUI Network Framework modern peer-transport capability recipes

This page is a capability cookbook for building nearby iOS 26 app features
with the modern Network Framework API. Each recipe names the ownership and
proof boundary so a feature does not accidentally turn discovery metadata into
identity, a socket into authorization, or a send callback into completion.

The foundation route is:

~~~text
Info.plist privacy
  -> listener and/or browser role
  -> Bonjour candidate
  -> selected endpoint
  -> authenticated connection
  -> typed protocol
  -> application receipt
  -> SwiftUI state
~~~

## Recipe matrix

| Capability | Build with | Keep outside the framework |
| --- | --- | --- |
| Advertise a local service | NetworkListener + BonjourListenerProvider | Service ownership, conflict handling, user-visible availability. |
| Browse nearby services | NetworkBrowser + Bonjour provider | Candidate list, sorting, selection, stale revision. |
| Reach Apple peer-to-peer Wi-Fi | NWParametersProvider.peerToPeerIncluded(true) | Device compatibility, permission, fallback, radio proof. |
| Keep traffic local | NWParametersProvider.localOnly(true) | Product statement about where data may travel. |
| Secure bytes | TLS { TCP() } or QUIC’s TLS | Pairing, authorization, certificate/trust policy. |
| Typed messages | Coder<Message, Message, NetworkJSONCoder> | Schema versioning, size budget, idempotence, application. |
| Typed message IDs | TLV | Type allowlist, malformed/unknown type behavior. |
| Custom framing | Framer<T> | Parser bounds, checksum, version, backpressure. |
| Large streams | TCP/TLS plus explicit framing | Resume, hash, destination, cancellation, receipt. |
| Multiplexed flows | QUIC streams | Stream ownership, limits, datagram loss policy. |
| Full mesh | Listener plus selected outbound connections | Membership, election, duplicate suppression, trust. |
| AI collaboration | Foundation Models proposal layer | User review, stale checks, tool boundary, transport authority. |

## 1. Host a service

Use a listener when the device accepts incoming connections. Give it a
product-specific Bonjour type and an intentionally small TXT record. Observe
listener state and service registration changes. A host should not display
“online” merely because listener construction succeeded; wait for the ready and
registered states.

The host contract should contain:

~~~text
service role: host
protocol version: 2
capability list: allowlisted
name: presentation only
trust requirement: explicit
new connection limit: bounded
~~~

When a service name conflicts, use the actual registered name exposed by the
framework. Never make a persistent identity depend on the requested Bonjour
name.

## 2. Browse and present candidates

Use a `NetworkBrowser` task scoped to the SwiftUI feature. Convert each
browser update into a candidate snapshot with a monotonically increasing
discovery revision. Keep the raw endpoint in the transport layer; expose a
redacted candidate model to the view.

~~~text
Candidate
  id: local correlation ID
  displayName: bounded presentation value
  endpoint: transport-owned reference
  protocolVersion: parsed allowlisted value
  capabilities: parsed allowlisted values
  trustState: unknown | paired | blocked
  discoveryRevision
~~~

The user’s selection must include the current discovery revision. If the
candidate disappears or its metadata changes, invalidate the selection and
ask the user whether to retry.

## 3. Opt into local peer-to-peer links

Use a parameter builder when a product needs Apple peer-to-peer Wi-Fi:

~~~text
TLS
  -> TCP
  -> localOnly
  -> peerToPeerIncluded
  -> explicit interface/path policy
~~~

This is not a guarantee that a peer is available. It is an opt-in to eligible
interfaces. Record whether the feature allows infrastructure Wi-Fi,
peer-to-peer Wi-Fi, or both, and test the actual supported-device matrix.

If the app can operate without peer-to-peer links, make that a fallback rather
than forcing a Wi-Fi-only design. If the product must stay local-only, show
that constraint before the operation and prohibit unintended wider paths.

## 4. Authenticate after discovery

Treat Bonjour and TXT values as hints that help the user select a candidate.
After the connection is ready:

1. exchange protocol version and app build family;
2. exchange a fresh nonce;
3. prove the app-owned identity with pairing, account binding, or certificate
   policy;
4. compare capabilities against the requested operation;
5. issue a local session epoch;
6. authorize each sensitive operation.

Do not put the entire trust decision in a one-time device picker. Pairing
records can be revoked, devices can be reinstalled, and a reconnect can use a
different endpoint. Re-run the handshake for each new connection epoch.

## 5. Send typed messages

For commands, state events, and small proposals, use a versioned Codable
envelope above an encrypted stream:

~~~text
Envelope
  protocolVersion
  messageType
  messageID
  sourceRevision
  sessionEpoch
  payload
~~~

The receiver should:

- bound the encoded size;
- reject unsupported versions;
- reject messages from the wrong peer or epoch;
- deduplicate by message ID;
- validate payload and authorization;
- persist or apply only after validation;
- return an application receipt when the domain operation completes.

“Send returned” means the local channel accepted the operation. It does not
mean the other app displayed, validated, or applied it.

## 6. Transfer larger content

Do not make a large file a single unbounded message. Use a framed stream or a
protocol with explicit chunks:

~~~text
TransferManifest
  transferID
  contentType
  byteCount
  contentHash
  sourceRevision
  chunkSize
  resumePolicy

chunks
  sequence
  offset
  length
  bytes
  checksum
~~~

The receiving app writes into a private temporary destination, caps the total
size, validates the hash and type, then atomically moves or imports the result.
Never treat a temporary received URL as a durable file until ownership and
validation are complete.

The user-facing states should distinguish:

~~~text
queued -> sending -> received -> validating -> imported -> applied
                         \-> rejected | cancelled | interrupted
~~~

## 7. Use QUIC deliberately

QUIC is useful when a product needs multiplexed reliable streams or a
best-effort datagram channel. Use streams for:

- handshake and trust;
- control messages;
- transfer manifests and receipts;
- data that must be ordered or retried.

Use datagrams only for data that can be dropped, reordered, or reconstructed.
Respect the maximum datagram/frame size and fragment at the application layer
when necessary. Do not send an irreversible action only as a datagram.

If the product needs one reliable path and one best-effort path, bootstrap the
datagram use over the reliable stream and bind it to the same connection,
peer, and epoch.

## 8. Build a full mesh

For a collaborative nearby app, give every peer the same role:

~~~text
each device
  -> advertises a service
  -> browses for peers
  -> presents candidates
  -> connects outbound to selected peers
  -> accepts inbound connections
  -> authenticates each edge
  -> replicates versioned operations
~~~

The mesh coordinator owns:

- maximum peers and connection limits;
- duplicate edge suppression;
- peer membership revisions;
- per-edge session epochs;
- leader or conflict policy if needed;
- replay and deduplication;
- user removal and trust revocation.

Do not assume that an inbound connection and an outbound connection to the
same peer are the same edge. Use an app-owned peer identity and handshake
nonce to coalesce or reject duplicates.

## 9. Create a client-server local route

For a one-host product, keep the flow simpler:

~~~text
host
  listener ready + Bonjour registered

client
  browser candidates
  -> user selects
  -> connection
  -> handshake
  -> request
  -> server validates authorization
  -> response + application receipt
~~~

The host may be authoritative for the local document or capability, but it
still must validate the client and operation. The client must show the user
what the host will receive or change.

## 10. Recover from path or peer loss

On waiting, failed, cancelled, path change, or a lost candidate:

1. preserve domain work in a local draft or queue;
2. close or scope out the old transport;
3. increment the connection epoch;
4. invalidate receipts and proposals from the old epoch;
5. rediscover or revalidate the endpoint;
6. reconnect with bounded backoff;
7. re-run the handshake;
8. resend only idempotent or explicitly resumable work;
9. show whether the user must approve again.

Never hide all errors behind automatic retry. The retry policy should stop
when permission is denied, the peer is blocked, the protocol is incompatible,
the user cancels, or the retry budget is exhausted.

## 11. Keep the SwiftUI boundary semantic

Expose a view model that speaks in product states, not raw Network Framework
objects:

~~~text
NearbyModel
  permission: PermissionState
  candidates: [Candidate]
  selectedCandidateID: ID?
  trustReview: TrustReview?
  connection: ConnectionPresentation
  transfer: TransferPresentation
  fallback: FallbackAction?
~~~

The model may retain a transport coordinator internally, but the view should
not call send, receive, run, or tryNextEndpoint directly. This makes the view
testable and prevents a presentation action from bypassing trust or
stale-revision checks.

## 12. Add Liquid Glass as a task layer

Good glass groups:

- refresh and cancel controls above the candidate list;
- trust review actions;
- compact transfer controls;
- a small status action group that does not hide the status text.

Bad glass groups:

- every candidate row;
- permission explanations;
- error text that needs maximum contrast;
- dynamic raw endpoint details;
- controls that are not semantically related.

Use the SwiftUI Liquid Glass APIs and system styles. Provide a solid or
opaque fallback under reduced-transparency settings and verify that the
surface remains legible without blur.

## 13. Add an on-device AI proposal layer

The model receives only bounded, redacted local input:

~~~text
AI input
  userGoal
  selectedItemSummary
  candidate summaries
  allowed operations
  discoveryRevision
~~~

The model returns a typed proposal:

~~~text
AI output
  candidateID
  action
  reason
  requestedFields
  sourceDiscoveryRevision
  expiry
  requiresUserApproval = true
~~~

The coordinator rechecks all values after approval. The model cannot:

- access a raw NetworkConnection or listener;
- choose a candidate outside the user allowlist;
- send or receive arbitrary bytes;
- bypass local-network permission;
- accept a pairing decision;
- apply a remote operation;
- continue after its source revision expires.

If Foundation Models is unavailable, the feature becomes less assisted, not
less usable.

## 14. Configuration route

Record the configuration as an artifact:

~~~text
service type
  _bishop-sync._tcp

Info.plist
  NSLocalNetworkUsageDescription
  NSBonjourServices = _bishop-sync._tcp

transport
  TCP + TLS + Coder
  localOnly = true or false
  peerToPeerIncluded = true or false
  maximum message size
  maximum transfer size
  retry budget
  pairing policy
~~~

Keep the service type consistent across code, Info.plist, test fixtures, and
physical-device instructions. If the feature is shipped in an extension,
verify the container target owns the privacy declaration and the extension has
the required framework and entitlement configuration.

## 15. Test route

Minimum deterministic fixtures:

- candidate discovery revision changes;
- TXT metadata has an unknown key or oversized value;
- connection waits, fails, and cancels;
- handshake version or nonce is invalid;
- duplicate message ID is replayed;
- frame length exceeds the limit;
- transfer hash or content type is wrong;
- peer disappears during review;
- reconnect starts a new epoch;
- AI proposal is stale or unavailable.

Minimum physical route:

~~~text
two signed devices
  -> fresh permission
  -> advertise + browse
  -> select + review
  -> authenticate
  -> typed message
  -> synthetic file transfer
  -> background/foreground
  -> peer loss/reconnect
  -> accessibility settings
  -> TestFlight build
~~~

## Do not combine these routes accidentally

| If the need is... | Prefer... | Why |
| --- | --- | --- |
| Existing MC app compatibility | An isolated legacy adapter | MC is deprecated for new iOS 26 work. |
| User-selected system device pairing | DeviceDiscoveryUI when its platform scenario fits | It supplies system discovery UI for supported flows. |
| Share a group activity | Group Activities and SharePlay | Group activity semantics differ from arbitrary peer transport. |
| Watch companion communication | Watch Connectivity | Companion lifecycle and identity are system-owned. |
| Accessory setup | AccessorySetupKit/Core Bluetooth/Matter/Thread | Accessory identity and permissions differ from app peers. |
| Cloud API or file upload | URLSession | Server-backed reliability and authentication differ from a local Bonjour route. |

## Sources

- [Network Framework modern peer transport route](../42-framework-deep-dives/139-swiftui-network-framework-modern-peer-transport-route.md)
- [Network](https://developer.apple.com/documentation/network)
- [NetworkConnection](https://developer.apple.com/documentation/network/networkconnection)
- [NetworkListener](https://developer.apple.com/documentation/network/networklistener)
- [NetworkBrowser](https://developer.apple.com/documentation/network/networkbrowser)
- [NetworkChannel](https://developer.apple.com/documentation/network/networkchannel)
- [Bonjour](https://developer.apple.com/documentation/network/bonjour)
- [BonjourListenerProvider](https://developer.apple.com/documentation/network/bonjourlistenerprovider)
- [NWTXTRecord](https://developer.apple.com/documentation/network/nwtxtrecord)
- [NWParametersProvider](https://developer.apple.com/documentation/network/nwparametersprovider)
- [TCP](https://developer.apple.com/documentation/network/tcp)
- [TLS](https://developer.apple.com/documentation/network/tls)
- [QUIC](https://developer.apple.com/documentation/network/quic)
- [Coder](https://developer.apple.com/documentation/network/coder)
- [TLV](https://developer.apple.com/documentation/network/tlv)
- [FramerProtocol](https://developer.apple.com/documentation/network/framerprotocol)
- [Choosing the right networking API](https://developer.apple.com/documentation/technotes/tn3151-choosing-the-right-networking-api)
- [Moving from Multipeer Connectivity to Network framework](https://developer.apple.com/documentation/technotes/tn3213-moving-from-multipeer-connectivity-to-network-framework)
- [Understanding local network privacy](https://developer.apple.com/documentation/technotes/tn3179-understanding-local-network-privacy)
- [Privacy - Local Network Usage Description](https://developer.apple.com/documentation/bundleresources/information_property_list/nslocalnetworkusagedescription)
- [Privacy - Bonjour Services](https://developer.apple.com/documentation/bundleresources/information_property_list/nsbonjourservices)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
