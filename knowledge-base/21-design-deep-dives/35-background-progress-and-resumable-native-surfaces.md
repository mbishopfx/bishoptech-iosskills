# Background progress and resumable native surfaces

## Design objective

A long-running iOS task should feel user-started, visible, cancellable, and recoverable. The system may continue work after the app backgrounds, but the person should never have to guess whether a job is queued, running, stalled, cancelled, failed, or complete.

This is an information-architecture problem before it is a Liquid Glass problem. Use native progress, Live Activity, toolbar, sheet, and notification patterns where they fit. Keep the source content, the job state, the generated result, and any later side effect separate.

## Begin with a person’s action

Continuous background work starts from an explicit foreground action. The button should communicate the actual outcome:

| Action | Better label | Avoid |
| --- | --- | --- |
| Export a video | Export 12 clips | Process |
| Analyze selected photos | Analyze selection | AI |
| Prepare a local audio set | Prepare audio | Run background task |
| Generate a draft | Generate draft for review | Automate everything |

Before submission, show source scope, estimated work shape if known, privacy treatment, and a cancel/recovery expectation. Do not promise an exact duration when the system may queue or terminate the work.

## State language

Use explicit status text:

~~~text
ready -> starting -> queued -> processing -> ready to review
                     ├-> cancelled
                     ├-> interrupted; resume available
                     └-> failed; source preserved
~~~

Every state gets:

- a title;
- a short explanation;
- a primary next action;
- an accessible announcement;
- a privacy-safe system projection;
- a recovery path that does not duplicate a side effect.

“Almost done” is not a state unless the job has a real checkpoint that supports it. Do not animate a fake percentage while the app is waiting for system resources.

## Native surface map

| Surface | Purpose | What it must not imply |
| --- | --- | --- |
| Main app | Start, configure, review source, inspect result, recover | That the app will keep running without a registered route |
| In-app progress | Current task detail and cancel | That progress is a guarantee of completion |
| System Live Activity | Visible progress when the task continues in background | That the output was saved, synced, or shared before reconciliation |
| Notification | A return-to-app prompt or completion reminder where appropriate | That a person saw or accepted the result |
| Widget | Last-known job projection | Live canonical state |
| Review sheet | Inspect/edit/confirm generated output | Automatic authorization for a side effect |

When the system owns the progress interface, the app should keep its durable job record current and use a deep link back to the review surface.

## Liquid Glass grouping

Liquid Glass is useful when it creates a functional control group:

- start/cancel controls over the current source;
- a progress capsule near the content being processed;
- a review action group once a result is ready;
- a compact status control in a navigation or toolbar region.

Keep large source previews and generated text on readable content surfaces. Avoid making the entire progress screen translucent, placing low-contrast progress text over moving media, or stacking glass controls that compete with the system Live Activity.

Material and motion should respond to state:

| State | Visual treatment | Motion rule |
| --- | --- | --- |
| Starting | Emphasized action feedback | One short transition |
| Queued | Clear text and restrained indicator | No endless shimmer |
| Processing | Progress and cancel affordance | Motion may indicate change, not fabricate work |
| Interrupted | Neutral warning plus resume/delete | Settle immediately under Reduce Motion |
| Ready to review | Emphasize review action | Reveal result once, then stop |
| Failed | Explain source preservation and retry | No red flash or alarm loop |

The interface must remain legible with reduced transparency, increased contrast, and larger text. Glass is a grouping material, not a substitute for a semantic label.

## Progress is a contract

Progress reporting should map to actual completed units:

- files exported;
- frames processed;
- samples analyzed;
- records migrated;
- chunks uploaded;
- deterministic pipeline stages completed.

If the model’s work has uncertain cost, use stage labels rather than a precise fake percentage. If the task can be cancelled, make the cancel action visible and explain what is preserved.

Use status text such as:

- “Preparing 8 selected photos”
- “Analyzing 3 of 8”
- “Paused; the original files are safe”
- “Stopped before saving the draft”
- “Ready for your review”

Avoid “done” until the result is persisted and reconciled with the domain record.

## Resumable review for on-device AI

An on-device AI task should produce a reviewable artifact:

1. preserve the original source;
2. persist the job and checkpoint;
3. write intermediate output with provenance;
4. show generated content as a proposal;
5. let the person edit, reject, or regenerate;
6. commit only after validation and confirmation.

The review surface should name the source and model/framework route in a human-readable way. It should not imply that on-device processing makes the result authoritative or that a background task can bypass the person’s normal permissions.

If a task is interrupted, invalidate any partially generated proposal whose source revision is no longer current. Never resume by applying an old proposal to a newly edited source without revalidation.

## Cancellation and interruption

Cancellation is a successful user action with a clear outcome:

- stop accepting new work;
- cancel child tasks and I/O;
- write a checkpoint or discard partial output according to policy;
- mark the job cancelled;
- remove or update the system projection;
- preserve the original source;
- let the person resume or delete.

System expiration is different from a person tapping Cancel. The UI can say “Interrupted; resume available” when the app has a safe checkpoint. If no checkpoint exists, say so plainly and offer a fresh run.

Force-quitting from the app switcher may cancel work without giving the app a normal completion callback. Reconcile on next launch from durable job records, not from in-memory flags.

## Accessibility and alternate input

An accessible task surface does not depend on a progress animation:

- expose progress as text and a value where meaningful;
- announce transitions without flooding VoiceOver with every increment;
- let VoiceOver reach cancel, pause/resume, review, and delete;
- make source scope and privacy treatment readable;
- support Dynamic Type and large accessibility sizes without hiding actions;
- test keyboard, switch, Voice Control, pointer, and touch routes;
- respect Reduce Motion and reduced transparency;
- avoid color-only warnings;
- localize title, subtitle, units, dates, and pluralization;
- move focus to the result/recovery heading after a completed task, then verify that focus behavior remains calm.

The system Live Activity is an additional surface, not a replacement for an accessible in-app review route.

## Background inference and privacy

If a task uses the background GPU or background Neural Engine route, make the required entitlement and device support explicit in the build plan. Do not hide those gates behind a generic “AI processing” label. Keep source selection, permission, retention, and generated-output policies visible.

Titles and subtitles may appear in a system progress surface. Do not include private filenames, raw transcriptions, health data, contact information, or model prompts unless the product has intentionally designed that exposure.

## Design review checklist

- Did a person explicitly start the continuous task?
- Can they see what source is being processed?
- Is queued versus processing distinct?
- Is progress tied to real work?
- Can they cancel from the app and system surface?
- Is the original source preserved?
- Is the generated result reviewable and editable?
- Does force-quit or expiration produce an honest recovery state?
- Does Liquid Glass group actions without obscuring content?
- Does the feature work with VoiceOver, Dynamic Type, Reduce Motion, reduced transparency, and alternate input?
- Does the app avoid claiming sync, export, delivery, or acceptance before reconciliation?

## Sources

- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Background Tasks](https://developer.apple.com/documentation/backgroundtasks)
- [Performing long-running tasks on iOS and iPadOS](https://developer.apple.com/documentation/backgroundtasks/performing-long-running-tasks-on-ios-and-ipados)
- [BGContinuedProcessingTask](https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtask)
- [BGContinuedProcessingTaskRequest](https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtaskrequest)
- [ActivityKit](https://developer.apple.com/documentation/activitykit/)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [AccessibilityFocusState](https://developer.apple.com/documentation/swiftui/accessibilityfocusstate)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Core ML](https://developer.apple.com/documentation/coreml)
