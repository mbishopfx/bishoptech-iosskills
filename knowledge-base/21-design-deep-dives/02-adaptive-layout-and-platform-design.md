# Adaptive Layout and Platform Design

## Capability

SwiftUI’s layout system lets one view hierarchy respond to proposals, available space, Dynamic Type, orientation, multitasking, platform, and accessibility settings. Adaptive design is not “make the iPhone screen wider”; it is choosing a different presentation when the task, space, or input model changes.

## Layout route

1. Identify the content hierarchy and the smallest useful layout.
2. Let parent containers propose size; avoid hard-coded screen dimensions.
3. Use stacks, grids, lists, forms, scroll views, and navigation containers for their semantic behavior.
4. Use `ViewThatFits`, `AnyLayout`, size/environment values, or a custom `Layout` only when a real adaptation requires it.
5. Keep content and controls independent so a toolbar, sidebar, tab, or sheet can move without duplicating business logic.
6. Verify at large text, split view, landscape, external display, and different platform idioms.

## Presentation choices

| Context | Native route to consider | Design question |
| --- | --- | --- |
| Compact iPhone | `NavigationStack`, lists, sheets, bottom actions | What is the shortest path to the primary task? |
| Regular-width iPad | `NavigationSplitView`, sidebars, multi-column content | Can navigation and detail stay visible together? |
| Dynamic Type | Text styles, flexible stacks, scrollable content | Does hierarchy survive when text grows? |
| A feature absent on a platform | Availability checks and alternate content | Is the fallback useful or should the feature be hidden? |
| Edge control over scroll content | `safeAreaBar`/safe-area tools | Does the content remain readable and tappable beneath it? |

## Avoid layout traps

- Do not use fixed heights for text that must scale.
- Do not encode every breakpoint as a magic number before observing the actual layout proposal.
- Do not put unrelated controls in a glass capsule merely because they fit geometrically.
- Do not assume a device is portrait, has one window, or has a specific safe-area inset.
- Do not use `GeometryReader` as a default container when a normal layout can express the relationship.
- Do not hide overflow that contains the user’s primary information.

## Platform adaptation

The same feature can use shared domain state and different presentation shells. For example, a capture flow may use a compact navigation stack on iPhone, a split view with source and review panes on iPad, and a different spatial presentation on visionOS. Keep platform-specific differences in the view layer and preserve the same permission, validation, and persistence contracts underneath.

## Verification route

- Preview representative device sizes, orientations, color schemes, text sizes, and layout directions.
- Test iPad multitasking, keyboard/pointer input, external display, and split view if supported.
- Test long localized strings, empty data, error states, and Dynamic Type at the largest accessibility sizes.
- Confirm controls do not move unpredictably or become unreachable when content grows.
- Inspect safe-area and scroll behavior with bars, sheets, keyboards, and system overlays.

## Sources

- [Layout](https://developer.apple.com/design/human-interface-guidelines/layout)
- [Laying out a simple view](https://developer.apple.com/documentation/swiftui/laying-out-a-simple-view)
- [Layout adjustments](https://developer.apple.com/documentation/swiftui/layout-adjustments)
- [Picking container views for your content](https://developer.apple.com/documentation/swiftui/picking-container-views-for-your-content)
- [Navigation](https://developer.apple.com/documentation/swiftui/navigation)
- [NavigationSplitView](https://developer.apple.com/documentation/swiftui/navigationsplitview)
- [ViewThatFits](https://developer.apple.com/documentation/swiftui/viewthatfits)
- [AnyLayout](https://developer.apple.com/documentation/swiftui/anylayout)
