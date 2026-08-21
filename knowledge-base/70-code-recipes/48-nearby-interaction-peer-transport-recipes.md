# Nearby Interaction and peer transport code recipes

These are compile-oriented route sketches for a selected iOS target. They are not compiled in this documentation-only workspace and do not prove UWB/device support, local-network authorization, identity, transport security, physical direction/distance, background behavior, throughput, accessibility, or release readiness. Verify current SDK signatures and platform availability in Xcode.

## Recipe 1: run a Nearby Interaction peer session

Exchange the peer’s discovery token through an approved transport, then create a peer configuration:

~~~swift
import NearbyInteraction

final class NearbyPeerSession: NSObject, NISessionDelegate {
    private let session = NISession()

    func start(with peerToken: NIDiscoveryToken) {
        guard NISession.deviceCapabilities.supportsPreciseDistanceMeasurement else {
            return
        }

        let configuration = NINearbyPeerConfiguration(peerToken: peerToken)
        session.delegate = self
        session.run(configuration)
    }

    func session(
        _ session: NISession,
        didUpdate nearbyObjects: [NINearbyObject]
    ) {
        for object in nearbyObjects {
            let distance = object.distance
            let direction = object.direction
            // Project freshness/distance/direction to the UI.
            _ = (distance, direction)
        }
    }

    func session(
        _ session: NISession,
        didRemove nearbyObjects: [NINearbyObject],
        reason: NINearbyObjectRemovalReason
    ) {
        // Mark the target unavailable or restart only through an explicit policy.
        _ = reason
    }

    func sessionWasSuspended(_ session: NISession) {
        // Show a paused/stale state.
    }

    func sessionSuspensionEnded(_ session: NISession) {
        // Reconcile and resume only if the task is still active.
    }

    func session(
        _ session: NISession,
        didInvalidateWith reason: NISessionInvalidationReason
    ) {
        // Explain invalidation and release session-scoped token state.
        _ = reason
    }
}
~~~

The capability property, delegate methods, and availability must be checked in the current SDK. One session represents one nearby object; create a separate policy/session for multiple targets.

## Recipe 2: exchange peer discovery tokens

Use an app-owned versioned message over the selected transport:

~~~swift
struct NearbyHello: Codable, Sendable {
    var protocolVersion: Int
    var sessionID: UUID
    var displayName: String
    var capabilities: [String]
}

struct NearbyTokenMessage: Codable, Sendable {
    var sessionID: UUID
    var tokenData: Data
}

func makeTokenMessage(
    sessionID: UUID,
    token: NIDiscoveryToken
) throws -> NearbyTokenMessage {
    let data = try NSKeyedArchiver.archivedData(
        withRootObject: token,
        requiringSecureCoding: true
    )
    return NearbyTokenMessage(sessionID: sessionID, tokenData: data)
}
~~~

Validate message size, protocol version, session ID, peer selection, and authentication before decoding or running the NI configuration. Discovery token data is session-scoped input, not an account identity. Use the current secure coding/archive route supported by the target.

## Recipe 3: browse local services with Network Framework

Use Network Framework for new local service discovery:

~~~swift
import Network

final class LocalServiceBrowser {
    private var browser: NWBrowser?

    func start() {
        let descriptor = NWBrowser.Descriptor.bonjour(
            type: "_example-nearby._tcp",
            domain: nil
        )
        let parameters = NWParameters.tcp
        let browser = NWBrowser(for: descriptor, using: parameters)
        browser.stateUpdateHandler = { state in
            // Handle waiting, ready, failed, and cancelled states.
            _ = state
        }
        browser.browseResultsChangedHandler = { results, changes in
            // Validate metadata/candidates before showing them as selectable.
            _ = (results, changes)
        }
        browser.start(queue: .main)
        self.browser = browser
    }

    func stop() {
        browser?.cancel()
        browser = nil
    }
}
~~~

Add NSLocalNetworkUsageDescription and NSBonjourServices when this route requires them. A browse result is untrusted candidate metadata. Do not connect or transfer based only on signal strength or display name.

## Recipe 4: connect with NWConnection and frame messages

Separate transport readiness from protocol/domain readiness:

~~~swift
import Network

final class LocalConnection {
    private var connection: NWConnection?

    func connect(to endpoint: NWEndpoint) {
        let connection = NWConnection(to: endpoint, using: .tcp)
        connection.stateUpdateHandler = { state in
            switch state {
            case .ready:
                // Send an authenticated Hello, not a domain side effect.
                break
            case .failed(let error):
                _ = error
            case .waiting(let error):
                _ = error
            default:
                break
            }
        }
        connection.start(queue: .main)
        self.connection = connection
    }

    func cancel() {
        connection?.cancel()
        connection = nil
    }
}
~~~

Implement length/schema/revision framing, partial-read handling, bounded send queues, authentication/encryption, cancellation, path changes, reconnect, and duplicate/out-of-order policy in the selected target. A ready connection is not proof that the intended peer accepted a transfer.

## Recipe 5: accept a legacy Multipeer invitation

Keep this behind an adapter for existing products. Apple’s current MCSession documentation marks the session route deprecated for new work and recommends Network Framework.

~~~swift
import MultipeerConnectivity

final class LegacyPeerRoute: NSObject,
    MCNearbyServiceAdvertiserDelegate,
    MCSessionDelegate {
    private let peer = MCPeerID(displayName: UIDevice.current.name)
    private lazy var session = MCSession(peer: peer)
    private var advertiser: MCNearbyServiceAdvertiser?

    func start() {
        session.delegate = self
        let advertiser = MCNearbyServiceAdvertiser(
            peer: peer,
            discoveryInfo: ["protocol": "1"],
            serviceType: "example-nearby"
        )
        advertiser.delegate = self
        advertiser.startAdvertisingPeer()
        self.advertiser = advertiser
    }

    func advertiser(
        _ advertiser: MCNearbyServiceAdvertiser,
        didReceiveInvitationFromPeer peerID: MCPeerID,
        withContext context: Data?,
        invitationHandler: @escaping (Bool, MCSession?) -> Void
    ) {
        // Validate the context and ask the person before accepting.
        _ = (advertiser, peerID, context)
        invitationHandler(false, nil)
    }
}
~~~

Fill in every required MCSessionDelegate callback in the target. Stop/restart advertising according to the product lifecycle and reestablish sessions after the framework disconnects them during backgrounding.

## Recipe 6: model an idempotent message

~~~swift
struct PeerMessage: Codable, Sendable {
    var protocolVersion: Int
    var sessionID: UUID
    var senderID: String
    var sequence: UInt64
    var revision: UInt64
    var kind: Kind
    var payload: Data
    var requiresConfirmation: Bool

    enum Kind: String, Codable, Sendable {
        case hello
        case ready
        case preview
        case commitRequest
        case commitResult
        case resync
    }
}

struct AppliedMessageSet {
    var highestRevision: UInt64 = 0
    var appliedSequences: Set<UInt64> = []

    mutating func shouldApply(_ message: PeerMessage) -> Bool {
        guard message.revision >= highestRevision else { return false }
        guard !appliedSequences.contains(message.sequence) else { return false }
        appliedSequences.insert(message.sequence)
        highestRevision = max(highestRevision, message.revision)
        return true
    }
}
~~~

Keep payload decoding separate from applying a side effect. Require explicit confirmation for a commitRequest and send a result that identifies the applied revision.

## Recipe 7: expose a spatial fallback

The UI should not require direction to remain available:

~~~swift
enum NearbyGuidance {
    case searching
    case point(directionDescription: String)
    case distanceOnly(meters: Double?)
    case obstructed
    case unavailable
    case complete
}

func guidance(
    distance: Double?,
    directionAvailable: Bool,
    isObstructed: Bool
) -> NearbyGuidance {
    if isObstructed { return .obstructed }
    if directionAvailable {
        return .point(directionDescription: "Use the on-screen direction")
    }
    return .distanceOnly(meters: distance)
}
~~~

The real UI should add visible text, VoiceOver values, audio/haptic alternatives, Reduce Motion behavior, and a manual target/action. Do not display a confident arrow when the direction signal is unavailable.

## Recipe 8: bound an AI nearby proposal

~~~swift
struct NearbyAIContext: Sendable {
    var selectedCandidateID: String
    var transportReady: Bool
    var directionAvailable: Bool
    var distanceMeters: Double?
    var sessionRevision: UInt64
}

struct NearbyProposal: Sendable {
    var nextStep: String
    var targetID: String
    var explanation: String
    var sourceRevision: UInt64
    var requiresConfirmation: Bool
}

func canApply(
    _ proposal: NearbyProposal,
    context: NearbyAIContext
) -> Bool {
    proposal.requiresConfirmation
        && proposal.targetID == context.selectedCandidateID
        && proposal.sourceRevision == context.sessionRevision
        && context.transportReady
}
~~~

The proposal may suggest “move to a clearer position” or rank the selected candidate. It must not infer a person’s identity, grant consent, or transfer content without the product’s explicit confirmation and protocol authorization.

## Recipe 9: fixture lifecycle and transport failure

~~~swift
enum NearbyFixture {
    case unsupportedDevice
    case noCandidates
    case candidateSelected
    case wrongPeer
    case staleToken
    case transportReady
    case directionUnavailable
    case obstructed
    case peerLeft
    case backgroundDisconnect
    case duplicateMessage
    case aiUnavailable
}

func reduce(_ fixture: NearbyFixture) -> NearbyRouteState {
    fatalError("Implement in the selected app target")
}
~~~

Exercise no-permission, candidate rejection, wrong peer, stale token, transport timeout, NI suspension, direction loss, obstruction, background disconnect, duplicate revision, and manual fallback before a physical two-device run.

## Sources

- [Nearby Interaction](https://developer.apple.com/documentation/nearbyinteraction)
- [NISession](https://developer.apple.com/documentation/nearbyinteraction/nisession)
- [NINearbyPeerConfiguration](https://developer.apple.com/documentation/nearbyinteraction/ninearbypeerconfiguration)
- [NINearbyAccessoryConfiguration](https://developer.apple.com/documentation/nearbyinteraction/ninearbyaccessoryconfiguration)
- [Initiating and maintaining a session](https://developer.apple.com/documentation/nearbyinteraction/initiating-and-maintaining-a-session)
- [Network](https://developer.apple.com/documentation/network)
- [NWBrowser](https://developer.apple.com/documentation/network/nwbrowser)
- [NWConnection](https://developer.apple.com/documentation/network/nwconnection)
- [NWListener](https://developer.apple.com/documentation/network/nwlistener)
- [Multipeer Connectivity](https://developer.apple.com/documentation/multipeerconnectivity)
- [MCSession](https://developer.apple.com/documentation/multipeerconnectivity/mcsession)
- [MCNearbyServiceAdvertiser](https://developer.apple.com/documentation/multipeerconnectivity/mcnearbyserviceadvertiser)
- [Nearby interactions HIG](https://developer.apple.com/design/human-interface-guidelines/nearby-interactions/)
- [Accessibility HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
