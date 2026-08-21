# Animation, motion, and Liquid Glass design

## Design principle

Apple-native motion is purposeful, brief, optional, and tied to the person’s
action or the relationship between two states. Liquid Glass can make a
transition feel fluid, but it should never hide whether an action is pending,
accepted, unavailable, or failed.

Use this loop:

    user intent -> state change -> visual relationship
      -> motion policy -> accessible alternative -> semantic feedback
      -> device/performance proof

This page is the design contract for the [SwiftUI animation and transition deep
dive](../42-framework-deep-dives/78-swiftui-animation-motion-transitions-and-feedback.md).
It also builds on the [interaction and transition cookbook](07-interaction-and-transition-cookbook.md),
[functional Liquid Glass interactions](../20-liquid-glass/05-functional-glass-interactions.md),
and [state ownership and native lifecycle design](105-state-ownership-and-native-lifecycle-design.md).

## Motion hierarchy

Use the least complex motion that explains the change:

| Design question | Preferred route | Example |
| --- | --- | --- |
| Did a value change in place? | State animation or content transition | A count or selection label |
| Did a view enter or leave? | Transition | A validation message or optional action |
| Is the same object represented elsewhere? | Matched geometry | Compact card to detail header |
| Does one short action need multiple beats? | PhaseAnimator | A bounded symbol response |
| Does the visual itself need independent tracks? | KeyframeAnimator | A composed, short illustration |
| Does a touch or result deserve tactile confirmation? | Sensory feedback | Selection, alignment, success, error |
| Do nearby glass shapes belong together? | GlassEffectContainer and glass IDs | A compact glass action group |
| Is motion only decoration? | Remove or make it optional | Repeating background shimmer |

Standard controls, navigation containers, sheets, toolbars, and system surfaces
already provide platform-appropriate feedback. A custom animation should earn
its place by improving comprehension, not by making every tap feel animated.

## Design the state chart before the effect

For a native screen that uses Liquid Glass and on-device AI, design the
semantic state chart first:

| State | What the person needs to know | Visual treatment | Motion |
| --- | --- | --- | --- |
| Ready | What can be started and what input it uses | Standard prominent control, concise source context | System control feedback |
| Generating | Work is in progress and can be canceled | Progress/status with stable source context | Optional subtle, nonessential phase |
| Proposal | Output is generated and needs review | Source and candidate in a clear review group | Content replacement or glass materialization |
| Applying | Which side effect is being performed | Explicit scope and duplicate-submit protection | Short progress/transition if useful |
| Saved | What changed and where it lives | Durable result, revision, undo or next action | Brief semantic feedback |
| Refused/unavailable | Why the route cannot run and what to do next | Manual fallback and explanation | No celebratory motion |
| Failed/stale | What did not complete and whether retry is safe | Recovery action and preserved source | Identity or opacity route |

The model may produce a candidate; it does not decide the transition to saved.
The domain operation does. This keeps a visual AI progress state honest and
testable.

## Native motion tokens

Do not begin with a catalog of durations and curves detached from meaning.
Create semantic tokens that can be changed by platform, accessibility, and
feature policy:

| Token | Normal behavior | Reduced-motion behavior |
| --- | --- | --- |
| controlResponse | Small, direct response to a tap or selection | System response or no custom animation |
| stateReveal | Short reveal of newly available content | Opacity or immediate layout |
| objectRelocation | Geometry link for the same object | Fade or stable destination |
| stagedEmphasis | Two or three discrete phases, then stop | One short state change |
| contentUpdate | Numeric/interpolated replacement when meaningful | Immediate value update |
| completionFeedback | Visual result plus optional sensory feedback | Visual/text result remains |
| backgroundAmbience | Only when it supports context | Static surface |

Keep token values in a feature-level policy or design system rather than
scattering unrelated animation literals through every view. The policy should
be able to return no animation when Reduce Motion or a power-saving mode is
active.

## Choose the right SwiftUI seam

Use withAnimation for a state mutation where several related view values should
move together. Use animation(_:value:) to keep the scope local to a view and a
specific Equatable value. Use a transaction modifier when a subtree should
disable or replace inherited animation.

Use a transition only when a view is inserted or removed. Use
contentTransition when the same view changes its content. Use
matchedGeometryEffect when two views represent one meaningful visual object,
and remember that the modifier synchronizes geometry but does not choose the
rendering transition.

Use PhaseAnimator for discrete phases with a clear end or controlled cycle.
Use KeyframeAnimator only when independently timed tracks add real meaning.
Keep the keyframe content closure lightweight because SwiftUI updates it every
frame.

Use sensoryFeedback for semantic events. A success response belongs after the
domain action succeeds, not after a button is tapped.

## Liquid Glass composition

Liquid Glass should organize controls and hierarchy:

- use standard system controls and styles first;
- apply custom glass to a small number of meaningful groups;
- use a GlassEffectContainer for related glass effects;
- assign stable glass IDs within a Namespace when the same shape should morph;
- choose matchedGeometry for nearby related shapes;
- choose materialize when content is farther away or geometry matching would
  suggest a false relationship;
- use identity for a reduced-motion or no-effect route;
- let container spacing express which shapes can blend;
- keep text, labels, and hit regions semantic and independent of the glass;
- test reduced transparency and increased contrast so the material cannot erase
  hierarchy.

An AI review shell can use a glass group around source, proposal, and review
actions. It should not use a glass morph to suggest that accepting an output
already changed the underlying record.

## Accessibility motion contract

Read the system Reduce Motion preference. When it is enabled:

- remove large scale, depth, parallax, and peripheral movement;
- tighten or remove bounce;
- prefer fades or stable layout over x-, y-, and z-axis relocation;
- avoid animating into or out of blur;
- stop repetitive automatic phases unless they are essential and have a
  static equivalent;
- do not auto-play animated images when the system setting says not to;
- keep progress, loading, success, failure, and unavailable states distinct
  through text, structure, shape, or accessible value;
- let people continue, cancel, or revisit the action without waiting for the
  animation;
- preserve focus order and VoiceOver meaning at the end of every transition.

Motion is not the only accessibility gate. Check Dynamic Type, reduced
transparency, increased contrast, Differentiate Without Color, VoiceOver,
Voice Control, Switch Control, keyboard/pointer input, localization, and
Assistive Access where relevant.

## Feedback design

Use a multimodal result:

    visible state + accessible label/value + optional haptic/audio

Suggested semantic mapping:

| Event | Visual | Accessibility | Optional feedback |
| --- | --- | --- | --- |
| Selection | Selected treatment and value | Selected state/value | selection |
| Start | Progress/status | Activity started | start |
| Cancel | Idle/canceled status | Cancellation result | stop only if it clarifies |
| Successful commit | Saved state and next action | Saved result/revision | success |
| Rejection/error | Error copy and recovery | Error and action | warning/error |
| Threshold crossing | Value and boundary | Updated value | increase/decrease/levelChange |
| Spatial alignment | Visible alignment | Position/state description | alignment/impact |

Never rely on a haptic, color change, animation, or sound alone. Use Core
Haptics only when a custom pattern is worth its engine and device lifecycle;
otherwise SwiftUI’s semantic sensory feedback is usually the smaller route.

## On-device AI progress without theater

Model requests are asynchronous and availability-sensitive. The design should
make each phase inspectable:

    request input -> availability gate -> generating
      -> candidate/refusal/error -> review
      -> validate -> apply -> saved or failed

Good progress:

- says what the device is doing in plain language;
- includes a cancel path when the operation is cancellable;
- does not claim completion because an animation finished;
- preserves the original source;
- explains model unavailability, unsupported input, refusal, or timeout;
- displays generated content as a candidate until accepted;
- records model/profile/schema/prompt version where it matters;
- falls back to manual entry or a deterministic route.

Avoid:

- an infinite shimmering glass surface while the operation is idle;
- a fake percentage whose value is not tied to measured work;
- a success haptic before the record is committed;
- a transition that hides a validation error;
- a generated sentence presented as a fact without review or provenance;
- a cancel button that stops the spinner but not the underlying task.

For a long operation, pair a real progress estimate or stage with a stable
status. A phase animation can make the waiting state less abrupt, but it is not
the progress source.

## Performance-oriented design

Design for the heaviest plausible state, not the empty canvas:

- long strings and large Dynamic Type;
- large images or model output;
- multiple simultaneous glass effects;
- a list or grid during scroll/drag;
- repeated trigger changes;
- background/foreground and cancellation;
- older supported devices and thermal pressure.

Keep expensive computation out of keyframe content and other per-frame paths.
Avoid broad animation modifiers that cause unrelated content to move. Prefer
stable layout and state-driven invalidation. Use the Animation Hitches
instrument and a repeatable workload before declaring motion smooth.

Record:

    app build + SDK + device + OS + fixture + thermal state
      + animation trigger + motion setting + hitch/latency evidence

A screenshot proves appearance at one instant. It does not prove frame
cadence, thermal behavior, accessibility task completion, or haptic output.

## Design review checklist

- Is every animation tied to a state relationship or user action?
- Can the screen explain the result with motion disabled?
- Does the transition preserve semantic identity and focus?
- Is the animation scoped to the smallest affected subtree?
- Does the AI state distinguish unavailable, generating, proposal, applying,
  saved, failed, and canceled?
- Are haptics optional and delayed until the meaningful result?
- Does the Liquid Glass group use stable IDs and a deliberate container?
- Is the reduced-transparency route legible?
- Is the keyframe/phase closure cheap and bounded?
- Has the heaviest fixture been run on a real device?
- Are hitches and accessibility results recorded separately?

## Sources

- [Motion](https://developer.apple.com/design/human-interface-guidelines/motion)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Animations](https://developer.apple.com/documentation/swiftui/animations)
- [Controlling the timing and movements of your animations](https://developer.apple.com/documentation/SwiftUI/Controlling-the-timing-and-movements-of-your-animations)
- [Transaction](https://developer.apple.com/documentation/swiftui/transaction)
- [Transition](https://developer.apple.com/documentation/swiftui/transition)
- [ContentTransition](https://developer.apple.com/documentation/swiftui/contenttransition)
- [matchedGeometryEffect(id:in:properties:anchor:isSource:)](https://developer.apple.com/documentation/swiftui/view/matchedgeometryeffect%28id%3Ain%3Aproperties%3Aanchor%3Aissource%3A%29)
- [PhaseAnimator](https://developer.apple.com/documentation/swiftui/phaseanimator)
- [KeyframeAnimator](https://developer.apple.com/documentation/swiftui/keyframeanimator)
- [SensoryFeedback](https://developer.apple.com/documentation/swiftui/sensoryfeedback)
- [accessibilityReduceMotion](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [GlassEffectTransition](https://developer.apple.com/documentation/swiftui/glasseffecttransition)
- [Understanding hitches in your app](https://developer.apple.com/documentation/xcode/understanding-hitches-in-your-app)
- [Improving app responsiveness](https://developer.apple.com/documentation/xcode/improving-app-responsiveness)
