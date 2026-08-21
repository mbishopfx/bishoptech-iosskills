# Background work, progress, and cancellation design

## Design objective

Background execution is a trust contract. The person needs to know:

- why work was started;
- whether it is queued, running, paused, or canceled;
- what has safely completed;
- what will happen if the app is backgrounded or terminated;
- whether a model, GPU, network, or sensor is still in use;
- how to resume, retry, or discard the incomplete work.

A polished native design makes the system's constraints legible. It does not
pretend that an opportunistic background task is a persistent worker.

## Choose the product story before the API

| User story | Design surface | Required truth |
| --- | --- | --- |
| “Keep my feed fresh” | Widget/timeline and BGAppRefresh | Refresh can be delayed |
| “Prepare my library tonight” | BGProcessing | The system chooses a suitable time |
| “Export these selected items now” | BGContinuedProcessingTask | The person started it; it may be canceled/expired |
| “Keep this transfer going” | Background URLSession | Transfer lifecycle is separate from processing |
| “Follow this event” | ActivityKit Live Activity | Event state is not identical to worker state |
| “Analyze this selected batch locally” | Continuous/deferred task plus review | AI output is a proposal until committed |
| “Finish saving this draft after leaving” | beginBackgroundTask | Only a short grace window exists |

Do not call a task “background processing” in the UI when it is merely queued for
a future system opportunity. Use distinct copy for requested, queued, running,
and committed.

## A state machine people can understand

Use one durable job state machine:

    draft
      -> requested
      -> queued
      -> running
      -> backgrounded
      -> committing
      -> completed

Any active state can become:

    canceled
    expired
    failed
    blocked
    needsReview

The system task's progress is a view of this state machine. It is not the state
machine itself. Persist a job ID, input revision, completed unit count, and
commit revision so a relaunch can reconcile it.

### State copy

| State | Good copy | Avoid |
| --- | --- | --- |
| Requested | “Preparing selected photos” | “Done” |
| Queued | “Waiting for device resources” | “Running” |
| Running | “Analyzing 12 of 40” | Spinner with no count |
| Backgrounded | “Continuing while you use another app” | “Always running” |
| Committing | “Saving results” | “Finished” before write |
| Completed | “Saved 40 results” | “AI says complete” |
| Canceled | “Canceled after 12 items; 12 results saved” | “Canceled” with no commit truth |
| Expired | “Stopped by the system; resume when ready” | “Failed” if partial work is safe |
| Blocked | “Needs access to continue” | Repeated retry loop |
| Needs review | “12 suggestions ready to review” | Auto-publish |

## Native system treatment

The system supplies the outer presentation for background-task progress, Live
Activities, widgets, and other system surfaces. Do not build a custom glass
dashboard that pretends to be the system task UI.

Use app-owned Liquid Glass only in the main app for:

- a review panel;
- a phase/action toolbar;
- a compact job inspector;
- a source-linked result card;
- a retry/resume action cluster.

Use semantic system surfaces for:

- task title/subtitle/progress;
- Live Activity content;
- widget background and rendering mode;
- control buttons/toggles;
- accessibility announcements.

The app's custom surface should hand off to the system surface with a clear
transition: “Continue in background” is different from “This screen remains
active.”

## Progress hierarchy

Progress should answer three questions in order:

1. Is the job alive?
2. How much has completed?
3. What is the next meaningful state?

A good progress model contains:

- a stable job title;
- a phase label;
- completed/total units when total is known;
- indeterminate state when total is not knowable;
- a freshness timestamp;
- a cancellation affordance;
- a retry/resume route;
- a completion/partial-commit summary.

Do not update the UI for every internal token, model callback, or frame. Coalesce
progress to meaningful units and avoid making the system think a task is stuck
because the UI only changes after a huge batch.

### AI progress

For an AI pipeline, expose phases instead of false precision:

    importing -> preparing -> analyzing -> validating -> saving -> complete

If a model reports token progress, translate it to a product phase unless token
count is genuinely meaningful to the person. Never expose a generated confidence
as a progress percentage.

## Cancellation design

Cancellation is a normal user action and an expected system event.

Before a job starts, state what cancellation means:

- no output will be saved;
- completed units remain saved;
- the job can resume from a checkpoint;
- temporary files are discarded;
- the model/session is released;
- the task will not restart automatically.

When cancellation happens:

1. stop new work;
2. cancel child tasks and framework requests;
3. finish or roll back the current safe unit;
4. persist a truthful checkpoint;
5. release temporary resources;
6. update the projection;
7. show the committed prefix and recovery route.

Do not display “Canceled” while a detached task continues writing records. Do not
silently retry a user-canceled AI or export task.

## Partial commit and resume

For batch operations, prefer a unit of work that can be committed independently
or an explicit transaction with a clear all-or-nothing boundary.

| Operation | Safe cancellation policy |
| --- | --- |
| Thumbnail generation | Keep completed thumbnails with source revision |
| AI classification | Keep accepted/approved results only; mark unreviewed suggestions |
| Video export | Keep only finalized file; delete incomplete temporary output |
| Database migration | Use atomic migration/checkpoint supported by the storage layer |
| Upload | Let background URLSession own transfer; commit after final file event |
| Sensor analysis | Store bounded raw/intermediate data under explicit retention policy |

The resume key should include the source revision. If the source changes, start a
new proposal or ask for review rather than applying results to a different input.

## Avoid duplicate progress surfaces

A continuous background task can have system progress, and the product may have
an ActivityKit Live Activity. Use a single visual hierarchy:

- system task progress for the execution operation;
- Live Activity for an event the person wants to follow after execution;
- widget for last-known summary;
- app screen for review and detailed recovery.

If both system task progress and an ActivityKit activity are present, the job ID
and source revision must be shared. The completion transition must be coordinated
so the product never shows contradictory progress.

## AI review and side effects

Background AI work should produce proposals, not silent side effects. Put source
IDs, model version, and review state in the job record. Keep the system progress
surface concise:

- “Analyzing selected photos”;
- “Suggestions ready to review”;
- “Saved 18 approved results.”

Do not say:

- “Your library is organized” before user-approved commit;
- “The model is certain” when the score is not calibrated;
- “All data stayed on device” unless the actual route and logging prove it;
- “Complete” before files, records, indexes, and projection are finalized.

If the device lacks the model, GPU, language, memory, or thermal headroom, choose a
clear fallback: defer, use CPU if supported, return source-only results, or ask
the person to retry in the foreground.

## Privacy and lock state

A background job may continue while the device is locked. Design:

- a lock-safe title/subtitle;
- no private filename, person, location, health, or message data in the system
  progress label;
- private projections redacted from widgets and Live Activities;
- secure temporary-file handling;
- deletion on cancel/sign-out/revocation;
- no model prompt/transcript in progress logs;
- explicit retention for source and generated artifacts.

System surfaces are notification-adjacent. Assume a bystander may see the title or
completion state.

## Accessibility and localization

Progress is not accessible just because it has a percentage.

Verify:

- VoiceOver announces job title, phase, count, and completion/cancellation state;
- Dynamic Type preserves the phase and count;
- Voice Control can invoke retry/resume/cancel;
- Switch Control can reach the action cluster;
- reduced motion still communicates state transitions;
- increased contrast and reduced transparency preserve hierarchy;
- localized pluralization, dates, units, and long/RTL strings remain truthful;
- generated summaries have bounded spoken output.

Use the system's labels and actions whenever possible. A custom glass panel must
not hide the actual accessible control behind a decorative overlay.

## Error and repair design

Every failure should answer:

1. What stopped?
2. What was saved?
3. What can the person do now?
4. Will retry duplicate work?
5. Does the app need permission, network, power, storage, or a model?

Examples:

| Failure | Repair |
| --- | --- |
| Resource unavailable | Retry later or continue without optional GPU |
| Permission revoked | Open the appropriate settings/review route |
| Low storage | Release temporary files and ask to free space |
| Model unavailable | Use source-only fallback or defer |
| Network lost | Resume transfer or keep local work |
| Source changed | Re-run proposal against new revision |
| Task expired | Resume from checkpoint |
| App switcher closed | Mark interrupted and offer safe recovery |
| Commit conflict | Review/merge rather than overwrite |

## Native visual review checklist

Before shipping a background-facing screen:

- Is the primary action native and semantically labeled?
- Is custom Liquid Glass limited to app-owned hierarchy?
- Does the system surface remain useful if the app UI is gone?
- Does the copy distinguish queued, running, stale, canceled, and completed?
- Does the person know whether a partial commit occurred?
- Is the cancellation path honest and fast?
- Can the job resume without duplicating outputs?
- Are AI suggestions visually distinct from approved records?
- Are sensitive details redacted on locked/system surfaces?
- Has the design been tested with accessibility settings and long localization?

## Sources

- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Background Tasks](https://developer.apple.com/documentation/backgroundtasks/)
- [Performing long-running tasks on iOS and iPadOS](https://developer.apple.com/documentation/backgroundtasks/performing-long-running-tasks-on-ios-and-ipados/)
- [Choosing Background Strategies for Your App](https://developer.apple.com/documentation/backgroundtasks/choosing-background-strategies-for-your-app)
- [Using background tasks to update your app](https://developer.apple.com/documentation/uikit/using-background-tasks-to-update-your-app)
- [Preparing your UI to run in the background](https://developer.apple.com/documentation/uikit/preparing-your-ui-to-run-in-the-background)
- [About the background execution sequence](https://developer.apple.com/documentation/uikit/about-the-background-execution-sequence)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit/)
- [ActivityKit](https://developer.apple.com/documentation/activitykit/)
- [Displaying live data with Live Activities](https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities)
- [Liquid Glass adoption](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Core ML](https://developer.apple.com/documentation/coreml/)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessibility](https://developer.apple.com/accessibility/)
