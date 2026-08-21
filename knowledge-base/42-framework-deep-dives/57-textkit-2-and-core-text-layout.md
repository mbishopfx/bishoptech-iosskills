# TextKit 2 and Core Text layout

Text is both content and geometry. On iOS, the most useful route is to let the
system own ordinary text display and editing, then move down a layer only when
the product needs custom layout, custom rendering, document-scale viewport
control, or glyph-level measurement.

Use this decision model:

~~~text
read-only SwiftUI text
  -> Text + system Font/Text styles

long-form SwiftUI input
  -> TextEditor, TextSelection, AttributedString

rich UIKit editing or document layout
  -> UITextView(usingTextLayoutManager: true)
  -> TextKit 2 object graph

custom text surface or editor integration
  -> NSTextContentStorage
  -> NSTextLayoutManager
  -> NSTextContainer
  -> NSTextLayoutFragment / NSTextLineFragment
  -> viewport renderer and semantic controls

low-level drawing, glyph metrics, or shaped export
  -> NSAttributedString
  -> CTFramesetter / CTFrame / CTLine / CTRun / CTFont
  -> CGContext drawing
~~~

The lower-level route is not automatically more native. It is a more explicit
responsibility boundary. A custom renderer must take ownership of sizing,
selection or hit testing, accessibility, invalidation, writing direction,
Dynamic Type policy, and performance evidence that a system text view would
otherwise supply.

## TextKit 2 object graph

| Object | Responsibility | Typical owner |
| --- | --- | --- |
| NSTextContentManager | Abstract document content and the relationship to layout managers | A document/editor layer |
| NSTextContentStorage | Attributed-string backing store and text-element generation for common paragraphs and lists | A rich text view or document model adapter |
| NSTextLayoutManager | Layout geometry, layout fragments, selection data source, rendering attributes, and layout invalidation | The view or custom display surface |
| NSTextContainer | Geometric region in which text lays out | The destination view/layout |
| NSTextLayoutFragment | A render-sized portion of a text element, often mapped to a view or layer | A viewport renderer |
| NSTextLineFragment | A single textual layout and rendering unit with character range, glyph origin, metrics, hit testing, and drawing | A custom line renderer |
| NSTextViewportLayoutController | Lays out the visible viewport plus an over-scroll region and notifies a delegate | A scrolling text surface |
| NSTextLocation / NSTextRange | Abstract document positions and ranges that survive beyond raw view coordinates | Selection, editing, and review state |
| NSTextSelection | Logical or visual selection context, including insertion-point affinity and typing attributes | Editor interaction |
| UITextView | System scrolling, editing, keyboard, selection, and text-input behavior | UIKit surface |

NSTextContentStorage uses an attributed string as its backing store and maps
portions of that content into text elements such as paragraphs and lists.
When editing that content, use the content manager editing transaction so the
attached layout managers can synchronize the change. A direct mutation that
bypasses the transaction can leave a custom display or secondary layout manager
out of step.

NSTextLayoutManager is the centerpiece of the layout side. It can expose a
text container, selections, usage bounds, text segments, rendering attributes,
layout fragments, and the viewport controller. Its ensureLayout and enumeration
methods let a custom surface ask only for the geometry it needs. That is useful
for a long document, a paginated reader, a review overlay, or a custom canvas
that should not eagerly construct every visual surface.

The layout manager also carries policy switches such as font leading,
hyphenation, a layout queue, and defensive handling for suspicious contents.
These are layout concerns, not a license to run arbitrary document processing
on a display callback. Keep parsing, model inference, and persistence outside
the render loop.

## Viewport layout and fragments

A viewport is a rectangle in the text system's flipped coordinate space. The
viewport controller manages the visible bounds with an additional overdraw
region. Its delegate can provide the viewport bounds, receive will-layout and
did-layout callbacks, and configure a rendering surface for a layout fragment.

Use the viewport boundary when:

- a document is large enough that eager layout is measurable;
- attachments need reuse as a person scrolls;
- a custom reader maps each paragraph or fragment to a view or layer;
- an AI review overlay should decorate only visible source spans;
- a UIKit text view subclass needs to coordinate rendering surfaces.

NSTextLayoutFragment is the unit to tile or draw. It exposes line fragments,
the element-relative range, layout and rendering bounds, attachments, state,
and a draw operation. NSTextLineFragment exposes its source attributed string,
character range, glyph origin, typographic bounds, character hit testing, caret
locations, and drawing. Use those APIs for geometry-driven features instead of
estimating line heights from string length.

The viewport is not the document model. Persist an abstract document range or
a stable source identifier, not a view index or a line-fragment frame. Frames
change when the font, width, locale, content, text direction, or Dynamic Type
size changes.

## Selection, locations, and editing

TextKit 2 identifies locations abstractly through NSTextLocation. An
NSTextRange represents a contiguous range, while NSTextSelection can hold
logical ranges, affinity, granularity, typing attributes, and transient
interaction state. This makes selection a better integration boundary for
review tools than a raw NSRange stored forever.

Use raw UTF-16 or NSRange only at a clearly defined boundary, such as an API
that requires it or a short-lived bridge to an attributed string. Convert back
to a document identity or a stable source span before persisting an AI
proposal. A proposal that stores only character offsets can become wrong after
an insertion before that range.

For a rich editor, keep these states separate:

| State | Meaning |
| --- | --- |
| Draft text | The current user-owned content |
| Selection | The current editing context |
| Layout | Geometry derived from draft, container, traits, and locale |
| Proposal | A generated change tied to source revision and spans |
| Review | User decision to accept, reject, or edit a proposal |
| Commit | A domain mutation after validation |

The selection is not proof that a proposal is accepted. A layout fragment is
not proof that a string was persisted. A text-view delegate callback is not
proof that a system writing tool or model completed its work.

## TextKit 1 and migration boundaries

TextKit 1 uses NSTextStorage, NSLayoutManager, NSTextContainer, and UITextView.
It remains a useful compatibility route for existing code and for APIs whose
delegate or glyph customization surface is already built around
NSLayoutManager. The documented custom-shaped-layout sample uses that route for
circular and multi-column containers.

Choose TextKit 1 when:

- the deployment target or existing editor architecture requires it;
- the feature depends on a TextKit 1 delegate or glyph-substitution path;
- the change can be isolated behind a UIKit adapter.

Choose TextKit 2 when:

- you are starting a new document/editor surface;
- viewport-driven layout, text elements, selection navigation, or custom layout
  fragments are central;
- the target uses UITextView's usingTextLayoutManager initializer;
- the feature needs a modern path for long documents and custom rendering.

Do not attach one text storage to a legacy layout manager and a TextKit 2
layout manager casually. Decide which object graph is authoritative for the
surface, or build an explicit synchronization adapter with tests for edits,
selection, undo, attributes, and layout invalidation.

UITextView can be constructed with or without a text layout manager. It still
owns practical editor concerns such as scroll behavior, first responder state,
selection, input traits, find interaction, Writing Tools configuration, and
text formatting. A custom TextKit 2 surface should reuse that system behavior
where it helps instead of rebuilding keyboard and selection semantics from
scratch.

## Core Text: the lower-level drawing route

Core Text is a low-level interface for text layout, font handling, font
metrics, and glyph data. A typical multiline path is:

~~~text
NSAttributedString / CFAttributedString
  -> CTFramesetter
  -> CTFrame
  -> CTLine
  -> CTRun
  -> CTFont and glyph metrics
  -> CGContext drawing
~~~

CTFramesetter creates frames from an attributed string and a shape path.
CTFrame contains the lines that fit and can draw the whole frame or expose line
origins. CTLine provides typographic bounds, glyph runs, string ranges, caret
offsets, string-index hit testing, and line drawing. CTFont supplies font
characteristics and metrics.

Use Core Text when the product really needs:

- deterministic drawing into a CGContext;
- text fitted into arbitrary paths or export surfaces;
- low-level glyph metrics or caret/hit-testing calculations;
- a renderer shared with a PDF, image, or custom layer pipeline;
- inspection of font tables or font descriptors.

Core Text layout objects such as the typesetter, framesetter, frame, line, and
run should be used within one operation, work queue, or thread. Individual
Core Text functions and font objects have different thread-safety guarantees.
Keep a framesetter/frame/line operation isolated; do not share mutable layout
objects across an uncontrolled collection of concurrent tasks.

Core Text does not provide a full editor. The app must implement selection
semantics, insertion, keyboard integration, accessibility, link activation,
undo, Dynamic Type policy, and text-direction behavior if those are required.

## SwiftUI boundary

Use the highest-level SwiftUI route that satisfies the feature:

| Need | Route |
| --- | --- |
| Static or dynamic read-only text | Text with system styles and semantic modifiers |
| Styled read-only text | AttributedString rendered by Text |
| Long-form editable text | TextEditor with TextSelection or AttributedTextSelection where supported |
| Custom run-level visual effect | TextAttribute, Text.Layout, and TextRenderer |
| UIKit editor behavior | UITextView in UIViewRepresentable |
| Document-scale custom geometry | TextKit 2 or Core Text behind a focused adapter |

SwiftUI Text can render an AttributedString, but it respects only a documented
subset of Foundation attributes and gives SwiftUI attributes precedence over
equivalent framework attributes. Do not assume that an arbitrary UIKit or Core
Text attribute will appear in a SwiftUI Text.

TextRenderer is a rendering extension point, not a replacement for TextKit's
editing and viewport machinery. A renderer can size and draw a SwiftUI text
layout and inspect custom TextAttribute values; it should not be used to
conceal important content, replace semantic controls, or turn an AI-generated
span into an unreviewable decoration.

## AI and on-device text boundaries

TextKit and Core Text do not generate meaning. They lay out and draw strings.
An on-device model, Vision observation, Natural Language tagger, Writing Tools
operation, or Foundation Models session can propose text, labels, or edits, but
the app still owns:

- the source revision and user authorization;
- the proposal schema and source spans;
- stale-result detection after edits;
- privacy and retention of source text;
- user-visible review and accept/reject actions;
- deterministic validation before commit;
- fallback when a model or system feature is unavailable.

For a reviewable proposal, render source-span highlights as an optional layer
over the existing text and put actions in a semantic toolbar or sheet. Do not
rewrite the text in place before the user has a chance to understand what
changed.

## Accessibility, typography, and performance

System text styles and SwiftUI Font routes give the platform room to adapt
Dynamic Type and accessibility sizes. A custom font should be scaled with the
platform's font metrics policy. Custom drawing must preserve readable contrast,
support the current writing direction, and expose meaningful text and actions
to VoiceOver.

When a custom surface draws text into a canvas or layer, pair it with one of:

- a real semantic text/control hierarchy;
- a UIKit text view whose accessibility behavior remains active;
- a SwiftUI accessibilityRepresentation that describes the same state and
  actions;
- an accessible custom element with stable labels, values, and actions.

For performance, profile the real document shape. Test long paragraphs,
attachments, Dynamic Type, localization, bidirectional text, selection
dragging, and rapid edits. Viewport layout can reduce work, but it does not
make an unbounded model request, full-document attribute pass, or synchronous
file operation safe on the main actor.

## Availability and proof boundary

The exact symbols and availability depend on the SDK and deployment target.
Use the iOS 26 SDK in the target, compile a minimal route, inspect warnings,
and add availability branches where Xcode requires them. Documentation
coverage is not compilation proof. A preview does not prove keyboard,
selection, VoiceOver, long-document performance, or physical-device text
rendering.

## Related routes

- [Native typography and rich-editor design](../21-design-deep-dives/77-native-typography-and-rich-editor-design.md)
- [TextKit 2 rich-editor and AI annotation route](../50-capability-recipes/80-textkit-2-rich-editor-and-ai-annotation-route.md)
- [TextKit 2 typography proof matrix](../60-verification/74-textkit-2-typography-proof-matrix.md)
- [TextKit 2 and Core Text recipes](../70-code-recipes/92-textkit-2-and-core-text-recipes.md)
- [Rich text and custom TextRenderer routes](../10-swiftui/10-rich-text-and-text-renderers.md)
- [Rich AI text and Apple-native typography](../21-design-deep-dives/15-rich-ai-text-and-typography.md)

## Sources

- [TextKit 2 interaction sample](https://developer.apple.com/documentation/uikit/using-textkit-2-to-interact-with-text)
- [Display text with a custom layout](https://developer.apple.com/documentation/uikit/display-text-with-a-custom-layout)
- [NSTextContentManager](https://developer.apple.com/documentation/uikit/nstextcontentmanager)
- [NSTextContentStorage](https://developer.apple.com/documentation/uikit/nstextcontentstorage)
- [NSTextLayoutManager](https://developer.apple.com/documentation/uikit/nstextlayoutmanager)
- [NSTextLayoutManager text container](https://developer.apple.com/documentation/uikit/nstextlayoutmanager/textcontainer)
- [NSTextLayoutFragment](https://developer.apple.com/documentation/uikit/nstextlayoutfragment)
- [NSTextLineFragment](https://developer.apple.com/documentation/uikit/nstextlinefragment)
- [NSTextViewportLayoutController](https://developer.apple.com/documentation/uikit/nstextviewportlayoutcontroller)
- [NSTextViewportLayoutControllerDelegate](https://developer.apple.com/documentation/uikit/nstextviewportlayoutcontrollerdelegate)
- [NSTextLocation](https://developer.apple.com/documentation/uikit/nstextlocation)
- [NSTextRange](https://developer.apple.com/documentation/uikit/nstextrange)
- [NSTextSelection](https://developer.apple.com/documentation/uikit/nstextselection)
- [UITextView](https://developer.apple.com/documentation/uikit/uitextview)
- [NSLayoutManager](https://developer.apple.com/documentation/uikit/nslayoutmanager)
- [NSTextStorage](https://developer.apple.com/documentation/uikit/nstextstorage)
- [Core Text](https://developer.apple.com/documentation/coretext)
- [CTFramesetter](https://developer.apple.com/documentation/coretext/ctframesetter)
- [CTFrame](https://developer.apple.com/documentation/coretext/ctframe)
- [CTLine](https://developer.apple.com/documentation/coretext/ctline)
- [CTTypesetter](https://developer.apple.com/documentation/coretext/cttypesetter)
- [CTFont](https://developer.apple.com/documentation/coretext/ctfont)
- [AttributedString](https://developer.apple.com/documentation/foundation/attributedstring)
- [SwiftUI text input and output](https://developer.apple.com/documentation/swiftui/text-input-and-output)
- [TextRenderer](https://developer.apple.com/documentation/swiftui/textrenderer)
- [Text.Layout](https://developer.apple.com/documentation/swiftui/text/layout)
- [TextAttribute](https://developer.apple.com/documentation/swiftui/textattribute)
- [Typography HIG](https://developer.apple.com/design/human-interface-guidelines/typography)
- [Supporting VoiceOver](https://developer.apple.com/documentation/uikit/supporting-voiceover-in-your-app)
- [UIFontMetrics](https://developer.apple.com/documentation/uikit/uifontmetrics)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
