# WorkoutKit and HealthKit live workouts

This route covers two related but different products:

1. WorkoutKit composes, previews, exports, and schedules structured workouts for the Workout app on Apple Watch.
2. HealthKit runs a live workout session, receives sensor-backed samples and events, and saves a finished workout to the HealthKit store.

Treat the planned workout, the live runtime, the app’s display projection, and the saved HealthKit record as separate state. A WorkoutKit plan is not proof that a workout started. A live metric is not a medical conclusion. A successful save is not proof that every sensor was available or that a person achieved a goal.

## The capability boundary

| Layer | Apple route | Responsibility | Keep separate from |
| --- | --- | --- | --- |
| Planned composition | WorkoutKit | Describe a custom interval workout, single goal, pacer, or swim-bike-run composition | The runtime session and the person’s actual performance |
| Apple Watch handoff | WorkoutPlan, ScheduledWorkoutPlan, WorkoutScheduler | Preview, open, serialize, or schedule a plan in the Workout app | A local “scheduled” row that has not reconciled with the system |
| Authorization | HealthKit and WorkoutScheduler | Ask for the health data and workout scheduling access that the feature actually needs | A Boolean that implies the user granted every requested type |
| Live session | HKWorkoutSession and HKWorkoutConfiguration | Start, pause, resume, stop, and observe an activity-specific workout session | A SwiftUI view’s local timer |
| Live collection | HKLiveWorkoutDataSource and HKLiveWorkoutBuilder | Receive automatic data, calculate statistics, collect events, and finish or discard the workout | A generated summary or stale last-known value |
| System projection | App Intents, ActivityKit, Lock Screen, watchOS surfaces | Expose safe controls and a compact progress projection | The HealthKit store and the app’s complete detail screen |
| Product domain | App-owned model and persistence | Store intent, plan metadata, review decisions, sync state, and user-facing copy | Raw health samples and generated AI proposals |

Apple’s [WorkoutKit documentation](https://developer.apple.com/documentation/workoutkit) describes models and utilities for creating and previewing workouts and syncing scheduled workouts to the Workout app on Apple Watch. Apple’s [running workout sessions guide](https://developer.apple.com/documentation/healthkit/running-workout-sessions) describes the HealthKit session, live builder, delegate, background, and save lifecycle.

## Route map

Use this as the architecture spine:

    user goal
        -> app-owned workout proposal or editor
        -> validate activity, goals, alerts, target, and availability
        -> WorkoutKit plan
        -> preview, open, export, or schedule
        -> Workout app / Apple Watch

    live-start decision
        -> HealthKit authorization
        -> HKWorkoutConfiguration
        -> HKWorkoutSession
        -> HKLiveWorkoutBuilder
        -> HKLiveWorkoutDataSource
        -> delegate samples and events
        -> app-owned projection for SwiftUI, Lock Screen, or Live Activity
        -> stop
        -> endCollection
        -> finishWorkout or discardWorkout
        -> reconcile saved or discarded result

The first branch is a plan. The second branch is an active session. They may be connected by a user action, but they should not be collapsed into one Boolean such as workoutIsRunning.

## WorkoutKit: planned workout composition

### Choose the narrowest workout type

WorkoutKit documents these common compositions:

- CustomWorkout for a structured series of work and recovery steps.
- SingleGoalWorkout for one distance, energy, or time goal.
- PacerWorkout for a distance and time goal.
- SwimBikeRunWorkout for a multisport composition that transitions between swimming, biking, and running.

Use CustomWorkout when the product is interval-first. Use a simpler type when the product does not need interval blocks. The simpler representation is easier to explain, validate, preview, and recover.

For custom intervals, the important concepts are:

- WorkoutStep for a warmup, cooldown, or standalone step.
- IntervalBlock for repeating work and recovery steps.
- IntervalStep for one work or recovery interval.
- WorkoutGoal for a supported time, distance, energy, or activity-specific goal.
- WorkoutAlert for a supported heart-rate, cadence, power, or speed boundary.

The exact initializer labels and measurement types belong to the selected SDK. Check the current [CustomWorkout API](https://developer.apple.com/documentation/workoutkit/customworkout), [IntervalStep API](https://developer.apple.com/documentation/workoutkit/intervalstep), [WorkoutGoal API](https://developer.apple.com/documentation/workoutkit/workoutgoal), and [WorkoutAlert API](https://developer.apple.com/documentation/workoutkit/workoutalert) in Xcode before copying a recipe.

### Validate before preview or schedule

Use the support queries on CustomWorkout before presenting a final plan:

1. Is the selected activity supported?
2. Is the selected goal supported for that activity and location?
3. Is the selected alert supported for that activity and location?
4. Are the step count, repeat count, durations, and measurements within the current API’s accepted values?
5. Does the target device and OS support the chosen workout type?
6. Is the user’s plan complete enough to preview without silently replacing a value?

When a proposal is invalid, show the field that needs attention. Do not silently downgrade a requested alert or goal to a different one and call the result successful.

### WorkoutPlan is a transport and system handoff boundary

Create a WorkoutPlan with a stable app-owned identifier. The plan can:

- open the workout in Workout on Apple Watch with openInWorkoutApp();
- provide a data representation for export or persistence;
- be reconstructed from data when the current SDK supports that initializer;
- be wrapped in a ScheduledWorkoutPlan for scheduling.

The data representation is a transport artifact. It is useful for caching, sharing, or reconciliation, but it does not mean the plan was accepted by the Workout app or completed by the person.

### Scheduling is a negotiated system state

The WorkoutScheduler route should be modeled as:

    local draft
        -> plan validated
        -> scheduler supported
        -> authorization requested
        -> schedule request submitted
        -> system schedule observed
        -> local row reconciled

The documented scheduler surface includes a shared WorkoutScheduler, support and authorization state, a schedule operation, scheduled-workout inspection, a maximum scheduled count, and operations for marking a scheduled workout complete or removing it. The system can be changed outside the app, so reload scheduled plans when the app becomes active and compare stable identifiers instead of trusting a local write.

Use [WorkoutScheduler](https://developer.apple.com/documentation/workoutkit/workoutscheduler) and [ScheduledWorkoutPlan](https://developer.apple.com/documentation/workoutkit/scheduledworkoutplan) as the source of truth for current names, async behavior, error cases, and availability.

## HealthKit: live workout runtime

### Configure for the actual activity

An HKWorkoutConfiguration describes the activity and location. The configuration influences the sensors and calculations the system uses. An outdoor run and an indoor cycle should not be treated as the same sensor contract.

The session startup boundary is:

1. Request permission to share workout types and read only the health types needed by the feature.
2. Create HKWorkoutConfiguration.
3. Create HKWorkoutSession with the HKHealthStore and configuration.
4. Obtain the associated HKLiveWorkoutBuilder.
5. Assign an HKLiveWorkoutDataSource using the same configuration.
6. Assign session and builder delegates.
7. Start the session and begin collection.
8. Update the app projection from builder callbacks and explicit runtime state.

Apple’s [HKLiveWorkoutBuilder documentation](https://developer.apple.com/documentation/healthkit/hkliveworkoutbuilder) identifies the data source, workout session, delegate, current workout activity, event collection flag, and elapsed time as the core live-builder surfaces.

### Samples are callbacks, not view state

The builder delegate receives notification that data types or events changed. For a changed quantity type, query the builder’s statistics for that type and derive a display value with explicit unit formatting. For events, inspect the builder’s event collection and update the domain event log.

Keep this flow one-way:

    HealthKit callback
        -> session coordinator
        -> normalized telemetry snapshot
        -> app-owned observable projection
        -> SwiftUI view / Live Activity / watchOS view

Do not let a view own the HealthKit session. A view can disappear while the session remains active, and an extension or system surface may need the same projection. Use an actor or another single-owner coordinator to serialize commands and protect lifecycle transitions.

The callback queue and actor boundary must be chosen deliberately. HealthKit delegate callbacks may not arrive on the main actor. Convert them into a small Sendable snapshot before updating SwiftUI state. Do not pass HKQuantity, HKWorkout, or mutable HealthKit objects through a loose task graph without checking the current SDK’s Sendable and isolation annotations.

### Session lifecycle

Use the documented HKWorkoutSession state and delegate transitions as the runtime authority. A product-level model can make the states easier to reason about:

| Product state | Meaning | Allowed next actions |
| --- | --- | --- |
| unavailable | HealthKit, target, device, or configuration cannot support the route | Explain, offer a non-live plan, or retry after capability changes |
| unauthorized | Required access is not granted or the user has not made a decision | Explain the feature-specific need and provide settings guidance |
| preparing | Configuration/session/builder creation is in progress | Cancel if supported; prevent duplicate start |
| running | Session is active and collection is expected | Pause, resume, add event, or end |
| paused | Session remains active but elapsed/runtime semantics change | Resume or end; show paused status |
| interrupted | Session or sensor path was interrupted | Reconcile callbacks; offer resume or end without inventing samples |
| stopping | Session reached stopped or stop was requested | End collection exactly once |
| saving | Builder is ending collection and finishing the workout | Disable duplicate finish; show progress |
| saved | Finish returned an HKWorkout | Display the saved result and provenance |
| discarded | User or product policy discarded the builder | Remove active UI and preserve a non-health record if needed |
| failed | Session, builder, authorization, or persistence failed | Preserve the error and offer a safe recovery |

The model above is app-owned language. Map it to the actual session state and completion callbacks rather than assuming every state is a first-class enum case on every target.

### Ending correctly

Apple’s running-sessions guide describes the critical order:

1. Call stopActivity with a timestamp.
2. Wait for the session to transition to the stopped state.
3. Call endCollection with the end date.
4. Call finishWorkout to create and save the HKWorkout, or discard the builder when the user chooses not to save.
5. End the session and update the product state.

Do not call finish from the tap handler before the state transition. Do not show Saved when finish returned an error or no workout. Do not leave a session running because the user navigated away. [HKWorkoutBuilder](https://developer.apple.com/documentation/healthkit/hkworkoutbuilder) documents the distinction between ending collection, finishing, and discarding.

## Targets, devices, and system surfaces

### Apple Watch route

For watchOS workout sessions, Apple documents the Workout processing background mode. A workout app can continue receiving sensor data while the user lowers their wrist or interacts with another app, subject to system resource limits. If short background audio or haptics are part of the feature, configure the related capability and test the active-session requirement.

The watch UI must make the active session obvious, make stopping easy, and give clear feedback after save or discard. Background execution is not permission to perform unbounded work. Limit CPU, allocations, rendering, logging, and model work during the session.

### iPhone and iPad route

Apple’s current [Building a workout app for iPhone and iPad sample](https://developer.apple.com/documentation/healthkit/building-a-workout-app-for-iphone-and-ipad) demonstrates an iOS-started workout, Lock Screen controls through App Intents, and status presented with Live Activities. It also links the Apple Watch and multidevice routes.

This is a separate architecture choice from mirroring a watch session:

- iPhone/iPad-first: the phone owns the live session and the Lock Screen projection.
- watchOS-first: the watch owns sensors and session lifetime; the phone receives selected state.
- multidevice: one device owns the session while another receives an explicit projection with a defined connection and stale-state policy.

Never make both devices independently authoritative for pause, end, or save. Define command ownership and idempotency.

### Live Activities and Lock Screen

An ActivityKit Live Activity should be a compact projection of the current session, not a second workout engine. Include only values that remain safe and meaningful while the device is locked. Provide clear freshness, activity label, primary metric, elapsed time, and one or two high-value controls.

App Intent controls must be idempotent. A repeated pause command should not create a second transition or corrupt the session. The intent should call the coordinator or a narrowly scoped command service, then publish a new projection after the authoritative result is known.

Use [Displaying live data with Live Activities](https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities) and [Adding interactivity to widgets and Live Activities](https://developer.apple.com/documentation/widgetkit/adding-interactivity-to-widgets-and-live-activities) for current target and extension behavior.

## Authorization, privacy, and health boundaries

Enable the HealthKit capability in the target that owns HealthKit work. Add the required health usage descriptions for read and update access, and request only the types the feature needs. Ask in a meaningful product context, not on first launch before the user knows why.

At minimum, separate these values:

- canUseHealthKit: the framework and target support the route;
- hasRequestedAuthorization: the app has asked;
- canShareWorkout: the app can attempt to save the requested workout type;
- canReadMetric: the app may receive the requested read type;
- hasLiveSession: the session exists;
- hasFreshMetric: a recent value exists;
- isMetricVisible: product policy allows showing it in the current surface.

A denied read type can produce an empty or unavailable result rather than a useful error. Design an honest empty state. Never infer a zero value from missing access, missing sensor data, or a stale callback.

Health data is sensitive. Log identifiers and technical errors, not raw heart-rate histories or location traces. Avoid sending health data to a model, server, analytics provider, or crash payload unless the product has an explicit, reviewed reason and privacy contract. A workout feature is not a diagnosis, treatment, or guarantee of calories, pace, recovery, or health outcome.

Apple’s [Protecting user privacy](https://developer.apple.com/documentation/healthkit/protecting-user-privacy) and [Requesting authorization to access health data](https://developer.apple.com/documentation/HealthKit/authorizing-access-to-health-data) should be read with the current HealthKit entitlement, usage-description, and App Store requirements for the selected target.

## On-device AI route

AI can make the authoring or reflection workflow more useful without becoming the authority for health truth:

1. The user provides a goal, constraints, experience level, or a plain-language request.
2. A local model proposes a structured workout draft or a label for an existing record.
3. Deterministic code validates activity, goal, alert, measurements, scheduling limits, and target support.
4. The UI shows the proposal with the input and validation messages.
5. The person explicitly edits or approves it.
6. Only then does the app create a WorkoutKit plan or write an app-owned record.

Do not ask a model to infer a diagnosis, silently alter a workout because a metric is missing, or promise that a plan is safe for a person. Keep raw HealthKit samples out of prompts by default. If a user intentionally asks for a summary, send the smallest normalized, unit-labeled, time-bounded data and identify it as an informational summary.

For Foundation Models or Core ML integration, keep availability, model load, cancellation, token/compute budgets, and no-model fallback explicit. A generated workout is a proposal until support queries and user review succeed. See the [Foundation Models documentation](https://developer.apple.com/documentation/foundationmodels) and [Apple Intelligence and Siri AI](https://developer.apple.com/documentation/appintents/apple-intelligence-and-siri-ai) for the relevant on-device and system-discovery boundaries.

## Liquid Glass and native design boundaries

Liquid Glass belongs around actions and hierarchy, not between the person and a critical measurement:

- Use system controls for pause, resume, end, and settings whenever they express the interaction correctly.
- Place the primary metric in a high-contrast content region with a stable reading order.
- Use a glass container for secondary controls, progress, or a compact status group when it improves grouping.
- Keep the active workout state visually distinct from a plan-editing state.
- Do not use blur, transparency, animation, or color as the only signal for a heart-rate alert, stale data, pause, or failure.
- Provide a reduced-motion and reduced-transparency fallback.
- Test Dynamic Type, VoiceOver, high contrast, color filters, and outdoor glare on the real device.

The [Human Interface Guidelines for health and fitness](https://developer.apple.com/design/human-interface-guidelines/workouts) and [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass) should govern the final composition. The target is native hierarchy and readable state, not a decorative glass replica.

## Evidence package

For a real app, keep these artifacts together:

1. Source and target register: iOS, iPadOS, watchOS, widget extension, and any App Intent target.
2. Entitlement and privacy record: HealthKit, background modes, usage strings, privacy manifest, and App Store metadata.
3. Plan evidence: a validated WorkoutKit plan, preview/open/export result, and schedule reconciliation.
4. Runtime evidence: authorization, start, live samples, pause/resume, interruption, stale/no-sensor state, stop, finish, discard, and failure.
5. Surface evidence: Lock Screen/App Intent command, Live Activity freshness, watch surface, and process termination recovery.
6. Physical evidence: representative Apple Watch and iPhone/iPad hardware, current OS, release configuration, battery/thermal observations, and assistive settings.
7. Data evidence: exact units, timestamps, source, freshness, user review, and whether the value is raw, aggregated, generated, or saved.

Use the [WorkoutKit and live-workout proof matrix](../60-verification/21-workoutkit-and-live-workout-proof-matrix.md) as the starting checklist and the [compile-oriented recipes](../70-code-recipes/39-workoutkit-healthkit-live-recipes.md) as route sketches only.

## Sources

- [WorkoutKit](https://developer.apple.com/documentation/workoutkit)
- [CustomWorkout](https://developer.apple.com/documentation/workoutkit/customworkout)
- [IntervalStep](https://developer.apple.com/documentation/workoutkit/intervalstep)
- [WorkoutGoal](https://developer.apple.com/documentation/workoutkit/workoutgoal)
- [WorkoutAlert](https://developer.apple.com/documentation/workoutkit/workoutalert)
- [WorkoutPlan](https://developer.apple.com/documentation/workoutkit/workoutplan)
- [ScheduledWorkoutPlan](https://developer.apple.com/documentation/workoutkit/scheduledworkoutplan)
- [WorkoutScheduler](https://developer.apple.com/documentation/workoutkit/workoutscheduler)
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
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Apple Intelligence and Siri AI](https://developer.apple.com/documentation/appintents/apple-intelligence-and-siri-ai)
- [Health and fitness](https://developer.apple.com/design/human-interface-guidelines/workouts)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
