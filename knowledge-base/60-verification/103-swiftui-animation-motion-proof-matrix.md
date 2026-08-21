# SwiftUI animation and motion proof matrix

## Purpose

Use this matrix to prove a SwiftUI motion feature at the level of the claim
being made. It separates source/API correctness, visual behavior, accessible
task completion, semantic feedback, performance, physical hardware, and
release evidence.

Related pages:

- [SwiftUI animation, motion, transitions, and feedback](../42-framework-deep-dives/78-swiftui-animation-motion-transitions-and-feedback.md)
- [Animation, motion, and Liquid Glass design](../21-design-deep-dives/106-animation-motion-and-liquid-glass-design.md)
- [SwiftUI animation and motion route](../50-capability-recipes/109-swiftui-animation-motion-route.md)
- [SwiftUI animation and motion recipes](../70-code-recipes/121-swiftui-animation-motion-recipes.md)
- [Custom rendering and animation proof matrix](09-custom-rendering-and-animation-proof-matrix.md)

## Evidence levels

| Level | Packet | Proves | Does not prove |
| --- | --- | --- | --- |
| M0 | Motion intent and state chart | The relationship the motion is meant to explain | The implementation matches the intent |
| M1 | Official source and SDK record | The API family, current documentation, and selected target are known | That the chosen overload compiles |
| M2 | Named-target compile | The selected target can build the route with the selected SDK | Runtime identity, accessibility, haptics, or performance |
| M3 | Preview/fixture matrix | Named normal, empty, loading, proposal, saved, failed, and fallback states render | Physical device, system settings, haptics, or production data |
| M4 | UI automation | State changes, insertion/removal, navigation, cancel, and visible result work | Human assistive task completion or physical feedback |
| M5 | Accessibility task run | Reduce Motion, Dynamic Type, contrast/transparency, VoiceOver, alternate input, and focus remain usable | Every device, App Review, or every future state |
| M6 | Async/domain proof | Cancellation, stale-result rejection, AI unavailable/refused, and durable commit are correct | Visual performance or system delivery |
| M7 | Device/performance proof | Haptics, glass rendering, frame/hitch behavior, memory, thermal, and input on a target device | Every supported device or production distribution |
| M8 | Signed release proof | Target/resource/entitlement/privacy and TestFlight behavior in the shipped artifact | Future builds, App Review decisions, or untested workloads |

## API claim matrix

| Claim | Required setup | Required assertion | Boundary |
| --- | --- | --- | --- |
| withAnimation animates a state change | Named target and stable state fixture | Related values animate and final state is correct | Does not prove domain success |
| animation(_:value:) is scoped | Two sibling views with one unrelated value | Only the intended subtree animates | Does not prove all inherited transactions |
| Transaction policy applies | Fixture with inherited and local animation | Local disable/replace behavior is observable | Does not prove persistence semantics |
| Completion fires at the intended point | Fixture with logical and removed criteria | Callback happens once at the documented visual boundary | Does not prove a save or task completion |
| Transition runs on insertion/removal | State-driven conditional view | Insertion and removal routes are distinct and cancellable | Does not prove identity preservation |
| Custom Transition preserves state | Stable content identity and transition body | State is not reset by transition implementation | Does not prove every layout variant |
| ContentTransition changes in place | Same view, changed content, animated transaction | Value updates with selected identity/opacity/interpolate/numeric route | Does not prove meaningful intermediate values |
| matchedGeometry links one object | One namespace, stable ID, exactly one source | Source and destination share selected geometry | Does not prove rendering transition, focus, or semantics |
| PhaseAnimator is bounded | Nonempty phases, trigger/cycle policy | Start, advance, stop/restart, and fallback behavior are deterministic | Does not prove real progress |
| KeyframeAnimator is bounded | Animatable value and track fixture | Trigger/restart/finish preserve expected values | Does not prove the per-frame path is inexpensive |
| Keyframe content is cheap | Instrumented maximum-workload fixture | No expensive work or domain mutation occurs per frame | A green compile is not a performance result |
| Content transition uses an Animation | Animated state mutation and content transition | The transition affects the content under test | Does not prove it runs when no animation exists |
| sensoryFeedback has meaning | Domain/result trigger and supported device | Feedback is emitted only on the intended change | Does not prove perception or accessibility |
| Glass morphs as intended | GlassEffectContainer, stable IDs, spacing fixture | Related shapes blend/morph under the selected transition | Does not prove GPU/thermal behavior |

## State and AI progress matrix

| Transition | Trigger | Visible state | Required assertion |
| --- | --- | --- | --- |
| unavailable -> idle | Device/model/input gate passes | Start action | Manual path is not blocked |
| idle -> generating | User starts request | Status/progress and cancel | No candidate is shown as committed |
| generating -> canceled | User cancels or view identity changes | Canceled/idle state | Late result cannot mutate the current record |
| generating -> proposal | Typed candidate returns | Review state and provenance | Candidate requires validation/acceptance |
| generating -> refusal | Model refuses or cannot answer | Explanation and fallback | No success animation or haptic |
| proposal -> applying | User accepts | Duplicate protection and scope | Domain operation begins once |
| applying -> saved | Durable operation succeeds | Saved record/revision | Success feedback is after the result |
| applying -> failed | Operation rejects/fails | Error, preserved source, recovery | No false saved state |
| saved -> stale | Current source/revision changes | Freshness/conflict action | Motion does not conceal stale truth |

## Transition and geometry matrix

| Scenario | Normal test | Reduced-motion test | Accessibility assertion |
| --- | --- | --- | --- |
| Optional message appears | Insert/remove with transition | Identity or opacity | Message and action are reachable |
| Card expands to detail | Matched geometry and destination transition | Crossfade/stable detail | Focus and label describe the same object |
| Glass action group changes | Container spacing/IDs/morph | Materialize or identity | Controls remain legible with reduced transparency |
| Content number updates | Numeric text transition | Immediate value | Exact value is exposed, not only animation |
| Long loading state | Bounded phase animation | Static status/progress | Cancel and status remain available |
| Error replacement | Content/opacity transition | Immediate error | Error and recovery are announced/readable |
| Rapid repeated action | Interrupt/restart fixture | Immediate route | No duplicate side effect |
| View disappears mid-motion | Remove/background fixture | Same final semantic state | No stale focus or false completion |

## Accessibility task matrix

| Setting/input | Task | Evidence |
| --- | --- | --- |
| Reduce Motion on | Start, cancel, review, accept, and recover | Same task and hierarchy without large/depth/repeating movement |
| Reduce Transparency on | Read and operate glass controls | Text, boundaries, focus, and selected state remain legible |
| Increased Contrast on | Distinguish ready/loading/saved/error | Distinction does not depend on translucency or color alone |
| Dynamic Type large | Complete the primary workflow | No clipped labels, hidden actions, or inaccessible status |
| VoiceOver | Navigate source, proposal, action, result | Labels/values/traits and focus order are meaningful |
| Voice Control | Invoke actions by name | Commands are discoverable and unambiguous |
| Switch Control | Move through the workflow | No timing-only or custom-gesture requirement |
| Keyboard/pointer | Complete on iPad/Mac input where supported | Focus and hover/pointer behavior do not change meaning |
| Localization/RTL | Use long translated strings and right-to-left layout | Motion and geometry do not clip or imply wrong direction |

## Performance and hitch matrix

| Claim | Fixture | Measurement | Record |
| --- | --- | --- | --- |
| Basic response is smooth | Normal tap/transition | Animation Hitches instrument | Build, device, OS, workload, hitches |
| Glass group is affordable | Maximum simultaneous glass effects | Instruments Animation Hitches and render tracks | Container count, spacing, effect count, thermal state |
| Keyframe path is cheap | Longest content and most complex tracks | CPU/GPU/frame/hitch data | Keyframe count, content closure work, frame evidence |
| Scroll/drag remains responsive | Motion while scrolling/dragging | Hitches, frame lifetime, main-thread activity | Content size, device refresh behavior, memory |
| AI review stays responsive | Generate/cancel/proposal in largest fixture | Main-thread work, hitches, memory, cancellation timing | Model/profile, input size, device, thermal state |
| Regression is repeatable | Fixed fixture and launch state | XCTest performance/hitch metric or Instruments trace | Baseline, threshold rationale, run count |
| Shipping behavior is known | Released/TestFlight build | Xcode Organizer/MetricKit aggregate signal | Release version, population/metric scope |

Apple’s Xcode documentation describes the Hitches metric in milliseconds of
pause per second and gives orientation values of 10 ms/s or less as good,
25 ms/s or less as warning, 50 ms/s or less as critical, and above 50 ms/s as
immediate attention. Store the exact metric context with the result; do not
turn one documented orientation into a universal product threshold.

## Physical and release matrix

| Claim | Physical-device evidence | Release evidence |
| --- | --- | --- |
| Haptic response works | Supported device, enabled setting, semantic event | Signed target contains the route |
| Liquid Glass renders acceptably | Representative and older supported device, appearance settings | Archive/TestFlight target/resource inspection |
| Reduced motion works | System setting enabled and full task completed | Accessibility review of release configuration |
| AI progress is honest | Model availability/refusal/cancel/proposal/commit run | Model resources, privacy manifest, and release configuration |
| Motion does not overheat/drain | Repeated workload and thermal/power observation | Post-release metric plan |
| External system presentation works | Widget/control/Live Activity/system surface if used | Target membership, capabilities, archive, TestFlight |

## Failure conditions

Stop and repair the route when:

- an animation completion writes domain truth;
- a repeating phase continues after the feature is idle or unavailable;
- a keyframe content closure performs expensive work;
- matched geometry has ambiguous sources or unstable IDs;
- a critical result is communicated only by motion, color, or haptic;
- Reduce Motion removes the task or hierarchy;
- a glass effect hides a disabled, stale, or error state;
- a preview or simulator screenshot is described as physical performance;
- a model result is shown as accepted before review/validation;
- a performance claim has no device, build, fixture, or measurement record.

## Sources

- [Animations](https://developer.apple.com/documentation/swiftui/animations)
- [Transaction](https://developer.apple.com/documentation/swiftui/transaction)
- [Transition](https://developer.apple.com/documentation/swiftui/transition)
- [ContentTransition](https://developer.apple.com/documentation/swiftui/contenttransition)
- [matchedGeometryEffect(id:in:properties:anchor:isSource:)](https://developer.apple.com/documentation/swiftui/view/matchedgeometryeffect%28id%3Ain%3Aproperties%3Aanchor%3Aissource%3A%29)
- [PhaseAnimator](https://developer.apple.com/documentation/swiftui/phaseanimator)
- [KeyframeAnimator](https://developer.apple.com/documentation/swiftui/keyframeanimator)
- [SensoryFeedback](https://developer.apple.com/documentation/swiftui/sensoryfeedback)
- [accessibilityReduceMotion](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion)
- [Motion](https://developer.apple.com/design/human-interface-guidelines/motion)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Understanding hitches in your app](https://developer.apple.com/documentation/xcode/understanding-hitches-in-your-app)
- [Improving app responsiveness](https://developer.apple.com/documentation/xcode/improving-app-responsiveness)
- [Performance Tests](https://developer.apple.com/documentation/xctest/performance-tests)
- [XCTHitchMetric](https://developer.apple.com/documentation/xctest/xcthitchmetric)
