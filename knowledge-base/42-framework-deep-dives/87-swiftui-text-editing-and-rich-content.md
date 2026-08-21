# SwiftUI text editing and rich-content deep dive

## Purpose

SwiftUI's text system now spans plain long-form editing, attributed editing,
selection, system formatting controls, find and replace, Writing Tools, Markdown
ingestion, and custom rendering. Treat these as separate responsibilities:

~~~text
durable content model
    -> String or AttributedString representation
    -> TextEditor input and selection
    -> formatting definition and system controls
    -> find/replace, commands, and focus
    -> optional UIKit/TextKit 2 escape hatch
    -> optional Writing Tools or on-device AI proposal
    -> explicit validation, review, and document commit
~~~

A TextEditor is not a document format. A selection is not a commit. An
AttributedString attribute is not automatically a supported rendered style.
Writing Tools and an on-device model are not interchangeable, and neither
should silently bypass the document's save or conflict boundary.

This page complements the existing low-level TextKit 2, rich-rendering, and
native typography pages by concentrating on the SwiftUI editor orchestration
layer.

## The route selector

| User need | First SwiftUI route | Escalate only when |
| --- | --- | --- |
| Plain multiline draft | TextEditor with Binding<String> | The document needs inline formatting or source-span attributes |
| Formatted document editing | TextEditor with Binding<AttributedString> and attributed selection | The required formatting or selection behavior is outside the supported SwiftUI surface |
| Read-only styled content | Text with AttributedString | The product needs placed-run effects, custom geometry, or a measured overlay |
| Selection-aware suggestion | TextSelection or AttributedTextSelection | The proposal needs text-system ranges, large-document viewport logic, or UIKit integration |
| Constrained formatting | AttributedTextFormattingDefinition | A custom UIKit/TextKit 2 editor owns the formatting system |
| Find and replace | findNavigator and native text-editor support | A custom text surface must implement its own find context |
| System Writing Tools | writingToolsBehavior and writingToolsAffordanceVisibility | A custom UIKit view needs UIWritingToolsCoordinator |
| Rich document layout | SwiftUI editor plus a focused adapter | UITextView/TextKit 2 or Core Text is truly required |
| Custom visual treatment | TextAttribute and TextRenderer | The effect requires document layout, hit testing, or editable attachments |
| Markdown import | AttributedString Markdown initializer with explicit options | The app needs a full Markdown AST, unsupported extensions, or round-trip source fidelity |

Start from the highest-level route that can complete the task. Each escalation
adds ownership for availability, selection, accessibility, performance, and
proof.

## 1. Choose the content representation

### Plain String

Use String when the document's durable meaning is plain text and formatting is
global.

Benefits:

- simple Codable and migration behavior;
- straightforward diffing and revision checks;
- native TextEditor editing and input behavior;
- easy search, selection, and AI source extraction;
- clear fallback when attributed formatting is unavailable.

The editor's font, color, line spacing, and alignment remain presentation
policy. Do not serialize those global view modifiers as if they were text
content.

### AttributedString

Use AttributedString when ranges carry meaningful content or formatting:

- emphasis, strong text, underline, or strikethrough;
- links and writing direction;
- supported SwiftUI formatting attributes;
- semantic app-owned attributes such as a contact ID or review span;
- Markdown-derived source positions or presentation intents;
- text that must transfer as an attributed representation.

Keep a clear policy for unsupported attributes. SwiftUI Text renders only a
documented subset of Foundation attributes, and SwiftUI attributes can take
precedence over equivalent attributes from UIKit or AppKit. A value that can
round-trip through Foundation or TextKit is not automatically a value that a
SwiftUI Text or TextEditor displays identically.

### Source Markdown or another authoring format

Markdown, JSON, or a custom document format can be the source representation.
An AttributedString can be a parsed/editor projection. Decide whether editing
the projection writes back to the source format or whether the application
promotes the projection to the new canonical format.

Record:

- source bytes and format version;
- parsed AttributedString or plain text;
- links and source positions;
- unsupported syntax or attributes;
- parse diagnostics;
- round-trip policy;
- revision and dirty state.

Do not promise lossless Markdown round-tripping when the editor only stores an
attributed projection.

## 2. Use TextEditor at the correct level

Plain editing uses the Binding<String> initializer:

~~~swift
struct PlainDraftEditor: View {
    @Binding var text: String

    var body: some View {
        TextEditor(text: $text)
            .font(.body)
            .textInputAutocapitalization(.sentences)
            .autocorrectionDisabled(false)
    }
}
~~~

This is a good native route for notes, journal entries, descriptions, messages,
and other text whose formatting is global. The editor is multiline and
scrollable. The surrounding view owns document identity, save state, focus
policy, and domain validation.

For formatted editing, use the attributed initializer with a selection binding
when the target SDK provides it:

~~~swift
struct FormattedDraftEditor: View {
    @Binding var text: AttributedString
    @Binding var selection: AttributedTextSelection?

    var body: some View {
        TextEditor(text: $text, selection: $selection)
    }
}
~~~

Verify the exact generic selection binding signature and deployment
availability in the selected iOS 26 SDK. Keep a plain-text fallback if the
product supports an older deployment target or a target whose SwiftUI surface
does not expose the required overload.

By default, iOS can show system text-formatting controls for attributed
TextEditor content. Configure them intentionally with
textInputFormattingControlVisibility rather than duplicating system controls
without a reason.

## 3. Treat selection as an interaction value

TextSelection represents an insertion point, a range, or platform-supported
multiple selections. AttributedTextSelection represents a selection of
AttributedString content. Both are view/editor state, not durable document
truth.

Track:

~~~swift
struct EditorSelectionState: Equatable, Sendable {
    let documentID: UUID
    let sourceRevision: Int
    let selectedText: String
    let isInsertionPoint: Bool
    let affinity: String
}
~~~

For a String selection:

1. capture the selection only while the editor owns the current text;
2. resolve indices against the current value;
3. reject or rebase when text changes;
4. avoid persisting a raw index as a long-lived domain identifier;
5. keep bidirectional text and affinity in the proof fixture.

For an attributed selection, preserve the semantic attributes only when the
editor and proposal route intentionally support them. A selected range that
happens to include a review marker is not authorization to apply it.

Selection-dependent actions should become unavailable when:

- the selection is empty and the action requires a range;
- the document revision changed;
- the selection points outside the current value;
- the source is read-only or conflict-locked;
- the model or system feature is unavailable;
- the selection includes protected content such as code or quoted text.

## 4. Constrain formatting with a definition

AttributedTextFormattingDefinition lets the app define an attribute scope and
value constraints for SwiftUI Text and TextEditor views initialized with
AttributedString. SwiftUI can use the definition to validate which system
formatting controls are visible and enabled.

Use a definition for product policy, not just appearance:

~~~swift
struct SafeNoteFormatting: AttributedTextFormattingDefinition {
    var body: some AttributedTextFormattingDefinition<
        AttributeScopes.SwiftUIAttributes
    > {
        ValueConstraint(
            for: \.underlineStyle,
            values: [nil, .single],
            default: .single
        )
    }
}
~~~

Apply it around the attributed editor:

~~~swift
TextEditor(text: $text, selection: $selection)
    .attributedTextFormattingDefinition(SafeNoteFormatting())
~~~

The definition affects the user-observable editor surface, but the bound
AttributedString can still contain values outside the definition, especially
in portions the editor has not rendered. Before serialization, export, sharing,
or commit, call the definition's constraint path or a domain validator over
the full value.

Keep three policies separate:

| Policy | Owner |
| --- | --- |
| Which attributes are legal in the document | Document/domain layer |
| Which formatting controls are shown | SwiftUI formatting definition and visibility modifiers |
| How an attribute looks in a given surface | SwiftUI/TextRenderer/editor presentation |

A formatting definition is not a sanitizer for arbitrary input. Validate
imported or AI-generated attributes before putting them into the document.

## 5. Configure system formatting controls

System text formatting controls are useful when they match the document's
meaning. They may appear in context menus or keyboard toolbars on iOS. If the
app provides a focused formatting toolbar, hide or limit duplicate system
controls with the documented visibility modifier and leave a clear alternative.

Decide:

- whether bold/italic/underline are part of the file format;
- whether links are authoring content or only a read-only projection;
- whether paragraph/list formatting is supported;
- whether the selection can span incompatible runs;
- how the editor represents mixed values;
- what happens when a formatting action is unavailable;
- which controls remain in accessibility and keyboard paths;
- how formatting survives Markdown import/export and migration.

Never infer that a visible system control means the document writer can preserve
the attribute. The writer and migration tests own that claim.

## 6. Give find and replace one focused owner

SwiftUI provides a findNavigator route for text editor views. Use a single
focused editor or make focus ownership explicit:

~~~swift
struct FindableEditor: View {
    @Binding var text: String
    @State private var isFinding = false

    var body: some View {
        TextEditor(text: $text)
            .findNavigator(isPresented: $isFinding)
            .toolbar {
                Button {
                    isFinding = true
                } label: {
                    Label("Find", systemImage: "magnifyingglass")
                }
            }
    }
}
~~~

The system find/replace surface can use native controls and keyboard shortcuts.
If several editors exist in one hierarchy, do not assume an unfocused call will
target the intended editor; the documented behavior can be nondeterministic.
Make one editor the active task or provide a custom route driven by FindContext.

Use findDisabled or replaceDisabled when the document policy forbids the
operation. A replace action is a document mutation: increment the source
revision, mark the document dirty, run format validation, and pass through the
normal save/conflict path.

## 7. Treat Writing Tools as system-owned editing

Writing Tools can proofread, rewrite, summarize, or compose text with system
large language models and Apple Intelligence. SwiftUI exposes
WritingToolsBehavior values:

| Behavior | Product meaning |
| --- | --- |
| automatic | Let the system choose an appropriate experience |
| limited | Prefer the limited overlay-panel experience when possible |
| complete | Prefer the complete inline-editing experience when possible |
| disabled | Do not offer Writing Tools for this surface |

Apply the behavior and affordance deliberately:

~~~swift
TextEditor(text: $text)
    .writingToolsBehavior(.limited)
    .writingToolsAffordanceVisibility(.visible)
~~~

This is a system editing route, not the same as a Foundation Models session in
the app. If the editor contains code, immutable quotations, identifiers, or
protected metadata, decide whether to disable Writing Tools or use a UIKit
boundary that can provide ignored ranges and richer lifecycle callbacks.

While Writing Tools operates, the system may make temporary changes and later
incorporate final changes. Do not concurrently apply cloud sync, autosave
rewrites, or app-specific transforms that can race those changes. Use a
Writing-Tools-active state to pause conflicting mutation paths, then let the
final text enter the ordinary revision/save pipeline.

On Mac Catalyst, verify the affordance visibility behavior and target-specific
availability. On unsupported or unavailable devices, the editor remains
functional without the system feature.

## 8. Escalate to UIKit/TextKit 2 deliberately

Use a SwiftUI TextEditor until the requirement is truly outside its surface.
Escalate to a UITextView/TextKit 2 bridge when the app needs:

- custom text elements or viewport layout;
- attachment views and document-scale layout;
- precise text-system selection or hit testing;
- custom Writing Tools coordination for a custom view;
- a legacy UIKit editor contract that cannot be replaced safely;
- a formatting or input capability not exposed by the selected SwiftUI API.

The bridge owns lifecycle:

~~~text
SwiftUI source of truth
    -> UIViewRepresentable update
    -> UITextView/TextKit 2 editor
    -> Coordinator delegate callbacks
    -> normalized document mutation
    -> SwiftUI state and revision
~~~

Do not assign the bound value on every update without comparing revisions. Do
not let a UIKit delegate callback mutate a stale SwiftUI binding after the view
has been replaced. Test coordinator teardown, first responder, selection
round-trip, undo, Writing Tools activity, Dynamic Type, and accessibility.

For a custom UIKit view, Writing Tools uses UIWritingToolsCoordinator and its
delegate/context route. That is a separate implementation from SwiftUI's
writingToolsBehavior modifier and should be documented as a target-specific
escape hatch.

## 9. Parse Markdown as untrusted content

AttributedString can parse Markdown with explicit
MarkdownParsingOptions, an optional attribute scope, and an optional baseURL.
Use the options to make syntax, extended attributes, failure policy, language,
and source-position behavior explicit.

~~~swift
struct ParsedMarkdown: Sendable {
    let value: AttributedString
    let source: String
}

func parseMarkdown(_ source: String) throws -> ParsedMarkdown {
    let options = AttributedString.MarkdownParsingOptions(
        allowsExtendedAttributes: false,
        interpretedSyntax: .full,
        failurePolicy: .returnPartiallyParsedIfPossible,
        languageCode: nil,
        appliesSourcePositionAttributes: true
    )

    let value = try AttributedString(
        markdown: source,
        options: options,
        baseURL: nil
    )
    return ParsedMarkdown(value: value, source: source)
}
~~~

The exact enum cases and initializer availability should be checked in the
selected SDK. Keep the raw source and parse diagnostics when recovery matters.
Validate links and custom attributes before presenting actions. A link attribute
is content data, not permission to open any URL; apply the app's URL policy at
the interaction boundary.

If the app needs lossless Markdown editing, keep an AST/source model or define
a deliberate serialization policy. Do not silently discard headings, tables,
custom attributes, or source positions during a user edit.

## 10. Separate rendering from authoring

Text with an AttributedString is a read/rendering route. TextEditor with an
AttributedString is an editing route. TextRenderer is a visual rendering
extension point. TextKit 2 is a layout/editor infrastructure route.

Use this separation:

~~~text
authoring model
    -> normalized AttributedString
        -> TextEditor for editing
        -> Text for read-only projection
        -> TextRenderer for bounded decoration
        -> export/Transferable/document writer
~~~

A TextRenderer should not own:

- document persistence;
- selection truth;
- link security;
- model invocation;
- formatting policy;
- accessibility labels for hidden controls;
- revision or conflict decisions.

When a custom rendered effect is important, expose the same meaning through
semantic text, labels, attributes, or an accessibility representation.

## 11. Add a reviewable on-device AI writing route

Foundation Models and Writing Tools have different ownership semantics:

| Route | Owner | Best fit |
| --- | --- | --- |
| Writing Tools | System text interaction | Proofread/rewrite/summarize/compose inside a supported editor |
| Foundation Models | App feature adapter | A bounded, reviewable domain proposal with app-owned schema and commit |
| TextRenderer | App rendering | Source-span highlighting or provisional visual treatment |
| TextKit 2 | App/editor infrastructure | Layout, selection, attachments, and custom viewport control |

For app-owned AI review, carry:

~~~swift
struct WritingReviewRequest: Sendable {
    let documentID: UUID
    let sourceRevision: Int
    let selection: String
    let instruction: String
    let allowedOperations: Set<String>
}
~~~

The adapter should:

1. check model capability and availability;
2. scope source text to the selection or explicit document region;
3. record the source revision and document identity;
4. cancel when the selection, document, or scene changes;
5. validate length, characters, attributes, links, and schema;
6. show a candidate rather than silently replacing content;
7. reject or rebase a stale candidate;
8. commit through the same attributed-document mutation and save path;
9. expose unavailable, partial, failed, stale, and committed states;
10. keep the editor fully useful without the model.

A generated AttributedString must be treated as untrusted content. Apply the
formatting definition and document validator across the complete value before
writing it.

## 12. Integrate with a document scene

For a T166 DocumentGroup editor, keep the layers explicit:

~~~text
DocumentGroup configuration
    -> document adapter and file format
        -> revisioned String/AttributedString content
            -> SwiftUI TextEditor + selection/focus
                -> formatting/find/Writing Tools actions
                    -> optional app AI candidate
                        -> user review
                            -> document mutation and save/conflict
~~~

The file URL and scene identity are context. The document binding and revision
are content state. The selection is editor state. The AI proposal is a
temporary candidate. Never serialize a selection or candidate as if it were the
canonical file without an explicit policy.

## 13. Input and accessibility boundaries

Text editing must remain usable through the platform's supported input paths:

- software keyboard, hardware keyboard, dictation, and Pencil where supported;
- VoiceOver focus, selection announcements, and formatting actions;
- Voice Control and Switch Control;
- pointer, trackpad, and Mac Catalyst menu/command routes;
- Dynamic Type, Bold Text, contrast, reduced transparency, and reduced motion;
- right-to-left and mixed-direction text;
- find/replace and error recovery.

Use semantic controls and labels around the editor. Do not make a glass toolbar
the only way to discover formatting or review actions. Do not hide the current
selection behind a floating status surface. Test focus after import, selection,
find/replace, Writing Tools completion, AI candidate review, conflict recovery,
and document relaunch.

## 14. Liquid Glass writing surface

Use Liquid Glass for a bounded formatting or review cluster:

~~~text
document title/save state
    -> readable editor canvas and selection
        -> compact formatting/find/review controls
            -> explicit apply/discard/commit
~~~

Rules:

- the text remains the visual primary;
- the glass group contains real semantic actions;
- the material does not carry the meaning of dirty/saved/stale;
- the group reflows around the keyboard and iPadOS window size;
- Dynamic Type and long localized labels are allowed to expand;
- reduced transparency or increased contrast leaves the actions understandable;
- AI state is written as text/status, not only a sparkle icon;
- the editor remains usable if the glass group is replaced by an opaque system
  surface or a normal toolbar.

## 15. Proof contract

A text-editor claim needs more than a screenshot:

| Claim | Minimum evidence |
| --- | --- |
| Plain TextEditor edits text | Named-target compile and UI test with multiline input |
| Attributed TextEditor edits and formats | Selected SDK compile plus physical iOS/iPadOS or Catalyst run |
| Selection-aware review | Unit/fixture selection revision test plus UI selection task |
| Formatting definition constrains UI | Compile, visible control test, and full-value serialization validator |
| Find/replace route | Focused editor UI/system run with replace and undo |
| Writing Tools integration | Target/device capability check and physical text-view/editor run |
| Custom UIKit/TextKit escape hatch | Named target compile plus lifecycle/selection/accessibility run |
| Markdown import | Parser fixture tests for valid, partial, invalid, links, and custom attributes |
| AI proposal | Availability fixture, source-revision/stale test, review/commit test |
| Liquid Glass editor shell | Light/dark/accessibility-size/reduced-effects visual and task run |
| Document integration | T166 file/revision/autosave/conflict proof, not a text-only preview |
| Release readiness | Archive/process/entitlement/physical/TestFlight evidence recorded separately |

## Common failures

- Using plain String TextEditor while claiming rich document editing.
- Persisting TextSelection indices after the text has changed.
- Assuming every AttributedString attribute renders in SwiftUI.
- Applying formatting UI that the document writer cannot preserve.
- Letting off-screen attributed values bypass the formatting policy at save time.
- Running app autosave or cloud sync while Writing Tools is making temporary
  changes.
- Treating Writing Tools as an app-owned Foundation Models result.
- Calling findNavigator in a hierarchy with multiple unfocused editors and
  assuming the target is deterministic.
- Sending full documents to an AI feature for a selection-sized request.
- Applying a generated attributed value without link/attribute/schema validation.
- Putting essential writing controls in a glass effect with no accessible
  fallback.
- Testing only Preview/Simulator and claiming keyboard, Pencil, Writing Tools,
  VoiceOver, performance, or release behavior.

## Related routes

- [Native typography and rich-editor design](../21-design-deep-dives/77-native-typography-and-rich-editor-design.md)
- [Rich text and custom TextRenderer routes](../10-swiftui/10-rich-text-and-text-renderers.md)
- [TextKit 2 and Core Text layout](57-textkit-2-and-core-text-layout.md)
- [TextKit 2 rich-editor and AI annotation route](../50-capability-recipes/80-textkit-2-rich-editor-and-ai-annotation-route.md)
- [Document apps and file workflows](86-swiftui-document-apps-and-file-workflows.md)

## Sources

- [Text input and output](https://developer.apple.com/documentation/swiftui/text-input-and-output)
- [TextEditor](https://developer.apple.com/documentation/swiftui/texteditor)
- [TextSelection](https://developer.apple.com/documentation/swiftui/textselection)
- [AttributedTextSelection](https://developer.apple.com/documentation/swiftui/attributedtextselection)
- [AttributedTextFormattingDefinition](https://developer.apple.com/documentation/swiftui/attributedtextformattingdefinition)
- [AttributedTextValueConstraint](https://developer.apple.com/documentation/swiftui/attributedtextvalueconstraint)
- [AttributedString](https://developer.apple.com/documentation/foundation/attributedstring)
- [Markdown parsing](https://developer.apple.com/documentation/foundation/instantiating-attributed-strings-with-markdown-syntax)
- [MarkdownParsingOptions](https://developer.apple.com/documentation/foundation/attributedstring/markdownparsingoptions)
- [Text input and symbol modifiers](https://developer.apple.com/documentation/swiftui/view-text-and-symbols)
- [Text input formatting control visibility](https://developer.apple.com/documentation/swiftui/view/textinputformattingcontrolvisibility%28_%3Afor%3A%29)
- [WritingToolsBehavior](https://developer.apple.com/documentation/swiftui/writingtoolsbehavior)
- [writingToolsBehavior(_:)](https://developer.apple.com/documentation/swiftui/view/writingtoolsbehavior%28_%3A%29)
- [writingToolsAffordanceVisibility(_:)](https://developer.apple.com/documentation/swiftui/view/writingtoolsaffordancevisibility%28_%3A%29)
- [Writing Tools for UIKit](https://developer.apple.com/documentation/uikit/writing-tools)
- [Customizing Writing Tools behavior for system views](https://developer.apple.com/documentation/uikit/customizing-writing-tools-behavior-for-system-views)
- [TextKit 2 interaction sample](https://developer.apple.com/documentation/uikit/using-textkit-2-to-interact-with-text)
- [UIKit integration](https://developer.apple.com/documentation/swiftui/uikit-integration)
- [findNavigator(isPresented:)](https://developer.apple.com/documentation/swiftui/view/findnavigator%28ispresented%3A%29)
- [FindContext](https://developer.apple.com/documentation/swiftui/findcontext)
- [Typography HIG](https://developer.apple.com/design/human-interface-guidelines/typography)
- [Text views HIG](https://developer.apple.com/design/human-interface-guidelines/text-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adding intelligent app features with generative models](https://developer.apple.com/documentation/foundationmodels/adding-intelligent-app-features-with-generative-models)
