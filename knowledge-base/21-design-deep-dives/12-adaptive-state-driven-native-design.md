# Adaptive, State-Driven Apple-Native Design

Apple-like polish is not a fixed screenshot. It is a stable hierarchy that adapts when content, window size, Dynamic Type, language, input method, accessibility settings, device family, and feature readiness change. Design the state and task flow first; choose Liquid Glass, layout, motion, and decoration only after the person’s next action is clear.

## The native screen contract

Write one contract before composing a screen:

| Layer | Question | Example |
| --- | --- | --- |
| Outcome | What is the person trying to finish? | Review and save a proposed record. |
| Content | What must remain readable? | Source, generated proposal, provenance, validation issue. |
| Primary action | What is the next safe action? | Edit, approve, retry, or continue manually. |
| Secondary actions | What can be deferred or discovered? | Share, duplicate, help, settings, delete. |
| System context | What belongs to Apple’s UI or another target? | Permission sheet, share sheet, App Intent, keyboard, notification. |
| Adaptation | What changes without changing the outcome? | Row-to-column layout, toolbar-to-menu, sheet-to-navigation route. |
| Proof | How will we know the task works? | Compile, fixture, accessibility task, physical device, system surface. |

The content layer should not depend on a glass effect to be understandable. The action layer may use system controls, toolbar placement, or a small `GlassEffectContainer` when the material communicates functional grouping. System-owned surfaces should remain system-owned.

## State is part of the visual hierarchy

Model the states the person can actually encounter:

```text
idle
 -> loading/readiness check
 -> content
 -> empty
 -> restricted/unavailable
 -> error/recovery
 -> editing/review
 -> committing
 -> committed
```

For intelligence features, keep model availability, input validity, proposal trust, user draft, and commit result separate. For device features, keep permission, hardware readiness, capture, processing, and accepted result separate. A disabled button, spinner, blur, or transition is not a state contract by itself.

Every state should answer:

- what content remains visible;
- what the person can do next;
- what happened and why, in plain language;
- how to recover without losing confirmed work;
- where accessibility focus should move;
- whether a system surface or permission is required;
- what evidence is needed before making a product claim.

## Adapt by proposal, not by guessed device names

SwiftUI provides composition tools for responding to available space and environment values. Use them in this order:

1. use semantic controls and system containers first;
2. allow text and controls to wrap or stack naturally;
3. use `ViewThatFits` when there are a few deliberate alternatives for the same task;
4. use `AnyLayout` when the container should change without destroying subview state;
5. use a custom `Layout` only when the repeated layout rule is real and testable;
6. use platform/size-class/availability conditions for genuine capability differences, not for arbitrary pixel tuning.

`ViewThatFits` evaluates its children in the order provided and chooses the first that fits the constrained axes. Put the preferred, most informative alternative first, followed by compact fallbacks. Do not hide the primary action merely because a label is long; move secondary actions into a menu or a focused route.

`AnyLayout` can switch between layout containers while preserving subview identity and state. This is useful for a review surface that is horizontal in a regular width and vertical when Dynamic Type or a compact width makes the horizontal arrangement unsafe.

Use custom `Layout` when the arrangement itself is a reusable design rule. Keep measurement independent of business state, test long labels and empty content, and avoid using geometry to create a fixed screenshot that fails in another locale.

## Adaptation matrix

| Context | Preferred response | Common failure |
| --- | --- | --- |
| Compact width | Keep content readable; move secondary actions to a menu/sheet; preserve the primary action | Shrinking every control until labels become icons or truncation. |
| Regular width/iPad | Use columns, split views, inspectors, or a wider reading region when the task benefits | Stretching a phone card across the window without adding useful hierarchy. |
| Large Dynamic Type | Let text wrap, increase vertical space, and change layout when needed | Fixed-height glass capsules and clipped generated text. |
| Right-to-left locale | Use leading/trailing semantics, localized formatting, and reading-order checks | Hard-coded left/right offsets and directional icons that imply the wrong action. |
| Long localization | Test the longest realistic labels and plural forms; prioritize content over decoration | Designing around English string lengths. |
| Increased contrast/reduced transparency | Use a readable opaque or standard-material fallback and maintain separation | Making meaning depend on blur, translucency, or a subtle tint. |
| Reduce Motion | Keep the same state and focus destination while reducing morphs, bounce, parallax, and depth changes | Removing feedback so the person cannot tell that a task completed. |
| VoiceOver | Expose source, proposal, validation, and actions in a deliberate reading order | Treating a decorative glass container as the semantic action. |
| Voice Control/Switch Control/keyboard/pointer | Provide named, discoverable, non-gesture paths | Making a swipe or drag the only route to completion. |
| Assistive Access | Simplify to the core workflow, reduce cognitive load, and confirm hard-to-recover actions | Assuming the default dense layout is usable in every system mode. |
| Device/orientation change | Preserve draft and navigation state; recompose the surface | Resetting the feature or losing an in-progress review. |

## Liquid Glass belongs to the functional layer

Use the system’s native controls and containers before applying custom material. When custom Liquid Glass adds useful grouping:

- group related controls with `GlassEffectContainer`;
- keep spacing and membership intentional;
- use stable identities only for genuine relationships across transitions;
- keep generated content, source evidence, and validation messages outside the effect when the material would reduce reading clarity;
- provide a standard-material or opaque fallback for increased contrast/reduced transparency;
- keep the same label, action, and focus behavior when morphing is reduced or removed.

Do not use a glass effect to imply model readiness, confidence, authorization, or a saved result. Drive both the content and the action cluster from the same state reducer, and render the canonical domain result only after the domain service confirms the commit.

## A compositional pattern for reviewable features

```text
NavigationStack
  -> source/provenance region
  -> readable proposal/editor
  -> validation or unknown-state explanation
  -> compact action group
       -> Edit / Reject / Approve / Retry / Cancel
  -> committed result or recovery route
```

Use `Form`, `TextEditor`, `List`, `ContentUnavailableView`, `ProgressView`, `Button`, `Menu`, `sheet`, and `confirmationDialog` according to the task. A review sheet should let the person inspect and correct the proposal before a consequential action. A confirmation dialog is useful for a small final choice; it is not a substitute for editing a generated record.

If a system surface such as a permission prompt, share sheet, App Intent, Writing Tools, or Image Playground is involved, the app should explain the handoff and resume from a durable state. Do not mimic a system-owned surface with app-owned glass merely to keep the visual shell consistent.

## Design tokens are constraints, not a skin

Keep a small semantic design vocabulary:

| Token group | Use |
| --- | --- |
| Role | Primary content, secondary content, warning, error, success, disabled, unknown. |
| Type | System text styles and scalable metrics, with hierarchy tied to reading order. |
| Spacing | A limited rhythm that can expand when text or controls require it. |
| Shape/material | Native control styles first; custom glass only for a functional cluster. |
| Motion | State feedback with a reduced-motion alternative. |
| Interaction | Semantic Button/Menu/Toggle/NavigationLink and named accessibility actions. |
| Layout | Reusable composition rules, not screen-specific coordinates. |

The token layer should make an original product coherent while leaving room for platform adaptation. “Replica” quality should mean that hierarchy, typography, controls, focus, material, and motion feel native—not that proprietary Apple screens or branding are copied.

## Proof-oriented design review

Run a task-based matrix, not just a screenshot review:

| Test | What to observe |
| --- | --- |
| Normal content | Primary outcome, hierarchy, reading order, and action discoverability. |
| Empty/loading/error/restricted | Explanation, recovery, cancellation, and preserved confirmed content. |
| Long content/large type | No clipped text, hidden action, or unusable editor. |
| Localization/RTL | Reading order, formatting, icon direction, and layout recomposition. |
| Reduced motion/transparency/contrast | Same meaning and task completion with reduced visual effects. |
| VoiceOver/Voice Control/Switch Control | Can the person find, understand, edit, reject, and commit the feature? |
| Compact/regular/orientation | No lost state; primary action remains reachable. |
| Physical device | Material legibility, touch targets, input ergonomics, performance, and thermal behavior. |
| System surface | Real permission, share, App Intent, notification, widget, or other handoff on the named configuration. |

## Sources

- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles)
- [Layout](https://developer.apple.com/design/human-interface-guidelines/layout)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
- [Designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [ViewThatFits](https://developer.apple.com/documentation/swiftui/viewthatfits)
- [AnyLayout](https://developer.apple.com/documentation/swiftui/anylayout)
- [Layout](https://developer.apple.com/documentation/swiftui/layout)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Dynamic Type](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [GlassEffectTransition](https://developer.apple.com/documentation/swiftui/glasseffecttransition)
- [ContentUnavailableView](https://developer.apple.com/documentation/swiftui/contentunavailableview)
- [Presentation modifiers](https://developer.apple.com/documentation/swiftui/view-presentation)
