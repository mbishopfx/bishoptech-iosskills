# Nearby Interaction and peer transport route

Use this route for device-to-device, accessory, or local-service experiences where proximity adds meaning. Keep discovery, trust, transport, nearby measurements, domain data, and side effects separate.

~~~text
user outcome
  -> supported device/platform check
  -> discovery and candidate selection
  -> consent and identity/protocol handshake
  -> transport connection
  -> NI token/configuration exchange
  -> distance/direction-driven UI
  -> typed data exchange
  -> confirmation/side effect
  -> teardown or resync
~~~

## Select the transport

| Need | Route | Current boundary |
| --- | --- | --- |
| Direction/distance to Apple peer | Nearby Interaction + NISession + NINearbyPeerConfiguration | Token exchange, UWB/device capability, permission, field of view, physical proof. |
| Direction/distance to accessory | Nearby Interaction accessory configuration + accessory protocol | Accessory firmware/protocol and configuration-data exchange. |
| New local service discovery/data | Network Framework NWBrowser/NWListener/NWConnection | Local network permission, Bonjour declarations, TLS/protocol, reconnect. |
| Existing high-level peer session | Multipeer Connectivity | MCSession is deprecated in current docs for new work; foreground/session reconnect and legacy maintenance. |
| Nearby only as a ranking signal | Discovery plus optional NI | Ranking is not identity or authorization. |

Do not use NI as a transport, or a socket connection as proof that the intended person/device accepted the action.

## State model

~~~swift
enum NearbyRouteState {
    case idle
    case checkingSupport
    case permissionRequired
    case discovering
    case candidateSelected
    case awaitingConsent
    case exchangingTokens
    case connectingTransport
    case running
    case directionUnavailable
    case interrupted
    case reconnecting
    case completed
    case failed(String)
}
~~~

The real target should add:

- current candidate/session ID;
- authenticated peer/accessory identity;
- discovery token/configuration lifetime;
- transport connection state;
- protocol revision/sequence;
- distance/direction freshness;
- side-effect confirmation;
- stop reason and fallback.

## Route A: discover and select

1. Check platform/device support and required permissions.
2. Advertise or browse a product-owned service using Network Framework, or use existing MC browser/advertiser behavior for a legacy route.
3. Show candidates with product-owned names and purpose.
4. Require explicit selection/acceptance.
5. Validate discovery metadata and protocol version.
6. Establish an app-owned identity handshake.

Do not auto-connect to the strongest nearby signal. Candidate data is untrusted until the handshake passes.

## Route B: exchange NI configuration

For a peer:

1. Create or receive an NISession.
2. Exchange discovery tokens through the approved transport.
3. Build NINearbyPeerConfiguration with the peer token.
4. Run the configuration.
5. Observe NISessionDelegate updates and lifecycle.

For an accessory:

1. Start the supported accessory discovery/transport route.
2. Receive or send configuration data according to the accessory protocol.
3. Build NINearbyAccessoryConfiguration.
4. Run the NI session.
5. Handle session suspension/invalidation and accessory removal.

Tokens are ephemeral session inputs. Discard them when the session ends and never use them as account IDs.

## Route C: Network Framework connection

For new local transport:

1. Declare local-network/Bonjour configuration when required.
2. Create NWBrowser/NWListener with a service type and parameters.
3. Validate candidates before connecting.
4. Create NWConnection and observe state.
5. Frame messages with length/schema/revision/sequence.
6. Apply authentication/encryption appropriate to the domain.
7. Bound send queues and handle partial reads/backpressure.
8. Reconnect or resync explicitly after path/session loss.

Do not use a connection’s ready state as domain completion. A connection can be ready while a peer has not confirmed the specific action.

## Route D: legacy Multipeer Connectivity

If an existing product uses MC:

1. Create a local MCPeerID and session.
2. Advertise/browse a valid service type.
3. Present or implement invitation acceptance.
4. Validate discovery context.
5. Exchange an application protocol message.
6. Track MCSession peer state and resources.
7. On foreground return, reestablish sessions that disconnected in the background.

For new projects, prefer Network Framework as the current Apple route. Keep MC behind an adapter so the product protocol and UI do not depend on deprecated object lifecycles.

## Protocol and side effect

Use an idempotent message envelope:

~~~text
Message
  protocolVersion
  sessionID
  senderID
  sequence
  revision
  kind
  payload
  requiresConfirmation
~~~

Before applying:

- verify session and peer identity;
- check revision/sequence and duplicate policy;
- validate payload size/type/range;
- confirm the user-approved target;
- make the side effect idempotent;
- return an outcome message;
- preserve local state until outcome reconciliation.

## Nearby UI and AI

Use distance/direction only for the physical guidance layer. The domain feature should use an explicit selected target and protocol-approved data. AI can rank or explain a candidate, but:

- it receives only the current selected context;
- it does not infer a person’s identity;
- it does not grant consent;
- it cannot silently transfer or control;
- it expires when proximity or transport freshness expires.

## Fallbacks

| Failure | Fallback |
| --- | --- |
| Unsupported NI/device | List or manual target selection. |
| Direction unavailable | Distance-only or non-spatial UI. |
| Candidate ambiguous | Ask for selection or show a pairing code. |
| Permission denied | Explain and keep local/manual route. |
| Token stale/wrong peer | Restart token exchange and invalidate session. |
| Network denied | Use user-mediated share/export or manual code. |
| Transport closed | Show reconnect/resync, do not claim delivery. |
| Peer leaves | Preserve draft/outcome and offer retry. |
| AI unavailable | Deterministic candidate list and manual action. |

## Build slices

1. Static candidate list and protocol fixtures.
2. Network discovery/connection with local-network permission.
3. App-owned handshake and versioned messages.
4. NI peer session with token exchange.
5. Direction/distance UI with loss/obstruction/manual states.
6. Physical two-device/accessory run.
7. Reconnect, background, cancellation, and idempotence.
8. AI proposal layer, accessibility, Liquid Glass, energy, and release proof.

## Sources

- [Nearby Interaction](https://developer.apple.com/documentation/nearbyinteraction)
- [NISession](https://developer.apple.com/documentation/nearbyinteraction/nisession)
- [NIConfiguration](https://developer.apple.com/documentation/nearbyinteraction/niconfiguration)
- [NINearbyPeerConfiguration](https://developer.apple.com/documentation/nearbyinteraction/ninearbypeerconfiguration)
- [NINearbyAccessoryConfiguration](https://developer.apple.com/documentation/nearbyinteraction/ninearbyaccessoryconfiguration)
- [Initiating and maintaining a session](https://developer.apple.com/documentation/nearbyinteraction/initiating-and-maintaining-a-session)
- [Network](https://developer.apple.com/documentation/network)
- [NWBrowser](https://developer.apple.com/documentation/network/nwbrowser)
- [NWConnection](https://developer.apple.com/documentation/network/nwconnection)
- [NWListener](https://developer.apple.com/documentation/network/nwlistener)
- [Multipeer Connectivity](https://developer.apple.com/documentation/multipeerconnectivity)
- [MCSession](https://developer.apple.com/documentation/multipeerconnectivity/mcsession)
- [MCNearbyServiceBrowser](https://developer.apple.com/documentation/multipeerconnectivity/mcnearbyservicebrowser)
- [Nearby interactions HIG](https://developer.apple.com/design/human-interface-guidelines/nearby-interactions/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
