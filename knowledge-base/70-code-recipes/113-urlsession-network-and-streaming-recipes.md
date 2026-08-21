# URLSession, Network Framework, and streaming recipes

## How to use these sketches

These recipes are route skeletons for a named iOS target. They are not proof that
the target compiles, that a server follows the assumed protocol, that a device
grants local-network access, or that a background transfer completes after
relaunch.

Before adopting one:

- record the SDK/deployment target and exact endpoint contract;
- add only the required Info.plist keys, capabilities, and entitlements;
- replace placeholder URLs, schemas, authentication, and storage;
- add status/content-type/size/schema validation;
- test cancellation, retries, offline mode, path changes, and process death;
- redact logs and use physical-device evidence for local, background, or
  system-owned behavior.

## Recipe 1: bounded request/response client

Use a small client boundary that validates the HTTP response before decoding.
Keep endpoint construction and credentials outside the view.

~~~swift
import Foundation

struct APIError: Error, Sendable, Equatable {
    enum Kind: Sendable, Equatable {
        case invalidURL
        case unacceptableStatus(Int)
        case unexpectedContentType
        case responseTooLarge
        case decoding
        case transport
    }

    let kind: Kind
    let message: String
}

struct APIClient: Sendable {
    let session: URLSession
    let allowedHost: String
    let maximumResponseBytes: Int

    init(
        session: URLSession = .shared,
        allowedHost: String,
        maximumResponseBytes: Int = 2_000_000
    ) {
        self.session = session
        self.allowedHost = allowedHost
        self.maximumResponseBytes = maximumResponseBytes
    }

    func get<Value: Decodable>(
        path: String,
        decode: Value.Type = Value.self
    ) async throws -> Value {
        guard let url = URL(string: "https://" + allowedHost + path),
              url.host == allowedHost else {
            throw APIError(kind: .invalidURL, message: "Endpoint is not allowlisted.")
        }

        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        request.timeoutInterval = 30

        do {
            let (data, response) = try await session.data(for: request)

            guard let http = response as? HTTPURLResponse else {
                throw APIError(kind: .transport, message: "Response was not HTTP.")
            }

            guard (200..<300).contains(http.statusCode) else {
                throw APIError(
                    kind: .unacceptableStatus(http.statusCode),
                    message: "Server returned an unacceptable status."
                )
            }

            if let contentType = http.value(forHTTPHeaderField: "Content-Type"),
               !contentType.localizedCaseInsensitiveContains("application/json") {
                throw APIError(
                    kind: .unexpectedContentType,
                    message: "Response content type was not JSON."
                )
            }

            guard data.count <= maximumResponseBytes else {
                throw APIError(
                    kind: .responseTooLarge,
                    message: "Response exceeded the application limit."
                )
            }

            do {
                return try JSONDecoder().decode(Value.self, from: data)
            } catch {
                throw APIError(kind: .decoding, message: "Response schema was invalid.")
            }
        } catch is CancellationError {
            throw CancellationError()
        } catch let error as APIError {
            throw error
        } catch {
            throw APIError(kind: .transport, message: "The request did not complete.")
        }
    }
}
~~~

Production additions normally include scoped authentication, server error
decoding, request IDs, cache policy, retry policy, and a domain operation ID.
Do not include bearer tokens, cookies, prompt text, or response bodies in the
error message unless the value is intentionally safe.

## Recipe 2: line-oriented AsyncBytes stream

Use URLSession bytes(for:) when the server contract provides a line/event
framing format. The example assumes newline-delimited JSON and treats a missing
final event as incomplete.

~~~swift
import Foundation

struct StreamEvent: Decodable, Sendable {
    let sequence: Int
    let kind: String
    let text: String?
    let final: Bool
}

enum StreamResult: Sendable, Equatable {
    case completed
    case canceled
    case incomplete
}

struct StreamClient: Sendable {
    let session: URLSession
    let maximumLineLength: Int

    func consume(
        request: URLRequest,
        onEvent: @Sendable (StreamEvent) async throws -> Void
    ) async throws -> StreamResult {
        let (bytes, response) = try await session.bytes(for: request)

        guard let http = response as? HTTPURLResponse,
              (200..<300).contains(http.statusCode) else {
            throw APIError(kind: .unacceptableStatus(0), message: "Stream did not start.")
        }

        var receivedFinal = false

        do {
            for try await line in bytes.lines {
                guard line.utf8.count <= maximumLineLength else {
                    throw APIError(
                        kind: .responseTooLarge,
                        message: "Stream event exceeded the line limit."
                    )
                }

                guard let data = line.data(using: .utf8) else {
                    throw APIError(
                        kind: .decoding,
                        message: "Stream event was not valid UTF-8."
                    )
                }

                let event = try JSONDecoder().decode(StreamEvent.self, from: data)
                try await onEvent(event)

                if event.final {
                    receivedFinal = true
                    break
                }
            }
        } catch is CancellationError {
            return .canceled
        }

        return receivedFinal ? .completed : .incomplete
    }
}
~~~

The server may send multiple events in a transport chunk or split one event
across chunks. The AsyncBytes line adapter handles byte delivery, but the app
still owns event size, JSON schema, sequence, and finalization policy. For a
different framing protocol, replace the parser rather than assuming lines.

## Recipe 3: batched proposal streaming

Keep partial model output out of the durable approved record. The repository
below is intentionally abstract: it can receive a remote stream or a local
model adapter, but both routes produce the same proposal state.

~~~swift
import Foundation

struct ProposalDraft: Sendable, Equatable {
    let sourceID: UUID
    let sourceRevision: Int64
    var text: String
    var isComplete: Bool
}

protocol ProposalStore: Sendable {
    func currentSourceRevision(for id: UUID) async throws -> Int64
    func saveDraft(_ draft: ProposalDraft) async throws
    func commitApproved(_ draft: ProposalDraft, idempotencyKey: String) async throws
}

struct ProposalRunner: Sendable {
    let store: any ProposalStore

    func run(
        sourceID: UUID,
        sourceRevision: Int64,
        stream: AsyncThrowingStream<String, Error>,
        idempotencyKey: String
    ) async throws {
        var draft = ProposalDraft(
            sourceID: sourceID,
            sourceRevision: sourceRevision,
            text: "",
            isComplete: false
        )

        do {
            for try await delta in stream {
                try Task.checkCancellation()
                draft.text.append(delta)

                // Production code should debounce/batch this write.
                try await store.saveDraft(draft)
            }
        } catch is CancellationError {
            try await store.saveDraft(draft)
            throw CancellationError()
        } catch {
            try await store.saveDraft(draft)
            throw error
        }

        guard draft.text.isEmpty == false else {
            throw APIError(kind: .decoding, message: "Proposal was empty.")
        }

        guard try await store.currentSourceRevision(for: sourceID) == sourceRevision else {
            throw APIError(
                kind: .decoding,
                message: "Source changed while the proposal was generated."
            )
        }

        draft.isComplete = true
        try await store.saveDraft(draft)

        // Call this only after the person-approved action has passed validation.
        // try await store.commitApproved(draft, idempotencyKey: idempotencyKey)
    }
}
~~~

The draft, final proposal, approval, and commit should be separate domain
transitions. A UI callback that says “finished” is not enough to authorize the
last line.

## Recipe 4: URLSessionWebSocketTask actor

Own a WebSocket task behind an actor and make the receive loop explicit. The
message format and reconnect policy belong to the server/product contract.

~~~swift
import Foundation

enum SocketMessage: Sendable, Equatable {
    case text(String)
    case binary(Data)
}

actor WebSocketSession {
    private let task: URLSessionWebSocketTask
    private var isRunning = false

    init(
        url: URL,
        protocols: [String] = [],
        session: URLSession = .shared
    ) {
        if protocols.isEmpty {
            task = session.webSocketTask(with: url)
        } else {
            task = session.webSocketTask(with: url, protocols: protocols)
        }
    }

    func start() {
        guard !isRunning else { return }
        isRunning = true
        task.resume()
    }

    func send(_ message: SocketMessage) async throws {
        let value: URLSessionWebSocketTask.Message
        switch message {
        case .text(let text):
            value = .string(text)
        case .binary(let data):
            value = .data(data)
        }
        try await task.send(value)
    }

    func receive() async throws -> SocketMessage {
        let value = try await task.receive()
        switch value {
        case .string(let text):
            return .text(text)
        case .data(let data):
            return .binary(data)
        @unknown default:
            throw APIError(kind: .decoding, message: "Unknown WebSocket message.")
        }
    }

    func cancel() {
        isRunning = false
        task.cancel(with: .goingAway, reason: nil)
    }
}
~~~

Add a receive loop outside or inside the actor with:

- maximumMessageSize;
- ping/idle timeout;
- close-code mapping;
- authentication refresh;
- sequence/cursor validation;
- reconnect backoff;
- command IDs and server dedupe;
- durable snapshot/cursor recovery.

A successful send only means the client handed the message to the task. The
server's command result is the domain acknowledgement.

## Recipe 5: NWPathMonitor policy signal

Use NWPathMonitor to update policy state. Pair it with actual request/connection
results and stop the monitor when the owner is released.

~~~swift
import Foundation
import Network

struct PathPolicy: Sendable, Equatable {
    let isSatisfied: Bool
    let isExpensive: Bool
    let isConstrained: Bool
}

final class PathPolicyMonitor: @unchecked Sendable {
    private let monitor: NWPathMonitor
    private let queue = DispatchQueue(label: "com.example.path-policy")
    private let onChange: @Sendable (PathPolicy) -> Void

    init(onChange: @escaping @Sendable (PathPolicy) -> Void) {
        self.monitor = NWPathMonitor()
        self.onChange = onChange
    }

    func start() {
        monitor.pathUpdateHandler = { [onChange] path in
            onChange(
                PathPolicy(
                    isSatisfied: path.status == .satisfied,
                    isExpensive: path.isExpensive,
                    isConstrained: path.isConstrained
                )
            )
        }
        monitor.start(queue: queue)
    }

    func stop() {
        monitor.cancel()
    }
}
~~~

Do not show “the internet is working” from this callback. Use it to choose
whether to begin/defer work and label policy; the URLSession or NWConnection
result decides what actually happened.

## Recipe 6: framed NWConnection receive loop

The receive callback can deliver partial or coalesced data. The framer below uses
a four-byte big-endian length prefix and rejects frames above a fixed limit.

~~~swift
import Foundation
import Network

enum FrameError: Error {
    case tooLarge
    case malformed
}

final class FramedConnection {
    private let connection: NWConnection
    private var buffer = Data()
    private let maximumFrameBytes = 1_000_000
    private let queue = DispatchQueue(label: "com.example.framed-connection")

    init(host: NWEndpoint.Host, port: NWEndpoint.Port) {
        let parameters = NWParameters.tcp
        self.connection = NWConnection(
            host: host,
            port: port,
            using: parameters
        )
    }

    func start(onFrame: @escaping (Result<Data, Error>) -> Void) {
        connection.stateUpdateHandler = { state in
            // Map setup/waiting/ready/failed/cancelled into domain state.
            _ = state
        }

        connection.start(queue: queue)
        receiveNext(onFrame: onFrame)
    }

    func send(frame: Data, completion: @escaping (Error?) -> Void) {
        guard frame.count <= maximumFrameBytes else {
            completion(FrameError.tooLarge)
            return
        }

        var length = UInt32(frame.count).bigEndian
        var packet = Data(bytes: &length, count: MemoryLayout<UInt32>.size)
        packet.append(frame)

        connection.send(
            content: packet,
            completion: .contentProcessed { error in
                completion(error)
            }
        )
    }

    func cancel() {
        connection.cancel()
    }

    private func receiveNext(onFrame: @escaping (Result<Data, Error>) -> Void) {
        connection.receive(
            minimumIncompleteLength: 1,
            maximumLength: 64 * 1024
        ) { [weak self] data, _, isComplete, error in
            guard let self else { return }

            if let error {
                onFrame(.failure(error))
                return
            }

            if let data {
                buffer.append(data)
                do {
                    for frame in try drainFrames() {
                        onFrame(.success(frame))
                    }
                } catch {
                    onFrame(.failure(error))
                    connection.cancel()
                    return
                }
            }

            if isComplete {
                return
            }

            receiveNext(onFrame: onFrame)
        }
    }

    private func drainFrames() throws -> [Data] {
        var frames: [Data] = []

        while buffer.count >= 4 {
            let length = buffer.prefix(4).reduce(UInt32(0)) { partial, byte in
                (partial << 8) | UInt32(byte)
            }

            guard length <= UInt32(maximumFrameBytes) else {
                throw FrameError.tooLarge
            }

            let total = 4 + Int(length)
            guard buffer.count >= total else { break }

            frames.append(buffer.subdata(in: 4..<total))
            buffer.removeSubrange(0..<total)
        }

        return frames
    }
}
~~~

For a production protocol, use a dedicated actor or serial owner for buffer
mutation, authenticate the peer, bound the number of queued frames, and define
the behavior for malformed bytes and reconnect. Do not treat a TCP-ready state as
proof that the peer can perform a product command.

## Recipe 7: background URLSession download coordinator

Background sessions need a stable identifier and a retained delegate. The app
must move and validate the temporary download URL before it is lost.

~~~swift
import Foundation

final class BackgroundDownloadCoordinator: NSObject,
    URLSessionDownloadDelegate,
    URLSessionTaskDelegate {

    private let identifier = "com.example.app.background-downloads"
    private lazy var session: URLSession = {
        let configuration = URLSessionConfiguration.background(withIdentifier: identifier)
        configuration.waitsForConnectivity = true
        return URLSession(
            configuration: configuration,
            delegate: self,
            delegateQueue: nil
        )
    }()

    func enqueue(url: URL) -> URLSessionDownloadTask {
        var request = URLRequest(url: url)
        request.timeoutInterval = 60
        let task = session.downloadTask(with: request)
        task.resume()
        return task
    }

    func urlSession(
        _ session: URLSession,
        downloadTask: URLSessionDownloadTask,
        didFinishDownloadingTo location: URL
    ) {
        do {
            let attributes = try FileManager.default.attributesOfItem(atPath: location.path)
            let size = (attributes[.size] as? NSNumber)?.intValue ?? 0
            guard size > 0 else { throw APIError(kind: .responseTooLarge, message: "Empty file.") }

            let destination = try appOwnedDestination(for: downloadTask)
            try FileManager.default.moveItem(at: location, to: destination)

            // Validate type, size, checksum, signature, and domain metadata here.
            // Only then write the durable import/installation record.
        } catch {
            // Record a safe transfer/import failure without logging private paths.
        }
    }

    func urlSession(
        _ session: URLSession,
        task: URLSessionTask,
        didCompleteWithError error: Error?
    ) {
        if let error {
            // Persist retryable versus terminal transfer state.
            _ = error
        }
    }

    func urlSessionDidFinishEvents(forBackgroundURLSession session: URLSession) {
        // The app delegate/scene coordinator should complete the system handoff
        // after task metadata and durable state have been reconciled.
    }

    private func appOwnedDestination(for task: URLSessionTask) throws -> URL {
        let directory = try FileManager.default.url(
            for: .applicationSupportDirectory,
            in: .userDomainMask,
            appropriateFor: nil,
            create: true
        )
        return directory.appendingPathComponent("download-" + String(task.taskIdentifier))
    }
}
~~~

A background download completing means bytes reached a temporary file. It does
not mean a model was installed, a document was imported, or an AI asset passed
validation. Keep transfer, validation, import, and projection as separate states.

## Recipe 8: Info.plist route notes

Add only declarations required by the selected feature. Keep user-facing
permission strings specific and truthful.

~~~xml
<key>NSLocalNetworkUsageDescription</key>
<string>Connect to your selected local device to transfer the approved session.</string>
<key>NSBonjourServices</key>
<array>
    <string>_example._tcp</string>
</array>
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsLocalNetworking</key>
    <true/>
</dict>
~~~

This is not a universal template. Confirm the service type and ATS policy with
the target protocol. Do not include NSAllowsArbitraryLoads merely to make a
development endpoint work, and do not request local-network access when the app
does not use it.

## Recipe 9: SwiftUI state projection

The view should consume typed state and send intent to an owner. It should not
create a new URLSessionTask every time the body recomputes.

~~~swift
import SwiftUI

enum NetworkViewState: Equatable {
    case idle
    case loading
    case streaming(text: String)
    case offline(draft: String)
    case failed(message: String, retryable: Bool)
    case readyToApply(text: String)
    case applied
}

@MainActor
final class NetworkViewModel: ObservableObject {
    @Published private(set) var state: NetworkViewState = .idle

    private var work: Task<Void, Never>?

    func start() {
        work?.cancel()
        work = Task { [weak self] in
            guard let self else { return }
            state = .loading

            do {
                // Call the client/parser/repository boundary here.
                try await Task.sleep(for: .milliseconds(10))
                try Task.checkCancellation()
                state = .readyToApply(text: "Validated draft")
            } catch is CancellationError {
                state = .offline(draft: "")
            } catch {
                state = .failed(message: "The operation did not complete.", retryable: true)
            }
        }
    }

    func cancel() {
        work?.cancel()
        work = nil
        state = .offline(draft: "")
    }

    deinit {
        work?.cancel()
    }
}
~~~

Use the actual observation system supported by the target. The important
invariant is stable ownership and a single state machine, not a particular
property-wrapper spelling. Pair this with semantic controls, Dynamic Type,
reduced motion, VoiceOver labels, and a detail route for diagnostics.

## Recipe 10: test cases to add beside the route

Name tests after product evidence, not implementation details.

~~~swift
@Test
func malformedStreamCannotBecomeApproved() async throws {
    // Feed split/oversized/malformed events to the parser.
    // Verify the proposal is incomplete or rejected and no commit occurs.
}

@Test
func retryingACommandUsesTheSameIdempotencyKey() async throws {
    // Simulate timeout after server acceptance.
    // Verify the repository reconciles the operation instead of duplicating it.
}

@Test
func sourceRevisionChangeRejectsStaleProposal() async throws {
    // Change the local record while inference is running.
    // Verify Apply requires a rerun or explicit review.
}

@Test
func offlineEditRemainsReadableAndPending() async throws {
    // Disable transport and write locally.
    // Verify local read succeeds and the projection says Waiting to sync.
}
~~~

Use the testing framework supported by the target and add XCUI/physical-device
tests for permission prompts, local services, background relaunch, accessibility,
and system-owned surfaces. A fixture test cannot prove radio behavior.

## Recipe 11: release checklist command shape

Keep a reviewable, redacted record for a release candidate:

~~~yaml
target: NamedApp
sdk: selected iOS SDK
deployment_target: selected minimum
archive:
  configuration: Release
  entitlements_inspected: true
  info_plist_inspected: true
network:
  allowed_hosts_reviewed: true
  ats_exceptions_reviewed: true
  tls_production_tested: true
  websocket_reconnect_tested: true
local_network:
  usage_description_reviewed: true
  bonjour_services_reviewed: true
background_transfer:
  stable_identifier_reviewed: true
  relaunch_reconciled: true
ai:
  source_revision_rechecked: true
  remote_fallback_explicit: true
  partial_output_not_committed: true
privacy:
  tokens_redacted: true
  prompts_redacted: true
  files_redacted: true
device:
  physical_wifi_cellular_tested: true
  accessibility_tested: true
~~~

Do not store credentials, tokens, personal files, raw prompts, or unredacted
server responses in this checklist.

## Sources

- [URL Loading System](https://developer.apple.com/documentation/foundation/url-loading-system)
- [URLSession](https://developer.apple.com/documentation/foundation/urlsession)
- [URLSessionConfiguration](https://developer.apple.com/documentation/foundation/urlsessionconfiguration)
- [URLSession.AsyncBytes](https://developer.apple.com/documentation/foundation/urlsession/asyncbytes)
- [URLSessionWebSocketTask](https://developer.apple.com/documentation/foundation/urlsessionwebsockettask)
- [URLSessionDownloadTask](https://developer.apple.com/documentation/foundation/urlsessiondownloadtask)
- [URLSessionDownloadDelegate](https://developer.apple.com/documentation/foundation/urlsessiondownloaddelegate)
- [URLSessionTaskDelegate](https://developer.apple.com/documentation/foundation/urlsessiontaskdelegate)
- [Downloading files in the background](https://developer.apple.com/documentation/foundation/downloading-files-in-the-background)
- [Network](https://developer.apple.com/documentation/network)
- [NWConnection](https://developer.apple.com/documentation/network/nwconnection)
- [NWParameters](https://developer.apple.com/documentation/network/nwparameters)
- [NWPathMonitor](https://developer.apple.com/documentation/network/nwpathmonitor)
- [NWProtocolTCP](https://developer.apple.com/documentation/network/nwprotocoltcp)
- [NSAppTransportSecurity](https://developer.apple.com/documentation/bundleresources/information_property_list/nsapptransportsecurity)
- [NSLocalNetworkUsageDescription](https://developer.apple.com/documentation/bundleresources/information_property_list/nslocalnetworkusagedescription)
- [NSBonjourServices](https://developer.apple.com/documentation/bundleresources/information-property-list/nsbonjourservices)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
