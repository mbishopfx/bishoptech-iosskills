# PencilKit handwriting-intelligence capability route

Use this route when the product needs expressive Apple Pencil input, editable ink, handwriting search, or a reviewable drawing-to-text workflow.

~~~text
PencilKit target
-> PKCanvasView input policy
-> PKDrawing persistence
-> optional PKStroke / PKStrokePath analysis
-> optional PKStrokeRecognizer
-> corrected text
-> Spotlight/search or bounded AI proposal
-> explicit domain commit
~~~

## Route selector

| Product need | Route | Boundary |
| --- | --- | --- |
| Freehand drawing or notes | PKCanvasView + PKDrawing | Ink is source content; domain meaning is separate |
| Annotated document | PaperKit + PencilKit | Structured markup and ink have separate models |
| Write into a custom field | Scribble interaction | Input behavior and text editing remain app-owned |
| Copy handwritten selection as text | PKStrokeRecognizer.recognizedText | Result is a proposal that can be nil or wrong |
| Search within a drawing | PKStrokeRecognizer.search | Highlight returned stroke IDs/bounds; do not replace source ink |
| Make handwriting searchable | PKStrokeRecognizer.indexableContent + Core Spotlight | Indexable content is a search projection with alternate readings |
| Summarize or classify corrected notes | Foundation Models, Natural Language, or a domain model | Model output needs source, review, and deterministic validation |

## Ownership graph

~~~text
SwiftUI shell
  -> UIViewRepresentable
  -> UIKit PKCanvasView + PKToolPicker
  -> PKDrawing / document store
  -> PKStrokeRecognizer actor
  -> recognized/corrected text
  -> Core Spotlight or model context
  -> review surface
  -> deterministic domain write
~~~

Do not persist only the recognized text when the drawing is the user’s source. Keep the drawing, recognition metadata, correction, and derived projection independently versioned.

## Target and module setup

The owning app target normally needs:

- PencilKit;
- UIKit for PKCanvasView and PKToolPicker;
- SwiftUI if the app shell is SwiftUI;
- Core Spotlight only if handwriting search/indexing is included;
- the selected persistence and export route;
- the current SDK availability register for PKStrokeRecognizer and newer stroke rendering APIs.

No protected-data permission is required merely to capture Pencil input, but handwritten content can be sensitive. Put retention, export, search indexing, sync, and model-context policies in the product privacy review.

If using the current handwriting recognizer, record:

- target deployment and SDK;
- whether the API is Beta-marked in the selected SDK;
- supported language set;
- recognitionVersion;
- physical Pencil/iPad test devices;
- drawing scale and page coordinate policy;
- regeneration policy when recognitionVersion changes.

## Canvas configuration

Choose the policy before creating the canvas:

~~~swift
import PencilKit

func configureCanvas(_ canvas: PKCanvasView) {
    canvas.drawingPolicy = .default
    canvas.alwaysBounceVertical = true
    canvas.alwaysBounceHorizontal = false
    canvas.backgroundColor = .systemBackground
    canvas.isOpaque = true
}
~~~

The final target should choose scrolling, zooming, background, input policy, and first-responder behavior intentionally. A drawing app may use anyInput; a precision annotation app may use pencilOnly and provide explicit touch selection.

## SwiftUI bridge boundary

Wrap the canvas rather than turning each stroke callback into a SwiftUI state update.

~~~swift
import PencilKit
import SwiftUI

struct PencilCanvas: UIViewRepresentable {
    @Binding var drawing: PKDrawing
    var drawingPolicy: PKCanvasViewDrawingPolicy = .default

    func makeCoordinator() -> Coordinator {
        Coordinator(owner: self)
    }

    func makeUIView(context: Context) -> PKCanvasView {
        let canvas = PKCanvasView()
        canvas.drawing = drawing
        canvas.drawingPolicy = drawingPolicy
        canvas.delegate = context.coordinator
        context.coordinator.canvas = canvas
        return canvas
    }

    func updateUIView(_ canvas: PKCanvasView, context: Context) {
        if canvas.drawing.dataRepresentation() != drawing.dataRepresentation() {
            canvas.drawing = drawing
        }
        canvas.drawingPolicy = drawingPolicy
    }

    final class Coordinator: NSObject, PKCanvasViewDelegate {
        var owner: PencilCanvas
        weak var canvas: PKCanvasView?

        init(owner: PencilCanvas) {
            self.owner = owner
        }

        func canvasViewDrawingDidChange(_ canvasView: PKCanvasView) {
            owner.drawing = canvasView.drawing
        }
    }
}
~~~

Comparing raw data on every update can be expensive for a large drawing. Use a document revision or coordinator ownership policy in a real app. The bridge is a route sketch and should be tested for feedback loops, delegate lifetime, rendering, and SwiftUI update frequency.

## Persistence route

Persist the editable drawing data separately from a preview.

~~~swift
import PencilKit

struct DrawingArchive: Codable, Sendable {
    let drawingData: Data
    let recognitionVersion: Int?
    let pageScale: Double
    let updatedAt: Date
}

func archive(_ drawing: PKDrawing, recognizerVersion: Int?) -> DrawingArchive {
    DrawingArchive(
        drawingData: drawing.dataRepresentation(),
        recognitionVersion: recognizerVersion,
        pageScale: 1.0,
        updatedAt: Date()
    )
}

func restore(_ archive: DrawingArchive) throws -> PKDrawing {
    try PKDrawing(data: archive.drawingData)
}
~~~

Use atomic file writes or a transaction/asset store suited to the target. The preview image can be regenerated; the drawing data is the editable source. Record a format/schema policy when synchronizing or exporting drawings.

## Tool picker attachment

The system tool picker is first-responder driven.

~~~swift
import PencilKit
import UIKit

func attachToolPicker(
    _ toolPicker: PKToolPicker,
    to canvas: PKCanvasView
) {
    toolPicker.addObserver(canvas)
    toolPicker.setVisible(true, forFirstResponder: canvas)
    canvas.becomeFirstResponder()
}

func detachToolPicker(
    _ toolPicker: PKToolPicker,
    from canvas: PKCanvasView
) {
    toolPicker.setVisible(false, forFirstResponder: canvas)
    toolPicker.removeObserver(canvas)
}
~~~

The tool picker does not display in Mac Catalyst according to Apple’s documentation. Provide a target-specific pointer/keyboard toolbar or menu when needed.

## Delegate and save debounce

Drawing callbacks can be frequent. Use end-of-tool boundaries or a debounced revision to save and schedule recognition.

~~~swift
import PencilKit

final class CanvasDelegate: NSObject, PKCanvasViewDelegate {
    var onStableDrawing: ((PKDrawing) -> Void)?
    private var pendingTask: Task<Void, Never>?

    func canvasViewDrawingDidChange(_ canvasView: PKCanvasView) {
        pendingTask?.cancel()
        let drawing = canvasView.drawing
        pendingTask = Task { [weak self] in
            try? await Task.sleep(for: .milliseconds(250))
            guard !Task.isCancelled else { return }
            self?.onStableDrawing?(drawing)
        }
    }

    func canvasViewDidEndUsingTool(_ canvasView: PKCanvasView) {
        onStableDrawing?(canvasView.drawing)
    }
}
~~~

For a document editor, add a generation number so a delayed save or recognition result cannot overwrite a newer drawing. Cancel the task when the document closes.

## On-device handwriting recognition

PKStrokeRecognizer is an actor. Keep one recognizer per open drawing, update it explicitly, and use the language register before offering choices.

~~~swift
import PencilKit

actor HandwritingService {
    private let recognizer: PKStrokeRecognizer

    init(preferredLanguages: [Locale.Language]?) {
        recognizer = PKStrokeRecognizer(preferredLanguages: preferredLanguages)
    }

    func update(with drawing: PKDrawing) async {
        await recognizer.updateDrawing(drawing)
    }

    func recognize(strokeIDs: Set<UUID>? = nil) async -> String? {
        await recognizer.recognizedText(strokeIDs: strokeIDs)
    }

    func search(
        _ query: String,
        fullWordsOnly: Bool = false,
        caseMatchingOnly: Bool = false
    ) async -> [PKStrokeRecognizer.SearchResult] {
        await recognizer.search(
            query,
            fullWordsOnly: fullWordsOnly,
            caseMatchingOnly: caseMatchingOnly
        )
    }
}
~~~

Call updateDrawing before recognizedText or search. Cancel or supersede a recognition task when a newer drawing revision is available.

## Language and result policy

~~~swift
import PencilKit

struct HandwritingLanguagePolicy: Sendable {
    let requested: [Locale.Language]
    let supported: Set<Locale.Language>

    var availableRequested: [Locale.Language] {
        requested.filter { supported.contains($0) }
    }
}

func handwritingPolicy() -> HandwritingLanguagePolicy {
    HandwritingLanguagePolicy(
        requested: [
            Locale.Language(identifier: "en"),
            Locale.Language(identifier: "es")
        ],
        supported: PKStrokeRecognizer.supportedLanguages
    )
}
~~~

Treat nil recognizedText as a normal result. Do not create a fake confidence number when the API does not return one. Store recognitionVersion when persisting a result and re-run recognition after the engine version changes.

## Search and Spotlight projection

Use search results to highlight source strokes and indexableContent to improve retrieval.

~~~swift
import CoreSpotlight
import PencilKit
import UniformTypeIdentifiers

func searchableItem(
    drawingID: String,
    recognizer: PKStrokeRecognizer,
    content: String
) -> CSSearchableItem {
    let attributes = CSSearchableItemAttributeSet(contentType: UTType.text.identifier)
    attributes.title = "Handwritten Note"
    attributes.textContent = content
    return CSSearchableItem(
        uniqueIdentifier: drawingID,
        domainIdentifier: "handwritten-notes",
        attributeSet: attributes
    )
}
~~~

The recognizer’s indexableContent is a search projection and may include alternate readings. Do not show it as the user’s final corrected text. Index only records the person has authorized as searchable, and delete or update the item when the drawing changes or is removed.

## Stroke inspection and animation

Use stable stroke IDs and render-aware APIs for playback or editing.

~~~swift
import PencilKit

func partialStroke(_ stroke: PKStroke, progress: CGFloat) -> PKStroke {
    let end = CGFloat(max(stroke.path.count - 1, 0)) * min(max(progress, 0), 1)
    return stroke.substroke(range: 0...end)
}

func playbackDrawing(
    _ drawing: PKDrawing,
    progress: CGFloat
) -> PKDrawing {
    let strokes = drawing.strokes.map {
        partialStroke($0, progress: progress)
    }
    return PKDrawing(strokes: strokes)
}
~~~

Substroke and render-state APIs are current/Beta-sensitive. Preserve render state when modifying a stroke if visual fidelity matters, and test marker/wet-ink behavior on a physical device. Do not use a playback animation as a shortcut for input latency proof.

## AI review route

Use a typed proposal that points back to source strokes:

~~~swift
struct HandwritingProposal: Sendable {
    let drawingID: String
    let strokeIDs: Set<UUID>
    let recognizedText: String
    let correctedText: String
    let proposal: String
    let recognitionVersion: Int
    let requiresApproval: Bool
}
~~~

Policy:

1. Show the selected source strokes.
2. Show recognized text and allow correction.
3. Provide corrected text, not raw indexable content, to the model when possible.
4. Keep model output in a proposal state.
5. Validate against current domain state.
6. Require approval before writing, sharing, sending, or scheduling.
7. Store provenance so the person can return to the strokes.

## Fallbacks

| Condition | Fallback |
| --- | --- |
| no Pencil | Finger, pointer, keyboard, Scribble, or typed entry |
| language unsupported | Choose another supported language or type |
| recognition unavailable/Beta removed | Keep the drawing editable and disable derived actions |
| nil result | Select clearer strokes, zoom, or type |
| stale result | Re-run after updateDrawing |
| recognizer version changed | Regenerate persisted derived text |
| large drawing | Recognize selection or a bounded region |
| model unavailable | Use corrected text and deterministic app logic |

## Verification handoff

Capture the target SDK, device/Pencil model, drawing scale, input policy, supported languages, recognition version, save/reopen evidence, recognition fixtures, Spotlight lifecycle, accessibility settings, and release build. Use the [PencilKit proof matrix](../60-verification/50-pencilkit-handwriting-proof-matrix.md) when validating the route.

## Sources

- [PencilKit](https://developer.apple.com/documentation/pencilkit)
- [PKCanvasView](https://developer.apple.com/documentation/pencilkit/pkcanvasview?language=objc%3A)
- [PKCanvasViewDelegate](https://developer.apple.com/documentation/pencilkit/pkcanvasviewdelegate)
- [PKCanvasViewDrawingPolicy](https://developer.apple.com/documentation/pencilkit/pkcanvasviewdrawingpolicy)
- [PKDrawing](https://developer.apple.com/documentation/pencilkit/pkdrawing-swift.struct?language=objc)
- [PKToolPicker](https://developer.apple.com/documentation/pencilkit/pktoolpicker?changes=_1)
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
