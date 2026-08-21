# Interaction and Transition Cookbook

## Purpose

Motion is part of the interaction contract. It should explain what changed, preserve context, confirm an important result, or help a person follow a transition. It should never be the only way to communicate meaning, and it should not make a frequent action slower just to look impressive.

Use this sequence for every animated or tactile interaction:

`user intent -> state change -> visible feedback -> optional sensory feedback -> interruption/cancellation -> reduced-motion equivalent -> proof`

The cookbook covers SwiftUI interaction families that commonly appear in Liquid Glass interfaces: state animation, insertion/removal, content replacement, scroll transitions, focus and keyboard movement, sensory feedback, safe-area bars, gesture cancellation, and glass identity. It does not replace the current SDK headers or HIG pages.

## Motion principles

### Give motion a job

Name the user-visible change before choosing an effect:

| State change | Useful motion route | Equivalent without motion |
| --- | --- | --- |
| Expand/collapse | A short transition that preserves the trigger’s spatial relationship | The new content appears with stable hierarchy and focus |
| Insert/remove | A built-in or small custom transition | Immediate insertion/removal with a visible status update |
| Save/fail | Brief state change plus text/accessibility status; optional success/error feedback | The status text, value, or icon changes immediately |
| Scroll into view | A controlled scroll position or focus move | The target is selected and clearly announced |
| Drag/reorder | Gesture-tracked movement and an alignment/selection cue | A static preview or explicit reorder action |
| Glass shape change | Stable `glassEffectID` inside a related container | Crossfade or immediate layout change that keeps labels and actions clear |

If the user cannot understand the result with animation disabled, the interaction contract is incomplete.

### Prefer system behavior

Standard SwiftUI controls, navigation containers, sheets, toolbars, and system surfaces already provide platform-appropriate feedback. Avoid wrapping every tap in a custom scale animation or adding custom backgrounds to standard bars. Use custom motion only when it explains a product-specific state or relationship that the system component cannot express.

### Keep feedback proportional

Use brief, precise feedback for frequent actions. A primary action should remain cancellable or interruptible where possible. Never block an urgent action behind an animation, and do not require a person to wait for a decorative transition before they can continue.

### Make feedback multimodal

Pair color with text or shape, sound with visual state, and haptics with a visible or accessible result. Haptics are unavailable, adjustable, or inappropriate in some contexts; they cannot be the sole confirmation. Error and success states must remain understandable to VoiceOver, Voice Control, Switch Control, keyboard users, and people who reduce motion.

## Route 1: state-scoped animation

### Use it when

A user action changes a value that should animate as a coherent state update: expanding a section, selecting an item, showing a progress state, or changing a control’s visual state.

### Decision

- Use `withAnimation` around the state mutation when the resulting view changes should move together.
- Use `animation(_:value:)` when only a specific view subtree should react to one Equatable value.
- Keep the state mutation authoritative. The animation is not the save operation, network request, model generation, or permission result.
- Select `nil` or an identity transition when Reduce Motion is enabled, unless a minimal motion is still explicitly appropriate and tested.

### Failure modes

- An animation is attached to a broad container and unrelated content moves.
- The same state value drives both a durable operation and a visual flourish, so a failed operation looks successful.
- A button can be tapped repeatedly while the animation is in flight and starts duplicate work.
- A long or bouncy animation prevents the next action.

### Proof

Test normal motion, Reduce Motion, rapid taps, cancellation, background/foreground, failed persistence, and VoiceOver announcements. Verify that a state change remains clear if the animation is removed.

## Route 2: insertion, removal, and content replacement

Use insertion/removal transitions for an actual hierarchy change, not to hide a layout jump. Keep stable identity for repeated content, and do not use a transition that resets a child’s state through `.id`, `if`, or `switch` changes inside the transition itself.

Use a content transition when the same view remains present but its displayed content changes, such as a number, symbol, or text representation. The transition must not replace a meaningful label or value.

For Liquid Glass, use `glassEffectTransition` when a custom glass view is added or removed and the effect should materialize or match a related effect. A glass transition does not replace semantic identity, domain model identity, navigation identity, or accessibility state.

## Route 3: scroll transitions

### Use it when

Content entering or leaving a scroll viewport benefits from a restrained cue, such as a horizontal browse row or a focused card carousel. Do not apply dramatic scale/opacity changes to essential text or controls that people need to scan.

### Safe pattern

- Leave the visible/identity phase at the normal readable appearance.
- Use small changes outside the visible region; avoid making content disappear before it is reachable.
- Keep selection and activation independent from scroll position.
- Test with Reduce Motion, large text, VoiceOver, keyboard, pointer, and reduced transparency.
- Do not use a scroll transition to conceal loading, unavailable, or error states.

`ScrollTransitionPhase.value` can be used to derive a restrained effect, but the value is an animation input—not a user-facing state. Keep the semantic content and action available in every phase.

## Route 4: focus, keyboard, and command flow

Focus is a navigation state. Use `FocusState` to move people to the field that needs attention, to advance through a form, or to dismiss the keyboard after a completed action. Do not move focus unexpectedly while a person is reading or typing.

### Focus rules

- Define a small, stable enum for fields rather than using arbitrary strings or view indices.
- Move focus when the person submits, requests correction, or starts a clearly defined flow.
- Preserve draft text when focus changes or the keyboard appears/disappears.
- Use visible labels and submit labels; focus is not a substitute for hierarchy.
- Test hardware keyboard, VoiceOver, Voice Control, Switch Control, pointer input, and Dynamic Type.

### Keyboard and safe area

The keyboard is part of the layout environment. Let scrollable content respond to the keyboard safe area, and apply `ignoresSafeArea` only to the background or region that genuinely should extend behind it. A custom bottom action bar must add to the safe area so content and the keyboard do not cover each other.

## Route 5: sensory feedback

SwiftUI’s `sensoryFeedback` route can associate feedback with a changing trigger. Choose the feedback by meaning: selection for a meaningful selection change, success for completion, warning/error for an actual outcome, and impact for a physical boundary. Do not emit feedback for every state update or use success feedback before durable work succeeds.

### Sensory decision table

| Event | Appropriate cue | Required visible/accessibility state |
| --- | --- | --- |
| Selection changes | Selection feedback when the change matters | Selected state, label/value, and focus remain clear |
| Save succeeds | Success feedback, if appropriate | Saved state or status message after the operation returns success |
| Save fails | Error feedback, if appropriate | Error copy, recovery action, and preserved draft |
| Boundary reached | Impact/alignment feedback during a meaningful interaction | Visual boundary or value change |
| Background refresh begins | Usually no tactile feedback | Visible freshness/loading state if the app is open |

Test silent mode, unsupported hardware, user settings, rapid changes, and VoiceOver. Core Haptics remains a separate route for custom patterns; use it only when the product needs a pattern that standard feedback cannot express and record the engine/device boundary.

## Route 6: safe-area bars and edge controls

Use `toolbar`, `safeAreaBar`, or `safeAreaInset` for controls that belong at an edge. These APIs communicate the relationship between the control and the content, adjust the content’s safe area, and let the system manage bars and scrolling more coherently than a manually positioned overlay.

### Edge-control checklist

- Does the action need to remain visible while content scrolls?
- Is it a single primary action or a small related group?
- Does the bar remain readable over light, dark, colorful, and text-heavy content?
- Does it make room for the keyboard and sheet corners?
- Does it remain discoverable with large text, VoiceOver, and reduced transparency?
- Would a normal toolbar or system button already express the relationship?

If a custom edge bar uses Liquid Glass, treat it as a functional surface. Do not make the bar a full-width decorative backdrop or cover content without adding the appropriate safe-area space.

## Route 7: gesture tracking and cancellation

Gestures can start asynchronous work that outlives the gesture. Decide whether work is continuous, throttled, debounced, cancellable, or committed on release.

| Interaction | State to define | Cancellation question |
| --- | --- | --- |
| Drag to reorder | Provisional position, committed order | What happens when the drag is cancelled or the item leaves the target? |
| Pull to refresh | Refreshing, refreshed, failed | Can the refresh be cancelled or superseded? |
| Long press | Recognized, cancelled, completed | Does a second input or VoiceOver route exist? |
| Camera/audio/model stream | Running, paused, stopped, failed | What stops work when the view disappears or permission changes? |
| Swipe action | Revealed, committed, undone | Is there a visible undo route and a durable result? |

Use `Task` cancellation, service-level cancellation, and lifecycle handlers where the underlying framework supports them. A view disappearing is not proof that a camera, audio engine, model session, or network request stopped; verify the service boundary.

## Route 8: Liquid Glass identity and morphing

Use a `GlassEffectContainer` for a small set of related custom glass effects. Give related effects stable `glassEffectID` values in a `Namespace`, choose `glassEffectTransition` deliberately, and animate the state change that changes the hierarchy.

### Glass identity rules

- IDs describe the visual relationship, not the array index or a random UUID generated on every render.
- A glass ID does not replace `Identifiable` domain data or accessibility identifiers.
- The container should group semantically related controls, not an entire screen.
- Match geometry only when the source and destination are meaningfully the same control or surface.
- Use a materialize or identity route when geometry matching would imply a relationship that does not exist.
- Test insertion/removal, rapid state changes, Reduce Motion, VoiceOver, reduced transparency, and performance on target hardware.

## Accessibility and reduced-motion gate

For every custom interaction, answer all of these:

- What does VoiceOver announce before, during, and after the state change?
- Can a person complete it without a custom gesture or timing-dependent animation?
- Does Reduce Motion remove or simplify the movement while preserving hierarchy and result?
- Does Reduce Transparency keep text and controls legible if material becomes opaque?
- Does Increased Contrast preserve distinction between selected, disabled, loading, and error states?
- Does Dynamic Type change the geometry without clipping the control or pushing the action off-screen?
- Do haptics and audio supplement, rather than replace, visible and accessible feedback?

## Verification matrix

| Evidence level | What to exercise for interaction work | Boundary |
| --- | --- | --- |
| Source review | Current Apple HIG Motion/Feedback, SwiftUI animation, transition, focus, safe-area, sensory, scroll, and Liquid Glass pages | Does not prove the selected SDK compiles the route |
| Preview | Normal/reduced motion, light/dark, large text, empty/error/loading, long strings | Does not prove real gestures, haptics, permissions, or device material performance |
| UI test/simulator | Navigation, focus, keyboard, cancellation, state transitions, accessibility identifiers, localization fixtures | Does not prove physical sensors, tactile feedback, thermal behavior, or every device family |
| Physical device | Touch/pointer, keyboard, haptics, safe areas, scroll feel, glass rendering, rapid updates, battery/thermal spot check | Does not prove production scale, App Store review, or unsupported devices |

## Sources

- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Motion](https://developer.apple.com/design/human-interface-guidelines/motion)
- [Feedback](https://developer.apple.com/design/human-interface-guidelines/feedback)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles)
- [Animations](https://developer.apple.com/documentation/swiftui/animations)
- [Animation](https://developer.apple.com/documentation/SwiftUI/Animation)
- [animation(_:value:)](https://developer.apple.com/documentation/swiftui/view/animation%28_%3Avalue%3A%29)
- [Transition](https://developer.apple.com/documentation/swiftui/transition)
- [TransitionPhase](https://developer.apple.com/documentation/swiftui/transitionphase)
- [Scroll views](https://developer.apple.com/documentation/swiftui/scroll-views)
- [ScrollTransitionPhase](https://developer.apple.com/documentation/swiftui/scrolltransitionphase)
- [ScrollPosition](https://developer.apple.com/documentation/swiftui/scrollposition)
- [FocusState](https://developer.apple.com/documentation/SwiftUI/FocusState)
- [SensoryFeedback](https://developer.apple.com/documentation/swiftui/sensoryfeedback)
- [sensoryFeedback(trigger:_:)](https://developer.apple.com/documentation/swiftui/view/sensoryfeedback%28trigger%3A_%3A%29)
- [SafeAreaRegions](https://developer.apple.com/documentation/swiftui/safearearegions)
- [safeAreaInset(edge:alignment:spacing:content:)](https://developer.apple.com/documentation/swiftui/view/safeareainset%28edge%3Aalignment%3Aspacing%3Acontent%3A%29)
- [safeAreaBar(edge:alignment:spacing:content:)](https://developer.apple.com/documentation/swiftui/view/safeareabar%28edge%3Aalignment%3Aspacing%3Acontent%3A%29)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [glassEffectID(_:in:)](https://developer.apple.com/documentation/swiftui/view/glasseffectid%28_%3Ain%3A%29)
- [GlassEffectTransition](https://developer.apple.com/documentation/swiftui/glasseffecttransition)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/SwiftUI/Applying-Liquid-Glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [accessibilityReduceMotion](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion)
- [accessibilityReduceTransparency](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducetransparency)
- [Core Haptics](https://developer.apple.com/documentation/corehaptics)
