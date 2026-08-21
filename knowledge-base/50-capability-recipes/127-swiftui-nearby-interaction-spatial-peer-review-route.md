# SwiftUI Nearby Interaction and spatial-peer review route

This route composes peer discovery, token exchange, Nearby Interaction ranging, spatial state, SwiftUI presentation, optional local AI, and explicit user action. It is a route sketch for a named iOS target and physical supported devices.

Pairs with [SwiftUI Nearby Interaction and spatial-peer review](../42-framework-deep-dives/96-swiftui-nearby-interaction-spatial-peer-review.md), [the design companion](../21-design-deep-dives/124-swiftui-nearby-interaction-spatial-peer-review-design.md), and [the proof matrix](../60-verification/121-swiftui-nearby-interaction-spatial-peer-review-proof-matrix.md).

## Route map

~~~text
target capability and usage descriptions
  -> transport discovery and user-selected peer
  -> NISession and local discovery token
  -> secure token/configuration exchange
  -> peer/accessory configuration
  -> NISession.run
  -> permission and capability checks
  -> nearby-object updates
  -> typed spatial snapshot and freshness
  -> MainActor SwiftUI projection
  -> optional local-AI proposal
  -> deterministic validation
  -> explicit action or stop
~~~

Nearby Interaction is the ranging/spatial stage. The transport is the discovery and data stage. App identity and authorization are separate stages.

## Capability gates

Check the route before opening a spatial action:

1. The target contains NSNearbyInteractionUsageDescription.
2. The runtime supports the required Nearby Interaction feature.
3. The peer token or accessory reports compatible capabilities.
4. The chosen platform is supported.
5. The transport can exchange tokens or accessory configuration.
6. Camera Assistance is only enabled when ARKit/camera conditions and privacy allow.
7. The selected background behavior is explicitly configured and supported.
8. A failure or userDidNotAllow error has a recovery state.

Use NISession.deviceCapabilities for the local feature set and NIDiscoveryToken.deviceCapabilities for the peer’s capabilities. Do not assume direction exists because distance exists.

## State machine

~~~swift
enum SpatialRouteState {
    case unsupported(String)
    case discovering
    case candidate(TransportPeer)
    case exchangingToken
    case waitingForPermission
    case configured
    case ranging
    case reported(SpatialSnapshot)
    case stale(SpatialSnapshot)
    case suspended
    case removed(String)
    case invalidated(String)
}

struct SpatialSnapshot: Sendable, Identifiable {
    let id: UUID
    let sessionGeneration: Int
    let peerTokenDescription: String
    let distanceMeters: Float?
    let direction: SIMD3<Float>?
    let horizontalAngleRadians: Float?
    let verticalEstimate: String
    let receivedAt: Date
    let isStale: Bool
}
~~~

Do not display a stale snapshot as ranging. Keep the session generation so a late delegate callback cannot replace a newer peer selection.

## Peer route

For a peer-device flow:

1. Start a browser/advertiser or Network Framework discovery route.
2. Show candidates and let the person select one.
3. Create the local NISession after the route is ready.
4. Obtain the local discoveryToken.
5. Exchange the token over the selected transport.
6. Securely decode the peer’s NIDiscoveryToken.
7. Check peer device capabilities.
8. Create NINearbyPeerConfiguration with the peer token.
9. Run the configuration on the local NISession.
10. Match updates by the configuration’s peerDiscoveryToken.

If the route uses Multipeer Connectivity, include local-network and Bonjour configuration and record the sample’s deprecation/availability caveat. If the route uses Network Framework, define peer identity, framing, cancellation, and local-network privacy explicitly.

## Accessory route

For a third-party accessory:

1. Discover and authenticate the accessory through Core Bluetooth, local network, or the documented data link.
2. Receive configuration data from the accessory for UWB interaction.
3. Construct NINearbyAccessoryConfiguration.
4. Set the NISession delegate and delegate queue.
5. Run the configuration.
6. Send the device’s shareable configuration data over the accessory link.
7. Match updates by accessoryDiscoveryToken.
8. Stop ranging when the accessory session ends.

Do not treat a Bluetooth connection or configuration-data receipt as proof that the intended physical accessory is present. Keep accessory product identity, pairing identity, and nearby token identity in separate fields.

## Session delegate ownership

Use one coordinator for the NISession and transport:

~~~swift
final class SpatialCoordinator: NSObject, NISessionDelegate {
    let sessionQueue = DispatchQueue(
        label: "com.example.app.nearby-session",
        qos: .userInitiated
    )

    private(set) var session: NISession?
    private var generation = 0

    func begin(peerToken: NIDiscoveryToken) {
        generation += 1
        let session = NISession()
        session.delegate = self
        session.delegateQueue = sessionQueue
        self.session = session

        let configuration = NINearbyPeerConfiguration(peerToken: peerToken)
        session.run(configuration)
    }

    func stop() {
        generation += 1
        session?.invalidate()
        session = nil
    }

    func sessionDidStartRunning(_ session: NISession) {
        // Publish configured/ranging state through a value snapshot.
    }

    func session(
        _ session: NISession,
        didUpdate nearbyObjects: [NINearbyObject]
    ) {
        // Match by discovery token, normalize optional values, and publish.
    }

    func sessionWasSuspended(_ session: NISession) {
        // Mark the last snapshot stale and stop automatic actions.
    }

    func session(
        _ session: NISession,
        didInvalidateWith error: Error
    ) {
        // Publish a bounded invalidated state and recovery action.
    }
}
~~~

Delegate callbacks are not SwiftUI state. Normalize values on the coordinator’s queue and publish small Sendable snapshots to the MainActor.

## Measurement normalization

Normalize the framework object without inventing missing values:

~~~swift
func snapshot(
    from object: NINearbyObject,
    generation: Int
) -> SpatialSnapshot {
    SpatialSnapshot(
        id: UUID(),
        sessionGeneration: generation,
        peerTokenDescription: String(describing: object.discoveryToken),
        distanceMeters: object.distance,
        direction: object.direction,
        horizontalAngleRadians: object.horizontalAngle,
        verticalEstimate: String(describing: object.verticalDirectionEstimate),
        receivedAt: Date(),
        isStale: false
    )
}
~~~

Use a domain type for vertical estimates instead of the illustrative String in production. A nil distance or direction remains nil. The UI can provide a last-known snapshot with a stale flag, but must not label it current.

## Token and peer matching

A session can have multiple peers over its lifetime. Store:

~~~swift
struct PeerSpatialBinding: Sendable {
    let appPeerID: String
    let transportPeerID: String
    let discoveryToken: NIDiscoveryToken
    let sessionGeneration: Int
}
~~~

NIDiscoveryToken is secure-codable in the documented token-exchange path, but it is still temporary session material. Do not use a token as a long-term account key. Use an app-owned peer ID or authenticated transport relationship for identity.

## Background and Live Activity policy

Select one of these documented product policies:

| Policy | Route |
| --- | --- |
| Foreground only | Stop or suspend ranging when the scene backgrounds. |
| Paired accessory | Use a supported BLE-paired and connected accessory path. |
| Live Activity | Start the Live Activity as the app backgrounds and prove its freshness/system delivery. |
| Unsupported | Explain that spatial updates pause outside the foreground. |

The Uses Nearby Interaction background capability and a Live Activity preview do not prove a background ranging session after process termination. Test lock, background, suspension, relaunch, peer removal, and stale state on physical supported devices.

## Local AI and explicit action

The AI adapter should accept only typed spatial context:

~~~swift
struct SpatialProposalInput: Codable, Sendable {
    let peerLabel: String
    let distanceMeters: Float?
    let horizontalDirection: String?
    let sourceAgeSeconds: Double
    let capabilitySummary: String
    let limitation: String
}
~~~

The output is a proposal. Before applying it, validate current session generation, peer identity, source age, available direction/distance, user intent, and action authorization. Reject proposals that infer security, consent, identity, or safety from ranging.

## SwiftUI surface

Compose the UI from native semantics:

- peer selection list for transport candidates;
- status card for permission, exchange, capability, and session state;
- text distance and direction values;
- accessible direction description;
- Button for stop, refresh, and review;
- sheet/inspector for source and AI proposal;
- functional Liquid Glass group for related controls;
- standard-material or opaque fallback;
- stale and unavailable states that preserve recovery.

Keep the measurement result separate from a command or destination. If the app uses ranging to guide a person, the guidance remains a suggestion until the person performs the next explicit action.

## Cancellation and recovery

Cancel the transport and NISession together when the user stops:

- stop browsing/advertising;
- cancel pending token exchange;
- invalidate the NISession;
- increment the session generation;
- mark prior measurement stale;
- clear or retain the selected peer according to product policy;
- redact or discard temporary token material.

On userDidNotAllow, show Settings recovery. On unsupportedPlatform or incompatiblePeerDevice, show capability-specific guidance. On session suspension, wait for resumed callbacks before treating the route as ranging again.

## Evidence route

Collect evidence in this order:

1. signed target privacy/capability and platform matrix;
2. local and peer capability checks;
3. transport discovery and user selection;
4. token/configuration exchange;
5. Nearby Interaction permission;
6. two-device ranging updates;
7. missing direction/distance and stale behavior;
8. suspension/removal/invalidation;
9. accessibility and reduced-motion task completion;
10. background/system surface if claimed;
11. sustained energy and physical-device behavior;
12. archive, TestFlight, and release proof.

## Sources

- [Nearby Interaction](https://developer.apple.com/documentation/nearbyinteraction)
- [NISession](https://developer.apple.com/documentation/nearbyinteraction/nisession)
- [NISessionDelegate](https://developer.apple.com/documentation/nearbyinteraction/nisessiondelegate)
- [NIDiscoveryToken](https://developer.apple.com/documentation/nearbyinteraction/nidiscoverytoken)
- [NINearbyPeerConfiguration](https://developer.apple.com/documentation/nearbyinteraction/ninearbypeerconfiguration)
- [NINearbyAccessoryConfiguration](https://developer.apple.com/documentation/nearbyinteraction/ninearbyaccessoryconfiguration)
- [NINearbyObject](https://developer.apple.com/documentation/nearbyinteraction/ninearbyobject)
- [NISession device capabilities](https://developer.apple.com/documentation/nearbyinteraction/nisession/devicecapabilities)
- [Initiating and maintaining a session](https://developer.apple.com/documentation/nearbyinteraction/initiating-and-maintaining-a-session)
- [Discovering peers with Multipeer Connectivity](https://developer.apple.com/documentation/nearbyinteraction/discovering-peers-with-multipeer-connectivity)
- [Multipeer Connectivity](https://developer.apple.com/documentation/multipeerconnectivity)
- [Network Framework](https://developer.apple.com/documentation/network)
- [NSNearbyInteractionUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsnearbyinteractionusagedescription)
- [NSLocalNetworkUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nslocalnetworkusagedescription)
- [NSBonjourServices](https://developer.apple.com/documentation/bundleresources/information-property-list/nsbonjourservices)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
