# SwiftUI text-editing and rich-content recipes

## Recipe rules

These snippets are route starters for a named app target. They are not compiled
in this documentation workspace and do not prove TextEditor formatting,
selection fidelity, Writing Tools availability, find/replace behavior,
keyboard/Pencil/VoiceOver input, document persistence, or on-device model
readiness.

Before copying a recipe:

1. Confirm the selected iOS 26 SDK signature and availability.
2. Name the canonical content model and document format.
3. Keep selection, focus, formatting UI, system-tool activity, and AI candidate
   state separate from durable document content.
4. Test plain, attributed, Markdown, long, localized, RTL, malformed, and
   unsupported-content fixtures.
5. Test editing, selection, formatting, find/replace, undo, Writing Tools,
   cancellation, document save/conflict, and AI stale-result behavior.
6. Record physical-device, system-surface, performance, archive, and release
   evidence separately.

Tilde fences keep the examples copyable inside this Markdown page.

## 1. Plain long-form editor

Use String when inline formatting is not part of the durable document.

~~~swift
struct PlainWritingEditor: View {
    @Binding var text: String
    @FocusState private var isFocused: Bool

    var body: some View {
        TextEditor(text: $text)
            .font(.body)
            .focused($isFocused)
            .textInputAutocapitalization(.sentences)
            .autocorrectionDisabled(false)
            .scrollDismissesKeyboard(.interactively)
            .padding(.horizontal)
    }
}
~~~

The surrounding feature owns document identity, revision, dirty state, autosave,
conflict, and validation. Global font/color/line-spacing modifiers do not make
this a rich-text editor.

## 2. Attributed editor with selection

Use the styled initializer when the target SDK supports attributed editing.

~~~swift
struct AttributedWritingEditor: View {
    @Binding var text: AttributedString
    @Binding var selection: AttributedTextSelection?
    @FocusState private var isFocused: Bool

    var body: some View {
        TextEditor(text: $text, selection: $selection)
            .focused($isFocused)
            .font(.body)
    }
}
~~~

The exact selection binding type and availability should be checked in the
selected SDK. Add an availability branch or a plain-text editor fallback if the
app supports targets where the attributed initializer is unavailable.

## 3. Formatting definition

Constrain the visible formatting surface to a product-owned policy.

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

struct ConstrainedAttributedEditor: View {
    @Binding var text: AttributedString
    @Binding var selection: AttributedTextSelection?

    var body: some View {
        TextEditor(text: $text, selection: $selection)
            .attributedTextFormattingDefinition(JournalFormatting())
    }
}
~~~

A formatting definition constrains the user-visible SwiftUI editor surface. It
does not guarantee that every value in the bound AttributedString is already
normalized. Run a full-document validator before serialization, export, share,
or commit.

## 4. Configure system formatting controls

Use system controls when they map to the file format.

~~~swift
struct SystemFormattingEditor: View {
    @Binding var text: AttributedString
    @Binding var selection: AttributedTextSelection?

    var body: some View {
        TextEditor(text: $text, selection: $selection)
            .textInputFormattingControlVisibility(
                .visible,
                for: .all
            )
    }
}
~~~

The placement set and availability are SDK-sensitive. If the app uses a custom
toolbar, hide only duplicate controls after the custom actions have labels,
keyboard routes, mixed-selection behavior, and undo proof.

## 5. Read a String selection

Resolve selection indices only against the current String.

~~~swift
enum SelectionReadError: Error {
    case noSelection
    case unsupportedSelection
}

func selectedText(
    in text: String,
    selection: TextSelection?
) throws -> String {
    guard let selection, let indices = selection.indices else {
        throw SelectionReadError.noSelection
    }

    switch indices {
    case .selection(let range):
        return String(text[range])
    case .multiSelection(let ranges):
        return ranges.map { String(text[$0]) }.joined(separator: "\n")
    @unknown default:
        throw SelectionReadError.unsupportedSelection
    }
}
~~~

Confirm the current TextSelection.Indices cases in the target SDK. For a
long-lived proposal, copy the selected text and source revision into a request
fixture; do not persist the selection index as the proposal's only identity.

## 6. Read an attributed selection

Use AttributedString.Index ranges and keep attributes intentionally.

~~~swift
func selectedAttributedText(
    in text: AttributedString,
    selection: AttributedTextSelection?
) -> AttributedString? {
    guard let selection, let range = selection.range else {
        return nil
    }
    return AttributedString(text[range])
}
~~~

The exact AttributedTextSelection range API is SDK-sensitive. Check whether the
target exposes one or more ranges and handle insertion points separately. Test
mixed attributes, Unicode graphemes, bidirectional text, and a source edit
between selection capture and review.

## 7. Make a revision-scoped selection request

Keep the selection and document identity together.

~~~swift
struct SelectionRequest: Sendable, Equatable {
    let documentID: UUID
    let sourceRevision: Int
    let selectedText: String
    let selectionDescription: String
}

func makeRequest(
    documentID: UUID,
    revision: Int,
    text: String,
    selection: TextSelection?
) throws -> SelectionRequest {
    let selected = try selectedText(in: text, selection: selection)
    return SelectionRequest(
        documentID: documentID,
        sourceRevision: revision,
        selectedText: selected,
        selectionDescription: "current selection"
    )
}
~~~

At completion, compare document ID and source revision before showing an Apply
action. A selection request can be stale even when its string is identical.

## 8. Native find and replace

Let SwiftUI drive the system find navigator for one focused editor.

~~~swift
struct FindablePlainEditor: View {
    @Binding var text: String
    @State private var isFinding = false

    var body: some View {
        TextEditor(text: $text)
            .findNavigator(isPresented: $isFinding)
            .toolbar {
                ToolbarItem(placement: .primaryAction) {
                    Button {
                        isFinding = true
                    } label: {
                        Label("Find", systemImage: "magnifyingglass")
                    }
                }
            }
    }
}
~~~

If a view hierarchy contains multiple editors, do not assume an unfocused
navigator targets the intended one. Define a single editor owner or build a
FindContext-based custom route. A replace operation must increment the document
revision and use ordinary undo/save/conflict handling.

## 9. Find policy for read-only or protected text

Bind native modifiers to document policy.

~~~swift
struct ProtectedTextEditor: View {
    @Binding var text: String
    let isReadOnly: Bool
    let allowReplace: Bool
    @State private var isFinding = false

    var body: some View {
        TextEditor(text: $text)
            .disabled(isReadOnly)
            .findDisabled(isReadOnly)
            .replaceDisabled(!allowReplace || isReadOnly)
            .findNavigator(isPresented: $isFinding)
    }
}
~~~

The target should verify how disabled state and find/replace modifiers compose.
Provide a visible explanation or alternate copy/search route for read-only
content.

## 10. Writing Tools policy

Make the system-owned policy explicit in the view.

~~~swift
enum WritingToolsPolicy: Equatable, Sendable {
    case automatic
    case limited
    case complete
    case disabled
}

struct WritingToolsEditor: View {
    @Binding var text: String
    let policy: WritingToolsPolicy

    var body: some View {
        editor
            .writingToolsAffordanceVisibility(.visible)
    }

    @ViewBuilder
    private var editor: some View {
        switch policy {
        case .automatic:
            TextEditor(text: $text)
                .writingToolsBehavior(.automatic)
        case .limited:
            TextEditor(text: $text)
                .writingToolsBehavior(.limited)
        case .complete:
            TextEditor(text: $text)
                .writingToolsBehavior(.complete)
        case .disabled:
            TextEditor(text: $text)
                .writingToolsBehavior(.disabled)
        }
    }
}
~~~

This is a route sketch; the concrete view-builder shape may need adjustment in
the target. Test automatic, limited, complete, disabled, unavailable, cancel,
interruption, and final-change behavior on a supported physical target.

## 11. Gate app mutations while Writing Tools is active

Treat system text operations as a mutation boundary.

~~~swift
enum TextMutationGate: Equatable, Sendable {
    case open
    case writingToolsActive
    case appReviewActive
    case conflict
}

@MainActor
final class WritingCoordinator: ObservableObject {
    @Published private(set) var gate: TextMutationGate = .open

    func beginSystemEditing() {
        guard gate == .open else { return }
        gate = .writingToolsActive
    }

    func endSystemEditing() {
        if gate == .writingToolsActive {
            gate = .open
        }
    }

    func canApplyAppCandidate() -> Bool {
        gate == .open
    }
}
~~~

SwiftUI's public callbacks may not expose every lifecycle event needed by a
complex editor. For a custom UIKit surface, use the UIKit Writing Tools
coordinator/delegate route. Never run app autosave, cloud transforms, and model
rewrites against temporary system text changes without a policy.

## 12. Parse Markdown with explicit options

Use raw source plus diagnostics when recovery matters.

~~~swift
struct MarkdownParseResult: Sendable {
    let source: String
    let value: AttributedString
}

func parseMarkdown(_ source: String) throws -> MarkdownParseResult {
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
    return MarkdownParseResult(source: source, value: value)
}
~~~

Verify the exact failure-policy cases in the SDK. Test invalid delimiters,
malformed links, Unicode, source-position mapping, relative links, and
unsupported attributes. If a partial parse is shown, label it as partial and
keep the raw source available.

## 13. Validate link attributes

A link attribute is data, not permission.

~~~swift
struct LinkPolicy: Sendable {
    let allowedSchemes: Set<String>
    let allowedHosts: Set<String>

    func allows(_ url: URL) -> Bool {
        guard let scheme = url.scheme?.lowercased(),
              allowedSchemes.contains(scheme) else {
            return false
        }
        guard let host = url.host?.lowercased() else {
            return true
        }
        return allowedHosts.contains(host)
    }
}
~~~

Apply the policy after Markdown parsing and before a link becomes an action.
Normalize Unicode/host/punycode policy deliberately. Validate model-proposed
links and imported content the same way as user-authored links.

## 14. Define a writing proposal state

Use a fixture that can drive preview, tests, and an actual adapter.

~~~swift
struct WritingCandidate: Equatable, Sendable {
    let id: UUID
    let documentID: UUID
    let sourceRevision: Int
    let sourceText: String
    let proposedText: String
    let operation: String
}

enum WritingReviewState: Equatable, Sendable {
    case unavailable(String)
    case ready
    case reviewing
    case partial(String)
    case candidate(WritingCandidate)
    case stale(candidateRevision: Int, currentRevision: Int)
    case failed(String)
    case committed(revision: Int)
}
~~~

Do not persist the candidate as ordinary document content until the person
accepts it and the document validator passes.

## 15. Apply an AI candidate safely

Keep commit on the document mutation path.

~~~swift
enum WritingApplyError: Error {
    case wrongDocument
    case staleRevision
    case invalidText
}

struct WritingDocument: Sendable {
    let documentID: UUID
    var revision: Int
    var text: String

    mutating func apply(
        _ candidate: WritingCandidate
    ) throws {
        guard candidate.documentID == documentID else {
            throw WritingApplyError.wrongDocument
        }
        guard candidate.sourceRevision == revision else {
            throw WritingApplyError.staleRevision
        }
        guard !candidate.proposedText.isEmpty else {
            throw WritingApplyError.invalidText
        }

        text = candidate.proposedText
        revision += 1
    }
}
~~~

A real app should validate length, Unicode, attributes, links, format version,
authorization, and conflict state before the mutation. On failure, keep the
original document and candidate visible for recovery.

## 16. Review UI with a bounded Liquid Glass group

Keep the document canvas outside the material.

~~~swift
struct WritingReviewControls: View {
    let state: WritingReviewState
    let review: () -> Void
    let apply: () -> Void
    let discard: () -> Void

    var body: some View {
        HStack(spacing: 12) {
            Label("Writing review", systemImage: "sparkles")

            switch state {
            case .ready:
                Button("Review selection", action: review)
            case .candidate:
                Button("Apply", action: apply)
                Button("Discard", action: discard)
            case .unavailable, .reviewing, .partial, .stale, .failed, .committed:
                EmptyView()
            }

            Text(statusText)
                .accessibilityLabel(statusText)
        }
        .padding(10)
        .glassEffect()
    }

    private var statusText: String {
        switch state {
        case .unavailable(let reason): return "Unavailable: \(reason)"
        case .ready: return "Ready"
        case .reviewing: return "Reviewing"
        case .partial: return "Partial result"
        case .candidate: return "Proposal ready"
        case .stale: return "Proposal out of date"
        case .failed: return "Review failed"
        case .committed: return "Applied"
        }
    }
}
~~~

Verify the current Liquid Glass API and availability in the target. The status
must remain useful with reduced transparency, increased contrast, Dynamic Type,
VoiceOver, and an opaque fallback.

## 17. Bridge a TextKit 2 editor

Escalate only for capabilities SwiftUI does not provide.

~~~swift
struct TextKitEditor: UIViewRepresentable {
    @Binding var value: NSAttributedString

    func makeCoordinator() -> Coordinator {
        Coordinator(parent: self)
    }

    func makeUIView(context: Context) -> UITextView {
        let view = UITextView(usingTextLayoutManager: true)
        view.delegate = context.coordinator
        return view
    }

    func updateUIView(
        _ view: UITextView,
        context: Context
    ) {
        guard view.attributedText != value else { return }
        view.attributedText = value
    }

    final class Coordinator: NSObject, UITextViewDelegate {
        var parent: TextKitEditor

        init(parent: TextKitEditor) {
            self.parent = parent
        }

        func textViewDidChange(_ textView: UITextView) {
            parent.value = textView.attributedText
        }
    }
}
~~~

Confirm the TextKit 2 initializer, delegate/concurrency annotations, and
AttributedString conversion in the selected SDK. Add selection, undo,
first-responder, Writing Tools, Dynamic Type, accessibility, and coordinator
teardown tests. Keep one source-of-truth boundary to avoid update loops.

## 18. Keep document revision and editor state separate

Use separate values in the document scene.

~~~swift
struct DocumentWritingState: Equatable, Sendable {
    let documentID: UUID
    var documentRevision: Int
    var editorSelectionDescription: String?
    var saveState: String
    var writingToolsState: String
    var reviewState: String
}
~~~

Persist durable document content and revision through FileDocument or the
app's storage layer. Restore only small editor continuity values. Do not write
a cursor range, model context, or temporary Writing Tools state into the file
unless the format explicitly owns it.

## 19. Add target-aware commands

Expose the same writing actions through native command surfaces.

~~~swift
struct WritingCommands: Commands {
    var body: some Commands {
        CommandGroup(after: .textEditing) {
            Button("Review Selection") {
                // Route to a selection/revision-aware coordinator.
            }
            .keyboardShortcut("r", modifiers: [.command, .option])

            Button("Find in Document") {
                // Toggle the focused editor's find navigator.
            }
            .keyboardShortcut("f", modifiers: [.command])
        }
    }
}
~~~

The exact command group placement is target-sensitive. On iPadOS, pair commands
with visible controls. On Catalyst, verify menu titles, focus, pointer, and
keyboard behavior. On iPhone, use the native compact route.

## 20. Build a proof fixture

Use a fixture that exercises visual and semantic states without a model.

~~~swift
struct WritingAcceptanceFixture: Hashable, Sendable {
    let target: String
    let contentModel: String
    let sourceRevision: Int
    let selection: String
    let formatting: String
    let findState: String
    let writingToolsState: String
    let aiState: String
    let dynamicType: String
    let input: String
}

let fixture = WritingAcceptanceFixture(
    target: "iPadOS",
    contentModel: "AttributedString",
    sourceRevision: 41,
    selection: "selected paragraph",
    formatting: "mixed",
    findState: "closed",
    writingToolsState: "unavailable",
    aiState: "candidate",
    dynamicType: "accessibility3",
    input: "keyboard"
)
~~~

For each fixture, record what the user sees, which action is enabled, what
revision is authoritative, what accessibility says, and which runtime artifact
supports the claim.

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
- [TextKit 2 interaction sample](https://developer.apple.com/documentation/uikit/using-textkit-2-to-interact-with-text)
- [UIKit integration](https://developer.apple.com/documentation/swiftui/uikit-integration)
- [AttributedString](https://developer.apple.com/documentation/foundation/attributedstring)
- [Instantiating attributed strings with Markdown syntax](https://developer.apple.com/documentation/foundation/instantiating-attributed-strings-with-markdown-syntax)
- [MarkdownParsingOptions](https://developer.apple.com/documentation/foundation/attributedstring/markdownparsingoptions)
- [Typography HIG](https://developer.apple.com/design/human-interface-guidelines/typography)
- [Text views HIG](https://developer.apple.com/design/human-interface-guidelines/text-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adding intelligent app features with generative models](https://developer.apple.com/documentation/foundationmodels/adding-intelligent-app-features-with-generative-models)
