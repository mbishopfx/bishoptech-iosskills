# Native typography and rich-editor design

Typography is the primary surface of a document product. Liquid Glass can
organize tools around the text, but it should never compete with the words,
selection, cursor, or review decision that the person came to make.

Use this composition contract:

~~~text
meaningful content
  -> platform text style and readable measure
  -> selection/focus/editing affordance
  -> optional annotation or proposal state
  -> semantic action group
  -> restrained native material
~~~

The target is an original app that feels at home on Apple platforms: system
typography, strong hierarchy, adaptive layout, recognizable controls, clear
focus, and useful system behavior. It is not a pixel copy of a proprietary
Apple screen.

## Choose the text surface before styling it

| Product need | Native starting point | Add only when needed |
| --- | --- | --- |
| Short read-only content | SwiftUI Text or Label | AttributedString for run-level formatting |
| Selectable article or result | Text with text selection | TextSelection state and accessibility review |
| Long-form editing | SwiftUI TextEditor | UIKit bridge when selection, formatting, or system editor behavior needs it |
| Rich document editing | UITextView with TextKit 2 | Custom viewport or attachment surface |
| Custom text effects | TextRenderer | TextAttribute and a bounded visual effect |
| Exact glyph/export layout | Core Text | Explicit hit testing, selection, accessibility, and export proof |

Do not begin with a custom canvas because the desired screenshot has unusual
spacing. First determine whether a system text view, AttributedString, a custom
layout, or TextRenderer already provides the behavior. The more custom the
renderer, the more the product must prove.

## Typographic hierarchy

Use a small semantic scale:

| Role | Visual job | Design rule |
| --- | --- | --- |
| Screen title | Names the current destination | Prefer a system title style and let the navigation shell own placement |
| Section heading | Groups content | Preserve heading semantics for VoiceOver and scanning |
| Lead or summary | Gives orientation before detail | Keep measure short enough to scan without shrinking the type |
| Body | Carries the main content | Optimize line length, leading, contrast, and selection |
| Metadata | Supports the body | Lower emphasis, never so small that it becomes a hidden requirement |
| Utility/action label | Explains a control | Let the control remain recognizable at larger text sizes |
| Code or structured value | Preserves exact characters | Use a suitable monospaced system design and copy/select behavior |

The HIG recommends system text styles and a restrained number of typefaces.
System fonts adjust across Dynamic Type sizes and accessibility categories.
Avoid thin weights at small sizes; hierarchy should survive larger text, bold
text, increased contrast, and a longer localized string.

For a custom font, make the scaling policy explicit. In UIKit, UIFontMetrics
can scale a custom UIFont for a text style and can scale related layout values.
In SwiftUI, use a dynamic Font route and verify the custom font at the largest
supported accessibility sizes. Do not fix a clipping problem by silently
reducing the user's chosen text size.

## The document reading surface

A native reader/editor usually benefits from this structure:

~~~text
navigation title and document state
  -> readable text column or editor surface
  -> inline selection/annotation state
  -> bottom or top action group
  -> optional inspector or review sheet
~~~

Keep the text surface visually quiet:

- use a readable measure rather than filling every pixel;
- use alignment and spacing to communicate hierarchy before adding color;
- keep selection highlights visible in light, dark, high-contrast, and
  increased-contrast settings;
- place destructive or irreversible actions away from frequent formatting
  actions;
- let the keyboard and safe areas reshape the layout rather than cover the
  current insertion point;
- keep the primary text readable while an asynchronous proposal loads.

For a long document, a sticky toolbar or floating control should not obscure
the current paragraph. A glass toolbar can be visually light while remaining
semantically explicit: each button needs a label, state, and action. Avoid
stacking several translucent surfaces over a paragraph, image, or selection.

## Liquid Glass around text

Use system Liquid Glass APIs for controls and containers that float above the
document. The glass surface should group related actions, not become the
document background or a blurred replacement for readable content.

Good boundaries:

- a formatting toolbar that contains real buttons and menus;
- a review action group with Accept, Reject, and More actions;
- a compact status pill that exposes a model or sync state;
- an inspector that opens after a selection or document action;
- a navigation control that remains legible over changing content.

Poor boundaries:

- a glass layer over every paragraph;
- a custom blur that hides selected or focused text;
- an animated background that competes with reading;
- a fake system toolbar that has no semantic controls;
- an AI-generated color or material that can lower contrast.

Use a glass container to express grouping and identity. Use the text hierarchy
to express meaning. If the glass is removed under reduced-transparency or a
fallback appearance, the editor must remain fully understandable.

## Selection, cursor, and focus

Selection is a first-class state, not a decorative highlight. Design for:

- a collapsed insertion point and an extended selection;
- a noncontiguous or logical selection where the text system supports it;
- selection handles and keyboard selection;
- selection across bidirectional text;
- a stale selection after an edit or document reload;
- VoiceOver focus and Full Keyboard Access;
- pointer, trackpad, Pencil, and hardware keyboard input where applicable.

Keep the selection's document identity separate from its screen frame. Recompute
the frame after width, font, locale, or Dynamic Type changes. If a review action
is attached to a selection, show which source span it refers to and invalidate
the action when the source revision changes.

Focus should move with intent:

- open a document with the correct first responder policy;
- do not steal focus when a background model result arrives;
- keep the selected text visible when the keyboard changes the viewport;
- return focus to the editor after accepting or rejecting a proposal;
- expose toolbar actions through keyboard and accessibility paths.

## Rich formatting and annotations

Separate authoring attributes from review attributes:

| Kind | Examples | Persistence |
| --- | --- | --- |
| Authoring | Font, paragraph style, link, list, emphasis | Part of the document format |
| System/editor | Selection, typing attributes, insertion point | View/editor state |
| Review | Suggested replacement, confidence label, source ID, stale marker | Proposal record, not hidden text |
| Rendering-only | Temporary highlight, hover state, focus ring | Recomputed from state |

AttributedString is a useful value-type boundary for content with ranges,
formatting, links, accessibility metadata, and custom attributes. It can also
be initialized from Markdown and localized resources. Restrict the attributes
that a rendering surface accepts; arbitrary attributes should not leak into a
route that ignores them.

For an AI review surface, prefer an explicit structure:

~~~text
document revision 41
  -> source span: paragraph 3, stable ID p3, original text hash
  -> proposal: replacement + rationale + model route/version
  -> review state: pending
  -> visible mark: optional, non-destructive
  -> actions: accept, reject, edit, dismiss
  -> commit: new revision 42
~~~

The rationale should be optional, concise, and clearly generated. Do not imply
that a model's highlight is a fact, diagnosis, proof, or user intent. A
proposal that changes a person's words should remain inspectable and
reversible.

## Custom rendering without losing semantics

TextRenderer is appropriate for a bounded visual treatment such as a subtle
highlight, a run-level outline, or an effect driven by a TextAttribute. Keep
the original text and its semantics available. Do not paint a bitmap of text
when the user needs Dynamic Type, selection, VoiceOver, copying, or search.

If a custom TextKit 2 or Core Text surface draws into a layer or canvas, pair
it with a semantic text/editor representation. The semantic representation
should expose the visible text or a useful summary, heading and link structure,
current selection or review state, action names and values, errors/stale state,
and a way to activate, adjust, copy, or edit the same content.

An accessibilityRepresentation can describe a custom visual using a semantic
SwiftUI view, but the representation is not permission to hide real controls
or to make the visual and semantic states diverge.

## Dynamic Type, localization, and writing direction

Test the whole screen, not only the font:

- xSmall through the largest supported accessibility size;
- Bold Text and increased contrast;
- light, dark, high-contrast, and reduced-transparency appearances;
- English plus a long localized language;
- right-to-left layout and bidirectional paragraphs;
- different writing systems and line-breaking behavior;
- keyboard, pointer, VoiceOver, and Switch Control;
- portrait, landscape, iPad window resizing, and external display context.

Do not use a fixed height for a paragraph, toolbar label, or review button.
Prefer flexible stacks, text measurement, adaptive layout, and scroll regions.
If a design truly needs a compact variant, make the choice based on available
space and preserve the full text elsewhere.

## Performance and energy

Measure the actual document shape:

- short and long paragraphs;
- many attributes and links;
- attachments or embedded images;
- rapid typing and undo;
- viewport scrolling and selection dragging;
- live annotation updates;
- model proposals arriving while the person edits;
- low-power and thermal conditions.

Use TextKit 2 viewport layout or a higher-level SwiftUI text surface when it
reduces work. Keep text parsing and model inference cancellable. Do not run a
full-document re-layout or model request for every keystroke without an
explicit debounce, revision check, and cancellation policy.

## Design review checklist

- The text surface uses the highest-level native route that satisfies the need.
- Type hierarchy remains readable at Dynamic Type and localization extremes.
- Selection, cursor, focus, and keyboard behavior are visible and testable.
- Glass groups real actions and never obscures essential text.
- Review annotations are inspectable, reversible, and tied to a source revision.
- Custom drawing has a semantic accessibility representation.
- Writing direction, VoiceOver, reduced effects, and contrast are designed.
- Long-document layout and AI work have bounded, cancellable lifecycles.
- The final design remains useful when model output is unavailable.

## Related routes

- [TextKit 2 and Core Text layout](../42-framework-deep-dives/57-textkit-2-and-core-text-layout.md)
- [TextKit 2 rich-editor and AI annotation route](../50-capability-recipes/80-textkit-2-rich-editor-and-ai-annotation-route.md)
- [TextKit 2 typography proof matrix](../60-verification/74-textkit-2-typography-proof-matrix.md)
- [TextKit 2 and Core Text recipes](../70-code-recipes/92-textkit-2-and-core-text-recipes.md)
- [Rich text and custom TextRenderer routes](../10-swiftui/10-rich-text-and-text-renderers.md)
- [Rich AI text and Apple-native typography](15-rich-ai-text-and-typography.md)

## Sources

- [Typography HIG](https://developer.apple.com/design/human-interface-guidelines/typography)
- [Text views HIG](https://developer.apple.com/design/human-interface-guidelines/text-views)
- [Layout HIG](https://developer.apple.com/design/human-interface-guidelines/layout)
- [Human Interface Guidelines accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility/)
- [SwiftUI text input and output](https://developer.apple.com/documentation/swiftui/text-input-and-output)
- [Text](https://developer.apple.com/documentation/swiftui/text)
- [Text attributed-content initializer](https://developer.apple.com/documentation/swiftui/text/init%28_%3A%29-1a4oh)
- [AttributedString](https://developer.apple.com/documentation/foundation/attributedstring)
- [TextSelection](https://developer.apple.com/documentation/swiftui/textselection)
- [AttributedTextSelection](https://developer.apple.com/documentation/swiftui/attributedtextselection)
- [TextRenderer](https://developer.apple.com/documentation/swiftui/textrenderer)
- [TextAttribute](https://developer.apple.com/documentation/swiftui/textattribute)
- [Text customAttribute](https://developer.apple.com/documentation/swiftui/text/customattribute%28_%3A%29)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [accessibilityRepresentation](https://developer.apple.com/documentation/swiftui/view/accessibilityrepresentation%28representation%3A%29)
- [UIFontMetrics](https://developer.apple.com/documentation/uikit/uifontmetrics)
- [TextKit 2 interaction sample](https://developer.apple.com/documentation/uikit/using-textkit-2-to-interact-with-text)
- [NSTextSelection](https://developer.apple.com/documentation/uikit/nstextselection)
- [NSTextViewportLayoutController](https://developer.apple.com/documentation/uikit/nstextviewportlayoutcontroller)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
