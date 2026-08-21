# URLSession, Network Framework, and streaming

## Scope

This page defines the networking foundation for native iOS apps that need ordinary
request/response APIs, incremental delivery, WebSockets, local-peer protocols,
background transfers, or path-aware offline behavior.

It covers:

- Foundation URL Loading System and URLSession configuration;
- data, upload, download, and background-transfer task selection;
- URLSession.AsyncBytes and bounded incremental parsing;
- URLSessionWebSocketTask for message-oriented WebSocket sessions;
- Network Framework NWConnection, NWListener, NWBrowser, protocol stacks, and
  NWPathMonitor;
- App Transport Security, local-network permission, and Bonjour declarations;
- cancellation, authentication, retry, idempotency, and process lifecycle;
- an on-device AI route that treats transport, model inference, proposal review,
  and durable commit as separate boundaries;
- native Liquid Glass and accessibility implications for network state.

The network is an input and transport boundary. It is not the domain source of
truth, an authorization decision, or proof that a remote operation committed.

## Version and target boundary

Record the selected SDK, deployment target, device family, architecture, and
network route before using an API. Confirm the declaration in the target SDK and
then compile it in the named app target.

Do not infer from a documentation page or a successful type check that:

- the server supports the HTTP method, content type, authentication, or stream
  framing;
- a TLS certificate and trust policy are correct;
- the user granted local-network access;
- a network path will remain available;
- a WebSocket will reconnect safely;
- a background transfer will wake the app at a particular time;
- a streamed model answer is complete, safe, or approved;
- a response changed the user's durable local state.

The app should be usable when the route is unavailable, slow, canceled, or
interrupted.

## Choose the narrowest transport

| Product outcome | First route | Boundary |
| --- | --- | --- |
| One request produces one response | URLSession data task or async data(for:) | Validate status, content type, size, schema, auth, and cancellation |
| Incremental server-sent text or bytes | URLSession bytes(for:) and AsyncBytes | Define framing, partial data, limits, cancellation, and incomplete-stream behavior |
| Large file upload/download that can outlive the app | Background URLSession configuration | Reconcile delegate events and temporary files after relaunch |
| Bidirectional remote messages | URLSessionWebSocketTask | Define handshake, message size, ping, close, reconnect, and idempotency |
| Custom local or peer protocol | Network Framework NWConnection/NWListener/NWBrowser | Own framing, identity, TLS/protocol stack, permission, reconnect, and lifecycle |
| Path and interface policy | NWPathMonitor | A path observation informs policy; it does not prove a request will succeed |
| Web page, cookies, or browser-authenticated content | WebKit/SafariServices | Keep browser content and app API trust boundaries distinct |
| iCloud-private record reconciliation | CloudKit/CKSyncEngine | Do not replace record reconciliation with ad hoc HTTP polling |
| Local-only AI inference | Foundation Models/Core ML/other selected Apple model route | Transport may be absent; model availability and proposal policy still apply |

Use URLSession for HTTP semantics and server APIs. Use Network Framework when
the app needs control over endpoints, protocol composition, local service
discovery, custom framing, or a connection lifecycle that does not fit URLSession.

## URL Loading System

The URL Loading System provides asynchronous access to URL-identified resources
using standard protocols such as HTTPS. URLSession coordinates related transfer
tasks and URLSessionConfiguration controls session behavior.

### Session configuration choices

| Configuration | Useful for | Privacy/lifecycle note |
| --- | --- | --- |
| default | Normal API traffic with standard caching/cookie behavior | Make cache, credential, and cookie policy explicit for sensitive data |
| ephemeral | Login bootstrap, private lookup, or a deliberately non-persistent session | Do not assume no system/network telemetry; verify the full privacy policy |
| background(withIdentifier:) | Transfers that should continue while the app is suspended | A system-managed transfer requires a delegate/reconciliation design and stable identifier |
| shared | Simple defaults or prototypes | Production clients often need explicit timeouts, cache, headers, connectivity, and delegate policy |

Set timeouts and cache behavior according to the operation. A short metadata
request, a long upload, and a user-visible AI stream should not silently share the
same retry and timeout policy.

For sensitive product data, keep authorization and cookies scoped to the selected
session. Avoid logging URLRequest headers, URLs containing secrets, raw response
bodies, prompts, transcripts, tokens, cookies, or user-selected file paths.

### Task families

- Data tasks return in-memory Data and URLResponse values. They fit bounded
  request/response payloads.
- Upload tasks send a request body or file and expose progress/delegate lifecycle.
- Download tasks write to a temporary file. The app must move, validate, and own
  the resulting file before the system removes the temporary location.
- Background sessions let the system continue eligible file transfers and later
  deliver delegate events. They do not turn arbitrary in-memory computation into
  background execution.
- Async APIs integrate with structured concurrency, but cancellation must still
  be mapped to the URLSessionTask and the domain operation.

Validate HTTP responses before decoding:

1. require the expected scheme/host or an allowlisted endpoint;
2. require the expected HTTP status range;
3. validate content type and content length where supplied;
4. enforce an application maximum size;
5. decode a versioned schema;
6. surface server errors without leaking sensitive response bodies;
7. persist only after domain validation.

A successful HTTP response is transport evidence. It is not proof that a remote
side effect was applied unless the server contract says so and the app verifies
the returned operation identifier or durable state.

## AsyncBytes and incremental delivery

URLSession bytes(for:) and bytes(from:) provide URLSession.AsyncBytes, an
AsyncSequence of bytes. The sequence also exposes line-oriented adapters for
text protocols. This is useful for server-sent events, newline-delimited JSON,
progress text, or model-token-like streams.

Treat framing as a protocol decision:

| Stream shape | Parser contract |
| --- | --- |
| newline-delimited JSON | Decode one complete line, reject oversized lines, preserve event IDs |
| server-sent events | Parse event fields and blank-line event boundaries; handle retry/id fields as specified |
| length-prefixed binary | Buffer only enough for the declared frame with a hard limit |
| arbitrary UTF-8 chunks | Use an incremental decoder; never assume one byte chunk is one character |
| model text deltas | Keep source revision, sequence, cancellation, and finalization metadata |

Do not render every byte directly into SwiftUI. Parse on an appropriate isolation
boundary, batch updates, and publish bounded display deltas on the main actor.
Keep the raw stream separate from the user-visible transcript when the product
needs replay, redaction, or audit.

A stream can end because the server completed, the user canceled, the task was
canceled, the path failed, the process ended, the server closed early, or the
parser rejected input. These states must not all become “success.”

## WebSockets

URLSessionWebSocketTask is a URLSessionTask that communicates over WebSocket
framing on a TCP/TLS transport. It supports ws and wss URLs, message-oriented
text/binary sends and receives, ping frames, close codes, authentication and
redirect delegate behavior, and a maximum message size.

Choose URLSessionWebSocketTask when:

- the endpoint is an HTTP/WebSocket service;
- URLSession authentication/cookie/delegate behavior is useful;
- the app wants message-oriented async send/receive;
- the server's reconnect and session semantics are well defined.

Use Network Framework with NWProtocolWebSocket when the app also needs a custom
Network protocol stack, NWConnection lifecycle, local-peer transport, or
protocol metadata/options that URLSession does not expose.

A WebSocket is not a durable queue. Define:

- session identity and authentication refresh;
- server and client message IDs;
- ordering and duplicate handling;
- maximum message size;
- ping/pong and idle timeout;
- close-code mapping;
- reconnect backoff with jitter;
- resubscription after reconnect;
- server-side resume cursor;
- idempotency for commands;
- local persistence for messages that must not be lost.

Never assume that reconnecting and resending the last command is safe. A command
needs a domain idempotency key and a server contract that makes duplicate delivery
safe.

## Network Framework

Network Framework exposes connections, listeners, browsers, path information,
and composable protocol stacks through types such as NWConnection, NWListener,
NWBrowser, NWParameters, NWPathMonitor, NWProtocolTLS, NWProtocolTCP,
NWProtocolQUIC, NWProtocolWebSocket, and NWProtocolFramer.

### NWConnection

NWConnection represents a connection to an NWEndpoint using NWParameters. The
app owns:

- endpoint selection;
- protocol parameters and optional TLS;
- stateUpdateHandler;
- viability/path change policy;
- receive framing;
- send completion and backpressure;
- cancellation;
- reconnect;
- authentication or application-level identity.

A connection state of ready means the transport is ready according to the
framework. It does not mean a peer is authenticated, the protocol handshake
completed, or the domain has accepted a command.

For a custom protocol, choose a framing rule before writing send/receive code:

- fixed-size records;
- length-prefixed records;
- delimiter-based records with escaped delimiters;
- Network Framework message metadata;
- a higher-level WebSocket or HTTP protocol.

Handle partial reads. A single receive callback is not guaranteed to contain one
complete domain message, and one callback may contain multiple messages.

### NWListener and NWBrowser

Use NWListener for a product-owned local service and NWBrowser for discovery
when local service discovery is the product requirement. Bonjour service types
must be declared in the target's Info.plist. Local-network access must be
explained with NSLocalNetworkUsageDescription.

Discovery is not identity. After discovering a service:

1. verify the endpoint is in the expected protocol family;
2. establish the selected secure/authenticated session;
3. authenticate the peer or pair it through a user-visible flow;
4. negotiate protocol version and capabilities;
5. apply authorization to each command;
6. show the connection and privacy state;
7. handle disappearance, path changes, and revocation.

Do not treat a Bonjour name, IP address, or local-network presence as proof of
identity.

### NWPathMonitor

NWPathMonitor observes changes to the currently available path. A path can report
interface, status, expensive, constrained, or unsatisfied information. Use it
to choose a policy such as:

- defer a large upload on an expensive/constrained path;
- keep local inference active while remote inference waits;
- show offline affordances;
- retry a user-visible operation after a path change;
- choose a LAN route when the product explicitly supports it.

Do not use NWPathMonitor as a preflight “internet available” test. The path can
change after the observation, DNS/TLS/auth can fail, the server can reject the
request, and a local permission prompt can block the route. The actual request or
connection result is the source of transport truth.

## App Transport Security and local-network privacy

App Transport Security (ATS) applies to URL Loading System HTTP connections and
requires HTTPS plus additional TLS/server-trust checks. Use an explicit,
narrowly scoped exception only when a documented server or local-device
requirement makes it necessary. Never add a global arbitrary-load exception as a
debugging shortcut that reaches production.

Important target configuration surfaces include:

- NSAppTransportSecurity for ATS settings;
- NSExceptionDomains for named domain exceptions;
- NSAllowsLocalNetworking for local resources where appropriate;
- NSLocalNetworkUsageDescription for any app that uses the local network,
  including Bonjour, direct unicast, or multicast;
- NSBonjourServices for the Bonjour service types the app expects to use.

A local-network usage description and ATS configuration solve different problems:
the first explains/request access to the local network; the second governs
transport security. Neither authenticates a peer.

Review entitlements, Info.plist values, associated domains, server certificates,
redirect hosts, and any proxy/VPN/network extension behavior in the named target.
A simulator can help inspect configuration, but physical network permission,
Wi-Fi isolation, captive portals, cellular constraints, and real accessories
require device proof.

## On-device AI and network boundaries

For an AI feature, write the route as four separate stages:

    source record
      -> transport or local model input
      -> typed proposal
      -> user/authorization validation
      -> durable commit
      -> projection

Remote streaming is not on-device inference. A product can use a remote stream,
a local Foundation Models/Core ML route, or a fallback between them, but the UI
must name the source and preserve availability/privacy policy.

A safe proposal contract includes:

- source record IDs and revision;
- model/provider route;
- prompt or input policy without unnecessary raw retention;
- output schema and parser version;
- confidence/uncertainty or “needs review” state where meaningful;
- cancellation and partial-output behavior;
- authorization and current-state validation;
- approval actor/time;
- commit idempotency key;
- privacy and retention policy.

If a network stream ends early, do not commit the partial text as an approved
answer. If the source changed while the model ran, revalidate before applying.
If a local model is unavailable, offer an explicit fallback or remain local-only;
do not silently send private data to a remote provider.

## Actors, cancellation, and ownership

A useful ownership split is:

- transport actor: URLSession task or NWConnection lifecycle;
- parser actor: framing, size limits, decoding, sequence numbers;
- domain actor/repository: validation, dedupe, outbox, persistence;
- main actor: user-visible state and system UI projections.

Keep delegate callbacks and connection handlers small. Convert callbacks into
typed events, then let one owner decide state transitions. Cancel the task and
the domain operation together, but preserve a durable “canceled” or “partial”
record when the product needs recovery.

Do not retry:

- a user cancellation;
- malformed or unsupported data;
- a permanent authorization failure;
- an idempotent operation without an idempotency contract;
- an ATS or certificate failure by blindly widening security exceptions.

Retry only according to operation type, server guidance, reachability evidence,
backoff, jitter, and a maximum attempt/deadline.

## Availability and fallback matrix

| Condition | User-visible state | Safe fallback |
| --- | --- | --- |
| No network path | Offline | Local data/model, draft, retry action |
| Expensive/constrained path | Limited connection | Defer/ask before large transfer |
| Local network denied | Local device unavailable | Explain Settings/permission route or remote mode |
| ATS/TLS failure | Secure connection unavailable | Repair server/configuration; never weaken globally |
| HTTP auth expired | Sign-in required | Refresh/reauthenticate; preserve draft |
| Stream canceled | Canceled | Keep source and offer resume/retry |
| Stream ended before final marker | Incomplete | Review/discard; never claim completion |
| WebSocket closed | Disconnected | Reconnect/resubscribe or offline mode |
| Background transfer relaunch | Transfer pending/reconciled | Restore delegate events and validate file |
| Local model unavailable | On-device AI unavailable | Manual workflow or explicit approved remote fallback |
| Server accepted request but result pending | Processing | Poll/subscribe with operation ID; do not duplicate command |

## Verification boundary

Prove the route in layers:

1. documentation/source review for the selected SDK and required configuration;
2. compile the exact session, parser, WebSocket, or Network Framework code;
3. deterministic tests for status, framing, limits, cancellation, retry, dedupe,
   and schema validation;
4. UI/system tests for loading, error, offline, permission, Dynamic Type,
   VoiceOver, and reduced-motion states;
5. physical-device tests for Wi-Fi/cellular, local-network permission, path loss,
   background transfer, WebSocket reconnect, and device thermals;
6. release/archive inspection for ATS, Info.plist, entitlements, privacy strings,
   server environment, and production endpoint policy.

A live HTTP 200, a ready NWConnection, a displayed stream, or a preview is only
one piece of evidence. Preserve the request ID, operation ID, sequence, source
revision, and final commit result when the feature is consequential.

## Sources

- [URL Loading System](https://developer.apple.com/documentation/foundation/url-loading-system)
- [URLSession](https://developer.apple.com/documentation/foundation/urlsession)
- [URLSessionConfiguration](https://developer.apple.com/documentation/foundation/urlsessionconfiguration)
- [URLSessionTask](https://developer.apple.com/documentation/foundation/urlsessiontask)
- [URLSessionDownloadTask](https://developer.apple.com/documentation/foundation/urlsessiondownloadtask)
- [URLSessionUploadTask](https://developer.apple.com/documentation/foundation/urlsessionuploadtask)
- [URLSession.AsyncBytes](https://developer.apple.com/documentation/foundation/urlsession/asyncbytes)
- [URLSessionWebSocketTask](https://developer.apple.com/documentation/foundation/urlsessionwebsockettask)
- [URLSessionTaskDelegate](https://developer.apple.com/documentation/foundation/urlsessiontaskdelegate)
- [URLSessionConfiguration.background(withIdentifier:)](https://developer.apple.com/documentation/foundation/urlsessionconfiguration/background%28withidentifier%3A%29)
- [Network](https://developer.apple.com/documentation/network)
- [NWConnection](https://developer.apple.com/documentation/network/nwconnection)
- [NWListener](https://developer.apple.com/documentation/network/nwlistener)
- [NWBrowser](https://developer.apple.com/documentation/network/nwbrowser)
- [NWParameters](https://developer.apple.com/documentation/network/nwparameters)
- [NWPathMonitor](https://developer.apple.com/documentation/network/nwpathmonitor)
- [NWProtocolWebSocket](https://developer.apple.com/documentation/network/nwprotocolwebsocket)
- [NWProtocolTLS](https://developer.apple.com/documentation/network/nwprotocoltls)
- [NSAppTransportSecurity](https://developer.apple.com/documentation/bundleresources/information_property_list/nsapptransportsecurity)
- [NSAllowsLocalNetworking](https://developer.apple.com/documentation/bundleresources/information_property_list/nsapptransportsecurity/nsallowslocalnetworking)
- [NSLocalNetworkUsageDescription](https://developer.apple.com/documentation/bundleresources/information_property_list/nslocalnetworkusagedescription)
- [NSBonjourServices](https://developer.apple.com/documentation/bundleresources/information-property-list/nsbonjourservices)
- [Supporting associated domains](https://developer.apple.com/documentation/xcode/supporting-associated-domains)
- [URLSession background transfers](https://developer.apple.com/documentation/foundation/downloading-files-in-the-background)
