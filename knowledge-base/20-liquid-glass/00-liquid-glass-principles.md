# Liquid Glass Principles

## What Liquid Glass is for

Apple describes Liquid Glass as a dynamic material that combines glass-like optical behavior with fluidity. It forms a distinct functional layer for controls and navigation so people can focus on the content beneath it. The design system is not “put a translucent blur behind every card.” It is a hierarchy: content first, functional navigation and controls above it.

## Three principles

### Establish hierarchy

Keep the main content visually primary. Put navigation, actions, and system surfaces in the functional layer. Use emphasis, tint, and prominence to show what matters now.

### Create harmony

Let the system adapt material, translucency, contrast, and motion to the environment and accessibility settings. Prefer semantic colors and standard shapes over hand-tuned per-device backgrounds.

### Maintain consistency

Use the same navigation and control conventions as the platform. A custom component should feel like a natural member of the system, not a web card pasted onto an iPhone.

## Content layer versus functional layer

The content layer may be edge-to-edge, image-rich, or scrollable. The functional layer contains tab bars, sidebars, navigation bars, toolbars, search, and primary controls. Avoid competing layers that all demand attention.

## Anti-patterns

- Applying glass to every row, label, and decorative badge.
- Painting custom backgrounds over a system toolbar or tab bar.
- Making text and icons low-contrast because the surface “looks premium.”
- Stacking multiple glass surfaces with no content or spacing between them.
- Using a fake blur to mimic a system component that SwiftUI already renders correctly.
- Treating motion or morphing as the purpose of the interface.

## Sources

- [Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/liquid-glass)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
