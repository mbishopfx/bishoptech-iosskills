---
name: liquid-glass-design
description: Create or review native iOS 26 Liquid Glass interfaces using system surfaces first, justified custom effects, adaptable hierarchy, and device-aware verification.
metadata:
  short-description: Build native Liquid Glass interfaces
---

# Liquid Glass Design

Use this skill when a SwiftUI or UIKit surface should participate in iOS 26 Liquid Glass. The goal is an original product that feels native because it follows Apple’s hierarchy, materials, controls, motion, and accessibility conventions—not a replica of Apple’s branded screens.

## Read before acting

Inspect the target view hierarchy and target settings first:

- identify the content layer, functional controls, navigation/container surface, scrolling behavior, custom backgrounds, and current SDK/deployment target;
- check whether the system already supplies the glass treatment for the navigation bar, tab bar, toolbar, search, sheet, or control;
- read [Liquid Glass principles](../../../20-liquid-glass/00-liquid-glass-principles.md), [system-first adoption](../../../20-liquid-glass/01-system-first-adoption.md), [custom glass effects](../../../20-liquid-glass/02-custom-glass-effects.md), and [containers and morphing](../../../20-liquid-glass/03-glass-containers-and-morphing.md);
- refresh Apple’s [Liquid Glass overview](https://developer.apple.com/documentation/TechnologyOverviews/liquid-glass), [adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass), [applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views), [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer), [Glass](https://developer.apple.com/documentation/swiftui/glass), and the [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/) before using update-sensitive APIs.

## Implementation route

1. Establish content hierarchy and interaction priority before adding material effects. Ask what must remain readable and what is actually floating above content.
2. Keep system-managed bars and controls system-managed. Remove custom backgrounds or overlays that fight the current navigation, tab, toolbar, search, sheet, or scroll-edge treatment.
3. Prefer standard SwiftUI controls and glass button styles for functional actions. Use `glassEffect` for a genuinely custom functional element only when a standard component cannot express the requirement.
4. Use a `GlassEffectContainer` for related glass elements when grouping or morphing communicates a real semantic relationship. Give morphing participants stable, meaningful identities; do not animate every incidental layout change.
5. Use safe-area and scroll-edge APIs for custom bars or controls that sit above scrolling content. Keep hit targets, labels, focus behavior, and scroll content legible when the material changes.
6. Define an adaptive visual fallback. Test light/dark appearance, contrast, Dynamic Type, reduced motion, reduced transparency/effects, localization, and content behind the effect. A glass layer must never be the only carrier of meaning.
7. Record which behavior is system-provided and which is custom so later SDK changes can be rechecked without treating a screenshot as the contract.

## Change boundary

May inspect and change the named UI surface, related layout modifiers, component styles, previews, and directly related state needed to demonstrate the effect. Preserve supplied copy, assets, navigation, and product hierarchy. Do not globally restyle an app or replace system bars with custom glass merely because a single screen requests Liquid Glass.

## Refuse to assume

- every surface should be translucent;
- a blur, opacity, gradient, or generic material is equivalent to Liquid Glass;
- a custom tint can repair poor contrast or missing semantics;
- morphing is useful without a meaningful relationship between elements;
- an API shown in a documentation snippet is available in the project’s selected SDK;
- simulator screenshots prove transparency, contrast, motion, performance, or readability on physical devices.

## Completion evidence

Report separately:

- which system components were retained and which custom components needed glass;
- the exact Liquid Glass APIs and grouping/identity decisions used;
- accessibility and reduced-effects behavior;
- previews plus simulator/device observations, naming target OS and device when available;
- source links and any unverified target-SDK, performance, or physical-device gaps.

Do not call a surface “Apple replica quality” solely because it resembles a screenshot. The evidence must include hierarchy, interaction, adaptability, and accessibility checks.

## Related knowledge-base routes

- [Liquid Glass component recipes](../../../21-design-deep-dives/01-liquid-glass-component-recipes.md)
- [Native screen recipes](../../../20-liquid-glass/04-native-screen-recipes.md)
- [SwiftUI and Liquid Glass code recipes](../../../70-code-recipes/00-swiftui-and-liquid-glass-recipes.md)
- [Accessibility and adaptability checklist](../../../60-verification/02-accessibility-and-adaptability-checklist.md)

## Sources

- [Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/liquid-glass)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
