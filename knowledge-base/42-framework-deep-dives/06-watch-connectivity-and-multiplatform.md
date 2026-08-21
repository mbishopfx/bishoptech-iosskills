# Watch Connectivity and Multiplatform State

## Scope

Companion apps create a distributed local system: iPhone and Apple Watch have separate processes, storage, clocks, network conditions, and lifecycles. `WCSession` is a transport, not a replicated database. Build a small protocol and reducer around it:

`event/context/file -> decode/version/check identity -> idempotent reducer -> local projection -> optional acknowledgement`

## Session state machine

```text
unsupported
   |
supported -> configured -> activating -> activated
                                  |          |
                                  |          +-> reachable / notReachable
                                  |
                                  +-> inactive -> deactivated -> activating
```

Configure the default session and assign the delegate before calling `activate()`. Implement the required activation callback. On iPhone, observe inactive/deactivated transitions so a switch between multiple watches cannot silently send new transfers to the wrong active counterpart. `isCompanionAppInstalled`, `isReachable`, `activationState`, and “paired” are separate fields in the UI/domain state.

## Transport contract

| Transport | Delivery/order | Payload design | Failure/fallback |
| --- | --- | --- | --- |
| Application context | Replaces the previous context in the pipeline | Latest compact snapshot, schema version, generated time | Rebuild from app state; do not use for a durable event log. |
| User info | Queued background dictionary, ordered by the system | Event ID, version, changed fields, account/device scope | Persist pending/retry state; duplicate-safe receiver. |
| File transfer | Queued background file plus metadata | File URL, content type, checksum/version, deletion policy | Check storage, integrity, and incomplete transfer; clean temporary files. |
| Immediate message | Requires current reachability and both processes’ availability | Small request/reply, timeout, correlation ID | Show retry/offline UI; fall back to a context/queued transfer if semantics allow. |
| Complication transfer | Special budget/priority route | Only the active complication’s minimal data | Treat budget exhaustion as normal; use a timeline/other route if appropriate. |

Background transfers are not instantaneous. A queued transfer can be delayed, fail from storage/malformed data/communication issues, or arrive after the domain has advanced. Send a monotonic revision and stable event ID. The receiver should ignore an older revision, accept a duplicate without a second side effect, and retain an error/retry marker when validation fails.

## Distributed state patterns

### Latest-context projection

Use application context for “what is true now,” such as the active focus mode or a compact progress summary. When a newer context arrives, replace the old projection. Never infer that an omitted field means it is unchanged unless the protocol says so.

### Event queue

Use `transferUserInfo` for durable changes such as “record created,” “task completed,” or “preference changed.” Include an event ID, source account, schema version, and timestamp. The receiver stores the applied IDs or a revision watermark. If the same event has a device-side side effect, apply the side effect only after recording the event as accepted.

### File handoff

Use `transferFile` for media/documents. Create a stable file snapshot, include metadata/checksum, and decide who deletes the source/received copy. Do not transfer an open mutable database file or assume a file URL from one sandbox is usable in the other.

### Immediate interaction

Use `sendMessage` only when the person is waiting for the response. Check `isReachable`, set a timeout, handle the error callback, and leave the user with a retry or local fallback. A successful reply means the counterpart responded to that request; it does not prove server sync or durable persistence.

## Time, identity, and privacy

Use server timestamps or domain revisions when cross-device ordering matters; device clocks can differ. Bind every payload to a signed-in account or explicit local profile if the product supports multiple accounts. Clear pending transfers on sign-out according to the privacy policy, and avoid sending raw health, contact, location, or call data when a redacted projection is sufficient.

Delegate callbacks arrive on a background thread. Decode and validate off the main actor, then publish a small state change to SwiftUI. Use an actor or serial reducer for storage/apply ordering; do not mutate an observable view model directly from delegate callbacks.

## Two-device test matrix

- iPhone-only/no Watch, unsupported route, Watch app not installed, not paired, paired but inactive, and active Watch switched.
- Activation succeeds/fails, delegate callback delayed, reachable toggles, immediate message timeout, queued transfer delayed, transfer duplicate/out-of-order, malformed payload, low storage, and file unavailable.
- iPhone/Watch app terminated, phone locked, watch wrist/connection state changes, app update/schema migration, account switch, reinstall, and device restore.
- Verify the app remains useful without the companion and clearly labels stale/queued/not-reachable state.

## Sources

- [Watch Connectivity](https://developer.apple.com/documentation/watchconnectivity)
- [WCSession](https://developer.apple.com/documentation/watchconnectivity/wcsession)
- [WCSessionDelegate](https://developer.apple.com/documentation/watchconnectivity/wcsessiondelegate)
- [Transferring data with Watch Connectivity](https://developer.apple.com/documentation/watchconnectivity/transferring-data-with-watch-connectivity)
- [WCSessionUserInfoTransfer](https://developer.apple.com/documentation/watchconnectivity/wcsessionuserinfotransfer)
- [WCSessionFileTransfer](https://developer.apple.com/documentation/watchconnectivity/wcsessionfiletransfer)
- [Configuring app groups](https://developer.apple.com/documentation/xcode/configuring-app-groups)
- [Shared data](https://developer.apple.com/documentation/technologyoverviews/shared-data)
- [Swift concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
