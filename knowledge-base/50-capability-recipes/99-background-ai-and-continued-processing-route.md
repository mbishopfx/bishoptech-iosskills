# Background AI and continued-processing capability route

## Capability contract

Use this route when a person starts a job in the foreground and the job may
continue after the app moves to the background, or when the system may defer
refresh/maintenance work until a suitable opportunity.

The route returns:

1. a durable job record;
2. a task request/handler appropriate to the product story;
3. a progress, cancellation, and checkpoint contract;
4. a compact widget/Live Activity projection;
5. a fallback when the task is delayed, expired, canceled, unavailable, or
   resource-constrained.

The worker is the app-owned job coordinator. BackgroundTasks supplies runtime;
it does not become the domain source of truth.

## Choose the route

| Product need | Route |
| --- | --- |
| Finish a short save after backgrounding | beginBackgroundTask |
| Short opportunistic refresh | BGAppRefreshTask |
| Deferred maintenance or batch preparation | BGProcessingTask |
| User-started minutes-long export or local AI job | BGContinuedProcessingTask |
| File upload/download independent of app runtime | Background URLSession |
| Irregular server event | Background push plus ordinary app reconciliation |
| Device-specific capture/sensor work | Framework-specific mode plus a checkpointed worker |
| Read-only glanceable status | WidgetKit projection |
| Follow a meaningful event | ActivityKit Live Activity |

Do not select BGContinuedProcessingTask merely because a job is expensive. It
must begin from a user action in the foreground and remain eligible for the
system's resources and policy.

## Job record

Define a record that survives process termination:

~~~swift
struct BackgroundJob: Codable, Sendable {
    enum State: String, Codable, Sendable {
        case requested
        case queued
        case running
        case backgrounded
        case committing
        case completed
        case canceled
        case expired
        case failed
        case needsReview
    }

    let id: UUID
    let kind: String
    let inputIDs: [String]
    let inputRevision: String
    var state: State
    var completedUnits: Int64
    var totalUnits: Int64?
    var checkpoint: String?
    var resultRevision: String?
    var modelIdentifier: String?
    var errorCategory: String?
    var updatedAt: Date
}
~~~

The job ID is not a permission token. Revalidate account, source revision,
authorization, and current domain state before each commit.

## Target and capability setup

For scheduled BGAppRefreshTask/BGProcessingTask:

1. add the appropriate Background Modes capability;
2. add permitted identifiers to the target's Info.plist;
3. register handlers during main-app launch;
4. schedule requests only after a product event or reconciliation decision;
5. keep identifiers stable across releases.

For BGContinuedProcessingTask:

1. verify selected SDK and deployment availability;
2. add the required Background Tasks support;
3. use a bundle-ID-prefixed, job-specific identifier;
4. create the request only in response to a foreground user action;
5. choose queue or fail submission strategy;
6. request GPU resources only when supported and entitled;
7. register the launch handler before app launch registration finishes;
8. write title/subtitle copy that is localized and privacy-safe.

Extensions may schedule work, but the main app registers the task. Keep target
membership explicit and do not assume the main app's UI process is alive.

## Route A: user-started continued processing

1. Person selects a bounded input set.
2. App validates access and creates a job record.
3. App presents a clear start action.
4. App creates BGContinuedProcessingTaskRequest.
5. App chooses resources and submission strategy.
6. App submits the request.
7. Task starts in the foreground.
8. Worker reports phase/progress and writes checkpoints.
9. When the app backgrounds, the task continues only as the system permits.
10. On completion, commit results and projections.
11. On expiration/cancellation, save truthful partial state and release resources.
12. On next launch, reconcile the task and job record.

The user-started boundary protects against silent background AI or library-wide
processing. The selected input scope remains part of the job record.

## Route B: deferred BGProcessing work

Use BGProcessingTask for work that can wait:

1. app or foreground reconciliation creates a maintenance job;
2. request is submitted with an earliest begin hint if appropriate;
3. system launches the app at its chosen time;
4. handler loads the job and current source revision;
5. work runs with cancellation/expiration handling;
6. checkpoint and commit are durable;
7. task reports success/failure;
8. next scheduled request is submitted only if the product still needs it.

Do not promise a completion time from the scheduling request. If a widget or
activity needs current content before the task runs, show stale/queued state.

## Route C: on-device AI workload

Use the following phases:

    scope inputs
      -> check device/model availability
      -> prepare bounded assets
      -> run local inference
      -> validate typed proposals
      -> write checkpoint
      -> optional user review
      -> commit approved results
      -> refresh widget/activity/search projection

The AI worker must define:

- input retention and deletion;
- model asset lifecycle;
- CPU/GPU selection and fallback;
- memory/thermal limits;
- cancellation point;
- partial proposal policy;
- review requirement;
- source and model revision;
- user-visible progress phases.

A local model result is not a domain commit. The worker can prepare proposals
while the app remains in the background, but an external or irreversible action
should return to an app-owned review route.

## Route D: capture/media pipeline

For a user-selected media workload:

1. acquire user-approved source URLs/assets;
2. copy or security-scope only what the job needs;
3. create a durable input manifest;
4. release picker/camera UI resources before backgrounding;
5. process one bounded unit at a time;
6. persist output or checkpoint;
7. cancel the current framework request when task expires;
8. remove temporary files on cancel/sign-out/retention expiry;
9. finalize output before reporting success;
10. project the committed result to widgets/activities.

Do not keep a live camera session or UI object as a hidden dependency of a
background job unless the selected framework explicitly documents that route.

## Route E: progress and system surfaces

Choose one primary progress story:

| Job type | Primary surface | Secondary surface |
| --- | --- | --- |
| Private export | System continued-task progress | In-app job history |
| User-facing delivery/event | ActivityKit Live Activity | Widget summary |
| Deferred maintenance | In-app history | Widget stale/ready state |
| AI suggestions | System task progress | App review queue |
| Server transfer | Background URLSession state | Activity/widget if useful |

If a custom ActivityKit Live Activity is used alongside the system continued-task
progress, share job ID, source revision, phase, and cancellation state. Do not
create two unrelated progress bars.

## Route F: checkpoint and commit

A checkpoint is safe when it can be replayed without duplicating durable output.

Use:

    job ID + input revision + unit ID + result hash

Before writing a result:

1. check cancellation;
2. check source revision;
3. check account/authorization;
4. check whether the unit is already committed;
5. write output atomically;
6. advance the checkpoint;
7. update the projection.

Report completed progress only after the unit reaches the chosen durable boundary.
For an all-or-nothing export, completed work may be temporary and progress should
not imply a usable file until finalization.

## Route G: fallback matrix

| Condition | Fallback |
| --- | --- |
| BGContinued unavailable in selected SDK/device | Foreground progress or BGProcessing/deferred route |
| GPU unsupported or not entitled | CPU, foreground, or defer |
| Queue submission delayed | Show queued state and allow cancel |
| Fail submission rejected | Keep job requested and offer retry |
| Model unavailable | Source-only or deterministic fallback |
| Low memory/thermal state | Reduce batch, checkpoint, defer |
| Network unavailable | Local work, background URLSession, or retry |
| App switcher closure | Mark interrupted and reconcile on launch |
| Task expires | Save partial state and offer resume |
| User cancels | Stop, release, report prefix, no silent retry |
| Sign-out/privacy revoke | Cancel or redact and delete according to policy |
| Commit conflict | Create review state, never overwrite silently |

## Route H: release and distribution

Before distribution, inspect:

- Background Modes and Background GPU Access capability;
- permitted task scheduler identifiers;
- target membership of handlers and resources;
- localized task title/subtitle;
- privacy/usage descriptions;
- model and media resource membership;
- App Group/shared-store configuration;
- cancellation and recovery behavior in a signed archive;
- device/OS availability branches;
- no private task-simulation calls in release code;
- widget/activity/control projections after task completion.

## Sources

- [Background Tasks](https://developer.apple.com/documentation/backgroundtasks/)
- [BGTaskScheduler](https://developer.apple.com/documentation/backgroundtasks/bgtaskscheduler)
- [BGAppRefreshTask](https://developer.apple.com/documentation/backgroundtasks/bgapprefreshtask)
- [BGProcessingTask](https://developer.apple.com/documentation/backgroundtasks/bgprocessingtask)
- [BGContinuedProcessingTask](https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtask)
- [BGContinuedProcessingTaskRequest](https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtaskrequest)
- [Performing long-running tasks on iOS and iPadOS](https://developer.apple.com/documentation/backgroundtasks/performing-long-running-tasks-on-ios-and-ipados/)
- [Using background tasks to update your app](https://developer.apple.com/documentation/uikit/using-background-tasks-to-update-your-app)
- [Choosing Background Strategies for Your App](https://developer.apple.com/documentation/backgroundtasks/choosing-background-strategies-for-your-app)
- [Starting and Terminating Tasks During Development](https://developer.apple.com/documentation/backgroundtasks/starting-and-terminating-tasks-during-development)
- [Background GPU Access](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.background-tasks.continued-processing.gpu)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit/)
- [ActivityKit](https://developer.apple.com/documentation/activitykit/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Core ML](https://developer.apple.com/documentation/coreml/)
- [App Groups](https://developer.apple.com/documentation/xcode/configuring-app-groups)
- [Swift concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
