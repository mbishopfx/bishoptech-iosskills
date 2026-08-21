# SwiftUI MultipeerConnectivity peer-session recipes

These recipes are route sketches for an iOS 26 target that must maintain or
prototype a MultipeerConnectivity adapter. The framework is deprecated in the
current Apple documentation; use the recipes to understand an existing route,
then compare it with Network Framework before starting new transport code.

The snippets deliberately keep domain state, identity, security, and user
approval outside the framework objects. Compile them in a target that includes
the required framework, Info.plist privacy keys, and physical-device proof.

## 1. Restore one stable local peer ID

Apple documents MCPeerID as secure-codable and warns that creating a new ID for
the same display name produces a new peer identity. Archive the local object;
never reconstruct a remote peer from its display name.

~~~swift
import Foundation
import MultipeerConnectivity

enum PeerIdentityStore {
    private static let key = "mc.local-peer-id"

    static func loadOrCreate(
        displayName: String,
        defaults: UserDefaults = .standard
    ) throws -> MCPeerID {
        if let data = defaults.data(forKey: key),
           let restored = try? NSKeyedUnarchiver.unarchivedObject(
            ofClass: MCPeerID.self,
            from: data
           ) {
            return restored
        }

        let peer = MCPeerID(displayName: displayName)
        let data = try NSKeyedArchiver.archivedData(
            withRootObject: peer,
            requiringSecureCoding: true
        )
        defaults.set(data, forKey: key)
        return peer
    }
}
~~~

Treat a decode failure as a deliberate identity reset. If a server or pairing
record binds the old peer identity, repair that binding instead of silently
pretending that the new object is the same device.

## 2. Create a session with an explicit encryption policy

Do not let the convenience initializer hide the legacy adapter’s security
decision.

~~~swift
import MultipeerConnectivity

func makeEncryptedSession(peer: MCPeerID) -> MCSession {
    MCSession(
        peer: peer,
        securityIdentity: nil,
        encryptionPreference: .required
    )
}
~~~

The peer matrix must include what happens when a remote peer cannot satisfy the
chosen preference. A connected session is not a complete application-level
authentication result.

## 3. Translate session delegate callbacks into bounded events

The framework calls its delegate on a private queue. This adapter emits small
events; a main-actor store can then update SwiftUI explicitly.

~~~swift
import Foundation
import MultipeerConnectivity

enum SessionEvent {
    case state(MCPeerID, MCSessionState)
    case data(Data, MCPeerID)
    case resourceStarted(String, MCPeerID, Progress)
    case resourceFinished(String, MCPeerID, URL?, Error?)
}

final class SessionDelegateAdapter: NSObject, MCSessionDelegate {
    let onEvent: (SessionEvent) -> Void

    init(onEvent: @escaping (SessionEvent) -> Void) {
        self.onEvent = onEvent
    }

    func session(
        _ session: MCSession,
        peer peerID: MCPeerID,
        didChange state: MCSessionState
    ) {
        onEvent(.state(peerID, state))
    }

    func session(
        _ session: MCSession,
        didReceive data: Data,
        fromPeer peerID: MCPeerID
    ) {
        guard data.count <= 256 * 1024 else { return }
        onEvent(.data(data, peerID))
    }

    func session(
        _ session: MCSession,
        didReceive stream: InputStream,
        withName streamName: String,
        fromPeer peerID: MCPeerID
    ) {
        stream.close()
    }

    func session(
        _ session: MCSession,
        didStartReceivingResourceWithName resourceName: String,
        fromPeer peerID: MCPeerID,
        with progress: Progress
    ) {
        onEvent(.resourceStarted(resourceName, peerID, progress))
    }

    func session(
        _ session: MCSession,
        didFinishReceivingResourceWithName resourceName: String,
        fromPeer peerID: MCPeerID,
        at localURL: URL?,
        withError error: Error?
    ) {
        onEvent(.resourceFinished(resourceName, peerID, localURL, error))
    }
}
~~~

The stream callback is only a seam; a production route must own a stream pump,
frame bytes, and close it through the same cancellation coordinator.

## 4. Validate an MC service type before constructing discovery objects

The framework applies Bonjour-style restrictions. Keep validation near product
configuration so a malformed service type does not fail at runtime.

~~~swift
import Foundation

func isValidMCServiceType(_ value: String) -> Bool {
    let scalars = Array(value.unicodeScalars)
    guard (1...15).contains(scalars.count),
          let first = scalars.first,
          let last = scalars.last,
          first.value != 45,
          last.value != 45 else {
        return false
    }

    var hasLetter = false
    var previousWasHyphen = false
    for scalar in scalars {
        let isLetter = (97...122).contains(scalar.value)
        let isNumber = (48...57).contains(scalar.value)
        let isHyphen = scalar.value == 45
        guard isLetter || isNumber || isHyphen else { return false }
        guard !(isHyphen && previousWasHyphen) else { return false }
        hasLetter = hasLetter || isLetter
        previousWasHyphen = isHyphen
    }
    return hasLetter
}
~~~

This checks the documented syntax, not whether a service is product-unique.

## 5. Start an advertiser with bounded discovery metadata

Keep discoveryInfo small, versioned, and non-sensitive.

~~~swift
import MultipeerConnectivity

final class AdvertiserController: NSObject, MCNearbyServiceAdvertiserDelegate {
    private let session: MCSession
    private let advertiser: MCNearbyServiceAdvertiser

    init(peer: MCPeerID, serviceType: String, session: MCSession) {
        self.session = session
        advertiser = MCNearbyServiceAdvertiser(
            peer: peer,
            discoveryInfo: ["v": "2", "role": "sender"],
            serviceType: serviceType
        )
        super.init()
        advertiser.delegate = self
    }

    func start() {
        advertiser.startAdvertisingPeer()
    }

    func stop() {
        advertiser.stopAdvertisingPeer()
    }

    func advertiser(
        _ advertiser: MCNearbyServiceAdvertiser,
        didReceiveInvitationFromPeer peerID: MCPeerID,
        withContext context: Data?,
        invitationHandler: @escaping (Bool, MCSession?) -> Void
    ) {
        let boundedContext = context.flatMap { $0.count <= 4096 ? $0 : nil }
        let accepted = boundedContext != nil
        invitationHandler(accepted, accepted ? session : nil)
    }
}
~~~

The example uses a deterministic fixture decision. A product should replace it
with a user-mediated approval state and resolve the handler exactly once.

## 6. Browse and invite a selected candidate

The browser sees discovery metadata, not a trusted identity.

~~~swift
import Foundation
import MultipeerConnectivity

final class BrowserController: NSObject, MCNearbyServiceBrowserDelegate {
    private let session: MCSession
    private let serviceBrowser: MCNearbyServiceBrowser
    private(set) var candidates: [MCPeerID] = []

    init(peer: MCPeerID, serviceType: String, session: MCSession) {
        self.session = session
        serviceBrowser = MCNearbyServiceBrowser(
            peer: peer,
            serviceType: serviceType
        )
        super.init()
        serviceBrowser.delegate = self
    }

    func start() {
        serviceBrowser.startBrowsingForPeers()
    }

    func stop() {
        serviceBrowser.stopBrowsingForPeers()
    }

    func invite(_ peer: MCPeerID, context: Data) {
        guard candidates.contains(where: { $0 == peer }) else { return }
        serviceBrowser.invitePeer(
            peer,
            to: session,
            withContext: context,
            timeout: 30
        )
    }

    func browser(
        _ browser: MCNearbyServiceBrowser,
        foundPeer peerID: MCPeerID,
        withDiscoveryInfo info: [String: String]?
    ) {
        guard !candidates.contains(where: { $0 == peerID }) else { return }
        candidates.append(peerID)
    }

    func browser(
        _ browser: MCNearbyServiceBrowser,
        lostPeer peerID: MCPeerID
    ) {
        candidates.removeAll { $0 == peerID }
    }
}
~~~

In an app, publish candidates through a main-actor model and remove selection
when the candidate’s discovery epoch ends.

## 7. Send a bounded versioned message

Reliable and unreliable modes are transport choices, not domain semantics.

~~~swift
import Foundation
import MultipeerConnectivity

struct PeerEnvelope: Codable {
    let schemaVersion: Int
    let transferID: UUID
    let sourceRevision: UInt64
    let kind: String
    let payload: Data
}

enum PeerSendError: Error {
    case payloadTooLarge
}

func sendEnvelope(
    _ envelope: PeerEnvelope,
    to peers: [MCPeerID],
    using session: MCSession,
    mode: MCSessionSendDataMode = .reliable
) throws {
    let data = try JSONEncoder().encode(envelope)
    guard data.count <= 256 * 1024 else { throw PeerSendError.payloadTooLarge }
    guard !peers.isEmpty else { return }
    try session.send(data, toPeers: peers, with: mode)
}
~~~

The size is an app policy. A production protocol should add an application
receipt and idempotent reducer; a successful send call is not a remote commit.

## 8. Send a resource with progress and completion state

Use resources for files instead of putting unbounded bytes in a message.

~~~swift
import Foundation
import MultipeerConnectivity

@discardableResult
func sendResource(
    at fileURL: URL,
    to peer: MCPeerID,
    using session: MCSession,
    completion: @escaping (Result<Void, Error>) -> Void
) -> Progress? {
    guard session.connectedPeers.contains(where: { $0 == peer }) else {
        completion(.failure(CocoaError(.fileNoSuchFile)))
        return nil
    }

    return session.sendResource(
        at: fileURL,
        withName: fileURL.lastPathComponent,
        toPeer: peer
    ) { error in
        if let error {
            completion(.failure(error))
        } else {
            completion(.success(()))
        }
    }
}
~~~

Retain the returned Progress only as long as the transfer is active. The
recipient still needs to validate the received file and distinguish delivery
from domain application.

## 9. Move and validate a received resource

Apple gives the receiver a temporary URL. Move or open it before the receive
callback returns, after checking the expected transfer metadata.

~~~swift
import Foundation

enum ResourceImportError: Error {
    case missingURL
    case unexpectedType
}

func importReceivedResource(
    localURL: URL?,
    expectedExtension: String,
    destination: URL
) throws {
    guard let localURL else { throw ResourceImportError.missingURL }
    guard localURL.pathExtension == expectedExtension else {
        throw ResourceImportError.unexpectedType
    }

    let directory = destination.deletingLastPathComponent()
    try FileManager.default.createDirectory(
        at: directory,
        withIntermediateDirectories: true
    )
    if FileManager.default.fileExists(atPath: destination.path) {
        try FileManager.default.removeItem(at: destination)
    }
    try FileManager.default.moveItem(at: localURL, to: destination)
}
~~~

Use a content hash, byte limit, Uniform Type Identifier check, and current
session/transfer revision before importing real content. The replacement logic
in this fixture is not a conflict policy.

## 10. Open a framed output stream

A stream is a byte channel. Configure scheduling and framing explicitly.

~~~swift
import Foundation
import MultipeerConnectivity

final class OutputStreamPump: NSObject, StreamDelegate {
    private let stream: OutputStream

    init(stream: OutputStream) {
        self.stream = stream
    }

    func open(on runLoop: RunLoop = .current) {
        stream.delegate = self
        stream.schedule(in: runLoop, forMode: .default)
        stream.open()
    }

    func close() {
        stream.close()
        stream.remove(from: .current, forMode: .default)
    }

    func write(frame: Data) -> Bool {
        var bytes = frame
        return bytes.withUnsafeMutableBytes { rawBuffer in
            guard let baseAddress = rawBuffer.baseAddress else { return false }
            let written = stream.write(
                baseAddress.assumingMemoryBound(to: UInt8.self),
                maxLength: rawBuffer.count
            )
            return written == rawBuffer.count
        }
    }

    func stream(
        _ aStream: Stream,
        handle eventCode: Stream.Event
    ) {}
}

func makeOutputStream(
    session: MCSession,
    peer: MCPeerID,
    name: String
) throws -> OutputStreamPump {
    let output = try session.startStream(withName: name, toPeer: peer)
    let pump = OutputStreamPump(stream: output)
    pump.open()
    return pump
}
~~~

The example writes one frame only when the stream accepts the whole buffer.
Production code must handle partial writes, `.hasSpaceAvailable`, errors, and a
length-prefixed framing parser on the other side.

## 11. Keep SwiftUI state on the main actor

Delegate callbacks must hop to the UI owner. Keep framework objects out of the
view body and make cancellation explicit.

~~~swift
import Combine
import Foundation
import MultipeerConnectivity
import SwiftUI

enum MainActorSessionEvent {
    case state(MCSessionState)
    case data(Data)
}

final class MainActorSessionBridge: NSObject, MCSessionDelegate {
    let onEvent: (MainActorSessionEvent) -> Void

    init(onEvent: @escaping (MainActorSessionEvent) -> Void) {
        self.onEvent = onEvent
    }

    func session(
        _ session: MCSession,
        peer peerID: MCPeerID,
        didChange state: MCSessionState
    ) {
        onEvent(.state(state))
    }

    func session(
        _ session: MCSession,
        didReceive data: Data,
        fromPeer peerID: MCPeerID
    ) {
        onEvent(.data(data))
    }

    func session(
        _ session: MCSession,
        didReceive stream: InputStream,
        withName streamName: String,
        fromPeer peerID: MCPeerID
    ) {
        stream.close()
    }

    func session(
        _ session: MCSession,
        didStartReceivingResourceWithName resourceName: String,
        fromPeer peerID: MCPeerID,
        with progress: Progress
    ) {}

    func session(
        _ session: MCSession,
        didFinishReceivingResourceWithName resourceName: String,
        fromPeer peerID: MCPeerID,
        at localURL: URL?,
        withError error: Error?
    ) {}
}

@MainActor
final class NearbySessionStore: ObservableObject {
    enum Phase: Equatable {
        case idle
        case browsing
        case connecting
        case ready
        case disconnected
        case failed(String)
    }

    @Published private(set) var phase: Phase = .idle
    @Published private(set) var peers: [MCPeerID] = []
    private var session: MCSession?
    private var delegate: MainActorSessionBridge?

    func start(peer: MCPeerID) {
        let session = MCSession(
            peer: peer,
            securityIdentity: nil,
            encryptionPreference: .required
        )
        let adapter = MainActorSessionBridge { [weak self] event in
            Task { @MainActor [weak self] in
                self?.apply(event)
            }
        }
        session.delegate = adapter
        self.session = session
        delegate = adapter
        phase = .browsing
    }

    func stop() {
        session?.disconnect()
        session = nil
        delegate = nil
        peers.removeAll()
        phase = .idle
    }

    private func apply(_ event: MainActorSessionEvent) {
        switch event {
        case let .state(state):
            phase = state == .connected ? .ready : .disconnected
        case let .data(data):
            guard !data.isEmpty else { phase = .failed("Empty message") ; return }
        }
    }
}
~~~

The store is a UI owner, not the domain reducer. Move parsed envelopes into a
separate deterministic reducer before committing a file, record, or command.

## 12. Compose a native peer list with a bounded glass action group

Use semantic controls and keep the glass treatment functional.

~~~swift
import MultipeerConnectivity
import SwiftUI

struct PeerListView: View {
    let peers: [MCPeerID]
    let onSelect: (MCPeerID) -> Void
    let onStop: () -> Void

    var body: some View {
        NavigationStack {
            List {
                Section("Nearby devices") {
                    ForEach(peers, id: \.self) { peer in
                        Button {
                            onSelect(peer)
                        } label: {
                            Label(peer.displayName, systemImage: "iphone")
                        }
                        .accessibilityValue("Discovered nearby device")
                    }
                }
            }
            .navigationTitle("Nearby")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Stop", action: onStop)
                }
            }
            .safeAreaInset(edge: .bottom) {
                Text("Choose a device to review an invitation")
                    .font(.footnote)
                    .padding(.horizontal)
                    .padding(.vertical, 10)
                    .glassEffect(.regular, in: .rect(cornerRadius: 18))
                    .padding()
            }
        }
    }
}
~~~

The glass footer is an action/status group, not the peer identity surface. Add
explicit phase text and a non-glass fallback in the product’s full design
system.

## 13. Model a source-bound collaboration proposal

Foundation Models output should remain typed, bounded, and subordinate to the
current candidate/session snapshot.

~~~swift
import Foundation
import FoundationModels

@Generable
struct CollaborationProposal {
    @Guide(description: "The allowlisted local peer correlation key.")
    let peerCorrelation: String

    @Guide(description: "A short explanation based only on the supplied snapshot.")
    let reason: String

    @Guide(description: "A low-risk action: inspect, invite, or prepareTransfer.")
    let action: String
}

struct ProposalSnapshot {
    let peerCorrelation: String
    let discoveryRevision: UInt64
    let sessionEpoch: UInt64
}

enum ProposalError: Error {
    case unavailable
    case stale
    case unknownPeer
    case unsupportedAction
}

func validateProposal(
    _ proposal: CollaborationProposal,
    snapshot: ProposalSnapshot,
    allowedPeers: Set<String>,
    currentRevision: UInt64,
    currentEpoch: UInt64
) throws -> CollaborationProposal {
    guard proposal.peerCorrelation == snapshot.peerCorrelation,
          allowedPeers.contains(proposal.peerCorrelation),
          currentRevision == snapshot.discoveryRevision,
          currentEpoch == snapshot.sessionEpoch else {
        throw ProposalError.stale
    }
    guard ["inspect", "invite", "prepareTransfer"].contains(proposal.action) else {
        throw ProposalError.unsupportedAction
    }
    guard !proposal.reason.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
        throw ProposalError.unknownPeer
    }
    return proposal
}
~~~

The final user action still performs the deterministic permission, transport,
encryption, and domain checks. Do not expose framework objects or invitation
closures to the model.

## 14. Record a physical two-device evidence packet

Keep proof structured and redacted.

~~~swift
import Foundation

struct PeerEvidencePacket: Codable {
    let build: String
    let deviceA: String
    let deviceB: String
    let localNetworkPermission: String
    let serviceType: String
    let invitationDecision: String
    let encryptionPolicy: String
    let sessionStates: [String]
    let transferResult: String
    let accessibilityResult: String
    let artifactPath: String?
}

func validateEvidence(_ packet: PeerEvidencePacket) -> Bool {
    !packet.build.isEmpty &&
    packet.deviceA != packet.deviceB &&
    packet.localNetworkPermission == "allowed" &&
    packet.invitationDecision == "accepted" &&
    packet.encryptionPolicy == "required" &&
    packet.sessionStates.contains("connected") &&
    packet.transferResult == "applied" &&
    packet.accessibilityResult == "passed"
}
~~~

The packet is a record of a named test, not proof that every device or network
will behave identically. Never put peer names, IP addresses, file contents, or
credentials in the evidence artifact.

## Sources

- [Multipeer Connectivity](https://developer.apple.com/documentation/multipeerconnectivity)
- [MCPeerID](https://developer.apple.com/documentation/multipeerconnectivity/mcpeerid)
- [MCSession](https://developer.apple.com/documentation/multipeerconnectivity/mcsession)
- [MCSessionDelegate](https://developer.apple.com/documentation/multipeerconnectivity/mcsessiondelegate)
- [MCSessionSendDataMode](https://developer.apple.com/documentation/multipeerconnectivity/mcsessionsenddatamode)
- [MCNearbyServiceAdvertiser](https://developer.apple.com/documentation/multipeerconnectivity/mcnearbyserviceadvertiser)
- [MCNearbyServiceBrowser](https://developer.apple.com/documentation/multipeerconnectivity/mcnearbyservicebrowser)
- [Moving from Multipeer Connectivity to Network framework](https://developer.apple.com/documentation/technotes/tn3213-moving-from-multipeer-connectivity-to-network-framework)
- [Understanding local network privacy](https://developer.apple.com/documentation/technotes/tn3179-understanding-local-network-privacy)
- [Privacy - Local Network Usage Description](https://developer.apple.com/documentation/bundleresources/information_property_list/nslocalnetworkusagedescription)
- [Privacy - Bonjour Services](https://developer.apple.com/documentation/bundleresources/information_property_list/nsbonjourservices)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
