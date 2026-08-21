# Capability recipe: reviewable rich text and on-device AI output

## User outcome

Turn a user-approved source or selection into a readable, editable, source-aware draft that can be accepted, corrected, copied, or exported without confusing a model proposal with domain truth.

This route covers summaries, rewrites, extracted notes, action-item proposals, and other text-first features. It is deliberately neutral about which on-device model route supplies the proposal.

## Composition

    source record or selection
    -> immutable source revision
    -> bounded model request
    -> raw proposal
    -> schema/length/content validation
    -> AttributedString or plain-text parse
    -> link and custom-attribute policy
    -> Text/TextEditor review surface
    -> explicit user decision
    -> approved domain record
    -> optional share/export/system projection

| Layer | Responsibility | Never delegate |
| --- | --- | --- |
| Source | Own the user-approved content and revision | Do not let the model replace the source |
| Request | Carry a bounded prompt, selection, locale, and cancellation | Do not include secrets or arbitrary UI instructions |
| Proposal | Hold raw model output and diagnostics | Do not treat it as saved truth |
| Presentation | Parse supported rich text and show status/provenance | Do not allow arbitrary code, actions, or resources |
| Review | Edit, select, apply, discard, retry, or inspect | Do not hide the original content |
| Domain record | Persist only after an explicit apply decision | Do not auto-save based on render completion |
| Projection | Copy, export, share, widget, or App Intent route | Do not project unapproved or stale content as current |

## State machine

    idle
    -> preparing(sourceRevision)
    -> generating(requestID)
    -> proposed(raw, diagnostics)
    -> parsed(draft, warnings)
    -> reviewing(selection?)
    -> applying
    -> approved(newRevision)

    preparing/generating -> canceled
    generating -> unavailable
    proposed/parsed -> failed
    reviewing -> discarded
    applying -> conflict or failed

The state machine should retain the source revision and request ID. If the source changes while a proposal is in flight, mark the proposal stale instead of silently applying it to the new source. If the model, language asset, or parser is unavailable, preserve the source and offer a deterministic fallback.

## Presentation contract

Define a typed, bounded presentation policy:

    struct RichTextPolicy {
        maximumInputCharacters
        maximumOutputCharacters
        supportedMarkdown
        allowedLinkSchemes
        allowedLinkHosts
        maximumSourceSpans
        showsGeneratedLabel
        showsProvenance
    }

The exact type is product-owned. The important rule is that the policy is code-owned and testable. Do not allow a model to return a font name, renderer type, shader, animation duration, arbitrary URL scheme, or action identifier and then apply it without validation.

## Markdown and attributed route

1. Keep the raw model string for audit and correction.
2. Parse with the selected AttributedString Markdown initializer.
3. Choose an explicit failure policy and record whether the result is partial.
4. Keep only supported Foundation and SwiftUI attributes.
5. Inspect links and allow only the product’s schemes/hosts or remove them.
6. Add app-owned source-span or review attributes after the parse.
7. Show warnings close to the draft and expose the original string.
8. Render with Text for read-only review or TextEditor for editable review.

For a small feature, plain text with a “generated draft” label is a safer fallback than a custom Markdown dialect. Rich text is worth the extra route when it materially improves review, source inspection, or export.

## UI composition

    NavigationStack {
        ScrollView {
            SourceContextView(source: source)
            ReviewStatusView(state: state)
            ReviewableTextView(draft: draft)
            ProvenanceButton(spans: draft.spans)
        }
        .safeAreaInset(edge: .bottom) {
            ReviewActions(
                apply: apply,
                edit: edit,
                discard: discard,
                retry: retry
            )
        }
    }

The action shell can use a bounded Liquid Glass group when it improves grouping. Keep the actions as native Buttons and expose the same state when glass is unavailable or reduced. For keyboard editing, test that the inset, focus, selection, and scroll position do not obscure the draft or the apply action.

## Selection-scoped suggestions

For an editor route:

    AttributedTextSelection
    -> selection.indices(in: draft)
    -> source revision check
    -> bounded suggestion request
    -> suggestion preview
    -> apply only to the selected range after review

Do not assume a selection maps to a single contiguous logical range in every writing direction. Keep the selected content and revision in the request payload, and re-check the editor’s current revision before applying.

## Source spans and provenance

Use TextAttribute or AttributedString custom attributes for presentation metadata only after the underlying source mapping is validated. A source span should contain a stable app-owned identifier or range reference, not a model-supplied executable instruction.

Provide at least one non-visual way to inspect a span:

- a details sheet;
- an accessibility label;
- a source link or record identifier;
- a “why am I seeing this?” action;
- a copyable citation/reference.

When spans cannot be mapped confidently, render the text without the highlight and show a general provenance label rather than inventing precision.

## Fallback matrix

| Condition | User-facing route |
| --- | --- |
| Model unavailable | Show source, explain unavailability, offer manual editing or a deterministic template |
| Request canceled | Preserve source and draft status; allow retry |
| Output too long | Truncate before parsing only with a visible warning, or ask for a shorter proposal |
| Markdown parse failure | Show plain text and parse warning; preserve raw output |
| Unsupported attribute | Remove it and continue with a warning when safe |
| Unsafe/disallowed link | Remove or render as non-clickable text; record the policy outcome |
| Source revision changed | Mark proposal stale and require regeneration |
| Selection changed | Keep current selection and discard the old suggestion |
| Apply conflict | Keep draft and source; ask for explicit resolution |
| Reduced effects | Use standard text and material; retain labels and actions |
| Large Dynamic Type | Stack actions and allow text to wrap |
| Right-to-left content | Verify selection, source spans, alignment, and action order |

## Privacy and safety boundary

Keep the source, raw proposal, parsed draft, and approved record in distinct models. State whether source text is processed only on-device, whether any service boundary exists, how long raw proposals are retained, and how deletion works. Redact sensitive text from logs and signposts.

An on-device model may improve privacy and latency, but it does not make output correct. A local parse does not prove link safety, provenance, or content quality. A user tap on Apply is an explicit approval boundary, not a guarantee that the proposal is accurate.

## Target register

Record:

- deployment target and SDK;
- Foundation Models or other generation route, if used;
- AttributedString and TextRenderer availability branch;
- TextEditor selection support;
- localization resources and supported scripts;
- any ShareLink, Transferable, App Intent, widget, or document extension target;
- privacy and retention behavior;
- fixture pack and review/device proof.

## Proof packet

Capture the source revision, raw proposal, parse diagnostics, policy decisions, visible draft, selection/apply action, resulting approved record, and any export/system projection. Add VoiceOver, Dynamic Type, right-to-left, reduced effects, long text, link safety, cancellation, stale source, and model-unavailable evidence.

## Sources

- [AttributedString](https://developer.apple.com/documentation/foundation/attributedstring)
- [Instantiating attributed strings with Markdown syntax](https://developer.apple.com/documentation/foundation/instantiating-attributed-strings-with-markdown-syntax)
- [MarkdownParsingOptions](https://developer.apple.com/documentation/foundation/attributedstring/markdownparsingoptions)
- [Text](https://developer.apple.com/documentation/swiftui/text)
- [TextEditor](https://developer.apple.com/documentation/swiftui/texteditor)
- [TextRenderer](https://developer.apple.com/documentation/swiftui/textrenderer)
- [TextAttribute](https://developer.apple.com/documentation/swiftui/textattribute)
- [Text.Layout](https://developer.apple.com/documentation/swiftui/text/layout)
- [Text.LayoutKey](https://developer.apple.com/documentation/swiftui/text/layoutkey)
- [TextSelection](https://developer.apple.com/documentation/swiftui/textselection)
- [AttributedTextSelection](https://developer.apple.com/documentation/swiftui/attributedtextselection)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Human Interface Guidelines: Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
- [Human Interface Guidelines: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Human Interface Guidelines: Right to left](https://developer.apple.com/design/human-interface-guidelines/right-to-left)
