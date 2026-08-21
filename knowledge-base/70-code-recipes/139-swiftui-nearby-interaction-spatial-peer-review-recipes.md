# SwiftUI Nearby Interaction and spatial-peer review recipes

These recipes are compile-oriented sketches for a named iOS target. They keep peer discovery, token exchange, Nearby Interaction, transport state, spatial measurements, SwiftUI, local AI, and physical actions separate. Run them on the selected SDK and physical supported devices before making a claim.

Pairs with [SwiftUI Nearby Interaction and spatial-peer review](../42-framework-deep-dives/96-swiftui-nearby-interaction-spatial-peer-review.md), [the spatial-peer route](../50-capability-recipes/127-swiftui-nearby-interaction-spatial-peer-review-route.md), and [the proof matrix](../60-verification/121-swiftui-nearby-interaction-spatial-peer-review-proof-matrix.md).

## Recipe 1: model spatial states

~~~swift
enum SpatialState {
    case unsupported(String)
    case discovering
    case candidate(String)
    case exchanging
    case waitingForPermission
    case ranging
    case reported(SpatialSnapshot)
    case stale(SpatialSnapshot)
    case suspended
    case invalidated(String)
}

struct SpatialSnapshot: Identifiable, Sendable {
    let id: UUID
    let generation: Int
    let distanceMeters: Float?
    let direction: SIMD3<Float>?
    let horizontalAngle: Float?
    let receivedAt: Date
    let limitation: String
}
~~~

An optional distance or direction must remain optional. A stale snapshot must carry a stale state even if it still has a numeric value.

## Recipe 2: check local and peer capabilities

~~~swift
import NearbyInteraction

func supportsRequiredFeature(
    peerToken: NIDiscoveryToken
) -> Bool {
    let local = NISession.deviceCapabilities
    let peer = peerToken.deviceCapabilities

    guard local.supportsPreciseDistanceMeasurement else {
        return false
    }
    return peer.supportsPreciseDistanceMeasurement
}
~~~

Use the exact capability properties required by the selected SDK and product. Check direction separately from precise distance and gate extended distance on both OS and device support.

## Recipe 3: own the session

~~~swift
final class NearbyCoordinator: NSObject, NISessionDelegate {
    let delegateQueue = DispatchQueue(
        label: "com.example.app.nearby-session",
        qos: .userInitiated
    )

    private(set) var session: NISession?
    private var generation = 0

    func run(peerToken: NIDiscoveryToken) throws {
        guard supportsRequiredFeature(peerToken: peerToken) else {
            throw SpatialError.unsupported
        }

        generation += 1
        let session = NISession()
        session.delegate = self
        session.delegateQueue = delegateQueue
        self.session = session

        let configuration = NINearbyPeerConfiguration(
            peerToken: peerToken
        )
        session.run(configuration)
    }

    func stop() {
        generation += 1
        session?.invalidate()
        session = nil
    }

    func sessionDidStartRunning(_ session: NISession) {
        // Publish a configured/ranging snapshot.
    }

    func session(
        _ session: NISession,
        didUpdate nearbyObjects: [NINearbyObject]
    ) {
        // Match by discovery token and publish typed optional values.
    }

    func sessionWasSuspended(_ session: NISession) {
        // Mark the last result stale.
    }

    func session(
        _ session: NISession,
        didInvalidateWith error: Error
    ) {
        // Publish a bounded error and recovery action.
    }
}
~~~

Keep the delegate queue and MainActor UI boundary explicit. When a new generation begins, discard old callbacks.

## Recipe 4: exchange tokens over a selected transport

~~~swift
func archiveToken(_ token: NIDiscoveryToken) throws -> Data {
    try NSKeyedArchiver.archivedData(
        withRootObject: token,
        requiringSecureCoding: true
    )
}

func unarchiveToken(_ data: Data) throws -> NIDiscoveryToken {
    try NSKeyedUnarchiver.unarchivedObject(
        ofClass: NIDiscoveryToken.self,
        from: data
    ) ?? { throw SpatialError.invalidToken }()
}
~~~

The archive is sent over a separate, selected transport. The transport must authenticate or bind the peer according to the product’s identity requirements. A nearby invitation or successful data connection is not automatically user consent or product identity.

For local-network discovery, configure the local-network privacy and Bonjour services required by the chosen transport. For new work, evaluate Network Framework alongside the Multipeer Connectivity sample route and record the decision.

## Recipe 5: normalize nearby-object updates

~~~swift
func makeSnapshot(
    object: NINearbyObject,
    generation: Int
) -> SpatialSnapshot {
    let limitation: String
    if object.distance == nil && object.direction == nil {
        limitation = "Distance and direction unavailable."
    } else if object.direction == nil {
        limitation = "Direction unavailable."
    } else if object.distance == nil {
        limitation = "Distance unavailable."
    } else {
        limitation = "Relative measurement; not secure identity."
    }

    return SpatialSnapshot(
        id: UUID(),
        generation: generation,
        distanceMeters: object.distance,
        direction: object.direction,
        horizontalAngle: object.horizontalAngle,
        receivedAt: Date(),
        limitation: limitation
    )
}
~~~

Do not convert nil to zero, straight ahead, or the last current value. A last-known value can be displayed only with an explicit stale state and source age.

## Recipe 6: bind a peer token to the configuration

~~~swift
struct PeerBinding: Sendable {
    let appPeerID: String
    let transportPeerID: String
    let peerToken: NIDiscoveryToken
    let generation: Int
}

func matches(
    object: NINearbyObject,
    binding: PeerBinding
) -> Bool {
    object.discoveryToken == binding.peerToken
}
~~~

Use the configuration’s peer token or accessory discovery token to match updates. Do not match by array index, display name, RSSI, or the most recent callback.

## Recipe 7: publish to SwiftUI with a generation gate

~~~swift
@MainActor
final class SpatialStore: ObservableObject {
    @Published private(set) var state: SpatialState = .unsupported(
        "Nearby Interaction is not ready."
    )

    private var generation = 0

    func begin() -> Int {
        generation += 1
        state = .ranging
        return generation
    }

    func publish(
        _ snapshot: SpatialSnapshot,
        generation: Int
    ) {
        guard generation == self.generation else { return }
        state = .reported(snapshot)
    }

    func stale(generation: Int) {
        guard generation == self.generation else { return }
        if case let .reported(snapshot) = state {
            state = .stale(snapshot)
        }
    }
}
~~~

The generation gate is a product stale-result guard. It does not replace NISession invalidation or transport cleanup.

## Recipe 8: make a local AI proposal

~~~swift
struct SpatialProposalInput: Codable, Sendable {
    let peerLabel: String
    let distanceMeters: Float?
    let directionText: String?
    let sourceAgeSeconds: Double
    let limitation: String
}

struct SpatialProposal: Codable, Sendable {
    let wording: String
    let requestedAction: String?
    let sourceGeneration: Int
    let warnings: [String]
}
~~~

Pass only typed, redacted context. Reject a proposal when its source generation is no longer current, when it assumes a missing measurement, or when it asks for a security-sensitive or physical action without a separate authorization and confirmation path.

## Recipe 9: create a native status group

~~~swift
struct SpatialStatusView: View {
    let stateLabel: String
    let detail: String
    let stop: () -> Void
    let review: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(stateLabel)
                .font(.headline)
            Text(detail)
                .font(.subheadline)
                .foregroundStyle(.secondary)

            HStack {
                Button("Stop ranging", action: stop)
                Button("Review", action: review)
            }
        }
        .padding()
        .glassEffect()
        .accessibilityElement(children: .contain)
    }
}
~~~

Apply Liquid Glass only when the selected target supports it and the group is a functional layer. Provide standard-material or opaque fallback and accessible text for all spatial values.

## Recipe 10: acceptance fixtures

~~~swift
struct SpatialFixture {
    let name: String
    let distance: Float?
    let hasDirection: Bool
    let expectedState: String
    let expectedLimitation: String
}

let fixtures = [
    SpatialFixture(
        name: "distance-only-peer",
        distance: 2.0,
        hasDirection: false,
        expectedState: "partial",
        expectedLimitation: "Direction unavailable."
    ),
    SpatialFixture(
        name: "no-measurement",
        distance: nil,
        hasDirection: false,
        expectedState: "acquiring",
        expectedLimitation: "Distance and direction unavailable."
    ),
    SpatialFixture(
        name: "stale-after-invalidation",
        distance: 1.4,
        hasDirection: true,
        expectedState: "stale",
        expectedLimitation: "Last measurement; session ended."
    )
]
~~~

Add fixtures for userDidNotAllow, unsupported platform, incompatible peer, delayed token exchange, two peers, peer removal, suspension, background stale state, VoiceOver, Dynamic Type, Reduce Motion, and reduced transparency. Mark which results come from physical devices.

## Sources

- [Nearby Interaction](https://developer.apple.com/documentation/nearbyinteraction)
- [NISession](https://developer.apple.com/documentation/nearbyinteraction/nisession)
- [NISessionDelegate](https://developer.apple.com/documentation/nearbyinteraction/nisessiondelegate)
- [NIDiscoveryToken](https://developer.apple.com/documentation/nearbyinteraction/nidiscoverytoken)
- [NINearbyPeerConfiguration](https://developer.apple.com/documentation/nearbyinteraction/ninearbypeerconfiguration)
- [NINearbyObject](https://developer.apple.com/documentation/nearbyinteraction/ninearbyobject)
- [Initiating and maintaining a session](https://developer.apple.com/documentation/nearbyinteraction/initiating-and-maintaining-a-session)
- [Discovering peers with Multipeer Connectivity](https://developer.apple.com/documentation/nearbyinteraction/discovering-peers-with-multipeer-connectivity)
- [Multipeer Connectivity](https://developer.apple.com/documentation/multipeerconnectivity)
- [Network Framework](https://developer.apple.com/documentation/network)
- [NSNearbyInteractionUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsnearbyinteractionusagedescription)
- [NSLocalNetworkUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nslocalnetworkusagedescription)
- [NSBonjourServices](https://developer.apple.com/documentation/bundleresources/information-property-list/nsbonjourservices)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
