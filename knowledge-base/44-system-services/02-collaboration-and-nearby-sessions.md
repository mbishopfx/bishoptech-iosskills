# Collaboration and Nearby Sessions

SharePlay/Group Activities and nearby peer connectivity solve different problems. Group Activities uses the system’s conversation/share context to create a coordinated activity; Multipeer Connectivity discovers nearby app instances and creates a direct peer session. Neither one is a general database, identity provider, or guaranteed delivery channel.

## Route matrix

| User outcome | First route | Target/configuration boundary | Proof that matters |
| --- | --- | --- | --- |
| Coordinate a shared experience from FaceTime, Messages, or the share sheet | [Group Activities](https://developer.apple.com/documentation/groupactivities) with `GroupActivity`, `GroupSession`, and the Group Activities capability | App target, `Codable` activity payload, unique `activityIdentifier`, metadata, supported platform/device matrix, and current conversation eligibility | Two or more physical devices with the actual FaceTime/Messages/share entry point, activation/join/leave/invalidation, late join, participant change, and privacy review. |
| Send small, time-sensitive commands or state | `GroupSessionMessenger` with a deliberate reliable or unreliable delivery mode | Active joined `GroupSession`, versioned `Codable` messages, participant/role policy, cancellation and ordering policy | Reconnect, duplicate/out-of-order message, participant subset, oversized payload, session invalidation, and deterministic reconciliation. |
| Share larger files or attachments with a group | `GroupSessionJournal` plus `Transferable` data | Group session lifetime, attachment size/retention policy, content validation, local storage, and redaction | Physical multi-device attachment add/remove/load, late join, unavailable data, cancellation, file-size boundary, and no claim that a journal is durable company storage. |
| Discover and invite nearby app peers | `MCNearbyServiceAdvertiser`, `MCNearbyServiceBrowser`, `MCPeerID`, and `MCSession` | Local-network usage description, `NSBonjourServices`, service-type rules, peer consent, target/device support, and transport/security policy | Two or more physical devices, local-network permission, invite accept/reject, foreground/background transition, disconnect/reconnect, and hostile/misidentified peer handling. |
| Build a new peer transport | Network Framework (`NWBrowser`, `NWListener`, `NWConnection`) after checking the selected SDK | Service discovery, local-network privacy, TLS/identity/authentication, protocol framing, cancellation, and background policy | Physical network fixtures, identity validation, packet loss/reconnect, permission denial, and a protocol test suite; discovery is not identity. |
| Persist shared state across time or devices | CloudKit/shared records or an app-owned server, not a live session object | Container/environment, account, schema, conflict/deletion policy, authentication, offline queue, and server truth | Signed multi-device/environment tests, conflict and deletion recovery, account changes, migration, and server acknowledgement distinct from local send. |
| Measure physical proximity or accessory range | Nearby Interaction or the accessory-specific framework | Hardware support, session/token exchange, user permission, accessory protocol, and camera/UWB/privacy boundary | Supported physical devices/accessory, session invalidation, movement/occlusion, approximate result, and safe physical-world fallback. |

The current Apple `MCSession` documentation marks Multipeer Connectivity’s session route deprecated and points new work toward Network Framework. Keep a legacy Multipeer adapter only when its invitation/browser UX or an existing product requires it; do not build a new security model around a deprecated transport without reviewing the current SDK documentation.

## Group Activities lifecycle

```text
ineligible | idle
    -> preparing -> activationPreferred | activationDisabled | cancelled
    -> activated -> sessionWaiting -> joined
    -> syncing -> participantChanged | attachmentPending
    -> left | invalidated | ended | failed
```

Use `GroupStateObserver`/the activity activation result to decide whether the system can start the experience. The system creates `GroupSession` asynchronously; the app joins only after restoring the activity UI and its local source state. Keep strong references to the session, messenger, journal, and listener tasks for the activity lifetime. Cancel those tasks when the session leaves or becomes invalidated.

For message semantics:

- `GroupSessionMessenger` is for small, time-sensitive `Codable` messages and commands. Give every mutation an event ID, schema version, source participant, logical clock or source revision, and idempotence rule.
- Use reliable delivery for information every participant must receive and unreliable delivery for ephemeral state where freshness matters more than retransmission.
- `GroupSessionJournal` is for larger `Transferable` attachments and late-join availability. Validate content before incorporating it into domain state, and use a server for content that is too large, confidential, or subject to moderation/revocation.
- A participant receiving a message proves transport receipt only. The receiving app must validate authorization, current activity, record version, and side effects locally.

## Nearby peer lifecycle and trust

```text
idle -> permissionPending -> advertising | browsing
advertising/browsing -> invitationPending -> accepted | rejected | expired
accepted -> connecting -> connected -> exchanging
connected -> disconnected -> reconnecting | ended
background -> discoveryStopped/sessionClosed -> foregroundRebuild
```

The Multipeer Connectivity framework stops advertising/browsing and disconnects open sessions when the app enters the background; when it returns to the foreground it resumes discovery, but the app must reestablish closed sessions. Persist only a resumable protocol checkpoint, not a live session object. For Network Framework, define the equivalent listener/browser/connection state machine explicitly.

Nearby discovery is not authentication. Require a user-visible invite/accept boundary, bind the session to an authenticated account or one-time pairing code when the action is sensitive, use an encrypted/authenticated protocol, limit message types, and display the peer identity/context the person is approving. Never infer that a nearby name, Bonjour service, or peer ID represents a trusted person or server.

## Shared protocol contract

Every collaborative event or attachment should carry:

| Field | Purpose |
| --- | --- |
| `schemaVersion` | Reject or migrate unknown message/attachment formats. |
| `activityID`/`sessionID` | Prevent an old session from mutating a new one. |
| `eventID`/`sourceRevision` | Deduplicate and reconcile out-of-order events. |
| `senderParticipantID`/`accountID` | Apply role and authorization checks. |
| `recordID`/`payload` | Keep the payload bounded and resolve the record through current local/server state. |
| `createdAt`/`expiresAt` | Make delayed or stale events visible. |
| `resultState`/`error` | Distinguish sent, received, accepted, applied, rejected, and failed. |

Use a deterministic reducer for remote events. If two participants edit the same record, choose an explicit merge/conflict policy; do not let arrival order silently become domain truth. Keep AI proposals, imported attachments, and user-approved mutations as separate states.

## Privacy, permissions, and release boundaries

- Group Activities requires the Group Activities capability on the app target. Its session data has a system privacy/security boundary, but app-level product data, participant identity, retention, and side effects still require their own review.
- Multipeer Connectivity requires the local-network usage description and, when browsing Bonjour services, the declared service list. The permission prompt does not prove that a peer is safe or that a connection will remain available.
- Do not put account credentials, private record dumps, or unreviewed Foundation Models output into activity metadata, discovery information, logs, notifications, or shared containers.
- App targets, extensions, Watch targets, and visionOS targets may have different Group Activities availability and entitlements. Record each target separately.
- A successful activation, invitation, send call, or connection callback is not proof of group consensus, server persistence, payment, account authorization, or a completed physical-world action.

## Verification matrix

| Evidence level | Checks |
| --- | --- |
| Source/configuration | Current SDK availability, Group Activities capability, local-network usage description, Bonjour services, target membership, entitlements, privacy copy, and protocol schema. |
| Deterministic test | Reducer ordering, duplicate IDs, stale revisions, late join snapshot, attachment validation, invitation policy, cancellation, and conflict resolution. |
| Simulator/preview | UI states for eligible/ineligible, waiting/joined/invalidated, peer list, permission denial, stale data, and fallback. Label transport as simulated. |
| Physical system | FaceTime/Messages/share-sheet SharePlay, two-device GroupSession, two-device nearby discovery, local-network prompt, background/foreground, lock/termination, network loss, and accessibility. |
| Release/service | Signed targets, supported platform/device matrix, account/server/authentication configuration, production privacy/retention, and any App Store capability or review requirements. |

## Sources

- [Group Activities](https://developer.apple.com/documentation/groupactivities)
- [GroupActivity](https://developer.apple.com/documentation/groupactivities/groupactivity)
- [GroupSession](https://developer.apple.com/documentation/groupactivities/groupsession)
- [GroupSessionMessenger](https://developer.apple.com/documentation/groupactivities/groupsessionmessenger)
- [GroupSessionJournal](https://developer.apple.com/documentation/groupactivities/groupsessionjournal)
- [Defining your app’s SharePlay activities](https://developer.apple.com/documentation/groupactivities/defining-your-apps-shareplay-activities)
- [Joining and managing a shared activity](https://developer.apple.com/documentation/groupactivities/joining-and-managing-a-shared-activity)
- [Synchronizing data during a SharePlay activity](https://developer.apple.com/documentation/groupactivities/synchronizing-data-during-a-shareplay-activity)
- [Multipeer Connectivity](https://developer.apple.com/documentation/multipeerconnectivity)
- [MCSession](https://developer.apple.com/documentation/multipeerconnectivity/mcsession)
- [Network](https://developer.apple.com/documentation/network)
- [NSLocalNetworkUsageDescription](https://developer.apple.com/documentation/bundleresources/information_property_list/nslocalnetworkusagedescription)
- [NSBonjourServices](https://developer.apple.com/documentation/bundleresources/information-property-list/nsbonjourservices)
- [CloudKit](https://developer.apple.com/documentation/cloudkit)
