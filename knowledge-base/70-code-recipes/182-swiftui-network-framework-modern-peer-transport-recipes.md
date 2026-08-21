# SwiftUI Network Framework modern peer-transport recipes

These snippets target the iOS 26 Network Framework API in the installed iOS
26.4 SDK. They are small, typechecked route examples rather than complete
application services. Add the product-owned permission, identity, pairing,
schema, cancellation, and physical-device proof around them.

The snippets intentionally use typed protocol stacks. Keep the transport
objects behind an actor or isolated coordinator before exposing them to
SwiftUI.

## 1. Create a TCP connection

TCP is a reliable ordered byte stream. It does not create message boundaries.

~~~swift
import Network

@available(iOS 26.0, *)
func makeTCPConnection(to endpoint: NWEndpoint) -> NetworkConnection<TCP> {
    NetworkConnection(to: endpoint) {
        TCP().noDelay(true)
    }
}
~~~

## 2. Add TLS peer authentication

TLS protects the stream and exposes peer-authentication configuration. It does
not replace app-level authorization or pairing.

~~~swift
import Network

@available(iOS 26.0, *)
func makeSecureConnection(to endpoint: NWEndpoint) -> NetworkConnection<TLS> {
    NetworkConnection(to: endpoint) {
        TLS { TCP() }.peerAuthentication(.required)
    }
}
~~~

## 3. Build local peer-to-peer parameters

The parameter builder can keep a route local and opt into Apple peer-to-peer
interfaces. Test the resulting policy on supported physical devices.

~~~swift
import Network

@available(iOS 26.0, *)
func makeLocalPeerParameters() -> NWParameters {
    NWParametersBuilder.parameters {
        TLS { TCP() }
    }
    .localOnly(true)
    .peerToPeerIncluded(true)
    .parameters
}
~~~

## 4. Advertise a Bonjour listener

Use a short, product-specific service type and declare the same type in the
app’s Bonjour privacy configuration.

~~~swift
import Network

@available(iOS 26.0, *)
func makeBonjourListener() throws -> NetworkListener<TCP> {
    try NetworkListener(
        for: .bonjour(name: "Bishop Peer", type: "_bishop-sync._tcp")
    ) {
        TCP()
    }
}
~~~

## 5. Run an accepted listener connection

The listener handler is an application boundary. Validate, authorize, and
bound the bytes before applying them to domain state.

~~~swift
import Network

@available(iOS 26.0, *)
func serve(_ listener: NetworkListener<TCP>) async throws {
    try await listener.run { connection in
        let message = try await connection.receive(
            atLeast: 1,
            atMost: 4096
        )
        _ = message.content
    }
}
~~~

## 6. Browse Bonjour services until one is selected

The explicit RunResult annotation selects the modern browser overload that
can continue until the user or policy returns a value.

~~~swift
import Network

@available(iOS 26.0, *)
func browseForOnePeer() async throws -> Bonjour.Endpoint {
    let browser = NetworkBrowser(
        for: .bonjour("_bishop-sync._tcp")
    )

    return try await browser.run {
        endpoints -> NetworkBrowser<Bonjour>.RunResult<Bonjour.Endpoint> in
        guard let endpoint = endpoints.first else {
            return .continue
        }
        return .finish(endpoint)
    }
}
~~~

## 7. Decode bounded TXT metadata

TXT records are discovery metadata. Decode only the fields the product
allowlists and validate their values before using them.

~~~swift
import Network

struct PeerAdvertisement: Decodable, Sendable {
    let protocolVersion: Int
    let role: String
}

@available(iOS 26.0, *)
func decodeAdvertisement(
    _ record: NWTXTRecord
) throws -> PeerAdvertisement {
    try TXTRecordDecoder().decode(PeerAdvertisement.self, from: record)
}
~~~

## 8. Connect to a typed Bonjour endpoint

The modern Bonjour endpoint conforms to Connectable. Keep its display name
separate from the app-owned identity and trust record.

~~~swift
import Network

@available(iOS 26.0, *)
func connect(to endpoint: Bonjour.Endpoint) -> NetworkConnection<TCP> {
    NetworkConnection(to: endpoint) {
        TCP()
    }
}
~~~

## 9. Build a typed Codable connection

Coder supplies a typed message protocol above the stream. Include a schema
version and message ID in real envelopes.

~~~swift
import Network

struct PeerEnvelope: Codable, Sendable {
    let revision: Int
    let body: String
}

@available(iOS 26.0, *)
func makeJSONConnection(
    to endpoint: NWEndpoint
) -> NetworkConnection<Coder<PeerEnvelope, PeerEnvelope, NetworkJSONCoder>> {
    NetworkConnection(to: endpoint) {
        Coder(PeerEnvelope.self, using: .json) {
            TCP()
        }
    }
}
~~~

## 10. Send and receive a typed message

The send call is transport progress, not an application receipt.

~~~swift
import Network

struct PeerEnvelope: Codable, Sendable {
    let revision: Int
    let body: String
}

@available(iOS 26.0, *)
func exchange(
    on connection: NetworkConnection<
        Coder<PeerEnvelope, PeerEnvelope, NetworkJSONCoder>
    >
) async throws -> PeerEnvelope {
    try await connection.send(
        PeerEnvelope(revision: 1, body: "hello")
    )
    return try await connection.receive().content
}
~~~

## 11. Bound a TCP length-prefixed payload

Use a fixed-width integer and reject the length before allocating or receiving
the payload.

~~~swift
import Foundation
import Network

@available(iOS 26.0, *)
func sendLengthPrefixed(
    on connection: NetworkConnection<TCP>,
    data: Data
) async throws {
    let length = UInt32(data.count)
    try await connection.send(length)
    try await connection.send(data)
}

@available(iOS 26.0, *)
func receiveLengthPrefixed(
    on connection: NetworkConnection<TCP>
) async throws -> Data {
    let length = try await connection.receive(as: UInt32.self).content
    guard length <= 1_048_576 else {
        throw NSError(domain: "PeerTransport", code: 1)
    }
    return try await connection.receive(exactly: Int(length)).content
}
~~~

## 12. Use TLV message types

TLV gives a message type and a completion marker. The app still needs a type
allowlist, size budget, and idempotent application.

~~~swift
import Foundation
import Network

@available(iOS 26.0, *)
func sendDocumentChunk(
    on connection: NetworkConnection<TLV>,
    data: Data
) async throws {
    try await connection.send(
        data,
        type: 1,
        lastMessage: true
    )
}

@available(iOS 26.0, *)
func makeTLVConnection(
    to endpoint: NWEndpoint
) -> NetworkConnection<TLV> {
    NetworkConnection(to: endpoint) {
        TLV { TCP() }
    }
}
~~~

## 13. Add a custom framer definition

A custom framer needs a real NWProtocolFramerImplementation. The implementation
below passes bytes through only as a compile-sized skeleton; a production
framer must parse, bound, and validate its own header and payload.

~~~swift
import Foundation
import Network

final class PeerFrameImplementation: NSObject, NWProtocolFramerImplementation {
    static let label = "com.example.peer.frame"

    required init(framer: NWProtocolFramer.Instance) {}

    func start(
        framer: NWProtocolFramer.Instance
    ) -> NWProtocolFramer.StartResult {
        .ready
    }

    func handleInput(framer: NWProtocolFramer.Instance) -> Int {
        framer.passThroughInput()
        return 0
    }

    func handleOutput(
        framer: NWProtocolFramer.Instance,
        message: NWProtocolFramer.Message,
        messageLength: Int,
        isComplete: Bool
    ) {
        framer.passThroughOutput()
    }

    func wakeup(framer: NWProtocolFramer.Instance) {}
    func stop(framer: NWProtocolFramer.Instance) -> Bool { true }
    func cleanup(framer: NWProtocolFramer.Instance) {}
}

enum PeerFrame: FramerProtocol {
    static let definition = NWProtocolFramer.Definition(
        implementation: PeerFrameImplementation.self
    )
}

@available(iOS 26.0, *)
func makeFramedConnection(
    to endpoint: NWEndpoint
) -> NetworkConnection<Framer<PeerFrame>> {
    NetworkConnection(to: endpoint) {
        Framer(using: PeerFrame.self) {
            TCP()
        }
    }
}
~~~

## 14. Observe paths and scope cancellation/reconnect

Use state and path callbacks for UI diagnostics, and let a scoped async
operation end when its task is cancelled. Reconnect only idempotent or
explicitly resumable work after a new epoch and handshake.

~~~swift
import Foundation
import Network

@available(iOS 26.0, *)
func watchPath(on connection: NetworkConnection<TCP>) {
    connection
        .onStateUpdate { _, state in print(state) }
        .onPathUpdate { _, path in print(path) }
        .onViabilityUpdate { _, viable in print(viable) }
        .onBetterPathUpdate { _, better in print(better) }
}

@available(iOS 26.0, *)
func runScopedSession(to endpoint: NWEndpoint) async throws {
    try await withNetworkConnection(to: endpoint, using: { TCP() }) {
        connection in
        connection.onStateUpdate { _, state in print(state) }
        try await withTaskCancellationHandler(operation: {
            let message = try await connection.receive(
                atLeast: 1,
                atMost: 4096
            )
            _ = message.content
        }, onCancel: {
            // Task cancellation exits the scoped connection operation.
        })
    }
}

@available(iOS 26.0, *)
func reconnect(
    endpointProvider: @Sendable () async throws -> NWEndpoint
) async throws {
    var attempt = 0
    while !Task.isCancelled && attempt < 3 {
        do {
            let endpoint = try await endpointProvider()
            try await withNetworkConnection(
                to: endpoint,
                using: { TCP() }
            ) { connection in
                try await connection.send(Data("hello".utf8))
            }
            return
        } catch is CancellationError {
            throw CancellationError()
        } catch {
            attempt += 1
            try await Task.sleep(nanoseconds: 200_000_000)
        }
    }
    throw NSError(domain: "PeerTransport", code: 2)
}
~~~

## Recipe guardrails

- These snippets do not request local-network permission.
- Add NSLocalNetworkUsageDescription and NSBonjourServices to the container
  app target when the route uses the local network.
- Treat Bonjour names, endpoints, and TXT records as untrusted discovery
  values.
- Add app-owned identity, pairing, authorization, schema, and epoch checks.
- Keep raw Network objects out of the SwiftUI view layer.
- Typecheck against the actual deployment SDK and run the physical-device
  proof matrix on the signed TestFlight artifact.

## Sources

- [Network Framework modern peer-transport route](../42-framework-deep-dives/139-swiftui-network-framework-modern-peer-transport-route.md)
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
- [NetworkChannel.State](https://developer.apple.com/documentation/network/networkchannel/state-swift.enum)
- [Choosing the right networking API](https://developer.apple.com/documentation/technotes/tn3151-choosing-the-right-networking-api)
- [Moving from Multipeer Connectivity to Network framework](https://developer.apple.com/documentation/technotes/tn3213-moving-from-multipeer-connectivity-to-network-framework)
- [Understanding local network privacy](https://developer.apple.com/documentation/technotes/tn3179-understanding-local-network-privacy)
- [Privacy - Local Network Usage Description](https://developer.apple.com/documentation/bundleresources/information_property_list/nslocalnetworkusagedescription)
- [Privacy - Bonjour Services](https://developer.apple.com/documentation/bundleresources/information_property_list/nsbonjourservices)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
