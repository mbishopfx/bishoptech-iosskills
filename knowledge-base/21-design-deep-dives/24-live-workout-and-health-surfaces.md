# Live workout and health surfaces

This design route is for a live workout product that feels native on iPhone, iPad, Apple Watch, the Lock Screen, and Live Activities. The visual target is calm, legible, and state-forward. Health data needs more than visual polish: a person must know what is current, what is paused, what is estimated, and what will be saved.

The design loop is:

    activity and goal
        -> target device and system surface
        -> primary metric hierarchy
        -> explicit runtime state
        -> semantic controls
        -> privacy and accessibility
        -> physical-device proof

## Design the job before the material

The central question is not “How much Liquid Glass can this screen hold?” It is “What must the person understand or do in the next two seconds?”

For an active workout, the hierarchy is usually:

1. Is the workout running, paused, interrupted, preparing, saving, or finished?
2. What activity is being tracked?
3. What is the one primary metric for this moment?
4. How much time or distance has elapsed, and what is the goal?
5. What can the person do now: pause, resume, mark a lap, change a segment, or end?
6. Is the data fresh, unavailable, estimated, or from a different device?

Do not let a decorative animation, a glass pill, or an AI sentence outrank the action or metric that keeps the person safe and oriented.

## Three screens, three jobs

### Planned workout editor

The editor is a decision surface. It should show:

- activity and location;
- warmup, interval, recovery, and cooldown structure;
- goals and alerts with units;
- target and device assumptions;
- validation messages before preview or schedule;
- a clear review-and-confirm step for generated proposals.

Use rows, forms, pickers, and disclosure rather than a dense visual timeline that hides values. If the workout is generated from natural language, show the original request next to the structured proposal. The person should be able to change every material assumption before the plan reaches WorkoutKit.

### Live workout monitor

The live screen is a monitoring and control surface, not an editor:

- a persistent activity and state label;
- one large primary metric with its unit;
- elapsed time or segment progress;
- a compact secondary metric group;
- a clear pause/resume control;
- a visually separated end action;
- freshness, sensor, connection, or permission status when relevant.

The primary metric should not jump position when a secondary metric appears. Prefer stable layout slots and graceful empty states. Keep the app-owned projection small enough to reuse in a watch face, Live Activity, or Lock Screen surface.

### Post-workout summary

The summary is a record review surface. Distinguish:

- values saved to HealthKit;
- values calculated by the app;
- notes or events entered by the person;
- labels or explanations proposed by an on-device model;
- missing or unavailable measurements.

Use source and timestamp language when a value is not obvious. “Heart rate unavailable for 04:12–05:03” is more honest than a smoothed line that appears continuous.

## A native component map

| Need | Prefer | Design note |
| --- | --- | --- |
| Primary action | Button with a semantic label and system role | Make pause/resume easy to find and test with VoiceOver |
| End action | Separate destructive or clearly final action | Confirm only when the cost of an accidental end warrants it |
| Activity choice | Picker, navigation destination, or menu | Show the activity name and location, not only an icon |
| Goal and alert | Form rows with units | Keep measurement and unit together |
| Progress | ProgressView or a semantic custom view | Include an accessible value and a non-color state |
| Secondary metrics | Stable grid or compact list | Avoid tiny labels that fail on watchOS or Dynamic Type |
| Sensor freshness | Text plus icon/state, not color alone | “Updated 8 seconds ago” can be more useful than a dot |
| Live projection | ActivityKit content state and compact layout | Do not put the complete workout engine in the widget extension |
| Generated proposal | Review card with source and validation | Keep Apply behind explicit review |
| Failure recovery | Inline status and one clear next action | Preserve the last known timestamp and explain what is missing |

Use semantic SwiftUI controls and platform adaptation first. A custom button that merely looks like a native control must still provide the same focus, accessibility, keyboard, pointer, and reduced-effects behavior.

## State is part of the visual system

The view should be designed for the full state set, not only the happy path:

| State | Visual treatment | Required copy/action |
| --- | --- | --- |
| Not authorized | Calm explanation, no fake metric | Explain why access is needed; open settings or continue without live data |
| Preparing | Progress and disabled duplicate starts | Say what is being prepared; allow cancellation where supported |
| Running | Strong primary metric and active controls | Make it obvious that data is being collected |
| Paused | Persistent paused label and deliberate contrast | Offer Resume and End; do not show a moving timer as if active |
| Interrupted | Banner or prominent status region | Explain whether the session can resume and what data may be missing |
| Stale | Metric remains labeled with age or unavailable state | Do not interpolate a fresh value from an old sample |
| Sensor unavailable | Per-metric unavailable state | Keep the workout usable if the missing sensor is nonessential |
| Low power or thermal pressure | Reduced animation and lower update rate | Preserve the control path and disclose degraded detail if meaningful |
| Saving | Non-dismissible progress state unless safe | Prevent duplicate finish; do not call the result saved yet |
| Saved | Summary with provenance | Show what was saved and what was app-only |
| Discarded | Clear non-save result | Make it clear the HealthKit workout was not created |
| Failed | Human-readable error and recovery | Preserve technical details for logs, not as the only user copy |

The state model should drive styling, animation, controls, and system projections. Do not make every state a different color theme; the state label and semantics should remain understandable in grayscale and with color filters.

## Liquid Glass restraint

Liquid Glass is useful for functional grouping when it does not compete with the workout content. A good live-workout composition often has:

- a normal content region for the primary metric and chart;
- a glass container around pause/resume and secondary actions;
- a separate alert or status region that remains legible when transparency is reduced;
- a compact bottom or edge projection for a Live Activity.

Avoid:

- glass behind a small heart-rate value that already has poor contrast;
- floating controls that move when content changes;
- nested blur layers that make the activity state hard to read outdoors;
- a translucent end button beside a non-destructive control without clear separation;
- animated glass as the only indication that a segment changed;
- simulated “Apple replica” chrome that ignores the current platform’s automatic treatment.

Use the current [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass) guidance and [Human Interface Guidelines design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles) to decide whether a glass treatment clarifies hierarchy. When in doubt, reduce material and improve content contrast.

## Device-specific composition

### Apple Watch

The watch is glance-first and movement-constrained. Prioritize:

- one primary metric;
- a large state label;
- a high-confidence pause/resume path;
- an end path that cannot be triggered accidentally;
- haptic or audio feedback only when it adds clear value;
- large tap targets and strong contrast;
- minimal text entry and no unnecessary model work during the active session.

Do not shrink an iPhone layout onto the watch. Make the watch route a product surface with its own layout, timeout, interruption, and save feedback.

### iPhone

The iPhone can show more metrics and a fuller interaction model. The screen can include segment detail, history, route, and richer controls, but the active state should remain apparent when the phone is locked or the app is backgrounded.

Apple’s current [HealthKit iPhone and iPad workout sample](https://developer.apple.com/documentation/healthkit/building-a-workout-app-for-iphone-and-ipad) demonstrates an iOS-started workout with Lock Screen App Intent controls and Live Activity status. Treat those surfaces as first-class designs, not as a late widget export.

### iPad

Use the larger canvas for a two-column or inspector composition only when it improves decision quality. Keep the primary metric and active controls in the main reading order. A sidebar can hold plan detail, history, or data provenance, but it must not hide the pause/end path.

### Lock Screen and Live Activity

The system surface should answer:

- what activity is active;
- whether it is running or paused;
- the primary metric and unit;
- how long it has been active;
- what safe action is available;
- whether the projection is stale.

The extension does not own the session. It sends a command to an authoritative coordinator or App Intent, handles errors, and refreshes the projection after the command result. If the app process is not available, define the behavior rather than assuming the command completes.

## Accessibility and environmental conditions

Design for:

- Dynamic Type and text expansion;
- VoiceOver labels, values, hints, and actions;
- Voice Control command names;
- Switch Control and keyboard navigation where supported;
- high contrast and color filters;
- reduced motion and reduced transparency;
- bright outdoor light, gloves, sweat, and movement;
- interrupted connectivity or a lowered wrist.

Every metric needs a semantic label, value, unit, and freshness policy. A chart should have an accessible summary and exact-value path. A heart-rate warning should be announced without relying on a color change or an animated glow. If haptic feedback is used, pair it with visible or spoken state.

Use the [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals), [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize), [AccessibilityFocusState](https://developer.apple.com/documentation/swiftui/accessibilityfocusstate), and the [Health and fitness HIG](https://developer.apple.com/design/human-interface-guidelines/workouts) as the starting source set.

## Privacy-forward copy

Prefer:

- “Live workout data is collected with HealthKit permission.”
- “No heart-rate sample is available yet.”
- “Last updated 18 seconds ago.”
- “This summary is generated from the values you selected.”
- “Save workout to HealthKit.”
- “Discard this workout without saving.”

Avoid:

- “Your heart is healthy.”
- “This plan is safe for you.”
- “You burned exactly 500 calories.”
- “AI knows your recovery.”
- “No data means zero.”

The UI should not expose more health data on a locked surface than the person expects. Include a privacy review for every metric placed in a Live Activity, notification, Siri/App Intent response, or shared device projection.

## AI proposal review shell

If the app generates an interval plan or a post-workout explanation, keep the review shell visibly different from the recorded session:

    proposal
        -> source request
        -> assumptions
        -> validation messages
        -> editable fields
        -> explicit approve
        -> WorkoutKit plan or app-owned note

Show uncertainty and missing inputs. Keep the Apply action disabled when the proposal is structurally invalid. A polished glass card must not make an unvalidated proposal feel like a system-certified workout.

## Preview and proof plan

Previews can prove layout and some state rendering. They cannot prove HealthKit authorization, sensor data, Apple Watch background execution, Live Activity invocation, or save semantics.

Build a deterministic fixture set for:

- running with fresh metrics;
- paused with unchanged metrics;
- missing heart rate;
- stale distance;
- interrupted session;
- end confirmation;
- saving;
- saved with partial data;
- discarded;
- authorization denied;
- generated proposal with an invalid alert;
- Dynamic Type and VoiceOver labels.

Then run the [live-workout proof matrix](../60-verification/21-workoutkit-and-live-workout-proof-matrix.md) on physical Apple Watch and iPhone/iPad hardware. Capture the build, target, OS, permissions, device, and exact action sequence with each result.

## Sources

- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles)
- [Health and fitness](https://developer.apple.com/design/human-interface-guidelines/workouts)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [AccessibilityFocusState](https://developer.apple.com/documentation/swiftui/accessibilityfocusstate)
- [WorkoutKit](https://developer.apple.com/documentation/workoutkit)
- [HealthKit](https://developer.apple.com/documentation/healthkit)
- [Running workout sessions](https://developer.apple.com/documentation/healthkit/running-workout-sessions)
- [Building a workout app for iPhone and iPad](https://developer.apple.com/documentation/healthkit/building-a-workout-app-for-iphone-and-ipad)
- [Displaying live data with Live Activities](https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities)
- [Adding interactivity to widgets and Live Activities](https://developer.apple.com/documentation/widgetkit/adding-interactivity-to-widgets-and-live-activities)
