# Focus, keyboard, pointer, and accessibility input

## Purpose

Native input is more than a tap gesture. SwiftUI gives separate routes for interaction focus, accessibility focus, selection, keyboard shortcuts, raw key presses, submit behavior, focused values, pointer behavior, and accessibility actions.

Use the route:

    semantic action and state
    -> native control or editor
    -> interaction focus/selection
    -> keyboard/pointer/gesture route
    -> accessibility focus/actions
    -> model/system side effect
    -> recovery and proof

Keep these concepts separate:

| Concept | Meaning | Typical owner |
| --- | --- | --- |
| Input focus | Which view receives the next interaction input | FocusState/focusable |
| Accessibility focus | Which element VoiceOver or another accessibility technology is inspecting | AccessibilityFocusState |
| Text selection | Which characters are selected or edited | TextSelection/AttributedTextSelection |
| Visual selection | Which item the product shows as selected | Domain/UI state |
| Keyboard shortcut | A command available in the active scene/window | Button, Toggle, commands, KeyboardShortcut |
| Key press | A hardware key event delivered to a focused view | onKeyPress |
| Focused value | Context published by the focused view for commands or ancestors | FocusedValues/FocusedBinding |

Do not use one focus state to stand in for all of them. A field can have input focus while VoiceOver focuses an error message, and a selected text range can remain meaningful after the editor loses focus.

## FocusState is a deliberate navigation tool

FocusState can read and write which focusable view is active. With focused or focused equals, a state change can move focus programmatically, and focus changes update the state.

Use a small Hashable enum for a form or review surface:

    title
    source
    editor
    search
    none

Move focus for a reason:

- after a deliberate submit;
- to the first invalid field after validation;
- when opening a new editor with an explicit user action;
- to a result that the person just requested;
- to dismiss the keyboard after an action is complete.

Do not move focus during ordinary model updates, animations, scroll events, or background refresh. Unexpected focus movement makes the person lose their place and can cause VoiceOver or keyboard users to act on the wrong control.

Focus is a state transition, not a decoration. A custom focus ring must not be the only indication of the active control; the semantic control and accessibility tree remain authoritative.

## Focused values connect the focused view to commands

FocusedValues is a collection of state exported by the focused scene or view and its ancestors. A focused value can expose the current document, selection, or command context to a toolbar, menu, scene command, or other ancestor without making every child know about every action.

Use FocusedValue or FocusedBinding when the action belongs to the currently focused context:

    focused editor/document
    -> focused value
    -> toolbar/menu command
    -> explicit validation and mutation

Focused values are optional by design. A command must handle the absence of a focused value, a read-only value, an unavailable document, and a stale revision. Do not treat “a value is focused” as permission to apply a destructive or model-generated change.

FocusedBinding is convenient when the focused value is a Binding. Keep ownership clear: the focused child publishes the binding, while the command surface requests an operation through a typed action or validates the binding before mutation.

## Keyboard shortcuts and raw key presses

Use keyboardShortcut for command-like actions that a person can invoke from the active scene or window. Prefer standard KeyboardShortcut.defaultAction and cancelAction where those semantics fit. Keep custom shortcuts limited to frequent app-specific commands, respect standard system shortcuts, and let the system localize/mirror shortcuts where appropriate.

Use onKeyPress for a focused view that needs to handle a hardware key event directly. It can match a key, set of keys, characters, or key phases, and it returns handled or ignored. Return ignored when the event should continue through normal dispatch.

Choose the layer deliberately:

| Interaction | Route |
| --- | --- |
| Save, apply, cancel, search, new item | Native Button/Toggle with keyboardShortcut |
| Move through a custom focused surface | focusable plus onKeyPress or a documented focus route |
| Editor submit/next field | TextField, submitLabel, onSubmit, FocusState |
| Arrow-key navigation in a custom collection | Focusable children and a bounded key handler |
| Global command with current document context | commands plus FocusedValue/FocusedBinding |

Do not intercept all key presses when a semantic control or command shortcut is sufficient. Avoid key codes that conflict with international layouts, input methods, or system shortcuts. Test hardware keyboard, Full Keyboard Access, text composition, keyboard repeat, and a non-keyboard path.

## Submit and editing behavior

TextField and TextEditor should retain native editing, selection, input method, and accessibility behavior. Use submitLabel to communicate the next step, and onSubmit to perform a deliberate action such as moving to the next field, validating, or starting a bounded request.

For an AI editor:

    text editing
    -> submit or explicit suggestion action
    -> capture text/revision/selection
    -> cancellable proposal
    -> visible review
    -> apply or discard

Do not make a model request on every keystroke unless the product has a clear debounce, cancellation, privacy, and cost policy. A focus change or keyboard dismissal is not an approval action.

## AccessibilityFocusState is a separate channel

AccessibilityFocusState reads and writes the focus used by active accessibility technologies such as VoiceOver. Its value must allow for no accessibility focus, commonly an optional value or Boolean. accessibilityFocused binds a view to that state.

Use accessibility focus for meaningful transitions:

- a validation error that needs immediate attention;
- a newly available result the person explicitly requested;
- an announcement/status element after a completed action;
- a sheet or editor whose focus should begin in a known location.

Do not steal accessibility focus for every streaming token, scroll update, material animation, or model status change. Preserve the person’s current reading location when background work changes.

If a feature has both input focus and accessibility focus, define the order:

    action -> visible state -> semantic status -> optional accessibility focus

The optional focus move should be targeted, localized, and testable. AccessibilityFocusState does not replace a correct label, value, trait, heading, action, or reading order.

## Accessibility actions and interaction

Use native controls first. For a custom view that exposes a meaningful action, use accessibilityAction or accessibilityActions with a clear name and state. Use accessibilityRespondsToUserInteraction deliberately when a custom view’s interaction status needs to be explicit for Switch Control, Voice Control, or Full Keyboard Access.

An accessibility action should:

- have the same effect as the visible action;
- validate the same source revision and permissions;
- announce or expose the resulting state;
- support cancellation and failure;
- not depend on a hidden gesture, pointer hover, or animation;
- remain available when reduced effects are enabled.

## Pointer and focus effects

Pointer input adds precision on iPad and visionOS and is central on Mac. Support the same task with touch, pointer, keyboard, eyes/hands, and assistive technologies where the target supports them. Use system pointer styles and focus effects when they express the platform convention.

Hover can reveal a tooltip, secondary affordance, or pointer feedback, but a consequential action must remain discoverable without hover. Do not use a pointer-only highlight to communicate selection, authorization, or error. Test pointer movement, press-and-hold, modifier keys, focus transitions, hit regions, and touch fallback.

## Focus and Liquid Glass

Functional Liquid Glass groups should be made of native controls whose focus, selection, accessibility, and keyboard behavior remain intact:

- the focused control keeps a visible semantic state;
- a glass group does not absorb focus that belongs to its buttons or fields;
- reduced transparency keeps the same focus and action hierarchy;
- pointer hover does not replace the button label or VoiceOver name;
- a custom glow never becomes the only error or approval cue.

For a custom focus effect, render it around a measured semantic control and test high contrast, Dynamic Type, right-to-left layout, reduced motion, and dark/light appearances. The glass treatment is a shell; focus and action state remain the contract.

## On-device AI and focus

Focus is a useful boundary for model requests:

    focused field or selected range
    -> user action
    -> source revision capture
    -> bounded prompt/context
    -> proposal
    -> review focus or editor selection
    -> explicit apply

The model should not choose which field receives focus, which keyboard shortcut applies a destructive action, or which accessibility element is announced without an app-owned policy. If the model returns a suggested correction, the app can show it near the focused content and let the person accept, edit, or reject it.

When a proposal finishes:

- keep the input focus if the person is still editing;
- move accessibility focus only when the new result is the outcome they requested and the move is helpful;
- preserve the original selection and revision;
- expose generated, stale, filtered, canceled, and approved states in text;
- provide an unavailable route when the model or language asset is not ready.

## Adaptation and privacy

Keyboard, pointer, VoiceOver, Voice Control, Switch Control, Full Keyboard Access, and touch can coexist. Test the complete task under each relevant route rather than only checking a control’s accessibility label.

Do not log raw key presses, typed sensitive text, focused document contents, or accessibility state unless the product has a justified, minimized, consented diagnostic path. Redact model prompts, selection text, and source records from logs and signposts.

## Target and proof register

Record the deployment target, focus/selection APIs, device families, keyboard/pointer/assistive-input claims, localization, target membership, and any UIKit/scene command bridge. Compile the smallest target slice and then test physical devices for touch, keyboard, pointer, VoiceOver, Voice Control, Switch Control, focus visibility, text input, and glass/material behavior.

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
- [Human Interface Guidelines: Entering data](https://developer.apple.com/design/human-interface-guidelines/entering-data)
