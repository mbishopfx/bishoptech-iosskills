# Core Animation motion proof matrix

This matrix keeps custom layer animation, UIKit property animation, SwiftUI interoperation, display cadence, accessibility, and release evidence distinct. A smooth preview or screenshot is not proof that the feature remains correct after interruption, reduced motion, thermal pressure, or a real device refresh-rate decision.

## Claim-to-evidence matrix

| Claim | Minimum evidence | Stronger evidence | Do not infer |
| --- | --- | --- | --- |
| The selected target links Core Animation/UIKit interop | Named target compile | Small sample target with route tests | That every layer property is owned correctly. |
| Layer state is correct | Unit/state tests for model values and reconciliation | Interrupted/reversed UI tests and device run | That presentation-layer state is canonical. |
| A transition is smooth | UI test and physical-device visual inspection | Frame-time/hitch measurements on supported device tiers | That a screenshot or newest device proves performance. |
| Core Animation completion means success | Test visual completion and separate domain completion | Failure/cancellation tests with independent records | That an animation completion proves save/network/system/model completion. |
| Interactive animation is correct | Gesture UI tests for pause, scrub, reverse, cancel | Slow/fast/interrupted gestures on device | That fill mode hides a wrong model layer. |
| Display-link work is frame-safe | Deterministic time-step tests and cancellation | ProMotion/Low Power/thermal/older device measurements | That preferred frame rate equals actual frame rate. |
| Liquid Glass composition is native | SwiftUI/HIG review and accessibility states | Physical-device appearance and settings test | That a custom CALayer glass clone matches system behavior. |
| Custom visual is accessible | Semantic control/accessibilityRepresentation review | VoiceOver, Switch Control, Voice Control, keyboard, Dynamic Type, reduced effects | That visual contrast alone makes a layer accessible. |
| AI motion parameters are safe | Bounded enum/range tests and fallback fixtures | Device model availability, memory, cancellation, and review tests | That model output can be executed as a layer instruction. |

## Deterministic fixture set

Create a fixture for each visual state:

- initial layout and immediate model reconciliation;
- appear, settle, move, morph, progress, highlight;
- interrupted animation halfway through;
- reversed or canceled interactive gesture;
- replaced source/state while an animation is active;
- Reduce Motion and reduced-transparency modes;
- dim flashing lights and animated-image setting;
- unavailable model or invalid AI motion proposal;
- display-link time steps below, at, and above the target deadline;
- Low Power Mode or simulated lower frame-rate policy;
- memory/thermal fallback;
- reused cell or representable rebuild.

Assertions should inspect domain/UI state separately from rendered appearance. Where a screenshot is needed, pair it with model-layer and semantic-control assertions.

## Layer and transaction tests

Verify:

- setup does not animate from stale layer values;
- every explicit animation ends with the intended model-layer value;
- implicit actions are disabled when a view is reused or reconciled;
- grouped changes complete together when the feature requires it;
- nested transactions do not leak timing into unrelated layers;
- old animations are removed when ownership changes;
- completion cleanup does not delete a new layer added during a rapid state change;
- presentation-layer reads are optional and transient;
- layer delegate ownership remains valid.

Test the same state change twice. An idempotent update should not create extra animations or drift the layer tree.

## UIKit and SwiftUI interoperation

For UIViewRepresentable routes:

- assert makeUIView creates one owner;
- assert updateUIView applies the same state repeatedly without duplication;
- check context transaction and environment settings;
- verify dismantle stops display links, observers, tasks, and animations;
- test view identity changes and parent list reuse;
- check semantic accessibility elements after the custom visual moves;
- test a SwiftUI state update arriving while a UIKit animator is paused.

The representable is an adapter. It should not become a second domain store.

## Display-link and performance proof

On physical devices, record:

- target and actual frame rate;
- frame-time budget and hitch count;
- CPU/GPU or render cost where available;
- memory for contents, masks, and cached paths;
- energy while active and while paused;
- behavior in Low Power Mode and critical thermal state;
- cadence on displays with different maximum refresh rates;
- cancellation and invalidation latency when leaving the screen.

Use targetTimestamp and timestamp for time-based scheduling. Do not assume duration is meaningful before the display link has delivered a callback. Invalidate the link and prove that callbacks stop.

A stable lower frame rate is preferable to a variable route that repeatedly misses its frame budget. If the effect does not need per-frame control, remove the display link and use a higher-level animation or TimelineView route.

## Accessibility proof

Run these tasks:

1. activate the semantic control represented by the layer;
2. observe the state change with VoiceOver;
3. complete the action with Reduce Motion;
4. use large Dynamic Type and localized text;
5. repeat with reduced transparency, increased contrast, and dim flashing lights;
6. interrupt, reverse, or cancel the action;
7. confirm focus and value remain correct.

Check that:

- custom layer visuals do not introduce false accessibility elements;
- an accessibilityRepresentation supplies the correct label, value, and actions;
- progress and success are exposed as state, not only movement;
- a particle or flash fallback is calm and understandable;
- hit testing remains aligned with the semantic control.

## AI and bounded behavior

For model-assisted motion, record:

- input preference/context and privacy status;
- model route/version and availability;
- validated output range;
- accessibility and power-policy decision;
- final deterministic layer configuration;
- user acceptance or opt-out;
- cancellation/memory-pressure fallback.

Test adversarial or out-of-range values. The renderer must reject invalid output and use a known default. Do not log raw model prompts or private source data in animation diagnostics.

## Physical-device and release proof

Use a signed build to verify:

- real display cadence and device settings;
- light/dark/high-contrast/reduced-effects behavior;
- touch, pointer, keyboard, Voice Control, and Switch Control where supported;
- background/foreground and rotation/lifecycle;
- old-device memory and thermal behavior;
- final target membership and bundle identity;
- required frameworks, assets, and privacy metadata;
- absence of debug-only animation bypasses or mock time sources.

The archive proves configuration and signing. It does not prove that every device tier feels the same or that an external system accepted a domain action.

## Related routes

- [Core Animation layers, transactions, timing, and display cadence](../42-framework-deep-dives/56-core-animation-layers-transactions-and-timing.md)
- [Core Animation native motion and Liquid Glass design](../21-design-deep-dives/76-core-animation-native-motion-and-glass-design.md)
- [Core Animation layer and display-link route](../50-capability-recipes/79-core-animation-layer-and-display-link-route.md)
- [Core Animation layer and animation recipes](../70-code-recipes/91-core-animation-layer-and-animation-recipes.md)

## Sources

- [Core Animation](https://developer.apple.com/documentation/quartzcore)
- [CALayer](https://developer.apple.com/documentation/quartzcore/calayer)
- [CATransaction](https://developer.apple.com/documentation/quartzcore/catransaction)
- [CADisplayLink](https://developer.apple.com/documentation/QuartzCore/CADisplayLink?changes=_9)
- [CADisplayLink preferred frame rate range](https://developer.apple.com/documentation/quartzcore/cadisplaylink/preferredframeraterange)
- [CADisplayLink target timestamp](https://developer.apple.com/documentation/quartzcore/cadisplaylink/targettimestamp)
- [UIViewPropertyAnimator](https://developer.apple.com/documentation/uikit/uiviewpropertyanimator)
- [UIViewRepresentableContext](https://developer.apple.com/documentation/swiftui/uiviewrepresentablecontext)
- [accessibilityReduceMotion](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion)
- [accessibilityDimFlashingLights](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilitydimflashinglights)
- [accessibilityRepresentation](https://developer.apple.com/documentation/swiftui/view/accessibilityrepresentation%28representation%3A%29)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Performance testing](https://developer.apple.com/documentation/xctest/performance-tests)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
- [Human Interface Guidelines accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Human Interface Guidelines motion](https://developer.apple.com/design/human-interface-guidelines/motion/)
