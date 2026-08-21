# SwiftUI MultipeerConnectivity peer-session proof matrix

MultipeerConnectivity crosses an app target, local-network privacy, Bonjour,
two or more physical devices, session delegates, a user invitation, and a
transport/application protocol. This matrix keeps those evidence layers
separate and records the migration boundary to Network Framework.

## Claim-to-evidence matrix

| Claim | Minimum evidence | Strong evidence | Does not prove |
| --- | --- | --- | --- |
| MC is the correct route | Decision record against Network, Nearby Interaction, Group Activities, and accessory routes | Existing product behavior or compatibility test shows the MC adapter is required | A peer-shaped screen or a successful import |
| The new app uses the modern route | Architecture review and Network Framework source links | Network connection/browser/listener runs on two signed physical devices | A deprecation warning suppressed in source |
| The local peer identity is stable | Secure archive/reload unit fixture | Relaunch, background/foreground, and reinstall-policy test preserve the intended identity | A display name that looks the same |
| A peer is discoverable | Browser/advertiser callback fixture | Two physical devices find each other with local-network access in the recorded environment | A mocked MCPeerID |
| Local-network permission is correct | Info.plist and denial-state test | Fresh install prompts with the truthful purpose, denied state repairs in Settings, and extension/container placement is correct | A usage string checked into source |
| An invitation is user-mediated | Delegate decision fixture | Physical accept/reject/expiry flow shows scope and creates a session only after approval | Auto-accepting an invitation in a unit test |
| Session encryption policy is enforced | MCEncryptionPreference and mismatch fixture | Physical peers complete required encryption or reject without downgrade | A connected state badge |
| Delegate lifecycle is safe | Queue/actor adapter test | Physical peer connect/disconnect/background callbacks update SwiftUI without races or stale reopen | A callback printed to a log |
| Data delivery is reliable enough | Framing/idempotence/revision tests | Two devices send repeated, reordered, rejected, and disconnected messages with application receipts | send returning without error |
| Resource transfer is correct | Temporary-URL, hash, size, and destination fixture | Physical file transfer shows progress, cancellation, validation, safe move, and reconnect behavior | A received temporary URL |
| Stream transfer is correct | Partial-read/write and frame-boundary fixture | Physical stream handles backpressure, close, cancellation, and malformed lengths | Opening an OutputStream |
| Peer reconnect is correct | Session-epoch reducer test | Background/foreground and radio/network interruption rebuild the session and prevent stale resume | A foreground spinner |
| SwiftUI surface is native | View inspection and accessibility audit | Complete discovery-to-transfer task under Dynamic Type, VoiceOver, reduced effects, keyboard, and Switch Control | A glass screenshot |
| AI is subordinate | Typed proposal and stale-revision fixture | Model unavailable/refusal/stale candidate leaves manual flow usable and only an explicit user action sends | A plausible model sentence |
| Privacy is bounded | Redacted logs and prompt fixture | No raw context, file content, credential, or unnecessary peer identity is logged or sent to AI | An empty analytics dashboard |
| Release configuration is real | Archive target/Info.plist/profile inspection | TestFlight build on named devices completes the two-device route with recorded OS/builds | Simulator success or host-only archive |

## Evidence layers

~~~text
source layer
  -> current Apple docs, headers, deprecation/migration record
compile layer
  -> Swift adapter and SwiftUI target typecheck
configuration layer
  -> Info.plist, privacy manifest, target membership, signing
simulation layer
  -> deterministic state/framing/error fixtures
physical layer
  -> two-device discovery, invite, session, transfer, disconnect
accessibility layer
  -> task completion with alternate settings and input
release layer
  -> archive/TestFlight artifact and target-device re-run
~~~

Do not promote evidence from one layer into a stronger claim. A compiler can
prove symbol usage; it cannot prove radio discovery. A physical data callback
can prove receipt at the MC layer; it cannot prove domain application or user
intent.

## Fixture model

Use synthetic, redacted values:

~~~text
PeerFixture
  peerCorrelation: test-peer-A
  displayName: Test Device A
  serviceType: bishop-sync
  discoveryRevision: 12
  protocolVersion: 2

InvitationFixture
  inviter: test-peer-A
  context: bounded versioned bytes
  decision: pending | accepted | rejected | expired

SessionFixture
  epoch: 42
  state: notConnected | connecting | connected
  encryption: required | optional | none
  connectedPeers: [test-peer-A]

TransferFixture
  transferID: transfer-7
  kind: message | resource | stream
  sourceRevision: 18
  bytes: synthetic payload
  state: queued | sending | received | validated | applied | canceled | failed

ProposalFixture
  sourceDiscoveryRevision: 12
  peerCorrelation: test-peer-A
  action: inspect | invite | prepareTransfer
  decision: review | approved | rejected | stale
~~~

Never commit real peer names, local IP addresses, invitation context, files,
account tokens, or production logs in fixtures.

## Deterministic reducer checks

Test without a radio, local network, or model:

- a discovery candidate is not authenticated because it was found;
- a lost peer cannot be invited after its candidate epoch expires;
- an invitation handler resolves exactly once on accept, reject, cancel, and
  expiry;
- a new session epoch invalidates messages from a previous session;
- reliable duplicate messages are idempotent;
- unreliable events tolerate drops and never directly commit an irreversible
  side effect;
- a resource with wrong content type, size, hash, or revision is rejected;
- a resource destination is not adopted until the file is moved/validated;
- a stream parser handles partial headers, partial payloads, zero lengths, and
  oversized lengths;
- cancellation does not allow late callbacks to restore a completed transfer;
- a peer disconnect preserves the draft and reports uncommitted work;
- a typed AI proposal is invalidated when candidate/session/source revision
  changes;
- AI cannot choose a peer outside the user-selected allowlist or call transport
  methods directly.

## Physical-device matrix

| Task | Setup | Observe | Record |
| --- | --- | --- | --- |
| Fresh permission | Delete/reinstall on two devices | Truthful local-network prompt and allowed route | OS/build, Info.plist, decision |
| Denied permission | Deny Local Network | Discovery fails with repair/fallback, no fake empty success | Error and Settings recovery |
| Advertise/browser | Both devices foreground, same service type | Found/lost events and bounded candidate metadata | Peer correlations and timestamps |
| Invitation accept | Select device A from device B | Invitee sees scope, accepts, both reach handshaking/ready | Context revision and session epoch |
| Invitation reject/expiry | Reject or let timeout pass | No session or stale selected state remains | Decision and cleanup |
| Encryption mismatch | Configure incompatible test policy where supported | Connection rejects or surfaces a safe error; no silent downgrade | Policy and result |
| Message | Send versioned reliable and unreliable fixtures | Receiver validates, deduplicates, and applies/rejects | Send/receive/application IDs |
| Resource | Transfer a synthetic file | Progress, cancel, temporary URL move, hash/type validation | Content revision and final state |
| Stream | Send fragmented frames and close mid-frame | Partial reads, backpressure, truncation, retry path | Frame counts and errors |
| Background | Background each app during discovery and session | Discovery/session behavior matches Apple lifecycle; foreground rebuilds | State transitions |
| Peer loss | Walk out of range or stop advertising | Draft/transfer state remains honest; reconnect is explicit | Disconnect reason and resume decision |
| Accessibility | VoiceOver, Dynamic Type, Reduce Motion/transparency, Switch Control | Full task completes and statuses are understandable | Task log and defects |
| AI fallback | Disable model/unavailable/refusal/stale input | Manual path remains complete; no silent invitation/send | Model state and reviewer action |

Run the same matrix on the signed TestFlight artifact. A Debug build on one
device is not release evidence for a nearby feature.

## Archive and release record

Capture the following per build:

~~~text
transport decision: MC legacy adapter | Network modern route
framework deprecation reviewed: yes/no
SDK/Xcode/build: recorded
deployment target: recorded
host target: compiled/embedded
extensions: compiled/embedded or none
NSLocalNetworkUsageDescription: present/truthful
NSBonjourServices: present/correct or not applicable
privacy manifest/log review: passed/failed
two physical devices: named and OS/build recorded
permission states: unknown/allowed/denied/revoked tested
session encryption policy: recorded
message/resource/stream proof: recorded
background/reconnect proof: recorded
accessibility proof: recorded
TestFlight artifact: recorded
production behavior: unverified until observed
~~~

## Sources

- [Multipeer Connectivity](https://developer.apple.com/documentation/multipeerconnectivity)
- [MCSession](https://developer.apple.com/documentation/multipeerconnectivity/mcsession)
- [MCSessionDelegate](https://developer.apple.com/documentation/multipeerconnectivity/mcsessiondelegate)
- [MCPeerID](https://developer.apple.com/documentation/multipeerconnectivity/mcpeerid)
- [MCNearbyServiceAdvertiser](https://developer.apple.com/documentation/multipeerconnectivity/mcnearbyserviceadvertiser)
- [MCNearbyServiceBrowser](https://developer.apple.com/documentation/multipeerconnectivity/mcnearbyservicebrowser)
- [MCSessionSendDataMode](https://developer.apple.com/documentation/multipeerconnectivity/mcsessionsenddatamode)
- [Moving from Multipeer Connectivity to Network framework](https://developer.apple.com/documentation/technotes/tn3213-moving-from-multipeer-connectivity-to-network-framework)
- [Understanding local network privacy](https://developer.apple.com/documentation/technotes/tn3179-understanding-local-network-privacy)
- [Privacy - Local Network Usage Description](https://developer.apple.com/documentation/bundleresources/information_property_list/nslocalnetworkusagedescription)
- [Privacy - Bonjour Services](https://developer.apple.com/documentation/bundleresources/information_property_list/nsbonjourservices)
- [Network](https://developer.apple.com/documentation/network)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
