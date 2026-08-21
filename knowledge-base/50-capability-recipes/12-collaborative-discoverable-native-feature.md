# Collaborative, Discoverable Native Feature

Use this recipe when an app idea should feel native beyond its main screen: people can share an activity, discover a record or action through the system, continue work on another device, and preview an artifact before saving it.

## Best fit

- shared whiteboards, watch parties, games, planning boards, study rooms, or collaborative photo experiences;
- local nearby transfer or pairing where the person explicitly approves the peer;
- private records that should be discoverable through Spotlight/App Intents without exposing the database;
- document/media/3D workflows that benefit from Quick Look;
- focused work that can continue through Handoff rather than forcing the person to restart.

## Route selector

| Need | Route | Keep canonical truth in |
| --- | --- | --- |
| Coordinate a FaceTime/Messages/share activity | Group Activities/SharePlay | The app’s domain store plus the current `GroupSession` projection. |
| Nearby ad-hoc communication | Network Framework, or a constrained legacy Multipeer adapter | A versioned protocol reducer and optional app/server record. |
| Durable multi-device collaboration | CloudKit/shared records or an app-owned service | Server/shared-store truth with conflict and deletion policy. |
| Teach a feature at the moment it matters | TipKit | App feature state and explicit completion event. |
| Search app content or resolve an action | Core Spotlight/App Intents | Authorized domain record/entity. |
| Continue the current task elsewhere | `NSUserActivity`/Handoff | Re-resolved record plus a focused destination. |
| Inspect or lightly edit an artifact | Quick Look | Validated file/artifact version, not the preview controller. |

Do not combine all routes by default. A live SharePlay session is not a CloudKit sync engine; a Spotlight item is not an entitlement; a Handoff payload is not authorization; and a Quick Look edit callback is not a saved domain mutation.

## Build order

1. Define the user outcome and the canonical record/operation that must remain true if every system surface is unavailable.
2. Choose live coordination, nearby transport, or durable collaboration based on latency, audience, offline behavior, identity, and retention—not on framework novelty.
3. Write a versioned protocol for messages/attachments/projections with stable IDs, source revisions, expiry, redaction, idempotency, and explicit result states.
4. Configure only the needed target capabilities: Group Activities, local-network usage/Bonjour, App Intents, `NSUserActivityTypes`, associated domains/Handoff where applicable, Quick Look extension/content types, App Groups, CloudKit, and privacy strings.
5. Build the main app flow first, then add one system surface at a time. Every surface must have a no-service fallback and a revalidation path back to canonical state.
6. Add TipKit only after the feature is usable without the tip. Add Spotlight/App Entity indexing only after create/edit/delete/deep-link behavior is deterministic. Add Handoff only for a genuinely current activity.
7. Treat files/attachments/AI proposals as untrusted inputs. Validate UTType, size, schema, account, permissions, and content before persistence or side effects.
8. Test the reducer with fixtures, then exercise the real system surface on physical devices and the signed target configuration.

## Cross-surface state contract

```text
canonicalIdle -> localReady -> projecting
projecting -> searchable | shareEligible | handoffCurrent | previewReady
shareEligible -> activating -> joined -> syncing -> left/invalidated
searchable -> selected -> revalidated -> focusedAppRoute | stale/deleted
handoffCurrent -> offered -> restored | rejected/expired
previewReady -> previewing -> editedCopyValidated -> saved | cancelled/failed
```

Each projection carries `schemaVersion`, `accountID`, `recordID`, `sourceRevision`, `updatedAt`, `expiresAt`, `redactionLevel`, `actionID`, and `recoveryRoute`. The main app or authorized service is the only place that can claim `completed`; a message send, index write, Handoff offer, preview callback, or system UI appearance may only claim the transport-specific state it actually observed.

## AI boundary

An on-device model can propose a title, message, grouping, search summary, or collaboration action, but it does not become a participant authority. Keep the model output as a versioned proposal with source references and confidence/unknown state. Before sharing, indexing, handing off, previewing, or mutating:

1. validate the generated structure and bounds;
2. confirm the source record and current account authorization;
3. show a review surface for consequential or privacy-sensitive actions;
4. require explicit user approval where appropriate;
5. apply the deterministic operation with an idempotency key;
6. project the confirmed result, not the raw model output, to system surfaces.

## Failure and fallback matrix

| Failure | User-facing fallback | Do not infer |
| --- | --- | --- |
| SharePlay unavailable/no conversation | Continue locally, offer a normal share/export, or explain the requirement | That an activity can start from a local button on every device. |
| Peer permission denied/disconnected | Show manual pairing/export or retry when foregrounded | That nearby discovery identifies a trusted peer or survives backgrounding. |
| Cloud/server unavailable | Show local draft and queued/retry state with freshness | That local persistence is shared truth. |
| Spotlight/App Intent stale or unresolved | Open the app’s search/recovery route | That system selection grants access or means the record still exists. |
| Handoff rejected/expired | Reopen the last local route or ask the person to choose the record | That an activity was delivered or restored on the other device. |
| Quick Look unsupported/malformed/edit failed | Offer app-owned rendering/export or preserve the original | That a preview is a safe parser or a saved mutation. |
| AI unavailable or proposal rejected | Use deterministic manual entry/search/share | That model availability, output, or system integration is universal. |

## Evidence plan

- Source: exact Apple route, current SDK availability, and any deprecation/entitlement note.
- Target: bundle IDs, capabilities, `Info.plist` keys, associated domains, App Groups, extension membership, privacy manifest, and server/account environment.
- Compile: route reducer, schema, authorization mapping, cancellation, and fallback tests.
- System: actual SharePlay, nearby permission/session, Spotlight selection, Handoff, Quick Look, and accessibility flows.
- Physical/release: two-device/paired-device behavior, lock/background/termination, signed configuration, TestFlight/production-like service state, and App Store metadata where relevant.

## Sources

- [Group Activities](https://developer.apple.com/documentation/groupactivities)
- [Multipeer Connectivity](https://developer.apple.com/documentation/multipeerconnectivity)
- [Network](https://developer.apple.com/documentation/network)
- [TipKit](https://developer.apple.com/documentation/tipkit)
- [Core Spotlight](https://developer.apple.com/documentation/corespotlight)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [NSUserActivity](https://developer.apple.com/documentation/foundation/nsuseractivity)
- [Implementing Handoff in your app](https://developer.apple.com/documentation/foundation/implementing-handoff-in-your-app)
- [Quick Look](https://developer.apple.com/documentation/quicklook)
- [Framework availability and device-proof matrix](../40-framework-routes/08-framework-availability-and-device-matrix.md)
