# Layout, Typography, and Controls

## Layout is proposal and response

SwiftUI containers propose a size to children, and children respond with a size. Build the hierarchy first, then tune spacing, alignment, padding, safe areas, and constraints. Avoid fighting the layout system with many fixed frames; fixed geometry tends to break with Dynamic Type, localization, split view widths, and device rotation.

## Container choices

| Content shape | First choice | Why |
| --- | --- | --- |
| Small horizontal/vertical group | HStack / VStack | Clear, simple composition. |
| Layered content | ZStack | Intentional overlay or background relationship. |
| Long repeated content | List or ScrollView plus lazy stack | System behavior or controlled custom layout. |
| Editable settings/data entry | Form and semantic controls | Platform-standard grouping and input behavior. |
| Two-dimensional repeated content | LazyVGrid / LazyHGrid | Efficient repeated grid. |
| Adaptive columns | Grid or adaptive grid items | Preserve relationships across widths. |
| Custom arrangement | Layout | Only when built-in containers cannot express the design. |

Use List and Form when their system behaviors help. Use a custom scroll view when the product needs a genuinely different content rhythm, but keep scrolling, focus, accessibility, and loading behavior explicit.

## Typography

Use semantic text styles such as largeTitle, title, headline, body, callout, subheadline, footnote, and caption before choosing a fixed point size. Semantic styles participate in Dynamic Type and communicate hierarchy. Use weight, design, and color to reinforce hierarchy rather than making every heading large and bold.

## Controls

Prefer a control that describes its action:

- Button for an action.
- Toggle for a persistent Boolean choice.
- Picker for choosing from a set.
- Slider for a continuous value.
- Stepper for bounded increments.
- TextField or TextEditor for text input.
- Menu for secondary actions.
- Link for navigation to a URL or deep link.
- ProgressView for progress or indeterminate work.

Give controls meaningful labels. If an icon-only button is necessary, supply an accessibility label and ensure the icon’s meaning is not the only clue.

## Spacing and shape

Use a small spacing scale and let platform containers provide their default metrics where possible. Keep shapes consistent with their containing surfaces. For iOS 26 Liquid Glass, avoid manually painting the background of system bars, toolbars, tabs, and navigation unless the design has a documented reason.

## Sources

- [Laying out a simple view](https://developer.apple.com/documentation/swiftui/laying-out-a-simple-view)
- [Layout adjustments](https://developer.apple.com/documentation/swiftui/layout-adjustments)
- [Picking container views for your content](https://developer.apple.com/documentation/swiftui/picking-container-views-for-your-content)
- [Text](https://developer.apple.com/documentation/swiftui/text)
- [Controls and indicators](https://developer.apple.com/documentation/swiftui/controls-and-indicators)
- [Accessible appearance](https://developer.apple.com/documentation/swiftui/accessible-appearance)
