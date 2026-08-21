# System-First Liquid Glass Adoption

## Start with standard components

Standard SwiftUI, UIKit, and AppKit components adopt the current platform appearance on the latest releases. Begin by building with the latest SDK and inspecting your existing NavigationStack, NavigationSplitView, TabView, toolbars, sheets, popovers, lists, forms, and controls.

## Remove conflicts before adding effects

Audit custom backgrounds and appearances in:

- navigation containers;
- tab bars;
- toolbars;
- split views and sidebars;
- sheets and popovers;
- list and form containers;
- custom bars above scrolling content.

If a background is only there to force an older visual, remove it and see what the system provides. Custom backgrounds can overlay or interfere with Liquid Glass and scroll-edge behavior.

## Use the system’s control styles

When a button should look like a glass control, start with the documented glass button styles rather than a custom material stack:

~~~swift
VStack {
    Button("Continue") { continueFlow() }
        .buttonStyle(.glassProminent)

    Button("More options") { showOptions = true }
        .buttonStyle(.glass)
}
~~~

Use prominence intentionally. The primary action should remain identifiable; if every button is prominent, none of them is.

## Scroll edge and safe area behavior

System bars automatically participate in scroll-edge behavior. If you build a custom bar with content scrolling underneath, investigate safeAreaBar and the system’s scroll-edge APIs rather than layering an arbitrary blur over the scroll view.

## Navigation and search

Keep navigation visually distinct from content. Use standard search placement, and use the semantic search tab role when search belongs in the primary tab bar so the system can position it appropriately.

## Verification

Inspect the same screen with:

- content behind the bar that changes color and contrast;
- light/dark mode;
- reduced transparency and increased contrast;
- large text;
- scrolling at the edge;
- iPhone and iPad/window contexts.

## Sources

- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/liquid-glass)
- [Navigation](https://developer.apple.com/documentation/swiftui/navigation)
- [safeAreaBar](https://developer.apple.com/documentation/swiftui/view/safeareabar%28edge%3Aalignment%3Aspacing%3Acontent%3A%29)
- [Tab](https://developer.apple.com/documentation/swiftui/tab)
