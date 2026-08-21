# URLSession, Network Framework, and streaming AI capability route

## Capability contract

Use this route when an app needs remote API calls, incremental output,
bidirectional sessions, local-device connections, large background transfers, or
a clear fallback to on-device work.

The route produces:

1. a transport selected for the actual protocol;
2. a typed result/event stream with bounded parsing;
3. cancellation, retry, dedupe, and authentication policy;
4. local-first persistence and projection behavior;
5. privacy/configuration declarations;
6. physical and release evidence proportional to the risk.

The transport is not the product's approval boundary. Keep source records,
streamed proposals, validated commands, and committed state distinct.

## Choose the route

| Need | Route | First proof |
| --- | --- | --- |
| Small authenticated API request | URLSession data(for:) | Compile and exercise status/schema/auth failure |
| Server-sent incremental text | URLSession bytes(for:) | Parse framing, cancellation, early close, and final marker |
| Bidirectional remote session | URLSessionWebSocketTask | Handshake, ping/close, reconnect, duplicate command |
| Custom local protocol | NWConnection with NWParameters | Framing, peer identity, local permission, path loss |
| Advertise a local service | NWListener | Bonjour declaration, lifecycle, authentication |
| Discover a local service | NWBrowser | Permission, discovery result validation, pairing |
| Large transfer | Background URLSession | Delegate, relaunch, file move/validation, resume/cancel |
| Decide whether to defer work | NWPathMonitor plus actual request result | Expensive/constrained/offline policy |
| Local-only intelligence | Foundation Models/Core ML route | Model availability, typed output, proposal/commit proof |
| Cloud/iCloud record sync | CloudKit/CKSyncEngine | Record reconciliation, not polling or socket presence |

## Common foundation

Define an operation envelope before implementing a client:

~~~swift
struct OperationEnvelope<Payload: Sendable>: Sendable {
    let operationID: UUID
    let sourceRevision: Int64?
    let attempt: Int
    let startedAt: Date
    let payload: Payload
}

enum TransportOutcome<Value: Sendable>: Sendable {
    case success(Value)
    case canceled
    case offline
    case unauthorized
    case failed(retryable: Bool, message: String)
    case incomplete
}
~~~

The exact types are product-owned. The important boundary is that an operation ID,
source revision, attempt, and outcome survive beyond one view update.

## Route A: request/response API

Use this for metadata, record reads, user-initiated commands, and bounded
responses.

1. Build a URLRequest from an allowlisted endpoint and typed input.
2. Attach authentication through a scoped credential/session policy.
3. Set content type, accept type, timeout, and idempotency key when needed.
4. Use URLSession data(for:) or a delegate-backed data task.
5. Validate HTTP status, content type, response size, and schema.
6. Map server error codes to user-safe domain errors.
7. Commit only after authorization/current-state validation.
8. Store operation ID and server result for dedupe/recovery.
9. Update the main UI and downstream projections after the local transaction.

For mutation endpoints, define whether the server may still complete after the
client cancels. If so, use an operation status endpoint or durable server event;
do not blindly retry the same mutation.

## Route B: streamed remote AI proposal

Use this when a remote service returns incremental text or structured events.

1. Load the source record and capture sourceRevision.
2. Decide whether remote processing is allowed for this data.
3. Build a request with a model/provider route and operation idempotency key.
4. Use URLSession bytes(for:) for the documented stream framing.
5. Parse lines/events through a bounded parser.
6. Validate every complete event against the schema and sequence.
7. Publish batched partial output as uncommitted draft content.
8. Handle cancel, path loss, early EOF, malformed events, and server errors.
9. Require a final completion marker or explicit server completion event.
10. Re-read the source record and validate sourceRevision before Apply.
11. Show the proposal and provenance.
12. On user approval, commit the typed result locally.
13. Sync or project the approved result according to the product policy.

A streamed response is not a durable fact. Do not persist every partial delta as an
approved record, and do not call a partial response complete because the TCP/TLS
connection closed cleanly.

## Route C: WebSocket live session

Use URLSessionWebSocketTask for an HTTP/WebSocket service that already defines a
message protocol.

Session contract:

~~~yaml
handshake:
  url: wss://allowlisted.example/session
  subprotocol: product-v1
  authentication: scoped-token
messages:
  client:
    - type: subscribe
      requestID: stable-id
    - type: command
      commandID: idempotency-key
    - type: resume
      cursor: last-applied-server-sequence
  server:
    - type: snapshot
      sequence: monotonically-increasing
    - type: event
      sequence: monotonically-increasing
    - type: command-result
      commandID: echoed-idempotency-key
    - type: error
close:
  reconnect: selected-codes-only
  backoff: exponential-with-jitter
~~~

Implement:

- handshake and authentication timeout;
- receive loop with maximum message size;
- ping/idle policy;
- sequence and cursor validation;
- duplicate event handling;
- reconnect/resubscribe;
- token refresh;
- close-code mapping;
- local durable cursor if events cannot be lost;
- server idempotency for commands.

If the live session is only a projection of durable records, rebuild from a
snapshot or CloudKit/server cursor after reconnect. Do not make a socket the only
copy of user data.

## Route D: local device or peer connection

Use Network Framework for a local or custom protocol:

1. Define the peer identity and pairing story.
2. Declare NSLocalNetworkUsageDescription.
3. If using Bonjour, declare every service type in NSBonjourServices.
4. Choose NWBrowser or a direct endpoint.
5. Create NWParameters with the intended transport/security stack.
6. Create NWConnection or NWListener.
7. Complete protocol handshake and authenticate the peer.
8. Negotiate protocol version and capabilities.
9. Frame messages and bound every length.
10. Apply authorization to each command.
11. Persist the last safe local result if the command matters.
12. Reconnect after path changes only when the protocol allows it.
13. Revoke/pair again when the user removes the device.

A discovered endpoint is not an authenticated device. A ready connection is not a
completed command. A local network permission grant is not product authorization.

## Route E: background transfer

Use a background URLSession configuration for transfers that should continue under
system-managed background conditions.

1. Give the background configuration a stable identifier.
2. Create the session with a delegate retained by an application-owned coordinator.
3. Persist task metadata, source record, destination policy, and operation ID.
4. Prefer a file-owned route for large content and validate the temporary file.
5. Reconcile task and delegate callbacks with the local transfer record.
6. Move the downloaded file into app-owned storage only after validation.
7. Handle authentication challenges, cancellation, failure, retry, and expiration.
8. Reconnect the delegate/session after relaunch.
9. Finish the app's background event handoff only after events are reconciled.
10. Update widgets/Live Activities only from durable local transfer state.

Background transfer is not proof that an import, model install, or user-facing
operation succeeded. The app still needs checksum/type/size validation and an
atomic domain commit.

## Route F: path-aware local/remote fallback

Use NWPathMonitor as a policy signal and the actual transport result as evidence.

~~~yaml
if:
  local_model_available: use_local_model
  else_if:
    path_status: satisfied
    service_policy: remote_allowed
    source_policy: remote_allowed
    request_result: success
  then: use_remote_route
else:
  save_local_draft_and_explain
~~~

A more complete decision records:

- data sensitivity and user consent;
- local model/asset availability;
- path status;
- expensive/constrained policy;
- server availability and auth;
- expected size/cost;
- whether the action is read-only or mutating;
- whether the remote result requires review;
- whether the person explicitly chose fallback.

Do not silently route sensitive source data to a remote provider merely because a
path became available.

## Route G: trust and configuration

Review target configuration together:

~~~yaml
target:
  sdk: selected iOS SDK
  deployment_target: selected minimum
  network:
    allowed_hosts:
      - api.example.invalid
    websocket_hosts:
      - stream.example.invalid
  plist:
    NSAppTransportSecurity: narrow documented exceptions only
    NSLocalNetworkUsageDescription: present when local network is used
    NSBonjourServices: present when Bonjour is used
  entitlements:
    review_required: network extensions, associated domains, iCloud, background modes
  privacy:
    remote_processing: explicit user/product policy
    log_redaction: tokens, prompts, transcripts, files, identifiers
~~~

Do not add ATS exceptions, local-network declarations, or entitlements just to
make a failing route disappear. Fix the server/protocol or document the narrow
exception and test it.

## Route H: SwiftUI state projection

Keep transport ownership outside the view:

~~~swift
@MainActor
final class NetworkFeatureModel: ObservableObject {
    @Published private(set) var state: ViewState = .idle

    private let client: FeatureClient
    private var task: Task<Void, Never>?

    func start() {
        task?.cancel()
        task = Task {
            await run()
        }
    }

    func cancel() {
        task?.cancel()
        task = nil
        state = .canceled
    }

    private func run() async {
        // Transport, parser, domain validation, and commit are separate steps.
    }
}
~~~

The concrete observation system and deployment target may differ. The invariant
is that the view renders a typed state and does not own a URLSessionTask,
NWConnection, parser buffer, or retry counter.

## Route I: system-surface projections

After a durable local boundary:

- reload a widget with compact, privacy-safe state;
- update a Live Activity only for its documented lifecycle;
- expose an App Intent that resolves current local state;
- index approved/searchable entities only after authorization;
- hide or redact content when the device is locked if the product requires it;
- never use a widget or socket callback as the record source of truth.

The projection revision should identify whether the state is local, pending,
streaming, incomplete, approved, synced, or stale.

## Route J: failure/recovery table

| Failure | Preserve | User action | Never do |
| --- | --- | --- | --- |
| Timeout | Source/draft and operation ID | Retry if safe | Duplicate an unknown mutation |
| Cancellation | Explicit canceled/partial state | Resume or discard | Claim completion |
| 401/403 | Draft/local record | Reauthenticate/repair access | Retry forever |
| ATS/TLS | Source and configuration diagnostics | Fix server/config | Widen ATS globally |
| Local permission denied | Local data | Settings/permission route | Fake a paired device |
| Malformed stream | Raw diagnostic metadata, not unsafe content | Retry/review | Commit partial output |
| WebSocket close | Cursor and durable snapshot | Reconnect/resubscribe | Assume messages were delivered |
| Background file failure | Transfer record and source | Retry/choose destination | Import a temporary file blindly |
| Path loss | Local state | Wait/retry/local mode | Treat path monitor as request proof |
| Source revision changed | New source revision | Rerun/review | Apply stale proposal |

## Evidence plan

Before calling a route complete, capture:

- exact target and SDK;
- source URL and API declaration;
- Info.plist/entitlement diff;
- request/response fixture or test server;
- status/content/schema/size tests;
- stream framing and early-EOF tests;
- WebSocket reconnect/duplicate tests;
- NWConnection partial-read and path-loss tests;
- local-network prompt and Bonjour discovery on device;
- background transfer cancel/relaunch/file validation;
- AI proposal source-revision and commit tests;
- accessibility and Dynamic Type screenshots;
- physical device and release/archive evidence where claimed.

## Sources

- [URL Loading System](https://developer.apple.com/documentation/foundation/url-loading-system)
- [URLSession](https://developer.apple.com/documentation/foundation/urlsession)
- [URLSessionConfiguration](https://developer.apple.com/documentation/foundation/urlsessionconfiguration)
- [URLSession.AsyncBytes](https://developer.apple.com/documentation/foundation/urlsession/asyncbytes)
- [URLSessionWebSocketTask](https://developer.apple.com/documentation/foundation/urlsessionwebsockettask)
- [Network](https://developer.apple.com/documentation/network)
- [NWConnection](https://developer.apple.com/documentation/network/nwconnection)
- [NWListener](https://developer.apple.com/documentation/network/nwlistener)
- [NWBrowser](https://developer.apple.com/documentation/network/nwbrowser)
- [NWPathMonitor](https://developer.apple.com/documentation/network/nwpathmonitor)
- [NWProtocolWebSocket](https://developer.apple.com/documentation/network/nwprotocolwebsocket)
- [NSAppTransportSecurity](https://developer.apple.com/documentation/bundleresources/information_property_list/nsapptransportsecurity)
- [NSAllowsLocalNetworking](https://developer.apple.com/documentation/bundleresources/information_property_list/nsapptransportsecurity/nsallowslocalnetworking)
- [NSLocalNetworkUsageDescription](https://developer.apple.com/documentation/bundleresources/information_property_list/nslocalnetworkusagedescription)
- [NSBonjourServices](https://developer.apple.com/documentation/bundleresources/information-property-list/nsbonjourservices)
- [Downloading files in the background](https://developer.apple.com/documentation/foundation/downloading-files-in-the-background)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [CloudKit](https://developer.apple.com/documentation/cloudkit)
