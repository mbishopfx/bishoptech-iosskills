# Watch, CarPlay, and App Clips Deep Dive

## Scope

These companion surfaces extend an iPhone product into a paired wearable, a vehicle display, or a short-lived installation. They are separate targets and system contexts, not alternate SwiftUI tabs. Model each with its own lifecycle and a small protocol:

`activation/invocation -> context validation -> focused UI/action -> durable handoff -> unavailable/complete`

## Watch Connectivity

### Activation and pairing state

Both the iPhone app and WatchKit extension configure their own `WCSession` and delegate, then activate it. Check `WCSession.isSupported()` before creating the route. Wait for `session(_:activationDidCompleteWith:error:)` and maintain an explicit state such as `unsupported`, `inactive`, `activating`, `activated`, `deactivated`, or `failed`.

On iPhone, support `sessionDidBecomeInactive` and `sessionDidDeactivate` when the user can switch between watches. While inactive/deactivated, do not initiate new transfers; reactivate after the system selects the new active watch. An installed/paired watch is not necessarily the active counterpart or a running process.

### Select the transport by semantics

| API | Semantics | Product use |
| --- | --- | --- |
| `updateApplicationContext` | Latest context replaces prior context waiting in the pipeline | Synchronize the current compact state, such as the selected mode or most recent summary. |
| `transferUserInfo` | Queued dictionary transfer | Events or durable changes that should eventually arrive and can be applied idempotently. |
| `transferFile` | Queued file transfer | Images/documents or larger payloads with a durable file lifecycle. |
| `sendMessage`/`sendMessageData` | Immediate request/reply while the counterpart is reachable | A live interaction where the user can retry if `isReachable` is false. |
| `transferCurrentComplicationUserInfo` | Complication-specific transfer with budget | Only data needed by an active complication; not a general background channel. |

Background transfers may be delayed and consume power. Send changed fields, include a schema/version/event ID, and make the receiver safe to process a duplicate or out-of-date event. The session delegate receives data serially on a background thread; hand UI changes to the main actor.

### Shared state and account switching

Use an App Group/shared container only for intentionally shared projections and handoff state. Key records by a stable app account/user ID and watch/device context. On sign-out or a new active watch, clear or quarantine pending private transfers according to the product’s retention policy. Do not assume the iPhone and watch can share a SwiftData container or a live actor.

## CarPlay

### Scene and template lifecycle

CarPlay creates a `CPTemplateApplicationScene` and informs its `CPTemplateApplicationSceneDelegate` about connection, disconnection, and user actions. The system provides the `CPInterfaceController`; the app stores it for the session and sets a supported root template. Most categories do not receive an arbitrary CarPlay window; navigation apps have a distinct map-window route.

The CarPlay scene is configured in the target’s scene manifest and requires the category-specific entitlement/approval. A successful simulator connection does not establish that the production target has the correct entitlement or that a vehicle supports the same behavior.

### Driver-attention rules

CarPlay content should be glanceable, low-interaction, and category-appropriate. Use Apple’s templates and keep text/actions within the framework’s limits. Avoid dense editing, free-form browsing, or an iPhone screen mirrored into the vehicle. Treat the user’s attention and vehicle state as a safety boundary; provide voice/short-choice/parked fallbacks when the category supports them.

On disconnect, release or invalidate CarPlay-only resources, persist only the safe domain state, and rebuild the template hierarchy on the next connection. Do not treat a cached `CPInterfaceController` as valid after its scene ends.

## App Clips

### Invocation is untrusted context

The App Clip receives an invocation through the system’s `NSUserActivity`/scene lifecycle. The URL may identify a location, item, action, or campaign, but the app must parse and validate it. It may not receive a URL when relaunched from a notification, App Library, or App Switcher. Save enough state to restore the last focused task when there is no fresh invocation.

Use a shared invocation parser in the App Clip and full app, but keep the allowed actions/permissions narrow. The full app replaces the App Clip after installation and must handle every invocation the Clip handled. A successful handoff is not proof that a checkout, reservation, account, or remote record is valid; fetch/reconcile that state through the same server/domain boundary as the full app.

### Experience and association configuration

An App Clip requires a default App Clip experience. Advanced experiences, website association, AASA files, QR/NFC/App Clip Codes, Maps, and location-specific links add configuration and release dependencies. The URL scheme, host, path prefix, query parameters, App Clip card copy, bundle association, signing, and App Store Connect metadata all need to agree.

Keep the startup path small and resilient to slow/offline networks. Put only the minimum data in local state and expire it under the App Clip’s privacy/retention policy. If notifications or Live Activities are used, test their return path with no invocation URL and do not rely on the Clip remaining resident.

## Companion API, target, and configuration matrix

| Surface/need | Concrete route | Ownership and configuration | Proof boundary |
| --- | --- | --- | --- |
| Activate Watch Connectivity | `WCSession.default`, `WCSessionDelegate`, `isSupported()`, `activate()` | The iOS app and WatchKit extension each own a session and target configuration; pairing/active-watch state is system-owned | Prove activation completion, inactive/deactivated transitions, active-watch switching, installed counterpart, and a real paired iPhone/Watch. |
| Synchronize latest Watch state | `updateApplicationContext(_:)` / `applicationContext` | Send a compact versioned projection that can be replaced; do not use it as an event log | Prove out-of-order/late delivery and schema migration; stale context must render as stale, not as a fresh action result. |
| Queue Watch changes or files | `transferUserInfo(_:)`, `transferFile(_:metadata:)`, `WCSessionUserInfoTransfer`, `WCSessionFileTransfer` | The system schedules delivery while a counterpart may be inactive; file URLs, metadata, retention, and idempotence are app-owned | Prove duplicate/out-of-date events, cancellation/progress, storage cleanup, unreachable counterpart, and delayed delivery on two physical devices. |
| Request an immediate Watch reply | `sendMessage`/`sendMessageData` when `isReachable` | Live messaging is only for the reachable counterpart process; it is not a background queue | Prove timeout/error/retry and a no-reachability fallback; never treat a sent message as a completed domain mutation. |
| Present a CarPlay surface | `CPTemplateApplicationScene`, `CPTemplateApplicationSceneDelegate`, `CPInterfaceController`, supported templates | Separate CarPlay scene/target configuration, category entitlement and approval, scene manifest, and vehicle/system support | Prove connection/disconnection, root-template rebuild, locked-phone behavior, audio/vehicle state, driver-attention rules, and an actual vehicle or supported hardware route. |
| Invoke an App Clip | App Clip scene/`NSUserActivity` invocation and a validated URL parser | App Clip target, default/advanced experience, associated domains/AASA where used, URL/host/path rules, signing, and App Store Connect metadata | Prove physical invocation from each entry path, no-URL relaunch, slow/offline state, card/experience configuration, and full-app replacement. |
| Hand off to the full app | Shared invocation schema and deep-link/handoff record | The full app must re-validate the stable ID/context against current authorized state; do not trust Clip-local or URL-supplied claims | Prove install/replace transition, expired/deleted item, signed-out user, duplicate handoff, and server reconciliation; handoff is not payment/reservation/account proof. |

Keep companion data as a projection with `schemaVersion`, stable record ID, source/account ID, `updatedAt`, expiry, redaction level, action intent, and a result/error state. Watch transfer, CarPlay scene state, and App Clip invocation are separate processes and lifecycles; sharing a Swift type or App Group file does not merge their availability or proof.

## Companion state machines and evidence

Watch Connectivity:

```text
unsupported | unpaired -> activating -> activated
activated -> reachable | backgroundTransferOnly
activated -> inactive/deactivated -> reactivating | failed
```

CarPlay:

```text
disconnected -> connecting -> connected -> rootInstalled
rootInstalled -> actionPending -> resultProjected | failed
connected -> disconnected -> rebuildOnNextConnection
```

App Clip:

```text
coldStart -> invoked -> URL/contextValidated -> focusedAction
focusedAction -> handoffToFullApp | completed | expired | offline | failed
```

Record the event ID, target/process, invocation source, configuration version, authorization/account state, and last confirmed result. A simulator template, local App Clip URL fixture, or successful `WCSession` enqueue proves only that local seam; it does not prove paired delivery, vehicle support, AASA/experience configuration, App Store readiness, or a remote business operation.

## Verification matrix

| Surface | Fixture/preview can show | Physical/release proof still needed |
| --- | --- | --- |
| Watch | Route parser, protocol reducer, projection view | Paired physical iPhone/Watch, activation/deactivation, active-watch switch, delayed/failed transfer, reachability, file size/storage, background delivery. |
| CarPlay | Template construction and scene delegate callbacks in CarPlay Simulator | Category entitlement/approval, real vehicle/aftermarket system, disconnect/reconnect, audio route, locked phone, driver-attention interaction, supported templates. |
| App Clip | Local `_XCAppClipURL` fixture and focused UI | Physical invocation, App Clip card/experience, AASA/associated domain, QR/NFC/Code/Maps/Safari/Messages path, slow network, no URL relaunch, App Store/TestFlight transition, full-app replacement. |

## Sources

- [Watch Connectivity](https://developer.apple.com/documentation/watchconnectivity)
- [WCSession](https://developer.apple.com/documentation/watchconnectivity/wcsession)
- [WCSessionDelegate](https://developer.apple.com/documentation/watchconnectivity/wcsessiondelegate)
- [WCSessionFileTransfer](https://developer.apple.com/documentation/watchconnectivity/wcsessionfiletransfer)
- [WCSessionUserInfoTransfer](https://developer.apple.com/documentation/watchconnectivity/wcsessionuserinfotransfer)
- [Transferring data with Watch Connectivity](https://developer.apple.com/documentation/watchconnectivity/transferring-data-with-watch-connectivity)
- [CarPlay](https://developer.apple.com/documentation/carplay)
- [CPTemplateApplicationScene](https://developer.apple.com/documentation/carplay/cptemplateapplicationscene)
- [CPTemplateApplicationSceneDelegate](https://developer.apple.com/documentation/carplay/cptemplateapplicationscenedelegate)
- [CPInterfaceController](https://developer.apple.com/documentation/carplay/cpinterfacecontroller)
- [Displaying content in CarPlay](https://developer.apple.com/documentation/carplay/displaying-content-in-carplay)
- [Requesting CarPlay entitlements](https://developer.apple.com/documentation/carplay/requesting-carplay-entitlements)
- [Using the CarPlay Simulator](https://developer.apple.com/documentation/carplay/using-the-carplay-simulator)
- [CarPlay Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/carplay/)
- [App Clips](https://developer.apple.com/documentation/appclip)
- [Creating an App Clip with Xcode](https://developer.apple.com/documentation/appclip/creating-an-app-clip-with-xcode)
- [Configuring App Clip experiences](https://developer.apple.com/documentation/appclip/configuring-the-launch-experience-of-your-app-clip)
- [Responding to invocations](https://developer.apple.com/documentation/appclip/responding-to-invocations)
- [Testing the launch experience of your App Clip](https://developer.apple.com/documentation/appclip/testing-the-launch-experience-of-your-app-clip)
- [Associating your App Clip with your website](https://developer.apple.com/documentation/appclip/associating-your-app-clip-with-your-website)
- [Enabling notifications in App Clips](https://developer.apple.com/documentation/appclip/enabling-notifications-in-app-clips)
- [App Clip Code URL encoding](https://developer.apple.com/documentation/appclip/encoding-a-url-in-an-app-clip-code)
