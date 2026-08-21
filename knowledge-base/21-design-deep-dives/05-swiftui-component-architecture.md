# SwiftUI Component Architecture

## Capability

SwiftUI components should make product intent visible while keeping state ownership, side effects, styling, and platform adaptation testable. A design system is useful when it reduces repeated decisions; it becomes harmful when it hides the platform’s semantic controls behind an untraceable abstraction layer.

## Layer the feature

Use a small, explicit boundary between:

1. **Domain** — models, rules, validation, and user outcomes.
2. **Services** — persistence, network, device/framework access, AI, and system routes.
3. **Feature state** — loading, permission, error, draft, and navigation state.
4. **SwiftUI views** — layout, semantic controls, presentation, and accessibility.
5. **Style/components** — reusable visual decisions that do not own product side effects.

Views can trigger an intent or service operation, but they should not become the database, camera session, model session, or entitlement authority.

## State ownership

Keep state at the lowest common ancestor that needs to coordinate it. Use bindings to express a child’s controlled edit, environment values for shared dependencies/context, and Observation/SwiftData mechanisms where their lifecycle fits. State is not persistence: write durable data through a deliberate model/service boundary.

## Component recipe

For every reusable component, document:

- semantic purpose and when not to use it;
- required inputs and bindings;
- loading, empty, error, disabled, and unavailable states;
- accessibility label/value/traits and focus behavior;
- Dynamic Type, localization, color scheme, and Reduce Motion behavior;
- Liquid Glass/material policy;
- preview fixtures and a UI-test entry point;
- whether the component may trigger a side effect.

Prefer composition of standard `Button`, `Label`, `Toggle`, `NavigationLink`, `List`, `Form`, `ToolbarItem`, `Sheet`, and `ScrollView` behaviors. Add a custom style or modifier when the semantic behavior remains intact.

## Environment and dependencies

Inject repositories, clocks, UUID generators, model containers, and AI services through explicit initializers or environment values. Previews should use deterministic in-memory fakes. Avoid hidden global singletons that make permission, persistence, and model availability impossible to test.

## Preview route

Build previews for:

- normal and large Dynamic Type;
- light/dark and high-contrast appearance;
- empty/loading/error/success states;
- long localized content;
- compact and regular width;
- unavailable permission/model/device states;
- Liquid Glass effects over representative backgrounds.

Previews prove rendering for the supplied state. They do not prove camera hardware, real model availability, entitlements, StoreKit, background execution, or production network behavior.

## Verification route

- Keep domain logic unit-testable without SwiftUI.
- Test component semantics and accessibility, not only screenshots.
- Inspect state transitions under cancellation, duplicate taps, and view recreation.
- Use Instruments/diagnostics for expensive body updates and framework work.
- Re-check the architecture when a component starts accumulating unrelated flags or side effects.

## Sources

- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Managing user interface state](https://developer.apple.com/documentation/swiftui/managing-user-interface-state)
- [Observation](https://developer.apple.com/documentation/observation)
- [View fundamentals](https://developer.apple.com/documentation/swiftui/view-fundamentals)
- [Picking container views for your content](https://developer.apple.com/documentation/swiftui/picking-container-views-for-your-content)
- [Previews in Xcode](https://developer.apple.com/documentation/swiftui/previews-in-xcode)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
