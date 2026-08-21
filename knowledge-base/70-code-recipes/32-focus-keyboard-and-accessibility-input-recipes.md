# Focus, keyboard, pointer, and accessibility input recipes

## Compile boundary

These are route sketches for a named iOS 26 target, not compiled code in this documentation workspace. Confirm exact overloads, availability, imports, target membership, platform behavior, and assistive technology behavior in Xcode. Prefer native controls and keep model output out of focus authority.

## Recipe 1: typed field focus

    enum Field: Hashable {
        case title
        case body
    }

    struct FocusedForm: View {
        @State private var title = ""
        @State private var body = ""
        @FocusState private var focusedField: Field?

        var body: some View {
            Form {
                TextField("Title", text: $title)
                    .focused($focusedField, equals: .title)
                    .submitLabel(.next)

                TextField("Body", text: $body)
                    .focused($focusedField, equals: .body)
                    .submitLabel(.done)
            }
            .onSubmit {
                switch focusedField {
                case .title:
                    focusedField = .body
                case .body:
                    focusedField = nil
                case .none:
                    break
                }
            }
        }
    }

Use the actual field order and validation policy. Do not move focus if the person is using a different input method or if an asynchronous model update merely changed supporting text.

## Recipe 2: validation and accessibility focus

    enum AccessibilityTarget: Hashable {
        case error
        case result
    }

    struct ValidatedEditor: View {
        @State private var errorMessage: String?
        @AccessibilityFocusState private var accessibilityTarget: AccessibilityTarget?

        var body: some View {
            VStack {
                EditorContent()

                if let errorMessage {
                    Text(errorMessage)
                        .accessibilityLabel("Validation error")
                        .accessibilityValue(errorMessage)
                        .accessibilityFocused(
                            $accessibilityTarget,
                            equals: .error
                        )
                }
            }
        }

        func showError(_ message: String) {
            errorMessage = message
            accessibilityTarget = .error
        }
    }

Accessibility focus should move for a meaningful validation or requested result. Confirm the exact property-wrapper and modifier syntax in the selected SDK, and test with an active VoiceOver/assistive technology route.

## Recipe 3: apply a standard keyboard shortcut

    Button("Apply suggestion") {
        applySuggestion()
    }
    .keyboardShortcut(.defaultAction)

Use a standard shortcut only when the action is actually the default action. A visible button and its shortcut must share validation, source-revision checks, loading state, cancellation, and success/error reporting.

## Recipe 4: bounded key press

    ReviewSurface()
        .focusable()
        .onKeyPress(.return) {
            guard canApply else { return .ignored }
            applySuggestion()
            return .handled
        }

Use onKeyPress for a focused custom surface only when a semantic Button/keyboardShortcut route is insufficient. Return ignored when the event belongs to normal text editing or other system dispatch. Test repeat and international keyboard layouts.

## Recipe 5: focused document context

    struct Document {
        var title: String
    }

    extension FocusedValues {
        @Entry var focusedDocument: Binding<Document>?
    }

    struct DocumentEditor: View {
        @Binding var document: Document

        var body: some View {
            TextField("Title", text: $document.title)
                .focusedValue(\.focusedDocument, $document)
        }
    }

    struct DocumentCommands: View {
        @FocusedBinding(\.focusedDocument)
        private var document: Document?

        var body: some View {
            Button("Rename focused document") {
                document?.title = "Renamed"
            }
            .disabled(document == nil)
        }
    }

Focused values are optional and nearest-focused values win. Keep the command safe when there is no focused document, the document is read-only, or a revision check fails. The exact macro and property-wrapper availability are SDK-sensitive.

## Recipe 6: accessible custom action

    ReviewBadge(state: state)
        .accessibilityLabel("Suggestion")
        .accessibilityValue(state.accessibilityValue)
        .accessibilityAction(named: "Apply") {
            applySuggestion()
        }
        .accessibilityAction(named: "Discard") {
            discardSuggestion()
        }

Prefer separate native buttons when the actions deserve separate focus targets. Use named accessibility actions when a compact semantic element truly owns a small set of related operations. Keep the actions available without pointer hover or a custom gesture.

## Recipe 7: pointer feedback with fallback

    Button("Inspect source") {
        inspectSource()
    }
    .pointerStyle(.link)

The exact pointer style and platform availability must be confirmed in the target. The button remains the semantic action for touch, keyboard, VoiceOver, Voice Control, and Switch Control. Pointer styling is feedback, not discovery authority.

## Recipe 8: focused AI suggestion

    enum SuggestionState {
        case idle
        case generating(sourceRevision: UUID)
        case ready(Draft)
        case stale
        case unavailable
    }

    func requestSuggestion(
        text: String,
        selection: String?,
        sourceRevision: UUID
    ) async {
        guard userInitiated else { return }
        state = .generating(sourceRevision: sourceRevision)
        do {
            let draft = try await model.generate(
                text: text,
                selection: selection,
                maximumOutputCharacters: 1200
            )
            guard currentRevision == sourceRevision else {
                state = .stale
                return
            }
            state = .ready(draft)
        } catch is CancellationError {
            state = .idle
        } catch {
            state = .unavailable
        }
    }

The model never chooses the focused field or accessibility target. The app validates source revision, selection, output, and action availability before showing or applying the draft.

## Recipe 9: input fixture matrix

    let inputFixtures = [
        "touch",
        "hardware-keyboard",
        "full-keyboard-access",
        "pointer",
        "voiceover",
        "voice-control",
        "switch-control",
        "large-text",
        "rtl",
        "reduced-effects",
        "stale-ai-proposal"
    ]

For each fixture, record input focus, accessibility focus, selected range, command context, proposal state, result announcement, and whether the person completed the same outcome. Use a physical device for assistive technology, keyboard/pointer feel, text entry, and material behavior.

## Sources

- [Focus](https://developer.apple.com/documentation/swiftui/focus)
- [FocusState](https://developer.apple.com/documentation/swiftui/focusstate)
- [FocusedValues](https://developer.apple.com/documentation/swiftui/focusedvalues)
- [FocusedBinding](https://developer.apple.com/documentation/swiftui/focusedbinding)
- [FocusedValueKey](https://developer.apple.com/documentation/swiftui/focusedvaluekey)
- [Focusable](https://developer.apple.com/documentation/swiftui/view/focusable%28_%3A%29)
- [Input events](https://developer.apple.com/documentation/swiftui/input-events)
- [KeyboardShortcut](https://developer.apple.com/documentation/swiftui/keyboardshortcut)
- [AccessibilityFocusState](https://developer.apple.com/documentation/swiftui/accessibilityfocusstate)
- [Accessibility focused](https://developer.apple.com/documentation/swiftui/view/accessibilityfocused%28_%3A%29)
- [Accessible controls](https://developer.apple.com/documentation/swiftui/accessible-controls)
- [TextField](https://developer.apple.com/documentation/swiftui/textfield)
- [TextEditor](https://developer.apple.com/documentation/swiftui/texteditor)
- [TextSelection](https://developer.apple.com/documentation/swiftui/textselection)
- [AttributedTextSelection](https://developer.apple.com/documentation/swiftui/attributedtextselection)
- [Human Interface Guidelines: Focus and selection](https://developer.apple.com/design/human-interface-guidelines/focus-and-selection)
- [Human Interface Guidelines: Keyboards](https://developer.apple.com/design/human-interface-guidelines/keyboards)
- [Human Interface Guidelines: Pointing devices](https://developer.apple.com/design/human-interface-guidelines/pointing-devices)
- [Human Interface Guidelines: Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
