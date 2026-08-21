# Skill Blueprint: Liquid Glass Design

## Use when

Creating or reviewing an iOS 26 screen that should feel native to Apple’s Liquid Glass design language.

## Inputs

- target screen and hierarchy;
- content layer and functional layer;
- navigation/container choice;
- custom visual requirements;
- accessibility and device matrix.

## Workflow

1. Start with standard SwiftUI/UIKit components and build with the latest SDK.
2. Remove custom backgrounds from system bars, toolbars, tabs, lists, and navigation where they conflict with the system treatment.
3. Establish content hierarchy before adding effects.
4. Use glass button styles for glass controls.
5. Use glassEffect only for a justified custom functional element.
6. Group related effects with GlassEffectContainer and stable IDs when morphing has semantic value.
7. Use safe-area/scroll-edge APIs for custom bars above scrolling content.
8. Check light/dark, contrast, reduced transparency, reduced motion, Dynamic Type, and content legibility.
9. Record which behavior comes from the system and which is custom.

## Refuse to assume

- Every surface should be translucent.
- A blur is equivalent to Liquid Glass.
- A morphing animation is always desirable.
- Custom tint can replace contrast or semantics.

## Output

- native component choices;
- Liquid Glass API decisions;
- accessibility fallback behavior;
- preview and device verification matrix;
- source links and evidence boundary.

## Sources

- [Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/liquid-glass)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
