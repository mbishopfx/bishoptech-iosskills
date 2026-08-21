# WorkoutKit and live-workout proof matrix

This matrix separates what documentation, source, a compile, a preview, a simulator, a signed device build, a system surface, and a release environment can actually prove. Mark each row with an artifact, date, target, SDK, OS, device, permission state, and exact action sequence.

## Evidence levels

| Level | Can prove | Cannot prove by itself |
| --- | --- | --- |
| Official documentation | The documented API shape, conceptual lifecycle, and stated system boundary | The project’s target membership, current signature in the selected SDK, hardware behavior, or product quality |
| Source review | The intended state model, permission gate, validation, and fallback logic exist in the repository | Compilation, entitlement correctness, sensor delivery, or system invocation |
| Compile and unit test | Types, conditional compilation, pure validation, serialization fixtures, and deterministic transitions | HealthKit permission, Apple Watch sensors, system schedule, Live Activity delivery, or physical ergonomics |
| Preview and UI test | Layout states, semantics, button paths, and fixture-driven projections | Real health data, locked-device privacy, target entitlements, thermal/battery behavior, or saved HealthKit records |
| Simulator | Some platform layout, lifecycle, and extension wiring | Apple Watch sensor behavior, true HealthKit data, physical haptics, workout background behavior, or all device-only APIs |
| Signed physical device | Target provisioning, entitlements, real input, permissions, and selected hardware path | Every device family, App Store review, production account/server behavior, or long-run thermal results |
| System-surface run | Lock Screen/App Intent/Live Activity/Workout handoff on the tested target | Other OS versions, device families, process/termination cases not exercised, or production delivery |
| TestFlight/App Store/production | Distribution and the specific environment observed | Universal support, future OS behavior, or claims outside the tested artifact and scope |

## Plan and scheduling matrix

| Capability | Minimum proof | Failure cases to exercise | Claim boundary |
| --- | --- | --- | --- |
| WorkoutKit module and target availability | Build the named target with the selected SDK | Unsupported target, conditional compilation, older deployment target | API is present in this target, not every Apple platform |
| CustomWorkout activity support | Unit test plus physical preview or open on the supported device | Unsupported activity, indoor/outdoor mismatch | Support query accepted the activity; it does not validate a person’s fitness |
| Workout goal support | Deterministic validation fixture and selected-device run | Invalid units, unsupported goal, zero/negative values | Goal is structurally supported, not achieved |
| Workout alert support | Validation fixture and visible preview or Workout run | Unsupported alert, conflicting activity/location | Alert can be represented, not that a sensor will always produce it |
| Interval sequence | Serialization fixture, preview, and target run | Missing warmup/cooldown, repeat boundary, changed plan | Sequence is encoded as intended |
| WorkoutPlan identity | Round-trip data fixture and stable-ID inspection | Duplicate IDs, corrupted data, migration | App can identify its plan; system acceptance remains separate |
| openInWorkoutApp | Signed physical Apple Watch run | Watch unavailable, user cancels, app not installed, stale plan | Handoff was attempted and result observed on this device |
| dataRepresentation | Round-trip or compatibility test | Corrupt data, SDK migration, unsupported plan type | Data transported or persisted successfully |
| WorkoutScheduler.isSupported | Device/target test and logged result | Unsupported OS/device, unavailable scheduler | Scheduler support was observed on this configuration |
| Scheduler authorization | Permission-flow device run | Denied, restricted, previously decided, settings change | Authorization result for requested scheduling route |
| Schedule submission | Physical Apple Watch/Workout observation and local reconciliation | System limit, date conflict, external removal, app termination | A schedule was observed, not merely requested |
| scheduledWorkouts reconciliation | Foreground/relaunch test with an external Workout-app change | Removed, completed, changed, duplicate, unknown ID | Local state reflects the observed system list at a timestamp |
| Mark complete/remove | Device run plus re-read | Repeated command, missing plan, process termination | Command result for the tested record |

## HealthKit authorization and runtime matrix

| Capability | Minimum proof | Failure cases to exercise | Claim boundary |
| --- | --- | --- | --- |
| HealthKit capability and target membership | Inspect project target and signed entitlements | Capability on wrong target, extension mismatch, missing usage text | The tested target is configured to request HealthKit |
| Health usage descriptions | Source, built Info, and permission screen review | Missing key, misleading text, extension-specific key | Copy and bundle configuration exist; user can still deny |
| Share workout authorization | Physical device permission run | Denied, restricted, changed in Settings | App can attempt the requested write path |
| Read metric authorization | Per-type permission run | Denied type, no samples, stale history | App handles unavailable data; it does not infer zero |
| HKWorkoutConfiguration | Unit/configuration fixture and target compile | Invalid activity/location combination | Configuration encodes the selected route |
| HKWorkoutSession creation | Signed physical device start attempt | Invalid configuration, no permission, concurrent session, OS/device restriction | Session creation behavior on the tested target |
| HKLiveWorkoutBuilder association | Runtime inspection and delegate setup | Missing association, wrong configuration, lifecycle error | Builder is connected for this session |
| HKLiveWorkoutDataSource | Physical session with expected types | Unsupported sensor, missing metric, route/location mismatch | Automatic data source behavior for this device/activity |
| Session start | Physical device action sequence | Duplicate start, interruption at start, background transition | Session reached an observed started state |
| Builder begin collection | Delegate/completion log with timestamp | Start error, callback delay, process termination | Collection began or failed with recorded evidence |
| Live sample projection | Physical sensor run plus normalized snapshot log | No sample, stale sample, unit conversion, callback ordering | Display reflects observed samples and freshness policy |
| Workout event projection | Physical event plus delegate log | Duplicate event, out-of-order event, missing event | Event handling for the tested event path |
| Pause | Physical device action and state transition | Tap during saving, repeated pause, system interruption | Session reported the observed paused state |
| Resume | Physical device action and state transition | Resume unavailable, sensor missing, repeated resume | Session reported the observed running state |
| Stop | Physical device action and stopped transition | Stop twice, app background, interruption | Stop request was accepted or failed as observed |
| endCollection | Runtime completion evidence | Wrong date, call before stopped, repeated call | Builder ended collection on the tested route |
| finishWorkout | Returned HKWorkout and HealthKit inspection | Finish error, no workout, duplicate finish, partial data | A workout was saved for this test, not that every metric exists |
| discardWorkout | HealthKit inspection and app record | Discard after stopped, repeated discard, stale UI | The builder was discarded without claiming a save |
| session.end | Final state and process logs | End before finish, termination, recovery | Session ended after the selected finalize path |

## Device, system, privacy, and design matrix

| Capability | Minimum proof | Failure cases to exercise | Claim boundary |
| --- | --- | --- | --- |
| watchOS Workout processing background | Physical Apple Watch while wrist lowers and another app is used | Suspension, excessive CPU, battery pressure, low power | Background behavior on the tested watch/OS/configuration |
| iPhone/iPad live route | Physical iPhone/iPad start, background, lock, and resume | Process termination, no network, locked device | The iOS/iPadOS route observed on selected hardware |
| Multidevice mirroring | Two-device run with command owner and sequence IDs | Reachability loss, stale message, duplicate command, owner switch | Projection and command contract for the tested pair |
| Lock Screen App Intent | Locked physical device invocation and post-command projection | Auth required, app process unavailable, duplicate tap, stale state | System invocation and result on this device |
| Live Activity | Start/update/end on signed device with extension target | Delayed update, stale state, relaunch, compact/expanded layouts | Activity projection for the tested route |
| Locked-surface privacy | Review every metric and generated string on the Lock Screen | Sensitive value leakage, shared device, redaction | Selected privacy policy was observed, not universal privacy |
| Liquid Glass fallback | Reduce transparency/motion and high contrast on physical device | Low contrast, moving control, loss of state | The tested composition remains usable with selected settings |
| VoiceOver and Switch Control | Task-based physical-device session | Wrong order, unlabeled metric, action unavailable, announcement race | Tested tasks and settings pass; not a universal accessibility claim |
| Dynamic Type | Largest supported text sizes on iPhone/iPad and watch where applicable | Clipping, hidden end action, chart unreadable | Tested sizes and surfaces remain usable |
| Outdoor/glove interaction | Physical movement and representative environment | Missed tap, accidental end, glare, haptic confusion | Ergonomics observed for the test protocol |
| Battery and thermal behavior | Release configuration run with duration/workload recorded | High CPU, excess logging, model run, display/thermal pressure | Measurements for the device, workload, and build |
| Privacy and diagnostics | Review logs, analytics, crash payloads, model inputs, retention | Raw health data leakage, identifiers in logs, unintended network | Audited artifacts and observed traffic for this build |

## AI proposal and trust matrix

| AI boundary | Minimum proof | Failure cases to exercise | Claim boundary |
| --- | --- | --- | --- |
| Availability gate | Device/OS/model availability fixture | Model unavailable, asset loading, cancellation | Fallback path works; no model quality claim |
| Typed workout proposal | Parser/schema tests and invalid fixture set | Missing field, unsupported activity, contradictory goal | Proposal is structurally typed, not safe or medically appropriate |
| WorkoutKit validation | Support-query tests and device validation | Unsupported goal/alert, schedule limit | Proposal can become a valid plan after deterministic checks |
| Human review | UI test and physical review action | Apply disabled, edit after generation, stale proposal | User explicitly approved this version |
| Health-data minimization | Prompt/input audit and logging review | Raw samples included, location leak, model output retained | Selected input scope is documented and observed |
| Generated explanation | Fixture with missing/stale values and provenance | Hallucinated metric, diagnosis language, certainty | Informational text is labeled and reviewable |
| AI command boundary | Code review plus UI/system command tests | Model attempts pause/end/save, command replay | Only deterministic App Intent/coordinator commands can cause side effects |

## Required evidence packet

For each route, save:

- project and target name;
- SDK and deployment target;
- build configuration and commit;
- device model, OS, watch pairing, and battery state;
- entitlements and usage descriptions;
- HealthKit authorization state by type;
- WorkoutKit plan identifier and serialized fixture;
- session start/stop/save/discard timestamps;
- sample/event freshness and units;
- Live Activity/App Intent action sequence;
- accessibility settings;
- logs with sensitive values redacted;
- screenshots or screen recording where appropriate;
- known limitations and untested surfaces.

The packet should make it possible for another developer to tell the difference between “the code path exists,” “the device returned a sample,” “the system surface responded,” and “the record was saved.”

## Related routes

- [WorkoutKit and HealthKit live workouts](../42-framework-deep-dives/12-workoutkit-healthkit-live-workouts.md)
- [Live workout and health surfaces](../21-design-deep-dives/24-live-workout-and-health-surfaces.md)
- [WorkoutKit + HealthKit live-workout route](../50-capability-recipes/27-workoutkit-healthkit-live-route.md)
- [Build, device, and release checklist](01-build-device-and-release-checklist.md)
- [Physical-device capability proof matrix](07-physical-device-capability-proof-matrix.md)

## Sources

- [WorkoutKit](https://developer.apple.com/documentation/workoutkit)
- [WorkoutPlan](https://developer.apple.com/documentation/workoutkit/workoutplan)
- [WorkoutScheduler](https://developer.apple.com/documentation/workoutkit/workoutscheduler)
- [ScheduledWorkoutPlan](https://developer.apple.com/documentation/workoutkit/scheduledworkoutplan)
- [HealthKit](https://developer.apple.com/documentation/healthkit)
- [Requesting authorization to access health data](https://developer.apple.com/documentation/HealthKit/authorizing-access-to-health-data)
- [Protecting user privacy](https://developer.apple.com/documentation/healthkit/protecting-user-privacy)
- [Running workout sessions](https://developer.apple.com/documentation/healthkit/running-workout-sessions)
- [HKWorkoutSession](https://developer.apple.com/documentation/healthkit/hkworkoutsession)
- [HKWorkoutConfiguration](https://developer.apple.com/documentation/healthkit/hkworkoutconfiguration)
- [HKWorkoutSessionState](https://developer.apple.com/documentation/healthkit/hkworkoutsessionstate)
- [HKLiveWorkoutBuilder](https://developer.apple.com/documentation/healthkit/hkliveworkoutbuilder)
- [HKLiveWorkoutBuilderDelegate](https://developer.apple.com/documentation/healthkit/hkliveworkoutbuilderdelegate)
- [HKLiveWorkoutDataSource](https://developer.apple.com/documentation/healthkit/hkliveworkoutdatasource)
- [HKWorkoutBuilder](https://developer.apple.com/documentation/healthkit/hkworkoutbuilder)
- [Building a workout app for iPhone and iPad](https://developer.apple.com/documentation/healthkit/building-a-workout-app-for-iphone-and-ipad)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [Displaying live data with Live Activities](https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities)
- [Adding interactivity to widgets and Live Activities](https://developer.apple.com/documentation/widgetkit/adding-interactivity-to-widgets-and-live-activities)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
