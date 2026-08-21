# Liquid Glass Component Recipes

## System-first rule

Standard SwiftUI components already participate in the current Liquid Glass design system. Start by removing custom backgrounds, opaque bar fills, and unnecessary visual wrappers. Use system navigation, toolbars, tabs, controls, sheets, and safe-area behavior first.

Custom Liquid Glass is for a component that needs a distinct functional surface, not for turning every card into a translucent ornament.

## Recipe: one custom control

Use the effect after the modifiers that define the content’s appearance, select a shape that matches the component, and make interactivity explicit:

```swift
Label("Focus", systemImage: "scope")
    .padding(.horizontal, 14)
    .padding(.vertical, 10)
    .glassEffect(
        .regular.tint(.blue).interactive(),
        in: .rect(cornerRadius: 18)
    )
```

Treat tint as a prominence signal, not a substitute for a semantic label or contrast. The example is a route sketch and must be compiled against the selected SDK.

## Recipe: a group of controls

Use `GlassEffectContainer` when several custom glass views should render and morph as one related group:

```swift
GlassEffectContainer(spacing: 24) {
    HStack(spacing: 16) {
        Button("Play", systemImage: "play.fill") { play() }
            .glassEffect()

        Button("Stop", systemImage: "stop.fill") { stop() }
            .glassEffect()
    }
}
```

Container spacing influences when shapes blend and morph. Keep the group semantically related; do not use one giant container for unrelated regions of the screen.

## Recipe: identity and transitions

When a glass view appears, disappears, or changes shape across a transition, use stable `glassEffectID` values and the appropriate `glassEffectTransition` route so SwiftUI can understand which visual object is moving. Keep the identity tied to the product’s stable state, not to a transient array index.

## Recipe: bars and scrolling content

Prefer system bars and navigation containers. When a custom control must live at an edge over scrolling content, use the documented safe-area bar/inset route so content, hit testing, and safe areas remain coherent. Do not place an opaque full-screen background behind a bar just to imitate a screenshot.

## What to avoid

- Applying custom glass to every card, row, and background.
- Stacking multiple glass effects on the same visual object without a documented reason.
- Using blur/translucency to hide low-contrast text or weak hierarchy.
- Tinting every action the same way so prominence disappears.
- Treating the material as a brand identity that must remain unchanged across platforms or accessibility settings.

## Adaptation and accessibility

Test Reduce Transparency, Increased Contrast, Reduce Motion, Dynamic Type, Dark Mode, and different backgrounds. If the system reduces or changes the effect, the control must remain legible and understandable. Provide labels, traits, and state through the semantic control rather than communicating meaning only through a glass shape.

## Verification route

- Compare system-first and custom-glass versions; keep the simpler route when behavior is equivalent.
- Test custom effects over light, dark, colorful, moving, and text-heavy content.
- Test insertion/removal/morphing with VoiceOver, Reduce Motion, and large text.
- Verify hit targets and controls remain discoverable when effects are reduced.
- Check performance when many glass views move simultaneously.

## Sources

- [Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/liquid-glass)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [glassEffect(_:in:)](https://developer.apple.com/documentation/swiftui/view/glasseffect%28_%3Ain%3A%29)
- [safeAreaBar(edge:alignment:spacing:content:)](https://developer.apple.com/documentation/swiftui/view/safeareabar%28edge%3Aalignment%3Aspacing%3Acontent%3A%29)
