# SwiftUI animation, motion, transitions, and feedback

## Purpose

SwiftUI motion is a rendering response to a state change. It is not the state
change, the persistence operation, the network request, or the result of an
on-device model. The clean route is:

    domain state -> visible state -> animation/transition policy
      -> accessibility policy -> semantic feedback -> proof

This page joins the current SwiftUI animation, transaction, transition,
geometry, phase, keyframe, content-transition, sensory-feedback, Liquid Glass,
and responsiveness documentation into one iOS 26 reference. It complements
the broader [interaction and transition cookbook](../21-design-deep-dives/07-interaction-and-transition-cookbook.md)
and the [custom rendering and animation proof matrix](../60-verification/09-custom-rendering-and-animation-proof-matrix.md).

Use this page with:

- [Animation, motion, and Liquid Glass design](../21-design-deep-dives/106-animation-motion-and-liquid-glass-design.md)
- [SwiftUI animation and motion route](../50-capability-recipes/109-swiftui-animation-motion-route.md)
- [SwiftUI animation and motion proof matrix](../60-verification/103-swiftui-animation-motion-proof-matrix.md)
- [SwiftUI animation and motion recipes](../70-code-recipes/121-swiftui-animation-motion-recipes.md)
- [Core Motion and Core Haptics](../42-framework-deep-dives/16-core-motion-and-core-haptics.md)

## The motion vocabulary

The first decision is what kind of visual change is being described. Choosing
the wrong family usually creates fragile identity, confusing accessibility
behavior, or an animation that claims more than the product actually knows.

| Need | SwiftUI route | Meaning | Boundary |
| --- | --- | --- | --- |
| Animate a value change in an existing view | Animation, withAnimation, animation(_:value:), or a binding animation | Interpolate animatable view values when state changes | It does not make a state mutation durable or successful |
| Pass motion through a hierarchy | Transaction, withTransaction, transaction modifier | Carry animation and update policy through the current state-processing update | It applies to view processing; it is not a domain transaction |
| Add or remove a view | transition(_:) and Transition | Define how a view enters or leaves the hierarchy | It requires correct view identity and an animated state change |
| Change content inside one view | contentTransition(_:) | Animate the content of the same view, such as text or a symbol | It only takes effect in an Animation transaction |
| Link two representations of one visual object | matchedGeometryEffect | Synchronize selected geometry between source and destination views | It links geometry; normal transitions still control rendering |
| Coordinate discrete animation states | phaseAnimator | Cycle through or trigger a sequence of Equatable phases | The phases are presentation values, not business progress |
| Coordinate continuous tracks | keyframeAnimator | Interpolate a custom Animatable value using keyed tracks | The content closure runs every frame; keep it cheap |
| Provide system haptic/audio meaning | sensoryFeedback | Play semantic feedback when a trigger changes | It is optional output and cannot be the only confirmation |
| Morph Liquid Glass shapes | GlassEffectContainer, glassEffectID, glassEffectTransition | Let related glass effects blend or morph during hierarchy changes | It is scoped to the container and requires performance/accessibility proof |

Animation should explain a relationship: where a control came from, what
changed, which content is replacing which, or that a short action completed.
Decorative motion that does not explain a relationship should be the first thing
removed when performance, battery, reduced motion, or cognitive load becomes a
problem.

## State is authoritative; motion is derived

Keep the domain state and presentation state separate:

    source record / operation status / model availability
      -> derived visual state
      -> selected animation or transition
      -> optional haptic/audio feedback

For an on-device AI feature, a useful state chart is:

| Domain state | Visible state | Motion policy | Completion rule |
| --- | --- | --- | --- |
| unavailable | Explain the device, OS, model, permission, or input gate | No looping ornament; show manual route | The user can continue without the model |
| idle | Ready control and source context | System control behavior or a restrained entrance | No generated result is implied |
| generating | Progress/status and cancel action | Optional subtle phase animation | Do not show accepted content before the request returns |
| proposal | Source, generated candidate, provenance, and review actions | Short content or glass transition | Candidate remains a proposal |
| applying | Disabled duplicate action and explicit scope | Completion animation only if it clarifies the commit | Domain operation decides success |
| saved | Durable record, revision, or confirmation | Brief semantic feedback | Persistence/sync result is the authority |
| refused or failed | Reason and recovery path | Identity/crossfade route is usually enough | Preserve source and allow retry/manual work |

Never use an animation completion callback to mark a record saved. The callback
only describes a view animation. Commit the record when the domain operation
returns success, then derive the saved visual state.

## Animation and transactions

An Animation describes how a view changes over time when an animatable value
changes. The common choices are:

- use withAnimation around a related state mutation when several visible
  values should respond as one update;
- use animation(_:value:) when a specific view subtree should respond to a
  specific Equatable value;
- use a Binding animation when the binding itself is the interaction seam;
- use withTransaction or a transaction modifier when a subtree needs a
  deliberate animation, disabled-animation, or transaction policy;
- return nil or disable motion in a reduced-motion route when the change does
  not need movement to remain understandable.

The Transaction type is the context of the current state-processing update.
SwiftUI uses the transaction associated with the binding or the transaction
created by withTransaction or withAnimation. A transaction can carry an
Animation and can set disablesAnimations. A view transaction modifier can
change the transaction for animations used within that view.

This creates two different meanings that must not be conflated:

| UI transaction | Domain transaction |
| --- | --- |
| Carries view animation and rendering-update policy | Validates and commits a business operation |
| May complete when the animation is logically complete or fully removed | Completes when the domain authority accepts or rejects the operation |
| Can be interrupted by a new state change | Must define idempotence, retry, conflict, or rollback |
| Is not persistence or network confirmation | Is the source for saved/error state |

SwiftUI also provides animation completion criteria. Logically complete means
the animation has reached its logical endpoint even if a long tail remains.
Removed waits until the entire animation is finished and the view can be
removed. If a completion is needed, choose the criterion based on what the
visual state means, and keep the callback idempotent. If a later state change
creates more animations, a completion can be delayed by those animations.

Use an animation completion for presentation work such as moving focus,
removing a temporary overlay, or announcing a visual phase. Use the domain
operation for saving, deleting, sending, accepting an AI proposal, or changing
authorization.

## Transitions and view identity

A transition describes what happens when a view is added to or removed from the
view hierarchy. It is different from an animation of a value in a view that
already exists.

Recommended sequence:

    stable state change -> view insertion/removal -> transition
      -> animated properties -> accessible final state

Important rules:

- the transition needs an animated state change to be visible;
- preserve stable identity for content that should keep its local state;
- use an explicit transition when insertion/removal semantics matter;
- choose an asymmetric transition when insertion and removal have different
  meanings;
- keep the semantic label and action present in the final state;
- do not hide an error, permission result, or critical control inside a
  decorative transition;
- avoid putting identity-affecting if, switch, or id changes inside a custom
  Transition body, because doing so can reset state and cause wasted work;
- make the identity/reduced-motion route understandable when motion is removed.

For a custom Transition, use its TransitionPhase to modify visual properties
such as opacity, offset, scale, or blur according to insertion/removal phase.
Do not use the transition itself to mutate domain state. If a view disappears
because a request was canceled, the request state should already say canceled.

## Content transitions

ContentTransition applies inside one view rather than to insertion/removal of
the view itself. It is useful for:

- a number that changes and should use numericText;
- a symbol that changes and can use a symbol effect;
- text or path changes that can use interpolate;
- a simple replacement where opacity is clearer;
- an identity route when motion is unnecessary.

Content transitions only have an effect inside an Animation transaction. They
are therefore a presentation choice, not a guarantee that every text update
will animate. The value, label, and accessibility representation must still
change correctly when the transition is unavailable or disabled.

Use numeric text transitions for values that people interpret as counts,
levels, or totals. Do not animate a count if the intermediate values would be
misleading, expose private information, or imply a precision the source does
not have. For model output, prefer a stable status and reviewable replacement
over a theatrical character-by-character effect unless that behavior is
intentional, bounded, and tested.

## Matched geometry

matchedGeometryEffect synchronizes selected geometry between views in the same
namespace using a Hashable identifier. If one view with the same key is
removed while another is inserted in the same transaction, SwiftUI can
interpolate their frame rectangles in window space so the user perceives one
object moving between representations.

The modifier does not own rendering. The normal transitions still determine
how the source and destination render, so combine geometry matching with an
appropriate opacity, scale, blur, or identity route.

Guardrails:

- create the Namespace in a view whose identity outlives both representations;
- derive IDs from stable visual identity, not a random UUID generated during
  body evaluation;
- ensure exactly one inserted view is the source for a matched group;
- do not create two competing source views; behavior is undefined when the
  source count is not exactly one;
- match only representations that people will understand as the same object;
- keep source and destination accessibility labels and focus behavior correct;
- use a simple crossfade or identity route when Reduce Motion is enabled or
  when geometry would imply a false relationship;
- test rapid toggles, interrupted transitions, dynamic type, compact layouts,
  and source/destination disappearance.

Matched geometry is especially useful for a card becoming a review sheet, a
compact Liquid Glass action becoming an expanded control group, or a thumbnail
becoming a detail header. It is not a replacement for NavigationStack route
state or persistence.

## PhaseAnimator

PhaseAnimator represents a sequence of discrete presentation phases. SwiftUI
can cycle continuously through a sequence or advance through phases when a
trigger value changes. Each phase is Equatable and the content closure maps
the current phase to visual modifiers. The animation closure can choose the
animation used for the change to the next phase, or return nil for an
instantaneous change.

Use phases for:

- a short, bounded tap response;
- a two- or three-step symbol or control flourish;
- a staged entrance where each stage has a clear visual meaning;
- a subtle unavailable/idle status hint that can stop when the state changes.

Avoid phases for:

- actual network/model progress;
- authorization or saved state;
- retry loops with no cancel or stop condition;
- a critical warning;
- continuous motion that can run without a user-visible purpose.

Keep the phase collection non-empty. A phase animator with no phases is a
runtime warning and does not produce a valid presentation. Separate the
trigger that starts the visual sequence from the operation state that decides
whether the feature is still running.

## KeyframeAnimator

KeyframeAnimator coordinates a custom value over time. Define a value type with
independently animatable properties, then use keyframe tracks to interpolate
those properties. KeyframeAnimator supports repeating and trigger-based
variants.

The important performance contract is that the content closure updates every
frame while the animation runs. Do not perform expensive work there. In
particular, do not:

- decode images;
- query a database;
- call a model;
- allocate a large collection;
- perform blocking I/O;
- log a large payload;
- calculate layout that could be precomputed;
- mutate the domain model.

Precompute constants and use the interpolated value only to apply lightweight
visual modifiers. If the effect needs a Canvas, shader, or GPU resource, keep
resource creation outside the per-frame path and use the [custom rendering
proof matrix](../60-verification/09-custom-rendering-and-animation-proof-matrix.md).

Keyframes are appropriate when the motion itself is the product experience:
for example, a bounded spring-and-scale response with independently timed
scale, offset, and rotation. Use a normal Animation when one spring or a
simple transition expresses the relationship more clearly.

## Sensory feedback

SwiftUI sensoryFeedback represents semantic haptic and/or audio feedback
played from a view when a trigger changes. Choose feedback by meaning rather
than by visual spectacle:

| Event | Possible feedback meaning | Do not do |
| --- | --- | --- |
| Selection changes | selection | Play on every unrelated model update |
| Activity begins | start | Announce success before work starts |
| Activity ends | stop | Treat cancellation as success |
| Durable operation succeeds | success | Play before persistence/sync succeeds |
| Error or rejected operation | error/warning | Use a warning for ordinary validation |
| Significant level threshold | increase/decrease/levelChange | Fire for noisy continuous samples |
| Alignment or boundary | alignment/impact | Use as the only state signal |

Haptics can be unavailable, disabled, hard to perceive, or inappropriate. Pair
them with visible text, shape, color, and accessible state. Use Core Haptics
when the product needs a custom pattern, synchronized audio/haptic timeline,
dynamic parameters, or an engine lifecycle; use sensoryFeedback for a concise
system-semantic response.

## Reduced motion and accessible motion

Read the accessibilityReduceMotion environment value and make the policy
explicit. Apple’s Motion guidance says to make motion purposeful and optional,
keep feedback brief and precise, let people cancel it, and avoid making motion
the only communication channel. When Reduce Motion is enabled, avoid large
animations, especially motion that simulates depth.

Useful reduced-motion substitutions:

| Normal route | Reduced-motion route |
| --- | --- |
| Matched geometry across distant positions | Opacity or identity transition with stable focus |
| Large scale/depth movement | Small opacity or color/state change |
| Repeating peripheral phase | Static status or a short nonrepeating response |
| Animated blur in/out | Stable material/opacity change |
| Bouncy spring | Tighter spring or no animation |
| Auto-playing image motion | Static first frame or user-started playback |
| Motion-only progress | Text/status/progress indicator with a cancel action |

Also test reduced transparency, increased contrast, Differentiate Without
Color, Dynamic Type, VoiceOver, Voice Control, Switch Control, keyboard/pointer
input, and localization. A reduced-motion branch is not complete if it removes
the only visible distinction between loading, failed, saved, and unavailable.

## Liquid Glass morphing

Liquid Glass is already used by standard system components. For custom
components, use the documented glassEffect route sparingly. When related glass
effects need to blend or morph, place them in a GlassEffectContainer and
associate stable glassEffectID values within a Namespace.

The documented Liquid Glass transition choices have distinct meanings:

- matchedGeometry coordinates nearby glass effects and lets the system match
  their shapes;
- materialize fades content and animates the glass material without trying to
  match distant geometry;
- identity changes nothing.

The IDs and transition modifiers affect content during view hierarchy
transitions or animations. They do not make unrelated glass shapes a single
semantic control.

The container spacing matters. Apple documents that larger spacing can cause
effects to blend sooner, and interior layout spacing can cause shapes to blend
at rest. Use a container for related effects and avoid many separate containers
or too many simultaneous glass effects. The system documentation explicitly
warns that excessive containers/effects can degrade performance.

A safe morphing contract is:

    same action/visual identity -> stable glass ID -> related container
      -> chosen glass transition -> normal animation
      -> reduced-motion/contrast fallback -> device hitch proof

Do not use Liquid Glass morphing to imply that a generated AI proposal is
already committed. The glass can make a review state feel coherent; the domain
state must still say proposal, applying, saved, or failed.

## Performance and responsiveness

Motion performance is a render-loop problem as well as a view-composition
problem. Apple describes a hitch as an interruption in motion caused by a late
frame. Commit hitches usually involve main-thread work; render hitches involve
rendering work. Both can occur during animation, scrolling, and dragging.

Keep the animated path small:

- keep per-frame closures cheap;
- avoid doing work on the main thread that does not need to be there;
- isolate expensive model, image, layout, or persistence work from visual
  state updates;
- avoid starting multiple animations for the same state change;
- prefer one related animation over nested, competing effects;
- stop repeating animations when the state no longer needs them;
- limit simultaneous Liquid Glass effects and containers;
- test the maximum content, longest strings, largest text, and heaviest model
  result rather than only the empty preview;
- profile on a real supported device, including an older supported device when
  practical.

Use Xcode’s Animation Hitches template and Instruments to find commit/render
hitches. XCTest performance and hitch metrics can provide repeatable
regression fixtures, but a metric from one synthetic fixture does not prove
every device, thermal state, or production workload. Xcode Organizer and
MetricKit provide post-release signals that should be interpreted separately
from a local debug run.

The Xcode documentation gives a useful orientation for Hitches: a hitch rate
at or below 10 ms/s is good, at or below 25 ms/s is a warning, at or below
50 ms/s is critical, and above 50 ms/s warrants immediate attention. Treat
these as Apple’s documented interpretation for the named metric, not as a
universal acceptance threshold for every app. Record the target, build,
fixture, device, OS, thermal state, and workload with any threshold.

## Proof boundary

| Claim | Minimum evidence | Still not proved |
| --- | --- | --- |
| A state change animates | Named-target compile and UI assertion | Accessibility comprehension or device performance |
| A transition preserves identity | Insert/remove test with stable IDs | Every layout, locale, or rapid-interaction path |
| Geometry looks like one object | Physical or simulator UI run with source/destination states | Correct semantics, focus, reduced motion, or device performance |
| Phase/keyframe motion is bounded | Trigger/restart/stop tests and a device run | Battery/thermal behavior under long use |
| Feedback has the right meaning | Domain result test plus supported-device run | Perception in every physical context |
| Reduced Motion is supported | UI task completed with setting enabled | App Store accessibility labeling or every accessibility setting |
| Glass morphs correctly | Signed target run with stable IDs/container spacing | All GPUs, thermal states, or custom materials |
| Motion is smooth | Animation Hitches/Instruments fixture on target device | All users, production traffic, future SDKs |
| AI progress is honest | State-machine test for availability, cancellation, refusal, proposal, commit | Model quality, availability, or truthfulness outside the evaluated setup |

## Sources

| Topic | Official source |
| --- | --- |
| SwiftUI animation overview | [Animations](https://developer.apple.com/documentation/swiftui/animations) |
| Animation values and completion | [Animation](https://developer.apple.com/documentation/SwiftUI/Animation), [withAnimation(_:_:)](https://developer.apple.com/documentation/swiftui/withanimation%28_%3A_%3A%29), [withAnimation(_:completionCriteria:_:completion:)](https://developer.apple.com/documentation/SwiftUI/withAnimation%28_%3AcompletionCriteria%3A_%3Acompletion%3A%29), and [AnimationCompletionCriteria](https://developer.apple.com/documentation/swiftui/animationcompletioncriteria) |
| Transactions | [Transaction](https://developer.apple.com/documentation/swiftui/transaction), [withTransaction(_:_:)](https://developer.apple.com/documentation/swiftui/withtransaction%28_%3A_%3A%29), and [transaction(_:)](https://developer.apple.com/documentation/swiftui/view/transaction%28_%3A%29) |
| View transitions | [Transition](https://developer.apple.com/documentation/swiftui/transition), [transition(_:)](https://developer.apple.com/documentation/swiftui/view/transition%28_%3A%29), and [TransitionPhase](https://developer.apple.com/documentation/swiftui/transitionphase) |
| Content transitions | [ContentTransition](https://developer.apple.com/documentation/swiftui/contenttransition) and [contentTransition(_:)](https://developer.apple.com/documentation/swiftui/view/contenttransition%28_%3A%29) |
| Geometry identity | [matchedGeometryEffect(id:in:properties:anchor:isSource:)](https://developer.apple.com/documentation/swiftui/view/matchedgeometryeffect%28id%3Ain%3Aproperties%3Aanchor%3Aissource%3A%29), [MatchedGeometryProperties](https://developer.apple.com/documentation/swiftui/matchedgeometryproperties), and [Namespace](https://developer.apple.com/documentation/swiftui/namespace) |
| Phases and keyframes | [PhaseAnimator](https://developer.apple.com/documentation/swiftui/phaseanimator), [phaseAnimator(_:content:animation:)](https://developer.apple.com/documentation/swiftui/view/phaseanimator%28_%3Acontent%3Aanimation%3A%29), [KeyframeAnimator](https://developer.apple.com/documentation/swiftui/keyframeanimator), [keyframeAnimator(initialValue:trigger:content:keyframes:)](https://developer.apple.com/documentation/swiftui/view/keyframeanimator%28initialvalue%3Atrigger%3Acontent%3Akeyframes%3A%29), and [Controlling the timing and movements of your animations](https://developer.apple.com/documentation/SwiftUI/Controlling-the-timing-and-movements-of-your-animations) |
| Sensory feedback | [SensoryFeedback](https://developer.apple.com/documentation/swiftui/sensoryfeedback) and [sensoryFeedback(trigger:_:)](https://developer.apple.com/documentation/swiftui/view/sensoryfeedback%28trigger%3A_%3A%29) |
| Accessibility motion policy | [accessibilityReduceMotion](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion), [Accessible appearance](https://developer.apple.com/documentation/swiftui/accessible-appearance), [Motion](https://developer.apple.com/design/human-interface-guidelines/motion), and [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility) |
| Liquid Glass identity and morphing | [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views), [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer), [GlassEffectTransition](https://developer.apple.com/documentation/swiftui/glasseffecttransition), [glassEffectID(_:in:)](https://developer.apple.com/documentation/swiftui/view/glasseffectid%28_%3Ain%3A%29), and [glassEffectTransition(_:)](https://developer.apple.com/documentation/swiftui/view/glasseffecttransition%28_%3A%29) |
| Hitches and responsiveness | [Understanding hitches in your app](https://developer.apple.com/documentation/xcode/understanding-hitches-in-your-app), [Improving app responsiveness](https://developer.apple.com/documentation/xcode/improving-app-responsiveness), [Performance Tests](https://developer.apple.com/documentation/xctest/performance-tests), and [XCTHitchMetric](https://developer.apple.com/documentation/xctest/xcthitchmetric) |
