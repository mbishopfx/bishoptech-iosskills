# PaperKit and markup recipes

These are compile-oriented route sketches for PaperKit, PencilKit, UIKit, and SwiftUI. They are not claimed to compile in this documentation workspace. PaperKit has beta-marked/current-SDK-sensitive symbols, so confirm imports, availability, MainActor isolation, feature-set signatures, and target membership in Xcode.

Every recipe assumes:

- the app target links PaperKit and PencilKit;
- the selected platform supports the controller route;
- the document has an app-owned id, source revision, bounds, and FeatureSet policy;
- the app separates PaperMarkup from the live controller;
- AI output is a proposal until the user confirms Apply;
- saves and renders are cancellable and recoverable.

## Recipe 1: create a PaperMarkup model

Create a model with the source document’s coordinate bounds:

~~~swift
import CoreGraphics
import PaperKit

let paper = PaperMarkup(
    bounds: CGRect(x: 0, y: 0, width: 1_024, height: 1_400)
)

let featureSet = FeatureSet.version1
~~~

Use FeatureSet.latest only when the document envelope and every target can persist and render all enabled features. Store the selected content version outside the model so migrations remain explicit.

## Recipe 2: create the UIKit controller

Create the view controller on the MainActor and pass the same compatible feature set used by the model and tool UI:

~~~swift
@MainActor
func makePaperViewController(
    paper: PaperMarkup,
    featureSet: FeatureSet
) -> PaperMarkupViewController {
    let controller = PaperMarkupViewController(
        markup: paper,
        supportedFeatureSet: featureSet
    )
    controller.isEditable = true
    controller.zoomRange = 0.5...4.0
    return controller
}
~~~

The exact zoom and edit defaults are product-specific. Do not set isEditable from a visual mode without also changing the app-owned command policy.

## Recipe 3: bridge the controller into SwiftUI

Use UIViewControllerRepresentable as the lifecycle boundary:

~~~swift
import PaperKit
import SwiftUI

struct PaperCanvasView: UIViewControllerRepresentable {
    let paper: PaperMarkup
    let featureSet: FeatureSet
    let isEditable: Bool

    func makeUIViewController(
        context: Context
    ) -> PaperMarkupViewController {
        let controller = PaperMarkupViewController(
            markup: paper,
            supportedFeatureSet: featureSet
        )
        controller.isEditable = isEditable
        controller.delegate = context.coordinator
        return controller
    }

    func updateUIViewController(
        _ controller: PaperMarkupViewController,
        context: Context
    ) {
        controller.isEditable = isEditable
        if controller.markup?.id != paper.id {
            controller.markup = paper
        }
    }

    func dismantleUIViewController(
        _ controller: PaperMarkupViewController,
        coordinator: Coordinator
    ) {
        coordinator.cancelTasks()
        controller.delegate = nil
    }

    func makeCoordinator() -> Coordinator {
        Coordinator()
    }

    final class Coordinator: NSObject,
        PaperMarkupViewController.Delegate {
        func cancelTasks() {
            // Cancel observation/render/save tasks owned by the adapter.
        }
    }
}
~~~

The delegate protocol has additional SDK-specific requirements. Add them from Xcode rather than assuming this minimal sketch is complete. Most importantly, do not instantiate a new PaperMarkupViewController from every body evaluation.

## Recipe 4: present the native markup tools

On iOS-family targets, MarkupEditViewController provides the insertion/configuration palette:

~~~swift
@MainActor
func makeMarkupEditor(
    featureSet: FeatureSet
) -> MarkupEditViewController {
    let editor = MarkupEditViewController(
        supportedFeatureSet: featureSet,
        additionalActions: []
    )
    editor.modalPresentationStyle = .popover
    return editor
}
~~~

Present the controller from a user-visible Add Markup action. On macOS, use MarkupToolbarViewController and set its delegate to the PaperMarkupViewController. Keep the same feature-set policy across all controllers.

## Recipe 5: insert a shape

Insert only after validating bounds and feature support:

~~~swift
let shape = ShapeConfiguration(
    type: .rectangle,
    fillColor: CGColor(gray: 0.95, alpha: 1.0),
    strokeColor: CGColor(gray: 0.2, alpha: 1.0),
    lineWidth: 2
)

paper.insertNewShape(
    configuration: shape,
    frame: CGRect(x: 120, y: 180, width: 300, height: 160),
    rotation: 0
)
~~~

Confirm the current ShapeConfiguration.Shape case names in the selected SDK. A model should propose a bounded semantic shape, not arbitrary raw drawing commands.

## Recipe 6: insert a text box

Use AttributedString for a structured text element:

~~~swift
var text = AttributedString("Review this region")
text.font = .systemFont(ofSize: 24, weight: .semibold)
text.foregroundColor = .black

paper.insertNewTextbox(
    attributedText: text,
    frame: CGRect(x: 140, y: 380, width: 420, height: 80),
    rotation: 0
)
~~~

The exact AttributedString attribute types and PaperKit text-box behavior should be checked in the selected SDK. Keep long localized content in the review UI before committing it to a bounded text box.

## Recipe 7: add an image or line

PaperMarkup supports image and line insertion:

~~~swift
paper.insertNewImage(
    approvedImage,
    frame: imageFrame,
    rotation: imageRotation
)

paper.insertNewLine(
    configuration: lineConfiguration,
    from: startPoint,
    to: endPoint,
    startMarker: false,
    endMarker: true
)
~~~

Image insertion must retain source provenance and orientation. Line markers should be part of a user-visible design decision, not an arbitrary model parameter.

## Recipe 8: restrict interactions

Make a document or proposed element read-only while the person reviews it:

~~~swift
for element in paper.subelements {
    element.allowedInteractions = .readOnly
}
~~~

The exact mutable element protocol surface may require editing the element value returned by the selected SDK’s ordered set. The documented policy is the important part: use MarkupInteractions.readOnly or subtract delete/style/rotate/resize/move where the product requires it.

## Recipe 9: save and load the model

Persist the serialized model asynchronously:

~~~swift
func save(
    paper: PaperMarkup,
    to url: URL
) async throws {
    let data = try await paper.dataRepresentation()
    try data.write(to: url, options: [.atomic])
}

func load(
    from url: URL
) throws -> PaperMarkup {
    let data = try Data(contentsOf: url)
    return try PaperMarkup(dataRepresentation: data)
}
~~~

Wrap the payload in an app-owned envelope containing source id, source revision, FeatureSet/content version, schema version, and last-saved timestamp. If the write fails, retain the last-good file and show a recoverable save state.

## Recipe 10: coalesce model-change saves

PaperMarkupViewController exposes the markup model as observable state. Use an observation/task boundary rather than saving every pointer event synchronously:

~~~swift
import Observation

@MainActor
final class PaperDocumentStore {
    private var saveTask: Task<Void, Never>?

    func scheduleSave(
        paper: PaperMarkup,
        url: URL
    ) {
        saveTask?.cancel()
        saveTask = Task {
            do {
                try await Task.sleep(for: .milliseconds(250))
                let data = try await paper.dataRepresentation()
                try Task.checkCancellation()
                try data.write(to: url, options: [.atomic])
            } catch is CancellationError {
                return
            } catch {
                // Publish a recoverable save-failed state.
            }
        }
    }

    func cancel() {
        saveTask?.cancel()
        saveTask = nil
    }
}
~~~

This is a route sketch. Match the task isolation and clock API to the selected deployment target. The save task must capture the model/version it intends to write and must not report Saved for a stale representation.

## Recipe 11: observe PaperMarkup changes

The PaperMarkupViewController documentation shows observation of its markup property. A simplified route is:

~~~swift
let changes = Observations.untilFinished { [weak paperViewController] in
    guard let markup = paperViewController?.markup else {
        return .finish
    }
    return .next(markup)
}

let observationTask = Task { @MainActor in
    for await markup in changes {
        documentStore.scheduleSave(
            paper: markup,
            url: documentURL
        )
    }
}
~~~

Confirm the Observation package and current Observations API in Xcode. Cancel the task when the document or controller is replaced. Do not retain a view controller forever through an observation closure.

## Recipe 12: render the model

PaperMarkup can render into a CGContext asynchronously:

~~~swift
func render(
    paper: PaperMarkup,
    context: CGContext,
    frame: CGRect,
    darkMode: Bool,
    rightToLeft: Bool
    ) async throws {
    let options = RenderingOptions(
        darkUserInterfaceStyle: darkMode,
        layoutRightToLeft: rightToLeft
    )
    await paper.draw(
        in: context,
        frame: frame,
        options: options
    )
}
~~~

The current SDK’s draw method is async but may not throw; keep the surrounding export service prepared for destination/context errors. Record frame, trait, color-space, and source revision with the artifact.

## Recipe 13: typed AI proposal

Keep AI output independent from PaperKit:

~~~swift
struct AnnotationProposal: Codable, Hashable, Sendable {
    let id: UUID
    let sourceRevision: String
    let kind: Kind
    let frame: CGRect
    let text: String?
    let sourceExcerpt: String

    enum Kind: String, Codable, Sendable {
        case summaryText
        case callout
        case outline
    }
}
~~~

Validation should reject:

- a stale source revision;
- a frame outside the PaperMarkup bounds;
- a feature unsupported by the current FeatureSet;
- a link that fails the app policy;
- a destructive operation not explicitly requested;
- a text box that cannot fit the localized content.

Render the proposal with a temporary overlay or adornment and call an explicit apply method only after confirmation.

## Recipe 14: apply a reviewed proposal

Keep the mutating command deterministic:

~~~swift
func apply(
    proposal: AnnotationProposal,
    to paper: PaperMarkup,
    featureSet: FeatureSet,
    currentSourceRevision: String
) throws {
    guard proposal.sourceRevision == currentSourceRevision else {
        throw ProposalError.staleSource
    }
    guard proposal.frame.isFinite,
          paper.bounds.contains(proposal.frame) else {
        throw ProposalError.invalidFrame
    }

    switch proposal.kind {
    case .summaryText:
        let attributed = AttributedString(proposal.text ?? "")
        paper.insertNewTextbox(
            attributedText: attributed,
            frame: proposal.frame,
            rotation: 0
        )
    case .callout:
        // Insert a bounded shape and an approved text box.
        break
    case .outline:
        // Map to a supported ShapeConfiguration.
        break
    }
}
~~~

The real implementation should return the inserted element IDs or an app-owned mutation record. Do not call this method from a model callback.

## Recipe 15: safe link policy

LinkMarkup can make a URL tappable. Validate before creating it:

~~~swift
func approvedURL(_ url: URL) -> URL? {
    guard let scheme = url.scheme?.lowercased(),
          scheme == "https" else {
        return nil
    }
    guard let host = url.host?.lowercased(),
          allowedHosts.contains(host) else {
        return nil
    }
    return url
}
~~~

Use the app’s own allowed-host policy and show the destination before activation. Treat AI-generated URLs as untrusted input.

## Recipe 16: SwiftUI review shell

Keep the PaperKit canvas and review controls distinct:

~~~swift
struct MarkupReviewShell: View {
    let proposalCount: Int
    let onApply: () -> Void
    let onReject: () -> Void

    var body: some View {
        VStack(spacing: 12) {
            Text("\(proposalCount) suggestions ready")
                .font(.headline)
            HStack {
                Button("Reject", action: onReject)
                Button("Apply", action: onApply)
                    .buttonStyle(.borderedProminent)
            }
        }
        .padding()
        .glassEffect()
    }
}
~~~

If the selected SDK or design does not require glass, use an opaque native control group. The review state must remain legible without a material.

## Recipe 17: test double boundary

Wrap the persistence/render/proposal side of the feature:

~~~swift
protocol MarkupDocumentClient: Sendable {
    func load(id: String) async throws -> PaperMarkup
    func save(_ paper: PaperMarkup, id: String) async throws
    func render(
        _ paper: PaperMarkup,
        request: RenderRequest
    ) async throws -> Data
}
~~~

The controller and PencilKit input remain physical/UI concerns. Test doubles can prove deterministic document and proposal behavior, not Apple Pencil latency or actual UIKit tool ergonomics.

## Verification notes

Before copying a recipe:

1. inspect the selected PaperKit SDK and beta annotations;
2. compile the smallest controller/representable target;
3. run model round-trip and proposal-validation tests;
4. use Preview/Simulator for app-owned shells and fixtures;
5. use a signed iPad/iPhone for Pencil, touch, save/reopen, accessibility, and export;
6. run target-specific Mac Catalyst/visionOS proof if supported.

Use the [PaperKit proof matrix](../60-verification/18-paperkit-and-markup-proof-matrix.md) to record evidence.

## Sources

- [PaperKit](https://developer.apple.com/documentation/paperkit)
- [Integrating PaperKit into your app](https://developer.apple.com/documentation/paperkit/getting-started-with-paperkit)
- [PaperKit updates](https://developer.apple.com/documentation/updates/paperkit)
- [PaperMarkup](https://developer.apple.com/documentation/paperkit/papermarkup)
- [PaperMarkupViewController](https://developer.apple.com/documentation/PaperKit/PaperMarkupViewController)
- [PaperMarkupViewController initializer](https://developer.apple.com/documentation/paperkit/papermarkupviewcontroller/init%28markup%3Asupportedfeatureset%3A%29)
- [MarkupEditViewController](https://developer.apple.com/documentation/paperkit/markupeditviewcontroller)
- [MarkupToolbarViewController](https://developer.apple.com/documentation/paperkit/markuptoolbarviewcontroller)
- [FeatureSet](https://developer.apple.com/documentation/paperkit/featureset)
- [ShapeConfiguration](https://developer.apple.com/documentation/paperkit/shapeconfiguration)
- [RenderingOptions](https://developer.apple.com/documentation/paperkit/renderingoptions)
- [MarkupInteractions](https://developer.apple.com/documentation/PaperKit/MarkupInteractions)
- [MarkupOrderedSet](https://developer.apple.com/documentation/PaperKit/MarkupOrderedSet)
- [LinkMarkup](https://developer.apple.com/documentation/PaperKit/LinkMarkup)
- [MarkupAdornment](https://developer.apple.com/documentation/paperkit/markupadornment)
- [PencilKit](https://developer.apple.com/documentation/pencilkit)
- [PKCanvasView](https://developer.apple.com/documentation/pencilkit/pkcanvasview)
- [PKToolPicker](https://developer.apple.com/documentation/pencilkit/pktoolpicker)
- [UIViewControllerRepresentable](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Apple Pencil and Scribble](https://developer.apple.com/design/human-interface-guidelines/apple-pencil-and-scribble)
