# Rich text, attributed content, and custom TextRenderer routes

## Purpose

SwiftUI gives a useful progression for text-heavy Apple-native features:

    localized or user/model text
    -> validated AttributedString or plain String
    -> Text or TextEditor
    -> optional text selection and attributed selection
    -> optional TextAttribute and TextRenderer treatment
    -> accessibility, Dynamic Type, localization, and review evidence

Use the lowest layer that satisfies the outcome. A normal Text view with a semantic font, link, heading, or selection route is usually a better native foundation than a custom renderer. TextRenderer is an extension point for a bounded visual treatment, not a replacement for content validation, text semantics, or accessibility review.

## Route chooser

| Need | First route | Escalate when |
| --- | --- | --- |
| Read-only localized copy | Text with a localized initializer and semantic font | The content needs links, inline intent, or structured attributes |
| User editing | TextEditor with String or AttributedString | Selection-aware suggestions, formatting, or source-range review are required |
| Markdown from a trusted source | AttributedString Markdown initializer, then Text | Parsing policy, custom attributes, or link validation must be explicit |
| Stable text highlighting | AttributedString attributes or a small Text composition | The effect must follow placed glyph runs or animate with the text |
| Run-aware visual effect | TextAttribute plus TextRenderer | The renderer needs a target-specific, measurable effect |
| Observe layout | Text.LayoutKey preference | A measured overlay or source-range interaction is actually needed |
| Share/export text | Preserve AttributedString or a deliberately flattened representation | The destination requires a file, PDF, image, or Transferable representation |

Do not move to TextRenderer merely because a screenshot looks more impressive. Start with the semantic text hierarchy, then prove that the custom effect survives font scaling, truncation, localization, right-to-left layout, reduced effects, and VoiceOver.

## AttributedString is a value boundary

Foundation AttributedString is a value type whose runs carry attributes over ranges of text. Foundation and SwiftUI expose attribute scopes, and an app can define custom keys and scopes when the product needs a typed representation.

That makes it useful as an intermediate value between an input source and a view:

    source string or localized resource
    -> parse or construct the attributed value
    -> remove, normalize, or reject unsupported attributes
    -> validate links and source metadata
    -> render with Text or edit with TextEditor

Keep this value boundary deterministic. A model may propose text, emphasis, or source spans, but application code should decide which attributes are legal, which links are allowed, and which ranges are safe to display. Never deserialize arbitrary model output into executable view code, arbitrary gestures, or unbounded renderer state.

### Markdown ingestion

AttributedString has Markdown initializers and parsing options. Markdown can express links and inline presentation intent, and SwiftUI Text renders a supported subset of Foundation attributes. In particular, Text uses supported inline presentation intent and writing direction attributes, and treats link attributes as clickable links. It ignores other Foundation-defined attributes that it does not support.

For an AI or imported document route:

1. bound the input length and any attached metadata;
2. parse with an explicit failure policy when the product needs to distinguish partial from complete parsing;
3. inspect and validate link attributes against the product’s allowlist and scheme policy;
4. remove unsupported or unsafe custom attributes before rendering;
5. attach app-owned source, confidence, or review metadata only after parsing;
6. show parse warnings and preserve the original source for correction;
7. make the final user-approved record separate from the proposal.

Do not use try! or silently accept a partial parse in a production review flow. If partial parsing is a deliberate fallback, label the result and expose the original text and the error state.

### Localization and formatting

Use localized text initializers and localization resources for user-facing copy. Use verbatim initialization only when the string is intentionally not a localization key. Keep generated or imported content separate from localized app chrome so a model cannot replace accessibility labels, action names, or safety copy.

Text may combine SwiftUI modifiers with supported AttributedString attributes. Treat that as a semantic hierarchy:

    text style and localization
    -> inline emphasis and link semantics
    -> source/review attributes
    -> optional visual renderer

Do not encode meaning only as a foreground color, underline, glow, or background shape.

## Text is the default renderer

Text is SwiftUI’s read-only text view. It supplies the system body font by default and supports semantic font styles, modifiers, accessibility labels/headings, localization, and supported AttributedString content. This default path participates in SwiftUI’s layout and environment behavior and should remain the fallback when a custom treatment is unavailable.

For a native-looking interface:

- use semantic font styles before fixed point sizes;
- preserve the relationship between title, supporting text, metadata, and actions at every Dynamic Type size;
- use links as links, not as a color-only visual convention;
- use TextEditor for editing and review rather than trying to make Text behave like an editor;
- expose a selectable read-only route when people need to copy or inspect content;
- keep generated content visually distinct from user-approved content through labels and state, not only color;
- give headings an accessibility heading level where the screen hierarchy calls for one.

## TextAttribute and Text.Layout

TextAttribute is a Hashable value that can be attached to a Text view and queried by a text renderer. Text.customAttribute attaches one attribute of a given type to a Text view; nested attributes of the same type take precedence. This is a good fit for bounded app-owned markers such as:

- source span identifiers;
- review state;
- a search match or user-selected emphasis;
- a visual treatment variant;
- a redaction or privacy mask;
- a stable semantic category used by a renderer.

Text.Layout describes the placed tree of Text views and their custom attributes. It is a collection of lines, runs, and run slices. A run exposes character indices, layout direction, typographic bounds, and custom TextAttribute values. Text.Layout also exposes whether the result is truncated.

Use layout values for visual placement, not as a second source of truth. CharacterIndex is opaque and intended for relative locations in the layout; do not assume it is a durable string index for persistence, analytics, or model prompts.

The typographic bounds of a line or run provide an origin, width, ascent, descent, leading, and rectangle. These bounds are useful for drawing a restrained highlight behind a run, positioning a carefully scoped affordance, or measuring a proof fixture. They do not automatically define an accessible element, a hit target, or a source range that can be safely edited.

## TextRenderer contract

TextRenderer is an Animatable protocol that can replace the default drawing behavior of text views. Its core contract is:

    draw(layout: Text.Layout, in: inout GraphicsContext)
    sizeThatFits(proposal: ProposedViewSize, text: TextProxy) -> CGSize
    displayPadding: EdgeInsets

The sizeThatFits and displayPadding requirements have default implementations, but a renderer still needs a clear size and clipping policy. displayPadding exists for extra drawing that would otherwise be clipped, such as a shadow. Treat that padding as part of the measured visual contract; do not use it to conceal an unbounded effect.

Apply a renderer with the textRenderer modifier to a view subtree. The renderer then affects text views inside that subtree. Keep the subtree small and the renderer value stable. A renderer should:

- draw the underlying text in every supported state;
- use custom attributes or explicit state to select effects;
- preserve the system’s font, line breaking, and writing direction unless the product has a tested reason to change them;
- avoid making a semantic state visible only through a decorative effect;
- keep drawing bounded to the measured layout;
- define a reduced-effects or standard Text fallback;
- be cheap enough for the largest fixture that the product supports.

The safest pattern is “draw the system text, add one restrained treatment, then verify the same content without that treatment.” A glow, shader, or animated color is not a substitute for contrast, VoiceOver, selection, or an explicit review state.

### Example renderer responsibility

    Text("Suggested summary")
        .customAttribute(ReviewHighlightAttribute())
        .textRenderer(ReviewHighlightRenderer())

The example says only that the text has a renderer-aware visual marker. It does not grant the text an action, approve the summary, or make the highlight an accessible state. Those responsibilities belong to the surrounding semantic view and domain state.

## Observing text layout

Text.LayoutKey is a PreferenceKey that provides Text.Layout values for Text views in a queried subtree. Its anchored layout values can be used when a feature truly needs to align an overlay with rendered text.

Use this route sparingly:

- observe layout only for a real interaction or visual relationship;
- keep source identity in app state rather than deriving it from pixel coordinates;
- invalidate overlays when content, font, width, layout direction, or Dynamic Type changes;
- treat a truncated layout as a product state, not a silent measurement success;
- avoid writing measured geometry back into domain state or using it to authorize actions;
- remove the overlay in reduced-effects or accessibility configurations when it is not essential.

Text.LayoutKey is not a license to rebuild a text engine in SwiftUI. If a feature becomes a document editor, annotation canvas, or complex selection system, evaluate TextEditor, UIKit text system interop, or a purpose-built document model instead.

## Selection and review

SwiftUI exposes TextSelection for selectable text and AttributedTextSelection for attributed text in a TextEditor. AttributedTextSelection represents an insertion point or a visually contiguous selection, and it can report selected indices, attributes, typing attributes, and selection affinity.

This makes a strong on-device AI review route possible:

    draft AttributedString
    -> TextEditor with bound AttributedTextSelection
    -> suggestion action scoped to the current selection
    -> deterministic or model-generated proposal
    -> user review
    -> explicit apply or discard

Selection is user intent, not authorization to mutate a record. Keep the selected range, source revision, model request, and final apply action separate. For bidirectional text, test TextSelectionAffinity and the actual visual insertion/selection behavior with mixed left-to-right and right-to-left fixtures.

## AI output as reviewable content

Treat model output as a proposal with a source revision and a bounded presentation policy:

    model request
    -> raw proposal
    -> schema/length/character validation
    -> Markdown or attributed parse
    -> link and custom-attribute policy
    -> visible draft
    -> user review and selection
    -> approved domain record

The visible output should disclose when it is generated, incomplete, stale, or awaiting review. A renderer can mark source-backed spans or pending suggestions, but it should not make unsupported confidence look like fact. Keep provenance accessible in labels or an inspectable detail surface, not only in highlights.

For model-unavailable, parse-failed, content-filtered, or canceled states, the deterministic fallback is usually plain text or the last approved record. Do not leave a spinner, empty glass pill, or stale “AI” badge that implies success.

## Liquid Glass and typography

Liquid Glass is a grouping and hierarchy treatment around functional content. Text inside a glass group should remain readable and meaningful when the material is removed, reduced, or replaced. Prefer:

- semantic Text and Label content;
- a small hierarchy of title, value, supporting text, and action;
- contrast tested over the actual background and color scheme;
- content insets and measured width so text does not collide with glass edges;
- a visible review/status label for AI-generated content;
- standard material or opaque fallback when transparency is reduced.

Avoid putting a custom text renderer on every label in a screen. A single renderer-aware review region can be useful; a fully shaderized text hierarchy often harms legibility, accessibility, localization, and performance.

## Accessibility and adaptation checklist

- Use Dynamic Type and scalable metrics; test the largest accessibility sizes.
- Test truncation, line limits, and multiline layout with long localized and generated strings.
- Test VoiceOver labels, headings, links, selection, and the difference between draft and approved content.
- Test right-to-left layout and mixed-direction text.
- Ensure source spans or highlights do not become the only way to discover meaning.
- Test reduced motion, reduced transparency, increased contrast, Bold Text, and color schemes.
- Keep editing and selection actions reachable by keyboard, Voice Control, and Switch Control where supported.
- Use adequate hit regions around any annotation or review affordance.
- Preserve the source and a recovery path when parsing, model generation, or rendering fails.

## Performance and target discipline

Record the minimum deployment target, target membership, platform, and availability branch for TextRenderer, attributed selection, Writing Tools, and any custom text formatting route. Compile the smallest target slice before adding a renderer.

Profile long text and frequent updates. Avoid rebuilding large AttributedString values on every frame, performing network/model work from a renderer, or using a layout preference as an unbounded state feedback loop. Measure a deterministic fixture with short, long, multilingual, mixed-direction, truncated, and attribute-heavy content.

## Sources

- [Text](https://developer.apple.com/documentation/swiftui/text)
- [Text initializer and AttributedString support](https://developer.apple.com/documentation/swiftui/text/init%28_%3A%29)
- [TextEditor](https://developer.apple.com/documentation/swiftui/texteditor)
- [Text input and output](https://developer.apple.com/documentation/swiftui/text-input-and-output)
- [TextAttribute](https://developer.apple.com/documentation/swiftui/textattribute)
- [Text.customAttribute(_:)](https://developer.apple.com/documentation/swiftui/text/customattribute%28_%3A%29)
- [TextRenderer](https://developer.apple.com/documentation/swiftui/textrenderer)
- [TextProxy](https://developer.apple.com/documentation/swiftui/textproxy)
- [Text.Layout](https://developer.apple.com/documentation/swiftui/text/layout)
- [Text.Layout.Run](https://developer.apple.com/documentation/swiftui/text/layout/run)
- [Text.Layout.TypographicBounds](https://developer.apple.com/documentation/swiftui/text/layout/typographicbounds)
- [Text.LayoutKey](https://developer.apple.com/documentation/swiftui/text/layoutkey)
- [GraphicsContext](https://developer.apple.com/documentation/swiftui/graphicscontext)
- [TextSelection](https://developer.apple.com/documentation/swiftui/textselection)
- [AttributedTextSelection](https://developer.apple.com/documentation/swiftui/attributedtextselection)
- [TextSelectionAffinity](https://developer.apple.com/documentation/swiftui/textselectionaffinity)
- [AttributedString](https://developer.apple.com/documentation/foundation/attributedstring)
- [Instantiating attributed strings with Markdown syntax](https://developer.apple.com/documentation/foundation/instantiating-attributed-strings-with-markdown-syntax)
- [MarkdownParsingOptions](https://developer.apple.com/documentation/foundation/attributedstring/markdownparsingoptions)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Human Interface Guidelines: Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
- [Human Interface Guidelines: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Human Interface Guidelines: Right to left](https://developer.apple.com/design/human-interface-guidelines/right-to-left)
