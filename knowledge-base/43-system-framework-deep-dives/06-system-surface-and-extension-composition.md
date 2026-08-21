# System-Surface and Extension Composition

## The app is one participant in a system workflow

Widgets, controls, Live Activities, App Intents, document providers, share extensions, App Clips, background tasks, Watch scenes, and CarPlay scenes may run in a different process, at a different time, with a smaller UI and less state than the main app. Design the handoff as a protocol rather than assuming the main app is alive.

```text
user/system invocation
        -> extension or system surface
        -> shared, versioned projection
        -> domain use case
        -> result/status projection
        -> app deep link or system-owned result
```

## Surface selection

| Outcome | Surface | Keep there | Handoff to the app when |
| --- | --- | --- | --- |
| Glance at current state | WidgetKit timeline/widget | A small, privacy-safe projection with freshness | The person needs editing, search, or a long workflow. |
| Perform one bounded action | Interactive widget/control/App Intent | A quick, idempotent action with explicit result | Authorization, review, or complex input is needed. |
| Show live progress/status | ActivityKit Live Activity | Time-sensitive state and a small set of actions | The activity ends, fails, or needs full detail. |
| Discover content/actions | App Intents, AppEntity, EntityQuery, Spotlight | Stable IDs, display representation, current resolution | The person needs the full record or correction. |
| Import/share a document | File/document/share extension | User-selected representation and short transfer | The target app needs a long edit/export or unsupported state. |
| Continue a user-started long task | `BGContinuedProcessingTask` or appropriate background route | Bounded work, progress, cancellation, system status | The task needs interactive review or cannot continue. |
| Lightweight first entry | App Clip | Minimum capability and handoff token/context | Identity, full data, purchase, or durable account work is needed. |
| Companion/vehicle action | WatchConnectivity/CarPlay scene/template | Surface-specific, attention-safe state | The phone app owns the longer workflow or source of truth. |

The surface is not a smaller copy of the main app. It is a capability with a stricter lifecycle and a narrower interaction budget.

## App Groups are a protocol

If an app and extension share state, define a versioned projection:

| Projection field | Purpose |
| --- | --- |
| `schemaVersion` | Lets every process decide whether it can read the projection. |
| `recordID`/stable entity ID | Reconnects a surface to the domain object without storing the entire object. |
| `updatedAt`/expiry | Lets the surface label stale state and avoid presenting old truth as current. |
| `state` | Explicit loading, ready, failed, unavailable, active, completed, or ended state. |
| `displayData` | Small, redacted values required to render the surface. |
| `actionToken`/intent input | A bounded request reference, not an authorization bypass. |
| `lastError`/recovery | A user-facing recovery hint that does not leak sensitive payloads. |

Write projections atomically, keep them small, and treat a missing/corrupt/old projection as a normal state. The extension must re-check authorization and current domain state before a mutating operation.

## Deep links and return paths

Every system surface should identify where the person goes next:

- widget/control action succeeds: update the projection and optionally open a specific app destination;
- review required: open the app to a focused review route with the stable record/source ID;
- Live Activity ends: preserve a result/detail destination rather than an orphaned notification;
- App Intent cannot complete: return a precise dialog/error and a recoverable app route;
- App Clip needs full app: preserve only the minimum handoff context and re-validate it in the full app;
- share/document import fails: preserve the user-selected source or provide a retry/export state.

Do not encode an entire private record in a URL or intent parameter. Use a stable identifier, resolve it against current authorized state, and handle deletion or account switching.

## Background route choice

| Need | Route | Boundary |
| --- | --- | --- |
| Opportunistic refresh | `BGAppRefreshTask` | The system chooses timing; refresh must tolerate being delayed or skipped. |
| Deferred resource work | `BGProcessingTask` | Requires declared conditions and can be interrupted/terminated. |
| Person-started long work | `BGContinuedProcessingTask` where supported | Start only from the allowed foreground/user boundary; expose progress/cancellation and handle resource limits. |
| Visible live status | ActivityKit | State/push/lifecycle and stale data are separate from the work itself. |
| Timeline/glance projection | WidgetKit | Reload budgets and timeline freshness are system-managed. |

Never use a background task as a guarantee that work will finish at a particular time. Persist checkpoints and make the operation resumable or safely discardable.

## Extension-specific state

Model these conditions explicitly:

- host process is unavailable or terminates;
- protected data is unavailable while the device is locked;
- the user is signed out or switched accounts;
- shared storage is missing, migrated, corrupt, or not yet synchronized;
- the intent/action is invoked twice or with a stale entity;
- a widget/control/Live Activity has older state than the app;
- background work expires or is cancelled;
- a system surface is unsupported on the device or vehicle.

The fallback may be to open the app, show the last confirmed state, request reauthorization, queue a safe retry, or explain that the operation needs the full app. It must not silently claim completion.

## Privacy and visual hierarchy

System surfaces are often visible outside the app’s normal privacy context. Minimize names, locations, health values, messages, images, and account state in widgets, Live Activities, notifications, CarPlay, Watch, and App Clip projections. Use protected-data/account state to determine whether a redacted or unavailable view should render.

Use native controls and templates. A custom Liquid Glass treatment belongs only in an app-owned functional group; it should not attempt to recreate a system-owned widget, CarPlay template, notification, or Apple Intelligence surface.

## Surface protocol matrix

| Surface/process | Input and output | Owns | Does not prove |
| --- | --- | --- | --- |
| Main app process | User intent, domain read/write, focused review UI, durable result | Canonical domain state, authorization review, migrations, long workflows, and full error recovery | That a widget, extension, companion, server, or notification received the projection. |
| Widget/Live Activity extension | Snapshot/timeline/content state, App Intent action, ActivityKit update | Redacted display projection, bounded action result, stale/ended state | Freshness at a precise time, continuous execution, arbitrary background work, or APNs delivery. |
| App Intent/control/system invocation | Resolved entity/parameters and a small command result | Re-read current state, authorization, idempotent mutation, concise dialog/result | That the full app UI ran, a third-party side effect succeeded, or the system will invoke it again. |
| Share/document/File Provider extension | Host-selected item/provider request and completion/cancel result | Representation validation, import/export handoff, provider item state, conflict/error | That the main app is alive, a remote file is reachable, or a recipient stored/acted on the result. |
| Background task process | Scheduled/user-started work and durable checkpoint | Bounded resumable work, expiration/cancellation, progress, retry policy | Scheduling, start time, completion by a deadline, or production delivery merely because a debug launch worked. |
| Watch/CarPlay/App Clip surface | Paired/invoked/vehicle context, focused action, projection/handoff | Surface-specific attention/privacy rules and return path | Pairing/reachability, vehicle support, AASA/experience configuration, full-app validity, or a remote transaction. |
| Notification/provider/server route | APNs/provider event, notification content, server acknowledgement | Transport-specific payload/result and user-visible fallback | Notification presentation, user attention, server business completion, or a current app projection. |

For each row, record the owning process, target bundle ID, input schema, output/result schema, shared projection version, authorization boundary, and evidence artifact. A shared model type can reduce duplication, but it does not collapse process lifetime, target membership, entitlements, privacy visibility, or OS scheduling into one guarantee.

## Cross-surface handoff contract

Use a small versioned handoff record rather than copying a whole domain object into a URL, widget entry, App Group file, Watch transfer, or App Clip invocation:

| Field | Rule |
| --- | --- |
| `schemaVersion` | Reject or migrate unknown versions; never guess field meaning. |
| `sourceSurface`/`targetSurface` | Identifies the producing and consuming process/target for diagnostics and fallback. |
| `accountID`/`recordID` | Stable identifiers resolved against current authorized state; no private record dump in a URL. |
| `sourceRevision`/`updatedAt`/`expiresAt` | Allows stale, superseded, or expired state to be shown truthfully. |
| `displayProjection` | Small, redacted, surface-appropriate values only. |
| `intent`/`actionID`/`idempotencyKey` | Describes the requested operation and prevents duplicate side effects. |
| `authorizationContext` | A hint for re-checking access, never a substitute for Keychain/server/system authorization. |
| `resultState`/`errorCode`/`recoveryRoute` | Separates accepted, started, checkpointed, completed, delivered, cancelled, and failed. |
| `deepLink` | Opens a focused app route after revalidation; handles deletion, sign-out, unsupported target, and missing record. |

The producer may write `accepted` or `queued`; only the owning domain/service boundary may write `completed`. A notification, Live Activity update, Watch transfer, widget refresh, App Clip handoff, or CarPlay template update is a projection/transport event—not proof that the underlying operation succeeded.

## Availability and release-evidence register

For a composed feature, keep these checks separate:

1. **Compile/target:** selected SDK symbol availability, deployment target, target membership, extension point, scene manifest, capabilities, entitlements, usage descriptions, App Group, associated domains, URL schemes, and privacy manifest.
2. **Runtime/invocation:** authorization, account/protected-data state, process launch, system invocation, scheduling acceptance, provider/server response, device-family support, and fallback behavior.
3. **Physical/system:** actual iPhone/iPad/Watch/accessory/vehicle/CarPlay/App Clip invocation, lock/background/termination, accessibility, network, battery/resource, and attention conditions.
4. **Artifact/release:** signed app and extension bundle inspection, entitlements, App Clip/associated-domain/App Store Connect configuration, APNs environment/topic/server state, TestFlight distribution, and production behavior only after the corresponding route is tested.

Do not use a green compile as runtime proof, a simulator callback as hardware proof, a signed archive as App Review approval, or a sent push/transfer as delivery proof. Save the exact build, target, device/OS, configuration, invocation source, timestamp, logs/result bundle, and observed outcome for each route.

## Verification matrix

| Evidence | Required check |
| --- | --- |
| Compile/configuration | Extension target, App Group, entitlements, background modes, associated domains, URL schemes, and privacy/usage descriptions. |
| Projection | Atomic write/read, schema migration, stale/empty/error/redacted states, account switch, deletion, and corruption. |
| Invocation | Actual widget/control/App Intent/Spotlight/share/document/App Clip/Watch/CarPlay/system invocation. |
| Lifecycle | Process termination, host expiration, background suspension, device lock, network loss, cancellation, and duplicate invocation. |
| UI/accessibility | Template constraints, Dynamic Type/VoiceOver where applicable, focus/deep link, driver attention, and system-owned copy. |
| Device/system | Physical hardware, paired Watch/accessory, vehicle/CarPlay, camera/microphone, and named OS/system surface. |
| Release | Signed extension/archive, capability approval, App Store/App Clip/AASA configuration, APNs/server/account state, and production delivery only if tested. |

## Sources

- [App Intents](https://developer.apple.com/documentation/appintents/)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- [EntityQuery](https://developer.apple.com/documentation/appintents/entityquery)
- [Making app entities available in Spotlight](https://developer.apple.com/documentation/appintents/making-app-entities-available-in-spotlight)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit/)
- [Adding interactivity to widgets and Live Activities](https://developer.apple.com/documentation/widgetkit/adding-interactivity-to-widgets-and-live-activities)
- [ActivityKit](https://developer.apple.com/documentation/activitykit/)
- [App Groups](https://developer.apple.com/documentation/xcode/configuring-app-groups)
- [BackgroundTasks](https://developer.apple.com/documentation/backgroundtasks/)
- [BGContinuedProcessingTask](https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtask)
- [FileProvider](https://developer.apple.com/documentation/fileprovider/)
- [Uniform Type Identifiers](https://developer.apple.com/documentation/uniformtypeidentifiers/)
- [Transferable](https://developer.apple.com/documentation/coretransferable/)
- [App Clips](https://developer.apple.com/documentation/appclip/)
- [WatchConnectivity](https://developer.apple.com/documentation/watchconnectivity/)
- [CarPlay](https://developer.apple.com/documentation/carplay)
- [CallKit](https://developer.apple.com/documentation/callkit/)
- [LiveCommunicationKit](https://developer.apple.com/documentation/livecommunicationkit)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
