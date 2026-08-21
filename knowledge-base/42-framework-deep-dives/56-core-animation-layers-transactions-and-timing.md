# Core Animation layers, transactions, timing, and display cadence

Core Animation is the lower-level rendering and animation system beneath many UIKit surfaces. It can compose image-based content, shapes, gradients, masks, shadows, transforms, and animated layer properties while the system performs much of the frame interpolation. It is useful when SwiftUI animation or UIKit view animation does not expose the exact rendering boundary the product needs.

Use it as a rendering tool, not as a second source of app truth:

~~~text
SwiftUI/UIKit state
  -> view or representable update
  -> model layer/property configuration
  -> Core Animation transaction/animation
  -> presentation-layer rendering
  -> completion/cancellation -> reconcile app state
~~~

Core Animation does not make a custom control semantic, a model result correct, or a glass surface native. The app still owns state, accessibility, permission, cancellation, and fallback behavior.

## Layer tree and view boundary

CALayer manages visual content and geometry. A layer can be the backing layer of a UIView or can be created and composed independently. Its properties include:

- contents, contentsRect, and contentsGravity;
- bounds, position, anchor point, transform, and z position;
- opacity, hidden state, masks, corner radius, border, and background color;
- shadow color, opacity, radius, offset, and shadow path;
- sublayers, masks, and hit testing;
- preferred dynamic range and content headroom on SDKs that expose them.

There are two important layer representations:

| Representation | Use | Authority |
| --- | --- | --- |
| Model layer | The property values the app intends to maintain | App-owned visual state. |
| Presentation layer | The values currently being rendered during an animation | Transient observation for interaction or diagnostics. |

When a view owns its backing layer, keep the view’s layer delegate relationship under UIKit’s control. For a custom layer tree, own the layer and its delegate intentionally. Do not attach a domain object as a layer delegate merely to receive business events.

Layer coordinates, hit testing, layout, and accessibility are separate systems. A shape that looks like a button is not a button. Keep a semantic SwiftUI or UIKit control above or beside custom visuals.

## Transactions: atomic layer updates

Every layer-tree modification belongs to a Core Animation transaction. Implicit transactions are created automatically and committed with the run loop. Explicit CATransaction groups let the app:

- update multiple layers as one visual change;
- set duration and timing for the group;
- disable implicit actions for setup or state reconciliation;
- register a completion block;
- nest a transaction for a sub-animation.

Use an explicit transaction for coordinated visual changes:

~~~text
begin
  configure duration/timing
  update model-layer properties
  optionally disable implicit actions
  register completion
commit
~~~

Do not use a completion callback as proof that a domain write, network request, system surface, or AI operation succeeded. It means the grouped animation reached its Core Animation completion boundary.

For initial setup, reuse, and state jumps, disable implicit actions. Otherwise, a cell reuse or a SwiftUI update can animate from an old model value and produce a visual ghost. For intentional transitions, use an explicit animation object or transaction so the visual contract is visible in code.

## CAAnimation family

| Type | Best use | Boundary |
| --- | --- | --- |
| CABasicAnimation | One property from a known start to end value | Keep the model layer at the intended end value. |
| CAKeyframeAnimation | A path or multiple key values | Paths with incompatible control points do not have a defined interpolation. |
| CASpringAnimation | A spring-like property transition | Tune for a consistent task, not just a dramatic effect. |
| CAAnimationGroup | Several animations with shared timing | Group completion is a visual completion, not a business completion. |
| CATransition | A transition between layer states | Avoid using a transition to hide content or state changes the user must understand. |

Adding an animation to a layer changes the render tree. A common mistake is to add a CABasicAnimation with a fromValue and toValue but never update the model layer. When the animation is removed, the layer can snap back to the old model value. Set the model property to the final intended value, then animate the presentation from the current visual state when needed.

The removed-on-completion and fill-mode options are not substitutes for updating model state. They can make a screenshot look correct while leaving later layout, hit testing, or state reconciliation wrong.

## Timing and pacing

CAMediaTiming models the relationship between parent and local time. Layers and animations can use duration, begin time, speed, time offset, repeat count, repeat duration, autoreverse, and fill mode. CAMediaTimingFunction maps normalized progress through a timing curve, including system-provided curves or a cubic Bézier curve.

Choose timing from the user task:

- direct manipulation should feel attached to the gesture;
- state confirmation should settle without overshoot that changes meaning;
- a status accent can use a short fade or scale;
- a large 3D-like move should honor Reduce Motion;
- a progress indicator should reflect actual work rather than a decorative timer.

Keep a small motion token set for duration, curve, spring, and interruption behavior. Do not scatter arbitrary durations through layer code. Core Animation pacing should agree with SwiftUI Transaction or UIViewPropertyAnimator when a single feature crosses frameworks.

## CADisplayLink and frame cadence

CADisplayLink calls a target in sync with display updates. Its timestamp describes the last displayed frame; targetTimestamp describes the next target frame. The interval targetTimestamp minus timestamp is useful for frame-budget calculations.

Use a display link only when the feature owns a per-frame computation or rendering loop, such as a custom visualizer, timeline scrubber, or legacy layer-driven effect. A display link is not needed for ordinary SwiftUI state animation.

The display link’s preferred frame rate is a request, not a guarantee. The system can choose a supported factor based on hardware, Low Power Mode, thermal state, accessibility settings, and other work. Apple recommends choosing a frame rate the app can maintain consistently. Pause when the surface is not visible and invalidate when the owner is gone.

Do not perform model inference, network work, file I/O, or unbounded layout in the display-link callback. Compute bounded visual parameters elsewhere and keep the per-frame step cheap.

## Shape, gradient, mask, and particle layers

CAShapeLayer draws a cubic Bézier path and supports fill, stroke, dash, line, and path properties. Its path can be animated with CAPropertyAnimation, but Apple documents that CGPath properties do not support implicit animation. Paths with different segment/control structures do not have defined interpolation.

CAGradientLayer draws a gradient over its bounds. Masks can reveal or clip content, and CAReplicatorLayer can create repeated sublayer copies with geometric, temporal, and color changes. CAEmitterLayer provides a particle system. These tools are powerful but can become visual noise or expensive rasterization.

Keep shapes and gradients subordinate to semantic content:

- use a CAShapeLayer for a progress outline behind a real label/value;
- use a gradient as a background accent, not as a substitute for contrast;
- use masks to reveal a known state, not to obscure a loading/error state;
- treat particles as optional decoration with reduced-motion and low-power fallbacks;
- avoid rasterization settings until measured on representative devices.

## UIKit property animation

UIViewPropertyAnimator animates changes to view properties and supports pause, resume, interactive control, fractionComplete, reversal, timing parameters, and completion. It is a good boundary for view-owned transitions, especially when the interaction needs to scrub or interrupt.

Use UIViewPropertyAnimator for view properties and Core Animation for layer properties or custom render trees. Do not drive the same property from SwiftUI, UIViewPropertyAnimator, and a layer animation at the same time without an explicit ownership rule.

## SwiftUI interoperation

UIViewRepresentableContext provides the current SwiftUI transaction and environment to a UIKit view wrapper. A bridge can use the context transaction to animate changes or disable animation when the update is a reconciliation jump. Keep the bridge small:

~~~text
SwiftUI state
  -> updateUIView(context)
  -> UIKit view/property owner
  -> layer configuration
  -> visual completion
~~~

The model layer is not a SwiftUI source of truth. SwiftUI should own the feature state; the representable should apply it idempotently and clean up animations/tasks when it disappears.

Accessibility must be expressed at the SwiftUI/UIKit semantic layer. If a visual layer communicates a custom interaction, use accessibilityRepresentation or a real semantic control. A moving shape alone has no useful label, value, or adjustable action.

## Liquid Glass and native polish

Use system Liquid Glass APIs and native controls for the main interface. Core Animation is appropriate for a small custom accent, a custom chart path, a layer-backed visualizer, or a UIKit control that must animate a layer property. Do not use CALayer to reproduce Apple-owned system chrome or to fake a glass effect that should be supplied by SwiftUI.

For a glass surface:

- keep the glass container and semantic controls in SwiftUI;
- keep custom layer visuals behind or beside those controls;
- synchronize layer bounds and corner geometry with layout;
- avoid animating a mask or blur over text that must remain readable;
- provide reduced-transparency and reduced-motion fallbacks;
- measure layer count, offscreen rendering, and frame time on device.

## AI-bounded motion

An on-device model may propose a visualization density, color family, or animation intensity from user-approved data. It should not write arbitrary layer key paths, inject unbounded particle counts, or control a display link directly.

Use a typed, bounded proposal:

~~~text
model proposal
  -> validated duration/opacity/scale/particle-count ranges
  -> accessibility and power policy
  -> deterministic layer configuration
  -> user-visible fallback
~~~

If the proposal is invalid, stale, unavailable, or conflicts with Reduce Motion, use the deterministic native fallback.

## Failure and safety checklist

- Keep model-layer state correct after every explicit animation.
- Cancel or remove animations when the owning view/task disappears.
- Do not use presentation-layer values as canonical persistence.
- Avoid retain cycles in display-link targets and animation completions.
- Invalidate display links and stop per-frame work offscreen.
- Avoid unmeasured shouldRasterize, masks, filters, and particle counts.
- Keep semantic controls independent of custom layers.
- Honor reduced motion, reduced flashing, reduced transparency, high contrast, Dynamic Type, and VoiceOver.
- Reconcile UIKit/Core Animation changes idempotently from SwiftUI updates.
- Test interrupted, reversed, repeated, and backgrounded animations.

## Related routes

- [Core Animation native motion and glass design](../21-design-deep-dives/76-core-animation-native-motion-and-glass-design.md)
- [Core Animation layer and display-link route](../50-capability-recipes/79-core-animation-layer-and-display-link-route.md)
- [Core Animation motion proof matrix](../60-verification/73-core-animation-motion-proof-matrix.md)
- [Core Animation layer and animation recipes](../70-code-recipes/91-core-animation-layer-and-animation-recipes.md)
- [Canvas, TimelineView, and custom rendering](../21-design-deep-dives/13-canvas-timeline-and-custom-rendering.md)

## Sources

- [Core Animation](https://developer.apple.com/documentation/quartzcore)
- [CALayer](https://developer.apple.com/documentation/quartzcore/calayer)
- [CAAnimation](https://developer.apple.com/documentation/quartzcore/caanimation)
- [CABasicAnimation](https://developer.apple.com/documentation/quartzcore/cabasicanimation)
- [CAKeyframeAnimation](https://developer.apple.com/documentation/quartzcore/cakeyframeanimation)
- [CASpringAnimation](https://developer.apple.com/documentation/quartzcore/caspringanimation)
- [CAAnimationGroup](https://developer.apple.com/documentation/quartzcore/caanimationgroup)
- [CATransition](https://developer.apple.com/documentation/quartzcore/catransition)
- [CATransaction](https://developer.apple.com/documentation/quartzcore/catransaction)
- [CAMediaTimingFunction](https://developer.apple.com/documentation/quartzcore/camediatimingfunction)
- [CADisplayLink](https://developer.apple.com/documentation/QuartzCore/CADisplayLink?changes=_9)
- [CAShapeLayer](https://developer.apple.com/documentation/quartzcore/cashapelayer)
- [CAGradientLayer](https://developer.apple.com/documentation/quartzcore/cagradientlayer)
- [UIViewPropertyAnimator](https://developer.apple.com/documentation/uikit/uiviewpropertyanimator)
- [UIViewRepresentableContext](https://developer.apple.com/documentation/swiftui/uiviewrepresentablecontext)
- [accessibilityReduceMotion](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion)
- [accessibilityRepresentation](https://developer.apple.com/documentation/swiftui/view/accessibilityrepresentation%28representation%3A%29)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
