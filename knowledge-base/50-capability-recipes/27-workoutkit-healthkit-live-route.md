# WorkoutKit + HealthKit live-workout route

Use this recipe when the product idea involves a planned workout, Apple Watch scheduling, live sensor data, a workout summary, or a lock-screen control path. Start with one route and add the other only when the user outcome requires both.

## Outcome

Build a private, reviewable workout feature that can:

- accept a structured or plain-language workout request;
- validate it against the current WorkoutKit support surface;
- preview, open, export, or schedule a WorkoutKit plan;
- optionally start a HealthKit live session;
- project current state to SwiftUI, Apple Watch, Lock Screen, or Live Activities;
- finish or discard the live session explicitly;
- keep raw health data, saved HealthKit data, app-owned notes, and AI proposals distinct.

This is a capability route, not a medical product specification. The user’s health, device, clinician, and safety context remains outside the authority of a generated plan.

## Choose the route

| Product need | Start here | Add later only if needed |
| --- | --- | --- |
| Create a structured interval plan for Workout | WorkoutKit CustomWorkout and WorkoutPlan | HealthKit live runtime |
| Put a future plan on Apple Watch | WorkoutKit WorkoutScheduler | HealthKit authorization for live/read data |
| Track a workout inside your own watchOS app | HealthKit HKWorkoutSession and HKLiveWorkoutBuilder | WorkoutKit for plan authoring |
| Start on iPhone and control from the Lock Screen | HealthKit iOS session plus App Intents and ActivityKit | watchOS mirroring |
| Explain a completed workout | HealthKit read/query plus app-owned summary | Foundation Models after data minimization |
| Generate an interval draft | Foundation Models or another local model | WorkoutKit validation and explicit approval |
| Mirror a watch workout to iPhone | One authoritative watch session plus Watch Connectivity projection | App Intents/Live Activity for commands |

Do not use a local countdown or a WorkoutKit schedule row as a substitute for the live HealthKit route.

## Target and capability register

Write this register before implementation:

| Target | Owns | Required review |
| --- | --- | --- |
| iOS app | Plan editor, iOS-owned live session or projection, authorization UI, app persistence | HealthKit capability, usage descriptions, target availability, background/system surface |
| iPadOS app | Plan editor, optional iPad live route, richer review surface | HealthKit support for chosen APIs and privacy on shared/locked surfaces |
| watchOS app | Apple Watch session, sensor UI, workout processing background behavior | HealthKit capability, Workout processing, physical watch testing, battery/thermal |
| Widget extension | Live Activity and widget presentation | ActivityKit/WidgetKit target membership, compact state, stale/relaunch behavior |
| App Intents target or shared module | Lock Screen commands, Siri/system actions, scheduling commands | Intent discovery, authorization, idempotency, process availability, privacy |
| Shared package/module | Domain models, normalized snapshots, validation, fixtures | Sendability, platform conditional code, no HealthKit objects leaking into pure logic |

If the project only needs a plan sent to Workout, do not create a watchOS app. If the project needs a live Apple Watch sensor route, do not assume an iOS-only target will provide the same runtime behavior.

## Data model boundary

Keep these types separate even if they share fields:

1. WorkoutDraft: app-owned editable intent, including user-entered text and selected constraints.
2. WorkoutProposal: generated or imported suggestion with model/version/source and validation status.
3. WorkoutKitPlanRecord: stable identifier, serialized plan data, target, validation result, and schedule intent.
4. ScheduledWorkoutRecord: local request identifier, requested date, last observed system state, and reconciliation timestamp.
5. LiveSessionState: authoritative lifecycle, device owner, start/pause/stop dates, and command version.
6. TelemetrySnapshot: normalized values, units, source, sample time, freshness, and availability.
7. WorkoutProjection: small Sendable state for SwiftUI, Live Activity, or companion transfer.
8. SavedWorkoutRecord: HealthKit object identifier, app-owned notes, user review, and source/provenance.
9. AIExplanation: generated text with input scope, model availability, prompt/version, and user approval.

The generated proposal must never masquerade as a HealthKit sample. A projection must never be the only copy of session truth.

## Route A: compose and schedule with WorkoutKit

### A1. Gather the request

Collect the minimum structured inputs:

- activity and location;
- step sequence;
- durations or goals;
- alerts;
- desired date and time, if scheduling;
- target platform;
- optional display name;
- whether the user wants preview, open-in-Workout, export, or schedule.

If the request came from on-device AI, retain the natural-language request and the structured proposal together for review.

### A2. Validate deterministically

Before creating a plan:

- validate the activity with the current support API;
- validate each goal and alert against activity and location;
- validate measurement units and ranges;
- validate repeat count and step order;
- validate target availability;
- validate the scheduled count and date policy;
- reject incomplete or contradictory values.

The UI should show actionable errors such as “Power alert is not supported for this activity and location.” Do not silently substitute a heart-rate alert or discard a step.

### A3. Create the plan and choose the handoff

Create a WorkoutPlan with a stable identifier. Choose one:

- preview the composition during editing;
- open it in Workout on Apple Watch for immediate use;
- export its data representation for app-owned persistence or sharing;
- create a ScheduledWorkoutPlan and submit it to WorkoutScheduler.

After a system operation, reload and reconcile. “Schedule requested” is not “system schedule observed.”

### A4. Reconcile

On app launch, foreground, schedule screen appearance, and after a system callback or error:

1. Load local scheduled records.
2. Ask WorkoutScheduler for the current scheduled plans.
3. Match by the stable identifier that the current API exposes.
4. Mark local records missing from the system as removed or unknown, not completed.
5. Record observed completion only from the system’s documented state.
6. Show a conflict when the plan changed and the serialized representation no longer matches.

Avoid auto-rescheduling in a loop. A user may remove a plan in the Workout app or reach the system limit.

## Route B: run a live HealthKit session

### B1. Preflight

Before the Start action:

- confirm the target supports the session route;
- confirm the device can run the desired activity;
- check HealthKit availability;
- explain the requested read/share types;
- request authorization in context;
- prepare the app-owned projection;
- prevent two simultaneous starts.

If authorization is unavailable, offer the plan route or a non-sensor timer only when the product can honestly describe what it does not measure.

### B2. Start

Use one HKWorkoutConfiguration for the HKWorkoutSession and HKLiveWorkoutDataSource. Create the associated builder, assign delegates, start activity, and begin collection. Keep start idempotent at the product layer: a repeated tap should observe or return the existing session rather than create a duplicate.

The session coordinator should own:

- session and builder references;
- the last accepted state transition;
- a command serial number;
- an end/finalize gate;
- the normalized projection;
- errors and recovery state.

### B3. Observe

When the builder reports changed types:

1. Ask the builder for statistics for the changed quantity type.
2. Convert the result to an explicit unit.
3. attach source and timestamp;
4. mark freshness;
5. update the normalized snapshot;
6. publish a projection to the view and any system surface.

When the builder reports an event, append a small app-owned event record and update the projection. Keep high-volume raw events out of UI state and analytics by default.

### B4. Pause, resume, interrupt

Map user commands to the current session API and observe the delegate state afterward. Do not change the display to Paused merely because the button was tapped. The authority is the session transition.

When the app is interrupted:

- preserve the last known state and timestamp;
- show whether data is fresh, stale, or unavailable;
- do not invent samples for the gap;
- decide whether the user can resume or should end;
- keep finalization available;
- reconcile the system projection after recovery.

### B5. End, finish, or discard

Stop the session. Wait for the stopped transition. End collection. Then finish and save, or discard, exactly once. Only mark the app-owned record as saved after the finish callback returns a workout and no error.

If the user abandons the screen, the coordinator still owns the session. On process recovery, restore enough metadata to detect an in-flight or orphaned route, then use the current HealthKit API and physical-device behavior to determine whether it can be resumed or must be closed.

## Cross-device command contract

For a watchOS-owned session mirrored to iPhone:

| Command | Owner | Request | Result | Duplicate policy |
| --- | --- | --- | --- | --- |
| Start | Watch or explicitly selected device | session intent and command ID | actual session state | Return current state if already running |
| Pause | Session owner | command ID and expected state | paused/running/error | Ignore or report duplicate |
| Resume | Session owner | command ID and expected state | running/error | Ignore or report duplicate |
| Mark event | Session owner | event type and timestamp | accepted/rejected | Use idempotent event ID |
| End | Session owner | command ID and save policy | stopped/saving/saved/discarded/error | Never save twice |
| Projection | Non-owner | normalized snapshot | freshness and owner metadata | Drop stale sequence |

The non-owner display should expose “last updated” and a connection state when the user could confuse a stale projection with live data.

## Permission and fallback matrix

| Condition | Primary route | Honest fallback |
| --- | --- | --- |
| HealthKit unavailable | Do not start live health route | Show a plan or non-health timer with clear limitations |
| User denies read access | Do not display the metric as zero | Omit it, show unavailable, or continue with permitted metrics |
| User denies share access | Do not claim saved HealthKit workout | Save only an app-owned note if the user agrees |
| Workout scheduling unsupported | Do not show schedule success | Offer open/preview/export if supported |
| Device lacks the sensor | Do not infer a value | Show unavailable and continue with other data |
| Sensor is stale | Do not animate as current | Show age and recovery state |
| App Intent process unavailable | Do not claim command completed | Return an error or show current state on next foreground |
| Live Activity update delayed | Do not modify HealthKit truth | Mark projection stale; refresh after authority responds |
| AI unavailable | Do not block deterministic plan editing | Use structured controls and manual review |
| Model output invalid | Do not coerce silently | Show field-level validation and let the user edit |
| Finish fails | Do not mark saved | Preserve error, allow retry or discard according to current state |

## AI and review route

The safe route for “make me an interval workout” is:

    natural-language request
        -> local typed proposal
        -> support/measurement validation
        -> editable review
        -> explicit approval
        -> WorkoutKit plan
        -> preview/open/schedule

The safe route for “explain my workout” is:

    user-selected saved values
        -> minimize and normalize
        -> local summary proposal
        -> label generated content and missing values
        -> user review
        -> app-owned note or share

Keep diagnosis, treatment, safety certification, and guaranteed outcome claims out of the generated copy. Do not allow the model to issue pause/end/save commands directly. Commands remain deterministic, permission-gated, and reviewable.

## Liquid Glass composition recipe

Use a small native shell:

1. Content layer: primary metric, time, activity, and progress.
2. Functional layer: pause/resume, lap/event, and settings.
3. System layer: Live Activity, Lock Screen, watchOS system presentation, and App Intent.
4. Review layer: proposal or post-workout explanation with source and approval.

Use the system’s native controls and containers where possible. Keep the content layer readable when glass is disabled or reduced. A generated suggestion should be visually recognizable as a proposal, not a system status.

## Build sequence

Implement in this order:

1. Pure domain models and deterministic validation.
2. WorkoutKit plan creation with a local fixture.
3. Preview/open/export and schedule reconciliation.
4. HealthKit authorization and a live session coordinator.
5. SwiftUI active screen with simulated telemetry.
6. Finish/discard and saved-result model.
7. Physical watch or iPhone session.
8. App Intent controls and Live Activity projection.
9. AI proposal generation and review.
10. Accessibility, performance, privacy, thermal, interruption, and release evidence.

Do not add AI, glass, or a second device until the state and proof boundary is stable.

## Acceptance checklist

- [ ] Product chooses plan, live, or both deliberately.
- [ ] Targets and required entitlements are written down.
- [ ] WorkoutKit support queries run before preview or schedule.
- [ ] Schedule reconciliation detects external system changes.
- [ ] HealthKit read/share permissions are contextual and minimized.
- [ ] The session coordinator, not a view, owns live lifecycle.
- [ ] Fresh, stale, unavailable, paused, interrupted, saved, discarded, and failed states are represented.
- [ ] End/finalize/discard is ordered and idempotent.
- [ ] App Intent controls report actual command results.
- [ ] Live Activity is a projection, not a second engine.
- [ ] AI proposals are typed, validated, editable, and explicitly approved.
- [ ] Raw health data is not silently sent to models, analytics, or servers.
- [ ] VoiceOver, Dynamic Type, reduced motion/transparency, contrast, and device ergonomics are tested.
- [ ] Physical Apple Watch and iPhone/iPad evidence is captured for every claimed route.

## Sources

- [WorkoutKit](https://developer.apple.com/documentation/workoutkit)
- [CustomWorkout](https://developer.apple.com/documentation/workoutkit/customworkout)
- [WorkoutPlan](https://developer.apple.com/documentation/workoutkit/workoutplan)
- [ScheduledWorkoutPlan](https://developer.apple.com/documentation/workoutkit/scheduledworkoutplan)
- [WorkoutScheduler](https://developer.apple.com/documentation/workoutkit/workoutscheduler)
- [HealthKit](https://developer.apple.com/documentation/healthkit)
- [Requesting authorization to access health data](https://developer.apple.com/documentation/HealthKit/authorizing-access-to-health-data)
- [Protecting user privacy](https://developer.apple.com/documentation/healthkit/protecting-user-privacy)
- [Running workout sessions](https://developer.apple.com/documentation/healthkit/running-workout-sessions)
- [HKWorkoutSession](https://developer.apple.com/documentation/healthkit/hkworkoutsession)
- [HKWorkoutConfiguration](https://developer.apple.com/documentation/healthkit/hkworkoutconfiguration)
- [HKLiveWorkoutBuilder](https://developer.apple.com/documentation/healthkit/hkliveworkoutbuilder)
- [HKLiveWorkoutDataSource](https://developer.apple.com/documentation/healthkit/hkliveworkoutdatasource)
- [HKWorkoutBuilder](https://developer.apple.com/documentation/healthkit/hkworkoutbuilder)
- [Building a workout app for iPhone and iPad](https://developer.apple.com/documentation/healthkit/building-a-workout-app-for-iphone-and-ipad)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [Displaying live data with Live Activities](https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities)
- [Adding interactivity to widgets and Live Activities](https://developer.apple.com/documentation/widgetkit/adding-interactivity-to-widgets-and-live-activities)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
