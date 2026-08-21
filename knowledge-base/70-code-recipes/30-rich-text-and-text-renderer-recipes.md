# Rich text and TextRenderer recipes

## Compile boundary

These are route sketches for a named iOS 26 target, not compiled code in this documentation workspace. Confirm the exact SDK signature, availability, imports, target membership, and behavior in Xcode before copying them. Keep model requests, parsing, presentation, review, persistence, and side effects separate.

## Recipe 1: parse a bounded Markdown proposal

Start with the smallest initializer and add explicit parsing options when the product needs a documented policy:

    import Foundation
    import SwiftUI

    enum DraftParseResult {
        case success(AttributedString)
        case partial(AttributedString, Error)
        case failure(Error)
    }

    func parseDraft(_ input: String) -> DraftParseResult {
        do {
            let value = try AttributedString(markdown: input)
            return .success(value)
        } catch {
            return .failure(error)
        }
    }

Before calling the initializer, enforce the app’s maximum input length. If partial parsing is required, use AttributedString.MarkdownParsingOptions with an explicit failure policy and retain the raw input plus diagnostics. Do not use try! for model or imported content.

## Recipe 2: render a validated attributed value

    struct DraftTextView: View {
        let content: AttributedString

        var body: some View {
            Text(content)
                .font(.body)
                .textSelection(.enabled)
                .accessibilityTextContentType(.sourceCode)
        }
    }

The accessibility text content type in this sketch is only an example and may not match the product. Choose the semantic content type deliberately or omit it. The important route is that Text receives the validated value, supports user selection when needed, and retains a normal SwiftUI fallback.

## Recipe 3: attach a typed review marker

    struct ReviewHighlightAttribute: TextAttribute {
        let sourceID: String
    }

    let marked = Text("This sentence is linked to a source.")
        .customAttribute(ReviewHighlightAttribute(sourceID: "source-1"))

Only one attribute of a given type is attached to a Text view, and nested attributes of that type take precedence. Keep sourceID app-owned and validated. A TextAttribute should describe a bounded presentation or query value; it should not contain a closure, executable instruction, arbitrary URL, or navigation mutation.

## Recipe 4: draw a restrained run highlight

    struct ReviewHighlightRenderer: TextRenderer {
        var color: Color = .yellow.opacity(0.22)

        func draw(
            layout: Text.Layout,
            in context: inout GraphicsContext
        ) {
            for line in layout {
                for run in line {
                    if run[ReviewHighlightAttribute.self] != nil {
                        context.fill(
                            Path(run.typographicBounds.rect),
                            with: .color(color)
                        )
                    }
                }
                context.draw(line)
            }
        }
    }

    Text("This sentence is linked to a source.")
        .customAttribute(ReviewHighlightAttribute(sourceID: "source-1"))
        .textRenderer(ReviewHighlightRenderer())

This pattern draws a background shape from typographic bounds and then draws the line. Verify the exact drawing order, corner treatment, clipping, color contrast, and API availability in the target. Keep the underlying text visible. For a shadow or other effect that extends beyond the layout, implement displayPadding deliberately and test the bounds.

## Recipe 5: a renderer-aware review surface

    struct ReviewSurface: View {
        let content: AttributedString
        let isReducedEffects: Bool

        var body: some View {
            Group {
                if isReducedEffects {
                    Text(content)
                } else {
                    Text(content)
                        .textRenderer(ReviewHighlightRenderer())
                }
            }
            .font(.body)
            .textSelection(.enabled)
            .padding()
            .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 20))
        }
    }

The fallback should preserve the content, hierarchy, selection, and state label. The material in this sketch is a standard fallback, not proof that a Liquid Glass route is available or visually correct.

## Recipe 6: read layout attributes for a diagnostic overlay

    struct LayoutDiagnosticView: View {
        let content: Text

        var body: some View {
            content
                .overlayPreferenceValue(Text.LayoutKey.self) { layouts in
                    Color.clear
                        .allowsHitTesting(false)
                        .accessibilityHidden(true)
                }
        }
    }

Text.LayoutKey supplies anchored layout values for Text views in a queried subtree. The overlay above is intentionally incomplete: a production overlay must decide how to consume the anchored layouts, respond to content/font/width changes, and remove itself when the interaction is not needed. Do not derive durable source identity from a pixel position.

## Recipe 7: attributed editor with selection

    struct SuggestionEditor: View {
        @State private var text: AttributedString = ""
        @State private var selection = AttributedTextSelection()

        var body: some View {
            TextEditor(text: $text, selection: $selection)
                .onChange(of: selection) {
                    let selected = selection.indices(in: text)
                    requestSuggestion(for: selected, in: text)
                }
        }

        private func requestSuggestion(
            for indices: AttributedTextSelection.Indices,
            in text: AttributedString
        ) {
            // Capture the source revision and launch cancellable work.
            // Apply only after the user reviews the returned proposal.
        }
    }

The exact TextEditor selection overload and onChange signature are SDK-sensitive. Re-check them in the selected SDK. Never start uncancellable model work on every selection movement, and never apply a suggestion without checking the current text revision.

## Recipe 8: policy-check links before review

    struct LinkPolicy {
        let allowedSchemes: Set<String>
        let allowedHosts: Set<String>
    }

    func isAllowed(_ url: URL, by policy: LinkPolicy) -> Bool {
        guard let scheme = url.scheme?.lowercased(),
              policy.allowedSchemes.contains(scheme)
        else {
            return false
        }

        if let host = url.host?.lowercased() {
            return policy.allowedHosts.contains(host)
        }

        return true
    }

The product should inspect link attributes in the parsed AttributedString and remove or neutralize links that fail policy. A renderer must not be the security boundary. Test encoded hosts, Unicode domains, missing schemes, unexpected ports, and links that arrive from a model or imported document.

## Recipe 9: preserve proposal and approved record separately

    struct DraftState: Sendable {
        let sourceRevision: UUID
        let rawText: String
        let rendered: AttributedString
        let warnings: [String]
        let isApproved: Bool
    }

    func applyDraft(
        _ draft: DraftState,
        currentSourceRevision: UUID
    ) throws -> ApprovedRecord {
        guard draft.sourceRevision == currentSourceRevision else {
            throw ApplyError.staleSource
        }
        guard draft.isApproved else {
            throw ApplyError.userReviewRequired
        }
        return ApprovedRecord(content: draft.rendered)
    }

The concrete persistence model belongs to the app. The important boundary is that drawing, parsing, or model completion does not set isApproved. Make apply a user-visible action that can fail, be canceled, or require conflict resolution.

## Recipe 10: fixture matrix for rich text

    let fixtures = [
        "short",
        "multiline",
        "malformed-markdown",
        "long-output",
        "allowed-link",
        "disallowed-link",
        "mixed-direction",
        "emoji-and-diacritics",
        "truncated",
        "stale-proposal",
        "model-unavailable"
    ]

For each fixture, record the source revision, locale, Dynamic Type size, width, color scheme, reduced-effects setting, renderer branch, parser warnings, selection state, and resulting approved/discarded state. Use previews for deterministic layout exploration, unit tests for policy/state parsing, UI tests for interaction, and a physical device for text rendering, touch, selection, memory, and performance claims.

## Sources

- [Text](https://developer.apple.com/documentation/swiftui/text)
- [Text.customAttribute(_:)](https://developer.apple.com/documentation/swiftui/text/customattribute%28_%3A%29)
- [TextRenderer](https://developer.apple.com/documentation/swiftui/textrenderer)
- [TextAttribute](https://developer.apple.com/documentation/swiftui/textattribute)
- [Text.Layout](https://developer.apple.com/documentation/swiftui/text/layout)
- [Text.Layout.Run](https://developer.apple.com/documentation/swiftui/text/layout/run)
- [Text.Layout.TypographicBounds](https://developer.apple.com/documentation/swiftui/text/layout/typographicbounds)
- [Text.LayoutKey](https://developer.apple.com/documentation/swiftui/text/layoutkey)
- [GraphicsContext](https://developer.apple.com/documentation/swiftui/graphicscontext)
- [TextEditor](https://developer.apple.com/documentation/swiftui/texteditor)
- [TextSelection](https://developer.apple.com/documentation/swiftui/textselection)
- [AttributedTextSelection](https://developer.apple.com/documentation/swiftui/attributedtextselection)
- [AttributedString](https://developer.apple.com/documentation/foundation/attributedstring)
- [Instantiating attributed strings with Markdown syntax](https://developer.apple.com/documentation/foundation/instantiating-attributed-strings-with-markdown-syntax)
- [MarkdownParsingOptions](https://developer.apple.com/documentation/foundation/attributedstring/markdownparsingoptions)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [Human Interface Guidelines: Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
