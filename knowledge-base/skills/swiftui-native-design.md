# Skill Blueprint: SwiftUI Native Design

## Use when

Designing, reviewing, or implementing a SwiftUI screen, component, navigation flow, preview matrix, or accessibility pass for iOS 27 with an explicit iOS 26 fallback.

## Inputs

- product outcome and target platforms;
- current project structure and deployment target;
- design brief;
- existing assets and copy;
- source-backed feature requirements.

## Workflow

1. Read the current SwiftUI and HIG sources for the relevant surface.
2. Identify the state owner and route before styling.
3. Choose standard SwiftUI containers and controls first.
4. Model empty/loading/success/error/permission states.
5. Use semantic typography, system colors, and adaptive layout.
6. Add animation only for a clear state transition.
7. Add accessibility labels, values, focus behavior, Dynamic Type, contrast, and motion handling.
8. Build previews for representative states.
9. Verify local links/source notes, then build/test in the target project.

For iOS 27 targets, also consult the [iOS 27 SwiftUI and SDK refresh](../10-swiftui/13-ios27-swiftui-refresh.md) and [iOS 27 native design brief](../90-templates/ios27-native-design-brief.md) before using toolbar overflow/minimization, the `Document` protocols, reorderable containers, `swipeActionsContainer`, new `AsyncImage` controls, interactive text selection, or macro-backed `@State` behavior. The selected Xcode 27 SDK has a targeted symbol-level probe; Xcode 26.4 remains the earlier lane, and neither SDK probe is app-target or runtime proof.

## Refuse to assume

- A fixed phone width is the only layout.
- Simulator rendering proves physical-device behavior.
- Custom UI is better than a system control.
- A visual screenshot is a sufficient accessibility review.

## Output

- changed files and architecture boundary;
- design decisions and rejected alternatives;
- preview/accessibility matrix;
- build/test evidence;
- remaining device or release checks.

## Sources

- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Managing user interface state](https://developer.apple.com/documentation/swiftui/managing-user-interface-state)
- [Navigation](https://developer.apple.com/documentation/swiftui/navigation)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [What’s new in SwiftUI](https://developer.apple.com/swiftui/whats-new/)
- [iOS and iPadOS 27 release notes](https://developer.apple.com/documentation/ios-ipados-release-notes/ios-ipados-27-release-notes)
- [iOS 27 native design brief](../90-templates/ios27-native-design-brief.md)
- [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles)
- [Designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios)
- [Designing for iPadOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ipados)
- [Designing for macOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-macos)
- [Designing for watchOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-watchos)
- [Designing for games](https://developer.apple.com/design/human-interface-guidelines/designing-for-games)
- [Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)
- [Apple Design Resources](https://developer.apple.com/design/resources/)
