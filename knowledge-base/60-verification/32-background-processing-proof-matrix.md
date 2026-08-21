# Background processing and continued-task proof matrix

This matrix separates a task request, scheduler permission, actual execution, progress system surface, resource entitlement, AI result, cancellation, and release behavior. A debugger-started task or a successful foreground export does not prove background continuation.

## Evidence levels

| Level | Evidence | What it proves |
| --- | --- | --- |
| L0 | Apple route and target review | The selected BGAppRefreshTask, BGProcessingTask, BGContinuedProcessingTask, URLSession, or foreground grace route matches the user outcome. |
| L1 | Deterministic job fixtures | Checkpoint state, progress reducer, idempotent cancellation, retry, output manifest, stale proposal invalidation, and privacy redaction. |
| L2 | Preview/simulator/UI fixture | Main-app start/review states, accessibility labels, Liquid Glass variants, fake progress, and system-surface deep links. |
| L3 | Signed physical-device task run | Entitlements, resource support, background transition, expiration/cancel behavior, progress, thermal/memory/resource states, and durable output. |
| L4 | Long-running/recovery run | Force-quit/relaunch, checkpoint resume, no-network/low-power/thermal/storage pressure, repeated cancellation, and duplicate-side-effect tests. |
| L5 | Release artifact and supported-device matrix | Final target membership, Info.plist identifiers, capabilities/entitlements, model resources, privacy copy, Live Activity projection, and release build. |

## Route and scheduling

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| BGAppRefreshTask is appropriate | Short refresh fixture, registered identifier, scheduler run, completion call | The system controls timing and may defer or omit a run. |
| BGProcessingTask is appropriate | Heavy deferrable job, power/network constraints, scheduled launch, expiration, completion | A scheduled task is not immediate-start proof. |
| BGContinuedProcessingTask is appropriate | Foreground user action, request submission, background transition, progress/cancel system surface | A background task cannot be silently started from launch or arbitrary model output. |
| Grace-time background task is sufficient | Background entry, bounded save/upload, expiration cancellation, end call | Limited grace time is not a long-running worker. |
| Background URLSession is appropriate | Transfer delegate, relaunch/reconcile, file protection, retry, destination validation | Transfer completion is not domain import/share completion. |

## Target configuration

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Scheduler permits the task | Identifier appears in BGTaskSchedulerPermittedIdentifiers and the correct target | Source registration alone can still fail with not permitted. |
| Background mode is present | Signed UIBackgroundModes/capability inspection for the selected route | A capability in another target does not configure the app. |
| GPU background use is allowed | supportedResources includes GPU, request requires GPU, Background GPU Access entitlement is signed | Not all devices support background GPU use. |
| Background inference is allowed | Exact preliminary entitlement, model/API route, signed artifact, named device support | The entitlement is not a blanket guarantee for every AI framework. |
| Model/resources are available | Resource membership, load success, revision, memory/thermal fixture | A model file in the project navigator is not runtime readiness. |
| Live Activity projection is configured | Widget extension/attributes/target configuration and system run | A progress callback does not prove the system surface rendered. |

## Lifecycle, progress, and cancellation

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Job starts from a person action | Foreground tap/confirmation log and request submission | App launch, notification delivery, or passive model output is not consent. |
| Job is queued honestly | Queue strategy, not-immediately-available case, queued copy, later run | Queue state is not processing state. |
| Progress is truthful | Real completed units/stages, monotonic updates, pause/stall behavior | A timer or indeterminate spinner is not completion evidence. |
| Person can cancel | In-app and Live Activity cancellation, expiration handler, child-task cancellation, durable state | A visible button without a stop/checkpoint test is not cancellation proof. |
| Expiration is recoverable | Expiration callback, checkpoint, partial output policy, resume/restart path | A task can be terminated abruptly under system conditions. |
| Force-quit is handled | App-switcher close, next-launch reconciliation, no duplicate side effect | No callback may arrive when the person force-quits the app. |
| Completion is real | Output persisted, validated, manifest updated, app re-opened, system projection reconciled | A task callback or progress 100% is not domain completion. |

## AI, media, and sensor work

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| On-device AI continued in background | Exact model/API, entitlement, device support, foreground start, background transition, output | A local model load or foreground inference does not prove background inference. |
| GPU route works | GPU resource check, signed entitlement, representative device, thermal/memory/energy run | Simulator cannot prove physical GPU support or performance. |
| Media export is resumable | Asset fixture, checkpoint, partial output, cancellation, corrupted source, resume | A successful export on one file does not prove batch recovery. |
| AI output is safe to use | Typed output, provenance, source revision, validation, editable review, explicit commit | Generated output remains a proposal until accepted. |
| Sensor analysis is safe | Permission, sampling lifecycle, interruption, background resource, privacy, stale data | Background execution does not make sensor data continuously available. |

## Design and accessibility

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Progress surface is native | HIG review, system Live Activity, titles/subtitles, no private data exposure | A custom glass card is not the system progress interface. |
| Liquid Glass is usable | Light/dark, increased contrast, reduced transparency, Dynamic Type, device sizes, hit regions | Translucent decoration cannot carry the only state signal. |
| Cancellation is accessible | VoiceOver, Voice Control, Switch Control, keyboard/pointer, Dynamic Type, Reduce Motion | A touch-only cancel action is incomplete. |
| Privacy is clear | Source scope, retention, lock-screen/system title, notification, logs/analytics, deletion review | On-device processing is not automatically privacy-safe. |

## Performance, energy, and release

| Claim | Required evidence |
| --- | --- |
| Task is resource-aware | Battery, thermal, memory, GPU/Neural Engine, network, storage, and long-run measurements |
| Checkpoint does not duplicate work | Interrupt at every stage boundary, relaunch, resume, and inspect outputs/side effects |
| Release is configured | Archive entitlements, Info.plist identifiers, Background Modes, GPU/Inference, model resources, extension targets |
| Device coverage is known | Named physical device/OS matrix, resource support, fallback route, unsupported behavior |
| System surface is shipped honestly | Release build shows queued/running/cancelled/completed/interrupted states and deep-links correctly |

## Evidence packet

Record:

~~~text
feature:
target/bundle/build:
sdk/deployment target:
route:
task identifier:
person action:
Info.plist permitted identifier:
background modes:
gpu/inference entitlement:
supported resources:
model/api:
source scope:
checkpoint schema:
progress unit:
queue/fail strategy:
expiration/cancel behavior:
force-quit/relaunch behavior:
system Live Activity:
privacy/title/subtitle review:
accessibility settings:
device/OS/thermal/battery:
known failures:
claim supported:
claim not yet supported:
~~~

## Claim language

Use:

- “The named signed device accepted a foreground-started continued-processing request, reported work-based progress, and resumed from a checkpoint after expiration.”
- “The request was rejected when the target lacked the permitted identifier; the app preserved the source and offered a foreground-only route.”
- “The system Live Activity exposed cancellation; the app treated cancellation as an interrupted job and did not apply the partial AI proposal.”
- “Background GPU/Inference capability is documented and signed for the named target; support remains limited to the tested device/API/model matrix.”

Avoid:

- “Runs in the background” from a foreground debugger run.
- “AI runs on the Neural Engine” from a model load or CPU fallback.
- “The export is complete” from progress 100% before the output is persisted.
- “The user cancelled” without proof of system cancellation handling.
- “Works on iOS 26 devices” without a device/resource/support matrix.

## Sources

- [Background Tasks](https://developer.apple.com/documentation/backgroundtasks)
- [BGTaskScheduler](https://developer.apple.com/documentation/backgroundtasks/bgtaskscheduler)
- [BGTask](https://developer.apple.com/documentation/backgroundtasks/bgtask)
- [BGAppRefreshTaskRequest](https://developer.apple.com/documentation/backgroundtasks/bgapprefreshtaskrequest)
- [BGProcessingTaskRequest](https://developer.apple.com/documentation/backgroundtasks/bgprocessingtaskrequest)
- [BGContinuedProcessingTask](https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtask)
- [BGContinuedProcessingTaskRequest](https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtaskrequest)
- [Performing long-running tasks on iOS and iPadOS](https://developer.apple.com/documentation/backgroundtasks/performing-long-running-tasks-on-ios-and-ipados)
- [BGTaskSchedulerPermittedIdentifiers](https://developer.apple.com/documentation/bundleresources/information-property-list/bgtaskschedulerpermittedidentifiers)
- [BGTaskSchedulerErrorCode.notPermitted](https://developer.apple.com/documentation/backgroundtasks/bgtaskscheduler/error/code/notpermitted)
- [BGContinuedProcessingTaskRequest.Resources](https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtaskrequest/resources)
- [Background GPU Access](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.background-tasks.continued-processing.gpu)
- [Background Inference](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.background-tasks.continued-processing.inference)
- [Configuring background execution modes](https://developer.apple.com/documentation/xcode/configuring-background-execution-modes)
- [ActivityKit](https://developer.apple.com/documentation/activitykit/)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Vision](https://developer.apple.com/documentation/vision)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
