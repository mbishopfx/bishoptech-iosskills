# URLSession and Network Framework proof matrix

## Purpose

Use this matrix to prove a networking feature at the boundary it claims. A
successful local compile is useful, but it does not prove server behavior,
physical network permission, path stability, background relaunch, on-device model
availability, or release configuration.

## Evidence levels

| Level | Evidence | Proves | Does not prove |
| --- | --- | --- | --- |
| L0 | Apple source/API and target review | The chosen route and documented configuration are understood | The target compiles or the server works |
| L1 | Named-target compile/archive | APIs, imports, availability, Info.plist, and entitlements resolve | Physical network, server contract, system prompt, or App Store delivery |
| L2 | Unit/Swift Testing and deterministic fixtures | Parsing, schema, cancellation mapping, retry, dedupe, and domain policy | Wi-Fi/cellular behavior or OS-owned UI |
| L3 | Simulator/XCUI/system-flow run | Repeatable app states, layout, accessibility navigation, fixture transport | Local-network permission, real path loss, radio, background timing, hardware thermals |
| L4 | Physical-device run | Wi-Fi/cellular, local permission, Bonjour, path change, background transfer, real server/device interaction | Production signing, App Review, fleet-wide reliability |
| L5 | Release/archive/TestFlight/production evidence | Signed configuration, endpoint/environment, privacy metadata, and release flow | A guarantee for every user/device/network |

Do not use a higher-level claim without preserving the lower-level artifacts that
support it.

## Source and configuration rows

| ID | Claim | Minimum evidence | Common false proof | Acceptance |
| --- | --- | --- | --- | --- |
| SRC-01 | The API route is documented for the selected SDK | Apple URL, symbol, availability note, target SDK record | A blog or autocomplete result | Source link and target decision recorded |
| CFG-01 | Session configuration is intentional | Target code and configuration test for default/ephemeral/background behavior | URLSession.shared only | Cache/cookie/timeout/background policy is named |
| CFG-02 | ATS is secure and narrow | Archive Info.plist, ATS inspection, endpoint TLS test | Request works on a permissive debug machine | HTTPS/TLS works with no unreviewed global exception |
| CFG-03 | Local-network privacy is configured | Info.plist and physical permission run | Bonjour discovery on a previously granted device | Usage description, service types, denial/repair path proved |
| CFG-04 | Entitlements match the route | Signed archive entitlements and target capabilities | Capability checkbox alone | Signed target contains only required entitlements |
| CFG-05 | Endpoint policy is allowlisted | Request builder tests and release configuration | A string URL assembled from user input | Host/scheme/redirect policy is deterministic and tested |

## Request/response rows

| ID | Claim | Test | Evidence | Failure boundary |
| --- | --- | --- | --- | --- |
| HTTP-01 | A bounded GET/POST succeeds | Fixture server returns expected status/content type/schema | Request ID, status, decoded fixture, local commit | A 200 with invalid schema fails |
| HTTP-02 | Status errors map safely | 401, 403, 404, 409, 429, 5xx fixtures | Domain error table and UI screenshots | Raw response body is not shown/logged |
| HTTP-03 | Response limits hold | Oversized Content-Length and streamed/unknown-size body | Limit test and cancellation log | Decoder is not allowed unbounded input |
| HTTP-04 | Authentication is scoped | Expired token, refresh, sign-out, account change | Redacted request log and state transition | Tokens/cookies are not logged or uploaded |
| HTTP-05 | Cancellation is real | Cancel during DNS/TLS/body decode/commit boundary | Task cancellation and domain state evidence | UI says canceled while task still mutates |
| HTTP-06 | Retry is safe | Timeout, offline, 429/Retry-After, 5xx, duplicate tap | Attempt/idempotency trace | Mutation is replayed without a dedupe contract |
| HTTP-07 | Redirect policy is safe | Redirect to allowed and disallowed host/scheme | Delegate decision and test output | Credentials follow an untrusted redirect |
| HTTP-08 | Offline local work survives | Disable network, edit/save/read locally | On-device local record and later retry | Feature requires a spinner to display local state |

## AsyncBytes/stream rows

| ID | Claim | Test | Evidence | Acceptance |
| --- | --- | --- | --- | --- |
| STR-01 | Stream framing is correct | One event per line, split UTF-8, multiple events per chunk | Parser fixture tests | No chunk-boundary assumptions |
| STR-02 | Oversized frame is rejected | One line/frame above limit | Error and bounded memory result | Parser stops without retaining unbounded data |
| STR-03 | Schema is validated per event | Missing field, wrong type, unknown version, bad sequence | Typed parser errors | Invalid event cannot update committed state |
| STR-04 | Early close is incomplete | Server closes before final marker | Incomplete state and UI copy | Partial output is not labeled complete |
| STR-05 | User cancel reaches transport | Cancel during first byte, middle, finalization | Task/operation cancellation trace | Cancel does not race into Apply |
| STR-06 | Backpressure/update batching holds | High-frequency fixture stream | Main-actor update count/hitch evidence | UI remains responsive and accessible |
| STR-07 | Source revision is rechecked | Change source while stream runs | Proposal rejected/rerun trace | Stale output cannot overwrite new source |
| STR-08 | Privacy policy holds | Sensitive fixture with redacted logs | Log review and endpoint policy | Prompt/transcript/file is not accidentally logged |

## WebSocket rows

| ID | Claim | Test | Evidence | Acceptance |
| --- | --- | --- | --- | --- |
| WS-01 | Handshake/auth works | Valid, expired, wrong subprotocol, redirect/close | Handshake result and redacted headers | Only expected endpoint/protocol accepted |
| WS-02 | Messages are bounded | Max accepted, oversized, binary/text mismatch | Size/error test | Message size cannot exhaust memory |
| WS-03 | Ping/idle policy works | Delayed pong, idle timeout, server close | Close reason and state trace | Disconnected state is honest |
| WS-04 | Ordering is enforced | Out-of-order/duplicate sequence | Cursor/rejection test | Domain applies each event once |
| WS-05 | Reconnect/resume works | Wi-Fi off/on, app background/foreground, server restart | Resume cursor and snapshot diff | No silent data loss or duplicate command |
| WS-06 | Commands are idempotent | Duplicate command ID after timeout | Server/client operation trace | One domain effect for repeated delivery |
| WS-07 | Token refresh is safe | Expire token during session | Reauth and resubscribe trace | No credential leakage or infinite reconnect |
| WS-08 | Socket is not only storage | Kill process and rebuild from durable snapshot/cursor | Relaunch state and reconciliation result | Feature recovers without old socket memory |

## Network Framework and local-service rows

| ID | Claim | Test | Evidence | Acceptance |
| --- | --- | --- | --- | --- |
| NW-01 | NWConnection lifecycle is handled | setup, preparing, waiting, ready, failed, canceled | State trace and UI state | Ready is not treated as authenticated/committed |
| NW-02 | Partial reads are framed | Split and coalesced messages | Buffer/framing fixtures | One callback is not assumed to equal one message |
| NW-03 | Send backpressure is handled | Slow peer and large send | Queue bound and cancellation evidence | Unbounded send queue is not created |
| NW-04 | Peer identity is verified | Wrong device, wrong protocol, revoked pair | Pairing/auth trace | Bonjour name/IP alone cannot authorize |
| NW-05 | NWBrowser/NWListener declarations work | Discover, deny permission, service disappears | Physical device prompt and discovery log | Denial is recoverable and explained |
| NW-06 | Path changes are handled | Wi-Fi to cellular, Wi-Fi loss, airplane mode | NWPathMonitor plus actual connection result | Monitor is not reported as request proof |
| NW-07 | TLS/protocol stack is intentional | Expected and invalid peer cert/protocol | Security/protocol test | No insecure fallback appears silently |

## Background transfer rows

| ID | Claim | Test | Evidence | Acceptance |
| --- | --- | --- | --- | --- |
| BG-01 | Background session is configured | Stable identifier, delegate, target capabilities | Archive/configuration record | The session can be recreated after relaunch |
| BG-02 | Download file is owned safely | Complete, partial, corrupt, wrong type, wrong size | Hash/type/size/move trace | Temporary file is not used as durable import |
| BG-03 | Upload survives process state | Start, background, terminate/relaunch where supported | Delegate/task reconciliation | UI does not require the original process instance |
| BG-04 | Cancellation is durable | Cancel before/after callback/relaunch | Transfer state and server policy | Canceled item is not later imported |
| BG-05 | Authentication challenges are handled | Expired credentials/certificate failure | Redacted challenge outcome | App does not weaken trust |
| BG-06 | Completion is domain-specific | Transfer complete but import/compile fails | Separate transfer/import/commit states | Bytes transferred is not “feature ready” |
| BG-07 | Large work has policy | Expensive/constrained path, storage pressure | User/system policy trace | Background session is not a general compute escape hatch |

## AI proposal and local-first rows

| ID | Claim | Test | Evidence | Acceptance |
| --- | --- | --- | --- | --- |
| AI-01 | Source provenance survives | Source ID/revision/model route fixture | Proposal record | Result links to current source |
| AI-02 | Remote/local choice is explicit | Local available/unavailable, path available/unavailable | Decision trace and UI copy | Sensitive data is not silently rerouted |
| AI-03 | Partial output remains draft | Cancel/early EOF/malformed event | Draft status and no commit | No partial answer becomes approved fact |
| AI-04 | Apply is validated | Delete/edit source during inference | Source-revision rejection/rerun | Stale proposal cannot mutate current record |
| AI-05 | Commit is idempotent | Double tap/repeated App Intent/retry | One durable mutation | Duplicate action is safe |
| AI-06 | Projection follows commit | Widget/Live Activity/App Intent after local transaction | Revision/timestamp evidence | Projection is not the domain source |
| AI-07 | Privacy/retention is honored | Logs, crash diagnostics, analytics, cache review | Redacted artifact inspection | Prompts/transcripts/files are not exposed |

## UI and accessibility rows

| ID | Claim | Test | Evidence | Acceptance |
| --- | --- | --- | --- | --- |
| UI-01 | State is understandable | Offline, connecting, streaming, incomplete, retry | Screenshots and copy review | Text/icon/action clarify state |
| UI-02 | Liquid Glass adapts | Light/dark, tinted/clear/system context, reduced transparency | Device screenshots | Glass does not hide content or become faux system UI |
| UI-03 | Dynamic Type works | Largest accessibility sizes, long localized strings | Screenshots and UI test | Source/result/actions remain reachable |
| UI-04 | VoiceOver path works | Focus through status, content, cancel, retry, apply | Accessibility tree/recording | Meaningful transitions are announced |
| UI-05 | Reduced motion works | Reduce Motion on during stream/reconnect | Device run | No essential information is animation-only |
| UI-06 | Alternate input works | Voice Control, Switch Control, keyboard/controller where relevant | Device evidence | No gesture-only recovery or permission route |
| UI-07 | Privacy projection works | Locked device, notification/widget preview, redacted mode | Device screenshots | Sensitive content is not exposed unexpectedly |

## Release and live-service rows

| ID | Claim | Test | Evidence | Acceptance |
| --- | --- | --- | --- | --- |
| REL-01 | Release endpoint is correct | Release configuration inspection | Archive/environment record | No staging host or debug bypass |
| REL-02 | Signed metadata is correct | Archive entitlements, Info.plist, privacy strings | Exported archive inspection | Required declarations are in signed product |
| REL-03 | Production TLS/auth works | TestFlight/release build against production | Redacted live operation trace | Debug-only trust does not mask failure |
| REL-04 | Server operation is observable | Operation ID, request ID, status endpoint/log correlation | Support-safe trace | Client cannot claim effect without evidence |
| REL-05 | Background/system behavior is delivered | Physical release or TestFlight device | Notification/transfer/system-surface evidence | Simulator/preview does not substitute |
| REL-06 | Performance is acceptable | Device timing/hitch/memory/power runs | XCT/MetricKit/signpost artifacts | Debug simulator speed is not release evidence |

## Test fixture matrix

Exercise each route with:

- healthy HTTPS response;
- invalid status/content type/schema;
- slow headers/body;
- split and coalesced stream frames;
- empty stream and early close;
- oversized body/frame/message;
- cancellation at every phase;
- DNS/TLS/auth failure;
- offline, Wi-Fi loss, cellular, expensive/constrained path;
- local-network permission allowed/denied;
- Bonjour service present/disappeared/wrong protocol;
- WebSocket duplicate/out-of-order/reconnect;
- background transfer relaunch/cancel/corrupt file;
- source changed during AI inference;
- locked device and redacted projection;
- largest Dynamic Type, VoiceOver, reduced motion/transparency;
- app process termination and cold launch.

## Evidence package

A reviewable package should include:

- target name, SDK, deployment target, device model and OS;
- source URLs and API notes;
- code commit or local diff identifier;
- test fixture/server version;
- redacted logs with request/operation IDs;
- screenshots or recordings for state/accessibility/system prompts;
- archive Info.plist and entitlements;
- device network conditions;
- model/provider route and source revision;
- known limitations and unproved claims.

Do not include live credentials, tokens, private prompts, raw transcripts, personal
files, or unredacted local-network identifiers in the package.

## Stop conditions

Stop and fix the route when:

- a transport callback is treated as a durable domain commit;
- a path monitor is presented as proof of internet availability;
- a partial stream is labeled final;
- retry can duplicate a consequential mutation;
- local-network discovery is treated as authentication;
- ATS is weakened globally to hide a server failure;
- background transfer completion is treated as successful import/installation;
- an on-device AI claim is based only on a remote route;
- a preview/simulator result is described as physical-device or release evidence;
- the UI depends on color, motion, glass, or a gesture without an accessible
  equivalent.

## Sources

- [URL Loading System](https://developer.apple.com/documentation/foundation/url-loading-system)
- [URLSessionConfiguration](https://developer.apple.com/documentation/foundation/urlsessionconfiguration)
- [URLSession.AsyncBytes](https://developer.apple.com/documentation/foundation/urlsession/asyncbytes)
- [URLSessionWebSocketTask](https://developer.apple.com/documentation/foundation/urlsessionwebsockettask)
- [URLSessionTaskDelegate](https://developer.apple.com/documentation/foundation/urlsessiontaskdelegate)
- [Downloading files in the background](https://developer.apple.com/documentation/foundation/downloading-files-in-the-background)
- [Network](https://developer.apple.com/documentation/network)
- [NWConnection](https://developer.apple.com/documentation/network/nwconnection)
- [NWBrowser](https://developer.apple.com/documentation/network/nwbrowser)
- [NWListener](https://developer.apple.com/documentation/network/nwlistener)
- [NWPathMonitor](https://developer.apple.com/documentation/network/nwpathmonitor)
- [NWProtocolWebSocket](https://developer.apple.com/documentation/network/nwprotocolwebsocket)
- [NSAppTransportSecurity](https://developer.apple.com/documentation/bundleresources/information_property_list/nsapptransportsecurity)
- [NSLocalNetworkUsageDescription](https://developer.apple.com/documentation/bundleresources/information_property_list/nslocalnetworkusagedescription)
- [NSBonjourServices](https://developer.apple.com/documentation/bundleresources/information-property-list/nsbonjourservices)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Performing accessibility testing for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
