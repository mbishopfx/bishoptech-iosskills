---
name: swiftui-native-design
description: Design, review, or implement native SwiftUI iOS screens and flows with adaptive state, accessibility, previews, and evidence-bound verification.
metadata:
  short-description: Build native SwiftUI interfaces
---

# SwiftUI Native Design

Use this skill when the requested work changes a SwiftUI screen, component, navigation flow, preview matrix, interaction model, or accessibility behavior. It is for Apple-native implementation and review, not for copying Apple branding or reproducing a screenshot without understanding the product behavior.

## Read before acting

Inspect the target project before proposing architecture or edits:

- locate the actual `.xcodeproj`, `.xcworkspace`, package manifest, app target, deployment target, and existing module boundaries;
- find the current root view, navigation model, state/observation approach, assets, supplied copy, and any UIKit or platform-specific bridge;
- read the relevant pages in the [knowledge-base map](../../../README.md), especially [SwiftUI mental model](../../../10-swiftui/00-swiftui-mental-model.md), [state and observation](../../../10-swiftui/01-state-observation-and-data-flow.md), [layout, typography, and controls](../../../10-swiftui/02-layout-typography-and-controls.md), [navigation and routing](../../../10-swiftui/03-navigation-and-routing.md), and [accessibility](../../../10-swiftui/05-accessibility-and-adaptable-ui.md);
- refresh the official [SwiftUI](https://developer.apple.com/documentation/swiftui/), [managing user interface state](https://developer.apple.com/documentation/swiftui/managing-user-interface-state), [navigation](https://developer.apple.com/documentation/swiftui/navigation), [accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals), and [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/) pages when an API or behavior is version-sensitive.

Do not begin with decorative styling. First identify the user outcome, route, state owner, domain data, system surface, and failure states.

## Implementation route

1. Define the screen contract: entry route, user intent, domain truth, derived presentation state, and exit/commit action.
2. Model the meaningful states before styling: initial, loading, empty, success, validation, permission denied, unavailable, error, and cancellation where applicable.
3. Prefer standard SwiftUI containers, controls, navigation, semantic colors, system typography, and platform behaviors. Use custom drawing only when it expresses a real product need that the system control cannot express.
4. Make layout adaptive across Dynamic Type, orientation, split views, iPad, Mac Catalyst where in scope, localization, and content length. Avoid fixed phone-width assumptions.
5. Add motion and haptics only to clarify state or confirm an action. Respect reduced-motion and reduced-effects settings.
6. Treat accessibility as part of the component contract: labels, values, hints, traits, reading order, focus, actions, contrast, hit targets, and VoiceOver behavior.
7. Create previews or fixture-driven tests for representative states, including long text, empty data, errors, and accessibility-sensitive variants.
8. Implement the smallest coherent slice, preserve the target project’s architecture, and compile/test the target when the user asked for implementation.

## Change boundary

May inspect the project files, assets, target settings, and existing UI needed for the requested surface. May change the named SwiftUI views, supporting state models, previews, tests, and directly related resources. Do not add a backend, package dependency, account flow, permission, entitlement, or broad redesign unless the route requires it and the request authorizes it.

## Refuse to assume

- a single fixed device width represents iOS;
- a screenshot or simulator preview proves accessibility, performance, sensors, model availability, or physical-device interaction;
- a custom control is better than a standard system control;
- a remembered API name is available in the target SDK;
- an Apple-like result requires copying Apple screens, icons, wording, or branding;
- visual polish makes an unmodeled loading, permission, or error state acceptable.

## Completion evidence

Report separately:

- files changed and the architecture boundary;
- native component and state decisions, including rejected alternatives when useful;
- preview/fixture and accessibility coverage;
- compiler, unit/UI test, simulator, and physical-device evidence, naming the exact target and OS when available;
- remaining release, entitlement, permission, performance, or device checks.

If no project build was run, say the result is documentation/design guidance rather than compiled proof. If no physical device was used, do not claim hardware or device-only behavior.

## Related knowledge-base routes

- [SwiftUI code and Liquid Glass recipes](../../../70-code-recipes/00-swiftui-and-liquid-glass-recipes.md)
- [Apple-native design deep dives](../../../21-design-deep-dives/README.md)
- [Accessibility and adaptability checklist](../../../60-verification/02-accessibility-and-adaptability-checklist.md)
- [Build, device, and release checklist](../../../60-verification/01-build-device-and-release-checklist.md)

## Sources

- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Managing user interface state](https://developer.apple.com/documentation/swiftui/managing-user-interface-state)
- [Navigation](https://developer.apple.com/documentation/swiftui/navigation)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
