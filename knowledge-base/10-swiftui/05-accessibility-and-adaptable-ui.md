# Accessibility and Adaptable UI

## Accessibility is part of the view contract

Use semantic SwiftUI controls and give them labels that describe the action or value. Combine decorative elements with their associated label when that produces a clearer VoiceOver element. Hide purely decorative images from accessibility and expose meaningful custom content with accessibilityLabel, accessibilityValue, accessibilityHint, traits, and actions as appropriate.

Start with the control that already owns the behavior: `Button`, `Toggle`, `Slider`, `Picker`, `NavigationLink`, `TextField`, `ProgressView`, and `List` bring useful platform semantics. Add modifiers when the default accessibility tree does not express the product meaning. `accessibilityElement(children: .combine)` is useful for one logical row; `.contain` keeps child actions discoverable; `accessibilityChildren` or `accessibilityRepresentation` can expose a meaningful tree for custom drawing. Do not flatten a row that contains independent actions into one inaccessible gesture target.

For dynamic state, expose the value and action rather than describing the visual implementation. Use `accessibilityAction` for a custom action, `accessibilitySortPriority` only when the reading order needs a deliberate correction, and `AccessibilityFocusState` when a new error, result, or sheet needs to move assistive-technology focus. Focus movement should be rare and purposeful; do not steal focus during ordinary animation or background updates.

## Adaptability checklist

Test at minimum with:

- light and dark appearance;
- increased contrast and reduced transparency;
- Dynamic Type sizes including the largest accessibility sizes;
- VoiceOver navigation and rotor order;
- Reduce Motion;
- different locale and longer strings;
- right-to-left layout where supported;
- keyboard and pointer input on iPad/Mac contexts;
- portrait, landscape, split view, and resizable window contexts.

## Motion preferences

Read the environment’s accessibility motion preference and provide a lower-motion behavior. A reduced-motion path can remove scale, parallax, morphing, and large movement while preserving state change and hierarchy. Do not merely speed up the same animation.

Treat `accessibilityReduceMotion`, `accessibilityReduceTransparency`, and `accessibilityDifferentiateWithoutColor` as behavior inputs. A view can keep its identity and hierarchy while replacing a morph with an opacity/state change, replacing a translucent treatment with a more opaque material, and adding a symbol, label, pattern, or shape to color-coded status.

## Contrast and translucency

Liquid Glass can change how content and controls blend. Test custom tints, icons, text, and backgrounds with different contrast and transparency settings. If a custom effect becomes illegible, simplify it; do not add more glow or shadow as the first response.

Prefer system colors and semantic text styles so the system can adapt them for appearance and contrast. For custom colors, test light, dark, increased contrast, reduced transparency, and visually rich content behind the control. Keep clear glass for appropriate media-overlaid controls and use a more legible regular/material treatment when text or dense controls need stronger separation. Never place glass behind every content card just to create a visual signature.

## Touch, focus, and labels

- Keep the whole visible control tappable, not only a small glyph.
- Make the label match the action: “Save draft” is better than “Checkmark.”
- Expose value and state for toggles, sliders, progress, and selected tabs.
- Preserve focus after validation errors and route focus intentionally when a sheet opens.
- Avoid relying on color, animation, or position as the only way to communicate state.
- Give UI-test identifiers to important surfaces without using those identifiers as spoken labels.
- Provide a keyboard, Voice Control, Switch Control, or other semantic alternative for every important gesture where the platform supports it.

## Sources

- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessible controls](https://developer.apple.com/documentation/swiftui/accessible-controls)
- [Accessible descriptions](https://developer.apple.com/documentation/swiftui/accessible-descriptions)
- [Accessible appearance](https://developer.apple.com/documentation/swiftui/accessible-appearance)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [AccessibilityFocusState](https://developer.apple.com/documentation/swiftui/accessibilityfocusstate)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [accessibilityReduceMotion](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion)
- [accessibilityReduceTransparency](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducetransparency)
- [accessibilityDifferentiateWithoutColor](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilitydifferentiatewithoutcolor)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
- [Motion](https://developer.apple.com/design/human-interface-guidelines/motion)
- [Color](https://developer.apple.com/design/human-interface-guidelines/color)
- [Apple accessibility](https://developer.apple.com/accessibility/)
