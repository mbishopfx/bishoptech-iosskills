# Core Animation native motion and Liquid Glass design

Motion is part of hierarchy. It tells a person what changed, what belongs together, what can be interrupted, and where to look next. Core Animation can create polished layer transitions, but Apple-native design comes from semantic controls, coherent state, useful timing, and respectful fallbacks.

Use this motion model:

~~~text
state change -> meaning -> small motion token -> interruptible transition
           -> accessibility/power fallback -> stable final state
~~~

Do not use motion to compensate for weak layout or to make a custom screen look like an Apple system screen.

## Choose the native owner

| Need | Prefer | Why |
| --- | --- | --- |
| SwiftUI state transition | SwiftUI animation and Transaction | Keeps layout, state, and accessibility near the view. |
| Native UIKit view transition | UIViewPropertyAnimator | Supports interactive pause, scrub, reverse, and completion. |
| Layer property or custom shape | Core Animation | Gives direct control over layer tree, timing, masks, paths, and render cadence. |
| Per-frame custom visualizer | CADisplayLink or a higher-level rendering route | Makes display cadence explicit; requires pause/invalidate and budget proof. |
| Liquid Glass grouping/morphing | SwiftUI Liquid Glass APIs | Preserves the system composition model and semantic surface. |

Use one owner per property. If SwiftUI changes opacity while a CALayer animation also owns opacity, the final state can jump or be overwritten.

## Motion tokens

Define a small design vocabulary:

| Token | Purpose | Fallback |
| --- | --- | --- |
| appear | New content becomes available | Immediate visibility with an announcement. |
| settle | A selected control or card confirms | Color, weight, or icon change without bounce. |
| move | An element changes position | Crossfade or direct update under Reduce Motion. |
| morph | Related glass controls change grouping | Stable container and explicit labels. |
| progress | Work advances | Determinate progress or text state; never an arbitrary loop as proof. |
| highlight | Focus a changed value | Contrast, border, or VoiceOver announcement. |

Record duration, curve, spring, and interruption behavior in a design system. A long duration is not automatically premium; a consistent, cancellable, task-proportional transition is more useful.

## Liquid Glass composition

Use Liquid Glass for controls and containers that float above content. Let SwiftUI own the glass surface and use Core Animation only for a contained accent such as:

- a shape-layer progress outline inside a real control;
- a small layer-backed visualization behind a toolbar;
- a custom mask that reveals a user-visible state;
- a UIKit bridge that needs a property animator.

Keep the hierarchy:

~~~text
content
  -> glass control group
  -> glass review group
  -> sheet or inspector for secondary detail
~~~

Avoid glass over glass over an animated blur. It lowers contrast, increases visual noise, and makes motion harder to parse. Do not animate the map, document, or important text merely to showcase the glass.

Native polish checklist:

- system controls remain recognizable;
- the primary action has a stable location;
- the glass container tracks layout and safe areas;
- interactive transitions can be interrupted;
- reduced transparency leaves a readable surface;
- the final model state is correct after a canceled animation;
- custom layer effects do not steal hit testing or accessibility focus.

## State and motion

Design motion from state transitions:

| State change | Visual behavior | Meaning |
| --- | --- | --- |
| loading -> ready | Short reveal or crossfade | Content is available. |
| ready -> error | Stop movement and expose error | The route needs attention. |
| draft -> accepted | Subtle settle/highlight | The person committed a value. |
| accepted -> shared | Use system handoff feedback | A share was initiated, not necessarily delivered. |
| collapsed -> expanded | Move related content together | The inspector belongs to the selected item. |
| old revision -> new revision | Replace or invalidate visibly | Earlier proposals may be stale. |

Do not let the animation itself carry essential state. A person using VoiceOver, Reduce Motion, or a slow device should still understand what changed.

## Accessibility and reduced effects

SwiftUI exposes accessibilityReduceMotion, accessibilityDimFlashingLights, and accessibilityPlayAnimatedImages environment values. Use them to reduce large depth-simulating moves, flashing/strobing effects, and automatically playing animated images.

For custom Core Animation:

- avoid large rotations, parallax, and depth simulation under Reduce Motion;
- pause or replace particle and flashing effects when the relevant setting is enabled;
- keep a visible final state when an animation is skipped;
- announce meaningful changes through the semantic view, not a visual layer;
- use accessibilityRepresentation when the visual control does not map cleanly to a semantic control;
- do not make a looping animation the only way to signal activity or success;
- test animation cancellation and VoiceOver focus after a sheet, card, or control moves.

Reduced motion is not a debug switch. It is a user requirement and a design mode.

## Interactive motion

If a person drags, scrubs, or dismisses a control, the motion should follow the gesture and settle to a predictable outcome. UIViewPropertyAnimator’s fractionComplete and timing controls are useful for UIKit. In a SwiftUI route, keep the gesture state in SwiftUI and let the representable apply the current transaction to its layer.

Rules:

- pause or remove an old animation before applying interactive state;
- read presentation-layer values only as transient visual input;
- commit the final model-layer value before ending;
- handle reversal and cancellation;
- keep hit testing aligned with the semantic view, not a moving decorative layer;
- test slow drags, interruptions, rotations, backgrounding, and repeated taps.

## AI-personalized motion

An on-device model may suggest a visual density, speed category, or accent style from explicit user preferences. Keep the output bounded:

~~~text
preference or proposal
  -> allowed token enum/range
  -> accessibility/power policy
  -> deterministic animation
~~~

Do not let a model choose arbitrary Core Animation key paths, durations, particle counts, or visual effects. The model cannot override Reduce Motion, high contrast, or a product safety rule. If the proposal is unavailable or invalid, use a tested default.

## Performance as perceived quality

Core Animation can offload much of interpolation, but layer composition, masks, filters, shadows, offscreen rendering, and large sublayer trees still cost. Measure:

- frame time and hitches during transitions;
- layer count and offscreen-rendering hotspots;
- memory for contents, masks, and rasterized surfaces;
- energy while a display link or particle system runs;
- behavior under Low Power Mode and thermal pressure;
- older supported devices and large Dynamic Type layouts.

Choose a consistent lower frame rate when a visualizer cannot maintain the maximum. A stable 30 frames per second can feel better than a stuttering 60.

## AccessibilityRepresentation for custom visuals

If a custom layer draws an adjustable value or control, expose a semantic SwiftUI representation. The visual layer remains decorative; the hidden representation supplies the accessibility element, label, value, and actions.

Do not put a fake visual control in the accessibility tree and leave the real action inaccessible. Keep the representation’s value synchronized with the model state, not a transient presentation-layer frame.

## Design review checklist

- The framework owner is chosen per property and per interaction.
- Motion communicates state and can be skipped without losing meaning.
- Glass contains semantic controls and does not cover critical content.
- Custom layers are decorative or rendering-specific, not business state.
- Model and presentation values reconcile after cancellation and reversal.
- Reduce Motion, reduced flashing, reduced transparency, contrast, Dynamic Type, and VoiceOver are designed.
- AI motion suggestions are typed, bounded, and subordinate to accessibility.
- The result is measured on physical devices and release-like builds.

## Related routes

- [Core Animation layers, transactions, timing, and display cadence](../42-framework-deep-dives/56-core-animation-layers-transactions-and-timing.md)
- [Core Animation layer and display-link route](../50-capability-recipes/79-core-animation-layer-and-display-link-route.md)
- [Core Animation motion proof matrix](../60-verification/73-core-animation-motion-proof-matrix.md)
- [Core Animation layer and animation recipes](../70-code-recipes/91-core-animation-layer-and-animation-recipes.md)

## Sources

- [Core Animation](https://developer.apple.com/documentation/quartzcore)
- [CALayer](https://developer.apple.com/documentation/quartzcore/calayer)
- [CATransaction](https://developer.apple.com/documentation/quartzcore/catransaction)
- [CAMediaTimingFunction](https://developer.apple.com/documentation/quartzcore/camediatimingfunction)
- [CADisplayLink](https://developer.apple.com/documentation/QuartzCore/CADisplayLink?changes=_9)
- [CAShapeLayer](https://developer.apple.com/documentation/quartzcore/cashapelayer)
- [UIViewPropertyAnimator](https://developer.apple.com/documentation/uikit/uiviewpropertyanimator)
- [UIViewRepresentableContext](https://developer.apple.com/documentation/swiftui/uiviewrepresentablecontext)
- [accessibilityReduceMotion](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion)
- [accessibilityDimFlashingLights](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilitydimflashinglights)
- [accessibilityPlayAnimatedImages](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityplayanimatedimages)
- [accessibilityRepresentation](https://developer.apple.com/documentation/swiftui/view/accessibilityrepresentation%28representation%3A%29)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Human Interface Guidelines accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Human Interface Guidelines motion](https://developer.apple.com/design/human-interface-guidelines/motion/)
