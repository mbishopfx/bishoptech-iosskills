# Accessibility and Internationalization

## Capability

An Apple-native interface remains useful when text grows, contrast changes, motion is reduced, VoiceOver reads it, layout direction flips, and translated strings become longer. Accessibility and internationalization are structural design inputs, not a final polish pass.

## Accessibility route

1. Use semantic controls and containers first.
2. Inspect the accessibility tree and identify missing labels, values, traits, hints, actions, and grouping.
3. Add only the metadata needed to express the user-facing meaning.
4. Test VoiceOver, Voice Control, Switch Control, Larger Text, Increase Contrast, Reduce Transparency, and Reduce Motion.
5. Ensure every important action has an equivalent non-gesture path.

Use `AccessibilityFocusState` only for a meaningful state transition such as presenting a validation error or announcing a newly available result. Combine related static content when it is one spoken unit, but keep buttons, toggles, links, and other independent actions as separate accessibility elements. A custom-drawn chart, canvas, or glass control needs an accessible representation that exposes data and actions instead of relying on pixels.

SwiftUI provides default accessibility information for common controls. Custom drawing, combined labels, decorative imagery, and UIKit/AV/RealityKit bridges need deliberate metadata.

## Typography and localization route

- Use text styles and dynamic system fonts instead of fixed-point text for primary content.
- Keep user-visible strings localizable and avoid concatenating sentence fragments.
- Use format styles for dates, times, numbers, currencies, measurements, and pluralization.
- Test right-to-left layout and avoid encoding meaning only in leading/trailing assumptions.
- Allow labels, buttons, navigation titles, and errors to expand without truncating the action.
- Use symbols and images with meaningful accessibility labels or mark decorative content appropriately.

## Semantic example

An icon-only control should expose its action and state, not its visual shape:

```swift
Button {
    isPinned.toggle()
} label: {
    Image(systemName: isPinned ? "pin.fill" : "pin")
}
.accessibilityLabel(isPinned ? "Unpin note" : "Pin note")
.accessibilityValue(isPinned ? "Pinned" : "Not pinned")
```

The exact modifier strategy depends on the surrounding control and platform. Prefer a visible text label when space and hierarchy allow it.

## Internationalization boundary

Treat translated copy as data with unknown length. Design test fixtures with long German, compact Chinese, right-to-left Arabic/Hebrew, plural changes, and locale-specific dates/numbers. Do not hard-code a layout around English word lengths or assume a single reading order.

## Verification route

- Run the accessibility inspector and VoiceOver through primary and recovery flows.
- Verify focus order, grouping, rotor actions, labels, values, hints, and custom actions.
- Test all Dynamic Type sizes and text truncation/scroll behavior.
- Test contrast and appearance settings, including reduced transparency.
- Test localized strings, right-to-left layout, pluralization, dates, numbers, and voice-over pronunciation.
- Ensure previews and UI tests use accessibility identifiers without making them the user-facing label.
- Run `XCUIApplication.performAccessibilityAudit(for:)` in UI tests, then manually test VoiceOver because a passing audit is not a complete accessibility claim.
- Test reduced motion as a different interaction path: state remains understandable without morphing, parallax, or large movement.
- Test custom Liquid Glass with increased contrast and reduced transparency; simplify the effect when legibility or hierarchy weakens.

## Sources

- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Accessible appearance](https://developer.apple.com/documentation/swiftui/accessible-appearance)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [AccessibilityFocusState](https://developer.apple.com/documentation/swiftui/accessibilityfocusstate)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [Performing accessibility audits for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-audits-for-your-app)
- [XCUIApplication](https://developer.apple.com/documentation/xcuiautomation/xcuiapplication)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
- [Motion](https://developer.apple.com/design/human-interface-guidelines/motion)
- [Color](https://developer.apple.com/design/human-interface-guidelines/color)
- [Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
- [Layout](https://developer.apple.com/design/human-interface-guidelines/layout)
- [Internationalization](https://developer.apple.com/localization/)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
