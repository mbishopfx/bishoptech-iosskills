# Nearby Interaction and peer transport proof matrix

This matrix separates discovery, identity, transport, proximity measurement, physical experience, data delivery, and side effects. A nearby candidate or a ready connection does not prove that the person selected the correct peer or that an action completed.

## Evidence levels

| Level | Evidence | What it proves |
| --- | --- | --- |
| L0 | Official route and platform review | Selected NI, Network, MC, privacy, HIG, deprecation, and device boundaries are known. |
| L1 | Protocol/state fixtures | Candidate validation, token lifetime, message framing, revisions, idempotence, cancellation, and fallback. |
| L2 | Simulator/preview/two-process fixture | UI states, candidate selection, manual route, accessibility identifiers, and non-hardware transport behavior. |
| L3 | Signed two-device/accessory run | Permission, token exchange, session callbacks, distance/direction, data connection, and physical context. |
| L4 | Long-session/network test | Reconnect, path change, throughput, latency, battery, thermal, obstruction, and background/foreground behavior. |
| L5 | Release artifact | Local-network/Bonjour declarations, capabilities, supported-device metadata, signing, privacy, and target/extension configuration. |

## Capability and target

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Nearby Interaction is supported | SDK compile plus runtime capability check on named devices | iPhone support does not imply every iPad/watch/accessory/platform route. |
| Direction/distance is available | Signed physical run with orientation and device field-of-view cases | A distance value does not guarantee direction or accuracy. |
| Accessory NI route works | Accessory protocol/configuration-data exchange on named firmware/device | An app-only peer run is not accessory proof. |
| Network Framework route works | Target compile, local-network usage string/Bonjour declaration, signed connection | A socket compile does not prove permission, encryption, or peer protocol. |
| Multipeer legacy route works | MC target/session run with foreground return | Existing MC behavior does not establish a recommended new architecture. |

## Discovery and trust

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Candidate discovery works | Browse/advertise fixtures, no results, duplicates, malformed metadata | Discovery is not identity. |
| Person selected a peer | Selection/accept/reject/cancel UI and state | A strongest signal or display name is not consent. |
| Identity/protocol handshake works | Wrong peer, stale session, replay, version mismatch, invalid payload | NI discovery tokens are session inputs, not permanent IDs. |
| Secure transport works | Named parameters/security, invalid credentials, tampered/oversized messages | A ready connection is not authorization for every domain action. |

## Nearby Interaction

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Peer token exchange works | Fresh token, wrong token, expired token, session restart | Tokens must be scoped to the interaction session and discarded at teardown. |
| NI session lifecycle works | Run, updates, suspend, invalidate, stop, peer disappearance | A single update does not prove continuous operation. |
| Direction works | Portrait/landscape, field-of-view, distance, obstructions, cases, crowded space | Direction can be unavailable while distance remains. |
| Distance works | Multiple ranges, movement, noise, interruptions, stale update | A sensor estimate is not a surveyed measurement or location proof. |
| Multiple targets work | Separate session policy, candidate switching, teardown | One NISession does not represent every nearby object. |

## Transport and protocol

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| NWBrowser/NWListener route works | Browse/listen state, local network allow/deny, service changes, cancel | A Bonjour result is untrusted candidate metadata. |
| NWConnection route works | Framing, partial reads, backpressure, close, path change, reconnect | Ready state does not mean domain data delivered. |
| MCSession route works | Invite accept/reject, peer state, resource/message errors, background disconnect | MC background behavior requires reestablishment; do not claim continuity. |
| Data delivery works | Sequence/revision/ack, duplicate/replay, out-of-order, timeout, resync | One successful message does not prove every payload or side effect. |
| Side effect works | Explicit confirmation, idempotent application, outcome response, retry | Transport completion is not domain completion. |

## Design, accessibility, and AI

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Spatial UI is understandable | Continuous visual/audio/haptic feedback, direction-loss/obstruction/manual states | An arrow/glow is not a truthful state by itself. |
| Non-spatial route works | Candidate list/manual selection without NI | Physical movement cannot be the only route unless the product’s core outcome requires it. |
| Accessibility works | VoiceOver, Voice Control, Switch Control, Dynamic Type, Reduce Motion/transparency | Haptics/audio cannot be the only output. |
| AI is bounded | Fixed candidate/context fixtures, typed proposal, stale invalidation, confirmation | AI cannot identify a person, grant consent, or silently transfer/control. |
| Liquid Glass is native | State variants, safe hit targets, adaptive layout, system handoff | Decorative glass does not prove platform polish. |

## Performance and release

| Claim | Required evidence |
| --- | --- |
| Responsive proximity | Named-device latency, update freshness, direction/distance transition measurements. |
| Reliable local session | Long session, path changes, reconnect, peer loss, throughput, memory, energy, and thermal. |
| Release-ready | Archive inspection for local network/Bonjour/capabilities, supported-device matrix, privacy review, and signed system run. |

## Evidence packet

Record:

~~~text
feature:
target/bundle/build:
sdk/deployment target:
device/accessory/firmware:
ni capability:
network/mc route:
local network/bonjour configuration:
candidate/selection:
identity handshake:
token/configuration lifetime:
transport protocol/revision:
direction/distance conditions:
obstruction/orientation:
accessibility settings:
ai model/context:
latency/throughput/energy/thermal:
known failures:
claim supported:
~~~

## Claim language

Use:

- “The signed two-device run exchanged session-scoped discovery tokens and received Nearby Interaction updates on the named hardware.”
- “The Network Framework connection delivered versioned, idempotent messages after explicit peer selection and handshake.”
- “When direction was unavailable, the UI switched to a distance/manual route and did not display a confident arrow.”
- “The AI ranked selected candidates and required confirmation; it did not infer identity or apply a transfer.”

Avoid:

- “Nearby devices are trusted.”
- “Works in the background” from a foreground run.
- “The arrow is accurate” without orientation/obstruction/device evidence.
- “The file was sent” from a connection-ready or send callback alone.

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
- [Nearby interactions HIG](https://developer.apple.com/design/human-interface-guidelines/nearby-interactions/)
- [Accessibility HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
