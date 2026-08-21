# Rich AI text and Apple-native typography

## Design thesis

The most convincing Apple-native text treatment is usually disciplined hierarchy, generous readable spacing, and native behavior under pressure. Rich AI output should feel like a useful document or review surface first, and a model surface second.

Use this loop:

    human task
    -> text hierarchy
    -> native input/output control
    -> source and review state
    -> adaptive typography
    -> bounded visual emphasis
    -> accessibility and device proof

Do not copy private Apple app layouts or trademarks. Use Apple’s public design principles and system behaviors as a foundation, then make the product’s own information architecture and voice recognizable.

## Typography is structure

Apple’s Human Interface Guidelines describe typography as a way to support legibility, information hierarchy, important content, and style. On iOS and iPadOS, the HIG lists 17 points as the default size and 11 points as the minimum reference for text, while also emphasizing that weight and context affect legibility. Treat those figures as design guidance, not permission to make every view a fixed-size type sample.

Define a small semantic type scale:

| Role | Job | Behavior |
| --- | --- | --- |
| Screen title | Orient the person | Large semantic style; may wrap or collapse in compact width |
| Section heading | Group related content | Heading semantics; remains distinct at larger text sizes |
| Primary value | Carry the main result | Strong weight and contrast; never communicates meaning by color alone |
| Supporting text | Explain, qualify, or show provenance | Comfortable body style; allowed to wrap |
| Metadata | Show source, timestamp, model state, or status | Secondary contrast but still readable; do not shrink below a useful size |
| Action label | Name the next step | Native control typography and sufficient hit area |
| Review annotation | Explain generated or selected content | Textual label plus optional restrained highlight |

Use the system font and semantic SwiftUI font styles unless a product requirement supports a tested custom font. Mixing many typefaces or thin weights can weaken hierarchy and readability.

## The AI review shell

For summaries, rewrite suggestions, extracted notes, and generated explanations, use a three-layer screen:

1. Context: what source, record, or selection is being considered.
2. Proposal: the generated or transformed text, visibly marked as draft or suggestion.
3. Decision: apply, edit, copy, export, retry, or discard actions.

The proposal should never visually impersonate the approved record. A small “Suggested” label, source detail, revision timestamp, or review state is more useful than a persistent glowing AI badge.

### A native composition

    NavigationStack
      ScrollView
        source context
        heading and status
        reviewable text surface
        source/provenance affordance
        primary apply action
        secondary edit/copy/export actions

Place the reviewable text in a measured surface. A bounded glass group can provide visual grouping, but the text must retain hierarchy and contrast if the glass effect is disabled. Put the apply action in a toolbar, bottom safe-area inset, or clearly owned content region according to the task and keyboard state.

## Rich text without visual noise

Use AttributedString for meaning-bearing inline attributes: emphasis, links, writing direction, supported SwiftUI text attributes, and app-owned review metadata. Use TextRenderer for a small visual layer that follows the placed text.

Good rich-text treatments:

- a soft background behind source-backed spans;
- a subtle marker for a selected suggestion;
- a restrained animation when a review state changes;
- a layout-aware underline or accent that follows a line wrap;
- a focused mask for privacy or redaction review;
- a provenance tint paired with text and an inspectable source action.

Risky treatments:

- rainbow or animated text for ordinary body copy;
- a blur or glow that makes the text harder to read;
- highlighting that says “high confidence” without a validated confidence contract;
- a custom shader that disappears when Reduce Motion or Reduce Transparency is on;
- a renderer that suppresses the underlying text in an error or unsupported state;
- a dense annotation layer that works only in English at default text size.

## Glass grouping rules for text

Use functional groups rather than decoration:

- group a title, current value, and one or two related actions;
- maintain enough inset for the longest supported label;
- avoid a glass pill around a paragraph when a normal card or scroll surface is clearer;
- keep an opaque or standard-material route for reduced transparency;
- verify text over both light and dark backgrounds;
- do not put a glass treatment behind every run of a paragraph;
- keep status and source labels close enough to the content they qualify.

When a text renderer adds a highlight, draw it behind the underlying text and retain the same text content for VoiceOver. If a visual annotation is actionable, add a real Button, Link, or editor interaction with an accessibility label. A painted rectangle is not a control.

## Dynamic Type and adaptive composition

Dynamic Type changes more than font size. It changes the space needed for hierarchy, wrapping, controls, annotations, and the decision surface. Design for these transitions:

    standard width + standard type
    -> compact width
    -> large text
    -> accessibility text
    -> keyboard/editing
    -> right-to-left
    -> reduced effects

At larger sizes:

- let supporting text wrap;
- move actions below the proposal or into a menu;
- keep the apply action visible;
- increase or preserve meaningful icon size;
- avoid truncating the only explanation of generated content;
- use fewer simultaneous annotations;
- verify that source labels remain associated with the correct paragraph.

Prefer SwiftUI’s layout and type adaptation rather than fixed geometry breakpoints. A review surface that survives a narrower container and larger text feels more native than one that merely resembles a screenshot at one size.

## Selection as a design signal

Selection is a powerful bridge between editing and AI:

    tap/drag selection
    -> visible selection affordance
    -> suggestion scoped to the selection
    -> side-by-side or inline proposal
    -> explicit apply

Keep selection visual state separate from generated state. A selected range can be empty, stale after editing, or in a different writing direction. Make the next action explicit and allow the person to return to the complete draft.

## Content hierarchy for generated text

Generated content tends to be longer, more variable, and less trustworthy than authored UI copy. Build a display contract:

- maximum source and output lengths;
- explicit title/summary/body sections;
- source timestamp or revision;
- warning for partial or stale content;
- supported Markdown subset;
- link policy;
- optional source spans;
- truncation and expansion behavior;
- “not available” and cancellation states.

The display contract belongs to the app. The model may fill a proposal, but it should not choose arbitrary colors, animation duration, interaction grammar, or system actions.

## Accessibility and inclusion

Apple’s guidance treats legibility, accessible text sizing, contrast, VoiceOver, and inclusive language as design work. Apply that directly to AI surfaces:

- provide a textual label for generated, selected, stale, and approved states;
- expose links and headings as semantic elements;
- do not rely on a highlight or color to show source provenance;
- keep generated copy plain enough to understand and edit;
- announce completion, failure, or cancellation through an appropriate state change;
- test long names, diacritics, emoji, mixed scripts, and right-to-left content;
- ensure focus and keyboard order make sense when a suggestion appears;
- allow people to enlarge text without hiding the decision action;
- review custom font behavior if a custom font is used.

## A small visual language

Use a limited visual vocabulary:

    neutral: user-authored or established content
    secondary: provenance and supporting metadata
    accent: the current selection or primary action
    caution: partial, stale, or needs-review state
    success: approved/saved state after a real state transition

Every state still needs text or structure. Never show success because a renderer finished drawing, or show confidence because a model returned a number without a defined evaluation path.

## Source and device proof

The design page is a decision guide, not proof that a custom renderer compiles or that Liquid Glass looks the same on every device. A target project must verify:

- the exact SDK and availability branch;
- text and selection signatures;
- the actual font, content, width, locale, and color scheme;
- VoiceOver, Dynamic Type, right-to-left, reduced effects, and keyboard behavior;
- long-output memory and rendering performance;
- physical touch and glass/material behavior where used;
- screenshots or recordings of draft, approved, stale, failed, and fallback states.

## Sources

- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Human Interface Guidelines: Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
- [Human Interface Guidelines: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Human Interface Guidelines: Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles)
- [Human Interface Guidelines: Right to left](https://developer.apple.com/design/human-interface-guidelines/right-to-left)
- [Text](https://developer.apple.com/documentation/swiftui/text)
- [TextRenderer](https://developer.apple.com/documentation/swiftui/textrenderer)
- [TextAttribute](https://developer.apple.com/documentation/swiftui/textattribute)
- [Text.Layout](https://developer.apple.com/documentation/swiftui/text/layout)
- [AttributedString](https://developer.apple.com/documentation/foundation/attributedstring)
- [TextSelection](https://developer.apple.com/documentation/swiftui/textselection)
- [AttributedTextSelection](https://developer.apple.com/documentation/swiftui/attributedtextselection)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
