# Focus-first native input design

## Design thesis

Focus is a quiet system signal that tells people where their next action will land. Apple-native polish comes from letting the system focus model, semantic controls, keyboard commands, selection, pointer behavior, and accessibility technologies agree with one another.

Use this loop:

    task
    -> semantic control/editor
    -> input focus and selection
    -> visible state
    -> alternate input route
    -> result and recovery

If a surface looks beautiful only while a pointer hovers over it or while a custom focus glow is visible, its interaction model is incomplete.

## The four focus questions

For every important action, answer:

1. Which view receives normal input?
2. Which text or item is selected?
3. What should VoiceOver or another accessibility technology focus?
4. What happens if the focused view disappears, becomes invalid, or is replaced by a model result?

Use separate state for those answers. A focused TextField is not the same as a selected record, a selected range, or an accessibility announcement.

## Form and editor rhythm

A polished form moves focus only when the person’s intent is clear:

    field -> submit/next -> validation -> next field or error

Good transitions:

- Return/Next moves to the next field in a known order;
- validation moves to the first invalid field and exposes the error;
- Save dismisses focus only when the action succeeds or the product intentionally ends editing;
- Cancel restores or discards without leaving a hidden focus target.

Poor transitions:

- a live model update moves focus while the person types;
- a status banner steals focus for every token;
- a sheet appears and the keyboard remains over the primary action;
- a hidden or collapsed field still owns the FocusState value;
- the app uses a custom rounded rectangle and tap gesture instead of a semantic Button.

## Keyboard is a first-class iPad/Mac route

Apple’s HIG describes physical keyboards as important for text entry and efficient commands, and recommends supporting Full Keyboard Access when possible. Respect standard keyboard shortcuts, keep custom shortcuts limited to frequent app-specific commands, prefer the Command key as the main modifier, and allow the system to localize and mirror shortcuts.

For iPadOS, distinguish text/sidebar keyboard navigation from general control activation and test Full Keyboard Access. For Mac Catalyst, also verify menus, command groups, pointer precision, window resizing, and platform-appropriate toolbar behavior. Do not force a phone-shaped shortcut system into a Mac surface.

Use system command placement:

    visible Button/Toggle
    -> keyboard shortcut
    -> optional Commands/Menu projection

The visible control remains the source of truth. A command should not exist only in a menu or hidden keyboard combination.

## Accessibility focus is not a notification channel

Accessibility focus should move when the person needs to know about a meaningful result:

- a requested search result;
- a validation error;
- a completed import or generation action;
- a newly presented editor or sheet.

Keep streaming and background progress in a labeled status element that can be inspected without interrupting the current reading position. If an accessibility focus move is necessary, make the target concise and explain the action through its label/value.

## Reviewable AI surface

A good AI review surface uses focus to preserve agency:

    source or selected range
    -> focused editor
    -> user-triggered proposal
    -> visible draft
    -> editor selection or result focus
    -> apply/edit/discard

The generated result can appear adjacent to the editor, in a sheet, or in a new section, but the original content and current selection remain available. “Apply” is a semantic action; a glow, shortcut, or automatic focus change does not approve a proposal.

Use FocusedValues to let a toolbar or command surface act on the currently focused document. This prevents a global Apply command from targeting the wrong editor, but the command still needs revision checks, availability state, and an accessible result.

## Pointer and glass

On iPad and visionOS, a pointer adds precision without replacing touch, eyes, or gestures. On Mac, pointer and keyboard are often a person’s primary route. Use system focus/pointer effects and give hover a supporting role:

- reveal a tooltip or secondary affordance;
- reinforce which control is under the pointer;
- expose a minimized toolbar when the platform convention calls for it.

Do not hide the only action until hover, make a glass pill grow under the pointer in a way that shifts layout, or use a hover state as the only status indicator. Keep the glass group measured, stable, and focusable through semantic controls.

## Focus visibility

Focus should be visible enough to locate but restrained enough not to compete with content:

- use system-defined focus effects when available;
- preserve contrast in dark/light and increased-contrast modes;
- avoid changing layout when focus appears;
- keep focus rings within the hit region;
- support reduced motion without removing the focused state;
- ensure a focused control remains visible after scrolling or keyboard appearance.

## Adaptation matrix

| Condition | Design response |
| --- | --- |
| Touch only | Native controls, clear labels, no gesture-only completion |
| Hardware keyboard | Focus path, submit/next, standard shortcuts, cancel |
| Pointer | Hover feedback and precise hit regions without hover-only actions |
| VoiceOver | Correct reading order, labels, values, actions, purposeful focus |
| Voice Control | Visible, stable names and action phrases |
| Switch Control | Reachable element order and same action semantics |
| Full Keyboard Access | Complete task without touch-only assumptions |
| Large Dynamic Type | Focus ring and error/result text remain readable |
| Right-to-left | Mirrored order, labels, keyboard behavior, and selection |
| Reduce Motion | No focus movement or effect required to understand state |
| Reduce Transparency | Focus and action hierarchy survive material fallback |

## Custom focus and custom controls

Prefer native Button, Toggle, Picker, Slider, TextField, TextEditor, List, NavigationLink, and Menu. Use a custom focusable view only when the product has a real component-level interaction that native controls cannot express.

If custom focus is justified:

- define which interactions it supports;
- implement activation and cancellation;
- expose the same state to accessibility technologies;
- keep keyboard and pointer paths;
- test focus traversal when items are inserted or removed;
- avoid using arbitrary model output to define focus order;
- provide a non-spatial, semantic alternative.

## AI safety and privacy

A model can suggest a next field, correction, or result, but code decides whether focus moves. Keep prompts and focused values bounded and redact sensitive content from logs. If the model is unavailable or the output is rejected, keep the editor and current focus usable.

## Proof packet

Capture normal interaction focus, text selection, keyboard submit/shortcut, pointer hover/press, VoiceOver focus/action, Voice Control naming, Switch Control traversal, Full Keyboard Access, Dynamic Type, RTL, reduced effects, stale proposal, cancellation, and a physical-device run for the target claims.

## Sources

- [Human Interface Guidelines: Focus and selection](https://developer.apple.com/design/human-interface-guidelines/focus-and-selection)
- [Human Interface Guidelines: Keyboards](https://developer.apple.com/design/human-interface-guidelines/keyboards)
- [Human Interface Guidelines: Pointing devices](https://developer.apple.com/design/human-interface-guidelines/pointing-devices)
- [Human Interface Guidelines: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Focus](https://developer.apple.com/documentation/swiftui/focus)
- [FocusState](https://developer.apple.com/documentation/swiftui/focusstate)
- [FocusedValues](https://developer.apple.com/documentation/swiftui/focusedvalues)
- [Input events](https://developer.apple.com/documentation/swiftui/input-events)
- [KeyboardShortcut](https://developer.apple.com/documentation/swiftui/keyboardshortcut)
- [AccessibilityFocusState](https://developer.apple.com/documentation/swiftui/accessibilityfocusstate)
- [Accessible controls](https://developer.apple.com/documentation/swiftui/accessible-controls)
- [TextEditor](https://developer.apple.com/documentation/swiftui/texteditor)
- [AttributedTextSelection](https://developer.apple.com/documentation/swiftui/attributedtextselection)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
