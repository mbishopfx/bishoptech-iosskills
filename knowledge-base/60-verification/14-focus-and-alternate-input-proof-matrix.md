# Focus and alternate-input proof matrix

## Evidence boundary

Focus and accessibility APIs can compile while the actual task remains impossible for a keyboard user, confusing for VoiceOver, or unsafe when a model result replaces focused content. Prove input focus, accessibility focus, selection, commands, pointer behavior, and side effects separately.

## Claim-to-evidence matrix

| Claim | Minimum evidence | Stronger evidence | Failure to record |
| --- | --- | --- | --- |
| Focus moves intentionally | Unit/state tests for open, submit, error, apply, cancel | Device run with typing, keyboard dismissal, and async updates | Background update steals focus |
| Focused value targets current context | Unit/UI test with two editors and no focused editor | Multi-window/scene or document run | Global command acts on arbitrary content |
| Keyboard shortcut is correct | UI test for visible control and shortcut | Physical iPad/Mac/Catalyst keyboard with localized layout | Shortcut conflicts with system or is undocumented |
| Raw key handling is bounded | KeyPress fixture for handled/ignored/down/repeat/up | Device run with text input, composition, and Full Keyboard Access | onKeyPress swallows normal editing |
| Submit route is correct | UI test for fields, submit labels, invalid/valid state | Device with virtual/hardware keyboard and input methods | Every keystroke triggers a side effect |
| Accessibility focus is purposeful | State/UI test for error/result/status transitions | Physical VoiceOver/Switch Control run | Streaming or background updates interrupt reading |
| Accessibility actions mirror visible actions | Accessibility audit plus action tests | Physical VoiceOver/Voice Control/Switch Control task | Custom control is gesture/pointer-only |
| Pointer feedback is supportive | UI review for hover/press and touch fallback | Physical iPad/Mac/visionOS pointer route | Hover is the only way to find or understand an action |
| Focus effects remain legible | Appearance/contrast/Dynamic Type fixture | Device light/dark/increased contrast/reduced effects | Focus ring is clipped, low contrast, or layout-shifting |
| AI proposal respects focus/selection | Unit tests for revision/range and stale transition | Screen recording while editing during generation | Model result replaces changed text or selection |
| Apply is explicit | State test for proposal versus approved record | Device keyboard/VoiceOver/pointer apply/discard | Shortcut or focus completion auto-approves |
| Keyboard and glass coexist | Layout/UI test with safe area and keyboard | Physical device with glass/material and editor keyboard | Action group obscures focused text or commit action |
| Right-to-left is supported | Arabic/Hebrew/mixed-direction focus and shortcut fixture | Physical device with selection and VoiceOver | Focus order or shortcut assumptions are LTR |
| Large text remains usable | Dynamic Type UI fixture and accessibility audit | Physical device at largest supported size | Error/result/action text is truncated |
| Privacy boundary is respected | Log/redaction/retention test | Archive/configuration review and realistic diagnostic run | Raw text, key events, or prompts leak to logs |
| Target/release route is correct | Archive target/configuration/entitlement check | TestFlight or production-like install on supported device | Simulator or preview treated as release proof |

## Deterministic fixture pack

- empty/valid/invalid form;
- title/body/search/editor focus values;
- open, next, submit, cancel, save, apply, discard, retry;
- two simultaneous documents with one focused and no focused context;
- typed text with composition, emoji, diacritics, and mixed scripts;
- keyboard shortcut conflict/localization and standard cancel/default actions;
- raw key down/repeat/up and handled/ignored paths;
- selection replacement and text revision conflict;
- model proposal ready, partial, stale, filtered, canceled, unavailable, approved;
- VoiceOver focus on field, error, result, status, and actions;
- Voice Control names and Switch Control traversal;
- Full Keyboard Access and pointer/hover/press;
- large Dynamic Type, right-to-left, increased contrast, reduced motion/transparency;
- keyboard visible/dismissed, rotation, split view, compact width, and safe-area action group.

## Focus assertions

Assert semantic state rather than visual coordinates:

    inputFocus
    accessibilityFocus
    selectedRange
    focusedDocumentID
    proposalRevision
    decisionState
    commandAvailability

Use screenshots to inspect focus rings, labels, material, and clipping. Do not treat a screenshot without an input task as proof that focus is reachable or understandable.

## Device notes

Record OS/SDK, device family, keyboard/pointer/accessibility settings, locale, build, target, and fixture. Simulator/UI tests can cover many state transitions; physical devices are required for touch/keyboard/pointer feel, VoiceOver/Voice Control/Switch Control interaction, text input, focus behavior, material rendering, memory, and thermal claims.

## Sources

- [Focus](https://developer.apple.com/documentation/swiftui/focus)
- [FocusState](https://developer.apple.com/documentation/swiftui/focusstate)
- [FocusedValues](https://developer.apple.com/documentation/swiftui/focusedvalues)
- [FocusedBinding](https://developer.apple.com/documentation/swiftui/focusedbinding)
- [FocusedValueKey](https://developer.apple.com/documentation/swiftui/focusedvaluekey)
- [Focusable](https://developer.apple.com/documentation/swiftui/view/focusable%28_%3A%29)
- [Input events](https://developer.apple.com/documentation/swiftui/input-events)
- [KeyboardShortcut](https://developer.apple.com/documentation/swiftui/keyboardshortcut)
- [AccessibilityFocusState](https://developer.apple.com/documentation/swiftui/accessibilityfocusstate)
- [Accessibility focused](https://developer.apple.com/documentation/swiftui/view/accessibilityfocused%28_%3A%29)
- [Accessible controls](https://developer.apple.com/documentation/swiftui/accessible-controls)
- [TextField](https://developer.apple.com/documentation/swiftui/textfield)
- [TextEditor](https://developer.apple.com/documentation/swiftui/texteditor)
- [TextSelection](https://developer.apple.com/documentation/swiftui/textselection)
- [AttributedTextSelection](https://developer.apple.com/documentation/swiftui/attributedtextselection)
- [Human Interface Guidelines: Focus and selection](https://developer.apple.com/design/human-interface-guidelines/focus-and-selection)
- [Human Interface Guidelines: Keyboards](https://developer.apple.com/design/human-interface-guidelines/keyboards)
- [Human Interface Guidelines: Pointing devices](https://developer.apple.com/design/human-interface-guidelines/pointing-devices)
- [Human Interface Guidelines: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
