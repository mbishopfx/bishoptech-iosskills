# SwiftUI Network Framework modern peer-transport proof matrix

Nearby networking needs evidence across source, compile, configuration,
permission, physical devices, accessibility, and release. Keep those layers
separate. A successful simulator connection or a green Network Framework
state does not prove local-network permission, Apple peer-to-peer Wi-Fi,
identity, user approval, or a TestFlight build.

## Claim-to-evidence matrix

| Claim | Minimum evidence | Strong evidence | Does not prove |
| --- | --- | --- | --- |
| Modern Network Framework is the correct route | Architecture decision against MC, URLSession, Bluetooth, SharePlay, and accessory routes | New NetworkConnection/Listener/Browser path runs on two signed physical devices | A deprecated MC prototype |
| A service is advertised | NetworkListener source, Info.plist, and service registration fixture | Physical listener reaches ready and reports the registered Bonjour endpoint | Listener initializer returned |
| A peer is discoverable | NetworkBrowser state and endpoint fixture | Two devices browse the same declared service after permission | A hard-coded NWEndpoint |
| Local-network privacy is correct | Truthful NSLocalNetworkUsageDescription and NSBonjourServices inspection | Fresh install prompts in context; denial shows repair/fallback; revocation is handled | Keys merely existing in a source file |
| Apple peer-to-peer Wi-Fi is supported | peerToPeerIncluded configuration and supported-device decision | Two compatible devices complete the route with the intended path recorded | Setting a Boolean |
| A discovered peer is trusted | Handshake and pairing decision fixtures | Wrong proof, stale nonce, wrong peer, and revoked pairing fail on devices | Matching display name or TXT record |
| TLS policy is correct | Stack and peer-authentication source review | Physical mismatch or invalid identity fails without downgrade | A ready state with encryption assumed |
| A typed message is safe | Codable/TLV/framer parser tests with bounds | Physical duplicate, stale, malformed, and incompatible messages are rejected or applied idempotently | send returning without error |
| A transfer is complete | Manifest, size, hash, and temporary destination fixture | Physical transfer reaches validated and applied receipt after interruption/reconnect | A received byte count |
| Backpressure is correct | Awaited send/receive and bounded queue test | Sustained physical transfer remains responsive and does not grow unbounded memory | A fast small-message demo |
| Reconnect is safe | Epoch reducer and cancellation tests | Background, path loss, peer loss, rediscovery, handshake, and resume run on devices | Recreating a connection object |
| SwiftUI state is native | View-state and accessibility inspection | VoiceOver, Dynamic Type, Reduce Motion/Transparency, keyboard, and Switch Control complete the task | A glass screenshot |
| AI is subordinate | Typed proposal, stale revision, and unavailable-model fixtures | User review gates the exact operation and manual path works with no model | A plausible recommendation |
| The release artifact is real | Archive, entitlements, Info.plist, and target inspection | TestFlight build repeats the two-device matrix with recorded OS/builds | Simulator or Debug-only success |

## Evidence layers

~~~text
source layer
  -> current Apple docs, migration guidance, SDK availability
compile layer
  -> recipe fences typecheck against the target SDK
configuration layer
  -> Info.plist, privacy keys, target membership, signing
deterministic layer
  -> reducer, parser, epoch, handshake, transfer fixtures
permission layer
  -> fresh, allowed, denied, revoked local-network states
physical layer
  -> two-device browse, connect, authenticate, transfer, disconnect
accessibility layer
  -> task completion with alternate settings and input
release layer
  -> archive/TestFlight artifact and repeated device route
~~~

Do not promote evidence from one layer into another. The compiler can prove
that a symbol is available; it cannot prove that Bonjour registration works on
the customer’s network. A physical byte receipt can prove transport delivery;
it cannot prove that a document was authorized and applied.

## Deterministic fixtures

Use synthetic values:

~~~text
PeerFixture
  candidateID: test-peer-A
  displayName: Test Device A
  serviceType: _bishop-sync._tcp
  discoveryRevision: 12
  protocolVersion: 2
  trust: unknown | paired | blocked

HandshakeFixture
  peerID: test-peer-A
  sessionEpoch: 42
  nonce: synthetic-nonce-A
  proof: valid | wrong-peer | stale | revoked

TransferFixture
  transferID: transfer-7
  sourceRevision: 18
  byteCount: synthetic
  hash: valid | wrong
  state: queued | sent | received | validated | applied | cancelled | failed

ProposalFixture
  candidateID: test-peer-A
  discoveryRevision: 12
  action: inspect | prepareTransfer
  decision: review | approved | stale | rejected
~~~

Never commit real service names, IP addresses, peer identifiers, invitation
metadata, file content, account tokens, or production logs in fixtures.

## Reducer and parser checks

Test without a network, radio, model, or SwiftUI renderer:

- a browser snapshot creates a candidate but not trust;
- an unknown TXT key is ignored;
- an oversized TXT value is rejected;
- a lost candidate cannot be selected at an old discovery revision;
- a selected candidate cannot skip the review state;
- a connection in waiting is not presented as failed;
- a failed connection does not automatically retry forever;
- a handshake with a reused nonce is rejected;
- a handshake for another peer is rejected;
- an authenticated epoch invalidates all previous messages;
- duplicate message IDs apply at most once;
- unsupported protocol versions have a recoverable error;
- a frame length above the budget fails before allocation;
- partial frame headers and payloads are handled;
- a transfer with wrong size, type, or hash is not imported;
- cancellation does not let a late callback restore a finished transfer;
- peer loss preserves local work and changes the epoch;
- an AI proposal is invalidated when its discovery revision changes;
- model failure leaves the manual action enabled.

## Network Framework configuration matrix

| Case | `localOnly` | `peerToPeerIncluded` | Expected proof |
| --- | --- | --- | --- |
| Infrastructure Wi-Fi local app | true | false or product default | Two devices on the same local network discover and transfer. |
| Nearby Apple-device route | true | true | Compatible physical devices complete with the peer-to-peer opt-in. |
| Local or wider fallback | false | product decision | UI explains the possible path and the privacy review covers it. |
| Metered transfer blocked | product decision | product decision | Expensive/constrained path behavior is visible and safe. |
| Permission denied | any | any | Discovery does not silently present “no devices”; repair/fallback appears. |

Record the actual path only in redacted test notes. Do not publish raw local
addresses or persistent device identifiers.

## Physical-device matrix

| Task | Setup | Observe | Record |
| --- | --- | --- | --- |
| Fresh permission | Delete/reinstall signed build on two devices | Truthful local-network explanation and system prompt | OS, build, decision, timestamp |
| Denied permission | Deny Local Network | Repair path, no false empty success | Error state and Settings recovery |
| Listener | Host app foreground, declared service | Ready state and registration callback | Requested versus actual service |
| Browser | Client app foreground, same service type | Candidate appears and refreshes | Discovery revision and redacted ID |
| Selection | Tap a candidate | Review sheet identifies peer and operation | Approval decision |
| Authentication | Pair or provide test proof | Valid proof succeeds; wrong/stale proof fails | Epoch and failure category |
| Typed message | Send valid, duplicate, oversized, and stale messages | Receiver validates/deduplicates/applies | Message IDs and receipts |
| Large transfer | Synthetic file with known hash | Progress, validation, import, application | Manifest and final state |
| Path interruption | Change network or move out of range | Waiting/reconnect state is honest | Path state and retry |
| Background | Background each app during route | Lifecycle behavior and foreground recovery | State sequence |
| Peer loss | Stop advertising or close peer | Work remains safe; retry is explicit | User action and new epoch |
| Accessibility | VoiceOver, Dynamic Type, Reduce Motion/Transparency, Switch Control | Full route is completable | Task log and defects |
| AI fallback | Disable/unavailable/refusal/stale proposal | Manual route remains complete | Model state and reviewer action |
| TestFlight | Install the signed beta artifact | Same two-device route works | App version/build and devices |

## SwiftUI/Liquid Glass review

Check that:

- the screen explains local-network access in context;
- a candidate is not visually presented as authenticated;
- glass groups actions rather than hiding data or status;
- reduced transparency retains contrast and grouping;
- reduced motion retains state changes and focus;
- VoiceOver hears candidate, trust, operation, transfer, and application
  status;
- keyboard and Switch Control can reach every action;
- an error or waiting state does not inherit a success color or animation;
- AI text is clearly optional and never replaces the manual action.

## Archive and release record

Capture the following per build:

~~~text
transport route: modern Network Framework
framework availability reviewed: yes/no
Xcode / SDK / build: recorded
deployment target: recorded
NSLocalNetworkUsageDescription: present and truthful
NSBonjourServices: present and exact
localOnly: recorded
peerToPeerIncluded: recorded
TLS / handshake / pairing policy: recorded
maximum message/frame/transfer sizes: recorded
privacy manifest and logging review: passed/failed
two physical devices: named and OS/build recorded
permission states: fresh/allowed/denied/revoked
background and path interruption: passed/failed
accessibility: passed/failed
AI unavailable/stale/manual fallback: passed/failed
TestFlight artifact: recorded
production behavior: unverified until observed
~~~

Run the matrix on the signed TestFlight artifact. Keep simulator and
typecheck evidence as compile or deterministic evidence, not as proof of
nearby radio behavior.

## Sources

- [Network Framework modern peer-transport route](../42-framework-deep-dives/139-swiftui-network-framework-modern-peer-transport-route.md)
- [Network](https://developer.apple.com/documentation/network)
- [NetworkConnection](https://developer.apple.com/documentation/network/networkconnection)
- [NetworkListener](https://developer.apple.com/documentation/network/networklistener)
- [NetworkBrowser](https://developer.apple.com/documentation/network/networkbrowser)
- [NetworkChannel](https://developer.apple.com/documentation/network/networkchannel)
- [NetworkChannel.State](https://developer.apple.com/documentation/network/networkchannel/state-swift.enum)
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
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
