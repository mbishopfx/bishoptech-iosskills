# BackgroundTasks, continued processing, and process boundaries

## Scope

This page covers the background execution choices that matter when an iOS app
needs to refresh content, maintain local state, finish user-started work, run a
bounded on-device AI pipeline, update a widget, or keep a system-visible progress
state honest.

The main routes are:

- BGAppRefreshTask for short, opportunistic refresh work;
- BGProcessingTask for deferred maintenance or processing;
- BGContinuedProcessingTask for a user-started foreground job that can continue
  when the app moves to the background;
- beginBackgroundTask for a short grace period to finish critical foreground
  work;
- background URLSession for transfers that should continue independently;
- background pushes and framework-specific events;
- Live Activity or widget projections that communicate current progress without
  becoming the work engine.

These mechanisms are not interchangeable. A background task is not a promise of
continuous execution, a specific start time, or a way to bypass user intent.

## Version and beta boundary

The current Apple documentation identifies BGContinuedProcessingTask and related
background GPU resources as newer capabilities whose exact availability and
entitlement requirements must be verified in the selected Xcode/iOS SDK. Record:

- deployment target and SDK version;
- whether the task/request type is final, beta, or preliminary in that SDK;
- supported device families and resource options;
- target capabilities and entitlement approval;
- task identifier and permitted identifier configuration;
- system cancellation and process-termination behavior.

Do not ship a background GPU claim because a symbol resolves. The device must
support the resource, the target must carry the entitlement, the workload must
be eligible, and the physical run must show measured behavior.

## Choose the execution strategy

Use the smallest mechanism that matches the user's expectation:

| Need | Mechanism | Core boundary |
| --- | --- | --- |
| Finish a save/send/export after the app backgrounds | beginBackgroundTask | Limited grace period; end it promptly |
| Transfer files independently | Background URLSession | Transfer lifecycle/delegate and file persistence |
| Refresh small current content | BGAppRefreshTask | System chooses when and may defer/throttle |
| Maintenance or deferred ML/database work | BGProcessingTask | System chooses a suitable time and resources |
| Continue a user-started minutes-long job | BGContinuedProcessingTask | Starts in foreground; can continue after backgrounding |
| Wake after an external event | Background push or framework event | Delivery is opportunistic and budgeted |
| Show progress/status | WidgetKit/ActivityKit/system task UI | Projection only; it is not the worker |
| Long-running sensor/capture route | Framework-specific background mode or BGContinued route | Hardware, privacy, entitlement, and thermal constraints |

A good selection answers:

1. Did the person explicitly start the work?
2. Must the work begin now, or can the system defer it?
3. Can the work be checkpointed and resumed?
4. Does it need network, CPU, GPU, sensor, camera, audio, or protected data?
5. What does cancellation mean after a partial commit?
6. What surface tells the person whether it is running, stale, or done?
7. What is the ordinary foreground fallback if background execution never occurs?

## BGAppRefreshTask

BGAppRefreshTask is for short tasks such as refreshing small amounts of content.
The system controls when the task runs. The earliestBeginDate on a request is a
hint, not a schedule guarantee.

Use it for:

- preparing a small widget projection;
- refreshing a compact feed;
- checking a server for lightweight changes;
- updating local metadata that improves the next foreground launch.

Do not use it for:

- a multi-minute model inference;
- a large media export;
- a migration that must finish before a user-visible commit;
- a workflow that requires a camera or interactive UI;
- a promise that a widget will update at a specific wall-clock time.

Register every task before the app's launch sequence ends. The permitted task
identifiers are configured for the target, and the task handler must call
setTaskCompleted(success:) when the work is done or canceled. Install an
expiration handler and make the operation cancelable.

## BGProcessingTask

BGProcessingTask is for time-consuming work that the system can schedule when
conditions are suitable, such as maintenance, synchronization, or model/data
preparation. It may run with external power or network conditions as allowed by
the system and target configuration.

Use it for:

- database maintenance and compaction;
- preparing thumbnails or indexes;
- deferred model asset preparation;
- synchronization that can safely resume;
- overnight or charging-friendly work.

The app does not choose an exact start time. It must remain correct if the task is
deferred, interrupted, or never delivered before the person opens the app.

A processing task still needs:

- an expiration handler;
- bounded memory and temporary-file cleanup;
- checkpoint or idempotent progress;
- a truthful completion record;
- a fallback that the foreground app can perform later.

## BGContinuedProcessingTask

BGContinuedProcessingTask is a distinct route for a critical, user-started job.
Apple documents that it starts in the foreground and can continue in the
background if the person backgrounds the app before the job finishes.

Good examples include:

- video/audio export;
- creating thumbnails for a user-selected batch;
- applying visual filters;
- Core ML processing initiated by a person;
- sensor-data analysis initiated by a person;
- intensive CPU/network work that can be safely continued.

The route is:

    explicit user action
      -> create BGContinuedProcessingTaskRequest
      -> register task identifier before launch completion
      -> submit request
      -> task begins in foreground
      -> user backgrounds app
      -> progress and title update through system UI
      -> checkpointed work
      -> success, expiration, or cancellation
      -> commit/fallback projection

The task is not an unattended scheduler. Do not submit it on app launch or in
response to a passive widget refresh. The initial user action must be visible
and meaningful.

### Request identity and title

Use a task identifier prefixed with the app's bundle identifier and a unique
job-specific suffix. The request title and subtitle are displayed to the person
through the system's progress interface, so they are localized, short, truthful,
and privacy-safe.

Do not put:

- an unredacted filename containing private data;
- a model prompt or transcript;
- a full location or health record;
- an internal database ID;
- a promise of completion before commit.

Use a human-readable operation label plus a bounded phase, such as “Preparing
photos” and “Analyzing 12 selected items.”

### Submission strategy

The request can use a queue strategy or a fail strategy in the selected SDK:

- queue allows the system to wait for available capacity;
- fail lets the app surface that the job could not begin immediately.

Choose fail when the user needs an immediate answer and the app has a clear
foreground retry. Choose queue when the user explicitly asked for a job that may
continue and the product can show queued state.

A queued task is not running. The app's state model must distinguish requested,
queued, running, paused/expired, canceled, failed, and committed.

### Progress, expiration, and cancellation

BGContinuedProcessingTask conforms to a progress-reporting contract. Report
meaningful progress with task.progress and update the displayed title/subtitle
when the phase changes.

The system can terminate a continuous task abruptly under resource constraints.
If the person cancels the task through the system interface, the expiration
handler is invoked. If the person closes the app in the app switcher, Apple
documents that the system cancels running tasks without necessarily providing a
separate cancellation indication.

Therefore:

- persist a checkpoint before or alongside each durable unit;
- make the operation idempotent by job ID and input revision;
- release camera, audio, file, model, and GPU resources on cancellation;
- mark an incomplete job as canceled/expired, not successful;
- show the last committed prefix and a retry/resume option;
- do not assume that deinitialization or a final callback always runs.

### Background GPU access

If the workload requires GPU resources, first check whether the system reports
GPU support in the available resources. The target also needs the documented
Background GPU Access capability/entitlement. Not every device supports the
resource, and entitlement approval does not guarantee that the task will run
under every thermal, power, or system condition.

A safe capability ladder is:

    supportedResources contains GPU?
      -> entitlement and target configuration present?
      -> workload can use GPU safely?
      -> device power/thermal budget acceptable?
      -> request GPU resource
      -> if unavailable, use CPU/foreground/deferred fallback

Do not tell a person “GPU processing is running” merely because the request asked
for GPU. Show the actual workload state and fallback.

## Registration and launch lifecycle

Apple's background-task route requires registration before the end of the app
launch sequence. A practical lifecycle is:

1. declare permitted identifiers in the target's Info.plist;
2. register every handler during app launch;
3. schedule a request only after the product event that justifies it;
4. start work inside the launch handler;
5. attach expiration/cancellation handling;
6. make the task complete through the documented API;
7. reschedule recurring refresh/processing work when appropriate;
8. write a durable outcome and update projections.

An extension may schedule a background task, but the main app must register the
task. Do not assume a widget extension can register the host app's work or that a
main-app singleton exists in an extension process.

When the system launches an app for a background event, the app may launch
directly into the background and be suspended again. Avoid UI assumptions,
window access, navigation, prompts, or MainActor work that requires a visible
scene. Keep domain services and persistence safe for a background process.

## Concurrency and resource ownership

Use an actor or a serialized job coordinator for:

- checkpoint state;
- model/session ownership;
- temporary file names;
- output commit;
- progress calculation;
- retry/resume policy.

Cancellation must travel through child tasks. Avoid detached work that survives
the task's expiration handler. If a framework callback is not cancellation-aware,
wrap it with a cancellation handler and ensure the callback cannot commit after
the job was canceled.

A safe ownership rule is:

    task lifetime owns operation lifetime
      -> operation owns temporary resources
      -> commit owns final resource
      -> cancellation releases temporary resources
      -> retry starts from a durable checkpoint

Never make a background task mutate SwiftUI view state directly. Write a domain
result, then let the next foreground/widget/activity projection observe it.

## On-device AI and background work

On-device AI can be a good workload for a user-started continuous task or a
deferred processing task when the product has a clear reason to run it. Choose
the route based on the user's intent and workload:

| AI job | Preferred route |
| --- | --- |
| Short summary of current visible text | Foreground Foundation Models route |
| User-selected batch of photos | BGContinuedProcessingTask after explicit start |
| Overnight thumbnail/index preparation | BGProcessingTask |
| Small widget refresh | WidgetKit timeline/projection; no model in renderer |
| Live event classification | Framework-specific sensor/capture route plus explicit policy |
| Model download/compilation | Background URLSession/BGProcessing with resource checks |
| Sensitive data transformation | On-device route with retention and cancellation policy |

The AI operation must record:

- input IDs and source revision;
- model/framework identifier;
- device/model availability;
- prompt/schema/version when relevant;
- progress phase;
- accepted/rejected output count;
- checkpoint and cancellation reason;
- commit revision;
- fallback when the model is unavailable.

Do not use a background task to quietly process an entire library without
explicit scope and retention policy. A user-selected batch is not permission to
retain every original, generated output, prompt, or feature vector forever.

## Progress surfaces and Live Activities

BGContinuedProcessingTask can display system progress in a Live Activity-like
system interface. A product may also have its own ActivityKit Live Activity for
the domain event. Treat them as separate system-owned projections unless the
selected SDK explicitly provides a supported unification.

Avoid two competing progress stories:

- choose the system task progress for a private export/analysis operation;
- use a custom ActivityKit Live Activity for a product event that remains useful
  after the work process ends;
- if both are required, share one job ID, one revision, one cancellation policy,
  and one completion state;
- never let one surface say “complete” while the durable commit is still pending.

WidgetKit widgets can show last-known state, but they are not the worker and do
not replace the task's progress/cancellation contract.

## Background URLSession and transfer boundaries

Use background URLSession for transfers that should continue independently of app
execution. Keep transfer state separate from a processing task:

    transfer accepted by URLSession
      -> task/extension receives completion event
      -> file moved to durable location
      -> domain record committed
      -> widget/activity projection refreshed

Do not keep a large upload/download inside a BGAppRefreshTask if the transfer
framework is the correct owner. On expiration, hand off or cancel according to
the documented transfer route.

## Testing and physical proof

Scheduled background tasks can be delayed for hours. Apple provides development
debugger support for starting and terminating tasks on devices, but those private
simulation functions must never ship in the App Store binary.

Proof must include:

- launch registration and permitted identifiers;
- scheduled BGAppRefresh/BGProcessing behavior on a physical device;
- user-started BGContinuedProcessingTask start and background transition;
- progress updates and system cancellation;
- expiration and abrupt termination;
- app-switcher close behavior;
- checkpoint/resume and partial commit;
- device resource availability, GPU entitlement, and fallback;
- model/capture/file cleanup;
- widget/Live Activity projection truth;
- accessibility, localization, privacy, thermal, battery, and archive proof.

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
- [Refreshing and Maintaining Your App Using Background Tasks](https://developer.apple.com/documentation/backgroundtasks/refreshing-and-maintaining-your-app-using-background-tasks)
- [Starting and Terminating Tasks During Development](https://developer.apple.com/documentation/backgroundtasks/starting-and-terminating-tasks-during-development)
- [Background GPU Access](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.background-tasks.continued-processing.gpu)
- [Preparing your UI to run in the background](https://developer.apple.com/documentation/uikit/preparing-your-ui-to-run-in-the-background)
- [About the background execution sequence](https://developer.apple.com/documentation/uikit/about-the-background-execution-sequence)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Core ML](https://developer.apple.com/documentation/coreml/)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit/)
- [ActivityKit](https://developer.apple.com/documentation/activitykit/)
- [Swift concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
