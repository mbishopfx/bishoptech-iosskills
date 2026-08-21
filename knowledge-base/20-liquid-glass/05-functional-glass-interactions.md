# Functional Liquid Glass Interactions

## Purpose

Use Liquid Glass to establish a functional layer for navigation and controls while keeping the content layer readable and product-specific. The goal is native hierarchy and responsive interaction, not a decorative glass card around every piece of content.

## Layer model

| Layer | Owns | Preferred treatment |
| --- | --- | --- |
| Content | Records, media, lists, charts, forms, editor text, empty/loading/error states | Solid or standard materials, semantic typography, clear contrast, content-specific color |
| Functional | Tab bars, sidebars, toolbars, transient controls, compact status/action clusters | System SwiftUI/UIKit controls; Liquid Glass supplied automatically or applied to a small related group |
| System | Sheets, menus, alerts, widgets, Live Activities, notifications, App Intents, share surfaces | System-owned presentation and interaction; configure the route rather than recreating it |

Apple’s HIG describes Liquid Glass as a distinct layer for controls and navigation. Do not move the entire content layer into custom glass just because the material is available. A transient slider, toggle, or control may use the interactive treatment when its function benefits from emphasis, but the background of a dense editor or dashboard should remain legible.

## System-first decision tree

1. Can a standard SwiftUI control, toolbar, tab bar, navigation container, menu, sheet, or system surface express the task? Use it first.
2. Does the target platform automatically provide the current Liquid Glass appearance? Let the system own that treatment.
3. Is there a small custom functional group that must visually read as one control layer over changing content? Use `GlassEffectContainer` and a minimal `glassEffect` route.
4. Does the group need an expressive shape or transition not supplied by the standard control? Add the smallest custom `Glass`/shape/tint needed, with an opaque/reduced-effects alternative.
5. Would the effect obscure text, reduce contrast, compete with content, or create an extra hit target? Remove it and return to a standard material/control.

## GlassEffectContainer rules

`GlassEffectContainer` groups multiple Liquid Glass shapes so SwiftUI can render them together and morph them during view hierarchy changes. Treat the container as a functional group, not a page-wide wrapper.

| Decision | Guidance |
| --- | --- |
| Group boundary | Include only controls/status items that act together or share a visual layer. |
| Spacing | Keep the container spacing and interior layout spacing intentional; the spacing influences when shapes blend or separate. |
| Shape | Use the default capsule for compact controls; choose a shape that follows the component’s actual affordance when a capsule is misleading. |
| Identity | Use unique stable `glassEffectID` values inside a `Namespace`; these are animation identities, not database IDs. |
| Union | Use `glassEffectUnion` only when separate effects should behave as one related shape; do not merge unrelated actions. |
| Interaction | Use `Glass.interactive()`/the current interactive glass style only when the control responds to input; preserve the same label and action without the effect. |
| Tint | Use tint as a restrained prominence cue after hierarchy and contrast are correct; never let tint replace a label, value, or error state. |

The exact modifier signatures are SDK-sensitive. Compile a minimal effect sample against the selected SDK before spreading a custom modifier through a design system.

## Morphing and transitions

Use `glassEffectID(_:in:)` to associate an effect with a stable visual identity and `glassEffectTransition(_:)` when an effect is inserted or removed inside a container. Use `matchedGeometry` when related shapes are near one another within the container’s spacing; use `materialize` for effects that should appear/disappear more simply or are farther apart.

Keep the underlying state authoritative:

`idle -> compact controls -> expanded controls -> compact controls`

The animation may morph the visual layer, but the accessibility tree, action labels, focus target, domain selection, and persisted state must remain correct if motion is reduced, the animation is interrupted, or the effect is unavailable. Never use a glass morph to imply that an action completed before the durable operation succeeds.

## Functional recipes

### Floating action group

- Use a `GlassEffectContainer` around two or three related semantic `Button`/`Menu` controls.
- Keep the scrollable content inset with `safeAreaInset` or a native toolbar rather than manually overlaying an unmeasured Z-stack.
- Give each control a label, hint/value where needed, and a clear focus order.
- Test keyboard, pointer, VoiceOver, Dynamic Type, landscape, sheet presentation, and reduced transparency.

### Compact status/control cluster

- Use standard `ProgressView`, `Toggle`, `Button`, or `Label` inside the group.
- Show `loading`, `ready`, `stale`, `failed`, and `permissionDenied` as explicit content states.
- Keep the status timestamp or uncertainty visible when the underlying service can be stale.
- Do not present an interactive status control when it cannot safely complete inside the extension/system-surface boundary.

### Detail-to-editor transition

- Use a native navigation or sheet transition for the route; add a glass identity only to the small control group that changes.
- Keep the source record, draft, and committed record separate.
- Move focus intentionally into the editor and restore it after validation/error handling.
- Use a non-morphing or identity transition when Reduce Motion is enabled.

## Accessibility and reduced effects

- Read `accessibilityReduceTransparency` and use an opaque or standard-material alternative when transparency should be reduced.
- Read `accessibilityReduceMotion` and remove nonessential morphing, scale, parallax, and timing while preserving the same state change.
- Verify text and symbols against changing backgrounds in light/dark appearance, increased contrast, large Dynamic Type, and localized strings.
- Keep hit regions at least as usable as the native control’s expected target; do not make a translucent shape the only way to discover an action.
- Test VoiceOver, Voice Control, Switch Control, keyboard/pointer, and focus movement through insertion/removal.

An accessibility audit can diagnose a tree; it cannot prove that a person can complete the physical task or that glass remains legible across devices.

## Performance and proof

- Keep the number of custom glass groups small and measure complex backgrounds or scrolling with the selected SDK/device.
- Prefer system bars/controls because they inherit platform behavior and avoid unnecessary custom rendering.
- Use previews for state matrices and simulator runs for layout/navigation; label them as such.
- Use a physical device for material legibility, interaction, animation/hitch behavior, Dynamic Type, reduced transparency, VoiceOver, thermal state, and battery impact.
- Test the signed artifact for widgets, controls, sheets, App Intents, notifications, and other system surfaces; custom glass in the main app does not prove the system surface.

## Sources

- [Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/liquid-glass)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Human Interface Guidelines: Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [accessibilityReduceTransparency](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducetransparency)
- [accessibilityReduceMotion](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [Safe area inset](https://developer.apple.com/documentation/swiftui/view/safeareainset%28edge%3Aalignment%3Aspacing%3Acontent%3A%29)
- [Animations](https://developer.apple.com/documentation/swiftui/animations)
