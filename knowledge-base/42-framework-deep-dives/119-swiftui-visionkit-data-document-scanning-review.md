# SwiftUI VisionKit data and document-scanning review

This review turns VisionKit’s current capture surfaces into a source-grounded iOS 26 route: live text and barcode scanning with DataScannerViewController, page-oriented document capture with VNDocumentCameraViewController, and Live Text interaction over app-owned images with ImageAnalyzer and ImageAnalysisInteraction. It pairs with the [design route](../21-design-deep-dives/147-swiftui-visionkit-data-document-scanning-review-design.md), the [capability route](../50-capability-recipes/150-swiftui-visionkit-data-document-scanning-review-route.md), the [proof matrix](../60-verification/144-swiftui-visionkit-data-document-scanning-proof-matrix.md), and the [code recipes](../70-code-recipes/162-swiftui-visionkit-data-document-scanning-review-recipes.md).

VisionKit is a capture and interaction layer, not a domain-truth layer. A recognized string, barcode payload, document page, detected subject, or Live Text transcript is an observation tied to a source image and a framework configuration. The app must keep the observation, the normalized proposal, the person’s edits, and the final domain action distinct.

## 1. Select the correct VisionKit surface

| Product need | First route | What the route owns | What the app still owns |
| --- | --- | --- | --- |
| Read text or codes from a live camera view | DataScannerViewController | Camera-facing UI, guidance, highlighting, focus, zoom, and recognized items | Permission copy, availability recovery, action policy, source record, validation, and review |
| Capture a multi-page physical document | VNDocumentCameraViewController | Camera pass-through and page capture flow | Page order, image retention, OCR, PDF export, field extraction, and review |
| Let a person select text or interact with data in an existing image | ImageAnalyzer plus ImageAnalysisInteraction | Analysis results and Live Text interaction UI | Image source, orientation, placement, custom actions, persistence, and accessibility task |
| Run custom OCR, object, barcode, pose, or model analysis on a frame or page | Vision and optionally Core ML | Request and observation contract | Frame admission, model lifecycle, normalization, stale-result policy, and user decision |
| Ask a local generative model to explain or structure a selected result | Foundation Models after capture | Model response generation | Bounded input, provenance, review, deterministic validation, and side-effect authorization |
| Build a custom camera UX or continuous frame pipeline | AVFoundation with Vision/Core ML | Capture session and sample buffers | Camera UI, frame pacing, thermal policy, observation presentation, and every privacy boundary |

Use the least complex route that meets the experience. DataScannerViewController is not a replacement for a custom AVFoundation pipeline, and the document camera is not a live OCR stream. ImageAnalysisInteraction is a system interaction attached to an existing image; it does not capture a camera feed.

## 2. Live scanning with DataScannerViewController

The live scanner is a main-actor UIKit view controller that scans the camera’s live video for text, semantic data in text, and machine-readable codes. Apple’s current documentation requires an availability check before presentation and a camera usage description before the app accesses the camera.

The minimum preflight is:

    DataScannerViewController.isSupported
    DataScannerViewController.isAvailable
    NSCameraUsageDescription in the actual application target

isSupported answers whether the device can perform data scanning. Apple documents A12 Bionic or later as the hardware boundary and documents the property as false for visionOS. isAvailable is a current runtime gate that includes camera authorization and restrictions. A supported device can still be unavailable because permission was denied, the camera is restricted, or the current system state prevents use.

If scanning is core to the app, Apple documents the UIRequiredDeviceCapabilities entry with the iphone-ipad-minimum-performance-a12 capability. Treat that as distribution filtering, not as a substitute for the runtime check. The route should still handle a device or session becoming unavailable after the screen appears.

### Configure only the data the feature needs

The DataScannerViewController initializer configures:

- recognizedDataTypes;
- qualityLevel;
- recognizesMultipleItems;
- isHighFrameRateTrackingEnabled;
- isPinchToZoomEnabled;
- isGuidanceEnabled;
- isHighlightingEnabled.

QualityLevel is a product and performance choice:

| Quality | Fit | Tradeoff to measure |
| --- | --- | --- |
| fast | Large, high-contrast items and a quick confirmation flow | Lower resolution can miss small or distant content |
| balanced | General-purpose scanning with unknown content | A compromise is not a quality guarantee |
| accurate | Small text, dense codes, or fine detail | Higher work can increase latency, memory, and thermal load |

Use recognizesMultipleItems when the person needs a set of results, such as labels on a shelf or several codes on a document. Use a single-item route when the product needs one explicit selection. Apple’s scanning article describes the single-item default as the item closest to the center, with tap input helping choose another item.

Enable high-frame-rate tracking when custom overlays must follow item geometry as the camera moves. Do not enable it simply because the app wants more callbacks; measure callback volume and overlay work. Pinch-to-zoom, guidance, and highlighting are user-facing controls. Disabling them changes the interaction contract and requires an equivalent explanation or fallback.

### RecognizedDataType is a scope boundary

RecognizedDataType can describe text or barcodes. A text type can include a language hint and an optional TextContentType. Supported semantic text types include URLs, dates and times, email addresses, flight numbers, full street addresses, shipment tracking numbers, telephone numbers, and currency.

The language list is a processing hint, not a hard “only these languages” filter. Apple documents that the scanner still recognizes all supported languages. Use supportedTextRecognitionLanguages to decide whether a requested hint is meaningful, but do not promise that an unsupported language will be excluded or that a supported language will be recognized in every scene.

Barcode recognition can be scoped to selected VNBarcodeSymbology values. Limit the symbologies when the domain knows what it expects. Narrow configuration can reduce false proposals and makes test fixtures easier to interpret.

Use the scanner’s current Swift spelling from the target SDK. The documented conceptual shapes are:

~~~swift
let recognizedDataTypes: Set<DataScannerViewController.RecognizedDataType> = [
    .text(languages: ["en-US"], textContentType: .telephoneNumber),
    .barcode(symbologies: [.qr])
]

let scanner = DataScannerViewController(
    recognizedDataTypes: recognizedDataTypes,
    qualityLevel: .balanced,
    recognizesMultipleItems: false,
    isHighFrameRateTrackingEnabled: true,
    isPinchToZoomEnabled: true,
    isGuidanceEnabled: true,
    isHighlightingEnabled: true
)
~~~

This is a compile-oriented shape, not a claim that every initializer default or overload is identical across SDK revisions. Compile the exact selected signature in the named iOS target.

### Start, stop, and observe

After the controller is configured and its delegate is assigned, startScanning begins live recognition. startScanning can throw; map failure to an unavailable or failed state rather than showing a scanning badge that was never established. stopScanning ends recognition while the controller may remain on screen. Stop before dismissal when the feature no longer needs camera work.

There are two current observation routes:

| Route | Use when | Ownership requirement |
| --- | --- | --- |
| DataScannerViewControllerDelegate | The product needs add, update, remove, tap, zoom, and unavailable callbacks | Coordinator or adapter handles callbacks quickly and publishes value state |
| recognizedItems AsyncStream | The product wants the current recognized collection over time | A consuming Task is cancelled when the scanner session or view disappears |

Do not use both routes to write the same state without an explicit deduplication policy. Delegate callbacks expose changes; the asynchronous stream exposes current arrays. Apple documents reading order for text items in the current all-items collection and documents difference(from:) as a way to compare successive arrays.

The stream is not a durable event log. A result can disappear when the camera moves, focus changes, the user changes the region of interest, or the scanner becomes unavailable. Store only a user-selected or otherwise explicitly retained capture as a product record.

### Delegate events are presentation events

The delegate surface includes:

- didAdd for newly recognized items;
- didUpdate for geometry changes;
- didRemove when items leave recognition;
- didTapOn for person-selected items;
- dataScannerDidZoom when the zoom changes;
- becameUnavailableWithError when scanning stops because the route became unavailable.

Use didAdd and didUpdate for custom highlighting only when the product truly needs a custom overlay. The scanner’s built-in highlighting is usually the more native starting point. If a custom overlay is required, add it to overlayContainerView so it does not interfere with the Live Text interface.

The tap callback is the user-intent boundary. A tap means “the person selected this recognized item,” not “the payload is authorized.” Validate a URL, phone number, shipment ID, or custom identifier before opening, calling, saving, or passing it to another feature.

### Item identity, content, and geometry

RecognizedItem has two cases:

- text, with transcript, bounds, observation, and id;
- barcode, with payload and barcode observation data, bounds, and id.

Every recognized item has an id that conforms to Identifiable. Use that ID for transient collection diffing, not as a long-term identity for the physical object. An item can leave the live view and a later item can represent the same printed value with a different ID.

RecognizedItem.Bounds contains four corners: topLeft, topRight, bottomRight, and bottomLeft. Apple documents these points in view coordinates. Do not treat bounds as normalized image coordinates, screen coordinates, or SwiftUI global coordinates. The view can be inset, transformed, cropped, or hosted inside a representable.

Text exposes transcript and a VNRecognizedTextObservation for Vision details not included in the simplified item properties. Barcode exposes its payload and VNBarcodeObservation. Use the observation only when the product needs Vision-specific details; keep the simple transcript/payload route as the default.

    live item
      -> item.id and source session
      -> text transcript or barcode payload
      -> item bounds in scanner-view coordinates
      -> user selection or explicit capture
      -> normalized proposal
      -> validation and review
      -> app-owned commit

Never turn the first recognized text into an irreversible save merely because it appears in the all-items collection.

### Capture a high-resolution still

DataScannerViewController can capture a high-resolution photo of the live video with capturePhoto. The still and the recognized item are related but not interchangeable. If the product needs an auditable source, capture the still or store the user-selected source according to a retention policy, then attach the item’s ID, transcript or payload, scanner configuration, and time to the proposal.

The capture route needs explicit states for:

- no still requested;
- capture in progress;
- capture succeeded;
- capture cancelled or failed;
- still retained;
- still deleted.

Do not claim that a high-resolution still contains the same crop, geometry, or exact frame as the item that prompted the action unless the app records and verifies that relationship.

### Region of interest and overlay placement

regionOfInterest is expressed in the live video’s view coordinates. It is not a pixel rectangle from the camera buffer and it is not a SwiftUI GeometryReader rectangle unless the adapter performs the required conversion. Keep the region and every custom overlay under one view-coordinate owner.

When using overlayContainerView:

1. let VisionKit own the camera and Live Text interface;
2. add only app-specific affordances to the overlay container;
3. keep hit testing and accessibility actions on the custom control;
4. avoid covering the system highlight or making a duplicate tap target;
5. clear custom overlays when the scanner session or source revision changes.

## 3. Document capture with VNDocumentCameraViewController

The document camera is a UIKit view controller for scanning a physical document page by page. It returns a VNDocumentCameraScan after the person saves the scan. It is not a live recognized-item stream.

Preflight:

    VNDocumentCameraViewController.isSupported
    NSCameraUsageDescription in the actual application target

The delegate receives exactly one of the documented outcomes:

- documentCameraViewController(_:didFinishWith:);
- documentCameraViewControllerDidCancel(_:);
- documentCameraViewController(_:didFailWithError:).

The app is responsible for dismissing the document camera in all delegate callbacks. Treat dismissal as part of the coordinator lifecycle and clear the delegate/coordinator relationship when the route is finished.

VNDocumentCameraScan exposes:

- title;
- pageCount;
- imageOfPage(at:).

Page indices are source identity. Preserve the scan title, page count, page order, and page index when deriving OCR or structured fields. If a page image is copied, give the copy a new asset identifier while retaining the scan/page provenance.

The document scan output can become:

    page images
      -> orientation and image-size record
      -> Vision text/barcode/rectangle requests
      -> field candidates
      -> page-aware review
      -> PDF/export or app-owned document

Apple’s document camera documentation describes exporting scanned images to PDF as an app responsibility. The framework returning images does not establish a PDF’s page order, metadata, security, or user approval. Those are app-owned export decisions.

Document scanning failure and cancellation are different:

| Outcome | Preserve | Next action |
| --- | --- | --- |
| cancel | Existing draft and any explicitly retained earlier pages | Return without claiming a completed scan |
| fail | Error category and any safe partial state | Explain, retry, import a photo, or enter fields manually |
| finish | Page count, title, ordered page images | Analyze and review before persistence |

Do not make a “finished” delegate callback silently commit extracted data. A finished scan only means the camera route returned a scan.

## 4. ImageAnalyzer and ImageAnalysisInteraction

ImageAnalyzer analyzes an app-owned image and produces ImageAnalysis. ImageAnalysisInteraction attaches a Live Text interface to an image view on iOS. The interaction is distinct from DataScannerViewController: the source is already an image, and the person interacts with recognized content over that image.

The documented flow is:

1. create an ImageAnalyzer.Configuration that describes analysis types and locales;
2. call the appropriate async analyze method with a UIImage, CGImage, CIImage, CVPixelBuffer, URL, or other supported image input and its orientation;
3. assign the resulting ImageAnalysis to ImageAnalysisInteraction.analysis;
4. add the interaction to the image view;
5. set preferredInteractionTypes;
6. optionally implement ImageAnalysisInteractionDelegate.

ImageAnalyzer is supported on the documented platforms and has supportedTextRecognitionLanguages. Do not infer support from the camera scanner’s A12 check; analyze the actual surface and target platform.

### InteractionTypes are explicit

ImageAnalysisInteraction.InteractionTypes includes:

- automatic;
- textSelection;
- dataDetectors;
- imageSubject;
- visualLookUp;
- automaticTextOnly.

The default preferred interaction set is empty, which disables interactions. Set the types the screen needs. automatic ignores the other types in the set, so choose either the automatic policy or a deliberate combination.

Use:

| Interaction type | Product meaning |
| --- | --- |
| textSelection | Select, copy, and translate recognized text |
| dataDetectors | Interact with URLs, email addresses, physical addresses, and related formats |
| imageSubject | Long-press to lift a subject from its background |
| visualLookUp | Offer more information about recognized subjects |
| automaticTextOnly | Enable text/data interactions without image-subject and Visual Look Up behavior |

Do not enable visual lookup or subject lifting simply because an image contains a person’s face or a product. Make the purpose and resulting action clear, and ensure the surrounding screen does not imply identification, ownership, or endorsement.

ImageAnalysisInteraction can expose text, selectedText, selectedAttributedText, contentsRect, and activeInteractionTypes. ImageAnalysis can report whether it has results for an analysis type and can provide a transcript. The transcript is still source-derived text, not a verified domain record.

### Use contentsRect for custom image views

If the image is not hosted in the standard image-view shape, implement the delegate’s contentsRect(for:) contract so VisionKit understands the interactive image region. A SwiftUI Image with a custom aspect-fit/fill layout can have a content region that differs from its container bounds.

The geometry rule is:

    source image
      -> orientation-normalized image
      -> displayed content rect
      -> VisionKit interaction coordinates
      -> SwiftUI container and accessibility frame

Keep the image orientation used for analysis aligned with the orientation used for display. A rotated source plus an unrotated analysis can produce a screen that looks correct but selects the wrong text or subject.

## 5. SwiftUI and UIKit bridging

VisionKit’s primary capture controllers are UIKit objects. SwiftUI should own value state and presentation intent; a coordinator or adapter should own the controller, delegate, and per-session tasks.

Recommended ownership:

| Concern | Owner |
| --- | --- |
| Sheet/full-screen presentation | SwiftUI |
| DataScannerViewController or VNDocumentCameraViewController instance | Representable coordinator or dedicated main-actor adapter |
| Delegate callbacks | Coordinator |
| recognizedItems consuming Task | Coordinator or session object, cancelled with the route |
| Item/page value state | SwiftUI model or main-actor store |
| OCR/Core ML/Foundation Models work | Dedicated bounded service with source revision |
| Review and commit | SwiftUI domain flow |

The representable should not create a new controller every time body recomputes. Create/configure in makeUIViewController, update only state that the controller actually supports, and stop or cancel in dismantleUIViewController. If a configuration change requires a new controller, end the old session explicitly first.

Use a session generation:

    presentation generation
      -> scanner/document controller
      -> source events
      -> analysis task
      -> review state

Every async completion must carry the generation. A late recognition or OCR completion from a dismissed scanner must not populate the next presentation.

For a Live Text interaction, a UIViewRepresentable can host an image view, add ImageAnalysisInteraction once, and update the image plus analysis. A custom image container must notify the interaction when its contents rectangle changes. Treat ImageAnalysis as value-like input to the interaction; do not retain an old analysis after the displayed image source changes.

## 6. Capture geometry and source provenance

The same string can be produced by a live camera item, a document page, an imported photo, or a cropped image. Those sources have different review and reproducibility properties.

Record a source envelope:

    sourceID
    sourceKind
    sessionGeneration
    deviceModel
    operatingSystem
    captureTime
    imageAssetID
    pageIndex
    sourceImageSize
    sourceOrientation
    displayedContentRect
    regionOfInterest
    scannerQuality
    recognizedDataTypes
    recognitionLanguageHint
    requestName
    requestRevision
    frameworkVersion

For DataScannerViewController, record item.id, text or barcode kind, transcript/payload, and RecognizedItem.Bounds corners in scanner-view coordinates. For document capture, record scan title, page count, page index, and image dimensions. For ImageAnalyzer, record the image asset and orientation passed to analyze plus the selected analysis types and interaction types.

When converting geometry:

1. establish the source image coordinate system;
2. normalize orientation and mirroring policy;
3. convert Vision or scanner coordinates into the displayed image content rect;
4. apply aspect-fit or aspect-fill crop;
5. apply safe-area and container transforms;
6. set an accessible frame that matches the actionable region;
7. test corners, center, rotation, crop, and mirrored camera.

Do not call a bounding box “accurate” without specifying the coordinate system and source revision. Geometry that is visually close on one device can be wrong at the edges of a cropped or rotated view.

## 7. Vision, Core ML, and Foundation Models handoff

VisionKit can be the capture front end while Vision, Core ML, or Foundation Models provide later stages. The handoff should narrow information at each boundary:

    VisionKit item/page/image
      -> app-owned source envelope
      -> Vision/Core ML observation
      -> normalized candidate
      -> user-selected bounded input
      -> Foundation Models proposal
      -> deterministic validation
      -> explicit review and commit

Vision requests should receive the correct image orientation, region, and request revision. Core ML models should be loaded with an explicit input/output contract, model identifier, revision, and compute policy. A model label or probability is not an authorization decision.

Foundation Models should receive only the source material needed for the user-approved task. A selected transcript, cropped page, or normalized field list is a better input boundary than an entire camera frame or document archive. Preserve the source item/page/frame ID and model/session generation beside any generated proposal.

The handoff contract should separate:

| Layer | Example | Save or act automatically? |
| --- | --- | --- |
| Raw capture | Live camera still or document page | Only under an explicit retention policy |
| Framework observation | Transcript, payload, bounds, page image | No |
| Normalized candidate | Parsed date, amount, URL, or field | Only after deterministic checks and product policy |
| AI proposal | Summary, grouping, explanation, or suggested field | No; show source and edit/reject |
| User-approved result | Edited field or confirmed action | Yes, subject to domain authorization |

If the AI output changes a URL, sends a message, mutates a record, opens a system surface, or triggers a device action, require an explicit confirmation at the side-effect boundary. Do not let a barcode payload or model response skip the review state.

## 8. Liquid Glass and native review UI

Use system controls and the system scanner interface as the primary native surface. The custom SwiftUI shell should explain:

1. why camera or image access is being used;
2. what the app is looking for;
3. whether scanning is supported and currently available;
4. what was recognized and where it came from;
5. what the person can review, edit, copy, save, or discard.

Liquid Glass is appropriate for compact controls such as:

- scan, capture, and stop actions;
- source/page navigation;
- a small review toolbar;
- retry and fallback actions;
- a bounded status capsule for permission or availability.

Keep recognized text, page previews, proposed fields, and source evidence on readable stable surfaces. Do not put long OCR text or a dense document review table inside a translucent floating glass group. If transparency is reduced, the content hierarchy and actions must remain understandable.

A polished scan screen is not one that hides state. It is one where the glass layer supports the action while the capture source and review result remain the visual subject.

## 9. Accessibility and alternate input

The complete task must work with:

- VoiceOver;
- Dynamic Type;
- Voice Control;
- Switch Control;
- keyboard and pointer on regular-width targets;
- increased contrast;
- reduced transparency;
- Reduce Motion;
- right-to-left layouts.

Do not make only the highlighted rectangle actionable. Provide a semantic list or review card for recognized items, with a meaningful label such as “Phone number found in camera view” or “Page 2, three fields need review.” Include stale, unavailable, failed, and permission states in the accessibility tree.

For live scanning:

- announce the scanner’s purpose before the camera opens;
- avoid repeated announcements for every geometry update;
- expose a selected item’s transcript or payload as a reviewable value;
- keep custom overlay hit targets large enough for alternate input;
- stop or pause announcements when the route is dismissed.

For documents:

- label pages by index and title;
- provide a page-level review route;
- avoid requiring a person to align a finger with a small OCR rectangle;
- keep manual entry available for every extracted field.

For ImageAnalysisInteraction:

- preserve the underlying image’s accessible label;
- ensure the interaction is enabled only when the analysis is current;
- provide a non-gesture path to the same text, data-detector, or subject action where the product defines one;
- test Dynamic Type around the image and action bar rather than treating the image itself as the entire interface.

## 10. Privacy and retention

Camera frames, document pages, OCR text, barcode payloads, and selected image content can contain personal, financial, health, location, or credential data. Maintain a route-specific data map:

| Data | Questions to answer |
| --- | --- |
| Camera stream | Is it processed only in memory? When does capture begin and stop? |
| High-resolution still | Is it retained, where, for how long, and how is deletion exposed? |
| Document page | Does page order or metadata identify the source person or business? |
| OCR/transcript | Is raw text logged, synced, exported, or sent to a model? |
| Barcode payload | Can it contain a credential, private URL, or personal identifier? |
| AI proposal | Is the source shown beside it and can the person edit or reject it? |
| Diagnostics | Do logs contain raw content, item IDs, image paths, or coordinates? |
| Network or provider | Is any custom handoff remote, and is that disclosed separately? |

The camera usage description should state the actual purpose in plain language. Do not request photo-library access for an image that can be selected through PhotosPicker. Do not say “on device” for a route that uploads page images, OCR text, or AI prompts.

Treat a captured image as sensitive until the product demonstrates otherwise. Redact or avoid storing the original when a normalized, user-approved value is enough. Provide deletion and cancellation behavior that clears provisional observations and stops capture.

## 11. Availability and failure state machine

Model the route explicitly:

    idle
      -> checkingSupport
      -> permissionNeeded
      -> unavailable
      -> ready
      -> presenting
      -> starting
      -> scanning or capturing
      -> sourceReady
      -> analyzing
      -> review
      -> confirmed
      -> saved

Failure branches:

- unsupported hardware -> photo import or manual route;
- camera restricted or denied -> settings explanation and manual route;
- startScanning throws -> stop, explain, and retry;
- scanner becomes unavailable -> mark current observations stale and recover;
- document cancelled -> preserve prior draft without claiming a completed scan;
- document fails -> keep safe partial state and offer retry/import;
- analysis throws -> show the source and allow manual extraction;
- AI generation cancelled -> preserve the selected source and discard only the provisional proposal;
- stale completion -> drop it and keep the current session generation;
- save fails -> preserve the reviewed draft and offer retry.

The fallback is part of the feature. If a live scanner is unavailable, a person should not lose the ability to enter or review the information that the feature was intended to capture.

## 12. Physical-device and release proof

Before calling a VisionKit route ready, record:

- target SDK and deployment target;
- device model and OS;
- DataScannerViewController.isSupported and isAvailable, or document-camera isSupported;
- camera permission state and recovery behavior;
- scanner configuration, recognized languages, and symbologies;
- start/stop/interruption behavior;
- item IDs, bounds, source time, and coordinate transforms;
- document page count, order, and image retention;
- ImageAnalyzer orientation and displayed-content rectangle;
- Vision/Core ML/Foundation Models handoff provenance;
- memory, latency, sustained-camera, and thermal observations;
- VoiceOver and Dynamic Type task results;
- archive target membership and privacy keys;
- TestFlight installation, upgrade, denial, and recovery behavior.

Simulator tests can exercise state machines, geometry fixtures, and review UI. They do not prove the physical camera, camera permission, scanner support, autofocus, lighting, live recognition latency, thermal behavior, or signed-release privacy configuration.

### Stop conditions

- A recognized item or OCR string is treated as domain truth without validation and review.
- isSupported and isAvailable are collapsed into one static capability.
- Camera usage text is missing from the actual target or does not describe the route.
- A document scan is treated as a live stream, or a live scanner is used as a multi-page document workflow.
- Item bounds or regions are mapped without a declared coordinate system.
- A recognizedItems Task outlives the scanner session.
- A document delegate callback fails to dismiss the controller.
- An ImageAnalysisInteraction is shown without current analysis or preferred interaction types.
- Raw page images or OCR text are sent to AI or network services without an explicit data boundary.
- A preview, simulator run, or one successful barcode is presented as physical-device, accessibility, privacy, or release proof.

## Sources

- [VisionKit](https://developer.apple.com/documentation/visionkit)
- [Scanning data with the camera](https://developer.apple.com/documentation/visionkit/scanning-data-with-the-camera)
- [DataScannerViewController](https://developer.apple.com/documentation/visionkit/datascannerviewcontroller)
- [DataScannerViewController.isSupported](https://developer.apple.com/documentation/visionkit/datascannerviewcontroller/issupported)
- [DataScannerViewController.isAvailable](https://developer.apple.com/documentation/visionkit/datascannerviewcontroller/isavailable)
- [DataScannerViewController.RecognizedDataType](https://developer.apple.com/documentation/visionkit/datascannerviewcontroller/recognizeddatatype)
- [Text data type](https://developer.apple.com/documentation/visionkit/datascannerviewcontroller/recognizeddatatype/text%28languages%3Atextcontenttype%3A%29?changes=_6)
- [DataScannerViewControllerDelegate](https://developer.apple.com/documentation/visionkit/datascannerviewcontrollerdelegate)
- [DataScannerViewController.recognizedItems](https://developer.apple.com/documentation/visionkit/datascannerviewcontroller/recognizeditems)
- [DataScannerViewController.ScanningUnavailable](https://developer.apple.com/documentation/visionkit/datascannerviewcontroller/scanningunavailable)
- [RecognizedItem](https://developer.apple.com/documentation/visionkit/recognizeditem)
- [RecognizedItem.Text](https://developer.apple.com/documentation/visionkit/recognizeditem/text)
- [RecognizedItem.Barcode](https://developer.apple.com/documentation/visionkit/recognizeditem/barcode)
- [RecognizedItem.Bounds](https://developer.apple.com/documentation/visionkit/recognizeditem/bounds)
- [VNDocumentCameraViewController](https://developer.apple.com/documentation/visionkit/vndocumentcameraviewcontroller)
- [VNDocumentCameraViewControllerDelegate](https://developer.apple.com/documentation/visionkit/vndocumentcameraviewcontrollerdelegate)
- [VNDocumentCameraScan](https://developer.apple.com/documentation/visionkit/vndocumentcamerascan)
- [ImageAnalyzer](https://developer.apple.com/documentation/visionkit/imageanalyzer)
- [ImageAnalysis](https://developer.apple.com/documentation/visionkit/imageanalysis)
- [ImageAnalysisInteraction](https://developer.apple.com/documentation/visionkit/imageanalysisinteraction)
- [ImageAnalysisInteraction.InteractionTypes](https://developer.apple.com/documentation/visionkit/imageanalysisinteraction/interactiontypes)
- [ImageAnalysisInteraction.preferredInteractionTypes](https://developer.apple.com/documentation/visionkit/imageanalysisinteraction/preferredinteractiontypes?changes=_1)
- [SwiftUI UIViewControllerRepresentable](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable)
- [SwiftUI UIViewRepresentable](https://developer.apple.com/documentation/swiftui/uiviewrepresentable)
- [Vision](https://developer.apple.com/documentation/vision)
- [VNImageRequestHandler](https://developer.apple.com/documentation/vision/vnimagerequesthandler)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
