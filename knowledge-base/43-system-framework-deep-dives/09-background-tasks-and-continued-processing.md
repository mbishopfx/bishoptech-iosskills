# Background Tasks and continued processing

## Capability

Background execution on iOS is a family of contracts, not a promise that an app can keep running whenever it wants. Select the route that matches when the work starts, who initiated it, how long it takes, what resources it needs, and how the person should be informed.

| Work shape | Apple route | Core truth |
| --- | --- | --- |
| A short refresh at a system-selected time | BGAppRefreshTask | The system chooses the launch time and the work must finish quickly |
| Deferrable intensive maintenance or sync | BGProcessingTask | The system chooses a suitable window, often based on power and conditions |
| A user-started job that should continue when the app backgrounds | BGContinuedProcessingTask | The job begins in the foreground after a person’s action and exposes progress/cancellation |
| Finish a small operation after entering background | beginBackgroundTask | Limited grace time; expiration must cancel or defer the work |
| Transfer files while the app is not active | URLSession background configuration | The transfer lifecycle belongs to the system and the app reconciles results |
| App-specific external wake-up | Background push or a framework event | Delivery is a hint, not a guaranteed execution time |

The rest of this page focuses on the iOS 26 continuous-background route and its relationship to scheduled tasks, on-device AI, media, and system surfaces.

## The iOS 26 continuous-background route

Apple documents BGContinuedProcessingTask for critical jobs that start in the foreground and may continue in the background for minutes or more. The submission must result from a person’s action, such as tapping a button. It is not a hidden scheduler for unattended work.

Examples Apple gives include:

- video export;
- audio export in a digital audio workstation;
- creating thumbnails for a batch of photo uploads;
- image filtering or compression;
- Core ML processing or sensor-data analysis on supported devices.

The system exposes progress through a system interface, represented by a Live Activity, and the person can cancel the task. The task can also be terminated under resource pressure. A route that cannot checkpoint or recover should not be placed behind this API.

## Request composition

Create BGContinuedProcessingTaskRequest with:

- an identifier prefixed with the app’s bundle ID;
- a localized title;
- a localized subtitle;
- requiredResources when the task needs an additional supported resource such as GPU;
- a submission strategy.

The task-name portion of the identifier should be unique for the specific job. Register permitted identifiers and target capabilities in the selected app target. A request that looks correct in source can still fail with a not-permitted scheduler error when the Info.plist identifier or background configuration is wrong.

### Resource gates

For GPU work:

1. Check BGTaskScheduler.supportedResources for GPU support.
2. Set the request’s requiredResources to .gpu only when the device supports it.
3. Add the Background GPU Access capability/entitlement to the target.
4. Provide a CPU or deferred route for devices or configurations without GPU background support.

Apple also documents a Background Inference entitlement for Neural Engine inference in the background. That route is preliminary and entitlement-gated. It applies to eligible Core AI, Core ML, or Metal Performance Shaders Graph inference and must not be presented as a general permission to run every Foundation Models or Core ML workload in the background. Verify the final SDK, entitlement approval, device support, model route, and release configuration.

### Submission strategy

The default queue strategy allows the system to queue the task when resources are not immediately available. A fail strategy asks the system to reject the request if it cannot begin immediately. Choose based on the user outcome:

| User outcome | Strategy |
| --- | --- |
| “Finish this export eventually” | queue, with visible queued state |
| “Start this live transformation now” | fail or queue only if the UI explains waiting |
| “Run a large overnight maintenance job” | BGProcessingTask, not a foreground continuous task |
| “Use Neural Engine while backgrounded” | Entitlement/device/API proof first; never infer from a local model load |

The request strategy does not control battery, thermal, or system scheduling. It only communicates the product’s tolerance for delayed start.

## Lifecycle and checkpoint contract

Model the job as a durable state machine:

~~~text
draft
  -> userConfirmed
  -> submitted
  -> queued
  -> running
  -> completed

submitted -> rejected
queued/running -> cancelledByPerson
queued/running -> expired
running -> failed
any incomplete state -> resumableCheckpoint
~~~

The work layer should:

- persist an immutable job ID and source references before submission;
- write checkpoints at meaningful boundaries;
- keep progress monotonic and truthful;
- respond to expiration by cancelling or deferring work;
- make cancellation idempotent;
- save partial output in a recoverable form;
- reconcile the final result when the app returns to the foreground;
- distinguish system cancellation from a completed export;
- avoid reprocessing a source because the app relaunched after an ambiguous termination.

If the person closes the app in the app switcher, Apple documents that running continuous tasks can be cancelled without an indication to the app. The product therefore needs a reconciler that marks an incomplete job as interrupted or resumable when it next opens.

## Scheduled tasks remain separate

BGAppRefreshTask and BGProcessingTask are system-scheduled background launches. Register their launch handlers before the end of app launch, list permitted task identifiers, add the appropriate Background Modes capability, and call setTaskCompleted(success:) for the task’s lifecycle.

Use BGProcessingTask for heavy maintenance, synchronization, or model preparation that can wait. Its request can express a need for external power or network connectivity. Do not use a scheduled processing task as a substitute for a user-started continuous task when the person expects the job to begin now.

An extension may schedule a task, but Apple’s background-task guidance says the main app must register the task and the system launches the app to run it. Keep extension projections and background work in separate process contracts.

## On-device AI route

Background processing can be useful for:

- classifying a user-selected batch of local images;
- generating thumbnails or embeddings for a confirmed local import;
- running a bounded Core ML or Vision pass over a saved asset;
- compressing or preparing a media export;
- continuing a user-started task that uses supported Neural Engine/GPU resources.

The AI boundary stays the same:

1. The person selects or creates the source.
2. The app records the task and consent.
3. Deterministic preprocessing validates the asset and budget.
4. The model produces typed intermediate output.
5. The task persists progress and provenance.
6. The app presents an editable result.
7. The person confirms any domain or system side effect.

Background execution does not grant permission to access private data, make medical or identity decisions, send communication, schedule calendar events, or mutate a shared record without the app’s normal authorization and review. A model result that finished in the background is still a proposal until the domain layer accepts it.

For Foundation Models, inspect the selected availability and session contract in the target SDK. Do not assume that an on-device model session can be kept alive across suspension or that it inherits BGContinuedProcessingTask GPU/Neural Engine entitlements. The background route must be proven with the exact model/API and hardware.

## Progress and system surfaces

The system uses the task’s ProgressReporting implementation to represent progress in the Live Activity. Progress should reflect actual completed work, not a timer animation. A task that stops reporting progress can be prioritized for termination under resource pressure.

Use the task title and subtitle as concise, localized context:

- “Exporting 12 clips”
- “Preparing audio”
- “Analyzing selected photos”

Avoid:

- exposing raw file paths or private content;
- claiming the result is uploaded when only local processing completed;
- promising an exact completion time;
- presenting model confidence as task completion;
- hiding the cancel action behind decorative controls.

The main app should reconcile the Live Activity projection with the durable job record. The system interface is a user-facing status surface, not the canonical business database.

## Liquid Glass and native design

Use Liquid Glass around task controls and status only when it improves hierarchy:

- a compact action bar for start/cancel;
- a progress summary above the content being processed;
- a review sheet when a result is ready;
- a small status control that opens job details.

The material must not hide paused, failed, unavailable, or cancelled states. For reduced transparency or increased contrast, the text and progress state remain fully legible. When a person cancels from the system interface, the app should show a calm interrupted state and an explicit resume/delete action rather than an animated failure.

## Privacy and storage

Before submitting background work:

- classify the source assets and generated outputs;
- use the minimum source scope;
- store credentials and tokens in Keychain;
- protect large files using the chosen file/storage contract;
- define retention for intermediate frames, audio, embeddings, and prompts;
- redact titles/subtitles and notification projections;
- delete or preserve partial output according to a documented user choice;
- record whether output is local-only, synced, shared, or exported.

The fact that a task runs on-device does not remove privacy obligations. A background inference entitlement is a capability gate, not a license to use sensitive data without product consent.

## Verification route

- Compile the task request and the exact API/model route in the named app target.
- Inspect Info.plist permitted identifiers, Background Modes, Background GPU Access, Background Inference, model resources, and signing.
- Start the task from an explicit user action; verify rejected, queued, running, completed, expired, and cancelled states.
- Test app backgrounding, foreground return, force-quit/app-switcher termination, low battery, thermal pressure, no GPU, no Neural Engine, storage pressure, and network loss.
- Verify progress in the system interface and cancellation from that interface.
- Restart from a checkpoint and confirm no duplicate side effect.
- Test VoiceOver, Dynamic Type, Reduce Motion, reduced transparency, localization, and privacy-safe task titles.
- Use representative physical devices for GPU/Neural Engine/resource claims; simulator evidence does not prove hardware support.
- Test release entitlements and the final system surface separately from a debugger-started task.

## Sources

- [Background Tasks](https://developer.apple.com/documentation/backgroundtasks)
- [BGTaskScheduler](https://developer.apple.com/documentation/backgroundtasks/bgtaskscheduler)
- [BGTask](https://developer.apple.com/documentation/backgroundtasks/bgtask)
- [BGAppRefreshTaskRequest](https://developer.apple.com/documentation/backgroundtasks/bgapprefreshtaskrequest)
- [BGProcessingTaskRequest](https://developer.apple.com/documentation/backgroundtasks/bgprocessingtaskrequest)
- [BGContinuedProcessingTask](https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtask)
- [BGContinuedProcessingTaskRequest](https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtaskrequest)
- [Performing long-running tasks on iOS and iPadOS](https://developer.apple.com/documentation/backgroundtasks/performing-long-running-tasks-on-ios-and-ipados)
- [Choosing background strategies for your app](https://developer.apple.com/documentation/backgroundtasks/choosing-background-strategies-for-your-app)
- [Using background tasks to update your app](https://developer.apple.com/documentation/uikit/using-background-tasks-to-update-your-app)
- [BGTaskSchedulerPermittedIdentifiers](https://developer.apple.com/documentation/bundleresources/information-property-list/bgtaskschedulerpermittedidentifiers)
- [BGContinuedProcessingTaskRequest.Resources](https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtaskrequest/resources)
- [BGContinuedProcessingTaskRequest.Resources.gpu](https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtaskrequest/resources/gpu)
- [Background GPU Access entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.background-tasks.continued-processing.gpu)
- [Background Inference entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.background-tasks.continued-processing.inference)
- [Configuring background execution modes](https://developer.apple.com/documentation/xcode/configuring-background-execution-modes)
- [ActivityKit](https://developer.apple.com/documentation/activitykit/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Vision](https://developer.apple.com/documentation/vision)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
