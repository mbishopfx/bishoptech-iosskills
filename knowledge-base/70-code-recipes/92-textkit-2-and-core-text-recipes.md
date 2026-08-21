# TextKit 2 and Core Text recipes

These are compile-oriented route sketches for native text editing, viewport
layout, Core Text drawing, SwiftUI bridging, and reviewable AI annotations.
They are not claimed to compile in this documentation-only workspace.

Before copying a recipe:

- set the deployment target and iOS 26 SDK;
- confirm the current declaration and availability in Xcode;
- decide whether SwiftUI or UIKit owns the editor state;
- keep document revisions and proposal state outside the renderer;
- add fixtures for Dynamic Type, localization, selection, and stale results;
- test the signed target on a physical device.

## 1. Create a system UITextView with TextKit 2

Start here when you need UIKit editing behavior, keyboard integration, system
selection, find interaction, and a modern layout manager.

~~~swift
import UIKit

@MainActor
func makeRichTextView(
    initialText: NSAttributedString
) -> UITextView {
    let view = UITextView(usingTextLayoutManager: true)
    view.attributedText = initialText
    view.isEditable = true
    view.isSelectable = true
    view.alwaysBounceVertical = true
    view.backgroundColor = .clear
    view.textContainerInset = UIEdgeInsets(
        top: 24,
        left: 20,
        bottom: 24,
        right: 20
    )
    view.accessibilityLabel = "Document editor"
    return view
}
~~~

Treat this as a system editor surface, not as the domain model. The text view's
current attributed string and selected ranges are observations that must be
reconciled into the app's document state through a deliberate delegate or
adapter.

## 2. Build an explicit TextKit 2 document graph

Use this route when a custom display needs direct access to content storage,
layout fragments, and a text container.

~~~swift
import UIKit

@MainActor
final class TextKit2Document {
    let contentStorage = NSTextContentStorage()
    let layoutManager = NSTextLayoutManager()
    let textContainer: NSTextContainer

    init(size: CGSize, text: NSAttributedString) {
        textContainer = NSTextContainer(size: size)
        contentStorage.addTextLayoutManager(layoutManager)
        layoutManager.textContainer = textContainer
        contentStorage.attributedString = NSMutableAttributedString(
            attributedString: text
        )
    }

    func replaceCharacters(
        in range: NSRange,
        with replacement: String
    ) {
        contentStorage.performEditingTransaction {
            guard let mutable = contentStorage.attributedString
                as? NSMutableAttributedString else {
                return
            }
            mutable.replaceCharacters(in: range, with: replacement)
        }
    }
}
~~~

This sketch assumes the selected SDK exposes the current Swift declarations
shown in the official documentation. Compile it in a target and decide how the
document revision, undo manager, selection, and persistence adapter observe
editing transactions.

## 3. Measure visible TextKit 2 fragments

Use fragment geometry for overlays, pagination, or a review mark instead of
guessing line positions from character counts.

~~~swift
@MainActor
func visibleFragmentFrames(
    in document: TextKit2Document,
    bounds: CGRect
) -> [CGRect] {
    document.layoutManager.ensureLayout(for: bounds)

    var frames: [CGRect] = []
    document.layoutManager.enumerateTextLayoutFragments(
        from: nil,
        options: []
    ) { fragment in
        if fragment.layoutFragmentFrame.intersects(bounds) {
            frames.append(fragment.layoutFragmentFrame)
        }
        return true
    }
    return frames
}
~~~

Use the fragment's text line fragments when a precise source range, typographic
bound, caret position, or character hit test is needed. Store the source range
or stable source ID with the annotation; do not store the frame as durable
state.

## 4. Install a viewport delegate boundary

The viewport controller is useful for a custom scrolling surface that lays out
the visible region plus an overdraw area. Keep the delegate focused on
rendering-surface lifecycle.

~~~swift
import UIKit

@MainActor
final class TextViewportCoordinator: NSObject,
    NSTextViewportLayoutControllerDelegate {
    weak var surface: UIView?

    func viewportBounds(
        for controller: NSTextViewportLayoutController
    ) -> CGRect {
        surface?.bounds ?? .zero
    }

    func textViewportLayoutController(
        _ controller: NSTextViewportLayoutController,
        configureRenderingSurfaceFor textLayoutFragment: NSTextLayoutFragment
    ) {
        // Attach or update the view/layer that renders this fragment.
        // Keep source identity separate from the rendering surface.
    }

    func textViewportLayoutControllerWillLayout(
        _ controller: NSTextViewportLayoutController
    ) {
        // Cancel obsolete decoration work before visible layout begins.
    }

    func textViewportLayoutControllerDidLayout(
        _ controller: NSTextViewportLayoutController
    ) {
        // Publish measured usage bounds to the layout owner.
    }
}
~~~

The current SDK may require additional delegate methods or a call to super in
a UITextView subclass. Treat this as a boundary sketch and compile against the
selected target before relying on it.

## 5. Draw a bounded Core Text frame

Use Core Text for a custom drawing/export surface, not for ordinary editing.

~~~swift
import CoreText
import CoreGraphics

func drawFrame(
    attributedString: NSAttributedString,
    in context: CGContext,
    bounds: CGRect
) {
    let path = CGPath(
        rect: bounds,
        transform: nil
    )
    let framesetter = CTFramesetterCreateWithAttributedString(
        attributedString as CFAttributedString
    )
    let frame = CTFramesetterCreateFrame(
        framesetter,
        CFRangeMake(0, attributedString.length),
        path,
        nil
    )

    context.saveGState()
    context.translateBy(x: 0, y: bounds.maxY)
    context.scaleBy(x: 1, y: -1)
    CTFrameDraw(frame, context)
    context.restoreGState()
}
~~~

Record the coordinate-system transform as part of the renderer contract.
For hit testing, use CTFrameGetLines and CTFrameGetLineOrigins, then
CTLineGetStringIndexForPosition or related line APIs. Keep the framesetter,
frame, and line operation on one controlled queue or thread.

## 6. Use a Core Text line for exact hit testing

When a custom surface needs a line-level character lookup, keep the geometry
and source string together.

~~~swift
import CoreText
import CoreGraphics

func characterIndex(
    in line: CTLine,
    at point: CGPoint
) -> CFIndex {
    CTLineGetStringIndexForPosition(line, point)
}
~~~

The returned index is a UTF-16 string position from the line's source
attributed string. Convert it at the adapter boundary and account for
bidirectional text, ligatures, composed characters, and the coordinate system.
Do not use this index as a durable AI span without a revision and anchor check.

## 7. Bridge a TextKit 2 editor into SwiftUI

Use UIViewRepresentable when UIKit supplies behavior that SwiftUI's current
text surface does not yet provide for the target.

~~~swift
import SwiftUI
import UIKit

struct RichTextEditor: UIViewRepresentable {
    @Binding var value: NSAttributedString

    func makeUIView(context: Context) -> UITextView {
        let view = UITextView(usingTextLayoutManager: true)
        view.isEditable = true
        view.isSelectable = true
        view.backgroundColor = .clear
        view.delegate = context.coordinator
        view.attributedText = value
        return view
    }

    func updateUIView(_ view: UITextView, context: Context) {
        // Apply only an actual model change. Avoid resetting selection on every
        // SwiftUI update and respect the incoming transaction when needed.
        if !view.attributedText.isEqual(value) {
            view.attributedText = value
        }
    }

    func makeCoordinator() -> Coordinator {
        Coordinator(owner: self)
    }

    final class Coordinator: NSObject, UITextViewDelegate {
        var owner: RichTextEditor

        init(owner: RichTextEditor) {
            self.owner = owner
        }

        func textViewDidChange(_ textView: UITextView) {
            owner.value = textView.attributedText
        }
    }
}
~~~

In a production bridge, make the coordinator's ownership and update policy
explicit. Avoid a stale copy of the Binding, preserve selection intentionally,
and use dismantleUIView when the feature owns tasks, observers, or model work.

## 8. Represent a bounded AI review mark

Keep proposal identity, source revision, and validation state in the domain.
Use a SwiftUI TextAttribute only for a visual hint that remains subordinate to
the review controls.

~~~swift
import SwiftUI

struct ReviewMark: TextAttribute, Hashable {
    let proposalID: UUID
    let isReplacement: Bool
}

struct ReviewLabel: View {
    let proposalID: UUID

    var body: some View {
        Text("Suggested edit")
            .customAttribute(
                ReviewMark(
                    proposalID: proposalID,
                    isReplacement: true
                )
            )
            .accessibilityLabel("Suggested edit")
    }
}
~~~

For a per-span rich document, use the current AttributedString formatting
definition or an explicit split into Text runs so the attribute maps to the
intended source. The custom mark does not accept or commit the edit. A real
semantic button or sheet must own that action.

## 9. Guard a proposal before applying it

The renderer should receive already-validated proposals. Keep the stale-result
check in the domain or feature actor.

~~~swift
struct TextProposal: Sendable, Hashable {
    let documentID: UUID
    let sourceRevision: Int
    let sourceTextHash: String
    let replacement: String
    let sourceRange: NSRange
}

struct DocumentSnapshot: Sendable {
    let documentID: UUID
    let revision: Int
    let textHash: String
}

func canReview(
    _ proposal: TextProposal,
    against snapshot: DocumentSnapshot
) -> Bool {
    proposal.documentID == snapshot.documentID
        && proposal.sourceRevision == snapshot.revision
        && proposal.sourceTextHash == snapshot.textHash
        && proposal.sourceRange.location >= 0
}
~~~

The actual validator must also check range length, document bounds, replacement
limits, user policy, cancellation, and any domain-specific content rules.

## 10. Compile and verification checklist

- Compile the smallest editor target with the iOS 26 SDK.
- Check TextKit 2 availability warnings and deployment branches.
- Test editing transactions and selection preservation.
- Test Dynamic Type, RTL, localization, VoiceOver, keyboard, pointer, and
  reduced-effects settings.
- Test long documents, viewport scroll, attachments, rapid edits, cancellation,
  and memory/energy behavior on device.
- Test model unavailable, stale, malformed, rejected, edited, and accepted
  proposal paths.
- Inspect a signed archive for fonts, resources, target membership, privacy
  configuration, and debug-only fixtures.

## Related routes

- [TextKit 2 and Core Text layout](../42-framework-deep-dives/57-textkit-2-and-core-text-layout.md)
- [Native typography and rich-editor design](../21-design-deep-dives/77-native-typography-and-rich-editor-design.md)
- [TextKit 2 rich-editor and AI annotation route](../50-capability-recipes/80-textkit-2-rich-editor-and-ai-annotation-route.md)
- [TextKit 2 typography proof matrix](../60-verification/74-textkit-2-typography-proof-matrix.md)
- [Rich text and custom TextRenderer routes](../10-swiftui/10-rich-text-and-text-renderers.md)

## Sources

- [UITextView](https://developer.apple.com/documentation/uikit/uitextview)
- [NSTextContentManager](https://developer.apple.com/documentation/uikit/nstextcontentmanager)
- [NSTextContentStorage](https://developer.apple.com/documentation/uikit/nstextcontentstorage)
- [NSTextLayoutManager](https://developer.apple.com/documentation/uikit/nstextlayoutmanager)
- [NSTextLayoutFragment](https://developer.apple.com/documentation/uikit/nstextlayoutfragment)
- [NSTextLineFragment](https://developer.apple.com/documentation/uikit/nstextlinefragment)
- [NSTextViewportLayoutController](https://developer.apple.com/documentation/uikit/nstextviewportlayoutcontroller)
- [NSTextViewportLayoutControllerDelegate](https://developer.apple.com/documentation/uikit/nstextviewportlayoutcontrollerdelegate)
- [NSTextSelection](https://developer.apple.com/documentation/uikit/nstextselection)
- [Using TextKit 2 to interact with text](https://developer.apple.com/documentation/uikit/using-textkit-2-to-interact-with-text)
- [Core Text](https://developer.apple.com/documentation/coretext)
- [CTFramesetter](https://developer.apple.com/documentation/coretext/ctframesetter)
- [CTFrame](https://developer.apple.com/documentation/coretext/ctframe)
- [CTLine](https://developer.apple.com/documentation/coretext/ctline)
- [CTFont](https://developer.apple.com/documentation/coretext/ctfont)
- [SwiftUI text input and output](https://developer.apple.com/documentation/swiftui/text-input-and-output)
- [TextRenderer](https://developer.apple.com/documentation/swiftui/textrenderer)
- [TextAttribute](https://developer.apple.com/documentation/swiftui/textattribute)
- [Text customAttribute](https://developer.apple.com/documentation/swiftui/text/customattribute%28_%3A%29)
- [AttributedString](https://developer.apple.com/documentation/foundation/attributedstring)
- [Typography HIG](https://developer.apple.com/design/human-interface-guidelines/typography)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
