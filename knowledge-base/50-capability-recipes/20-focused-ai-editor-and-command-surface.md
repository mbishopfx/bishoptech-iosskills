# Capability recipe: focused AI editor and command surface

## User outcome

Build an editor or review surface where a person can type, select, invoke a bounded on-device suggestion, inspect the proposal, and apply or discard it using touch, keyboard, pointer, and accessibility routes.

## Composition

    TextField/TextEditor
    -> FocusState and text/selection state
    -> explicit submit or suggestion action
    -> source revision capture
    -> bounded model proposal
    -> review surface
    -> FocusState/AccessibilityFocusState policy
    -> apply/edit/discard
    -> optional focused command/system projection

| Layer | Responsibility | Boundary |
| --- | --- | --- |
| Editor | Own text, selection, focus, input method, and validation | Do not replace it with a visual canvas without a real need |
| Command context | Expose the focused document/action set | Optional focused values; nil-safe and revision-checked |
| Proposal | Hold generated text/attributes and diagnostics | Never approved truth |
| Focus policy | Decide input/accessibility focus after explicit transitions | Never model-controlled without app policy |
| Apply action | Validate source revision and persist | User-visible, cancellable, failure-aware |
| Projection | Share, App Intent, widget, or command | Project only approved/current state |

## State model

    editor: empty | editing | selection | invalid | unavailable
    inputFocus: none | title | body | search
    accessibilityFocus: none | error | proposal | status
    proposal: none | preparing | generating | ready | stale | canceled | rejected
    decision: none | reviewing | applying | approved | discarded | failed
    command: unavailable | available | disabled | executing

Keep inputFocus and accessibilityFocus separate. A person may continue editing while VoiceOver is moved to a concise validation result, or inspect a proposal without changing the editor’s selection.

## Build order

1. Build the native editor and validation route.
2. Add FocusState for deliberate field transitions.
3. Add submit labels and visible error copy.
4. Add a visible suggestion button with a native shortcut only if the action is frequent.
5. Capture the source revision, selection, locale, and privacy boundary.
6. Generate a bounded proposal with cancellation and unavailable states.
7. Show the proposal in Text/TextEditor with selection/source review.
8. Move accessibility focus only for a meaningful requested result or error.
9. Expose focused document actions with FocusedValues/FocusedBinding if needed.
10. Apply only after revision, permission, and validation checks.
11. Add Liquid Glass grouping after the input and command behavior works without effects.

## Focus policy

Use a typed policy:

    onOpen: focus the first useful field only when the person started editing
    onSubmit: move to the next field or validate
    onError: focus the first invalid input and expose its message
    onProposalReady: keep input focus; optionally focus a concise result after an explicit request
    onApply: keep or dismiss focus according to the editing task and actual success
    onCancel: restore the prior focus/selection when possible

Do not move focus every time model tokens arrive. Do not move accessibility focus to a long generated paragraph when a short status/result label can explain what changed.

## Focused command surface

Publish only the current focused context:

    focused editor/document
    -> toolbar/menu/scene command
    -> current action availability
    -> explicit apply/copy/export/cancel

The command must be nil-safe when no editor is focused, disabled when the current revision is stale, and unavailable when permissions or model readiness are missing. A keyboard shortcut should activate the same semantic action as the visible Button.

## Selection-scoped suggestion

For a selected range:

    selected text and range
    -> source revision
    -> bounded prompt
    -> proposal
    -> compare/replace review
    -> explicit apply

Preserve the original selection until the suggestion is accepted or discarded. Revalidate the range after an edit or concurrent update. For bidirectional text, test the visual selection and logical range on the actual target.

## Accessibility route

Expose:

- field labels, hints, values, and errors;
- proposal state: generated, partial, stale, unavailable, or approved;
- named Apply, Edit, Copy, Export, Retry, and Discard actions;
- a concise result/status element for a requested generation;
- accessibility actions for custom review controls;
- focus movement only where it reduces search cost for the person.

Keep the same actions available through VoiceOver, Voice Control, Switch Control, Full Keyboard Access, and pointer/keyboard routes where the platform supports them.

## Liquid Glass shell

Use a bounded glass group around action controls or a small status cluster:

    editor/content
    -> safe-area-owned toolbar/inset
    -> native action controls
    -> glass/material fallback

The group must not own text focus, obscure the keyboard, or make the proposal look approved merely because it is glowing. Reduced transparency keeps the same labels, action order, state, and focus.

## Fallback matrix

| Condition | Route |
| --- | --- |
| No input focus | Keep visible action disabled or explain what must be selected |
| Validation error | Focus invalid field; expose a concise accessible error |
| Model unavailable | Keep editing and manual workflow usable |
| Proposal canceled | Preserve source text, selection, and retry action |
| Proposal stale | Show stale state; require regeneration |
| Selection changed | Discard or rebase only through an explicit policy |
| No focused command context | Hide or disable context action; never target an arbitrary document |
| Large Dynamic Type | Stack actions and keep error/result text visible |
| Right-to-left | Test focus order, selection, labels, and shortcut mirroring |
| Reduce Motion/Transparency | Preserve semantic focus/actions with static/material fallback |
| Keyboard dismissed | Keep apply/retry reachable without requiring keyboard restoration |

## Privacy and proof packet

Record the source revision, selected range policy, model availability, raw/proposed/approved separation, focus transitions, accessibility focus transitions, command context, and final decision. Redact typed text, prompts, and source documents from diagnostics unless explicitly justified.

## Sources

- [Focus](https://developer.apple.com/documentation/swiftui/focus)
- [FocusState](https://developer.apple.com/documentation/swiftui/focusstate)
- [FocusedValues](https://developer.apple.com/documentation/swiftui/focusedvalues)
- [FocusedBinding](https://developer.apple.com/documentation/swiftui/focusedbinding)
- [Input events](https://developer.apple.com/documentation/swiftui/input-events)
- [KeyboardShortcut](https://developer.apple.com/documentation/swiftui/keyboardshortcut)
- [AccessibilityFocusState](https://developer.apple.com/documentation/swiftui/accessibilityfocusstate)
- [Accessible controls](https://developer.apple.com/documentation/swiftui/accessible-controls)
- [TextField](https://developer.apple.com/documentation/swiftui/textfield)
- [TextEditor](https://developer.apple.com/documentation/swiftui/texteditor)
- [TextSelection](https://developer.apple.com/documentation/swiftui/textselection)
- [AttributedTextSelection](https://developer.apple.com/documentation/swiftui/attributedtextselection)
- [TextRenderer](https://developer.apple.com/documentation/swiftui/textrenderer)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Human Interface Guidelines: Focus and selection](https://developer.apple.com/design/human-interface-guidelines/focus-and-selection)
- [Human Interface Guidelines: Keyboards](https://developer.apple.com/design/human-interface-guidelines/keyboards)
- [Human Interface Guidelines: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
