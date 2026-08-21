# SwiftUI text-editing and rich-content capability route

## Use this route when

Choose this route when the feature needs a SwiftUI writing surface rather than
only a read-only text projection:

- multiline plain-text entry;
- inline formatting or attributed selection;
- selection-scoped suggestions or review;
- system find and replace;
- Writing Tools behavior and affordance policy;
- Markdown or attributed-content import;
- a document editor that must keep content and editor state separate;
- iPadOS keyboard/Pencil and Mac Catalyst command/pointer adaptation;
- an optional on-device AI writing proposal;
- a bounded UIKit/TextKit 2 escape hatch.

Use the existing TextKit 2 route when the central problem is custom viewport
layout, attachments, text elements, or glyph geometry. Use this route when the
central problem is coordinating the SwiftUI editor, selection, formatting,
system text tools, and document revision.

## Route contract

Complete these decisions before implementing the view.

| Field | Required decision |
| --- | --- |
| User outcome | What can the person write, select, format, find, review, or commit? |
| Content model | String, AttributedString, source Markdown, or richer editor model |
| Canonical format | What is persisted and how is it migrated? |
| Editor initializer | TextEditor plain or attributed initializer; fallback target |
| Selection | TextSelection or AttributedTextSelection; revision and affinity policy |
| Formatting | Allowed attribute scope, mixed-value behavior, system controls, writer |
| Input | Keyboard, dictation, Pencil, pointer, VoiceOver, Voice Control, Switch Control |
| Find/replace | Native navigator or custom FindContext route; focused editor owner |
| Writing Tools | automatic, limited, complete, disabled, or custom UIKit coordinator |
| UIKit bridge | Why SwiftUI is insufficient; ownership and teardown boundary |
| Markdown | Syntax, custom attributes, source positions, links, failure policy |
| AI | Capability, source scope, candidate schema, stale policy, commit path |
| Document | File URL, scene/window, autosave/conflict, provider state |
| Material | Glass action group, opaque fallback, accessibility behavior |
| Targets | iPhone, iPadOS, Catalyst, visionOS/watchOS projection, extensions |
| Proof | Compile, parser, formatting, selection, UI, physical, system, release |

## Route selection table

| Scenario | Route | Key proof |
| --- | --- | --- |
| Plain note | TextEditor Binding<String> | Multiline input, focus, save, accessibility |
| Styled note | TextEditor Binding<AttributedString> plus AttributedTextSelection | Formatting, serializer, selection, Dynamic Type |
| Limited format | AttributedTextFormattingDefinition | System control policy and full-value validation |
| Source Markdown | String source + parsed attributed preview/editor | Parse diagnostics, links, round-trip decision |
| Searchable editor | findNavigator on one focused editor | Find/replace, undo, keyboard, localization |
| System writing | writingToolsBehavior | Physical/device capability and conflict with app mutations |
| App-owned writing AI | Foundation Models adapter | Source revision, candidate review, commit, fallback |
| Rich attachments | SwiftUI shell + UIKit/TextKit 2 adapter | TextKit lifecycle, selection, viewport, accessibility |
| Custom visual annotation | TextAttribute/TextRenderer | Readability, semantics, reduced effects, performance |
| Document editor | T166 DocumentGroup/FileDocument route + this editor | File, autosave, conflict, revision, device proof |

## 1. Establish the source of truth

Use one content model and derive the editor projection.

~~~swift
struct WritingDocumentState: Sendable {
    let documentID: UUID
    var sourceRevision: Int
    var content: AttributedString
    var saveState: String
}
~~~

If the canonical format is plain text, keep AttributedString as a temporary
projection only when necessary. If formatting is canonical, write and migrate
the attributed representation intentionally. If Markdown is canonical, keep
the source and parse diagnostics available.

Do not use:

- a view's line/character frame as document identity;
- a TextSelection index as a durable span ID;
- a renderer attribute as a security or permission boundary;
- a generated candidate as an automatically committed document;
- a file URL as the only revision source.

## 2. Choose plain or attributed TextEditor

Use plain editing:

~~~swift
TextEditor(text: $plainText)
~~~

Use attributed editing when the selected SDK and target support it:

~~~swift
TextEditor(text: $attributedText, selection: $attributedSelection)
~~~

Confirm:

- the selected SDK signature;
- deployment target and platform availability;
- whether the target receives the system formatting controls;
- how selection indices map to the chosen value;
- whether the writer preserves every allowed attribute;
- which fallback is provided if attributed editing is unavailable.

Do not call a globally styled plain editor “rich text.” Do not offer inline
formatting if the document writer will drop it.

## 3. Add a formatting definition

A formatting definition is the product's allowed editing surface.

~~~swift
struct JournalFormatting: AttributedTextFormattingDefinition {
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

struct JournalEditor: View {
    @Binding var text: AttributedString
    @Binding var selection: AttributedTextSelection?

    var body: some View {
        TextEditor(text: $text, selection: $selection)
            .attributedTextFormattingDefinition(JournalFormatting())
    }
}
~~~

Use custom attribute scopes when semantic metadata matters. Keep review source
IDs, contact IDs, or protected-range markers distinct from visual attributes.
Before saving or exporting, constrain/validate the whole value, including
off-screen ranges.

## 4. Configure formatting visibility

Use the system controls where they are useful:

~~~swift
TextEditor(text: $text, selection: $selection)
    .textInputFormattingControlVisibility(
        .visible,
        for: .all
    )
~~~

The exact placement set and availability are SDK-sensitive. Verify the selected
platform and use the narrowest modifier that expresses the product policy. If a
custom toolbar is the primary route, hide duplicate system controls only after
the custom toolbar has labels, keyboard commands, and accessibility actions.

A visible formatting control must have:

- an allowed document attribute;
- a deterministic mixed-value state;
- an undo path;
- a persistence and migration test;
- a fallback if the action cannot be applied.

## 5. Read a selection safely

For String selection, derive a short-lived substring:

~~~swift
func selectedText(
    in text: String,
    selection: TextSelection?
) -> String? {
    guard let selection, let indices = selection.indices else {
        return nil
    }

    switch indices {
    case .selection(let range):
        return String(text[range])
    case .multiSelection(let ranges):
        return ranges.map { String(text[$0]) }.joined(separator: "\n")
    @unknown default:
        return nil
    }
}
~~~

The exact TextSelection.Indices cases are SDK-sensitive; confirm them before
compiling. For AttributedTextSelection, resolve AttributedString.Index ranges
against the current value and preserve attributes only if the review/format
route supports them.

Capture the current document revision at the same time as the selected value.
If the editor changes before an async action finishes, mark the candidate stale
or recompute the selection rather than applying by old indices.

## 6. Add find and replace

Use the native route for one focused editor:

~~~swift
struct SearchableWritingView: View {
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

If the hierarchy has several editors, define which one owns the find task or
provide a custom FindContext-driven implementation. Test replace, undo, close,
no matches, keyboard shortcuts, VoiceOver, localization, and document revision.

## 7. Choose Writing Tools policy

Write the policy as data so previews and proof fixtures can cover it.

~~~swift
enum WritingToolsPolicy: Equatable, Sendable {
    case automatic
    case limited
    case complete
    case disabled
}

@ViewBuilder
func writingToolsView(
    _ editor: some View,
    policy: WritingToolsPolicy
) -> some View {
    switch policy {
    case .automatic:
        editor.writingToolsBehavior(.automatic)
    case .limited:
        editor.writingToolsBehavior(.limited)
    case .complete:
        editor.writingToolsBehavior(.complete)
    case .disabled:
        editor.writingToolsBehavior(.disabled)
    }
}
~~~

The generic helper above is a route sketch; SwiftUI view-builder generic
constraints may require an AnyView or a concrete wrapper in a real target.

Policy examples:

- automatic for general prose;
- limited for an editor where the person should review changes in a contained
  experience;
- complete for a full writing surface that can absorb inline changes;
- disabled for code, immutable legal text, identifiers, or protected quotations.

Use writingToolsAffordanceVisibility for target-specific affordance policy,
especially when the same editor runs on Mac Catalyst. Do not claim that a
policy value guarantees that the system feature is available.

## 8. Pause conflicting mutations

Writing Tools can make temporary changes before a person approves or the system
incorporates final changes. App-specific autosave, cloud transforms, external
sync, and AI requests need a conflict policy.

~~~swift
enum EditorMutationGate: Equatable, Sendable {
    case open
    case writingToolsActive
    case appReviewActive
    case conflict
    case unavailable
}
~~~

At the editor boundary:

1. enter the gate before a system or app-owned editing operation;
2. suspend conflicting mutation streams;
3. preserve the last confirmed revision;
4. accept or reject the operation;
5. normalize the final content;
6. increment the revision;
7. resume autosave/sync only after the gate closes.

If the system feature's SwiftUI callbacks are not sufficient for the required
coordination, isolate a UIKit/TextKit 2 editor and use its Writing Tools
lifecycle APIs.

## 9. Parse Markdown and validate links

Use explicit Markdown options:

~~~swift
func parse(_ source: String) throws -> AttributedString {
    let options = AttributedString.MarkdownParsingOptions(
        allowsExtendedAttributes: false,
        interpretedSyntax: .full,
        failurePolicy: .returnPartiallyParsedIfPossible,
        languageCode: nil,
        appliesSourcePositionAttributes: true
    )
    return try AttributedString(
        markdown: source,
        options: options,
        baseURL: nil
    )
}
~~~

The exact failure policy and initializer signature must be verified in the
target SDK. Apply a link policy after parsing. Reject or neutralize unapproved
schemes, hosts, ports, or links that arrive from an AI candidate or imported
document. Keep raw source and diagnostics if the user needs to repair it.

## 10. Add app-owned AI review

Use an explicit adapter contract:

~~~swift
struct WritingCandidate: Equatable, Sendable {
    let candidateID: UUID
    let documentID: UUID
    let sourceRevision: Int
    let sourceText: String
    let proposedText: String
    let operation: String
}

enum WritingCandidateState: Equatable, Sendable {
    case unavailable(String)
    case ready
    case reviewing
    case candidate(WritingCandidate)
    case stale(candidateRevision: Int, currentRevision: Int)
    case failed(String)
}
~~~

The route is:

~~~text
selected content
    -> capability check
    -> bounded prompt/context
    -> typed proposal
    -> length/attribute/link validation
    -> candidate review
    -> accept/edit/discard
    -> document mutation
    -> autosave/conflict path
~~~

Use the system Writing Tools route when the task belongs to system text editing.
Use Foundation Models when the app needs a domain-specific proposal, structured
output, or an app-owned workflow. Do not present one as the other.

## 11. Build a document adapter

Connect the editor to the T166 document route:

~~~swift
struct DocumentWritingAdapter: Sendable {
    let documentID: UUID
    var content: AttributedString
    var revision: Int

    mutating func apply(
        _ candidate: WritingCandidate
    ) throws {
        guard candidate.documentID == documentID,
              candidate.sourceRevision == revision else {
            throw WritingError.staleCandidate
        }
        let replacement = try ValidatedAttributedContent(
            plainText: candidate.proposedText
        )
        content = replacement.value
        revision += 1
    }
}
~~~

The concrete validator should preserve supported attributes, reject unsafe links,
enforce document limits, and pass through FileDocument/ReferenceFileDocument
serialization. The candidate's source text is evidence for review, not an
instruction to bypass the current document value.

## 12. Use a focused UIKit/TextKit bridge when required

When SwiftUI cannot express the needed editor, keep one bridge:

~~~swift
struct RichTextView: UIViewRepresentable {
    @Binding var value: NSAttributedString

    func makeUIView(context: Context) -> UITextView {
        UITextView(usingTextLayoutManager: true)
    }

    func updateUIView(_ view: UITextView, context: Context) {
        guard view.attributedText != value else { return }
        view.attributedText = value
    }

    final class Coordinator: NSObject, UITextViewDelegate {
        var parent: RichTextView

        init(parent: RichTextView) {
            self.parent = parent
        }

        func textViewDidChange(_ textView: UITextView) {
            parent.value = textView.attributedText
        }
    }

    func makeCoordinator() -> Coordinator {
        Coordinator(parent: self)
    }
}
~~~

This is a sketch. The target must verify the TextKit 2 initializer and
main-actor/concurrency details. Add selection round-trip, undo, Writing Tools,
teardown, Dynamic Type, accessibility, and revision guards before production
use. If a value is an AttributedString, convert at a deliberate boundary and
define the allowed attribute scope.

## 13. Design the Liquid Glass editor shell

A route-level shell can be:

~~~text
document identity/status
    -> system text editor
        -> formatting/find command group
            -> AI review group
                -> explicit document commit
~~~

Glass should group actions rather than carry the document. Keep the status
textual and accessible:

- “Unsaved changes”
- “Formatting selection”
- “Writing Tools active”
- “Reviewing selection”
- “Proposal ready”
- “Proposal out of date”
- “Saved on this device”
- “Conflict needs review”

Every state needs a non-glass fallback. Test content behind the glass, keyboard
overlap, large text, increased contrast, reduced transparency, RTL, and Catalyst
menu/toolbar behavior.

## 14. Target matrix

| Target | Preferred editor route | Required evidence |
| --- | --- | --- |
| iPhone | TextEditor, native selection, sheet/toolbar review | Physical device with software keyboard and VoiceOver |
| iPadOS | Attributed TextEditor, keyboard/Pencil, find/format controls | Physical iPad with external keyboard and window resizing |
| Mac Catalyst | TextEditor or UIKit bridge, menus, pointer, Writing Tools affordance | Actual Catalyst compile/run and keyboard task |
| visionOS | Readable text/editor window when task is appropriate | visionOS target run; no unsupported spatial claim |
| watchOS | Short text entry or handoff/projection | Watch target run; no full document-editor claim |
| Document/File Provider extension | Keep editor in app; provider owns file lifecycle | Extension/system provider run plus document proof |

## Stop conditions

Stop and repair if:

- a plain String TextEditor is marketed as rich text;
- the attributed editor's binding can contain unsupported attributes that save
  without validation;
- selection indices survive edits without a revision check;
- find/replace can target an ambiguous editor;
- Writing Tools and app autosave/sync can mutate the same text concurrently;
- an AI candidate can apply without source revision and document validation;
- UIKit/TextKit 2 is added only for a visual effect that TextRenderer handles;
- Liquid Glass obscures text, selection, or essential writing actions;
- a device/system feature is claimed from Preview or Simulator only;
- the document editor lacks a non-AI and non-Writing-Tools fallback.

## Sources

- [Text input and output](https://developer.apple.com/documentation/swiftui/text-input-and-output)
- [TextEditor](https://developer.apple.com/documentation/swiftui/texteditor)
- [TextSelection](https://developer.apple.com/documentation/swiftui/textselection)
- [AttributedTextSelection](https://developer.apple.com/documentation/swiftui/attributedtextselection)
- [AttributedTextFormattingDefinition](https://developer.apple.com/documentation/swiftui/attributedtextformattingdefinition)
- [AttributedTextValueConstraint](https://developer.apple.com/documentation/swiftui/attributedtextvalueconstraint)
- [Text input and symbol modifiers](https://developer.apple.com/documentation/swiftui/view-text-and-symbols)
- [Text input formatting control visibility](https://developer.apple.com/documentation/swiftui/view/textinputformattingcontrolvisibility%28_%3Afor%3A%29)
- [findNavigator(isPresented:)](https://developer.apple.com/documentation/swiftui/view/findnavigator%28ispresented%3A%29)
- [FindContext](https://developer.apple.com/documentation/swiftui/findcontext)
- [WritingToolsBehavior](https://developer.apple.com/documentation/swiftui/writingtoolsbehavior)
- [writingToolsBehavior(_:)](https://developer.apple.com/documentation/swiftui/view/writingtoolsbehavior%28_%3A%29)
- [writingToolsAffordanceVisibility(_:)](https://developer.apple.com/documentation/swiftui/view/writingtoolsaffordancevisibility%28_%3A%29)
- [Writing Tools for UIKit](https://developer.apple.com/documentation/uikit/writing-tools)
- [Customizing Writing Tools behavior for system views](https://developer.apple.com/documentation/uikit/customizing-writing-tools-behavior-for-system-views)
- [AttributedString](https://developer.apple.com/documentation/foundation/attributedstring)
- [Markdown parsing](https://developer.apple.com/documentation/foundation/instantiating-attributed-strings-with-markdown-syntax)
- [MarkdownParsingOptions](https://developer.apple.com/documentation/foundation/attributedstring/markdownparsingoptions)
- [TextKit 2 interaction sample](https://developer.apple.com/documentation/uikit/using-textkit-2-to-interact-with-text)
- [UIKit integration](https://developer.apple.com/documentation/swiftui/uikit-integration)
- [Typography HIG](https://developer.apple.com/design/human-interface-guidelines/typography)
- [Text views HIG](https://developer.apple.com/design/human-interface-guidelines/text-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adding intelligent app features with generative models](https://developer.apple.com/documentation/foundationmodels/adding-intelligent-app-features-with-generative-models)
