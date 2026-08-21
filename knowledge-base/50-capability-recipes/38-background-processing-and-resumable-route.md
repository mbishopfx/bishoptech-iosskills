# Background processing and resumable work route

## Use this route when

Use this route for a user-started job that should continue if the person backgrounds the app, or for work the system can schedule later:

- media export;
- photo thumbnail or compression batches;
- bounded Vision/Core ML processing;
- sensor-data analysis;
- local database maintenance;
- deferred sync;
- long-running on-device AI work with an approved and supported resource route.

Choose the smallest background contract. A background task is not a replacement for a server, a perpetual process, or an unbounded AI worker.

## Route selector

| Outcome | Route | Start condition | Evidence boundary |
| --- | --- | --- | --- |
| Refresh a small amount of content | BGAppRefreshTask | System-selected | The system chooses time and may defer |
| Perform heavy maintenance or sync later | BGProcessingTask | System-selected, often power/network-aware | Requires scheduled-task proof, not immediate-start proof |
| Finish a person-started export or analysis | BGContinuedProcessingTask | Foreground user action | Requires progress, cancellation, checkpoint, and system Live Activity proof |
| Finish a short save/upload after backgrounding | beginBackgroundTask | App enters background | Limited grace period and expiration proof |
| Transfer large files | Background URLSession | User/system starts a transfer | URLSession delegate and file reconciliation proof |
| Run AI in the background | Continued processing + exact model/resource entitlement | User-started or supported background event | Exact API, entitlement, hardware, model, thermal, and privacy proof |

Do not put a scheduled maintenance job behind the continuous route just because the work is expensive. Do not put an interactive export behind BGProcessingTask if the person expects it to start as soon as they tap.

## Build contract for BGContinuedProcessingTask

### 1. Record the job before submission

Persist:

- a job identifier;
- source asset identifiers and security scope;
- operation and model/framework version;
- privacy/retention policy;
- checkpoint schema version;
- current stage and completed units;
- cancel/resume policy;
- whether the output is local, synced, shared, or exported.

### 2. Require an explicit user action

The foreground screen should explain what will happen and offer a clear start action. The submission is not an invisible side effect of app launch, a notification, or model availability.

### 3. Configure request resources

Set a bundle-prefixed identifier, localized title/subtitle, and strategy. Check supported GPU resources before requesting GPU. Add Background GPU Access only if the exact target and release route are eligible. Treat Background Inference as a separate preliminary entitlement route.

### 4. Register early

Register the task handler during app launch. Add the identifier to BGTaskSchedulerPermittedIdentifiers and the relevant Background Modes/entitlements. The main app target owns registration even when another surface initiates the request.

### 5. Checkpoint and report progress

Use a durable stage model and report real progress through BGContinuedProcessingTask.progress. Update the title/subtitle with concise, localized state. Do not use a clock animation as progress.

### 6. Handle expiration and cancellation

Set expirationHandler, stop child work, write a checkpoint, and mark the job interrupted/cancelled. Make cancellation idempotent and keep source data safe.

### 7. Reconcile after return

On foreground return, read the job record and output manifest. Do not trust an in-memory completion flag or a stale system projection. Move the person to the review surface only after the output is persisted and validated.

## Scheduled task route

For BGAppRefreshTask and BGProcessingTask:

1. register every handler before the end of app launch;
2. add the permitted identifier;
3. add the correct Background Modes capability;
4. submit a request with the appropriate constraints;
5. schedule the next run only when the product needs recurring work;
6. set task completion success/failure;
7. keep the work bounded and restartable.

The system chooses the actual launch time. Design the UI as “last attempted,” “next eligible,” or “waiting for the system,” never as an exact appointment.

## On-device AI pipeline

Use this boundary:

~~~text
user selects source
  -> local job record
  -> deterministic validation
  -> bounded model/vision/core-ml stage
  -> checkpointed typed output
  -> reviewable proposal
  -> explicit domain commit
  -> optional sync/system side effect
~~~

For background Neural Engine or GPU work:

- confirm the exact API can run in the selected background route;
- confirm device support at runtime;
- verify the entitlement in the signed artifact;
- keep a CPU/deferred fallback;
- cap input size, duration, and output;
- preserve source and provenance;
- test thermal/memory pressure;
- do not describe background inference as guaranteed availability.

The app may generate a draft while backgrounded; it still needs normal validation, privacy, authorization, and confirmation before changing a calendar, contact, health record, shared record, notification, or purchase.

## Extension and system-surface handoff

An App Intent, widget, Live Activity, or notification can show or request a job, but the app-owned job record remains canonical. Model each handoff:

| Handoff | Re-check |
| --- | --- |
| Widget to app | Job exists, source still available, status is fresh |
| Notification to app | User action, privacy, current job status |
| App Intent to job | Entity identity, authorization, confirmation, idempotence |
| Live Activity to app | Job ID, current stage, cancellation/review outcome |
| Background task to SwiftData | Container/context ownership, actor isolation, save result |

Never treat a Live Activity update or completion callback as proof that a file was shared, a record was synced, or a person accepted an AI result.

## Failure and recovery table

| Failure | Durable state | User route |
| --- | --- | --- |
| Submission not permitted | rejected | Fix configuration or offer foreground-only run |
| System queues task | queued | Continue using app; show waiting state |
| No GPU support | resourceUnavailable | CPU/deferred route or explain limitation |
| Task expires | interrupted | Resume from checkpoint or restart |
| Person cancels | cancelled | Preserve source; discard/resume by choice |
| Force-quit | unknownUntilReconcile | Reconcile job/output on next launch |
| Model/input failure | failed | Show source-safe error and retry/edit |
| Thermal/memory pressure | paused/interrupted | Release resources and offer resume |
| Output save fails | outputPending | Retry persistence before declaring success |

## Privacy and release gates

- Usage descriptions and privacy manifests match the real source.
- Task title/subtitle do not expose sensitive data.
- Background GPU/Inference entitlements are approved and present only where needed.
- Model resources are included in the correct target.
- App Groups are used only when a cross-process file/data contract is explicit.
- Checkpoints are versioned and migration-tested.
- The system Live Activity and in-app review are accessible.
- Production archive and physical-device behavior are tested separately from debugger task simulation.

## Verification questions

- Who started the job?
- Which framework owns the scheduling?
- What is the maximum expected runtime and unit of progress?
- Can the source and partial output be recovered after termination?
- What happens when a person cancels from the system interface?
- Which device/resource entitlement is required?
- What exact AI/API route runs in the background?
- Does the generated output remain a proposal?
- Which system surface reports status, and what can it honestly claim?
- What evidence exists for signed hardware, release entitlements, and production privacy?

## Sources

- [Background Tasks](https://developer.apple.com/documentation/backgroundtasks)
- [Choosing background strategies for your app](https://developer.apple.com/documentation/backgroundtasks/choosing-background-strategies-for-your-app)
- [Performing long-running tasks on iOS and iPadOS](https://developer.apple.com/documentation/backgroundtasks/performing-long-running-tasks-on-ios-and-ipados)
- [BGContinuedProcessingTask](https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtask)
- [BGContinuedProcessingTaskRequest](https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtaskrequest)
- [BGProcessingTaskRequest](https://developer.apple.com/documentation/backgroundtasks/bgprocessingtaskrequest)
- [BGAppRefreshTaskRequest](https://developer.apple.com/documentation/backgroundtasks/bgapprefreshtaskrequest)
- [BGTaskScheduler](https://developer.apple.com/documentation/backgroundtasks/bgtaskscheduler)
- [Using background tasks to update your app](https://developer.apple.com/documentation/uikit/using-background-tasks-to-update-your-app)
- [BGTaskSchedulerPermittedIdentifiers](https://developer.apple.com/documentation/bundleresources/information-property-list/bgtaskschedulerpermittedidentifiers)
- [Background GPU Access](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.background-tasks.continued-processing.gpu)
- [Background Inference](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.background-tasks.continued-processing.inference)
- [Configuring background execution modes](https://developer.apple.com/documentation/xcode/configuring-background-execution-modes)
- [ActivityKit](https://developer.apple.com/documentation/activitykit/)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Vision](https://developer.apple.com/documentation/vision)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
