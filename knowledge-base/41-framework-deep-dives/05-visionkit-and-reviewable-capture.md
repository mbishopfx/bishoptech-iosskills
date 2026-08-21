# VisionKit and Reviewable Capture

## Capability

VisionKit supplies user-facing capture and analysis experiences around the camera and images, including live text and barcode scanning. Vision supplies lower-level requests such as text recognition. Together they are a strong route for “capture something, propose structured values, let the person correct them, then save.”

## Choose the capture route

| Need | First route | Boundary |
| --- | --- | --- |
| Scan text or codes directly from a live camera view | `DataScannerViewController` | Camera permission and device support/availability are required. |
| Scan a physical document | VisionKit document camera | The returned scan still needs domain validation and review. |
| Recognize text in an existing image | Vision text recognition request | Image quality, language, orientation, and confidence affect results. |
| Identify objects, faces, poses, or image quality | Vision request family | Choose the request for the actual task; do not call generic “AI” without a measurable output. |

## DataScanner route

Before presenting a data scanner:

1. Check `DataScannerViewController.isSupported`.
2. Check `DataScannerViewController.isAvailable`.
3. Add an honest `NSCameraUsageDescription`.
4. Configure only the text and barcode types the feature needs.
5. Handle recognized-item callbacks or the asynchronous recognized-items stream.
6. Convert the result into a draft domain object and show the source/captured value for review.
7. Stop scanning when the user leaves the capture flow.

Availability is not a one-time install fact: camera access, restrictions, device capability, and current system state can make the scanner unavailable.

## Reviewable extraction pipeline

`camera/image -> recognized observations -> normalized draft -> user review -> confirmed model -> optional AI enrichment`

Keep the original capture or a user-approved reference when the product needs traceability. Preserve confidence or provenance where the selected API exposes it. Avoid silently overwriting a person’s existing record with a low-confidence recognition result.

Illustrative domain boundary:

```swift
struct ExtractedField {
    let label: String
    let proposedValue: String
    let source: String
    let requiresReview: Bool
}

struct CaptureDraft {
    var fields: [ExtractedField]
    var isConfirmed: Bool = false
}
```

The model above is intentionally independent of VisionKit. Framework observations should be translated into a product-owned draft before SwiftUI renders an edit form or before a Foundation Models feature receives bounded input.

## Boundaries and failure modes

- Camera permission must be requested in context and described accurately.
- A supported scanner can still be unavailable; show a fallback such as photo-library import or manual entry when appropriate.
- OCR and barcode output are observations, not guaranteed truth. Validate formats, totals, dates, and identifiers before saving.
- Avoid sending raw captured content to a remote service when on-device processing is sufficient or when the product has not obtained the necessary consent.
- Consider redaction and retention for documents containing names, addresses, financial details, or health information.
- Physical-device testing is required for camera, lighting, focus, and real-world capture behavior.

## Verification route

- Test real and poor-quality samples: glare, skew, small type, handwriting, multiple languages, partial occlusion, and duplicate codes.
- Test camera denied, scanner unsupported, scanner unavailable, and interrupted capture states.
- Confirm a user can correct every proposed field before persistence.
- Measure extraction quality with a labeled sample set instead of relying on one successful demo.
- Verify accessible labels, focus order, zoom, and alternate manual entry.

## Capture route decision tree

Choose the least privileged capture path that still serves the task:

1. If the user already has an image, start with `PhotosPicker` and request a representation of the selected item.
2. If the user needs a live text/barcode scan, check `DataScannerViewController.isSupported` and `isAvailable` before presenting the camera scanner.
3. If the task is a multi-page physical document, use the document camera route and treat the returned scan as source material for Vision and review.
4. If the task needs a custom camera UI or continuous frames, use AVFoundation plus Vision/Core ML and define frame pacing, backpressure, and cancellation explicitly.

Do not request broad photo-library authorization just to support a one-off selected image. Do not present a scanner that the device or current permission/restriction state cannot use. Keep a manual or import fallback when the feature can still provide value without the live camera.

## Availability state machine

`unselected -> loading source -> source ready -> analyzing -> review -> confirmed`

Failure branches are first-class:

- `camera unsupported -> photo/manual fallback`
- `camera unavailable or denied -> explain and offer settings/manual route`
- `source load failed -> retry or choose another asset`
- `analysis cancelled -> preserve source, discard only provisional observations`
- `analysis failed -> show the source and allow manual entry`
- `low confidence or invalid format -> highlight the field for review`
- `confirmed save failed -> preserve the corrected draft and retry`

The user should be able to see what was captured, what the framework proposed, what they changed, and what was finally saved. Avoid a spinner that hides the source or an automatic overwrite that makes correction difficult.

## Review UI contract

For every extracted field, display or make available:

| Field property | Why it matters |
| --- | --- |
| Proposed value | The person needs to see what the system will save |
| Editable control | Correction is part of the feature, not an exceptional path |
| Source/provenance | A crop, line, page, barcode, or captured image can explain the proposal |
| Confidence/review flag | Directs attention without pretending to be truth |
| Validation message | Explains format, missing value, conflict, or unsupported content |
| Save state | Distinguishes draft, confirmed, saving, saved, and failed |

Use semantic `Form`, `TextField`, `TextEditor`, and navigation/sheet behavior for review. A Liquid Glass action bar may make a commit action visible over a long review, but the proposed values remain the visual subject and must remain legible when effects are reduced.

## API route matrix

VisionKit owns the camera-facing interaction; Vision or Core ML owns the analysis route; the app owns normalization, review, and persistence. Keep those boundaries visible in the target and module graph.

| API seam | Best use | Output to normalize | Required state/proof |
| --- | --- | --- | --- |
| `DataScannerViewController` | Live text/barcode capture with Apple-provided guidance, highlighting, focus, and zoom | `RecognizedItem` text/barcode, bounds, stable item ID, capture time, scanner configuration | `isSupported`, `isAvailable`, camera permission, supported languages/symbologies, start/stop/interruption, and physical camera proof. |
| `recognizedItems` `AsyncStream` | Async tracking of the current recognized-item collection | Collection diff, reading order, item additions/removals/updates | Cancel the consuming task on dismissal and avoid treating a transient item as confirmed data. |
| `DataScannerViewControllerDelegate` | Event-driven item changes and user taps | Add/remove/update/tap event plus item payload and bounds | Keep callbacks fast, route the tap through validation/confirmation, and handle scanner-unavailable callbacks. |
| `VNDocumentCameraViewController` | Multi-page document capture | Page/image references, order, capture metadata | Camera permission, cancellation, page count, failed save, and physical document samples. |
| `VNImageRequestHandler` + `VNRecognizeTextRequest` | OCR on a photo, document page, or video frame | Recognized text observations, candidates/confidence, bounding boxes, language/revision | Orientation, recognition level, language/correction choice, bounded input, cancellation, and labeled quality fixtures. |
| Vision request family | Barcodes, rectangles, faces/poses, object classification, image quality, or custom model bridge | Typed observation plus revision/request/model identifier | Select a measurable request; validate confidence/quality and never infer identity, safety, or authorization from an observation alone. |
| `PhotosPicker` | User-selected existing media without broad library access | Selected asset/transfer result and source identifier | Transfer failure, representation choice, privacy/retention, orientation, and import fallback. |

## Scanner lifecycle and SwiftUI bridge

Keep the scanner in a dedicated controller/adapter and expose value state to SwiftUI:

`unavailable -> ready -> presenting -> starting -> scanning -> selected/review -> stopping -> stopped`

with failure branches for `permissionDenied`, `unsupported`, `restricted`, `interrupted`, `startFailed`, `cancelled`, and `sourceSaveFailed`. A `UIViewControllerRepresentable` may host the controller, but the coordinator must not make `View.body` the owner of a long-lived camera session. Start and stop once per feature session, cancel the `recognizedItems` task when the controller disappears, and clear provisional highlights when the source or session changes.

Use `recognizedItems` when the product wants an async sequence of the current collection; use delegate callbacks when it needs event-specific add/remove/update/tap hooks. In both cases, compare item IDs and source/session identity before publishing. A text item’s reading order and a barcode payload are useful presentation/proposal inputs, not a commit authorization.

## Static-image fallback and AI handoff

When live scanning is unavailable, preserve the product’s outcome through the least-privileged fallback:

`PhotosPicker -> transfer/load -> orientation normalization -> Vision request -> typed draft -> review`

For a multimodal or Foundation Models step, pass only the bounded, user-approved fields or a cropped source that the feature needs. Carry `sourceAssetID`, `page/index`, `requestRevision`, `recognitionLanguage`, `model/framework version`, and `reviewState` with the proposal. Do not pass the entire photo library, raw document, or unrelated OCR text merely because the model accepts multimodal input.

The conversion contract should distinguish:

| Layer | Example | Can it be saved as domain truth? |
| --- | --- | --- |
| Observation | OCR candidate, barcode payload, bounding box | No; validate and review. |
| Normalized proposal | Parsed date, amount, identifier, or field list | Only after deterministic format/range/source checks and user policy. |
| User correction | Edited value with source and edit timestamp | Yes, subject to normal domain validation. |
| Confirmed record | App-owned model with provenance and retention policy | Yes; preserve the source and review history required by the product. |

## Physical-device capture gate

Before calling a capture feature ready, record the target device and OS, camera permission state, supported scanner state, lighting samples, orientation, focus/zoom behavior, frame rate/backpressure, thermal/memory observations, VoiceOver path, and manual fallback. A simulator image test can validate mapping and review logic; it cannot stand in for camera hardware or real-time capture proof.

## Sources

- [VisionKit](https://developer.apple.com/documentation/visionkit)
- [DataScannerViewController](https://developer.apple.com/documentation/visionkit/datascannerviewcontroller)
- [DataScannerViewController.RecognizedDataType](https://developer.apple.com/documentation/visionkit/datascannerviewcontroller/recognizeddatatype)
- [DataScannerViewControllerDelegate](https://developer.apple.com/documentation/visionkit/datascannerviewcontrollerdelegate)
- [RecognizedItem](https://developer.apple.com/documentation/visionkit/recognizeditem)
- [Recognized items](https://developer.apple.com/documentation/visionkit/datascannerviewcontroller/recognizeditems)
- [Scanning data with the camera](https://developer.apple.com/documentation/visionkit/scanning-data-with-the-camera)
- [Vision](https://developer.apple.com/documentation/vision/)
- [Recognizing text in images](https://developer.apple.com/documentation/vision/recognizing-text-in-images)
- [VNImageRequestHandler](https://developer.apple.com/documentation/vision/vnimagerequesthandler)
- [VNRecognizeTextRequest](https://developer.apple.com/documentation/vision/vnrecognizetextrequest)
- [PhotosUI](https://developer.apple.com/documentation/photosui)
