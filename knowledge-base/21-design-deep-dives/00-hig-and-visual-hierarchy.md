# HIG and Visual Hierarchy

## Design objective

Apple-native visual quality starts with hierarchy, harmony, consistency, simplicity, and craft. The goal is not “make everything rounded and translucent.” The goal is to make the primary task obvious, the content legible, the controls discoverable, and the response to every action coherent.

## Hierarchy before decoration

Use this order when designing a screen:

1. Name the one primary user outcome.
2. Identify the content that proves progress or success.
3. Choose the primary action and the safest location for it.
4. Move secondary actions into progressive disclosure, menus, toolbars, sheets, or detail views.
5. Establish reading order through alignment, type scale, spacing, and grouping.
6. Add material, color, animation, and haptics only when they clarify state or affordance.

Controls and navigation form a functional layer above content. Content should remain the visual subject; Liquid Glass can distinguish the functional layer without requiring a custom panel behind every view.

## Native signals of quality

- Use semantic SwiftUI controls so behavior, focus, accessibility, and platform styling come with the component.
- Prefer system typography, text styles, and SF Symbols before introducing custom type or iconography.
- Use a small, deliberate color vocabulary with sufficient contrast and semantic meaning.
- Align edges and baselines so related information scans as a group.
- Give touch targets enough surrounding space and separate unrelated actions.
- Use progressive disclosure instead of presenting every option at once.
- Let standard bars, navigation, tabs, sheets, and menus adopt current system behavior.

## “Apple-like” without cloning

Borrow principles, not proprietary screen compositions, copy, icons, or branding. Create an original content model, voice, icon treatment, and interaction hierarchy. A native app can feel at home through platform conventions while still having a distinct product identity.

## Screen recipe

For each screen, record:

| Decision | Question |
| --- | --- |
| Purpose | What should the person understand or accomplish first? |
| Content | What is essential, optional, empty, loading, or unavailable? |
| Action | Which action is primary, reversible, destructive, or delayed? |
| Structure | Which native container expresses the hierarchy? |
| Material | Is a functional layer needed, and why? |
| Adaptation | What changes for Dynamic Type, iPad, orientation, Dark Mode, or a different platform? |
| Proof | What preview, accessibility, simulator, and physical-device evidence is required? |

## Verification route

- Review the screen with all custom color removed; hierarchy should still be understandable.
- Review it at the largest accessibility text size and in landscape/multitasking contexts.
- Check empty, loading, error, disabled, permission-denied, and destructive-action states.
- Compare behavior to current HIG guidance and native system components, not to a screenshot alone.
- Test VoiceOver and keyboard/focus navigation where the target platform supports them.

## Sources

- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles)
- [Designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios/)
- [Layout](https://developer.apple.com/design/human-interface-guidelines/layout)
- [Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
- [Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
