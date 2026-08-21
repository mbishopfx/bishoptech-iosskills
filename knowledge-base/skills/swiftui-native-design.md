# Skill Blueprint: SwiftUI Native Design

## Use when

Designing, reviewing, or implementing a SwiftUI screen, component, navigation flow, preview matrix, or accessibility pass for iOS 26.

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
