# SwiftUI VisionKit data and document-scanning capability route

This route is an implementation plan for a named iOS target that needs live text/barcode scanning, document capture, or Live Text interaction over existing images. It pairs with the [framework review](../42-framework-deep-dives/119-swiftui-visionkit-data-document-scanning-review.md), the [design route](../21-design-deep-dives/147-swiftui-visionkit-data-document-scanning-review-design.md), the [proof matrix](../60-verification/144-swiftui-visionkit-data-document-scanning-proof-matrix.md), and the [recipes](../70-code-recipes/162-swiftui-visionkit-data-document-scanning-review-recipes.md).

The route is deliberately source-first: establish the capture surface and permission boundary, build a bounded adapter, normalize source data, then add review and optional on-device AI. Do not begin with a glass overlay or a model prompt.

## 1. Route selection

Choose one primary entry point:

| Entry point | Use | Required downstream work |
| --- | --- | --- |
| Live scanner | Text, semantic text, or barcode selection from the camera | Availability, permission, item tracking, tap validation, geometry, review |
| Document camera | One or more physical pages | Delegate lifecycle, page storage, OCR/analysis, page review, export |
| Existing image | Live Text/data detectors/subject interaction | Image orientation, ImageAnalyzer, interaction types, custom actions |
| Custom capture | Continuous frames, custom camera UI, or custom model | AVFoundation session, frame admission, Vision/Core ML, thermal policy |

If a product needs more than one, expose separate modes with separate state and provenance. Reusing a controller or a single “scan result” model across fundamentally different source types tends to hide cancellation, geometry, and review errors.

## 2. Target configuration gate

Before coding:

1. Confirm the target’s deployment target and selected iOS 26 SDK.
2. Add VisionKit, Vision, and any downstream framework imports to the named target.
3. Add NSCameraUsageDescription to the actual application target.
4. If live scanning is core, evaluate the documented A12 device-capability filter.
5. Decide whether the app needs PhotosPicker as a least-privilege fallback.
6. Decide whether document pages are retained, exported, synced, or deleted after extraction.
7. Define the source envelope and session generation before writing asynchronous handlers.
8. Define which actions require user review and which are deterministic formatting steps.

Privacy keys, device capabilities, entitlements, and target membership are release configuration. A local source file or a preview that displays the camera screen does not prove the signed target has them.

## 3. Shared route model

Use one product-owned state model with source-specific details:

~~~swift
enum VisionKitRouteState: Sendable {
    case idle
    case checking
    case permissionRequired
    case unsupported
    case restricted
    case ready
    case presenting
    case starting
    case scanning
    case capturing
    case captured(SourceEnvelope)
    case analyzing(SourceEnvelope)
    case review(ReviewDraft)
    case saved(destination: String)
    case cancelled
    case failed(RouteFailure)
}

enum VisionKitSurface: Sendable {
    case liveDataScanner
    case documentCamera
    case imageAnalysis
    case customVision
}

struct SourceEnvelope: Sendable, Hashable {
    let sourceID: UUID
    let surface: VisionKitSurface
    let sessionGeneration: UInt64
    let captureDate: Date
    let deviceDescription: String
    let osDescription: String
    let imageAssetID: String?
    let pageIndex: Int?
    let sourceWidth: Int?
    let sourceHeight: Int?
    let orientationDescription: String?
}

struct ReviewDraft: Sendable, Hashable {
    let source: SourceEnvelope
    var proposedFields: [ProposedField]
    var warnings: [String]
    var isConfirmed = false
}

struct ProposedField: Sendable, Hashable, Identifiable {
    let id: UUID
    let label: String
    let sourceValue: String
    var editedValue: String
    let sourceReference: String
    var requiresReview: Bool
}
~~~

The exact property types can change to match the target’s domain. The important boundary is that a VisionKit controller, recognized item, or model session is not persisted in a SwiftData record.

## 4. Live DataScanner implementation phases

### Phase A: preflight

Evaluate:

    DataScannerViewController.isSupported
    DataScannerViewController.isAvailable

Then request camera access through the app’s chosen authorization flow. Do not present the scanner until the route can explain a meaningful ready or recovery state.

Map:

| Condition | Route |
| --- | --- |
| unsupported | Import/manual fallback |
| not available because authorization is unknown | Permission context, then request |
| denied | Settings explanation and import/manual fallback |
| restricted | Explain restriction without repeated prompts |
| supported and available | Configure and present |

Keep a small diagnostic record of the evaluated result and target device. Do not use that record as a permanent capability cache; re-evaluate when the route returns to the foreground.

### Phase B: configure

Build a recognized-data set from the feature’s actual needs:

~~~swift
func liveDataTypes() -> Set<DataScannerViewController.RecognizedDataType> {
    [
        .text(
            languages: ["en-US"],
            textContentType: .URL
        ),
        .barcode(
            symbologies: [.qr, .ean13]
        )
    ]
}
~~~

Choose quality and interface options deliberately. Record the configuration in the session envelope:

    qualityLevel
    recognizesMultipleItems
    isHighFrameRateTrackingEnabled
    isPinchToZoomEnabled
    isGuidanceEnabled
    isHighlightingEnabled
    recognizedDataTypes
    requestedLanguageHints

Use the SDK’s current initializer signature. The values above are a route contract, not a reason to assume a particular overload or default.

### Phase C: present and start

Create the controller in a coordinator or main-actor adapter. Set its delegate before presentation or before scanning begins. Start scanning only after the view is ready and the route generation is current.

Use a single start guard:

    generation matches
    controller is the active controller
    scanner is available
    scanner is not already scanning
    permission is authorized

If startScanning throws, stop any partially configured path, publish a failure, and provide recovery. Do not swallow the error with a silent try? in production UI.

### Phase D: observe

Select one primary observation strategy:

| Need | Strategy |
| --- | --- |
| Custom add/update/remove highlighting | Delegate methods |
| Tap action and unavailable callback | Delegate methods |
| Current list with Swift concurrency | recognizedItems AsyncStream |
| Both event hooks and a list | Use one route as authoritative and derive the other carefully |

For recognizedItems:

1. create a Task for the active generation;
2. iterate the AsyncStream;
3. compare item IDs to update app state;
4. publish reading order for text;
5. check Task cancellation;
6. cancel the Task on disappearance, stop, dismissal, or generation change.

For delegates:

1. return quickly from callbacks;
2. copy only the small value data needed by SwiftUI;
3. keep custom overlay work bounded;
4. handle becameUnavailableWithError;
5. send didTapOn through validation and review.

Do not persist every transient array. A current collection is useful for UI, not necessarily a durable event history.

### Phase E: stop

Stop scanning when:

- the person taps cancel;
- the person selects an item and the feature no longer needs live video;
- the screen disappears;
- the app is backgrounded according to the product’s privacy policy;
- the scanner becomes unavailable;
- the route generation changes.

Then cancel the recognized-items Task, clear custom overlays, and dismiss or keep the controller according to the UX. The next presentation should use a new generation if the source or route identity changed.

## 5. Document-camera implementation phases

### Phase A: support and permission

Check VNDocumentCameraViewController.isSupported. Confirm the target contains NSCameraUsageDescription. Document camera support and live data scanner support are separate checks.

### Phase B: delegate adapter

Implement all three delegate outcomes:

- didFinishWith scan;
- didCancel;
- didFailWithError.

Dismiss the controller in each callback. Convert a successful scan to a SourceEnvelope with:

    scan.title
    scan.pageCount
    ordered page indices
    page image sizes
    capture time
    route generation

### Phase C: copy or process pages

Decide whether to:

- process each UIImage immediately;
- retain page images temporarily;
- write them to a protected app file;
- export a PDF;
- delete source pages after review.

Keep page processing bounded. A multi-page scan should not create an unbounded set of simultaneous OCR or model Tasks. Use a queue or actor with cancellation and a visible page status.

### Phase D: page-aware extraction

For each page:

    page source
      -> orientation record
      -> Vision request or Core ML request
      -> observation candidates
      -> normalized fields
      -> page reference
      -> review

Do not flatten all pages into one string before the app records page provenance. A person should be able to find the page that produced a field.

## 6. ImageAnalyzer implementation phases

Use ImageAnalyzer when the source is already an image and the person needs Live Text or subject interaction:

1. choose an image and preserve its identity;
2. preserve or normalize its orientation;
3. create an ImageAnalyzer.Configuration for required analysis types/locales;
4. call analyze with the correct image type and orientation;
5. store ImageAnalysis only for the current displayed source;
6. add ImageAnalysisInteraction to the image view;
7. set preferredInteractionTypes;
8. update contentsRect when layout changes;
9. clear analysis when the image changes.

Preferred interaction types should be explicit. The empty set disables interaction. automatic is convenient but can expose more behavior than the feature needs. automaticTextOnly is a useful route when text and data detectors are needed but image-subject interactions are not.

The view adapter should not analyze an image on every SwiftUI body update. Use a source ID and image revision to make analysis work idempotent:

    imageAssetID + imageRevision + orientation + analysisTypes

If the key has not changed, retain the current analysis. If it has changed, cancel or ignore old work and publish only the current generation.

## 7. SwiftUI bridge

For DataScannerViewController and VNDocumentCameraViewController:

~~~swift
struct ScannerControllerHost: UIViewControllerRepresentable {
    let generation: UInt64
    let onState: @MainActor (ScannerEvent) -> Void

    func makeCoordinator() -> Coordinator {
        Coordinator(generation: generation, onState: onState)
    }

    func makeUIViewController(context: Context) -> DataScannerViewController {
        let controller = DataScannerViewController(
            recognizedDataTypes: liveDataTypes(),
            qualityLevel: .balanced,
            recognizesMultipleItems: true,
            isHighFrameRateTrackingEnabled: true,
            isPinchToZoomEnabled: true,
            isGuidanceEnabled: true,
            isHighlightingEnabled: true
        )
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
}
~~~

This sketch intentionally leaves out event types and the exact start timing. The adapter must ensure that the controller is not started before permission and availability are ready. A representable is a bridge, not a substitute for a session owner.

For ImageAnalysisInteraction, use UIViewRepresentable to own the image view and interaction. Add the interaction once, update the image and analysis separately, and call the interaction’s contents update method when SwiftUI layout changes.

## 8. Normalize recognized values

Convert VisionKit outputs into product-owned proposals:

~~~swift
struct RecognizedProposal: Sendable, Hashable, Identifiable {
    let id: UUID
    let source: SourceEnvelope
    let itemID: UUID?
    let kind: String
    let rawValue: String
    let normalizedValue: String?
    let sourceGeometryDescription: String?
    let requiresReview: Bool
    let validationMessages: [String]
}
~~~

Examples:

- trim surrounding whitespace from text but retain raw transcript;
- parse a telephone number without silently changing country meaning;
- validate a URL before opening it;
- validate an EAN or shipment number with the domain’s checksum rules;
- preserve barcode payload bytes or string encoding where relevant;
- keep a document field’s page index and crop reference;
- reject empty or malformed values rather than saving them as successful recognition.

The normalized value is still not confirmed. The review flow owns the transition from proposal to confirmed domain value.

## 9. AI handoff route

Foundation Models, Core ML, and Vision can be downstream routes:

### Deterministic first

Run deterministic parsing and validation before a generative step. For example:

    barcode payload -> symbology check -> domain checksum -> review

or:

    OCR transcript -> field parser -> date/amount/identifier validation -> review

### Bounded generative input

If the user asks for an on-device explanation or structure:

1. let the user choose the item, page, or selected text;
2. copy only the needed source into an AI request;
3. attach source ID, page/item ID, and session generation;
4. show generated output as a proposal;
5. validate and edit;
6. require confirmation before a side effect.

Do not pass the complete camera stream or all pages to the model by default. Do not treat a model response as a replacement for OCR source or page provenance.

### Route-specific fallback

If Foundation Models is unavailable:

- keep deterministic fields;
- offer a manual editor;
- preserve the selected source;
- state that the optional suggestion is unavailable.

If Core ML model loading fails:

- keep the VisionKit capture;
- mark the analysis unavailable;
- never show the model result from a prior generation.

## 10. Route-specific errors

Use an error enum that retains evidence:

~~~swift
enum RouteFailure: Error, Sendable, Hashable {
    case unsupportedSurface
    case permissionDenied
    case cameraRestricted
    case scannerUnavailable(String)
    case scannerStartFailed(String)
    case documentCaptureFailed(String)
    case imageAnalysisFailed(String)
    case sourceChanged
    case cancelled
    case invalidProposal(String)
    case saveFailed(String)
}
~~~

Map errors to recovery, not technical strings:

| Technical boundary | User route |
| --- | --- |
| isSupported false | Import/manual |
| isAvailable false | Permission/restriction explanation |
| ScanningUnavailable.unsupported | Device fallback |
| ScanningUnavailable.cameraRestricted | Settings/admin route |
| startScanning throws | Retry or alternate source |
| document delegate failure | Keep safe partial state |
| ImageAnalyzer throws | Show image and manual/select route |
| cancellation | Preserve source, discard provisional result |
| stale generation | Drop completion silently or show current state |
| save error | Keep reviewed draft |

## 11. Verification sequence

Implement in this order:

1. target privacy and capability audit;
2. support/availability view with manual fallback;
3. representable/controller lifecycle;
4. live item or document page value state;
5. source envelope and generation guard;
6. review form;
7. deterministic field validation;
8. ImageAnalyzer route if needed;
9. Vision/Core ML handoff;
10. optional Foundation Models proposal;
11. Liquid Glass grouping;
12. accessibility task pass;
13. physical-device capture pass;
14. archive and TestFlight proof.

Do not add the AI route before the source and review route has a reliable manual path.

## 12. Device and release packet

For each chosen surface, record:

    target name
    SDK and deployment target
    device and OS
    framework availability values
    permission state
    recognized data configuration
    session generation
    source/page/item identifiers
    geometry coordinate system
    analysis/model revision
    fallback behavior
    accessibility task result
    memory/latency/thermal observations
    archive and TestFlight build

The packet should include at least one denial/recovery run, one unsupported or restricted simulation where possible, one physical-device run, one long source or multi-page run, one stale completion case, one Dynamic Type/VoiceOver pass, and one signed build.

## Stop conditions

- The controller is recreated by every SwiftUI body update.
- The recognized-items Task is not cancelled on dismissal.
- A successful document callback commits fields without review.
- ImageAnalysis uses stale analysis after the image source changes.
- The route lacks a manual/import fallback.
- Foundation Models receives unbounded raw capture by default.
- A geometry value is used outside its declared coordinate system.
- A Debug or simulator run is used as physical-camera or release proof.

## Sources

- [VisionKit](https://developer.apple.com/documentation/visionkit)
- [Scanning data with the camera](https://developer.apple.com/documentation/visionkit/scanning-data-with-the-camera)
- [DataScannerViewController](https://developer.apple.com/documentation/visionkit/datascannerviewcontroller)
- [DataScannerViewController.isSupported](https://developer.apple.com/documentation/visionkit/datascannerviewcontroller/issupported)
- [DataScannerViewController.isAvailable](https://developer.apple.com/documentation/visionkit/datascannerviewcontroller/isavailable)
- [DataScannerViewController.RecognizedDataType](https://developer.apple.com/documentation/visionkit/datascannerviewcontroller/recognizeddatatype)
- [DataScannerViewControllerDelegate](https://developer.apple.com/documentation/visionkit/datascannerviewcontrollerdelegate)
- [DataScannerViewController.recognizedItems](https://developer.apple.com/documentation/visionkit/datascannerviewcontroller/recognizeditems)
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
- [Vision](https://developer.apple.com/documentation/vision)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
