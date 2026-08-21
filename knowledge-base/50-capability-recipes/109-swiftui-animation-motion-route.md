# SwiftUI animation and motion route

## Route contract

Use this route when a native iOS feature needs animation, transitions,
Liquid Glass morphing, tactile feedback, or bounded on-device AI progress.
Start from the semantic state change and select the smallest SwiftUI motion
primitive that expresses it.

This route does not claim that a code sketch compiles for every deployment
target or that a preview/simulator run proves physical performance,
accessibility, haptics, system delivery, or release readiness.

Related pages:

- [SwiftUI animation, motion, transitions, and feedback](../42-framework-deep-dives/78-swiftui-animation-motion-transitions-and-feedback.md)
- [Animation, motion, and Liquid Glass design](../21-design-deep-dives/106-animation-motion-and-liquid-glass-design.md)
- [SwiftUI animation and motion proof matrix](../60-verification/103-swiftui-animation-motion-proof-matrix.md)
- [SwiftUI animation and motion recipes](../70-code-recipes/121-swiftui-animation-motion-recipes.md)

## Route map

    user outcome
      -> semantic state chart
      -> motion family selection
      -> target SDK and availability gate
      -> scoped SwiftUI implementation
      -> Liquid Glass/accessibility policy
      -> AI progress and cancellation policy
      -> compile/UI/device/performance proof
      -> signed/release evidence

## Phase 0: name the state change

Write the before and after state in domain language:

| Question | Example |
| --- | --- |
| What changed? | A review proposal was accepted |
| Who owns it? | Review model and persistence service |
| What is visible? | The candidate becomes a saved record |
| What can be canceled? | The generation request, not a completed save |
| What should remain without motion? | Source, candidate, saved result, recovery action |
| What feedback is meaningful? | Success after the durable operation succeeds |

If the only description is “make it feel more Apple,” stop and identify the
task, hierarchy, or relationship the motion should clarify.

## Phase 1: choose the motion family

| If the feature does this | Select |
| --- | --- |
| Changes a value in an existing view | Animation or ContentTransition |
| Inserts/removes a view | Transition |
| Moves one meaningful object between representations | matchedGeometryEffect |
| Needs discrete beats | PhaseAnimator |
| Needs independently timed interpolated tracks | KeyframeAnimator |
| Needs semantic tactile/audio feedback | sensoryFeedback |
| Morphs related glass surfaces | GlassEffectContainer plus glass IDs and glass transition |
| Needs continuous drawing cadence or custom GPU rendering | TimelineView, Canvas, Metal, or another specialized route |

Prefer the normal Animation route first. A more powerful primitive should solve
a named coordination problem, not add incidental complexity.

## Phase 2: establish scope and identity

1. Put the state owner above every view that must respond.
2. Give the animation the smallest affected subtree.
3. Use stable IDs for data and visual identity.
4. Create a Namespace that outlives both sides of a geometry match.
5. Ensure one and only one matched-geometry source is active.
6. Keep insertion/removal identity separate from content updates.
7. Define the reduced-motion result before writing the normal effect.

For a glass group:

    related glass views -> one GlassEffectContainer
      -> stable glassEffectID values in Namespace
      -> matchedGeometry or materialize policy
      -> scoped withAnimation state change

Do not use a view ID or glass ID as a substitute for route identity, model
identity, authorization, or persistence.

## Phase 3: select transaction behavior

Decide whether the update needs:

- a shared Animation around one state mutation;
- a value-scoped animation on one view;
- an explicit transaction that disables inherited animation;
- a completion callback for presentation cleanup;
- no animation under Reduce Motion.

Document the completion meaning:

| Completion meaning | Correct owner |
| --- | --- |
| The visual is logically at its endpoint | Animation completion with logicallyComplete |
| The visual and removal tail are finished | Animation completion with removed |
| A record was saved | Domain operation |
| An AI request was canceled | Task/request identity and cancellation-aware service |
| A haptic should play | Result state or semantic trigger |

If a new state update can interrupt the animation, make cleanup safe when
completion is delayed or when an alternate state arrives first.

## Phase 4: add an accessibility policy

Use the system accessibilityReduceMotion value. Define a policy for:

- large scale, depth, and peripheral movement;
- repeated automatic phases;
- blur-in/blur-out effects;
- geometry relocation;
- image/symbol auto-play;
- focus and VoiceOver announcements;
- reduced transparency and increased contrast.

Example policy:

    normal -> spring/matched geometry/content transition
    reduced motion -> opacity/identity/static state
    reduced transparency -> opaque or standard material fallback
    increased contrast -> stronger semantic distinction

The reduced route must preserve the same task and information hierarchy.

## Phase 5: connect on-device AI honestly

Keep model availability and generated output outside the animation primitive:

    availability check -> request task -> generating
      -> typed candidate/refusal/error
      -> human review -> domain validation
      -> apply -> saved or failed

The animation can indicate that the view is in generating or proposal state.
It cannot invent a progress percentage, authorize an action, or commit a
record.

For cancellation:

1. cancel the view task or explicit model task;
2. make the underlying operation cooperative;
3. reject late results by request ID/revision;
4. update the visible state to canceled or idle;
5. do not play success feedback;
6. keep source content available.

For model unavailability, use a real manual or deterministic fallback instead
of leaving a glass loading surface running.

## Phase 6: implement Liquid Glass morphing

Use the system-first route:

1. start with standard controls and system containers;
2. identify a small related group that benefits from custom glass;
3. wrap related effects in GlassEffectContainer;
4. assign stable IDs in one Namespace;
5. select matchedGeometry for nearby related shapes;
6. select materialize for distant add/remove effects;
7. select identity for reduced motion or a no-effect fallback;
8. test spacing at rest and during insertion/removal;
9. reduce the number of effects if Instruments shows a rendering cost.

Do not put a full-screen duplicate glass shell inside a widget, control, or
other system-owned surface. The system surface owns its outer treatment.

## Phase 7: compile and availability gate

For the named app target:

- confirm the Xcode/SDK version and deployment target;
- check the current declaration and overload in that SDK;
- check platform and device availability;
- compile the smallest isolated view;
- include any required framework import;
- check that the target contains the source and any resources;
- add an availability fallback where the minimum target requires it;
- record whether the route is iOS-only or shared across platforms;
- do not call a beta or renamed API stable without a source and target check.

The documentation page is a source map. The target’s generated interface and
compiler are the final signature authority.

## Phase 8: proof packet

Build the evidence in layers:

| Layer | Evidence |
| --- | --- |
| Design | State chart, motion family decision, normal/reduced policy |
| Source | Official URLs, SDK/deployment record, API signature checked |
| Compile | Named target/build configuration and clean compile |
| UI | Insertion/removal, geometry, phase/keyframe, content, feedback state |
| Accessibility | Reduce Motion, Dynamic Type, contrast/transparency, VoiceOver and alternate input |
| Async | Cancellation, stale result, model unavailable/refusal, durable commit |
| Performance | Animation Hitches/Instruments fixture and device/build/thermal record |
| Physical | Supported device run for haptics, glass rendering, timing, and input |
| Release | Signed archive/TestFlight target/resource and privacy verification |

Do not promote a preview screenshot to a performance result or a simulator
animation to a haptic result.

## Phase 9: acceptance checklist

- [ ] The state change is named in domain language.
- [ ] Motion is scoped to the smallest meaningful subtree.
- [ ] The chosen primitive matches value, content, insertion, geometry, phase,
      keyframe, feedback, or glass meaning.
- [ ] The source and destination identities are stable.
- [ ] No domain commit is hidden in animation completion.
- [ ] AI progress is real, cancelable, and separate from presentation motion.
- [ ] Reduce Motion and reduced transparency routes preserve task completion.
- [ ] Text, actions, and accessible values remain meaningful without motion.
- [ ] Per-frame closures contain no expensive work.
- [ ] Glass effects are grouped, limited, and profiled.
- [ ] A named target compiles against the selected SDK.
- [ ] The required device/system/release proof has been recorded.

## Sources

- [Animations](https://developer.apple.com/documentation/swiftui/animations)
- [Animation](https://developer.apple.com/documentation/SwiftUI/Animation)
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
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [GlassEffectTransition](https://developer.apple.com/documentation/swiftui/glasseffecttransition)
- [Understanding hitches in your app](https://developer.apple.com/documentation/xcode/understanding-hitches-in-your-app)
