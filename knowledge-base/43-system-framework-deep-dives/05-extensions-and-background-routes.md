# Extensions, Widgets, Live Activities, and Background Routes

## Scope

An extension is a separate target and process with a system-defined entry point, host context, capability set, memory/runtime limits, and termination behavior. Background execution is a scheduling contract, not a timer. Design every route around durable state and interruption:

`system invokes -> extension/task restores durable state -> bounded work -> completion/cancellation -> system surface or app-owned checkpoint`

## Extension taxonomy

| Route | System/host role | What the target should own | What it must not assume |
| --- | --- | --- | --- |
| Share/action extension | Host app supplies `NSExtensionContext` input items | Review/redaction/transform and completion/cancel | The containing app is running or every input is available as bytes immediately. |
| Document picker/File Provider | Files app or another app asks for files/metadata/content | Enumeration, placeholders, fetch/upload, versions, progress, conflict state | Remote content is local, network is available, or a request will be retried safely without idempotence. |
| Widget extension | WidgetKit asks for a snapshot/timeline or interactive intent | A small renderable projection and safe action | The widget is continuously active or a timeline date is exact. |
| Live Activity UI | WidgetKit renders ActivityKit content | Compact/expanded/Lock Screen/other supported presentations | A Live Activity is a widget timeline or can be started at any time in the background. |
| App Intent/Control | System invokes a focused action | Validation, confirmation, idempotent mutation, result state | The full app UI, navigation stack, or main-process memory exists. |
| Notification service/content | System gives a notification-specific opportunity | Bounded content modification/presentation | It can perform arbitrary app work or guarantee notification delivery. |
| Custom ExtensionKit app extension | Host app launches a separate extension through a declared extension point/XPC boundary | Typed protocol, process lifecycle, capability grant, and interruption cleanup | An XPC connection is permanent or extension state is safe to keep only in memory. |

## Host and extension lifecycle

For a host-invoked extension, the host supplies input items and the extension must call `completeRequest` or `cancelRequest` through its context. This is a request lifecycle, not an app lifecycle. Persist enough progress for a cancellation or termination to leave the user with a truthful state, and return only the result items the host expects.

For a custom ExtensionKit route, the host defines the extension point and protocol. Keep a strong reference to the extension process, observe interruption, remove/invalidates connections when the work ends, and clean up proxy references when the process terminates. Starting in iOS 26, Apple documents programmatic extension-point generation through the Xcode build setting `EX_ENABLE_EXTENSION_POINT_GENERATION`; treat this as an SDK/target configuration detail to verify in the selected toolchain rather than copying a build setting blindly.

Do not use unavailable app-only APIs from an extension. Put shared, pure domain code in a framework/package and keep UIKit/SwiftUI system-surface adapters in their target. An extension’s view can be embedded in a host surface, but it is not a second navigation stack with unrestricted presentation privileges.

## App Group state is a protocol

An App Group provides a shared container for related signed targets. It does not solve synchronization or schema ownership. Define:

- one canonical record format with a version and migration rules;
- a small projection for each system surface;
- atomic replacement or file coordination for files;
- a lock/transaction policy when multiple targets can write;
- redaction rules for lock screen/widgets/extensions;
- deletion/account-switch behavior;
- recovery when a process is killed during a write;
- a source-of-truth rebuild path from the main app or server.

Use shared defaults for small preferences, not large documents or secrets. Use an App Group container for intentionally shared files. Keep Keychain material under a deliberate access group/accessibility policy and never serialize credentials into widget timelines or extension payloads.

## WidgetKit is timeline-driven and budgeted

WidgetKit renders a view in a separate process. A `TimelineProvider` or `AppIntentTimelineProvider` returns entries and a reload policy such as `.atEnd`, `.after`, or `.never`. The policy is an earliest request signal, not a promise that the view changes at that exact date. Widget refreshes are budgeted, may be coalesced, and behave differently under the debugger.

Prepare widget data ahead of time in the app or a shared container. Include a timestamp, freshness/unknown state, and an account/privacy projection in every entry. Call `WidgetCenter` only when the displayed kind actually changed. Never make a widget dependent on a synchronous network request or a live main-app actor.

Interactive widget/control actions use App Intents. Make them safe when the app is not running: identify the target by stable ID, re-read current state, perform an idempotent mutation, write the new projection, and return a concise result. Ask for confirmation when the action has a consequential side effect.

## ActivityKit is a distinct live-status channel

ActivityKit starts, updates, and ends Live Activities. Local starts occur while the app is in the foreground unless the app uses a documented App Intent route; updates and ending can occur while the app is in the background. Remote updates use ActivityKit push notifications through APNs and require the correct environment/topic/push setup. Live Activities do not use WidgetKit timelines.

Model the lifecycle explicitly:

`eligible -> requesting -> active -> stale/paused -> completed|ended|denied|failed`

Include a final content state when ending, define dismissal behavior, and show stale/unknown values rather than inventing current progress. Verify each supported surface and device family; visionOS does not support Live Activities even though ActivityKit supports other Apple platforms.

## BackgroundTasks choices

### `BGAppRefreshTask`

Use for short, opportunistic content refresh. Register the identifier at the documented launch point, schedule a request with an earliest begin date, load a small checkpoint, cancel/finish quickly, and reschedule only when policy permits. The system controls timing.

### `BGProcessingTask`

Use for deferred maintenance or longer work that may need network or external power. Express those requirements, persist work units, make retries idempotent, observe `expirationHandler`, cancel ongoing work, and call `setTaskCompleted(success:)`. A processing request is not a guarantee that the job will run or finish.

### `BGContinuedProcessingTask` on iOS 26

This route is different: a person starts the work in the foreground, the app submits a `BGContinuedProcessingTaskRequest`, and the system may let it continue after the app backgrounds. The task can be queued or rejected based on submission strategy/resources, can be canceled through the system UI, and can terminate under resource constraints. Report meaningful progress, checkpoint work, and handle expiration/failure. GPU use has a separate resource/entitlement boundary; measure the actual device rather than assuming that a supported API means unlimited background compute.

Good candidates include a user-started media export, thumbnail batch, or on-device processing job. Do not use this route as a hidden scheduler, background daemon, silent tracker, or guarantee that an AI job will finish before a chosen deadline.

## Framework-specific background handoffs

If the product is driven by a system event, prefer that framework’s route over generic background tasks:

| Event | Candidate route | Key proof |
| --- | --- | --- |
| Health data update | HealthKit observer/background delivery | HealthKit capability, authorization, delivery policy, protected data, physical device. |
| Significant/continuous location | Core Location | Purpose, accuracy, authorization, background mode, power, and device route. |
| Ongoing audio/media | AVAudioSession/media APIs | Audio session, route/interruption, background entitlement, and actual hardware. |
| Watch handoff | Watch Connectivity | Paired state, transfer type, reachability semantics, retries, and two-device proof. |
| Live event status | ActivityKit/APNs | Content state, push token/environment, stale/end behavior, and system surface. |
| User-requested long job | BGContinuedProcessingTask | Foreground initiation, progress, cancellation, resource support, and resume. |

Do not combine several background mechanisms just to increase the chance of execution without a product need and a clear duplicate/idempotence policy.

## API, target, and configuration matrix

| Route | Concrete API seams | Target/process/configuration | Lifecycle and proof gate |
| --- | --- | --- | --- |
| Share/action extension | `NSExtensionContext`, `NSExtensionItem`, `NSItemProvider`, `completeRequest`/`cancelRequest` | Separate extension target and extension point/activation rule; host controls the input and lifetime | Prove text/file/URL representations, cancellation, host expiration, redaction, result handoff, and no assumption that the containing app is running. |
| File Provider | `NSFileProviderReplicatedExtension`, `NSFileProviderEnumerating`, item identifiers, placeholders/content fetch | File Provider target, provider identifier, storage/authentication model, App Group/file coordination where applicable | Prove enumeration, placeholder, fetch/upload, version/conflict, offline, cancellation, remote error, and Files-app behavior; remote availability is not local persistence. |
| Widget timeline | `TimelineProvider`/`AppIntentTimelineProvider`, `Timeline`, `TimelineEntry`, `WidgetCenter` | Widget extension target, supported families/configuration, redacted projection, shared container only for intentional state | Prove placeholder/snapshot/timeline, reload policy and budget, stale/locked content, interactive intent, process termination, and actual Home Screen/StandBy surface. |
| Interactive widget/control | `AppIntent`, `ControlWidget`, intent parameter/entity resolution | Widget/control extension target, App Intent registration, capability and privacy configuration | Re-read current state, authorize, make mutation idempotent, project result/error; an invocation acknowledgement is not proof that the domain operation persisted. |
| Live Activity | `Activity`, `ActivityContent`, ActivityKit updates/ending, APNs push route when remote | Widget extension plus app target, ActivityKit attributes/content-state schema, push environment/topic/server configuration | Prove permission/start boundary, update/end/stale/final state, push token/environment, dismissal, supported surface/device, and server acknowledgement separately. |
| Notification service/content | `UNNotificationServiceExtension`, `UNNotificationContentExtension` | Separate extension target, notification category/Info.plist configuration, APNs payload and privacy rules | Prove time/resource limit, mutable-content path, unavailable extension, redaction, category action, and notification presentation; extension execution is not guaranteed delivery. |
| Custom ExtensionKit | `AppExtension`, declared extension point/protocol, host connection/process lifecycle | Host and extension targets, extension-point declaration, XPC/protocol version, capabilities, signing, and optional App Group | Prove handshake, interruption/invalidation, protocol mismatch, process termination, cleanup, and host fallback; an XPC connection is not a permanent process. |
| Scheduled background refresh | `BGTaskScheduler`, `BGAppRefreshTask`, `BGAppRefreshTaskRequest` | Main app target, registered identifier, permitted task identifiers, background capability/configuration | Prove registration, scheduling, launch handler, checkpoint, expiration, cancellation, reschedule, and skipped/delayed execution; the system chooses timing. |
| Deferred processing | `BGProcessingTask`, `BGProcessingTaskRequest`, resource/network/power requirements | Main app target, registered identifier and requested conditions; selected resources/entitlements are target-specific | Prove resumable work units, external power/network branch, expiration, retry/backoff, duplicate execution, and physical-device energy/time behavior. |
| Foreground-started continuous work | `BGContinuedProcessingTask`, `BGContinuedProcessingTaskRequest`, progress/cancellation | iOS 26 selected SDK/target, foreground user-start boundary, supported resource/optional GPU entitlement | Prove submit acceptance/rejection, queued/running/cancelled/expired state, progress, checkpoint/resume, resource pressure, and no claim of a deadline or daemon. |

The target graph is part of the feature: app, widget, Live Activity, notification, File Provider, custom extension, and companion targets do not inherit the main app’s process memory or all of its entitlements. Record bundle IDs, extension point, Info.plist activation rules, deployment target, capabilities/entitlements, App Group, privacy/usage strings, shared schema version, and server/APNs configuration before calling a route configured.

## Background checkpoint contract

```text
notScheduled -> scheduled -> launched -> restoring -> running
running -> checkpointed -> completed | expired | cancelled | failed
scheduled -> skipped/rejected -> retryPolicy | userVisibleFallback
```

Each work record needs a stable operation ID, schema/version, input snapshot or source revision, progress unit, checkpoint location, cancellation/expiration state, retry count/backoff, last error, and final result provenance. Commit checkpoints before acknowledging a chunk, make every side effect idempotent, and distinguish `accepted`, `started`, `checkpointed`, `completed`, and `delivered-to-surface`. A debug launch or a task object in memory is not evidence that the production scheduler will invoke or finish the job.

## Verification and release matrix

- Target setup: extension point, bundle ID, deployment target, Info.plist activation rule, App Group, capabilities, entitlements, signing, and privacy strings.
- Lifecycle: app foreground/background/terminated, extension launch/termination, locked device, low power, no network, provider unavailable, process crash, app update, and schema migration.
- Widget: placeholder/snapshot/timeline, `.never` reload, stale data, refresh budget outside Xcode, interactive intent, redacted lock-screen content, and actual Home Screen/StandBy/other supported surface.
- Live Activity: permission, foreground start, update/end, stale state, remote push environment, final content state, dismissal, and supported device/surface matrix.
- Background: normal system scheduling, debug launch/termination only as a development aid, expiration, cancellation, retry, duplicate execution, checkpoint restore, and physical-device measurements for time/memory/battery.
- ExtensionKit: host/extension handshake, interruption handler, process invalidation, XPC error, protocol version mismatch, and cleanup of proxy references.

## Sources

- [ExtensionFoundation](https://developer.apple.com/documentation/extensionfoundation)
- [AppExtension](https://developer.apple.com/documentation/extensionfoundation/appextension)
- [Adding support for app extensions to your app](https://developer.apple.com/documentation/extensionfoundation/adding-support-for-app-extensions-to-your-app)
- [NSExtensionContext](https://developer.apple.com/documentation/foundation/nsextensioncontext)
- [App Extension Programming Guide](https://developer.apple.com/library/archive/documentation/General/Conceptual/ExtensibilityPG/ExtensionOverview.html)
- [App Extension Programming Guide: Document Provider](https://developer.apple.com/library/archive/documentation/General/Conceptual/ExtensibilityPG/FileProvider.html)
- [File Provider](https://developer.apple.com/documentation/fileprovider)
- [NSFileProviderReplicatedExtension](https://developer.apple.com/documentation/fileprovider/nsfileproviderreplicatedextension)
- [Synchronizing files using file provider extensions](https://developer.apple.com/documentation/fileprovider/synchronizing-files-using-file-provider-extensions)
- [Configuring app groups](https://developer.apple.com/documentation/xcode/configuring-app-groups)
- [Shared data](https://developer.apple.com/documentation/technologyoverviews/shared-data)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit)
- [Timeline](https://developer.apple.com/documentation/widgetkit/timeline)
- [TimelineProvider](https://developer.apple.com/documentation/widgetkit/timelineprovider)
- [AppIntentTimelineProvider](https://developer.apple.com/documentation/widgetkit/appintenttimelineprovider)
- [WidgetCenter](https://developer.apple.com/documentation/widgetkit/widgetcenter)
- [Keeping a widget up to date](https://developer.apple.com/documentation/widgetkit/keeping-a-widget-up-to-date)
- [Adding interactivity to widgets and Live Activities](https://developer.apple.com/documentation/widgetkit/adding-interactivity-to-widgets-and-live-activities)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [Activity](https://developer.apple.com/documentation/activitykit/activity)
- [Displaying live data with Live Activities](https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities)
- [Starting and updating Live Activities with ActivityKit push notifications](https://developer.apple.com/documentation/activitykit/starting-and-updating-live-activities-with-activitykit-push-notifications)
- [Background Tasks](https://developer.apple.com/documentation/backgroundtasks)
- [BGTaskScheduler](https://developer.apple.com/documentation/backgroundtasks/bgtaskscheduler)
- [BGTask](https://developer.apple.com/documentation/backgroundtasks/bgtask)
- [BGTaskRequest](https://developer.apple.com/documentation/backgroundtasks/bgtaskrequest)
- [BGAppRefreshTask](https://developer.apple.com/documentation/backgroundtasks/bgapprefreshtask)
- [BGAppRefreshTaskRequest](https://developer.apple.com/documentation/backgroundtasks/bgapprefreshtaskrequest)
- [BGProcessingTask](https://developer.apple.com/documentation/backgroundtasks/bgprocessingtask)
- [BGProcessingTaskRequest](https://developer.apple.com/documentation/backgroundtasks/bgprocessingtaskrequest)
- [BGContinuedProcessingTask](https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtask)
- [BGContinuedProcessingTaskRequest](https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtaskrequest)
- [Performing long-running tasks on iOS and iPadOS](https://developer.apple.com/documentation/backgroundtasks/performing-long-running-tasks-on-ios-and-ipados)
- [BGTask expirationHandler](https://developer.apple.com/documentation/backgroundtasks/bgtask/expirationhandler)
