# Sheets, Forms, and Focused Editing

## Product rule

A sheet or editor should make one focused task easier to complete. It should have a clear entry reason, an explicit draft/commit boundary, predictable dismissal, and enough context to recover from validation or permission failure.

## Choose the presentation

| Need | First route | State to expose |
| --- | --- | --- |
| Short confirmation | Alert or confirmation dialog | Pending, confirmed, canceled, failed |
| Focused creation/review | `.sheet` with `Form`/editor | Draft, validation, saving, saved, discarded |
| Inspect a related item without leaving context | Sheet/popover or navigation destination | Selected item, stale/deleted, loading, unavailable |
| Settings/preferences | Native settings screen or focused navigation destination | Current value, pending change, permission/status |
| Long-running task | Dedicated screen plus system progress projection if appropriate | Queued, running, paused, canceling, completed, failed |

Use `presentationDetents` when a sheet has meaningful natural sizes, `presentationDragIndicator` when resizing/dismissal is not otherwise obvious, and the current presentation sizing/background/content-interaction APIs only after verifying the selected SDK. Do not use a custom sheet to imitate a system surface that already expresses the task.

## Draft and commit model

`presented -> loading? -> draft -> editing -> validating -> saving -> saved|failed -> dismissed`

Keep these values separate:

- source record or captured input;
- editable draft;
- validation errors/warnings;
- save operation/progress;
- committed domain record;
- external side effect such as calendar write, purchase, device command, or notification.

Dismissal rules must be explicit:

- If the draft is unchanged, dismiss normally.
- If the draft is dirty, offer discard/keep editing/save according to product policy.
- If saving is in progress, disable duplicate commit or provide a cancellable operation.
- If the sheet is dismissed by a system gesture, preserve or discard only according to the documented product rule; never silently report a save.

## Form composition

- Use `Form`, `Section`, `TextField`, `TextEditor`, `Picker`, `Toggle`, `DatePicker`, `Stepper`, and semantic buttons before custom controls.
- Keep the primary commit action in a toolbar or safe-area bar when it remains visible and does not cover the keyboard/content.
- Show field-level errors near the field and a summary/announcement for screen-reader users when multiple fields fail.
- Preserve entered text when a permission, network, model, or external-store request fails.
- Use `ContentUnavailableView` or a clear inline state when the source is missing/stale; do not leave a blank glass panel.
- Keep destructive actions separate from the primary save action and require appropriate confirmation.

## Focus choreography

Use `@FocusState` to move between fields after a deliberate submit or validation result, not on every state update.

| Event | Focus behavior |
| --- | --- |
| Sheet appears | Focus the first field only when it is clearly the task’s first step and it does not surprise VoiceOver/keyboard users. |
| Submit valid field | Move to the next field or resign focus with a clear label. |
| Validation failure | Move to the first invalid field and expose visible/localized error text. |
| Save succeeds | Announce the saved state and move/dismiss according to the product flow; do not hide confirmation in animation. |
| Save fails | Preserve focus/draft, expose retry/error, and keep the sheet open unless the person chooses to leave. |
| Accessibility focus | Verify focus order and announcements independently from keyboard focus. |

Test hardware keyboard, VoiceOver editing, Voice Control, Switch Control, Dynamic Type, input methods, RTL, and keyboard/sheet detent interaction.

## AI and capture review editor

For OCR, transcription, translation, Foundation Models, or sensor-derived proposals:

1. Show the source or source reference.
2. Label generated/observed fields and uncertainty.
3. Let the person edit values directly.
4. Validate deterministic constraints before enabling commit.
5. Commit only after explicit approval.
6. Preserve the source/provenance and allow discard/retry/export.

The sheet’s glass, transition, or “smart” copy must never imply that a generated proposal is already domain truth.

## Liquid Glass and sheet surfaces

- Let the system supply the sheet, toolbar, form, and controls’ current material treatment.
- Use custom glass only for a compact action/status group that clarifies the task; avoid translucent backgrounds behind dense form text.
- Test detents, drag indicator, keyboard, safe areas, Dynamic Type, reduced transparency, reduced motion, high contrast, and light/dark appearance.
- Keep the commit action and error state legible when the sheet is small or partially covered.
- If a custom glass group morphs between draft/saving/saved controls, preserve stable IDs and remove the morph under Reduce Motion while keeping the labels/actions.

## Proof plan

- Previews: pristine/dirty draft, field errors, save progress, saved, discard confirmation, permission denied, unavailable source, and model/capture failure at all supported text sizes.
- Simulator/UI tests: present/dismiss, detents, keyboard, focus, validation, duplicate taps, deep links, and state restoration.
- Physical device: touch/keyboard/VoiceOver/Voice Control/Switch Control, sheet gestures, text input/localization, reduced effects, and haptic/animation behavior.
- Signed/release: permission copy, privacy resources, system picker/store/entitlement behavior, App Intent/notification entry, and production side-effect/account state.

## Sources

- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Presentation modifiers](https://developer.apple.com/documentation/swiftui/view-presentation)
- [presentationDetents](https://developer.apple.com/documentation/swiftui/view/presentationdetents%28_%3A%29)
- [presentationDragIndicator](https://developer.apple.com/documentation/swiftui/view/presentationdragindicator%28_%3A%29)
- [Presentation sizing](https://developer.apple.com/documentation/swiftui/presentationsizing)
- [Form](https://developer.apple.com/documentation/swiftui/form)
- [FocusState](https://developer.apple.com/documentation/swiftui/focusstate)
- [AccessibilityFocusState](https://developer.apple.com/documentation/swiftui/accessibilityfocusstate)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [accessibilityReduceMotion](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion)
- [accessibilityReduceTransparency](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducetransparency)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Performing accessibility testing for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)
