# PencilKit and handwriting-intelligence code recipes

These recipes are compile-oriented sketches for a named UIKit or SwiftUI target. PencilKit’s canvas, tool picker, handwriting recognizer, and newer stroke-rendering APIs are platform and SDK sensitive. A recipe is not proof of Apple Pencil latency, handwriting quality, accessibility, or release behavior.

## Recipe 1: UIKit canvas with a stable document boundary

Keep PKCanvasView inside a document controller or SwiftUI representable, not inside a transient button action.

~~~swift
import PencilKit
import UIKit

final class DrawingViewController: UIViewController, PKCanvasViewDelegate {
    let canvasView = PKCanvasView()
    private var saveTask: Task<Void, Never>?

    override func viewDidLoad() {
        super.viewDidLoad()
        canvasView.delegate = self
        canvasView.drawingPolicy = .default
        canvasView.backgroundColor = .systemBackground
        canvasView.alwaysBounceVertical = true
        canvasView.translatesAutoresizingMaskIntoConstraints = false

        view.addSubview(canvasView)
        NSLayoutConstraint.activate([
            canvasView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            canvasView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            canvasView.topAnchor.constraint(equalTo: view.topAnchor),
            canvasView.bottomAnchor.constraint(equalTo: view.bottomAnchor)
        ])
    }

    func canvasViewDrawingDidChange(_ canvasView: PKCanvasView) {
        scheduleSave(canvasView.drawing)
    }

    func canvasViewDidEndUsingTool(_ canvasView: PKCanvasView) {
        scheduleSave(canvasView.drawing)
    }

    private func scheduleSave(_ drawing: PKDrawing) {
        saveTask?.cancel()
        saveTask = Task { [weak self] in
            try? await Task.sleep(for: .milliseconds(250))
            guard !Task.isCancelled else { return }
            let data = drawing.dataRepresentation()
            await self?.persist(data: data)
        }
    }

    private func persist(data: Data) async {
        // Write atomically through the document store.
    }
}
~~~

For a real app, isolate the document ID, revision, and storage actor. Do not retain a UIKit controller merely to keep a drawing alive if the document is closed.

## Recipe 2: SwiftUI UIViewRepresentable bridge

Use a coordinator to translate UIKit callbacks into a deliberate SwiftUI data boundary.

~~~swift
import PencilKit
import SwiftUI

struct CanvasRepresentable: UIViewRepresentable {
    @Binding var drawing: PKDrawing
    var policy: PKCanvasViewDrawingPolicy

    func makeCoordinator() -> Coordinator {
        Coordinator(owner: self)
    }

    func makeUIView(context: Context) -> PKCanvasView {
        let canvas = PKCanvasView()
        canvas.drawing = drawing
        canvas.drawingPolicy = policy
        canvas.delegate = context.coordinator
        context.coordinator.canvas = canvas
        return canvas
    }

    func updateUIView(_ canvas: PKCanvasView, context: Context) {
        canvas.drawingPolicy = policy
        if canvas.drawing.dataRepresentation() != drawing.dataRepresentation() {
            canvas.drawing = drawing
        }
    }

    final class Coordinator: NSObject, PKCanvasViewDelegate {
        var owner: CanvasRepresentable
        weak var canvas: PKCanvasView?

        init(owner: CanvasRepresentable) {
            self.owner = owner
        }

        func canvasViewDrawingDidChange(_ canvasView: PKCanvasView) {
            owner.drawing = canvasView.drawing
        }
    }
}
~~~

For large drawings, compare a revision or hash maintained by the document layer instead of repeatedly comparing full data representations. Test for update loops and delegate lifetime.

## Recipe 3: attach the system tool picker

The picker is coordinated with first responder and window lifecycle.

~~~swift
import PencilKit
import UIKit

final class ToolPickerCoordinator {
    private let picker = PKToolPicker()

    func attach(to canvas: PKCanvasView) {
        picker.addObserver(canvas)
        picker.setVisible(true, forFirstResponder: canvas)
        canvas.becomeFirstResponder()
    }

    func detach(from canvas: PKCanvasView) {
        picker.setVisible(false, forFirstResponder: canvas)
        picker.removeObserver(canvas)
    }
}
~~~

Keep the coordinator alive while the canvas is active. Test multiple windows separately. Mac Catalyst needs a different toolbar/menu route because the documented PencilKit tool picker does not display there.

## Recipe 4: choose a drawing policy

~~~swift
import PencilKit

func applyInputPolicy(
    _ policy: PKCanvasViewDrawingPolicy,
    to canvas: PKCanvasView
) {
    canvas.drawingPolicy = policy
}

func policyForProduct(
    wantsFingerInk: Bool,
    requiresPencilPrecision: Bool
) -> PKCanvasViewDrawingPolicy {
    if requiresPencilPrecision {
        return .pencilOnly
    }
    if wantsFingerInk {
        return .anyInput
    }
    return .default
}
~~~

The policy is a UX decision. Pair it with a pan/selection route and an alternate input path rather than assuming every user has Apple Pencil.

## Recipe 5: persist and restore the drawing

~~~swift
import PencilKit

struct StoredDrawing: Codable, Sendable {
    let documentID: String
    let data: Data
    let revision: Int
    let requiredContentVersion: String
}

func storedDrawing(
    id: String,
    drawing: PKDrawing,
    revision: Int
) -> StoredDrawing {
    StoredDrawing(
        documentID: id,
        data: drawing.dataRepresentation(),
        revision: revision,
        requiredContentVersion: String(describing: drawing.requiredContentVersion)
    )
}

func loadDrawing(_ stored: StoredDrawing) throws -> PKDrawing {
    try PKDrawing(data: stored.data)
}
~~~

The required content version is a compatibility signal, not a migration engine. Check it against the target’s maximum supported content version before opening imported content. Keep a last-good copy when writes can be interrupted.

## Recipe 6: recognize selected strokes

Keep the recognizer as an actor and update its drawing before every result request that depends on a newer revision.

~~~swift
import PencilKit

actor DrawingRecognizer {
    private let recognizer: PKStrokeRecognizer
    private var revision: Int = 0

    init(languages: [Locale.Language]?) {
        recognizer = PKStrokeRecognizer(preferredLanguages: languages)
    }

    func update(drawing: PKDrawing, revision: Int) async {
        guard revision >= self.revision else { return }
        self.revision = revision
        await recognizer.updateDrawing(drawing)
    }

    func selectedText(
        strokeIDs: Set<UUID>?,
        revision: Int
    ) async -> String? {
        guard revision == self.revision else { return nil }
        return await recognizer.recognizedText(strokeIDs: strokeIDs)
    }
}
~~~

The recognizer can return nil. Treat it as a normal result and preserve the drawing. Do not run recognition against a stale drawing because a previous result happened to be non-nil.

## Recipe 7: language support and versioned results

~~~swift
import PencilKit

struct PersistedRecognition: Codable, Sendable {
    let text: String
    let recognitionVersion: Int
    let languageIdentifiers: [String]
}

func supported(
    _ requested: [Locale.Language]
) -> [Locale.Language] {
    let available = PKStrokeRecognizer.supportedLanguages
    return requested.filter(available.contains)
}

func shouldRegenerate(_ result: PersistedRecognition) -> Bool {
    result.recognitionVersion < PKStrokeRecognizer.recognitionVersion
}
~~~

Recognition output can change across OS releases. Store the engine version with derived text and regenerate rather than silently treating old output as permanent truth.

## Recipe 8: search inside a drawing

~~~swift
import PencilKit

struct DrawingSearchHit: Sendable {
    let strokeIDs: Set<UUID>
    let bounds: CGRect
}

func searchDrawing(
    recognizer: PKStrokeRecognizer,
    query: String
) async -> [DrawingSearchHit] {
    let results = await recognizer.search(
        query,
        fullWordsOnly: true,
        caseMatchingOnly: false
    )
    return results.map {
        DrawingSearchHit(
            strokeIDs: $0.strokeIDs,
            bounds: $0.bounds
        )
    }
}
~~~

Use each result’s bounds to scroll or highlight the source drawing. Do not replace the drawing with a text-only search screen when the source ink is important to the user.

## Recipe 9: index handwriting as a projection

The indexableContent route is for search recall, not user-facing prose.

~~~swift
import CoreSpotlight
import PencilKit
import UniformTypeIdentifiers

func makeSearchItem(
    id: String,
    recognizer: PKStrokeRecognizer,
    title: String
) async -> CSSearchableItem? {
    guard let content = await recognizer.indexableContent else {
        return nil
    }

    let attributes = CSSearchableItemAttributeSet(
        contentType: UTType.text.identifier
    )
    attributes.title = title
    attributes.textContent = content

    return CSSearchableItem(
        uniqueIdentifier: id,
        domainIdentifier: "handwritten-notes",
        attributeSet: attributes
    )
}
~~~

Index only what the person or product has authorized as searchable. Update and delete with the drawing record. Keep a stable ID that can route a search result back to the source document.

## Recipe 10: preserve render state for a substroke

Use current/Beta APIs only behind a target availability decision.

~~~swift
import PencilKit

func reveal(_ stroke: PKStroke, progress: CGFloat) -> PKStroke {
    let bounded = min(max(progress, 0), 1)
    let last = CGFloat(max(stroke.path.count - 1, 0))
    return stroke.substroke(range: 0...(last * bounded))
}

func animatedDrawing(
    _ drawing: PKDrawing,
    progress: CGFloat
) -> PKDrawing {
    PKDrawing(strokes: drawing.strokes.map {
        reveal($0, progress: progress)
    })
}
~~~

Substroke is preferable to rebuilding only the path when the product needs the original ink appearance. Test renderState, grain, and renderGroupID behavior on the target SDK and physical device before relying on it for export or playback.

## Recipe 11: typed handwriting review proposal

~~~swift
struct HandwritingReview: Sendable {
    let drawingID: String
    let drawingRevision: Int
    let strokeIDs: Set<UUID>
    let recognizedText: String
    let correctedText: String
    let recognitionVersion: Int
}

struct ActionProposal: Sendable {
    let source: HandwritingReview
    let summary: String
    let requiresApproval: Bool
}
~~~

The proposal should show source strokes, recognized text, corrections, and the action scope. Use correctedText as model context when possible; do not send raw indexableContent for a side effect.

## Recipe 12: deterministic apply gate

~~~swift
enum ApplyDecision: Sendable {
    case blocked(String)
    case ready
}

func canApply(
    review: HandwritingReview,
    currentDrawingRevision: Int,
    userApproved: Bool,
    domainStateAllowsAction: Bool
) -> ApplyDecision {
    guard review.drawingRevision == currentDrawingRevision else {
        return .blocked("The source drawing changed.")
    }
    guard !review.correctedText.isEmpty else {
        return .blocked("There is no corrected text.")
    }
    guard userApproved else {
        return .blocked("Approval is required.")
    }
    guard domainStateAllowsAction else {
        return .blocked("The current domain state does not allow this action.")
    }
    return .ready
}
~~~

The model never calls the domain write directly. Re-read the drawing revision and domain state at apply time.

## Recipe 13: drawing and recognition test fixtures

~~~text
fixtures:
  empty_drawing:
    expected: nil recognition, no index item
  selected_word:
    expected: selected stroke IDs only
  changed_after_request:
    expected: old result discarded
  unsupported_language:
    expected: language omitted or typed fallback
  large_zoom:
    expected: quality note, no universal accuracy claim
  recognition_version_changed:
    expected: derived text regenerated
  delete_source:
    expected: drawing and Spotlight projection removed
  model_proposal:
    expected: source-linked review and explicit approval
~~~

## Recipe 14: physical-device handoff

Before shipping a PencilKit feature, capture:

- target SDK and deployment target;
- iPad/iPhone and Apple Pencil model;
- tool picker and input policy;
- drawing save/reopen;
- language support and recognition version;
- handwriting fixtures at the chosen scale;
- VoiceOver and alternate-input results;
- Spotlight update/delete if used;
- AI proposal and correction trace if used;
- signed release artifact and actual destination evidence.

## Sources

- [PencilKit](https://developer.apple.com/documentation/pencilkit)
- [PKCanvasView](https://developer.apple.com/documentation/pencilkit/pkcanvasview?language=objc%3A)
- [PKCanvasViewDelegate](https://developer.apple.com/documentation/pencilkit/pkcanvasviewdelegate)
- [PKCanvasViewDrawingPolicy](https://developer.apple.com/documentation/pencilkit/pkcanvasviewdrawingpolicy)
- [PKDrawing](https://developer.apple.com/documentation/pencilkit/pkdrawing-swift.struct?language=objc)
- [PKToolPicker](https://developer.apple.com/documentation/pencilkit/pktoolpicker?changes=_1)
- [Configuring the PencilKit tool picker](https://developer.apple.com/documentation/pencilkit/configuring-the-pencilkit-tool-picker)
- [PKStroke](https://developer.apple.com/documentation/pencilkit/pkstroke-swift.struct?changes=_3)
- [PKStrokeRecognizer](https://developer.apple.com/documentation/pencilkit/pkstrokerecognizer?changes=_1)
- [Recognizing handwriting and converting it to text](https://developer.apple.com/documentation/pencilkit/recognizing-handwriting-and-converting-to-text?changes=_1)
- [Building a handwriting recognition experience with PencilKit](https://developer.apple.com/documentation/pencilkit/building-a-handwriting-recognition-experience-with-pencilkit?changes=latest_bet___5&language=objc)
- [Controlling stroke rendering for animation and editing](https://developer.apple.com/documentation/pencilkit/controlling-stroke-rendering-for-animation-and-editing?changes=latest_minor%2Clatest_minor)
- [Core Spotlight](https://developer.apple.com/documentation/corespotlight)
- [Apple Pencil and Scribble](https://developer.apple.com/design/human-interface-guidelines/apple-pencil-and-scribble)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Swift concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
