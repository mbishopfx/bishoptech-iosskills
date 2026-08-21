---
name: ios-native-design-verification
description: Design, implement, or review Apple-native SwiftUI and iOS 26 Liquid Glass surfaces with adaptive layout, semantic controls, accessibility, purposeful motion, and evidence-bound visual verification. Use when a screen should feel native without copying Apple branding or relying on screenshots alone.
---

# iOS Native Design and Liquid Glass Verification

Use this skill to make an original product feel at home on Apple platforms through hierarchy, system components, semantic typography, adaptive composition, accessibility, and restrained material/motion decisions.

`user outcome -> hierarchy/state -> native route -> adaptive interaction -> accessibility/reduced effects -> preview/fixture audit -> device proof`

## Read before acting

- Inspect the actual Xcode target, deployment target, platform/device family, scene/lifecycle model, root view, navigation, state/observation model, assets, supplied copy, localization, and existing UIKit bridges.
- Read the [knowledge-base map](../../../README.md), [SwiftUI mental model](../../../10-swiftui/00-swiftui-mental-model.md), [state and observation](../../../10-swiftui/01-state-observation-and-data-flow.md), [layout, typography, and controls](../../../10-swiftui/02-layout-typography-and-controls.md), [navigation and routing](../../../10-swiftui/03-navigation-and-routing.md), [accessibility and adaptable UI](../../../10-swiftui/05-accessibility-and-adaptable-ui.md), and [Liquid Glass principles](../../../20-liquid-glass/00-liquid-glass-principles.md).
- Read [system-first Liquid Glass adoption](../../../20-liquid-glass/01-system-first-adoption.md), [custom glass effects](../../../20-liquid-glass/02-custom-glass-effects.md), [glass containers and morphing](../../../20-liquid-glass/03-glass-containers-and-morphing.md), and the [native screen/design recipes](../../../20-liquid-glass/04-native-screen-recipes.md).
- Refresh the exact official SwiftUI, Liquid Glass, accessibility, and Human Interface Guidelines pages in the Sources section before relying on an API, iOS 26 behavior, material effect, availability annotation, or accessibility convention.

## Design workflow

1. State the user outcome, entry/exit route, primary action, domain truth, derived presentation state, and meaningful loading/empty/validation/permission/error/cancel states. Do not begin with a screenshot or material.
2. Establish hierarchy: content first, functional controls second, navigation/system surfaces third, decorative treatment last. Preserve the target app’s supplied copy, assets, product identity, and scope.
3. Prefer the narrowest native route: `NavigationStack`/`NavigationSplitView`, standard controls, semantic colors, system typography, toolbars, sheets, lists, forms, search, and platform behaviors before custom drawing or custom controls.
4. Keep system-managed bars and controls system-managed. Use Liquid Glass system adoption when the OS supplies the treatment; use custom `glassEffect` only for a genuinely functional custom element that a standard control cannot express.
5. Group related glass elements with `GlassEffectContainer` only when grouping or morphing communicates a real semantic relationship. Give morphing participants stable, meaningful identity; do not animate incidental layout changes or turn every surface into translucent decoration.
6. Make layout adaptive across Dynamic Type, localization/content length, orientation, split views, iPad, Mac Catalyst or other in-scope destinations, safe areas, keyboard, and compact/regular size classes. Avoid fixed phone-width assumptions.
7. Treat accessibility as a component contract: semantic control role, label/value/hint, reading order, grouping, focus, actions, contrast, hit region, VoiceOver result, captions/text alternatives, and a non-gesture/non-color path for core actions.
8. Add motion, morphing, and haptics only when they explain state, spatial identity, or action confirmation. Provide reduced-motion/reduced-effects behavior and preserve the task when animation is skipped or interrupted.
9. Build a preview/fixture matrix for long text, empty/loading/error states, dark/light appearance, large text, right-to-left or localized strings where in scope, reduced motion/transparency, high contrast, split view, and compact width. A preview is design evidence, not physical-device proof.
10. Verify the real target on representative physical devices. Record OS build, device, text size, appearance, accessibility settings, interaction route, scroll/hit behavior, transition interruption, haptic result, material legibility, performance, and remaining release gaps.

## Native and Liquid Glass boundaries

- Apple-native does not mean copying Apple screens, icons, wording, proprietary branding, or a screenshot. Preserve an original product hierarchy while using the platform’s semantic components and conventions.
- A blur, opacity, gradient, or generic material is not automatically Liquid Glass. Record which behavior is system-provided and which is custom so SDK changes can be rechecked.
- Glass is a functional layer above content, not a substitute for hierarchy or contrast. Keep text and controls readable over changing backgrounds; never make translucency, color, blur, or motion the only carrier of meaning.
- Custom controls must expose the same semantic role, focus/action behavior, hit target, keyboard/controller path, and accessibility value as the native control they replace. Prefer a native control when it fits.
- Animation is state-scoped and cancellable. The destination state must remain understandable when Reduce Motion is enabled, a transition is interrupted, content loads slowly, or a device cannot provide the desired effect.
- Haptic feedback confirms a user action; it does not replace visible or spoken feedback and must have a graceful no-hardware/no-preference path.

## Verification matrix

| Surface | Check | Evidence boundary |
| --- | --- | --- |
| Hierarchy/navigation | Primary action, back behavior, sheet/toolbar semantics, loading/error/empty routes | A screenshot cannot prove state ownership or a complete navigation path. |
| Liquid Glass | System bars retained, custom glass justified, grouping/identity stable, content legible behind material | Preview/simulator cannot prove all physical contrast, performance, or OS-version behavior. |
| Adaptation | Dynamic Type, localization, split view, orientation, keyboard, long content, compact width | One device size or one language is not coverage. |
| Accessibility | VoiceOver labels/actions/focus, contrast, hit targets, captions, non-color/non-gesture alternatives, Reduce Motion/Effects | Static visual review cannot prove assistive technology behavior. |
| Interaction | Scroll, gesture cancellation, focus, keyboard/controller, haptic availability, transition interruption | A successful tap in a preview is not physical ergonomics or completion proof. |
| Release | Actual SDK availability, performance, system surface, signing, and supported device matrix | Documentation guidance does not prove the app compiles, passes review, or works in production. |

## Deliverable

Produce a compact design note or implementation change containing:

- user outcome, hierarchy, native component choices, state matrix, and rejected alternatives;
- system-provided versus custom Liquid Glass boundary, grouping/identity, and fallback;
- adaptive layout, localization, Dynamic Type, accessibility, reduced motion/effects, focus, gesture, and haptic behavior;
- preview/fixture matrix and exact compile, accessibility-inspection, simulator, physical-device, performance, signing, and release evidence;
- remaining `to-verify` gaps and claims deliberately not made.

For implementation, change only the requested screen/component and directly related state or preview fixtures. Do not globally restyle an app, replace system bars with custom glass, add a dependency, alter supplied copy/assets, or add analytics/permissions/entitlements without a stated product need and authorization.

## Related routes and recipes

- [SwiftUI native design package](../swiftui-native-design/SKILL.md)
- [Liquid Glass design package](../liquid-glass-design/SKILL.md)
- [Apple-native design deep dives](../../../21-design-deep-dives/README.md)
- [SwiftUI and Liquid Glass recipes](../../../70-code-recipes/00-swiftui-and-liquid-glass-recipes.md)
- [Accessibility, adaptation, and native design recipes](../../../70-code-recipes/12-accessibility-adaptive-and-native-design-recipes.md)
- [Interaction and transition recipes](../../../70-code-recipes/07-interaction-and-transition-recipes.md)
- [Accessibility and adaptability checklist](../../../60-verification/02-accessibility-and-adaptability-checklist.md)
- [Build, device, and release checklist](../../../60-verification/01-build-device-and-release-checklist.md)

## Sources

- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Managing user interface state](https://developer.apple.com/documentation/swiftui/managing-user-interface-state)
- [Navigation](https://developer.apple.com/documentation/swiftui/navigation)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/liquid-glass)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [Sensory feedback](https://developer.apple.com/documentation/swiftui/sensoryfeedback)
