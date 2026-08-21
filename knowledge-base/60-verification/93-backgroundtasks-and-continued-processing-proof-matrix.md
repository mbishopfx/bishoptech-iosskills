# BackgroundTasks and continued-processing proof matrix

## Purpose

This matrix proves the difference between a documented background API and a
reliable, user-started, resource-aware operation on a named physical device.

A complete route requires evidence for:

- strategy selection and user intent;
- target capabilities, permitted identifiers, and launch registration;
- scheduled-task deferral and expiration;
- continued-processing foreground start;
- queue/fail submission behavior;
- progress, system cancellation, and process termination;
- checkpoint, partial commit, retry, and idempotence;
- model, GPU, network, media, and sensor resource boundaries;
- widget/ActivityKit projection truth;
- accessibility, privacy, thermal, battery, archive, and release.

## Evidence levels

| Level | Establishes | Does not establish |
| --- | --- | --- |
| Source | Apple documents an API or behavior | Selected SDK signature or runtime support |
| Compile | Target and symbols resolve | Scheduling, entitlement approval, or device resources |
| Fixture/unit | Job state, checkpoint, idempotence, and fallback logic | Actual system launch or task budget |
| Preview/simulator | App UI and representative state | Physical background execution, GPU, push, or thermal behavior |
| Signed physical device | Real target, process, system progress, cancellation, and device state | Every release/account environment |
| Archive/release | Capabilities, entitlements, resources, identifiers, and distribution artifact | User behavior or future scheduling |

Record device, OS build, Xcode/SDK, app version/build, account fixture,
network/power state, locale, accessibility settings, and redacted artifact path.

## Source and configuration gates

| ID | Question | Pass evidence | Boundary |
| --- | --- | --- | --- |
| SRC-01 | Does the selected SDK expose BGAppRefreshTask? | Main target compile and availability branch | Do not infer delivery time |
| SRC-02 | Does it expose BGProcessingTask? | Main target compile and request fixture | Do not infer resource conditions |
| SRC-03 | Does it expose BGContinuedProcessingTask? | Selected SDK target compile and beta/final status recorded | Do not infer physical support |
| SRC-04 | Is the request identifier valid? | Bundle-ID-prefixed stable identifier fixture | Do not infer registration |
| SRC-05 | Are identifiers permitted? | Info.plist/archive inspection | Do not infer handler delivery |
| SRC-06 | Are handlers registered before launch completion? | Launch path test/log | Do not infer extension registration |
| SRC-07 | Is Background GPU Access configured? | Capability/entitlement inspection | Do not infer GPU support |
| SRC-08 | Does the device report GPU resource support? | Physical device supportedResources result | Do not infer workload performance |
| SRC-09 | Is queue or fail strategy intentional? | Product decision and fixture | Do not infer immediate start |
| SRC-10 | Are task title/subtitle localized and lock-safe? | Localization/privacy review | Do not infer system rendering |
| SRC-11 | Are private task simulation calls excluded from release? | Source/archive scan | Do not infer physical scheduling |
| SRC-12 | Are App Groups/resources present? | Signed archive and extension read test | Do not infer authorization |
| SRC-13 | Are model/media dependencies in the target? | Archive/resource inspection | Do not infer model readiness |
| SRC-14 | Is the system-surface projection registered? | Widget/ActivityKit target compile | Do not infer truthful state |

## Strategy-selection tests

| ID | Scenario | Fixture | Expected result | Negative evidence |
| --- | --- | --- | --- | --- |
| STRAT-01 | Short refresh | Small feed fixture | BGAppRefresh route selected | Multi-minute processor |
| STRAT-02 | Deferred maintenance | Database/index fixture | BGProcessing route selected | Exact-time promise |
| STRAT-03 | User-started export | Selected media fixture | BGContinued route selected | Silent app-launch submission |
| STRAT-04 | File transfer | Large upload/download | Background URLSession route selected | Transfer trapped in refresh task |
| STRAT-05 | Finish save | Small pending file write | beginBackgroundTask route selected | Long worker hidden behind grace period |
| STRAT-06 | Irregular server event | Background push fixture | Push/reconcile route selected | Polling loop |
| STRAT-07 | Unsupported continued route | Older/unsupported device | Foreground/deferred fallback | User told it will continue |
| STRAT-08 | Model availability | Model missing | Source-only/deferred fallback | Fabricated AI result |
| STRAT-09 | Hardware resource | GPU unavailable | CPU/foreground/defer policy | GPU claim from request field |
| STRAT-10 | Sensitive workload | Private records | Explicit scope/retention/review | Whole-library silent processing |

## Scheduled task lifecycle tests

| ID | Scenario | Fixture | Expected result | Negative evidence |
| --- | --- | --- | --- | --- |
| SCHED-01 | Registration | Clean launch | All handlers register before launch completes | Registered after event |
| SCHED-02 | Permitted identifiers | Archive Info.plist | Identifier matches allowed list | Typo/omission |
| SCHED-03 | App refresh request | earliest begin hint | Request submits; run time remains system-controlled | Exact-time promise |
| SCHED-04 | Processing request | Deferred maintenance | Request submits with correct capability | Heavy work in refresh |
| SCHED-05 | Replacement | Same identifier submitted twice | Documented replacement behavior respected | Duplicate scheduled jobs |
| SCHED-06 | Delayed launch | Physical device | App remains correct if task is delayed | Empty state treated as failure |
| SCHED-07 | Expiration | Forced/test expiration | Work cancels and calls completion API | Work continues detached |
| SCHED-08 | Reschedule | Recurring refresh | Next request only when product still needs it | Infinite schedule |
| SCHED-09 | Background launch | App terminated/suspended | Handler reconstructs dependencies | UI/window assumed |
| SCHED-10 | Extension schedule | Widget/extension submits | Main app registration still owns launch | Extension registration assumption |
| SCHED-11 | Account change | Sign-out before launch | Job refuses/redacts/cleans up | Old account used |
| SCHED-12 | Storage unavailable | Locked/protected data | Safe retry/defer state | Force unwrap/corrupt write |

## Continued-processing request tests

| ID | Scenario | Fixture | Expected result | Negative evidence |
| --- | --- | --- | --- | --- |
| CONT-01 | Explicit foreground start | Person taps start | Request created only after action | Launch-time submission |
| CONT-02 | Identifier | Bundle ID plus unique job suffix | System identifies the intended job | Shared static identifier |
| CONT-03 | Title/subtitle | Long/RTL/private inputs | Localized safe copy | Filename/prompt leak |
| CONT-04 | Queue strategy | Resource contention | Job queued and visible as queued | Queued called running |
| CONT-05 | Fail strategy | Resource contention | Submission fails and offers retry | Hidden retry loop |
| CONT-06 | Foreground execution | Job begins | Same domain state used before/after background | Separate duplicate worker |
| CONT-07 | Background transition | Person backgrounds app | Task continues where supported | UI process assumed active |
| CONT-08 | Progress | 0/25/50/100 fixture | Progress is meaningful and monotonic by policy | Stuck/no progress |
| CONT-09 | Title update | Phase changes | System copy follows truthful phase | Generated verbose text |
| CONT-10 | User cancel | System cancellation | Expiration/cancel path releases resources | Silent completion |
| CONT-11 | App switcher close | User closes app | Interruption is reconciled on next launch | Guaranteed final callback |
| CONT-12 | System expiration | Resource pressure | Incomplete result is truthful | “Complete” before commit |
| CONT-13 | GPU support | Device supports GPU | Request asks for resource only if entitled | GPU always assumed |
| CONT-14 | GPU unsupported | Device lacks resource | CPU/foreground/defer fallback | Task blocks forever |
| CONT-15 | Thermal pressure | Hot/low-power device | Graceful throttle/checkpoint | Newest-device promise |
| CONT-16 | Multiple jobs | Two user requests | Policy prevents unsafe concurrency | Shared state races |
| CONT-17 | Account sign-out | Sign-out during run | Job cancels/redacts and removes sensitive output | Cross-account completion |
| CONT-18 | Resource cleanup | Media/model/temp files | Cleanup executes on cancel/expire | Temp files remain |
| CONT-19 | Finalization | Export/index plus projection | Success only after final commit | Early success |
| CONT-20 | Relaunch | App starts after interruption | Job state and checkpoint reconcile | Duplicate output |

## Checkpoint and commit tests

| ID | Scenario | Fixture | Expected result | Negative evidence |
| --- | --- | --- | --- | --- |
| CKPT-01 | Unit checkpoint | 3 of 10 completed | Checkpoint reflects committed prefix | Count advances before write |
| CKPT-02 | Resume | Restart at unit 4 | Unit 1-3 not repeated | Duplicate records |
| CKPT-03 | Source revision | Input changes | Proposal rejected/reviewed | Old output applied to new source |
| CKPT-04 | Result hash | Same unit retried | Idempotent output | Duplicate file/record |
| CKPT-05 | Atomic output | Write interrupted | No partial final artifact | Corrupt output marked final |
| CKPT-06 | Partial commit | Cancel after prefix | UI reports saved prefix | All-or-nothing claim |
| CKPT-07 | All-or-nothing export | Temporary file | Final file appears only after finalize | Partial file exposed |
| CKPT-08 | Conflict | Record edited elsewhere | Review/merge route | Silent overwrite |
| CKPT-09 | Retry | Expired job | Resume or restart policy explicit | Automatic duplicate work |
| CKPT-10 | Retention | Cancel/sign-out | Temporary/source/output cleanup matches policy | Sensitive data retained |
| CKPT-11 | Error category | Disk/model/network failure | Localized actionable error | Raw internal diagnostic |
| CKPT-12 | Projection revision | Commit result | Widget/activity/index projection matches commit | Surface leads domain |

## AI and resource tests

| ID | Scenario | Fixture | Expected result | Negative evidence |
| --- | --- | --- | --- | --- |
| AI-BG-01 | Model available | Supported device/model | Typed inference starts | Availability assumed |
| AI-BG-02 | Model unavailable | Unsupported language/device | Fallback/defer state | Fabricated output |
| AI-BG-03 | Input scope | User-selected IDs | Only selected inputs processed | Whole library scanned |
| AI-BG-04 | Privacy | Private source | Lock-safe title/log/projection | Prompt or title leak |
| AI-BG-05 | Progress phase | Import/prepare/analyze/save | Human-readable phases | Token count as completion |
| AI-BG-06 | Cancellation | Model request canceled | Child work stops/resources released | Detached model continues |
| AI-BG-07 | Partial proposals | 4 accepted/6 pending | Review state truthful | All approved |
| AI-BG-08 | Side effect | Message/delete/purchase proposal | Main-app review/confirmation | System task silently commits |
| AI-BG-09 | Evaluation | Known fixture set | Quality/fallback metrics recorded | One sample |
| AI-BG-10 | Memory/thermal | Representative devices | Batch adapts/defer policy | Simulator only |
| AI-BG-11 | GPU entitlement | Entitled supported device | Resource path measured | Entitlement treated as performance |
| AI-BG-12 | Resource cleanup | Model/audio/file route | Handles expiration/sign-out | Locks remain |
| AI-BG-13 | Projection | Committed result | Widget/activity shows commit revision | AI proposal shown as truth |
| AI-BG-14 | Localization | Long/RTL summary | Bounded readable/spoken copy | English-only |

## System-surface tests

| ID | Scenario | Fixture | Expected result | Negative evidence |
| --- | --- | --- | --- | --- |
| SURF-01 | System progress | Continued task backgrounded | Title/progress describes real job | Custom progress detached |
| SURF-02 | Cancel from system surface | Person cancels | Job becomes canceled/partial | Worker continues |
| SURF-03 | Widget while queued | Deferred job | Queued/stale state is honest | “Running” |
| SURF-04 | Activity while running | Product event | Activity state shares job revision | Competing clocks |
| SURF-05 | Completion handoff | Commit finished | Widget/activity refreshes after commit | Surface leads domain |
| SURF-06 | Error handoff | Model/network failure | Repair path and redacted reason | Raw error |
| SURF-07 | Lock state | Device locked | No sensitive title/output | Bystander leak |
| SURF-08 | Accessibility | VoiceOver/Dynamic Type | Phase/count/cancel understandable | Percentage-only |
| SURF-09 | Cold launch | Tap surface/deep link | App reconstructs current job | Route index stale |
| SURF-10 | Duplicate surface | System task plus ActivityKit | One coherent state story | Two contradictory progress bars |

## Physical, accessibility, performance, and release gates

| ID | Scenario | Pass evidence | Boundary |
| --- | --- | --- | --- |
| DEV-01 | Physical scheduled task | Signed device run and logs | Simulator timing |
| DEV-02 | Physical continued task | Foreground start then background | Preview |
| DEV-03 | Power state | Battery/charging fixtures | One power state |
| DEV-04 | Network | Offline/poor/recovered fixtures | Wi-Fi happy path |
| DEV-05 | Thermal | Representative device run | Newest device |
| DEV-06 | Storage | Low-space fixture | Full storage |
| DEV-07 | VoiceOver | Task/repair/cancel/readout | Visual screenshot |
| DEV-08 | Dynamic Type | Large content sizes | Default size |
| DEV-09 | Contrast/transparency | Accessibility settings | Default appearance |
| DEV-10 | Localization | Long/RTL/plural/date/unit | English-only |
| DEV-11 | Memory/performance | Metrics and signposts | Debugger only |
| DEV-12 | Archive | Capabilities, Info.plist, resources | Local target compile |
| DEV-13 | Release | Signed/TestFlight route | Debug private task tools |
| DEV-14 | Privacy | Redacted logs/artifacts | Raw production data |
| DEV-15 | No simulation calls | Source/archive scan | Development helper shipped |

## Evidence record template

~~~yaml
test_id: CONT-13
feature: user-started local AI continued processing
app_version: 0.1.0
build: 43
sdk: Xcode-selected iOS SDK
device:
  model: physical-device-model
  os: iOS build
power: battery-or-charging
network: Wi-Fi-or-offline
accessibility:
  voice_over: false
  dynamic_type: default
  reduce_motion: false
  reduce_transparency: false
job:
  id: synthetic-job
  input_revision: fixture-revision
  source_count: 40
  checkpoint_before: 12
  checkpoint_after: 40
  model_identifier: local-model-version
resources:
  gpu_supported: true
  gpu_entitled: true
  resource_requested: gpu
result: pass
observed_state: completed
cancellation_tested: true
artifact: redacted-artifact-path
known_limits:
  - scheduling timing remains system-controlled
~~~

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
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Core ML](https://developer.apple.com/documentation/coreml/)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit/)
- [ActivityKit](https://developer.apple.com/documentation/activitykit/)
- [Testing](https://developer.apple.com/documentation/testing)
- [XCTest](https://developer.apple.com/documentation/xctest)
- [UI testing](https://developer.apple.com/documentation/xcuiautomation)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
- [Accessibility](https://developer.apple.com/accessibility/)
