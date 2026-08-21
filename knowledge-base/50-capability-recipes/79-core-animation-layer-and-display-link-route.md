# Core Animation layer and display-link route

Use this route when a native SwiftUI or UIKit feature needs a bounded custom visual: a progress outline, shape-based indicator, layer-backed image effect, interactive card transition, or per-frame visualizer. Keep the route below the semantic view and above the renderer.

The route is:

~~~text
domain/UI state
  -> chosen animation owner
  -> model-layer or view-property update
  -> transaction/property animator/Core Animation
  -> presentation/render output
  -> cancellation/reconciliation
  -> accessibility and performance proof
~~~

Use SwiftUI animation for ordinary SwiftUI state. Branch to Core Animation only when the layer or cadence boundary is itself part of the feature.

## Choose the smallest owner

| Need | Owner |
| --- | --- |
| Fade, scale, layout, or state transition in SwiftUI | SwiftUI animation and Transaction |
| UIKit view properties with interruption | UIViewPropertyAnimator |
| Path, gradient, mask, shadow, or layer property | CALayer and CAAnimation |
| Per-frame visualizer or custom timeline | CADisplayLink, Canvas/TimelineView, or Metal according to the rendering need |
| Native glass grouping | SwiftUI Liquid Glass APIs |

Do not animate one property from multiple owners. Write down the owner in the feature plan.

## Route A: shape-layer progress indicator

Use a CAShapeLayer behind a semantic label or ProgressView-like control:

1. create the layer once;
2. set its frame/path during layout;
3. configure stroke/fill colors and line width;
4. update the model layer’s strokeEnd for domain progress;
5. animate only the change that the person should see;
6. expose the numeric or textual progress through the semantic view.

The path and presentation layer are visual details. Store progress in the domain/UI model, not in presentation-layer state.

## Route B: layer-backed state transition

For a layer property:

1. stop or reconcile any old animation;
2. read the current presentation value only if an interactive handoff needs it;
3. update the model layer to the intended final value;
4. add a basic, spring, keyframe, or group animation;
5. complete or cancel the route;
6. keep the semantic state and hit testing aligned.

If a feature is interrupted, remove the animation and leave the model layer at the appropriate current or final state. Never use fill mode to keep an incorrect model value on screen.

## Route C: coordinated transaction

Use CATransaction when several layers must update together:

~~~text
begin explicit transaction
  set duration/curve
  update model layers
  set completion for visual cleanup
commit
~~~

Use disable actions for setup, reuse, and immediate state reconciliation. Use a completion only for visual cleanup such as removing a temporary layer. A transaction completion is not a domain commit or a proof that another framework finished.

## Route D: interactive UIKit transition

Use UIViewPropertyAnimator when a UIKit view’s position, transform, alpha, or other animatable property follows a gesture:

- create the animator with a deliberate timing curve;
- pause and set fractionComplete from the gesture;
- support reversal and cancellation;
- finish or continue with a final timing parameter;
- remove references when the transition completes;
- keep the semantic control and accessibility focus stable.

If SwiftUI owns the feature state, the representable should receive the state and transaction from SwiftUI and apply it idempotently.

## Route E: display-synchronized visualizer

Use CADisplayLink only when per-frame work is required:

1. create the link with an owner that does not retain itself accidentally;
2. add it to the correct run loop;
3. use timestamp and targetTimestamp for time-based progress;
4. choose a frame-rate range the device can maintain;
5. pause when not visible or when the task is inactive;
6. avoid model/network/file work in the callback;
7. invalidate when the owner disappears.

For a visualizer, drive a bounded visual state such as phase, amplitude, or progress. Do not store a raw frame history indefinitely.

## State and cancellation

| Event | Required response |
| --- | --- |
| New model state | Reconcile model layer/property first, then animate if appropriate. |
| View reused | Remove old animations and apply current state without an implicit transition. |
| Gesture begins | Pause or remove conflicting animation and capture a transient presentation value if needed. |
| Gesture cancels | Restore model state and animate back or settle immediately. |
| Reduce Motion enabled | Skip or simplify the visual transition and announce the state through semantics. |
| View leaves screen | Pause display link, cancel task, and remove observers. |
| App backgrounds | Stop unnecessary frame work and preserve domain state. |
| Memory/thermal pressure | Reduce content, frame rate, particles, or effects before dropping the feature. |

## AI-bounded visual parameters

If on-device AI proposes a motion or visualization style, map it to a closed enum or bounded numeric range. Validate against:

- Reduce Motion and dim-flashing settings;
- maximum duration and particle count;
- high-contrast and reduced-transparency fallback;
- device performance tier and current thermal/power state;
- feature semantics, so a progress indicator cannot become an indeterminate flourish.

The app owns the final layer configuration. Never execute model output as a key-path name or animation class.

## Privacy and data boundaries

Custom motion should not capture more user data than the visual requires. If a visualizer uses microphone, motion, location, health, or camera input, keep that permission and data lifecycle in its owning framework. Core Animation only renders the derived value.

Do not put raw input, model output, or personal content in layer names, debug screenshots, analytics, or Core Animation completion logs.

## Evidence boundary

| Evidence | Proves | Does not prove |
| --- | --- | --- |
| Preview | Initial layout and deterministic visual state | Device cadence, energy, accessibility task, or runtime performance. |
| Compile | API names and target interop | Correct layer ownership, cancellation, or device smoothness. |
| Unit test | Token mapping, state machine, and bounded values | Render-tree appearance or physical timing. |
| UI test | Tap/gesture/state transitions in a controlled build | Real frame pacing, thermal behavior, or all accessibility settings. |
| Physical device | Actual rendering, cadence, settings, memory, and interaction on that device | All supported devices or future OS behavior. |
| Signed release build | Target membership, flags, resources, and artifact identity | Fleet performance or App Store delivery. |

Use the [Core Animation motion proof matrix](../60-verification/73-core-animation-motion-proof-matrix.md) for the full route.

## Related routes

- [Core Animation layers, transactions, timing, and display cadence](../42-framework-deep-dives/56-core-animation-layers-transactions-and-timing.md)
- [Core Animation native motion and Liquid Glass design](../21-design-deep-dives/76-core-animation-native-motion-and-glass-design.md)
- [Core Animation layer and animation recipes](../70-code-recipes/91-core-animation-layer-and-animation-recipes.md)

## Sources

- [Core Animation](https://developer.apple.com/documentation/quartzcore)
- [CALayer](https://developer.apple.com/documentation/quartzcore/calayer)
- [CAShapeLayer](https://developer.apple.com/documentation/quartzcore/cashapelayer)
- [CAGradientLayer](https://developer.apple.com/documentation/quartzcore/cagradientlayer)
- [CAAnimation](https://developer.apple.com/documentation/quartzcore/caanimation)
- [CABasicAnimation](https://developer.apple.com/documentation/quartzcore/cabasicanimation)
- [CAKeyframeAnimation](https://developer.apple.com/documentation/quartzcore/cakeyframeanimation)
- [CASpringAnimation](https://developer.apple.com/documentation/quartzcore/caspringanimation)
- [CATransaction](https://developer.apple.com/documentation/quartzcore/catransaction)
- [CAMediaTimingFunction](https://developer.apple.com/documentation/quartzcore/camediatimingfunction)
- [CADisplayLink](https://developer.apple.com/documentation/QuartzCore/CADisplayLink?changes=_9)
- [UIViewPropertyAnimator](https://developer.apple.com/documentation/uikit/uiviewpropertyanimator)
- [UIViewRepresentableContext](https://developer.apple.com/documentation/swiftui/uiviewrepresentablecontext)
- [accessibilityReduceMotion](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
