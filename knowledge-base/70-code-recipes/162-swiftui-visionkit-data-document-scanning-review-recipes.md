# SwiftUI VisionKit data and document-scanning code recipes

These recipes are compile-oriented sketches for the [VisionKit review](../42-framework-deep-dives/119-swiftui-visionkit-data-document-scanning-review.md). They pair with the [design route](../21-design-deep-dives/147-swiftui-visionkit-data-document-scanning-review-design.md), the [capability route](../50-capability-recipes/150-swiftui-visionkit-data-document-scanning-review-route.md), and the [proof matrix](../60-verification/144-swiftui-visionkit-data-document-scanning-proof-matrix.md).

Compile each selected API in a named iOS target against the target SDK. These sketches intentionally keep source, framework observations, proposals, review, and side effects separate. They are not camera, privacy, accessibility, physical-device, or release proof.

## Recipe 1: model availability and source identity

Keep framework state out of a persisted domain model:

~~~swift
import Foundation
import VisionKit

enum CaptureAvailability: Sendable, Equatable {
    case checking
    case ready
    case permissionRequired
    case denied
    case restricted
    case unsupported
    case failed(String)
}

enum CaptureSurface: Sendable, Hashable {
    case liveDataScanner
    case documentCamera
    case imageAnalysis
}

struct SourceEnvelope: Sendable, Hashable {
    let id: UUID
    let surface: CaptureSurface
    let generation: UInt64
    let capturedAt: Date
    let device: String
    let system: String
    let assetID: String?
    let pageIndex: Int?
    let width: Int?
    let height: Int?
    let orientation: String?
}

enum ReviewState: Sendable, Equatable {
    case provisional
    case needsReview([String])
    case approved
    case discarded
}
~~~

The source envelope may later become a SwiftData record, but the active DataScannerViewController, VNDocumentCameraScan, ImageAnalysis, or recognized-items stream should not be persisted as domain data.

## Recipe 2: check the live-scanner gate

Check support and current availability near presentation time:

~~~swift
import AVFoundation
import VisionKit

@MainActor
func liveScannerAvailability() -> CaptureAvailability {
    guard DataScannerViewController.isSupported else {
        return .unsupported
    }

    switch AVCaptureDevice.authorizationStatus(for: .video) {
    case .authorized:
        return DataScannerViewController.isAvailable ? .ready : .restricted
    case .notDetermined:
        return .permissionRequired
    case .denied:
        return .denied
    case .restricted:
        return .restricted
    @unknown default:
        return .failed("Unknown camera authorization state")
    }
}
~~~

isAvailable remains the final VisionKit gate because restrictions can exist beyond the authorization enum. Re-check after a settings return or scene activation.

## Recipe 3: request camera access in context

Request only when the person chooses the camera route:

~~~swift
import AVFoundation

func requestCameraAccess() async -> Bool {
    switch AVCaptureDevice.authorizationStatus(for: .video) {
    case .authorized:
        return true
    case .notDetermined:
        return await AVCaptureDevice.requestAccess(for: .video)
    case .denied, .restricted:
        return false
    @unknown default:
        return false
    }
}
~~~

Add NSCameraUsageDescription to the actual application target before this runs. A denied result should route to settings/import/manual entry rather than repeatedly requesting access.

## Recipe 4: configure a focused data scanner

Scope the recognition types and record the values:

~~~swift
import VisionKit
import Vision

struct ScannerConfiguration: Sendable, Hashable {
    let quality: DataScannerViewController.QualityLevel
    let multiple: Bool
    let highFrameRateTracking: Bool
    let pinchToZoom: Bool
    let guidance: Bool
    let highlighting: Bool
    let languageHints: [String]
}

func makeScanner(
    configuration: ScannerConfiguration
) -> DataScannerViewController {
    let types: Set<DataScannerViewController.RecognizedDataType> = [
        .text(
            languages: configuration.languageHints,
            textContentType: nil
        ),
        .barcode(
            symbologies: [.qr, .ean13, .code128]
        )
    ]

    return DataScannerViewController(
        recognizedDataTypes: types,
        qualityLevel: configuration.quality,
        recognizesMultipleItems: configuration.multiple,
        isHighFrameRateTrackingEnabled: configuration.highFrameRateTracking,
        isPinchToZoomEnabled: configuration.pinchToZoom,
        isGuidanceEnabled: configuration.guidance,
        isHighlightingEnabled: configuration.highlighting
    )
}
~~~

The exact initializer signature should be compiled against the selected SDK. Keep language hints and symbologies in the source record so a later proposal can explain what the scanner was configured to recognize.

## Recipe 5: bridge a live scanner into SwiftUI

Use a coordinator for the UIKit controller and keep SwiftUI state value-based:

~~~swift
import SwiftUI
import VisionKit

enum ScannerEvent: Sendable {
    case didStart
    case didAdd([RecognizedItem])
    case didUpdate([RecognizedItem])
    case didRemove([RecognizedItem])
    case didTap(RecognizedItem)
    case didStop
    case becameUnavailable(String)
}

struct DataScannerHost: UIViewControllerRepresentable {
    let configuration: ScannerConfiguration
    let generation: UInt64
    let onEvent: @MainActor (ScannerEvent) -> Void

    func makeCoordinator() -> Coordinator {
        Coordinator(generation: generation, onEvent: onEvent)
    }

    func makeUIViewController(context: Context) -> DataScannerViewController {
        let controller = makeScanner(configuration: configuration)
        controller.delegate = context.coordinator
        context.coordinator.attach(controller)
        return controller
    }

    func updateUIViewController(
        _ controller: DataScannerViewController,
        context: Context
    ) {
        context.coordinator.update(generation: generation)
    }

    static func dismantleUIViewController(
        _ controller: DataScannerViewController,
        coordinator: Coordinator
    ) {
        coordinator.stop()
    }

    @MainActor
    final class Coordinator: NSObject, DataScannerViewControllerDelegate {
        private var generation: UInt64
        private weak var controller: DataScannerViewController?
        private let onEvent: @MainActor (ScannerEvent) -> Void

        init(
            generation: UInt64,
            onEvent: @escaping @MainActor (ScannerEvent) -> Void
        ) {
            self.generation = generation
            self.onEvent = onEvent
        }

        func attach(_ controller: DataScannerViewController) {
            self.controller = controller
        }

        func update(generation: UInt64) {
            if generation != self.generation {
                stop()
                self.generation = generation
            }
        }

        func stop() {
            controller?.stopScanning()
            onEvent(.didStop)
        }

        func dataScanner(
            _ dataScanner: DataScannerViewController,
            didAdd addedItems: [RecognizedItem],
            allItems: [RecognizedItem]
        ) {
            onEvent(.didAdd(addedItems))
        }

        func dataScanner(
            _ dataScanner: DataScannerViewController,
            didUpdate updatedItems: [RecognizedItem],
            allItems: [RecognizedItem]
        ) {
            onEvent(.didUpdate(updatedItems))
        }

        func dataScanner(
            _ dataScanner: DataScannerViewController,
            didRemove removedItems: [RecognizedItem],
            allItems: [RecognizedItem]
        ) {
            onEvent(.didRemove(removedItems))
        }

        func dataScanner(
            _ dataScanner: DataScannerViewController,
            didTapOn item: RecognizedItem
        ) {
            onEvent(.didTap(item))
        }

        func dataScanner(
            _ dataScanner: DataScannerViewController,
            becameUnavailableWithError error:
                DataScannerViewController.ScanningUnavailable
        ) {
            onEvent(.becameUnavailable(String(describing: error)))
        }
    }
}
~~~

This sketch does not decide when the controller starts. Start only after the parent route has passed support, permission, and current-generation checks. Avoid triggering start repeatedly from updateUIViewController.

## Recipe 6: consume recognizedItems with cancellation

Use the stream as the current collection source:

~~~swift
import VisionKit

@MainActor
final class RecognizedItemsConsumer {
    private var task: Task<Void, Never>?
    private var generation: UInt64 = 0

    func start(
        scanner: DataScannerViewController,
        generation: UInt64,
        publish: @escaping @MainActor ([RecognizedItem]) -> Void
    ) {
        stop()
        self.generation = generation

        task = Task { @MainActor [weak self, scanner] in
            for await items in scanner.recognizedItems {
                guard
                    let self,
                    !Task.isCancelled,
                    self.generation == generation
                else {
                    return
                }
                publish(items)
            }
        }
    }

    func stop() {
        task?.cancel()
        task = nil
    }
}
~~~

If the SDK’s concurrency diagnostics require a different capture arrangement, adapt the isolation while preserving the invariant: the consuming task must not publish after the session generation changes.

## Recipe 7: normalize a recognized item

Keep raw and normalized values:

~~~swift
import CoreGraphics
import VisionKit

struct ItemProposal: Sendable, Hashable, Identifiable {
    let id: UUID
    let itemID: UUID
    let kind: String
    let rawValue: String
    let normalizedValue: String?
    let boundsDescription: String
    let warnings: [String]
    var reviewed = false
}

func proposal(for item: RecognizedItem) -> ItemProposal {
    switch item {
    case .text(let text):
        return ItemProposal(
            id: UUID(),
            itemID: text.id,
            kind: "text",
            rawValue: text.transcript,
            normalizedValue: text.transcript.trimmingCharacters(
                in: .whitespacesAndNewlines
            ),
            boundsDescription: String(describing: text.bounds),
            warnings: []
        )
    case .barcode(let barcode):
        let payload = barcode.payloadString ?? ""
        return ItemProposal(
            id: UUID(),
            itemID: barcode.id,
            kind: "barcode",
            rawValue: payload,
            normalizedValue: payload.isEmpty ? nil : payload,
            boundsDescription: String(describing: barcode.bounds),
            warnings: payload.isEmpty
                ? ["The barcode has no usable payload."]
                : []
        )
    @unknown default:
        return ItemProposal(
            id: UUID(),
            itemID: item.id,
            kind: "unknown",
            rawValue: "",
            normalizedValue: nil,
            boundsDescription: String(describing: item.bounds),
            warnings: ["This item kind is not handled by this build."]
        )
    }
}
~~~

The exact barcode payload property should be compiled against the current SDK. A normalized value is still provisional until deterministic validation and user review pass.

## Recipe 8: validate a tapped destination

Treat a tap as user intent, not authorization:

~~~swift
import Foundation

enum TapAction {
    case reviewText(String)
    case reviewBarcode(String)
    case reject(String)
}

func actionForTappedPayload(_ payload: String) -> TapAction {
    guard
        let url = URL(string: payload),
        let scheme = url.scheme?.lowercased(),
        ["https", "http"].contains(scheme)
    else {
        return .reviewBarcode(payload)
    }

    return .reviewBarcode(url.absoluteString)
}
~~~

The product may support additional schemes, phone numbers, or app links. Validate the actual domain policy and present the destination before opening. Never let arbitrary camera text become an app action without a review boundary.

## Recipe 9: document-camera coordinator

Convert page-oriented callbacks into value state:

~~~swift
import UIKit
import VisionKit

@MainActor
final class DocumentCameraCoordinator:
    NSObject,
    VNDocumentCameraViewControllerDelegate
{
    var onFinish: (@MainActor (VNDocumentCameraScan) -> Void)?
    var onCancel: (@MainActor () -> Void)?
    var onFailure: (@MainActor (String) -> Void)?

    func documentCameraViewController(
        _ controller: VNDocumentCameraViewController,
        didFinishWith scan: VNDocumentCameraScan
    ) {
        onFinish?(scan)
        controller.dismiss(animated: true)
    }

    func documentCameraViewControllerDidCancel(
        _ controller: VNDocumentCameraViewController
    ) {
        onCancel?()
        controller.dismiss(animated: true)
    }

    func documentCameraViewController(
        _ controller: VNDocumentCameraViewController,
        didFailWithError error: any Error
    ) {
        onFailure?(error.localizedDescription)
        controller.dismiss(animated: true)
    }
}
~~~

The delegate must remain retained by the representable or presentation owner for the controller’s lifetime. Dismiss in all three callback paths, then decide whether safe partial page state should remain in the app’s draft.

## Recipe 10: copy document pages with provenance

Build a page source list immediately after a successful scan:

~~~swift
import UIKit
import VisionKit

struct DocumentPageSource: Sendable, Hashable, Identifiable {
    let id: UUID
    let scanTitle: String
    let scanPageCount: Int
    let pageIndex: Int
    let imageSize: CGSize
}

func pageSources(
    from scan: VNDocumentCameraScan
) -> [DocumentPageSource] {
    (0..<scan.pageCount).compactMap { index in
        let image = scan.imageOfPage(at: index)
        guard image.size.width > 0, image.size.height > 0 else {
            return nil
        }
        return DocumentPageSource(
            id: UUID(),
            scanTitle: scan.title,
            scanPageCount: scan.pageCount,
            pageIndex: index,
            imageSize: image.size
        )
    }
}
~~~

If pages are written to disk, add an app-owned asset ID and retention/deletion policy. The page index is a source reference, not a guarantee that a field is correct.

## Recipe 11: configure ImageAnalyzer

Analyze an existing image with an explicit source revision:

~~~swift
import UIKit
import VisionKit

struct ImageAnalysisKey: Hashable, Sendable {
    let sourceID: UUID
    let revision: String
    let orientationDescription: String
}

@MainActor
final class ImageAnalysisController {
    private let analyzer = ImageAnalyzer()
    private(set) var analysis: ImageAnalysis?
    private(set) var key: ImageAnalysisKey?

    func analyze(
        image: UIImage,
        key: ImageAnalysisKey,
        configuration: ImageAnalyzer.Configuration
    ) async throws {
        guard self.key != key else { return }
        self.analysis = nil
        let result = try await analyzer.analyze(
            image,
            configuration: configuration
        )
        guard !Task.isCancelled else { return }
        self.analysis = result
        self.key = key
    }

    func clear() {
        analysis = nil
        key = nil
    }
}
~~~

Use the analyze overload that matches the source image type and pass the correct orientation. If a source changes while analysis is running, the caller must use a generation or key guard before publishing.

## Recipe 12: host ImageAnalysisInteraction

Add the interaction to a UIKit image view through SwiftUI:

~~~swift
import SwiftUI
import UIKit
import VisionKit

struct LiveTextImageView: UIViewRepresentable {
    let image: UIImage
    let analysis: ImageAnalysis?
    let interactionTypes: ImageAnalysisInteraction.InteractionTypes

    func makeUIView(context: Context) -> UIImageView {
        let imageView = UIImageView()
        imageView.contentMode = .scaleAspectFit
        imageView.isUserInteractionEnabled = true

        let interaction = ImageAnalysisInteraction()
        interaction.preferredInteractionTypes = interactionTypes
        imageView.addInteraction(interaction)
        context.coordinator.interaction = interaction
        return imageView
    }

    func updateUIView(_ imageView: UIImageView, context: Context) {
        imageView.image = image
        context.coordinator.interaction?.analysis = analysis
        context.coordinator.interaction?.preferredInteractionTypes =
            interactionTypes
    }

    func makeCoordinator() -> Coordinator {
        Coordinator()
    }

    final class Coordinator {
        var interaction: ImageAnalysisInteraction?
    }
}
~~~

The interaction’s default preferred types are empty. Set the intended types explicitly. If the image is inside a custom container rather than a normal image view, implement the delegate’s contents-rectangle contract and update it when layout changes.

## Recipe 13: convert a selected item to a bounded AI input

Keep the AI input narrow and source-linked:

~~~swift
struct AIInputEnvelope: Sendable, Hashable {
    let sourceID: UUID
    let sessionGeneration: UInt64
    let pageIndex: Int?
    let itemID: UUID?
    let selectedText: String
    let taskDescription: String
}

struct AIProposal: Sendable, Hashable, Identifiable {
    let id: UUID
    let source: AIInputEnvelope
    let generatedText: String
    let warnings: [String]
    var editedText: String
    var approved = false
}

func makeAIInput(
    sourceID: UUID,
    generation: UInt64,
    pageIndex: Int?,
    itemID: UUID?,
    selectedText: String,
    task: String
) -> AIInputEnvelope? {
    let trimmed = selectedText.trimmingCharacters(in: .whitespacesAndNewlines)
    guard !trimmed.isEmpty else { return nil }
    return AIInputEnvelope(
        sourceID: sourceID,
        sessionGeneration: generation,
        pageIndex: pageIndex,
        itemID: itemID,
        selectedText: trimmed,
        taskDescription: task
    )
}
~~~

The model request may use Foundation Models, Core ML, or another local route. Keep the source envelope next to the proposal and require deterministic validation before applying an action.

## Recipe 14: ignore stale asynchronous work

Use a generation gate at every async boundary:

~~~swift
@MainActor
final class CaptureSessionStore {
    private(set) var generation: UInt64 = 0
    private(set) var currentSource: UUID?

    func beginSource(_ sourceID: UUID) -> UInt64 {
        generation &+= 1
        currentSource = sourceID
        return generation
    }

    func accepts(
        sourceID: UUID,
        generation: UInt64
    ) -> Bool {
        sourceID == currentSource && generation == self.generation
    }
}
~~~

The store does not stop framework work by itself. Pair it with Task cancellation, controller stop, and model-service cancellation. The gate is the final publication guard.

## Recipe 15: review before commit

Make the commit operation explicit:

~~~swift
enum CommitResult: Sendable {
    case needsReview
    case invalid([String])
    case saved(String)
}

@MainActor
func commit(
    draft: ReviewDraft,
    editedFields: [ProposedField]
) async -> CommitResult {
    let invalid = editedFields.flatMap { field in
        field.editedValue.isEmpty
            ? ["\(field.label) is empty"]
            : []
    }

    guard invalid.isEmpty else {
        return .invalid(invalid)
    }

    guard draft.isConfirmed else {
        return .needsReview
    }

    // Persist or trigger the side effect only here.
    return .saved("app-owned-record")
}
~~~

Replace the placeholder persistence with the target’s authorization and transaction policy. The framework observation and AI proposal never call the side effect directly.

## Recipe 16: pure geometry fixture

Keep mapping tests independent from the camera:

~~~swift
import CoreGraphics

struct DisplayTransform: Sendable, Hashable {
    let sourceSize: CGSize
    let contentRect: CGRect
    let mirrored: Bool
}

func mapPoint(
    _ point: CGPoint,
    using transform: DisplayTransform
) -> CGPoint {
    let sourceX = transform.mirrored
        ? transform.sourceSize.width - point.x
        : point.x
    let normalizedX = sourceX / transform.sourceSize.width
    let normalizedY = point.y / transform.sourceSize.height
    return CGPoint(
        x: transform.contentRect.minX
            + normalizedX * transform.contentRect.width,
        y: transform.contentRect.minY
            + normalizedY * transform.contentRect.height
    )
}
~~~

This is only a geometry adapter fixture. DataScannerViewController bounds already arrive in scanner-view coordinates, while Vision observations and image content can use different systems. Test the actual source coordinate declaration before using this mapping.

## Recipe 17: capture proof log without raw content

Log metadata, not private text or image bytes:

~~~swift
import OSLog

struct CaptureProofRecord: Sendable {
    let surface: String
    let generation: UInt64
    let sourceID: String
    let pageIndex: Int?
    let itemKind: String?
    let itemCount: Int
    let coordinateSpace: String?
    let availability: String
    let outcome: String
}

let captureLogger = Logger(
    subsystem: "com.example.app",
    category: "visionkit-capture"
)

func record(_ proof: CaptureProofRecord) {
    captureLogger.info(
        "surface=\(proof.surface, privacy: .public) " +
        "generation=\(proof.generation, privacy: .public) " +
        "source=\(proof.sourceID, privacy: .private(mask: .hash)) " +
        "page=\(proof.pageIndex ?? -1, privacy: .public) " +
        "kind=\(proof.itemKind ?? "none", privacy: .public) " +
        "count=\(proof.itemCount, privacy: .public) " +
        "space=\(proof.coordinateSpace ?? "none", privacy: .public) " +
        "availability=\(proof.availability, privacy: .public) " +
        "outcome=\(proof.outcome, privacy: .public)"
    )
}
~~~

Review the privacy behavior of logs in the chosen deployment and avoid passing raw transcript, barcode payload, page paths, or image-derived identifiers into public log messages.

## Recipe 18: route tests to write first

Use pure fixtures before asking for a physical camera:

~~~swift
struct VisionKitRouteFixture {
    let name: String
    let expectedState: String
    let expectedFallback: String
}

let fixtures = [
    VisionKitRouteFixture(
        name: "scanner unsupported",
        expectedState: "unsupported",
        expectedFallback: "manual or import"
    ),
    VisionKitRouteFixture(
        name: "permission denied",
        expectedState: "denied",
        expectedFallback: "settings or import"
    ),
    VisionKitRouteFixture(
        name: "stale completion",
        expectedState: "current generation only",
        expectedFallback: "discard late result"
    ),
    VisionKitRouteFixture(
        name: "document cancelled",
        expectedState: "cancelled",
        expectedFallback: "preserve draft"
    ),
    VisionKitRouteFixture(
        name: "AI unavailable",
        expectedState: "reviewable deterministic result",
        expectedFallback: "manual edit"
    )
]
~~~

Add target-specific Swift Testing or XCTest assertions for state, source provenance, geometry, and review. The fixture list is not a substitute for a physical-device capture matrix.

## Stop conditions

- A recipe persists a framework controller, live stream, or ImageAnalysis as domain truth.
- A bridge starts scanning from every SwiftUI update.
- A recognized item can trigger a side effect without review or validation.
- The document coordinator does not dismiss on every delegate path.
- An image-analysis adapter keeps old analysis after the image source changes.
- AI input has no source ID, page/item ID, or generation.
- Logs include raw captured content.
- A successful compile is called physical-camera or release proof.

## Sources

- [VisionKit](https://developer.apple.com/documentation/visionkit)
- [Scanning data with the camera](https://developer.apple.com/documentation/visionkit/scanning-data-with-the-camera)
- [DataScannerViewController](https://developer.apple.com/documentation/visionkit/datascannerviewcontroller)
- [DataScannerViewController.RecognizedDataType](https://developer.apple.com/documentation/visionkit/datascannerviewcontroller/recognizeddatatype)
- [DataScannerViewControllerDelegate](https://developer.apple.com/documentation/visionkit/datascannerviewcontrollerdelegate)
- [DataScannerViewController.recognizedItems](https://developer.apple.com/documentation/visionkit/datascannerviewcontroller/recognizeditems)
- [DataScannerViewController.ScanningUnavailable](https://developer.apple.com/documentation/visionkit/datascannerviewcontroller/scanningunavailable)
- [RecognizedItem](https://developer.apple.com/documentation/visionkit/recognizeditem)
- [RecognizedItem.Text](https://developer.apple.com/documentation/visionkit/recognizeditem/text)
- [RecognizedItem.Barcode](https://developer.apple.com/documentation/visionkit/recognizeditem/barcode)
- [VNDocumentCameraViewController](https://developer.apple.com/documentation/visionkit/vndocumentcameraviewcontroller)
- [VNDocumentCameraViewControllerDelegate](https://developer.apple.com/documentation/visionkit/vndocumentcameraviewcontrollerdelegate)
- [VNDocumentCameraScan](https://developer.apple.com/documentation/visionkit/vndocumentcamerascan)
- [ImageAnalyzer](https://developer.apple.com/documentation/visionkit/imageanalyzer)
- [ImageAnalysis](https://developer.apple.com/documentation/visionkit/imageanalysis)
- [ImageAnalysisInteraction](https://developer.apple.com/documentation/visionkit/imageanalysisinteraction)
- [ImageAnalysisInteraction.InteractionTypes](https://developer.apple.com/documentation/visionkit/imageanalysisinteraction/interactiontypes)
- [SwiftUI UIViewControllerRepresentable](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable)
- [SwiftUI UIViewRepresentable](https://developer.apple.com/documentation/swiftui/uiviewrepresentable)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
